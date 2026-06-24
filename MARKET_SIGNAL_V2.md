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

## 4. The Accuracy Ledger is the validator (NOT a price backtest)

Money-Dark-Matter detections are logged like attention detections. The ledger later asks the
**factual** question: did broad money movement and/or **attention arrival** follow, and how many
days after? Verdicts: LED / SAME_DAY / LAGGED / FALSE_POSITIVE; lead-time recorded.

- Ground truth for "money movement arrived" = subsequent Mainstream(M) confirmation (broad flow /
  short-interest shift / volume) **and/or** the name's **attention breakout** (unifying the two
  Gradients: money dark matter as a precursor to attention).
- The earlier return-prediction backtest is a **footnote**, not a gate — it tested *price*, which we
  do not claim. The ledger tests *movement*, which we do.

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
3. **Ledger** — money detections logged + validated.
4. **Validate** — confirm the v2 output is sane (flow direction matches filings; ledger populating).
5. **Flip** `MARKET_SIGNAL_V2=1`; then **propagate to all 3 platforms** (web terminal → desktop
   inherits; mobile) with the new labels (Money Movement / Confirmation / Leverage Facts / flow) and
   the language purge. Maintain 3-platform parity.

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
