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
    # Observations are `(time, event)` or `(time, event, stratum)` — the stratum is carried
    # for the stratified log-rank and IGNORED here (KM is a pooled, single-arm estimate).
    # Accepting both shapes keeps one arm-building path in the caller: building the arms
    # twice is how the two analyses drift apart on subtly different data.
    obs = []
    for row in observations:
        try:
            tt = max(0, int(row[0]))
            ee = 1 if int(row[1]) == 1 else 0
        except (TypeError, ValueError, IndexError):
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


def _chi2_sf_1df(x: float) -> float:
    """Upper tail of chi-square with 1 df = erfc(sqrt(x/2)). Exact, no tables, no SciPy."""
    if x <= 0:
        return 1.0
    return math.erfc(math.sqrt(x / 2.0))


def stratified_logrank(treated: Sequence[tuple], control: Sequence[tuple],
                       alpha: float = 0.05, follow_up_days: Optional[int] = None) -> dict:
    """Stratified log-rank test on time-to-arrival. THE PRE-REGISTERED PRIMARY ANALYSIS.

    ⚠ B8 (Board review 2, Economist). The pre-registration named a stratified log-rank as the
    PRIMARY analysis and nothing in this codebase computed one — the only implemented test
    was the disjoint-bands PUBLICATION GATE, which the registration lists as the conservative
    secondary. Writing the test statistic after the data accumulate is precisely the analytic
    flexibility a pre-registration exists to foreclose, so it is implemented here, BEFORE the
    first row enrolls, with its conventions fixed in code rather than chosen later.

    CONVENTIONS (fixed; changing any of them is a new registration):
      • Observations are `(time, event, stratum)`; `event` 1 = arrival, 0 = right-censored.
      • STRATA are the match groups — one treated row and its matched controls. Comparing
        within the stratum is the whole point of matching: sector, size, ADV and pretrend are
        held fixed, so the test asks whether the DISCLOSURE moved the clock, not whether
        big liquid names move differently from small ones.
      • Mantel-Haenszel form: at each distinct event time in a stratum, O = observed treated
        events, E = d*n1/n, V = d*n1*n0*(n-d) / (n^2*(n-1)). Sum O-E and V ACROSS strata,
        then Z = sum(O-E)/sqrt(sum V), chi-square 1 df, TWO-SIDED at `alpha`.
      • Ties: hypergeometric variance with the (n-d)/(n-1) correction (exact for tied times).
      • A stratum with no events, or with only one arm at risk, contributes ZERO information
        and is skipped — reported as `strata_uninformative`, never silently dropped.
      • `follow_up_days` right-censors every observation at the registered horizon before
        testing, so the test uses the whole curve up to the horizon and no further.

    Returns the statistic, the two-sided p-value, and the DIRECTION. Direction matters: a
    significant result with sum(O-E) < 0 means controls arrived SOONER than treated — the
    opposite of the hypothesis, and it must be reported as a refutation, never as "a result".
    """
    def _prep(rows, arm):
        out = []
        for r in rows or []:
            t, e = float(r[0]), int(r[1])
            s = r[2] if len(r) > 2 else "_pooled"
            if follow_up_days is not None and t > follow_up_days:
                t, e = float(follow_up_days), 0        # censor at the registered horizon
            out.append((t, e, s, arm))
        return out

    obs = _prep(treated, 1) + _prep(control, 0)
    if not obs:
        return {"available": False, "reason": "no observations"}

    strata = {}
    for t, e, s, arm in obs:
        strata.setdefault(s, []).append((t, e, arm))

    sum_o_minus_e = 0.0
    sum_var = 0.0
    used = uninformative = 0
    total_events = 0
    for s, rows in strata.items():
        n1 = sum(1 for _, _, a in rows if a == 1)
        n0 = len(rows) - n1
        ev = sum(e for _, e, _ in rows)
        if n1 == 0 or n0 == 0 or ev == 0:
            uninformative += 1
            continue
        used += 1
        total_events += ev
        contributed = False
        for t in sorted({tt for tt, e, _ in rows if e == 1}):
            # Recompute risk sets at this time (small strata — clarity over cleverness).
            r1 = sum(1 for tt, _, a in rows if a == 1 and tt >= t)
            r0 = sum(1 for tt, _, a in rows if a == 0 and tt >= t)
            n = r1 + r0
            if n < 2 or r1 == 0 or r0 == 0:
                continue
            d = sum(1 for tt, e, _ in rows if e == 1 and tt == t)
            d1 = sum(1 for tt, e, a in rows if e == 1 and tt == t and a == 1)
            sum_o_minus_e += d1 - (d * r1 / n)
            sum_var += (d * r1 * r0 * (n - d)) / (n * n * (n - 1))
            contributed = True
        if not contributed:
            used -= 1
            uninformative += 1

    if sum_var <= 0:
        return {"available": False, "reason": "no informative strata — the test carries no "
                                              "information yet",
                "strata_total": len(strata), "strata_used": used,
                "strata_uninformative": uninformative, "events": total_events}

    z = sum_o_minus_e / math.sqrt(sum_var)
    chi2 = z * z
    p = _chi2_sf_1df(chi2)
    direction = ("treated_arrives_sooner" if sum_o_minus_e > 0
                 else "control_arrives_sooner" if sum_o_minus_e < 0 else "no_difference")
    significant = p < alpha
    return {
        "available": True, "test": "stratified log-rank (Mantel-Haenszel), two-sided",
        "strata_total": len(strata), "strata_used": used,
        "strata_uninformative": uninformative,
        "events": total_events,
        "observed_minus_expected": round(sum_o_minus_e, 4),
        "variance": round(sum_var, 4),
        "z": round(z, 4), "chi_square": round(chi2, 4), "df": 1,
        "p_value": round(p, 6), "alpha": alpha,
        "significant": bool(significant),
        "direction": direction,
        "follow_up_days": follow_up_days,
        "verdict": (
            "treated arrives SOONER than matched controls "
            f"(p={p:.4g})" if significant and direction == "treated_arrives_sooner" else
            "REFUTED IN THE OPPOSITE DIRECTION: matched controls arrived sooner than "
            f"treated (p={p:.4g}) — this refutes the hypothesis, it is not support for it"
            if significant and direction == "control_arrives_sooner" else
            f"no significant difference from matched controls (p={p:.4g}) — the null stands"),
    }


def compare_arms(treated: Sequence[tuple], control: Sequence[tuple],
                 horizons: Iterable[int] = (30, 90, 180, 365), alpha: float = 0.05,
                 primary_horizon: Optional[int] = None) -> dict:
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
    # ⚠ O3 (Board round 4, Challenger): `separated` previously meant "disjoint at ANY
    # horizon", i.e. three or four independent chances to beat the null — a multiple-
    # comparisons problem hidden inside a boolean. The verdict is now decided by ONE
    # pre-registered primary horizon; every other horizon is descriptive only.
    hz = list(horizons)
    primary = primary_horizon if primary_horizon is not None else (hz[0] if hz else None)
    any_sep = False
    primary_sep = None
    for h in hz:
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
        if h == primary:
            primary_sep = sep
        out["horizons"].append({
            "horizon_days": h, "treated_pct": a["confirmed_pct"], "control_pct": b["confirmed_pct"],
            "delta_pp": delta, "intervals_disjoint": sep,
            "is_primary": h == primary,
            "treated_at_risk": a["at_risk"], "control_at_risk": b["at_risk"]})

    # The VERDICT is the primary horizon alone. `separated_any_horizon` is retained purely
    # as a descriptive diagnostic and must never be published as the result.
    out["primary_horizon_days"] = primary
    out["separated"] = bool(primary_sep)
    out["separated_any_horizon"] = any_sep
    out["verdict"] = (
        f"treated separates from matched control at the pre-registered primary horizon "
        f"({primary}d)" if primary_sep else
        f"NO separation from the matched control at the pre-registered primary horizon "
        f"({primary}d) — the signal has not been shown to beat its null"
        + (" (note: a NON-primary horizon appears disjoint; that is descriptive only and "
           "is not a result)" if any_sep else ""))
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

    # 5c. REGRESSION (Board R4, O3 — Challenger): separation at a NON-primary horizon must
    #     NOT count as a result. `separated` previously meant "disjoint at ANY horizon",
    #     which is three or four chances at the null hidden inside a boolean.
    late_t = [(150, 1)] * 28 + [(400, 0)] * 2     # nothing happens before 180d
    late_c = [(350, 1)] * 2 + [(400, 0)] * 28
    cmp_late = compare_arms(late_t, late_c, horizons=(30, 180), primary_horizon=30)
    assert cmp_late["separated"] is False, \
        "must not claim a win when the primary horizon does not separate"
    assert cmp_late["separated_any_horizon"] is True, cmp_late
    assert cmp_late["primary_horizon_days"] == 30
    print("separates only at a NON-primary horizon -> separated=False  OK")
    print(f"  verdict: {cmp_late['verdict'][:88]}...")
    # ...and declaring 180 primary flips the verdict, as it should
    cmp_p180 = compare_arms(late_t, late_c, horizons=(30, 180), primary_horizon=180)
    assert cmp_p180["separated"] is True, cmp_p180
    print("same data, primary=180 -> separated=True (the horizon must be pre-registered)  OK")

    # 6. Missing control arm is reported, never silently treated as a pass
    cmp_nocontrol = compare_arms(same, [])
    assert cmp_nocontrol["separated"] is None and not cmp_nocontrol["control_arm_present"]
    print(f"no control arm -> separated=None, control_arm_present=False  OK")

    # ── 7. STRATIFIED LOG-RANK (B8) — the pre-registered PRIMARY analysis ────────────────
    # Validated against a PUBLISHED result, because an estimator nobody checked against a
    # known answer is not evidence. Freireich et al. 6-MP vs placebo (Kalbfleisch & Prentice):
    # log-rank chi-square = 16.79, p = 4.2e-05, placebo relapses sooner.
    fre_t = [(6, 0), (6, 1), (6, 1), (6, 1), (7, 1), (9, 0), (10, 0), (10, 1), (11, 0),
             (13, 1), (16, 1), (17, 0), (19, 0), (20, 0), (22, 1), (23, 1), (25, 0),
             (32, 0), (32, 0), (34, 0), (35, 0)]
    fre_c = [(1, 1), (1, 1), (2, 1), (2, 1), (3, 1), (4, 1), (4, 1), (5, 1), (5, 1),
             (8, 1), (8, 1), (8, 1), (8, 1), (11, 1), (11, 1), (12, 1), (12, 1),
             (15, 1), (17, 1), (22, 1), (23, 1)]
    lr = stratified_logrank(fre_t, fre_c)
    assert abs(lr["chi_square"] - 16.79) < 0.02, lr["chi_square"]
    assert abs(lr["p_value"] - 4.2e-05) < 1e-06, lr["p_value"]
    assert lr["direction"] == "control_arrives_sooner", lr
    print(f"log-rank vs PUBLISHED Freireich trial: chi2={lr['chi_square']} "
          f"p={lr['p_value']:.2g} (published 16.79 / 4.2e-05)  OK")

    # Type-I calibration: under the null the rejection rate must sit near alpha. A test that
    # never rejects is useless; one that rejects often manufactures findings.
    import random as _rnd

    def _t1(strata, reps=400, per_arm=80, seed=11):
        rng = _rnd.Random(seed)
        rej = usable = 0
        for _ in range(reps):
            t, c = [], []
            for g in range(strata):
                for _ in range(per_arm // strata):
                    t.append((rng.expovariate(1 / 30.0), 1, f"g{g}"))
                    c.append((rng.expovariate(1 / 30.0), 1, f"g{g}"))
            r = stratified_logrank(t, c)
            if r.get("available"):
                usable += 1
                rej += 1 if r["significant"] else 0
        return rej / usable
    for _s in (1, 20):
        _rate = _t1(_s)
        assert 0.02 <= _rate <= 0.09, f"type-I rate {_rate} at {_s} strata is not ~0.05"
        print(f"log-rank type-I rate at {_s:>2} strata = {_rate:.3f} (target 0.05)  OK")

    # Power: a real 2x hazard difference must actually be detected, in the RIGHT direction.
    _rng = _rnd.Random(3)
    _det = 0
    for _ in range(200):
        _t = [(_rng.expovariate(1 / 60.0), 1, f"g{i % 20}") for i in range(80)]
        _c = [(_rng.expovariate(1 / 30.0), 1, f"g{i % 20}") for i in range(80)]
        _r = stratified_logrank(_t, _c)
        _det += 1 if _r["significant"] and _r["direction"] == "control_arrives_sooner" else 0
    assert _det / 200 > 0.85, _det
    print(f"log-rank detects a true 2x hazard gap in {_det / 200:.0%} of replications  OK")

    # An OPPOSITE-direction significant result must read as a REFUTATION, never as support.
    _opp = stratified_logrank([(2, 1, "g"), (3, 1, "g"), (2, 1, "h"), (3, 1, "h")],
                              [(40, 1, "g"), (41, 1, "g"), (40, 1, "h"), (41, 1, "h")])
    assert _opp["direction"] == "treated_arrives_sooner"
    _opp2 = stratified_logrank([(40, 1, "g"), (41, 1, "g")], [(2, 1, "g"), (3, 1, "g")])
    assert "REFUTES" in _opp2["verdict"] or not _opp2["significant"], _opp2["verdict"]
    # Uninformative strata are counted, never silently dropped.
    _u = stratified_logrank([(5, 0, "a")], [(5, 0, "a")])
    assert not _u["available"] and _u["strata_uninformative"] == 1, _u
    print("direction reported honestly; uninformative strata counted, not dropped  OK")

    # KM must accept the 3-tuple shape the log-rank needs, so ONE arm feeds both analyses.
    # Building the arms twice is how two analyses quietly end up on different data.
    _mixed = kaplan_meier([(10, 1, "g1"), (20, 0, "g1"), (30, 1, "g2")], horizons=(30,))
    assert _mixed["available"] and _mixed["observations"] == 3, _mixed
    print("KM accepts (t,e) and (t,e,stratum) alike -> one arm feeds both analyses  OK")

    print("\nAll self-tests passed.")
