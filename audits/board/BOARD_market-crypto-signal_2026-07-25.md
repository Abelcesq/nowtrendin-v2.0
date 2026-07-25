# ADVISORY BOARD — Market Signal + Crypto Signal reassessment
**Convened:** 2026-07-25 by the Chairman · **Six archetypes, independent, no cross-visibility**
**Evidence pack:** identical for all six; all six independently re-verified against live code per §10a.
**Status:** COLLATION FOR THE CHAIRMAN — nothing has been shipped, flipped, or changed.

---

## 0. WHY THIS WAS CONVENED

The Chairman's stated purpose for the Market Signal (and Crypto Signal):

> "The market signal focuses on money movement. The goal of this section like crypto is to attempt to utilize our system to 'predict' (if at all possible or at least to indefinity) where insiders are moving their money in and out before the mainstream begins to move it."

Three items were put to the Board: (1) the contested congress/13F wiring; (2) reconciling the Chairman's insider-precedes-mainstream thesis with our own null backtest; (3) a sources/tools/agents roadmap.

**A correction was made to the pack before the Board convened.** The `or MARKET_SIGNAL_V2` gate was initially characterized (by Claude, to the Chairman) as an accidental "leak." Git history disproved that: commit `72b7271` states verbatim *"MARKET_SIGNAL_V2 implies the congress/13F dark-positioning blend (they are D inputs),"* and `MARKET_SIGNAL_V2.md` §4 calls the return backtest *"a footnote, not a gate."* The blend is **deliberate**. The pack was corrected to present both sides before fan-out. This is itself a §10a verify-before-fix instance: the first diagnosis was wrong, and checking git history before acting is what caught it.

---

## 1. VERDICT TABLE

| | Item 1 — Contested wiring | Item 2 — Reconciliation | Item 3 — Roadmap |
|---|---|---|---|
| **Challenger** | **REJECT** (a); adopt (b) | APPROVE-WITH-CONDITIONS | APPROVE-WITH-CONDITIONS |
| **First-Principles Guardian** | **REJECT** as-is → restore `DARK_POSITIONING_V2`-only | APPROVE-WITH-CONDITIONS | APPROVE-WITH-CONDITIONS (strict ordering) |
| **Expansionist** | **REJECT** as-is; adopt (b) | APPROVE-WITH-CONDITIONS | APPROVE-WITH-CONDITIONS (re-ranked) |
| **Outsider (VC/banker)** | **REJECT** as wired | APPROVE-WITH-CONDITIONS | APPROVE-WITH-CONDITIONS |
| **Economist** | **REJECT** as wired; adopt (b) | APPROVE-WITH-CONDITIONS | APPROVE-WITH-CONDITIONS (reprioritised) |
| **Executioner** | **SHIP-LATER** — as a config flip, after evidence capture | SHIP-LATER (one instrument first) | per-candidate (see §5) |

**6/6 against the blend as currently wired.** The only divergence is *timing*: five say the wiring is indefensible now; the Executioner agrees on substance but rules **do not flip until you can prove what the flip did** — you currently have no instrument that would tell you whether it helped.

---

## 2. THE FINDING THE PACK DID NOT CONTAIN

Four archetypes independently traced the same defect, and it reframes Item 1 entirely. **The dispute in the pack was about lag and validation. The actual defect is dimensional.**

`positioning_intel.py:114-116`:
```
positioning_signal = 0.6·min(1, funds_holding/6) + 0.4·min(1, members/8)
```

**(a) It has no direction in it.** `net = buys − sells` and `flow` (in/out) are computed at `:100`/`:117` — and routed *only* to display and the ledger. What is blended at 0.4 weight into the score is **unsigned breadth**. Congressional *selling* raises the component exactly as much as buying, while the UI renders D-high as *"Informed money is moving here AHEAD of broad market confirmation"* (`market_signal_engine.py:434-439`).

> **Challenger:** *"An auditor needs one line: 'Eight members dumped it; your score rose.'"*
> **Guardian:** *"It cannot serve the Chairman's stated purpose — in and out before mainstream — even in principle. That is not a policy disagreement; it is a dimensional error."*

The repo *already knows* this failure mode: `positioning_intel.py:135-137` fixes exactly this degeneracy (buying-is-signal, net is sell-dominated) — **for the AV insider term that is switched off**, while the congress/13F term that is switched **on** keeps it.

**(b) 0.6 of it is a market-cap proxy.** `_build_smart_money()` reads `top_holdings` from ~9 curated funds, and `latest_13f()` truncates to the **top 10 positions per fund** (`sec_13f_research.py:154`). The entire "smart money" universe is ≤90 issuers — overwhelmingly mega-caps. `funds_holding` pins at 1.0 permanently for AAPL/MSFT/NVDA and 0.0 for small caps.

> **Economist:** *"0.4 × 0.55 = **22% of Money Movement (D)** is a quarterly step function of 'is this a large index constituent.'"*
> **Outsider:** *"40% of a component called 'positioning concentration' is a large-cap popularity proxy positively correlated with mainstream attention — the exact opposite of what a dark-matter input is supposed to be. That isn't a lag problem you can fix by waiting; it's a construct-validity problem."*

**(c) The backtest never tested the wired variable.** The backtest correlated *direction* (`net`) with returns. The blend uses *intensity*. **Economist:** *"The blended term has never been tested against anything. Under the null, burden of proof runs toward the component."*

**(d) Variance destruction.** A near-constant quarterly term blended into `positioning_concentration` shrinks that component's own stdev toward the floor — silent inflation on a baseline-relative engine, invisible in a code diff, and it interacts with the §16a degenerate class.

---

## 3. THE SECOND STRUCTURAL FINDING — the ledger does not validate the product

Independently reached by Guardian, Economist, Outsider, Challenger.

- **The market ledger enrolls on the congress feed, not the Market Signal.** `financial_risk_gradient.py:2600-2604` passes `_dpi2["flow"]` (congressional net direction) and `movement_intensity`. `detection_score` is stored as a witness and **never thresholded, never in the verdict** (by design, `:220-227`). With `AV_DARKPOS_ENABLED` off, `flow` is **100% congressional net**.
  > **Economist:** *"It is a track record of the QuiverQuant congress feed, on a universe structurally confined to mega-caps — exactly the cohort already shown to be a coin flip. It will converge on ~50% by construction, and the Chairman will be tempted to read that as a verdict on his product. It is not."*
  > **Guardian:** *"The product's only falsifiable money claim rests entirely on its slowest source, while its fastest lawful source (Form-4, 2 business days, already paid for) is excluded from that claim. If one thing is fixed this quarter, it is this."*

- **`lead_time_days` is time-to-our-own-price-move, not lead over mainstream.** `market_accuracy_ledger.py:326`: `lead = move_date − detection_date`, where `move_date` is the first ±5% close. Nothing observes when mainstream *arrived*.
  > **Guardian:** *"If the confirming event is a price threshold, 'we detected it early' means 'we were early to the move' — alpha wearing measurement's clothes, no matter how thoroughly §5 purges the word. **Extending 'before it arrives' from attention to money is legitimate; extending it from arrival to payoff is the drift.** Rule the target, not the vocabulary."*

- **Three measurement defects in published figures** (Challenger + Outsider):
  1. `median_lead_days` is computed over **CONFIRMED rows only** (`:538`) and published as "Median lead" (`Ledger.tsx:184`) → survivorship by construction.
  2. `_regime_adjusted()` (`:446-450`) filters to rows with non-null `move_date`, but `NO_MOVE` rows are written with `move_date = None` (`:404`) → **the benchmark-adjusted rate silently excludes every flat outcome** while the raw rate includes them. *Outsider: "Found undisclosed in a data room, it costs you the deal."*
  3. Market ledger window is **60 days** (`:47`) vs the attention ledger's **365** — the two rates are presented side by side but are not comparable, and Kaplan-Meier was never ported to the market ledger.
  4. **No null control.** A ±5% move within 60 days on a liquid large-cap is near-certain; direction is a coin flip. No matched-random comparator exists.

---

## 4. ITEM 2 — THE RECONCILIATION (unanimous in substance)

All six converge: **the Chairman's thesis is not refuted — it was tested in the one place it was never plausible.**

> **Outsider:** *"Form-4 (2 business days) and 13D (10 days) are where the surviving literature — Lakonishok–Lee, Cohen–Malloy–Pomorski on 'opportunistic' insiders, Brav/Jiang on activists — still finds real, replicable abnormal returns, concentrated in small/mid-cap, low-coverage names. Your backtest tested 35 liquid large-caps and found nothing. That is the expected result. It does not falsify the Chairman's thesis; it tested it in the one place the thesis was never plausible."*
> **Economist:** *"Absence of evidence there is not evidence of absence elsewhere."*

The reconciliation the Board offers, in plain English (Outsider's phrasing):
> *"Insiders file before the crowd notices. Congress files too late to matter. Corporate officers file in two days, and that's where we look."*

**Unanimous conditions:**
1. **Re-target the ground truth to LEAD** — measure detection → *mainstream arrival* (abnormal volume vs trailing 60d, coverage-breadth expansion, analyst initiation), **not** detection → our own price move. Guardian adds the non-circularity constraint: the arrival clock **must not be derived from price**.
2. **Re-target enrollment** to Form-4 buying velocity (2-day lag, already paid for) + 13D/G, not congress direction.
3. **Re-target the universe** to small/mid-cap, low-coverage names, pre-registered as a hypothesis rather than a post-hoc slice.

This also resolves the "predict" vs measurement-not-advice tension: a measured statement about **our own timing against a control, after the fact** is measurement. A price-threshold target is a trading record.

---

## 5. ITEM 3 — ROADMAP (verdicts differ; see disagreements)

| Candidate | Challenger | Guardian | Expansionist | Outsider | Economist | Executioner |
|---|---|---|---|---|---|---|
| **Lead-time auditor** | precondition | **build first** | first, jurisdiction-segmented | **build first** | prescribed | **SHIP (first)** |
| **Form-4 velocity** | same fix needed | route into `flow` | **the portable primitive** | #2, $0 incremental | Tier 1 | **SHIP** |
| **13D/G + 8-K (EDGAR, free)** | only defensible one | Tier 2 | Tier 1 (intl. twins better) | **#1** | Tier 1 | SHIP-LATER |
| **Turn on `insider_feed()`** | — | — | **highest leverage; dead code** | — | — | (implicit in Form-4) |
| **On-chain crypto** | — | hold at CALIBRATING | **Tier 1 — biggest gap** | #4, "weakest link" | **DEFER** (use free funding/basis first) | SHIP-LATER, funded by swap |
| **Options flow** | — | defer | Tier 2 | **defer** ($2-10k/mo, hedge-contaminated) | Tier 2 defer | **CUT** |
| **Dark-pool/ATS** | — | defer | Tier 2 | — | defer | **CUT** |
| **Borrow rate** | — | — | Tier 2 | #3 "cheap" | Tier 1 (price of positioning) | **CUT** |

**Expansionist's standout operational finding:** `finviz_data.py:132 insider_feed()` — documented as *"the Dark-Matter goldmine, ~100 insider buys across ALL tickers in ONE call"* — has **exactly one call site, inside `if __name__ == "__main__"`. It is dead code.**
> *"We pay $30/mo for market-wide and run watchlist-wide."* And `WATCHLIST_TICKERS` is **16 hard-coded names in Python source** (`financial_risk_gradient.py:1124`). *"The only thing standing between us and 100× coverage is a Python dict and a deploy step."*

**Expansionist's international map** (the strategic argument on Quiver): every input we rely on has a good international analogue — **except congress, which has none anywhere**, and which is the one input welded into the score at 0.4. Two analogues are *faster* than their US counterparts: EU/UK **TR-1** major-shareholding notifications (event-driven, days — vs 13F's quarterly/45-day) and ESMA **net short position** registers (daily — vs FINRA bi-monthly). Insider-disclosure regimes are near-universal (US 2bd, India 2, UK 4, EU MAR 4, HK 3, Japan/Canada/Australia 5). *"The global build is more achievable than it looks."*

**Crypto defect** (Challenger + Expansionist): `crypto_signals.py:60-90` — 8 of 12 coins have **`COIN` (Coinbase equity) as their only proxy**, differing solely by a static 0.3–0.4 weight. Cross-coin Money Movement ranking among them is **deterministic, not informative**. Worse, the crypto ledger's episode collapse keys on (ticker, flow) and does **not** collapse across coins — one Coinbase filing can enroll ~8 correlated rows that are one bet, inflating the denominator.

---

## 6. EXECUTION — how this would actually be done (Executioner, decisive)

The Executioner found that **the pack's literal option (b) is a trap**, and that a safer lever already exists.

1. **A config-only kill switch exists.** `DARK_POS_WEIGHT` (`market_signal_engine.py:66`). At `0`, line 493 reduces to `_norm(pos_conc)` — **byte-identical to unblended. No code, no deploy.**
2. **Do NOT gate lines 2371/2567 on `DARK_POSITIONING_V2`** (the pack's literal option b). Those control whether `positioning_intel` is *attached at all*; killing them empties `_dpi2` → `flow`→`neutral` → **`record_market_detection` rejects every row as non-directional** → the market ledger silently stops recording. *"That is the trap."*
3. **Ledger blast radius of a `DARK_POS_WEIGHT` change is provably zero** (enrollment gates on `flow`+`intensity`; `detection_score` is a witness, guarded by `test_market_ledger_witness.py`). **Crypto is unaffected** (zero references, grep-verified).
4. **Prove the change, don't just observe it:** precompute `expected_current = (current − 0.4·sig) / 0.6` per ticker **before** flipping; pass criterion is an exact match, plus Δ(ledger)=0.
5. **`serve_payload` regeneration is NOT required** — that is the *trend* path. Market scores live in `risk_scores` + the prewarmed risk superset; changes appear after one scoring cycle (≤6h). Poll `/prewarm`, never loop on `/scores`.
6. **Known transient:** `market_signal_history` holds 12 cycles of *blended* values, so after a flip `current` drops while `baseline_mean` stays elevated → **z goes negative for ~12 cycles (~3 days)**. A baseline regime break, not a regression. Annotate up front; **do not delete history to "fix" it.**
7. **Rollback:** `heroku config:unset DARK_POS_WEIGHT -a nowtrendin-v2-engine`.

**New bug found in passing (Executioner):** `positioning_intel.py:107` matches 13F issuers by **unbounded substring** (`qn in nm or nm in qn`), and `signal_for` is called with `display` as ticker when no watchlist entry exists (`:2570`). Short/generic names can match unrelated issuers and inflate `funds_holding`. *"Verify before any ruling that assumes the blend measures what it claims."*

**Executioner's ship order:** (1) doc reconciliation → (2) fix the substring match → (3) evidence capture → (4) lead-time auditor → (5) `DARK_POS_WEIGHT` flip *if the Chairman so rules* → (6) Form-4 velocity (backtest-gated) → (7) cost swap → 13D/G → on-chain.

---

## 7. DISAGREEMENTS (not smoothed)

1. **Flip now, or instrument first?** Challenger / Guardian / Expansionist / Outsider / Economist: the wiring is indefensible — restore the gate. **Executioner: SHIP-LATER** — capture before-state evidence and build the lead auditor first, because *"you currently have no instrument that would tell you whether the flip helped."* **This is a sequencing disagreement, not a substantive one.**
2. **How many new agents?** **Economist prescribes four** (degenerate-signal detector, lead-time, decay, source-value). **Executioner: CUT to one** — build the lead auditor, fold decay and source-value in as segments of the same report, extend the existing `/monitor/degenerate-census` rather than writing a fifth agent. *"Four agents is four things that page you at 3am."* Direct conflict.
3. **On-chain crypto priority.** **Expansionist: Tier 1**, the single largest legibility gain (crypto is the most globally scalable surface, currently read "through a US equity keyhole"). **Economist: DEFER** — exhaust free funding-rate/basis/stablecoin-supply series first, which capture most of what Glassnode sells. **Outsider:** largest genuine gap but ranks it #4 behind free EDGAR sources. **Executioner:** SHIP-LATER, and only funded by deleting dead Heroku apps, not as a new spend.
4. **Quiver's subscription.** The Chairman has ruled: **keep it.** The Board did not contest that ruling, but qualified it: **Outsider** — fund other work by killing the $30 *if* congress goes display-only and nobody clicks it; **Economist** — keep only if the source-value auditor shows measured lead; gov-contracts and lobbying are genuinely pre-mainstream and pass §16, WSB sentiment is *"mainstream-crowd, not dark matter, and circular-adjacent with our own attention side,"* corporate-jet tracking fails on provenance; **Expansionist** — strategically it is the one input with no international analogue.
5. **Borrow-rate data.** Economist calls it Tier 1 (*"the price of positioning, which moves before the underlying"*); Outsider ranks it #3 and cheap; **Executioner CUTs it** as licensed and single-purpose.
6. **Is the three-rate disclosure a strength or a risk?** **Outsider: a strength** — *"blended 10.8% / tracked-race 26.3% / KM 3.4% reads as unusual rigor... the fact that the most flattering framing is disclosed alongside the most punishing one is the strongest single credibility signal in the pack"* — **but** label which is the headline and never move it, *"three rates become number-shopping the instant a deck picks whichever is highest that quarter."* Challenger treats the same spread as evidence the market ledger's incomparable 60d window needs fixing before publication.

---

## 8. WHAT THE BOARD AGREES ON UNANIMOUSLY

1. The congress/13F term **as currently wired** should not carry weight in a scored component (6/6).
2. The **documentation contradiction must be fixed regardless of the ruling** — three artifacts (`positioning_intel.py:10-13`, `market_signal_engine.py:485-486`, SESSION_LOG) assert a safety gate that does not exist in production. *Challenger: "the most discreditable artifact in the repository; counsel doesn't need the math."*
3. The Chairman's thesis is **legitimate and testable** — and was tested in the wrong regime (mega-caps, 30-45d lag).
4. **Form-4 velocity, in low-coverage names, is where the thesis can actually be true** — and it is already paid for.
5. **Build the lead-time auditor before buying any new source.** *Guardian: "You cannot price a source whose value you cannot measure."*
6. The **crypto proxy chain** (equity 13F → crypto smart money) is the weakest link in the stack and must be labelled honestly (§17) or held at CALIBRATING.
7. Nothing here is score-affecting until the Chairman rules; backtest-before-ship and flag-never-force apply throughout.

---

## 9. NOTED FOR THE RECORD — the moat

> **First-Principles Guardian:** *"Today: diluted at the edges, intact at the core. Intact because the ledger machinery is genuinely rigorous and I verified it: non-directional flows rejected, MIN_INTENSITY gate, one-open-row-per-(ticker,flow) dedup against correlated flooding, the at-detection witness never substituted, gate-rejects counted so what the ledger never sees is on the record, no-lookahead, regime-adjusted, and the standing rule forbidding publication at n=12/6 episodes. **That is a team defending a number it cannot yet defend — which is the founding vision behaving correctly under pressure.** Diluted because the scored surface now contains a 0.4-weight input that is direction-free, lag-bound and documented-null, while the falsifiable surface measures time-to-price rather than lead-over-mainstream. Fix the clock, route the fast source, restore the gate. Then the money moat is real."*

> **Outsider:** *"Deal-makers: the 365-day patience window, the episode-collapse anti-gaming logic, and the fact that you built a ledger that can prove you wrong. Very few founders do that. Fix the wiring and I'd take a second meeting."*

---

**Chairman — your decision per item.**
