# CATEGORY REVIEW — why "taco bell" shows Technology while the story is Health

**Asked by the founder 2026-07-18** (screenshot: Taco Bell BREAKOUT under Technology while the
AI Context correctly describes the cyclosporiasis/lettuce outbreak). Read-only investigation;
no change shipped. Scope note first: **the category is DISPLAY-ONLY navigation metadata** —
it never feeds the Gradient Score, the stage, or any ledger (CLAUDE.md §13); this is a
labeling defect, not a scoring defect.

## What was ruled out (each tested, not assumed)

1. **The bare-word lexicon (layer 3) is NOT the source.** Run locally against the deployed
   classifier: "taco bell", "taco", "tacoma", "taco bell lettuce", "lettuce taco" ALL return
   `general` (no lexicon hit at all). Nothing maps "taco" or "bell" to technology.
2. **Staleness is NOT the source.** `/monitor/catmaps` at review time: both override maps
   LIVE and fresh (situation 388 entries, refreshed 03:17 UTC; context 68,460 entries,
   refreshed 02:47 UTC). Technology is a current, live decision.
3. **The machinery CAN read this story correctly.** The same serve-time pipeline puts
   `lettuce_taco` under **Health** — and replicating the context layer on the actual news
   syndication (NPR/CNN/Time/CDC headlines via Google News RSS) classifies "taco bell" as
   **health, conf 0.562** (strong term "outbreak"), comfortably above the 0.35 floor.

## Root cause (two defects, one structural bias)

The Technology label comes from the OVERRIDE layers (`_SITUATION_CAT` checked first, then
`_CONTEXT_CAT`), and the current live map holds `taco_bell → technology`. The mechanism,
demonstrated concretely against the deployed classifier:

**D1 — SOURCE-COMPOSITION BIAS in the context builder.** `_refresh_context_categories` takes
each topic's **6 most-recent** `raw_signals.title` strings — whatever collector ran last —
and taco_bell's feed is bluesky-dominant (the detail rail shows "38 signals · bluesky"; the
mainstream-v2 probe confirms 51 signals, 19 news outlets, incl. kotaku.com). Social post text
is structurally tech-flavored because the technology WEAK lexicon now contains the platform
vocabulary of social chatter itself: `ai, app, google, youtube, meta, reddit, bsky, bluesky,
model, platform, update, launch`. Demonstration (synthetic blobs, marked illustrative):

| input text style | classifies as |
|---|---|
| bluesky-style chatter ("...AI drive thru... the app... google reviews") | **technology conf 0.75** (`ai, app, google`) |
| a single weak word ("taco bell app deals") | **technology conf 0.583** (`app`) |
| the actual news headline ("pulls lettuce after cyclospora outbreak") | **health conf 0.75** (`outbreak`) |
| chatter without tech words ("lettuce got people sick") | general 0.0 |

One incidental "app"/"ai"/"google" in six social posts is enough to cross the 0.35 confidence
floor and stamp the topic Technology — while the 19 news outlets carrying the outbreak story
never reach the classifier because only the 6 newest titles do.

**D2 — TIE-BREAK PRIORITY.** `_PRIORITY` ranks `technology` ABOVE `health`, so any tech-vs-
health tie resolves to Technology. Compounds D1.

**D3 (unconfirmed, lower likelihood) — situation-cluster inheritance.** The situation layer
is checked FIRST and "the largest situation a topic belongs to wins" for every member.
`/situations/search` is internal-key-gated, so whether taco_bell currently carries a
situation override could not be confirmed from outside. The all-Technology pattern across
taco/taco_bell/tacoma is consistent with either D1 applied per-key or one shared cluster.
(The outbreak cluster itself would likely vote `general` — taco-family displays have no
lexicon hits — and general situations are skipped, which points back to D1 as the driver.)

## Why the AI Context is right while the chip is wrong

The AI Context is Perplexity + Claude over the live open web at explainer time — it reads the
news. The category chip is a lexicon over our own 6 most-recent stored titles — it read the
chatter. Different inputs, honestly different answers; the defect is that the chip's input
window is composition-sensitive and its lexicon is chatter-biased.

## Recommended fixes (all DISPLAY-ONLY; none touch scoring; founder's call per flag-never-force)

- **F1 (root fix): tier-weight the context builder.** Prefer titles from news/mainstream-tier
  signals when present (e.g., classify news-tier titles first; fall back to social text only
  when no news titles exist in the window), and/or raise `heads_per_topic` so 6 social posts
  cannot crowd out 19 news outlets. Small change in `_refresh_context_categories`.
- **F2: de-bias the tech weak lexicon for HEADLINE context.** The platform words
  (`google/youtube/bluesky/bsky/reddit/meta/app/ai`) are correct for TOPIC-name matching
  ("youtube" the topic IS technology) but poisonous when matched inside social TEXT. Split
  matching: platform words count for the topic string, not the text blob — or exclude them
  from text-side matching.
- **F3: swap health above technology in `_PRIORITY`** (a public-health story losing a tie to
  "app" is the wrong default for an attention instrument).
- **F4 (hygiene): a per-topic category-provenance probe** (internal-gated) — this review took
  N probes because no endpoint says WHICH layer decided a topic's category; one
  `?explain=taco_bell` param on /monitor/catmaps would have answered it in one call.

**Nothing implemented** — this is the review the founder asked for. F1–F3 are small,
display-only, and testable against this exact case (taco_bell should flip to Health at the
next context refresh after F1/F2; lettuce_taco must stay Health as the regression check).
