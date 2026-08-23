# BASE-RATE CALIBRATION LOG — PRE-REGISTRATION, SEALED BEFORE THE FIRST ROW
### Sealed 2026-08-23, before `base_rate_calibration_log` has a writer, a row, or a served number.
### Cause: board round 7 convergent condition 3 (nine seats), ratified by the Chairman 2026-08-23 —
### "Seal the calibration log BEFORE its first row." A calibration loop whose rules are written
### after its first results is a demo with a ledger costume.

---

## 1. What is being pre-committed

The three probability agents (`transfer/trend_probability_agent.py`,
`market_flow_probability_agent.py`, `crypto_flow_probability_agent.py`) read a table named
`base_rate_calibration_log` that, as of this seal, **has no writer and no rows**. This document
fixes — before any number exists — what gets written, by whom, when, how the record is graded,
and what result withdraws the product. Every term below is chosen while the answer is genuinely
unknown.

## 2. Write discipline (server-writes-at-serve-time)

1. **The SERVER writes the row at the moment the probability is served.** No batch
   reconstruction, no backfill, no client-reported rows. A probability that was served but not
   logged is an incident, not a gap.
2. Each served row records, at minimum: `kind` (trend|market|crypto), `item_key`, `cohort_key`,
   `served_probability` (the blended value actually rendered), **`F_port` — the portfolio base
   rate SEALED PER ROW at serve time** (the climatology this row will be judged against, frozen
   before its outcome is knowable), `raw_rate`, `credibility_z`, `horizon_days`, `as_of`,
   `param_version`, `served_at` (UTC).
3. **Append-only.** Outcomes arrive as SEPARATE resolution rows (`observed_outcome` 0/1,
   `resolved_at`, resolution basis) that reference the served row. A served row is never edited.
4. Rows the agents refuse to serve (ABSENT / NOT_APPLICABLE / INSTRUMENT_ERROR) are **not**
   logged as probabilities — a withheld number has no forecast to grade. The refusal counts are
   monitored separately; they are operations, not skill.

## 3. The decision-binding number: BSS_port

- The record is graded by **Murphy decomposition** (reliability − resolution + uncertainty,
  within-bin term reported) and the **binning-independent Brier Skill Score against the per-row
  sealed `F_port`** — called **BSS_port**. Because `F_port` is sealed into each row at serve
  time, no reference forecast can be chosen after the outcomes are known.
- BSS_port is THE decision-binding number. No other read of this table (a favourable bin, a
  trimmed window, a cohort subset) may substitute for it in any decision or any published claim.
- With fewer than **n = 50 resolved rows**, no skill number exists: the section reports
  "insufficient resolved rows (n=<count>)" — honest absence, never a provisional BSS.

## 4. Scoring calendar and the withdrawal rule (pre-committed)

- **Quarterly scorings** on the last day of February, May, August and November (the standing
  readout calendar), first scoring at the first quarter-end with **n ≥ 50 resolved rows**.
- **WITHDRAWAL:** if **BSS_port < 0 at n ≥ 50 on TWO CONSECUTIVE quarterly scorings**, the
  probability sections are WITHDRAWN from every panel (trend, market, crypto) — removed from
  render, not reworded — pending a NEW sealed pre-registration. A negative BSS_port means the
  sealed portfolio rate alone was the better statement; serving the blend past that finding
  would be selling noise with a confidence interval.
- One negative scoring is a warning, recorded and published, not a withdrawal. UNSCORABLE
  (n < 50) is **not a pass**: it defers to the next scoring, and the deferral is recorded.

## 5. Completeness audit (the section disables itself)

A completeness audit compares probabilities SERVED (from the serve path's own accounting)
against rows LOGGED, per period. **If served ≠ logged, the probability section is DISABLED on
all panels until reconciled** — an incomplete log cannot certify anything, and a log that only
holds the rows that survived is survivorship with a schema. The audit result is reported
alongside every quarterly scoring.

## 6. Render preconditions (board condition 6, carried into the seal)

No user-facing render of any cohort probability before: **(a)** the log holds **n ≥ 60 logged
resolutions** accumulated in shadow mode (served-to-log only, not displayed), and **(b)** the
first quarterly scoring has completed and been published, whatever it says. The trend panel
honestly reading ABSENT for months is the shipped state, not a bug to hurry past.

## 7. Amendment rule

This pre-registration may be amended ONLY by a superseding sealed entry that cites this row,
made BEFORE the scoring it would affect. An amendment after a scoring is void by construction.

---
**PIT SEAL:** `kind='forecast'`, `item_key=PREREG-calibration-log-2026-08-23`,
`row_sha256 e75a71ec2f8496d8c88787e7510dc24faac428e8b203e285491a12f3570bdd5b`,
`text_sha256 c25766e63c69a4534186e63b12b67c4120fcbf85ed2b21c792f4ef7c70b72271` (body above
this block: 4801 bytes LF-normalized == 4769 characters, up to and including the newline
preceding the `---` that opens this block — the D-KILL extraction recipe applies verbatim).
Registered in `FORECAST_REGISTER.md`; anchored in `audits/pit-anchors/PIT_SEAL_ANCHORS.md`;
enforced by claim `C-CALLOG-PREREG` in `tools/integrity_gate.py`.
