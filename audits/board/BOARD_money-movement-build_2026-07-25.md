# ADVISORY BOARD — ROUND 2: BUILD BLUEPRINT for a real money-movement tracking system
**Convened:** 2026-07-25 by the Chairman · **Six archetypes, independent, no cross-visibility**
**Charge:** *"Recommendations on what to implement to generate an actual, legitimate, verifiable money movement tracking system."*
**Status:** COLLATION FOR THE CHAIRMAN — nothing built, nothing shipped. Decisions required at §6.

Round 1 record: `BOARD_market-crypto-signal_2026-07-25.md` (diagnosis; accepted).
Chairman has already approved and shipped the documentation correction (commit `ac521ba`).

---

## 1. THE DISCOVERY THAT CHANGES THE COST MATH

Five of six archetypes independently found the same thing in the code:

> **`fmp_data.historical_close()` calls `historical-price-eod/light`, whose payload is documented in our own code as "date + close **and volume**" — and we keep only the close. `databento_price.historical_close` reads `ohlcv-1d` records and discards volume identically.**

Combined with Round 1's finding that `finviz_data.insider_feed()` (market-wide Form-4, "~100 insider buys across ALL tickers in ONE call") is dead code called only under `__main__`:

**The entire system below can be built for $0/month in new subscriptions.** Every input is either already paid for and discarded, already paid for and unused, or free from EDGAR/CFTC/regulator feeds.

> **Executioner:** *"The arrival clock costs $0 and requires no new source — it requires extracting a field we already pay for and discard. That fact drives the whole sequence."*

---

## 2. THE CONSENSUS BLUEPRINT (all six agree)

### 2.1 The observable — signed, normalized, a CHANGE not a level
Open-market Form-4 transactions only: codes **P** (purchase) and **S** (sale). **Exclude M/A/G/F** — option exercises, awards, gifts, tax withholding — *"those are compensation, not money moving"* (Outsider). Exclude 10b5-1 pre-planned trades (Challenger notes the checkbox is parseable from **EDGAR XML but not Finviz HTML** — an independent reason EDGAR is required).

Normalize to a dimensionless, size-neutral quantity, then take deviation from the instrument's **own** base rate. This is the generalization of the settled insider-NET degeneracy lesson: *level → deviation-from-own-base-rate.*

**Sells are baselined, not zeroed.** Today's rule (selling always neutral) is right about 10b5-1 noise and wrong as a permanent rule: measure sells against the name's own 24-month sale distribution, so routine diversification nets to ≈0 while abnormal selling still registers (Outsider, Expansionist, Guardian).

**Opportunistic vs routine split** (Cohen–Malloy–Pomorski), buildable from our own accumulated feed at zero marginal cost: an insider is ROUTINE if they traded the same calendar month in ≥2 of the prior 3 years; only opportunistic trades carry full weight. **Cluster weighting** by distinct filers and role (CEO/CFO > officer > director > 10% owner) — *"a 3-officer cluster buy is the observable; one director's $120K is not"* (Economist).

### 2.2 The arrival clock — ABNORMAL VOLUME (unanimous, and the crux)
All six independently chose **abnormal trading volume / turnover**, measured against the instrument's own trailing baseline, as the mainstream-arrival event. It is:
- **not price** → so LEAD is not a return test renamed;
- **not our attention engine** → so it is not circular with the Trend side;
- **already paid for** → the discarded volume field;
- **symmetric** → *"it fires identically on up and down moves, so it cannot be quietly converted into a return test"* (Guardian).

**The baseline must be frozen at enrollment** (measured as of, or 5 sessions before, detection) — several archetypes call this the single most auditable anti-lookahead lock in the design.

**Explicitly rejected as clocks:** our own Trend/attention output (circular by construction — the trap named in the pack); price return; options OI and retail-platform interest (no licensed source); analyst initiation and coverage breadth as *headline* (Economist: our Trend engine consumes the same RSS → contaminated; admissible only as a logged secondary witness after a written independence audit).

### 2.3 The null control — MANDATORY, and it must ship FIRST
Unanimous, and the Executioner's ruling on sequencing is the sharpest statement on this board:

> *"MUST SHIP FIRST — and it is not the insider feed: the **null cohort**, wired before the first live enrollment. Every other piece is reversible with one config:set. A ledger that accumulates 90 days of live rows with no contemporaneous control cannot be retro-fitted — you cannot enroll a placebo in the past without fabricating data, which the ground rules forbid. Ship the control first, or in 90 days we will have a beautiful, unfalsifiable number and will have to start over."*

Control arms proposed (union of the six): **random-date** (same name, random prior date), **random-name** (same date, matched on liquidity decile + sector + volatility, no qualifying event), **shuffled-sign** (tests whether direction carries any information), and **congress arm** (Quiver as the known-lagged benchmark — *"if we don't beat arm 3, we have nothing"* — Outsider). K = 3–5 controls per detection.

### 2.4 The ledger — build new, freeze the old
Do **not** mutate `market_accuracy_ledger`. Keep it byte-identical and never deleted; **relabel it honestly** as the legacy congress-flow record (it is an accurate track record of the Quiver feed — it was merely mislabeled as validating the Market Signal).

New tables (additive, forward-only): pending detections · accuracy ledger · placebo/control ledger · arrival events · gate rejects · pre-registration lock. Reuse the machinery that Round 1 verified is already correct: episode collapse, one-open-row-per-key, at-detection witness never substituted, gate-reject counters as silent-evidence accounting.

**Port `survival_confirmation()` (KM) — and fix what is missing.** Two archetypes independently found it has **no variance estimator and no confidence interval**. Add **Greenwood's variance with a log-log 95% band**. *"A KM curve without an interval is not evidence"* (Economist, Bernstein).

**Pre-arrival purity gate:** if volume already crossed the threshold before detection, the row is `PRE_ARRIVED` / `ALREADY_ARRIVED` — excluded from the lead denominator, counted and reported separately. This is the market analogue of the attention ledger's `pre_broken` split, already proven.

### 2.5 How a component earns weight — pre-registration, git-timestamped
Unanimous, and it is the structural answer to Round 1's finding that *"the backtest tested a different variable than the one wired."*

Write the hypothesis, exact formula, universe, window, arrival definition, thresholds, control design, success criterion, and stop rule to a file **committed before the analysis runs**; store its SHA. **No component may take weight from an analysis whose git timestamp precedes its pre-registration file.** Until it passes, the component ships at **weight 0**, computed and shadowed, user-invisible.

**Cut immediately from the score (unanimous):** the 13F `funds_holding` term — quarterly, top-10, a level, an index-membership proxy. Keep collecting it; Guardian makes the elegant point that it is *"weak as a signal and strong as ground truth"* and therefore belongs on the **referee** side (see §5).

### 2.6 Universe as data, not code
Retire the 16 hard-coded `WATCHLIST_TICKERS`. Replace with a DB table, **event-driven**: any ticker appearing in the market-wide insider feed with a qualifying event auto-enters as a candidate, governed by the **§16a cold-start progression** (CALIBRATING → honest absence → scored), with dormancy after N days without an event. This turns market-wide scanning on for $0 and naturally skews small/mid-cap — where the literature locates surviving edge.

### 2.7 Crypto — honest absence, not a repaired proxy
Unanimous: the 8-of-12 coins sharing `COIN` as their only proxy is *"not a signal with a bug — it is not a signal"* (Outsider). Serve **§16a stage-2 honest absence** (`money_data_absent`, `score: null`) rather than a fabricated read. *"An absent read is a product; a fabricated read is a liability"* (Guardian).

The real observable when resumed: **spot-ETF creations/redemptions** (actual dollars entering the coin) and/or **CFTC Commitments of Traders** (free, weekly, signed by trader category — commercial/managed-money vs non-reportable, i.e. informed vs crowd), covering BTC/ETH only. Honest coverage of 2 of 12 beats twelve fabricated ones. Crypto arrival clock must run on **UTC 24/7 buckets** — the ledger's EOD-close grid silently assumes a US trading calendar. One-line integrity fix regardless: collapse episodes on `(instrument, direction)` so 8 coins sharing one proxy stop counting as 8 independent trials.

### 2.8 What we publish, and what we refuse
**Publish exactly ONE headline number**, with n, a 95% CI, and its param_version. The six phrasings differ (see §4) but agree on the shape: *a control-referenced timing statistic*.

**Refuse to publish (unanimous):** any return, P&L, Sharpe, equity curve, or backtested performance · any rate without a control arm · any median lead computed on winners only (the existing survivorship defect) · any rate whose denominator drops pending rows · any figure below a minimum n or above a maximum CI width · anything spanning two param_versions.

---

## 3. THE THREE NEW RISKS FLAGGED (none were in the pack)

1. **Calendar artifacts (Challenger).** Earnings dates, index rebalances and lockup expiries produce volume shocks on a *predictable schedule*; "leading" them is trivial and worthless. → Stamp arrivals within ±2 sessions of a scheduled event as `arrival_scheduled`, report in a **separate arm**, headline uses unscheduled only, and alarm if scheduled arrivals exceed ~25% of wins.
2. **Finviz redistribution rights are unresolved (Outsider).** *"Never cite a Finviz-derived field to a client without confirming redistribution rights — that is a live legal item, not a footnote to defer."* EDGAR is public domain and must be the source of record; Finviz is the fast mirror. **Serve derived scores, not vendor rows.**
3. **Personal data / GDPR (Expansionist).** Form-4, UK PDMR and EU MAR all name natural persons. Store `actor_id` as a salted hash with names in a separate, region-restrictable `actor_reference` table. *"GDPR is not a later problem; it is a schema decision made in the first 30 days."*

Plus two the Challenger raised as guards on our own honesty: **specification shopping** (three thresholds generate hundreds of specifications; publish the **specification curve** across the whole grid, not the best cell) and **truncated-feed survivorship** (a 100-row feed silently drops the busiest filing days — the days that matter; reconcile against EDGAR and bar `coverage_gap` intervals from enrollment).

---

## 4. DISAGREEMENTS (preserved, not smoothed)

| # | Question | Positions |
|---|---|---|
| **D1** | **Normalizer** | **Float-relative** (bp of free float): Challenger, Guardian, Expansionist — purest size-neutrality. **Liquidity-relative** (÷ median daily dollar volume): Outsider, Economist, Executioner — *"days of normal volume,"* how a trader actually sizes a print, and the most client-legible. Outsider: *"a $3T name and a $300M name both read '3.1 days.'"* |
| **D2** | **Time to first read** | **Week 3 via historical backfill** (Economist — Form-4 history on EDGAR + FMP volume history exist, so the placebo test can run on history immediately: *"a thesis that can be killed in three weeks for $20/mo is the best trade on this board's table"*). **Day 90** at n≈100 resolved (Executioner, Outsider). **Day 270** pre-registered first inferential read (Challenger — *"say so now so nobody reads the 30-day number"*). |
| **D3** | **Agents** | **One** (Executioner, defending Round 1: *"four agents alarm on the same root failure — the feed stopped — through four pagers. One engineer + four pagers = alert fatigue, then a muted channel, then an undetected outage"*). **Two** (Challenger, Expansionist, Outsider — one pipeline, one control/honesty auditor that must be able to kill the product independently). **Three** (Guardian — adds a firewall auditor). **Four checks in one module/endpoint** (Economist — moved substantially toward the Executioner). |
| **D4** | **Universe scope** | Cap at **300** (Executioner, self-pruning) · **1,200–1,800** small/mid, ≤8 analysts (Outsider) · **1,500** float-decile stratified (Expansionist) · **1,500–3,000** (Economist) · Guardian dissents on exclusion: **don't hard-exclude large caps — stratify by size decile and *show* where edge lives rather than assume it.** |
| **D5** | **Score shape** | **Stage-based** — DISPLACEMENT → EXPANSION → EUPHORIA → DISTRESS → PANIC (Economist, Kindleberger: *"a stage label is more honest and more useful than a single number"*). **Signed continuous** z/tanh in [−100, +100] (all others). |
| **D6** | **Statistical test** | Stratified **log-rank + Cox hazard ratio at α=0.01** (Economist) · **KM separation + bootstrap CI on the median-lead difference** (Outsider) · **excess arrival at 90d with cluster-bootstrap CI clustered by ticker** (Challenger) · **Wilson-interval LED-rate vs placebo** (Executioner) · **KM hazard ratio with CI excluding 1.0** (Expansionist). |
| **D7** | **Horizon** | 180d (Guardian, Outsider, Executioner) · 252 trading days (Challenger, *"makes any horizon readable off one estimator"*) · 365d (Economist, matching the attention ledger's patience window). |
| **D8** | **Crypto now or later** | **Cut entirely for 90 days** (Executioner — *"a refactor mid-build is how the one engineer loses a month"*). **Design now, serve absence now** (all others), with CFTC COT (Guardian) or spot-ETF flows (Challenger, Outsider, Economist, Expansionist) as the eventual observable. |

---

## 5. THE STRUCTURAL IDEA WORTH THE CHAIRMAN'S ATTENTION

Guardian's reallocation of the 13F data, which no other archetype phrased this way:

> *"Round 1 settled that curated-fund 13F top-10 membership is a weak **signal**. It is a strong **truth**. Data that is weak as a signal and strong as ground truth belongs on the **referee** side of the firewall. Removing it from the score is what makes it admissible as truth."*

i.e. quarter-over-quarter change in the count of 13F filers holding a name is literally *mainstream institutional money arriving* — a slow, signed, corroborating arrival clock. The same is true of Quiver: demoted from the score, it becomes a legitimate **control arm** (the known-lagged benchmark we must beat) and a US annex.

And Guardian's enforcement mechanism, which is the design's spine:

> **THE DESIGN RULE:** *the target of every verdict, every weight fit, and every published number must be an arrival event that is (a) not a price return, (b) on a `HELD_OUT_ARRIVAL_INPUTS` registry, and (c) compared against a matched control* — enforced by an agent plus a contract test that greps the resolution path for any price-return import.

**Never build, however impressive** (Guardian): a backtested P&L, equity curve or Sharpe · a ranked "top picks" buy list · any alert phrased as a trigger to act · a confidence-to-price-target mapping · paper trading · retroactive re-enrollment or any ledger rewrite · *"and, most insidiously, any horizon or threshold chosen after looking at results — the last one leaves no trace in the UI and destroys the moat entirely."*

---

## 6. WHAT THE CHAIRMAN MUST DECIDE

**Ruling required (the build cannot start without these):**
- **R1 — Proceed?** Build the money-movement system on the consensus blueprint (§2), at $0/mo new spend.
- **R2 — D1 normalizer:** float-relative or liquidity-relative ("days of normal volume")? *Note: these are not exclusive — both can be computed and one chosen as headline at pre-registration.*
- **R3 — D2 first read:** backfill for a week-3 falsification test, or forward-only with the first read at day 90/270?
- **R4 — D3 agents:** one, two, or three?
- **R5 — D4 universe:** cap and whether large caps are excluded or stratified.
- **R6 — D8 crypto:** freeze entirely for 90 days, or serve honest absence now with the design specified?
- **R7 — the pending Round-1 item:** `DARK_POS_WEIGHT=0` (config-only, no deploy) to remove the index-membership term from the live score now, or leave it until the replacement is proven?

**Already unanimous — needs only the Chairman's assent, not a choice:**
turn on `insider_feed()` · capture the discarded volume field · null cohort ships **before** the first live enrollment · new ledger tables (old one frozen and relabeled) · KM ported with Greenwood CI · pre-registration gate before any weight · universe as data · cut 13F `funds_holding` from the score · one published headline with n and CI · the refuse-to-publish list · EDGAR as source of record · resolve Finviz redistribution rights before any client-facing derived field · salted-hash actor IDs from day one.

**Cost:** $0/mo new subscriptions. Recoverable headroom identified: frozen-1.0 `essential-2` Postgres ($20), the redundant `nowtrendin-web` mirror, and Apify Scale→Starter (~$100–150) — which would also resolve the standing cap breach.

---

**Chairman — your ruling per item (R1–R7).**
