"""
================================================================
NOW TRENDIN — SIGNAL CONVERGENCE (downstream direction validator)
================================================================

WHAT IT IS
  A read-only validation layer that sits DOWNSTREAM of the Gradient Score.
  It never feeds or alters the score. It reads the score's recent trajectory
  and the raw collected volume, and asks one honest question:

      Is the Gradient Score's direction actually backed by the underlying data?

  When the score is rising AND the raw signal volume is rising → CONFIRMED.
  When the score rises but raw volume is flat/falling → CONFLICTING — a move the
  data does not support, exactly the kind of signal you'd want doubted.

WHY THIS IS SAFE (the architecture point)
  The contamination risk we guard against is internal/derived signals flowing
  UPSTREAM into the Gradient Score. This flows the other way: it consumes the
  gradient + raw data and emits a SEPARATE verdict. The N component
  (nowtrendin_score, query demand) is NOT used here — convergence is validated
  against signals that are INDEPENDENT of N, so the check is non-circular.

TWO VALIDATION TARGETS (what the app shows)
  1. vs the GRADIENT SCORE — does raw volume confirm the score's direction?
  2. vs NICHE ANALYSIS    — is the current niche-concentration (G) consistent
                            with that direction? (rising + still-niche = genuine
                            early spread; rising + already-mainstream = late.)

DATA (live, honest about granularity)
  Reads `pull_history` — DAILY per-topic snapshots of detection_score +
  total_signals + signal_stage. Needs >= 3 daily snapshots to produce a verdict;
  below that it returns status='warming_up'. Current niche concentration (G) is
  read from velocity_scores. Coarser than the per-cycle demo, but built only on
  data we actually persist.
================================================================
"""
import os
import statistics
from datetime import datetime, timezone

try:
    import db_compat
except Exception:
    db_compat = None

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
MIN_SNAPSHOTS = 3
LOOKBACK_SNAPSHOTS = 7


def _linregress_slope(ys: list) -> float:
    n = len(ys)
    if n < 2:
        return 0.0
    xs = list(range(n))
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den = sum((xs[i] - mx) ** 2 for i in range(n))
    return (num / den) if den else 0.0


def _fetch_history(topic_key: str, conn):
    """Recent daily pull_history snapshots for a topic (attention feed),
    oldest-first. Returns list of {detection, volume, stage}."""
    rows = conn.execute(
        "SELECT detection_score, total_signals, signal_stage, snapshot_date "
        "FROM pull_history WHERE topic_key = ? AND feed = 'attention' "
        "ORDER BY snapshot_date DESC LIMIT ?",
        (topic_key, LOOKBACK_SNAPSHOTS),
    ).fetchall()
    out = []
    for r in reversed(rows):  # back to oldest-first
        d = dict(r) if hasattr(r, "keys") else {
            "detection_score": r[0], "total_signals": r[1],
            "signal_stage": r[2], "snapshot_date": r[3],
        }
        out.append({
            "detection": float(d.get("detection_score") or 0),
            "volume": float(d.get("total_signals") or 0),
            "stage": d.get("signal_stage") or "",
        })
    return out


def _current_niche_g(topic_key: str, conn):
    """Current gradient_strength (G, niche concentration 0-100) for the topic."""
    try:
        row = conn.execute(
            "SELECT gradient_strength FROM velocity_scores WHERE topic_key = ?",
            (topic_key,),
        ).fetchone()
        if row:
            g = (row["gradient_strength"] if hasattr(row, "keys") else row[0])
            return float(g) if g is not None else None
    except Exception:
        pass
    return None


def compute_convergence(topic_key: str, db_path: str = DB_PATH, conn=None) -> dict:
    """Validate the Gradient Score's direction against raw volume + niche context.
    Returns the convergence verdict for one topic. Never alters the score."""
    own = False
    if conn is None:
        if db_compat is None:
            return {"status": "unavailable"}
        conn = db_compat.connect(db_path)
        own = True
    try:
        hist = _fetch_history(topic_key, conn)
        g_now = _current_niche_g(topic_key, conn)
    finally:
        if own:
            try: conn.close()
            except Exception: pass

    if len(hist) < MIN_SNAPSHOTS:
        return {"status": "warming_up", "snapshots": len(hist),
                "needed": MIN_SNAPSHOTS,
                "note": "Convergence needs a few daily snapshots before it can "
                        "validate direction. Check back as history accumulates."}

    det = [h["detection"] for h in hist]
    vol = [h["volume"] for h in hist]

    # Direction of the GRADIENT SCORE (slope of detection over snapshots).
    score_slope = _linregress_slope(det)
    score_dir = 1 if score_slope > 0.8 else (-1 if score_slope < -0.8 else 0)

    # Direction of RAW VOLUME (pct change earlier-half vs recent-half).
    mid = len(vol) // 2
    earlier = statistics.mean(vol[:mid]) if mid else vol[0]
    recent = statistics.mean(vol[mid:]) if (len(vol) - mid) else vol[-1]
    if earlier <= 0:
        vol_pct = 1.0 if recent > 0 else 0.0
    else:
        vol_pct = (recent - earlier) / earlier
    vol_dir = 1 if vol_pct > 0.08 else (-1 if vol_pct < -0.08 else 0)

    # ── Validation 1: does raw volume confirm the gradient's direction? ──
    if score_dir == 0:
        gradient_validation = "STABLE"
        gradient_text = "The Gradient Score is roughly flat — no strong direction to validate."
    elif score_dir == vol_dir:
        gradient_validation = "CONFIRMED"
        gradient_text = ("The score is " + ("rising" if score_dir > 0 else "falling") +
                         " and the underlying signal volume agrees — the direction is "
                         "backed by the raw data.")
    elif vol_dir == 0:
        gradient_validation = "MIXED"
        gradient_text = ("The score is " + ("rising" if score_dir > 0 else "falling") +
                         " but raw volume is flat — direction is only partly supported.")
    else:
        gradient_validation = "CONFLICTING"
        gradient_text = ("The score is " + ("rising" if score_dir > 0 else "falling") +
                         " but raw signal volume is moving the OPPOSITE way — the move is "
                         "NOT validated by the underlying data. Treat with caution.")

    # ── Validation 2: is niche concentration consistent with the direction? ──
    # High G = still niche/expert (early). Low G = already mainstream (late).
    if g_now is None:
        niche_validation = "UNKNOWN"
        niche_text = "Niche concentration unavailable for this topic."
    elif score_dir > 0 and g_now >= 55:
        niche_validation = "CONFIRMED"
        niche_text = ("Rising while still concentrated in niche/expert communities "
                      f"(G={round(g_now)}) — consistent with a genuine early spread.")
    elif score_dir > 0 and g_now < 40:
        niche_validation = "CONFLICTING"
        niche_text = ("Rising but already mainstream "
                      f"(G={round(g_now)}) — the easy early diffusion has likely "
                      "happened; a late-stage rise.")
    elif score_dir < 0 and g_now < 40:
        niche_validation = "CONFIRMED"
        niche_text = ("Falling and already mainstream "
                      f"(G={round(g_now)}) — consistent with a topic past its peak.")
    else:
        niche_validation = "MIXED"
        niche_text = (f"Niche concentration (G={round(g_now)}) is only partly "
                      "consistent with the current direction.")

    # ── Overall convergence: agreement across the two validations ──
    votes = [gradient_validation, niche_validation]
    confirmed = votes.count("CONFIRMED")
    conflicting = votes.count("CONFLICTING")
    if conflicting >= 1 and confirmed == 0:
        overall = "CONFLICTING"
    elif confirmed == 2:
        overall = "CONFIRMED"
    elif confirmed >= 1 and conflicting == 0:
        overall = "MIXED"
    elif conflicting >= 1:
        overall = "MIXED"
    else:
        overall = "INCONCLUSIVE"

    direction = ("RISING" if score_dir > 0 else
                 "FALLING" if score_dir < 0 else "HOLDING")

    return {
        "status": "ok",
        "topic_key": topic_key,
        "direction": direction,
        "convergence": overall,            # CONFIRMED / MIXED / CONFLICTING / INCONCLUSIVE
        "snapshots": len(hist),
        "vs_gradient": {
            "validation": gradient_validation,
            "text": gradient_text,
            "score_slope": round(score_slope, 2),
            "volume_change_pct": round(vol_pct * 100, 1),
        },
        "vs_niche": {
            "validation": niche_validation,
            "text": niche_text,
            "niche_g": round(g_now, 1) if g_now is not None else None,
        },
        "note": "Downstream validation — reads the Gradient Score + raw volume; "
                "never feeds or alters the score. Independent of the N demand metric.",
    }
