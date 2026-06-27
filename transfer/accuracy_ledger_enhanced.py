"""
NOW TRENDIN — ACCURACY LEDGER ENHANCEMENT (engine-native, db_compat)

Honest denominator: counts the MISSES, not just the wins.

Extends google_trends_validation.py. The base ledger recorded topics that broke
out (LED/LAGGED) but let fizzles sit in limbo forever — survivorship bias. This
adds:
  1. PENDING TRACKING  — record_detection() logs every flagged topic with a
     timeout deadline, starting the clock for every call.
  2. TIMEOUT SWEEP     — sweep_pending() resolves each pending detection:
        broke out → LED / LAGGED / SAME_DAY ; past deadline → FALSE_POSITIVE.
  3. HONEST REPORT     — hit rate = LED / (LED + SAME_DAY + LAGGED + FALSE_POSITIVE),
     leads with MEDIAN lead time, prints sample size, flags small samples.

Postgres-safe: upserts use explicit ON CONFLICT (db_compat turns the sqlite
'INSERT OR REPLACE' into a plain INSERT, which would dup-key on re-runs).
"""
import os
import hashlib
import statistics
from datetime import datetime, timezone, timedelta
from typing import Optional

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
DEFAULT_TIMEOUT_DAYS = int(os.getenv("LEDGER_TIMEOUT_DAYS", "90"))
MATCH_WINDOW_DAYS    = int(os.getenv("LEDGER_MATCH_WINDOW_DAYS", "30"))
LEDGER_PARAM_VERSION = "calib-params-v1"

try:
    from google_trends_validation import (
        fetch_trends_curve, detect_breakout_date, compute_lead_time,
    )
    _HAS_BASE = True
except Exception:
    _HAS_BASE = False


def init_pending_db(db_path: str = DB_PATH):
    conn = db_compat.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pending_detections (
            id TEXT PRIMARY KEY, topic_key TEXT, topic_display TEXT,
            detection_date TEXT, detection_score REAL, timeout_date TEXT,
            last_checked TEXT, status TEXT DEFAULT 'pending')
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accuracy_ledger (
            id TEXT PRIMARY KEY, topic_key TEXT, topic_display TEXT,
            detection_date TEXT, detection_score REAL, breakout_date TEXT,
            breakout_multiple REAL, lead_time_days INTEGER, verdict TEXT,
            validated_at TEXT, provider TEXT)
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pending_status ON pending_detections(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ledger_verdict2 ON accuracy_ledger(verdict)")
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


def record_detection(topic_key, topic_display, detection_date, detection_score,
                     timeout_days=DEFAULT_TIMEOUT_DAYS, db_path=DB_PATH, conn=None):
    """Log a detection as PENDING the moment the engine flags it. Idempotent on
    (topic_key, detection_date).

    This is the ATTENTION (Trends) ledger — validated by Google Trends breakout.
    Money-movement detections use a SEPARATE ledger (market_accuracy_ledger.py),
    validated by realized EOD price direction (FMP), NOT Google Trends."""
    # Sink-harden (quality): reject fragment/boilerplate non-topics at the WRITE boundary
    # so legacy-style junk ("sunday afternoon", "york for months", "every single") can
    # never enter the TRACKED ledger going forward — the same defense-at-the-boundary
    # principle as the date gate below and the catch-all corroboration floor. Same shared
    # gate every scorer uses, so a properly-scored topic always passes (no false drops).
    # Fail OPEN: if the gate can't be imported, never drop a real detection.
    try:
        from gravitational_anomaly_detector import _is_quality_topic as _qt
        if not _qt(topic_display or (topic_key or "").replace("_", " ")):
            print(f"[ledger] record_detection skipped non-quality topic: {topic_display!r}")
            return
    except Exception:
        pass
    own = conn is None
    if own:
        conn = db_compat.connect(db_path)
    # Sink-harden (§14): normalize to canonical 'YYYY-MM-DD' HERE too, so even a caller
    # that forgets to gate can't write a non-canonical detection_date. Defense at the
    # boundary (the same principle as the catch-all floor: enforce at the write, not
    # the caller). to_iso_date returns None on an unparseable value → keep the original
    # so the existing _parse-based behaviour/skip still applies.
    try:
        from date_utils import to_iso_date
        detection_date = to_iso_date(detection_date) or detection_date
    except Exception:
        pass
    now = datetime.now(timezone.utc).isoformat()
    try:
        timeout_dt = (_parse(detection_date) + timedelta(days=timeout_days)).isoformat()
    except Exception:
        timeout_dt = None
    rec_id = hashlib.md5(f"{topic_key}-{detection_date}".encode()).hexdigest()[:16]
    try:
        # Don't reopen something already resolved.
        ex = conn.execute("SELECT status FROM pending_detections WHERE id=%s" if db_compat.USE_PG
                          else "SELECT status FROM pending_detections WHERE id=?", (rec_id,)).fetchone()
        if not ex:
            conn.execute("""
                INSERT OR IGNORE INTO pending_detections
                    (id, topic_key, topic_display, detection_date, detection_score,
                     timeout_date, last_checked, status)
                VALUES (?,?,?,?,?,?,?,'pending')
            """, (rec_id, topic_key, topic_display, detection_date,
                  detection_score, timeout_dt, now))
            conn.commit()
    except Exception as e:
        print(f"[ledger] record_detection error: {e}")
    finally:
        if own:
            conn.close()


def _upsert_ledger(conn, rec_id, p, breakout_date, multiple, lead_days, verdict, provider):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT INTO accuracy_ledger
            (id, topic_key, topic_display, detection_date, detection_score,
             breakout_date, breakout_multiple, lead_time_days, verdict, validated_at, provider)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT (id) DO UPDATE SET
            breakout_date=EXCLUDED.breakout_date, breakout_multiple=EXCLUDED.breakout_multiple,
            lead_time_days=EXCLUDED.lead_time_days, verdict=EXCLUDED.verdict,
            validated_at=EXCLUDED.validated_at, provider=EXCLUDED.provider
    """, (rec_id, p["topic_key"], p["topic_display"], p["detection_date"],
          p["detection_score"], breakout_date, multiple, lead_days, verdict, now, provider))


def sweep_pending(db_path=DB_PATH, breakout_threshold=2.5, fetch_fn=None, limit=None) -> dict:
    """Resolve pending detections into hits or counted misses.

    ROTATION (fix #1): order by oldest-checked first (`last_checked` ASC, NULLs
    first) so each capped run advances through the WHOLE pool instead of re-hitting
    the same head-of-table rows every time — a `LIMIT n` with no order would re-check
    the first n forever and never reach the tail (where the slow-to-confirm LED wins
    sit). Every row that stays pending gets its `last_checked` stamped to `now`, which
    sends it to the back of the queue.

    TIMEOUT-FIRST (fix #2): a row already past its deadline is a FALSE_POSITIVE that
    needs NO Trends curve to confirm — resolve it before spending an Apify fetch, so
    the paid budget is spent only on rows that might still be breaking out."""
    if not _HAS_BASE:
        return {"available": False}
    conn = db_compat.connect(db_path)
    # Oldest-checked first; never-checked (NULL) rows lead. Portable across PG + SQLite
    # (avoids relying on NULLS FIRST support).
    q = ("SELECT * FROM pending_detections WHERE status='pending' "
         "ORDER BY (last_checked IS NULL) DESC, last_checked ASC")
    if limit:
        q += f" LIMIT {int(limit)}"
    pending = [dict(r) for r in conn.execute(q).fetchall()]
    fetch = fetch_fn or fetch_trends_curve
    now = datetime.now(timezone.utc)
    led = lagged = same = fp = still = late = excluded = 0
    # Shared quality gate (fail-open) — resolve LEGACY non-topics out of the pool WITHOUT
    # scoring them as predictions. A fragment that slipped in before the gate existed is
    # not a real detection, so timing it out as a FALSE_POSITIVE would corrupt the ledger's
    # honest denominator. Mark it 'excluded_nonquality' (non-deleting, auditable) instead.
    try:
        from gravitational_anomaly_detector import _is_quality_topic as _qt
    except Exception:
        _qt = None
    for p in pending:
        if _qt is not None:
            try:
                _disp = p.get("topic_display") or (p.get("topic_key") or "").replace("_", " ")
                if not _qt(_disp):
                    conn.execute(
                        "UPDATE pending_detections SET status='excluded_nonquality' WHERE id=?",
                        (p["id"],))
                    conn.commit()
                    excluded += 1
                    continue
            except Exception:
                pass
        # TIMEOUT-FIRST (free): past the deadline → FALSE_POSITIVE with no Trends fetch.
        timed_out = False
        if p.get("timeout_date"):
            try:
                timed_out = now > _parse(p["timeout_date"])
            except Exception:
                timed_out = False
        if timed_out:
            rec_id = hashlib.md5(f"fp-{p['topic_key']}-{p['detection_date']}".encode()).hexdigest()[:16]
            _upsert_ledger(conn, rec_id, p, None, None, None, "FALSE_POSITIVE", "timeout")
            conn.execute("UPDATE pending_detections SET status='resolved' WHERE id=?", (p["id"],))
            conn.commit()
            fp += 1
            continue
        # Still within the window → spend a Trends fetch to see if it has broken out.
        try:
            curve = fetch(p["topic_display"])
        except Exception:
            curve = None
        # SAME-SURGE FLOOR: match only a breakout on/after (detection − MATCH_WINDOW).
        # A breach earlier than that is a different, older surge (the −92d artifact),
        # so the engine no longer mis-matches a June detection to a Spring spike.
        since = None
        try:
            since = (_parse(p["detection_date"]) - timedelta(days=MATCH_WINDOW_DAYS)).date().isoformat()
        except Exception:
            since = None
        breakout = detect_breakout_date(curve, breakout_threshold, since=since) if curve else None
        if breakout:
            lead = compute_lead_time(p["detection_date"], breakout)
            if lead:
                # C1: reject cross-surge matches where the breakout date is outside
                # the detection window — e.g. nukes detected in June matching a Feb spike.
                if abs(lead["lead_time_days"]) > MATCH_WINDOW_DAYS:
                    rec_id = hashlib.md5(f"{p['topic_key']}-{p['detection_date']}".encode()).hexdigest()[:16]
                    _upsert_ledger(conn, rec_id, p, lead["breakout_date"], breakout.get("multiple"),
                                   lead["lead_time_days"], "LATE_REDETECTION", "sweep")
                    conn.execute("UPDATE pending_detections SET status='resolved' WHERE id=?", (p["id"],))
                    conn.commit()
                    late += 1
                    continue
                rec_id = hashlib.md5(f"{p['topic_key']}-{p['detection_date']}".encode()).hexdigest()[:16]
                _upsert_ledger(conn, rec_id, p, lead["breakout_date"], breakout.get("multiple"),
                               lead["lead_time_days"], lead["verdict"], "sweep")
                conn.execute("UPDATE pending_detections SET status='resolved' WHERE id=?", (p["id"],))
                conn.commit()
                if lead["verdict"] == "LED": led += 1
                elif lead["verdict"] == "LAGGED": lagged += 1
                else: same += 1
                continue
        # No breakout, not timed out → stays pending; stamp last_checked so rotation
        # moves past it to the next-oldest row on the following run.
        conn.execute("UPDATE pending_detections SET last_checked=? WHERE id=?",
                     (now.isoformat(), p["id"]))
        conn.commit()
        still += 1
    conn.close()
    out = {"resolved_led": led, "resolved_lagged": lagged, "resolved_same_day": same,
           "resolved_false_positive": fp, "resolved_late_redetection": late,
           "still_pending": still, "excluded_nonquality": excluded}
    print(f"[ledger] sweep: {out}")
    return out


def generate_honest_report(db_path=DB_PATH) -> dict:
    """Accuracy report with the misses counted in the denominator.

    SEGMENTED by topic MATURITY CLASS (topic_maturity.maturity_class): the product's claim
    is EARLY detection of EMERGING topics, so `early_detection_*` / by_maturity['emerging']
    is the meaningful headline. ESTABLISHED/MONITORING topics (e.g. 'world cup') broke out on
    Google Trends long before any first-sighting and can ONLY resolve LAGGED — they measure
    coverage latency, not the early-signal thesis, and drag the blended rate down. NOTHING is
    hidden: every cohort is reported. Maturity is the CURRENT class; held-out, score-neutral."""
    conn = db_compat.connect(db_path)
    try:
        rows = [dict(r) for r in conn.execute("SELECT * FROM accuracy_ledger").fetchall()]
        pending = conn.execute(
            "SELECT COUNT(*) AS c FROM pending_detections WHERE status='pending'").fetchone()["c"]
        # Current maturity class per topic (held-out, display-only segmentation source).
        mat = {}
        try:
            for _m in conn.execute("SELECT topic_key, maturity_class FROM topic_maturity").fetchall():
                _md = dict(_m); mat[_md.get("topic_key")] = (_md.get("maturity_class") or "").upper()
        except Exception:
            mat = {}
        # FALLBACK coverage from velocity_scores (365-day retention → covers EVERY ledger topic,
        # unlike topic_maturity which is sparse): a topic ever confirmed MAINSTREAM is one Google
        # Trends already knows, so it can only resolve LAGGED → established; an unconfirmed niche
        # topic → emerging. Used only where topic_maturity has no class. Threshold-free + held-out.
        vs_ms = {}
        try:
            tks = list({r.get("topic_key") for r in rows if r.get("topic_key")})
            if tks:
                ph = ",".join((["%s"] if db_compat.USE_PG else ["?"]) * len(tks))
                vq = ("SELECT topic_key, MAX(CASE WHEN mainstream_confirmed THEN 1 ELSE 0 END) AS ms "
                      f"FROM velocity_scores WHERE topic_key IN ({ph}) GROUP BY topic_key")
                for _v in conn.execute(vq, tuple(tks)).fetchall():
                    _vd = dict(_v); vs_ms[_vd.get("topic_key")] = int(_vd.get("ms") or 0)
        except Exception:
            vs_ms = {}
    except Exception:
        conn.close()
        return {"status": "empty", "message": "Ledger not initialised yet.", "pending": 0}
    conn.close()
    led = [r for r in rows if r["verdict"] == "LED"]
    same = [r for r in rows if r["verdict"] == "SAME_DAY"]
    lag = [r for r in rows if r["verdict"] == "LAGGED"]
    fp = [r for r in rows if r["verdict"] == "FALSE_POSITIVE"]
    # LATE_REDETECTION rows are excluded from the honest denominator (C1 gate).
    late = [r for r in rows if r["verdict"] == "LATE_REDETECTION"]
    resolved = len(led) + len(same) + len(lag) + len(fp)
    if resolved == 0:
        return {"status": "empty", "message": "No resolved predictions yet.", "pending": pending,
                "late_redetection_excluded": len(late), "param_version": LEDGER_PARAM_VERSION}
    lead_times = [r["lead_time_days"] for r in led if r["lead_time_days"] is not None]
    naive_denom = len(led) + len(same) + len(lag)

    # ── Maturity segmentation (held-out, display-only) ──────────────────────────────────
    # EARLY-DETECTION cohort = topics that were genuinely EMERGING (the product's claim);
    # ESTABLISHED ones can only resolve LAGGED. All cohorts reported (transparency).
    _RES = ("LED", "SAME_DAY", "LAGGED", "FALSE_POSITIVE")
    _EMERGING, _ESTABLISHED = {"NEW", "EMERGING", "RESURGENT"}, {"ESTABLISHED", "MONITORING"}
    def _cohort(tk):
        c = mat.get(tk, "")
        if c in _EMERGING:
            return "emerging"
        if c in _ESTABLISHED:
            return "established"
        # Fallback: a mainstream-confirmed topic is one Trends already knows → established.
        ms = vs_ms.get(tk)
        if ms == 1:
            return "established"
        if ms == 0:
            return "emerging"
        return "unknown"
    def _seg(name):
        sub = [r for r in rows if r["verdict"] in _RES and _cohort(r.get("topic_key")) == name]
        s_led = [r for r in sub if r["verdict"] == "LED"]
        s_leads = [r["lead_time_days"] for r in s_led if r["lead_time_days"] is not None]
        return {"resolved": len(sub), "led": len(s_led),
                "hit_rate_pct": round(len(s_led) / len(sub) * 100, 1) if sub else None,
                "median_lead_days": round(statistics.median(s_leads), 1) if s_leads else None}
    by_mat = {k: _seg(k) for k in ("emerging", "established", "unknown")}

    return {
        "status": "ok",
        "param_version": LEDGER_PARAM_VERSION,
        "sample_size": resolved,
        "still_pending": pending,
        "late_redetection_excluded": len(late),
        "hits_led": len(led), "same_day": len(same),
        "misses_lagged": len(lag), "misses_false_positive": len(fp),
        "honest_hit_rate_pct": round(len(led) / resolved * 100, 1),
        "naive_hit_rate_pct": round(len(led) / naive_denom * 100, 1) if naive_denom else 0.0,
        "median_lead_days": round(statistics.median(lead_times), 1) if lead_times else 0,
        "mean_lead_days": round(statistics.mean(lead_times), 1) if lead_times else 0,
        "max_lead_days": max(lead_times) if lead_times else 0,
        "small_sample_warning": resolved < 20,
        # Maturity-segmented — headline going forward = the EMERGING cohort (the product's claim).
        "by_maturity": by_mat,
        "maturity_source": "topic_maturity.maturity_class, else velocity_scores.mainstream_confirmed",
        "maturity_coverage": {"by_topic_maturity": sum(1 for r in rows if mat.get(r.get("topic_key"))),
                              "by_mainstream_fallback": sum(1 for r in rows if r.get("topic_key") in vs_ms),
                              "total_resolved_rows": len(rows)},
        "early_detection_hit_rate_pct": by_mat["emerging"]["hit_rate_pct"],
        "early_detection_sample": by_mat["emerging"]["resolved"],
        "best": sorted([{"topic": r["topic_display"], "lead_days": r["lead_time_days"]}
                        for r in led], key=lambda x: x["lead_days"] or 0, reverse=True)[:5],
    }
