# ADVISORY BOARD RECORD — Branch `integrity-recs-A-G` (2026-07-07)

Six INDEPENDENT archetype reviews of the seven flag-gated integrity recommendations
(branch commit `7e7708c`). Each member received the identical evidence pack (branch diff,
D-weight backtest results, live ledger data, audit docs) and worked in isolation — no
member saw another's output. This document is a COLLATION, not a blend. The Chairman
(founder) decides per item.

## VERDICT TABLE

| Item | Challenger | Guardian | Expansionist | Outsider | Executioner | Economist |
|---|---|---|---|---|---|---|
| A. D-weight backtest | APPR-COND | APPR-COND | APPROVE | APPROVE | SHIP | APPROVE |
| B. MOAT_EXEMPT_STRICT | APPR-COND | APPR-COND | APPR-COND | APPROVE | SHIP (shadow first) | APPR-COND |
| C. N query dedup | APPR-COND | APPROVE | APPR-COND | APPR-COND | SHIP | APPROVE |
| D. Maturity backfill | **REJECT the write** | APPR-COND | APPR-COND | APPR-COND | **SHIP-LATER (bug)** | APPR-COND |
| E. Sweep newest slots | APPR-COND | APPR-COND | APPR-COND | APPR-COND | SHIP | APPR-COND |
| F. Stage from Detection | APPR-COND | APPR-COND | APPROVE | APPROVE | **SHIP-LATER (incomplete)** | APPROVE |
| G. Positioning quarantine | APPR-COND (no flip yet) | APPR-COND (split it) | APPR-COND (prioritize) | APPROVE (flip fast) | SHIP-LATER (shadow diff) | APPR-COND |

## EXPLICIT DISAGREEMENTS (signal, not noise)

1. **D is the contested item.** The Challenger REJECTS the write outright: maturity is
   classified from distinct scored days AS OF TODAY, so successful detections accumulate
   days after breaking out and migrate OUT of the EMERGING cohort with hindsight — very
   plausibly the CAUSE of the alarming 2.3%-vs-24% inversion; writing 900 rows launders
   that artifact into a canonical, calibration-feeding table. The Executioner independently
   found a concrete implementation BUG: the INSERT omits `calibration_multiplier` → table
   default 1.0 → ~900 backfilled ESTABLISHED topics would transiently serve UNDISCOUNTED
   (score inflation) until the reclassify job corrects them. Everyone else conditions the
   write on a what-if score-delta report. Net: the write as coded satisfies NO member.
2. **G's flip urgency splits the board.** The Outsider: flip fast — a fabricated
   "ROUTINE 30.0" is live in front of users today and is the worst item in the pack. The
   Challenger/Guardian/Executioner/Economist: the flip is score-affecting and the code's
   own referee gate is unmet (market ledger n=6). The Guardian and Challenger converge
   independently on the SPLIT: ship the honest-"n/a" display half immediately; hold the
   renormalization half behind the referee + a before/after shift audit on the 133 pinned
   instruments (Challenger warns renormalization could systematically INFLATE
   thin-coverage names — "score inflation via honesty is still score inflation").
3. **B's instrument is questioned even by approvers.** The Guardian: it fixes a QUALITY
   failure with a TIMING tool, taxing the single-source expert early signal — the thesis
   itself; prefer the quality-bar/expiry redesign. The Economist (Taleb): the cost is
   SILENT and lives in the fat tail. Five of six independently demanded the same thing:
   a SHADOW LOG of what strict mode would have blocked, checked against later breakouts,
   BEFORE any flip. The Expansionist adds: catch-all membership is an English-lexicon
   function — flipping this globally makes it de facto language policy.
4. **F was believed done by five members; the Executioner proved it near-no-op.**
   `signal_stage` is written at THREE sites; the flag patches only the raw detector —
   `apply_calibration` (writes stage from calibrated averages) and the post-cal
   dual-pathway block overwrite it afterward. The behavior test exercised a layer
   production discards. Everyone's conditions (consumer audit, version stamp, changelog)
   still stand once the flag reaches all three sites.
5. **Universal convergences** (independent, no coordination): (a) publish rates
   cohort-tagged (pre-fix vs first-crossing enrollment) permanently; (b) stamp every flip
   param_version-style so no published rate silently spans two definitions; (c) A's result
   is "insufficient evidence," never "evidence of no effect" — and never quote the 0.558
   no-D bound as directional.

## CONDENSED MEMOS (faithful; full texts preserved in session transcript)

### THE CHALLENGER (accuracy attack)
Overall: unusually honest pack, but the resolved cohort (70/26/7) makes every number
order-, definition-, and time-sensitive; D/E/F quietly change who gets measured, when,
under what label. Sharpest findings: (A) backtest uses components provably not from
detection time (the P=100 anomaly), AUC SE ≈0.11 → all variants noise; winners defined
LED+SAME_DAY though the published rate is LED-only; recompute path ≠ production fold.
(B) an invisible-false-negative machine — suppressed topics never appear in any metric;
the published rate could IMPROVE while true earliness degrades: a denominator game the
flag creates by accident. (C) N becomes topology-dependent and two-regime without a
version marker; incumbents keep pre-dedup inflated counts (loop frozen in their favor).
(D) REJECT: hindsight-biased heuristic laundered into a canonical calibration-feeding
table mid-experiment; also `substr(scored_at,1,10)` is the banned [:10] slice in SQL
clothing. Fix = classify AS OF detection_date (data exists; 365d retention). (E) newest-K
has no last-checked guard → same rows burn paid fetches every run; sweep order determines
publication-time rates for months. (F) "display-only" unverified; mass-demotion toward
MONITORING = regime change in the ruler. (G) violates its own stated gate; renormalization
could systematically raise sparse-coverage scores; decouple the n/a display half.
Cross-cutting demand: stamp every flip.

### THE FIRST-PRINCIPLES GUARDIAN (vision + ledger)
Overall: the rare change-set the original vision recognizes — effort spent making
measurement honest rather than numbers impressive; A's refusal to reweight is the moat
working. Meta-warning: A/D/E all READ the ledger to steer design — legitimate, but once
tuned against resolved rows those rows are in-sample; the only rate ever put before a
customer is the rate on detections stamped AFTER the tuning. (B) the moat exemption is
the thesis encoded; strict mode converts a detection into a corroboration — the one trade
never to make casually; prefer quality-bar/expiry; let the ledger falsify (did any
excluded topic later break out?). (D) a scoring-input write in a reporting costume; the
maturity rule reads the future — cap day-counts at detection_date or disclose. (F) verify
nothing behavioral consumes stored stage before calling it display-only. (G) the standing
violation is the STATUS QUO; split display honesty (ship now) from renormalization
(referee first); confirm renormalization doesn't raise thin-coverage scores. Bottom line:
merge all seven; flip C now (+G display half if separable); hold B and D at their gates.

### THE EXPANSIONIST (global scale)
Overall: net scale-positive — honesty is the only thing that travels. The REAL
globalization blockers sit underneath: the English lexicon (non-English content will be
~100% catch-all → B becomes language policy), the US-only positioning regimes (FINRA/13F/
Form-4/Congress — G's renormalization architecture is exactly the multi-jurisdiction
model: SEDI/TR-1/EDINET contribute what exists, absent components honestly vanish), and
Google-only metered validation (promote the Wikipedia-referee thinking to a per-region
referee strategy). (C) in-process dict breaks at horizontal scale — move dedup to a shared
store before a second web process; (D) convert to a scheduled fill-only job after first
supervised run, batch the per-topic query; (E) make K a proportion; validation throughput
must scale with enrollment; (F) flip early — every quarter it waits gets more expensive.
G is the single most expansion-critical flag. Merge all seven.

### THE OUTSIDER (first-look VC/banker, plain English)
One sentence: "They score internet topics 0–100 on whether attention is about to surge,
and keep a timestamped scorecard of every call graded against Google Trends — including
every miss." The culture is the real asset (nobody dressing numbers writes the 0-FP
footnote in their own pack). The numbers say the product does not work YET: 10% blended,
26.9% on a coin-flippable 26, the thesis cohort INVERTED (2.3% vs 24%), and the house
backtest says the score is decoration at detection time. Defense (broken enrollment) is
plausible and unfalsifiable until the post-fix cohort resolves → "a pre-evidence company
with exceptional instrumentation; the entire bet is the next cohort." Pre-broken carve-out
= adjusted-EBITDA-shaped; survives ONLY while the blended 10% is published beside it,
forever. The 133 pinned "30.0/ROUTINE" instruments are fabricated numbers live today —
flip G fast (with a before/after snapshot). Jargon kill-list for anything client-facing:
Dark Matter, moat, LED, pre-broken, catch-all, N, GHOST feeds. Diligence digs: the
inversion (D's dry run answers it), sample sizes (6 market resolutions is six coin
flips, not a rate), and a PRE-REGISTERED success threshold for the post-fix cohort
written down BEFORE it resolves. Merge all seven; fund nothing on today's numbers.

### THE EXECUTIONER (delivery)
Two items not actually finished: **F is a near-no-op as diffed** (stage overwritten later
by signal_calibration_integration.py:1217–1228/1364 and detector:4741–4747; the behavior
test exercised a discarded layer). **D's write violates no-score-inflation as coded**
(INSERT omits calibration_multiplier → default 1.0 → ~900 ESTABLISHED topics transiently
serve UNDISCOUNTED vs today's effective 0.45; also the backfill's ≥14-days rule ≠ the
calibration fallback's days≥10+cycles≥40 rule → classes flip for some topics; enrollment
consequences must be stated). D rollback is clean (`maturity_reason LIKE 'backfill:%'`
tagged delete). G verified as claimed (flag consumed at signal_calibration_integration
:104/:1143/:1174 + market_signal_engine:57). RECOMMENDED SHIP ORDER: (1) fix F at all
three sites + D's INSERT on the branch pre-merge; (2) merge all flags OFF → deploy →
verify zero change; (3) record A's no-reweight decision + re-run trigger (post-fix cohort
≥30 races); (4) flip E (=2), verify slot mix; (5) flip C after founder picks window +
accepts global-dedup semantics; (6) flip B after 48h moat-only shadow count, watch
catchall_floor_log; (7) D's write after the delta report + founder sign-off; (8) flip G
after shadow score-diff + 3-platform n/a check + cache regen; (9) flip F last, announce
the label shift, run /frontend-consistency.

### THE ECONOMIST (founder-specified canon)
Overall: these are measurement-hygiene changes, and the ledger is the company's *Monetary
History* — the long, embarrassing-when-it-must-be series that settles arguments no pitch
deck can. A's refusal to reweight on noise is Malkiel's null-hypothesis discipline
practiced. Concerns concentrate on D (a score change through a side door — Bernstein:
the risk is the coupling you didn't measure), E (changing panel composition mid-series —
the sin F&S built their book to catch; R&R: headline rates move when composition moves),
and B (in Extremistan the one single-source expert signal you delay may outweigh every
junk fragment you block — and the cost is silent). The edge, on the ledger's own
evidence, is a SPEED AND BREADTH edge (M=80 at first sighting; losses by 1–4 days).
Verdicts: A APPROVE · B APPR-COND (shadow 60–90d; prefer expiry variant) · C APPROVE
(engagement is the price system of the attention economy; a price that feeds back on
itself carries no information — Smith) · D APPR-COND (what-if diff or decouple from
calibration) · E APPR-COND (K=2; permanent cohort segmentation; param_version) ·
F APPROVE (one good, one price; announce as definition reconciliation — anchoring works
on labels too) · G APPR-COND (a constant emitted regardless of the world carries zero
information; referee gate stands; set a review date).

**THE ECONOMIST'S PRESCRIPTIONS (the founder-requested expert methods):**
1. **Naive-baseline ledger column (Malkiel).** Run 1–2 dumb rules (e.g., enroll anything
   above a fixed mention-velocity floor) through the IDENTICAL ledger pipeline; publish
   engine-vs-baseline forever. The ledger currently proves honesty; a baseline column
   proves EDGE.
2. **Tail-capture rate + magnitude-weighted leads (Taleb).** Of each period's top-decile-
   magnitude Google breakouts, what fraction did the engine lead? A 26% that includes the
   giants is a business; a 26% of median races that misses every giant is not. Report-side
   only.
3. **Instrument silent evidence (Taleb).** A rolling "seen-but-not-enrolled" register,
   swept quarterly against Trends breakouts — until it exists, every published rate has
   an invisible survivorship subsidy. Bake the 0-FP-is-a-timeout-artifact caveat into the
   /accuracy/ledger payload itself; numbers travel without their footnotes.
4. **Freeze the panels; version every methodology change (F&S).** Every enrollment/sweep/
   definition change gets a param_version; the pre-change cohort stays a frozen,
   separately-reported panel. "Measured the same way since 2026" is worth more than any
   quarter's rate.
5. **Breakout-signature library at ~50 resolved races (R&R).** Cluster winner trajectories
   (breadth at first sighting, D-arrival lag, category, stage-transition speed) into named
   signatures; annotate new detections held-out/display-only until a backtest earns more.
   "This time is different" is answered with "no — it looks like these eleven prior times."
6. **Operationalize Kindleberger's stages.** Displacement (M-led early breadth) →
   informed-attention arrival (D — the credit-expansion analogue; the mining proved D IS
   the confirmation stage) → mainstream quorum (euphoria). Ship the display-only
   "informed-attention confirmed" marker; measure time-in-stage and stage-skipping — a
   topic that skips the D stage is a different animal (manufactured/event-shock attention),
   and that distinction is measurable today, score-free.
7. **Attack the 1–4-day losses (Malkiel + F&S).** The free-source fast-lane recheck for
   M/D-triggered candidates is the highest-expected-value operational change available;
   define the success metric (near-miss→LED conversion) BEFORE flipping.
8. **Pre-register every flag flip (Belsky/Gilovich + Zweig).** One paragraph before each
   flip: success metric, review date, revert condition. The builders are the biggest bias
   risk; this is the cheapest overconfidence insurance an Extremistan business can buy.
9. **Publish measurement completeness per score (Bernstein).** "Detection 62, measured on
   5 of 6 components" is defensible; silent renormalization is a smaller 30.0 pin. Risk
   is what remains after you think you've measured — say how much measuring happened.

## STATUS
Branch `integrity-recs-A-G` at `7e7708c`, all flags OFF, not merged. Two branch defects
identified by the board (F's three write sites; D's calibration_multiplier omission)
await the Chairman's instruction. Chairman — your decision per item.
