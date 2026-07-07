"""backtest_d_weights.py — HELD-OUT what-if backtest for Dark-Matter weight shifts.

READ-ONLY research tool (integrity-recs branch, rec A). Never imported by scoring.
Question: given the resolved accuracy-ledger cohort, would shifting D's weight
(Detection ↓ / Confidence ↑ — the "D as confirmation" hypothesis) have SEPARATED
winners from near-miss losers better at detection time?

Method:
  • Cohort: resolved ledger rows — WINNERS (LED + SAME_DAY) vs NEAR-MISS LAGGED
    (lead ≥ −7d; races actually run). PRE-BROKEN rows are excluded (never a race).
  • For each topic, take its FIRST velocity_scores row (detection-time components
    G/I/M/D/C/P) and recompute Detection under each candidate weight vector.
  • Metrics per vector: median winner vs loser Detection, and rank-AUC =
    P(random winner outranks random loser). Higher AUC = better early separation.
Honest caveats printed with results: small n; components from the first STORED row
(may postdate true first sighting for bulk-enrolled topics); rank-AUC on ~7 vs ~15
rows has wide error bars — this GATES a decision, it does not settle it.
"""
import os
import statistics
import sys

import db_compat
from scoring_weights import WEIGHTS_DETECTION, WEIGHTS_CONFIDENCE

DB_PATH = os.getenv("DB_PATH", "anomaly_detector.db")

# Candidate weight vectors (each sums to 1.0; renormalized shifts of the current).
VARIANTS = {
    "current detection": dict(WEIGHTS_DETECTION),
    # D→M shift: D was 0 at first sighting for winners AND losers (2026-07-07 mining);
    # M (breadth) separated winners (median 80 vs 50). Move half of D's weight to M.
    "D->M shift (D .108, M .210)": {"G": 0.375, "D": 0.108, "I": 0.182, "M": 0.210, "C": 0.057, "P": 0.068},
    # D→G shift: same idea, weight to niche concentration instead.
    "D->G shift (D .108, G .483)": {"G": 0.483, "D": 0.108, "I": 0.182, "M": 0.102, "C": 0.057, "P": 0.068},
    # D fully redistributed (extreme bound, NOT a proposal — brackets the effect).
    "no-D bound (D 0)": {"G": 0.425, "D": 0.0, "I": 0.212, "M": 0.182, "C": 0.087, "P": 0.094},
}


def _auc(winners, losers):
    """Rank-AUC: P(winner > loser) + half ties. Small-n; report with caveats."""
    if not winners or not losers:
        return None
    wins = ties = 0
    for w in winners:
        for l in losers:
            if w > l:
                wins += 1
            elif w == l:
                ties += 1
    return round((wins + ties * 0.5) / (len(winners) * len(losers)), 3)


def run(db_path: str = DB_PATH) -> dict:
    conn = db_compat.connect(db_path)
    rows = [dict(r) for r in conn.execute(
        "SELECT topic_key, verdict, lead_time_days FROM accuracy_ledger "
        "WHERE verdict IN ('LED','SAME_DAY','LAGGED')").fetchall()]
    # first stored score per topic (detection-time components)
    comps = {}
    for r in rows:
        tk = r["topic_key"]
        if tk in comps:
            continue
        c = conn.execute(
            "SELECT gradient_strength, inertia_score, platform_diversity, "
            "       dark_matter_score, confidence_decay, persistence_score "
            "FROM velocity_scores WHERE topic_key=? ORDER BY scored_at ASC LIMIT 1",
            (tk,)).fetchone()
        if c:
            d = dict(c)
            comps[tk] = {"G": float(d.get("gradient_strength") or 0.0),
                         "I": float(d.get("inertia_score") or 0.0),
                         "M": float(d.get("platform_diversity") or 0.0),
                         "D": float(d.get("dark_matter_score") or 0.0),
                         "C": float(d.get("confidence_decay") or 0.0),
                         "P": float(d.get("persistence_score") or 0.0)}
    conn.close()

    winners, losers = [], []   # lists of component dicts
    for r in rows:
        c = comps.get(r["topic_key"])
        if not c:
            continue
        if r["verdict"] in ("LED", "SAME_DAY"):
            winners.append(c)
        elif r["verdict"] == "LAGGED" and r["lead_time_days"] is not None \
                and r["lead_time_days"] >= -7:
            losers.append(c)   # near-miss races only; pre-broken excluded

    out = {"n_winners": len(winners), "n_losers": len(losers), "variants": {}}
    for name, w in VARIANTS.items():
        assert abs(sum(w.values()) - 1.0) < 1e-6, name
        dw = [sum(c[k] * w[k] for k in w) for c in winners]
        dl = [sum(c[k] * w[k] for k in w) for c in losers]
        out["variants"][name] = {
            "winner_median": round(statistics.median(dw), 1) if dw else None,
            "loser_median": round(statistics.median(dl), 1) if dl else None,
            "separation": (round(statistics.median(dw) - statistics.median(dl), 1)
                           if dw and dl else None),
            "rank_auc": _auc(dw, dl),
        }
    return out


if __name__ == "__main__":
    res = run()
    print(f"cohort: {res['n_winners']} winners (LED+SAME_DAY) vs "
          f"{res['n_losers']} near-miss LAGGED (pre-broken excluded)")
    for name, v in res["variants"].items():
        print(f"  {name:34s} winner_med {v['winner_median']} | loser_med {v['loser_median']} "
              f"| sep {v['separation']} | AUC {v['rank_auc']}")
    print("\nCAVEATS: small n; components are the first STORED row (may postdate true "
          "first sighting for bulk-enrolled topics); AUC error bars are wide. "
          "This gates a decision; it does not settle it.")
