# NowTrendIn — Data Rights Register
**Version 1.0 · compiled 2026-08-09 from a full code + audit-record sweep · Owner: Founder**
**Fields:** source · access method · license basis · redistribution posture as recorded · status
**Rule (FISD gate 3):** a right we cannot evidence is recorded as OPEN, never asserted. "We
fetched it and nobody complained" is not a right. Evidence citations live in the compile
record (`audits/board/` + per-source §16 review docs); the register states the conclusion.

## A. Paid/licensed commercial data vendors (strongest rights class)
| Source | Access | License basis | Status |
|---|---|---|---|
| Finviz Elite | subscription export | paid license $30/mo | active — PRIMARY insider Form-4 |
| FMP | official API | paid Starter $20/mo | active (prices/fundamentals/crypto M-leg; demoted to observations-only on issuer-covered ETF tickers) |
| QuiverQuant | official API | paid $30/mo | active (congress → Dark Matter input; display de-named by ruling) |
| WhaleWisdom | official signed API | paid metered | active (13F) |
| Databento | official API | paid metered commercial | active — referee/verification only |
| X (Twitter) API v2 | official API, OAuth2 | paid (Pay-Per-Use) | active, budget-capped |
| NewsAPI.ai (Event Registry) | aggregator API | paid subscription | active |
| NewsData.io | aggregator API | paid/free-tier terms | active |
| NewsAPI.org | aggregator API | ⚠ free tier is production-banned per its own terms (recorded in code); whether a commercial tier is held is **OPEN item 4** | active — resolve tier |
| Apify (Google Trends actors) | paid scraper platform | vendor relationship (Scale plan); trend-only scope, clock-slot capped | active — see OPEN item 8 |
| Socialcrawl (rising-queries lane) | paid scraper-vendor API | vendor credits; §16 conditional pass, Lane A only | active (flag-gated, monitored trial) — see OPEN item 2 |
| Perplexity / Anthropic | official APIs | metered commercial | active (AI enrichment outputs only) |

## B. Official/government/public-domain (clean rights class)
SEC EDGAR (public domain; programmatic access explicitly permitted with declared UA) ·
FRED · FINRA · OFR STFM · Nasdaq Trade Halts (official exchange RSS) · Federal
Reserve/ECB feeds · Wikipedia/Wikimedia APIs · GDELT ("free, no commercial
restriction") · Google Trends daily-trending RSS (official public feed) · Blogger API ·
YouTube Data API v3 (official terms; **metadata-only posture recorded in code — no
content republication**) · Google Custom Search API (dormant). All active except as
noted; none redistributes source content — the product ships derived aggregates.

## C. Official free APIs of platforms/communities
GitHub API (token; rotated 2026-07-07) · Hacker News (Algolia public API) · Dev.to ·
Hashnode · WordPress.com public API · Discourse forum APIs · Bluesky public AppView ·
Lemmy · Mastodon public trends. Free official API terms; titles/metadata-level
ingestion; active.

## D. Direct RSS of reputable outlets (the documented-rights GAP class — OPEN item 3)
El País, TechCrunch, BBC, LA Times, CNBC, The Guardian(⚠), DW, ABC (AU+US), The Verge,
InfoQ, Financial Times, The Economist, The New Yorker, The Independent, NBC News, NYT
section RSS, plus newsletter/sport/culture feeds and expert/research blogs (GHOST/
RESEARCH feeds, §16-passed). Basis as recorded: official public syndication feeds,
fetched directly (no aggregators), titles/summary-metadata-only ingestion, no content
republication; per-feed live verification noted in code. **Honest posture: no
outlet-level license or redistribution permission document exists** — the internal
board record itself concedes "'licensed' is doing less work here than for
FMP/Finviz/Databento." Recorded OPEN; see item 3.

## E. Issuer/official public documents
ETF issuer product pages (iShares, Bitwise, 21Shares, Canary; Grayscale/VanEck/
Fidelity pending wave 3) — the issuer's own official public disclosures, ruled PRIMARY
daily-shares source (A2.3). Caveat disclosed: iShares serves 403 to bare clients; we
fetch with a browser-grade UA carrying our declared token; Grayscale's active 429 wall
is respected (fail-closed absence, no escalation) — doctrine in annex A2-N1.7; rights
posture OPEN item 7.

## F. Held-out referees (never feed any score)
Wikipedia pageviews referee · GDELT referee · Farside Investors (declared UA;
"held-out REFEREE, never a data source feeding any score") · CoinGecko/CMC keyless
(§16-onboarded 2026-08-05 into a STRICT display-supply + referee role; previously
banned — documented reversal trail) · Databento price-verify · the Google-Trends
validation curve (the ledger itself is held-out).

## G. Banned / removed / never-linked (the exclusion list — evidence of the gate working)
| Source | Disposition |
|---|---|
| yahoo_finance (RapidAPI) | removed 2026-06-24 — 429s (access gate) |
| Mises Literature | never linked — 404 + archival (currency/type gates) |
| NBER | failed §16 twice — author-name topic noise; do not re-add without a paper-title extractor |
| Pew Research | failed as-is — feed pollution |
| Reddit official API | intentionally disabled — "banned until written commercial approval" |
| Guardian API | key deliberately never set (ban list) — see OPEN item 1 |
| Messari | banned, never wired |
| OpenBB | TOTAL exclusion (Chairman ruling 2026-07-28, binding — AGPLv3 exposure declined) |
| Medium tag RSS | blocked by Medium ~2023; replaced by newsletter feeds |
| FT Alphaville / Reuters agency / WSJ / SF Chronicle RSS | tested and excluded (paywall teaser / discontinued / dead) |
| Scrape Creators | §16 HOLD — do not link (format fail + upstream 503); credits retained |
| Socialcrawl lanes B/C/D | not wired (B gated on held-out comparison; D "do not wire") |

## H. OPEN RIGHTS QUESTIONS (the honest section — Chairman's queue)
1. **Guardian conflict (A1): ✅ RESOLVED — Chairman ruling 2026-08-10.** "Public RSS
   headlines are different from API access" — the ban list's "until written
   commercial approval" governs the Guardian **API product** (key remains unset);
   the outlet's PUBLIC RSS syndication feeds are a distinct access class under the
   direct-RSS doctrine (titles/metadata only, no content reproduction, derived
   scores as the product). Position paper: `COPYRIGHT_POSITION.md` (adopted same
   date, incorporating the reviewed fair-use/facts-doctrine authority). The 7
   Guardian RSS feeds are therefore CONSISTENT with policy as ruled.
2. **Scraper-backed social acceptability:** the general ruling requested in the
   2026-08-07 review was never recorded — only the Socialcrawl Lane-A arm. Record
   the general ruling.
3. **Direct-RSS redistribution rights:** the largest documented-rights gap. The
   ingestion is titles-metadata-only and the product ships derived aggregates (a
   defensible fair-dealing posture), but no outlet-level permission exists. Options:
   counsel memo blessing the derived-aggregate posture; per-outlet permissions for
   the load-bearing feeds; or reclassify affected feeds.
4. **NewsAPI.org tier:** evidence whether a commercial tier is held; the free tier is
   production-banned by its own terms.
5. **youtube_transcript module:** self-declared ToS gray area; held-out today; needs
   a rights ruling before any promotion.
6. **Residual reddit.com public-JSON corroborator calls** remain in code despite the
   Reddit ban — rule explicitly (remove or bless keyless public-page reads).
7. **Bot-protected issuer pages:** UA doctrine documented (annex A2-N1.7); ruling it
   as a RIGHTS matter (counsel eyeball of site terms) remains open per the board.
8. **Google Trends via Apify:** vendor-mediated only; no Google-side license recorded
   (predecessor of item 2 — same ruling should cover both).
9. **US Treasury:** listed in the risk-source registry with a legal basis but no
   fetch call found — confirm before ever representing it as an ingested source.

## I. Register maintenance rule
A new source row is created by the §16 onboarding itself (the commit-msg hook already
forces the review); this register is updated in the same commit that links a source,
and the OPEN list may only shrink via a recorded ruling — never by silence.
