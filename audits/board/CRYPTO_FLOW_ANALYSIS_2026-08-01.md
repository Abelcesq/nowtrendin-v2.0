# CRYPTO INFLOW/OUTFLOW — RESEARCH, ANALYSIS & PROPOSED DESIGN (pre-Board)
**Date:** 2026-08-01 · **Author:** the Chairman's agent · **Constraint (founder-ordered):
$0 — no option that increases cost.** Board convenes on this document.

## 0. WHAT THE FOUNDER ASKED, AND WHAT THE CONTEXT DEMANDS

The standing brief (put before the Board verbatim three times now): identify signals of major
money movement BEFORE it goes mainstream, using the footprints institutions cannot avoid
leaving in public data — cluster buying, dark-pool/volume forensics, congressional alignment,
and (Paulson's lesson) capped-downside instruments read from long, honest series. The crypto
translation of "dark pools + volume forensics" is NOT insider filings — it is **fund flow**:
creations/redemptions of the spot ETPs where institutional crypto allocation actually happens.

A founder-run external research task (Claude chat) surveyed nine paid whale-flow providers and
the regulated-data alternatives. Its result doc is auth-gated (fetch returned 401), so every
decision-critical claim below was **re-verified directly** — against our own paid provider and
the open web — rather than quoted. The founder's cost directive supersedes that brief's
$150/mo headroom: **paid providers (Whale Alert, CryptoQuant, Glassnode, Nansen, Arkham,
IntoTheBlock, Coinglass, Amberdata, Kaiko) are OUT OF SCOPE entirely.**

## 1. CURRENT SYSTEM — measured, not recalled

**The read today:** per-proxy insider votes → weighted net → `inflow if net > +0.15, outflow
if net < −0.15` → gate requires ≥2 voting proxies → tier/flow/lead all derive from it.
**Live state:** all 12 coins `money_data_absent`; 11 structurally unreachable (ETF proxies
file no Form 4s); the one historical vote (MSTR) was retired by the dominance fix (v301:
buying must exceed selling; MSTR was $0.998M buys vs $22.1M sells). **On the live path the
instrument cannot emit an outflow at all** (votes ∈ {None, +1}) — Board-documented.

**Evidence collector (running since 2026-07-29):** `etf_flow.snapshot()` records
`shares = AUM/NAV` per ETF per day. 4 days observed; **movement is real** — FBTC −1.37%
day-over-day (~$140M redemption), IBIT and ETHA also moving. Formal 5-day CURRENCY verdict
expected 2026-08-02.

## 2. NEW VERIFIED FACTS (2026-08-01, tested on OUR paid FMP plan — not web claims)

US spot ETPs now exist well beyond BTC/ETH, and **our existing subscription serves AUM+NAV
(⇒ share count) for them**:

| Coin | Votable ETF proxies verified on our plan | Floor (≥2)? |
|---|---|---|
| BTC | IBIT, FBTC, GBTC, **ARKB, BITB, HODL** (6) | ✅ |
| ETH | ETHA, ETHE, **FETH, ETHW** (4) | ✅ |
| **SOL** | **BSOL ($588M), GSOL ($95M), TSOL** (3) | ✅ **new** |
| **XRP** | **XRPC ($272M), TOXR ($124M)** (2) | ✅ **new** |
| LTC | LTCC ($5.7M) (1) | ❌ below floor |
| DOGE, ADA, AVAX, LINK, DOT, BNB, BCH | none found on our plan | ❌ structural |

**Consequence: at $0, a genuine two-sided institutional money read is buildable for 4 of 12
coins — BTC, ETH, SOL, XRP — which are the overwhelming majority of tracked market cap.**
Seven (+LTC borderline) remain honestly absent, as the page already discloses per coin.

**Also $0 and regulated, for a later phase (NOT this build):** CFTC Commitment-of-Traders for
CME BTC/ETH futures (weekly leveraged-funds/asset-manager positioning; free, official) and
13F holdings of the spot ETFs via WhaleWisdom (already paid; quarterly institutional
accumulation — the direct crypto analogue of the 13F leg the equity engine already trusts).
Both are §16 onboarding candidates, each needing its own five-gate pass.

## 3. PROPOSED DESIGN (what the Board is asked to tear apart)

**D-leg vote per ETF (pre-declared, inside a written spec BEFORE any flip — no tuning after
looking):**
- Signal = day-over-day **share-count** delta (never AUM; AUM = shares×NAV is circular with M).
- **Materiality floor: |Δshares| ≥ 0.10% per day** — proposed from the 4-day evidence where
  real events read 0.29–1.37% and noise reads 0.00–0.05%; the Board should stress this number.
- Vote = sign(Δ) × min(1, |Δ%| / 1.0%) — magnitude-scaled, capped at 1.0 (a 1%/day share-count
  change is a very large institutional day), NOT the binary latch that broke the insider vote.
- Coin aggregate = weight-averaged votes (existing weights); keep `±0.15` net threshold and the
  ≥2-proxy floor UNCHANGED this cohort (change one thing at a time).
- Insider votes (MSTR/COIN) remain in the mix under the dominance rule — rare but legitimate.
- **Cold start per §16a:** components enter CALIBRATING; no tier until `MIN_BASELINE_TRUSTWORTHY`
  cycles of the coin's OWN flow history accrue; degenerate/rail stamps inherited from S5/S6.
- Flag `CRYPTO_ETF_FLOW`, default OFF; flip only after the 5-day CURRENCY verdict passes AND
  the spec above is committed (the git timestamp is the pre-declaration).

**Conveyance (what the user sees):**
- Money Movement number + flow chip for BTC/ETH/SOL/XRP once calibrated; the other coins keep
  the structural-absence text already live.
- Per-coin detail: plain-English flow line — *"Net creations across N funds ≈ $X over the last
  day/week"* — dollars derived as Δshares × NAV *for display only*, clearly labelled derived.
- Ledger: crypto accuracy ledger begins enrolling ONLY flow-driven detections (clean cohort
  start = the flip date; n≥30 floor already enforced; `enrollment_possible` becomes true).
- Jargon rule (Outsider standing order): "money into/out of the funds", never "D-leg/venue
  diffusion" user-facing.

**Monitoring (how we know it's alive and honest — all existing machinery, $0):**
- `etf_flow` gets a `collector_health` row with `min_distinct` = floor(votable proxies × 0.6)
  — the dead-parser signature detector, applied on day one, not after a 30-day corpse.
- `/diag/etf-flow` stays as the currency/coverage evidence endpoint; snapshot gaps show as
  missing days there and in the health row.
- Stale-payload census (S6) picks up any coin serving a pre-guard payload.
- The reachability test (`_max_votable`) is updated in the same commit that adds proxies, so
  `absence_class` flips from structural → transient for SOL/XRP truthfully.

## 4. QUESTIONS THE BOARD MUST RULE ON
1. Is the **0.10%/day materiality floor** and the magnitude-scaled vote defensible, or does it
   need a different form (z-score vs own history? rolling window?) — remembering the insider
   vote failed precisely because it was an unscaled latch.
2. Is Δshares once per 6h cycle (our cadence) a faithful daily-flow read, or does timing
   (NAV strike vs our snapshot hour) introduce a bias the spec must state?
3. Does GBTC (chronic redeemer since 2024) need special handling, or does baseline-relative
   scoring absorb its secular outflow naturally?
4. SOL/XRP funds are young and small ($3M–$588M): does §16a CALIBRATING suffice, or do the
   smallest (TSOL $3M) need an AUM floor to vote at all?
5. Sequencing vs the trend-ledger repair and S7 — and whether COT/13F onboarding starts now
   (held-out) or waits.

*Everything in §1–§2 verified this session against live systems or our own paid provider; the
external research doc noted, inaccessible, and superseded on cost grounds.*
