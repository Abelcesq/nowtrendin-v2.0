#!/usr/bin/env python3
"""
d_plumbing_ab.py — Chairman ruling 1c (board round 4, 2026-08-20D):
the paired A/B recompute over the frozen pre-flip snapshot.

WHAT THIS IDENTIFIES, EXACTLY (mandatory output language — do not soften):
  ONE of the five 2026-08-20 treatments, CONDITIONALLY:  E[T5 | T1..T4 = ON].
  T1–T4 main effects are PERMANENTLY UNIDENTIFIED BY DESIGN, not by data loss —
  five treatments at one switch point is a rank-1 design matrix, and no
  post-hoc analysis recovers what the design never encoded (Statistician's
  binding caveat, carried in the snapshot manifest itself).

  FURTHER CONDITIONING, verified in code before this script was written
  (§10a): `is_first_timer` is a STORED bit stamped at collection time, and the
  snapshot's window (2026-08-14 → 08-19) predates the flip — so every blog/
  discovery-lane row carries the OLD writers' hardcoded 0.  Toggling
  `_D_PLUMBING_V2` here therefore measures the COMPUTE-SIDE component of T5
  only (the ft-ratio denominator and the author-platform set inside
  `compute_dark_matter`); the WRITER-SIDE component (real first-timer bits on
  the blog lanes) is not identifiable from pre-flip stamps.  Anyone quoting
  this result quotes E[T5.compute | T1..T4 = ON, pre-flip writer stamps].

ORDER OF OPERATIONS (the ruling's own):
  1. ARM-VALIDITY CHECK — verify the flag is consulted at compute time (a
     constructed fixture must flip between arms; if it does not, the arm is
     void and the script aborts rather than printing a zero delta as a truth).
  2. T3 NULL-TREATMENT CHECK — count Reddit rows in the snapshot; per f5b1956
     Reddit had been 403-ing for two months, so ≈0 rows drops T3 and the
     confound set falls 5 → 4 for free.
  3. The paired recompute: `compute_dark_matter` (the REAL production method,
     never a re-implementation) over IDENTICAL rows, flag OFF then ON.
  4. Report the PAIRED WITHIN-TOPIC difference with a bootstrap CI over
     topics (the recompute is deterministic over identical rows, so each
     topic's delta is EXACT; the uncertainty is over WHICH topics).
  5. ONE preregistered primary contrast: the T5 main effect on D, pooled.
     Everything else is EXPLORATORY under Benjamini–Hochberg (uncorrected,
     P(≥1 false positive) across 15 contrasts = 53.7%).
  6. Any cohort with fewer than 30 resolved-author rows prints
     "underpowered, not estimable" — never a number.

DEFERRED_ITEMS asked for three exploratory cuts; two are computable here:
  (i)  by platform, (ii) feed cohort (the 12 new WordPress lanes vs the rest —
  platform=='wordpress' is the honest proxy; the 3 sports desks are not
  distinguishable from the snapshot's columns and are NOT guessed at),
  (iii) ft_ratio by community collection age <14d vs ≥14d — NOT ESTIMABLE from
  this snapshot: community collection ages live in author_history /
  community-first-seen state, which the snapshot deliberately does not carry.
  Stated here so absence reads as absence, not as a run that forgot.

Usage:
  python3 tools/d_plumbing_ab.py                      # default snapshot paths
  python3 tools/d_plumbing_ab.py --out results.json   # row-level JSON out

Read-only over the snapshot; touches no database, no score, no served value.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "transfer"))

SNAP_DIR = os.path.join(_ROOT, "audits", "ab-attribution")
SEED = 1082          # fixed: reruns against the sealed baseline must reproduce
N_BOOT = 2000
UNDERPOWERED_MIN = 30


def _load_jsonl_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_snapshot(snap_dir):
    """Mirror the production signal loader's shape: topic_signals LEFT JOIN
    raw_signals on rs.id = ts.signal_id for author/title, platform_tier !=
    'unverified' (gravitational_anomaly_detector._get_topic_signals)."""
    raw_by_id = {}
    for r in _load_jsonl_gz(os.path.join(snap_dir, "preflip_raw_signals.jsonl.gz")):
        raw_by_id[r.get("id")] = r
    topics = {}
    n_rows = 0
    for ts in _load_jsonl_gz(os.path.join(snap_dir, "preflip_topic_signals.jsonl.gz")):
        if (ts.get("platform_tier") or "") == "unverified":
            continue
        rs = raw_by_id.get(ts.get("signal_id"))
        ts["author"] = (rs or {}).get("author")
        ts["title"] = (rs or {}).get("title")
        topics.setdefault(ts.get("topic_key"), []).append(ts)
        n_rows += 1
    return topics, raw_by_id, n_rows


def arm_validity_check(g, det):
    """The flag must act at COMPUTE time on identical rows, or the arm is void
    (the ruling's precondition, made executable). A wordpress-heavy fixture
    with real authors and stamped first-timers must read differently under the
    two arms (V2 widens the author-platform set and narrows the ft pool)."""
    fixture = (
        [{"platform": "wordpress", "author": f"a{i}", "is_first_timer": 1,
          "upvotes": 0, "comments": 0, "is_organic": 1, "engagement_raw": 1}
         for i in range(4)]
        + [{"platform": "gdelt", "author": "", "is_first_timer": 0,
            "upvotes": 0, "comments": 0, "is_organic": 1, "engagement_raw": 1}
           for _ in range(8)]
    )
    g._D_PLUMBING_V2 = False
    off = det.compute_dark_matter(list(fixture))
    g._D_PLUMBING_V2 = True
    on = det.compute_dark_matter(list(fixture))
    g._D_PLUMBING_V2 = False
    if off == on:
        raise SystemExit(
            "ARM VOID: compute_dark_matter is identical under both flag "
            "values on a fixture built to separate them — the flag is baked "
            "somewhere upstream of compute time. Do not report a delta.")
    return off, on


def _bh(pvals):
    """Benjamini–Hochberg adjusted p-values (q-values), preserving order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    prev = 1.0
    for rank_from_top in range(m, 0, -1):
        i = order[rank_from_top - 1]
        q = min(prev, pvals[i] * m / rank_from_top)
        adj[i] = q
        prev = q
    return adj


def _boot_ci_p(deltas, rng):
    """Percentile bootstrap CI for the mean paired delta + a two-sided
    bootstrap p-value against 0. Deltas are exact per topic; the resample is
    over topics."""
    n = len(deltas)
    if n == 0:
        return None, None, None, None
    means = []
    for _ in range(N_BOOT):
        s = [deltas[rng.randrange(n)] for _ in range(n)]
        means.append(sum(s) / n)
    means.sort()
    lo = means[int(0.025 * N_BOOT)]
    hi = means[int(0.975 * N_BOOT) - 1]
    ge = sum(1 for m in means if m >= 0.0) / N_BOOT
    le = sum(1 for m in means if m <= 0.0) / N_BOOT
    p = max(min(2.0 * min(ge, le), 1.0), 1.0 / N_BOOT)
    mean = sum(deltas) / n
    return mean, lo, hi, p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snap-dir", default=SNAP_DIR)
    ap.add_argument("--out", default=os.path.join(SNAP_DIR, "d_plumbing_ab_rows.json"))
    args = ap.parse_args()

    os.environ.setdefault("D_PLUMBING_V2", "0")
    import gravitational_anomaly_detector as g
    cls = g.GravitationalAnomalyDetector
    det = cls.__new__(cls)          # no DB: compute_dark_matter is pure over rows

    print("d_plumbing_ab — E[T5.compute | T1..T4 = ON, pre-flip writer stamps]")
    print("=" * 72)

    # 1 — arm validity
    off_fix, on_fix = arm_validity_check(g, det)
    print(f"[1] arm valid: fixture D {off_fix[0]:.2f} (OFF) != {on_fix[0]:.2f} (ON) "
          f"— flag consulted at compute time")

    # 2 — T3 null check (BEFORE any contrast)
    topics, raw_by_id, n_rows = load_snapshot(args.snap_dir)
    reddit_rows = sum(1 for r in raw_by_id.values()
                      if (r.get("platform") or "").lower() == "reddit")
    print(f"[2] T3 null check: {reddit_rows} reddit rows in the snapshot "
          + ("→ T3 DROPS; the confound set is 4, not 5"
         if reddit_rows == 0 else "→ T3 stays in the confound set"))

    # 3 — paired recompute over identical rows
    min_app = getattr(g, "MIN_TOPIC_APPEARANCES", 2)
    high_mag = getattr(g, "HIGH_MAGNITUDE_ENG", 8.0)
    rows_out = []
    for tk, signals in topics.items():
        eligible = (len(signals) >= min_app
                    or any(float(s.get("engagement_raw") or 0) >= high_mag
                           for s in signals))
        g._D_PLUMBING_V2 = False
        d0, ft0, _, m0 = det.compute_dark_matter(list(signals))
        g._D_PLUMBING_V2 = True
        d1, ft1, _, m1 = det.compute_dark_matter(list(signals))
        g._D_PLUMBING_V2 = False
        plats = sorted({(s.get("platform") or "").lower() for s in signals})
        rows_out.append({
            "topic_key": tk, "n_signals": len(signals),
            "scoring_eligible": eligible,
            "platforms": plats,
            "has_resolved_author": any((s.get("author") or "").strip()
                                       for s in signals),
            "D_off": d0, "D_on": d1, "delta_D": round(d1 - d0, 4),
            "ft_off": round(ft0, 4), "ft_on": round(ft1, 4),
            "d_measured_off": m0, "d_measured_on": m1,
        })

    rng = random.Random(SEED)
    scored = [r for r in rows_out if r["scoring_eligible"]]
    print(f"[3] snapshot: {n_rows} joined rows, {len(topics)} topics, "
          f"{len(scored)} scoring-eligible")

    # 4/5 — PRIMARY (preregistered): T5 main effect on D, pooled, scoring-eligible
    deltas = [r["delta_D"] for r in scored]
    mean, lo, hi, p = _boot_ci_p(deltas, rng)
    n_auth = sum(1 for r in scored if r["has_resolved_author"])
    print("\nPRIMARY (preregistered): pooled paired ΔD over scoring-eligible topics")
    if n_auth < UNDERPOWERED_MIN:
        print(f"  underpowered, not estimable ({n_auth} resolved-author rows "
              f"< {UNDERPOWERED_MIN})")
    else:
        print(f"  mean ΔD = {mean:+.4f}  bootstrap 95% CI [{lo:+.4f}, {hi:+.4f}]  "
              f"p≈{p:.4f}  (n={len(deltas)} topics, {n_auth} with a resolved author)")
        print(f"  d_measured flips OFF→ON: "
              f"{sum(1 for r in scored if r['d_measured_on'] and not r['d_measured_off'])} "
              f"gained, "
              f"{sum(1 for r in scored if r['d_measured_off'] and not r['d_measured_on'])} lost")

    # EXPLORATORY under BH — by platform, and the wordpress-lane feed cohort
    contrasts = []
    plat_topics = {}
    for r in scored:
        for pl in r["platforms"]:
            plat_topics.setdefault(pl, []).append(r)
    for pl, rs in sorted(plat_topics.items()):
        contrasts.append((f"platform:{pl}", rs))
    contrasts.append(("feed-cohort:wordpress-lanes",
                      [r for r in scored if "wordpress" in r["platforms"]]))
    contrasts.append(("feed-cohort:non-wordpress",
                      [r for r in scored if "wordpress" not in r["platforms"]]))

    print(f"\nEXPLORATORY ({len(contrasts)} contrasts, Benjamini–Hochberg; "
          f"uncorrected P(≥1 false positive) at 15 contrasts = 53.7%)")
    results, pvals = [], []
    for name, rs in contrasts:
        na = sum(1 for r in rs if r["has_resolved_author"])
        if na < UNDERPOWERED_MIN:
            results.append((name, None, na, len(rs)))
            continue
        m2, l2, h2, p2 = _boot_ci_p([r["delta_D"] for r in rs], rng)
        results.append((name, (m2, l2, h2, p2), na, len(rs)))
        pvals.append(p2)
    adj_iter = iter(_bh(pvals)) if pvals else iter(())
    for name, stat, na, n in results:
        if stat is None:
            print(f"  {name:34s} underpowered, not estimable "
                  f"({na} resolved-author rows < {UNDERPOWERED_MIN}; n={n})")
        else:
            m2, l2, h2, p2 = stat
            q = next(adj_iter)
            print(f"  {name:34s} ΔD {m2:+.4f} CI [{l2:+.4f},{h2:+.4f}] "
                  f"p≈{p2:.4f} q≈{q:.4f} (n={n})")
    print("  ft-by-community-age (<14d vs ≥14d): NOT ESTIMABLE from this "
          "snapshot — community collection ages are not among its columns.")

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump({"seed": SEED, "n_boot": N_BOOT,
                   "identifies": "E[T5.compute | T1..T4 = ON, pre-flip writer stamps]",
                   "t3_reddit_rows": reddit_rows,
                   "rows": rows_out}, fh, indent=1)
    print(f"\nrow-level JSON → {args.out}")

    print("\nOUTPUT LANGUAGE (mandatory, ruling 1c): this run identifies the "
          "COMPUTE-side of exactly ONE treatment,\nconditionally — "
          "E[T5 | T1..T4 = ON] on pre-flip writer stamps. T1–T4 main effects "
          "are permanently\nunidentified BY DESIGN (rank-1), not by data loss. "
          "This is preservation arithmetic, not an untangling.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
