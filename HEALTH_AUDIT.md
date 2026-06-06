# Now TrendIn 2.0 — Deep Health Audit

**Date:** 2026-06-06
**Scope:** calculations, calibration, data points, data sorting, pull speed, frontend display
**Engine:** `nowtrendin` (FastAPI) · **Backend:** `nowtrendin-backend` (Django) · **DB:** Heroku Postgres essential-0

> Severity key: 🔴 critical (product looks broken) · 🟠 important · 🟢 healthy / fixed this session

---

## 0. Executive summary

The platform is **up and fast on warm cache**, and the outage that was returning
30s timeouts/500s on `/scores` is fully resolved. **However, the single biggest
problem is data quality: every scored topic currently sits below 35/100, and the
top of the feed is blog/GitHub tokenization noise** (`threejs`, `openai openai-api`,
`pdf chat`). This is not a formula bug — it is caused by (a) the primary niche
source (Reddit) producing **zero** signal because no credentials are configured,
(b) GitHub running unauthenticated/rate-limited, and (c) high-volume low-quality
blog sources fragmenting the corpus into ~2,650 micro-topics of ~3 mentions each,
none of which can accumulate enough signal to score as a real trend.

**Fix the two config gaps (Reddit + GitHub creds) and add a sort tie-breaker and
the feed quality jumps immediately — no engine code change required for the creds.**

---

## 1. Pull speed 🟢 (warm) / 🟠 (cold)

| Endpoint | Cold | Warm |
|---|---|---|
| `/scores?limit=20` | 6.2s | 0.42s |
| `/scores?limit=50` | 10.7s | 0.56s |
| `/scores/{topic}` | 0.37s | 0.28s |
| `/x/budget` | 1.36s | 0.34s |
| `/risk/scores` | 1.0s | 0.52s |
| `/trending`, `/anomalies` | <0.9s | <0.36s |

- **Warm cache (300s) is excellent** (<0.6s everywhere).
- 🟠 **Cold `/scores` is 6–11s** because each cache-miss calibrates 160–200
  candidate rows in Python (per-row DB ops), amplified by the over-fetch needed
  for the noise filter. Every ~5 min one unlucky request eats this.
  **Recommendation:** precompute the calibrated + noise-filtered score set at
  **scoring time** (worker) and have `/scores` read it directly. Removes per-serve
  calibration entirely and makes cold == warm.

## 2. Database 🟢 (fixed this session)

- `velocity_scores` had ballooned to **135k rows / 100 MB** with no index → the
  latest-per-topic `GROUP BY` self-join caused the 30s timeout outage.
- **Fixed:** added 4 indexes, pruned to 30 cycles/topic (→71k rows), and added
  **automatic per-cycle pruning** in the worker (`_prune_velocity_scores`,
  `KEEP_CYCLES_PER_TOPIC=30`) so it cannot re-bloat.
- Connections healthy at **5/20**.
- 🟠 `anomaly_log` is **24,777 rows** and growing unbounded — add a retention prune.
- 🟠 `topic_signals` (82k/40MB) and `topic_registry`/`topic_lifecycle` (2,651 rows)
  are inflated by topic over-fragmentation (see §4).

## 3. Data collection (data points) 🔴

48h volume = **4,642 signals across 9 platforms**, but the mix is wrong:

| Platform | 48h count | Note |
|---|---|---|
| wordpress | 1,614 (35%) | 🟠 low-quality blog spam, fragments topics |
| devto | 648 | ok |
| github | 432 | 🟠 unauthenticated → 60 req/hr cap |
| discourse | 312 | ok |
| hackernews | 233 | ok |
| ghost / medium / youtube / blogger | 137 / 119 / 45 / 21 | ok |
| **reddit** | **0** | 🔴 **no `REDDIT_CLIENT_ID`/`SECRET` configured** |

- 🔴 **Reddit is the spec's #1 niche source** (LocalLLaMA, MachineLearning, etc.) and
  it is completely dark. The Gradient-Strength "niche vs mainstream" ratio — the
  largest scoring component — is being computed without its best input.
- 🟠 **No `GITHUB_TOKEN`** → GitHub collection throttled to 60 req/hr (vs 5,000).
- Engine config has only 13 vars; **missing: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `GITHUB_TOKEN`.**

## 4. Calculations / scoring 🟢 (served) / note on raw

- The **detection formula weights are correct** (G33+D19+I16+M9+C5+P6+N12 = 100). ✅
- **Important raw-vs-served distinction:** the `velocity_scores` table stores
  **raw** scores whose latest-per-topic distribution looks degenerate
  (`max 27.5, mean 15.7, all <35`). But that is **pre-calibration**. The `/scores`
  serve path applies calibration + AI floor, which lifts genuine topics into a
  healthy range. Live served feed after the §5 fix:
  ```
  mcp            det 88  (90 mentions)
  ai-powered     ov 51.7
  ai-safety      ov 51.0
  developer-tools ov 50.8
  Spacex ipo     ov 44.6 (97 mentions)
  ```
- So the scoring engine is functioning; the earlier "everything is junk" symptom
  was a **sorting** problem (§5), not a math problem.
- 🟠 Still worth doing: restore Reddit + GitHub and reduce fragmentation so more
  topics build multi-cycle Inertia/Persistence and reach the breakout band.

## 5. Data sorting 🟢 (fixed this session)

- `/scores` sorts by score DESC, over-fetches, noise-filters, then truncates. ✅
- 🟢 **Fixed the core feed-quality bug:** previously hundreds of topics were tied
  on raw score, so ordering among them was effectively random and 3-mention
  fragments (`threejs`, `pdf chat`) surfaced at the top. Added a deterministic
  tie-breaker — `ORDER BY score DESC, total_mentions DESC, scored_at DESC`.
  The feed now leads with real high-volume trends (`mcp`, `ai-safety`, `Spacex ipo`).

## 6. Calibration 🟢 / 🟠

- Serve-time `apply_calibration` runs per row and even **writes** (maturity update)
  during a read request — architectural smell and part of the cold-latency cost.
  Fold into the precompute-at-scoring recommendation (§1).
- 🟢 **N "now trending" fixed:** the serve path read the wrong key
  (`nowtrend_internal` vs stored `nowtrendin_score`), leaving N at 0/pending.
  Now wired; `component_groups.nowtrendin_demand` carries the real value (verified 46.66).
- 🟢 Noise filter (`is_meaningful_topic`) + AI floor active.

## 7. Frontend display 🟢 / 🟠

- 🟢 **N "Now Trending"** now renders in the breakdown + a chip on the detail screen.
- 🟢 **AI variation map + tier badge + score explanation** now render on the detail
  screen when the engine returns a taxonomy-recognized topic.
- 🟠 Pre-existing TypeScript errors (unrelated to this work):
  - `profile/notifications.tsx`: `User` type missing `notifyEmail` / `notifyPush`.
  - `risk/[key].tsx`: risk-lens object missing `detect` on some union members.
- Tier data-aging gating present via `firstSeenAt`.

---

## Prioritized recommendations

| # | Pri | Action | Effort |
|---|---|---|---|
| 1 | 🟠 partial | `GITHUB_TOKEN` set (✅, 5000/hr — rotate, was pasted in chat); Reddit creds still pending | config only |
| 2 | ✅ done | Sort tie-breaker (`total_mentions DESC, scored_at DESC`) — feed now leads with real trends | done |
| 3 | ✅ done | Reduce fragmentation: `MENTIONS_FLOOR=5` on `/scores` + `MAX_TOPICS_PER_POST=8` | done |
| 4 | ✅ done | Precompute calibrated serve_payload per cycle → cold `/scores` 10.7s→1.4s | done |
| 5 | ✅ done | Retention prune for `anomaly_log` (auto, 30-day, keeps confirmed) | done |
| 6 | 🟠 P2 | Fix the two pre-existing tsc errors; fix Hashnode collector | small |
| 7 | ✅ done | Ported the **extensions layer** → `/enterprise/methodology`, `/enterprise/scores/{key}/audit`, `/enterprise/scores/{key}/scenarios` (7-component, Postgres, no new tables) | done |
| 8 | 🟠 P2 | Engine: AI-taxonomy override boosts detection/confidence but not `overall_score` (e.g. mcp overall 46 < det 88). App shows dual score so cosmetic; reconcile for consistency | small |
| 9 | 🟢 next | Surface the enterprise audit/scenarios in the app (frontend, currently delayed) | small |

---

## Fixed during this session

- Connection-pool exhaustion (pool 10→8/dyno, explainer on-demand, aux tables at startup).
- `/scores` 30s timeout (indexes + prune + auto-prune per cycle).
- `/scores` empty feed (over-fetch candidates before noise filter, then truncate).
- N "now trending" gap (backend key fix + frontend render).
- AI variation map + tier badge + score explanation surfaced in the app.
- **Feed quality**: sort tie-breaker so real high-volume trends lead instead of noise.
- **Cold `/scores` 10.7s → 1.4s**: worker precomputes calibrated `serve_payload`
  per cycle; serve reads it directly instead of recalibrating 160–200 rows/request.
- `anomaly_log` auto-retention (30-day, preserves confirmed).
- **Fragmentation reduced**: `MENTIONS_FLOOR=5` removes the 3-mention micro-topic tail
  (feed now min 14 / max 97 mentions); `MAX_TOPICS_PER_POST` 12→8.
- **GitHub authenticated** (`GITHUB_TOKEN` set, 5000/hr vs 60) — rotate it (chat-pasted).
- **Extensions layer ported** → `enterprise_intel.py` mounted on the engine:
  `/enterprise/methodology` (versioned weights), `/enterprise/scores/{key}/audit`
  (per-component contribution + reconciliation w/ official AI-override scores),
  `/enterprise/scores/{key}/scenarios` (response-surface what-ifs). No new tables.

_Ops scripts: `maint_dbfix.py` (index+prune), `maint_health.py` (read-only probe),
`maint_precompute.py` (manual prune + serve_payload precompute)._

---

## Review of the v1 source files (integration_patch, gradient_engine_backend, gradient_engine_extensions)

**Conclusion: nothing critical missing from the live 2.0 engine — but one valuable
dormant layer was identified.**

- `gradient_engine_backend.py` — the **v1 prototype** (separate SQLite `gradient_scores.db`,
  5 components G·I·M·D·C, no P/N). **Superseded** by `gravitational_anomaly_detector.py`
  (7 components G·I·M·D·C·P·N, Postgres). Its collectors are the originals the 2.0 engine
  re-implements. Confirms Reddit collection exists and just needs credentials.
- `integration_patch.py` — the wiring spec for the calibration layer. **All 5 edits verified
  present** in the live engine: imports ✓, `apply_signal_count_modifier` in scoring (line 2106) ✓,
  `apply_calibration` ✓, AI intelligence ✓, `is_meaningful_topic` noise filter ✓. Integration complete.
- `gradient_engine_extensions.py` — **DORMANT, not ported to 2.0.** Provides
  methodology versioning (reproducible scores), a per-component **audit log with signal
  attribution**, **scenario projections** ("what would move this score and by how much"),
  and an **outcome/track-record ledger**. None are wired into the 2.0 engine. These are
  exactly the trust/explainability features an enterprise/hedge-fund tier would pay for —
  recommend porting (rec #7). The 2.0 engine has partial overlap only (Google-Trends
  accuracy ledger + `anomaly_log.was_confirmed`).
- `gradient_scores.db`, `pipeline_tracker.db` — local v1 SQLite artifacts; not used by
  the live Postgres engine.
