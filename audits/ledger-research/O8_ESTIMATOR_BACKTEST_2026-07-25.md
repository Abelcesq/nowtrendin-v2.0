# O8 — MARKET ESTIMATOR BACKTEST: result
**Date:** 2026-07-25 · **Ordered by:** the Chairman ("let's do back test and then phase 2")
**Tool:** `tools/market_estimator_backtest.py` (read-only, endpoints only, zero writes)
**Status:** RESULT — awaiting Chairman sign-off before any score-affecting change.

---

## 1. The three claims, verified in code first (§10a)

The Economist's round-4 critique was treated as a starting point, not a diagnosis. All three
were checked against `transfer/market_signal_engine.py` before any data was pulled:

| Claim | Verdict in code |
|---|---|
| **A. No robust scale** — `statistics.mean` / `statistics.stdev` over `lookback` cycles, stdev floored at 0.05; zero uses of MAD anywhere in `transfer/` | **CONFIRMED** |
| **B. Tail deletion** — `_z_to_unit` returns `min(1.0, 0.30 + z*0.22)`, saturating at z = 0.70/0.22 = **3.18**; z=3.2 and z=32 serve the identical score. (Negative side floors at z = −3.125 via `max(0.05, 0.30 + z*0.08)`.) | **CONFIRMED** (arithmetic) |
| **C. Self-blinding** — `baseline_cycles = cycles[1:lookback+1]` correctly excludes the current cycle, but a spike enters the baseline for the next ~`lookback` cycles, inflating stdev and suppressing subsequent readings | **CONFIRMED as a mechanism** |

**But a mechanism that is real in code may be immaterial in production.** That is what the
backtest existed to decide, because the fix is score-affecting across every instrument.

## 2. Gates, registered before the run

| Gate | Measures | Material if |
|---|---|---|
| **G1** | share of scored components with \|z\| ≥ 3.18 (served score no longer responds to data) | ≥ 2.0% |
| **G2** | share of components whose stdev sits at the 0.05 floor (z denominator fabricated) | ≥ 15% |
| **G3** | observed P(\|z\|≥3) vs the Gaussian 0.27% | ≥ 3× |
| **G4** | max \|z\| observed — contextual, no pass/fail | — |

**Decision rule (registered):** ship only if **G1 or G2** is material. A null is a real result
and gets published as one.

## 3. ⚠ A CONFOUND I CREATED — and it changed the answer

The first run reported **G1 = 3.57% → MATERIAL**. Then the breakdown showed 3 of the 4
saturated components were `positioning_concentration` at large **negative** z
(MSFT −5.40, AAPL −4.96, AMZN −3.95).

That is **exactly the transient the R7 evidence document predicted, hours earlier**: with
`DARK_POS_WEIGHT=0`, `current` drops while `baseline_mean` stays elevated for ~12 cycles, so
z goes sharply negative until the baseline re-forms.

**So the headline G1 number was measuring my own change, not a standing defect.** Excluding
the perturbed component:

- **G1: 3.57% → 0.89%** — *below* the registered 2.0% threshold. **G1 does NOT bind.**
- **G2: 33.93% → 35.42%** — unaffected, and more than double its threshold. **G2 binds.**

Had the headline figure been reported as-is, a score-affecting change to every instrument
would have been justified on an artifact created hours before by the very same operator.
A confound guard is now permanent in the tool: gates are evaluated on confound-excluded
figures, and all-in numbers are printed alongside but cannot satisfy a gate.

*(G3's 13.2× is likewise inflated by the same transient and should not be leaned on until a
clean re-run after the baseline re-forms.)*

## 4. RESULT

```
components observed        : 112 (16 instruments x 7 components)
G1 saturation |z|>=3.18    : all-in 3.57%  | CONFOUND-EXCLUDED 0.89%   -> NOT material
G2 stdev at 0.05 floor     : all-in 33.93% | CONFOUND-EXCLUDED 35.42%  -> MATERIAL
G3 tail vs Gaussian        : 13.2x (inflated by the same transient — re-run clean)
G4 max |z|                 : 5.40 (itself the R7 transient)
```

**Per-component floor-binding — the finding that matters:**

| component | n | saturated | **floor-bound** | min z | max z |
|---|---|---|---|---|---|
| `market_momentum` | 16 | 0 | **15** | −2.09 | 1.01 |
| `cross_market_diffusion` | 16 | 1 | **8** | −1.41 | 3.30 |
| `signal_freshness` | 16 | 0 | **7** | −1.44 | 1.70 |
| `positioning_concentration` | 16 | 3 *(R7)* | 4 | −5.40 | 2.45 |
| `fundamental_confirmation` | 16 | 0 | 4 | −1.10 | 1.88 |
| `dark_positioning` | 16 | 0 | 0 | 0.77 | 1.05 |
| `analyst_signal` | 16 | 0 | 0 | 0.34 | 0.71 |

**`market_momentum` is floor-bound in 15 of 16 instruments.** Its z denominator is the 0.05
floor, not a measured dispersion — so that component's contribution is largely an artifact of
the floor rather than of the data, on nearly the entire curated universe. Note these are not
thin baselines: `n_history` is 528–556 rows. The floor is binding on *deep* histories, which
means the underlying series genuinely has near-zero dispersion at the observed granularity,
and dividing by a fabricated 0.05 manufactures a z from nothing.

## 5. DECISION SUPPORTED BY THIS EVIDENCE

**Ship a robust scale estimator. Do NOT remove the saturation cap.**

- **Supported (G2):** replace mean/stdev with a robust location/scale (median + MAD×1.4826),
  and revisit the 0.05 floor — a floor that binds on a third of components with 500+ rows of
  history is doing more work than the data. MAD additionally *mitigates claim C* (self-
  blinding), because one spike barely moves a median-absolute-deviation while it substantially
  moves a standard deviation. One fix addresses two of the three claims.
- **NOT supported (G1):** removing the z≈3.18 cap. Once the confound is excluded, saturation
  affects 1 component in 112. Real in code, inert in production, at today's universe.
- **Deferred:** the Economist's stronger proposal — replacing the served z with an *exceedance
  rank* + Wilson interval — is a larger, user-visible change and is not decided by this
  evidence. It should stand or fall on its own pre-registered test.

## 6. SCOPE LIMITATION (stated, not hidden)

This reads the served diagnostic surface (per-component z, floor_binding, history depth). It
measures **whether the defects bind**; it does **not** replay a counterfactual median/MAD
score per instrument, which needs engine-side DB access (`pg:psql` is broken on this box).
So it justifies *which* fix, not *how much* the scores would move. A staged rollout with
before/after capture — the R7 pattern — remains required.

## 7. RE-RUN TRIGGERS

- After the R7 baseline re-forms (~12 cycles / ~3 days) — for a clean G1 and G3.
- **At Phase 2 market-wide enrollment.** The current universe is 16 curated mega-caps; the
  Board's own finding is that this is the regime where the market signal is weakest. Floor
  binding and tail behaviour may look entirely different on a small/mid-cap universe, and
  that is precisely when this gate should be read again.

---

**Chairman — sign-off requested on:** adopting a robust scale estimator (median/MAD) for the
market baselines, gated behind a flag, with before/after capture per the R7 pattern; and on
leaving the saturation cap alone until it demonstrably binds.
