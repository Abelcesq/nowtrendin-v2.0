# D8 — Degenerate-Component Score-Side Exclusion: Held-Out Backtest (2026-07-19)

**Held-out, read-only research** (founder-ordered; board decision-table item D8 in
`audits/board/BOARD_estimator-fdm-snapshot2_2026-07-19.md`; proposal pinned in
`audits/ledger-research/POSITIONING_FLOORPIN_RESEARCH_2026-07-19.md`). No code, score, ledger,
or git change follows from this note. Sources: read-only code trace of
`transfer/market_signal_engine.py`, `transfer/crypto_money_gradient.py`,
`transfer/financial_risk_gradient.py` (enrollment site, lines ~2587–2606),
`transfer/market_accuracy_ledger.py`, `transfer/crypto_accuracy_ledger.py`; live pulls
2026-07-19 (engine `nowtrendin-v2-engine`): `GET /risk/scores?limit=300` (300/300),
`GET /market/accuracy`, `GET /market/accuracy/detail`, `GET /crypto`, `GET /crypto/accuracy`,
`GET /crypto/accuracy/detail`. No SQL, no paid pulls. This file is the only artifact written.
The ledgers are HELD-OUT — this note measures them; nothing here changes them.

**D8 as gated:** additionally EXCLUDE degenerate z=0.0 pinned components (zero-variance
baselines under the 0.05 stdev floor) from the Money Movement weighted score, renormalizing
over the remaining live components — the score-affecting half that POSITIONING_FLOORPIN
un-bundled from the display-only D7 quartet. Backtest question: had D8 been live, which
market/crypto-ledger detections would not have fired, and how would the
CONFIRMED / NOT_CONFIRMED / NO_MOVE rates have moved?

---

## 1. Structural finding first: ledger enrollment is DECOUPLED from money_movement

This is the decisive fact of the backtest, and it is code-level, not statistical:

- **Equity ledger.** `financial_risk_gradient.py` (~2596–2604) calls
  `market_accuracy_ledger.record_market_detection(ticker, name, date, _dpi2.get("flow"),
  _dpi2.get("movement_intensity"), detection_score=mkt.get("detection"))`. The gates inside
  `record_market_detection` are: `flow in ("inflow","outflow")` and
  `movement_intensity ≥ MIN_INTENSITY (0.25)` — both from `positioning_intel.signal_for`
  (`dark_positioning_intel`), i.e. **actual filings evidence, baseline-independent**.
  `detection_score` (= `money_movement` under MARKET_SIGNAL_V2 aliasing) is stored as
  **context only**; no threshold anywhere reads it.
- **Crypto ledger.** The live recording path is `crypto_accuracy_ledger.record_from_serve`
  (called from `gravitational_anomaly_detector.py` ~5317/~7124), which gates on
  `dark_matter.flow` directional + `dark_matter.intensity ≥ CRYPTO_MIN_MM (40)` — the
  baseline-independent proxy intensity — and passes `gate=False` so the `money_movement`
  floor in `record_crypto_detection` is bypassed; `money_movement` is stored as context.
  (Verified in the data: the one resolved BTC row stores `money_movement 19.7` < 40.)
- **Verdicts** depend only on the stored flow + realized price closes
  (`_evaluate`: first ±threshold crossing decides; timeout → NO_MOVE). money_movement is
  never an input.

**Therefore D8 cannot retroactively or prospectively change a single ledger enrollment or
verdict** unless the enrollment gate itself is rewired (which is not what D8 proposes). The
backtest below confirms this empirically row by row, but the mechanism already forces the
answer: Δ(fired) = 0, Δ(rates) = 0, on both ledgers.

---

## 2. Method

### 2a. Degenerate signature (per the pinned research, applied to served payloads)

On each instrument's `market_gradient.components`, per Money-Movement component
(Insider Tracking w=0.55 · Analyst Signal w=0.30 · Signal Freshness w=0.15):

- **absent** — `score == 0.0`, `z == null`, `baseline_relative == false` (quarantine-excluded;
  already OUT of the score; SCORE_QUARANTINE_ENABLED is live).
- **degenerate** — `z == 0.0` exactly (zero-variance baseline under the 0.05 stdev floor;
  the D8 target class).
- **measured** — anything else. (**n/a** — lane-driven `not_applicable`.)

**Simulation:** recompute `money_movement` as the renormalized weighted sum over MEASURED
components only (D8 semantics = quarantine semantics extended to the degenerate class). If no
component survives, `money_movement → None` (the component set is empty — same serialization
class as the macro-theme n/a). Sanity check: reconstructing the SERVED mm by renormalizing
over non-absent components reproduced the served value on **300/300** rows (±0.1) — the
arithmetic model of the engine is exact.

### 2b. At-detection state (honest measurability accounting)

- **At-detection headline mm IS served**: the ledger's stored `detection_score` is
  `mkt.get("detection")` = money_movement at detection time. So the degenerate-pin headline
  signature (mm == 30.0 exactly) is testable **at detection** for all 12 resolved rows —
  no approximation needed for the headline.
- **At-detection component-level state is NOT served** by any endpoint (no component-history
  route). Component-level classification is approximated from CURRENT (2026-07-19) state for
  12/12 resolved rows, and §4c shows why that back-projection over-tags.
- **Pending rows are uninspectable**: 6 market + 1 crypto pending detections exist
  (`/market/accuracy`, `/crypto/accuracy` counts) but no served route exposes pending-row
  detail. Counted honestly as not-inspected; they are not in any denominator below.

---

## 3. What D8 would do to the SCORE surface (context for the ledger read)

Live universe, `/risk/scores` n=300 (2026-07-19):

| Effect of excluding degenerate MM components | Count |
|---|---|
| mm == 30.0 exactly today (the pin cohort; was ~173 on the earlier 07-19 snapshot — it breathes with freshness state) | **189** |
| mm → **None** (every MM component absent or degenerate — the D ring is annihilated, not moved) | **188** (all `halted_microcap`, all `data_coverage: insufficient`, all `flow: neutral`, all tier ROUTINE) |
| mm moves >0.15 but survives | 110 |
| tier changes among survivors | **95 — every one ROUTINE→DORMANT, every one flow-neutral** (freshness-only renorm, mm ~24.4→13.2) |
| Component class matrix | Insider: 281 absent · 16 degenerate · 1 measured (nvidia) · 2 n/a — Analyst: 284 degenerate · 16 measured — Freshness: 188 degenerate · 112 measured |

Directional-flow instruments today: **8 of 300** (alphabet, apple, jpmorgan, meta, nvidia,
citigroup, spacex, wells_fargo; the last three under the 0.25 intensity gate). None changes
tier under D8; max mm shift among them is +4.0 (apple 33.3→37.3). Exactly one (meta) sits at
mm 30.0 today — coincidentally, not degenerately (its analyst + freshness are measured;
mm_excl 30.1).

**Key structural overlap: the D8 cohort and the ledger cohort are DISJOINT.** Every one of
the 188 annihilated rows and all 95 tier-change rows is flow-neutral — and flow-neutral
instruments are unenrollable by construction (`record_market_detection` rejects
non-directional flows as unfalsifiable). The instruments D8 would move are precisely the
instruments the ledger never sees.

---

## 4. Market ledger backtest (n = 12 resolved)

### 4a. The resolved rows vs the degenerate signature

`/market/accuracy/detail` — all 12 resolved rows, with at-detection mm (stored
`detection_score`) and the D8 simulation on current state:

| Ticker | Detected | Flow | mm at detection | Verdict | mm now → D8-excl | Tier now → D8 | Degenerate-pinned at detection (mm==30.0)? |
|---|---|---|---|---|---|---|---|
| TSLA | 06-25 | inflow | 44.2 | CONFIRMED | 29.0 → 27.7 | ROUTINE → ROUTINE | No |
| AMZN | 06-25 | inflow | 68.5 | CONFIRMED | 31.8 → 33.9 | MODERATE → MODERATE | No |
| META | 06-25 | inflow | 70.0 | CONFIRMED | 30.0 → 30.1 | ROUTINE → ROUTINE | No |
| AAPL | 06-25 | outflow | 69.7 | NOT_CONFIRMED | 33.3 → 37.3 | ROUTINE → ROUTINE | No |
| GOOGL | 06-25 | outflow | 68.5 | NOT_CONFIRMED | 31.9 → 34.2 | ROUTINE → ROUTINE | No |
| NVDA | 06-25 | outflow | 68.5 | NOT_CONFIRMED | 30.6 → 30.6 | ROUTINE → ROUTINE | No |
| TSLA | 06-29 | inflow | 33.8 | NOT_CONFIRMED | 29.0 → 27.7 | ROUTINE → ROUTINE | No |
| AMZN | 06-29 | inflow | 32.6 | CONFIRMED | 31.8 → 33.9 | MODERATE → MODERATE | No |
| AAPL | 07-01 | outflow | 32.4 | NOT_CONFIRMED | 33.3 → 37.3 | ROUTINE → ROUTINE | No |
| META | 07-02 | inflow | 41.1 | CONFIRMED | 30.0 → 30.1 | ROUTINE → ROUTINE | No |
| AAPL | 07-07 | outflow | 41.2 | NOT_CONFIRMED | 33.3 → 37.3 | ROUTINE → ROUTINE | No |
| META | 07-08 | inflow | 34.4 | CONFIRMED | 30.0 → 30.1 | ROUTINE → ROUTINE | No |

- **0 of 12 resolved detections carried the degenerate-pin headline signature (mm == 30.0
  exactly) at detection time.** All 12 are covered-lane majors whose directional flow came
  from real positioning evidence — the same evidence that fired the enrollment.
- **0 of 12 would have failed to fire under D8** — structurally (the gate never reads mm)
  and empirically (no at-detection pin; no tier change under simulation; every mm shift ≤4.0).
- Detections that would newly fire under D8: also 0 (D8 removes components; it cannot create
  a directional flow or raise `movement_intensity`).

### 4b. Rates — actual vs D8 counterfactual (identical row sets → identical rates)

Wilson 95% intervals; n's as served.

| Read | Actual | D8 counterfactual |
|---|---|---|
| Blended | 6/12 = **50.0%** [25.4, 74.6] | 6/12 = 50.0% [25.4, 74.6] — **unchanged** |
| Inflow lane | 6/7 = **85.7%** [48.7, 97.4] | unchanged |
| Outflow lane | 0/5 = **0.0%** [0.0, 43.4] | unchanged |
| NO_MOVE | 0 | unchanged |
| By current market lane | covered 6/12 (halted_microcap 0 enrolled — ever) | unchanged |
| Pending (not inspectable) | 6 | 6 |

Adjacent finding (not D8, worth the record): the **outflow lane is 0-for-5** while inflow is
6-for-7. At n=5 the interval reaches 43%, so it is not yet a verdict — but it rhymes with the
2026-06-26 degenerate-net insider finding (routine selling ≈ noise; buying is the signal).
If it persists as n grows, the fix is in the FLOW claim (positioning_intel outflow logic),
not in money_movement — and no D8-style component exclusion would touch it.

### 4c. Why current-state back-projection must not be used to prune the ledger

Classified on CURRENT component state, 11/12 resolved rows show a degenerate Insider
Tracking component today (only NVDA is fully measured). Had we back-projected today's
signature onto the ledger and dropped "degenerate-cohort" rows, the ledger would shrink to
n=1 (NVDA, NOT_CONFIRMED → 0% blended) — while the stored at-detection mm (68.5, 70.0,
44.2 …) PROVES those instruments were not pinned when they fired. Current state is not
detection-time state; the stored `detection_score` is the honest at-detection witness, and by
that witness the degenerate cohort contributed **zero** resolved rows.

---

## 5. Crypto ledger backtest (n = 1 resolved)

- **Live state (2026-07-19, `/crypto`):** all 12 coins serve mm = 30.0 exactly; **both** MM
  components (Proxy Positioning w=0.75, Signal Freshness w=0.25) are z=0.0 degenerate on all
  12. **D8 does not move the crypto D ring — it annihilates it**: mm → None on 12/12 coins.
  Market Confirmation differentiates (23.6–55.4) and flow differentiates (7 inflow / 2
  outflow / 3 neutral), so the D8-excluded crypto payload would be an M-only score with a
  flow annotation.
- **Ledger:** `/crypto/accuracy` — resolved 1, pending 1. The one resolved row: BTC, detected
  2026-06-26, inflow, stored mm context 19.7 (not 30.0 — pre-pin/calibrating era), CONFIRMED
  at +8.31% on 07-14, lead 18d. Blended 1/1 = 100% — Wilson 95% **[20.7, 100.0]**, i.e. the
  data cannot distinguish a coin-flip from a perfect signal.
- **Excluded-vs-floor-pinned comparison:** identical — enrollment gates on the
  baseline-independent proxy-DM intensity (BTC dm intensity 60 ≥ 40 today; 11 coins serve no
  intensity and so cannot enroll), and the verdict is realized coin price vs the FLOW claim.
  The pinned D=30.0 number was never consulted; removing it changes 0 enrollments and 0
  verdicts. At n=1 there is nothing further to measure.

---

## 6. Threats to validity

1. **Post-hoc component state.** Component-level degenerate classification uses the
  2026-07-19 payload, not detection-time state (no served history). Mitigated for the
  headline by the stored at-detection `detection_score` (mm), which is decisive here
  (0/12 pinned); §4c quantifies how badly current-state back-projection would mislead
  (it tags 11/12). Residual risk: a component could have been degenerate at detection yet
  measured today on a row whose at-detection mm was coincidentally non-30.0 — undetectable
  from endpoints, and irrelevant to firing (the gate never reads components).
2. **Small n.** 12 equity + 1 crypto resolved verdicts. The blended interval spans
  [25.4, 74.6] — the ledger cannot yet detect ANY intervention's effect on rates, let alone
  a null one. This cuts both ways: it also means no accuracy claim FOR D8 could be
  demonstrated today even if the mechanism allowed one.
3. **Survivorship / pending censoring.** 6 market + 1 crypto pending rows are uninspectable
  via endpoints; all resolved rows are threshold-crossers (no NO_MOVE yet), so the resolved
  set over-represents movers. Does not affect the Δ=0 conclusion (gate decoupling is
  mechanism-level), but bounds any rate statement.
4. **Regime drift inside the sample.** The 06-25 detections carry mm 68.5–70 vs ~30–33 for
  the same instruments today — quarantine flip, baseline accumulation, and the 07-15
  `record_market_cycle` None-skip fix all landed inside the sample window. The 12 rows are
  not one regime. Again immaterial to Δ=0; material to any future rate-trend claim.
5. **Snapshot breathing.** The pin cohort measured 173 on the earlier 07-19 pull and 189 on
  this one (Signal Freshness flips between measured/degenerate cycle to cycle). Class
  membership at the margins is cycle-sensitive; the disjointness with the ledger cohort
  (flow-neutral ⇒ unenrollable) is not.
6. **This backtest cannot evaluate what D8 would do to a FUTURE, rewired enrollment** (e.g.
  if the ledger ever gated on mm or tier). Under the current recorder, Δ=0 is exact; that
  invariant should be restated if enrollment logic ever changes.

---

## 7. Verdict

**The evidence does not justify a board gate for the score-side change (D8) on accuracy
grounds. The display-only D7 quartet suffices for the integrity problem that motivated the
item.**

- The backtest's answer to the gated question is exact and null: under the live recorders,
  excluding degenerate components changes **0 enrollments and 0 verdicts** on both ledgers —
  blended 6/12 = 50.0% [25.4, 74.6] and 1/1 [20.7, 100.0] are byte-identical in the
  counterfactual. There is no accuracy payoff to buy with a score-affecting change, and at
  the current n there could be no demonstrable one for months regardless.
- The cohorts are structurally disjoint: every instrument D8 would materially move
  (188 mm→None + 95 ROUTINE→DORMANT) is flow-neutral and therefore unenrollable; every
  enrolled detection fired on filings-evidence flow with a non-pinned at-detection mm.
- What D8 actually is, on the evidence, is a **presentation-truth decision, not an accuracy
  decision**: it would remove the D ring entirely from 188/300 equity rows and all 12 crypto
  coins (mm → None, an honest "no informed-money data"), rather than re-rank anything the
  ledger can falsify. That is exactly the territory D7 already covers display-side
  (degenerate-baseline stamp + absence serialization + crypto coverage fields + mobile
  parity) without touching a served score.
- **Recommendation:** ship D7; **defer D8** (do not convene the score-side board gate now).
  Revisit only if (a) after D7, the founder wants served mm/tier to equal the honest-absence
  display state on the affected rows — at which point this file is the backtest evidence
  that the change is ledger-neutral, satisfying backtest-before-ship for that narrow claim —
  or (b) positioning coverage grows (Finviz insider breadth / 13F expansion) so degenerate
  baselines start converting to measured ones and exclusion semantics would bind on data
  rather than on absence. Track the **outflow 0/5** thread separately (positioning_intel
  flow logic, n too small today) — it is the one live lead in this ledger, and D8 would not
  touch it.

---

*Method note: single-snapshot pulls 2026-07-19 (engine UTC): `/risk/scores?limit=300` →
scratchpad `risk_scores_d8.json` (1.8 MB), `/market/accuracy[.detail]`,
`/crypto[,/accuracy,/accuracy/detail]`; analysis script `d8_analysis.py` retained in the
session scratchpad, not committed. Served-mm reconstruction validated 300/300 before any
simulation. No production data was modified; no sweeps were triggered; no paid actors ran.*
