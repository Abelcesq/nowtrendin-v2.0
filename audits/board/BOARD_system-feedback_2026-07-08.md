# ADVISORY BOARD RECORD — Review #2: Executed Updates + System-Wide Feedback (2026-07-08)

Six independent archetype reviews (identical evidence pack; no member saw another's output).
Scope: (1) audit of the seven Chairman-authorized updates executed 2026-07-07/08;
(2) system-wide feedback across scoring systems / scoring methods / data capture /
database integrity / presentation. Full memos preserved in the session transcript;
this record is the faithful collation. The Chairman decides all actions.

## PART 1 — VERDICT ON THE SEVEN EXECUTED UPDATES

**Unanimous: execution was real and disciplined.** The Executioner verified all seven in
code, live config (v222/v224), and the production API: "7/7 flips are real in code and
live in production. No near-no-op this cycle." Pre-registration was called "demonstrably
a working institution" (Economist) and "a paper trail I have rarely seen at this size"
(Outsider). Multiple members noted the pattern: the founder chose worse-looking numbers
over better-looking ones repeatedly — "that culture is fundable" (Outsider), "that is the
moat" (Guardian).

**Open execution items (multi-member convergence — this cycle's homework):**
1. **G-2 (Guardian + Challenger + Executioner): the trend-side quarantine went live
   UNSHADOWED.** SCORE_QUARANTINE_ENABLED flips BOTH engines; the 0.00 diff covered only
   32 market instruments. The trend half (absent components renormalizing the G/D/I/M/C/P
   composite — including absent-Persistence renormalizing Confidence UPWARD for new
   topics) has no distribution diff. Challenger adds: absent-vs-zero must be decided per
   component (zero persistence on a new topic is a real reading, not missing data).
   Executioner: run the trend diff; split the flag (MKT/TREND) if there is movement.
2. **G-1 (Executioner): population reconciliation.** Full served feed scan: only 3 rows
   serve insider-tracking n/a while 269/300 still serve exactly 30.0/z=0. Explanations to
   test: re-score lag, insider!=0 rows being genuinely "measured", population mismatch.
   Count all-inputs-absent rows vs n/a-serving rows — they must match by 07-14.
3. **B is now unmetered (Guardian; Challenger sharpens).** The shadow log only records
   while the flag is OFF; with strict ON, blocked topics are recorded nowhere — B's
   revert condition is unfalsifiable. AND the revert condition tracks enrollment VOLUME
   while the real risk is LEAD EROSION (a delayed enrollment converts LED into
   SAME_DAY/near-miss with no volume drop). Build the durable blocked-topic register +
   instrument first-sighting→first-scored latency.
4. **D-1 (Executioner): unmeasured side-effect now operational.** Ledger enrollment
   excludes ESTABLISHED via topic_maturity — inert at 3 rows, operational at 698.
   Intent-aligned but unregistered; measure enrollment volume pre/post D and spot-audit
   backfilled-ESTABLISHED recent crossers.
5. **7's basis is computed live over a pruned table (Challenger; Executioner partial).**
   velocity_scores prunes at 365d → cohort membership will silently reclassify as
   pre-detection history ages out — breaching 7's own "deterministic per row"
   pre-registration. Fix: STAMP the at-detection day count into accuracy_ledger rows at
   resolution; never recompute published bases.
6. **Process note (Outsider): five flags in one restart = attribution confound** on
   07-14. Per-flag metrics are mostly disjoint (partial save). Next time: one flip, one
   cycle.
7. Small: E's cooldown compares last_checked as an ISO string (format-uniformity check);
   maturityCoverage stamp needs a basis label (reads 0 under basis-7 — do not misread as
   "D failed"); minor denominator legend (70 resolved vs 76 incl. late-redetections).

## PART 2 — CRITICAL FINDINGS (new this review, ranked)

**#1 — FABRICATED FP RATES ARE LIVE IN THE PRODUCT (Challenger E1; CRITICAL).**
Screener detail renders "speed · ~22% FP" and "precision · <9% FP" on every trend topic;
the API serves the same strings; they trace to a design-era constant (06_10_26 file),
supported by no study — while the actual ledger cannot measure FP until mid-2027.
An invented quantitative accuracy claim in the UI, contradicted by the moat itself.
Violates "no fabricated data" + "never assert what we can't support". PURGE FIRST.

**#2 — THE GROUND-TRUTH INSTRUMENT IS NONSTATIONARY (Challenger B1; CRITICAL).**
detect_breakout_date baselines on the lowest 40% of a curve whose window GROWS with row
age, on a Google index renormalized per-window; long windows return weekly points (the
sustain rule silently means 2 days young / 2 weeks old; ±7d lead quantization). The same
detection can resolve differently depending on WHEN swept — the published record is not
reproducible from the stored row, and the longest LED leads are the most suspect. FIX:
persist the fetched curve (or hash+window+params) per resolution; one final curve fetch
before any timeout-FP (B4); re-validate existing LED rows on fixed windows.

**#3 — THE REFEREE CORROBORATES THE WRONG THING (Challenger B2; HIGH; cheap fix).**
Wikipedia arrival is compared to the GOOGLE BREAKOUT (±14d), searching from detection−30d
— a win where Wikipedia says attention arrived BEFORE our detection can still read
"corroborated". Compare arrival to OUR DETECTION date. Executioner companion: all 7 LED
wins currently read "referee unchecked" — one read-only sweep closes the highest
defensibility gap in the building (1–2h).

**#4 — DATE-LOCALE SILENT MIS-PARSE (Expansionist; §14 bug TODAY).**
date_utils' bare %m/%d/%Y parses European DD/MM dates as US ordering whenever both
fields ≤12 — silent mis-canonicalization, the exact failure the gate exists to prevent.
One European RSS source away from corrupt canonical dates.

**#5 — SELF-REFERENCE NOT FULLY CLOSED (Outsider; HIGH).**
Persistence (P) measures the topic's elevation across the ENGINE'S OWN prior cycles —
own-score history feeding ~27% of Confidence. Deserves the N-rule treatment: re-ground
externally (source recurrence) or defend in writing. (Outsider also cited "Grade tool
still folds N" from the punch list — COLLATION NOTE: that item was verified FIXED in
code 2026-07-07 [ai_grade uses renormalized N-free weights]; the punch list is stale.)

**#6 — WIN DEFINITION NOT PINNED (Outsider; HIGH).**
The backtest counts LED+SAME_DAY as wins; the served headline is LED-only (7/70) with
4 same-day rows uncounted; UI copy says "LED ÷ all resolved". One metric, two
definitions. Pin it everywhere (and Economist: rename naive_hit_rate_pct before the
real Malkiel baseline collides with the name).

**#7 — MARKET/CRYPTO CONFIRM RATES HAVE NO NULL BASELINE (Challenger B3; HIGH).**
±5%/60d (market) and ±8%/45d (crypto) confirm almost surely under drift; inflow 3/3 vs
outflow 0/3 is the drift signature. Control cohort (random ticker/date/direction, same
thresholds) or market-adjusted thresholds before any confirm rate reaches a client.

**#8 — WEIGHT LITERALS FORKED (Guardian).** signal_calibration_integration:1187-1204
hand-copies 0.375/0.216/… beside the imported _WD/_WC — violates the single-source rule
scoring_weights.py itself declares. + Executioner: weights carry no provenance stamp.

## PART 3 — THE FIVE DIMENSIONS (condensed convergence)

**(a) Scoring systems**: architecture sound (N-exclusion structural; dual-pathway
byte-identical for expert topics; held-out ledger verified again). D carries 21.6% of
Detection while empirically 0 at first sighting for winners and losers — "a 4-component
score wearing 6-component weights" (Challenger); the fix path exists (research feeds
OFF + confirmation-marker) and any reweight stays gated on the ≥30-race backtest.
269/300 market rows read exactly 30.0/z=0 on the 0.55-weight positioning component —
near-zero discrimination on most of the universe (Executioner).
**(b) Scoring methods**: every weight/threshold is a hand-tuned prior; the ledger proves
honesty, not edge. The four unbuilt edge instruments (Economist progress ledger):
naive-baseline column, tail-capture rate, fast-lane recheck, full silent-evidence
register. No interval estimates anywhere (26.9% is Wilson [14%,46%] — "precision
theater" at one decimal). Freeze + version the measurement constants
(PRE_BROKEN_DAYS/EST_MIN_DAYS into param_version).
**(c) Data capture**: 63% of resolved rows entered post-breakout — coverage latency is
the binding constraint; GHOST_RESEARCH_FEEDS flip = highest-leverage pending action
(unanimous). Entity-level extraction (the Haaland gap) = #1 strategic capture build
(Outsider + weekly audit). Sweep throughput must scale with enrollment (fixed 8 vs
~915 pending; ~5-month rotation). misclassified_tracked=73 worklist. Expansionist:
stamp lang/region provenance on every row NOW (days now, quarters later); the entire
NLP spine is English-hard-coded; validation referee chain is US/English-only — the moat
currently proves the claim for English-language US attention only.
**(d) Database integrity**: strongest dimension (canon, retention, INV-1, stamps,
self-healing pool). Items: stamp-don't-recompute (the #1 integrity fix from Part 1);
substr(scored_at,1,10) needs a documented exemption or helper (2 members); Postgres
tier decision needs a DATE before the 365d tail forces retention-vs-cost; regenerate
DB_DATA_DICTIONARY; last_checked format check.
**(e) Presentation**: Ledger view praised unanimously ("the most honest client-facing
scorecard I have reviewed" — Economist). Gaps: the FP-rate purge (#1); 0-FP timeout
caveat into payload + UI; basis stamps rendered in UI/Export (numbers travel without
footnotes); stage vocabulary triple-mismatch (Methodology EMERGING/WATCHING vs UI
Indicating/Marginal); topic_key snake_case leaking into client tables; jargon kill-list;
trend-side measurement completeness ("measured on X of Y components" — market side
already does it); earlyDetectionHitRate == blended under basis-7 (annotate, don't
present two identical numbers as two facts); disclaimer critique (Outsider recommends
counsel-drafted rider with named biases — CHAIRMAN'S CALL: current text is
founder-approved legal copy).

## PART 4 — DISAGREEMENTS
- **Disclaimer**: Outsider wants it rewritten institutional-grade; it is founder-approved
  verbatim copy. Chairman decides.
- **B's instrument**: Guardian/Economist still prefer the expiry-variant redesign over
  the hard floor; all accept strict mode as the running stopgap pending the register.
- **Severity of the nonstationary-instrument finding**: Challenger rates it CRITICAL and
  wants existing LED rows re-validated; others implicitly trust current rows. Resolved
  only by doing the re-validation.
- **Five-in-one-restart**: Outsider objects; Executioner accepted it with disjoint
  metrics. Process rule proposal: one flip per cycle going forward.

## PART 5 — CONSENSUS ACTION QUEUE (awaiting Chairman ruling)
1. PURGE the fabricated ~22%/<9% FP claims (UI + API + engine constants). [XS, urgent]
2. Referee sweep of the 7 LED wins + fix referee to corroborate the LEAD (vs detection). [S]
3. G trend-side shadow diff → split the quarantine flag if movement. [S]
4. Stamp-don't-recompute: at-detection day count + pre-broken lag written into ledger
   rows at resolution; PRE_BROKEN_DAYS/EST_MIN_DAYS into param_version. [S]
5. Durable blocked-topic register (B) + first-sighting→first-scored latency metric. [M]
6. date_utils locale fix (kill bare %m/%d/%Y ambiguity). [S]
7. Naive-baseline ledger column (+ rename naive_hit_rate_pct). [M — the edge instrument]
8. FP-timeout caveat + basis stamps into payload/UI/Export; win definition pinned;
   stage-vocab reconciliation; Wilson CIs on headline rates. [S–M bundle]
9. GHOST_RESEARCH_FEEDS founder flip (unanimous highest-leverage pending action). [XS]
10. Persist Trends curves per resolution + final-fetch-before-timeout + LED re-validation. [M]
11. Fast-lane recheck (near-miss→LED metric pre-registered). [M]
12. lang/region provenance stamps on ingest (the global option, cheap now). [M]
13. Null-baseline the market/crypto ledgers. [M]
14. P self-reference: external re-grounding proposal (backtest-gated). [design]
15. Weight-literal dedup + provenance stamp; entity-level extraction design; Postgres
    tier date; DB_DATA_DICTIONARY regen; misclassified_tracked worklist. [housekeeping]

**07-14 review homework (pre-registered):** G-1 reconciliation · G-2 trend diff ·
D-1 enrollment measurement · E slot mix + tail advance · C discrimination · F stage
rotation + /frontend-consistency · 7 determinism (twice-run identical) · cost sentinel.
**07-21:** B — junk drain vs enrollment volume vs LEAD-TIME comparison, with the
register built first.
