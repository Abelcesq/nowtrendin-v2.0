"""
market_platform_indicator.py — N for the Market Signal surface. HELD-OUT.

WHAT THIS IS
────────────
The Market Signal mirror of the Trends "N · Platform Indicator": a
PLATFORM-TRACKING read of how often an instrument is triggered and surfaced as a
tracked item across NowTrendIn (the /risk feed, on-demand instrument lookups,
crypto rails, grades). Same system values as the topic-side N — identical 0-100
formula, identical bands, identical vocabulary — so a user who has learned to
read N on Trends reads it the same way on Market Signal.

WHAT IT IS NOT — THE INTEGRITY LINE (founder instruction, 2026-08-19)
─────────────────────────────────────────────────────────────────────
N NEVER TOUCHES A SCORE. Not money_movement, not market_confirmation, not the
tier, not the lead, not any component or baseline. It is platform-internal with
NO public source, and a score can never be validated by a signal produced by
engagement with that score — that is the circularity the integrity standard
bans outright. The same reasoning that keeps topic-N out of the Gradient Score
keeps instrument-N out of the Money Gradient.

This is enforced as a MECHANISM, not a promise:
  • this module is registered in heldout_registry.HELD_OUT_ARRIVAL_INPUTS, and
    market_signal_engine / crypto_money_gradient are SCORING_MODULES — so the
    AST firewall audit FAILS the build if a scoring module ever imports it;
  • nothing here reads or writes velocity_scores / market_signal_history /
    any ledger table — it owns exactly one table, instrument_queries;
  • test_market_platform_indicator.py proves the served money numbers are
    byte-identical with N present and with N absent.

WHAT USERS GET (the founder's "there is value in showing it")
─────────────────────────────────────────────────────────────
Three things, all clearly fenced as platform-internal:
  1. N itself (0-100) + its raw counts — an honest read of platform attention on
     the instrument, labelled as having no public source.
  2. An N-INCLUSIVE WHAT-IF pair (money+N / confirmation+N) shown in its own
     panel, never as the headline. The headline Money Movement / Market
     Confirmation stay N-free (external world only), exactly as Detection and
     Confidence do on Trends.
  3. A convergence line (RISING/FALLING · CONFIRMED/MIXED/CONFLICTING) comparing
     the platform's own tracking direction against the money read — which is
     interesting precisely BECAUSE it is independent of it.

FAIL-OPEN throughout: a logging or compute failure returns zero/None and never
raises into a serve path.
"""
from __future__ import annotations

import math
import os
import queue as _queue
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

# Same system values as the topic-side N (compute_nowtrendin_score) — deliberately
# identical so the two surfaces mean the same thing by the same arithmetic.
_VOL_MAX = 70.0          # volume component ceiling (0-70)
_VOL_REF = 100.0         # appearances that earn ~full volume score
_REC_MAX = 30.0          # recency component ceiling (0-30)

#: Repeat surfacings of the same instrument+endpoint inside this window count ONCE,
#: so N measures DISTINCT surfacing episodes rather than render loops. The topic
#: side ships this as an optional guard (N_QUERY_DEDUP_MIN, default off); the
#: market feed is prewarm-cached and re-served often, so it defaults ON here.
DEDUP_MIN = int(os.getenv("MARKET_N_DEDUP_MIN", "5"))

_q: "_queue.Queue[tuple]" = _queue.Queue(maxsize=10000)
_dedup_seen: dict = {}
_init_done = False
_init_lock = threading.Lock()
_log_failures = 0
_flusher_started = False


def _connect(db_path):
    conn = db_compat.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """Create instrument_queries (idempotent). Owns this table and nothing else."""
    global _init_done
    if _init_done:
        return
    with _init_lock:
        if _init_done:
            return
        conn = _connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS instrument_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    queried_at TEXT NOT NULL,
                    item_key TEXT NOT NULL,
                    endpoint TEXT
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_instrument_queries_key "
                        "ON instrument_queries (item_key, queried_at DESC)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_instrument_queries_recent "
                        "ON instrument_queries (queried_at DESC)")
            conn.commit()
            _init_done = True
        finally:
            conn.close()


# ── Logging (queue + background flusher, mirrors the topic-side pattern) ─────

def _ensure_flusher(db_path: Optional[str] = None) -> None:
    """Start the flusher on FIRST USE, never at boot.

    INCIDENT 2026-08-19: an earlier revision called init_db() synchronously in the
    API startup handler and started this thread there. That deploy failed to boot
    twice (R10, SIGKILL at 60s) and production was rolled back. The blocking call
    was never proven — which is exactly why this module no longer runs ANY code
    during startup. Schema creation and thread start happen lazily behind the
    first surfacing, off the critical path, so a slow or contended DDL can delay
    a display feature and nothing else. Boot must never wait on a display read.
    """
    global _flusher_started
    if _flusher_started:
        return
    # Resolve the path at CALL time, not at def time — a module-level default
    # argument would freeze whatever DB_PATH was when this file was imported.
    db_path = db_path or DB_PATH
    with _init_lock:
        if _flusher_started:
            return
        try:
            t = threading.Thread(target=flusher_loop, args=(db_path,), daemon=True,
                                 name="market-n-flusher")
            t.start()
            _flusher_started = True
        except Exception:
            pass


def log_query(item_key: str, endpoint: str = "/risk/scores") -> None:
    """Record one surfacing. Fail-open, non-blocking, dedup-guarded."""
    if not item_key:
        return
    try:
        _ensure_flusher()
        if DEDUP_MIN > 0:
            k = (item_key, endpoint)
            now_m = time.monotonic()
            last = _dedup_seen.get(k)
            if last is not None and (now_m - last) < DEDUP_MIN * 60:
                return
            _dedup_seen[k] = now_m
            if len(_dedup_seen) > 50000:
                _dedup_seen.clear()
        _q.put_nowait((datetime.now(timezone.utc).isoformat(), item_key, endpoint))
    except Exception:
        pass


def log_many(item_keys, endpoint: str = "/risk/scores") -> None:
    for k in (item_keys or []):
        log_query(k, endpoint)


def flusher_loop(db_path: str = DB_PATH) -> None:
    """Background daemon: batch-insert surfacing events. Own connection."""
    global _log_failures
    conn = None
    while True:
        try:
            first = _q.get(timeout=5)
        except _queue.Empty:
            continue
        batch = [first]
        while not _q.empty() and len(batch) < 200:
            try:
                batch.append(_q.get_nowait())
            except _queue.Empty:
                break
        try:
            init_db(db_path)
            if conn is None:
                conn = _connect(db_path)
            conn.executemany(
                "INSERT INTO instrument_queries (queried_at, item_key, endpoint) "
                "VALUES (?,?,?)", batch)
            conn.commit()
        except Exception as e:
            _log_failures += 1
            try:
                conn.close()
            except Exception:
                pass
            conn = None
            if _log_failures % 20 == 1:
                print(f"[market_n] flush failed ({_log_failures} total): {e}")


# ── The indicator ───────────────────────────────────────────────────────────

def compute(item_key: str, db_path: str = DB_PATH, conn=None) -> tuple:
    """N for one instrument → (score 0-100, detail dict).

    IDENTICAL formula to the topic-side N:
      volume  (0-70): log-scale of appearances in the last 30 days
      recency (0-30): last-24h rate vs the 7-day daily baseline
    Bands: 0 never surfaced · 1-20 rare · 20-50 moderate · 50-80 frequent ·
    80+ very frequently surfaced. Fail-open → (0.0, zeroed detail).
    """
    own = conn is None
    try:
        init_db(db_path)
        c = conn or _connect(db_path)
    except Exception:
        return 0.0, {"total_queries_30d": 0, "queries_7d": 0, "queries_24h": 0,
                     "daily_rate_7d": 0.0, "available": False}
    try:
        now = datetime.now(timezone.utc)
        c30 = (now - timedelta(days=30)).isoformat()
        c7 = (now - timedelta(days=7)).isoformat()
        c24 = (now - timedelta(hours=24)).isoformat()
        q = ("SELECT COUNT(*) AS c FROM instrument_queries "
             "WHERE item_key = ? AND queried_at >= ?")
        total_30d = c.execute(q, (item_key, c30)).fetchone()["c"] or 0
        recent_7d = c.execute(q, (item_key, c7)).fetchone()["c"] or 0
        recent_24h = c.execute(q, (item_key, c24)).fetchone()["c"] or 0
    except Exception:
        return 0.0, {"total_queries_30d": 0, "queries_7d": 0, "queries_24h": 0,
                     "daily_rate_7d": 0.0, "available": False}
    finally:
        if own:
            try:
                c.close()
            except Exception:
                pass

    vol = 0.0 if total_30d == 0 else min(
        _VOL_MAX, math.log1p(total_30d) / math.log1p(_VOL_REF) * _VOL_MAX)
    daily = recent_7d / 7.0
    if daily > 0 and recent_24h > daily:
        rec = min(_REC_MAX, (recent_24h / daily - 1.0) * 15)
    elif recent_24h > 0:
        rec = min(15.0, math.log1p(recent_24h) * 5)
    else:
        rec = 0.0
    return round(min(100.0, vol + rec), 2), {
        "total_queries_30d": total_30d,
        "queries_7d": recent_7d,
        "queries_24h": recent_24h,
        "daily_rate_7d": round(daily, 2),
        "available": True,
    }


def compute_many(item_keys, db_path: str = DB_PATH) -> dict:
    """N for a list of instruments in ONE connection (the feed path)."""
    out = {}
    try:
        init_db(db_path)
        conn = _connect(db_path)
    except Exception:
        return {k: 0.0 for k in (item_keys or [])}
    try:
        for k in (item_keys or []):
            try:
                out[k] = compute(k, db_path=db_path, conn=conn)[0]
            except Exception:
                out[k] = 0.0
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return out


def band(n: float) -> str:
    n = float(n or 0)
    if n <= 0:
        return "never surfaced"
    if n < 20:
        return "rare"
    if n < 50:
        return "moderate"
    if n < 80:
        return "frequent"
    return "very frequent"


# ── The N-INCLUSIVE what-if (a SEPARATE read, never the headline) ────────────
# Mirrors the topic-side "N-Inclusive Gradient Score": the served headline stays
# N-free; this shows where the numbers WOULD land if the platform-tracking signal
# were folded in. Weights are the market twins of the topic weights and are
# scaled down when external evidence is thin, so platform tracking can never
# appear to lift an instrument that has little real-world footprint.
_N_MM_WEIGHT = float(os.getenv("MARKET_N_MM_WEIGHT", "0.12"))
_N_MC_WEIGHT = float(os.getenv("MARKET_N_MC_WEIGHT", "0.10"))
#: signal count at which N earns full what-if weight (thin-data reflexivity guard)
_N_SUFFICIENCY_FULL = float(os.getenv("MARKET_N_SUFFICIENCY_FULL", "20"))


def n_inclusive(money_movement, market_confirmation, n_val,
                signal_count=None) -> dict:
    """What-if pair with N folded in. NEVER stored, NEVER served as the headline,
    NEVER read by any scorer — a display-side companion to the real numbers.
    Returns {available, money_with_n, confirmation_with_n, tracking_driven, note}.
    money_movement may be None (D8 honest-absence) — then only confirmation is
    computed, because a null money read must stay null."""
    try:
        if n_val is None or market_confirmation is None:
            return {"available": False}
        n = max(0.0, min(100.0, float(n_val)))
        suff = max(0.0, min(1.0, float(signal_count or 0) / _N_SUFFICIENCY_FULL))
        w_mm, w_mc = _N_MM_WEIGHT * suff, _N_MC_WEIGHT * suff
        mc = max(0.0, min(100.0, float(market_confirmation)))
        out = {
            "available": True,
            "confirmation_with_n": round(mc * (1 - w_mc) + n * w_mc, 1),
            "money_with_n": None,
            "tracking_driven": False,
            "note": ("Separate what-if read. The served Money Movement and Market "
                     "Confirmation are N-free (external world only); this shows "
                     "where they would land with the platform-tracking signal "
                     "folded in. Platform-internal — no public source."),
        }
        if money_movement is not None:
            mm = max(0.0, min(100.0, float(money_movement)))
            out["money_with_n"] = round(mm * (1 - w_mm) + n * w_mm, 1)
            out["tracking_driven"] = bool(suff < 0.5 and n > mm)
        return out
    except Exception:
        return {"available": False}


def convergence(n_val, n_detail: dict, money_movement, market_confirmation) -> dict:
    """Platform-tracking direction vs the money read — informative precisely
    BECAUSE the two are independent. Read-only; feeds nothing.
      direction: RISING (24h rate above the 7-day baseline) / FALLING / STEADY
      agreement: CONFIRMED  — tracking and money point the same way
                 CONFLICTING — platform attention rising while money is quiet
                               (or the reverse)
                 MIXED       — neither clearly
    """
    try:
        d = n_detail or {}
        rate = float(d.get("daily_rate_7d") or 0.0)
        h24 = float(d.get("queries_24h") or 0.0)
        if rate <= 0 and h24 <= 0:
            return {"available": False}
        if rate > 0 and h24 > rate * 1.25:
            direction = "RISING"
        elif rate > 0 and h24 < rate * 0.75:
            direction = "FALLING"
        else:
            direction = "STEADY"
        money = money_movement if money_movement is not None else market_confirmation
        money = float(money or 0.0)
        hot = money >= 50.0
        if direction == "RISING" and hot:
            agree = "CONFIRMED"
        elif direction == "RISING" and not hot:
            agree = "CONFLICTING"
        elif direction == "FALLING" and hot:
            agree = "CONFLICTING"
        elif direction == "FALLING" and not hot:
            agree = "CONFIRMED"
        else:
            agree = "MIXED"
        return {"available": True, "direction": direction, "agreement": agree,
                "label": f"{direction} · {agree}"}
    except Exception:
        return {"available": False}


def payload(item_key: str, money_movement=None, market_confirmation=None,
            signal_count=None, db_path: str = DB_PATH, conn=None) -> dict:
    """The whole display block for one instrument, ready to serve."""
    n, detail = compute(item_key, db_path=db_path, conn=conn)
    return {
        "n": round(n),
        "n_exact": n,
        "band": band(n),
        "label": "Platform Indicator (N)",
        "definition": ("A platform-tracking signal — how often this instrument is "
                       "triggered and surfaced as a tracked item across the Now "
                       "TrendIn platform (feeds, lookups, grades). A "
                       "platform-internal read no public source has."),
        "held_out": True,
        "excluded_from_score": True,
        "detail": detail,
        "n_inclusive": n_inclusive(money_movement, market_confirmation, n,
                                   signal_count),
        "convergence": convergence(n, detail, money_movement, market_confirmation),
    }


def status(db_path: str = DB_PATH) -> dict:
    """Operational read for /diag."""
    try:
        init_db(db_path)
        conn = _connect(db_path)
    except Exception as e:
        return {"available": False, "reason": str(e)[:120]}
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS n, MIN(queried_at) AS first, MAX(queried_at) AS last "
            "FROM instrument_queries").fetchone()
        top = [dict(r) for r in conn.execute(
            "SELECT item_key, COUNT(*) AS c FROM instrument_queries "
            "WHERE queried_at >= ? GROUP BY item_key ORDER BY c DESC LIMIT 10",
            ((datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),)
        ).fetchall()]
        return {"available": True, "rows": row["n"], "first": row["first"],
                "last": row["last"], "queue_depth": _q.qsize(),
                "log_failures": _log_failures, "dedup_minutes": DEDUP_MIN,
                "top_30d": top,
                "held_out": "registered in heldout_registry; scoring modules may "
                            "not import this (AST-enforced)"}
    finally:
        conn.close()
