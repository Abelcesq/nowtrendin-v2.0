# The $1M/Month Question — What Actually Commands It, and the Path
### Prepared: 2026-08-09 · Companion to the buyer roadmap and the Gemini assessment
### (Archived verbatim from the Chairman's submission to the 2026-08-17 board; under board review for integration with the positioning question Q5.)

## Part 1 — The answer, stated plainly
No data product has ever reached $1M/month from a single client by selling data. Not one:
exchange market data tops out in the hundreds of thousands per firm per exchange (IEX 2019:
NYSE OpenBook $226,320/yr, Nasdaq TotalView $195,972/yr, Cboe BZX $119,280/yr); enterprise
platforms (Aladdin, Charles River, SimCorp) average $0.2M–$2M per client (Credit Suisse's
Aladdin deal: CHF 50–100M over ~6 years); Enfusion ~$230k/client; FactSet ~$263k/client.

Two structures — and only two — reach eight figures from one client:

**Structure A — Bloomberg:** fixed price × thousands of seats ($31,980/yr standalone, no
volume discounts; JPMorgan 10,000+ subscriptions ≈ $210M/yr at 2016 prices). CLOSED to new
entrants: the moat is a two-sided network (20M messages/day, 320,000+ participants), proven
by Money.Net's failure at 90% lower price, Symphony's failure at $15/mo despite JPM/Goldman/
BlackRock backing, and the 2013 snooping scandal not denting the count. SEC's $1.1B
off-channel fines (2022) push conversations toward the archived incumbent channel.
"Competition for this market already happened. We are not going to win it."

**Structure B — Index licensing:** a percentage of the client's own assets. S&P DJI earns
~$247M/yr from State Street for SPY alone (0.03% of daily size + $600k; SPY $821.1B AUM as
of 2026-08-13). MSCI: BlackRock = 10.8% of consolidated revenue (~$338M), 96.5% asset-based.
"The difference between $200,000 and $250,000,000 is not the data. It is the meter."
Academic confirmation: An, Benetton & Song (JFE 2023) — >95% of index licensing fees are
%-of-AUM, avg 4.4bps (~2.8bps pure markup); index providers capture >⅓ of ETF management
fees (31.4% 2010 → 35.7% 2019).

## Part 2 — The arithmetic
$1M/month = $12M/yr. At published rates: 2.41bps (MSCI realised) → ~$49.8B tracking AUM;
3.0bps (SPY variable; Nasdaq→First Trust) → ~$40.0B; 4.4bps (2019 avg) → ~$27.3B; 9.0bps
(QQQ) → ~$13.3B; 10bps (rare ceiling) → ~$12.0B. **Goal precisely stated: ~$13B of assets
tracking a NowTrendIn index at a premium proprietary-strategy rate.**

Honest calibration: the closest comparable — BUZZ NextGen AI US Sentiment Leaders Index
(15M posts/mo NLP, top-75 large-caps by sentiment, VanEck ETF $120.8M at 0.76% TER) — is
worth ~$109,000/yr to BUZZ Holdings at ~9bps. A plan built on a number 100× the best
comparable will fail in a way a staged plan will not.

## Part 3 — What would make it worth paying for (four properties)
1. **The meter is the client's assets, not our data.** A structural choice available now;
   costs nothing to decide.
2. **Embeddedness** — the index written into documents the client cannot unilaterally
   change (prospectus, IMA, board mandate, fund name). Why MSCI retains 95.9% of Index
   revenue annually. (Vanguard's 2012 MSCI defection = the exception proving the rule.)
3. **Reproducibility — our genuine, defensible edge.** Yewno (alt-data index provider) was
   forced into liquidation with two DWS Xtrackers ETFs (£782M + £450M) dependent on it —
   clients had no fallback because Yewno's models "could not be replicated exactly." Our
   published, pre-registered, immutably archived methodology that a licensee could
   reconstruct if we vanished converts permanency risk (a literal Neudata diligence item)
   into a contractual mitigation.
4. **Non-replicability by self-indexing** (SEC self-indexing relief since 2013): the
   Renaissance answer — a point-in-time archive accruing daily that cannot be back-filled.
   An issuer starting today cannot manufacture 2026 knowable_at stamps in 2029.

## Part 4 — The regulatory bar
- **The barrier just collapsed:** Regulation (EU) 2025/914 (from 2026-01-01) narrows the
  EU BMR to critical/significant/climate/certain commodity benchmarks; "significant" only
  above €50B referencing. Below: out of scope; third-country benchmarks freely usable by
  EU supervised entities. ⚠ UK mirror UNCONFIRMED (FCA still lists "UK non-significant
  benchmarks") — needs UK counsel.
- **Direct fees trivial:** FCA £1,130–£5,640; 4-month determination; budget 6–12 months.
- **Our archive exceeds the record-keeping standard** (BMR Art 8: full replication +
  5-year retention; ESMA: historical values reconstructable): the bitemporal
  event_date/knowable_at store with append-only triggers, Merkle sealing, immutable
  prereg delivers by construction; neither IOSCO nor BMR requires pre-registration or
  non-restatement — strictly stronger on the anti-hindsight dimension.
- **What the archive does NOT do (never gloss):** Art 13 advance-notice/consultation on
  methodology changes; Art 5 oversight function; Art 4 conflicts policy; Art 6 control
  framework; Art 9 complaints mechanism; IOSCO P17 independent audit. Organisational, not
  archival. "The archive is one control among a dozen, not a compliance programme."

## Part 5 — The concrete path
**Stage 1 (0–12 mo, low cost) — become a licensable index administrator:** 1.1 DECIDE THE
METER (AUM-linked licensing — costs nothing, changes everything); 1.2 finish buyer-roadmap
Phase 0; 1.3 publish methodology to BMR Art 13 standard; 1.4 constitute the oversight
function (the Advisory Board is the prototype — formalise); 1.5 conflicts policy + control
framework + complaints procedure; 1.6 independent methodology audit (IOSCO P17); 1.7
publish an index rulebook a licensee could reconstruct from — and SAY SO in sales (the
Yewno answer); 1.8 fix the A4 accuracy spread + build the A5 null model ("no issuer
licenses an index with seven hit rates"); 1.9 FCA registration if UK counsel confirms.
**Stage 2 (12–24 mo) — sell benchmark subscriptions BEFORE any AUM exists:** the rung most
skip. MSCI earns more from index subscriptions ($957.9M) than asset-based fees ($770.7M);
FTSE Russell likewise (£630M vs £324M). $25k–$150k/yr per client, stacks, builds the
citation footprint; flat minimums decouple early revenue from AUM (SPY carries $600k fixed).
**Stage 3 (24–36 mo) — land the first issuer:** not BlackRock — a small/thematic issuer,
defined-outcome shop, or white-label platform. Know their economics ($100k–$500k to
register, $2.5M seed, $200k–$500k/yr running, breakeven ~$50M AUM at 0.50%). The winning
pattern (MerQube ~$27B platform; Solactive 17,000+ indices; BUZZ): own a strategy the
issuer cannot self-index.
**Stage 4 (36 mo+) — scale, or sell:** $13B at 9bps = the $12M/yr goal state — decade-scale,
low probability; Kensho (the alt-data index that worked, $2.8B in SPDR KOMP) succeeded by
being ACQUIRED by S&P Global. Acquisition by an incumbent distributor is a legitimate and
probably more likely destination; Stages 1–3 increase its value either way.

## Part 6 — What to stop doing
Stop benchmarking price against Bloomberg (a communications network, not a data business).
**Stop pricing per-seat or per-API-call — that meter caps at six figures no matter how good
the data is (the single most consequential change in this document).** Do not build the
rejected Gemini items. Do not claim the archive is a compliance programme (the App Annie
failure mode, aimed at a regulator).

## The one-paragraph version
$1M/month is not a subscription price — it is what a percentage fee on someone else's
balance sheet looks like. The route: stop being a data vendor and become a benchmark
administrator — publish the score as a rules-based, pre-registered, independently
auditable index; sell benchmark subscriptions first; then license to an issuer for basis
points. The archive already exceeds the record-keeping standard, the EU dropped the
barrier for small administrators on 2026-01-01, and the reproducibility Yewno's licensees
lacked is the exact objection our architecture answers. Honest calibration: BUZZ earns
~$109k/yr — this is a decade-scale climb with acquisition as the more probable good
outcome. But the first move costs nothing: **change the meter.**

*(Full source list preserved in the original submission — SPY prospectus, MSCI 10-K,
An/Benetton/Song JFE 2023, Nasdaq→First Trust EDGAR exhibit, IEX 2019 cost disclosure,
Reg (EU) 2025/914, ESMA BMR guidelines, IOSCO Principles, FCA fee schedules, Yewno/DWS
coverage, BUZZ/Kensho/MerQube/Solactive records.)*
