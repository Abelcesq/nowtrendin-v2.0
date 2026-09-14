---
name: catchall-audit
description: NowTrendIn catch-all specialist — the dedicated daily monitor for the topic/post 'news'/general catch-all congestion. Reports catch-all %, corroboration-floor health, any tracked calls (ledger/pending) stuck in the catch-all, and the top lexicon-candidate terms to reclassify. Use when the user says "check the catch-all", "catch-all report", "why are topics in news", "what should be reclassified", "end of day catch-all", or runs the scheduled daily catch-all report.
---

# /catchall-audit — the catch-all specialist (block B3)

Runs the **Catch-All Auditor**, the agent dedicated to the topic/post catch-all
congestion. Unlike the topic-quality audit (which reports a single %), this one
produces a **worklist**: what's congesting the catch-all and exactly what to do.

**Engine (v2):** `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com` (public).

## Steps
1. Run the agent:
   ```bash
   curl -s --max-time 45 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/monitor/catchall
   ```
2. **Report** from `summary` (this is the end-of-day report body):
   - **Headline:** `catchall_pct` (`catchall_count` / `total_scored`) — track the
     trend vs prior days (improving = lexicon work landing).
   - **Floor health:** `single_source_catchall_leak` — single-source catch-all
     topics that slipped past the `floor_min_sources` corroboration floor. Should
     be ≈0. A climb means the floor is disabled (`CATCHALL_MIN_SOURCES`) or a
     re-score/purge is overdue.
   - **Misclassified tracked calls:** `misclassified_tracked` + examples — real
     accuracy-ledger / pending detections stuck in the catch-all. **Highest
     priority** — these are real signals the thin lexicon mis-sorted.
   - **Lexicon candidates:** `lexicon_candidates` (top meaningful terms) — the
     terms to add to `topic_categories._LEX` so those topics leave the catch-all.
3. **Act / recommend** (worst-first):
   - tracked calls in catch-all → add their anchor terms to the right `_LEX`
     category in `transfer/topic_categories.py`, re-score.
   - recurring lexicon candidates (e.g. dockerfile/kubernetes → technology;
     a league/club → sports) → add to `_LEX`, re-score, re-check the %.
   - floor leak → confirm `CATCHALL_MIN_SOURCES>=2` is set and re-score/purge.
4. **Verdict:** the catch-all % with its trend, the top 3–5 reclassification
   actions, and whether the floor is holding.

## End-of-day report format
When run on the daily schedule, output a short founder-facing summary:
> **Catch-all EOD — <date>**
> • Catch-all: X% (Y/Z scored) — ↑/↓ vs yesterday
> • Floor: holding (N leaks) / NEEDS ATTENTION
> • Tracked calls stuck in catch-all: N — [list]
> • Top reclassify targets: term1, term2, term3 …
> • Recommended action: …

## Integrity
NEVER force a topic into a category it doesn't match, and never drop a tracked
call (ledger/pending) — the floor already exempts them. Lexicon additions must be
genuine category terms (objectivity / measurement-not-advice). Part of the
monitoring fleet (see `/topic-quality-audit`, `/data-watchdog`,
DATA_BUILDING_BLOCKS.md block B3).

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
- **For THIS skill:** Catch-all corroboration floor — the planned M reweighting EXTENDS this exact ≥2-distinct-source philosophy from admission to WEIGHT (1 reputable = ½, full on ≥2 distinct reputable). Same distinct-source counting; watch that wire-syndication does not inflate the distinct count.
