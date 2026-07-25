"""
SHARED SURVIVAL + INTERVAL MATH for every NowTrendIn accuracy ledger — HELD-OUT.

Board round 2 (2026-07-25, unanimous): the existing Kaplan-Meier estimator
(`accuracy_ledger_enhanced.survival_confirmation`) computes a point estimate with
**no variance estimator and no confidence interval**. Two archetypes flagged this
independently; the Economist's ruling, from Bernstein's *Against the Gods*:

    "A KM curve without an interval is not evidence."

So this module is the ONE place survival + interval math lives, parameterized by
(time, event) observations rather than by table names, so all three existing ledgers
(attention / market / crypto) and the new flow ledger can share it without a fourth
copy-paste of the estimator.

WHAT IT ADDS over the previous implementation:
  • Greenwood's variance for the KM curve.
  • Log-log-transformed confidence bands (bounds stay inside [0,1] — the plain linear
    band goes negative at small n, which is exactly our regime).
  • Number-at-risk at every reported horizon, so a reader can see the denominator
    thinning rather than trusting a lone percentage.
  • Wilson score intervals for binomial rates (never publish a naked point estimate).

MEASUREMENT ONLY. Imported by ledgers and reports; NEVER by scoring. Pure functions,
no DB, no network — so it is trivially testable and reproducible (run this file directly
for the self-test).
"""
from __future__ import annotations

import math
from typing import Iterable, Optional, Sequence

# Two-sided normal quantiles for the intervals we actually publish.
_Z = {0.10: 1.6448536269514722, 0.05: 1.959963984540054, 0.01: 2.5758293035489004}


def _z_for(alpha: float) -> float:
    """Normal quantile for a two-sided (1-alpha) interval; falls back to the nearest
    supported alpha rather than silently using the wrong critical value."""
    if alpha in _Z:
        return _Z[alpha]
    return _Z[min(_Z, key=lambda a: abs(a - alpha))]


def wilson_interval(successes: int, n: int, alpha: float = 0.05) -> dict:
    """Wilson score interval for a binomial rate.

    Preferred over the normal approximation because our episode counts are small and
    rates sit near 0 — precisely where the Wald interval produces impossible bounds
    (negative lower limits, or a zero-width interval when successes == 0).
    """
    if n <= 0:
        return {"rate_pct": None, "lo_pct": None, "hi_pct": None, "n": 0,
                "successes": 0, "method": "wilson", "note": "no observations"}
    z = _z_for(alpha)
    p = successes / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    lo, hi = max(0.0, center - half), min(1.0, center + half)
    return {
        "rate_pct": round(p * 100, 1),
        "lo_pct": round(lo * 100, 1),
        "hi_pct": round(hi * 100, 1),
        "half_width_pp": round((hi - lo) / 2 * 100, 1),
        "n": n,
        "successes": successes,
        "method": f"wilson {int((1 - alpha) * 100)}%",
    }


def kaplan_meier(observations: Sequence[tuple], horizons: Iterable[int] = (30, 90, 180, 365),
                 alpha: float = 0.05) -> dict:
    """Kaplan-Meier estimate of CONFIRMATION probability (= 1 - survival) with Greenwood
    variance and log-log confidence bands.

    observations: iterable of (time_days, event) where event is 1 = the awaited thing
                  happened at time_days, 0 = right-censored at time_days (we stopped
                  watching without seeing it).

    Right-censoring is the whole point: a detection that has not yet been confirmed has
    not FAILED — it has not finished being observed. Dropping those rows biases the rate
    toward whatever resolves fastest.

    Returns the curve, the estimate at each horizon with an interval and the number still
    at risk there, and the 'eventual' estimate at the largest observed event time.
    """
    obs = []
    for t, e in observations:
        try:
            tt = max(0, int(t))
            ee = 1 if int(e) == 1 else 0
        except (TypeError, ValueError):
            continue
        obs.append((tt, ee))

    n_total = len(obs)
    events_total = sum(e for _, e in obs)
    if n_total == 0 or events_total == 0:
        return {"available": False,
                "reason": "no events observed yet" if n_total else "no observations",
                "observations": n_total, "events": events_total,
                "censored": n_total - events_total}

    z = _z_for(alpha)
    event_times = sorted({t for t, e in obs if e == 1})

    S = 1.0            # survival = P(not yet confirmed)
    greenwood = 0.0    # running Σ d_i / (n_i (n_i - d_i))
    curve = []
    for t in event_times:
        d = sum(1 for tt, e in obs if e == 1 and tt == t)
        n = sum(1 for tt, _ in obs if tt >= t)      # at risk at t
        if n <= 0 or d <= 0:
            continue
        S *= (1.0 - d / n)
        if n > d:
            greenwood += d / (n * (n - d))
        # else: at the final time everyone at risk had the event -> term undefined;
        # standard practice is to leave the variance at its last value (band is widest here).
        curve.append({"t": t, "confirmed": round(1.0 - S, 4), "at_risk": n,
                      "events": d, "survival": round(S, 6), "greenwood": greenwood})

    def _band(S_val: float, gw: float) -> tuple:
        """Log-log-transformed CI for S, returned as a CI for confirmation (1-S).

        Plain Greenwood on the linear scale gives bounds outside [0,1] at small n. The
        log-log transform (Kalbfleisch-Prentice) keeps them inside by construction.
        """
        if S_val <= 0.0 or S_val >= 1.0 or gw <= 0.0:
            return (None, None)
        try:
            se_loglog = math.sqrt(gw) / abs(math.log(S_val))
            theta = math.exp(z * se_loglog)
            s_lo = S_val ** theta          # lower band on survival
            s_hi = S_val ** (1.0 / theta)  # upper band on survival
        except (ValueError, ZeroDivisionError, OverflowError):
            return (None, None)
        # confirmation = 1 - survival, so the bounds swap
        return (round((1.0 - s_hi) * 100, 1), round((1.0 - s_lo) * 100, 1))

    def _zero_event_upper(n: int) -> Optional[float]:
        """Exact (Clopper-Pearson) upper bound when 0 events have been seen in n subjects
        still under observation: 1 - (alpha/2)^(1/n) — the 'rule of three' (~3/n at 95%).

        WHY THIS EXISTS: a KM curve with no events yet has S=1, so Greenwood's variance is
        0 and the log-log transform divides by ln(1)=0 — undefined. Returning "no interval"
        there would be wrong in a way that matters for this product: at the 30- and 90-day
        horizons the matched CONTROL arm normally has zero arrivals, and that is precisely
        when we most want to show the treated arm separating from it. Zero events is not
        an absence of information — it bounds the rate from above.
        """
        if n <= 0:
            return None
        try:
            return (1.0 - (alpha / 2.0) ** (1.0 / n)) * 100.0
        except (ValueError, ZeroDivisionError, OverflowError):
            return None

    def _at(h: int) -> dict:
        last = None
        for pt in curve:
            if pt["t"] <= h:
                last = pt
            else:
                break
        at_risk_h = sum(1 for tt, _ in obs if tt >= h)
        if last is None:
            # No events by this horizon. Point estimate is 0%, with a real upper bound
            # whenever anyone is still under observation. If nobody is, we genuinely know
            # nothing at h and say so with None.
            hi = _zero_event_upper(at_risk_h)
            return {"horizon_days": h, "confirmed_pct": 0.0,
                    "lo_pct": 0.0 if hi is not None else None, "hi_pct": None if hi is None
                    else round(hi, 1), "at_risk": at_risk_h,
                    "basis": "no events by horizon; exact upper bound on 0/n"
                             if hi is not None else "no subjects under observation at horizon"}
        lo, hi = _band(last["survival"], last["greenwood"])
        return {"horizon_days": h, "confirmed_pct": round(last["confirmed"] * 100, 1),
                "lo_pct": lo, "hi_pct": hi, "at_risk": at_risk_h,
                "basis": "Kaplan-Meier with Greenwood log-log band"}

    tail = curve[-1] if curve else None
    ev_lo, ev_hi = _band(tail["survival"], tail["greenwood"]) if tail else (None, None)

    return {
        "available": True,
        "method": f"Kaplan-Meier with Greenwood variance, log-log {int((1 - alpha) * 100)}% bands",
        "observations": n_total,
        "events": events_total,
        "censored": n_total - events_total,
        "at_horizon": [_at(h) for h in horizons],
        "eventual": {
            "confirmed_pct": round(tail["confirmed"] * 100, 1) if tail else 0.0,
            "lo_pct": ev_lo, "hi_pct": ev_hi,
            "largest_event_time_days": tail["t"] if tail else None,
            "at_risk_there": tail["at_risk"] if tail else 0,
        },
        "curve": [{"t": p["t"], "confirmed_pct": round(p["confirmed"] * 100, 1),
                   "at_risk": p["at_risk"]} for p in curve],
        "caveat": ("Right-censored rows are retained at their observation time, not dropped. "
                   "Read the interval and at_risk, never the point estimate alone."),
    }


def compare_arms(treated: Sequence[tuple], control: Sequence[tuple],
                 horizons: Iterable[int] = (30, 90, 180, 365), alpha: float = 0.05) -> dict:
    """KM for a treated arm and its matched control arm, plus the separation between them.

    The Board's unanimous position: a single-arm rate is not evidence. What we publish is
    the SEPARATION between real detections and matched controls. If the intervals overlap
    at every horizon, we have not demonstrated anything — and this function says so in
    `separated`, rather than leaving a reader to eyeball two percentages.
    """
    # Materialize BOTH arms first. Passing a generator would otherwise be exhausted by
    # kaplan_meier(), and the later `bool(list(control))` would read an empty iterator as
    # "no control arm" — silently turning a real comparison into an unverified claim.
    treated = list(treated)
    control = list(control)
    t_km = kaplan_meier(treated, horizons=horizons, alpha=alpha)
    c_km = kaplan_meier(control, horizons=horizons, alpha=alpha)
    out = {"treated": t_km, "control": c_km,
           "control_arm_present": bool(control),
           "horizons": []}
    if not (t_km.get("available") and c_km.get("available")):
        out["separated"] = None
        out["verdict"] = ("insufficient data in one or both arms — no comparison is "
                          "publishable yet")
        return out

    t_by_h = {h["horizon_days"]: h for h in t_km["at_horizon"]}
    c_by_h = {h["horizon_days"]: h for h in c_km["at_horizon"]}
    any_sep = False
    for h in horizons:
        a, b = t_by_h.get(h), c_by_h.get(h)
        if not a or not b:
            continue
        delta = None
        if a["confirmed_pct"] is not None and b["confirmed_pct"] is not None:
            delta = round(a["confirmed_pct"] - b["confirmed_pct"], 1)
        # Non-overlapping log-log bands is a conservative separation test: it is stricter
        # than a formal two-sample test, so it under-claims rather than over-claims.
        sep = None
        if None not in (a.get("lo_pct"), b.get("hi_pct"), a.get("hi_pct"), b.get("lo_pct")):
            sep = a["lo_pct"] > b["hi_pct"] or b["lo_pct"] > a["hi_pct"]
            any_sep = any_sep or bool(sep)
        out["horizons"].append({
            "horizon_days": h, "treated_pct": a["confirmed_pct"], "control_pct": b["confirmed_pct"],
            "delta_pp": delta, "intervals_disjoint": sep,
            "treated_at_risk": a["at_risk"], "control_at_risk": b["at_risk"]})

    out["separated"] = any_sep
    out["verdict"] = ("treated and control separate at >=1 horizon (intervals disjoint)"
                      if any_sep else
                      "NO separation from the matched control at any horizon — the signal "
                      "has not been shown to beat its null")
    return out


if __name__ == "__main__":
    import json
    print("=== ledger_survival self-test ===\n")

    # 1. Textbook KM (Kalbfleisch & Prentice style small sample). '+' = censored.
    #    times: 6,6,6,6+,7,9+,10,10+,11+,13,16,17+,19+,20+,22,23,25+,32+,32+,34+,35+
    classic = [(6, 1), (6, 1), (6, 1), (6, 0), (7, 1), (9, 0), (10, 1), (10, 0), (11, 0),
               (13, 1), (16, 1), (17, 0), (19, 0), (20, 0), (22, 1), (23, 1), (25, 0),
               (32, 0), (32, 0), (34, 0), (35, 0)]
    km = kaplan_meier(classic, horizons=(6, 10, 23))
    print(f"classic sample: n={km['observations']} events={km['events']} "
          f"censored={km['censored']}")
    for h in km["at_horizon"]:
        print(f"  t<={h['horizon_days']:>3}d  confirmed={h['confirmed_pct']:>5}% "
              f"CI[{h['lo_pct']}, {h['hi_pct']}]  at_risk={h['at_risk']}")
    # Known result: S(6)=18/21=0.857 -> confirmed 14.3%
    s6 = km["curve"][0]["confirmed_pct"]
    assert abs(s6 - 14.3) < 0.15, f"KM S(6) wrong: {s6}"
    # Monotonic non-decreasing confirmation
    cps = [p["confirmed_pct"] for p in km["curve"]]
    assert cps == sorted(cps), "confirmation must be non-decreasing"
    # Bands must stay inside [0,100] — the whole reason for the log-log transform
    for h in km["at_horizon"]:
        for b in (h["lo_pct"], h["hi_pct"]):
            assert b is None or 0.0 <= b <= 100.0, f"band escaped [0,100]: {b}"
    print("  OK: S(6)=14.3% confirmed, monotonic, bands inside [0,100]\n")

    # 2. No events -> unavailable, not a fake zero
    assert kaplan_meier([(10, 0), (20, 0)])["available"] is False
    print("censored-only -> available:False (no fabricated rate)  OK\n")

    # 3. Wilson behaves at the edges where Wald fails
    w0 = wilson_interval(0, 20)
    assert w0["lo_pct"] == 0.0 and w0["hi_pct"] > 0, "0/20 must have a non-degenerate upper bound"
    print(f"wilson 0/20  -> {w0['rate_pct']}% CI[{w0['lo_pct']}, {w0['hi_pct']}]  OK")
    w = wilson_interval(3, 10)
    assert 0 < w["lo_pct"] < 30.0 < w["hi_pct"] < 100.0
    print(f"wilson 3/10  -> {w['rate_pct']}% CI[{w['lo_pct']}, {w['hi_pct']}]  OK\n")

    # 3c. Zero events by the horizon must still yield a usable upper bound (rule of three),
    #     not None. This is the regime the control arm lives in at 30/90 days.
    km_ne = kaplan_meier([(250, 1)] * 2 + [(300, 0)] * 28, horizons=(30,))
    h30 = km_ne["at_horizon"][0]
    assert h30["confirmed_pct"] == 0.0 and h30["lo_pct"] == 0.0, h30
    assert h30["hi_pct"] is not None and 9.0 < h30["hi_pct"] < 14.0, \
        f"0/30 upper bound should be ~11.6% (rule of three ~3/n), got {h30['hi_pct']}"
    print(f"zero events by 30d, 30 at risk -> 0.0% CI[0.0, {h30['hi_pct']}]  "
          f"(rule of three ~{round(300/30, 1)}%)  OK")
    # Invariant worth pinning: if no events have occurred by h, every event lies beyond h,
    # so subjects are necessarily still at risk there — a bound is ALWAYS available. (The
    # n<=0 guard in _zero_event_upper is therefore defensive, not reachable: an arm with no
    # events anywhere returns available:False before it can be evaluated at a horizon.)
    for arm in ([(250, 1)] * 2 + [(300, 0)] * 28, [(400, 1)], [(90, 1)] * 5 + [(95, 0)]):
        for hz in (1, 30, 89):
            row = kaplan_meier(arm, horizons=(hz,))["at_horizon"][0]
            if row["confirmed_pct"] == 0.0:
                assert row["at_risk"] > 0 and row["hi_pct"] is not None, \
                    f"zero-event horizon must still bound: {row}"
    print("invariant: a zero-event horizon always has subjects at risk -> always bounded  OK\n")

    # 4. Two-arm comparison: identical arms must NOT separate (the null must hold)
    same = [(30, 1), (60, 1), (90, 0), (120, 1), (150, 0)] * 4
    cmp_null = compare_arms(same, list(same))
    assert cmp_null["separated"] is False, "identical arms must not separate"
    print(f"identical arms -> separated={cmp_null['separated']}  ({cmp_null['verdict'][:60]}...)  OK")

    # 5. Strongly different arms SHOULD separate. The control needs at least one event —
    #    an all-censored arm has no estimable KM, and we deliberately return
    #    separated=None there rather than claiming a win by default.
    fast = [(5, 1)] * 28 + [(200, 0)] * 2      # nearly everything confirms fast
    slow = [(250, 1)] * 2 + [(300, 0)] * 28    # almost nothing confirms
    cmp_sep = compare_arms(fast, slow, horizons=(30, 90))
    assert cmp_sep["separated"] is True, "clearly different arms must separate"
    h30 = next(h for h in cmp_sep["horizons"] if h["horizon_days"] == 30)
    print(f"fast vs slow   -> separated={cmp_sep['separated']} "
          f"(30d: {h30['treated_pct']}% vs {h30['control_pct']}%, "
          f"delta={h30['delta_pp']}pp, disjoint={h30['intervals_disjoint']})  OK")

    # 5b. An all-censored control cannot be compared — must NOT read as a pass
    cmp_nc = compare_arms(fast, [(300, 0)] * 30)
    assert cmp_nc["separated"] is None, "all-censored control must not yield a verdict"
    print(f"all-censored control -> separated=None (refuses to claim a win)  OK")

    # 6. Missing control arm is reported, never silently treated as a pass
    cmp_nocontrol = compare_arms(same, [])
    assert cmp_nocontrol["separated"] is None and not cmp_nocontrol["control_arm_present"]
    print(f"no control arm -> separated=None, control_arm_present=False  OK")

    print("\nAll self-tests passed.")
