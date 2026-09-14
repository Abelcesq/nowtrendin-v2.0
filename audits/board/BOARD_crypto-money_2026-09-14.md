# BOARD COLLATION — crypto money-movement: tracking + communication — 2026-09-14

Nine seats, in isolation, on `EVIDENCE_PACK_2026-09-14_CRYPTO-MONEY.md` (C1–C6), each
verifying in code at HEAD `25f9bae`. COLLATION, not a blend. **Chairman — your decision
per item.** The Chairman asked for a substantive solution; the CONVERGENT PLAN below is
what the nine memos, read together, add up to — every divergence is flagged.

## THE ANSWER TO THE CHAIRMAN'S TWO QUESTIONS, UP FRONT

**"How do we track the data?"** Unanimous across seats: the only honest 12/12-coin
money-class source is the CoinAPI perpetuals collector already running held-out
(funding rate + open interest, ~$5/mo) — but what it measures is **LEVERAGE
POSITIONING, never "money movement"** (funding is the price of leverage; OI is
outstanding speculative credit in COIN units; perps are zero-sum — no money enters a
coin when OI rises). It cannot ship yet on any seat's standard: ~35 days of baseline
against a 45-day resolution window (zero complete episodes — Statistician), the crypto
ledger's clean cohort is **n=0 resolved** so there is nothing to backtest against yet,
single-venue Binance-USDT concentration (Operator: commodity data, sampled daily —
the edge, if any, is the JOIN with our attention series, not the leg), and the rights
question is open (Buyer's Desk: neither CoinAPI nor CoinMetrics is in the
RIGHTS_REGISTER; §16 has NO rights gate — the structural finding of the round).

**"Does option 2 work?"** — **Yes, as a renamed, pre-registered, patient project; no,
as a fix for the n/a.** Verdict spread: Economist/Expansionist/Buyer's Desk
APPROVE-WITH-CONDITIONS (the conditions are binding); Guardian/Challenger REJECT it as
a *Money Movement leg* while approving continued held-out accumulation; Executioner
SHIP-LATER (and found the wiring trap: the coverage gate keys on EQUITY-proxy counts,
so a wired derivs leg would stay invisible — all 12 coins would keep serving ABSENT
beside a live leg; four atomic changes needed, not one); Statistician OVERFIT-RISK;
Forecaster UNSCORABLE-until-prereg; Operator NOT-AN-EDGE-as-specified. Nobody says
stop collecting; everybody says do not wire, do not label it money, and seal the
pre-registration before the first correlation is computed.

## THE CONVERGENT PLAN (in the Executioner's ship order)

1. **C1 — fix the display language NOW (web-only, no engine deploy, $0).** Root cause
   found (Executioner): `web-terminal/src/lib/mobileTheme.ts:47-53` `MARKET_TIER_COLOR`
   has **no ABSENT key** → the chip falls through to DORMANT's grey `#9AA3B0` — absence
   rendered byte-identically to a measured low tier. The founder didn't misread prose;
   the chip told him it was a reading. Ship: distinct unmeasured treatment
   (hollow/dashed chip), label **NOT MEASURED** (Forecaster: `· structural` vs `· none
   this cycle`; never "yet," never a roadmap line), replace the ring's `n/a` zero-arc
   with a struck-through slot, put the one-line reason ON the card ("a money read
   requires 2 votable sources; this coin's proxies are ETFs, which file no insider
   reports"), retire the words "Dark Matter"/"Proxy Positioning" from client-facing
   crypto copy (Buyer's Desk). Verify: a naive reader no longer says "broken."
2. **C6-wart — delete `signal_freshness` from the money composite IN THE FREE WINDOW.**
   Unanimous FIX-don't-disclose, 9/9: a 0.8/0.3 price-feed-liveness flag is 25% of a
   score called money (Buyer's Desk: a methodology misstatement — the App Annie fact
   pattern; Statistician: floored-stdev artifact generator). Executioner's decisive
   fact: with all 12 coins serving `money_movement: None` TODAY, removing it is
   **provably zero-delta** — after C2 ever goes live the same edit becomes
   score-affecting and backtest-gated. Also fix the Challenger's sibling defect: when
   the price leg fails, M renormalizes to 100% `venue_diffusion` still labeled "coin
   price/volume trend" with an ACTIVE-capable confidence chip — floor the
   renormalization (≥50% of a leg absent → leg serves None).
3. **C5 — the shelf, worse than the pack said.** THREE unregistered crypto shelves
   (CoinAPI, CoinMetrics, Coinbase-premium — zero grep hits in DEFERRED_ITEMS) plus a
   second orphaned date (`etf_issuer_pages.py:10` "re-eval 2026-09-05", also passed,
   also unregistered — Operator). And `/monitor/deferred-triggers`' docstring claims it
   evaluates "every reactivation trigger in DEFERRED_ITEMS.md" while it hard-codes two
   triggers and **never opens the file** (Executioner) — a false claim in code. Fix:
   register all shelves with dates + owners, make the endpoint read date-based triggers
   (overdue → FIRE; unregistered collector → UNREGISTERED), fix the docstring, lint it.
4. **C2 — pre-register, accrue, THEN test.** Seal a spec file (SHA = param_version, the
   flow-spec precedent) BEFORE any correlation: estimand named `perp_positioning` /
   "Leverage & Positioning"; coin-denominated ΔOI only (USD-notional OI = OI×price is
   circular with M — Challenger/Economist independently); robust median-MAD z; ≥90
   daily obs/coin (Forecaster; Statistician notes N ≠ 12×days — one venue ≈ one
   factor); nulls: coin momentum, lagged persistence, funding autocorrelation, AND the
   F8 unconditional first-crossing null; Brier decomposed, all sealed enrollments,
   Bonferroni; the Economist's target: the DIVERGENCE states (OI↑ price↓ distress;
   OI↓ deleveraging) are what M does not already contain — and the sign must be able
   to go NEGATIVE (extreme funding = fragility), or it is the 07-29 sign-degenerate
   defect in new clothes. Enrollment invariance is binding (Forecaster): a
   funding-informed D enrolls only under a new `flow_basis` + new cohort boundary —
   never through the existing intensity/proxies gates. Rights evidence (CoinAPI
   redistribution clause; CoinMetrics community-tier commercial terms) is condition
   precedent to ANY display (Buyer's Desk). Add a rights gate to §16.
5. **C4 — ETF share-flow stays dark, on a written trigger** (5 in-band issuer
   comparisons, ≥2 funds). DISAGREEMENT to note: the Operator calls the issuer-page
   plumbing the real edge ("tedious and breaks" = moat) and would fund 2 weeks of
   adapter work; the Expansionist REJECTS it as the most parochial item (4/12 coins,
   US-only, O(issuers) maintenance forever). Chairman's call when the trigger fires.
6. **C3 — Coinmetrics is activity, not money: never a D component** (9/9). Split on
   display: most seats allow a separately-labeled "Network Activity" lane (Grade B,
   not marketing-eligible); the Executioner cuts even that for now. Keep the $0
   collector accruing either way.

## VERDICT TABLE

| Item | Chal | Guard | Expan | Buyer | Exec | Econ | Oper | Stat | Fore |
|---|---|---|---|---|---|---|---|---|---|
| C1 display | AWC | AWC | AWC | AWC | **SHIP 1st** | AWC | fix-now | fix-now | MIS-SCORED→fix |
| C2 option 2 | **REJECT-as-money** | **REJECT-as-money** | AWC | AWC (rights first) | SHIP-LATER | AWC | NOT-AN-EDGE-as-spec | OVERFIT-RISK | UNSCORABLE-yet |
| C3 activity | non-money display | non-money display | AWC display | REJECT-as-money | **CUT** | AWC non-money | not-edge | UNSUPPORTED-as-money | UNSCORABLE-as-money |
| C4 ETF leg | AWC dark | AWC | **REJECT growth path** | AWC pursue | SHIP-LATER | AWC dark+trigger | **DURABLE (the edge)** | shelve+trigger | WELL-SCORED, blocked |
| C5 process | APPROVE | APPROVE | APPROVE | APPROVE | SHIP 2nd | REJECT-status-quo | fix-today | fix | MIS-SCORED→lint |
| C6 wart | FIX | FIX | FIX | FIX | FIX (free window) | FIX | FIX | FIX | FIX |

## NEW DEFECTS THIS ROUND (beyond the pack)

| # | Finding | Seat(s) |
|---|---|---|
| K1 | `MARKET_TIER_COLOR` lacks ABSENT → absence styled as measured DORMANT grey | Executioner |
| K2 | M renormalizes to 100% venue_diffusion when price fails, still labeled price, confidence chip can read ACTIVE | Challenger |
| K3 | §16 has no RIGHTS gate; CoinAPI+CoinMetrics absent from RIGHTS_REGISTER (broken within a day of its own §I rule) | Buyer's Desk |
| K4 | Held-out firewall is import-only — a table read graduates a source invisibly; graduation mechanics undefined | Guardian |
| K5 | `/monitor/deferred-triggers` docstring falsely claims it reads DEFERRED_ITEMS; 2 hard-coded triggers | Executioner, Economist, Statistician |
| K6 | Second orphaned review date: `etf_issuer_pages.py` 09-05, unregistered, passed | Operator |
| K7 | `coinapi_derivs` docstring misstates its own estimand ("ΔOI = money entering/leaving" — in coin units it is not) | Challenger |
| K8 | Missing-not-at-random baseline: `has_row_for_today` is any-coin; 429s cluster on volatile days → stdev biased down | Challenger |
| K9 | Crypto ledger clean cohort n=0 AND accrual structurally zero (enrollment gates exclude all 12 coins) — the track record cannot start until a money leg exists | Statistician |
| K10 | Four divergent hand-written coin rosters (env, crypto_signals, coinapi, coinmetrics) — a 13th coin silently half-exists | Expansionist |
| K11 | KM "eventual confirmation" stat renders a censored estimate in a win-colored card | Forecaster |

**Chairman — your decision per item (C1–C6; and K3's rights-gate addition to §16).**
