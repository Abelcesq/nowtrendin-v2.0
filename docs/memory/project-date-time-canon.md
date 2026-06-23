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

**ENFORCEMENT GAP + the guardrail (2026-06-23).** `gate_date()` is OPT-IN per call site, and
the `DATE_SEMANTIC` registry had NO consumer verifying compliance — so a path that BYPASSES the
gate (a hand-rolled `[:10]`) creates no review and is INVISIBLE to the gate's own nightly audit.
That is how two ledger `detection_date` slices survived the "complete" canon sweep
(`_record_top_detections` in `gravitational_anomaly_detector.py` + `validate_recent_detections`
in `google_trends_validation.py`). The data was NOT actually corrupted (the sliced inputs were
our own ISO `scored_at`/`first_at`, so `[:10]` happened to give a correct date) — it was a latent
code violation. Both now use `date_utils.to_iso_date`. **The guardrail: the Canonical Date Auditor
(Agent 16, `monitoring_agents.canon_date_auditor`, `/monitor/datecanon`, in `run_all`).** It audits
the DATA not the code path — every `DATE_SEMANTIC` column AND every `*_date` column DISCOVERED from
the live schema — so a bad date is caught regardless of producer and a NEW source is covered
AUTOMATICALLY (coverage by the column funnel + schema discovery, not a per-source list). Critical
only on declared columns; an unregistered `*_date` column = warn ("classify: gate it, or allowlist
as operational"); operational instants like `pending_detections.timeout_date` are allowlisted (full
ISO datetime is fine, it's a deadline not a sort key). Sinks (e.g. `record_detection`) also
normalize via `to_iso_date` (defense-in-depth). **When adding a date column: register it in
`DATE_SEMANTIC` + gate its writes, or Agent 16 flags it next cycle.** Verified live 2026-06-23:
status ok, 0 non-canonical across all 8 date-semantic columns.

**Ledger pending-backlog (same session).** The Accuracy-Ledger sweep (`sweep_pending`) had no
`ORDER BY` (re-checked the same head rows forever) + ran once/day at 8/run vs ~20 detections/score-
cycle inflow → 1066 stuck pending, with the slow-to-confirm LED wins stranded in the tail. Fixed
(safe set): (1) rotate oldest-checked-first; (2) past-deadline rows resolve FALSE_POSITIVE with NO
Apify fetch; (3) own cadence `LEDGER_SWEEP_INTERVAL_HOURS` (default 6h), env-tunable vs Apify budget.
Deferred (backtest-gated): shorten `LEDGER_TIMEOUT_DAYS` 90→~45; prioritize fetches by window+conviction.

See [[serve-payload-cache-gotcha]], [[feedback-verify-before-ship]], [[project-read-path-prewarm]],
and [[feedback-integrity-standard]]. The nightly audit (`nowtrendin_data_adapter.py`) is
read-only/stored-data-only — see [[deploy-topology]].
