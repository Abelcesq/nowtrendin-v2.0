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
            param_version TEXT, doc_path TEXT, registered_at TEXT, active INTEGER DEFAULT 1)
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
                    db_path: str = DB_PATH) -> dict:
    """Commit a pre-registration BEFORE any enrollment. Its id is the sha256 of the terms,
    so an altered hypothesis is a different registration and cannot masquerade as the
    original. Registering a new one deactivates the previous — a threshold change mints a
    new cohort rather than silently redefining the running one.
    """
    payload = json.dumps({"hypothesis": hypothesis, "observable": observable,
                          "universe": universe, "enroll_threshold": enroll_threshold,
                          "arrival_mult": arrival_mult, "horizon_days": horizon_days,
                          "controls_per": controls_per, "min_episodes": min_episodes,
                          "stop_rule": stop_rule, "param_version": param_version},
                         sort_keys=True)
    pid = hashlib.sha256(payload.encode()).hexdigest()[:16]
    conn = _connect(db_path)
    try:
        conn.execute("UPDATE flow_prereg SET active=0 WHERE active=1")
        ph = "%s" if db_compat.USE_PG else "?"
        cols = ("id,hypothesis,observable,universe,enroll_threshold,arrival_mult,"
                "horizon_days,controls_per,min_episodes,stop_rule,param_version,"
                "doc_path,registered_at,active")
        conn.execute(
            f"INSERT INTO flow_prereg ({cols}) VALUES ({','.join([ph] * 14)}) "
            f"ON CONFLICT (id) DO UPDATE SET active=1",
            (pid, hypothesis, observable, universe, enroll_threshold, arrival_mult,
             horizon_days, controls_per, min_episodes, stop_rule, param_version,
             doc_path, _now(), 1))
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
        return {"enrolled": False, "reason": "no active pre-registration — "
                "register_prereg() must be called before any enrollment"}

    need = int(pre.get("controls_per") or FLOW_CONTROLS_PER)
    controls = list(controls or [])
    if len(controls) < need:
        _GATE_REJECTS["no_controls"] += 1
        return {"enrolled": False, "reason": f"needs {need} matched controls, got "
                f"{len(controls)} — a treated row is never written alone"}

    base = treated.get("baseline") or {}
    if not base.get("available"):
        _GATE_REJECTS["calibrating"] += 1
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
            rid = _mk_id(cohort, r.get("ticker"), det, pre["id"])
            conn.execute(
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
            written += 1

        if written < 1 + need:
            conn.rollback()
            _GATE_REJECTS["no_controls"] += 1
            return {"enrolled": False, "reason": f"only {written} of {1 + need} rows had a "
                    f"usable baseline — enrollment is all-or-nothing so the arms stay at parity"}

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

def sweep(db_path: str = DB_PATH, arrival_fn=None, limit: int = 200, today: str = "") -> dict:
    """Resolve pending rows. TREATED AND CONTROL ROWS TAKE THE IDENTICAL PATH — that is the
    point of the design; any asymmetry here would invalidate the comparison.

    Verdicts: ARRIVED (participation expanded after detection) · PRE_ARRIVED (the crowd was
    already there at detection — discovery latency, reported separately, never a race) ·
    NO_ARRIVAL (horizon reached without expansion — CENSORED, not a miss).
    """
    if arrival_fn is None:
        import arrival_clock
        arrival_fn = arrival_clock.arrival_for

    now = _parse(today) if today else datetime.now(timezone.utc)
    conn = _connect(db_path)
    out = {"checked": 0, "arrived": 0, "pre_arrived": 0, "no_arrival": 0, "errors": 0}
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
                if p.get("pre_arrived"):
                    verdict = "PRE_ARRIVED"
                else:
                    a = arrival_fn(p["ticker"], det,
                                   horizon_days=int(FLOW_TIMEOUT_DAYS))
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

    conn = _connect(db_path)
    try:
        rows = [dict(r) for r in conn.execute("SELECT * FROM flow_ledger").fetchall()]
        pend = [dict(r) for r in conn.execute(
            "SELECT cohort, detection_date FROM flow_pending_detections "
            "WHERE status='pending'").fetchall()]
        rejects = {r["reason"]: r["count"] for r in
                   [dict(x) for x in conn.execute("SELECT * FROM flow_gate_rejects").fetchall()]}
    except Exception:
        return {"available": False, "reason": "flow ledger not initialised"}
    finally:
        conn.close()

    pre = active_prereg(db_path)
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
            arms[cohort].append((FLOW_TIMEOUT_DAYS, 0))       # censored at the horizon

    # Still-pending rows are censored at their current age — they have not failed, they
    # have not finished being observed.
    for p in pend:
        c = p.get("cohort")
        d = _parse(p.get("detection_date") or "")
        if c in arms and d:
            arms[c].append((min((now - d).days, FLOW_TIMEOUT_DAYS), 0))

    cmp_out = ledger_survival.compare_arms(arms[COHORT_TREATED], arms[COHORT_CONTROL],
                                           horizons=(30, 90, 180))
    n_t = len([1 for t, e in arms[COHORT_TREATED] if e == 1])
    min_ep = int((pre or {}).get("min_episodes") or 0)
    publishable = bool(cmp_out.get("separated")) and n_t >= min_ep and min_ep > 0

    return {
        "available": True,
        "held_out": True,
        "prereg": {"id": (pre or {}).get("id"), "param_version": (pre or {}).get("param_version"),
                   "min_episodes": min_ep, "stop_rule": (pre or {}).get("stop_rule")},
        "arms": {"treated_rows": len(arms[COHORT_TREATED]),
                 "control_rows": len(arms[COHORT_CONTROL]),
                 "treated_events": n_t,
                 "control_events": len([1 for t, e in arms[COHORT_CONTROL] if e == 1])},
        "excluded": excluded,
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

    # 6. Sweep with an injected clock: treated arrives fast, controls do not.
    def fake_arrival(ticker, det, horizon_days=180):
        if ticker == "AAA":
            return {"available": True, "arrival": {
                "arrived": True, "arrival_date": "2026-03-25", "lead_days": 15,
                "ratio_to_baseline": 4.2, "scheduled": None}}
        return {"available": True, "arrival": {"arrived": False}}

    s = sweep(db_path=tmp, arrival_fn=fake_arrival, today="2026-12-31")
    print(f"sweep: checked={s['checked']} arrived={s['arrived']} "
          f"no_arrival={s['no_arrival']}  OK")
    assert s["arrived"] == 1 and s["no_arrival"] == 3, s

    # 7. Report: both arms present, and NOT publishable at n=1 vs min_episodes=60.
    rep = report(db_path=tmp)
    assert rep["arms"]["treated_events"] == 1 and rep["arms"]["control_rows"] == 3, rep["arms"]
    assert rep["publishable"] is False, "must refuse to publish below min_episodes"
    print(f"report: treated_events={rep['arms']['treated_events']} "
          f"control_rows={rep['arms']['control_rows']} "
          f"publishable={rep['publishable']}  OK")
    print(f"  headline: {rep['headline']}")
    print(f"  gate_rejects: {rep['gate_rejects']}")
    assert rep["gate_rejects"].get("no_prereg", 0) >= 1, "refusals must be counted"
    print("  refusals recorded as silent evidence  OK")

    print("\nAll self-tests passed.")
