---
name: project-data-building-blocks
description: "NowTrendIn data+scoring monitoring foundation — DATA_BUILDING_BLOCKS.md: source registry, pipeline invariants, failure-mode catalog, monitoring-agent specs"
metadata: 
  node_type: memory
  type: project
  originSessionId: 46ab8dd5-70c6-49dc-8816-b88ccdd2bb93
---

`DATA_BUILDING_BLOCKS.md` (repo root of `NowTrendin v2.0`) is the durable contract for keeping data pulling + scores honest — built because the project keeps hitting two recurring failure classes: data not pulling, and scores wrong/absent.

It defines, grounded in the live engine (`transfer/`): the **source registry** (every collector + auth + cadence + cost + SLA, from `collector_health.COLLECTOR_EXPECTATIONS`), the **pipeline** (collect→extract→consolidate→filter→score→calibrate→dual-pathway→persist→precompute→serve) with an invariant + check-endpoint + failure-signal per stage (blocks B1–B8), the **5 integrity guardrails**, the **budgets** (AI $20/mo `/ai/costs`; X 12k/mo `/x/budget`; YouTube 10k u/day; Apify ~$68/mo; dyno R14), the **skills→blocks** mapping, and **5 monitoring-agent specs**: Source Watchdog (B1/B2), Pipeline Integrity Monitor (B3/B4/B8), Calibration Auditor (B5), Cost Sentinel (B7), Integrity Reviewer gate (B6). Each agent maps 1:1 to a block + an existing health endpoint (`/health/collectors`, `/usage`, `/accuracy/ledger`, `/ai/costs`, `/x/budget`, `/stats`).

Key recurring failure modes catalogued: clock-only cron not firing (→ run in boot+6h main cycle); YouTube public RSS returns HTTP 500 from datacenter IPs (→ use Data API, not RSS); health window < cadence = false STALE (→ window 420m for 6h cadence); junk topics (→ `common_words.txt`); dupes (→ `_canonicalize_topic`); topic below scoring threshold like SpaceX (→ improve collection, NEVER force-inject — violates objectivity); R14 score stall; unverifiable UI stats (→ remove/denominator).

When building the monitoring agents, build Source Watchdog + Pipeline Integrity Monitor first. See [[project-gradient-calibration]] and [[feedback-integrity-standard]].
