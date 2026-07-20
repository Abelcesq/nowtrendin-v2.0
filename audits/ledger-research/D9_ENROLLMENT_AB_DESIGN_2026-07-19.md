# D9 — Prospective Alternate-Slot A/B: Breadth-Ordered Ledger Enrollment (REGISTERED DESIGN)

**Status: REGISTERED, NOT RUNNING.** Written 2026-07-19 by the held-out research agent,
founder-ordered per board decision item **D9** (`audits/board/BOARD_estimator-fdm-snapshot2_2026-07-19.md`):
"15a enrollment-ordering tiebreaker → prospective alternate-slot A/B design. Measurement-side;
board gate after A/B."

This document is the **a-priori registration**. Every rule, threshold, endpoint, n-floor and stop
rule below is fixed BEFORE any data is collected. Running the test later may not tune anything in
this file; any change requires a NEW registration document plus board + founder sign-off, and
restarts the clock. Design file only — **no code has been changed, no flag exists yet.**

**Grounding:**
- Backtest: `audits/ledger-research/BREADTH_PRIORITY_BACKTEST_2026-07-19.md` — win rates dead-tied
  (28.6% vs 28.6%); the robust effect is **enrollment EFFICIENCY**: top-half-breadth slots were
  60% real races vs 19% for bottom-half (~3x races per slot at flat win rate).
- Enrollment code path (read-only): `transfer/gravitational_anomaly_detector.py` —
  `_record_top_detections` (line 582), invoked once per score cycle from `_score_phase`
  (line 5334, `LEDGER_RECORD_TOP=20`); `transfer/accuracy_ledger_enhanced.py` —
  `record_detection` (idempotent on md5(topic_key-detection_date)), `_upsert_ledger`,
  `sweep_pending`.
- CLAUDE.md §14 (first-crossing enrollment, `LEDGER_ENROLL_RECENT_DAYS=14`,
  ESTABLISHED/MONITORING excluded, patience window 365d, ledger held-out and never deleted).

---

## 0. The question, stated once and honestly

**Registered claim under test (efficiency, NOT accuracy):** ordering a cycle's not-yet-enrolled
floor-crossers by cross-platform breadth (descending) before filling that cycle's enrollment slots
increases **races-run per enrollment slot** (equivalently, lowers the pre-broken share of enrolled
rows), relative to the current arrival-order enrollment.

**Explicitly NOT under test:** "breadth-priority raises the tracked-race WIN rate." The backtest
tied dead on that claim, and §3.3 below shows the A/B is hopelessly underpowered for it on any
realistic timeline. Win rate is *monitored* (stop rule) but no win-rate conclusion of any kind may
be drawn from this test.

**Registered breadth definition (decided now, per backtest threat #5):** breadth =
`len(json.loads(platforms_active))` of the topic's **newest `velocity_scores` row at the moment of
enrollment** (the row the enrollment query already joins). This is RAW platform count — the metric
the backtest actually measured — NOT mainstream breadth (`n_mainstream_platforms`), which was
unmeasurable for all 8 LED rows and is explicitly deferred to a future, separately registered
study. No post-enrollment information is used: the ordering key is frozen at decision time and
stamped (§6).

---

## 1. Assignment rule (deterministic, auditable, no randomness)

Assignment is **per enrollment cycle** (each `_record_top_detections` invocation), derived purely
from the UTC wall clock at function entry. No `Date.now`-style seeds, no RNG, no state.

Let `t` = Unix seconds (UTC) at function entry:

```
d   = floor(t / 86400)          # days since epoch
s   = floor((t mod 86400) / 21600)   # 6h slot of day, s in {0,1,2,3}
arm = "A"  if (d + s) mod 2 == 0  else  "B"
```

**Why `(d + s) mod 2` and not plain slot parity or day parity:**
- Plain slot parity with 4 slots/day (even) maps each UTC time-of-day to the SAME arm every day —
  arm would be confounded with news-flow time-of-day.
- Plain day parity gives each arm whole days — a single big news day dumps its entire cohort into
  one arm (cluster confound).
- `(d + s) mod 2` gives each arm 2 slots per day AND flips the slot→arm mapping daily (day d:
  slots 0,2→A, 1,3→B; day d+1: 0,2→B, 1,3→A) — a balanced alternation over both time-of-day and
  day, still reproducible by anyone from the timestamp alone.

Cycle-start drift (cycles are ~6h but not boundary-aligned) can occasionally give two consecutive
cycles the same `s`; that is acceptable — the rule stays deterministic from the timestamp, and the
per-cycle audit log (§7f) records the computed arm, so there is never reconstruction ambiguity.

**ARM A (control):** the current rule verbatim — candidates ordered by first-seen DESC (newest
crossers first), exactly as `_record_top_detections` orders today.

**ARM B (treatment):** the SAME candidate set ordered by breadth DESC; ties broken by first-seen
DESC, then `topic_key` ascending lexicographic (fully deterministic total order).

**The shared cap that makes the test real.** Ordering is a no-op unless slots are scarce. Current
throughput (~14 new enrollments/day, ~3.5/cycle) never saturates the 20-row query cap, so a naive
reorder would produce two identical arms. The test therefore registers a per-cycle **new-enrollment
cap `LEDGER_ENROLL_NEW_CAP = 3`** applied IDENTICALLY to both arms (capacity 12/day vs the observed
~14/day). The cap is a shared experimental condition, not the treatment: arm A under the cap trims
its arrival-order tail (oldest of the new crossers), arm B trims its lowest-breadth tail. The test
thereby isolates ORDERING as the only difference between arms. The cap value may not be changed
mid-test (no tuning); if fewer than 25% of cycles turn out contested (candidates > cap) at the
4-week interim, the test is EXTENDED or re-registered — never re-tuned.

A cycle is **contested** when its not-yet-enrolled candidate count exceeds the cap; only contested
cycles can differ between arms, and the log marks each cycle contested true/false.

## 2. What is HELD CONSTANT (the judge never changes)

Frozen for the entire test, both arms, at today's live values:

| Frozen element | Value |
|---|---|
| Detection floor | `LEDGER_DETECTION_FLOOR = 10` |
| First-crossing recency | `LEDGER_ENROLL_RECENT_DAYS = 14` |
| Maturity exclusion | ESTABLISHED / MONITORING excluded (topic_maturity), fail-open branch unchanged |
| Detection date | topic's true first-seen (`topic_lifecycle.first_detected_at` / MIN(scored_at)), canonicalized via `to_iso_date` |
| Quality gate | `_is_quality_topic` at the write boundary, unchanged |
| Idempotency | `record_detection` md5(topic_key-detection_date), unchanged |
| Verdict logic | LED / SAME_DAY / LAGGED / FALSE_POSITIVE / LATE_REDETECTION taxonomy, `_upsert_ledger`, unchanged |
| Patience window | `DEFAULT_TIMEOUT_DAYS = 365`, computed live from detection_date |
| Match windows | `MATCH_WINDOW_DAYS = 30` backward, `LEAD_MAX_DAYS = 365` forward (asymmetric) |
| Pre-broken grace | `LEDGER_PRE_BROKEN_DAYS = 7` (server-computed, one definition) |
| Breakout threshold | 2.5 |
| Sweep mechanics | rotation, timeout-first, budget guard, `LEDGER_SWEEP_LIMIT=8`, 24h newest-slot cooldown — unchanged, and **ARM-BLIND** (the sweep never reads the arm stamp; registered invariant) |
| Referee | Wikipedia-pageviews referee on wins, fail-open, unchanged |
| Retention | 365-day retention, no deletes, no rewrites of existing rows (§13/§14) |

The ONLY things that vary: (a) the ordering of new candidates within a cycle, by arm; (b) the
shared new-enrollment cap of §1, identical across arms.

## 3. Endpoints, power, and minimum n (registered before any data)

### 3.1 Primary endpoint — races-run per enrollment slot

Per arm: `race_share = races / classified_slots`, where a **classified slot** is an enrolled row
that has received **≥1 successful sweep fetch**, and:

- **pre-broken slot** — resolved LAGGED with `pre_broken = 1` (breakout > 7d before first
  sighting; the stored server field, one definition);
- **race slot** — everything else that has been swept ≥1 time: resolved LED / SAME_DAY /
  near-miss LAGGED (`pre_broken = 0`), OR **still pending after ≥1 sweep**. This last clause is
  sound because the sweep resolves any breakout it finds: a pre-broken row resolves LAGGED on its
  FIRST successful sweep, so a row still pending after a sweep has, by construction, no prior
  breakout — it is a race in progress. This lets the primary endpoint be read without waiting out
  the 365-day patience window, with no censoring bias in the pre-broken direction.
- FALSE_POSITIVE (timeout) and LATE_REDETECTION rows are counted as race slots run-and-lost /
  excluded respectively, exactly as the served tracked-race denominator treats them today
  (LATE_REDETECTION excluded per §14).
- Unswept rows are NOT in the denominator (disclosed as pending-classification per arm).

### 3.2 Powering the primary endpoint — the arithmetic, shown

Two-proportion test, two-sided α = 0.05 (95% confidence), power 1−β = 0.80,
n per arm = ( z_{α/2}·√(2·p̄·q̄) + z_β·√(p₁q₁ + p₂q₂) )² / (p₁ − p₂)².

**Scenario 1 — the backtest's raw split (60% vs 19% race share), the effect named in the gate:**
p₁ = .60, p₂ = .19, p̄ = .395:
- 1.96·√(2·.395·.605) = 1.96·.6914 = **1.355**
- 0.84·√(.60·.40 + .19·.81) = 0.84·√.3939 = 0.84·.6276 = **0.527**
- n = (1.355 + 0.527)² / (.41)² = 3.543 / .1681 = **21.1 → 22 per arm** (at 90% power: 28/arm).

**Scenario 2 — the honest diluted contrast (registered PRIMARY power basis).** A live arm B does
not enroll only the top half of the pool; under a modestly binding cap it shifts composition
partway. Registered conservative contrast: arm A ≈ 40% race share (the backtest's all-actual
39.4%) vs arm B ≈ 60%: p₁ = .60, p₂ = .40, p̄ = .50:
- 1.96·√(2·.5·.5) = 1.96·.7071 = **1.386**
- 0.84·√(.24 + .24) = 0.84·.6928 = **0.582**
- n = (1.386 + 0.582)² / (.20)² = 3.873 / .04 = **96.8 → 97 per arm**.

**Calendar arithmetic** (from ~14 new enrollments/day → ~7/arm/day, and ~50–60% pre-broken share
today):
- Enrolling 97/arm ≈ **14 days** of enrollment (22/arm ≈ 3–4 days).
- The binding constraint is FIRST-SWEEP latency, not enrollment: at `LEDGER_SWEEP_LIMIT=8` ×
  4 runs/day = ≤32 sweeps/day against a ~1,114-row pending rotation, first sweep arrives in up to
  ~35 days. **Registered precondition:** the test runs with `LEDGER_SWEEP_NEWEST_SLOTS ≥ 2`
  (the existing rec-E mechanism, 24h cooldown intact) so new cohort rows get first sweeps within
  days, not weeks. No other sweep change.
- Expected timeline: **interim read ~4 weeks; final read ~8–10 weeks** (enrollment 2 weeks +
  sweep coverage + classification maturity).

**Registered n-floors — no conclusion of ANY kind may be stated before:**
- **Interim:** both arms ≥ **28** classified slots AND ≥ 28 calendar days elapsed. Interim may
  claim efficacy ONLY at p < 0.01 (spent alpha; large-effect Scenario-1 check).
- **Final:** both arms ≥ **97** classified slots. Final claim at p < 0.04 (remaining alpha;
  total ≈ 0.05).
- Anything read before these floors is monitoring (stop rules, §5), never a conclusion.

### 3.3 Secondary endpoint — tracked-race hit rate per arm (monitored, never concluded)

Per arm: LED / (LED + SAME_DAY + near-miss LAGGED + FALSE_POSITIVE races), the served
tracked-race definition. Powering the backtest's observed 33.3% vs 28.6% (Δ = 4.7pp): pooled
p̄ = .31, n = (1.96·.654 + 0.84·.653)² / (.047)² = 3.35 / .00221 ≈ **1,516 races per arm** — at
~2–4 races/arm/day that is **years, not weeks**. The A/B is therefore REGISTERED AS UNPOWERED for
win rate: per-arm hit rates are reported with Wilson 95% intervals and the explicit label
"underpowered — no inference", and feed only the §5 stop rules.

## 4. Fairness / bias analysis (registered disclosures)

1. **Denominator composition shift (the central bias).** Arm B's races are, by construction,
   breadth-skewed high. Its tracked-race hit rate is measured on a DIFFERENT population than arm
   A's. Any cross-arm hit-rate comparison must carry the per-arm breadth distribution of race rows
   (median + IQR of breadth-at-enrollment), printed beside every per-arm rate. The two arms' hit
   rates are not directly comparable and are never blended silently: the served blended and
   tracked-race rates continue to be computed over ALL rows (both arms), so the public numbers are
   unaffected by arm partitioning; per-arm numbers live only in the A/B report.
2. **Shared candidate pool spillover.** Arms alternate over ONE stream: a candidate deprioritized
   by arm B's ordering in cycle t remains a floor-crosser and can enroll in a later (possibly
   arm-A) cycle while still within the 14-day recency window. So arm A's pool contains arm B's
   deferrals (and vice versa for the arrival-order tail). Primary analysis is therefore
   **per-SLOT** (the arm of the cycle that actually enrolled the row), which stays well-defined
   under spillover; the audit log additionally counts **spillover rows** (rows enrolled in arm X
   that appeared as unenrolled candidates in ≥1 earlier opposite-arm contested cycle) and the
   report discloses the count per arm. If spillover exceeds 30% of either arm's enrollments the
   slot-level contrast is diluted and the final read must say so (and the effect estimate is then
   a LOWER bound on the true ordering effect, since spillover pushes arms toward each other —
   direction disclosed, not corrected post hoc).
3. **The socialists-class counterexample (standing monitor, registered).** The backtest's one
   bottom-half LED (`socialists`, breadth 1, lead +11d) proves low-breadth genuine early
   detections exist. Registered monitor: (a) count LED wins with breadth-at-enrollment ≤ 2 in
   EACH arm; (b) from the candidate log, track every contested-cycle candidate with breadth ≤ 2
   that arm B deprioritized — the **deferred-low-breadth cohort** — and report how many later
   enrolled (either arm) and how each resolved. A deferred low-breadth candidate that resolves
   LED is a **missed-socialists event** and feeds stop rule §5(b). This cost is reported in the
   final read whatever the primary result.
4. **Cap fairness.** The §1 cap trims ~2 candidates/day below today's natural inflow, in BOTH
   arms. Arm A's trimmed tail (oldest new crossers) and arm B's (lowest breadth) differ — that IS
   the treatment. The total trimmed count per arm is logged and reported; a persistent asymmetry
   in total enrollment throughput between arms (> 20%) indicates an implementation bug, §5(c).
5. **Time-window bias.** Both arms run simultaneously through the same news regime, so epoch
   mixing (backtest threat #6) does not apply across arms; it applies only to comparisons of
   either arm against pre-test history, which this design does not make.

## 5. Stop / rollback rules (registered margins)

Checked at every weekly monitoring read (monitoring, not conclusions). The test STOPS — flag off,
enrollment reverts to pure arm-A behavior everywhere — if any of:

- **(a) LED lag:** at or after the interim floor (≥28 classified/arm), arm B's absolute LED count
  is ≥ 4 behind arm A's AND arm B's LED count is ≤ half of arm A's. (Both conditions, so a 1-vs-4
  small-n fluke doesn't trip it, but a real early-detection cost does.)
- **(b) Missed-socialists:** ≥ 2 deferred-low-breadth candidates (§4.3) resolve LED during the
  test — the ordering is demonstrably discarding the exact wins the thesis exists to catch.
- **(c) Throughput asymmetry:** cumulative enrollments differ between arms by > 20% after ≥ 2
  weeks (arms alternate symmetrically, so this can only be a bug).
- **(d) Integrity breach:** any stored pre-existing row rewritten, any sweep/verdict code path
  found reading the arm stamp, or any mid-test change to a §2 frozen value → immediate stop and
  incident note. (Adding nullable columns and stamping NEW rows is the registered mechanism and
  is not a breach.)
- **(e) Founder order,** any time, no justification required.

**Rollback mechanics:** unset the flag (`LEDGER_AB_D9=0`). Already-stamped rows KEEP their
`enroll_arm` stamps forever (the ledger is never rewritten or deleted); a stopped test is reported
as truncated with whatever n it reached, verdict "stopped under rule (x)", and no efficacy claim.

## 6. Integrity gates (measurement-only)

- **Held-out:** enrollment ordering, like enrollment itself, is measurement-side. Nothing in this
  test touches scoring, calibration, serve payloads, or any Gradient/N component. The sweep and
  verdict logic are arm-blind (§2). The accuracy ledger's judge is unchanged.
- **No rewrites:** existing `pending_detections` / `accuracy_ledger` rows are never modified.
  New columns are nullable, forward-only, stamped at write time only (the same pattern as
  `sweep_query` / `pre_broken` / `at_detection_days`).
- **Param stamping per arm:** the ledger summary `param_version` gains the suffix `|abD9` for the
  test's duration; every row enrolled during the test carries `enroll_arm` ('A'|'B') plus
  `breadth_at_enroll` (integer, the frozen ordering key), so every per-arm number in any future
  report is reconstructible from stored rows alone. Rows with `enroll_arm IS NULL` are pre-test
  rows and are excluded from all A/B reads by definition.
- **No tuning:** cap, arm formula, breadth definition, endpoints, n-floors, alphas, and stop
  margins are fixed by this document. The one registered adaptive element is EXTENSION of the
  test window (more time, same rules) if contested-cycle frequency or sweep coverage runs low.
- **Board gate after, not before the read:** per D9, the A/B result goes to the board; only after
  a board review + founder sign-off could arm-B ordering become the standing rule. A positive
  primary result alone changes nothing by itself.

## 7. Eventual code touch-point (described, NOT implemented)

All in `_record_top_detections` (`transfer/gravitational_anomaly_detector.py:582`) plus two
schema/stamp threads in `transfer/accuracy_ledger_enhanced.py`. Entirely flag-gated behind
`LEDGER_AB_D9` (default 0 = today's behavior byte-identical).

- **(a)** Extend the existing SELECT to also read `v.platforms_active` from the already-joined
  latest `velocity_scores` row (breadth = length of the JSON list; no extra query, no new join
  cost beyond the column).
- **(b)** Exclude already-enrolled topics IN the query (`NOT EXISTS` against
  `pending_detections`/`accuracy_ledger` on topic_key + canonical detection_date) and widen the
  raw fetch (e.g., LIMIT 60) so ordering acts on the cycle's genuinely NEW candidates — today the
  idempotent skip happens after the LIMIT, which would let already-enrolled high-breadth rows eat
  arm B's slots and silently starve new low-breadth crossers (the naive-reorder failure mode this
  design exists to avoid).
- **(c)** Compute `arm` from the §1 clock formula at function entry.
- **(d)** Order the new-candidate list: arm A = first-seen DESC (current behavior); arm B =
  breadth DESC, first-seen DESC, topic_key ASC. Truncate to `LEDGER_ENROLL_NEW_CAP` (3).
- **(e)** Pass `enroll_arm` + `breadth_at_enroll` into `record_detection` (two new OPTIONAL
  keyword params, defaulting None so all existing callers are untouched); `record_detection`
  stores them on the pending row (two nullable columns, ALTER TABLE ADD COLUMN forward-only), and
  `_upsert_ledger` carries both into `accuracy_ledger` at resolution (same nullable-column
  pattern as `pre_broken`).
- **(f)** Append one audit row per cycle to a new `enroll_ab_log` table: cycle UTC timestamp,
  computed (d, s, arm), candidate count, contested flag, enrolled count, trimmed count, and the
  candidate list with breadths (JSON) — the reproducibility record for §1, §4.2 spillover counts
  and §4.3 deferred-cohort tracking. Read-only with respect to the ledger; never swept; never
  served.
- **(g)** Precondition env: `LEDGER_SWEEP_NEWEST_SLOTS ≥ 2` (existing mechanism, §3.2), set at
  test start, restored at test end.

Estimated diff: ~40 lines in `_record_top_detections`, ~10 in `record_detection`, ~5 in
`_upsert_ledger`, one small CREATE TABLE — nothing else. The scheduler call site (line 5334) is
untouched.

## 8. Reporting

Weekly monitoring note (stop rules only) + interim report at the §3.2 interim floor + final report
at the final floor, all to `audits/ledger-research/`. Every report prints, per arm: enrolled /
swept / classified n, race share with Wilson 95%, pre-broken share, LED count, hit rate (labeled
underpowered), breadth distribution of race rows, spillover count, deferred-low-breadth cohort
status, contested-cycle fraction. The public served ledger numbers remain arm-blended and carry
their existing disclosures; the catch-all-style rule applies here too — **per-arm interim numbers
are never published externally.**

*Registered 2026-07-19. Held-out research agent. No code changed; no flag set; nothing runs until
the founder orders the build and the touch-points of §7 pass their own review.*
