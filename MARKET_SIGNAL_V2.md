# Market Signal v2.0 — the Money Gradient

_Design spec. Founder-directed 2026-06-24. Flag-gated rollout (`MARKET_SIGNAL_V2`, default OFF)
until validated, then flipped + propagated to all 3 platforms._

---

## 1. Purpose & identity (what we are — and are NOT)

Now TrendIn runs **two parallel movement trackers**, one pattern:

| | Tracks | Dark Matter (early/informed) | Mainstream (broad/confirming) |
|---|---|---|---|
| **Attention Gradient** (live) | where attention is moving | expert/niche communities | mainstream media/platforms |
| **Money Gradient** (v2.0) | where money is moving | congress · insiders · smart-money 13F · quality finance analysts | economic + market APIs |

Both obey the same law: **a Dark-Matter signal is an EARLY, possibly-leading indicator; the
Accuracy Ledger decides — factually, after the fact — whether it actually led.**

**We do:** track money-movement signals; surface direction (IN/OUT) + intensity; state leverage
facts; keep an honest, falsifiable track record (the ledger).
**We do NOT:** recommend buy/sell, guarantee outcomes, or claim to predict prices. We are an
attention- and money-**movement** platform, plus an objective leverage-facts metric — **not** a
financial, legal, or investment advisor (per the disclaimer).

> The distinction that reconciles "no prediction" with "leading indicators": we never *advise* or
> *guarantee*, but our signals MAY be precursors — and the **ledger**, over time, is what
> establishes whether they were. Removing the precursor possibility would gut the moat; we keep it,
> and we *measure* it instead of claiming it.

---

## 2. The Money Gradient — sources by tier (D vs M)

Routing uses the engine's existing `platform_tier` M/D mechanism (same as attention).

### Dark Matter (D) — early / informed money movement (the precursor layer)
- **Congress trades** (QuiverQuant) — members often act on information ahead of the market.
  Routed D (insider-tier), **net flow direction** (inflow/outflow) + breadth (# members).
- **Insider Form-4** (SEC EDGAR) — corporate insiders buying/selling their own stock.
- **Smart-money 13F** (SEC EDGAR, curated funds — `sec_13f_research`) — fund accumulation/trimming.
- **Alpha Vantage insider + 13F-by-ticker** (`av_dark_positioning.py`) — Form-4 insider trades (≥$250K,
  A/D direction) + institutional 13F net flow by ticker. Blended into `positioning_intel` behind
  **`AV_DARKPOS_ENABLED` (default OFF)** — provisional weights, **backtest-before-ship** before flipping.
- **Databento tape microstructure** (`databento_microstructure.py`, HELD-OUT prototype) — block prints
  (≥$250K) + tick-test direction = institutional footprints in the tape (a *different* Dark-Matter angle).
  NVDA cross-validated outflow across all three (filings + AV insider + microstructure). Phase-2: harden
  to full-day (DBN client) + dark-pool venue map, then backtest + flag-gate.
- **Quality finance YouTube** — Meet Kevin et al. **RECLASSIFIED from Stage-5 "Retail Amplify" to
  Dark Matter.** Original macro/market *analysis* by informed independents is an early read, not
  lagging retail noise. (Generic hype channels stay low-tier; the curated quality set is D.)

### Mainstream (M) — broad / confirming market state (the confirmation layer)
- **Economic APIs:** FRED (rates, inflation, employment, credit) — the macro backdrop.
- **System leverage / funding:** OFR STFM (repo volume = leverage building; rates = funding stress).
- **Market data APIs:** Alpha Vantage, Finnhub, FMP — price/volume/valuation (factual market state).
- **Broad positioning:** FINRA short interest (market-wide).

A money signal is strongest when **D leads and M later confirms** — and the ledger logs the lead.

### Leverage & Financial Facts (separate factual dimension — the "bonus")
- Company: debt/equity → `leverage_health` (from real financials; already built).
- System: OFR funding/leverage. Stated as **facts**, never a rating-as-advice.

---

## 3. Scoring (reuse what works; fix routing + language)

Keep the proven primitives; change the inputs, framing, and validation:

- **KEEP:** baseline-relative deviation (`score_component` z-scores vs the item's own history) +
  multi-source corroboration. These are pure measurement — no prediction.
- **CHANGE:** the component routing (above) so D = early/informed money, M = broad market/economy.
- **OUTPUT per instrument/sector/theme:**
  - **Money-Movement (Detection):** intensity of Dark-Matter money flow (0-100, baseline-relative).
  - **Confirmation (Confidence):** Mainstream/market confirmation (0-100).
  - **Flow direction:** INFLOW / OUTFLOW / NEUTRAL (factual).
  - **Leverage facts:** `leverage_health` + raw figures.
  - **Lead:** how far Detection runs ahead of Confirmation — described factually, scored by the
    ledger, NOT presented as a buy-timing.
- **Economy/sector layer:** aggregate per-instrument D-flow into **sector rotation** (money moving
  out of tech → into energy) + overlay macro facts (OFR + FRED).

---

## 4. A SEPARATE Accuracy Ledger — validated by realized PRICE DIRECTION, not Google Trends

**Founder correction (2026-06-24): Google Trends does NOT validate a market signal.** Search
velocity is the right ground truth for ATTENTION (did attention arrive?), but a *money* signal is
validated by what the *market actually did*. So the Money Gradient gets its **own** ledger —
`market_accuracy_ledger.py`, distinct from the attention ledger (`accuracy_ledger_enhanced.py`).

| | Trends ledger (`accuracy_ledger_enhanced`) | **Market-Signal ledger (`market_accuracy_ledger`)** |
|---|---|---|
| Detection | attention moving toward a topic | **money moving IN/OUT of an instrument** (flow + intensity) |
| Ground truth | Google Trends breakout | **realized EOD CLOSE price DIRECTION** — Databento (exchange-direct, primary) cross-checked against FMP (fallback) |
| Verdicts | LED / SAME_DAY / LAGGED / FALSE_POSITIVE | **CONFIRMED / NOT_CONFIRMED / NO_MOVE** (+ lead-time) |

**How it validates (the NVDA example):** detect **OUTFLOW** on NVDA → if NVDA's EOD close
subsequently trends **down** past the move threshold (default ±5%), the detection is **CONFIRMED**
and the **lead time** (days from our detection to the confirming close) is recorded. An **INFLOW**
is CONFIRMED on a move **up**. A move in the *opposite* direction → **NOT_CONFIRMED** (an honest
miss). Flat by the deadline (default 60d) → **NO_MOVE**. `hit_rate = CONFIRMED / (CONFIRMED +
NOT_CONFIRMED + NO_MOVE)` — the misses stay in the denominator.

**This does NOT contradict "no prediction / no advice."** The ledger is a **retrospective accuracy
measurement**, not a forward claim. We never tell a user a price will move; we keep an honest,
falsifiable record of whether *our* detected money flow corresponded to (and preceded) the realized
move — exactly as the attention ledger records whether attention arrived. Measurement of our own
accuracy, never a buy/sell call.

**Integrity:** NO LOOKAHEAD (only closes on/after the detection date; the detection date is when WE
flagged it, and `positioning_intel` reads PUBLIC filings). Forward-only, additive tables, degrades
to `available:false` when `FMP_API_KEY` is absent, flag-gated so only the Money Gradient
(`MARKET_SIGNAL_V2`) records into it. Endpoints: `GET /market/accuracy` (report),
`POST /market/accuracy/sweep` (resolve). The earlier return-prediction backtest
(`dark_positioning_backtest.py`) remains a **footnote**, not a gate — it tested *forward returns /
alpha*, which we do not claim; this ledger tests *directional accuracy of our movement signal*,
which we do.

---

## 5. Language purge (hard requirement)

Remove everywhere in the Risk Gradient + Market Signal: **"before it's priced in," "alpha,"
"early-warning," "leading indicator [as a promise]," "buy/sell," "treat with caution," "not yet
priced in."** Replace with movement + facts + ledger language: "money is moving IN/OUT," "Dark-Matter
money signal detected — the ledger will show whether it led," "leverage is elevated (fact)."

---

## 6. Rollout (safe, phased)

1. **Engine** — Money Gradient scoring behind `MARKET_SIGNAL_V2` (default OFF); v1 stays live.
2. **Sources** — reclassify YouTube/Meet Kevin → D; wire economic/market APIs → M.
3. **Ledger** — money detections → **`market_accuracy_ledger`** (a SEPARATE ledger, validated by
   realized **EOD price direction** via FMP, NOT Google Trends). ✅ built + wired (record at the
   scoring site, sweep on the ledger cadence, `GET /market/accuracy`), flag-gated.
4. **Validate** — confirm the v2 output is sane (flow direction matches filings; the market ledger
   populates + resolves CONFIRMED/NOT_CONFIRMED/NO_MOVE once `FMP_API_KEY` is set + the flag is on).
5. **Flip** `MARKET_SIGNAL_V2=1`; then **propagate to all 3 platforms** (web terminal → desktop
   inherits; mobile) with the new labels (Money Movement / Confirmation / Leverage Facts / flow) and
   the language purge. Maintain 3-platform parity.

> **STATUS: LIVE.** Flag flipped ON (engine v155) and validated 2026-06-25 — 8/8 rows scored
> `model_version=v2`, directional signals correct (NVDA/AAPL/JPM outflow, MM≫MC; macro/micro-caps
> neutral), detections recording, enriched interpretation live. All 3 platforms propagated; both
> accuracy ledgers exposed (Attention/Money toggle). Reversible with `MARKET_SIGNAL_V2=0`. Market
> ledger verdicts resolve forward as price confirms (±5%) or the 60-day window elapses.

---

## 7. Naming map (v1 → v2)

| v1 (predictive framing) | v2 (movement + facts) |
|---|---|
| Detection (leading, "early warning") | **Money Movement** (Dark-Matter flow intensity + direction) |
| Confidence (lagging, "confirmed") | **Market Confirmation** (Mainstream/economic confirmation) |
| Risk Gradient "Stage 5 Retail Amplify" (YouTube) | **Dark Matter** (quality analysts) / low-tier (hype) |
| "before it's priced in / alpha" | "early money-movement signal — ledger-validated" |
| Positioning Concentration | folds into **Money Movement (D)** |
| Dark Positioning (macro funding) | folds into **Leverage Facts** |
