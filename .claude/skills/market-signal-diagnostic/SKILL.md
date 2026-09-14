---
name: market-signal-diagnostic
description: NowTrendIn Market Signal calibration diagnostic — read-only agent that audits ONE instrument's market score (baseline depth, stdev-floor binding, provenance, tier-vs-deviation contradiction) and returns a verdict. Catches cold-start artifacts like SPCX. Use when the user says "why is <ticker> scored this way", "is the market score real", "market calibration", "diagnose <symbol>", "is this a cold start", or doubts a Market Signal read.
---

# /market-signal-diagnostic — make the Market score explain itself (read-only)

The devoted agent for **Market Signal scoring calibration**. It changes nothing — it
opens one instrument's score and answers four questions: (1) how many baseline
history points each of the 7 components actually used, (2) whether the 0.05 stdev
floor is fabricating the z instead of real data, (3) which inputs are real, and
(4) whether the "UNUSUAL/+X%" deviation flag contradicts a quiet tier.

**Engine (v2):** `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com`

## Steps
1. Run it for an instrument:
   ```bash
   curl -s --max-time 60 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/diagnostic/market/<symbol>
   ```
   (e.g. `spacex`)
2. **Report** from the JSON: `verdict` · `median_baseline_depth` · `floor_binding` (k/7)
   · `tier_deviation_clash` · per-component `n_history`/`z`/`status` · `recompute` ·
   `issues` · `recommendation`.
3. **Verdicts:**
   - **INSUFFICIENT_HISTORY** — baseline too thin; z is floor-fabricated. The score is a
     cold-start artifact. FIX: emit `baseline forming` instead of a confident tier (and
     optionally score cross-sectionally vs the sector/IPO cohort during cold start).
   - **DATA_GAP** — ≥4 component sources missing; don't score, hold the instrument.
   - **CONTRADICTION** — UNUSUAL deviation flag next to ROUTINE/DORMANT; reconcile the
     deviation detector with the tier classifier.
   - **VALID** — supportable on depth + provenance.

## Mission & integrity (every run obeys)
Read-only — never writes or changes a score. Its job is to keep every Market Signal a
**defensible read of real data**: a cold-start instrument must read "baseline forming",
never a confident ROUTINE the data can't support. Recommendations cite the exact
baseline depth / floor-binding / contradiction — never a guess. This protects the
brand's credibility with institutional users. Uses the engine's REAL weights
(`market_signal_engine.DETECTION_WEIGHTS/CONFIDENCE_WEIGHTS`), not hardcoded numbers.
Twin of `/trend-signal-diagnostic`; part of the monitoring fleet.

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
- **For THIS skill:** Market signal diagnostic — `market_signal_history` now carries `signal_date` (primary) + `signal_time`; sort/match on `signal_date`. The date model changes nothing about leverage/positioning inputs.
