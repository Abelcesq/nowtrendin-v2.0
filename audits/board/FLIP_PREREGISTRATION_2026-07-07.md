# FLIP PRE-REGISTRATIONS — Chairman-authorized, 2026-07-07

Per the Economist's prescription #8: each flip's success metric, review date, and revert
condition, written BEFORE the flip. Chairman ruling: proceed with all six (2026-07-07).
Rollback for every flag = unset/zero the env var (one command, no data cleanup).

## 1. E — LEDGER_SWEEP_NEWEST_SLOTS=2
- **What**: 2 of 8 sweep slots reserved for newest pending detections (24h cooldown).
- **Success metric**: first-crossing-cohort detections get their first sweep check within
  ≤7 days of enrollment (was: weeks behind an ~900-row rotation); no repeat topic_keys in
  the reserved slots on consecutive runs.
- **Review**: 2026-07-14. **Revert if**: repeat paid fetches on identical rows despite the
  cooldown, or the old tail stops advancing entirely.
- **Stamp**: served in /accuracy/ledger as sweep_newest_slots.

## 2. C — N_QUERY_DEDUP_MIN=10
- **What**: repeat surfacing of the same topic+endpoint within 10 min counts once toward N.
- **Semantic accepted by Chairman**: N = distinct surfacing episodes (global window, not
  per-viewer); per-process dedup under-dedups when horizontally scaled (errs conservative);
  pre-flip N counts are grandfathered (definition change effective this date).
- **Success metric**: hot-topic N accrual drops to ~windowed rate; cold topics unaffected;
  Now-TrendIn view rank churn increases (loop damped).
- **Review**: 2026-07-14. **Revert if**: N stops discriminating at all (all topics flat).

## 3. B — MOAT_EXEMPT_STRICT=1
- **What**: catch-all moat topics need ≥2 sources like everything else (high-magnitude +
  tracked-call exemptions unchanged).
- **Precondition executed**: offline shadow count over the live scoring pool, sample
  reviewed for junk-vs-signal before the flip (results appended below).
- **Success metric**: catchall_floor_log single_source_leak falls; floor_trend never
  WORSENING due to this; no measurable drop in genuine first-crossing enrollment volume.
- **Review**: 2026-07-21 (2 weeks — enough scoring cycles to see enrollment effects), plus
  the standing ledger question: did any strict-blocked topic later break out? (The shadow
  log continues to answer this in reverse: topics blocked while ON are simply delayed until
  a second source or high magnitude arrives.)
- **Revert if**: first-crossing enrollment volume drops >30% with no junk-rate improvement,
  or a delayed topic demonstrably cost a LED win.

## 4. D — POST /maintenance/maturity-backfill {dry_run: 0}
- **What**: write ~934 topic_maturity rows (698 ESTABLISHED/0.45 · 156 EMERGING/0.85 ·
  80 NEW/0.80) — CALIBRATION-NEUTRAL BY CONSTRUCTION (exact lifecycle-fallback rule +
  explicit multiplier; a DB row returns what the fallback already returned).
- **Success metric**: written count ≈ dry-run candidates; /accuracy/ledger
  maturity_coverage.by_topic_maturity jumps ~3 → ~900; served scores unchanged
  (spot-check before/after on 3 topics); cohort figures may shift only insofar as the
  lifecycle rule differs from the sustained-days fallback (disclosed, basis-stamped).
- **Review**: immediately post-write. **Revert**: DELETE FROM topic_maturity WHERE
  maturity_reason LIKE 'backfill%' (tagged; restores the fallback path exactly).

## 5. G — SCORE_QUARANTINE_ENABLED=true
- **What**: instruments with ALL positioning inputs absent stop rendering a fabricated
  "30.0/ROUTINE"; the component reads None; weights renormalize over measured components;
  display shows honest n/a coverage.
- **Precondition executed**: held-out shadow score-diff over the pinned population from
  STORED component data (old-vs-new detection distribution — results appended below);
  flip proceeds only if renormalization does not systematically inflate thin-coverage
  instruments. (This is the honest version of the "Phase 2 referee" gate given a 6-row
  market ledger — the Chairman's ruling supersedes waiting for referee sample size, with
  the shadow diff as the safeguard the board demanded.)
- **Success metric**: pinned instruments show n/a positioning coverage on all platforms
  (never NaN/empty, §17); no systematic upward shift in the diff; market ledger annotated
  that scores changed basis this date.
- **Review**: 2026-07-14. **Revert if**: the live distribution shows thin-coverage names
  systematically rising, or any NaN/empty render appears.

## 6. F — STAGE_FROM_DETECTION=1 (last)
- **What**: stored signal_stage keys off calibrated DETECTION at all three write sites —
  one definition, matching every UI chip.
- **Announcement**: dated definition-reconciliation note added to the Methodology page
  (label change ≠ score change; anchoring works on labels too — Zweig).
- **Success metric**: after one scoring rotation, stored stage == stageOf(detection) on
  re-scored rows; /frontend-consistency clean; stage-filtered feeds return sane counts.
- **Known effect**: forward-only mixed-vocabulary window of ~one scoring rotation;
  labels demote where detection < overall (honesty arriving, announced).
- **Review**: 2026-07-14. **Revert if**: any operational consumer (enrollment, alerts,
  pruning) turns out to branch on stored stage in an unintended way.

---
## Appended precondition + execution results (2026-07-07/08 UTC)

**B shadow review (precondition PASSED):** offline replication over the live 96h pool:
16,788 raw single-source catch-all moat topics; **12,851 survive the quality gate** (the
real would-block set). Random sample of 30 reviewed: overwhelmingly expert-platform
tag-mash junk ("groq llama", "int4 int8", "rag summarization", "capable but pricier",
"another postgres connection") — ~0 plausible early signals. The moat exemption was a
junk highway of ~13k topics/window into scoring. Tail-loss risk mitigated: high-magnitude
+ tracked-call exemptions intact; a genuine signal is delayed, not killed. FLIPPED.

**G shadow diff (precondition PASSED — best case):** real before/after over the served
risk feed (32 previously data_coverage=insufficient instruments): **median/mean/min/max
delta = 0.00** — zero score movement; **0 instruments still pinned at 30.0; all 32 now
serve positioning as honest n/a.** The Challenger's inflation scenario is empirically
absent. FLIPPED. Market-basis note added to the Methodology changelog.

**Flips executed (engine v222, one restart):** LEDGER_SWEEP_NEWEST_SLOTS=2 ·
N_QUERY_DEDUP_MIN=10 · MOAT_EXEMPT_STRICT=1 · SCORE_QUARANTINE_ENABLED=true ·
STAGE_FROM_DETECTION=1. Stamps verified live: sweepNewestSlots=2, maturityBasis,
paramVersion now served on /accuracy/ledger.

**D write executed:** 952 rows (698 ESTABLISHED/0.45 · 156 EMERGING/0.85 · 98 NEW/0.80),
0 skipped. maturity_coverage.by_topic_maturity 3 → 76 (all resolved rows on real
classification). Headline rates UNCHANGED (blended 10.0 / tracked-race 26.9) —
calibration-neutrality held. Rollback tag present (maturity_reason LIKE 'backfill%').

**F announced:** "Definition changes" section live on the Methodology page (gh-pages
cf70abf) — label reconciliation ≠ re-scoring, plus the honest-n/a note for G.
Stage-basis effect materializes as rows re-score over the next rotation (forward-only).

**⚠ POST-D OBSERVATION FOR THE CHAIRMAN (the 7th decision):** with real as-of-today
classes covering all resolved rows, the served EMERGING cohort is now 8 resolved / 0 LED
(0.0%) and ESTABLISHED holds all 7 wins (11.3%) — the hindsight artifact in its purest
form (winners sustain, therefore reclassify ESTABLISHED). The no-lookahead basis is built
and flag-gated (LEDGER_MATURITY_AT_DETECTION=1): under it, cohorts classify by days
scored ON/BEFORE each row's detection (dry-run showed 0–1 days for ~all — nearly
everything was genuinely new at detection). RECOMMENDATION: flip it so the headline
early-detection cohort measures the claim without hindsight; basis is stamped either way.
Not flipped — it was not among the authorized six.
