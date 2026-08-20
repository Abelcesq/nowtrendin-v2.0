# PRE-REGISTRATION — Referee branch decomposition + null control
### Sealed 2026-08-20 UTC, BEFORE the harness is written and BEFORE any row is re-examined.
### Chairman-approved 2026-08-20 (nine-seat board convening 2026-08-19).

## Why this document exists at all

The correction I am about to make will produce a **softer-sounding headline**, and I am
making it **after** seeing an unwelcome result. Specifically: reclassifying the referee's
non-confirmations will move rows out of *uncorroborated* and into *inconclusive /
unrefereeable*, which **lowers `refereeCheckedPct`** — plausibly below the 20% floor —
flipping `refereeState` from `exercised_and_inconclusive` to `not_exercised`.

A definition change that makes our own disconfirming control look less damning, made after
reading its verdict, is **indistinguishable from fitting** unless the expectation is sealed
first. That is the entire reason for this file. If the results come back differently from
what is written below, that difference is data about us and stays on the record.

## The a-priori justification (established from CODE ONLY, no outcome consulted)

All four defects below are demonstrable by reading `_referee_corroborate`
(`transfer/accuracy_ledger_enhanced.py:161-196`) and `transfer/referee_wikipedia.py`. None
required looking at a single result. This matters: the re-specification is justified by
mechanism, not by the answer it produced.

1. **Absence scored as refutation.** `if not arrival: return 0`. "Wikipedia shows no
   qualifying surge" is written to the same column, with the same value, as "Wikipedia says
   attention preceded our call." This is §15a violated inside the control that gates
   citability.
2. **The referee is anchored on Google.** Corroboration requires
   `abs(wiki_arrival − google_breakout) ≤ 14`. The second referee's verdict is conditioned
   on the first referee's date. Independent *data*, Google-*anchored* comparison.
3. **Long leads are structurally penalised.** With `brk = det + L`, corroboration requires
   arrival `≥ det + L − 14`. **Any row with L > 16 returns 0 even when Wikipedia confirms
   the lead more strongly than Google did.** Median lead is 11 days, so a material share of
   the LED cohort sits in the penalised region.
4. **Sensitivity floor anti-correlated with the claim.** `SURGE_MIN_ABS = 200` views/day on
   en-only Wikipedia. Our asserted edge is niche, early, pre-mainstream topics — precisely
   the articles least likely to clear 200 daily views. The instrument's coverage is
   anti-correlated with the population it is asked to adjudicate.

## SEALED EXPECTATIONS (the falsifiable part)

Stated before the harness runs. Each is scored honestly afterward.

- **E1 — Branch composition.** I expect the **majority of the 14** non-confirmations to be
  branch (1) *no qualifying surge* or branch (3) *outside the ±14d Google band* — i.e.
  silence and ill-posedness — rather than branch (2) *arrival precedes detection*.
  **Sealed point estimate: ≥ 8 of 14 in branches (1)+(3); ≤ 4 of 14 in branch (2).**
- **E2 — Sensitivity floor.** I expect **≥ 5 of 14** LED topics to have an en-Wikipedia
  article whose in-window peak never clears 200 views/day (structurally unrefereeable).
- **E3 — Effect on the served metric.** I expect `refereeCheckedPct` to fall from **93.3%**
  to **below 40%**, and plausibly below the 20% floor, once only CORROBORATED + DISPUTED
  count as checked.
- **E4 — Null control (THE DECISIVE TEST).** I expect the LAGGED cohort to corroborate at a
  **similarly low rate (≤ 20%)**. If so, the referee has little discriminating power and
  0-of-14 carries little information about our wins.

## DECISION RULE (binding, written before the data)

| Outcome | Conclusion | Action |
|---|---|---|
| LAGGED corroborates ≈0% too | Referee has **no discriminating power**. 0-of-14 says nothing about our wins. | Fix or retire the referee. Citation bar unchanged — we simply have no working second referee. |
| LAGGED corroborates materially (> 30%) while LED stays ~0 | **The wins are in real trouble.** The referee discriminates and it does not confirm us. | Reaches the Chairman the day it lands. Ledger rows untouched; the finding is reported, not buried. |
| Branch table dominated by (1)/(3) + sub-200-view articles | **The referee is blind to our cohort.** | A coverage disclosure, not a verdict. Proceed to `wiki-v3` + GDELT. |

**In no outcome does any verdict, lead, date, or ledger row change.** This is measurement.

## CONSTRAINTS ON THE RE-SPECIFICATION (Challenger's governance condition)

The frozen params (`SURGE_MULT 3.0`, `SURGE_MIN_ABS 200`, `±14d`, `2d grace`) were sealed
2026-08-17 — two days before the referee returned its answer. Therefore:

1. The re-spec is justified **solely** by the four a-priori defects above, sealed here,
   before any re-run.
2. It ships as a **NEW referee** (`wiki-v3`, new `param_version`) — never a tune of
   `wiki-v2`. Registered as H8b, a definition change, not a parameter adjustment.
3. **The original `wiki-v2` 0-of-14 result is reported permanently, alongside, forever.**
   If the re-spec produces corroboration, both numbers travel together, always.
4. `referee_rule_version` is stamped on every row from this point, so no forecast in flight
   (notably F7/B7) silently changes meaning when the rule changes.

## WHAT IS EXPLICITLY NOT PERMITTED

- Lowering `SURGE_MIN_ABS` because it produced zeros. That is instrument-tuning toward a
  desired answer. The correct repair for a floor-bound referee is **more coverage**
  (multi-language wikis, GDELT as a second arm), never a lower bar.
- `UPDATE`-ing `referee_corroborated` in place. Ledger rows are never rewritten; the new
  reading is a new forward-only column.
- Citing any corrected rate. The citation bar (majority corroboration + minimum checks +
  query quality, sealed constants as of 2026-08-20) governs regardless of what this finds.

---
*Sealed to the PIT store as `kind='forecast'`, item_key `PREREG-referee-decomposition`,
before the harness existed. Row hash recorded below on sealing.*

**PIT SEAL (recorded on sealing):** `item_key=PREREG-referee-decomposition-2026-08-20`, `row_sha256 572adc8fa5690f3cb09ab32d1b94103015edf61c8398a038ee02d258817616d4`, `text_sha256 2d99c8de3191d4e714cdb1780f8b8b9828a7f2e28f372f7b865531aabdd7c069` (5930 chars, this file through the line before the seal note). Sealed BEFORE the harness was written.
