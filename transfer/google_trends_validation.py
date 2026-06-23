"""
================================================================
NOW TRENDIN — GOOGLE TRENDS VALIDATION MODULE
The Accuracy Ledger
================================================================

PURPOSE:
  Google Trends is a STAGE 3 (Consumer) signal. It lags Now TrendIn's
  Stage 2 (Expert) detection by design. This module does NOT use
  Google Trends for detection — it uses it for VALIDATION:

    "We detected topic X on day 1. Google Trends didn't spike until
     day 9. That is an 8-day documented lead time."

  This is the single most valuable proof asset for institutional
  clients. It converts the Gradient Score from a claim into a
  measured, auditable track record.

WHAT IT PRODUCES:
  The Accuracy Ledger — a permanent record of every detection,
  its eventual Google Trends breakout date, and the lead time
  between them. This is what you show Coatue.

PROVIDER-AGNOSTIC DESIGN:
  pytrends is archived (April 2025) and unreliable for production.
  This module defines a clean provider interface so you can plug in:
    - Google's official Trends API (alpha — preferred when available)
    - SerpApi, Apify, or ScrapingBee (managed, low-volume validation)
  The valuable logic — breakout detection and lead-time computation —
  is provider-independent and lives here.

USAGE PATTERN (low volume — validation only):
  You do NOT crawl Google Trends continuously. You look up a topic
  ONLY after Now TrendIn has already detected it, then periodically
  re-check until it breaks out. This keeps volume minimal and stays
  well within reasonable-use limits.

================================================================
"""

import os
import json
import uuid
import sqlite3
import hashlib
import statistics
from datetime import datetime, timezone, timedelta
from typing import Optional, Callable

import db_compat
from date_utils import to_iso_date

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")


def _iso_curve_date(s: str) -> str:
    """Normalize a provider curve-point date to the canonical primary ISO
    'YYYY-MM-DD'. Keeps the raw string ONLY if unparseable (e.g. a rare SerpApi
    week range), never the corrupt slice the old `[:10]` path produced from
    'May 22, 2026'. This is the fetch-time chokepoint that guarantees every
    breakout_date written to accuracy_ledger is canonical ISO."""
    return to_iso_date(s) or (s or "")

# Provider selection: "official" | "serpapi" | "apify" | "manual"
SERPAPI_KEY     = os.getenv("SERPAPI_KEY", "")
APIFY_TOKEN     = os.getenv("APIFY_TOKEN", "")
GOOGLE_TRENDS_API_KEY = os.getenv("GOOGLE_TRENDS_API_KEY", "")
# Default to Apify when a token is present (the chosen low-volume validation path).
TRENDS_PROVIDER = os.getenv("TRENDS_PROVIDER") or (
    "apify" if APIFY_TOKEN else "official" if GOOGLE_TRENDS_API_KEY else "serpapi" if SERPAPI_KEY else "manual"
)

# C2: Frozen breakout parameters — version-stamped so any threshold change
# creates a new epoch and can't silently alter historical comparisons.
BREAKOUT_THRESHOLD_MULT = float(os.getenv("LEDGER_BREAKOUT_MULT", "2.5"))
BREAKOUT_SUSTAIN_DAYS   = int(os.getenv("LEDGER_SUSTAIN_DAYS", "2"))
# Same-surge window: a breakout must fall within ±this of the detection to be a
# valid match; beyond it the breakout belongs to a different surge (frozen, mirrors
# accuracy_ledger_enhanced.MATCH_WINDOW_DAYS).
MATCH_WINDOW_DAYS       = int(os.getenv("LEDGER_MATCH_WINDOW_DAYS", "30"))
LEDGER_PARAM_VERSION    = "calib-params-v1"


# ════════════════════════════════════════════════════════════════
# SECTION 1: PROVIDER INTERFACE
# A clean abstraction so the provider can be swapped without
# touching the valuable lead-time logic.
# ════════════════════════════════════════════════════════════════

def fetch_trends_curve(topic: str, days: int = 90) -> Optional[list[dict]]:
    """
    Fetch the Google Trends interest-over-time curve for a topic.

    Returns a list of {date, value} where value is 0-100 relative interest,
    or None if unavailable.

    Routes to the configured provider. The data SHAPE is identical
    regardless of provider, so downstream logic never changes.
    """
    provider = TRENDS_PROVIDER

    if provider == "serpapi" and SERPAPI_KEY:
        return _fetch_serpapi(topic, days)
    elif provider == "apify" and APIFY_TOKEN:
        return _fetch_apify(topic, days)
    elif provider == "official" and GOOGLE_TRENDS_API_KEY:
        return _fetch_official(topic, days)
    else:
        # Manual mode — data supplied externally (CSV import, etc.)
        return None


def _fetch_serpapi(topic: str, days: int) -> Optional[list[dict]]:
    """Fetch via SerpApi Google Trends endpoint."""
    try:
        from urllib.request import urlopen
        from urllib.parse import urlencode
        params = urlencode({
            "engine":   "google_trends",
            "q":        topic,
            "data_type":"TIMESERIES",
            "date":     f"today {max(1, days//30)}-m",
            "api_key":  SERPAPI_KEY,
        })
        url = f"https://serpapi.com/search.json?{params}"
        with urlopen(url, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        timeline = data.get("interest_over_time", {}).get("timeline_data", [])
        return [{
            "date":  _iso_curve_date(point.get("date", "")),
            "value": point.get("values", [{}])[0].get("extracted_value", 0),
        } for point in timeline]
    except Exception as e:
        print(f"SerpApi fetch error for '{topic}': {e}")
        return None


def _clean_time_str(s: str) -> str:
    """Repair mojibake in Apify's formattedTime strings.

    Google emits a U+202F narrow no-break space before AM/PM; Apify returns it
    UTF-8-encoded but mis-decoded, so it arrives as 'â€¯' (and similar). Normalise
    all no-break / narrow spaces (and that mojibake sequence) to a plain space.
    """
    if not s:
        return ""
    # Repair the UTF-8-as-cp1252 mojibake of U+202F / U+00A0 / U+2026, then let
    # str.split() collapse every real unicode whitespace (nbsp, narrow nbsp,
    # thin space) down to single plain spaces.
    s = (s.replace("â€¯", " ")   # mojibake U+202F (narrow nbsp)
           .replace("Â ", " ")          # mojibake U+00A0 (nbsp)
           .replace("â€¦", "..."))# mojibake U+2026 (ellipsis)
    return " ".join(s.split())


def _point_value(v):
    """The actor returns value as a list like [88]; some shapes use a scalar."""
    if isinstance(v, (list, tuple)):
        return v[0] if v else 0
    return v if v is not None else 0


def _fetch_apify(topic: str, days: int) -> Optional[list[dict]]:
    """Fetch interest-over-time via the Apify Google Trends Scraper actor.

    Uses the ASYNC run-and-poll pattern (start run → poll status → read dataset)
    instead of the blocking run-sync endpoint. run-sync holds one HTTP connection
    open for the entire actor run and routinely exceeds the read timeout on slow
    runs, which silently starved the accuracy ledger. Polling keeps each call
    short and reliable."""
    try:
        import time as _t
        from urllib.request import Request, urlopen
        actor = os.getenv("APIFY_TRENDS_ACTOR", "apify~google-trends-scraper")
        max_wait = int(os.getenv("APIFY_RUN_TIMEOUT", "300"))   # total budget (s)
        poll_every = int(os.getenv("APIFY_POLL_SEC", "8"))

        try:
            from collector_health import log_api_call as _api
            _api("apify_trends")
        except Exception:
            pass
        # 1) Start the run (returns immediately with id + defaultDatasetId).
        start_url = f"https://api.apify.com/v2/acts/{actor}/runs?token={APIFY_TOKEN}"
        payload = json.dumps({
            "searchTerms":  [topic],
            "timeRange":    f"today {max(1, days//30)}-m",
            "isPublic":     False,
        }).encode("utf-8")
        req = Request(start_url, data=payload, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=30) as resp:
            run = json.loads(resp.read().decode("utf-8")).get("data", {})
        run_id = run.get("id")
        dataset_id = run.get("defaultDatasetId")
        if not run_id or not dataset_id:
            print(f"Apify start failed for '{topic}'")
            return None

        # 2) Poll the run status until it finishes (or the budget runs out).
        status, waited = run.get("status", "READY"), 0
        while status in ("READY", "RUNNING") and waited < max_wait:
            _t.sleep(poll_every)
            waited += poll_every
            try:
                with urlopen(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}",
                             timeout=20) as r:
                    status = json.loads(r.read().decode("utf-8")).get("data", {}).get("status", status)
            except Exception:
                continue
        if status != "SUCCEEDED":
            print(f"Apify run for '{topic}' ended status={status} after {waited}s")
            return None

        # 3) Read the dataset items.
        with urlopen(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&clean=true",
                     timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))

        # Apify returns interest-over-time points. The actor's field name is
        # 'interestOverTime_timelineData'; fall back to the older 'interestOverTime'.
        curve = []
        for item in data:
            points = (item.get("interestOverTime_timelineData")
                      or item.get("interestOverTime")
                      or [])
            for point in points:
                if point.get("hasData") in (False, [False]):
                    continue
                curve.append({
                    "date":  _iso_curve_date(_clean_time_str(point.get("formattedTime") or point.get("date") or "")),
                    "time":  point.get("time", ""),  # epoch seconds (string) — secondary
                    "value": _point_value(point.get("value")),
                })
        return curve or None
    except Exception as e:
        print(f"Apify fetch error for '{topic}': {e}")
        return None


def _fetch_official(topic: str, days: int) -> Optional[list[dict]]:
    """Fetch via Google's official Trends API (alpha). Endpoint shape may change."""
    try:
        from urllib.request import Request, urlopen
        from urllib.parse import urlencode
        params = urlencode({"term": topic, "timeRange": f"{days}d"})
        url = f"https://trends.googleapis.com/v1beta/timeseries?{params}"
        req = Request(url, headers={"X-Goog-Api-Key": GOOGLE_TRENDS_API_KEY})
        with urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [{
            "date":  _iso_curve_date(p.get("date", "")),
            "value": p.get("value", 0),
        } for p in data.get("timeline", [])]
    except Exception as e:
        print(f"Official API fetch error for '{topic}': {e}")
        return None


def import_manual_curve(topic: str, csv_path: str) -> list[dict]:
    """
    Import a Google Trends curve from a manually-exported CSV.
    Google Trends lets you export any chart as CSV — this is the
    zero-cost, zero-ToS-friction validation path for low volume.
    """
    curve = []
    try:
        with open(csv_path, "r") as f:
            lines = f.readlines()
        # Google Trends CSV: skip header rows, parse date,value
        for line in lines:
            parts = line.strip().split(",")
            if len(parts) >= 2:
                date_str, val_str = parts[0], parts[1]
                try:
                    val = int(val_str)
                    curve.append({"date": _iso_curve_date(date_str), "value": val})
                except ValueError:
                    continue  # skip header/non-numeric rows
    except Exception as e:
        print(f"CSV import error: {e}")
    return curve


# ════════════════════════════════════════════════════════════════
# SECTION 2: BREAKOUT DETECTION
# Finds the point where a topic "broke out" on Google Trends —
# i.e. crossed from background noise into mainstream consumer search.
# This is the moment we measure lead time against.
# ════════════════════════════════════════════════════════════════

def detect_breakout_date(curve: list[dict],
                         breakout_threshold: float = BREAKOUT_THRESHOLD_MULT,
                         since: object = None) -> Optional[dict]:
    """
    Detect the breakout point in a Google Trends curve.

    Breakout = the first sustained jump above baseline. Defined as:
      the first date where the value exceeds (baseline_mean * threshold)
      AND stays elevated for at least 2 subsequent points (sustained,
      not a one-day spike).

    SAME-SURGE MATCHING (since): a 90-day curve can contain several distinct
    surges. When validating a detection, pass `since` = (detection_date −
    MATCH_WINDOW) so ONLY breaches on/after that floor are considered — a June
    detection then matches the June surge, never an earlier Spring spike in the
    same window (the −92d "stale match" artifact). The baseline is still computed
    over the WHOLE curve (the quiet period is the right reference); only the SEARCH
    for the breach is floored. Without `since`, behaviour is unchanged (first breach).

    Returns {breakout_date, breakout_value, baseline_mean, multiple}
    or None if no qualifying breakout (topic still pre-breakout for this surge).
    """
    if not curve or len(curve) < 5:
        return None

    values = [p["value"] for p in curve]

    # Baseline = mean of the lowest 40% of values (the "quiet" period) — whole curve
    sorted_vals = sorted(values)
    baseline_pool = sorted_vals[:max(2, int(len(sorted_vals) * 0.4))]
    baseline_mean = statistics.mean(baseline_pool) if baseline_pool else 1
    baseline_mean = max(1.0, baseline_mean)  # avoid divide-by-zero

    threshold_value = baseline_mean * breakout_threshold

    # same-surge floor: ignore breaches before `since` (ISO 'YYYY-MM-DD')
    since_iso = to_iso_date(since) if since is not None else None

    # Walk forward looking for the first sustained breach (on/after `since`)
    for i in range(len(curve) - 2):
        if since_iso is not None:
            d_iso = _iso_curve_date(curve[i].get("date", ""))
            if d_iso and d_iso < since_iso:
                continue   # earlier surge — not the one this detection is about
        if values[i] >= threshold_value:
            # Confirm sustained: next 2 points also elevated
            if values[i+1] >= threshold_value * 0.8 and \
               values[i+2] >= threshold_value * 0.7:
                return {
                    "breakout_date":  _iso_curve_date(curve[i]["date"]),
                    "breakout_value": values[i],
                    "baseline_mean":  round(baseline_mean, 1),
                    "multiple":       round(values[i] / baseline_mean, 1),
                    "breakout_index": i,
                    "param_version":  LEDGER_PARAM_VERSION,
                }

    return None  # No breakout yet — topic still pre-mainstream for this surge


# ════════════════════════════════════════════════════════════════
# SECTION 3: LEAD TIME COMPUTATION
# The core proprietary value: how many days did Now TrendIn lead?
# ════════════════════════════════════════════════════════════════

def compute_lead_time(detection_date: str,
                     breakout: dict) -> Optional[dict]:
    """
    Compute the lead time between Now TrendIn detection and
    Google Trends breakout.

    detection_date: ISO date when Now TrendIn first scored this topic high
    breakout:       output of detect_breakout_date()

    Returns {lead_time_days, detection_date, breakout_date, verdict}
    """
    if not breakout:
        return None

    try:
        det_dt = _parse_date(detection_date)
        brk_dt = _parse_date(breakout["breakout_date"])
    except Exception:
        return None

    lead_days = (brk_dt - det_dt).days

    if lead_days > 0:
        verdict = "LED"      # Now TrendIn detected before Google Trends
    elif lead_days == 0:
        verdict = "SAME_DAY"
    else:
        verdict = "LAGGED"   # Google Trends moved first — a miss

    return {
        "lead_time_days":  lead_days,
        "detection_date":  detection_date,
        "breakout_date":   breakout["breakout_date"],
        "breakout_multiple": breakout["multiple"],
        "verdict":         verdict,
    }


def _parse_date(date_str: str) -> datetime:
    """Parse various date formats from trends providers."""
    date_str = date_str.strip()
    # Try common formats
    for fmt in ("%Y-%m-%d", "%b %d, %Y", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.split("T")[0] if "T" in date_str else date_str, fmt)
        except ValueError:
            continue
    # Try ISO
    return datetime.fromisoformat(date_str.replace("Z", ""))


# ════════════════════════════════════════════════════════════════
# SECTION 4: THE ACCURACY LEDGER
# Permanent record of every validated prediction
# ════════════════════════════════════════════════════════════════

def init_ledger_db(db_path: str = DB_PATH):
    """Create the accuracy ledger table."""
    conn = db_compat.connect(db_path)
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ledger_verdict ON accuracy_ledger(verdict)")
    conn.commit()
    conn.close()


def record_validation(topic_key: str, topic_display: str,
                     detection_date: str, detection_score: float,
                     lead_result: dict, breakout: dict,
                     db_path: str = DB_PATH):
    """Write a validated prediction to the permanent ledger (upsert by id)."""
    conn = db_compat.connect(db_path)
    now = datetime.now(timezone.utc).isoformat()
    rec_id = hashlib.md5(f"{topic_key}-{detection_date}".encode()).hexdigest()[:16]

    conn.execute("""
        INSERT INTO accuracy_ledger
            (id, topic_key, topic_display, detection_date, detection_score,
             breakout_date, breakout_multiple, lead_time_days, verdict,
             validated_at, provider)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
            breakout_date     = EXCLUDED.breakout_date,
            breakout_multiple = EXCLUDED.breakout_multiple,
            lead_time_days    = EXCLUDED.lead_time_days,
            verdict           = EXCLUDED.verdict,
            validated_at      = EXCLUDED.validated_at,
            provider          = EXCLUDED.provider
    """, (
        rec_id, topic_key, topic_display, detection_date, detection_score,
        lead_result["breakout_date"], breakout["multiple"],
        lead_result["lead_time_days"], lead_result["verdict"],
        now, TRENDS_PROVIDER,
    ))
    conn.commit()
    conn.close()


def validate_topic(topic_key: str, topic_display: str,
                  detection_date: str, detection_score: float,
                  db_path: str = DB_PATH) -> dict:
    """
    Full validation pipeline for one topic:
      1. Fetch its Google Trends curve
      2. Detect the breakout point
      3. Compute lead time vs Now TrendIn detection
      4. Record in the accuracy ledger

    Returns the validation result.
    """
    curve = fetch_trends_curve(topic_display)
    if not curve:
        return {"status": "no_data",
                "message": f"No Trends data available for '{topic_display}' "
                           f"(provider: {TRENDS_PROVIDER})"}

    # SAME-SURGE FLOOR: only match a breakout on/after (detection − MATCH_WINDOW),
    # so this detection is paired with its own surge, not an earlier Spring spike.
    try:
        since = (_parse_date(detection_date) - timedelta(days=MATCH_WINDOW_DAYS)).date().isoformat()
    except Exception:
        since = None
    breakout = detect_breakout_date(curve, since=since)
    if not breakout:
        return {"status": "pre_breakout",
                "message": f"'{topic_display}' has not yet broken out on Google "
                           f"Trends — Now TrendIn is still ahead. Re-check later."}

    lead = compute_lead_time(detection_date, breakout)
    if not lead:
        return {"status": "error", "message": "Could not compute lead time"}

    # C1 gate: a breakout still outside ±MATCH_WINDOW (e.g. a far-forward re-surge)
    # is a cross-surge match — record as LATE_REDETECTION so it is excluded from the
    # honest denominator rather than mislabelled LED/LAGGED.
    if abs(lead["lead_time_days"]) > MATCH_WINDOW_DAYS:
        lead = {**lead, "verdict": "LATE_REDETECTION"}

    record_validation(topic_key, topic_display, detection_date,
                      detection_score, lead, breakout, db_path)

    return {"status": "validated", **lead}


# ════════════════════════════════════════════════════════════════
# SECTION 5: LEDGER REPORTING — THE PROOF ASSET
# ════════════════════════════════════════════════════════════════

def generate_accuracy_report(db_path: str = DB_PATH) -> dict:
    """
    Generate the accuracy summary — the headline metrics you put
    in front of Coatue and every institutional client.
    """
    init_ledger_db(db_path)
    conn = db_compat.connect(db_path)
    try:
        rows = conn.execute("SELECT * FROM accuracy_ledger").fetchall()
    except Exception:
        conn.close()
        return {"status": "no_ledger"}
    conn.close()

    if not rows:
        return {"status": "empty", "message": "No validations recorded yet."}

    led      = [r for r in rows if r["verdict"] == "LED"]
    lagged   = [r for r in rows if r["verdict"] == "LAGGED"]
    lead_times = [r["lead_time_days"] for r in led]

    return {
        "status":              "ok",
        "total_predictions":   len(rows),
        "led_count":           len(led),
        "lagged_count":        len(lagged),
        "hit_rate_pct":        round(len(led) / len(rows) * 100, 1),
        "avg_lead_time_days":  round(statistics.mean(lead_times), 1) if lead_times else 0,
        "median_lead_time_days": round(statistics.median(lead_times), 1) if lead_times else 0,
        "max_lead_time_days":  max(lead_times) if lead_times else 0,
        "best_predictions":    sorted(
            [{"topic": r["topic_display"], "lead_days": r["lead_time_days"],
              "multiple": r["breakout_multiple"]} for r in led],
            key=lambda x: x["lead_days"], reverse=True
        )[:10],
    }


def validate_recent_detections(db_path: str = DB_PATH,
                               limit: int = int(os.getenv("ACCURACY_BATCH", "8"))) -> dict:
    """
    Validation pass: take our highest detections, use their first-scored date
    as the detection date, and check Google Trends for a breakout → record
    lead time in the ledger. Runs on the scheduler (daily). No-op gracefully
    when no Trends provider/token is configured.
    """
    init_ledger_db(db_path)
    conn = db_compat.connect(db_path)
    try:
        # Mirror the /scores query shape (proven to work on Postgres): pull the
        # latest row per topic + first-seen date, then filter/sort in Python.
        raw = conn.execute("""
            SELECT v.topic_key, v.topic_display, v.detection_score,
                   fs.first_at AS first_at
            FROM velocity_scores v
            INNER JOIN (
                SELECT topic_key, MAX(scored_at) AS max_at
                FROM velocity_scores GROUP BY topic_key
            ) latest ON v.topic_key = latest.topic_key
                AND v.scored_at = latest.max_at
            INNER JOIN (
                SELECT topic_key, MIN(scored_at) AS first_at
                FROM velocity_scores GROUP BY topic_key
            ) fs ON v.topic_key = fs.topic_key
        """).fetchall()
    except Exception as e:
        conn.close()
        return {"status": "error", "detail": str(e)}
    conn.close()

    # The stored detection_score column is the *raw* pre-calibration score
    # (serve-time calibration in /scores rescales it upward, but that scaling
    # is not persisted). So rank by the raw column and validate the strongest
    # N detections above a modest floor, rather than an absolute threshold.
    DETECTION_FLOOR = float(os.getenv("ACCURACY_MIN_DETECTION", "10"))
    rows = [r for r in raw if (r["detection_score"] or 0) >= DETECTION_FLOOR]
    rows.sort(key=lambda r: r["detection_score"] or 0, reverse=True)
    rows = rows[:limit]

    out = {"validated": 0, "pre_breakout": 0, "no_data": 0, "errors": 0,
           "candidates": len(rows),
           "sample": [r["topic_display"] for r in rows[:5]]}
    for r in rows:
        # Canonical PRIMARY date (§14): never raw [:10] — to_iso_date tries whole-
        # string formats and returns None (skip) on an unparseable value rather than
        # a corrupt date, so accuracy_ledger.detection_date stays a clean YYYY-MM-DD.
        det_date = to_iso_date(r["first_at"])
        if not det_date:
            out["errors"] += 1
            continue
        try:
            res = validate_topic(r["topic_key"], r["topic_display"], det_date,
                                  r["detection_score"] or 0, db_path)
            st = res.get("status")
            out[st if st in out else "errors"] += 1
        except Exception:
            out["errors"] += 1
    print(f"[accuracy] validation pass ({TRENDS_PROVIDER}): {out}")
    return {"status": "ok", "provider": TRENDS_PROVIDER, **out}


# ════════════════════════════════════════════════════════════════
# SECTION 6: DEMO
# ════════════════════════════════════════════════════════════════

def run_demo():
    print("\n" + "="*64)
    print("NOW TRENDIN — GOOGLE TRENDS VALIDATION — DEMO")
    print("="*64)

    # Synthetic curve: a topic that was flat then broke out
    synthetic_curve = []
    base = datetime(2026, 3, 1)
    # 30 days of low baseline, then breakout
    pattern = [3,4,2,3,5,4,3,4,2,3,4,3,5,4,3,  # quiet baseline
               8,18,35,55,72,85,90,88,92,95,    # breakout
               80,78,82,79,81]
    for i, v in enumerate(pattern):
        synthetic_curve.append({
            "date":  (base + timedelta(days=i)).strftime("%Y-%m-%d"),
            "value": v,
        })

    print("\nScenario: Now TrendIn detected 'agentic coding' on 2026-03-08")
    print("Google Trends curve fetched (90-day window)...")

    breakout = detect_breakout_date(synthetic_curve)
    print(f"\nBreakout detected:")
    print(f"  Date:     {breakout['breakout_date']}")
    print(f"  Baseline: {breakout['baseline_mean']}")
    print(f"  Multiple: {breakout['multiple']}x above baseline")

    lead = compute_lead_time("2026-03-08", breakout)
    print(f"\nLead time computation:")
    print(f"  Now TrendIn detected:    2026-03-08")
    print(f"  Google Trends broke out: {lead['breakout_date']}")
    print(f"  LEAD TIME:               {lead['lead_time_days']} days")
    print(f"  Verdict:                 {lead['verdict']}")

    print("\n" + "="*64)
    print("This is the proof asset: a documented, measurable lead time")
    print("between Now TrendIn detection and mainstream Google Trends breakout.")
    print("="*64)


if __name__ == "__main__":
    run_demo()
