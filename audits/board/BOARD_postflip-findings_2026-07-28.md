# ADVISORY BOARD — POST-FLIP FINDINGS (F-1..F-4) + the solution
**Convened:** 2026-07-28 by the Chairman · **Six archetypes, independent, no cross-visibility**
**Scope:** the four findings from the first post-flip cycle (engine v292).
**Outcome: the Board REFUTED the pack's own root causes on two of four findings, and found
five defects the pack never raised.**

---

## 0. THE PACK WAS WRONG — corrections accepted, independently re-verified

Two diagnoses I put in front of the Board (and in front of the Chairman) were **false**. Both
are §10a violations committed by the very process that enforces §10a. Re-verified in code:

| Claim I made | Truth (verified) |
|---|---|
| **F-3:** "`grep -c degenerate financial_risk_gradient.py` → 0 — the market path NEVER HAD the guard; missing feature." | **FALSE.** The guard is `market_signal_engine.py:234` and `financial_risk_gradient` calls straight into it (`apply_market_signal`, :2380/:2576). It is **live and firing** on hundreds of components. I grepped a file that does not score components and called it a root cause. |
| **F-1:** "SpaceX is PRIVATE; its proxy carries only congressional data." | **FALSE.** `financial_risk_gradient.py:1129` — *"SpaceX IPO'd 2026-06-12 on NASDAQ:SPCX."* It is public. The whole private-proxy hypothesis rested on an error. |
| **F-2:** "B9 watches the Finviz insider feed only." | **Wrong in a worse direction.** `insider_flow.py:481` returns `{"status":"OFF"}` when `INSIDER_FLOW != 1` — which is live config. **B9 watches NOTHING today.** |

> **Challenger:** *"This is the §10a gotcha recurring three days after it was codified. A grep
> count is evidence; it is not a diagnosis."*
> **Guardian:** *"The pack itself asserted a root cause nobody traced — the same shape as the
> 2026-07-23 F1 gotcha that produced §10a."*

## 1. THE REAL ROOT CAUSES (converged, independently verified)

**F-1 — a BASELINE-EPOCH artifact, not a signal, and arithmetically demonstrable.**
`get_market_baselines(lookback=12)` (`market_signal_engine.py:640`) reads the item's own last
12 cycles ≈ **3 days at 6h cadence — a window that STRADDLES the parser flip**. `current` is
post-flip; the mean is dead-parser-era. The Economist reproduced the number exactly: `stdev` is
floored at 0.05, mean ≈ 0.1575, current 0.0 → **z = −3.15 precisely**, and `_z_to_unit` clamps
at 0.05 → served **5.0 is a left-censored RAIL** (z = −3.15 and z = −10 both render 5.0).
**Consequence: EVERY post-flip insider z on EVERY instrument is currently measured across a
definitional break.** Self-clears ~12 cycles (~3 days) as contaminated points roll out.

**F-3 — a STALE PRE-GUARD ROW, not a missing feature.** `drawdown.scored_at = 2026-07-04` —
**23 days stale, and the ONLY one of 300 rows scored before 2026-07-20**, when the D7 guard
shipped. It serves its pre-guard `serve_payload` verbatim, exactly as INV-1 requires, and will
keep doing so for the rest of the 365-day retention because it will never re-score.
**The general defect is far worse than the instance:** *every display-integrity guard we ship is
forward-only; stale rows keep serving the pre-guard state indefinitely, and nothing counts them.*
Secondary (Economist/Expansionist): the predicate `stdev <= 0.05 AND current == mean` is
**float-exact against a 3dp-rounded stored mean** — brittle by construction, and unit-dependent,
so it cannot survive new asset classes or currencies.

**Denominator dispute (Challenger):** 1.4% (6/439) is a **survivor** denominator — of 2,100
component slots, 1,661 are absent/degenerate and only 439 serve a number. Defensible figures are
**86%** (6 of 7 on the affected topic) or **0.29%** (6/2,100). Never 1.4%.

## 2. FIVE DEFECTS THE PACK NEVER RAISED

1. **THE LEDGER'S PUBLISHED WINS ARE UNCORROBORATED** (Challenger; I re-verified live):
   `/accuracy/ledger` → `led: 11`, **`ledCorroborated: 0`**, `ledUncorroborated: 9`,
   **`ledAmbiguousQuery: 8`**. The independent Wikipedia referee has confirmed **zero** wins, and
   8 of 11 rest on a query the system itself flags as a weak Trends match — while `hitRate 11.3`
   is served beside a KM `eventual 3.5%`. *"The discreditable pair."*
2. **THE MATURITY SEGMENTATION IS A TAUTOLOGY** (verified): `maturityCoverage.by_topic_maturity
   = 0` — `topic_maturity` is empty, so §14's ESTABLISHED/MONITORING exclusion is **not operative**,
   and `earlyDetectionHitRate` (11.3) is **identical** to the blended rate. It is not a cohort.
3. **ENROLLMENT FAILS OPEN** (Challenger): on a statement timeout `_record_top_detections`
   retries **without** the maturity filter (:637) — silently reverting to the pre-2026-07-07
   polluted population, with nothing marking the fallback rows.
4. **POSSIBLE ENTITY-RESOLUTION ERROR — the Outsider's diligence-killer:** SPCX serves hard
   financials (net margin −26.4%, ROE −11.9%, D/E 0.73) under a definition reading *"the
   company's own reported financials."* SpaceX IPO'd 2026-06-12, so financials may legitimately
   exist — **but nobody has verified the mapping is the right entity.** *"The failure a quant
   finds in ninety seconds and cannot unsee."* **UNVERIFIED — must be checked before anything else.**
5. **`transfer/maint_dbfix.py` IS A LOADED GUN** (Executioner): its `DELETE ... rn > KEEP_CYCLES`
   is a **count-based prune, explicitly forbidden by §13**. Never run it.

Also flagged: `/diagnostic/market/drawdown` returns `verdict: VALID, "Score is supportable"` on
the single worst read in the system, and reports `reported_detection: 0` while `/risk/scores`
serves 30.0 — an INV-1 serve-consistency break. **Prewarm is O(N)**: full warm 423s, scores feed
188.7s at 3,819 rows — *"at 100x it never finishes, and the 25-minute TTL guarantees permanent
in-flight churn."* And **the entire market path is US-only by construction** (SEC Form 4, US
Congress, FINRA, NASDAQ, USD) — the largest strategic gap, unmentioned in the pack.

## 3. THE GATE THAT UNBLOCKED THE FLIP WAS NOT A TEST

**Challenger:** the accepted criterion ("max served insider |z| < 1.5") was measured on **three
observations** — and **one of the three was `drawdown`'s fabricated `z: 0.0`**. **Economist:** a
max over per-instrument z's with n ≤ 12 each is *"an order statistic over mutually
non-comparable distributions,"* mechanically decreasing as the population shrinks — *"a
criterion a data outage can pass is not a criterion."* Both independently: **restate it**, on a
stated minimum n, measured **after** the baseline washout. (Note: live now, 6+ NON-insider
components exceed |z| 1.5 — WLDS Signal Freshness +3.15, bond_selloff +2.28.)

## 4. VERDICTS

| | Challenger | Guardian | Economist | Executioner | Expansionist | Outsider |
|---|---|---|---|---|---|---|
| **F-1** | REJECT reading | REJECT serving | REJECT | SHIP-LATER | APPROVE (transient) | **REJECT** |
| **F-2** | APPROVE-COND | **REJECT posture (BLOCKING)** | **BLOCKING** | SHIP (5 lines) | **APPROVE-COND (my one BLOCKER)** | **REJECT deferral** |
| **F-3** | REJECT cause+denominator | APPROVE-COND (not that fix) | APPROVE-COND | **CUT the proposed fix** | APPROVE-COND | REJECT cause |
| **F-4** | APPROVE-COND | APPROVE (can ride) | APPROVE-COND | SHIP (alarm only) | APPROVE-COND | APPROVE-COND |

**F-4 is NOT the 07-06 outage class** (Executioner, verified): `/prewarm last_run` is current,
the warm **completed**, `busy (another build in flight)` is single-flight **working as designed**,
and `/scores?limit=200` returns 200 in **0.78s**. `/engine-recovery` is contraindicated. The real
F-4 finding is the **ledger enrollment timeout on a GROWING query** (two full `GROUP BY` scans
over a `velocity_scores` table on 365-day retention, fired at peak write pressure) with **no
alarm** — a bare `print`.

## 5. THE ONE DISAGREEMENT: where does `INSIDER_FLOW=1` go?

- **Challenger — FIRST.** *"Flipping it is what STARTS the B9 tripwire running at all. Holding
  it gives us no safety — it only keeps the alarm switched off."* `FLOW_ENROLL=0` keeps the panel
  out of every published number.
- **Guardian, Economist, Expansionist, Outsider — LAST.** *"Never begin a permanent record while
  its source has no armed liveness contract and its baselines are known-contaminated: you would
  be writing an un-deletable ledger of numbers you cannot defend."* Economist adds the decisive
  point: rows accrued now are **stamped with a contaminated epoch and cannot be repaired** under
  the 365-day retention rule.
- **Executioner — MIDDLE.** Alarms first, then flip, then optimisation.

**RESOLUTION (Chairman's synthesis).** The Challenger's premise is true but argues for the wrong
remedy: B9 being flag-gated is a **defect to fix**, not a reason to flip. The Guardian states the
rule directly — *"a liveness check that turns off with the feature is not a liveness check."*
**Un-gate liveness; do not flip to arm it.** Then 5 of 6 agree the flip goes after.

## 6. THE SOLUTION — ordered, each item display-only or additive; no score-side change

**S0 — TODAY, before anything else.** Verify the SPCX entity mapping and audit every proxy
resolution (Outsider's killer, unverified). If wrong, correct or suppress immediately.

**S1 — Un-gate + generalise liveness (the one true blocker).** Do NOT build a framework. Two
converging minimums: register `finnhub` in the EXISTING `collector_health.COLLECTOR_EXPECTATIONS`
+ one `log_collector_run()` call at its call site (Executioner — the `alphavantage` precedent is
already in that file, `critical: False` so a quiet source degrades but never blocks); and hoist
`liveness()`'s two predicates out of `insider_flow` so they read a table, **not gated on any
feature flag** (Guardian). Register it in `/monitor run_all` — *"an alarm nobody hears is
decoration"* (Outsider). **Must not become:** per-source thresholds, severity tiers, YAML, a
plugin API, or anything requiring a human to remember to add a source.

**S2 — Enrollment: fail CLOSED + alarm.** Remove the maturity-filter fallback; add a durable
failure counter; alarm in `pipeline_integrity` on "enrollment errored" or "0 enrolled ×2 cycles";
one retry after `SCORE_BATCH_PAUSE_S`. Then either populate `topic_maturity` **or delete the
exclusion claim from §14** — do not keep a filter that does nothing.

**S3 — Ledger disclosure (do not publish into this).** Suppress or asterisk `hitRate` while
`ledCorroborated = 0`; stop serving `earlyDetectionHitRate` as a cohort while
`by_topic_maturity = 0`; never print 28.2% beside KM 3.5% without both denominators.

**S4 — Baseline epoch (F-1).** Stamp `series_epoch` on `market_signal_history`, bump at any
parser/definitional change, filter baselines to the current epoch, and serve **CALIBRATING**
below `MIN_BASELINE_CYCLES` in-epoch. Also stamp `rail: true` whenever `_z_to_unit` clamps — a
censored value must never wear the measured badge. *Cheap alternative if deferred: wait ~12
cycles for washout — but the epoch stamp is what prevents the NEXT flip from doing this again.*

**S5 — Degenerate invariant + stale-payload census (F-3).** Replace the float-exact predicate
with a scale-relative one (`stdev <= max(floor, ε·scale)`, or distinct-value count == 1) —
closes F-1's and F-3's shared branch defect. Add a **stale-payload census** counting rows whose
`scored_at` predates the newest display guard (today: 1), plus serve-side staleness disclosure.
Extend the `.githooks` cold-start gate to fire on **lane** changes, not just ticker lists.

**S6 — THEN `INSIDER_FLOW=1`**, after S1–S2 land and the F-1 washout is confirmed by measurement.

**S7 — Next batch:** incremental/delta prewarm (O(N) is a scheduled failure); enrollment SQL off
`topic_lifecycle`; retire `baseline_relative: true` as a user-facing badge and the jargon with it
(*"degenerate baseline," "z," "Cross-Market Diffusion"* → plain English).

---
*Six memos, faithfully collated; full texts in the session record. Every correction in §0 was
independently re-verified by the Chairman's agent before adoption. Nothing has been flipped.*

---

## S0 — EXECUTED 2026-07-28: entity-resolution audit. **CLEARS. The diligence-killer was a false alarm.**

Verified against the data provider the engine actually uses (`fmp_data.profile`, the `/stable`
path — note the v3 `/profile` endpoint 403s on this plan for EVERY ticker, so a 403 there is
not a per-ticker signal).

**SPCX is genuinely SpaceX.** `companyName: "Space Exploration Technologies Corp."` · NASDAQ ·
`ipoDate: 2026-06-12` (matches the code comment exactly) · `isEtf: False` · `isFund: False` ·
`isActivelyTrading: True` · Aerospace & Defense · description is unmistakably SpaceX (rockets,
spacecraft, satellite broadband).

**The financials are its own, and arithmetically correct.** Both income statements are stamped
`symbol: SPCX`: FY2025 revenue **$18.674B**, net income **−$4.937B** → net margin
**−26.44%**, which is exactly the served **−26.4%**; FY2024 revenue $14.015B → the served
revenue growth **33.2%**. A negative margin on a just-IPO'd, capital-intensive launch business
is unremarkable. **No lookalike ticker, no misattributed balance sheet.**

**Full mapping audit — 23 of 23 correct:**
- **16/16 `WATCHLIST_TICKERS`** resolve to the right entity (the single flag, IBM → *International
  Business Machines Corporation*, was my matcher not knowing IBM is an initialism, not a defect).
- **7/7 crypto-exposure proxies** resolve correctly AND their declared `kind` agrees with
  reality: COIN → Coinbase Global (exchange), MSTR → Strategy Inc (treasury, not a fund),
  IBIT/GBTC/ETHA/ETHE → the named spot ETFs, FBTC → Fidelity Wise Origin Bitcoin Fund.

**Why the alarm looked credible, stated plainly:** the Outsider was reasoning from the pack's
false claim that SpaceX is private — **my error**. Given that premise, hard financials under
"the company's own reported financials" *would* have been damning. The premise was wrong, so
the finding dissolves. The audit was still worth running: it converted an assumption into a
measurement across 23 mappings, which is the standing obligation.

**Cosmetic only (no action required):** the `MSTR` comment reads "MicroStrategy"; the company is
now *Strategy Inc*. A stale comment, not a mapping error.

**S0 verdict: CLOSED, no defect. S1 (un-gate + generalise liveness) is now the head of the queue
and remains the one true blocker before `INSIDER_FLOW=1`.**
