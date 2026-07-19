# FREE-SOURCE FAST-LANE RECHECK — Design + Backtest (2026-07-19)

**Read-only research (founder-ordered, backtest-before-ship).** No code changed, no git
writes, no paid pulls, no SQL — evidence gathered exclusively from the live engine's
public endpoints (`/accuracy/ledger`, `/accuracy/ledger/detail`), the free Wikimedia REST
pageviews API, and the free Google daily-trending RSS. This document is the ONLY file
written by this task. Nothing here changes a verdict, a score, or a stored row.

**Origin:** `audits/ledger-research/LED_FEATURE_MINING_2026-07-07.md` finding 3 — 5 of 15
near-miss LAGGED rows lost their race by only 1–2 days; recommendation G proposed a
free-source fast-lane recheck. This is that proposal's design + backtest.

---

## 0. Executive summary (the honest one)

1. **The lane is buildable, $0-marginal, and integrity-safe** — it only *triggers* an
   earlier check inside the existing 4 paid clock slots and records corroborating
   metadata. Google Trends remains the sole judge of LED/LAGGED, untouched.
2. **The premise as stated must be corrected before any board memo.** A recheck of
   *pending* rows — at any speed — can flip **zero** verdicts, because a verdict is
   `detection_date` vs `breakout_date`, and both are fixed historical facts by the time
   any sweep runs. The mining doc's "flips the 1–2-day losses" mechanism is **earlier
   DETECTION** (scoring/enrollment side — GHOST_FEEDS, collect cadence), not earlier
   validation. Conflating the two would be selling a hit-rate fix the lane cannot deliver.
3. **What the backtest shows the lane genuinely buys** (n=19 near-miss rows, 9 with
   usable Wikipedia coverage):
   - **Earlier surfacing: 8 of 9** covered rows would have been flagged by a daily free
     check **0–20 days before the paid sweep actually resolved them (median 8 days)**.
   - **Match-validity payload: 4 of 9** covered verdicts are contradicted or softened by
     the independent Wikipedia referee (2 outright "we actually led", 2 "same-day tie") —
     exactly the artifact class the 2026-07-07 match-validity work exists to name.
   - **The 1–2-day losses are mostly REAL.** Of the five 1–2-day losers with coverage,
     Wikipedia *confirms the loss* in 4 (wally funk, Tay Keith, claude mythos,
     Juneteenth) and ties in 1 (2026 NBA draft). The free source does **not** rescue
     them — it corroborates that the fix for those races is earlier detection.
4. **Strict flip count: 0 of 19.** "Would-have-surfaced-earlier" count: **8 of 19**
   (42% of the near-miss cohort; 8 of the 9 with coverage).
5. **Verdict:** merits a board gate — but **re-scoped as a resolution-latency +
   match-validity lane**, not a tracked-race-rate fix. Expected direct rate impact: ~0.

---

## 1. Context read (what governs this design)

- **Sweep today** (`transfer/gravitational_anomaly_detector.py` ~L5411–5528,
  `transfer/accuracy_ledger_enhanced.py`): cron at `LEDGER_SWEEP_CRON_HOURS`
  (00/06/12/18 UTC) **:45**, `LEDGER_SWEEP_LIMIT=8` rows/run, oldest-checked-first
  rotation, timeout rows resolve free, `_apify_sweep_budget_ok` guard,
  `LEDGER_SWEEP_NEWEST_SLOTS=2` live (2 of 8 slots reserved for newest, 24h cooldown —
  board condition 2026-07-07).
- **Live pool (2026-07-18):** 1,114 pending vs 32 paid checks/day → a given pending row
  is re-examined roughly every **~35 days**. Blended honest rate 9.2%; tracked-race
  24.2% (n=33); 8 LED / 6 SAME_DAY / 19 near-miss LAGGED / 54 pre-broken / 0 FP.
- **§14 rules honored by this design:** patience window 365d (never conclude failure
  early); asymmetric match window (back 30d / forward 365d); Apify clock-slot hard rule
  (ALL paid pulls only at the 4 slots — the lane adds **no** pull and moves **no** pull
  off-slot); match-validity metadata (`sweep_query`, `query_ambiguous`,
  `referee_corroborated`) is the precedent this lane extends.
- **Rotation mechanic the design exploits:** the sweep orders by
  `(last_checked IS NULL) DESC, last_checked ASC` — a row with `last_checked=NULL` goes
  to the **head** of the next paid run. A trigger can therefore promote a row using an
  existing, already-audited mechanism, with zero sweep-code change.

## 2. Design — the FREE-SOURCE FAST-LANE RECHECK

**One-line contract:** a free, held-out daily scanner that watches *young* pending
detections for evidence their Google race has concluded, and — when it fires —
**promotes** the row into the next existing paid clock slot and stores corroborating
metadata. It never fetches from Apify, never writes `accuracy_ledger`, never computes a
verdict, never touches scoring.

### 2.1 What runs, when
- New held-out module (e.g. `transfer/fastlane_recheck.py`), scheduled like the other
  aux jobs: **every 6h at :10 UTC** — deliberately OFF the :30/:45 paid slot family, so
  a fired trigger is picked up by the *next* :45 sweep (≤ 6h35m later). All fetches are
  free, so cadence is a load question only (Wikimedia asks for a descriptive UA, which
  the referee already sends).

### 2.2 What it reads (free only)
1. **Scan set:** pending rows with `status='pending'` and
   `detection_date ≥ today − FASTLANE_RECENT_DAYS` (default **21**) — the cohort whose
   race is plausibly live. Older rows are patience-window waiters; the 365d rule stands.
   Capped at `FASTLANE_SCAN_LIMIT` (default **40**) per run, oldest-unscanned-first.
2. **Wikipedia pageviews (Wikimedia REST, free, no key):** resolve topic → article via
   the *existing* `referee_wikipedia.resolve_article` (quarantine-on-no-match, never
   guess); fetch daily views `detection−45d → today`; **no-lookahead baseline** = mean of
   the lowest-40% of pre-detection days; **breach** = a day ≥ max(3× baseline, 200 views)
   on/after `detection−2d` (the frozen `wiki-v2-2026-06-23` referee params, reused —
   no new tunables). Cache resolutions (incl. unresolved) so opensearch is hit once per
   topic, not per run.
3. **Google daily-trending RSS** (`trends.google.com/trending/rss?geo=US`, free, no key,
   verified reachable 2026-07-18, ~10 items): fetched **once per run**, token-matched
   against the scan set's `topic_display`s. A match = "Google itself says this is
   trending today" — the strongest free hint the race has concluded. (Note: the RSS is
   current-day-only and has no archive, so it is design-forward, not backtestable — §4.)

### 2.3 What a trigger does (and does NOT do)
- Writes one row to a new, held-out log table `fastlane_recheck_log`
  (`topic_key, detection_date, triggered_at, source ∈ {wiki, rss}, evidence_json`) —
  audit trail + cooldown state, restart-safe.
- **Promotes** the row: `UPDATE pending_detections SET last_checked=NULL` — the row
  leads the next :45 paid sweep's rotation. That is the *entire* actuation surface.
- Caps + cooldown (board-pattern, mirrors the NEWEST_SLOTS conditions):
  `FASTLANE_TRIGGER_MAX` = **2** promotions per run (so of the 8 paid slots, ≤2 are
  fast-lane, 2 are newest-reserved, ≥4 remain pure rotation — the tail never starves);
  `FASTLANE_COOLDOWN_H` = **72** per topic (a still-pending promoted row cannot re-claim
  a slot for 3 days).
- **Never:** calls Apify, adds a 5th slot, resolves a verdict, writes `accuracy_ledger`,
  touches `velocity_scores` or any scoring path, or deletes anything.

### 2.4 Metadata (the second, equal deliverable)
At report time (read-only join in `/accuracy/ledger/detail`), a resolved row whose
`(topic_key, detection_date)` appears in `fastlane_recheck_log` is served with
`fastlane_triggered: true` + trigger source/date. Optionally the sweep may stamp
`provider='sweep_fastlane'` on promoted rows — a one-word change; the join keeps the
build strictly additive if preferred.

### 2.5 Env flags + rollback
- `FASTLANE_RECHECK=0` **default OFF** (flag-never-force; founder flip after board gate).
- `FASTLANE_SCAN_LIMIT=40`, `FASTLANE_RECENT_DAYS=21`, `FASTLANE_TRIGGER_MAX=2`,
  `FASTLANE_COOLDOWN_H=72`.
- **Rollback = unset the flag.** Residue: inert log-table rows and some
  `last_checked=NULL`s (a one-time rotation reorder the sweep already handles — NULLs
  are the normal state of never-checked rows). No stored verdict, score, or date is ever
  altered, so rollback is complete by construction.
- **`param_version`** gains a `|fastlane1` token while the flag is ON (the 2026-07-08
  board convergence: no published rate may silently span a measurement-policy change).

## 3. Backtest — would a daily free check have surfaced these races earlier?

**Method.** Pulled `/accuracy/ledger/detail?verdict=LAGGED` (2026-07-18): 73 LAGGED rows,
**19 served `pre_broken=false`** (near-misses — the population grew from the mining doc's
15). For each: resolved the topic against Wikipedia (opensearch, quarantine-on-no-match),
fetched daily pageviews `detection−45d → breakout+21d`, computed the **no-lookahead**
baseline (lowest-40% mean of strictly-pre-detection days; threshold = max(3×, 200) —
frozen referee params), then simulated a daily checker: first breach day on/after
`detection−2d`, surfaced at **breach+1d** (honest Wikimedia publication lag). Compared
against the sweep's actual `validated_at`.

### 3.1 Per-row evidence (all 19 near-miss rows)

| Topic | Google lead | Detected | Google breakout | Sweep resolved | Wiki breach (day it crossed 3×/200) | Free lane would surface | Days before the sweep | Wiki vs our detection | Reading |
|---|---|---|---|---|---|---|---|---|---|
| wally funk | −1 | 07-10 | 07-09 | 07-16 | 07-09 (13,257 vs thr 251) | 07-10 | **6** | −1 | **Loss confirmed** by referee |
| us and iran | −1 | 06-15 | 06-14 | 07-11 | — | — | — | — | Unresolved (no confident article) |
| wimbledon semi final | −4 | 07-09 | 07-05 | 07-10 | — | — | — | — | Unresolved |
| Tay Keith | −1 | 06-19 | 06-18 | 07-09 | 06-18 (174,284 vs 571) | 06-19 | **20** | −1 | **Loss confirmed** |
| congo | −4 | 06-13 | 06-09 | 07-03 | 06-17 (1,788 vs 469) | 06-18 | **15** | **+4** | **Referee contradicts** — wiki arrived AFTER our call (bare-geo ambiguous query) |
| socialist melat kiros | −1 | 07-01 | 06-30 | 07-03 | — | — | — | — | Unresolved |
| Aldon Smith | −2 | 06-15 | 06-13 | 07-01 | — | — | — | — | No pageview data (REST 404) |
| Curaçao | −1 | 06-14 | 06-13 | 07-01 | — | — | — | — | Unresolved — stored display is mojibake ("CuraÃ§ao"), which also defeats resolution |
| panama england | −4 | 06-27 | 06-23 | 06-29 | — | — | — | — | Unresolved |
| budapest pride | −7 | 06-27 | 06-20 | 06-28 | 06-27 (941 vs 200) | 06-28 | 0 | **0** | **Referee contradicts** — wiki surge = our detection day; Google likely matched an earlier micro-surge |
| ocarina time | −5 | 06-14 | 06-09 | 06-27 | 06-12 (8,688 vs 4,083) | 06-13 | **14** | −2 | Loss confirmed (smaller than Google's −5) |
| kimi | −6 | 06-13 | 06-07 | 06-27 | no surge | — | — | — | Article "Kimi" is generic — resolution too weak to read |
| access to fable | −4 | 06-13 | 06-09 | 06-26 | — | — | — | — | Unresolved |
| 2026 NBA draft | −2 | 06-22 | 06-20 | 06-25 | 06-22 (18,905 vs 9,941) | 06-23 | **2** | **0** | **Referee ties it** — wiki surge on our detection day |
| ai agents | −5 | 06-02 | 05-28 | 06-24 | — | — | — | — | Unresolved |
| claude mythos | −1 | 06-10 | 06-09 | 06-24 | 06-08 (2,549 vs 582) | 06-09 | **15** | −2 | **Loss confirmed** (wiki even earlier than Google) |
| world models | −3 | 06-09 | 06-06 | 06-23 | 06-16 (527 vs 514) | 06-17 | **6** | **+7** | **Referee contradicts** — wiki says we LED by 7 (churning topic) |
| Juneteenth | −2 | 06-13 | 06-11 | 06-20 | 06-11 (23,712 vs 8,600) | 06-12 | **8** | −2 | **Loss confirmed** |
| model context protocol | −6 | 06-02 | 05-27 | 06-18 | no surge (steady-high traffic never 3×) | — | — | — | No readable surge |

### 3.2 Counts (n = 19)

- **Coverage:** 9 usable (47%) · 7 unresolved (37%) · 1 no-data · 2 no-surge. The
  free lane simply cannot see ~half of this cohort — consistent with the referee's known
  ~38% no-coverage on niche-early topics.
- **Earlier surfacing: 8/9 covered rows (42% of all 19)** would have been surfaced by a
  daily free check before the paid sweep actually resolved them — median **8 days**
  earlier, max 20, min 2 (budapest pride: 0 — the sweep happened to run the next day).
- **Strict verdict flips a recheck could have produced: 0/19.** Both dates in every
  verdict were fixed before any sweep ran. This is a feature of the ledger's integrity,
  not a flaw of the lane.
- **Referee-contradicted verdicts (artifact candidates): 4/9** — congo (+4),
  world models (+7), budapest pride (0), 2026 NBA draft (0). Two of these carry the
  known weak-match signatures (bare geo; churning topic). These rows are where the
  *match-validity metadata* earns its keep: the published near-miss count is honest, but
  4 of the 9 measurable races may not have been losses at all.
- **The 1–2-day losers (the mining doc's flip candidates): 9 rows in today's cohort;
  5 covered; 4 losses CONFIRMED by the independent referee, 1 tie.** The free source
  refutes, rather than supports, the idea that faster validation flips them: those races
  were lost at detection time. The flip lever is **earlier detection_date** — the
  GHOST_FEEDS expert/niche expansion (live as a monitored trial since 2026-07-15) and
  collect/enrollment cadence — exactly mining finding 1.

### 3.3 What earlier resolution IS worth (the real, smaller claim)

- **Granularity fairness (forward-looking):** at 1,114 pending vs 32 paid checks/day,
  rotation latency is ~35 days and growing. Rows swept >90 days after detection fetch
  weekly-granularity Trends curves, where a breakout date carries ±3d error — larger
  than the entire near-miss margin. All 19 rows here were swept inside the daily-
  granularity window; as the pool ages, that stops being true. A trigger that gets a row
  swept near its event keeps the race measured at daily resolution.
- **Symmetric by construction:** the trigger fires on the free-source *surge*, blind to
  whether we led or lagged. In this backtest, **5 of the 8 earlier-surfaced rows were
  losses** — the lane accelerates the recording of losses at least as much as wins. It
  is not a win-harvesting mechanism.
- **Fresher published record:** wins AND losses enter the public ledger a median ~8 days
  sooner for covered topics — an institutional-credibility gain (the ledger is the moat),
  not an accuracy gain.

## 4. Verdict-timing fairness (the required disclosure)

**Does the lane change race conditions?** The race itself — `detection_date` vs the true
Google breakout — is over before any recheck runs; the lane cannot start, speed, or bias
a race. What it changes is **when a concluded race is measured and which rows are
measured first**. Three bias channels, each named and mitigated:

1. **Coverage bias.** Wikipedia resolves ~47% of this cohort and the RSS skews
   mainstream — so triggered rows skew toward covered/mainstream topics, while the
   uncovered niche-early rows (the thesis cohort) stay on plain rotation. *Mitigations:*
   trigger cap ≤2 of 8 slots (≥4 always pure rotation); publish the tracked-race rate
   segmented by `fastlane_triggered` so a coverage-correlated shift is visible, never
   blended silently.
2. **Measurement-fidelity asymmetry.** Triggered rows get daily-granularity curves near
   the event; long-waiting rows can degrade to weekly granularity (±3d). The lane
   *reduces* error for covered rows and leaves it for uncovered ones → verdict noise
   becomes coverage-correlated. *Disclosure:* stamp and segment (above); the complete
   fix is sweep-throughput, a budget question outside this $0 lane.
3. **Point-in-time composition.** Earlier resolution pulls wins and losses into the
   published rate sooner; a reader comparing rates across the flip date sees a
   composition shift, not a performance shift. *Mitigation:* `param_version` gains
   `|fastlane1` (the board's stamp-every-definition rule), and the report serves a
   `fastlane_triggered` count.

**Net fairness statement for the board:** because verdicts are date-vs-date and the
trigger is surge-symmetric, the lane cannot inflate the tracked-race rate by design; the
only honest concern is *composition visibility*, fully handled by stamping + segmentation.

## 5. Threats to validity (this backtest)

- **Small n:** 19 near-miss rows, 9 measurable. Directional, like the mining doc.
- **Resolution done today:** article titles/redirects were resolved 2026-07-18, not on
  the detection dates — a topic renamed since could mis-resolve (quarantine makes the
  failure mode "no data", never a wrong curve).
- **No-lookahead is honored for the baseline, not the calendar:** the simulated daily
  checker assumes Wikimedia data available at breach+1d; occasional 24–48h publication
  lag would cost one more day on some rows (would not change any conclusion above; the
  median earlier-surfacing margin is 8 days).
- **The RSS half of the lane is unbacktestable** (no historical archive) — its value is
  asserted from design (Google itself announcing the breakout), not measured. Treat it
  as a bonus trigger, not the load-bearing one.
- **Wikipedia is an attention proxy, not ground truth** — fine for a *trigger* (it only
  needs to correlate with Google), and its independence from our scoring inputs is what
  makes the contradiction metadata meaningful; but a wiki-silent breakout (7 unresolved
  + 2 no-surge rows here) is invisible to the lane.
- **Six of the 19 rows are `v1_engine`-epoch detections** (pre pg:copy boundary) — the
  forward population may behave differently; re-run on the first-crossing cohort as it
  resolves (same instruction as the mining doc).
- **Incidental defects observed (not fixed — read-only task):** stored display
  "CuraÃ§ao" is mojibake (breaks free-source resolution AND likely weakens its Trends
  sweep query); "kimi" resolves to a generic disambiguation-grade article (mirrors the
  `query_ambiguous` class). Both are pre-existing data-quality items, not lane issues.

## 6. Cost analysis

- **Marginal spend: $0.** Per run: ≤40 Wikimedia pageview GETs + ≤40 (cached, one-time)
  opensearch GETs + 1 RSS GET — all free, no keys, UA declared, trivially inside
  Wikimedia's anonymous limits. Four runs/day ≈ ≤160 free requests.
- **Apify: unchanged by hard design.** No new pull, no 5th slot, no cadence change; the
  budget guard and `LEDGER_SWEEP_LIMIT=8` are untouched. The lane only *re-orders* which
  8 rows an already-scheduled slot examines. (Second-order: promoted rows are less likely
  to be already-timed-out free-resolves, so the *share* of the 8 that spend a fetch could
  tick up marginally; the cap and the budget guard bound it exactly as today.)
- **Engine load:** one small SELECT over `pending_detections` (indexed by status), ≤2
  single-row UPDATEs, and log-table inserts per run — negligible; batch-pacing rules
  don't apply (no heavy build).

## 7. Honest verdict — does it merit a board gate?

**Yes — but only under the corrected claim.** Recommend convening the board on:

> *"Fast-lane recheck: a $0, flag-gated, held-out lane that (a) gets covered races
> measured a median ~8 days sooner at daily granularity inside the existing 4 paid
> slots, and (b) attaches independent match-validity evidence that already contradicts
> 4 of the 9 measurable near-miss verdicts. Expected direct tracked-race-rate impact:
> ~zero flips — it is a measurement-latency and verdict-quality improvement, not an
> accuracy improvement."*

Do **not** bring it to the board as the mining doc's "flips the 1–2-day losses" — this
backtest affirmatively shows those losses were real (4 confirmed, 1 tie, 0 refuted among
the covered 1–2-day rows) and the flip lever is earlier detection (GHOST_FEEDS trial +
enrollment cadence), already in flight. If the board weighs priorities: the GHOST_FEEDS
trial readout is the higher-leverage item; this lane is a cheap, safe complement whose
strongest single deliverable may be the referee-contradiction metadata on near-misses —
a direct extension of the 2026-07-07 match-validity layer the board already approved.

*Backtest artifacts (scratchpad, session-local, not committed): `fastlane_backtest.py`,
`lagged.json`, `backtest_results.json`. All numbers reproducible from
`/accuracy/ledger/detail?verdict=LAGGED` + Wikimedia REST with the frozen referee params.*
