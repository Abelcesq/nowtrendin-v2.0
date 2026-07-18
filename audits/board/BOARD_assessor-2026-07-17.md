# BOARD ANALYSIS GATE — Scoring Assessor Snapshot #1 (ASSESSOR_2026-07-17)

**Convened:** 2026-07-17 (evening, UTC 2026-07-18 00:10–00:50) · **Snapshot under review:**
`audits/assessor/ASSESSOR_2026-07-17.md/.json` (param `assessor-v2.b95dabebb4`, born
`UNVERIFIED_PENDING_BOARD_REVIEW`) · **Mandate:** the Chairman's directive — independent critique
of each finding + fresh outside-data cross-check + verify/refute per work-queue item, BEFORE any
finding teaches or is implemented. Six independent archetype agents, identical evidence pack,
no cross-contamination. **Chairman rules item by item; nothing below is a decision.**

**Evidence pack (gathered at review time, not reused from the snapshot):** live `/accuracy/ledger`
(tracked-race 24.2% n=33 · blended 9.2% · byEpoch v1 9.7%/v2 4.8%); live `/health/collectors`
(all HEALTHY, reddit DEGRADED=founder-deferred); live `/scores` state of all 19 flagged topics;
fresh Google daily-trending US RSS (00:22 UTC — sports/entertainment, 500+–2000+ traffic, no
genuine match in top-600 served); Wikimedia en:Spain pageviews (9.5–12k baseline → 34,939 on
07-15, ~3× and rising); `/crypto` 7d movers (quiet tape, BCH −10.3% the only large move).
Several members made their OWN independent pulls beyond the pack (ledger, Spain, Tom Brady,
Oscar Piastri pageviews; the assessor tool's source code) — noted inline.

---

## UNANIMOUS PRELIMINARY: the instrument obeyed the rebuild conditions

All six verified in the raw JSON (not the prose): every task carries `task_class` +
`held_out_derived` + `shadow` + `ruling_id`; lifecycle runs shadow/WARN-only; abstentions are
honest; reddit honored as DEFERRED not FAILED; solutions are diagnostic pointers with zero tuning
prescriptions and zero ruling contradictions; the ledger prints ABOVE the module grades as THE
number; the internal pass % carries the internal-only caveat. The laundering paths rejected in
the pre-run review are closed in the artifact. The Challenger's summary: "a successful shakedown
cruise, not a findings document." The Guardian: "this is the teacher I asked for."

---

## MEMO 1 — THE CHALLENGER (condensed; independent re-pulls: ledger, en:Spain, raw JSON)

**Independent verification first.** Ledger arithmetic reconciles (87 = 8+6+73; 33 = 8+6+19) —
EXCEPT the epoch split: v1 resolved 72 + v2 resolved 21 = 93 ≠ 87, gap exactly the 6 same-day
rows. Two denominators for "resolved" in one payload; a skeptical auditor finds it in five
minutes. Predates the assessor (ledger-report defect) but the assessor republished it unflagged.

**The referee module is broken and its A grade is an artifact of its own defect.** C_ACCURACY
"A (2/2)" with 18 INSUFFICIENT = 90% abstention. Stated reason "thin pageview history" for
spain/japan/canada/ukraine/mexico/england/fifa is NOT credible — I fetched en:Spain myself: 21
clean daily points in one request. The fetch/resolve path is defective and mislabeling its own
failure as data absence. No letter grade should print at graded-n=2 (nor E's "C" on n=1).

**Items 1–19 (class): APPROVE-WITH-CONDITIONS** as a diagnostic worklist only. The check
conflates three things and two are not defects: (a) a genuine breakout IS high std — the check
flags the thesis working; live reads show every flagged topic at/near its range max. NAMED
REFUTATIONS (cold-start or confirmed-surge shapes; flag should not have fired without a
maturity/direction discriminator): **rikers, trump_fires, cyclosporiasis_outbreak,
cyclosporiasis_cases, tillis, spain**. (b) Thin-input variance (tillis 8 mentions/2 platforms
etc.) — the flag is really "thin input"; the proposed diagnostic is right for this subset.
(c) The PASS side is contaminated: std 0.0 labeled "moving normally" (canada, china, florida,
election, agent) is affirmatively false — a frozen served score has three known non-attention
causes (INV-1 stale-serve, stale serve_payload, wedged prewarm). The check may be measuring
RECOMPUTE CADENCE, not attention stability — the same warmth/cycle-phase confound class that
demoted the catch-all %. Threshold (fires ~12) unbacktested and arbitrary. Raw 6-value series
not stored in the finding — unverifiable from the artifact. Would change my mind: the diagnostic
run with raw series + per-cycle volume, showing high-volume MATURE topics oscillating
(down-up-down) rather than rising. Class: OPERATIONAL; any remedy SCORE_AFFECTING.

**Item 20: the 2/10 figure REFUTED as a defensible number; diagnostic APPROVE-WITH-CONDITIONS.**
Four independent grounds: unvalidated substring matcher (fresh run's only "matches" were
"boston"→aliyah boston, "search_rubble"→gbi warrant — even the numerator is unverified); biased
reference class (same-day sports matchups the engine deliberately does not model); n=10 one day;
unpinned scan scope (top-600 of 3537; check's own denominator not pinned — the exact unpinned-
denominator disease the catch-all % was demoted for). Also 2/10 implies 8 misses, evidence names
4 — incomplete artifact. Coverage gauge under the catch-all-% rule: internal-only, never
published as "recall." OPERATIONAL.

**Item 21: REFUTED.** Own Wikimedia pull: ~10k baseline → 26k (07-06/07-10) → 33.9k (07-14) →
34.9k (07-15); live engine back at det 94.2 BREAKOUT. The stage machinery was RIGHT; the WARN's
own RECURRENT caveat was prescient. Close, log the refutation. Caveat: item 21's prescribed
diagnostic ("compare against the referee") is currently impossible — the referee is broken
(above). Referee fix OPERATIONAL (assessor, not engine).

**Instrument defects (fix before snapshot #2, all OPERATIONAL):** 1) referee resolver/fetch
broken; abstention reasons must be truthful. 2) epoch reconciliation (93 vs 87) — reconcile
before any epoch figure leaves the building; print tracked-race PER EPOCH or the headline
invites the "your current engine is worse than your number" diligence attack. 3) "moving
normally" at std 0.0 → own WARN class. 4) no letter grades below min graded-n. 5) findings must
carry the raw values they judged.

## MEMO 2 — FIRST-PRINCIPLES GUARDIAN (condensed)

**Items 1–19: APPROVE-WITH-CONDITIONS as ONE consolidated class finding** (nineteen tickets is
one finding with a topic table). Ranges verified real — live reads sit at the maxima almost
exactly. Hidden structure the per-topic framing missed: (a) thin-input topics — the deeper
question is not volatility but whether BREAKOUT/STRONG on 8 mentions from 2 platforms is a
defensible read at all (tillis det 88.4 on 2 platforms the sharpest instance) — accuracy above
all; (b) high-volume topics swinging 25→94 in 36h points to a CYCLE-LEVEL shared cause
(collector flapping across a cycle; reddit DEGRADED is the live suspect) — investigate ONCE
across cycles, not per topic; (c) "shutting"/"trump_fires" are verb fragments — volatility as a
symptom of fragment quality; reroute to the topic-quality worklist.
**Principle-drift detected:** the gap text "hard to act on" is advice-flavored, and the natural
"fix" (smoothing/damping) is score-shaping — it would also delay ledger enrollment and SHRINK
THE MEASURED LEAD — the moat itself. A smoothed number we can't defend is worst of all. Rewrite
gap text to "score swings exceed plausible attention dynamics — verify input integrity per
cycle." Diagnostic OPERATIONAL; any remedy SCORE_AFFECTING.

**Item 20: APPROVE-WITH-CONDITIONS as an awareness gauge; REJECT any use as a recall target.**
The largest principle-drift in the snapshot: Google daily-trending is a LAGGING same-day fame
index; optimizing recall against it steers the engine toward becoming a Google Trends mirror —
against the thesis. Missing "dodgers vs yankees" may even be hygiene. Honest topical recall on
the fresh list is 0/10 (substring inflation). Conditions: never a KPI; fix matcher + pin
denominator; filter/flag ephemeral fixtures; the collector look is fine and read-only. If anyone
proposes adding trending-RSS terms as scored topics, that is §16 SOURCE ONBOARDING, not lexicon
housekeeping — flag now so it cannot slide in.

**Item 21: check APPROVED as designed (model citizen); instance REFUTED by both fresh sources.**
BREAKOUT was correct; FADING was a sampling-phase artifact of reading a bursty topic in its dip
— the false-ENDED failure mode the pre-run board predicted; the RECURRENT class is load-bearing
and this is its first live proof. Record the refutation in the snapshot's board annotation —
a refuted instance is itself curriculum. Class if stamped: RULED (stage rules already under
founder+backtest lock).

**Instrument notes:** compliant with all rebuild conditions. Watch (not editorialize): v2 epoch
4.8% vs v1 9.7% on n=21 — too small to panic or celebrate; it is the moat working as designed.
Fixes for next param bump: the std-0.0 label; per-topic flood → class consolidation.

## MEMO 3 — THE EXPANSIONIST (condensed)

**Items 1–19: APPROVE-WITH-CONDITIONS (class).** The most scale-portable check in the snapshot
(pure arithmetic, language-agnostic) but unconditioned on input volume — conflates THIN-INPUT
flappers (tillis 8/2, amnesty 8/4, cyclosporiasis_cases 9/6, rikers 12/6, trump_fires, shutting,
taco, mamdani, jordan — REFUTED as individual actionables; expected sampling noise) with
HIGH-VOLUME genuine jitter (spain 105/13, google 104/16, america 136/12, russia, texas, japan,
andy_burnham, white_house, youtube — VERIFIED as a real look). Scale-fatal flaw: "inspect input
volume per topic" is a MANUAL step — 19 hand investigations today is 1,900 at 100×; the check
must compute its own diagnostic (emit per-cycle volume + score-vs-volume covariance in the
evidence field; auto-bucket below-floor topics into an expected-noise stratum) and emit
aggregates + top-K exemplars. Also: half the flagged subjects are Anglophone extraction
fragments — the check should cross-reference the fragment gate. Opportunity: volume-conditioned
stability disclosure is a sellable institutional metric. OPERATIONAL (check redesign); any score
damping SCORE_AFFECTING.

**Item 20: APPROVE-WITH-CONDITIONS the check's existence; REFUTE the "recall gap" claim as
evidenced.** Hardest flag: it HARD-CODES A LOCALE (US English same-day list, sports/entertainment
ephemera). Grading recall against that denominator teaches the system to chase zero-enterprise-
value ephemera — more parochial, not less. Substring matcher will fail worse in non-Latin
scripts. Real arithmetic on the wrong denominator with an unreliable matcher. Opportunity — the
reason to KEEP the check: Google trending exists free PER COUNTRY, Wikimedia per language;
rebuilt as a stratified multi-locale recall panel (category-filtered, entity-matched,
full-corpus, locale as parameter) it becomes the global-coverage page an enterprise buyer
diligences. Conditions: durability filter; entity matching; full-corpus scan; LOCALE_PROFILES.
Missed matchups → discovery/lexicon worklist as candidates at most. OPERATIONAL.

**Item 21: REFUTE the finding; APPROVE continued shadow existence.** Both referees refute
(pageviews ~3×; engine back at 94.2). The real defect is in the ASSESSOR: its C.referee_surge
returned INSUFFICIENT "thin pageview history" for spain while the board pulled 21 clean days
from the same free API — the instrument blinded itself on fetch depth, then issued a lifecycle
look it couldn't referee. At 100× topics the referee abstains everywhere and module C grades on
n=2 ("A" on two data points is not a grade). Conditions: ≥21d referee window; lifecycle look
requires a non-INSUFFICIENT referee before emitting even a shadow WARN; per-language referee
selection (es.wikipedia etc.) is the scale-correct design. RULED (closure under the standing
stage-rule gate) + OPERATIONAL (fetch-depth fix).

**Cross-cutting:** snapshot is structurally US/English end-to-end — extend FEED_PROFILES to
LOCALE_PROFILES before a second referee/trending source is wired; tiny-denominator module grades
must never leak externally; reddit DEGRADED = founder-deferred, no action; 19 templated items
prove the aggregates+top-K condition's necessity.

## MEMO 4 — THE OUTSIDER, VC/banker (condensed; independent re-pulls: ledger, en:Spain)

**One sentence for my partners:** "They measure where public attention is heading before it
shows up in Google Trends, and they keep a tamper-evident, held-out scorecard of how often they
actually got there first — currently 24% of the races they demonstrably entered, on a very
small sample." That sentence survives diligence.

**Do the numbers smell managed? No — honest and small.** Re-fetched everything myself; matches
to the digit. A managed deck would not print 9.2% above the fold. BUT: (1) 8/33 carries a
confidence band of roughly low-teens to ~40% — "24.2%" to one decimal is false precision
externally. (2) **The epoch table undercuts the story and nobody flagged it:** v2 epoch 1 LED /
21 resolved (4.8%) vs v1 9.7% — first number a hostile diligence team circles (innocent
explanations exist: young races; patience-window adverse selection toward fast breakouts —
but say it proactively). (3) "0 false positives" is currently guaranteed by construction (a FP
takes up to a year to exist under the 365d window) — disclose that. (4) **Of the 8 LED wins,
ZERO are referee-corroborated** (6 uncorroborated, 2 unchecked) — probably instrument failure
(blind referee), but as printed the moat number rests on unconfirmed wins. Fix referee → re-run
corroboration BEFORE this number nears a data room.

**NEW WORK-QUEUE ITEM (outranks most of the queue): the blind Wikipedia referee.** Abstained
"thin pageview history" on spain/england/japan/mexico/canada/fifa while one free API call
returns 21 full days. It hollowed out module C (an "A" over 18/20 abstentions — the two graded
checks are the two easiest), made item 21's prescribed diagnostic impossible, and plausibly
explains the 0/8 LED corroboration. OPERATIONAL, HIGH: debug resolve/fetch against live
Wikimedia REST; re-run referee corroboration on the 8 LED wins after the fix.

**Items 1–19: APPROVE-WITH-CONDITIONS (class).** Main contribution — **the minima cluster**: at
least 11 of 19 topics bottomed in a tight ~24–27 band inside the same 6-cycle window (spain
25.0, mamdani 24.7, white_house 24.76, japan 23.9, america 23.6, russia 24.4, texas 25.9,
trump_fires 24.3, google 27.1, youtube 26.5). Nineteen independent topics do not independently
choose the same floor — ONE systemic bad cycle (restart/cold cache/scoring on partially-landed
inputs; this shop has documented exactly this failure class). Condition 1: run the diagnostic
AGGREGATED first — which cycle held each minimum? If they coincide: one ticket, operational fix
(don't score mid-restart / mark the cycle). Condition 2: split by volume; the real question
lives in the high-volume names. Named exceptions to judge individually: amnesty (std 12.0 —
sits exactly on the apparent threshold, no low-band signature; where did 12 come from?),
andy_burnham (floor 12.4), tillis (floor 12.6 — different signature). Point-blank question:
"Did these nineteen scores hit their minimum in the SAME cycle? Pull timestamps against the
deploy/restart log before anyone opens nineteen tickets." OPERATIONAL; follow-ons re-class.

**Item 20: APPROVE-WITH-CONDITIONS.** Evidence real — worse than real: honest fresh read is
0/10 (both "matches" substring accidents). Matcher manufactures false recall (use the alias
layer); scheduled same-day fixtures are outside the thesis and should be segmented out. **The
defense I will NOT accept:** "same-day trending is unfair" — tom brady, oscar piastri, epic
games, rhea ripley are durable entities; an entity trending on Google that the engine never
served is, in the house's own language, a pre-broken race — a race never entered. Genuine
coverage misses; exactly what discovery collectors exist to prevent. Two-bucket reporting
(scheduled/ephemeral vs durable entities), entity matching, coverage gauge never an accuracy
KPI. OPERATIONAL.

**Item 21: REFUTE the instance; APPROVE the check.** Own pull confirms attention ~3× and
climbing at the exact moment the assessor read FADING. Log as the D-module's first track-record
entry — the WARN-only probation accumulating calibration history is working. OPERATIONAL
(closure); stage-decay changes remain SCORE_AFFECTING. No RULED exposure found in any item.

**Three questions before any money:** (1) why is v2 epoch 4.8% vs v1 9.7%, and how many
resolved v2 races before 24.2% is quotable? (2) zero of eight LED wins referee-corroborated —
instrument failure or truth failure, and which will you prove first? (3) which single number
would you defend under oath? (Right answer: tracked-race with its denominator; if it's any
internal %, stop the meeting.) Queue should collapse from 21 items to ~4.

## MEMO 5 — THE EXECUTIONER (condensed; read the assessor source at `tools/scoring_assessor.py`)

**Compliance audit passed** (stamps populated; D excluded from grades; reddit DEFERRED;
all 21 solutions diagnostic; zero ruling contradictions). "The danger surface the board feared
is closed in this artifact."

**Instrument defect that reframes items 1–19:** cross-referenced all 19 ranges against live
scores — **in 19 of 19 cases the topic's CURRENT detection equals the MAXIMUM of its range**
(spain 94.2=94.25, rikers 96.3=96.31, tillis 88.4=88.37 …). Every flagged history is a series
ending at its own high: these topics ROSE into the current cycle. A fixed std>12 line cannot
distinguish a genuine surge (a step up — the thing the product exists to detect) from a sawtooth.
It fired on 19/48 (40%) of a top-served cohort, predominantly on successful arrivals — an alarm
describing the normal regime; alarms that fire on success get ignored, and then the real flap
goes unread. Threshold set a priori, never derived from the fleet's distribution.

**Items 1–19: SHIP as ONE batched read-only diagnostic** (NOT 19 sessions), low-input subclass
first (tillis 8/2 first; the "single flapping source" hypothesis is genuinely live under ~15
mentions); high-volume names ride along, expected to close "surge, real." Method: one scratchpad
script, endpoints-only, batch-paced per §13 — per topic pull score_history, align per-cycle
detection vs mentions vs platforms, compute the discriminator the std check lacks (sign-flips of
first differences): monotone rise + rising mentions = SURGE (close); alternating flips + a
toggling source = FLAP (report; remedy is a separate proposal). Output one table to
audits/assessor/. Rollback: none needed — zero writes. FOLLOW-ON (assessor code, separate item):
surge exemption in B.volatility (suppress WARN when window is monotone-rising with mentions) or
distribution-derived threshold; param bump v2→v2.1, trend-line discontinuity annotated, git
revert as rollback, verified by re-run + WARN-count diff. Without it every future snapshot
re-emits ~19 medium items per breakout wave — alarm fatigue by construction. OPERATIONAL.

**Item 20: SHIP-LATER; the finding as evidenced is REFUTED; the underlying question is real.**
Verified AT SOURCE (`assess_outside`): (1) it matches the 10 RSS titles against the 60-topic
COHORT, not the 3,537-topic served feed — recall understated by construction; (2) matching is
any single word >3 chars substring-contained in a concatenated blob — simultaneously understates
and overstates. 2/10 is not a number we can defend. The gap itself is independently attested
(improve-system #1: 2/19) but thesis-sensitive. Ship-and-verify order: (1) fix the check
(full-feed scan, phrase/entity matching, ephemeral-vs-entity class split, param bump);
(2) re-measure 5–7 daily snapshots; (3) only THEN a founder-facing discovery/lexicon worklist.
Do not touch collectors off one unsound reading. OPERATIONAL. Caution for the record: "add
whatever Google trends we missed" must remain a MEASUREMENT, never a mandate.

**Item 21: CUT (close as validated, no action) — and that is a GOOD result.** Check ran exactly
as ordered; outside data refutes the look; keeping BREAKOUT was CORRECT — a stage-decay rule
acting on this look would have demoted a topic mid-resurgence. Log as shadow-scorecard
observation #1 for D.lifecycle (outcome: engine right; this data point counts toward the
STEADY-monkey null, on the null's side).

**Ship order:** 1) item 21 closure + scorecard note (zero risk). 2) batched 1–19 diagnostic
(read-only; produces the evidence everything else depends on). 3) E-check fix + B-check surge
exemption as ONE assessor patch, one param bump, one snapshot re-run to verify (B WARNs collapse
toward the true flap set; E measured against the full feed). 4) re-measure E a week; only then
any founder-facing worklist. **Nothing in this queue is SCORE_AFFECTING; nothing needs a feature
flag; every step is git-revertible or pure-read.** CUT as not worth the surface: per-topic
sessions on the 10 high-volume names; any lexicon/collector work sourced from item 20's current
evidence — fix the ruler before cutting the board.

## MEMO 6 — THE ECONOMIST (condensed; independent pulls: raw JSON 113 findings, en:Spain,
Tom Brady, Oscar Piastri pageviews, live /history)

**Items 1–19: APPROVE-WITH-CONDITIONS (class), OPERATIONAL.** (Taleb/Malkiel/Kindleberger/
Zweig.) Std over SIX observations of a fat-tailed generator has enormous sampling variance; the
unregistered ~12 threshold flagged 40% of the cohort — an alarm measuring normal behavior; no
stated null (for thin topics the null is strong: attention at 8–17 mentions IS volatile; a jumpy
score there may be the honest read, and smoothing it away is the inflation-adjacent sin of
manufacturing false stability). **Independent confirmation of the common factor:** the range
LOWS cluster tightly at ~24–27 across ten unrelated topics while all currently serve 63–96 —
"ten unrelated topics do not independently choose the same trough." Conditions: (1) FIRST the
cross-sectional co-movement test — if the lows share cycle timestamps (judged likely), items
1–19 collapse into ONE systemic ticket (deploy/cold-cache/serve-phase artifact — the house's
documented artifact class: the 33↔68 catch-all swing, INV-1); (2) volume-split before any
topic-level conclusion; thin topics must reject the sampling-noise null against a volume-matched
baseline; (3) named exceptions **spain and japan** — the outside referee shows spain's attention
genuinely tripling; some of that volatility is TRUE attention volatility (World-Cup burstiness);
a system that reports it is telling the truth — do not "fix" it; (4) re-derive the threshold
from the cohort's own dispersion (top decile), require 2 consecutive windows, register both in
the manifest.

**Item 20: APPROVE-WITH-CONDITIONS, OPERATIONAL.** (Malkiel — the null won; Taleb — Extremistan;
Bernstein.) **Cross-check proves the misses were not attention arrivals:** Tom Brady pageviews
flat ~5.5–6k/day, no surge; Oscar Piastri DECLINING (4.0k→1.3k). Small-traffic ephemeral query
patterns; failing to serve "rangers vs braves" is not a thesis failure — the null (most daily-
trending queries are noise) carried the day on the very items the check flagged. HOWEVER recall
against external trending is a legitimate COVERAGE gauge, and the day WILL come when a genuinely
enormous surge is missed — this check is how we'd know. Conditions: registered traffic floor
(grade only qualifying items; a day with none = honest INSUFFICIENT); **referee-confirmed
misses only** (a miss counts only when the independent surge referee confirms real attention
arrived); entity resolution + full-corpus scan; "X vs Y" matchup class registered and excluded;
any discovery-collector expansion through §16.

**Item 21: REJECT the work-queue item (concern REFUTED); commend the check's conduct.**
(Taleb — silent evidence; Friedman & Schwartz — trust the long series.) Spain ~3× baseline
through 07-14/15, still ~2.3× on 07-16; BREAKOUT corroborated by an independent referee; FADING
was a trailing-window artifact of the same depressed cycles driving items 1–19. **NEW FINDING
(assessor defect, OPERATIONAL):** C abstained on spain "thin pageview history" while Wikimedia
serves a complete series for "Spain" — person-named topics resolved (Donald Trump, Andy Burnham
passed); the lowercase common-noun key failed title resolution. An abstention caused by
instrument failure masquerades as epistemic humility — silent evidence inside the instrument.
Fix title resolution; log resolution failures distinctly from genuinely thin histories.

**Cross-cutting:** 8/33 ≈ 24.2% carries a 95% interval of roughly 12–41% — month-over-month
movement inside that band is noise; v2-epoch 4.8% on 21 resolved is nearly meaningless with
1,121 pending under the 365d patience window (the denominator is mostly unhatched eggs, by
design). Suppress letter grades below a registered minimum n.

**PRESCRIPTIONS (canon-tied):** 1) standing common-factor decomposition — whenever ≥K topics
flag in one window, test for shared-cycle co-movement FIRST (R&R panel method). 2) every check
states its null + threshold provenance in the manifest (Malkiel) — this snapshot's two biggest
interpretive errors were missing nulls. 3) volume-conditioned dispersion baselines (Taleb) —
one std threshold across 8-mention and 136-mention topics is a category error. 4) tail-weighted
recall ledger (Extremistan): register every external trending item above the traffic floor,
referee-confirmed, hit/miss + lead — a 2/10 on 500-traffic matchups is noise, but one missed
500k-traffic surge would be the finding of the quarter; build the instrument that can see that
day. 5) persistence (2 windows) + distribution-derived thresholds (Zweig) — a 40% alarm rate
teaches everyone to stop reading. 6) always ship the Wilson interval with the tracked-race rate
(F&S/Bernstein). 7) START THE ENGINE–REFEREE CORRELATION SERIES NOW (drift alarm R3): if
agreement trends toward 1.0 the loop is closing toward a lagging fame index; the number to
maximize is LED — disagreement now, agreement later. 8) every INSUFFICIENT carries a cause code
(thin data / resolution failure / endpoint error) — the spain case shows an instrument bug can
hide in the abstention column indefinitely.

---

## DISAGREEMENTS (signal, not noise)

1. **Which volatility stratum carries the real signal.** Challenger: refute the thin/cold-start
   rows (rikers, tillis, cyclosporiasis ×2, trump_fires, spain) as flags and prioritize
   high-volume MATURE oscillation (google, america, russia, japan, youtube, white_house, texas).
   Expansionist: same split, same priority. Executioner: the OPPOSITE priority — the low-input
   subclass is where the flapping-source hypothesis is genuinely live; high-volume names are
   expected to close "surge, real." Guardian: the thin rows raise a DIFFERENT question (is
   BREAKOUT on 8 mentions/2 platforms defensible at all — tillis). Outsider/Economist: run the
   co-movement test first; the stratum debate may be moot if one bad cycle explains the lows.
   All six agree on the mechanics: ONE batched read-only diagnostic, volume-stratified,
   co-movement first — the disagreement is about which outcome to expect, which the diagnostic
   itself settles.
2. **Are the item-20 entity misses real coverage gaps?** Outsider: yes — tom brady / oscar
   piastri / epic games are durable entities; a never-served trending entity is a race never
   entered, exactly what discovery collectors exist to prevent. Economist: refuted by outside
   data — Brady's pageviews were flat and Piastri's declining; the null won on those very items.
   (Both agree the MATCHER is broken and the number indefensible as printed; the Economist's
   referee-confirmed-miss condition operationally resolves the dispute: a miss counts only when
   independent data confirms attention actually arrived.)
3. **Whether spain belongs in the volatility flag set.** Challenger/Economist: refuted/exception
   — confirmed genuine surge; do not "fix" true attention volatility. Expansionist: verified as
   genuine high-volume jitter worth a look. Resolved by the same batched diagnostic.
4. **Item 21 closure stamp.** Guardian/Expansionist: stamp RULED (cite the standing stage-rule
   gate). Outsider/Executioner/Economist: plain OPERATIONAL closure/scorecard note. Cosmetic —
   same substance: close it, log it, change nothing.

## PER-ITEM VERDICT TABLE

| Item | Challenger | Guardian | Expansionist | Outsider | Executioner | Economist |
|---|---|---|---|---|---|---|
| 1–19 volatility (class) | AWC (6 topics refuted) | AWC (one consolidated finding) | AWC (thin rows refuted) | AWC (co-movement first) | SHIP (one batched diagnostic) | AWC (co-movement first; spain/japan exceptions) |
| 20 external recall | AWC / 2-10 figure REFUTED | AWC gauge / REJECT as target | AWC check / REFUTE claim | AWC (two-bucket; entity misses real) | SHIP-LATER (refuted as evidenced) | AWC (misses refuted by referee) |
| 21 spain fading | REFUTED (check stands) | Check APPROVED / instance REFUTED | REFUTE (shadow stays) | REFUTE instance / APPROVE check | CUT (close as validated) | REJECT item (commend check) |

**Consensus verdicts:** Items 1–19 — VERIFIED as a CLASS-level look, REFUTED as 19 individual
tickets; proceed only as one batched, volume-stratified, co-movement-first read-only diagnostic
(OPERATIONAL). Item 20 — the QUESTION verified, the 2/10 NUMBER refuted (6/6); rebuild the check
before any collector/lexicon action (OPERATIONAL). Item 21 — REFUTED 6/6 by fresh outside data;
close with a scorecard note; the check's conduct commended 6/6.

## NEW ITEMS SURFACED BY THE GATE (not in the original queue)

- **N1 [HIGH · OPERATIONAL] Blind Wikipedia referee** (Challenger, Outsider, Expansionist,
  Economist independently): title-resolution/fetch fails on common-noun keys ("spain", "japan",
  "canada", "fifa"...) and mislabels the failure "thin pageview history" — hollowed module C
  (A on 2/20), blocked item 21's diagnostic, and plausibly explains 0/8 LED referee
  corroboration. Fix resolve/fetch; truthful abstention cause codes; then RE-RUN referee
  corroboration on the 8 LED wins.
- **N2 [HIGH · OPERATIONAL] Ledger epoch reconciliation** (Challenger): byEpoch resolved sums to
  93 vs headline 87 (gap = the 6 same-day rows) — reconcile before any epoch figure is shown
  externally; consider printing tracked-race per epoch with the young-races/patience-window
  adverse-selection disclosure (Outsider).
- **N3 [MED · OPERATIONAL] Assessor check fixes, one patch + param bump v2.1** (Executioner ship
  order step 3): B surge exemption or distribution-derived threshold + persistence; std≈0 as its
  own WARN class (never "moving normally"); E full-feed scan + entity matching + class split +
  traffic floor + referee-confirmed misses; no letter grades below min graded-n; findings carry
  raw series; INSUFFICIENT cause codes; nulls + threshold provenance registered in the manifest.
- **N4 [MED · OPERATIONAL] Start the engine–referee correlation series** (Economist R3) from
  snapshot #1 forward — the drift alarm needs a baseline.
- **N5 [LOW · OPERATIONAL] Reroute fragment-shaped topics** ("shutting", "trump_fires") to the
  topic-quality worklist (Guardian).
- **N6 [LOW] External-communication notes** (Outsider): tracked-race always with n + interval;
  "0 false positives" disclosed as guaranteed-by-construction under the 365d window; one-page
  plain-English glossary for house dialect.

**Chairman — your decision per item.**
