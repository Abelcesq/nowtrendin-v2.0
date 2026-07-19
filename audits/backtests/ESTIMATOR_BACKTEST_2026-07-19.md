# ESTIMATOR BACKTEST — D1 offline replay, run #1 (2026-07-19)

**Mandate:** Chairman-ordered D1 build (board record BOARD_estimator-fdm-snapshot2_2026-07-19.md).
Pre-registered candidates and gates; read-only endpoints-only replay over the servable window
(107 topics × ~26 cycles ≈ 2,765 reproducible cycles). Harness: `tools/estimator_backtest.py`;
raw numbers: `ESTIMATOR_BACKTEST_2026-07-19.json`. **Nothing ships from this run.**

## VERDICT FIRST (the honest one): NO CANDIDATE PASSES — THE INCUMBENT STANDS

The backtest did exactly what the board built it to do: it **refuted the naive versions of both
favored estimator families** under the registered gates, on real stored data. Per the Malkiel
null (a candidate flips ON only by beating the incumbent on the numbers), the integer median
survives round 1.

| candidate | flaps | cliffMax | plateau | mean det | delayed 70/85 | earlier | tailFail | verdict |
|---|---|---|---|---|---|---|---|---|
| INC (incumbent) | 5 | 78.7 | 95 | 49.21 | — | — | — | baseline |
| C1 dedup-window | 5 | 78.7 | 95 | 49.21 | 0/0 | 0 | 0 | no effect on this window |
| C2 interpolated median | 7 | 79.2 | 90 | 50.09 | 0/0 | 2 | 1 | **WORSE flaps; cliff unfixed** |
| C3a/b/c slew-limited | 0–2 | **14.7–18.6** | 19–27 | 51.6–53.1 | 0/0 | 2–3 | **1–4** | kills cliffs, **fails G2+G4** |
| +hysteresis overlays | (unchanged) | | | | | | | **vacuous — see below** |

## What each result means

- **G1 (enrollment invariance) passed everywhere** — zero delayed 70/85 crossings on every
  candidate, and the slew family produced 2–3 EARLIER crossings. The moat gate was never the
  problem.
- **C2 (the five-memo consensus candidate) is refuted**: the interpolated median produced MORE
  flaps (7 vs 5) and left the cliff untouched (79.2). The Executioner's bimodal-series
  argument — a pure quantile still steps on peak-hold data — is **empirically confirmed**.
- **C3 (the Executioner's slew family) fixes the artifact and fails the honesty gates**: cliffs
  collapse 78.7 → 14.7 (under the ≤20 registered bar), flaps → 0, plateau exposure 95 → 27,
  crossings never delayed. But the mean served detection rises +2.4 to +3.9 points (**G2
  no-inflation FAIL** — the slow-rising baseline holds post-surge scores elevated; max
  per-cycle uplift 79.6 where the incumbent had already cliffed) and genuine input collapses
  released ≥1 cycle slower on 1–4 occasions (**G4 tails FAIL**). This is precisely the
  Guardian/Outsider warning made measurable: taper-the-decay designs buy smoothness by
  serving stale highs longer. The gates exist for exactly this trade and they caught it.
- **Hysteresis was untestable**: the registered H_MARGIN derivation (fleet median absolute
  one-cycle factor change) returned **0.0** — most cycles are static, so the median is
  degenerate and the overlay never engaged. A future run must register a different derivation
  (e.g., median over NONZERO changes) — changing it now, after seeing results, is forbidden
  by the pre-registration discipline.

## Two material limitations (why this is round 1, not the final word)

1. **Reproduction gate: 82.2% vs the 95% registered bar.** The replay recomputes w from served
   fields only; tier-migration (+0.3 breadth), expert-community counts, and calibrating states
   are NOT served, so the incumbent itself cannot be perfectly reproduced from outside. Gate
   comparisons are therefore DIRECTIONAL, not ship-grade.
2. **Coverage: 1,789 of ~4,500 cycle-evaluations skipped** by the pathway-recovery det
   reconstruction (cycles lacking both an expert and a mainstream anchor). The candidate det
   series are real where computed and absent where not — counted, never fabricated.

Both limitations point the same way: a ship-grade round 2 requires an **ENGINE-SIDE replay**
(a read-only job with access to true per-cycle expert_detection / mainstream_detection and
the full 365d history), not a better endpoint harness.

## Recommendations to the Chairman

1. **Keep the incumbent estimator** (no engine change now). The artifact class it produces is
   already display-explained in production (input-freshness facts, known-mechanism ruling tags
   in the assessor) — the honesty layer shipped this week does the explaining while the
   estimator question matures.
2. If D1 is to continue, the next step is the **engine-side full-history replay job**
   (read-only, OPERATIONAL to build; its output returns to the board): true components remove
   both limitations above, and the slew family's G2/G4 failures get a fair re-test along with
   a properly-registered hysteresis margin and a down-side-taper variant if the board wants
   one designed.
3. The **C1 dedup-window fix rides along whenever an estimator change eventually ships**
   (it showed no standalone effect on this window, so it earns no expedited path), and the
   deploy-cluster row noise remains harmless to serving in the meantime.
4. Record this run in the D1 file as the standing "before" evidence — including that the
  incumbent's own cliffMax measured **78.7 points on static args**, the number any future
  candidate must beat WITHOUT failing G2/G4.

*Read-only throughout; no flag, no engine code, no serve-path change. The 365d retention and
ledger are untouched.*
