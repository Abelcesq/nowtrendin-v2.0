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
# PATIENCE WINDOW (365d, 2026-06-27). The product tracks human attention BEFORE it reaches Google —
# and human attention can arrive MONTHS after our agents detect the dark matter. So we give every
# early detection a FULL YEAR to be confirmed by a later Google breakout before judging it a miss:
# "the big money is not in the buying and selling, but in the WAITING" (Munger). Integrity to our
# own system means never marking a detection FALSE_POSITIVE before human attention has had a real
# chance to arrive — we must not conclude the agents failed because we removed the data too early.
# Aligns with the 365-day velocity_scores retention (§13). HELD-OUT — affects measurement only,
# never a score. Shorten only with founder sign-off + a backtest of the denominator impact.
DEFAULT_TIMEOUT_DAYS = int(os.getenv("LEDGER_TIMEOUT_DAYS", "365"))
# BACKWARD stale-match floor stays TIGHT: a breakout more than this many days BEFORE detection is a
# different, older surge (the −92d cross-surge artifact), never a "lead". Asymmetric vs LEAD_MAX_DAYS.
MATCH_WINDOW_DAYS    = int(os.getenv("LEDGER_MATCH_WINDOW_DAYS", "30"))
# FORWARD lead window: a Google breakout up to this many days AFTER detection still counts as a
# genuine LED win (early detection of dark matter that took time to reach Google). Defaults to the
# full patience window so the wait horizon and the lead-credit horizon move together.
LEAD_MAX_DAYS        = int(os.getenv("LEDGER_LEAD_MAX_DAYS", str(DEFAULT_TIMEOUT_DAYS)))
LEDGER_PARAM_VERSION = "calib-params-v2-patience365"

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
    # Match-validity metadata (2026-07-07, measurement-only): the exact query the sweep
    # matched on, whether that query is generically AMBIGUOUS (a Trends curve for
    # 'mexico' is country-level noise — a breakout in it may not be OUR surge), and
    # whether an independent referee (Wikipedia pageviews) corroborated a win.
    # Idempotent ALTERs; each failure ROLLED BACK so a PG txn never aborts on the
    # duplicate-column error (the market-ledger startup lesson).
    for _col, _typ in (("sweep_query", "TEXT"),
                       ("query_ambiguous", "INTEGER"),
                       ("referee_corroborated", "INTEGER")):
        try:
            conn.execute(f"ALTER TABLE accuracy_ledger ADD COLUMN {_col} {_typ}")
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
    conn.close()


# ── Match validity: query ambiguity + independent referee ─────────────────────────────
# Bare geo/institution terms whose Trends curves aggregate unrelated attention.
_GENERIC_GEO = {
    "united states", "the us", "usa", "america", "new york", "white house",
    "washington", "europe", "china", "russia", "mexico", "spain", "france",
    "germany", "india", "japan", "brazil", "canada", "australia", "england",
    "london", "texas", "california", "florida", "congress", "senate",
}


def _query_ambiguity(display: str) -> int:
    """1 = the sweep query is generically ambiguous (single word, or a bare
    geo/institution term) — a breakout on its Trends curve is weak evidence the
    matched surge is OURS. Metadata only; changes no verdict."""
    d = (display or "").strip().lower()
    if not d:
        return 1
    if d in _GENERIC_GEO:
        return 1
    return 1 if len(d.split()) == 1 else 0


def _referee_corroborate(topic_display, detection_date, breakout_date):
    """Independent second referee (held-out): did Wikipedia pageviews ALSO show
    attention arriving near the Google breakout? 1 = arrival within ±14d of the
    breakout; 0 = referee readable but no matching arrival; None = referee
    unavailable/unresolvable (never blocks or changes a resolution). Free API."""
    try:
        import referee_wikipedia as _rw
        art = _rw.resolve_article(topic_display)
        if not art:
            return None
        det = _parse(detection_date)
        brk = _parse(breakout_date)
        curve = _rw.fetch_pageviews(art, det - timedelta(days=30), brk + timedelta(days=14))
        if not curve:
            return None
        arrival = _rw.detect_arrival_date(curve, since=(det - timedelta(days=30)).date().isoformat())
        if not arrival or not arrival.get("arrival_date"):
            return 0
        adt = _parse(arrival["arrival_date"])
        return 1 if abs((adt - brk).days) <= 14 else 0
    except Exception:
        return None


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


def _upsert_ledger(conn, rec_id, p, breakout_date, multiple, lead_days, verdict, provider,
                   sweep_query=None, query_ambiguous=None, referee_corroborated=None):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT INTO accuracy_ledger
            (id, topic_key, topic_display, detection_date, detection_score,
             breakout_date, breakout_multiple, lead_time_days, verdict, validated_at, provider,
             sweep_query, query_ambiguous, referee_corroborated)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT (id) DO UPDATE SET
            breakout_date=EXCLUDED.breakout_date, breakout_multiple=EXCLUDED.breakout_multiple,
            lead_time_days=EXCLUDED.lead_time_days, verdict=EXCLUDED.verdict,
            validated_at=EXCLUDED.validated_at, provider=EXCLUDED.provider,
            sweep_query=EXCLUDED.sweep_query, query_ambiguous=EXCLUDED.query_ambiguous,
            referee_corroborated=EXCLUDED.referee_corroborated
    """, (rec_id, p["topic_key"], p["topic_display"], p["detection_date"],
          p["detection_score"], breakout_date, multiple, lead_days, verdict, now, provider,
          sweep_query, query_ambiguous, referee_corroborated))


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
        # TIMEOUT-FIRST (free): past the deadline → FALSE_POSITIVE with no Trends fetch. Compute the
        # deadline LIVE from detection + DEFAULT_TIMEOUT_DAYS so the patience-window policy applies to
        # ALL pending rows — including the ~881 recorded under the old 90d default — not just new ones.
        timed_out = False
        try:
            timed_out = now > (_parse(p["detection_date"]) + timedelta(days=DEFAULT_TIMEOUT_DAYS))
        except Exception:
            try:
                timed_out = bool(p.get("timeout_date")) and now > _parse(p["timeout_date"])
            except Exception:
                timed_out = False
        if timed_out:
            rec_id = hashlib.md5(f"fp-{p['topic_key']}-{p['detection_date']}".encode()).hexdigest()[:16]
            _upsert_ledger(conn, rec_id, p, None, None, None, "FALSE_POSITIVE", "timeout")
            conn.execute("UPDATE pending_detections SET status='resolved' WHERE id=?", (p["id"],))
            conn.commit()
            fp += 1
            continue
        # Still within the window → spend a Trends fetch to see if it has broken out. Fetch a curve
        # long enough to span detection→now (+buffer) so a breakout arriving MONTHS after our
        # detection is still visible to match. Recent rows keep the 90d (daily-granularity) default;
        # older rows widen toward the patience window (coarser/weekly granularity — fine for long leads).
        try:
            _cdays = max(90, min(DEFAULT_TIMEOUT_DAYS + 35,
                                 (now - _parse(p["detection_date"])).days + 35))
        except Exception:
            _cdays = 90
        try:
            curve = fetch(p["topic_display"], days=_cdays)
        except TypeError:
            curve = fetch(p["topic_display"])   # an injected fetch_fn may not accept days=
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
                # C1 (ASYMMETRIC): reject a STALE BACK-match (a breakout long BEFORE detection is a
                # different, older surge — the −92d artifact), but ACCEPT a long FORWARD lead: an
                # early detection confirmed by a Google breakout up to LEAD_MAX_DAYS later is a
                # genuine LED win, not a re-detection. This is the patience principle in code — we do
                # NOT disqualify our own early read just because human attention took months to arrive.
                _lt = lead["lead_time_days"]
                _q = p["topic_display"]
                _amb = _query_ambiguity(_q)
                if _lt < -MATCH_WINDOW_DAYS or _lt > LEAD_MAX_DAYS:
                    rec_id = hashlib.md5(f"{p['topic_key']}-{p['detection_date']}".encode()).hexdigest()[:16]
                    _upsert_ledger(conn, rec_id, p, lead["breakout_date"], breakout.get("multiple"),
                                   lead["lead_time_days"], "LATE_REDETECTION", "sweep",
                                   sweep_query=_q, query_ambiguous=_amb)
                    conn.execute("UPDATE pending_detections SET status='resolved' WHERE id=?", (p["id"],))
                    conn.commit()
                    late += 1
                    continue
                # Independent referee on WINS only (LED/SAME_DAY — the claims we publish):
                # free Wikipedia pageviews, fail-open, never changes the verdict.
                _corr = None
                if lead["verdict"] in ("LED", "SAME_DAY"):
                    _corr = _referee_corroborate(_q, p["detection_date"], lead["breakout_date"])
                rec_id = hashlib.md5(f"{p['topic_key']}-{p['detection_date']}".encode()).hexdigest()[:16]
                _upsert_ledger(conn, rec_id, p, lead["breakout_date"], breakout.get("multiple"),
                               lead["lead_time_days"], lead["verdict"], "sweep",
                               sweep_query=_q, query_ambiguous=_amb, referee_corroborated=_corr)
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
        # unlike topic_maturity which is sparse): use SUSTAINED PRESENCE — the count of DISTINCT
        # DAYS the topic was scored. Present across many days = an ESTABLISHED, sustained trend
        # Google Trends already knows (can only resolve LAGGED); few days = still EMERGING/early.
        # Frequency-independent, uses the real scored_at column. Used where topic_maturity is blank.
        vs_days = {}
        try:
            tks = list({r.get("topic_key") for r in rows if r.get("topic_key")})
            if tks:
                ph = ",".join((["%s"] if db_compat.USE_PG else ["?"]) * len(tks))
                vq = ("SELECT topic_key, COUNT(DISTINCT substr(scored_at,1,10)) AS d "
                      f"FROM velocity_scores WHERE topic_key IN ({ph}) GROUP BY topic_key")
                for _v in conn.execute(vq, tuple(tks)).fetchall():
                    _vd = dict(_v); vs_days[_vd.get("topic_key")] = int(_vd.get("d") or 0)
        except Exception:
            vs_days = {}
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

    # ── PRE-BROKEN segmentation (report-time only; no stored row changes) ────────────
    # A LAGGED row whose Google breakout happened more than LEDGER_PRE_BROKEN_DAYS
    # BEFORE our first sighting was never a race we were in: the topic entered the
    # system already post-breakout (ledger cold-start / late discovery — e.g. the
    # 2026-06-13 bulk-enrollment rows lagging May breakouts). Those measure coverage
    # latency. A NEAR-MISS lag (within the grace window) is a race we ran and lost.
    # NOTHING leaves the honest denominator — both cohorts stay counted; this only
    # names them so the blended rate can be read correctly.
    _pre_grace = int(os.getenv("LEDGER_PRE_BROKEN_DAYS", "7"))
    def _lag_days(r):
        ld = r.get("lead_time_days")
        if ld is not None:
            return ld  # negative = breakout preceded detection
        try:
            return (_parse(r["breakout_date"]) - _parse(r["detection_date"])).days
        except Exception:
            return None
    lag_pre = [r for r in lag if (_lag_days(r) is not None and _lag_days(r) < -_pre_grace)]
    lag_near = [r for r in lag if r not in lag_pre]
    # Hit rate over races actually RUN (pre-broken rows excluded from THIS view only).
    _race_denom = len(led) + len(same) + len(lag_near) + len(fp)
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
    _EST_MIN_DAYS = int(os.getenv("LEDGER_ESTABLISHED_MIN_DAYS", "14"))
    def _cohort(tk):
        c = mat.get(tk, "")
        if c in _EMERGING:
            return "emerging"
        if c in _ESTABLISHED:
            return "established"
        # Fallback: sustained presence across many distinct days → established (Trends knows it).
        d = vs_days.get(tk)
        if d is not None:
            return "established" if d >= _EST_MIN_DAYS else "emerging"
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
        # Pre-broken split of LAGGED (see comment above) — transparency fields; the
        # blended honest rate below still counts EVERYTHING.
        "misses_lagged_near": len(lag_near),
        "misses_pre_broken": len(lag_pre),
        "pre_broken_grace_days": _pre_grace,
        # Match-validity segmentation of the WINS (metadata recorded at sweep time;
        # older rows resolved before 2026-07-07 have NULLs = 'unchecked'):
        "led_referee_corroborated": sum(1 for r in led if r.get("referee_corroborated") == 1),
        "led_referee_uncorroborated": sum(1 for r in led if r.get("referee_corroborated") == 0),
        "led_referee_unchecked": sum(1 for r in led if r.get("referee_corroborated") is None),
        "led_ambiguous_query": sum(1 for r in led if r.get("query_ambiguous") == 1),
        "tracked_race_hit_rate_pct": (round(len(led) / _race_denom * 100, 1)
                                      if _race_denom else None),
        "tracked_race_sample": _race_denom,
        "honest_hit_rate_pct": round(len(led) / resolved * 100, 1),
        "naive_hit_rate_pct": round(len(led) / naive_denom * 100, 1) if naive_denom else 0.0,
        "median_lead_days": round(statistics.median(lead_times), 1) if lead_times else 0,
        "mean_lead_days": round(statistics.mean(lead_times), 1) if lead_times else 0,
        "max_lead_days": max(lead_times) if lead_times else 0,
        "small_sample_warning": resolved < 20,
        # Maturity-segmented — headline going forward = the EMERGING cohort (the product's claim).
        "by_maturity": by_mat,
        "maturity_source": ("topic_maturity.maturity_class, else velocity_scores sustained-days "
                            "(>=%dd distinct = established)" % _EST_MIN_DAYS),
        "maturity_coverage": {"by_topic_maturity": sum(1 for r in rows if mat.get(r.get("topic_key"))),
                              "by_sustained_days_fallback": sum(1 for r in rows if r.get("topic_key") in vs_days),
                              "total_resolved_rows": len(rows)},
        "early_detection_hit_rate_pct": by_mat["emerging"]["hit_rate_pct"],
        "early_detection_sample": by_mat["emerging"]["resolved"],
        "best": sorted([{"topic": r["topic_display"], "lead_days": r["lead_time_days"],
                         "referee_corroborated": r.get("referee_corroborated"),
                         "query_ambiguous": r.get("query_ambiguous")}
                        for r in led], key=lambda x: x["lead_days"] or 0, reverse=True)[:5],
    }
