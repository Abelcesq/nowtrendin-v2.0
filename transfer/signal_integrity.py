"""
================================================================
NOW TRENDIN — SIGNAL INTEGRITY ENGINE
Distinguishing Authentic Dark Matter from Manufactured Noise
================================================================

THE PROBLEM:
  "Dark Matter" — early hidden signal from genuine experts/insiders —
  is the highest-value input to the Gradient Score. But in 2026,
  bot networks and AI content farms can manufacture fake grassroots
  trends (astroturfing, pump-and-dump, coordinated inauthentic behavior).

  If the engine can't tell genuine early chatter from manufactured
  hype, the Gradient Score is worthless to institutions — and
  acting on a fake signal becomes a liability event.

THE APPROACH (honest about what works):
  Content-based AI-text detection is UNRELIABLE — it's an arms race
  with too many false positives to bet money on. So this engine
  weights BEHAVIORAL and NETWORK signals far more heavily, because
  those are much harder to fake at scale than the text itself:

    NETWORK authenticity   30%  — coordination detection (hardest to fake)
    TEMPORAL authenticity  25%  — organic vs synthetic timing patterns
    ACCOUNT authenticity   20%  — age diversity, creation clustering
    ENGAGEMENT authenticity 20% — genuine discussion vs hollow amplification
    INCENTIVE context       5%  — is someone positioned to profit from fakery?

OUTPUT:
  A Signal Integrity Score (0-100) and a classification:
    AUTHENTIC    (80-100) — trust the dark matter fully
    MIXED        (55-79)  — real core with some noise; weight normally
    SUSPICIOUS   (30-54)  — significant manufactured indicators; discount
    MANUFACTURED (0-29)   — likely fake; flag and heavily discount

  The score becomes a MULTIPLIER on the dark matter contribution,
  so manufactured signals are discounted, not silently dropped.
  Every flag is recorded for transparency (institutional clients
  can see exactly why a signal was trusted or doubted).

DESIGN PRINCIPLE:
  Discount and flag, never silently block. Preserve the evidence.
  An analyst must be able to see why the engine trusted or doubted
  any signal. No black box.

================================================================
"""

import re
import math
import statistics
from collections import Counter
from datetime import datetime, timezone
from typing import Optional


# ════════════════════════════════════════════════════════════════
# INPUT FORMAT — "Signal Bundle"
# A collection of posts about one topic, with author + engagement metadata.
# Collectors (Reddit, X, blogs) normalise their data into this shape.
# ════════════════════════════════════════════════════════════════
#
# {
#   "topic": "agentic coding",
#   "posts": [
#     {
#       "timestamp":  "2026-05-20T14:30:00Z",
#       "text":       "...",
#       "author": {
#         "account_age_days": 1200,
#         "followers":        4500,
#         "following":        800,
#         "has_bio":          True,
#         "has_avatar":       True,
#         "handle":           "real_researcher",
#       },
#       "engagement": {"likes": 45, "replies": 12, "reposts": 8, "quotes": 3},
#       "reply_texts": ["genuinely substantive reply text", ...],
#     }, ...
#   ],
#   "linked_instrument": "$NVDA" | None,   # for incentive analysis
# }


# ════════════════════════════════════════════════════════════════
# SECTION 1: TEMPORAL AUTHENTICITY (25%)
# Organic human activity has circadian rhythm and natural variance.
# Bots post too uniformly (regular intervals) or impossibly bursty.
# ════════════════════════════════════════════════════════════════

def analyze_temporal_authenticity(posts: list[dict]) -> dict:
    """
    Detect synthetic timing patterns.

    Authentic indicators:
      - Activity clusters in waking hours (circadian rhythm)
      - Natural variance in inter-post intervals
      - Gradual onset (organic S-curve), not a sudden step from zero

    Synthetic indicators:
      - Flat 24-hour distribution (bots don't sleep)
      - Perfectly regular intervals (scheduled posting)
      - Instantaneous spike from zero (coordinated drop)
    """
    timestamps = []
    for p in posts:
        ts = p.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            timestamps.append(dt)
        except Exception:
            continue

    if len(timestamps) < 5:
        return {"score": 50, "confidence": "low",
                "flags": [], "note": "Too few timestamps for temporal analysis"}

    timestamps.sort()
    flags = []
    score = 100.0

    # ── Check 1: Circadian rhythm (hour-of-day distribution) ──────
    hours = [t.hour for t in timestamps]
    hour_counts = Counter(hours)
    # Entropy of hour distribution — humans concentrate in waking hours
    total = len(hours)
    probs = [c / total for c in hour_counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    max_entropy = math.log2(24)  # uniform across all hours
    normalized_entropy = entropy / max_entropy

    # Very high entropy (near-uniform 24h) is suspicious — humans sleep
    if normalized_entropy > 0.92:
        score -= 30
        flags.append("activity_spread_evenly_across_24h (bots don't sleep)")
    elif normalized_entropy > 0.85:
        score -= 12
        flags.append("unusually_uniform_hourly_activity")

    # ── Check 2: Inter-arrival regularity ─────────────────────────
    intervals = [(timestamps[i+1] - timestamps[i]).total_seconds()
                 for i in range(len(timestamps) - 1)]
    if len(intervals) >= 5:
        mean_int = statistics.mean(intervals)
        if mean_int > 0:
            cv = statistics.stdev(intervals) / mean_int  # coefficient of variation
            # Too regular (low CV) = scheduled bot posting
            if cv < 0.15:
                score -= 25
                flags.append("near_perfect_posting_intervals (scheduled automation)")
            elif cv < 0.35:
                score -= 10
                flags.append("suspiciously_regular_intervals")

    # ── Check 3: Onset shape (burst detection) ────────────────────
    # Bin posts into time windows; a sudden spike from zero is synthetic
    if len(timestamps) >= 10:
        span = (timestamps[-1] - timestamps[0]).total_seconds()
        if span > 0:
            first_third_cut = timestamps[0].timestamp() + span / 3
            first_third = sum(1 for t in timestamps if t.timestamp() <= first_third_cut)
            # Organic: builds gradually. If 0 posts in first third then sudden flood:
            if first_third == 0 and len(timestamps) > 15:
                score -= 20
                flags.append("instant_onset_from_zero (coordinated drop)")

    score = max(0, min(100, score))
    return {
        "score":               round(score, 1),
        "confidence":          "high" if len(timestamps) >= 20 else "medium",
        "normalized_entropy":  round(normalized_entropy, 2),
        "flags":               flags,
    }


# ════════════════════════════════════════════════════════════════
# SECTION 2: ACCOUNT AUTHENTICITY (20%)
# Real communities have diverse account ages. Bot swarms are
# often created in clusters and share profile signatures.
# ════════════════════════════════════════════════════════════════

def analyze_account_authenticity(posts: list[dict]) -> dict:
    """
    Detect bot-swarm account signatures.

    Authentic: diverse account ages, complete profiles, varied handles.
    Synthetic: many same-age accounts, default profiles, handle+digits.
    """
    authors = [p.get("author", {}) for p in posts if p.get("author")]
    if len(authors) < 5:
        return {"score": 50, "confidence": "low", "flags": [],
                "note": "Too few authors for account analysis"}

    flags = []
    score = 100.0

    # ── Check 1: Account age diversity ────────────────────────────
    ages = [a.get("account_age_days", 365) for a in authors]
    young_accounts = sum(1 for age in ages if age < 90)
    young_pct = young_accounts / len(ages)

    if young_pct > 0.6:
        score -= 30
        flags.append(f"{int(young_pct*100)}%_accounts_under_90_days (swarm signature)")
    elif young_pct > 0.4:
        score -= 15
        flags.append(f"{int(young_pct*100)}%_young_accounts")

    # Age clustering — many accounts the same age = created together
    if len(ages) >= 10:
        age_buckets = Counter(age // 30 for age in ages)  # 30-day buckets
        biggest_bucket = max(age_buckets.values())
        if biggest_bucket / len(ages) > 0.5:
            score -= 20
            flags.append("account_ages_clustered (likely created in one batch)")

    # ── Check 2: Profile completeness ─────────────────────────────
    no_bio    = sum(1 for a in authors if not a.get("has_bio", True))
    no_avatar = sum(1 for a in authors if not a.get("has_avatar", True))
    incomplete_pct = (no_bio + no_avatar) / (len(authors) * 2)
    if incomplete_pct > 0.5:
        score -= 18
        flags.append("majority_incomplete_profiles")

    # ── Check 3: Handle patterns (name+digits = auto-generated) ──
    digit_handles = 0
    for a in authors:
        handle = a.get("handle", "")
        # Pattern: word followed by 4+ digits (e.g. user12847)
        if re.search(r'[a-zA-Z]+\d{4,}$', handle):
            digit_handles += 1
    if digit_handles / len(authors) > 0.4:
        score -= 15
        flags.append("many_auto_generated_handles (name+digits pattern)")

    # ── Check 4: Follower/following ratio anomalies ───────────────
    bad_ratio = 0
    for a in authors:
        followers = a.get("followers", 0)
        following = a.get("following", 1)
        # Bots often follow many, followed by few
        if following > 1000 and followers < following * 0.1:
            bad_ratio += 1
    if bad_ratio / len(authors) > 0.4:
        score -= 12
        flags.append("skewed_follower_ratios (mass-follow bots)")

    score = max(0, min(100, score))
    return {
        "score":              round(score, 1),
        "confidence":         "high" if len(authors) >= 20 else "medium",
        "young_account_pct":  round(young_pct * 100, 1),
        "flags":              flags,
    }


# ════════════════════════════════════════════════════════════════
# SECTION 3: NETWORK AUTHENTICITY (30% — highest weight)
# Coordination is the hardest thing to fake. Genuine diffusion is
# organic and branching; manufactured is duplicated and synchronized.
# ════════════════════════════════════════════════════════════════

def analyze_network_authenticity(posts: list[dict]) -> dict:
    """
    Detect coordinated inauthentic behavior — the strongest signal.

    Authentic: diverse phrasing, branching organic discussion, varied timing.
    Synthetic: near-duplicate text, synchronized bursts, copy-paste rings.
    """
    if len(posts) < 5:
        return {"score": 50, "confidence": "low", "flags": [],
                "note": "Too few posts for network analysis"}

    flags = []
    score = 100.0
    texts = [p.get("text", "") for p in posts if p.get("text")]

    # ── Check 1: Near-duplicate content detection ─────────────────
    # Coordinated campaigns reuse the same text with minor variations
    duplicate_pairs = 0
    comparisons = 0
    text_sigs = [_text_signature(t) for t in texts]

    for i in range(len(text_sigs)):
        for j in range(i + 1, min(i + 20, len(text_sigs))):  # sample window
            comparisons += 1
            sim = _jaccard_similarity(text_sigs[i], text_sigs[j])
            if sim > 0.7:
                duplicate_pairs += 1

    if comparisons > 0:
        dup_rate = duplicate_pairs / comparisons
        if dup_rate > 0.25:
            score -= 35
            flags.append(f"{int(dup_rate*100)}%_near_duplicate_posts (copy-paste campaign)")
        elif dup_rate > 0.12:
            score -= 18
            flags.append("elevated_content_duplication")

    # ── Check 2: Synchronized bursts ──────────────────────────────
    # Many accounts posting within seconds of each other = coordination
    timestamps = []
    for p in posts:
        try:
            dt = datetime.fromisoformat(p.get("timestamp", "").replace("Z", "+00:00"))
            timestamps.append(dt)
        except Exception:
            continue
    timestamps.sort()

    if len(timestamps) >= 10:
        # Count posts arriving within 60-second windows
        burst_clusters = 0
        i = 0
        while i < len(timestamps) - 1:
            window_count = 1
            j = i + 1
            while j < len(timestamps) and \
                  (timestamps[j] - timestamps[i]).total_seconds() <= 60:
                window_count += 1
                j += 1
            if window_count >= 5:  # 5+ posts in 60 seconds
                burst_clusters += 1
            i = j if j > i + 1 else i + 1

        if burst_clusters >= 2:
            score -= 25
            flags.append(f"{burst_clusters}_synchronized_posting_bursts (coordination)")

    # ── Check 3: Vocabulary diversity ─────────────────────────────
    # Genuine discussion has rich, varied vocabulary and real disagreement.
    # Manufactured content is repetitive and uniform.
    all_words = []
    for t in texts:
        all_words.extend(re.findall(r'\b[a-z]{3,}\b', t.lower()))
    if len(all_words) >= 50:
        unique_ratio = len(set(all_words)) / len(all_words)
        if unique_ratio < 0.25:
            score -= 20
            flags.append("low_vocabulary_diversity (templated content)")
        elif unique_ratio < 0.35:
            score -= 8
            flags.append("reduced_vocabulary_diversity")

    score = max(0, min(100, score))
    return {
        "score":           round(score, 1),
        "confidence":      "high" if len(posts) >= 20 else "medium",
        "flags":           flags,
    }


def _text_signature(text: str) -> set:
    """Create a token signature for similarity comparison."""
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    return set(words)


def _jaccard_similarity(a: set, b: set) -> float:
    """Jaccard similarity between two token sets."""
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union > 0 else 0.0


# ════════════════════════════════════════════════════════════════
# SECTION 4: ENGAGEMENT AUTHENTICITY (20%)
# Genuine topics generate real discussion (replies, disagreement).
# Manufactured ones get hollow amplification (likes/reposts, no substance).
# ════════════════════════════════════════════════════════════════

def analyze_engagement_authenticity(posts: list[dict]) -> dict:
    """
    Detect hollow amplification vs genuine discussion.

    Authentic: high reply ratio, substantive replies, diverse sentiment.
    Synthetic: high likes/reposts but few real replies; generic replies.
    """
    if len(posts) < 3:
        return {"score": 50, "confidence": "low", "flags": [],
                "note": "Too few posts for engagement analysis"}

    flags = []
    score = 100.0

    total_replies   = 0
    total_amplify   = 0   # likes + reposts
    all_reply_texts = []

    for p in posts:
        eng = p.get("engagement", {})
        total_replies += eng.get("replies", 0)
        total_amplify += eng.get("likes", 0) + eng.get("reposts", 0)
        all_reply_texts.extend(p.get("reply_texts", []))

    # ── Check 1: Reply-to-amplification ratio ─────────────────────
    # Real discussion generates replies. Pure amplification (likes/reposts
    # with no replies) suggests purchased/bot engagement.
    if total_amplify > 100:
        reply_ratio = total_replies / total_amplify
        if reply_ratio < 0.02:
            score -= 28
            flags.append("almost_no_replies_despite_high_amplification (hollow engagement)")
        elif reply_ratio < 0.05:
            score -= 12
            flags.append("low_reply_ratio")

    # ── Check 2: Reply substance ──────────────────────────────────
    # Generic replies ("this!", "so true", "💯") indicate bot engagement.
    if len(all_reply_texts) >= 10:
        generic_replies = 0
        generic_patterns = [
            r'^(this|so true|facts|💯|🔥|exactly|agreed|same)\.?!?$',
            r'^(great|amazing|love this|interesting)\.?!?$',
        ]
        for reply in all_reply_texts:
            reply_clean = reply.strip().lower()
            if len(reply_clean) < 5 or any(re.match(p, reply_clean) for p in generic_patterns):
                generic_replies += 1
        generic_pct = generic_replies / len(all_reply_texts)
        if generic_pct > 0.6:
            score -= 22
            flags.append(f"{int(generic_pct*100)}%_generic_replies (low-substance engagement)")
        elif generic_pct > 0.4:
            score -= 10
            flags.append("elevated_generic_replies")

        # Reply length diversity — real discussion varies
        reply_lengths = [len(r) for r in all_reply_texts]
        if len(reply_lengths) >= 10:
            mean_len = statistics.mean(reply_lengths)
            if mean_len > 0 and statistics.stdev(reply_lengths) / mean_len < 0.3:
                score -= 10
                flags.append("uniform_reply_lengths (templated)")

    score = max(0, min(100, score))
    return {
        "score":       round(score, 1),
        "confidence":  "high" if len(posts) >= 15 else "medium",
        "flags":       flags,
    }


# ════════════════════════════════════════════════════════════════
# SECTION 5: INCENTIVE ANALYSIS (5% modifier — context flag)
# "Cui bono?" — is someone positioned to profit from manufacturing
# this signal? Topics tied to tradeable instruments get extra scrutiny.
# ════════════════════════════════════════════════════════════════

def analyze_incentive_context(bundle: dict) -> dict:
    """
    Flag topics where there's a financial incentive to manufacture hype.

    A topic tied to a tradeable instrument (ticker, token) that suddenly
    surges in chatter is a classic pump pattern. This does NOT mean the
    signal is fake — it means it warrants extra scrutiny. The flag raises
    the bar for trusting the dark matter contribution.
    """
    flags = []
    incentive_risk = 0  # 0 = no incentive, higher = more pump-prone

    instrument = bundle.get("linked_instrument")
    topic      = bundle.get("topic", "").lower()

    if instrument:
        incentive_risk += 30
        flags.append(f"topic_tied_to_tradeable_instrument ({instrument})")

    # Pump-prone language patterns
    pump_terms = ["moon", "to the moon", "100x", "1000x", "next big",
                  "get in early", "don't miss", "buy now", "pump",
                  "gem", "moonshot", "easy money", "guaranteed"]
    posts = bundle.get("posts", [])
    pump_hits = 0
    for p in posts:
        text = p.get("text", "").lower()
        if any(term in text for term in pump_terms):
            pump_hits += 1
    if posts and pump_hits / len(posts) > 0.2:
        incentive_risk += 25
        flags.append("pump_language_present (moon/100x/get-in-early)")

    # Crypto/penny-stock topics are inherently more pump-prone
    if any(t in topic for t in ["coin", "token", "crypto", "$"]):
        incentive_risk += 15
        flags.append("asset_class_prone_to_manipulation")

    return {
        "incentive_risk": min(100, incentive_risk),
        "flags":          flags,
    }


# ════════════════════════════════════════════════════════════════
# SECTION 6: COMBINED SIGNAL INTEGRITY SCORE
# ════════════════════════════════════════════════════════════════

INTEGRITY_WEIGHTS = {
    "network":    0.30,   # hardest to fake — weighted highest
    "temporal":   0.25,
    "account":    0.20,
    "engagement": 0.20,
    # incentive is a modifier, applied separately
}


def compute_signal_integrity(bundle: dict) -> dict:
    """
    Compute the overall Signal Integrity Score for a signal bundle.

    Returns the integrity score (0-100), classification, the
    dark-matter weight multiplier, and all contributing flags.
    """
    posts = bundle.get("posts", [])
    if len(posts) < 3:
        return {
            "integrity_score":     50,
            "classification":      "INSUFFICIENT_DATA",
            "dark_matter_multiplier": 0.5,
            "confidence":          "low",
            "component_scores":    {},
            "all_flags":           [],
            "summary":             "Too few posts to assess integrity reliably.",
        }

    # Run all analyzers
    temporal   = analyze_temporal_authenticity(posts)
    account    = analyze_account_authenticity(posts)
    network    = analyze_network_authenticity(posts)
    engagement = analyze_engagement_authenticity(posts)
    incentive  = analyze_incentive_context(bundle)

    # Weighted combination
    base_score = (
        network["score"]    * INTEGRITY_WEIGHTS["network"] +
        temporal["score"]   * INTEGRITY_WEIGHTS["temporal"] +
        account["score"]    * INTEGRITY_WEIGHTS["account"] +
        engagement["score"] * INTEGRITY_WEIGHTS["engagement"]
    )

    # Incentive risk pulls the score down (extra scrutiny for pump-prone topics)
    incentive_penalty = incentive["incentive_risk"] * 0.15
    integrity_score = max(0, min(100, base_score - incentive_penalty))

    # Classification
    if integrity_score >= 80:
        classification = "AUTHENTIC"
        multiplier     = 1.0
        summary        = "Genuine organic signal. Dark matter contribution trusted fully."
    elif integrity_score >= 55:
        classification = "MIXED"
        multiplier     = 0.7
        summary        = "Real core signal with some noise. Dark matter weighted normally."
    elif integrity_score >= 30:
        classification = "SUSPICIOUS"
        multiplier     = 0.35
        summary        = "Significant manufactured indicators. Dark matter discounted heavily."
    else:
        classification = "MANUFACTURED"
        multiplier     = 0.1
        summary        = "Likely fake/coordinated. Dark matter nearly nullified and flagged."

    # Collect all flags with their source
    all_flags = []
    for name, result in [("network", network), ("temporal", temporal),
                         ("account", account), ("engagement", engagement),
                         ("incentive", incentive)]:
        for flag in result.get("flags", []):
            all_flags.append({"source": name, "flag": flag})

    return {
        "integrity_score":        round(integrity_score, 1),
        "classification":         classification,
        "dark_matter_multiplier": multiplier,
        "confidence":             network.get("confidence", "medium"),
        "component_scores": {
            "network":    network["score"],
            "temporal":   temporal["score"],
            "account":    account["score"],
            "engagement": engagement["score"],
            "incentive_risk": incentive["incentive_risk"],
        },
        "all_flags":              all_flags,
        "summary":                summary,
    }


# ════════════════════════════════════════════════════════════════
# SECTION 7: INTEGRATION — APPLY INTEGRITY TO DARK MATTER
# ════════════════════════════════════════════════════════════════

def apply_integrity_weighting(result: dict, bundle: dict) -> dict:
    """
    Drop-in: weight the dark matter contribution by signal integrity.

    Usage in the scorer, AFTER dark matter is computed but BEFORE
    the final score is assembled:

        result = apply_integrity_weighting(result, signal_bundle)

    This multiplies the dark_matter component by the integrity
    multiplier, recomputes affected scores, and attaches the full
    integrity assessment for transparency.
    """
    integrity = compute_signal_integrity(bundle)
    mult = integrity["dark_matter_multiplier"]

    # Apply to dark matter components
    original_dm_d = result.get("dark_matter_detection", 0) or 0
    original_dm_c = result.get("dark_matter_confidence", 0) or 0

    result["dark_matter_detection"]  = round(original_dm_d * mult, 1)
    result["dark_matter_confidence"] = round(original_dm_c * mult, 1)

    # Attach full integrity assessment for transparency / audit
    result["signal_integrity"] = {
        "score":          integrity["integrity_score"],
        "classification": integrity["classification"],
        "multiplier_applied": mult,
        "summary":        integrity["summary"],
        "component_scores": integrity["component_scores"],
        "flags":          integrity["all_flags"],
        "dark_matter_before": original_dm_d,
        "dark_matter_after":  result["dark_matter_detection"],
    }

    # If manufactured, add a prominent warning flag
    if integrity["classification"] in ("MANUFACTURED", "SUSPICIOUS"):
        result["integrity_warning"] = (
            f"⚠ Signal integrity {integrity['classification']} "
            f"({integrity['integrity_score']}/100). "
            f"Dark matter discounted {int((1-mult)*100)}%. "
            f"Treat this signal with caution."
        )

    return result


# ════════════════════════════════════════════════════════════════
# SECTION 8: DEMO — authentic vs manufactured
# ════════════════════════════════════════════════════════════════

def run_demo():
    from datetime import timedelta

    print("\n" + "="*68)
    print("NOW TRENDIN — SIGNAL INTEGRITY ENGINE — DEMO")
    print("="*68)

    base = datetime(2026, 5, 20, 9, 0, tzinfo=timezone.utc)

    # ── AUTHENTIC bundle: organic expert chatter ─────────────────
    authentic_posts = []
    import random
    random.seed(42)
    vocab_a = ["agent", "memory", "context", "persistence", "retrieval", "embedding",
               "benchmark", "latency", "token", "framework", "architecture", "approach",
               "tried", "results", "interesting", "production", "scaling", "issue",
               "solved", "comparison", "tradeoff", "implementation", "pattern"]
    for i in range(30):
        # Organic: waking-hours timing, natural gaps, varied content
        hour_offset = random.choice([0,1,2,3,4,5,6,7,8,9,10,11,12]) + random.random()*2
        words = random.sample(vocab_a, random.randint(6, 12))
        authentic_posts.append({
            "timestamp": (base + timedelta(hours=hour_offset, minutes=random.randint(0,59))).isoformat(),
            "text": " ".join(words) + f" {random.choice(['?', '.', '!'])}",
            "author": {
                "account_age_days": random.randint(200, 3000),
                "followers": random.randint(800, 80000),
                "following": random.randint(100, 2000),
                "has_bio": True, "has_avatar": True,
                "handle": random.choice(["mleng", "airesearcher", "devops_jane", "quantdev"]) + str(random.randint(1,99)),
            },
            "engagement": {"likes": random.randint(10,80), "replies": random.randint(3,20),
                           "reposts": random.randint(1,10), "quotes": random.randint(0,5)},
            "reply_texts": [
                "have you tried the new approach with persistent context?",
                "the latency tradeoff matters more than the benchmark here",
                "disagree, the embedding approach scales better in production",
            ],
        })
    authentic_bundle = {"topic": "agent memory", "posts": authentic_posts, "linked_instrument": None}

    # ── MANUFACTURED bundle: coordinated bot pump ────────────────
    manufactured_posts = []
    template = "this token is going to the moon 100x get in early dont miss"
    for i in range(30):
        # Synthetic: uniform 24h timing, regular intervals, duplicate text
        manufactured_posts.append({
            "timestamp": (base + timedelta(minutes=i*2)).isoformat(),  # perfectly regular
            "text": template + (f" {i}" if i % 3 else ""),  # near-duplicate
            "author": {
                "account_age_days": random.randint(5, 45),  # all young
                "followers": random.randint(2, 50),
                "following": random.randint(2000, 5000),  # mass-follow
                "has_bio": False, "has_avatar": False,
                "handle": "user" + str(random.randint(10000, 99999)),  # auto-generated
            },
            "engagement": {"likes": random.randint(200,500), "replies": 0,  # hollow
                           "reposts": random.randint(100,300), "quotes": 0},
            "reply_texts": ["🚀", "💯", "moon", "lfg"],
        })
    manufactured_bundle = {"topic": "$MOONCOIN", "posts": manufactured_posts,
                          "linked_instrument": "$MOONCOIN"}

    for name, bundle in [("AUTHENTIC (organic expert chatter)", authentic_bundle),
                        ("MANUFACTURED (coordinated bot pump)", manufactured_bundle)]:
        result = compute_signal_integrity(bundle)
        print(f"\n{'─'*68}")
        print(f"BUNDLE: {name}")
        print(f"{'─'*68}")
        print(f"  Integrity Score:  {result['integrity_score']}/100")
        print(f"  Classification:   {result['classification']}")
        print(f"  DM Multiplier:    {result['dark_matter_multiplier']}x")
        print(f"  Components: network={result['component_scores']['network']} "
              f"temporal={result['component_scores']['temporal']} "
              f"account={result['component_scores']['account']} "
              f"engagement={result['component_scores']['engagement']}")
        print(f"  Summary: {result['summary']}")
        if result['all_flags']:
            print(f"  Flags raised:")
            for f in result['all_flags'][:8]:
                print(f"    [{f['source']}] {f['flag']}")

    print("\n" + "="*68)
    print("The engine weights NETWORK + TEMPORAL signals most heavily because")
    print("they are hardest to fake. Content/text analysis is deliberately")
    print("minor — it is an unreliable arms race. Behavior betrays the bots.")
    print("="*68)


if __name__ == "__main__":
    run_demo()
