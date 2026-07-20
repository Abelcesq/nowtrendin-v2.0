# DEFERRED ITEMS — gated work with written reactivation triggers

> Purpose: an un-triggered shelf is how a documented defect becomes furniture (Guardian,
> D8 board 2026-07-19). Every deferral here carries WRITTEN reactivation triggers so it
> reopens by rule, not by memory. Load-bearing invariants are recorded so the next
> regression can't ship silently.

---

## D8 — score-side exclusion of degenerate positioning components (DEFERRED 2026-07-19)

**What it is:** exclude degenerate (zero-variance, constant-mean) positioning components
from the Money Movement *composite* so the served number equals the honest-absence display
(D7 shipped the display half; E1 shipped the composite disclosure).

**Why deferred (board-unanimous):** the market/crypto accuracy ledgers NEVER read
money_movement (enrollment gates on positioning flow + intensity; verdicts are realized
price direction). The held-out backtest
(`audits/ledger-research/D8_DEGENERATE_EXCLUSION_BACKTEST_2026-07-19.md`) proved
Δ(enrollments)=0, Δ(verdicts)=0 exactly, at every n — **zero accuracy payoff by mechanism**,
while the change would blank money_movement on 188 flow-neutral instruments + all 12 coins
and flip 95 ROUTINE→DORMANT (all structurally unenrollable). Spending score-surface risk +
a 95-row communication burden for zero ledger effect is the wrong trade until data (not
absence) gives the exclusion something to bind on.

**REACTIVATION TRIGGERS (any one reopens D8; T3 makes it MANDATORY-before):**
- **T1 — founder truth-ruling:** the founder rules that served money_movement / tier must
  equal the displayed honest-absence state.
- **T2 — coverage conversion (H2 granularity fix, 2026-07-20):** watch each LANE's
  `fully_degenerate_fraction` on `/monitor/degenerate-census` → `by_lane` fall — NOT the
  global `any_unmeasured` count, which is saturated at ~299/300 and stays high FOREVER by the
  permanent-frontier rule (E5/§16a), so it can never trend down even as a mature cohort
  (e.g. covered-lane large caps) fully converts. The trigger reads the covered-lane fraction
  crossing below 0.5. Evaluated on cadence by `/monitor/deferred-triggers` (H6).
- **T3 — enrollment rewiring (MANDATORY):** ANY proposal to make ledger enrollment, a
  verdict, or any downstream consumer read money_movement or tier. This VOIDS the Δ=0
  shield — D8's ledger-neutrality is a property of *today's* wiring, not permanent
  (backtest §6.6). If enrollment ever reads mm/tier, D8 must be re-backtested BEFORE that
  ships.

**IF EVER BUILT — the narrowed spec (board-ruled, not the original):**
- Serve `money_movement: null` ONLY when ALL money-movement components are absent/degenerate
  (macro-theme n/a serialization class). **NO renormalized-survivor composites** — recomputing
  mm from one thin surviving component is a price whose recipe drifts row to row (Economist,
  Friedman & Schwartz inconsistent-series). Never a fabricated number.
- Crypto: the D ring goes to null on all 12 coins → M-only score. **Product decision required**
  before ship: label it market-confirmation-only, do NOT headline a "Money Gradient" with no
  money data (Outsider).
- Flag-gated (default off), founder sign-off, fresh backtest at then-current n, same-deploy
  explaining copy on all 3 platforms, serve_payload regeneration, hysteresis on tier
  transitions (no ROUTINE↔DORMANT flapping from cycle-sensitive components).

**LOAD-BEARING INVARIANT (do not violate):** ledger enrollment must NEVER read
money_movement or tier. This is what makes the score and its own validator independent;
coupling them manufactures circularity. Undocumented, it is how the next regression ships.

---

## S1 — asymmetric outflow gate (SPEC ONLY, gated 2026-07-20)

**What it is:** the market-signal "outflow" flow claim is built (with `AV_DARKPOS_ENABLED`
effectively off in production) purely from congress net-selling (`positioning_intel` L118:
`flow='outflow' if congress net(buys−sells) < −1`). This is the SAME degenerate-net class
ruled *noise* for insiders on 2026-06-26 (routine selling ≈ noise; buying is the signal) —
the insider path got the accumulation-only asymmetric fix at L160; the congress base flow
never did. S1 = give outflow the same asymmetry (routine net-sell → neutral unless
corroborated). Full evidence:
`audits/ledger-research/OUTFLOW_FLOWLOGIC_INVESTIGATION_2026-07-19.md`.

**Why gated / NOT implemented:** the outflow lane is 0-for-5 resolved, BUT the regime control
(run first, per the Challenger) found these names rallied +8–19% in-window, giving an 18.8%
outflow-confirm base rate and P(0-for-5 | regime) = 0.35 — **the failures are fully consistent
with market regime alone at n=5**; both lanes are the same rally bet pointed opposite ways.
Episode-collapsed the lane is 0-for-3. Tuning a score to a 5-row, regime-confounded, losing
lane is exactly the Goodhart / score-inflation the board forbids.

**REACTIVATION TRIGGER (R2 — PRINCIPLE-OR-n, Chairman-ruled 2026-07-20, Expansionist resolution).**
The S1 mechanism is a *principle* already ruled true for insiders on 2026-06-26 (routine net-sell
= degenerate noise; net-buy = signal), which required NO ledger n. So S1 reopens on EITHER of:
- **PRINCIPLE:** the founder rules that insider-parity governs — the congress base flow gets the
  same accumulation-only asymmetry the insider path already has; OR
- **n:** the outflow lane reaches **n≥15 resolved EPISODES** (H5 — the unit is EPISODES, the
  declared honest n, not rows; rows run ~3× faster and would fire prematurely), OR **0-for-10
  EPISODES** (immediate).

Reopening means: open the held-out backtest — it does NOT mean ship. Until then: **keep enrolling
the outflow lane UNCHANGED — never throttle the losing lane** (Taleb's cemetery — the losing rows
ARE the evidence that will settle it).

**IF REOPENED — ship gate (unchanged):** S1 is a SCORE_AFFECTING item behind its own held-out,
**regime-adjusted** (vs benchmark — now available in `market_accuracy_ledger.report().regime_adjusted`),
precision-AND-recall backtest + founder sign-off. It must NOT be tuned against the ledger it is
measured by. Even the principle-reopen path passes this backtest before shipping.

**TRIGGER UNIT (H5):** all S1 counts are EPISODES (distinct ticker×flow), read from
`/market/accuracy` → `episodes` / `regime_adjusted.episodes`. The `/monitor/deferred-triggers`
endpoint evaluates this on cadence (H6).

---

## R1 — SYMMETRY RULING (Chairman-adopted 2026-07-20; standing, not deferred)
Neither market-ledger lane is validated at the current n. The absolute ±5% confirm rates are
regime-BLENDED in BOTH directions: in a broad rally, inflow confirms and outflow fails
MECHANICALLY, with zero skill either way ("the same coin landing heads because the market went
up"). A high inflow rate (6/7 rows, 3/3 episodes) is as regime-flattered as the low outflow
rate (0/5 rows, 0/3 episodes). **RULES:** (a) never cite either absolute lane rate as evidence
the Money Gradient works — cite `report().regime_adjusted` (excess return vs benchmark); (b)
never publish any market-ledger confirm rate OR the degenerate-census % on any external surface
(pitch / demo / marketing) while `small_sample`/`episode_small_sample` is true — the payload
flags protect the payload, not a slide.

## Standing reporting/monitoring hardenings SHIPPED — recorded here for the trail
**E4 (2026-07-19):** episode-collapse; gate-reject counter; `/monitor/degenerate-census`;
witness-corruption fix (absent → NULL).
**Hardenings review fixes (2026-07-20, this session):**
- **H1** census cold cache (equity + crypto) → `available:false`/unknown, never a false 0.
- **H2** census T2 = per-LANE `fully_degenerate_fraction` (trendable), global is saturated-by-design.
- **H3** episode confirm-rate served as a RANGE [strict, any] + majority; never headline the
  optimistic ANY-rule (a MAX operator that only inflates the winning lane).
- **H4** gate-reject counter is now DURABLE + fleet-global (`market_gate_rejects` table,
  flushed on any enrollment/sweep/report conn); a 0 with no history still = UNKNOWN.
- **H7** the witness NULL behavior is guarded by `transfer/test_market_ledger_witness.py`
  (the test is the mechanism, not the comment); the tautology no-op was deleted.
- **P1** `report().regime_adjusted` — excess return vs benchmark (SPY), de-confounds BOTH lanes.
- **R1** symmetry ruling above; `regime_caveat` in the payload.

## SCHEDULED READER (H6 — so triggers fire by rule, not memory)
`/monitor/deferred-triggers` evaluates every trigger here (D8 T2 via the census covered-lane
fraction; S1 via the market-ledger EPISODE counts) and returns FIRE/HOLD per item. The weekly
**improve-system** audit reads it each run (checklist item) and surfaces any FIRE. An
un-scheduled shelf becomes furniture — this endpoint + the weekly read is the walk.
