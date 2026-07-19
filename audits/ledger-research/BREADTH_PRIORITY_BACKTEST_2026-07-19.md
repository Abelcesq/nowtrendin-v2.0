# Breadth-at-First-Sighting Enrollment Priority — Held-Out Backtest (2026-07-19)

**Read-only research. Endpoints only** (`/accuracy/ledger`, `/accuracy/ledger/detail?limit=500`,
`/scores/{key}`, `/scores/{key}/score-history`). No SQL, no engine change, no paid pulls, no
enrollment change. The ledger is held-out: this note MEASURES; nothing here teaches or acts
without a board gate + founder sign-off.

**Proposal under test** (from `LED_FEATURE_MINING_2026-07-07.md`, finding 2): when first-crossing
enrollment (`LEDGER_ENROLL_RECENT_DAYS=14`) has more floor-crossers than slots, prioritize
candidates with HIGHER cross-platform breadth at first sighting — the mining doc found LED median
M=80 vs near-miss M=50 at first score and asked whether breadth-priority would raise the
tracked-race hit rate.

---

## 1. Data

- `/accuracy/ledger/detail?limit=500` (pulled 2026-07-19 UTC): **93 resolved rows** —
  LED 8 · SAME_DAY 6 · LAGGED 73 (near-miss 19, pre-broken 54, server `pre_broken` field,
  grace 7d) · LATE_REDETECTION 6 (excluded from races, per §14).
- Summary at pull time: blended hit rate 9.2%, **tracked-race 24.2% (8/33)**, pending 1,114,
  `param_version calib-params-v3|patience365|lead365|match30|preb7|estmin14`.
- Per-topic per-cycle history from `/scores/{key}/score-history?limit=3000` (serves stored values
  for stale rows — INV-1 — so historical numbers are the stored ones, not re-derived) plus the
  embedded 30-row `score_history` in `/scores/{key}` for `n_mainstream_platforms`.

### Breadth measure — and an honest limitation

The mining doc's "M" is the platform-diversity COMPONENT (0–100) of the first `velocity_scores`
row, read via direct DB SELECT. The endpoints do NOT serve that per-cycle: `score-history` serves
a raw **`platforms`** count (len of `platforms_active`) per cycle; `n_mainstream_platforms` is
served only in the embedded newest-30 window of `/scores/{key}`.

- **Primary metric here: raw platform count at detection** — the median of `platforms` over
  cycles inside `[detection_date − 1d, detection_date + 3d]`; sensitivity run on the EARLIEST
  cycle in that window only (no post-detection leakage).
- **Mainstream-specific breadth (`n_mainstream_platforms`) is unmeasurable for the rows that
  matter**: the embedded window reaches the detection window for only **29/93** rows — and for
  **0 of the 8 LED rows**. The mining doc's exact M metric cannot be reproduced from endpoints.
  This backtest therefore tests *breadth*-priority generally, not *mainstream*-breadth-priority
  specifically.

### Measurability (counted honestly)

Per-cycle history floors DB-wide at ~**2026-06-12/13** (several topics also hold exactly 30 rows —
a prior prune era), and 4 topics return no history at all (`curaçao`, `canadá`, `chinese_nlp`,
`implemented`).

- **Unmeasurable: 18 of 93** (no cycle within [det−1d, det+3d]): pre-broken 11, near-miss 3
  (`curaçao`, `ai_agents`, `model_context_protocol`), SAME_DAY 2 (`claude_fable`, `fable`),
  LATE_REDETECTION 2. These are mostly early-June detections that predate the history floor.
- **Measurable: 75 of 93**, including **28 of the 33 race rows** (all 8 LED, 4/6 SAME_DAY,
  16/19 near-miss). Actual LED rate on the measurable race subset: **8/28 = 28.6%**
  (Wilson 95%: 15.3–47.1) — close to the served 24.2%, so the measurable subset is not
  obviously unrepresentative, but the 5 dropped race rows include 2 SAME_DAYs.

---

## 2. Does breadth separate winners from near-misses? (the mining claim, re-tested)

Platforms-at-detection (window median), measurable rows:

| Cohort | n | median platforms | values |
|---|---|---|---|
| LED | 8 | 4.5 | 1,3,4,4,5,5,6,7 |
| SAME_DAY | 4 | 5.5 | 2,4,7,8 |
| NEAR_MISS | 16 | 4.0 | 1…9 |
| PRE_BROKEN | 43 | **2** | mostly 1–2 |
| LATE_REDETECTION | 4 | 4.0 | 1,3,5,11 |

**The LED-vs-near-miss separation largely does NOT replicate on raw platform breadth**
(4.5 vs 4.0 window-median; 3.0 vs 2.0 on the first-cycle sensitivity). The mining doc's 80-vs-50
was on the platform-diversity component of a different, pre-segmentation cohort — directional
then, and it stays directional-at-best here. **What breadth strongly separates is race rows from
pre-broken rows** (4.0 vs 2.0): low-breadth first sightings are dominated by single-lane niche
topics (sqlalchemy, npm_package, fastembed, token_usage…) whose Google breakout predates the
engine — cold-start rows that were never races.

## 3. Simulated enrollment priority

### 3a. Race pool only (LED + SAME_DAY + near-miss, n=28) — does priority raise the WIN rate?

| Split (by platforms-at-detection) | LED rate | Wilson 95% |
|---|---|---|
| Top half (n=14) — window median | 4/14 = 28.6% | 11.7–54.6 |
| Bottom half (n=14) — window median | 4/14 = 28.6% | 11.7–54.6 |
| Above-median threshold (n=12) | 4/12 = 33.3% | 13.8–60.9 |
| At/below median (n=16) | 4/16 = 25.0% | 10.2–49.5 |
| **Sensitivity: first-cycle-only breadth, top half** | 5/14 = 35.7% | 16.3–61.2 |
| Sensitivity: first-cycle-only, bottom half | 3/14 = 21.4% | 7.6–47.6 |
| Rank-weighted (weight = breadth rank) | 31.3% | vs 28.6% unweighted |

Every interval overlaps every other almost completely. The window-median split is a dead tie; the
first-cycle split is +14.3pp in the right direction on n=14-vs-14; the rank-weighted lift is
+2.7pp. **No detectable win-rate effect at this sample size.**

### 3b. Full measurable pool (n=71, incl. pre-broken, excl. LATE_REDETECTION) — what enrollment would actually see

Enrollment cannot know pre-broken status in advance, so the honest simulation ranks the WHOLE
candidate pool by breadth:

| Enrolled subset | n | races run | LED | race rate (Wilson) | pre-broken share |
|---|---|---|---|---|---|
| **Top half by breadth** | 35 | **21** | 7 | 33.3% (17.2–54.6) | **40.0%** |
| Bottom half | 36 | **7** | 1 | 14.3% (2.6–51.3) | **80.6%** |
| All (actual) | 71 | 28 | 8 | 28.6% (15.3–47.1) | 60.6% |

**This is the real, robust effect: breadth-priority is a pre-broken filter, not a win-rate
booster.** 60% of top-half slots become actual races vs 19% of bottom-half slots — ~3× more
races run per enrollment slot. The subset race rate rises (33.3% vs 28.6% overall) almost
entirely because low-breadth slots are wasted on cold-start rows that were never races, not
because high-breadth races are won more often.

---

## 4. Threats to validity

1. **Small n everywhere.** 28 measurable races; splits of 12–16; 8 LED total. A real ±10pp
   win-rate effect is undetectable. Nothing in §3a can clear a significance bar.
2. **Breadth measured post-hoc, not at-decision.** The window-median leaks up to 3 days of
   post-detection information (mitigated by the first-cycle sensitivity, which agrees
   directionally); stored rows serve via INV-1 so values are stored, but the stored first row can
   postdate true first sighting (the mining doc's own P=100 caveat).
3. **Measurability is itself biased.** The 18 unmeasurable rows cluster in early-June
   detections and are 11/18 pre-broken — the history floor censors exactly the cold-start era.
   The 5 dropped race rows (2 SAME_DAY) would move small-n rates by points.
4. **Survivorship on two levels.** Only enrolled-AND-resolved rows are visible; 1,114 pending
   rows and every never-enrolled floor-crosser are not. A priority rule reorders the ENROLLMENT
   pool, which this retrospective set only proxies.
5. **Metric mismatch vs the mining doc.** Raw platform count ≠ platform-diversity M ≠
   mainstream breadth; `n_mainstream_platforms` is unmeasurable for all 8 LED rows from
   endpoints. If the founder's intent is specifically MAINSTREAM breadth, this backtest cannot
   confirm or refute it.
6. **Epoch mixing.** Rows span v1_engine and v2_engine scoring; breadth semantics and the
   enrollment rule both changed at the 2026-06-15 boundary (v1 tracked-race 35.0% vs blended
   10.4%). Sub-splitting by epoch drives n below usability, so it was not done.
7. **Pre-broken coupling.** The 7d grace definition makes "pre-broken" partly a detection-latency
   artifact; a breadth filter that skips low-breadth candidates would also skip any future
   low-breadth topic that WOULD have been a race (1 bottom-half LED exists: `socialists`,
   breadth 1, lead +11d — a real win a strict filter would have deprioritized).

---

## 5. Verdict

**Board gate: YES — but for a reframed, weaker claim; NOT for the mining doc's claim.**

- **Not supported (at this n):** "breadth-priority raises the tracked-race WIN rate." The direct
  test is a coin-flip tie on the primary metric (28.6% vs 28.6%), with only directional,
  CI-overlapping support from the sensitivity variants.
- **Supported (robust, mechanism understood):** "breadth-priority raises RACES RUN per enrollment
  slot" — top-half slots produce ~3× more actual races (60% vs 19%) because low breadth at first
  sighting strongly marks pre-broken cold-start rows (median 2 vs 4 platforms). More races at a
  flat win rate = more LED wins per enrollment budget, and a healthier tracked-race denominator.
- **Recommended gate framing:** an enrollment-ORDERING tiebreaker (measurement-side only, no
  score impact, consistent with the mining doc's "enrollment ordering" scope), sold to the board
  as slot-efficiency, with the honest caveat that it deprioritizes low-breadth genuine
  early-detections (`socialists`-class wins). Preconditions before any flip: (a) prospective
  A/B (alternate slots by cycle) rather than trusting this retrospective read; (b) re-run this
  backtest when the post-06-15 first-crossing cohort resolves in volume (the current v2 resolved
  n is tiny); (c) decide raw-breadth vs mainstream-breadth explicitly — the latter is untestable
  from today's endpoints and would need the per-cycle `n_mainstream_platforms` served (or a
  read-only DB study) first.

*Analysis artifacts (scratchpad only, not committed): breadth_measurements.json,
first_cycle_sensitivity.json. Author: held-out research agent, 2026-07-19.*
