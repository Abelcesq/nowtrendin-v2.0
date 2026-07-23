# D8 — T2 reopen review (covered lane now majority-MEASURED) — 2026-07-23

**Trigger:** `/monitor/deferred-triggers` → `D8_T2_coverage_conversion` FIRED. The recalibrated H2b
metric (covered-lane `unmeasured_fraction`) fell **0.524 → 0.362** (< 0.5 = majority-MEASURED) — the
genuine coverage-maturation event the tripwire was built to catch. Per the written rule this reopens
D8's held-out backtest **for REVIEW (reopen ≠ ship)**. Read-only; live pulls 2026-07-23 (engine
`7cff966`). This note is the only artifact.

## First — state reconciliation (what "D8" means today)
D8's **narrowed-spec T1** ("serve `money_movement: null` ONLY when ALL money-movement components are
absent/degenerate") **already SHIPPED** on 2026-07-20 under the founder truth-ruling — flag
`D8_MM_EXCLUDE=1`, live and confirmed (config value `1`). Live effect today: **206/300** equity
instruments serve the honest `money_data_absent` state; all 12 crypto coins are market-confirmation-
only. The DEFERRED_ITEMS D8 section still read "DEFERRED" — a stale doc (reconciled this session).
So what T2 reopens is NOT the shipped T1; it is the **only remaining unbuilt D8 scope**: a
composite-level exclusion that *renormalizes over surviving components* for PARTIALLY-degenerate
instruments (vs the shipped null-only-when-ALL-absent behavior).

## The reopen question, and the answer
Does the covered lane maturing to majority-measured turn D8 from presentation-truth into an
**accuracy** item — i.e., would excluding degenerate components from the composite now move the
ledger?

**No — the structural Δ=0 shield is intact and unchanged.** The load-bearing invariant holds: the
market + crypto ledgers NEVER read `money_movement` — enrollment gates on positioning flow +
intensity, verdicts are realized price direction (T3 has NOT fired; nothing was rewired). Confirmed
live: the market ledger is **unchanged** at 12 resolved / regime-adjusted 6-of-11 confirmed / 6
episodes — identical to before D8-T1 shipped. Excluding degenerate components from the composite
therefore still changes **0 enrollments and 0 verdicts**, majority-measured covered lane or not. The
maturation changes only WHICH instruments are all-degenerate (fewer now, hence 206 vs the earlier
166 breathes with coverage), not the accuracy payoff, which remains exactly zero by mechanism.

## Verdict — DEFER STANDS (the fuller composite exclusion is not built)
- The shipped **T1 (null-when-ALL-absent)** is the correct and complete D8 under its board-ruled
  narrowed spec. Nothing further to build there.
- The **renormalized-survivor composite** (excluding degenerate components and re-normalizing over
  survivors for partially-degenerate instruments) remains **REJECTED** on its own merits — a price
  whose recipe drifts row to row (Economist / inconsistent-series), for **zero** ledger effect. The
  covered-lane maturation does not change that trade.
- **Re-fires cleanly:** T2 will keep firing while `unmeasured_fraction < 0.5`; that is expected and
  is not a new ship signal. The genuine reactivation for the fuller exclusion is **T3** (any proposal
  to make enrollment/verdicts read mm/tier — which VOIDS the Δ=0 shield and MANDATES a fresh
  backtest before shipping). Absent T3, D8 stays presentation-truth.

## Board follow-ups still open (from the F1-ratification residual risks, D8-adjacent)
- The census % is a coverage/congestion gauge, never an external accuracy KPI (unchanged rule).
- The `serve_taxonomy_capped` visibility guard (shipped this session) is the transparency analogue
  for the census exemption class.

*Method: single-snapshot pulls 2026-07-23 (`/risk/scores?limit=300`, `/market/accuracy`,
`/monitor/degenerate-census`, `/monitor/deferred-triggers`, config `D8_MM_EXCLUDE`). No production
data modified; no paid actors ran; ledgers untouched (held-out).*
