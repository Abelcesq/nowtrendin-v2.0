# Now TrendIn 2.0 — Update Verification

**Date:** 2026-06-06
**Scope:** verify the two fixes from the calibration-file review + full live health test before deploy.

---

## Changes in this round

1. **Backend — stray multiplier fixed.** `signal_calibration_integration.py` `recompute_velocities()`
   still reset ESTABLISHED topics to the *old* `0.25` (and MONITORING `0.55`, NEW `0.75`). Aligned
   to the corrections-doc values already live elsewhere: **ESTABLISHED 0.40 · MONITORING 0.60 · NEW 0.80**.
   Affects the daily velocity re-classification job only (serve path was already 0.40).

2. **App — maturity badge surfaced.** The payload exposes `calibration.maturity_class` +
   `maturity_badge` (verified live) but the app never rendered it. Added:
   - `maturityClass` / `maturityBadge` / `maturityReason` to the `Signal` model + `mapSignal`.
   - `maturityColourHex()` palette helper.
   - A maturity badge on the signal-detail screen (e.g. `🔵 New Signal`; ESTABLISHED shows
     "gradient reflects permanent expert home").

---

## Live health test (pre-deploy)

**Endpoints — all 200:**

| Endpoint | HTTP | Time |
|---|---|---|
| `/scores?limit=20` | 200 | 1.24s (warm <0.5s) |
| `/x/budget` | 200 | 0.33s |
| `/risk/scores` | 200 | 0.34s |
| `/trending` | 200 | 0.36s |
| `/anomalies` | 200 | 0.36s |
| `/enterprise/methodology` | 200 | 0.28s |
| `/scores/{key}` | 200 | 0.30s |
| `/explainer/{key}` | 200 | 4.73s (on-demand Perplexity, then cached) |
| `/enterprise/scores/{key}/audit` | 200 | 0.29s |
| `/enterprise/scores/{key}/scenarios` | 200 | 0.30s |

**Payload completeness (live list row):**
- N: `nowtrendin_score = 66.37`, and **same value in `component_groups`** (66.37) ✓
- Maturity: `maturity_class = NEW`, `maturity_badge = "🔵 New Signal"` ✓ (app badge will render)
- Dark Matter: `dark_matter_score`, `first_timer_ratio`, `engagement_asymmetry` all present ✓
- `total_mentions = 97` (real topic; mentions floor working) ✓

**Database:** connections **4/20** (healthy headroom).

**Typecheck/syntax:** backend `ast.parse` OK; frontend `tsc` clean on all changed files
(only the two pre-existing unrelated errors in `notifications.tsx` / `risk/[key].tsx` remain).

**Verdict:** ✅ all updates functioning. Cleared to deploy.

---

## Calibration-file review conclusion (this round's source files)

All six reviewed files (`updates 1/calibration/*`, `Temp/*`) are **older staging/source copies**;
the live engine supersedes each. The corrections-doc fixes (`is_meaningful_topic`,
`apply_signal_count_modifier`, `apply_ai_floor`, ESTABLISHED multiplier 0.40) are confirmed live.
The only gaps found were the stray `0.25` and the app maturity-badge display — both fixed above.
