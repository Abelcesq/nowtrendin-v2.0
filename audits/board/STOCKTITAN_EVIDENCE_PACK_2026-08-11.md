# Evidence Pack — StockTitan RSS candidacy (identical pack to all nine seats)

**Decision before the board (Chairman-ordered 2026-08-11):** Canary's XRPC issuer-page
adapter has been REMOVED from the roster (frozen page, 0 production successes — already
executed and deployed). The Chairman designates StockTitan RSS (https://www.stocktitan.net/rss)
as the replacement candidate and asks the board to review the data and determine: usable for
**TRENDS** (the attention Gradient Score), **MONEY MOVEMENT** (Market Signal / risk
positioning), **both, or neither** — and under what conditions.

## Live data findings (tested 2026-08-11/12, production UA, all figures from the live feed)

- **Access:** keyless public RSS 2.0, HTTP 200; robots.txt permits; the feed advertises
  itself (self atom:link + a superfeedr push hub) — built for syndication. Per-ticker feeds
  exist and return 200: `/rss/news/{TICKER}` (tested AAPL).
- **Structure:** latest-100-item window; 100/100 pubDates parse cleanly (RFC-822 GMT →
  canonical `signal_date` + `source_time` via our §14 gate, verified format-compatible);
  ticker embedded in every title ("… | {TICKER} Stock News") and URL path.
- **Volume:** ~200–400 items/day; 53 items in the single peak hour observed. The 100-item
  window therefore spans only ~2–4 peak hours — a 6h poll of the firehose samples roughly
  a third of the flow. Targeted per-ticker polling avoids the completeness problem for a
  defined watchlist (we have 33 mapped tickers + crypto ETF/treasury proxies).
- **Content (live 100-item sample):** 46% earnings/results, 13% capital raises (offerings,
  converts, private placements, ATMs), 41% other company news. 99 distinct tickers in 100
  items; pronounced small/micro-cap + OTC tilt (WAUXF, FPVTF, ANPMF, DYNR, SLXN…).
- **Nature of the data:** issuer-authored PRESS RELEASES, wire-syndicated, aggregated in
  near-real-time. This is the company speaking about itself — PRIMARY source material for
  corporate EVENTS, but NOT independent editorial coverage of topics.

## Standing rules the verdicts must respect (not up for debate)

- §15 trusted-direct mainstream roster: "official/direct — **no aggregators**". Mainstream M
  measures BREADTH of INDEPENDENT outlets (Mainstream v2: ≥5 independent outlets,
  syndication-collapsed). A press release is self-issued — every wire copy collapses to ONE
  voice (the issuer), regardless of how many sites carry it.
- Dark Matter D routes via `platform_tier` expert/niche (GHOST_FEEDS), never `_news_write`;
  D's value is early first-timer signal under quality gates.
- Money data: **volume is NEVER flow** (C5/C6, board-unanimous). Positioning and capital
  events ARE money data (funding, OI, insider buying, ETF flow). A priced offering /
  convert / placement is a primary capital-structure event with a dollar amount attached.
- §16 five gates bind; a score-affecting source additionally requires backtest-before-ship
  (held-out accumulation first). §16a cold-start posture applies to any universe expansion.
- Copyright posture (Chairman-ruled): public RSS headlines are used for measurement, text
  never republished; StockTitan's own AI summaries are THEIR derivative content — we would
  use titles/tickers/dates/classes only.
- StockTitan carries NO shares-outstanding/NAV data — it CANNOT serve the A2 flow-derivation
  role the Canary adapter held. It is a candidate news/event source, not an issuer-shares source.

## Items for per-seat verdicts

- **ITEM 1 — TRENDS as mainstream M:** wire the firehose into `news_collectors` as a
  mainstream outlet feeding breadth/magnitude.
- **ITEM 2 — TRENDS as event/context signal (not M):** use corporate-event headlines as
  situation/context-layer input or expert-tier dark-matter trigger (e.g., crypto-treasury
  announcements, sector event clusters), never counted as independent outlet breadth.
- **ITEM 3 — MONEY MOVEMENT:** per-ticker feeds for the mapped watchlist (+ crypto
  ETF/treasury tickers); classify capital-event classes (offering/convert/placement/buyback);
  held-out event accumulation first, backtest before any score wiring.
- **ITEM 4 — Cadence/completeness:** firehose 6h-poll sampling (~⅓ coverage, honesty
  requirement) vs targeted per-ticker pulls vs push-hub subscription.
