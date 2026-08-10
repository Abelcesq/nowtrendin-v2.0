# NowTrendIn — Personal Data (PII) Policy for the Data Product
**Version 1.0 · 2026-08-09 · Owner: Founder (Chairman) · Review: annually or on any new source class**

> Scope: this policy covers the NowTrendIn DATA PRODUCT — the signals, scores,
> components, and ledgers served to customers. (End-user ACCOUNT data — login email,
> subscription tier — is an application concern governed separately by the platform's
> terms; it never enters the data product.)

## 1. Position statement

**NowTrendIn does not collect, process, or ship personal data as a data category.**
The product measures aggregate attention and market positioning at the TOPIC and
INSTRUMENT level. No natural-person profiling, identity resolution, contact
information, geolocation, device data, browsing history, or individual transaction
data is collected from any source, and none is delivered in any product surface.

## 2. What the pipeline actually touches (stated precisely, per the App Annie rule)

- **Ingested content:** public headlines, public post titles, public trending-query
  strings, public page-view counts, market data (prices, share counts, volumes,
  filings-derived aggregates), and official regulatory publications.
- **Attribution metadata:** some raw records carry the PUBLIC byline, username, or
  channel name attached to public content (e.g., a blog author, a public YouTube
  channel). These are stored internally as source-attribution metadata only. They are
  not aggregated into person-level profiles, not enriched, not joined across sources
  on identity, and not served except where the public channel IS the source being
  cited (e.g., a named public YouTube channel in creator coverage).
- **Public-figure regulatory disclosures:** insider-transaction inputs derive from
  public SEC Form-4 filings; congressional-trading inputs derive from public STOCK
  Act disclosures. These are statutory public records about public roles, ingested
  after public release, and served only in aggregate/instrument-level form.

## 3. Prohibitions (standing, enforced at source onboarding)

The §16 source-onboarding protocol (TYPE gate) excludes at admission any source
whose content is: personal contact data; individual location/movement data; device
or clickstream data; individual financial transaction records; scraped private or
semi-private content (private groups, DMs, gated communities); or any dataset
requiring identity resolution to be useful. A proposed source that fails this test
is not linked, regardless of signal value.

## 4. Incident handling

If personal data beyond public attribution metadata is discovered in any ingested
store, it is treated as a data-quality incident: the record class is quarantined,
the source is suspended pending re-review under §16, and the finding is logged in
the session/audit record. Flag-never-force does not apply — removal of PII is not a
scoring change and executes immediately.

## 5. Buyer-facing summary (DDQ answer)

"We do not collect or ship PII. Product data is aggregate topic- and
instrument-level. Internal raw stores retain public bylines/handles solely as
source attribution on public content; no person-level profiling, enrichment, or
identity joins are performed. Insider and congressional inputs are public statutory
disclosures ingested post-publication. Sources that would require personal data are
excluded at onboarding by written protocol."
