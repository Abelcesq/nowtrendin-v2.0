# Positioning Floor-Pin Omission — Research Report (2026-07-19)

**Read-only research** (founder-ordered, from the 2026-07-07 backtest-gated queue). No code,
score, or ledger change follows from this note without founder sign-off. Sources: project
record (audits + SESSION_LOG), code-level trace of `transfer/market_signal_engine.py` /
`transfer/av_dark_positioning.py` / `transfer/financial_risk_gradient.py`, and a live pull of
`GET /risk/scores` (300/300 instruments) + `GET /crypto` (12 coins) on 2026-07-19 (engine UTC).
No SQL, no paid pulls, no git writes. This file is the only artifact written.

---

## 1. The proposal, as recorded

The item entered the record in three places:

**(a) IMPROVE_SYSTEM_2026-07-05.md (weekly audit #3), Recommendation 2 — the origin:**

> "Open a backtest-gated investigation into the 30.0-floor degeneracy (F2). … Determine whether
> the market/crypto baseline cold-start is defaulting to a uniform floor. Per §17, **omit**
> floor-pinned instruments with no positioning coverage rather than rendering `ROUTINE /
> neutral`. **Requires backtest-before-ship** (touches the market/crypto score surface)."

Supporting findings in the same audit: F2 ("All 12 crypto coins report identical
`money_movement=30.0` + `flow=inflow`; 133/274 risk instruments pinned at exactly 30.0"), F9
("the fix is §17 omission of no-coverage floor-pinned instruments, not a new source"), and the
fiduciary-lens watch ("presentationally they imply differentiation and coverage that isn't
there. Fix by omission (§17), not by inventing a number").

**(b) SCORING_INTEGRITY_ASSESSMENT_2026-07-07.md, item G:**

> "Market Signal open items: positioning floor-pin (no-coverage instruments read 'ROUTINE 30.0'
> as if measured — §17 violation in spirit; backtest-gated fix queued)."

**(c) SESSION_LOG.md 2026-07-07 (lines ~1285, ~1303-1305), the queue itself:**

> "Backtest-gated queue (founder sign-off to start): GHOST_FEEDS expert/niche outlets;
> breadth-at-first-sighting enrollment priority; free-source fast-lane recheck;
> **positioning floor-pin omission**."

`LED_FEATURE_MINING_2026-07-07.md` does not name the item; it is adjacent context only (its
D-is-late-confirmation finding explains WHY positioning data is absent early: market-side Dark
Matter — 13F/insider/congress — structurally arrives after a story is already big).

**Precise statement of the proposal:** market-signal positioning components that sit at a
floor/pinned value because the underlying data is ABSENT (a cold-start / no-coverage artifact,
the SPCX class) should be **omitted from display** (rendered as absent per §17) instead of
being shown — and counted — as if they were measured reads ("ROUTINE 30.0", "neutral").

---

## 2. Mechanism — where the pin comes from (code-traced, read-only)

All in `transfer/market_signal_engine.py`:

1. **The 30.0 value is `z = 0` exactly.** `_z_to_unit(0) = 0.30` → component score 30.0
   (line ~164). `score_component` computes `z = (current − mean) / max(0.05, stdev)`.
   An instrument whose positioning inputs are **always zero** accumulates a baseline of
   `mean = 0, stdev = 0` → the 0.05 stdev floor binds → `z = 0/0.05 = 0` → a confident-looking
   30.0 served with `baseline_relative: true` (the UI renders "✓ scored vs own history").
   **A zero-on-zero baseline is informationless, but it wears the measured badge.**
2. **`MIN_BASELINE_TRUSTWORTHY` (=10) does not catch this.** The SPCX Fix #1 guard flags THIN
   baselines (3–9 cycles) as calibrating. A baseline of ≥10 **constant-zero** samples passes the
   gate — `calibrating: false` — so the pin graduates into a "trustworthy" 30.0. This is the gap
   the 2026-07-05 audit called the 30.0-floor degeneracy. (Verified live: all 12 crypto coins
   serve Proxy Positioning `score 30.0, z 0.0, baseline_relative true, calibrating false`.)
3. **The quarantine flag is ON in production** (`SCORE_QUARANTINE_ENABLED`, `_MKT_QUARANTINE`).
   Verified arithmetically from live payloads: e.g. `corgi_acmr…` serves
   `money_movement = 28.9 = (0.30·analyst + 0.15·freshness)/0.45` — positioning EXCLUDED and
   weights renormalized. With the flag on, `assemble_market_components` returns
   `positioning_concentration = None` when FINRA + WhaleWisdom are both absent and insider
   count is 0; `compute_market_signal` excludes it from the weighted sum; and
   `record_market_cycle` **skips None** (never poisons the baseline with a fabricated 0 —
   the a_k_a_brands fix, 2026-07-15). **So for the dominant class, the SCORE side of the
   proposal is already implemented.** What remains is the DISPLAY side: the excluded component
   is still served in `components` as `score: 0.0` (z null, baseline_relative false) and the
   front-ends render it as a numeric 0 bar.
4. **The residual exactly-30.0 `money_movement` pin** (173 instruments, §3) is now produced by
   z=0 pins on the REMAINING components (analyst_signal + signal_freshness both at 30.0 on
   zero-on-zero baselines), positioning already excluded. Same mechanism, different components.
5. **Crypto** (`crypto_money_gradient` path) has no quarantine and no `data_coverage` field in
   the served coin payload at all — Proxy Positioning is pinned at 30.0 for all 12 coins and
   `money_movement` = 30.0 uniformly, with nothing in the payload for a UI to caveat on.

---

## 3. Live extent (measured 2026-07-19, engine `/risk/scores` 300 rows + `/crypto` 12 coins)

### 3a. How pinned was distinguished from genuinely-low (explicit method)

Three mutually exclusive classes, per instrument, on the served
`market_gradient.components["Insider Tracking (insider + 13F filings)"]`:

- **ABSENT (quarantined):** `score == 0.0` with `z == null`, `baseline_relative == false` —
  the quarantine path (no FINRA, no WhaleWisdom, no insider stage-1). Cross-checked against
  `dark_positioning_intel`: **0 of these rows** have any funds_holding / congress members /
  positioning_signal > 0 — omitting this class can never hide real data.
- **PINNED at the floor:** `score == 30.0` with `z == 0.0` exactly. For continuous real inputs
  an exact z of 0.0 is a measure-zero event — in practice it means a constant (usually all-zero)
  history under the 0.05 stdev floor. Sub-split by independent evidence in
  `dark_positioning_intel` (funds_holding / congress / positioning_signal):
  evidence present → *plausibly genuinely-at-baseline* (constant but data-backed);
  evidence absent → *pure zero-on-zero pin* (nothing was ever measured).
- **MEASURED:** any other score (z ≠ 0, or a non-floor value).

### 3b. Results — /risk/scores (n = 300)

| Class (Insider Tracking component) | Count | % |
|---|---|---|
| ABSENT — served as numeric `0.0` (score-excluded, display-rendered) | **281** | **93.7%** |
| PINNED 30.0, z=0.0 | 8 | 2.7% |
| — of which NO independent positioning evidence (pure pin): `ford`, `drawdown` | 2 | |
| — with some dpi evidence (constant-but-real: `alphabet` funds=6, `jpmorgan` 2, `chevron` 1, `citigroup`, `spacex`, `lockheed_martin`) | 6 | |
| MEASURED (z ≠ 0; e.g. apple 28.2, morgan_stanley 36.6, tesla 29.5) | 9 | 3.0% |
| Structurally N/A (macro_theme: `recession`, `inflation`) — served `score: null, not_applicable: true` | 2 | 0.7% |

Headline reads built on top of this:

- `money_movement == 30.0` **exactly: 173/300 (57.7%)** — every one `halted_microcap` lane +
  `data_coverage: "insufficient"`. (The 2026-07-05 audit's "133 of 274"; the class persists.)
- `data_coverage`: insufficient **282** / partial 10 / full 8. `flow`: neutral **292**/300.
- Top-level `positioning_score` (financial_risk_gradient) pinned at exactly **16.5 on 276/300**;
  `classification` ROUTINE 295/300.
- **`spacex` itself is in the pinned-at-30 cohort** (mm 37.0, z=0.0 on positioning) — the named
  SPCX-class artifact is still live, now wearing `baseline_relative: true` rather than
  CALIBRATING (its zero-baseline aged past the 10-cycle trustworthy gate).

### 3c. Results — /crypto (n = 12)

**All 12 coins** serve `money_movement = 30.0` exactly; Proxy Positioning
`30.0 / z 0.0 / baseline_relative true / calibrating false` on every coin. Market Confirmation
DOES differentiate (22.4–52.6) and `flow` now differentiates (4 inflow / 4 outflow / 4 neutral —
improved since the 07-05 audit), but the D-side number is a uniform floor artifact presented as
a measured baseline-relative read, and the coin payload has **no `data_coverage` field** for any
UI to caveat on.

### 3d. Current display state, surface by surface

| Surface | Insufficient-coverage caveat | Absent positioning row | Pinned 30.0 row |
|---|---|---|---|
| Web MarketSignal list | ✔ "LTD DATA" chip replaces tier; scores dimmed | n/a (list) | n/a (list) |
| Web MarketSignal detail | ✔ amber "Insufficient positioning data" banner; rings dimmed | ✘ rendered as numeric **0** bar | ✘ rendered as **30 ✓** ("scored vs own history") |
| Web Grade | ✔ LIMITED DATA | — | — |
| Web Crypto detail | ✘ impossible — payload lacks `data_coverage` | — | ✘ rendered as **30 ✓** |
| Mobile risk/[key] | ✘ **no `data_coverage` handling at all** — full-opacity rings, ROUTINE tier chip | ✘ numeric **0** bar | ✘ **30 ✓ base** |

Only the lane-driven macro-theme N/A (`score: null`) renders "n/a" everywhere — that path is the
exemplar of what §17 asks for.

---

## 4. Assessment against §17 and the SPCX precedent

§17 (CLAUDE.md): *"a topic's detail view shows ONLY the sources, coverage, and components that
actually CONTRIBUTE … a data source that returns no data … is OMITTED, never rendered as empty …
Component breakdowns render a real value or an explicit 'n/a' — NEVER NaN."*

- The **281 ABSENT rows literally render a component that does not contribute** (quarantine
  excludes it from the weighted sum) **as a numeric 0.0 bar** on all three platforms. This is
  the exact §17 violation class ("rendered as empty/0"), one notch subtler than the removed
  NaN panel: the number is real-looking but describes nothing.
- The **pinned 30.0 class is worse in spirit**: it renders a zero-on-zero-baseline artifact as
  a *measured, baseline-relative* value, with a ✓ that asserts "scored vs own history." The
  2026-07-05 fiduciary lens named it precisely: it implies an assessment we did not make.
- **SPCX precedent** (`market_signal_diagnostic.py`, Fix #1): a cold-start must read
  CALIBRATING/"baseline forming", "never a confident ROUTINE the data can't support." The
  trustworthy-baseline gate implemented that for THIN baselines but not for **degenerate
  (constant-zero) baselines** — which is how spacex and all 12 coins graduated back into
  confident floor reads. The floor-pin omission item is the §17-display completion of the same
  principle.
- The engine already contains the design answer twice over: the macro-theme `not_applicable`
  serialization (`score: null` → UI "n/a") and the quarantine's score-side exclusion. The
  proposal is to make the served/display truth match the scoring truth.

---

## 5. Recommendation

**Recommended: OMIT (§17 display-absence) for the absent class, ANNOTATE-then-gate for the
pinned class.** Concretely, in priority order:

1. **Absent positioning → serve as absent (DISPLAY-ONLY; no backtest needed).** When the
   quarantine path excludes `positioning_concentration`, serialize the component as
   `score: null, absent: true` (mirroring `not_applicable`) instead of `score: 0.0`; UIs then
   render explicit "n/a — no positioning data for this instrument" or omit the row, exactly as
   macro themes already do. The weighted score is untouched (already renormalized without it);
   `record_market_cycle` already skips None. Zero risk of hiding real data (0/281 rows had any
   dpi evidence). This is the same shippable class as the removed NaN panel (§17, 2026-06-25).
2. **Degenerate-baseline guard for the z=0 pin (classification display-only; any score use
   BACKTEST-GATED).** Detect `mean == 0 and raw_stdev == 0` (or an all-constant history) in
   `score_component` and stamp the component `degenerate_baseline: true`. Display-side: render
   it as absent/"no data yet" and drop the ✓ — this converts spacex, ford, drawdown and all 12
   crypto Proxy Positioning rows from "measured 30 ✓" to honest absence. Score-side EXCLUSION
   of such components (extending quarantine semantics to the z=0-on-zero case, which would move
   the 173 uniform `money_movement=30.0` reads) **is score-affecting and stays backtest-gated**
   per the original queue — it changes served detection numbers on 57.7% of the risk universe.
3. **Crypto: add `data_coverage`/absence fields to the coin payload (DISPLAY-ONLY).** The coin
   payload currently gives a UI nothing to caveat on; all 12 coins present a uniform 30.0 as
   measured. Same serialization as (1). The uniform-crypto-inflow concern from 07-05 has since
   resolved (flows differentiate); the uniform D=30.0 has not.
4. **Mobile parity (DISPLAY-ONLY, §12/§17):** mobile `risk/[key]` consumes no `data_coverage`
   at all — no LTD-DATA equivalent, full-strength ROUTINE chip and rings on insufficient-
   coverage instruments. Bring it to the web's banner/dim/LTD-DATA behavior (Frontend
   Consistency agent scope).
5. **Do not "leave as is."** It fails §17 verbatim on 281 of 300 instruments and presents
   floor artifacts as measured reads on the remainder — the presentation-integrity issue the
   attorney lens flagged on 2026-07-05.

### Option classification (display-only vs score-affecting)

| Option | Score impact | Gate |
|---|---|---|
| (1) Serve absent positioning as `null/absent`, UI renders n/a or omits | **None** (score already excludes it) | Ship after normal verify; no backtest |
| (2a) `degenerate_baseline` stamp + display absence for z=0 pins | **None** (annotation only) | Ship after verify |
| (2b) EXCLUDE degenerate-baseline components from the weighted score | **Yes** — moves mm on ~173 risk rows + all crypto D | **Backtest-before-ship** + founder sign-off (the original queue item's gate) |
| (3) Crypto payload coverage fields | None | Ship after verify |
| (4) Mobile data_coverage parity | None | Ship after verify (frontend-consistency) |
| Annotate-only (keep numeric 0/30 + chip) | None | Not recommended — §17 forbids rendering the non-contributing value at all |
| Leave as is | — | Fails §17 |

**Net:** the item as queued conflated one score-affecting change (2b) with four display-only
changes that need no backtest. Recommend un-bundling: ship (1)+(2a)+(3)+(4) as the §17
compliance fix, and hold (2b) behind the held-out backtest exactly as the 2026-07-05 audit
required.

---

*Method note: live counts from a single `GET /risk/scores?limit=300` snapshot (scored_at range
2026-07-04 → 2026-07-19; 173-row mm=30.0 cohort all fresh) + `GET /crypto` (prewarm cache).
Raw pull + per-row stats retained in the session scratchpad (`risk_scores_full.json`,
`risk_positioning_stats.csv`), not committed. No production data was modified.*
