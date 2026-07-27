# PRE-REGISTRATION — the disclosure-to-participation flow ledger (cohort 1)
**Date:** 2026-07-26 · **Committed BEFORE the lock is posted and BEFORE any row enrolls —
the git timestamp of this file is the pre-registration.**
**Authority:** Chairman's "proceed" on the Board's master-remediation recommendation
(R-a: 3.0–3.5×, read mechanically off the CORRECTED calibration curve).

## The hypothesis

**Cluster open-market insider buying precedes expanded market participation.**
Formally: instruments where ≥3 distinct insiders file open-market purchases (Form-4 code P)
within a 10-trading-day window reach an abnormal share-volume arrival sooner than matched
control instruments with no qualifying disclosure.

This is a TIMING claim measured against a control — never a return claim, never advice.
The defensible sentence (Economist, adopted): *"We do not predict prices. We measure —
against matched controls and a pre-registered, never-deleted record — which mandatory
disclosures have historically been followed by expanded market participation, and how many
days of warning that expansion gave."*

## The terms (all inside the SHA-hashed registration)

| Term | Value | Basis |
|---|---|---|
| Observable | distinct open-market buyers (BREADTH) ≥ **3** in **10** trailing days | the Chairman's cluster-buying red flag; Seyhun-grounded; a change, never a dollar level |
| `enroll_threshold` | 3 buyers | as above |
| `arrival_mult` | **3.0×** the frozen 60-session median share volume | mechanical read: corrected 60d null **19.6% [13.8–26.0%]** sits at the Board's ~20–25% regime; 2.5× = 27.3% (above), 3.5× = 17.5% (below). Power rule: required n DECREASES in the null |
| Arrival persistence | crossing day + ≥1 of the following 4 sessions | arrival_clock `arrival-v2-sharevolume`, frozen semantics |
| `primary_horizon_days` | **90** | the 9–14-day median lead is the NULL's behaviour (noise arrives early); the treated tail is weeks-to-months (Seyhun-descended literature); 60d saves little null (19.6→25.2% at 90d) |
| `horizon_days` (censoring) | **180** | right-censoring horizon; KM retains censored rows |
| `min_episodes` | **120** resolved treated | log-rank-primary at a ~15pp-equivalent effect: the ~200 band-rule requirement cut by the log-rank's ⅓–½ saving |
| `controls_per` | 3, atomic with the treated row | cannot be retrofitted |
| Control match key | sector + size band + ADV band + **pretrend bucket** (last-20-sessions mean ÷ frozen-window median; contracting <0.9 / flat / expanding >1.15), no qualifying disclosure of their own | controls must trend the way the treated name trended BEFORE the filing, or separation measures volume momentum |
| Analysis | **PRIMARY: stratified log-rank on time-to-arrival** (match_group strata, full 180d). Disjoint Greenwood bands at the primary horizon = the conservative PUBLICATION gate | uses the whole curve; cuts required n ⅓–½ |
| Stop rule | ONE confirmatory analysis at min_episodes; quarterly descriptive reads permitted, stamped "no verdict yet" | no optional stopping |
| Pre-registered falsifiers | (1) >50% of treated arrivals are `disclosure_echo` (≤3 sessions) → the instrument is a reading service, and we say so. (2) log-rank fails at min_episodes → the null is published as the result | |
| Exclusions | `pre_arrived` rows: enrolled, excluded from the lead denominator, reported separately. Echo + scheduled-artifact arrivals excluded from the headline, reported as counts | |
| `param_version` | `arrival-v2-sharevolume` | |

## The corrected calibration (the curve the multiple was read from)

Seed 20260725 · universe FROZEN in `tools/calibration_universe_2026-07-26.txt` (55 tickers) ·
295 ticker-dates · pre-arrived excluded per multiple · ticker-clustered bootstrap:

| mult | 60d null [95% CI] | 90d | 180d | pre-arr | events/name-yr (−ln(1−p)×365/60) | med lead |
|---|---|---|---|---|---|---|
| 2.0 | 51.5% [43.5–60.3] | 59.9% | 77.2% | 58 | 4.40 | 18 |
| 2.5 | 27.3% [20.7–34.4] | 36.5% | 56.9% | 35 | 1.94 | 14 |
| **3.0** | **19.6% [13.8–26.0]** | 25.2% | 42.6% | 25 | 1.33 | 13 |
| 3.5 | 17.5% [11.9–23.8] | 22.2% | 32.0% | 20 | 1.17 | 11 |
| 4.0 | 13.6% [7.7–20.4] | 18.6% | 27.1% | 15 | 0.89 | 16 |
| 5.0 | 12.0% [6.9–18.1] | 15.5% | 19.1% | 12 | 0.78 | 25 |

All four accountability-review corrections applied: `already_arrived_before` on the null ·
hazard-correct events/yr · frozen universe with SHA · clustered intervals. (The prior run's
24.1% at 3.0× was biased upward by mid-surge draws; its 252/60 events arithmetic misstated
the Challenger's own target, which corrected maps to ~2.2–2.5× — below the power-chosen band.)

## Power (the calendar this buys)

Against the corrected 19.6% null, two-proportion at 80% power w/ clustering + band rule:
+20pp ≈ 100/arm · +15pp ≈ 180/arm · +10pp ≈ 390/arm — cut ⅓–½ by the log-rank primary.
At the Expansionist's central 3 treated enrollments/day (market-wide ingestion), the
+15pp-equivalent read closes **Q4 2026–Q1 2027**; every week the flags stay off moves it
one-for-one.

## What changes this registration

Nothing, silently. Any term change mints a NEW SHA-hashed registration and a NEW cohort;
`report()` refuses publication while a superseded cohort holds rows. Before the first row
enrolls, a re-lock is costless (a zero-row superseded cohort blocks nothing) — after it,
the change is a visible, disclosed cohort break.
