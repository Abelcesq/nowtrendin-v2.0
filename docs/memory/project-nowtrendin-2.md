---
name: project-nowtrendin-2
description: "Now TrendIn 2.0 — Attention Intelligence app (expo-router + NativeWind + Django/Heroku). Architecture, tiers, phases, run/redeploy."
metadata: 
  node_type: memory
  type: project
  originSessionId: 68bada2a-c5b3-4db5-a55b-bc9a4f6844d3
---

## What it is
Now TrendIn 2.0 is a dark-mode React Native (Expo) "Attention Intelligence" app whose
core product is the **Gradient Score**. It replaced the v1 todo app in `frontend/`.

## Stack (LOCKED — see repo-root CLAUDE.md)
- Expo SDK 54, RN 0.81, React 19
- **expo-router** (file-based) — NOT react-navigation
- **NativeWind v4** (Tailwind) for ALL styling — no StyleSheet
- **lucide-react-native** for ALL icons — no other icon lib
- Zustand state, react-hook-form + zod, expo-secure-store
- Deferred (break Expo Go): @stripe/stripe-react-native, expo-notifications push

## Brand colors & logo (v2.0 — matches v1.0 logo PNG)
Theme is LIGHT (not dark). Defined in `frontend/tailwind.config.js`.
- Background `bg` #F4F5F7 (light grey) · cards `surface`/`elevated` #FFFFFF · `border` #E4E7EC
- Text: primary #1A1A2E · secondary #5B6472 · muted #9AA3B0
- Accent/active (tabs, scores, buttons): green `primary` #00C896
- **Wordmark** ("Now TrendIn"): "Now" = `brandMaroon` #6E1A17 (dark maroon),
  "TrendIn" = `brandOrange` #E8551C (orange-red). Rendered via `<Wordmark>` in components/ui/Logo.tsx.
- **Flame logo gradient** (top→bottom): flameGold #F7A41C → flameOrange #F26522 →
  flameRed #CF2A1B → flameDeep #6E1410; arrow = silver/grey. The logo is a flame with an
  integrated rising chart-arrow.
- Logo asset: user provided the real PNG. Place at `frontend/assets/logo.png` and render with
  `<Image source={require('.../assets/logo.png')} />` in splash + home header for pixel-exact match.
  Until then, `components/ui/Logo.tsx` renders an SVG stand-in approximating it.
- Tier colors: consumer #2D7EEF · business #00C896 · enterprise #D4A017.

## Source of truth files
- `CLAUDE.md` (repo root) — master rules Claude Code must follow every session
- `docs/NOW_TRENDIN_2_FLOW.md` — screen-by-screen wireframes
- `frontend/constants/tiers.ts` — THE single authority for tier access control

## Membership tiers (constants/tiers.ts)
| Tier | $/mo | Data freshness | search | new query | sources | tokens |
|------|------|----------------|--------|-----------|---------|--------|
| consumer | 49 | ≥12h | ✗ | ✗ | ✗ | 0 |
| business | 499 | ≥1h | ✓ | ✗ | ✗ | 0 |
| enterprise | 25000 | live | ✓ | ✓ | ✓ | 1000 |
Helpers: `canAccess(tier, feature)`, `isDataAccessible(tier, dataAgeMs)`. Never hardcode tier checks.

## Folder map (frontend/)
- `app/(auth)/` splash, onboarding, login, signup, forgot-password, membership
- `app/(app)/` _layout (tier-aware tabs), index (dashboard), history, search, alerts, profile/index
- `components/ui/` Screen, Button, Input · `components/trends/TierGate.tsx`
- `lib/api.ts` (real fetch client → Heroku) · `lib/auth.ts` (**mock auth, Phase 1 only**)
- `store/auth.store.ts` (Zustand: user/tier/token)

## Phase status
- Phase 1 ✅ DONE: auth + onboarding + membership shell, mock auth, TierGate, tab shell.
  Dev bundle verified compiling via Metro. Committed: "Now TrendIn 2.0 Phase 1".
- Phase 2 ✅ DONE (frontend): tier-based age filtering. `lib/signals.ts` holds a mock signal
  dataset + `getSignals(tier)` returning {accessible, lockedCount, total} via `isDataAccessible`.
  Dashboard + History are data-driven; `components/trends/SignalCard.tsx` and
  `LockedSignalsBanner.tsx` (shows N hidden newer signals + upgrade CTA to next tier).
  Consumer sees ≥12h, Business ≥1h, Enterprise all. To finish Phase 2 server-side: add Django
  `/api/signals/?min_age=` and swap getSignals() for `signalsApi.list({min_age})` — no screen changes.
- Phase 3 ✅ DONE: Gradient Score display. `components/ui/GradientScoreRing.tsx` (SVG arc, sizes
  sm/md/lg/xl). Signal detail screen at `app/signal/[id].tsx` (full-screen over tabs, registered in
  root Stack): dual ring (detection green + confidence blue), "What to do" action card (per stage),
  why-this-matters, expandable score breakdown (Quality/Momentum/Context bars), Set Alert button.
  SignalCard taps → `/signal/{id}`. Dashboard has an xl hero ring for the top signal.
  Detail helpers in lib/signals.ts: getSignalById, scoreGap, actionFor, breakdownGroups.
- Phase 4: search + alerts + push. Phase 5: enterprise direct-query + token deduction + source editor.

## Milestone 2 — REAL Django JWT auth DONE (replaced the mock)
- Backend `accounts` app (backend/accounts/): Profile(tier, tokens_remaining); endpoints under
  /api/auth/ — signup, login, me (GET+PATCH), refresh — via djangorestframework-simplejwt
  (1d access / 30d refresh; JWT is default DRF auth). PATCH /me sets tier (enterprise→1000 tokens).
  Deployed to nowtrendin-backend (v8), migrated. Verified live: signup/login/me/tier/bad-pass.
- Frontend: lib/auth.ts now REAL (login/signup/fetchMe/setTier/logout; same {user,token} shape).
  api.ts request helper attaches Bearer from SecureStore. Tokens persisted (access_token +
  refresh_token in expo-secure-store). splash.tsx hydrates user via fetchMe() on launch (validates
  token → routes by tier; clears on expiry). login/signup hit backend; signup shows dup-email error;
  membership.choose()/free-trial call setTier() to persist tier server-side. Google button = "coming
  soon" (OAuth deferred). Bundle verified.
- Edit Profile: backend Profile has phone + phone_verified. PATCH /api/auth/me updates name/email
  (uniqueness-checked)/phone; POST /api/auth/change-password (validates current, min 8). Frontend
  screen app/(app)/profile/edit.tsx (in profile stack → keeps tab bar) with name/email/phone +
  change-password; lib/auth updateProfile()/changePassword(); store.updateUser(). Profile "Edit
  Profile" row → /profile/edit.
- SMS 2FA: BUILT via Twilio. Profile.otp_code/otp_expires. POST /api/auth/phone/send-code (6-digit,
  10-min, Twilio Messages API) + POST /api/auth/phone/verify → phone_verified. _send_sms() returns 503
  "SMS is not configured yet." until env vars set. **ACTION NEEDED**: set on nowtrendin-backend:
  TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER (a Twilio number). Then 2FA is live.
  Frontend: edit.tsx has Send/Verify code flow; lib/auth sendPhoneCode()/verifyPhoneCode().
- Greeting ranges (home): 1–10:59 morning, 11–14:59 day, 15–17:59 afternoon, 18–20:59 evening,
  21–00:59 night.
- Alerts: backend Alert model (topic_key/display, score_type, threshold, notify_email/push, active)
  + CRUD at /api/alerts/ & /api/alerts/{id}/ (user-scoped). Frontend app/(app)/alerts.tsx: list w/
  toggle(active)+delete, create form (topic + live-signal suggestions, score type, threshold stepper,
  push/email switches) via React Query (['alerts']). Detail "Set Alert" passes topic+key params.
  lib/api alertsApi. NOTE: alerts are stored but NOT yet evaluated/fired (no engine cron checking
  thresholds + no push/email send pipeline) — that's the next step to make them actually notify.
- Search: app/(app)/search.tsx — searches live tier feed (TrendCard results); enterprise sees a
  tokenised direct-query note (not yet functional). Tab still gated to business+enterprise.
- Notifications: Profile.notify_email/notify_push; UserSerializer notifyEmail/notifyPush; PATCH /me
  handles them. Frontend profile/notifications.tsx (Email/Push switches, autosave) + lib/auth
  updateNotifyPrefs. Profile rows now route to /profile/edit, /profile/membership, /profile/notifications.
- Enterprise direct query (score a topic not in the list) — DONE end-to-end:
  * Engine: POST /query {topic} → collect_for_term() targeted HN Algolia + GitHub search → score →
    persist_velocity_score → returns {found, result, signals_collected}. Also helpers added.
  * Django: POST /api/query/ (DirectQueryView) — enterprise-only (403 else), tokens>0 (402 else),
    proxies to engine, deducts 1 token ONLY when found, returns {..., tokensRemaining}. requests dep added.
  * Frontend: search.tsx "Score any topic" box (enterprise/canQueryNew) — shows tokens, "Score X · 1 token";
    on success injects mapped Signal into ['scores'] cache + navigates to /signal/{topic_key}; updateUser
    tokens. lib/api queryApi.run(). Verified live: rust gpu → found, 80 signals, tokens 1000→999.
- Tier freshness UPDATED: Consumer >=1h, Business >=30m, Enterprise live (was 12h/1h). Aging waterfall:
  new score is Enterprise-only → 30m Business → 1h Consumer → (future) 1d partners. constants/tiers.ts
  dataFreshness; dataWindowLabel "1h+"/"30m+"; LockedSignalsBanner "30m+".
- Research archival + retention (engine) — DONE: score_archive table (monthly latest-per-topic snapshot,
  PK snapshot_date+topic_key). Functions archive_scores_snapshot/prune_velocity_scores(30d, keeps latest
  per topic)/prune_archive(395d)/run_retention(). APScheduler monthly job (1st 03:00 UTC) + `--mode=archive`
  CLI. Verified: snapshot archived 1050 topics. velocity_scores retained indefinitely until prune (>=30d).
- TIER AGING FIX (important): engine re-scores every topic each cycle so latest scored_at is always
  recent → Consumer (>=1h) and Business (>=30m) saw 0 results. FIX: /scores now returns
  `first_scored_at` (per-topic MIN(scored_at)); mapSignal sets Signal.firstSeenAt; filterFeed gates on
  firstSeenAt (createdAt still used for "Xm ago"/sort). A topic ages into lower tiers by FIRST-seen
  time; brand-new queries stay hidden until old enough. Applies to ALL tiers/home pages (same useTierFeed).
- Alert firing DONE: Django EvaluateAlertsView (X-Internal-Key) pulls /scores, fires active alerts whose
  threshold crossed (6h cooldown), emails user (console backend until EMAIL_HOST set), sets
  last_triggered_at. Engine scheduler POSTs ALERT_EVAL_URL after each cycle. Shared INTERNAL_API_KEY set
  on both Heroku apps. Alerts screen shows "🔔 Triggered {ago}". Push still needs a dev build (Expo Go can't).
- Forgot password DONE: Profile reset_code/reset_expires; POST /api/auth/forgot-password (emails 6-digit,
  15min, always 200) + /reset-password. forgot-password.tsx = email→code+newpass→done. lib/auth
  requestPasswordReset/resetPassword.
- Android pinch-zoom DONE: Screen uses gesture-handler Gesture.Pinch + reanimated transform scale on
  Android (1–3x); iOS keeps native ScrollView zoom. Both bundles verified.
- EMAIL: to actually send (alerts + reset), set on nowtrendin-backend: EMAIL_HOST/EMAIL_PORT/
  EMAIL_HOST_USER/EMAIL_HOST_PASSWORD (e.g. SendGrid) + DEFAULT_FROM_EMAIL. Until then emails log to dyno.
## Risk Gradient Score (financial risk) — DONE
- Engine repo has `financial_risk_gradient.py` (from user). 5-stage risk diffusion (Dark Positioning →
  Expert → Consumer → Media → Retail); early smart-money signals score highest; crowdedness interpretation.
  Routed through db_compat (shared Postgres): risk_signals + risk_scores tables.
- Collectors: SEC EDGAR insider Form 4 + 8-K for SEC_WATCHLIST (15 large caps) — LIVE, primary source
  (fixed: use requests not urlopen, SEC gzips). GDELT news (no key, but 1 req/5s rate-limited).
  Reddit finance (public JSON, usually BLOCKED from Heroku datacenter IP → 0). FRED macro + YouTube
  finance = key-gated (set FRED_API_KEY / YOUTUBE_API_KEY to activate).
- Endpoints on engine: GET /risk/scores, GET /risk/{topic}, POST /risk/collect. Scheduler runs risk
  collect+score each cycle; `--mode=risk` CLI. VERIFIED LIVE: 353 SEC signals → 15 risk topics; e.g.
  Meta DET 85/CONF 75 ELEVATED, 16 stage-1 dark-positioning signals, no retail = "smart money before the crowd".
- App: dashboard Attention|Risk toggle (index.tsx). useRiskScores hook, gradientApi.fetchRiskScores,
  components/trends/RiskCard.tsx (DET/CONF, stage badge, 5-stage diffusion bars, interpretation). Risk feed
  is NOT tier-aged (shown to all tiers currently).
- TODO for richer risk data: set FRED_API_KEY + YOUTUBE_API_KEY on engine; Reddit needs PRAW creds (datacenter
  IP blocks public JSON). SEC_USER_AGENT default ok.
- Risk integrity/analysis features DONE: source_provenance audit ("Sources: sec_edgar · …") on RiskCard +
  detail; RiskExplainer banner (proprietary T&C); DETECT marker on Dark stage; risk tier-aged via firstSeenAt
  (first_scored_at). MATURITY classification (_risk_maturity): watchlist names → ESTABLISHED (+ honest note:
  insider Form 4 routine for large caps, score = current positioning intensity NOT confirmed acceleration,
  needs 2+ cycles since monitoring just began); macro themes → MACRO; else EMERGING. risk_scores gained
  source_provenance/maturity/maturity_note cols (per-ALTER commit/rollback migration — PG aborts txn on
  failed ALTER, so each ALTER must commit/rollback independently — IMPORTANT pattern).
- Risk detail screen app/risk/[key].tsx (RiskCard taps → /risk/{key}; useRisk hook finds in cached list):
  dual DET(blue)/CONF(green) rings, action, **Market tenure panel** (maturity + note + first-cycle caveat),
  what-this-means, full diffusion pipeline w/ DETECT + stage descriptions, score components bars, provenance.

- STILL DEFERRED: Google OAuth, Stripe payment, push delivery (needs Expo dev build), Partner tier,
  risk detail screen + risk tier-gating.

## (Old) Mock auth behavior — REPLACED by Milestone 2 above
- `mockLogin` → returns user with tier 'consumer' (existing member) → dashboard
- `mockSignup` → user with tier null → membership selection
- membership card → `updateTier()` → enters app. To test other tiers, change mockLogin tier
  or pick a plan on the membership screen.

## Run locally (Expo Go)
```
cd frontend
npx expo start          # scan QR with Expo Go; or press t for tunnel if firewall blocks
```
Notes (Windows): if "running scripts disabled" → `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force`.
The dev bundle is served as plain JS (Hermes precompile via `expo export` fails on zod v4 private
fields — that's expected and does NOT affect Expo Go).

## Backends — TWO services
1. **Gradient Score engine** (the real product) — separate **FastAPI** app, already live at
   `https://nowtrendin-e62dcb9ecb69.herokuapp.com` (repo `Abelcesq/nowtrendin-score-prototype`).
   Endpoints: GET /scores, /scores/{topic_key}, /scores/{topic_key}/history, POST /collect.
   `/scores` returns rich rows: detection_score, confidence_score, heisenberg_gap, signal_stage,
   what_to_do_*, why_this_matters, what_to_watch, component_groups {signal_quality/momentum/context},
   ai_tier_label, platforms_active. The v2.0 RN app consumes this DIRECTLY (mobile fetch = no CORS issue).
   Source of the engine is in repo `transfer/` (gravitational_anomaly_detector.py etc.).
   Scoring: Detection=G·.40+D·.25+I·.20+M·.10+C·.05, Confidence=I·.35+M·.30+G·.20+C·.10+D·.05.
   ENGINE REPO is local at `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin` (separate
   from v2.0). Remotes: heroku→nowtrendin.git (deploys the engine), origin→github nowtrendin,
   prototype→github nowtrendin-score-prototype. Deploy engine: `git push heroku main` from that dir.

### Milestone 1 — calibration + Postgres migration DONE (this engine repo)
   - The 6 calibration edits (imports, signal_count_modifier, apply_calibration+apply_ai_intelligence,
     noise filter via is_meaningful_topic) were already integrated by a prior session and are live.
   - Added `db_compat.py`: SQLite/Postgres shim. When DATABASE_URL set → psycopg2 + on-the-fly SQL
     translation (?→%s, datetime('now')→(now())::text, INSERT OR IGNORE→ON CONFLICT DO NOTHING,
     AUTOINCREMENT→SERIAL, PRAGMA skipped, RealDictCursor). All sqlite3.connect()→db_compat.connect().
     2 upserts (topic_maturity, research_history_cache) → explicit ON CONFLICT DO UPDATE. Fixed 3
     pre-existing ON CONFLICT upserts to QUALIFY existing-row refs with table name (PG ambiguity:
     topic_registry, topic_maturity, topic_baselines). psycopg2-binary in requirements.
   - Provisioned heroku-postgresql:essential-0 (~$5/mo) on app nowtrendin (postgresql-shaped-41629).
     Deployed (v40+). Seeded 48 known topics into PG. verify_integration: ALL 6 checks pass on PG.
     /scores serves from PG (durable). Full collect+score cycle runs clean on PG.
   - Continuous collection: IN-APP APScheduler wired into the FastAPI startup hook
     (gravitational_anomaly_detector.py ~line 2100). Runs a full collect+score cycle every 30 min
     + daily (06:00 UTC) recompute_velocities, on the web dyno → shared Postgres. Confirmed in logs:
     "[startup] APScheduler started — collect+score every 30 min". The redundant Heroku Scheduler
     addon was REMOVED (in-app scheduler supersedes it). Procfile: `web: python
     gravitational_anomaly_detector.py --mode=api` (single uvicorn process → one scheduler).
   - EXPECTATION: tier classification is correct immediately; full 90+ score climb needs ~24h of
     continuous collection (inertia needs 2+ consecutive 6h windows). Reddit creds still unset
     (REDDIT_CLIENT_ID/SECRET) → only github/HN/blogs collecting.
2. **Django** app `nowtrendin-backend` → `https://nowtrendin-backend-acb79c396814.herokuapp.com`
   (old todo API). Will host AUTH (/api/auth/*) later. Redeploy: `git subtree push --prefix backend heroku main`.

## Gradient Score integration (frontend) — DONE
### Engine connection pooling (CRITICAL fix)
The serve path opens a DB connection PER ROW (get_topic_maturity_state in apply_calibration). On
Heroku essential-0 Postgres (~20 conn cap) this made /scores with default limit=50 exhaust
connections and time out (H12, engine effectively down; limit<=10 worked). FIX: db_compat.py now uses
psycopg2.pool.ThreadedConnectionPool(1,10); connect() borrows, _Conn.close() returns to pool. /scores
back to ~0.5s. If adding heavy per-row DB work or higher traffic, keep this pool (don't revert to
per-call psycopg2.connect). The in-app APScheduler thread shares the same pool (maxconn 10).

## Gradient Score integration (frontend)
- `lib/gradientApi.ts`: `fetchScores()` + `mapSignal()` mapping engine rows → Signal (incl. rich fields).
  Base URL env-overridable via EXPO_PUBLIC_GRADIENT_API.
- `lib/signals.ts`: Signal type extended (overall, gap, gapMeaning, whatToDo, why, whatToWatch,
  platforms, groups). `filterFeed(list,tier)`, MOCK_SIGNALS fallback, stageColor (+WATCH/DECAY).
- `hooks/useSignals.ts`: React Query `useSignals()` (fetch live, fall back to MOCK on error → isSample flag),
  `useTierFeed(tier)`, `useSignal(id)`. QueryClientProvider added in app/_layout.tsx.
- Dashboard/History/Detail consume the hooks (loading spinners, sample-data note). Detail renders the
  engine's real what_to_do / why / what_to_watch / component_groups (det+conf bars) / platforms / gap_meaning.

## Connections
GitHub `github.com/Abelcesq/nowtrendin-v2.0` · Heroku `nowtrendin-backend` ·
Expo EAS project `ef045a1d-05df-4ab5-b474-508c412ae420` (owner now-trendin).
