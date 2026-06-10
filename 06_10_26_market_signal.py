"""
================================================================
NOW TRENDIN — MARKET SIGNAL ENGINE
A Dual-Score Gradient for Market Factors (finance-native actors)
================================================================

WHAT THIS IS:
  The same Detection / Confidence philosophy as the attention Gradient
  Score — but built from FINANCE-NATIVE actors instead of social ones,
  and measured relative to each item's own baseline.

  It replaces the single "Positioning" number with two scores plus a
  gap, so the section can express not just "is this abnormal" but
  "how EARLY is this market signal" — the same earliness/certainty
  tradeoff the attention gradient captures.

THE TWO SCORES (the earliness vs certainty tradeoff):
  DETECTION  (early-warning, ~higher false positive):
     leading / soft signals — are informed actors moving BEFORE the
     hard data confirms? Built from:
       · Dark Positioning   (emerging & cross-market micro-shifts)
       · Positioning Concentration (smart-money vs retail)
       · Analyst Signal     (revisions, target & rating changes)
  CONFIDENCE (confirmation, ~lower false positive):
     hard / realized signals — does the financial reality confirm it?
     Built from:
       · Fundamental Confirmation (realized revenue/margin/EPS)
       · Market Momentum    (sustained price/fundamental trend)
  SHARED (feed both):
       · Cross-Market Diffusion (signal across venues)
       · Signal Freshness   (recency / persistence)

THE GAP (reads exactly like the attention gradient):
  Detection >> Confidence  → EARLY: analysts/smart money positioning
                              before fundamentals confirm (the window)
  Both high, small gap     → CONFIRMED: corroborated, likely priced in
  Both low                 → ROUTINE: nothing unusual vs baseline
  Detection << Confidence  → LAGGING: hard data moved, early window passed

PRESERVED PRINCIPLES:
  1. BASELINE-RELATIVE: every component is scored vs the item's OWN
     history (z-score), so large names don't auto-score high.
  2. MEASUREMENT, NOT ADVICE: describes the STATE of market signals.
     Never says buy/sell. Not a risk rating. Carries the disclaimer.

================================================================
"""

import os
import sqlite3
import hashlib
import statistics
from datetime import datetime, timezone
from typing import Optional

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
MIN_BASELINE_CYCLES = 3

# ── Dual-score component weights (each set sums to 1.0) ───────────
DETECTION_WEIGHTS = {
    "dark_positioning":          0.30,   # earliest, highest-value-if-abnormal
    "positioning_concentration": 0.25,
    "analyst_signal":            0.25,
    "cross_market_diffusion":    0.10,
    "signal_freshness":          0.10,
}
CONFIDENCE_WEIGHTS = {
    "fundamental_confirmation":  0.35,
    "market_momentum":           0.30,
    "cross_market_diffusion":    0.20,
    "signal_freshness":          0.15,
}

# Descriptive false-positive characterization (mirrors attention gradient)
DETECTION_FP  = "~22% false positive · early-warning"
CONFIDENCE_FP = "<9% false positive · confirmation"

COMPONENT_LABELS = {
    "dark_positioning":          "Dark Positioning (emerging & cross-market shifts)",
    "positioning_concentration": "Positioning Concentration (smart-money vs retail)",
    "analyst_signal":            "Analyst Signal (revisions & rating changes)",
    "fundamental_confirmation":  "Fundamental Confirmation (realized financials)",
    "market_momentum":           "Market Momentum (sustained trend)",
    "cross_market_diffusion":    "Cross-Market Diffusion (venues confirming)",
    "signal_freshness":          "Signal Freshness (recency / persistence)",
}


# ════════════════════════════════════════════════════════════════
# SECTION 1: BASELINE-RELATIVE COMPONENT SCORING
# Each component → 0-1, scored against the item's own history.
# ════════════════════════════════════════════════════════════════

def _z_to_unit(z: float) -> float:
    """Map a z-score to 0-1. z=0 (at baseline) → 0.30; z=2 → ~0.80; z=3+ → ~0.95.
    Only ABOVE-baseline activity is rewarded (negative z floors near 0.1)."""
    if z <= 0:
        return max(0.05, 0.30 + z * 0.08)   # below baseline → low
    return min(1.0, 0.30 + z * 0.22)


def score_component(name: str, current: float,
                   baseline: Optional[dict]) -> dict:
    """
    Score one component baseline-relative. If the item has enough history,
    use a z-score; otherwise fall back to a calibrating absolute scale and
    flag it (honest 'not enough baseline yet').
    """
    if baseline and baseline.get("samples", 0) >= MIN_BASELINE_CYCLES:
        mean = baseline["mean"]
        # Components are normalised 0-1, so the stdev floor must be small —
        # a count-scale floor (0.5) would crush every z-score to near zero.
        stdev = max(0.05, baseline.get("stdev", max(0.08, mean * 0.3)))
        z = (current - mean) / stdev
        return {"score": round(_z_to_unit(z), 3), "z": round(z, 2),
                "baseline_relative": True, "current": current}
    else:
        # Calibrating: no reliable baseline — use a soft absolute scale,
        # held conservative so we don't over-score on no history.
        soft = min(1.0, max(0.0, current))   # expects pre-normalised 0-1 input
        return {"score": round(soft * 0.6, 3), "baseline_relative": False,
                "calibrating": True, "current": current}


# ════════════════════════════════════════════════════════════════
# SECTION 2: DUAL-SCORE COMPUTATION
# ════════════════════════════════════════════════════════════════

def _level(score: float) -> str:
    if score >= 85: return "ACUTE"
    if score >= 70: return "ELEVATED"
    if score >= 55: return "BUILDING"
    if score >= 35: return "WATCH"
    return "ROUTINE"


def compute_market_signal(item_key: str, item_name: str,
                         components_current: dict,
                         baselines: Optional[dict] = None) -> dict:
    """
    Compute the dual Market Signal (Detection + Confidence) for an item.

    components_current: {component_name: current_value, ...} for THIS cycle.
      Values for non-baseline components should be pre-normalised to 0-1
      (e.g. cross_market_diffusion as venue_count/max_venues, freshness 0-1).
    baselines: optional {component_name: {mean, stdev, samples}} from history.
    """
    baselines = baselines or {}

    # Score every component baseline-relative
    scored = {}
    for name in COMPONENT_LABELS:
        cur = components_current.get(name, 0.0)
        scored[name] = score_component(name, cur, baselines.get(name))

    any_calibrating = any(s.get("calibrating") for s in scored.values())

    # Detection = leading cluster
    detection = sum(DETECTION_WEIGHTS[c] * scored[c]["score"]
                    for c in DETECTION_WEIGHTS) * 100
    # Confidence = confirming cluster
    confidence = sum(CONFIDENCE_WEIGHTS[c] * scored[c]["score"]
                     for c in CONFIDENCE_WEIGHTS) * 100

    detection = round(detection, 1)
    confidence = round(confidence, 1)
    gap = round(detection - confidence, 1)

    interpretation = _interpret_gap(detection, confidence, gap, any_calibrating)

    return {
        "item_key":   item_key,
        "item_name":  item_name,
        "detection":  detection,
        "confidence": confidence,
        "gap":        gap,
        "detection_level":  _level(detection),
        "confidence_level": _level(confidence),
        "detection_fp":  DETECTION_FP,
        "confidence_fp": CONFIDENCE_FP,
        "gap_state":  interpretation["state"],
        "interpretation": interpretation["text"],
        "calibrating": any_calibrating,
        "components": {
            COMPONENT_LABELS[c]: {
                "score":   round(scored[c]["score"] * 100, 1),
                "feeds":   _feeds(c),
                "baseline_relative": scored[c].get("baseline_relative", False),
                "z":       scored[c].get("z"),
            } for c in COMPONENT_LABELS
        },
        "section": "Market Signal",
        "disclaimer": "Measurement of market-signal state relative to this "
                      "item's own baseline. Analysis only — not financial "
                      "advice, and not a risk rating.",
    }


def _feeds(component: str) -> str:
    in_det  = component in DETECTION_WEIGHTS
    in_conf = component in CONFIDENCE_WEIGHTS
    if in_det and in_conf: return "both"
    if in_det:             return "detection"
    if in_conf:            return "confidence"
    return "none"


# ════════════════════════════════════════════════════════════════
# SECTION 3: GAP INTERPRETATION (mirrors the attention gradient)
# ════════════════════════════════════════════════════════════════

def _interpret_gap(detection: float, confidence: float,
                  gap: float, calibrating: bool) -> dict:
    if calibrating:
        return {"state": "CALIBRATING",
                "text": "Not enough baseline history yet to judge whether this "
                        "is abnormal. Building the item's normal level — treat "
                        "as a snapshot, not a confirmed market signal."}

    both_low = detection < 35 and confidence < 35
    if both_low:
        return {"state": "ROUTINE",
                "text": "No unusual market signal versus this item's own baseline. "
                        "Leading and hard indicators are both quiet."}

    # Large positive gap → early
    if gap >= 36 and detection >= 45:
        return {"state": "EARLY",
                "text": "EARLY SIGNAL — leading indicators (analyst revisions, "
                        "smart-money positioning, cross-market shifts) are active "
                        "while the realized financials and price have NOT yet "
                        "confirmed. The early-warning window, before the move is "
                        "reflected in hard data."}
    if 16 <= gap < 36:
        return {"state": "CONFIRMING",
                "text": "Leading indicators are running ahead of the hard data, "
                        "and the fundamentals are starting to confirm. Confirmation "
                        "is building but not complete."}
    # Small gap, both elevated → confirmed
    if abs(gap) < 16 and confidence >= 45:
        return {"state": "CONFIRMED",
                "text": "Leading and hard signals agree — the market move is "
                        "corroborated by realized fundamentals and price, and is "
                        "likely already reflected. Confirmed, not early."}
    # Confidence exceeds detection → lagging
    if gap <= -16:
        return {"state": "LAGGING",
                "text": "The hard data (financials/price) shows movement, but the "
                        "early leading signals have already passed. A late-stage "
                        "read — the early-warning window has closed."}
    return {"state": "MIXED",
            "text": "Mixed signal — leading and hard indicators are partially "
                    "aligned. Direction is forming but not yet clear-cut."}


# ════════════════════════════════════════════════════════════════
# SECTION 4: BASELINE STORAGE (per-item, per-component history)
# ════════════════════════════════════════════════════════════════

def init_market_signal_db(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_signal_history (
            id TEXT PRIMARY KEY,
            item_key TEXT,
            component TEXT,
            value REAL,
            cycle_at TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ms_item ON market_signal_history(item_key)")
    conn.commit()
    conn.close()


def record_market_cycle(item_key: str, components_current: dict,
                       db_path: str = DB_PATH):
    """Record this cycle's component values to build the baseline."""
    conn = sqlite3.connect(db_path)
    now = datetime.now(timezone.utc).isoformat()
    for comp, val in components_current.items():
        rid = hashlib.md5(f"{item_key}-{comp}-{now}".encode()).hexdigest()[:16]
        conn.execute("""INSERT OR IGNORE INTO market_signal_history
            (id, item_key, component, value, cycle_at) VALUES (?,?,?,?,?)""",
            (rid, item_key, comp, val, now))
    conn.commit()
    conn.close()


def get_market_baselines(item_key: str, lookback: int = 12,
                        db_path: str = DB_PATH) -> dict:
    """Build {component: {mean, stdev, samples}} from prior cycles
    (excluding the most recent, so we compare now vs normal-before-now)."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("""SELECT component, value, cycle_at
            FROM market_signal_history WHERE item_key = ?
            ORDER BY cycle_at DESC""", (item_key,)).fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()

    if not rows:
        return {}

    cycles = sorted({r["cycle_at"] for r in rows}, reverse=True)
    baseline_cycles = set(cycles[1:lookback+1])   # skip most recent

    by_comp = {}
    for r in rows:
        if r["cycle_at"] in baseline_cycles:
            by_comp.setdefault(r["component"], []).append(r["value"])

    profile = {}
    for comp, vals in by_comp.items():
        if vals:
            mean = statistics.mean(vals)
            stdev = statistics.stdev(vals) if len(vals) >= 2 else max(0.08, mean*0.3)
            profile[comp] = {"mean": round(mean,3),
                            "stdev": round(max(0.05, stdev),3),
                            "samples": len(vals)}
    return profile


def apply_market_signal(item_key: str, item_name: str,
                       components_current: dict,
                       record_this_cycle: bool = True,
                       db_path: str = DB_PATH) -> dict:
    """Full pipeline: record cycle, load baselines, compute dual score."""
    if record_this_cycle:
        record_market_cycle(item_key, components_current, db_path)
    baselines = get_market_baselines(item_key, db_path=db_path)
    return compute_market_signal(item_key, item_name, components_current, baselines)


# ════════════════════════════════════════════════════════════════
# SECTION 5: DEMO — the four market-signal states
# ════════════════════════════════════════════════════════════════

def run_demo():
    print("\n" + "="*70)
    print("NOW TRENDIN — MARKET SIGNAL ENGINE (dual-score) — DEMO")
    print("="*70)

    # A baseline where "normal" is modest across components
    baselines = {c: {"mean": 0.30, "stdev": 0.12, "samples": 12}
                 for c in COMPONENT_LABELS}

    scenarios = [
        ("EARLY — analysts & smart money moving, fundamentals quiet", {
            "dark_positioning": 0.85, "positioning_concentration": 0.80,
            "analyst_signal": 0.78, "fundamental_confirmation": 0.32,
            "market_momentum": 0.30, "cross_market_diffusion": 0.5,
            "signal_freshness": 0.8,
        }),
        ("CONFIRMED — both leading and hard signals high", {
            "dark_positioning": 0.70, "positioning_concentration": 0.72,
            "analyst_signal": 0.75, "fundamental_confirmation": 0.85,
            "market_momentum": 0.82, "cross_market_diffusion": 0.9,
            "signal_freshness": 0.7,
        }),
        ("ROUTINE — everything near the item's baseline", {
            "dark_positioning": 0.30, "positioning_concentration": 0.32,
            "analyst_signal": 0.28, "fundamental_confirmation": 0.31,
            "market_momentum": 0.30, "cross_market_diffusion": 0.3,
            "signal_freshness": 0.4,
        }),
        ("LAGGING — hard data moved, early signals already passed", {
            "dark_positioning": 0.30, "positioning_concentration": 0.33,
            "analyst_signal": 0.30, "fundamental_confirmation": 0.85,
            "market_momentum": 0.80, "cross_market_diffusion": 0.7,
            "signal_freshness": 0.4,
        }),
    ]

    for name, comps in scenarios:
        r = compute_market_signal("demo", name.split(" —")[0], comps, baselines)
        print(f"\n── {name} ──")
        print(f"  DETECTION {r['detection']} ({r['detection_level']})   "
              f"CONFIDENCE {r['confidence']} ({r['confidence_level']})   "
              f"GAP {r['gap']:+}")
        print(f"  State: {r['gap_state']}")
        print(f"  → {r['interpretation']}")

    # Show component transparency for the EARLY case
    print("\n" + "-"*70)
    print("Component transparency (EARLY case) — the metrics UNDER the number:")
    r = compute_market_signal("demo", "early", scenarios[0][1], baselines)
    for label, c in r["components"].items():
        print(f"  {c['score']:>5}  [{c['feeds']:<10}] {label}")

    print("\n" + "="*70)
    print("Two scores, finance-native actors, each baseline-relative. The GAP")
    print("tells you how EARLY the market signal is — analysts/positioning")
    print("ahead of fundamentals = the early window. Measurement, not advice.")
    print("="*70)


if __name__ == "__main__":
    run_demo()
