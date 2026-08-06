# EVIDENCE PACK — Incorporating the Founder's Book Canon: Market Cap, Crypto, Investing
**Date:** 2026-08-05 PT · **Convened at the Chairman's order:** "have the advisory board
implement and incorporate the principles in the books provided regarding market cap, crypto
and investing."

**What is being decided:** (a) judge the A1 implementation (committed `75e0726`, flag-gated
dark) as the FIRST incorporation of these principles; (b) recommend further CONCRETE
incorporations of the canon into the crypto/market scoring, displays, and agents — each
respecting $0 marginal cost, no circularity, measurement-not-advice, flag-never-force, and
backtest-before-ship for anything score-affecting.

## 1. THE CANON (what the founder supplied; verified excerpts read this session)

**Burniske & Tatar, *Cryptoassets*** (publisher summary, read in full): crypto market cap =
"network value" (coin price × supply); an asset's price decomposes into UTILITY value
(current use) vs SPECULATIVE value (expected future use) — young assets are speculation-
dominated and the ratio shifts with maturity; valuation metric offered: network value ÷
daily on-chain transaction dollar volume (the NVT shape); due diligence = supply/issuance
model, developer commitment, decentralization, user adoption; crowd manias recur in every
asset class (fixation on highs, "this time is different", cornering, misleading issuers).

**Antony Lewis, *The Basics of Bitcoins and Blockchains*** (399-pp PDF; supply + bubble
chapters read): issuance mechanics are PER-ASSET — BTC's fixed 21M halving schedule vs
ETH's pre-mine (~72M) + block rewards (5→3 ETH, Byzantium) + uncle rewards, with supply
policy CHANGEABLE by protocol upgrade; bubble history (2010/2011/2013/2014) shows 80%
drawdowns driven by narratives ("all it takes to move markets is for people to believe
stories"); ICO treasury/vesting mechanics distort effective float.

**Founder's market-cap brief (verbatim supplied):** equities cap = price × shares
outstanding with size bands (large ≥$10B / mid $2–10B / small <$2B mapping to volatility &
liquidity risk); crypto cap = price × CIRCULATING supply, with FDV (max supply) as the
alternative denominator, lost/burned coins overstating cap, and REALIZED cap (price at last
on-chain move) as the corrective; money-market funds have NO market cap — they are measured
by AUM at a ~$1.00 NAV. Core doctrine: **each asset class is sized by its own metric; each
coin and each ETF must be scored separately.**

**Graham, *The Intelligent Investor*** (founder-cited): price is not value; Mr. Market's
quotes are opportunities to measure, not instructions; margin of safety; discipline against
narrative. (Maps to the platform's existing measurement-not-advice + baseline-relative
doctrine.)

## 2. THE FIRST INCORPORATION — A1, COMMITTED THIS SESSION (75e0726, dark, flag-gated)

- **Per-asset metric doctrine applied:** funds sized by AUM (their correct metric), coins
  by their own price series; each fund tracked separately (per-fund votes + shadow votes);
  each coin scored separately against its own baseline (pre-existing doctrine, now
  reinforced).
- **AUM-relative fund weights:** within a coin's fund class, votes sized by AUM share; the
  class keeps the coin's configured weight budget. Price cancels in relative weights (all
  funds of one coin track the same coin) — not circular. Dominance proven in test: an $80B
  fund's −0.8%/day redemption outvotes a $60M fund's +0.9%/day creation (a naive average
  reads the wrong sign).
- **Venue classes:** diffusion + intensity coverage measured over venue KINDS
  (insider-equity / etf-flow), never instrument count.
- **4h strike capture:** every pull recorded as an observation; the daily flow row updates
  only on a genuine NAV strike, never on AUM (price) wiggle; honesty boundary pre-declared
  (six looks/day at at most ONE flow point — timeliness, never six data points).
- **Latency stamps** (flow_basis / signal_latency_days=1) through payload + both crypto
  ledger tables. **Continuous daily reconciliation** vs issuer-published flows with the
  tolerance band pre-declared (±25% or ±$20M, direction mandatory on material days) —
  harness build is the next task.
- Full text: `audits/board/CRYPTO_FLOW_SPEC_A1_AMENDMENT_2026-08-05.md`.

## 3. CANDIDATE FURTHER INCORPORATIONS (the board is asked to judge / rank / extend)

C1. **Coin size bands (display + context):** classify each coin large/mid/small by
    CIRCULATING-supply cap (CoinGecko-style bands), shown on the crypto detail with the
    volatility/liquidity meaning stated — the equity size-band doctrine applied to coins.
    Display-only; FMP already serves the inputs at $0.
C2. **Circulating-vs-FDV disclosure:** per coin, show circulating cap beside FDV and the
    % of max supply outstanding (BTC ~19.7M/21M vs a low-float/high-FDV alt) — the
    dilution-overhang fact institutional buyers check first. Display-only, $0.
C3. **Supply-schedule awareness:** stamp each coin's issuance model (fixed-schedule /
    policy-changeable / pre-mined share) as reference metadata on the detail page —
    straight from Lewis; prevents treating BTC and ETH supply semantics as identical.
C4. **Utility-vs-speculative framing (Burniske):** where the attention engine already
    tracks the coin's TOPIC, display attention-heat beside measured fund flow — the
    platform's own two axes (speculative attention vs money arriving) — WITHOUT blending
    them into one number (no circularity; the divergence-detector design already queued).
C5. **NVT-shaped metric:** network value ÷ transaction volume needs on-chain data —
    NOT reachable at $0 today (Glassnode/Nansen are paid). Candidate for the deferred
    shelf with a written trigger (a free/licensed on-chain volume source passing §16).
C6. **Realized-cap corrective:** same $0 blocker (on-chain data). Shelf with trigger.
C7. **Graham margin-of-safety language:** display discipline — tier/flow copy states what
    is MEASURED and its error bars (the disclosed smear, latency, coverage), never a
    target or a recommendation. Largely enforced already (D1/D2, §17); the ask is a sweep
    of crypto copy against it.
C8. **Mania-signature awareness (Kindleberger/Lewis bubbles):** the already-queued
    attention-vs-flow divergence detector IS this canon's instrument; the board is asked
    to rank it against C1–C4.

## 4. CONSTRAINTS (unchanged, binding)

$0 marginal cost (founder directive). No circularity (N never feeds scores; AUM never a
signal, only size/eligibility). Measurement, not advice. Flag-never-force; score-affecting
changes require design + backtest before ship. Ledgers held-out, never deleted, n≥30
publication floors. Reference: CLAUDE.md §13–§17, CRYPTO_FLOW_SPEC v1 + A1 amendment.
