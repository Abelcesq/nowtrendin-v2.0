# CRYPTO ETF SHARE-FLOW SPEC — AMENDMENT A1 (pre-flip)
**Date:** 2026-08-05 PT · **Amends:** `CRYPTO_FLOW_SPEC_v1_2026-08-02.md` (SHA `c3bf3eeb8e1a2201`)
**Status:** adopted BEFORE the flip; `CRYPTO_ETF_FLOW` remains 0; zero cohort rows exist. Per
spec §3.4 this amendment mints a NEW spec identity — the `param_version` stamped at flip is
this file's SHA lineage, and the clean-cohort start moves at flip in the same config change.
**Authority:** Chairman rulings 2026-08-05 (gates 1–3), grounded in the founder-supplied
market-cap brief and the provided texts (Burniske & Tatar, *Cryptoassets* — network value =
price × circulating supply, per-asset fundamentals; A. Lewis, *The Basics of Bitcoins and
Blockchains* — issuance/supply mechanics are per-asset (BTC fixed 21M schedule vs ETH
pre-mine + block + uncle rewards); B. Graham, *The Intelligent Investor* — price vs value
discipline, measurement over narrative).

## A1.1 — Sampling (amends §6): 4-hour observation cadence, strike-guarded daily row

Every pull (env `ETF_SNAPSHOT_INTERVAL_MIN`, default 240 → up to 6/day) is recorded in the
new `etf_share_observations` table. The daily `etf_share_snapshots` row INSERTs on first
sight and UPDATEs **only when the NAV itself changes** (a genuine later strike) — never on
AUM alone, which is the coin's own price moving (the banned circularity).

**Honesty boundary, stated so it can never be narrated otherwise:** NAV strikes once per
trading day. Six observations are six looks at **at most one genuine flow point per day** —
the cadence buys STRIKE-CAPTURE TIMELINESS (detection within ~4h instead of up to 24h,
shrinking the disclosed ±1-day smear), never six flow points. The 24h assessment view is
`etf_flow.intraday_report()` (served in `/diag/etf-flow.intraday`): looks taken, whether and
when the day's strike landed, per fund.

**Cost (assessed per the ruling):** 15 tickers × 6 pulls/day = 90 FMP calls/day (vs 60
today at the 6h risk cycle) — within the paid FMP plan's limits ($0 marginal; the Board's
2026-08-01 read called +40/day a non-issue). Apify is never touched (crypto has zero Apify
references). Heroku compute negligible. **Net new cost: $0.**

## A1.2 — Per-fund AUM-relative weighting (amends §2): each item tracked separately

Every fund keeps its own tracked vote (per-fund rows in detail; per-fund shadow votes on
`/diag/etf-flow`). The coin aggregate folds the fund class in one step: each fund's vote is
sized by its **AUM share within the coin's fund class**; the class's total voice keeps the
coin's CONFIGURED weight budget, so adding funds redistributes voice within the class and
never grows the class's share of the coin. Measured-quiet (0.0) funds stay in the
denominator (§2's sub-floor rule, unchanged).

**Why this is not circular:** all funds of one coin track the same coin price, so the price
multiplies every AUM equally and cancels in the relative weights. AUM is used as a SIZE
measure for funds — the correct per-asset-class metric (funds: AUM/NAV; coins:
circulating-supply network value; the founder's brief + both texts) — never as a signal.

## A1.3 — Venue classes (satisfies flip gate 5; amends the diffusion basis)

Coverage/diffusion is measured over **kinds of venue** — insider-equity filings = one
class, fund share-flow = one class — never over instrument count. `venue_diffusion` and the
intensity coverage-confidence both move to classes-active / classes-reachable when
`CRYPTO_ETF_FLOW=1`. Flipping six funds live is more thermometers, not more temperature;
the next fund (or a future non-US ETP) never moves a score by existing. Flag off =
byte-identical legacy behavior.

## A1.4 — Latency stamps (satisfies flip gate 6; per §5, unchanged semantics)

`flow_basis: "etf_creations"` + `signal_latency_days: 1` stamped on the dark-matter leg,
the top-level coin payload, and both crypto ledger tables (guarded forward-only ALTERs).
Lead 0–1 is parity, never prescience; the latency is never subtracted back.

## A1.5 — Reconciliation (amends §8 gate 4): continuous, cadence-based — not an N-day wait

Chairman ruling: the flip is NOT gated on a fixed 2- or 5-day green window. Gate 4 is
satisfied by a **continuous daily reconciliation**: every 24h cycle, derived Δshares are
compared against the issuers' published daily flows, with the tolerance band PRE-DECLARED
here before the first comparison ever runs (Bernstein rule):

> **Band (pre-declared):** on any fund-day where the published net flow exceeds that fund's
> materiality floor, the DIRECTION must match; magnitude must agree within **±25% or
> ±$20M, whichever is more forgiving** (the disclosed ±1-day UTC smear makes day-boundary
> slippage expected; a persistent one-direction bias is a fail even inside the band).

The harness runs as a standing daily check with an alarm (a divergence fires the monitor,
forever — not a one-time pre-flip ceremony). Flip precondition: the harness is LIVE, its
first comparison has completed inside the band, and the alarm is armed.

## A1.6 — F-FIX ADDENDUM (Board 2026-08-05 findings; Chairman-ordered same day; all
## adopted PRE-FLIP, zero cohort rows, before any comparison has run)

- **F1:** the fund class's voice is a PINNED per-coin constant (`etf_class_budget`: BTC 4.2,
  ETH 3.0, SOL 2.0, XRP 1.8 — frozen at the 2026-08-05 configured sums). Roster growth and
  day-to-day data availability redistribute voice WITHIN the class; neither moves the
  class-vs-insider mix. Changing a budget is a deliberate ruling, never a side effect.
- **F2:** flow deltas compare VALUE-DISTINCT strike days — a pre-strike daily copy (same
  shares+NAV, new date) is the same strike seen again, never a "measured quiet" 0.0. The
  genuine latest flow point serves until a new strike lands. Known disclosed artifact: a
  real strike repeating values exactly reads as no-new-strike (harness artifact class).
- **F3:** `CRYPTO_SERIES_EPOCH` (crypto-scoped) — set in the SAME config change as the flip
  so crypto baselines reset to CALIBRATING across the definitional break while every equity
  baseline is untouched. The flip command is now THREE stamps: `CRYPTO_ETF_FLOW=1` +
  `CRYPTO_LEDGER_CLEAN_COHORT_START=<flip date>` + `CRYPTO_SERIES_EPOCH=e1-flowleg-<date>`.
- **F4:** gap normalization is by TRADING days (Mon–Fri; US holidays deliberately not
  excluded — same declared basis as the flow-ledger window). Monday flow reads full-strength.
- **F5:** the committed regression harness is `transfer/test_crypto_flow_a1.py` (9 checks:
  fold arithmetic, dominance sign, F1 budget invariance, F2 pre-strike, F4 Monday, F6 class
  coverage, retained guards, ledger stamps, flag-off equivalence). Run before the flip.
- **F6:** `proxy_coverage` grades on venue classes when the flag is on (strong = both kinds
  reporting; partial = one; thin = none); `proxies_covered` keeps its labeled
  instrument-count meaning for the ≥2-fund corroboration check.
- **F7 (pre-declared BEFORE the first comparison — the Bernstein rule, closed):** the
  reconciliation harness direction-tests a fund-day ONLY when the issuer-published net flow
  exceeds that fund's **materiality floor = max($10M, 0.05% of the fund's AUM)**. Inside the
  band: direction must match; magnitude within ±25% or ±$20M (whichever more forgiving); a
  persistent one-direction bias fails even inside the band. These numbers are fixed now, at
  n=0 comparisons; changing them after data exists is a new spec identity.
- **F8:** the crypto ledger serves the per-coin UNCONDITIONAL first-crossing base rate
  (`compute_null_baseline`, deterministic over the coin's own retained history) beside any
  confirm rate, as a PUBLICATION PRECONDITION — no rate publishes without its luck-alone
  twin, adopted at n=0.
- **Chairman ruling recorded (C4):** the attention-beside-flow display keeps the
  utility-vs-speculative framing (the board's rename condition is OVERRULED); the
  methodology note will state attention-heat and fund-flow are the OBSERVABLE PROXIES for
  the two components. Build remains post-flip.

## Unchanged

Shares-never-AUM (§1); the vote table's stale/discontinuity/eligibility refusals (§2); the
≥30-trading-day per-fund null study and robust-z destination (§3 — the bridge constants
remain rejected-as-final); the pre-registered momentum/persistence nulls and the n≥30
publication floor (§4); coverage truth (§7 — BTC/ETH/SOL/XRP at $0; seven coins remain
honestly structural).
