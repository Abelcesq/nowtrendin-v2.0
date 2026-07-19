# BOARD SESSION — Q1 (cliff decay) & Q2 (identical plateaus) — HOW TO PROCEED

**Convened:** 2026-07-18 (UTC 07-19 early) on the Chairman's direct question. **Material:** the
ruled volatility diagnostic (`audits/assessor/VOLATILITY_DIAG_2026-07-18.md`), fresh Wikimedia
referee data, code anchors, standing constraints. Six independent archetypes, identical evidence
pack, no cross-contamination; several made their own live pulls and code traces (noted inline).
**Chairman rules item by item; nothing here is a decision.**

---

## THE HEADLINE: the mechanism was identified during the session

The pack offered a hypothesis (hard 72h input-window rolloff). Four memos reasoned from it; the
**Executioner ran the discriminating diagnostic live and refuted it, then named and arithmetically
verified the actual mechanism**; the **Challenger's independent live pulls** (bistability) are
consistent with the Executioner's read. Standing of the evidence:

- **The embedded `score_history` block in `/scores/{key}` serves RAW STORED rows** (built at
  gravitational_anomaly_detector.py:9085–9093, no serve-time calibration) — the pack's code
  anchor conflated it with `get_topic_score_history` (:9340, a DIFFERENT route,
  `/scores/{key}/score-history`, which recalibrates live). One HTTP call per topic settles
  raw-vs-served.
- **tillis:** raw stored det 88.37 / conf 67.41 / overall 81.15 byte-identical across 6 cycles;
  served 88/67/78 — calibration is a pass-through. **Q2 cause is (i): the scorer writes identical
  raws.** Not calibration saturation, not INV-1.
- **The inputs did NOT vanish at the cliff:** tillis total_mentions stayed 8 through the cliff
  cycle (served TODAY by the standalone route — the "mentions null" gap afflicts only the
  embedded block's SELECT); every component (G=0, I=9.7, platform=50, D=0, P=0) static through
  plateau AND cliff. spain's confidence_decay ≈ 99.5 (fresh inputs) while det flipped
  94.24→25.0→91.96→94.25→25.1 — **bistable between two attractors on unchanged data.**
- **Named mechanism (code-anchored):** the dual-pathway blend weight `w` (dual_pathway.py:blend,
  wired at :4906–4964). `w = max(breadth_factor, magnitude_factor)`, each = deviation from the
  topic's own baseline, where the baseline is the **integer MEDIAN of the last 12 stored cycles**
  (`sorted[len//2]`, :4920–4923). A surge fills the window with high rows; the median flips
  DISCRETELY on the **7th cycle after the step-up**, collapsing `w` and releasing the full
  ~79-point pathway gap in one cycle (tillis: step-up 07-17T05, cliff exactly on the 7th run,
  07-18T16, det → expert_detection 9.7). Plateaus, cliffs, spain's flap, google's
  cliff-rebound-cliff, and the staggered timing all fall out of this one estimator.
- **Falsifiable predictions logged:** mamdani / taco / cyclosporiasis_outbreak (stepped up
  07-17T22) should cliff at the ~**2026-07-19T10 UTC** cycle (±1); russia (stepped 07-18T04) at
  ~**07-19T16** — absent renewed expansion. If they land, the mechanism is confirmed cohort-wide.
- **Challenger (independent):** spain was ALREADY toggling 94↔25 before the diagnostic's 6-cycle
  window opened — the diagnostic's clean "plateau-then-cliff" shape was partly window truncation;
  tillis's det+conf freeze as a PAIR vs its normally 0.1-granular late-June history proves the
  engine can produce fine variation and didn't during the plateau.

**Framing correction adopted by multiple memos (Challenger, Executioner):** the Wikimedia
comparison is a category error as posed — pageviews are an attention LEVEL; Detection is a
baseline-relative DEVIATION/gradient instrument. Spain at 1.7× baseline with expansion over
should NOT serve 94; the post-cliff ~25 LEVEL is defensible. What is indefensible is the SHAPE:
a 69–79-point single-cycle release, and BREAKOUT↔MONITORING flapping twelve hours apart on
unchanged data, are estimator artifacts — measurement noise we manufacture.

## THE SECOND HEADLINE: a latent INV-1 gap found by five of six

Independently found (Guardian, Outsider, Economist, Challenger, Executioner): the standalone
history route `get_topic_score_history` re-runs LIVE calibration (today's maturity state + AI
floor) on rows of ANY age with **no `_serve_row_is_stale` guard** — while `/scores` serves
stored values for rows older than 48h (INV-1). Consequences: served history ≠ what was served
at the time; the same query on different days can return different historical values; the exact
35.6→100 inflation class INV-1 was built to stop is live on that endpoint. The Outsider:
"a history that changes with your software releases is not a track record; it's an opinion with
a version number." Benign on the plateau topics today (calibration passed through); a divergence
bomb on maturity-boost/AI-floor topics. All five recommend extending the stale-serve rule to the
history route, founder-confirmed (it changes served numbers), flag-gated, trivial rollback.
Interim prohibition (Guardian): do not cite that route's served values as evidence about scorer
behavior; use the raw embedded block.

---

## MEMO SUMMARIES (condensed; verdicts verbatim in class)

**CHALLENGER** — Q1: REJECT any score change now; APPROVE-WITH-CONDITIONS no-change +
diagnostics + display-only annotation. The accuracy defect is the PLATEAU (a stale 88.37 served
36h), not the cliff ("deferred honesty"). Attacks: n=1 level-vs-gradient referent; window
truncation hid bistability; single-regime sample (one news wave) forbids window redesign.
Q2: APPROVE-WITH-CONDITIONS diagnostics; four hypotheses not three — (i-a) innocent determinism
vs **(i-b) carry-forward rows asserting scoring events that didn't happen** (audit contamination
if true); production-path verification FIRST (repo-vs-deploy drift found); diagnostic surface
must serve null-not-zero. Forbids: smoothing, jitter, calibration changes pre-evidence,
publishing history externally while the recalibration gap stands.

**FIRST-PRINCIPLES GUARDIAN** — The moat is the RISE side; the decay side carries no ledger
weight, so the burden of proof is asymmetric. Q1: cliff as served APPROVE (honest; of the four
named sins — fabrication, inflation, staleness, circularity — it commits none; a smoothed 94
would commit staleness); input-level age-weighting APPROVE-WITH-CONDITIONS behind the five-step
gauntlet (enrollment-crossing unchanged-or-earlier on EVERY topic, no inflation); output
smoothing REJECT. Unique warning: **if Wikipedia pageviews become a tuning target for decay,
they are contaminated as the ledger's independent referee** — validator and tuning signal must
never be the same data. Q2: expect it to dissolve into Q1 (deterministic scorer on static inputs
is reproducibility WORKING); ship raw/mentions instrumentation first; history INV-1 alignment
to the founder as its own ruled item.

**EXPANSIONIST** — Q1 APPROVE-WITH-CONDITIONS (staged): a 70-point single-cycle swing makes the
feed un-integrable for alert-driven enterprise clients — but the fix is never output smoothing.
Mechanism-confirm → display-only post-burst annotation (the biggest legibility win per unit
risk; generalizes across locales because it annotates input recency, not content) → component-
level change only behind an enrollment-invariance backtest. Q2 APPROVE diagnostics; scale finds:
the live-recalibration of history is an **O(history) compute amplifier on a fragile read path**
(scale debt — design deliberately before 100× forces it); backtest referees must include
per-language Wikimedia or we tune decay to Anglophone rhythm. Forbids jitter, INV-1 weakening,
en.wikipedia-only validation.

**OUTSIDER** — "The cliff is not the misrepresentation — the plateau is." Spain served 94 for
twelve hours while the referee showed the wave receding; any remedy slowing the DROP makes the
score MORE stale. The honest direction: within-window recency weighting so declines start
EARLIER (rises untouched → no enrollment delay) — behind mechanism-confirmation + a backtest
whose kill criterion is the lead-time distribution. Q2: favors (i); diagnostic script not a new
public endpoint (read-path fragility); found the history-recalibration gap independently and
rates it "the most diligence-dangerous fact in this material." Point-blank questions: "Which
number do you defend — the 94 served while Wikipedia receded, or the 25 that arrived a day
late?" / "Same history query after your next calibration deploy — same numbers? Today: no."

**ECONOMIST** — The canon's answer to the Chairman's decay-shape question: attention decay
should be **ASYMMETRIC (down faster than up — Kindleberger's revulsion), HEAVY-TAILED (Taleb:
never force a decay template; some surges genuinely end abruptly), and CONTINUOUS in the
inputs' own terms**. This cliff fails not for being fast but for being **symmetric-instant both
ways and quantized to cycle boundaries** — the signature of machinery, not manias ("processes
don't know our cron schedule; windows do"). A frozen price is a halted market, not a stable one
(Smith). Sharp code catch: the 0.01-precision plateau series cannot have come from the rounding
history endpoint — the values were **identical at compute time** (favors (i), disfavors
saturation; Taleb: "calibration is clamping" is narrative fallacy on current evidence).
Prescriptions: referee-PANEL not anecdote (F&S); the Malkiel null for any window change (beat
the incumbent on ledger outcomes, not smoothness); tail-first evaluation; a standing
Kindleberger asymmetry audit in the assessor; Bernstein saturation gauge; Smith price-integrity
rule (label stale, never repaint, never dither); Goodhart guard (volatility-flag count must
never become the score's objective).

**EXECUTIONER** — Ran the diagnostic live; mechanism found (above). Q1: input-window remedies
**CUT — wrong locus** (inputs did not age out at the cliffs; verified); "nothing forever"
REJECTED as terminal (an instrument serving BREAKOUT and MONITORING twelve hours apart on
unchanged data is a number we cannot defend, and it refires flags indefinitely); the one
narrow score-affecting candidate = **replace the integer-median baseline with a continuous
estimator with hysteresis** — "not smoothing the score; smoothing the RULER" — SHIP-LATER,
flag-gated default OFF, offline replay backtest on stored per-cycle inputs (cheap — all
persisted), hard bar: no systematic delay of upward enrollment crossings. Q2: **no engine
change — CLOSED as cause (i), verified**; identical raws are the honest output of a
deterministic scorer on a static snapshot; bounded confirmation sweep on the remaining four
topics; corrected the record: the mentions diagnostic was always runnable via the standalone
route. Ship order (containment-sequenced): assessor patch → confirmation sweep → history
instrumentation columns → cohort replay + the 07-19 predictions → founder packet (estimator +
INV-1 history guard). "Steps 1–4 are containable failures: nothing in them can move a served
score."

---

## DISAGREEMENTS (signal, not noise)

1. **The mechanism.** Pack hypothesis (72h input-window rolloff) was adopted by Expansionist /
   Guardian / Outsider / Economist as the working model; the Executioner's live component trace
   REFUTES it (inputs static through the cliffs) and pins the median-of-12 baseline flip; the
   Challenger's bistability evidence supports the estimator read. Resolution is empirical and
   already scheduled: the cohort replay + the falsifiable 07-19 cliff predictions. Every
   score-affecting recommendation was conditioned on mechanism confirmation, so the disagreement
   collapses into one read-only test.
2. **Which score-affecting remedy, if any.** Input-age decay weighting (Expansionist/Outsider/
   Economist/Guardian, conditioned on the window mechanism) vs baseline-estimator continuity/
   hysteresis (Executioner, conditioned on the median mechanism) — mutually exclusive loci; the
   replay test picks. All six agree the remedy is at the INPUT/ESTIMATOR level, never the output.
3. **Is the cliff or the plateau the defect?** Guardian: the cliff is honest, defend it.
   Outsider/Challenger: the plateau (a stale high served 36h) is the real exposure; the cliff is
   deferred honesty. Economist: both are faces of quantization; the shape, not the speed, is the
   artifact. Executioner: the LEVEL is defensible, the SHAPE is not. Not blocking — every course
   of action is compatible with all four readings.
4. **Annotation timing.** Expansionist/Outsider/Guardian/Economist: ship the display-only
   post-burst annotation now. Executioner: SHIP-LATER — sequence after the estimator ruling so
   the copy matches the mechanism that ships (3-platform frontend cost). Chairman's call on
   sequencing only.
5. **Wikimedia referent validity.** Pack framing (score should track the referee's smooth decay)
   vs Challenger/Executioner (level-vs-gradient category error; the post-cliff level is
   defensible). The Economist's panel prescription + the Guardian's contamination warning bound
   how the referee may be used either way: panels not anecdotes, and never as a tuning target.

## UNANIMOUS FORBIDDEN LIST (6/6, binding on every course)

- NO output-level smoothing, EMA, damping, hysteresis floors, max-drop caps, or display
  interpolation of served scores — manufactured stability; delays enrollment; spends the moat.
- NO jitter/noise/dither to break plateaus — manufactured variance is fabricated data.
- NO retroactive rewrite, deletion, or backfill of stored history rows (365-day retention).
- NO weakening of INV-1 anywhere; consistency is achieved by EXTENDING the guard to history,
  never removing it from /scores.
- NO silent shifts of ledger enrollment timing — enrollment-crossing invariance is a named,
  hard backtest gate on any estimator/window change.
- NO tuning any parameter to quiet the assessor's volatility flags (Goodhart), and no
  hand-tuning of _BREADTH_DELTA_FULL / _MAG_DELTA_FULL / MIN_BASELINE_CYCLES off these 19 topics.

## DECISION TABLE FOR THE CHAIRMAN

| # | Item | Class | Board standing |
|---|---|---|---|
| 1 | Close Q2 as cause (i) — identical raws verified live (tillis); bounded confirmation sweep on white_house / shutting / jordan / andy_burnham (read-only, paced) | OPERATIONAL | Executioner verified; Economist/Guardian predicted; none oppose |
| 2 | History instrumentation: add total_mentions, attention_magnitude, n_mainstream_platforms, mainstream_ratio (w), detection_pathway to the EMBEDDED score_history block (:9085) — additive, null-not-zero (Challenger condition) | OPERATIONAL | 6/6 |
| 3 | Cohort replay verification: recompute median-of-12 from served per-cycle fields for all 19 topics; check the 07-19T10 / 07-19T16 cliff predictions | OPERATIONAL (read-only) | 6/6 — THE mechanism arbiter |
| 4 | INV-1 stale-serve guard on `/scores/{key}/score-history` (rows > SERVE_LIVECAL_MAX_AGE_H serve stored) — flag-gated; before/after diff on 5 old topics | Serve-consistency, FOUNDER-RULED (changes served numbers) | 5/6 flagged it; 0 oppose |
| 5 | Display-only "post-burst / input-freshness" annotation (input-fact-driven, founder-confirmed copy) | OPERATIONAL (user-visible) | 4 now / Executioner ship-later (sequencing only) |
| 6 | Baseline-estimator continuity + hysteresis (replace integer median-of-12) — ONLY if item 3 confirms; flag-gated default OFF; offline replay backtest on stored inputs; HARD GATES: no systematic delay of upward enrollment crossings, no inflation, flap count down, tails unclipped | SCORE_AFFECTING (founder + backtest + param bump + serve_payload regen) | Executioner proposes; others' input-age variant dies if item 3 confirms the median mechanism |
| 7 | Assessor follow-ups: cycle-7 catchup classification, Kindleberger asymmetry audit, Bernstein saturation gauge, referee-panel build-out | OPERATIONAL (assessor-only, param-bump aware) | Economist prescriptions; none oppose |
| 8 | Scale-debt log item: live-recalibration compute amplifier on the history read path (design before 100×) | OPERATIONAL (log now, design later) | Expansionist |

**Chairman — your decision per item.**
