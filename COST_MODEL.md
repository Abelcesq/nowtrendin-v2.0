# Now TrendIn — Hard Cost Model & Unit Economics

> Living doc. Update weekly. Measured figures are from live API responses;
> estimates are labelled (est). Live AI tally: `GET /grade/costs`.

_Last updated: 2026-06-05_

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

**Key:** the only meaningful marginal cost per *new* search is the **AI Grade (~1.2¢)**. Reading existing scores is **free**.

---

## 2. Fixed monthly costs (infrastructure + subscriptions)

| Item | Cost/mo | Notes |
|---|---|---|
| Heroku — engine dyno (Basic) | ~$7 | 512MB. Scale to Standard/Perf at load (est $25–250). |
| Heroku — engine Postgres (essential-0) | $5 | |
| Heroku — backend dyno (Basic) | ~$7 | |
| Heroku — backend Postgres (essential-0) | $5 | |
| Heroku Scheduler | $0 | free |
| **Apify** (Google Trends) | **$150** | current plan; capped. |
| **X API** (Basic) | **$200** | 15,000 posts/mo cap. → Pay-Per-Use Jun 21. |
| FRED | $0 | free |
| YouTube Data API | $0 | free ≤10,000 units/day (~100 searches/day). |
| Twilio (SMS verify) | ~$0.008/msg | signup only, negligible. |
| SendGrid (email) | $0 | free tier. |
| **Total fixed (today)** | **~$374/mo** | before scaling dynos. |

---

## 3. THE HEDGE-FUND QUESTION: 1 search every 5 minutes
### (Enterprise = $250K/mo · 10,000 tokens · up to 5 users, shared pool)

**Volume:** 1 / 5 min = 12/hr × 24 × 30.4 = **~8,755 searches / month** per user.

### A. Does the 10,000-token allowance ALLOW it?  ✅ **Yes (for the account).**
- 10,000 tokens ÷ 1 token/search = 10,000 searches.
- At 1 every 5 min, 10,000 tokens lasts **~34.7 days** → covers a full month for **one** continuous 5-min poller (8,755 < 10,000).
- **Caveat — 5 shared users:** if *all 5* independently grade *new* topics every 5 min, that's 5 × 8,755 = ~43,775 → exceeds the 10,000 pool. BUT:
  - **Reads of already-scored topics are FREE** (the engine re-scores on its own 30-min schedule), and
  - funds watch a **shared watchlist** that the **12h cache** collapses to a handful of real grades/day.
  - Realistic shared usage stays well under 10,000. Heavy unique-grading across 5 users is the only case that hits the cap → meter overage if it occurs.

### B. Does $250K cover the COST of it?  ✅ **Yes — overwhelmingly.**
- Full 10,000 tokens as *new* AI Grades (worst case, no cache): 10,000 × $0.0124 = **~$124/mo** per account.
- 20-topic shared watchlist, cached: ~40 grades/day = **~$15/mo** per account.
- Pure reads (likely real case): **$0 marginal.**

### C. Margin check at $250K / account
| Scenario | Monthly cost / account | Gross margin |
|---|---|---|
| Reads of existing scores (5-min) | ~$0 | ~100% |
| 20-topic watchlist, AI-graded, cached | ~$15 | 99.99% |
| **Full 10,000 tokens, all unique grades** | **~$124** | **99.95%** |
| All-in (10k grades + ~$374 fixed) | ~$500 | **99.80%** |
| 100 accounts, worst case each | ~$12,400 AI + fixed | 99.99%+ |

**80% margin target:** met by >1,000×. Costs would have to reach **$50,000/mo** to break the 80% floor; full-tilt usage of one account is ~$500/mo all-in. **At $250K/account the model is profitable at ~99.8% even if every included token is burned on the most expensive action.**

---

## 4. Conclusion & recommendation

1. **Resolved:** Enterprise is now **10,000 tokens/mo, 5 users (shared pool), reads unlimited.** This covers one continuous 5-min poller for a full month, at ~$124 worst-case cost → **99.95% margin**.
2. **Only remaining risk:** 5 users *each* unique-grading every 5 min exceeds 10,000. Mitigated by free reads + 12h cache; if it ever bites, **meter overage** at a token price ≥ $1 (80× cost) to preserve margin.
3. **The real scaling cost is X data, not AI.** At hedge-fund concurrency, X PPU (~$0.005/read, 100/pull) is the one line that can grow — the 12h cache and velocity-trigger already contain it; revisit `X_SCAN_LIMIT` after the Jun-22 reset.
4. **Watch weekly:** `GET /grade/costs` (AI split), Apify usage dashboard, X post-cap dashboard, Heroku metrics (dyno load → when to upsize).

---

## 5. Estimates to firm up
- Apify per-run cost (check Apify usage dashboard for $/run).
- X Pay-Per-Use exact per-read rate (effective Jun 21).
- Heroku dyno tier needed at N concurrent funds (load-test).
