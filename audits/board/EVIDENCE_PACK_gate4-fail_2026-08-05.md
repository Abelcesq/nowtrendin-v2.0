# EVIDENCE PACK — Gate 4 first-pass FAIL, CRYPTO_ETF_FLOW flip blocked (2026-08-05 PT, late)

## What is being decided (neutral statement)

The Chairman ordered the CRYPTO_ETF_FLOW=1 flip (the crypto ETF share-flow vote entering the
crypto Money Movement leg). Per protocol, the just-deployed reconciliation harness
(`transfer/etf_flow_reconcile.py`, spec §8 gate 4 / amendment A1.5+F7 — the LAST unbuilt flip
gate) ran its FIRST live pass before any config change. It returned **gate_status: FAIL**.
The flip was NOT executed. The board is asked to analyze the first-pass results and rule on:

- **(a) Harness join fix** — the harness compares derived Δshares (keyed to the strike's
  `snapshot_date`) against the issuer-published flow for the SAME calendar date, but strikes
  are captured 00:00–06:00 UTC (prior US evening) and ETF shares settle T+1, so derived[D]
  reflects trades from D−1/D−2. The harness's own pre-declaration names "the disclosed ±1-day
  UTC smear" an "expected artifact class" — but the comparison logic never implements it.
  Question: is amending the verifier's date-matching AFTER seeing first failures legitimate
  (implementing the declared smear = completing the harness to its own spec), or is it
  post-hoc goalpost-moving that requires a new spec id per F7? What exact matching rule
  should be adopted (lag-aware match? multi-day cumulative windows? exclude the still-moving
  latest day?), and must it be pre-declared before the next scored pass?

- **(b) Derived-leg source** — the share counts feeding `etf_share_snapshots` come from FMP's
  `etf/info` (`fmp_data.etf_info` in `transfer/etf_flow.py snapshot()`). First-pass evidence
  (below) shows this source fails §16 gate 4 CURRENCY at daily resolution: IBIT frozen 4+
  days through ~$282M of published inflows; FBTC zigzagging ±5M shares against published
  flows never exceeding ±$55M. Note `etf_flow.py`'s own header (written 2026-07-29) states
  CURRENCY was NEVER proven: "nobody has yet shown these share counts actually move day to
  day at a usable resolution." Question: replace or supplement the source? Candidates:
  issuers' own product pages (iShares/Fidelity publish daily shares outstanding —
  official/direct, §15-compliant, needs full §16 5-gate onboarding). CIRCULARITY TRAP named:
  Farside is the REFEREE/comparator — using it as the data source would have the verifier
  verifying itself. Is there any acceptable interim (e.g., keep FMP but require value-change
  freshness proof per fund-day)?

- **(c) Flip timeline** — the ~08-10 flip target. What evidence standard re-arms the flip
  (how many clean PASS days on a currency-grade source? does the shadow-vote observation
  clock restart when the source changes?), and does CRYPTO_LEDGER_CLEAN_COHORT_START /
  CRYPTO_SERIES_EPOCH handling change?

Also under review: **the results of the (blocked) flip attempt** — i.e., the first-pass gate
report itself, including whether the harness verdicts, honest-absence states, and monitoring
wiring behaved as designed.

## First-pass gate report (live, /diag/etf-reconcile?run=1, 2026-08-06T01:54Z)

- checked=34 · pass=2 · fail=4 · immaterial=12 · no_published=16 · no_comparator: XRP
- material_comparisons=6 · gate_status=**FAIL** · bias_flags=none
- Band (F7, pre-declared at n=0): materiality floor max($10M, 0.05% AUM); direction
  mandatory on material days; magnitude ±25% or ±$20M (more forgiving); ≥5 consecutive
  same-sign errors fail even in band.
- Open failures:
  | date | ticker | derived | published |
  |---|---|---|---|
  | 2026-07-30 | IBIT | −$47.0M | +$183.4M |
  | 2026-07-31 | FBTC | −$29.5M | −$54.8M |
  | 2026-08-05 | FBTC | −$153.0M | +$11.3M |
  | 2026-08-05 | HODL | +$0.08M | −$14.7M |
- Passes: BITB ×1, ETHA ×1. XRP funds honestly no_comparator (Farside page verified 404).
- The `etf_reconcile_watch` monitor agent is now firing in the fleet (by design — a
  divergence fires forever, not a one-time pre-flip ceremony).

## Published comparator series (Farside, fetched live 2026-08-06, $M)

| date | FBTC | IBIT | HODL |
|---|---|---|---|
| 07-28 | 0.0 | −54.8 | 0.0 |
| 07-29 | −43.1 | +89.8 | 0.0 |
| 07-30 | +15.5 | +183.4 | +2.3 |
| 07-31 | −54.8 | −122.7 | 0.0 |
| 08-03 | +33.4 | +111.4 | +4.5 |
| 08-04 | +19.6 | +170.3 | 0.0 |
| 08-05 | +11.3 | (not yet published) | −14.7 |

## Raw derived-leg strikes (engine DB `etf_share_snapshots`, read live)

FBTC (nav in $): 07-29 184,376,690 @55.43 → 07-31 183,846,020 @55.59 (Δ −530,670 = −$29.5M)
→ 08-01 181,334,270 @56.36 (Δ −2,511,750 = −$141.6M) → 08-02 186,564,430 @54.78
(Δ +5,230,160 = +$286.5M) → [flat 08-03/08-04] → 08-05 183,812,940 @55.60 (Δ −2,751,490 =
−$153.0M) → 08-06 182,728,420 @55.93 (Δ −1,084,520 = −$60.7M).

IBIT: 07-29 1,298,671,200 @36.08 → 07-30 1,297,372,500 @36.22 (Δ −1,298,700 = −$47.0M) →
[flat] → 08-02 1,304,652,500 @35.66 (Δ +7,280,000 = +$259.6M) → **FROZEN 08-02 through
08-06** (same shares AND same nav=35.66 across 5 daily rows).

HODL: 08-01 58,862,080 @17.81 → [flat] → 08-05 58,866,608 @18.07 (Δ +4,528 = +$0.08M) →
08-06 59,115,344 @18.18 (Δ +248,736 = +$4.5M).

Capture times: all strikes land 00:00–06:00 UTC (= prior US evening ET), except the first
(07-29 17:48 UTC, intraday). Big Δs land on WEEKEND dates (08-01, 08-02) where the
comparator has no row → 16 of 34 checks NO_PUBLISHED.

## Freshness cross-check (etf_share_observations — 4h looks, table new as of the A1 deploy)

Three live pulls tonight (08-06 00:44, 01:43, 02:02 UTC): IBIT identical all three —
shares 1,304,652,500, nav 35.66 (the SAME values since 08-02) while FBTC's nav struck
normally tonight (55.60→55.93). Conclusion: our collector pulls fine; **FMP `etf/info` is
serving stale data for IBIT** (≥4 days old) while issuers published +$111.4M (08-03) and
+$170.3M (08-04) IBIT inflows. A stale source fabricates "measured quiet" through ~$282M
of real flow.

## Lag re-tests (diagnostic, computed from the two tables above)

- IBIT derived[07-30] −$47.0M vs published[07-28] −$54.8M → direction ✓, diff $7.8M —
  IN BAND at a 2-trading-day lag.
- FBTC derived[07-31] −$29.5M vs published[07-29] −$43.1M → direction ✓, diff $13.6M —
  IN BAND at the same lag.
- HODL derived[08-05] +$0.08M vs published[08-04] $0.0 → measured-quiet match at T+1
  (the −$14.7M published 08-05 should hit shares outstanding next strike).
- FBTC derived[08-05] −$153.0M matches NO nearby published day or multi-day sum — not
  explainable by alignment; consistent with source flapping (see zigzag above).
- CUMULATIVE over the window: FBTC derived Δ −1,648,270 shares vs published-implied
  Δ ≈ −313,000 shares → diverges ~5× even fully lag-corrected. The join fix alone CANNOT
  turn this FAIL into a PASS.

## Context and constraints

- Flip preconditions (spec §8): #1–#3 (≥5 obs/ticker, shadow votes through the real
  `_etf_flow_vote`, daily sanity) read green as of 08-04 — but the shadow votes (e.g. FBTC
  −1.0 capped on a −1.47%/day "redemption") are computed from the SAME FMP share series now
  shown stale/flapping, so their green status is contaminated by the same source defect.
- #4 = this reconciliation (FAIL). #5 venue_diffusion freeze + latency stamps: built (gates
  1–3, commits 75e0726 + 9c8f5a7, dark).
- F7 pre-declaration rule (in `etf_flow_reconcile.py`): "Changing after data exists = new
  spec id" — written about the FLOOR/BAND constants.
- The flip, when it happens, must set CRYPTO_SERIES_EPOCH + move
  CRYPTO_LEDGER_CLEAN_COHORT_START in the SAME config change (F3, board 2026-08-05).
- FLOW_ENROLL=1 (insider flow enrollment) is a SEPARATE chain, unaffected.
- Relevant §16a COLD-START posture: honest absence over fabricated reads; the interim truth
  on an insufficient instrument is a display that SAYS SO.
- Cost context: FMP $20/mo Starter (already paid, serves crypto prices + fundamentals
  elsewhere — this is NOT a proposal to drop FMP globally). Issuer product pages are free.
- Key code to read: `transfer/etf_flow_reconcile.py` (harness — join at `_derived_by_date`,
  band at `reconcile()`), `transfer/etf_flow.py` (snapshot() → `fmp_data.etf_info`; header's
  CURRENCY admission), `transfer/crypto_signals.py` (COIN_UNIVERSE proxies; `_etf_flow_vote`),
  spec: `audits/board/CRYPTO_FLOW_SPEC_v1_2026-08-02.md` +
  `audits/board/CRYPTO_FLOW_SPEC_A1_AMENDMENT_2026-08-05.md`.
