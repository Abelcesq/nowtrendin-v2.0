"""
================================================================
NOW TRENDIN — INTEGRATION PATCH
gravitational_anomaly_detector.py
================================================================

This file shows the EXACT modifications to make to your existing
gravitational_anomaly_detector.py. Each section shows:
  - WHERE the change goes (the anchor — existing code to find)
  - BEFORE (what's there now)
  - AFTER (what it becomes)

There are 5 edit points. Make them in order.

The integration philosophy:
  - Do NOT touch the core scoring math (the 5-component calculation)
  - ADD a calibration layer that wraps the raw output
  - The layer corrects: gradient over-discount, bigram noise,
    AI topic tiers, and lead-time-with-zero-inertia

PIPELINE ORDER (this is why the edits are sequenced as they are):

  raw signals collected
        │
        ▼
  score_topic() computes 5 raw components
        │
        ▼
  [EDIT 3] apply_signal_count_modifier()   ← adds volume variance to gradient
        │
        ▼
  result dict assembled (detection, confidence, etc.)
        │
        ▼
  [EDIT 4a] apply_calibration()            ← maturity discount + anomaly gate
        │
        ▼
  [EDIT 4b] apply_ai_intelligence()        ← tier scores override for AI topics
        │
        ▼
  return result
        │
        ▼
  endpoint collects all results
        │
        ▼
  [EDIT 5] filter_topics_batch()           ← removes bigram noise
        │
        ▼
  return to API / frontend
================================================================
"""

# ════════════════════════════════════════════════════════════════
# EDIT 1 — ADD IMPORTS
# Location: top of gravitational_anomaly_detector.py, after existing imports
# ════════════════════════════════════════════════════════════════

# ─── BEFORE ───────────────────────────────────────────────────────
# import os
# import sqlite3
# from datetime import datetime, timezone, timedelta
# ... (your existing imports)

# ─── AFTER ────────────────────────────────────────────────────────
# import os
# import sqlite3
# from datetime import datetime, timezone, timedelta
# ... (your existing imports)

# ── ADD THESE: calibration layer imports ──────────────────────────
from signal_calibration_integration import (
    apply_calibration,
    seed_known_topics,
    init_calibration_db,
    recompute_velocities,
)
from calibration_parameter_corrections import (
    apply_signal_count_modifier,
    filter_topics_batch,
)
from ai_topic_intelligence import apply_ai_intelligence


# ════════════════════════════════════════════════════════════════
# EDIT 2 — INITIALIZE + SEED ON STARTUP
# Location: after DB_PATH is defined and after your init_db() call
# ════════════════════════════════════════════════════════════════

# ─── BEFORE ───────────────────────────────────────────────────────
# DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
#
# def init_db():
#     # ... your existing table creation
#     pass
#
# init_db()

# ─── AFTER ────────────────────────────────────────────────────────
# DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
#
# def init_db():
#     # ... your existing table creation
#     pass
#
# init_db()
#
# ── ADD THESE: initialise calibration tables and seed known topics ──
# init_calibration_db(DB_PATH)   # creates topic_maturity, topic_baselines,
#                                #  topic_score_history tables
# seed_known_topics(DB_PATH)     # pre-loads "ai agent", "llm", etc. so
#                                #  calibration is correct on first run


# ════════════════════════════════════════════════════════════════
# EDIT 3 — ADD SIGNAL COUNT MODIFIER INSIDE score_topic()
# Location: inside score_topic(), right after the raw gradient is computed
# ════════════════════════════════════════════════════════════════

# ─── BEFORE ───────────────────────────────────────────────────────
# def score_topic(topic_key):
#     # ... collect signals for this topic
#     niche_count      = count_niche_signals(...)
#     mainstream_count = count_mainstream_signals(...)
#
#     raw_gradient = compute_gradient_strength(niche_count, mainstream_count)
#     # ... rest of scoring

# ─── AFTER ────────────────────────────────────────────────────────
# def score_topic(topic_key):
#     # ... collect signals for this topic
#     niche_count      = count_niche_signals(...)
#     mainstream_count = count_mainstream_signals(...)
#
#     raw_gradient = compute_gradient_strength(niche_count, mainstream_count)
#
#     # ── ADD THIS: volume-based variance so a 15-signal topic ──────
#     #    scores higher than a 3-signal topic even on first run ────
#     raw_gradient = apply_signal_count_modifier(
#         raw_gradient,
#         signal_count   = total_signals,   # use your actual variable name
#         platform_count = platform_count,  # use your actual variable name
#     )
#     # ... rest of scoring continues unchanged


# ════════════════════════════════════════════════════════════════
# EDIT 4 — APPLY CALIBRATION + AI INTELLIGENCE AT END OF score_topic()
# Location: inside score_topic(), immediately before the return statement
# ════════════════════════════════════════════════════════════════

# ─── BEFORE ───────────────────────────────────────────────────────
# def score_topic(topic_key):
#     # ... all the scoring logic ...
#     result = {
#         "topic_key":         topic_key,
#         "topic_display":     topic_display,
#         "detection_score":   detection_score,
#         "confidence_score":  confidence_score,
#         "overall_score":     overall_score,
#         "gradient_strength_detection":  gradient_d,
#         "gradient_strength_confidence": gradient_c,
#         "inertia_score":     inertia,
#         "platform_count":    platform_count,
#         "total_signals":     total_signals,
#         "signal_stage":      stage,
#         # ... all other fields ...
#     }
#     return result

# ─── AFTER ────────────────────────────────────────────────────────
# def score_topic(topic_key):
#     # ... all the scoring logic (unchanged) ...
#     result = {
#         "topic_key":         topic_key,
#         "topic_display":     topic_display,
#         "detection_score":   detection_score,
#         "confidence_score":  confidence_score,
#         "overall_score":     overall_score,
#         "gradient_strength_detection":  gradient_d,
#         "gradient_strength_confidence": gradient_c,
#         "inertia_score":     inertia,
#         "platform_count":    platform_count,
#         "total_signals":     total_signals,
#         "signal_stage":      stage,
#         # ... all other fields ...
#     }
#
#     # ── ADD THESE TWO LINES, IN THIS ORDER, BEFORE return ─────────
#     # 1. General maturity calibration (discount established topics,
#     #    fix anomaly gate, gate lead-time on inertia)
#     result = apply_calibration(result, db_path=DB_PATH)
#
#     # 2. AI taxonomy tier scores — OVERRIDES for known AI topics only.
#     #    Non-AI topics pass through unchanged. This is what makes
#     #    "agentic coding" score 95+ and "ai agent" score ~26.
#     result = apply_ai_intelligence(result)
#
#     return result

# WHY THIS ORDER:
#   apply_calibration runs first and handles the general case
#   (maturity, velocity, anomaly gate) for ALL topics.
#   apply_ai_intelligence runs second and, for topics in the AI
#   taxonomy, replaces the scores with tier-aware values. For topics
#   NOT in the taxonomy, it returns the result unchanged — so the
#   calibration from step 1 stands. No conflict.


# ════════════════════════════════════════════════════════════════
# EDIT 5 — ADD NOISE FILTER AT THE ENDPOINT / LIST LEVEL
# Location: wherever you build the list of all scored topics for the API
# (likely a function like get_all_scores() or the /scores endpoint handler)
# ════════════════════════════════════════════════════════════════

# ─── BEFORE ───────────────────────────────────────────────────────
# def get_all_scores():
#     all_keys      = get_all_topic_keys()
#     scored_topics = [score_topic(k) for k in all_keys]
#     scored_topics.sort(key=lambda x: x["detection_score"], reverse=True)
#     return scored_topics

# ─── AFTER ────────────────────────────────────────────────────────
# def get_all_scores():
#     all_keys      = get_all_topic_keys()
#     scored_topics = [score_topic(k) for k in all_keys]
#
#     # ── ADD THIS: remove bigram noise before display ──────────────
#     #    Filters out "actually costs", "advice almost", etc.
#     #    Keeps real AI topics and multi-source signals.
#     scored_topics = filter_topics_batch(
#         scored_topics,
#         min_signal_count = 3,
#     )
#
#     scored_topics.sort(key=lambda x: x["detection_score"], reverse=True)
#     return scored_topics


# ════════════════════════════════════════════════════════════════
# EDIT 6 (OPTIONAL) — EXPOSE RESEARCH + VARIATIONS IN DETAIL ENDPOINT
# Location: the single-topic detail endpoint (/scores/{topic_key})
# These fields are already added by apply_ai_intelligence() — this
# just confirms they flow through to the API response.
# ════════════════════════════════════════════════════════════════

# ─── AFTER apply_ai_intelligence runs, result already contains: ────
#   result["ai_tier"]              → "tier_1" / "tier_2" / etc.
#   result["ai_tier_label"]        → "VIRAL — Maximum Lead Time"
#   result["ai_classification"]    → canonical display name
#   result["research"]             → { topic_age, what_to_do, what_to_watch, ... }
#   result["variations"]           → [ list of related topics with scores ]
#   result["score_explanation"]    → full plain-English explanation
#   result["calibration"]          → { maturity_class, maturity_badge, ... }
#   result["what_to_do_action"]    → "Act now" / "Monitor" / etc.
#   result["show_lead_time"]       → Boolean (false when inertia = 0)
#
# No endpoint changes needed — these flow through automatically since
# they are part of the result dict. The v2.0 frontend reads them directly.


# ════════════════════════════════════════════════════════════════
# VERIFICATION SCRIPT
# Run this after integration to confirm everything works
# ════════════════════════════════════════════════════════════════

def verify_integration(db_path=None):
    """
    Run after integration to confirm the calibration layer is working.
    Usage: python -c "from integration_patch import verify_integration; verify_integration()"
    """
    import os
    db_path = db_path or os.getenv("GAD_DB_PATH", "anomaly_detector.db")

    print("\n" + "="*64)
    print("NOW TRENDIN — INTEGRATION VERIFICATION")
    print("="*64)

    checks = []

    # Check 1: modules import
    try:
        from signal_calibration_integration import apply_calibration, get_topic_maturity_state
        from calibration_parameter_corrections import is_meaningful_topic, apply_signal_count_modifier
        from ai_topic_intelligence import apply_ai_intelligence, lookup_topic
        checks.append(("Module imports", True, "All four modules import cleanly"))
    except ImportError as e:
        checks.append(("Module imports", False, str(e)))
        # Cannot continue without imports
        for name, ok, detail in checks:
            print(f"  {'✓' if ok else '✗'} {name}: {detail}")
        return

    # Check 2: known topics seeded
    try:
        state = get_topic_maturity_state("ai_agent", db_path)
        is_established = state.get("maturity_class") == "ESTABLISHED"
        mult = state.get("calibration_multiplier")
        checks.append((
            "ai_agent classification",
            is_established and mult == 0.40,
            f"class={state.get('maturity_class')}, multiplier={mult}"
        ))
    except Exception as e:
        checks.append(("ai_agent classification", False, str(e)))

    # Check 3: AI taxonomy lookup
    try:
        result = lookup_topic("agentic coding")
        is_tier1 = result and result[0] == "tier_1"
        checks.append((
            "agentic coding → Tier 1",
            is_tier1,
            f"tier={result[0] if result else 'NOT FOUND'}"
        ))
    except Exception as e:
        checks.append(("agentic coding lookup", False, str(e)))

    # Check 4: noise filter
    try:
        keep_real  = is_meaningful_topic("agent memory", 5, 2)
        drop_noise = not is_meaningful_topic("actually costs", 3, 1)
        checks.append((
            "Noise filter",
            keep_real and drop_noise,
            f"keeps 'agent memory'={keep_real}, drops 'actually costs'={not drop_noise is False}"
        ))
    except Exception as e:
        checks.append(("Noise filter", False, str(e)))

    # Check 5: signal modifier produces variance
    try:
        g3  = apply_signal_count_modifier(80, 3, 1)
        g15 = apply_signal_count_modifier(80, 15, 3)
        has_variance = g15 > g3
        checks.append((
            "Signal count variance",
            has_variance,
            f"3 signals→{g3}, 15 signals→{g15}"
        ))
    except Exception as e:
        checks.append(("Signal count variance", False, str(e)))

    # Check 6: AI intelligence end-to-end
    try:
        test_result = {
            "topic_key": "agentic_coding",
            "topic_display": "agentic coding",
            "detection_score": 22,
            "confidence_score": 11,
            "total_signals": 20,
            "platform_count": 3,
            "inertia_score": 75,
            "times_scored": 8,
        }
        out = apply_ai_intelligence(test_result)
        scored_high = out["detection_score"] >= 88
        checks.append((
            "AI intelligence end-to-end",
            scored_high,
            f"agentic coding: DET {out['detection_score']}, "
            f"CONF {out['confidence_score']}, tier {out.get('ai_tier')}"
        ))
    except Exception as e:
        checks.append(("AI intelligence end-to-end", False, str(e)))

    # Print results
    print()
    all_pass = True
    for name, ok, detail in checks:
        symbol = "✓" if ok else "✗"
        print(f"  {symbol} {name}")
        print(f"      {detail}")
        if not ok:
            all_pass = False

    print("\n" + "="*64)
    if all_pass:
        print("  ✓ ALL CHECKS PASSED — calibration layer is correctly integrated")
        print("  Next: run 24h of continuous collection, then check the prototype")
    else:
        print("  ✗ SOME CHECKS FAILED — review the failures above")
        print("  Common fix: run 'python signal_calibration_integration.py --seed'")
    print("="*64 + "\n")


if __name__ == "__main__":
    verify_integration()
