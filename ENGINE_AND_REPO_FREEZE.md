# ⛔ Repo & Engine Boundary — 1.0 is FROZEN, everything lives in 2.0

**Read this before touching any engine / scoring / `.py` code or deploying anything.**

---

## The rule (one line)
There is **one v2.0 engine, one database, one repo**. The old **NowTrendIn 1.0** folder/repo/Heroku
app is **frozen legacy** (live Android app + pre-April-2026 data) and must **never** be edited or
deployed for 2.0 work.

## The two repos
| | 1.0 — FROZEN (do not touch) | 2.0 — the only place we work |
|---|---|---|
| Folder | `…/CODING PROJECTS/NowTrendin/` | `…/CODING PROJECTS/NowTrendin v2.0/` |
| GitHub | `Abelcesq/nowtrendin` | `Abelcesq/nowtrendin-v2.0` |
| Heroku engine app | `nowtrendin` (…e62dcb9) | `nowtrendin-v2-engine` (…edcb10d4) |
| Database | 1.0's Postgres (pre-Apr-2026 data — **untouchable**) | one Postgres on `nowtrendin-v2-engine` (migrated from v1 via `pg:copy`) |
| Status | **FROZEN** — serves the live Android app `com.benmore.nowTrendIn` | **ACTIVE** — all current work |

## Where things live in 2.0
- **Engine + all scoring + the agents (canonical source):** `transfer/` (41 modules, incl.
  `gravitational_anomaly_detector.py`, `monitoring_agents.py`, `calibration_engine.py`, …).
- **Mobile:** `frontend/` (React Native) → reads engine via `lib/gradientApi.ts`.
- **Web + Desktop:** `web-terminal/` → `src/lib/api.ts`; desktop = Tauri over the same build.
- **Accounts/alerts/watchlists API:** `backend/` (Django) → Heroku `nowtrendin-backend`.
- All three clients are **read-only** against the one engine — they never compute or store scores.
  (Consolidation completed 2026-06-15 — see `CONSOLIDATION_CHECKPOINT_2026-06-15.md`.)

## Deploy commands (always from the 2.0 repo)
```
# Engine  -> nowtrendin-v2-engine
git subtree push --prefix transfer heroku-v2engine main

# Backend -> nowtrendin-backend  (then run migrate)
git subtree push --prefix backend  heroku       main

# Web     -> gh-pages (prod) + heroku nowtrendin-terminal (staging)
cd web-terminal && npm run build   # then publish dist/* to gh-pages + web-deploy-terminal
```

## The gotcha (already installed in the 1.0 repo)
The 1.0 `NowTrendin/` repo has **`pre-commit` + `pre-push` git hooks** that **block** commits and
pushes with a message redirecting here, plus a `_FROZEN__USE_NowTrendin_v2.0_INSTEAD.txt` banner.
Override only for deliberate live-1.0 maintenance: `git commit --no-verify` / `git push --no-verify`.

## What went wrong once (don't repeat)
An engine change was edited in the **1.0 folder** and pushed/deployed to the **1.0 repo + `nowtrendin`
app** by mistake. It was additive/read-only so **1.0 data stayed safe**, but the correct home is
`2.0/transfer/`. If you need an engine change: edit `2.0/transfer/…`, commit to the 2.0 repo, then
`git subtree push --prefix transfer heroku-v2engine main`.
