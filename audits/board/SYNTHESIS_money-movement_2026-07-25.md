# SYNTHESIS — Rounds 2 + 3: what the tool actually is, how to proceed, and what data feeds it
**Date:** 2026-07-25 · **For:** the Chairman · **Status:** synthesis + recommendations. Decisions flagged at §6.

Sources: `BOARD_market-crypto-signal_2026-07-25.md` (R1 diagnosis) · `BOARD_money-movement-build_2026-07-25.md` (R2 blueprint) · `BOARD_mechanisms-and-tools_2026-07-25.md` (R3 mechanisms) · the Chairman's mechanism brief and the Paulson/Pellegrini ruling.

---

## 1. THE INSTRUMENT, STATED IN ONE PLACE

Rounds 2 and 3 describe **one coherent instrument**. Neither round states it whole, so here it is:

> **A disclosure-to-participation latency instrument.** It measures how long it takes the market to react to a legally-compelled disclosure of money movement — and it proves, against a matched control and a never-deleted record, which disclosures are followed by real participation and how much warning they give.

Five stages, each settled by the Board:

| Stage | What it is | Settled by |
|---|---|---|
| **1. Trigger** | A mandatory disclosure becomes public: an open-market insider purchase cluster (Form 4, T+2), an activist stake (13D). We stamp **when it became knowable** — the *filing* instant, never the trade date. | R3 unanimous |
| **2. Observable** | Signed, liquidity- or float-normalized insider **buying breadth**, expressed as a deviation from the instrument's **own base rate**. A change, not a level. Never a size proxy. | R2 unanimous |
| **3. Clock** | **Abnormal SHARE volume** vs the instrument's own baseline, frozen before detection = participation expanded = the market noticed. Not price. Not our attention engine. | R2+R3 unanimous |
| **4. Measurement** | **LEAD = days from disclosure to participation expansion**, measured against a matched control cohort enrolled at the same time. | R2+R3 unanimous |
| **5. Proof** | Kaplan-Meier survival with Greenwood intervals, treated vs placebo, pre-registered, held-out, never deleted. Publish one headline with n and a CI. | R2+R3 unanimous |

**What it is NOT** — and the Board wants this in the methodology: it does not detect concealed accumulation, does not predict prices, does not touch non-public information.

## 2. THE TENSION BETWEEN THE ROUNDS — and the reframe it forces

This is the most important thing in this document.

**Round 2** accepted the goal as *"detect money moving before mainstream."* **Round 3** concluded we can only observe mandatory disclosures — which are, by definition, already public. The Challenger stated the consequence sharply:

> *"We are quietly redefining 'before it arrives' from **before the market** to **before the slow tail**... Opposing counsel needs one question: 'Isn't your lead just the time it takes retail to read a filing you both received simultaneously?'"*

**That question has to be answered before it is asked.** But the honest answer does not kill the product — it *repositions* it, and the repositioned version is more defensible and more sellable:

| ❌ What we cannot claim | ✅ What we can claim, and prove |
|---|---|
| "We see what insiders do before anyone else" | Everyone sees the same Form 4s. |
| "We detect hidden institutional accumulation" | Nobody at any budget does; concealment works. |
| "We predict where the price goes" | We refuse to make return claims. |
| | **"Of the thousands of disclosures filed each week, these are the ones historically followed by real market participation — and here is the measured warning window, with a control arm and a track record that can prove us wrong."** |

The scarce good is **not access — it is filtering and timing**. Everyone can read a Form 4. Almost nobody knows *which ones matter* or *how long the window is*, because measuring that requires a control cohort and a multi-year held-out record that cannot be assembled retroactively. That is the gap, and it is a real one.

**This is also exactly the Pellegrini lesson the Chairman ruled on.** Pellegrini's edge was not access — every mortgage figure he used was public. It was that he assembled the long, consistent, deflated series nobody had bothered to assemble, and it settled what narrative could not. Our analogue is not a cleverer signal; it is the **arrival-lag register**.

## 3. THE STRUCTURAL ASYMMETRY THAT MAKES THE PRODUCT WORK

Worth seeing plainly, because it is why a "slow" detection side is not fatal:

- **Detection side** — disclosure-bound. Slow (T+2 to 45 days), but *legally guaranteed to exist* and precisely timestamped.
- **Arrival side** — volume. Fast, mechanical, unconcealable, and measured on the instrument's own history.

The product is the **gap between them**. And the size of that gap is an **open empirical question nobody has answered**: what *is* the distribution of disclosure→participation latency, by size decile, by filer role, by year? If it is near zero, the thesis is dead and we will say so. If it is days-to-weeks in small/mid caps — which is what the Seyhun-descended literature implies — we have a real instrument.

**Either outcome is publishable, and we find out in months, not years.**

## 4. WHAT BOTH ROUNDS AGREE ON (no further deliberation needed)

1. **Mandatory disclosure is the floor and the ceiling.** Say so in the methodology.
2. **The null/placebo cohort ships BEFORE the first live enrollment.** It cannot be retrofitted without fabricating data. This is the single hardest ordering constraint in the project.
3. **Pre-registration before any component earns weight** — hypothesis, threshold, universe, stop rule committed to git *before* the analysis runs, SHA stored.
4. **New ledger; freeze and honestly relabel the old one** as the congress-flow record.
5. **Cut 13F `funds_holding` from the score** — and Guardian's reallocation: it is *weak as a signal, strong as truth*, so it belongs on the **referee** side (a change in the count of institutional holders is literally mainstream money arriving).
6. **Universe as data**, §16a-governed, small/mid-cap weighted — that is where the literature locates surviving edge, and our 16 hard-coded mega-caps are the regime where it is weakest.
7. **Crypto: honest absence** over a repaired proxy, until a real observable exists.
8. **Abandon in writing** (not backlog): stop runs / liquidity sweeps · Volume Profile / POC · dark-pool inference · gamma-hedging inference · any return, P&L, Sharpe or equity-curve claim.
9. **Cohort-level publication only** on anything involving named individuals.
10. **Publish one headline number** with n, a CI, and a param_version — never a naked point estimate.

## 5. RECOMMENDED SEQUENCE

Merging both rounds' orderings. Everything below is **$0 in new subscriptions** and **held-out** (imported by nothing in scoring).

### Phase 0 — finish the foundation (days, not weeks) — *no decision needed*
- **0a.** Fix the open Executioner items in `arrival_clock.py` **before any enrollment**: one wide fetch per ticker per day (today every ledger row mints its own HTTP call), an LRU cap on `fmp_data._CACHE`, pacing inside `_collect_phase` only, and deterministic `scheduled` stamps (rebalance / triple-witching / month-end) so the "scheduled arrivals" alarm can actually fire rather than being a promise.
- **0b.** **Verify FMP volume is consolidated (TRF-inclusive)**, not primary-listing-only. One API comparison. If it is exchange-only, the clock under-samples by ~half in the most-internalized names. *This gates everything downstream.*
- **0c.** Confirm the current **13D deadline** (shortened in 2024; our brief carries the stale "10 days").

### Phase 1 — the ledger and its control arm — *the critical path*
- **1a.** `flow_pending_detections` / `flow_ledger` / `flow_null_cohort` / `flow_prereg`, additive and forward-only, §14 canonical dates, registered with the datecanon auditor.
- **1b.** **Null cohort wired from row one**, at parity with the treated arm.
- **1c.** **Pre-registration lock** committed before the first enrollment — including calibrating `ARRIVAL_VOL_MULT` against the placebo cohort's unconditional arrival rate. (Today's 3.0 is a placeholder; enrolling first would permanently bake it in as a taste parameter.)
- **1d.** One monitoring agent, `flow_integrity`, folded into the existing `/monitor` `run_all`. **One, not four.**

### Phase 2 — persist what we already pay for and throw away
- **2a.** Turn on Finviz **`insider_feed()`** (verified dead code) → `insider_events`, market-wide, with salted-hash `actor_id` and a separately-keyed `actor_reference` table from day one (GDPR is a schema decision, not a later problem).
- **2b.** Persist **OFR full history** (currently fetched then dropped every 12h, memory-only) and **FINRA short-interest history** → `macro_series_daily`.
- **2c.** **Universe as data** from the Finviz screener (float, market cap, sector, analyst count — already paid for), §16a cold-start promotion.

### Phase 3 — the highest-value free upgrade
- **3a.** **SEC EDGAR Form-4 XML** through the full §16 five gates. Gets the **10b5-1 checkbox** (the opportunistic-vs-routine discriminator), exact transaction codes, officer role, and the acceptance timestamp. Three archetypes independently called this *"the single highest-value $0 upgrade on the board."* EDGAR becomes source of record; Finviz is the latency mirror with a coverage reconciliation.
- **3b.** **`insider_breadth_daily`** — the market-wide aggregate (Seyhun: the aggregate carries more content than per-name). Forward-only from today plus an unhurried backfill.

### Phase 4 — subject to decisions at §6
- Committee-alignment test (three pre-registered cells, cohort-level) — **blocked on D1**.
- Disclosure-latency series · 13D/G ingestion · absorption covariate (if approved).

**Timeline honesty:** first *interpretable* read at roughly 90–120 days; a defensible published verdict at 6–9 months. Anything published before that is a marketing number, and the Board said so in three separate voices.

---

## 6. DECISIONS REQUIRED FROM THE CHAIRMAN

| # | Decision | My recommendation |
|---|---|---|
| **R7** (from R1) | `DARK_POS_WEIGHT=0` — remove the directionless index-membership term from the live Market Signal score? Config-only, no deploy, one-command rollback. | **Yes, but capture before/after evidence first** (Executioner's condition). It is 6/6 condemned and ~22% of Money Movement is currently a quarterly index-membership step function. |
| **R1-breach** | `market_accuracy_ledger.regime_adjusted` computes **excess return vs SPY**, and `DEFERRED_ITEMS.md` P1 proposes citing it as proof the engine works. | **Ring-fence as an internal confound diagnostic.** Never a headline, never marketing, never a weight-fitting target. Strike the P1 proposal. |
| **D1** | Can the committee test use 2014-present history? Executioner: no — free rosters are current-only, so a historical join is lookahead. Expansionist: yes, backtest-only. | **Executioner wins on the facts.** Restrict to the current Congress, or forward-only. A lookahead-contaminated backtest is worse than no test. |
| **D2** | Composite aggregate index, or primitive observables only? | **Primitives first** (Challenger). Build the arrival-lag register and insider breadth as audited primitives; a composite on top of two audited primitives is defensible, one built first is not. |
| **D3** | Which self-contamination control? | **Executioner's** — store row-level fields now, publish no metric until a written trigger (>100 seats). *"A ratio computed over an audience of ~0 is theater."* Adopt Guardian's permanent holdout later if we scale. |
| **D4** | Finviz-first or EDGAR-first? | **Both, in that order** — Finviz now (it is paid for and dead), EDGAR next as source of record. Note the Challenger's catch: `insider_feed()` is capped at 100 rows and silently truncates on heavy filing days, which are exactly the cluster days we want. |
| **D5** | Absorption / turnover-compression covariate: one test or cut? | **Cut for now.** Two archetypes want one test; two want it gone. It is the weakest item and one engineer's time is the binding constraint. |

---

## 7. DATA SOURCES — the Board's recommended roster for the database

### 7a. ALREADY PAID FOR, CURRENTLY UNUSED OR DISCARDED — take these first ($0 marginal)

| Source | What it gives | Status |
|---|---|---|
| **Finviz `insider_feed()`** | Market-wide Form-4 in ONE call — the "Dark-Matter goldmine" per its own docstring | **Dead code** (called only under `__main__`). ⚠ capped at 100 rows + cached — truncates on heavy days |
| **FMP daily volume** | The arrival clock's entire input | **Was discarded**; now captured via `historical_ohlcv()` |
| **Finviz screener** | Float, market cap, sector, analyst count — universe construction + Seyhun size stratification | Live, underused |
| **OFR STFM** | Funding stress, repo, macro leverage — full history served | Fetched then **dropped every 12h, memory-only** |
| **FINRA short interest** | Bi-monthly short interest / days-to-cover; the borrow side is unconcealable | Live (~180d), **not persisted** |
| **QuiverQuant** | Congressional trades | Live. Demoted from score → **control arm + US annex** |
| **Databento** | Price verify, microstructure | Metered ~$0. Keep for cross-check only |
| **Nasdaq Trade Halts** | Official microstructure events | Already collected |

### 7b. FREE, RECOMMENDED — each needs the §16 five gates

| Source | Why the Board wants it | Priority |
|---|---|---|
| **SEC EDGAR Form-4 XML** | **10b5-1 checkbox** (opportunistic vs routine), exact transaction codes (P/S vs M/A/G/F), officer role, acceptance timestamp. Authoritative; public domain; no redistribution question | **#1 — "highest-value $0 upgrade"** |
| **SEC EDGAR 13D/G** | Activist stakes; genuinely pre-mainstream; strongest literature (Brav/Jiang). ⚠ verify the post-2024 deadline | **#2** |
| **CFTC Commitments of Traders** | Free, weekly, back to **1986** — signed by trader category (commercial / managed money / **non-reportable**), i.e. informed vs crowd in one series. Covers CME **BTC/ETH** → the only honest crypto observable we can afford | **#3** (and the crypto answer) |
| **SEC EDGAR 8-K / full-text** | Event disclosures; the disclosure-latency series | #4 |
| **SEC 13F (full, via EDGAR)** | **Reallocated** — not a signal, but *ground truth*: a change in the count of institutional holders IS mainstream money arriving (Guardian) | #5, referee side |
| **Committee rosters** (`unitedstates/congress-legislators`) | The committee-alignment test. ⚠ current-only — see D1 | #6 |

### 7c. INTERNATIONAL — free, for the expansion phase (Expansionist)

The strategic finding: **every input we rely on has a good international analogue except congressional trading, which has none anywhere** — and two analogues are *faster than their US equivalents*:
- **EU/UK TR-1** major-shareholding notifications — event-driven, days (vs 13F quarterly/45d)
- **ESMA/FCA net-short registers** — **daily, and they name holders above 0.5%** (vs FINRA's anonymous bi-monthly aggregate)
- Insider-disclosure regimes are near-universal: UK PDMR (4bd), EU MAR Art.19 (4bd), India SEBI (2bd), HK SFC (3bd), Japan EDINET, Canada SEDI, Australia App 3Y

### 7d. DEFERRED BY CHAIRMAN'S RULING
Options flow / OPRA ($2–10k/mo, and hedge-contaminated) · dark-pool vendors · paid on-chain (Glassnode/Nansen/Arkham) · borrow-rate feeds.

### 7e. REJECTED ON THE MERITS
Volume Profile / Point of Control (**not computable** — FMP's light endpoint has no high/low, so any POC would be fabrication) · liquidity sweeps / stop runs (unfalsifiable by construction) · expert networks / channel checks (the MNPI line) · dark-pool venue inference (the venue is precisely what is hidden).

### 7f. TABLES THIS IMPLIES

```
insider_events(id, ticker, filed_date, txn_date, actor_id_hash, role_class,
               txn_code, value_usd, shares, plan_10b51, source, ingested_at)
actor_reference(actor_id_hash PK, name, cik)      -- separately keyed, region-restrictable
arrival_events(ticker, arrival_date, observable, ratio_to_baseline, scheduled, param_version)
flow_pending_detections / flow_ledger / flow_null_cohort / flow_gate_rejects
flow_prereg(id, hypothesis, threshold, universe, stop_rule, registered_at, sha)
market_universe(ticker PK, sector, size_decile, float_usd, state, promoted_at, admit_reason)
macro_series_daily(mnemonic, signal_date, value, source, fetched_at)
insider_breadth_daily(signal_date PK, buyers_n, sellers_n, issuers_n, by size/role, plan_10b51_n)
congress_committee_roster(bioguide, member_name_raw, committee_code, chamber, congress_no)
```
All additive, forward-only, §14 canonical dates, registered with the datecanon auditor.

---

## 8. THE ONE-PARAGRAPH VERSION

Build a **disclosure-to-participation latency instrument**: trigger on mandatory disclosures we can timestamp exactly, measure how long until abnormal share volume shows the market noticed, prove it against a matched control with a pre-registered, never-deleted record. We cannot see concealed accumulation and should stop implying otherwise — but nobody knows *which* disclosures precede real participation or *how long the window is*, because answering that needs a control cohort that cannot be built retroactively. Start that register now, with the null arm from row one; everything else is purchasable later, and the register is not.
