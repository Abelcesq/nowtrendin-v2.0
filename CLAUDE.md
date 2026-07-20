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

> **⚠ RECONCILIATION NOTE (2026-07-19, closes the standing doc-debt):** the palette below is
> the ORIGINAL v2.0 token set and is now the WEB-TERMINAL lineage only. The authorities are
> per-surface (founder ruling §12, "one brand, two dialects"): **mobile = the Aurora contract**
> (`frontend/DESIGN_SYSTEM.md` — midnight `#1B3066` ink, jewel stage colors; `#00C896`,
> `#2D7EEF`, `#E85A1E`/`#EE6A2A`, `#DC2626` are BANNED in new mobile UI); **web/desktop =
> `web-terminal/WEB_DESIGN_SYSTEM.md`** with `web-terminal/src/lib/mobileTheme.ts` as the web's
> own token authority (vivid institutional dialect + dark `*Text` twins for WCAG). Cross-platform
> parity is SEMANTIC (hue MEANINGS contractual, hue VALUES per-surface). Do not copy hexes from
> the table below into NEW mobile code; use the Aurora tokens. The table remains for the web
> lineage and for reading legacy code.

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

## 11. THEME — ⚠ SUPERSEDED FOR MOBILE (see §3 reconciliation note, 2026-07-19). The paragraph
below describes the ORIGINAL v1.0-matching light theme and survives only as the web lineage /
legacy-code reference. Mobile theme authority = the Aurora contract (`frontend/DESIGN_SYSTEM.md`:
white canvas, borderless `#F4F5F8` cards, midnight `#1B3066`/`#16264A` ink, `#B11226` accent,
jewel stage colors; `#00C896` is BANNED in new mobile UI). Web theme authority =
`web-terminal/WEB_DESIGN_SYSTEM.md`. Wordmark + flame logo rules remain in force on all surfaces.
*(Legacy text:)* light (matches v1.0). bg #F4F5F7, surface #FFFFFF (white cards w/ soft shadow),
dark text #1A1A2E. Green #00C896 = accents/active states. Wordmark: "Now" brandOrange + "TrendIn"
brandMaroon. Flame logo preserved from v1.0 — rendered via components/ui/Logo.tsx (SVG stand-in;
swap for the original logo.png in assets/ when available). StatusBar = dark-content.

## 12. WEB TERMINAL + DESKTOP (3-platform parity)
The enterprise **web terminal** (`web-terminal/`, React+Vite, Heroku app
`nowtrendin-terminal`) and the **desktop** app (`tauri-desktop/`, Tauri over the
same web build) are the institutional surfaces; the **mobile app** (`frontend/`)
is consumer/business. The trend **signal-detail** and **market-analysis** pages
present the SAME sections and data points on all three (web may add MORE — denser
filters, extra columns). **COLOR PARITY IS SEMANTIC, NOT LITERAL (founder ruling
2026-07-16/17, "one brand, two dialects"):** hue MEANINGS are contractual on every
surface — blue = Detection, green = Confidence, orange = emphasis/N, red = loss/error
ONLY (one meaning per hue family) — but hue VALUES are per-surface. Web/desktop =
the vivid institutional dialect (`web-terminal/src/lib/mobileTheme.ts` is the WEB's
own authority: Detection #2D7EEF, Confidence #00C896, orange #df7a36; dark
`*Text` twins wherever the hue is TEXT, per WCAG). Mobile = the calm jewel Aurora
dialect (`frontend/DESIGN_SYSTEM.md`). NEVER restore jewel tones to web data colors;
NEVER copy vivid hexes into mobile; the Frontend Consistency agent enforces hue
MEANING and section parity, never hex equality. Web contract:
`web-terminal/WEB_DESIGN_SYSTEM.md`. The avatar opens a full
Account view (edit profile, change password, **Authorized Users** = the Enterprise
5-seat / 100,000 shared-token entitlement, admin identified). Parity is enforced by
the **Frontend Consistency** agent (`/frontend-consistency`).

## 13. DATA-QUALITY + MONITORING (the engine guardrails)

> **DATA RETENTION RULE (hard — do not override):** All `velocity_scores` rows
> are retained for **365 days** (canonical; extended from 90 on 2026-06-24, founder
> decision — a full year of history strengthens trend tracking + the accuracy ledger).
> Never delete scored data within this window — historical scores are required for
> trend tracking, calibration, and accuracy-ledger validation. Only rows older than
> 365 days are removed by `_prune_velocity_scores()` (default 365; env
> `VELOCITY_RETENTION_DAYS`/`VELOCITY_KEEP_DAYS`). Do NOT change this to a count-based
> prune; count-based deletes valid history for frequently-scored topics. Do NOT add any
> function that deletes `velocity_scores` rows based on quality judgements
> (e.g., corroboration level) — the floor is enforced at SCORING time so that
> new bad data never enters; old data stays for the full retention window.

- **Catch-all corroboration floor** (`CATCHALL_MIN_SOURCES`, default 2): a topic
  classifying into news/general must have ≥2 distinct sources to score, with hard
  exemptions (expert-tier signal, high magnitude, ledger/pending). De-congests the
  catch-all without losing early signals. NOT a raw post-volume floor (that would
  break the before-it-arrives thesis). Floor applied at SCORING time only (forward-
  only); historical rows within the 365-day window are never retroactively deleted.
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
- **Content category routing (display-only, no score impact, non-circular).** `'news'`
  has NO lexicon — real news/geopolitics is `current_events`; `'news'` was ONLY the
  classifier's no-match fallback, so the 77% "news" catch-all was 77% UNCLASSIFIED,
  mislabeled. Fallback now → honest **`'general'`**. Serve-time category =
  `_category_for(topic_key, display)`, layered strongest-first: **situation (event
  co-occurrence) → context (the topic's own `raw_signals.title` headlines, 0.35 conf
  floor) → bare lexicon → general**. Both override maps are background-refreshed,
  held-out (built FROM scored signals, NEVER fed back into the score). Live served
  catch-all: 70.2% over the 6000-topic working set (2026-07-06; the earlier 77%→56%
  drain figure predates the World Cup surge). MEASUREMENT RULE (2026-07-06): the
  catch-all AUDITORS measure with the SERVE-TIME `_category_for`, never the bare
  lexicon — the bare read over-counts (the phantom 80.5%-vs-served-70.2% gap).
  NEVER wire `_category_for` into scoring admission
  (`_passes_corroboration`) or the score — that would be circular.
- **Stage from Detection** (`stageOf`) everywhere; `Now TrendIn` view ranks by the
  proprietary **N** (`nowtrendin_score`), `All Signals` by Detection.
- **9 monitoring agents** (`monitoring_agents.py` → `/monitor` `run_all`): Source Watchdog,
  Scorer Watchdog, Pipeline Integrity, Topic Quality Auditor, Catch-All Auditor (daily EOD),
  Cost Sentinel, Data Subscriptions, Calibration Auditor, **Canonical Date Auditor** (B3a —
  `/monitor/datecanon`; audits every date-semantic + discovered `*_date` column so §14
  compliance is verified for ALL sources, new ones auto-covered). Plus the **Prewarm Agent**
  (operational, read-only, API-process `/prewarm` — keeps every list-feed superset cache hot;
  PULL-SYNCHRONIZED: fires `PREWARM_AFTER_PULL_S` = 60s after EVERY data pull completes, with
  the 25-min loop as TTL safety net; warms are overlap-guarded).
  Full specs: `AGENT_CHARTER.md` (Agents 1–16) + `DATA_BUILDING_BLOCKS.md`.
- **BATCH-PACED PIPELINE (founder rule, 2026-07-06 — heavy phases must never clog the serve
  path).** The whole pipeline breathes between units of heavy work so the DB pool + serve path
  stay responsive: collectors pause `COLLECT_SOURCE_PAUSE_S` (10s) between sources; the scorer
  scores in batches of `SCORE_BATCH_SIZE` (100) with `SCORE_BATCH_PAUSE_S` (10s) between
  batches; prewarm pauses `PREWARM_FEED_PAUSE_S` (10s) between its 7 feed builds. Superset
  builds are additionally **SINGLE-FLIGHT** (`_get_or_build`): one builder per cache key —
  concurrent requests wait for its result or get an honest 503 "warming", never a second
  build (the 2026-07-06 thundering-herd lesson). All in
  `transfer/gravitational_anomaly_detector.py`; env-tunable, defaults live (no overrides set).

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
- **Quarantine REVIEW LOOP (closed 2026-06-24):** before quarantining, `gate_date()`
  consults `format_rules` — a human decision saved via `resolve_review()` auto-applies to
  identical future inputs. Review via `GET /quarantine/dates` (pending + candidate
  normalizations); resolve via `POST /quarantine/dates/resolve {id, chosen_value}` (validated
  canonical; learns a rule). Flag-never-force — nothing changes until a human posts.
- Date-semantic columns: `accuracy_ledger.detection_date/breakout_date`,
  `pending_detections.detection_date`, `risk_signals.signal_date` (+ `source_time`,
  `signal_time`), `market_signal_history.signal_date` (+ `signal_time`),
  `pull_history.snapshot_date`, `score_archive.snapshot_date`, `topic_baselines.snapshot_date`,
  `market_accuracy_ledger.detection_date/move_date`, `market_pending_detections
  .detection_date`, `crypto_accuracy_ledger.detection_date/move_date`,
  `crypto_pending_detections.detection_date` (market/crypto ledgers registered 2026-07-06
  after B3a auto-discovery; writers canonicalize via `to_iso_date`). The three
  `*_pending_detections.timeout_date` columns are OPERATIONAL INSTANTS (full ISO datetime,
  `now > _parse(...)` deadline checks) — on the auditor's operational allowlist, not canonical.
- Parsers try WHOLE-STRING formats FIRST — NEVER naive-split on a space (the
  `'May 22, 2026' → 'May'` bug silently dropped 13 accuracy-ledger rows). NEVER
  reintroduce raw `[:10]` date slicing.
- **Purpose:** one consistent internal sort key across every source → strengthens the
  viability of the **Accuracy Ledger** (the moat). Same-surge matching now floors
  `detect_breakout_date(curve, since=detection−30d)` — fixed stale ledger matches (a
  −62d stale match became a correct −2d).
- **PATIENCE WINDOW (365d, hard rule — 2026-06-27).** A pending detection gets a FULL YEAR for human
  attention to reach Google before it is judged a miss: `LEDGER_TIMEOUT_DAYS=365` (computed LIVE from
  `detection_date`, so it applies to the existing pending pool too, not just new rows). The lead
  window is **ASYMMETRIC**: the backward stale-match floor stays tight (`MATCH_WINDOW_DAYS=30` — a
  breakout >30d BEFORE detection is a different, older surge, the −92d artifact), but a FORWARD lead
  up to `LEAD_MAX_DAYS=365` now counts as a genuine **LED** win (early dark-matter detection confirmed
  by a LATER Google breakout — no longer wrongly excluded as LATE_REDETECTION). The sweep fetches a
  Trends curve spanning detection→now so a months-later breakout is visible. **Rationale:** the
  product detects attention BEFORE Google, so we must be FAIR to our own system — never conclude the
  agents failed by removing data before human attention had a real chance to arrive ("the big money
  is in the waiting" — Munger). Held-out — measurement only, NO score impact. NEVER shorten without
  founder sign-off + a denominator backtest. Aligns with the 365-day retention (§13). `param_version`
  → `calib-params-v2-patience365`.
- **LEDGER ENROLLMENT + PRE-BROKEN SPLIT (2026-07-07, measurement-only).** Enrollment is
  FIRST-CROSSING: `_record_top_detections` enrolls topics first-seen within
  `LEDGER_ENROLL_RECENT_DAYS` (14) that cross the floor, excluding ESTABLISHED/MONITORING
  maturity — NOT the leaderboard top-N (already-big topics Google broke out on →
  structurally LAGGED; the old query measured coverage latency, not the thesis). Report
  splits LAGGED at report-time only: near-miss (race run and lost) vs **pre_broken**
  (breakout > `LEDGER_PRE_BROKEN_DAYS`=7 before first sighting — cold-start, never a race);
  `tracked_race_hit_rate_pct` = LED over races actually run. Blended honest rate still
  counts everything; no stored rows changed. First read: blended 10% → tracked-race 26.9%
  (44 of 59 lagged were pre-broken cold-start rows).
- **Guardrail (do NOT violate):** this model governs SORTING/MATCHING only. It removes
  NO scoring input — all Gradient-Score components and Market-Risk inputs (incl.
  leverage/positioning) are preserved exactly. Operational `*_at` timestamps keep their
  full instant via `to_iso_dt`. Forward-only: it gates NEW writes; it never deletes or
  rewrites existing rows (respects the 365-day retention + no-quality-delete rules).

## 15. SOURCE ROSTER + M/D PROVENANCE DIRECTION

**Trusted-direct RSS (reputable mainstream, full roster, official/direct — no
aggregators):** El País, TechCrunch, BBC News, LA Times, CNBC, The Guardian, DW, ABC
(AU+US), The Verge, InfoQ, Financial Times, The Economist, Federal Reserve, ECB,
**The New Yorker** (news + business). **Risk module:** **Nasdaq Trade Halts** (official
exchange RSS; stage-2 market-microstructure; `signal_date`=HaltDate,
`source_time`=HaltTime). Google: Blogger API (live), YouTube Data API v3
(coverage/broadcast/creators), Custom Search reviewed; Apify retained for Google Trends.

**Market/risk + insider sources (this week):** **Finviz Elite** ($30/mo, `finviz_data.py`) = **PRIMARY
insider Form-4** (uncapped market-wide feed) + equity screener; **FMP** ($20 Starter, prices/fundamentals +
**crypto coin prices**); **QuiverQuant** ($30, congress → Dark Matter); **Databento** (metered ~$0, ledger
price-verify + microstructure). Finviz crypto is display-only → FMP serves crypto prices.

**✅ SHIPPED 2026-06-26 — Finviz primary insider + Market-Signal "insider" reframe + Mainstream v2.**
- **Finviz = PRIMARY insider** (`FINVIZ_INSIDER=1`, `av_dark_positioning._best_insider` → Finviz, AV fallback).
  INTEGRITY FIX: insider NET is degenerate (≈always sell-dominated) → the signal is insider **BUYING**
  (`signal=='accumulation'`, ≥$250K); routine selling is neutral, NOT bearish (applied across finviz_data /
  av_dark_positioning / crypto_signals / positioning_intel).
- **Market Signal de-Congress → "insider."** All user-facing "Congress" generalized to **insider tracking**
  (interpretation `_market_analysis`, `ai_grade` prompt, explainer, Methodology, `_interpret_movement`). Labels:
  "Positioning Concentration" → **Insider Tracking**; "Dark Positioning" (macro funding/OFR) → **Macro
  Positioning** (accurate — NOT insider); Diffusion "Dark Positioning" stage label → Insider Tracking. Tier
  **BUILDING → MODERATE** (engine + web + mobile). SOURCES accuracy: now ADDS the score-driving FINRA/OFR/FMP/13F
  that `source_provenance` (signals-only) omitted (§17). De-Congress means the DISPLAY only — congress trade
  DATA (Quiver) is still a Dark-Matter input, just not named to the user.
- **Mainstream v2 (`MAINSTREAM_V2=1`, LIVE)** — credible media is a Dark-Matter **TRIGGER** until **≥5 INDEPENDENT
  outlets** corroborate (syndication-collapsed `min(distinct outlets, distinct titles)`) OR magnitude spikes →
  `mainstream_confirmed`. FIFA validated: "world cup" stays mainstream (134 outlets), thin-credible "mexico world
  cup" (5→4 stories) demotes to a dark-matter trigger (det 38.5→70). The ½/full weight reweighting below is the
  related, still-in-design refinement.

**M / D provenance reweighting — part 2 BUILT (2026-07-07, flag-gated OFF awaiting founder flip);
part 1 still in design.** Two coupled changes:
1. **Reputable ≠ automatic mainstream full weight.** 1 reputable source = **½ weight**;
   FULL weight only on **≥2 DISTINCT reputable sources** (keyed on distinct `source_name`
   to defeat wire-syndication). The "Belgium vs Iran, 2026 World Cup" corroboration case.
   Extends the catch-all corroboration philosophy (`CATCHALL_MIN_SOURCES ≥2`) from
   *admission* to *weight*.
2. **Research / early-signal outlets → Dark Matter (D), NOT Mainstream (M) — ✅ LIVE
   2026-07-15 (founder-ordered flip), flag `GHOST_RESEARCH_FEEDS=1` on the engine.**
   Pre-flip adversarial re-verify on live titles caught + fixed 3 extractor defects
   (curly-apostrophe contractions anchoring junk; RAND "Q&amp;A with <staff>" titles
   extracting staff names — the NBER failure mode; inflected common words passing the
   dictionary test). Title-Case style pairs now reduce to their real entity
   ("Breaking America"→america); sentence-case proper-noun pairs ("the Shin Bet") are
   never mutilated. Confirmed collecting live (WoR/RoW/GI/RAND through
   `research_entity_topics` at expert tier). **Monitored two-week trial** per the
   validation doc: watch topic-quality + catch-all auditors (fragment count,
   single-source leak) + ghost collector counts; roll back by unsetting the flag.
   Original build 2026-07-07: `audits/source-onboarding/RESEARCH_FEEDS_VALIDATION_2026-07-07.md`. §16 five-gate
   verdicts: **War on Rocks / Rest of World / Global Issues / RAND PASS** via the new
   ENTITY-ANCHORED extractor (`blog_collectors.research_entity_topics`,
   `mode="research_entity"` — required because the generic n-gram extractor FAILED the
   FORMAT gate on editorial titles and expert-tier signals bypass the corroboration
   floor); **NBER FAILED (2nd time — author-name topics + undated items)**; **Pew FAILED
   as-is (report sub-pages pollute the feed)**. Premise test: 51/59 extracted topics were
   NOVEL to the system. They surface topics BEFORE mainstream (research that reads like blogs).
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

## 16. SOURCE ONBOARDING PROTOCOL (hard rule — no source is linked until ALL 5 gates pass)

> **Before linking ANY new media/data source** (RSS, API, feed, collector) you MUST clear all
> five gates below, IN ORDER. No exceptions. This is the codified lesson of three failures caught
> in onboarding: **yahoo_finance** (HTTP 429 every cycle — access gate), **Mises Literature**
> (HTTP 404 + classic *literature*, not current signal — currency/type gate), **NBER** (academic
> titles extract to noise like "times geopolitical fragmentation" — format gate). Enforced by the
> `.githooks/commit-msg` gotcha, which blocks a source-shaped commit until the message asserts
> `[source-onboarded]`.

1. **TYPE** — Identify what the source actually provides and classify it: *attention/trend
   signal · market positioning · risk/microstructure · reference/research*. Macro-research ≠
   positioning data.
2. **ENGINE** — State the EXACT pipeline it will feed and confirm it's the right one. A source
   feeds exactly ONE primary engine:
   - Trend / Gradient Score → `news_collectors` (mainstream **M**) · `blog_collectors.GHOST_FEEDS`
     (expert/niche → Dark Matter **D**) · `discovery_collectors`.
   - Market Signal / risk positioning → `financial_risk_gradient` (SEC/FINRA/WhaleWisdom/OFR).
   - Held-out referee → never feeds the score (e.g., `referee_wikipedia`).
3. **FORMAT** — Confirm the data structures to OUR formatting systems BEFORE wiring: dates pass
   `gate_date()` → canonical `signal_date` (§14); topic text extracts to CLEAN topics through
   `_is_quality_topic` + the extractor (no academic-title fragments / boilerplate); a provenance
   tier is assignable (mainstream/expert/niche).
4. **CURRENCY + ACCESS** — Confirm BOTH: **current** (fresh, dated items — not stale/archival) AND
   **regular access** (stable URL, HTTP 200, no 404/429/auth-block, declared UA where required,
   rate-limit headroom).
5. **TEST → LINK → DEPLOY** — TEST FIRST on a LIVE sample (run real items through the gate +
   extractor + classifier and eyeball the output), THEN wire it, THEN deploy. A **score-affecting**
   source ADDITIONALLY requires **backtest-before-ship**: build it held-out, research the output,
   review, and only then integrate into any score.

### 16a. COLD-START POSTURE (hard rule — 2026-07-19, D8 board; Expansionist)
> The degenerate/zero-baseline class is not a bug coverage cures — it is the **permanent
> frontier of expansion**: every new instrument, coin, region, or asset class enters the
> universe with a zero-variance baseline and lives in the degenerate class until its own
> history accumulates. So a codified cold-start posture is required, not a per-batch patch.

Any universe expansion (new instruments / asset classes / regions) MUST state its
degenerate-window handling, and it follows this fixed progression, never skipping a stage:
1. **CALIBRATING** — under `MIN_BASELINE_TRUSTWORTHY` cycles: the component reads on the
   absolute scale, stamped `calibrating`; the overall tier reads "baseline forming", never a
   confident tier the data can't support.
2. **HONEST ABSENCE (display, §17/D7)** — a zero-variance/constant baseline (`stdev` at floor
   AND `current == mean`) is `degenerate_baseline` → served `score: null, absent: true`, never
   a numeric floor value wearing the measured badge (the "30 ✓" defect). The composite still
   counts it at the neutral baseline BUT discloses it (`composite_note`, E1) — display-only.
3. **SCORE-SIDE EXCLUSION (gated, D8)** — excluding degenerate components from the *composite*
   is SCORE_AFFECTING and stays deferred behind its written triggers (`audits/DEFERRED_ITEMS.md`)
   until coverage growth makes exclusion bind on DATA rather than absence
   (`/monitor/degenerate-census` is the tripwire). Never skip stages 1–2 to reach 3.

The interim, diligence-defensible truth on an insufficient-coverage instrument is: the score
is baseline-floor-informed and the display SAYS SO — never a fabricated read, never a silent 30.

## 17. SOURCE-DISPLAY RULE (detail sections — trend + market, ALL platforms)

> **Hard rule:** a topic's detail view shows ONLY the sources, coverage, and components that
> actually CONTRIBUTE to that topic's score or research. A data source that returns no data for
> the topic — isn't covering it, has 0 items, or is N/A for it — is **OMITTED**, never rendered as
> empty, "not in recent uploads", "0 articles", "no coverage across N channels", or **NaN**.

- Applies to BOTH the **trend signal detail** and the **market signal detail**, on **all three
  platforms** (web terminal · desktop · mobile). Parity enforced by the **Frontend Consistency**
  agent (`/frontend-consistency`).
- **Why:** showing a non-contributing source implies it informed the read when it did not — noise
  that misrepresents what supports the score. Integrity: only reference what contributes
  ([[feedback-integrity-standard]]).
- **Mechanics:** gate each source/coverage sub-block on real content for the topic (covered creators
  only; news only when `article_count > 0`; broadcast only when `channels > 0`; positioning/
  fundamentals only when present). A section with no contributing sub-blocks is not rendered.
  Component breakdowns render a real value or an explicit **"n/a"** — NEVER `NaN` (read the
  component's `.score`, never `Number()` the component object).
- **Canonical example of what this forbids:** the web "Score Components" panel (removed 2026-06-25)
  duplicated "Market Factors" and rendered `NaN`; and creator-coverage rows that listed finance
  YouTubers as "not in recent uploads" for a topic they weren't covering.

*Last updated: 2026-07-11 — **Catch-all warm/cold refresh: writer-guard + warm-on-boot snapshot (Board-ruled).**
Two advisory-board reviews (audits/board/BOARD_catchall-eod_2026-07-10.md + BOARD_warm-cold-refresh_2026-07-10.md).
**Root finding (code-inventoried):** the serve-time category `_category_for` reads two IN-MEMORY maps
(`_SITUATION_CAT`/`_CONTEXT_CAT`) that reset EMPTY on every process restart and rebuild via a background daemon
(context ~4-5 min post-boot, ~69k entries); while cold it falls to the bare lexicon and the catch-all metric reads
~68% vs the warm ~33% (a deploy swung the auditor 33.6→68.5→33.4 in an hour). **SCORING + all 3 LEDGERS are
INSULATED** — `/scores` serves stored `serve_payload`, stale rows serve stored verbatim (INV-1), the scoring-admission
gate uses the STATELESS import-time lexicon (`_topic_category`, NOT `_category_for`), ledgers are DB-driven/restart-safe;
the confound is DISPLAY category + the catch-all monitoring metric only. **Fixes shipped (v231/v232):** (a) **WRITER-GUARD**
— `catchall_auditor` skips the `catchall_floor_log` write + suppresses the WORSENING/leak alarms when the context map is
cold (<`CATCHALL_WARM_CTX_MIN`=5000); `fragment_category_auditor` suppresses its ≥70% alarm cold — a cold reading no
longer poisons the trajectory or fires a false floor-integrity alarm. (b) **WARM-ON-BOOT SNAPSHOT** (`CATEGORY_SNAPSHOT`=1):
each live `_refresh_*` persists its map to the new `category_override_snapshot` table; startup loads it SYNCHRONOUSLY
before serving, so `_category_for` is warm-on-boot (no ~5-min / ~2100-topic "General" flicker) and consistent across a
dyno fleet (all load the same DB snapshot). DISPLAY-ONLY, never wired into scoring. (c) **OLD-vs-CURRENT provenance**:
`_CAT_MAP_META` stamps each map `source` (empty|snapshot|live) + `refreshed_at`, surfaced in `override_maps` + the auditor
summary + the new **`/monitor/catmaps`** fast status endpoint (used because `/monitor/catchall` + `/monitor/catchall/attribution`
H12 under load). Board **rejected** a readiness-gate (wedged-prewarm outage class) and **cut** prewarm-sync (daemon already
refreshes on boot). Also shipped `broadcom→technology` in `_LEX` + `/monitor/catchall/attribution` (frozen-panel decomposer):
the 70→34 catch-all drop was **classifier maturation** (07-06→07-07, pre the 07-08 flips), not the junk purge. **RULE:** never
publish the catch-all % externally as an accuracy KPI (warmth/denominator/cycle-phase sensitive) — it is a congestion gauge,
demoted below the accuracy ledger. RESOLVED (v233, founder-ruled restore+tighten): `?clean_poisoned=1` had over-deleted a probably-legitimate 2026-07-06
trajectory row — it was restored (idempotent, NULL for the 2 unrecovered sub-fields, not fabricated) and the cleanup FLOOR
was tightened 2026-07-06 → 2026-07-09 (warm there is ~33-35%, so ≥60% is unambiguously a cold-boot artifact).
Prior: 2026-07-07 — **Ledger truth + match validity + 3-platform ledger UI + hardening sweep.**
(1) **LEDGER FIRST-CROSSING ENROLLMENT + PRE-BROKEN SPLIT** (§14; measurement-only): enrollment now
takes fresh floor-crossers (first-seen ≤ `LEDGER_ENROLL_RECENT_DAYS`=14, ESTABLISHED/MONITORING excluded),
NOT the leaderboard top-N (structurally LAGGED). Report splits LAGGED near-miss vs **pre_broken** (breakout
>7d before first sighting — never a race); `tracked_race_hit_rate_pct` = LED over races run. First read:
blended 10% → **tracked-race 26.9%** (44/59 lagged were pre-broken cold-start rows). (2) **MATCH VALIDITY**:
every sweep resolution records `sweep_query` + `query_ambiguous` (single word / bare geo = weak Trends match);
LED/SAME_DAY wins get an INDEPENDENT **Wikipedia-pageviews referee** (±14d of breakout; fail-open; old wins
honestly "unchecked"). (3) **Accuracy Ledger UI on all 3 platforms**: web chips (Lagged·near / Pre-broken) +
tracked-race + referee cards; mobile got LEDGER mode chips + verdict filter chips + a filterable row list
(server-computed pre_broken — ONE grace definition); **click/tap a row → Ledger Entry Analysis panel**
(`POST /analysis/ledger`, deterministic signal_analysis kind='ledger': method-of-tracking + verdict meaning +
match validity, formula-confidential). (4) **Hardening**: grade `_num` clamps AI numerics to [0,100]; N detail
(queries 30d/24h/rate) recomputed at detail-serve from topic_queries (the "No internal query history yet" at
N=100 bug); last two silent apply_calibration swallows now log + stamp `calibration_errors`. (5) **Feature
mining** (read-only, audits/ledger-research/): D=0 at first sighting for winners AND near-misses but 40 for
pre-broken → current Dark Matter is LATE-confirmation, not early-warning — empirical case for the §15
GHOST_FEEDS expansion; LED median M=80 vs near-lag 50 (breadth-at-first-sighting separates winners); 5/15
near-misses lost by 1–2 days (fast-lane recheck flips them). (6) **Founder-approved DISCLAIMER (verbatim,
sign-off to edit)** on all platforms, panels top AND bottom: "*All information contained herein may not be
accurate including any and all figures indicated in this section and or site and may be an approximation and
should not be construed as financial, investment, or legal advice." (7) **Ops**: GITHUB_TOKEN rotated (classic
no-scope no-expiry; collector HEALTHY 6132 signals) + 401-fallback in collect_github; monitor fixes verified
(datecanon ok — market/crypto ledger date cols registered, timeout_date = operational allowlist; calibration
auditor reads real denominators 70/821); Cost Sentinel back under cap $497.89/$700. ⚠ **Anthropic API account
credits EXHAUSTED** (400 "credit balance too low" on every call) — AI Context definitions + Grade Claude stage
DOWN until credits purchased at console.anthropic.com (cached explainers still serve).
Prior: 2026-07-06 — **Catch-all fixed + Apify clock-slot rule + true costs + INV-1 serve-consistency +
self-healing DB pool + mobile parity (audit #3).** (1) **/monitor/catchall FIXED** (was 503/H12): the auditors
measured the bare lexicon while users see the layered `_category_for` — both catch-all auditors now use the
SERVE-TIME classifier (true served catch-all **70.2%**, not the phantom 80.5%); scan bounded to the recent
working set (`CATCHALL_WORKING_SET`=6000); corroboration reads via explicit-key chunks (index seeks, no
full-table scan). Lexicon drained per the Agent-6 worklist (WC-2026 cluster worldcup/mundial/golden boot/
haaland/balogun/vozinha; khamenei/ayatollah; america250/250th birthday/july 4th/mount rushmore; mamdani/
mcconnell; walmart/costco; zendaya/victor willis; youtube/whatsapp) — policy held: bare countries/kelce/visa
stay OUT (situation layer routes). (2) **APIFY CLOCK-SLOT RULE (hard):** ALL paid Apify pulls fire ONLY at the
4 daily 6h slots (00/06/12/18 UTC family) or on explicit user request — the ledger sweep moved
interval+boot-fire → **cron :45** (a paid sweep fired on EVERY deploy/dyno-cycle before); `_fetch_apify` now
passes `&timeout=&memory=` ON the actor run + ABORTS on poll-budget expiry (the 10-min 0-result runs were the
~$93/mo compute line). Realtime confirmed clean 4×/day :30; trudax runs were pre-rotation one-offs (console
Schedules clean). Recommend Scale→Starter downgrade once usage drop confirms (~$100-150/mo). (3) **True
Heroku cost**: `COST_HEROKU_USD` 64→**112** (engine Std-2X $50 + essential-1 $9; backend $12; preview/terminal/
web Basic ×3; **frozen-1.0 essential-2 $20 unused — archive+delete candidate**; nowtrendin-web mirror
redundancy candidate). Cost Sentinel now honestly **CRITICAL $718.82 > $700** — the old $64 masked it; Apify
fixes restore headroom next period. (4) **INV-1 serve-consistency FIX**: /scores re-ran live calibration
(incl. the AI floor) on payload-less STALE rows, inflating stored 35.6→served 100 ("coding agent" ranked #1
on mobile 4 days stale while web showed it mid-pack) — rows older than `SERVE_LIVECAL_MAX_AGE_H` (48h) now
serve STORED values exactly like /topics. One score per topic, everywhere. (5) **Self-healing PG pool**
(db_compat, 12/12 behavior-tested): psycopg2's pool has NO reclamation — dead conns handed out + orphaned
checkouts = permanently leaked slots (the 07-06 /scores outage: PoolError with the server at 2/20). Now:
SELECT-1 checkout probe, broken-conn discard, bounded DIRECT fallback (`PG_DIRECT_MAX`=4, reads keep serving
while exhausted), auto pool-REBUILD after 90s persistent exhaustion (closes ALL old conns — server usage
bounded ≤ pool+direct), `OperationalError`-on-growth retried; try/finally on the hottest builders;
**`PG_POOL_MAX`=8** (deliberate headroom — engine ≤12 of the 20-conn cap; raising it to 12 eroded the margin
and let the server brush the cap). NEVER `pg:killall` while dynos run — it poisons every pooled conn. THIRD
outage phase found: the prewarm thread WEDGED 6.3h inside one build against the saturated server → no cache
ever warmed → every client request cold-built (self-sustaining churn); a wedged prewarm is detected by
`/prewarm` `last_run` age. Full triage/recovery runbook = the new **`/engine-recovery`** skill (signature
table + safe sequence: scale-0 → killall → scale-1; never probe /scores repeatedly — poll /prewarm).
Recommended next (founder-confirmed deploy): a pipeline_integrity read-path alarm on cache-absent +
prewarm-stale. (6) **Mobile parity
(all deployed to nowtrendin-v2-preview)**: TRENDS signal-stage chip row restored (Now TrendIn/All Signals/
Breakout≥85/Strong≥70/Indicating/Marginal/Anomalies — combines with CATEGORY like the web); per-row category
chip on TrendCard; **Accuracy Ledger zeros fixed** (mobile mapped extinct snake_case fields; engine serves
camelCase — now camelCase-first with fallbacks; "PREDICTIONS"→"RESOLVED" + a pending-in-flight line, honest
denominators). (7) Weekly improve-system audit #3 committed (`audits/improve-system/`). ⚠ NOTE: mobile design
is now the **Aurora contract** (`frontend/DESIGN_SYSTEM.md` — midnight #1B3066, #00C896 BANNED in new mobile
UI); §3/§11 palettes predate it and pend reconciliation.
Prior: 2026-06-26 (evening) — **Per-item Signal Analysis + accuracy-ledger maturity segmentation + Apify
usage audit + token rotation.** (1) **Signal Analysis** — held-out `signal_analysis.py` + `POST /analysis/{kind}`:
a reproducible, formula-CONFIDENTIAL, measurement-only narrative per item (explains each metric + analyzes the
finding vs the accuracy-ledger track record, honest denominators). LIVE on web (trend/market/crypto rails) + mobile
(trend `signal/[id]` + market `risk/[key]`; crypto N/A — no mobile crypto screen); desktop inherits via the web build.
Founder enterprise standard: explain the metric, HIDE the formula, every claim data-supported + defensible to hedge-fund
counsel. (2) **The accuracy ledger is HELD-OUT** — `calibration_engine`/`signal_calibration_integration` have ZERO
ledger refs, `calibration_agent` is read-only → the sweep cap NEVER affects a score. The 909-pending / 2.1% *blended*
rate is an ARTIFACT (throughput starvation + survivorship bias + ESTABLISHED-topic pollution). `generate_honest_report`
is now MATURITY-SEGMENTED (`topic_maturity.maturity_class` + a `velocity_scores` sustained-days fallback) → headline =
the EMERGING early-detection cohort (`/accuracy/ledger` `byMaturity`/`earlyDetectionHitRate`); all cohorts reported.
(3) **Sweep runaway fixed** — the `google-trends-scraper` actor is COMPUTE-expensive per run (1–11 min, some fail; the
"$0.001/result" read was wrong). Keep `LEDGER_SWEEP_LIMIT=8` (code default reverted 300→8; `0`=uncapped footgun),
`_apify_sweep_budget_ok` guard (skips paid fetches within `LEDGER_APIFY_RESERVE_USD`=40 of the Apify cap), manual
`POST /accuracy/ledger/sweep`. (4) **Apify = TREND/ATTENTION-ONLY** (Google Trends realtime+sweep + Reddit; crypto +
financial have ZERO Apify refs — FMP/Finviz/AV/FINRA/OFR/Databento). Realtime 2× overrun (actor fires :00 AND :30 vs
the single :30 cron — a 2nd process on the old token). `APIFY_TOKEN` rotated (was leaked in a tool output → old
deleted) → new set on engine; confirmed **NON-EXPIRING** (2026-06-26) — trend pipeline safe. (5) **Cost Sentinel $700/mo total cap** (critical if exceeded, warn at 80%). (6) **Accuracy-ledger
PATIENCE WINDOW (365d)** — `LEDGER_TIMEOUT_DAYS` 90→365 (computed LIVE from detection → applies to the
existing ~881 pending) + ASYMMETRIC lead window (backward stale-floor stays 30d; FORWARD lead up to
`LEAD_MAX_DAYS`=365 now a genuine LED win, was excluded as LATE_REDETECTION) + dynamic curve span
detection→now. The product detects attention BEFORE Google, so be FAIR to our own system — never judge a
detection a miss before human attention can arrive ("the big money is in the waiting" — Munger). Held-out
(no score impact); `param_version=calib-params-v2-patience365`; aligns with the §13 365-day retention. The
881 pending is a ROLLING working set (resolves at a Google breakout or the 365-day timeout), NOT a
throughput problem. Full rule in §14.
Prior: 2026-06-26 — **Finviz primary insider + Market-Signal "insider" reframe + Mainstream v2 +
the Crypto Money Gradient** (see §15). (1) **Finviz Elite** = PRIMARY insider Form-4 (uncapped; `FINVIZ_INSIDER=1`),
AV→fallback; integrity fix = insider **BUYING** is the signal (net is sell-dominated/degenerate). (2) **Market
Signal de-Congress**: user-facing "Congress" → "insider tracking" everywhere (text/AI prompt/explainer/Methodology);
"Positioning Concentration"→**Insider Tracking**, "Dark Positioning"→**Macro Positioning**; tier **BUILDING→MODERATE**
(all platforms); SOURCES now add the score-driving FINRA/OFR/FMP/13F (§17). (3) **Mainstream v2** (`MAINSTREAM_V2=1`,
LIVE): credible media is a Dark-Matter TRIGGER until ≥5 INDEPENDENT outlets corroborate (syndication-collapsed) or
magnitude spikes — FIFA-validated. (4) **Crypto Money Gradient LIVE** (`CRYPTO_SIGNAL=1`): 12 coins (BTC/ETH/SOL/XRP/
BNB/DOGE/ADA/AVAX/LINK/DOT/LTC/BCH), proxy-based Dark Matter (D, crypto-exposure 13F/insider via Finviz) + FMP coin
price (M); master/detail `/crypto` page + nav (under Market Signal, above Grade) + Dashboard tile; **served from the
prewarm cache** (live compute uses FAST Finviz-only DM — AV 13F too slow; `CRYPTO_FULL_DM=1` for research); its OWN
**crypto accuracy ledger** (realized COIN price direction) — the 3rd distinct ledger. (5) New paid sources tracked:
Finviz $30 + QuiverQuant $30 + FMP $20 Starter + Databento (metered); the Data Subscriptions + Cost Sentinel agents
now register them. Health check clean: services up, 0 quarantine, ledgers forward-only, catch-all STABLE.
Prior: 2026-06-25 — **§17 SOURCE-DISPLAY RULE** added (detail views show ONLY contributing
sources/components; omit no-data sources, never show empty/"not in uploads"/NaN — trend + market,
all platforms). Removed the web "Score Components" NaN panel (duplicated Market Factors) + the
non-covering creator rows. **Market Signal v2.0 (Money Gradient) is LIVE** (`MARKET_SIGNAL_V2=1`,
validated): Money Movement / Market Confirmation + factual flow + leverage facts across all
platforms; a SEPARATE **market accuracy ledger** validated by realized EOD price direction (FMP),
distinct from the Trends ledger (Google Trends); see `MARKET_SIGNAL_V2.md`. **N component** copy
corrected — N is **platform tracking** (how often a topic is triggered/surfaced as a tracked topic),
NOT "user demand"; "Community Demand" → "Platform Indicator". Prior: 2026-06-24 — **§16 SOURCE ONBOARDING PROTOCOL** added (hard 5-gate rule before
linking ANY source: TYPE → ENGINE → FORMAT → CURRENCY+ACCESS → TEST→LINK→DEPLOY; enforced by the
`.githooks/commit-msg` gotcha). Source cleanup: HackerNews fixed (algolia `/search`→`/search_by_date`),
yahoo_finance removed (429/dead), QA runbook (`monitoring/integrity-check.ps1`) repointed 1.0→v2.
SEC fund-13F being built held-out (research-before-integrate). Retention extended to **365 days** canonical (§13; founder decision — ⚠ ~4× storage, exceeds the 10GB plan, needs a larger Postgres tier as the tail fills). **Overbroad "news" fixed** (§13): the no-match fallback was 'news' but 'news' has no lexicon — now → honest 'general'; added headline-context classification (`_category_for` layers situation→context→lexicon→general), live catch-all 77%→56%, display-only/non-circular. **Quarantine review loop closed** (§14): `gate_date` consults `format_rules` + new `GET/POST /quarantine/dates[/resolve]`. Market Signal **coverage lanes** (Tier 1) covered/halted-microcap/macro (macro themes drop positioning+fundamentals as N/A). Guardian + Reddit keys deliberately deferred (proceeding without). Fixed `/categories` 500 (missing topic_key in SELECT, regression since v133). Prior: 2026-06-23 — Canonical Date Auditor (Agent 16, `/monitor/datecanon`): audits the DATA by date-semantic column + live-schema `*_date` discovery, so §14 compliance is verified for ALL sources and new sources are auto-covered (closes the "gate_date is opt-in, bypasses invisible" gap that let two ledger `[:10]` slices survive — now refixed via `to_iso_date`). Prewarm Agent (15, read-path superset-cache + 100-at-a-time pagination on all list feeds). Accuracy-Ledger sweep backlog fixes (rotate oldest-checked-first + free timeouts + own cadence). Prior: 2026-06-22 — canonical date/time model (signal_date primary + source_time/signal_time secondary, ingestion_gate condition-precedent, same-surge floor); New Yorker + Nasdaq Trade Halts sources; M/D provenance reweighting IN DESIGN.*
