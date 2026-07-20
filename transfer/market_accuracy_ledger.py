"""
NOW TRENDIN — MARKET-SIGNAL ACCURACY LEDGER (the Money Gradient's track record)

DISTINCT from the attention/Trends ledger (accuracy_ledger_enhanced.py). Same honest
philosophy, DIFFERENT ground truth:

  • Trends ledger   : detection = attention moving toward a topic
                      ground truth = Google Trends breakout (did attention arrive?)
  • THIS ledger     : detection = MONEY moving IN/OUT of an instrument (a flow + intensity,
                      measured from filings: Congress / insider Form-4 / smart-money 13F /
                      quality analysts)
                      ground truth = realized EOD CLOSE price DIRECTION (FMP) — did the
                      market actually move the way the detected money flow indicated?

WHY A SEPARATE LEDGER (founder direction, 2026-06-24): Google Trends does NOT validate a
market signal. A money-movement signal is validated by what the MARKET did — e.g. an
OUTFLOW (net selling) signal on NVDA is CONFIRMED if NVDA's EOD close subsequently trends
DOWN; an INFLOW signal is CONFIRMED if it trends UP. The lead time (days from our detection
to the confirming move) is recorded, exactly like the attention ledger records lead-to-breakout.

THIS IS MEASUREMENT, NOT ADVICE. We do not recommend buy/sell and do not predict prices.
This ledger only keeps an honest, falsifiable record of whether OUR money-movement signals
corresponded to (and preceded) the realized move. The verdict is about our accuracy — never
a call to the user.

INTEGRITY:
  • NO LOOKAHEAD — only price data on/after detection_date is used. detection_date is when
    WE flagged the signal (positioning_intel reads PUBLIC filings, so the data was public).
  • Honest denominator — counts NOT_CONFIRMED (moved against us) and NO_MOVE (flat by the
    deadline), not just the wins. hit_rate = CONFIRMED / (CONFIRMED+NOT_CONFIRMED+NO_MOVE).
  • Forward-only, additive — its own tables; touches nothing in the attention ledger or the
    scoring inputs. Degrades gracefully (available:False) when FMP_API_KEY is absent.
  • Flag-gated origin — only the Money Gradient (MARKET_SIGNAL_V2) records into it.

Postgres-safe via db_compat (explicit ON CONFLICT upserts; ? placeholders translated).
"""
import os
import hashlib
import statistics
from datetime import datetime, timezone, timedelta
from typing import Optional

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
# How long to wait for the market to confirm a money-flow detection before resolving it.
MARKET_TIMEOUT_DAYS = int(os.getenv("MARKET_LEDGER_TIMEOUT_DAYS", "60"))
# % EOD-close move (from the detection-day close) that counts as a real DIRECTIONAL move,
# above price noise. Tunable; deliberately conservative so noise isn't scored as a hit.
MOVE_THRESHOLD_PCT = float(os.getenv("MARKET_MOVE_THRESHOLD_PCT", "5.0"))
# Minimum movement intensity (0-1) for a money signal to be worth logging — keeps weak/noise
# flows out of the ledger so only real money-movement detections get a falsifiable record.
MIN_INTENSITY = float(os.getenv("MARKET_LEDGER_MIN_INTENSITY", "0.25"))
# Max calendar days to skip forward to find the first available close (weekends/holidays).
_MAX_SKIP = 6
# E4 / H4 (board 2026-07-19 + hardenings review 2026-07-20): count directional-flow
# candidates the ledger NEVER SEES — rejected at the enrollment gate. The board found the
# original module-global was per-process on a multi-dyno fleet, so a served 0 read as
# "nothing filtered" when it meant "this process never enrolled". FIX: the in-memory dict
# holds only UNFLUSHED deltas for THIS process; _flush_gate_rejects() upserts them into a
# DURABLE table (fleet-global, boot-durable) on any connection we already open (enrollment /
# sweep / report) — zero extra connections. report() serves the durable total + the note
# that a durable 0 with no boot history still means "unknown".
_GATE_REJECTS = {"nondirectional": 0, "weak_intensity": 0}


def _flush_gate_rejects(conn):
    """Upsert this-process unflushed reject deltas into the durable table, then zero them.
    Best-effort: a monitoring counter must never break enrollment or a report."""
    try:
        deltas = {k: v for k, v in _GATE_REJECTS.items() if v}
        if not deltas:
            return
        now = datetime.now(timezone.utc).isoformat()
        for reason, d in deltas.items():
            if db_compat.USE_PG:
                conn.execute(
                    "INSERT INTO market_gate_rejects (reason, count, updated_at) "
                    "VALUES (%s,%s,%s) ON CONFLICT (reason) DO UPDATE SET "
                    "count = market_gate_rejects.count + EXCLUDED.count, "
                    "updated_at = EXCLUDED.updated_at", (reason, d, now))
            else:
                conn.execute(
                    "INSERT INTO market_gate_rejects (reason, count, updated_at) "
                    "VALUES (?,?,?) ON CONFLICT(reason) DO UPDATE SET "
                    "count = count + excluded.count, updated_at = excluded.updated_at",
                    (reason, d, now))
            _GATE_REJECTS[reason] = 0
        conn.commit()
    except Exception as _fe:
        print(f"[mkt-ledger] gate-reject flush skipped: {_fe}")


def _connect(db_path: str = DB_PATH):
    """db_compat connection with dict-style rows in BOTH modes: Postgres uses a
    RealDictCursor; local sqlite needs an explicit sqlite3.Row factory so dict(row) works."""
    conn = db_compat.connect(db_path)
    if not db_compat.USE_PG:
        try:
            import sqlite3
            conn.row_factory = sqlite3.Row
        except Exception:
            pass
    return conn


def _cross_check(ticker: str, db: dict, fmp: dict, tol_pct: float = 1.0) -> None:
    """Log a WARNING when Databento + FMP EOD closes diverge >tol_pct on a shared date — an
    independent-source discrepancy worth a human look. The ledger keeps using the exchange-direct
    Databento value; this only surfaces disagreement (never silently trusts a mismatch)."""
    try:
        shared = set(db) & set(fmp)
        diffs = []
        for d in sorted(shared):
            a, b = db.get(d), fmp.get(d)
            if a and b and b != 0 and abs(a - b) / b * 100.0 > tol_pct:
                diffs.append((d, round(a, 2), round(b, 2)))
        if diffs:
            print(f"[mkt-ledger] price cross-check {ticker}: {len(diffs)}/{len(shared)} shared "
                  f"date(s) diverge >{tol_pct}% (databento vs fmp): {diffs[:3]}")
    except Exception:
        pass


def _price_fetch(ticker: str, frm: str, to: str):
    """Ground-truth EOD closes {YYYY-MM-DD: close} for the ledger. **Databento** (exchange-direct,
    no rate cap) is the PRIMARY verification source; **FMP** is the fallback. When BOTH are
    available the overlapping dates are cross-checked and any material divergence is logged — two
    independent sources agreeing makes a CONFIRMED/NOT_CONFIRMED verdict robust. Referee only;
    never feeds a score."""
    db = fmp = None
    try:
        import databento_price
        db = databento_price.historical_close(ticker, frm, to)
    except Exception as e:
        print(f"[mkt-ledger] databento {ticker}: {e}")
    try:
        import fmp_data
        fmp = fmp_data.historical_close(ticker, frm=frm, to=to)
    except Exception as e:
        print(f"[mkt-ledger] fmp {ticker}: {e}")
    if db and fmp:
        _cross_check(ticker, db, fmp)
        return db   # exchange-direct primary (already cross-checked against FMP)
    return db or fmp


def init_market_ledger_db(db_path: str = DB_PATH):
    conn = db_compat.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_pending_detections (
            id TEXT PRIMARY KEY, ticker TEXT, name TEXT,
            detection_date TEXT, flow TEXT, intensity REAL, detection_score REAL,
            timeout_date TEXT, last_checked TEXT, status TEXT DEFAULT 'pending')
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_accuracy_ledger (
            id TEXT PRIMARY KEY, ticker TEXT, name TEXT,
            detection_date TEXT, flow TEXT, detection_score REAL,
            price_at_detection REAL, price_at_move REAL, price_change_pct REAL,
            move_date TEXT, lead_time_days INTEGER, verdict TEXT, validated_at TEXT)
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mkt_pending_status ON market_pending_detections(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mkt_ledger_verdict ON market_accuracy_ledger(verdict)")
    # H4 durable, fleet-global gate-reject counter (hardenings review 2026-07-20).
    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_gate_rejects (
            reason TEXT PRIMARY KEY, count INTEGER DEFAULT 0, updated_at TEXT)
    """)
    conn.commit()
    conn.close()


def _parse(date_str: str) -> datetime:
    s = (date_str or "").strip().replace("Z", "")
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M", "%b %d, %Y", "%m/%d/%Y"):
        try:
            base = s.split("T")[0] if (fmt == "%Y-%m-%d" and "T" in s) else s
            return datetime.strptime(base, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


def _close_on_or_after(px: dict, date_str: str, max_skip: int = _MAX_SKIP):
    """First available EOD close on/after date_str (skips weekends/holidays)."""
    try:
        d0 = _parse(date_str)
    except Exception:
        return None, None
    for i in range(max_skip):
        k = (d0 + timedelta(days=i)).strftime("%Y-%m-%d")
        if k in px:
            return px[k], k
    return None, None


def record_market_detection(ticker, name, detection_date, flow, intensity,
                            detection_score=None, db_path=DB_PATH, conn=None):
    """Log a MONEY-MOVEMENT detection as PENDING the moment the Money Gradient flags it.
    Idempotent on (ticker, detection_date, flow).

    flow MUST be directional ('inflow' or 'outflow') — a 'neutral' flow makes no falsifiable
    directional claim, so it is not logged (nothing to validate). ticker is required (the
    price ground truth is keyed by symbol)."""
    flow = (flow or "").lower().strip()
    tkr = (ticker or "").upper().strip()
    if flow not in ("inflow", "outflow"):
        _GATE_REJECTS["nondirectional"] += 1   # E4 (board): count what the ledger never sees
        return  # only directional claims are falsifiable
    if not tkr:
        return
    try:
        if intensity is not None and float(intensity) < MIN_INTENSITY:
            _GATE_REJECTS["weak_intensity"] += 1
            return  # too weak to be a real money-movement detection
    except (TypeError, ValueError):
        pass
    # WITNESS-CORRUPTION FIX (board D8 session, Challenger finding, 2026-07-19; H7 hardening
    # 2026-07-20): detection_score is the stored AT-DETECTION WITNESS (what the money score
    # read when we enrolled) — context only, never thresholded, never in the verdict. We must
    # NEVER substitute intensity*100 when it is absent: that stores a DIFFERENT quantity under
    # the same column name and (under a future D8) would silently corrupt the one honest
    # at-detection record. So we simply do NOT touch it — absent stays NULL. Guarded by the
    # regression test in test_market_ledger_witness.py (which is the real mechanism, not this
    # comment). No substitution code here by design.
    # Canonicalize the detection date (§14) at the write boundary.
    try:
        from date_utils import to_iso_date
        detection_date = to_iso_date(detection_date) or detection_date
    except Exception:
        pass
    own = conn is None
    if own:
        conn = db_compat.connect(db_path)
    _flush_gate_rejects(conn)   # H4: piggyback the durable flush on this enrollment's conn
    now = datetime.now(timezone.utc).isoformat()
    try:
        timeout_dt = (_parse(detection_date) + timedelta(days=MARKET_TIMEOUT_DAYS)).isoformat()
    except Exception:
        timeout_dt = None
    rec_id = hashlib.md5(f"{tkr}-{detection_date}-{flow}".encode()).hexdigest()[:16]
    try:
        # Dedup: at most ONE OPEN (pending) detection per (ticker, flow). A flow that
        # persists across cycles is the SAME ongoing signal — re-logging it every day would
        # flood the ledger with correlated rows and inflate the denominator. A flow FLIP
        # (different flow value) is a genuinely new detection and is NOT blocked; a fresh
        # same-flow detection is logged only after the prior one resolves.
        open_same = conn.execute(
            ("SELECT 1 FROM market_pending_detections WHERE ticker=%s AND flow=%s "
             "AND status='pending' LIMIT 1") if db_compat.USE_PG else
            ("SELECT 1 FROM market_pending_detections WHERE ticker=? AND flow=? "
             "AND status='pending' LIMIT 1"),
            (tkr, flow)).fetchone()
        if open_same:
            return
        ex = conn.execute("SELECT status FROM market_pending_detections WHERE id=%s" if db_compat.USE_PG
                          else "SELECT status FROM market_pending_detections WHERE id=?",
                          (rec_id,)).fetchone()
        if not ex:
            conn.execute("""
                INSERT OR IGNORE INTO market_pending_detections
                    (id, ticker, name, detection_date, flow, intensity, detection_score,
                     timeout_date, last_checked, status)
                VALUES (?,?,?,?,?,?,?,?,?,'pending')
            """, (rec_id, tkr, name or tkr, detection_date, flow,
                  float(intensity) if intensity is not None else None,
                  detection_score, timeout_dt, now))
            conn.commit()
    except Exception as e:
        print(f"[mkt-ledger] record_market_detection error: {e}")
    finally:
        if own:
            conn.close()


def _upsert_ledger(conn, rec_id, p, price0, price1, change_pct, move_date, lead_days, verdict):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT INTO market_accuracy_ledger
            (id, ticker, name, detection_date, flow, detection_score,
             price_at_detection, price_at_move, price_change_pct,
             move_date, lead_time_days, verdict, validated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT (id) DO UPDATE SET
            price_at_detection=EXCLUDED.price_at_detection,
            price_at_move=EXCLUDED.price_at_move,
            price_change_pct=EXCLUDED.price_change_pct,
            move_date=EXCLUDED.move_date, lead_time_days=EXCLUDED.lead_time_days,
            verdict=EXCLUDED.verdict, validated_at=EXCLUDED.validated_at
    """, (rec_id, p["ticker"], p.get("name"), p["detection_date"], p.get("flow"),
          p.get("detection_score"), price0, price1, change_pct, move_date, lead_days, verdict, now))


def _evaluate(px: dict, p: dict):
    """Walk EOD closes forward from detection_date and decide the verdict.

    Returns (verdict, price0, price1, change_pct, move_date, lead_days) or None if the
    detection-day close can't be located yet. Verdicts:
      CONFIRMED      — close moved past +threshold (inflow) / -threshold (outflow): direction matched.
      NOT_CONFIRMED  — close moved past the OPPOSITE threshold first: moved against the detected flow.
      NO_MOVE        — neither threshold crossed within the window (only final at timeout).
    The first threshold crossed (in either direction) decides it — honest, no cherry-picking."""
    flow = p.get("flow")
    p0, d0 = _close_on_or_after(px, p["detection_date"])
    if p0 is None or p0 <= 0:
        return None
    up_lvl = p0 * (1.0 + MOVE_THRESHOLD_PCT / 100.0)
    dn_lvl = p0 * (1.0 - MOVE_THRESHOLD_PCT / 100.0)
    start = _parse(p["detection_date"])
    # Only look at closes AFTER the detection-day close (no lookahead, no same-bar credit).
    for d, px_close in sorted(px.items()):
        if d <= d0:
            continue
        try:
            cur = float(px_close)
        except (TypeError, ValueError):
            continue
        crossed_up = cur >= up_lvl
        crossed_dn = cur <= dn_lvl
        if not (crossed_up or crossed_dn):
            continue
        change_pct = round((cur - p0) / p0 * 100.0, 2)
        try:
            lead = (_parse(d) - start).days
        except Exception:
            lead = None
        # Direction match → CONFIRMED; opposite → NOT_CONFIRMED.
        matched = (flow == "inflow" and crossed_up) or (flow == "outflow" and crossed_dn)
        verdict = "CONFIRMED" if matched else "NOT_CONFIRMED"
        return (verdict, round(p0, 4), round(cur, 4), change_pct, d, lead)
    return ("PENDING", round(p0, 4), None, None, None, None)


def sweep_market_pending(db_path=DB_PATH, fetch_price_fn=None, limit=None) -> dict:
    """Resolve pending money-movement detections against realized EOD close direction.

    ROTATION: oldest-checked first, so a capped run advances through the whole pool.
    TIMEOUT-FIRST: a row past its deadline with no confirming move resolves as NO_MOVE
    (still needs the price series to report the realized change, but never stays stuck)."""
    fetch = fetch_price_fn or _price_fetch
    conn = _connect(db_path)
    _flush_gate_rejects(conn)   # H4: sweep always has a conn — flush any pending deltas
    q = ("SELECT * FROM market_pending_detections WHERE status='pending' "
         "ORDER BY (last_checked IS NULL) DESC, last_checked ASC")
    if limit:
        q += f" LIMIT {int(limit)}"
    pending = [dict(r) for r in conn.execute(q).fetchall()]
    now = datetime.now(timezone.utc)
    confirmed = not_conf = no_move = still = unpriced = 0
    for p in pending:
        timed_out = False
        if p.get("timeout_date"):
            try:
                timed_out = now > _parse(p["timeout_date"])
            except Exception:
                timed_out = False
        # Pull closes from detection_date → now (forward-only).
        to_str = now.strftime("%Y-%m-%d")
        px = None
        try:
            px = fetch(p["ticker"], p["detection_date"], to_str)
        except Exception:
            px = None
        if not px:
            # Can't price it yet (no key / no data). Leave pending unless past deadline,
            # in which case we cannot validate it honestly → mark unpriced (auditable, non-deleting).
            if timed_out:
                conn.execute("UPDATE market_pending_detections SET status='unpriced' WHERE id=?",
                             (p["id"],))
                conn.commit()
                unpriced += 1
            else:
                conn.execute("UPDATE market_pending_detections SET last_checked=? WHERE id=?",
                             (now.isoformat(), p["id"]))
                conn.commit()
                still += 1
            continue
        ev = _evaluate(px, p)
        if ev is None:
            # No detection-day close located yet; keep pending (or unpriced if past deadline).
            if timed_out:
                conn.execute("UPDATE market_pending_detections SET status='unpriced' WHERE id=?",
                             (p["id"],))
                conn.commit()
                unpriced += 1
            else:
                conn.execute("UPDATE market_pending_detections SET last_checked=? WHERE id=?",
                             (now.isoformat(), p["id"]))
                conn.commit()
                still += 1
            continue
        verdict, p0, p1, change_pct, move_date, lead = ev
        if verdict == "PENDING":
            if timed_out:
                # Window elapsed with no threshold crossing → honest NO_MOVE (flat).
                last_d = max(px.keys())
                try:
                    final = float(px[last_d]); change_pct = round((final - p0) / p0 * 100.0, 2)
                except Exception:
                    final = None
                rec_id = hashlib.md5(f"{p['ticker']}-{p['detection_date']}-{p.get('flow')}".encode()).hexdigest()[:16]
                _upsert_ledger(conn, rec_id, p, p0, final, change_pct, None, None, "NO_MOVE")
                conn.execute("UPDATE market_pending_detections SET status='resolved' WHERE id=?",
                             (p["id"],))
                conn.commit()
                no_move += 1
            else:
                conn.execute("UPDATE market_pending_detections SET last_checked=? WHERE id=?",
                             (now.isoformat(), p["id"]))
                conn.commit()
                still += 1
            continue
        # CONFIRMED or NOT_CONFIRMED — a threshold was crossed.
        rec_id = hashlib.md5(f"{p['ticker']}-{p['detection_date']}-{p.get('flow')}".encode()).hexdigest()[:16]
        _upsert_ledger(conn, rec_id, p, p0, p1, change_pct, move_date, lead, verdict)
        conn.execute("UPDATE market_pending_detections SET status='resolved' WHERE id=?",
                     (p["id"],))
        conn.commit()
        if verdict == "CONFIRMED":
            confirmed += 1
        else:
            not_conf += 1
    conn.close()
    out = {"resolved_confirmed": confirmed, "resolved_not_confirmed": not_conf,
           "resolved_no_move": no_move, "still_pending": still, "unpriced": unpriced}
    print(f"[mkt-ledger] sweep: {out}")
    return out


# P1 (hardenings review 2026-07-20, Economist): regime-adjust the verdict. The absolute
# ±5% verdict is regime-BLENDED in BOTH directions — in a broad rally inflow confirms and
# outflow fails MECHANICALLY, with zero skill either way (both lanes are "the same rally
# bet pointed opposite ways"). The honest read asks: did the instrument's flow-direction
# move BEAT its concurrent benchmark? Reported ALONGSIDE the absolute verdict, never
# replacing it. Measurement-only; the benchmark referee never feeds a score.
BENCHMARK = os.getenv("MARKET_LEDGER_BENCHMARK", "SPY")
REGIME_DEADBAND_PCT = float(os.getenv("MARKET_REGIME_DEADBAND_PCT", "2.0"))


def _regime_adjusted(rows, fetch=None):
    """For resolved rows with a realized move, classify EXCESS return vs the benchmark over
    the SAME window. One benchmark fetch covers all rows (shared union window). Fail-open:
    returns {available: False} if the benchmark series can't be fetched."""
    fetch = fetch or _price_fetch
    usable = [r for r in rows
              if r.get("verdict") in ("CONFIRMED", "NOT_CONFIRMED", "NO_MOVE")
              and r.get("detection_date") and r.get("move_date")
              and r.get("price_change_pct") is not None]
    if not usable:
        return {"available": False, "reason": "no rows with a realized move + date"}
    try:
        dates = [d for r in usable for d in (r["detection_date"], r["move_date"])]
        frm = min(str(d)[:10] for d in dates)
        to = max(str(d)[:10] for d in dates)
        bpx = fetch(BENCHMARK, frm, to)
        if not bpx:
            return {"available": False, "reason": f"{BENCHMARK} series unavailable"}
    except Exception as e:
        return {"available": False, "reason": str(e)[:80]}
    reg = {"CONFIRMED": 0, "NOT_CONFIRMED": 0, "NO_MOVE": 0}
    reg_flow = {"inflow": {"c": 0, "n": 0}, "outflow": {"c": 0, "n": 0}}
    reg_ep = {}
    computed = 0
    for r in usable:
        b0, _ = _close_on_or_after(bpx, str(r["detection_date"])[:10])
        b1, _ = _close_on_or_after(bpx, str(r["move_date"])[:10])
        if b0 is None or b1 is None or b0 <= 0:
            continue
        bench_change = (float(b1) - float(b0)) / float(b0) * 100.0
        excess = float(r["price_change_pct"]) - bench_change
        flow = r.get("flow")
        if abs(excess) < REGIME_DEADBAND_PCT:
            rv = "NO_MOVE"
        elif (flow == "inflow" and excess > 0) or (flow == "outflow" and excess < 0):
            rv = "CONFIRMED"
        else:
            rv = "NOT_CONFIRMED"
        reg[rv] += 1
        computed += 1
        if flow in reg_flow:
            reg_flow[flow]["n"] += 1
            if rv == "CONFIRMED":
                reg_flow[flow]["c"] += 1
        k = ((r.get("ticker") or "").upper(), flow)
        reg_ep.setdefault(k, []).append(rv)
    if not computed:
        return {"available": False, "reason": "benchmark closes not found for the windows"}
    ep_conf = sum(1 for v in reg_ep.values() if any(x == "CONFIRMED" for x in v))
    ep_strict = sum(1 for v in reg_ep.values() if v and all(x == "CONFIRMED" for x in v))
    return {
        "available": True, "benchmark": BENCHMARK, "deadband_pct": REGIME_DEADBAND_PCT,
        "definition": "CONFIRMED = the instrument's flow-direction move BEAT the benchmark "
                      "(excess return past the deadband) over the same window",
        "computed": computed,
        "confirmed": reg["CONFIRMED"], "not_confirmed": reg["NOT_CONFIRMED"],
        "no_move": reg["NO_MOVE"],
        "confirm_rate_pct": round(100.0 * reg["CONFIRMED"] / computed, 1),
        "by_flow": {f: {"confirmed": reg_flow[f]["c"], "resolved": reg_flow[f]["n"],
                        "confirm_rate_pct": round(100.0 * reg_flow[f]["c"] / reg_flow[f]["n"], 1)
                        if reg_flow[f]["n"] else None} for f in ("inflow", "outflow")},
        "episodes": {"resolved": len(reg_ep), "confirmed_any": ep_conf,
                     "confirmed_strict": ep_strict},
        "note": "de-confounds BOTH lanes vs market regime — this is the diligence-defensible "
                "read; the absolute-threshold rate above is regime-BLENDED in both directions.",
    }


def report(db_path=DB_PATH) -> dict:
    """Honest accuracy report for the Money Gradient. hit_rate counts the misses
    (NOT_CONFIRMED + NO_MOVE), never just the wins. MEASUREMENT of our own accuracy —
    not a forecast or advice."""
    conn = _connect(db_path)
    _flush_gate_rejects(conn)   # H4: flush this process's deltas before reading the durable total
    rows = [dict(r) for r in conn.execute("SELECT * FROM market_accuracy_ledger").fetchall()]
    # In-flight detections (recorded, awaiting a confirming move or the timeout) — proves
    # detections are being captured even before any verdict resolves.
    try:
        pending = conn.execute(
            "SELECT COUNT(*) FROM market_pending_detections WHERE status='pending'").fetchone()
        pending = (pending[0] if not isinstance(pending, dict) else list(pending.values())[0]) or 0
    except Exception:
        pending = 0
    # H4: durable, fleet-global gate-reject totals (a 0 with no history still = unknown).
    gate_durable = {"nondirectional": 0, "weak_intensity": 0}
    try:
        for gr in conn.execute("SELECT reason, count FROM market_gate_rejects").fetchall():
            gate_durable[(gr["reason"] if hasattr(gr, "keys") else gr[0])] = \
                (gr["count"] if hasattr(gr, "keys") else gr[1]) or 0
    except Exception:
        pass
    conn.close()
    confirmed = [r for r in rows if r.get("verdict") == "CONFIRMED"]
    not_conf = [r for r in rows if r.get("verdict") == "NOT_CONFIRMED"]
    no_move = [r for r in rows if r.get("verdict") == "NO_MOVE"]
    resolved = len(confirmed) + len(not_conf) + len(no_move)
    leads = [r["lead_time_days"] for r in confirmed if r.get("lead_time_days") is not None]
    by_flow = {}
    for f in ("inflow", "outflow"):
        c = sum(1 for r in confirmed if r.get("flow") == f)
        n = sum(1 for r in rows if r.get("flow") == f and r.get("verdict") in
                ("CONFIRMED", "NOT_CONFIRMED", "NO_MOVE"))
        by_flow[f] = {"confirmed": c, "resolved": n,
                      "confirm_rate_pct": round(100.0 * c / n, 1) if n else None}
    # E4 EPISODE-COLLAPSE (board D8 session, Challenger): a persistent claim re-enrolls
    # on later dates (AAPL outflow x3 = ONE ongoing signal, not 3 independent trials).
    # Collapse resolved rows to distinct (ticker, flow) EPISODES so the reported rate
    # isn't a denominator game — row-level rate is kept alongside for transparency, and
    # the episode counts are the honest n for any interval/claim.
    _res_rows = [r for r in rows if r.get("verdict") in ("CONFIRMED", "NOT_CONFIRMED", "NO_MOVE")]
    _ep = {}
    for r in _res_rows:
        key = ((r.get("ticker") or "").upper(), r.get("flow"))
        _ep.setdefault(key, []).append(r)
    # H3 (hardenings review 2026-07-20, all six): "confirmed if ANY row confirmed" is a MAX
    # operator that can only move the rate UP (it flattered inflow 6/7 rows -> 3/3 episodes,
    # burying the miss). Serve THREE rollups — strict (all rows), majority, and the optimistic
    # any — so the number cannot be gamed by aggregation; the episode confirm-rate KPI is
    # reported as a RANGE [strict, any], never a single optimistic figure.
    def _ep_rate(rule):
        hits = sum(1 for v in _ep.values() if rule([x.get("verdict") == "CONFIRMED" for x in v]))
        return hits, (round(100.0 * hits / len(_ep), 1) if _ep else None)
    ep_any_n, ep_any = _ep_rate(any)
    ep_strict_n, ep_strict = _ep_rate(all)
    ep_maj_n, ep_maj = _ep_rate(lambda bs: sum(bs) * 2 > len(bs))
    episodes = {
        "definition": "distinct (ticker, flow); a persistent claim's re-enrollments = one episode",
        "resolved_episodes": len(_ep),
        "aggregation_note": "confirm-rate reported as a RANGE across rollup rules; never "
                            "headline the optimistic 'any' alone (it can only inflate)",
        "confirmed_range_pct": [ep_strict, ep_any],
        "confirm_rate_strict_pct": ep_strict,     # all rows in the episode confirmed
        "confirm_rate_majority_pct": ep_maj,       # >half the rows confirmed
        "confirm_rate_any_pct": ep_any,            # optimistic upper bound (any row)
        "confirmed_episodes_any": ep_any_n,
        "confirmed_episodes_strict": ep_strict_n,
        "by_flow": {f: {
            "episodes": sum(1 for (t, fl) in _ep if fl == f),
            "confirmed_any": sum(1 for (k, v) in _ep.items() if k[1] == f
                                 and any(x.get("verdict") == "CONFIRMED" for x in v)),
            "confirmed_strict": sum(1 for (k, v) in _ep.items() if k[1] == f
                                    and v and all(x.get("verdict") == "CONFIRMED" for x in v)),
        } for f in ("inflow", "outflow")},
    }
    regime = _regime_adjusted(rows)
    return {
        "ground_truth": "realized EOD close direction (FMP)",
        "distinct_from": "trends accuracy ledger (Google Trends breakout)",
        "move_threshold_pct": MOVE_THRESHOLD_PCT,
        "timeout_days": MARKET_TIMEOUT_DAYS,
        "resolved": resolved,
        "pending": pending,
        "confirmed": len(confirmed),
        "not_confirmed": len(not_conf),
        "no_move": len(no_move),
        "confirm_rate_pct": round(100.0 * len(confirmed) / resolved, 1) if resolved else None,
        "median_lead_days": round(statistics.median(leads), 1) if leads else None,
        "by_flow": by_flow,
        "episodes": episodes,
        # P1: regime-adjusted (vs benchmark) — the diligence-defensible read.
        "regime_adjusted": regime,
        # R1 SYMMETRY RULING (hardenings review 2026-07-20): the absolute-threshold rates
        # (confirm_rate_pct, by_flow) are regime-BLENDED in BOTH directions. Neither lane is
        # validated at this n — a high inflow rate is as regime-flattered as a low outflow
        # rate ("the same coin landing heads because the market went up"). Read
        # regime_adjusted above, not the absolute rates, and NEVER publish either externally
        # while small_sample is true.
        "regime_caveat": "absolute rates are regime-blended in BOTH directions; neither lane "
                         "is validated at this n — see regime_adjusted; do not publish externally",
        # H4: durable, fleet-global reject totals. A 0 with no updated_at history = UNKNOWN
        # (this process may never have enrolled), NOT 'nothing filtered'.
        "gate_rejects_durable": gate_durable,
        "gate_rejects_this_process_unflushed": dict(_GATE_REJECTS),
        "small_sample": resolved < 20,
        "episode_small_sample": len(_ep) < 15,
        "note": "MEASUREMENT of the Money Gradient's own accuracy — did the realized market "
                "move match the detected money flow, and how many days after. NOT a forecast, "
                "NOT advice, NOT a buy/sell signal.",
    }


def detail(db_path=DB_PATH, limit=300, verdict=None) -> dict:
    """Per-detection rows of the market ledger (for the Money-ledger table). Newest-validated
    first. Optional verdict filter (CONFIRMED / NOT_CONFIRMED / NO_MOVE)."""
    conn = _connect(db_path)
    try:
        q = "SELECT * FROM market_accuracy_ledger"
        params = ()
        if verdict:
            q += (" WHERE verdict=%s" if db_compat.USE_PG else " WHERE verdict=?")
            params = (verdict,)
        q += " ORDER BY validated_at DESC"
        q += f" LIMIT {int(limit)}"
        rows = [dict(r) for r in conn.execute(q, params).fetchall()]
    except Exception as e:
        print(f"[mkt-ledger] detail error: {e}")
        rows = []
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return {"rows": rows, "count": len(rows)}


if __name__ == "__main__":
    import json
    init_market_ledger_db()
    print(json.dumps(report(), indent=2))
