# D2 DEDUP DIAGNOSTIC — duplicate/off-cycle scoring rows (step 1, read-only)

**Mandate:** Chairman-ruled D2 step 1 (board record BOARD_estimator-fdm-snapshot2_2026-07-19.md):
quantify duplicate-cycle rows fleet-wide, correlate with deploys, and replay britain's
07-18T10 dip with a deduplicated window. Endpoints-only, zero writes; script: scratchpad
`dedup_diag.py`. Scan: 150 top-served topics, their served 30-row histories.

## FINDING 1 — off-cycle rows are ENDEMIC, not rare
**130 of 150 topics** carry extra rows: **113 same-hour duplicates + 689 short-gap (<3h)
extras** inside 30-row windows on a ~6h cadence. The assessor's 20-dup reading (hour-bucket
only, 60-topic cohort) undercounted by design — the fuller inter-row-gap metric shows the
real scale: roughly one in six rows of recent history is an off-cycle scoring run.

## FINDING 2 — the big clusters are DEPLOY-CORRELATED; the rest are explainable ops
The largest clusters sit inside 90 minutes of Heroku releases:
- **2026-07-19T03–04: 176 extra rows** — the v247–v250 deploy sequence (02:07–03:33 UTC).
- **2026-07-15T20/22/T16T00: ~204 extra rows** — the three 07-15 releases (20:31/22:29/23:45).
- June clusters (06-26/27, 06-22, 07-05/06/07) align with known heavy deploy sessions.
Mechanism: the engine scores on BOOT (deliberate freshness behavior), so every deploy inserts
a full off-cycle scoring pass ~15–20 min after release. A second legitimate source exists:
user-triggered **Pull Trends** runs (the Enterprise button) also insert off-cycle rows.
**Neither source is illegitimate** — the defect is that the baseline window is defined in
ROWS (`LIMIT 12`), so any off-cycle run silently shrinks the window's TIME span (12 rows can
now cover ~1.5 days instead of ~3), which moves the median without any attention change.
This is the Expansionist's "window specced in cycles, not time" scale-trap, measured live.

## FINDING 3 — britain's dip is NOT dup-caused (honest refutation)
Replaying her 2026-07-18T10:15 dip cycle (served det 24.0, stored w=0.0) with the exact
engine formulas (upper-median of 12; mf=(mag−base)/35, bf=(n−base)/3, clipped):
- RAW window (engine as-is): magBase=54.49, brBase=27 → mf=0.000, bf=0.000, w≈0
- DEDUPED window (candidate): identical — magBase=54.49, brBase=27 → w≈0
Both windows produce the same collapse because the topic sat at CONSTANT mag 54.49 / 27
platforms long enough for the upper-median to exactly EQUAL the current values — deviation
0 at the boundary. One old row leaving the window later tips the median back below 54.49 and
w snaps back to 1.0. **britain is a genuine marginal-deviation boundary oscillation** — the
exact case D1's hysteresis (the re-crossing-only Schmitt design) targets. The dup hypothesis
for this specific glitch is refuted; the instance stays in D1's evidence file.

## IMPLICATIONS FOR STEPS 2–3 (for the Chairman's ruling; nothing changed yet)
1. **The window fix matters MORE than britain suggested, for a different reason**: dups don't
   explain her flap, but with ~1-in-6 rows off-cycle fleet-wide, every topic's "12-cycle
   baseline" is silently time-warped after each deploy day. The Executioner's B1 (one row per
   cycle slot in the baseline query — dedup at READ time, never deletion) or the
   Expansionist's time-based window definition remains correct and now has fleet-scale
   evidence. It changes w on some cycles ⇒ **rides D1's flag + backtest**, as ruled.
2. **Step 3 (source suppression) is now OPTIONAL/ops-only**: boot-scoring and Pull-Trends
   are deliberate features; the row-window fix makes their extra rows harmless to the
   baseline. Suppressing boot scoring would only save compute — a cost decision, not an
   integrity one.
3. The assessor's B.dup_cycles check should adopt the inter-row-gap metric (<3h) alongside
   hour buckets at its next param bump (its current reading undercounts ~6×).

*365-day retention untouched; all rows remain stored; read-only throughout.*
