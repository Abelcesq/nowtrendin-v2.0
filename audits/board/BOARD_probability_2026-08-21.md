# BOARD ROUND 5 — COLLATION FOR THE CHAIRMAN
### Nine seats, 2026-08-21, on the Base Rate Panel (Part B) + the D Retirement Rule (Part A).
### Seats ran in parallel, blind to each other. COLLATION, not a blend. No recommendation.

---

## 1. UNANIMOUS — nine seats, nine routes, one conclusion

**REJECT Part A. The sealed `D_KILL_CRITERION_2026-08-20` stands unamended.**

Not one seat dissented, and no two reached it the same way:

| Seat | Route to rejection |
|---|---|
| **Statistician** | **The test is UNDEFINED at its own readout date.** The only non-arrival verdict is `FALSE_POSITIVE`, reachable *only* by 365-day timeout. At 2026-11-30 the resolved set contains **zero negatives**. AUC over a single-class outcome is undefined; LR χ² has no outcome variation. *"Part A does not merely guarantee a FAIL — there is no test."* |
| **Operator** | **2026-11-30 IS `ENROLL_CLOSE`** (`shadow_ledger.py:56`). With `SHADOW_PATIENCE_DAYS=365`, zero rows have completed patience. N≥120 is arithmetically unreachable ⇒ a **pre-scheduled demotion wearing a futility rule's clothes.** |
| **Economist** | Computed the blank power paragraph: **~46%** at N=120; **N≈541** for 80%. *"Demotes D by arithmetic."* |
| **Statistician** (independently) | Power **0.471 / 0.387 / 0.210** by case-control split; realistic ≈**0.39**, joint IUT ≈**0.37**. N for 80% = **258 / 335 / 735**. |
| **Guardian** | The sealed rule **never reads a D magnitude**, so it is structurally immune to the fabricated `0.0`; Part A's AUC reads it directly. *"Do not trade a clean test for a sophisticated one."* |
| **Challenger** | AUC needs a binary outcome ⇒ forces **either** dropping pending (overstates) **or** coding pending as 0 (inconsistent) — *the exact two errors Part B rejects the GLM for.* The two halves of the pack contradict each other. |
| **Executioner** | **CUT.** `d_at_enroll` is stamped from `dark_matter_score` with **no `d_measured_at_enroll` companion**; live `unmeasured_fraction = 0.752`. An AUC on a field that is a fabricated constant for ¾ of rows is an AUC of "did the author-resolution path fire." |
| **Forecaster** | **There are not two live criteria — there is one, and a memo.** Part A is not sealed, has no PIT row, does not cite `caf62911..`, is not in the register. Supersession is *available*, not *exercised*. |
| **Expansionist** | (did not rule on Part A; ruled the panel's build) |

**Also unanimous where raised:** a seal with a **blank power paragraph is not sealable** (Guardian, Forecaster, Economist, Statistician). The blank *is* the preserved degree of freedom.

**Also unanimous:** the sealed **UNSCORABLE-and-defer** posture is correct and Part A's `N<120 = FAIL` is not. Guardian: it *"makes non-enrollment a weapon — anyone who wants D dead achieves it by not feeding the trial."* Statistician: *"N is a property of throughput, not of the hypothesis."* The sealed rule **already** carries operational futility (a still-UNSCORABLE FINAL demotes anyway).

---

## 2. THE NUMBER THE CHAIRMAN MUST SEE FIRST (Economist, live ledger 2026-08-21)

> Resolved **129** · LED **15** · tracked races **58** · pending 1,356 · KM eventual confirmation **4.2%**
> false positives **0 (structural)** · **LED wins corroborated by the independent referee: 0 of 15**
> **Tracked-race rate 25.9%, 95% Wilson CI [16.3%, 38.4%], against a 50% random-order null —
> the interval EXCLUDES the coin flip FROM BELOW.**

On the only skill comparison currently available, the detector is **significantly worse than random ordering**. The Economist's ruling: the pre-committed three-statement menu **omits the branch that is currently true.** The honest v1 sentence is not *"skill unproven"* — it is *"skill has been measured against the only available null and we are behind it."* A panel shipped without that sentence is the Reinhart-Rogoff signature; shipped with it, and with the seal standing, it is an honest actuarial product.

**Credibility, with real numbers (Economist + Statistician, independently, agreeing):**

| Unit | events | Z |
|---|---|---|
| Entire portfolio pooled | 58–66 | **0.231 – 0.247** |
| Median cell, 27-cell design | ~2 | **0.045 – 0.053** |
| Proposed 4-factor (~216–270 cells) | <1 | **0.014 – 0.03** |

**3.4 years for ONE credible portfolio cell. ~92 years for 27 cells.** Full portfolio credibility is **11–20 years** out. Both seats: v1 **is** climatology at ~95% weight in every cell, by arithmetic — *"the portfolio mean, displayed 216 times with different labels."*

---

## 3. FACTUAL CORRECTIONS TO MY OWN PACK (found by seats, verified by me)

| Claim in the pack | Truth |
|---|---|
| *"`d_at_enroll` does not exist"* | **FALSE.** `accuracy_ledger_enhanced.py:134` ALTER, `:359-371` stamped, commit `cb8f183`, live 4 days. **Found by 6 of 9 seats.** I repeated it from the outside analysis without verifying — the §10a failure round 4 was convened over. |
| *"point-in-time by construction via `as_of(t)`"* | **FALSE — and it was Part B's claim, which my pack passed through.** `pit_store.py` has **no reader**; its docstring says *"nothing ever READS this store."* Our own DDQ already said so (`FISD_DDQ_RESPONSES.md:21`). |
| *"no source delivers per-coin money movement"* | **Overstated.** §1 says all 12 `money_data_absent` (Guardian, correct on the current instrument); §2 says a subset is buildable at $0 (Expansionist). Honest form: **absent today, buildable for a subset, unbuilt.** |

---

## 4. DISAGREEMENTS — PRESERVED, NOT MERGED

**4a. THE SEAL HASH — a direct factual conflict that must be settled by a third check.**
- **Economist (round 4):** reproduced `text_sha256 403b6a7e..` from `body[:4065]`; seal cryptographically intact.
- **Forecaster (today):** **not reproducible** across 36 decode/marker/whitespace/encode recipes, on a file with one commit, never edited.
One is wrong. The answer decides whether the D kill criterion is verifiable by anyone outside this room. **Unresolved. Needs a decisive independent run, not a vote.**

**4b. IMMORTAL TIME — three seats, three different mechanisms and directions.**
- **Challenger:** real; inflates lead time (*"the bias runs our way on the number we sell"*).
- **Statistician:** confirmed but **mechanism misidentified** — it is the *maturity exclusion*, not floor-crossing. Direction: **understates** early arrival. Magnitude ~3% at 365d but **up to 30% relative at 30d**. Net sign **UNIDENTIFIED** because the filter is leaky.
- **Economist:** **rejects the diagnosis as stated** — classic immortal time is a *between-arm* misallocation; the panel has no arms. Real mechanisms are left-truncation + depletion of susceptibles, both **deflating**. Calls the borrowed 0.74→1.97 figure *"the narrative fallacy operating inside a bias audit."*
- **All three agree** `pre_broken` corrects **none** of it. Statistician: *"REFUTE."* Strike that sentence.
- **Operator dissents on priority:** the larger bias is **S2 — enrollment capped at 20/cycle (`LEDGER_RECORD_TOP`), correlated with news volume**, so we systematically under-sample the highest-arrival cycles. *Correcting immortal time alone yields a number still wrong, now carrying a correction certificate.*

**4c. CREDIBILITY ENGINE — Guardian endorses, Statistician rejects the construction.**
- **Guardian:** `Z→0` collapse is *"§16a expressed in credibility form"* — endorsed.
- **Statistician:** **framework splice.** Bühlmann-Straub is derived for exposure-weighted means of conditionally-independent observations with variance σ²/m; a KM point estimate is none of those. And the pack **contradicts itself**: exposure-in-topic-days would give **Z ≈ 0.99 on twelve events** — *"confident nonsense produced by the mechanism advertised to prevent it."* The live hazard is not `VHM→0⇒Z→0` (absence of *signal*) but **`EPV→0 ⇒ Z→1` on a single row** (absence of *data*), which is unguarded. Replacement: **piecewise-exponential person-time Poisson credibility**, where λ̂ = d/e *is* an exposure-weighted mean and Bühlmann-Straub applies exactly, with overdispersed EPV and a cap `Z ≤ √(events/1082)`.

**4d. CRYPTO** — Guardian/Economist: absent (2 resolved, 0 clean). Expansionist: ship **per-coin**, 4 with a rate, 8 absent; blanket-absent is *"the A3 floor-end defect in a new costume."* Economist adds: **the same test disqualifies Market** — 29 resolved, 7 clean, against the ledger's own 30-clean precondition.

---

## 5. FINDINGS NO OTHER SEAT REACHED

- **GUARDIAN F-1 — the Market surface violates a standing board ruling, in code, in his own voice.** `arrival_clock.py`: *"NOT PRICE. If the confirming event were a price move, then 'we detected it early' would mean 'we were early to the move' — **a trading record with the P&L column hidden.**"* `market_accuracy_ledger` grades on EOD direction. A probability over it is a **return forecast**. **Surface #2 must be built on the volume clock or not built.**
- **GUARDIAN F-2 / EXECUTIONER / CHALLENGER — the event definition is env-flippable.** `ARRIVAL_VOL_MULT = getenv(...,"3.0")`, **not** in `SEALED_CONSTANTS`. Also `LEDGER_TIMEOUT_DAYS` and `LEDGER_LEAD_MAX_DAYS`. A base rate is a function of its event definition.
- **CHALLENGER — the event counted is not "gaining attention."** Near-miss LAGGED admits `lead_days >= -7`: a topic whose breakout preceded our first sighting by up to 7 days counts as an arrival at **t=0**. *"The actuary's analogue would be counting houses that burned down the week before the policy was written."*
- **CHALLENGER — `d_at_enroll` is LOOKAHEAD.** Stamped at enrollment E; the clock starts at first-seen D0, **up to 14 days earlier**. A predictor measured after the outcome clock starts is not a predictor.
- **STATISTICIAN — a landmine for the first caller.** `ledger_survival.py:95` `tt = max(0, int(row[0]))` clamps negative leads to zero. 44 of 59 LAGGED were pre-broken ⇒ **~75% would land at t=0, fabricating a day-zero arrival spike.** `flow_ledger.py:661` already handles the analogue correctly.
- **STATISTICIAN — non-informative censoring FAILS.** `fastlane_recheck` **preferentially re-checks near-misses** — rows selected *because they look close to arriving*. Ascertainment intensity is outcome-correlated ⇒ pooled KM biased **upward**. Not in the pack.
- **STATISTICIAN — "KM inside a Brier" breaks the identity.** BS = REL − RES + UNC is an algebraic identity of the empirical MSE; substituting a group-level KM estimate makes the components sum to nothing. Replacement: **Graf IPCW Brier** at a sealed horizon, decomposed with the same weights, covariate-adjusted Ĝ, **CORP/PAV** instead of bins.
- **OPERATOR S3 — our P&L is wired into our accuracy denominator.** A timeout resolves FALSE_POSITIVE **free**; an LED win requires a **paid Apify fetch**. Under budget pressure the ledger manufactures misses cheaply and stops buying wins — and **no row records which regime produced it**, so it is unauditable. Stamp `resolution_mode` at resolution; it is unrecoverable afterwards.
- **OPERATOR E4 — D may already be a constant.** On the >90% unmeasured stratum D contributes a fixed `0.0`. **The score impact of demoting D may be near zero.** One query would tell us whether four rounds have debated the retirement of a constant.
- **ECONOMIST P2 — don't freeze climatology; use the nulls already sealed.** `null_volume` and `null_random` from `SHADOW_TRIAL_PREREG` are adversarially chosen and unmovable. *Removes the choice rather than freezing one arbitrary option.*
- **ECONOMIST item 9 — the proper-scoring-rule claim is a CATEGORY ERROR.** Proper scoring disciplines *the forecaster being scored*; it says nothing about an adversary who moves the input and is never scored. Moving a topic into the high-arrival cell costs **five outlets with five distinct titles** — a press-release budget, against a threshold **we published ourselves** in §15a. **Strike the sentence.**
- **ECONOMIST item 8 — REFLEXIVITY, a new circularity through a different door.** The standing invariant is *N never feeds the score*. The new loop is **the display feeding the OUTCOME that validates the display**. Needs its own scale-triggered invariant.
- **ECONOMIST P4 — the tail instrument is on the wrong axis.** Refusing EVT for *time* is right; concluding we have no tail instrument is a non-sequitur. **Attention is Extremistan in MAGNITUDE.** Report `P(arrival)` and `Magnitude | arrival` **separately, never multiplied.**
- **EXPANSIONIST — two of four rating factors are dead.** `breadth_at_enroll` is **NULL on every live row** (`LEDGER_AB_D9` defaults `"0"`, so the branch that passes it never runs; `topic_signals` prunes ⇒ unrecoverable). `category` (`_category_for`) assigns cells by **dyno warmth** (33%↔68% swing). Buyer's Desk: *"two users on two dynos see different base rates for the same topic in the same minute, and neither is wrong."*
- **BUYER'S DESK — `author_history` IS a person-level profile.** Keyed `(author, platform, community)` with `first_seen_at` + `post_count`. `PII_POLICY.md:24-25` says *"not aggregated into person-level profiles."* **The written control is not the actual control** — App Annie exposure, instant-kill gate. And `is_first_timer` from it feeds D at 0.216 of Detection.
- **FORECASTER Finding 1 — the receipt.** He mutated **every binding number** in the sealed criterion (the exact Part A substitution) and `_enforcer_live('sealed')` returned **GREEN**. Only deleting the string `2027-02-28` turns it red. **Part A could be installed inside the sealed document today and the gate would pass.**
- **OPERATOR S7 — the metric that names the disease.** *"The org is now generating board rounds faster than it is generating resolved ledger rows."* Four rounds in four days; 111 resolved rows in thirteen months. **Make the next round's convening condition a DATA event, not a calendar date.**

---

## 6. DECISION TABLE

| Item | Chal | Guard | Expan | Buyer | Exec | Econ | Oper | Stat | Fore |
|---|---|---|---|---|---|---|---|---|---|
| **Part A as binding** | REJ | REJ | — | ~30% theatre | **CUT** | REJ | REJ | REJ | REJ |
| Blank power paragraph | — | REJ | — | — | — | REJ | no | REJ | REJ |
| N<120 = FAIL | REJ | REJ | — | — | — | REJ | REJ | REJ | REJ |
| Actuarial reframe escapes speculation | REJ as spec'd | cohort ✓ / per-item ✗ | — | **sellable** | — | A-W-C | struct ✓ / inventory ✗ | — | ✓ w/ seal |
| KM engine | REJ (obs-building) | A-W-C | — | — | SHIP | A-W-C | A-W-C | A-W-C | reuse it |
| Bühlmann-Straub | REJ (gameable) | APPROVE | REJ at cell count | — | defer | A-W-C | Z≈0.045 | **REJ — splice** | seal it |
| EVT refusal | — | APPROVE | — | — | endorse | ✓ reason / ✗ conclusion | — | APPROVE, delete the 1,000 figure | — |
| Copula refusal | **destroys the Z estimator** | APPROVE | — | — | endorse | APPROVE | — | APPROVE but interval problem is NOW | — |
| Calibrated-but-uninformative v1 | REJ (binning) | A-W-C | — | **sellable if said first** | — | A-W-C, menu incomplete | REJ at n=13 | A-W-C | A-W-C |
| Panel ahead of round-4 open set | — | **REJECT** | — | 4 items first | **Tier 5** | — | — | 2 prereqs | — |
| Crypto absent | — | APPROVE | **REJ premise** | — | CUT surface | APPROVE + Market too | — | — | seal it |

---

## 7. WHAT EVERY SEAT AGREED ON

The **EVT and copula refusals are correct** (8 of 8 who ruled). **Display Z, never suppress** (§16a in credibility form). **Reuse `ledger_survival.py`** — it is genuinely excellent, validated against published Freireich (χ²=16.79, p=4.2e-05), held-out, pure. **Trend surface only.** **The actuarial reframe is logically sound** — the dispute is inventory and rendering, not logic. And **the reversal of the accuracy lead from 27.1% to 5.0% is the single most creditworthy act in this record** (Buyer's Desk).

## 8. THE TWO PREREQUISITES EVERY TECHNICAL SEAT NAMED INDEPENDENTLY

1. **Stamp `d_measured_at_enroll`** beside `d_at_enroll` — same SELECT, one line. `d_measured` already exists in `velocity_scores`. Forward-only: **every day of delay is permanently un-triageable population.**
2. **Add an immutable `enrolled_at`** column — required for any left-truncated estimator and for epoch stratification. `last_checked` is overwritten by every sweep.
