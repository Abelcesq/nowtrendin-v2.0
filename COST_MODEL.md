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

**Volume:** 1 / 5 min = 12/hr × 24 × 30.4 = **~8,755 searches / month**.

### A. Does the 1,000-token cap ALLOW it?  ❌ **No.**
- 1,000 tokens ÷ (1 token/search) = 1,000 searches.
- At 1 every 5 min, 1,000 tokens is exhausted in **~3.5 days**, not a month.
- A full month of 5-min pulls needs **~8,755 tokens**, ~8.75× the current allowance.

### B. Does $250K cover the COST of it?  ✅ **Yes — overwhelmingly.**
- If every pull is a *new* AI Grade (worst case, no cache): 8,755 × $0.0124 = **~$109/mo** per fund.
- With the 12h cache (funds re-poll the same watchlist): a 20-topic watchlist = ~40 grades/day = ~$15/mo per fund.
- If pulls are just **reads of already-scored topics** (the likely real case — the engine re-scores on its own 30-min schedule): **$0 marginal.**

### C. Margin check at $250K / fund
| Scenario | Monthly cost / fund | Gross margin |
|---|---|---|
| Reads of existing scores (5-min) | ~$0 | ~100% |
| 20-topic watchlist, AI-graded, cached | ~$15 | 99.99% |
| 8,755 unique AI grades (worst case) | ~$109 | 99.96% |
| 100 funds, worst case each | ~$10,900 total | still 99.99%+ |

**80% margin target:** met by a factor of >1,000×. Costs would have to hit **$50,000/mo** to break the 80% floor — current all-in is ~$374/mo + a few hundred in AI even at scale.

---

## 4. Conclusion & recommendation

1. **Price is not the problem — the token cap is.** $250K covers 5-min hedge-fund polling with >99.9% margin. But **1,000 tokens does not permit it** (lasts 3.5 days).
2. **Fix the token model to match the use case.** Options:
   - Make Enterprise **reads unlimited** (they already are — only *new* grades/queries cost tokens), and **raise the new-query allowance** to e.g. 10,000/mo (cost ~$124 → still 99.95% margin), or
   - Remove the hard cap and **meter overages** at a token price that preserves margin (even $1/token is 80× your cost).
3. **The real scaling cost is X data, not AI.** At hedge-fund concurrency, X PPU (~$0.005/read, 100/pull) is the one line that can grow — the 12h cache and velocity-trigger already contain it; revisit `X_SCAN_LIMIT` after the Jun-22 reset.
4. **Watch weekly:** `GET /grade/costs` (AI split), Apify usage dashboard, X post-cap dashboard, Heroku metrics (dyno load → when to upsize).

---

## 5. Estimates to firm up
- Apify per-run cost (check Apify usage dashboard for $/run).
- X Pay-Per-Use exact per-read rate (effective Jun 21).
- Heroku dyno tier needed at N concurrent funds (load-test).
