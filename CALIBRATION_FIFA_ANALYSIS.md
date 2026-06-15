# Calibration Analysis — Why the FIFA World Cup Is Invisible to NowTrendIn
*2026-06-15 · founder-internal*

## TL;DR
The World Cup (started 06/11/2026) does not appear because NowTrendIn is, in its
current implementation, a **technology/AI attention engine — not a general-culture
one**. Sports falls outside its sensory range at **three independent layers**, each
sufficient on its own to make FIFA invisible. This is a *coverage + calibration*
gap by construction, not a bug. Separately, a scheduled mega-event like the World
Cup is a poor fit for a "pre-viral early detector" anyway — the real early-sports
signals are things like breakout players and transfer rumors, not the tournament itself.

## Empirical confirmation (live engine, 2026-06-15)
- `/trending` top topics: `fable`, `scaffolding` (AI/dev), `white house ufc`,
  `iran announce deal` (hard news/politics). **Zero** sports/soccer/FIFA topics.
- `/topics?q=fifa|soccer|world cup|football|messi` → all return the *same default
  list* (the `q` filter is not applied). No sports topic exists to match.
- Note: news **is** ingested (it caught "iran deal", even "ufc" from a headline) —
  so the gap is sports *coverage + salience*, not "news is off".

## Root causes (with evidence)

### Layer 1 — Collector coverage is ~95% AI/tech by construction
Every discovery surface is an AI/dev publication:
- `blog_collectors.py`: DEV.to tags (`ai, machinelearning, llm, python…`), Hashnode
  search terms (`llm, ai agent, rag…`), Discourse instances (HuggingFace, PyTorch,
  FastAI), newsletters (Ben's Bites, The Batch, Latent Space, Wired **AI**), Ghost
  feeds (Import AI, The Gradient). All AI.
- Core collectors in `gravitational_anomaly_detector.py` are GitHub + Hacker News
  (developer-only) + Reddit (now removed).
- **No open-world "what is trending right now" feed exists.** Google Trends is wired
  via `pytrends.interest_over_time()` on *topics the engine already has*
  (`research_history.py`) and Apify Google Trends is used to *validate existing
  topics* (`backend/accounts/views.py:275`) — it is never asked for the trending-
  searches list (which would return the World Cup instantly).

→ The engine essentially never *reads* sports content.

### Layer 2 — Topic-extraction salience is tech-only
`DOMAIN_TERMS` (103 entries) and all 5 `COMPOUND_PATTERNS` in
`gravitational_anomaly_detector.py` (and mirrored in `blog_collectors.py`) boost
**only** AI/ML vocabulary (`AI|LLM|ML|model|agent|framework|protocol`). Sports terms
get no domain boost and survive only as generic n-grams.

**Calibration test (ran the engine's real `extract_topics_from_text`):**

| Headline | domain-boosted | extracted (sample) |
|---|---|---|
| "FIFA World Cup 2026 kicks off as USA beats Mexico…" | **[]** | `2026 kicks off`, `off usa`, `beats mexico opening`, `fifa world`, `world` |
| "Messi scores twice as Argentina cruises past opener…" | **[]** | `argentina`, `opener`, `cruises past opener`, `scores` |
| "World Cup fever grips North America…" | **[]** | `world cup fever`, `fever grips north`, `ticket sales` |
| "New open source LLM agent framework beats GPT-4 on agentic coding" | **[agent, agentic coding, llm, gpt, open source llm]** | `llm agent`, `agentic coding`, `agent framework` |

→ Sports text disintegrates into low-salience noise fragments; tech text is
canonicalized and amplified.

### Layer 3 — Scoring is calibrated for expert→mainstream *tech* diffusion
The gravitational score rewards: appearance on **expert dev platforms**, high
**first-timer ratio in dev communities**, and "still expert, not yet mainstream".
`ai_topic_intelligence.py` further applies an **88–100 score floor** to taxonomy AI
topics. A sports event is consumer-origin and already mainstream, so even if
extracted it scores near the bottom. Non-AI topics are explicitly labeled
"Not in AI taxonomy — scoring from raw signals only."

### Bonus — entity resolution is weak for everything, fatal for non-tech
Even the tech headline fragments (`beats gpt-4`, `gpt-4 agentic`), but tech is
*rescued* by `DOMAIN_TERMS` canonicalization. Sports has no rescue, so fragments
("announce deal end", "beats mexico opening") never consolidate into one
high-volume "World Cup" topic that could cross the anomaly threshold.

## The "dark matter chatter" question, answered honestly
Within its domain (AI/dev/tech), the architecture **is** genuinely an early-detector:
expert-platform first-timer signals + velocity + diffusion-stage migration are a real
pre-viral mechanism. That is the moat. But it is **domain-locked to tech.** It is not
currently picking up general-culture "dark matter" because it never ingests it and
would shred + under-score it if it did.

## Solutions (tiered by effort)

### A. Add open-world discovery feeds (highest leverage, ~days)
Category-agnostic "what's trending now" sources, independent of seed lists:
1. **Google Trends Daily/Realtime Trending Searches** (Apify actor or RSS
   `trends.google.com/trends/trendingsearches/daily/rss?geo=US`) — would surface
   "World Cup" the day it spikes. *Single highest-ROI fix.*
2. **Wikipedia pageview spikes** (free API) — breakout-entity detector across all topics.
3. **YouTube trending** (mostRopular endpoint, category-agnostic), **GDELT** top
   themes (already partially present), **news top-headlines** (un-seeded, all categories).
4. **Bluesky/Mastodon firehose sampling** (already collected — broaden beyond tech reposts).

### B. De-bias extraction / add domain packs (~days)
- Make `DOMAIN_TERMS` **pluggable per domain** (sports, entertainment, politics,
  finance) instead of AI-only — or neutralize the tech-only salience advantage.
- Replace tech-regex `COMPOUND_PATTERNS` with proper **NER** (spaCy / a small model)
  so "FIFA World Cup", "Lionel Messi", "Club World Cup" resolve as single entities.
- Add an **entity-canonicalization** pass so fragments collapse to one topic.

### C. Domain-aware scoring (~1–2 weeks)
- Add a **second velocity track for consumer-origin trends** (mainstream platforms,
  pageview/search velocity) so non-tech trends aren't penalized by the
  expert-platform/first-timer weighting.
- Gate the AI-taxonomy 88–100 floor to AI searches only (it currently biases the
  global ranking).

### D. Strategic decision (prerequisite for B/C)
Decide scope: **(i)** stay a focused tech/finance attention engine and *honestly scope
the marketing* ("we measure emerging tech & market attention"), or **(ii)** become a
general-culture attention platform (matches the "where human attention is moving"
tagline) — which requires A + B + C and a broader collector budget.

## Recommended first step
Ship **A1 (Google Trends Trending-Searches discovery feed) + B (NER entity
resolution)** behind a flag, then re-run this calibration test. That combination is
the minimum that would let the World Cup — and any non-tech breakout — appear at all.
Do **not** market general-culture detection until a calibration test shows non-tech
topics surfacing and scoring sensibly.
