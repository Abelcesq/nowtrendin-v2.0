# CONTAMINATION STATEMENT — the dead insider parser
**Date:** 2026-07-25 · **Status:** standing record, referenced from `MARKET_SIGNAL_V2.md`
**Rule applied:** ledgers are never deleted; contamination is stamped, never erased. Where we
know, we state numbers; where we cannot know, we state the bound and why. Nothing here is
fabricated precision.

## 1. What broke, precisely

The primary insider source (Finviz Elite, `transfer/finviz_data.py` — PRIMARY per CLAUDE.md §15,
flag `FINVIZ_INSIDER=1`) had two independent defects:

**(a) Doubled-ticker parsing.** The feed's ticker cell renders a one-letter logo-fallback
initial before the ticker text; tag-stripping concatenated them, so **every** ticker parsed with
its first letter doubled (LEVI→LLEVI, NOC→NNOC, AAPL→AAAPL — verified on live data,
**111 of 111 distinct tickers**). Consequences:
- `insider_signal(ticker)` filters rows on exact ticker match → the filter never matched →
  **zero rows returned for every symbol, always**, failing as `available: False` ("no data")
  rather than as an error anyone would notice.
- Any consumer of the market-wide feed grouping by ticker received **misattributed** rows
  (wrong-ticker-shaped, not just absence-shaped).

**(b) Form 144 counted as executed sales.** "Proposed Sale" — a Form 144 *notice of intent*,
not an executed Form 4 transaction — was substring-classified as a sale (`"proposed sale"`
contains `"sale"`). Live sample: **53 of 200 rows (26.5%)**. Those same rows were also
column-misaligned (different cell count shifted every field left: timestamps in `shares_total`,
empty `filed`).

Both defects are fixed in code (commit `7bd9849`): unambiguous ticker recovery from the logo
URL/alt (which correctly preserves MMM), exact-match transaction classification (`F144` is its
own class, never a sale), and misaligned-row rejection at the parser. The classification fix is
ungated (wrong on both branches); the parser fix ships behind `INSIDER_PARSER_FIX`
(default `"0"`) and flips with before/after capture per the R7 pattern.

## 2. The period, honestly bounded

Git bounds the **code**: the parser was written **2026-06-25** (Finviz onboarding, `[source-
onboarded]`) and was untouched until **2026-07-25**. What cannot be determined: whether the
parser worked on day one and Finviz's HTML later changed (adding the logo-initial markup), or
whether it was born broken and the onboarding gate-5 sample did not exercise the per-ticker
filter path. **No raw HTML snapshots were retained, so the onset date is unknowable.**

Therefore: **the worst-case contamination window is the source's entire life as primary insider
input, 2026-06-25 → 2026-07-25 (~30 days). The window cannot be bounded tighter, and we do not
pretend otherwise.**

Standing fix so this paragraph is never written again: the recurring gate-5 assertion (master
remediation, Part C control #2) archives its daily sample rows — every future window is
boundable by construction.

## 3. Which numbers are affected, by shape

**Absence-shaped (a component that read "no data" when data existed):**
- The **Insider Tracking** component of every Market Signal in the window: with Finviz dead,
  reads came only from the Alpha Vantage fallback (25 calls/day cap) — 5→17 of ~300 instruments
  ever carried a scored value; the rest served honest absence per §16a/§17. This is
  contamination of **coverage**, not fabrication: the display said the read was absent, and it
  was. What was wrong is that absence was involuntary and unalarmed.
- **Crypto proxy dark matter** in the window: proxy positioning went degenerate downstream of
  the dead parser; all 12 coins fell to `money_data_absent`. Also involuntary.

**Wrong-value-shaped (a number that existed and was wrong):**
- Any in-window consumer of the market-wide feed keyed by ticker (misattributed rows).
- In any pre-doubling period (if one existed — see §2), Form 144 intents inflated insider
  *sell* totals and could bias `flow` toward outflow. `flow` is what the market accuracy
  ledger enrolls on.
- The **BTC contradiction** specifically: a single AV-fallback proxy vote served as
  `flow: "inflow", intensity: 60.0` beside all-absent money components (fixed 2026-07-25 by
  the contradiction guard; the two crypto-ledger rows it produced are annotated below).

## 4. What we did with the ledgers

**Nothing is deleted — ever.**
- **Crypto accuracy ledger:** the 2 rows enrolled in the window (1 CONFIRMED inflow lead-18d +
  1 pending) were produced by the single-proxy AV-fallback read while the serve payload said
  the money read was absent (C2b). They remain in the record, are reported as the
  **`dead_parser_era` cohort** (boundary env `CRYPTO_LEDGER_CLEAN_COHORT_START`, set at the
  parser flip), and never blend into a cited post-fix rate. No crypto rate is published at all
  below 20 resolved episodes.
- **Market accuracy ledger:** rows in the window enrolled on `flow` derived from congress net
  (Finviz contributed nothing — it was returning zero rows). They are a legitimate record *of
  the congress feed*; the master remediation's A5 labelling (enrollment-source disclosure)
  covers them. Post-fix detections form the citable cohort per the citability order (Part C
  control #5).

## 5. Why this happened, in one sentence, and the control that prevents recurrence

Absence and failure shared a code path — a source dead across 100% of the universe was
indistinguishable from a source with nothing to say — and both discoveries were made by a human
running a gate-5 sample by hand. The **source-liveness contract** (master remediation Part C
control #1: per-source coverage floors; RED on zero usable rows across the whole universe; the
acceptance test is replaying this exact corpse) is the standing control. Until it ships, this
statement is the record that the gap is known, bounded where boundable, and disclosed where not.
