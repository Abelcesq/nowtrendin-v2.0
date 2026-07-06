# Now TrendIn — Hard Cost Model & Unit Economics

> Living doc. Update weekly. Measured figures are from live API responses;
> estimates are labelled (est). Live AI tally: `GET /grade/costs`.

_Last updated: 2026-06-26 — **FMP upgraded free → $20 Starter** (300/min, crypto+forex) for the Crypto
Money Gradient + reliable crypto prices; the Cost Sentinel + Data Subscriptions agents now register Finviz/
Quiver/FMP/Databento (`COST_FINVIZ_USD`/`COST_QUIVER_USD`/`COST_FMP_USD` set). Total fixed ~$390/mo. Prior:
2026-06-25 — added **Finviz Elite ($30/mo)** as PRIMARY insider + equity-market source (uncapped market-wide
SEC Form-4; AV demoted to fallback); QuiverQuant ($30/mo, congress), Databento (~free, metered); X migrated
Basic→Pay-Per-Use; worker dyno live. Live AI spend June: **$15.32 / $20** (`/ai/costs`)._

---

## 1. Per-search (marginal) costs — what one action actually costs

| Action | What it calls | Measured cost | Notes |
|---|---|---|---|
| **Search Current Trends** | local filter only | **$0.00** | No external call. Free, unlimited. |
| **AI Grade** (new topic) | Perplexity + Claude | **~$0.0124** | Perplexity ~$0.0056 + Claude ~$0.0068. Measured. 12h cached. |
| └ Perplexity (Sonar) | web research | ~$0.0056 | ~$0.005 request + tokens. |
| └ Claude (Sonnet 4.5) | score synthesis | ~$0.0068 | $3/M in, $15/M out. ~1.5k tok/call. |
| **Pull Trends / live query** | HN, GitHub, YouTube, Reddit + scoring | **~$0.00** | All free APIs (YouTube within free quota). |
| **X signal** (`/signal-x`) | X search+counts | **~$0.50** (est, PPU) | 100 posts/pull. Basic: free within 15k cap. PPU (Jun 21+): ~$0.005/read. **12h cached** → ~zero on repeat. |
| **Google Trends validation** | Apify actor | **~$0.02–0.05/run** (est) | Daily batch (8 topics), NOT per search. Draws from $150 Apify plan. |
| **Market-ledger price verify** | Databento (+FMP cross-check) | **~$0.0003/ticker** | EQUS.SUMMARY ohlcv-1d; per sweep, cached 6h. Effectively free. |
| **Microstructure read** (held-out) | Databento trades | **~$0.001/window** | block/dark-pool/imbalance prototype. Not in any score yet. |
| **Dark-Matter insider/13F** (held-out) | Alpha Vantage | **$0** | free tier, throttled (13s/call). Not in any score yet. |
| **Market AI analysis** | Claude (guardrailed) | **~$0.003** | folds into the $20 AI cap; 12h-cached per instrument. |

**Key:** the only meaningful marginal cost per *new* search is the **AI Grade (~1.2¢)**. Reading existing scores is **free**.

---

## 2. Fixed monthly costs (infrastructure + subscriptions)

| Item | Cost/mo | Notes |
|---|---|---|
| Heroku — engine web dyno (**Standard-2X**) | **$50** | verified `heroku ps` 2026-07-05 (no worker dyno — scheduler runs in-process on web). |
| Heroku — engine Postgres (**essential-1**) | **$9** | upsized for the 365-day retention (§13); 10GB tier. |
| Heroku — backend dyno (Basic) | $7 | |
| Heroku — backend Postgres (essential-0) | $5 | |
| Heroku — v2-preview dyno (Basic) | $7 | enterprise web mobile preview (Aurora). |
| Heroku — terminal dyno (Basic) | $7 | web-terminal Heroku mirror (canonical site = GH Pages, free). |
| Heroku — nowtrendin-web dyno (Basic) | $7 | ⚠ possible redundant mirror — review vs terminal + GH Pages (−$7 candidate). |
| Heroku — **frozen 1.0 Postgres (essential-2)** | **$20** | ⚠ preserved-but-unused DB on the disabled 1.0 app — archive (pg:backups) then delete (−$20 candidate). |
| Heroku Scheduler | $0 | free |
| **Heroku total (NowTrendIn footprint)** | **$112** | = `COST_HEROKU_USD` (set on engine 2026-07-05, was $64 — the June invoice $82.13 + July run-rate ~$3.46/day exposed the under-count). Excludes the $5 `mytaskapp` personal app on the same account. |
| **Apify** (Google Trends) | **$150** | current plan; capped. |
| **X API** (Pay-Per-Use) | **~$100 (est)** | was $200 Basic; migrated PPU Jun 21. June usage **9,160 / 14,880** posts. Confirm $/post on X dashboard. |
| **QuiverQuant** (congress trades / Dark Matter) | **$30** | **confirmed 06/25** (card charge). |
| **Finviz Elite** (PRIMARY insider Form-4 + equity market) | **$30** | **confirmed 06/25** (card charge). Uncapped market-wide insider feed (`insidertrading.ashx`) + screener export. Flag `FINVIZ_INSIDER`. NOT crypto (display-only → FMP). |
| **AI** (Perplexity + Claude — Grade/explainer/market) | **≤$20 (hard cap)** | **June live: $15.32** (Perplexity $13.76 + Claude $1.56; explainer/definition is the bulk). |
| **Databento** (accuracy-ledger price verify + microstructure) | **~$0** | metered (~$0.0003/ticker), new-acct free credit; ~cents/mo after. No request cap. |
| **Alpha Vantage** (NEWS_SENTIMENT + 13F + insider FALLBACK) | **$0** | free tier (25/day · 5/min). Insider role now FALLBACK behind Finviz; AV kept for 13F institutional + NEWS_SENTIMENT. |
| **FMP** (prices/fundamentals + crypto coin prices) | **$20** | **Starter, confirmed 06/26** (300/min, crypto+forex). Upgraded from free — fixes free-tier 429s; now serves the **Crypto Money Gradient** coin prices + the market-ledger cross-check. `COST_FMP_USD`. |
| FRED · SEC EDGAR · OFR · FINRA · GDELT | $0 | free / public. |
| YouTube Data API | $0 | free ≤10,000 units/day (~100 searches/day). |
| Twilio (SMS verify) · SendGrid (email) | ~$0 | signup only / free tier, negligible. |
| **Total fixed (today)** | **~$390/mo (est)** | Heroku ~$31 + Apify $150 + X ~$100 + Quiver $30 + Finviz $30 + FMP $20 + AI ~$20; Databento/AV ~$0. Net adds this week: Finviz $30 + FMP $20 (the Crypto Money Gradient + reliable crypto prices). All wired into the Cost Sentinel via `COST_FINVIZ_USD`/`COST_QUIVER_USD`/`COST_FMP_USD`. |

---

## 3. THE HEDGE-FUND QUESTION: 1 search every 5 minutes
### (Enterprise = $250K/mo · 100,000 tokens · up to 5 users, shared pool)

**Volume:** 1 / 5 min = 12/hr × 24 × 30.4 = **~8,755 searches / month** per user.

### A. Does the 100,000-token allowance ALLOW it?  ✅ **Yes, with huge headroom.**
- 100,000 tokens ÷ 1 token/search = 100,000 searches.
- At 1 every 5 min, 100,000 tokens lasts **~347 days (~11.4 user-months)**.
- **All 5 users** polling every 5 min = 5 × 8,755 = ~43,775 → still **well under 100,000.** The cap is no longer a practical constraint for any realistic hedge-fund workflow.
- Reads of already-scored topics are **FREE**; the **12h cache** collapses shared watchlists further.

### B. Does $250K cover the COST of it?  ✅ **Yes — overwhelmingly.**
- Full 100,000 tokens as *new* AI Grades (absolute worst case, no cache): 100,000 × $0.0124 = **~$1,240/mo** per account.
- 5 users polling 5-min (43,775 grades, no cache): ~$543/mo.
- 20-topic shared watchlist, cached: **~$15/mo.**
- Pure reads (likely real case): **$0 marginal.**

### C. Margin check at $250K / account
| Scenario | Monthly cost / account | Gross margin |
|---|---|---|
| Reads of existing scores (5-min) | ~$0 | ~100% |
| 20-topic watchlist, AI-graded, cached | ~$15 | 99.99% |
| 5 users × 5-min unique grades (~43,775) | ~$543 | 99.78% |
| **Full 100,000 tokens, all unique grades** | **~$1,240** | **99.50%** |
| All-in (100k grades + ~$374 fixed) | ~$1,614 | **99.35%** |
| 100 accounts, worst case each | ~$124,000 AI / $25M rev | 99.50% |

**80% margin target:** met by >150×. To break the 80% floor a single account would have to cost **$50,000/mo** (~4M grades) — impossible within 100,000 tokens. **At $250K/account the model is profitable at ~99.4% even if every one of the 100,000 included tokens is burned on the most expensive action.**

---

## 4. Conclusion & recommendation

1. **Resolved:** Enterprise is now **100,000 tokens/mo, 5 users (shared pool), reads unlimited.** Covers ~11 user-months of 5-min polling — the cap is a non-issue for realistic use. Worst case (all 100k as unique grades) ~$1,240 → **99.50% margin**.
2. **No remaining cap risk** for normal workflows; even 5 users polling 5-min stays under 100,000. The only cost that scales nonlinearly is **X data** (PPU), governed separately by the post-cap + 12h cache, not by tokens.
3. **The real scaling cost is X data, not AI.** At hedge-fund concurrency, X PPU (~$0.005/read, 100/pull) is the one line that can grow — the 12h cache and velocity-trigger already contain it; revisit `X_SCAN_LIMIT` after the Jun-22 reset.
4. **Watch weekly:** `GET /grade/costs` (AI split), Apify usage dashboard, X post-cap dashboard, Heroku metrics (dyno load → when to upsize).

---

## 5. Estimates to firm up
- Apify per-run cost (check Apify usage dashboard for $/run).
- X Pay-Per-Use exact per-read rate (effective Jun 21).
- Heroku dyno tier needed at N concurrent funds (load-test).

---

## 6. Infrastructure scaling spec (Heroku)

**Why:** today the engine runs **everything on one Basic web dyno** — the FastAPI
server AND the in-process APScheduler (collect every 30 min, risk cycle, X scan
at 1am/1pm). When those background jobs run together they saturate the single
512 MB / shared-CPU dyno and `/scores` times out (observed live). At hedge-fund
concurrency this is the #1 reliability risk. Fixes below, in priority order.

### Priority 1 — Separate background work from web serving ✅ DONE (+$7/mo)
**Implemented.** The scheduler now runs on a dedicated **worker dyno**
(`worker: --mode=worker`); the web dyno serves only requests (it prints
"Scheduler NOT started on web dyno"). This removed the collect/scan-vs-web
contention that caused `/scores` timeouts. Verified: web uncontended, `/scores`
~0.35s cached. Cost: +1 Basic worker ($7/mo). Toggle back with
`RUN_SCHEDULER_IN_WEB=1` for single-dyno/dev.

### Priority 2 — Upsize the web tier (concurrency + HA)
| Tier | RAM | $/mo | When |
|---|---|---|---|
| Basic (today) | 512 MB | $7 | dev / pre-launch |
| Standard-1X | 512 MB, better CPU, **metrics + autoscale** | $25 | first paying account |
| Standard-2X | 1 GB | $50 | a few concurrent accounts |
| Performance-M | 2.5 GB, dedicated | $250 | many funds / heavy polling |
- Run **2× web dynos** (any Standard+ tier) for horizontal concurrency + zero-downtime deploys. Standard tiers support **autoscaling** on request latency.

### Priority 3 — Upgrade Postgres (engine)
| Plan | RAM cache | Conns | $/mo | When |
|---|---|---|---|---|
| essential-0 (today) | shared, **CPU-throttled** | 20 | $5 | dev |
| essential-2 | shared | 40 | $25 | bridge |
| **standard-0** | 4 GB, **no throttle**, metrics | 120 | $50 | **recommended at launch** |
| standard-2 | 8 GB | 400 | $200 | scale |
- Data is only ~50 MB, so size isn't the driver — **CPU throttling + connection
  count** are. standard-0 removes the throttle and adds the metrics needed to
  watch load. Same for the Django backend Postgres when user volume grows.

### Recommended launch baseline (first hedge-fund accounts)
| Component | Plan | $/mo |
|---|---|---|
| Engine web | Standard-1X × 2 | 50 |
| Engine worker (scheduler) | Standard-1X | 25 |
| Engine Postgres | standard-0 | 50 |
| Backend web | Standard-1X | 25 |
| Backend Postgres | essential-2 → standard-0 | 25–50 |
| **Total** | | **~$175–200/mo** |

**Margin impact:** ~$200/mo infra vs **$250,000/account** = **<0.1%**. Even a
Performance-M build (~$700/mo) is rounding error against revenue — upgrade freely;
reliability matters more than the line item. The 80% floor is untouched.

### Trigger metrics (when to upsize)
- Heroku dyno **memory > 80%** or **load (load avg/#cores) > 1** sustained → bigger dyno.
- Router **H12 timeouts** appearing → add a dyno or move work to worker (P1).
- Postgres **CPU throttle events** or conns near cap → upgrade plan.
