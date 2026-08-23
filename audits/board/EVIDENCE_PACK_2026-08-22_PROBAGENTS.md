# EVIDENCE PACK — THE THREE PROBABILITY AGENTS + INCORPORATION INTO THE SIGNAL PANELS
### Chairman-commissioned 2026-08-22. Nine seats.

## 0. THE GOVERNANCE FACT THIS PACK MUST LEAD WITH

**Round 6, yesterday, nine seats, unanimous: CUT the Base Rate Panel.** Reasons of record:
portfolio Z ≈ 0.24 on ~61 events; the 4-factor design at Z ≈ 0.014–0.03; v1 is climatology at
~95% weight; `tailCapture` reads 0-of-13 LED on top-decile surges; the current engine reads 9.4%
[3.2, 24.2] against a 50% null.

**The Chairman has now ordered:** review the three probability agents in `Probability Py folder/`
and assess **incorporating probability sections into the signal panels** for Trends, Market and
Crypto. Under the board's own mechanics the Chairman rules; the CUT was advice. The seats' job is
NOT to re-litigate whether they were right — it is to judge THIS material, state whether it
answers the objections that drove the CUT, and if the panel proceeds anyway, state the conditions
that make it least dishonest.

## 1. WHAT EXISTS (read the files; do not take this summary)

`Probability Py folder/`: `probability_core.py` (shared KM + Greenwood log-log, Bühlmann-Straub,
Murphy decomposition, tri-state `Measured`, `Reading` with structural invariants) ·
`trend_probability_agent.py` (P(RISE)/P(DECAY) as **competing risks**, cohort = maturity ×
corroboration × provenance) · `market_flow_probability_agent.py` (P(±5%/60d) conditioned on
insider-buying breadth × short-interest band × macro regime; **R7 exclusions declared in the
payload**) · `crypto_flow_probability_agent.py` (P(±8%/45d) attention-conditioned; **money leg
NOT_APPLICABLE by construction**, CFTC COT pre-wired and OFF behind §16) ·
`test_probability_agents.py` (**41/41, 16 tripwires — I ran it**).

**These answer, in code, most of what the board said in rounds 5–6:**
- I1: a non-MEASURED Reading structurally cannot carry a number (constructor raises).
- I2: tri-state `YES/BLIND/UNKNOWN`; UNKNOWN rows excluded AND counted (`excluded_unmeasured`).
- I3: zero events → ABSENT, never 0%. I4: KM, never drop/never code-pending-as-0.
- I5: credibility, no suppression threshold; negative VHM floored and reported `degenerate`.
- `NOT_APPLICABLE` vs `ABSENT` distinguished (the crypto D1 defect). R7 never enters a cohort key
  (tripwire-enforced). Macro outage degrades to UNKNOWN, never fabricates a regime. COT
  knowable_at = Friday publication, refused otherwise. BSS served binning-independent.
- Every enforcer has a tripwire shown to FAIL — the t6 standard, applied throughout, including a
  tripwire on the write-scanner itself.

## 2. WHAT IS BROKEN OR UNTESTED (verified by me, today)

1. **THE SQL TARGETS A SCHEMA THAT DOES NOT EXIST.** `accuracy_ledger_enhanced` is the MODULE;
   the table is `accuracy_ledger`. `raw_signals` has NO `topic_key` and NO `signal_date` column
   (join is via `topic_signals`; time is `collected_at`). `market_positioning`,
   `crypto_signal_state`, `base_rate_calibration_log` have no CREATE anywhere. `topic_lifecycle`
   has no `first_seen` per the live schema. The ledger has no `direction`/`move_date`/
   `rates_regime` columns of these names. **The 41/41 pass is against a synthetic fixture whose
   schema matches the SQL. These agents have never executed against real data.** (The class
   attributes say "override to match the live schema" — the override does not exist yet.)
2. **The calibration loop reads a table nobody writes.** `base_rate_calibration_log` is the
   accountability mechanism and it has no writer. Note the design intends the SERVED probability
   to be logged and later graded — building that writer is itself a new forward-only store.
3. **The trend cohort factor `corroboration` inherits the round-6 finding**: computed as raw
   `COUNT(DISTINCT source_name)` with no tier filter and no `_title_sig` — the same not-the-§15a
   quantity that was disabled at the enrollment stamp yesterday. Same defect, new home.
4. **`d_measured` gating reads a ledger column named `d_measured` — the live column is
   `d_measured_at_enroll`**, is four days old, and is NULL on all 61 resolved races. Under I2 the
   agent will therefore exclude **the entire resolved set** as UNKNOWN and read ABSENT everywhere
   — which is honest, and means the trend agent serves nothing for months.
5. **Round 6 arithmetic is unchanged**: 61 races, 15 LED, 0 referee-corroborated, v2 engine 9.4%,
   tailCapture 0/13, ~4.5 resolved/month. Nothing here adds an event.
6. Deploy state: the round-4/5/6 fixes remain undeployed; the 4c defect is live on the wire.

## 3. WHAT THE BOARD IS ASKED

1. **Does this material answer the objections that drove yesterday's CUT?** Which specifically
   survive (credibility arithmetic? tail capture? the climatology-at-95% point?) and which are
   now moot (I1–I5, NOT_APPLICABLE crypto, R7 exclusion)?
2. **The incorporation question as ordered:** probability sections in the Trend, Market and
   Crypto signal panels. Rule on placement, wording, and preconditions — per-item rendering was
   the Guardian's REJECT in round 5 ("the reference class must be the subject of the sentence").
3. **The schema adaptation** (§2.1): who verifies the rewritten SQL is the §15a/live-schema
   quantity — what is the regression test that stops the corroboration drift recurring a third
   time?
4. **The calibration log**: forward-only, becomes real only when served numbers are logged. Does
   it need a seal (climatology reference, bins, withdrawal rule) BEFORE the first row, per the
   round-5 Forecaster P5/P7 conditions?
5. **Sequencing against the standing open set** (4c completion + deploy, resolution_mode, CI,
   register teeth). What may the agents jump, and what may they not?
6. **The crypto agent ships honest absence as its PRIMARY content** (money leg NOT_APPLICABLE,
   ledger_warning in-payload). Is that a product, per the Buyer's Desk's "honest measurement
   describing itself"?
7. **What is the pattern's next costume in THIS material?** (Candidates I can see: the fixture
   schema diverging from live; the calibration log with no writer; `min_cohort=1`.)

**Standing constraints:** held-out (no writes — tripwire-enforced), measurement not advice,
honest absence, §15a A3, score-affecting = backtest + board note, the Chairman rules.
