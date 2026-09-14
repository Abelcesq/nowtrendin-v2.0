# PRE-REGISTRATION — Leverage & Positioning divergence (SEALED)

**Sealed 2026-09-14 by Chairman order ("create and implement the recommended 1–6"),
per `BOARD_divergence_2026-09-14.md`. The git commit introducing this file IS the seal
(flow-spec precedent, CRYPTO_FLOW_SPEC v1 §1): its timestamp is the pre-declaration and
this file's SHA-256 becomes `param_version` for every cohort scored under it. Any edit
to a sealed section below mints a NEW param_version and a NEW cohort — quiet retuning is
the forbidden path. Board seats' binding conditions are cited inline.**

## 1. Estimand and name (sealed)

- Internal name: `perp_divergence`. Client-facing name: **"Positioning vs Price"**.
- The words "money movement", "inflow", "distress", "warning", "risk", "fragile",
  "unwind", "overheated", "crash", "bubble" are FORBIDDEN in any client-facing rendering
  of this signal (Buyer's Desk / Forecaster). Display may state arithmetic only, e.g.
  "open interest +X% while price −Y% over 7 days", sign-aware (K17).
- What it measures: the residual of leveraged-positioning quantity after price momentum
  is removed — **leverage positioning, never money inflow** (perps are zero-sum; OI is
  coin-denominated contract count).

## 2. The statistic (sealed — Economist's specification, board-converged)

Per coin *c*, daily, UTC, forward-only:
- `q_t = Δln(OI_coin)` over a 7-day window — **coin-denominated OI only**; USD-notional
  (OI×price) is disqualified by construction (Guardian/Statistician: ∂reading/∂price ≠ 0).
- `p_t = Δln(price)` over the same 7-day window, from a price series stored independently
  of the M composite.
- `zq, zp`: robust z (median/MAD), trailing 90 observations, forward-only.
- Robust fit (Theil–Sen) `zq ~ α + β·zp` on the trailing 90 days, refit weekly.
- **D_t = zq_t − (α̂ + β̂·zp_t)** — one continuous SIGNED residual. No phase labels are
  scored objects (9/9). Sign must be able to go negative (07-29 degeneracy rule).
- Funding rate enters ONLY as `f_sign` = sign(trailing-7d mean funding) — a conditioner
  and a null, NEVER a term of D (funding is price-derived; permanently disqualified).

## 3. The internal forecast criterion (sealed — Forecaster)

- Flag: `D_t ≥ θ` with **θ = +1.5** — set BY CONSTRUCTION, not fitted; never re-tuned
  under this param_version.
- Resolution: close-to-close drawdown **≥ 8% within 45 days** of the flag date, resolved
  by the existing first-crossing machinery (full windows only). **Unresolved at horizon
  RESOLVES NO** — a miss, printed as a miss; open windows render OPEN, never "pending".
- Scope: **BTC and ETH only** are independently scorable (one venue ≈ one factor;
  Operator's reflexivity fence: no flag on thin-book coins).
- N is counted in **independent episodes** (non-overlapping 45-day windows,
  cross-sectionally collapsed), never coin-days.

## 4. Nulls and scoring (sealed)

Judged against ALL of, out-of-sample, before any publication claim:
- **Null A** — 7-day momentum sign alone.
- **Null B** — lagged persistence (yesterday's flag state).
- **Null C** — funding level alone (and funding autocorrelation).
- **Null F8** — the coded unconditional first-crossing baseline
  (`crypto_accuracy_ledger.compute_null_baseline`), per-direction, never pooled
  (Challenger D4: pooled rates let composition drift harvest the up-bias).
Scoring rule: **Brier, Murphy-decomposed** (reliability/resolution/uncertainty), over ALL
sealed flags, never survivors; BSS against the per-row sealed baseline per
`CALIBRATION_LOG_PREREG_2026-08-23.md`. Multiple-hypothesis accounting: the PRIMARY
hypothesis is exactly ONE — pooled BTC+ETH, θ=+1.5, 45d/8% — everything else is
exploratory and Bonferroni-corrected; the hypothesis family is counted in the analysis
file each run.

## 5. Data windows and instrument gates (sealed — Challenger K12–K16)

- **Every `coinapi_derivs` row written before this seal is SPEC-DEVELOPMENT DATA** (K16:
  `/diag/coinapi` exposed values to the spec authors) — permanently excluded from any
  scored window. The scored window begins at the first post-seal row.
- No forecast correlation is computed before **≥90 post-seal daily observations per
  scored coin**. Instrument audits (missingness, timing, cross-leg correlation, unit
  sanity) are exempt — they test the thermometer, not the forecast, and MUST pass first:
  - K8/K12 missingness audit: per-coin daily-row presence regressed on same-day |return|;
    a significant coefficient DISQUALIFIES the leg until the collector is fixed.
  - K12 timing audit (3 fixed intra-day offsets, ≥30 days, ≥1 coin) — REQUIRED BEFORE
    GRADUATION; the collector's `captured_at` stamp (shipped with this seal) is its input.
  - K14 unit guard: rows carry `units='coin'`; a >10× day-over-day OI discontinuity marks
    the row `suspect` and breaks the series rather than silently converting the leg to a
    price-multiplied one.
- Historical reconstructions (deep venue dumps, licensed panels) are **non-enrolling**:
  training/context only, never a track record (Economist).

## 6. Fencing (sealed — Guardian K19 / Forecaster enrollment invariance)

- `flow_basis = 'perp_divergence'`, its own cohort boundary, its own register. It NEVER
  enters the attention ledger, the crypto accuracy ledger's existing cohorts, or any
  published accuracy rate of the attention product. Enrollment gates
  (`record_from_serve`) are not touched by this program.
- Graduation to any user-facing surface additionally requires: the three instrument
  audits passed · rights evidence for every input (RIGHTS_REGISTER items 9–11; §16
  gate 5) · board note · Chairman sign-off. Publication floor: no rate of any kind below
  **30 resolved flags**, and no binned reliability claim below 50 (Forecaster); the
  8–15-year honest-calibration horizon is printed beside any flag from day one.

## 7. Equity-first instantiation (Chairman-ruled GO, item 6)

The SAME §2 residual, asset-class-agnostic, instantiated on the rights-clean equity legs:
`q` = Δln(FINRA short interest) per ticker (bi-monthly cadence; windows scale to the
cadence: z over trailing 24 observations, Theil–Sen on the same), `p` = matching-window
Δln(price). OFR repo volume is a MACRO series — reported as its own market-wide residual
against SPX-proxy momentum, clearly labeled macro, never per-instrument. Equity outputs
are research-only under this same seal until their own board note; they share §1's
forbidden-words rule.

## 8. Analysis code contract (sealed)

The research runner (`tools/divergence_research.py`) is read-only (SELECT only), declared
in `heldout_registry` as a research consumer (K4), and **contains no forward-looking
join**: it may compute D_t and instrument audits, and may NOT join D_t to any
subsequent-return or ledger-outcome column until the §5 gates are met — enforced by the
absence of any outcome column in its queries under this param_version.
