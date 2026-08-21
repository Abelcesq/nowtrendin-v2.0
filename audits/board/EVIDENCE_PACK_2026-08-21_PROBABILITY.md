# EVIDENCE PACK — THE BASE RATE PANEL + THE D RETIREMENT RULE
### Chairman-commissioned, 2026-08-21. Nine seats. Material: Part A (D retirement pre-registration),
### Part B (Base Rate Panel design), and the Chairman's framing of the goal.

---

## 0. THE GOAL, IN THE CHAIRMAN'S OWN TERMS (read this first; everything else is subordinate)

Two things are being decided, and they must not be confused with each other.

**(1) THE RETIREMENT RULE.** Today, if the shadow trial comes back saying Dark Matter does not
work, **nothing happens** — there is always another repair to try. The Buyer's Desk named this:
*"a demo with a long calendar, not a trial."* The remedy is to write down NOW, while the answer is
genuinely unknown, that if the candidate feeds do not beat a coin flip by a fixed date, **D is
demoted from a scored component to a research indicator.** Deciding it in advance is what makes it
real.

**(2) THE PROBABILITY SECTION — AND THE REFRAME THAT MAKES IT LEGITIMATE.**
The Chairman's ruling, verbatim in substance:

> *"Although there was an initial impression that our system can 'predict', after studying the FIFA
> World Cup data, it is clear attempting to guess whether something will trend or not is
> SPECULATIVE and that is not aligned to any of our core principles. So the issue here is not
> whether the dark matter is valuable or not, the question is how we use it to have our
> application, mechanisms and data accurately reflect the MOVEMENT."*

The ask is therefore **NOT** a forecast. It is a **held-out probability section**, separate from
scoring, that never touches the score, displayed under "How the scoring works" on **every trend,
market signal, and crypto** item, showing the probability of an item gaining attention — and
**updating and trackable** over time.

**THE ACTUARIAL REFRAME (the load-bearing idea).** An actuary does not predict that YOUR house will
burn down. They state the **frequency in your risk class**. The first is prophecy — ruled out by
the World Cup study. The second is a **measurement of the historical record**, which is exactly
what this product already does, and it is computable today from data we already hold.

> Not *"will this trend?"* but *"of the topics that historically looked like this one at this point
> in their lifecycle, what fraction subsequently arrived, and when?"*

**Judge every item below against that distinction.** Any wording that implies a forecast about the
specific item in front of the user is a failure of the whole design, not a copy problem.

---

## 1. GOVERNANCE CONFLICT — THE FIRST QUESTION FOR THE BOARD

**Part A collides with a document we have already sealed.**

| | Sealed `D_KILL_CRITERION_2026-08-20` (PIT `caf62911..`) | Proposed Part A |
|---|---|---|
| Date | **2027-02-28** interim (then 05-31, final 11-30) | **2026-11-30** |
| N | **≥ 20 per compared arm** | **≥ 120 resolved** |
| Test | race rate vs both nulls (≥10pt) **AND** median lead ≥3d vs control | **AUC** of `d_at_enroll` (95% CI LB > 0.50) **AND** LR χ² (p<0.05) |
| Under-N | **UNSCORABLE → defers**, and a still-UNSCORABLE FINAL demotes | **N<120 = FAIL, not extension** |

Our seal states: *"This criterion may be amended ONLY by a superseding sealed entry that cites this
row, made BEFORE the readout that would test it. An amendment made after a readout is void by
construction."* No readout has occurred, so a superseding seal is **available and legitimate**.
But two live criteria is worse than one. **Seats must rule: supersede, harmonise, or reject.**

**Note the substantive disagreement, not just the numbers.** The sealed rule treats under-N as
UNSCORABLE-and-defer (with a terminal demotion if still unscorable at the FINAL readout). Part A
treats under-N as an immediate FAIL, invoking **operational futility** — "the inability to determine
whether an intervention works," distinct from statistical futility. Which is the correct posture is
a genuine question, not a drafting detail.

**A verified contamination that binds Part A and NOT the sealed rule.** Round 4 established
(Guardian + Challenger, independently; confirmed at the return statement) that `compute_dark_matter`
returns **`0.0` on the unmeasured path**, and that this zero is served and enters the composite.
Part A's primary test is an **AUC on `d_at_enroll`** — computed on D magnitudes directly — so a
structural zero on measured-blind rows corrupts it, and the test would partly measure *"does having
author-bearing signal correlate with arrival."* The sealed rule compares **race rates and lead
times between arms** and never reads a D magnitude, so it is not contaminated by this defect.
Part A's own population clause (rows enrolled after `d_at_enroll` stamping goes live) excludes the
NULL stratum but **does not** exclude the fabricated zero.

**⚠ CORRECTION ISSUED MID-REVIEW (2026-08-21) — the author was wrong, verify the rest accordingly.**
This pack originally asserted that **`d_at_enroll` does not exist**. **IT EXISTS.** Column ALTER at
`accuracy_ledger_enhanced.py:134`, written at `:359-371`, shipped under the Chairman-approved
2026-08-17 step-0 batch. The author repeated the claim from the outside analysis **without
verifying it** — the §10a failure round 4 was convened over. Any seat that reasoned from "the
population field has never been stamped" should re-reason. `tools/d_plumbing_ab.py` genuinely does
not exist (verified absent).

**AND THE MIRROR DEFECT THE PACK DID NOT CATCH IN THE DESIGN IT IS REVIEWING:** Part B claims the
panel is *"point-in-time by construction via `as_of(t)` on the PIT store."* **`pit_store.py` has no
point-in-time read function.** Its API is `record` / `seal_day` / `seal_pending` / `verify` /
`status` / `completeness` / `anchors`, and its own docstring says the store is *"HELD-OUT and
WRITE-ONLY from the score sinks: nothing ever READS this store."* The panel's central architectural
guarantee references an API that has never been written. Seats should treat PIT-backed
reproducibility as an ASPIRATION, not a property.

---

## 2. PART B — THE BASE RATE PANEL AS PROPOSED (summarise fairly, then attack)

**Engine: Kaplan-Meier per cell + Bühlmann-Straub credibility across cells. NOT a GLM.**

- **Why not a GLM on "did it arrive?"** The data is **heavily right-censored** — the 365-day
  patience window (§14) means most rows are still pending. A binary GLM must do something with
  pending rows and both options are wrong **in opposite directions**: coding pending as
  `arrived = 0` is *inconsistent* (more data does not fix it) and understates arrival; dropping
  pending rows conditions on having resolved and overstates it. Cited magnitude: on the standard
  `lung` dataset with *modest* censoring, naive one-year = 47% vs Kaplan-Meier 41%. Our censoring
  is far heavier.
- **KM** gives `1 − S(t)` per cohort, handles censoring natively, Greenwood gives variance. Use
  **log-log transformed CIs** — the linear form can fall outside (0,1) and has poor tail coverage
  exactly where the risk set has collapsed.
- **Bühlmann-Straub** solves the sparse-cell problem. `Z = m/(m+K)`, `K = EPV/VHM`. The property
  that matters: **if our rating factors do not actually separate arrival rates, VHM → 0, K → ∞,
  Z → 0, and the model correctly collapses to the portfolio base rate** rather than producing
  confident nonsense on twelve observations. Exposure is **observed topic-days at risk**, not topic
  count — which is why *Straub* and not plain Bühlmann.
- **Credibility counts EVENTS, not observations.** A cell with 5,000 topics and 12 arrivals has
  **12 units of credibility**. Classical full-credibility standard: **1,082 arrivals**
  (p=90%, k=5%; (1.645/0.05)² = 1082.4). Very few cells will be near credible and the panel should
  say so rather than hide it.
- **Rating cells** from fields we already hold: maturity (`topic_lifecycle`) · corroboration at
  first sighting (1 / 2–4 / 5+ outlets, the §15a quorum threshold) · provenance tier
  (`platform_tier`, the D-vs-M router) · category (`_category_for`, display-only, **held out**).
- **NO "suppress cells with n<50" rule.** Credibility theory *replaces* the minimum-cell-size
  threshold — which is why no standards body publishes one. **Display Z.** A cell reading
  *"12% (Z = 0.08 — essentially the portfolio base rate)"* is honest and informative; a suppressed
  cell tells the user nothing and looks like a bug. This is §16a honest-absence discipline applied
  to a rate.

**What the design explicitly REFUSES to build, and why:**
- **EVT / Generalized Pareto — NO.** Satisfactory POT performance is associated with **1,000+
  exceedances**; at a 95th-percentile threshold on a few thousand rows we would have tens, and most
  rows are censored so the effective tail sample is smaller still. Conceptual mismatch: EVT models
  the tail of a **magnitude** distribution; our outcome is a **time** under a **fixed 365-day
  administrative boundary** — our design choice, not a heavy tail to extrapolate. Honest statement
  about beyond-365-day behaviour: *"we did not observe it."*
- **Copulas — PREMATURE.** Our problem is **marginal** (one topic's arrival). Tail-dependence
  estimation needs far more data than marginal fitting. **Li's Gaussian copula failed precisely by
  fitting a dependence structure on too short and too benign a history** — a fair description of
  where we are. If it ever matters: first test whether portfolio-level arrival counts are
  overdispersed relative to independence, then use a **shared-frailty survival model** (native to
  correlated event times), and **never the Gaussian copula**.
- **Monte Carlo for the intervals — unnecessary.** Greenwood gives them analytically; KM+Greenwood
  already exist in `ledger_survival`.

**⚠ THE LIVE BIAS THE DESIGN FLAGS AGAINST ITSELF — IMMORTAL TIME.**
`LEDGER_ENROLL_RECENT_DAYS = 14` first-crossing enrollment creates an interval during which arrival
was **impossible by construction** — between a topic's true origin and the moment it crossed the
floor and entered the panel. Textbook immortal time bias. The Catalogue of Bias documents corrected
cases where a hazard ratio moved from **0.74 to 1.97 — reversing the sign of the conclusion.** The
`pre_broken` split (§14) was an instinctive partial correction; this names the mechanism. **Must be
checked before anything publishes, and it is checkable now.**

**WHY IT SHIPS HONESTLY WITH DISCRIMINATION UNPROVEN — the Murphy decomposition.**
`BS = REL − RES + UNC`. Set stated probability = observed frequency in every bin → **REL = 0**.
Let every bin's frequency equal the overall base rate → **RES = 0**, `BS = UNC`. That forecast is
**perfectly honest and completely uninformative** — the **climatological forecast**, which Gneiting,
Balabdaoui & Raftery construct explicitly as calibrated yet useless for discriminating between
occasions. So the two properties come apart cleanly and only one is in doubt:
- **Discrimination** — can we rank topics better than chance? **OPEN. Currently unproven.**
- **Calibration** — when we say 20%, does 20% happen? **Separate, and achievable now.**

Pre-commit which of three statements we will make: `BSS≈0, REL≈0, RES≈0` → *"our rates are
calibrated; we have not demonstrated skill against the base rate"* · `BSS≈0, REL>0, RES>0` → we DO
discriminate and miscalibration is cancelling it, **fixable by isotonic/PAV recalibration**
(resolution is invariant to monotone recalibration; reliability is not) · `BSS<0` → **withdraw**.
**Freeze the climatology reference in the register BEFORE computing any BSS** — sample vs long-run
vs regime-conditional give materially different BSS, so **this is a place where skill can be
manufactured.**

**Governance reason for proper scoring rules:** under a strictly proper rule, truth-telling is the
**unique** maximiser of expected score. Hedging toward 50% to look safe, or toward extremes to look
decisive, is strictly penalised in expectation. **The incentive to misreport is removed by
construction rather than by policy.**

**Measurement traps the design pre-empts:** never publish a bare Brier (a *lower* Brier can mean a
*worse-calibrated* model with more discriminatory power — publish REL/RES/UNC separately) · use
**bias-corrected** components (plug-in estimates are biased; bias-corrected are negligible above
n>60, naive need n>300) · reliability diagrams need **consistency bars** or **CORP** (Dimitriadis,
Gneiting & Jordan, PNAS 2021); prefer the **attributes diagram** which overlays no-resolution and
no-skill lines · **compute observed frequencies via Kaplan-Meier, never naive proportions**, or the
calibration check inherits the same censoring bias and we validate a biased model against a biased
benchmark and see agreement.

**Three surfaces:** Trend (Google Trends breakout, best data, build first) · Market Signal (realized
EOD direction, build second) · **Crypto reads ABSENT by construction** — the 2026-08-01 finding
stands that no source in the stack delivers per-coin money movement, so publishing a base rate over
that ledger would **dress the gap in a percentage**.

**Architecture:** held out absolutely (reads ledgers + PIT, never feeds a score — the
`signal_analysis.py` precedent) · **point-in-time by construction** via `as_of(t)` on the PIT store
so a rate shown on day T uses only what was knowable at T · method confidential per ruling (e) —
insurance discloses rating factors, never full GLM coefficients.

**One documentation correction claimed:** *do not cite SR 11-7 as live guidance* — asserted to have
been replaced by revised interagency guidance on **2026-04-17**. **UNVERIFIED BY US.**

---

## 3. WHAT THE BOARD IS ASKED

1. **The governance conflict (§1).** Supersede the sealed criterion, harmonise the two, or reject
   Part A? And is **operational futility (N<120 = FAIL)** the right posture, or is the sealed
   UNSCORABLE-and-defer posture right? Note Part A's own binding/non-binding argument: the futility
   literature's cautionary case is **LUME-Lung 2**, where a *non-binding* boundary was considered
   and the trial continued anyway — which is exactly the failure the Buyer's Desk named. Note also
   that Part A forbids interim looks because computing conditional power off the *currently
   observed* effect inflates Type II error from 0.10 to roughly **0.306 across six looks**.
2. **The power paragraph is deliberately blank.** Part A requires that the power to detect a true
   AUC of 0.60 at N=120 be **computed, not asserted**, before sealing — copying Basel's traffic-light
   framework not for its thresholds but because it **documents its own two error rates**. Is a seal
   with a blank power paragraph sealable at all?
3. **Does the actuarial reframe (§0) actually escape the speculation trap**, or does a percentage
   next to a topic read as a forecast to a user no matter what the copy says?
4. **Is the engine right?** KM + Bühlmann-Straub vs alternatives. Is the EVT and copula refusal
   correct, or is it declining tools we will need?
5. **Immortal time bias** — is the diagnosis right, and what is the correction?
6. **Does the Murphy argument license shipping a calibrated-but-uninformative v1**, or is
   "calibrated and uninformative" a product nobody should be shown?
7. **What does this do to the round-4 open set** — the D score-side zero, the NULL stratum, the
   register's tautological enforcers, the laptop-local gates, and AB-ATTRIBUTION?

**Standing constraints:** no circular metrics (N never feeds or validates the Gradient Score) ·
held-out means held out · flag-never-force · measurement not advice · honest absence (§16a) ·
score-affecting changes are backtest-gated and board-reviewed (§16a stage 3) · the §15a A3 hard
fence — a correctly-measured mainstream 96 is still LAGGED in the ledger, and a thermometer reading
is never a forecast.
