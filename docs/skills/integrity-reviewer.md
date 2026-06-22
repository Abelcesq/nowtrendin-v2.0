---
name: integrity-reviewer
description: NowTrendIn integrity gate — reviews any new data source, metric, scoring change, or public-facing claim against the 5 hard guardrails (objectivity, no circular metrics, licensed sources, measurement-not-advice, never assert what we can't support). Block 6 of DATA_BUILDING_BLOCKS.md. Use BEFORE shipping a new source/metric/UI claim, when the user says "integrity check", "is this OK to ship", "review this for integrity", or proposes a new data source or marketing number.
---

# /integrity-reviewer — the 5-guardrail ship gate (block B6)

A GATE, not a poller. Run it on any **new data source, metric, scoring change, or
public-facing claim** before it ships. If anything fails, **block it and propose
the clean alternative** — do not soften. (Founder hard rule.)

## The 5 guardrails — every item must pass ALL

1. **Gradient-Score objectivity.** Nothing flows *upstream* into the score that
   contaminates it; validators sit downstream (read-only). **No force-injected /
   always-on topics** (that fakes detection). Derived internal signals (e.g. N
   demand) already feeding it are the ceiling — add no more.

2. **No circular metrics.** A validator must use inputs INDEPENDENT of what it
   validates. (Caught live: "does N agree with the score" is circular — N is
   inside the score.) State the independence in code + UI copy.

3. **Reputable, licensed sources only.** Commercially licensed + authoritative
   publisher. Banned until written approval: Reddit, Guardian-as-primary,
   CoinGecko, Messari. When in doubt, leave OFF and flag.

4. **Measurement, not advice.** Outputs describe exposure/positioning/cycle —
   never buy/sell/will-grow. Every financial output carries the
   not-investment-advice disclaimer.

5. **Never assert what we can't support.** No published performance/accuracy/scale
   number without a real, **denominator-backed** source. No hardcoded marketing
   stats. "Illustrative" labels on sample/mock data. If live data isn't there yet,
   remove the claim or show the honest value WITH its denominator.

## Steps
1. Restate what's being added/claimed in one line.
2. Walk all 5 guardrails; for each: PASS / FAIL + one-line why.
3. **Verdict:** SHIP (note which guardrails it respected) or BLOCK (name the
   failing guardrail + the clean alternative). Any single FAIL ⇒ BLOCK.

## Examples of correct BLOCKs (from this project)
- Login "73% accuracy / 11d lead" hardcoded while the ledger was 0%-on-5 → BLOCK
  (G5) → removed; show denominator-backed or nothing.
- Force-scoring SpaceX so it always appears → BLOCK (G1 objectivity) → fix the
  collection so it surfaces organically instead.
- Market tiers fudged so everything isn't ROUTINE → BLOCK (G5) → at-baseline is
  honestly ROUTINE; restore the real input gap instead.

## Discipline
Surfacing the risk IS the job. Investor-grade truth over a prettier demo. Related:
`DATA_BUILDING_BLOCKS.md` §6, the `feedback-integrity-standard` memory.

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
- **For THIS skill:** Provenance integrity (the gate) — enforce: reputable ≠ automatic mainstream full weight (½ → full on ≥2 distinct reputable); research/early-signal outlets must route to Dark Matter via expert/niche tier (`platform_tier` is the D-vs-M router, NOT `is_organic`). FLAG any attempt to add them to `_NEWS_REPUTABLE_SOURCES`/`_news_write` (forces mainstream = suppresses early signal). Both M/D changes are gated by backtest-before-ship.
