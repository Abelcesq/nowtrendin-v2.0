---
name: accuracy-sweep
description: Run NowTrendIn's accuracy ledger validation cycle — sweep pending Google Trends detections, generate the honest hit-rate report (LED / (LED + same_day + lagged + false_positive)), and surface the lead-time distribution. The irreproducible moat. Use when the user says "run accuracy", "weekly accuracy", "sweep the ledger", "accuracy report", or asks how the engine is performing vs Google Trends.
---

# /accuracy-sweep — Honest accuracy ledger sweep + report

You run the weekly accuracy validation cycle and produce the honest hit-rate report.

**Engine URL**: `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com`
**Internal key**: `nt-internal-7f3a9c2e5b81`

## Steps

1. **Trigger the sweep** (internal-key gated POST):
   ```bash
   curl -s --max-time 60 -X POST https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/accuracy/validate -H "X-Internal-Key: nt-internal-7f3a9c2e5b81"
   ```
   Wait up to 60s for the response. The sweep validates pending detections against current Google Trends data.

2. **Pull the honest report**:
   ```bash
   curl -s --max-time 20 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/accuracy/ledger
   ```

3. **Report** in this exact structure:

   ### Detection volume
   Total detections recorded · Pending (not yet evaluable) · Evaluated

   ### Honest hit rate
   `LED / (LED + same_day + lagged + false_positive)` — the actual % where Now TrendIn called it BEFORE Google Trends. Include the raw counts so the denominator is visible.

   ### Lead-time distribution
   - Median days early on LED hits
   - P25 / P75 (if available)
   - Best-case lead time (longest)

   ### Failure modes
   - same_day count (we called it the day Google did — neutral)
   - lagged count (we called it AFTER Google — bad)
   - false_positive count (we called it, Google never confirmed — bad)

4. **Interpret the result**:
   - Hit rate ≥ 60% with median lead ≥ 3 days → Strong evidence the moat is real
   - Hit rate 40-60% → Real signal but inconsistent — investigate which themes lead vs lag
   - Hit rate < 40% → The accuracy claim is weak; do not market it externally until improved

5. **Persist a one-line entry** to `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\ACCURACY_LOG.md` (create if missing): `YYYY-MM-DD · hit_rate% · median_lead_days · N_evaluated`. This builds the longitudinal record over time.

## Important framing

This is the **irreproducible moat** — competitors can replicate the engine but can't replicate the time-stamped detection history. Be honest about results, never inflate numbers. A measured 55% with 4-day median lead is a real moat; a self-reported 90% with no denominator is a liability.

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
- **For THIS skill:** Accuracy Ledger — the canonical `signal_date` is the ledger's sort/match backbone; detection↔breakout matching now uses the same-surge floor (`since=detection−30d`). Read dates from `signal_date`, never re-derive from raw strings.
