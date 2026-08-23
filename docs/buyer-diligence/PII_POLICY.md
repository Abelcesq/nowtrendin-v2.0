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
  channel). These are stored internally as source-attribution metadata, and are not
  enriched, not joined across sources on identity, and not served except where the
  public channel IS the source being cited (e.g., a named public YouTube channel in
  creator coverage).

- **CORRECTED 2026-08-22 — WE DO HOLD ONE PER-PERSON BEHAVIOURAL TABLE, AND THIS
  DOCUMENT PREVIOUSLY DENIED IT.** The paragraph above used to end with the words *"not
  aggregated into person-level profiles"*. That was **not accurate**, and an outside
  reviewer was right to call it the one item that should not leave the building. Stated
  plainly, because a description that does not match the mechanism is the exposure —
  not the data (SEC v. App Annie, 2021):

  **`author_history`** — primary key `(author, platform, community)`, columns
  `first_seen_at` and `post_count`; approximately 32,000 rows. It is a per-person,
  per-venue longitudinal record: when we first observed a public byline in a given
  community, and how many public posts we have observed from it there. Under GDPR Art
  4(1) an online identifier plus behavioural history is personal data, and we do not
  argue otherwise.

  - **Purpose, and it is narrow.** One boolean: `is_first_timer` — is this byline new to
    this community? That flag feeds the Dark Matter component. **No other use exists.**
  - **What it is NOT.** Not enriched from any external source. Not joined to any other
    dataset on identity. Not used to profile, target, rank, score or characterise any
    individual. Never served: no API response, no UI surface, and no export contains a
    row of it. It is derived wholly from content the person published publicly.
  - **Cross-community.** The key includes `community`, and the first-timer read is
    per-community. A read that spans communities for the same byline is possible in
    principle and is not part of any shipped path.

  **KNOWN GAPS, stated rather than implied (open, dated 2026-08-22):**
  1. **No retention limit.** Rows persist indefinitely. Signal tables prune; this one
     does not, by design — the first-timer flag needs history to mean anything. The
     tension between that and data minimisation is real and unresolved.
  2. **No erasure path.** There is no mechanism today for a named individual to request
     deletion, and no runbook for what happens to `is_first_timer` on topics they
     touched if a row were removed. A deletion would silently change a scoring input.
  3. **No lawful-basis assessment on record** for the behavioural aggregate specifically,
     as distinct from the public-content ingestion.

  These are recorded here because a buyer will find the table in the schema, and finding
  it after reading a denial is materially worse than reading this paragraph. Tracked in
  `audits/DEFERRED_ITEMS.md` as **PII-AUTHOR-HISTORY**.
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

"We do not ship PII; product data is aggregate topic- and instrument-level. We DO
hold one internal per-person behavioural table: `author_history`, keyed on public
byline × platform × community, carrying first-seen date and post count (~32,000
rows), used solely to derive one boolean scoring input (is this byline new to this
community). It is never served, never enriched, and never identity-joined across
sources; under GDPR Art 4(1) it is personal data and we describe it as such (§2 of
this policy, corrected 2026-08-22, including its three open gaps: no retention
limit, no erasure path, no recorded lawful-basis assessment). Insider and
congressional inputs are public statutory disclosures ingested post-publication.
Sources that would require non-public personal data are excluded at onboarding by
written protocol."

*(This summary previously said "no person-level profiling" while §2 above, corrected
2026-08-22, disclosed `author_history`. A buyer-facing summary that contradicts its
own policy body is worse than either statement alone; the summary now matches the
mechanism.)*
