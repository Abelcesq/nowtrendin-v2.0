---
name: nowtrendin2.0
description: NowTrendIn 2.0 session startup — loads all project context, runs health + skills + agents check, and arms the auto-save protocol. Invoke at the start of every session, or when context feels stale. Use when the user says "start session", "load context", "catch me up", "what's the state of NowTrendIn", or after a new Claude Code window opens.
---

# /nowtrendin2.0 — Session Startup + Continuous Context

This skill loads full project context, runs health and readiness checks, and
establishes the auto-save protocol that protects all work for the session.
Run it once at the start of every session. Takes ~60 seconds.

---

## ⚠ FOUNDATIONAL PRINCIPLES — READ BEFORE ANYTHING ELSE

These principles are not preferences. They are the foundation the entire product
stands on. Violating any one of them is fatal to the project and cannot be allowed
under any circumstance, by any agent, in any session.

### 1. Accuracy above all

> **"A number we cannot defend with real data is worse than no number at all."**
> — AGENT_CHARTER.md, Part 0 §0.1

Every Gradient Score, Market Signal, and derivative output must reflect what
real, external data actually shows — not what looks plausible, not what a
previous version produced, not what an AI model infers in the absence of data.
When data is insufficient to produce a defensible result, the correct output is
"insufficient data," not a best-guess number.

### 2. Reproducibility — results must be derivable from their inputs

Every score, signal, and analysis must be reproducible from the same input data.
If two runs on the same data produce materially different results and there is no
intentional randomness in the algorithm, that is a bug, not a feature. New data
sources and scoring changes require a backtest against known outcomes before
shipping — not to validate novelty, but to confirm the signal is real and
directionally consistent with ground truth. See: `CALIBRATION_FIFA_ANALYSIS.md`,
`BACKTEST_LOG.md`, `/accuracy-sweep`.

### 3. Integrity of information — no fabrication, no circularity, no inflation

- **No fabricated data.** Never synthesize, interpolate, or hallucinate a data
  point as if it were measured. If a source is unavailable, say so.
- **No circular metrics.** The on-platform demand signal N (nowtrendin_score)
  must NEVER be folded into the Gradient Score or used to validate it. A score
  cannot be confirmed by a signal that was itself produced by user engagement
  with that score. This circularity would corrupt the one thing the platform
  claims to measure — attention that arrives BEFORE it's mainstream.
- **No score inflation.** Scores are calibrated to reflect real-world signal
  strength relative to a topic's own baseline — not to maximize engagement or
  make the platform look more impressive.
- **Reputable, licensed sources only.** Every data point that enters the corpus
  must come from a vetted publisher or licensed data provider. Unvetted content
  is quarantined, never scored.

### 4. Measurement, not advice

Now TrendIn measures where attention is moving. It does not recommend actions.
No output — from any agent, any UI surface, any report — may editorialize a
score into investment, trading, or financial advice. Neutral tier labels
(BREAKOUT, ELEVATED, EMERGING) are descriptive, not prescriptive.

### 5. Flag, never force — humans confirm before anything changes what users see

Diagnostic and monitoring agents are READ-ONLY. They surface findings for
human review. No agent auto-applies a scoring change, updates a calibration
weight, or publishes an accuracy result without explicit human confirmation.
A wrong auto-action is a credibility event. A flagged candidate is not.

### What "fatal" means

A project whose scores cannot be defended with real, reproducible, non-circular
data cannot exist as an Attention Intelligence Platform. It becomes noise at
best and fraud at worst. These principles are not a checklist — they ARE the
product. Every session, every task, every line of code is either upholding them
or eroding them. There is no neutral.

If any requested task, data source, scoring change, or agent behavior would
violate these principles, STOP and say so explicitly before proceeding.

---

## INFRASTRUCTURE STATE — AUDITED 2026-06-20 (do not re-audit unless user asks)

> This section records what was confirmed in the 2026-06-20 infrastructure audit.
> Do NOT repeat this audit at session start — check PENDING USER ACTIONS below
> to see if the user has filled the known gaps since last time.

### What was confirmed correct ✅

- Both clients point to v2 engine: `web-terminal/src/lib/api.ts` line 8 and
  `frontend/lib/gradientApi.ts` lines 5-6 both hardcode the v2 engine URL
  `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com`
- Backend `GRADIENT_API` env var on Heroku = v2 engine URL ✅
- Git remotes confirmed: `heroku` → `nowtrendin-backend`, `heroku-v2engine` → `nowtrendin-v2-engine`
- Engine deploy command corrected in the deploy skill (was wrong — pointed to 1.0 app)
- `AI_GRADE_CLAUDE_MODEL` updated to `claude-sonnet-4-6` on nowtrendin-v2-engine ✅
- `docs/ENV_REFERENCE.md` created — complete map of all env vars with SET/MISSING status
- `transfer/.env.example` and `backend/.env.example` created for local dev reference
- `docs/skills/deploy.md` — cloud backup of the corrected deploy skill
- Deploy skill rewritten: engine subtree command now correctly uses `heroku-v2engine` remote

### What was found broken / wrong (now fixed) 🔧

- **Deploy skill (old):** Engine subtree command used `heroku main` (the backend remote),
  which would have deployed engine code to the backend app. Now fixed to `heroku-v2engine main`.
- **nowtrendin2.0 skill (old):** Health check URL pointed to the 1.0 frozen engine
  (`nowtrendin-e62dcb9ecb69.herokuapp.com`) — now corrected to the v2 engine URL.
- **Deploy skill (old):** Was entirely pointing to `NowTrendin/` folder → `nowtrendin`
  Heroku app (1.0 frozen). This caused an accidental deploy to the frozen 1.0 app on 2026-06-19.

### PENDING USER ACTIONS — check these at each session start

At session start, quickly check whether the user has addressed any of these.
Do NOT repeat the full Heroku config audit — just check the specific gaps:

```powershell
# Check if user has set the high-priority gaps (Guardian + Reddit on hold; Apify resolved)
heroku config -a nowtrendin-backend 2>$null | Select-String "SECRET_KEY|GOOGLE_ANDROID_CLIENT_ID"
heroku config -a nowtrendin-v2-engine 2>$null | Select-String "GUARDIAN_API_KEY|REDDIT_CLIENT_ID"
```

| Gap | Impact | Action |
|---|---|---|
| `SECRET_KEY` (backend) | RESOLVED ✅ | Set 2026-06-20, Heroku v39. Django no longer using insecure default. |
| `GUARDIAN_API_KEY` missing on engine | HIGH — Stage 4 mainstream media signal absent; GDELT fallback rate-limited on Heroku IPs | **ON HOLD** (user deferred 2026-06-20). Register free at open-platform.theguardian.com/access when ready. |
| `REDDIT_CLIENT_ID/SECRET/USER_AGENT` missing on engine | MEDIUM — Reddit signal entirely absent | **ON HOLD** (user deferred 2026-06-20). Register at reddit.com/prefs/apps when ready. |
| `GOOGLE_ANDROID_CLIENT_ID` missing on backend | MEDIUM — Android Google OAuth may fail silently | Retrieve from Google Cloud Console → OAuth credentials |
| `APIFY_REALTIME_ACTOR` + `APIFY_TRENDS_ACTOR` | RESOLVED ✅ | Both actors have hardcoded defaults and ARE running. Confirmed 2026-06-20: 125 results, $0.574/run. No env vars needed. Monitor spend (~$103/mo). |
| `DEVTO_API_KEY` missing on engine | LOW — Dev.to blog signal silently skips | Register at dev.to/settings/extensions (free) when ready |

Full env var reference: `docs/ENV_REFERENCE.md` in the v2.0 repo.

---

## STEP 1 — MEMORY LOAD

Read these files first (in order). They establish what was built, what's open,
and what rules must never be broken.

```
C:\Users\acinv\.claude\projects\C--Users-acinv-OneDrive-Desktop-CODING-PROJECTS-NowTrendin-v2-0\memory\MEMORY.md
```
Then read every file that MEMORY.md links to (each `[Title](file.md)` entry).

Key memory files to prioritize:
- `deploy-topology.md` — which git remotes go where (one wrong push = wrong app)
- `feedback-integrity-standard.md` — hard rules that override everything
- `feedback-verify-before-ship.md` — never document over broken state
- `serve-payload-cache-gotcha.md` — stale payloads survive scoring changes
- `project-gradient-calibration.md` — dual-pathway model + backtest requirement

---

## STEP 2 — PROJECT MD FILES

Read these in the v2.0 repo. Skim for anything marked "(NEW)", "(CHANGED)",
or dated more recently than the last session.

**Root-level (always read):**
- `CLAUDE.md` — master build rules, tech stack, tier logic, phase status
- `ENGINE_AND_REPO_FREEZE.md` — NowTrendin/ (1.0 engine) is FROZEN; all engine work is in transfer/
- `DATA_BUILDING_BLOCKS.md` — pipeline invariants B1–B8, source registry, monitoring agents
- `AGENT_CHARTER.md` — shared mandate for every autonomous agent (integrity rules)
- `SESSION_LOG.md` — running catch-up of completed + open work
- `COST_MODEL.md` — per-call cost estimates; check before adding new data sources

**New docs created 2026-06-20 (read if env/deploy work comes up):**
- `docs/ENV_REFERENCE.md` — complete env var map: SET/MISSING status + action items
- `transfer/.env.example` — engine local dev template (key names only)
- `backend/.env.example` — backend local dev template (key names only)
- `docs/skills/deploy.md` — cloud backup of the corrected deploy skill

**Deep context (skim if topic comes up):**
- `docs/METHODOLOGY.md` — Gradient Score composition, the dual-pathway model
- `docs/PLATFORMS.md` — three-platform topology (mobile, web terminal, desktop)
- `docs/NOW_TRENDIN_2_FLOW.md` — end-to-end data flow
- `CONSOLIDATION_CHECKPOINT_2026-06-15.md` — engine consolidation record
- `CHECKPOINT_2026-06-10_eod.md` — last major feature checkpoint
- `CALIBRATION_FIFA_ANALYSIS.md` — dual-pathway calibration case study

**Engine (frozen 1.0 — read-only reference):**
Located at `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin\`
- `CLAUDE.md` — frozen; do NOT modify this repo
- `ACCURACY_LOG.md` — historical hit-rate record
- `BACKTEST_LOG.md` — backtest results

---

## STEP 3 — GIT STATE CHECK

Run these to understand current branch state:

```powershell
# v2.0 repo (main working repo)
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0"
git status
git log --oneline -15
git stash list

# Check gh-pages is current with main's last build
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\.ghpages-deploy"
git log --oneline -3
```

Flag if:
- Any modified-but-uncommitted files that look like finished work (push them)
- `git stash list` is non-empty (stash may contain unfinished work to surface)
- `.ghpages-deploy` is more than 1 commit behind what was last built

---

## STEP 4 — HEALTH CHECKS

Run all three service checks in parallel:

```powershell
# Engine (v2 — the ONLY active scoring engine)
# ⚠ CORRECT URL: nowtrendin-v2-engine-edcb10d44f91.herokuapp.com
# ⚠ WRONG (frozen 1.0): nowtrendin-e62dcb9ecb69.herokuapp.com — never use this
curl -s --max-time 20 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/health

# Backend (Django API) — /api/health/ doesn't exist; use auth endpoint as liveness probe
# HTTP 400 with JSON = Django is up and routing correctly
curl -s --max-time 20 https://nowtrendin-backend-acb79c396814.herokuapp.com/api/auth/login/ -X POST -H "Content-Type: application/json" -d "{}" -w "\nHTTP:%{http_code}" | tail -2

# Web terminal (GitHub Pages — canonical user-facing site)
curl -s -o /dev/null -w "%{http_code}" --max-time 20 https://abelcesq.github.io/nowtrendin-v2.0/
```

Expected:
- Engine: JSON with `"status"` field (any non-error value = up)
- Backend: HTTP 400 with JSON = Django is up and healthy
- GH Pages: HTTP 200

If any are down, report immediately and pause other work — a down service
may affect what code changes are safe to ship.

Also check the web terminal build is not broken:
```powershell
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\web-terminal"
npm run build 2>&1 | Select-Object -Last 5
```
A clean build ends with `built in X.XXs`. If it errors, report before touching any TS files.

---

## STEP 5 — SKILLS INVENTORY

List every skill in `C:\Users\acinv\.claude\skills\` and confirm its SKILL.md exists.
For skills that are agent-type (fleet monitoring, diagnostics), note whether they
match the agents listed in `DATA_BUILDING_BLOCKS.md` §Monitoring Agents.

Current skill roster (update this list when new skills are added):
| Skill | Purpose |
|---|---|
| `/deploy` | Full-stack deploy — engine (heroku-v2engine), backend (heroku), web terminal (gh-pages) |
| `/frontend-consistency` | UI parity audit across mobile / web terminal / desktop |
| `/data-health` | Pipeline health — collector gaps, stale data, budget burn |
| `/data-watchdog` | Source watchdog — publisher allowlist, provenance tiers |
| `/data-subscriptions` | Subscription monitor — WhaleWisdom, X, external APIs |
| `/accuracy-sweep` | Accuracy ledger + backtest runner |
| `/beneficiary-backtest` | Trend Beneficiary (SanDisk-pattern) backtest |
| `/catchall-audit` | Catch-all corroboration floor monitor |
| `/expo-recover` | Expo Go / Metro bundler recovery steps |
| `/grade-agent` | Grade tool — Perplexity + Claude AI scoring |
| `/integrity-reviewer` | Integrity standard audit (non-circular, reputable sources) |
| `/market-coverage` | Market signal coverage audit |
| `/market-signal-diagnostic` | Market signal diagnostic runner |
| `/risk-verify` | Risk/Other tab verification |
| `/terminal-deploy-parity` | Web terminal deploy + GH Pages parity |
| `/tier-gate-audit` | Tier-gate coverage check |
| `/topic-quality-audit` | Topic quality floor + catch-all audit |
| `/trend-signal-diagnostic` | Trend signal diagnostic runner |
| `/nowtrendin2.0` | THIS SKILL — session startup + auto-save |

---

## STEP 6 — AGENTS INVENTORY

Available agent types for the Agent tool (from Claude Code SDK):
- `claude` — general catch-all
- `Explore` — fast read-only codebase search (use for "find X in code")
- `Plan` — implementation planner (use before major architectural changes)
- `code-reviewer` — independent code review
- `claude-code-guide` — Claude Code / API questions

Fleet monitoring agents (in-engine, invoked via `/monitor` endpoint):
1. Source Watchdog — publisher allowlist + provenance tiers
2. Pipeline Integrity — collector gaps, stale windows, B1–B8 invariants
3. Topic Quality Auditor — fragment gate, maturity, corroboration floor
4. Catch-All Auditor (daily EOD) — catch-all floor trend (IMPROVING/STABLE/WORSENING)
5. Cost Sentinel — per-source cost tracking vs budgets
6. Data Subscriptions — external API status + quota remaining
7. Calibration Auditor — dual-pathway gate, baseline-relative sanity

Full specs in `DATA_BUILDING_BLOCKS.md` §Monitoring Agents.

---

## STEP 7 — SESSION REPORT

After steps 1–6, output a compact status card:

```
=== NowTrendIn 2.0 — Session Status ===

SERVICES       Engine v2: [UP/DOWN]   Backend: [UP/DOWN]   Web Terminal: [UP/DOWN]
BUILD          web-terminal: [CLEAN/BROKEN]
LAST COMMIT    [hash] [message]
OPEN WORK      [list anything uncommitted or flagged in SESSION_LOG.md as open]
PENDING USER   [which of the PENDING USER ACTIONS above are still unresolved]
ACTIVE RULES   [any memory warnings or hard rules relevant to current open work]
SKILLS         [count] loaded, [any missing or stale]
```

Then ask: "What would you like to work on?"

---

## AUTO-SAVE PROTOCOL (active for the entire session)

**GitHub IS the cloud backup.** Every push to `origin main` or `gh-pages` saves
all code permanently off the local drive. Follow this protocol every session:

### After every completed task:
1. Stage the changed files by name (never `git add -A` — avoid committing .env or binaries)
2. Commit with a meaningful message + Co-Authored-By trailer
3. Push to `origin main` immediately — do NOT batch pushes to "later"
4. If the task touched web-terminal source: also build + deploy to gh-pages

### After significant findings or discoveries:
- Update `SESSION_LOG.md` with a dated entry summarizing what was done and what's open
- Update the relevant memory file in `~/.claude/projects/.../memory/` if a new pattern was confirmed
- Stage + commit SESSION_LOG.md to `origin main`

### Before closing / at natural pause points:
```powershell
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0"
git status          # confirm nothing uncommitted
git push origin main
```

### Protecting memory files (local only by default):
Memory files at `C:\Users\acinv\.claude\projects\...\memory\` are local. If asked
to back them up to the cloud, export the MEMORY.md index + key memory files into
`SESSION_LOG.md` or a dedicated `docs/SESSION_MEMORY_EXPORT.md` in the repo, then
push to origin. Do this at the end of any session where substantial new memory was saved.

---

## REPOSITORY IDENTITY — ONE REPO, NO EXCEPTIONS

> **All commits and pushes go to `github.com/Abelcesq/nowtrendin-v2.0` only.**
> The old `NowTrendin` (1.0) repository is permanently frozen and must never
> receive a commit. A git hook in that repo enforces the freeze — if you ever
> see a push succeed to the 1.0 repo, treat it as a hard error and reverse it.

### The two local directories — do not confuse them

| Local path | GitHub repo | Status |
|---|---|---|
| `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\` | `Abelcesq/nowtrendin-v2.0` | **ACTIVE — all work goes here** |
| `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin\` | `Abelcesq/NowTrendin` | **FROZEN — read-only reference only** |

When in doubt, check which repo you're in before any `git commit` or `git push`:
```powershell
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0"
git remote -v   # must show Abelcesq/nowtrendin-v2.0
```
If `git remote -v` shows the 1.0 repo, STOP — you are in the wrong directory.

### `origin` always means `nowtrendin-v2.0`

Throughout this skill and all other skills, `origin main` and `origin gh-pages`
always refer to the `nowtrendin-v2.0` repository. There is no legitimate reason
to push to the 1.0 repository. Engine code that was formerly in `NowTrendin/` is
now canonical in `NowTrendin v2.0/transfer/` — see `ENGINE_AND_REPO_FREEZE.md`.

---

## DEPLOY TOPOLOGY QUICK-REFERENCE

> ⚠ Two Heroku remotes — do NOT mix them up:
> - `heroku` → `nowtrendin-backend` (Django API)
> - `heroku-v2engine` → `nowtrendin-v2-engine` (FastAPI scoring engine)
> Verify with `git remote -v` before any subtree push.

| App | Dir | Heroku app | Remote | Command (from v2.0 root) |
|---|---|---|---|---|
| **Engine (v2, ACTIVE)** | `transfer/` | `nowtrendin-v2-engine` | `heroku-v2engine` | `git subtree push --prefix transfer heroku-v2engine main` |
| **Backend (Django)** | `backend/` | `nowtrendin-backend` | `heroku` | `git subtree push --prefix backend heroku main` |
| Web terminal (source) | `web-terminal/` | — | `origin main` | `git push origin main` |
| Web terminal (live) | `.ghpages-deploy/` | — | `origin gh-pages` | build → copy → push gh-pages |
| Mobile (source) | `frontend/` | — | `origin main` | `git push origin main` |
| NowTrendin 1.0 | `NowTrendin/` | `nowtrendin` (FROZEN) | — | ❌ NEVER PUSH HERE |

**Live URLs:**
- Engine v2: `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com`
- Backend: `https://nowtrendin-backend-acb79c396814.herokuapp.com`
- Web terminal: `https://abelcesq.github.io/nowtrendin-v2.0/`
- Frozen 1.0 engine (DO NOT DEPLOY TO): `https://nowtrendin-e62dcb9ecb69.herokuapp.com`

After engine deploy: verify with `/health`.
After backend deploy: run `heroku run python manage.py migrate -a nowtrendin-backend`.
Full deploy spec: `C:\Users\acinv\.claude\skills\deploy\SKILL.md` and `docs/skills/deploy.md`.

---

## HARD RULES (never skip, never override)

The FOUNDATIONAL PRINCIPLES section above is the governing statement. These
operational rules are the concrete expressions of those principles. They come from
`AGENT_CHARTER.md` Part 0 and the memory files and apply every session:

1. **Data-backed only.** Never assert, infer, or estimate without a source.
   (Accuracy principle — "insufficient data" beats a guessed number.)
2. **No circular metrics.** N (nowtrendin_score / on-platform demand) must NEVER
   be folded into the Gradient Score. Any validator must use N-independent inputs.
   (Integrity principle — circularity corrupts the core measurement claim.)
3. **Reputable sources only.** Only vetted publishers enter the corpus.
   (Integrity principle — unvetted content is quarantined, never scored.)
4. **Flag, never force.** Monitoring agents are read-only. Scoring changes require
   human confirmation + backtest before deploy.
   (Reproducibility + accuracy principle — backtest first, ship second.)
5. **Verify before ship.** Fix failures first, then document. Never document over broken state.
   (Integrity principle — documentation of broken behavior is a lie.)
6. **90-day data retention (hard).** Never delete `velocity_scores` rows younger than
   90 days. No quality-based deletes within the window. Count-based prune is forbidden.
   (Reproducibility principle — historical scores are required for backtest + calibration.)
   365-day extension is PENDING USER CONFIRMATION — do NOT implement until confirmed.
7. **Engine 1.0 is FROZEN. Push only to `nowtrendin-v2.0`.** `NowTrendin/` repo is
   read-only. All engine work goes in `NowTrendin v2.0/transfer/`. A git hook enforces
   the freeze. Every `git push` must target `Abelcesq/nowtrendin-v2.0`.
8. **serve_payload must be regenerated** after any scoring or calibration change or
   the API serves stale data. See memory: `serve-payload-cache-gotcha.md`.
   (Accuracy principle — a stale payload is a wrong number presented as current.)
9. **API key values never go in Git.** Only key names go in `.env.example` and
   `docs/ENV_REFERENCE.md`. Values live only in Heroku Config Vars and local `.env`
   files (gitignored). See `.gitignore` before staging anything env-related.

---

## SESSION LOG UPDATE TEMPLATE

Append this at the end of `SESSION_LOG.md` after each substantive session:

```markdown
## Session [DATE]

### Completed
- [bullet per task]

### Open / Next
- [bullet per unfinished item]

### Hard decisions made
- [any architectural or integrity decisions, with rationale]
```

Always push SESSION_LOG.md to origin before closing.
