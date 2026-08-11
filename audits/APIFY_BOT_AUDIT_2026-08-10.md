# Apify Bot Audit + Cleanup — 2026-08-10 (Chairman-ordered)

**Question put:** are we double-paying (the X pattern — an external consumer on our bill),
and should any bots be eliminated?

## Verdict: NO double-paying. Every run on the account is NowTrendIn's.

Attribution method: Apify API, last **986 runs (2026-07-11 → 2026-08-11)** — not the console
eyeball. Every run belongs to one of exactly two actors, both called only by the engine's own
internal crons. Account-side surface is clean: **0 schedules, 0 saved tasks, 0 webhooks** —
nothing fires on Apify itself; nothing external holds the token (rotated 2026-06-26).

## Actor-level economics (last 31 days, API-sourced)

| Actor | Role | Runs | Success | Spend | Verdict |
|---|---|---|---|---|---|
| `easyapi/google-realtime-trends-data-scraper` (oOHXMAv8kImUCpHff) | Realtime trend discovery, 4×/day at :30 (clock slots) | 125 | **125/125 (100%)** | $69.48 | **KEEP** — sole realtime discovery feed, perfectly on schedule (125 ÷ 31d = 4.03/day) |
| `apify/google-trends-scraper` (DyNQEYDj9awfGQf9A) | Accuracy-ledger sweep resolution (cron :45, ≤8 queries/slot) | 861 | **144/861 (17%)** | $62.22 — of which **$57.93 was 715 TIMED-OUT runs returning 0 results** | **KEEP ON NOTICE** — see below |
| `apify/instagram-scraper` | none (consent-list entry only) | 0 | — | $0 | Not running; nothing to eliminate. Untick consent (cosmetic). |
| `trudax/reddit-scraper-lite` | none (consent-list entry only; Reddit data comes direct from Reddit's API, not Apify) | 0 | — | $0 | Same. |
| `nowtrendin-v2-0` (gqQAthXVmE3WQHqqN, custom) | none — empty shell created 2026-06-04, **0 runs ever**, no source/description | 0 | — | $0 | **DELETE candidate** (hygiene only; costs nothing while it sits) |

Plan: **STARTER** (already downgraded — the console's "$19/$200" is month-to-date platform
usage against the founder-set $200 spending limit, not a plan fee).

## The one real problem: the sweep actor fails 83% of the time

The ledger-sweep actor's runs mostly die as "Crawled 0/1 pages" → TIMED-OUT at the 10-minute
server-side cap, $0.07–0.10 each — **$57.93/31d of pure waste (93% of the sweep's spend bought
nothing)**. Successful runs finish in 35–101 s and cost $0.02–0.03. Root behavior: Google
blocking/starving the actor's crawls on most attempts, not our scheduling (clock-slot cadence
confirmed clean).

### Cleanup applied (Chairman-ordered, live)
- **`APIFY_RUN_TIMEOUT` 600 → 120 s** (engine config v338, effective immediately, no deploy).
  Every observed success fits under 120 s; each failure now bills ~⅕ of before.
  Projected: the ~$58/mo waste line drops to ~$12/mo (≈ $45/mo saved); total Apify actor
  spend ≈ $132 → ≈ $86/mo with zero data loss.

### Not eliminated, and why
The sweep actor cannot be dropped outright: it is the resolution mechanism of the attention
accuracy ledger (the moat) — LED/LAGGED verdicts need the Google Trends curve. 144
successes/month ≈ 4.6 resolutions/day keeps the ledger resolving under the 365-day patience
window. The Wikipedia referee is independent and unaffected.

### Watch item (1 week)
If the success rate stays ~17% after the timeout cut, options in order: (a) trial an
alternative Google-Trends actor from the Apify Store through §16 gates; (b) test the actor's
residential-proxy input (raises per-success cost, may cut failures); (c) accept the limp —
resolution throughput is tolerable under the patience window. Decision to the Chairman with a
week of post-cut data.

## Cross-check on the other paid sources (single-consumer confirmed)
FMP, Finviz, QuiverQuant, Socialcrawl, CoinAPI keys exist only on the engine. X runs on the
dedicated NowTrendin2.0 app (33295718): 80 requests this month (~$0.80 metered), 4,800-post
budget fully spent → deep pulls stopped until Sept 1 (the cap enforcing, by design).
Cost Sentinel's Apify line ($18.99) matches the console ($19) — it reads the real meter.

**Open line for the Chairman:** the Cost Sentinel's **AWS $104/mo** entry — nothing in the
NowTrendIn stack runs on AWS (Heroku end-to-end). Confirm whether it belongs to another
venture; if so it should leave this product's $700-cap ledger.

---

## ADDENDUM 2026-08-11 — Full failure-data identification + fix-or-eliminate verdicts (Chairman-ordered)

### Failure inventory (complete sweep: engine 28 collectors + both actors + all paid meters)

| # | Failing item | Cost of failure | Fixable by us? | Verdict |
|---|---|---|---|---|
| 1 | **Apify sweep actor** (`apify/google-trends-scraper`): 83% of runs blocked by Google | was $58/mo → **~$20/mo** after the 2-min cap (verified live: failed-run cost $0.086→$0.028) | **NO** — all fix paths tested and exhausted (below) | **KEEP** (it resolves the attention ledger — the moat; elimination = ledger stops resolving). Replacement vendor path identified for Chairman if desired. |
| 2 | Canary issuer page (XRPC): DOWN, never succeeded | **$0** (free scrape) | **NO** — our adapter is correct; Canary's own page is stale (as-of 2026-07-31, 7 tdays > 3-tday guard → declared absence, by design) | **KEEP WATCHING** — self-heals when Canary updates their page. If stale ≥30d, drop XRPC from the A2 roster. Nothing saved by eliminating (free). |
| 3 | X posts budget exhausted (4,800/4,800 by Aug 10) | $0 extra (the cap BLOCKS spend — working as designed) | n/a | Most of the budget burned pre-fix (shared-app era). NOTE for Chairman: under the new dedicated-app pricing, 4,800 post-reads ≈ **$24/mo**, not the ~$200 the cap was sized for — raising it is now cheap, founder's call, no urgency. |
| 4 | Cost Sentinel "Firecrawl: $None" display | $0 (cosmetic) | Yes — trivial | Fix batched into next engine deploy. |
| — | Everything else | — | — | Healthy: 21/28 collectors green (2 disabled intentionally), realtime actor 125/125, CoinAPI 12/12, Coinbase premium accumulating, FMP paid plan serving. |

### Sweep fix attempts (all live-tested 2026-08-11, total test spend ~$0.11)
1. **Residential proxy** on the official actor: TIMED-OUT 2/2 (incl. a 300s leash) — **not the fix**.
2. **Query dependence**: ruled out — same query fails then succeeds; failures span mainstream + niche.
3. **Store alternatives**: `vnx0/google-trends-scraper` (5.0★) and `data_xplorer/google-trends-fast-scraper`
   (4.9★) both return trending-keyword LISTS, not interest-over-time curves — **fail §16 TYPE gate**
   (the fast-scraper silently ignored our input and returned trending searches; recorded as a
   would-be onboarding failure). No drop-in actor replacement exists on the Store today.

### The one genuine replacement path (Chairman decision, not urgent)
A dedicated Google-Trends API vendor (e.g. DataForSEO, ~$0.01/query ≈ **$10/mo** at our ~960
queries/mo) would likely take resolution reliability from 17% → ~95%+ and REPLACE the sweep actor
outright (net save ~$40/mo AND ~6× resolution throughput). It is a NEW source feeding the held-out
ledger → full §16 five-gate workup + a curve-equivalence check (run both vendors on the same
queries, compare) before any switch. On the shelf until ordered.

### Current steady state (post-cut)
Apify ≈ $90/mo total (realtime $69 legitimate + sweep ~$20 incl. residual waste), ledger resolving
~5/day at 17% actor success under the 365-day patience window. Acceptable; not silent — this line
is watched weekly by improve-system.
