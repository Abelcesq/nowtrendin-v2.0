---
name: terminal-deploy-parity
description: NowTrendIn terminal deploy-parity monitor — confirms the web terminal build is actually on the GitHub (nowtrendin-v2.0) repo and that every deploy target serves the SAME build. Compares the GitHub Pages live site, the gh-pages branch in the repo, and the Heroku mirror by bundle hash, so a stale/forgotten deploy is caught immediately. Use when the user says "is the data on github", "check the terminals", "are the deploys in sync", "did my change deploy", "deploy parity", or after deploying the terminal.
---

# /terminal-deploy-parity — are both terminals serving the build that's on GitHub?

**Why this exists:** the terminal has TWO deploy targets and they drifted once —
Heroku was updated but the user's actual site (GitHub Pages) was stale, so fixes
"didn't work" because they never reached the page. This agent confirms the build is
**on the GitHub repo** and that every surface serves the SAME build. Read-only.

## The targets (all must match)
- **GitHub Pages (CANONICAL — what the user sees):** https://abelcesq.github.io/nowtrendin-v2.0/
- **gh-pages branch (the repo content itself):** `Abelcesq/nowtrendin-v2.0` @ `gh-pages`
- **Heroku mirror:** https://nowtrendin-terminal-1183c0ac00c4.herokuapp.com/
- (optional) **local build:** `web-terminal/dist/index.html`

The build is identified by its hashed bundle name, `assets/index-XXXXXXXX.js`, in each
`index.html`. Same hash ⇒ same build.

## Steps
1. Pull the bundle hash from each target (PowerShell — verified working):
   ```powershell
   function Get-Bundle($u){ try { $c=(Invoke-WebRequest $u -TimeoutSec 30 -UseBasicParsing -Headers @{'Cache-Control'='no-cache'}).Content; if($c -match 'assets/(index-[A-Za-z0-9_\-]+\.js)'){$matches[1]}else{'NO-BUNDLE'} } catch { "ERR $($_.Exception.Response.StatusCode.value__)" } }
   Get-Bundle 'https://abelcesq.github.io/nowtrendin-v2.0/'                                            # GitHub Pages live
   Get-Bundle 'https://raw.githubusercontent.com/Abelcesq/nowtrendin-v2.0/gh-pages/index.html'        # gh-pages branch (repo)
   Get-Bundle 'https://nowtrendin-terminal-1183c0ac00c4.herokuapp.com/'                               # Heroku mirror
   ```
   bash/curl variant:
   ```bash
   for u in \
     "https://abelcesq.github.io/nowtrendin-v2.0/" \
     "https://raw.githubusercontent.com/Abelcesq/nowtrendin-v2.0/gh-pages/index.html" \
     "https://nowtrendin-terminal-1183c0ac00c4.herokuapp.com/"; do
     echo "$u -> $(curl -s --max-time 30 "$u" | grep -oE 'assets/index-[A-Za-z0-9_-]+\.js' | head -1)"
   done
   ```
2. Confirm `web-terminal/dist/index.html` (local last build) hash too, if checking after a build.

## Verdict + diagnosis
- **IN SYNC** — all three hashes equal → the build IS on the GitHub repo and every
  surface serves it. Say so plainly with the hash.
- **DRIFT** — name which target is stale and the cause:
  - **gh-pages live ≠ gh-pages branch** → GitHub Pages rebuild is pending (~1 min) or
    failed; re-check shortly / check the repo's Pages build status.
  - **Heroku ≠ gh-pages** → the Heroku mirror wasn't redeployed (or vice-versa).
  - **local dist ≠ gh-pages branch** → a build was made but **not pushed to gh-pages**
    (the classic miss — the user would see no change).
- If gh-pages is behind, the FIX is to redeploy gh-pages (see `/frontend-consistency`
  or the [[deploy-terminal-ghpages]] memory): build → worktree on `gh-pages` → replace
  `index.html`+`assets/` (keep `.nojekyll`) → `git push origin gh-pages`.

## Discipline
The **GitHub Pages / gh-pages branch is canonical** — it's what the user actually views.
A green Heroku is NOT proof the user sees the change. Always confirm the GitHub repo
target. Part of the monitoring fleet (see `/frontend-consistency`).
