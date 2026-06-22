---
name: frontend-consistency
description: NowTrendIn UI-parity monitor across all 3 platforms (mobile app, web terminal, desktop) — checks the signal/trend pages AND the market-analysis pages stay consistent (same labels, filters, detail sections, data points, and the mobile color scheme) and that the deployed sites are up. Use when the user says "check UI consistency", "do the apps match", "frontend parity", "are the sites up", "audit the front end", or after changing a filter/label/detail-section/color on any surface.
---

# /frontend-consistency — keep all 3 platforms consistent

**Product rule:** the **trend signal pages** and the **market-analysis pages** should
present the SAME information, sections, and color scheme on every surface. The web
terminal may add MORE (denser filtering, extra columns, deeper detail) but must not
DIVERGE on shared labels, filters, detail sections, or colors. Read-only audit.

## The 3 platforms
- **Mobile app** — `frontend/` (React Native). Trend detail: `frontend/app/(app)/signal/[id].tsx`.
  Market detail: `frontend/app/(app)/risk/[key].tsx`. Colors/helpers: `frontend/lib/signals.ts`.
- **Web terminal** — `web-terminal/`. Trend detail: `web-terminal/src/views/Screener.tsx`
  (`DetailRail`). Market detail: `web-terminal/src/views/MarketSignal.tsx` (`MarketRail`).
  Colors mirrored in `web-terminal/src/lib/mobileTheme.ts`.
  - ⚠️ **CANONICAL user-facing site = GitHub Pages:** https://abelcesq.github.io/nowtrendin-v2.0/
    served from the **`gh-pages` branch** of origin. A Heroku mirror exists at
    https://nowtrendin-terminal-1183c0ac00c4.herokuapp.com/ (`nowtrendin-terminal`).
  - **DEPLOY MUST HIT gh-pages** (else the user sees nothing change):
    `npm run build` in `web-terminal/` → `git worktree add ../ghp gh-pages` → replace
    `index.html` + `assets/` (keep `.nojekyll`) → commit → `git push origin gh-pages`.
    Also mirror dist into `web-deploy-terminal/` and push to the `heroku` remote.
- **Desktop** — Tauri wrapper around the SAME `web-terminal/` build (`tauri-desktop/`), so
  web parity ⇒ desktop parity. No separate UI to audit; just confirm it ships the latest build.
- **Mobile web export** (legacy mirror): https://nowtrendin-web-8c1bb8c9f7f2.herokuapp.com/

## Steps

1. **Uptime** — should return HTTP 200:
   ```bash
   curl -s -o /dev/null -w "terminal %{http_code}\n" --max-time 25 https://nowtrendin-terminal-1183c0ac00c4.herokuapp.com/
   curl -s -o /dev/null -w "mobile-web %{http_code}\n" --max-time 25 https://nowtrendin-web-8c1bb8c9f7f2.herokuapp.com/
   ```

2. **Signal-filter parity** — canonical set in mobile `frontend/lib/signals.ts` `CATEGORY_DEFS`;
   terminal mirror `web-terminal/src/views/Screener.tsx` `SIGNAL_FILTERS`. MUST match
   (keys + labels + predicate):
   - `Now TrendIn` (ranks by the **N / nowtrendin_score**) · `All Signals` (by Detection) ·
     `Breakout ≥85` · `Strong ≥70` · `Emerging` · `Low Risk` (|gap|≤6) · `Anomalies` (|gap|≥18).
   - **Stage column must derive from Detection** (`stageOf(det)`), NOT the server `current_stage`,
     so Stage reconciles with the Det column + the filter buckets. Flag any reversion.

3. **Trend signal DETAIL parity** — every section in mobile `signal/[id].tsx` must exist in the
   terminal `DetailRail` (web may add more). Checklist:
   - Topic Maturity badge (`calibration.maturity_class` → NEW/EMERGING/ESTABLISHED/RESURGENT) + reason
   - AI-tier badge · Dual gradient rings (Detection/Confidence)
   - **N component + Now Trending Gradient Score (demand-inclusive) + Signal Convergence**
   - Detection–Confidence Gap · **Dual Score Analysis** (gap bands + who-uses-which)
   - **Score Breakdown** = 4 groups: Signal Quality · Signal Momentum · Signal Context · Community Demand
   - **Why the Scores Diverge** · Dark Matter · Topic Variations · Research History · X Signal ·
     Scoring History · Methodology · Signal Read · Source & Why
   ```bash
   grep -nE "<h4>|Topic Maturity|Now Trending|Dual Score|Why the Scores|Dark Matter|Score Breakdown" web-terminal/src/views/Screener.tsx
   ```

4. **Market-analysis DETAIL parity** — every section in mobile `risk/[key].tsx` must exist in the
   terminal `MarketRail`:
   - Market Gradient dual score + tier + gap-state + interpretation
   - **Market Factors** (colored by feed: detection/confidence/both, ✓ baseline-relative) · Tier legend
   - **Financial Sustainability** (raw + sector-adjusted + profitability/liquidity/leverage + metrics)
   - **Retail & Media Coverage** (Alpha Vantage, creators, broadcast) ·
     **Leverage & Funding** (FINRA short interest, OFR macro, WhaleWisdom 13F)
   - Market Tenure · Vs-own-baseline · Diffusion Pipeline · Score Components · Sources

5. **Color-scheme parity** — the web trend + market detail must use the MOBILE palette via
   `web-terminal/src/lib/mobileTheme.ts`: Detection `#2D7EEF`, Confidence `#00C896`, stage colors
   (BREAKOUT green / STRONG blue / EMERGING gold / WATCHING orange / MONITORING grey), market tiers
   (ELEVATED/ACTIVE/BUILDING/ROUTINE/DORMANT), feed colors (detection blue / confidence green / both
   purple). Cross-check the hex against `frontend/lib/signals.ts` (`STAGE_COLORS`, `SCORE_ROLES`,
   `maturityColourHex`) + `frontend/app/(app)/risk/[key].tsx` (`MARKET_TIER_COLOR`, `FEEDS_COLOR`).

6. **Category-chip parity** — mobile `CONTENT_CATEGORIES` vs terminal live `/categories` (12 content
   categories). **Key-action parity** — both have Pull Trends (1 token), Trends label (not "Signal"),
   Watchlists, Market Signal, Accuracy Ledger.

7. **Report**: ✅ in sync (what matched) · ⚠ drift (file:line each side + the mismatch) · note
   intentional web-only enhancements so they aren't flagged.

## Discipline
Code-truth, cite file:line on each side. Web/desktop may add MORE; they must not DIVERGE on shared
labels, filters, **detail sections, data points, or colors**. Audit only — hand findings back for a fix.
Part of the monitoring fleet (DATA_BUILDING_BLOCKS.md).
