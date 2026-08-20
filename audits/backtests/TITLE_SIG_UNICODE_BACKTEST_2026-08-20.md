# `_title_sig` Unicode fix — backtest before ship
### 2026-08-20 · Chairman-ordered ("fix this issue so that we are maximizing our data sources")
### Score-affecting (feeds `n_news_independent` → §15a quorum) → backtested per the §15a rule before deploy.

## History (from the session-log review the Chairman requested)

`_title_sig` was built 2026-06-26 as Mainstream v2's syndication collapse. The non-Latin
gap was identified and DEFERRED three times — SESSION_LOG 2026-07-10: "Native-script terms
deferred (pending `_demojibake` fix)"; "today's non-Latin finding maps to pending #12 + #15
(entity extraction) — **raised 3x now**." This backtest closes that thread.

## The defect

Old signature kept only `[a-z0-9 ]`. Every non-Latin-script headline therefore collapsed to
the **same empty string** — five Arabic or Chinese outlets covering one story counted as ONE
voice under `min(distinct outlets, distinct titles)` and could never reach the quorum of 5.
Non-English coverage was structurally unable to corroborate anything.

## The fix

NFKD-fold diacritics (é→e — so Mbappé/Mbappe wire variants now correctly collapse to ONE
story, an *improvement* in syndication detection), then keep unicode letters/digits in any
script. ASCII text is unchanged by construction.

## Backtest — full production news corpus, last 7 days (read-only)

77,037 (topic, outlet, title) rows over news platforms (newsapi_org/newsapi_ai/newsdata_io/
gdelt/guardian), 58,037 topics.

| Measure | Result |
|---|---|
| ASCII titles old-vs-new signature | **63,273 of 63,273 byte-identical — zero mismatches** |
| Non-ASCII titles now producing real signatures | **13,764 (17.9% of news titles)** |
| Topics whose story-set contained the EMPTY signature | **804** |
| Topics where `n_news_independent` changes | 15 |
| … crossing the **QUORUM (5)** boundary | **0 — zero mainstream badges flip** |
| … crossing the reputable-weight (2) boundary | 15, all upward (1→2), all previously-collapsed distinct stories now honestly counted (e.g. Bengali measles coverage, Chinese wire stories, a PR-wire pair) |

Same clean profile as the v2.1 quorum backtest: **zero badge flips, zero detection change at
the quorum**; the only movement is de-collapsing stories that were always distinct.

## Verified properties (live, not asserted)

- `Mbappé…` and `Mbappe…` → identical signature (accent-fold collapse works).
- Arabic / Chinese / Russian headlines → three distinct, non-empty signatures.
- 63k ASCII titles → byte-identical to the old function.

*Read-only backtest; no rows written. Harness inline in session (old/new sig functions +
production corpus comparison); results reproduced above in full.*
