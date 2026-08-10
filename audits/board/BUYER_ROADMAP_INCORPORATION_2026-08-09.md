# BUYER ROADMAP — critical analysis + incorporation record (2026-08-09)

Source: the parallel session's "What Hedge Funds Actually Buy — and a Realistic Path for
NowTrendIn" (archived: `HEDGE_FUND_BUYER_ROADMAP_parallel-session_2026-08-09.docx/.txt`;
~25 sources incl. the FISD Alternative Data Council's public DDQ standards, SEC v. App
Annie, the SBAI trial-license template, AIMA/JPM/Deloitte buyer research, Neudata/
BattleFin listing mechanics, and named data-org roles at Citadel/Point72/D.E. Shaw/
Millennium). Chairman rulings this session: (a) NINE full always-convening seats;
(b) NO tenth customer seat — the buyer view is SYNTHESIZED into THE OUTSIDER / BUYER'S
DESK (implemented in the skill, this date).

---

## 1. Why synthesis, not a seat (the ruling's rationale, recorded)

A seat whose mandate is "the problems and concerns of hedge funds" structurally
represents buyer APPETITE, and a fund's standing appetite from any data product is
actionable signal — the seat would generate advice-drift pressure convening after
convening, against measurement-not-advice. The buyer's legitimate voice is DILIGENCE,
and diligence is the Outsider's existing lane. The roadmap itself seals the argument:
the top of the buyer market is mostly NOT our first customer (only 4 of the top-10
Rich-List firms are addressable at all; the #1 earner runs ten positions and no data
function; Griffin himself is on record calling alt-data's impact "modest"), so a seat
tuned to hedge-fund desire would also aim the product at the wrong tier. The Outsider
now carries the FISD gate order + the App Annie rule as a standing checklist, and every
verdict names which buyer-desk gate an item strengthens or endangers.

## 2. The critical analysis (what we learn, what we adopt, where I push back)

**The document's central reframe is correct and matches everything three boards have
built toward:** adoption of a Bloomberg-class utility comes from being the NEUTRAL,
COMPLIANCE-APPROVABLE, REPRODUCIBLE data layer, not from oracle claims. Its one-line
strategy — "the attention dataset a compliance team can actually approve and a quant can
actually reproduce" — is the founder's "we are not selling scores, we assess data
through agents and sources" stated as a market position. Three findings deserve to be
treated as doctrine:

1. **The App Annie rule** (SEC's first alt-data enforcement, 2021: $10M for
   MISDESCRIBING methodology and controls — not for bad data). Every DDQ answer and
   published methodology claim is securities-law exposure. This converts our
   honest-absence discipline, the never-publish-catch-all-as-KPI rule, and
   reproducible-numbers-only from ethics into LEGAL DEFENSE. It is the commercial
   twin of the foundational principle "a number we cannot defend is worse than none."
2. **Scores are unbuyable by sophisticated quants for mechanical reasons, not
   snobbery** (can't orthogonalize a black box; can't reconstruct point-in-time across
   model retrains; score revisions collide with lineage; can't answer "why
   predictive") — but ~62% of buyers want cleaned/tagged data with services, not raw.
   The survivable shape: **ship the components AND the score, both vintaged, with the
   transformation logic documented to lineage standard** — and sell first to the tiers
   without in-house quant capacity (smaller funds, family offices, RIAs, IR, sell-side).
   Our engine already serves component breakdowns (the Gradient components, Money
   Movement/Market Confirmation, per-item Signal Analysis); the gap is vintage-shaped
   DELIVERY, not the data's existence.
3. **The moat restated:** the point-in-time archive accrues daily and cannot be
   backfilled — a 2028 competitor cannot manufacture 2026 capture stamps. This is the
   Statistician's Straus lesson and the Economist's Friedman-&-Schwartz lesson landing
   as a BALANCE-SHEET fact: our 365-day retention, capture-instant discipline, src
   provenance, and held-out ledgers are the asset; the score is the demo.

**Where I push back on the document (critical, per the founder's ask):**

- **Category framing.** It accepts placement in "social/sentiment data" — the most
  crowded, lowest-rated, cheapest-priced category (~30% under $25k/yr). That
  under-sells the actual product: three HELD-OUT OUTCOME LEDGERS validating detection
  lead against external ground truth is closer to an index/benchmark + validation
  product than to a sentiment feed. Positioning should lead with the measurement rails
  and the audited record; "sentiment" is an input class, not the product.
- **The 75-ticker coverage threshold** applies to instrument-keyed legs (Market
  Signal, Trend Beneficiary, crypto proxies) — the attention product's unit is TOPICS,
  not tickers. Row-level identifiers (OpenFIGI) are right for the market/crypto legs;
  imposing ticker-frame metrics on the attention leg would misdescribe it (an App
  Annie hazard in itself). Scope the identifier work where instruments exist.
- **The "fails a DDQ today" list is the PARALLEL lineage's, not ours — verified
  before adoption** (verify-before-fix): its "live credential in engine CLAUDE.md line
  100" is NOT present in this repo (markdown credential scan clean, 2026-08-09); its
  "crypto ledger grades a signal with zero money input" does not describe THIS engine
  (our crypto DM is the live Finviz proxy leg; our crypto ledger validates realized
  coin-price direction; the FLOW leg is flag-gated OFF pending A2.4 — the gap is
  disclosed, not silent); "hist_store.py / prereg lock / A4-A5 audit findings" are the
  other lineage's artifacts. What DOES apply here, honestly: scoped-per-ledger
  accuracy figures with N (our reports are maturity-segmented but the N-with-
  every-figure discipline is not yet universal); no written PII/MNPI policy documents;
  no rights REGISTER as a single table (the rulings exist across §15/§16 records —
  nobody has compiled the one-row-per-source register); no null-model baseline
  published for the 365-day window (the Economist's prescription #1, same finding
  independently); the single-founder permanency item (Griffin H-9, same finding);
  coverage-by-month never counted.

## 3. The adoptables (joins the Griffin + Two-Poles lists; PENDING CHAIRMAN, ranked)

Phase-0-class (documentation, £0, no customer needed):
1. **PII policy** (we collect and ship none — write it) + **MNPI policy** (all sources
   public/licensed, no expert networks, no panels — write it). Instant-kill DDQ items.
2. **Rights register** — one row per source: license, ToS reviewed, redistribution
   Y/N, date, ruling reference. The material exists in §15/§16 + Chairman rulings;
   compile it. (A genuine differentiator — most vendors cannot answer this.)
3. **Lineage document to FISD standard** — the ingestion gate, date canon, quarantine
   loop, catch-all floor, src provenance, written up as transformation lineage.
4. **Resolve published accuracy into scoped, per-ledger, N-carrying figures** (aligns
   with Two-Poles mechanics 2–3 and the Statistician's mandate).
5. **Complete the FISD DDQ cold** — free spec; forces every remaining gap into view.
Phase-1-class:
6. Row-level OpenFIGI on instrument-keyed records (market/crypto/beneficiary legs).
7. Coverage count + coverage-by-month over history (instrument legs).
8. Null-model baseline for the ledger windows (= Economist prescription #1).
9. Vintage-shaped delivery: components + score as columns with capture stamps
   (expose what the DB already does).
Phase-2-class (free listings/templates): Neudata listing · SBAI trial-license template ·
BattleFin scorecard-shaped documentation · marketplace listing evaluation.
Sequencing doctrine (adopted from the roadmap): do NOT open with the mega-funds; open
with the tier that buys processed signals; publish the methodology and the question we
answer precisely, because ~80% of dataset discovery is thesis-driven search, not
prospecting.

## 4. One-line strategy (adopted verbatim as the commercial articulation)

> We are not competing on having attention data — we are competing on being the
> attention dataset a compliance team can actually approve and a quant can actually
> reproduce: point-in-time from the start, lineage documented, rights written down,
> identifiers where instruments exist, methodology published, absences shown honestly.
