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

*All scoring/calibration lives in the engine (see `transfer/`): dual-pathway detection,
baseline-relative mainstreaming (fame vs. diffusion), community-level tiers, tier-migration,
content-category classifier, Phase A discovery, Phase B entity resolution. Clients never re-score.*
