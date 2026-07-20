# ESTIMATOR BACKTEST — ROUND 2 (engine-side, full served-universe panel)

**Commissioned by the Chairman 2026-07-19.** Engine-side chunked replay
(`transfer/estimator_replay.py`, endpoints `/backtest/estimator/step|report`), read-only,
single-flight, batch-paced; corpus = ALL quality-gated topics active in the last 30 days
(**32,989 topics**, up to 400 stored cycles each — the full served universe, ~200× round 1's
panel). Junk drained via prefilter (479 marked). **Reproduction gate: 95.5% — ABOVE the 95%
registered bar.** Unlike round 1, this gate table is valid evidence.

## VERDICT: EVERY CANDIDATE FAILS — THE INCUMBENT STANDS, DECISIVELY

| candidate | flaps | cliffMax | plateau | delayed 70/85 | tail fails | gates failed |
|---|---|---|---|---|---|---|
| **INC (incumbent)** | 92 | 78.7 | 6001 | — | — | baseline |
| C1 dedup-window | 85 | 79.9 | 6826 | **10 / 6** | 8 | G1, G4, G5, P |
| C2 interpolated | 73 | 80.2 | 3310 | **9 / 4** | 38 | G1, G4, G5 |
| C3b slew Δ/8 | 40 | 37.3 | 4665 | **5 / 3** | 167 | G1, G2, G4, G5 |
| C5 slew+snap | 46 | 37.3 | 5512 | **5 / 3** | 44 | G1, G2, G4, G5 |
| hysteresis overlays | (no material change) | | | | | same as bases |

## What the full panel settled that the small samples could not

1. **G1 (enrollment invariance) is the killer, and it kills EVERYTHING — including dedup.**
   On the full universe, every candidate — even the "bug-class" C1 dedup-window fix —
   produced delayed enrollment-floor crossings (10 topics for dedup alone). Changing window
   composition changes crossing times in BOTH directions somewhere in 33k topics; the zero-
   delay bar is absolute (the moat), and no member of this candidate family clears it.
   The board's instinct to gate even the dedup fix behind this backtest (never a hotfix)
   is vindicated by its own failure.
2. **The slew family's trade is intrinsic, not a small-sample artifact**: cliffs halve
   (78.7→37.3, still above the ≤20 bar), flaps halve, but inflation (G2) and slow tail
   releases (G4: 167 events; C5's genuine-collapse snap cuts them to 44 but not to zero)
   persist at scale. Taper designs buy smoothness with staleness; the gates price that
   trade correctly and reject it.
3. **The hysteresis overlays were immaterial** even with a valid fixed margin — the flap
   phenomenon on the full panel is dominated by window-composition and median-catch-up
   dynamics, not by marginal re-crossings.
4. Round 1's directional readings were confirmed in every particular by the valid round —
   the endpoint harness under-measured but did not mislead.

## DISPOSITION (per the Malkiel null and the board's own discipline)

- **No estimator change ships. D1 closes with the incumbent standing** — now proven against
  two rounds, eight candidates, and a full-universe panel at valid reproduction. A number we
  cannot defend is worse than no number; equally, a "fix" that delays a single enrollment
  crossing spends the moat, and every fix on the table does.
- The cliff/flap artifact class remains **display-explained in production** (input-freshness
  facts on all three platforms; known-mechanism ruling tags in the assessor; D6 disclosures) —
  the honesty layer is the shipped fix.
- **D2 step 2 (dedup-in-query) is WITHDRAWN** on this evidence — it fails G1 on its own.
  The off-cycle rows stay harmless-by-explanation; the assessor's B.dup_cycles shadow check
  keeps watching them.
- Any future attempt needs a **fundamentally different design** (e.g., recomputing true
  per-cycle components from raw signals rather than re-weighting stored aggregates), arrives
  as its own registered round, and faces the same gates. Nothing in this round licenses
  loosening a gate to let a candidate through — that is the Goodhart door and it stays shut.

Raw numbers: `round2_report.json` (this folder). The replay results table
(`estimator_replay_results`) remains in the DB as the standing evidence base; the endpoints
stay available for future registered rounds.

*Read-only throughout: no score, no serve path, no ledger touched; 365d retention intact.*
