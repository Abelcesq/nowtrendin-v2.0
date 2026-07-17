# BOARD REVIEW — the proposed "Scoring Assessor" agent (pre-run review)
**Date:** 2026-07-17 · **Material:** `07 17 2026 - nowtrendin_scoring_assessor.py`
(authored in a SEPARATE Claude chat session without access to this repo) · **Context:**
the payment portal is ON HOLD until data collection, sorting, and scoring are proven
accurate; this tool is meant to be the continuous monitoring/teaching instrument.
Six independent memos; the Executioner ran the file; the Challenger forensically
checked its claims against the live engine code.

## DECISION TABLE

| Item | Challenger | Guardian | Expansionist | Outsider | Executioner | Economist |
|---|---|---|---|---|---|---|
| A — concept (assessor/teacher) | AWC | AWC | AWC | AWC | **SHIP** | AWC |
| B — design as written | **REJECT** | **REJECT** | AWC | **REJECT as-is** | ship after F1–F5 | **REJECT** |
| C — wiring (adapter/cadence) | AWC | AWC (skill, not adapter) | AWC | AWC | **SHIP as skill** | AWC |

**Unanimous answer to the founder's question ("modify before running?"): YES — do not
run as-is.** Equally unanimous: the CONCEPT is right — the teaching layer (gap +
solution per failure), the machine work queue, and the trend-over-time framing fill a
genuine hole the 16-agent fleet does not cover ("/monitor = now; this = better than
last month"). Keep the teacher, fire half the curriculum (Outsider).

## WHY NOT AS-IS (the convergent findings)

1. **It would countermand a Chairman ruling.** Its prescribed fix for topic variants —
   "merge before scoring via normalize_topic()" — is exactly Option B/C the board
   unanimously REJECTED on 2026-07-15 (alias handling is DISPLAY-ONLY, Option A). A
   teaching agent emitting that into a Claude Code work queue steers future sessions
   into violating the ruling. (All six memos; Guardian: add a RULINGS REGISTRY so a
   solution contradicting a ruling fails the assessor itself.)
2. **Stale folklore hardcoded as "known truth" (Challenger, verified in code):** the
   45/67 collapse bands pre-date Mainstream v2; "frozen at 74"/gap-23 was FIXED
   (sink-harden); guardian/reddit absences are founder-DEFERRED decisions, not
   failures; the stage taxonomy does not match the engine; the collapse-band test is
   dead code. Running it today would emit false FAILs and mis-teach.
3. **The mainstream-referee check measures FAME, not MOTION.** Level-based pageviews
   (China/Apple always high) would fail the engine's CORRECT baseline-relative reads
   and teach score-INFLATION for mainstream topics — an integrity violation. Must
   reuse referee_wikipedia's surge logic (3x median vs own baseline).
4. **"Circularity by courier" (Guardian):** referee-derived solutions flowing through
   the JSON work queue into scoring edits = the held-out wall breached by hand. Every
   task needs held_out_derived stamps + classes (OPERATIONAL / SCORE_AFFECTING —
   founder + backtest + serve_payload regen / RULED); solutions must DIAGNOSE, never
   tune; and (Economist) track engine-referee correlation as a DRIFT ALARM — rising
   correlation means the loop is closing toward a lagging fame index, the opposite of
   the thesis.
5. **The readiness % is a Goodhart/vanity trap as built:** living denominator, comment-
   only threshold freezing, gameable by check-count (500 per-topic PASSes drown one
   HIGH silent-absence FAIL), INSUFFICIENT-exclusion rewards less history. Rename to
   operational_check_pass_pct, INTERNAL-ONLY (same rule as the catch-all %); severity-
   weighted + worst-module floor; hashed CHECK_MANIFEST + shadow-check onboarding +
   param_version bump on any change (the Friedman-Schwartz series protocol). **The
   accuracy ledger's tracked-race rate remains THE number — and the portal gate.**
6. **Lifecycle classifier fragile:** max-as-peak on 8 points — one viral spike poisons
   the peak (false ENDED on steady topics; bursty topics called dead in their trough);
   no absolute floor (2-to-5 views reads as RISING). Quantile-not-max, abs floor,
   RECURRENT class, WARN-only until it beats the STEADY-monkey null (Malkiel).
7. **Mechanics:** crashes on Windows cp1252 (needs UTF-8); writes real-looking
   assessor_work_queue.json from FAKE demo data with no synthetic watermark (demo must
   stamp DEMO + require --demo); output path must be audits/assessor/.

## THE APPROVED SHAPE (what to build instead — convergent)
- **A /scoring-assessor SKILL** reading the EXISTING deployed surfaces (/monitor,
  /health/collectors, /accuracy/ledger + epoch stamp, /aliases, referee_wikipedia
  free Wikimedia pageviews) — NOT the 10-method raw-SQL adapter (a second read path;
  the 07-06 pool-outage class). 6/10 adapter methods already map to endpoints; per-
  source coverage baselines do not exist — CUT from v1.
- Positioned as the AGGREGATOR/TEACHER OVER the fleet — annotates and grades existing
  agents' output, never a contradicting 10th checker.
- Fixed stratified cohort (~250-350: ledger-enrolled + top Breakout/Strong + rotating
  maturity samples), cohort_spec persisted per snapshot.
- Snapshots: append-only + git-committed audits/assessor/*.json (tamper-evident trend
  line); monthly official point + weekly internal work-queue run; never on deploy.
- feed parameter now (trend/market/crypto — market+crypto referee = their own
  price-validated ledgers).
- Free sources only (Apify clock-slot rule untouched).

## CHAIRMAN DECISION REQUESTED
Adopt the board's modification list and have the assessor REBUILT to the approved
shape (est. ~half a day for v1 as a skill), or amend the list first. The original
file is preserved as the concept source; credit to it for the four-question frame
and the teaching layer — both survive intact.

## ARCHETYPE MEMOS (verbatim)

---

# BOARD MEMO — The Challenger (adversarial accuracy skeptic)
## Re: `07 17 2026 - nowtrendin_scoring_assessor.py` as a measuring instrument
### 2026-07-17 · Evidence verified against the live v2 codebase, not the file's own claims

My brief: attack the assessor's ACCURACY. An instrument that mis-measures is worse than no
instrument — and this one is explicitly designed to TEACH Claude Code what to fix, so every
measurement error becomes a prescribed wrong action. I verified each "known" signature
against the repo. Findings below, then verdicts.

---

## 1. The hardcoded "known" signatures are STALE SESSION LORE, not current v2 facts

**COLLAPSE_DET_BAND (40,50) / COLLAPSE_CONF_BAND (60,72), "the known ~45/67 collapse
signature":** I traced this to `_audit_work/report_sections.md` — the **2026-06-22/23 audit**
(file dates confirm: audit_full.json Jun 22 23:02). That audit's own quick-win list shows what
happened NEXT: since then the system shipped **Mainstream v2** (2026-06-26, ≥5-independent-outlet
corroboration, FIFA-validated), the INV-1 serve-consistency fix, and multiple calibration
epochs. Nothing in `transfer/` carries these bands — `grep collapse|45/67` hits only the old
audit artifacts. There is **no verification anywhere that the 45/67 signature still exists in
the July engine.** Freezing a 3.5-week-old, pre-Mainstream-v2 symptom as a "known signature"
with `PARAM_VERSION="assessor-v1"` and the charter line "never tune a threshold to pass" is
integrity theater: the threshold was never validated in the first place, so refusing to tune
it preserves an error, not a standard.

Worse — **the collapse-band test is dead code**. The failure condition is
`det < 70 or conf < 70 or collapsed`; since the band's det ceiling is 50 < 70, `collapsed`
can never be the deciding term. Every band row already fails on `det < 70`. The band exists
only to append the string "the known ~45/67 collapse signature" to the finding — i.e., its
sole function is to inject stale lore into the teaching text.

**"mcp frozen at 74" + "stored_gap -23.0":** the demo's mcp row reproduces the June-22
heisenberg_gap arithmetic bug — which was **FIXED**: `gravitational_anomaly_detector.py:3545`
("SINK-HARDEN the heisenberg_gap invariant") and :4972 ("FINAL stored-gap recompute") enforce
persisted gap == stored det − conf at the write sink. The gap_arithmetic check is fine as a
regression tripwire; teaching it as a LIVE failure mode mis-dates the system by a month.

**"guardian silently absent" / GUARDIAN_API_KEY gap:** CLAUDE.md 2026-06-24: "Guardian +
Reddit keys deliberately deferred (proceeding without)" — a founder DECISION, not a failure.
And the live fleet already encodes this: `monitoring_agents.py` `_OFF_SOURCES = {"reddit"}`
("intentionally off — never alert"); `collector_health.py` marks reddit non-critical with a
sentinel window. The assessor has **no concept of an intentionally-off source**, so wired
naively it FAILs forever on decisions the founder already made — alarm fatigue plus a work
queue instructing Claude Code to "verify the API key" for a source that was deliberately not
keyed.

**Stage taxonomy is wrong:** `ENGINE_ACTIVE = {BREAKOUT, STRONG, EMERGING, INDICATING}` and
the RISING check looks for `MARGINAL`. The engine's actual stage set is
`BREAKOUT | STRONG | EMERGING | WATCHING | MONITORING`
(`gravitational_anomaly_detector.py:1152`). INDICATING and MARGINAL are UI chip/band labels,
not `signal_stage` values — those comparisons silently never fire. The author didn't know the
live taxonomy; module D is comparing against labels that don't exist.

**Freshness threshold contradicts the fleet's own hard rule:** `STALE_SOURCE_HOURS = 24`
flat, per source. `collector_health.py` spent a documented lesson learning that flat windows
cause STALE flapping — its windows are per-collector (420m = 6h cadence + 1h margin; 8h for
6-hourly discovery), and CLAUDE.md §13 makes `max_gap_minutes > COLLECT_INTERVAL_MIN + 60`
a validated startup rule. Two instruments with different definitions of "stale" over the same
sources = guaranteed contradictory reports.

**Volume check breaks on live wiring:** `counts[-1]` vs the 7d mean assumes complete days.
A live adapter reading TODAY's partial count at mid-day flags ~every source at ~50% volume
every morning. The real system avoids this class entirely (gap-since-last-success, not
partial-day counts).

**Conclusion §1:** Of the five "known" signatures the file teaches (45/67 collapse, frozen-74
caps, gap arithmetic, guardian absence, hormuz variants), **at least three are fixed, decided,
or unverified-stale**; the taxonomy and thresholds diverge from the live fleet's hard-won
values. As a measuring instrument its reference marks are mis-calibrated before first use.

---

## 2. The grading math is gameable and "Phase-1 readiness %" is a vanity metric

`score = (n − fails − 0.5·warns) / n` per module; `readiness = PASS share of ALL pooled
gradeable findings`. Attacks:

- **Check-count gaming (confirmed by construction).** Module A emits up to 2 PASS rows per
  healthy source (freshness + coverage); module B emits 1 row per topic; module D 1 per topic.
  Feed the adapter 500 topics with ≥6 cycles of history and module B contributes ~500 PASS
  rows; one HIGH silent-absence failure (an entire channel missing from every score) moves
  readiness by ~0.2%. The number is weighted by how many things you LOOKED at, not by what
  matters. Same grade math: 1 FAIL in 2 checks = C; the identical defect among 50 checks = A.
- **Severity is ignored in the math.** A `high` FAIL and a `low` WARN differ 2× in the
  formula; the severity field decorates the work queue but never the grade. A module can be
  graded "A" while carrying the exact failure the founder holds the payment portal for.
- **Asymmetric PASS emission biases the numerator.** Freshness and coverage emit PASS rows;
  volume emits only WARNs; gap_arithmetic emits one row per RUN but no_gap emits one per
  TOPIC. The PASS/FAIL mass per check class is arbitrary, so the pooled ratio measures the
  emission design, not the system.
- **The INSUFFICIENT exclusion inverts incentives.** Topics with <6 cycles drop out of the
  denominator — a system that retains LESS history grades BETTER. On a platform whose §13
  retention rule exists precisely because history is the moat, that is exactly backwards.
- **Shifting denominator.** Readiness moves when: topics enter/leave the working set, a source
  is added, a check is added to the code, history crosses the 6-cycle floor, or the referee
  resolves more topics. None of these is a change in system quality. This is the same defect
  class as the catch-all % that CLAUDE.md explicitly demotes: "never publish the catch-all %
  externally as an accuracy KPI (warmth/denominator/cycle-phase sensitive)." A "Phase-1
  readiness %" gating the PAYMENT PORTAL is a strictly higher-stakes number with the same
  disease — and unlike the accuracy ledger it carries no version-stamped denominator
  definition (contrast `LEDGER_PARAM_VERSION`, which was rebuilt on 2026-07-08 specifically
  so "a published rate can never silently span an env edit").

**Verdict on the number:** the accuracy ledger (LED / tracked-race, honest denominators,
version-stamped) IS the readiness instrument. A pooled PASS-share cannot sit beside it.
At most: per-module counts with a FIXED, versioned check registry, severity-weighted,
published as a work-queue length — never as a percent named "readiness."

---

## 3. MAINSTREAM_REFEREE_LVL 4.0 is a category error: it measures FAME, the engine measures MOTION

log10 median daily pageviews ≥ 4.0 (=10k/day) classifies a topic "mainstream," then demands
`det ≥ 70 AND conf ≥ 70` or FAIL. But median pageview LEVEL is a **static fame** measure:
the China / Apple / India Wikipedia pages sit above 10k/day **permanently**, trending or not.
The Gradient Score is **baseline-relative by design** (fame vs diffusion — the calibration
model's core distinction): a famous-but-quiet topic SHOULD read low Detection. This check
therefore hard-FAILs the engine for correctly refusing to confuse fame with movement, and its
prescribed "solution" — "extend the dual-pathway anti-collapse preservation across the
mid-mainstream band" — teaches Claude Code to INFLATE mainstream scores until famous topics
read high forever. That is a score-corrupting instruction generated by a mis-specified
referee.

The repo already contains the correct referee design and the assessor ignored it:
`referee_wikipedia.py` uses **surge** detection (3× a clean MEDIAN baseline, 200-view
absolute floor, ±30d same-surge window, frozen `wiki-v2-2026-06-23` params) precisely
because level ≠ arrival. The right mainstream test is "referee says this topic SURGED
recently and the engine still reads early/uncertain" — a motion-vs-motion comparison.
`det<70 or conf<70` as a binary failure line is additionally unjustified: 70 is the STRONG
stage boundary, chosen here without any backtest linking referee-surge topics to a 70-floor.

Also: per-topic no_gap FAILs are emitted and graded even when the cohort summary abstains
(`checked < 5`) — the abstention discipline advertised in the header applies to the summary
row only, while the grade still ingests the unabstained per-topic rows.

---

## 4. The lifecycle classifier is not noise-robust

- **Peak poisoning:** `peak = max(vals)` over the whole series. One viral day on an otherwise
  steady series makes `recent < 0.25·peak` → **ENDED** for a topic that never stopped. A
  steady 60/day series with a single 300 spike is classified ENDED. This is the single most
  common shape in attention data.
- **No absolute floor:** 2→5 views/day = "RISING" (2.5× prior). referee_wikipedia solved this
  with `SURGE_MIN_ABS = 200`; the assessor rolls its own weaker classifier in the same repo.
- **No smoothing/median:** 3-point and 5-point MEANS on daily data; one bot-spike day flips
  the phase. The referee uses medians for exactly this reason.
- **"Sustained" is claimed, not implemented:** the ENDED docstring says "sustained"; the code
  checks a single 3-day mean.
- **Boundary incoherence:** PEAKING requires `recent ≥ 0.9·peak AND recent > prior`; RISING
  requires `recent > 1.25·prior`. A series at 0.95·peak and 1.3×prior is PEAKING; at
  0.85·peak and 3×prior it's RISING — phase labels flap across adjacent days near a peak.
- Combined with the wrong stage taxonomy (§1), module D compares a noisy phase label against
  a partly-nonexistent stage vocabulary. Its FAIL/WARN output is not evidence.

---

## 5. The demo FABRICATES failure modes and writes them where Claude Code is told to eat

`_Demo` hardcodes: guardian silently absent (founder-deferred, not a failure), mcp frozen at
74 with caps at 99.5/99.8 (June lore), the 45/67 cohort (stale), mcp stored_gap −23.0 (bug
fixed at the sink), hormuz variant split. Running the file bare — the documented default —
writes **`assessor_work_queue.json` at the CWD with no `synthetic` flag**, containing tasks
like "verify the API key/env var" (for a deliberately unkeyed source), "raise/soften the
saturating component caps" (a SCORING change prescribed with no backtest gate), and "add the
alias-consolidation layer to normalize_topic() so variants merge before scoring" — which
**directly contradicts the Chairman's 2026-07-15 ruling** (alias consolidation is
DISPLAY-ONLY; score-time merge was REJECTED unanimously). The file's stated purpose is that
Claude Code ingests this JSON as a work queue. A naive wiring session — or any future session
that simply finds the JSON in the repo root — inherits a fabricated, partly-rescinded,
partly-founder-overruled task list as ground truth. This is the exact mechanism by which
stale lore from one chat session becomes executed code in another.

Two aggravators: (a) solution strings are PRESCRIPTIVE scoring edits from a read-only
"teacher" — the fleet's own charter (`nowtrendin_agent.py`: "No score/weight/tier/verdict
changes") and the flag-never-force rule say measurement proposes, humans dispose; nothing in
the JSON marks tasks as requiring founder sign-off. (b) The header's fleet framing is
half-right (calibration_agent / lead_moat_agent / nowtrendin_agent DO exist in `transfer/`),
which makes the file look better-informed than it is — the parts that matter (thresholds,
taxonomy, fixed-vs-live status) are where it's wrong.

---

## VERDICTS

### (A) CONCEPT — APPROVE-WITH-CONDITIONS
The genuinely novel part is the **teaching layer** (gap + solution per finding) and the
**machine work queue** — the 9-agent fleet reports status, not curricula. That gap is real.
But modules A and B are re-implementations of `source_watchdog`/`collector_health` and
`trend_signal_diagnostic` with DIVERGENT thresholds — two instruments disagreeing about
"stale" and "frozen" is worse than one. Condition: the assessor must **compose over the
existing fleet's outputs** (annotate /monitor + /health/collectors + trend_signal_diagnostic
+ referee_wikipedia + ledger findings with gap/solution text), never re-measure with its own
constants.

**Strongest attack:** it duplicates the fleet with worse calibration, so every disagreement
between the assessor and /monitor becomes a founder-time-burning dispute about which
instrument is lying.

### (B) DESIGN/INTEGRITY — REJECT as written
**Strongest attack:** the mainstream referee measures fame while the engine measures motion
(§3), so its highest-severity check systematically FAILs correct behavior and its prescribed
fix inflates scores — a measurement error that self-converts into score corruption via the
teaching channel. Add the stale frozen "signatures" (§1), the gameable grade / vanity
readiness % (§2), the noise-fragile lifecycle classifier (§4), and a solution string that
countermands a unanimous Board ruling (§5).

Required modifications before any live run:
1. Delete COLLAPSE_DET_BAND / COLLAPSE_CONF_BAND and every "known ~45/67" / "frozen at 74" /
   GUARDIAN string. Re-derive any collapse check from a LIVE distribution read, dated, or
   drop it. (The band is dead code anyway.)
2. Replace `referee_mainstream_levels` (log10 level) with the surge-based referee: reuse
   `referee_wikipedia.py` observations (held-out table, frozen wiki-v2 params). The no_gap
   test becomes "referee-confirmed RECENT surge + engine still early," with the 70/70 line
   replaced by a backtested threshold or a distributional (percentile) test.
3. Grading: fixed versioned check registry; severity-weighted per-module scores; delete
   `phase1_readiness_pct` (or demote to an internal work-queue-length gauge, never published,
   never portal-gating — the accuracy ledger is the readiness instrument).
4. Adopt the fleet's stale semantics: per-collector windows from `COLLECTOR_EXPECTATIONS`,
   honor `_OFF_SOURCES`/non-critical flags, gap-since-success not partial-day counts.
5. Fix stage taxonomy to `BREAKOUT|STRONG|EMERGING|WATCHING|MONITORING`.
6. Lifecycle: median smoothing, absolute floor (≥ SURGE_MIN_ABS analog), spike-robust peak
   (e.g., 95th percentile or exclude the recent window from peak), implement "sustained."
7. Rewrite the variants solution to DISPLAY-ONLY alias grouping per the 2026-07-15 ruling;
   rewrite all solution strings as DIAGNOSTIC pointers ("check X; propose via research
   gate"), never prescriptive parameter edits; stamp every task `requires_founder_signoff`.
8. Demo: stamp `"synthetic": true` in the JSON, write to a demo-named file in scratch, and
   purge fabricated live-lore (use obviously fake topic names).

### (C) WIRING — APPROVE-WITH-CONDITIONS
Run as a **skill / scheduled read-only report** (daily EOD, alongside the catch-all EOD), NOT
an engine endpoint — the per-topic referee fan-out would H12 exactly like /monitor/catchall
did, and per-topic HTTP must be batch-paced. The 10-method AssessorAdapter should be thin
reads of EXISTING surfaces: `/health/collectors`, `/monitor` outputs, `velocity_scores`
history, the referee's held-out table, `/accuracy/ledger`. **Hard integrity conditions:**
referee series come ONLY from free Wikipedia pageviews or already-slot-scheduled data —
never new Apify/Google-Trends pulls (clock-slot rule); read-only to all engine tables;
work-queue JSON lands in `audits/`, flagged synthetic-or-live, and is consumed only under
founder review (flag-never-force). **Strongest attack:** wired as-is against live config it
would page forever on reddit/guardian and mid-day volume, training everyone to ignore it —
the fate of every mis-calibrated alarm.

**Bottom line:** keep the teaching-layer concept; throw away the instrument's reference
marks, its headline number, and its demo; rebuild it as an annotation layer over the fleet
that already measures correctly.

— The Challenger


---

# BOARD MEMO — First-Principles Guardian
**Subject:** `07 17 2026 - nowtrendin_scoring_assessor.py` (the "Assessor/Teacher" agent)
**Date:** 2026-07-17 · **Basis:** CLAUDE.md §13–§17 · AGENT_CHARTER.md Part 0 (Shared Mandate 0.2.1–0.2.6) · BOARD_entity-grouping_2026-07-15 (Chairman ruling) · the file itself (read in full)

---

## Framing

The first principle at stake in every one of the four questions is the same one: **the
system's validators must remain independent of what they validate, and the authority to
change a score must never be delegated to a machine-readable queue.** The assessor is a
genuinely novel and valuable artifact — the existing fleet FLAGS, this one TEACHES (gap +
solution + denominator). But teaching is prescription, and prescription is where held-out
walls, Chairman rulings, and flag-never-force are breached — not in the checks, in the
`solution:` strings. The checks are mostly fine. The solutions are the danger surface.

---

## (1) HELD-OUT WALLS — the laundering path is real

**Finding: YES, there is a laundering path, and it is the file's designed-in output channel.**

Trace it: `referee_mainstream_levels()` / `referee_series()` (held-out Wikipedia referee,
per `referee_wikipedia.py` — "never imports into scoring") → module C/D findings → each
FAIL carries a `solution:` that names a **scoring-code change** ("extend the dual-pathway
anti-collapse preservation across the mid-mainstream band"; "verify mainstream_ratio w
isn't collapsing **for these rows**"; "drive stage decay from the Confidence-Decay path")
→ `to_claude_code_json()` writes `assessor_work_queue.json` explicitly "for Claude Code /
the dev" → a future session ingests the queue and edits scoring. The referee never
*imports* into scoring — it *dictates* to it through a JSON file. That is circularity by
courier. The no-circularity rule (Charter 0.2.3, feedback-no-circular-metrics) is about
information flow, not Python imports: **if referee readings select which rows/bands get
changed scoring treatment, the referee has tuned the score, and it is thereafter
worthless as that change's validator** — it confirmed a change it caused.

Two distinct failure grades, and the wall text must distinguish them:

- **Per-topic/per-row tuning (absolute prohibition).** "china reads 45/67 vs referee 5.1
  → fix china's rows" is fitting the score to the referee, topic by topic. Never
  permissible in any form.
- **Class-level hypothesis (permissible only via the human gate).** "The mid-mainstream
  band under-reads" is a legitimate hypothesis the referee may *motivate* — exactly as
  the ledger's feature-mining motivated the GHOST_FEEDS case. The lawful path is:
  finding → founder review → held-out backtest → validation on an instrument OTHER than
  the one that motivated it (or a strictly out-of-sample period of the same referee).

**Required wall text** (in the module docstring AND stamped into every C/D task in the
machine JSON — the JSON is what future sessions actually read):

> HELD-OUT WALL: Modules C and D consume the held-out Wikipedia referee. Their findings
> are MEASUREMENTS; their `solution` fields are HYPOTHESES, never authorizations. No
> scoring, calibration, admission, or ledger code may be changed on the basis of this
> work queue without (a) founder sign-off and (b) a held-out backtest. No per-topic or
> per-row scoring parameter may EVER be changed to close a gap this referee reported.
> Any scoring change motivated by a C/D finding must be validated out-of-sample or on an
> independent instrument — the motivating referee window is spent. This module must
> never be imported by engine/scoring code; it runs read-only, off the serve path.

And in `to_claude_code_json`, every task must carry
`"held_out_derived": true|false` so the laundering path is visible in the artifact itself.

---

## (2) THE C-MODULE VARIANTS "SOLUTION" — prescribes a fix the Chairman rejected

**Finding: line 244–245 ("add the alias-consolidation layer to normalize_topic() so
variants merge before scoring") is Option B/C — extraction-time canonicalization /
pre-score merge. The Board's 2026-07-15 decision table: C REJECTED unanimously (Chairman:
adopted); B DEFERRED, no work authorized. Option A (display-only alias layer,
ENTITY_GROUPING, 7 conditions) is the ONLY ruled path.**

The principle at stake is **governance integrity of the teaching layer itself.** This
agent's entire value proposition is that its output steers future dev/Claude Code
sessions. A teacher that emits a Chairman-rejected fix as a machine-readable task will —
with high probability, because the queue is *designed* to be acted on with less context
than the Board had — cause a future session to violate the ruling in good faith. That is
worse than a one-off mistake: it institutionalizes the violation. My own memo in that
review rejected B essentially permanently (ingestion-time identity assertion =
fabrication by routing); the assessor would re-open it by side door.

There is also a substantive error beneath the governance one: the check presumes variant
divergence is a *bug*. The Board's fragment-lead study (authorized read-only work) exists
precisely because fragments sometimes LEAD the canonical key ("mcgregor" det 94.6 vs
canonical 93.9 live) — divergence can be signal. Auto-grading it FAIL/medium with "merge
before scoring" as the fix pre-judges the open empirical question.

**Required changes:**
1. Rewrite the solution verbatim to the ruled path:
   > "Variant divergence is a MEASUREMENT, not a merge mandate. Per BOARD_entity-grouping
   > _2026-07-15: score-time merge REJECTED (unanimous); extraction-time canonicalization
   > DEFERRED (no work authorized). Route through the DISPLAY-ONLY alias layer
   > (ENTITY_GROUPING, Option A, 7 convergent conditions) and log the pair into the
   > fragment-family prevalence audit + fragment-lead study."
2. Downgrade the check's status from FAIL to WARN/INFO — divergence across surface forms
   is an observation feeding the authorized read-only studies, not a defect.
3. **Structural fix (the general lesson):** the assessor must carry a RULINGS registry —
   a small dict mapping check names to governing board rulings/CLAUDE.md sections — and
   every `solution` string must cite its authority or be marked `"authorization":
   "founder"`. A prescribed solution that contradicts a registered ruling is itself an
   assessor FAIL (the agent grades itself). Without this, every future ruling can be
   silently steered around by a stale teacher.

---

## (3) FLAG-NEVER-FORCE — the work queue MUST carry an authorization class

**Finding: YES — required, not optional.** "Raise/soften the saturating component caps or
re-scale so headroom exists" (B-module freeze check), "extend the dual-pathway
anti-collapse preservation" (C), "drive stage decay from freshness/decline" (D) are
score-affecting prescriptions. Charter 0.2.5 (flag, never force) + 0.2.6
(backtest-before-ship) make these *recommendations for human confirmation* by definition.
But the current JSON schema is flat — a `solution` string and a `severity`. A downstream
Claude Code session ingesting `assessor_work_queue.json` has no field telling it that
task 3 ("check the API key") is directly actionable while task 1 ("soften the caps")
requires the founder and a backtest. Severity is not authorization; "high" severity
*invites* immediate action — precisely backwards for score-affecting items.

**Required design change — a three-class taxonomy on every task:**

| class | meaning | examples in this file | downstream permission |
|---|---|---|---|
| `OPERATIONAL` | ops/config/collector; no score surface | missing env key, stale collector, quota check | dev/Claude Code may act, verify-before-ship |
| `SCORE_AFFECTING` | changes any score, weight, cap, stage, admission | cap softening, anti-collapse extension, stage decay | **founder sign-off + held-out backtest + serve_payload regeneration** (the serve-payload gotcha) — Claude Code must refuse to auto-implement |
| `RULED` | touches a standing board ruling | variants/alias anything | cite the ruling; only the ruled option is prescribable |

Additionally, the score-affecting solutions as written **pre-judge the diagnosis**. A
Detection frozen 6 cycles has at least three known causes in THIS system before "caps too
tight": stale `serve_payload` (the documented cache gotcha), the *intentional* INV-1
stale-serve rule (rows >48h serve stored verbatim — frozen-by-design, and the assessor
would grade the integrity fix as a defect), and a wedged prewarm. Prescriptions must be
**diagnostic-first** ("confirm the row is recomputing and not serving stored payload per
INV-1; only then hypothesize cap saturation — founder class"). Same for the hardcoded
`COLLAPSE_DET_BAND (40,50)` / `(60,72)` and "frozen at 74": the evidence pack flags these
as possibly 1.0-era. Freezing a threshold *to a remembered bug signature* is the same sin
as tuning a threshold to pass — the bands must be re-derived from the live distribution
(the trend-signal-diagnostic distribution check exists for this) or shipped as
`WARN`-only until verified.

---

## (4) MOAT vs A SECOND "ACCURACY" NUMBER

**Finding: as written, it manufactures a competing accuracy number. Fixable by
subordination, and worth fixing — the teaching layer genuinely strengthens the moat once
subordinated.**

The moat is the **accuracy ledger**: denominator-backed, price/attention-validated,
365-day patience, tracked-race vs blended honesty, epoch-stamped. It is the ONE
instrument allowed to answer "are the scores right." The assessor's
`phase1_readiness_pct` is a share-of-passing-checks figure whose denominator is *the
check list the author happened to write*. That has three first-principles defects:

1. **The denominator is the tuning surface.** The file promises "never tunes a threshold
   to pass," but adding ten easy checks raises readiness without touching a threshold.
   A checklist pass-rate is not a measurement of anything external.
2. **It is warmth/config-sensitive** — exactly the failure class the standing rule already
   demoted the catch-all % for ("never publish as an accuracy KPI; it is a congestion
   gauge"). Readiness % inherits the same rule on arrival.
3. **The founder's stated use is gating the payment portal on "proven accurate."** If the
   gate number is the assessor's own readiness %, the system grades its own homework with
   a self-authored rubric while the actual external-truth instrument (the ledger) sits
   one field over. Module C's "no-gap test" is a useful *consistency probe*; it is not an
   accuracy verdict, and module D's lifecycle check partially re-implements the ledger
   sweep's job with a cruder ruler.

**Required changes:**
- Rename `phase1_readiness_pct` → `operational_check_pass_pct`, with a printed caveat:
  "share of self-defined checks passing — NOT an accuracy measurement; the accuracy
  instrument is the ledger." Internal-only; never published externally (same rule as the
  catch-all %).
- The report's ACCURACY headline must be **pulled from `/accuracy/ledger`**
  (tracked-race + blended, with denominators) and displayed ABOVE the module grades.
  Module C findings hang beneath it as consistency probes. One accuracy instrument,
  one number, everywhere.
- Module D must consume the FREE Wikipedia referee series (or already-slot-scheduled
  data) — never new Google Trends pulls (Apify CLOCK-SLOT rule, hard). It should report
  disagreements into the ledger's context, not issue its own lifecycle verdicts as a
  parallel truth.
- Letter grades per module are fine as *teaching* devices; the combined single percent is
  the dangerous artifact. If kept at all, it must never appear in any founder-facing
  "ready to charge money" sentence — the ledger's tracked-race rate + the operational
  fleet's green is that sentence.

---

## VERDICTS (per the evidence pack's A/B/C)

**(A) CONCEPT — APPROVE-WITH-CONDITIONS.** The teaching grammar (gap + solution +
denominator + abstention) and the machine work queue are a real, novel layer the fleet
lacks — the 9 agents flag, none teach. "A failing grade is a successful run" is
Charter-0.2 in spirit. Conditions: it is a TEACHER, not a second accuracy instrument
(see 4), and its checks must wire to the existing instruments rather than re-implement
them (see C).

**(B) DESIGN/INTEGRITY — REJECT AS-WRITTEN; approvable only after ALL of:**
1. Held-out wall text + `held_out_derived` stamps (§1) — laundering path closed in the
   artifact itself.
2. Variants solution rewritten to Option A verbatim + check downgraded + RULINGS
   registry (§2) — no machine-readable Chairman violations.
3. Task authorization classes OPERATIONAL / SCORE_AFFECTING / RULED; Claude Code refuses
   to auto-implement SCORE_AFFECTING (§3).
4. Diagnostic-first prescriptions for freeze/collapse; INV-1 stale-serve and
   serve_payload cache listed as first-check causes so the assessor doesn't grade an
   integrity rule as a bug (§3).
5. COLLAPSE bands + "frozen at 74" re-derived from live data or demoted to WARN
   (stale-claim risk flagged in the pack).
6. Readiness % renamed/demoted; ledger promoted to the report's accuracy headline (§4).
7. Referee series = free Wikipedia only; no new paid pulls (Apify clock-slot rule).

**(C) WIRING — APPROVE the endpoint-reading form; REJECT the 10-method fresh-DB
adapter.** First principles: one instrument per truth. `source_health` /
`expected_sources` already exist as `/health/collectors` + collector_health;
score/component state as `/monitor` run_all + the diagnostic agents; accuracy as
`/accuracy/ledger`; referee as `referee_wikipedia` outputs. A parallel adapter
re-implementing these reads creates drift between what the assessor grades and what the
fleet monitors — two dashboards disagreeing is a credibility event. Run it as a
**standalone read-only skill/off-engine script** (never imported by the engine, never in
the web process — the serve path is sacred per §13 batch-pacing), consuming the deployed
endpoints; cadence **weekly, folded into /improve-system** (it IS the missing
machine-readable half of that audit) plus on-demand post-deploy; reports to
`audits/assessor/`; JSON queue written beside the report, carrying the class +
held-out stamps above. The synthetic `_Demo` stays — it is an honest fixture — but must
be clearly marked non-live so its 1.0-era signatures are never mistaken for current truth.

**Bottom line.** The founder asked for a proof-and-teaching instrument. This file is 70%
of one. The 30% that must change is exactly the part that touches power: what the
solutions are allowed to *prescribe*, who is allowed to *act* on them, and which number
is allowed to call itself *accuracy*. Fix those three and the teacher strengthens the
moat; run it as-is and it quietly becomes an unaccountable second scorer with a pen.

— First-Principles Guardian


---

# BOARD MEMO — The Expansionist (Scale) · Scoring Assessor review · 2026-07-17

Subject: `07 17 2026 - nowtrendin_scoring_assessor.py` (~470 lines, external authoring session)
Lens: does this scale, and does it build the enterprise story buyers will diligence?

---

## Executive position

The single number this file produces — `phase1_readiness_pct`, trending upward month over
month, per product surface — is the closest thing to a diligence artifact this company has
outside the accuracy ledger. Buyers do not read 9 agent payloads; they read one line going
up and ask "prove it." So my whole review is about making that line PROVABLE at scale:
stable denominators, one read path, bounded working sets, and a frame that extends to
market and crypto without a rewrite. The file's concept is right. Its wiring, as written,
would produce a jumpy, unprovable line and a second data-access layer we then maintain
forever. Fixable, and worth fixing.

---

## Q1 — Snapshot storage/versioning: how does the trend line become provable?

**Answer: BOTH a DB table (canonical) and git-committed JSONs in `audits/assessor/`
(tamper-evident export). Neither alone is sufficient.**

- **DB table `assessor_snapshots`** — append-only, forward-only, same discipline as the
  three ledgers: `(run_at, feed, param_version, readiness_pct, module_grades JSON,
  gradeable_n, pass_n, fail_n, warn_n, insufficient_n, cohort_spec JSON, findings JSON)`.
  This is what a future `/assessor/history` endpoint and any dashboard trend line reads.
  Retention: full 365 days minimum, same as everything else (§13).
- **`audits/assessor/YYYY-MM-DD_<feed>.json` committed to git** — the provability layer.
  A git history of monthly JSONs, each stamped with `param_version` and the check
  inventory, is externally verifiable in a way a DB row is not: commit hashes are
  tamper-evident, diffable, and showable in a data room without granting DB access. This
  repo already has the exact pattern (`audits/improve-system/`, `audits/ledger-research/`,
  `audits/board/`).

**Provability conditions (these are the hard part, not the storage):**
1. **Readiness is only comparable within a `param_version`.** Add a check to a module, or
   change a threshold, and the % moves for reasons that have nothing to do with the system.
   Rule: any change to thresholds OR the check inventory bumps `param_version`
   (`assessor-v1` → `-v2`), and the trend chart annotates the discontinuity. Never splice
   two versions into one unlabeled line. This is the same discipline as
   `calib-params-v2-patience365`.
2. **Every snapshot records its denominator AND its cohort.** `gradeable_n` plus the
   actual sampled topic/source ids (`cohort_spec`). A % without its N and its cohort is
   exactly the mistake the catch-all metric taught us (warmth/denominator-sensitive
   numbers must never be published as KPIs). Readiness must not repeat that: it is
   publishable ONLY because each point carries a frozen, reproducible cohort.
3. **Module-weighted, not finding-weighted.** As written, readiness = share of ALL
   gradeable findings passing — so whichever module emits the most per-item findings
   (B and D, per-topic) dominates the number, and growing the working set from 300 to
   3,000 topics swings the % with zero change in system quality. Fix: readiness =
   mean of the four module scores (25% each). The letter grades already compute
   per-module; reuse that. This one change is the difference between a diligence
   artifact and a vanity metric.
4. **INSUFFICIENT must be reported next to the %.** An agent that abstains its way to
   90% readiness on 12 gradeable checks is not the same as 90% on 400. The abstention
   count is part of the honest denominator story — print it on the same line.

## Q2 — Overlap discipline: adapter over endpoints, or raw SQL?

**Answer: endpoints-first, emphatically. The 10-method raw-SQL adapter is my biggest
scale objection to the file as written.**

The evidence pack is right that modules A and (parts of) C/D re-derive what
`/health/collectors`, `/monitor` (`run_all` — source_watchdog, scorer_watchdog,
pipeline_integrity, cost_sentinel, calibration_auditor, etc., `monitoring_agents.py:1534`),
and `/accuracy/ledger` already serve. A raw-SQL adapter is:
- **A second read path to maintain.** Every schema change now breaks two consumers; every
  future fix to source-health semantics has to be made twice or the assessor silently
  drifts from what /monitor says — and then the diligence artifact CONTRADICTS the
  monitoring fleet, which is worse than not having it.
- **A DB-load hazard we already paid for.** The 2026-07-06 outage chain (pool saturation →
  wedged prewarm → cold-build churn) is the direct cost of new heavy readers hitting
  Postgres. `run_all` deliberately excludes the heavy scanners to stay under 30s; a new
  agent doing per-topic history queries over 3k topics via raw SQL walks straight back
  into that failure class. `PG_POOL_MAX=8` headroom is a deliberate margin — do not spend
  it on a duplicate of data we already serve over HTTP.

**Prescription:** the adapter's methods become HTTP reads of the existing surfaces:
`source_health`/`expected_sources` ← `/health/collectors` + collector_health expectations;
accuracy/ledger context ← `/accuracy/ledger`; liveness ← `/monitor` run_all; category
warmth ← `/monitor/catmaps`. For the two things genuinely NOT served today — per-topic
score histories (B) and component states — do not write assessor-side SQL: add ONE thin,
batch-paced, superset-cached engine endpoint (e.g. `/assessor/inputs?feed=trend`,
prewarm-pattern, single-flight) that serves the sampled cohort's histories. One truth,
one owner, and the assessor stays a pure consumer that could even run OFF-dyno (skill,
scheduled task) without DB credentials — which is also the better security story for an
agent whose output goes in a data room.

## Q3 — Working-set bounds over 3k+ topics: sampling policy

**Answer: stratified fixed-size cohort, persisted per snapshot, ~250–350 topics max.**

Per-topic checks (B freeze/volatility, D lifecycle) over the full 6,000-topic working set
would (a) drown the report, (b) hammer the read path, (c) make readiness hostage to
working-set churn. Policy:

1. **Always-in stratum (the ones that matter for the story):** every ledger-enrolled
   pending/resolved topic in its patience window, plus all current BREAKOUT/STRONG
   stage topics (capped ~top-50 by Detection). These are the topics a buyer will
   spot-check; they must never be sampled out.
2. **Stratified random stratum:** ~30 per maturity class (NEW / EMERGING / ESTABLISHED)
   × per feed-category band, seeded from the snapshot date so the draw is reproducible
   AND rotates month to month — coverage of the long tail accrues across snapshots
   instead of pretending to be exhaustive in one.
3. **Report shape:** aggregates + top-K exemplar findings per check (K≈5), full findings
   only in the machine JSON. The human report must fit on two screens or nobody reads it,
   and the work queue must stay sorted severity-first (it already is).
4. **Persist `cohort_spec`** (strata definitions + drawn ids + seed) in the snapshot —
   Q1's provability depends on this.

D's referee series has an additional hard bound: referee data must be FREE
(Wikipedia pageviews, already the held-out referee pattern) — never Apify/Google Trends
pulls (clock-slot rule, paid). Wikipedia pageviews for ~300 topics/run is fine; for 3k
it's not. Sampling is also the cost policy.

## Q4 — Does the four-module frame generalize to market/crypto? Feed parameter now?

**Answer: yes, and yes — parameterize the SIGNATURES now, build the trend feed only.**

The four questions are feed-agnostic: sources tracking? scores moving? scores right vs a
held-out referee? where in the lifecycle? Market and crypto already have the structure
waiting — their own ledgers, their own referee (realized EOD price direction via FMP,
which is exactly the "held-out external truth" role Wikipedia plays for trend), their own
stage/tier labels. What does NOT generalize is the constants: MAINSTREAM_REFEREE_LVL is
log10-pageviews-specific, ENGINE_ACTIVE stage sets are trend-specific, the collapse bands
are trend-specific (and possibly stale — see integrity note).

**Modification:** `run_assessment(adapter, feed="trend")`; add `feed` to `Finding` and to
the snapshot key `(run_at, feed, param_version)`; move feed-specific constants into a
`FEED_PROFILES` dict (referee semantics, stage vocabulary, thresholds) so
`assessor-v1/trend`, `-v1/market`, `-v1/crypto` are distinct provable lines. Cost: ~20
lines now. Payoff: the enterprise story becomes "readiness per product surface, three
independent upward trend lines, each validated by an independent referee" — that is a
materially stronger diligence page than one blended number, and it mirrors the
three-ledger architecture the founder already committed to. Do NOT build the market/
crypto adapters yet — just don't let trend assumptions fossilize into the signatures.

---

## Verdicts

### (A) CONCEPT — APPROVE-WITH-CONDITIONS
- **Verdict:** the teaching layer (gap + prescribed solution per failure), the
  machine-readable work queue, and above all the versioned readiness trend line are
  genuinely novel vs the fleet — /monitor tells you what is broken NOW; nothing today
  tells you whether the system is more ready than last month. That delta is the product
  of this file.
- **Biggest opportunity:** monthly `audits/assessor/` snapshots per feed = the Phase-1
  diligence page. Payment portal is gated on "prove scoring is accurate"; this is the
  proof instrument, provided the line is provable (Q1 conditions).
- **Condition:** reposition it explicitly as the AGGREGATOR/GRADER over the existing
  fleet + ledger + referee — not a 10th checker with its own facts. Where it overlaps
  /monitor, it must consume /monitor's answer, never re-derive and possibly contradict it.

### (B) DESIGN/INTEGRITY — APPROVE-WITH-CONDITIONS
- **Verdict:** structure is sound (abstention, denominators, severity sort, frozen
  version-stamped params, "a failing grade is a successful run"). Four must-fix items.
- **Biggest blocker:** the C-module `variants` solution text prescribes
  "alias-consolidation in normalize_topic() so variants merge BEFORE scoring" — that is
  Option C, unanimously REJECTED by the Board on 2026-07-15 (alias consolidation is
  DISPLAY-ONLY). An assessor whose prescribed fix contradicts a Chairman ruling would
  teach Claude Code to violate governance. Rewrite the solution to display-layer alias
  grouping + flagging, and make the check compare variants for MEASUREMENT only.
- **Modifications:**
  1. Fix the variants solution text (above) — blocking.
  2. Verify-or-drop the hardcoded 1.0-era signatures: COLLAPSE bands (40–50/60–72),
     "frozen at 74", "~45/67" — validate against live v2 data before first run; if they
     don't reproduce, ship without them and add back under a bumped param_version.
  3. Solutions must prescribe INVESTIGATION, not score changes: "raise/soften component
     caps" edges toward tune-to-pass and violates flag-never-force. Rephrase as "flag
     for founder review + trend-signal-diagnostic."
  4. Readiness math: module-weighted 25/25/25/25, INSUFFICIENT count printed beside the
     %, param_version bump rule (Q1). Referee series: Wikipedia/free only, never Apify.

### (C) WIRING — APPROVE-WITH-CONDITIONS
- **Verdict:** run it as a scheduled read-only skill/agent consuming HTTP endpoints;
  do NOT implement the 10-method adapter as raw SQL.
- **Biggest blocker:** the second read path (Q2) — duplicate maintenance + the 07-06
  pool-outage failure class. Endpoints-first is the one-truth architecture.
- **Modifications:**
  1. Adapter = HTTP client over `/monitor` + `/health/collectors` + `/accuracy/ledger`
     + `/monitor/catmaps`; ONE new thin engine endpoint for score histories/components
     (batch-paced, superset-cached, single-flight — house pattern).
  2. Cadence: monthly SNAPSHOT run (writes DB row + git JSON — the official trend
     point), weekly internal run feeding the work queue (not snapshotted), aligned
     after `/improve-system` so they share a data window. Never on deploy/boot.
  3. Storage: `assessor_snapshots` table + `audits/assessor/YYYY-MM-DD_<feed>.json`
     committed; later a read-only `/assessor/history` for the terminal's enterprise view.
  4. Sampling policy (Q3) with persisted cohort_spec; `feed` parameter (Q4) now.

— The Expansionist


---

# BOARD MEMO — The Outsider (VC / former hedge-fund banker)
**Re:** `07 17 2026 - nowtrendin_scoring_assessor.py` — is this the right proof instrument for un-pausing the payment portal?
**Date:** 2026-07-17
**Posture:** First look, plain English, diligence chair. I did not build this system; I am the person you would eventually pitch.

---

## 0. The one-paragraph read

This is a well-built internal checklist wearing the costume of a proof instrument. As an ops tool for a one-founder company, I like it — a prioritized work queue with severities is exactly what a solo operator needs. As *proof* that scoring is accurate — the thing the payment portal is waiting on — it is structurally incapable of being that, because the same party writes the checks, runs the checks, fixes the failures, and reports the grade. The proof instrument you need already exists in this company: the held-out accuracy ledger. The assessor should feed it, not compete with it.

---

## 1. Question 1 — Would I believe "Phase-1 readiness 40% → 85% over five monthly runs"?

**No. Not as this file computes it.** Here is exactly why, from the code, not from vibes:

**(a) The denominator is alive.** `readiness = PASS / gradeable` where "gradeable" is whatever checks happened to fire this run, minus every `INSUFFICIENT` abstention (line 362–363). Three consequences:
- Add a batch of easy checks next month → readiness rises with zero system improvement.
- Remove or reshape a failing check → readiness rises.
- Topics/sources churn between runs (they will — this is a trend engine), so run 1 and run 5 are grading **different cohorts**. A 40→85 line over five runs where the denominator, the check roster, and the graded population all shifted is not a trend; it is five unrelated snapshots joined by a line.

**(b) Abstentions leave the denominator.** `INSUFFICIENT` findings are excluded entirely. A thin-data month with 6 gradeable checks passing 5 reads 83%; a rich month passing 40 of 60 reads 67%. The number moves *against* information content.

**(c) "Frozen thresholds" are frozen by comment.** The constants block says "never tune to pass" and stamps `PARAM_VERSION = "assessor-v1"` — good instinct, but nothing enforces it. The evidence pack already flags that some of these constants (`COLLAPSE_DET_BAND` 40–50, the "~45/67 collapse signature", "mcp frozen at 74") may be **1.0-era stale**. If the thresholds themselves encode last year's failure modes, the grade is measuring against a ghost.

**(d) The loop is closed on itself.** The tool emits a work queue; the founder fixes the queue; the same tool re-grades. That is what a checklist is *for* — it is legitimate ops. But as evidence, it is homework graded by the student's own answer key. Every improvement in the number is equally consistent with "the system got better" and "the fixes were shaped to the checks."

**What would make the number credible to a diligence chair:**
1. **Freeze the roster, not just the thresholds.** Version the *check list* (`roster-v1`: N checks, named). Readiness is only comparable within one roster version. Adding a check = new roster version = the trend line restarts or is dual-reported.
2. **Always print the fraction, never the bare percent.** "85% (34/40, roster-v1)" is auditable; "85%" is marketing.
3. **Persist raw inputs per run** so any run can be re-graded later by anyone (including a skeptical acquirer's diligence team). If the inputs are gone, the grade is unfalsifiable.
4. **Third-party referee on the outcome-facing checks.** The C/D modules already lean on Wikipedia pageviews — held-out, external, free. That is the only part of this tool an outsider would weight.
5. **A change log with a second pair of eyes.** Any threshold or roster change gets a dated entry and (in this company's structure) a board/Chairman sign-off. Right now "who can change the grading" = "whoever edits the file."

Even with all five, this number is an **internal gate**, not external proof. I would report it to the board; I would never put it in front of a buyer.

## 2. Question 2 — Self-assessment vs the held-out accuracy ledger: which number do I anchor on?

**The ledger. Without hesitation.** The company already owns the rarest thing in this category: an external-ground-truth instrument — held-out, forward-only, 365-day patience, epoch-stamped, with a Wikipedia-pageviews referee on wins and honest denominators (blended 10% vs tracked-race 26.9%, with the pre-broken split explaining the gap). That is the moat *and* the proof. No self-graded checklist competes with "did a later Google breakout confirm our earlier detection, verified by an independent referee."

**How the two should relate in the story:** the assessor is the *preflight instrument panel*; the ledger is *whether the plane actually arrived early*. Preflight tells you the engine is safe to run; it never tells you the flight succeeded. So:
- **Portal-reopen criterion = a ledger number** (e.g., tracked-race hit rate over a stated window with a stated denominator, referee-verified), *optionally* AND-ed with "assessor readiness ≥ X on roster-v1" as a hygiene gate.
- **Never the reverse.** The moment "readiness 85%" becomes the headline and the ledger's 26.9% is the footnote, the story is inverted and any competent diligence will invert it back — unkindly.
- This company already has the right reflex codified: the catch-all % is ruled "never publish externally as an accuracy KPI — it is a congestion gauge." **Readiness % deserves the identical rule, written down the same day this tool is adopted.**

## 3. Question 3 — The "teacher" framing: real ops discipline or complexity theater?

**Genuinely useful — one layer of it. The rest is duplication with a hazard attached.**

The valuable 20%: `Finding.gap` + `Finding.solution` + severity-sorted `work_queue` + machine JSON. For a solo founder already running 16 agents, a single prioritized "here is what is broken and why it matters" list that Claude Code can ingest is real leverage. That layer does not exist in the current fleet and I would keep it.

The duplicative 60%: modules A and B substantially re-implement what `/monitor` (Source Watchdog, Scorer Watchdog, Pipeline Integrity) and `/health/collectors` already do — the authoring session did not know the fleet existed. A 17th thing to babysit that re-checks what nine agents already check is complexity theater by definition. The fix is cheap: make the assessor a **formatter/aggregator over existing endpoints**, not a parallel measurement stack with its own 10-method adapter.

The hazardous 20%: **canned solutions that touch scoring.** Two live examples in the file:
- The variants check prescribes "add alias-consolidation to `normalize_topic()` so variants merge **before scoring**" — this **directly contradicts the Board's 2026-07-15 unanimous ruling** (alias consolidation is display-only; score-time merge rejected). A teaching tool that teaches the developer to violate a Chairman ruling is worse than no tool.
- The freeze check prescribes "raise/soften the saturating component caps" — that is threshold-tuning advice emitted automatically, in a company whose integrity charter says *never tune a threshold to pass*. Prescriptions that modify scoring must be flagged `REQUIRES BOARD REVIEW`, not handed to Claude Code as a work item.

**Verdict on the framing:** keep the teacher, fire half the curriculum.

## 4. Question 4 — The synthetic demo: could a screenshot ever be mistaken for a real result?

**Yes, and the file makes it easy.** The `_Demo` run produces output *byte-identical in format* to a real run: same banner, same `PHASE-1 READINESS: N%`, same `param_version` stamp, real-looking topic names (trump, china, apple, openai, fifa), plausible dates — and it **writes `assessor_work_queue.json` to the working directory** with no marker that the contents are fabricated. In a company where terminal screenshots circulate to advisors and (eventually) investors, that is a fabricated-metrics incident waiting for a careless Tuesday. Given this founder's own integrity standard ("every claim data-supported and defensible to hedge-fund counsel"), this is the cheapest fix with the highest downside avoided:
- Watermark every demo line and the header: `SYNTHETIC DEMO — NOT LIVE DATA`.
- `param_version = "assessor-v1-SYNTHETIC-DEMO"` on demo runs.
- Demo writes `assessor_work_queue.DEMO.json` or nothing at all.
- Require an explicit `--demo` flag; bare invocation with no adapter should refuse to run, not silently grade fiction.

## 5. Verdicts

**(A) CONCEPT — APPROVE-WITH-CONDITIONS.** The teaching layer (gap/solution/work-queue JSON) fills a real gap. The measurement layer duplicates the existing fleet and the readiness % is internal-only, never external.
> **Point-blank question for the founder:** *"Name one check in this file that `/monitor`, `/health/collectors`, and the ledger do not already run. If the honest answer is 'only the grade and the work queue,' why is this a four-module agent instead of a thin formatter over the outputs you already trust?"*

**(B) DESIGN/INTEGRITY — REJECT AS-IS for any live run; APPROVE after modifications.** Required before first live run: (1) delete/replace the alias-consolidation solution — it contradicts the 2026-07-15 Chairman ruling; (2) verify or retire the 1.0-era collapse bands and "frozen at 74" signature against the live system; (3) freeze and version the check roster, print denominators with every percent; (4) mark all score-touching solutions `REQUIRES BOARD REVIEW`; (5) watermark the synthetic demo; (6) referee series must use free Wikipedia pageviews or existing slot-scheduled data — never new paid Apify pulls (clock-slot rule).
> **Point-blank question:** *"Who can change a threshold or add/remove a check between monthly runs, and where is that change logged? If the answer is 'me, in this file,' your 40→85 trend line is unauditable — including to you."*

**(C) WIRING — APPROVE-WITH-CONDITIONS.** Do not implement the 10-method `AssessorAdapter` as a fresh measurement stack. Read the existing `/monitor` run_all, `/health/collectors`, `/accuracy/ledger`, and referee outputs. Run it as a scheduled skill (weekly, alongside `/improve-system`) or an offline job — **not** a new engine endpoint on the serve path this company has already had outages on. Persist each run's inputs + JSON to `audits/` so the trend is re-gradable.
> **Point-blank question:** *"Before the first run, say out loud what number reopens the payment portal: this tool's self-grade, or a ledger number with a denominator. If you can't answer in one sentence today, the tool will quietly become the answer — and it's the wrong one."*

## 6. The story I would tell an investor (so you don't have to reverse-engineer it later)

"Our instrument panel is green (assessor, internal, roster-versioned, denominators shown) **and** our outcomes are independently confirmed (ledger: tracked-race X% over N races, referee-verified, 365-day patience)." Instruments gate the launch; outcomes *are* the pitch. A company that leads with its own report card gets discounted; a company that leads with a held-out ledger and treats the report card as plumbing gets believed. You already built the hard half. Don't let the easy half upstage it.

— The Outsider


---

# BOARD MEMO — THE EXECUTIONER · Scoring Assessor (`07 17 2026 - nowtrendin_scoring_assessor.py`)
**Date:** 2026-07-17 · **Question:** what is the RUNNABLE path, what ships, what gets cut.

---

## 1. DOES IT EXECUTE STANDALONE? — YES, with one Windows caveat

Ran `python "07 17 2026 - nowtrendin_scoring_assessor.py"` from the scratchpad.

- **First run CRASHED** on this Windows box: `UnicodeEncodeError: 'charmap' codec can't encode` —
  the report uses `═`/`·`/`✓`/`✗` and Windows console defaults to cp1252. **Fix required**
  (see §5, F1) — either `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at top of
  `print_report`, or ASCII marks. Until then it only runs with `PYTHONIOENCODING=utf-8`.
- **Second run (UTF-8 forced): clean, exit 0.** Demo output exactly as designed:
  - `PHASE-1 READINESS: 40%` — grades: Sources **C** (6/11), Movement **C** (1/3),
    Accuracy **F** (0/7), Lifecycle **B** (3/4).
  - 15-item severity-sorted work queue (9 HIGH), each with GAP + SOLUTION text.
  - Wrote `assessor_work_queue.json` to **CWD** — a side effect that will litter the repo root
    if run there (the repo root already has stray `bf.json`/`ledger.json`/`r*.json`). Must be
    pointed at `audits/assessor/` (F2).
- The demo data is synthetic and clearly labeled; the four failure archetypes it simulates
  (silent-absent source, frozen score at cap, mainstream mis-read, stale-active stage) are the
  right archetypes. The logic itself is sound, deterministic, dependency-free (stdlib only).

## 2. ADAPTER → CONCRETE SOURCE MAP (the 10 `AssessorAdapter` methods)

| # | Method | Concrete source in THIS repo | Status |
|---|--------|------------------------------|--------|
| 1 | `source_health()` — `{src: {last_success, daily_counts[]}}` | `last_success`: **EXISTS** — `GET /health/collectors` (`collector_health` table: `last_success_at`, `last_signal_count`, `consecutive_failures`; report shape in `transfer/collector_health.py get_health_report`). `daily_counts[]`: **PARTIAL** — no per-day signal series is stored; `api_usage` (source, day, calls) is a per-day CALL series (usable proxy via `get_api_usage`), or derive true volume with a new query `SELECT platform, date(collected_at), COUNT(*) FROM raw_signals GROUP BY 1,2` (8 days needed; data exists) | EXISTS + small new query |
| 2 | `expected_sources()` | **EXISTS** — `COLLECTOR_EXPECTATIONS` keys in `transfer/collector_health.py` (also embedded in the `/health/collectors` response: every expected collector appears with DOWN if absent — the "silent absence" check is ALREADY served) | EXISTS |
| 3 | `source_coverage()` — per-source topic-coverage vs historical baseline | **DOES NOT EXIST.** "Seen" is computable (`topic_signals` has `platform`+`topic_key`), but the BASELINE ("topics this source historically covers") is undefined — no table, no definition. Building it is a real design task (per-source topic-coverage baselines) | MISSING → defer (cut from v1) |
| 4 | `score_histories()` — per-topic detection series | **EXISTS as data** — `velocity_scores` (topic_key, scored_at, detection; 365-day retention; `/topic/{key}` detail already serves `score_history`). Batch across a cohort = one new query or N detail calls on a bounded cohort | EXISTS (new query/loop) |
| 5 | `component_states()` — `{component: (value, cap)}` | **PARTIAL** — component values exist (`gradient_strength`, `inertia_score`, `platform_diversity`, … columns + `serve_payload` breakdown in `calibration_engine.py` ~L1417). Caps are implicit (100); the demo's `NicheConcentration`/`PlatformDiversity` names are 1.0-era — v2 names are `niche_concentration`/`platform_diversity` (see `ai_grade.py` L489-501) | EXISTS (rename + new query) |
| 6 | `score_snapshot()` — detection/confidence/stored_gap | **EXISTS** — `/scores` (served `serve_payload`); `stored_gap` = `heisenberg_gap` (`calibration_engine.py` L1446). Gap-arithmetic check wires directly | EXISTS (endpoint) |
| 7 | `referee_mainstream_levels()` — log10 median daily pageviews | **PARTIAL** — `transfer/referee_wikipedia.py` has `resolve_article()` + `fetch_pageviews()` (Wikimedia REST, **FREE**, held-out). A ~15-line wrapper (median→log10 over trailing 30d) is new. NOT served by any endpoint today | small new wrapper, free |
| 8 | `variant_groups()` | **EXISTS** — entity-alias layer: `GET /aliases` (confirmed groups) + `/monitor/aliasmaps`. ⚠ the file's SOLUTION text ("merge before scoring") contradicts the Board's 2026-07-15 Option-A ruling (display-only) — text must be rewritten (F3) | EXISTS (fix the prescription text) |
| 9 | `referee_series()` — per-topic external interest series | **PARTIAL** — `fetch_pageviews(article, start, end)` gives exactly this, FREE (Wikimedia REST, declared UA, no Apify, no clock-slot concern). At full scale (6000 topics) it's thousands of HTTP calls — **the Apify-safe/free answer is: Wikipedia pageviews, bounded cohort** (top ~25 by N + a sample of ledger-pending), NOT Google Trends | EXISTS per-topic; scale must be bounded |
| 10 | `engine_stages()` | **EXISTS** — stage is derived from Detection via `stageOf` (§13 CLAUDE.md); available from the `/scores` payload (or recompute from detection thresholds) | EXISTS (endpoint) |

**Summary:** 6 of 10 wire to existing endpoints/tables today; 2 need thin new queries/wrappers
(daily volume series, referee levels); 1 needs bounding (referee series); **1 does not exist and
should be cut from v1** (per-source coverage baselines).

Also note: modules A and part of B **duplicate the live fleet** — `/health/collectors` already
does freshness+silent-absence+consecutive-failures; `/monitor` (9 agents) already does scorer
liveness, pipeline integrity, calibration audit. The assessor's NOVEL value is the teaching
layer (GAP+SOLUTION), the readiness %, the machine work-queue, and modules C (referee no-gap
test) and D (lifecycle agreement) — nothing in the fleet does those.

## 3. WIRING SHAPE — RECOMMEND: **skill over deployed endpoints** (like `/improve-system`)

Options considered:
- **(a) Skill hitting the deployed engine's endpoints** — RECOMMENDED for v1.
- (b) New engine endpoint (`/monitor/assessor`) — SHIP-LATER. Costs a deploy, adds load to a
  dyno that has H12'd under monitor endpoints before (`/monitor/catchall` history), and needs
  the two missing queries added engine-side first.
- (c) Standalone cron on the founder's box — rejected: `heroku run`/psql is broken on this
  Windows machine (known); endpoints are the sanctioned access path anyway.

**Why (a):** read-only by construction (can't touch the DB), zero deploy risk, adapters mostly
map to endpoints already, matches the established `/improve-system` + `/data-health` pattern,
and its output (work-queue JSON) is consumed BY Claude Code — which is exactly where a skill runs.

**Steps (v1, ~half-day):**
1. Apply file fixes F1–F6 (§5). Move the file to `transfer/tools/scoring_assessor.py` (or
   `monitoring/`) — repo root with a space-laden date-name is not a home.
2. Write `EndpointAdapter(AssessorAdapter)` in the same file: `/health/collectors` →
   methods 1–2; `/scores?limit=~200` → 6, 10; `/topic/{key}` (bounded cohort ~25) → 4, 5;
   `/aliases?status=confirmed` → 8; `referee_wikipedia.fetch_pageviews` (imported directly,
   FREE) → 7, 9 on the bounded cohort; method 3 returns `{}` (check auto-skips).
3. Create skill `/scoring-assessor` (SKILL.md modeled on `/improve-system`): run the adapter,
   write the human report + `assessor_work_queue.json` to `audits/assessor/ASSESSOR_<date>/`,
   and diff readiness % vs the previous run (the "trackable over time" requirement).
4. Cadence: **daily is overkill; 2×/week or fold into the Saturday `/improve-system` run** as a
   pre-step whose work queue feeds the audit. Wikipedia calls ≈ cohort×2 ≈ 50-60/run — free.
5. After 2-3 stable runs, consider promoting to `/monitor/assessor` (engine endpoint) with the
   readiness % persisted to a table for trend charts. Not before.

## 4. CUT / DEFER FROM V1

- **CUT: module A coverage check (`source_coverage`)** — baseline data doesn't exist; inventing
  it inline would be a guess, and the file's own abstention rule says don't guess. Revisit as a
  designed feature (per-source topic-coverage baselines) if module A findings prove insufficient.
- **CUT: module D at full scale** — bounded cohort only (top ~25 + ledger-pending sample).
  Full-universe lifecycle audit belongs to the ledger sweep, not this tool.
- **CUT: the raw direct-DB adapter path** — v1 talks to endpoints only.
- **DEFER: Google-Trends-based referee anything** — Apify clock-slot rule; Wikipedia only.
- **KEEP but demote: the collapse-band signature check** — see F4.

## 5. FIX BEFORE FIRST LIVE RUN (sequenced)

- **F1 (blocker):** Windows encoding crash — `sys.stdout.reconfigure(encoding="utf-8",
  errors="replace")` guard (or ASCII status marks). Verified crash on this box.
- **F2 (blocker):** output path — write `assessor_work_queue.json` + report to
  `audits/assessor/`, never CWD.
- **F3 (integrity, blocker):** rewrite the `variants` SOLUTION text — current text prescribes
  score-time merge (`normalize_topic()` alias-consolidation), which the Board REJECTED
  unanimously 2026-07-15 (Option A: display-only fold). New text: "confirm the alias pair via
  `/aliases` review; display-layer fold only — never merge before scoring." A teaching tool
  that teaches a rejected fix is worse than no tool.
- **F4 (staleness):** `COLLAPSE_DET_BAND (40,50)` / `COLLAPSE_CONF_BAND (60,72)` and the
  "known ~45/67 collapse signature" are 1.0-era claims the authoring session imported blind.
  Do NOT treat as a live FAIL signature: demote the band-match to an annotation on the
  (independently valid) `det<70 or conf<70` mainstream test, and verify the band against the
  live distribution before ever re-promoting. Same for the frozen-score SOLUTION's cap names —
  rename to v2 component names (`niche_concentration`, `platform_diversity`).
- **F5 (consistency):** `STALE_SOURCE_HOURS=24` contradicts the engine's own per-collector
  windows (`COLLECTOR_EXPECTATIONS.max_gap_minutes`, 420m for 6h-cadence collectors, §13 stale
  window rule). Read staleness FROM `/health/collectors` statuses instead of re-deriving with a
  flat 24h — one source of truth, and the assessor stops disagreeing with the watchdog.
- **F6 (math nit, non-blocking):** `grade()` weights every Finding line equally, so a module's
  grade depends on how many PASS lines a check emits (per-source vs per-cohort). Acceptable for
  v1; note it in the report header so nobody reads readiness % as calibrated.

## 6. VERDICTS

- **(A) CONCEPT — SHIP.** The teaching layer (GAP+SOLUTION per failure), readiness %, and
  machine work-queue are genuinely novel vs the 9-agent fleet; modules C/D fill a real hole
  (no live referee no-gap test, no lifecycle-agreement check exists today). Position it as a
  CONSUMER of `/monitor` + `/health/collectors`, not a rival re-implementation.
- **(B) DESIGN/INTEGRITY — SHIP-WITH-CONDITIONS.** Conditions = F1–F5 above, all cheap. The
  file honors read-only/abstain/denominator rules already; the two real integrity defects are
  the Option-C alias prescription (F3) and the imported 1.0-era signatures (F4).
- **(C) WIRING — SHIP as `/scoring-assessor` skill over deployed endpoints**, bounded cohorts,
  Wikipedia-only referee, output to `audits/assessor/`, cadence 2×/week or pre-step of the
  weekly `/improve-system`. Engine endpoint = SHIP-LATER (after 2-3 stable skill runs).
  Direct-DB adapter + coverage baselines + full-scale D = CUT from v1.

**Sequenced worklist:** F1→F2→F3→F4→F5 (edits, ~1h) → move file into `transfer/tools/` →
`EndpointAdapter` (~2h) → SKILL.md (~1h) → first live run → review its work queue with the
founder → then decide on `/monitor/assessor` promotion. Nothing here blocks on a deploy.

— The Executioner


---

# BOARD MEMO — The Economist
## Review: `07 17 2026 - nowtrendin_scoring_assessor.py` ("Scoring Assessor / Teacher")
### Date: 2026-07-17 · For the Chairman (founder) · Canon: Kindleberger, Taleb, Malkiel, Bernstein, Friedman & Schwartz, Reinhart & Rogoff, Belsky/Gilovich, Zweig, Smith

---

## 0. The instrument in one sentence

A read-only grader that asks four questions (sources tracking? scores moving? scores right? trend alive?), emits PASS/FAIL findings with a prescribed fix each, rolls them into module letter grades and a single "Phase-1 readiness %," and writes a machine work queue for Claude Code to consume.

Bernstein's definition of risk — *what remains after you think you have measured everything* — is the correct lens for the whole review. The assessor measures what it can see. The dangers below are all in what it cannot: the checks it doesn't run, the denominator it silently changes, the tail behavior of its short windows, and the feedback loop it creates by teaching.

---

## 1. BERNSTEIN / GOODHART — the readiness % as a target

**The problem, stated plainly.** The moment `phase1_readiness_pct` becomes the number that unlocks the payment portal, it stops being a measurement and becomes a target — Goodhart's law. And the agents that will be "taught" by the work queue are precisely the agents (human + Claude Code) with the power to change what is checked. Three failure channels, in ascending subtlety:

1. **Tuning thresholds to pass.** The file's own charter forbids it ("never tunes a threshold to pass") and `PARAM_VERSION` freezes the constants. Good — necessary, not sufficient.
2. **Optimizing the CHECKS, not the accuracy.** A fix that makes `no_gap` pass (e.g., a band-specific score adjustment for referee-confirmed mainstream topics) is indistinguishable, to the assessor, from a fix that makes the *engine* better. The work queue's `solution` fields actively invite this: "extend the dual-pathway anti-collapse preservation across the mid-mainstream band" is a prescription aimed at the check's trigger region. Fixing the band the referee looks at is teaching to the test.
3. **Gaming the denominator.** `readiness = PASS / gradeable`. This denominator is soft in four ways:
   - **INSUFFICIENT rows are excluded.** Starve a module of history (or of referee coverage) and its failures vanish from the denominator. Abstention is epistemically right (Taleb would insist on it) but it must not *raise* the headline number. Today it does.
   - **PASS rows are cheap to mint.** Module A emits one PASS per fresh source per run; a fleet of small healthy sources dilutes one catastrophic C-module failure. The metric is an unweighted average over checks of wildly different economic significance — a classic index-construction error.
   - **The check set itself is unregistered.** Nothing stops next month's run from adding, removing, or re-scoping checks, silently moving the number.
   - **Severity doesn't reach the score.** A HIGH fail and a LOW fail cost the same readiness point. So the cheapest path to a higher % is fixing many trivial WARNs, not the one HIGH that matters.

**What resists Goodhart (design features to require):**

- **G1 — Registered check manifest, frozen per phase.** A `CHECK_MANIFEST` (check id, module, scope query, threshold set, weight) hashed into the report alongside `param_version`. Readiness is computed **only** over manifest checks. Adding a check = new manifest version = new series (see §2). This is check-set immutability, and yes — it is the single most important missing feature.
- **G2 — Fixed evaluation panel.** The topics/sources graded must be drawn by a *registered rule* (e.g., "all sources in collector_health config as of phase start; the top-N topics by a frozen selection rule"), not by whatever the adapter happens to return. Otherwise the easiest optimization is curating the sample. Reinhart & Rogoff's whole method was refusing to let the sample be chosen by the outcome.
- **G3 — Separation of teacher and examiner.** The work queue may prescribe fixes; the *verification* that a fix improved accuracy must come from an instrument the fixer does not control — the held-out accuracy ledger (LED/tracked-race), not the assessor's own re-run. A check flipping FAIL→PASS is evidence the check was satisfied, nothing more. Require: any HIGH-severity C-module fix ships only with a ledger-side confirmation (or explicit "no ledger movement expected, here's why").
- **G4 — Report the number as a vector, never a scalar, externally.** Internally the % is a useful thermometer. The portal-unlock decision should be gated on the *module-C and ledger* numbers with their denominators, not the blended %. (Same discipline the house already applies to the catch-all %: "congestion gauge, never an accuracy KPI.")
- **G5 — Severity-weighted, module-floored score.** If a scalar must exist: weight by severity, and cap overall readiness at the worst module's grade band (a chain is its weakest link; an A in source freshness cannot buy back an F in accuracy).
- **G6 — Denominator disclosure line.** Every report prints: checks run / abstained / added-since-last-manifest. An abstention-heavy run should *look* abstention-heavy.

---

## 2. FRIEDMAN & SCHWARTZ — series integrity (the M1/M2 splice problem)

*A Monetary History* settled arguments because the series was long **and consistently constructed**; where the definition of money changed, the splice was documented and the overlap published. The assessor, run monthly, aspires to be that series for scoring quality. As drafted it will not be one: the first time someone adds a fifth check to module A, the readiness % moves for reasons that have nothing to do with the system, and every cross-month comparison after that is an apples-splice-oranges argument.

**Series-integrity protocol (prescribed):**

- **S1 — Manifest versioning.** `manifest_version` (distinct from `param_version`: thresholds vs check-set). The monthly series is keyed on (manifest_version, param_version). Numbers across different keys are **never** plotted on one line without a splice note.
- **S2 — Overlap runs at every change.** When the manifest or params change, run BOTH definitions on the same data for ≥2 consecutive periods and publish both numbers (the F&S splice technique). The overlap quantifies the definitional jump so trend ≠ definition-change.
- **S3 — Immutable run archive.** Persist every report (raw findings JSON, not just the %) — the equivalent of keeping the worksheets. The house already has the pattern: 365-day retention, forward-only, never rewrite. Store in Postgres next to the ledgers, stamped with git SHA of the assessor file.
- **S4 — Frozen cadence and clock.** Same day-of-period, same UTC hour, same lookback windows. The catch-all lesson (warm/cold swings 33↔68% by *process restart phase*) applies verbatim: a series sampled at varying cycle phases measures the sampling, not the system. Pin the run to a slot after prewarm is warm and after the daily collection completes.
- **S5 — Additions enter as "shadow checks."** A new check runs and reports for ≥2 periods **outside** the graded set (status SHADOW, excluded from readiness) before promotion into the next manifest version. You get early visibility without breaking the series — the monetary-aggregate equivalent of publishing a satellite series before redefining the headline aggregate.
- **S6 — Never backfill.** Do not retro-run new manifests over old months and present it as history; recomputed history is simulation, and must be labeled as such (Reinhart & Rogoff's data appendix discipline).

---

## 3. TALEB — fat tails, bursty attention, and the lifecycle classifier

`classify_lifecycle` judges on `recent = mean(last 3)` vs `prior = mean(preceding 5)` vs `peak = max(all)`. Attention series are precisely the domain where this breaks:

- **Fat tails make `peak` a one-off hostage.** Attention interest is heavy-tailed; the max of the series is typically a single spike an order of magnitude above the body. After any spike, *everything* is <25–50% of peak forever — so a topic with a healthy, elevated plateau after one viral day is classified ENDED. The peak is not a level to revert to; it is a tail draw. Ratios-to-max are non-robust statistics by construction (a single observation determines the denominator).
- **Bursty/recurrent attention (spike–sleep–spike) is the NORM, not the exception.** Weekly sports cycles, earnings, episodic geopolitics, meme resurrections. The classifier will mark the sleep phase ENDED, the engine (correctly, if it has structural signal) keeps it active, and module D logs a FAIL against the *engine* — the assessor punishing the engine for being right about recurrence. Worse: an 8-point window cannot distinguish "dormant volcano" from "extinct volcano," and the difference is the entire product thesis. This is silent evidence: the topics that resurge after being called ENDED never appear in the report that called them dead.
- **3-vs-5 point means have enormous sampling variance** under fat tails; `recent > prior * 1.25` will flap on noise. And `PEAKING` requires `recent ≥ 0.9·peak` — under heavy tails almost nothing but the spike window itself ever qualifies, so PEAKING is nearly unreachable except in-spike.

**Robustness prescriptions:**

- **T1 — Replace `max` with a high quantile of a trailing window** (e.g., 90th percentile of trailing 90d) as the reference level; or use log-interest throughout. Never let one observation own the denominator.
- **T2 — Require persistence for terminal states.** ENDED only after N consecutive sub-threshold periods **and** a minimum elapsed time since last spike ≥ the topic's own observed inter-spike interval (or a global floor, e.g. 30d). Asymmetric patience is already house doctrine (the 365-day ledger patience window; "the big money is in the waiting"). ENDED is the assessor's version of judging a miss too early — same rule applies.
- **T3 — Add a RECURRENT/DORMANT-CYCLING class** for series with ≥2 distinct spikes, detected on the full history, exempt from ENDED-vs-active FAILs (downgrade to WARN "in inter-spike trough").
- **T4 — Downgrade all module-D disagreements to WARN in v1.** With 8 data points and a fat-tailed generator, D's verdicts are opinions, not measurements. Let them accumulate a track record (does D's ENDED actually predict no-resurgence at 90d?) before they carry FAIL weight in readiness. Grade the grader first.
- **T5 — Never let module D feed the ledger or stage decay directly.** Its "solution" text ("drive stage decay from freshness/decline") is a *scoring change* prescribed from a 3-point mean — exactly how fragile rules enter systems. Flag-never-force.

---

## 4. MALKIEL — the null hypothesis each module must beat

Malkiel's discipline: before believing a signal, state the naive alternative that costs nothing, and show you beat it. A FAIL from the assessor is itself a claim — and claims need nulls. Per module:

- **A (sources).** *Null: collection volumes are stationary noise; a 50% one-day drop is within normal variation for this source.* A Poisson-ish feed with mean 30/day breaches `VOLUME_DROP_ALERT=0.5` regularly by chance. Beat it: calibrate per-source thresholds to that source's own historical dispersion (z-score or quantile, not a universal 0.5×), and require 2 consecutive breach days. Otherwise module A becomes an alarm that always rings — and Zweig will tell you what operators do with alarms that always ring: they stop listening (alarm fatigue is how the *real* outage gets missed).
- **B (movement).** *Null: a frozen score is the correct output of unchanged inputs.* Six identical readings on a genuinely static topic is truth-telling, not failure. The check as written cannot tell "cache bug / cap saturation" from "the world didn't move." Beat it: FAIL only when the score is frozen **while inputs changed** (input-delta gate) or a component sits at cap. The cap-saturation branch is legitimate; the bare freeze branch needs the conditioning. Conversely — *null for volatility*: thin topics are volatile because attention is volatile; std>12 on a low-volume topic may be the honest read.
- **C (accuracy).** *Null: the referee is wrong or mismatched, not the engine.* Wikipedia pageview levels proxy *fame stock*, the engine's Detection/Confidence measure *attention flow and structure* — a high-pageview topic ("china", "apple") reading mid-band is only a failure if the engine *claims* to measure the same construct at the same horizon. The `no_gap` check assumes referee-mainstream ⇒ engine-must-read-high/high. That's a mapping hypothesis, and it must be validated before FAILs are believed: show that on an agreed calibration set, referee level ≥4.0 and engine ≥70/70 co-occur at (say) ≥90% when humans adjudicate "already mainstream." Also: perennial-fame topics (country names, mega-caps) have permanently high pageviews with zero current surge — the null says the engine's mid read may be *right*. Segment the referee cohort: exclude perennial entities (pageview level high AND flat) from the mainstream cohort, or the check punishes the engine for refusing to call "india" a trend. The gap-arithmetic check, by contrast, has a tautological null (stored = computed) and needs no defense — it is the best check in the file.
- **D (lifecycle).** *Null: a monkey classifier that says STEADY for everything.* Given fat tails and 8 points, the burden is on D to show classification skill above that monkey (does FADING today predict lower interest at +14d better than base rate?). Until measured, D's disagreement FAILs are unfalsifiable stories.

Institutionalize it: **every check in the manifest carries a `null_hypothesis` field and a note on how the threshold was calibrated against it.** A check that cannot state its null does not enter the manifest.

---

## 5. CIRCULARITY — does the teaching loop train the system toward the referee?

Yes — this is the memo's sharpest warning, and it is subtle because every component is individually clean. The referee is held-out from *scoring* (referee_wikipedia never imports into the engine — good). But the assessor creates a **second-order coupling through the work queue**: referee disagreement → FAIL → prescribed engine change → Claude Code implements → next run, referee agreement improves → readiness rises. Iterate monthly and the engine's parameters have been fitted to Wikipedia pageviews *by gradient descent through the developers*. No import statement required; the humans are the backprop.

Consequences if unchecked:
- The engine converges toward a *lagging* fame index — the exact opposite of the before-it-arrives thesis. Wikipedia pageviews confirm arrival; an engine trained to agree with them detects arrival, not approach. (The house's own 2026-07-07 finding — Dark Matter is late-confirmation, not early-warning — shows the drift direction this loop would amplify.)
- The referee simultaneously stops being a valid *validator*: once targeted, it's Goodharted too, and the accuracy ledger inherits an engine subtly optimized to a different objective.
- Kindleberger's addendum: manias are precisely when mainstream confirmation (pageviews) and forward-looking value diverge most. An engine trained to the referee is trained to be maximally wrong at the moments that matter most.

**Firewall prescriptions:**

- **R1 — Referee findings may prescribe DIAGNOSIS, never SCORE CHANGES.** Rewrite module C/D `solution` fields to route to *investigation* ("audit inputs/coverage/caching for this topic") and to *held-out logging* ("record for the lead audit") — never "extend anti-collapse preservation across the band" (a direct score-tuning instruction). The work queue's task schema should carry a hard field: `may_touch_scoring: false` for any finding whose evidence includes referee data. Score-affecting changes keep their existing gate: backtest-before-ship + board review — with the *ledger*, not the assessor, as the acceptance instrument (G3).
- **R2 — Rotate/ensemble referees, and hold one out from the teacher.** If module C uses Wikipedia, the acceptance test for fixes must use a different independent series (Google Trends slot data already collected, or the ledger's realized outcomes). Never let the same referee both generate the work queue and grade the fix. One referee must remain untargeted — a series no work-queue item is ever derived from — as the drift detector.
- **R3 — Track the coupling explicitly.** Add a standing meta-metric to the report: engine-vs-referee correlation over time. If it *rises* toward 1.0, that is not success — it is evidence the loop is closing. The product's value is precisely the LEAD, i.e., disagreement now, agreement later. The number to maximize is the ledger's tracked-race LED rate, not contemporaneous referee agreement.
- **R4 — The alias fix must be struck regardless** (contradicts the Chairman's 2026-07-15 ruling: alias consolidation is display-only; score-time merge rejected unanimously). Its presence in the `solution` field is a live example of the loop's danger: a stale authoring session's prescription would have walked a rejected score-time change in through the work queue. The queue needs a rulings-check gate before Claude Code consumes it.

---

## 6. VERDICTS

### (A) CONCEPT — **APPROVE-WITH-CONDITIONS**
The teaching layer (gap + prescribed solution per finding), the abstention discipline, denominator-shipping, and the machine work queue are genuinely novel versus the 9-agent /monitor fleet and worth having. "A failing grade is a successful run" is Bernstein-grade epistemics. But as an *argument-settling series* it fails F&S consistency requirements until the manifest/splice protocol (§2) exists, and the readiness scalar as a portal-unlock gate is a Goodhart trap (§1). Framework: a measurement instrument earns authority through (i) registered construction, (ii) consistent series, (iii) stated nulls, (iv) independence from what it measures. It currently has (iii) partially and (iv) nominally.

### (B) DESIGN/INTEGRITY — **REJECT AS-DRAFTED** (approvable after modifications)
Blocking items before any live run:
1. Strike/rewrite the alias-consolidation solution (contradicts the 2026-07-15 Chairman ruling) — R4.
2. Rewrite all referee-derived `solution` fields to diagnosis-only; add `may_touch_scoring:false` — R1.
3. Verify-or-demote the hardcoded folklore: the (40–50)/(60–72) collapse bands and "frozen at 74" are possibly 1.0-era; a frozen threshold encoding a stale fact is *worse* than a tunable one (it will FAIL forever on ghosts or PASS forever on the real current failure). Each such constant needs a live-system verification note or removal.
4. Null-hypothesis conditioning per §4: input-delta gate on the freeze check; per-source calibrated volume thresholds with 2-day persistence; perennial-fame exclusion from the mainstream cohort; module D demoted to WARN-only.
5. Lifecycle robustness per §3 (quantile reference, persistence for ENDED, RECURRENT class).
6. Readiness recomputation per §1: severity-weighted, module-floored, abstention-disclosed, manifest-scoped; the blended % never gates the portal by itself.
7. Referee series must be FREE sources (Wikipedia pageviews) or existing clock-slot data — never new paid Apify pulls (house rule; also plain cost discipline).

### (C) WIRING — **APPROVE-WITH-CONDITIONS**
Do **not** build the 10-method adapter against raw tables — that duplicates ingestion the fleet already does and creates a second source of truth (two measurements of one quantity is how splice disputes are born). The adapter should read the EXISTING instruments: /health/collectors (module A), score history already persisted in velocity_scores (module B), /accuracy/ledger + referee_wikipedia outputs (modules C/D), /monitor for cross-checks. Run it as a **scheduled read-only job in its own process/skill** (not inside the serve path — batch-pacing doctrine; not a hot engine endpoint someone can poll into an H12), monthly for the graded series (S4 frozen slot) with optional ad-hoc *unofficial* runs clearly marked non-series. Reports persist to Postgres (S3) and the work queue lands as a file for Claude Code — with the rulings-gate (R4) between queue and action.

---

## 7. PRESCRIPTIONS (consolidated, canon-tied)

| # | Prescription | Canon |
|---|---|---|
| G1 | Registered, hashed CHECK_MANIFEST; readiness computed only over it; check-set immutability per phase | Bernstein/Goodhart |
| G2 | Fixed evaluation panel drawn by frozen rule, never adapter-curated | Reinhart & Rogoff |
| G3 | Teacher≠examiner: fixes verified by the held-out ledger, never by the assessor's own re-run | Goodhart |
| G5 | Severity-weighted, worst-module-floored readiness; blended % never the sole portal gate | Bernstein |
| G6 | Denominator disclosure: run/abstained/shadow counts printed every report | Malkiel (honest denominators) |
| S1–S6 | Manifest versioning + 2-period overlap runs at every definition change + immutable archive + frozen cadence/clock + shadow-check onboarding + no backfill | Friedman & Schwartz |
| T1–T5 | Quantile (not max) reference; persistence + inter-spike patience before ENDED; RECURRENT class; module D WARN-only until it beats the monkey; D never drives stage decay | Taleb |
| N1 | Every manifest check carries a stated null hypothesis + threshold calibration note; no null, no entry | Malkiel |
| R1–R4 | Referee findings diagnose, never tune; second held-out referee grades fixes; track engine-referee correlation as a drift alarm (rising = bad); strike the alias solution; rulings-gate on the work queue | Malkiel, Kindleberger, house held-out doctrine |
| Z1 | Per-source calibrated alarms with persistence, to prevent alarm fatigue burying the one real failure | Zweig/Belsky |

**Smith, last word.** The division of labor among agents is productive exactly insofar as each specializes honestly: collectors collect, scorers score, referees stay outside, and the teacher teaches *diagnosis* — not answers to its own test. The invisible hand fails when the examiner and the examined share an incentive in the grade. Freeze the manifest, publish the splices, state the nulls, respect the tails, and wall the referee off from the curriculum — then the monthly series can, in time, settle arguments the way long consistent series always have.

*— The Economist, NowTrendIn Advisory Board*


