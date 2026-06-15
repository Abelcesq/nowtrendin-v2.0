"""
================================================================
NOW TRENDIN — X (TWITTER) SIGNAL MODULE
Dual-Role: Detection + Confirmation
================================================================

THE STRATEGIC ASSESSMENT (why X is different from Google Trends):

  Google Trends is validation-only — it lags by design.
  X is DUAL-ROLE — it spans the diffusion pipeline:

    EXPERT X      →  Stage 2 (Expert Signal)    →  feeds DETECTION
    (niche technical accounts, researchers,
     small high-signal communities)

    VIRAL X       →  Stage 3-4 (Consumer/Media)  →  feeds CONFIRMATION
    (broad accounts, high impressions,
     mainstream amplification)

  This means you can compute the GRADIENT WITHIN X ITSELF — the same
  niche-vs-mainstream ratio that defines the whole Gradient Score,
  measured on a single platform. The ratio of expert-X chatter to
  viral-X volume is a powerful early-warning indicator:

    HIGH expert / LOW viral   →  early — experts know, public doesn't
    HIGH expert / HIGH viral  →  crossing — diffusing to mainstream NOW
    LOW expert  / HIGH viral  →  late — already mainstream, likely priced in

HOW X DATA FLOWS INTO THE GRADIENT SCORE:

  X Author Gradient   →  Gradient Strength component (within-X niche concentration)
  X Velocity          →  Inertia component (acceleration of mentions)
  X presence          →  Medium Sequence component (platform in diffusion path)
  X Engagement Quality→  Dark Matter signal (genuine interest vs passive volume)

CAUTION (built into the scoring):
  X is noisy, bot-prone, and engagement can be manipulated. This module
  weights ENGAGEMENT QUALITY (replies/quotes from credible accounts)
  over raw volume, and discounts signals that look bot-amplified
  (high volume + low reply ratio + new accounts).

API ACCESS:
  Uses X API v2 with OAuth 2.0 Bearer Token (app-only auth) for
  reading public tweets. Set X_BEARER_TOKEN env var (from your
  developer portal — App: JOINMYNET, App ID 29655389).
  Endpoints used:
    GET /2/tweets/counts/recent  — volume over time (low quota cost)
    GET /2/tweets/search/recent  — sample tweets + author authority
  Tier note: recent search requires Basic tier or above.

================================================================
"""

import os
import json
import math
import statistics
from datetime import datetime, timezone, timedelta
from typing import Optional
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote

X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN", "")
X_API_BASE     = "https://api.twitter.com/2"

try:
    from collector_health import log_api_call as _api
except Exception:
    def _api(*a, **k): pass

# Signal Integrity engine — distinguishes genuine expert chatter from
# coordinated bot/astroturf content. X is the highest bot-risk source, so
# its dark-matter contribution is weighted by an authenticity multiplier.
try:
    import signal_integrity
    _INTEGRITY_AVAILABLE = True
except Exception:
    _INTEGRITY_AVAILABLE = False


# ════════════════════════════════════════════════════════════════
# SECTION 1: X API CLIENT
# ════════════════════════════════════════════════════════════════

def _x_get(endpoint: str, params: dict) -> Optional[dict]:
    """Make an authenticated X API v2 request (app-only Bearer auth)."""
    if not X_BEARER_TOKEN:
        print("X_BEARER_TOKEN not set — skipping X collection")
        return None

    url = f"{X_API_BASE}/{endpoint}?{urlencode(params)}"
    req = Request(url, headers={
        "Authorization": f"Bearer {X_BEARER_TOKEN}",
        "User-Agent":    "NowTrendIn/2.0",
    })
    try:
        with urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        # 429 = rate limit, 403 = tier access, 401 = auth
        print(f"X API error for {endpoint}: {e}")
        return None


# ════════════════════════════════════════════════════════════════
# SECTION 2: VOLUME & VELOCITY (Inertia signal)
# Uses the counts endpoint — low quota cost, daily granularity
# ════════════════════════════════════════════════════════════════

def collect_x_volume(topic: str, days: int = 7) -> Optional[dict]:
    """
    Collect tweet volume over time for a topic.

    Returns daily counts and computed velocity (acceleration).
    The counts/recent endpoint is cheap — use it first to decide
    whether a topic is worth the more expensive search sampling.
    """
    _api("x")
    # Build query: topic, exclude retweets, English
    query = f'"{topic}" -is:retweet lang:en'

    data = _x_get("tweets/counts/recent", {
        "query":       query,
        "granularity": "day",
    })
    if not data:
        return None

    counts = data.get("data", [])
    if not counts:
        return {"topic": topic, "total": 0, "daily": [], "velocity": 0}

    daily = [{"date": c.get("start", "")[:10], "count": c.get("tweet_count", 0)}
             for c in counts]
    total = sum(d["count"] for d in daily)

    # counts_recent's window edges are partial days: the trailing bucket is the
    # in-progress UTC day (and the leading bucket can be a partial too). Including
    # a stub day understates velocity, so compute acceleration over complete days
    # only. A bucket is "partial" if it's an edge and far below the interior median.
    def _median(xs):
        s = sorted(xs)
        n = len(s)
        if n == 0:
            return 0
        return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2

    full = list(daily)
    if len(full) >= 3:
        interior_med = _median([d["count"] for d in full[1:-1]]) or 1
        # drop trailing partial (in-progress day)
        if full[-1]["count"] < 0.5 * interior_med:
            full = full[:-1]
        # drop leading partial (window start mid-day)
        if len(full) >= 3 and full[0]["count"] < 0.5 * interior_med:
            full = full[1:]

    # Velocity = recent half vs earlier half (acceleration), complete days only
    mid = len(full) // 2
    if mid >= 1:
        earlier = sum(d["count"] for d in full[:mid]) / max(1, mid)
        recent  = sum(d["count"] for d in full[mid:]) / max(1, len(full) - mid)
        velocity = round((recent - earlier) / max(1, earlier) * 100, 1)  # % change
    else:
        velocity = 0

    return {
        "topic":      topic,
        "total":      total,
        "daily":      daily,            # full series (for display/audit)
        "full_days":  len(full),        # complete days used for velocity
        "velocity":   velocity,         # % acceleration (partial days excluded)
        "days":       days,
    }


# ════════════════════════════════════════════════════════════════
# SECTION 3: AUTHOR AUTHORITY GRADIENT (Gradient Strength signal)
# The key dual-role computation: expert-X vs viral-X
# ════════════════════════════════════════════════════════════════

def collect_x_author_gradient(topic: str, sample_size: int = 100) -> Optional[dict]:
    """
    Sample recent tweets about a topic and segment by author authority.

    Computes the INTRA-X GRADIENT: the ratio of expert/niche-account
    activity to broad/mainstream-account activity. This is the single
    most valuable X signal — it tells you WHERE on the diffusion curve
    the topic sits, using only X data.

    Author segmentation heuristic:
      EXPERT-tier signal indicators:
        - moderate follower count (1K-100K — niche authority, not celebrity)
        - high engagement-to-follower ratio (genuine community interest)
        - account age > 1 year (not a bot/throwaway)
      MAINSTREAM-tier indicators:
        - very high followers (>500K — broad reach)
        - OR very low followers + low engagement (grassroots/bot noise)
    """
    _api("x")
    query = f'"{topic}" -is:retweet lang:en'

    # sort_order: "relevancy" surfaces the top/most-engaged posts in the recent
    # window (vs "recency" = newest first). Env-overridable.
    sort_order = os.getenv("X_SEARCH_SORT", "relevancy")
    # X search/recent caps at 100 results/request, so fetch `sample_size` (e.g.
    # 120) across pages via next_token. Each page's posts count against the
    # monthly post cap; per-page max_results must be in [10,100].
    tweets, users, next_token, fetched = [], {}, None, 0
    while fetched < sample_size:
        want = min(100, sample_size - fetched)
        if want < 10:
            want = 10  # API floor; we trim to sample_size after the loop
        params = {
            "query":        query,
            "max_results":  want,
            "sort_order":   sort_order,
            "tweet.fields": "public_metrics,created_at",
            "expansions":   "author_id",
            # description + profile_image_url let the Signal Integrity engine read
            # profile completeness (bio/avatar) for bot-swarm detection.
            "user.fields":  "public_metrics,verified,created_at,description,profile_image_url,username",
        }
        if next_token:
            params["next_token"] = next_token
        data = _x_get("tweets/search/recent", params)
        if not data:
            break
        page = data.get("data", []) or []
        tweets.extend(page)
        for u in data.get("includes", {}).get("users", []) or []:
            users[u["id"]] = u
        fetched += len(page)
        next_token = (data.get("meta", {}) or {}).get("next_token")
        if not next_token or not page:
            break
    # Trim to the requested sample size (last page may overshoot via the floor).
    tweets = tweets[:sample_size]
    if not tweets and not users:
        return None

    if not tweets:
        return {"topic": topic, "expert_score": 0, "mainstream_score": 0,
                "intra_gradient": 0, "sample": 0}

    expert_signal     = 0.0
    mainstream_signal = 0.0
    total_engagement  = 0
    bot_suspect       = 0
    bundle_posts      = []   # normalized posts for the Signal Integrity engine

    for tweet in tweets:
        author = users.get(tweet.get("author_id"))
        if not author:
            continue

        am        = author.get("public_metrics", {})
        followers = am.get("followers_count", 0)
        following = am.get("following_count", 0)
        metrics   = tweet.get("public_metrics", {})
        engagement = (
            metrics.get("like_count", 0) +
            metrics.get("reply_count", 0) * 3 +   # replies weighted (real discussion)
            metrics.get("quote_count", 0) * 2     # quotes weighted (amplification w/ commentary)
        )
        total_engagement += engagement

        # Engagement-to-follower ratio (genuine interest indicator)
        eng_ratio = engagement / max(1, followers)

        # Account age (bot detection)
        try:
            created = datetime.fromisoformat(
                author.get("created_at", "").replace("Z", "+00:00")
            )
            age_days = (datetime.now(timezone.utc) - created).days
        except Exception:
            age_days = 365

        # ── Normalize this post for the Signal Integrity engine ──────
        avatar_url = author.get("profile_image_url", "") or ""
        bundle_posts.append({
            "timestamp": tweet.get("created_at", ""),
            "text":      tweet.get("text", ""),
            "author": {
                "account_age_days": age_days,
                "followers":        followers,
                "following":        following,
                "has_bio":          bool((author.get("description") or "").strip()),
                "has_avatar":       "default_profile" not in avatar_url,
                "handle":           author.get("username", ""),
            },
            "engagement": {
                "likes":   metrics.get("like_count", 0),
                "replies": metrics.get("reply_count", 0),
                "reposts": metrics.get("retweet_count", 0),
                "quotes":  metrics.get("quote_count", 0),
            },
        })

        # Classify the signal
        if 1000 <= followers <= 100000 and eng_ratio > 0.005 and age_days > 365:
            # Niche authority — the high-value expert signal
            expert_signal += engagement * 1.5
        elif followers > 500000:
            # Broad reach — mainstream amplification
            mainstream_signal += engagement
        elif followers < 100 and eng_ratio < 0.001 and age_days < 90:
            # Likely bot/noise — discount heavily
            bot_suspect += 1
            mainstream_signal += engagement * 0.2
        else:
            # General audience
            mainstream_signal += engagement * 0.6

    # Intra-X gradient: expert concentration relative to total
    total_signal = expert_signal + mainstream_signal
    intra_gradient = (expert_signal / total_signal * 100) if total_signal > 0 else 0

    return {
        "topic":            topic,
        "expert_score":     round(expert_signal, 1),
        "mainstream_score": round(mainstream_signal, 1),
        "intra_gradient":   round(intra_gradient, 1),   # 0-100, higher = more expert-concentrated
        "total_engagement": total_engagement,
        "bot_suspect_count":bot_suspect,
        "sample":           len(tweets),
        "posts":            bundle_posts,   # for Signal Integrity analysis
    }


# ════════════════════════════════════════════════════════════════
# SECTION 4: X DIFFUSION STAGE CLASSIFICATION
# Maps the intra-X gradient to a diffusion stage
# ════════════════════════════════════════════════════════════════

def classify_x_diffusion(volume: dict, gradient: dict) -> dict:
    """
    Combine volume and author gradient into a diffusion-stage read.

    This is the dual-role output: it tells the Gradient Score engine
    BOTH where the topic sits AND whether X is acting as a detection
    signal (expert-led) or a confirmation signal (viral-led).
    """
    if not gradient or not volume:
        return {"stage": "unknown", "role": "none", "x_contribution": 0}

    intra    = gradient.get("intra_gradient", 0)
    velocity = volume.get("velocity", 0)
    total    = volume.get("total", 0)

    # Determine stage and role
    if intra >= 60 and total < 5000:
        stage = "expert_emerging"
        role  = "DETECTION"      # X is acting as an early detection signal
        interpretation = (
            "Expert-concentrated on X with low broad volume. "
            "Niche authorities are discussing this before the public. "
            "X is functioning as a Stage 2 detection signal."
        )
    elif intra >= 40 and velocity > 50:
        stage = "crossing"
        role  = "DETECTION+CONFIRMATION"
        interpretation = (
            "Accelerating with meaningful expert concentration. "
            "The topic is crossing from expert to mainstream on X right now — "
            "the highest-value diffusion window."
        )
    elif intra < 40 and total > 10000:
        stage = "viral_mainstream"
        role  = "CONFIRMATION"   # X is acting as a confirmation/late signal
        interpretation = (
            "High volume, low expert concentration. The topic is already "
            "mainstream on X. Treat as confirmation, not detection — "
            "likely past the early-actor window."
        )
    else:
        stage = "background"
        role  = "WEAK"
        interpretation = "Low signal on X. Not yet a meaningful indicator."

    # X contribution score to the gradient (0-100)
    # Weighted toward expert concentration and velocity
    x_contribution = round(
        min(100,
            intra * 0.5 +                          # expert concentration
            min(40, max(0, velocity)) * 0.3 +      # acceleration (capped)
            min(20, math.log10(max(1, total)) * 5) # volume (log-scaled, capped)
        ), 1
    )

    return {
        "stage":          stage,
        "role":           role,
        "interpretation": interpretation,
        "x_contribution": x_contribution,
        "intra_gradient": intra,
        "velocity":       velocity,
        "total_volume":   total,
    }


# ════════════════════════════════════════════════════════════════
# SECTION 5: GRADIENT SCORE INTEGRATION
# How X signal feeds into the main Gradient Score components
# ════════════════════════════════════════════════════════════════

def build_x_gradient_contribution(topic: str) -> dict:
    """
    Full X signal pipeline for one topic, formatted to plug into
    the main Gradient Score engine as component contributions.

    Returns contributions to: gradient_strength, inertia, medium, dark_matter
    plus the diffusion classification and a provenance record.
    """
    volume   = collect_x_volume(topic)
    # Pull X_SAMPLE_SIZE posts per topic (default 120, paginated 100+20). Each
    # post counts against the monthly cap; the engine budgets _X_POSTS_PER_PULL
    # to match this so accounting stays accurate.
    gradient = collect_x_author_gradient(topic, sample_size=int(os.getenv("X_SAMPLE_SIZE", "120")))

    if not volume or not gradient:
        return {
            "available":     False,
            "reason":        "X data unavailable (no token, rate limit, or tier access)",
            "contributions": {},
        }

    diffusion = classify_x_diffusion(volume, gradient)

    # ── Signal Integrity: is this genuine chatter or a coordinated pump? ──
    # Build a bundle from the sampled posts and score authenticity. The
    # resulting multiplier (1.0 authentic → 0.1 manufactured) discounts the
    # dark-matter contribution so bot-amplified topics can't fake an early
    # signal. Discount, never silently block — the full assessment is returned.
    integrity = None
    dm_multiplier = 1.0
    if _INTEGRITY_AVAILABLE:
        try:
            bundle = {
                "topic": topic,
                "posts": gradient.get("posts", []),
                # $-prefixed topics are tradeable → incentive scrutiny
                "linked_instrument": topic if topic.strip().startswith("$") else None,
            }
            assessment = signal_integrity.compute_signal_integrity(bundle)
            dm_multiplier = assessment["dark_matter_multiplier"]
            integrity = {
                "score":          assessment["integrity_score"],
                "classification": assessment["classification"],
                "multiplier":     dm_multiplier,
                "summary":        assessment["summary"],
                "component_scores": assessment["component_scores"],
                "flags":          assessment["all_flags"],
            }
        except Exception as _ie:
            print(f"signal_integrity error for '{topic}': {_ie}")

    # Map X signals onto Gradient Score components
    contributions = {
        # Author gradient feeds Gradient Strength (within-X niche concentration)
        "gradient_strength_boost": round(gradient["intra_gradient"] * 0.6, 1),

        # Velocity feeds Inertia (acceleration evidence)
        "inertia_boost": round(min(60, max(0, volume["velocity"])) * 0.5, 1),

        # X presence adds to Medium Sequence (another diffusion platform)
        "medium_sequence_boost": 15 if volume["total"] > 100 else 5,

        # High engagement-to-volume with expert concentration = dark matter signal.
        # Discounted by the integrity multiplier so manufactured pumps can't
        # masquerade as genuine early expert chatter.
        "dark_matter_boost": round(
            (gradient["intra_gradient"] / 100) *
            min(20, gradient["total_engagement"] / max(1, gradient["sample"])) *
            dm_multiplier,
            1
        ),
    }

    out = {
        "available":      True,
        "topic":          topic,
        "diffusion":      diffusion,
        "contributions":  contributions,
        "x_role":         diffusion["role"],
        "x_stage":        diffusion["stage"],
        "provenance":     f"x_api:search_recent+counts_recent (sample {gradient['sample']})",
        "raw": {
            "volume":   volume,
            "gradient": {k: v for k, v in gradient.items() if k != "posts"},
        },
    }
    if integrity is not None:
        out["signal_integrity"] = integrity
    return out


def apply_x_signal(result: dict, topic: str) -> dict:
    """
    Drop-in: enrich a Gradient Score result with X signal contributions.

    Adds X data as ADDITIVE boosts to the relevant components, respecting
    the dual-role principle: expert-X strengthens detection, viral-X is
    logged as confirmation but does NOT inflate the detection score.

    Usage in the scorer:
        result = apply_x_signal(result, topic_display)
    """
    x = build_x_gradient_contribution(topic)
    if not x["available"]:
        result["x_signal"] = {"available": False}
        return result

    role = x["x_role"]
    contrib = x["contributions"]

    # Only apply detection-strengthening boosts when X is in a
    # DETECTION or CROSSING role. When X is purely CONFIRMATION
    # (viral/mainstream), we record it but do NOT inflate detection —
    # that would defeat the early-detection purpose.
    if role in ("DETECTION", "DETECTION+CONFIRMATION"):
        result["detection_score"] = min(100, round(
            result.get("detection_score", 0) +
            contrib["gradient_strength_boost"] * 0.15 +
            contrib["inertia_boost"] * 0.10,
            1
        ))
        result["confidence_score"] = min(100, round(
            result.get("confidence_score", 0) +
            contrib["inertia_boost"] * 0.12 +
            contrib["dark_matter_boost"] * 0.10,
            1
        ))

    # Always attach the X signal detail for transparency
    result["x_signal"] = {
        "available":      True,
        "role":           role,
        "stage":          x["x_stage"],
        "interpretation": x["diffusion"]["interpretation"],
        "x_contribution": x["diffusion"]["x_contribution"],
        "intra_gradient": x["diffusion"]["intra_gradient"],
        "velocity":       x["diffusion"]["velocity"],
        "provenance":     x["provenance"],
    }

    return result


# ════════════════════════════════════════════════════════════════
# SECTION 6: DEMO (works without live API — uses synthetic data)
# ════════════════════════════════════════════════════════════════

def run_demo():
    print("\n" + "="*66)
    print("NOW TRENDIN — X (TWITTER) SIGNAL MODULE — DEMO")
    print("="*66)

    # Synthetic scenarios showing the dual-role classification
    scenarios = [
        ("agentic coding (early)", 
         {"topic": "agentic coding", "total": 3200, "velocity": 85,
          "daily": [], "days": 7},
         {"topic": "agentic coding", "expert_score": 720, "mainstream_score": 280,
          "intra_gradient": 72, "total_engagement": 4800, "bot_suspect_count": 2,
          "sample": 90}),

        ("$NVDA earnings (crossing)",
         {"topic": "$NVDA", "total": 8500, "velocity": 120,
          "daily": [], "days": 7},
         {"topic": "$NVDA", "expert_score": 1100, "mainstream_score": 1400,
          "intra_gradient": 44, "total_engagement": 22000, "bot_suspect_count": 8,
          "sample": 100}),

        ("ai (mainstream)",
         {"topic": "ai", "total": 95000, "velocity": 10,
          "daily": [], "days": 7},
         {"topic": "ai", "expert_score": 800, "mainstream_score": 9200,
          "intra_gradient": 8, "total_engagement": 180000, "bot_suspect_count": 45,
          "sample": 100}),
    ]

    for name, volume, gradient in scenarios:
        diffusion = classify_x_diffusion(volume, gradient)
        print(f"\n── {name} ──")
        print(f"  Intra-X gradient: {gradient['intra_gradient']}  "
              f"(expert concentration, 0-100)")
        print(f"  Volume: {volume['total']:,}   Velocity: {volume['velocity']}%")
        print(f"  → Stage: {diffusion['stage']}")
        print(f"  → Role:  {diffusion['role']}")
        print(f"  → X contribution to gradient: {diffusion['x_contribution']}")
        print(f"  → {diffusion['interpretation']}")

    print("\n" + "="*66)
    print("KEY: expert-led X signal feeds DETECTION; viral-led X is logged")
    print("as CONFIRMATION only and does not inflate the detection score.")
    print("This preserves the early-detection purpose of the Gradient Score.")
    print("="*66)


if __name__ == "__main__":
    run_demo()
