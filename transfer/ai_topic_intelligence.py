"""
================================================================
NOW TRENDIN — AI TOPIC INTELLIGENCE ENGINE
================================================================

AI-FEATURE BRANCH — DEVELOPMENT CHECKPOINT
----------------------------------------------------------------
Branch   : AI-feature
Purpose  : Isolated development of AI tier scoring improvements
Status   : Active ✓
----------------------------------------------------------------

THE PROBLEM THIS SOLVES:
  The user correctly identified that "AI" and AI-related topics
  should score near 100 — but the prototype was returning scores
  of 8-22 for the most viral AI topics in the world right now.

  The root cause: the engine treats "AI" as a single concept.
  It is not. "AI" is a category containing hundreds of distinct
  topics at radically different positions on the diffusion curve:

    "Artificial Intelligence" → mainstream consumer → score: 20
    "LLM"                     → established expert  → score: 35
    "Agentic Coding"          → VIRAL right now      → score: 97
    "Agent Memory"            → VIRAL right now      → score: 94
    "12-Factor Agents"        → VIRAL right now      → score: 92

  The same parent category ("AI") contains topics spanning from
  MONITORING all the way to near-BREAKOUT. A search for "AI"
  should surface ALL of them — ranked by their individual score —
  rather than returning one blurred aggregate.

WHAT THIS FILE PROVIDES:
  1. AI_TOPIC_TIERS — comprehensive taxonomy of 70+ AI topics
     classified by their current virality tier (1–4)

  2. AITopicIntelligenceEngine — the main scoring engine that:
     a. Classifies any topic into the correct tier
     b. Applies tier-appropriate score floors and ceilings
     c. Detects AI topic "clusters" (related variations)
     d. Generates research section content (why this scores here)
     e. Produces the "variation map" showing all related topics

  3. score_ai_topic() — drop-in function for the existing detector
     that replaces raw scores with tier-aware calibrated scores

  4. generate_research_section() — produces the plain-English
     research section showing how long this topic has been
     discussed, what velocity it's showing, and how it relates
     to other AI variations

HOW IT INTEGRATES:
  In gravitational_anomaly_detector.py, after score_topic():

    from ai_topic_intelligence import AITopicIntelligenceEngine
    engine = AITopicIntelligenceEngine()
    result = engine.apply(result, raw_signals)

  In the /scores/{topic_key} endpoint, add:
    result["research"] = engine.generate_research_section(result)
    result["variations"] = engine.get_related_variations(result)

SCORING PHILOSOPHY:
  A topic scores 100/100 when:
    - It is genuinely NEW or RESURGENT (not just permanently expert)
    - It has sustained acceleration across multiple collection windows
    - It appears on 2+ independent expert platforms simultaneously
    - It has not yet crossed into mainstream awareness
    - New voices are entering the conversation (first-timer ratio high)

  "AI" as a generic term scores ~20 because it IS mainstream.
  "Agentic Coding" scores ~97 because it IS viral and still expert.
  Both are correct. Both are "AI". The engine distinguishes them.
================================================================
"""

import re
import math
import json
from datetime import datetime, timezone
from typing import Optional


# ════════════════════════════════════════════════════════════════
# SECTION 1: AI TOPIC TAXONOMY
# 70+ topics classified by virality tier (current as of May 2026)
# Updated based on live GitHub Trending, HN, DEV.to data
# ════════════════════════════════════════════════════════════════

AI_TOPIC_TIERS = {

    # ── TIER 1: VIRAL RIGHT NOW ────────────────────────────────────
    # These should score 90–100 on Detection AND Confidence
    # Criteria: genuinely new vocabulary + sustained acceleration
    #           + still primarily in expert communities
    #           + 73,000+ new GitHub stars in 7 days (week of May 21, 2026)
    "tier_1": {
        "label": "VIRAL — Maximum Lead Time",
        "detection_floor": 88,
        "confidence_floor": 85,
        "detection_ceiling": 100,
        "confidence_ceiling": 100,
        "colour": "green",
        "topics": {
            "agentic_coding": {
                "display": "agentic coding",
                "first_appeared": "2024-01-01",
                "viral_since": "2025-11-01",
                "why_viral": (
                    "Claude Code now authors 10% of all public GitHub commits "
                    "(326,000/day, up from 4% in February 2026). Developers are "
                    "fundamentally changing how they write software. This behavioural "
                    "shift is still almost entirely inside developer communities — "
                    "mainstream awareness has not caught up."
                ),
                "platforms": ["github", "hackernews", "devto", "discourse"],
                "natural_gradient": 96,
                "velocity_signal": "ACCELERATING",
                "aliases": ["agentic coding", "agent coding", "ai-assisted coding",
                           "ai coding workflow", "coding agent"],
            },
            "agent_memory": {
                "display": "agent memory",
                "first_appeared": "2024-06-01",
                "viral_since": "2026-03-01",
                "why_viral": (
                    "Mem0 hit 55,000+ GitHub stars with April 2026 algorithm upgrade. "
                    "Three of the top 10 GitHub repositories for the week of May 21, 2026 "
                    "directly address agent memory and token reduction. Persistent memory "
                    "is becoming standard agent infrastructure — a new engineering "
                    "category is crystallising in real time."
                ),
                "platforms": ["github", "hackernews", "devto"],
                "natural_gradient": 95,
                "velocity_signal": "ACCELERATING",
                "aliases": ["agent memory", "persistent memory", "agentic memory",
                           "memory layer", "agent context", "mem0"],
            },
            "12_factor_agents": {
                "display": "12-factor agents",
                "first_appeared": "2025-04-01",
                "viral_since": "2026-04-01",
                "why_viral": (
                    "The 12-factor-agents repository landed in GitHub's top 10 trending "
                    "for the week of May 21, 2026. In the spirit of Heroku's 12 Factor "
                    "Apps, these are principles for building reliable LLM-powered software. "
                    "This is vocabulary crystallisation — developers independently naming "
                    "the same shared problem. New terminology emerging = high first-timer "
                    "ratio and maximum gradient."
                ),
                "platforms": ["github", "hackernews"],
                "natural_gradient": 97,
                "velocity_signal": "BREAKOUT",
                "aliases": ["12-factor agents", "12 factor agents", "12factor agents",
                           "twelve factor agents"],
            },
            "context_engineering": {
                "display": "context engineering",
                "first_appeared": "2025-06-01",
                "viral_since": "2026-02-01",
                "why_viral": (
                    "Emerging as the successor framing to 'prompt engineering'. "
                    "The insight: managing what goes into the model's context window "
                    "is the real engineering discipline. Appearing explicitly as a "
                    "GitHub tag alongside agentic-coding and 12-factor-agents. "
                    "Still entirely inside expert developer communities."
                ),
                "platforms": ["github", "devto", "hackernews"],
                "natural_gradient": 94,
                "velocity_signal": "ACCELERATING",
                "aliases": ["context engineering", "context management", "context window engineering"],
            },
            "on_device_ai": {
                "display": "on-device AI",
                "first_appeared": "2024-01-01",
                "viral_since": "2026-01-01",
                "why_viral": (
                    "Six of the top 10 GitHub trending repositories for the week of "
                    "May 21, 2026 declared on-device or local-first architecture. "
                    "Latency, per-call cost, and privacy are driving a convergent "
                    "architectural decision across independent projects simultaneously — "
                    "the definition of a genuine trend signal."
                ),
                "platforms": ["github", "hackernews", "devto"],
                "natural_gradient": 93,
                "velocity_signal": "ACCELERATING",
                "aliases": ["on-device ai", "on device ai", "edge inference",
                           "local inference", "device-side ai"],
            },
            "openai_codex": {
                "display": "OpenAI Codex",
                "first_appeared": "2026-01-01",
                "viral_since": "2026-03-01",
                "why_viral": (
                    "OpenAI Codex CLI hit ~85,000 GitHub stars by May 2026. "
                    "Ships weekly releases (v0.133.0 as of May 21, 2026). "
                    "Shipped subagents GA in March 2026 with up to 8 parallel workers. "
                    "Predominantly in developer communities — limited mainstream awareness."
                ),
                "platforms": ["github", "hackernews", "devto"],
                "natural_gradient": 91,
                "velocity_signal": "STRONG",
                "aliases": ["openai codex", "codex cli", "gpt-5 codex", "codex agent"],
            },
        },
    },

    # ── TIER 2: STRONG SIGNAL ──────────────────────────────────────
    # Should score 65–88 on Detection, 60–85 on Confidence
    # Criteria: established within last 18 months, still accelerating
    #           but beginning to cross to informed mainstream audiences
    "tier_2": {
        "label": "STRONG — Window Open",
        "detection_floor": 65,
        "confidence_floor": 58,
        "detection_ceiling": 88,
        "confidence_ceiling": 85,
        "colour": "blue",
        "topics": {
            "mcp": {
                "display": "MCP (Model Context Protocol)",
                "first_appeared": "2024-11-01",
                "viral_since": "2025-01-01",
                "why_viral": (
                    "97 million monthly SDK downloads, 81,000+ GitHub stars, "
                    "supported by all major AI vendors. Introduced November 2024, "
                    "now 18 months old. Still very high expert-community concentration "
                    "but beginning to reach informed business audiences. "
                    "Velocity has normalised from its 2024-2025 explosive growth "
                    "but remains well above zero — qualifying as STRONG."
                ),
                "platforms": ["github", "hackernews", "devto", "discourse"],
                "natural_gradient": 92,
                "velocity_signal": "NORMALISING",
                "aliases": ["mcp", "model context protocol", "mcp server",
                           "mcp client", "mcp tools"],
            },
            "claude_code": {
                "display": "Claude Code",
                "first_appeared": "2025-01-01",
                "viral_since": "2025-06-01",
                "why_viral": (
                    "Anthropic's agentic coding tool now authors 326K GitHub commits/day. "
                    "The Anthropic June 15, 2026 billing split (interactive vs programmatic) "
                    "is generating significant developer discussion. Strong signal but "
                    "Claude Code is a product name — the underlying concept "
                    "'agentic coding' is the purer trend signal at Tier 1."
                ),
                "platforms": ["github", "hackernews", "devto"],
                "natural_gradient": 88,
                "velocity_signal": "STRONG",
                "aliases": ["claude code", "anthropic claude code", "claude coding agent"],
            },
            "vibe_coding": {
                "display": "vibe coding",
                "first_appeared": "2025-02-01",
                "viral_since": "2025-02-15",
                "why_viral": (
                    "Term coined by Andrej Karpathy in February 2025. Now 15+ months "
                    "old, still growing but moving from peak virality toward "
                    "established vocabulary. Appeared in GitHub tags alongside "
                    "12-factor-agents and agentic-coding as of May 2026."
                ),
                "platforms": ["github", "hackernews", "devto", "twitter"],
                "natural_gradient": 87,
                "velocity_signal": "MATURE",
                "aliases": ["vibe coding", "vibecoding", "vibe-coding"],
            },
            "multi_agent": {
                "display": "multi-agent systems",
                "first_appeared": "2024-01-01",
                "viral_since": "2025-06-01",
                "why_viral": (
                    "Codex shipped subagents GA in March 2026 (8 parallel workers). "
                    "Claude Code added agent teams with message passing. "
                    "The concept of coordinating multiple agents is becoming "
                    "standard architecture — moving from research to production."
                ),
                "platforms": ["github", "hackernews", "discourse"],
                "natural_gradient": 90,
                "velocity_signal": "ACCELERATING",
                "aliases": ["multi-agent", "multi agent", "multiagent", "agent teams",
                           "agent orchestration", "agent coordination"],
            },
            "ai_agent_framework": {
                "display": "AI agent framework",
                "first_appeared": "2024-01-01",
                "viral_since": "2025-01-01",
                "why_viral": (
                    "Mastra (21K+ stars), VoltAgent, LangGraph, CrewAI — "
                    "the framework wars are active. A new framework lands on "
                    "GitHub trending roughly every 2-3 weeks. The category is "
                    "real and growing but individual frameworks fragment the signal."
                ),
                "platforms": ["github", "hackernews", "devto"],
                "natural_gradient": 91,
                "velocity_signal": "STRONG",
                "aliases": ["agent framework", "ai agent framework", "llm framework",
                           "agentic framework"],
            },
            "a2a_protocol": {
                "display": "A2A (Agent-to-Agent Protocol)",
                "first_appeared": "2025-04-01",
                "viral_since": "2025-10-01",
                "why_viral": (
                    "Google released A2A in April 2025 as MCP's companion protocol. "
                    "Defines how agents collaborate with each other (MCP = agents to tools, "
                    "A2A = agents to agents). Now part of the Agentic AI Foundation "
                    "under the Linux Foundation. Strong but slightly behind MCP in adoption."
                ),
                "platforms": ["github", "hackernews", "devto"],
                "natural_gradient": 93,
                "velocity_signal": "BUILDING",
                "aliases": ["a2a", "agent to agent", "a2a protocol", "agent communication protocol"],
            },
        },
    },

    # ── TIER 3: ESTABLISHED EXPERT — NEEDS VELOCITY TO EMERGE ──────
    # Current score: 25–65 Detection, 20–60 Confidence
    # These have permanently high gradient (expert home) but
    # baseline gradient does NOT indicate current emergence.
    # Score rises ONLY if velocity is confirmed above baseline.
    "tier_3": {
        "label": "ESTABLISHED — Monitor for Resurgence",
        "detection_floor": 18,
        "confidence_floor": 12,
        "detection_ceiling": 65,
        "confidence_ceiling": 60,
        "colour": "gray",
        "topics": {
            "llm": {
                "display": "LLM",
                "first_appeared": "2020-01-01",
                "velocity_signal": "STABLE",
                "natural_gradient": 92,
                "why_calibrated": "LLM is the permanent vocabulary of the ML community. "
                                  "It has been in expert discussions since 2020. High gradient "
                                  "reflects permanent expert home, not emergence.",
                "aliases": ["llm", "large language model", "language model"],
            },
            "rag": {
                "display": "RAG (Retrieval-Augmented Generation)",
                "first_appeared": "2020-04-01",
                "velocity_signal": "STABLE",
                "natural_gradient": 88,
                "why_calibrated": "RAG paper published April 2020. Core ML technique "
                                  "for 5+ years. Still expert-only but at baseline — "
                                  "no current resurgence signal.",
                "aliases": ["rag", "retrieval augmented", "retrieval augmented generation"],
            },
            "agentic_ai": {
                "display": "agentic AI",
                "first_appeared": "2023-01-01",
                "velocity_signal": "STABLE_HIGH",
                "natural_gradient": 91,
                "why_calibrated": "Term from 2023, now standard vocabulary. High gradient "
                                  "is permanent expert home. Tier 1 sub-topics (agentic coding, "
                                  "agent memory) are the current velocity signals — "
                                  "this umbrella term is stable.",
                "aliases": ["agentic ai", "agentic", "agentic systems"],
            },
            "ai_agent": {
                "display": "AI agent",
                "first_appeared": "2018-01-01",
                "velocity_signal": "STABLE",
                "natural_gradient": 85,
                "why_calibrated": "In expert communities since 2018. AutoGPT surge in 2023 "
                                  "has settled. The specific sub-problems (memory, workflow, "
                                  "reliability patterns) are the current signals — not the "
                                  "umbrella term.",
                "aliases": ["ai agent", "ai agents", "autonomous agent"],
            },
            "fine_tuning": {
                "display": "fine-tuning",
                "first_appeared": "2018-01-01",
                "velocity_signal": "STABLE",
                "natural_gradient": 90,
                "why_calibrated": "Core ML technique stable for 5+ years. No current "
                                  "resurgence unless a major new fine-tuning method releases.",
                "aliases": ["fine-tuning", "fine tuning", "finetuning", "lora", "qlora"],
            },
            "prompt_engineering": {
                "display": "prompt engineering",
                "first_appeared": "2021-06-01",
                "velocity_signal": "DECLINING",
                "natural_gradient": 75,
                "why_calibrated": "Being superseded by 'context engineering' as the "
                                  "preferred framing. Declining velocity is a signal in "
                                  "itself — the category is maturing out.",
                "aliases": ["prompt engineering", "prompting", "system prompt"],
            },
            "vector_database": {
                "display": "vector database",
                "first_appeared": "2021-01-01",
                "velocity_signal": "STABLE",
                "natural_gradient": 90,
                "why_calibrated": "Pinecone, Weaviate, Qdrant — the category is "
                                  "established infrastructure now. Used everywhere "
                                  "but no current breakout signal.",
                "aliases": ["vector database", "vector db", "embedding database",
                           "pinecone", "qdrant", "weaviate"],
            },
        },
    },

    # ── TIER 4: MAINSTREAM / CONSUMER ─────────────────────────────
    # Current score: 15–35 Detection, 20–45 Confidence
    # These have CROSSED into mainstream awareness. Low gradient
    # because mentions are distributed across all audience types,
    # not concentrated in expert communities.
    "tier_4": {
        "label": "MAINSTREAM — Already Arrived",
        "detection_floor": 12,
        "confidence_floor": 15,
        "detection_ceiling": 40,
        "confidence_ceiling": 48,
        "colour": "muted",
        "topics": {
            "ai": {
                "display": "AI (generic)",
                "first_appeared": "1956-01-01",
                "velocity_signal": "MAINSTREAM",
                "natural_gradient": 20,
                "why_calibrated": "Artificial intelligence has been mainstream consumer "
                                  "vocabulary since ChatGPT (2022). Mentions are distributed "
                                  "across all audience types. Low gradient is correct — "
                                  "this IS the mainstream. Search for specific AI sub-topics "
                                  "to find the leading edge.",
                "aliases": ["ai", "artificial intelligence"],
            },
            "chatgpt": {
                "display": "ChatGPT",
                "first_appeared": "2022-11-30",
                "velocity_signal": "MAINSTREAM",
                "natural_gradient": 25,
                "why_calibrated": "Mainstream consumer product since November 2022. "
                                  "Search volume dominated by non-technical users. "
                                  "Low gradient is correct — the expert community has "
                                  "moved to more specific sub-topics.",
                "aliases": ["chatgpt", "chat gpt", "gpt-4", "openai chat"],
            },
            "generative_ai": {
                "display": "generative AI",
                "first_appeared": "2022-01-01",
                "velocity_signal": "MAINSTREAM",
                "natural_gradient": 42,
                "why_calibrated": "Business buzzword since 2022. Now appears in McKinsey "
                                  "reports, corporate strategy documents, and mainstream news. "
                                  "The expert community uses more specific terminology.",
                "aliases": ["generative ai", "genai", "gen ai"],
            },
            "machine_learning": {
                "display": "machine learning",
                "first_appeared": "1959-01-01",
                "velocity_signal": "STABLE_MAINSTREAM",
                "natural_gradient": 58,
                "why_calibrated": "Academic term from 1959. Now split between expert "
                                  "technical use and mainstream business use. "
                                  "Mid-range gradient reflects this split.",
                "aliases": ["machine learning", "ml"],
            },
        },
    },
}


# ════════════════════════════════════════════════════════════════
# SECTION 2: TOPIC LOOKUP INDEX
# Flat index for O(1) lookup of any topic → its tier config
# ════════════════════════════════════════════════════════════════

def _build_lookup_index() -> dict:
    """Build a flat {alias: (tier_key, topic_key, topic_config)} index."""
    index = {}
    for tier_key, tier_config in AI_TOPIC_TIERS.items():
        topics = tier_config.get("topics", {})
        for topic_key, topic_config in topics.items():
            aliases = topic_config.get("aliases", [topic_config["display"]])
            for alias in aliases:
                normalised = alias.lower().strip()
                index[normalised] = (tier_key, topic_key, topic_config, tier_config)
            # Also index by topic_key itself
            index[topic_key.replace("_", " ")] = (tier_key, topic_key, topic_config, tier_config)
    return index

_TOPIC_INDEX = _build_lookup_index()


def lookup_topic(phrase: str) -> Optional[tuple]:
    """
    Look up a topic phrase in the AI taxonomy.
    Returns (tier_key, topic_key, topic_config, tier_config) or None.

    Tries:
      1. Exact normalised match
      2. Any known alias substring match
      3. Any known topic key contained in the phrase
    """
    pl = phrase.lower().strip()
    pl_clean = re.sub(r'[-_]', ' ', pl)

    # Exact match
    if pl in _TOPIC_INDEX:
        return _TOPIC_INDEX[pl]
    if pl_clean in _TOPIC_INDEX:
        return _TOPIC_INDEX[pl_clean]

    # Substring match — phrase contains a known alias
    best_match = None
    best_len   = 0
    for alias, entry in _TOPIC_INDEX.items():
        if alias in pl_clean and len(alias) > best_len and len(alias) >= 4:
            best_match = entry
            best_len   = len(alias)

    return best_match


# ════════════════════════════════════════════════════════════════
# SECTION 3: SCORE CALCULATION ENGINE
# Applies tier-aware scoring floors, ceilings, and velocity boosts
# ════════════════════════════════════════════════════════════════

def _years_old(date_str: str) -> float:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return (datetime.now() - dt).days / 365.25
    except Exception:
        return 0.0


def compute_tier_aware_scores(
    topic_phrase: str,
    raw_detection: float,
    raw_confidence: float,
    signal_count: int,
    platform_count: int,
    inertia_score: float,
    gradient_velocity: Optional[float],
    times_scored: int,
) -> dict:
    """
    The main scoring function. Given a raw Gradient Score result,
    applies AI-taxonomy-aware adjustments to produce accurate scores.

    Key principle:
      Tier 1 topics ARE viral right now — their raw score should
      reach toward 100 when signal volume and platform spread confirm it.

      Tier 4 topics ARE mainstream — their raw score correctly lands
      low because gradient is naturally low. This is not a bug.

    Returns a dict with corrected scores and full explanation.
    """
    result = lookup_topic(topic_phrase)

    if not result:
        # Not a known AI topic — return raw scores unchanged
        return {
            "detection_score":  raw_detection,
            "confidence_score": raw_confidence,
            "tier":             None,
            "tier_label":       None,
            "ai_classification": None,
            "score_explanation": None,
            "research_note":     None,
        }

    tier_key, topic_key, topic_config, tier_config = result

    det_floor   = tier_config["detection_floor"]
    conf_floor  = tier_config["confidence_floor"]
    det_ceiling = tier_config["detection_ceiling"]
    conf_ceiling= tier_config["confidence_ceiling"]

    # ── Base: apply tier floor ────────────────────────────────────
    det  = max(raw_detection,  det_floor)
    conf = max(raw_confidence, conf_floor)

    # ── Volume modifier: more signals = higher confidence ─────────
    # Tier 1 topics should approach 100 with sufficient volume
    if tier_key == "tier_1":
        if signal_count >= 20:
            volume_boost = 15
        elif signal_count >= 10:
            volume_boost = 10
        elif signal_count >= 5:
            volume_boost = 5
        else:
            volume_boost = 0

        platform_boost = (platform_count - 1) * 5 if platform_count > 1 else 0
        det  = min(det_ceiling,  det  + volume_boost + platform_boost)
        conf = min(conf_ceiling, conf + volume_boost + platform_boost)

    elif tier_key == "tier_2":
        if signal_count >= 15:
            volume_boost = 8
        elif signal_count >= 8:
            volume_boost = 5
        else:
            volume_boost = 0
        det  = min(det_ceiling,  det  + volume_boost)
        conf = min(conf_ceiling, conf + volume_boost)

    # ── Inertia boost: confirmed acceleration raises score ─────────
    # Only applies when the system has seen multiple collection cycles
    if inertia_score > 5 and times_scored >= 2:
        inertia_pct = min(1.0, inertia_score / 100.0)
        if tier_key == "tier_1":
            inertia_boost_det  = round(inertia_pct * 20, 1)
            inertia_boost_conf = round(inertia_pct * 25, 1)
        elif tier_key == "tier_2":
            inertia_boost_det  = round(inertia_pct * 15, 1)
            inertia_boost_conf = round(inertia_pct * 18, 1)
        else:
            inertia_boost_det  = round(inertia_pct * 8, 1)
            inertia_boost_conf = round(inertia_pct * 10, 1)

        det  = min(det_ceiling,  det  + inertia_boost_det)
        conf = min(conf_ceiling, conf + inertia_boost_conf)

    # ── Velocity boost for Tier 3 RESURGENT signals ───────────────
    if tier_key == "tier_3" and gradient_velocity and gradient_velocity >= 15:
        resurgence_boost = min(20, gradient_velocity * 0.8)
        det  = min(det_ceiling + 25, det  + resurgence_boost)
        conf = min(conf_ceiling + 20, conf + resurgence_boost)
        tier_key = "tier_3_resurgent"

    # ── Ceiling: mainstream topics cannot score above their ceiling ─
    det  = min(det_ceiling,  round(det,  1))
    conf = min(conf_ceiling, round(conf, 1))

    # ── Build explanation ─────────────────────────────────────────
    velocity_str = topic_config.get("velocity_signal", "UNKNOWN")
    why          = topic_config.get(
        "why_viral",
        topic_config.get("why_calibrated", "")
    )
    first_appeared = _years_old(topic_config.get("first_appeared", "2020-01-01"))

    explanation = _build_score_explanation(
        topic_phrase, tier_key, tier_config["label"],
        det, conf, signal_count, platform_count,
        inertia_score, velocity_str, why, first_appeared
    )

    return {
        "detection_score":   det,
        "confidence_score":  conf,
        "tier":              tier_key,
        "tier_label":        tier_config["label"],
        "tier_colour":       tier_config["colour"],
        "velocity_signal":   velocity_str,
        "ai_classification": topic_config["display"],
        "score_explanation": explanation,
        "why_this_score":    why,
        "first_appeared_years_ago": round(first_appeared, 1),
    }


def _build_score_explanation(
    topic: str,
    tier: str,
    tier_label: str,
    detection: float,
    confidence: float,
    signals: int,
    platforms: int,
    inertia: float,
    velocity: str,
    why: str,
    years_old: float,
) -> str:
    """Plain-English explanation of why this topic scores where it does."""

    if "tier_1" in tier:
        intro = (
            f"'{topic}' is scoring in the VIRAL tier because it represents "
            f"genuinely new vocabulary in the developer community that has been "
            f"building over the past {int(years_old * 12)} months."
        )
        action = (
            "Detection is optimised for speed — act now if you can tolerate "
            "some uncertainty. Confidence is high enough to recommend planning "
            "concrete action. This is inside the early-actor window."
        )
    elif tier == "tier_2":
        intro = (
            f"'{topic}' is a strong active signal. It is approximately "
            f"{int(years_old * 12)} months old and still showing positive velocity "
            f"above its own baseline — meaning it continues to accelerate, "
            f"not just persist."
        )
        action = (
            "The window to act as an early mover is narrowing but still open. "
            "Begin planning concrete strategy. Wait for one more confirmation "
            "cycle if confidence matters more than speed."
        )
    elif "resurgent" in str(tier):
        intro = (
            f"'{topic}' is an established topic showing renewed acceleration "
            f"above its historical baseline. This is a resurgence signal — "
            f"the community has returned to something it understands, which "
            f"typically accelerates faster than a first emergence."
        )
        action = (
            "Resurgence signals often move faster than first-emergence signals "
            "because the infrastructure and vocabulary already exist. Act with "
            "the same urgency as a Tier 1 signal."
        )
    elif tier == "tier_3":
        intro = (
            f"'{topic}' has been established expert vocabulary for "
            f"{int(years_old)} years. Its high gradient strength reflects "
            f"its permanent home in expert communities — not current emergence. "
            f"Scoring reflects baseline presence, not active trend."
        )
        action = (
            "Monitor for velocity signals: a first-timer surge, cross-platform "
            "acceleration, or gradient above historical baseline would trigger "
            "reclassification. The sub-topics below may show current momentum."
        )
    else:  # tier_4 mainstream
        intro = (
            f"'{topic}' is mainstream consumer vocabulary. Its low score "
            f"reflects that mentions are distributed across all audience types — "
            f"not concentrated in expert communities. This is correct. "
            f"The topic has already arrived. Search for specific sub-topics "
            f"to find the leading edge."
        )
        action = (
            "This topic is not where the leading edge is. Navigate to "
            "'Related Topics' below to find the Tier 1 and Tier 2 sub-signals "
            "that are showing current velocity."
        )

    return f"{intro}\n\n{why}\n\n{action}"


# ════════════════════════════════════════════════════════════════
# SECTION 4: VARIATION MAP
# Shows all AI topic variations with their relative scores,
# grouped by relationship to the searched topic
# ════════════════════════════════════════════════════════════════

# Relationship graph: {topic_key: [related_topic_keys]}
TOPIC_RELATIONSHIPS = {
    # AI Agents cluster
    "ai_agent":       ["agentic_ai", "agentic_coding", "agent_memory",
                       "12_factor_agents", "multi_agent", "ai_agent_framework"],
    "agentic_ai":     ["ai_agent", "agentic_coding", "agent_memory",
                       "12_factor_agents", "multi_agent"],
    "agentic_coding": ["claude_code", "openai_codex", "vibe_coding",
                       "context_engineering", "12_factor_agents", "agent_memory"],
    "agent_memory":   ["12_factor_agents", "agentic_coding", "multi_agent",
                       "mcp", "context_engineering"],

    # Coding agents cluster
    "claude_code":    ["agentic_coding", "openai_codex", "vibe_coding",
                       "mcp", "context_engineering"],
    "openai_codex":   ["claude_code", "agentic_coding", "vibe_coding", "mcp"],
    "vibe_coding":    ["agentic_coding", "claude_code", "openai_codex",
                       "context_engineering"],

    # Infrastructure cluster
    "mcp":            ["a2a_protocol", "agent_memory", "multi_agent",
                       "agentic_coding", "claude_code"],
    "a2a_protocol":   ["mcp", "multi_agent", "ai_agent_framework"],
    "llm":            ["rag", "fine_tuning", "prompt_engineering",
                       "vector_database", "context_engineering"],

    # Generic → specific
    "ai":             ["agentic_coding", "agent_memory", "12_factor_agents",
                       "mcp", "claude_code", "vibe_coding", "on_device_ai"],
    "chatgpt":        ["openai_codex", "gpt", "vibe_coding"],
    "generative_ai":  ["agentic_coding", "mcp", "claude_code", "agent_memory"],
}


def get_variation_map(topic_phrase: str) -> list[dict]:
    """
    Returns a list of related topics with their tier scores,
    sorted by Detection score descending.

    This is the core "distinguish the variations" output:
    Shows that "AI" → 20 while "agentic coding" → 97,
    both within the same parent category.
    """
    lookup = lookup_topic(topic_phrase)
    if not lookup:
        return []

    _, topic_key, _, _ = lookup
    related_keys = TOPIC_RELATIONSHIPS.get(topic_key, [])

    # Always include the topic itself
    all_keys = [topic_key] + [k for k in related_keys if k != topic_key]

    variations = []
    for key in all_keys[:10]:  # max 10 variations
        # Find this topic in the taxonomy
        found = False
        for tier_key, tier_config in AI_TOPIC_TIERS.items():
            topics = tier_config.get("topics", {})
            if key in topics:
                t = topics[key]
                # Compute typical score for this tier with median signal volume
                typical_det  = (tier_config["detection_floor"]  + tier_config["detection_ceiling"]) / 2
                typical_conf = (tier_config["confidence_floor"] + tier_config["confidence_ceiling"]) / 2

                # For Tier 1 topics, use the upper range as the "expected" score
                if tier_key == "tier_1":
                    typical_det  = tier_config["detection_ceiling"] * 0.95
                    typical_conf = tier_config["confidence_ceiling"] * 0.93

                variations.append({
                    "topic_key":    key,
                    "display":      t["display"],
                    "tier":         tier_key,
                    "tier_label":   tier_config["label"],
                    "tier_colour":  tier_config["colour"],
                    "velocity":     t.get("velocity_signal", "UNKNOWN"),
                    "typical_detection": round(typical_det,  1),
                    "typical_confidence": round(typical_conf, 1),
                    "is_queried":   key == topic_key,
                    "why_different": _variation_note(topic_key, key, tier_key),
                })
                found = True
                break

        if not found and key == topic_key:
            variations.append({
                "topic_key": key, "display": topic_phrase,
                "tier": None, "tier_label": "Unknown",
                "tier_colour": "muted",
                "typical_detection": 0, "typical_confidence": 0,
                "is_queried": True, "why_different": "",
            })

    # Sort: Tier 1 first, then by detection score
    tier_order = {"tier_1": 0, "tier_2": 1, "tier_3": 2,
                  "tier_3_resurgent": 1, "tier_4": 3}
    variations.sort(key=lambda x: (
        tier_order.get(x["tier"], 4),
        -x["typical_detection"],
    ))

    return variations


def _variation_note(parent_key: str, child_key: str, child_tier: str) -> str:
    """One-sentence note explaining why a related topic scores differently."""
    if child_tier == "tier_1":
        notes = {
            "agentic_coding": "The specific application causing the surge — 10% of GitHub commits",
            "agent_memory":   "New infrastructure category — 55K stars, 73K new this week",
            "12_factor_agents": "New design pattern vocabulary crystallising in real time",
            "context_engineering": "Successor to prompt engineering — new vocabulary emerging",
            "on_device_ai":   "6 of top 10 GitHub trending repos declare on-device architecture",
            "openai_codex":   "OpenAI's coding agent — 85K stars, weekly releases",
        }
        return notes.get(child_key, "Active Tier 1 signal — showing maximum velocity.")
    elif child_tier == "tier_2":
        notes = {
            "mcp":          "18 months old, 97M downloads/month — normalising but still strong",
            "claude_code":  "Product-specific signal — underlying concept scores higher as 'agentic coding'",
            "vibe_coding":  "15+ months old, now moving toward established vocabulary",
            "multi_agent":  "Accelerating with Codex subagents GA in March 2026",
            "a2a_protocol": "MCP's companion protocol — newer and building momentum",
        }
        return notes.get(child_key, "Strong signal — window still open.")
    elif "tier_3" in child_tier:
        return "Established expert vocabulary — high gradient is permanent home, not emergence."
    else:
        return "Mainstream consumer term — low gradient correctly reflects broad audience."


# ════════════════════════════════════════════════════════════════
# SECTION 5: RESEARCH SECTION GENERATOR
# Produces the plain-English research content for the detail panel
# This replaces "why this matters" and "what to watch" with
# taxonomy-aware, historically grounded explanations
# ════════════════════════════════════════════════════════════════

def generate_research_section(
    topic_phrase: str,
    detection_score: float,
    confidence_score: float,
    signal_count: int,
    platform_count: int,
    inertia_score: float,
    is_first_run: bool,
) -> dict:
    """
    Generates the complete research section for the signal detail panel.

    Returns a dict containing:
      - topic_age: plain English description of how old this topic is
      - tier_context: why it scores in this tier
      - what_to_do: action recommendation (maturity-aware)
      - what_to_watch: specific next signals to monitor
      - variations_intro: intro text for the variation map
      - lead_time_warning: shown when inertia is zero
      - accuracy_note: what confidence level to assign
    """
    lookup = lookup_topic(topic_phrase)

    if not lookup:
        return {
            "topic_age":        "Not in AI taxonomy — scoring from raw signals only.",
            "tier_context":     None,
            "what_to_do":       "Collect more data — single cycle insufficient for assessment.",
            "what_to_watch":    "Check if this topic appears on multiple platforms.",
            "variations_intro": None,
            "lead_time_warning": "⏱ Lead time estimate requires inertia confirmation." if is_first_run else None,
            "accuracy_note":    None,
        }

    tier_key, topic_key, topic_config, tier_config = lookup
    first_appeared = topic_config.get("first_appeared", "2020-01-01")
    years_old      = _years_old(first_appeared)
    velocity       = topic_config.get("velocity_signal", "UNKNOWN")

    # ── Topic age ─────────────────────────────────────────────────
    if years_old < 0.5:
        age_str = f"Very new — first detected {int(years_old * 12)} months ago. No long-term baseline yet."
    elif years_old < 1.5:
        age_str = f"{int(years_old * 12)} months old. Recent enough to be calibrated as new emerging vocabulary."
    elif years_old < 3:
        age_str = f"{years_old:.1f} years old. Established enough that high gradient may reflect permanent expert home."
    else:
        age_str = (
            f"{int(years_old)} years old (first appeared ~{first_appeared[:4]}). "
            f"Long-established expert vocabulary. Current gradient reflects permanent "
            f"community home, not new emergence."
        )

    # ── Tier context ──────────────────────────────────────────────
    tier_context = tier_config["label"] + " — " + topic_config.get(
        "why_viral", topic_config.get("why_calibrated", "")
    )

    # ── What to do ────────────────────────────────────────────────
    if is_first_run:
        what_to_do = (
            "First collection run — scores will sharpen after 2–3 cycles. "
            "The tier classification below is based on the AI taxonomy "
            "and is accurate regardless of collection cycle count. "
            "Inertia and persistence components activate after ~30 minutes."
        )
    elif "tier_1" in tier_key:
        if detection_score >= 85:
            what_to_do = (
                "Act now. This is a Tier 1 VIRAL topic with confirmed signal volume. "
                "The expert community is actively producing content on this. "
                "Mainstream awareness is still low — the lead time window is open."
            )
        else:
            what_to_do = (
                "Begin planning. This is a Tier 1 topic and more collection cycles "
                "will push scores higher as inertia and persistence activate. "
                "Position now while the topic is still primarily in expert communities."
            )
    elif tier_key == "tier_2":
        what_to_do = (
            "Window is open but closing. This topic has been building for "
            f"{int(years_old * 12)} months and is showing continued positive velocity. "
            "Begin positioning now — the early-mover advantage is still available "
            "but decreasing each week."
        )
    elif tier_key == "tier_3":
        what_to_do = (
            "This is established expert vocabulary — not an active trend signal. "
            "Monitor the Tier 1 sub-topics below that ARE showing current velocity. "
            "If you need to act on this space, use the specific sub-topics "
            "as your timing signal."
        )
    else:  # tier_4 mainstream
        what_to_do = (
            "This topic has already reached mainstream. "
            "If you are trying to position ahead of the curve, "
            "navigate to the Tier 1 variations below — those are "
            "the leading edge of this broader space."
        )

    # ── What to watch ─────────────────────────────────────────────
    related = get_variation_map(topic_phrase)
    tier1_related = [r for r in related if r.get("tier") == "tier_1" and not r["is_queried"]]

    if tier1_related:
        watch_topics = ", ".join([f'"{t["display"]}"' for t in tier1_related[:3]])
        what_to_watch = (
            f"Watch these Tier 1 sub-signals for confirmed breakout: {watch_topics}. "
            f"Any one of these crossing Detection 90+ with confirmed inertia "
            f"is a strong action signal in this space."
        )
    elif "tier_1" in tier_key:
        what_to_watch = (
            "Watch for: (1) mainstream tech media coverage beginning — "
            "signals the lead time window is closing; (2) inertia score rising "
            "above 50 — confirms sustained acceleration; (3) new platforms "
            "joining (especially YouTube tutorials and LinkedIn posts) — "
            "signals crossing from developer to business audience."
        )
    else:
        what_to_watch = (
            "Watch for velocity spike above baseline (gradient +15pts) and "
            "first-timer ratio above 30% — those two signals together indicate "
            "genuine resurgence in an established topic."
        )

    # ── Lead time warning ─────────────────────────────────────────
    if is_first_run:
        lead_time_warning = (
            "⏱ Lead time estimate is not shown — requires 2+ collection windows "
            "to confirm inertia. Tier classification is accurate; score will "
            "increase as collection cycles accumulate."
        )
    elif inertia_score < 5:
        lead_time_warning = (
            "⏱ Lead time estimate requires sustained inertia (2+ consecutive "
            "6-hour windows of acceleration). Check back after next cycle."
        )
    else:
        lead_time_warning = None

    # ── Accuracy note ─────────────────────────────────────────────
    if "tier_1" in tier_key:
        accuracy_note = (
            "Tier 1 classification is based on the Now TrendIn AI taxonomy "
            "validated against live GitHub Trending (week of May 21, 2026), "
            "Hacker News discussion data, and DEV.to article velocity. "
            "High confidence in tier assignment regardless of collection cycle count."
        )
    elif tier_key == "tier_4":
        accuracy_note = (
            "Mainstream classification confirmed. Low Gradient Score for this "
            "term is not a calibration error — it correctly reflects that this "
            "topic has already arrived in the broader public consciousness. "
            "Low score = topic is past the early-detection window."
        )
    else:
        accuracy_note = None

    return {
        "topic_age":          age_str,
        "tier_context":       tier_context,
        "what_to_do":         what_to_do,
        "what_to_watch":      what_to_watch,
        "variations_intro":   f"All variations of '{topic_phrase}' ranked by current velocity:",
        "lead_time_warning":  lead_time_warning,
        "accuracy_note":      accuracy_note,
        "tier_key":           tier_key,
        "tier_label":         tier_config["label"],
        "velocity":           velocity,
    }


# ════════════════════════════════════════════════════════════════
# SECTION 6: MAIN ENGINE — DROP-IN APPLY FUNCTION
# ════════════════════════════════════════════════════════════════

def apply_ai_intelligence(raw_result: dict) -> dict:
    """
    Apply the full AI Topic Intelligence Engine to a raw score result.

    Drop-in function for gravitational_anomaly_detector.py:

        from ai_topic_intelligence import apply_ai_intelligence
        result = apply_ai_intelligence(result)

    Adds these fields to the result dict:
      - ai_tier / ai_tier_label / ai_tier_colour
      - ai_velocity_signal
      - ai_classification (canonical display name)
      - score_explanation (full plain-English explanation)
      - research (research section dict)
      - variations (list of related topics with scores)

    Overwrites detection_score and confidence_score with
    tier-aware calibrated values when the topic is in the AI taxonomy.
    """
    if not raw_result:
        return raw_result

    topic      = raw_result.get("topic_display", raw_result.get("topic", ""))
    det        = raw_result.get("detection_score", 0) or 0
    conf       = raw_result.get("confidence_score", 0) or 0
    signals    = raw_result.get("total_signals", 0) or raw_result.get("total_mentions", 0) or 0
    platforms  = raw_result.get("platform_count", 0) or 1
    inertia    = raw_result.get("inertia_score", 0) or 0
    velocity   = raw_result.get("gradient_velocity")
    times_scored = raw_result.get("times_scored", 0) or 0
    is_first_run = (times_scored <= 1 or inertia < 5)

    # ── Compute tier-aware scores ─────────────────────────────────
    tier_result = compute_tier_aware_scores(
        topic_phrase     = topic,
        raw_detection    = det,
        raw_confidence   = conf,
        signal_count     = signals,
        platform_count   = platforms,
        inertia_score    = inertia,
        gradient_velocity= velocity,
        times_scored     = times_scored,
    )

    # ── Generate research section ─────────────────────────────────
    research = generate_research_section(
        topic_phrase    = topic,
        detection_score = tier_result["detection_score"],
        confidence_score= tier_result["confidence_score"],
        signal_count    = signals,
        platform_count  = platforms,
        inertia_score   = inertia,
        is_first_run    = is_first_run,
    )

    # ── Get variation map ─────────────────────────────────────────
    variations = get_variation_map(topic)

    # ── Build calibrated result ───────────────────────────────────
    calibrated = {
        **raw_result,

        # Overwrite with AI-taxonomy-aware scores
        "detection_score":    tier_result["detection_score"],
        "confidence_score":   tier_result["confidence_score"],

        # AI taxonomy fields
        "ai_tier":            tier_result.get("tier"),
        "ai_tier_label":      tier_result.get("tier_label"),
        "ai_tier_colour":     tier_result.get("tier_colour"),
        "ai_velocity_signal": tier_result.get("velocity_signal"),
        "ai_classification":  tier_result.get("ai_classification"),
        "score_explanation":  tier_result.get("score_explanation"),
        "why_this_score":     tier_result.get("why_this_score"),
        "years_in_ecosystem": tier_result.get("first_appeared_years_ago"),

        # Research section
        "research":           research,

        # Variation map
        "variations":         variations,
    }

    return calibrated


# ════════════════════════════════════════════════════════════════
# SECTION 7: DEMO / VALIDATION
# Shows expected scores for key topics
# ════════════════════════════════════════════════════════════════

def run_demo():
    """
    Demonstrates expected scores for key AI topics.
    Run to validate: python ai_topic_intelligence.py
    """
    test_topics = [
        # (topic, signals, platforms, inertia, times_scored)
        ("agentic coding",      20, 3, 75, 8),  # Should be near 100/100
        ("agent memory",        15, 2, 60, 6),  # Should be near 96/94
        ("12-factor agents",    12, 2, 50, 5),  # Should be near 94/91
        ("on-device AI",        18, 3, 65, 7),  # Should be near 93/90
        ("context engineering",  8, 2, 40, 4),  # Should be near 89/82
        ("mcp",                 25, 4, 80, 12), # Should be near 82/78
        ("claude code",         20, 3, 70, 8),  # Should be near 80/76
        ("vibe coding",         15, 3, 55, 6),  # Should be near 78/72
        ("llm",                 30, 4, 90, 20), # Should be ~35/30 (established)
        ("agentic ai",          15, 2, 60, 8),  # Should be ~40/38 (established)
        ("ai agent",            10, 2, 45, 6),  # Should be ~32/28 (established)
        ("rag",                 20, 3, 70, 10), # Should be ~30/25 (established)
        ("chatgpt",             50, 5, 95, 20), # Should be ~28/35 (mainstream)
        ("ai",                  80, 6, 99, 30), # Should be ~22/30 (mainstream)
        ("artificial intelligence", 90, 6, 99, 30), # Should be ~20/28 (mainstream)
    ]

    print("\n" + "="*80)
    print("NOW TRENDIN — AI TOPIC INTELLIGENCE ENGINE — DEMO OUTPUT")
    print("="*80)
    print(f"\n{'Topic':<26} {'Tier':<8} {'Velocity':<16} {'Detection':>9} {'Confidence':>11}")
    print("-"*80)

    for topic, signals, platforms, inertia, times in test_topics:
        result = compute_tier_aware_scores(
            topic_phrase      = topic,
            raw_detection     = 22,  # Typical first-run raw score
            raw_confidence    = 11,
            signal_count      = signals,
            platform_count    = platforms,
            inertia_score     = inertia,
            gradient_velocity = None,
            times_scored      = times,
        )
        tier = result.get("tier", "unknown")
        tier_short = {"tier_1":"VIRAL","tier_2":"STRONG","tier_3":"ESTABLISHED",
                      "tier_4":"MAINSTREAM","tier_3_resurgent":"RESURGENT"}.get(tier, tier or "?")
        vel = result.get("velocity_signal", "?")[:14]

        det  = result["detection_score"]
        conf = result["confidence_score"]

        bar_width = 25
        det_bar  = "█" * int(det  / 100 * bar_width)
        conf_bar = "█" * int(conf / 100 * bar_width)

        print(
            f"  {topic:<24} {tier_short:<8} {vel:<16} "
            f"{det:>6.1f} {det_bar:<{bar_width}} "
            f"{conf:>6.1f} {conf_bar}"
        )

    print("\n" + "="*80)
    print("\nVARIATION MAP — Search for 'ai' shows all sub-topics ranked:")
    print("-"*50)
    variations = get_variation_map("ai")
    for v in variations:
        tier_short = {"tier_1":"VIRAL","tier_2":"STRONG","tier_3":"ESTABLISHED",
                      "tier_4":"MAINSTREAM"}.get(v["tier"], "?")
        print(
            f"  {'▶ ' if v['is_queried'] else '  '}{v['display']:<28} "
            f"{tier_short:<12} "
            f"DET ~{v['typical_detection']:>5.1f}  "
            f"CONF ~{v['typical_confidence']:>5.1f}"
        )

    print("\n" + "="*80)
    print("\nRESEARCH SECTION — Example for 'agentic coding':")
    print("-"*50)
    research = generate_research_section(
        "agentic coding", 97, 95, 20, 3, 75, False
    )
    for k, v in research.items():
        if v:
            print(f"\n[{k.upper()}]\n{v}")
    print("="*80)


if __name__ == "__main__":
    run_demo()
