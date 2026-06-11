# Checkpoint — 2026-06-10 (end of session)

A return-point snapshot. If we need to come back to exactly this state, this is
where everything stood. Full detail lives in `SESSION_LOG.md`; this is the
"current status + what's verified live" view.

---

## Status: everything deployed & green

| Surface | URL / target | State |
|---|---|---|
| Web app (use anywhere) | https://nowtrendin-web-8c1bb8c9f7f2.herokuapp.com/ | ✅ live (v4); desktop layout centered 480px; tab bar = Home/Search/History/Alerts/Profile only |
| Engine `nowtrendin` | https://nowtrendin-e62dcb9ecb69.herokuapp.com | ✅ `/scores` 50, `/risk/scores` 29 (all carry market_gradient) |
| Backend `nowtrendin-backend` | https://nowtrendin-backend-acb79c396814.herokuapp.com | ✅ migration `0007_gradehistory` applied; grade history + all endpoints live |
| Frontend source | `origin` | ✅ pushed |

Internal key (gated endpoints): `X-Internal-Key: nt-internal-7f3a9c2e5b81`

---

## Verified live this session
- `/convergence/{topic}` returns CONFIRMED/MIXED/CONFLICTING (e.g. llm → MIXED).
- Dark-matter recalibration: 62.5% vs 100% first-timer now distinct (72 vs 65).
- VIRAL evidence-gate: 0-signal known topic → raw score + no tier; 20-signal → tier-1.
- Market Signal: 29 rows, baseline-relative; Leverage Health live (Meta 100, MSFT 91, TSLA 66, MS 40).
- `/market/backfill`: FINRA 180 points seeded; Finnhub 0 (free-tier limit).
- Grade attaches `market_signal` for companies (Tesla: attention 38/59 MONITORING + market 22/21 DORMANT, LH 66).
- Explainer (MORE INFO) works after `full`→`full_text` fix.
- Web app HTTP 200, CORS `*` on both APIs.

---

## Open / scheduled (don't lose these)
1. **2026-06-20** — 10-day integrity monitor (scheduled task `nowtrendin-10day-integrity-monitor`): convergence sanity, dark-matter spread, news quarantine/corroboration rates, Market Signal baselines filling in.
2. **2026-07-08** — WhaleWisdom upgrade-analysis review (scheduled task `whalewisdom-upgrade-review`).
3. **Market Signal CALIBRATING** — only `positioning_concentration` is baseline-seeded (FINRA); the other 6 components accrue live, so most items read CALIBRATING until ~3 cycles pass. Options when ready: extend backfill (needs paid Finnhub) OR relax the all-components-calibrating gate to majority-weighted.
4. **WhaleWisdom** `holders` endpoint still blocked (trial tier) — institutional_holdings will populate when quota resets/upgraded.
5. Non-watchlist graded companies show CALIBRATING market signal (no baseline yet) — expected.

---

## Machine / continuity notes
- Continuing on the **desktop** (`C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0`).
- Conversations + memory live in `C:\Users\acinv\.claude\projects\C--Users-acinv-...-NowTrendin-v2-0\` (NOT in OneDrive — see SESSION_LOG.md "Recovery cheatsheet" for cross-machine copy).
- Update the web app after any frontend change: `./redeploy-web.sh` from this folder.

---

## Deploy commands (reference)
```
# Engine (from NowTrendin/)
git push heroku HEAD:main
# Backend (from NowTrendin v2.0/)
git subtree push --prefix backend heroku main
# Frontend source (from NowTrendin v2.0/)
git push origin HEAD
# Web app rebuild+deploy (from NowTrendin v2.0/)
./redeploy-web.sh
```
