"""
referee_wikipedia.py — Wikipedia Pageviews referee (Phase 2, the INDEPENDENT referee).

PURPOSE (the moat's external check):
  The Accuracy Ledger validates our detections against GOOGLE TRENDS today. But a
  leading *search* trend is not independent truth — it is another attention proxy that
  can move WITH us. Phase 2 stands up an outside source of truth that shares NO inputs
  with the Gradient Score: Wikipedia daily pageviews. The question it answers is narrow
  and falsifiable: "On the day WE detected a topic, had public attention (Wikipedia
  pageviews) ALREADY surged?" If yes, we were late, not early — a FALSE-EARLY. The rate
  of that across matured detections turns the Greenspan / already-arrived failures into a
  NUMBER instead of a hunch.

INTEGRITY (hard rules — do not violate):
  • READ-ONLY TO THE SCORE, FOREVER. Nothing in this module is imported by the scoring
    path (gravitational_anomaly_detector / dual_pathway / signal_calibration_integration).
    The referee observations live in a HELD-OUT table the score never reads. Folding the
    referee into a weight would destroy its purpose (it must remain falsifiable).
  • NEVER GUESS. A topic we cannot confidently resolve to a Wikipedia article is
    QUARANTINED (status='unresolved'), never matched to a wrong article. A wrong arrival
    date would corrupt the false-early rate — the one number this exists to defend.
  • CANONICAL DATES. Every date returned is ISO YYYY-MM-DD via date_utils (CLAUDE.md §14).

SOURCES (free, no key, public):
  • Resolve  : MediaWiki opensearch  (en.wikipedia.org/w/api.php?action=opensearch)
  • Pageviews: Wikimedia REST metrics/pageviews/per-article/en.wikipedia/all-access/...

Wikimedia requires a descriptive User-Agent; we send a contact UA.
"""
from __future__ import annotations

import json
import statistics
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Optional

try:
    from date_utils import to_iso_date
except Exception:                       # defensive: referee must not crash the process
    def to_iso_date(s):
        return (str(s)[:10] if s else None)

_UA = "NowTrendIn-Referee/1.0 (https://abelcesq.github.io/nowtrendin-v2.0/; abelc.esq@gmail.com)"
_OPENSEARCH = "https://en.wikipedia.org/w/api.php"
_PAGEVIEWS = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
              "en.wikipedia/all-access/all-agents/{article}/daily/{start}/{end}")

# Frozen surge parameters — VERSION-STAMPED. A topic's Wikipedia "arrival" is the first
# day its pageviews exceed a CLEAN pre-anchor baseline * SURGE_MULT, with a minimum
# absolute floor so a tiny-traffic article's noise can't read as a surge. The baseline is
# the MEDIAN of a fixed early ("quiet") window — median, not mean, so a fast ramp at the
# window edge does not contaminate it (the bug a trailing-mean baseline had). DO NOT tune
# without re-freezing + a documented rationale (these are the referee's frozen params).
REFEREE_PARAM_VERSION = "wiki-v2-2026-06-23"
SURGE_MULT = 3.0                 # surge = 3x the clean baseline median
SURGE_MIN_ABS = 200              # ...and at least 200 views/day (kills micro-article noise)
PRE_DAYS = 75                    # fetch this many days BEFORE the anchor (detection) date —
                                 # wide enough that the lowest-40% baseline captures a genuine
                                 # quiet floor even when detection lands somewhat after arrival
POST_DAYS = 30                   # ...and this many AFTER (to catch arrival shortly after)
MATCH_WINDOW = 30                # same-surge floor: the arrival counted against a detection
                                 # must be the surge within ±this of the detection — not an
                                 # unrelated earlier surge in the wide baseline window (mirrors
                                 # the ledger's same-surge guard; baseline still uses the whole
                                 # window, only the breach SEARCH is floored to anchor-MATCH_WINDOW)


def _get(url: str, timeout: int = 20) -> Optional[bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception:
        return None


def resolve_article(topic_display: str) -> Optional[str]:
    """Resolve a topic to its canonical Wikipedia article title via opensearch.
    Returns the exact article title (URL-ready) or None if no confident match —
    None means QUARANTINE, never a guess. Only accepts a first hit whose title is a
    reasonable lexical match to the query (guards against opensearch returning a loosely
    related article for an ambiguous fragment)."""
    q = (topic_display or "").strip()
    if len(q) < 2:
        return None
    params = urllib.parse.urlencode({
        "action": "opensearch", "search": q, "limit": 3,
        "namespace": 0, "format": "json", "redirects": "resolve",
    })
    raw = _get(f"{_OPENSEARCH}?{params}")
    if not raw:
        return None
    try:
        data = json.loads(raw.decode("utf-8"))
        titles = data[1] if len(data) > 1 else []
    except Exception:
        return None
    if not titles:
        return None
    # Confidence gate: accept the top hit only if it shares a meaningful token with the
    # query (defeats opensearch's habit of returning a tangential article for junk).
    ql = q.lower()
    q_tokens = {t for t in ql.replace("-", " ").split() if len(t) > 2}
    for title in titles:
        tl = title.lower()
        if tl == ql:
            return title                         # exact match — best
        t_tokens = {t for t in tl.replace("-", " ").split() if len(t) > 2}
        if q_tokens and (q_tokens & t_tokens):
            return title                         # shares a content token — accept
    return None                                  # no confident match → quarantine


def _parse_iso(d: str):
    return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()


def fetch_pageviews(article: str, start_date, end_date) -> Optional[list[dict]]:
    """Daily pageviews for an article over an EXPLICIT [start_date, end_date] range
    (date objects or ISO strings). Returns [{date: YYYY-MM-DD, views: int}] ascending,
    or None on failure/empty. Anchoring the window on a caller-supplied range (rather than
    'last N days') is what gives a CLEAN pre-detection baseline — the referee observes the
    period AROUND our detection, not a generic recent window."""
    if isinstance(start_date, str):
        start_date = _parse_iso(start_date)
    if isinstance(end_date, str):
        end_date = _parse_iso(end_date)
    art = urllib.parse.quote(article.replace(" ", "_"), safe="")
    url = _PAGEVIEWS.format(article=art,
                            start=start_date.strftime("%Y%m%d"), end=end_date.strftime("%Y%m%d"))
    raw = _get(url)
    if not raw:
        return None
    try:
        items = json.loads(raw.decode("utf-8")).get("items", [])
    except Exception:
        return None
    curve = []
    for it in items:
        ts = it.get("timestamp", "")           # 'YYYYMMDD00'
        if len(ts) >= 8:
            iso = f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}"
            curve.append({"date": iso, "views": int(it.get("views", 0) or 0)})
    return curve or None


def detect_arrival_date(curve: list[dict], since: object = None) -> Optional[dict]:
    """The Wikipedia 'arrival' date = first SUSTAINED jump in daily pageviews above a quiet
    baseline. Mirrors the ledger's frozen google_trends_validation.detect_breakout_date so
    the two providers define 'arrival' IDENTICALLY (the punch-list requirement):
      • baseline = MEAN of the lowest 40% of in-window days (the quiet period, robust to
        where the anchor falls — a ramp can't inflate it);
      • breach   = first day >= baseline * SURGE_MULT (and the absolute floor);
      • SUSTAINED = the next 2 days stay >= 80% / 70% of threshold (kills one-day spikes);
      • `since`   = same-surge floor: ignore breaches before this ISO date so a long window's
        earlier surge doesn't match a later detection (the −92d 'stale match' guard).
    Returns {arrival_date, surge_views, baseline_mean, multiple} or None (no qualifying
    surge — still pre-arrival, or steady-state traffic that never tripled)."""
    if not curve or len(curve) < 5:
        return None
    curve = sorted(curve, key=lambda p: p["date"])
    views = [p["views"] for p in curve]
    quiet_pool = sorted(views)[:max(2, int(len(views) * 0.4))]
    base_mean = max(1.0, statistics.mean(quiet_pool) if quiet_pool else 1.0)
    threshold = max(base_mean * SURGE_MULT, SURGE_MIN_ABS)
    since_iso = to_iso_date(since) if since is not None else None
    for i in range(len(curve) - 2):
        if since_iso is not None:
            d_iso = to_iso_date(curve[i]["date"])
            if d_iso and d_iso < since_iso:
                continue
        if views[i] >= threshold and \
           views[i+1] >= threshold * 0.8 and views[i+2] >= threshold * 0.7:
            return {
                "arrival_date": to_iso_date(curve[i]["date"]),
                "surge_views": views[i],
                "baseline_mean": round(base_mean, 1),
                "multiple": round(views[i] / base_mean, 2) if base_mean else None,
                "param_version": REFEREE_PARAM_VERSION,
            }
    return None


# ── Topic-class reconciliation (the "Strait of Hormuz" research) ─────────────────
# Empirically, topics fall into THREE classes by their long-window pageview shape, and a
# single "arrival date" is only well-defined for ONE of them. Measured on the live ledger:
#   • CLEAN          — one isolated quiet→loud transition (Claude 1% elevated/2994x,
#                      FIFA 6%/25x). Arrival is precise; the referee is gold here.
#   • CHURNING       — surges REPEATEDLY, never goes quiet (Strait of Hormuz 42% of days
#                      elevated, Iran 17%, world models 54%). No single "arrival"; the
#                      same-surge floor still answers "were we late vs the surge our
#                      detection was about," but the precise lead is low-confidence.
#   • STEADY_MAIN    — permanently high, never surges (Russia/China peak/floor ~2x). It
#                      has ALREADY arrived; detecting it as "emerging" is late by definition.
# Plus the non-class outcomes UNRESOLVED / NO_DATA (Wikipedia doesn't cover the topic —
# 38% of our niche-early ledger; these are EXCLUDED from the rate, never guessed).
# Frozen class thresholds (version-stamped with the surge params):
CLS_STEADY_MAX_PEAK_FLOOR = 3.0    # peak/p10 below this = never meaningfully surges
CLS_CHURN_MIN_ELEVATED   = 0.15    # >=15% of days above 3x baseline = churning
CLS_SIGNATURE_DAYS       = 365     # long window used to read the topic's shape


def classify_topic(topic_display: str, window_days: int = CLS_SIGNATURE_DAYS,
                   _curve: Optional[list] = None, article: Optional[str] = None) -> dict:
    """Read a topic's long-window pageview SHAPE and assign its class. `_curve`/`article`
    may be passed to reuse a single fetch. Returns {topic_class, elevated_pct, peak_floor,
    article, status}. topic_class ∈ {clean, churning, steady_mainstream, unresolved, no_data}."""
    art = article or resolve_article(topic_display)
    if not art:
        return {"topic_class": "unresolved", "article": None, "status": "unresolved"}
    if _curve is None:
        end = datetime.now(timezone.utc).date()
        _curve = fetch_pageviews(art, end - timedelta(days=window_days), end)
    if not _curve or len(_curve) < 30:
        return {"topic_class": "no_data", "article": art, "status": "no_data"}
    v = sorted(p["views"] for p in _curve)
    base = max(1.0, statistics.mean(v[:max(2, int(len(v) * 0.4))]))
    p10 = v[len(v) // 10] or 1
    elevated_pct = round(100 * sum(1 for x in v if x >= base * SURGE_MULT) / len(v), 1)
    peak_floor = round(max(v) / p10, 1)
    if peak_floor < CLS_STEADY_MAX_PEAK_FLOOR:
        cls = "steady_mainstream"
    elif elevated_pct >= CLS_CHURN_MIN_ELEVATED * 100:
        cls = "churning"
    else:
        cls = "clean"
    return {"topic_class": cls, "elevated_pct": elevated_pct, "peak_floor": peak_floor,
            "article": art, "status": "ok"}


# ── Observation-window gate (the "we just started in March 2026" reconciliation) ──
# A false-early verdict is FAIR only if our engine had a real chance to detect the topic
# early — i.e. we were already TRACKING it before its independent arrival. Two artifacts
# of a young system (launched ~2026-03) otherwise masquerade as scoring failures:
#   • PRE_OBSERVATION       — the topic arrived before our data even began. We didn't exist.
#   • DISCOVERED_AFTER_ARRIVAL — we DID exist, but the topic didn't enter our CORPUS until
#                             after it surged (a DISCOVERY-LATENCY / collection-breadth gap,
#                             NOT a scoring false-early — different problem, different fix:
#                             wider/earlier feeds, not recalibration).
# Both are EXCLUDED from the false-early rate and reported separately, so the rate measures
# SCORING earliness on topics we actually watched in time — not our launch date or our feed
# coverage. OBSERVATION_START is the engine's data start (override via env when wired in).
import os as _os
OBSERVATION_START = to_iso_date(_os.getenv("REFEREE_OBSERVATION_START", "2026-03-01"))
OBSERVATION_WARMUP_DAYS = 21      # baseline the engine needs on a topic before a fair early call


def assess(topic_display: str, detection_date, our_first_seen=None) -> dict:
    """The referee's RECONCILED per-detection verdict — the function the false-early
    aggregation calls. ONE long fetch drives both the class and the anchored arrival.
    `our_first_seen` = when the TOPIC first entered our corpus (topic_lifecycle.
    first_detected_at); pass it so the observation-window gate can separate a scoring
    false-early from a discovery-latency gap. Returns referee_verdict ∈
      • FALSE_EARLY        — we were TRACKING it in time, yet an independent surge preceded
                             our detection (a genuine scoring late-call — the real signal)
      • LED                — we detected at/before the surge (the 'before it arrives' claim)
      • ALREADY_MAINSTREAM — steady-mainstream: permanently arrived → counts as NOT-early
      • NO_SURGE           — clean/churning topic, no surge near detection (inconclusive)
      • EXCLUDE            — not a fair scoring test: unresolved/no_data (coverage), OR
                             pre_observation / discovered_after_arrival (young-system artifacts)
    plus topic_class, lead_days, confidence, and the signature."""
    anchor = _parse_iso(detection_date) if isinstance(detection_date, str) else detection_date
    art = resolve_article(topic_display)
    if not art:
        return {"referee_verdict": "EXCLUDE", "reason": "unresolved",
                "topic": topic_display, "topic_class": "unresolved", "lead_days": None}
    end = datetime.now(timezone.utc).date()
    curve = fetch_pageviews(art, min(anchor - timedelta(days=CLS_SIGNATURE_DAYS), end - timedelta(days=CLS_SIGNATURE_DAYS)), end)
    cinfo = classify_topic(topic_display, _curve=curve, article=art)
    cls = cinfo["topic_class"]
    _sig = {"elevated_pct": cinfo.get("elevated_pct"), "peak_floor": cinfo.get("peak_floor")}
    if cls in ("unresolved", "no_data"):
        return {"referee_verdict": "EXCLUDE", "reason": cls, "topic": topic_display,
                "article": art, "topic_class": cls, "lead_days": None}
    if cls == "steady_mainstream":
        return {"referee_verdict": "ALREADY_MAINSTREAM", "topic": topic_display, "article": art,
                "topic_class": cls, "lead_days": None, "confidence": "high", "signature": _sig}
    # clean / churning: anchored same-surge arrival
    sub = [p for p in (curve or [])
           if anchor - timedelta(days=PRE_DAYS) <= _parse_iso(p["date"]) <= anchor + timedelta(days=POST_DAYS)]
    arrival = detect_arrival_date(sub, since=anchor - timedelta(days=MATCH_WINDOW)) if len(sub) >= 5 else None
    if not arrival:
        return {"referee_verdict": "NO_SURGE", "topic": topic_display, "article": art,
                "topic_class": cls, "lead_days": None,
                "confidence": "high" if cls == "clean" else "low", "signature": _sig}
    arr_date = arrival["arrival_date"]
    lead = (anchor - _parse_iso(arr_date)).days
    # ── Observation-window gate: is this a FAIR scoring test? ──────────────────────
    if arr_date < OBSERVATION_START:
        return {"referee_verdict": "EXCLUDE", "reason": "pre_observation",
                "topic": topic_display, "article": art, "topic_class": cls,
                "arrival_date": arr_date, "lead_days": lead, "signature": _sig}
    if our_first_seen is not None:
        fs = to_iso_date(our_first_seen)
        if fs and fs > arr_date:
            return {"referee_verdict": "EXCLUDE", "reason": "discovered_after_arrival",
                    "topic": topic_display, "article": art, "topic_class": cls,
                    "arrival_date": arr_date, "our_first_seen": fs, "lead_days": lead,
                    "discovery_lag_days": (_parse_iso(fs) - _parse_iso(arr_date)).days,
                    "signature": _sig}
    return {"referee_verdict": ("FALSE_EARLY" if lead > 0 else "LED"),
            "topic": topic_display, "article": art, "topic_class": cls,
            "arrival_date": arr_date, "lead_days": lead,
            "confidence": "high" if cls == "clean" else "low",
            "signature": {**_sig, "multiple": arrival.get("multiple")}}


def observe(topic_display: str, anchor_date=None,
            pre_days: int = PRE_DAYS, post_days: int = POST_DAYS) -> dict:
    """Full referee read for one topic, ANCHORED on our detection date:
        resolve → pageviews[anchor-pre_days, anchor+post_days] → arrival date → lead.
    `anchor_date` = OUR detection date (ISO or date); defaults to today for a smoke test.
    `lead_days` = (anchor - arrival): POSITIVE = Wikipedia arrived BEFORE we detected
    (we were LATE → a false-early candidate); NEGATIVE/zero = we detected at or before
    the public surge (the 'before it arrives' claim holds for this topic).
    status ∈ {ok, unresolved, no_data, no_surge}. Never raises."""
    if anchor_date is None:
        anchor = datetime.now(timezone.utc).date()
    else:
        anchor = _parse_iso(anchor_date) if isinstance(anchor_date, str) else anchor_date
    start = anchor - timedelta(days=pre_days)
    end = anchor + timedelta(days=post_days)
    # Never fetch the future; cap end at today.
    today = datetime.now(timezone.utc).date()
    if end > today:
        end = today

    article = resolve_article(topic_display)
    if not article:
        return {"status": "unresolved", "topic": topic_display, "article": None,
                "arrival_date": None, "lead_days": None}
    curve = fetch_pageviews(article, start, end)
    if not curve:
        return {"status": "no_data", "topic": topic_display, "article": article,
                "arrival_date": None, "lead_days": None}
    # Same-surge floor: count only the surge within ±MATCH_WINDOW of OUR detection, so an
    # unrelated earlier surge in the wide baseline window isn't what we measure against.
    arrival = detect_arrival_date(curve, since=(anchor - timedelta(days=MATCH_WINDOW)))
    if not arrival:
        return {"status": "no_surge", "topic": topic_display, "article": article,
                "arrival_date": None, "lead_days": None, "points": len(curve)}
    lead = (anchor - _parse_iso(arrival["arrival_date"])).days
    return {"status": "ok", "topic": topic_display, "article": article,
            "anchor_date": anchor.isoformat(),
            "arrival_date": arrival["arrival_date"], "lead_days": lead,
            "we_were_late": lead > 0, "detail": arrival, "points": len(curve)}


if __name__ == "__main__":
    import sys
    # Smoke test: anchor on a date AFTER each topic's known surge so the referee should
    # report we were "late" (arrival before anchor). Demonstrates the false-early detector.
    cases = sys.argv[1:] and [(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)] or [
        ("Strait of Hormuz", "2026-04-12"),
        ("Iran", "2026-04-12"),
        ("ChatGPT", None),
    ]
    for t, anchor in cases:
        print(json.dumps(observe(t, anchor_date=anchor), indent=1))
