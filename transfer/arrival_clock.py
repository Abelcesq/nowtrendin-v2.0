"""
THE MAINSTREAM-ARRIVAL CLOCK — HELD-OUT ground truth for the money-movement ledger.

Board round 2 (2026-07-25): all six archetypes independently chose ABNORMAL TRADING
VOLUME, measured against an instrument's OWN trailing baseline, as the event that marks
"mainstream money/attention has arrived." The reasoning is the spine of the whole design:

  • NOT PRICE. If the confirming event were a price move, then "we detected it early"
    would mean "we were early to the move" — a trading record with the P&L column hidden.
    Volume is participation, not payoff. It fires identically on up and down moves, so it
    cannot be quietly converted into a return test. (First-Principles Guardian, R1 firewall)
  • NOT OUR ATTENTION ENGINE. Using our own Trend output as ground truth would make the
    ledger validate itself. Exchange-reported volume is independent of every scoring input.
    (the circularity trap named explicitly in the board pack)
  • ALREADY PAID FOR. FMP's `historical-price-eod/light` returns volume and we were
    discarding it — see fmp_data.historical_ohlcv. Cost of this clock: $0.

EXPLICITLY REJECTED as clocks: our own attention/topic scores (circular); price return
(R1); analyst initiation and coverage breadth as HEADLINE (the Economist's finding: our
Trend engine consumes the same RSS, so breadth is contaminated — admissible only as a
logged secondary witness after a written independence audit); options OI and retail
platform interest (no licensed source).

THE ANTI-LOOKAHEAD LOCK: the baseline is computed from a window that ENDS BEFORE the
detection date and is FROZEN INTO THE LEDGER ROW at enrollment. It is never recomputed
at resolution time. Several archetypes called this the most auditable property in the
design, and it is the reason a resolution can be re-derived years later from the stored
row alone.

CALENDAR ARTIFACTS (Challenger, round 2): earnings dates, index rebalances and lockup
expiries produce volume shocks on a PREDICTABLE schedule — "leading" them is trivial and
worthless. Arrivals near such dates are stamped `scheduled` so they can be reported in a
SEPARATE arm and kept out of the headline. We do not yet have an earnings calendar feed
wired; until we do, `scheduled` is honestly reported as None ("unknown"), never as False.
Fabricating a clean flag would be worse than admitting we cannot yet tell.

MEASUREMENT ONLY. Held-out: imported by the flow ledger and its monitors, NEVER by scoring.
"""
from __future__ import annotations

import os
import statistics
from datetime import datetime, timezone, timedelta
from typing import Optional

# Multiple of the instrument's own trailing median dollar-volume that counts as arrival.
# NOT a taste threshold: calibrate it against the PLACEBO cohort's unconditional arrival
# rate (target ~5-8% per 60d window) and freeze it in the pre-registration before any
# live enrollment. Changing it mints a new param_version and a new cohort.
ARRIVAL_VOL_MULT = float(os.getenv("ARRIVAL_VOL_MULT", "3.0"))
# Arrival must persist: N of the next M sessions must clear the multiple. A single
# print (a block trade, a fat finger) is not the crowd arriving.
ARRIVAL_HITS_REQUIRED = int(os.getenv("ARRIVAL_HITS_REQUIRED", "2"))
ARRIVAL_WINDOW_SESSIONS = int(os.getenv("ARRIVAL_WINDOW_SESSIONS", "5"))
# Trailing sessions used for the baseline, and the gap between the baseline window and
# the detection date (so the detection day's own activity cannot contaminate its baseline).
BASELINE_SESSIONS = int(os.getenv("ARRIVAL_BASELINE_SESSIONS", "60"))
BASELINE_GAP_SESSIONS = int(os.getenv("ARRIVAL_BASELINE_GAP", "5"))
# Below this many baseline observations we refuse to compute — §16a: an instrument without
# enough history is CALIBRATING, not a zero.
BASELINE_MIN_SESSIONS = int(os.getenv("ARRIVAL_BASELINE_MIN", "30"))

# v2 (2026-07-25): the observable is SHARE volume, not dollar volume. v1 was price-
# contaminated and is retired before any row was ever enrolled under it. Any change to the
# observable, the multiple, the persistence rule or the baseline window MUST mint a new
# version and a new cohort — stored rows are never re-scored under a different definition.
PARAM_VERSION = os.getenv("ARRIVAL_PARAM_VERSION", "arrival-v2-sharevolume")

# One wide, stable fetch window per ticker (see arrival_for) instead of a per-detection
# range — the latter made every ledger row mint its own HTTP call.
FETCH_WINDOW_DAYS = int(os.getenv("ARRIVAL_FETCH_WINDOW_DAYS", "1100"))   # ~3 years


def scheduled_event_on(date_str: str) -> Optional[str]:
    """Name the DETERMINISTIC calendar artifact on `date_str`, else None.

    Board round 3 (Challenger): earnings, index rebalances and lockup expiries produce
    volume shocks on a PREDICTABLE schedule — "leading" them is trivial and worthless. The
    round-2 control was an alarm when scheduled events exceed ~25% of wins, but the field
    was hard-coded None, so the alarm COULD NEVER FIRE. It was a promise, not a control.

    This stamps the artifacts that are computable with zero data: quarterly
    triple-witching (3rd Friday of Mar/Jun/Sep/Dec, when index futures/options expire and
    S&P rebalances take effect — reliably the highest-volume sessions of the year),
    month-end and quarter-end (index fund rebalancing).

    ⚠ HONEST LIMIT: earnings dates are NOT covered — we have no calendar feed wired. An
    unstamped date therefore means "no KNOWN scheduled artifact", never "verified clean".
    Callers must treat None as unknown. Fabricating a clean flag would be worse than
    admitting the gap.
    """
    d = _parse(date_str)
    if d is None:
        return None
    # 3rd Friday of a quarter-end month = triple witching
    if d.month in (3, 6, 9, 12) and d.weekday() == 4 and 15 <= d.day <= 21:
        return "triple_witching"
    nxt = d + timedelta(days=1)
    if nxt.month != d.month:
        return "quarter_end" if d.month in (3, 6, 9, 12) else "month_end"
    # last WEEKDAY of the month (month-end rebalancing lands on the last session)
    if d.weekday() == 4 and (d + timedelta(days=3)).month != d.month:
        return "quarter_end" if d.month in (3, 6, 9, 12) else "month_end"
    return None


def _iso(d) -> str:
    return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)[:10]


def _parse(s: str) -> Optional[datetime]:
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def share_volume_series(ohlcv: dict) -> dict:
    """{date: share_volume} — **THE PRIMARY OBSERVABLE.**

    ⚠ CORRECTED 2026-07-25 after a Board round-3 finding (First-Principles Guardian),
    reproduced and confirmed by probe before this change. The clock originally ran on
    DOLLAR volume (close x volume), which silently broke the R1 payoff firewall that is
    this module's entire justification:

      • share volume FLAT, price 3x  -> the clock FIRED (ratio 3.0). A pure PRICE move
        triggered the instrument that exists precisely so that "lead" is not a return
        test wearing a different name.
      • share volume 5x, price -70%  -> the clock stayed SILENT. A genuine participation
        surge was MASKED because the price collapse shrank the dollar figure.

    Dollar volume is therefore asymmetric in price (a rally inflates it, a crash deflates
    it) and cannot be described as "fires identically on up and down moves" — which is
    what the docstring claimed. Share volume, ratioed to the instrument's OWN frozen
    baseline, is price-free: the cross-instrument comparability that motivated dollars is
    already supplied by the ratio, so nothing is lost.

    Dollar volume survives as DISPLAY-ONLY context (see dollar_volume_series).
    """
    out = {}
    for d, rec in (ohlcv or {}).items():
        if not isinstance(rec, dict):
            continue
        v = rec.get("volume")
        if v is None:
            continue
        try:
            out[str(d)[:10]] = float(v)
        except (TypeError, ValueError):
            continue
    return out


def dollar_volume_series(ohlcv: dict) -> dict:
    """{date: close*volume} — **DISPLAY / CONTEXT ONLY. NEVER the arrival observable.**

    Retained because "how many dollars changed hands" is how a human reads a print, and
    it is useful beside an arrival row. It must never drive a verdict: it is price-
    contaminated (see share_volume_series for the reproduction).
    """
    out = {}
    for d, rec in (ohlcv or {}).items():
        if not isinstance(rec, dict):
            continue
        c, v = rec.get("close"), rec.get("volume")
        if c is None or v is None:
            continue
        try:
            out[str(d)[:10]] = float(c) * float(v)
        except (TypeError, ValueError):
            continue
    return out


def compute_baseline(dv: dict, asof: str,
                     sessions: int = BASELINE_SESSIONS,
                     gap: int = BASELINE_GAP_SESSIONS) -> dict:
    """Median volume over the `sessions` trading days ending `gap` sessions BEFORE `asof`.
    This is the value frozen into the ledger row at enrollment.

    Pass a SHARE-volume series (the primary observable). It accepts any date->value map,
    but the arrival verdict must be computed on shares, not dollars — see
    share_volume_series for why.

    Median (not mean) because volume is heavy-tailed — one news day would drag a mean
    baseline up and mask a subsequent genuine arrival.
    """
    a = _parse(asof)
    if a is None:
        return {"available": False, "reason": "bad asof date"}
    prior = sorted(d for d in dv if (_parse(d) or a) < a)
    if gap > 0:
        prior = prior[:-gap] if len(prior) > gap else []
    window = prior[-sessions:] if sessions else prior
    vals = [dv[d] for d in window if dv.get(d)]
    if len(vals) < BASELINE_MIN_SESSIONS:
        return {"available": False, "reason": "insufficient_history", "samples": len(vals),
                "required": BASELINE_MIN_SESSIONS, "calibrating": True}
    med = statistics.median(vals)
    if med <= 0:
        return {"available": False, "reason": "degenerate_baseline", "samples": len(vals)}
    return {"available": True, "median_volume": med, "samples": len(vals),
            "window_start": window[0], "window_end": window[-1],
            "gap_sessions": gap, "param_version": PARAM_VERSION}


def find_arrival(dv: dict, since: str, baseline_median: float,
                 mult: float = ARRIVAL_VOL_MULT,
                 hits_required: int = ARRIVAL_HITS_REQUIRED,
                 window: int = ARRIVAL_WINDOW_SESSIONS,
                 until: str = "") -> dict:
    """First session on/after `since` where volume clears `mult` x the FROZEN baseline,
    sustained over a window.

    PERSISTENCE SEMANTICS (stated exactly, because `param_version` freezes them into every
    stored row and a later "clarification" would silently redefine an existing cohort):
    the window BEGINS AT the crossing day and spans `window` sessions INCLUSIVE of it, and
    the crossing day counts as one of the `hits_required` hits. So the defaults
    (hits_required=2, window=5) mean **"the crossing day plus at least 1 more of the
    following 4 sessions"** — NOT "2 of the 5 sessions after the crossing".

    `baseline_median` is passed IN, never recomputed here — the caller supplies the value
    frozen at detection. That is what makes a resolution reproducible from the stored row.
    """
    s = _parse(since)
    if s is None or not baseline_median or baseline_median <= 0:
        return {"arrived": False, "reason": "bad inputs"}
    u = _parse(until) if until else None
    dates = sorted(d for d in dv
                   if (_parse(d) or s) >= s and (u is None or (_parse(d) or s) <= u))
    threshold = mult * baseline_median
    for i, d in enumerate(dates):
        if dv.get(d, 0) < threshold:
            continue
        # Candidate crossing — require persistence across the following window.
        forward = dates[i:i + window]
        hits = sum(1 for f in forward if dv.get(f, 0) >= threshold)
        if hits >= hits_required:
            first = _parse(d)
            return {"arrived": True, "arrival_date": d,
                    "lead_days": (first - s).days if first else None,
                    "dollar_volume": round(dv[d], 2),
                    "threshold": round(threshold, 2),
                    "ratio_to_baseline": round(dv[d] / baseline_median, 2),
                    "hits_in_window": hits, "window_sessions": len(forward),
                    # None = no KNOWN artifact, NOT "verified clean" (no earnings feed).
                    "scheduled": scheduled_event_on(d),
                    "param_version": PARAM_VERSION}
    return {"arrived": False, "sessions_checked": len(dates),
            "threshold": round(threshold, 2), "param_version": PARAM_VERSION}


def already_arrived_before(dv: dict, detection_date: str, baseline_median: float,
                           lookback_sessions: int = 10,
                           mult: float = ARRIVAL_VOL_MULT,
                           hits_required: int = ARRIVAL_HITS_REQUIRED) -> bool:
    """True if volume had ALREADY arrived shortly before detection.

    The market analogue of the attention ledger's `pre_broken` split, and the reason that
    split exists: if the crowd had already arrived when we flagged it, the row measures
    DISCOVERY LATENCY, not lead. Such rows are enrolled but excluded from the lead
    denominator and reported separately — never silently dropped, never counted as a race.

    ⚠ SYMMETRY REQUIREMENT (corrected 2026-07-25, Board round 3 — Executioner). This test
    MUST use the same persistence rule as `find_arrival`. Originally it fired on ANY single
    prior day over the threshold while `find_arrival` demanded persistence, so a lone block
    print before detection stamped the row `pre_arrived` and removed it from the lead
    denominator — on evidence too weak to have counted as an arrival in the first place.
    That asymmetry shrinks exactly the denominator the thesis is measured on, in the
    direction that flatters us (fewer races, each easier to win).
    """
    d = _parse(detection_date)
    if d is None or not baseline_median or baseline_median <= 0:
        return False
    prior = sorted(x for x in dv if (_parse(x) or d) < d)[-lookback_sessions:]
    hits = sum(1 for x in prior if dv.get(x, 0) >= mult * baseline_median)
    return hits >= hits_required


def arrival_for(ticker: str, detection_date: str, horizon_days: int = 180,
                fetch_ohlcv=None) -> dict:
    """Convenience end-to-end read for ONE instrument at ONE detection date.

    Returns the frozen baseline, whether the crowd had already arrived, and the first
    arrival within the horizon. The ledger stores the baseline from this call so the
    resolution never depends on re-fetching or re-deriving it.
    """
    if fetch_ohlcv is None:
        try:
            import fmp_data
            fetch_ohlcv = fmp_data.historical_ohlcv
        except Exception as e:
            return {"available": False, "reason": f"no price source ({e})"}

    d = _parse(detection_date)
    if d is None:
        return {"available": False, "reason": "bad detection_date"}

    # FETCH AMPLIFICATION FIX (Board round 3, Executioner). A per-detection date range
    # makes the cache key unique per row, so EVERY ledger row minted its own HTTP call —
    # invisible at 16 tickers, hundreds of calls per sweep once enrollment goes
    # market-wide. Instead request ONE WIDE, STABLE window per ticker: the range depends
    # only on the ticker and today's date, so every detection for that ticker on a given
    # day shares a single cached fetch. ~3y of daily bars covers any baseline + horizon.
    today = datetime.now(timezone.utc)
    frm = _iso(min(d - timedelta(days=400), today - timedelta(days=FETCH_WINDOW_DAYS)))
    to = _iso(today)
    try:
        ohlcv = fetch_ohlcv(ticker, frm, to)
    except Exception as e:
        return {"available": False, "reason": f"fetch failed ({e})"}
    if not ohlcv:
        return {"available": False, "reason": "no price/volume data"}

    sv = share_volume_series(ohlcv)          # PRIMARY — price-free (see share_volume_series)
    if not sv:
        return {"available": False, "reason": "no volume in payload"}
    base = compute_baseline(sv, detection_date)
    if not base.get("available"):
        return {"available": False, "reason": base.get("reason"),
                "calibrating": base.get("calibrating", False), "baseline": base}

    med = base["median_volume"]
    horizon_end = _iso(d + timedelta(days=horizon_days))
    arr = find_arrival(sv, detection_date, med, until=horizon_end)

    # Dollar volume travels alongside as human-readable CONTEXT only. It is never
    # consulted for the verdict — it is price-contaminated by construction.
    dv_ctx = dollar_volume_series(ohlcv)
    if arr.get("arrived") and arr.get("arrival_date") in dv_ctx:
        arr["dollar_volume_context"] = round(dv_ctx[arr["arrival_date"]], 2)

    return {"available": True, "ticker": ticker.upper(),
            "detection_date": str(detection_date)[:10],
            "observable": "share_volume_ratio_to_frozen_baseline",
            "baseline": base,
            "pre_arrived": already_arrived_before(sv, detection_date, med),
            "arrival": arr, "horizon_days": horizon_days,
            "param_version": PARAM_VERSION}


if __name__ == "__main__":
    print("=== arrival_clock self-test (synthetic, no network) ===\n")
    base_day = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def mk(vols):
        """Build an ohlcv payload from a list of share volumes at a constant $10 close."""
        return {_iso(base_day + timedelta(days=i)): {"close": 10.0, "volume": v}
                for i, v in enumerate(vols)}

    # 100 quiet sessions at 1000 shares, then a sustained 5x surge from index 100.
    quiet = [1000] * 100
    surge = [5000] * 6 + [1000] * 20
    sv = share_volume_series(mk(quiet + surge))
    det = _iso(base_day + timedelta(days=99))          # detect the day before the surge

    b = compute_baseline(sv, det)
    assert b["available"] and abs(b["median_volume"] - 1000.0) < 1e-6, b
    print(f"baseline: {b['median_volume']:,.0f} shares from {b['samples']} sessions "
          f"(window {b['window_start']}..{b['window_end']}, gap {b['gap_sessions']})  OK")

    a = find_arrival(sv, det, b["median_volume"])
    assert a["arrived"] and a["ratio_to_baseline"] == 5.0, a
    print(f"arrival: {a['arrival_date']} lead={a['lead_days']}d "
          f"ratio={a['ratio_to_baseline']}x hits={a['hits_in_window']}  OK")

    # Anti-lookahead: the baseline must exclude the detection day and the gap window.
    assert b["window_end"] < det, "baseline window must end strictly before detection"
    print(f"anti-lookahead: window_end {b['window_end']} < detection {det}  OK")

    # A single one-day spike must NOT count as arrival (persistence requirement).
    sv_blip = share_volume_series(mk(quiet + [5000] + [1000] * 20))
    a2 = find_arrival(sv_blip, det, b["median_volume"])
    assert not a2["arrived"], f"single-day blip must not be an arrival: {a2}"
    print("single-day blip -> not an arrival (persistence enforced)  OK")

    # REGRESSION (Board R3, Guardian): a PURE PRICE MOVE must NOT fire the clock, and a
    # genuine volume surge must NOT be masked by a price crash. v1 failed both.
    rally = {_iso(base_day + timedelta(days=i)): {"close": p, "volume": 1000}
             for i, p in enumerate([10.0] * 100 + [30.0] * 6 + [10.0] * 20)}
    sv_r = share_volume_series(rally)
    b_r = compute_baseline(sv_r, det)
    assert not find_arrival(sv_r, det, b_r["median_volume"])["arrived"], \
        "R1 LEAK: a pure price move fired the volume clock"
    print("price 3x, shares flat -> NOT an arrival (R1 firewall holds)  OK")
    crash = {_iso(base_day + timedelta(days=i)): {"close": p, "volume": v}
             for i, (p, v) in enumerate(zip([10.0] * 100 + [3.0] * 6 + [10.0] * 20,
                                            [1000] * 100 + [5000] * 6 + [1000] * 20))}
    sv_c = share_volume_series(crash)
    b_c = compute_baseline(sv_c, det)
    assert find_arrival(sv_c, det, b_c["median_volume"])["arrived"], \
        "genuine volume surge was masked by a price crash"
    print("shares 5x during a -70% crash -> IS an arrival (not masked)  OK")

    # pre-arrival detection: crowd already there before we flagged it
    sv_pre = share_volume_series(mk([1000] * 95 + [5000] * 5 + [5000] * 10))
    det_late = _iso(base_day + timedelta(days=100))
    b2 = compute_baseline(sv_pre, det_late)
    assert already_arrived_before(sv_pre, det_late, b2["median_volume"]), \
        "should detect the crowd already arrived"
    print("pre_arrived detected (discovery latency, not lead)  OK")

    # REGRESSION (Board R3, Executioner): pre_arrived must use the SAME persistence rule
    # as find_arrival. A lone pre-detection blip must NOT disqualify the row.
    sv_blip_pre = share_volume_series(mk([1000] * 95 + [5000] + [1000] * 4 + [1000] * 20))
    b_bp = compute_baseline(sv_blip_pre, det_late)
    assert not already_arrived_before(sv_blip_pre, det_late, b_bp["median_volume"]), \
        "a single pre-detection blip must not shrink the lead denominator"
    print("single pre-detection blip -> NOT pre_arrived (symmetric with find_arrival)  OK")

    # §16a: too little history must refuse, not return a zero
    sv_thin = share_volume_series(mk([1000] * 10))
    b3 = compute_baseline(sv_thin, _iso(base_day + timedelta(days=9)))
    assert not b3["available"] and b3.get("calibrating"), b3
    print(f"thin history -> refuses ({b3['reason']}, calibrating=True)  OK")

    # A flat/degenerate series must not fabricate a baseline of zero
    sv_zero = share_volume_series({_iso(base_day + timedelta(days=i)):
                                   {"close": 10.0, "volume": 0} for i in range(80)})
    b4 = compute_baseline(sv_zero, _iso(base_day + timedelta(days=79)))
    assert not b4["available"], b4
    print(f"zero-volume history -> refuses ({b4['reason']})  OK")

    # Scheduled-artifact stamps (Board R3): the field must actually populate, or the
    # "too many scheduled wins" alarm can never fire.
    assert scheduled_event_on("2026-06-19") == "triple_witching", \
        scheduled_event_on("2026-06-19")           # 3rd Friday of June
    assert scheduled_event_on("2026-03-20") == "triple_witching"
    assert scheduled_event_on("2026-06-30") == "quarter_end"
    assert scheduled_event_on("2026-07-31") == "month_end"
    assert scheduled_event_on("2026-07-15") is None
    print("scheduled stamps: triple_witching / quarter_end / month_end populate  OK")
    print("  (None = no KNOWN artifact, NOT verified-clean — no earnings feed wired)")

    print("\nAll self-tests passed.")
