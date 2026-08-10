# NowTrendIn — Data Dictionary (buyer-facing)
**Version 0.9 · 2026-08-09 · Accurate-but-not-yet-exhaustive: field CLASSES, vintage
stamps, cadences, and revision policies below are verified; an exhaustive per-field
enumeration pass is the remaining Phase-1 item (a wrong dictionary is worse than a
partial one — App Annie rule).**

## 1. Product surfaces (endpoint families)

| Family | Unit | What a row is |
|---|---|---|
| `/scores`, `/topics` | topic | Current calibrated read per topic: Gradient Score with component breakdown (breadth/intensity/mainstream/dark-matter/confidence/persistence classes), detection + confidence reads, stage label, display category, maturity class, and the platform indicator N (NEVER inside the score) |
| `/history/recent`, `/history/{topic}` | topic × cycle | The VINTAGE series: one row per scoring cycle with the scores as they were computed then (`scored_at` stamp) — the point-in-time panel, 365-day retention |
| `/risk/scores` + market detail | instrument | Money Gradient: Money Movement + Market Confirmation components, tier labels, coverage lane, factual flow/leverage facts; `signal_date`/`signal_time` canon |
| `/crypto`, `/crypto/{coin}` | coin | Coin-level Money Gradient (proxy Dark Matter + price leg), served from the prewarm cache |
| `/accuracy/ledger`, `/market/accuracy`, `/crypto/accuracy`, `/flow/accuracy` | detection/verdict | The held-out track records: enrollment rows, verdicts (LED/SAME_DAY/LAGGED/±; CONFIRMED/NOT_CONFIRMED/NO_MOVE), leads, referee flags, param-version stamps, null-model comparators, withheld-by-design rates with their publication thresholds |

## 2. Field classes and their semantics

- **DERIVED scores** (0–100 or 0–1): computed each cycle from admitted external
  signals; weights single-sourced from a version-controlled module; calibration is
  versioned. Never averaged across legs.
- **RAW aggregates**: source counts, engagement sums, share counts, prices — stored
  as fetched (see the lineage statement: no interpolation; format-only alteration).
- **METADATA**: stage/category/maturity labels (display-only, non-circular by
  construction), provenance stamps (`src`, `platform_tier`), coverage lanes.
- **MEASUREMENT fields** (ledgers): verdicts and leads are immutable once resolved
  (status flips only, never deletion); every rate rides with `param_version`.

## 3. Vintage stamps (where point-in-time lives)

| Stamp | Meaning | Carried on |
|---|---|---|
| `scored_at` | when this score row was computed | every velocity/history row |
| `collected_at` | when the raw signal was fetched | every raw signal |
| `captured_at` | capture instant (μs precision on issuer rows) | ETF share observations/strikes |
| `signal_date` / `source_time` / `signal_time` | canonical event date / source's own clock / our fetch clock | risk + market rows |
| `verdict_at`, `validated_at` | when a ledger verdict was (re)computed | ledger rows |
| `param_version`, `series_epoch`, `src` | which measurement definition / series lineage / data source produced the row | ledgers; market baselines; ETF rows |

**Revision policy:** score history is append-per-cycle and never rewritten; served
current reads for stale rows serve stored values verbatim (no retroactive
recalibration); ledger verdicts re-computed under the SAME rule version refresh
`verdict_at` in place, and any semantic change ships under a new version or with the
prior rows archived (annex A2-N1.2). Withheld rates (`null` + reason) are a design
state, not missing data.

## 4. Update cadences

Collect cycle ~6h (attention + risk) · ETF share snapshots 4h · ledger sweeps daily
(paid-slot capped) · X scans 12h · serve caches prewarmed ~25min · accuracy reports
recomputed on read from stored rows.

## 5. Identifiers

Instrument legs: exchange ticker per row; FIGI mapping table live (OpenFIGI,
`figi_map`) for watchlist + ETF proxies + crypto proxy equities. Attention leg:
`topic_key` (canonical normalized key) — deliberately NO instrument identifier
(topics are not securities; forcing a mapping would misdescribe the data).
