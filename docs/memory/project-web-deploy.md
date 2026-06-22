---
name: project-web-deploy
description: NowTrendIn has a public web build on Heroku for access from any network (no LAN/Expo Go needed)
metadata: 
  node_type: memory
  type: project
  originSessionId: 68bada2a-c5b3-4db5-a55b-bc9a4f6844d3
---

NowTrendIn 2.0 has a **public web version** so the founder can use the app from any network/device without the home-LAN Expo Go setup (set up 2026-06-10 before founder traveled).

- **Public URL:** https://nowtrendin-web-8c1bb8c9f7f2.herokuapp.com/
- **Heroku app:** `nowtrendin-web` — a tiny Express server (`web-deploy/server.js`) serving the static Expo web export (`dist/`) with SPA fallback for expo-router.
- It hits the **live** engine (`nowtrendin`) + backend (`nowtrendin-backend`); both return `Access-Control-Allow-Origin: *`, so CORS works from the web origin.
- **It is a SNAPSHOT** — frontend code changes do NOT appear until the web bundle is rebuilt + redeployed.

**To update the web app after a frontend change:** run `./redeploy-web.sh` from the `NowTrendin v2.0/` dir (rebuilds `npx expo export --platform web`, copies `dist/`, commits, `git push heroku HEAD:main` to the `nowtrendin-web` remote). The `web-deploy/` dir is its own git repo (gitignored in the parent) with the Heroku remote already set.

**The three deploy targets remain:** engine → `nowtrendin` (`git push heroku HEAD:main`), backend → `nowtrendin-backend` (`git subtree push --prefix backend heroku main`), frontend source → `origin`. The web build is a 4th target, rebuilt on demand. Continuing to code/deploy only needs internet, not the home LAN — that constraint is purely the Expo Go phone preview. [[project-nowtrendin-2]], [[feedback-expo-same-network-first]].
