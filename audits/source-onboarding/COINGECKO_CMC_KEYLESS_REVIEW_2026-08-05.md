# CoinGecko / CoinMarketCap keyless APIs — §16 candidate review (2026-08-05 PT, late)

Founder question: "confirm our data pulls are accurate and that we can actually monitor
money flow" — review of docs.coingecko.com/docs/keyless-public-api and the
CoinMarketCap keyless public API. Review only — NOTHING wired (flag-never-force; the
Gate-4 board rulings are pending).

## The honest headline answers

**1. Can these APIs monitor money flow? NO — and nothing should ever claim they can.**
They provide prices, market caps, exchange trading volume, supply, and (GeckoTerminal /
CMC DEX) on-chain DEX pool/trade data. Exchange `total_volume` is TURNOVER, not net
directional dollars — and the C5/C6 shelf entry (Chairman-ruled 2026-08-05) already wrote
the no-proxy prohibition: **exchange volume ≠ on-chain flow**. Neither API carries ETF
shares outstanding or creations/redemptions, so neither addresses the Gate-4 derived-leg
problem — the issuer-product-pages path from the board review remains the only §16-viable
money-flow fix on the table. GeckoTerminal's DEX trades are genuine on-chain data but
measure DEX trading activity, not net asset flow; as a possible future Dark-Matter
instrument it would be a NEW instrument class (full §16 + §16a cold-start + prereg),
not a drop-in.

**2. Are our current pulls accurate? The live cross-check found one real discrepancy.**
Tested live 2026-08-06 05:10 UTC:

| quantity | CoinGecko | CoinMarketCap | Our engine (FMP-based) |
|---|---|---|---|
| BTC price | $64,896 | $64,920.87 | ~$64,550 implied (network_value ÷ supply) |
| ETH price | $1,913.57 | $1,914.69 | — |
| BTC circulating supply | **20,066,368** | — | **19,972,590** |

- **Price agreement CG↔CMC: 0.04%** (ETH 0.06%) — two independent aggregators this tight
  proves a referee band is feasible. Our implied BTC price sits ~0.55% below both —
  plausibly the daily FMP strike timing, not alarming alone.
- **The finding: our BTC circulating supply is 93,778 BTC (0.47%) BELOW CoinGecko's.**
  At post-halving issuance (~450 BTC/day) that gap equals **~208 days ≈ 7 months** of
  issuance — consistent with EITHER a ~7-month-stale supply basis inside FMP OR the same
  two-field-quotient desync defect the Challenger just identified in the ETF leg (our
  supply figure derives from FMP marketCap ÷ price, exactly the AUM ÷ NAV construction
  class). Note the display irony: `supply_as_of: 2026-08-05` stamps the number fresh
  while the underlying figure appears months old — the "stale wearing a fresh badge"
  class again. Effect today is small (band stays mega; pct_of_max 95.1% vs a
  CoinGecko-based 95.5%) but it is a REAL accuracy defect in served `supply_facts`.

## §16 five-gate assessment — for the proposed role only

Proposed role: **held-out REFEREE / cross-check** (like `referee_wikipedia` and Farside)
— never a scoring input. This satisfies §15's no-aggregators rule, which governs scoring
inputs, not verifiers.

1. **TYPE** — market reference data (price / market cap / supply / volume), aggregated
   from exchanges. CG adds GeckoTerminal on-chain DEX; CMC adds a DEX API + fear/greed.
2. **ENGINE** — held-out referee only: (i) a **price-freshness referee** on the FMP coin
   price (M leg): alarm when FMP diverges >1% from the CG/CMC median or goes stale;
   (ii) a **supply-facts cross-check** on C1/C2 (`supply_facts`): alarm on >0.5%
   circulating-supply divergence. NEVER a Money-Movement input; NEVER a volume-as-flow
   proxy (written prohibition).
3. **FORMAT** — clean JSON; real freshness stamps (`last_updated_at` unix / ISO
   `last_updated`, observed 1–2 min fresh); dates canonicalizable via `to_iso_date`.
4. **CURRENCY + ACCESS** — proven live: HTTP 200 keyless, both APIs, data 1–2 min fresh.
   Limits (from official docs): CG keyless **~10–30 calls/min** (GeckoTerminal ~10/min),
   "not suitable for production workloads or scheduled polling"; CMC keyless = shared
   IP-based pool, 429 + backoff, free key raises limits. A referee needs only a handful
   of calls per day — well inside keyless limits — but BOTH docs give no stability
   guarantee, so any adapter must fail CLOSED to "referee unavailable," never block or
   guess. If ever polled on a schedule, register the free keys (still $0) per the docs'
   own guidance.
5. **TEST → LINK → DEPLOY** — today's live pass WAS the test (recorded above). LINK is
   NOT done and awaits the Chairman — held-out referee wiring is not score-affecting, but
   it belongs inside the same A2/hardening batch the board just proposed (the Economist's
   SOURCE_STALE alarm + "staleness-as-null" CURRENCY test are exactly this shape).

## Recommendation to the Chairman (not executed)

1. Onboard CoinGecko keyless (CMC as the second opinion) as a **held-out price + supply
   referee** with divergence/staleness alarms in the monitor fleet — it directly answers
   "confirm our data pulls are accurate," continuously, for $0.
2. Open a defect for the **FMP-derived BTC circulating-supply staleness** in
   `supply_facts` (C1/C2): either re-source supply from a fresher field/vendor or have
   the referee stamp an honest divergence caveat. Verify-before-fix applies — confirm
   the mechanism (stale vendor field vs quotient desync) before any code change.
3. Do NOT represent any of this as money-flow capability. Money flow remains: ETF
   creations/redemptions (issuer pages, per the Gate-4 board) + true on-chain flow
   (Glassnode/Nansen-class, the known future paid gap). GeckoTerminal DEX data may
   someday be a D-side candidate — full prereg required.
