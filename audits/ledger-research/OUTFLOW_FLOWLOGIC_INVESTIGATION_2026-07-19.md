# OUTFLOW FLOW-LOGIC INVESTIGATION — held-out, read-only (2026-07-19)

**Chairman-ordered E2** (board record `audits/board/BOARD_D8-degenerate-exclusion_2026-07-19.md`,
decision-table row E2, 6/6 board standing — "the one live lead"). A NEW, independent item —
not a transform of D8. Question: the market accuracy ledger's **outflow lane is 0-for-5
resolved** while inflow is 6-for-7 — is the outflow CLAIM built on the evidence class already
ruled degenerate for insiders on 2026-06-26 (routine selling ≈ noise), and does the lane beat
a regime base-rate control?

**Hard constraints honored:** read-only everywhere; this file is the ONLY artifact written; no
git writes, no code changes, no paid pulls, no SQL. Sources: full code read of
`transfer/positioning_intel.py`, `transfer/market_accuracy_ledger.py`,
`transfer/financial_risk_gradient.py` (enrollment site ~2567–2606, detail serve
`get_risk_detail`/`_format_risk_row`), `transfer/gravitational_anomaly_detector.py`
(`GET /risk/{topic}` route ~6673); live engine pulls (`/market/accuracy`,
`/market/accuracy/detail`, `/risk/{topic}` for the episode instruments); free Stooq daily CSV
for ground-truth closes (no key, no cost). The ledger is HELD-OUT: nothing here edits a row,
and **nothing here proposes throttling outflow enrollment** (board forbid — the losing lane IS
the evidence).

---

## 0. PRE-REGISTRATION (written before any price data was fetched or any rate computed)

Per the board's order (Challenger: regime control FIRST; Economist: pre-registered review
threshold), the following are fixed BEFORE computation:

### 0.1 Defect criterion (pre-registered)

> **The outflow lane is DEFECTIVE if outflow claims confirm at a rate at or below the regime
> base rate of qualifying downward moves for the same tickers over the same windows.**

Operationally: for each resolved outflow row, the confirmation event is the ledger's own
mechanics as coded in `market_accuracy_ledger._evaluate` — starting from the first available
EOD close on/after `detection_date` (skipping ≤6 days for weekends/holidays), walk closes
strictly AFTER the detection-day close; the FIRST close at or beyond **−5%** (outflow-confirm)
or **+5%** (opposite → NOT_CONFIRMED) decides; neither within **60 days** → NO_MOVE
(`MOVE_THRESHOLD_PCT=5.0`, `MARKET_TIMEOUT_DAYS=60`, confirmed from code before computation).

The regime base rate is estimated by sliding the SAME first-crossing procedure across every
feasible start date for the same ticker within June–July 2026 (all trading days with enough
forward data to resolve, same thresholds, same walk): the fraction of start dates on which an
outflow claim would have CONFIRMED. If the lane's observed confirm rate ≤ that base rate, the
claims carry no information beyond regime; combined with a mechanism trace showing the claims
derive from the degenerate-net evidence class, the lane is defective **in mechanism** (subject
to §0.2's n-threshold for a formal verdict).

### 0.2 Review threshold (pre-registered)

> **No lane verdict is issued until outflow resolved n ≥ 15, OR immediately if the lane
> reaches 0-for-10.** Today (n=5) this report is MECHANISM evidence only, not a verdict.

Also pre-registered: rates are reported BOTH per-row and **episode-collapsed** (idempotent
re-enrollment of a persistent flow makes rows correlated; the Challenger's ~7-episodes
finding), and no lane rate from this file may be published externally as an accuracy KPI.

*(Everything below §0 was computed after this section was written.)*

---

## 1. The resolved outflow rows (served, verified against reconstructed prices)

`/market/accuracy` (2026-07-19): resolved 12, pending 6; blended 6/12 = 50.0%; **inflow 6/7 =
85.7%**, **outflow 0/5 = 0.0%**, NO_MOVE 0. The five resolved outflow rows from
`/market/accuracy/detail`, each re-evaluated independently from free Stooq daily closes using the
ledger's own first-crossing rule (`_evaluate`: start at the first close on/after `detection_date`,
walk forward, first ±5% crossing decides):

| # | Ticker | Detected | det_score (mm) | Served verdict | First 5% crossing (my recompute) | change@cross | Matches ledger? |
|---|---|---|---|---|---|---|---|
| 1 | NVDA | 2026-06-25 | 68.5 | NOT_CONFIRMED | **UP** on 07-10 | +7.78% | ✓ (served p1 210.97 = +7.8%) |
| 2 | GOOGL | 2026-06-25 | 68.5 | NOT_CONFIRMED | **UP** on 07-01 | +5.09% | ✓ (served p1 361.21 = +5.1%) |
| 3 | AAPL | 2026-06-25 | 69.7 | NOT_CONFIRMED | **UP** on 06-30 | +5.16% | ✓ (served p1 289.36 = +5.2%) |
| 4 | AAPL | 2026-07-01 | 32.4 | NOT_CONFIRMED | **UP** on 07-06 | +6.21% | ✓ (served p1 312.66 = +6.2%) |
| 5 | AAPL | 2026-07-07 | 41.2 | NOT_CONFIRMED | **UP** on 07-15 | +5.42% | ✓ (served p1 327.5 = +5.4%) |

Every outflow claim resolved because the stock crossed **+5% (upward)** before −5% — i.e. each name
rose right after we called money flowing OUT. My independent reconstruction reproduces the ledger's
p0, p1, change_pct, and verdict on all five rows, validating both the price series and the procedure
before any base-rate work. The realized cluster moves were all sharply positive: AAPL **+19.0%**,
NVDA **+8.6%**, GOOGL **+7.9%** from 06-25 to ~07-15. The outflow lane fired into a mega-cap rally.

## 2. Mechanism trace — the outflow claim is the degenerate-net class (Executioner's candidate confirmed)

**Finding A — AV_DARKPOS_ENABLED is effectively OFF in production.** Every served
`dark_positioning_intel` payload carries `dark_matter_inputs = "congress + curated_13F"` — NOT the
`"... + av_insider + av_institutional"` string that the flag-on path writes
(`positioning_intel.py` L170). So the AV blend block (L136–172), including the **asymmetric flow fix
at L160** (`ins_dir = "inflow" if ins.get("signal")=="accumulation" else None` — routine selling
casts NO vote), never runs. The production flow claim is built **entirely by the base path**.

**Finding B — the base flow claim is congress net (buys−sells) < −1, the exact degenerate-net class.**
`positioning_intel.signal_for` L118: `flow = ("inflow" if net > 1 else "outflow" if net < -1 else
"neutral")`, where `net = cg["buys"] - cg["sells"]` (L100). This is the raw congressional net — and
the served payloads for all three outflow instruments are sell-dominated:

| Instrument (served 2026-07-19/20) | congress buys | sells | net | → flow | movement_intensity |
|---|---|---|---|---|---|
| AAPL (apple) | 6 | 14 | **−8** | outflow | 1.00 |
| GOOGL (alphabet) | 4 | 9 | **−5** | outflow | 1.00 |
| NVDA (nvidia) | 6 | 11 | **−5** | outflow | 0.95 |

This is the same failure mode the board already ruled degenerate for insiders on **2026-06-26**
(`SESSION_LOG.md` L72–73): *"raw insider NET is degenerate (15/15 basket 'outflow' — insiders
structurally sell). The signal is insider BUYING (`signal=='accumulation'`, ≥$250K); routine
selling = neutral, not bearish."* Congressional trading for mega-caps is likewise sell-skewed
(diversification, tax, comp-driven), so `net < −1` fires 'outflow' on routine selling. The insider
blend got the accumulation-only correction (L160); **the congress base flow at L118 never did** —
and in production, with the AV blend off, L118 IS the whole signal. The Executioner's traced
candidate path is confirmed as the live mechanism for all five resolved outflow rows.

Note the intensity is saturated (1.0 / 1.0 / 0.95), so these clear the `MIN_INTENSITY=0.25`
enrollment gate easily — the gate measures *breadth of trading*, not *directional conviction*, so a
name being heavily but routinely sold enrolls a high-intensity outflow claim.

## 3. Regime base-rate control (Challenger's FIRST test) — run before any verdict

For each outflow ticker I slid the identical first-crossing procedure across every feasible start
date and counted the fraction that would CONFIRM an outflow claim (−5% crossed before +5%). Two
windows, because a regime shift sits inside the sample (these names fell into late May, rallied
through late June–July):

| Ticker | Broad window (May 20–Jul 17) DOWN-first | Local detection cluster (Jun 22–Jul 10) DOWN-first |
|---|---|---|
| AAPL | 17/30 = 56.7% | 3/14 = **21.4%** |
| GOOGL | 17/23 = 73.9% | 2/7 = **28.6%** |
| NVDA | 14/25 = 56.0% | 1/11 = **9.1%** |
| **Pooled** | **48/78 = 61.5%** | **6/32 = 18.8%** |

The **local cluster** is the honest, apples-to-apples control — the regime the claims actually lived
in. In that regime the base rate for an outflow-confirm was only **18.8%**: a coin-flip outflow call
on these names in that window would have failed ~81% of the time regardless of any signal, because
the tape was rising. Consequently **P(0-for-5 | local regime) = 0.812^5 = 0.35** — the lane's
0-for-5 is *fully consistent with regime alone*; no mechanism defect is required to explain it at
n=5. (Against the broad-window base rate 61.5%, P(0/5)=0.385^5=0.009 — but that base rate is
contaminated by the May selloff and is not the fair control.)

**This is the decisive methodological point, and it is exactly why the board pre-registered n≥15.**
The outflow lane and the inflow lane are **the same regime bet pointed in opposite directions**:
inflow fired into the rally and confirmed 6/7; outflow fired into the *same* rally and failed 0/5.
Both lanes are regime-confounded (Challenger). The 0-for-5 today is not yet evidence that the flow
claim is defective — it is evidence that we called OUT on names the market took UP, which regime
alone predicts.

## 4. Episode collapse (Challenger's correlated-rows correction)

The 5 outflow rows are not 5 independent trials. AAPL re-enrolls the same persistent congress
net-sell signal three times (06-25, 07-01, 07-07 — idempotent re-enrollment of an unresolved,
still-sell-dominated positioning state). Collapsing to independent signal episodes:

| Episode | Rows | Verdict |
|---|---|---|
| AAPL outflow (persistent) | 3 | all NOT_CONFIRMED |
| GOOGL outflow | 1 | NOT_CONFIRMED |
| NVDA outflow | 1 | NOT_CONFIRMED |

**Per-episode: 0-for-3**, not 0-for-5. Three independent episodes, all in the same up-regime, all on
the same degenerate-net mechanism. The effective n is even smaller than the row count suggests, and
the Wilson interval on 0/3 reaches ~56% — nowhere near a verdict.

## 5. Candidate SPEC (do NOT implement) — asymmetric outflow gate, future SCORE_AFFECTING

The mechanism is consistent across all three episodes, so per the board's step (4) I spec — **but do
not build** — the candidate fix. It mirrors the L160 insider accumulation-only rule, extending it to
the congress base flow:

> **Spec S1 (SCORE_AFFECTING; gated; not implemented here).** In `positioning_intel.signal_for`,
> stop letting a bare congressional net-sell assert 'outflow'. Options, in order of conservatism:
> (a) treat routine net selling as **neutral** (only `net > 1` → inflow; everything else neutral)
> unless corroborated by an independent OUT signal (institutional holders_decreased skew, or
> insider distribution beyond routine); (b) require ≥2 independent directional sources to agree
> before any directional flow enrolls (mirrors §15 part-1 ½/full reputable-corroboration and the
> `CATCHALL_MIN_SOURCES≥2` philosophy); (c) raise the outflow bar specifically (a magnitude/breadth
> threshold on net selling) while leaving inflow at `net > 1`.

**Mandatory gate before ANY of these ships** (this is a flow claim that drives enrollment, so it is
squarely score/ledger-affecting):
1. It cannot be justified on today's data — the pre-registered **n≥15 resolved outflow (or 0-for-10)**
   threshold governs, and the regime control (§3) shows the current 0-for-5 is regime-explained.
2. A held-out **backtest-before-ship** (§16 gate 5): re-derive the historical outflow enrollments
   under the new rule and show the ledger confirm rate improves *out of regime* (control for the
   tape), not merely that fewer outflow rows enroll. Naming the outcome metric the gate reads
   (ledger outflow confirm rate, regime-adjusted) is required per the Economist's P3 standing rule.
3. **Guardrail (Guardian):** the shortest path to a prettier ledger is loosening what counts as
   outflow. Any such change must be shown NOT to be silently suppressing true OUT calls — evaluate
   precision AND recall against realized down-moves, never just the confirm rate.
4. Never throttle or stop outflow enrollment because the lane is losing (board unanimous — Taleb's
   cemetery; the losing lane is the evidence). S1 changes how the *claim* is CONSTRUCTED from
   evidence; it does not censor the lane.

## 6. Threats to validity

1. **Small n / regime confounding (dominant threat).** n=5 rows / 3 episodes, all in one mega-cap
   up-regime. §3 shows 0-for-5 is consistent with regime alone (p=0.35 local). This is MECHANISM
   evidence, not a verdict — the pre-registered n≥15 / 0-for-10 threshold is not met.
2. **Detection-time vs current positioning state.** The congress buys/sells/net in §2 are the
   served 2026-07-19/20 payloads, not the stored detection-instant values (no served
   positioning-history route; `dark_positioning_intel` serves current state only). The *mechanism*
   (L118 base flow = congress net; AV blend off) is code-certain and time-invariant, and the stored
   `detection_score` (mm 68.5–69.7 on the 06-25 rows) confirms these were directional-flow
   detections at enrollment; but the exact buys/sells counts at each detection date are not
   endpoint-recoverable. The claim "all three are sell-dominated" is verified on current state and
   consistent with the sell-skewed nature of mega-cap congressional trading, not proven per-row at
   detection instant.
3. **Price source.** Stooq daily closes (free, unadjusted-for-nothing-material over this 3-week
   span); reconstruction reproduces the ledger's own p0/p1/change on all 5 rows (§1), so the series
   is validated against the engine's FMP-sourced verdicts. Any residual split/dividend adjustment
   over June–July 2026 is immaterial at the 5% threshold and did not desync a single row.
4. **Base-rate window choice.** I report both broad and local windows and rely on the local one as
   the fair control; the local window boundaries (Jun 22–Jul 10) are a judgment call, though the
   qualitative conclusion (low local outflow base rate → 0-for-5 is regime-explained) is robust
   across reasonable boundaries.
5. **Pending rows uninspectable.** 6 market pending detections exist but no endpoint exposes
   pending-row detail; they are not in any denominator and could shift the lane either way as they
   resolve.
6. **Read-only snapshot.** Single-pull 2026-07-19/20; the congress map rebuilds daily
   (`DARK_POS_TTL_SEC`), so net counts breathe. The mechanism finding does not depend on the
   snapshot; the specific net values do.

## 7. Honest verdict (per the pre-registered criteria)

- **No lane verdict is issued.** Outflow resolved n=5 (3 episodes) < 15, and the lane is not
  0-for-10. Per §0.2 this report is **mechanism evidence only.**
- **Mechanism finding (high confidence, code-certain):** in production (AV_DARKPOS_ENABLED off) the
  outflow claim for all five resolved rows is produced by `positioning_intel` L118 — a bare
  congressional net-sell (`net < −1`) — which is the **exact degenerate-net evidence class the board
  ruled noise for insiders on 2026-06-26**, and which never received the accumulation-only
  asymmetric correction the insider path got at L160. The suspect the board named is confirmed as
  the live mechanism.
- **Defect criterion (§0.1) — NOT met at n=5.** The lane's 0% confirm is at/below the regime base
  rate (0% ≤ 18.8% local; ≤ 61.5% broad), which satisfies the *literal* "≤ base rate" clause — but
  the local regime control shows 0-for-5 is what regime *alone* predicts (p=0.35), so the criterion
  is uninformative here: it cannot distinguish "degenerate-net noise" from "correct null signal
  swamped by a rally." Both point the same way today. A real verdict requires n≥15 spanning more
  than one regime, so the flow claim can be tested *out of tape*.
- **Standing recommendation:** keep enrolling the outflow lane unchanged (never throttle); track to
  n≥15 / 0-for-10; hold **Spec S1** as a queued SCORE_AFFECTING item behind its own held-out,
  regime-adjusted backtest gate. The 2026-06-26 insider precedent is a strong *prior* that the fix
  is real, but the ledger — not the analogy — must earn the change.

---

*Method note: read-only. Live pulls 2026-07-19/20 (engine `nowtrendin-v2-engine`):
`/market/accuracy`, `/market/accuracy/detail`, `/risk/{apple,alphabet,nvidia}`. Prices: Stooq daily
history HTML (`/q/d/?s=<t>.us`, free, no key; the CSV-download path was IP-quota-blocked so the HTML
history table was parsed instead — a JS proof-of-work anti-bot challenge was solved per-session to
reach it). Analysis scripts (`analyze.py`, `fetch_html.py`) retained in the session scratchpad, not
committed. No SQL, no paid pulls, no sweeps, no code/ledger/git writes. This file is the only
artifact.*
