---
name: project-date-time-canon
description: "Canonical date/time model, Ingestion Gate, and same-surge ledger matching for the v2 engine"
metadata: 
  node_type: memory
  type: project
  originSessionId: 365856a3-a15a-4e81-b551-17dcfef7ec5c
---

The v2 engine (transfer/) has a hard canonical date/time model — never reintroduce raw
date slicing (`[:10]`) or store a provider's date verbatim.

**Canonical rule.** Every date-semantic column is primary ISO `YYYY-MM-DD`; time is
secondary. The single normalizer is `transfer/date_utils.py`: `to_iso_date()` (→ `YYYY-MM-DD`),
`to_iso_dt()` (→ ISO datetime), `iso_time_of()` (→ `HH:MM:SS`, `default_now` controls the
empty-source fallback). Tries whole-string formats first (a naive space-split once sliced
`'May 22, 2026'`→`'May'` and silently dropped 13 ledger rows).

**Ingestion Gate** (`transfer/ingestion_gate.py`) is the condition-precedent filter: every
date-semantic write goes through `gate_date()`, which normalizes and, on an unparseable
value, QUARANTINES it to `format_review_queue` (surfaced as a nightly-audit alert) instead
of guessing. `DATE_SEMANTIC` registry lists the gated columns.

**Schema (migrated 2026-06-22).** `market_signal_history`: `cycle_at` RENAMED → `signal_date`
+ `signal_time` (our cycle time). `get_market_baselines` keys cycles on (signal_date,
signal_time) — byte-identical ordering to the old timestamp, so market scoring is unchanged.
`risk_signals`: `signal_date` + `source_time` (the SOURCE's time-of-day, empty if date-only)
+ `signal_time` (OUR pull time, always `HH:MM:SS`) + `collected_at` (full pull instant). Risk
recency keys on signal_date, so scoring is unaffected. `positioning_history.cycle_at` is a
SEPARATE column — left untouched (already consistent). market_signal_history has NO source_time
(its rows are our own measurements, no external source time).

**Same-surge ledger matching** (the stale-match fix). `google_trends_validation.detect_breakout_date(curve, since=...)`
takes a same-surge floor: only breaches on/after `(detection − MATCH_WINDOW_DAYS=30)` count, so
a June detection matches the June surge, not an earlier Spring spike (the −41d/−92d artifacts).
`sweep_pending` and `validate_topic` pass `since`; `validate_topic` also got the C1 gate
(breakout still outside ±MATCH_WINDOW → `LATE_REDETECTION`, excluded from the honest denominator).

See [[serve-payload-cache-gotcha]] and [[feedback-verify-before-ship]]. The nightly audit
(`nowtrendin_data_adapter.py`) is read-only/stored-data-only — see [[deploy-topology]].
