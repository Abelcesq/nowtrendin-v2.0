# PRE-REGISTRATION (cohort 1, CORRECTED) — disclosure-to-participation flow ledger
**Date:** 2026-07-27 · **Committed BEFORE the lock is posted and BEFORE any row enrolls —
the git timestamp of this file is the pre-registration.**
**Supersedes:** `FLOW_PREREG_2026-07-26.md` (prereg_id `261716973f6968b4`), which is retained
unaltered. **Rows enrolled under the superseded registration: ZERO** — which is the only
reason this correction is free. After row 1 it would have been a disclosed cohort break.

## Why this exists (Board review 2, 2026-07-27)

Five independent archetypes audited the never-reviewed enrollment module. Four findings made
the previous registration a promise the code did not keep:

1. **The registered `enroll_threshold` was decorative.** It was hashed, then compared to
   nothing. Qualification ran on the env var `FLOW_QUALIFY_MIN_BUYERS`; the `below_threshold`
   refusal counter was initialised and incremented by no code path. One dyno `config:set`
   would have redefined the cohort under an unchanged SHA, permanently, in a ledger that
   never deletes. *(All five archetypes found this independently.)*
2. **"10 trading days" was 10 CALENDAR days in code** (~7 sessions — a ~30% tighter window
   than the one registered).
3. **Four material terms sat OUTSIDE the SHA** — the qualify window, the arrival persistence
   rule, the echo threshold (an input to a pre-registered *falsifier*), and the match-key
   spec. Anything enforceable by env but absent from the hash can drift without minting a
   cohort, which is the exact defect the hash exists to prevent.
4. **The observable's prose overclaimed.** It read "breadth **vs the name's own base rate**";
   the code computes an absolute count with no normalisation of any kind. *"A registration
   whose prose flatters its code is a small lie in the one document whose entire value is
   that it cannot lie."* (Economist)

Additionally, the **stratified log-rank named PRIMARY existed nowhere in code** — only the
disjoint-bands publication gate (the registered *secondary*) was implemented. Writing the
test statistic after the data accumulate is precisely the flexibility a pre-registration
exists to foreclose, so it is now implemented and validated **before** row 1.

## The hypothesis (unchanged)

**Cluster open-market insider buying precedes expanded market participation.**
Instruments where ≥3 distinct insiders file open-market purchases (Form-4 code P) within a
10-trading-session window reach an abnormal share-volume arrival sooner than matched control
instruments with no qualifying cluster of their own.

A TIMING claim measured against a control — never a return claim, never advice. *"We do not
predict prices. We measure — against matched controls and a pre-registered, never-deleted
record — which mandatory disclosures have historically been followed by expanded market
participation, and how many days of warning that expansion gave."*

## The terms — ALL of these are inside the SHA-hashed registration

| Term | Value | Note |
|---|---|---|
| Observable | **distinct open-market Form-4 buyers (absolute breadth) ≥ 3 within 10 trailing trading sessions** | Corrected text: an absolute count, NOT base-rate-normalised. Per-name base-rate normalisation needs panel history the panel does not yet have (§16a cold start) and is pre-declared as a **cohort-2 refinement**, never a mid-cohort patch. Heterogeneous treatment intensity attenuates toward the null — the conservative direction — and size-band matching absorbs part of it. |
| `enroll_threshold` | **3 buyers** | Now ENFORCED at the ledger door (`enroll()` refuses below it and COUNTS the refusal) and cross-checked in `run_cycle`, which **halts the cycle** if the env disagrees with the registration. |
| `qualify_window_sessions` | **10 trading sessions** | Counted as weekdays walked back from the detection date. **US market holidays are NOT excluded**, so a holiday lengthens the effective calendar span by one day. Stated exactly, because "trading days" is what drifted. |
| `arrival_mult` | **3.0×** the frozen 60-session median share volume | Mechanical read off the corrected null: 60d **19.6% [13.8–26.0]** at the Board's ~20–25% regime. **Disclosure:** the 2.5× and 3.0× intervals OVERLAP — 3.0× is a convention fixed before any treated data, not measured superiority over 2.5×. |
| Arrival persistence | **crossing day + ≥1 of the following 4 sessions** (`hits_required` 2, `window` 5) | Now passed to the resolver from the ROW's registration; previously read live env, so an env edit could re-resolve enrolled rows under a different definition of "arrival". |
| `echo_sessions` | **3** | Arrivals within 3 sessions of the filing are disclosure echo. This is an input to falsifier (1), so it belongs in the hash. |
| Baseline | 60 sessions ending 5 sessions before detection; refuses below 30 samples | Frozen at enrollment, used verbatim at resolution. |
| `primary_horizon_days` | **90** | The 9–14-day median lead is the NULL's behaviour (noise arrives early); the treated tail is weeks-to-months. |
| `horizon_days` (censoring) | **180** | Right-censoring horizon; KM retains censored rows. |
| `min_episodes` | **120 resolved treated**, registered as a **LOOK POINT** | Corrected disclosure (Economist): the power table was computed against the **60d** null (19.6%) while the primary horizon is **90d**, where the null is **25.2%** — at which 120 sits at the aggressive end. Rather than restate a number we cannot yet justify, 120 is registered as the single pre-declared analysis point with the underpowered outcome **pre-accepted**: if the log-rank does not reject at 120, falsifier (2) fires and the null is published. |
| `controls_per` | 3, atomic with the treated row | Cannot be retrofitted. |
| Control match key | sector + size band + **ADV band 0.2–5.0× on the FROZEN 60-session median share volume** + pretrend bucket (contracting <0.9 / flat / expanding >1.15); control must have **no qualifying cluster of its own** in the same window | ADV is no longer the screener's current-session volume (which is inflated for a name mid-spike). A candidate missing either side's ADV is now REFUSED, not passed-and-stamped-matched. The control exclusion now matches the registered wording exactly: a *qualifying cluster*, not any single purchase — excluding every name with any insider buying would have selected systematically quieter controls, flattering the treated arm. |
| **PRIMARY analysis** | **stratified log-rank on time-to-arrival** — strata = `match_group`, Mantel-Haenszel with the hypergeometric tie correction, two-sided α = 0.05, censored at the registered 180d horizon | Implemented in `ledger_survival.stratified_logrank`, validated against the published Freireich 6-MP trial (χ² = 16.79, p = 4.2e-05) with Type-I calibration at 0.053/0.057 vs 0.05 and 95% power on a true 2× hazard gap. |
| Publication gate | disjoint Greenwood log-log bands at the 90d primary horizon | Deliberately STRICTER than the primary test, so a published claim never rests on the log-rank alone. |
| Stop rule | ONE confirmatory analysis at `min_episodes`; quarterly descriptive reads permitted, stamped "no verdict yet" | No optional stopping. |
| Falsifiers | (1) >50% of treated arrivals are `disclosure_echo` (≤ `echo_sessions`) → the instrument is a reading service, and we say so. (2) the log-rank fails at `min_episodes` → **the null is published as the result** | |
| Exclusions | `pre_arrived` rows enrolled, excluded from the lead denominator, reported separately. Echo + scheduled-artifact arrivals excluded from the headline, reported as counts | `pre_arrived` is now stamped using the registration's `arrival_mult`, not the env default. |
| `param_version` | `arrival-v2-sharevolume` | |

## Known limitations, disclosed now rather than when someone finds them

- **The calibration universe** (55 tickers; 40 drawn from one day's filings) is filing-heavy.
  For calibrating the threshold on the kind of name that will actually enroll, that is
  arguably the right reference — but the *control* arm is drawn from non-filing names, which
  plausibly run quieter. The verdict is unaffected (the control rate is **observed**, never
  assumed); the power arithmetic is uncertain in a direction we cannot sign. A
  screener-random robustness re-run is prescribed **before any publication**, not before
  enrollment.
- **Control determinism** is reproducible *given the screener snapshot*, which is live. The
  seed fixes the shuffle, not the pool.
- **Control reuse** across match groups is measured and disclosed; `report()` refuses to
  publish above a 1.25× reuse factor.

## What changes this registration

Nothing, silently. Any term change mints a NEW SHA and a NEW cohort; `report()` refuses
publication while a superseded cohort holds rows. Before the first row enrolls a re-lock is
costless — which is exactly the allowance being used here, once, and it does not apply again
after row 1.
