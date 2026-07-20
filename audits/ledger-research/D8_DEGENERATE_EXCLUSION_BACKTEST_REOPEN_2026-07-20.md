# D8 — Degenerate-Component Score-Side Exclusion: REOPEN Refresh (2026-07-20)

**Reopen trigger:** founder ruling 2026-07-20 ("proceed with 1 and 2") — reopen D8's held-out
backtest for review at current n, alongside the H2b tripwire recalibration. **Reopen ≠ ship.**
This is a review-stage refresh of `D8_DEGENERATE_EXCLUSION_BACKTEST_2026-07-19.md` (the full
analysis; read it first — this note only records what changed in one day and whether the verdict
still holds). Held-out, read-only; no code/score/ledger/enrollment change follows. Sources: live
pulls 2026-07-20 (engine `nowtrendin-v2-engine`): `GET /risk/scores?limit=300` (300/300),
`GET /market/accuracy/detail`, `GET /crypto/accuracy/detail`, `GET /monitor/degenerate-census`.
No SQL, no paid pulls, no sweeps.

---

## 1. The decisive finding is code-level and UNCHANGED

Ledger enrollment remains DECOUPLED from `money_movement`. The equity recorder still gates on
`flow ∈ {inflow, outflow}` + `movement_intensity ≥ 0.25` (filings evidence, baseline-independent);
`detection_score` (= mm) is stored as **context only**, read by no threshold. The enrollment site
was not touched by any 2026-07-20 change (the hardenings were reporting/monitoring only). Therefore
**Δ(enrollments) = 0, Δ(verdicts) = 0 remains exact by mechanism** — the T3 invariant (never wire
enrollment to mm/tier) is intact.

## 2. Ledger cohort — reconfirmed row-by-row at current data

`GET /market/accuracy/detail`, 2026-07-20 — **12 resolved rows, identical set to 07-19** (the
ledger is a rolling working set; no new resolved evidence in one day):

| Metric | 2026-07-19 | 2026-07-20 | Δ |
|---|---|---|---|
| Resolved rows | 12 | 12 | 0 |
| At-detection degenerate-pin (mm == 30.0) | 0/12 | **0/12** | 0 |
| Blended CONFIRMED | 6/12 = 50.0% | 6/12 = 50.0% | 0 |
| Inflow lane | 6/7 | 6/7 | 0 |
| Outflow lane | 0/5 | 0/5 | 0 |
| Crypto resolved | 1/1 (BTC, mm ctx 19.7) | 1/1 | 0 |

Every resolved detection is a covered-lane major whose directional flow came from real positioning
evidence, with a **non-pinned at-detection mm** (33.8–70.0). D8 excludes components; it cannot
create a directional flow or raise intensity → **0 rows would have failed to fire, 0 would newly
fire.** The counterfactual rates are byte-identical.

## 3. D8 population on the SCORE surface (context; breathes cycle-to-cycle)

`/risk/scores` n=300, lanes halted_microcap 283 · covered 15 · macro_theme 2 (unchanged):

| Effect of excluding degenerate/absent MM components | 2026-07-19 | 2026-07-20 |
|---|---|---|
| mm == 30.0 pin cohort (freshness-only survivor) | 189 | **175** |
| mm → None (no MM component measured) | 188 | **174** |
| Directional-flow instruments (the enrollable set) | 8 | **7** |

The ~14-row drift is the documented "snapshot breathing" (threat #5 — Signal Freshness flips
measured/degenerate cycle to cycle); it is not a trend. **The structural disjointness holds:** all
174 mm→None rows are flow-neutral, and flow-neutral instruments are unenrollable by construction —
the rows D8 would move are exactly the rows the ledger never sees.

## 4. Has coverage converted enough for the exclusion to bind on DATA? Not yet.

The reopen's substantive question (the 07-19 verdict said "revisit when positioning coverage grows
so degenerate baselines convert to measured ones"). Current `/monitor/degenerate-census` → `by_lane`:

- **covered lane `unmeasured_fraction` = 0.524** — the recalibrated T2 metric (H2b). It is *just
  above* the 0.5 majority-measured line, so the covered lane is at the cusp but **has not
  converted**. D8's exclusion still binds on ABSENCE, not on data.
- `fully_degenerate_fraction` = 0.0 across every lane — i.e. every instrument carries ≥1 measured
  component; nothing is fully annihilated at the instrument level this cycle. (This is precisely why
  the original T2 metric fired spuriously — see the H2b recalibration.)
- crypto census reads `available:false` (cache cold — unknown, not 0); the 12-coin all-degenerate
  D ring is unchanged from 07-19 by every served pull that HAS resolved.

## 5. Reopen verdict — the 2026-07-19 conclusion STANDS: defer D8

- **No new evidence.** n is unchanged (12 + 1 resolved); the mechanism-level Δ=0 is reconfirmed
  exactly; the population numbers only breathed within their known cycle-sensitivity.
- **Coverage has not crossed the bind-on-data threshold.** Covered-lane unmeasured_fraction 0.524
  ≥ 0.5 — the exclusion would still act on absence, which is exactly what the display-only D7
  quartet already handles without touching a served score.
- **D8 remains a presentation-truth decision, not an accuracy decision** — the same finding as
  07-19. The two live reopen paths are unchanged:
  - **T1 (founder truth-ruling):** if you want served mm/tier to equal the honest-absence display
    on the affected rows, this file + the 07-19 backtest satisfy backtest-before-ship for that
    narrow, ledger-neutral claim. Product decision required for crypto (M-only score, do not
    headline a "Money Gradient" with no money data).
  - **T2 (coverage conversion, now correctly calibrated):** `/monitor/deferred-triggers` will FIRE
    when covered-lane `unmeasured_fraction` falls below 0.5 — the genuine maturation event. It
    currently HOLDS.
- Track the **outflow 0/5** thread separately (S1 — positioning_intel flow logic; still n-small,
  regime-confounded per R1); D8 would not touch it.

*Method note: single-snapshot pulls 2026-07-20 (engine UTC); analysis reproduced the 07-19 method
(narrow MM-component degenerate signature on Insider/Analyst/Freshness; at-detection witness =
stored detection_score). No production data modified; no paid actors ran. This file is the only
artifact.*
