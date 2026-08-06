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
