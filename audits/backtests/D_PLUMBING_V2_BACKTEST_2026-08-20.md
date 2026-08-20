# D_PLUMBING_V2 — held-out backtest (flag stays OFF pending Chairman flip)
### 2026-08-20 · read-only recomputation over live production signals · board decision item 1

## What was backtested

The three board-verified plumbing repairs, gated as ONE regime flag (`D_PLUMBING_V2`,
default OFF — live scores are bit-identical to before this build until the flip):
1. **(1a) writer fix** — blog collectors now pass the REAL `_first_timer()` bit into
   `topic_signals` (was a hardcoded `0` for every blog/newsletter/ghost/discourse row).
   **Forward-only**: historical rows keep their stored 0 and cannot be repaired — the flip
   date is the epoch boundary, recorded in the regime ledger.
2. **(1b) denominator fix** — `ft_ratio` over author-bearing signals only (the behavior the
   function's own comment always claimed).
3. **(1c) community-age guard** — no first-timer credit until our collection of the
   community is ≥ `D_COMMUNITY_MIN_AGE_DAYS` (14) old; authors are still recorded during
   calibration, so history accrues. Kills the cold-start fabrication that would have let
   the shadow trial manufacture its own positive result (Guardian F2).

Plus (ungated, measurement-only, live at next deploy): **`d_measured`** — the honest-absence
tri-state stored per score row (NULL=pre-epoch, 1=readable, 0=structurally blind).

## Method + limits

Recompute `compute_dark_matter` under BOTH regimes for every topic scored in the last 72h
with ≥3 signals (n=800, the full eligible working set), from the live signal store.
**Limit stated plainly: the operational signal tables carry ~7-day retention** (the GHOST
close-out's finding), so no LED-cohort replay is possible — the historical LED rows'
signals are pruned. This is the maximal honest backtest available; the LED-cohort test of
the repaired instrument is exactly what the A4 shadow trial exists to run.

## Results (n=800 topics)

| Measure | OLD (live) | NEW (V2) |
|---|---|---|
| D mean | 9.49 | 10.66 |
| D median | 0.00 | 0.00 |
| Topics with D>0 | 268 | 245 |
| Topics moving ≥5 points | — | **92 (11.5%)** |
| Topics structurally UNMEASURED (`d_measured=0`) | — | **259 (32.4%)** |

- **No inflation regime**: mean moves +1.2; the median stays 0; FEWER topics carry a
  nonzero D under V2 (245 vs 268 — the age guard and clean denominator remove noise credit
  even as real reads rise).
- **The movers are the thesis cohort**: the largest gains are mixed news+expert topics —
  `norway` 12→46, `nvidia` 9→40, `openai` 22→47, `france` 8→34, `anthropic` 30→53 —
  precisely the Guardian's sealed prediction ("the near-miss cohort's D rises most, because
  those topics had early news volume diluting a real expert influx"). The dilution defect
  was structurally anti-correlating D with breadth; V2 removes that.
- **32.4% of the working set is structurally blind to D** — now disclosed per row instead
  of served as a quiet 0. This number is the honest scope statement for any D claim.

## Flip conditions (unchanged, per canon)

Score-affecting → the flag flips only on Chairman sign-off. On flip: regime-ledger entry +
`param_version` note + serve_payload regeneration (G1) + the flip date becomes the shadow
trial's instrument epoch (freeze thereafter). Recommended flip timing: BEFORE 2026-09-01 so
the trial runs entirely on the repaired instrument, never across the boundary.
