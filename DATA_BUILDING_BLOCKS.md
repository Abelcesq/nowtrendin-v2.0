# Now TrendIn — Data & Scoring Building Blocks
**The foundation for monitoring agents.** *Last updated 2026-06-16.*

> Why this exists: we keep hitting the same two failure classes — **(a) data not
> pulling** and **(b) scores wrong/absent**. This document is the single, durable
> contract that defines every source, every pipeline stage, the invariant that
> must hold at each, how to check it, and what "broken" looks like — so monitoring
> agents can be built directly against it. Every claim here is grounded in the
> live engine (`transfer/`), not aspiration.

---

## 0. The pipeline in one line
```
COLLECT → EXTRACT → CONSOLIDATE → FILTER → SCORE → CALIBRATE → DUAL-PATHWAY →
PERSIST → PRECOMPUTE → SERVE
```
Each arrow is a building block with an **invariant**, a **check**, and a **failure
signal**. An agent owns one or more blocks and watches its invariants.

Engine: Heroku **`nowtrendin-v2-engine`** (one Postgres, one standard-2x dyno,
scheduler in-process). Internal key header `X-Internal-Key`. Clients (web/desktop/
mobile) are read-only.

---

## 1. SOURCE REGISTRY — what we pull, how, cost, SLA

Source of truth in code: `collector_health.COLLECTOR_EXPECTATIONS` (freshness SLA +
criticality) and the collectors in `gravitational_anomaly_detector.start_scheduler`.

### Attention sources (feed Trends)
| Source | Access | Auth | Cadence | Cost | Critical | Notes |
|---|---|---|---|---|---|---|
| github | REST API | token | 6h (main cycle) | free | ✅ | core dev signal |
| hackernews | Firebase API | none | 6h | free | ✅ | core dev signal |
| blogs (dev.to, hashnode, discourse, wordpress, medium…) | RSS/API | none | 6h | free | — | `blog_collectors.py` |
| newsapi_org | aggregator API | key | 6h | paid tier | — | reputable-allowlist filtered |
| newsapi_ai | aggregator API | key | 6h | paid tier | — | Event Registry |
| newsdata_io | aggregator API | key | 6h | paid tier | — | |
| gdelt | open API | none | 6h | free | — | global media |
| bluesky / lemmy / mastodon | open API | none | 6h | free | — | early-chatter tier (replaced Reddit) |
| google_trends | **Apify actor** | token | clock cron 00:30/06:30/12:30/18:30 UTC | ~$0.57/run (~$68/mo) | ✅ | paid → controlled cadence |
| youtube (mainstream coverage) | YouTube Data API v3 | key | 6h (main cycle) | quota 10k u/day | — | per-topic mainstream denominator |
| broadcast (22 channels) | YouTube Data API v3 | key | 6h (main cycle) | quota | — | CNBC/CNN/Bloomberg… uploads |
| creators (5 finance) | YouTube Data API v3 | key | 6h (main cycle) | quota | — | Meet Kevin, Graham Stephan… |
| wikipedia / google-trends-RSS | discovery | none | 6h | free | — | `discovery_collectors.py` (open-world) |
| x (Twitter) | X API v2 | bearer | clock cron + on movers | **post budget 12k/mo** | — | volume scan free; deep pulls budgeted (`/x/budget`) |
| reddit | — | — | OFF | — | — | **licensing — intentionally disabled** |

### Market/risk sources (feed Market Signal)
| Source | Access | Auth | Purpose |
|---|---|---|---|
| Finnhub | REST | key | fundamentals, price, beneficiary cycle |
| FINRA | file API | UA | short interest |
| OFR | open | none | macro funding-stress / leverage |
| WhaleWisdom | REST | key | 13F institutional positioning |
| Alpha Vantage | REST | key (free 25/day) | news/retail coverage, sentiment |
| Yahoo Finance | scrape/API | none | market news |

### AI services (definitions + grades)
| Service | Use | Cost control |
|---|---|---|
| Perplexity | topic definitions + grade research | **$20/mo unified cap** (`/ai/costs`, guardrail 5) |
| Anthropic (Claude) | grade synthesis | same cap |

**INVARIANT (B1):** every source above is either pulling within its SLA window
**or** explicitly OFF with a documented reason. **CHECK:** `GET /health/collectors`
+ `GET /usage`. **FAILURE:** a `critical:true` source is `DOWN`, or a paid source
shows 0 calls when it should be running.

---

## 2. COLLECTION HEALTH — is data actually arriving?

Code: `collector_health.py` (`log_collector_run`, `get_health_report`,
`should_trust_scores`), called via `_log_health()` after every collector in the
scheduler.

- Each collector logs **success/failure + signal_count + timestamp** every run.
- Status = `HEALTHY` (fresh + signals) · `DEGRADED` (ran but 0 signals) ·
  `STALE` (last success older than its window) · `DOWN` (consecutive failures /
  never ran / long gap).
- **Freshness window MUST exceed the cadence + margin** — main-cycle collectors
  are 420m (6h cadence + 1h). *(This was a real bug: 120m windows on a 6h cadence
  made news/github flap false-STALE.)*

**INVARIANT (B2):** no `critical` collector is DOWN; no source is DEGRADED for >2
consecutive cycles. **CHECK:** `/health/collectors` (per-source status) and
`/health` (`should_trust_scores`). **FAILURE:** critical DOWN ⇒ scores are
half-blind — do not trust the board until restored.

**Known failure modes (caught this session):**
- Collector registered on a **clock-only cron** never fires if the dyno restarts
  before the slot → moved free collectors into the **boot+6h main cycle**.
- **YouTube public RSS returns HTTP 500 from datacenter IPs** → must use the Data
  API, not RSS.
- Health window shorter than cadence → false STALE.

---

## 3. EXTRACTION INTEGRITY — are topics real, deduped, clean?

Code: `extract_topics_from_text`, `_extract_entities`, `_is_quality_topic`
(common-word `common_words.txt` + `GENERIC_JUNK` + `PROFANITY`),
`_canonicalize_topic` / `_topic_key` (consolidation), `_consolidate_window_keys`.

**INVARIANTS (B3):**
- No bare **common word** as a topic (`suffering`, `saying`) — rejected
  regardless of volume.
- No **morphological/entity duplicates** (`japan`≠`japanese`, `trump`≠`Donald
  Trump`) — folded to one canonical key before scoring.
- No **profanity / news-filler fragments** ("iran announce deal").
**CHECK:** sample `GET /scores?limit=15` and `/topics?limit=200` for junk/dupes;
re-run the generator if the dictionary drifts. **FAILURE:** junk/dupes in the
served list ⇒ extraction regression.

---

## 4. SCORING COMPLETENESS — did every scoreable topic get scored?

Code: `score_all_topics` (SQL gate `HAVING COUNT>=MIN_TOPIC_APPEARANCES OR
MAX(engagement_raw)>=HIGH_MAGNITUDE_ENG`), `_precompute_serve_payloads`.

**INVARIANT (B4):** a full score cycle completes without OOM/timeout, scores
~12–13k topics, and writes `serve_payload` for the top N. **CHECK:** `/health`
`last_score` recency; `/stats` topic count; logs `SCORED N PRECOMPUTED M`.
**FAILURE:** score cycle stops mid-run (R14 / 79ms-per-query), or `last_score`
stale > 1 cycle.

**Known gap (SpaceX class):** a genuinely-mainstream topic with **< 3 mentions /
cycle and low magnitude is filtered before scoring** — it exists but `detection =
None`. Correct fix is *more/better collection* (so it crosses the gate
organically), **not** force-injecting it (would violate B6 objectivity).

---

## 5. CALIBRATION ACCURACY — are the numbers honest?

Code: `dual_pathway.py` (expert vs mainstream; baseline-relative fame-vs-diffusion;
news-outlet corroboration → `mainstream_confirmed`; tier-migration),
`community_tiers.py`, `signal_calibration_integration`, `market_signal_engine.py`
(z-score baseline-relative tiers), `google_trends_validation` + `accuracy_ledger_
enhanced` (the **Accuracy Ledger** — the moat).

**INVARIANTS (B5):**
- `backtest_dual_pathway.py` **all cases pass before any calibration ship**
  (backtest-before-ship, hard rule).
- Scores are **baseline-relative** (deviation from a topic's own norm), so fame
  ≠ movement. Market tiers (ELEVATED/ACTIVE/BUILDING/ROUTINE/DORMANT) are z-score
  calibrated — at-baseline reads ROUTINE *honestly* (don't fudge thresholds).
- Accuracy is reported **with its denominator** (`/accuracy/ledger`), never
  inflated. Small-sample is stated as small-sample.
**CHECK:** run `backtest_dual_pathway.py`; `/accuracy/ledger` hit-rate + pending;
spot-check `detection_pathway` / `mainstream_confirmed` on news topics.
**FAILURE:** a backtest case fails, or a published number lacks a real denominator.

---

## 6. INTEGRITY GUARDRAILS — the non-negotiables

Mirror of the founder hard rule (`feedback-integrity-standard`). Every addition
**and every public-facing claim** must pass:
1. **Gradient-Score objectivity** — nothing contaminates the score; validators sit
   downstream, never feed back. No force-injected topics.
2. **No circular metrics** — a validator uses inputs independent of what it validates.
3. **Reputable, licensed sources only** — allowlist enforced; unlicensed (Reddit)
   stays OFF.
4. **Measurement, not advice** — never buy/sell; disclaimers on every financial output.
5. **Never assert what we can't support** — no hardcoded/unverifiable performance
   or accuracy claims; "Illustrative" labels on sample data; wire to live + show
   the denominator, or remove.

**CHECK:** review any new source/metric/claim against all five. **FAILURE:** any
violation — surface it and propose the clean version; do not ship.

---

## 7. COST / BUDGET CONTROL — spend never runs away

| Budget | Limit | Check | Code |
|---|---|---|---|
| AI (Perplexity + Anthropic) | **$20/mo** | `GET /ai/costs` (`over_budget`) | unified `ai_costs` ledger; explainer/backfill/grade skip when over |
| X posts | **12k/mo** | `GET /x/budget` | volume scan free; deep pulls budgeted |
| YouTube Data API | 10k units/day | `/usage` youtube | cheap calls + caching |
| Apify Google Trends | ~$68/mo | clock cron only | not boot-fired |
| Dyno memory | 1GB (standard-2x) | Heroku metrics R14 | scoring co-located, every 6h only |

**INVARIANT (B7):** no budget exceeds its cap; paid AI calls stop at $20/mo.
**FAILURE:** `/ai/costs.over_budget = true`, X 429 storms, or R14 memory warnings.

---

## 8. SERVING CONSISTENCY — one DB, every platform identical

**INVARIANT (B8):** all surfaces (web `web-terminal` → Pages, desktop Tauri,
mobile `frontend`) read the **same** v2 engine; none re-score. Serve-time filters
(quality, category) apply uniformly. Watchlists sync via `backend` `/api/watchlists/`.
**CHECK:** same topic shows the same score on web vs mobile; `/scores` returns
`category` + audit fields. **FAILURE:** a client computing its own scores, or
divergent numbers across platforms.

---

## 9. SKILLS — the current manual checks (agents formalize these)

| Skill | Block(s) | What it verifies | Endpoint(s) |
|---|---|---|---|
| **data-health** | B1, B2, B7 | collector status + API cost + ledger | `/usage` `/health/collectors` `/accuracy/ledger` |
| **accuracy-sweep** | B5 | honest hit-rate + lead-time | `POST /accuracy/validate` → `/accuracy/ledger` |
| **beneficiary-backtest** | B5 | financial weights flag winners EARLY not late | `/beneficiary/backtest/*` |
| **risk-verify** | B1, B4 | a company's market layers populated | `/risk/scores` `/beneficiary/{t}` |
| **tier-gate-audit** | B8 | access control via `canAccess`/`TierGate` only | frontend grep |

All skills point at the **v2** engine (`nowtrendin-v2-engine`).

---

## 10. MONITORING AGENTS — built on these blocks

Each agent owns blocks, runs on a cadence, reads the listed endpoints, and raises
a typed alert. (These are specs to build; the checks already exist as endpoints.)

> **Status: ALL agents LIVE.** Runtime pollers in `monitoring_agents.py` →
> `GET /monitor` (combined), `/monitor/sources`, `/monitor/pipeline`,
> `/monitor/cost`, `/monitor/calibration` (public, read-only, no AI). Invokable
> skills: **`/data-watchdog`** (A+B), **`/frontend-consistency`** (F),
> **`/integrity-reviewer`** (E gate). A 6th agent — **Frontend Consistency** —
> watches terminal↔mobile UI parity.

### A. Source Watchdog — owns **B1, B2** ✅ LIVE
- **Every cycle (6h):** `GET /health/collectors`, `/usage`.
- **Alert if:** any `critical` collector DOWN; any source DEGRADED ≥2 cycles; a
  paid source at 0 calls; freshness past SLA.
- **Action:** name the source, the last-success age, and the likely cause
  (cron-not-fired / quota / key / datacenter-block) from the failure-mode list (§2).

### B. Pipeline Integrity Monitor — owns **B3, B4, B8** ✅ LIVE
- **Each score cycle:** sample `/scores?limit=15` + `/topics?limit=200`.
- **Alert if:** junk/common-word or duplicate keys appear; `last_score` stale >1
  cycle; `/scores` returns 0 or errors; a topic's `category`/audit fields missing.

### C. Calibration Auditor — owns **B5** ✅ LIVE (`/monitor/calibration`)
- **Runtime:** `/accuracy/ledger` honesty — flags small-sample so no undefendable
  hit-rate is published. **Deploy gate:** run `backtest_dual_pathway.py` before any
  calibration ship (block on fail).

### D. Cost Sentinel — owns **B7** ✅ LIVE (`/monitor/cost`)
- AI $/mo (vs $20 cap) + X posts/mo: warn at 80%, critical at exhausted. (R14
  dyno memory watched via Heroku metrics, outside the process.)

### E. Integrity Reviewer — owns **B6** ✅ LIVE (gate skill `/integrity-reviewer`)
- On every new source/metric/claim/PR: run the 5 guardrails; block + propose
  clean alternative on any violation.

### F. Frontend Consistency — owns **B8 (UI parity)** ✅ LIVE (skill `/frontend-consistency`)
- Both sites up (Pages terminal + mobile-web); terminal `SIGNAL_FILTERS` ==
  mobile `CATEGORY_DEFS`; same category chips + key actions (Pull Trends, Trends
  label, Watchlists). Web may add MORE filtration; it must not DIVERGE on shared
  labels/filters/actions.

---

## 11. Recurring failure modes (the catalog agents watch for)
| Symptom | Root cause | Fix pattern |
|---|---|---|
| Collector DOWN despite API working | clock-only cron didn't fire | run in boot+6h main cycle |
| Collector DOWN "quota" | YouTube RSS 500 from datacenter | use Data API, not RSS |
| False STALE | health window < cadence | window = cadence + margin (420m) |
| Junk topics (`saying`) | weak filter | `common_words.txt` dictionary |
| Dupes (`japan`/`japanese`) | no canonicalization | `_canonicalize_topic` + window consolidation |
| Topic absent despite news (SpaceX) | < scoring threshold | improve collection, never force-inject |
| Score cycle stalls | R14 / 79ms-per-query local | co-locate scoring; 1GB dyno; 6h cadence |
| `/scores?limit` high → 0 | per-row enrichment OOM | keep limits modest; serve_payload fast-path |
| Unverifiable stat on UI | hardcoded marketing number | remove / wire live with denominator |
| X 429 storms | rate limit | back off; pace the volume scan |

---

*Build order for agents: **Source Watchdog** and **Pipeline Integrity Monitor**
first (they catch the two recurring failure classes), then **Cost Sentinel**,
**Calibration Auditor**, and the **Integrity Reviewer** gate. Each maps 1:1 to the
blocks above and to an existing health endpoint — nothing new to instrument first.*
