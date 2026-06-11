# Now TrendIn — Platform Map (iOS · Android · Desktop · Web)

_Last updated: 2026-06-11._

One codebase, two build artifacts, four delivery surfaces:

| Surface | Artifact | Tooling | Status |
|---|---|---|---|
| **iOS (App Store)** | Expo **native** app (`frontend/`) | EAS Build (Expo cloud — no Mac needed for build) | Phase 8: native build also unblocks Stripe + push |
| **Android (Play Store)** | Expo **native** app (`frontend/`) | EAS Build | same as iOS |
| **Desktop (Windows/Mac installable)** | Expo **web** build wrapped in **Capacitor + Electron** (`capacitor/`) | `setup-capacitor.ps1` → `electron:make` | scaffolded — needs Node installed |
| **Browser (anywhere)** | Expo **web** build on Heroku (`web-deploy/`) | `redeploy-web.ps1` | live |

The Capacitor project also carries optional **android/** and **ios/** WebView wraps of
the web build. Keep these for testing/kiosk use — the **store** mobile apps should be
the Expo native build (real native modules, better performance, and each store allows
only one "Now TrendIn" app identity anyway).

## Workflows

**After any frontend change**, each surface refreshes independently:

```powershell
# Browser:  rebuild + push the Heroku snapshot
powershell -ExecutionPolicy Bypass -File "...\NowTrendin v2.0\redeploy-web.ps1"

# Desktop:  rebuild bundle + re-sync the Capacitor/Electron shell
powershell -ExecutionPolicy Bypass -File "...\NowTrendin v2.0\setup-capacitor.ps1"
cd capacitor\electron ; npm run electron:start     # run it
cd capacitor\electron ; npm run electron:make      # package installer

# Mobile (native): Expo Go for dev; EAS Build for store binaries (Phase 8)
```

## Known constraints / gotchas

1. **Node.js is the prerequisite for everything** (web rebuild, Capacitor, EAS). Install
   LTS from nodejs.org, then use a fresh terminal.
2. **CORS — already fine.** Engine FastAPI is `allow_origins=["*"]` and Django is
   `CORS_ALLOW_ALL_ORIGINS=True`, so `capacitor://localhost` / `https://localhost`
   origins work without backend changes.
3. **Google OAuth inside a WebView**: Google blocks sign-in from embedded WebViews
   (`disallowed_useragent`). In the Capacitor shells, Google login must open the
   **system browser** (Capacitor Browser plugin / deep-link return) — email+password
   auth works as-is. Test this first on desktop.
4. **iOS builds need a Mac** (Xcode) for the Capacitor ios/ wrap; `cap add ios`/sync
   errors on Windows are expected. The Expo-native iOS path avoids this via EAS cloud.
5. **Deep links / routing**: the shells load `index.html` and navigate client-side
   (expo-router). Cold-starting into a deep route inside the shell may need a SPA
   fallback tweak if it ever 404s.
6. **Token storage**: the web bundle already runs on Heroku web, so its storage
   fallbacks (localStorage vs expo-secure-store) carry over to the shells unchanged.
7. **`@capacitor-community/electron` is community-maintained** — if it ever breaks
   against a new Capacitor major, the fallback is a plain Electron wrapper around
   `frontend/dist` (small, easy to generate).
