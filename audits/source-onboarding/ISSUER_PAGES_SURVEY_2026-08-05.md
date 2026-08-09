# Issuer product pages — §16 TEST-phase survey (2026-08-05 PT, late)

Per Chairman ruling (b) + amendment A2.3: the issuers' own product pages become the
PRIMARY daily-shares-outstanding source for the crypto ETF flow leg. This is the
TEST-phase evidence (live fetches, all 15 roster funds). Adapters wire next, per-issuer,
fail-CLOSED, stamped `src` per the splice rule.

## Verdict summary — every fund has official daily shares data (no honest absences)

**Cleanly coverable, plain HTTP (8):** BITB, ETHW, BSOL (Bitwise — bitbetf.com /
ethwetf.com / bsoletf.com, direct field, T-1 stamps); ARKB, TSOL, TOXR (21Shares —
21shares.com/en-us/products-us/<t>, direct field, same-day; NOTE ark-funds.com is no
longer the ARKB authority — 21Shares is the sponsor); XRPC (Canary — canaryetfs.com/xrpc,
direct field + a FULL daily NAV/shares HISTORY table back to 11/12/2025 inception —
backfill gold).

**Coverable, bot-protected (5):** IBIT + ETHA (iShares — product pages 403 plain
fetch; same-day direct field; clean path = the official blackrock.com fund-download
API, portfolioId 333011 / 337614); GBTC + ETHE + GSOL (Grayscale — etfs.grayscale.com,
same-day direct field incl. coin-per-share; 403/429 to plain fetch — needs
browser-grade UA handling).

**Derived-precise (2):** FBTC + FETH (Fidelity — the research dashboard rounds shares
to 0.1M; the PRECISE daily figure = coin-in-fund ÷ coin-per-share, both T-1 dated;
**NEVER NetAssets÷NAV** — Fidelity's Net Assets is stale quarterly). HODL (VanEck):
direct field unconfirmed headless (lazy-load); derivable Net Assets ÷ NAV same-day —
adapter must verify which field actually hydrates before trusting either.

## Integration hazards (must be handled in the adapters)

1. **ETHA reverse split effective 2026-10-06** — a share-count cliff; the splice/epoch
   machinery (src column, no-delta-across-seam) must treat it as a declared series
   break, not flow.
2. **Mixed date conventions**: Grayscale/iShares/21Shares stamp same-day;
   Bitwise/Canary/Fidelity T-1; Bitwise's NAV lags its shares field by a day. All dates
   pass `gate_date()` → canonical `signal_date` (§14); the A2 t_of/settled-through
   mapping keys on OUR capture instant regardless.
3. **Staking/distribution funds** (ETHE monthly distributions; ETHE/GSOL/BSOL stake):
   shares outstanding stays the clean creation/redemption quantity — never use
   NAV-derived paths for these.
4. Sample values captured in test (2026-08-05/06): IBIT 1,309,120,000 (Aug 05) —
   vs FMP's frozen 1,304,652,500 since 08-02, i.e. the issuer's own page ALREADY shows
   the ~4.5M-share creation FMP missed; GBTC 171,180,100; ARKB 103,370,000;
   BITB 68,270,000; FBTC ≈197,353,532 derived-precise (Aug 04); ETHA 387,360,000;
   ETHE 94,048,500; ETHW 14,880,000; BSOL 59,010,000; GSOL 17,314,135; TSOL 430,000
   (below AUM voting floor — snapshot-only); XRPC 21,870,000; TOXR 11,120,000;
   HODL ≈58.9M derived (unconfirmed direct field).

## Next (adapter build order)

1. Wave 1 — the 8 plain-HTTP funds (Bitwise ×3, 21Shares ×3, Canary XRPC incl.
   history backfill, + HODL probe) → `src='issuer_<name>'`, fail-closed, dark.
2. Wave 2 — iShares via the blackrock.com fund-download API (IBIT/ETHA).
3. Wave 3 — Grayscale (UA handling) + Fidelity derived-precise.
4. Each wave: live-sample eyeball → wire → observe strikes accumulate → the A2
   harness scores them (re-arm counts ONLY these rows). ≥5 value-distinct strikes per
   votable fund re-earns §8 preconditions on the new source.

## ✅ BUILD STATUS 2026-08-08 (waves 1+2 WIRED; founder-ordered "proceed with the fix")

`transfer/etf_issuer_pages.py` — 9 funds live-verified and wired, fail-closed:
- **iShares IBIT/ETHA** — the product page serves the key-fund-facts JSON blob
  server-rendered but HTML-entity-encoded (&quot;) with browser-grade UA (bare fetch
  403s); parser unescapes then reads sharesOutstanding/navAmount/totalNetAssets;
  rendered-span fallback. Live 2026-08-08: IBIT 1,318,000,000 sh / nav 36.74 /
  $48.42B (as-of Aug 07) — confirms the ~13.3M-share creation FMP's frozen
  1,304,652,500 missed. ETHA 396,480,000 / 14.45 / $5.73B.
- **Bitwise BITB/ETHW/BSOL** — server-rendered `fundDetails` JSON (netAssets,
  sharesOutstanding, asOfDate T-1) + navAndMarketPrice.nav. Live: BITB 68.38M/34.94;
  ETHW 14.88M/13.64; BSOL 59.01M/9.93 (as-of 2026-08-07).
- **21Shares ARKB/TSOL/TOXR** — `ki4-shares-outstanding` + `ki3-nav-per-unit`
  data-elements. Live: ARKB 103.46M/21.51; TSOL 0.43M/7.16; TOXR 11.12M/9.96.
- **Canary XRPC** — wpDataTables daily history rows, newest Rate Date. Live:
  21.77M/11.27 (as-of 2026-07-31 page-stamp; capture-instant rule governs).
- **NOT wired (fail-closed absence, wave 3):** Grayscale GBTC/ETHE/GSOL (HTTP 429
  bot-wall), VanEck HODL (redirect loop headless), Fidelity FBTC/FETH
  (derived-precise; dashboard JS-hydrated, no plain-fetch path proven).

Integration (per A2.3): `snapshot_issuer()` writes observations + daily strikes
`src='issuer_<family>'`; `etf_flow.snapshot()` (FMP) demotes to OBSERVATIONS-ONLY on
covered tickers (`ETF_ISSUER_PRIMARY=1`) — the silent 30-day comparison; takeover of
an existing FMP daily row is a one-time seam (splice rule voids deltas across it).
Scheduler: runs with the 4h ETF snapshot loop; manual `POST /etf/issuer-snapshot`
(internal). Health row `issuer_shares` (360m, min_distinct 5). Dates: capture-instant
rule (survey hazard 2) — page as-of logged for the eyeball only. Behavior-tested
(insert/no-change/strike/takeover/FMP-demotion + a caught same-second PK collision →
microsecond captured_at); 19/19 A2 checks + A1/F-fix regressions green.
