"""
================================================================
NOW TRENDIN — SIGNAL CALIBRATION INTEGRATION LAYER
================================================================

PURPOSE:
  This file is the missing bridge between:
    calibration_engine.py   (the calibration logic — built)
    research_history.py     (the topic age lookup — built)
    gravitational_anomaly_detector.py (the live prototype — running)

  The prototype currently outputs RAW scores without calibration.
  This layer wraps every score output before it reaches the API
  and the frontend — correcting everything the screenshot showed
  was wrong for "ai agent":

  ┌─────────────────────────────────────────────────────────────┐
  │ ISSUE SEEN IN SCREENSHOT      → FIX IN THIS FILE            │
  ├─────────────────────────────────────────────────────────────┤
  │ Gradient 83 for "ai agent"    → Discounted to ~21 for       │
  │ (topic lives here permanently)  ESTABLISHED topics          │
  │                                                             │
  │ Anomaly fires on ratio alone  → Gate requires velocity OR   │
  │ (10x ratio = anomaly)           first-timer evidence too    │
  │                                                             │
  │ "Est. 2 days" with Inertia=0  → Lead time hidden until      │
  │ (false precision)               Inertia confirmed           │
  │                                                             │
  │ "14pt gap = high conviction"  → Directional label:          │
  │ (misleading — conviction of     "Both agree at WATCHING     │
  │  weak signal sounds strong)     level — unconfirmed"        │
  │                                                             │
  │ Inertia shows 0/0             → Shows "Pending — first      │
  │ (no explanation)                collection run"             │
  │                                                             │
  │ 7 components in flat list     → Grouped into 3 buckets:     │
  │ (cognitive overload)            Quality/Momentum/Context    │
  └─────────────────────────────────────────────────────────────┘

HOW TO INTEGRATE:
  In gravitational_anomaly_detector.py, find the score_topic()
  function and add at the end:

    from signal_calibration_integration import apply_calibration
    result = apply_calibration(result, db_path=DB_PATH)
    return result

  The calibrated result is a drop-in replacement — all existing
  fields are preserved and new calibration fields are added.

KNOWN TOPICS DATABASE:
  "ai agent", "llm", "gpt", and 60+ other established topics
  are pre-seeded so calibration works on day 1, not after
  30 days of history accumulation.

STANDALONE USE:
  python signal_calibration_integration.py --seed
  python signal_calibration_integration.py --analyse ai_agent
  python signal_calibration_integration.py --report
================================================================
"""

import os
import re
import json
import math
import sqlite3
import db_compat
import hashlib
import argparse
from datetime import datetime, timezone, timedelta
from typing import Optional

# ── Import the existing calibration engine ────────────────────────
# Handles all maturity classification, velocity calculation,
# anomaly gating, and communication text generation
try:
    from calibration_engine import (
        CalibrationEngine,
        TopicMaturityClassifier,
        compute_calibrated_gradient,
        evaluate_anomaly_gate,
        build_what_to_do,
        build_gap_interpretation,
        build_component_groups,
        init_calibration_db,
        INERTIA_ZERO_THRESHOLD,
    )
    CAL_ENGINE_AVAILABLE = True
except ImportError:
    CAL_ENGINE_AVAILABLE = False
    print("WARNING: calibration_engine.py not found. Running in passthrough mode.")

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

# ── Score-quarantine feature flag ────────────────────────────────────────────
# When True: None-aware component reads in apply_calibration — absent inputs
# are excluded from the weighted sum (weights renormalized over present
# components only) rather than defaulting to 0.0, which is indistinguishable
# from a genuine zero signal.
#
# DEFAULT = False. Production scores are unchanged until Phase 2 (Wikipedia
# + GDELT referee) validates the direction. Flip to "true" only after backtest.
SCORE_QUARANTINE_ENABLED = os.getenv("SCORE_QUARANTINE_ENABLED", "false").lower() == "true"

# rec F (2026-07-07, default OFF): stage keys off the calibrated DETECTION score
# (matching the UI's stageOf) instead of the det/conf average. Must agree with the
# detector's STAGE_FROM_DETECTION — both read the same env var.
_STAGE_FROM_DETECTION = os.getenv("STAGE_FROM_DETECTION", "0") == "1"


def _quarantine_weighted_sum(components: dict, weights: dict) -> float:
    """
    None-aware weighted average used when SCORE_QUARANTINE_ENABLED is True.
    Absent (None) components are excluded; weights are renormalized over the
    present subset so the sum of active weights still equals 1.0.
    Returns 0.0 when ALL components are absent (prevents division by zero).
    """
    active = {k: v for k, v in components.items() if v is not None}
    if not active:
        return 0.0
    total_w = sum(weights[k] for k in active)
    if total_w == 0:
        return 0.0
    return sum(active[k] * weights[k] / total_w for k in active)


# ════════════════════════════════════════════════════════════════
# KNOWN TOPICS SEED DATABASE
# Pre-loads established topic ages so calibration works immediately
# without needing 30 days of history accumulation.
#
# Format: topic_key → {
#   "display": human-readable name,
#   "established_since": approximate first discussion date (YYYY-MM-DD),
#   "domain": category,
#   "natural_gradient": expected expert-community concentration (%)
#   "note": why this is established
# }
#
# Sources: GitHub repo creation dates, HN first mention,
# Wikipedia article creation dates, well-known industry timelines.
# ════════════════════════════════════════════════════════════════

KNOWN_TOPICS: dict = {

    # ── AI Agents & Agentic AI ─────────────────────────────────────
    "ai_agent": {
        "display": "ai agent",
        "established_since": "2018-01-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 85,
        "note": "In expert ML communities since ~2018. AutoGPT surge 2023 — now settled.",
    },
    "ai_agents": {
        "display": "ai agents",
        "established_since": "2018-01-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 85,
        "note": "Plural form — same established timeline as 'ai agent'.",
    },
    "autonomous_agent": {
        "display": "autonomous agent",
        "established_since": "2017-06-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 88,
        "note": "Academic term, predates modern LLM era.",
    },
    "agentic": {
        "display": "agentic",
        "established_since": "2023-01-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 80,
        "note": "Emerged post-GPT-4, now stable in expert communities.",
    },
    "agentic_coding": {
        "display": "agentic coding",
        "established_since": "2024-01-01",
        "domain": "developer_tooling",
        "natural_gradient": 90,
        "note": "Developer-specific term, high gradient reflects domain.",
    },

    # ── Large Language Models ─────────────────────────────────────
    "llm": {
        "display": "llm",
        "established_since": "2020-01-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 92,
        "note": "Term standardised ~2020. Permanently in expert communities.",
    },
    "large_language_model": {
        "display": "large language model",
        "established_since": "2018-06-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 90,
        "note": "Google 'Attention Is All You Need' paper 2017 → term widespread 2018.",
    },
    "foundation_model": {
        "display": "foundation model",
        "established_since": "2021-08-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 88,
        "note": "Stanford HAI paper August 2021 coined the term.",
    },
    "gpt": {
        "display": "gpt",
        "established_since": "2018-06-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 75,
        "note": "GPT-1 June 2018. Expert term but now mainstream too → lower gradient.",
    },
    "transformer": {
        "display": "transformer",
        "established_since": "2017-06-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 92,
        "note": "Vaswani et al. 2017. Pure expert term.",
    },
    "fine_tuning": {
        "display": "fine tuning",
        "established_since": "2018-01-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 90,
        "note": "Expert ML technique, stable for 5+ years.",
    },
    "rag": {
        "display": "rag",
        "established_since": "2020-04-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 88,
        "note": "Lewis et al. RAG paper April 2020. Expert-only acronym.",
    },
    "retrieval_augmented": {
        "display": "retrieval augmented",
        "established_since": "2020-04-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 88,
        "note": "Same as RAG — full form.",
    },
    "embedding": {
        "display": "embedding",
        "established_since": "2013-01-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 94,
        "note": "Word2Vec 2013. Fundamental ML concept — permanently expert.",
    },
    "embeddings": {
        "display": "embeddings",
        "established_since": "2013-01-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 94,
        "note": "Plural form of embedding.",
    },
    "vector_database": {
        "display": "vector database",
        "established_since": "2021-01-01",
        "domain": "developer_tooling",
        "natural_gradient": 90,
        "note": "Pinecone launched 2021. Expert infrastructure term.",
    },

    # ── Specific Models ───────────────────────────────────────────
    "claude": {
        "display": "claude",
        "established_since": "2023-03-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 78,
        "note": "Anthropic Claude public launch March 2023. Expert + broad audience.",
    },
    "llama": {
        "display": "llama",
        "established_since": "2023-02-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 85,
        "note": "Meta LLaMA February 2023. Primarily developer community.",
    },
    "gemini": {
        "display": "gemini",
        "established_since": "2023-12-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 70,
        "note": "Google Gemini December 2023. Mixed expert/mainstream.",
    },
    "mistral": {
        "display": "mistral",
        "established_since": "2023-09-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 88,
        "note": "Mistral AI September 2023. Expert community.",
    },
    "deepseek": {
        "display": "deepseek",
        "established_since": "2024-01-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 82,
        "note": "DeepSeek V1 late 2023. Surge in January 2025.",
    },
    "openai": {
        "display": "openai",
        "established_since": "2015-12-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 55,
        "note": "OpenAI founded December 2015. Now mainstream — low gradient expected.",
    },

    # ── Infrastructure & Tools ────────────────────────────────────
    "mcp": {
        "display": "mcp",
        "established_since": "2024-11-01",
        "domain": "developer_tooling",
        "natural_gradient": 92,
        "note": "Anthropic Model Context Protocol November 2024. NEW — calibrate cautiously.",
    },
    "model_context_protocol": {
        "display": "model context protocol",
        "established_since": "2024-11-01",
        "domain": "developer_tooling",
        "natural_gradient": 92,
        "note": "Full form of MCP. Same timeline.",
    },
    "vllm": {
        "display": "vllm",
        "established_since": "2023-06-01",
        "domain": "developer_tooling",
        "natural_gradient": 93,
        "note": "vLLM GitHub June 2023. Pure developer infrastructure term.",
    },
    "ollama": {
        "display": "ollama",
        "established_since": "2023-07-01",
        "domain": "developer_tooling",
        "natural_gradient": 90,
        "note": "Ollama July 2023. Local LLM serving — developer tool.",
    },
    "local_llm": {
        "display": "local llm",
        "established_since": "2023-03-01",
        "domain": "developer_tooling",
        "natural_gradient": 90,
        "note": "Emerged post LLaMA leak March 2023.",
    },
    "pytorch": {
        "display": "pytorch",
        "established_since": "2016-09-01",
        "domain": "developer_tooling",
        "natural_gradient": 95,
        "note": "Facebook September 2016. Permanently in ML developer spaces.",
    },
    "hugging_face": {
        "display": "hugging face",
        "established_since": "2019-01-01",
        "domain": "developer_tooling",
        "natural_gradient": 90,
        "note": "HuggingFace pivot to models 2019. Expert ML community mainstay.",
    },
    "cursor": {
        "display": "cursor",
        "established_since": "2023-03-01",
        "domain": "developer_tooling",
        "natural_gradient": 85,
        "note": "Cursor AI IDE March 2023. Developer-only — high gradient natural.",
    },

    # ── Techniques ────────────────────────────────────────────────
    "prompt_engineering": {
        "display": "prompt engineering",
        "established_since": "2021-06-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 80,
        "note": "Term went mainstream 2022 — gradient now lower than pure expert terms.",
    },
    "chain_of_thought": {
        "display": "chain of thought",
        "established_since": "2022-01-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 88,
        "note": "Wei et al. January 2022. Still primarily expert term.",
    },
    "context_window": {
        "display": "context window",
        "established_since": "2021-01-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 85,
        "note": "Expert ML term, now crossing to informed mainstream.",
    },
    "quantization": {
        "display": "quantization",
        "established_since": "2019-01-01",
        "domain": "developer_tooling",
        "natural_gradient": 95,
        "note": "Pure ML engineering term. Permanently in expert spaces.",
    },
    "lora": {
        "display": "lora",
        "established_since": "2021-10-01",
        "domain": "developer_tooling",
        "natural_gradient": 92,
        "note": "LoRA paper October 2021. Expert fine-tuning technique.",
    },
    "mixture_of_experts": {
        "display": "mixture of experts",
        "established_since": "1991-01-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 92,
        "note": "Academic term from 1991. Re-emerged with GPT-4 MoE speculation.",
    },
    "speculative_decoding": {
        "display": "speculative decoding",
        "established_since": "2022-11-01",
        "domain": "developer_tooling",
        "natural_gradient": 95,
        "note": "Inference optimization technique. Purely expert term.",
    },
    "multimodal": {
        "display": "multimodal",
        "established_since": "2021-01-01",
        "domain": "ai_consumer_tech",
        "natural_gradient": 85,
        "note": "Academic term now crossing to informed mainstream.",
    },

    # ── Consumer AI ───────────────────────────────────────────────
    "chatgpt": {
        "display": "chatgpt",
        "established_since": "2022-11-30",
        "domain": "mainstream_consumer",
        "natural_gradient": 30,
        "note": "ChatGPT November 2022. Mainstream consumer product — LOW gradient expected.",
    },
    "artificial_intelligence": {
        "display": "artificial intelligence",
        "established_since": "1956-01-01",
        "domain": "mainstream_consumer",
        "natural_gradient": 20,
        "note": "Academic term from 1956. Now mainstream — very low gradient expected.",
    },
    "machine_learning": {
        "display": "machine learning",
        "established_since": "1959-01-01",
        "domain": "mainstream_consumer",
        "natural_gradient": 60,
        "note": "Term from 1959. Now split expert/mainstream.",
    },
    "generative_ai": {
        "display": "generative ai",
        "established_since": "2022-01-01",
        "domain": "mainstream_consumer",
        "natural_gradient": 45,
        "note": "Went mainstream 2022. Lower gradient than pure expert terms.",
    },

    # ── Vibe Coding (genuinely new) ───────────────────────────────
    "vibe_coding": {
        "display": "vibe coding",
        "established_since": "2025-02-01",
        "domain": "developer_tooling",
        "natural_gradient": 92,
        "note": "Term coined by Andrej Karpathy February 2025. GENUINELY NEW.",
    },
    "vibecoding": {
        "display": "vibecoding",
        "established_since": "2025-02-01",
        "domain": "developer_tooling",
        "natural_gradient": 92,
        "note": "Alternative spelling — same timeline.",
    },

    # ── Programming & DevOps ──────────────────────────────────────
    "python": {
        "display": "python",
        "established_since": "1991-02-01",
        "domain": "developer_tooling",
        "natural_gradient": 88,
        "note": "Created 1991. Developer community staple — gradient is natural.",
    },
    "javascript": {
        "display": "javascript",
        "established_since": "1995-12-01",
        "domain": "developer_tooling",
        "natural_gradient": 82,
        "note": "1995. Developer community constant — gradient is natural.",
    },
    "typescript": {
        "display": "typescript",
        "established_since": "2012-10-01",
        "domain": "developer_tooling",
        "natural_gradient": 88,
        "note": "Microsoft October 2012. Developer community term.",
    },
    "open_source": {
        "display": "open source",
        "established_since": "1998-02-01",
        "domain": "developer_tooling",
        "natural_gradient": 80,
        "note": "Term coined 1998. Developer mainstay.",
    },
}

# ── Compute years established from known date ─────────────────────
def _years_established(established_since: str) -> float:
    try:
        since = datetime.strptime(established_since, "%Y-%m-%d")
        delta = datetime.now() - since
        return round(delta.days / 365.25, 1)
    except Exception:
        return 0.0


# ════════════════════════════════════════════════════════════════
# KNOWN TOPICS SEEDER
# Call once to pre-populate the topic_maturity table
# so calibration works on day 1 without 30 days of history
# ════════════════════════════════════════════════════════════════

def seed_known_topics(db_path: str = DB_PATH) -> int:
    """
    Pre-populate topic_maturity for all known established topics.

    This solves the cold-start problem: when the detector first
    sees "ai agent", it has 0 days of history. Without seeding,
    it would be classified as NEW for 30 days before being
    correctly classified as ESTABLISHED.

    With seeding, the correct classification is immediate.

    Run once after database initialisation:
      python signal_calibration_integration.py --seed
    """
    # Ensure calibration tables exist
    init_calibration_db(db_path)

    conn = db_compat.connect(db_path)
    conn.row_factory = sqlite3.Row

    count = 0
    now   = datetime.now(timezone.utc).isoformat()

    for topic_key, info in KNOWN_TOPICS.items():
        established_since = info["established_since"]
        years             = _years_established(established_since)
        days_in_system    = int(years * 365.25)
        natural_gradient  = info["natural_gradient"]

        # Determine maturity class based on age and natural gradient
        if years >= 2.0:
            maturity_class = "ESTABLISHED"
            calibration_multiplier = 0.40
            maturity_reason = (
                f"{info['note']} Established for {years:.1f} years. "
                f"Natural expert-community gradient: {natural_gradient}%. "
                "High gradient reflects permanent expert-home, NOT emergence."
            )
        elif years >= 0.5:
            maturity_class = "MONITORING"
            calibration_multiplier = 0.60
            maturity_reason = (
                f"{info['note']} In system {years:.1f} years. "
                "Calibration building — monitoring for velocity signals."
            )
        else:
            maturity_class = "NEW"
            calibration_multiplier = 0.80
            maturity_reason = (
                f"{info['note']} Recent emergence ({years:.1f} years old). "
                "Gradient taken cautiously — baseline still building."
            )

        # Set a synthetic first_detected_at based on established_since
        # (capped at DB deployment date to be honest)
        first_detected = (
            datetime.now(timezone.utc) - timedelta(days=min(days_in_system, 730))
        ).isoformat()

        conn.execute("""
            INSERT INTO topic_maturity (
                topic_key, topic_display,
                first_detected_at, last_scored_at,
                times_scored, days_in_system,
                maturity_class, maturity_reason,
                baseline_gradient, baseline_overall,
                baseline_detection, baseline_confidence,
                gradient_velocity, score_velocity, velocity_trend,
                calibration_multiplier, anomaly_gate_passed,
                updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(topic_key) DO UPDATE SET
                topic_display=EXCLUDED.topic_display,
                first_detected_at=EXCLUDED.first_detected_at,
                last_scored_at=EXCLUDED.last_scored_at,
                times_scored=EXCLUDED.times_scored,
                days_in_system=EXCLUDED.days_in_system,
                maturity_class=EXCLUDED.maturity_class,
                maturity_reason=EXCLUDED.maturity_reason,
                baseline_gradient=EXCLUDED.baseline_gradient,
                baseline_overall=EXCLUDED.baseline_overall,
                baseline_detection=EXCLUDED.baseline_detection,
                baseline_confidence=EXCLUDED.baseline_confidence,
                gradient_velocity=EXCLUDED.gradient_velocity,
                score_velocity=EXCLUDED.score_velocity,
                velocity_trend=EXCLUDED.velocity_trend,
                calibration_multiplier=EXCLUDED.calibration_multiplier,
                anomaly_gate_passed=EXCLUDED.anomaly_gate_passed,
                updated_at=EXCLUDED.updated_at
        """, (
            topic_key,
            info["display"],
            first_detected,
            now,
            # times_scored: synthetic — enough to satisfy ESTABLISHED threshold
            max(10, min(50, int(years * 12))),
            days_in_system,
            maturity_class,
            maturity_reason,
            # baseline_gradient: set to natural_gradient
            float(natural_gradient),
            # baseline_overall: estimate based on natural gradient
            round(natural_gradient * 0.55, 1),
            round(natural_gradient * 0.60, 1),
            round(natural_gradient * 0.40, 1),
            # gradient_velocity: 0 (stable — no data yet)
            0.0,
            0.0,
            "stable",
            calibration_multiplier,
            0,  # anomaly_gate_passed = False by default for established
            now,
        ))
        count += 1

    conn.commit()
    conn.close()
    print(f"Seeded {count} known topics into topic_maturity table.")
    print("Established topics will now be correctly calibrated immediately.")
    return count


# ════════════════════════════════════════════════════════════════
# TOPIC KEY NORMALISER
# Matches incoming topic strings to known_topics keys
# ════════════════════════════════════════════════════════════════

def _normalise_key(topic: str) -> str:
    """Normalise a topic string to a known_topics lookup key."""
    key = topic.lower().strip()
    key = re.sub(r'[^\w\s]', '', key)
    key = re.sub(r'\s+', '_', key)
    return key[:80]


def _lookup_known_topic(topic_key: str) -> Optional[dict]:
    """
    Return known topic info if this topic is in our knowledge base.
    Handles minor key variations.
    """
    # Direct lookup
    if topic_key in KNOWN_TOPICS:
        return KNOWN_TOPICS[topic_key]

    # Try normalised version
    normalised = _normalise_key(topic_key)
    if normalised in KNOWN_TOPICS:
        return KNOWN_TOPICS[normalised]

    # Partial match — find if any known key is contained in topic_key
    for known_key, info in KNOWN_TOPICS.items():
        if known_key in topic_key or topic_key in known_key:
            return info

    return None


# ════════════════════════════════════════════════════════════════
# CALIBRATION STATE READER
# Gets current maturity for a topic from DB (or knowledge base)
# ════════════════════════════════════════════════════════════════

def get_topic_maturity_state(
    topic_key: str,
    db_path: str = DB_PATH,
) -> dict:
    """
    Returns the calibration state for a topic.
    Priority:
      1. Database topic_maturity record (has history/velocity)
      2. KNOWN_TOPICS knowledge base (correct on day 1)
      3. Default NEW state (first time we've seen it)
    """
    conn = db_compat.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        row = conn.execute("""
            SELECT * FROM topic_maturity WHERE topic_key = ?
        """, (topic_key,)).fetchone()
    except sqlite3.OperationalError:
        row = None
    finally:
        conn.close()

    if row:
        return {
            "source":                "database",
            "maturity_class":        row["maturity_class"],
            "maturity_reason":       row["maturity_reason"],
            "calibration_multiplier": row["calibration_multiplier"],
            "anomaly_gate_passed":   bool(row["anomaly_gate_passed"]),
            "days_in_system":        row["days_in_system"],
            "times_scored":          row["times_scored"],
            "gradient_velocity":     row["gradient_velocity"],
            "score_velocity":        row["score_velocity"],
            "baseline_gradient":     row["baseline_gradient"],
            "baseline_overall":      row["baseline_overall"],
            "velocity_trend":        row["velocity_trend"],
        }

    # Fall back to knowledge base
    known = _lookup_known_topic(topic_key)
    if known:
        years = _years_established(known["established_since"])
        if years >= 2.0:
            return {
                "source":                "knowledge_base",
                "maturity_class":        "ESTABLISHED",
                "maturity_reason":       known["note"] + f" In expert communities {years:.1f} years.",
                "calibration_multiplier": 0.25,
                "anomaly_gate_passed":   False,
                "days_in_system":        int(years * 365.25),
                "times_scored":          0,
                "gradient_velocity":     None,
                "score_velocity":        None,
                "baseline_gradient":     float(known["natural_gradient"]),
                "baseline_overall":      None,
                "velocity_trend":        "unknown",
            }
        elif years >= 0.5:
            return {
                "source":                "knowledge_base",
                "maturity_class":        "MONITORING",
                "maturity_reason":       known["note"],
                "calibration_multiplier": 0.55,
                "anomaly_gate_passed":   False,
                "days_in_system":        int(years * 365.25),
                "times_scored":          0,
                "gradient_velocity":     None,
                "score_velocity":        None,
                "baseline_gradient":     float(known["natural_gradient"]),
                "baseline_overall":      None,
                "velocity_trend":        "unknown",
            }

    # ── Lifecycle fallback ────────────────────────────────────────
    # The topic_maturity table is only seeded for ~48 known topics, but the live
    # pipeline maintains topic_lifecycle for EVERY topic (total_scoring_cycles +
    # first_detected_at). Without this fallback every un-seeded topic defaulted to
    # NEW / "first detection" forever — even after hundreds of cycles. Derive real
    # maturity from the maintained lifecycle counters. Self-contained: no
    # dependency on the (also-dormant) baseline-history table.
    try:
        lc_conn = db_compat.connect(db_path)
        lc_conn.row_factory = sqlite3.Row
        lc = lc_conn.execute(
            "SELECT total_scoring_cycles, first_detected_at FROM topic_lifecycle "
            "WHERE topic_key = ?", (topic_key,)).fetchone()
        lc_conn.close()
    except Exception:
        lc = None
    if lc:
        cycles = int(lc["total_scoring_cycles"] or 0)
        days = 0
        fda = lc["first_detected_at"]
        if fda:
            try:
                from datetime import datetime as _dt, timezone as _tz
                _first = _dt.fromisoformat(str(fda).replace("Z", "+00:00"))
                days = max(0, (_dt.now(_tz.utc) - _first).days)
            except Exception:
                days = 0
        if cycles < 5 or days < 1:
            _cls, _mult, _reason = "NEW", 0.80, (
                f"First cycles scored ({cycles} cycle(s), {days} day(s)) — the gradient is "
                "still stabilizing and not yet calibrated against a baseline.")
        elif days >= 10 and cycles >= 40:
            # 0.45 matches the calibration engine's stable-ESTABLISHED multiplier so
            # the explanation branch (which requires <=0.45) renders the correct
            # "permanent home" text instead of the MONITORING fallback.
            _cls, _mult, _reason = "ESTABLISHED", 0.45, (
                f"Long-running topic — {days} days in system across {cycles} scoring cycles. "
                "High gradient reflects a permanent expert/attention base, not a new surge, so "
                "the score is discounted to avoid over-reading an old topic as breaking news.")
        else:
            _cls, _mult, _reason = "EMERGING", 0.85, (
                f"Gaining across cycles ({cycles} cycles over {days} day(s)) — momentum is "
                "forming and calibration is still building confidence; not yet a permanent base.")
        return {
            "source":                "lifecycle",
            "maturity_class":        _cls,
            "maturity_reason":       _reason,
            "calibration_multiplier": _mult,
            "anomaly_gate_passed":   False,
            "days_in_system":        days,
            "times_scored":          cycles,
            "gradient_velocity":     None,
            "score_velocity":        None,
            "baseline_gradient":     None,
            "baseline_overall":      None,
            "velocity_trend":        "unknown",
        }

    # True new topic — no prior knowledge
    return {
        "source":                "default",
        "maturity_class":        "NEW",
        "maturity_reason":       "First time this topic has been detected.",
        "calibration_multiplier": 0.75,
        "anomaly_gate_passed":   False,
        "days_in_system":        0,
        "times_scored":          0,
        "gradient_velocity":     None,
        "score_velocity":        None,
        "baseline_gradient":     None,
        "baseline_overall":      None,
        "velocity_trend":        "unknown",
    }


# ════════════════════════════════════════════════════════════════
# SCORE HISTORY RECORDER
# Call after every scoring cycle to build the baseline over time
# ════════════════════════════════════════════════════════════════

def record_score_history(
    topic_key: str,
    topic_display: str,
    raw_gradient: float,
    calibrated_gradient: float,
    overall_score: float,
    detection_score: float,
    confidence_score: float,
    inertia_score: float,
    platform_count: int,
    total_mentions: int,
    maturity_class: str,
    db_path: str = DB_PATH,
) -> None:
    """
    Record every score in topic_score_history for baseline building.
    Also updates topic_maturity with latest values.

    Call this AFTER apply_calibration() on every scoring cycle.
    """
    now  = datetime.now(timezone.utc)
    now_str = now.isoformat()
    date_str = now.strftime("%Y-%m-%d")
    rec_id = hashlib.md5(
        f"{topic_key}-{now_str}".encode()
    ).hexdigest()[:16]

    conn = db_compat.connect(db_path)

    try:
        # Insert score history record
        conn.execute("""
            INSERT OR IGNORE INTO topic_score_history VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            rec_id, topic_key, now_str,
            overall_score, detection_score, confidence_score,
            raw_gradient, calibrated_gradient,
            inertia_score, platform_count, total_mentions,
            maturity_class,
        ))

        # Upsert daily baseline snapshot (average for today)
        conn.execute("""
            INSERT INTO topic_baselines
                (topic_key, snapshot_date, avg_gradient, avg_overall,
                 avg_detection, avg_confidence, signal_count)
            VALUES (?,?,?,?,?,?,1)
            ON CONFLICT(topic_key, snapshot_date) DO UPDATE SET
                avg_gradient   = (topic_baselines.avg_gradient   * topic_baselines.signal_count + ?) / (topic_baselines.signal_count + 1),
                avg_overall    = (topic_baselines.avg_overall    * topic_baselines.signal_count + ?) / (topic_baselines.signal_count + 1),
                avg_detection  = (topic_baselines.avg_detection  * topic_baselines.signal_count + ?) / (topic_baselines.signal_count + 1),
                avg_confidence = (topic_baselines.avg_confidence * topic_baselines.signal_count + ?) / (topic_baselines.signal_count + 1),
                signal_count   = topic_baselines.signal_count + 1
        """, (
            topic_key, date_str,
            calibrated_gradient, overall_score, detection_score, confidence_score,
            calibrated_gradient, overall_score, detection_score, confidence_score,
        ))

        # Update topic_maturity last_scored_at and times_scored
        existing = conn.execute(
            "SELECT times_scored, first_detected_at FROM topic_maturity WHERE topic_key = ?",
            (topic_key,)
        ).fetchone()

        if existing:
            conn.execute("""
                UPDATE topic_maturity
                SET last_scored_at = ?,
                    times_scored   = times_scored + 1,
                    updated_at     = ?
                WHERE topic_key = ?
            """, (now_str, now_str, topic_key))
        else:
            conn.execute("""
                INSERT INTO topic_maturity
                    (topic_key, topic_display, first_detected_at, last_scored_at,
                     times_scored, maturity_class, updated_at)
                VALUES (?,?,?,?,1,?,?)
            """, (topic_key, topic_display, now_str, now_str, maturity_class, now_str))

        conn.commit()
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════
# VELOCITY UPDATER
# Recomputes gradient velocity for all topics with enough history
# Run every 24 hours (Heroku Scheduler daily job)
# ════════════════════════════════════════════════════════════════

def recompute_velocities(db_path: str = DB_PATH) -> int:
    """
    For every topic with 5+ days of baseline data:
      1. Compute rolling 14-day avg gradient
      2. Compare to last 3 days avg gradient
      3. Update gradient_velocity in topic_maturity
      4. Re-classify maturity if velocity crosses a threshold

    This is what makes "ai agent" correctly RESURGENT if a new
    breakthrough causes it to actually accelerate above its baseline.
    """
    conn = db_compat.connect(db_path)
    conn.row_factory = sqlite3.Row
    updated = 0

    topics = conn.execute(
        "SELECT DISTINCT topic_key FROM topic_baselines"
    ).fetchall()

    for row in topics:
        topic_key = row["topic_key"]

        # 14-day baseline window
        cutoff_14 = (
            datetime.now(timezone.utc) - timedelta(days=14)
        ).strftime("%Y-%m-%d")
        cutoff_3  = (
            datetime.now(timezone.utc) - timedelta(days=3)
        ).strftime("%Y-%m-%d")

        baseline_rows = conn.execute("""
            SELECT avg_gradient, avg_overall FROM topic_baselines
            WHERE topic_key = ? AND snapshot_date >= ? AND snapshot_date < ?
            ORDER BY snapshot_date DESC
        """, (topic_key, cutoff_14, cutoff_3)).fetchall()

        recent_rows = conn.execute("""
            SELECT avg_gradient, avg_overall FROM topic_baselines
            WHERE topic_key = ? AND snapshot_date >= ?
            ORDER BY snapshot_date DESC
        """, (topic_key, cutoff_3)).fetchall()

        if not baseline_rows or not recent_rows:
            continue

        baseline_grads = [r["avg_gradient"] for r in baseline_rows if r["avg_gradient"]]
        recent_grads   = [r["avg_gradient"] for r in recent_rows   if r["avg_gradient"]]

        if not baseline_grads or not recent_grads:
            continue

        import statistics as _stats
        baseline_avg = _stats.mean(baseline_grads)
        recent_avg   = _stats.mean(recent_grads)
        velocity     = round(recent_avg - baseline_avg, 2)

        # Determine velocity trend
        if velocity > 15:
            trend = "rising"
        elif velocity < -15:
            trend = "falling"
        else:
            trend = "stable"

        # Re-classify if velocity crosses thresholds
        maturity_row = conn.execute(
            "SELECT maturity_class, days_in_system, times_scored FROM topic_maturity WHERE topic_key = ?",
            (topic_key,)
        ).fetchone()

        if maturity_row:
            current_class = maturity_row["maturity_class"]
            days          = maturity_row["days_in_system"]
            times_scored  = maturity_row["times_scored"]

            new_class = current_class
            reason    = ""

            if current_class == "ESTABLISHED":
                if velocity >= 15:
                    new_class = "RESURGENT"
                    reason    = (
                        f"Velocity +{velocity:.0f}pts above 14-day baseline. "
                        "Established topic showing renewed acceleration."
                    )
                elif velocity <= -15:
                    new_class = "MONITORING"
                    reason    = f"Declining velocity {velocity:.0f}pts. Interest fading."

            elif current_class == "RESURGENT":
                if velocity < 10:
                    new_class = "ESTABLISHED"
                    reason    = "Velocity returned to baseline. Resurgence cooling."

            elif current_class == "NEW" and days >= 30 and times_scored >= 5:
                if velocity > 20:
                    new_class = "EMERGING"
                    reason    = f"Emerging: +{velocity:.0f}pts velocity with growing history."
                else:
                    new_class = "ESTABLISHED"
                    reason    = f"Graduated from NEW → ESTABLISHED after 30+ days."

            conn.execute("""
                UPDATE topic_maturity
                SET gradient_velocity = ?,
                    velocity_trend     = ?,
                    maturity_class     = ?,
                    maturity_reason    = CASE WHEN ? != '' THEN ? ELSE maturity_reason END,
                    calibration_multiplier = CASE
                        WHEN ? = 'RESURGENT'  THEN 1.2
                        WHEN ? = 'EMERGING'   THEN 1.0
                        WHEN ? = 'ESTABLISHED' THEN 0.40
                        WHEN ? = 'MONITORING' THEN 0.60
                        ELSE 0.80
                    END,
                    updated_at = ?
                WHERE topic_key = ?
            """, (
                velocity, trend, new_class,
                reason, reason,
                new_class, new_class, new_class, new_class,
                datetime.now(timezone.utc).isoformat(),
                topic_key,
            ))
            updated += 1

    conn.commit()
    conn.close()
    return updated


# ════════════════════════════════════════════════════════════════
# MAIN CALIBRATION APPLIER
# The function to call after every score_topic() call in the detector
# ════════════════════════════════════════════════════════════════

def apply_calibration(
    raw_result: dict,
    db_path: str = DB_PATH,
) -> dict:
    """
    Apply full calibration to a raw score result from the detector.

    INPUT:  raw_result dict from score_topic() in gravitational_anomaly_detector.py
    OUTPUT: calibrated_result dict — drop-in replacement with corrections

    WHAT THIS CHANGES:
      - gradient_strength_detection and _confidence: calibrated versions
      - is_anomaly: re-evaluated with maturity-aware gate
      - anomaly_label: more specific (NEW/EMERGING/RESURGENT/gradient-only)
      - what_to_do: maturity-aware action recommendation
      - gap_interpretation: directional, not size-only
      - component_groups: 3 grouped buckets instead of 7 flat rows
      - lead_time_estimate: hidden when Inertia = 0
      - show_lead_time: boolean gate for frontend
    """
    if not raw_result:
        return raw_result

    topic_key = raw_result.get("topic_key", "")

    # ── Get maturity state ────────────────────────────────────────
    maturity = get_topic_maturity_state(topic_key, db_path)

    # ── Extract raw scores ────────────────────────────────────────
    raw_gradient    = raw_result.get("gradient_strength_detection", 0) or 0
    raw_gradient_c  = raw_result.get("gradient_strength_confidence", raw_gradient) or 0
    gradient_ratio  = raw_result.get("gradient_ratio", 1.0) or 1.0
    inertia         = raw_result.get("inertia_score", 0) or 0
    platform_count  = raw_result.get("platform_count", 0) or 0
    detection_score = raw_result.get("detection_score", 0) or 0
    confidence_score= raw_result.get("confidence_score", 0) or 0
    overall_score   = raw_result.get("overall_score", 0) or 0
    ft_ratio        = raw_result.get("first_timer_ratio", 0.0) or 0.0
    # KEY-DRIFT fix: the scorer writes the producer key "engagement_asymmetry" (int 1/0);
    # the "_detected" alias only exists on the serve path. Read the real key with the
    # serve alias as fallback (matches calibration_engine.py) so engagement-asymmetry
    # evidence is live in the scoring-time anomaly gate instead of silently False.
    asymmetry       = bool(raw_result.get("engagement_asymmetry_detected",
                                          raw_result.get("engagement_asymmetry", False)))
    stage           = raw_result.get("signal_stage", "MONITORING")
    # Prefer the authoritative lifecycle cycle count — the topic_maturity record's
    # own counter can lag at 0 even after several scoring cycles, which would
    # mislabel an established topic as "first collection".
    times_scored    = max(
        int(maturity.get("times_scored", 0) or 0),
        int(raw_result.get("total_scoring_cycles", 0) or 0),
        # The scorer surfaces the real cycle count (from stored history) here.
        int(raw_result.get("momentum_cycle_count", 0) or 0),
        int(raw_result.get("persistence_cycles", 0) or 0),
    )
    # "First run" must mean genuinely first — NOT merely flat inertia (a multi-
    # cycle topic with flat momentum is messaged separately, not "first collection").
    is_first_run    = (times_scored <= 1)

    # ── Calibrate gradient ────────────────────────────────────────
    if CAL_ENGINE_AVAILABLE:
        cal_gradient_d, cal_factor_d, cal_note_d = compute_calibrated_gradient(
            raw_gradient, gradient_ratio, maturity
        )
        cal_gradient_c, cal_factor_c, cal_note_c = compute_calibrated_gradient(
            raw_gradient_c, gradient_ratio, maturity
        )
    else:
        # Fallback: apply multiplier directly if engine not imported
        mult = maturity.get("calibration_multiplier", 1.0)
        cal_gradient_d = round(min(100, raw_gradient * mult), 1)
        cal_gradient_c = round(min(100, raw_gradient_c * mult), 1)
        cal_factor_d = cal_factor_c = mult
        cal_note_d = cal_note_c = f"Calibration multiplier: {mult}"

    # ── Recompute overall scores with calibrated gradient ─────────
    # Uses same formula weights as the detector:
    # Detection:   G(0.40) + D(0.25) + I(0.20) + M(0.10) + C(0.05)
    # Confidence:  I(0.35) + M(0.30) + G(0.20) + C(0.10) + D(0.05)
    inertia_d  = raw_result.get("inertia_detection", inertia)
    inertia_c  = raw_result.get("inertia_confidence", inertia)
    # These mode-specific fields (..._detection/..._confidence) are not stored as
    # separate columns — the engine persists one value per component. Fall back to
    # the actual stored column so Platform Diversity, Dark Matter and Confidence
    # Decay aren't silently zeroed in the serve recompute AND the breakdown display.
    # Raw component reads. When SCORE_QUARANTINE_ENABLED=True, None (absent data)
    # is preserved so _quarantine_weighted_sum can renormalize over present inputs.
    # When False (default/production): or-0 collapses None → 0.0 (current behavior).
    if SCORE_QUARANTINE_ENABLED:
        _platform  = raw_result.get("platform_diversity")
        _dark      = raw_result.get("dark_matter_score")
        _decay     = raw_result.get("confidence_decay")
        platform_d = raw_result.get("platform_diversity_detection", _platform)
        platform_c = raw_result.get("platform_diversity_confidence", _platform)
        dark_d     = raw_result.get("dark_matter_detection", _dark)
        dark_c     = raw_result.get("dark_matter_confidence", _dark)
        decay_d    = raw_result.get("confidence_decay_detection", _decay)
        decay_c    = raw_result.get("confidence_decay_confidence", _decay)
        _persist   = raw_result.get("persistence_score")
    else:
        _platform  = raw_result.get("platform_diversity", 0) or 0
        _dark      = raw_result.get("dark_matter_score", 0) or 0
        _decay     = raw_result.get("confidence_decay", 0) or 0
        platform_d = raw_result.get("platform_diversity_detection", _platform) or 0
        platform_c = raw_result.get("platform_diversity_confidence", _platform) or 0
        dark_d     = raw_result.get("dark_matter_detection", _dark) or 0
        dark_c     = raw_result.get("dark_matter_confidence", _dark) or 0
        decay_d    = raw_result.get("confidence_decay_detection", _decay) or 0
        decay_c    = raw_result.get("confidence_decay_confidence", _decay) or 0
        _persist   = raw_result.get("persistence_score", 0) or 0

    # 6-component external weights (N excluded by design; renormalized to 1.0).
    # Matches the authoritative scoring formula in gravitational_anomaly_detector.
    try:
        from scoring_weights import WEIGHTS_DETECTION as _WD, WEIGHTS_CONFIDENCE as _WC
    except ImportError:
        _WD = {"G": .375, "D": .216, "I": .182, "M": .102, "C": .057, "P": .068}
        _WC = {"I": .278, "P": .267, "M": .222, "G": .122, "C": .067, "D": .044}

    if SCORE_QUARANTINE_ENABLED:
        det_comps  = {"G": cal_gradient_d, "D": dark_d,  "I": inertia_d,
                      "M": platform_d,     "C": decay_d,  "P": _persist}
        conf_comps = {"G": cal_gradient_c, "D": dark_c,  "I": inertia_c,
                      "M": platform_c,     "C": decay_c,  "P": _persist}
        new_detection  = round(min(100, _quarantine_weighted_sum(det_comps,  _WD)), 1)
        new_confidence = round(min(100, _quarantine_weighted_sum(conf_comps, _WC)), 1)
    else:
        new_detection = round(
            cal_gradient_d * 0.375 +
            dark_d         * 0.216 +
            inertia_d      * 0.182 +
            platform_d     * 0.102 +
            decay_d        * 0.057 +
            _persist       * 0.068,
            1
        )
        new_confidence = round(
            inertia_c      * 0.278 +
            _persist       * 0.267 +
            platform_c     * 0.222 +
            cal_gradient_c * 0.122 +
            decay_c        * 0.067 +
            dark_c         * 0.044,
            1
        )
    new_overall = round((new_detection + new_confidence) / 2, 1)

    # ── Pathway gate: the expert-component recompute above is valid ONLY for
    # expert-pathway topics. Mainstream/blended topics are scored by the
    # dual-pathway on magnitude+breadth, because the expert gradient is
    # structurally ~0 for them — re-deriving here collapses EVERY mainstream
    # topic to ~25-28 (FIFA 27.6, Trump 25.8, Juneteenth 25.1 — all ≈27,
    # unrankable) and silently undoes the dual-pathway. For those, PRESERVE the
    # incoming dual-pathway headline. (At scoring time the dual-pathway step runs
    # AFTER calibration and overwrites anyway; at SERVE time the stored row
    # carries detection_pathway='mainstream', so this keeps the two consistent.)
    _pathway = (raw_result.get("detection_pathway") or "expert").lower()
    if _pathway not in ("expert", "niche", ""):
        new_detection  = round(detection_score, 1)
        new_confidence = round(confidence_score, 1)
        new_overall    = round(overall_score, 1)

    # ── Reclassify stage with calibrated scores ───────────────────
    # rec F (2026-07-07, STAGE_FROM_DETECTION, default OFF): the board's Executioner
    # found the original flag was a near-no-op — this recompute (and the post-cal
    # dual-pathway block) OVERWROTE the detector's stage from the det/conf AVERAGE.
    # With the flag on, stage keys off the calibrated DETECTION score everywhere,
    # matching the UI's stageOf chips (one concept, one definition).
    _stage_basis = new_detection if _STAGE_FROM_DETECTION else (new_detection + new_confidence) / 2
    if _stage_basis >= 85:
        new_stage = "BREAKOUT"
    elif _stage_basis >= 70:
        new_stage = "STRONG"
    elif _stage_basis >= 55:
        new_stage = "EMERGING"
    elif _stage_basis >= 35:
        new_stage = "WATCHING"
    else:
        new_stage = "MONITORING"

    # ── Re-evaluate anomaly gate ──────────────────────────────────
    if CAL_ENGINE_AVAILABLE:
        new_is_anomaly, anomaly_evidence, anomaly_label = evaluate_anomaly_gate(
            gradient_ratio   = gradient_ratio,
            ft_ratio         = ft_ratio,
            asymmetry_detected = asymmetry,
            platform_count   = platform_count,
            inertia_score    = inertia,
            maturity         = maturity,
            gradient_velocity = maturity.get("gradient_velocity"),
        )
    else:
        # Fallback gate without calibration engine
        mat_class     = maturity.get("maturity_class", "NEW")
        has_velocity  = (maturity.get("gradient_velocity") or 0) >= 15
        has_xplatform = platform_count >= 2
        has_inertia   = inertia > INERTIA_ZERO_THRESHOLD

        if mat_class == "ESTABLISHED":
            new_is_anomaly = has_velocity and has_inertia
            anomaly_label  = "RESURGENCE ANOMALY" if new_is_anomaly else ""
        elif mat_class == "RESURGENT":
            new_is_anomaly = True
            anomaly_label  = "RESURGENCE ANOMALY"
        elif mat_class == "NEW":
            new_is_anomaly = has_xplatform and (has_inertia or ft_ratio > 0.20)
            anomaly_label  = "NEW SIGNAL ANOMALY" if new_is_anomaly else ""
        else:
            new_is_anomaly = has_xplatform and has_inertia and gradient_ratio >= 4
            anomaly_label  = "EMERGING ANOMALY" if new_is_anomaly else ""

        anomaly_evidence = []

    # ── Build communication text ──────────────────────────────────
    if CAL_ENGINE_AVAILABLE:
        what_to_do_dict = build_what_to_do(
            stage           = new_stage,
            maturity_class  = maturity["maturity_class"],
            inertia_score   = inertia,
            confidence_score = new_confidence,
            detection_score = new_detection,
            times_scored    = times_scored,
            gradient_velocity = maturity.get("gradient_velocity"),
            is_anomaly      = new_is_anomaly,
        )
        gap = abs(new_detection - new_confidence)
        gap_dict = build_gap_interpretation(gap, new_stage, maturity["maturity_class"])
        component_groups = build_component_groups({
            "gradient_calibrated": cal_gradient_d,
            "gradient_conf":       cal_gradient_c,
            "gradient_raw":        raw_gradient,
            "platform_det":        platform_d,
            "platform_diversity":  platform_c,
            "inertia":             inertia,
            "persistence":         raw_result.get("persistence_score", 0) or 0,
            "dark_matter":         dark_d,
            "confidence_decay":    decay_d,
            # N "now trending" internal demand is stored as `nowtrendin_score`
            # (with `nowtrend_internal` as a legacy fallback alias). Reading the
            # wrong key was leaving N hardcoded at 0/pending in the breakdown.
            "nowtrend_internal":   raw_result.get("nowtrendin_score",
                                       raw_result.get("nowtrend_internal", 0)) or 0,
            "gradient_calibration_note": cal_note_d,
        })
    else:
        what_to_do_dict = {
            "action":    "Monitor — check back after next collection cycle",
            "urgency":   "WAIT",
            "instruction": "Calibration engine not available. Showing raw scores.",
            "detail":    "",
            "lead_time_note": None,
        }
        gap_dict       = {"label": "", "meaning": ""}
        component_groups = {}

    # ── Lead time gating ──────────────────────────────────────────
    # NEVER show a lead time estimate when inertia = 0
    show_lead_time  = (
        inertia > INERTIA_ZERO_THRESHOLD
        and times_scored >= 2
        and new_stage in ("BREAKOUT", "STRONG", "EMERGING")
        and maturity["maturity_class"] not in ("ESTABLISHED",)
    )
    lead_time_note = what_to_do_dict.get("lead_time_note") if show_lead_time else None

    # ── Maturity badge text ───────────────────────────────────────
    maturity_class = maturity["maturity_class"]
    MATURITY_BADGE = {
        "NEW":         "🔵 New Signal",
        "EMERGING":    "🟢 Emerging",
        "ESTABLISHED": "⚪ Established Topic",
        "RESURGENT":   "🟡 Resurgent",
        "MONITORING":  "🔘 Monitoring",
    }
    MATURITY_COLOUR = {
        "NEW":         "blue",
        "EMERGING":    "green",
        "ESTABLISHED": "gray",
        "RESURGENT":   "gold",
        "MONITORING":  "light",
    }

    # ── Build calibration metadata block ─────────────────────────
    calibration_meta = {
        "applied":              True,
        "source":               maturity.get("source", "unknown"),
        "maturity_class":       maturity_class,
        "maturity_badge":       MATURITY_BADGE.get(maturity_class, maturity_class),
        "maturity_colour":      MATURITY_COLOUR.get(maturity_class, "light"),
        "maturity_reason":      maturity.get("maturity_reason", ""),
        "days_in_system":       maturity.get("days_in_system", 0),
        "times_scored":         times_scored,
        "is_first_run":         is_first_run,
        "gradient_velocity":    maturity.get("gradient_velocity"),
        "velocity_trend":       maturity.get("velocity_trend", "unknown"),
        "baseline_gradient":    maturity.get("baseline_gradient"),
        "calibration_factor":   cal_factor_d,
        "gradient_raw":         raw_gradient,
        "gradient_calibrated":  cal_gradient_d,
        "calibration_note":     cal_note_d,
        "anomaly_label":        anomaly_label,
        "anomaly_evidence":     anomaly_evidence,
        "show_lead_time":       show_lead_time,
        "lead_time_note":       lead_time_note,
    }

    # ── Assemble calibrated result ────────────────────────────────
    calibrated = {
        **raw_result,  # All original fields preserved

        # ── Overwritten scores ────────────────────────────────────
        "detection_score":               new_detection,
        "confidence_score":              new_confidence,
        "overall_score":                 new_overall,
        "signal_stage":                  new_stage,

        # ── Calibrated gradient components ───────────────────────
        "gradient_strength_detection":   cal_gradient_d,
        "gradient_strength_confidence":  cal_gradient_c,
        "gradient_strength_raw":         raw_gradient,

        # ── Corrected anomaly ─────────────────────────────────────
        "is_anomaly":                    new_is_anomaly,
        "anomaly_label":                 anomaly_label,

        # ── Communication text (WHAT TO DO first) ─────────────────
        "what_to_do_action":             what_to_do_dict["action"],
        "what_to_do_instruction":        what_to_do_dict["instruction"],
        "what_to_do_detail":             what_to_do_dict.get("detail", ""),
        "show_lead_time":                show_lead_time,
        "lead_time_note":                lead_time_note,

        # ── Gap interpretation (directional) ──────────────────────
        "gap_label":                     gap_dict["label"],
        "gap_meaning":                   gap_dict["meaning"],

        # ── Component groups (3 buckets) ──────────────────────────
        "component_groups":              component_groups,

        # ── First-run state flags ─────────────────────────────────
        "is_first_run":                  is_first_run,
        "inertia_pending_explanation": (
            "First collection run — inertia requires 2+ windows. "
            "Check back in ~30 minutes."
            if inertia <= INERTIA_ZERO_THRESHOLD else ""
        ),

        # ── Calibration metadata ──────────────────────────────────
        "calibration": calibration_meta,
    }

    # ── Record history for future baseline building ───────────────
    try:
        record_score_history(
            topic_key        = topic_key,
            topic_display    = raw_result.get("topic_display", topic_key),
            raw_gradient     = raw_gradient,
            calibrated_gradient = cal_gradient_d,
            overall_score    = new_overall,
            detection_score  = new_detection,
            confidence_score = new_confidence,
            inertia_score    = inertia,
            platform_count   = platform_count,
            total_mentions   = raw_result.get("total_mentions", 0),
            maturity_class   = maturity_class,
            db_path          = db_path,
        )
    except Exception:
        pass  # Never let history recording crash the main scoring flow

    return calibrated


# ════════════════════════════════════════════════════════════════
# CALIBRATION REPORT
# Shows current state of all calibrated topics
# ════════════════════════════════════════════════════════════════

def print_calibration_report(db_path: str = DB_PATH) -> None:
    """Print a summary of current calibration state."""
    conn = db_compat.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        rows = conn.execute("""
            SELECT topic_key, topic_display, maturity_class,
                   days_in_system, times_scored,
                   gradient_velocity, baseline_gradient,
                   calibration_multiplier
            FROM topic_maturity
            ORDER BY maturity_class, days_in_system DESC
            LIMIT 100
        """).fetchall()
    except sqlite3.OperationalError:
        print("topic_maturity table not found. Run --seed first.")
        conn.close()
        return

    conn.close()

    print("\n" + "="*70)
    print("NOW TRENDIN — CALIBRATION REPORT")
    print("="*70)

    current_class = None
    for row in rows:
        if row["maturity_class"] != current_class:
            current_class = row["maturity_class"]
            print(f"\n── {current_class} ──")

        velocity = row["gradient_velocity"]
        v_str    = f"{velocity:+.0f}pts" if velocity is not None else "no data"
        baseline = row["baseline_gradient"]
        b_str    = f"{baseline:.0f}" if baseline is not None else "no data"

        print(
            f"  {row['topic_display']:<25} "
            f"days:{row['days_in_system']:>4}  "
            f"cycles:{row['times_scored']:>3}  "
            f"baseline:{b_str:>6}  "
            f"velocity:{v_str:>8}  "
            f"multiplier:{row['calibration_multiplier']:.2f}"
        )

    # Known topics not yet in DB
    print("\n── KNOWN TOPICS NOT YET SEEDED ──")
    try:
        seeded_keys = set(r["topic_key"] for r in rows)
        not_seeded  = [k for k in KNOWN_TOPICS if k not in seeded_keys]
        if not_seeded:
            for k in not_seeded[:20]:
                info = KNOWN_TOPICS[k]
                years = _years_established(info["established_since"])
                print(f"  {k:<30} {years:.1f}y old — run --seed to load")
        else:
            print("  All known topics are seeded.")
    except Exception:
        pass

    print("\n" + "="*70)


# ════════════════════════════════════════════════════════════════
# INTEGRATION GUIDE
# Exact code to add to gravitational_anomaly_detector.py
# ════════════════════════════════════════════════════════════════

INTEGRATION_CODE = """
# ── ADD TO THE TOP OF gravitational_anomaly_detector.py ──────────

from signal_calibration_integration import (
    apply_calibration,
    seed_known_topics,
    recompute_velocities,
    init_calibration_db,
)

# Run once on startup (idempotent)
init_calibration_db(DB_PATH)
seed_known_topics(DB_PATH)


# ── MODIFY score_topic() — ADD AT THE VERY END ───────────────────

    # --- After the existing return dict is assembled: ---
    result = {
        "topic_key": ...,
        "detection_score": ...,
        # ... all existing fields ...
    }

    # Apply calibration (drop-in replacement)
    result = apply_calibration(result, db_path=DB_PATH)

    return result


# ── ADD AS A DAILY HEROKU SCHEDULER JOB ─────────────────────────

# Command: python -c "from signal_calibration_integration import
#    recompute_velocities; recompute_velocities()"
# Schedule: Daily at 6am UTC


# ── ADD TO /scores/{topic_key} ENDPOINT RESPONSE ─────────────────

# The calibration fields are already in the result dict.
# No changes needed to the endpoint — all new fields flow through.
# Frontend reads:
#   result.calibration.maturity_class
#   result.calibration.maturity_badge
#   result.what_to_do_action
#   result.what_to_do_instruction
#   result.component_groups
#   result.show_lead_time  (Boolean gate)
#   result.gap_label
#   result.is_first_run
#   result.inertia_pending_explanation
"""


# ════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Now TrendIn Signal Calibration Integration"
    )
    parser.add_argument("--seed", action="store_true",
        help="Pre-seed known topics into topic_maturity table")
    parser.add_argument("--report", action="store_true",
        help="Print calibration report for all topics")
    parser.add_argument("--analyse", type=str, default="",
        help="Analyse a specific topic key (e.g. 'ai_agent')")
    parser.add_argument("--update-velocities", action="store_true",
        help="Recompute gradient velocities for all topics")
    parser.add_argument("--show-integration", action="store_true",
        help="Print the exact integration code for the detector")
    args = parser.parse_args()

    if args.seed:
        init_calibration_db(DB_PATH)
        count = seed_known_topics(DB_PATH)
        print(f"\n✓ {count} known topics seeded.")
        print("Known topics will now calibrate correctly on first detection.")

    elif args.report:
        print_calibration_report(DB_PATH)

    elif args.analyse:
        topic_key = args.analyse.lower().replace(" ", "_")
        state     = get_topic_maturity_state(topic_key, DB_PATH)
        print(f"\nCalibration state for: {args.analyse}")
        print(json.dumps(state, indent=2, default=str))

        known = _lookup_known_topic(topic_key)
        if known:
            years = _years_established(known["established_since"])
            print(f"\nKnown topic: {known['display']}")
            print(f"  Established: {known['established_since']} ({years:.1f} years ago)")
            print(f"  Domain: {known['domain']}")
            print(f"  Natural expert gradient: {known['natural_gradient']}%")
            print(f"  Note: {known['note']}")
        else:
            print(f"\nNot in known topics database — will calibrate from history.")

    elif args.update_velocities:
        updated = recompute_velocities(DB_PATH)
        print(f"✓ Updated velocities for {updated} topics.")

    elif args.show_integration:
        print(INTEGRATION_CODE)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
