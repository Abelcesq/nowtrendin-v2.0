# EVIDENCE PACK — A2 fix board review (2026-08-08 PT, late)

## What is being decided (neutral statement)

On 2026-08-05 the Chairman ruled (amendment A2) that the issuers' own product pages
become the PRIMARY daily-shares-outstanding source for the crypto ETF flow leg, with
FMP demoted to a silent 30-day comparison, after FMP failed §16 CURRENCY at Gate 4.
The adapters implementing that ruling were built, deployed, and live-verified tonight
(2026-08-08), under founder order "please address and proceed with the fix for A2."
During the build, two defects were caught and fixed (one in the new writer, one
pre-existing in the A2 harness that the source-swap exposed). The board is asked to
review the completed work and answer the workup's five open questions (§6). The
`CRYPTO_ETF_FLOW=1` flip remains BLOCKED pending the A2.4 evidence standard; nothing
in this work changes any served score. The board informs; the Chairman rules.

## Documents to read (in this order)

1. The workup under review:
   `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\audits\board\A2_FIX_WORKUP_2026-08-08.md`
2. The governing amendment (pre-declared spec):
   `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\audits\board\CRYPTO_FLOW_SPEC_A2_AMENDMENT_2026-08-05.md`
3. The §16 survey the adapters were built from:
   `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\audits\source-onboarding\ISSUER_PAGES_SURVEY_2026-08-05.md`
4. The full change-set diff (b0a2df0..53253d8, the two commits under review):
   `C:\Users\acinv\AppData\Local\Temp\claude\C--Users-acinv-OneDrive-Desktop-CODING-PROJECTS-NowTrendin-v2-0\977fc17c-f583-47ec-9510-22477f6b005b\scratchpad\a2fix_diff.txt`
5. The implementation itself (post-change, on main):
   `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\transfer\etf_issuer_pages.py`
   `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\transfer\etf_flow_reconcile.py`

## Live verification record (production, tonight — verbatim results)

**First issuer snapshot (POST /etf/issuer-snapshot, 2026-08-09 ~03:35Z):**
```
{"date":"2026-08-09","written":0,"strikes_updated":0,"takeovers":9,"missing":[],
 "tickers":{"IBIT":{"shares":1318000000,"nav":36.740252,"src":"issuer_ishares","page_asof":"Aug 07, 2026"},
 "ARKB":{"shares":103460000,"nav":21.51,"src":"issuer_21shares","page_asof":"Aug 07, 2026"},
 "BITB":{"shares":68380000,"nav":34.94,"src":"issuer_bitwise","page_asof":"2026-08-07"},
 "ETHA":{"shares":396480000,"nav":14.449835,"src":"issuer_ishares","page_asof":"Aug 07, 2026"},
 "ETHW":{"shares":14880000,"nav":13.64,"src":"issuer_bitwise","page_asof":"2026-08-07"},
 "BSOL":{"shares":59010000,"nav":9.93,"src":"issuer_bitwise","page_asof":"2026-08-07"},
 "TSOL":{"shares":430000,"nav":7.16,"src":"issuer_21shares","page_asof":"Aug 07, 2026"},
 "XRPC":{"shares":21770000,"nav":11.27,"src":"issuer_canary","page_asof":"2026-07-31"},
 "TOXR":{"shares":11120000,"nav":9.96,"src":"issuer_21shares","page_asof":"Aug 07, 2026"}}}
```

**A2 pass BEFORE the era-attribution fix (exposed the defect):**
```
re_arm: {"pass_comparisons":0,"funds":0,"trading_days":0,"open_bad":12,"ready":false}
```
(the 12 open_bad were FMP-era uncovered July days newly stamped with the issuer src)

**A2 pass AFTER the era-attribution fix (deployed 1d7924a, 2026-08-09 04:32Z):**
```
run: {"rule_version":"A2","checked":69,"pass":6,"fail":11,"immaterial":24,
      "pending_final":5,"empty_interval":2,"no_derived":21,"no_published":0,
      "no_comparator_coins":["XRP"]}
gate: FAIL   open_failures_fmp: 13   open_failures_live_source: null
re_arm: {"pass_comparisons":0,"funds":0,"trading_days":0,"open_bad":0,"ready":false}
```
(gate FAIL is entirely FMP silent-comparison rows — the known-dead source; the issuer
source has zero failures and 5 PENDING_FINAL intervals at its still-moving edge)

**Test suites:** test_etf_reconcile_a2.py 22/22 (incl. new t4 era-attribution
regression); test_crypto_flow_a1.py all green.

## The five open questions for the board (workup §6, restated)

1. UA posture: browser-grade UA carrying our declared token on the iShares fetch
   (bare clients 403) — acceptable for a cited primary source, or require the
   blackrock.com fund-download endpoint instead?
2. Wave-3/FBTC: confirm the reading that FBTC's NO_DERIVED days (attributed to
   src='fmp' under era attribution, since FBTC has no issuer adapter) do NOT block
   re-arm under A2.4 — and how urgent is the Fidelity wave-3 adapter?
3. XRPC history backfill (issuer page publishes full daily history to inception):
   ingest under what rules, if at all?
4. ETHA reverse split effective 2026-10-06: pre-declare a scheduled series break
   (new src epoch) now — what exactly should be pre-declared?
5. Health granularity: one `issuer_shares` collector-health row for all four
   families vs one row per family (the S2 one-row-per-independently-failing-endpoint
   rule) — now or on first incident?
