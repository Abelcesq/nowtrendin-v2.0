# Checkpoint — 2026-06-10 Health + Audit

Snapshot after the homepage redesign, Market pipeline split, dual-pipeline
YouTube/Yahoo Finance wiring, and the connection-pool-leak fix.

---

## 1. Engine health — ✅ operational

| Check | Result |
|---|---|
| `GET /health` | `operational`, v1.0.0 |
| `GET /scores` | 200 · **50 results** (the pool-exhaustion 500 is fixed) |
| Web dyno | `up` (Basic) |
| Worker dyno | `up` (Basic) — scheduler in-process |

### Connection-pool bug (fixed this session)
`/scores` was returning **500 — psycopg2 PoolError: connection pool exhausted**.
Root cause: `conn.close()` lived inside `try` blocks in `trend_beneficiary_wire`
+ `theme_extension`; any `.execute()` error leaked the connection until the pool
drained. Fixed with `try/finally` in all three paths. Verified 200 + 50 results.

---

## 2. Collector health — ⚠️ expected post-deploy staleness (NOT a failure)

At check time most collectors read STALE/DOWN. **This is an artifact of frequent
redeploys, not a broken pipeline:**

- APScheduler `interval` jobs fire *after* the first interval elapses; every deploy
  restarts the worker and **resets that clock**. The 6 h collectors (google_trends,
  youtube, creators, broadcast) hadn't reached their first post-restart cycle.
- `broadcast` / `blogs` / `gdelt` = "never recorded" → brand-new or best-effort
  collectors whose first cadence run hasn't landed.
- Manual triggers prove the collectors themselves work (Yahoo Finance counter went
  1 → 34 today after a manual `/risk/collect`).

> **Operational rule (reaffirmed):** during any continuous-accuracy run, do **not**
> redeploy the engine repeatedly — each deploy resets the scheduler and keeps
> collectors perpetually "stale." Batch engine changes, deploy once, let it run.

---

## 3. Accuracy ledger — ✅ honest-denominator logic live, sample young

`POST /accuracy/validate` → sweep started (apify). `GET /accuracy/ledger`:

| Field | Value |
|---|---|
| total resolved | 2 (both LAGGED) |
| pending | **206** |
| honest hit rate | 0.0% (too few resolved to mean anything) |
| false positives counted | yes (honest denominator present) |
| smallSample flag | true |

The enhanced ledger (`accuracy_ledger_enhanced.py`) is integrated — false positives
are counted in the denominator and `smallSample` guards against over-claiming. The
206 pending detections need their timeout windows to elapse before the rate is
meaningful. **Do not quote a hit rate externally until sample ≥ 20 resolved.**

---

## 4. Tier-gate audit — ✅ PASS

Every access decision routes through the source of truth:
- `canAccess(tier, feature)` — PullTrends, PullMarket, search nav, TierGate
- `isDataAccessible(tier, age)` — the data-aging waterfall on the feed
- `<TierGate>` — restricted regions

The only `tier === 'x'` literals found are **cosmetic or routing**, not feature
gates: Button visual variant, MembershipPlans "popular" badge, and login/splash
routing on whether a plan is chosen. **No hardcoded feature gates outside
`constants/tiers.ts`.** (Backend `PullMarketView` checks `tier != 'enterprise'`
directly — legitimate, it's the server enforcement boundary, separate from the
frontend rule.)

---

## 5. "Now Trending" Direction Engine — reviewed, two bug-fixes applied, design decision pending

`6_9_2026_now_trending.py` (downstream convergence-validation module). Assessment
in the session notes. **Two correctness refinements applied + verified:**
1. Stage migration is now **volume-aware** — late-stage drift with falling volume
   reads as decay, not spreading (fixed Case-4 misread; stage vote flipped to −1.00).
2. Conflict-case interpretation copy no longer asserts "signals agree" then
   contradicts itself (hedged base sentence when validation ≠ CONFIRMED).

**Not yet wired to the live app** — pending a naming/architecture decision (the new
"direction validation" concept collides with the existing **N = nowtrendin_score**
metric, which already feeds the Gradient Score). See session analysis.

**Data feasibility (verified):** `pull_history` stores daily per-topic
detection/confidence/overall/stage/total_signals. So 3 of 4 external factors are
buildable (score trajectory, volume velocity via total_signals, stage migration via
signal_stage) at **daily** granularity needing 3+ days of history. **Platform
breadth over time is NOT persisted** — pull_history has no platform_count column.

---

## State summary

- Engine: v-current, both dynos up, `/scores` healthy (50)
- Pipelines: Trends (`/collect`) + Market (`/risk/collect`) cleanly separated
- Dual-feed: YouTube (5 creators + 22 broadcast) and Yahoo Finance feed BOTH
- Skills available: deploy, data-health, risk-verify, tier-gate-audit,
  accuracy-sweep, beneficiary-backtest, expo-recover
- Expo: LAN mode on `exp://192.168.68.52:8081` (firewall rule + same-WiFi required)
