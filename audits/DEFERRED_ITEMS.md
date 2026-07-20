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
- **T2 — coverage conversion:** `/monitor/degenerate-census` shows the degenerate class
  SHRINKING (Finviz insider breadth / 13F expansion converting degenerate baselines to
  measured) such that exclusion would bind on real data. Watch:
  `instruments_with_unmeasured_components` trending down toward < half of scored.
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

**REACTIVATION TRIGGER:** the outflow lane reaches **n≥15 resolved episodes**, OR **0-for-10**
(immediate). Until then: **keep enrolling the outflow lane UNCHANGED — never throttle the
losing lane** (Taleb's cemetery — the losing rows ARE the evidence that will settle it). The
mechanism is code-certain and time-invariant; only the *effect size vs regime* awaits n.

**IF ITS TRIGGER FIRES:** S1 is a SCORE_AFFECTING item behind its own held-out,
regime-adjusted, precision-AND-recall backtest gate + founder sign-off. It must NOT be tuned
against the ledger it is measured by.

---

## Standing reporting/monitoring hardenings SHIPPED (E4, 2026-07-20) — not deferred, recorded here for the trail
- `market_accuracy_ledger.report()` now serves **episode-collapsed** rates (distinct
  (ticker, flow)) alongside row rates — 12 rows were ~7 episodes; the episode counts are the
  honest n. `episode_small_sample` flags < 15.
- `gate_rejects_since_boot` surfaces directional candidates the ledger never sees.
- `/monitor/degenerate-census` is the D8 T2 tripwire metric (coverage gauge, never published).
- The `detection_score=None → intensity×100` fallback is FIXED: absent at-detection witness
  now stores NULL, never a substituted quantity (would have corrupted the witness under D8).
