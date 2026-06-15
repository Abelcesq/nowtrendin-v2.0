"""
NOW TRENDIN — MOMENTUM ENGINE (engine-native, db_compat)

Single source of truth for INERTIA, PERSISTENCE, cycle count, and the
Signal Read message — all computed from the scoring history the engine
already stores in velocity_scores.

Why this exists: the old logic used two disagreeing cycle counters
(topic_lifecycle.total_scoring_cycles and calibration's times_scored) and an
inertia calc that read 100 on a flat trace. On "software development" that
produced four contradictions at once — a false "first collection cycle"
message, persistence 0 (despite 12 held cycles), and inertia 100 (despite a
flat score). Reading the actual stored history fixes all of them:

  INERTIA     = directional acceleration. Flat → low, climbing → high.
  PERSISTENCE = sustained elevation across consecutive cycles.

These are different questions: a flat-but-elevated signal is LOW inertia +
HIGH persistence (it is lasting, not gaining).
"""
import os
import statistics

try:
    import db_compat
except Exception:  # pragma: no cover
    db_compat = None

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

HISTORY_TABLE = "velocity_scores"
COL_TOPIC, COL_DET, COL_CONF, COL_SCORED = (
    "topic_key", "detection_score", "confidence_score", "scored_at")

ELEVATION_THRESHOLD = 50      # "meaningfully elevated" for persistence
MIN_CYCLES_FOR_MOMENTUM = 4   # below this, momentum is still stabilising


def stage_label(score: float) -> str:
    if score >= 85: return "BREAKOUT"
    if score >= 70: return "STRONG"
    if score >= 55: return "EMERGING"
    if score >= 35: return "WATCHING"
    return "MONITORING"


def read_scoring_history(topic_key: str, limit: int = 24, db_path: str = DB_PATH,
                         conn=None) -> list:
    """Stored scoring history for a topic, oldest-first, from velocity_scores."""
    own = False
    if conn is None:
        if db_compat is None:
            return []
        conn = db_compat.connect(db_path)
        own = True
    try:
        rows = conn.execute(
            f"SELECT {COL_SCORED} AS scored_at, {COL_DET} AS detection, "
            f"{COL_CONF} AS confidence, signal_stage AS signal_stage FROM {HISTORY_TABLE} "
            f"WHERE {COL_TOPIC} = ? ORDER BY {COL_SCORED} ASC LIMIT ?",
            (topic_key, limit)).fetchall()
    except Exception as e:
        print(f"  momentum: could not read history ({e})")
        rows = []
    finally:
        if own:
            conn.close()
    return [{"scored_at": r["scored_at"], "detection": r["detection"] or 0,
             "confidence": r["confidence"] or 0,
             "signal_stage": (r["signal_stage"] or "").upper()} for r in rows]


# Stages that count as "meaningfully elevated" for persistence. Stage is
# scale-independent (matches what the UI shows) — unlike the RAW detection
# score stored in velocity_scores, which calibration rescales upward at serve.
ELEVATED_STAGES = {"EMERGING", "STRONG", "BREAKOUT"}


def compute_inertia(history: list, use: str = "detection") -> dict:
    """Inertia = directional acceleration (is the score CLIMBING?)."""
    scores = [h[use] for h in history]
    n = len(scores)
    if n < 2:
        return {"inertia": 0.0, "slope_per_cycle": 0.0, "basis": "insufficient_history"}
    window = scores[-min(6, n):]
    w = len(window)
    xs = list(range(w))
    mean_x = statistics.mean(xs)
    mean_y = statistics.mean(window)
    num = sum((xs[i] - mean_x) * (window[i] - mean_y) for i in range(w))
    den = sum((xs[i] - mean_x) ** 2 for i in range(w))
    slope = (num / den) if den else 0.0
    if w >= 3 and slope != 0:
        steps = [window[i + 1] - window[i] for i in range(w - 1)]
        same_dir = sum(1 for s in steps if (s > 0) == (slope > 0) and s != 0)
        consistency = same_dir / max(1, len(steps))
    else:
        consistency = 0.0
    if slope <= 0:
        inertia = max(0.0, 10 + slope * 4)
    else:
        inertia = min(100.0, 10 + slope * 13) * (0.5 + 0.5 * consistency)
    return {"inertia": round(max(0.0, min(100.0, inertia)), 1),
            "slope_per_cycle": round(slope, 2),
            "consistency": round(consistency, 2),
            "basis": f"{w}-cycle window"}


def compute_persistence(history: list, use: str = "detection",
                        threshold: float = ELEVATION_THRESHOLD) -> dict:
    """Persistence = sustained elevation across consecutive cycles."""
    scores = [h[use] for h in history]
    n = len(scores)
    if n < 2:
        return {"persistence": 0.0, "consecutive_cycles": 0, "basis": "insufficient_history"}
    # Persistence is measured RELATIVE to the topic's own peak, which is
    # scale-independent: the stored scores are RAW (pre-calibration), so an
    # absolute threshold or the stored stage (also raw) understates a topic that
    # is genuinely held. "Held" = the recent score has not collapsed from its
    # peak. A flat trace stays near its peak → high; a faded spike drops → low.
    peak = max(scores) if scores else 0
    floor = max(15.0, 0.6 * peak)
    consecutive = 0
    for s in reversed(scores):
        if s >= floor:
            consecutive += 1
        else:
            break
    basis_note = f"held>=60% of peak({round(peak)})"
    if consecutive <= 1:
        persistence = consecutive * 15
    elif consecutive <= 3:
        persistence = 15 + (consecutive - 1) * 15
    elif consecutive <= 6:
        persistence = 45 + (consecutive - 3) * 10
    else:
        persistence = min(100, 75 + (consecutive - 6) * 4)
    if consecutive >= 3:
        recent = scores[-consecutive:]
        mean_r = statistics.mean(recent)
        if mean_r > 0 and statistics.stdev(recent) / mean_r < 0.08:
            persistence = min(100, persistence + 8)
    return {"persistence": round(max(0.0, min(100.0, persistence)), 1),
            "consecutive_cycles": consecutive,
            "basis": f"{n} cycles, by {basis_note}"}


def generate_signal_read(history: list, inertia: dict, persistence: dict,
                         use: str = "detection") -> dict:
    """Honest Signal Read based on the REAL cycle count + computed momentum."""
    n = len(history)
    cur = history[-1][use] if history else 0
    # Prefer the stored stage (matches the displayed score) over a raw-score label.
    lvl = (history[-1].get("signal_stage") if history and history[-1].get("signal_stage")
           else stage_label(cur))
    if n <= 1:
        return {"headline": "First collection cycle", "cycle_count": n,
                "body": ("Engine is in its first scoring cycle for this topic. "
                         "Scores will sharpen after more cycles.")}
    if n < MIN_CYCLES_FOR_MOMENTUM:
        return {"headline": f"Early cycles ({n} runs)", "cycle_count": n,
                "body": (f"{n} scoring runs so far. Momentum is still stabilising — "
                         f"inertia and persistence become reliable after "
                         f"{MIN_CYCLES_FOR_MOMENTUM}+ cycles.")}
    iner = inertia["inertia"]
    pers = persistence["persistence"]
    slope = inertia.get("slope_per_cycle", 0)
    consec = persistence.get("consecutive_cycles", 0)
    if iner >= 60:
        headline = "Accelerating"
        body = (f"Detection has climbed about {slope:+.1f} pts/cycle across recent "
                f"windows ({n} cycles). Genuine upward momentum — gaining, not just holding.")
    elif pers >= 60 and iner < 40:
        headline = "Sustained signal"
        body = (f"Held steady for {consec} consecutive cycles ({n} total). "
                f"A stable, persistent signal — lasting, but not currently accelerating.")
    elif slope < -1:
        headline = "Cooling"
        body = (f"Score is declining about {slope:+.1f} pts/cycle across {n} cycles. "
                f"Momentum is fading.")
    else:
        headline = "Holding"
        body = (f"{n} cycles of data. Steady with mixed momentum — "
                f"neither clearly accelerating nor fading.")
    return {"headline": headline, "body": body, "cycle_count": n}


def momentum_for(topic_key: str, db_path: str = DB_PATH, conn=None,
                 use: str = "detection") -> dict:
    """Compute the full momentum bundle for a topic from stored history."""
    history = read_scoring_history(topic_key, db_path=db_path, conn=conn)
    inertia = compute_inertia(history, use=use)
    persistence = compute_persistence(history, use=use)
    signal_read = generate_signal_read(history, inertia, persistence, use=use)
    return {"inertia": inertia["inertia"], "persistence": persistence["persistence"],
            "cycle_count": len(history), "signal_read": signal_read,
            "inertia_detail": inertia, "persistence_detail": persistence}
