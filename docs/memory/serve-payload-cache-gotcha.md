---
name: serve-payload-cache-gotcha
description: "After ANY scoring/calibration change you MUST regenerate velocity_scores.serve_payload, or /scores + detail serve stale precomputed values. And apply_calibration lives in signal_calibration_integration.py, not calibration_engine.py."
metadata: 
  node_type: memory
  type: project
  originSessionId: 46ab8dd5-70c6-49dc-8816-b88ccdd2bb93
---

Two non-obvious traps when changing engine scoring/calibration (cost a long debug 2026-06-18):

**1. serve_payload is a precomputed cache that masks code changes.**
`/scores` (and now `/scores/{key}` detail + `/topics`) read a fully-calibrated row
from `velocity_scores.serve_payload` (a JSON column) via the FAST PATH in
`_format_score_rows` — they only fall back to live `_calibrate_score_fields` when the
payload is NULL. So after editing `apply_calibration` / `_calibrate_score_fields` /
scoring, the endpoints keep serving the OLD payload until it's regenerated. Symptom:
score-history (which live-calibrates, no payload) shows the NEW value while /scores
shows the OLD one. Fix: regenerate with
`python -c "import gravitational_anomaly_detector as g; g._precompute_serve_payloads(600)"`
(it clears ALL payloads first, then rebuilds) — or trigger a full re-score. The
scheduler's `_score_phase` does this every cycle, and the local worker does on its
runs, so it self-heals next cycle; regenerate manually for an immediate fix. NOTE the
web dyno also has an in-memory response `_cache` — a one-off dyno's precompute can't
invalidate it; use a novel `?limit=` to bypass when verifying, or it clears on the
deploy restart / next `/score-all` (which calls `_cache.invalidate()`).

**2. The live `apply_calibration` is in `signal_calibration_integration.py` (~line 1029),
NOT `calibration_engine.py`.** The engine imports it from signal_calibration_integration
(gravitational_anomaly_detector.py:199). calibration_engine.py has a same-named function
that is NOT called. Edit the wrong one and nothing changes.

**The fix that lives here now (dual-pathway gate):** at serve+scoring, the
Detection/Confidence/Overall expert-component recompute is GATED to expert/niche
pathway. Mainstream/blended topics PRESERVE their dual-pathway headline — otherwise the
expert formula (G≈0 for mainstream) collapsed every mainstream topic to ~25-28
(FIFA/Trump/Juneteenth all ≈27, unrankable). See [[gradient-calibration]] and the Trend
Signal Diagnostic. Three serve paths (`/topics`, `/scores`, `/scores/{key}`) now all
prefer serve_payload = single source of truth. See [[deploy-terminal-ghpages]].
