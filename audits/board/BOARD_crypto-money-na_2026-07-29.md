# ADVISORY BOARD — WHY CRYPTO "MONEY MOVEMENT" IS n/a
**Convened:** 2026-07-29 · **Five archetypes, independent** · engine **v298**
**VERDICT: UNANIMOUS REJECT of the insider-on-proxy design as a crypto money estimand.**
The absence machinery is working perfectly. The instrument behind it cannot fire.

---

## 0. THE ANSWER, IN ONE PARAGRAPH

Crypto Money Movement reads n/a because the money leg infers crypto flow from **insider Form-4
filings on crypto-exposure equities** — and **five of the seven proxies (IBIT, FBTC, GBTC, ETHA,
ETHE) are ETFs and trusts, which have no insiders and therefore no Form-4 filings, ever.** Only
MSTR and COIN can emit the signal being read. The gate requires ≥2 voting proxies. So a money
read is reachable **only for BTC**, and only when MSTR *and* COIN both register insider buying
at the same time. This is not a data outage. It is the design.

## 1. CORRECTIONS TO MY OWN PACK (all re-verified)

| My claim | Truth |
|---|---|
| "10 COIN-only coins are structurally absent" | **11 of 12.** ETH also. It has `total=3` so it never trips `"thin"`, but its proxies are ETHA + ETHE (trusts, no insiders) + COIN — max reachable `covered = 1`, below the floor of 2. Different clause, identical outcome (Challenger, Guardian). |
| "the insider-buying-only rule is CORRECT" | **Correct about selling, wrong about buying — and that error is the entire content of the one live vote.** `signal = "accumulation" if buy_usd >= MIN_USD` — **`sell_usd` is not in the expression.** VERIFIED. A single $250K purchase anywhere in a 90-day window latches a full-strength **+1.0** vote against MSTR's **−$21.8M** of net selling. Unweighted: $250K and $250M both yield 1.0. |
| implied the instrument reads direction | **It is SIGN-DEGENERATE.** With 13F off, `_proxy_vote` can return only `None` or `+1.0`, so `net ≡ +1.0` and **`flow` is always `"inflow"`. The instrument cannot emit "outflow." Ever.** (Challenger, Economist) |

## 2. THE ESTIMAND IS NOT IDENTIFIED (Economist, Outsider — market expertise)

Beyond the plumbing, the Board rejects the premise:

- **MSTR insider flow is not a bitcoin signal.** Strategy buys bitcoin by issuing stock and
  convertibles — an **8-K/ATM event, not a Form 4**. Form 4 at MSTR is option exercises and
  10b5-1 sales, i.e. tax planning. *"The proxy is attached to the right company through the
  wrong filing."* Insider **buying** at MSTR is a bet on the equity's premium to NAV (mNAV),
  which frequently moves **opposite** to bitcoin.
- **COIN is a second-derivative read** on exchange fee revenue, RSU-heavy on the sell side.
- **BNB's only proxy is COIN — and Coinbase does not list BNB in the US.** A proxy with no
  economic link to the asset (Outsider).
- Ten alts share **one** COIN vote: if it ever fired, all ten would print the *same number* under
  ten coin names — *"the same number wearing twelve hats."*

**Two contamination findings nobody had raised:**
- **`signal_freshness` is 25% of Money Movement and is computed `0.8 if price_avail else 0.3`** —
  VERIFIED. A quarter of the "money" score is driven by whether the **price** feed answered.
- **`venue_diffusion` (25% of Market Confirmation) = `proxies_covered/total` = 0** — so the one
  populated column, M, is itself contaminated by D's absence.

## 3. WHAT THE ABSENCE IS HIDING (Challenger — the day it fires)

If MSTR and COIN ever both latch: intensity 70 → z = +2.0 against a floor-stdev baseline →
**Money Movement ≈ 63/100, stamped `baseline_relative: true` (the measured badge), flow
"inflow," interpretation "money may be moving IN"** — and the ledger enrols it as a *clean-cohort*
claim. **The absence is currently protecting the user from a 63 that would be indefensible.**

## 4. THE LEDGER (unanimous)

`record_from_serve` guards on `money_data_absent`, `thin`, and `covered < 2` — so the crypto
ledger **can never enrol a row**. It is not broken; it is *correctly starved*. Its one visible
row (BTC, 2026-06-26, CONFIRMED) predates `clean_cohort_start` and is self-labelled
dead-parser-era. **Obligation:** it may never be cited as validation, must publish its
denominator as explicitly 0, and must be excluded from any aggregate accuracy figure. *"An empty
ledger listed beside two populated ones reads as 'three ledgers' and is a misstatement by
juxtaposition"* (Guardian).

## 5. THE PRINCIPLE (Guardian) — and a gap in §16a

> **Absence is transient only if the instrument, exactly as built, has a reachable state in which
> it emits a value. If producing a read requires changing the source set, the gate, or the vote
> rule, the absence is a design verdict, not a data condition — and calling it "not yet" is a
> claim about the future the mechanism cannot underwrite.**

§16a assumed absence is a cold-start condition **time** cures; this one only **engineering** can
cure, and the two are indistinguishable from outside. **Proposed §16a stage 0 — REACHABILITY:**
before a universe ships, compute `max_votable_proxies` (sources whose *type* can ever emit the
signal being read) and compare against the gate. If `max < floor`, the instrument is unreachable
at birth. The `[cold-start-stated]` hook today accepts a posture that is never satisfiable.

## 6. RULINGS

| Fix | Verdict |
|---|---|
| **Copy/disclosure fix — TODAY, $0** | **UNANIMOUS SHIP.** "not **yet** available" is a promise the mechanism cannot keep. |
| **Retire Money Movement column for the 11 unreachable coins** (§17: omit, never render empty) | SHIP (Guardian, Challenger, Executioner) |
| **Fix the `accumulation` test** — require dominance (`buy_usd > sell_usd`), scale the vote, shorten the 90d latch | SHIP, $0, one line (Challenger) |
| **ETF share-count / creation-redemption flow** as the real institutional signal | **SHIP-LATER, flag-gated, §16 five gates.** ⚠ **Use SHARE COUNT, never AUM** — `AUM = shares × NAV` and NAV tracks the coin, so an AUM-delta D would be **circular with M** (Executioner). Fixes **BTC + ETH only — 2 of 12.** |
| **Lower the ≥2 floor for single-proxy coins** | **UNANIMOUS CUT.** Ten identical reads under ten coin names; the ledger's mirror gate would enrol ten correlated rows off one signal — fabrication by replication. |
| **On-chain (Glassnode/Nansen)** | **CUT for now.** ~$800–1,000/mo against a $700 cap already CRITICAL, to feed an instrument that cannot express a negative. Revisit only after ETF flow earns ledger evidence. |
| **Flip `INSIDER_PARSER_FIX` default to "1"** (code default is `"0"` while production runs `"1"`) | SHIP — code must not lie about intent (Executioner). |

**Also flagged:** the absence payload sets `dark_matter: None`, and `proxies_covered` lives
*inside* it — so the UI is **structurally unable** to say "this coin has one proxy." And
`absence_reason` is served but **no platform reads it** (grep: zero hits in `web-terminal/` and
`frontend/`). Two different truths computed, then discarded at the boundary.

**Jargon to retire externally:** "Dark Matter," "proxy positioning," "venue diffusion,"
"degenerate baseline," "coverage-keyed absence." Say *money into ETFs*, *coin price*, *no data
for this coin*.

## 7. THE POINT-BLANK QUESTION (Outsider)

> *"You built a crypto money-flow product on filings that do not exist for five of your seven
> sources, and the one live vote was Michael Saylor's Form 4. Who on the team has traded these
> instruments — and if nobody has, what else in the market and crypto engines was designed the
> same way?"*
