"""
================================================================
NOW TRENDIN — "NOW TRENDING" DIRECTION ENGINE
Downstream Validation of Trend Direction Through Convergence
================================================================

WHAT IT IS:
  A synthesis layer that sits DOWNSTREAM of the Gradient Score. It
  reads (never feeds) the Gradient Score and the raw collected data,
  and validates which way a trend is actually moving by checking
  whether multiple independent signals AGREE.

WHY THIS IS THE SAFE ARCHITECTURE:
  The contamination risk we guarded against was internal/derived
  signals flowing UPSTREAM into the Gradient Score. This module flows
  the other way — it consumes the gradient and raw data to produce a
  separate directional verdict. The Gradient Score stays objective and
  uncontaminated; "Now Trending" is a read-only consumer of it.

WHAT IT VALIDATES — direction by convergence:
  Four independent directional signals "vote" on where the trend is going:
    1. Score Trajectory   — is the Gradient Score itself rising? (from history)
    2. Volume Velocity     — is the raw signal volume accelerating? (from collectors)
    3. Stage Migration     — is the signal spreading down the diffusion pipeline?
    4. Platform Breadth     — is it appearing on MORE platforms over time?
  When they converge, direction is CONFIRMED. When they conflict, the
  module flags it — a rising score that the raw data does NOT support is
  exactly the kind of false signal you want caught.

  Internal demand (the app's own users) may be passed as an OPTIONAL
  fifth input — used here ONLY to corroborate direction, never to drive
  the Gradient Score. This is the safe, downstream way to use it.

OUTPUT:
  direction:            EMERGING / RISING / HOLDING / PEAKING / FADING
  direction_confidence: 0-100, how strongly the signals agree
  validation:           CONFIRMED / MIXED / CONFLICTING
  factor breakdown + interpretation

INTEGRATION:
  Reads the same scoring-history table as momentum_engine plus the
  collected-signal history. Produces the "Now Trending" panel —
  separate from, and never blended into, the Gradient Score.
================================================================
"""

import statistics
from datetime import datetime, timezone
from typing import Optional


# ════════════════════════════════════════════════════════════════
# Each factor returns a vote in [-1, +1] (rising positive) and a strength.
# ════════════════════════════════════════════════════════════════

def analyze_score_trajectory(score_history: list) -> dict:
    """
    Factor 1: is the GRADIENT SCORE itself rising across recent cycles?
    score_history: [{detection, scored_at}, ...] oldest-first.
    """
    scores = [h.get("detection", 0) for h in score_history]
    if len(scores) < 3:
        return {"vote": 0.0, "strength": 0.2, "label": "insufficient_history"}

    window = scores[-min(6, len(scores)):]
    xs = list(range(len(window)))
    mx, my = statistics.mean(xs), statistics.mean(window)
    num = sum((xs[i]-mx)*(window[i]-my) for i in range(len(window)))
    den = sum((xs[i]-mx)**2 for i in range(len(window)))
    slope = (num/den) if den else 0.0

    vote = max(-1.0, min(1.0, slope / 4.0))   # ~4 pts/cycle saturates
    return {"vote": round(vote, 3), "strength": min(1.0, abs(slope)/4 + 0.3),
            "slope_per_cycle": round(slope, 2), "label": "score_trajectory"}


def analyze_volume_velocity(raw_history: list) -> dict:
    """
    Factor 2: is the RAW signal volume accelerating? (validates the score)
    raw_history: [{volume, ...}, ...] oldest-first, per collection window.
    """
    vols = [r.get("volume", 0) for r in raw_history]
    if len(vols) < 3:
        return {"vote": 0.0, "strength": 0.2, "label": "insufficient_volume"}

    mid = len(vols)//2
    earlier = statistics.mean(vols[:mid]) if mid else 0
    recent  = statistics.mean(vols[mid:]) if (len(vols)-mid) else 0
    if earlier <= 0:
        pct = 1.0 if recent > 0 else 0.0
    else:
        pct = (recent - earlier) / earlier

    vote = max(-1.0, min(1.0, pct))   # +100% → +1, -100% → -1
    return {"vote": round(vote, 3), "strength": min(1.0, abs(pct)+0.3),
            "pct_change": round(pct*100, 1), "label": "volume_velocity"}


def analyze_stage_migration(raw_history: list) -> dict:
    """
    Factor 3: is the signal SPREADING down the diffusion pipeline?
    A center-of-mass moving from early stages toward later stages means
    the trend is diffusing outward (spreading). Contracting = fading.
    raw_history items carry stage_distribution: {1:n, 2:n, ...}.
    Also returns the current center-of-mass so the verdict knows whether
    the trend is early (emerging) or late (mainstream/peaking).
    """
    def com(dist):
        total = sum(dist.values()) if dist else 0
        if not total:
            return None
        return sum(stage*cnt for stage, cnt in dist.items()) / total

    coms = [com(r.get("stage_distribution", {})) for r in raw_history]
    coms = [c for c in coms if c is not None]
    if len(coms) < 2:
        return {"vote": 0.0, "strength": 0.2, "current_com": None,
                "label": "insufficient_stage_data"}

    drift = coms[-1] - coms[0]   # positive = spreading toward mainstream
    vote = max(-1.0, min(1.0, drift / 1.5))
    return {"vote": round(vote, 3), "strength": min(1.0, abs(drift)+0.3),
            "current_com": round(coms[-1], 2), "drift": round(drift, 2),
            "label": "stage_migration"}


def analyze_platform_breadth(raw_history: list) -> dict:
    """
    Factor 4: is the trend appearing on MORE platforms over time?
    raw_history items carry platform_count.
    """
    counts = [r.get("platform_count", 0) for r in raw_history]
    if len(counts) < 2:
        return {"vote": 0.0, "strength": 0.2, "label": "insufficient_breadth"}

    mid = len(counts)//2
    earlier = statistics.mean(counts[:mid]) if mid else counts[0]
    recent  = statistics.mean(counts[mid:]) if (len(counts)-mid) else counts[-1]
    delta = recent - earlier

    vote = max(-1.0, min(1.0, delta / 2.0))   # +2 platforms → +1
    return {"vote": round(vote, 3), "strength": min(1.0, abs(delta)/2 + 0.3),
            "platform_delta": round(delta, 1), "label": "platform_breadth"}


def analyze_internal_corroboration(internal_history: list,
                                  external_vote: float) -> dict:
    """
    OPTIONAL Factor 5: does internal demand AGREE with the external
    direction? Used only to corroborate — never to drive the gradient.
    internal_history: [demand_value, ...] oldest-first.
    """
    if not internal_history or len(internal_history) < 3:
        return {"agrees": None, "label": "no_internal_data"}

    mid = len(internal_history)//2
    earlier = statistics.mean(internal_history[:mid]) if mid else internal_history[0]
    recent  = statistics.mean(internal_history[mid:])
    internal_dir = 1 if recent > earlier*1.05 else (-1 if recent < earlier*0.95 else 0)
    ext_dir = 1 if external_vote > 0.15 else (-1 if external_vote < -0.15 else 0)

    agrees = (internal_dir == ext_dir) and internal_dir != 0
    diverges = (internal_dir != 0 and ext_dir != 0 and internal_dir != ext_dir)
    return {"agrees": agrees, "diverges": diverges,
            "internal_direction": internal_dir, "label": "internal_corroboration"}


# ════════════════════════════════════════════════════════════════
# SYNTHESIS — combine the four external votes into a direction
# ════════════════════════════════════════════════════════════════

FACTOR_WEIGHTS = {"score": 0.35, "volume": 0.30, "stage": 0.20, "breadth": 0.15}


def compute_now_trending(topic: str,
                        score_history: list,
                        raw_history: list,
                        internal_history: Optional[list] = None,
                        current_detection: Optional[float] = None) -> dict:
    """
    Produce the "Now Trending" directional verdict for a topic by
    validating direction across the four independent external signals,
    with optional internal-demand corroboration.
    """
    f_score  = analyze_score_trajectory(score_history)
    f_volume = analyze_volume_velocity(raw_history)
    f_stage  = analyze_stage_migration(raw_history)
    f_breadth= analyze_platform_breadth(raw_history)

    # REFINEMENT: stage migration is ambiguous without volume context.
    # Drift toward later stages with RISING volume = healthy spreading (positive).
    # The same drift with FALLING volume = early-stage activity DYING OFF, leaving
    # only late-stage remnants (negative — the trend is contracting, not spreading).
    # We gate the stage vote's sign by the volume direction so a fading trend's
    # late-stage concentration is not misread as diffusion.
    if f_stage["vote"] > 0 and f_volume["vote"] < -0.15:
        f_stage = {**f_stage,
                   "vote": -abs(f_stage["vote"]),
                   "volume_adjusted": True,
                   "label": "stage_migration(volume_adjusted:late-stage_decay)"}

    votes = {"score": f_score["vote"], "volume": f_volume["vote"],
             "stage": f_stage["vote"], "breadth": f_breadth["vote"]}

    # Weighted net direction
    net = sum(FACTOR_WEIGHTS[k] * votes[k] for k in votes)

    # Convergence: how much do the votes agree? (low spread = high agreement)
    vote_vals = list(votes.values())
    spread = statistics.pstdev(vote_vals) if len(vote_vals) > 1 else 0
    convergence = max(0.0, 1.0 - spread)        # 1 = perfect agreement
    direction_confidence = round(convergence * 100, 1)

    # Internal corroboration (optional, does not change `net`)
    internal = analyze_internal_corroboration(internal_history or [], net)

    # Current diffusion position (early vs mainstream) for the verdict
    com = f_stage.get("current_com")
    is_mainstream = (com is not None and com >= 3.5)
    cur_level = current_detection if current_detection is not None else \
                (score_history[-1].get("detection", 0) if score_history else 0)

    # ── Map net + context → direction label ──────────────────────
    if net >= 0.4:
        if is_mainstream and f_volume["vote"] < 0.25:
            direction = "PEAKING"      # high/late and velocity flattening
        elif cur_level < 45:
            direction = "EMERGING"     # rising from a low base
        else:
            direction = "RISING"
    elif net >= 0.15:
        direction = "EMERGING" if cur_level < 45 else "RISING"
    elif net > -0.2:
        direction = "HOLDING"
    else:
        direction = "FADING"

    # Validation status from convergence
    if convergence >= 0.75:
        validation = "CONFIRMED"
    elif convergence >= 0.5:
        validation = "MIXED"
    else:
        validation = "CONFLICTING"

    interpretation = _interpret(direction, validation, votes,
                                internal, f_volume, f_score)

    return {
        "topic":                topic,
        "direction":            direction,
        "direction_confidence": direction_confidence,
        "validation":           validation,
        "net_direction":        round(net, 3),
        "factors": {
            "score_trajectory": f_score,
            "volume_velocity":  f_volume,
            "stage_migration":  f_stage,
            "platform_breadth": f_breadth,
        },
        "internal_corroboration": internal,
        "interpretation":       interpretation,
        "note": "Downstream directional validation. Reads the Gradient Score "
                "and raw data; does not feed or alter the Gradient Score.",
    }


def _interpret(direction, validation, votes, internal, f_volume, f_score) -> str:
    # REFINEMENT: when validation is not CONFIRMED, the directional sentence must
    # NOT assert that the signals "agree" — that contradicts the conflict warning
    # that follows. We pick a confident base only for CONFIRMED; otherwise the base
    # is hedged so the copy stays internally consistent.
    if validation == "CONFIRMED":
        base = {
            "EMERGING": "Early and rising — signals agree it's gaining from a low base.",
            "RISING":   "Trending upward — the score and the underlying data agree it's gaining.",
            "HOLDING":  "Stable — signals agree it is neither gaining nor fading.",
            "PEAKING":  "High but momentum is flattening at mainstream stages — likely near a peak.",
            "FADING":   "Cooling — the signals agree the trend is losing momentum.",
        }[direction]
    else:
        base = {
            "EMERGING": "Leaning early/rising from a low base, but not all signals confirm it.",
            "RISING":   "Leaning upward, but the signals do not fully agree it's gaining.",
            "HOLDING":  "Roughly stable, with signals sending mixed direction reads.",
            "PEAKING":  "Possibly near a peak — momentum reads are mixed at mainstream stages.",
            "FADING":   "Leaning toward cooling, but the signals are not unanimous.",
        }[direction]

    if validation == "CONFLICTING":
        # Identify the disagreement
        if f_score["vote"] > 0.2 and f_volume["vote"] < -0.1:
            base += (" ⚠ CONFLICT: the score is rising but the raw collected volume "
                     "is NOT — the score direction is not validated by the underlying "
                     "data. Treat the rise with caution.")
        else:
            base += (" ⚠ CONFLICT: the directional signals disagree — direction is "
                     "not validated. Investigate before trusting the move.")
    elif validation == "MIXED":
        base += " Some signals lag the others — direction is probable but not fully confirmed."

    if internal.get("diverges"):
        base += (" Internal app demand is moving the OPPOSITE way from external attention "
                 "— a divergence worth noting (your users vs the world).")
    elif internal.get("agrees"):
        base += " Internal app demand corroborates the external direction."

    return base


# ════════════════════════════════════════════════════════════════
# DEMO — convergent rise, conflicting case, peaking, fading
# ════════════════════════════════════════════════════════════════

def run_demo():
    print("\n" + "="*70)
    print("NOW TRENDIN — 'NOW TRENDING' DIRECTION ENGINE — DEMO")
    print("="*70)

    def hist(scores):
        return [{"detection": s, "scored_at": f"t{i}"} for i, s in enumerate(scores)]

    def raw(vols, plats, stage_dists):
        return [{"volume": v, "platform_count": p, "stage_distribution": d}
                for v, p, d in zip(vols, plats, stage_dists)]

    # 1. CONVERGENT RISE — score up, volume up, spreading, more platforms
    print("\n── 1. Convergent rising trend ──")
    r = compute_now_trending(
        "agentic coding",
        score_history=hist([40, 45, 52, 58, 64, 70]),
        raw_history=raw([100,140,190,260,340,430], [2,2,3,3,4,5],
                        [{1:8,2:2},{1:9,2:4},{1:8,2:6,3:2},{1:7,2:7,3:4},
                         {2:6,3:7,4:3},{2:5,3:8,4:5}]),
        internal_history=[20,28,35,44,55,68],
    )
    _show(r)

    # 2. CONFLICTING — score rising but raw volume flat/falling
    print("\n── 2. Score rising but raw data does NOT confirm ──")
    r = compute_now_trending(
        "suspicious topic",
        score_history=hist([40, 48, 55, 62, 68, 73]),
        raw_history=raw([200,190,185,180,175,170], [3,3,3,2,2,2],
                        [{1:5,2:3}]*6),
    )
    _show(r)

    # 3. PEAKING — high, mainstream stages, velocity flattening
    print("\n── 3. Peaking (mainstream, momentum flattening) ──")
    r = compute_now_trending(
        "mainstream topic",
        score_history=hist([78, 80, 81, 81, 82, 82]),
        raw_history=raw([900,905,910,908,912,915], [6,6,6,6,6,6],
                        [{4:8,5:6},{4:7,5:7},{4:6,5:8},{4:6,5:8},{4:5,5:9},{4:5,5:9}]),
    )
    _show(r)

    # 4. FADING — everything declining
    print("\n── 4. Fading trend ──")
    r = compute_now_trending(
        "cooling topic",
        score_history=hist([70, 64, 57, 50, 44, 38]),
        raw_history=raw([400,330,270,210,160,120], [5,4,4,3,3,2],
                        [{3:6,4:5},{3:5,4:4},{4:5,5:3},{4:4,5:3},{5:4},{5:3}]),
    )
    _show(r)

    print("\n" + "="*70)
    print("The engine confirms direction when signals converge, and FLAGS the")
    print("case where the score rises but the raw data doesn't back it up —")
    print("catching exactly the kind of unvalidated move you'd want to doubt.")
    print("It reads the gradient and raw data; it never feeds the gradient.")
    print("="*70)


def _show(r):
    print(f"  Direction: {r['direction']}   "
          f"Confidence: {r['direction_confidence']}%   "
          f"Validation: {r['validation']}")
    f = r["factors"]
    print(f"  Votes: score={f['score_trajectory']['vote']:+.2f} "
          f"volume={f['volume_velocity']['vote']:+.2f} "
          f"stage={f['stage_migration']['vote']:+.2f} "
          f"breadth={f['platform_breadth']['vote']:+.2f}")
    print(f"  → {r['interpretation']}")


if __name__ == "__main__":
    run_demo()
