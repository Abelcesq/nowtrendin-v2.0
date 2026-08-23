# BOARD ROUND 7 — THE THREE PROBABILITY AGENTS, COLLATION FOR THE CHAIRMAN
### Nine seats, 2026-08-22/23. Question: incorporate probability sections into the Trend, Market
### and Crypto signal panels? COLLATION, not a blend. Disagreements preserved. No recommendation.
### Context of record: round 6 CUT the panel unanimously; the Chairman ordered this review — his
### office, working as designed. The seats judged the material, not the override.

---

## 1. THE SPLIT VERDICT — unanimous on both halves

**`probability_core.py`: APPROVED, all nine seats.** "The best-engineered statistical module this
board has reviewed" (Expansionist); "the mathematics finally deserves the product" (Executioner);
"genuinely good engineering... the t6 standard applied honestly" (Guardian). I1–I5 enforced
structurally; 41/41 with 16 tripwires reproduced independently by **seven seats**. The BSS<0 →
WITHDRAW branch is pre-committed in writing (Forecaster: "credit where due" — the round-6 omission
does not recur). The crypto agent's honest-absence-as-primary-content is "the strategy I have been
asking for, executed" (Economist) and "the single strongest App Annie artifact in the stack"
(Buyer's Desk).

**The three agents as built: NOT SERVABLE, all nine seats.** They have never executed against real
data — 12 of 12 SQL queries fail on the live schema (Executioner, verified per query) — and the
41/41 certifies a **synthetic fixture written to match the SQL**, which six seats independently
named as the pattern's costume this round.

---

## 2. THE FIVE DEFECTS THAT EACH INDEPENDENTLY PRODUCE A WRONG SERVED NUMBER
### (Statistician, all quantified through the shipped code; Challenger constructed three live)

| # | Defect | Quantified |
|---|---|---|
| 1 | **Credibility Z explodes on member-day exposure** — a topic's 365 days treated as 365 independent trials | **Z = 0.996 on 2 events** vs the round-5 cap √(2/1082)=0.043 — **23× violation**; behavior is "bimodal junk" (~0 or ~0.99 on a noise coin-flip) |
| 2 | **Resolved-only KM conditions on resolution** — the ~881 pending rows live in `pending_detections`, which the cohort query never reads; the docstring's "pending → right-censored" never executes | **F(30) = 0.242 vs 0.016 — 14.9× inflation** at live counts |
| 3 | **"Competing risks" is two independent 1−KM curves** — same row counts as an event in BOTH; the `max(0,…)` clamp hides the incoherence | **rise=1.0 + decay=1.0 = 2.0** constructed and run (Challenger AND Forecaster, independently); Aalen-Johansen is the fix |
| 4 | **Every LAGGED row is silently deleted** — LAGGED means breakout BEFORE detection, so duration<0 hits `continue`; `RISE_VERDICTS` including "LAGGED" is **dead code** | informative deletion of exactly the fast-arrival topics (5 of 15 near-misses lost by 1–2 days); compounds the −16% left-truncation bias at short horizons |
| 5 | **No delayed entry** — `kaplan_meier` takes (durations, events) only; the 14-day enrollment lag requires left truncation | **−16% relative bias at F(30)**, differential across cells → manufactures spurious separation that feeds defect 1 |

Plus: **MEASURED 0.000 served on late events** (n_events counts beyond-horizon events, defeating
I3); **MEASURED 100% on one row** (min_cohort=1, where the lone row IS the portfolio so the blend
defends nothing); the **I2 gate is a category error** (a D-measurement gate on a cohort with no D
factor, discarding 100% of usable history); the **hand-widened band served as "95% CI" has no
coverage property at any level**.

## 3. THE PAYLOAD PERIMETER LEAKS — the 2026-08-20 incident shape, one door down
### (Forecaster, ten attacks, eight fired; Buyer's Desk found A5 independently)

- **A2:** an ABSENT Reading serves `raw_rate=0.42, base_rate=0.87` — only `value/ci/credibility`
  are guarded; the side fields are not.
- **A5:** the crypto `money_leg_available=True` + `conditioned_on: [cftc_cot_positioning]` flip on
  the constructor flag alone while the legs read ABSENT/NOT_APPLICABLE and **COT never enters any
  cohort key** — two fields in one payload disagreeing, verbatim the incident class.
- **A10:** `money_leg_sources` lists Finviz/FINRA/OFR/FMP when nothing contributed (§17).
- **The named next costume (three seats independently): error-to-ABSENT laundering.** Every fetch
  is `except: return []`, so the broken SQL serves "no comparable history for this cohort" — a
  fabricated reason on an instrument fault. On deploy day the schema mismatch would have served
  ABSENT everywhere **and nobody would have known it was an outage** (Operator). Requires an
  INSTRUMENT_ERROR state distinct from ABSENT.
- **`plain_english()` narrates the wrong denominator** (Guardian, Operator, Buyer's Desk,
  Statistician — four seats): "Of N items that matched this profile, X% moved" where X is the
  BLENDED value, mostly portfolio rate at any realistic Z. The reference class must be the subject
  AND the number's provenance disclosed: raw_rate for the cohort, blend labeled as blend.

## 4. FINDINGS UNIQUE TO ONE SEAT

- **Operator — the payload gives the archive away**: `cohort_key + n + events + raw_rate +
  base_rate` swept over topics reconstructs the ledger — the moat — violating the Chairman's own
  method-confidential collation ruling (`c6670f7`). Withhold raw/base/cohort_key from
  non-Enterprise surfaces. **And the common-mode self-certifies**: Apify budget → resolution
  timing → KM censoring → every served probability, and the calibration log then grades shifted
  forecasts against the same shifted outcomes and shows green.
- **Expansionist — fabricated RELEVANCE**: a Frankfurt sector gets a correctly-measured **US**
  regime stamped as universal, and `insider NONE` ("we looked") where the truth is "we cannot look"
  (Form-4 is US-only). Jurisdiction must be a cohort dimension. Also: `MAX(platform_tier)` routes
  D/M by **string collation** ('niche' > 'mainstream' alphabetically). And every payload sentence
  is assembled English — a forced wire migration at the first non-English contract; `reason_code`
  enum + keyed strings before first serve.
- **Economist — `distinct_buyers` isn't**: `SUM(CASE…)` counts accumulation FILINGS; one insider
  filing three Form-4s reads as BROAD. Seyhun's is a distinct-persons result. Also: with breakout
  base rate a degenerate 100% (enrollment conditions on eventual attention), P(RISE|enrolled) is
  largely a WHEN, not a WHETHER — "closer to a coverage-latency curve"; serve it as that. R7
  carried correctly. **Instrument freeze prescribed**: no fourth probability instrument until one
  LED is referee-corroborated or the calibration log holds n≥60.
- **Buyer's Desk — the line that converts measurement into a signal product** is description and
  tailoring, not the numbers: "P(this coin moves 8%)" is an unregistered adviser's sentence;
  "the frequency at which signals like this one graded CONFIRMED under our published rule" is a
  measurement company's — and the code currently renders closer to the first. STRIKE internal
  ruling citations (R7/D1/D2) from customer payloads; rename `inflow_move`→`price_up`; add
  `param_version` to every Reading. **The "Crypto Money Gradient" name over a no-money-leg
  admission is a plaintiff's slide — rename the surface or wire COT, not neither indefinitely.**
- **Challenger — corroboration is the disabled defect's third home, WEAKER**: raw
  `COUNT(DISTINCT source_name)` — no collapse at all, so one wire story = forty voices in every
  locale; and after the 30-day prune it returns 0 → banded "1" — cohort membership becomes a
  function of the prune horizon.
- **Forecaster — his own round-6 predictions were VOID**: never registered, per the register's own
  7-day census rule; "the file drawer has eaten its own contents." New predictions PA-1…PD sealed
  in-ruling with the self-imposed condition they enter `FORECAST_REGISTER.md` or are void. Notable:
  **PC = 0.40** that the corroboration factor is §15a-conformant before any trend cohort renders;
  **PD = 0.25** that panels render BEFORE the round-4/5/6 fixes deploy (the dishonest order).

## 5. WHAT COULD BE SERVED HONESTLY TODAY (Statistician, the constructive answer)

1. The portfolio resolved-race frequency with its exact interval — **15/61 = 24.6%, Wilson
   [15.5%, 36.7%]** — labeled "of races that resolved," restating the ledger report, never
   re-deriving a different number.
2. One pooled left-truncated KM over resolved ∪ pending (entry = `enrolled_at`, LAGGED counted
   and disclosed) — a time-from-enrollment-to-arrival curve, portfolio level only.
3. Honest-absence blocks for every cohort cell — √(15/1082) = **0.118**: no split is credible,
   with that arithmetic stated as the reason.
4. The disclaimers. Nothing else is computable correctly yet.

## 6. THE CONVERGENT CONDITIONS (where ≥5 seats independently agree)

1. **Commit the untracked folder; deploy rounds 4/5/6 first.** The agents jump nothing; the 4c
   defect is still live on the wire while this round reviews new construction.
2. **Single-source the corroboration quantity** — the agents read the *stamp*
   (`corroboration_at_enroll`, re-enabled per its three frozen conditions), never a recomputation;
   equality regression against `dual_pathway.mainstream_breadth`; a wire-duplication fixture that
   FAILS on the current SQL.
3. **Seal the calibration log BEFORE its first row** (Forecaster's prereg §2 is the draft): F_port
   sealed per row at serve time; BSS_port as the decision-binding number; withdrawal at BSS_port<0,
   n≥50, two consecutive quarterly scorings; server-writes-at-serve-time; a completeness audit that
   disables the section if served≠logged.
4. **Statistical rebuild before any cohort number**: delayed-entry Aalen-Johansen over
   resolved∪pending; Z-cap √(events/1082) in code with a tripwire; horizon-capped n_events;
   the band never labeled "95% CI".
5. **INSTRUMENT_ERROR ≠ ABSENT**; fix `plain_english`'s denominator; guard the payload side
   channels (A2/A5/A10); DDL-derived fixtures replacing the hand-written schema.
6. **Shadow mode to n≥60 logged resolutions** before any user-facing render (Operator: converts an
   unpriceable withdrawal into a free one). The trend panel will honestly read ABSENT for months —
   **ship that state as-is or do not ship** (Buyer's Desk, Economist, Statistician).
7. **Redact the reconstruction kit** on non-Enterprise surfaces (Operator).

## 7. WHAT THE OVERRIDE IS OWED (Operator, endorsed unopposed)

Conditions in writing once — the list above; pre-committed numeric tripwires; the disclosure line
fixed in advance; full execution with no slow-walking once conditions are met; and a dated record
that CUT was the advice and override the ruling. **The Buyer's Desk sentence that precedes any
probability shown to any counterparty:**

> "The figure below is the historical frequency with which signals in this cohort resolved under
> our published grading rule — a description of our own ledger, not a forecast for this instrument
> — and that ledger's current-engine early-detection rate is 9.4% on 61 resolved races with zero
> of our early-detection wins yet corroborated by an independent referee."

## 8. THE ARITHMETIC, UNCHANGED BY 2,688 LINES

62 races (one added in-window, zero new LED) · 15 LED · 0 referee-corroborated · v2 engine 9.4%
[3.2, 24.2] · tailCapture 0-of-13 · ~4.5 resolutions/month · `citable: false` on the wire.
No line of code adds an event. The Executioner's item 7 — PIT covariate stamping, forward-only —
is "the probability project's real first commit, and the clock starts only when it lands."
