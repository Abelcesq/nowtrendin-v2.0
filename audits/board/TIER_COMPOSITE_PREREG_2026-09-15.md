# PRE-REGISTRATION — CoinAPI OI leg into the crypto positioning composite (SEALED)

**Sealed 2026-09-15 by Chairman ruling on board round 4, disagreement 1 ("please do both"):
the acceptance criteria below are fixed BEFORE any candidate composite is computed; the
already-accrued CoinAPI window may inform an EXPLORATORY read only (labeled
SPEC-DEVELOPMENT, per the K16 taint logic — its authors have seen the data); the BINDING
validation runs on post-seal accrual only. The commit introducing this file is the seal;
its SHA-256 is the param_version of the tier-composite cohort. Any edit to a sealed
section mints a new param_version.**

## 1. Purpose and scope (sealed)

Make the crypto **Tier** honestly computable by adding the CoinAPI open-interest leg — the
only positioning-class source with full 12-coin coverage — to the crypto positioning
composite (`money_movement` leg of `crypto_money_gradient`). Display of the resulting tier
is ADDITIONALLY gated on rights (register item 9(b) written CoinAPI grant covering derived
composite indicators + 9(c) Binance pass-through counsel review) and on the K12 timing
audit; this seal governs the measurement side only.

## 2. Candidate definition (sealed — fixed before any outcome is examined)

- The OI leg enters as a **baseline-relative component** in the existing market-signal
  style: per coin, the 7-day Δln of **coin-denominated** open interest scored against the
  coin's own trailing baseline, with the standard §16a cold-start progression
  (CALIBRATING under `MIN_BASELINE_TRUSTWORTHY` cycles → honest absence on degenerate
  baselines → never a floor value). USD-notional OI is disqualified (∂reading/∂price ≠ 0).
  Rows marked `suspect=1` (K14 unit guard) are excluded, and rows failing the D10
  retroactive unit backscan never seed a baseline.
- **Corroboration floor unchanged:** the ≥2-votable-positioning-sources floor stands. The
  OI leg adds ONE votable source to every roster coin; a coin reaches a measured
  positioning read only where a second independent source (insider/13F proxies, ETF flow
  where covered) also votes. Coins with no second source remain honestly ABSENT
  (`structural — source limit`) — the floor is never lowered to fill the column.
- Weighting when both sources are measured: equal weight. When fewer than the K2 floor of
  a leg's weight is measured, the leg serves None (the existing renormalization rule is
  not weakened by this change).
- Funding rate is NOT a term of this composite (price-derived; conditioner/null only, per
  the divergence prereg).

## 3. Acceptance criteria (sealed — the pass bar the backtest must clear)

The wired candidate, computed held-out, SHIPS only if ALL of:
1. **Beats Null A** — its directional association with the crypto accuracy ledger's
   realized outcomes exceeds that of bare 7-day momentum sign over the same rows, with
   day-clustered inference (effective N = distinct days, never coin-days), and the
   advantage's confidence interval excludes zero.
2. **Fabricates nothing** — on every absence/degenerate fixture, the composite serves
   None/CALIBRATING per §16a; no default band ever appears (the D11 lint must stay green).
3. **Instrument gates passed** — the K12 3-offset timing audit passed on ≥30 days of its
   own collection, and the missingness audit is either non-trivially passed or the
   missingness observed is shown non-informative.
4. **Stability** — the tier bands produced on the validation window are not degenerate
   (not >90% of measured coins in one band) and are insensitive to ±1 day of window
   alignment (a re-run shifted by one day changes no coin by more than one band).

## 4. Windows (sealed — the Chairman's "do both")

- **Exploratory read:** the pre-seal accrued window (2026-08-10 → 2026-09-15) MAY be used
  to develop and sanity-check the candidate. Every artifact it produces is stamped
  **SPEC-DEVELOPMENT (K16)** and can never be cited as validation or shipping evidence.
- **Binding validation:** post-seal accrual only, ≥90 daily observations per scored coin
  (earliest read ≈ 2026-12-14). The acceptance criteria of §3 are judged on this window
  alone, once, by a board note; a failed validation is reported as failed — re-tuning the
  candidate after seeing the validation mints a new param_version and a new validation
  window.

## 5. Process gates (sealed)

Backtest-before-ship (§16 gate 6) → board note reviewing §3 against the §4 binding window
→ Chairman flips the flag. Never an env-flip alone; never a display flip while register
item 9(b)/(c) is open; the interim display remains honest ABSENT.
