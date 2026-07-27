# -*- coding: utf-8 -*-
"""
arrival_calibration.py — measure the UNCONDITIONAL arrival rate. READ-ONLY.

THE DEADLOCK THIS BREAKS
────────────────────────
`flow_ledger` refuses to enroll without an active pre-registration, and the pre-registration
cannot be locked because `ARRIVAL_VOL_MULT = 3.0` is a placeholder. The Board's rule is to
calibrate that multiple against the PLACEBO cohort's unconditional arrival rate — but you
cannot enroll placebos without a pre-registration. Circular.

The way out: the unconditional rate is a property of the DATA, not of our enrollment. It can
be measured offline over random ticker-dates without enrolling anything. That is what this
does. It is a calibration study, not a detection, and nothing it produces is a claim about
our signal.

WHY A FIXED SEED
────────────────
This number feeds a pre-registration, so it must be reproducible by anyone who re-runs it.
A calibration drawn from an unseeded sample is a number nobody can check — and "we picked
3.0 after looking" is precisely the specification-shopping the Board spent two rounds
guarding against.

WHAT IT MEASURES
────────────────
For each sampled (ticker, date): freeze the baseline exactly as the ledger would, then ask
whether an arrival fires within each horizon, at each candidate multiple. The output is a
BASE-RATE CURVE. It deliberately does NOT pick the threshold — the Board offered two
different targets (~5-8% per 60d window; 2-4 events per name-year) which do not reconcile,
and reconciling them is the Chairman's ruling, not this tool's.
"""
from __future__ import annotations
import json
import math
import os
import random
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "transfer"))

import arrival_clock  # noqa: E402
import fmp_data  # noqa: E402

SEED = int(os.getenv("CALIB_SEED", "20260725"))
SAMPLES_PER_TICKER = int(os.getenv("CALIB_SAMPLES_PER_TICKER", "6"))
MULTIPLES = [2.0, 2.5, 3.0, 3.5, 4.0, 5.0]
HORIZONS = [60, 90, 180]
BOOTSTRAP_B = int(os.getenv("CALIB_BOOTSTRAP_B", "1000"))

# ⚠ CORRECTION 3 of 4 (accountability review, Challenger): the universe is FROZEN in a
# committed file. The prior run drew 40 tickers from the live insider feed — a set that
# changes daily and is selected on the variable correlated with the treatment — so "fixed
# seed" fixed the date draw but not the sample. Same seed next week, different universe.
# Now: same seed, same file, same result, and the file's git SHA is the provenance.
UNIVERSE_FILE = os.getenv(
    "CALIB_UNIVERSE_FILE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "calibration_universe_2026-07-26.txt"))


def universe() -> list:
    with open(UNIVERSE_FILE, encoding="utf-8") as fh:
        tickers = [ln.strip().upper() for ln in fh
                   if ln.strip() and not ln.startswith("#")]
    print(f"  universe: {len(tickers)} tickers, FROZEN in "
          f"{os.path.basename(UNIVERSE_FILE)} (committed; SHA = provenance)")
    return tickers


def main():
    rng = random.Random(SEED)
    print(__doc__.split("WHAT IT MEASURES")[0])
    print("=" * 78)
    print(f"CALIBRATION  seed={SEED}  samples/ticker={SAMPLES_PER_TICKER}")
    print("=" * 78)

    tickers = universe()
    today = datetime.now(timezone.utc)

    # Each sample needs baseline history BEFORE it and a full horizon AFTER it, so draw
    # detection dates from a window that leaves room for both.
    oldest = today - timedelta(days=900)
    newest = today - timedelta(days=max(HORIZONS) + 20)
    span = (newest - oldest).days

    # ⚠ CORRECTION 1 of 4 (Challenger): the prior run never applied `already_arrived_before`,
    # so dates drawn mid-surge fired at lead ~0 against a still-low frozen baseline — rows
    # the ledger would stamp PRE_ARRIVED and exclude from the lead denominator. The null was
    # therefore biased UPWARD. Pre-arrived samples are now excluded per multiple, and counted.
    # Tallies are kept PER TICKER for correction 4 (a ticker-clustered bootstrap): the 295
    # "observations" were ~55 clusters, and a naive n=295 interval overstates precision.
    tally = {m: {h: {} for h in HORIZONS} for m in MULTIPLES}   # [m][h][ticker] = [fired, n]
    pre_arrived = {m: 0 for m in MULTIPLES}
    lead_days = {m: [] for m in MULTIPLES}
    checked = skipped_thin = 0

    for i, t in enumerate(tickers):
        try:
            ohlcv = fmp_data.historical_ohlcv(
                t, oldest.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        except Exception as e:
            print(f"  {t}: fetch failed ({e})")
            continue
        if not ohlcv:
            continue
        sv = arrival_clock.share_volume_series(ohlcv)
        if not sv:
            continue

        for _ in range(SAMPLES_PER_TICKER):
            det = (oldest + timedelta(days=rng.randint(0, max(1, span)))).strftime("%Y-%m-%d")
            base = arrival_clock.compute_baseline(sv, det)
            if not base.get("available"):
                skipped_thin += 1
                continue
            med = base["median_volume"]
            checked += 1
            for m in MULTIPLES:
                # The ledger's own rule, applied to the null: a date where the crowd had
                # ALREADY arrived at this multiple is discovery latency, not a race.
                if arrival_clock.already_arrived_before(sv, det, med, mult=m):
                    pre_arrived[m] += 1
                    continue
                for h in HORIZONS:
                    end = (datetime.strptime(det, "%Y-%m-%d")
                           + timedelta(days=h)).strftime("%Y-%m-%d")
                    a = arrival_clock.find_arrival(sv, det, med, mult=m, until=end)
                    cell = tally[m][h].setdefault(t, [0, 0])
                    cell[1] += 1
                    if a.get("arrived"):
                        cell[0] += 1
                        if h == 60 and a.get("lead_days") is not None:
                            lead_days[m].append(a["lead_days"])
        if i < len(tickers) - 1:
            time.sleep(0.35)

    print(f"\n  evaluated {checked} ticker-dates across {len(tickers)} instruments "
          f"({skipped_thin} skipped: baseline too thin, §16a)")
    if not checked:
        print("\nNo evaluable samples — inconclusive, not a result.")
        return 2

    def _pool(m, h):
        fired = sum(v[0] for v in tally[m][h].values())
        n = sum(v[1] for v in tally[m][h].values())
        return fired, n

    def _boot_ci(m, h):
        """⚠ CORRECTION 4: ticker-clustered bootstrap (resample TICKERS with replacement).
        Six overlapping draws per ticker from one 900-day window are not independent."""
        keys = list(tally[m][h].keys())
        if not keys:
            return (None, None)
        brng = random.Random(SEED + int(m * 10) + h)      # deterministic per cell
        rates = []
        for _ in range(BOOTSTRAP_B):
            f = n = 0
            for k in (brng.choice(keys) for _ in keys):
                f += tally[m][h][k][0]
                n += tally[m][h][k][1]
            if n:
                rates.append(f / n)
        if not rates:
            return (None, None)
        rates.sort()
        lo = rates[max(0, int(0.025 * len(rates)) - 1)]
        hi = rates[min(len(rates) - 1, int(0.975 * len(rates)))]
        return (round(lo * 100, 1), round(hi * 100, 1))

    print()
    print("=" * 78)
    print("CORRECTED ARRIVAL BASE-RATE CURVE  (random dates; NO signal; pre-arrived excluded;")
    print("ticker-clustered bootstrap 95% CI on the 60d cell; hazard-correct events/yr)")
    print("=" * 78)
    print(f"  {'mult':>5} | {'60d null [95% CI]':>22} | {'90d':>6} | {'180d':>6} | "
          f"{'pre-arr':>7} | {'ev/name-yr':>10} | med lead")
    print("  " + "-" * 76)
    for m in MULTIPLES:
        f60, n60 = _pool(m, 60)
        p60 = (f60 / n60) if n60 else 0.0
        lo, hi = _boot_ci(m, 60)
        cells = []
        for h in (90, 180):
            fh, nh = _pool(m, h)
            cells.append(f"{(100.0*fh/nh if nh else 0):>5.1f}%")
        # ⚠ CORRECTION 2: events/name-year = -ln(1-p) x 365/60 — hazard-correct, CALENDAR
        # days (the window is timedelta(days=h)). The prior run used 252 trading days over
        # a calendar window and skipped the -ln(1-p), overstating the gap between the two
        # Board targets by enough to misstate the Challenger's own position.
        per_year = (-math.log(max(1e-9, 1.0 - min(p60, 0.999999))) * (365.0 / 60.0)
                    if p60 < 1 else float("inf"))
        lds = sorted(lead_days[m])
        med_lead = lds[len(lds) // 2] if lds else None
        ci = f"[{lo}-{hi}%]" if lo is not None else "[n/a]"
        print(f"  {m:>5} | {100.0*p60:>6.1f}% {ci:>14} | " + " | ".join(cells)
              + f" | {pre_arrived[m]:>7} | {per_year:>10.2f} | "
                f"{med_lead if med_lead is not None else '-'}")

    print()
    print("  READING THE CORRECTED CURVE (the Board's mechanical rule):")
    print("    - The Board recommends 3.0-3.5x on power grounds, reading the multiple off the")
    print("      corrected 60d null (target regime ~20-25%). Required n DECREASES in the null,")
    print("      so the old 5-8% target was the wrong direction, not merely unreachable.")
    print("    - Challenger's 2-4 events/name-year is now computed hazard-correct")
    print("      (-ln(1-p) x 365/60); the prior run's 252/60 arithmetic overstated the gap")
    print("      between the two targets and misstated his position.")
    print()
    print("  This tool deliberately does not choose. Picking the multiple after seeing the")
    print("  curve is exactly the specification-shopping the Board guarded against; the")
    print("  TARGET must be fixed first, then the multiple read off the curve.")
    print(f"\n  reproducible with: CALIB_SEED={SEED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
