"""
================================================================
GRADE AGENT — pool-first topic grading (serves all 3 platforms)
================================================================

The raw AI grade ALWAYS spends a Perplexity+Claude call to ESTIMATE a score —
even when the topic is already measured in our live data pool. The Grade Agent
fixes that: it searches the full data pool FIRST, and

  • IF the topic is already in the pool  -> returns the MEASURED Gradient Score
    + the MEASURED N (Now Trending) score from the live engine record. No AI
    cost, no grade-credit burn — we already know the real answer.

  • IF the topic is NOT in the pool       -> runs the AI grade (PROPOSED Gradient
    Score with research + citations) and attaches the live N score (0 until
    on-platform demand accrues; the grade query itself logs N so it starts to).

Either way it returns BOTH a Gradient Score (detection + confidence + overall +
stage) AND an N score, plus `source` ('measured' | 'ai_proposed'), `in_data_pool`,
and `charge_token` (False for measured — nothing was spent). One engine endpoint
(/grade) feeds web, desktop, and mobile identically.

INTEGRITY: a measured return is the engine's OWN score (objective, not an AI
estimate); an AI return is clearly flagged 'ai_proposed'. N is always the
separate demand signal — never folded into the Gradient (no demand feedback loop).
================================================================
"""
from __future__ import annotations


def _num(x, nd=0):
    try:
        v = float(x)
        return round(v, nd) if nd else round(v)
    except (TypeError, ValueError):
        return 0


def _measured_mainstream(s: dict) -> dict:
    """Mainstream-vs-niche from OUR OWN data — the dual-pathway scoring agent's
    determination (detection_pathway / mainstream_ratio / mainstream_confirmed).
    This is the 'communicate with other data agents' path for in-pool topics."""
    pathway = (s.get("detection_pathway") or "").lower()
    try:
        ratio = float(s.get("mainstream_ratio") or 0)
    except (TypeError, ValueError):
        ratio = 0.0
    confirmed = bool(s.get("mainstream_confirmed"))
    if confirmed or pathway == "mainstream" or ratio >= 0.6:
        label = "mainstream"
        note = "Confirmed across many distinct mainstream communities / reputable outlets."
    elif pathway == "blended" or ratio >= 0.2:
        label = "emerging"
        note = "Crossing from expert communities into the mainstream (highest-confidence mainstreaming)."
    else:
        label = "niche"
        note = "Concentrated in expert/specialist communities — the public hasn't caught on yet."
    return {"label": label, "note": note, "source": "engine · dual-pathway",
            "mainstream_ratio": round(ratio, 3), "mainstream_confirmed": confirmed,
            "detection_pathway": pathway or "expert"}


def _ai_mainstream(result: dict) -> dict:
    """Mainstream-vs-niche for a topic NOT in our pool — from the OPEN-WEB research
    (Perplexity classified WHERE the conversation lives + whether experts lead)."""
    cls = (result.get("classification") or "").lower()
    if cls in ("mainstream", "emerging", "niche", "fading"):
        label = cls
    else:  # fall back to the AI-estimated niche concentration (G)
        g = _num(result.get("gradient_strength"))
        label = "niche" if g >= 55 else ("mainstream" if g <= 35 else "emerging")
    return {"label": label, "note": result.get("reach_note") or "",
            "source": "open-web research (Perplexity)"}


def _measured_from_row(g, s: dict) -> dict:
    """Build a grade result from a live, measured velocity_scores row (already
    run through _format_score_rows so calibration/components/N are present)."""
    comps = s.get("components") or {}

    def comp(k):
        c = comps.get(k)
        return _num(c.get("score")) if isinstance(c, dict) else 0

    det = _num(s.get("detection_score"))
    conf = _num(s.get("confidence_score"))
    overall = _num(s.get("overall_score"))
    n = _num(s.get("nowtrendin_score"))
    stage = (s.get("signal_stage") or "").upper()
    cal = s.get("calibration") or {}
    return {
        "available": True,
        "source": "measured",
        "in_data_pool": True,
        "charge_token": False,                 # nothing was spent — measured lookup
        "proposed": True,                      # has a real score (renderers key off this)
        "topic": s.get("topic_display") or s.get("topic_key"),
        "topic_key": s.get("topic_key"),
        "category": s.get("category"),
        "stage": stage,
        # headline scores (top-level, for existing mobile/web renderers)
        "detection_score": det,
        "confidence_score": conf,
        "heisenberg_gap": _num(s.get("heisenberg_gap")),
        # structured duplicates the new renderers read
        "gradient_score": {"detection": det, "confidence": conf, "overall": overall, "stage": stage},
        "n_score": n,
        # signal-quality components (same labels the AI grade returns)
        "gradient_strength": comp("G_gradient_strength"),
        "platform_diversity": comp("M_platform_diversity"),
        "inertia": comp("I_inertia"),
        "dark_matter": comp("D_dark_matter"),
        "persistence": comp("P_persistence"),
        # narrative
        "action": s.get("what_to_do_action") or "",
        "reasoning": s.get("score_explanation") or s.get("why_this_matters") or "",
        "research": s.get("why_this_matters") or "",
        "citations": [],
        "maturity": cal.get("maturity_class"),
        "maturity_reason": cal.get("maturity_reason"),
        # mainstream-vs-niche from OUR data (dual-pathway agent) + what we consulted
        "mainstream_vs_niche": _measured_mainstream(s),
        "data_pool": {
            "in_pool": True,
            "category": s.get("category"),
            "detection_pathway": s.get("detection_pathway"),
            "mainstream_ratio": s.get("mainstream_ratio"),
            "mainstream_confirmed": bool(s.get("mainstream_confirmed")),
        },
        "consulted": ["data pool (velocity_scores)", "topic classifier",
                      "dual-pathway agent (expert vs mainstream)"],
        "measured_row": s,                     # full live row for rich rendering
        "note": ("This topic is already in the Now TrendIn data pool — returning the "
                 "MEASURED Gradient Score and N score from the live engine (no AI "
                 "estimate, no grade credit charged)."),
    }


def _lookup_n(g, conn, key: str) -> int:
    """Live N (nowtrendin_score) for a canonical key, even if it never crossed the
    scoring floor (0 is honest — demand hasn't accrued yet)."""
    try:
        r = conn.execute(
            "SELECT nowtrendin_score FROM velocity_scores WHERE topic_key = ? "
            "ORDER BY scored_at DESC LIMIT 1", (key,)).fetchone()
        return _num(r["nowtrendin_score"]) if r else 0
    except Exception:
        return 0


def resolve_grade(topic: str) -> dict:
    """Pool-first grade resolution. See module docstring."""
    import gravitational_anomaly_detector as g

    raw = (str(topic or "")).strip()
    if not raw:
        return {"available": False, "reason": "topic is required"}

    try:
        key = g._topic_key(raw)
    except Exception:
        key = raw.lower().replace(" ", "_")

    # ── 1) SEARCH THE DATA POOL (exact canonical key, then display match) ──
    conn = g.get_db(g.DB_PATH)
    row = None
    try:
        row = conn.execute(
            "SELECT * FROM velocity_scores WHERE topic_key = ? ORDER BY scored_at DESC LIMIT 1",
            (key,)).fetchone()
        if not row:
            row = conn.execute(
                """SELECT v.* FROM velocity_scores v
                   INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores
                               GROUP BY topic_key) l
                     ON v.topic_key = l.topic_key AND v.scored_at = l.m
                   WHERE LOWER(v.topic_display) = ? LIMIT 1""",
                (raw.lower(),)).fetchone()
    except Exception as e:
        print(f"[grade_agent] pool search failed: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # ── 2) MEASURED — topic is already scored: return the real numbers ──
    if row:
        try:
            formatted = g._format_score_rows([row])
            s = formatted["results"][0] if formatted.get("results") else dict(row)
        except Exception:
            s = dict(row)
        if not s.get("category"):
            s["category"] = g._topic_category(s.get("topic_display") or raw)
        res = _measured_from_row(g, s)
        try:
            g._log_topic_query(res["topic_key"], "grade:measured")
        except Exception:
            pass
        # companies: attach the measured Market Signal too (consistent w/ Market tab)
        _attach_market(g, raw, res)
        return res

    # ── 3) NOT IN POOL — AI proposed grade, with the live N attached ──
    if not getattr(g, "_AI_GRADE_AVAILABLE", False):
        return {"available": False, "reason": "AI grade module unavailable", "source": "ai_proposed"}
    if not g._ai_budget_ok():
        return {"available": False, "source": "ai_proposed", "reason": "monthly AI budget reached",
                "budget": g.AI_MONTHLY_BUDGET_USD,
                "spent": round(g._ai_spend_this_month().get("total", 0), 4)}

    result = g.ai_grade.grade_topic(raw)
    if not isinstance(result, dict):
        return {"available": False, "reason": "grade failed", "source": "ai_proposed"}

    nconn = g.get_db(g.DB_PATH)
    try:
        n = _lookup_n(g, nconn, key)
    finally:
        try:
            nconn.close()
        except Exception:
            pass
    try:
        g._log_topic_query(key, "grade:ai")   # logging the grade query seeds N
    except Exception:
        pass

    result["source"] = "ai_proposed"
    result["in_data_pool"] = False
    result["n_score"] = n
    # only charge a grade credit when a real proposed score returned
    result["charge_token"] = bool(result.get("available") and result.get("proposed"))
    if result.get("proposed"):
        result["gradient_score"] = {
            "detection": _num(result.get("detection_score")),
            "confidence": _num(result.get("confidence_score")),
            "stage": (result.get("stage") or "").upper(),
        }
    # mainstream-vs-niche from the OPEN WEB (the topic isn't in our pool) + the
    # classifier's category, and what the agent consulted.
    result["mainstream_vs_niche"] = _ai_mainstream(result)
    try:
        cat = g._topic_category(raw)
    except Exception:
        cat = None
    result["data_pool"] = {"in_pool": False, "category": cat}
    result["consulted"] = ["data pool (velocity_scores · miss → web)", "topic classifier",
                           "open-web research (Perplexity)", "AI synthesis (Claude)"]
    _attach_market(g, raw, result)
    return result


def _attach_market(g, topic: str, result: dict) -> None:
    """Attach the measured Market Signal for companies (same data the Market tab
    shows) so the market read is identical across Grade and Market."""
    if not getattr(g, "_RISK_AVAILABLE", False) or not isinstance(result, dict):
        return
    try:
        tkr, disp = g.risk.resolve_ticker(topic)
        if tkr:
            ms = g.risk.market_signal_for_company(tkr, disp or topic, g.DB_PATH)
            if ms and ms.get("available"):
                result["market_signal"] = ms
                _attach_market_ai_analysis(g, topic, tkr, disp, ms, result)
    except Exception as e:
        print(f"[grade_agent] market attach error: {e}")


def _attach_market_ai_analysis(g, topic, tkr, disp, ms, result) -> None:
    """LLM market narrative for the Grade — incorporates Money Movement / Market Confirmation /
    Leverage as a MEASUREMENT (guardrailed against advice). Budget-gated + 12h-cached per
    instrument, so cost stays bounded under the engine's monthly AI cap. Opt-out via
    MARKET_AI_ANALYSIS=0. The reproducible score-walk already lives in market_signal.market_gradient
    .interpretation; this is the optional richer prose layer."""
    import os
    if os.getenv("MARKET_AI_ANALYSIS", "1") != "1":
        return
    if not getattr(g, "_AI_GRADE_AVAILABLE", False):
        return
    try:
        if not g._ai_budget_ok():
            return
        mgd = ms.get("market_gradient") or {}
        if not mgd or mgd.get("calibrating") or mgd.get("data_coverage") == "insufficient":
            return
        ma = g.ai_grade.market_analysis(
            disp or topic, mgd.get("detection"), mgd.get("confidence"),
            mgd.get("leverage_health"), mgd.get("flow"), ticker=tkr)
        if ma and ma.get("available"):
            result["market_analysis"] = {"text": ma["text"], "provider": ma.get("provider", "claude"),
                                         "cached": ma.get("cached", False),
                                         "note": "AI measurement of Money Movement / Market "
                                                 "Confirmation / Leverage from our scores — not advice."}
            if ma.get("cost"):
                g._record_ai_cost("market_analysis", disp or topic, ma["cost"])
    except Exception as e:
        print(f"[grade_agent] market AI analysis error: {e}")
