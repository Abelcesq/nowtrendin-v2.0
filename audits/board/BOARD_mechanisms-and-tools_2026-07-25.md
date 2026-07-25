# ADVISORY BOARD — ROUND 3: MECHANISMS & TOOLS for identifying money-signal flows
**Convened:** 2026-07-25 by the Chairman · **Six archetypes, independent, no cross-visibility**
**Charge:** be clear on the CONTEXT and PERSPECTIVE on how big money actually moves, and which tools can detect it — using only what we already have ($0 new spend).

Prior rounds: `BOARD_market-crypto-signal_2026-07-25.md` (diagnosis) · `BOARD_money-movement-build_2026-07-25.md` (blueprint).
Chairman's rulings in force: implement the unanimous blueprint · **defer options flow and all new paid sources** · the Paulson value is the **mechanism** (Pellegrini's long series + asymmetry), not the narrative.

---

## 1. THE HEADLINE CONCLUSION — unanimous, and it is a clarifying one

**Mandatory disclosure is our floor AND our ceiling on the money side. The Board asks that this be written into the methodology in plain English.**

The Chairman's own brief contains the reason: institutions engineer execution to be *undetectable* — order splitting, TWAP/VWAP, dark pools exist precisely to suppress the footprint we would want to detect. So:

- **Detection side** = legally compelled disclosures on their statutory clocks (Form 4 T+2, 13D/G, 8-K, 13F), plus mechanical residue nobody can conceal (aggregate volume, short interest/borrow, halts).
- **We never see intent, and we never see concealed execution.** No product at our budget does.

> **Guardian:** *"Admitting this strengthens the moat. The constraint is legal, therefore symmetric — no competitor beats it without paying or breaking the law. Our differentiator was never access; it is assembly."*
> **Outsider:** *"That sentence loses nothing — it is what an allocator wants to hear, because the alternative claim is one they know is false."*
> **Economist (Grossman-Stiglitz, not Fama):** *"Information-gathering earns roughly what it costs. Our marginal data cost is $0, so our expected PRICE edge is $0. That is arithmetic, not defeatism. What survives is a different good: dated observation."*

**The corollary the Board wants stated:** the arrival clock is **a clock, not a detector**. Never let a UI or memo blur the two.

## 2. UNANIMOUS: RENAME WHAT THE CLOCK MEASURES

Four archetypes independently reached the same correction from Harris's microstructure: observed volume is *intermediated* participation — a single $10M institutional buy prints far more than $10M of tape as dealers pass inventory, by a multiplier that varies by name and regime.

So the clock measures **turnover / participation expansion**, NOT "the crowd arriving" and NOT "mainstream money".

> **Challenger:** *"The moment we publish 'arrival', we assert something about WHO, which we do not observe."*
> **Outsider:** *"For a timing measurement that is fine — the multiplier scales the spike, it does not move the date. For any claim about magnitude it is disqualifying. **Never publish '$X of money moved.' Publish the date.**"*

## 3. THE CONTAMINATION QUESTION — the Outsider WITHDREW his own round-2 proposal

He proposed the "contamination ratio" in round 2 and retracted it here: *"a ratio implies we can decompose initiating flow from intermediation, and we cannot."* All six proposed replacements; they differ (see §6, D3) but converge on **partition or removal rather than estimation**.

**The Outsider's most useful single correction — and it cuts against the Chairman's reading list:**
> *"**Lewis is the wrong book for our timescale.** Flash Boys is about microseconds — latency arbitrage and order-routing conflict. Our clock resolves in DAYS, requires persistence across sessions, and measures against a 60-session baseline. There is no mechanism by which a millisecond-scale intermediary contaminates that. HFT front-running is real and simply orthogonal to us. **Harris is the right book**, and he says something more awkward."*

**Also: the dark-pool sampling fear is largely misplaced, which materially rescues the clock.** ~40–50% of US equity volume executes off-exchange, but off-exchange executions are *reported to the consolidated tape via the TRFs*. What is hidden is **pre-trade** (book depth, venue attribution), not the executed print. Consolidated volume is not a biased sample of participation — it is an **unattributed** one.

⚠ **ACTION BEFORE ENROLLMENT (Outsider, not optional):** verify FMP's volume is **consolidated (TRF-inclusive)**, not primary-listing-only. If exchange-only, the clock silently under-samples by ~half in exactly the names with heaviest internalization. One API comparison settles it; put it in the pre-registration.

## 4. RULINGS ON THE CHAIRMAN'S RED FLAGS

| Red flag | Board ruling |
|---|---|
| **Cluster buying (3+ C-suite)** | **ADOPT** — already in the blueprint; Seyhun-grounded. Use *breadth* (count of distinct buying insiders), not net dollars. |
| **Open-market vs grants** | **ADOPT** — already specified (P/S codes only; exclude M/A/G/F). Parse transaction CODES from EDGAR XML, not Finviz strings. |
| **Committee alignment** | **TEST, heavily conditioned** — see §5. |
| **Unusual options activity** | **DEFERRED by Chairman's ruling** (cost). Board concurs. |
| **Dark-pool prints** | **ABANDON** — venue attribution is the very thing that is hidden; the executed prints are already in our volume. |
| **Volume Profile / Point of Control** | **ABANDON as specified.** ⚠ Verified by the Challenger: FMP's `historical-price-eod/light` returns **date, close, volume only — no high/low**. There is no intraday range, therefore no volume-at-price. *"Any POC we built from close+volume would be a fabrication dressed as microstructure."* Executioner adds the decisive point: *"'heavy volume in a tight range' is the NEGATION of our arrival clock's event. We would be building a second, weaker detector whose premise is that the first one's signal is absent."* Two archetypes offer a salvageable cousin (a turnover-compression / absorption residual) as a low-priority **covariate**, never a standalone signal. |
| **Liquidity sweeps / stop runs** | **ABANDON — UNANIMOUS, and explicitly "in writing, not backlog."** The pattern is defined by the reversal that identifies it; there is no ex-ante definition that does not embed its own outcome. *Guardian:* "A rule that requires knowing the answer to state the question cannot be pre-registered." *Outsider:* "A CIO would not laugh; he would stop taking the meeting." *Economist:* "Record the rejection so it does not return in round four." |

## 5. COMMITTEE ALIGNMENT — approved to TEST, and much harder than it looks

All six say the idea is **legitimate and genuinely untested** (the prior null pooled ~500 members undifferentiated and asked a *returns* question). All six also impose conditions. Verified this round: **the string "committee" appears nowhere in the codebase**, and Quiver's payload carries no committee field — this is a join we build.

**⚠ The Executioner found what may be a killer, and it is verified:** the free roster source (`unitedstates/congress-legislators`) publishes **current** membership. Point-in-time membership by Congress is not cleanly free. *"Applying the 2026 roster to 2014 trades is lookahead contamination of exactly the kind §14 exists to prevent. **Ruling: the backtest cannot run over 113k historical rows.**"* Either restrict to the current Congress (~2 years of rows) or accept forward-only enrollment. **This directly conflicts with the Expansionist's plan to use the 2014-present bulk history — see D1.**

**Consensus conditions:**
- **Reframe from returns to lead-time** — does an aligned purchase precede turnover expansion sooner than matched controls?
- **Detection timestamp = the FILING date, never the trade date.** *Challenger: "Using the trade date buys ~30 days of free 'lead' from information we did not have. This is the single most tempting and most invisible lie in the design."*
- **Pre-register exactly three cells** (Armed Services→defense; Health→biotech; Financial Services→banks), Bonferroni-corrected — against ~220–440 possible committee×sector cells (Challenger counts up to ~16,000–32,000 full specifications). *Economist: publish the full grid regardless of outcome; "a lone surviving cell shown without its 219 siblings is a fabrication by omission."*
- **The right control is the same member's NON-aligned purchases**, not a random ticker — that controls for "some members just trade a lot."
- **Gate zero is a COUNT, not a test.** Estimates range from tens to low hundreds of aligned purchases per year; after episode collapse, single digits to low tens per cell. Pre-register a minimum n (30–60 suggested) and **publish "underpowered" rather than a rate** if it isn't met.
- **Cluster the bootstrap by MEMBER and by TICKER** — one prolific trader can drive the whole result.
- **Cohort-level publication ONLY. Never name a legislator.**

## 6. THE MNPI BOUNDARY — the Guardian's permanent line (adopt verbatim)

> **"We observe only what the law compelled someone to publish, on the schedule the law set. We never attempt to learn a specific non-public fact before its lawful disclosure, and we never obtain information from a human source."**

Three categorical differences from the *Black Edge* / SAC fact pattern: **source** (every input is a filed public document), **channel** (we operate no human-source channel — no expert networks, channel checks, employee panels), **position** (we hold none, trade none, advise none). SAC's liability required an information *source*; we have only filings.

**The defamation point, which all three legally-minded archetypes raised independently and which exceeds the securities exposure:**
> *"'Members of committee C traded sector S at N× the unaligned base rate' is a statistical statement about public records — legitimate. 'Senator X traded on privileged committee knowledge' is an imputation of a federal crime against a living, identifiable person: **defamation per se**, where truth is the only defense and a filing date alone cannot carry it. **A system that mints accusations at scale is the fact pattern for reckless disregard.**"*

**Rule: cohort-level only. No per-member score. No "unusual/suspicious/red-flag" label on any named person, ever.**

**Language purge extended** (add to the F6 refusal-guard word list): *"knew," "ahead of the announcement," "non-public," "anticipated," "unusual," "suspicious," "smart money," "front-running."*

⚠ **Guardian's live audit finding — R1 breach already in the code:** `market_accuracy_ledger.report().regime_adjusted` computes **excess return vs SPY**, and `audits/DEFERRED_ITEMS.md` P1 proposes citing it as evidence "the Money Gradient works." *"That is a return claim — a track record with the P&L relabelled. Ring-fence as an internal confound diagnostic. Never a headline, never marketing, never a weight-fitting target."* **This needs a Chairman ruling.**

## 7. PELLEGRINI OPERATIONALIZED — what only we can build

Unanimous on the principle: assemble the long, boring series nobody else maintains. Unanimous on the *reason* it is a moat:

> **Economist:** *"The only series a better-funded competitor cannot buy later is one whose observations exist ONLY if you were watching that day. Everything else on this board is purchasable. Friedman and Schwartz did not out-theorize anyone. They assembled the series."*
> **Challenger:** *"Nobody who starts later can obtain it: **you cannot enroll a placebo in the past.**"*

**Series ranked by consensus:**
1. **The arrival-lag register** (all six) — detection date, frozen baseline, disclosure anchor, arrival date, arm label, param_version; never deleted. Unreconstructable ex post at any budget. *This is the moat.*
2. **Market-wide insider-buy breadth** (Challenger, Guardian, Expansionist, Economist) — daily count of distinct open-market-buying insiders, size- and role-stratified. Seyhun's finding is that the **aggregate** carries more content than per-name. Free from EDGAR. *Economist's honest caveat: a full 2003 backfill is ~8M filings — do forward-only from today (~1,500/day) plus an unhurried trickle. "The discipline is the asset, not the heroics."*
3. **The disclosure-latency series** (Guardian, Outsider, Executioner) — the empirical distribution of event → filing → our ingestion, per filing class. *"The honest map of how stale the 'legally guaranteed' footprints actually are — it answers Q1 with data instead of argument."*
4. **The null archive** (Challenger) — every pre-registered hypothesis with SHA and date, **including every failure**. *"What makes 1 and 2 believable."*

**Asymmetry applied to CLAIMS, not trades** — the consensus formulation:
> Cap the downside: every claim ships with n, an interval, a param_version, a stop rule, and a pre-commitment to publish failures — so the worst case is *"they measured, it didn't work, and they said so."* Leave the upside uncapped: the register compounds and cannot be bought. **Corollary: never make a claim whose downside is unbounded** (a return claim, a ranked buy list, a named-person allegation). *Economist:* "Be quiet cheaply, most of the time, so the rare confident statement carries a record behind it. **Claim volume should be inversely proportional to interval width.**"

## 8. ⚠ THE BOARD FOUND FOUR DEFECTS IN THE CODE BUILT THIS SESSION — ALL REPRODUCED AND FIXED

The Executioner's production review and the Guardian's firewall audit found real bugs. **Each was independently reproduced by probe before being fixed** (§10a), then pinned with a regression test.

| # | Defect | Status |
|---|---|---|
| **D-a** | **R1 FIREWALL LEAK (Guardian).** The clock ran on DOLLAR volume (close×volume). Probe: share volume flat + price 3× → **fired** (ratio 3.0); share volume 5× during a −70% crash → **silent**. A pure price move triggered the instrument whose entire justification is that it is not price. | **FIXED** — primary observable switched to **share volume** ratioed to its own frozen baseline; dollar volume retained as display-only context. `param_version` → `arrival-v2-sharevolume`. Two regression tests added. |
| **D-b** | **`compare_arms` generator exhaustion (Executioner).** A generator control arm was consumed by the first KM call, so `control_arm_present` read **False** — silently turning a real comparison into an unverified claim. | **FIXED** — both arms materialized first. |
| **D-c** | **`pre_arrived` asymmetry (Executioner).** It fired on ANY single prior threshold day while `find_arrival` required persistence — so a lone block print removed a row from the lead denominator on evidence too weak to be an arrival. *Shrinks the denominator in the direction that flatters us.* | **FIXED** — same persistence rule both sides; regression test added. |
| **D-d** | **Window semantics ambiguity (Executioner).** `hits_required=2, window=5` actually means "the crossing day plus 1 of the following 4", not "2 of the next 5". Would have been frozen into `param_version` at enrollment. | **FIXED** — semantics documented exactly, with a warning that changing them mints a new cohort. |

**Still open from the Executioner's review (not yet fixed, no rows enrolled so not yet binding):**
- **Cache-key claim is false at scale.** `historical_ohlcv` shares the key `hc:{tkr}:{frm}:{to}`, but `frm`/`to` derive from each row's detection date — so **every ledger row mints its own HTTP call**. Invisible at 16 tickers; hundreds of calls per sweep at market-wide enrollment. Fix: one wide fetch per ticker per day, sliced in memory.
- **`fmp_data._CACHE` is unbounded** — a slow memory leak that surfaces as dyno R14, not an obvious failure.
- **Pacing/placement:** `arrival_for` is a blocking fetch with no pause; it must run only in the scheduler thread inside `_collect_phase` with `COLLECT_SOURCE_PAUSE_S`, never behind an API endpoint (§13; the 2026-07-06 wedged-prewarm lesson).
- **`scheduled` is hard-coded `None`** — so the round-2 "alarm if >25% of wins are scheduled events" **cannot fire**. It is a promise, not a control. Deterministic artifacts (rebalance/triple-witching/month-end) are stampable today at $0.
- **Nothing is committed or deployed.** *Executioner: "'Built and verified' currently means 'self-tests pass on the founder's laptop.' That is the correct state; do not let it be described as shipped."*

## 9. DISAGREEMENTS (preserved)

| # | Question | Positions |
|---|---|---|
| **D1** | **Can the committee test use history?** | **Executioner: NO** — point-in-time rosters aren't freely available; a current-roster join to 2014 trades is lookahead. Forward-only or current-Congress only. **Expansionist: YES** — use 2014-present bulk, "backtest power is adequate; forward-live power is not," so it must be a backtest-only finding. *Directly opposed, and the answer determines whether this test is feasible at all.* |
| **D2** | **Composite aggregate index?** | **Economist:** build the insider-breadth aggregate (Seyhun: the aggregate beats per-name). **Challenger dissents in part:** *"a composite is precisely where circularity and specification freedom re-enter. Series 1 and 2 are primitive observables. A composite built on top of two audited primitives is defensible; one built first is not."* **Outsider dissents:** *"latency is one number with one meaning"* — prefers the latency series alone. |
| **D3** | **How to handle self-contamination** | **Guardian:** a permanent pre-publication **holdout** (a random fraction never surfaced to customers) — the only clean measurement, $0. **Expansionist:** stamp `disclosed_to_clients` and headline the never-disclosed subset — a partition, not an estimate. **Executioner:** store row-level fields but publish **no** metric until a written trigger (>100 seats) — *"a ratio computed over an audience of ~0 is theater."* **Economist:** anchor the clock to the EDGAR acceptance timestamp so contamination is definitionally irrelevant. |
| **D4** | **Finviz vs EDGAR first** | **Challenger ranks EDGAR ABOVE turning on `insider_feed()`** (complete, free, 10b5-1 checkbox, no redistribution question). Most others: turn on the paid-for feed first, EDGAR next. Note the Challenger's supporting catch: `insider_feed()` is **capped at 100 rows** and cached — *on heavy filing days, the clusters we most want, it silently truncates.* |
| **D5** | **Absorption / turnover-compression covariate** | Challenger and Expansionist would allow **one** pre-registered test (with an M&A-pin exclusion — a target pinned at a deal price is the strongest absorption signature in the market and is 100% public). Outsider and Executioner say cut it entirely ("we would rediscover volatility clustering and be unable to say which way"). |

## 10. ⚠ FACT-CHECK FLAG

**Economist:** the brief's "13D — 10 days" is **the old rule; the deadline was shortened in 2024.** Verify the current statutory deadline before it is written into any methodology document or pre-registration.

## 11. CONSENSUS NEXT-BUILD ORDER

Merging all six rankings (items appearing in ≥4 lists, in consensus order):

1. **Flow ledger + null/placebo cohort wired from row one** + the pre-registration lock. *Cannot be retrofitted without fabricating data.* Also: `ARRIVAL_VOL_MULT=3.0` is documented as requiring calibration **against the placebo cohort** — which does not exist yet. Enrolling first would permanently bake 3.0 in as a taste parameter.
2. **Persist what we already fetch and discard** — `insider_feed()` (verified dead code), OFR full history (fetched then dropped every 12h, memory-only), FINRA short-interest history. No spend, no new source gates, and it starts the clock that cannot be bought later.
3. **EDGAR Form-4 XML** (§16 five gates) — 10b5-1 checkbox, exact transaction codes, officer rank, acceptance timestamp. Called *"the single highest-value $0 upgrade on the board"* by three archetypes.
4. **Universe as data** — 16 hard-coded tickers is the binding constraint on everything above, and it is the mega-cap regime where Seyhun says the signal is **weakest**.
5. **Fix the open Executioner items** (§8) before enrollment freezes anything.
6. **Committee-alignment test** — three pre-registered cells, cohort-level, subject to D1.
7. **Disclosure-latency series.**

**Abandon explicitly, in writing (not backlog):** liquidity sweeps / stop runs · Volume Profile / Point of Control · dark-pool inference · gamma-hedging inference without options data · the published contamination ratio · per-member congressional attribution · any return/alpha/P&L claim. *Executioner: "an aspirational backlog with one engineer is a lie told slowly."*

---

## 12. THE SHARPEST WARNING OF THE ROUND

> **Challenger:** *"We are quietly redefining 'before it arrives' from **before the market** to **before the slow tail**, and nothing in the current design forces us to notice. Our trigger is a public document that algorithms consume in milliseconds. Our clock is consolidated turnover, which includes those algorithms' intermediation. If the turnover expansion we score as 'arrival' is mostly the disclosure being consumed, then a strong measured lead is evidence of a **slow measurement instrument**, not a fast one — and the result would look identical either way. Opposing counsel needs one question: 'Isn't your lead just the time it takes retail to read a filing you both received simultaneously?' The answer must be built, not argued."*

What builds the answer: the `disclosure_echo` stamp (arrivals within ~3 sessions of the filing reported separately, excluded from the headline), the deterministic `scheduled` stamps, the specification curve instead of a single cell, and the aligned-vs-unaligned control.

> **Guardian, on what this round must not become:** *"A market-microstructure trading desk wearing a measurement disclaimer. The tell: **if the natural next sentence after our output is 'so you should buy,' we have crossed.**"*

---

**Chairman — decisions requested:** D1 (can the committee test use history at all?), D2 (composite index or primitives only?), D3 (which contamination control), D4 (Finviz-first or EDGAR-first), D5 (absorption covariate: one test or cut), plus the **R1 breach ruling** in §6 (`regime_adjusted` excess-return diagnostic) and confirmation of the §11 build order.
