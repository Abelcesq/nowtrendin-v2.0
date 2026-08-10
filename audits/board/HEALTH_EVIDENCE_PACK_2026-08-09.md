# EVIDENCE PACK — Full health review board (2026-08-09/10)

## What is being decided (neutral statement)
The Chairman ordered a complete health check and a NINE-seat board review of ALL
current agents, data sources, and scoring models, producing an analysis of what must
improve across the TRENDS, MARKET, and CRYPTO products to serve the goal: monitor
information and track human attention movement BEFORE it arrives. Plus one specific
item: what must be done to fix the crypto page's "n/a" Money Movement and ABSENT
tier state. The board informs; the Chairman rules.

## Read these (identical for all seats)
1. `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\CLAUDE.md` (§6, §13–§17 + footer — the system spec + recent history)
2. `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\SESSION_LOG.md` (read the LAST ~400 lines — everything since 2026-08-05)
3. `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\audits\DEFERRED_ITEMS.md` (the gated-work shelf, esp. D8)
4. `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\docs\buyer-diligence\ACCURACY_FIGURES_SCOPED.md` + `RIGHTS_REGISTER.md` §H (open rights questions)
5. `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\AGENT_CHARTER.md` (agent roster, skim)

## LIVE HEALTH BATTERY (2026-08-10 ~04:30–05:00 UTC, verbatim reads)

**Engine:** operational. **Prewarm:** healthy (scores superset 4,025 rows, 25-min loop).
**Category maps:** warm (situation 408, context 60,974 entries, live).

**Collectors (26 rows):** HEALTHY: github 5362 sig · hackernews 188 · blogs 1677 ·
newsapi_org 231 · newsapi_ai 566 · newsdata_io 72 · bluesky 559 · lemmy 382 ·
mastodon 132 · google_trends 661 · youtube 12 · creators 325 · broadcast 2584 ·
risk 1486 · alphavantage 16 · finviz_insider 163 (65 distinct) · finnhub_insider 408
· issuer_shares 8/8 + families ishares 2, bitwise 3, 21shares 3.
DEGRADED: gdelt (runs, 0 signals — Heroku IP rate-limit class).
DOWN: issuer_canary (correct fail-closed — XRPC page frozen at 07-31).
STALE: **socialcrawl (24h since success; window 900m)** — suspected cause: the 6h
collect cycle is boot-phase-anchored, tonight's repeated deploys phase-shifted it
away from the two armed clock-slot families (00/12 UTC); slot-skips don't log runs.
A cycle-phase vs clock-slot mismatch can keep it stale indefinitely. (Operator
finding, unfixed — for the board.)
DISABLED (intentional, reported-not-alarmed): reddit, finnhub_congress.

**Monitoring fleet (run_all):** scorer_watchdog ok · fragment_category ok ·
calibration ok · data_subscriptions ok · heldout_firewall ok · flow_integrity ok ·
similar_fragmentation ok. WARN: source_watchdog (the 3 collector items above);
pipeline_integrity (5 risk topics still serving pre-2026-07-20-guard rows).
**CRITICAL: cost_sentinel — X pay-per-use pacing $437/mo vs the $200 configured
line (3,480 posts MTD × $0.0413).** INFO: etf_reconcile (FMP silent-comparison: 10
divergent intervals — accruing evidence for the 2026-09-05 drop decision);
crypto_price_referee (FMP-implied SOL supply 3.10% and XRP 2.97% off CoinGecko).

**Scoring/ledger models (live):**
- Attention ledger: tracked-race 27.1% (N=48) / blended 11.7% (N=111), PROVISIONAL
  (0 of 13 LED wins referee-corroborated; 10 ambiguous queries); epoch split: v1
  (retired) 15.8%/42.9% n=28 vs v2 (current) 2.9%/5.0% n=20; 1,195 pending;
  KM eventual 4.0%; null-model comparators now live (breakout base rate 100%,
  random-order 50%); enrollment completeness 69.6%.
- Market ledger: rate WITHHELD by design (clean cohort 4 of 30 required; 22
  dead-parser-era rows excluded; record 15 confirmed / 11 not).
- Crypto ledger: rate withheld (1 resolved, 0 clean).
- Flow/arrival ledger: publishable=false (0 episodes vs pre-registered min 120).
- A2 ETF-flow re-arm: pass 0/5, open_bad 0, zero live-source failures — clocks
  running cleanly on the issuer source; flip BLOCKED as designed.

## THE CRYPTO "n/a / ABSENT" ITEM (Chairman-flagged, screenshot 2026-08-09)
The Crypto page shows ALL 12 coins: Money Movement "n/a", tier ABSENT, lead "—";
only Market Confirmation (the coin's own price read) is numeric. Detail panel:
"No money-positioning source reported for this coin this cycle (0 of 2 required)."
This is the HONEST-ABSENCE design (D7/D8-T1) working as ruled — but the Chairman's
question is what must be BUILT so the money leg actually reads. Known chain:
(a) the proxy Dark-Matter leg (Finviz insider accumulation on crypto-exposure
equities) fires only on ≥$250K insider BUYING events — sparse, so most cycles read
absent; (b) the designed second source, ETF creation/redemption FLOW
(CRYPTO_ETF_FLOW), is flag-gated OFF pending the A2.4 re-arm (5 in-band issuer-
source comparisons; clocks started 2026-08-08, currently 0/5) + wave-3 adapters
(Fidelity FBTC/FETH, Grayscale) + the flip's coverage-disclosure condition;
(c) XRP funds have NO published-flow comparator (honest no_comparator); (d) on-chain
data (Glassnode/Nansen class) is an unfunded future gap. The board should assess:
the fastest INTEGRITY-COMPLIANT path to real money reads per coin, interim display
improvements (if any), and whether the current absent-state communication is right.

## Standing open items (context)
Chairman queues: 9 open rights questions (RIGHTS_REGISTER §H, incl. Guardian
conflict + scraper-acceptability ruling never recorded); 6 accuracy-display defects
(ACCURACY_FIGURES_SCOPED §3, incl. the provisional caveat not rendered on any UI);
adoptables lists (Griffin + Two-Poles mechanics + roadmap Phases); ETHA epoch
pre-declared (effective 2026-10-06); FMP re-eval 2026-09-05; key rotations
(Socialcrawl/ScrapeCreators/QUIVER/FMP) still owed; single-founder permanency
(runbooks workstream); D8 fuller exclusion deferred behind T3.

## What each seat must return
Your archetype's standard verdict format, applied to FOUR review items:
(A) the AGENT fleet (collectors + monitors) health and gaps;
(B) the DATA layer (sources, rights, provenance) health and gaps;
(C) the SCORING MODELS (trend gradient, market money gradient, crypto, ledgers) —
    specifically what must improve for the before-it-arrives goal, per product;
(D) the crypto n/a/ABSENT fix path.
**HARD LIMIT: your complete memo must be under 700 words.** Prioritize your
highest-conviction findings; omit the routine. Plain text.
