# CLAUDE.md — Now TrendIn 2.0
## Master Instructions for Claude Code

> This file is the single source of truth for all development decisions.
> Claude Code MUST read this file before making any code change.
> Do NOT deviate from these specifications without explicit user confirmation.

---

## 1. PROJECT IDENTITY

**App:** Now TrendIn 2.0
**Purpose:** Attention Intelligence Platform — provides the Gradient Score,
             a proprietary algorithm that measures where human attention
             is moving before it arrives.
**Tagline:** "The first instrument that measures where human attention is moving before it arrives."
**Platform:** React Native (Expo) — iOS + Android
**Backend:** Django REST API on Heroku with Postgres
**Repo:** github.com/Abelcesq/nowtrendin-v2.0

---

## 2. TECH STACK — NEVER CHANGE THESE

```
Mobile:      React Native 0.81 + Expo SDK 54   (React 19)
Routing:     expo-router (file-based, NOT React Navigation)
Styling:     NativeWind v4 (Tailwind CSS for React Native)
Icons:       lucide-react-native EXCLUSIVELY — no other icon library
State:       Zustand (global) + React Query (server state)
Auth:        Django JWT + Google OAuth via expo-auth-session
Payments:    Stripe via @stripe/stripe-react-native
Forms:       react-hook-form + zod validation
HTTP:        axios/fetch with interceptors (in lib/api.ts)
Storage:     expo-secure-store (tokens) + AsyncStorage (preferences)
Push alerts: expo-notifications
```

> **Live status (current):** Real Django JWT + Google OAuth auth is in production —
> backend on Heroku (`nowtrendin-backend`), engine on Heroku (`nowtrendin`). Phases
> 1–4 are complete (auth, tier-gated dashboard, Gradient Score, search/alerts).
> Stripe and `expo-notifications` push are **still deferred** — they require a custom
> dev client and break Expo Go. Add when moving off Expo Go for production builds.

**FORBIDDEN:** Do not use:
- react-navigation (use expo-router only)
- Any icon library other than lucide-react-native
- Styled-components, emotion, or StyleSheet (use NativeWind/Tailwind only)
- Any UI component library (build from scratch with NativeWind)
- React Native Paper, NativeBase, RN Elements, etc.

---

## 3. DESIGN SYSTEM — EXACT VALUES ONLY

### 3.1 Color Tokens (tailwind.config.js)

```js
colors: {
  primary:   '#00C896',   // Now TrendIn green — buttons, accents, active states
  primaryDk: '#009970',
  brandOrange: '#EE6A2A',  // Wordmark "Now"
  brandMaroon: '#B5341B',  // Wordmark "TrendIn" (maroon-orange, matches logo N)
  bg:        '#F4F5F7',   // Page background (light grey — matches v1.0)
  surface:   '#FFFFFF',   // Cards, panels
  elevated:  '#FFFFFF',   // Modals, drawers
  border:    '#E4E7EC',
  textPrimary:   '#1A1A2E',
  textSecondary: '#5B6472',
  textMuted:     '#9AA3B0',
  consumer:    '#2D7EEF',   // Blue
  business:    '#00C896',   // Green
  enterprise:  '#D4A017',   // Gold
  success:  '#00C896',
  warning:  '#D4A017',
  error:    '#DC2626',
  info:     '#2D7EEF',
  breakout:    '#00C896',
  strong:      '#2D7EEF',
  emerging:    '#D4A017',
  watching:    '#E85A1E',
  monitoring:  '#94A3B8',
}
```

### 3.2 Typography
```
text-xs 10 · text-sm 12 · text-base 14 · text-lg 16 · text-xl 18
text-2xl 22 · text-3xl 28 · text-4xl 36 · text-5xl 48
font-normal 400 · medium 500 · semibold 600 · bold 700 · black 900
```

### 3.3 Spacing — Tailwind only (p-2..p-6, gap-2..gap-4, screen = px-5)
### 3.4 Radius — rounded-lg 8 · rounded-xl 12 · rounded-2xl 16 · rounded-full

---

## 4. ICON SYSTEM — LUCIDE ONLY

```tsx
import { TrendingUp, Lock, Bell } from 'lucide-react-native';
<TrendingUp size={20} color="#00C896" />
```
Sizes: 14 tiny · 16 small · 20 standard · 24 header · 28 large · 32 hero · 48 empty-state

Mapping: Trends→TrendingUp, History→Clock, Search→Search, Profile→User,
Alert→Bell, Lock→Lock, Consumer→Zap, Business→Briefcase, Enterprise→Building2,
Gradient Score→Activity, Breakout→Flame, Home→Home, Back→ChevronLeft, Close→X,
Check→Check/CheckCircle, Email→Mail, Password→KeyRound, Eye/EyeOff, Logout→LogOut.

---

## 5. FOLDER STRUCTURE — STRICT

```
app/
├── _layout.tsx               # Root — imports global.css, gesture handler, providers
├── index.tsx                 # Redirect → (auth)/splash or (app)
├── (auth)/
│   ├── _layout.tsx
│   ├── splash.tsx
│   ├── onboarding.tsx
│   ├── login.tsx
│   ├── signup.tsx
│   ├── forgot-password.tsx
│   └── membership.tsx
└── (app)/
    ├── _layout.tsx           # Tab bar (tier-aware)
    ├── index.tsx             # Dashboard
    ├── history.tsx
    ├── search.tsx
    ├── alerts.tsx
    └── profile/index.tsx
lib/        api.ts · auth.ts (mock for now)
store/      auth.store.ts
components/  ui/{Screen,Button,Input}.tsx · trends/TierGate.tsx
constants/  tiers.ts          # ← THE authority on access control
```

---

## 6. MEMBERSHIP TIERS — access rules live ONLY in constants/tiers.ts

| Tier | Price/mo | Data freshness | Search | New query | Sources | Query Tokens | AI Grade /mo |
|------|----------|----------------|--------|-----------|---------|--------|------|
| Consumer   | $49      | ≥ 24h  | ✗ | ✗ | ✗ | 0 | 25 |
| Business   | $499     | ≥ 12h  | ✓ | ✗ | ✗ | 0 | 250 |
| Enterprise | $250,000 | live   | ✓ | ✓ (1 token/search) | ✓ | 100000 (5 users, shared) | 100000 |

**AI Grade** (the "Grade" tool — Perplexity + Claude, ~$0.012/grade, 12h-cached) is on **all
three tiers**, metered by a separate monthly grade-credit allowance (`profile.grade_tokens`,
Consumer 25 / Business 250 / Enterprise 100000). Enforced in Django `GradeView`; 1 credit charged
only when a proposed score returns. Distinct from Enterprise query tokens.

Use `canAccess(tier, feature)` and `isDataAccessible(tier, dataAgeMs)` everywhere.
Never hardcode a tier check anywhere else.

**Data-aging waterfall:** a new score is Enterprise-only at first (live, the moment
it is obtained) → at 12 h it becomes visible to Business → at 24 h to Consumer →
(future) at 1 day+ to partners. X is scanned every 6h over the top-100 topics:
the volume scan (counts/recent) is FREE vs the 15k post cap; deep author-gradient
pulls (search/recent, ~100 posts each) fire only on movers and are hard-capped at
X_MONTHLY_POST_BUDGET (12,000 posts/mo) — status at GET /x/budget. Consumer/Business
cannot run queries; Enterprise can run direct queries at 1 token per search.
Enforced purely by `dataFreshness` + `isDataAccessible(tier, age)` on the score's age.
**Retention:** engine persists all scores in Postgres (≥30-day history); monthly
research snapshots for a year are a planned backend job.

---

## 7. MANDATORY PATTERNS
- Every screen wrapped in `<Screen>` (components/ui/Screen.tsx)
- Every button is `<Button variant size>` — never raw styled TouchableOpacity
- Every restricted region wrapped in `<TierGate>`
- The Gradient Score hero is `<GradientScoreRing>` (Phase 3)

---

## 8. TERMS & CONDITIONS — MANDATORY CLAUSE
All users must accept at signup (checkbox blocks submit):
"All Gradient Score results, trend analyses, signal data, and any information
generated by or accessed through the Now TrendIn platform are proprietary to
Now TrendIn LLC. Users have no ownership rights to any data, scores, analyses,
or results obtained through the platform."

---

## 9. PHASES — current status
1. ✅ Auth + onboarding + membership shell (real Django JWT + Google OAuth)
2. ✅ Dashboard + tier-restricted nav (TierGate + data-aging filter)
3. ✅ Gradient Score display (rings, signal cards, breakdown)
4. ✅ Search + alerts (push deferred — needs custom dev client)
5. ✅ Enterprise direct-query + token deduction
6. ✅ Risk/Other tab (FINRA + OFR + WhaleWisdom + creators + broadcast)
7. ✅ Trend Beneficiary (SanDisk-pattern), auto-theme extension
8. ⏳ Stripe payments + push notifications (require custom dev client)

---

## 10. MEMORY CHECKPOINTS — verify before each change
1. lucide-react-native for ALL icons?
2. NativeWind/Tailwind for ALL styling?
3. expo-router for ALL navigation?
4. Tier logic in constants/tiers.ts only?
5. Restricted features use TierGate?
If any answer is NO — stop and fix.

---

## 11. THEME — light (matches v1.0). bg #F4F5F7, surface #FFFFFF (white cards w/ soft shadow),
dark text #1A1A2E. Green #00C896 = accents/active states. Wordmark: "Now" brandOrange + "TrendIn"
brandMaroon. Flame logo preserved from v1.0 — rendered via components/ui/Logo.tsx (SVG stand-in;
swap for the original logo.png in assets/ when available). StatusBar = dark-content.

## 12. WEB TERMINAL + DESKTOP (3-platform parity)
The enterprise **web terminal** (`web-terminal/`, React+Vite, Heroku app
`nowtrendin-terminal`) and the **desktop** app (`tauri-desktop/`, Tauri over the
same web build) are the institutional surfaces; the **mobile app** (`frontend/`)
is consumer/business. The trend **signal-detail** and **market-analysis** pages
present the SAME sections, data points, and color scheme on all three (web may add
MORE — denser filters, extra columns). Mobile color scheme mirrored for the web
detail rails in `web-terminal/src/lib/mobileTheme.ts` (Detection #2D7EEF,
Confidence #00C896, stage/tier/maturity/feed palettes). The avatar opens a full
Account view (edit profile, change password, **Authorized Users** = the Enterprise
5-seat / 100,000 shared-token entitlement, admin identified). Parity is enforced by
the **Frontend Consistency** agent (`/frontend-consistency`).

## 13. DATA-QUALITY + MONITORING (the engine guardrails)

> **DATA RETENTION RULE (hard — do not override):** All `velocity_scores` rows
> are retained for **90 days**. Never delete scored data within this window —
> historical scores are required for trend tracking, calibration, and accuracy-
> ledger validation. Only rows older than 90 days are removed by
> `_prune_velocity_scores()`. Do NOT change this to a count-based prune; count-
> based deletes valid history for frequently-scored topics. Do NOT add any
> function that deletes `velocity_scores` rows based on quality judgements
> (e.g., corroboration level) — the floor is enforced at SCORING time so that
> new bad data never enters; old data stays for the full retention window.

- **Catch-all corroboration floor** (`CATCHALL_MIN_SOURCES`, default 2): a topic
  classifying into news/general must have ≥2 distinct sources to score, with hard
  exemptions (expert-tier signal, high magnitude, ledger/pending). De-congests the
  catch-all without losing early signals. NOT a raw post-volume floor (that would
  break the before-it-arrives thesis). Floor applied at SCORING time only (forward-
  only); historical rows within the 90-day window are never retroactively deleted.
- **Catch-all floor trend monitoring**: `catchall_auditor()` writes a row to
  `catchall_floor_log` table each run (total_scored, catchall_count, catchall_pct,
  single_source_leak, min_sources). Reads the last row to compute `floor_trend`
  (IMPROVING / STABLE / WORSENING). Alerts on WORSENING (leak growing >10 since
  last check) — signals floor disabled or new junk bypassing corroboration.
- **Stale window rule**: `collector_health.COLLECTOR_EXPECTATIONS` `max_gap_minutes`
  MUST exceed `COLLECT_INTERVAL_MIN + 60m` for every collector that runs with the
  main cycle. `risk` runs inside `_collect_phase` (not standalone), so its window
  must be `COLLECT_INTERVAL_MIN + 60` (currently 360+60=420m). The scheduler
  validates this on startup and logs a WARNING on mismatch — update both
  `collector_health.py` AND this rule whenever `COLLECT_INTERVAL_MIN` changes.
- **Fragment gate**: single-word junk + multi-word filler-anchored fragments
  rejected at scoring + pruned each cycle.
- **Topic maturity** (NEW/EMERGING/ESTABLISHED) derived from the maintained
  `topic_lifecycle` table (cycles + age); ESTABLISHED topics discounted.
- **Stage from Detection** (`stageOf`) everywhere; `Now TrendIn` view ranks by the
  proprietary **N** (`nowtrendin_score`), `All Signals` by Detection.
- **9 monitoring agents** (`monitoring_agents.py` → `/monitor` `run_all`): Source Watchdog,
  Scorer Watchdog, Pipeline Integrity, Topic Quality Auditor, Catch-All Auditor (daily EOD),
  Cost Sentinel, Data Subscriptions, Calibration Auditor, **Canonical Date Auditor** (B3a —
  `/monitor/datecanon`; audits every date-semantic + discovered `*_date` column so §14
  compliance is verified for ALL sources, new ones auto-covered). Plus the **Prewarm Agent**
  (operational, read-only, API-process `/prewarm` — keeps every list-feed superset cache hot).
  Full specs: `AGENT_CHARTER.md` (Agents 1–16) + `DATA_BUILDING_BLOCKS.md`.

## 14. CANONICAL DATE & TIME MODEL — data streamlining → Accuracy-Ledger viability

> **Canonical rule (hard — enforced centrally, do not bypass):** every date-semantic
> value is normalized to a PRIMARY canonical date `signal_date` = ISO `YYYY-MM-DD` —
> the ONE key every row is sorted, matched, and scored on. Two SECONDARY 24h-UTC time
> columns accompany it: `source_time` = the SOURCE's own `HH:MM:SS` (empty if the
> source is date-only) and `signal_time` = OUR fetch `HH:MM:SS`. Going forward EVERY
> fetched row carries a `signal_time` stamp (format `17:15:00`).

- Enforced by `date_utils.py` (`to_iso_date` / `to_iso_dt` / `iso_time_of` /
  `canonical_date_of`) + `ingestion_gate.py` (`gate_date()` — the CONDITION-PRECEDENT
  filter run before any date-semantic write). An unparseable, non-empty value is
  QUARANTINED to `format_review_queue` for human review — never a corrupt or guessed date.
- Date-semantic columns: `accuracy_ledger.detection_date/breakout_date`,
  `pending_detections.detection_date`, `risk_signals.signal_date` (+ `source_time`,
  `signal_time`), `market_signal_history.signal_date` (+ `signal_time`),
  `pull_history.snapshot_date`, `score_archive.snapshot_date`, `topic_baselines.snapshot_date`.
- Parsers try WHOLE-STRING formats FIRST — NEVER naive-split on a space (the
  `'May 22, 2026' → 'May'` bug silently dropped 13 accuracy-ledger rows). NEVER
  reintroduce raw `[:10]` date slicing.
- **Purpose:** one consistent internal sort key across every source → strengthens the
  viability of the **Accuracy Ledger** (the moat). Same-surge matching now floors
  `detect_breakout_date(curve, since=detection−30d)` — fixed stale ledger matches (a
  −62d stale match became a correct −2d).
- **Guardrail (do NOT violate):** this model governs SORTING/MATCHING only. It removes
  NO scoring input — all Gradient-Score components and Market-Risk inputs (incl.
  leverage/positioning) are preserved exactly. Operational `*_at` timestamps keep their
  full instant via `to_iso_dt`. Forward-only: it gates NEW writes; it never deletes or
  rewrites existing rows (respects the 90-day retention + no-quality-delete rules).

## 15. SOURCE ROSTER + M/D PROVENANCE DIRECTION

**Trusted-direct RSS (reputable mainstream, full roster, official/direct — no
aggregators):** El País, TechCrunch, BBC News, LA Times, CNBC, The Guardian, DW, ABC
(AU+US), The Verge, InfoQ, Financial Times, The Economist, Federal Reserve, ECB,
**The New Yorker** (news + business). **Risk module:** **Nasdaq Trade Halts** (official
exchange RSS; stage-2 market-microstructure; `signal_date`=HaltDate,
`source_time`=HaltTime). Google: Blogger API (live), YouTube Data API v3
(coverage/broadcast/creators), Custom Search reviewed; Apify retained for Google Trends.

**M / D provenance reweighting — ⏳ IN DESIGN (next phase, NOT yet shipped; gated by
backtest-before-ship).** Two coupled changes to the `_news_write` provenance decision:
1. **Reputable ≠ automatic mainstream full weight.** 1 reputable source = **½ weight**;
   FULL weight only on **≥2 DISTINCT reputable sources** (keyed on distinct `source_name`
   to defeat wire-syndication). The "Belgium vs Iran, 2026 World Cup" corroboration case.
   Extends the catch-all corroboration philosophy (`CATCHALL_MIN_SOURCES ≥2`) from
   *admission* to *weight*.
2. **Research / early-signal outlets → Dark Matter (D), NOT Mainstream (M).** War on
   Rocks, Rest of World, Global Issues, Pew Research, RAND (blog), NBER — they surface
   topics BEFORE mainstream (research that reads like blogs).
   **Mechanism (mapped + anchored this session):** the D-vs-M router is **`platform_tier`**,
   NOT `is_organic`. `tier="mainstream"` feeds M (dual-pathway breadth/magnitude), lands
   in G's denominator (SUPPRESSES the early read) and raises blend weight `w`; `tier in
   {"expert","niche"}` → the Dark-Matter / expert-gradient pathway (zero mainstream
   breadth, `w`~0, G numerator). `is_organic` only scales D's quality gate; `is_first_timer`
   is D's numerator. **→ Wire these via `blog_collectors.py` GHOST_FEEDS at expert/niche
   tier** (the blog template the founder invoked), NOT via `_RSS_FEEDS`/`_news_write`
   (which forces `mainstream` and would suppress them — the exact failure to avoid).
   Feeds validated (production UA). Adversarial integrity verify + backtest still required
   before deploy.

*Last updated: 2026-06-23 — Canonical Date Auditor (Agent 16, `/monitor/datecanon`): audits the DATA by date-semantic column + live-schema `*_date` discovery, so §14 compliance is verified for ALL sources and new sources are auto-covered (closes the "gate_date is opt-in, bypasses invisible" gap that let two ledger `[:10]` slices survive — now refixed via `to_iso_date`). Prewarm Agent (15, read-path superset-cache + 100-at-a-time pagination on all list feeds). Accuracy-Ledger sweep backlog fixes (rotate oldest-checked-first + free timeouts + own cadence). Prior: 2026-06-22 — canonical date/time model (signal_date primary + source_time/signal_time secondary, ingestion_gate condition-precedent, same-surge floor); New Yorker + Nasdaq Trade Halts sources; M/D provenance reweighting IN DESIGN.*
