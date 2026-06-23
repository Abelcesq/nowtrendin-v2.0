---
name: project-read-path-prewarm
description: "Read-path performance: Prewarm Agent (15), superset-cache + O(1) offset slices, progressive 100-at-a-time pagination on all web list feeds"
metadata: 
  node_type: memory
  type: project
  originSessionId: 46ab8dd5-70c6-49dc-8816-b88ccdd2bb93
---

How the v2 engine keeps every list feed fast (2026-06-23). The pattern for ALL list
endpoints (`/scores`, `/topics`, `/history/recent`, `/risk/scores`): compute a
**limit-INDEPENDENT superset once** via a `_compute_*_full()` builder, cache it
(`CACHE_TTL_SCORES_FULL`, default 1800s), and serve **O(1) `(offset, limit)` slices**.
Clients page **100 at a time** (no caps, no giant payloads); the heavy build runs at most
once per cache window. Endpoints return `total` so the client knows when it's done.

**Prewarm Agent (Agent 15 — operational, read-only re: data).** A daemon thread
(`prewarm-agent`) started in the **API process** at `@app.on_event("startup")`
(`PREWARM_ENABLED`). Every `PREWARM_INTERVAL_MIN` (default 25 min — deliberately INSIDE the
30-min cache TTL so it never lapses) it recomputes + caches all the supersets: scores,
topics, `history` at `7d`/`24h`/`12h`, and `risk`. **Per-process caveat (hard):** it MUST
run in the API/web process — the worker dyno has a SEPARATE `_cache`; warming there warms the
wrong cache (the original mobile cold-load bug). `GET /prewarm` is NON-BLOCKING (kicks a
background warm, returns last status) — warming all five supersets synchronously (~38–44s)
exceeds Heroku's 30s router limit. It writes ONLY the in-memory read cache, never a score
(INV-1 holds — it caches the same `serve_payload`). Full spec: `AGENT_CHARTER.md` Agent 15.

**What it fixed.** The History feed (`/history/recent`, the web History view) was uncached →
~6s / 2.1MB on the 7d view (the visible "Loading…" delay); now ~0.4s compute from the warm
cache. Trends was already cached; Market got the same superset-cache + prewarm for full
parity. Web client loaders: `api.ts` `topicsAll()` / `historyAll()` / `riskAll()` (loop pages
of 100, fire `onBatch` per page so the UI paints progressively); History.tsx + MarketSignal.tsx
use them with a token guard against stale window-switch batches.

**Remaining:** the History full payload is still ~2MB transfer (2000 topics × sparkline) — a
separate optimization (paginate the History list UI like Trends) if needed; the compute delay
is gone.

See [[serve-payload-cache-gotcha]] (the per-process cache + regenerate-serve_payload gotcha)
and [[project-date-time-canon]] (Agent 16, the other agent added this session).
