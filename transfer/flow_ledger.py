"""
FLOW LEDGER — the disclosure-to-participation latency register. HELD-OUT.

The instrument the Board specified across rounds 2 and 3 (see
audits/board/SYNTHESIS_money-movement_2026-07-25.md):

    trigger  = a MANDATORY DISCLOSURE we can timestamp exactly (Form 4 T+2, 13D 5bd)
    observable = signed, normalized insider BUYING BREADTH, a deviation from the
                 instrument's OWN base rate — a change, never a level, never a size proxy
    clock    = abnormal SHARE volume vs a baseline FROZEN before detection (arrival_clock)
    measure  = LEAD, in days, from disclosure to participation expansion
    proof    = Kaplan-Meier vs a MATCHED CONTROL, pre-registered, held-out, never deleted

WHAT THIS IS NOT: it does not detect concealed accumulation (order splitting and dark
pools defeat that by design, at any budget), it does not predict prices, and it touches
no non-public information. Mandatory disclosure is our floor AND our ceiling.

────────────────────────────────────────────────────────────────────────────────────────
TWO CONSTRAINTS ARE ENFORCED STRUCTURALLY, NOT BY CONVENTION
────────────────────────────────────────────────────────────────────────────────────────
1. **THE CONTROL ARM CANNOT BE RETROFITTED.** The Executioner's ruling: "you cannot enroll
   a placebo in the past without fabricating data, which the ground rules forbid. Ship the
   control first, or in 90 days we will have a beautiful, unfalsifiable number and will
   have to start over." So `enroll()` writes a treated row and its matched controls in ONE
   transaction, or writes nothing. There is no code path that produces a treated row alone.

2. **NO ENROLLMENT WITHOUT AN ACTIVE PRE-REGISTRATION.** Every threshold (enrollment cut,
   arrival multiple, horizon, minimum episodes, stop rule) must be committed to a
   pre-registration row BEFORE the first row is enrolled. `enroll()` refuses otherwise.
   This is the structural answer to round 1's finding that "the backtest tested a
   different variable than the one wired."

Forward-only, additive, never deleted (§13 retention does not apply — this is a ledger).
Postgres-safe via db_compat. Imported by NOTHING in scoring: this is measurement only.
"""
from __future__ import annotations

import os
import json
import time
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Sequence

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

# How long a detection waits for participation before it resolves as NO_ARRIVAL (censored,
# NOT a miss — the KM estimator uses it at its observation time).
FLOW_TIMEOUT_DAYS = int(os.getenv("FLOW_TIMEOUT_DAYS", "180"))
# Controls enrolled per treated row. The Board asked for 3-5; each is matched on sector +
# size decile + liquidity and carries NO qualifying disclosure.
FLOW_CONTROLS_PER = int(os.getenv("FLOW_CONTROLS_PER", "3"))
# An arrival within this many sessions of the DISCLOSURE is stamped `disclosure_echo` and
# reported separately — it is the market consuming the filing we both just read, which is
# not the same thing as us leading the crowd (the Challenger's sharpest round-3 warning).
FLOW_ECHO_SESSIONS = int(os.getenv("FLOW_ECHO_SESSIONS", "3"))

COHORT_TREATED = "treated"
COHORT_CONTROL = "control"

_GATE_REJECTS = {"no_prereg": 0, "no_controls": 0, "already_open": 0,
                 "calibrating": 0, "below_threshold": 0}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _iso(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


def _parse(s: str) -> Optional[datetime]:
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def _canon_date(v):
    """§14: canonical YYYY-MM-DD via date_utils, never a raw [:10] slice."""
    try:
        from date_utils import to_iso_date
        return to_iso_date(v)
    except Exception:
        return str(v)[:10] if v else None


def _connect(db_path: str = DB_PATH):
    conn = db_compat.connect(db_path)
    if not db_compat.USE_PG:
        try:
            import sqlite3
            conn.row_factory = sqlite3.Row
        except Exception:
            pass
    return conn


def init_flow_db(db_path: str = DB_PATH):
    """Additive, forward-only DDL. Safe to call repeatedly."""
    conn = _connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS flow_prereg (
            id TEXT PRIMARY KEY, hypothesis TEXT, observable TEXT, universe TEXT,
            enroll_threshold REAL, arrival_mult REAL, horizon_days INTEGER,
            controls_per INTEGER, min_episodes INTEGER, stop_rule TEXT,
            param_version TEXT, doc_path TEXT, registered_at TEXT, active INTEGER DEFAULT 1,
            -- Board accountability review: report() read `primary_horizon_days` from the
            -- prereg, but the column and the parameter did not exist — so it was ALWAYS
            -- None and fell through to a hardcoded 90. The O3 multiple-comparisons fix was
            -- a constant the pre-registration could not express. It is now a real,
            -- SHA-covered term (see register_prereg).
            primary_horizon_days INTEGER)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS flow_pending_detections (
            id TEXT PRIMARY KEY, cohort TEXT, match_group TEXT,
            ticker TEXT, name TEXT,
            detection_date TEXT, disclosure_ts TEXT,
            observable_value REAL, direction INTEGER,
            baseline_median REAL, baseline_samples INTEGER,
            baseline_window_start TEXT, baseline_window_end TEXT,
            pre_arrived INTEGER DEFAULT 0, size_decile INTEGER, sector TEXT,
            prereg_id TEXT, param_version TEXT,
            timeout_date TEXT, last_checked TEXT, status TEXT DEFAULT 'pending')
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS flow_ledger (
            id TEXT PRIMARY KEY, cohort TEXT, match_group TEXT,
            ticker TEXT, name TEXT,
            detection_date TEXT, disclosure_ts TEXT,
            observable_value REAL, direction INTEGER,
            baseline_median REAL,
            arrival_date TEXT, lead_days INTEGER, ratio_to_baseline REAL,
            scheduled TEXT, disclosure_echo INTEGER DEFAULT 0,
            verdict TEXT, pre_arrived INTEGER DEFAULT 0,
            size_decile INTEGER, sector TEXT,
            prereg_id TEXT, param_version TEXT, resolved_at TEXT)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS flow_gate_rejects (
            reason TEXT PRIMARY KEY, count INTEGER DEFAULT 0, updated_at TEXT)
    """)
    for ddl in (
        "CREATE INDEX IF NOT EXISTS idx_flow_pend_status ON flow_pending_detections(status)",
        "CREATE INDEX IF NOT EXISTS idx_flow_pend_group ON flow_pending_detections(match_group)",
        "CREATE INDEX IF NOT EXISTS idx_flow_ledger_verdict ON flow_ledger(verdict)",
        "CREATE INDEX IF NOT EXISTS idx_flow_ledger_cohort ON flow_ledger(cohort)",
    ):
        try:
            conn.execute(ddl)
        except Exception:
            pass
    conn.commit()
    conn.close()


# ── Pre-registration ────────────────────────────────────────────────────────────────────

def register_prereg(hypothesis: str, observable: str, universe: str,
                    enroll_threshold: float, arrival_mult: float, horizon_days: int,
                    min_episodes: int, stop_rule: str, param_version: str,
                    doc_path: str = "", controls_per: int = FLOW_CONTROLS_PER,
                    primary_horizon_days: int = 90,
                    db_path: str = DB_PATH) -> dict:
    """Commit a pre-registration BEFORE any enrollment. Its id is the sha256 of the terms,
    so an altered hypothesis is a different registration and cannot masquerade as the
    original. Registering a new one deactivates the previous — a threshold change mints a
    new cohort rather than silently redefining the running one.
    """
    # `primary_horizon_days` is INSIDE the hashed payload: it is a pre-registered term, so
    # changing it must mint a different registration rather than silently redefining the
    # running one.
    payload = json.dumps({"hypothesis": hypothesis, "observable": observable,
                          "universe": universe, "enroll_threshold": enroll_threshold,
                          "arrival_mult": arrival_mult, "horizon_days": horizon_days,
                          "controls_per": controls_per, "min_episodes": min_episodes,
                          "primary_horizon_days": primary_horizon_days,
                          "stop_rule": stop_rule, "param_version": param_version},
                         sort_keys=True)
    pid = hashlib.sha256(payload.encode()).hexdigest()[:16]
    conn = _connect(db_path)
    try:
        conn.execute("UPDATE flow_prereg SET active=0 WHERE active=1")
        ph = "%s" if db_compat.USE_PG else "?"
        cols = ("id,hypothesis,observable,universe,enroll_threshold,arrival_mult,"
                "horizon_days,controls_per,min_episodes,stop_rule,param_version,"
                "doc_path,registered_at,active,primary_horizon_days")
        conn.execute(
            f"INSERT INTO flow_prereg ({cols}) VALUES ({','.join([ph] * 15)}) "
            f"ON CONFLICT (id) DO UPDATE SET active=1",
            (pid, hypothesis, observable, universe, enroll_threshold, arrival_mult,
             horizon_days, controls_per, min_episodes, stop_rule, param_version,
             doc_path, _now(), 1, primary_horizon_days))
        conn.commit()
    finally:
        conn.close()
    return {"prereg_id": pid, "registered_at": _now(), "param_version": param_version}


def active_prereg(db_path: str = DB_PATH) -> Optional[dict]:
    conn = _connect(db_path)
    try:
        row = conn.execute("SELECT * FROM flow_prereg WHERE active=1 "
                           "ORDER BY registered_at DESC").fetchone()
        return dict(row) if row else None
    except Exception:
        return None
    finally:
        conn.close()


# ── Enrollment (atomic: treated + controls, or nothing) ─────────────────────────────────

def _mk_id(*parts) -> str:
    return hashlib.md5("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def enroll(treated: dict, controls: Sequence[dict], db_path: str = DB_PATH) -> dict:
    """Enroll ONE treated detection together with its matched controls, atomically.

    `treated` / each `controls[i]`: {ticker, name, detection_date, observable_value,
    direction, baseline (the arrival_clock baseline dict), pre_arrived, size_decile,
    sector, disclosure_ts}

    REFUSES (and counts the refusal in flow_gate_rejects — silent-evidence accounting) if:
      • no active pre-registration exists,
      • fewer controls are supplied than the pre-registration requires,
      • the treated ticker already has an open row (one open episode per ticker),
      • the baseline is CALIBRATING/degenerate (§16a — never score on a fabricated floor).
    """
    pre = active_prereg(db_path)
    if not pre:
        _GATE_REJECTS["no_prereg"] += 1
        _persist_rejects(db_path)
        return {"enrolled": False, "reason": "no active pre-registration — "
                "register_prereg() must be called before any enrollment"}

    need = int(pre.get("controls_per") or FLOW_CONTROLS_PER)
    controls = list(controls or [])
    if len(controls) < need:
        _GATE_REJECTS["no_controls"] += 1
        _persist_rejects(db_path)
        return {"enrolled": False, "reason": f"needs {need} matched controls, got "
                f"{len(controls)} — a treated row is never written alone"}

    base = treated.get("baseline") or {}
    if not base.get("available"):
        _GATE_REJECTS["calibrating"] += 1
        _persist_rejects(db_path)
        return {"enrolled": False, "reason": f"baseline unusable "
                f"({base.get('reason', 'calibrating')}) — §16a honest absence"}

    conn = _connect(db_path)
    try:
        ph = "%s" if db_compat.USE_PG else "?"
        tkr = (treated.get("ticker") or "").upper()
        open_row = conn.execute(
            f"SELECT id FROM flow_pending_detections WHERE ticker={ph} AND status='pending'",
            (tkr,)).fetchone()
        if open_row:
            _GATE_REJECTS["already_open"] += 1
            _flush_rejects(conn)          # conn is open here; do not nest a connection
            conn.commit()
            return {"enrolled": False, "reason": f"{tkr} already has an open episode"}

        det = _canon_date(treated.get("detection_date"))
        group = _mk_id("grp", tkr, det, pre["id"])
        horizon = int(pre.get("horizon_days") or FLOW_TIMEOUT_DAYS)
        timeout = _iso((_parse(det) or datetime.now(timezone.utc))
                       + timedelta(days=horizon))

        rows = [(COHORT_TREATED, treated)] + [(COHORT_CONTROL, c) for c in controls[:need]]
        cols = ("id,cohort,match_group,ticker,name,detection_date,disclosure_ts,"
                "observable_value,direction,baseline_median,baseline_samples,"
                "baseline_window_start,baseline_window_end,pre_arrived,size_decile,"
                "sector,prereg_id,param_version,timeout_date,last_checked,status")
        written = 0
        for cohort, r in rows:
            rb = r.get("baseline") or {}
            if not rb.get("available"):
                continue          # a control without a usable baseline is simply not enrolled
            # ⚠ D1 FIX (Board round 4, Executioner — reproduced before fixing). The id
            # previously omitted `group`, so two treated tickers enrolled on the SAME date
            # sharing a control ticker collided; `ON CONFLICT DO NOTHING` swallowed the
            # insert while the counter still incremented, so the all-or-nothing check
            # passed and a LONE TREATED ROW was written while enroll() reported success.
            # Matched controls are drawn on sector + size decile + liquidity, so control
            # overlap is the NORMAL case on a heavy filing day, not an edge case.
            rid = _mk_id(cohort, r.get("ticker"), det, pre["id"], group)
            cur = conn.execute(
                f"INSERT INTO flow_pending_detections ({cols}) "
                f"VALUES ({','.join([ph] * 21)}) ON CONFLICT (id) DO NOTHING",
                (rid, cohort, group, (r.get("ticker") or "").upper(), r.get("name") or "",
                 _canon_date(r.get("detection_date")) or det, r.get("disclosure_ts") or "",
                 float(r.get("observable_value") or 0), int(r.get("direction") or 0),
                 float(rb.get("median_volume") or 0), int(rb.get("samples") or 0),
                 rb.get("window_start") or "", rb.get("window_end") or "",
                 1 if r.get("pre_arrived") else 0,
                 r.get("size_decile"), r.get("sector") or "",
                 pre["id"], pre.get("param_version") or "", timeout, "", "pending"))
            # Count ACTUAL inserts, never loop iterations — that conflation is what let the
            # parity check pass on a swallowed insert.
            # If rowcount is unavailable we must NOT assume success — that silently
            # restores the iteration-counting bug this replaced.
            try:
                inserted = cur is not None and cur.rowcount != 0
            except Exception:
                inserted = False
            written += 1 if inserted else 0

        if written < 1 + need:
            conn.rollback()
            _GATE_REJECTS["no_controls"] += 1
            _flush_rejects(conn)
            conn.commit()
            return {"enrolled": False, "reason": f"only {written} of {1 + need} rows were "
                    f"actually written — enrollment is all-or-nothing so the arms stay at parity"}

        _flush_rejects(conn)
        conn.commit()
        return {"enrolled": True, "match_group": group, "rows": written,
                "treated": 1, "controls": written - 1, "prereg_id": pre["id"],
                "timeout_date": timeout}
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return {"enrolled": False, "reason": f"error: {e}"}
    finally:
        conn.close()


def _persist_rejects(db_path: str = DB_PATH):
    """D4 FIX (Board round 4, Executioner): `_flush_rejects` was only reached on the SUCCESS
    path, so in the regime where refusals carry the most information — no pre-registration,
    no controls, everything calibrating — nothing succeeded, nothing flushed, and the
    counters died with the dyno. The `no_prereg` branch returned before a connection even
    existed. Opens its own connection so a refusal is always durably recorded.
    """
    if not any(_GATE_REJECTS.values()):
        return
    try:
        c = _connect(db_path)
        try:
            _flush_rejects(c)
            c.commit()
        finally:
            c.close()
    except Exception as e:
        print(f"[flow-ledger] reject persist skipped: {e}")


def _flush_rejects(conn):
    """Persist unflushed reject counters — what the ledger NEVER SEES is part of the record."""
    try:
        ph = "%s" if db_compat.USE_PG else "?"
        for reason, d in list(_GATE_REJECTS.items()):
            if not d:
                continue
            if db_compat.USE_PG:
                conn.execute(
                    "INSERT INTO flow_gate_rejects (reason,count,updated_at) "
                    f"VALUES ({ph},{ph},{ph}) ON CONFLICT (reason) DO UPDATE SET "
                    "count = flow_gate_rejects.count + EXCLUDED.count, "
                    "updated_at = EXCLUDED.updated_at", (reason, d, _now()))
            else:
                conn.execute(
                    "INSERT INTO flow_gate_rejects (reason,count,updated_at) "
                    "VALUES (?,?,?) ON CONFLICT(reason) DO UPDATE SET "
                    "count = count + excluded.count, updated_at = excluded.updated_at",
                    (reason, d, _now()))
            _GATE_REJECTS[reason] = 0
    except Exception as e:
        print(f"[flow-ledger] reject flush skipped: {e}")


# ── Resolution ──────────────────────────────────────────────────────────────────────────

def sweep(db_path: str = DB_PATH, arrival_fn=None, limit: int = 200, today: str = "",
          pause_s: float = None) -> dict:
    """Resolve pending rows. TREATED AND CONTROL ROWS TAKE THE IDENTICAL PATH — that is the
    point of the design; any asymmetry here would invalidate the comparison.

    Verdicts: ARRIVED (participation expanded after detection) · PRE_ARRIVED (the crowd was
    already there at detection — discovery latency, reported separately, never a race) ·
    NO_ARRIVAL (horizon reached without expansion — CENSORED, not a miss).

    ⚠ PLACEMENT (Board round 4, O5 — Executioner). This issues one price/volume fetch per
    pending row. It MUST run in the scheduler thread inside `_collect_phase`, never behind
    an API endpoint: a synchronous few-hundred-row loop reachable from a request is an H12
    generator, and §13's batch-pacing rule exists precisely because heavy phases must not
    clog the serve path (the 2026-07-06 wedged-prewarm outage is the precedent). Each fetch
    is separated by FLOW_SWEEP_PAUSE_S, defaulting to the pipeline's COLLECT_SOURCE_PAUSE_S.
    """
    if pause_s is None:
        pause_s = float(os.getenv("FLOW_SWEEP_PAUSE_S",
                                  os.getenv("COLLECT_SOURCE_PAUSE_S", "10")))
    if arrival_fn is None:
        import arrival_clock
        arrival_fn = arrival_clock.arrival_for

    now = _parse(today) if today else datetime.now(timezone.utc)
    conn = _connect(db_path)
    out = {"checked": 0, "arrived": 0, "pre_arrived": 0, "no_arrival": 0, "errors": 0}
    _pre_cache: dict = {}
    fetched = 0          # remote fetches issued this sweep (drives §13 pacing)

    def _pre_for(pid):
        """D2 FIX (Board round 4): resolve thresholds from the ROW'S OWN pre-registration,
        never from module/env values. Previously `sweep()` used FLOW_TIMEOUT_DAYS and
        `find_arrival` used ARRIVAL_VOL_MULT, so a config change on the dyno silently
        re-resolved ALREADY-ENROLLED rows under a different definition — exactly the
        'tested a different variable than the one wired' failure this module exists to
        prevent."""
        if pid not in _pre_cache:
            try:
                r = conn.execute(
                    ("SELECT * FROM flow_prereg WHERE id=%s" if db_compat.USE_PG
                     else "SELECT * FROM flow_prereg WHERE id=?"), (pid,)).fetchone()
                _pre_cache[pid] = dict(r) if r else {}
            except Exception:
                _pre_cache[pid] = {}
        return _pre_cache[pid]

    try:
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM flow_pending_detections WHERE status='pending' "
            "ORDER BY last_checked ASC NULLS FIRST" if db_compat.USE_PG else
            "SELECT * FROM flow_pending_detections WHERE status='pending' "
            "ORDER BY COALESCE(last_checked,'') ASC").fetchall()][:limit]

        ph = "%s" if db_compat.USE_PG else "?"
        for p in rows:
            out["checked"] += 1
            try:
                det = p["detection_date"]
                verdict = arrival_date = None
                lead = ratio = None
                sched = ""
                rp = _pre_for(p.get("prereg_id"))
                row_horizon = int(rp.get("horizon_days") or FLOW_TIMEOUT_DAYS)
                row_mult = rp.get("arrival_mult")
                if p.get("pre_arrived"):
                    verdict = "PRE_ARRIVED"
                else:
                    kw = {"horizon_days": row_horizon}
                    if row_mult:
                        kw["mult"] = float(row_mult)
                    # ⚠ THE ANTI-LOOKAHEAD LOCK (Board accountability review). This call
                    # previously omitted the baseline, so the resolver recomputed it from a
                    # fresh series under today's env — making the "frozen at enrollment"
                    # guarantee decorative: the column was written and never read. Pass the
                    # stored value so a resolution is reproducible from the row alone.
                    if p.get("baseline_median"):
                        kw["baseline_median"] = float(p["baseline_median"])
                    if pause_s and fetched:
                        time.sleep(pause_s)      # §13 batch pacing between remote fetches
                    fetched += 1
                    a = arrival_fn(p["ticker"], det, **kw)
                    arr = (a or {}).get("arrival") or {}
                    if arr.get("arrived"):
                        verdict = "ARRIVED"
                        arrival_date = arr.get("arrival_date")
                        lead = arr.get("lead_days")
                        ratio = arr.get("ratio_to_baseline")
                        sched = arr.get("scheduled") or ""
                    elif _parse(p.get("timeout_date") or "") and \
                            now >= _parse(p["timeout_date"]):
                        verdict = "NO_ARRIVAL"          # censored at the horizon

                if not verdict:
                    conn.execute(f"UPDATE flow_pending_detections SET last_checked={ph} "
                                 f"WHERE id={ph}", (_now(), p["id"]))
                    continue

                echo = 0
                if verdict == "ARRIVED" and lead is not None and lead <= FLOW_ECHO_SESSIONS:
                    echo = 1        # the market consuming the same filing we read

                lcols = ("id,cohort,match_group,ticker,name,detection_date,disclosure_ts,"
                         "observable_value,direction,baseline_median,arrival_date,"
                         "lead_days,ratio_to_baseline,scheduled,disclosure_echo,verdict,"
                         "pre_arrived,size_decile,sector,prereg_id,param_version,resolved_at")
                conn.execute(
                    f"INSERT INTO flow_ledger ({lcols}) VALUES ({','.join([ph] * 22)}) "
                    f"ON CONFLICT (id) DO NOTHING",
                    (p["id"], p["cohort"], p["match_group"], p["ticker"], p.get("name") or "",
                     det, p.get("disclosure_ts") or "", p.get("observable_value"),
                     p.get("direction"), p.get("baseline_median"), arrival_date, lead, ratio,
                     sched, echo, verdict, p.get("pre_arrived") or 0, p.get("size_decile"),
                     p.get("sector") or "", p.get("prereg_id"), p.get("param_version"), _now()))
                conn.execute(f"UPDATE flow_pending_detections SET status='resolved', "
                             f"last_checked={ph} WHERE id={ph}", (_now(), p["id"]))
                out[{"ARRIVED": "arrived", "PRE_ARRIVED": "pre_arrived",
                     "NO_ARRIVAL": "no_arrival"}[verdict]] += 1
            except Exception as e:
                out["errors"] += 1
                print(f"[flow-ledger] sweep {p.get('ticker')}: {e}")
        conn.commit()
    finally:
        conn.close()
    return out


# ── Reporting ───────────────────────────────────────────────────────────────────────────

def report(db_path: str = DB_PATH, exclude_echo: bool = True,
           exclude_scheduled: bool = True) -> dict:
    """Treated vs control, via Kaplan-Meier with intervals. Publishes the SEPARATION, never
    a single-arm rate.

    By default the headline EXCLUDES `disclosure_echo` rows (arrivals within
    FLOW_ECHO_SESSIONS of the filing — the market reading the same document we did) and
    rows landing on a known scheduled artifact (triple witching, quarter/month end). Both
    exclusions are reported as counts so nothing is silently dropped.
    """
    import ledger_survival

    pre = active_prereg(db_path)
    active_id = (pre or {}).get("id")

    conn = _connect(db_path)
    try:
        # ⚠ D3 FIX (Board round 4, Challenger). This previously read the WHOLE table with no
        # prereg filter, while the banner and min_episodes came from the ACTIVE
        # registration — so enrolling under prereg A, disliking the trend, and
        # re-registering as B would present B's terms over A+B's rows, with no reader able
        # to see that A existed. That is specification shopping, shipped, inside the module
        # written to prevent it. Rows are now scoped to one cohort, and every superseded
        # cohort is surfaced (the "null archive", enforced in code rather than in prose).
        ph = "%s" if db_compat.USE_PG else "?"
        rows = [dict(r) for r in conn.execute(
            f"SELECT * FROM flow_ledger WHERE prereg_id={ph}", (active_id,)).fetchall()]
        pend = [dict(r) for r in conn.execute(
            f"SELECT cohort, detection_date, prereg_id FROM flow_pending_detections "
            f"WHERE status='pending' AND prereg_id={ph}", (active_id,)).fetchall()]
        # Horizons per registration, so censoring uses the term the ROW was registered
        # under rather than whatever the dyno env says today.
        _horizons = {h["id"]: h.get("horizon_days")
                     for h in [dict(x) for x in conn.execute(
                         "SELECT id, horizon_days FROM flow_prereg").fetchall()]}
        rejects = {r["reason"]: r["count"] for r in
                   [dict(x) for x in conn.execute("SELECT * FROM flow_gate_rejects").fetchall()]}
        history = [dict(r) for r in conn.execute(
            "SELECT id, param_version, registered_at, active FROM flow_prereg "
            "ORDER BY registered_at").fetchall()]
        counts = {}
        for h in history:
            c = conn.execute(f"SELECT COUNT(*) n FROM flow_ledger WHERE prereg_id={ph}",
                             (h["id"],)).fetchone()
            h["ledger_rows"] = dict(c)["n"] if c else 0
            counts[h["id"]] = h["ledger_rows"]
    except Exception as e:
        return {"available": False, "reason": f"flow ledger not initialised ({e})"}
    finally:
        conn.close()

    superseded = [h for h in history if not h.get("active") and h.get("ledger_rows")]

    def horizon_for(pid):
        """Censoring horizon for a row, from ITS registration — never module env."""
        return int(_horizons.get(pid) or FLOW_TIMEOUT_DAYS)
    now = datetime.now(timezone.utc)
    excluded = {"pre_arrived": 0, "disclosure_echo": 0, "scheduled": 0}
    arms = {COHORT_TREATED: [], COHORT_CONTROL: []}

    for r in rows:
        cohort = r.get("cohort")
        if cohort not in arms:
            continue
        v = r.get("verdict")
        if v == "PRE_ARRIVED":
            excluded["pre_arrived"] += 1          # discovery latency, never a race
            continue
        if v == "ARRIVED":
            if exclude_echo and r.get("disclosure_echo"):
                excluded["disclosure_echo"] += 1
                continue
            if exclude_scheduled and (r.get("scheduled") or ""):
                excluded["scheduled"] += 1
                continue
            lead = r.get("lead_days")
            if lead is None:
                continue
            arms[cohort].append((max(0, int(lead)), 1))
        elif v == "NO_ARRIVAL":
            # D2(a), Board accountability review: censoring used the module/env horizon, so
            # changing FLOW_TIMEOUT_DAYS on the dyno would move every censored observation's
            # time and shift the survival tail for rows already resolved. Censor at the
            # horizon the ROW was registered under.
            arms[cohort].append((horizon_for(r.get("prereg_id")), 0))

    # Still-pending rows are censored at their current age — they have not failed, they
    # have not finished being observed.
    for p in pend:
        c = p.get("cohort")
        d = _parse(p.get("detection_date") or "")
        if c in arms and d:
            arms[c].append((min((now - d).days, horizon_for(p.get("prereg_id"))), 0))

    # O4 (Board round 4, Executioner): a control ticker reused across match groups yields
    # repeated, NON-INDEPENDENT observations. Kaplan-Meier assumes independence, so the
    # control arm's interval comes out too narrow — and it errs IN OUR FAVOUR, which is
    # exactly the direction that must never be left silent. We cannot widen the interval
    # honestly without a cluster bootstrap, so we measure and DISCLOSE the clustering, and
    # refuse to publish when it is material.
    ctrl_tickers = [r.get("ticker") for r in rows if r.get("cohort") == COHORT_CONTROL]
    uniq = len(set(ctrl_tickers))
    reuse_factor = round(len(ctrl_tickers) / uniq, 2) if uniq else None
    control_independence = {
        "control_rows": len(ctrl_tickers), "distinct_control_tickers": uniq,
        "reuse_factor": reuse_factor,
        "independent": bool(reuse_factor is not None and reuse_factor <= 1.25),
        "note": ("Controls reused across match groups are not independent observations; the "
                 "KM interval on the control arm is narrower than the data support. A "
                 "cluster bootstrap (by ticker) is required before any published claim."),
    }

    cmp_out = ledger_survival.compare_arms(
        arms[COHORT_TREATED], arms[COHORT_CONTROL],
        horizons=(30, 90, 180),
        # O3: the verdict rests on ONE pre-registered horizon, not on whichever separates.
        primary_horizon=int((pre or {}).get("primary_horizon_days") or 90))
    n_t = len([1 for t, e in arms[COHORT_TREATED] if e == 1])
    min_ep = int((pre or {}).get("min_episodes") or 0)
    publishable = (bool(cmp_out.get("separated")) and n_t >= min_ep and min_ep > 0
                   # A superseded cohort holding rows must be disclosed before anything is
                   # publishable — otherwise the reader cannot see that an earlier
                   # definition was tried and set aside.
                   and not superseded
                   # O4: material control reuse makes the control interval falsely narrow.
                   and control_independence["independent"])

    return {
        "available": True,
        "held_out": True,
        "prereg": {"id": active_id, "param_version": (pre or {}).get("param_version"),
                   "min_episodes": min_ep, "stop_rule": (pre or {}).get("stop_rule")},
        "prereg_history": history,
        "superseded_cohorts_with_rows": [h["id"] for h in superseded],
        "arms": {"treated_rows": len(arms[COHORT_TREATED]),
                 "control_rows": len(arms[COHORT_CONTROL]),
                 "treated_events": n_t,
                 "control_events": len([1 for t, e in arms[COHORT_CONTROL] if e == 1])},
        "excluded": excluded,
        "control_independence": control_independence,
        "gate_rejects": rejects,
        "pending": len(pend),
        "comparison": cmp_out,
        "publishable": publishable,
        "headline": (
            "insufficient evidence — not publishable" if not publishable else
            "treated detections reach participation expansion ahead of matched controls; "
            "see comparison.horizons for the separation and interval"),
        "caveat": ("Measurement only. Lead is measured to abnormal SHARE-VOLUME expansion "
                   "(participation), never to a price move, and always against a matched "
                   "control. Disclosure-echo and scheduled-artifact arrivals are excluded "
                   "from the headline and reported as counts."),
    }


if __name__ == "__main__":
    import tempfile

    print("=== flow_ledger self-test (sqlite temp db, synthetic) ===\n")
    tmp = os.path.join(tempfile.gettempdir(), "flow_ledger_selftest.db")
    if os.path.exists(tmp):
        os.remove(tmp)
    init_flow_db(tmp)

    good_base = {"available": True, "median_volume": 1000.0, "samples": 60,
                 "window_start": "2026-01-01", "window_end": "2026-03-01"}
    mk = lambda t, **kw: dict({"ticker": t, "name": t, "detection_date": "2026-03-10",
                               "observable_value": 2.5, "direction": 1,
                               "baseline": good_base, "sector": "tech",
                               "size_decile": 3}, **kw)

    # 1. Enrollment MUST refuse before any pre-registration exists.
    r = enroll(mk("AAA"), [mk("C1"), mk("C2"), mk("C3")], db_path=tmp)
    assert not r["enrolled"] and "pre-registration" in r["reason"], r
    print(f"no prereg      -> refused ({r['reason'][:52]}...)  OK")

    pr = register_prereg(
        hypothesis="Insider open-market buying breadth precedes participation expansion",
        observable="signed normalized insider buying breadth vs own base rate",
        universe="US small/mid cap, event-driven", enroll_threshold=1.5,
        arrival_mult=3.0, horizon_days=180, min_episodes=60,
        stop_rule="publish 'underpowered' if treated events < 60",
        param_version="arrival-v2-sharevolume", db_path=tmp)
    print(f"prereg registered: {pr['prereg_id']}  OK")

    # 2. A treated row with too few controls must be refused ENTIRELY.
    r = enroll(mk("AAA"), [mk("C1")], db_path=tmp)
    assert not r["enrolled"] and "controls" in r["reason"], r
    print(f"1 of 3 controls-> refused ({r['reason'][:52]}...)  OK")
    conn = _connect(tmp)
    n = conn.execute("SELECT COUNT(*) c FROM flow_pending_detections").fetchone()
    conn.close()
    assert dict(n)["c"] == 0, "a refused enrollment must write NOTHING"
    print("refused enrollment wrote 0 rows (atomic)  OK")

    # 3. A CALIBRATING baseline must be refused (§16a).
    r = enroll(mk("AAA", baseline={"available": False, "reason": "insufficient_history"}),
               [mk("C1"), mk("C2"), mk("C3")], db_path=tmp)
    assert not r["enrolled"] and "16a" in r["reason"], r
    print(f"calibrating baseline -> refused (§16a honest absence)  OK")

    # 4. Valid enrollment writes treated + controls together.
    r = enroll(mk("AAA"), [mk("C1"), mk("C2"), mk("C3")], db_path=tmp)
    assert r["enrolled"] and r["treated"] == 1 and r["controls"] == 3, r
    print(f"valid enroll   -> {r['rows']} rows (1 treated + {r['controls']} controls)  OK")

    # 5. One open episode per ticker.
    r2 = enroll(mk("AAA"), [mk("C1"), mk("C2"), mk("C3")], db_path=tmp)
    assert not r2["enrolled"] and "already has an open episode" in r2["reason"]
    print("duplicate ticker -> refused (one open episode)  OK")

    # 5b. REGRESSION (Board R4, D1 — reproduced before fixing). TWO treated tickers on the
    #     SAME detection date SHARING control tickers. Controls are matched on sector +
    #     size decile + liquidity, so overlap is the NORMAL case on a heavy filing day.
    #     Previously the control ids omitted match_group -> collision -> ON CONFLICT DO
    #     NOTHING swallowed the insert -> `written` counted ITERATIONS not inserts -> the
    #     parity check passed and a LONE TREATED ROW was written while enroll() reported
    #     success. The original suite never enrolled two treated rows on one date, so it
    #     never caught the module's headline guarantee being false.
    r3 = enroll(mk("BBB"), [mk("C1"), mk("C2"), mk("C3")], db_path=tmp)
    assert r3["enrolled"], r3
    conn = _connect(tmp)
    grp = {}
    for row in [dict(x) for x in conn.execute(
            "SELECT match_group, cohort FROM flow_pending_detections").fetchall()]:
        grp.setdefault(row["match_group"], []).append(row["cohort"])
    conn.close()
    lone = [g for g, c in grp.items()
            if COHORT_TREATED in c and COHORT_CONTROL not in c]
    assert not lone, f"LONE TREATED ROW written for group(s) {lone} — the control arm " \
                     f"cannot be retrofitted, so this must never happen"
    for g, c in grp.items():
        assert c.count(COHORT_TREATED) == 1 and c.count(COHORT_CONTROL) == 3, (g, c)
    print(f"2nd treated, shared controls -> {len(grp)} groups, each 1 treated + 3 "
          f"controls, no lone treated  OK")

    # 6. Sweep with an injected clock: treated arrives fast, controls do not.
    seen_mult = []
    seen_baseline = []

    def fake_arrival(ticker, det, horizon_days=180, mult=None, baseline_median=None):
        # `mult` and `horizon_days` must arrive from the ROW'S pre-registration (D2), not
        # from module env — record them so the test can assert it.
        seen_mult.append((horizon_days, mult))
        seen_baseline.append(baseline_median)
        if ticker == "AAA":
            return {"available": True, "arrival": {
                "arrived": True, "arrival_date": "2026-03-25", "lead_days": 15,
                "ratio_to_baseline": 4.2, "scheduled": None}}
        return {"available": True, "arrival": {"arrived": False}}

    s = sweep(db_path=tmp, arrival_fn=fake_arrival, today="2026-12-31", pause_s=0)
    print(f"sweep: checked={s['checked']} arrived={s['arrived']} "
          f"no_arrival={s['no_arrival']} errors={s['errors']}  OK")
    # 2 treated (AAA arrives, BBB does not) + 6 controls = 8 rows
    assert s["errors"] == 0, s
    assert s["arrived"] == 1 and s["no_arrival"] == 7, s
    # D2 REGRESSION: the horizon and multiple must come from the pre-registration
    # (180 / 3.0), never from module env — a dyno config change must not be able to
    # re-resolve already-enrolled rows under a different definition.
    assert seen_mult and all(h == 180 and m == 3.0 for h, m in seen_mult), seen_mult
    print(f"sweep used prereg thresholds (horizon=180, mult=3.0) not env  OK")

    # REGRESSION (Board accountability review): THE ANTI-LOOKAHEAD LOCK. sweep() must pass
    # the baseline FROZEN at enrollment to the resolver. Previously it did not, and
    # arrival_for could not accept it — so every resolution recomputed the baseline under
    # today's env, making the "frozen at enrollment" guarantee decorative.
    assert seen_baseline and all(b == 1000.0 for b in seen_baseline), \
        f"frozen baseline must reach the resolver verbatim, got {set(seen_baseline)}"
    print(f"sweep passed the FROZEN baseline (1000.0) to resolution  OK")

    # 7. Report: both arms present, and NOT publishable at n=1 vs min_episodes=60.
    rep = report(db_path=tmp)
    assert rep["arms"]["treated_events"] == 1 and rep["arms"]["control_rows"] == 6, rep["arms"]
    assert rep["publishable"] is False, "must refuse to publish below min_episodes"

    # 7b. REGRESSION (Board R4, D3 — Challenger). Re-registering with different terms must
    #     NOT let the new banner present the OLD cohort's rows. Previously report() read the
    #     whole table with no prereg filter while min_episodes came from the ACTIVE prereg —
    #     enroll under A, dislike the trend, re-register as B, and B's terms were shown over
    #     A+B's rows with no reader able to see A existed.
    pr2 = register_prereg(
        hypothesis="same but a friendlier threshold", observable="o2", universe="u",
        enroll_threshold=0.5, arrival_mult=2.0, horizon_days=180, min_episodes=1,
        stop_rule="s", param_version="v2", db_path=tmp)
    rep2 = report(db_path=tmp)
    assert rep2["prereg"]["id"] == pr2["prereg_id"], rep2["prereg"]
    assert rep2["arms"]["treated_events"] == 0, \
        f"new cohort must NOT inherit the old cohort's rows: {rep2['arms']}"
    assert pr["prereg_id"] in rep2["superseded_cohorts_with_rows"], rep2
    assert rep2["publishable"] is False, "must not publish while a superseded cohort holds rows"
    print(f"re-register -> new cohort sees 0 rows, superseded cohort disclosed "
          f"({len(rep2['prereg_history'])} in history)  OK")
    print(f"report: treated_events={rep['arms']['treated_events']} "
          f"control_rows={rep['arms']['control_rows']} "
          f"publishable={rep['publishable']}  OK")
    # O4 REGRESSION (Board R4): C1/C2/C3 serve BOTH match groups, so the control arm has 6
    # rows over 3 distinct tickers. Those are not independent observations — KM would give a
    # falsely narrow control interval, erring in our favour. It must be measured, disclosed,
    # and must block publication until a cluster bootstrap exists.
    ci = rep["control_independence"]
    assert ci["control_rows"] == 6 and ci["distinct_control_tickers"] == 3, ci
    assert ci["reuse_factor"] == 2.0 and ci["independent"] is False, ci
    print(f"  control_independence: {ci['control_rows']} rows / "
          f"{ci['distinct_control_tickers']} distinct = {ci['reuse_factor']}x reuse -> "
          f"independent={ci['independent']} (blocks publication)  OK")
    print(f"  headline: {rep['headline']}")
    print(f"  gate_rejects: {rep['gate_rejects']}")
    assert rep["gate_rejects"].get("no_prereg", 0) >= 1, "refusals must be counted"
    print("  refusals recorded as silent evidence  OK")

    print("\nAll self-tests passed.")
