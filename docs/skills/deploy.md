---
name: deploy
description: NowTrendIn full-stack deploy — syntax-check Python, push engine to nowtrendin-v2-engine (Heroku), push backend subtree to nowtrendin-backend (Heroku), push frontend/web-terminal to origin (GitHub → gh-pages). Verifies each stage. Use when the user says "deploy", "ship it", "push to prod", "deploy NowTrendIn", or asks to redeploy any of the three apps.
---

# /deploy — NowTrendIn full-stack deploy

## ⚠ REPO + APP IDENTITY — READ FIRST

All work is in the **v2.0 repo only** (`Abelcesq/nowtrendin-v2.0`, local path
`NowTrendin v2.0/`). The `NowTrendin/` (1.0) folder and the `nowtrendin` Heroku
app are **FROZEN** and must NEVER receive a deploy from this workflow.

Confirm you are in the right directory before any push:
```powershell
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0"
git remote -v   # must show: heroku → nowtrendin-backend, heroku-v2engine → nowtrendin-v2-engine
```

---

## The three deployable apps (all from `NowTrendin v2.0/`)

| App | Source dir | Heroku app | Remote | Command |
|---|---|---|---|---|
| **Engine** | `transfer/` | `nowtrendin-v2-engine` | `heroku-v2engine` | `git subtree push --prefix transfer heroku-v2engine main` |
| **Backend** | `backend/` | `nowtrendin-backend` | `heroku` | `git subtree push --prefix backend heroku main` |
| **Web terminal** | `web-terminal/` | GitHub Pages (canonical) | `origin gh-pages` | `npm run build` → copy dist → push gh-pages |

> **Note:** "Frontend" (`frontend/`) is the mobile React Native app. It is NOT
> deployed from this workflow — it builds via Expo. Push source to `origin main`.

---

## Steps

### 1. Confirm what's changed
```powershell
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0"
git status
git log --oneline -10
```
Ask the user which app(s) to deploy if not clear. Default to all that have changed.

### 2. Syntax-check Python (engine + backend — REQUIRED before any push)
```powershell
# Engine
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\transfer"
python -c "import ast,sys,glob; files=glob.glob('*.py'); [ast.parse(open(f,encoding='utf-8').read()) for f in files]; print('OK:', len(files), 'files')"

# Backend
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\backend"
python -c "import ast,sys,glob; files=glob.glob('**/*.py',recursive=True); files=[f for f in files if 'venv' not in f]; [ast.parse(open(f,encoding='utf-8').read()) for f in files]; print('OK:', len(files), 'files')"
```
If any file fails to parse, STOP and report — do not deploy broken Python.

### 3. Commit changes
Commit to `origin main` first with a meaningful message + Co-Authored-By trailer.
NEVER skip this — GitHub is the source of truth; Heroku is the runtime target.

### 4. Deploy

**Engine → nowtrendin-v2-engine:**
```powershell
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0"
git subtree push --prefix transfer heroku-v2engine main
```

**Backend → nowtrendin-backend:**
```powershell
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0"
git subtree push --prefix backend heroku main
# After backend deploy, run migrations:
heroku run python manage.py migrate -a nowtrendin-backend
```

**Web terminal → GitHub Pages (canonical user-facing site):**
```powershell
cd "C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\web-terminal"
npm run build
# Copy dist to .ghpages-deploy worktree (exclude .git and .nojekyll)
$src = "dist"; $dst = "..\. ghpages-deploy"
Get-ChildItem $dst -Exclude ".git",".nojekyll" | Remove-Item -Recurse -Force
Copy-Item "$src\*" $dst -Recurse -Force
cd "..\. ghpages-deploy"
git add -A
git commit -m "deploy: web terminal build <date>"
git push origin gh-pages
```

### 5. Verify after each deploy

```powershell
# Engine (v2 — the active engine)
curl -s --max-time 20 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/health

# Backend (Django liveness probe — HTTP 400 + JSON = up)
curl -s --max-time 20 https://nowtrendin-backend-acb79c396814.herokuapp.com/api/auth/login/ -X POST -H "Content-Type: application/json" -d "{}" -w "\nHTTP:%{http_code}" | tail -2

# Web terminal (GitHub Pages)
curl -s -o /dev/null -w "GH_PAGES_HTTP_%{http_code}" --max-time 20 https://abelcesq.github.io/nowtrendin-v2.0/
```

### 6. Report
State which app(s) deployed, the Heroku release version (`heroku releases --num=1 -a <app>`),
and any warnings. Confirm GitHub is current before closing.

---

## Safety rules

- **NEVER** deploy to `nowtrendin` (the 1.0 frozen Heroku app) — it serves the live Android
  app on `com.benmore.nowTrendIn` and its database is the pre-April-2026 1.0 data. Any deploy
  there is accidental and must be reversed.
- **NEVER** use `--no-verify` or `--force` unless the user explicitly requests it.
- **NEVER** push the backend via `git push heroku main` from the root — the subtree command
  (`git subtree push --prefix backend heroku main`) is required or Heroku gets the wrong files.
- If syntax check fails, fix it or report — do not push broken code.
- If a Heroku push fails with a build error, read logs:
  `heroku logs --tail -a nowtrendin-v2-engine -n 50`
  Report the error; do NOT retry blindly.
