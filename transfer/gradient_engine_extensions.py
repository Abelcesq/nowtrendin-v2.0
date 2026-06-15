"""
gradient_engine_extensions.py
=============================
Now TrendIn — Auditability, Calibration & Scenario Projection layer.

Drop alongside gradient_engine_backend.py. Adds:
  • Methodology versioning (every score is reproducible under the rules that made it)
  • Full audit log (signal-by-signal attribution per component)
  • Outcome tracking (label trends as true/false positives for calibration)
  • Calibration run log (every weight/threshold change recorded with before/after stats)
  • Scenario projection engine (premium tier: "what would change this score and by how much")
  • Tier-gated FastAPI routes (free / premium)

Integration (3 lines in your existing startup):
    from gradient_engine_extensions import init_extensions, ext_router, score_and_audit
    init_extensions()
    app.include_router(ext_router)

Then replace `compute_gradient_score(topic)` calls with `score_and_audit(topic)`
to get the same return value PLUS audit + scenario rows persisted.

NOTE: scenarios are NOT predictions. They are response-surface samples:
"given current measurements, here is what the model would output if X changed."
That epistemological framing is what makes the premium tier defensible.
"""

import os
import json
import hashlib
import sqlite3
import statistics
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from typing import Optional

from fastapi import APIRouter, HTTPException, Header, Query, Depends

# Import from your existing backend
from gradient_engine_backend import (
    DB_PATH, get_db, compute_gradient_score, fetch_recent_signals,
    save_gradient_score, GradientScore,
)


# ── Methodology Registry ──────────────────────────────────────────────────────

DEFAULT_METHODOLOGY = {
    "weights_overall":    {"G": 0.30, "I": 0.25, "M": 0.20, "D": 0.15, "C": 0.10},
    "weights_detection":  {"G": 0.40, "D": 0.25, "I": 0.20, "M": 0.10, "C": 0.05},
    "weights_confidence": {"I": 0.35, "M": 0.30, "G": 0.20, "C": 0.10, "D": 0.05},
    "thresholds": {
        "detection_niche_to_mainstream_ratio":  3.0,
        "confidence_niche_to_mainstream_ratio": 6.0,
        "detection_inertia_consecutive_windows":  2,
        "confidence_inertia_consecutive_windows": 4,
        "detection_first_timer_ratio":  0.25,
        "confidence_first_timer_ratio": 0.40,
        "breakout_score":  85,
        "strong_signal_score": 70,
    },
    "notes": "v1.0 — initial methodology per project spec May 2026",
}


def methodology_version_id(methodology: dict) -> str:
    """Deterministic version hash. Same inputs → same version. Change weights → new version."""
    payload = json.dumps(
        {k: v for k, v in methodology.items() if k != "notes"},
        sort_keys=True
    ).encode()
    return "v" + hashlib.sha256(payload).hexdigest()[:10]


def register_methodology(methodology: dict = None) -> str:
    """Register a methodology version if not already present. Returns version id."""
    methodology = methodology or DEFAULT_METHODOLOGY
    ver = methodology_version_id(methodology)
    conn = get_db()
    existing = conn.execute(
        "SELECT version FROM methodology_versions WHERE version = ?", (ver,)
    ).fetchone()
    if not existing:
        conn.execute(
            """INSERT INTO methodology_versions
               (version, created_at, weights_overall, weights_detection,
                weights_confidence, thresholds, notes)
               VALUES (?,?,?,?,?,?,?)""",
            (ver, datetime.now(timezone.utc).isoformat(),
             json.dumps(methodology["weights_overall"]),
             json.dumps(methodology["weights_detection"]),
             json.dumps(methodology["weights_confidence"]),
             json.dumps(methodology["thresholds"]),
             methodology.get("notes", ""))
        )
        conn.commit()
    conn.close()
    return ver


def get_methodology(version: str) -> dict:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM methodology_versions WHERE version = ?", (version,)
    ).fetchone()
    conn.close()
    if not row:
        raise ValueError(f"Unknown methodology version: {version}")
    return {
        "version": row["version"],
        "created_at": row["created_at"],
        "weights_overall":    json.loads(row["weights_overall"]),
        "weights_detection":  json.loads(row["weights_detection"]),
        "weights_confidence": json.loads(row["weights_confidence"]),
        "thresholds":         json.loads(row["thresholds"]),
        "notes": row["notes"],
    }


# ── Extended Schema ───────────────────────────────────────────────────────────

EXTENSIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS methodology_versions (
    version TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    weights_overall TEXT NOT NULL,
    weights_detection TEXT NOT NULL,
    weights_confidence TEXT NOT NULL,
    thresholds TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS gradient_scores_meta (
    topic TEXT NOT NULL,
    computed_at TEXT NOT NULL,
    methodology_version TEXT NOT NULL,
    PRIMARY KEY (topic, computed_at),
    FOREIGN KEY (methodology_version) REFERENCES methodology_versions(version)
);

CREATE TABLE IF NOT EXISTS score_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    computed_at TEXT NOT NULL,
    methodology_version TEXT NOT NULL,
    component TEXT NOT NULL,
    raw_value REAL,
    normalized_value REAL,
    weight_overall REAL,
    weight_detection REAL,
    weight_confidence REAL,
    contribution_overall REAL,
    contribution_detection REAL,
    contribution_confidence REAL,
    supporting_signal_ids TEXT,
    explanation TEXT,
    FOREIGN KEY (methodology_version) REFERENCES methodology_versions(version)
);
CREATE INDEX IF NOT EXISTS idx_audit_topic ON score_audit_log (topic, computed_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_version ON score_audit_log (methodology_version);

CREATE TABLE IF NOT EXISTS outcome_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL UNIQUE,
    first_scored_at TEXT NOT NULL,
    first_overall_score REAL,
    first_detection_score REAL,
    first_confidence_score REAL,
    peak_score REAL,
    peak_score_at TEXT,
    google_trends_breakout_at TEXT,
    mainstream_media_first_seen_at TEXT,
    outcome_class TEXT,
    lead_time_days REAL,
    reviewed_by TEXT,
    reviewed_at TEXT,
    notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_outcomes_class ON outcome_tracking (outcome_class);

CREATE TABLE IF NOT EXISTS calibration_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at TEXT NOT NULL,
    methodology_version_before TEXT,
    methodology_version_after TEXT,
    training_window_start TEXT,
    training_window_end TEXT,
    n_outcomes_used INTEGER,
    fp_rate_breakout_before REAL,
    fp_rate_breakout_after REAL,
    lead_time_median_before REAL,
    lead_time_median_after REAL,
    notes TEXT,
    FOREIGN KEY (methodology_version_before) REFERENCES methodology_versions(version),
    FOREIGN KEY (methodology_version_after)  REFERENCES methodology_versions(version)
);

CREATE TABLE IF NOT EXISTS scenario_projections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    score_computed_at TEXT NOT NULL,
    methodology_version TEXT NOT NULL,
    scenario_name TEXT NOT NULL,
    perturbation TEXT NOT NULL,
    original_overall REAL,
    projected_overall REAL,
    delta_overall REAL,
    original_detection REAL,
    projected_detection REAL,
    delta_detection REAL,
    original_confidence REAL,
    projected_confidence REAL,
    delta_confidence REAL,
    natural_language TEXT,
    generated_at TEXT NOT NULL,
    FOREIGN KEY (methodology_version) REFERENCES methodology_versions(version)
);
CREATE INDEX IF NOT EXISTS idx_scenarios_topic ON scenario_projections (topic, generated_at DESC);
"""


def init_extensions(path: str = DB_PATH):
    """Idempotent: creates extension tables and registers default methodology."""
    conn = sqlite3.connect(path)
    conn.executescript(EXTENSIONS_SCHEMA)
    conn.commit()
    conn.close()
    ver = register_methodology(DEFAULT_METHODOLOGY)
    print(f"[ext] Methodology registered: {ver}")
    return ver


# ── Signal Attribution (which signals drove which component) ─────────────────

def attribute_signals_to_components(signals: list) -> dict:
    """
    Best-effort attribution: which raw_signals.id values drove each component.
    Mirrors the logic in compute_* functions, returns capped lists for storage.
    """
    if not signals:
        return {"G": [], "I": [], "M": [], "D": [], "C": []}

    # G — Gradient Strength: signals in niche/expert tier (drive the niche ratio)
    g_sigs = [s["id"] for s in signals if s.get("source_tier") in ("niche", "expert")]

    # I — Inertia: signals in the most recent 12h (the windows whose acceleration matters)
    now = datetime.now(timezone.utc)
    recent_cutoff = now - timedelta(hours=12)
    i_sigs = []
    for s in signals:
        try:
            ts = datetime.fromisoformat(s["collected_at"].replace("Z", "+00:00"))
            if ts >= recent_cutoff:
                i_sigs.append(s["id"])
        except Exception:
            continue

    # M — Medium Sequence: first signal per platform (drives sequence detection)
    platform_first = {}
    for s in signals:
        key = f"{s.get('source')}_{s.get('source_tier')}"
        try:
            ts = datetime.fromisoformat(s["collected_at"].replace("Z", "+00:00"))
            if key not in platform_first or ts < platform_first[key][0]:
                platform_first[key] = (ts, s["id"])
        except Exception:
            continue
    m_sigs = [v[1] for v in platform_first.values()]

    # D — Dark Matter: reddit first-timers + engagement-asymmetric signals
    d_sigs = [
        s["id"] for s in signals
        if s.get("source") == "reddit" and (
            s.get("is_first_timer")
            or s.get("comment_count", 0) > s.get("upvote_count", 0) * 0.3
        )
    ]

    # C — Confidence Decay: most recent signals (freshness)
    sorted_recent = sorted(signals, key=lambda s: s.get("collected_at", ""), reverse=True)
    c_sigs = [s["id"] for s in sorted_recent[:5]]

    # Cap each at 20 to keep audit log JSON manageable
    return {
        "G": g_sigs[:20], "I": i_sigs[:20], "M": m_sigs[:20],
        "D": d_sigs[:20], "C": c_sigs[:20],
    }


# ── Audit Log Writer ─────────────────────────────────────────────────────────

COMPONENT_EXPLANATIONS = {
    "G": "Gradient Strength — niche-to-total engagement ratio. Higher = signal still contained in expert communities, maximum runway ahead.",
    "I": "Inertia — consecutive 6-hour windows showing accelerating signal count + vocabulary expansion. Higher = sustained momentum, not a one-day spike.",
    "M": "Medium Sequence — diffusion pattern across platforms (Builder→Buyer, Enthusiast→Mainstream, Research→Commerce). Higher = canonical pre-mainstream shape.",
    "D": "Dark Matter — first-timer ratio + engagement asymmetry + vocabulary clustering. Higher = external traffic flowing into niche, ripples of unseen private conversations.",
    "C": "Confidence Decay — signal freshness + score trajectory direction. Higher = signal still strengthening, lower = fading.",
}


def write_audit_log(topic: str, gs: GradientScore, signals: list, methodology: dict):
    """Persist one row per component into score_audit_log."""
    version = methodology_version_id(methodology)
    w_o = methodology["weights_overall"]
    w_d = methodology["weights_detection"]
    w_c = methodology["weights_confidence"]
    attribution = attribute_signals_to_components(signals)

    comp_values = {
        "G": gs.gradient_strength,
        "I": gs.inertia_score,
        "M": gs.medium_sequence_score,
        "D": gs.dark_matter_score,
        "C": gs.confidence_decay,
    }

    conn = get_db()
    conn.execute(
        """INSERT OR REPLACE INTO gradient_scores_meta
           (topic, computed_at, methodology_version) VALUES (?,?,?)""",
        (topic, gs.computed_at, version)
    )

    rows = []
    for comp, val in comp_values.items():
        rows.append((
            topic, gs.computed_at, version, comp,
            val, val,  # raw == normalized (components emit 0-100 already)
            w_o[comp], w_d[comp], w_c[comp],
            round(val * w_o[comp], 4),
            round(val * w_d[comp], 4),
            round(val * w_c[comp], 4),
            json.dumps(attribution[comp]),
            COMPONENT_EXPLANATIONS[comp],
        ))
    conn.executemany(
        """INSERT INTO score_audit_log
           (topic, computed_at, methodology_version, component,
            raw_value, normalized_value,
            weight_overall, weight_detection, weight_confidence,
            contribution_overall, contribution_detection, contribution_confidence,
            supporting_signal_ids, explanation)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows
    )
    conn.commit()
    conn.close()


def fetch_audit_for_score(topic: str, computed_at: str) -> list:
    conn = get_db()
    rows = conn.execute(
        """SELECT * FROM score_audit_log
           WHERE topic = ? AND computed_at = ?
           ORDER BY CASE component
              WHEN 'G' THEN 1 WHEN 'I' THEN 2 WHEN 'M' THEN 3
              WHEN 'D' THEN 4 WHEN 'C' THEN 5 ELSE 6 END""",
        (topic, computed_at)
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        try:
            d["supporting_signal_ids"] = json.loads(d["supporting_signal_ids"])
        except Exception:
            pass
        out.append(d)
    return out


# ── Scenario Projection Engine ───────────────────────────────────────────────

def apply_perturbation(components: dict, perturbation: dict) -> dict:
    """
    Apply perturbation to component values. Two forms:
      - "X": +N  (delta added to component X, e.g. {"I": +20})
      - "X_target": N  (absolute target value for component X)
    Result is bounded [0, 100].
    """
    out = dict(components)
    for key in ("G", "I", "M", "D", "C"):
        if f"{key}_target" in perturbation:
            out[key] = max(0.0, min(100.0, float(perturbation[f"{key}_target"])))
        elif key in perturbation:
            out[key] = max(0.0, min(100.0, out[key] + float(perturbation[key])))
    return out


def recompute_scores(components: dict, methodology: dict) -> dict:
    w_o = methodology["weights_overall"]
    w_d = methodology["weights_detection"]
    w_c = methodology["weights_confidence"]
    return {
        "overall":    round(min(100, sum(components[k] * w_o[k] for k in "GIMDC")), 2),
        "detection":  round(min(100, sum(components[k] * w_d[k] for k in "GIMDC")), 2),
        "confidence": round(min(100, sum(components[k] * w_c[k] for k in "GIMDC")), 2),
    }


SCENARIO_CATALOG = [
    {
        "name": "mainstream_entry_48h",
        "perturbation": {"G": -15, "M": +5, "C": -10},
        "narrative": (
            "If '{topic}' crosses into mainstream subreddits (e.g. r/technology, r/news) "
            "within ~48 hours, Gradient Strength falls (~15pt) as the niche ratio drops "
            "below the detection threshold. Platform spread improves but the value window "
            "closes — signal moves from 'detected' to 'crowded'."
        ),
    },
    {
        "name": "dark_matter_surge_to_confidence",
        "perturbation": {"D_target": 75},
        "narrative": (
            "If first-timer ratio climbs from {first_timer_pct} to 40%+ over the next 4 days, "
            "Dark Matter rises to ~75 (Δ {d_delta:+.0f}pt). This is the canonical pre-mainstream "
            "signature: external traffic flowing into niche communities before public awareness. "
            "Detection Score gains most (+{detection_delta:+.1f}pt) — Dark Matter is weighted "
            "25% in Detection vs 5% in Confidence."
        ),
    },
    {
        "name": "inertia_two_more_windows",
        "perturbation": {"I": +20},
        "narrative": (
            "If two additional 6-hour windows show ≥10% growth in signal count, Inertia rises "
            "~20pt. Confidence Score weights Inertia at 35%, so the Detection/Confidence gap "
            "closes by approximately {confidence_delta:+.1f}pt — signal moves from 'early' "
            "toward 'confirmed'."
        ),
    },
    {
        "name": "github_velocity_surge",
        "perturbation": {"G": +5, "M": +7},
        "narrative": (
            "If GitHub star velocity for related repositories increases meaningfully "
            "(+500/day or more) and Hacker News picks it up, Pattern A (Builder-to-Buyer) "
            "signal strengthens. Medium Sequence gains ~7pt, Gradient Strength holds. "
            "Lead time estimate extends 2–3 days."
        ),
    },
    {
        "name": "signal_decay_48h",
        "perturbation": {"I": -25, "C": -30},
        "narrative": (
            "If signal volume drops 50%+ over the next 48 hours, Inertia falls ~25pt and "
            "Confidence Decay drops ~30pt. This is the false-positive signature — the score "
            "retroactively marks itself as a fading spike, not a sustained trend. "
            "Overall drops ~{overall_delta:.1f}pt."
        ),
    },
    {
        "name": "twitter_breakout",
        "perturbation": {"G": -20, "C": -15, "M": +3},
        "narrative": (
            "If Twitter/X drives mainstream attention before niche communities reach inertia "
            "threshold, Gradient Strength collapses (~-20pt). Classic 'viral moment' shape — "
            "high visibility, no underlying builder activity. Net signal: act fast if positioned, "
            "exit if not."
        ),
    },
]


def compute_scenarios(topic: str, score: GradientScore,
                      methodology: dict = None) -> list:
    """
    Generate scenario projections for a topic given its current score.
    Returns list of dicts; persists to scenario_projections table.

    NOT predictions — response-surface samples. The natural-language narrative
    makes this framing explicit to the institutional user.
    """
    methodology = methodology or DEFAULT_METHODOLOGY
    version = methodology_version_id(methodology)

    current = {
        "G": score.gradient_strength,
        "I": score.inertia_score,
        "M": score.medium_sequence_score,
        "D": score.dark_matter_score,
        "C": score.confidence_decay,
    }
    orig = recompute_scores(current, methodology)

    results = []
    rows = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for scn in SCENARIO_CATALOG:
        perturbed = apply_perturbation(current, scn["perturbation"])
        proj = recompute_scores(perturbed, methodology)

        deltas = {
            "overall_delta":    round(proj["overall"]    - orig["overall"],    2),
            "detection_delta":  round(proj["detection"]  - orig["detection"],  2),
            "confidence_delta": round(proj["confidence"] - orig["confidence"], 2),
        }
        d_delta = round(perturbed["D"] - current["D"], 2)

        narrative = scn["narrative"].format(
            topic=topic,
            first_timer_pct=f"{score.first_timer_ratio:.0%}",
            d_delta=d_delta,
            **deltas,
        )

        result = {
            "scenario_name": scn["name"],
            "perturbation": scn["perturbation"],
            "original": orig,
            "projected": proj,
            **deltas,
            "natural_language": narrative,
        }
        results.append(result)

        rows.append((
            topic, score.computed_at, version, scn["name"],
            json.dumps(scn["perturbation"]),
            orig["overall"], proj["overall"], deltas["overall_delta"],
            orig["detection"], proj["detection"], deltas["detection_delta"],
            orig["confidence"], proj["confidence"], deltas["confidence_delta"],
            narrative, now_iso,
        ))

    conn = get_db()
    conn.executemany(
        """INSERT INTO scenario_projections
           (topic, score_computed_at, methodology_version, scenario_name, perturbation,
            original_overall, projected_overall, delta_overall,
            original_detection, projected_detection, delta_detection,
            original_confidence, projected_confidence, delta_confidence,
            natural_language, generated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows
    )
    conn.commit()
    conn.close()
    return results


# ── Outcome Tracking ─────────────────────────────────────────────────────────

def upsert_outcome_on_first_score(topic: str, gs: GradientScore):
    """When a topic is first scored, capture its baseline for later outcome labeling."""
    conn = get_db()
    existing = conn.execute(
        "SELECT topic, peak_score FROM outcome_tracking WHERE topic = ?", (topic,)
    ).fetchone()
    if not existing:
        conn.execute(
            """INSERT INTO outcome_tracking
               (topic, first_scored_at, first_overall_score,
                first_detection_score, first_confidence_score,
                peak_score, peak_score_at, outcome_class)
               VALUES (?,?,?,?,?,?,?,?)""",
            (topic, gs.computed_at, gs.overall_score,
             gs.detection_score, gs.confidence_score,
             gs.overall_score, gs.computed_at, "still_pending")
        )
    else:
        if gs.overall_score > (existing["peak_score"] or 0):
            conn.execute(
                """UPDATE outcome_tracking
                   SET peak_score = ?, peak_score_at = ?
                   WHERE topic = ?""",
                (gs.overall_score, gs.computed_at, topic)
            )
    conn.commit()
    conn.close()


def label_outcome(topic: str, outcome_class: str,
                  google_trends_breakout_at: Optional[str] = None,
                  mainstream_first_seen_at: Optional[str] = None,
                  reviewed_by: str = "system", notes: str = "") -> dict:
    """
    Mark a topic as true_positive / false_positive / false_negative / still_pending.
    Computes lead_time_days if breakout date is given.
    """
    valid = {"true_positive", "false_positive", "false_negative", "still_pending"}
    if outcome_class not in valid:
        raise ValueError(f"outcome_class must be one of {valid}")

    conn = get_db()
    row = conn.execute(
        "SELECT first_scored_at FROM outcome_tracking WHERE topic = ?", (topic,)
    ).fetchone()
    if not row:
        conn.close()
        raise ValueError(f"No outcome record for topic: {topic}")

    lead_time = None
    if google_trends_breakout_at:
        try:
            first = datetime.fromisoformat(row["first_scored_at"].replace("Z", "+00:00"))
            breakout = datetime.fromisoformat(
                google_trends_breakout_at.replace("Z", "+00:00")
            )
            lead_time = round((breakout - first).total_seconds() / 86400, 2)
        except Exception:
            pass

    conn.execute(
        """UPDATE outcome_tracking
           SET outcome_class = ?,
               google_trends_breakout_at = ?,
               mainstream_media_first_seen_at = ?,
               lead_time_days = ?,
               reviewed_by = ?,
               reviewed_at = ?,
               notes = ?
           WHERE topic = ?""",
        (outcome_class, google_trends_breakout_at, mainstream_first_seen_at,
         lead_time, reviewed_by, datetime.now(timezone.utc).isoformat(),
         notes, topic)
    )
    conn.commit()
    result = dict(conn.execute(
        "SELECT * FROM outcome_tracking WHERE topic = ?", (topic,)
    ).fetchone())
    conn.close()
    return result


def outcome_stats(min_score: float = 70.0) -> dict:
    """Aggregate stats for the calibration dashboard."""
    conn = get_db()
    rows = conn.execute(
        """SELECT outcome_class, first_overall_score, peak_score, lead_time_days
           FROM outcome_tracking
           WHERE first_overall_score >= ?""",
        (min_score,)
    ).fetchall()
    conn.close()
    if not rows:
        return {"n": 0, "min_score_threshold": min_score}

    counts = {"true_positive": 0, "false_positive": 0,
              "false_negative": 0, "still_pending": 0}
    lead_times = []
    for r in rows:
        counts[r["outcome_class"]] = counts.get(r["outcome_class"], 0) + 1
        if r["outcome_class"] == "true_positive" and r["lead_time_days"]:
            lead_times.append(r["lead_time_days"])

    decided = counts["true_positive"] + counts["false_positive"]
    fp_rate = counts["false_positive"] / decided if decided else None

    return {
        "n": len(rows),
        "min_score_threshold": min_score,
        "counts": counts,
        "fp_rate": round(fp_rate, 4) if fp_rate is not None else None,
        "median_lead_time_days": round(statistics.median(lead_times), 2) if lead_times else None,
        "mean_lead_time_days":   round(statistics.mean(lead_times),   2) if lead_times else None,
    }


# ── Calibration Run Logger ────────────────────────────────────────────────────

def log_calibration_run(version_before: str, version_after: str,
                        training_window_start: str, training_window_end: str,
                        n_outcomes: int,
                        fp_rate_before: float, fp_rate_after: float,
                        lead_time_before: float, lead_time_after: float,
                        notes: str = "") -> int:
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO calibration_runs
           (run_at, methodology_version_before, methodology_version_after,
            training_window_start, training_window_end, n_outcomes_used,
            fp_rate_breakout_before, fp_rate_breakout_after,
            lead_time_median_before, lead_time_median_after, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (datetime.now(timezone.utc).isoformat(),
         version_before, version_after,
         training_window_start, training_window_end, n_outcomes,
         fp_rate_before, fp_rate_after,
         lead_time_before, lead_time_after, notes)
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id


# ── Unified Scoring Wrapper ──────────────────────────────────────────────────

def score_and_audit(topic: str, methodology: dict = None) -> Optional[dict]:
    """
    Drop-in replacement for compute_gradient_score(topic) that also:
      • writes audit rows (one per component, with signal attribution)
      • registers/updates outcome_tracking with the baseline
      • generates scenario projections (premium-tier data)

    Returns the same GradientScore as a dict, plus audit + scenarios attached.
    """
    methodology = methodology or DEFAULT_METHODOLOGY
    gs = compute_gradient_score(topic)
    if not gs:
        return None

    signals = fetch_recent_signals(topic, hours=72)
    save_gradient_score(gs)
    write_audit_log(topic, gs, signals, methodology)
    upsert_outcome_on_first_score(topic, gs)
    scenarios = compute_scenarios(topic, gs, methodology)

    return {
        **asdict(gs),
        "methodology_version": methodology_version_id(methodology),
        "audit": fetch_audit_for_score(topic, gs.computed_at),
        "scenarios": scenarios,
    }


# ── Tier Gating (stub auth — replace with JWT for production) ────────────────

def require_tier(min_tier: str):
    """
    FastAPI dependency. Reads X-Tier header. For validation phase only —
    replace with proper JWT-based auth before any real institutional sales.
    """
    tier_rank = {"free": 0, "premium": 1, "institutional": 2}

    def checker(x_tier: str = Header(default="free")):
        if tier_rank.get(x_tier, -1) < tier_rank.get(min_tier, 99):
            raise HTTPException(
                status_code=402,
                detail=f"This endpoint requires tier '{min_tier}' or higher. "
                       f"Current tier: '{x_tier}'."
            )
        return x_tier
    return checker


# ── FastAPI Router ───────────────────────────────────────────────────────────

ext_router = APIRouter(prefix="/v1", tags=["audit-calibration-scenarios"])


# --- Free / Influencer / SMB tier ---

@ext_router.get("/score/{topic}/public")
def get_public_score(topic: str):
    """Free tier: score + component breakdown + top signals + plain-English narrative."""
    conn = get_db()
    row = conn.execute(
        """SELECT * FROM gradient_scores WHERE topic = ?
           ORDER BY computed_at DESC LIMIT 1""", (topic,)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, f"No scores for topic: {topic}")

    history = conn.execute(
        """SELECT computed_at, overall_score, detection_score, confidence_score
           FROM gradient_scores WHERE topic = ?
           ORDER BY computed_at DESC LIMIT 14""", (topic,)
    ).fetchall()
    conn.close()

    d = dict(row)
    for f in ("active_platforms", "platform_sequence", "top_signals"):
        if isinstance(d.get(f), str):
            try:    d[f] = json.loads(d[f])
            except: d[f] = []

    return {
        "topic": d["topic"],
        "computed_at": d["computed_at"],
        "overall_score": d["overall_score"],
        "detection_score": d["detection_score"],
        "confidence_score": d["confidence_score"],
        "gap": round(d["detection_score"] - d["confidence_score"], 2),
        "components": {
            "G": d["gradient_strength"], "I": d["inertia_score"],
            "M": d["medium_sequence_score"], "D": d["dark_matter_score"],
            "C": d["confidence_decay"],
        },
        "component_narratives": {k: COMPONENT_EXPLANATIONS[k] for k in "GIMDC"},
        "top_signals": d.get("top_signals", []),
        "lead_time_days": d["lead_time_estimate_days"],
        "diffusion_pattern": d["diffusion_pattern"],
        "confidence_level": d["confidence_level"],
        "why_this_matters": d["why_this_matters"],
        "history_7d": [dict(r) for r in history],
    }


@ext_router.get("/track-record")
def get_public_track_record(min_score: float = Query(80.0, ge=50.0, le=100.0)):
    """Public ledger of high-confidence detections with outcome status. Free."""
    conn = get_db()
    rows = conn.execute(
        """SELECT topic, first_scored_at, first_overall_score, peak_score,
                  outcome_class, lead_time_days, google_trends_breakout_at
           FROM outcome_tracking
           WHERE first_overall_score >= ?
           ORDER BY first_scored_at DESC LIMIT 200""",
        (min_score,)
    ).fetchall()
    conn.close()
    return {
        "min_score_threshold": min_score,
        "stats": outcome_stats(min_score=min_score),
        "calls": [dict(r) for r in rows],
    }


# --- Premium / Institutional tier ---

@ext_router.get("/score/{topic}/audit",
                dependencies=[Depends(require_tier("premium"))])
def get_score_audit(topic: str, computed_at: Optional[str] = None):
    """Full audit log per component with signal attribution. Reproducible under methodology_version."""
    conn = get_db()
    if not computed_at:
        row = conn.execute(
            "SELECT computed_at FROM gradient_scores WHERE topic = ? ORDER BY computed_at DESC LIMIT 1",
            (topic,)
        ).fetchone()
        if not row:
            conn.close()
            raise HTTPException(404, f"No scores for topic: {topic}")
        computed_at = row["computed_at"]

    meta = conn.execute(
        "SELECT methodology_version FROM gradient_scores_meta WHERE topic = ? AND computed_at = ?",
        (topic, computed_at)
    ).fetchone()
    conn.close()

    audit = fetch_audit_for_score(topic, computed_at)
    if not audit:
        raise HTTPException(404, "No audit log for that score.")

    return {
        "topic": topic,
        "computed_at": computed_at,
        "methodology_version": meta["methodology_version"] if meta else None,
        "methodology": get_methodology(meta["methodology_version"]) if meta else None,
        "components": audit,
    }


@ext_router.get("/score/{topic}/scenarios",
                dependencies=[Depends(require_tier("premium"))])
def get_scenarios(topic: str):
    """Latest scenario projections for a topic. Premium tier."""
    conn = get_db()
    rows = conn.execute(
        """SELECT * FROM scenario_projections
           WHERE topic = ?
           ORDER BY generated_at DESC LIMIT 12""", (topic,)
    ).fetchall()
    conn.close()
    if not rows:
        raise HTTPException(404, "No scenarios. Run score_and_audit() first.")
    scenarios = []
    for r in rows:
        d = dict(r)
        try:
            d["perturbation"] = json.loads(d["perturbation"])
        except Exception:
            pass
        scenarios.append(d)
    seen, deduped = set(), []
    for s in scenarios:
        if s["scenario_name"] not in seen:
            seen.add(s["scenario_name"])
            deduped.append(s)
    return {"topic": topic, "scenarios": deduped}


@ext_router.post("/score/{topic}/refresh",
                 dependencies=[Depends(require_tier("premium"))])
def refresh_full_score(topic: str):
    """Compute score + write audit + generate scenarios. Premium tier."""
    result = score_and_audit(topic)
    if not result:
        raise HTTPException(404, f"Insufficient signals for: {topic}")
    return result


@ext_router.post("/outcomes/{topic}/label",
                 dependencies=[Depends(require_tier("premium"))])
def label_outcome_endpoint(
    topic: str,
    outcome_class: str = Query(...,
        pattern="^(true_positive|false_positive|false_negative|still_pending)$"),
    google_trends_breakout_at: Optional[str] = None,
    mainstream_first_seen_at: Optional[str] = None,
    reviewed_by: str = "manual",
    notes: str = "",
):
    return label_outcome(topic, outcome_class, google_trends_breakout_at,
                         mainstream_first_seen_at, reviewed_by, notes)


@ext_router.get("/calibration/stats",
                dependencies=[Depends(require_tier("premium"))])
def calibration_dashboard(min_score: float = Query(70.0, ge=0.0, le=100.0)):
    """Outcome stats for calibration dashboard. Premium tier."""
    return outcome_stats(min_score=min_score)


@ext_router.get("/methodology/{version}",
                dependencies=[Depends(require_tier("premium"))])
def get_methodology_endpoint(version: str):
    try:
        return get_methodology(version)
    except ValueError as e:
        raise HTTPException(404, str(e))


@ext_router.get("/methodology",
                dependencies=[Depends(require_tier("premium"))])
def list_methodology_versions():
    conn = get_db()
    rows = conn.execute(
        "SELECT version, created_at, notes FROM methodology_versions ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return {"versions": [dict(r) for r in rows]}


# ── Standalone run (for testing the extension in isolation) ──────────────────

if __name__ == "__main__":
    print("Initializing extensions schema...")
    ver = init_extensions()
    print(f"Default methodology version: {ver}")
    print("\nExtension ready. Wire into your existing FastAPI app:")
    print("  from gradient_engine_extensions import init_extensions, ext_router, score_and_audit")
    print("  init_extensions()")
    print("  app.include_router(ext_router)")
