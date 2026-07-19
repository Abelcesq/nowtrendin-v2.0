# COHORT REPLAY VERIFICATION — the median-of-12 baseline-flip mechanism (board item 3)

**Mandate:** Chairman-ruled item 3 of BOARD_q1q2-cliff-plateau_2026-07-18.md — verify, cohort-wide
and read-only, that the cliff/plateau/flap behavior across the 19 volatility topics is the
dual-pathway blend weight `w` moving, not the attention data. Enabled by board item 2 (the
embedded `score_history` now serves per-cycle `mainstream_ratio` (w), `detection_pathway`,
`attention_magnitude`, `n_mainstream_platforms`). Script: scratchpad `median_replay.py`
(raw output: `median_replay_raw.json`). Method: for every |Δdet| ≥ 30 single-cycle transition
in each topic's served 30-cycle history, check whether the STORED w / pathway / median-of-prior-12
moved at that exact cycle.

## RESULT: MECHANISM CONFIRMED — 49 of 50 transitions (98%)

Every topic with cliffs shows the same signature: the ~30–79-point single-cycle moves coincide
exactly with `mainstream_ratio` snapping between its saturation points (predominantly 1.0 ↔ 0.0)
and `detection_pathway` flipping mainstream ↔ expert. Highlights:

- **spain** — all four 94↔25 toggles are w flips: +70.1 (w 0→1.0), −69.2 (1.0→0), +67.0
  (0→0.967), −69.2 (1.0→0). The bistability the Challenger observed IS the weight oscillating.
- **tillis** — +75.8 on w 0→1.0; −78.7 on w 1.0→0 at the exact cycle its magnitude median
  caught up (5.56→99.71) — the textbook baseline-catchup cliff (7th-cycle flip, as predicted).
- **google** — EIGHT confirmed w transitions in 30 cycles (0↔1.0↔0.633…), the marginal-deviation
  flapper: an instrument serving BREAKOUT and MONITORING alternately on a topic whose median
  inputs barely move.
- **jordan / cyclosporiasis_cases / amnesty / japan(07-15)** — down-cliffs land on the cycle the
  magnitude median jumps up (0→69.26, 0→49.37, 0→61.33, 59.18→93.84): the topic's own surge
  filling the 12-cycle baseline window until deviation collapses.

**The one honest exception:** japan 2026-07-18T04 (−48.4) with w 1.0→1.0, pathway
mainstream→mainstream, medians flat — a mainstream-pathway-INTERNAL drop not explained by the
blend weight. Logged for the (held) item-6 backtest to examine; 1/50 does not change the verdict.

## What this settles

1. The cliffs/plateaus/flaps are **estimator dynamics, not attention dynamics** — the board's
   framing correction stands: the LEVEL after a cliff is defensible (baseline-relative deviation
   ended); the SHAPE (full-height single-cycle release, and google-class oscillation at the
   boundary) is manufactured by the integer-median/threshold discontinuity in
   `w = max(breadth_factor, magnitude_factor)`.
2. The **item-6 remedy locus is confirmed** (continuous baseline estimator + hysteresis at the
   w boundary) — but item 6 is **HELD by the Chairman**; nothing in this replay licenses touching
   it. When/if the founder revisits, this file + `median_replay_raw.json` are the backtest's
   "before" evidence.
3. The 07-19 falsifiable predictions (mamdani/taco/cyclosporiasis_outbreak cliff at ~07-19T10
   UTC; russia at ~07-19T16, absent renewed expansion) remain **PENDING** — those cycles had not
   run at replay time. Check the next assessor run or re-run the replay after 07-19T17 UTC.

*Read-only throughout; zero writes, zero engine surface. 2026-07-19 ~02:5x UTC.*
