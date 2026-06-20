# NowTrendIn 2.0 — Session Log

A running, readable catch-up of what's been built and what's open — so any new
Claude Code session (or you on your phone) can resume without the local thread.

_Last updated: 2026-06-20_

---

## Session 2026-06-20

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
