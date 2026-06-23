# NowTrendIn 2.0 — Session Log

A running, readable catch-up of what's been built and what's open — so any new
Claude Code session (or you on your phone) can resume without the local thread.

_Last updated: 2026-06-23_

---

## Session 2026-06-23 — Read-path performance: Prewarm Agent, pagination, favorites

### Completed (✅ LIVE — deployed)
- **Prewarm Agent (Agent 15 — operational, read-only re: data).** Daemon thread in the
  **API process** that keeps every list-feed superset hot (`/scores`, `/topics`,
  `/history/recent` 7d/24h/12h, `/risk/scores`), re-warming every 25 min inside the 30-min
  cache TTL. `GET /prewarm` is non-blocking (kicks a background warm — synchronous warm
  ~38–44 s exceeds Heroku's 30 s router limit). Documented in `AGENT_CHARTER.md` (Agent 15),
  `DATA_BUILDING_BLOCKS.md` (§10.J + §8 read-path), and the nowtrendin2.0 skill.
- **History endpoint cached + prewarmed.** `/history/recent` was uncached → ~6 s/2.1 MB on
  the 7d view (the visible "Loading…" delay). Refactored to the scores/topics superset-cache
  pattern (`_compute_history_full`, limit-independent) → ~0.4 s compute from warm cache.
- **Progressive pagination for all list sections.** `/history/recent` + `/risk/scores` now
  take `offset`; web `api.ts` got `historyAll()` + `riskAll()` (fetch 100 at a time, paint
  per batch). History.tsx + MarketSignal.tsx load progressively (Trends `/topics` already did).
  All three list surfaces now match.
- **Market Signal prewarm parity** — `/risk/scores` superset-cached (`risk_full`) + warmed
  each cycle. All five web/mobile feeds are now prewarmed.
- **Favorites "Track topic" fix** — scoped to trend/history topics only (was mixing market
  instruments); clicking opens **History** pre-filtered to the topic (was the Market detail rail).
- **AI Context fixes** — serve-time `_clean_explainer` + hardened `_extract_json` (raw
  ` ```json ` leak); `key={topic_key}` on the web detail rail (stale-context-on-topic-switch).
- **Stage rename** — "Emerging" → "Indicating" (display-only via `stageLabel()`, all surfaces).

### Open / Next
- **1066 pending Accuracy-Ledger detections** — analysis + backlog-prevention recommendations
  (in progress this session).
- Optional: apply the same progressive load to Alerts/Watchlist/Dashboard typeaheads.

## Session 2026-06-22 — Sources, canonical-date checkpoint, M/D direction

### Completed (✅ LIVE — engine v98)
- **Nasdaq Trade Halts** wired into the risk module (`financial_risk_gradient.collect_nasdaq_halts`,
  registered in `run_risk_collection`): official exchange RSS, stage-2 microstructure;
  canonical `signal_date`=HaltDate, `source_time`=HaltTime. Verified in prod: 29 halts.
- **The New Yorker** (news + business) added to the reputable-direct RSS roster
  (`_RSS_FEEDS`). Verified in prod: 54 raw / 269 topic signals, tier=mainstream.
- **Documentation checkpoint:** CLAUDE.md (§14 canonical date/time model, §15 source roster +
  M/D direction), DATA_BUILDING_BLOCKS.md (§3a canonical-date block B3a, source registry,
  §5 M-vs-D router note), the **nowtrendin2.0 skill** (CURRENT BUILD STATE section), and 11
  data/scoring agent skills (consistent "Canonical dates · sources · M/D" section).
- Memory: added `project-dark-matter-routing` (the platform_tier D-vs-M finding + gotcha).

### Open / Next (⏳ IN DESIGN — NOT shipped; gated by backtest-before-ship)
- **M/D provenance reweighting**, two coupled `_news_write` changes:
  1. Reputable ≠ automatic mainstream full weight → 1 reputable = ½, FULL only on ≥2 DISTINCT
     reputable (distinct `source_name`; the "Belgium vs Iran" case).
  2. Research/early-signal outlets (War on Rocks, Rest of World, Global Issues, Pew, RAND-blog,
     NBER) → Dark Matter via `blog_collectors` GHOST_FEEDS at **expert/niche tier** (NOT
     `_news_write`). Feeds validated (prod UA). Adversarial integrity verify + `backtest_dual_pathway.py`
     required before deploy.

### Hard decisions made
- The D-vs-M router is **`platform_tier`**, NOT `is_organic` (mapped across the engine). Routing
  research outlets through `_RSS_FEEDS`/`_news_write` would stamp them `mainstream` and SUPPRESS
  the early signal — so they must go through the blog/expert-tier path. (This corrected an earlier
  plan that had prepped them for `_RSS_FEEDS`.)
- Reputable-corroboration weighting extends the catch-all `CATCHALL_MIN_SOURCES≥2` philosophy from
  *admission* to *weight*; distinct-source counting must key on `source_name` to defeat wire syndication.

---

## Session 2026-06-20 (session 2) — Infrastructure audit + skill hardening

### Completed

- **Full infrastructure audit:** Confirmed both clients (web terminal + mobile) and backend
  all correctly point to the v2 engine (`nowtrendin-v2-engine-edcb10d44f91.herokuapp.com`).
  No discrepancies between platforms — single source of truth rule is working at the data layer.

- **Deploy skill rewrite (critical fix):** The old `/deploy` skill was pointing the engine
  subtree push to `heroku main` (the BACKEND remote) instead of `heroku-v2engine main`.
  This is what caused the accidental 1.0 engine deploy on 2026-06-19. Fixed and backed up
  to `docs/skills/deploy.md` in the repo.

- **`AI_GRADE_CLAUDE_MODEL` updated live on Heroku:** Changed from `claude-sonnet-4-5-20250929`
  to `claude-sonnet-4-6` on `nowtrendin-v2-engine` (Heroku release v69).

- **`docs/ENV_REFERENCE.md` created:** Complete map of every env var for both engine and
  backend — status (SET/MISSING), description, and exact fix commands for all gaps.
  Key finding: GUARDIAN_API_KEY is missing → Stage 4 mainstream media signal silently absent
  every scoring run; GDELT fallback is rate-limited on Heroku IPs.

- **`transfer/.env.example` + `backend/.env.example` created:** Local dev reference templates
  (key names only — no values). Standard practice to prevent onboarding confusion.

- **`/nowtrendin2.0` skill hardened:** Added INFRASTRUCTURE STATE section (audit results,
  what's correct, what was fixed, pending user actions with exact commands). Added PENDING
  USER ACTIONS quick-check to session startup. Fixed wrong engine URL that was in STEP 4
  health check (pointed to 1.0 frozen engine). Fixed wrong deploy topology table.
  Rule #9 added: API key values never go in Git.

- **`docs/skills/nowtrendin2.0.md` synced:** Cloud backup of the skill now matches local.

- All above committed and pushed: `6909737` + follow-up skill sync.

### Open / Next

- **GUARDIAN_API_KEY** (HIGH) — Register free at open-platform.theguardian.com/access.
  Without it, mainstream media (Stage 4) is absent every scoring run.
  Command ready: `heroku config:set GUARDIAN_API_KEY=<key> -a nowtrendin-v2-engine`

- **SECRET_KEY on backend** (HIGH — security) — Django using insecure hardcoded default.
  Generate + set: `heroku config:set SECRET_KEY=<key> -a nowtrendin-backend`

- **REDDIT_CLIENT_ID/SECRET/USER_AGENT** (MEDIUM) — Reddit signal not collected.
  Register at reddit.com/prefs/apps (free), set 3 vars on engine.

- **APIFY_REALTIME_ACTOR + APIFY_TRENDS_ACTOR** (MEDIUM) — Token set, actor IDs missing.
  Check Apify console for existing actor IDs.

- **GOOGLE_ANDROID_CLIENT_ID** (MEDIUM) — Android Google OAuth may fail.
  Retrieve from Google Cloud Console.

- **Velocity retention 365 days** — PENDING USER CONFIRMATION. Do NOT implement until explicitly confirmed.
- **Stripe + push notifications** — deferred, require custom dev client (off Expo Go).
- **NYT RSS feeds** — 39 live feeds identified as viable for topic extraction. Not yet implemented.

### Hard decisions made

- ENV_REFERENCE.md documents key names + status only — never values. Values live on Heroku only.
- Do NOT re-run the full Heroku config audit each session; check the specific PENDING USER
  ACTIONS list instead (saved in /nowtrendin2.0 skill INFRASTRUCTURE STATE section).

---

## Session 2026-06-20 (session 1)

### Completed
- **Web terminal UX:** Added X clear buttons to every filter input across all platforms (History search, Market chip-search, Grade GradedList search, Shell global search, mobile history/search/watchlists)
- **History tab reset:** Clicking "History" in the sidebar now remounts the component (historyNavKey counter) — clears filter + selection. Mobile uses `useFocusEffect` to clear on tab focus.
- **Screener — Trends table:** Centered all column headers. Added DIRECTION column (TrendingUp/TrendingDown/Minus icon) after Category.
- **Screener — Direction sort:** Direction column is now fully sortable (orange triangle, SortKey type extended, special-case comparator mapping gap→-1/0/1). Deployed to gh-pages.
- **Grade click-through fix:** Clicking rows in Graded Library (and History) now opens the full ProposedCard detail — `sel` state added to GradeList. Fixed smart-quote encoding bug in GradeList that broke the esbuild step.
- **Skill /nowtrendin2.0:** Created session-startup skill — reads all context, runs health + skills + agents checks, and enforces the GitHub-as-cloud-backup auto-save protocol.

### Open / Next
- **Velocity retention 365 days** — PENDING USER CONFIRMATION. Do NOT delete any velocity_scores rows until user explicitly confirms the rule change from 90→365 days.
- **Stripe + push notifications** — deferred, require custom dev client (off Expo Go).

### Hard decisions made
- Direction sort: `direction` is derived from `gap`, not a stored field — special-cased in the sort comparator rather than materializing a fake field on Row.
- GradeList encoding: Edit tool on Windows can introduce Unicode smart quotes; future mitigation is Python binary replacement for source files.

---

## Live URLs

| Surface | URL | Notes |
|---|---|---|
| **Web app** (use from anywhere) | https://nowtrendin-web-8c1bb8c9f7f2.herokuapp.com/ | Static Expo web build on Heroku app `nowtrendin-web`. Snapshot — rebuild with `./redeploy-web.sh`. |
| Engine (FastAPI) | https://nowtrendin-e62dcb9ecb69.herokuapp.com | Heroku `nowtrendin`. Deploy: `git push heroku HEAD:main` from `NowTrendin/`. |
| Backend (Django) | https://nowtrendin-backend-acb79c396814.herokuapp.com | Heroku `nowtrendin-backend`. Deploy: `git subtree push --prefix backend heroku main` from `NowTrendin v2.0/`. |
| Frontend source | `origin` (GitHub) | Expo Go phone preview needs same-WiFi LAN (`exp://192.168.68.52:8081`) + firewall rule for TCP 8081. |

Internal founder key (gated engine endpoints): `X-Internal-Key: nt-internal-7f3a9c2e5b81`

---

## What was built this session (2026-06-10)

### Data sources
- Added creators: Graham Stephan, TheGrahamStephanShow, Minority Mindset (join Meet Kevin, Andrei Jikh).
- Added 22 broadcast YouTube channels (CNBC, BBC, Bloomberg×3, Reuters, WSJ, FT, Al Jazeera, 60 Minutes, etc.) — mainstream tier.
- Yahoo Finance (RapidAPI) news as a genuine contributor; feeds BOTH the Trends pipeline and the Market (risk) pipeline.
- WhaleWisdom 13F institutional positioning (metered/trial tier — `holders` endpoint blocked until subscription upgrade; monitor `WHALEWISDOM_MONITOR.md`, review 2026-07-08).
- OFR Short-Term Funding Monitor (systemic leverage) + FINRA short interest, both instrumented in the founder `/usage` cost ledger.
- YouTube creators + broadcast + Yahoo Finance all feed both Trends and Market (free pulls).

### Integrity (HARD RULES — now enforced)
- Reputable-publisher **allowlist** on aggregated news (`_NEWS_REPUTABLE_SOURCES`) — only vetted outlets enter the corpus; non-reputable dropped with a logged count.
- **Provenance tiering**: broad/unverified news quarantined at ~1% weight, promoted to ~10% ONLY when independently corroborated — reputable corroboration → mainstream (M), dark-matter corroboration → Dark Matter (D). Uncorroborated never stands alone (excluded from scoring).
- **No circular metrics**: the N (Now TrendIn demand) component is DELIBERATELY EXCLUDED from the Gradient Score (Detection/Confidence/Overall) — the live engine composes from six external components (G/I/M/D/C/P), renormalized to sum to 1.0, so our own users' demand can never create a feedback loop. N is computed and shown as a SEPARATE community-demand signal. The Signal Convergence validator also uses N-independent factors. (A separate, demand-inclusive "Now Trending Gradient Score" what-if is shown only on the trend signal page, clearly labeled and never sold as the Gradient Score.)
- Measurement, not advice — neutral tiers, disclaimers everywhere.

### Engine / scoring
- **Signal Convergence** (`now_trending_direction.py`, `GET /convergence/{topic_key}`) — downstream directional validator: does raw volume + niche concentration confirm the Gradient Score's direction? (vs Gradient, vs Niche). Independent of N.
- **Dark Matter recalibration** — first-timer score now `100 * ratio^0.7` (was `ratio*160`, clipped at 62.5% → no high-end resolution). Tested across 12 cases.
- **VIRAL-with-0-signals fix** — evidence gate in `ai_topic_intelligence.py`: a recognized AI topic with < `AI_TAXONOMY_MIN_SIGNALS` (5) collected signals no longer floors to a measured-looking VIRAL score; falls back to raw score + no tier, so the score is consistent with the signal count shown.
- **Trend Beneficiary** (`trend_beneficiary.py` + `_wire.py`) — SanDisk-pattern exposure: is a company positioned to benefit from a detected trend, EARLY vs LATE in the cycle. `GET /beneficiary/{ticker}`. Auto-theme extension (`theme_extension.py`) promotes BREAKOUT/STRONG topics into the beneficiary THEMES.
- **Explainer bug fixed** — `topic_explainers.full` → `full_text` (`full` is a Postgres reserved word; was breaking the MORE INFO feature).
- Connection-pool leak fix (was 500-ing `/scores`).

### Market Signal (the "Market" section)
- **Baseline-relative dual score** (`market_signal_engine.py`) — Gradient-Score philosophy on market data, every component z-scored vs the item's own history. Detection (analyst + positioning) / Confidence (fundamentals + price). Neutral tiers ELEVATED/ACTIVE/BUILDING/ROUTINE/DORMANT. CALIBRATING until 3+ cycles.
- Grounded in real sources only (Alpha Vantage, FINRA, WhaleWisdom, Finnhub/beneficiary, OFR, SEC Form-4, creators/broadcast, sustainability) — rejected aspirational components (options flow, credit spreads, price candles we can't source).
- **Historical backfill** (`POST /market/backfill`) — seeded `positioning_concentration` from FINRA 180-day series (180 points, 15 companies). Finnhub fundamentals backfill returns 0 (free-tier limit).
- **Leverage Health** category (1–100, high = lower debt) from balance-sheet sustainability. Live for ~8 companies (Meta 100, Microsoft 91, Tesla 66, Morgan Stanley 40).
- Market tab UI now **mirrors Trends**: "Search Current Market Trends" bar, Pull Market Trends, "Market Signal" explanation (renamed from Positioning), category chips + stat tiles, focused `market-category/[key]` pages.

### Grade section
- 3 tabs: **New Grade** (only one that charges, "Grade · 1 token"), **History** (this member's grades, 12-month, search, no charge), **Graded** (all members' graded topics, search, no charge). Backend `GradeHistory` model + `/api/grade/history/` + `/api/grade/all/`.
- **Grade ↔ Market consistency**: grading a COMPANY now also pulls the full market data and attaches `market_signal` — the same Market read as the Market section (identical numbers). The AI attention estimate stays a separate, labeled read. (They measure different questions: attention trend vs market positioning.)
- Enterprise grade allowance bumped 1,000 → 100,000 (founder balance set to 99,997).

### App UI / homepage
- Homepage chip row + stat tiles unified from one source of truth (`CATEGORY_DEFS`): NowTrendIn (lead, brand-colored) + All + Breakout/Strong/Emerging/LowRisk/Anomalies. Each navigates to a focused `category/[stage]` page. Removed the static "What does this mean?" card.
- "Now Trending (N)" explanation added to Signal Detail (above Dual Score Analysis), with the real Volume/Recency formula.
- "Why the scores diverge" made LIVE (was static); Topic Maturity ("ESTABLISHED") clarified with the live `maturity_reason`.
- Heisenberg → **DUALITY** wording.
- "Other" tab → **Market**; new "Pull Market Trends" button (`/api/pull-market/` → engine `/risk/collect`).
- Detail pages moved under `(app)` so they get the bottom tab bar; non-primary routes hidden from the bar (only Home/Search/History/Alerts/Profile show).
- "Search" tab rebuilt as "Search A Topic" with 3 tabs (Trends/Market/Graded), each searchable.
- **Web desktop layout**: app centered in a 480px phone-width column; onboarding carousel width capped.

### Tooling (Claude Code skills in `~/.claude/skills/`)
`/deploy`, `/data-health`, `/risk-verify`, `/tier-gate-audit`, `/accuracy-sweep`, `/beneficiary-backtest`, `/expo-recover`.

---

## Scheduled / open items
- **2026-06-20** — 10-day integrity monitor (scheduled task): convergence, dark-matter recalibration, news provenance rates, Market Signal baselines filling in.
- **2026-07-08** — WhaleWisdom upgrade-analysis review (scheduled task).
- Market Signal reads **CALIBRATING** until per-component baselines build (FINRA seeded only 1 of 7 components; the rest accrue live). Watch on the monitor; option to extend the backfill (needs paid Finnhub) or relax the CALIBRATING gate.
- Non-watchlist companies graded via Grade show CALIBRATING market signal (no baseline history yet) — expected.

---

## Recovery cheatsheet
- Resume this thread (same machine): `claude --continue` (or `--resume`) in `NowTrendin v2.0/`.
- Move to another machine: copy `~/.claude/projects/C--Users-acinv-...-NowTrendin-v2-0/` (transcript + `memory/`) to the same path; needs identical project path for the hash to match. Otherwise rely on `git pull` + the copied `memory/` folder + this log.
- Update the web app after any frontend change: `./redeploy-web.sh` from `NowTrendin v2.0/`.
