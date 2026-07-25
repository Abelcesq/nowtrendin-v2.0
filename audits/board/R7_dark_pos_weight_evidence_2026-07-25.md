# R7 — `DARK_POS_WEIGHT=0` : before/after evidence record
**Date:** 2026-07-25 · **Ruling:** Chairman approved (Board round 1, 6/6 against the blend as wired)
**Mechanism:** config-only, no deploy, no code change. Rollback: `heroku config:unset DARK_POS_WEIGHT`.

## What is being changed and why

`market_signal_engine.py:~493` blends the held-out `positioning_intel.positioning_signal`
into `positioning_concentration` at weight 0.4:

```python
pos_conc = _norm(pos_conc * (1 - DARK_POS_WEIGHT) + float(_sig) * DARK_POS_WEIGHT)
```

With `DARK_POS_WEIGHT=0` this reduces to `_norm(pos_conc * 1.0 + sig * 0.0)` = `_norm(pos_conc)`,
and `pos_conc` is already `_norm`'d on the line above — so the result is **byte-identical to the
unblended value**. No code path is removed; the attach sites at
`financial_risk_gradient.py:2371/2567` are deliberately **left untouched**, because gating those
would empty `payload['dark_positioning_intel']`, blank `flow`, and silently stop the market
accuracy ledger from recording (Executioner, round 1 — "that is the trap").

The Board's grounds (6/6): the blended quantity is **directionless** (`flow` never reaches the
score, so congressional *selling* raises the component as much as buying); ~0.6 of it is
`funds_holding`, sourced from the top-10 holdings of ~9 curated mega-cap funds; and the
`dark_positioning_backtest` null tested *direction* while the blend uses *intensity*, so the
wired quantity has never been tested against any baseline.

## BEFORE-STATE (captured live, 2026-07-25, engine `nowtrendin-v2-engine`)

- `/risk/scores?limit=300` → 300 rows, all 300 carrying `dark_positioning_intel`.
- Rows where the blend **actually fires** (`positioning_signal` non-null AND
  `funds_holding` or `congress.members` > 0): **16 of 300.**
- Rows with a scored `Insider Tracking` component at all: **5 of 300** (the rest serve
  `absent: true, score: null` — §17 honest absence working correctly).

### ⚠ The blast radius is an empirical confirmation of the Board's charge

Every one of the 16 affected rows is a household-name mega-cap:

| instrument | positioning_signal | funds_holding | congress members | component score | money_movement | tier |
|---|---|---|---|---|---|---|
| Apple | 1.00 | 6 | 9 | (absent) | 30.4 | ROUTINE |
| Nvidia | 0.95 | 8 | 7 | 24.4 (z −0.70) | 27.4 | ROUTINE |
| Microsoft | 0.90 | 5 | 10 | (absent) | 30.5 | ROUTINE |
| Alphabet | 0.85 | 6 | 5 | (absent) | 30.3 | ROUTINE |
| Amazon | 0.85 | 7 | 5 | (absent) | 30.5 | MODERATE |
| Meta | 0.65 | 4 | 5 | 31.3 (z +0.06) | 31.2 | ROUTINE |
| Tesla | 0.50 | 4 | 2 | (absent) | 37.0 | ROUTINE |
| JPMorgan | 0.30 | 2 | 2 | 29.7 (z −0.04) | 23.2 | ROUTINE |
| IBM | 0.25 | 0 | 5 | (absent) | 30.2 | ROUTINE |
| Chevron | 0.20 | 1 | 2 | (absent) | 24.3 | ROUTINE |
| SpaceX | 0.15 | 0 | 3 | (absent) | 23.3 | ROUTINE |
| Lockheed Martin | 0.10 | 0 | 2 | (absent) | 24.0 | ROUTINE |
| Wells Fargo | 0.10 | 0 | 2 | (absent) | 32.1 | ROUTINE |
| Morgan Stanley | 0.10 | 0 | 2 | (absent) | 23.2 | ROUTINE |
| Ford | 0.05 | 0 | 1 | 27.6 (z −0.30) | 21.8 | ROUTINE |
| Citigroup | 0.05 | 0 | 1 | (absent) | 23.1 | ROUTINE |

**The signal is non-zero for 16 mega-caps and exactly zero for the other 284 instruments in the
universe.** That is the Economist's round-2 claim — *"0.6 of that intensity is a market-cap
indicator, not a flow"* — confirmed on live production data rather than argued. It ranks Apple
(1.00) above Nvidia (0.95) above Microsoft (0.90) in an ordering that tracks index membership and
household-name status, not money movement.

## FALSIFIABLE PREDICTIONS, RECORDED BEFORE THE FLIP

An exact post-flip *value* cannot be predicted from the served payload: the blend operates on the
raw 0–1 `pos_conc` **before** z-scoring, and only the post-z component score is exposed. So the
prediction is stated on what IS determinate. Any failure of these is a red flag requiring rollback:

1. **Exactly 16 rows change.** The 284 rows with `positioning_signal = 0` or no
   funds/members must be **unchanged** — for them the blend term was already `sig*0.4 = 0`
   against a `(1-0.4)` scaling, so removing it changes their input.
   ⚠ NOTE: rows with `sig = 0` are NOT unaffected — `_norm(base*0.6 + 0)` ≠ `_norm(base)`. The
   blend *deflates* every scored row whose `sig` is 0 but which passes the `_has` gate. Only rows
   failing `_has` entirely are untouched. Verify this distinction in the after-state.
2. **`flow` is unchanged on all 300 rows.** `flow` is read from `dark_positioning_intel`, not from
   the blend, and the attach sites are untouched.
3. **Market accuracy ledger Δ = 0.** Enrollment gates on `flow` + `movement_intensity`;
   `detection_score` is a stored witness "never thresholded, never in the verdict"
   (`market_accuracy_ledger.py:220-227`, guarded by `test_market_ledger_witness.py`).
4. **Crypto is entirely unaffected** — `crypto_money_gradient` has zero references to
   `positioning_intel` / `dark_positioning_intel` (grep-verified in round 1).
5. **A ~12-cycle (~3 day) negative-z transient is EXPECTED, not a regression.**
   `market_signal_history` holds 12 cycles of *blended* values, so after the flip `current` drops
   while `baseline_mean` stays elevated → z goes negative until the baseline re-forms. Do **not**
   delete history to "fix" this. Annotated in advance precisely so it is not misdiagnosed.

## VERIFICATION PROCEDURE (after ≥1 scoring cycle, ≤6h)

1. Confirm `/prewarm` `last_run` is fresh — a wedged prewarm serves the old numbers and looks
   like a failed flip.
2. Re-pull `/risk/scores?limit=300`; diff against `r7_before_riskscores.json`.
3. Assert predictions 1–4; record the observed transient for 5.
4. `/monitor` `run_all` clean; `/market/accuracy` counts identical.

## ROLLBACK

`heroku config:unset DARK_POS_WEIGHT -a nowtrendin-v2-engine` — returns to 0.4. The baseline heals
over the same ~12 cycles.
