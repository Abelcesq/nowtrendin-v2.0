---
name: project-dark-matter-routing
description: "The D-vs-M router is platform_tier (NOT is_organic). Route early-signal/research sources via blog_collectors expert/niche tier, never _news_write (forces mainstream → suppresses the early signal). Plus the reputable→½/full-on-corroboration reweighting in design."
metadata: 
  node_type: memory
  type: project
  originSessionId: 365856a3-a15a-4e81-b551-17dcfef7ec5c
---

**The Dark-Matter (D) vs Mainstream (M) router is the `platform_tier` column — NOT
`is_organic`.** Mapped across the engine 2026-06-22 (`gravitational_anomaly_detector.py`,
`dual_pathway.py`). Verified mechanism:

- `platform_tier="mainstream"` → feeds M (dual_pathway breadth/magnitude), lands in
  Gradient-Strength **G's denominator** (compute_gradient_strength), and raises the
  dual-pathway blend weight `w` → tells the engine the topic has ALREADY arrived =
  **suppresses the early read.**
- `platform_tier in {"expert","niche"}` → the Dark-Matter / expert-gradient pathway:
  zero mainstream breadth, `w`~0, lands in G's **numerator**. This is "before it arrives."
- `is_organic` only scales D's quality gate (`quality = 0.4 + 0.6·organic_ratio`);
  `is_first_timer` is D's numerator (`compute_dark_matter`). NEITHER routes M-vs-D.

**GOTCHA I hit:** I first validated the research feeds (War on Rocks, Rest of World,
Global Issues, Pew, RAND-blog, NBER) for `_RSS_FEEDS` / `collect_rss_news`. That path
calls `_news_write`, which stamps reputable sources `tier="mainstream"` — which would
have SUPPRESSED the very early signal the founder wants. **Correct home = the blog
template:** add them to `blog_collectors.py` GHOST_FEEDS at `tier="expert"/"niche"`
(is_organic=True, honest first-timer via `_first_timer` author history). The founder
explicitly framed these as "like blog sites that research and surface topics before
mainstream" — the blog collector IS the route.

**Also in design (not shipped, gated by backtest-before-ship):** reputable ≠ automatic
mainstream FULL weight. New rule: 1 reputable source = **½ weight**; FULL weight only on
**≥2 DISTINCT reputable sources** (count distinct `source_name`, not rows — wire copy
syndicated across 5 sites is ONE source). The "Belgium vs Iran, 2026 World Cup" case.
Extends the catch-all corroboration floor (`CATCHALL_MIN_SOURCES≥2`) from admission to
WEIGHT.

**Why:** crediting a research/analysis outlet as reputable-mainstream is the precise
failure mode that kills the "before it arrives" thesis — it reads as diffusion, not
early signal. **How to apply:** never add early-signal/research outlets to
`_NEWS_REPUTABLE_SOURCES` or `_news_write`; route via expert/niche tier. Before shipping
either M/D change, run `backtest_dual_pathway.py` (B5 hard rule) and an adversarial
integrity pass. Full spec lives in CLAUDE.md §15 + DATA_BUILDING_BLOCKS.md §5. Validated
feeds (prod UA): War on Rocks 40, Rest of World 12, Global Issues 10, Pew 40, RAND-blog
20, NBER 29. Related: [[project-gradient-calibration]], [[feedback-no-circular-metrics]],
[[feedback-integrity-standard]], [[serve-payload-cache-gotcha]].
