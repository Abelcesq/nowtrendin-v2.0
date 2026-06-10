"""
================================================================
NOW TRENDIN — ACCURACY LEDGER ENHANCEMENT
Honest Denominator: Counting the Misses
================================================================

EXTENDS (does not replace) google_trends_validation.py.

THE PROBLEM THIS FIXES:
  The base ledger recorded topics that broke out (LED / LAGGED) but
  let topics that NEVER broke out sit in "pre-breakout" forever. That
  is survivorship bias — counting only the wins. A "90% hit rate" that
  silently excludes every fizzled call is marketing, not measurement,
  and the first institutional analyst who asks "how many did you flag
  that went nowhere?" exposes it instantly.

THE FIX (three parts):
  1. PENDING TRACKING — every detection is logged as "pending" with a
     timeout deadline (detection_date + N days).
  2. TIMEOUT SWEEP — a periodic pass that resolves pending detections:
        broke out      → record LED / LAGGED / SAME_DAY (a real verdict)
        timed out      → record FALSE_POSITIVE (a counted miss)
        still in window → leave pending
  3. HONEST REPORT — hit rate = hits / (hits + ALL misses), where misses
     include both LAGGED (we were late) and FALSE_POSITIVE (never broke
     out). Leads with MEDIAN lead time. Prints sample size. Flags small
     samples instead of presenting a percentage as settled.

WHY IT MATTERS:
  An honest ledger that admits its misses is far more sellable than a
  perfect-looking one nobody believes. This is the calibration that
  turns the ledger from a highlight reel into a track record an
  institution can act on — and it aligns with the integrity standard
  the whole product is built on.

INTEGRATION:
  When the scorer first logs a high-confidence detection:
      from accuracy_ledger_enhanced import record_detection
      record_detection(topic_key, topic_display, detection_date,
                       detection_score, timeout_days=90)
  On a daily scheduler job:
      python accuracy_ledger_enhanced.py --sweep
      python accuracy_ledger_enhanced.py --report
================================================================
"""

import os
import sqlite3
import hashlib
import argparse
import statistics
from datetime import datetime, timezone, timedelta
from typing import Optional

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

# Default window: if a detected topic hasn't broken out within this many
# days, it is recorded as a false positive (a counted miss).
DEFAULT_TIMEOUT_DAYS = 90

# Pull breakout/lead-time logic from the base module. Fall back to local
# stubs so this file runs standalone for the demo if the base isn't present.
try:
    from google_trends_validation import (
        fetch_trends_curve, detect_breakout_date, compute_lead_time,
        init_ledger_db, record_validation,
    )
    _HAS_BASE = True
except Exception:
    _HAS_BASE = False


# ════════════════════════════════════════════════════════════════
# SECTION 1: PENDING-DETECTION TRACKING
# ════════════════════════════════════════════════════════════════

def init_pending_db(db_path: str = DB_PATH):
    """Create the pending-detections table and ensure the ledger exists."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pending_detections (
            id TEXT PRIMARY KEY,
            topic_key TEXT,
            topic_display TEXT,
            detection_date TEXT,
            detection_score REAL,
            timeout_date TEXT,
            last_checked TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    # Ensure the ledger table exists (mirrors the base module's schema,
    # extended to allow FALSE_POSITIVE rows with null breakout fields).
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accuracy_ledger (
            id TEXT PRIMARY KEY,
            topic_key TEXT,
            topic_display TEXT,
            detection_date TEXT,
            detection_score REAL,
            breakout_date TEXT,
            breakout_multiple REAL,
            lead_time_days INTEGER,
            verdict TEXT,
            validated_at TEXT,
            provider TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pending_status ON pending_detections(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ledger_verdict2 ON accuracy_ledger(verdict)")
    conn.commit()
    conn.close()


def record_detection(topic_key: str, topic_display: str,
                    detection_date: str, detection_score: float,
                    timeout_days: int = DEFAULT_TIMEOUT_DAYS,
                    db_path: str = DB_PATH):
    """
    Log a detection as PENDING the moment the engine flags it.

    This starts the clock. The topic will later resolve to a hit
    (LED/LAGGED) or a counted miss (FALSE_POSITIVE) via the sweep.
    Idempotent on (topic_key, detection_date) so re-runs don't duplicate.
    """
    conn = sqlite3.connect(db_path)
    now = datetime.now(timezone.utc).isoformat()
    try:
        det_dt = _parse(detection_date)
        timeout_dt = (det_dt + timedelta(days=timeout_days)).isoformat()
    except Exception:
        timeout_dt = None

    rec_id = hashlib.md5(f"{topic_key}-{detection_date}".encode()).hexdigest()[:16]

    # Don't re-open something already resolved
    existing = conn.execute(
        "SELECT status FROM pending_detections WHERE id = ?", (rec_id,)
    ).fetchone()
    if existing:
        conn.close()
        return

    conn.execute("""
        INSERT OR IGNORE INTO pending_detections
            (id, topic_key, topic_display, detection_date, detection_score,
             timeout_date, last_checked, status)
        VALUES (?,?,?,?,?,?,?, 'pending')
    """, (rec_id, topic_key, topic_display, detection_date,
          detection_score, timeout_dt, now))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════════
# SECTION 2: THE TIMEOUT SWEEP
# Resolves pending detections into hits or counted misses.
# ════════════════════════════════════════════════════════════════

def _write_false_positive(conn, p: dict):
    """Record a timed-out detection as a counted miss."""
    now = datetime.now(timezone.utc).isoformat()
    rec_id = hashlib.md5(f"fp-{p['topic_key']}-{p['detection_date']}".encode()).hexdigest()[:16]
    conn.execute("""
        INSERT OR REPLACE INTO accuracy_ledger
            (id, topic_key, topic_display, detection_date, detection_score,
             breakout_date, breakout_multiple, lead_time_days, verdict,
             validated_at, provider)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (rec_id, p["topic_key"], p["topic_display"], p["detection_date"],
          p["detection_score"], None, None, None, "FALSE_POSITIVE",
          now, "timeout"))


def sweep_pending(db_path: str = DB_PATH,
                 breakout_threshold: float = 2.5,
                 fetch_fn=None) -> dict:
    """
    Resolve every pending detection.

    For each pending topic:
      - fetch its trends curve and look for a breakout
      - if it broke out → record LED / LAGGED / SAME_DAY, mark resolved
      - elif past its timeout date → record FALSE_POSITIVE, mark resolved
      - else → still in window, update last_checked, leave pending

    fetch_fn lets the demo inject a mock; production uses the base module.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    pending = [dict(r) for r in conn.execute(
        "SELECT * FROM pending_detections WHERE status = 'pending'"
    ).fetchall()]

    fetch = fetch_fn or (fetch_trends_curve if _HAS_BASE else None)
    now = datetime.now(timezone.utc)

    resolved_led = resolved_lagged = resolved_same = resolved_fp = still_pending = 0

    for p in pending:
        curve = fetch(p["topic_display"]) if fetch else None
        breakout = detect_breakout_date(curve, breakout_threshold) if (curve and _HAS_BASE) else \
                   (_local_detect_breakout(curve, breakout_threshold) if curve else None)

        if breakout:
            lead = (compute_lead_time(p["detection_date"], breakout) if _HAS_BASE
                    else _local_lead_time(p["detection_date"], breakout))
            if lead:
                _write_verdict(conn, p, breakout, lead)
                conn.execute("UPDATE pending_detections SET status='resolved' WHERE id=?", (p["id"],))
                if   lead["verdict"] == "LED":      resolved_led += 1
                elif lead["verdict"] == "LAGGED":   resolved_lagged += 1
                else:                               resolved_same += 1
                continue

        # No breakout — check timeout
        timed_out = False
        if p.get("timeout_date"):
            try:
                timed_out = now > _parse(p["timeout_date"])
            except Exception:
                timed_out = False

        if timed_out:
            _write_false_positive(conn, p)
            conn.execute("UPDATE pending_detections SET status='resolved' WHERE id=?", (p["id"],))
            resolved_fp += 1
        else:
            conn.execute("UPDATE pending_detections SET last_checked=? WHERE id=?",
                        (now.isoformat(), p["id"]))
            still_pending += 1

    conn.commit()
    conn.close()
    return {
        "resolved_led": resolved_led, "resolved_lagged": resolved_lagged,
        "resolved_same_day": resolved_same, "resolved_false_positive": resolved_fp,
        "still_pending": still_pending,
    }


def _write_verdict(conn, p: dict, breakout: dict, lead: dict):
    now = datetime.now(timezone.utc).isoformat()
    rec_id = hashlib.md5(f"{p['topic_key']}-{p['detection_date']}".encode()).hexdigest()[:16]
    conn.execute("""
        INSERT OR REPLACE INTO accuracy_ledger
            (id, topic_key, topic_display, detection_date, detection_score,
             breakout_date, breakout_multiple, lead_time_days, verdict,
             validated_at, provider)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (rec_id, p["topic_key"], p["topic_display"], p["detection_date"],
          p["detection_score"], lead["breakout_date"],
          breakout.get("multiple"), lead["lead_time_days"], lead["verdict"],
          now, "sweep"))


# ════════════════════════════════════════════════════════════════
# SECTION 3: THE HONEST REPORT
# ════════════════════════════════════════════════════════════════

def generate_honest_report(db_path: str = DB_PATH) -> dict:
    """
    The corrected accuracy report — counts the misses in the denominator.

    hits          = LED (provided genuine lead time)
    same_day      = SAME_DAY (detected on the breakout day)
    misses        = LAGGED (we were late) + FALSE_POSITIVE (never broke out)
    honest_hit_rate = hits / (hits + same_day + misses)
    Leads with MEDIAN lead time; prints sample size; flags small samples.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM accuracy_ledger").fetchall()]
    pending = conn.execute(
        "SELECT COUNT(*) FROM pending_detections WHERE status='pending'"
    ).fetchone()[0]
    conn.close()

    led   = [r for r in rows if r["verdict"] == "LED"]
    same  = [r for r in rows if r["verdict"] == "SAME_DAY"]
    lag   = [r for r in rows if r["verdict"] == "LAGGED"]
    fp    = [r for r in rows if r["verdict"] == "FALSE_POSITIVE"]

    resolved = len(led) + len(same) + len(lag) + len(fp)
    if resolved == 0:
        return {"status": "empty",
                "message": "No resolved predictions yet.",
                "pending": pending}

    lead_times = [r["lead_time_days"] for r in led if r["lead_time_days"] is not None]

    honest_hit_rate = round(len(led) / resolved * 100, 1)
    # The survivorship-biased number, shown ONLY to illustrate the gap:
    naive_denom = len(led) + len(same) + len(lag)   # excludes false positives
    naive_hit_rate = round(len(led) / naive_denom * 100, 1) if naive_denom else 0.0

    small_sample = resolved < 20

    return {
        "status":              "ok",
        "sample_size":         resolved,           # resolved predictions
        "still_pending":       pending,
        "hits_led":            len(led),
        "same_day":            len(same),
        "misses_lagged":       len(lag),
        "misses_false_positive": len(fp),
        "honest_hit_rate_pct": honest_hit_rate,    # the real number
        "naive_hit_rate_pct":  naive_hit_rate,     # what survivorship bias showed
        "median_lead_days":    round(statistics.median(lead_times), 1) if lead_times else 0,
        "mean_lead_days":      round(statistics.mean(lead_times), 1) if lead_times else 0,
        "max_lead_days":       max(lead_times) if lead_times else 0,
        "small_sample_warning": small_sample,
        "best": sorted(
            [{"topic": r["topic_display"], "lead_days": r["lead_time_days"]}
             for r in led], key=lambda x: x["lead_days"], reverse=True)[:5],
    }


def print_honest_report(db_path: str = DB_PATH):
    r = generate_honest_report(db_path)
    print("\n" + "="*64)
    print("NOW TRENDIN — ACCURACY LEDGER (honest)")
    print("="*64)
    if r["status"] != "ok":
        print(f"  {r.get('message')}  (pending: {r.get('pending',0)})")
        print("="*64); return

    print(f"  Sample size: {r['sample_size']} resolved predictions"
          f"  ({r['still_pending']} still in flight)")
    if r["small_sample_warning"]:
        print(f"  ⚠ Small sample — treat percentages as provisional until 20+.")
    print("-"*64)
    print(f"  Hits (LED, gave lead time):     {r['hits_led']}")
    print(f"  Same-day:                       {r['same_day']}")
    print(f"  Misses — lagged (we were late): {r['misses_lagged']}")
    print(f"  Misses — never broke out (FP):  {r['misses_false_positive']}")
    print("-"*64)
    print(f"  HONEST HIT RATE: {r['honest_hit_rate_pct']}%   "
          f"(counts every miss in the denominator)")
    print(f"  (survivorship-biased number would have read {r['naive_hit_rate_pct']}%)")
    print("-"*64)
    print(f"  MEDIAN lead time: {r['median_lead_days']} days   "
          f"(mean {r['mean_lead_days']}, max {r['max_lead_days']})")
    if r["best"]:
        print(f"  Best calls:")
        for b in r["best"]:
            print(f"    · {b['topic']}: {b['lead_days']} days early")
    print("="*64)


# ════════════════════════════════════════════════════════════════
# SECTION 4: LOCAL HELPERS (parsing + standalone-demo fallbacks)
# ════════════════════════════════════════════════════════════════

def _parse(date_str: str) -> datetime:
    s = date_str.strip().replace("Z", "")
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M", "%b %d, %Y", "%m/%d/%Y"):
        try:
            base = s.split("T")[0] if (fmt == "%Y-%m-%d" and "T" in s) else s
            return datetime.strptime(base, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


def _local_detect_breakout(curve, threshold):
    """Minimal breakout detector for standalone demo (base module mirrors this)."""
    if not curve or len(curve) < 5:
        return None
    vals = [p["value"] for p in curve]
    s = sorted(vals)
    baseline = max(1.0, statistics.mean(s[:max(2, int(len(s)*0.4))]))
    thr = baseline * threshold
    for i in range(len(curve) - 2):
        if vals[i] >= thr and vals[i+1] >= thr*0.8 and vals[i+2] >= thr*0.7:
            return {"breakout_date": curve[i]["date"], "breakout_value": vals[i],
                    "baseline_mean": round(baseline,1),
                    "multiple": round(vals[i]/baseline,1), "breakout_index": i}
    return None


def _local_lead_time(detection_date, breakout):
    try:
        d = _parse(detection_date); b = _parse(breakout["breakout_date"])
    except Exception:
        return None
    days = (b - d).days
    verdict = "LED" if days > 0 else ("SAME_DAY" if days == 0 else "LAGGED")
    return {"lead_time_days": days, "detection_date": detection_date,
            "breakout_date": breakout["breakout_date"],
            "breakout_multiple": breakout.get("multiple"), "verdict": verdict}


# ════════════════════════════════════════════════════════════════
# SECTION 5: DEMO — shows the honest vs survivorship-biased hit rate
# ════════════════════════════════════════════════════════════════

def run_demo():
    import tempfile
    fd, tmp = tempfile.mkstemp(suffix=".db"); os.close(fd)
    init_pending_db(tmp)

    base = datetime(2026, 1, 1)
    def d(n): return (base + timedelta(days=n)).strftime("%Y-%m-%d")

    # Log 14 detections: 5 will break out early, 1 will lag, 8 will fizzle
    breakouts = {}   # topic -> trends curve, for the mock fetch

    def curve_breaking_at(start_day, offset):
        """Flat baseline then a breakout `offset` days after detection."""
        pts = []
        for i in range(40):
            v = 3 if i < offset else min(95, 8 + (i-offset)*12)
            pts.append({"date": d(start_day + i), "value": v})
        return pts

    # 5 genuine early calls (LED) with various lead times
    for k, off in [("agentic coding", 8), ("agent memory", 12),
                   ("12-factor agents", 5), ("on-device ai", 15),
                   ("context engineering", 6)]:
        record_detection(k, k, d(0), 90, timeout_days=90, db_path=tmp)
        breakouts[k] = curve_breaking_at(0, off)

    # 1 LAGGED — Google broke out BEFORE detection
    record_detection("late topic", "late topic", d(20), 75, timeout_days=90, db_path=tmp)
    lc = [{"date": d(i), "value": (3 if i < 10 else 80)} for i in range(40)]
    breakouts["late topic"] = lc   # breakout ~day 10, detection day 20 → lagged

    # 8 FALSE POSITIVES — flagged, never broke out (flat curve), timed out
    for i in range(8):
        k = f"fizzle {i+1}"
        # detection 100 days ago so it's past the 90-day timeout
        det = (datetime.now(timezone.utc) - timedelta(days=100)).strftime("%Y-%m-%d")
        record_detection(k, k, det, 80, timeout_days=90, db_path=tmp)
        breakouts[k] = [{"date": d(j), "value": 3} for j in range(40)]  # never breaks out

    def mock_fetch(topic):
        return breakouts.get(topic)

    print("\nSweeping 14 pending detections (5 hits, 1 lagged, 8 fizzles)...")
    result = sweep_pending(db_path=tmp, fetch_fn=mock_fetch)
    print(f"  Resolved: {result}")

    print_honest_report(tmp)

    print("\nThe point: survivorship bias would have advertised a ~83% hit rate")
    print("(5 of 6 that broke out). The honest rate counts the 8 fizzles too —")
    print("a very different, but defensible, number an institution will trust.")

    os.unlink(tmp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sweep", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    init_pending_db(DB_PATH)
    if args.sweep:
        print(sweep_pending(DB_PATH))
    elif args.report:
        print_honest_report(DB_PATH)
    else:
        run_demo()
