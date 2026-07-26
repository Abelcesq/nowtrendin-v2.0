# MASTER REMEDIATION PLAN — Market Signal + Crypto accuracy, and the money-movement model
**Date:** 2026-07-25 · **Six archetypes, independent, full-record read (session logs, MDs, board record, code, live engine v286)**
**Chairman's charge:** what updates must take place so Market Signal + Crypto data is ACCURATE,
how accuracy is ASSURED, and the MODEL that identifies money-movement signals.
**Context re-anchored:** the Chairman's money-markets mechanism brief (order splitting/dark
pools · options flow/delta hedging · political information asymmetry · cluster buying ·
open-market vs grants · Seyhun/Harris/Lewis canon · the Pellegrini ruling) was placed in every
archetype's pack verbatim. All six confirm the standing translation: **mandatory disclosure is
the detection floor and ceiling; the honest instrument is disclosure-to-participation latency;
"before mainstream" = before the slow tail reads the filing; the scarce good is filtering and
timing, not access.**

This is the plan the freeze thaws into. Nothing below is new design; every item is §10a-verified
inventory, ordered.

---

## PART A — MARKET SIGNAL ACCURACY INVENTORY (Challenger; each item verified against v286)

| # | Defect | Status | Acceptance criterion |
|---|---|---|---|
| **A1** | Primary insider source dead on the live path (doubled-ticker parser; `insider_signal` returns 0 rows for every ticker) | **Fixed in code, OFF in prod** (`INSIDER_PARSER_FIX=0`) | Post-flip: rows>0 for any ticker with a known Form 4; Insider Tracking coverage rises above 17/300 with Finviz provenance |
| **A2** | Form-144-as-sale | Fixed in code (exact-match classifier, ungated — correct on both branches); largely inert live because A1 starves the path | Contamination statement carries machine-readable date bounds; no row deleted |
| **A3** | `market_momentum` floor-bound 15/16 — **root cause verified: 12-month aggregates re-read every 6h** have near-zero per-cycle dispersion; the 0.05 floor manufactures the z. **Data defect, not estimator** (median/MAD retraction stands — MAD of a near-constant series floors MORE) | Unbuilt; diagnosis-first (raw-series dump) | Floor-binding <20% OR component serves absent/degenerate wherever raw dispersion ~0; no floor-denominator z wearing the measured badge |
| **A3b** | **NEW:** `market_momentum` is direction-blind — `abs(price_return_12m)` at `market_signal_engine.py:552`: a −50% crash scores identically to a +50% rally under "price/valuation trend". Same family as the 6/6-rejected directionless blend | Needs ruling (signed vs magnitude) | Definition states signed-or-magnitude explicitly; UI label matches |
| **A4** | Coverage: money component unmeasured on ~94% of universe (17/300 scored, AV fallback capped 25/day); absence and failure share a code path | A1 flip + the source-liveness contract (Part C) | Each source declares a coverage floor; alarm fires when scored coverage < floor for N cycles; today's 17/300 would trip it |
| **A5** | Market ledger validates the congress feed, not the Market Signal (all 10 live directional flows track congress net exactly; S1 says congress net is legitimate *as a congress claim* — the defect is it's the ledger's ONLY claim) | Needs re-target to the Form-4 observable (A1 + INSIDER_FLOW + salt) | Every enrollment records its driving source; confirm-rate split by source published; congress-only rows labelled a congress-feed record |
| **A6** | Ledger measurement defects: CONFIRMED-only median lead (survivorship, `:538`) · 60d vs 365d incomparability, no KM ported · **no null control** (±5%/60d on a mega-cap is near-certain) · `_regime_adjusted` drops NO_MOVE rows (gated off, but the internal read stays biased) · `lead_time_days` is time-to-our-own-move | Unbuilt, mostly trivial | Median over all resolved rows w/ per-verdict split; KM+Greenwood or explicit incomparability note; confirm-rate never published without the matched null beside it; UI says "days to ±5% close", never "before mainstream" |
| **A7** | **NEW, same defect class as the flag the review just fixed:** `DARK_POS_WEIGHT` code default is **0.4** (`market_signal_engine.py:91`); the Board-ruled 0 exists only as an unversioned config var — a fresh environment silently restores the rejected blend | One-line default flip | `grep` shows default "0"; fresh-dyno behaviour equals production intent |
| **A8** | R7 transient (self-resolving; listed so nobody re-diagnoses it) | Wait | Clean O8 re-run: G1<2%, G3 near-Gaussian |
| **A9** | **Spot-check flag:** SpaceX (SPCX) serves `flow: inflow` from congress buys 3/0 — Quiver ticker-mapping check before trusting any enrollment from it | Unverified mapping | Mapping audit note |

**Operational definition of "accurate" (Challenger):** (1) every served number computed from data
that exists for that instrument — no floor-fabricated z, no directionless quantity under a
directional label, absence served as absence; (2) every contributing source demonstrably alive
with a declared coverage floor and an alarm — never a human running gate 5 by hand; (3) every
published figure survives an adversary — stated window, stated denominator, per-verdict leads,
matched null beside it, enrollment source disclosed.

**Most likely to embarrass if unfixed:** A5+A6 jointly — `/market/accuracy` in a data room. *"A
buyer's analyst needs one afternoon to find that the 'Market Signal track record' is a
QuiverQuant congress-feed record on mega-caps, with survivorship in the median lead, no null
control, and a 60-day window dressed beside a 365-day one."*

## PART B — CRYPTO (Guardian; two corrections to the record, one NEW live breach)

**Correction 1:** it is **10 of 12** coins with COIN as sole proxy (code-verified), not 8.
**Correction 2 / NEW LIVE BREACH (C2b):** the crypto ledger is **already enrolling on the
suppressed direction** — `record_from_serve` gates on `dark_matter.flow` + intensity≥40 and
ignores `money_data_absent`. Live `/crypto/accuracy`: **1 CONFIRMED (inflow, lead 18d) + 1
pending** — falsifiable informed-money claims enrolled off a single AV-fallback proxy vote while
the serve payload says the money read is absent. Fix: skip absent/thin coins at enrollment;
**annotate** (never delete) the two existing rows `basis: single_proxy_av_fallback_dead_parser_era`
(the v233 restore-and-annotate precedent).

**The BTC contradiction, mechanism traced exactly:** dead parser → AV fallback → ONE proxy of
five votes → intensity = 100×(0.5+0.5×0.2) = **60.0 exactly**. Fix in `compute_crypto_signal`
(the single choke point all three platforms inherit): when `money_data_absent`, serve
`flow: "no_data"` and **omit the `dark_matter` block entirely** (§17).

**The pre-flip gate, specified:** absence becomes coverage-keyed IN ADDITION to degeneracy —
`money_data_absent = True` when `proxy_coverage == "thin"` **or `proxies_covered < 2`** (BTC
serves "partial" today with covered==1, so the label alone is insufficient), with a served
`absence_reason` field distinguishing `proxy_coverage_thin` from `degenerate_baseline` — two
different truths a diligence reader must be able to tell apart. **Acceptance:** all ten COIN-only
coins show `absence_reason: proxy_coverage_thin` on live `/crypto` BEFORE `INSIDER_PARSER_FIX=1`
is set; a local run with the flag on asserts they STAY null.

**What crypto may honestly say at 2-of-12:** header sentence *"Money-movement measurement is
currently available for BTC and ETH only"* (once CFTC COT passes the §16 five gates, CALIBRATING
first, `[cold-start-stated]`); the other ten: `absent`, no flow, no dark_matter block,
composite_note "the money read is absent, not zero"; market_confirmation continues everywhere
(price is real); **no cross-coin MM ranking among COIN-only coins, ever**; no ledger rate while
`small_sample`; episode collapse keyed on the underlying proxy event (one Coinbase event ≠ ten
trials).

**Integrity checklist carried forward (owners):** R1 payoff firewall (monitor, weekly read) ·
R2 + acknowledged-exception review — the `(financial_risk_gradient, market_accuracy_ledger)`
exception must STAY write-only; a read there is circular and revokes it · MNPI/cohort-only; salt
before INSIDER_FLOW · no-forward-dates (datecanon future-date assertion) · language purge (F6
list + "never publish '$X moved' — publish the date") · ledgers never deleted (annotation is the
only remedy).

## PART C — ACCURACY ASSURANCE (Outsider; five controls, ~4.5 engineer-days, no new agent processes)

1. **Source-liveness contract (~1.5d):** per-source `{universe_size, min_universe_hit_rate,
   min_rows_per_cycle}` beside `COLLECTOR_EXPECTATIONS`. **RED = zero/below-floor usable rows
   across the WHOLE universe** (per-item absence stays legitimate) and the misattribution
   variant (rows return but don't match known tickers — the doubled-letter signature).
   Lives INSIDE Source Watchdog — not agent #10. **Acceptance: replay the actual corpse** — a
   captured legacy parse must go RED in one cycle; a normal cycle GREEN.
2. **Gate-5 recurring (~1d):** 3 real rows/source/cycle, field-level (gate_date, ticker grammar,
   numeric parses, UNKNOWN-rate threshold, `_TS_LIKE` misalignment). Archive the samples — that
   is what makes every FUTURE contamination window boundable.
3. **Contamination statement (~0.5d):** honest content specified — the defect precisely; the
   window bounded as *"worst case = the source's entire life as primary insider input,
   2026-06-25 → 2026-07-25 (~30 days); it cannot be bounded tighter (no raw HTML snapshots were
   retained) and we do not pretend otherwise"*; affected numbers by shape (absence-shaped vs
   wrong-value-shaped); ledger rows annotated, never deleted.
4. **Contradiction guard (~0.5d):** payload-build-time, in the ENGINE (three UIs, one engine):
   all-feeding-components-absent ⇒ direction/flow/intensity null. Plus one monitor line
   (zero-count scan).
5. **Data-room definition + citability order (~1d):** accurate = liveness + fidelity +
   consistency + validation, each with an artifact. **Citability order:** (1) the control
   numbers themselves → (2) price-derived market-confirmation components → (3) the market
   ledger's POST-FIX cohort (pre-fix rows annotated, reported separately) → (4) Insider Tracking
   after 14 green cycles + R7-pattern capture → (5) crypto money_movement last. **One labelled
   headline rate per ledger, never moved without a signed re-registration; crypto gets NO
   headline rate until a pre-declared n=30 resolved post-fix.**

## PART D — THE MODEL, SPECIFIED (Economist; each element verified in v286 code)

**TRIGGER** — mandatory disclosure at the FILING instant (`disclosure_ts`; `insider_flow` built,
OFF; refuses identity storage without salt). **OBSERVABLE** — signed, normalized insider buying
breadth vs the name's own base rate (*least-finished element — flagged so the summary cannot
overstate again*: the enroll threshold must be IN `flow_prereg` before row 1, not in prose).
**CLOCK** — abnormal share volume vs the baseline frozen at enrollment (lock now real and
regression-tested; `ARRIVAL_VOL_MULT` pending the target ruling; the FMP-consolidated check
already passed). **LEAD** — days from disclosure to participation expansion; echoes ≤3 sessions
carved out; *pre-registered falsifier: if >50% of treated arrivals are echoes, the instrument is
a reading service and we say so.* **PROOF** — KM + Greenwood, treated vs matched control, one
primary horizon, cohort-scoped, refusals counted.

**The pre-registration, as it should lock:**
- Multiple **3.0–3.5×**, read mechanically off the CORRECTED curve (required n = 4(1−p₀)/(p₀(RR−1)²), decreasing in p₀ — the 5–8% target was the wrong direction)
- **PRIMARY analysis: stratified log-rank on time-to-arrival** (match_group strata, full 180d window) — uses the whole curve, cuts n by ⅓–½; disjoint-Greenwood-bands demoted to the conservative *publication* gate
- **Reporting horizon 90d** — justified against the 9–14-day finding: that median is the NULL's behaviour (noise arrives early); the treated tail is weeks-to-months per the Seyhun-descended literature; 60d saves almost no null (24.1→29.8%)
- **min_episodes = 120** resolved treated (power table written into `doc_path`)
- **Stop rule: one analysis at min_episodes** — quarterly descriptive reads permitted, stamped "no verdict yet"
- **Control match key upgraded:** `(sector, size_decile, ADV_decile, pretrend_bucket)` where pretrend = last-20-sessions mean ÷ full-window median, computed only inside the frozen window, buckets {<0.9 · 0.9–1.15 · >1.15}, ±0.25 caliper, achieved distance stored — *controls must be trending the way the treated name was trending before the filing*, or "separation" measures volume momentum
- **Final calibration run first**, with all four Challenger corrections: `already_arrived_before` applied to the null · events/yr = −ln(1−p)×365/60 (corrected, 2.5× = 2.24/yr — inside the Challenger's own band) · frozen universe with SHA · ticker-clustered bootstrap intervals on every cell

**Open live-surface item, ordered into the pre-enrollment batch:** the naked KM on Ledger.tsx
(3.5%, no band) — wire `ledger_survival.kaplan_meier` into `survival_confirmation`, serve
lo/hi/n. *"No rate leaves this building without n and an interval."*

**"Predict," said defensibly (adopt verbatim):**
> *"We do not predict prices. We measure — against matched controls and a pre-registered,
> never-deleted record — which mandatory disclosures have historically been followed by expanded
> market participation, and how many days of warning that expansion gave, published as a
> lead-time distribution with its confidence interval and its failure rate."*

## PART E — UNIVERSE BREADTH & THE CALENDAR (Expansionist; the binding constraint)

Accrual math (assumptions stated; 48h of hourly idempotent ingest replaces the guesses with
counts): market-wide ingestion yields **~1.5–5 treated enrollments/trading day, central 3**.
Against the power table:

| Effect | n/arm | Central | With log-rank primary |
|---|---|---|---|
| 20pp | 110 | Dec 2026 | **Oct–Nov 2026** |
| 15pp | 200 | Feb–Mar 2027 | ~Jan 2027 |
| 10pp | 430 | May–Jun 2027 | ~Mar–Apr 2027 |

16 names = a decade; market-wide = one quarter of enrollment + one of resolution. **Every week
the flags stay off moves these dates one-for-one.**

**Cheaper-now-than-later (only these, everything else stays frozen):** nullable `plan_10b51`
column on `insider_events` before accrual · actor-identity join rule (hash CIK when known,
name fallback; nullable `cik` on `actor_reference`) · **salt write-once, in the ops doc** —
rotating it fractures identities across a never-deleted ledger. EDGAR = completeness lane, slots
AFTER accrual starts (reconciliation → 10b5-1 backfill → history). Crypto expansion = COT
(BTC/ETH register, 52 obs/coin-yr — a series worth persisting, not a power-bearing cohort);
coverage of 2 beats fabrication of 12.

## PART F — THE RUNBOOK (Executioner; verified: the enrollment wiring DOES NOT EXIST — zero refs to flow modules in the detector; it is the one construction the freeze permits, because enrollment IS the objective)

0. **Captures** (today) → `audits/board/preflip/`
1. **Crypto coverage-gate + contradiction guard** (one deploy; keeps honest absence true post-flip) — *includes the C2b ledger-enrollment skip + annotation of the 2 contaminated rows, and the A7 `DARK_POS_WEIGHT` default flip*
2. **Contamination statement** ($0, no code)
3. **`INSIDER_PARSER_FIX=1`** — after Step 1 verified live one full cycle AND R7 transient decayed (re-read `/risk/scores`; wait if |z|>1.5). 72h capture. Rollback = unset. **[Chairman GO]**
4. **serve_payload regeneration** (the cache gotcha) + verification
5. **`ACTOR_ID_SALT` (write-once, secret store, never git) → `INSIDER_FLOW=1`** — hard order **[Chairman ruling: salt]**
6. **THE WIRING** (~150 lines in the detector): `_collect_phase` tail behind `FLOW_ENROLL` — ingest → cluster-qualify → enroll(treated+3 controls) → sweep, §13-paced; endpoints `GET /flow/status`, `GET /flow/accuracy`, `POST /flow/prereg`. Deploy with `FLOW_ENROLL=0` (zero blast radius)
7. **Prereg lock** — needs the **arrival-target ruling** (the only calendar dependency on the Chairman; Board recommends 3.0–3.5×). The code enforces nothing-enrolls-before-this.
8. **`FLOW_ENROLL=1`** → success = `flow_integrity` green with **`pending_treated ≥ 1, pending_control ≥ 3`** — the number the freeze thaws on
9. **market_momentum raw-series dump** (read-only, parallel) — diagnosis BEFORE any fix
10. **O8 re-run** on ≥14 days of repaired data (~Aug 8–12)
11. **Source-liveness monitor** (post-thaw construction)

**Calendar:** Steps 0–2 Jul 25 · flip Jul 26–27 · salt/flow + wiring Jul 28–29 · prereg + enroll
Jul 30 · first row ~Aug 1–8 · interim censored KM honest from ~Sep 1 · **first cohort completes
late October 2026.** *"That tail is irreducible and correct: the big money is in the waiting."*

**CUT list (frozen by decision, named):** MACRO_PERSIST · MARKET_REGIME_ADJ_INTERNAL ·
DARK_POS_WEIGHT restoration · UOA/options flow · dark-pool/volume-profile/liquidity-sweep
detectors · crypto proxy-map expansion · on-chain · D8 stage-3 · median/MAD (retracted) · any
market_momentum fix before the Step-9 diagnosis · new congress modeling · the panel name
(Chairman's, blocks nothing).

## DISAGREEMENTS (two, preserved)

1. **Source-liveness timing.** Challenger orders it #2 and the Outsider calls it "the highest-ROI
   item in the backlog"; the **Executioner sequences it AFTER enrollment (Step 11)** — "it is
   construction, and the freeze thaws when the register enrolls." Chairman's call: safety-first
   vs clock-first. (Middle path: the ~1.5-day control could ship inside the Step-1 deploy window
   without moving the flip date.)
2. **Ingest cadence.** Expansionist wants **hourly** ingestion (the 200-row newest-first cap vs
   the 4–10pm ET filing burst; 24 pulls/day ≈ 4,800-row capacity, watermark tells us in 48h);
   the Executioner wired it to the 6h collect cycle. Cheap to resolve empirically via the
   truncation watermark.

## RULINGS REQUESTED (everything else proceeds without you)

| # | Ruling | Board recommendation |
|---|---|---|
| R-a | **Arrival target** (gates the prereg lock — the only calendar dependency) | **3.0–3.5×**, read off the corrected curve |
| R-b | Parser flip GO (post Step-1 verification + transient decay) | GO |
| R-c | `ACTOR_ID_SALT` authorization (write-once) | Set before INSIDER_FLOW |
| R-d | Contamination statement approval (honest unbounded-onset wording) | Approve |
| R-e | A3b: market_momentum signed vs magnitude | Decide at Step-9 diagnosis |
| R-f | Panel name (blocks nothing) | Letter-free candidates stand |

---
*Collation of six independent memos; disagreements preserved; nothing executed without the
Chairman's rulings above.*
