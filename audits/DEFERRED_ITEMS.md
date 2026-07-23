# DEFERRED ITEMS — gated work with written reactivation triggers

> Purpose: an un-triggered shelf is how a documented defect becomes furniture (Guardian,
> D8 board 2026-07-19). Every deferral here carries WRITTEN reactivation triggers so it
> reopens by rule, not by memory. Load-bearing invariants are recorded so the next
> regression can't ship silently.

---

## D8 — score-side exclusion of degenerate positioning components (T1 SHIPPED; fuller exclusion DEFERRED)

> **STATE RECONCILIATION (2026-07-23):** D8's narrowed-spec **T1 SHIPPED** 2026-07-20 under the
> founder truth-ruling — `D8_MM_EXCLUDE=1` is LIVE: serve `money_movement: null` when ALL money
> components are absent/degenerate (206/300 equity + all 12 coins serve the honest absent state).
> The ONLY remaining unbuilt scope is the renormalized-survivor composite exclusion, which stays
> DEFERRED. **T2 fired 2026-07-23** (covered-lane `unmeasured_fraction` 0.524→0.362, majority-
> measured) → reopen backtest REVIEWED (`audits/ledger-research/D8_REOPEN_REVIEW_2026-07-23.md`):
> **DEFER STANDS** — the Δ=0 shield is intact (ledgers still never read mm; T3 not fired; market
> ledger unchanged at 12 resolved / regime 6-of-11), so the fuller exclusion still has zero ledger
> effect and the renormalized-survivor recipe stays rejected (recipe-drift). T2 will keep firing
> while <0.5; that is expected, NOT a ship signal. The real reactivation is T3.

**What it is:** exclude degenerate (zero-variance, constant-mean) positioning components
from the Money Movement *composite* so the served number equals the honest-absence display
(D7 shipped the display half; E1 shipped the composite disclosure; T1 shipped the null-when-
ALL-absent half).

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
- **T2 — coverage conversion (H2b recalibration, founder-ruled 2026-07-20):** watch the
  COVERED LANE's **`unmeasured_fraction`** on `/monitor/degenerate-census` → `by_lane` fall
  **below 0.5** (i.e. the majority of covered-lane components become MEASURED). The trigger
  fires there — a genuine maturation event — and reopens D8's held-out backtest for review
  (reopen ≠ ship). Evaluated on cadence by `/monitor/deferred-triggers` (H6).
  - **Why NOT `fully_degenerate_fraction` (the original H2 metric, superseded):** it counts
    instruments where EVERY component is degenerate, which is structurally ~0 for large caps
    (they almost always carry ≥1 measured component). It sat below 0.5 from the BASELINE state
    and fired on the FIRST live read (2026-07-20) — crying wolf, not signalling conversion.
    `unmeasured_fraction` starts near 1.0 cold and falls as component history accrues, so it
    crosses 0.5 only when the lane has genuinely matured (live 2026-07-20: 0.524 → HOLDS).
  - **Why NOT the global `any_unmeasured` count (the pre-H2 metric):** saturated ~299/300 and
    stays high FOREVER by the permanent-frontier rule (E5/§16a) — un-fireable in the FIRE
    direction even as a mature cohort fully converts.
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

## S1 — asymmetric outflow gate (PRINCIPLE ARM CLOSED 2026-07-20; n-arm remains)

> **UPDATE 2026-07-20 (founder ruled "run the degeneracy test"; board Economist synthesis).**
> The principle-reopen path was EXERCISED and **RESOLVED: REJECT parity (board branch S1-4).**
> The ledger-independent degeneracy test
> (`audits/ledger-research/S1_CONGRESS_NET_DEGENERACY_TEST_2026-07-20.md`) measured the distribution
> of congress `net(buys−sells)` across the served universe: **7 net-BUY / 7 net-SELL, mean ≈ 0**
> (clean net-buyers like 3/0, 5/0 present) — congress net **DISCRIMINATES**; it is NOT the
> structurally-sell-dominated degenerate class insider net was (~15/15 all-sell). **The insider
> parity does NOT transfer**, so the blanket accumulation-only asymmetry on the congress base flow
> is NOT justified. `positioning_intel.py` L118 stays UNCHANGED. This CLOSES the PRINCIPLE arm of the
> trigger below. The **n-arm remains open**: the outflow question is settled by DATA (n≥15 resolved
> EPISODES or 0-for-10), never the parity shortcut and never the regime-confounded small-n rate.
> Spin-off noted but NOT acted on: the 4 outflow mega-caps are two-sided (e.g. 6 buys / 14 sells) yet
> fire "outflow" at saturated intensity 1.0 — a *conviction/intensity* calibration question, a NEW
> item with its own investigation + backtest if pursued, NOT S1.

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

**REACTIVATION TRIGGER — n-ARM ONLY (the PRINCIPLE arm was tested and REJECTED 2026-07-20).**
~~PRINCIPLE: insider-parity governs~~ — **CLOSED:** the degeneracy test rejected parity (congress net
discriminates, see the update box above). The principle path does NOT reopen S1. The one live arm:
- **n:** the outflow lane reaches **n≥15 resolved EPISODES** (H5 — the unit is EPISODES, the
  declared honest n, not rows; rows run ~3× faster and would fire prematurely), OR **0-for-10
  EPISODES** (immediate). Evaluated on cadence by `/monitor/deferred-triggers` (H6).

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
- **H2** census T2 = per-LANE fraction (trendable), global is saturated-by-design.
  **H2b** (founder-ruled, same day): the per-lane metric is covered-lane `unmeasured_fraction`
  (< 0.5 = majority-measured = reopen), NOT `fully_degenerate_fraction` — the latter is ~0 at
  baseline for large caps and fired on the first live read (a mis-calibrated tripwire).
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
