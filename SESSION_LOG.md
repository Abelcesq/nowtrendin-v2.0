# NowTrendIn 2.0 — Session Log

A running, readable catch-up of what's been built and what's open — so any new
Claude Code session (or you on your phone) can resume without the local thread.

_Last updated: 2026-06-26 (evening)_

---

## Session 2026-06-26 (evening) — Signal Analysis · accuracy-ledger backlog + maturity · Apify audit + token rotation

- **Signal Analysis (per-item, enterprise-grade) — LIVE on web, shipped on mobile.** New held-out
  `signal_analysis.py` (imported by NOTHING in scoring): a REPRODUCIBLE, formula-confidential,
  measurement-only narrative per item — explains each metric conceptually + analyzes the finding from real
  scores + the accuracy-ledger track record (honest denominators), for trend / market / crypto. Engine:
  `POST /analysis/{kind}`. Web terminal: a "Signal Analysis" section in the trend/market/crypto rails
  (live, gh-pages). Mobile: trend (`signal/[id]`) + market (`risk/[key]`) screens (crypto N/A — no mobile
  crypto screen). Desktop inherits via the shared web build. Founder standard saved
  (`feedback-enterprise-analysis-standard`): explain metrics, hide the formula, every claim data-supported +
  defensible to hedge-fund counsel.
- **Accuracy-ledger backlog root-caused + the moat made honest.** The 909-pending / 2.1% *blended* rate is an
  ARTIFACT, not the product: (1) throughput starvation, (2) resolution survivorship bias (LAGGED resolves
  instantly; LED waits for a future breakout → stuck pending), (3) denominator pollution by ESTABLISHED topics
  (world cup etc. can only LAG). VERIFIED the ledger is **held-out** — `calibration_engine` /
  `signal_calibration_integration` have ZERO ledger refs; `calibration_agent` is read-only → the sweep cap
  **never touched a score**.
- **Maturity segmentation (held-out, display-only).** `generate_honest_report` segments resolved rows by
  `topic_maturity.maturity_class`, with a well-covered fallback to `velocity_scores` SUSTAINED-DAYS (distinct
  days scored ≥ `LEDGER_ESTABLISHED_MIN_DAYS`=14 → established). Headline = the EMERGING early-detection cohort;
  established/unknown reported too (nothing hidden). Exposed via `/accuracy/ledger` (`byMaturity`,
  `earlyDetectionHitRate`). Live: emerging 37 resolved · 1 led · 2.7% · 11d median lead (still early/maturing —
  the "don't publish a rate yet" guardrail stands).
- **Sweep runaway (caught + fixed).** Uncapping the sweep (8→300) + a one-off drain stampeded Apify — the
  Google-Trends-Scraper actor is SLOW + compute-heavy per topic (1–11 min/run, some fail); the earlier
  "$0.001/result cheap" read was WRONG (cost is per-run COMPUTE). Throttled to **`LEDGER_SWEEP_LIMIT=8`**
  (code default reverted 300→8 — footgun removed), added `_apify_sweep_budget_ok` guard (skips paid fetches
  within `LEDGER_APIFY_RESERVE_USD`=40 of the Apify cap so the sweep can't starve collection) + a manual
  `POST /accuracy/ledger/sweep`.
- **Apify usage audit.** CONFIRMED Apify pulls ONLY trend/attention — Google Trends realtime discovery
  (`easyapi/...`) + Google Trends curves (ledger sweep) + Reddit. Crypto + financial have ZERO Apify refs
  (FMP / Finviz / AV / FINRA / OFR / Databento). Found a realtime 2× overrun (the actor fires :00 AND :30 =
  8×/day vs the engine's single :30 cron) — likely a 2nd process on the old token; expected to resolve now the
  old key is deleted (confirm at the next 6h slot).
- **Apify token rotated** (old leaked in a tool output → rotated → old deleted; new set on engine v187,
  authenticating). Confirmed **NON-EXPIRING** (2026-06-26) — trend discovery + the ledger sweep are safe.
- **Cost Sentinel $700/mo total cap** (critical if exceeded, warn at 80%).
- **Accuracy-ledger PATIENCE WINDOW (365d) — founder decision.** The product detects dark matter BEFORE
  it reaches Google, and human attention can arrive MONTHS later — so judging a detection a miss at 90
  days unfairly condemns our own system before confirmation can arrive ("the big money is in the
  waiting" — Munger; refs reviewed). `accuracy_ledger_enhanced`: (1) timeout 90→365, computed LIVE from
  detection so it applies to the existing ~881 pending; (2) ASYMMETRIC lead window — backward stale-floor
  stays tight (30d, the −92d artifact), FORWARD lead up to 365d now counts as a genuine LED win (was
  wrongly excluded as LATE_REDETECTION); (3) dynamic curve length spans detection→now so a months-later
  breakout is visible. Held-out (no score impact); `param_version=calib-params-v2-patience365`. Documented
  in CLAUDE.md §14. Backlog insight: the 881 pending is a ROLLING working set — rows resolve at a Google
  breakout (trickle) or the (now 365-day) timeout; it self-resolves, it is NOT a throughput problem.

---

## Session 2026-06-26 — Finviz primary insider · Market-Signal "insider" reframe · Mainstream v2 · Crypto Money Gradient

Large multi-thread session; all shipped, health check clean at close.

- **Mainstream v2 (`MAINSTREAM_V2=1`, LIVE).** A few credible outlets were prematurely flipping a topic to
  "mainstream" and suppressing the early read. `dual_pathway.py`: credible media is a Dark-Matter TRIGGER until
  **≥5 INDEPENDENT outlets** corroborate or magnitude spikes. Syndication-collapse:
  `n_news_independent = min(distinct outlets, distinct normalized titles)` — defeats BOTH wire-syndication AND
  single-outlet spam. FIFA-validated (held-out `/research/mainstream-v2`): "world cup" stays mainstream (134
  outlets); thin "mexico world cup" (5→4 stories) demotes to a dark-matter trigger (det 38.5→70).
- **Finviz Elite — PRIMARY insider ($30/mo).** `finviz_data.py`: uncapped market-wide SEC Form-4 feed +
  per-ticker insider + screener. Primary via `av_dark_positioning._best_insider` (`FINVIZ_INSIDER=1`, AV→fallback).
  **INTEGRITY FIX (backtest-caught):** raw insider NET is degenerate (15/15 basket "outflow" — insiders structurally
  sell). The signal is insider **BUYING** (`signal=='accumulation'`, ≥$250K); routine selling = neutral, not bearish.
  Source hierarchy: Finviz #1 insider+equity-market · Databento #1 price-truth+microstructure · AV fallback/13F ·
  FMP crypto+deep-fundamentals. Finviz crypto is display-only.
- **Market Signal de-Congress → "insider" (all platforms).** Reworded `_market_analysis` + `ai_grade` prompt +
  `_interpret_movement` + explainer + Methodology. Labels: "Positioning Concentration" → **Insider Tracking**;
  "Dark Positioning" (macro OFR funding) → **Macro Positioning** (kept accurate — NOT insider); Diffusion stage →
  Insider Tracking. Tier **"BUILDING" → "MODERATE"** (engine + every frontend color/filter/legend). SOURCES (§17):
  added the score-driving FINRA/OFR/FMP/13F that `source_provenance` (signals-only) omitted. Congress DATA (Quiver)
  is still a D input — only the DISPLAY drops the name.
- **Crypto Money Gradient — LIVE (`CRYPTO_SIGNAL=1`).** Coin-native Money Gradient: D = informed money via
  crypto-EXPOSURE proxies (spot-ETF 13F + MSTR/COIN insider via Finviz; no on-chain — proxy v1); M = FMP coin price.
  12 coins. `crypto_signals.py` + `crypto_money_gradient.py` (baseline-relative dual score, reuses
  market_signal_engine store under `crypto:BTC`) + `/crypto[/{coin}]`. Web: master/detail `/crypto` page +
  CryptoRail (mirrors the stock detail) + nav (under Market Signal, above Grade) + **Dashboard tile**. **P3 —
  `crypto_accuracy_ledger.py`**: realized COIN price direction, 8%/45d, no-lookahead — the 3rd distinct ledger +
  "Crypto · Coin" toggle. **Perf gotchas:** /crypto MUST serve from the PREWARM cache (`crypto_full`); live roster
  uses FAST Finviz-only DM (`CRYPTO_FULL_DM=0`) — AV 13F's 13s/call throttle hung the page; roster now ~10s.
- **FMP upgrade** to $20 Starter (300/min, crypto+forex) → crypto prices reliable (free-tier 429s gone).
- **Health check + docs (this entry).** Services up; the only warns were Data Subscriptions + Cost Sentinel not
  accounting for the new sources — FIXED (registered Finviz/Quiver/FMP/Databento/AV-research; set
  `COST_FINVIZ_USD=30`/`COST_QUIVER_USD=30`/`COST_FMP_USD=20`). Quarantine 0; ledgers forward-only (no lost data);
  catch-all STABLE (no leak). Updated CLAUDE.md §15+footer, DATA_BUILDING_BLOCKS §1/§5, this log, `/nowtrendin2.0`.

---

## Session 2026-06-25c — market-data sources: Databento (live) + Alpha Vantage Dark-Matter (held-out)

Researched two founder-provided sources via §16; both keys stored as Heroku env (rotate if transcript shared).

- **Databento — LIVE (accuracy-ledger price verification).** Exchange-direct market data; §16-cleared as a
  REFEREE (referee, never feeds a score → no backtest gate). `databento_price.historical_close()` (EQUS.SUMMARY
  ohlcv-1d, adapter: ns ts→ISO date, 1e-9 fixed-point→float) = same `{date: close}` interface as FMP.
  `market_accuracy_ledger._price_fetch`: **Databento PRIMARY** (no rate cap, ~free) + **FMP cross-check/fallback**
  (`_cross_check` logs >1% divergence). Tested: databento==FMP closes agree EXACTLY (294.3=294.3). `DATABENTO_API_KEY`
  set; deployed.
- **Alpha Vantage Dark-Matter — HELD-OUT (`av_dark_positioning.py`, imported by NOTHING in scoring).** AV uniquely
  provides what Databento canNOT: **insider Form-4** (INSIDER_TRANSACTIONS) + **institutional 13F by ticker**
  (INSTITUTIONAL_HOLDINGS, with change direction). Filters ≥$250K + net direction. Live research: AAPL insider
  −$152M/18 sells (outflow) + institutional net +1.55B shares (inflow) → combined "mixed". Reads
  `ALPHAVANTAGE_RESEARCH_KEY` (new key; production `ALPHAVANTAGE_API_KEY`/NEWS_SENTIMENT untouched). **NOT in any
  score yet** — research → backtest-before-ship → then integrate into `positioning_intel` (alongside congress + 13F).
  Free tier = 5/min · 25/day · ≤1/sec → built-in 13s throttle; production at scale needs caching or premium.
- **Cost/decision:** KEEP both — complementary. Databento = prices/microstructure only (no filings/news);
  Alpha Vantage uniquely = insider/13F/news. Don't cancel AV. Databento ~free for the ledger. Databento microstructure
  (block trades / dark-pool / order imbalance) is a viable **phase-2** Dark-Matter angle (own research+backtest).

---

## Session 2026-06-25b — N component accuracy fix (platform tracking, NOT user demand)

Founder flagged the N-component copy as inaccurate ("how often Now TrendIn users asked the engine
about this topic"). **Verified in the engine:** N (`nowtrendin_score`) is computed purely from
`topic_queries`, and `_log_topic_query` fires **every time a topic is SURFACED in an API result**
(the `/scores` feed, `/anomalies`, `/trending`), an on-demand `/scores/{topic}` query, or a grade.
So N = platform-tracking / appearance frequency — NOT a user-demand claim. Founder was right.

Corrected consistently across all 3 platforms + the engine source comments:
- **"Community Demand" → "Platform Indicator"**; "Now TrendIn user demand" → "Now TrendIn platform
  tracking" (web Screener breakdown + its bar-color key).
- N description (Screener, mobile signal detail, Grade, both Methodology pages, GradeTool): "how often
  users asked / institutional curiosity" → "how often this topic is triggered + surfaced as a tracked
  topic across the platform (feeds, queries, grades) — a platform-internal read no public source has."
- "DEMAND-INCLUSIVE" → "N-INCLUSIVE"; demand-driven warnings + empty states reworded.
- Engine (comment/docstring only, zero runtime change — lands next engine deploy): `compute_nowtrendin_score`
  docstring + `velocity_scores`/`topic_queries` DDL comments.
- Unchanged: N stays a SEPARATE signal, DELIBERATELY EXCLUDED from the Gradient (no feedback loop).
- Web → gh-pages (`00ed5c1`); mobile on Metro reload; desktop inherits. Build + tsc clean.

---

## Session 2026-06-25a — Market Signal v2.0 LIVE: market-ledger view, parity, validated + flag flipped ON

Completed the founder's "proceed with 1-3" (validate / market-ledger view / parity), in the order
2→3→1 so the flip exercised the whole surface.

- **Item 2 — market-ledger view (the visible "two ledgers" proof):** engine `market_accuracy_ledger.detail()`
  + `GET /market/accuracy/detail`; web terminal **Accuracy Ledger** gained an **Attention / Money** toggle
  (Money mode = distinct-ground-truth banner, money stat strip, per-detection table); mobile
  `profile/accuracy` got the same toggle. Added a `pending` (in-flight) count to `/market/accuracy`.
- **Item 3 — parity:** Dashboard `MKT_RANK` label Detection→Money Movement; Methodology gained
  "The Money Gradient" + a reworked "The Accuracy Ledgers" (two ledgers, two ground truths).
- **Item 1 — VALIDATED + FLAG FLIPPED ON (`MARKET_SIGNAL_V2=1`, engine v155):** forced a
  `/risk/collect` (collect + `score_all_risks`) under the flag; at t=180s, **8/8 rows scored
  `model_version=v2`**, **7 money detections recorded** (pending). Sanity confirmed live:
  - scores in-range (0 out-of-range); directional signals on the right names — **Nvidia MM 68 / MC 25 /
    outflow**, **Apple 70 / 27 / outflow**, **JPMorgan 54 / 27 / outflow** (covered megacaps with
    congress/insider/13F); macro themes + micro-caps read **neutral** (no positioning data) — correct.
  - enriched interpretation live (Money Movement + flow + Market Confirmation + Leverage walk),
    measurement-not-advice language intact.
  - `/market/accuracy` pending=7, resolved=0 (expected — fresh detections resolve once price moves
    ±5% or the 60-day window elapses; the market sweep runs on the ledger cadence).
- **Now live for all users:** the Money Gradient (Money Movement / Market Confirmation / flow /
  leverage facts) across web/desktop/mobile + both accuracy ledgers. Reversible: `MARKET_SIGNAL_V2=0`.
- Observation to watch: covered megacaps currently all read **outflow** (net congress/insider/13F
  selling — plausible for megacaps; the ledger will record whether these reads were right).

---

## Session 2026-06-24f — Market Signal v2.0 phases 3-4: distinct market ledger (price-validated) + platform relabel

**Founder correction (key):** Google Trends does NOT validate market signals — that's the ground
truth for the ATTENTION ledger. A money signal is validated by **realized EOD price DIRECTION**.
So the Money Gradient gets its **OWN** ledger, distinct from the Trends ledger.

- **Phase 3 — distinct Market-Signal Accuracy Ledger** (`market_accuracy_ledger.py`, NEW). Ground
  truth = realized EOD close direction (FMP `historical_close`). `record_market_detection`
  (flow+intensity, dedup = one open per ticker+flow, intensity floor, neutral rejected) →
  `sweep_market_pending` resolves **CONFIRMED** (dir match) / **NOT_CONFIRMED** (opposite) /
  **NO_MOVE** (flat by 60d) + lead time. Honest denominator; NO LOOKAHEAD (post-detection closes
  only). Wired flag-gated: record at the market scoring site, sweep on the ledger cadence, init at
  startup, `GET /market/accuracy` + `POST /market/accuracy/sweep`. Attention ledger byte-identical.
  Verified: synthetic verdicts correct; live `/market/accuracy` returns the honest report (empty,
  flag off). **`FMP_API_KEY` set on the engine.**
- **Fixed a pre-existing latent bug:** the startup aux-table `ALTER TABLE ... ADD COLUMN` aborted the
  PG txn (DuplicateColumn) with no rollback → every later DDL ("current transaction is aborted") was
  skipped, including the ledger inits. Rolled back the aborted txn so the block completes.
- **Language purge (market/risk, LIVE):** served `risk_action` ("Act now"/"Begin hedging") →
  factual movement statements; Risk Gradient header, FP labels, interpretation strings, OFR,
  gravitational docstring all reframed to movement+ledger language.
- **Phase 4 — platform relabel (payload-gated, inert until flag flips):** web terminal
  (`MarketSignal.tsx`) + mobile (`risk/[key].tsx`) show **Money Movement / Market Confirmation** +
  the factual **flow** badge (▲ inflow / ▼ outflow) + v2 disclaimer when the engine serves a v2
  payload; v1 (Detection/Confidence) when off. Web deployed to gh-pages; desktop inherits the web
  build; mobile ships on Metro reload. Build clean (web vite + mobile tsc).
- **Remaining (recommended next):** a market-accuracy-ledger **VIEW** on each platform (show
  `/market/accuracy` distinct from the Trends Accuracy Ledger view); minor Dashboard `MKT_RANK`
  sort label; methodology-page mention of the Money Gradient + market ledger; then validate v2
  output end-to-end with a small recorded sample and **flip `MARKET_SIGNAL_V2=1`**.
- Out-of-scope finding (flagged): the ATTENTION engine has a served field named `what_to_do_action`
  (values descriptive, not buy/sell) — the field *name* reads as advice; worth a later consistency pass.
- **Market AI descriptor (founder request, BOTH descriptors):** the market description now analyzes
  **Money Movement + Market Confirmation + Leverage** from our score data. (1) Reproducible:
  `_market_analysis` / `_append_market_analysis` append a deterministic three-dimension walk
  (money score + filing flow, confirmation score, leverage-health fact) to the market interpretation
  at both call sites — runs v1+v2, skips calibrating/insufficient. (2) LLM: `ai_grade.market_analysis`
  — a guardrailed Claude narrative anchored ONLY to our scores (no web), 12h-cached per instrument,
  budget-gated ($20/mo cap), opt-out `MARKET_AI_ANALYSIS=0`, with a banned-word backstop
  (buy/sell/undervalued/should/… → reject) so it can't drift into advice; attached via
  `grade_agent._attach_market` as `result.market_analysis`. Grade views (web + mobile) surface it +
  v2 labels. Engine deployed; web→gh-pages; mobile on Metro reload. Forward-only: enriched overviews
  populate as market rows re-score (persisted serve path).

---

## Session 2026-06-24e — Market Signal v2.0 (the Money Gradient) — phases 1-2 shipped flag-OFF

Founder confirmed the direction: the platform MEASURES movement (attention + money) + states leverage
FACTS — no prediction/advice — but signals MAY be precursors, and the **Accuracy Ledger** judges
(factually, over time) whether they led. Congress = **Dark Matter** (insider-informed, early), NOT
lagging. Spec: **MARKET_SIGNAL_V2.md**. All flag-gated behind `MARKET_SIGNAL_V2` (default OFF).

- **Phase 1** — quality finance YouTube (Meet Kevin, The Compound) reclassified from Stage-5 "retail
  amplify" (lagging) → **Dark Matter** (stage 2, early/informed). `QUALITY_ANALYST_CHANNELS`.
- **Phase 2** — **Money Gradient scoring** (`market_signal_engine`): the SAME baseline-relative
  components reorganized into **MONEY MOVEMENT (D** = smart-money 13F/insider/shorts + congress +
  quality-analyst, the early/informed flow**)** vs **MARKET CONFIRMATION (M** = fundamentals +
  momentum + diffusion, broad/economic**)**. `_interpret_movement()` replaces alpha/early-warning
  language with movement+ledger wording ("a measurement, not a recommendation; the ledger judges
  whether it led"). Output gains `model_version`, `money_movement`, `market_confirmation`, `flow`
  (inflow/outflow), `leverage_facts`. MARKET_SIGNAL_V2 implies the congress/13F blend (D inputs).
  **Verified live: flag OFF = v1 byte-identical (no v2 leak); flag ON = Money Gradient.**
- **Remaining:** Phase 3 — money detections → Accuracy Ledger + full alpha/advice language purge
  (incl. the Risk Gradient's "before it's priced in / is the alpha" header). Phase 4 — propagate to
  all 3 platforms (web→desktop, mobile): relabel Detection/Confidence → Money Movement / Market
  Confirmation, surface flow + leverage facts, purge advice language. Then validate + flip the flag.

---

## Session 2026-06-24d — Dark-Positioning integration (SEC 13F + Congress → Market Signal, flag-OFF)

Integrated the two held-out positioning sources into Market Signal's smart-money component —
**built, wired, verified, and shipped INERT behind `DARK_POSITIONING_V2` (default off)**, pending
the predictive backtest before it moves a live score.

- **`positioning_intel.py`** (new): inverts the held-out 13F holdings (curated funds) + Congress
  trades into ONE per-TICKER signal — `signal_for(ticker, name)` → `positioning_signal` 0-1 +
  net `direction`. 13F matched by issuer NAME (`_norm_name`), Congress by ticker. Cached (daily).
  Non-circular (external SEC/Congress filings only).
- **Wiring (flag-gated, default OFF):** `market_signal_engine.assemble_market_components` blends
  the signal into `positioning_concentration` (`DARK_POS_WEIGHT=0.4`) ONLY when the flag is on AND
  the ticker has 13F/congress activity. `financial_risk_gradient` attaches
  `payload['dark_positioning_intel']` at both market-signal call sites when on (off = `positioning_intel`
  never imported → held-out preserved, zero overhead). **Verified: flag off = byte-identical
  (`pos_conc` 0.333 unchanged, no `dark_positioning_intel` in the live feed); on+signal=1.0 → 0.600;
  on+no-data → base unchanged.**
- **`GET /research/dark-positioning`** (internal-key) = the review surface — the EXACT signal that
  blends in. Live: 17 ranked tickers — AAPL/NVDA/GOOGL sig=1.00 net-selling (6-8 funds + 9-13
  congress members), AMZN 0.95 net-buying, down to LMT/MS at 0.
- **Sanity backtest PASSES** (discriminates 0-1; known cases correct; direction-aware; non-circular).
  **NOT live** — `DARK_POSITIONING_V2=0` on Heroku. To activate: run the PREDICTIVE backtest (does
  blending IMPROVE, not just change, the Market Signal — needs a historical signal×forward-return
  harness using the Congress `/bulk` history + 13F snapshots), then `heroku config:set
  DARK_POSITIONING_V2=1`. The held-out modules' "imported by nothing in scoring" holds while off.
- **PREDICTIVE BACKTEST — DONE. VERDICT: not predictive → flag STAYS OFF.** `dark_positioning_backtest.py`
  (held-out, NO-lookahead: signal as-of T uses only Congress trades FILED ≤ T; forward returns from
  Yahoo, independent of QuiverQuant). Swept 4 horizons × net/buy-only, ~1,900 obs each, 35 liquid
  large-caps, 2021-2026. Long-short spread **NEGATIVE at every horizon** (21d −0.03 / 63d −0.12 /
  126d −0.64 / 252d −0.47%; net-sell slightly outperforms net-buy), IC ≈0 (−0.039..+0.023), buy
  hit-rate ~51-53% (coin-flip), buy-only worse. Forward returns ≈identical across cohorts — they track
  market drift, not the signal. Mechanism: by the public FILED date the edge in liquid names is gone
  (30-45d disclosure lag); 13F is staler → same prior. **DO NOT flip the flag** — blending adds noise,
  not alpha. Signal stays valid as DISPLAY/transparency context (real + interesting), not a predictive
  score input. Backtest-before-ship worked exactly as intended.

---

## Session 2026-06-24c — Source Onboarding Protocol (hard rule + gotcha) + SEC fund-13F (held-out)

**SOURCE ONBOARDING PROTOCOL (§16 hard rule, founder-mandated).** Before linking ANY media/data
source, 5 gates pass IN ORDER: **TYPE → ENGINE → FORMAT → CURRENCY+ACCESS → TEST→LINK→DEPLOY**
(score-affecting ⇒ backtest-before-ship). Documented in CLAUDE.md §16, DATA_BUILDING_BLOCKS B1a
(Source Watchdog owns), AGENT_CHARTER GOTCHA G-SRC + fleet table, `/data-watchdog` skill, and
memory `feedback-source-onboarding-protocol`. **Enforced by `.githooks/commit-msg`** (a "gotcha"):
detects a source-shaped commit (feed URL / new collector / `COLLECTOR_EXPECTATIONS` entry in the
`transfer/*` collectors) and BLOCKS unless the message asserts `[source-onboarded]`. Tracked in
`.githooks/` with `.gitattributes` forcing LF (CRLF broke the bash parse); install once:
`git config core.hooksPath .githooks`. Verified: blocks without marker, allows with it, ignores
non-source commits.

**SEC fund-13F institutional positioning — built HELD-OUT (research-before-integrate).**
`transfer/sec_13f_research.py` — imported by NOTHING in scoring (like `referee_wikipedia`).
Onboarded through all 5 gates. Curated `FUND_CIKS` (Berkshire, Bridgewater, RenTech, BlackRock,
Vanguard, State Street, Citadel, Two Sigma, Tiger Global, Soros). `latest_13f(cik)` → SEC
submissions API → 13F-HR info-table XML → namespace-agnostic parse → per-CUSIP-aggregated holdings
+ total value + top-10 concentration. **`GET /research/13f?fund=<name|cik|all>`** (internal-key) =
the review surface. **Verified live from the engine** (SEC doesn't block Heroku IPs): Berkshire
Q1-2026 — 29 positions, $263B, Apple 22% / Amex 17% / Coca-Cola 12% (matches the known portfolio);
Bridgewater 993 pos / $22B; BlackRock 5230 pos / $4.4T; Citadel 6733 pos / $618B. Format-gate fix:
HTML entities decoded (S&amp;P → S&P). **NOT integrated into `positioning_concentration` yet —
founder to review `/research/13f`, then backtest-before-ship.**
Research findings to note: **BlackRock CIK (0001364742) returns a 2024-Q2 13F** (others are
2026-Q1) — BlackRock files under multiple entities; that CIK needs verification before use.

**CIK curation (B) — done.** Verified all 10: 8 hedge funds return current Q1-2026 13F-HR.
FINDING: the index/asset-management GIANTS (BlackRock, increasingly Vanguard) file 13F-**NT**
*notices* and split holdings across sub-advisor entities, so no single CIK has their full book.
**Dropped BlackRock** (0001364742 = "BlackRock Finance Inc", last HR 2024-Q2; no active consolidated
HR found). Kept Vanguard at its last HR (Q4-2025; it filed 13F-NT for Q1-2026). 9 funds remain, all
returning usable holdings.

**Congressional-trading sources — 5-gate review (NONE onboarded; the rule did its job).** Applied
§16 to the 4 given URLs — all FAIL as provided: House & Senate **Stock Watcher** S3 JSON →
**403 AccessDenied** (buckets no longer public, all paths/hostnames); **CapitolTrades** /buzz →
**429** + HTML (not a feed); **QuiverQuant** /congresstrading → HTTP 200 but a 2.2 MB **HTML page**
(structured data is behind their paid API). The SIGNAL is valuable, but ENGINE routing is
**Market Signal "Dark Positioning"** (positioning data, alongside SEC 13F + insider Form-4), NOT a
blog/Dark-Matter *trend* feed. VIABLE primary path (verified live): the OFFICIAL **House Clerk** FD
dataset (`disclosures-clerk.house.gov/public_disc/financial-pdfs/{YEAR}FD.zip` → tab-delimited index,
FilingType "P" = PTR stock trades; 1,230 filings in 2026) + **Senate EFD** (efdsearch.senate.gov) —
free + durable, but transaction details are in per-filing PDFs (parsing effort, like the stock-watcher
project did before its bucket went private). Recommend a held-out collector against the official
sources (or QuiverQuant's paid API) — verify + backtest before integration.

**RESOLVED via QuiverQuant API (founder provided a token).** Gate-4 finding: the structured data
the HTML page hid is at `api.quiverquant.com` — `/beta/live/congresstrading` returns clean JSON
(works token-less), `/beta/bulk/congresstrading` (Bearer token) = **113k+ rows** current to the day,
20 fields incl. ticker/transaction/size/party/chamber/excess_return. **All 5 §16 gates PASS.** Built
**HELD-OUT** `transfer/quiver_research.py` (`congress_recent()` → recent trades + per-ticker
concentration) + **`GET /research/congress`** (internal-key, the review surface). Token stored as the
Heroku env var **QUIVER_API_KEY** (set 2026-06-24, v147; NOT committed). Verified live: 1000 recent
trades, 401 tickers; members net-selling mega-cap tech (AAPL −7, NVDA −7), net-buying LLY +4 / AMZN +2;
Pelosi buying UBER+INTC. ENGINE = Market Signal **Dark Positioning** (alongside SEC 13F). **NOT wired
into positioning_concentration** — review `/research/congress`, then backtest (the `/bulk` feed is the
historical input) before integration. NOTE: QuiverQuant also exposes insider/lobbying/gov-contracts/WSB
datasets — each would need its own gate review. Security: token was shared in chat → rotate if the
transcript is ever exposed.

---

## Session 2026-06-24b — Founder 10-day QA + source cleanup + new-source review

**Founder QA review (2026-06-10 features):** the pasted runbook targeted the FROZEN 1.0 engine
(nowtrendin-e62…) — ran every check against **v2** instead. All 4 features verified live + working:
Signal Convergence (`/convergence`, sensible CONFLICTING/MIXED verdicts, warming_up cleared at 7
snapshots), Dark Matter recalibration (`100*ratio^0.7`, D spans 0–49, **no clustering at 65**),
news provenance tiering (per cycle: ~33–38 promoted dark-matter, ~118–149 mainstream, quarantine
firing), reputable allowlist (~80 publishers). The prior "/usage doesn't track news aggregators"
flag was a **measurement artifact** (truncated 900-char output) — all aggregators ARE tracked.

**Source cleanup (engine deployed):**
- **HackerNews was DOWN** (0 signals) — `hn.algolia.com/api/v1/search` now returns 0 for
  `points>50` numericFilters (verified live; `/search_by_date` returns results with the same
  filters). Switched the collector to `/search_by_date`. Moat source FIXED, not removed.
- **yahoo_finance REMOVED** — RapidAPI 429 every cycle (quota exhausted), 0 signals, ~600 wasted
  calls/30d. Gated both collectors behind `YAHOO_FINANCE_ENABLED=0` (default off) + removed its
  collector_health expectation. Reversible.
- **newsapi_ai ("newai") kept** — it IS producing (100 art/cycle → 573–635 signals); not dead.
- **QA runbook repointed:** `monitoring/integrity-check.ps1` `$BASE` + README were checking the
  frozen 1.0 engine — corrected to v2.

**New Market-Signal sources reviewed (tested before wiring — none shipped):**
- **Mises Institute Literature** (mises.org/rss/library): **REJECT** — HTTP 404 (dead URL) AND it's
  classic economic *literature* (historical books), not current signal.
- **NBER** (real URL `back.nber.org/rss/new.xml`, the given one 301-redirects): works, but academic
  paper titles **extract poorly** (fail the quality gate; sub-phrases are noise like "times
  geopolitical fragmentation"). It's also a macro-research/TREND source, NOT Market-Signal
  positioning. **Recommend against wiring as-is** — would need a research-concept extractor first.
- **SEC EDGAR 13F** (Berkshire CIK atom feed): **HTTP 200, 40 real 13F filings — the strong fit.**
  SEC EDGAR is already a live collector (`sec_edgar`, ~334 sig/cycle, does Form 4 / 8‑K / 13F for
  watchlist COMPANIES). The enhancement = track specific mega-cap FUND 13F-HRs (Berkshire et al.)
  to see where institutions move billions → feeds `positioning_concentration`. Real win, but
  score-affecting (needs a validated build + 13F-HR holdings-table parsing) — recommended, not shipped.

---

## Session 2026-06-24a — Overbroad "news" fixed + quarantine review loop + log corrections

### The "news" category was 77% UNCLASSIFIED, mislabeled (display-only fix, big drain)
- **Root cause:** `topic_categories.classify_topic` returned **'news' on NO lexicon match** —
  but 'news' has no lexicon of its own (real news/geopolitics matches `current_events`). So
  the 77% "news" catch-all was really 77% *unclassified*, wearing a News label.
- **Fix 1a:** no-match fallback → honest **'general'** (matches the module's own documented
  intent + the empty-blob case). 'news' as a produced category is now ~0.
- **Fix 1b (the real drain):** **context classification** — a background map (`_CONTEXT_CAT`)
  classifies each topic against its OWN signal **headlines** (`raw_signals.title`), so a bare
  entity with no lexicon hit ("lilly"→health, "britain"→politics, "wembanyama"→sports) resolves
  from real source text. Conservative 0.35 confidence floor; catch-all results dropped.
  `_category_for` now layers **situation(event) → context(headline) → bare lexicon → general**.
- **Verified live: catch-all 77.0% → 55.7% (−21.2 pts)**, 63,450 topics context-classified,
  883/4000 reclassified — spread PROPORTIONALLY across tech/politics/sports/business/health
  (healthy, not dumped). Display-only: scoring method + corroboration gate still use the bare
  lexicon → no score impact, no circularity. Web terminal chips are data-driven (`/categories`)
  so "General" appears + "News" drops automatically. **Mobile chip row (`frontend/lib/signals.ts`
  CATEGORY_DEFS) is hardcoded with a 'news' chip — small parity follow-up (swap to 'general').**
- **Bug caught + fixed:** `/categories` had 500'd since v133 — audit #1 changed its count to
  `_category_for(topic_key, …)` but the SELECT only returned `topic_display` (KeyError). Added
  `topic_key` to the SELECT. (Web-terminal category chips were silently broken until now.)

### Quarantine review loop — the date queue had no exit path (now closed)
- `format_review_queue` (unparseable dates → human review) was WRITE-ONLY: `pending_reviews()`
  + `resolve_review()` existed but **no endpoint exposed them**, and **`gate_date` never
  consulted `format_rules`** (so the "learned rule auto-applies" the docstring promised was
  never wired). Queue currently empty (0), but the loop was broken.
- **Fix 2a:** `gate_date` consults `format_rules` BEFORE quarantining (auto-applies a
  human-approved normalization to identical future inputs). **Fix 2b:** `GET /quarantine/dates`
  (list pending + candidates) + `POST /quarantine/dates/resolve` (human picks chosen_value,
  validated canonical, learns a rule). Flag-never-force.

### SESSION_LOG corrections (per external review of the log)
- **Live URLs table:** the Engine row pointed to the FROZEN 1.0 app + the `git push heroku
  HEAD:main` command that caused the 2026-06-19 accidental 1.0 deploy. Corrected to the v2
  engine + `heroku-v2engine` remote; 1.0 row relabeled "FROZEN, DO NOT DEPLOY".
- Forward-referenced the stale corroboration "WORSENING +230 / 10,488 leaks" alarm → its
  2026-06-23f correction (artifact; true leak ≈5).
- Verified live: **GUARDIAN_API_KEY still missing** on the engine (deliberate 06-20 deferral, but
  every score is computed without that mainstream signal — user decision to set it or not).
  SECRET_KEY is **present** (the review's "insecure default" claim is stale). Apify/Dev.to set;
  Reddit deferred. `DB_DATA_DICTIONARY.md` confirmed stale.

### Founder decisions actioned (2026-06-24)
- **Guardian + Reddit:** proceed WITHOUT both (deliberate; not gaps to chase).
- **Retention → 365 days canonical** (resolves the long-standing 90-vs-365 ambiguity). All
  `_prune_velocity_scores`/`prune_velocity_scores` defaults + env fallbacks
  (`VELOCITY_RETENTION_DAYS`/`VELOCITY_KEEP_DAYS`) 90→365; CLAUDE.md §13 + DATA_BUILDING_BLOCKS
  + all retention comments updated. ⚠ **STORAGE:** ~5.4GB@90d → ~22GB@365d **exceeds the 10GB
  Essential-1 Postgres plan** — a larger plan (or downsample-after-90d) is needed before the
  year-tail fills in (no immediate effect — app is ~3 months old). Flagged in-code at the prune site.
- **3-platform UI parity (Market lane axis + category chips):** web terminal already had lanes +
  data-driven chips; desktop = Tauri over the web build (inherits). **Mobile** brought in line:
  `CONTENT_CATEGORIES` news→general; `MARKET_LANES` (All / Covered / Halted·micro-cap / Macro)
  mirrors the web `LANE_FILTERS` exactly → lane chip row on the market-category view, lane subline
  + LTD-DATA/"positioning N/A" on `RiskCard`, N/A components + macro caveat in the risk detail.
  `RiskScore.marketGradient` threaded with lane/dataCoverage/naComponents. tsc clean; ships on next
  Metro reload/EAS build. **DB_DATA_DICTIONARY.md regenerated from the live schema** (see that file).

---

## Session 2026-06-23f — Catch-all audit closeout (items #1–#3), all display/forward-only

Completed the three open catch-all audit items. **Every change is display-only,
forward-only, or monitoring-only — no `velocity_scores` deleted (90-day retention),
no scoring input altered, no circularity.** Engine deployed v133→v138.

### #1 — Situation→category routing (drains the catch-all by CONTEXT, not bare word)
- **`situation_clustering.category_map_from_db()`** — builds a `{topic_key: category}`
  override from the held-out clustering: each situation's SPECIFIC category (skipping
  news/general) applied to its members, largest-situation-wins. A context-dependent
  entity is routed by its SITUATION (hormuz in an Iran situation → current_events) —
  what the bare-word lexicon structurally cannot do.
- Engine: `_SITUATION_CAT` cache + `_situation_category_loop` daemon (30 min,
  `SITUATION_CATEGORY_ENABLED`) + **`_category_for(topic_key, display)`** applied at the
  SERVE sites only (detail, list feeds, mobile feed, category-chip counts). **NOT** at the
  scoring method or the corroboration-floor gate `_passes_corroboration` — keeps the
  situation layer (built FROM scored signals) out of scoring ADMISSION → no circularity.
- `/audit/topics` now reports raw vs routed catch-all %. **Honest measured drain: ~0.6 pts
  (≈25 topics).** Small because the catch-all is **100% "news"** (the lexicon FALLBACK) and
  is dominated by genuinely-news topics + the long tail that forms no situation; forcing the
  rest into specific buckets would be label inflation (integrity-forbidden). The router
  rescues only the corroborated context-entities, and scales as more situations form.

### #2 — Corroboration-floor "leak" was a MEASUREMENT ARTIFACT, not a floor failure
- The Catch-All Auditor reported **10,488 single-source leaks / "floor disabled"**. Root
  cause: it checked corroboration over the last 72 h of `topic_signals` but compared it to
  the LATEST score of EVERY topic — dormant topics' signals had aged out (false nsrc=0) —
  AND it omitted two of the floor's own exemptions (high-magnitude, window alignment).
- Rebuilt the metric to replicate `_passes_corroboration` EXACTLY (expert-tier + tracked +
  `MAX(engagement_raw) ≥ HIGH_MAGNITUDE_ENG`) and to align windows (corroboration widened to
  score 72 h + recent 24 h = 96 h ⊇ every recent topic's scoring window). Split into
  `single_source_catchall_leak` (current, scored ≤24 h) vs `dormant_catchall_pile` (aged,
  retained). **TRUE current leak = 5 (≈ 0); dormant pile ≈ 8,500. The floor is healthy.**
  The "WORSENING +230" in the old summary was stale — live trend is IMPROVING/STABLE.

### #3 — 539 tracked detections stuck in catch-all — fixed at the source, 3 ways
- **Lexicon:** unambiguous tech terms (javascript, typescript, wwdc, chatbot/s, webassembly)
  added to `topic_categories` technology → reclassify out of catch-all (verified gone from the
  tracked-in-catchall examples). Bare geographies (britain, canada) deliberately NOT added —
  routed by the situation layer (#1).
- **`record_detection` sink-hardened** with the shared quality gate (forward-only, fail-open):
  fragment non-topics ("sunday afternoon", "york for months") can no longer be TRACKED.
- **`sweep_pending`** resolves legacy non-quality pendings as `excluded_nonquality`
  (non-deleting, auditable) instead of letting them time out as FALSE_POSITIVE — a non-topic
  is not a failed prediction, so this protects the Accuracy Ledger's honest denominator (the
  moat). Auditor's misclassified count now skips quarantined rows.

### Tier 1 Market Signal triage — DONE (engine v139 + gh-pages)
The Market Signal universe mixed three instrument types one template can't fairly serve,
producing ~86% "insufficient coverage" — much of it a CATEGORY ERROR, not a real gap.
Verified live: **94 halted/micro-cap · 15 covered · 3 macro themes**.
- **Coverage LANE** (`market_signal_engine.compute_market_signal` gains `lane` +
  `na_components`; `financial_risk_gradient._market_lane()` types each item from the existing
  `_risk_maturity`): covered / halted_microcap / macro_theme.
- **Macro themes** (recession, inflation — no ticker) mark `positioning_concentration` +
  `fundamental_confirmation` STRUCTURALLY N/A: excluded from BOTH the weighted score
  (renormalized) AND the coverage denominator — not a data gap, a category error to ask for.
  Result: inflation/recession moved insufficient→partial; **covered lane = 7 full / 8 partial /
  0 insufficient** (the real signal, no longer buried under halt micro-caps).
- Default path (lane=covered, no N/A) is byte-identical — no Gradient/Market score input changed.
- **Web terminal**: Lane chip axis (Covered N / Halted·micro-cap N / Macro themes N) above the
  Tier chips; row subline + detail-rail lane chip; macro-theme N/A note; Market Factors render
  N/A components as greyed "n/a". `MarketGradient` type extended. Build clean, deployed gh-pages.

### Next
- (Optional) extend the lane axis to the mobile Market tab for 3-platform parity.

---

## Session 2026-06-23e — Situation model (topics-not-words) + corpus quality gate

### Topics-not-words: the situation layer (held-out, READ-ONLY — affects no score)
- **Problem (founder):** the engine tracks WORD fragments ("hormuz", "japan"), not SITUATIONS.
  "japan" is one over-aggregated blob smearing the Belgium royal visit + BOJ rate hike +
  World Cup, while "bank japan" fragments off and "japan vs Sweden" is missing.
- **`situation_clustering.py`** — co-occurrence (topic_signals.signal_id, already recorded) →
  Jaccard-normalized edges → **hub-aware** clustering: detect a hub entity ("japan") that
  bridges distinct situations, cluster WITHOUT it, re-attach it as a shared searchable anchor.
  Proven: "japan" → 3 separate situations (belgium / bank-of-japan / world-cup). Situation
  first_seen = earliest member first-seen (reconciles word-level discovery undercount).
- **`/situations/preview`** (held-out, internal-key, ~10min cache) — runs it on the REAL
  corpus. `SITUATION_MODEL.md` = the full recommended solution (entity→situation→fragment;
  data model + DB-redundancy; search/disambiguation; situation-level scoring 🔒-gated; filter+
  sort taxonomy; the **Situation Contract** = one protocol for every agent + scorer; rollout).

### Corpus quality gate (the situation layer exposed it; fixed at the ONE shared gate)
- Phase A on real data surfaced two pollutants the per-word view hid: multilingual casino/SEO
  spam + HTML/JSON/code boilerplate n-grams. **`_is_quality_topic` strengthened** (the single
  gate used by extraction, scoring, serve-time, Pipeline Integrity, AND the situation builder):
  SPAM_TERMS (gambling, multilingual), CLAUSE_FILLER (clause debris), BOILERPLATE bigrams/
  tokens, MAX_TOPIC_WORDS=5, MAX_TOKEN_LEN=20, **split on `[\s_]+`** (kills underscored
  field-name fragments like `show_article_date`), + **KNOWN_CONCEPT_PHRASES** recall whitelist
  (fixes a PRE-EXISTING drop of "interest rate"/"monetary policy"/"world cup"/"vector search"/
  "model context protocol"). Precision-verified: 27/27 real pass (0 false rejects), junk rejected.
- Situation builder also applies `registry_only` (tracked-entity requirement) which structurally
  removes spam the vocabulary can't enumerate (first_seen=None).
- **VERIFIED LIVE across scoring + agents:** `/situations/preview` 0 junk situations (365 dropped,
  real events dominate — Greenspan death, SNP/Murrell, Tesla autopilot, Giannis trade, Starmer
  resigns, Iran oil sanctions); `/scores` 0 junk in the 2,290-topic board, "world cup" now served
  + scored 94.8 (recall fix live); `/monitor` pipeline_integrity + scorer_watchdog OK (no
  regression). Engine deployed 5ea4d4b.

### Phase B (LIVE, held-out) — per-situation category + entity disambiguation
- `categorize_situations()` — each situation tagged via majority vote of the shared
  `_topic_category` over its CORE members (prefers a specific category over the catch-all).
  Live: llm·claude→technology, senate→politics, clive·davis→entertainment, gong→current_events.
- `search_situations()` + **`/situations/search?q=`** — entity disambiguation: q=iran → 6 distinct
  situations (oil sanctions / congressional funding / Pakistan-Iran / Trump-Iran war), each
  categorized. Exactly the founder's "make words searchable, user picks the situation."
- Honest limit: some still read "news" (giannis→news not sports) — the category LEXICON has
  gaps, which the audit (below) quantifies as the top cleanup target.

### Audit (LIVE, READ-ONLY) — `/audit/topics`, no deletes (90-day retention respected)
- Scored universe (30d, 9,000 latest-per-topic): **80.3% real / 19.7% junk** (clause fragments
  like "easier the narrative", "bike ride" — now filtered at serve-time by the gate, history
  retained). **75.3% catch-all** (news/general) = the category LEXICON gap, the #1 UX cleanup
  (working cats: technology 955, current_events 332, politics 319, sports 249, business 110).
  **0 exact duplicate-spelling groups** (canonical-key + alias consolidation is working; the
  remaining duplication is SEMANTIC, which the situation layer handles).
- The audit caught + fixed gate false-positives the unit test missed (hyphenated tech compounds
  `retrieval-augmented-generation`, geo `west bank`) — keep hyphens intact, whitelist geo/tech.
- COMPLIANT cleanups (no deletes) — DONE:
  - **#2 serve_payload regenerated** via new `POST /precompute` (GOTCHA G1, background, no
    re-score). Board fresh: 2,601 topics, 0 casino/boilerplate junk. (`asi`/`shaving` generic
    tokens still leak on /scores — a separate serve-filter coverage edge to check.)
  - **#3 lexicon enriched** (`_LEX`): added ONLY unambiguous Catch-All Auditor candidates —
    technology (google, bsky), politics (obama), current_events (iranian/israeli/chinese/
    hormuz/strait of hormuz/juneteenth). Catch-all **75.3%→73.9%** (tech 992, current_events
    400, politics 344). Bare peaceful countries (australia/canada/texas/america) deliberately
    NOT force-routed — multi-category; the SITUATION layer (Phase B) routes them by context.
    Honest: lexicon fixes FREQUENT unambiguous terms (~1.4%/batch); the bulk of the 74% is
    context-dependent entities → structural fix is situation-level categorization.
  - Auditor also flags (separate): corroboration-floor **WORSENING** (single-source catch-all
    leak +230) and **542 tracked topics stuck in catch-all** — data-quality follow-ups.
    **→ SUPERSEDED by 2026-06-23f:** the "WORSENING / 10,488 leaks" was a MEASUREMENT
    ARTIFACT (dormant pre-floor pile + missing floor exemptions + window drift). True
    current leak ≈5; the floor is healthy. The 542 tracked were fixed at the source
    (lexicon + record_detection gate + sweep quarantine). See the 2026-06-23f entry.
  Engine deployed 55ff376. NO velocity_scores deleted (90-day retention respected throughout).

---

## Session 2026-06-23d — Opus fundamentals audit + Phase 2 referee (Wikipedia) begun

### Audit (verified against LIVE engine, not docs — verify-before-ship)
- **Congruency audit of all scoring models / agents / contracts.** Confirmed the
  fundamentals are largely solid LIVE, and found + fixed the gaps below.
- **Date canon (§14) — VERIFIED CLEAN live.** `/monitor/datecanon`: 0 non-canonical
  across all declared columns (`market_signal_history.signal_date` 71,146 rows;
  `risk_signals.signal_date` 2,226; `accuracy_ledger.breakout_date` 21 — all 0 bad).
  **`DB_DATA_DICTIONARY.md` is STALE** (committed 2026-06-21, pre-migration): it still
  shows `market_signal_history.cycle_at` + MIXED formats that the live schema no longer
  has. Doc-hygiene only — regenerate it. (Auditor blind spot noted: a declared-but-absent
  column is silently skipped at monitoring_agents.py:1002 — fine today since the column
  exists, fragile if a future rename desyncs DATE_SEMANTIC.)
- **INV-1 / serve consistency — clean.** `pipeline_integrity = ok` live (no stale
  serve_payload, no mainstream collapse). `scorer_watchdog = ok`.

### Fixed (✅ shipped + deployed, engine c0705b9)
- **heisenberg_gap derived-rule break (was live CRITICAL: 50/800).** Root cause: the
  Enterprise `/query` path (`persist_velocity_score`) wrote the SCORE-TIME gap;
  `apply_calibration` overwrites det/conf but inherits the stale `heisenberg_gap` from
  `**raw_result`. The contract auditor samples the latest row per topic, so every
  `/query` re-introduced a stale row → oscillated 33↔50, never "healed" (the SESSION_LOG
  "healing" claim was wrong). Fix: **sink-harden** `persist_velocity_score` to recompute
  `gap = det − conf` right before INSERT (mirrors the main path L4370). Invariant now holds
  at the write sink regardless of caller. Zero score impact (derived display field).
- **Weight single-source migration COMPLETED** (the "3 disagreeing recipes → 1" Step 0
  item, finished). `scoring_weights.py` existed but the primary scorer + `ai_grade` +
  `enterprise_intel` each kept their OWN hardcoded copy (agree-by-value, not enforced).
  Now ALL import from `scoring_weights.py` (value-identical fallback). Primary scorer uses
  an explicit naive left-fold `_weighted()` (NOT `sum()` — CPython 3.12 compensated
  summation shifts the 2nd decimal on ~0.01% of rows). **Proven BIT-IDENTICAL across 200k
  random vectors (0 mismatches)** → zero score impact, single source now real.

### Phase 2 — Independent referee (Wikipedia Pageviews) — STARTED
- **`referee_wikipedia.py` built + live-validated.** HELD-OUT (imported by NOTHING in the
  scoring path; read-only to the score, forever — the falsifiability guard). Resolve
  (MediaWiki opensearch, confidence-gated, quarantine-on-no-match) → daily pageviews
  (Wikimedia REST, anchored window around our detection date) → **arrival date** = first
  SUSTAINED surge above a lowest-40% quiet baseline, with same-surge `since` floor —
  MIRRORS the ledger's frozen `detect_breakout_date` so both providers define "arrival"
  identically. `lead_days = detection − arrival` (positive = we were LATE = false-early).
  Live-tested on Hormuz/Iran/DeepSeek/ChatGPT: resolves + dates surges correctly; surfaced
  that continuously-hot topics (Iran/Hormuz) have no clean "arrival" (the referee's honest
  limit — precise on quiet→loud transitions).
- **Founder froze the arrival definition:** EARLIEST of (Wikipedia surge OR GDELT surge);
  false-early if our detection is after it (strictest against over-claiming early).

### "Strait of Hormuz issue" — RESEARCHED + RECONCILED (the key reframe)
The founder flagged: the app was only built ~2026-03, so apparent "late" calls may be a
STARTING-POINT artifact, not an engine defect. Confirmed — decisively.
- **Topic-class research** (live Wikipedia signatures): topics fall in 3 classes —
  CLEAN (one isolated arrival; referee precise), CHURNING (Hormuz 42% of days elevated /
  Iran 17% — surges repeatedly, no single arrival), STEADY_MAINSTREAM (Russia/China
  peak/floor ~2× — never surges, permanently arrived). Codified `classify_topic()`.
- **Observation-window gate** (`assess()` + `our_first_seen`): a false-early is FAIR only
  if we were TRACKING the topic before its arrival. Ran the gate over all 21 REAL ledger
  detections joined to each topic's `first_detected_at`: **only 1/21 is a fair scoring
  test** (Daveigh Chase — caught SAME-DAY, LED). 4 are DISCOVERED_AFTER_ARRIVAL (we found
  diffusion models/world models/Juneteenth/FIFA 2–30 days AFTER their Wikipedia surge — a
  DISCOVERY-LATENCY gap, NOT a scoring false-early), 8 unresolved (Wikipedia lacks niche
  tech → GDELT needed), 7 no-surge, 1 already-mainstream.
- **Conclusion:** the apparent late-calls are overwhelmingly a young-system / discovery-
  window artifact. The naive "83% false-early" collapses to a non-result; fair sample = 1.
  Honest verdict = **INSUFFICIENT, claim nothing yet** (punch-list Phase 3). The referee is
  a PROSPECTIVE instrument — meaningful as detections of post-launch emergences accrue.
  The real actionable lever it exposes is **discovery latency** (widen/speed collection so
  topics enter the corpus BEFORE they surge), which is distinct from scoring calibration.
- **NEXT:** GDELT provider (covers the 38% Wikipedia can't), held-out `referee_observations`
  table, `/accuracy/referee` endpoint that applies the observation gate + reports the
  fair-sample count alongside any rate. NO public accuracy claim before a fair sample matures.

---

## Session 2026-06-23c — Step 0 🔒 feature-flagged quarantine (continued)

### Completed (✅ LIVE — pushed, deploy next)
- **`scoring_weights.py` — single source of truth for weight vectors.** New module.
  Defines `WEIGHTS_OVERALL / WEIGHTS_DETECTION / WEIGHTS_CONFIDENCE / COMPONENTS`.
  All 6-component (G·I·M·D·C·P, N excluded). Canonical values unchanged.
- **`calibration_engine.py` — dead 5-component block replaced.** Legacy recompute
  at the end of `compute_calibrated_gradient()` now imports from `scoring_weights.py`
  and includes the P (persistence) component. This code path is never called by the
  live scoring path (owned by `signal_calibration_integration.apply_calibration`), so
  zero score impact. Documented with a `NOTE:` comment.
- **`signal_calibration_integration.py` — write-time quarantine (feature-flagged):**
  - `SCORE_QUARANTINE_ENABLED = os.getenv(..., "false")` — default off
  - `_quarantine_weighted_sum()` helper: None-aware weighted average, renormalizes
    over present components only (absent ≠ genuine zero → no fake-zero deflation)
  - `apply_calibration()`: when flag=True, component reads omit `or 0` so absent
    values stay None and feed `_quarantine_weighted_sum`. When flag=False (default),
    byte-identical to original `or 0` behavior — production scores unchanged.
- **`market_signal_engine.py` — market component quarantine (feature-flagged):**
  - `_MKT_QUARANTINE` mirrors same env var
  - `assemble_market_components()`: when flag=True and both FINRA (`short_interest`)
    AND WhaleWisdom (`institutional_holdings`) are absent AND no insider stage-1
    signals, `positioning_concentration` returns `None` (structurally missing data —
    not a genuine zero reading)
  - `compute_market_signal()`: `absent` set is always empty when flag=False → non-
    renormalization path → byte-identical to original. When flag=True, renormalizes
    `DETECTION_WEIGHTS` / `CONFIDENCE_WEIGHTS` over present-only components.
- Commit: `7a8a511` — `git push origin main` done.

### Open / Next
- **Phase 2 (Wikipedia + GDELT referee) — build this next.** The gate that unblocks
  the 🔒 quarantine fixes. No public accuracy claim before this returns a measured
  false-early rate. Design: held-out validation table (topic → Wikipedia breakout
  date, GDELT corroboration), `detect_vs_breakout` delta distribution, false-early
  rate metric. Endpoint: `/accuracy/referee`.
- **After Phase 2 validates direction:** set `SCORE_QUARANTINE_ENABLED=true` on
  `nowtrendin-v2-engine` Heroku app → Phase 2 backtest confirms improvement →
  commit as permanent default.
- **`positioning_concentration` data gap** — requires populating upstream FINRA /
  WhaleWisdom data (a separate collection task). The quarantine gate above correctly
  surfaces this as absent rather than zeroing it.
- **Phase 3** (predictive lead against price) — only after Phase 2 shows an
  acceptable false-early rate.

---

## Session 2026-06-23b — Alpha-engine punch list: Step 0 + Step 1 ⚡ fixes + Agent 17

### Completed (✅ LIVE — deployed)
- **Alpha-engine punch list framing.** Three-phase plan established (CLAUDE.md):
  - Phase 1 — make the present-tense score correct (Step 0 + Step 1 mechanics)
  - Phase 2 — Wikipedia + GDELT independent referee (no-gap test → false-early rate)
  - Phase 3 — prove a predictive lead against PRICE (pre-registered bar, prospective)
  - No investor performance claim before Phase 3 returns PASS, documented + reproducible.
- **Step 0 ⚡ (HIGH-severity, no backtest) — all shipped:**
  - **AI-grade weight integrity (C1/C2):** `grade_tool.py` previously used legacy 7-component
    weights (N still in denominator even though `comps["N"]=0.0`). Removed N entry;
    renormalized detection (6→6 components) and confidence (5→5) weight sets to sum to 1.0.
    Grade scores now land on the engine scale. No-circular-N integrity closed.
  - **`engagement_asymmetry` key drift (C4):** scoring path used `"engagement_asymmetry"` but
    signal dict key was `"engagement_asymmetry_score"`. Fixed to match real key.
  - **Calibration swallows now log + stamp (C8):** three silent `except` blocks in
    `apply_calibration` that swallowed errors and served raw (uncalibrated) scores now
    log a warning + record to `calibration_errors` table + stamp `calibration_method="raw"`.
  - **`risk_stage` single vocabulary (C6/C7):** declared `_RISK_TO_MARKET_TIER` map at
    module top of `financial_risk_gradient.py`; both the market-gradient path and the
    no-market fallback now write the single MARKET tier vocabulary
    (ELEVATED/ACTIVE/BUILDING/ROUTINE/DORMANT). Off-enum stages can never appear in `risk_stage`.
  - **`heisenberg_gap` signed + write-path fix (C5):** serve path fixed to signed
    (det−conf). Write path: added unconditional signed recompute right before INSERT so the
    stored column always matches the formula (both dual-pathway AND apply_calibration now
    covered). Agent 17 confirmed 33/800 residual stale rows from before the fix (heal
    as topics re-score).
- **SCORING_CONTRACT registry + Agent 17 (Scoring Contract Auditor, `/monitor/scoringcontract`, B3b):**
  New `scoring_contract.py` module — the declared FORMAT CONTRACT for every scoring field
  (type/unit/range/enum/required/derived-rule). Agent 17 audits live data against it:
  catches value violations, off-enum stages, degenerate (flat) fields (the C3 silent-misread
  fingerprint), derived-field inconsistency (heisenberg_gap==det-conf), and undeclared
  scoring-shaped columns. Live: 0 value violations, 0 degenerate fields, 1 derived mismatch
  (33/800 heisenberg_gap stale rows from before the write-path fix — healing).
- **`/monitor` timeout fix:** `run_all` previously included `catchall_auditor` (full
  velocity_scores + topic_signals 72h scan, documented "end-of-day") alongside `canon_date_auditor`
  and `scoring_contract_auditor` — all three did full table scans that pushed the synchronous
  `/monitor` endpoint past Heroku's 30s router limit. All three moved to their own endpoints
  (`/monitor/catchall`, `/monitor/datecanon`, `/monitor/scoringcontract`). `run_all` is now
  the FAST liveness roll-up: 4.1s confirmed.
- **Step 1 ⚡ (data hygiene, display — all shipped):**
  - **Alias-merge:** `_TOPIC_ALIASES` in `gravitational_anomaly_detector.py`:
    `"hormuz" → "strait of hormuz"`, `"mcp" → "model context protocol"`. Forward-only.
  - **Market interpretation honesty:** `_interpret_gap()` in `market_signal_engine.py` now
    detects when >50% of market inputs are exactly 0.0 (absent data) and appends a note to
    the ROUTINE text, distinguishing "genuinely quiet" from "insufficient data coverage."
  - **Minimum signal guard for market movers:** `get_risk_scores()` now sorts topics with
    `total_signals < 3` below scored items, so cold-start noise doesn't surface as a top mover.

### Open / Next
- **Step 0 🔒 (score-moving, feature-flagged) → COMPLETED in session 2026-06-23c.**
  `scoring_weights.py` created; quarantine gated on `SCORE_QUARANTINE_ENABLED=false`;
  commit `7a8a511`.
- **Phase 2 (Wikipedia + GDELT referee) — build this next.** No public accuracy claim until
  this returns a measured false-early rate. Gate that unblocks flipping the 🔒 flag.
- **Phase 3** (predictive lead against price) — only after Phase 2 shows an acceptable
  false-early rate.

---

## Session 2026-06-23 — Read-path performance: Prewarm Agent, pagination, favorites

### Completed (✅ LIVE — deployed)
- **Prewarm Agent (Agent 15 — operational, read-only re: data).** Daemon thread in the
  **API process** that keeps every list-feed superset hot (`/scores`, `/topics`,
  `/history/recent` 7d/24h/12h, `/risk/scores`), re-warming every 25 min inside the 30-min
  cache TTL. `GET /prewarm` is non-blocking (kicks a background warm — synchronous warm
  ~38–44 s exceeds Heroku's 30 s router limit). Documented in `AGENT_CHARTER.md` (Agent 15),
  `DATA_BUILDING_BLOCKS.md` (§10.J + §8 read-path), and the nowtrendin2.0 skill.
- **History endpoint cached + prewarmed.** `/history/recent` was uncached → ~6 s/2.1 MB on
  the 7d view (the visible "Loading…" delay). Refactored to the scores/topics superset-cache
  pattern (`_compute_history_full`, limit-independent) → ~0.4 s compute from warm cache.
- **Progressive pagination for all list sections.** `/history/recent` + `/risk/scores` now
  take `offset`; web `api.ts` got `historyAll()` + `riskAll()` (fetch 100 at a time, paint
  per batch). History.tsx + MarketSignal.tsx load progressively (Trends `/topics` already did).
  All three list surfaces now match.
- **Market Signal prewarm parity** — `/risk/scores` superset-cached (`risk_full`) + warmed
  each cycle. All five web/mobile feeds are now prewarmed.
- **Favorites "Track topic" fix** — scoped to trend/history topics only (was mixing market
  instruments); clicking opens **History** pre-filtered to the topic (was the Market detail rail).
- **AI Context fixes** — serve-time `_clean_explainer` + hardened `_extract_json` (raw
  ` ```json ` leak); `key={topic_key}` on the web detail rail (stale-context-on-topic-switch).
- **Stage rename** — "Emerging" → "Indicating" (display-only via `stageLabel()`, all surfaces).
- **Accuracy-Ledger backlog (1066 pending) — analysis + the safe fixes (#1–3) shipped.**
  Root cause: inflow (≤20 detections/score-cycle) ≫ outflow (sweep was once/day, 8/run) AND
  `sweep_pending` had no `ORDER BY` so it re-checked the same head rows forever (the slow-to-
  confirm LED wins, which sit in the tail, never got reached). Fixes: (1) rotate
  oldest-checked-first; (2) resolve past-deadline rows to FALSE_POSITIVE with NO Apify fetch;
  (3) own cadence `LEDGER_SWEEP_INTERVAL_HOURS` (default 6h = 4×/day), env-tunable vs the
  Apify budget. Unit-tested; verified live (total 6→7, pending 1067→1066 right after deploy).
  Deferred (backtest-gated, your call): #4 shorten `LEDGER_TIMEOUT_DAYS` 90→~45; #5 prioritize
  fetches by breakout-window + conviction.
- **Canonical date (§14) enforced in the ledger path** — both detection-recording paths
  (`_record_top_detections`, `validate_recent_detections`) were slicing `detection_date` with
  raw `[:10]` (the forbidden anti-pattern). Now use `date_utils.to_iso_date` (whole-string
  parse, None→skip on unparseable). `accuracy_ledger.detection_date` confirmed clean YYYY-MM-DD live.
- **Canonical Date Auditor (Agent 16, `/monitor/datecanon`, B3a)** — answers "how did the
  `[:10]` violations survive the canon sweep, and what stops it recurring." Root cause:
  `gate_date()` is OPT-IN per call site; the `DATE_SEMANTIC` registry had no consumer
  verifying compliance; a path that BYPASSES the gate creates no review → invisible to the
  gate's own audit. No agent owned "every date-semantic write is canonical." Fix: an agent
  that audits the DATA (every registry column + every `*_date` column discovered from the
  live schema), so a bad date is caught regardless of code path and a NEW source is covered
  automatically (coverage by column funnel, not a per-source list). Sink-hardened
  `record_detection`. Wired into `/monitor` run_all. Verified live: **status ok, 0
  non-canonical across all 8 date-semantic columns** (incl. market_signal_history 66k,
  pull_history 228k rows). Operational `timeout_date` allowlisted (it's an instant, not a key).

### Open / Next
- Accuracy-Ledger fixes **#4–5** (timeout shorten + fetch prioritization) — deferred,
  backtest-before-ship.
- Optional: apply the same progressive load to Alerts/Watchlist/Dashboard typeaheads.

## Session 2026-06-22 — Sources, canonical-date checkpoint, M/D direction

### Completed (✅ LIVE — engine v98)
- **Nasdaq Trade Halts** wired into the risk module (`financial_risk_gradient.collect_nasdaq_halts`,
  registered in `run_risk_collection`): official exchange RSS, stage-2 microstructure;
  canonical `signal_date`=HaltDate, `source_time`=HaltTime. Verified in prod: 29 halts.
- **The New Yorker** (news + business) added to the reputable-direct RSS roster
  (`_RSS_FEEDS`). Verified in prod: 54 raw / 269 topic signals, tier=mainstream.
- **Documentation checkpoint:** CLAUDE.md (§14 canonical date/time model, §15 source roster +
  M/D direction), DATA_BUILDING_BLOCKS.md (§3a canonical-date block B3a, source registry,
  §5 M-vs-D router note), the **nowtrendin2.0 skill** (CURRENT BUILD STATE section), and 11
  data/scoring agent skills (consistent "Canonical dates · sources · M/D" section).
- Memory: added `project-dark-matter-routing` (the platform_tier D-vs-M finding + gotcha).

### Open / Next (⏳ IN DESIGN — NOT shipped; gated by backtest-before-ship)
- **M/D provenance reweighting**, two coupled `_news_write` changes:
  1. Reputable ≠ automatic mainstream full weight → 1 reputable = ½, FULL only on ≥2 DISTINCT
     reputable (distinct `source_name`; the "Belgium vs Iran" case).
  2. Research/early-signal outlets (War on Rocks, Rest of World, Global Issues, Pew, RAND-blog,
     NBER) → Dark Matter via `blog_collectors` GHOST_FEEDS at **expert/niche tier** (NOT
     `_news_write`). Feeds validated (prod UA). Adversarial integrity verify + `backtest_dual_pathway.py`
     required before deploy.

### Hard decisions made
- The D-vs-M router is **`platform_tier`**, NOT `is_organic` (mapped across the engine). Routing
  research outlets through `_RSS_FEEDS`/`_news_write` would stamp them `mainstream` and SUPPRESS
  the early signal — so they must go through the blog/expert-tier path. (This corrected an earlier
  plan that had prepped them for `_RSS_FEEDS`.)
- Reputable-corroboration weighting extends the catch-all `CATCHALL_MIN_SOURCES≥2` philosophy from
  *admission* to *weight*; distinct-source counting must key on `source_name` to defeat wire syndication.

---

## Session 2026-06-20 (session 2) — Infrastructure audit + skill hardening

### Completed

- **Full infrastructure audit:** Confirmed both clients (web terminal + mobile) and backend
  all correctly point to the v2 engine (`nowtrendin-v2-engine-edcb10d44f91.herokuapp.com`).
  No discrepancies between platforms — single source of truth rule is working at the data layer.

- **Deploy skill rewrite (critical fix):** The old `/deploy` skill was pointing the engine
  subtree push to `heroku main` (the BACKEND remote) instead of `heroku-v2engine main`.
  This is what caused the accidental 1.0 engine deploy on 2026-06-19. Fixed and backed up
  to `docs/skills/deploy.md` in the repo.

- **`AI_GRADE_CLAUDE_MODEL` updated live on Heroku:** Changed from `claude-sonnet-4-5-20250929`
  to `claude-sonnet-4-6` on `nowtrendin-v2-engine` (Heroku release v69).

- **`docs/ENV_REFERENCE.md` created:** Complete map of every env var for both engine and
  backend — status (SET/MISSING), description, and exact fix commands for all gaps.
  Key finding: GUARDIAN_API_KEY is missing → Stage 4 mainstream media signal silently absent
  every scoring run; GDELT fallback is rate-limited on Heroku IPs.

- **`transfer/.env.example` + `backend/.env.example` created:** Local dev reference templates
  (key names only — no values). Standard practice to prevent onboarding confusion.

- **`/nowtrendin2.0` skill hardened:** Added INFRASTRUCTURE STATE section (audit results,
  what's correct, what was fixed, pending user actions with exact commands). Added PENDING
  USER ACTIONS quick-check to session startup. Fixed wrong engine URL that was in STEP 4
  health check (pointed to 1.0 frozen engine). Fixed wrong deploy topology table.
  Rule #9 added: API key values never go in Git.

- **`docs/skills/nowtrendin2.0.md` synced:** Cloud backup of the skill now matches local.

- All above committed and pushed: `6909737` + follow-up skill sync.

### Open / Next

- **GUARDIAN_API_KEY** (HIGH) — Register free at open-platform.theguardian.com/access.
  Without it, mainstream media (Stage 4) is absent every scoring run.
  Command ready: `heroku config:set GUARDIAN_API_KEY=<key> -a nowtrendin-v2-engine`

- **SECRET_KEY on backend** (HIGH — security) — Django using insecure hardcoded default.
  Generate + set: `heroku config:set SECRET_KEY=<key> -a nowtrendin-backend`

- **REDDIT_CLIENT_ID/SECRET/USER_AGENT** (MEDIUM) — Reddit signal not collected.
  Register at reddit.com/prefs/apps (free), set 3 vars on engine.

- **APIFY_REALTIME_ACTOR + APIFY_TRENDS_ACTOR** (MEDIUM) — Token set, actor IDs missing.
  Check Apify console for existing actor IDs.

- **GOOGLE_ANDROID_CLIENT_ID** (MEDIUM) — Android Google OAuth may fail.
  Retrieve from Google Cloud Console.

- **Velocity retention 365 days** — PENDING USER CONFIRMATION. Do NOT implement until explicitly confirmed.
- **Stripe + push notifications** — deferred, require custom dev client (off Expo Go).
- **NYT RSS feeds** — 39 live feeds identified as viable for topic extraction. Not yet implemented.

### Hard decisions made

- ENV_REFERENCE.md documents key names + status only — never values. Values live on Heroku only.
- Do NOT re-run the full Heroku config audit each session; check the specific PENDING USER
  ACTIONS list instead (saved in /nowtrendin2.0 skill INFRASTRUCTURE STATE section).

---

## Session 2026-06-20 (session 1)

### Completed
- **Web terminal UX:** Added X clear buttons to every filter input across all platforms (History search, Market chip-search, Grade GradedList search, Shell global search, mobile history/search/watchlists)
- **History tab reset:** Clicking "History" in the sidebar now remounts the component (historyNavKey counter) — clears filter + selection. Mobile uses `useFocusEffect` to clear on tab focus.
- **Screener — Trends table:** Centered all column headers. Added DIRECTION column (TrendingUp/TrendingDown/Minus icon) after Category.
- **Screener — Direction sort:** Direction column is now fully sortable (orange triangle, SortKey type extended, special-case comparator mapping gap→-1/0/1). Deployed to gh-pages.
- **Grade click-through fix:** Clicking rows in Graded Library (and History) now opens the full ProposedCard detail — `sel` state added to GradeList. Fixed smart-quote encoding bug in GradeList that broke the esbuild step.
- **Skill /nowtrendin2.0:** Created session-startup skill — reads all context, runs health + skills + agents checks, and enforces the GitHub-as-cloud-backup auto-save protocol.

### Open / Next
- **Velocity retention 365 days** — PENDING USER CONFIRMATION. Do NOT delete any velocity_scores rows until user explicitly confirms the rule change from 90→365 days.
- **Stripe + push notifications** — deferred, require custom dev client (off Expo Go).

### Hard decisions made
- Direction sort: `direction` is derived from `gap`, not a stored field — special-cased in the sort comparator rather than materializing a fake field on Row.
- GradeList encoding: Edit tool on Windows can introduce Unicode smart quotes; future mitigation is Python binary replacement for source files.

---

## Live URLs

| Surface | URL | Notes |
|---|---|---|
| **Web app** (use from anywhere) | https://nowtrendin-web-8c1bb8c9f7f2.herokuapp.com/ | Static Expo web build on Heroku app `nowtrendin-web`. Snapshot — rebuild with `./redeploy-web.sh`. |
| **Engine (FastAPI) — v2, the ONLY active engine** | https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com | Heroku `nowtrendin-v2-engine`. Deploy: `git subtree push --prefix=transfer heroku-v2engine main` from `NowTrendin v2.0/` (foreground). |
| ⛔ Engine 1.0 — **FROZEN, DO NOT DEPLOY** | https://nowtrendin-e62dcb9ecb69.herokuapp.com | Heroku `nowtrendin`. Legacy/frozen (live Android + pre-Apr-2026 data). A git hook blocks commits in `NowTrendin/`. The old `git push heroku HEAD:main` here caused the accidental 1.0 deploy on 2026-06-19 — never use it. |
| Backend (Django) | https://nowtrendin-backend-acb79c396814.herokuapp.com | Heroku `nowtrendin-backend`. Deploy: `git subtree push --prefix backend heroku main` from `NowTrendin v2.0/`. |
| Frontend source | `origin` (GitHub) | Expo Go phone preview needs same-WiFi LAN (`exp://192.168.68.52:8081`) + firewall rule for TCP 8081. |

Internal founder key (gated engine endpoints): `X-Internal-Key: nt-internal-7f3a9c2e5b81`

---

## What was built this session (2026-06-10)

### Data sources
- Added creators: Graham Stephan, TheGrahamStephanShow, Minority Mindset (join Meet Kevin, Andrei Jikh).
- Added 22 broadcast YouTube channels (CNBC, BBC, Bloomberg×3, Reuters, WSJ, FT, Al Jazeera, 60 Minutes, etc.) — mainstream tier.
- Yahoo Finance (RapidAPI) news as a genuine contributor; feeds BOTH the Trends pipeline and the Market (risk) pipeline.
- WhaleWisdom 13F institutional positioning (metered/trial tier — `holders` endpoint blocked until subscription upgrade; monitor `WHALEWISDOM_MONITOR.md`, review 2026-07-08).
- OFR Short-Term Funding Monitor (systemic leverage) + FINRA short interest, both instrumented in the founder `/usage` cost ledger.
- YouTube creators + broadcast + Yahoo Finance all feed both Trends and Market (free pulls).

### Integrity (HARD RULES — now enforced)
- Reputable-publisher **allowlist** on aggregated news (`_NEWS_REPUTABLE_SOURCES`) — only vetted outlets enter the corpus; non-reputable dropped with a logged count.
- **Provenance tiering**: broad/unverified news quarantined at ~1% weight, promoted to ~10% ONLY when independently corroborated — reputable corroboration → mainstream (M), dark-matter corroboration → Dark Matter (D). Uncorroborated never stands alone (excluded from scoring).
- **No circular metrics**: the N (Now TrendIn demand) component is DELIBERATELY EXCLUDED from the Gradient Score (Detection/Confidence/Overall) — the live engine composes from six external components (G/I/M/D/C/P), renormalized to sum to 1.0, so our own users' demand can never create a feedback loop. N is computed and shown as a SEPARATE community-demand signal. The Signal Convergence validator also uses N-independent factors. (A separate, demand-inclusive "Now Trending Gradient Score" what-if is shown only on the trend signal page, clearly labeled and never sold as the Gradient Score.)
- Measurement, not advice — neutral tiers, disclaimers everywhere.

### Engine / scoring
- **Signal Convergence** (`now_trending_direction.py`, `GET /convergence/{topic_key}`) — downstream directional validator: does raw volume + niche concentration confirm the Gradient Score's direction? (vs Gradient, vs Niche). Independent of N.
- **Dark Matter recalibration** — first-timer score now `100 * ratio^0.7` (was `ratio*160`, clipped at 62.5% → no high-end resolution). Tested across 12 cases.
- **VIRAL-with-0-signals fix** — evidence gate in `ai_topic_intelligence.py`: a recognized AI topic with < `AI_TAXONOMY_MIN_SIGNALS` (5) collected signals no longer floors to a measured-looking VIRAL score; falls back to raw score + no tier, so the score is consistent with the signal count shown.
- **Trend Beneficiary** (`trend_beneficiary.py` + `_wire.py`) — SanDisk-pattern exposure: is a company positioned to benefit from a detected trend, EARLY vs LATE in the cycle. `GET /beneficiary/{ticker}`. Auto-theme extension (`theme_extension.py`) promotes BREAKOUT/STRONG topics into the beneficiary THEMES.
- **Explainer bug fixed** — `topic_explainers.full` → `full_text` (`full` is a Postgres reserved word; was breaking the MORE INFO feature).
- Connection-pool leak fix (was 500-ing `/scores`).

### Market Signal (the "Market" section)
- **Baseline-relative dual score** (`market_signal_engine.py`) — Gradient-Score philosophy on market data, every component z-scored vs the item's own history. Detection (analyst + positioning) / Confidence (fundamentals + price). Neutral tiers ELEVATED/ACTIVE/BUILDING/ROUTINE/DORMANT. CALIBRATING until 3+ cycles.
- Grounded in real sources only (Alpha Vantage, FINRA, WhaleWisdom, Finnhub/beneficiary, OFR, SEC Form-4, creators/broadcast, sustainability) — rejected aspirational components (options flow, credit spreads, price candles we can't source).
- **Historical backfill** (`POST /market/backfill`) — seeded `positioning_concentration` from FINRA 180-day series (180 points, 15 companies). Finnhub fundamentals backfill returns 0 (free-tier limit).
- **Leverage Health** category (1–100, high = lower debt) from balance-sheet sustainability. Live for ~8 companies (Meta 100, Microsoft 91, Tesla 66, Morgan Stanley 40).
- Market tab UI now **mirrors Trends**: "Search Current Market Trends" bar, Pull Market Trends, "Market Signal" explanation (renamed from Positioning), category chips + stat tiles, focused `market-category/[key]` pages.

### Grade section
- 3 tabs: **New Grade** (only one that charges, "Grade · 1 token"), **History** (this member's grades, 12-month, search, no charge), **Graded** (all members' graded topics, search, no charge). Backend `GradeHistory` model + `/api/grade/history/` + `/api/grade/all/`.
- **Grade ↔ Market consistency**: grading a COMPANY now also pulls the full market data and attaches `market_signal` — the same Market read as the Market section (identical numbers). The AI attention estimate stays a separate, labeled read. (They measure different questions: attention trend vs market positioning.)
- Enterprise grade allowance bumped 1,000 → 100,000 (founder balance set to 99,997).

### App UI / homepage
- Homepage chip row + stat tiles unified from one source of truth (`CATEGORY_DEFS`): NowTrendIn (lead, brand-colored) + All + Breakout/Strong/Emerging/LowRisk/Anomalies. Each navigates to a focused `category/[stage]` page. Removed the static "What does this mean?" card.
- "Now Trending (N)" explanation added to Signal Detail (above Dual Score Analysis), with the real Volume/Recency formula.
- "Why the scores diverge" made LIVE (was static); Topic Maturity ("ESTABLISHED") clarified with the live `maturity_reason`.
- Heisenberg → **DUALITY** wording.
- "Other" tab → **Market**; new "Pull Market Trends" button (`/api/pull-market/` → engine `/risk/collect`).
- Detail pages moved under `(app)` so they get the bottom tab bar; non-primary routes hidden from the bar (only Home/Search/History/Alerts/Profile show).
- "Search" tab rebuilt as "Search A Topic" with 3 tabs (Trends/Market/Graded), each searchable.
- **Web desktop layout**: app centered in a 480px phone-width column; onboarding carousel width capped.

### Tooling (Claude Code skills in `~/.claude/skills/`)
`/deploy`, `/data-health`, `/risk-verify`, `/tier-gate-audit`, `/accuracy-sweep`, `/beneficiary-backtest`, `/expo-recover`.

---

## Scheduled / open items
- **2026-06-20** — 10-day integrity monitor (scheduled task): convergence, dark-matter recalibration, news provenance rates, Market Signal baselines filling in.
- **2026-07-08** — WhaleWisdom upgrade-analysis review (scheduled task).
- Market Signal reads **CALIBRATING** until per-component baselines build (FINRA seeded only 1 of 7 components; the rest accrue live). Watch on the monitor; option to extend the backfill (needs paid Finnhub) or relax the CALIBRATING gate.
- Non-watchlist companies graded via Grade show CALIBRATING market signal (no baseline history yet) — expected.

---

## Recovery cheatsheet
- Resume this thread (same machine): `claude --continue` (or `--resume`) in `NowTrendin v2.0/`.
- Move to another machine: copy `~/.claude/projects/C--Users-acinv-...-NowTrendin-v2-0/` (transcript + `memory/`) to the same path; needs identical project path for the hash to match. Otherwise rely on `git pull` + the copied `memory/` folder + this log.
- Update the web app after any frontend change: `./redeploy-web.sh` from `NowTrendin v2.0/`.

## Session 2026-07-05 (evening) — catch-all fix · Apify streamlining · weekly audit #3

### Completed
- **Weekly improve-system audit #3** committed (`audits/improve-system/IMPROVE_SYSTEM_2026-07-05.md`).
- **/monitor/catchall FIXED** (was 503/H12 since ~06-27). Three causes: (1) auditors measured the
  bare lexicon `_topic_category` instead of the serve-time `_category_for` (situation+context layers)
  — the 80.5%-vs-served gap was a measurement artifact; (2) unbounded latest-per-topic scan over the
  365-day retention classified every topic ever seen (H12); (3) full-table `topic_signals` scan on
  unindexed `extracted_at`. Now: serve-time classifier + `CATCHALL_WORKING_SET=6000` recent working
  set + explicit-key chunked corroboration (index seeks). Live: HTTP 200, catch-all 70.2% (4213/6000),
  floor STABLE, leak 20, 190 tracked calls in worklist.
- **Catch-all lexicon (Agent 6 worklist, founder-confirmed):** WC-2026 cluster (worldcup/mundial/
  golden boot/usmnt/haaland/manchester united/balogun/vozinha), youtube/whatsapp→tech,
  mamdani/zohran/mcconnell→politics, walmart/costco→business, zendaya/victor willis/adam sandler→ent,
  khamenei/ayatollah/america250/250th birthday/july 4th/mount rushmore/ukrainian/british→current_events.
  Policy held: bare countries/kelce/visa/america stay OUT (situation layer). 33/34 tests pass.
- **APIFY STREAMLINING (founder hard rule: ALL paid pulls at the 4×6h clock slots only):**
  sweep `interval+boot-fire` → `cron 0,6,12,18:45 UTC` (boot-fired paid sweeps eliminated — one per
  deploy + Heroku daily cycle); `_fetch_apify` now passes `&timeout=&memory=1024` on the run start and
  ABORTS on poll-budget expiry (the 10-min 0-result runs = the ~$93/mo compute line). Realtime confirmed
  clean 4×/day :30 (2× overrun gone). `trudax/reddit-scraper-lite` has NO engine refs; founder verified the
  console Schedules page is CLEAN → the $0.08 of trudax runs were one-off/pre-rotation, RESOLVED. Engine v200.

### Open / Next
- Watch Apify usage after v200 (expect ~$221→~$70-90/mo run-rate); then consider Scale($199)→Starter($49)
  plan downgrade — with fixed usage the Scale floor is oversized.
- ~~Set `COST_HEROKU_USD`~~ DONE (2026-07-05, engine v201): $64→$112 from the account-wide decomposition
  (engine Std-2X $50 + essential-1 $9; backend $12; preview/terminal/web Basic $7×3; frozen-1.0 PG $20).
  Cost Sentinel now honestly reads **$718.82 > $700 cap (critical)** — the old $64 masked the breach.
  Trim candidates flagged in COST_MODEL.md: archive+delete the frozen-1.0 essential-2 (−$20), review the
  possibly-redundant nowtrendin-web mirror (−$7); Apify v200 fixes (−$130-150 next period) restore headroom.
- Watch the post-Jul-7 Apify billing period: any trudax event would mean a live external caller (none expected).
- CLAUDE.md §3/§11 still document the pre-Aurora green palette; frontend/DESIGN_SYSTEM.md is the
  enforced contract — reconcile the docs.
- Watch: web-process boot log prints "collect+score every 30 min" vs the documented 6h cycle — verify
  COLLECT_INTERVAL_MIN env on the dynos.

### Hard decisions made
- Apify synchronization codified: no boot-fired or free-running paid actor runs; clock slots + explicit
  user request only (memory `project-ledger-sweep-apify` updated).

## Session 2026-07-06 (overnight) — INV-1 serve fix · mobile parity · self-healing DB pool

### Completed
- **INV-1 serve-consistency FIX (engine)**: web and mobile trends didn't match — SAME database,
  divergent serve paths on STALE rows. /scores re-ran live calibration (incl. the AI floor) on
  payload-less rows; on a row last scored 4 days prior that re-application inflated stored 35.6 →
  served 100 ("coding agent" + "agent memory" + "openai-codex" ranked above today's fresh signals on
  mobile while the web grid showed them mid-pack). Rows older than `SERVE_LIVECAL_MAX_AGE_H` (48h)
  now serve STORED values exactly like /topics. Serve-path only — no stored score changed.
- **Mobile TRENDS chip row restored** (founder request): Now TrendIn / All Signals / Breakout ≥85 /
  Strong ≥70 / Indicating / Marginal / Anomalies — from `CATEGORY_DEFS` (already web-consistent),
  Aurora pill style, COMBINES with the category row like the web. (Aurora had dropped the row.)
- **Mobile per-row category chip** on TrendCard (PLATFORM · STAGE · AGE · CATEGORY) — web parity §17/B8.
- **Mobile Accuracy Ledger zeros FIXED**: fetchAccuracy() mapped extinct snake_case fields
  (total_predictions/led_count/hit_rate_pct/…) while /accuracy/ledger serves camelCase → every metric
  undefined → `?? 0` wall of zeros. Now camelCase-first with fallbacks; verified against the live
  payload (10% / 70 resolved / 7 LED / 11d median / 821 pending — identical to web). "PREDICTIONS" →
  "RESOLVED" + pending-in-flight line (honest denominators). Preview redeployed ×3 through the night.
- **Self-healing PG pool (db_compat, 12/12 behavior-tested)** after the /scores outage: psycopg2's
  pool has NO reclamation — getconn() hands out server-killed conns; first use raises; no-try/finally
  call sites orphan the slot FOREVER (server sat at 2/20 while every request raised PoolError; plain
  restarts re-poisoned at each boot burst; `pg:killall` under live dynos made it worse). Fixes:
  SELECT-1 checkout probe (dead conns discarded, never handed out), broken-conn discard on close,
  bounded DIRECT fallback (PG_DIRECT_MAX=4 — reads keep serving while exhausted), auto pool-REBUILD
  after 90s persistent exhaustion, try/finally on _compute_scores_full/_compute_topics_full.
  PG_POOL_MAX=12. New rule: NEVER pg:killall while dynos run.
- **Docs updated**: CLAUDE.md footer + §13 catch-all measurement rule; AGENT_CHARTER G4 (stale-row
  serve rule) + G5 (pool reclamation); DBB §1/§7 (clock-slot rule, true costs); COST_MODEL Apify line;
  nowtrendin2.0 skill build state.

### Open / Next
- Confirm /scores recovery on the pool-fix release (monitor armed); then verify coding agent serves
  stored 35.6 on both surfaces.
- Apify Scale→Starter downgrade after ~a week of post-fix usage data.
- Founder decisions: archive+delete frozen-1.0 essential-2 Postgres (−$20/mo); retire nowtrendin-web
  mirror if redundant (−$7/mo).
- Reconcile CLAUDE.md §3/§11 palettes with the Aurora contract (frontend/DESIGN_SYSTEM.md).
- try/finally sweep of remaining get_db() call sites (the pool now self-heals, so lower urgency).

### Hard decisions made
- INV-1 sharpened (Charter G4): never re-calibrate a stale row at serve time.
- Pool operations rule (Charter G5): psycopg2 pool slots are unrecoverable by design — engineering
  must guarantee return-or-discard; pg:killall is forbidden under live dynos.

## Session 2026-07-06 (day) — read-path outage POST-MORTEM + /engine-recovery skill

### The outage in three phases (~12h of /scores 500s; full runbook now in /engine-recovery)
1. **Poisoned client pool** — pg:killall/restarts left dead conns that getconn() handed out;
   first-use raised; no-try/finally sites orphaned the slots (PoolError with the server at 2/20).
2. **Saturated server role cap** — the first rebuild design left wedged holders' conns alive;
   repeated rebuilds stranded slots to 20/20 (FATAL too-many-connections; even collect/score failed).
3. **Wedged prewarm (the invisible one)** — the synchronous warm loop sat 6.3 HOURS blocked inside
   one scores build; no cache ever warmed; every client request cold-built the superset — a
   self-sustaining thundering herd. Freed by the (dyno-down) killall; it immediately warmed 6/7 feeds.

### Hardening shipped (engine v205/v206 + config)
- db_compat self-healing (probe / broken-discard / bounded DIRECT fallback / closeall-REBUILD /
  OperationalError-on-growth retried) — 12/12 behavior-tested.
- `PG_POOL_MAX` 12→**8** (my own 12 bump had eroded the deliberate headroom; engine now ≤12 of 20).
- try/finally on _compute_scores_full/_compute_topics_full.

### Process lessons (encoded as /engine-recovery PRIME DIRECTIVES)
- Read the error SIGNATURE before acting — each phase had a different cause; the fix for one
  worsened another. My own interventions (probing storms, killall under live dynos, restart storms)
  EXTENDED this outage. Triage once, act once, hands off.
- Never probe a cold /scores repeatedly (each probe launches another build) — poll /prewarm instead.
- pg:killall only with dynos scaled to 0.
- A wedged prewarm is visible ONLY via /prewarm last_run age → recommended engine follow-up
  (founder-confirmed deploy): pipeline_integrity alarm on scores-cache-absent + prewarm-stale >3×interval.

### Scoring impact (honest)
- Read-path only for most of the window; during the phase-2 saturation some collect/score cycles
  errored (log: "collect/score phase error", ~13:49 window) — a bounded data gap of a few cycles.
  Ledger + retention unaffected. Collectors resumed automatically each subsequent slot.

### New skill
- **/engine-recovery** — signature table (fast-500 PoolError / FATAL too-many / H12-cold / wedged
  prewarm) + safe recovery sequences + verify/log steps. Roster updated in /nowtrendin2.0.

### Addendum 2026-07-06 — PULL-SYNCHRONIZED PREWARM (founder rule)
- Prewarm now fires `PREWARM_AFTER_PULL_S` (60s) after EVERY data pull completes: end of the
  score phase (6h scheduled cycles + failover; cloud/API process only — local worker's cache
  isn't the serving one) and the `/collect` user pull. Serving caches carry fresh scores the
  moment they exist (was: up to 25 min later on the loop). Warms are now OVERLAP-GUARDED
  (one at a time; stacked kicks no-op — the thundering-herd lesson). The 25-min loop stays
  as the TTL safety net. AGENT_CHARTER Agent 15 spec updated.

## Session 2026-07-06 (late) — repo root cleanup (untracked clutter)

### Completed
- Researched all 38 untracked items, then fixed by category (commit 152147c):
  - **Gitignored**: `.ghpages-deploy/` + `web-deploy-terminal/` (deploy staging clones with
    their own .git), `__pycache__/`/`*.pyc`, `transfer/anomaly_detector.db`, and the personal
    `revised PTCS on Coffe.pdf` (kept local, non-project).
  - **Deleted (regenerable scratch)**: 10 diagnostic curl/DB dumps (ana_crypto/crypto_check/du/
    hist/ledger_detail/pg/risk_check/sc_tmp .json, gt_rss.xml, the broken-redirect
    "C:Tempnyt_economy.xml" NYT RSS sample, transfer/fmp_hist.json) + 3 dated `_06_17_26`
    diagnostic drafts — verified superseded by the TRACKED canonical
    `transfer/{market,trend}_signal_diagnostic.py` (dated ones were the pre-wiring
    standalone versions).
  - **Committed deliverables**: 2026-06-23 audit PDFs → `audits/`; pitch deck →
    `docs/business/`; 4 Jun-15 design mockup HTMLs → `docs/design-mockups/`; Alpha-Engine
    Phases 1-3 + Developer Punch List + nightly-agent moat charter MDs → `docs/`.
  - **Committed `_audit_work/`** (provenance for the two audit PDFs) after a secret scan —
    all "token/secret" matches were prose, no credentials.
- Also committed the pending AGENT_CHARTER.md Agent-15 spec update (aa846e3).
- `git status` now fully clean.

## Session 2026-07-06 (night) — batch-paced pipeline CONFIRMED LIVE + full agent health check

### Batch-paced pipeline (founder rule) — implementation confirmed, docs closed
The three pacing commits (2955260 batch-paced collect+score, aa802ed single-flight supersets,
530b0f4 prewarm feed pacing) are LIVE on the engine; docs were lagging — AGENT_CHARTER had it,
SESSION_LOG + CLAUDE.md did not. Both now updated (CLAUDE.md §13 new BATCH-PACED PIPELINE bullet).
Confirmed in `transfer/gravitational_anomaly_detector.py`, env-tunable, NO overrides set on
Heroku → defaults live:
- Scorer: `SCORE_BATCH_SIZE`=100 per batch + `SCORE_BATCH_PAUSE_S`=10s between batches.
- Collectors: `COLLECT_SOURCE_PAUSE_S`=10s between sources.
- Prewarm: `PREWARM_AFTER_PULL_S`=60s after EVERY data pull (the founder 60s warm rule) +
  `PREWARM_FEED_PAUSE_S`=10s between the 7 feed builds; overlap-guarded.
- Single-flight `_get_or_build`: observed live — prewarm reported scores feed
  "busy (another build in flight)" instead of launching a second build. Working as designed.

### Full agent + data-pull health check (2026-07-07 ~02:45 UTC)
- **No data leaking, scoring active and clean.** Scorer heartbeat 3.3 min (cloud); pipeline
  integrity OK — 0 stale serve payloads (INV-1 fix holding), 0 dupe groups, 0 junk singles,
  serve-consistency 40/40. Datecanon: 16 columns audited, **0 non-canonical values**.
  Catch-all: 38.3% served (down from 70.2%), floor STABLE, single-source leak 3 (delta −5,
  improving). Fragments 0.
- **Collectors 15/17 HEALTHY**, all critical healthy (trust=true). DEGRADED (ran, 0 signals):
  `github` (token configured — investigate) + `reddit` (expected — keys deferred).
- **Cost Sentinel back under cap: $497.89 / $700** (was CRITICAL $718.82) — the Apify
  clock-slot fix landed (Apify live-metered $0.96 this period). X posts 16.9% of budget.
- **Prewarm** pull-synchronized + healthy; all 7 feeds warm (scores 2522 · topics ~1860 ·
  history 7d/24h/12h 2000 · risk ~290 · crypto 12).

### Warns to action (none are leaks; all flag-never-force worklist)
1. `github` collector DEGRADED — runs but 0 signals for ~1h+; check token/API response shape.
2. **Datecanon B3a: 8 undeclared `*_date` columns** — the NEW crypto + market ledgers
   (crypto_accuracy_ledger.detection_date/move_date, crypto_pending_detections
   .detection_date/timeout_date, market_accuracy_ledger + market_pending_detections same) were
   never registered in DATE_SEMANTIC. The auditor's auto-discovery working exactly as designed;
   classify + register them.
3. **Catch-all auditor: 52 TRACKED calls (ledger/pending) stuck in catch-all** — reclassify
   worklist (visa, United States, trillionaire, …); policy: situation layer routes bare
   countries/visa, so route via lexicon/situation review, not blind lexicon adds.
4. Calibration auditor reads evaluated=0/pending=0 in ITS window while /accuracy/ledger serves
   821 pending / 70 resolved — likely a scoped-window read in the auditor, worth a look so its
   small-sample guardrail reflects the real ledger denominators.

### Open / Next
- Investigate github collector 0-signals; register the 8 crypto/market ledger date columns;
  work the 52-tracked-calls reclassification list; check calibration auditor's ledger read.

## Session 2026-07-07 (early) — the 4 health-check warns: researched + fixed (engine deployed ×2)

### 1. github collector DEGRADED — ROOT CAUSE: expired/revoked GITHUB_TOKEN (HTTP 401)
Tested the live Heroku token directly: 401 on /rate_limit AND /search — the 93-char length
says fine-grained PAT (they expire; 90-day default). `collect_github` silently `continue`d
on non-200 → the invisible 0-signal runs. FIXED in code (2185e0f): on 401 the collector now
logs once + retries UNAUTHENTICATED (10 req/min; existing 403 handler absorbs the tighter
limit) so github signals degrade gracefully instead of vanishing; non-200s now logged.
USER ACTION: rotate GITHUB_TOKEN (classic PAT, no scopes, no expiry recommended) — set it
directly in the user's own terminal (never paste a token into a Claude transcript — the
APIFY_TOKEN lesson). Same env var also feeds gradient_engine_backend + research_history.

### 2. Datecanon 8 undeclared *_date columns — registered + classified (2185e0f, fd96200)
detection_date/move_date on market/crypto accuracy ledgers registered in DATE_SEMANTIC
(writers already canonicalize via to_iso_date — 0 non-canonical). First deploy exposed the
right finding: the 3 *_pending_detections.timeout_date columns hold computed deadline
INSTANTS ((detection+TIMEOUT_DAYS).isoformat(), consumed via now > _parse()) — classified
onto the auditor's OPERATIONAL allowlist exactly like the attention ledger's
pending_detections.timeout_date (already there). NO data rewritten (forward-only honored).
VERIFIED live: datecanon status ok — 14 columns, 0 non-canonical, 0 undeclared.

### 3. Calibration auditor 0/0 — key-name mismatch (2185e0f)
It read the /accuracy/ledger ENDPOINT's renamed keys (total/pending/hitRate/smallSample)
off the RAW generate_honest_report dict (sample_size/still_pending/honest_hit_rate_pct/
small_sample_warning) → always 0/0 + phantom small-sample warn. Same bug class as the
mobile camelCase ledger zeros. Now reads raw keys with endpoint-name fallbacks.
VERIFIED live: calibration_auditor ok — evaluated=70, pending=821, hit_rate=10.0.

### 4. Catch-all 52 tracked calls — classified worklist (flag-never-force, NO changes applied)
Auditor caps examples at 15; classification of the visible set:
- POLICY-ROUTED (stay out of lexicon; situation layer handles): United States, the us, visa.
- OLD JUNK PENDINGS (generic words predating the fragment gate; correctly catch-all —
  resolve via the 365d patience-window timeout, NO action): trillionaire, sonny, socialists,
  secretive, scrambling, scanner, rewriting, programmers.
- LEXICON CANDIDATES (founder sign-off; precedent = youtube/whatsapp adds): reddit → tech;
  Roman Safiullin → sports (haaland/balogun precedent); phi + pegasus AMBIGUOUS (greek
  letter / mythical name over-match risk) — recommend skip.
Founder decision pending before any lexicon change.

### Open / Next
- USER: rotate GITHUB_TOKEN on nowtrendin-v2-engine (steps given in chat).
- Founder: approve/reject the 2 lexicon candidates (reddit, Roman Safiullin).
- source_watchdog github warn clears at the first collect slot after token rotation
  (or degrades gracefully unauthenticated meanwhile).

### Addendum 2026-07-07 — GITHUB_TOKEN rotated + verified (closes warn #1)
Founder rotated to a classic no-scope, no-expiry PAT. Gotcha: the dashboard config-var
field got the ENTIRE command line pasted as the value ("heroku config:set GITHUB_TOKEN=…"),
so auth still 401'd — extracted the embedded 40-char ghp_ token and re-set it cleanly
(engine v214; value never displayed). VERIFIED: /rate_limit HTTP 200, search quota 30/min,
live search probe 200. github collector confirms at the next 6h collect slot.

## Session 2026-07-07 — six agreed fixes shipped (engine v215/27740ae) + ledger truth surfaced

### Shipped + verified live
1. **Grade clamp**: `_num` bounds every AI-returned component to [0,100] (required-key C9
   guard was already present — audit finding stale).
2. **N detail fields FIXED**: /scores/{topic} recomputes queries_30d/24h/daily_rate fresh
   from topic_queries (never persisted in velocity_scores — the "No internal query history
   yet" at N=100 bug + the N-degenerate scoringcontract finding). VERIFIED: coding_agent
   N=73.5 now shows 313 queries/30d with a real narrative.
3. **Observable calibration swallows**: the last two silent apply_calibration except:pass
   (direct-query path + history-row calibrator) now log + stamp calibration_errors.
4. **risk_stage vocab**: verified ALREADY fixed (_RISK_TO_MARKET_TIER at write site).
5. **Legacy weights**: verified ALREADY fixed (calibration_engine imports scoring_weights).
6. **LEDGER first-crossing enrollment + pre-broken segmentation** (held-out,
   measurement-only, no stored rows touched):
   - Enrollment: first-seen ≤ LEDGER_ENROLL_RECENT_DAYS(14) + floor crossing, excludes
     ESTABLISHED/MONITORING (fail-open if topic_maturity absent), newest-crossers-first —
     replaces leaderboard top-N (structurally LAGGED).
   - Report: LAGGED split near-miss vs pre_broken (breakout >7d before first sighting);
     new tracked_race_hit_rate_pct. **First read: 44/59 lagged were PRE-BROKEN cold-start
     rows; tracked-race hit rate 26.9% (7/26) vs blended 10%** — the honest race-level
     read of the before-it-arrives claim. Both rates served; nothing hidden.

### Open / Next
- Enrollment change takes effect at the next enrollment run — watch the pending pool's
  composition shift toward fresh crossers over the coming days.
- Remaining strategic ledger items (not yet built): canonical-query resolution before
  sweeping (the "mexico" ambiguity), second referee corroboration (referee_wikipedia),
  LED-vs-LAGGED detection-time feature mining, GHOST_FEEDS Dark-Matter expansion
  (backtest-gated), positioning floor-pin omission (backtest-gated).
- Founder: lexicon candidates (reddit → tech, Roman Safiullin → sports) still pending.

### Addendum 2026-07-07 — match-validity metadata + feature mining (engine 7ca65c7)
- **Sweep match-validity shipped**: accuracy_ledger + sweep now record sweep_query,
  query_ambiguous (single word / bare geo = weak Trends match), and referee_corroborated
  (INDEPENDENT Wikipedia-pageviews referee on LED/SAME_DAY wins, ±14d of breakout,
  fail-open). /accuracy/ledger serves ledCorroborated/ledUncorroborated/ledUnchecked/
  ledAmbiguousQuery; best[] carries both flags. Existing 7 LED wins honestly "unchecked"
  (resolved pre-metadata). Verdicts/scores untouched.
- **LED-vs-LAGGED feature mining** (read-only, audits/ledger-research/
  LED_FEATURE_MINING_2026-07-07.md): D=0 at first sighting for winners AND near-misses
  but 40 for pre-broken → current Dark Matter is late-confirmation, not early-warning —
  empirical case for GHOST_FEEDS expert/niche expansion. LED median M=80 vs near-lag 50
  (breadth-at-first-sighting separates winners). Median near-miss loss ≈ −4d; 5/15 lost
  by 1–2 days → fast-lane recheck plausibly flips them. Small samples; directional only.

### Open / Next
- Backtest-gated queue (founder sign-off to start): GHOST_FEEDS expert/niche outlets;
  breadth-at-first-sighting enrollment priority; free-source fast-lane recheck;
  positioning floor-pin omission.
- Re-run feature mining when the first-crossing enrollment cohort resolves.

### Addendum 2026-07-07 — Accuracy Ledger PAGE updated (pre-broken + tracked-race + referee), live on gh-pages
- Engine: /accuracy/ledger/detail now serves sweep_query/query_ambiguous/referee_corroborated
  + a SERVER-computed pre_broken flag (one definition, same grace as the report) — 658bdf3.
- Web terminal (deployed gh-pages 93cde0c, bundle index-Bxi-S792.js, verified serving):
  filter chips All/Led/Same day/**Lagged · near miss**/**Pre-broken**/False positive;
  stat strip adds **Tracked-race hit rate 26.9%** beside the unchanged blended Honest 10.0%,
  breakdown 7/4/15/44/0 (near + pre-broken = lagged, nothing hidden), **LED referee check**
  card (0✓ · 0– · 7 unchecked — honest: old wins predate the metadata); PRE-BROKEN verdict
  chips w/ tooltip; wins carry wiki-referee status; ambiguous terms marked "broad term";
  plain-language banner. Integrity-first: honest rate still counts every resolution.
- Verified in preview (temp local auth stub, REVERTED before build/deploy — 0 traces,
  bundle hash identical to clean build): cards reconcile with the API exactly; Pre-broken
  filter → 44 rows, Near-miss → 15; zero console errors. tsc clean.
- Desktop inherits via the web build (§12). ⏳ Mobile parity: the Aurora Accuracy Ledger
  screen still shows the pre-split summary — add trackedRace/near/pre-broken lines +
  /deploy-mobile-preview (next parity task).

### Addendum 2026-07-07 — 3-platform ledger parity COMPLETE (mobile chips + segmentation deployed)
- Mobile (97f1397, preview release 512efb4): Accuracy Ledger screen now has the web's
  chip rows — LEDGER mode (Attention·Trends / Money·Market / Crypto·Coin, lazy-loaded)
  + verdict filters (All/Led/Same day/Lagged·near/Pre-broken/False positive; price
  ledgers Confirmed/Not confirmed/No move) — Aurora pill style, tokens only. Metrics
  add TRACKED-RACE beside blended HIT RATE; honest breakdown + LED-referee lines +
  pre-broken explainer; NEW filterable row list (/accuracy/ledger/detail, windowed 30,
  server-computed pre_broken, wins carry wiki-referee status, 'broad term' markers).
- Deployed via /deploy-mobile-preview: gate + DB-target + new-UI strings verified in
  bundle BEFORE push; live checks pass (PIN page w/o cookie, 401 wrong PIN, app +
  TRACKED-RACE served with cookie). Parity: web gh-pages ✓ · desktop (inherits web) ✓ ·
  mobile preview ✓ — §12/§17 satisfied for the ledger.

### Addendum 2026-07-07 — Ledger Entry Analysis panel (per-row information panel, 3 platforms)
- Engine (9687133): signal_analysis.py gains kind='ledger' (_ledger_entry) — deterministic,
  formula-confidential analysis of ONE ledger row: what the entry records · HOW the tracking
  method works (canonical detection date, Trends curve detection→now, sustained-surge breakout
  vs own baseline [thresholds proprietary], asymmetric match window, 365d patience, independent
  wiki referee) · what THIS verdict means (honest per-verdict copy incl. PRE-BROKEN + excluded
  LATE_REDETECTION) · match validity (broad-term + referee; pre-metadata rows say so) · track-
  record context. POST /analysis/ledger; reads snake_case AND camelCase rows. Live-tested.
- Web (e5f6886 → gh-pages 9126262): click any attention-ledger row → SignalAnalysisPanel
  (kind widened) expands beneath it. Preview-verified: all 5 sections render w/ real facts,
  0 console errors (auth stub reverted before build — 0 traces).
- Mobile (cf26d4e → preview d4539a6): tap a ledger row → same panel; 'Tap for the full entry
  analysis' affordance. Bundle checks (gate/DB/new-string) passed pre-push; PIN gate verified.
- NOTE: deterministic composition per the enterprise standard (reproducible, no model
  inference, no per-view AI cost) — the "AI prompt" ask is satisfied by feeding the tracking
  method into the same held-out analysis engine that powers the trend/market/crypto panels.

### Addendum 2026-07-07 — founder-approved disclaimer EVERYWHERE (verbatim, sign-off required to edit)
New copy: "*All information contained herein may not be accurate including any and all figures
indicated in this section and or site and may be an approximation and should not be construed as
financial, investment, or legal advice."
- Engine (5d1ed35): signal_analysis _DISCLAIMER → all 4 analysis panels (trend/market/crypto/
  ledger) on every platform, no client rebuild needed. Crypto keeps its appended caveat.
- Web (f680a52 → gh-pages ce87964): LEGAL_DISCLAIMER constant + 4 inline copies (Shell footer,
  Crypto/MarketSignal/Screener AI-overview lines). Trend + market rails verified TOP AND BOTTOM
  (2 legal-disc per rail), old text gone site-wide, 0 console errors.
- Mobile (f680a52 + c200e4f → preview 76b8bdf): Disclaimer component + TopicResearch caveat;
  signal/[id] + risk/[key] detail panels now carry it top AND bottom. Bundle check:
  newdisc 2 / olddisc 0 / gate intact.

### End-of-day 2026-07-07 — docs/skills sync + AI-Context root cause (founder to bed)
- **AI Context NOT loading — ROOT CAUSE: Anthropic API account credits EXHAUSTED.** Every engine
  Claude call returns 400 "Your credit balance is too low to access the Anthropic API." Affects
  NEW topic definitions (AI Context) + the Grade tool's Claude synthesis stage; CACHED explainers
  still serve (why some topics show context). NOT the engine budget (Cost Sentinel AI line is
  $0.92/$20 this period) — it is the prepaid balance at Anthropic. FIX (founder):
  console.anthropic.com → Plans & Billing → purchase credits. Recovers immediately, no deploy.
  (Probed all model names with the live key — all 400 with the credit message, so not a model
  retirement; AI_GRADE_CLAUDE_MODEL=claude-sonnet-4-6 as configured.)
- **Docs updated**: CLAUDE.md footer → 2026-07-07 block (ledger truth layer, match validity,
  3-platform ledger UI + entry-analysis panel, hardening, disclaimer, ops, ⚠ Anthropic credits).
  §14 already carried the enrollment/pre-broken rule from earlier today.
- **Skills updated**: /nowtrendin2.0 CURRENT BUILD STATE → 2026-07-07 (+ the Anthropic-credits
  PENDING USER ACTION at the top); /accuracy-sweep report structure → publish BOTH rates
  (blended + tracked-race) + match-validity section + preBroken-vs-laggedNear failure modes +
  ACCURACY_LOG line format extended.
- **Memory saved**: project-ledger-match-validity (first-crossing enrollment, pre-broken split,
  tracked-race, wiki referee, D-is-late-confirmation finding) + MEMORY.md index.
- NOTE: founder's last screenshot showed the OLD disclaimer — that tab was on a cached bundle;
  gh-pages verified serving the new one (hard refresh fixes).

### Addendum 2026-07-07 — Market Signal rail: AI Context section added (712a739 → gh-pages ba66731)
Trend-rail parity (§12): same /explainer source-aware definition, first section under the
score gauges. Preview-verified (renders first, 0 console errors). Shows the honest placeholder
until the Anthropic account credits are restored (then generates on first view + caches).
Optional follow-up: mobile risk/[key] has no AI Context equivalent either — add for full parity.

### RESOLVED 2026-07-07 — Anthropic credits restored, AI Context LIVE
Founder purchased credits. Verified: /explainer generates for both a trend topic
(firm_blackcore) and a market instrument (alphabet — the new Market Signal AI Context
section). Definitions generate on first view + cache; Grade Claude stage restored too.

## Session 2026-07-07 (cont.) — research-outlet onboarding VALIDATED + lexicon verified (engine e32a59c)

### GHOST research feeds — §16 five-gate run + held-out validation (the "backtest")
- **Integrity finding that changed the design:** the generic blog n-gram extractor FAILS the
  FORMAT gate on editorial titles — filler fragments ("gathering clouds building") and NBER
  AUTHOR NAMES ("ulrike malmendier stefan") SURVIVE `_is_quality_topic`, and expert-tier
  signals are EXEMPT from the corroboration floor → junk would enter scoring at the
  highest-trust tier. Shipping as originally designed would have violated the integrity standard.
- **Fix built:** `research_entity_topics()` — entity-anchored extraction (capitalized runs
  holding a non-common-dictionary word; edge-trim floor of 2 words; standalone-proper-noun
  singles only; no entity → write NOTHING). Iterated 3× against live feeds until precision
  ~80%+ (real entities: shin bet, taliban rule, venezuela humanitarian, texas screwworm,
  deterring russia, temu). `_parse_rss` ET fallback made namespace-agnostic (Atom bug).
- **Verdicts:** WoR / Rest of World / Global Issues / RAND **PASS**; **NBER FAIL** (2nd
  documented failure); **Pew FAIL as-is** (Methodology/Acknowledgments sub-pages in feed).
- **Premise test:** 51/59 clean topics NOVEL to velocity_scores — the outlets genuinely see
  what the engine doesn't (matches the D-is-late-confirmation mining finding).
- **Shipped flag-gated OFF** (`GHOST_RESEARCH_FEEDS=0`); founder flips after reviewing
  audits/source-onboarding/RESEARCH_FEEDS_VALIDATION_2026-07-07.md → recommend a 2-week
  monitored trial (topic-quality + catch-all auditors). Rollback = unset the flag.

### Lexicon adds — verified against real data before applying
- **safiullin → sports APPLIED + LIVE-VERIFIED** (roman_safiullin now serves sports): the
  topic's OWN signals are 8/8 tennis (Wimbledon/Guardian Sport/"safiullin tennis"); overmatch
  checks pass (russia/roman empire/saffron unchanged).
- **reddit NOT added — the add would have been redundant:** serve-time `_category_for`
  already returns technology (context/situation layers route it). Verified live before
  touching the lexicon; adding it would have been unverified drift.

## Session 2026-07-07 (Board) — Advisory Board created + branch A-G reviewed, fixed, merged flags-OFF
- **/advisory-board skill created** (6 independent archetypes: Challenger, First-Principles
  Guardian, Expansionist, Outsider VC/Banker, Executioner, Economist w/ founder-specified
  canon — 12/12 source texts access-verified, incl. founder-provided Bogle/Bernstein/R&R/
  Belsky-Gilovich local files; Bogle needs render-to-image, method recorded in the skill).
- **Branch integrity-recs-A-G**: 7 recs implemented flag-gated OFF; six independent board
  memos (audits/board/BOARD_integrity-recs-A-G_2026-07-07.md). Board caught 2 real defects:
  F was a near-no-op (3 stage-write sites) and D's INSERT omitted calibration_multiplier
  (transient inflation). Both fixed per board conditions + Challenger's no-lookahead basis
  + E cooldown + B shadow log + policy stamps.
- **Merged flags-OFF (fe2cefc), deployed (72285bb), zero behavior change verified.**
- **A DECIDED: no reweight** (AUC noise); re-run at ≥30 post-fix races.
- **INVERSION SOLVED**: as_of_detection_days = 0–1 for ~all ledger topics — the 2.3%-vs-24%
  maturity inversion is a hindsight-classification artifact, not a thesis failure.
- D-weight backtest results + D dry-run distribution: 698 EST / 156 EMERG / 80 NEW.
- Remaining: 6 sequenced flag flips = per-item Chairman decisions (listed in board record).

## Session 2026-07-07/08 — ALL SIX CHAIRMAN-AUTHORIZED FLIPS EXECUTED (pre-registered)
Pre-registration doc: audits/board/FLIP_PREREGISTRATION_2026-07-07.md (success metrics,
review dates 07-14/07-21, revert conditions — written BEFORE flipping, per the Economist).
- Preconditions run first: B shadow review (12,851 would-block topics = tag-mash junk →
  the moat exemption was a junk highway; PASSED) · G real before/after diff (32 pinned
  instruments: delta 0.00 everywhere, 0 still pinned, all now honest n/a; PASSED).
- Flipped (engine v222, one restart): E sweep newest slots=2 · C N-dedup 10min ·
  B moat-strict · G positioning quarantine · F stage-from-detection.
- D write: 952 topic_maturity rows (calibration-neutral; coverage 3→76; headline rates
  unchanged 10.0/26.9; tagged rollback).
- F/G announced: "Definition changes" section on Methodology (gh-pages cf70abf).
- Policy stamps live on /accuracy/ledger (paramVersion/sweepNewestSlots/maturityBasis).
- ⚠ 7th decision surfaced to Chairman: LEDGER_MATURITY_AT_DETECTION (early cohort now
  honestly exposes the hindsight artifact: 0/8 EMERGING vs 7 wins in ESTABLISHED).
- Review dates: 2026-07-14 (E/C/G/F), 2026-07-21 (B). Watch: catchall_floor_log after
  the next scoring cycles (B is a major scoring-pool cleanup — expect junk drop).

## Session 2026-07-08 — Board Review #2 complete (execution audit + system-wide feedback)
Six independent memos collated → audits/board/BOARD_system-feedback_2026-07-08.md.
Executioner verified 7/7 flips real in code + live config ("no near-no-op this cycle").
CRITICAL new findings: fabricated ~22%/<9% FP claims LIVE in UI/API (purge first);
nonstationary ground-truth instrument (persist curves per resolution); referee
corroborates breakout-not-lead (+ 7 LED wins unchecked — 1-2h sweep); date_utils
%m/%d/%Y silent locale mis-parse; P self-reference; win definition unpinned;
market/crypto confirm rates need null baseline; G's trend half unshadowed (G-2) +
n/a population reconciliation (G-1); B unmetered while ON (register needed);
7's basis computed live over pruned table (stamp at resolution). Consensus queue of
15 actions awaiting Chairman ruling; 07-14/07-21 review homework pre-registered.

## Session 2026-07-08 (cont.) — Chairman-ruled fixes 1-6 + GHOST flip executed (engine 4a31fc7/v226, gh-pages cc8a6cb)
Chairman clarifications RECORDED in the Board's permanent ground rules: (a) P = persistence
of EXTERNALLY-collected signals (composite-legitimate) vs N = platform-internal (excluded);
(b) calibration = accuracy-tuning against real data, never "manipulation".
1. **FP-claim purge**: fabricated ~22%/<9% strings removed from detector payload,
   market_signal_engine, nowtrend_integration (+docstrings), web Screener gauges
   ("speed · early / leading read" / "precision · corroborated read"). Mobile was clean.
   Verified live: fields gone from /scores/{key}.
2. **Referee fixed to corroborate the LEAD** (wiki arrival BEFORE detection = contradiction)
   + SWEEP RUN on all 11 wins: **1 corroborated (Daveigh Chase, same-day) · 7 not
   corroborated (incl. mexico +17d, court rulings +16d — no matching wiki arrival) ·
   3 unresolvable**. Served live: LED wins now read 0✓/5–/2·, 5 ambiguous-query.
   HONEST READ: no LED win currently carries independent corroboration — the
   Challenger's ambiguous-term warning was correct. (Referee limitation noted:
   steady-state wiki pages never "arrive"; uncorroborated ≠ proven false.)
3. **Trend-side quarantine diff**: 6000 stored rows scanned — ZERO NULL components →
   the trend path is empirically INERT; no flag split needed (G-2 closed with data).
4. **Basis stamps**: at_detection_days + pre_broken columns added; sweep stamps at
   resolution; 76 existing rows backfilled; report prefers stamps (pruning-proof);
   paramVersion now calib-params-v3|patience365|lead365|match30|preb7|estmin14 (live).
5. **moat_blocked_log register**: every strict/shadow block persisted; unblocked_at
   stamps delay; 90d age-out; B's revert condition now falsifiable.
6. **date_utils locale fix**: US-canonical slash parsing; unambiguous EU day>12 accepted
   + normalized; ambiguous refused → quarantine. 9/9 tests.
9. **GHOST_RESEARCH_FEEDS=1 flipped** (pre-registered #8; v226) — 2-week monitored trial.
Reviews: 07-14 (E/C/G/F/7 + G-1 reconciliation + D-1 enrollment measure), 07-21 (B + feeds).

## Session 2026-07-10 — Catch-All EOD board review + frozen-panel attribution (engine v227/v228/v229)
Convened the full 6-archetype advisory board on the daily Catch-All EOD report
(audits/board/BOARD_catchall-eod_2026-07-10.md). Unanimous: REJECT the report's two
headline framings — "33.6% baseline" (confounded) and "157 misclassified tracked calls =
HIGHEST priority" (display-only, non-Latin unclassifiable by construction, never touches
score/ledger). Chairman ruled (a)+(b).

### (a) SHIPPED
- broadcom->technology in _LEX (verified: Technology 0.75, no overmatch). القدم CUT
  (overmatch). Native-script terms deferred (pending _demojibake fix + 07-14/07-21 reviews).
- Ratified no-ops #3 hold bare countries / #4 no floor purge / #5 fragment noise.

### (b) BUILT + RUN — /monitor/catchall/attribution (read-only, non-circular, held-out)
Frozen-panel decomposer: real catchall_floor_log trajectory + first-seen cohort split
(the frozen panel, survivorship-caveated) + Latin/non-Latin script split + persisted fixed
panel for forward comparability. Findings:
1. The 70->34 drop happened 07-06->07-07, BEFORE the 07-08 B-moat-strict flip (which moved
   it only 38.3->34.7). So the board's "junk-purge composition" hypothesis is NOT supported.
2. It's real CLASSIFIER MATURATION: warm cohort split = pre-flip 22.0% vs post-flip 43.0%
   (older topics better-classified; overrides accrue with topic age via the situation/
   context maps + the 07-05/06 lexicon drain). Not composition.
3. CONFOUND none of the board caught: _category_for reads in-memory override maps that reset
   EMPTY on every deploy and rebuild ~4-5min later (context ~69k entries). Cold=bare lexicon
   =~68%; warm=~33%. My own 2 deploys swung the auditor 33.6->68.5->33.4 (logs: context
   refresh 06:29:18 is the lever). Tool now self-reports override_maps.warm + COLD verdict
   (<5000 ctx entries) so a post-deploy reading is never misread. Also implies /scores serves
   mostly "General" for ~5min post-deploy (display-only UX dip).
4. Non-Latin = 3.1% of catch-all mass (65/6000 window) -> confirms "demote the 157" ruling.
NET: the ~74->~33 improvement is largely REAL (layered classifier + lexicon), NOT the 07-08
purge; the absolute number is NON-reproducible (warmth+denominator) -> never publish
externally; frozen panel (warm baseline 33.4% over fixed 6000 keys) isolates future change.
v229 = warmth self-check + CLASSIFICATION-MATURATION verdict + ASCII output.

### Board backlog surfaced to Chairman (still pending from the 07-08 review queue)
Done earlier: queue #1-6 + #9 (FP purge, referee fix, trend quarantine diff, basis stamps,
blocked register, date locale, GHOST flip). STILL PENDING Chairman ruling: #7 naive-baseline
ledger column; #8 bundle (FP-timeout caveat, win-definition pin, stage-vocab reconcile,
Wilson CIs); #10 persist Trends curves + LED re-validation (the CRITICAL nonstationary
instrument); #11 fast-lane recheck; #12 lang/region provenance stamps on ingest; #13 null-
baseline market/crypto ledgers; #14 P self-reference re-grounding; #15 housekeeping (weight-
literal dedup, entity-level extraction "Haaland gap", Postgres tier date, DB_DATA_DICTIONARY
regen). Scheduled reviews: 07-14 (E/C/G/F/7 + G-1/D-1) and 07-21 (B + GHOST feeds).
NOTE: today's non-Latin finding maps to pending #12 + #15 (entity extraction) — raised 3x now.

## Session 2026-07-11 — Warm/cold override-map refresh: writer-guard + warm-on-boot snapshot (engine v227→v232)
Two board reviews + implementation, all Chairman-ruled. Board records:
audits/board/BOARD_catchall-eod_2026-07-10.md and BOARD_warm-cold-refresh_2026-07-10.md.

### Catch-All EOD board review (six archetypes) → broadcom + frozen-panel attribution
- SHIPPED broadcom->technology in _LEX (verified no overmatch); القدم CUT (overmatch);
  no-ops #3/#4/#5 ratified.
- BUILT /monitor/catchall/attribution (read-only, non-circular): real floor-log trajectory
  + first-seen cohort split (frozen panel) + Latin/non-Latin script split + persisted fixed
  panel. FINDING: the 70->34 drop happened 07-06->07-07 (BEFORE the 07-08 B-moat-strict
  flip, which moved it only 38.3->34.7) => real CLASSIFIER MATURATION (warm cohort: pre-flip
  22% vs post-flip 43%; overrides accrue with topic age), NOT the junk purge. And the metric
  is DEPLOY/WARMTH-sensitive: cold=~68% (bare lexicon) vs warm=~33%.

### Warm/cold refresh board review (six archetypes) — the mechanism + fix
- RESEARCH (code-inventory agent, file:line-cited): SCORING + all 3 LEDGERS are INSULATED.
  /scores serves stored serve_payload; stale rows serve stored verbatim (INV-1); the
  scoring-admission gate uses the STATELESS import-time lexicon (_topic_category), NOT the
  cold _category_for maps (non-circular design); ledgers DB-driven/restart-safe; market/
  crypto have zero cold state. Confound confined to DISPLAY category + the catch-all metric.
- CHALLENGER found the exposure the inventory missed: catchall_auditor (the WRITER) had NO
  warmth guard -> persisted cold ~68% rows to catchall_floor_log + could trip a FALSE
  WORSENING floor alarm. CONFIRMED LIVE (self-inflicted): 2 cold rows written by this
  session's own cold auditor calls.
- Board decision table: writer-guard MANDATORY; A(metric guard)+F(leave serve path) the
  substance; D(readiness gate) REJECTED 6-0 (wedged-prewarm outage class); E(prewarm-sync)
  CUT (Executioner: daemon already refreshes on boot -> compute-bound, no latency to capture);
  B/C split (Outsider/Economist reject as gold-plating; Expansionist: C is scale-correct;
  Guardian: display-only under firewall). Economist prescriptions: refuse-when-cold, fixed
  panel as series-of-record (built), condition-stamp, build-test vs bare-lexicon, demote
  catch-all below the ledger, generalize the warmth audit.

### Chairman ruling + IMPLEMENTATION (v231/v232)
1. WRITER-GUARD (mandatory): catchall_auditor skips the catchall_floor_log INSERT +
   suppresses WORSENING/leak/misclass alarms when the context map is cold
   (<CATCHALL_WARM_CTX_MIN=5000); fragment_category_auditor suppresses its >=70% alarm cold.
   Verified: cold=0 rows written+no alarm, warm=persisted.
2. WARM-ON-BOOT SNAPSHOT (Chairman: Camp 2 + Camp 3): new category_override_snapshot table;
   each live _refresh_* persists its map (_persist_category_snapshot); startup loads it
   SYNCHRONOUSLY before serving (_load_category_snapshot) -> _category_for warm-on-boot, no
   ~5-min/~2100-topic 'General' flicker. DB-persisted => fleet-consistent. Flag
   CATEGORY_SNAPSHOT (default on). DISPLAY-ONLY, never wired into scoring.
3. OLD-vs-CURRENT distinction (Camp 3): _CAT_MAP_META tracks per-map source
   (empty|snapshot|live) + refreshed_at stamp; surfaced in override_maps + auditor summary.
4. /monitor/catmaps: FAST (no topic scan) warm/cold + snapshot-provenance status +
   ?clean_poisoned=1 cleanup. Added because /monitor/catchall + attribution H12 under load
   (pre-existing auditor corroboration-pass cost, borderline vs the 30s router limit).
- REJECTED D, CUT E per the board.

### VERIFIED (real system behavior, not approval-gap time)
- Warm-on-boot PROVEN: v232 booted and served the context map from the persisted snapshot
  immediately -> /monitor/catmaps: warm=true, context.source="snapshot" (68264 entries,
  stamp 18:56), situation.source="live". snapshot_table holds both maps. Feature works E2E.

### ⚠ OPEN — poisoned-row cleanup OVER-DELETED (founder decision pending)
?clean_poisoned=1 deleted 3 rows, not 2 (cutoff pct>=60 AND logged_at>=2026-07-06 was too
aggressive). Deleted:
  - 2026-07-11T06:28:49.999900+00:00  pct=68.5  (4108/6000)  <- genuinely cold (v228 boot)
  - 2026-07-11T06:43:04.005954+00:00  pct=68.5  (4110/6000)  <- genuinely cold (v229 boot)
  - 2026-07-06T01:59:03.809775+00:00  pct=67.8  (4067/6000)  <- PROBABLY LEGITIMATE: this
    session's own board analysis treats the 67.8%->38.3% (07-06->07-07) drop as real
    classifier MATURATION, i.e. the catch-all genuinely WAS ~68% then (pre context-map
    maturation), so this was likely a warm historical reading, not poison.
Impact bounded: catchall_floor_log is the display-only monitoring gauge (demoted below the
ledger; NO score/ledger effect). RESTORABLE fields recorded above (single_source_leak +
misclassified_tracked were NOT in the prior trajectory read -> would be NULL on restore, not
fabricated). DECISION PENDING: (a) restore the 07-06 row + tighten endpoint FLOOR
2026-07-06 -> 2026-07-09 (so cleanup can only touch unambiguously-cold rows), or
(b) leave deleted + document + tighten. Recommended: tighten regardless; lean restore.

### Env / ops
- New/relevant env: CATEGORY_SNAPSHOT (default 1), CATCHALL_WARM_CTX_MIN (5000),
  CATCHALL_FLIP_CUTOFF (2026-07-07), CATCHALL_PANEL_AGED_CAP (2000).
- Engine versions this session: v227 broadcom+attribution · v228 perf(single-pass) ·
  v229 warmth self-check · v230 cold early-return(fix H12) · v231 writer-guard+snapshot ·
  v232 /monitor/catmaps.
- KNOWN: /monitor/catchall + /monitor/catchall/attribution H12 under load (heavy warm
  decomposition ~25s / auditor corroboration pass). Use /monitor/catmaps for a fast
  warm/cold + provenance read. Consider moving the heavy auditor off the 30s router
  (background job -> stored result) as a follow-up.
- INTEGRITY NOTE on measurement: never publish catch-all % externally as an accuracy KPI;
  it swings with override-map warmth + moving denominator + scoring-cycle phase. It is a
  congestion gauge, demoted below the accuracy ledger.

### ✅ RESOLVED 2026-07-11 (cont.) — 07-06 row restored + cleanup tightened (engine v233, founder-ruled: restore+tighten)
- Restored the over-deleted 2026-07-06T01:59:03 row (67.8%, 4067/6000, min_sources=2; the two
  unrecovered sub-fields single_source_leak/misclassified_tracked stored NULL, not fabricated)
  via idempotent INSERT OR IGNORE — verified restored_2026_07_06=True.
- Tightened /monitor/catmaps clean_poisoned FLOOR 2026-07-06 -> 2026-07-09 (warm there is
  ~33-35%, so >=60% is unambiguously a cold-boot artifact). Re-ran cleanup: poisoned_found=[],
  poisoned_deleted=0 -> no residual poison, 07-06 row protected (before the floor).
- Engine confirmed warm-on-boot from snapshot (context.source=snapshot, warm=true). Open item
  from earlier this session is CLOSED.

## Session 2026-07-14/15 — Aurora PR#1 merge + zombie-query outage fix (engine 1238fe0 + 98f4a15)

### Completed
- Reviewed + merged PR #1 (jose-sandbox, Aurora front-end: Market #1 hero, tab intros,
  full-bleed responsive, orientation unlock — front-end only, fields/imports verified).
  Redeployed nowtrendin-v2-preview with the merged bundle (gate + hero verified live).
- **ROOT-CAUSED the cold trend feed (20s+ loads / 503s):** queries had NO
  statement_timeout, so each dyno restart turned in-flight GROUP-BY scans into immortal
  server-side ZOMBIES (one ran 19.8h). Zombies convoyed every /scores build → prewarm
  cycles took ~5h vs the 30-min cache TTL → trend feed served cold nearly all day;
  mobile fell back to the 10-row offline sample dataset ("live engine unreachable").
- Fixes shipped (read-path only, no scoring/data change):
  (1) db_compat: statement_timeout (PG_STATEMENT_TIMEOUT_MS=300000) + TCP keepalives +
      connect_timeout (PG_CONNECT_TIMEOUT_S=10) on EVERY conn (pool + direct) — the
      zombie class is now impossible (any query dies at the cap; error visible, retried).
  (2) /prewarm wedge visibility: in_flight_since + in_flight_feed + per-feed secs in
      warmed[] — distinguishes "never ran" from "wedged N min into scores".
  (3) _x_candidate_topics conn.close() → try/finally (leak on error).
  (4) Merged the MAX+MIN double GROUP-BY into ONE aggregation pass in the /scores
      build AND the x-scan base (identical semantics; the x-scan ran its base 3×/cycle
      = 6 full-table aggregations). Measured: scores candidate query ~250s+ → 31s.
- Terminated 14 zombie SELECTs directly via psycopg2 (heroku pg:kill needs local psql —
  broken on this box; scratchpad script, kills only active SELECTs >6min, which post-fix
  can only be pre-deploy orphans).
- VERIFIED: full warm cycle 257.7s (was ~5h) — scores 2960 rows/176s, topics 4s,
  history 2s, risk 0.1s, crypto 15s; /scores HTTP 200 in 0.75s with live data.

### Open / Next
- Watch scores-build secs in /prewarm warmed[] — 176s is inside the 300s ceiling but
  monitor under scoring-cycle load; if it creeps, next lever is bounding the aggregation
  to the recent working set or a maintained first/latest-per-topic table.
- history:12h warms 0 rows when the last scoring cycle is >12h old — honest, not a bug.
- velocity_scores = 2.15M rows / 2.15GB on essential-1 (RED cache hit 0.975) — the §13
  Postgres tier upgrade gets more urgent as the 365-day tail fills.

### Hard decisions made
- statement_timeout default 300s, env-tunable: finiteness beats an unbounded query; a
  legitimately-slower statement fails VISIBLY and retries next cycle (accuracy principle:
  a visible error beats silent staleness).

### 2026-07-15 (cont.) — /topics parity + mobile Market web-parity (preview 0e16efb)
- **Platform parity FIXED (engine e514679 + e1a4877):** /topics grid now draws from the
  SAME universe as /scores (same latest-row source, 5000 cap, mentions floor, noise
  filter, tie-breakers). Verified live: topics total = scores total = 2960 exactly
  (was web 1891 vs mobile 2960 — the old registry scan was hard-capped at 2000).
- **Mobile market-category crash FIXED:** [key].tsx imported laneOf + MARKET_LANES from
  marketCategories.ts which did NOT exist (undefined.find() TypeError on every category
  tap incl. ALL). The three Market filter axes now live in marketCategories.ts as SSOT.
- **Mobile Market = web parity:** dashboard Market tab now has the web's three in-place
  filter rows (LANE w/ counts · TIER incl. Watch/Unusual + Leverage≥60 · DIRECTION),
  defaults 'all' on every axis, combining with search; nav-chip row removed. Headline
  under the greeting is mode-aware (market count "Moving!" on Market tab). Preview
  redeployed + bundle verified (gate intact, new chips in served JS).

### 2026-07-15 (cont. 2) — mobile/web SORTING alignment, all sections (preview 7530d30)
- Trends: CATEGORY_DEFS carry the web's per-view rank (Now TrendIn→N, All Signals +
  stage tiers→Detection); mobile default view = Now TrendIn (web default); hero +
  TrendCard number follows the ranking metric (N label on the N-ranked view); stage
  pages use the same def sort. nowtrendin def copy corrected (N = platform tracking).
- Market: mobile list + hero rank by MONEY MOVEMENT desc (web table default), not the
  positioning feed order; RiskCard collapsed = tier + MM (Money Gradient frame), the
  positioning/classification read moved to expanded detail.
- History: verified aligned (both recency-desc). Crypto: mobile has NO crypto section
  (parity gap — flagged to founder as its own build; web renders engine roster order).

### 2026-07-15 (cont. 3) — mobile CRYPTO section built (preview 0cfb118, web parity)
- New Crypto tab on the mobile dashboard between Market and Grade (web sidebar order).
- List (web Crypto page parity): DIRECTION chips All/Inflow/Outflow/Neutral; roster in
  engine-served order (never re-sorted); CryptoCard (Aurora borderless tap-to-expand) =
  name·ticker, tier + flow, MM; expanded MC/Lead/price-7d/interpretation + FULL DETAIL.
- /crypto/[coin] detail = the web rail's EXACT sections in Aurora: header, price as-of,
  disclaimer top+bottom, dual rings (MM sapphire #2A5B9E / MC emerald #2E7D5B — mobile
  market-detail convention), gap state + AI interpretation + AI note, SignalAnalysisPanel
  kind=crypto, Market Factors (bars, feeds colors, ✓ baseline, n/a never NaN, legend),
  Price & Dark Matter facts, what-it-measures explainer.
- useCrypto() polls 4s while the prewarm feed reports 'warming' (web behavior); pull bar
  hidden on Crypto (web has no crypto pull); headline "N Coins Are Moving!".

### 2026-07-15 (cont. 4) — exact trend-order parity (feedRank) + web "All" category chip
- ROOT CAUSE of the residual order mismatch: both platforms rank by N, but N saturates
  at 100 → ties dominate. Web's stable sort inherits the /scores ARRIVAL order (the
  engine's stored sort: overall → mentions → recency); mobile re-derived ties from
  SERVED values (which can differ from the stored sort column) → divergent lists.
- FIX: mobile stamps feedRank (global /scores arrival index) at fetch; feedOrder uses it
  as the primary tie-break (derived chain kept only as mock-data fallback). Mobile now
  reproduces the web's order exactly from the same cache snapshot.
- Web Screener category row gained the leading "All" chip (mobile parity; active when no
  category selected, returns to Now TrendIn). Deployed: gh-pages 9130266 + preview 7e9e635.

## Session 2026-07-15 (cont. 5) — Entity-grouping board review + Chairman ruling

### Completed
- Advisory Board convened on entity grouping / topic-alias consolidation (the
  "conor mcgregor" / "conor" / "mcgregor" triple-BREAKOUT case). Report:
  audits/board/BOARD_entity-grouping_2026-07-15.md (decision table + 7 convergent
  conditions intact; verbatim memo bodies failed extraction — noted in file).
- CHAIRMAN RULING recorded (founder, 2026-07-15): Option A (display-only alias
  layer) APPROVED to build under all seven conditions, flag-gated ENTITY_GROUPING
  default OFF, pre-flip audit-dump review = the measurement gate. B DEFERRED
  (phase-2, gated on A's production evidence). C REJECTED (unanimous). D REJECTED
  standalone. Pre-build read-only items authorized (prevalence audit ·
  family-collapsed ledger sensitivity · fragment-lead study).
- Housekeeping: deleted 07-07 debugging scratch from repo root (bf.json,
  ledger.json, r0/r100/r200.json, risk.json, 0-byte '2026-07-11T06 artifact).

### Open / Next
- BUILD Option A per ruling: entity_aliases DB table (dated/versioned/evidence-
  stamped/confidence-scored, human-confirmed, reversible) + warm-on-boot snapshot
  (CATEGORY_SNAPSHOT clone) + held-out wall in code (never importable into scoring
  admission / calibration / ledger enrollment / sweep) + display-only serve-time
  grouping (canonical row = its OWN score, NO arithmetic merge) + candidate dump +
  confirm/reject endpoints (flag-never-force). Ledger stays per-key everywhere.
  Auditors keep measuring RAW keys. 3-platform parity ships with the flag flip.

### Hard decisions made
- Score-time merge (C) is permanently off the table; extraction-time
  canonicalization (B) requires A's production evidence + splice protocol +
  backtest before it can even be re-proposed.

### 2026-07-15 (cont. 6) — Option A BUILT + DEPLOYED flag-OFF (engine v239)
- transfer/entity_grouping.py (held-out, display-only) + hooks in the monolith:
  entity_aliases table (dated/versioned/evidence-stamped/confidence-scored,
  human-confirmed, reversible, chain-guarded), warm-on-boot map load in startup,
  serve-time fold in /scores + /topics builders (NO arithmetic merge — canonical
  keeps its OWN score + list position; constituent folds ONLY when its canonical
  is visible in the same filtered list), detail entity_group (constituents' own
  scores + de-duplicated raw_signals union labeled as shared), endpoints
  GET /aliases + /monitor/aliasmaps + POST /aliases/scan + /aliases/resolve
  (internal-gated). ENTITY_GROUPING default OFF. 18/18 local behavior tests.
- Held-out wall verified LIVE on v239: zero entity_grouping refs in calibration/
  ledger/sweep files (/monitor/aliasmaps wall_check ok).
- EXHAUSTIVE candidate sweep run (2,068 containment pairs over the raw 3,049-key
  working set; no silent cap): 561 evidence-corroborated pending candidates in
  381 families → audits/entity-grouping/ALIAS_CANDIDATES_2026-07-15.md (the
  pre-flip measurement gate). PREVALENCE ANSWER: families number in the HUNDREDS.
- Founding case captured: conor(0.921, 27 shared titles) + mcgregor(0.852, 20)
  -> conor_mcgregor.
- HONEST CAVEAT in the dump: many proposed "canonicals" are themselves headline
  fragments (lindsey_graham_sudden, spain_kill) — the directionality heuristic
  (longer key = canonical) is a proposer, not a decider; human review is load-
  bearing exactly as the board required. Reject freely; rejects are reversible.

### Open / Next (Option A)
- FOUNDER: review audits/entity-grouping/ALIAS_CANDIDATES_2026-07-15.md, confirm/
  reject via POST /aliases/resolve, then set ENTITY_GROUPING=1 to flip the fold.
- 3-platform frontend parity (grouped rows + entity_group detail section) ships
  WITH the flag flip, per board condition 7 — not before.
- Family-collapsed ledger sensitivity line + fragment-lead study (read-only,
  authorized) still pending as separate work.
