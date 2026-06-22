---
name: deploy-topology
description: "The repo + deploy map — ONE v2 engine for all platforms; the NowTrendin (1.0) folder/repo/app is FROZEN legacy, never touch it"
metadata: 
  node_type: memory
  type: project
  originSessionId: 46ab8dd5-70c6-49dc-8816-b88ccdd2bb93
---

Authority: `NowTrendin v2.0/CONSOLIDATION_CHECKPOINT_2026-06-15.md`. The consolidation is DONE.

**ONE v2.0 engine, ONE database, three thin clients:**
- Engine (live): Heroku **`nowtrendin-v2-engine`** (…edcb10d4) + its own Postgres (migrated from v1 via pg:copy — 23,090 topics, ledger, baselines). Runs all scoring + the agents (web=1, worker=1).
- Engine CODE is canonical in **`NowTrendin v2.0/transfer/`** (41 modules, incl. `gravitational_anomaly_detector.py`, `monitoring_agents.py`). Deploy: `git subtree push --prefix transfer heroku-v2engine main` from the v2.0 repo.
- All 3 clients READ-ONLY from that one engine: web `web-terminal/src/lib/api.ts`, mobile `frontend/lib/gradientApi.ts`, backend `GRADIENT_API` config var (Heroku `nowtrendin-backend`). Clients never compute/store scores.
- Web prod = gh-pages (abelcesq.github.io/nowtrendin-v2.0); staging = Heroku `nowtrendin-terminal`. Backend = subtree push `--prefix backend heroku main` then migrate.

**⛔ FROZEN — never touch for 2.0 work:** the **`NowTrendin/` folder** = 1.0 LEGACY (GitHub `Abelcesq/nowtrendin`, Heroku app `nowtrendin` …e62dcb9). It runs the LIVE 1.0 Android app + pre-April-2026 data. A pre-commit/pre-push git hook in that repo now BLOCKS commits/pushes (override: `--no-verify`). If an engine change is needed, edit `v2.0/transfer/` and deploy to `nowtrendin-v2-engine` — NOT the 1.0 folder.

(Mistake to avoid, made once: editing/deploying the engine from the 1.0 folder. The change was additive/read-only so 1.0 data stayed safe, but it must live in `transfer/`.) See [[deploy-terminal-ghpages]], [[project-gradient-calibration]].
