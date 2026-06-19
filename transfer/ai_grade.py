"""
================================================================
NOW TRENDIN — AI GRADE MODULE
Propose a Gradient Score for a topic NOT in our data, using
open-web research + LLM synthesis.
================================================================

TWO-STAGE PIPELINE:
  1) RESEARCH  (Perplexity, search-native) — gathers current web
     evidence about the topic with citations.
  2) SYNTHESIS (Anthropic Claude) — maps that evidence onto the
     Gradient Score framework and returns a PROPOSED score with the
     reasoning + which evidence drove it.

Both are optional/independent: if only one key is set, the module
degrades gracefully. With neither, it returns available=False.

ENV:
  PERPLEXITY_API_KEY   — research stage
  ANTHROPIC_API_KEY    — synthesis stage
  AI_GRADE_PPLX_MODEL  — default "sonar"
  AI_GRADE_CLAUDE_MODEL— default "claude-sonnet-4-20250514"

The proposed score is clearly labelled PROPOSED — it is an AI
estimate from public web evidence, not a measured engine score.
"""

import os
import re
import json
import requests

try:
    from collector_health import log_api_call as _api
except Exception:
    def _api(*a, **k): pass

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY", "")
PPLX_MODEL   = os.getenv("AI_GRADE_PPLX_MODEL", "sonar")
CLAUDE_MODEL = os.getenv("AI_GRADE_CLAUDE_MODEL", "claude-sonnet-4-5-20250929")


def is_available() -> bool:
    return bool(PERPLEXITY_API_KEY or ANTHROPIC_API_KEY)


# ── Stage 1: RESEARCH (Perplexity) ──────────────────────────────────
_RESEARCH_PROMPT = (
    "You are a trend-intelligence researcher. Research the topic \"{topic}\" "
    "across the open web RIGHT NOW. Report, concisely:\n"
    "1. What it is and whether it is currently emerging, mainstream, or fading.\n"
    "2. Where the conversation is happening (niche/expert communities vs "
    "mainstream platforms like YouTube, news, Reddit, X).\n"
    "3. Whether expert/insider discussion is leading mainstream awareness, or "
    "it is already widely known.\n"
    "4. Momentum: is attention accelerating, flat, or declining?\n"
    "Cite sources. Do NOT invent specific quantitative metrics (star counts, "
    "'X new this week', percentages of a whole, user numbers) you cannot verify "
    "from sources — describe them qualitatively if unsure, and never give a total "
    "and a growth figure that are internally inconsistent."
)


_EXPLAINER_PROMPT = (
    "Explain the topic \"{topic}\" for a smart but non-expert reader. "
    "Return ONLY valid JSON, no prose, with two keys: "
    "\"short\" — 1-2 plain sentences saying what it is and why it matters; "
    "\"full\" — 3-5 short paragraphs in markdown covering what it is, the core "
    "problem it solves, and why it matters. Be accurate and current.\n\n"
    "STRICT RULES (this text is displayed next to a live, measured score, so it "
    "must never contradict the engine or invent data):\n"
    "- Do NOT state specific quantitative metrics you cannot verify (star counts, "
    "'73K new this week', 'X% of all commits', user/download numbers, market "
    "sizes). If unsure a figure is correct AND current, describe it qualitatively "
    "instead (e.g. 'rapidly growing adoption', not a made-up number). Never state "
    "a total and a growth figure that are internally inconsistent.\n"
    "- Do NOT assert the topic's current momentum or DIRECTION (accelerating, "
    "normalising, cooling, peaking, surging). The engine measures and reports "
    "velocity separately; describe what the topic IS and why it matters, not how "
    "fast it is moving right now."
)

# Source-aware variant: when we know HOW the word is actually appearing across the
# sources, define the SPECIFIC trend driving attention right now (e.g. "japan" in
# World-Cup blog posts = the national team's run, not the country in general) —
# never a generic dictionary definition of the bare word.
_EXPLAINER_CONTEXT_PROMPT = (
    "A trend-detection engine is currently surfacing the term \"{topic}\". Below "
    "is a sample of how it is ACTUALLY appearing right now — real headlines/posts "
    "and the platforms/communities they came from:\n\n"
    "{context}\n\n"
    "Using THIS evidence, explain what is driving attention to \"{topic}\" RIGHT "
    "NOW — the specific event, story, product, match, release, or controversy the "
    "sources point to. Do NOT give a generic dictionary definition of the bare "
    "word; if the sources show \"{topic}\" refers to a specific thing (a sports "
    "team's match, a company, a person, a launch), explain THAT specific thing.\n\n"
    "Return ONLY valid JSON, no prose, with two keys: "
    "\"short\" — 1-2 plain sentences on what is driving attention and why it "
    "matters; \"full\" — 3-5 short markdown paragraphs on what it is (in this "
    "context), what is happening, and why it matters.\n\n"
    "STRICT RULES (shown next to a live measured score — never contradict the "
    "engine or invent data):\n"
    "- Ground the explanation in the sample above; if the evidence is thin, say so "
    "qualitatively rather than inventing specifics.\n"
    "- Do NOT state unverifiable quantitative metrics (counts, percentages, "
    "user/market numbers).\n"
    "- Do NOT assert momentum/direction (accelerating, cooling, surging) — the "
    "engine reports velocity separately."
)


def explain_topic(topic: str, context: str = "") -> dict:
    """Evergreen plain-English explainer for a topic (cached/persisted by the
    caller). One Perplexity call → {short, full, citations}.

    When `context` is supplied (a sample of the real headlines/posts + their
    source platforms where this term is currently appearing), the explainer is
    SOURCE-AWARE: it defines the specific trend driving attention right now rather
    than a generic dictionary definition of the bare word — so "japan" surfacing
    from World-Cup blog posts is explained as the team's run, not the country."""
    if not PERPLEXITY_API_KEY:
        return {"available": False}
    ctx = (context or "").strip()
    prompt = (_EXPLAINER_CONTEXT_PROMPT.format(topic=topic, context=ctx[:2500])
              if ctx else _EXPLAINER_PROMPT.format(topic=topic))
    try:
        _api("perplexity")
        r = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                     "Content-Type": "application/json"},
            json={"model": PPLX_MODEL,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=45,
        )
        r.raise_for_status()
        data = r.json()
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        citations = data.get("citations", []) or []
        # Perplexity reports per-call cost in usage.cost.total_cost — capture it so
        # the engine can meter monthly AI-definition spend against the budget.
        cost = float(((data.get("usage") or {}).get("cost") or {}).get("total_cost", 0) or 0)
        _c = {"perplexity": cost, "anthropic": 0.0, "total": cost}
        parsed = _extract_json(content)
        if parsed and parsed.get("short"):
            return {"available": True, "short": str(parsed.get("short", ""))[:400],
                    "full": str(parsed.get("full", "")), "citations": citations, "cost": _c}
        # Fallback: model didn't return clean JSON — use the prose directly.
        return {"available": True, "short": content[:240], "full": content,
                "citations": citations, "cost": _c}
    except Exception as e:
        print(f"[ai_grade] explain error for '{topic}': {e}")
        return {"available": False, "error": str(e)}


_MOVEMENT_PROMPT = (
    'You are analysing why a topic\'s ATTENTION score has been {direction} on an '
    'attention-measurement platform. Detection = how early/strong the signal is; '
    'Confidence = how broadly it is confirmed across sources.\n\n'
    'Topic: "{topic}"\n'
    'Score movement (oldest to newest): {movement}\n\n'
    'Real recent coverage where this topic is appearing:\n{context}\n\n'
    'In 2-4 sentences, explain the most likely real-world reason attention is '
    '{direction} (specific events, news, releases, controversies). Ground every '
    'claim in the coverage above; do NOT speculate beyond it. This is measurement '
    'of attention, NOT financial, investment, or legal advice. '
    'Return ONLY JSON: {{"short": "<one-sentence headline>", "full": "<2-4 sentence explanation>"}}'
)


def analyze_movement(topic: str, movement: str, direction: str, context: str = "") -> dict:
    """Explain WHY a topic's score has been rising/falling/flat — one Perplexity
    call, grounded in the real movement + coverage. Caller caches + meters."""
    if not PERPLEXITY_API_KEY:
        return {"available": False}
    prompt = _MOVEMENT_PROMPT.format(topic=topic, movement=movement[:600],
                                     direction=direction, context=(context or "")[:2200])
    try:
        _api("perplexity")
        r = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                     "Content-Type": "application/json"},
            json={"model": PPLX_MODEL, "messages": [{"role": "user", "content": prompt}]},
            timeout=45,
        )
        r.raise_for_status()
        data = r.json()
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        citations = data.get("citations", []) or []
        cost = float(((data.get("usage") or {}).get("cost") or {}).get("total_cost", 0) or 0)
        _c = {"perplexity": cost, "anthropic": 0.0, "total": cost}
        parsed = _extract_json(content)
        if parsed and parsed.get("short"):
            return {"available": True, "short": str(parsed.get("short", ""))[:300],
                    "full": str(parsed.get("full", "")), "citations": citations, "cost": _c}
        return {"available": True, "short": content[:200], "full": content,
                "citations": citations, "cost": _c}
    except Exception as e:
        print(f"[ai_grade] movement analysis error for '{topic}': {e}")
        return {"available": False, "error": str(e)}


def research_topic(topic: str) -> dict:
    """Perplexity web research. Returns {available, summary, citations}."""
    if not PERPLEXITY_API_KEY:
        return {"available": False, "summary": "", "citations": []}
    try:
        _api("perplexity")
        r = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                     "Content-Type": "application/json"},
            json={
                "model": PPLX_MODEL,
                "messages": [{"role": "user", "content": _RESEARCH_PROMPT.format(topic=topic)}],
            },
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        summary = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        citations = data.get("citations", []) or []
        cost = float(((data.get("usage") or {}).get("cost") or {}).get("total_cost", 0) or 0)
        return {"available": True, "summary": summary, "citations": citations, "cost": cost}
    except Exception as e:
        print(f"[ai_grade] perplexity error: {e}")
        return {"available": False, "summary": "", "citations": [], "cost": 0.0, "error": str(e)}


# ── Stage 2: SYNTHESIS (Claude → proposed Gradient Score) ────────────
# Engine component weights (must match velocity_scores schema). The AI estimates
# the COMPONENTS; we compute detection/confidence with these exact weights so the
# AI score lands on the SAME scale as engine-collected signals. N (query count)
# is 0 for a topic that has never been queried.
_DET_W  = {"G": 0.33, "D": 0.19, "I": 0.16, "M": 0.09, "C": 0.05, "P": 0.06, "N": 0.12}
_CONF_W = {"I": 0.25, "P": 0.24, "M": 0.20, "G": 0.11, "C": 0.06, "D": 0.04, "N": 0.10}

_SCORE_SYSTEM = (
    "You are the scoring engine for Now TrendIn's Gradient Score — an instrument "
    "that measures where human attention is moving BEFORE it arrives. From web "
    "research you ESTIMATE the underlying COMPONENTS (the app computes the final "
    "Detection/Confidence from them, so estimate the components honestly).\n\n"
    "Components (all 0-100):\n"
    "- niche_concentration (G): niche/expert concentration vs mainstream. HIGH = "
    "experts talking, public hasn't caught on (early). LOW = already mainstream.\n"
    "- platform_diversity (M): how many distinct platforms carry the signal.\n"
    "- momentum (I): acceleration of attention (rising vs flat vs declining).\n"
    "- dark_matter (D): hidden early-insider activity ahead of the crowd.\n"
    "- persistence (P): how sustained/established the topic is over time. A brand-"
    "new spike = low P; a topic with long, steady, broad coverage = high P.\n"
    "- freshness (C): how current the signal is right now (recency of coverage).\n\n"
    "Guidance: an EARLY topic has high niche_concentration + low persistence. An "
    "already-MAINSTREAM topic (e.g. a household name) has LOW niche_concentration "
    "but HIGH persistence and platform_diversity.\n\n"
    "Return ONLY valid JSON, no prose, with keys: niche_concentration, "
    "platform_diversity, momentum, dark_matter, persistence, freshness (numbers "
    "0-100), stage (one of BREAKOUT, STRONG, EMERGING, WATCHING, MONITORING), "
    "action (short imperative), reasoning (2-4 sentences citing the evidence), "
    "classification (ONE of: 'mainstream' = already widely known across general "
    "platforms; 'emerging' = expert/insider attention leading mainstream, crossing "
    "over now; 'niche' = confined to specialist/expert communities; 'fading' = past "
    "its peak), and reach_note (1 sentence on WHERE the conversation lives and "
    "whether experts lead the public — the basis for the classification). "
    "Optionally also include holistic_detection and holistic_confidence (0-100) — "
    "your own direct read, which the app shows alongside the computed score."
)


def _composite(c: dict, weights: dict) -> float:
    return round(sum(c.get(k, 0.0) * w for k, w in weights.items()), 1)


def propose_score(topic: str, research_summary: str) -> dict:
    """Claude synthesis → proposed score dict. Returns {available, ...score} ."""
    if not ANTHROPIC_API_KEY:
        return {"available": False}
    user = (
        f"Topic: \"{topic}\"\n\n"
        f"Web research:\n{research_summary or '(no external research available)'}\n\n"
        "Estimate the Gradient Score components now as JSON."
    )
    try:
        _api("claude")
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY,
                     "anthropic-version": "2023-06-01",
                     "Content-Type": "application/json"},
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": 1024,
                "system": _SCORE_SYSTEM,
                "messages": [{"role": "user", "content": user}],
            },
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        # Cost from token usage (Claude Sonnet 4.5: $3/M input, $15/M output).
        usage = data.get("usage") or {}
        cost = (usage.get("input_tokens", 0) / 1e6) * 3.0 + (usage.get("output_tokens", 0) / 1e6) * 15.0
        parsed = _extract_json(text)
        if parsed is None:
            return {"available": False, "error": "Could not parse model output", "cost": cost}
        parsed["available"] = True
        parsed["cost"] = round(cost, 6)
        return parsed
    except Exception as e:
        print(f"[ai_grade] claude error: {e}")
        return {"available": False, "error": str(e), "cost": 0.0}


def _extract_json(text: str):
    """Pull the first JSON object out of a model response."""
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


# ── Orchestration ───────────────────────────────────────────────────
def grade_topic(topic: str) -> dict:
    """Full AI grade: research → propose score. Returns the combined payload."""
    if not is_available():
        return {"available": False,
                "reason": "AI grading not configured (set PERPLEXITY_API_KEY / ANTHROPIC_API_KEY)."}

    research = research_topic(topic)
    score = propose_score(topic, research.get("summary", ""))

    if not score.get("available"):
        return {
            "available": bool(research.get("available")),
            "topic": topic,
            "proposed": False,
            "research": research.get("summary", ""),
            "citations": research.get("citations", []),
            "detail": score.get("error", "Scoring synthesis unavailable."),
        }

    # AI-estimated components, mapped to the engine's component letters.
    comps = {
        "G": _num(score.get("niche_concentration")),
        "M": _num(score.get("platform_diversity")),
        "I": _num(score.get("momentum")),
        "D": _num(score.get("dark_matter")),
        "P": _num(score.get("persistence")),
        "C": _num(score.get("freshness"), 50.0),
        "N": 0.0,  # never queried before
    }
    # Detection/Confidence computed with the ENGINE's weights → same scale as
    # collected signals.
    detection  = _composite(comps, _DET_W)
    confidence = _composite(comps, _CONF_W)

    return {
        "available": True,
        "proposed": True,
        "topic": topic,
        # Engine-calibrated composites (authoritative for display consistency)
        "detection_score":   detection,
        "confidence_score":  confidence,
        "heisenberg_gap":    round(detection - confidence, 1),
        # Components (same names the app/engine breakdown uses)
        "gradient_strength":  comps["G"],
        "platform_diversity": comps["M"],
        "inertia":            comps["I"],
        "dark_matter":        comps["D"],
        "persistence":        comps["P"],
        "freshness":          comps["C"],
        # Claude's own holistic read, shown alongside (labeled "AI estimate")
        "holistic_detection":  _num(score.get("holistic_detection"), detection),
        "holistic_confidence": _num(score.get("holistic_confidence"), confidence),
        "stage":  score.get("stage", "MONITORING"),
        "action": score.get("action", ""),
        "reasoning": score.get("reasoning", ""),
        # Internet-researched mainstream/niche read (from the open web, not our pool).
        "classification": str(score.get("classification") or "").lower() or None,
        "reach_note": score.get("reach_note", ""),
        "research": research.get("summary", ""),
        "citations": research.get("citations", []),
        "provenance": "ai_grade:perplexity+claude (engine-weighted)",
        "cost": {
            "perplexity": round(float(research.get("cost", 0) or 0), 6),
            "anthropic":  round(float(score.get("cost", 0) or 0), 6),
            "total":      round(float(research.get("cost", 0) or 0) + float(score.get("cost", 0) or 0), 6),
        },
    }


def _num(v, default=0.0):
    try:
        return round(float(v), 1)
    except Exception:
        return default
