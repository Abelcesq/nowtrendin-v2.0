# NowTrendIn — Cold DDQ (FISD-gate answers, completed before anyone asked)
**Version 1.0 · 2026-08-09 · Answers state verified behavior only (SEC v. App Annie discipline). Gaps are answered "not yet," never dressed up.**
Companion documents: `PII_POLICY.md` · `MNPI_POLICY.md` · `RIGHTS_REGISTER.md` ·
`DATA_LINEAGE_FISD.md` · `ACCURACY_FIGURES_SCOPED.md`.

## Gate 1 — Point-in-time integrity
**Answer:** Every date-semantic value normalizes to one canonical date key through a
single ingestion gate; unparseable/ambiguous values are quarantined for human review,
never guessed. Fetch instants are stamped per row (`signal_time`/`captured_at`;
capture-instant discipline governs source-cutover joins). The scored panel is
append-per-cycle with 365-day retention and a hard no-quality-deletion rule refused
in code. The accuracy ledgers enroll at first crossing, stamp their measurement
parameters into a version string that rides with every verdict, and never impute or
backfill what was not enrolled. Look-ahead controls: ledger resolutions use only
data on/after detection; the market ledger's no-lookahead rule is explicit; stale
serve rows serve stored values verbatim (no retroactive recalibration).
**Gaps stated:** two disclosed backfill classes exist (market baselines seeded from
real published FINRA/financial history at their historical dates; maturity rows
stamped `backfill`); the platform is not yet a fully bitemporal as-of-t query store —
point-in-time reconstruction rests on append-only tables + capture stamps + archived
snapshots rather than a universal `as_of(t)` read API. Enrollment completeness is
published (69.6% of cycles as of 2026-08-09) rather than hidden.

## Gate 2 — Data lineage (the hardest gate)
**Answer:** documented in `DATA_LINEAGE_FISD.md` to the four FISD questions:
backfill — no, two labeled exceptions; interpolation — none in production (absence is
declared, never estimated); schema alteration — format-level only (canonical dates,
key normalization, unit expansion), ambiguity refused to quarantine; outliers —
refused at admission or read time with rows kept, never deleted retroactively on
quality judgments (refused in code). Audit trails: UTC stamps on every mutation,
parameter-version stamps on every measurement, src/epoch provenance per data row,
an intake log on every ledger-enrollment exit path.
**Gaps stated:** tier-promotion lacks a per-row audit column; junk-key prune keeps no
tombstones; human-actor attribution lives in git/board records, not DB columns.

## Gate 3 — Rights to use and redistribute
**Answer:** `RIGHTS_REGISTER.md` — one row per source with license basis and status;
a written five-gate onboarding protocol enforced by a commit hook; a real exclusion
list (sources banned/removed with reasons, incl. a binding total-exclusion ruling);
referee sources firewalled from the product. The product redistributes DERIVED
AGGREGATES (scores, components, counts), not source content; ingestion is
titles/metadata-level.
**Gaps stated (register §H, 9 items):** the direct-RSS class has no outlet-level
permission documents (posture: official public feeds, metadata-only, derived-output
product — counsel memo pending); one recorded ban/ingestion contradiction (Guardian)
awaits ruling; scraper-vendor lanes rest on vendor relationships with a general
acceptability ruling still to be recorded.

## Gate 4 — PII
**Answer:** none collected, none shipped (`PII_POLICY.md`). Aggregate topic/
instrument product; public bylines retained internally as attribution metadata only;
statutory public disclosures (Form-4, STOCK Act) ingested post-publication;
PII-requiring sources excluded at onboarding by written protocol. Discovery of PII
is an incident with immediate removal (no review-cycle delay).

## Gate 5 — MNPI
**Answer:** architecturally excluded (`MNPI_POLICY.md`): public information or
licensed commercial feeds of public information only; no expert networks, panels,
channel checks, NDA data, or pre-release access; provenance established at
onboarding; suspicion suspends a source immediately.

## Gate 6 — Security identifiers at row level
**Answer today:** instrument-keyed legs (Market Signal, crypto proxies, insider
panel, ETF flow) key on exchange tickers; the attention product's unit is TOPICS
(no instrument exists for most rows — imposing tickers there would misdescribe the
data). **Gap stated:** row-level FIGI mapping is researched (OpenFIGI, free,
MIT-licensed) and scheduled as Phase-1 work for the instrument legs; not yet
implemented.

## Gate 7 — Coverage breadth and stability
**Answer today:** instrument legs cover a curated watchlist + 12 coins + 15 ETF
proxies; the attention leg covers an open topic universe (~6,000-topic recent
working set). **Gap stated:** a distinct-mapped-ticker count and coverage-by-month
series have never been compiled against the 75-ticker quant threshold — Phase-1
work. Coverage claims will be scoped per leg, never blended.

## Gate 8 — Economics
**Answer:** pricing not yet set; the published-band context and the 10× all-in-cost
hurdle are recorded in the buyer-roadmap incorporation. The product's cost story
leans on infrastructure (the point-in-time archive) rather than per-seat analytics.
No claims made.

## Gate 9 — Vendor permanency
**Answer, stated plainly:** single-founder company; this is a known Neudata check
item. Mitigations in place and growing: the system's operating judgment is written
into committed runbooks, charters, specs, and board records (succession-grade
documentation is an open workstream — Griffin H-9); infrastructure is standard
(Heroku/Postgres/GitHub); the never-deleted ledgers and append-only stores mean the
asset survives operator interruption. Buyers may structure payments across the term
(the standard hedge for this item).

## The one-line answer a buyer gets to "what is your accuracy?"
See `ACCURACY_FIGURES_SCOPED.md` §4 — one scoped, N-carrying, provisional-flagged
sentence per ledger; rates the system withholds are stated as withheld BY DESIGN
with their pre-declared publication thresholds.
