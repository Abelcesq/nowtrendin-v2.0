---
name: topic-quality-audit
description: NowTrendIn topic-quality monitor — checks for news-filler/multi-word headline fragments ("iran deal", "leaders meet"), geo/country topics mis-sorted into Business/Economy, and category-sorting clarity. Keeps the category views clean and sources accurate. Use when the user says "check topic quality", "any fragments", "are categories accurate", "audit the trends list", or after changing extraction/NEWS_FILLER/the category classifier.
---

# /topic-quality-audit — fragments + geo/category sorting (block B3 deep)

Runs the Topic Quality Auditor so the trends/category views stay clean and the
sources read accurately. Catches the three failure modes that make the list messy:
1. **News-filler / multi-word fragments** — headline clauses, not topics
   ("iran deal", "says iran deal", "leaders meet").
2. **Geo/country mis-sorts** — geopolitics in Business/Economy when it belongs in
   current-events/politics (the "iran deal → Business" bug class).
3. **Category clarity** — too many topics dumped in the 'news'/general catch-all.

**Engine (v2):** `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com` (public).

## Steps
1. Run the auditor:
   ```bash
   curl -s --max-time 30 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/monitor/quality
   ```
2. **Report** from `summary` + `alerts`:
   - `sampled` · `fragments` (count + examples) · `geo_missorted` (count + examples)
   - `news_catchall_pct` — % in the catch-all (high = thin sorting)
3. **Diagnose** each finding to the fix (DATA_BUILDING_BLOCKS.md §11):
   - fragments → extend `NEWS_FILLER` and/or the `_is_quality_topic` multi-word
     anchor check in `transfer/gravitational_anomaly_detector.py` (enforced at
     extraction AND serve); re-score to clear stored rows.
   - geo mis-sorts → `transfer/topic_categories.py` `_LEX`: keep ambiguous terms
     ("deal") out of Business; ensure geo/conflict terms route to current_events.
   - high catch-all % → add lexicon coverage for the under-sorted topics.
4. **Verdict:** clean (say so) or list the specific fragments/mis-sorts to fix,
   worst-first. Never force/inject topics (integrity guardrail B6/objectivity).

## Discipline
Code-truth: cite the exact fragments/mis-sorted topics from the live response.
A clean run = clear, accurately-sourced category views. Part of the monitoring
fleet (see `/data-watchdog`, DATA_BUILDING_BLOCKS.md block B3).

## Canonical dates · sources · M/D — updated 2026-06-22

> Cross-cutting updates every data/scoring skill should know. Authoritative specs:
> `CLAUDE.md` §14–15, `DATA_BUILDING_BLOCKS.md` §3a + §5.

- **Canonical date model (✅ LIVE):** PRIMARY `signal_date` = ISO `YYYY-MM-DD` (the ONE
  sort/match/score key); SECONDARY `source_time` (the SOURCE's own HH:MM:SS) + `signal_time`
  (OUR fetch HH:MM:SS, stamped on every fetched row). Enforced by `date_utils` +
  `ingestion_gate.gate_date()`; an unparseable non-empty value → `format_review_queue`
  (human review), never guessed. Same-surge ledger floor `since=detection−30d`. Governs
  SORT/MATCH only — removes NO scoring input. Never reintroduce raw `[:10]` date slicing.
- **New sources (✅ LIVE):** reputable-direct RSS roster incl. **The New Yorker** (news+business);
  **Nasdaq Trade Halts** in the risk module (stage-2; `signal_date`=HaltDate, `source_time`=HaltTime).
- **M/D reweighting (⏳ IN DESIGN — NOT shipped; backtest-before-ship gates it):** reputable ≠
  automatic mainstream full weight — 1 reputable = ½ weight, FULL only on ≥2 DISTINCT reputable
  (distinct `source_name`; the "Belgium vs Iran" case). Research/early-signal outlets (War on
  Rocks, Rest of World, Global Issues, Pew, RAND, NBER) → Dark Matter via `blog_collectors`
  GHOST_FEEDS at **expert/niche tier** — the D-vs-M router is `platform_tier`, NOT `is_organic`;
  do NOT route them through `_RSS_FEEDS`/`_news_write` (which forces `mainstream` and suppresses
  the early signal).
- **For THIS skill:** Topic quality — date-semantic writes must pass `ingestion_gate` (no corrupt/guessed dates; junk-date rows quarantine to `format_review_queue`). New sources feed the same quality + fragment gate.
