# NowTrendIn — Material Non-Public Information (MNPI) Policy
**Version 1.0 · 2026-08-09 · Owner: Founder (Chairman) · Review: annually or on any new source class**

## 1. Position statement

**Every input to the NowTrendIn data product is either public information or a
licensed commercial feed of public information.** The system is architecturally
incapable of expressing private information because it ingests none: no expert
networks, no employee or insider panels, no channel checks, no survey panels, no
data acquired under NDA, no data sourced from fiduciaries or counterparties, and no
private-venue content.

## 2. Source classes and their MNPI posture

| Class | Examples | MNPI posture |
|---|---|---|
| Official/direct publications | Issuer product pages, exchange RSS (Nasdaq halts), central-bank feeds, SEC/FINRA/OFR data | Public by construction; ingested after publication |
| Reputable licensed media | Direct RSS from named mainstream outlets | Public editorial content |
| Licensed commercial data APIs | Finviz Elite, FMP, QuiverQuant, Databento, AlphaVantage | Vendors of public-market and public-filing data under paid license |
| Public platform content | Trending queries, public posts, public research feeds, Wikipedia pageviews | Public at fetch time |
| Regulatory disclosures | SEC Form-4 (insider), STOCK Act (congressional) | Statutory PUBLIC records — by definition no longer non-public when ingested (ingestion occurs only after public release) |
| Held-out referees | Farside (published fund flows), Wikipedia pageviews, CoinGecko/CMC | Public; verification-only, never score inputs |

## 3. Controls

1. **Onboarding gate (§16, written protocol, commit-hook enforced):** every proposed
   source passes a TYPE review that identifies what the data is and where it
   originates before any linkage. A source whose provenance cannot be established as
   public/licensed fails the gate.
2. **No selective-disclosure channels:** the company does not solicit or accept
   information from issuers, management, employees, or advisors. There is no
   expert-network relationship and no primary-research function that contacts
   companies.
3. **Timing discipline:** regulatory-filing inputs are ingested from public
   distribution points after publication; the pipeline has no pre-release access to
   anything.
4. **Escalation:** any suspicion that a source carries non-public material (e.g., a
   vendor feed containing leaked or embargoed content) suspends the source
   immediately pending review; the event is logged in the audit record. Removal is
   not a scoring change and executes without the flag-never-force review cycle.

## 4. The accuracy-of-description rule (App Annie)

SEC v. App Annie (2021) established that MISDESCRIBING methodology and controls to
buyers is itself the violation. Accordingly: this policy states only what the
system verifiably does; methodology descriptions served to users and buyers are
kept consistent with the code; and accuracy figures are published only where
reproducible from the retained ledgers. Where a control does not exist, the answer
given is "it does not exist," never an aspiration dressed as a control.

## 5. Buyer-facing summary (DDQ answer)

"All inputs are public information or licensed commercial feeds of public
information, ingested post-publication. We operate no expert networks, panels, or
primary-research contacts, and have no pre-release access to any source. Provenance
is established at onboarding under a written, commit-hook-enforced protocol; a
source with unestablishable provenance is not linked. Suspected non-public content
suspends a source immediately."
