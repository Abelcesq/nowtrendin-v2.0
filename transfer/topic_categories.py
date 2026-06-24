"""
================================================================
NOW TRENDIN — TOPIC CATEGORY CLASSIFIER
================================================================

WHY THIS EXISTS:
  With the open-world discovery feeds (Phase A) the topic pool exploded
  from ~50 tech items to the full breadth of human attention (sports,
  entertainment, politics, …). Every topic currently serves with
  category "General", which makes the larger pool impossible to
  navigate. This module assigns each topic one of the canonical
  Now TrendIn 1.0 content categories so the UI can sort/filter by WHAT
  a trend is about — orthogonal to the signal-STAGE axis (Breakout /
  Emerging / Anomaly) the engine already produces.

THE 12 CANONICAL CATEGORIES (from Now TrendIn 1.0):
  business, economy, education, entertainment, current_events, fashion,
  health, news, sports, politics, religion, technology
  (+ "general" as the honest fallback when nothing matches)

DESIGN:
  - Deterministic keyword/lexicon classifier. Free, fast, no model
    dependency on Heroku, fully explainable.
  - Scores every category by weighted keyword hits, returns the best
    plus a confidence and the matched terms (for debugging / display).
  - Accepts optional `hints` (e.g. Wikipedia article categories, source
    section) which are trusted MORE than raw keyword matching — this is
    the upgrade path to high accuracy without a model.

INTEGRITY:
  This is METADATA only. Category never feeds the Gradient Score — it
  just labels topics for navigation. No circular metrics.
================================================================
"""

import re

CATEGORIES = [
    "business", "economy", "education", "entertainment", "current_events",
    "fashion", "health", "news", "sports", "politics", "religion", "technology",
]

# Human-readable labels for the UI.
CATEGORY_LABELS = {
    "business": "Business", "economy": "Economy", "education": "Education",
    "entertainment": "Entertainment", "current_events": "Current Events",
    "fashion": "Fashion", "health": "Health", "news": "News", "sports": "Sports",
    "politics": "Politics", "religion": "Religion", "technology": "Technology",
    "general": "General",
}

# ── Lexicons ───────────────────────────────────────────────────────
# Each category maps to (strong_terms, weak_terms). Strong terms are
# high-precision and weighted 3×; weak terms are weighted 1×. Phrases
# match on word boundaries; multi-word phrases match as substrings.

_LEX = {
    "sports": (
        # strong — almost never anything but sports
        ["fifa", "world cup", "nba", "nfl", "mlb", "nhl", "olympic", "olympics",
         "premier league", "la liga", "bundesliga", "serie a", "champions league",
         "super bowl", "ufc", "mma", "grand slam", "wimbledon", "f1", "formula 1",
         "world series", "playoffs", "world ranking", "national football team",
         # unambiguous franchise names (Catch-All Auditor lexicon candidates)
         "knicks", "celtics", "lakers", "mavericks", "nuggets", "warriors nba"],
        # weak — sports-ish, can appear elsewhere
        ["soccer", "football", "basketball", "baseball", "hockey", "tennis",
         "golf", "boxing", "cricket", "rugby", "cycling", "match", "league",
         "tournament", "championship", "coach", "striker", "midfielder",
         "goalkeeper", "athlete", "medal", "fixture", "transfer", "squad"],
    ),
    "technology": (
        ["llm", "gpt", "openai", "anthropic", "claude", "chatgpt", "gemini",
         "nvidia", "spacex", "starship", "satellite", "semiconductor", "quantum",
         "agentic", "machine learning", "artificial intelligence", "blockchain",
         "cryptocurrency", "github", "iphone", "android", "cybersecurity",
         "malware", "data breach", "software", "algorithm", "robotics"],
        ["ai", "app", "chip", "rocket", "tesla", "ev", "robot", "crypto",
         "bitcoin", "ethereum", "coding", "programming", "developer", "startup",
         "gadget", "cloud", "server", "api", "hack", "cyber", "tech", "device",
         "launch", "update", "platform", "model",
         # dev/AI tooling that fell into the catch-all (Catch-All Auditor candidates)
         "streamlit", "fastapi", "copilot", "kubernetes", "dockerfile", "pytorch",
         "langchain", "bioinformatics", "semantic search", "prompt engineering",
         "diffusion model", "object detection", "vector database", "hugging face",
         # unambiguous tech entities (Catch-All Auditor candidates 2026-06-23)
         "google", "bsky", "bluesky"],
    ),
    "politics": (
        ["election", "president", "senate", "congress", "parliament",
         "white house", "supreme court", "prime minister", "impeachment",
         "democrat", "republican", "campaign trail", "ballot", "governor",
         "legislation", "sanctions", "diplomacy"],
        ["vote", "government", "policy", "minister", "campaign", "senator",
         "politician", "law", "bill", "deal", "summit", "treaty", "cabinet",
         "regulation", "court",
         # unambiguous political figures (Catch-All Auditor candidates)
         "trump", "biden", "harris", "putin", "zelensky", "netanyahu", "starmer",
         "modi", "macron", "obama"],
    ),
    "business": (
        ["ipo", "merger", "acquisition", "earnings", "quarterly results",
         "layoffs", "bankruptcy", "valuation", "venture capital", "private equity",
         "stock split", "shareholder", "ceo", "startup funding"],
        # NOTE: "deal" deliberately NOT here — it routed geopolitical "X deal"
        # (Iran deal, trade deal, peace deal) to Business. M&A is still caught by
        # the strong list (ipo/merger/acquisition) + "merge".
        ["company", "stock", "market", "shares", "revenue", "profit", "brand",
         "retail", "funding", "investor", "business", "corporate", "firm",
         "executive", "merge"],
    ),
    "economy": (
        ["inflation", "interest rate", "federal reserve", "gdp", "recession",
         "unemployment rate", "trade deficit", "tariff", "treasury yield",
         "central bank", "fiscal policy", "monetary policy"],
        ["economy", "jobs report", "tariffs", "trade", "currency", "dollar",
         "bond", "debt", "tax", "wages", "prices", "growth"],
    ),
    "entertainment": (
        ["box office", "netflix", "hbo", "disney+", "grammy", "oscar", "oscars",
         "academy award", "billboard", "blockbuster", "tv series", "music video",
         "movie premiere", "celebrity", "reality show"],
        ["movie", "film", "show", "series", "music", "album", "song", "concert",
         "actor", "actress", "singer", "rapper", "band", "streaming", "trailer",
         "premiere", "hollywood", "comedy", "drama", "tour"],
    ),
    "health": (
        ["vaccine", "covid", "pandemic", "outbreak", "cancer", "alzheimer",
         "fda approval", "clinical trial", "mental health", "public health",
         "epidemic", "obesity", "diabetes"],
        ["health", "disease", "virus", "drug", "medical", "hospital", "doctor",
         "patient", "medicine", "therapy", "diet", "fitness", "wellness",
         "infection", "symptom", "treatment"],
    ),
    "fashion": (
        ["met gala", "fashion week", "haute couture", "runway show", "vogue"],
        ["fashion", "style", "designer", "runway", "couture", "outfit",
         "wardrobe", "sneaker", "streetwear", "apparel", "clothing", "model"],
    ),
    "education": (
        ["university", "college admission", "tuition", "scholarship",
         "student loan", "curriculum", "standardized test", "phd"],
        ["school", "student", "exam", "degree", "professor", "academic",
         "education", "campus", "graduation", "teacher", "classroom"],
    ),
    "religion": (
        ["the vatican", "the pope", "ramadan", "easter", "passover",
         "pilgrimage", "archbishop", "papal"],
        ["church", "mosque", "temple", "pope", "bible", "quran", "faith",
         "prayer", "religious", "christian", "muslim", "jewish", "hindu",
         "buddhist", "clergy", "worship", "synagogue"],
    ),
    "current_events": (
        ["earthquake", "hurricane", "wildfire", "mass shooting", "terror attack",
         "plane crash", "mid-air collision", "natural disaster", "state of emergency",
         "evacuation", "nuclear deal", "peace deal", "ceasefire", "war crimes"],
        ["protest", "disaster", "flood", "fire", "crash", "shooting", "attack",
         "crisis", "emergency", "rescue", "storm", "explosion", "accident",
         "kidnapping", "murder", "missing",
         # geopolitics / conflict — genuinely current-events (and what made
         # "iran deal" land in Business via the bare "deal" keyword)
         "war", "conflict", "missile", "strike", "troops", "military", "border",
         "refugee", "hostage", "coup", "invasion", "nuclear", "sanctions",
         "iran", "israel", "gaza", "ukraine", "syria", "hamas", "hezbollah",
         "taiwan", "north korea", "geopolitical",
         "china", "russia", "russian", "venezuela", "lebanon", "yemen", "sudan",
         # demonyms + the Iran/Hormuz chokepoint cluster (Catch-All Auditor candidates).
         # NOTE: bare peaceful countries (australia/canada/france…) are deliberately NOT
         # added — a country alone is multi-category; the SITUATION layer routes them by
         # context (canada+hockey→sports, canada+election→politics).
         "iranian", "israeli", "chinese", "strait of hormuz", "hormuz", "juneteenth"],
    ),
    # "news" and "general" are fallbacks — no lexicon; assigned when nothing
    # else scores. "economy"/"business" and "politics"/"current_events" overlap
    # by design; tie-breaking prefers the more specific category (order below).
}

# Tie-break priority: more specific / higher-signal categories win ties.
_PRIORITY = ["sports", "technology", "health", "fashion", "religion",
             "education", "entertainment", "economy", "business",
             "politics", "current_events", "news"]


def _count_hits(text: str, terms: list[str]) -> tuple[int, list[str]]:
    hits = []
    for t in terms:
        if " " in t or "-" in t or "+" in t:
            if t in text:
                hits.append(t)
        else:
            if re.search(rf"\b{re.escape(t)}\b", text):
                hits.append(t)
    return len(hits), hits


def classify_topic(topic: str, text: str = "", hints=None) -> dict:
    """
    Classify a topic into one of the 12 canonical categories.

    topic : the topic string (e.g. "2026 FIFA World Cup")
    text  : optional extra context (headline, related news, raw_text)
    hints : optional list of trusted category strings (e.g. Wikipedia
            article categories, source section). Matched against lexicons
            with extra weight — the high-accuracy upgrade path.

    Returns: {category, label, confidence (0-1), matched: [...]}
    """
    blob = f"{topic} {text}".lower().strip()
    if not blob:
        return {"category": "general", "label": "General", "confidence": 0.0, "matched": []}

    scores: dict[str, float] = {}
    matched: dict[str, list[str]] = {}
    for cat, (strong, weak) in _LEX.items():
        s_n, s_hits = _count_hits(blob, strong)
        w_n, w_hits = _count_hits(blob, weak)
        score = s_n * 3 + w_n
        if score:
            scores[cat] = score
            matched[cat] = s_hits + w_hits

    # Hints (trusted source metadata) add strong weight to any category
    # whose name/label appears in them.
    if hints:
        hint_blob = " ".join(str(h) for h in hints).lower()
        for cat in _LEX:
            if cat.replace("_", " ") in hint_blob or CATEGORY_LABELS[cat].lower() in hint_blob:
                scores[cat] = scores.get(cat, 0) + 5
                matched.setdefault(cat, []).append(f"hint:{cat}")
        # common hint synonyms → category
        for syn, cat in {"sport": "sports", "film": "entertainment",
                         "movie": "entertainment", "musician": "entertainment",
                         "politician": "politics", "scientist": "technology",
                         "company": "business", "disease": "health"}.items():
            if syn in hint_blob:
                scores[cat] = scores.get(cat, 0) + 5
                matched.setdefault(cat, []).append(f"hint:{syn}")

    if not scores:
        return {"category": "news", "label": "News", "confidence": 0.15, "matched": []}

    top = max(scores.values())
    winners = [c for c, v in scores.items() if v == top]
    if len(winners) > 1:
        winners.sort(key=lambda c: _PRIORITY.index(c) if c in _PRIORITY else 99)
    best = winners[0]

    total = sum(scores.values())
    confidence = round(min(1.0, (top / total) * (0.5 + min(top, 6) / 12)), 3)
    return {"category": best, "label": CATEGORY_LABELS[best],
            "confidence": confidence, "matched": matched.get(best, [])}


if __name__ == "__main__":
    samples = [
        "2026 FIFA World Cup", "FIFA Men's World Ranking", "spacex",
        "Initial public offering of SpaceX", "iran announce deal", "llm",
        "agentic coding", "Oliver Tree", "Victor Wembanyama",
        "2026 Rio de Janeiro mid-air collision", "Met Gala 2026",
        "inflation cools as Fed holds rates", "new cancer vaccine trial",
        "the pope visits", "university tuition rises", "Taylor Swift new album",
        "Japan", "Ecuador", "security situation",
    ]
    for s in samples:
        r = classify_topic(s)
        print(f"  {s:<42} -> {r['label']:<14} ({r['confidence']:.2f})  {r['matched'][:4]}")
