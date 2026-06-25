"""
================================================================
NOW TRENDIN — DUAL-PATHWAY DETECTION (Phase C recalibration)
================================================================

THE PROBLEM (diagnosed empirically):
  Detection is composed ~60% from G (gradient strength = niche/expert
  engagement ratio) + D (dark matter = expert first-timer asymmetry).
  Both REWARD expert-community origin. Discovery feeds (Wikipedia / Google
  Trends "what the world is searching") are tagged platform_tier
  "mainstream" — so their niche ratio is ~0 and their Detection is floored,
  no matter how large the real attention. Result: a fragmented news n-gram
  ("iran announce deal") that recurs across niche/expert news feeds scored
  47 / flagged ANOMALY, while "FIFA World Cup" (777K Wikipedia views that
  day) scored 41. The engine measured the niche/mainstream RATIO and threw
  away absolute attention MAGNITUDE entirely.

THE FIX — two legitimate trend archetypes, one Detection number:
  1. EXPERT-ORIGIN (tech): scored by the existing gradient (niche
     concentration = runway ahead). THE MOAT — left completely unchanged
     when a topic is expert-origin (mainstream_ratio ~ 0).
  2. MAINSTREAM-ORIGIN (consumer culture): there is no expert phase — the
     World Cup is mainstream by nature. The honest signal is absolute
     attention MAGNITUDE + breadth + acceleration (data we already collect:
     Wikipedia views, Google Trends traffic), NOT a niche ratio that is
     structurally ~0 and meaningless for it.

  Detection blends the two pathways by how mainstream-origin the topic is:
     w = mainstream_ratio (0 = pure expert, 1 = pure mainstream)
     detection = (1-w) * expert_detection + w * mainstream_detection

  At w~0 expert topics are IDENTICAL to before (moat preserved). At w~1 a
  consumer trend is judged on real magnitude instead of a ~0 gradient.

INTEGRITY:
  Magnitude is REAL attention (log of actual views/traffic the source
  reports) — not fabricated, not circular, not our own users' demand. This
  recalibration changes how EXTERNAL attention is weighed, never invents it.
================================================================
"""

import math
import os

# ── MAINSTREAM v2 (founder model: trigger-vs-corroborator) — flag-gated, DEFAULT OFF ──────────
# Concern: a few credible news outlets prematurely flip a topic to "mainstream", which then lands
# in the gradient's denominator and SUPPRESSES the very early read we exist to catch. v2 says: a
# credible outlet is a DARK-MATTER TRIGGER until enough DISTINCT outlets corroborate. Mainstream
# requires a real news QUORUM (≥ NEWS_QUORUM_V2 distinct outlets) OR a genuine magnitude spike —
# NOT a single outlet and NOT the bare community-count branch (which leaked "footballer" on 1
# outlet). A sub-quorum, low-magnitude topic keeps mainstream weight ~0 → stays a trigger (its
# detection rides the expert/dark-matter pathway, preserved). Anti-circularity: distinct source_name
# counting means one outlet (even repeated) can't self-confirm mainstream. Tune via the backtest
# (mainstream_v2_backtest / GET /research/mainstream-v2) on the FIFA basket BEFORE flipping.
MAINSTREAM_V2 = os.getenv("MAINSTREAM_V2", "0") == "1"
NEWS_QUORUM_V2 = int(os.getenv("NEWS_QUORUM_V2", "5"))        # distinct reputable outlets ⇒ mainstream
MAG_MAINSTREAM_V2 = float(os.getenv("MAG_MAINSTREAM_V2", "60"))  # magnitude that alone ⇒ mainstream (FIFA ~82)
MAG_TRIGGER_FLOOR_V2 = float(os.getenv("MAG_TRIGGER_FLOOR_V2", "30"))  # below this + sub-quorum ⇒ stay trigger

# Tiers that represent general-public / discovery attention.
_MAINSTREAM_TIERS = {"mainstream"}

# Magnitude normalization on log1p(views/traffic):
#   log1p(2,000)   ≈ 7.6     (a small Google-Trends spike)
#   log1p(50,000)  ≈ 10.8
#   log1p(777,000) ≈ 13.6    (FIFA World Cup, the day it opened)
#   log1p(5,000,000) ≈ 15.4
_LOG_FLOOR = 7.0
_LOG_CEIL = 15.0


def _norm(x: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.0
    return max(0.0, min(100.0, (x - lo) / (hi - lo) * 100.0))


import math as _math
def _soft_cap(raw: float, knee: float = 85.0, ceil: float = 100.0) -> float:
    """Order-preserving ceiling (Fix #2, saturation). Linear up to `knee`, then the
    excess is compressed asymptotically into (knee, ceil) so the HOTTEST topics still
    separate instead of all hard-pinning at 100 (FIFA vs obama were both 100 →
    unrankable). raw 85→85, 100→~94.5, 130→~99.2, ∞→100. Strictly monotonic, so
    ranking is preserved everywhere."""
    if raw <= knee:
        return round(max(0.0, raw), 2)
    span = ceil - knee
    return round(knee + span * (1.0 - _math.exp(-(raw - knee) / span)), 2)


# Cross-platform corroboration: the niche->mainstream transition is signalled
# by the SAME/similar words appearing across MANY mainstream-tier platforms
# (news + social + broadcast + discovery), not by any single source's tier.
# One source — even a news outlet — can still be niche/early. We therefore
# count DISTINCT MAINSTREAM-TIER PLATFORMS: 1 = still concentrated (niche),
# rising to fully mainstream at BREADTH_FULL. Concentration on expert/dev
# platforms (GitHub/HN) contributes ZERO mainstream breadth — that stays dark
# matter no matter how many expert platforms corroborate it.
_BREADTH_FULL = 4   # this many distinct mainstream platforms == fully mainstream

# Baseline-relative mainstreaming (fame vs. diffusion). A topic must have at
# least this much scoring history before its baseline footprint is trusted;
# until then we fall back to absolute magnitude and flag "calibrating".
MIN_BASELINE_CYCLES = 3
_BREADTH_DELTA_FULL = 3.0   # mainstream platforms ABOVE baseline for full mainstreaming
_MAG_DELTA_FULL = 35.0      # magnitude points ABOVE baseline for full mainstreaming

# ── News-outlet corroboration (the founder's model) ──────────────────────────
# "One news source can be niche; multiple news sources + other platforms = it is
#  mainstream." News carries low per-article ENGAGEMENT (≈log1p(120)=4.79, below
# the magnitude floor of 7.0) — so a topic living PURELY in the news registers
# near-zero MAGNITUDE and would never surface on the magnitude pathway. The honest
# news signal is therefore BREADTH: how many DISTINCT reputable outlets carry it.
# A topic corroborated across this many distinct reputable outlets is mainstream-
# CONFIRMED ("it has arrived"), independent of view-count magnitude or baseline.
_NEWS_PLATFORMS = {
    "newsapi_org", "newsapi_ai", "newsdata_io", "gdelt", "guardian",
}
NEWS_MAINSTREAM_MIN = 3     # distinct reputable outlets that == mainstream-confirmed


def attention_magnitude(signals: list) -> dict:
    """
    Absolute mainstream-attention magnitude for a topic.

    Uses the PEAK mainstream-tier engagement (log of views/traffic) rather
    than a sum — one 777K-view Wikipedia signal must outweigh thirty tiny
    recurring news rows.
    """
    if not signals:
        return {"magnitude": 0.0, "mainstream_ratio": 0.0, "peak_eng": 0.0}

    def eng(s):
        try:
            return float(s.get("engagement_raw", 0) or 0)
        except (TypeError, ValueError):
            return 0.0

    main_eng = sum(eng(s) for s in signals if s.get("platform_tier") in _MAINSTREAM_TIERS)
    total_eng = sum(eng(s) for s in signals)
    mainstream_ratio = (main_eng / total_eng) if total_eng > 0 else 0.0

    main_peaks = [eng(s) for s in signals if s.get("platform_tier") in _MAINSTREAM_TIERS]
    peak = max(main_peaks) if main_peaks else 0.0
    magnitude = _norm(peak, _LOG_FLOOR, _LOG_CEIL)

    return {"magnitude": round(magnitude, 2),
            "mainstream_ratio": round(mainstream_ratio, 3),
            "peak_eng": round(peak, 2)}


_EXPERT_TIERS = {"expert", "niche"}


def mainstream_breadth(signals: list) -> dict:
    """
    Cross-COMMUNITY corroboration. Counts distinct mainstream COMMUNITIES
    (source_name — a subreddit, a channel, an outlet) rather than platforms,
    so r/SpaceX and r/all count as different venues even on one platform. Also
    counts distinct EXPERT communities so the niche->mainstream tier-migration
    can be detected.

    1 mainstream community -> 0.0 (one venue can be niche); BREADTH_FULL+ -> 1.0.
    """
    def comms(rows):
        # a "community" is its source_name; fall back to platform when absent.
        return {(s.get("source_name") or s.get("platform")) for s in rows
                if (s.get("source_name") or s.get("platform"))}

    main = [s for s in signals if s.get("platform_tier") in _MAINSTREAM_TIERS]
    expert = [s for s in signals if s.get("platform_tier") in _EXPERT_TIERS]
    main_comms = comms(main)
    expert_comms = comms(expert)
    n_main = len(main_comms)
    n_expert = len(expert_comms)

    # Distinct reputable NEWS OUTLETS carrying the topic (mainstream-tier rows on
    # a news platform). This is the founder's news-corroboration count: 1 = can be
    # niche, NEWS_MAINSTREAM_MIN+ = mainstream-confirmed. Quarantined/unverified
    # rows never reach here (they are tier 'unverified', excluded from `main`).
    news_outlets = comms([s for s in main
                          if (s.get("platform") or "").lower() in _NEWS_PLATFORMS])
    n_news = len(news_outlets)

    factor = max(0.0, min(1.0, (n_main - 1) / (_BREADTH_FULL - 1)))
    return {"breadth": round(factor, 3),
            "n_platforms": n_main,          # mainstream COMMUNITY count (name kept for compat)
            "n_expert": n_expert,
            "n_news_outlets": n_news,
            "n_sources": n_main}


def mainstream_detection(magnitude: float, M: float, I: float, P: float,
                         breadth: float = 0.0) -> float:
    """
    Detection for a mainstream-origin topic: absolute attention MAGNITUDE
    (views / search traffic) PLUS cross-outlet/community CORROBORATION breadth,
    supported by platform diversity (M), acceleration (I), persistence (P).
    Deliberately ignores G/D (expert-ratio metrics that are ~0 and meaningless
    for consumer-origin trends).

    The `breadth` term (0-1, distinct mainstream communities incl. news outlets)
    is what lets a PURELY-NEWS topic surface: news engagement is below the
    magnitude floor, so without this a story across a dozen reputable outlets
    would read magnitude ~0. Broad outlet corroboration IS mainstream attention.
    """
    return _soft_cap(
        magnitude * 0.55   # absolute attention now (views / search traffic)
        + breadth * 28.0   # cross-outlet / cross-community corroboration (news!)
        + M * 0.10         # platform diversity
        + I * 0.10         # acceleration — is it rising
        + P * 0.07)        # persistence — has it held


def blend(expert_detection: float, expert_overall: float,
          components: dict, signals: list,
          breadth_baseline: float = None, magnitude_baseline: float = None,
          baseline_cycles: int = 0, expert_confidence: float = None) -> dict:
    """
    Blend the expert (gradient) pathway with the mainstream (magnitude)
    pathway by how mainstream-origin the topic is RIGHT NOW.

    CRITICAL — fame vs. diffusion. Mainstreaming is measured as DEVIATION FROM
    THE TOPIC'S OWN BASELINE, not absolute breadth/magnitude. A household name
    (SpaceX) sits permanently broad + visible; that ambient fame is its baseline
    and must read as NEUTRAL (weight ~0) so a genuinely early SpaceX signal can
    still score high on the expert pathway. Only breadth/magnitude EXPANDING
    PAST baseline counts as mainstreaming. The same rule promotes FIFA — near
    zero off-season, so a World Cup spike is massively above its own baseline.

    Cold start: until the topic has >= MIN_BASELINE_CYCLES of history its
    baseline isn't trustworthy, so we fall back to ABSOLUTE magnitude (so real
    spikes still surface on day one) and flag the result "calibrating".

    components: {"M":…, "I":…, "P":…} (already-computed 0-100 components)
    """
    am = attention_magnitude(signals)
    br = mainstream_breadth(signals)
    mag = am["magnitude"]
    cur_n = br["n_platforms"]

    n_news = br.get("n_news_outlets", 0)
    # Mainstream-CONFIRMED is an ABSOLUTE classification ("it has arrived"),
    # independent of baseline/magnitude: corroborated across many distinct
    # reputable outlets, OR broadly across mainstream communities. This is the
    # founder's "multiple news sources + other platforms = mainstream" rule.
    if MAINSTREAM_V2:
        # v2: a real news QUORUM (≥5 distinct outlets) OR a genuine magnitude spike — NOT a
        # single outlet and NOT the bare community-count branch (which flipped "footballer" on
        # 1 outlet). This is the trigger-vs-corroborator rule: corroboration, not a lone source.
        mainstream_confirmed = (n_news >= NEWS_QUORUM_V2) or (mag >= MAG_MAINSTREAM_V2)
    else:
        mainstream_confirmed = (n_news >= NEWS_MAINSTREAM_MIN) or (cur_n >= _BREADTH_FULL)

    calibrating = baseline_cycles < MIN_BASELINE_CYCLES or breadth_baseline is None
    if calibrating:
        # No trustworthy baseline yet. Use absolute magnitude for view-count
        # spikes AND absolute breadth for news-outlet corroboration — on a topic's
        # first cycles, broad simultaneous outlet/community corroboration is itself
        # the best mainstream signal (a story across 8 outlets but with no
        # Wikipedia/Trends views has magnitude ~0 and would otherwise be invisible).
        # The moat is preserved: an early EXPERT signal sits in expert communities,
        # so its mainstream breadth is ~0 and w stays ~0 regardless.
        breadth_factor = br["breadth"]
        magnitude_factor = mag / 100.0
        breadth_mode = "calibrating"
    else:
        # Baseline-relative: how far ABOVE the topic's own norm is it now?
        breadth_factor = max(0.0, min(1.0,
            (cur_n - (breadth_baseline or 0.0)) / _BREADTH_DELTA_FULL))
        magnitude_factor = max(0.0, min(1.0,
            (mag - (magnitude_baseline or 0.0)) / _MAG_DELTA_FULL))
        breadth_mode = "baseline_relative"

    # ── Tier migration (refinement 2): the niche->mainstream TRANSITION ──
    # A topic carried in EXPERT communities that is NOW also expanding into
    # mainstream communities is crossing tiers — the highest-confidence
    # mainstreaming signal (vs. always-mainstream noise that never had an expert
    # phase). When that crossing is underway, amplify the mainstreaming weight.
    n_expert = br.get("n_expert", 0)
    tier_migration = (not calibrating) and n_expert >= 1 and breadth_factor > 0
    if tier_migration:
        breadth_factor = min(1.0, breadth_factor + 0.3)

    # ── v2 trigger-vs-corroborator clamp ──────────────────────────────────────
    # A topic carried by FEWER than the news quorum of distinct outlets AND with no real
    # magnitude is a TRIGGER (dark matter), not mainstream. Zero its mainstreaming weight so
    # detection rides the early/expert pathway — the credible source acts as an early signal,
    # not a denominator vote that suppresses it — until DISTINCT outlets actually corroborate
    # (≥ NEWS_QUORUM_V2) or attention magnitude spikes. (Magnitude path keeps FIFA mainstream.)
    if MAINSTREAM_V2 and n_news < NEWS_QUORUM_V2 and mag < MAG_TRIGGER_FLOOR_V2:
        breadth_factor = 0.0
        tier_migration = False

    # Mainstream when breadth OR magnitude expands past baseline (cross-community
    # corroboration velocity, a mass-attention spike, or a tier-crossing).
    w = round(max(breadth_factor, magnitude_factor), 3)

    M = float(components.get("M", 0) or 0)
    I = float(components.get("I", 0) or 0)
    P = float(components.get("P", 0) or 0)

    abs_breadth = br["breadth"]   # ABSOLUTE corroboration (how mainstream it IS),
                                  # vs. breadth_factor above (how much it's MOVING)
    md = mainstream_detection(mag, M, I, P, breadth=abs_breadth)

    # Mainstream OVERALL leans on magnitude + corroboration breadth + persistence
    # (a real, held, broadly-carried consumer/news trend), parallel to md.
    mo = _soft_cap(mag * 0.45 + abs_breadth * 28.0 + P * 0.18 + M * 0.15 + I * 0.08)

    # Mainstream CONFIDENCE (Fix #3, Confidence-not-discriminating). The expert
    # confidence formula is ~constant for mainstream topics (its G/D terms are ~0),
    # so FIFA (23k mentions) and obama (1.5k) both read ~58. A mainstream topic's
    # confidence is its CONFIRMATION strength: held attention magnitude + breadth of
    # corroboration + persistence. Magnitude-weighted so a 16×-bigger topic separates;
    # soft-capped so it doesn't re-saturate.
    mc = _soft_cap(mag * 0.32 + abs_breadth * 28.0 + P * 0.25 + M * 0.15)

    detection = round((1 - w) * expert_detection + w * md, 2)
    overall = round((1 - w) * expert_overall + w * mo, 2)
    confidence = (round((1 - w) * expert_confidence + w * mc, 2)
                  if expert_confidence is not None else None)

    pathway = ("mainstream" if w >= 0.6 else
               "expert" if w <= 0.2 else "blended")

    return {
        "detection": detection,
        "confidence": confidence,            # blended (None if no expert_confidence passed)
        "mainstream_confidence": round(mc, 2),
        "overall": overall,
        "pathway": pathway,
        "mainstream_ratio": w,
        "magnitude": mag,
        "breadth": br["breadth"],
        "n_mainstream_platforms": br["n_platforms"],
        "breadth_mode": breadth_mode,        # baseline_relative | calibrating
        "breadth_baseline": breadth_baseline,
        "magnitude_baseline": magnitude_baseline,
        "n_expert_communities": br.get("n_expert", 0),
        "news_outlets": n_news,
        "mainstream_confirmed": bool(mainstream_confirmed),
        "mainstream_model": "v2" if MAINSTREAM_V2 else "v1",
        "news_quorum": (NEWS_QUORUM_V2 if MAINSTREAM_V2 else NEWS_MAINSTREAM_MIN),
        "tier_migration": bool(tier_migration),
        "mainstream_detection": md,
        "expert_detection": round(expert_detection, 2),
    }
