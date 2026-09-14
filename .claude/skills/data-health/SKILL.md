---
name: data-health
description: NowTrendIn founder-only cost + collector health dashboard. Pulls /usage (API call costs today/7d/30d/all-time), /health/collectors (which collectors are HEALTHY/STALE/DOWN), and /accuracy/ledger (Google Trends accuracy hit-rate) in one pass and formats a founder-facing report. Use when the user says "data health", "how is the engine doing", "check costs", "API usage", "collector status", "what's running", or asks about financial viability of data sources.
---

# /data-health — NowTrendIn engine health + cost dashboard

You produce a single founder-facing report from THREE engine endpoints. ALL are internal-key gated.

**Internal key**: `nt-internal-7f3a9c2e5b81` (header `X-Internal-Key`).
**Engine URL**: `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com` (v2.0 — the canonical engine; the legacy v1 `nowtrendin-e62dcb9ecb69` is frozen).

## Steps

1. **Fetch all three in parallel** via Bash:
   ```
   curl -s --max-time 20 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/usage -H "X-Internal-Key: nt-internal-7f3a9c2e5b81"
   curl -s --max-time 20 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/health/collectors -H "X-Internal-Key: nt-internal-7f3a9c2e5b81"
   curl -s --max-time 20 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/accuracy/ledger
   ```

2. **Parse and report** in this exact format:

   ### Cost — last 30 days
   Top 5 sources by call count (today / 7d / 30d / all-time), then total today + total 30d.

   ### Collector health
   List any STALE or DOWN collector with its `detail`. If all HEALTHY, just say "All N collectors HEALTHY". Flag any CRITICAL problems separately.

   ### Accuracy ledger
   Honest hit-rate, lead-time median, total detections, pending count. If empty, say so.

3. **Surface anomalies** at the end as a single section "⚠ Watch":
   - Any source with calls > 2× its 7d average today (cost spike)
   - Any collector STALE > 12h that's marked critical
   - Accuracy hit-rate dropping vs prior period (if data available)
   - Sources with $cost-per-call > $0.10 estimated (high-cost API exposure)

## Output

This is **founder-internal**. Don't soften or hedge — give numbers directly. Cost data NEVER leaves this report (do not post to PRs, never log to public files). The user is the founder using it for financial viability assessment.

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
- **For THIS skill:** Overall pipeline health — new sources (The New Yorker, Nasdaq halts) in the roster; the canonical-date invariant (B3a) and the `format_review_queue` pending count are now part of a healthy pipeline; M/D reweighting is in design (not yet shipped).
