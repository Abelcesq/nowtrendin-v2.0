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
