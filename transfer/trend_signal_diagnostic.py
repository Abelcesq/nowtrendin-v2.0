"""
trend_signal_diagnostic.py — LIVE Trend Signal (Gradient Score) diagnostic agent
=================================================================================
Twin of market_signal_diagnostic.py, devoted to the GRADIENT SCORE. Read-only. It
makes the engine explain itself for one topic and across topics, on the real
failure modes the live view surfaced:

  • SCORE SATURATION  — top topics pinned at Detection 100 (can't rank #1 vs #2).
  • N-DISCIPLINE      — the headline Detection/Overall must reconcile to the five
    EXTERNAL components G/I/M/D/C only; N (demand) must NEVER feed the headline.
    Reconcile is GATED to the expert pathway (mainstream/blended topics use the
    dual-pathway magnitude formula, so a G/I/M/D/C recompute doesn't apply — not
    flagging those avoids false 'leak' alarms).
  • WHAT-IF-N INVERTION — the separate demand-inclusive read must not move DOWN
    when demand (N) is high.
  • CROSS-TOPIC DISTRIBUTION — is Confidence actually separating topics, or
    collapsing many onto one value?

INTEGRITY: instrumentation, never a scorer. Writes nothing. Mission: keep every
Gradient Score a defensible, N-free, discriminating read — the basis of the
product's credibility.

VERDICTS: VALID | SATURATED | FROZEN | UNDOCUMENTED_INPUT | WHATIF_N_INVERTED | DATA_GAP
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import math
import statistics

COMPONENTS = {"G": "gradient_strength", "I": "inertia", "M": "medium_sequence",
              "D": "dark_matter", "C": "confidence_decay"}
# Confirmed from compute_gradient_score (detection + overall). Confidence weights
# are intentionally left None (the live runtime blend is ambiguous between two
# documented vectors — we will not hardcode a number we can't verify).
OVERALL_WEIGHTS   = {"G": 0.30, "I": 0.25, "M": 0.20, "D": 0.15, "C": 0.10}
DETECTION_WEIGHTS = {"G": 0.40, "D": 0.25, "I": 0.20, "M": 0.10, "C": 0.05}
CONFIDENCE_WEIGHTS: Optional[dict] = None

SCORE_CAP = 100.0
SATURATION_EPS = 0.02
FREEZE_MIN_CYCLES = 6
RECONCILE_TOL = 8.0          # z/pathway calibration adds slack; only a large gap = leak
LOW_HEADROOM_PCT = 0.05
N_HIGH = 70.0


@dataclass
class ComponentState:
    value: Optional[float]; cap: float = 100.0; floor: float = 0.0

@dataclass
class TopicInput:
    topic: str
    components: dict
    reported_detection: float
    reported_confidence: float
    reported_overall: float
    recent_detection: list = field(default_factory=list)
    recent_overall: list = field(default_factory=list)
    n_value: Optional[float] = None
    det_plus_n: Optional[float] = None
    conf_plus_n: Optional[float] = None
    detection_pathway: str = "expert"   # expert | mainstream | blended (gates reconcile)


def load_diagnostic_input(topic: str) -> TopicInput:
    """Wire to live data: latest velocity_scores row (components + scores + pathway),
    the recent score series, N, and the demand-inclusive 'Now-Trending Gradient'."""
    import gravitational_anomaly_detector as g
    key = g._topic_key(topic) if hasattr(g, "_topic_key") else topic.lower().replace(" ", "_")
    conn = g.get_db(g.DB_PATH)
    try:
        row = conn.execute("SELECT * FROM velocity_scores WHERE topic_key=? ORDER BY scored_at DESC LIMIT 1",
                           (key,)).fetchone()
        hist = conn.execute("SELECT detection_score, overall_score FROM velocity_scores "
                            "WHERE topic_key=? ORDER BY scored_at DESC LIMIT 12", (key,)).fetchall()
    finally:
        conn.close()
    if not row:
        return TopicInput(topic=topic, components={}, reported_detection=0,
                          reported_confidence=0, reported_overall=0)
    s = dict(row)
    comp = {
        "G": ComponentState(value=s.get("gradient_strength")),
        "I": ComponentState(value=s.get("inertia_score")),
        "M": ComponentState(value=s.get("platform_diversity")),
        "D": ComponentState(value=s.get("dark_matter_score")),
        "C": ComponentState(value=s.get("confidence_decay")),
    }
    det = round(float(s.get("detection_score") or 0))
    conf = round(float(s.get("confidence_score") or 0))
    ovr = round(float(s.get("overall_score") or 0))
    n = s.get("nowtrendin_score")
    n = round(float(n)) if n is not None else None
    # demand-inclusive what-if read (computed the same way the serve path does)
    ntd = ntc = None
    try:
        _d, _c, _ = g._now_trending_gradient(s.get("detection_score"), s.get("confidence_score"),
                                              s.get("nowtrendin_score"), s.get("total_mentions"))
        ntd = round(_d) if _d is not None else None
        ntc = round(_c) if _c is not None else None
    except Exception:
        pass
    recent_det = [round(float(h["detection_score"] or 0)) for h in reversed(hist)]
    recent_ovr = [round(float(h["overall_score"] or 0)) for h in reversed(hist)]
    return TopicInput(topic=s.get("topic_display") or topic, components=comp,
                      reported_detection=det, reported_confidence=conf, reported_overall=ovr,
                      recent_detection=recent_det, recent_overall=recent_ovr,
                      n_value=n, det_plus_n=ntd, conf_plus_n=ntc,
                      detection_pathway=(s.get("detection_pathway") or "expert").lower())


@dataclass
class ComponentReport:
    code: str; name: str; value: Optional[float]; cap: float
    headroom_pct: Optional[float]; status: str

@dataclass
class Report:
    topic: str
    components: list = field(default_factory=list)
    score_saturated: list = field(default_factory=list)
    missing: list = field(default_factory=list)
    detection_frozen: int = 0
    overall_frozen: int = 0
    reconcile: Optional[dict] = None
    whatif_n: Optional[dict] = None
    pathway: str = "expert"
    verdict: str = "VALID"
    issues: list = field(default_factory=list)
    recommendation: str = ""


def _finite(x): return isinstance(x, (int, float)) and math.isfinite(x)

def _frozen_run(series):
    if len(series) < 2:
        return 0
    last, run = series[-1], 1
    for v in reversed(series[:-1]):
        if v == last:
            run += 1
        else:
            break
    return run if run >= 2 else 0

def _diagnose_component(code, name, s: ComponentState) -> ComponentReport:
    if not _finite(s.value):
        return ComponentReport(code, name, None, s.cap, None, "MISSING")
    rng = max(s.cap - s.floor, 1e-9)
    headroom = (s.cap - s.value) / rng
    if s.value >= s.cap - SATURATION_EPS * rng:
        status = "SATURATED"
    elif s.value <= s.floor + SATURATION_EPS * rng:
        status = "FLOORED"
    elif headroom < LOW_HEADROOM_PCT:
        status = "LOW_HEADROOM"
    else:
        status = "OK"
    return ComponentReport(code, name, s.value, s.cap, headroom, status)

def _reconcile(inp: TopicInput) -> dict:
    vals = {c: (inp.components[c].value if c in inp.components and _finite(inp.components[c].value) else 0.0)
            for c in COMPONENTS}
    clamp = lambda x: max(0.0, min(SCORE_CAP, x))
    det = clamp(sum(vals[c] * w for c, w in DETECTION_WEIGHTS.items()))
    ovr = clamp(sum(vals[c] * w for c, w in OVERALL_WEIGHTS.items()))
    return {"detection_recompute": round(det, 2), "detection_reported": inp.reported_detection,
            "detection_gap": round(inp.reported_detection - det, 2),
            "overall_recompute": round(ovr, 2), "overall_reported": inp.reported_overall,
            "overall_gap": round(inp.reported_overall - ovr, 2)}

def _whatif_n(inp: TopicInput) -> Optional[dict]:
    if inp.n_value is None or inp.det_plus_n is None:
        return None
    inverted = inp.n_value >= N_HIGH and inp.det_plus_n < inp.reported_detection
    return {"n": inp.n_value, "det": inp.reported_detection, "det_plus_n": inp.det_plus_n,
            "delta": round(inp.det_plus_n - inp.reported_detection, 2), "inverted": inverted}


def diagnose(inp: TopicInput) -> Report:
    r = Report(topic=inp.topic, pathway=inp.detection_pathway)
    for code, name in COMPONENTS.items():
        cr = _diagnose_component(code, name, inp.components.get(code, ComponentState(value=None)))
        r.components.append(cr)
        if cr.status == "MISSING":
            r.missing.append(code)
    for label, val in (("detection", inp.reported_detection), ("confidence", inp.reported_confidence),
                       ("overall", inp.reported_overall)):
        if _finite(val) and val >= SCORE_CAP - SATURATION_EPS * SCORE_CAP:
            r.score_saturated.append(label)
    r.detection_frozen = _frozen_run(inp.recent_detection)
    r.overall_frozen = _frozen_run(inp.recent_overall)
    r.reconcile = _reconcile(inp)
    r.whatif_n = _whatif_n(inp)

    # Leak = headline ABOVE what G/I/M/D/C justify. ONLY meaningful on the expert
    # pathway (mainstream/blended use the magnitude formula, not this recompute).
    expert = inp.detection_pathway == "expert"
    leak = expert and ((r.reconcile["detection_gap"] > RECONCILE_TOL) or (r.reconcile["overall_gap"] > RECONCILE_TOL))
    frozen = r.detection_frozen >= FREEZE_MIN_CYCLES or r.overall_frozen >= FREEZE_MIN_CYCLES
    comp_sat = any(c.status in ("SATURATED", "FLOORED") for c in r.components)
    score_sat = bool(r.score_saturated)
    whatif_bad = bool(r.whatif_n and r.whatif_n["inverted"])

    if len(r.missing) >= 3:
        r.verdict = "DATA_GAP"
        r.issues.append(f"{len(r.missing)} of 5 components missing: {', '.join(r.missing)}")
    elif leak:
        r.verdict = "UNDOCUMENTED_INPUT"
        r.issues.append(f"[expert pathway] headline Detection {inp.reported_detection} vs G/I/M/D/C recompute "
                        f"{r.reconcile['detection_recompute']} (gap {r.reconcile['detection_gap']:+}); "
                        f"a term outside the five components may be feeding the HEADLINE — verify N is excluded.")
    elif (comp_sat or score_sat) and frozen:
        r.verdict = "SATURATED"
    elif frozen:
        r.verdict = "FROZEN"
    elif comp_sat or score_sat:
        r.verdict = "SATURATED"
    elif whatif_bad:
        r.verdict = "WHATIF_N_INVERTED"
    else:
        r.verdict = "VALID"

    if score_sat:
        r.issues.append(f"final score pinned at ceiling: {', '.join(r.score_saturated)} = {SCORE_CAP:g} "
                        f"(cannot rank top topics against each other).")
    if comp_sat:
        pins = [f"{c.code}({c.name}) {c.value:g}/{c.cap:g}" for c in r.components if c.status in ("SATURATED", "FLOORED")]
        r.issues.append("components pinned — no discrimination: " + "; ".join(pins))
    if r.detection_frozen >= FREEZE_MIN_CYCLES:
        r.issues.append(f"Detection frozen at {inp.recent_detection[-1]} for {r.detection_frozen} cycles.")
    if whatif_bad:
        w = r.whatif_n
        r.issues.append(f"what-if-N inverted: N={w['n']:g} (high) yet Detection+N {w['det_plus_n']:g} < "
                        f"headline {w['det']:g} (Δ {w['delta']:+}). Folding in demand should not lower the score.")
    r.recommendation = _recommend(r.verdict)
    return r


def _recommend(verdict) -> str:
    if verdict == "UNDOCUMENTED_INPUT":
        return ("Governance check: confirm N is excluded from the HEADLINE gradient (non-negotiable) and no "
                "other term feeds Detection/Overall on the expert pathway. Reconcile to G/I/M/D/C or document it.")
    if verdict in ("SATURATED", "FROZEN"):
        return ("Restore dynamic range: soften the binding ceilings (component caps AND the final-score cap) "
                "so the hottest topics separate instead of all pinning at 100 — a soft/log compression near the top.")
    if verdict == "WHATIF_N_INVERTED":
        return ("Fix or retire the what-if-N read: folding in high demand currently LOWERS the score, which is "
                "unexplainable to an institutional user. Make the blend monotonic in N, or remove the block.")
    if verdict == "DATA_GAP":
        return "Do not score. Hold the topic until its components populate."
    return "Score is supportable on saturation, reconciliation, what-if-N, and provenance grounds."


def diagnose_distribution(rows: list) -> dict:
    """rows: [(topic, detection, confidence)] — is the engine separating topics?"""
    dets = [d for _, d, _ in rows]
    cons = [c for _, _, c in rows]
    n = len(rows)
    ceiling = [t for t, d, _ in rows if d >= SCORE_CAP - SATURATION_EPS * SCORE_CAP]
    def collisions(vals):
        seen = {}
        for v in vals:
            seen[v] = seen.get(v, 0) + 1
        return sorted(((v, c) for v, c in seen.items() if c >= 2), key=lambda x: -x[1])
    det_sd = round(statistics.pstdev(dets), 2) if n >= 2 else 0.0
    con_sd = round(statistics.pstdev(cons), 2) if n >= 2 else 0.0
    con_coll = collisions(cons)
    issues = []
    if ceiling:
        issues.append(f"Detection ceiling collision: {', '.join(map(str, ceiling))} all at {SCORE_CAP:g} — top topics unrankable.")
    if con_coll:
        v, c = con_coll[0]
        issues.append(f"Confidence collision: value {v:g} shared by {c} topics (under-discriminating).")
    if n >= 6 and con_sd < 0.6 * det_sd:
        issues.append(f"Confidence spread ({con_sd}) < 60% of Detection spread ({det_sd}) — Confidence barely separates topics.")
    return {"topics": n, "detection_sd": det_sd, "confidence_sd": con_sd,
            "ceiling_pinned": ceiling, "confidence_collisions": con_coll[:5], "issues": issues,
            "recommendation": "Re-scale Confidence so volume/precision differences move it; identical "
                              "Confidence across very-different topics is the symptom to kill."}


def to_dict(r: Report) -> dict:
    return {
        "topic": r.topic, "verdict": r.verdict, "detection_pathway": r.pathway,
        "score_saturated": r.score_saturated,
        "components": [{"code": c.code, "name": c.name, "value": c.value, "cap": c.cap,
                        "headroom_pct": round(c.headroom_pct * 100, 1) if c.headroom_pct is not None else None,
                        "status": c.status} for c in r.components],
        "detection_frozen_cycles": r.detection_frozen,
        "reconcile": r.reconcile, "whatif_n": r.whatif_n,
        "issues": r.issues, "recommendation": r.recommendation,
    }


def run(topic: str) -> dict:
    return to_dict(diagnose(load_diagnostic_input(topic)))

def run_distribution(limit: int = 30) -> dict:
    import gravitational_anomaly_detector as g
    conn = g.get_db(g.DB_PATH)
    try:
        rows = conn.execute(
            """SELECT v.topic_display, v.detection_score, v.confidence_score FROM velocity_scores v
               INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores GROUP BY topic_key) l
                 ON v.topic_key=l.topic_key AND v.scored_at=l.m
               ORDER BY v.detection_score DESC LIMIT ?""", (limit,)).fetchall()
    finally:
        conn.close()
    grid = [(r["topic_display"], round(float(r["detection_score"] or 0)), round(float(r["confidence_score"] or 0)))
            for r in rows]
    return diagnose_distribution(grid)
