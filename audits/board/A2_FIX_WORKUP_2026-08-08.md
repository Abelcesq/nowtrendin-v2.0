# A2 FIX WORKUP — issuer-page shares adapters (2026-08-08, for Advisory-Board review)

Prepared for the board at the founder's direction ("please address and proceed with the
fix for A2 … have the /advisory-board convene to review the updates completed and a
[A]2 fix workup"). Everything below is committed (d8c23d9) and deployed to
nowtrendin-v2-engine; the flip `CRYPTO_ETF_FLOW=1` remains **BLOCKED** — nothing in
this work changes a served score.

## 1. The defect this fixes (verified, not assumed)

The A2.4 re-arm standard counts ONLY issuer-source rows, and on 2026-08-08 the live
report read `re_arm: {pass_comparisons: 0, funds: 0, trading_days: 0, ready: false}` —
because **every row in `etf_reconcile_log2` carried `src='fmp'`**. The A2.3 primary
source (issuer product pages) was ruled on 2026-08-05 and surveyed the same night, but
the adapters themselves were never built (the 08-05 session log lists them under
"NEXT"). The re-arm clock could not start: the fix is the missing derived-leg source,
not any change to the harness, the band, the floor, or the standard.

## 2. What was built

`transfer/etf_issuer_pages.py` — official/direct issuer-page adapters for daily shares
outstanding, per the §16 survey (`ISSUER_PAGES_SURVEY_2026-08-05.md`):

| Family | Funds | Mechanism (live-verified 2026-08-08) |
|---|---|---|
| iShares | IBIT, ETHA | Product page's key-fund-facts JSON blob (server-rendered, HTML-entity-encoded; browser-grade UA required — bare fetch 403s). shares + NAV + AUM + as-of |
| Bitwise | BITB, ETHW, BSOL | Server-rendered `fundDetails` JSON (`sharesOutstanding`, `netAssets`, `asOfDate` T-1) + `navAndMarketPrice.nav` |
| 21Shares | ARKB, TSOL, TOXR | `ki4-shares-outstanding` / `ki3-nav-per-unit` data-elements, page-level as-of |
| Canary | XRPC | wpDataTables full daily NAV/shares history table; newest dated row |

**Not wired (declared absence, fail-closed — wave 3):** Grayscale GBTC/ETHE/GSOL
(HTTP 429 bot-wall to plain fetch), VanEck HODL (headless redirect loop; direct field
unconfirmed), Fidelity FBTC/FETH (derived-precise coin-in-fund ÷ coin-per-share; the
dashboard is JS-hydrated — no plain-fetch path proven). These funds simply produce no
issuer strikes; material published days there will surface as `NO_DERIVED` per A2.1.4
— failure semantics, never silence.

Live sample vs the survey's 08-05/06 captures (sanity): IBIT 1,309.1M → **1,318.0M**
(the ~13M-share creation FMP's frozen 1,304.65M never showed), ETHA 387.4M → 396.5M,
ARKB 103.37M → 103.46M, BITB 68.27M → 68.38M — every value moved plausibly; nothing
frozen, nothing zigzagging.

## 3. Integration mechanics (all pre-declared rules honored)

- **Provenance:** every write stamps `src='issuer_<family>'`
  (observations + daily strikes). NULL/`'fmp'` rows remain FMP's.
- **FMP demotion (ruling b):** `etf_flow.snapshot()` now writes covered tickers to
  `etf_share_observations` ONLY — the silent 30-day comparison stream (re-eval
  2026-09-05). Its daily-strike path survives for uncovered funds so no fund goes
  dark silently.
- **Splice (A2.3):** the first issuer daily row after an FMP row is a one-time
  takeover of that date's strike row — a source seam. `latest_delta` and the A2
  harness already refuse Δshares across a seam (regression-tested); the issuer series
  re-earns its own history. Clocks restarted = exactly what A2.4 requires.
- **Dates (survey hazard 2):** mixed issuer stamp conventions (same-day vs T-1) are
  NOT interpreted; the A2 `t_of()` settled-through mapping keys on OUR capture
  instant, as pre-declared. Page as-of stamps are logged for the eyeball only.
- **Fail-closed:** an adapter that cannot parse BOTH shares AND nav returns nothing.
  No stale value, no guess, no partial row.
- **Cadence:** runs with the existing 4h ETF snapshot loop (free HTTP fetches,
  batch-paced 2s between issuers; no paid API touched). Manual trigger:
  `POST /etf/issuer-snapshot` (internal-key gated). Health row `issuer_shares`
  (360m window, `min_distinct` 5 — the dead-parser guard).

## 4. Defects caught during the build (verify-before-ship evidence)

1. **Same-second PK collision (would have silently dropped data):** the FMP pass and
   issuer pass run back-to-back; `etf_share_observations` keys on
   (ticker, captured_at) at second resolution, so a same-second issuer observation
   collided with the FMP row and vanished under `ON CONFLICT DO NOTHING`. Caught in
   the local behavior test; fixed by microsecond-precision `captured_at` on the
   issuer writer.
2. **iShares entity-encoding:** the JSON blob arrives `&quot;`-encoded on the live
   page (curl-saved copies differed) — parser unescapes first, with the rendered-span
   as an independent fallback.
3. **NO_DERIVED era-attribution defect (found in the FIRST live A2 pass after the
   swap, fixed same night):** the sweep stamped uncovered material days with the
   LATEST strike's src — so at takeover, all 12 FMP-era uncovered July days were
   suddenly attributed to the brand-new issuer source (`re_arm.open_bad` jumped 0→12
   on rows the issuer series is STRUCTURALLY unable to cover; its first strike
   postdates them). That both violates A2.4's "no FMP-era row counts toward any
   gate" and would have permanently blocked re-arm. Fix (mechanism-derived, no
   per-row freedom): each published day is blamed on the source whose strike ERA
   covered it — era boundaries at `t_of(first strike of each src run)`, strict
   inequality so the boundary day (the new source's baseline, unspannable by any
   interval) stays with the prior era. This changes ONLY the `src` stamp on
   NO_DERIVED rows (re-computed under the same A2 rule_version with fresh
   verdict_at, per the Chairman's ruling a); no verdict, band, floor, or PASS/FAIL
   outcome changes. New regression `t4_no_derived_era_attribution` (22/22 green).

Behavior test matrix (throwaway DB): FMP demotion (covered ticker skipped, uncovered
written) · first-sight insert · same-value no-op · genuine strike update · FMP→issuer
takeover seam. All passed. Regression suites: `test_etf_reconcile_a2.py` **19/19**,
`test_crypto_flow_a1.py` **all green**.

## 5. What this does NOT do

- Does not flip `CRYPTO_ETF_FLOW`. The A2.4 standard is untouched: ≥5 material
  in-band interval comparisons on the issuer source, ≥2 funds, ≥3 distinct trading
  days, zero FAIL/EMPTY_INTERVAL/NO_DERIVED, zero bias, in the rolling 21-day window
  — plus Chairman go. Realistic earliest remains days away (strikes must accumulate
  and intervals must close behind the comparator's edge).
- Does not touch F7 floor/band constants, the harness join, the verdict log, any
  served score, or any ledger.
- Does not backfill history: the issuer series starts at first capture (XRPC's
  history table is noted as backfill-gold but deliberately NOT ingested this wave —
  backfill would fabricate pre-source strikes the splice rule exists to prevent;
  board may consider it separately with its own rules).

## 6. Open questions put to the board

1. **UA posture:** iShares 403s bare clients; the adapter sends a browser-grade UA
   carrying our declared token (`… Chrome/126.0 Safari/537.36 NowTrendIn/2.0`),
   env-overridable. Is this acceptable posture for an official issuer page we cite as
   primary source, or does a seat want a stricter standard (e.g., the blackrock.com
   fund-download endpoint only)?
2. **Wave-3 priority:** FBTC is one of the two highest-materiality BTC funds and
   remains FMP-silent/no-issuer-strikes (its published material days will log
   NO_DERIVED **against src='fmp'** rows, which A2.4 already excludes; the re-arm
   gate reads open_bad on NON-FMP rows only, so FBTC absence does not block re-arm —
   but a seat should confirm that reading of A2.4 is the intended one).
3. **XRPC history backfill** (see §5) — wanted under what rules, if at all?
4. **ETHA reverse split effective 2026-10-06** (survey hazard 1): the split will
   appear as a share-count cliff. The 20%/day discontinuity guard catches it at
   vote level, and the harness would see a massive EMPTY_INTERVAL/FAIL unless the
   series is epoch-broken. Proposal: declare a scheduled series break (new src epoch
   `issuer_ishares_r1`) effective that date — decide now, before it hits.
5. **Sub-source health rows** (the S2 rule): one `issuer_shares` row covers all four
   families today; families fail independently (Grayscale already does). Should each
   family get its own row now, or when the first silent-family incident occurs?
