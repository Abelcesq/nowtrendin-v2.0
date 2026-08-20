# EVIDENCE PACK — Dark Matter (D) component: complete analysis convening
### Prepared 2026-08-20 for the nine-seat advisory board (Chairman-ordered).
### Question before the board: how must the Dark Matter component improve for the product to achieve its goal — identifying items and movement BEFORE they trend?

Read-only convening. All paths relative to repo root. Board members may read any file cited.

---

## 1. WHAT DARK MATTER IS (mechanism, from code)

- **The D-vs-M router is `platform_tier`** (`raw_signals.platform_tier`), NOT `is_organic`.
  `tier="mainstream"` feeds M (breadth/magnitude), lands in the mainstream denominator
  (suppresses the early read) and raises blend weight `w`; `tier in {"expert","niche"}`
  routes to the Dark-Matter/expert pathway (zero mainstream breadth, `w`~0).
  `detection = (1-w)·expert + w·mainstream` (`transfer/dual_pathway.py`).
- **D's numerator is `is_first_timer`** (author first seen in a community); `is_organic`
  scales D's quality gate. First-timer influx into expert/niche communities = the early signal.
- **Expert-tier signals are EXEMPT from the catch-all corroboration floor** (§13) — precision
  in expert-tier extraction is an integrity requirement, not a preference.
- **§15a quorum:** 5 independent outlets (syndication-collapsed, spike counts as one vote)
  = mainstream. Below quorum a topic stays a Dark-Matter TRIGGER — early read preserved.
- Market-side D (Money Gradient): Finviz Form-4 insider BUYING (primary), 13F, congress
  (Quiver), FINRA/OFR macro. Crypto D = proxy-based via Finviz. (This convening's focus is
  the TREND-side D; market D findings welcome where relevant.)

## 2. MEASURED STATE (live production, 2026-08-20)

**Tier mix (raw_signals, 7d):** mainstream 51,576 (89.0%) · expert 3,954 (6.8%) ·
niche 701 (1.2%) · unverified 1,707 (2.9%). **Dark Matter = 8.0% of collection.**

**Composition: ~90% of D volume is technology** (Dev.to ~1,400 items/7d, GitHub topic feeds
~1,700, HackerNews 376, dev forums ~450, AI newsletters ~200, Google dev blogs ~80, Lemmy ~75).
Non-tech D: 3 football desks (~290/7d) + Pitchfork (37) + socialcrawl `rising_*` niche lane
(25–43/wk EACH for ai/crypto/stocks/health/sports/entertainment) + firecrawl search (~30) +
research outlets War on the Rocks/Rest of World/Global Issues/RAND (**113 items → 145 topics
per week total, ~2.5% of D**; flag `GHOST_RESEARCH_FEEDS=1` live since 2026-07-15).

**Reddit is DOWN (403 on every subreddit, visible in today's boot logs — praw errors on
r/LocalLLaMA … r/soccer, r/nba).** Credentials deferred by founder 2026-06-20; the collector
still attempts and fails every cycle. Twitter/X: 12h cadence, top-100 topics, deep pulls
movers-only (budget-capped). Guardian API key: on hold. FRED silent 20 days;
`coinmetrics_onchain` degraded (4 rows vs floor 7).

## 3. THE EMPIRICAL RECORD ON D (chronological, all sealed/committed)

1. **LED feature mining** (`audits/ledger-research/LED_FEATURE_MINING_2026-07-07.md`):
   **D=0 at first sighting for LED winners AND near-misses; D≈40 for pre-broken rows** →
   "current Dark Matter is LATE-confirmation, not early-warning." The empirical case that
   D does not currently deliver the product's thesis. LED wins were carried by M-breadth
   (median M=80 at first sighting vs 50 for near-lags).
2. **World Cup case study** (`audits/board/WORLDCUP_CASE_STUDY_2026-08-17.md`): across all
   532 stored `world_cup` cycles, `dark_matter` never exceeded 9/100; `niche_mentions` read 0
   — through an entire World Cup, with three live niche football feeds.
3. **Football-feed post-mortem** (`audits/ledger-research/FOOTBALL_FEED_POSTMORTEM_2026-08-19.md`):
   mechanism = EXTRACTION (generic n-gram shredder), not routing, not delivery. The quality
   gate leaked junk ("turns against infantino") while REJECTING real entities ("real madrid").
4. **A4 gap statement (Chairman-adopted 2026-08-19):** in any domain whose first pipe is
   Google Trends + news, the engine is structurally 1–3 weeks late. Remedy sequence RULED:
   shadow trial (2026-09-01→11-30, candidate feeds enrolled in a SHADOW ledger under sealed
   rules) → pre-registered PIT-sealed backtest → post-mortem (DONE) → GHOST trial close-out
   (**OVERDUE since ~2026-07-29**).
5. **Referee decomposition** (`audits/ledger-research/REFEREE_DECOMPOSITION_RESULTS_2026-08-20.md`):
   the Wikipedia referee is blind on precisely the niche/early cohort where D claims its edge
   (5 of 15 LED topics sub-200-views/day; 5 more too-busy-to-spike). SAME_DAY corroborates
   at 50%; LED at 0 with 14/15 SILENCE. Instrument coverage anti-correlated with the D cohort.
6. **2026-08-20 fixes (committed d4d73e0, 1473e1c — today):** three Unicode/vocabulary
   silencers PROVEN and fixed: (a) ASCII-only tokenizer deleted non-ASCII letters mid-word
   (Mbappé→mbapp); (b) `_ENTITY_RUN` anchored on ASCII [A-Z] only; (c) the quality gate's
   all-common-words rule structurally favors tech vocabulary ('nestjs' passes, 'real madrid'
   REJECTED) — opt-in `from_entity_run` exemption added. `sports_entity` extractor LIVE
   (flag on, engine v364) on the 3 football desks; Football365 URL revived (/feed 404, 0 rows
   ever → /rss 200); The Batch removed (dead feed, 0 rows ever, unnoticed — the Source
   Watchdog monitors collector blocks, not individual feeds). `_title_sig` unicode fix
   deployed (backtested: 0 quorum flips; 17.9% of news titles are non-ASCII and previously
   all collapsed to ONE empty signature — non-English coverage could never corroborate).
   Tech filter removed from general-purpose platforms (WordPress tags, Blogger search terms,
   socialcrawl seeds 6→12 domains).

## 4. WHAT THE GOAL REQUIRES (the founder's stated objective)

"Identifying items and movement BEFORE they trend." The accuracy ledger is the arbiter:
current headline = tracked-race rate 26.9% (blended 10%); LED wins exist but D contributed
0 at their first sighting. The question is NOT whether D exists — it is whether D can be made
to LEAD: what sources, mechanisms, weights, and validation would make the D pathway the thing
that finds attention 1–3 weeks before Google/news, measurably, without circularity or
score inflation.

## 5. CONSTRAINTS (non-negotiable, from canon)

§16 five-gate onboarding for ANY new source (TYPE→ENGINE→FORMAT→CURRENCY+ACCESS→TEST);
score-affecting changes need backtest-before-ship; expert tier carries the corroboration-floor
exemption so extraction precision is an integrity requirement; §16a cold-start posture for
any universe expansion; the ledger is held-out and never feeds scores; N never feeds D or
detection; budget context: Apify clock-slot rule, X post budget 4,800/mo, total cost cap
$700/mo (Cost Sentinel), socialcrawl £15/2,500 credits.

## 6. FILES THE BOARD MAY READ (read-only)

`transfer/dual_pathway.py` (router, quorum, breadth) · `transfer/blog_collectors.py`
(rosters, extractors) · `transfer/discovery_collectors.py` (socialcrawl/firecrawl) ·
`transfer/gravitational_anomaly_detector.py` (quality gate ~L1879, entity runs ~L1939) ·
`CLAUDE.md` §13–16a · `audits/DEFERRED_ITEMS.md` (A4-SEQ, ACC-LC) ·
`audits/ledger-research/LED_FEATURE_MINING_2026-07-07.md` ·
`audits/ledger-research/FOOTBALL_FEED_POSTMORTEM_2026-08-19.md` ·
`audits/board/WORLDCUP_CASE_STUDY_2026-08-17.md` ·
`audits/ledger-research/REFEREE_DECOMPOSITION_RESULTS_2026-08-20.md`
