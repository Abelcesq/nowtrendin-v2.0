# EVIDENCE PACK — crypto money-movement: tracking + site communication — 2026-09-14

**Chairman's question (verbatim intent):** the Crypto page serves "n/a" (Money Movement)
and "ABSENT" (Tier) on all 12 coins. "We need to figure out how to track the data and
communicate it on our site. Provide a substantive solution, and assess whether option 2
works" — option 2 = onboarding the crypto-native sources already scaffolded
(`coinapi_derivs`, `coinmetrics_onchain`, `coinbase_premium`).

All facts below are code/document-verified this session (file:line in the compiled
record); seats should re-verify what they lean on. Repo HEAD `25f9bae` on main.

## A. Why the display shows n/a/ABSENT (working as designed, founder-ruled)

- LIVE mechanism: D = 0.75·proxy_positioning + 0.25·signal_freshness
  (`crypto_money_gradient.py:28-35`); the positioning leg reads **insider Form-4/13F on
  crypto-exposure EQUITIES** (`crypto_signals.py`), not coins. Five of seven original
  proxies are ETFs/trusts with no insiders EVER; 10 alts share one COIN vote → **11 of
  12 coins can never reach the ≥2-voting-proxy floor** (BOARD_crypto-money-na_2026-07-29
  §0-1, which REJECTED insider-on-proxy as a crypto estimand, unanimous).
- The coverage gate (`CRYPTO_COVERAGE_GATE=1`) therefore serves `money_movement: None`
  with `absence_reason`/`absence_class` (structural vs transient), tier `"ABSENT"`, flow
  `"no_data"`, dark-matter block omitted. This is §16a stage-2 honest absence + the D8
  founder truth-ruling — a fabricated number here is the forbidden fix.
- Also note `signal_freshness` = 0.8-if-price-else-0.3: **25% of the "money" score is a
  price-feed liveness flag** — a quiet integrity wart in the current composite.

## B. The tracking candidates (what actually exists)

| Candidate | Coverage | Cost | State |
|---|---|---|---|
| **CoinAPI derivatives** (`coinapi_derivs.py`): Binance USDT-perp **funding rate + open interest** | **12/12 coins** | ~$4.6/mo (`COST_COINAPI_USD=5`, founder $1/day cap) | Collecting daily since ~08-10, held-out (AST-enforced: scoring can't import it), **~1 month baseline accrued**; `/diag/coinapi` exists. The "CoinAPI gate ~08-24" review date PASSED 3 weeks ago and lives ONLY in session-log open-items — not in DEFERRED_ITEMS (an unscheduled shelf, the §16a "furniture" failure) |
| **Coinmetrics on-chain** (`coinmetrics_onchain.py`): AdrActCnt + TxCnt | 9/12 (SOL/BNB/DOT permanent declared absence; paid flow fields 403 on community tier) | $0 | Collecting, held-out; measures ACTIVITY, not money flow |
| **Coinbase premium** (`coinbase_premium.py`) | 12/12 | $0 | **Already SHELVED** (5-day review 08-18: ±0.1% noise, t≈−1.9, `/spot` is mid-market so retail spread never measured, BNB synthetic rows). Re-arm trigger: capture `/buy`+`/sell` legs |
| **ETF share-flow leg** (spec v1 + A1 + A2) | 4/12 (BTC/ETH/SOL/XRP) | $0 | **BUILT, DEPLOYED DARK** (`CRYPTO_ETF_FLOW=0`); unanimous architecture approval 08-01; **flip BLOCKED**: Gate-4 issuer reconciliation failed first pass, A2 re-arm needs 5 in-band issuer comparisons, currently `pass_comparisons=0, funds=0, ready=false`; FMP ruled dead as the derived-leg source. shares-never-AUM (AUM circular with M) |
| Glassnode/Nansen on-chain | — | ~$800-1,000/mo | **CUT** by the 07-29 board (cost cap; Cost Sentinel history CRITICAL at $718 of $700) |
| CFTC COT (in `crypto_flow_probability_agent`) | BTC/ETH (CME) only | $0, regulated | Pre-wired, disabled; the probability agent is NOT SERVABLE (round 7, 9-0) until shadow n≥60 logged resolutions |

## C. Binding constraints on any solution

§16 five gates IN ORDER + backtest-before-ship for anything score-affecting; §16a
stages 1→2→3 never skipped (`[cold-start-stated]` commit gate); §17 (omit
non-contributing sources — but the D8 record deliberately chose DISCLOSED absence over
hiding the column); §15a-A3 (a false zero = a false peak; "never measured as nothing");
the $700/mo Cost Sentinel cap; flag-never-force; round-7's not-servable ruling on the
probability agents.

## Items for per-seat verdicts

- **C1 — COMMUNICATION.** The founder read "n/a"/"ABSENT" as errors. Is the current
  display the right honest-absence communication? Propose CONCRETE site changes (labels,
  tier-chip wording, tooltip/explainer copy, §17 layout treatment) that keep the
  integrity posture while stopping the founder's-own-confusion failure. Note the header
  explainer already exists and did not prevent the misreading.
- **C2 — OPTION 2, the core assessment.** Does CoinAPI derivatives (funding + OI, 12/12,
  $5/mo, ~1 month held-out baseline) WORK as the money-movement leg for coins? What
  estimand does funding/OI honestly support (positioning/leverage direction ≠ "money
  inflow")? Specify the acceptance standard: the §16 gate-5 backtest design, §16a
  cold-start staging, the D-composite wiring rule (replace insider-proxy leg? blend?),
  and what the display may claim while it calibrates.
- **C3 — Coinmetrics activity (9/12, $0).** Admit as a money-class component, a separate
  displayed signal, or reject? (Activity ≠ flow — where does it honestly belong?)
- **C4 — The dark ETF share-flow leg (4/12).** Path to unblock Gate-4 (issuer-page
  derived leg; FMP dead) worth pursuing, or shelve with a trigger? Interaction with C2.
- **C5 — PROCESS.** The CoinAPI review date passed unowned because it was never in
  DEFERRED_ITEMS. Prescribe the shelf fix (and whether `/monitor/deferred-triggers`
  needs a registration lint).
- **C6 — SEQUENCE + COST.** One ordered plan inside the cost cap: what ships first,
  what is cut, what the founder must decide, and the single measurement that would
  reverse each step. Also: the `signal_freshness` price-liveness wart (A above) — fix,
  keep, or disclose?

**Chairman = the founder. Memos inform; the founder rules.**
