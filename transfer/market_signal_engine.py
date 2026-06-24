"""
================================================================
NOW TRENDIN — MARKET SIGNAL ENGINE (baseline-relative dual score)
================================================================

The Gradient-Score philosophy applied to MARKET factors, with the key upgrade
from the design review: EVERY component is scored relative to the item's OWN
history (z-score), not as an absolute magnitude — so a mega-cap doesn't auto-
score high just because it always has heavy coverage. This is the same integrity
principle that fixed the size-bias bug on the attention side.

DUAL SCORE (earliness vs certainty — the same tradeoff as attention):
  DETECTION (leading/soft)  — are informed actors moving BEFORE confirmation?
     · dark_positioning          (macro / cross-market shifts: OFR repo + stress)
     · positioning_concentration (FINRA shorts + 13F change + insider Form-4)
     · analyst_signal            (news sentiment/volume + analyst + creator/broadcast)
  CONFIDENCE (hard/realized) — does the financial reality confirm it?
     · fundamental_confirmation  (beneficiary cycle-inflection + sustainability)
     · market_momentum           (price return + valuation re-rating)
  SHARED (feed both):
     · cross_market_diffusion    (distinct venues active)
     · signal_freshness          (recency of newest signal)

GAP: Detection >> Confidence = EARLY (the window). Both high = CONFIRMED. Both
low = ROUTINE. Confidence >> Detection = LAGGING. <3 cycles = CALIBRATING.

GROUNDED IN REAL SOURCES ONLY — every component is fed from data we actually
pull (Alpha Vantage, FINRA, WhaleWisdom, Finnhub, SEC Form-4, OFR). We do NOT
include options-flow / credit-spread / price-candle components we can't source.

MEASUREMENT, NOT ADVICE. Neutral tiers describe positioning intensity, never
buy/sell. Carries the disclaimer.
================================================================
"""
import os
import math
import hashlib
import statistics
from datetime import datetime, timezone
from typing import Optional

try:
    import db_compat
except Exception:
    db_compat = None
import sqlite3
from date_utils import to_iso_date, iso_time_of, source_has_time

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

# ── Score-quarantine feature flag (mirrors signal_calibration_integration) ────
# When True: assemble_market_components returns None for positioning_concentration
# when both FINRA (short_interest) and WhaleWisdom (institutional_holdings) are
# absent, so compute_market_signal excludes it and renormalizes weights rather than
# treating the artificial 0.0 default as a real reading.
# DEFAULT = False. Flip only after Phase 2 (Wikipedia+GDELT referee) validates.
_MKT_QUARANTINE = os.getenv("SCORE_QUARANTINE_ENABLED", "false").lower() == "true"

# ── Dark-Positioning V2 feature flag (SEC 13F + Congress → positioning_concentration) ──
# When True: a ticker's held-out dark-positioning signal (positioning_intel: curated-fund
# 13F breadth + congressional net-trading), passed in via payload["dark_positioning_intel"],
# BLENDS into positioning_concentration (40% weight). DEFAULT False — the code ships inert;
# flip ONLY after the predictive backtest validates it improves (not just changes) the score.
# Non-circular: inputs are external SEC/Congress filings, independent of any Now TrendIn score.
DARK_POSITIONING_V2 = os.getenv("DARK_POSITIONING_V2", "0") == "1"
DARK_POS_WEIGHT = float(os.getenv("DARK_POS_WEIGHT", "0.4"))

MIN_BASELINE_CYCLES = 3        # below this: no usable baseline at all
# Cold-start guard (Fix #1, market diagnostic): a baseline of 3–9 cycles passes the
# MIN_BASELINE_CYCLES gate but is too thin to trust — the 0.05 stdev floor dominates
# and fabricates the z (SPCX = 5 cycles, floor-bound on 6/7 components). Until a
# component has this many cycles it stays "baseline forming", so a fresh IPO reads
# CALIBRATING, never a confident ROUTINE the data can't support.
MIN_BASELINE_TRUSTWORTHY = int(os.getenv("MARKET_MIN_BASELINE", "10"))

DETECTION_WEIGHTS = {
    "dark_positioning":          0.30,
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

DETECTION_FP  = "~22% false positive · early-warning"
CONFIDENCE_FP = "<9% false positive · confirmation"

COMPONENT_LABELS = {
    "dark_positioning":          "Dark Positioning (macro & cross-market shifts)",
    "positioning_concentration": "Positioning Concentration (smart-money: shorts/13F/insider)",
    "analyst_signal":            "Analyst Signal (news, ratings, attributed coverage)",
    "fundamental_confirmation":  "Fundamental Confirmation (realized financials)",
    "market_momentum":           "Market Momentum (price / valuation trend)",
    "cross_market_diffusion":    "Cross-Market Diffusion (venues confirming)",
    "signal_freshness":          "Signal Freshness (recency / persistence)",
}

# Market-signal LANE — separates instruments by what data CAN exist for them, so an
# "insufficient coverage" read reflects a genuine gap rather than a category error.
# Covered names have institutional positioning (13F / short interest); halt-surfaced
# micro-caps have a ticker but typically NO institutional coverage (honestly "partial");
# macro themes (recession, inflation) have no single instrument at all, so positioning +
# fundamentals are structurally N/A. The lane is supplied by the caller (risk module),
# which knows the watchlist + macro-theme set.
LANE_LABELS = {
    "covered":         "Covered instrument — institutional positioning available",
    "halted_microcap": "Halted / micro-cap — limited institutional coverage",
    "macro_theme":     "Macro theme — no single instrument; positioning N/A",
}

# Neutral intensity tiers (NOT advice). Reused from the deployed Market section.
MARKET_LEVELS = [(80, "ELEVATED"), (60, "ACTIVE"), (40, "BUILDING"),
                 (25, "ROUTINE"), (0, "DORMANT")]


def _conn(db_path):
    if db_compat is not None:
        return db_compat.connect(db_path)
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    return c


def _norm(v):
    try:
        return max(0.0, min(1.0, float(v)))
    except (TypeError, ValueError):
        return 0.0


def _level(score: float) -> str:
    return next(name for thr, name in MARKET_LEVELS if score >= thr)


# ── Baseline-relative component scoring ─────────────────────────────
def _z_to_unit(z: float) -> float:
    """z=0 (at baseline) → 0.30; z=2 → ~0.74; z=3+ → ~0.96. Below-baseline floors low."""
    if z <= 0:
        return max(0.05, 0.30 + z * 0.08)
    return min(1.0, 0.30 + z * 0.22)


def score_component(current: float, baseline: Optional[dict]) -> dict:
    samples = baseline.get("samples", 0) if baseline else 0
    if baseline and samples >= MIN_BASELINE_CYCLES:
        mean = baseline["mean"]
        # Components are 0-1, so the stdev floor must be small — a count-scale
        # floor (0.5) would crush every z-score (the bug caught in the design review).
        raw_stdev = baseline.get("stdev", max(0.08, mean * 0.3))
        stdev = max(0.05, raw_stdev)
        z = (current - mean) / stdev
        # Cold-start guard: a thin baseline (< MIN_BASELINE_TRUSTWORTHY cycles) yields
        # a floor-fabricated z. Keep the z for transparency but flag it calibrating so
        # the OVERALL read is "baseline forming", not a confident tier the data can't
        # support. Sample counts are uniform across an item's components (all recorded
        # each cycle), so an established name's deep baseline never false-triggers.
        calibrating = samples < MIN_BASELINE_TRUSTWORTHY
        return {"score": round(_z_to_unit(z), 3), "z": round(z, 2),
                "baseline_relative": not calibrating,
                "calibrating": calibrating,
                "baseline_samples": samples, "current": current}
    return {"score": round(_norm(current) * 0.6, 3), "baseline_relative": False,
            "calibrating": True, "baseline_samples": samples, "current": current}


def _feeds(component: str) -> str:
    d, c = component in DETECTION_WEIGHTS, component in CONFIDENCE_WEIGHTS
    return "both" if (d and c) else "detection" if d else "confidence" if c else "none"


def compute_market_signal(item_key: str, item_name: str,
                          components_current: dict,
                          baselines: Optional[dict] = None,
                          lane: str = "covered",
                          na_components: Optional[set] = None) -> dict:
    baselines = baselines or {}
    # STRUCTURAL N/A (lane-driven): components that CANNOT exist for this instrument
    # type — e.g. positioning_concentration + fundamental_confirmation for a macro theme
    # (recession, inflation) that has no ticker. Excluded from the weighting (renormalized)
    # AND from the coverage denominator, because they are not a data GAP — it is a category
    # error to even ask for them. Distinct from `absent` (real input, currently missing).
    na = {n for n in (na_components or set()) if n in COMPONENT_LABELS}
    applicable = [n for n in COMPONENT_LABELS if n not in na]
    # When _MKT_QUARANTINE=True an APPLICABLE component may be None (real input missing —
    # FINRA + WhaleWisdom both unavailable). THAT is a coverage gap (counts toward the
    # caveat). Gate on the flag so the default-off path is unchanged.
    absent = ({n for n in applicable if components_current.get(n) is None}
              if _MKT_QUARANTINE else set())
    scored = {n: score_component(
                  (components_current.get(n, 0.0) if n not in absent
                   else 0.0),
                  baselines.get(n))
              for n in applicable}
    any_calibrating = any(s.get("calibrating") for s in scored.values())
    # Count APPLICABLE components reading 0.0 (missing/absent inputs treated as zero).
    # If a majority of APPLICABLE inputs are zero AND the baseline is also near-zero, the
    # ROUTINE read reflects missing data coverage — not a genuinely quiet market.
    zero_inputs = sum(1 for s in scored.values() if s.get("current", -1) == 0.0)
    n_applicable = len(scored) or 1

    def _weighted(weights: dict) -> float:
        # Renormalize over present (applicable, non-absent) components so N/A or missing
        # ones don't drag the weighted sum down. With no N/A and quarantine off, present
        # == weights and total_w == 1.0, so this is identical to the plain weighted sum.
        present = {c: w for c, w in weights.items() if c in scored and c not in absent}
        total_w = sum(present.values())
        if not total_w:
            return 0.0
        return sum(present[c] * scored[c]["score"] / total_w for c in present) * 100

    detection  = round(_weighted(DETECTION_WEIGHTS), 1)
    confidence = round(_weighted(CONFIDENCE_WEIGHTS), 1)
    gap = round(detection - confidence, 1)
    interp = _interpret_gap(detection, confidence, gap, any_calibrating, zero_inputs, n_applicable)

    return {
        "item_key": item_key, "item_name": item_name,
        "detection": detection, "confidence": confidence, "gap": gap,
        "tier": _level((detection + confidence) / 2),
        "detection_level": _level(detection), "confidence_level": _level(confidence),
        "detection_fp": DETECTION_FP, "confidence_fp": CONFIDENCE_FP,
        "gap_state": interp["state"], "interpretation": interp["text"],
        "calibrating": any_calibrating,
        # Display-only coverage flag (NOT a score change): when most positioning inputs are
        # absent (FINRA short-interest / WhaleWisdom 13F not populated), a "30/ROUTINE" read
        # reflects MISSING DATA, not a confirmed quiet market. The UI shows an honest
        # "insufficient coverage" caveat instead of a misleading flat score.
        "data_coverage": ("insufficient" if zero_inputs > n_applicable // 2 else
                          "partial" if zero_inputs > 0 else "full"),
        "absent_inputs": zero_inputs, "total_inputs": n_applicable,
        # Lane = what data CAN exist for this instrument (covered / halted_microcap /
        # macro_theme). na_components are the structurally-inapplicable inputs excluded
        # from BOTH the score and the coverage denominator for this lane.
        "lane": lane, "lane_label": LANE_LABELS.get(lane, lane),
        "na_components": sorted(COMPONENT_LABELS[c] for c in na),
        "components": {
            COMPONENT_LABELS[c]: ({
                "score": round(scored[c]["score"] * 100, 1),
                "feeds": _feeds(c),
                "baseline_relative": scored[c].get("baseline_relative", False),
                "z": scored[c].get("z"),
            } if c in scored else {
                "score": None, "feeds": "n/a", "not_applicable": True,
                "baseline_relative": False, "z": None,
            }) for c in COMPONENT_LABELS
        },
        "section": "Market Signal",
        "disclaimer": "Measurement of market-signal state relative to this item's "
                      "own baseline. Analysis only — not financial advice, and not "
                      "a risk rating.",
    }


def _interpret_gap(detection, confidence, gap, calibrating,
                   zero_inputs: int = 0, total_inputs: int = 7) -> dict:
    if calibrating:
        return {"state": "CALIBRATING",
                "text": "Building this item's baseline — not enough history yet to "
                        "judge whether current activity is abnormal. Treat as a "
                        "snapshot, not a confirmed market signal."}
    if detection < 35 and confidence < 35:
        # If a majority of inputs are zero (absent), the ROUTINE read reflects
        # missing data coverage — not a confirmed quiet market.
        absent_note = (
            " (Note: several data inputs are absent for this item — "
            "scores reflect partial coverage, not a confirmed quiet reading.)"
            if zero_inputs > total_inputs // 2 else ""
        )
        return {"state": "ROUTINE",
                "text": "No unusual market signal versus this item's own baseline — "
                        "leading and hard indicators are both quiet." + absent_note}
    if gap >= 36 and detection >= 45:
        return {"state": "EARLY",
                "text": "EARLY — leading indicators (analyst, smart-money positioning, "
                        "cross-market shifts) are active while realized financials and "
                        "price have NOT yet confirmed. The early-warning window."}
    if 16 <= gap < 36:
        return {"state": "CONFIRMING",
                "text": "Leading indicators run ahead of the hard data, which is "
                        "starting to confirm. Confirmation building, not complete."}
    if abs(gap) < 16 and confidence >= 45:
        return {"state": "CONFIRMED",
                "text": "Leading and hard signals agree — corroborated by realized "
                        "fundamentals and price, and likely already reflected."}
    if gap <= -16:
        return {"state": "LAGGING",
                "text": "Hard data (financials/price) shows movement, but the early "
                        "leading signals have already passed — a late-stage read."}
    return {"state": "MIXED",
            "text": "Mixed — leading and hard indicators are partially aligned; "
                    "direction is forming but not yet clear-cut."}


# ── Component assembly from our real market sources ─────────────────
def assemble_market_components(payload: dict, sig_summary: dict) -> dict:
    """Build the 7 normalized (0-1) component values from the positioning payload
    + a summary of the item's risk signals. Grounded ONLY in sources we pull."""
    av    = payload.get("alpha_vantage") or {}
    si    = payload.get("short_interest") or {}
    iw    = payload.get("institutional_holdings") or {}
    bene  = payload.get("beneficiary") or {}
    macro = payload.get("macro_leverage") or {}
    cc    = payload.get("creator_coverage") or {}
    bcov  = payload.get("broadcast_coverage") or {}
    sus   = payload.get("sustainability") or {}
    stages = sig_summary.get("stage_counts") or {}

    # Analyst Signal — news volume + |tone| + attributed coverage
    art = av.get("article_count") or 0
    sent = abs(av.get("avg_sentiment") or 0.0)
    cov = sum(1 for c in (cc.get("creators") or []) if c.get("covered")) + len(bcov.get("channels") or [])
    analyst = _norm(math.log1p(art) / math.log1p(50) * 0.6 + sent * 0.3 + min(cov, 8) / 8 * 0.1)

    # Positioning Concentration — shorts + 13F change + insider (stage-1).
    # When _MKT_QUARANTINE=True and BOTH FINRA (si) and WhaleWisdom (iw) are
    # absent, return None so compute_market_signal renormalizes weights over
    # present components only (absent ≠ genuinely zero). Flag is default False;
    # flip only after Phase 2 referee validates direction.
    si_chg   = abs(si.get("change_pct") or 0.0)
    inst_chg = abs(iw.get("shares_change_pct") or 0.0)
    insider  = stages.get(1, 0)
    _both_absent = (not si) and (not iw)
    if _MKT_QUARANTINE and _both_absent and insider == 0:
        pos_conc = None  # structurally absent — exclude from weighted sum
    else:
        pos_conc = _norm(min(si_chg, 30) / 30 * 0.4 + min(inst_chg, 40) / 40 * 0.4
                         + math.log1p(insider) / math.log1p(20) * 0.2)
        # Dark-Positioning V2 (flag-gated, default OFF): blend the held-out smart-money
        # (curated-fund 13F breadth) + political (Congress net-trading) signal for this
        # ticker into positioning_concentration. Only fires when the flag is on AND the
        # ticker actually has 13F/Congress activity, so the default path is unchanged.
        if DARK_POSITIONING_V2:
            _dpi = payload.get("dark_positioning_intel") or {}
            _sig = _dpi.get("positioning_signal")
            _has = (_dpi.get("smart_money", {}).get("funds_holding")
                    or _dpi.get("congress", {}).get("members"))
            if _sig is not None and _has:
                pos_conc = _norm(pos_conc * (1 - DARK_POS_WEIGHT) + float(_sig) * DARK_POS_WEIGHT)

    # Dark Positioning — macro / cross-market (OFR funding stress + repo change)
    stress = ((macro.get("funding_stress") or {}).get("label") or "").lower()
    stress_v = (0.85 if ("high" in stress or "severe" in stress)
                else 0.6 if "moderate" in stress else 0.35 if "mild" in stress else 0.2)
    repo_chg = abs(((macro.get("leverage") or {}).get("repo_volume_change_pct")) or 0.0)
    dark = _norm(stress_v * 0.6 + min(repo_chg, 20) / 20 * 0.4)

    # Fundamental Confirmation — FMP income/profile (primary) + beneficiary
    # cycle inflection + Finnhub sustainability (supporting).  FMP is the
    # strongest signal: real P&L data, not proxy indicators.
    fmp_d  = payload.get("fmp") or {}
    comps  = bene.get("components") or {}
    fu_parts = []
    if fmp_d.get("score_normalized") is not None:
        fu_parts.append(_norm(fmp_d["score_normalized"]))
    if "cycle_inflection" in comps:
        fu_parts.append(_norm(comps["cycle_inflection"]))
    if sus.get("score") is not None:
        fu_parts.append(_norm(float(sus["score"]) / 100))
    fundamental = _norm(sum(fu_parts) / len(fu_parts)) if fu_parts else 0.0

    # Market Momentum — price return + valuation re-rating
    li = bene.get("live_inputs") or {}
    mm_parts = []
    if li.get("valuation_rerating") is not None:
        mm_parts.append(_norm(li["valuation_rerating"]))
    if li.get("price_return_12m") is not None:
        mm_parts.append(_norm(min(abs(float(li["price_return_12m"])), 2.0) / 2.0))
    momentum = _norm(sum(mm_parts) / len(mm_parts)) if mm_parts else 0.0

    # Cross-Market Diffusion — distinct venues active
    venues = sig_summary.get("venue_count") or 0
    diffusion = _norm(min(venues, 6) / 6)

    # Signal Freshness — recency of newest signal (1-week decay)
    age_h = sig_summary.get("newest_age_hours")
    fresh = _norm(1 - (age_h / 168)) if age_h is not None else 0.4

    return {
        "dark_positioning": round(dark, 3),
        # pos_conc may be None (absent) when _MKT_QUARANTINE=True and both
        # FINRA + WhaleWisdom are unavailable. compute_market_signal handles None.
        "positioning_concentration": (None if pos_conc is None else round(pos_conc, 3)),
        "analyst_signal": round(analyst, 3),
        "fundamental_confirmation": round(fundamental, 3),
        "market_momentum": round(momentum, 3),
        "cross_market_diffusion": round(diffusion, 3),
        "signal_freshness": round(fresh, 3),
    }


# ── Baseline storage (per-item, per-component history) ──────────────
def init_market_signal_db(db_path: str = DB_PATH, conn=None):
    own = conn is None
    c = conn or _conn(db_path)
    c.execute("""
        CREATE TABLE IF NOT EXISTS market_signal_history (
            id TEXT PRIMARY KEY,
            item_key TEXT,
            component TEXT,
            value REAL,
            signal_date TEXT,
            signal_time TEXT
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_ms_item ON market_signal_history(item_key)")
    c.commit()
    if own:
        c.close()


def record_market_cycle(item_key: str, components_current: dict,
                        signal_ts: Optional[str] = None, db_path: str = DB_PATH, conn=None):
    own = conn is None
    c = conn or _conn(db_path)
    # CANONICAL split: signal_date = primary 'YYYY-MM-DD'; signal_time = secondary
    # 'HH:MM:SS'. Live writes (signal_ts=None) record the fetch time; a timed source
    # keeps its time; a bare-date backfill seed has no time -> empty. The baseline
    # keys on (signal_date, signal_time), which is byte-identical ordering to the old
    # full timestamp, so NO market score changes.
    if signal_ts is None:
        _nowdt = datetime.now(timezone.utc)
        sig_date = _nowdt.strftime("%Y-%m-%d")
        sig_time = _nowdt.strftime("%H:%M:%S")
    else:
        sig_date = to_iso_date(signal_ts) or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        sig_time = iso_time_of(signal_ts, default_now=False) if source_has_time(signal_ts) else ""
    try:
        for comp, val in components_current.items():
            rid = hashlib.md5(f"{item_key}-{comp}-{sig_date}T{sig_time}".encode()).hexdigest()[:16]
            c.execute("INSERT OR IGNORE INTO market_signal_history "
                      "(id, item_key, component, value, signal_date, signal_time) VALUES (?,?,?,?,?,?)",
                      (rid, item_key, comp, float(val), sig_date, sig_time))
        c.commit()
    except Exception as e:
        print(f"  [market_signal] record error ({item_key}): {e}")
    finally:
        if own:
            c.close()


def get_market_baselines(item_key: str, lookback: int = 12,
                         db_path: str = DB_PATH, conn=None) -> dict:
    own = conn is None
    c = conn or _conn(db_path)
    try:
        rows = c.execute("SELECT component, value, signal_date, signal_time FROM market_signal_history "
                         "WHERE item_key = ? ORDER BY signal_date DESC, signal_time DESC",
                         (item_key,)).fetchall()
    except Exception:
        rows = []
    finally:
        if own:
            c.close()
    if not rows:
        return {}
    def g(r, k, i):
        return r[k] if hasattr(r, "keys") else r[i]
    # A cycle is identified by (signal_date, signal_time) — the same distinct key the
    # old full-timestamp cycle_at provided, so the baseline window is unchanged.
    def cyc(r):
        return (g(r, "signal_date", 2), g(r, "signal_time", 3) or "")
    cycles = sorted({cyc(r) for r in rows}, reverse=True)
    baseline_cycles = set(cycles[1:lookback + 1])  # skip the most recent cycle
    by_comp = {}
    for r in rows:
        if cyc(r) in baseline_cycles:
            by_comp.setdefault(g(r, "component", 0), []).append(g(r, "value", 1))
    profile = {}
    for comp, vals in by_comp.items():
        if vals:
            mean = statistics.mean(vals)
            stdev = statistics.stdev(vals) if len(vals) >= 2 else max(0.08, mean * 0.3)
            profile[comp] = {"mean": round(mean, 3),
                             "stdev": round(max(0.05, stdev), 3), "samples": len(vals)}
    return profile


def apply_market_signal(item_key: str, item_name: str, components_current: dict,
                        record_this_cycle: bool = True, db_path: str = DB_PATH,
                        conn=None, lane: str = "covered",
                        na_components: Optional[set] = None) -> dict:
    """Full pipeline: record this cycle, load baselines, compute the dual score."""
    if record_this_cycle:
        record_market_cycle(item_key, components_current, db_path=db_path, conn=conn)
    baselines = get_market_baselines(item_key, db_path=db_path, conn=conn)
    return compute_market_signal(item_key, item_name, components_current, baselines,
                                 lane=lane, na_components=na_components)


# ── Historical backfill (seed baselines from real history) ──────────
def backfill_from_finra(items: list, db_path: str = DB_PATH) -> dict:
    """Seed the `positioning_concentration` baseline from each watchlist company's
    FINRA short-interest history (~180-day bi-monthly series). Records a component
    point at each historical settlement date so the baseline is populated from day
    one rather than reading CALIBRATING for days.

    items: list of (item_key, ticker). Returns counts. Idempotent (INSERT OR IGNORE).
    Free-tier reality: FINRA gives ~12 bi-monthly points / 180 days — a real but
    SHALLOW seed; live cycles + other backfills deepen it over time.
    """
    try:
        import finra_data
    except Exception as e:
        return {"error": f"finra_data unavailable: {e}"}
    init_market_signal_db(db_path)
    seeded_items = 0
    seeded_points = 0
    conn = _conn(db_path)
    try:
        for item_key, ticker in items:
            if not ticker:
                continue
            series = finra_data.short_interest_series(ticker)
            if not series:
                continue
            for pt in series:
                sd = pt.get("settlement_date")
                if not sd:
                    continue
                # Normalize this historical point to the same 0-1 scale as the live
                # positioning_concentration's short-interest term.
                si_chg = abs(pt.get("change_pct") or 0.0)
                dtc = pt.get("days_to_cover") or 0.0
                val = _norm(min(si_chg, 30) / 30 * 0.6 + min(dtc, 10) / 10 * 0.4)
                record_market_cycle(item_key, {"positioning_concentration": val},
                                    signal_ts=sd, conn=conn)
                seeded_points += 1
            seeded_items += 1
    finally:
        conn.close()
    return {"seeded_items": seeded_items, "seeded_points": seeded_points,
            "source": "FINRA short-interest 180d series",
            "note": "Shallow seed (bi-monthly). Other components accrue live."}


def backfill_from_finnhub(items: list, db_path: str = DB_PATH) -> dict:
    """Seed `fundamental_confirmation` from each company's quarterly financials
    (Finnhub financials-reported). Computes a normalized fundamental value per
    historical quarter (revenue growth + margin) and records it at the quarter's
    period date. Several years of quarters available → a deeper seed than FINRA."""
    import os as _os
    key = _os.getenv("FINNHUB_API_KEY", "")
    if not key:
        return {"error": "no FINNHUB_API_KEY"}
    init_market_signal_db(db_path)
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
    import json as _json
    seeded_items = seeded_points = 0
    conn = _conn(db_path)
    try:
        for item_key, ticker in items:
            if not ticker:
                continue
            try:
                url = ("https://finnhub.io/api/v1/stock/financials-reported?"
                       + urlencode({"symbol": ticker, "freq": "quarterly", "token": key}))
                with urlopen(Request(url, headers={"User-Agent": "NowTrendIn/2.0"}), timeout=15) as r:
                    data = _json.loads(r.read().decode("utf-8"))
            except Exception as e:
                print(f"  [finnhub backfill] {ticker}: {e}")
                continue
            quarters = (data.get("data") or [])[:12]   # ~3 years
            # oldest→newest so we can compute QoQ growth
            quarters = list(reversed(quarters))
            prev_rev = None
            for q in quarters:
                period = q.get("endDate") or q.get("filedDate")
                ic = {it.get("concept", ""): it.get("value")
                      for it in (q.get("report", {}).get("ic", []) or [])}
                rev = ic.get("Revenues") or ic.get("RevenueFromContractWithCustomerExcludingAssessedTax")
                gross = ic.get("GrossProfit")
                if not period or not rev:
                    prev_rev = rev or prev_rev
                    continue
                # Normalized fundamental value: QoQ revenue growth + gross margin.
                growth = ((rev - prev_rev) / abs(prev_rev)) if (prev_rev and prev_rev != 0) else 0.0
                margin = (gross / rev) if (gross and rev) else 0.0
                val = _norm(min(max(growth, -0.5), 0.5) + 0.5) * 0.6 + _norm(margin) * 0.4
                record_market_cycle(item_key, {"fundamental_confirmation": round(_norm(val), 3)},
                                    signal_ts=str(period)[:10], conn=conn)
                seeded_points += 1
                prev_rev = rev
            seeded_items += 1
    finally:
        conn.close()
    return {"seeded_items": seeded_items, "seeded_points": seeded_points,
            "source": "Finnhub quarterly financials",
            "note": "Seeds fundamental_confirmation from ~12 quarters."}
