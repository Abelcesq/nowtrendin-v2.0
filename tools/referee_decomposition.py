"""Referee branch decomposition + null control — READ-ONLY MEASUREMENT HARNESS.

Step 2+3 of the Chairman-approved plan (2026-08-20), executed against the sealed
pre-registration `audits/ledger-research/REFEREE_DECOMPOSITION_PREREG_2026-08-20.md`
(PIT row 572adc8f..). The pre-registration was written and sealed BEFORE this file
existed. Read it first; the expectations E1-E4 and the binding decision rule are there,
not here.

WHAT THIS DOES
    `_referee_corroborate` (accuracy_ledger_enhanced.py:161) collapses FOUR distinct
    worlds into the single integer 0:
        (1) NO_SURGE          — Wikipedia shows no qualifying surge at all
        (2) PRECEDES          — wiki attention arrived BEFORE our detection (a real refutation)
        (3) OUTSIDE_BAND      — a surge exists, but is >14d from the GOOGLE breakout date
        (4) [None]            — unresolvable/unavailable (already distinguished in code)
    Only (2) is evidence against us. (1) and (3) are silence and ill-posedness. This
    harness instruments a FAITHFUL COPY of that function and records which branch fired,
    plus the raw quantities needed to check the sealed expectations.

WHAT THIS DOES NOT DO — enforced, not merely intended
    • No writes of any kind. No UPDATE, no INSERT, no ledger mutation, no PIT record.
      The ONLY database statement issued is SELECT (asserted at runtime, see _ro_query).
    • No change to any verdict, lead, date, rate, or served payload.
    • It does not re-specify the referee. Re-specification is a separate, later step and
      ships as wiki-v3 under the constraints sealed in the pre-registration.

THE NULL CONTROL (step 3, the decisive test)
    Running the identical instrument over LED rows alone proves nothing: a referee that
    says 0 to EVERYTHING has no discriminating power, and 0-of-14 would then be a fact
    about the instrument, not about our wins. So the same harness runs over:
        • LED / SAME_DAY   — the cohort under test
        • LAGGED           — known-positive control (Google demonstrably broke out; if
                             the referee cannot corroborate even these, it is blind)
        • PLACEBO          — the same topics against RANDOM detection dates (dates the
                             surge has no reason to sit near). A referee that corroborates
                             placebo at the same rate as real detections is measuring
                             nothing.
    Placebo dates are drawn from a FIXED seed so the run is reproducible.

USAGE
    python tools/referee_decomposition.py --out audits/ledger-research/<file>.json
    (add --limit N while smoke-testing; --skip-placebo to omit the placebo arm)

Network: hits the public Wikimedia pageviews API through referee_wikipedia's own client,
at its own pace. Rate-limited with a courtesy pause. Expect ~1s/row.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
_TRANSFER = os.path.join(os.path.dirname(_HERE), "transfer")
if _TRANSFER not in sys.path:
    sys.path.insert(0, _TRANSFER)

import referee_wikipedia as _rw            # noqa: E402
import db_compat                          # noqa: E402

# Frozen for reproducibility. The placebo arm must give the same answer on a re-run,
# or its rate is not a control, it is a coin.
PLACEBO_SEED = 20260820
# Mirrors the constants inside _referee_corroborate. Read here so the harness stays a
# faithful copy: if the production function's window ever changes, this must be updated
# deliberately, not silently inherited.
BAND_DAYS = 14
GRACE_DAYS = 2
LOOKBACK_DAYS = 30


def _parse(d):
    """Same permissive parse the ledger uses (whole-string first, never a naive split)."""
    if d is None:
        return None
    if isinstance(d, datetime):
        return d
    s = str(d).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:len(fmt) + 2].strip(), fmt)
        except Exception:
            continue
    try:
        return datetime.fromisoformat(s.replace("Z", ""))
    except Exception:
        return None


def _ro_query(conn, sql, params=()):
    """Read-only guard. The harness's central promise is that it writes nothing; that
    promise is worth more as an assertion than as a comment in the docstring."""
    stripped = sql.strip().lstrip("(").upper()
    if not stripped.startswith("SELECT"):
        raise RuntimeError(f"read-only harness attempted non-SELECT: {sql[:60]!r}")
    cur = conn.execute(sql, params) if params else conn.execute(sql)
    return [dict(r) for r in cur.fetchall()]


# ── The instrumented copy of _referee_corroborate ────────────────────────────────
# Deliberately a COPY, not a monkeypatch of the production function: the production
# path stays untouched while this runs, so there is no window in which a live sweep
# could pick up instrumented behaviour.

def decompose(topic_display, detection_date, breakout_date, article=None, pause_s=0.9):
    """Return the branch that production would have taken, plus the evidence behind it.

    `branch` is one of:
      NO_ARTICLE / NO_CURVE  -> production returns None (already honest)
      NO_SURGE               -> production returns 0  [defect 1: absence read as refutation]
      PRECEDES               -> production returns 0  [the ONLY genuine refutation]
      OUTSIDE_BAND           -> production returns 0  [defect 2/3: Google-anchored, lead-penalised]
      CORROBORATED           -> production returns 1
      ERROR                  -> production returns None via the bare except
    """
    out = {
        "branch": None, "production_value": None, "article": None,
        "curve_len": None, "baseline_mean": None, "threshold": None,
        "peak_views_in_window": None, "arrival_date": None,
        "days_arrival_minus_detection": None, "days_arrival_minus_breakout": None,
        "lead_days": None, "sub_floor": None, "error": None,
    }
    try:
        det = _parse(detection_date)
        brk = _parse(breakout_date)
        if det is None or brk is None:
            out["branch"], out["error"] = "ERROR", "unparseable date"
            return out
        out["lead_days"] = (brk - det).days

        art = article or _rw.resolve_article(topic_display)
        out["article"] = art
        if not art:
            out["branch"], out["production_value"] = "NO_ARTICLE", None
            return out

        curve = _rw.fetch_pageviews(art, det - timedelta(days=LOOKBACK_DAYS),
                                    brk + timedelta(days=BAND_DAYS))
        if pause_s:
            time.sleep(pause_s)
        if not curve:
            out["branch"], out["production_value"] = "NO_CURVE", None
            return out

        views = [p["views"] for p in curve]
        out["curve_len"] = len(curve)
        out["peak_views_in_window"] = max(views) if views else 0
        # Recompute the threshold exactly as detect_arrival_date does, so E2 (the
        # sensitivity-floor expectation) can be scored without guessing.
        quiet = sorted(views)[:max(2, int(len(views) * 0.4))]
        base_mean = max(1.0, statistics.mean(quiet) if quiet else 1.0)
        threshold = max(base_mean * _rw.SURGE_MULT, _rw.SURGE_MIN_ABS)
        out["baseline_mean"] = round(base_mean, 1)
        out["threshold"] = round(threshold, 1)
        # "Structurally unrefereeable": the article's BEST day in the whole window never
        # reaches the absolute floor, so no detection date could ever have corroborated.
        out["sub_floor"] = bool(out["peak_views_in_window"] < _rw.SURGE_MIN_ABS)

        arrival = _rw.detect_arrival_date(
            curve, since=(det - timedelta(days=LOOKBACK_DAYS)).date().isoformat())
        if not arrival or not arrival.get("arrival_date"):
            out["branch"], out["production_value"] = "NO_SURGE", 0
            return out

        out["arrival_date"] = arrival["arrival_date"]
        adt = _parse(arrival["arrival_date"])
        out["days_arrival_minus_detection"] = (adt - det).days
        out["days_arrival_minus_breakout"] = (adt - brk).days

        if adt < det - timedelta(days=GRACE_DAYS):
            out["branch"], out["production_value"] = "PRECEDES", 0
            return out
        if abs((adt - brk).days) <= BAND_DAYS:
            out["branch"], out["production_value"] = "CORROBORATED", 1
        else:
            out["branch"], out["production_value"] = "OUTSIDE_BAND", 0
        return out
    except Exception as exc:                                  # noqa: BLE001
        out["branch"], out["production_value"] = "ERROR", None
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out


# ── Cohort loading ───────────────────────────────────────────────────────────────

_ROW_COLS = ("al.id, al.topic_key, al.topic_display, al.detection_date, al.breakout_date, "
             "al.verdict, al.sweep_query, al.query_ambiguous, al.referee_corroborated, "
             "al.pre_broken, al.at_detection_days, al.referee_sealed, "
             "pd.sealed_wiki_article")


def load_cohort(conn, verdicts, limit=None):
    """The SEALED referee article lives on `pending_detections` (chosen at ENROLLMENT,
    before any outcome is knowable) and is carried through resolution, so it is joined
    back by topic_key rather than read off the ledger row. Where the pending row is gone
    or predates the sealed columns, `sealed_wiki_article` is NULL and the harness falls
    back to live opensearch — the same second-class path production marks with
    referee_sealed=0. The harness records which path each row took."""
    ph = "%s" if db_compat.USE_PG else "?"
    marks = ",".join([ph] * len(verdicts))
    sql = (f"SELECT {_ROW_COLS} FROM accuracy_ledger al "
           f"LEFT JOIN pending_detections pd ON pd.topic_key = al.topic_key "
           f"WHERE al.verdict IN ({marks}) AND al.breakout_date IS NOT NULL "
           f"ORDER BY al.detection_date DESC")
    rows = _ro_query(conn, sql, tuple(verdicts))
    # The join can duplicate a ledger row if a topic re-enrolled; keep the first.
    seen, uniq = set(), []
    for r in rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        uniq.append(r)
    return uniq[:limit] if limit else uniq


def run_arm(name, rows, date_shift=None, pause_s=0.9):
    """Run the harness over one cohort. `date_shift` (days) produces the placebo arm by
    moving the detection/breakout pair to a date the surge has no reason to sit near,
    preserving the lead length so only the ANCHOR is randomised."""
    results = []
    for i, r in enumerate(rows, 1):
        det, brk = r["detection_date"], r["breakout_date"]
        if date_shift is not None:
            d, b = _parse(det), _parse(brk)
            if d is None or b is None:
                continue
            shift = date_shift(r["id"])
            det = (d + timedelta(days=shift)).date().isoformat()
            brk = (b + timedelta(days=shift)).date().isoformat()
        d = decompose(r["topic_display"], det, brk,
                      article=r.get("sealed_wiki_article"), pause_s=pause_s)
        d.update({
            "arm": name, "ledger_id": r["id"], "topic": r["topic_display"],
            "verdict": r["verdict"], "detection_date": det, "breakout_date": brk,
            "stored_referee": r.get("referee_corroborated"),
            "query_ambiguous": r.get("query_ambiguous"),
            "sealed_article_used": bool(r.get("sealed_wiki_article")),
            "pre_broken": r.get("pre_broken"),
        })
        results.append(d)
        if i % 10 == 0:
            print(f"  [{name}] {i}/{len(rows)}", flush=True)
    return results


def summarise(results):
    """Per-arm rollup. Reports the corroboration rate two ways, because the whole point
    of the exercise is that the denominator is contested: `naive` counts every row (what
    the served metric does today), `refereeable` counts only rows where the instrument
    could actually render a verdict — CORROBORATED + PRECEDES."""
    by_arm = {}
    for r in results:
        by_arm.setdefault(r["arm"], []).append(r)
    out = {}
    for arm, rows in by_arm.items():
        branches = Counter(r["branch"] for r in rows)
        corr = branches.get("CORROBORATED", 0)
        precedes = branches.get("PRECEDES", 0)
        refereeable = corr + precedes
        sub_floor = sum(1 for r in rows if r.get("sub_floor"))
        leads = [r["lead_days"] for r in rows if r.get("lead_days") is not None]
        # STORED vs RECOMPUTED. If these disagree, the referee is not a fixed function of
        # the row — it depends on WHEN it was run. Wikimedia publishes pageviews with a
        # lag, so a referee that fired on resolution day may have judged a curve whose
        # surge had not been published yet. That would be a fifth failure branch, and one
        # NOT anticipated in the sealed pre-registration: it must be reported as such,
        # never folded silently into the branch table.
        agree = Counter()
        for r in rows:
            if r.get("arm") == "PLACEBO":
                continue          # placebo has no meaningful stored counterpart
            agree[f"stored={r.get('stored_referee')}|now={r.get('production_value')}"] += 1
        out[arm] = {
            "n": len(rows),
            "branches": dict(branches),
            "corroborated": corr,
            "genuine_refutations": precedes,
            "refereeable_n": refereeable,
            "naive_rate_pct": round(100.0 * corr / len(rows), 1) if rows else None,
            "refereeable_rate_pct": (round(100.0 * corr / refereeable, 1)
                                     if refereeable else None),
            "sub_floor_articles": sub_floor,
            "sub_floor_pct": round(100.0 * sub_floor / len(rows), 1) if rows else None,
            "lead_gt_16d": sum(1 for x in leads if x > 16),
            "median_lead_days": (round(statistics.median(leads), 1) if leads else None),
            "sealed_article_rows": sum(1 for r in rows if r.get("sealed_article_used")),
            "stored_vs_recomputed": dict(agree),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="write full JSON results here")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--lagged-limit", type=int, default=100,
                    help="null-control cohort size (pre-registered at 100)")
    ap.add_argument("--skip-placebo", action="store_true")
    ap.add_argument("--arms", default="LED,LAGGED,PLACEBO",
                    help="comma-separated subset of arms to run")
    ap.add_argument("--pause", type=float, default=0.9)
    args = ap.parse_args()

    rnd = random.Random(PLACEBO_SEED)
    conn = db_compat.connect()
    try:
        led = load_cohort(conn, ("LED", "SAME_DAY"), args.limit)
        lagged = load_cohort(conn, ("LAGGED",), args.limit or args.lagged_limit)
    finally:
        try:
            conn.close()
        except Exception:
            pass

    arms = {a.strip().upper() for a in args.arms.split(",") if a.strip()}
    print(f"cohorts: LED/SAME_DAY={len(led)}  LAGGED={len(lagged)}  arms={sorted(arms)}",
          flush=True)
    results = []
    if "LED" in arms:
        results += run_arm("LED", led, pause_s=args.pause)
    if "LAGGED" in arms:
        results += run_arm("LAGGED", lagged, pause_s=args.pause)
    if "PLACEBO" in arms and not args.skip_placebo:
        # BACKWARD-ONLY shift (corrected after run 1). A forward shift pushes the window
        # past the last published pageview day, so the row returns NO_CURVE and the
        # placebo silently loses power instead of failing loudly: run 1 lost 14 of 25
        # rows that way. Shifting only into the past keeps every window inside published
        # data, so a NO_SURGE in this arm means the referee genuinely found nothing —
        # which is the whole point of a placebo.
        offsets = {r["id"]: -rnd.randint(120, 400) for r in led}
        results += run_arm("PLACEBO", led, date_shift=lambda i: offsets.get(i, -200),
                           pause_s=args.pause)

    summary = summarise(results)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "prereg": "audits/ledger-research/REFEREE_DECOMPOSITION_PREREG_2026-08-20.md",
        "prereg_row_sha256": ("572adc8fa5690f3cb09ab32d1b94103015edf61c"
                              "8398a038ee02d258817616d4"),
        "referee_param_version": _rw.REFEREE_PARAM_VERSION,
        "surge_mult": _rw.SURGE_MULT, "surge_min_abs": _rw.SURGE_MIN_ABS,
        "placebo_seed": PLACEBO_SEED,
        "summary": summary,
        "rows": results,
    }
    print(json.dumps(summary, indent=2))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print(f"\nwrote {args.out}  ({len(results)} rows)")


if __name__ == "__main__":
    main()
