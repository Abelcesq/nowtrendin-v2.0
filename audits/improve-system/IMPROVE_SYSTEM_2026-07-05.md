# NowTrendIn — Weekly System-Improvement Audit — 2026-07-05   [INTERNAL]

*Run #3 (weekly). Read-only. Nothing in this report was auto-applied. Engine time at pull: 2026-07-05T22:08Z.*

## 1. Executive summary

The platform is **operationally healthy and structurally honest** — all services up, non-circularity
intact (0 ledger refs in calibration code, N excluded from the composite), no committed secrets, every
ledger held-out with denominator-backed rates. **No CRITICAL findings.** But three things are drifting
the wrong way week-over-week and one new degeneracy surfaced:

1. **Cost is at 96% of the $700 cap ($670.26)** — up from 94% last week; **Apify at 89%** ($221 of
   $250). We will breach the cap within days at this run-rate. This is the single most urgent finding.
2. **The Money Gradient is barely differentiating.** In crypto, **all 12 coins** report identical
   `money_movement=30.0` and `flow=inflow`; in risk, **133 of 274 instruments** are pinned at the exact
   30.0 cold-start floor. A uniform "everything is inflowing" read is a number we cannot defend
   (Principle 1) and a hedge-fund client would distrust on sight.
3. **Catch-all regressed to 80.5%** (76.5% last week, documented target 56%) — the 2026-06-30 lexicon
   commit did **not** reduce it — **and the `/monitor/catchall` endpoint that should alarm on this is
   down** (persistent Heroku application error), so the WORSENING trip-wire (§13) isn't firing.

**Top recommendation:** cut Apify run-rate this week (the cap's largest live lever) and open a
backtest-gated investigation into the 30.0-floor degeneracy in the market/crypto Money Gradient — per
§17, floor-pinned instruments with no positioning coverage should be **omitted**, not shown as a
neutral "ROUTINE" read that implies coverage we don't have.

## 2. Current status (the dashboard)

- **Services:** UP (`/health` operational). **Collectors:** **15 HEALTHY / 2 DEGRADED / 0 stale / 0 down.**
  Degraded: `github` (**critical collector**, ran 163m ago, 0 signals) and `reddit` (0 signals, non-critical).
- **Cost:** **$670.26 / $700 (96%, WARN — near breach).** AI $0.92 · **Apify $221.34/$250 (89%, WARN)** ·
  Heroku $64 · X Developer API $200 · AWS $104 · Data subscriptions $80 · Firecrawl 0/500 credits.
- **Quarantine:** **0** (clean). **Date-canon:** WARN — 8 market/crypto ledger `*_date` cols undeclared;
  13 `timeout_date` values non-canonical (full timestamp, not ISO date). No corruption in declared cols.
- **Catch-all floor:** **80.5% WARN** (fragment_category_auditor). `/monitor/catchall` endpoint **DOWN**.
- **Scoring contract:** WARN — `velocity_scores.nowtrendin_score` **degenerate: 0.0 on 90% of 800 rows.**
  0 value-violations, 0 derived-mismatches, 0 unregistered columns otherwise.
- **Trend ledger (held-out):** overall **7 LED / 70 resolved (10%)**, **817 pending**, median lead 11d.
  Emerging cohort (the honest early-detection claim): **1 LED / 44 resolved = 2.3%**, median lead 16d.
  Established 6/25 = 24%.
- **Market ledger:** **3 confirmed / 5 resolved (60%)**, 7 pending, median lead **4d**, inflow 3/3, outflow 0/2. *(healthiest ledger)*
- **Crypto ledger:** **0 resolved / 1 pending** (empty — no rate published; honest).

## 3. Accuracy vs ground truth

### 3a. Viral Google Trends — captured the theme, missed the entities

Ground truth: Google daily-trending RSS (US + GB), 2026-07-05. The week's viral set was **heavily World
Cup 2026-dominated** (golden boot race, Haaland goals, FIFA ranking, world-cup winners, goleadores;
plus Manchester United, Rodrygo, Ederson, and celebrity names Harrison Ford / Tobey Maguire).

| Viral term (Google) | Our status | Note / root cause |
|---|---|---|
| world cup / world cup winners / fifa ranking | **COINCIDENT** | `world_cup`, `world_cup_2026`, `fifa`, `fifa_world_cup` all scored (broad theme captured) |
| golden boot race / golden boot | **MISSED** | sub-query granularity — we hold the event, not the stat query |
| haaland goals in world cup | **MISSED** | entity resolution — no `haaland`; we have teams/countries, not top scorers |
| manchester united / rodrygo / ederson | **MISSED** | player/club entities not extracted (we have `michael_olise`, `folarin_balogun` only) |
| mexico city weather | **MISSED** | micro weather query — out of scope |
| china | **COINCIDENT** | `china` scored |
| harrison ford / tobey maguire | **MISSED** | celebrity-name virals not in pipeline |
| nottingham maternity (GB) | **COINCIDENT** | `maternity` scored |

**Capture (theme-level): ~4 of ~12 viral clusters. LED: 0 confirmed at entity level this week.** The
pattern is unchanged from last week and is the platform's #1 strategic gap: **we capture the broad
event but miss the specific viral entities/sub-queries** (players, clubs, celebrities, stat queries).
World Cup is an ESTABLISHED topic (discounted), which further suppresses its rank. Held-out emerging
cohort LED rate **2.3% (1/44)** corroborates: honest early-detection is real but thin.

### 3b. Market 20% movers — 4 covered movers, all MISSED (known coverage gap)

Checked 20 covered instruments via FMP (`/stable/historical-price-eod/light`, window 2026-06-25→07-05).
No large-cap moved ≥20% (max AAPL +12.2%). Four **covered microcaps** cleared ±20%:

| Ticker | Weekly % | Our read | Status | Root cause |
|---|---|---|---|---|
| FCUV | **−26.1%** | det 30.0 (floor), flow neutral | **MISSED** | microcap, no 13F/insider Dark Matter |
| LICN | **−26.9%** | det 30.0 (floor), flow neutral | **MISSED** | ” |
| PLSM | **−23.1%** | det 30.0 (floor), flow neutral | **MISSED** | ” |
| DSC | **−23.1%** | det 30.0 (floor), flow neutral | **MISSED** | ” |

All four are floor-pinned microcaps in the halt/microcap lane with **no informed-money coverage** — a
**known Dark-Matter gap**, not a model failure. The concern is §17: rendering them as `ROUTINE / neutral`
implies we assessed them when we have no positioning data. The differentiated large caps (Ford −5.3%,
Tesla +4.9% inflow, Apple +12.2% outflow, Lockheed +8.1%) all stayed sub-20%, so **no LED win to claim
this week** on the covered side.

### 3c. Crypto 20% movers — signal undifferentiated

`/crypto` (prewarm cache). Two coins cleared ±20% over 7d:

| Coin | 7d % | money_movement | flow | market_confirmation | Status |
|---|---|---|---|---|---|
| ADA | **+31.6%** | 30.0 | inflow | 47.1 | COINCIDENT (direction right, undifferentiated) |
| BCH | **+30.1%** | 30.0 | inflow | 54.0 | COINCIDENT (direction right, undifferentiated) |

Flow direction (inflow → price rose) was **directionally correct**, but **all 12 coins share the
identical `money_movement=30.0` and `flow=inflow`** — the signal does not separate ADA/BCH from BTC or
DOT. The crypto ledger is empty (0 resolved), so no rate is over-claimed (honest). A miss here would be
the **known on-chain gap** (Dark Matter is proxy-based: spot-ETF 13F + MSTR/COIN insider, not wallet
flow) — but the flat 30.0 across the board is a **degeneracy**, not merely a coverage gap.

## 4. Eight-lens verdict

- **Engineer** `WARN` — All services up, but a **critical collector (github) is degraded** at 0 signals,
  a monitoring endpoint (`/monitor/catchall`) is **down**, and the Money Gradient shows a **30.0-floor
  degeneracy** across 133/274 risk instruments and all 12 coins. Maintainable, but three components need
  attention. *Evidence:* `/health/collectors`, `/monitor/catchall` (app-error), `/risk/scores`, `/crypto`.
- **Auditor** `PASS (with drift)` — The fatal checks pass: **non-circularity intact** (0
  `accuracy_ledger`/`hit_rate`/`breakout_date` refs in `calibration_engine.py` /
  `signal_calibration_integration.py`; `nowtrendin_score` present only as a stored output field), **no
  committed secrets** (week's diffs contain only UI "token" labels), **ledgers held-out**, denominators
  honest. Drift: degenerate N (0.0 on 90%), 13 non-canonical ledger `timeout_date` values. Quality, not
  fabrication. *Evidence:* `/monitor/scoringcontract`, `git log -p` scan, grep of calibration files.
- **Attorney** `PASS` — Crypto panel carries the "may be inaccurate / not advice" disclaimer (shipped
  cf50088); no advice-like language on any surface; IP/ownership clause intact; no secret committed. One
  watch: floor-pinned microcap reads (§17) could be read as an assessment we didn't make — a
  presentation-integrity issue, not a legal one yet.
- **Banker client** `WARN` — I would trust the **market ledger** number (3/5 confirmed, inflow 3/3,
  4-day lead, labeled small-sample) in a deck. I would **not** put the crypto panel in front of a
  client while all 12 coins read identical inflow. And **spend at 96% of cap** with Apify at 89% is a
  governance flag. *Evidence:* `/monitor/cost`, `/crypto`.
- **Venture capitalist** `WATCH` — The moat (held-out ledger + measured lead time) is **real but early
  and thin**: 1 LED of 44 in the emerging cohort, 817 pending under the 365-day patience window. The
  market ledger gaining its first resolutions (0/7 → 3/5) is genuine week-over-week progress. Lead time
  must **grow**; entity-resolution is the lever.
- **Financial advisor** `PASS` — Nothing reads as a recommendation. Flow is labeled a measurement;
  "NOT a forecast, NOT advice, NOT a buy/sell signal" is on the ledger surfaces.
- **Board confidant** `WATCH` — We remain candid and non-circular. Top strategic risk is **claim vs
  coverage**: a broad "where human attention is moving" promise against a pipeline that captures the
  World Cup but not Haaland or Manchester United, and a Money Gradient that reads a flat floor on most
  instruments. Second: cost governance (96%).
- **Fiduciary** `PASS (with one watch)` — No false, inflated, or circular number reaches a user via a
  score: N is display-only/non-circular, ledgers are held-out and honestly denominated. The **watch** is
  the uniform crypto inflow + floor-pinned microcap reads — presentationally they imply differentiation
  and coverage that isn't there. Fix by omission (§17), not by inventing a number.

## 5. Agent productivity

| Agent | Running? | Last run | Found this week | Verdict |
|---|---|---|---|---|
| Source Watchdog | ✓ warn | 22:08Z | github DEGRADED (critical, 0 signals) | keep — **act (F4)** |
| Scorer Watchdog | ✓ ok | 22:08Z | heartbeat 150m, no failover issue | keep |
| Pipeline Integrity | ✓ ok | 22:08Z | 0 junk-single, 0 dupes, 0 stale-payload | keep — earning its keep |
| Fragment/Category (Quality) | ✓ warn | 22:19Z | **80.5% catch-all** (regressed) | keep — **act (F3)** |
| Cost Sentinel | ✓ warn | 22:08Z | **$670/96%, Apify 89%** | keep — **act (F1)** |
| Calibration Auditor | ✓ warn | 22:08Z | **evaluated=0/pending=0** vs live ledger 70/817 | keep — **fix wiring (F6)** |
| Data Subscriptions | ✓ ok | 22:08Z | 10 paid / 10 free / 5 metered, 0 untracked | keep — clean this week |
| Canonical Date Auditor | ✓ warn | 22:08Z | 8 undeclared ledger date cols, 13 non-canonical | keep — **act (F7)** |
| Catch-All Auditor (`/monitor/catchall`) | ✗ **DOWN** | app-error | floor-trend monitor unavailable | **fix endpoint (F3)** |
| Prewarm (operational) | ✓ (implied) | — | crypto served from cache OK | keep |

## 6. Findings (ranked)

- **F1 · HIGH — Cost at 96% of the $700 cap ($670.26); Apify 89% ($221/$250).** Up from 94%/77% last
  week. At this run-rate the cap breaches within days. *Principle: cost discipline / banker + board lens.*
  Apify is the largest live lever; the X Developer API ($200) is the largest fixed line — assess its
  signal contribution. *Evidence:* `/monitor/cost`.
- **F2 · HIGH — Money Gradient degeneracy (30.0 floor).** All 12 crypto coins report identical
  `money_movement=30.0` + `flow=inflow`; 133/274 risk instruments pinned at exactly 30.0. A uniform read
  we cannot defend (Principle 1) and that implies coverage/differentiation that isn't there (Principle 3,
  §17). *Evidence:* `/crypto`, `/risk/scores` histogram.
- **F3 · HIGH — Catch-all regressed to 80.5% AND its monitor is down.** 76.5%→80.5% week-over-week; the
  2026-06-30 lexicon commit did not reduce it; documented serve-time target is 56%. `/monitor/catchall`
  (the WORSENING trip-wire, §13) returns a Heroku application error, so the alarm can't fire. *Evidence:*
  `/monitor/quality`, `/monitor/catchall`.
- **F4 · MEDIUM — github (critical collector) DEGRADED, reddit degraded.** Both ran but returned 0
  signals (163m). github is `critical:true`; a sustained 0-signal state risks a coverage hole in the
  attention pipeline. *Evidence:* `/health/collectors`.
- **F5 · MEDIUM — N (`nowtrendin_score`) degenerate: 0.0 on 90% of 800 rows** *(repeat of last week's
  F9, unactioned).* Non-circular and display-only → **no score risk**, but the "Now TrendIn" ranking
  view (ranks by N) is effectively broken/flat. *Evidence:* `/monitor/scoringcontract`.
- **F6 · MEDIUM — Calibration Auditor reports 0 evaluated / 0 pending** while the live ledger holds
  **70 resolved / 817 pending** *(repeat, unactioned).* The agent isn't seeing the ledger — a query/table
  mismatch. Conservative (won't over-publish) but the agent isn't earning its keep. *Evidence:* `/monitor`
  vs `/accuracy/ledger`.
- **F7 · MEDIUM — 8 market/crypto ledger `*_date` columns undeclared in the gate registry; 13
  `timeout_date` values non-canonical** (full timestamp `2026-08-24T00:00:00+00:00` vs ISO `YYYY-MM-DD`)
  *(repeat of F6 last week).* Held-out ledger cols → no score impact, but a §14 compliance gap; classify
  (gate + add to DATE_SEMANTIC) or allowlist as operational. *Evidence:* `/monitor/datecanon`.
- **F8 · MEDIUM (strategic) — Entity-resolution / viral sub-query recall gap.** We capture the World Cup
  theme but miss Haaland, Manchester United, golden boot, celebrity virals. This caps LED rate. *Evidence:*
  Phase 2 table; emerging cohort 2.3% LED.
- **F9 · LOW — 4 covered microcaps moved ±20% (FCUV/LICN/PLSM/DSC), all MISSED.** Known Dark-Matter
  microcap coverage gap; the fix is §17 omission of no-coverage floor-pinned instruments, not a new source.
- **F10 · WATCH — Stale docs.** `nowtrendin2.0` skill's CURRENT BUILD STATE (dated 2026-06-26) is
  internally contradictory: it lists the 365-day patience window as LIVE (line ~159) **and** as "PENDING
  USER CONFIRMATION — do NOT implement" (line ~544), though it shipped 2026-06-27. CLAUDE.md footer's
  catch-all "77%→56%" figure no longer holds (live 80.5%). Flag only — do not edit here.

## 7. Recommendations (ranked by impact × effort)

1. **Cut Apify run-rate this week (F1).** *Impact: high (only fast lever on the cap) · Effort: low.*
   Verify only one Google-Trends actor is firing (the realtime 2× overrun was supposedly fixed — confirm
   from `/usage` `apify_realtime` vs `apify_trends` cadence), and consider lowering realtime/sweep
   frequency. Separately, decide whether the **X API $200 line** earns its signal. Owner: founder/eng.
2. **Open a backtest-gated investigation into the 30.0-floor degeneracy (F2).** *Impact: high · Effort:
   medium.* Determine whether the market/crypto baseline cold-start is defaulting to a uniform floor. Per
   §17, **omit** floor-pinned instruments with no positioning coverage rather than rendering `ROUTINE /
   neutral`. **Requires backtest-before-ship** (touches the market/crypto score surface). Owner: eng.
3. **Fix `/monitor/catchall` and re-examine the catch-all drain (F3).** *Impact: high · Effort: medium.*
   Restore the endpoint so the WORSENING trip-wire works, then diagnose why the drain reversed (80.5% vs
   56% target) despite the 2026-06-30 lexicon add — is the background-refresh/`_category_for` layering
   live? Owner: eng.
4. **Restore github + reddit collectors (F4).** *Impact: medium · Effort: low.* Check credentials/rate
   limits; github is critical. Owner: eng.
5. **Fix Calibration Auditor wiring (F6).** *Impact: medium · Effort: low.* Point it at the live ledger
   table so 0/0 stops masking 70/817. Owner: eng.
6. **Declare/allowlist the 8 ledger date columns + canonicalize `timeout_date` (F7).** *Impact: low ·
   Effort: low.* Owner: eng.
7. **Entity-resolution / viral sub-query capture (F8).** *Impact: high (this is the lead-time lever) ·
   Effort: high.* Add sub-entity extraction (players/clubs/people/stat-queries) so we surface Haaland, not
   just World Cup. The largest driver of a higher LED rate. **Requires backtest-before-ship.** Owner: eng.

*Nothing above is auto-applied (Principle 5). Each score-affecting item is marked backtest-before-ship.*

## 8. Context delta + stale docs

**Week-over-week (2026-06-27 → 2026-07-05):**
- Cost **$655→$670** (94%→96%); Apify **$192→$221** (77%→89%) — both **worse**.
- Catch-all **76.5%→80.5%** — **worse** (lexicon commit 520d0e9 did not help).
- Collectors **16H/1D → 15H/2D** — github newly degraded (critical) — **worse**.
- Market ledger **0/7 → 3/5 confirmed (60%)** — **better** (first resolutions, 4-day lead).
- Trend emerging LED **1/41 (2.4%) → 1/44 (2.3%)**; pending 871→817; N degenerate 91%→90% (steady).
- Crypto ledger 0/1 → 0/1 (steady, empty).
- **New this week:** the 30.0-floor degeneracy explicitly quantified across risk + crypto (F2).
- **Unactioned repeats from last week:** F5 (N degenerate), F6 (calibration wiring), F7 (ledger date
  cols), catch-all reconciliation, `/monitor/catchall` down — all persist.

**Stale docs (flag only):**
- `nowtrendin2.0` skill CURRENT BUILD STATE (2026-06-26) — contradictory on the 365-day patience window
  (listed both LIVE and "pending confirmation"); the shipped state is LIVE. Needs a refresh pass.
- CLAUDE.md footer catch-all "77%→56%" drain figure — live is 80.5%; the claim no longer holds.

*— End of audit. Read-only run; no scores, weights, calibration, or ledgers were modified.*
