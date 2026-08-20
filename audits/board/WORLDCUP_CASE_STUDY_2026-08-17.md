# The FIFA World Cup Trend Family — Full Lifecycle Case Study
*Chairman-commissioned · 2026-08-17 · read-only reconstruction from the platform's own live data + audit records*

> ## ⚠ CORRECTION NOTICE — issued 2026-08-19 (Chairman-ordered, A1)
> **Defect found by the Challenger seat** (`BOARD_worldcup-casestudy_2026-08-18.md`): this study
> quoted "mexico world cup … det **38.5→70**" in Q5 and Q7/Q8 while its own Q1 table records that
> topic's all-time peak served detection as **48.96** across 222 cycles. A served detection of 70
> is impossible against that ceiling, and the two figures sat in the same register as though both
> were served data.
>
> **Reconciled — they measure different things, and neither number is wrong:**
> - **48.96** is the real, SERVED peak from stored history (`topic_lifecycle` / `velocity_scores`).
> - **38.5→70** is a **VALIDATION-HARNESS read** from `GET /research/mainstream-v2` on 2026-06-26,
>   which is held-out and changes no score. Critically, that endpoint **pins `expert_detection` at
>   a fixed 70 reference by design** ("so the PATHWAY/weight shift is the meaningful output").
>   The "70" is therefore that synthetic constant surfacing once the topic is demoted to the
>   expert/dark-matter pathway — **not a score the engine ever served, and not a prediction that it
>   would**. The meaningful content of the comparison is the DIRECTION (sub-quorum ⇒ demotion to
>   the trigger pathway ⇒ Detection rises off the mainstream floor), never the magnitude.
>
> Both passages below are corrected in place and marked. **Standing rule this establishes:**
> harness/what-if reads are never printed in the same register as served values; they carry their
> source and their fixed-reference caveat, every time.
*Doctrine under test: "If it is trending on Google, it is not dark matter but more likely already trending; if news sources confirm in addition to Google Trends, it is very likely already mainstream."*

---

## Data provenance (what this study is built from)

| Source | What it provided |
|---|---|
| Live engine `GET /history/{key}` (topic_lifecycle) | first sighting, cycle counts, peaks, persistence for 8 family topics |
| Live engine `GET /scores/{key}/score-history?limit=1000` | 532 stored cycles for `world_cup` (2026-06-13 → 2026-08-18 UTC), 500 for `fifa_world_cup` |
| Live engine `GET /scores/world_cup` | current pathway components (G/I/M/D/C/P/N) |
| Live engine `GET /accuracy/ledger/detail` | 7 resolved world-cup-family ledger rows with verdicts |
| Live engine `GET /research/mainstream-v2` (internal key) | live v1-vs-v2 mainstream quorum read for "world cup" |
| Live engine `GET /scores?limit=100` + `/topics?limit=100` | today's leaderboard (exit evidence) |
| Repo: `CALIBRATION_FIFA_ANALYSIS.md` (2026-06-15) | the "World Cup is invisible" root-cause audit |
| Repo: `transfer/dual_pathway.py`, `transfer/discovery_collectors.py` | the mechanism headers (WC as motivating case) |
| Repo: `SESSION_LOG.md`, `CONSOLIDATION_CHECKPOINT_2026-06-15.md`, `CLAUDE.md` §15 | dated build/validation records |

**Honest gaps (nothing below is fabricated):**
- Stored score rows begin **2026-06-13**; the 2026-06-08→06-12 cycles (v1-engine epoch, pre-consolidation) are not in the served score archive. First-sighting dates for that window come from `topic_lifecycle.first_detected_at` and the ledger rows (epoch `v1_engine`).
- The ledger pairs `detection_date` = first sighting with `detection_score` = the floor-crossing (peak) score — the score actually *served* on 06-08 is not retrievable, but the 06-13→06-22 archive shows it was ~41.
- `/trending` returned a Heroku application error (H12-class) during this study; leaderboard absence was verified via `/scores?limit=100` and `/topics?limit=100` instead.
- Wikipedia-referee corroboration is `null` (unchecked) on all family ledger rows — they resolved before the referee shipped and are honestly labeled unchecked.
- "134 outlets" is the recorded 2026-06-26 validation figure; the live 2026-08-17 read is 8 independent outlets (decay is real, both figures are quoted with their dates).

---

## Q1. Timeline — first sighting, rise, peak, decay, today

### First sightings (topic_lifecycle, live)

| topic_key | first_detected_at (UTC) | last_scored_at | cycles | cycles ≥ breakout | peak overall | peak detection |
|---|---|---|---|---|---|---|
| world_cup | **2026-06-08 00:47** | 2026-08-18 05:48 | 755 | 120 | **96.45** | **94.75** |
| erling_haaland | 2026-06-08 01:14 | 2026-08-18 05:39 | 376 | 2 | 85.49 | 89.51 |
| fifa_world_cup | 2026-06-08 11:51 | 2026-08-14 07:55 | 701 | 89 | 92.94 | 88.22 |
| mundial | 2026-06-09 17:57 | 2026-08-18 05:43 | 590 | 0 | 70.70 | 60.51 |
| mexico_world_cup | 2026-06-12 23:46 | **2026-07-10** (dead) | 222 | 0 | 64.23 | 48.96 |
| haaland | 2026-06-13 00:45 | 2026-08-01 | 334 | 0 | 84.21 | 88.41 |
| final_del_mundial | 2026-07-07 02:14 | 2026-08-13 | 93 | 0 | 70.69 | 62.59 |
| golden_boot | 2026-07-19 03:04 | **2026-07-21** (dead, 18 cycles) | 18 | 0 | 14.0 | 11.3 |
| world_cup_soccer | — no history found (never a topic key) | | | | | |

Real-world anchor: the 2026 World Cup ran **June 11 → July 19** (final). Google Trends breakout (per the ledger's own sweep): **May 22–30**.

### The score arc of `world_cup` (532 stored cycles, daily max)

| Phase | Dates | Overall | Detection | Stage | Mentions/day (max) |
|---|---|---|---|---|---|
| **Under-scored plateau** | 06-13 → 06-22 | 41–42 | ~25 | WATCHING | up to **689** (06-15) |
| **First breakout** (recall fix + group stage) | **06-23** → 06-27 | **96** | **95** | BREAKOUT | 104→718 |
| Group-stage trough | 06-28 → 07-04 | 40–67 | 24–57 | WATCHING/EMERGING | 330–590 |
| Knockout burst | 07-05 → 07-08 | 96 | 95 | BREAKOUT | 350–520 |
| Between rounds | 07-09 → 07-14 | 40–41 | 24 | MONITORING | 170–470 |
| **Semis + FINAL (Jul 19)** | **07-15 → 07-21** | 93–96 | 90–95 | BREAKOUT | 230–574 |
| **Post-final collapse** | 07-22 → 07-28 | 39–42 | 24–25 | MONITORING | 509→75 |
| Aftermath echo | 07-29 → 08-02 | 93–95 | 88–91 | BREAKOUT | only 90–194 |
| **August decay** | 08-03 → 08-18 | mostly 39–41 (spikes 56–80) | mostly 23–25 | MONITORING↔WATCHING flap | 61 → **23** |

**Today (2026-08-17/18):** overall 50.3, detection 37.6, confidence 63.0, stage WATCHING, 22 mentions, `current_streak_cycles: 0`. `fifa_world_cup` decayed further: last scored 08-14 at overall 26, MONITORING, 3 mentions.

Note the 06-13→06-22 plateau: the topic was **present and heavily mentioned (689 mentions/day) but scored 41** — the exact "777K Wikipedia views scoring 41" defect documented in `dual_pathway.py`'s header. The 06-23 jump to 96 is dated to the `KNOWN_CONCEPT_PHRASES` recall fix (SESSION_LOG 2026-06-23e: a pre-existing quality-gate drop of "world cup" was fixed; "'world cup' now served + scored 94.8"). So the recorded peak is part real-world arc, part instrumentation coming online mid-event.

---

## Q2. Pathway — was it EVER dark matter?

**No. It was mainstream-born, and the engine's own components say so on every cycle we can read.**

- Current components (`/scores/world_cup`, 2026-08-18): `G_gradient_strength = 0.0` (niche_mentions **0**, mainstream_mentions 22), `D_dark_matter = 0.0` (first_timer_ratio 0.0), `M_platform_diversity = 92`.
- Across all 532 stored cycles, `dark_matter` never exceeded **9/100** (typically 0–5). There is no cycle in the archive where the World Cup rode the expert/dark-matter pathway.
- Live `/research/mainstream-v2`: pathway `mainstream`, **w = 1.0**, `mainstream_confirmed: true` under BOTH v1 and v2 rules (8 independent outlets today; **134 outlets** at the 2026-06-26 validation).
- `dual_pathway.py` (the mechanism, verbatim intent): the World Cup was the **motivating case** for the dual-pathway fix — a fragmented news n-gram ("iran announce deal") scored 47/ANOMALY while "FIFA World Cup" at 777K Wikipedia views scored 41, because Detection was ~60% G+D (both reward expert origin) and discovery/news feeds are tagged `platform_tier=mainstream` (niche ratio ~0 → Detection floored). The fix: `detection = (1-w)·expert + w·mainstream`, where the mainstream pathway scores honest absolute **magnitude + breadth + acceleration**. At w=1.0 the World Cup is judged as what it is — a mainstream-origin consumer trend.
- The `_soft_cap` in the same file records a second WC-driven fix: FIFA and "obama" both hard-pinned at 100 and were unrankable until the order-preserving soft ceiling was added.

**Doctrine reading:** the engine's own architecture agrees with the Chairman. A topic arriving via Google-Trends discovery and news feeds enters at `platform_tier=mainstream`, lands in the gradient's denominator, and produces G≈0, D≈0 — *structurally* "not dark matter." The dual-pathway fix did not make the WC dark matter; it made the engine stop mis-scoring an already-mainstream trend as if a niche ratio were the only truth.

---

## Q3. Stages vs the real-world arc

| Real-world event | Engine stage response |
|---|---|
| Qualifiers/run-up (May) | Not on radar at all (see Q8) — Google broke out May 22–30 with zero engine coverage |
| Opening (Jun 11) → group stage | WATCHING at 41 (under-scored; `fifa_world_cup` variant did hit BREAKOUT 06-16–17, det 84, immediately after the 06-15 dual-pathway/news-calibration ship) |
| Group→knockouts (Jun 23–27) | BREAKOUT 96 (recall fix live) — 53-cycle longest streak begins here |
| Knockout rounds (Jul 5–8) | BREAKOUT 96 |
| Semis + Final Jul 19 | BREAKOUT 93–96 through **Jul 21** |
| Post-final (Jul 22+) | Immediate drop to MONITORING ~41 within 1–2 cycles |
| Aftermath (late Jul/Aug) | Echo BREAKOUTs on thin mentions (90–194), then MONITORING↔WATCHING flap, mentions → 23 |

The stage machinery tracked the tournament arc *once the topic was properly served*, and the post-final exit was fast (BREAKOUT → MONITORING in ~2 days). Two honest defects in the record: (a) intra-day stage flapping (BREAKOUT and MONITORING on the same day) from serve-time recalculation; (b) `final_del_mundial` det **frozen at 62.59 for 6 straight cycles** while mentions varied 10–16 — caught by the assessor (2026-07-18/19), decomposed to byte-identical M/I/P components, and closed as freeze-mechanism instance #2, later a clean out-of-sample win for the freeze-detection instrument.

---

## Q4. The Accuracy Ledger's verdict — was the system honest?

All seven world-cup-family resolutions in `/accuracy/ledger/detail`:

| topic | detection_date | det score | Google breakout | lead (days) | verdict | pre_broken | epoch |
|---|---|---|---|---|---|---|---|
| world cup | 2026-06-13 | 94.75 | 2026-05-22 | **−22** | LAGGED | true | v1_engine |
| world cup (re-sweep) | 2026-06-08 | 94.75 | 2026-05-30 | **−9** | LAGGED | true | v1_engine |
| FIFA | 2026-06-13 | 93.74 | 2026-05-26 | **−18** | LAGGED | true | v1_engine |
| 2026 fifa world | 2026-06-13 | 90.02 | 2026-05-26 | −18 | LAGGED | true | v1_engine |
| 2026 fifa world (re-sweep) | 2026-06-10 | 90.02 | 2026-06-02 | −8 | LAGGED | true | v1_engine |
| socceroos | 2026-06-11 | 89.23 | 2026-05-29 | −13 | LAGGED | true | v1_engine |
| haaland | 2026-06-17 | 88.33 | 2026-06-04 | −13 | LAGGED | true | v2_engine |

**Every row is LAGGED and every row is `pre_broken` — Google broke out 8–22 days before the engine's first sighting.** The player topic (haaland) fared no better than the tournament (−13d).

The system was honest about it, in layers:
1. **Maturity segmentation** (2026-06-26): the honest report was rebuilt because ESTABLISHED topics "(world cup etc.) can only LAG" were polluting the denominator; the headline became the EMERGING early-detection cohort, with everything still reported.
2. **Pre-broken split** (2026-07-07): breakout >7d before first sighting = "cold-start, never a race" — the WC rows are the canonical members of this class (44 of 59 lagged rows were pre-broken).
3. **First-crossing enrollment**: leaderboard-top-N enrollment was abandoned precisely because already-big topics like the WC are *structurally* LAGGED — the old query measured coverage latency, not the thesis.
4. **Wikipedia-referee study** (2026-06-23d): FIFA was found "2–30 days AFTER its Wikipedia surge — a DISCOVERY-LATENCY gap, NOT a scoring false-early." The system attributed the miss to its own collection blind spot rather than claiming the detection.

---

## Q5. Corroboration machinery — Mainstream v2 quorum + lexicon

- **Mainstream v2** (`MAINSTREAM_V2=1`, live 2026-06-26; NEWS_QUORUM_V2=5, syndication-collapsed `min(distinct outlets, distinct titles)`): FIFA was the validation basket. "world cup" at **134 independent outlets** stayed mainstream (w=1.0) — quorum vastly exceeded. Thin-credible **"mexico world cup" (5→4 stories) demoted to a dark-matter TRIGGER** — the doctrine's boundary case: a few news stories do NOT make a topic mainstream; five distinct outlets do. *(CORRECTED 2026-08-19 — see the correction notice at the top: the previously-printed "det 38.5→70" was a validation-harness read whose "70" is that endpoint's FIXED `expert_detection` reference, not a served score. The topic's real served peak detection was **48.96**. The demotion DIRECTION is the finding; the magnitude was never a served value.)*
- **Common-word filter** (2026-06-15): "fifa" was explicitly kept (proper noun) while junk common words were purged — the family survived the quality purge.
- **KNOWN_CONCEPT_PHRASES recall whitelist** (2026-06-23e): fixed a pre-existing quality-gate drop of "world cup"; it re-entered `/scores` at 94.8 the same day.
- **Situation model** (2026-06-23e, held-out): "japan" hub-clustered into 3 separate situations, one of them world-cup — evidence the family bled into country-name blobs.
- **WC-2026 lexicon cluster** (2026-07-05/06, Agent-6 worklist): worldcup / mundial / golden boot / usmnt / haaland / manchester united / balogun / vozinha routed to sports to drain the catch-all (the earlier 77%→56% drain figure "predates the World Cup surge" — the WC materially congested the catch-all). Policy held: bare countries stay out (situation layer routes them). Serve-time category today: `world_cup → sports`. ✓
- Current corroboration state: 8 independent outlets, still ≥5 quorum → `mainstream_confirmed` even in decay.

---

## Q6. Decay and exit — is "no longer a trend" visible in our data?

Yes, on five independent instruments:

1. **Mentions**: 689/day (06-15 peak) → 574 (final week) → **23** (08-17). A ~97% collapse.
2. **Scores**: overall 96 (peak) → 50.3 today (det 37.6); `fifa_world_cup` → 26; stage MONITORING↔WATCHING.
3. **Leaderboard exit**: in today's `/scores?limit=100` and `/topics?limit=100`, the ONLY family member present is bare "fifa" at **rank #100** (55.6, WATCHING). `world_cup` itself is off the top-100 entirely.
4. **Streaks**: `current_streak_cycles: 0` vs `longest_streak_cycles: 53` (the tournament); persistence_rate 0.20 and falling.
5. **Family die-off**: `mexico_world_cup` last scored **2026-07-10** (dead pre-final), `golden_boot` lived 18 cycles (07-19→07-21, peak 14 — post-event fragment, never a trend), `final_del_mundial` last scored 08-13, `haaland` last scored 08-01. The periphery died before the core.

The maturity system classes long-sustained topics ESTABLISHED (≥14 sustained days) and discounts them; the WC family is exactly the class the discount exists for.

---

## Q7 + Q8. The doctrine test — including the news-collector origin question

### Q8 first: how the World Cup got on the radar at all

The Chairman's recollection is confirmed by the dated record, with one important refinement about which pipe carried it:

- **Before June 2026 the engine could not see the World Cup at any price.** `CALIBRATION_FIFA_ANALYSIS.md` (2026-06-15) documents three independent blinding layers: ~95% AI/tech collector coverage, tech-only extraction salience (sports headlines shredded to "fifa world", "beats mexico opening"), and expert-origin scoring (+ the AI-taxonomy floor). Google Trends existed only as a *validator of topics the engine already had* — never asked for the trending list.
- **News aggregation is what first carried the family in.** The reputable-allowlist news pipeline (newsapi_org / newsapi_ai / newsdata_io / gdelt / guardian, `_NEWS_REPUTABLE_SOURCES` + provenance tiering) was live by the 2026-06-10 build; the family's first sightings (06-08→06-13, v1-engine epoch) are news-era, pre-discovery-feed. The 06-15 audit itself notes "news IS ingested (it caught 'iran deal')" while `/trending` showed zero sports — the WC existed only as under-scored rows/fragments (the 41-score plateau in the archive).
- **Phase A discovery collectors** (`discovery_collectors.py`: Google Trends Daily Trending RSS + Wikipedia top pageviews, the audit's "single highest-ROI fix") shipped with the 06-15 consolidation; `fifa_world_cup` hit its first BREAKOUT (det 84) on 06-16–17, the next day.
- **The refinement that matters for the doctrine:** news sources did NOT enter as a dark-matter input. The D-vs-M router is `platform_tier`, and `_news_write` stamps everything `mainstream` — so the World Cup arrived on the **M pathway with D≈0 from the first retrievable cycle**. The engine never treated it as dark matter, not even for a day. (The 2026-07-07 ledger feature-mining found the same at fleet level: current Dark Matter is *late-confirmation, not early-warning* — the empirical case for the GHOST_FEEDS expert-tier expansion.)

### The doctrine, clause by clause

**Clause 1 — "If it is trending on Google, it is not dark matter but more likely already trending": CONFIRMED, by our own ledger.**
Google breakout May 22–30; our first sighting June 8–13; verdict LAGGED, lead −8 to −22 days, pre_broken on all 7 rows. By the time the World Cup was Google-trending it was not merely "likely already trending" — it was already 1–3 weeks past breakout. And the engine's D component read 0–9/100 throughout: Google-borne discovery is *structurally* not dark matter in this architecture (discovery feeds are mainstream-tier by design).

**Clause 2 — "If news sources confirm in addition to Google Trends, it is very likely already mainstream": CONFIRMED, and codified.**
By 06-26 the WC had 134 independent outlets; `mainstream_confirmed=true`, w=1.0, pathway=mainstream under both v1 and v2 rules. Mainstream v2 *is* this clause turned into an algorithm — with the crucial quantitative boundary the doctrine's prose lacks: **news confirmation is quorum-dependent.** "mexico world cup" at 4–5 stories was demoted to a dark-matter trigger *(corrected 2026-08-19: the demotion is the finding; the previously-quoted "det 38.5→70" was a harness read against a fixed 70 reference, not a served score — served peak was 48.96)*; one-to-four credible outlets is a lead to chase, not mainstream arrival. Five distinct, syndication-collapsed outlets is.

**Three complications the data adds (none refute the doctrine):**
1. **The converse failure mode.** Before the dual-pathway fix, the engine over-applied the doctrine's spirit: mainstream-born = ratio-zero = scored 41 while 777K people looked at it. "Already mainstream" correctly means "not our early-detection trade"; it must not mean "measured as nothing." The fix keeps both truths: honest magnitude on M, moat untouched on D.
2. **Scheduled mega-events are structurally pre-broken.** A World Cup has a known date; there is no dark-matter phase to catch — the ledger's pre-broken class exists to stop such rows from being counted as lost races. The plausible early plays were the periphery (players, qualifiers) — but haaland also LAGGED (−13d), because the periphery arrived through the same mainstream pipes. The early-sports signal the 06-15 audit hypothesized (breakout players, transfer rumors *before* they hit news) would require expert/niche sports sources the roster still does not carry.
3. **The miss was discovery latency, not scoring.** The Wikipedia-referee study classed FIFA as DISCOVERED_AFTER_ARRIVAL. The doctrine describes what Google-trending *means*; the WC case additionally shows what it *costs* — if the first pipe that can see a domain is Google Trends + news, the engine is by construction 1–3 weeks late in that domain, and honest labeling (LAGGED / pre_broken / ESTABLISHED-discounted) is the only defensible posture. The system did label it honestly, everywhere we checked.

### One-line verdict

The World Cup entered the engine already-trending (Google, −9 to −22d), was scored as mainstream-born from its first retrievable cycle (w=1.0, D≤9/100 ever, 134-outlet quorum), rose and fell in lockstep with the tournament (peak 96.45; BREAKOUT through the Jul 19 final +2 days), and is now measurably not a trend (mentions 689→23, off the top-100, streak 0) — the ledger records the engine's own lateness without excuse. The Chairman's doctrine is confirmed by the platform's own data, with one earned refinement: *news confirmation makes a topic mainstream only at quorum (≥5 independent outlets); below quorum it is a dark-matter trigger, and that boundary — not the prose — is what is enforced in production.*
