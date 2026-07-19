# VOLATILITY DIAGNOSTIC — Board-ruled batched read-only investigation (2026-07-18)

**Mandate:** Chairman ruling on board gate item A (BOARD_assessor-2026-07-17.md): one batched,
read-only, endpoints-only diagnostic over the 19 volatility-flagged topics from assessor
snapshot #1 — co-movement test first, volume-stratified, with the sign-flip (surge-vs-flap)
discriminator the std check lacks. Zero writes, zero engine surface. Script: scratchpad
`volatility_diag.py`; window = the 6 cycles available at diagnosis time (2026-07-17T16 →
2026-07-18T22 UTC; the snapshot's own window ended 2026-07-17T22 — one day earlier, same regime).

## Verdict in one line

**None of the three competing hypotheses fully held. The 19 flags reduce to ONE systemic
behavior: burst-plateau-cliff.** Topics ride a flat high plateau for 2–4 cycles after a surge,
then fall off a cliff (one cycle, e.g. tillis 88.4→9.7, spain 94.3→25.1, jordan 83.0→21.6) —
or step UP the same way (mamdani 24.7→89.9, taco 15.3→80.9). There is NO sawtooth flapping:
17 of 19 topics show ≤2 sign-flips over the window; the only genuine alternator is **america**
(71→52→78→43, 3 flips). The "single flapping source" framing of the original 19 items is
REFUTED; the "one systemic bad cycle" hypothesis (Outsider/Economist) is PARTIALLY refuted —
transitions cluster WITHIN cycles but are staggered ACROSS four different cycles, which is the
signature of per-topic input-recency rolloff after the 2026-07-16/17 news wave, not of a single
restart/cold-cache event.

## Evidence

### 1. Raw 6-cycle detection series (old → new; cycle timestamps UTC)

| topic | series | shape |
|---|---|---|
| spain | 91.96, 94.25, **25.1**, 25.5, 25.6, 25.3 | cliff DOWN at 07-18T04 |
| mamdani | 24.7, **89.9**, 89.95, 89.9, 90.0, 90.0 | step UP at 07-17T22 |
| white_house | 80.68, 80.68, 80.68, 49.61, **25.0**, 24.5 | cliff DOWN at 07-18T10→16 |
| andy_burnham | 63.47, 63.47, 63.47, 63.47, 63.57, 63.64 | now FLAT (std 0.1) |
| shutting | 94.55, 94.55, 94.55, 94.55, **47.01**, 22.0 | cliff DOWN at 07-18T16→22 |
| japan | 93.97, 93.97, **45.57**, 38.39, 38.45, 23.6 | stepped decay from 07-18T04 |
| rikers | 95.86, 96.31, 96.48, 96.64, 94.48, 94.2 | now FLAT-high (std 1.0) |
| jordan | 83.04, 83.04, 83.04, **21.6**, 22.0, 22.0 | cliff DOWN at 07-18T10 |
| google | 81.93, 81.93, 77.73, **27.2**, 59.21, 27.2 | cliff + one rebound (07-18T10/16) |
| cyclosporiasis_outbreak | 54.17, **83.76**, 83.4, 83.1, 82.8, 82.63 | step UP at 07-17T22 |
| youtube | 74.19, 74.19, 56.67, 39.71, 22.9, 22.3 | gradual decay from 07-18T04 |
| cyclosporiasis_cases | 78.2, 78.9, 79.6, **26.4**, 13.1, 13.3 | cliff DOWN at 07-18T10 |
| amnesty | 86.88, 86.88, 86.88, **38.47**, 13.6, 13.1 | cliff DOWN at 07-18T10→16 |
| america | 71.1, 71.13, 52.57, 52.54, 78.08, 43.38 | ALTERNATOR (3 flips) |
| russia | 70.86, 70.86, **88.32**, 88.36, 88.36, 83.77 | step UP at 07-18T04 |
| tillis | 88.37, 88.37, 88.37, 88.37, **9.7**, 9.2 | cliff DOWN at 07-18T16 |
| texas | 69.33, 69.33, 69.27, 69.27, 69.27, **52.8** | step DOWN at 07-18T22 |
| trump_fires | 70.24, 73.49, 65.27, 61.05, 56.68, 39.41 | gradual decay |
| taco | 15.3, **80.88**, 81.08, 81.08, 81.22, 81.31 | step UP at 07-17T22 |

### 2. Co-movement (the Outsider/Economist test): PARTIAL, staggered

Transition-cycle clustering (hour buckets): step-UPs concentrate in the **2026-07-17T22** cycle
(mamdani, taco, cyclosporiasis_outbreak); step-DOWNs spread across **07-18T04** (spain, japan),
**07-18T10** (jordan, google, cyclosporiasis_cases, amnesty start, white_house start),
**07-18T16** (tillis, shutting start), **07-18T22** (texas). 10 of 19 topics sit at their
window minimum in the newest cycle (the news wave receding). This is NOT the single-shared-
trough signature of a deploy/restart artifact — it is per-topic rolloff, staggered by when
each topic surged. The one systemic element: transitions land ON cycle boundaries and are
near-vertical.

### 3. The two findings that survive as real engine questions (diagnosis only — no action
without founder + backtest; any remedy is SCORE_AFFECTING)

- **Q1 — CLIFF DECAY:** scores transition 60–79 points in a single 6-h cycle (tillis 88.4→9.7)
  rather than decaying smoothly. Consistent with a hard input-recency window boundary (surge
  inputs aging out all at once). If real, every bursty topic will manufacture a volatility flag
  ~24h after its surge, forever. Whether cliff decay is the DESIRED representation of a burst's
  end is a founder-level measurement-design question, not a defect per se — the engine may be
  honestly reporting that the inputs vanished.
- **Q2 — IDENTICAL-PLATEAU REPEATS:** plateaus repeat to 0.01 precision across successive
  cycles while `scored_at` advances (white_house 80.68×3, shutting 94.55×4, tillis 88.37×4,
  jordan 83.04×3, andy_burnham 63.47×4). Fresh rescoring on moving inputs producing byte-
  identical values 3–4 times in a row suggests either component saturation/quantization or
  history rows recording served-stored values rather than fresh computations. Endpoints cannot
  distinguish these; an engine-side look is the next step if the founder wants one.

### 4. Instrument gap found while running (feeds the v2.1 assessor patch)

`/scores/{key}` `score_history` serves `total_mentions: null` on every row — the per-cycle
input-volume diagnostic the original 19 items prescribed is IMPOSSIBLE from the endpoint, and
B.freeze's "inputs static too" null-condition silently never sees mentions (explains its 8
INSUFFICIENT). The assessor must record this as a cause-coded limitation; adding mentions to
score_history rows is a small engine change (measurement/display-only) if the founder wants
the diagnostic to be runnable.

### 5. Volume strata

The cliff pattern spans strata — thin (tillis 8 mentions/2 platforms, 88→9) and thick (spain
105/13, 94→25) behave identically in shape; thin topics simply fall further. Volume does not
explain the volatility; burst timing does. The board's thin-vs-thick debate is settled by the
data: BOTH strata were riding the same news-wave burst.

## Disposition of the original items 1–19 (per the Chairman's ruling A)

CLOSED as 19 individual tickets. Survives as TWO diagnostic questions (Q1 cliff decay, Q2
identical plateaus) + one assessor-patch requirement (shape-aware volatility: flag alternators
like america; classify monotone step/burst shapes as expected burst dynamics) + one optional
engine enhancement (mentions in score_history). All OPERATIONAL except any actual scoring
change arising from Q1/Q2, which is SCORE_AFFECTING (founder + held-out backtest +
serve_payload regeneration).
