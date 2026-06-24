# Now TrendIn — Engine Integrity Monitor

`monitoring\integrity-check.ps1` runs nine automated checks against the live Heroku scoring engine
(`https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com` — the v2 engine, the ONLY active one;
the legacy `nowtrendin-e62dcb9ecb69` is frozen 1.0, do NOT QA it) and prints a colour-coded PASS / FAIL / WARN / INFO
report to the console. Exit code is **1** if any check FAILs, **0** otherwise — making it safe to
run from CI or a scheduled task.

## How to run

```powershell
# From the repo root
powershell -ExecutionPolicy Bypass -File .\monitoring\integrity-check.ps1
```

No dependencies beyond the Windows PowerShell 5.1 standard library. Internet access is required
(the script issues GET requests only).

Suggested cadence: **daily** (e.g. 06:00 UTC), and additionally after every engine deploy.

---

## Checks

### Check 1 — Health endpoint (`GET /health`)

**Protects:** Basic engine availability. A FAIL means the Heroku dyno is down, sleeping, or returning
an unexpected status string. No other check is meaningful if the engine is unreachable, so this is
always the first gate. A FAIL here should trigger an immediate alert.

### Check 2 — Score list ranges (`GET /scores?limit=50`)

**Protects:** Core numeric integrity of the scored feed. Every row must have a non-empty `topic_key`
(otherwise the mobile app cannot navigate to a detail screen) and every score field
(`detection_score`, `confidence_score`, `overall_score`, `nowtrendin_score`) must be in the
mathematical range [0, 100]. A FAIL means a calibration pipeline bug or a DB corruption has allowed
an impossible value into the served feed, which would break client-side progress rings and tier-gate
comparisons.

### Check 3 — Trade-secret hygiene (`GET /scores/{topic_key}`)

**Protects:** Proprietary algorithm confidentiality. The Gradient Score weighting formula is a core
intellectual property asset. The API must never expose `weight_overall`, `weight_detect`, or
`weight_conf` on any component object, nor `false_positive_detect` or `false_positive_confirm` on
the `heisenberg` block. A FAIL means a code regression has re-exposed the trade-secret fields —
strip them immediately and redeploy. See the hygiene block at the bottom of `get_topic_detail` in
`gravitational_anomaly_detector.py`.

### Check 4 — What-if fields presence (`nowtrending_gradient_*`)

**Protects:** The "Now Trending Gradient Score" demand-inclusive what-if feature (added in the
2026-06-11 deploy). When the N-component score is greater than zero the detail response's
`velocity_scores` block must contain all three fields: `nowtrending_gradient_detection`,
`nowtrending_gradient_confidence`, and `nowtrending_gradient_demand_driven`. A FAIL on the detail
endpoint means the `_now_trending_gradient()` helper is not being called or its result is not being
merged. List rows may legitimately be missing the fields until the worker re-scores all topics
(hence a WARN rather than FAIL on the list path).

### Check 5 — Demand-driven logic guard (`nowtrending_gradient_demand_driven`)

**Protects:** Transparency and anti-manipulation. The `demand_driven=true` flag signals that
internal query demand is outpacing thin external evidence. The guard condition requires
`total_mentions < 15` (half-sufficiency of the 30-mention floor). A FAIL means the flag has fired
on a topic with substantial external evidence, which would incorrectly show a transparency warning
to users viewing a well-evidenced trend. If FAILs appear, inspect `_N_SUFFICIENCY_FULL` and the
`suff < 0.5 and n > det` condition in `_now_trending_gradient()`.

### Check 6 — Frozen-score detector (`GET /scores/{topic_key}/score-history`)

**Protects:** Scoring liveness. If the 8 most recent history entries for a top-5 topic all share
an identical `detection` value, the score is frozen — the engine is re-storing the same value
every cycle rather than re-computing. The 2026-06-11 deploy introduced the continuous
`platform_diversity` formula specifically to break this saturation (the old flat-90 cap caused
the M component to stop contributing variation). A WARN rather than FAIL is used here because
transient repetition (e.g. a topic genuinely unchanged across a few cycles) is not a bug; only
strictly identical values across all 8 cycles are flagged.

### Check 7 — Platform-diversity spread (informational)

**Protects:** Confirms the continuous `platform_diversity` formula is actually flowing into served
data. The legacy scoring formula emitted only the anchor values `{0, 20, 35, 50, 65, 80, 90, 95,
100}`. After the PLATFORM_DIVERSITY_CONTINUOUS deploy any topic spanning 4+ platforms receives a
fractional value (e.g. `92.0`, `93.33`) instead of the flat `90`. Seeing non-legacy values in the
feed proves the new code path is live and that `_precompute_serve_payloads` has refreshed at least
some rows. If only legacy anchors appear, the worker has not yet re-scored any multi-platform
topics since the deploy — wait one collection cycle (~1 h) and re-run.

### Check 8 — Stage values (`signal_stage`)

**Protects:** Client rendering and filter logic. The mobile app tier-gate, history screen, and
badge renderer all switch on a closed set of stage strings:
`BREAKOUT / STRONG / EMERGING / WATCHING / MONITORING / VIRAL / DECAY / WATCH`.
A FAIL means an unknown string has been written to the database (e.g. a typo in a new calibration
rule), which would cause the frontend badge to fall through to a default/blank state and potentially
break filter queries.

### Check 9 — Accuracy endpoint + collector trust

**Protects:** Two ancillary systems. `/accuracy` returning a 200 confirms the accuracy ledger is
operational (used by the AccuracyView leaderboard in the app). A FAIL means the ledger query has
broken and the track-record screen will be blank. `/health/collectors` with `trust=false` is a
WARN rather than FAIL because collection can be temporarily interrupted without invalidating cached
scores; however a prolonged `trust=false` means the pipeline is half-blind and re-scored cards will
carry stale signals — escalate if it persists beyond two collection cycles.

---

## Informational telemetry

The script also reports **X post-budget consumption** by calling `GET /x/budget` with the internal
key. This is read-only telemetry that shows how much of the monthly 12,000-post cap has been used.
No write or administrative action is performed.
