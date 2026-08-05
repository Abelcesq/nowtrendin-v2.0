# CRYPTO ETF SHARE-FLOW LEG — PRE-DECLARED SPEC v1
**Committed BEFORE the flag is flipped. The git timestamp of this file is the
pre-declaration; its SHA becomes the crypto ledger cohort's `param_version`.**
**Date:** 2026-08-02 · **Flag:** `CRYPTO_ETF_FLOW` (default OFF)

## 1. WHAT IS MEASURED, NAMED HONESTLY

Net **creations and redemptions** of US spot crypto ETPs, derived as
`shares = AUM ÷ NAV` and read as the **day-over-day change in share count**.

This is the flow into and out of the **regulated US fund wrapper** — *not* "crypto money."
Structurally missing, and stated so it can never be implied otherwise: offshore spot volume,
on-chain/stablecoin issuance, and perpetual-futures leverage (where Kindleberger's credit
expansion actually lives in crypto). The known bias is therefore toward **lateness and
allocator-selectivity**: it detects the regulated-institution wave and under-detects
retail/leveraged/offshore episodes.

**SHARES, NEVER AUM.** `AUM = shares × NAV` and NAV tracks the coin, so an AUM-delta would be
driven by the same price series that drives Market Confirmation — a circular metric, banned.
Dividing by NAV removes the price. AUM is retained ONLY as an eligibility test, never a signal.

## 2. THE VOTE (v1 — the §16a CALIBRATING BRIDGE, explicitly not the destination)

Per fund, once per cycle, from recorded snapshots only (no network call on the serve path):

| Condition | Result |
|---|---|
| AUM < `ETF_VOTE_MIN_AUM` ($50M) | **None — ineligible.** A micro-fund's creation basket is a large % of its shares; it would vote on quantization. |
| No 2 distinct snapshot days | None — no read |
| Gap > 5 days | None — **stale**; a stale read must never pass as today's flow |
| \|Δ\| > 20%/day | None — **discontinuity** (reverse split / closure / provider garbage) |
| Gap 2–5 days | Δ is **per-day normalized** (weekend/missed cycle) |
| \|Δ\| < `ETF_VOTE_FLOOR_PCT` (0.10%/day) | **0.0, IN the denominator** — a measured quiet day is information, never absence |
| otherwise | `sign(Δ) × min(1, \|Δ\| ÷ ETF_VOTE_SCALE_PCT)` — magnitude-scaled, never a binary latch |

Coin aggregate, floor, and `±0.15` net threshold are **unchanged this cohort** (one change at
a time). Insider votes (MSTR/COIN) remain under the dominance rule.

## 3. WHAT THE BOARD REJECTED, AND THE COMMITTED REPLACEMENT

The constants above were derived from a 4-day window containing weekend phantom-zeros, and the
1.0% scale sat at the largest value in that sample — accidental spec-shopping. They ship as a
**bridge only**. Pre-declared replacement, committed here BEFORE any data is examined:

1. **Study:** after **≥30 trading days** of snapshots, compute per-fund null distributions.
2. **Per-fund floor formula (fixed now, numbers read off the study):**
   `floor_f = max( 2 × 0.005 / NAV_f , k × null_p99_f , basket_f / shares_f )`
   — the three terms are NAV-rounding noise, the empirical null, and creation-basket
   granularity. `k = 1.0`.
3. **Destination form:** a **robust z (median/MAD)** on the coin's own aggregate flow, taking
   over automatically at `MIN_BASELINE_TRUSTWORTHY` cycles of that coin's flow history —
   consistent with the platform's baseline-relative doctrine, and it absorbs GBTC's secular
   redemption trend naturally (its baseline *is* negative; deviation is the information).
4. Any change to §2 or §3 mints a **new spec SHA and a new ledger cohort**. Quiet tuning of
   the bridge constants instead of running the study is the forbidden path.

## 4. THE NAIVE NULL — PRE-REGISTERED BEFORE THE FLIP

US ETF flows are notoriously price-chasing, so the binding null is not randomness:

- **Null A — the coin's own 7-day momentum sign.**
- **Null B — lagged flow (persistence).**

The crypto ledger reports the flow cohort's confirmed-direction rate **beside both nulls**.
Until the flow cohort beats **Null A** at n ≥ `CRYPTO_MIN_PUBLISH_N` (30), the word **"signal"
is not earned** — the surface says "measured flow," and no rate is published.

## 5. LATENCY AND LEAD — WHAT MAY NEVER BE CLAIMED

A creation is money **arriving**, observed at **T+1**. Every payload and every ledger row
carries `flow_basis: "etf_creations"` and `signal_latency_days: 1`.

- **Lead 0–1 is PARITY, not prescience.**
- Earliness language is reserved for **lead ≥ 2**, reported separately.
- The latency is **never** subtracted to reconstruct "when the demand happened."

## 6. SAMPLING RULE

NAV strikes once daily (~4pm ET); snapshots are idempotent per `(ticker, UTC date)`, first
write wins. Deltas are computed over **distinct snapshot dates**, gap-normalized. Known and
stated: a UTC-date label can sit one day after the NAV strike it reflects — a ±1-day smear,
disclosed rather than silently carried. Detection timestamp = snapshot capture; the judged
price window starts the **next** cycle (no lookahead).

## 7. COVERAGE, STATED PLAINLY

Reachable at $0: **BTC, ETH, SOL, XRP** (funds ≥ the eligibility floor). LTC has one fund
below the floor. The remaining seven coins have **no US spot fund** and therefore no
institutional fund flow to measure — they keep the structural-absence text, and no path
relabels them optimistically.

## 8. FLIP PRECONDITIONS (all must hold)

1. §16 gate-4 **CURRENCY passes** for the original five — **PASSED 2026-08-02** (4/15 funds
   show real day-over-day movement; the other ten had ≤2 observations at verdict time).
2. **≥5 snapshot days on each new ticker** before it may vote — each fund earns its own window.
3. **Shadow votes sane** on `/diag/etf-flow` (no daily discontinuity stamps; GBTC not pinned).
4. **Reconciliation** of derived Δshares against issuers' published daily flows.
5. `venue_diffusion` frozen or recomputed for crypto — coverage jumping 1→6 must not
   mechanically move Market Confirmation.
6. `CRYPTO_LEDGER_CLEAN_COHORT_START` moved to the flip date **in the same config change**.
