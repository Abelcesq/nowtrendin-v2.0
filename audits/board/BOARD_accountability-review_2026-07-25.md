# ADVISORY BOARD — ACCOUNTABILITY REVIEW
**Convened:** 2026-07-25 by the Chairman · **Five archetypes, independent, no cross-visibility**
**Charge:** you raised concerns across four rounds. Assess the WORK ACTUALLY DONE. On track?
What was fixed in appearance rather than substance? What next?

The summary given to the Board was itself the object under audit. They were told to verify it
against code, and they did. **Several of its claims did not survive.**

---

## 1. VERDICTS

| | On track? |
|---|---|
| **Executioner** | **NO** — "the reason changed from 'not yet' to 'cannot'" |
| **Outsider** | **NO** — "the engineering is on track. The company is not." |
| **Challenger** | Structurally yes, **evidentially no** |
| **Economist** | **Partially** — "modules are not measurement" |
| **Guardian** | **Qualified yes** — but the firewall "cannot go red where it matters" |

**Unanimous on one point:** the analysis loop has inverted. What was discipline through round 3
is now, in their words, *"a way of never being wrong"* — and **all five say enroll now and freeze
new construction.**

## 2. THE THREE FINDINGS I VERIFIED MYSELF — ALL CONFIRMED, ALL MINE

### 2a. The anti-lookahead lock is decorative (Executioner)
I wrote, in three separate docstrings, that the baseline is *"FROZEN INTO THE LEDGER ROW at
enrollment… never recomputed at resolution time"* and called it the most auditable property in
the design.

`flow_ledger.sweep()` line 443 calls `arrival_fn(p["ticker"], det, **kw)` where `kw` holds only
`horizon_days` and `mult`. **`baseline_median` is never passed — and `arrival_for` does not even
accept it.** It recomputes the baseline from a freshly-fetched series, under whatever
`ARRIVAL_BASELINE_SESSIONS` the dyno holds at resolution time. The frozen columns are written
and never read.

> *"The property is asserted in prose, tested nowhere, and contradicted by the only resolution
> path."*

### 2b. The pre-registration cannot express its own primary horizon (Executioner)
O3 was "fixed" by having `report()` read `pre.get("primary_horizon_days")`. That string appears
**exactly once in the module** — in the read. `flow_prereg` has no such column and
`register_prereg()` no such parameter. It is always `None` → hardcoded 90. The multiple-
comparisons fix is a constant the pre-registration cannot set.

### 2c. I told you flags were OFF. The code default is ON. (four archetypes)
`finviz_data.py:132` — `INSIDER_PARSER_FIX = os.getenv("INSIDER_PARSER_FIX", "1") == "1"`.
The OFF state exists **only** as an unversioned Heroku config var. A fresh dyno, a config reset,
a review app, a local run, or `tools/arrival_calibration.py` all get the changed behaviour
silently — including inside the R7 transient the gate exists to avoid.

> **Outsider:** *"It is a flag that is ON everywhere except one server."*

## 3. WHAT ELSE THEY FOUND

**Guardian — the firewall is scoped away from the risk.** `SCORING_MODULES` omits
`gravitational_anomaly_detector.py`: the file containing `score_topic`, `compute_nowtrendin_score`
and `apply_calibration`, which imports **four of the eight held-out modules**. Also
`audit_payoff_firewall` explicitly exempts `market_accuracy_ledger` — the module where the R1
breach lived — and, unlike the arrival audit, **has no negative control**. My claim that the
firewall "can go red" is true of one of the two audits.

**Economist — the interval math was built beside the wrong estimator.** `ledger_survival` is
correct and governs nothing. `accuracy_ledger_enhanced.survival_confirmation` still computes KM
with no Greenwood term, and `Ledger.tsx` renders it to enterprise customers as a naked point
estimate. *"A second, correct estimator was built beside the wrong one, and the wrong one is
still on screen."* He also **retracts his own median/MAD prescription**: `market_momentum` being
floor-bound on 15/16 names across 550 rows is a near-constant series, and **MAD of a
near-constant series is zero — it floors more often, not less.** That is a data defect, not an
estimator defect. *Do not deploy median/MAD; look at the raw series first.*

**Challenger — my calibration has an arithmetic error that misstated his own target.**
Events/name-year used `252/60` — trading days over a *calendar*-day window — and omitted
`−ln(1−p)`. Corrected, 2.5× gives **2.24 events/name-year, inside his 2–4 band**; his target maps
to ~2.5×, not to 2.0× with a 55% null. He also notes the calibration measures the wrong
population (it never applies `already_arrived_before`, so the null is biased **upward**), and the
"fixed seed" does not fix the universe — 40 of 55 tickers come from a feed that changes daily.

**Outsider — the deepest structural finding.** *"Absence and failure share a code path."* 212 of
300 instruments legitimately read ABSENT, so a source returning zero rows for **100%** of symbols
is invisible by construction. No source declares a coverage floor. Both silent deaths were caught
by a human running gate 5 by hand — *"that is not a control; it is a person."* He also pulled the
live trends ledger: **KM eventual confirmation 3.5%**, 39 events, 1,100 censored — *"the most
important number the company owns,"* and it was not in my pack.

**And a live integrity breach both he and the Guardian found:** BTC serves
`money_movement: null, tier: ABSENT` on every component **while emitting `flow: "inflow",
intensity: 60.0`** — a directional claim on top of components that declare themselves unmeasured.
My pack said crypto absence was *not* implemented; in fact it *is* live, but for the wrong
reason (every proxy is degenerate downstream of the dead parser), so **it will silently evaporate
the moment `INSIDER_PARSER_FIX` flips.**

## 4. THE POWER ARITHMETIC NOBODY HAD RUN

Against the measured 24.1% null, treated episodes needed per arm (80% power, disjoint-band rule,
control reuse):

| effect | naive | with band rule + clustering |
|---|---|---|
| 24%→44% | ~56 | **~110** |
| 24%→39% | ~97 | **~200** |
| 24%→34% | ~210 | **~430** |

At 3.0× the study measured ~1.0 arrival events per name-year. **At 16 names this is a decade; at
market-wide enrollment it is 2–3 quarters.** The binding constraint was never the multiple — it
is **universe breadth**, and nobody had said so.

The Economist adds the statistical resolution of the target dispute: required n scales as
`4(1−p₀)/(p₀(RR−1)²)`, which is **decreasing in p₀** — so driving the null to 5–8% is not merely
unreachable, it is *the wrong direction*. **Option B (3.0–3.5×), chosen on power, not aesthetics.**
Better still: pre-register a **stratified log-rank on time-to-arrival** rather than a 60-day
indicator — it uses the whole curve and cuts required n by a third to a half.

## 5. CONVERGENT NEXT STEPS

**All five independently reached the same shape: fix what would corrupt row 1, then enrol, then
freeze everything else.**

1. **Fix the four defects that would corrupt the first row** — pass the frozen baseline through
   resolution; add `primary_horizon_days` to the prereg schema; pass `mult` to
   `already_arrived_before`; censor at the row's prereg horizon, not env. Flip the
   `INSIDER_PARSER_FIX` code default to `"0"` so code equals intent. Add
   `gravitational_anomaly_detector` to `SCORING_MODULES` and give the payoff audit a negative
   control.
2. **Ship the source-liveness contract** (Outsider): every source declares a universe-coverage
   floor; zero rows across the *whole* universe is RED, independent of per-item absence. *"An
   afternoon of work and the highest-ROI item in the entire backlog."* Then deploy the parser fix
   with R7-pattern capture — and gate crypto refusal on `proxy_coverage == "thin"` **first**, or
   the flip silently un-does the honest absence.
3. **Lock the pre-registration with the power calculation attached and ENROL.** Success is one
   number: `pending_treated ≥ 1 and pending_control ≥ 3`.

**FREEZE:** the corpus, the panel, crash physics, committee alignment, the naming debate,
`macro_series` persistence, Phase 2c promotion — *until the register has rows and a date.*

## 6. THE SENTENCE THAT SHOULD GOVERN THE NEXT SESSION

> **Executioner:** *"Every finding above except the parser is in code that has never executed
> against a real row. Defects in unwired modules are free to find and free to have; a review round
> that finds six of them feels like rigor and costs nothing. The review loop has become the
> product."*

> **Outsider:** *"Four rounds of design have produced a better-instrumented zero. The fifth must
> produce n."*

---

**Chairman — the Board is unanimous: rule the target (they recommend 3.0–3.5× on power grounds),
and enrol. Everything else waits.**
