# BOARD COLLATION — divergence tracking + mania-independence — 2026-09-14

Nine seats, in isolation, on `EVIDENCE_PACK_2026-09-14_DIVERGENCE.md` (D1–D4), each
verifying in code; third round of the day, building on `BOARD_crypto-money_2026-09-14.md`.
COLLATION, not a blend. **Chairman — your decision per item.**

## THE BOARD'S ANSWER TO THE CHAIRMAN'S QUESTION

**Yes — divergence is trackable, and honestly so — but not the way the idea first
sounded.** Nine seats converge on the same reshaping:

1. **Track ONE SIGNED NUMBER, not four named phases.** The Kindleberger phase classifier
   (expansion/euphoria/distress/deleveraging) was rejected by every seat that examined
   it — Kindleberger assigned those labels AFTER outcomes were known (Buyer's Desk);
   four buckets × thresholds × coins × windows is a hypothesis factory of ~10³ researcher
   degrees of freedom over ~35 observations (Challenger, Statistician); every coin-day
   lands in a phase so none can be wrong (Forecaster: unfalsifiable). What every seat
   would sign instead: **a single continuous, signed residual — the z-scored change in
   coin-denominated open interest AFTER the coin's own price momentum is regressed out**
   (robust median-MAD, window and threshold fixed at pre-registration, sign free to go
   negative per the 07-29 degeneracy rule). Phases may exist as prose in research notes,
   never as scored objects.

2. **"Independent from the mania" is a THREE-PART TEST, not a property you assert**
   (Guardian's formulation, echoed by Statistician and Forecaster):
   - **Construction**: no price term in the arithmetic — ∂reading/∂price = 0 at fixed
     quantities. Funding rate, USD-notional OI, and AUM **fail permanently** (funding is
     derived from the perp-spot basis; notional = quantity × price).
   - **Channel**: the reporting entity must not be a participant in the mania's pricing.
     A CFTC filing > an issuer share register > an exchange's own mark.
   - **Instrument error**: the *missingness and timing* of the measurement must be
     independent of the mania. This is where our own collector currently FAILS — see
     K12 below.

3. **The leg ranking (grades per Statistician):**
   | Leg | Grade | Why |
   |---|---|---|
   | **CFTC COT** | **A** | Regulated weekly filings, free public record, `knowable_at` point-in-time rule ALREADY CODED, and — Executioner's decisive fact — **fully backfillable: it needs no accrual clock at all**. Limits: BTC/ETH (CME) only, weekly, T+3. |
   | ETF share counts | A/B | True primary flow; 4/12 coins; Gate-4 blocked; post-2024 only. |
   | Coin-denominated ΔOI | **C until fixed** | Passes construction; fails instrument-error TODAY (K8 + new K12). Single venue ≈ one statistical factor. |
   | On-chain counts | B | Independent channel, wrong estimand — activity is never credit (settled 9/9 in round 2). |
   | Funding rate | DISQUALIFIED as a leg | Price-derived. Survives only as a declared null/covariate. |
   | Stablecoin issuance | unranked | Unbuilt; do not rank what does not exist. |

4. **The Expansionist's reframe (the biggest strategic idea of the round):** the
   platform ALREADY owns a typed, contract-enforced signed-divergence primitive —
   `heisenberg_gap` (min −100, max +100, derived-field invariant enforced). And two
   **equity** credit-quantity legs are ALREADY COLLECTING, free, rights-clean, with no
   n=0 problem: **OFR repo volume** (whose own docstring states the divergence semantics
   verbatim) and **FINRA short interest**. Proposal: build the divergence computation
   asset-class-agnostic and **prove it on equities first**, instantiating the existing
   gap schema — crypto joins when its legs clear their gates. One caveat found in the
   same pass: the web display bands on `Math.abs(gap)` in four files — **the sign is
   thrown away at render**, which would collapse distress and deleveraging into one
   band; any divergence display must be sign-aware.

5. **The Operator's edge discipline:** raw OI-vs-price divergence is a commodity screen
   (Coinglass et al. publish it free); the only NAMEABLE proprietary edge is the
   **join with our attention series** — divergence conditioned on whether attention
   leads or trails (the GAP × credit interaction). And reflexivity is priced: a
   published flag on thin-book coins can move the very series it scores —
   **pre-commit: BTC/ETH only, and never a directional noun.**

6. **What the site may say (Buyer's Desk + Forecaster, converging):** name the
   OBSERVATION, never the interpretation. Permitted: "open interest +X% while price
   −Y% over 7 days." Forbidden client-facing words: distress, warning, risk, fragile,
   unwind, overheated, crash, bubble. Internally it may be SEALED as a forecast
   (drawdown ≥8% within 45 days, resolved by the existing crossing machinery, judged
   against the coded first-crossing null, unresolved-at-horizon RESOLVES NO); the
   display shows state arithmetic only. At rare-event rates (~3–6 independent episodes
   a year), an honest calibration claim takes **8–15 years** — that number prints
   beside any flag from day one, or the flag does not render.

## NEW DEFECTS THIS ROUND

| # | Finding | Seat |
|---|---|---|
| K12 | **Sampling-time jitter is mania-coupled**: serial 2.5s-paced point snapshots + 6s 429-retries displace the sample LATER exactly on liquidation-cascade days — the mania moves the reading without the quantity changing. Fix: fixed-offset multi-pull + store `captured_at`; run the 3-offset instrument-error audit before any correlation | Challenger |
| K13 | Funding snapshot samples a drifting phase of the 8h settlement cycle — collection-time drift manufactures a phantom funding step | Challenger |
| K14 | No units field / contract-multiplier recorded — the coin-denomination independence claim rests on one docstring observation; a vendor unit switch silently converts the leg to price-multiplied with no detector | Challenger |
| K15 | Perp-listing survivorship: young perps carry a structural OI uptrend from zero that reads as permanent "expansion" | Challenger |
| K16 | `/diag/coinapi` exposes latest values → the spec author has seen the data; the ~35 pre-seal days must be declared spec-development data, excluded from any scored window | Challenger |
| K17 | Web display bands on `abs(gap)` in 4 files — sign-blind rendering would merge opposite divergence states | Expansionist |
| K18 | Roster fragmentation is ≥6 hand-written lists across 5 files (K10 undercounted) | Expansionist |
| K19 | The verdict side is still price: a quantity leg scored on a price-direction ledger is a risk gauge, not an attention-lead claim — it must live in its OWN fenced register, never the attention or crypto ledgers | Guardian |

## VERDICT TABLE

| Item | Chal | Guard | Expan | Buyer | Exec | Econ | Oper | Stat | Fore |
|---|---|---|---|---|---|---|---|---|---|
| D1 trackable? | AWC residual-only | AWC binary/no-phases | AWC signed-scalar | residual APPROVE / classifier REJECT | SHIP amended / classifier CUT | YES as residual | DECAYING (join is the edge) | OVERFIT-RISK unless rewritten | UNSCORABLE as phases |
| D2 legs | REJECT criterion as written (K12) | AWC 3-part test | AWC (equity legs first) | COT-led AWC | SHIP COT#1 | quantities only | NOT-AN-EDGE as posed (one leg, three uniforms) | COT A / ΔOI C | MIS-SCORED (test, don't assert) |
| D3 system | AWC (seal integrity) | AWC (K4 precedent) | AWC (invert to equities) | APPROVE resequenced | research-script SHIPS, engine CUT | approve held-out | one DURABLE part (ETF adapters) | UNSUPPORTED near-term / SOUND accumulation | MIS-SCORED (episodes not coin-days) |
| D4 publication | REJECT as specified | REJECT ledger-feeding / AWC fenced | AWC per-flow_basis | AWC renamed copy only | seal SHIPS / publication CUT | nothing publishes | NOT-AN-EDGE yet | no rate at present N, ever | UNSCORABLE-until-prereg |

## THE CONVERGENT NEXT STEPS (all $0, no deploy, no restart)

1. **P0 — seal the pre-registration spec** (SHA = param_version) BEFORE any correlation:
   the residual definition, window, θ, nulls (momentum / persistence / funding-level /
   F8 first-crossing), Brier-with-Murphy scoring, `flow_basis='perp_divergence'` fencing,
   and the K16 declaration that pre-seal rows are spec-development data.
2. **Run the three free audits on data already held**: the K8/K12 missingness-vs-|return|
   regression, the 3-offset instrument-error test, and the Operator's cross-leg ρ test.
3. **Backfill CFTC COT to CSV** (public record, no clock, grade A) — the research
   dataset exists the same day.
4. **`tools/divergence_research.py`** — read-only SELECT against the held-out table,
   declared in `heldout_registry` as a read-only research consumer (closing K4 for this
   path); no endpoint, no collector change, no UI.
5. Fix K7 (the collector's own docstring misstates its estimand) and K14 (record units)
   — one small collector patch riding the next scheduled deploy.
6. The equity-first instantiation (OFR repo volume / FINRA short interest vs price) as
   the primitive's proving ground — Chairman decision, since it touches the Market
   Signal surface.

**Chairman — your decision per item.**
