# NowTrendIn 2.0 — Consolidation Checkpoint
**2026-06-15** · single-source-of-truth established; all platforms aligned to one database.

---

## 1. The principle — one database, one engine, three builds

There is **one v2.0 engine with one database**. Every platform is a **thin, read-only
client** that fetches from that engine — none of them compute or store scores. This
guarantees the *same* signals, scores, calibration, and integrity on every surface.

```
                 ┌──────────────────────────────────────────┐
                 │   v2.0 ENGINE  (Heroku: nowtrendin-v2-engine)
                 │   one Postgres database (the source)       │
                 │   all scoring + calibration + ledger       │
                 └───────────────────┬──────────────────────┘
                   read-only API: /scores /topics /accuracy/ledger /risk …
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                           ▼
  a) WEBSITE (HTML)        b) DESKTOP                    c) MOBILE (iOS + Android)
     web-terminal/            Tauri wraps the SAME          frontend/ (React Native)
     React + Vite             website build                 → reads engine via gradientApi
```

- **a) Website** and **b) Desktop** are the *same* code (`web-terminal/`); desktop = Tauri wrapping it.
- **c) Mobile** is the React Native app (`frontend/`); its `gradientApi.ts` reads the same engine.
- All three compute nothing — consistency is structural.

---

## 2. Deploy + source-of-truth topology

| Concern | Location |
|---|---|
| **Code source of truth** | **GitHub** — `Abelcesq/nowtrendin-v2.0` (app + terminal + mobile; engine in `transfer/`) |
| **v2.0 engine (live)** | Heroku **`nowtrendin-v2-engine`** → https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com |
| **v2.0 database** | The Postgres attached to `nowtrendin-v2-engine` (essential-1) — migrated from v1 via `pg:copy` |
| **v2.0 backend** | Heroku `nowtrendin-backend` (Django JWT accounts/alerts/grades); `GRADIENT_API` → v2 engine |
| **v1.0 (LEGACY, SEPARATE)** | `NowTrendin` folder → GitHub `Abelcesq/nowtrendin` + Heroku `nowtrendin`. **Frozen — never touched by v2.0 work.** |

**Heroku is the deploy/runtime target and live DB host; GitHub is the source of truth.**
Deploy flow: commit → GitHub → Heroku (engine via `git subtree push --prefix transfer heroku-v2engine main`).

### How each platform points at the one engine
- **Website / Desktop**: `web-terminal/src/lib/api.ts` → `nowtrendin-v2-engine` (auth via backend `lib/auth.ts`).
- **Mobile**: `frontend/lib/gradientApi.ts` → `nowtrendin-v2-engine` (was previously hitting the v1 URL directly — corrected today).
- **Backend proxy** (mobile token-metered actions): `GRADIENT_API` config var → `nowtrendin-v2-engine`.

---

## 3. Consolidation actions completed today

1. **Stood up the dedicated v2.0 engine** (`nowtrendin-v2-engine`) from `transfer/`, with its own Postgres.
2. **Migrated the database** v1 → v2 (`pg:copy`): preserved **23,090 scored topics, the Accuracy Ledger, and the calibration baselines** (the moat).
3. **Copied all 24 API-key config vars** to the v2 engine; scaled `web=1` + `worker=1` (self-sustaining collection).
4. **Repointed all three clients** to the v2 engine (terminal, mobile `gradientApi`, backend `GRADIENT_API`).
5. **Moved the full engine (41 modules) into `transfer/`** so the v2.0 repo is canonical; **GitHub made current** (engine had been Heroku-only).
6. **`/scores` list now returns `category`** + the profanity/junk quality filter, so the mobile feed matches `/topics` (web/desktop) — categories now populate on mobile.
7. **Mobile dashboard** split into two labelled chip rows — **Signal** (stage) and **Category** (content) — distinct in kind.

---

## 4. Health check — 2026-06-15 (v2.0 engine, post-fix verified)

**Every data source verified pulling** on the v2 engine:

| Endpoint / source | Result |
|---|---|
| `/health` | 200 ✓ |
| `/topics` (default + `?category=`) | ✓ (new york, knicks, epstein… + per-category) |
| `/scores` (mobile feed) | ✓ now includes `category` |
| `/categories` | ✓ Business 17 · Current Events 13 · Entertainment 10 · Economy 5 · Fashion 2 |
| `/accuracy/ledger` (+`/detail`) | ✓ 5 resolved / 826 pending |
| `/risk/scores` | ✓ 30 rows (collector HEALTHY after re-collect) |
| `/beneficiary/backtest` | ✓ **FIXED** — attention_curve 0→25, no crash |

**data-health** — Cost 2,460 today / 16,972 (30d); top youtube 919 · x 411 · whalewisdom 286.
**accuracy-sweep** — ledger migrated intact (5/826, small-sample); validation triggered.
**tier-gate-audit** — ✅ 17 compliant gates, 0 access-control violations.

### Fix applied this pass
- **Beneficiary backtest** queried a non-existent `stage` column on `pull_history` (real name `signal_stage`) — emptied the attention curve and errored. Fixed → attention curve now populates (0→25). Deployed to v2.
- Set `WEB_CONCURRENCY=1` on the v2 web dyno.

### Inherited baseline (NOT v2 regressions — identical on the live v1 engine)
- **R14 (memory) warnings**: the engine is memory-heavy for a 512 MB Basic dyno. v1 shows *more* R14s (incl. its worker). Soft warning — Heroku swaps; all endpoints still serve. A Standard dyno would clear it (cost decision).
- **4 collectors STALE** (google_trends/youtube/creators/broadcast, ~20h): **identical on v1** (both `trust:false`). A pre-existing prod cadence issue on the slow collectors, not introduced by the consolidation.

---

## 5. Known issues / follow-ups
- **Slow collectors stalled ~20h on BOTH engines** (google_trends/youtube/creators/broadcast) — pre-existing; investigate why their job stopped firing on production (affects v1 too).
- **R14 memory** — inherited; bump to a Standard dyno to clear, or trim in-process caches (cost vs. code decision).
- **Residual common-word noise** in the feed (`away`, `owner`…) — swap the curated junk list for a real common-word dictionary (spun-off task).
- **Spun-off engine fixes** (apply to `transfer/` then deploy to v2): `/score-all` async; `/scores/{key}` 500 on some keys; register discovery collectors in the health monitor.
- **Accuracy ledger** remains small-sample — re-run weekly as the 826 pending age in.

---

---

# Session 2 (2026-06-15, later) — Calibration, Data Quality & AI Cost Cap

## 6. News → mainstream calibration (the founder's model, now live)

**Problem found:** news headlines carry a low per-article weight (`engagement_raw ≈
log1p(120)=4.79`), but the magnitude scale floors at `7.0` — so a topic living
*purely* in the news registered magnitude ≈ 0. And cold-start (calibrating) mode
hard-zeroed breadth, so multi-outlet news corroboration was **dropped entirely** on
a topic's first cycles. A story breaking across many reputable outlets scored as
expert dark-matter — the opposite of "multiple outlets = mainstream."

**Fix (`dual_pathway.py`):**
- Count **distinct reputable news outlets** carrying a topic → `news_outlets`.
  `NEWS_MAINSTREAM_MIN = 3` distinct outlets ⇒ `mainstream_confirmed`.
- Cold-start now uses **absolute breadth** — broad simultaneous outlet/community
  corroboration *is* the mainstream signal on day one (moat preserved: an early
  EXPERT signal sits in expert communities, breadth ≈ 0 → `w` stays ≈ 0).
- `mainstream_detection` gains a **cross-outlet corroboration term** so a pure-news
  topic (magnitude ≈ 0) still surfaces.
- `mainstream_confirmed` = absolute "it has arrived", kept **distinct** from the
  baseline-relative "it's *moving*" (`w`). A perennial topic reads confirmed-but-
  not-moving; a genuine spike reads moving.
- **Persisted + surfaced** as columns: `detection_pathway`, `mainstream_ratio`,
  `mainstream_breadth`, `news_outlets`, `mainstream_confirmed`, `tier_migration`.

**Backtest:** `backtest_dual_pathway.py` — **13/13 pass** (breaking-news cold-start
18→37 mainstream/confirmed; single outlet stays niche; multi-outlet-at-baseline =
confirmed-but-not-moving). **Live verified:** every news topic now `path=mainstream`
with outlet counts (trump 110, iran 148, knicks 60).

## 7. Data quality — common words, consolidation, source-aware definitions

1. **Common-word filter** (`common_words.txt`, ~10.3k frequent English words from
   `wordfreq`, proper nouns subtracted — countries/demonyms/orgs/brands). A single
   common word is **never a trend regardless of volume**. `suffering`, `saying`,
   `exclusive`, `feeling` rejected; `japan`/`fifa`/`apple`/`chatgpt` kept. Applies at
   extraction **and serve-time** (cleans the existing pool with no re-collection).
   **Live verified:** junk gone from `/scores`.
2. **Pre-score consolidation** — `_canonicalize_topic` folds variants to one key
   (demonym→country `japanese→japan`, possessive `japan's→japan`, alias `gpt→chatgpt`)
   at write-time, plus a **self-heal pass** each score cycle that folds existing
   variant signals and drops orphaned non-canonical score rows. **Live verified:**
   `japanese`→`japan`, `dutch`→`netherlands` (duplicates gone).
3. **Source-aware AI explainer** — `_topic_source_context()` samples the real
   headlines + their platforms/communities; `explain_topic(topic, context=…)` now
   describes the *specific* trend driving attention (e.g. "japan" from World-Cup
   blogs = the team's run), not a generic dictionary definition.

## 8. AI cost cap — $20/month, both providers

All paid AI calls — topic **definitions** (Perplexity) and **grades** (Perplexity +
Anthropic) — are metered in a unified `ai_costs` ledger and checked against a hard
monthly budget (`AI_MONTHLY_BUDGET_USD`, default **$20**). Once month-to-date spend
≥ budget, the explainer endpoint, the per-cycle backfill, and `/grade` **skip new
paid calls** (cached/persisted results still serve). New endpoint **`GET /ai/costs`**:
month-to-date spent vs budget, remaining, %, by provider + by kind.
**Live verified:** `/ai/costs` = `$0.00 / $20.00`.

## 9. Print-to-PDF (mobile/web app)

`printSignalsReport()` renders the **entire** scored list into a fresh paginating
HTML report (the browser previously printed only the visible RN ScrollView viewport).
Web-only "Print / PDF" button in the Trends header. *Committed; needs a
`nowtrendin-web` rebuild to appear on that deployment.*

## 10. Skills health check — 2026-06-15 (Session 2, v2 engine)

| Skill | Result |
|---|---|
| **data-health** | 18 collectors: 13 HEALTHY/fresh; **4 STALE** (google_trends/youtube/creators/broadcast ~23h) + reddit DEGRADED (0 signals) — pre-existing slow-collector issue, not a regression. Costs tracked per source. |
| **accuracy-sweep** | Validation triggered (Apify, async). Ledger **young**: 5 evaluated (all lagged), 850 pending, `smallSample=true` — accuracy not yet claimable (honest). |
| **beneficiary-backtest** | `ai_infrastructure` live (NVDA EARLY/29.6, SNDK LATE/42.8, VST EARLY/24.2, CEG EARLY/24.7); `energy_transition` empty → INCONCLUSIVE (theme attention curve not populated). `would_have_flagged_early_at` null (25-pt history, young). |
| **tier-gate-audit** | ✅ **PASS** — 17 gates, 0 access-control violations; data-aging all via `isDataAccessible`. |
| **risk-verify** | Beneficiary layer live (NVDA 28.9/EARLY/AI Infrastructure). `/risk/scores` keyed by risk-topic not ticker in v2 — skill's ticker-match needs a field-name update. |
| **AI cost cap** | ✅ `/ai/costs` = `$0.00 / $20.00`. |

## 11. Known issues / follow-ups (updated)
- **Calibration warm-up:** the news/baseline columns are new, so historical breadth
  baselines ≈ 0 → most topics currently read `path=mainstream`. Baselines accumulate
  over the next few 6-h cycles, after which perennial entities settle to baseline and
  genuine movers stand out. Expected, self-correcting.
- **Deeper entity resolution:** `trump` vs `Donald Trump` (surname vs full name) and
  stray short tokens (`asi`, `dept`) aren't yet folded — needs a name/alias gazetteer
  beyond the demonym/possessive rules.
- **Slow collectors** (google_trends/youtube/creators/broadcast) still stalled ~23h —
  pre-existing on both engines; investigate why their jobs stop firing in prod.
- **Accuracy ledger** small-sample (850 pending) — re-run weekly as it ages in.
- **`nowtrendin-web`** needs a rebuild to pick up the Print button (no git remote on
  this machine; last deployed 6/10 from the laptop).
- ✅ *Resolved this session:* residual common-word noise (now a real dictionary);
  AI-spend was untracked (now capped); generic AI definitions (now source-aware).

---

*All scoring/calibration lives in the engine (see `transfer/`): dual-pathway detection,
baseline-relative mainstreaming (fame vs. diffusion), **news-outlet corroboration +
mainstream-confirmed**, community-level tiers, tier-migration, **common-word filter**,
**topic consolidation**, content-category classifier, Phase A discovery, Phase B entity
resolution, **source-aware AI explainer**, **$20/mo AI cost cap**. Clients never re-score.*
