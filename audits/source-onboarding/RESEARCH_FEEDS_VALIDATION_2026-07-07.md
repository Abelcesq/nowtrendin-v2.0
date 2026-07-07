# Research/Early-Signal Outlets — §16 Five-Gate Onboarding + Validation (2026-07-07)

**Scope:** the §15 M/D-reweighting design — route research outlets into Dark Matter (D) via
`blog_collectors` GHOST feeds at expert tier. Candidates: War on the Rocks, Rest of World,
Global Issues, Pew Research, RAND (blog), NBER.

**Status: BUILT + HELD-OUT VALIDATED — flag-gated OFF (`GHOST_RESEARCH_FEEDS`, default 0).
Founder flips the flag after reviewing this report (flag-never-force / backtest-before-ship).**

## Gate results (live samples, production code path)

| Gate | Verdict |
|---|---|
| 1 TYPE | All six are attention/early-signal editorial or research feeds (not positioning data) ✓ |
| 2 ENGINE | Dark Matter D via `blog_collectors` GHOST path at `tier="expert"` — the §15-anchored router (`platform_tier`), NOT `_news_write` ✓ |
| 3 FORMAT | **THE decisive gate — see findings** |
| 4 CURRENCY+ACCESS | All six HTTP 200 with production UA; WoR/RoW/GI items same-day fresh, RAND ≤5d, Pew ≤1d. NBER items carry **no dates** ✗ |
| 5 TEST→LINK | Tested live end-to-end (parse → extract → `_is_quality_topic`); wired flag-OFF; NOT deployed live pending founder flip |

## The FORMAT-gate finding (integrity-critical)

The generic blog n-gram extractor **fails** these editorial titles: it produces filler
fragments ("gathering clouds building", "nissan can fill") — and the engine's scoring
quality gate does NOT reliably reject them (NBER author names passed 6/6: "ulrike
malmendier stefan"). Because **expert-tier signals are exempt from the catch-all
corroboration floor**, that junk would have entered scoring through the HIGHEST-trust
pathway. Wiring these feeds through the existing extractor would have violated the
integrity standard.

**Fix implemented:** `research_entity_topics()` — ENTITY-ANCHORED extraction for
`mode="research_entity"` feeds. Keeps only capitalized runs containing a non-common-
dictionary word (real entities), trims Title-Case style words at phrase edges (never
below 2 words), allows single-word topics only for standalone mid-sentence proper nouns
(Temu, Maldives). Items with no clean entity write NOTHING (misses > junk). Also fixed:
`_parse_rss` ET fallback was namespace-blind (Atom/`xmlns` feeds returned empty titles —
production uses feedparser, but the fallback is now correct too).

## Per-outlet verdicts

- **War on the Rocks — PASS** (20 topics/15 items; real entities: shin bet, mossad,
  israeli intelligence, hizballah, chinese military, taiwan)
- **Rest of World — PASS** (10/12; china ai/ev, temu, maldives, nissan, ford)
- **Global Issues — PASS** (13/10; taliban rule, venezuela humanitarian, caricom leaders,
  saint lucia, ebola outbreak)
- **RAND (blog) — PASS** (17/15; texas screwworm, deterring russia, securing nato,
  psychedelics policy, angeles homelessness)
- **NBER — FAIL (2nd documented failure).** Academic paper titles extract author names as
  topics; items carry no dates. Excluded; do not re-add without a paper-title extractor.
- **Pew Research — FAIL as-is.** Feed mixes report sub-pages ("Methodology",
  "Acknowledgments", "Appendix B…") into items; "acknowledgments" survived the quality
  gate. Revisit only with a sub-page title filter.

**Residual noise estimate:** ~15–20% marginal fragments across the four PASS feeds
("history thrice", "deepening fast") — single-source, low-frequency; the fragment-prune
cycle and low volume bound the impact. Materially cleaner than the existing blog-feed
output. Honest trade: the extractor also skips some real topics (misses > junk).

## Premise test (does the D-expansion thesis hold?)

Of 59 unique clean topics extracted from the four PASS feeds today, **51 are NOVEL — not
in `velocity_scores` at all**; 8 corroborate already-tracked topics (china ai, ebola
outbreak, temu). These outlets genuinely surface material the engine currently does not
see — consistent with the 2026-07-07 feature-mining finding that current Dark Matter is
late-confirmation, not early-warning.

## Recommendation

Flip `GHOST_RESEARCH_FEEDS=1` for a **monitored two-week trial**: watch
`/monitor` topic-quality + catch-all auditors (fragment count, single-source leak) and
the ghost collector counts. Roll back by unsetting the flag (no data cleanup needed —
junk-guarding is at extraction; the 365-day retention rule is unaffected). Re-run the
LED-vs-LAGGED feature mining after the first-crossing cohort + these feeds accumulate.
