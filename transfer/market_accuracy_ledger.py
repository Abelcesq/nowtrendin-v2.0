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


def _price_fetch(ticker: str, frm: str, to: str):
    """Default ground-truth price source: FMP daily EOD closes {YYYY-MM-DD: close}."""
    try:
        import fmp_data
        return fmp_data.historical_close(ticker, frm=frm, to=to)
    except Exception as e:
        print(f"[mkt-ledger] price fetch {ticker}: {e}")
        return None


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
        return  # only directional claims are falsifiable
    if not tkr:
        return
    try:
        if intensity is not None and float(intensity) < MIN_INTENSITY:
            return  # too weak to be a real money-movement detection
    except (TypeError, ValueError):
        pass
    if detection_score is None:
        try:
            detection_score = round(float(intensity) * 100.0, 1)
        except (TypeError, ValueError):
            detection_score = None
    # Canonicalize the detection date (§14) at the write boundary.
    try:
        from date_utils import to_iso_date
        detection_date = to_iso_date(detection_date) or detection_date
    except Exception:
        pass
    own = conn is None
    if own:
        conn = db_compat.connect(db_path)
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


def report(db_path=DB_PATH) -> dict:
    """Honest accuracy report for the Money Gradient. hit_rate counts the misses
    (NOT_CONFIRMED + NO_MOVE), never just the wins. MEASUREMENT of our own accuracy —
    not a forecast or advice."""
    conn = _connect(db_path)
    rows = [dict(r) for r in conn.execute("SELECT * FROM market_accuracy_ledger").fetchall()]
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
    return {
        "ground_truth": "realized EOD close direction (FMP)",
        "distinct_from": "trends accuracy ledger (Google Trends breakout)",
        "move_threshold_pct": MOVE_THRESHOLD_PCT,
        "timeout_days": MARKET_TIMEOUT_DAYS,
        "resolved": resolved,
        "confirmed": len(confirmed),
        "not_confirmed": len(not_conf),
        "no_move": len(no_move),
        "confirm_rate_pct": round(100.0 * len(confirmed) / resolved, 1) if resolved else None,
        "median_lead_days": round(statistics.median(leads), 1) if leads else None,
        "by_flow": by_flow,
        "small_sample": resolved < 20,
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
