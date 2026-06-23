"""
enterprise_intel.py — Enterprise intelligence layer for the 2.0 engine.

Ports the valuable, dormant capabilities from gradient_engine_extensions.py
(which was bound to the v1 5-component SQLite prototype) onto the live 2.0
engine: the 7-component G·I·M·D·C·P·N model on Postgres.

Provides (read-only, computed on demand from the latest stored score):
  • Methodology versioning   — a reproducible hash of the exact weights/thresholds
  • Per-component audit        — value × weight contribution to each of the 3 scores
  • Scenario projections       — response-surface "what would move this score and
                                 by how much" (NOT predictions — explicit framing)

Wired via build_router(get_db, db_path); the engine includes the returned router.
No new tables — everything derives from velocity_scores, so there is no migration
or write path (safe to add during a freeze).
"""
import hashlib
import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException


def _official_scores(row: dict, calibrate_fn=None):
    """The scores the platform actually displays come from serve-time
    calibration + AI-taxonomy override. Prefer the precomputed serve_payload;
    otherwise compute live via the injected calibrate_fn (the engine's
    _calibrate_score_fields). Returns (scores_dict_or_None, ai_override_bool)."""
    s = None
    payload = row.get("serve_payload")
    if payload:
        try:
            s = json.loads(payload)
        except Exception:
            s = None
    if s is None and calibrate_fn is not None:
        try:
            s = calibrate_fn(dict(row))
        except Exception:
            s = None
    if s is None:
        return None, False
    scores = {
        "overall": s.get("overall_score"),
        "detection": s.get("detection_score"),
        "confidence": s.get("confidence_score"),
    }
    return scores, bool(s.get("ai_tier"))

# ── The 2.0 model — SIX external components drive the composite. ──────
# N (internal demand) is tracked & displayed but DELIBERATELY excluded from the
# weighted score to keep the Gradient Score a clean external-world instrument
# (no user-demand feedback loop). COMPONENTS = all shown; COMPOSITE = scored.
COMPONENTS = ["G", "I", "M", "D", "C", "P", "N"]
COMPOSITE_COMPONENTS = ["G", "I", "M", "D", "C", "P"]
COMPONENT_COL = {
    "G": "gradient_strength", "I": "inertia_score", "M": "platform_diversity",
    "D": "dark_matter_score", "C": "confidence_decay", "P": "persistence_score",
    "N": "nowtrendin_score",
}
COMPONENT_LABEL = {
    "G": "Gradient Strength", "I": "Inertia", "M": "Platform Diversity",
    "D": "Dark Matter", "C": "Confidence Decay", "P": "Persistence",
    "N": "Now Trending (internal demand — separate signal, not in composite)",
}
# 6-component weights renormalized to sum to 1.0 (N removed from the composite),
# imported from the single source of truth (scoring_weights.py). N:0.0 is appended
# only for the methodology DISPLAY table (N is shown as a separate signal, never in
# the composite). Fallback is value-identical if the import fails.
try:
    from scoring_weights import (
        WEIGHTS_OVERALL as _SW_O, WEIGHTS_DETECTION as _SW_D, WEIGHTS_CONFIDENCE as _SW_C,
    )
    W_OVERALL    = {**_SW_O, "N": 0.0}
    W_DETECTION  = {**_SW_D, "N": 0.0}
    W_CONFIDENCE = {**_SW_C, "N": 0.0}
except Exception:
    W_OVERALL    = {"G": .244, "I": .222, "M": .167, "D": .133, "C": .078, "P": .156, "N": 0.0}
    W_DETECTION  = {"G": .375, "I": .182, "M": .102, "D": .216, "C": .057, "P": .068, "N": 0.0}
    W_CONFIDENCE = {"G": .122, "I": .278, "M": .222, "D": .044, "C": .067, "P": .267, "N": 0.0}

METHODOLOGY = {
    "weights_overall":    W_OVERALL,
    "weights_detection":  W_DETECTION,
    "weights_confidence": W_CONFIDENCE,
    "thresholds": {
        "breakout_score": 85, "strong_signal_score": 70, "emerging_score": 55,
    },
    "notes": "v2.1 — 6 external components G·I·M·D·C·P (renormalized). "
             "N (internal demand) is a separate displayed signal, excluded from the composite.",
}


def methodology_version(m: dict = None) -> str:
    m = m or METHODOLOGY
    payload = json.dumps({k: v for k, v in m.items() if k != "notes"}, sort_keys=True).encode()
    return "v2-" + hashlib.sha256(payload).hexdigest()[:10]


def _recompute(c: dict, w: dict) -> float:
    # Composite uses the six external components only (N excluded by design).
    return round(min(100.0, max(0.0, sum(c[k] * w[k] for k in COMPOSITE_COMPONENTS))), 2)


def _scores(c: dict) -> dict:
    return {
        "overall":    _recompute(c, W_OVERALL),
        "detection":  _recompute(c, W_DETECTION),
        "confidence": _recompute(c, W_CONFIDENCE),
    }


def _components_from_row(row: dict) -> dict:
    return {k: float(row.get(COMPONENT_COL[k]) or 0.0) for k in COMPONENTS}


def audit_breakdown(components: dict) -> dict:
    """Per-component value × weight contribution to each score. Reproducible
    under methodology_version — the auditable attribution institutions ask for."""
    rows = []
    for k in COMPONENTS:
        v = round(components[k], 2)
        rows.append({
            "component": k,
            "label": COMPONENT_LABEL[k],
            "value": v,
            "weight_overall": W_OVERALL[k],
            "weight_detection": W_DETECTION[k],
            "weight_confidence": W_CONFIDENCE[k],
            "contribution_overall": round(v * W_OVERALL[k], 2),
            "contribution_detection": round(v * W_DETECTION[k], 2),
            "contribution_confidence": round(v * W_CONFIDENCE[k], 2),
        })
    return {"methodology_version": methodology_version(), "scores": _scores(components), "components": rows}


# ── Scenario catalog (7-component response-surface perturbations) ─────
def _clamp(x):
    return max(0.0, min(100.0, x))


def _perturb(c: dict, deltas: dict, targets: dict = None) -> dict:
    out = dict(c)
    for k, d in (deltas or {}).items():
        out[k] = _clamp(out[k] + d)
    for k, t in (targets or {}).items():
        out[k] = _clamp(t)
    return out


SCENARIO_CATALOG = [
    {"name": "mainstream_entry_48h", "deltas": {"G": -15, "M": +5, "C": -10},
     "narrative": "If '{topic}' crosses into mainstream channels within ~48h, Gradient "
                  "Strength falls (~15pt) as the niche ratio drops below threshold. "
                  "Platform spread rises but the value window closes — Overall {overall_delta:+.1f}pt."},
    {"name": "inertia_confirms", "deltas": {"I": +20, "P": +8},
     "narrative": "If two more 6-hour windows show ≥10% growth, Inertia (+20) and Persistence "
                  "(+8) rise. Confidence weights these heavily — Confidence {confidence_delta:+.1f}pt, "
                  "the Detection/Confidence gap closes."},
    {"name": "internal_demand_surge", "deltas": {"N": +25},
     "narrative": "If in-app demand for '{topic}' spikes (more users surfacing it), the Now-Trending "
                  "component rises ~25pt. Detection {detection_delta:+.1f}pt — N is weighted 12% in "
                  "Detection, the earliest demand-side confirmation."},
    {"name": "dark_matter_surge", "targets": {"D": 75},
     "narrative": "If the first-timer ratio climbs to 40%+ over ~4 days, Dark Matter rises toward 75. "
                  "Detection {detection_delta:+.1f}pt (D is 19% of Detection) — the canonical "
                  "pre-mainstream signature of external traffic entering niche communities."},
    {"name": "persistence_builds", "deltas": {"P": +20},
     "narrative": "If '{topic}' stays elevated across more scoring cycles, Persistence rises ~20pt. "
                  "Confidence {confidence_delta:+.1f}pt (P is 24% of Confidence) — moves from "
                  "'early' toward 'confirmed trend'."},
    {"name": "signal_decay_48h", "deltas": {"I": -25, "C": -30, "P": -10},
     "narrative": "If volume drops 50%+ over 48h, Inertia (-25), Confidence Decay (-30) and "
                  "Persistence (-10) fall — the false-positive signature. Overall {overall_delta:+.1f}pt; "
                  "the score retroactively marks itself a fading spike."},
]


def compute_scenarios(components: dict, topic: str) -> list:
    orig = _scores(components)
    out = []
    for scn in SCENARIO_CATALOG:
        perturbed = _perturb(components, scn.get("deltas"), scn.get("targets"))
        proj = _scores(perturbed)
        deltas = {
            "overall_delta":    round(proj["overall"] - orig["overall"], 2),
            "detection_delta":  round(proj["detection"] - orig["detection"], 2),
            "confidence_delta": round(proj["confidence"] - orig["confidence"], 2),
        }
        out.append({
            "scenario": scn["name"],
            "perturbation": {**(scn.get("deltas") or {}), **{f"{k}→": v for k, v in (scn.get("targets") or {}).items()}},
            "original": orig,
            "projected": proj,
            **deltas,
            "narrative": scn["narrative"].format(topic=topic, **deltas),
        })
    return out


# ── Router factory (dependency-injected get_db) ──────────────────────
def build_router(get_db, db_path, calibrate_fn=None) -> APIRouter:
    router = APIRouter(prefix="/enterprise", tags=["enterprise-intel"])

    def _latest(topic_key: str) -> dict:
        conn = get_db(db_path)
        try:
            row = conn.execute(
                """
                SELECT v.* FROM velocity_scores v
                INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores
                            WHERE topic_key = ? GROUP BY topic_key) l
                  ON v.topic_key = l.topic_key AND v.scored_at = l.m
                """,
                (topic_key,),
            ).fetchone()
        finally:
            conn.close()
        if not row:
            raise HTTPException(404, f"No score for topic: {topic_key}")
        return dict(row)

    @router.get("/methodology")
    def get_methodology():
        return {
            "version": methodology_version(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            **METHODOLOGY,
        }

    @router.get("/scores/{topic_key}/audit")
    def get_audit(topic_key: str):
        row = _latest(topic_key)
        breakdown = audit_breakdown(_components_from_row(row))
        official, ai_override = _official_scores(row, calibrate_fn)
        note = (
            "Component attribution is the raw 7-component baseline. The displayed "
            "(official) scores apply serve-time calibration"
            + (" plus an AI-taxonomy tier override for this topic, so they intentionally "
               "diverge from the raw component sum." if ai_override else ".")
        )
        return {
            "topic_key": topic_key,
            "topic": row.get("topic_display", topic_key),
            "scored_at": row.get("scored_at"),
            "official_scores": official,        # what the platform displays
            "ai_taxonomy_override": ai_override,
            "reconciliation_note": note,
            **breakdown,                        # raw component attribution + recomputed scores
        }

    @router.get("/scores/{topic_key}/scenarios")
    def get_scenarios(topic_key: str):
        row = _latest(topic_key)
        comps = _components_from_row(row)
        return {
            "topic_key": topic_key,
            "topic": row.get("topic_display", topic_key),
            "scored_at": row.get("scored_at"),
            "methodology_version": methodology_version(),
            "disclaimer": "Scenarios are response-surface samples, not predictions: "
                          "what the model would output if the named component(s) changed.",
            "current": _scores(comps),
            "scenarios": compute_scenarios(comps, row.get("topic_display", topic_key)),
        }

    return router
