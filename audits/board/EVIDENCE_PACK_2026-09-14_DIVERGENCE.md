# EVIDENCE PACK — tracking DIVERGENCE with mania-independent instruments — 2026-09-14

**Chairman's question (follow-up to `BOARD_crypto-money_2026-09-14.md`, prompted by the
Economist's memo):** *"Is it possible to track 'divergence', and what tracking systems can
we implement that are measurable and independent from the 'mania'?"*

## What "divergence" meant in the Economist's memo (the idea under review)

Funding-rate level is largely a monotone function of recent price momentum — crowding
follows price, so the LEVEL is mostly already inside M (Malkiel's null). The incremental
information is the **divergence between the credit series and the price series**:
- **Distress**: leverage/credit expanding (OI↑ or flat, funding still positive) while
  price stops confirming (flat/rolling over) — Kindleberger's phase the price alone
  reads wrong.
- **Deleveraging**: OI collapsing without a proportional price move.
- Phase classification proposed: expansion / euphoria / distress / deleveraging; only
  distress + deleveraging judged worth serving (the states M mis-reads).

## The precise framing seats must engage (the crux)

Divergence is a RELATION between two series. One leg is price/attention — **that leg IS
the mania**; it cannot be independent and does not need to be. The independence
requirement therefore lands entirely on the **credit/positioning leg**: it must be
measured through a channel the mania cannot mechanically move. Working taxonomy for
seats to test, amend, or reject:
- **Prices are mania-coupled** (funding rate = derived from perp-spot basis; USD-notional
  OI = quantity × price; AUM = shares × price). The Guardian's round-1 objection:
  predictor-derived-from-price scored against a price-verdict ledger is circular.
- **Quantities are candidates for independence** (coin-denominated ΔOI = contract counts;
  ETF **share** counts from issuer pages; on-chain transaction/address counts; CFTC COT
  reported positions). A quantity can still be mania-CORRELATED (people buy in manias) —
  the question is whether the mania can move the READING without the underlying quantity
  changing. Seats: is that the right independence criterion, and what test proves a leg
  passes it (orthogonalization vs momentum? instrument-error analysis? channel audit)?

## Instrument inventory (state per the crypto round, all code-verified there)

| Leg candidate | Kind | Independence claim to test | State |
|---|---|---|---|
| Coin-denominated ΔOI (CoinAPI, Binance perps) | quantity (contracts) | count changes only when positions open/close; price moves don't change it | collecting daily, held-out, ~35d, 12/12, $5/mo; single venue; K7 docstring misstates estimand; K8 MNAR baseline risk |
| Funding rate (same) | price of leverage | WEAK — derived from perp-spot basis (mania-coupled by construction) | same collector |
| CFTC COT (in `crypto_flow_probability_agent`, disabled) | regulated weekly filings | strong channel independence (CFTC, not an exchange mark); BTC/ETH CME only; weekly, T+3 | pre-wired, off |
| ETF share counts (issuer pages, dark) | quantity (shares outstanding) | shares change only at creation/redemption — literal primary flow; shares-never-AUM already ruled | built dark, Gate-4 blocked (`pass_comparisons=0`), 4/12 |
| On-chain activity (Coinmetrics, 9/12, $0) | quantity (tx/address counts) | fully market-independent channel — but measures ACTIVITY not credit (round-1: never money-class) | collecting, held-out |
| Stablecoin net issuance | quantity (supply) | issuer attestations/on-chain mints — candidate the round-1 Guardian named as currently unmeasured | NOT built; seats may assess |
| Equity analogue: the platform already SERVES a divergence primitive — the Trends GAP column (Detection − Confidence) and the market D-vs-M framing | — | product-coherence note: "divergence" extends an existing primitive, not a new concept | live |

## Constraints in force (from the standing rulings — do not re-litigate)

Never labeled "money movement"; prereg sealed BEFORE any correlation (spec-file SHA =
param_version); ≥90 daily obs and rights evidence before display (round-2 convergent
plan); enrollment invariance — a divergence signal reaches any ledger only under a new
`flow_basis` + cohort boundary; §16 five gates (+ the rights gate the Chairman is asked
to add); §16a staging; $700/mo cap; held-out firewall (and K4: graduation mechanics
undefined — a divergence system must state HOW its legs graduate); sign must be able to
go negative (07-29 sign-degeneracy); K9: the crypto ledger clean cohort is n=0 — any
validation target must be stated honestly.

## Items for per-seat verdicts

- **D1 — Is divergence trackable?** Give the operational definition you would sign:
  exact series pair(s), transformation, window, and the phase classifier (if any) —
  or reject the construct as untrackable/unfalsifiable.
- **D2 — Which legs qualify as mania-independent?** Rank the inventory (and any leg you
  add). State the independence criterion precisely and the TEST that demonstrates a leg
  passes (this is the Chairman's core question — "measurable and independent").
- **D3 — The tracking SYSTEM.** Concrete implementable design within constraints:
  collection cadence + storage, held-out staging, where the divergence computation
  lives, how phases are classified without peeking at outcomes, what the site displays
  at each §16a stage, and cost. Reuse what exists; name every new build.
- **D4 — Scoring + publication.** How a divergence claim is sealed, what resolves it,
  what rate may ever be published, and how it feeds (or is fenced from) the ledgers.

**Chairman = the founder. Memos inform; the founder rules.**
