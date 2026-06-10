"""
================================================================
NOW TRENDIN — MOMENTUM ENGINE
Honest Inertia, Persistence, and Conditional Signal Read
================================================================

THE BUG THIS FIXES:
  The "software development" card showed four contradictions that all
  trace to ONE root cause — the momentum logic was NOT reading the
  scoring-history table that the engine was already populating:

    1. "First collection cycle" message — FALSE. History had 12 cycles.
    2. Persistence 0/0 — WRONG. Score held at 60 for 8+ straight cycles.
    3. Inertia 100/100 — WRONG. The score was FLAT, not accelerating.
    4. Inertia/Persistence INVERTED — flat-but-sustained should read
       LOW inertia + HIGH persistence; the card showed the opposite.

  The scoring history was stored correctly (12 rows). The momentum
  computation just wasn't reading it — it treated every scoring run
  as if it were the first.

WHAT THIS MODULE DOES:
  - Reads the existing scoring-history table
  - Computes INERTIA honestly = directional acceleration (is the score
    actually climbing across recent cycles?). Flat → low. Rising → high.
  - Computes PERSISTENCE honestly = sustained elevation (has the score
    held at an elevated level across consecutive cycles?).
  - Counts real cycles and makes the Signal Read message CONDITIONAL:
    "first collection cycle" fires ONLY when there is genuinely 1 cycle.
  - Produces a corrected Signal Momentum section payload.

DEFINITIONS (aligned to your Law 2 — "Attention has inertia"):
  INERTIA     = momentum/acceleration. A score climbing across windows.
                Measures whether the trend is GAINING.
  PERSISTENCE = staying power. A score holding elevated across cycles.
                Measures whether the trend is LASTING.
  A signal can be high on one and low on the other — they are different
  questions. Flat-but-elevated = low inertia, high persistence.

INTEGRATION:
  Point SCORING_HISTORY_TABLE / column names at your actual table.
  In the scorer, replace the old inertia/persistence computation with:
      from momentum_engine import apply_momentum
      result = apply_momentum(result, topic_key, db_path=DB_PATH)
================================================================
"""

import os
import sqlite3
import statistics
from datetime import datetime, timezone
from typing import Optional

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

# Point these at your actual scoring-history table + columns.
# Based on your screenshots the history stores: scored_at, DET, CONF.
SCORING_HISTORY_TABLE = os.getenv("SCORING_HISTORY_TABLE", "unified_scores")
COL_TOPIC   = "topic_key"
COL_DET     = "detection_score"
COL_CONF    = "confidence_score"
COL_SCORED  = "scored_at"

# Signal stages (your existing bands)
def stage_label(score: float) -> str:
    if score >= 85: return "BREAKOUT"
    if score >= 70: return "STRONG"
    if score >= 55: return "EMERGING"
    if score >= 35: return "WATCHING"
    return "MONITORING"

ELEVATION_THRESHOLD = 50   # "meaningfully elevated" for persistence counting
MIN_CYCLES_FOR_MOMENTUM = 4  # below this, momentum is still stabilising


# ════════════════════════════════════════════════════════════════
# SECTION 1: READ THE SCORING HISTORY (the table already populated)
# ════════════════════════════════════════════════════════════════

def read_scoring_history(topic_key: str, limit: int = 24,
                        db_path: str = DB_PATH) -> list[dict]:
    """
    Read the stored scoring history for a topic, oldest-first.

    Returns [{scored_at, detection, confidence}, ...] in chronological order.
    This is the table the engine was already writing to — the momentum
    logic simply needs to READ it.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(f"""
            SELECT {COL_SCORED} AS scored_at,
                   {COL_DET}    AS detection,
                   {COL_CONF}   AS confidence
            FROM {SCORING_HISTORY_TABLE}
            WHERE {COL_TOPIC} = ?
            ORDER BY {COL_SCORED} ASC
            LIMIT ?
        """, (topic_key, limit)).fetchall()
    except sqlite3.OperationalError as e:
        print(f"  momentum: could not read history ({e})")
        rows = []
    conn.close()

    return [{
        "scored_at":  r["scored_at"],
        "detection":  r["detection"] or 0,
        "confidence": r["confidence"] or 0,
    } for r in rows]


# ════════════════════════════════════════════════════════════════
# SECTION 2: INERTIA — honest directional acceleration
# Flat signal → LOW. Climbing signal → HIGH. Falling → near zero.
# ════════════════════════════════════════════════════════════════

def compute_inertia(history: list[dict], use: str = "detection") -> dict:
    """
    Inertia = sustained directional momentum (is the score CLIMBING?).

    Method: linear-regression slope of the recent window, scaled to 0-100,
    weighted by how consistent (monotonic) the movement is. A flat trace
    yields near-zero slope → low inertia. A steady climb yields high inertia.
    """
    scores = [h[use] for h in history]
    n = len(scores)

    if n < 2:
        return {"inertia": 0, "slope_per_cycle": 0.0, "basis": "insufficient_history"}

    # Use the recent window (last up to 6 cycles) for current momentum
    window = scores[-min(6, n):]
    w = len(window)

    # Linear regression slope (points per cycle)
    xs = list(range(w))
    mean_x = statistics.mean(xs)
    mean_y = statistics.mean(window)
    num = sum((xs[i] - mean_x) * (window[i] - mean_y) for i in range(w))
    den = sum((xs[i] - mean_x) ** 2 for i in range(w))
    slope = (num / den) if den else 0.0

    # Consistency: fraction of step-to-step moves in the slope's direction
    if w >= 3 and slope != 0:
        steps = [window[i+1] - window[i] for i in range(w - 1)]
        same_dir = sum(1 for s in steps if (s > 0) == (slope > 0) and s != 0)
        consistency = same_dir / max(1, len(steps))
    else:
        consistency = 0.0

    # Map slope → inertia. Only POSITIVE slope builds inertia.
    # ~0 pts/cycle → ~10; +1 → ~35; +3 → ~65; +5 → ~85; +7+ → ~100
    if slope <= 0:
        inertia = max(0, 10 + slope * 4)   # falling pushes toward 0
    else:
        inertia = min(100, 10 + slope * 13)
        inertia = inertia * (0.5 + 0.5 * consistency)   # reward consistency

    return {
        "inertia":         round(max(0, min(100, inertia)), 1),
        "slope_per_cycle": round(slope, 2),
        "consistency":     round(consistency, 2),
        "basis":           f"{w}-cycle window",
    }


# ════════════════════════════════════════════════════════════════
# SECTION 3: PERSISTENCE — honest sustained elevation
# Held elevated across many cycles → HIGH. One-off spike → LOW.
# ════════════════════════════════════════════════════════════════

def compute_persistence(history: list[dict], use: str = "detection",
                       threshold: float = ELEVATION_THRESHOLD) -> dict:
    """
    Persistence = staying power (has the score HELD at an elevated level
    across consecutive cycles?).

    Method: count the run of consecutive most-recent cycles at or above
    the elevation threshold, then scale. This is the metric that should
    be HIGH for a flat-but-elevated signal like 'software development.'
    """
    scores = [h[use] for h in history]
    n = len(scores)
    if n < 2:
        return {"persistence": 0, "consecutive_cycles": 0, "basis": "insufficient_history"}

    # Count consecutive most-recent cycles >= threshold
    consecutive = 0
    for s in reversed(scores):
        if s >= threshold:
            consecutive += 1
        else:
            break

    # Map consecutive elevated cycles → persistence
    #   0-1 → 0-15 ; 2-3 → 15-45 ; 4-6 → 45-75 ; 7+ → 75-100
    if consecutive <= 1:
        persistence = consecutive * 15
    elif consecutive <= 3:
        persistence = 15 + (consecutive - 1) * 15
    elif consecutive <= 6:
        persistence = 45 + (consecutive - 3) * 10
    else:
        persistence = min(100, 75 + (consecutive - 6) * 4)

    # Stability bonus: low variance across the elevated run = steadier
    if consecutive >= 3:
        recent = scores[-consecutive:]
        mean_r = statistics.mean(recent)
        if mean_r > 0:
            cv = statistics.stdev(recent) / mean_r
            if cv < 0.08:
                persistence = min(100, persistence + 8)

    return {
        "persistence":        round(max(0, min(100, persistence)), 1),
        "consecutive_cycles": consecutive,
        "basis":              f"{n} cycles, threshold {threshold}",
    }


# ════════════════════════════════════════════════════════════════
# SECTION 4: CONDITIONAL SIGNAL READ
# "First collection cycle" fires ONLY when there is genuinely 1 cycle.
# ════════════════════════════════════════════════════════════════

def generate_signal_read(history: list[dict], inertia: dict,
                        persistence: dict, use: str = "detection") -> dict:
    """
    Produce an honest Signal Read message based on the REAL cycle count
    and the computed momentum — not a hardcoded 'first cycle' template.
    """
    n = len(history)
    cur = history[-1][use] if history else 0
    lvl = stage_label(cur)

    if n <= 1:
        return {
            "headline": "First collection cycle",
            "body": ("Engine is in its first scoring cycle for this topic. "
                     "Scores will sharpen after more cycles. Inertia and "
                     "persistence need 2+ consecutive windows to confirm."),
            "cycle_count": n,
        }

    if n < MIN_CYCLES_FOR_MOMENTUM:
        return {
            "headline": f"Early cycles ({n} runs)",
            "body": (f"{n} scoring runs so far. Momentum is still stabilising — "
                     f"inertia and persistence become reliable after "
                     f"{MIN_CYCLES_FOR_MOMENTUM}+ cycles."),
            "cycle_count": n,
        }

    iner = inertia["inertia"]
    pers = persistence["persistence"]
    slope = inertia.get("slope_per_cycle", 0)
    consec = persistence.get("consecutive_cycles", 0)

    # 4+ cycles — give the real read
    if iner >= 60:
        headline = "Accelerating"
        body = (f"Detection has climbed about {slope:+.1f} pts/cycle across recent "
                f"windows ({n} cycles total). Genuine upward momentum — the trend "
                f"is gaining, not just holding.")
    elif pers >= 60 and iner < 40:
        headline = "Sustained signal"
        body = (f"Held at the {lvl} level for {consec} consecutive cycles "
                f"({n} total). This is a stable, persistent signal — lasting, "
                f"but not currently accelerating.")
    elif slope < -1:
        headline = "Cooling"
        body = (f"Detection is declining about {slope:+.1f} pts/cycle from its recent "
                f"level across {n} cycles. Momentum is fading.")
    else:
        headline = "Holding"
        body = (f"{n} cycles of data. The signal is steady at the {lvl} level with "
                f"mixed momentum — neither clearly accelerating nor fading.")

    return {"headline": headline, "body": body, "cycle_count": n}


# ════════════════════════════════════════════════════════════════
# SECTION 5: DROP-IN APPLY
# ════════════════════════════════════════════════════════════════

def apply_momentum(result: dict, topic_key: str,
                  use: str = "detection", db_path: str = DB_PATH) -> dict:
    """
    Drop-in: replace the broken inertia/persistence/signal-read with
    honest values computed from the stored scoring history.

        result = apply_momentum(result, topic_key, db_path=DB_PATH)

    Overwrites: inertia_score, persistence_score, signal_read, cycle_count.
    Leaves everything else untouched.
    """
    history = read_scoring_history(topic_key, db_path=db_path)

    inertia     = compute_inertia(history, use=use)
    persistence = compute_persistence(history, use=use)
    signal_read = generate_signal_read(history, inertia, persistence, use=use)

    result["inertia_score"]     = inertia["inertia"]
    result["persistence_score"] = persistence["persistence"]
    result["cycle_count"]       = len(history)
    result["signal_read"]       = signal_read
    result["momentum_detail"]   = {
        "inertia":     inertia,
        "persistence": persistence,
        "is_first_cycle": len(history) <= 1,
    }
    return result


# ════════════════════════════════════════════════════════════════
# SECTION 6: DEMO — uses the EXACT history from your screenshot
# ════════════════════════════════════════════════════════════════

def run_demo():
    print("\n" + "="*68)
    print("NOW TRENDIN — MOMENTUM ENGINE — DEMO")
    print("(using the exact 12-cycle history from the screenshot)")
    print("="*68)

    # The actual "software development" history, chronological (oldest first)
    # From Image 9: 6:01→58, 6:31→58, 7:01→61, 7:31→55, then flat at 60
    sw_dev = [
        {"scored_at": "2026-06-07T06:01", "detection": 58, "confidence": 60},
        {"scored_at": "2026-06-07T06:31", "detection": 58, "confidence": 60},
        {"scored_at": "2026-06-07T07:01", "detection": 61, "confidence": 61},
        {"scored_at": "2026-06-07T07:31", "detection": 55, "confidence": 54},
        {"scored_at": "2026-06-07T08:10", "detection": 60, "confidence": 61},
        {"scored_at": "2026-06-07T08:41", "detection": 60, "confidence": 61},
        {"scored_at": "2026-06-07T09:11", "detection": 60, "confidence": 61},
        {"scored_at": "2026-06-07T09:41", "detection": 60, "confidence": 61},
        {"scored_at": "2026-06-07T10:11", "detection": 60, "confidence": 61},
        {"scored_at": "2026-06-07T10:29", "detection": 60, "confidence": 61},
        {"scored_at": "2026-06-07T10:40", "detection": 60, "confidence": 61},
        {"scored_at": "2026-06-07T11:38", "detection": 60, "confidence": 61},
    ]

    inertia     = compute_inertia(sw_dev)
    persistence = compute_persistence(sw_dev)
    signal_read = generate_signal_read(sw_dev, inertia, persistence)

    print(f"\nCycles in history: {len(sw_dev)}")
    print(f"\n  BEFORE (what the app showed):")
    print(f"    Inertia:     100/100   ← WRONG (score is flat, not accelerating)")
    print(f"    Persistence: 0/0       ← WRONG (held at 60 for 8+ cycles)")
    print(f"    Signal Read: 'First collection cycle'  ← WRONG (12 cycles exist)")

    print(f"\n  AFTER (honest, computed from history):")
    print(f"    Inertia:     {inertia['inertia']}/100   "
          f"(slope {inertia['slope_per_cycle']:+.2f} pts/cycle — flat, so low)")
    print(f"    Persistence: {persistence['persistence']}/100   "
          f"({persistence['consecutive_cycles']} consecutive elevated cycles — high)")
    print(f"    Signal Read: '{signal_read['headline']}'")
    print(f"      {signal_read['body']}")

    print("\n" + "-"*68)
    print("CONTRAST — a genuinely accelerating signal:")
    rising = [{"scored_at": f"t{i}", "detection": d, "confidence": d}
              for i, d in enumerate([32, 38, 45, 53, 62, 71])]
    ri = compute_inertia(rising)
    rp = compute_persistence(rising)
    rr = generate_signal_read(rising, ri, rp)
    print(f"  Scores: 32→38→45→53→62→71 (climbing)")
    print(f"    Inertia:     {ri['inertia']}/100   (slope {ri['slope_per_cycle']:+.2f} — rising, so HIGH)")
    print(f"    Persistence: {rp['persistence']}/100")
    print(f"    Signal Read: '{rr['headline']}' — {rr['body'][:60]}...")

    print("\n" + "="*68)
    print("RESULT: flat-but-sustained → LOW inertia + HIGH persistence,")
    print("honest 'Sustained signal' read. Climbing → HIGH inertia,")
    print("'Accelerating' read. The inversion is fixed and the false")
    print("'first collection cycle' message is gone.")
    print("="*68)


if __name__ == "__main__":
    run_demo()
