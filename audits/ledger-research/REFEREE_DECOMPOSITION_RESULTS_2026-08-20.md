# Referee branch decomposition + null control — RESULTS
### Run 2026-08-20 UTC · read-only · scored against the pre-registration sealed BEFORE the harness existed
### Pre-registration: `REFEREE_DECOMPOSITION_PREREG_2026-08-20.md` (PIT row `572adc8f..`, text `2d99c8de..`)
### Harness: `tools/referee_decomposition.py` · raw: `REFEREE_DECOMPOSITION_RESULTS_2026-08-20.json` (150 rows) + `REFEREE_PLACEBO_BACKWARD_2026-08-20.json` (25 rows)

---

## THE HEADLINE

**The referee is SPECIFIC but BLIND.** It is not a rubber stamp — over 25 placebo rows
(real topics against random past dates) it corroborated **zero**. It is not mute either —
on the SAME_DAY cohort it corroborates **5 of 10**. But on the LED cohort, the one cohort
whose claim is the entire product, it corroborates **0 of 15**, and **13 of those 14
non-confirmations are SILENCE, not refutation.**

Exactly **one** LED row is a genuine refutation.

> The served sentence "the independent referee returned non-confirmation on 14 of 15 LED
> wins (93.3%)" is arithmetically true and **materially misleading**. The honest sentence
> is: *the referee could render a verdict on 1 of 15 LED wins, and that one went against
> us. On the other 14 it saw nothing to judge.*

## THE FOUR ARMS

| Arm | n | Corroborated | Genuine refutations (PRECEDES) | Silence (NO_SURGE / NO_ARTICLE / NO_CURVE) | Naive rate |
|---|---|---|---|---|---|
| **LED** (the claim) | 15 | **0** | 1 | 14 | **0.0%** |
| **SAME_DAY** | 10 | **5** | 2 | 3 | **50.0%** |
| **LAGGED** (null control) | 100 | 9 | 21 | 70 | **9.0%** |
| **PLACEBO** (random past dates) | 25 | **0** | 2 | 23 | **0.0%** |

The instrument recomputed **identically** to what production stored — LED: 14 stored
zeros and 1 stored NULL reproduced exactly, SAME_DAY: 5 stored ones reproduced exactly.
The referee is a deterministic function of the row; there is no evaluation-time drift
from Wikimedia's publication lag. That hypothesis is dead, and it was worth killing.

## SCORING THE SEALED EXPECTATIONS

**E1 — Branch composition. Sealed: ≥8 of 14 in branches (1)+(3); ≤4 in branch (2). → CONFIRMED, with one mechanism wrong.**
Observed: branch (1) *no qualifying surge* = **13**; branch (3) *outside the ±14d band* = **0**;
branch (2) *arrival precedes detection* = **1**.
The numbers land inside the sealed range, but **my stated mechanism was wrong**: I expected
branch (3) to carry part of the load. It carried none. Defect 3 (long leads structurally
penalised) is real in the code and **empirically inert on this cohort** — the function
fails *earlier*, at surge detection, so execution never reaches the band comparison. A
right answer for a partly wrong reason, recorded as such.

**E2 — Sensitivity floor. Sealed: ≥5 of 14 sub-200-view articles. → CONFIRMED, exactly at the sealed point estimate.**
5 of 15 LED topics have an en-Wikipedia article whose best day in the entire window never
reaches 200 views: `karoline` (peak 17), `court rulings` (17), `verde` (102), `nestjs` (122),
`pytest` (180). These are **structurally unrefereeable** — no detection date could ever have
corroborated them.

A **second, unsealed blindness** appeared next to it, and it is larger. Five more LED rows
fail the *relative* 3× threshold rather than the absolute floor, because the article is
already busy: `strait of hormuz` peak 12,964 vs threshold 14,749 (88% of the bar);
`white house` 11,265 vs 11,943 (94%); `spain` 27,572 vs 31,491 (88%); `paramount-warner`
6,524 vs 8,776 (74%); `webhook` 802 vs 1,154 (70%). Six of the ten near-misses land within
30% of their own threshold. So the LED cohort splits into **too small to see** and
**too busy to spike** — and the middle band the referee can actually adjudicate is nearly
empty. This was not in the pre-registration and is reported as a new finding, not folded
into E2.

**E3 — Effect on the served metric. Sealed: `refereeCheckedPct` falls from 93.3% to below 40%, plausibly below the 20% floor. → CONFIRMED, and more extreme than sealed.**
Under the corrected definition (checked = CORROBORATED + PRECEDES, the two worlds where the
instrument actually rendered a verdict), LED checked = **1 of 15 = 6.7%** — far below the
20% floor. `refereeState` must flip from `exercised_and_inconclusive` to **`not_exercised`**.

**E4 — The null control. Sealed: LAGGED corroborates at a similarly low rate (≤20%), implying the referee has little discriminating power. → NUMBER CONFIRMED, INFERENCE REFUTED.**
LAGGED corroborated at **9.0%**, inside the sealed ≤20% band. But the conclusion I attached
to that number is **wrong**, and two arms I did not designate as decisive are what refute it:

- **PLACEBO = 0 of 25.** A referee with no discriminating power would corroborate random
  date-anchors at roughly its base rate. It corroborates them at zero. It is not saying
  "yes" indiscriminately.
- **SAME_DAY = 5 of 10.** A referee with no discriminating power could not hit 50% on any
  cohort. It is not saying "no" indiscriminately either.

So the referee discriminates. It simply cannot see the LED cohort. **E4's prediction was
numerically right and its conclusion was wrong**, and that is precisely the error the
pre-registration existed to catch. It stays on the record.

**A defect in the pre-registration itself.** E4's decision-rule row 2 reads "LAGGED
corroborates materially (> 30%)" without naming a denominator. On the naive denominator
LAGGED is 9.0%; on the refereeable denominator it is exactly 30.0% — sitting on the
threshold from opposite sides depending on a choice I left unspecified. I am not resolving
that ambiguity now, because resolving it after seeing the data is the exact move the seal
forbids. Recorded as a drafting defect: **future pre-registrations must state the
denominator with the threshold.**

## WHICH DECISION-RULE ROW FIRES

**Row 3 — "Branch table dominated by (1)/(3) + sub-200-view articles → the referee is
blind to our cohort → a coverage disclosure, not a verdict. Proceed to `wiki-v3` + GDELT."**

Row 1 (no discriminating power → fix or retire) is **not** supported: placebo 0% and
SAME_DAY 50% show real specificity. Row 2 (the wins are in real trouble) is **not**
supported: it requires LAGGED corroborating materially while LED stays near zero, and
LAGGED is 9.0% naive.

Per the binding rule and per the sealed constraints: **no ledger row, verdict, lead, date,
or rate was changed by this exercise, and none may be.** The citation bar (majority
corroboration + minimum checks + query quality, sealed constants as of 2026-08-20) governs
regardless of these findings, and it currently blocks — correctly, and now for the
*accurate* reason.

## WHY THE COHORTS DIFFER — the load-bearing confound

SAME_DAY has **zero** sub-floor articles. LED has **five**, a third of the cohort. The
referee corroborates precisely the cohort it can see (large, already-mainstream topics
where detection and breakout coincide) and is blind on precisely the cohort where the
product claims its edge (niche, early, pre-mainstream). That is sealed defect 4 —
*instrument coverage anti-correlated with the population it adjudicates* — now confirmed
quantitatively rather than argued from the constants.

This also means the 0-of-15 **cannot** be read as evidence against the LED wins, and
equally **cannot** be read as evidence for them. It is an absence of measurement. Under
§15a that is reported as absence, never as a zero.

## HARNESS DEFECT FOUND AND FIXED MID-RUN (disclosed, not quietly patched)

Run 1's placebo arm shifted detection dates **forward or backward**. Forward shifts pushed
the window past the last published pageview day, so 14 of 25 rows returned NO_CURVE — the
control silently lost power instead of failing loudly, and reported 1 corroboration on an
effective n of 9. The arm was re-run **backward-only** (`REFEREE_PLACEBO_BACKWARD_2026-08-20.json`),
where every window sits inside published data: **0 of 25 corroborated, 22 rows usable.**
The backward-only figure is the one cited above. Run 1's placebo number is superseded and
is retained in the raw JSON rather than deleted.

## WHAT HAPPENS NEXT (no code shipped by this document)

1. **Correct `refereeCheckedPct` and `refereeState`** to count only CORROBORATED + PRECEDES.
   The served number moves 93.3% → 6.7% and the state moves to `not_exercised`. This is the
   softer-sounding correction the pre-registration anticipated and pre-justified.
2. **Replace the `citationBlockReason` sentence.** The current text says the referee
   "returned non-confirmation on 14 of 15" — replace with the count of genuine refutations
   (1) and the count of unmeasurable rows (14), naming both blindness modes.
3. **Proceed to `wiki-v3` + GDELT as a second arm** (task #15) under the sealed constraints:
   a NEW `param_version`, never a tune of `wiki-v2`; `SURGE_MIN_ABS` is **not** lowered; the
   `wiki-v2` 0-of-15 result travels alongside permanently. The right repair for a
   floor-bound instrument is more coverage, and the relative-threshold blindness found here
   says multi-language wikis alone will not fix the busy-article half.
4. **Report the SAME_DAY 50% corroboration** — it is the first independent corroboration
   evidence this ledger has produced, and it was invisible while the metric reported LED only.

---
*Read-only. No ledger row was written, updated, or deleted. The harness asserts SELECT-only
at runtime.*

**PIT SEAL:** `kind=assessment`, `item_key=RESULT-referee-decomposition-2026-08-20`, `row_sha256 bb5bf9f597e582967dcb4e9dcf4d9ea5e99573c31a9ebe3074d5879fbb26220f`, `text_sha256 ce5120925b9e6dde7f08009d7166c5aa549b1a88fb00556541ed5b7a4dc483fe` (9387 chars, this file through the line before this note). Sealed AFTER the run, referencing the pre-registration row `572adc8f..` sealed BEFORE it.
