# MULTIPLE-COMPARISONS REGISTER — attention accuracy ledger
### Written 2026-08-17, per the Statistician seat (nine-seat board, 2026-08-09)

> **The seat's finding:** "the searched-hypothesis count (D9, fastlane, enrollment
> redesigns) is undisclosed — write the multiple-comparisons correction BEFORE a cohort
> clears a threshold." A correction written *after* a cohort clears is fitting: with
> enough cuts of the same resolved pool, some cohort will cross any threshold by chance.
> This register is the pre-commitment. It exists so that when a rate finally clears a
> bar, the denominator of *searched hypotheses* is on the record and the claim can be
> discounted accordingly — or survive the discount and mean something.

## 1. Every searched hypothesis / cohort cut to date (the disclosure)

Each entry is a distinct way the same underlying ledger pool has been cut, re-scored,
or re-defined since inception. All are counted whether or not they were kept.

| # | Hypothesis / cut | Introduced | Status |
|---|---|---|---|
| H1 | Blended hit rate (all resolved) | inception | reported |
| H2 | Maturity segmentation — EMERGING vs ESTABLISHED cohort (`by_maturity`, early-detection headline) | 2026-06-26 | reported |
| H3 | Patience window 90d → 365d (`LEDGER_TIMEOUT_DAYS`) + asymmetric lead (LED up to 365d forward) | 2026-06-27 | definition change, param-stamped |
| H4 | First-crossing enrollment (replacing leaderboard top-N) | 2026-07-07 | definition change |
| H5 | Pre-broken split (LAGGED → near-miss vs pre_broken; tracked-race rate) | 2026-07-07 | reported |
| H6 | At-detection maturity basis (`LEDGER_MATURITY_AT_DETECTION`, no-lookahead cohorts) | 2026-07-08 | flag, default off |
| H7 | Match-validity metadata (query_ambiguous; ambiguous-query win subset) | 2026-07-07 | reported as metadata |
| H8 | Wikipedia referee corroboration subset (corroborated wins only) | 2026-07-07 (backfill 2026-08-17) | reported as metadata |
| H9 | D9 enrollment A/B (`enroll_arm`, breadth-at-first-sighting priority) | 2026-07 (gated) | arm labels stored |
| H10 | Fast-lane recheck proposal (near-misses lost by 1–2 days) | 2026-07-07 (queued, backtest-gated) | not shipped |
| H11 | Engine-epoch split (v1 engine vs current epoch rates) | 2026-08-10 | reported |
| H12 | Kaplan–Meier survival estimate over the censored pending pool | 2026-07-23 | reported alongside |
| H13 | Null-model comparators (breakout base rate; random-order 50%) | 2026-08-09 | reported |
| H14 | Tail-capture (top-decile-by-magnitude cohort) | 2026-08-17 | reported (this batch) |
| H15 | Calibration-curve buckets + Brier (score-graded cohorts) | 2026-08-17 | reported (this batch) |

Count as of this writing: **15 registered hypothesis families.** Any new cut of the
ledger pool (a new cohort, threshold, window, or re-scoring) MUST be appended here in
the same change that introduces it — an unregistered cut is treated as undisclosed
search when any rate is cited.

## 2. The correction policy (pre-committed, before any threshold clears)

1. **Family definition.** The "family" for correction purposes is every registered
   cohort whose rate could be cited as evidence of ordering skill (today: H1, H2, H5,
   H8-subset, H11-current-epoch, H14, H15 buckets — 7 citable families; definition
   changes H3/H4 and estimators H12/H13 are not independent cohorts but change what
   the others mean and are disclosed alongside).
2. **The bar.** No cohort rate is citable as demonstrated skill unless it beats its
   stated null (the random-order 50% for race rates; the base-rate Brier for H15) at
   **p < 0.05 Bonferroni-corrected across the citable families at time of citation**
   (today: p < 0.05/7 ≈ 0.007 — recompute against the register's then-current count).
   Exact binomial test against the null, two-sided; the CI must exclude the null.
3. **Sample floors first.** The corrected test is not even run below the existing
   floors (`small_sample` flags; market-ledger 30-episode clean floor). A cohort that
   clears the bar at N under the floor is reported as PROVISIONAL regardless.
4. **One pre-registered headline.** The externally citable claim remains the one the
   product pre-registered: the EMERGING early-detection cohort's tracked-race rate
   (H2×H5) with the referee subset disclosed (H8). Other cohorts are diagnostics; a
   diagnostic cohort clearing the bar prompts a pre-registered REPLICATION window
   (fresh detections only, enrolled after the hypothesis was written), never a
   headline swap on the historical pool.
5. **Replication beats correction.** The preferred path for any surprising cohort is
   a forward replication on rows enrolled after the finding — out-of-sample by
   construction — rather than a corrected p-value on the searched pool.

## 3. Frozen within-family parameters (board amendment, 2026-08-17 credibility review)

> Statistician: "families without frozen parameters are still a garden of forking
> paths." The parameters below are FROZEN as of this amendment; changing any one is a
> DEFINITION CHANGE that must be appended here with a new param version, never a tune.

- Patience window `LEDGER_TIMEOUT_DAYS` = 365 (H3) · backward match floor
  `MATCH_WINDOW_DAYS` = 30 · forward lead cap `LEAD_MAX_DAYS` = 365.
- Pre-broken grace `LEDGER_PRE_BROKEN_DAYS` = 7 (H5).
- Tail-capture (H14): top decile = `len(sized) // 10` (min 1) over resolved rows
  carrying a breakout multiple; computation requires ≥10 sized rows; LED baseline at
  registration = 1/12 (frozen — the trial may not move its own goalpost).
- Calibration curve (H15): 20-point score buckets over race rows (confirmed =
  led/same-day/near-miss, miss = timeout FP; pre-broken excluded); `skill_vs_base_rate`
  SUPPRESSED while the outcome set is single-class (degenerate flag).
- Referee (H8): wiki-v2 frozen params (`SURGE_MULT` 3.0, `SURGE_MIN_ABS` 200,
  `MATCH_WINDOW` 30, ±14d breakout match, 2d detection grace). `referee_sealed`
  distinguishes sealed-article checks (first-class) from hindsight-opensearch
  fallbacks (second-class, permanent marking).
- Maturity split (H2): `LEDGER_ESTABLISHED_MIN_DAYS` = 14.
- **Null models (written derivations, per the Statistician's amendment):**
  - `random_order_race_expectation` = 50%: among races actually run (led + near-miss;
    same-day ties excluded from the strict order test), a timing-skill-free detector
    precedes the breakout half the time under exchangeability of (detection, breakout)
    order. CAVEATS ON RECORD: the 6h sweep cadence vs Google's daily granularity
    biases SAME_DAY assignment; exchangeability is assumed, not derived from an
    attention model (Challenger). A naive-momentum comparator (yesterday's risers) is
    the stronger Malkiel null and is REGISTERED AS FUTURE WORK (H-null-2), not yet
    computed (Economist).
  - `breakout_base_rate`: degenerate at zero FPs (labeled in-payload; not a comparator).
- **Cadence epochs:** `enroll_arm='fastlane_nearcross'` marks rows enrolled via the
  Lever-B pre-enrollment lane (live 2026-08-17). Pre/post-cadence rates are never
  compared like-for-like (Challenger condition).
- **H16 amendment (Statistician):** the D-early "inversion flips" criterion is a
  MANIPULATION CHECK, never evidence of skill (Lever A raises race-cohort D by
  construction); the citable tests are (ii) null-beating on sealed new-epoch races and
  (iii) tail-capture improvement. The dark phase's flip gate is the pre-registered
  discrimination test: does d_early-at-enrollment separate subsequently-confirmed from
  pre-broken on NEW rows (threshold to be stated before the first readout).

## 4. Standing rules this register inherits

- Rates stay PROVISIONAL (payload-stamped) until the above is satisfied — the display
  caveat + epoch split shipped 2026-08-10 remain in force.
- R1 symmetry ruling: no absolute lane rate cited while regime-blended.
- Never publish the catch-all % or degenerate-census % as accuracy KPIs.
- The ledger is HELD-OUT: nothing here feeds a score; this register governs CITATION,
  not computation.
