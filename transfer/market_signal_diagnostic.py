"""
market_signal_diagnostic.py — LIVE Market Signal diagnostic agent (read-only)
=============================================================================
Devoted agent for MARKET SIGNAL scoring calibration. It makes the engine explain
itself for one instrument: how much baseline history each of the 7 components
actually used, whether the 0.05 stdev floor is doing the work, which inputs are
real, and whether the "unusual" deviation flag contradicts the tier.

Origin: read-only harness from the diagnostic review (06/17/26), now WIRED to live
data — `market_signal_history` (per-component baselines) + the risk/market score
store — and using the engine's REAL Detection/Confidence weights (no guesses).

INTEGRITY: instrumentation, never a scorer. It writes nothing and changes no score.
Its mission is to keep every Market Signal a DEFENSIBLE read of real data — so a
cold-start instrument (e.g. SPCX, public since 2026-06-12) is reported as
"baseline forming", never as a confident ROUTINE the data can't support.

VERDICTS: VALID | INSUFFICIENT_HISTORY | DATA_GAP | CONTRADICTION
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import math
import statistics

# Real values, read from the engine at runtime (see _load_engine_config).
BASELINE_STDEV_FLOOR = 0.05
MIN_HISTORY_OK       = 30
MIN_HISTORY_FORMING  = 10
COMPONENTS = {
    "dark_positioning": "leading", "positioning_concentration": "leading",
    "analyst_signal": "leading", "fundamental_confirmation": "confirming",
    "market_momentum": "confirming", "cross_market_diffusion": "both",
    "signal_freshness": "both",
}
DETECTION_WEIGHTS: Optional[dict] = None    # filled from market_signal_engine
CONFIDENCE_WEIGHTS: Optional[dict] = None
QUIET_TIERS = {"ROUTINE", "DORMANT"}


@dataclass
class ComponentSeries:
    history: list
    current: Optional[float]

@dataclass
class InstrumentInput:
    symbol: str
    components: dict
    reported_detection: float
    reported_confidence: float
    reported_tier: str
    pct_vs_baseline: Optional[float] = None
    flagged_unusual: bool = False
    leverage: Optional[float] = None
    signals: Optional[int] = None


def _load_engine_config():
    """Pull the REAL weights + floor + min-cycles from the live engine (verified,
    not hardcoded guesses)."""
    global DETECTION_WEIGHTS, CONFIDENCE_WEIGHTS, BASELINE_STDEV_FLOOR
    try:
        import market_signal_engine as mse
        DETECTION_WEIGHTS = dict(mse.DETECTION_WEIGHTS)
        CONFIDENCE_WEIGHTS = dict(mse.CONFIDENCE_WEIGHTS)
    except Exception:
        pass


def load_diagnostic_input(symbol: str) -> InstrumentInput:
    """Wire to live data: per-component baseline history from market_signal_history
    + the reported market score from the risk store."""
    import gravitational_anomaly_detector as g
    _load_engine_config()
    raw = (symbol or "").strip()
    conn = g.get_db(g.DB_PATH)
    # resolve the item_key used in market_signal_history (risk key form)
    candidates = [raw, raw.lower(), raw.lower().replace(" ", "_")]
    try:
        if getattr(g, "_RISK_AVAILABLE", False):
            tkr, disp = g.risk.resolve_ticker(raw)
            if disp:
                candidates += [disp, disp.lower(), disp.lower().replace(" ", "_")]
    except Exception:
        pass
    item_key, rows = None, []
    try:
        for k in dict.fromkeys(candidates):
            r = conn.execute("SELECT component, value, cycle_at FROM market_signal_history "
                             "WHERE item_key = ? ORDER BY cycle_at", (k,)).fetchall()
            if r:
                item_key, rows = k, r
                break
    except Exception:
        rows = []

    series = {}
    for name in COMPONENTS:
        vals = [(rw["cycle_at"], rw["value"]) for rw in rows if rw["component"] == name]
        vals.sort()
        hist = [v for _, v in vals]
        current = hist[-1] if hist else None
        # engine baseline skips the most recent cycle; mirror that for the history set
        series[name] = ComponentSeries(history=hist[:-1] if len(hist) > 1 else hist, current=current)

    # reported market score from the risk store
    det = conf = 0.0
    tier = "ROUTINE"
    pct = None
    unusual = False
    lev = sigs = None
    try:
        d = g.risk.get_risk_scores(g.DB_PATH, 200)
        match = None
        for rr in d.get("results", []):
            rk = str(rr.get("risk_topic", "")).lower()
            if rk == (item_key or raw).lower() or raw.lower() in (str(rr.get("risk_display", "")).lower()):
                match = rr
                break
        if match:
            mg = match.get("market_gradient") or {}
            det = float(mg.get("detection", match.get("detection_score", 0)) or 0)
            conf = float(mg.get("confidence", match.get("confidence_score", 0)) or 0)
            tier = (mg.get("tier") or match.get("risk_stage") or "ROUTINE").upper()
            pct = match.get("percent_delta") if match.get("percent_delta") is not None else match.get("abnormality")
            cls = (match.get("classification") or "").upper()
            bs = (match.get("baseline_status") or "").upper()
            unusual = cls in ("UNUSUAL", "ELEVATED") or bs in ("SPIKE_VS_SELF", "ELEVATED_VS_SELF")
            lev = (mg.get("leverage_health"))
            sigs = match.get("total_signals")
    except Exception:
        pass
    finally:
        conn.close()

    return InstrumentInput(symbol=raw, components=series,
                           reported_detection=round(det), reported_confidence=round(conf),
                           reported_tier=tier, pct_vs_baseline=pct, flagged_unusual=unusual,
                           leverage=lev, signals=sigs)


@dataclass
class ComponentReport:
    name: str; role: str; n_history: int
    mean: Optional[float]; std_raw: Optional[float]; std_used: Optional[float]
    z: Optional[float]; floor_binding: bool; status: str

@dataclass
class Report:
    symbol: str
    components: list = field(default_factory=list)
    median_depth: int = 0
    floor_binding_count: int = 0
    missing: list = field(default_factory=list)
    contradiction: bool = False
    recompute: Optional[dict] = None
    verdict: str = "VALID"
    issues: list = field(default_factory=list)
    recommendation: str = ""


def _finite(x): return isinstance(x, (int, float)) and math.isfinite(x)


def _diagnose_component(name, role, s: ComponentSeries) -> ComponentReport:
    hist = [h for h in s.history if _finite(h)]
    n = len(hist)
    if not _finite(s.current):
        return ComponentReport(name, role, n, None, None, None, None, False, "MISSING")
    if n == 0:
        return ComponentReport(name, role, 0, None, None, None, None, True, "DEGENERATE")
    mean = statistics.fmean(hist)
    std_raw = statistics.pstdev(hist) if n >= 2 else 0.0
    std_used = max(std_raw, BASELINE_STDEV_FLOOR)
    z = (s.current - mean) / std_used
    fb = std_raw < BASELINE_STDEV_FLOOR
    status = "DEGENERATE" if n < MIN_HISTORY_FORMING else ("THIN" if n < MIN_HISTORY_OK else "OK")
    return ComponentReport(name, role, n, mean, std_raw, std_used, z, fb, status)


def diagnose(inp: InstrumentInput) -> Report:
    r = Report(symbol=inp.symbol)
    for name, role in COMPONENTS.items():
        s = inp.components.get(name, ComponentSeries(history=[], current=None))
        cr = _diagnose_component(name, role, s)
        r.components.append(cr)
        if cr.status == "MISSING":
            r.missing.append(name)
        if cr.floor_binding and cr.status != "MISSING":
            r.floor_binding_count += 1
    depths = [c.n_history for c in r.components if c.status != "MISSING"]
    r.median_depth = int(statistics.median(depths)) if depths else 0
    r.contradiction = bool(inp.flagged_unusual and inp.reported_tier.upper() in QUIET_TIERS)
    if DETECTION_WEIGHTS and CONFIDENCE_WEIGHTS:
        r.recompute = _recompute(r.components, inp)

    if len(r.missing) >= 4:
        r.verdict = "DATA_GAP"
        r.issues.append(f"{len(r.missing)} of 7 component sources missing: {', '.join(r.missing)}")
    elif r.median_depth < MIN_HISTORY_FORMING:
        r.verdict = "INSUFFICIENT_HISTORY"
        r.issues.append(f"median baseline depth {r.median_depth} pts (< {MIN_HISTORY_FORMING}); "
                        f"z-scores are dominated by the {BASELINE_STDEV_FLOOR} floor, not measured.")
    elif r.median_depth < MIN_HISTORY_OK:
        r.verdict = "INSUFFICIENT_HISTORY"
        r.issues.append(f"median baseline depth {r.median_depth} pts (< {MIN_HISTORY_OK}); baseline still forming.")
    elif r.contradiction:
        r.verdict = "CONTRADICTION"
    else:
        r.verdict = "VALID"

    if r.contradiction and r.verdict != "CONTRADICTION":
        r.issues.append(f"UNUSUAL/+{inp.pct_vs_baseline}% baseline flag while tier = {inp.reported_tier} "
                        f"(deviation detector and tier classifier disagree).")
    if r.missing and r.verdict != "DATA_GAP":
        r.issues.append(f"partial source gap: {', '.join(r.missing)}")
    if r.floor_binding_count and "INSUFFICIENT_HISTORY" not in r.verdict:
        r.issues.append(f"stdev floor binding on {r.floor_binding_count}/7 components "
                        f"(baseline near-flat — small moves look extreme or vanish).")
    r.recommendation = _recommend(r.verdict, inp)
    return r


def _recompute(components, inp) -> dict:
    zmap = {c.name: (c.z if c.z is not None else 0.0) for c in components}
    det = sum(zmap[n] * w for n, w in DETECTION_WEIGHTS.items() if n in zmap)
    con = sum(zmap[n] * w for n, w in CONFIDENCE_WEIGHTS.items() if n in zmap)
    return {"detection_from_z": round(det, 3), "confidence_from_z": round(con, 3),
            "reported_detection": inp.reported_detection, "reported_confidence": inp.reported_confidence,
            "note": "z-space, pre-squash — directional cross-check (engine applies a sigmoid + scale)."}


def _recommend(verdict, inp) -> str:
    if verdict == "INSUFFICIENT_HISTORY":
        return ("Suppress the confident tier: emit 'INSUFFICIENT HISTORY · baseline forming' instead of "
                "ROUTINE, and optionally score cross-sectionally vs the sector / IPO cohort during the "
                "cold-start window so a real move can still surface. (See the proposed engine guard.)")
    if verdict == "DATA_GAP":
        return "Do not score. Hold the instrument until its component sources populate."
    if verdict == "CONTRADICTION":
        return "Reconcile the deviation flag and the tier — don't show 'UNUSUAL' next to a 'quiet' narrative."
    return "Score is supportable on baseline depth and provenance grounds."


def to_dict(r: Report) -> dict:
    """Structured output for the /diagnostic/market endpoint."""
    return {
        "symbol": r.symbol, "verdict": r.verdict,
        "median_baseline_depth": r.median_depth,
        "floor_binding": f"{r.floor_binding_count}/7",
        "missing_sources": r.missing,
        "tier_deviation_clash": r.contradiction,
        "components": [{"name": c.name, "role": c.role, "n_history": c.n_history,
                        "z": round(c.z, 3) if c.z is not None else None,
                        "floor_binding": c.floor_binding, "status": c.status} for c in r.components],
        "recompute": r.recompute,
        "issues": r.issues, "recommendation": r.recommendation,
    }


def run(symbol: str) -> dict:
    return to_dict(diagnose(load_diagnostic_input(symbol)))
