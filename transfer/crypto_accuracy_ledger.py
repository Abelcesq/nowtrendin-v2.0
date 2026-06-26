"""
NOW TRENDIN — CRYPTO ACCURACY LEDGER (the Crypto Money Gradient's track record)

DISTINCT from both the attention ledger (Google Trends) AND the market ledger (equity EOD price).
Same honest philosophy, crypto-native ground truth:

  • Trends ledger   : attention moving toward a topic   → Google Trends breakout
  • Market ledger   : money moving in/out of an EQUITY  → realized EOD equity close direction (FMP/Databento)
  • THIS ledger     : MONEY moving in/out of a COIN     → realized COIN close direction (FMP crypto + AV)

The crypto Money Movement (D) read — informed money via crypto-EXPOSURE proxies (spot-ETF 13F +
MSTR/COIN insider) — makes a directional claim per coin (inflow / outflow). Ground truth = whether the
COIN's own price subsequently moved that way, and how many days after (the lead). NOT Google Trends
(attention) and NOT equity price — a coin's own realized price is the only honest validator of a crypto
money-movement read.

THIS IS MEASUREMENT, NOT ADVICE — no buy/sell, no price prediction. It keeps a falsifiable record of
whether OUR crypto reads corresponded to (and preceded) the realized coin move. A verdict about our
accuracy, never a call to the user.

INTEGRITY:
  • NO LOOKAHEAD — only price on/after detection_date is used (proxy 13F/insider are PUBLIC filings).
  • Honest denominator — counts NOT_CONFIRMED + NO_MOVE, not just wins.
  • Forward-only, additive — its own tables; touches nothing in the score or the other ledgers.
  • Held-out / flag-gated — only records when CRYPTO_SIGNAL=1; degrades gracefully when prices are absent.
  • Crypto move threshold is higher than equities (coins are far more volatile) so noise isn't scored.

Postgres-safe via db_compat (same idioms as market_accuracy_ledger).
"""
import os
import hashlib
import statistics
from datetime import datetime, timezone, timedelta
from typing import Optional

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
CRYPTO_TIMEOUT_DAYS = int(os.getenv("CRYPTO_LEDGER_TIMEOUT_DAYS", "45"))      # coins move faster than stocks
# % move from the detection-day close that counts as a real DIRECTIONAL move above crypto noise.
# Higher than the equity ledger (5%) because crypto is ~3-5x more volatile — keeps noise out of the record.
CRYPTO_MOVE_THRESHOLD_PCT = float(os.getenv("CRYPTO_MOVE_THRESHOLD_PCT", "8.0"))
# Minimum Money Movement (D) score for a read to be worth logging — only meaningful informed-money
# detections get a falsifiable record (a weak/quiet D read claims nothing).
CRYPTO_MIN_MM = float(os.getenv("CRYPTO_LEDGER_MIN_MM", "40"))
_MAX_SKIP = 4   # crypto trades 7 days/wk, but FMP can gap — small forward skip to the next close


def _connect(db_path: str = DB_PATH):
    conn = db_compat.connect(db_path)
    if not db_compat.USE_PG:
        try:
            import sqlite3
            conn.row_factory = sqlite3.Row
        except Exception:
            pass
    return conn


def _crypto_price_fetch(coin: str, frm: str, to: str):
    """Ground-truth COIN closes {YYYY-MM-DD: close} — FMP crypto (BTCUSD…) primary, AV
    DIGITAL_CURRENCY fallback. Reuses the same price helpers as the live signal. Referee only."""
    px = None
    try:
        import crypto_signals as cs
        import fmp_data
        c = cs.COIN_UNIVERSE.get((coin or "").upper())
        sym = (c or {}).get("fmp") or (f"{coin.upper()}USD" if coin else "")
        if sym:
            px = fmp_data.historical_close(sym, frm=frm, to=to)
        if not px:                                  # FMP throttled/empty → AV crypto fallback
            av = cs._av_crypto_series(coin)
            if av:
                px = {d: v for d, v in av.items() if frm <= d <= to} or av
    except Exception as e:
        print(f"[crypto-ledger] price {coin}: {e}")
    return px


def init_crypto_ledger_db(db_path: str = DB_PATH):
    conn = db_compat.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS crypto_pending_detections (
            id TEXT PRIMARY KEY, coin TEXT, name TEXT,
            detection_date TEXT, flow TEXT, money_movement REAL,
            timeout_date TEXT, last_checked TEXT, status TEXT DEFAULT 'pending')
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS crypto_accuracy_ledger (
            id TEXT PRIMARY KEY, coin TEXT, name TEXT,
            detection_date TEXT, flow TEXT, money_movement REAL,
            price_at_detection REAL, price_at_move REAL, price_change_pct REAL,
            move_date TEXT, lead_time_days INTEGER, verdict TEXT, validated_at TEXT)
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_crypto_pending_status ON crypto_pending_detections(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_crypto_ledger_verdict ON crypto_accuracy_ledger(verdict)")
    conn.commit()
    conn.close()


def _parse(date_str: str) -> datetime:
    s = (date_str or "").strip().replace("Z", "")
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M"):
        try:
            base = s.split("T")[0] if (fmt == "%Y-%m-%d" and "T" in s) else s
            return datetime.strptime(base, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


def _close_on_or_after(px: dict, date_str: str, max_skip: int = _MAX_SKIP):
    try:
        d0 = _parse(date_str)
    except Exception:
        return None, None
    for i in range(max_skip):
        k = (d0 + timedelta(days=i)).strftime("%Y-%m-%d")
        if k in px:
            return px[k], k
    return None, None


def record_crypto_detection(coin, name, detection_date, flow, money_movement,
                            db_path=DB_PATH, conn=None, gate=True):
    """Log a crypto MONEY-MOVEMENT (D) detection as PENDING. Idempotent on (coin, detection_date, flow);
    at most ONE open detection per (coin, flow) — a persistent read is the same ongoing signal, not many.
    flow MUST be directional ('inflow'/'outflow'). When gate=True the money_movement floor applies;
    record_from_serve passes gate=False (it already gated on the baseline-independent proxy intensity)."""
    flow = (flow or "").lower().strip()
    cn = (coin or "").upper().strip()
    if flow not in ("inflow", "outflow") or not cn:
        return
    if gate:
        try:
            if money_movement is not None and float(money_movement) < CRYPTO_MIN_MM:
                return
        except (TypeError, ValueError):
            pass
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
        timeout_dt = (_parse(detection_date) + timedelta(days=CRYPTO_TIMEOUT_DAYS)).isoformat()
    except Exception:
        timeout_dt = None
    rec_id = hashlib.md5(f"{cn}-{detection_date}-{flow}".encode()).hexdigest()[:16]
    try:
        open_same = conn.execute(
            ("SELECT 1 FROM crypto_pending_detections WHERE coin=%s AND flow=%s AND status='pending' LIMIT 1")
            if db_compat.USE_PG else
            ("SELECT 1 FROM crypto_pending_detections WHERE coin=? AND flow=? AND status='pending' LIMIT 1"),
            (cn, flow)).fetchone()
        if open_same:
            return
        ex = conn.execute("SELECT status FROM crypto_pending_detections WHERE id=%s" if db_compat.USE_PG
                          else "SELECT status FROM crypto_pending_detections WHERE id=?",
                          (rec_id,)).fetchone()
        if not ex:
            conn.execute("""
                INSERT OR IGNORE INTO crypto_pending_detections
                    (id, coin, name, detection_date, flow, money_movement, timeout_date, last_checked, status)
                VALUES (?,?,?,?,?,?,?,?,'pending')
            """, (rec_id, cn, name or cn, detection_date, flow,
                  float(money_movement) if money_movement is not None else None, timeout_dt, now))
            conn.commit()
    except Exception as e:
        print(f"[crypto-ledger] record error: {e}")
    finally:
        if own:
            conn.close()


def record_from_serve(payload: dict, db_path=DB_PATH) -> dict:
    """Record ledger detections from a serve_crypto() payload — the coin's MONEY MOVEMENT (D)
    direction = its Dark-Matter flow. The flow + proxy intensity are baseline-INDEPENDENT (the
    informed-money read), so a detection is a valid falsifiable claim even while the displayed
    baseline-relative TIER is still calibrating. Gated on directional flow + proxy intensity ≥
    CRYPTO_MIN_MM. Held-out: the caller gates on CRYPTO_SIGNAL."""
    init_crypto_ledger_db(db_path)
    n = 0
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = db_compat.connect(db_path)
    try:
        for c in (payload or {}).get("coins", []):
            dm = c.get("dark_matter") or {}
            flow = (dm.get("flow") or "").lower()             # informed-money (D) direction
            intensity = dm.get("intensity")                   # proxy DM strength (0-100), baseline-independent
            if flow not in ("inflow", "outflow"):
                continue
            try:
                if intensity is None or float(intensity) < CRYPTO_MIN_MM:
                    continue
            except (TypeError, ValueError):
                continue
            # Store the dual-ring Money Movement score as context; the gate above is on proxy intensity.
            record_crypto_detection(c.get("coin"), c.get("item_name"), today, flow,
                                    c.get("money_movement"), conn=conn, gate=False)
            n += 1
    finally:
        conn.close()
    return {"recorded": n}


def _upsert_ledger(conn, rec_id, p, price0, price1, change_pct, move_date, lead_days, verdict):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT INTO crypto_accuracy_ledger
            (id, coin, name, detection_date, flow, money_movement,
             price_at_detection, price_at_move, price_change_pct, move_date, lead_time_days, verdict, validated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT (id) DO UPDATE SET
            price_at_detection=EXCLUDED.price_at_detection, price_at_move=EXCLUDED.price_at_move,
            price_change_pct=EXCLUDED.price_change_pct, move_date=EXCLUDED.move_date,
            lead_time_days=EXCLUDED.lead_time_days, verdict=EXCLUDED.verdict, validated_at=EXCLUDED.validated_at
    """, (rec_id, p["coin"], p.get("name"), p["detection_date"], p.get("flow"),
          p.get("money_movement"), price0, price1, change_pct, move_date, lead_days, verdict, now))


def _evaluate(px: dict, p: dict):
    """Walk COIN closes forward from detection_date; first threshold crossed decides it (no cherry-pick).
    CONFIRMED = moved the detected way; NOT_CONFIRMED = moved opposite; PENDING = neither yet."""
    flow = p.get("flow")
    p0, d0 = _close_on_or_after(px, p["detection_date"])
    if p0 is None or p0 <= 0:
        return None
    up_lvl = p0 * (1.0 + CRYPTO_MOVE_THRESHOLD_PCT / 100.0)
    dn_lvl = p0 * (1.0 - CRYPTO_MOVE_THRESHOLD_PCT / 100.0)
    start = _parse(p["detection_date"])
    for d, px_close in sorted(px.items()):
        if d <= d0:
            continue                                      # no lookahead / no same-bar credit
        try:
            cur = float(px_close)
        except (TypeError, ValueError):
            continue
        crossed_up, crossed_dn = cur >= up_lvl, cur <= dn_lvl
        if not (crossed_up or crossed_dn):
            continue
        change_pct = round((cur - p0) / p0 * 100.0, 2)
        try:
            lead = (_parse(d) - start).days
        except Exception:
            lead = None
        matched = (flow == "inflow" and crossed_up) or (flow == "outflow" and crossed_dn)
        return ("CONFIRMED" if matched else "NOT_CONFIRMED", round(p0, 6), round(cur, 6), change_pct, d, lead)
    return ("PENDING", round(p0, 6), None, None, None, None)


def sweep_crypto_pending(db_path=DB_PATH, fetch_price_fn=None, limit=None) -> dict:
    """Resolve pending crypto detections vs realized coin price direction. Oldest-checked first;
    timeout → honest NO_MOVE; unpriceable past deadline → 'unpriced' (auditable, non-deleting)."""
    fetch = fetch_price_fn or _crypto_price_fetch
    conn = _connect(db_path)
    q = ("SELECT * FROM crypto_pending_detections WHERE status='pending' "
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
        px = None
        try:
            px = fetch(p["coin"], p["detection_date"], now.strftime("%Y-%m-%d"))
        except Exception:
            px = None
        if not px:
            conn.execute("UPDATE crypto_pending_detections SET status='unpriced' WHERE id=?" if timed_out
                         else "UPDATE crypto_pending_detections SET last_checked=? WHERE id=?",
                         ((p["id"],) if timed_out else (now.isoformat(), p["id"])))
            conn.commit(); unpriced += timed_out; still += (not timed_out); continue
        ev = _evaluate(px, p)
        if ev is None:
            conn.execute("UPDATE crypto_pending_detections SET status='unpriced' WHERE id=?" if timed_out
                         else "UPDATE crypto_pending_detections SET last_checked=? WHERE id=?",
                         ((p["id"],) if timed_out else (now.isoformat(), p["id"])))
            conn.commit(); unpriced += timed_out; still += (not timed_out); continue
        verdict, p0, p1, change_pct, move_date, lead = ev
        rec_id = hashlib.md5(f"{p['coin']}-{p['detection_date']}-{p.get('flow')}".encode()).hexdigest()[:16]
        if verdict == "PENDING":
            if timed_out:
                last_d = max(px.keys())
                try:
                    final = float(px[last_d]); change_pct = round((final - p0) / p0 * 100.0, 2)
                except Exception:
                    final = None
                _upsert_ledger(conn, rec_id, p, p0, final, change_pct, None, None, "NO_MOVE")
                conn.execute("UPDATE crypto_pending_detections SET status='resolved' WHERE id=?", (p["id"],))
                conn.commit(); no_move += 1
            else:
                conn.execute("UPDATE crypto_pending_detections SET last_checked=? WHERE id=?", (now.isoformat(), p["id"]))
                conn.commit(); still += 1
            continue
        _upsert_ledger(conn, rec_id, p, p0, p1, change_pct, move_date, lead, verdict)
        conn.execute("UPDATE crypto_pending_detections SET status='resolved' WHERE id=?", (p["id"],))
        conn.commit()
        confirmed += (verdict == "CONFIRMED"); not_conf += (verdict == "NOT_CONFIRMED")
    conn.close()
    out = {"resolved_confirmed": confirmed, "resolved_not_confirmed": not_conf,
           "resolved_no_move": no_move, "still_pending": still, "unpriced": unpriced}
    print(f"[crypto-ledger] sweep: {out}")
    return out


def report(db_path=DB_PATH) -> dict:
    """Honest accuracy report for the Crypto Money Gradient — hit_rate counts the misses too."""
    conn = _connect(db_path)
    try:
        rows = [dict(r) for r in conn.execute("SELECT * FROM crypto_accuracy_ledger").fetchall()]
    except Exception:
        rows = []
    try:
        pend = conn.execute("SELECT COUNT(*) FROM crypto_pending_detections WHERE status='pending'").fetchone()
        pending = (pend[0] if not isinstance(pend, dict) else list(pend.values())[0]) or 0
    except Exception:
        pending = 0
    conn.close()
    confirmed = [r for r in rows if r.get("verdict") == "CONFIRMED"]
    not_conf = [r for r in rows if r.get("verdict") == "NOT_CONFIRMED"]
    no_move = [r for r in rows if r.get("verdict") == "NO_MOVE"]
    resolved = len(confirmed) + len(not_conf) + len(no_move)
    leads = [r["lead_time_days"] for r in confirmed if r.get("lead_time_days") is not None]
    by_flow = {}
    for f in ("inflow", "outflow"):
        c = sum(1 for r in confirmed if r.get("flow") == f)
        nn = sum(1 for r in rows if r.get("flow") == f and r.get("verdict") in ("CONFIRMED", "NOT_CONFIRMED", "NO_MOVE"))
        by_flow[f] = {"confirmed": c, "resolved": nn, "confirm_rate_pct": round(100.0 * c / nn, 1) if nn else None}
    return {
        "ground_truth": "realized coin close direction (FMP crypto + AV)",
        "distinct_from": "trends ledger (Google Trends) AND market ledger (equity EOD price)",
        "move_threshold_pct": CRYPTO_MOVE_THRESHOLD_PCT, "timeout_days": CRYPTO_TIMEOUT_DAYS,
        "resolved": resolved, "pending": pending,
        "confirmed": len(confirmed), "not_confirmed": len(not_conf), "no_move": len(no_move),
        "confirm_rate_pct": round(100.0 * len(confirmed) / resolved, 1) if resolved else None,
        "median_lead_days": round(statistics.median(leads), 1) if leads else None,
        "by_flow": by_flow, "small_sample": resolved < 20,
        "note": "MEASUREMENT of the Crypto Money Gradient's own accuracy — did the coin's realized price "
                "move the way the detected informed-money flow indicated, and how many days after. NOT a "
                "forecast, NOT advice, NOT a buy/sell signal.",
    }


def detail(db_path=DB_PATH, limit=300, verdict=None) -> dict:
    conn = _connect(db_path)
    try:
        q = "SELECT * FROM crypto_accuracy_ledger"
        params = ()
        if verdict:
            q += (" WHERE verdict=%s" if db_compat.USE_PG else " WHERE verdict=?")
            params = (verdict,)
        q += f" ORDER BY validated_at DESC LIMIT {int(limit)}"
        rows = [dict(r) for r in conn.execute(q, params).fetchall()]
    except Exception as e:
        print(f"[crypto-ledger] detail error: {e}")
        rows = []
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return {"rows": rows, "count": len(rows)}


if __name__ == "__main__":
    import json
    init_crypto_ledger_db()
    print(json.dumps(report(), indent=2))
