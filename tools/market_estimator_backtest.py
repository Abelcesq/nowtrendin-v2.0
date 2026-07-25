# -*- coding: utf-8 -*-
"""
market_estimator_backtest.py — O8 backtest (Board round 4, Chairman-ordered 2026-07-25)
========================================================================================
Tests whether the MARKET-side estimator defects the Economist identified actually BIND on
live data, before any score-affecting change ships. Follows the discipline established by
tools/estimator_backtest.py (D1, 2026-07-19): candidates and gates registered BEFORE the
run, READ-ONLY, endpoints only, zero writes, zero engine surface.

THE THREE CLAIMS UNDER TEST (verified in code first, per §10a)
--------------------------------------------------------------
Verified by reading transfer/market_signal_engine.py:
  A. NO ROBUST SCALE. `get_market_baselines` uses statistics.mean / statistics.stdev over
     `lookback` cycles; `score_component` floors stdev at 0.05. Grep confirms zero uses of
     MAD anywhere in transfer/. CONFIRMED IN CODE.
  B. TAIL DELETION. `_z_to_unit` returns min(1.0, 0.30 + z*0.22) for z>0, so it saturates
     at z = 0.70/0.22 = 3.18: z=3.2 and z=32 produce the IDENTICAL served score.
     CONFIRMED IN CODE (arithmetic, not opinion).
  C. SELF-BLINDING. `baseline_cycles = cycles[1:lookback+1]` excludes the CURRENT cycle
     (good) but a spike enters the baseline for the NEXT ~lookback cycles, inflating stdev
     and suppressing subsequent readings — the wrong direction under volatility clustering.
     CONFIRMED IN CODE as a mechanism.

But a mechanism that is real in code may still be IMMATERIAL in production. That is the
question this backtest exists to answer, and it is the one that decides whether a
score-affecting change is justified at all.

PRE-REGISTERED GATES (registered before the first run; do not add or edit post-hoc)
-----------------------------------------------------------------------------------
  G1 SATURATION BINDS?   share of live scored components with |z| >= 3.18 (the point where
                         the served score stops responding to the data).
                         MATERIAL if >= 2.0% of scored components.
  G2 FLOOR BINDS?        share of components whose stdev sits at the 0.05 floor, i.e. the z
                         denominator is fabricated rather than measured.
                         MATERIAL if >= 15% of components.
  G3 TAIL SHAPE.         is the live z distribution actually heavier-tailed than Gaussian?
                         Compare observed P(|z|>=3) against the Gaussian 0.27%.
                         MATERIAL if observed >= 3x Gaussian expectation.
  G4 HEADROOM LOST.      among saturated components, how much information is discarded —
                         report max |z| observed. Contextual (no pass/fail), because a
                         single extreme instrument is itself the finding.

DECISION RULE (registered): ship the estimator change ONLY if G1 or G2 is MATERIAL. If
neither binds, the critique is theoretically correct but practically inert, and a
score-affecting change to every instrument is NOT justified on this evidence. A null
result here is a real result and gets published as one.

SCOPE LIMITATION (stated, not hidden): this reads the SERVED diagnostic surface, which
exposes per-component z, floor_binding and history depth — not the raw per-cycle baseline
series. So it measures whether the defects BIND; it cannot replay a counterfactual
median/MAD score per instrument. That replay needs an engine-side harness with DB access
and is out of scope for an endpoints-only tool on this box (pg:psql is broken here).
"""
from __future__ import annotations
import json
import sys
import time
import urllib.request

ENGINE = "https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com"

# The 16 curated instruments (financial_risk_gradient.WATCHLIST_TICKERS).
TICKERS = ["AAPL", "MSFT", "TSLA", "NVDA", "META", "GOOGL", "AMZN", "JPM",
           "WFC", "C", "MS", "IBM", "F", "CVX", "LMT", "SPCX"]

SATURATION_Z = 3.18          # 0.70 / 0.22 — where _z_to_unit stops responding
GAUSSIAN_P_ABS_Z_GE_3 = 0.0027
# The component R7 (DARK_POS_WEIGHT=0) perturbed. Its baseline needs ~12 cycles to re-form,
# so readings here are transient by construction and must not be allowed to satisfy a gate.
R7_TRANSIENT_COMPONENT = "positioning_concentration"

G1_MATERIAL_PCT = 2.0
G2_MATERIAL_PCT = 15.0
G3_MATERIAL_RATIO = 3.0


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "NowTrendIn-backtest/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def collect():
    rows = []
    for i, t in enumerate(TICKERS):
        try:
            d = get(f"{ENGINE}/diagnostic/market/{t}")
        except Exception as e:
            print(f"  {t}: fetch failed ({e})")
            continue
        if not d.get("available"):
            print(f"  {t}: unavailable ({d.get('reason') or d.get('error')})")
            continue
        for c in d.get("components") or []:
            rows.append({"ticker": t, "component": c.get("name"), "z": c.get("z"),
                         "n_history": c.get("n_history"),
                         "floor_binding": bool(c.get("floor_binding")),
                         "status": c.get("status")})
        print(f"  {t}: {len(d.get('components') or [])} components, "
              f"verdict={d.get('verdict')}, floor_binding={d.get('floor_binding')}")
        if i < len(TICKERS) - 1:
            time.sleep(1.0)          # be polite to the serve path
    return rows


def main():
    print(__doc__.split("PRE-REGISTERED GATES")[0])
    print("=" * 78)
    print("COLLECTING (read-only, endpoints only)")
    print("=" * 78)
    rows = collect()
    if not rows:
        print("\nNo data collected — cannot evaluate gates. This is an inconclusive run, "
              "NOT a null result.")
        return 2

    scored = [r for r in rows if isinstance(r.get("z"), (int, float))]
    n = len(scored)
    zs = [abs(float(r["z"])) for r in scored]
    saturated = [r for r in scored if abs(float(r["z"])) >= SATURATION_Z]
    floored = [r for r in rows if r.get("floor_binding")]
    ge3 = [z for z in zs if z >= 3.0]

    g1_pct = 100.0 * len(saturated) / n if n else 0.0
    g2_pct = 100.0 * len(floored) / len(rows) if rows else 0.0
    obs_p3 = (len(ge3) / n) if n else 0.0
    g3_ratio = (obs_p3 / GAUSSIAN_P_ABS_Z_GE_3) if n else 0.0
    max_z = max(zs) if zs else 0.0

    # ── CONFOUND GUARD (added after the first run, and the first run is why) ────────────
    # R7 set DARK_POS_WEIGHT=0 hours before this backtest first ran. The R7 evidence doc
    # PREDICTED that `current` would drop while baseline_mean stayed elevated for ~12
    # cycles, driving z sharply NEGATIVE on positioning_concentration. On the first run,
    # 3 of the 4 saturated components were exactly that — so the headline G1 number was
    # measuring our own change, not a standing defect. Any gate that can be satisfied by a
    # transient we caused must be reported both ways, permanently.
    clean = [r for r in scored if r.get("component") != R7_TRANSIENT_COMPONENT]
    sat_clean = [r for r in clean if abs(float(r["z"])) >= SATURATION_Z]
    g1_pct_clean = 100.0 * len(sat_clean) / n if n else 0.0
    floored_clean = [r for r in floored if r.get("component") != R7_TRANSIENT_COMPONENT]
    denom_clean = len([r for r in rows if r.get("component") != R7_TRANSIENT_COMPONENT])
    g2_pct_clean = 100.0 * len(floored_clean) / denom_clean if denom_clean else 0.0

    # Gates are evaluated on the CONFOUND-EXCLUDED figures. The all-in numbers are still
    # printed, but a gate may not pass on a transient.
    g1 = g1_pct_clean >= G1_MATERIAL_PCT
    g2 = g2_pct_clean >= G2_MATERIAL_PCT
    g3 = g3_ratio >= G3_MATERIAL_RATIO

    print()
    print("=" * 78)
    print("GATE TABLE  (thresholds registered before this run)")
    print("=" * 78)
    print(f"  components observed        : {len(rows)}  ({n} with a numeric z)")
    print(f"  [confound guard] excluding '{R7_TRANSIENT_COMPONENT}' — perturbed by R7, "
          f"baseline re-forms over ~12 cycles")
    print(f"  G1 saturation |z|>={SATURATION_Z}     : all-in {g1_pct:.2f}%  |  "
          f"CONFOUND-EXCLUDED {g1_pct_clean:.2f}%"
          f"   material>={G1_MATERIAL_PCT}%   -> {'MATERIAL' if g1 else 'NOT material'}")
    print(f"  G2 stdev at 0.05 floor     : all-in {g2_pct:.2f}%  |  "
          f"CONFOUND-EXCLUDED {g2_pct_clean:.2f}%"
          f"   material>={G2_MATERIAL_PCT}%  -> {'MATERIAL' if g2 else 'NOT material'}")
    print(f"  G3 tail vs Gaussian        : P(|z|>=3) observed {obs_p3*100:.2f}% vs "
          f"Gaussian 0.27% = {g3_ratio:.1f}x   material>={G3_MATERIAL_RATIO}x "
          f"-> {'MATERIAL' if g3 else 'not material'}")
    print(f"  G4 max |z| observed        : {max_z:.2f}"
          + (f"  (headroom above saturation: {max_z - SATURATION_Z:.2f}z discarded)"
             if max_z > SATURATION_Z else "  (below saturation — no headroom lost)"))

    if saturated:
        print("\n  saturated components (served score is pinned, data ignored above z=3.18):")
        for r in sorted(saturated, key=lambda r: -abs(r["z"]))[:12]:
            print(f"    {r['ticker']:6} {str(r['component'])[:34]:34} z={r['z']}")
    if floored:
        print(f"\n  floor-bound components (z denominator fabricated, not measured): "
              f"{len(floored)}")
        for r in floored[:8]:
            print(f"    {r['ticker']:6} {str(r['component'])[:34]:34} "
                  f"n_history={r['n_history']}")

    ship = g1 or g2
    print()
    print("=" * 78)
    print("DECISION (rule registered before the run: ship only if G1 or G2 is MATERIAL)")
    print("=" * 78)
    if ship:
        print("  -> DEFECT BINDS IN PRODUCTION. A score-affecting estimator change is")
        print("     justified on this evidence. Proceed to Chairman sign-off, then a")
        print("     staged rollout with before/after capture (the R7 pattern).")
        print()
        print(f"     WHICH defect binds decides WHICH fix is justified:")
        print(f"       G1 saturation  {'BINDS' if g1 else 'does NOT bind'} -> "
              f"{'removing the z cap is supported' if g1 else 'removing the z cap is NOT supported by this evidence'}")
        print(f"       G2 scale floor {'BINDS' if g2 else 'does NOT bind'} -> "
              f"{'a ROBUST SCALE ESTIMATOR (median/MAD) is the supported fix' if g2 else 'no scale change supported'}")
    else:
        print("  -> DEFECT DOES NOT BIND on the current universe. The Economist's critique")
        print("     is correct in code (the saturation and the missing robust scale are")
        print("     real) but IMMATERIAL at today's data. Shipping a change to every")
        print("     instrument's score is NOT justified on this evidence.")
        print("     PUBLISH THE NULL and re-run this gate when the universe expands —")
        print("     Phase 2 market-wide enrollment is exactly when it may start to bind.")
    print()
    print("  NOTE (scope): measures whether the defects BIND. It does not replay a")
    print("  counterfactual median/MAD score — that needs engine-side DB access.")
    return 0 if not ship else 1


if __name__ == "__main__":
    sys.exit(main())
