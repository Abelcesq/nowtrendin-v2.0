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
TRADING_DAYS_PER_YEAR = 252

# Curated mega-caps PLUS whatever the live insider feed surfaces — the latter skews small/mid,
# which is the universe the Board says the real signal lives in.
BASE_TICKERS = ["AAPL", "MSFT", "TSLA", "NVDA", "META", "GOOGL", "AMZN", "JPM",
                "WFC", "C", "MS", "IBM", "F", "CVX", "LMT"]


def universe(max_extra: int = 40) -> list:
    tickers = list(BASE_TICKERS)
    try:
        os.environ.setdefault("INSIDER_PARSER_FIX", "1")   # research read; correct tickers
        import finviz_data
        rows = finviz_data.insider_feed(limit=500) or []
        extra = sorted({(r.get("ticker") or "").upper() for r in rows})
        extra = [t for t in extra if t and t not in tickers][:max_extra]
        tickers += extra
        print(f"  universe: {len(BASE_TICKERS)} curated + {len(extra)} from the live "
              f"insider feed = {len(tickers)}")
    except Exception as e:
        print(f"  universe: insider feed unavailable ({e}); curated only")
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

    # results[mult][horizon] = [n_fired, n_evaluated]
    results = {m: {h: [0, 0] for h in HORIZONS} for m in MULTIPLES}
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
                for h in HORIZONS:
                    end = (datetime.strptime(det, "%Y-%m-%d")
                           + timedelta(days=h)).strftime("%Y-%m-%d")
                    a = arrival_clock.find_arrival(sv, det, med, mult=m, until=end)
                    results[m][h][1] += 1
                    if a.get("arrived"):
                        results[m][h][0] += 1
                        if h == 60 and a.get("lead_days") is not None:
                            lead_days[m].append(a["lead_days"])
        if i < len(tickers) - 1:
            time.sleep(0.35)

    print(f"\n  evaluated {checked} ticker-dates across {len(tickers)} instruments "
          f"({skipped_thin} skipped: baseline too thin, §16a)")
    if not checked:
        print("\nNo evaluable samples — inconclusive, not a result.")
        return 2

    print()
    print("=" * 78)
    print("UNCONDITIONAL ARRIVAL BASE-RATE CURVE  (random dates; NO signal involved)")
    print("=" * 78)
    print(f"  {'mult':>5} | " + " | ".join(f"{h:>3}d window" for h in HORIZONS)
          + " | events/name-yr | median lead(60d)")
    print("  " + "-" * 74)
    for m in MULTIPLES:
        cells = []
        for h in HORIZONS:
            fired, n = results[m][h]
            cells.append(f"{(100.0*fired/n if n else 0):>9.1f}%")
        f60, n60 = results[m][60]
        rate60 = (f60 / n60) if n60 else 0.0
        per_year = rate60 * (TRADING_DAYS_PER_YEAR / 60.0)
        lds = sorted(lead_days[m])
        med_lead = lds[len(lds) // 2] if lds else None
        print(f"  {m:>5} | " + " | ".join(cells)
              + f" | {per_year:>13.2f} | {med_lead if med_lead is not None else '-':>16}")

    print()
    print("  Reference targets the Board offered (they do NOT reconcile — see below):")
    print("    Executioner : placebo arrival ~5-8% per 60d window")
    print("    Challenger  : 2-4 arrival events per name-year")
    print("    2-4 events/yr implies roughly 40-70% chance of >=1 arrival in any 60d window,")
    print("    which is an order of magnitude looser than 5-8%. The Chairman must rule on")
    print("    which target governs BEFORE the threshold is written into the pre-registration.")
    print()
    print("  This tool deliberately does not choose. Picking the multiple after seeing the")
    print("  curve is exactly the specification-shopping the Board guarded against; the")
    print("  TARGET must be fixed first, then the multiple read off the curve.")
    print(f"\n  reproducible with: CALIB_SEED={SEED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
