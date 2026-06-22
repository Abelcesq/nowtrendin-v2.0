---
name: data-subscriptions
description: NowTrendIn data-API subscription monitor — inventories every external data API the engine pays for (AlphaVantage, Finnhub, NewsAPI.org/.ai, NewsData.io, RapidAPI, WhaleWisdom), classifies each paid/free/metered, and flags paid subscriptions with no tracked cost (untracked spend) or a cost set with no key. Use when the user says "check our subscriptions", "what data APIs are we paying for", "audit data costs", or after adding/removing a data source or API key.
---

# /data-subscriptions — paid data-API spend & config (block B7)

Runs the Data Subscriptions agent so every external data API is accounted for and
no paid subscription is silently untracked. Three classes:
1. **paid** — a real subscription; each has a `COST_*_USD` env var (default $0).
   Configured key + $0 cost = **untracked spend** → warn.
2. **free** — free / free-tier APIs (FRED, FINRA, YouTube, Guardian, GitHub, …).
3. **metered** — usage-billed, tracked on their OWN cost line (AI ledger / Apify
   live / X line) — listed for completeness, never added to the subs total.

**Engine (v2):** `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com` (public).

## Steps
1. Run the agent:
   ```bash
   curl -s --max-time 40 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/monitor/subscriptions
   ```
2. **Report** from `summary`:
   - `paid_subscriptions` · `free_apis` · `metered_elsewhere`
   - `paid_total_usd` (sum of the per-provider COST_*_USD)
   - `untracked_paid` (paid + configured + $0) — the ones owing a real number
   - `items[]` — per-API {name, configured, billing, usd}
3. **Diagnose**:
   - untracked paid API → set its `COST_*_USD` Heroku env on `nowtrendin-v2-engine`
     to the real monthly figure (or `$0` if genuinely on the provider's free tier).
   - cost set but key missing → paying for an unconfigured API; remove the cost or
     restore the key.
4. **Verdict:** clean (every paid API has a tracked cost) or list the providers
   still owing a number, then confirm `paid_total_usd` flows into the Cost
   Sentinel's "Data API subscriptions" line (`/monitor/cost`).

## Integrity
NEVER invent a dollar amount. The agent defaults every cost to $0 and flags where
a real figure is owed — the operator supplies the verified number. Costs that
can't be supported aren't asserted (no asserting anything we cannot support).

## Setting a cost
```bash
heroku config:set COST_FINNHUB_USD=50 -a nowtrendin-v2-engine
```
Part of the monitoring fleet (see `/data-watchdog`, `/topic-quality-audit`,
DATA_BUILDING_BLOCKS.md block B7 / Cost Sentinel).

## Canonical dates · sources · M/D — updated 2026-06-22

> Cross-cutting updates every data/scoring skill should know. Authoritative specs:
> `CLAUDE.md` §14–15, `DATA_BUILDING_BLOCKS.md` §3a + §5.

- **Canonical date model (✅ LIVE):** PRIMARY `signal_date` = ISO `YYYY-MM-DD` (the ONE
  sort/match/score key); SECONDARY `source_time` (the SOURCE's own HH:MM:SS) + `signal_time`
  (OUR fetch HH:MM:SS, stamped on every fetched row). Enforced by `date_utils` +
  `ingestion_gate.gate_date()`; an unparseable non-empty value → `format_review_queue`
  (human review), never guessed. Same-surge ledger floor `since=detection−30d`. Governs
  SORT/MATCH only — removes NO scoring input. Never reintroduce raw `[:10]` date slicing.
- **New sources (✅ LIVE):** reputable-direct RSS roster incl. **The New Yorker** (news+business);
  **Nasdaq Trade Halts** in the risk module (stage-2; `signal_date`=HaltDate, `source_time`=HaltTime).
- **M/D reweighting (⏳ IN DESIGN — NOT shipped; backtest-before-ship gates it):** reputable ≠
  automatic mainstream full weight — 1 reputable = ½ weight, FULL only on ≥2 DISTINCT reputable
  (distinct `source_name`; the "Belgium vs Iran" case). Research/early-signal outlets (War on
  Rocks, Rest of World, Global Issues, Pew, RAND, NBER) → Dark Matter via `blog_collectors`
  GHOST_FEEDS at **expert/niche tier** — the D-vs-M router is `platform_tier`, NOT `is_organic`;
  do NOT route them through `_RSS_FEEDS`/`_news_write` (which forces `mainstream` and suppresses
  the early signal).
- **For THIS skill:** Source/subscription inventory — The New Yorker (free RSS) and Nasdaq Trade Halts (free exchange RSS) are now in the roster; the research/early-signal outlets are planned as FREE expert-tier feeds. No new paid-API spend from any of these.
