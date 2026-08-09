# §16 Source Onboarding Review — Socialcrawl + Scrape Creators (2026-08-07)

Founder-submitted candidates (both with fresh accounts, 100 free credits each). Reviewed
together because they cover the same space: scraper-backed social/trend data APIs. All
five gates run IN ORDER per CLAUDE.md §16; live TESTs performed with the founder's keys
(≈21 Socialcrawl credits + 2 Scrape Creators credits spent; responses archived in the
session scratchpad).

> ⚠ **KEY HYGIENE:** both API keys were pasted into the chat (screenshots + text) and are
> therefore transcript-exposed. Per the 2026-06-26 Apify precedent: **rotate both keys**
> after wiring decisions land. Values go ONLY into Heroku config vars + local `.env`
> (gitignored) — never git.

---

## Vendor 1 — Socialcrawl (socialcrawl.dev)

Unified social-data API: 48 platforms / ~380 endpoints, one normalized schema
(`post{content,author,engagement,published_at}` + `computed`). Credit-priced: standard
call 1 credit, heavy endpoints more (**trending endpoints charged 5 credits** in live
test); £15/2,500 · £49/20–25k · £299/150k; cache hits free. OpenAPI at `/v1/openapi.json`.

### Gate 1 — TYPE: PASS
Attention/trend signal (social trending feeds, search, Google Trends series). Not
positioning, not risk. The `computed` fields (`engagement_rate`, `estimated_reach`) are
VENDOR-DERIVED — if ever ingested, use raw counts only; never store vendor-derived
estimates as measured data.

### Gate 2 — ENGINE: PASS (discovery)
Correct pipeline: `discovery_collectors.py` (category-agnostic "what is trending NOW"
feeds, TRUST-THE-SOURCE-ENTITY design). NOT `_news_write`/mainstream RSS (would force
`mainstream` tier), NOT risk. One primary engine per §16.

### Gate 3 — FORMAT: PASS for google_trends/*; MODERATE for social feeds
- Dates: ISO 8601 (`2026-08-07T04:00:01Z`) → `to_iso_date` clean. PASS.
- **`/google_trends/rising`** (live test, keyword "ai"): entity-grade pre-resolved
  queries WITH growth magnitude — `"ray dalio ai bubble warning" +7000%`,
  `"ai workforce skills mismatch" +2400%`. Exactly the discovery shape we already trust
  from the free daily-trending RSS. PASS.
- **`/google_trends/explore`**: hourly `{date, datetime, value}` interest-over-time
  series. Clean. PASS (as a curve source).
- **`/instagram/reels/trending`** (live test): 29 items, fresh (published 08-05/08-06),
  captions carry content-descriptor hashtags (`#spiderman #parody`) — extractable via a
  hashtag stoplist but entity quality is MODERATE (descriptors ≠ emergent trend entities).
- `/tiktok/trending` (live test): same caption-grade limitation; feed mixes months-old
  resurging posts. MODERATE-WEAK.

### Gate 4 — CURRENCY + ACCESS: PASS
Fresh (YT trending items published same-day; IG previous-day). HTTP 200, 0.3–8s
responses, clean error bodies (400s charge 0 credits), stable UA-less access, per-key
rate limits described as generous. Small-vendor risk noted (young product, solo-dev
origin) — acceptable for a non-critical discovery lane with graceful absence.

### Gate 5 — TEST: DONE (evidence above) → LINK: one lane wired DARK → DEPLOY: pending founder
Verdict: **CONDITIONAL PASS — lane-by-lane, founder picks which to arm.**

| Lane | Read | Status |
|---|---|---|
| A. `google_trends/rising` seeded discovery | Entity-grade, growth-weighted; extends the free daily-RSS discovery with rising-query expansion | **✅ WIRED + ARMED 2026-08-08 (founder go)** — `discovery_collectors.collect_socialcrawl_rising` at **niche** tier (Dark-Matter routing; deliberately not `expert` — no corroboration-floor exemption earned), flag `SOCIALCRAWL_RISING=1` + `SOCIALCRAWL_API_KEY` on the engine; 2 slots/day (00/12 UTC families), `SOCIALCRAWL_SEEDS_PER_SLOT`=3 rotating over 6 seeds ≈ 900 credits/mo; `collector_health` row `socialcrawl` (900m window, disabled-pattern when flag off); `COST_SOCIALCRAWL_USD` + Data Subscriptions entry registered. Gate-5 live test 2026-08-08: 43 topic signals from 2 seeds, clean entities ("mitch mcconnell health" +2300%, "spacex stock", "hybe stocks"), 10 credits. Monitored trial: watch topic-quality + catch-all auditors per the GHOST_FEEDS template |
| B. `google_trends/explore` as ledger-sweep curve alternative to Apify | High potential cost/latency win (~$0.04/curve vs compute-expensive actor runs) | **NOT wired.** Touches the moat's measurement path — requires a held-out side-by-side vs the Apify actor on identical keywords before any swap (separate §16 + board gate) |
| C. `instagram/reels/trending` | Only IG-trending source available to us; moderate entity quality | NOT wired — founder call on value at ~$0.04/pull |
| D. Social trending feeds (TikTok) | Caption-grade, stale-mix | Do not wire |

## Vendor 2 — Scrape Creators (scrapecreators.com / api.scrapecreators.com)

Raw platform-native payloads, 110+ endpoints, flat ~1 credit/call, $47/25k pay-as-you-go,
credits never expire. Cheapest per call (~$0.002).

### Gate 1 — TYPE: PASS (attention/trend signal)
### Gate 2 — ENGINE: PASS (discovery — same reasoning as above)
### Gate 3 — FORMAT: **FAIL for the tested trending endpoint**
`/v1/tiktok/get-trending-feed` live test: 16 items = ~9 unique (duplicates), regions mixed
(PK/US/AU/SA/ZA/AE) with no filter, create_times mostly WEEKS-TO-MONTHS old (resurging
evergreen content), captions extract to content-descriptor tags (`bassboosted`,
`cookieplatter`, `asmr`) — not emergent trend entities. Ran through `to_iso_date` + a
hashtag stoplist locally: dates canonicalize fine (epoch → ISO), but topic quality fails
the eyeball ("run real items through the extractor and eyeball the output"). Wiring this
would inject exactly the fragment/catch-all junk class §13 fights.
### Gate 4 — CURRENCY + ACCESS: PARTIAL FAIL today
API is up and fast, but the RIGHT endpoint for measured trend discovery —
`/v1/tiktok/videos/popular` (TikTok Creative Center: time-period + country filtered)
— returns 503 "endpoint unavailable; TikTok's own page is down" (upstream outage,
honestly reported by the vendor, 0 credits charged). Cannot pass CURRENCY on an
endpoint that cannot currently serve.
### Gate 5: **HOLD — do not link.**
**Re-tested 2026-08-08 (founder-ordered wiring attempt): BOTH `/v1/tiktok/videos/popular`
AND `/v1/tiktok/songs/popular` still 503 (upstream TikTok Creative Center down; vendor
honest, 0 credits charged, 98 remaining). HOLD stands — §16 forbids linking a source
that cannot currently serve.**
Re-test `/v1/tiktok/videos/popular` (+ `/v1/tiktok/songs/popular`) when TikTok Creative
Center is back up. If it passes the eyeball then, Scrape Creators becomes the preferred
TikTok lane on cost (~10–20× cheaper per pull than Socialcrawl's 5-credit trending calls).
Keep the account + credits (never expire).

---

## Cross-cutting integrity note (founder acknowledgment requested)

Both vendors are **unofficial scrapers** of TikTok/Instagram/etc. We would license data
from the vendor; the vendor bears the scraping relationship with the platforms. This is
one step beyond the existing Apify precedent (Google Trends + Reddit scraping, accepted
2026-06). It does not violate the letter of the reputable-sources rule (the SOURCE
platforms are the world's largest attention venues; the vendor is the access method), but
"licensed" is doing less work here than for FMP/Finviz/Databento. Flagged, not decided —
Chairman's call whether scraper-backed social lanes are acceptable at all.

## Cost + monitoring (if/when armed)

- Lane A at default sizing (6 seeds × 2 slots/day × 5 credits) ≈ 1,800 credits/mo ≈
  **£11–15/mo** — register a `COST_SOCIALCRAWL_USD` line + Data Subscriptions entry when
  flipped; clock-slot compliant (runs inside the 6h collect cycle).
- `collector_health` entry added (disabled-pattern window, mirroring `reddit`), tighten
  to 420m on flip.
- Free-credit runway: ~79 Socialcrawl credits remain (≈2 weeks at half sizing for a
  monitored trial), 98 Scrape Creators credits remain.

## Decisions awaiting the Chairman

1. Arm Lane A (`SOCIALCRAWL_RISING=1` + `SOCIALCRAWL_API_KEY` on the engine) for a
   monitored trial? (Watch topic-quality + catch-all auditors, per the GHOST_FEEDS
   trial template.)
2. Approve building the Lane B held-out Apify-vs-Socialcrawl curve comparison?
3. Lane C (IG reels trending) — wanted at all?
4. Scraper-backed-social acceptability (integrity note above).
5. Key rotation timing (both keys transcript-exposed).
