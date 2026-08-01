# ADVISORY BOARD — CRYPTO INFLOW/OUTFLOW DESIGN (the ETF share-flow leg)
**Convened:** 2026-08-01 · **Five archetypes, independent** · on `CRYPTO_FLOW_ANALYSIS_2026-08-01.md`
**Constraint honored throughout: $0 (founder-ordered; all paid providers out of scope).**
**VERDICT: the architecture is APPROVED unanimously — the first crypto money leg any archetype
would defend to a client. Every CONSTANT in it is REJECTED until a proper study, and six
conditions are BLOCKING before the flip.**

## 0. THE HEADLINE FACTS (verified, not quoted)
- On our existing FMP plan, share counts (= AUM/NAV) are derivable for **BTC ×6 (IBIT, FBTC,
  GBTC, ARKB, BITB, HODL), ETH ×4 (ETHA, ETHE, FETH, ETHW), SOL ×3 (BSOL, GSOL, TSOL),
  XRP ×2 (XRPC, TOXR)** — so at $0, four of twelve coins (~90% of tracked cap) can carry a
  genuine two-sided institutional money read. LTC has one fund (below floor); seven coins
  remain honestly structural.
- The founder's external research doc is auth-gated (401) — noted, and superseded: every
  decision-critical claim was re-verified directly, and the $0 directive removes the paid
  providers it surveyed from consideration entirely.

## 1. WHAT THE BOARD REJECTED IN MY DESIGN (adopted; all pre-flip)
1. **The constants are numerology (Challenger).** 0.10%/1.0% came from FOUR days containing
   weekend phantom-zeros, and the 1.0% cap was set at the largest value in the sample —
   accidental spec-shopping. **Adopted method (the arrival-clock precedent): pre-declare the
   target and the FORMULA now, read the numbers off a ≥30-trading-day study.** Per-fund floors:
   `floor_f = max(2×0.005/NAV_f, k×null-p99_f, basket_f/shares_f)`.
2. **Quantization breaks a global floor (Challenger, computed).** NAV-rounding noise alone is
   0.028%/day on IBIT but **0.143% on TSOL — above the proposed floor**; TSOL's creation-basket
   granularity is ~2.3% per unit. A $3M fund would vote on rounding error.
3. **AUM eligibility floor to vote** (Executioner $25M / Economist $50M / Outsider "yes"):
   TSOL snapshots but never votes. Eligibility floors don't feed price into the signal.
4. **Fixed thresholds are the §16a BRIDGE, not the destination (Economist).** Pre-declare both
   forms now: magnitude-scaled fixed vote while CALIBRATING; **robust z (median/MAD) on the
   coin's own aggregate flow** takes over at `MIN_BASELINE_TRUSTWORTHY` — the platform's own
   baseline-relative doctrine, and it absorbs GBTC's secular bleed naturally.
5. **±0.15 kept "unchanged" is unexamined, not conservative (Challenger).** With magnitude
   votes the aggregate is a different instrument; sub-floor handling (0-in-denominator vs
   None-out) gives opposite behavior and must be pre-declared.
6. **The 5-day verdict licenses only the ORIGINAL FIVE tickers.** `ETF_PROXIES` is still
   hard-coded — the ten new funds have zero snapshot history. **Each ticker earns its own
   currency window** (Guardian: BLOCKING; Challenger: "the exact insider mistake, repeated").

## 2. CONDITIONS ADOPTED AS BINDING (by archetype)
- **Guardian:** `_max_votable` counts ETF kinds **iff `CRYPTO_ETF_FLOW=1`** — otherwise SOL/XRP
  read "transient" while the deployed instrument cannot fire (the optimistic false-promise).
  `absence_class` describes the instrument **as deployed**, never as committed. Never add
  below-floor funds (LTCC) to the universe — the shared-COIN crutch would flip LTC on a
  technicality. **Latency stamp:** `flow_basis: "etf_creations"`, `signal_latency_days: 1` on
  every payload and ledger row; lead 0–1 is PARITY — earliness language reserved for lead ≥ 2;
  never reconstruct "when the demand happened." **Spec SHA becomes the crypto ledger cohort's
  `param_version`** — enrollment-gating parameters are experiment-side, and a git timestamp is
  not evidence to hedge-fund counsel.
- **Economist:** name the aggregate honestly — *flow into/out of the REGULATED US funds*,
  never "crypto money" (offshore/on-chain/perps are structurally missing; the bias is toward
  lateness and allocator-selectivity, and the display must not claim otherwise).
  **Pre-register the naive null BEFORE the flip:** null A = sign of the coin's 7-day momentum,
  null B = lagged flow; the ledger reports the flow cohort beside both; the word "signal" is
  earned only by beating null A. Pin ONE daily sampling slot after the NAV strike; deltas over
  trading days only (weekend rows are phantom zeros). Detection timestamp = snapshot capture;
  the judged window starts the NEXT cycle (no lookahead).
- **Executioner:** three stages. **Stage 0 (NOW, dark):** roster derives from `COIN_UNIVERSE`
  `kind=="etf"`; add all 15 proxies so every clock starts — live behavior byte-identical
  (ETFs return None on the insider path). **Stage 1 (post-verdict, flag OFF):**
  `latest_delta` with gap-normalization, >5-day staleness cutoff, ±20%/day discontinuity clamp
  (splits/closures); shadow votes served on `/diag/etf-flow` through the REAL vote function —
  verified same-hour, no 6h wait. **Stage 2 (flip, ~08-10):** gates = old-five verdict PASS +
  ≥5 shadow days on new tickers + sane shadow votes + **`CRYPTO_LEDGER_CLEAN_COHORT_START`
  moved to the flip date in the same config change.** FMP budget: +40 calls/day — non-issue.
  **Decoupled from S7 and from the trend-ledger repair** (separate evidence chains).
- **Outsider:** the missing gate is **reconciliation against the issuers' published daily
  flows** (Farside aggregates them free) for two weeks pre-flip — "the single cheapest
  credibility purchase available." Conveyance: direction in words, dollars rounded hard,
  streak, vs-typical ("about 4× this coin's normal daily flow"); banned user-facing: D-leg,
  Dark Matter, proxy, votes, Δshares, z-score, and the ≈ symbol. Frame coverage as focus:
  *"Institutional flow tracked for BTC · ETH · SOL · XRP — the coins where US spot funds
  exist"*; covered coins above the fold. The empty ledger sells itself: *"Track record begins
  at instrument launch. No hypothetical results."*
- **Guardian (drift):** `venue_diffusion` = covered/total sits inside M — wiring flow jumps
  BTC's covered 1→6 and **mechanically moves Market Confirmation off a D-coverage change**.
  Freeze or recompute it for crypto **BEFORE the flip** (BLOCKING). Display dollars
  (Δshares×NAV) are never persisted anywhere the scorer or ledger reads.

## 3. THE PLAN OF RECORD
- **Stage 0 — TODAY:** roster expansion, dark, `[cold-start-stated]`; every new ticker's
  currency clock starts. (Executed with this collation — see commit.)
- **Stage 1 — after 08-02 verdict:** delta/vote functions + shadow-vote diagnostics +
  reconciliation harness; spec committed with SHA; null pre-registered.
- **Stage 2 — flip (~08-10):** all gates green → `CRYPTO_ETF_FLOW=1` + cohort start moved;
  BTC/ETH/SOL/XRP populate; seven coins keep the structural truth.
- **Later, own §16 passes:** CFTC COT (free) and 13F-of-ETFs via WhaleWisdom (already paid) as
  the credit and accumulation legs; stablecoin issuance as the monetary base — the full
  Friedman & Schwartz aggregate, all at $0.

*Five memos faithfully collated; full texts in the session record. The founder's directive —
no option that increases cost — is satisfied by the entire plan.*
