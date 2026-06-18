"""
================================================================
NOW TRENDIN — SIGNAL CALIBRATION ENGINE v1.0
================================================================

THE CORE PROBLEM THIS FIXES:
  The Gravitational Anomaly Detector scores gradient strength
  using the ABSOLUTE ratio of niche-to-mainstream signals.

  This creates a critical error:
  - "ai agent" has been discussed in expert communities for
    2+ years → it will ALWAYS score high gradient strength
  - A genuinely new topic appearing in expert communities for
    the FIRST TIME also scores high gradient strength
  - The detector cannot tell these apart — both get flagged
    as anomalies, misleading users about what is truly emerging

THE FIX — Three-Layer Calibration:
  1. TOPIC MATURITY TRACKING
     Track every topic's score history. Classify each as:
     NEW / EMERGING / ESTABLISHED / RESURGENT / MONITORING

  2. VELOCITY-ADJUSTED GRADIENT STRENGTH
     Score the RATE OF CHANGE from baseline, not the
     absolute niche concentration. A topic that has always
     had 80% gradient strength gets a LOW gradient score.
     A topic that JUMPED from 20% to 80% gets a HIGH score.

  3. MULTI-SIGNAL ANOMALY GATE
     Anomaly flag now requires maturity-aware evidence:
     - ESTABLISHED topics need RESURGENCE proof before anomaly
     - NEW topics get more lenient anomaly threshold
     - Gradient ratio alone is NEVER sufficient for anomaly

COMMUNICATION FIXES IN THIS FILE:
  4. Lead time estimate hidden when Inertia = 0
  5. "High conviction" gap label corrected to be directional
  6. Inertia = 0 shows process explanation not a zero
  7. Components grouped into Quality / Momentum / Context
  8. What-To-Do section built from maturity + evidence together
  9. Anomaly labels distinguish gradient-only vs confirmed

HOW TO INTEGRATE:
  from calibration_engine import CalibrationEngine, build_calibrated_response

  # After scoring a topic in GravitationalAnomalyDetector:
  cal = CalibrationEngine(db_path)
  calibrated = cal.apply(raw_score_dict, signals)

  # calibrated dict is a drop-in replacement with all fields
  # corrected plus new maturity + communication fields added

RUN STANDALONE:
  python calibration_engine.py --mode=analyse   # analyse all topics
  python calibration_engine.py --mode=reclassify # reclassify all maturity
  python calibration_engine.py --mode=report     # print calibration report
================================================================
"""

import os
import re
import json
import math
import sqlite3
import db_compat
import argparse
import statistics
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Optional

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

# ── Maturity thresholds ───────────────────────────────────────────
DAYS_TO_ESTABLISHED   = 30   # days in system before "established" is possible
MIN_SCORES_ESTABLISHED = 5   # minimum scoring cycles before established
VELOCITY_EMERGING     = 20   # gradient delta to count as emerging
VELOCITY_RESURGENT    = 15   # gradient delta to count as resurgent (for established)
BASELINE_WINDOW_DAYS  = 14   # days used to compute rolling baseline
INERTIA_ZERO_THRESHOLD = 5   # inertia below this = treat as "no inertia confirmed"
GRADIENT_RATIO_THRESHOLD = 4.0  # niche density 4x greater than mainstream = high gradient


# ════════════════════════════════════════════════════════════════
# SECTION 1: DATABASE SCHEMA ADDITIONS
# Run init_calibration_db() once to add the new tables
# ════════════════════════════════════════════════════════════════

CALIBRATION_SCHEMA = """
-- ── TOPIC MATURITY REGISTRY ──────────────────────────────────────
-- Tracks each topic's lifecycle classification
-- Updated every scoring cycle

CREATE TABLE IF NOT EXISTS topic_maturity (
    topic_key              TEXT PRIMARY KEY,
    topic_display          TEXT,

    -- Lifecycle
    first_detected_at      TEXT,
    last_scored_at         TEXT,
    times_scored           INTEGER DEFAULT 0,
    days_in_system         INTEGER DEFAULT 0,

    -- Maturity classification
    -- NEW: < 7 days AND < 5 scoring cycles
    -- EMERGING: accelerating gradient, < 30 days
    -- ESTABLISHED: consistent presence 30+ days, stable gradient
    -- RESURGENT: established topic showing renewed acceleration
    -- MONITORING: present but not trending
    maturity_class         TEXT DEFAULT 'NEW',
    maturity_reason        TEXT,

    -- Baseline metrics (rolling 14-day average)
    baseline_gradient      REAL DEFAULT 0,
    baseline_overall       REAL DEFAULT 0,
    baseline_detection     REAL DEFAULT 0,
    baseline_confidence    REAL DEFAULT 0,

    -- Velocity (current vs baseline)
    gradient_velocity      REAL DEFAULT 0,   -- positive = accelerating
    score_velocity         REAL DEFAULT 0,
    velocity_trend         TEXT DEFAULT 'unknown',  -- rising/falling/stable

    -- Calibrated score adjustments
    calibration_multiplier REAL DEFAULT 1.0,  -- applied to gradient strength
    anomaly_gate_passed    INTEGER DEFAULT 0,  -- 1 = cleared the stricter check

    updated_at             TEXT DEFAULT (datetime('now'))
);

-- ── TOPIC SCORE HISTORY ───────────────────────────────────────────
-- Every individual score stored for baseline calculation
-- Separate from velocity_scores (which may be pruned)

CREATE TABLE IF NOT EXISTS topic_score_history (
    id             TEXT PRIMARY KEY,
    topic_key      TEXT NOT NULL,
    scored_at      TEXT NOT NULL,
    overall_score  REAL,
    detection_score REAL,
    confidence_score REAL,
    gradient_raw   REAL,   -- raw gradient before calibration
    gradient_cal   REAL,   -- calibrated gradient
    inertia_score  REAL,
    platform_count INTEGER,
    total_mentions INTEGER,
    maturity_at_time TEXT  -- what class it was when scored
);

-- ── BASELINE SNAPSHOTS ────────────────────────────────────────────
-- Daily baseline snapshots per topic, used for trend calculation

CREATE TABLE IF NOT EXISTS topic_baselines (
    topic_key      TEXT NOT NULL,
    snapshot_date  TEXT NOT NULL,  -- YYYY-MM-DD
    avg_gradient   REAL,
    avg_overall    REAL,
    avg_detection  REAL,
    avg_confidence REAL,
    signal_count   INTEGER,
    PRIMARY KEY (topic_key, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_maturity_class
    ON topic_maturity (maturity_class, last_scored_at DESC);
CREATE INDEX IF NOT EXISTS idx_score_history_topic
    ON topic_score_history (topic_key, scored_at DESC);
CREATE INDEX IF NOT EXISTS idx_baselines_topic
    ON topic_baselines (topic_key, snapshot_date DESC);
"""


def init_calibration_db(db_path: str = DB_PATH):
    """Add calibration tables to the existing detector database."""
    conn = db_compat.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(CALIBRATION_SCHEMA)
    conn.commit()
    conn.close()
    print(f"Calibration tables initialised in: {db_path}")


def get_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = db_compat.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ════════════════════════════════════════════════════════════════
# SECTION 2: TOPIC MATURITY CLASSIFIER
# ════════════════════════════════════════════════════════════════

class TopicMaturityClassifier:
    """
    Determines whether a topic is truly emerging or merely
    an established expert-community topic with permanent
    high gradient strength.

    Classification logic:
    ┌─────────────┬──────────────────────────────────────────────┐
    │ NEW         │ First seen < 7 days OR < 5 scoring cycles    │
    ├─────────────┼──────────────────────────────────────────────┤
    │ EMERGING    │ Gradient accelerating > 20pts above baseline │
    │             │ Topic age < 30 days OR score rising steadily │
    ├─────────────┼──────────────────────────────────────────────┤
    │ ESTABLISHED │ 30+ days, 5+ cycles, gradient stable ± 10pts │
    ├─────────────┼──────────────────────────────────────────────┤
    │ RESURGENT   │ Established topic, gradient jumped 15+ pts   │
    │             │ from its own baseline — it's waking up again │
    ├─────────────┼──────────────────────────────────────────────┤
    │ MONITORING  │ Present but no clear trend direction         │
    └─────────────┴──────────────────────────────────────────────┘
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def get_score_history(self, topic_key: str, limit: int = 50) -> list[dict]:
        """Fetch full scoring history for a topic."""
        conn = get_db(self.db_path)
        rows = conn.execute("""
            SELECT * FROM topic_score_history
            WHERE topic_key = ?
            ORDER BY scored_at DESC
            LIMIT ?
        """, (topic_key, limit)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_baseline(self, topic_key: str) -> dict:
        """
        Compute the rolling 14-day baseline for a topic.
        Returns average gradient, score, detection, confidence.
        """
        conn = get_db(self.db_path)
        cutoff = (
            datetime.now(timezone.utc) - timedelta(days=BASELINE_WINDOW_DAYS)
        ).strftime("%Y-%m-%d")

        rows = conn.execute("""
            SELECT avg_gradient, avg_overall, avg_detection, avg_confidence,
                   snapshot_date
            FROM topic_baselines
            WHERE topic_key = ? AND snapshot_date >= ?
            ORDER BY snapshot_date DESC
        """, (topic_key, cutoff)).fetchall()
        conn.close()

        if not rows:
            return {
                "avg_gradient": None,
                "avg_overall":  None,
                "avg_detection": None,
                "avg_confidence": None,
                "data_points": 0,
            }

        grads   = [r["avg_gradient"] for r in rows if r["avg_gradient"] is not None]
        overall = [r["avg_overall"]  for r in rows if r["avg_overall"]  is not None]
        det     = [r["avg_detection"] for r in rows if r["avg_detection"] is not None]
        conf    = [r["avg_confidence"] for r in rows if r["avg_confidence"] is not None]

        return {
            "avg_gradient":   round(statistics.mean(grads),   2) if grads   else None,
            "avg_overall":    round(statistics.mean(overall), 2) if overall else None,
            "avg_detection":  round(statistics.mean(det),     2) if det     else None,
            "avg_confidence": round(statistics.mean(conf),    2) if conf    else None,
            "data_points":    len(rows),
        }

    def classify(
        self,
        topic_key: str,
        current_gradient: float,
        current_overall: float,
        times_scored: int,
        first_detected_at: Optional[str],
    ) -> dict:
        """
        Main classification method.
        Returns a dict with maturity_class, reason, and multipliers.
        """
        # ── Compute days in system ────────────────────────────────
        days_in_system = 0
        if first_detected_at:
            try:
                first = datetime.fromisoformat(
                    first_detected_at.replace("Z", "+00:00")
                )
                days_in_system = (datetime.now(timezone.utc) - first).days
            except Exception:
                days_in_system = 0

        # ── Get baseline ──────────────────────────────────────────
        baseline = self.get_baseline(topic_key)
        baseline_gradient = baseline.get("avg_gradient")
        baseline_overall  = baseline.get("avg_overall")
        baseline_data_pts = baseline.get("data_points", 0)

        # ── Compute velocity (gradient delta from baseline) ───────
        gradient_velocity = None
        if baseline_gradient is not None:
            gradient_velocity = round(current_gradient - baseline_gradient, 2)

        score_velocity = None
        if baseline_overall is not None:
            score_velocity = round(current_overall - baseline_overall, 2)

        # ── Classification decision tree ──────────────────────────
        maturity_class  = "NEW"
        maturity_reason = ""
        calibration_multiplier = 1.0
        anomaly_gate_passed    = False

        # NEW: insufficient history
        if times_scored < MIN_SCORES_ESTABLISHED or days_in_system < 3:
            maturity_class  = "NEW"
            maturity_reason = (
                f"First detection — {times_scored} scoring cycle(s), "
                f"{days_in_system} day(s) in system. "
                "Gradient strength cannot yet be calibrated against baseline."
            )
            # Discount gradient for NEW topics (we cannot confirm it's
            # accelerating vs just existing at this level)
            calibration_multiplier = 0.80
            # Anomaly gate: require 2+ platform signals for NEW topics
            anomaly_gate_passed = False  # Will be re-evaluated with signals

        # ESTABLISHED: long-running stable presence
        elif (days_in_system >= DAYS_TO_ESTABLISHED
              and times_scored >= MIN_SCORES_ESTABLISHED
              and baseline_gradient is not None
              and baseline_data_pts >= 5):

            if gradient_velocity is not None:
                abs_vel = abs(gradient_velocity)

                if abs_vel <= 10:
                    # Stable established topic
                    maturity_class  = "ESTABLISHED"
                    maturity_reason = (
                        f"Topic has been in system {days_in_system} days with stable gradient. "
                        f"Baseline gradient: {baseline_gradient:.0f}. "
                        f"Current gradient: {current_gradient:.0f} (±{abs_vel:.0f}pts from baseline). "
                        "High gradient strength reflects permanent expert-community presence, "
                        "NOT a new emerging signal."
                    )
                    # Discount gradient — permanent expert home, not emergence
                    calibration_multiplier = 0.40
                    anomaly_gate_passed = False

                elif gradient_velocity >= VELOCITY_RESURGENT:
                    # Established topic showing renewed acceleration
                    maturity_class  = "RESURGENT"
                    maturity_reason = (
                        f"Established topic ({days_in_system} days in system) showing "
                        f"renewed acceleration. Gradient jumped {gradient_velocity:+.0f}pts "
                        f"above its {BASELINE_WINDOW_DAYS}-day baseline of {baseline_gradient:.0f}. "
                        "This indicates genuine resurgence, not permanent expert presence."
                    )
                    # Boost gradient — the change is real and significant
                    calibration_multiplier = 1.2
                    anomaly_gate_passed = True

                elif gradient_velocity <= -15:
                    # Established topic declining
                    maturity_class  = "MONITORING"
                    maturity_reason = (
                        f"Established topic declining. Gradient fell {gradient_velocity:.0f}pts "
                        f"below its {BASELINE_WINDOW_DAYS}-day baseline. Interest fading."
                    )
                    calibration_multiplier = 0.4
                    anomaly_gate_passed = False

                else:
                    # Established, mildly moving — still established
                    maturity_class  = "ESTABLISHED"
                    maturity_reason = (
                        f"Established topic ({days_in_system} days). Gradient variation "
                        f"({gradient_velocity:+.0f}pts) within normal range for this topic."
                    )
                    calibration_multiplier = 0.45
                    anomaly_gate_passed = False
            else:
                maturity_class  = "ESTABLISHED"
                maturity_reason = (
                    f"Established topic ({days_in_system} days, {times_scored} scoring cycles). "
                    "No velocity comparison available — treating as stable."
                )
                calibration_multiplier = 0.45
                anomaly_gate_passed = False

        # EMERGING: recent, accelerating, or newly crossing platforms
        elif (baseline_gradient is not None
              and gradient_velocity is not None
              and gradient_velocity >= VELOCITY_EMERGING):
            maturity_class  = "EMERGING"
            maturity_reason = (
                f"Gradient accelerating: +{gradient_velocity:.0f}pts above "
                f"{BASELINE_WINDOW_DAYS}-day baseline of {baseline_gradient:.0f}. "
                f"Topic is {days_in_system} days in system. "
                "Velocity confirms genuine emergence, not permanent expert presence."
            )
            calibration_multiplier = 1.0  # Full score — this is exactly what we want to detect
            anomaly_gate_passed = True

        # MONITORING: present but not trending
        else:
            maturity_class  = "MONITORING"
            maturity_reason = (
                f"Topic present {days_in_system} days, {times_scored} scoring cycles. "
                "No significant velocity or acceleration detected. "
                "Gradient may reflect topic's natural community affinity rather than emergence."
            )
            calibration_multiplier = 0.60
            anomaly_gate_passed = False

        return {
            "maturity_class":         maturity_class,
            "maturity_reason":        maturity_reason,
            "calibration_multiplier": calibration_multiplier,
            "anomaly_gate_passed":    anomaly_gate_passed,
            "days_in_system":         days_in_system,
            "times_scored":           times_scored,
            "gradient_velocity":      gradient_velocity,
            "score_velocity":         score_velocity,
            "baseline_gradient":      baseline_gradient,
            "baseline_overall":       baseline_overall,
            "baseline_data_pts":      baseline_data_pts,
        }


# ════════════════════════════════════════════════════════════════
# SECTION 3: CALIBRATED GRADIENT STRENGTH
# Replaces the raw gradient computation in the detector
# ════════════════════════════════════════════════════════════════

def compute_calibrated_gradient(
    raw_gradient: float,
    gradient_ratio: float,
    maturity: dict,
) -> tuple[float, float, str]:
    """
    Applies maturity-based calibration to the raw gradient strength.

    Returns:
        (calibrated_score, calibration_factor, explanation)

    The key principle:
      - ESTABLISHED topics: gradient measures permanent home, not emergence
        → Discount heavily (×0.25). Ratio means nothing without velocity.
      - RESURGENT topics: gradient change above baseline is meaningful
        → Boost (×1.2). The delta is the signal.
      - EMERGING topics: gradient is valid signal
        → Full score (×1.0).
      - NEW topics: can't calibrate yet — moderate discount (×0.75)
        → Apply as-is but flag as unconfirmed.
    """
    multiplier   = maturity.get("calibration_multiplier", 1.0)
    maturity_cls = maturity.get("maturity_class", "NEW")
    velocity     = maturity.get("gradient_velocity")
    baseline_g   = maturity.get("baseline_gradient")
    days         = maturity.get("days_in_system", 0)

    calibrated = round(min(100, raw_gradient * multiplier), 2)

    # Build explanation
    if maturity_cls == "ESTABLISHED" and multiplier <= 0.45:
        explanation = (
            f"Gradient discounted {round((1-multiplier)*100)}% — "
            f"topic has been in expert communities {days} days. "
            f"High niche concentration ({raw_gradient:.0f}) reflects permanent home, "
            "not new emergence. Score adjusted to prevent false anomaly detection."
        )
    elif maturity_cls == "RESURGENT":
        # velocity/baseline can be None for lifecycle-derived maturity (no
        # score-history baseline) — never let the explanation string crash.
        _v = f"+{velocity:.0f}pts" if velocity is not None else "renewed velocity"
        _b = f" of {baseline_g:.0f}" if baseline_g is not None else ""
        explanation = (
            f"Gradient boosted {round((multiplier-1)*100)}% — "
            f"established topic showing {_v} above its baseline{_b}. "
            "Velocity confirms genuine renewed interest."
        )
    elif maturity_cls == "EMERGING":
        _ev = (f"+{velocity:.0f}pts above baseline {baseline_g:.0f}"
               if (velocity is not None and baseline_g is not None)
               else "gaining across cycles")
        explanation = (
            f"Gradient lightly calibrated (×{multiplier}) — "
            f"emerging: {_ev}. Acceleration is forming but the baseline is still building."
        )
    elif maturity_cls == "NEW":
        explanation = (
            f"Gradient modestly discounted (×{multiplier}) — "
            f"first detection, no baseline available yet. "
            "Cannot confirm whether this is emergence or permanent expert presence. "
            "Gradient will be calibrated after 5+ scoring cycles."
        )
    else:
        explanation = (
            f"Gradient moderately discounted (×{multiplier}) — "
            "topic present but no clear acceleration trend. "
            "Monitoring for velocity changes."
        )

    return calibrated, multiplier, explanation


# ════════════════════════════════════════════════════════════════
# SECTION 4: CALIBRATED ANOMALY GATE
# Replaces the simple anomaly check in GravitationalAnomalyDetector
# ════════════════════════════════════════════════════════════════

def evaluate_anomaly_gate(
    gradient_ratio: float,
    ft_ratio: float,
    asymmetry_detected: bool,
    platform_count: int,
    inertia_score: float,
    maturity: dict,
    gradient_velocity: Optional[float],
) -> tuple[bool, list[str], str]:
    """
    Multi-signal anomaly gate that accounts for topic maturity.

    OLD LOGIC (broken):
      Fires when gradient_ratio >= 4x AND 2+ indicators present.
      Problem: "ai agent" at 10x ratio + cross-platform = anomaly
      even though it has been in expert spaces for 2+ years.

    NEW LOGIC:
      The anomaly gate requires EVIDENCE OF CHANGE, not just
      evidence of niche concentration. For established topics,
      gradient ratio alone provides zero evidence of change.

    Rules:
    ┌────────────┬──────────────────────────────────────────────┐
    │ ESTABLISHED│ Anomaly ONLY if: velocity > 15pts AND        │
    │            │ (first_timer_ratio >= 35% OR inertia > 30)   │
    ├────────────┼──────────────────────────────────────────────┤
    │ NEW        │ Anomaly if: cross-platform (2+ platforms) AND │
    │            │ at least 1 of: ft_ratio, asymmetry, inertia  │
    ├────────────┼──────────────────────────────────────────────┤
    │ EMERGING   │ Standard gate: gradient ratio AND 2+ signals  │
    ├────────────┼──────────────────────────────────────────────┤
    │ RESURGENT  │ Anomaly confirmed (velocity passed gate)      │
    ├────────────┼──────────────────────────────────────────────┤
    │ MONITORING │ No anomaly (no velocity evidence)             │
    └────────────┴──────────────────────────────────────────────┘

    Returns: (is_anomaly, evidence_list, anomaly_label)
    """
    maturity_cls  = maturity.get("maturity_class", "NEW")
    gate_passed   = maturity.get("anomaly_gate_passed", False)
    evidence      = []
    is_anomaly    = False
    anomaly_label = ""

    # ── Evidence collection ───────────────────────────────────────
    has_first_timer = ft_ratio >= 0.35   # unified with FIRST_TIMER_THRESHOLD (was 0.30)
    has_asymmetry   = asymmetry_detected
    has_inertia     = inertia_score > INERTIA_ZERO_THRESHOLD
    has_xplatform   = platform_count >= 2
    has_velocity    = (
        gradient_velocity is not None
        and gradient_velocity >= VELOCITY_RESURGENT
    )
    has_high_ratio  = gradient_ratio >= GRADIENT_RATIO_THRESHOLD

    # Always collect what we see
    if has_first_timer:
        evidence.append(
            f"First-timer ratio {round(ft_ratio*100)}% "
            "(new voices entering expert community)"
        )
    if has_asymmetry:
        evidence.append(
            "Engagement asymmetry detected "
            "(discussion depth exceeds passive engagement pattern)"
        )
    if has_inertia:
        evidence.append(
            f"Inertia confirmed: {round(inertia_score)} "
            "(sustained acceleration across multiple windows)"
        )
    if has_xplatform:
        evidence.append(
            f"Cross-platform: {platform_count} independent communities"
        )
    if has_velocity:
        evidence.append(
            f"Gradient velocity: +{gradient_velocity:.0f}pts above baseline"
        )

    # ── Gate decisions by maturity ────────────────────────────────

    if maturity_cls == "RESURGENT":
        # Velocity already cleared the gate
        is_anomaly = True
        anomaly_label = "RESURGENCE ANOMALY"
        if not evidence:
            evidence.append(
                f"Gradient velocity +{gradient_velocity:.0f}pts "
                "above established baseline — renewed emergence confirmed"
            )

    elif maturity_cls == "ESTABLISHED":
        # Very strict gate — gradient ratio alone is noise, not signal
        if has_velocity and (has_first_timer or has_inertia):
            is_anomaly = True
            anomaly_label = "RESURGENCE ANOMALY"
            evidence.append(
                "NOTE: Established topic showing renewed acceleration. "
                "Gradient boost confirmed by first-timer or inertia evidence."
            )
        else:
            is_anomaly = False
            anomaly_label = ""
            evidence.append(
                f"ESTABLISHED TOPIC: Gradient ratio {gradient_ratio:.1f}x reflects "
                f"permanent expert-community presence ({maturity.get('days_in_system')} days). "
                "Anomaly gate requires velocity evidence — not triggered."
            )

    elif maturity_cls == "EMERGING":
        # Standard gate with velocity confirmation
        evidence_count = sum([
            has_first_timer, has_asymmetry, has_inertia,
            has_xplatform, has_high_ratio, has_velocity,
        ])
        if evidence_count >= 2:
            is_anomaly = True
            anomaly_label = "EMERGING ANOMALY"
        else:
            is_anomaly = False

    elif maturity_cls == "NEW":
        # Lenient gate but requires cross-platform + at least one signal
        evidence_count = sum([has_first_timer, has_asymmetry, has_inertia])
        if has_xplatform and evidence_count >= 1:
            is_anomaly = True
            anomaly_label = "NEW SIGNAL ANOMALY"
        elif has_xplatform and has_high_ratio:
            # Gradient-only for new topics: flag but label appropriately
            is_anomaly = True
            anomaly_label = "NEW SIGNAL — GRADIENT ONLY"
        else:
            is_anomaly = False

    else:  # MONITORING
        is_anomaly = False

    return is_anomaly, evidence, anomaly_label


# ════════════════════════════════════════════════════════════════
# SECTION 5: COMMUNICATION LAYER FIXES
# All plain-English output corrected for maturity and data state
# ════════════════════════════════════════════════════════════════

def build_what_to_do(
    stage: str,
    maturity_class: str,
    inertia_score: float,
    confidence_score: float,
    detection_score: float,
    times_scored: int,
    gradient_velocity: Optional[float],
    is_anomaly: bool,
) -> dict:
    """
    THE MOST IMPORTANT COMMUNICATION FUNCTION.

    Produces a clear, honest What-To-Do recommendation
    that accounts for both the score AND the maturity context.

    Returns dict with:
      - action: short label (1-4 words)
      - instruction: one sentence
      - detail: 1-2 supporting sentences
      - urgency: HIGH / MEDIUM / LOW / WAIT
    """
    # ── First-run state ───────────────────────────────────────────
    # GENUINELY first cycle — no history yet.
    if times_scored <= 1:
        return {
            "action":    "First collection cycle",
            "urgency":   "WAIT",
            "instruction": (
                "Engine is in its first scoring cycle for this topic. "
                "Scores will sharpen after more cycles."
            ),
            "detail": (
                "Inertia requires 2+ consecutive 6-hour windows to confirm. "
                "Check back after the next collection run (~30 min). "
                "If the gradient holds and inertia rises, confidence will increase."
            ),
            "lead_time_note": None,  # NEVER show lead time estimate with inertia = 0
        }
    # Scored several cycles but momentum (inertia) is still flat — this is NOT a
    # first collection; it's a tracked topic whose acceleration hasn't kicked in.
    if inertia_score <= INERTIA_ZERO_THRESHOLD:
        return {
            "action":    "Momentum not yet building",
            "urgency":   "WAIT",
            "instruction": (
                f"Tracked across {times_scored} scoring cycles, but momentum "
                f"(inertia) is still flat — no confirmed acceleration yet."
            ),
            "detail": (
                "Inertia needs 2+ consecutive 6-hour windows of acceleration to "
                "confirm. The signal is stable but not yet accelerating."
            ),
            "lead_time_note": None,  # no lead-time estimate without confirmed inertia
        }

    # ── Established topics: different action framing ──────────────
    if maturity_class == "ESTABLISHED":
        return {
            "action":    "Established topic",
            "urgency":   "LOW",
            "instruction": (
                "This is an established expert-community topic, "
                "not a new emerging signal."
            ),
            "detail": (
                "High gradient strength reflects where this topic has always lived, "
                "not a sudden move. Monitor for genuine velocity changes — "
                "a first-timer surge or inertia acceleration would indicate real resurgence."
            ),
            "lead_time_note": None,
        }

    # ── Resurgent: established but waking up ──────────────────────
    if maturity_class == "RESURGENT":
        return {
            "action":    "Resurgence detected",
            "urgency":   "HIGH",
            "instruction": (
                "An established topic is showing renewed acceleration "
                "above its historical baseline."
            ),
            "detail": (
                "This is stronger evidence than a new topic appearing — "
                "the community has returned to something it understands, "
                "which typically accelerates faster than a first emergence. "
                "Both detection and confidence are rising together."
            ),
            "lead_time_note": "Resurgence signals typically reach Google Trends in 5–10 days.",
        }

    # ── Standard stage-based recommendations ─────────────────────
    if stage == "BREAKOUT":
        return {
            "action":    "Breakout — maximum lead time",
            "urgency":   "HIGH",
            "instruction": "Both scores above 85 — as confirmed as early signals get.",
            "detail": (
                "Gradient and inertia are both high, cross-platform spread is confirmed, "
                "and the gap between detection and confidence is closing. "
                "This window is open now and will narrow as mainstream awareness grows."
            ),
            "lead_time_note": f"Est. {_estimate_lead_time(detection_score, confidence_score)} days before Google Trends breakout.",
        }

    elif stage == "STRONG":
        return {
            "action":    "Strong signal — window open",
            "urgency":   "MEDIUM",
            "instruction": "Strong signal with good confidence; not yet breakout.",
            "detail": (
                "Both scores agree this is real. Not yet breakout, "
                "but the runway ahead is significant — detection is ahead of "
                "confidence, and that gap typically closes over subsequent cycles."
            ),
            "lead_time_note": f"Est. {_estimate_lead_time(detection_score, confidence_score)} days before Google Trends breakout.",
        }

    elif stage == "EMERGING":
        if confidence_score >= 55:
            return {
                "action":    "Confidence building",
                "urgency":   "MEDIUM",
                "instruction": "Confidence is building toward the breakout threshold.",
                "detail": (
                    "Signal is confirmed across multiple windows. "
                    "Detection is ahead of confidence — that gap typically closes "
                    "over subsequent cycles."
                ),
                "lead_time_note": f"Est. {_estimate_lead_time(detection_score, confidence_score)} days before Google Trends breakout.",
            }
        else:
            return {
                "action":    "Signal building",
                "urgency":   "LOW",
                "instruction": "Movement detected but confidence still building.",
                "detail": (
                    "The detection score sees something meaningful, but confidence "
                    "has not yet crossed 55. Worth tracking across the next 2–3 cycles."
                ),
                "lead_time_note": None,
            }

    elif stage == "WATCHING":
        return {
            "action":    "Signal building",
            "urgency":   "WAIT",
            "instruction": (
                "Not yet confirmed — scores are in the early 35–54 range."
            ),
            "detail": (
                "Both scores are in the 35–54 range. "
                "The gap between them indicates which score to watch — "
                "a closing gap means momentum is building."
            ),
            "lead_time_note": None,
        }

    else:  # MONITORING
        return {
            "action":    "Below threshold",
            "urgency":   "WAIT",
            "instruction": "Signal is below the monitoring threshold.",
            "detail": (
                "Topic is present but not trending. "
                "It remains in the background queue; any acceleration surfaces it automatically."
            ),
            "lead_time_note": None,
        }


def _estimate_lead_time(detection: float, confidence: float) -> str:
    """
    Only called when Inertia > threshold AND scores are meaningful.
    Returns a range string, never a single number.
    """
    avg = (detection + confidence) / 2
    if avg >= 85:
        return "3–7"
    elif avg >= 70:
        return "5–10"
    elif avg >= 55:
        return "7–14"
    else:
        return "10–21"


def build_gap_interpretation(gap: float, stage: str, maturity: str) -> dict:
    """
    Corrected gap interpretation that describes the gap directionally —
    not as inherently positive or negative.

    The old version: "14-point gap = high conviction" sounds positive.
    The corrected version: "14-point gap — both scores agree at WATCHING level"
    makes clear that high conviction of weakness is not a strong signal.
    """
    if gap <= 15:
        label = f"Both scores agree - high conviction {stage.lower()} signal"
        meaning = (
            f"The detection and confidence systems are aligned. "
            f"This is a high-conviction signal at the {stage} level. "
            + ("Both agree this is strong." if stage in ("BREAKOUT", "STRONG")
               else "Both agree this is not yet confirmed." if stage in ("WATCHING", "MONITORING")
               else "Both agree this is building.")
        )
    elif gap <= 35:
        label = "Early stage - confirmation building"
        meaning = (
            "Detection sees the signal clearly. Confidence is accumulating evidence. "
            "The gap will close over the next 24–72 hours as more windows confirm."
        )
    elif gap <= 60:
        label = "Very early - detected, not confirmed"
        meaning = (
            "Maximum lead time opportunity. The engine detected this before "
            "the confirmation data has arrived. High potential, not yet proven. "
            "Ideal window for early actors who accept some uncertainty."
        )
    else:
        label = "Speculative - dark matter signal only"
        meaning = (
            "Detection fired primarily on dark matter inference. "
            "Confirmation has not arrived. Highest risk, "
            "highest potential lead time if correct."
        )

    # Maturity override for established topics
    if maturity == "ESTABLISHED":
        label   = f"Established topic - gap reflects permanent expert home"
        meaning = (
            "High gradient is where this topic permanently lives in expert communities. "
            "The gap does not indicate early emergence — it reflects the topic's "
            "natural community distribution. Watch for velocity changes instead."
        )

    return {"label": label, "meaning": meaning}


def build_component_groups(components: dict) -> dict:
    """
    Groups the seven score components into three labelled buckets
    for the Score Breakdown display.

    Reduces cognitive load from 7 individual rows to 3 meaningful groups.
    Each group has a status derived from its component scores.
    """
    g = components.get("gradient_calibrated", components.get("gradient_raw", 0))
    m = components.get("platform_diversity", 0)
    i = components.get("inertia", 0)
    p = components.get("persistence", 0)
    d = components.get("dark_matter", 0)
    c = components.get("confidence_decay", 0)
    n = components.get("nowtrend_internal", 0)

    # ── Group 1: Signal Quality ──────────────────────────────────
    quality_avg = (g + m) / 2
    if quality_avg >= 60:
        quality_status = "STRONG"
        quality_label  = "Strong — real niche signal confirmed"
    elif quality_avg >= 35:
        quality_status = "MODERATE"
        quality_label  = "Moderate — partial confirmation"
    else:
        quality_status = "WEAK"
        quality_label  = "Weak — insufficient signal density"

    # ── Group 2: Signal Momentum ─────────────────────────────────
    # Most important group — both 0 = first collection run
    momentum_avg = (i + p) / 2
    i_zero = i <= INERTIA_ZERO_THRESHOLD
    p_zero = p <= INERTIA_ZERO_THRESHOLD

    if i_zero and p_zero:
        momentum_status = "PENDING"
        momentum_label  = "Pending — first collection run, check back in ~30 min"
    elif momentum_avg >= 50:
        momentum_status = "CONFIRMED"
        momentum_label  = "Confirmed — sustained acceleration across windows"
    elif momentum_avg >= 25:
        momentum_status = "BUILDING"
        momentum_label  = "Building — early acceleration, needs more cycles"
    else:
        momentum_status = "LOW"
        momentum_label  = "Low — no sustained acceleration detected"

    # ── Group 3: Signal Context ───────────────────────────────────
    # N (internal app demand) is DELIBERATELY excluded from this average and
    # shown as a separate block below — it must not contaminate the objective
    # gradient with our own users' behaviour (reflexivity).
    context_avg = (d + c) / 2
    if context_avg >= 40:
        context_status = "STRONG"
        context_label  = "Strong — dark matter and freshness support signal"
    elif context_avg >= 20:
        context_status = "MODERATE"
        context_label  = "Moderate — partial context signals"
    else:
        context_status = "LOW"
        context_label  = "Low — limited context data"

    return {
        "signal_quality": {
            "label":   "Signal Quality",
            "status":  quality_status,
            "note":    quality_label,
            "components": {
                "gradient_strength": {
                    "det": g,
                    "conf": components.get("gradient_conf", g),
                    "desc": "Niche vs mainstream concentration",
                    "calibration_note": components.get("gradient_calibration_note", ""),
                },
                "platform_diversity": {
                    "det": components.get("platform_det", m),
                    "conf": m,
                    "desc": "Cross-platform diffusion pattern match",
                    "calibration_note": "",
                },
            },
        },
        "signal_momentum": {
            "label":   "Signal Momentum",
            "status":  momentum_status,
            "note":    momentum_label,
            "pending_explanation": (
                "Requires 2+ consecutive 6-hour collection windows. "
                "Run collection again in ~30 minutes."
                if momentum_status == "PENDING" else ""
            ),
            "components": {
                "inertia": {
                    "det":  i,
                    "conf": i,
                    "desc": "Acceleration sustained across time windows",
                    "pending": i_zero,
                },
                "persistence": {
                    "det":  p,
                    "conf": p,
                    "desc": "Sustained elevation across scoring cycles",
                    "pending": p_zero,
                },
            },
        },
        "signal_context": {
            "label":  "Signal Context",
            "status": context_status,
            "note":   context_label,
            "components": {
                "dark_matter": {
                    "det":  d,
                    "conf": d,
                    "desc": "First-timer ratio — inferred private conversation",
                    "pending": False,
                },
                "confidence_decay": {
                    "det":  c,
                    "conf": c,
                    "desc": "Signal freshness and directional momentum",
                    "pending": False,
                },
            },
        },
        # Separate, clearly-labeled block — NOT part of the Gradient Score math.
        # Internal app demand (how often our own users surface this topic). Shown
        # for context only; excluded from Detection/Confidence/Overall to keep the
        # score an objective measure of EXTERNAL attention.
        "community_demand": {
            "label":  "Community Demand",
            "status": "INFO",
            "note":   "Internal app demand — shown for context, not part of the Gradient Score",
            "in_composite": False,
            "components": {
                "nowtrendin_demand": {
                    "det":  n,
                    "conf": n,
                    "desc": "How often Now TrendIn users surface this topic (not scored)",
                    "pending": n == 0,
                },
            },
        },
    }


def build_why_this_matters(
    topic: str,
    maturity_class: str,
    maturity_reason: str,
    platforms: list,
    gradient_raw: float,
    gradient_calibrated: float,
    gradient_velocity: Optional[float],
    baseline_gradient: Optional[float],
    inertia: float,
    ft_ratio: float,
    asymmetry: bool,
    stage: str,
) -> str:
    """
    Builds the Why This Matters explanation with full maturity context.
    This is the second most important communication field after What To Do.
    """
    parts = []

    # Lead with maturity context for established/resurgent
    if maturity_class == "ESTABLISHED":
        parts.append(
            f"'{topic}' is an established expert-community topic. "
            f"It has maintained high niche concentration "
            f"(current: {round(gradient_raw)}%, baseline: {round(baseline_gradient or 0)}%) "
            f"for an extended period — this is its natural home, not a new emergence."
        )
    elif maturity_class == "RESURGENT":
        parts.append(
            f"'{topic}' is re-emerging after a period of stability. "
            f"Gradient strength jumped +{round(gradient_velocity or 0)} points above "
            f"its {BASELINE_WINDOW_DAYS}-day baseline — this acceleration is the signal, "
            f"not the absolute niche concentration."
        )
    elif maturity_class == "NEW":
        parts.append(
            f"'{topic}' was first detected recently. "
            f"Current gradient strength of {round(gradient_raw)} reflects niche concentration, "
            f"but cannot yet be confirmed as emergence vs permanent expert presence. "
            f"Baseline calibration available after 5+ scoring cycles."
        )
    elif maturity_class == "EMERGING":
        parts.append(
            f"'{topic}' is confirmed emerging. Gradient strength rose "
            f"+{round(gradient_velocity or 0)} points above its {BASELINE_WINDOW_DAYS}-day "
            f"baseline — velocity confirms this is a real signal, not a permanent expert home."
        )

    # Platform spread
    if len(platforms) >= 2:
        plat_str = " + ".join(p.upper() for p in platforms)
        parts.append(
            f"Detected independently on {len(platforms)} platforms ({plat_str}) — "
            "cross-community convergence that is difficult to fake."
        )

    # Dark matter signals
    if ft_ratio >= 0.30:
        parts.append(
            f"{round(ft_ratio*100)}% of discussants are new to this community — "
            "suggests external traffic arriving from a private source."
        )
    if asymmetry:
        parts.append(
            "Discussion depth is disproportionate to passive engagement — "
            "the community is debating, not just acknowledging."
        )

    # Inertia status
    if inertia <= INERTIA_ZERO_THRESHOLD:
        parts.append(
            "Inertia is not yet confirmed — this is the first collection cycle. "
            "The velocity will be measurable after the next run."
        )
    elif inertia >= 60:
        parts.append(
            "Inertia is high — acceleration sustained across multiple time windows "
            "confirms this is momentum, not a one-time spike."
        )

    return " ".join(parts)


# ════════════════════════════════════════════════════════════════
# SECTION 6: THE MAIN CALIBRATION ENGINE
# Drop-in processor for GravitationalAnomalyDetector output
# ════════════════════════════════════════════════════════════════

class CalibrationEngine:
    """
    The main integration point.

    Usage in GravitationalAnomalyDetector.score_all_topics():

        cal = CalibrationEngine(db_path)
        raw_result = self.score_topic(topic_key, signals)
        if raw_result:
            calibrated = cal.apply(raw_result, signals)
            # Use calibrated instead of raw_result for all storage/API responses
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path    = db_path
        self.classifier = TopicMaturityClassifier(db_path)
        init_calibration_db(db_path)

    def _get_or_create_maturity_record(self, topic_key: str) -> dict:
        """Fetch existing maturity record or create a new one."""
        conn = get_db(self.db_path)
        row = conn.execute(
            "SELECT * FROM topic_maturity WHERE topic_key = ?",
            (topic_key,)
        ).fetchone()
        conn.close()
        if row:
            return dict(row)
        return {
            "topic_key":      topic_key,
            "first_detected_at": _now(),
            "times_scored":   0,
            "days_in_system": 0,
        }

    def _save_score_to_history(
        self,
        topic_key: str,
        raw_result: dict,
        calibrated_gradient: float,
        maturity_class: str,
    ):
        """Persist score to history table for future baseline calculation."""
        conn = get_db(self.db_path)
        import uuid as _uuid
        conn.execute("""
            INSERT OR IGNORE INTO topic_score_history
            (id, topic_key, scored_at, overall_score, detection_score,
             confidence_score, gradient_raw, gradient_cal, inertia_score,
             platform_count, total_mentions, maturity_at_time)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            _uuid.uuid4().hex[:16],
            topic_key,
            raw_result.get("scored_at", _now()),
            raw_result.get("overall_score"),
            raw_result.get("detection_score"),
            raw_result.get("confidence_score"),
            raw_result.get("gradient_strength"),
            calibrated_gradient,
            raw_result.get("inertia_score"),
            len(json.loads(raw_result.get("platforms_active", "[]"))),
            raw_result.get("total_mentions"),
            maturity_class,
        ))
        conn.commit()
        conn.close()

    def _update_daily_baseline(self, topic_key: str, raw_gradient: float,
                                overall: float, detection: float, confidence: float):
        """Update or insert today's baseline snapshot."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        conn  = get_db(self.db_path)
        # Upsert: average if multiple scores today
        existing = conn.execute(
            "SELECT * FROM topic_baselines WHERE topic_key=? AND snapshot_date=?",
            (topic_key, today)
        ).fetchone()
        if existing:
            conn.execute("""
                UPDATE topic_baselines SET
                    avg_gradient  = (avg_gradient + ?) / 2.0,
                    avg_overall   = (avg_overall  + ?) / 2.0,
                    avg_detection = (avg_detection + ?) / 2.0,
                    avg_confidence= (avg_confidence + ?) / 2.0,
                    signal_count  = signal_count + 1
                WHERE topic_key=? AND snapshot_date=?
            """, (raw_gradient, overall, detection, confidence,
                  topic_key, today))
        else:
            conn.execute("""
                INSERT INTO topic_baselines
                    (topic_key, snapshot_date, avg_gradient, avg_overall,
                     avg_detection, avg_confidence, signal_count)
                VALUES (?,?,?,?,?,?,1)
            """, (topic_key, today, raw_gradient, overall, detection, confidence))
        conn.commit()
        conn.close()

    def _update_maturity_record(
        self,
        topic_key: str,
        topic_display: str,
        maturity: dict,
        is_anomaly: bool,
        anomaly_label: str,
    ):
        """Persist the maturity classification."""
        conn = get_db(self.db_path)
        conn.execute("""
            INSERT INTO topic_maturity
                (topic_key, topic_display, first_detected_at, last_scored_at,
                 times_scored, days_in_system, maturity_class, maturity_reason,
                 baseline_gradient, baseline_overall, gradient_velocity,
                 score_velocity, calibration_multiplier, anomaly_gate_passed,
                 updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(topic_key) DO UPDATE SET
                topic_display       = excluded.topic_display,
                last_scored_at      = excluded.last_scored_at,
                times_scored        = topic_maturity.times_scored + 1,
                days_in_system      = excluded.days_in_system,
                maturity_class      = excluded.maturity_class,
                maturity_reason     = excluded.maturity_reason,
                baseline_gradient   = excluded.baseline_gradient,
                baseline_overall    = excluded.baseline_overall,
                gradient_velocity   = excluded.gradient_velocity,
                score_velocity      = excluded.score_velocity,
                calibration_multiplier = excluded.calibration_multiplier,
                anomaly_gate_passed = excluded.anomaly_gate_passed,
                updated_at          = excluded.updated_at
        """, (
            topic_key,
            topic_display,
            maturity.get("first_detected_at", _now()),
            _now(),
            maturity.get("times_scored", 0) + 1,
            maturity.get("days_in_system", 0),
            maturity.get("maturity_class", "NEW"),
            maturity.get("maturity_reason", ""),
            maturity.get("baseline_gradient"),
            maturity.get("baseline_overall"),
            maturity.get("gradient_velocity"),
            maturity.get("score_velocity"),
            maturity.get("calibration_multiplier", 1.0),
            1 if is_anomaly else 0,
            _now(),
        ))
        conn.commit()
        conn.close()

    def apply(self, raw_result: dict, signals: list) -> dict:
        """
        MAIN ENTRY POINT.

        Takes the raw dict from GravitationalAnomalyDetector.score_topic()
        and returns a fully calibrated dict with:
          - Corrected gradient strength
          - Maturity classification
          - Re-evaluated anomaly flag
          - All communication fields rebuilt
          - Component groups added
        """
        topic_key  = raw_result["topic_key"]
        topic_disp = raw_result.get("topic_display", topic_key)

        # ── 1. Load/create maturity record ──────────────────────
        record     = self._get_or_create_maturity_record(topic_key)
        # The maturity record's own counter can lag the authoritative lifecycle
        # count (topic_lifecycle.total_scoring_cycles). Prefer the highest known
        # cycle count so a topic scored 5× is never mislabeled "first collection".
        times_scored = max(
            int(record.get("times_scored", 0) or 0),
            int(raw_result.get("total_scoring_cycles", 0) or 0),
            int(raw_result.get("times_scored", 0) or 0),
        )
        first_detected = record.get("first_detected_at", _now())

        # ── 2. Classify maturity ─────────────────────────────────
        maturity = self.classifier.classify(
            topic_key      = topic_key,
            current_gradient = raw_result.get("gradient_strength", 0),
            current_overall  = raw_result.get("overall_score", 0),
            times_scored     = times_scored,
            first_detected_at = first_detected,
        )
        maturity["first_detected_at"] = first_detected
        maturity["times_scored"]      = times_scored

        # ── 3. Calibrate gradient strength ───────────────────────
        raw_G     = raw_result.get("gradient_strength", 0)
        cal_G, cal_mult, cal_note = compute_calibrated_gradient(
            raw_gradient   = raw_G,
            gradient_ratio = raw_result.get("gradient_ratio", 0),
            maturity       = maturity,
        )

        # ── 4. Re-evaluate anomaly gate ──────────────────────────
        platforms = json.loads(raw_result.get("platforms_active", "[]"))
        is_anomaly, evidence, anomaly_label = evaluate_anomaly_gate(
            gradient_ratio   = raw_result.get("gradient_ratio", 0),
            ft_ratio         = raw_result.get("first_timer_ratio", 0),
            asymmetry_detected = bool(raw_result.get("engagement_asymmetry", 0)),
            platform_count   = len(platforms),
            inertia_score    = raw_result.get("inertia_score", 0),
            maturity         = maturity,
            gradient_velocity = maturity.get("gradient_velocity"),
        )

        # ── 5. Recalculate scores with calibrated gradient ───────
        I   = raw_result.get("inertia_score", 0)
        M   = raw_result.get("platform_diversity", 0)
        D   = raw_result.get("dark_matter_score", 0)
        C   = raw_result.get("confidence_decay", 0)

        # The Detection/Confidence/Overall headline is re-derived from the EXPERT
        # G·I·M·D·C formula ONLY for expert-pathway topics. Mainstream/blended
        # topics are scored by the dual-pathway on magnitude+breadth, because the
        # expert gradient is structurally ~0 for them — re-deriving here would
        # collapse EVERY mainstream topic to ~25-28 (FIFA, Trump, Juneteenth all
        # ≈ 27, unrankable) and silently undo the dual-pathway. At scoring time
        # the pathway isn't set yet (defaults to expert, then the dual-pathway
        # step overwrites mainstream values afterward); at SERVE time the stored
        # row carries detection_pathway='mainstream', so we PRESERVE the
        # dual-pathway headline instead of clobbering it. (See dual-pathway step
        # in score_all_topics + the Trend Signal Diagnostic's N-discipline gate.)
        _pathway = (raw_result.get("detection_pathway") or "expert").lower()
        if _pathway in ("expert", "niche", ""):
            overall_cal = round(min(100,
                cal_G * 0.30 + I * 0.25 + M * 0.20 + D * 0.15 + C * 0.10), 2)
            detection_cal = round(min(100,
                cal_G * 0.40 + D * 0.25 + I * 0.20 + M * 0.10 + C * 0.05), 2)
            confidence_cal = round(min(100,
                I * 0.35 + M * 0.30 + cal_G * 0.20 + C * 0.10 + D * 0.05), 2)
        else:
            overall_cal    = round(min(100, float(raw_result.get("overall_score", 0) or 0)), 2)
            detection_cal  = round(min(100, float(raw_result.get("detection_score", 0) or 0)), 2)
            confidence_cal = round(min(100, float(raw_result.get("confidence_score", 0) or 0)), 2)
        gap_cal = round(detection_cal - confidence_cal, 1)

        # Recalculate stage from calibrated overall
        if overall_cal >= 85:   stage_cal = "BREAKOUT"
        elif overall_cal >= 70: stage_cal = "STRONG"
        elif overall_cal >= 55: stage_cal = "EMERGING"
        elif overall_cal >= 35: stage_cal = "WATCHING"
        else:                   stage_cal = "MONITORING"

        # ── 6. Build all communication fields ───────────────────
        what_to_do = build_what_to_do(
            stage           = stage_cal,
            maturity_class  = maturity["maturity_class"],
            inertia_score   = I,
            confidence_score = confidence_cal,
            detection_score  = detection_cal,
            times_scored    = times_scored,
            gradient_velocity = maturity.get("gradient_velocity"),
            is_anomaly      = is_anomaly,
        )

        gap_interp = build_gap_interpretation(
            gap      = gap_cal,
            stage    = stage_cal,
            maturity = maturity["maturity_class"],
        )

        why_this_matters = build_why_this_matters(
            topic               = topic_disp,
            maturity_class      = maturity["maturity_class"],
            maturity_reason     = maturity["maturity_reason"],
            platforms           = platforms,
            gradient_raw        = raw_G,
            gradient_calibrated = cal_G,
            gradient_velocity   = maturity.get("gradient_velocity"),
            baseline_gradient   = maturity.get("baseline_gradient"),
            inertia             = I,
            ft_ratio            = raw_result.get("first_timer_ratio", 0),
            asymmetry           = bool(raw_result.get("engagement_asymmetry", 0)),
            stage               = stage_cal,
        )

        component_groups = build_component_groups({
            "gradient_raw":            raw_G,
            "gradient_calibrated":     cal_G,
            "gradient_conf":           round(raw_G * 0.5, 2),  # conf mode uses lower G weight
            "gradient_calibration_note": cal_note,
            "platform_diversity":      M,
            "platform_det":            raw_result.get("platform_diversity", M),
            "inertia":                 I,
            "persistence":             0,  # populated after multiple cycles
            "dark_matter":             D,
            "confidence_decay":        C,
            "nowtrend_internal":       0,
        })

        # ── 7. Persist history and maturity ─────────────────────
        self._save_score_to_history(topic_key, raw_result, cal_G, maturity["maturity_class"])
        self._update_daily_baseline(topic_key, raw_G,
                                    raw_result.get("overall_score", 0),
                                    raw_result.get("detection_score", 0),
                                    raw_result.get("confidence_score", 0))
        self._update_maturity_record(topic_key, topic_disp, maturity, is_anomaly, anomaly_label)

        # ── 8. Return the full calibrated result dict ────────────
        return {
            **raw_result,  # start with raw, override with calibrated values

            # Calibrated scores
            "gradient_strength_raw":   raw_G,
            "gradient_strength":       cal_G,
            "gradient_calibration_note": cal_note,
            "gradient_calibration_multiplier": cal_mult,
            "overall_score":           overall_cal,
            "detection_score":         detection_cal,
            "confidence_score":        confidence_cal,
            "heisenberg_gap":          gap_cal,
            "signal_stage":            stage_cal,

            # Maturity
            "maturity_class":          maturity["maturity_class"],
            "maturity_reason":         maturity["maturity_reason"],
            "days_in_system":          maturity.get("days_in_system", 0),
            "times_scored":            times_scored,
            "gradient_velocity":       maturity.get("gradient_velocity"),
            "baseline_gradient":       maturity.get("baseline_gradient"),

            # Corrected anomaly
            "is_gravitational_anomaly": 1 if is_anomaly else 0,
            "anomaly_label":           anomaly_label,
            "anomaly_reason":          " · ".join(evidence),
            "anomaly_evidence":        evidence,

            # Communication
            "what_to_do":             what_to_do,
            "gap_interpretation":      gap_interp,
            "why_this_matters":        why_this_matters,
            "component_groups":        component_groups,

            # Lead time: only present when inertia is confirmed
            "lead_time_available":     I > INERTIA_ZERO_THRESHOLD,
            "lead_time_note":          what_to_do.get("lead_time_note"),
        }


# ════════════════════════════════════════════════════════════════
# SECTION 7: STANDALONE ANALYSIS AND REPORTING
# ════════════════════════════════════════════════════════════════

def analyse_all_topics(db_path: str = DB_PATH):
    """Print maturity classification for all scored topics."""
    conn = get_db(db_path)
    try:
        rows = conn.execute("""
            SELECT topic_key, topic_display, maturity_class,
                   days_in_system, times_scored,
                   baseline_gradient, gradient_velocity,
                   anomaly_gate_passed
            FROM topic_maturity
            ORDER BY maturity_class, gradient_velocity DESC
        """).fetchall()
    except Exception:
        print("Maturity table not found — run init_calibration_db() first")
        conn.close()
        return
    conn.close()

    print("\n" + "═" * 80)
    print("TOPIC MATURITY REPORT")
    print("═" * 80)
    print(f"{'TOPIC':30} {'MATURITY':12} {'DAYS':>5} {'CYCLES':>7} "
          f"{'BASE_G':>7} {'VEL':>6} {'ANOMALY':>8}")
    print("─" * 80)

    for row in rows:
        r = dict(row)
        vel   = f"{r['gradient_velocity']:+.0f}" if r['gradient_velocity'] else "  N/A"
        base  = f"{r['baseline_gradient']:.0f}" if r['baseline_gradient'] else " N/A"
        anom  = "YES" if r['anomaly_gate_passed'] else "no"
        print(
            f"{(r['topic_display'] or r['topic_key'])[:29]:30} "
            f"{r['maturity_class']:12} "
            f"{r['days_in_system']:>5} "
            f"{r['times_scored']:>7} "
            f"{base:>7} "
            f"{vel:>6} "
            f"{anom:>8}"
        )

    # Summary
    print("─" * 80)
    counts = defaultdict(int)
    for row in rows:
        counts[row["maturity_class"]] += 1
    for cls, cnt in sorted(counts.items()):
        print(f"  {cls}: {cnt}")
    print("═" * 80)


def reclassify_all(db_path: str = DB_PATH):
    """
    Re-runs maturity classification for all topics in the database.
    Run this after the first week of data accumulation.
    """
    engine = CalibrationEngine(db_path)
    conn   = get_db(db_path)

    try:
        topics = conn.execute(
            "SELECT DISTINCT topic_key FROM topic_score_history"
        ).fetchall()
    except Exception:
        print("Score history table not found")
        conn.close()
        return
    conn.close()

    print(f"Reclassifying {len(topics)} topics...")
    reclassified = defaultdict(int)

    for row in topics:
        tk = row["topic_key"]
        record = engine._get_or_create_maturity_record(tk)
        maturity = engine.classifier.classify(
            topic_key         = tk,
            current_gradient  = record.get("baseline_gradient") or 50,
            current_overall   = record.get("baseline_overall") or 50,
            times_scored      = record.get("times_scored", 0),
            first_detected_at = record.get("first_detected_at"),
        )
        reclassified[maturity["maturity_class"]] += 1

    print("Reclassification complete:")
    for cls, cnt in sorted(reclassified.items()):
        print(f"  {cls}: {cnt}")


# ════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Now TrendIn — Signal Calibration Engine"
    )
    parser.add_argument(
        "--mode",
        choices=["analyse", "reclassify", "report", "init"],
        default="report",
    )
    parser.add_argument("--db", default=DB_PATH)
    args = parser.parse_args()

    if args.mode == "init":
        init_calibration_db(args.db)
        print("Calibration database initialised.")

    elif args.mode in ("analyse", "report"):
        init_calibration_db(args.db)
        analyse_all_topics(args.db)

    elif args.mode == "reclassify":
        init_calibration_db(args.db)
        reclassify_all(args.db)


if __name__ == "__main__":
    main()
