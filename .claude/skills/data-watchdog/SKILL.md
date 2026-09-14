---
name: data-watchdog
description: NowTrendIn automated monitoring — runs the Source Watchdog + Pipeline Integrity agents (GET /monitor) and reports whether data is pulling and scores are healthy. Catches the two recurring failure classes (data not pulling; scores wrong/absent) per DATA_BUILDING_BLOCKS.md. Use when the user says "monitor", "watchdog", "is the data healthy", "check pulls + scoring", "run the agents", or after any collector/scoring change.
---

# /data-watchdog — automated data + scoring health agents

You run NowTrendIn's monitoring agents and report status against the building
blocks (DATA_BUILDING_BLOCKS.md, repo root). These agents catch the failure
classes the project keeps hitting: **(A) data not pulling**, **(B) scores
wrong/absent**, **(C) junk topics / catch-all congestion**, **(D) cost drift**.

**Engine (v2.0)**: `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com`
(no key needed — `/monitor` is public read-only).

## Source onboarding (B1a — hard rule, owned by Source Watchdog)

Before ANY new media/data source is linked, all 5 gates must pass (CLAUDE.md §16 /
DATA_BUILDING_BLOCKS B1a): **TYPE → ENGINE → FORMAT → CURRENCY+ACCESS → TEST→LINK→DEPLOY**.
If the user proposes a source, run the gates BEFORE wiring: classify the info type; name the
ONE pipeline it feeds; confirm dates pass `gate_date()` and topics extract clean through
`_is_quality_topic`; confirm it's current + reachable (HTTP 200, no 404/429); then test a live
sample, and only then wire + deploy (score-affecting sources also need backtest-before-ship).
The `.githooks/commit-msg` gotcha blocks a source-shaped commit lacking `[source-onboarded]`.

## The fleet (7 agents — `/monitor` returns ALL of them)
1. **source_watchdog** (`/monitor/sources`) — is data pulling? (B1/B2)
2. **pipeline_integrity** (`/monitor/pipeline`) — are scores fresh + honest? (B3/B4/B8)
3. **fragment_category_auditor** (`/monitor/quality`) — news-filler/multi-word fragments + geo mis-sorts + category clarity (B3 deep)
4. **catchall_auditor** (`/monitor/catchall`) — the news/general catch-all specialist: %, corroboration-floor health, misclassified tracked calls, lexicon candidates (B3) — runs the daily EOD report
5. **cost_sentinel** (`/monitor/cost`) — all monthly cost lines vs budgets (B7)
6. **data_subscriptions** (`/monitor/subscriptions`) — paid data-API spend & config (B7)
7. **calibration_auditor** (`/monitor/calibration`) — is the Accuracy Ledger denominator-backed (B5)

## Recently-shipped invariants the agents now protect (cite these when diagnosing)
- **Catch-all corroboration floor** — `CATCHALL_MIN_SOURCES` (default 2): catch-all
  topics need ≥2 distinct sources to score, with hard exemptions (expert-tier signal,
  high magnitude, ledger/pending). A single-source-catchall LEAK climbing = floor
  disabled or purge overdue (see `/monitor/catchall`).
- **Fragment gate** — single-word junk AND multi-word filler-anchored fragments are
  rejected at scoring + pruned each cycle (`/monitor/quality` fragments should be ~0).
- **Maturity from topic_lifecycle** — maturity_class (NEW/EMERGING/ESTABLISHED) is
  derived from real cycle count + age (not the dormant topic_maturity table); ESTABLISHED
  topics are discounted. If everything reads NEW again, the lifecycle fallback regressed.

## Steps

1. **Run the combined monitor** (one call covers all 7 agents):
   ```bash
   curl -s --max-time 30 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/monitor
   ```
   For a deeper look hit any individual endpoint listed above.

2. **Report** in this structure:

   ### Overall: <OK / WARN / CRITICAL>
   One line — `status` + `alert_count`.

   ### Source Watchdog (B1/B2 — is data pulling?)
   - `summary` healthy/total. List every alert: level · source · message.
   - CRITICAL here = a critical collector (github/hackernews/google_trends/risk)
     is DOWN/STALE → **scores are half-blind; do not trust the board**.

   ### Pipeline Integrity (B3/B4/B8 — are scores honest?)
   - `last_score_min_ago` (B4 freshness), `junk_count` (B3), `dupe_groups` (B3),
     `missing_pathway` (B8). List every alert.

3. **Diagnose** each alert using the failure-mode catalog (DATA_BUILDING_BLOCKS.md §11):
   - collector DOWN but API works → clock-only cron didn't fire (run in main cycle)
   - DOWN "quota"/500 → YouTube RSS blocked from datacenter (use Data API)
   - STALE while pulling → health window < cadence
   - junk topics → common_words.txt dictionary; dupes → _canonicalize_topic
   - scores stale → R14 / score cycle stalled
   Name the most likely cause + the fix pattern; never guess beyond the catalog.

4. **Verdict**: if OK, say so plainly. If WARN/CRITICAL, list the specific
   sources/blocks to fix, worst-first. Do NOT propose forcing/injecting data
   (violates integrity guardrail B6/objectivity).

## Output discipline
Founder-internal, numbers-direct. This is the honest health of the data behind
every score — never soften a CRITICAL. `over_budget`/cost specifics come from
`/ai/costs` + `/x/budget` (Cost Sentinel), not this agent.

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
- **For THIS skill:** Source Watchdog + Pipeline Integrity — when auditing "is data pulling", expect the new reputable RSS outlets (incl. The New Yorker) and Nasdaq Trade Halts in the risk feed; and treat a rising `format_review_queue` pending count as a date-format regression to surface (the canonical-date invariant B3a).
