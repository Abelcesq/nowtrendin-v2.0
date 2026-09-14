---
name: trend-signal-diagnostic
description: NowTrendIn Trend Signal (Gradient Score) calibration diagnostic — read-only agent that audits ONE topic's score (saturation, N-discipline reconcile on the expert pathway, what-if-N inversion, frozen range) plus a cross-topic distribution check (is Confidence/Detection actually separating topics). Use when the user says "why is <topic> scored this way", "is the gradient score saturated", "is N leaking into the headline", "are topics unrankable", "trend calibration", or doubts a Gradient Score.
---

# /trend-signal-diagnostic — make the Gradient Score explain itself (read-only)

The devoted agent for **Gradient Score calibration**, twin of the market one. Changes
nothing. It audits the real failure modes the live view surfaced.

**Engine (v2):** `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com`

## Steps
1. One topic:
   ```bash
   curl -s --max-time 60 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/diagnostic/trend/<topic>
   ```
   Cross-topic distribution:
   ```bash
   curl -s --max-time 60 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/diagnostic/trend-distribution?limit=30
   ```
2. **Report** the per-topic `verdict` · `detection_pathway` · `score_saturated` ·
   component `value`/`headroom_pct`/`status` · `reconcile` · `whatif_n` · `issues`;
   and the distribution `detection_sd`/`confidence_sd`/`ceiling_pinned`/`confidence_collisions`.
3. **Verdicts & fixes:**
   - **SATURATED / FROZEN** — top topics pinned at 100 (can't rank #1 vs #2). FIX: soften
     the binding ceilings (component caps AND final-score cap) — soft/log compression near the top.
   - **UNDOCUMENTED_INPUT** — *(expert pathway only)* headline Detection sits ABOVE what
     G/I/M/D/C justify → a term outside the five (N? the undocumented P?) may be leaking into
     the HEADLINE. Governance check: N must NEVER feed the headline.
   - **WHATIF_N_INVERTED** — the demand-inclusive read moves DOWN when N is high (e.g. Musk
     N 94 → Det+N 49). FIX: make the blend monotonic in N, or retire the block.
   - **Distribution:** if Confidence collapses many topics onto one value, re-scale Confidence
     so volume/precision differences move it.

## Why it's gated to the expert pathway (important)
The engine is **dual-pathway**: mainstream/news topics are scored on magnitude+breadth,
NOT the G/I/M/D/C gradient formula. So the N-leak reconcile only runs on `detection_pathway
== expert` — otherwise it would false-flag every mainstream topic. (Saturation, frozen,
what-if-N, and distribution checks are formula-independent and always run.)

## Mission & integrity (every run obeys)
Read-only — never writes a score. Mission: keep every Gradient Score a defensible, **N-free**,
discriminating read — the basis of the product's credibility. Findings cite exact
values/headroom/gaps, never guesses. Detection/Overall weights are confirmed from the
engine; Confidence weights are intentionally OFF (ambiguous in the runtime — we won't
assert an unverified number). Twin of `/market-signal-diagnostic`; part of the monitoring fleet.

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
- **For THIS skill:** Trend signal diagnostic — detection/breakout dates are canonical `detection_date`/`breakout_date`; the same-surge floor (`since=detection−30d`) governs ledger matching. Never naive-split date strings.
