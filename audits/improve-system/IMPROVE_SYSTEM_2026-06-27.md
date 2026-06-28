# NowTrendIn — Weekly System-Improvement Audit — 2026-06-27   [INTERNAL]

*First run of `/improve-system`. Read-only / flag-never-force — nothing below was auto-applied.*

---

## 1. Executive summary

The platform is **operationally healthy and foundationally sound**: all services up, 16/17
collectors HEALTHY, **zero committed secrets**, and the two integrity bedrocks hold — the accuracy
ledger is **held-out** (0 ledger references in calibration code) and **N (`nowtrendin_score`) is
excluded from the Gradient Score composite**. No foundational-principle breach was found.

The single most important issue is the **scoring data-contract is in CRITICAL drift** — not from
fabrication or circularity, but from three real data-quality defects introduced/accumulated in the
build: an off-enum `risk_stage` ('MODERATE'), a broken `heisenberg_gap` derived-rule on 10/800 rows,
and a degenerate `nowtrendin_score` (0.0 on 91% of rows). The top **strategic** finding is a **trend
recall gap**: of 19 currently-viral Google Trends, we captured 2 — and both only at theme granularity
(fifa, england), missing all person/event-level virality (Beckham, Bellingham, Djokovic, …).

**Top recommendation:** clear the CRITICAL contract drift (low effort, high trust) and set the 7
untracked paid-API cost lines (we are at **94% of the $700 cap** and true spend may already exceed
it). Both are low-effort, high-integrity wins. Market/crypto 20%-mover validation had **no cases this
week** (a calm week) — reported honestly, with a structural fix proposed.

---

## 2. Current status (the dashboard)

- **Services:** engine `operational` · backend up (HTTP 400 liveness) · web terminal (gh-pages) HTTP 200
- **Collectors:** 16 HEALTHY · 1 DEGRADED (`reddit` — known; keys deferred per nowtrendin2.0 pending actions)
- **Cost:** **$655.44 / $700 (94%, WARN)** — AI $15.36/$20 · Apify $192.09/$250 · Heroku $64 · X $200 · AWS $104 · subscriptions $80. **⚠ 7 paid APIs have untracked cost → true total may exceed $700.**
- **Quarantine (dates):** 0 — clean.
- **Catch-all floor:** `fragment_category_auditor` WARN **76.5%** (vs documented serve-time 56% — needs reconciliation).
- **Date-canon:** WARN — 8 market/crypto ledger `*_date` columns undeclared in gate registry (`non_canonical_total=0` → no corruption, just undeclared).
- **Scoring contract:** **CRITICAL (3 alerts)** — see F1/F2/F9.
- **Trend ledger (emerging cohort):** **1/41 LED = 2.4%** · 871 pending · median lead **11 days**. (Established 0/11, unknown 0/1. Coverage: 3 by topic-maturity + 57 by sustained-days fallback = 59 resolved.)
- **Market ledger:** 0 resolved / 7 pending.  **Crypto ledger:** 0 resolved / 1 pending. (Both new; honest — no rate published yet.)
- **Monitoring agents (`/monitor` run_all):** overall WARN — source/scorer/pipeline OK; fragment-category, cost-sentinel, calibration, data-subscriptions WARN.

---

## 3. Accuracy vs ground truth

### 3a. Viral Google Trends — captured **2 / 19** (LED: 0 confirmed at entity level)
Ground truth: Google daily-trending RSS (US + GB), 19 unique fully-viral terms.

| Viral term (sample) | Our status | Note / root cause |
|---|---|---|
| fifa world cup standings | CAPTURED | matched theme `fifa` (not the specific story) |
| england coach | CAPTURED | matched theme `england` |
| david beckham, jude/­bellingham, john terry, cody gakpo, djokovic, sterling, pascal struijk, anthony barry, ben whittaker | MISSED | **person-level** entity — our extractor surfaces teams/countries/tournaments, not individual people |
| diamondbacks vs rays, rugby nations championship | MISSED | **event/fixture-level** — not indexed at this granularity |
| tom homan, trump patriot passport design | MISSED | person/news-event granularity |
| fireworks, charlotte weather | MISSED | ephemeral local/novelty (likely out-of-scope) |

**Read (fair):** Google daily-trending is dominated by **sports/celebrity/local ephemera**, which is
not the institutional wheelhouse where early lead time has $ value. But the public claim is broad
("where human attention is moving before it arrives"), and at **theme** granularity we cover well
(white house, greece, ukraine, claude code, agi, mcp, fifa) while at **person/event** granularity we
miss almost everything. This is a **recall + granularity gap**, partly a **scope** question (F3).

### 3b. Market 20% movers — **0 movers this week** (0 to validate)
Covered tradeable large-caps checked via FMP (1-week close-to-close): CVX −3.7, WFC +0.1, F +1.2,
IBM +3.5, C −1.4, GOOGL −7.3, NVDA −5.9, LMT −4.7, AMZN −2.0, JPM −1.3, META −3.1, TSLA −4.2. None
≥ ±20%. **Calm week — no validatable case.** (Structural note → F8.)

### 3c. Crypto 20% movers — **0 movers this week** (0 to validate)
12 coins, 7-day change: all between −14.6% (DOT) and +3.0% (AVAX). None ≥ ±20%. Flow direction was
broadly sane (the only up coin, AVAX, was the only `inflow`), but **every coin's Money Movement (D)
= exactly 30.0** → the per-coin proxy Dark-Matter signal is not differentiating (F7).

---

## 4. Eight-lens verdict

- **Engineer** `WATCH` — Services up, collectors healthy, quarantine zero. But the scoring contract is
  CRITICAL (F1/F2) and a CRITICAL status does **not** surface in `/monitor` run_all (F10) — a blind spot.
- **Auditor** `PASS (with drift)` — The fatal checks pass: non-circularity intact (0 ledger refs in
  calibration; N excluded from composite), no committed secrets, ledger held-out. Drift exists in
  derived fields (heisenberg_gap 10/800) and a degenerate N (F9) — quality, not fabrication.
- **Attorney** `PASS` — Disclaimers present on every surface incl. the new crypto Signal-Analysis line;
  language is measurement-not-advice; IP/ownership clause intact; no secret in tracked files. Watch the
  7 untracked paid-data lines for licensing/cost exposure (F4).
- **Banker client** `WATCH` — Denominators are honest (2.4% of 41; "0 resolved" stated plainly). But
  spend is at 94% of cap **with untracked lines** — the headline cost number is not yet trustworthy (F4).
- **Venture capitalist** `WATCH` — The moat (held-out ledger + 11-day median lead on the emerging
  cohort) is real but **early and thin** (1 LED of 41 resolved; 871 pending under the new 365-day
  patience window). The recall gap (F3) caps the addressable "attention" claim. Moat is forming, not proven.
- **Financial advisor** `PASS` — Nothing in any surface reads as a recommendation; flow is labeled a
  fact-from-filings; tiers are descriptive. Compliant.
- **Board confidant** `WATCH` — We are candid and accurate with users (honest denominators, held-out
  ledger). The strategic risk is **claim vs coverage**: a broad "human attention" promise against
  theme-level (not person/event-level) recall. Decide the posture (F3).
- **Fiduciary** `PASS` — No false, inflated, or circular information is reaching users right now. The N
  degeneracy is display-only and non-circular; scores reflect real data or sit at an honest baseline.

---

## 5. Agent productivity

| Agent | Running? | Found this week | Verdict |
|---|---|---|---|
| Source Watchdog | ✓ ok | clean | keep |
| Scorer Watchdog | ✓ ok | clean | keep |
| Pipeline Integrity | ✓ ok | clean | keep |
| Fragment/Category Auditor | ✓ WARN | 76.5% catch-all | keep — **act on F5** |
| Cost Sentinel | ✓ WARN | 94% of cap | keep — **act on F4** (and untracked lines) |
| Calibration Auditor | ✓ WARN | evaluated=0/pending=0 (mismatch vs live ledger 59/871) | keep — **verify wiring (F11)** |
| Data Subscriptions | ✓ WARN | 7 untracked paid APIs | keep — **act on F4** |
| Canonical Date Auditor | ✓ WARN | 8 undeclared ledger date cols | keep — **act on F6** |
| Catch-All Auditor (`/monitor/catchall`) | ✗ 503 standalone | n/a (works inside run_all) | **fix endpoint (F10)** |
| Scoring-Contract monitor | ✓ CRITICAL | 3 contract defects | keep — **not in run_all (F10)** |
| Prewarm Agent | ✓ (crypto/feeds served from cache, fast) | caches hot | keep |

---

## 6. Findings (ranked)

**CRITICAL (monitor-flagged data-contract drift — fix first; not a foundational breach)**
- **F1 · `risk_stage` off-enum.** `risk_scores.risk_stage = 'MODERATE'` is outside the declared enum
  `[ELEVATED, ACTIVE, BUILDING, ROUTINE, DORMANT]`. Introduced by this week's de-Congress
  **BUILDING→MODERATE** reframe; the contract enum wasn't updated. *Evidence:* `/monitor/scoringcontract`.
- **F2 · `heisenberg_gap` derived-rule broken on 10/800 rows.** `heisenberg_gap ≠ detection − confidence`
  on 1.25% of rows — a sink-hardening regression (cf. memory `project-scoring-congruency`: compute at
  the write sink, not the caller). *Evidence:* `/monitor/scoringcontract`.

**HIGH**
- **F3 · Trend recall/granularity gap (strategic).** 2/19 viral terms captured, both theme-level; all
  person/event-level virality missed. Decide: broaden recall (person-entity extraction + a realtime
  event/sports source) **or** explicitly scope the public "before it arrives" claim to institutional
  themes. *Evidence:* §3a. *(Score-affecting if extraction changes → backtest-before-ship.)*
- **F4 · Cost integrity at 94% with untracked spend.** $655/$700 **and** 7 paid APIs have no
  `COST_*_USD` set → true total may already exceed the cap. *Evidence:* `/monitor/cost`, `/monitor/subscriptions`.

**MEDIUM**
- **F5 · Catch-all 76.5% vs documented 56%; visible miscategorization.** Raw catch-all reads 76.5%;
  serve-time `_category_for` is documented at 56% — reconcile (is the drain/background-refresh live?).
  Also clear mislabels seen in `/scores`: texas→religion, egypt→sports, "new yorkers"→sports, plus
  fragments ("yorkers", "estados unidos"). *Evidence:* `/monitor` run_all + `/scores` sample.
- **F6 · 8 ledger date columns undeclared (§14).** market/crypto `*_date` columns not in the gate
  registry (no corruption — `non_canonical_total=0`). Classify (gate_date + DATE_SEMANTIC) or allowlist
  as operational. *Evidence:* `/monitor/datecanon`.
- **F7 · Crypto Money Movement flat at 30.0 across all 12 coins.** The per-coin proxy Dark-Matter read
  carries no per-coin information right now (likely the FAST Finviz-only DM serving a flat baseline).
  *Evidence:* `/crypto`. *(Score-affecting → backtest.)*
- **F8 · Market universe composition limits 20%-mover validation.** Large-caps (rarely ±20%/wk) +
  halted microcaps at the 30.0 "insufficient data" floor (no positioning). The 20%-mover audit will
  seldom have a validatable case. Consider mid-cap coverage where 20% moves and positioning coexist;
  meanwhile lean on the EOD-direction market ledger. *Evidence:* `/risk/scores`.

**LOW / WATCH**
- **F9 · N degenerate (0.0 on 91%).** Non-circular + display-only → no score risk, but "Platform
  Indicator" shows 0 for most topics. Confirm legit (most topics unqueried) vs a wiring misread.
- **F10 · Monitoring blind spot.** `/monitor/catchall` 503 standalone; scoring-contract CRITICAL does
  not appear in `/monitor` run_all. Fold a contract-status line into run_all; fix the catchall route.
- **F11 · Calibration Auditor wiring.** Reports evaluated=0/pending=0 while the live trend ledger has
  59 resolved / 871 pending — verify it reads the live ledger.
- **F12 · X cost line stale.** Still flat $200 "configured" though X migrated to pay-per-use 2026-06-21.
  Update `COST_X_API_USD` to the pay-per-use baseline.
- Reddit collector DEGRADED — known (keys deferred).

---

## 7. Recommendations (ranked by impact × effort)

1. **Clear the CRITICAL contract drift (high impact · low effort).** Add `MODERATE` to the `risk_stage`
   enum (realias/retire `BUILDING`); re-harden the `heisenberg_gap` write-sink and backfill the 10 rows.
   Restores a clean contract. *Verify-before-ship (not a score change).*
2. **Make the cost number trustworthy (high · low).** Set `COST_*_USD` for the 7 untracked paid APIs;
   then reassess Apify/X optimization. We are at 94% — this is a fiduciary/banker priority.
3. **Decide the trend-recall posture (highest strategic · med-high).** Add person-level entity
   extraction + a realtime event source to broaden recall, **or** scope the public claim to
   institutional themes. *Score-affecting → backtest-before-ship.*
4. **Reconcile catch-all 76.5% vs 56% + fix miscategorizations (med · low).**
5. **Declare the 8 ledger date columns in the gate registry (med · low).** §14 compliance for the newer ledgers.
6. **Differentiate crypto Money Movement per coin (med · med).** The flat 30.0 makes the per-coin D read
   uninformative. *Score-affecting → backtest.*
7. **Close the monitoring blind spots (low · low).** Fold contract status into run_all; fix `/monitor/catchall`;
   verify Calibration-Auditor ledger wiring; update the X pay-per-use cost line.

> Nothing here is auto-applied. Each is a separate, human-confirmed task (Principle 5). The score-affecting
> items (F3, F7) additionally require backtest-before-ship.

---

## 8. Context delta + stale docs

- **This session's shipped work** (reflected live): crypto loading fix; crypto AI interpretation walk;
  DIRECTION filter row (Market + Crypto); crypto Signal-Analysis disclaimer line; the `/improve-system`
  skill itself + its weekly schedule (Sat 06:01 EST).
- **Stale-doc flags (do NOT edit here — confirm separately):**
  - `CLAUDE.md` §13 states the catch-all drained to **56%**; the live auditor reads **76.5%**. Reconcile
    the doc + the serve-time drain (F5).
  - The scoring-contract enum for `risk_stage` predates the BUILDING→MODERATE reframe (F1) — update
    wherever the enum is declared.
  - `nowtrendin2.0` skill "CURRENT BUILD STATE" is current as of 2026-06-26; add the 2026-06-27 items
    (DIRECTION filter, crypto disclaimer, improve-system skill) on the next doc pass.
- No prior weekly report (this is run #1) — future runs will diff against this file.

---
*Generated by `/improve-system` (read-only). Foundational integrity verified: ledger held-out,
N excluded from composite, no committed secrets. Internal document — keep formulas confidential if shared.*
