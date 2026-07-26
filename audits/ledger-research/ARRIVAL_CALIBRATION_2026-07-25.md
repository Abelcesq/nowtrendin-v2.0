# ARRIVAL THRESHOLD CALIBRATION — result
**Date:** 2026-07-25 · **Tool:** `tools/arrival_calibration.py` (read-only, fixed seed `20260725`)
**Purpose:** measure the UNCONDITIONAL arrival rate so the pre-registration threshold can be
set on evidence rather than taste. **Status:** RESULT — Chairman's ruling required before the
pre-registration can be locked.

---

## 1. Why this had to exist

`flow_ledger` refuses enrollment without an active pre-registration; the pre-registration
could not be locked because `ARRIVAL_VOL_MULT = 3.0` was a placeholder the Board said to
calibrate against the placebo cohort's unconditional rate — which requires enrolling
placebos, which requires a pre-registration. Circular.

Resolved by measuring the unconditional rate **offline**: it is a property of the DATA, not
of our enrollment. Random ticker-dates, baseline frozen exactly as the ledger would freeze
it, no signal involved anywhere.

**Sample:** 295 evaluable ticker-dates across 55 instruments (15 curated mega-caps + 40 drawn
from the live insider feed, which skews small/mid — the universe the Board says the real
signal lives in). 29 samples skipped for insufficient baseline history (§16a working as
designed). Fixed seed, so anyone can reproduce the number.

## 2. THE BASE-RATE CURVE

Share-volume arrival vs the instrument's own frozen baseline. **No signal is involved — these
are random dates.** Any of these firings is noise by construction.

| multiple | 60d window | 90d window | 180d window | events/name-yr | median lead (60d) |
|---|---|---|---|---|---|
| 2.0× | **55.3%** | 63.7% | 80.0% | 2.32 | 14 |
| 2.5× | **30.8%** | 40.7% | 60.3% | 1.30 | 11 |
| **3.0× (current placeholder)** | **24.1%** | 29.8% | 46.1% | 1.01 | 11 |
| 3.5× | **20.7%** | 25.1% | 34.9% | 0.87 | 11 |
| 4.0× | **16.6%** | 21.4% | 29.5% | 0.70 | 9 |
| 5.0× | **14.9%** | 17.6% | 20.7% | 0.63 | 12 |

## 3. THREE FINDINGS, IN ORDER OF CONSEQUENCE

### 3a. The placeholder 3.0× has a 24% unconditional base rate

**Roughly one in four random ticker-dates "arrives" within 60 days with no signal at all.**
That is not fatal — what the ledger publishes is the SEPARATION between treated and control,
not the absolute rate — but it sets the bar: the treated arm must clear ~24% by a margin wide
enough for two Greenwood bands to be disjoint. A high null costs statistical power, and power
costs calendar time, which is the one resource the Executioner keeps pointing at.

### 3b. The Executioner's target is UNREACHABLE at any multiple tested

He specified tuning K until placebo arrival is ~5-8% per 60d window. At **5.0×** the rate is
still **14.9%** — roughly double the top of that range, and the curve is flattening (2.0→3.0
drops 31 points; 4.0→5.0 drops only 1.7). Reaching 5-8% would need a multiple far above 5.0×,
at which point "arrival" stops meaning *the crowd showed up* and starts meaning *a once-in-
years volume event*.

### 3c. The two Board targets are incompatible, and neither was derived from data

- **Executioner:** ~5-8% per 60d window → needs >5.0×
- **Challenger:** 2-4 arrival events per name-year → only **2.0×** reaches it (2.32/yr), and
  2.0× has a **55.3%** 60-day base rate, i.e. a coin flip

They differ by more than an order of magnitude. Both were offered in good faith as
reasonable-sounding defaults, and **neither was measured** — which is precisely why this study
had to run before the threshold was written down rather than after.

## 4. WHAT THIS TOOL DELIBERATELY DOES NOT DO

**It does not pick the multiple.** Reading the curve and then choosing the number that looks
best is specification-shopping with an evidence-shaped alibi. The correct order is: the
Chairman fixes the TARGET, then the multiple is read off the curve mechanically, then the
pre-registration is locked, and only then does enrollment begin.

## 5. RULING REQUIRED — the target, not the multiple

The question is what an "arrival" should mean:

| Option | Target | → multiple | Consequence |
|---|---|---|---|
| **A. Strict** | ~15% per 60d | ~5.0× | Arrival = a rare, unambiguous participation event. Highest signal-to-noise, but few events → slow accrual, and possibly too rare to accumulate n |
| **B. Balanced** | ~20-25% per 60d | 3.0–3.5× | Keeps the current placeholder's regime. Adequate event flow; needs a clearly separated treated arm |
| **C. Loose** | 2-4 events/yr | 2.0× | Matches the Challenger's event-count target, but a 55% null means arrival is nearly ubiquitous and can barely discriminate. **Not recommended** |

**My reading:** option **A or B**, and the choice turns on whether we want fewer, cleaner
events or more, noisier ones. C should be rejected on the evidence — a coin-flip null cannot
support a lead claim.

Two design dimensions were held fixed here and could be revisited instead of the multiple:
the **persistence rule** (currently the crossing day + 1 of the next 4) and the **60-session
baseline**. Tightening persistence would lower the base rate without pushing the multiple to
an implausible level. That is a separate study, not a post-hoc adjustment.

## 6. INCIDENTAL FINDING

Median lead sits at **9-14 days across every multiple**. Arrivals cluster early in the
window rather than spreading across it — which suggests a 60-day horizon captures most of
what a 180-day horizon would, and that the horizon may be a cheaper lever than the multiple.
Worth a look before the horizon is fixed in the pre-registration too.

---

**Chairman — ruling requested:** fix the TARGET (A, B, or C), and confirm whether the
persistence rule and horizon are in scope for calibration or frozen as-is. The multiple then
follows mechanically, the pre-registration locks, and enrollment starts.

*Reproduce: `CALIB_SEED=20260725 python tools/arrival_calibration.py`*
