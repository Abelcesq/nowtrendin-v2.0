---
name: deploy-terminal-ghpages
description: "The web terminal the user actually views is GitHub Pages (gh-pages branch), NOT the Heroku mirror — deploy there or changes are invisible."
metadata: 
  node_type: memory
  type: project
  originSessionId: 46ab8dd5-70c6-49dc-8816-b88ccdd2bb93
---

The user's canonical web terminal is **https://abelcesq.github.io/nowtrendin-v2.0/**,
served from the **`gh-pages` branch** of origin (`github.com/Abelcesq/nowtrendin-v2.0`).
A Heroku mirror exists (`nowtrendin-terminal`, web-deploy-terminal/) but the user does
NOT use it.

**Why this matters:** deploying only to Heroku means the user sees NO change — this
caused a long stretch where stage/filter/Grade/N-column fixes "didn't work" because
they never reached gh-pages.

**How to deploy the terminal (`web-terminal/`):**
1. `npm run build` (vite, base `./` — relative paths work at the /nowtrendin-v2.0/ subpath).
2. gh-pages (REQUIRED): `git worktree add ../ghp gh-pages` → delete `index.html`+`assets/`,
   copy `web-terminal/dist/*` in, keep `.nojekyll` → commit → `git push origin gh-pages`.
   Pages rebuilds in ~1 min.
3. Heroku mirror (optional): copy dist into `web-deploy-terminal/dist`, push the `heroku` remote.

Engine = `heroku-v2engine` remote; backend = `heroku` remote (nowtrendin-backend).
See [[project-nowtrendin-2]] and the `/frontend-consistency` skill.
