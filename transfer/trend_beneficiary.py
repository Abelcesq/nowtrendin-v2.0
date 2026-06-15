"""
================================================================
NOW TRENDIN — TREND BENEFICIARY ENGINE
Measuring Business Exposure to a Detected Trend (the "SanDisk pattern")
================================================================

WHAT IT MEASURES (and what it does NOT):
  It measures how well-positioned a company's BUSINESS is to benefit
  from a trend Now TrendIn has detected — its revenue exposure, the
  inflection in its fundamentals, the structural setup, gated by
  quality. It outputs a CYCLE STAGE telling you whether the
  re-rating is early or already realized.

  It does NOT predict stock prices, recommend buying, or claim a
  company "will grow." It is a measurement of business exposure and
  cycle position for further human research. Every output carries a
  not-investment-advice flag.

THE METHODOLOGY FIX (vs a naive hindsight model):
  A model reverse-engineered from SanDisk-the-winner is full of
  BACKWARD-looking factors (huge 12m return, re-rated multiple,
  saturated narrative). Those describe a move that ALREADY happened.
  Scoring on them flags winners at the moment the edge is gone.

  So factors are split:
    LEADING  (the early edge, weighted for the SCORE):
       - Theme Exposure     — is the business tied to the trend?
       - Cycle Inflection   — are fundamentals TURNING UP now?
       - Structural Setup   — recent spinoff/IPO creating a pure-play
       - Trend Attention    — is the underlying trend gaining? (NowTrendIn engine)
    QUALITY (a gate — "solid, reputable"):
       - profitability, size, balance sheet — junk is excluded
    LAGGING  (used for CYCLE STAGE, NOT chased):
       - 12m price run, valuation re-rating, narrative saturation

  Result: high exposure + EARLY stage = the SanDisk-early-2025 setup
  (the valuable find). High exposure + LATE/REALIZED = SanDisk-today
  (great company, move already happened — flagged as priced in).

DATA: Finnhub (company profile, financials, news, recommendation
  trends) + the existing Now TrendIn attention engine for the trend
  side. Degrades gracefully when a field or endpoint is unavailable.

INTEGRATION: slots beside the Positioning engine in the financial
  ("Other") section as a per-company trend-exposure read.
================================================================
"""

import os
import math
import statistics
from datetime import datetime, timezone
from typing import Optional

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

# ════════════════════════════════════════════════════════════════
# SECTION 1: THEME DEFINITIONS
# A theme = the keyword/sector fingerprint of a detected trend.
# Extend this dict as Now TrendIn detects new themes.
# ════════════════════════════════════════════════════════════════

THEMES = {
    "ai_infrastructure": {
        "label": "AI Infrastructure",
        "keywords": ["ai", "artificial intelligence", "llm", "datacenter",
                     "data center", "hyperscale", "inference", "training",
                     "gpu", "hbm", "nand", "dram", "ssd", "nvme", "memory",
                     "storage", "accelerator", "compute"],
        "sectors": ["Semiconductors", "Technology", "Hardware",
                    "Electronic Equipment", "Semiconductor Equipment"],
    },
    "energy_transition": {
        "label": "Energy Transition",
        "keywords": ["battery", "ev", "electric vehicle", "grid", "solar",
                     "renewable", "lithium", "energy storage", "charging"],
        "sectors": ["Energy", "Utilities", "Industrials", "Materials"],
    },
    # add more themes as the attention engine surfaces them
}


# ════════════════════════════════════════════════════════════════
# SECTION 2: LEADING SUB-SCORES (the early edge)
# ════════════════════════════════════════════════════════════════

def compute_theme_exposure(theme_key: str, profile: dict,
                          recent_news: list) -> dict:
    """
    Theme Exposure (TE), 0-1: how tied is the BUSINESS to the trend?
      - sector match (is the company in a relevant sector?)
      - keyword density in news headlines + business profile
    """
    theme = THEMES.get(theme_key, {})
    keywords = theme.get("keywords", [])
    sectors  = theme.get("sectors", [])

    # Sector match (up to 0.5)
    company_sector = (profile.get("finnhubIndustry") or
                      profile.get("sector") or "")
    sector_score = 0.5 if any(s.lower() in company_sector.lower()
                              for s in sectors) else 0.0

    # Keyword density in recent news headlines (up to 0.5)
    headlines = " ".join(n.get("headline", "").lower() for n in (recent_news or []))
    if headlines:
        hits = sum(headlines.count(k) for k in keywords)
        # normalize: ~1 hit per headline saturates
        density = min(1.0, hits / max(1, len(recent_news)))
        keyword_score = 0.5 * density
    else:
        keyword_score = 0.0

    te = round(min(1.0, sector_score + keyword_score), 3)
    return {"score": te, "sector_match": sector_score > 0,
            "company_sector": company_sector}


def compute_cycle_inflection(financials: list) -> dict:
    """
    Cycle Inflection (CI), 0-1: are fundamentals TURNING UP *now*?

    We reward ACCELERATION (the early signal), not just high growth:
      - revenue growth accelerating (recent YoY > prior YoY)
      - gross margin expanding
      - EPS accelerating
    financials: list of quarterly dicts (newest last) with
      revenue, gross_margin, eps  (degrades if fields missing)
    """
    if not financials or len(financials) < 5:
        return {"score": 0.3, "basis": "insufficient_financials"}

    rev = [f.get("revenue") for f in financials if f.get("revenue") is not None]
    gm  = [f.get("gross_margin") for f in financials if f.get("gross_margin") is not None]
    eps = [f.get("eps") for f in financials if f.get("eps") is not None]

    components = []

    # Revenue growth acceleration: YoY now vs YoY a quarter/year ago
    if len(rev) >= 8:
        yoy_now  = (rev[-1] - rev[-5]) / abs(rev[-5]) if rev[-5] else 0
        yoy_prev = (rev[-5] - rev[-8]) / abs(rev[-8]) if len(rev) >= 8 and rev[-8] else 0
        accel = yoy_now - yoy_prev
        components.append(_sigmoid_scale(accel, center=0.1, width=0.4))
    elif len(rev) >= 5:
        yoy_now = (rev[-1] - rev[-5]) / abs(rev[-5]) if rev[-5] else 0
        components.append(_sigmoid_scale(yoy_now, center=0.2, width=0.6))

    # Gross margin expansion (recent vs 4q ago)
    if len(gm) >= 5:
        gm_delta = gm[-1] - gm[-5]
        components.append(_sigmoid_scale(gm_delta, center=0.0, width=0.08))

    # EPS acceleration
    if len(eps) >= 5:
        eps_yoy = (eps[-1] - eps[-5])
        components.append(_sigmoid_scale(eps_yoy, center=0.0, width=2.0))

    score = round(statistics.mean(components), 3) if components else 0.3
    return {"score": score, "basis": f"{len(components)} fundamental signals"}


def compute_structural_setup(profile: dict) -> dict:
    """
    Structural Setup (SS), 0-1: a recent corporate-clarity event
    (spinoff / IPO / carve-out) that creates a focused pure-play.
    Approximated from the IPO/listing date — high if within ~18 months,
    decaying after. (SanDisk: Feb 2025 spinoff.)
    """
    ipo = profile.get("ipo")
    if not ipo:
        return {"score": 0.2, "basis": "no_listing_date"}
    try:
        ipo_dt = datetime.fromisoformat(str(ipo)[:10]).replace(tzinfo=timezone.utc)
        months = (datetime.now(timezone.utc) - ipo_dt).days / 30.4
    except Exception:
        return {"score": 0.2, "basis": "unparseable_date"}

    if months <= 12:
        score = 1.0
    elif months <= 24:
        score = 1.0 - (months - 12) / 12 * 0.6   # 1.0 → 0.4 across yr 2
    elif months <= 48:
        score = max(0.1, 0.4 - (months - 24) / 24 * 0.3)
    else:
        score = 0.1
    return {"score": round(score, 3), "months_since_listing": round(months, 1)}


def compute_trend_attention(theme_attention_score: float,
                          theme_exposure: float) -> dict:
    """
    Trend Attention (TA), 0-1: is the underlying TREND gaining, and is
    this company linked to it? Ties this engine to Now TrendIn's core
    attention gradient — a beneficiary only matters if the trend is real.

    theme_attention_score: 0-100 from the attention engine for the theme
    theme_exposure: the company's TE (so a high-attention trend only
      lifts companies actually exposed to it)
    """
    trend = max(0.0, min(1.0, theme_attention_score / 100.0))
    ta = round(trend * (0.4 + 0.6 * theme_exposure), 3)
    return {"score": ta, "trend_strength": round(trend, 2)}


# ════════════════════════════════════════════════════════════════
# SECTION 3: QUALITY GATE ("solid, reputable")
# ════════════════════════════════════════════════════════════════

def compute_quality(profile: dict, financials: list) -> dict:
    """
    Quality (Q), 0-1: is this a solid, reputable company — not a
    microcap pump? Profitability + size + balance-sheet sanity.
    A low Q heavily caps the score (junk is excluded by design).
    """
    score = 0.0
    flags = []

    # Size — market cap floor (microcaps excluded)
    mcap = profile.get("marketCapitalization", 0) or 0   # Finnhub: in $M
    if mcap >= 10000:      score += 0.35; flags.append("large_cap")
    elif mcap >= 2000:     score += 0.25; flags.append("mid_cap")
    elif mcap >= 500:      score += 0.12; flags.append("small_cap")
    else:                  flags.append("micro_cap_penalty")

    # Profitability — positive recent net income / EPS
    if financials and len(financials) >= 2:
        recent_eps = [f.get("eps") for f in financials[-4:] if f.get("eps") is not None]
        if recent_eps:
            if all(e > 0 for e in recent_eps):
                score += 0.35; flags.append("consistently_profitable")
            elif recent_eps[-1] > 0:
                score += 0.20; flags.append("recently_profitable")
            else:
                flags.append("unprofitable")

        # Positive and improving gross margin
        gms = [f.get("gross_margin") for f in financials[-4:]
               if f.get("gross_margin") is not None]
        if gms and statistics.mean(gms) > 0.20:
            score += 0.15; flags.append("healthy_margins")
    else:
        score += 0.10  # unknown — neutral-ish, not rewarded

    # Established listing (not a brand-new shell) — but spinoffs are OK
    score = round(min(1.0, score + 0.15), 3)  # base reputability credit

    below_threshold = score < 0.40
    return {"score": score, "below_threshold": below_threshold, "flags": flags,
            "market_cap_m": mcap}


# ════════════════════════════════════════════════════════════════
# SECTION 4: LAGGING INDICATORS → CYCLE STAGE (not chased)
# ════════════════════════════════════════════════════════════════

def compute_cycle_stage(price_return_12m: Optional[float],
                       valuation_rerating: Optional[float],
                       narrative_saturation: Optional[float]) -> dict:
    """
    Where in the re-rating cycle is this name? Built from LAGGING signals.
    These do NOT add to the exposure score — they tell you whether the
    opportunity window is open (EARLY) or largely closed (REALIZED).

      price_return_12m:     fractional 12m return (e.g. 4.0 = +400%)
      valuation_rerating:   0-1, how far the multiple has expanded
      narrative_saturation: 0-1, how mainstream the story already is
                            (from attention engine: Stage 4-5 = saturated)
    """
    parts = []
    if price_return_12m is not None:
        # +50% → 0.2 ; +200% → 0.6 ; +500%+ → ~1.0
        parts.append(min(1.0, max(0.0, price_return_12m / 5.0)))
    if valuation_rerating is not None:
        parts.append(max(0.0, min(1.0, valuation_rerating)))
    if narrative_saturation is not None:
        parts.append(max(0.0, min(1.0, narrative_saturation)))

    if not parts:
        return {"stage": "UNKNOWN", "lateness": None,
                "note": "no lagging data — cannot place in cycle"}

    lateness = round(statistics.mean(parts), 3)
    if lateness < 0.30:   stage = "EARLY"
    elif lateness < 0.60: stage = "MID"
    elif lateness < 0.85: stage = "LATE"
    else:                 stage = "REALIZED"

    return {"stage": stage, "lateness": lateness}


# ════════════════════════════════════════════════════════════════
# SECTION 5: COMPOSITE — Beneficiary Exposure Score + interpretation
# ════════════════════════════════════════════════════════════════

LEADING_WEIGHTS = {"theme": 0.30, "cycle": 0.30, "structural": 0.20, "attention": 0.20}


def compute_beneficiary_score(theme_key: str, ticker: str,
                            profile: dict, financials: list,
                            recent_news: list,
                            theme_attention_score: float = 50.0,
                            price_return_12m: Optional[float] = None,
                            valuation_rerating: Optional[float] = None,
                            narrative_saturation: Optional[float] = None) -> dict:
    """
    Full trend-beneficiary assessment for one company against one theme.
    Returns the exposure score (0-100), the cycle stage, the component
    breakdown, an interpretation, and the not-advice flag.
    """
    te = compute_theme_exposure(theme_key, profile, recent_news)
    ci = compute_cycle_inflection(financials)
    ss = compute_structural_setup(profile)
    ta = compute_trend_attention(theme_attention_score, te["score"])
    q  = compute_quality(profile, financials)

    leading = (LEADING_WEIGHTS["theme"]      * te["score"] +
               LEADING_WEIGHTS["cycle"]      * ci["score"] +
               LEADING_WEIGHTS["structural"] * ss["score"] +
               LEADING_WEIGHTS["attention"]  * ta["score"])

    # Quality gate: below threshold → heavily capped (junk excluded);
    # above → quality scales the score from 0.5x to 1.0x.
    if q["below_threshold"]:
        exposure_score = round(leading * 100 * 0.25, 1)
        quality_note = "Below quality threshold — excluded from beneficiary ranking."
    else:
        exposure_score = round(leading * 100 * (0.5 + 0.5 * q["score"]), 1)
        quality_note = None

    cycle = compute_cycle_stage(price_return_12m, valuation_rerating, narrative_saturation)

    # Interpretation — combines exposure with cycle stage honestly
    interpretation = _interpret(exposure_score, cycle["stage"], q["below_threshold"])

    return {
        "ticker":          ticker,
        "theme":           THEMES.get(theme_key, {}).get("label", theme_key),
        "exposure_score":  exposure_score,        # 0-100, business exposure (NOT a price call)
        "cycle_stage":     cycle["stage"],         # EARLY / MID / LATE / REALIZED
        "lateness":        cycle.get("lateness"),
        "components": {
            "theme_exposure":   te["score"],
            "cycle_inflection": ci["score"],
            "structural_setup": ss["score"],
            "trend_attention":  ta["score"],
            "quality":          q["score"],
        },
        "quality_flags":   q["flags"],
        "quality_note":    quality_note,
        "interpretation":  interpretation,
        "disclaimer":      "Measurement of business exposure and cycle position "
                           "only. Not investment advice, not a prediction of price "
                           "or growth. For research context.",
    }


def _interpret(score: float, stage: str, below_quality: bool) -> str:
    if below_quality:
        return ("Limited reputability/quality — does not meet the 'solid company' "
                "bar, so trend linkage is not treated as a beneficiary signal.")
    if score < 35:
        return "Limited business exposure to this trend. Not a notable beneficiary."
    if stage in ("EARLY", "MID") and score >= 60:
        return (f"Strong business exposure to this trend, and {stage.lower()} in the "
                f"re-rating cycle — the higher-value window where the linkage is not "
                f"yet fully reflected. The SanDisk-early-2025 pattern.")
    if stage in ("LATE", "REALIZED") and score >= 60:
        return (f"Strong business exposure, but {stage.lower()} in the cycle — the "
                f"re-rating has largely occurred and is likely reflected already. "
                f"High linkage, but the early window has mostly closed (the "
                f"SanDisk-today pattern).")
    if stage == "UNKNOWN":
        return ("Moderate-to-strong exposure; cycle position unknown (no price/"
                "valuation data). Treat as exposure signal pending cycle context.")
    return f"Moderate exposure to this trend; {stage.lower()} in the cycle."


# ════════════════════════════════════════════════════════════════
# SECTION 6: FINNHUB FETCH LAYER (graceful)
# ════════════════════════════════════════════════════════════════

def fetch_company_data(ticker: str) -> dict:
    """
    Pull profile + financials + news from Finnhub. Degrades gracefully:
    any unavailable piece returns empty and the scorer handles it.
    Returns {profile, financials, news}.
    """
    import json, time
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode

    def get(path, params):
        if not FINNHUB_API_KEY:
            return None
        params["token"] = FINNHUB_API_KEY
        url = f"https://finnhub.io/api/v1/{path}?{urlencode(params)}"
        try:
            time.sleep(1.1)
            with urlopen(Request(url, headers={"User-Agent": "NowTrendIn/2.0"}),
                        timeout=15) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print(f"  Finnhub {path} error: {e}")
            return None

    profile = get("stock/profile2", {"symbol": ticker}) or {}

    # Basic financials → margins; financials-reported → revenue/eps series
    fins = []
    reported = get("stock/financials-reported", {"symbol": ticker, "freq": "quarterly"})
    if reported and reported.get("data"):
        for q in reversed(reported["data"][:12]):   # oldest→newest
            rpt = q.get("report", {})
            ic = {item.get("concept", ""): item.get("value")
                  for item in rpt.get("ic", [])}
            revenue = ic.get("Revenues") or ic.get("RevenueFromContractWithCustomerExcludingAssessedTax")
            net_inc = ic.get("NetIncomeLoss")
            gross   = ic.get("GrossProfit")
            fins.append({
                "revenue": revenue,
                "eps": q.get("report", {}).get("eps"),
                "gross_margin": (gross / revenue) if (gross and revenue) else None,
                "net_income": net_inc,
            })

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    frm = (datetime.now(timezone.utc).replace(day=1)).strftime("%Y-%m-%d")
    news = get("company-news", {"symbol": ticker, "from": frm, "to": today}) or []

    return {"profile": profile, "financials": fins, "news": news}


def apply_beneficiary_score(ticker: str, theme_key: str,
                          theme_attention_score: float = 50.0,
                          price_return_12m: Optional[float] = None,
                          db_fetch=None) -> dict:
    """
    Drop-in for the financial gradient: fetch + score one company against
    a theme. db_fetch lets you inject cached data (or the demo's mock).
    """
    data = (db_fetch(ticker) if db_fetch else fetch_company_data(ticker))
    return compute_beneficiary_score(
        theme_key, ticker,
        profile=data.get("profile", {}),
        financials=data.get("financials", []),
        recent_news=data.get("news", []),
        theme_attention_score=theme_attention_score,
        price_return_12m=price_return_12m,
        valuation_rerating=data.get("valuation_rerating"),
        narrative_saturation=data.get("narrative_saturation"),
    )


# ════════════════════════════════════════════════════════════════
# SECTION 7: HELPERS
# ════════════════════════════════════════════════════════════════

def _sigmoid_scale(x, center=0.0, width=1.0):
    """Smoothly map x to 0-1 around a center; width sets the spread."""
    try:
        return round(1 / (1 + math.exp(-(x - center) / (width / 4))), 3)
    except OverflowError:
        return 0.0 if x < center else 1.0


# ════════════════════════════════════════════════════════════════
# SECTION 8: DEMO — the four cases, incl. SanDisk-early vs SanDisk-today
# ════════════════════════════════════════════════════════════════

def run_demo():
    print("\n" + "="*70)
    print("NOW TRENDIN — TREND BENEFICIARY ENGINE — DEMO")
    print("="*70)

    def fins_inflecting():
        # revenue + margins + eps accelerating (the early turn)
        base = []
        rev = 1.0
        for i in range(9):
            rev *= (1.05 if i < 5 else 1.45)   # growth accelerates late
            base.append({"revenue": rev, "gross_margin": 0.20 + i*0.02,
                         "eps": -0.2 + i*0.4})
        return base

    cases = [
        ("SanDisk — EARLY (Feb 2025 setup)", {
            "profile": {"finnhubIndustry": "Semiconductors", "marketCapitalization": 12000,
                        "ipo": "2025-02-01"},
            "financials": fins_inflecting(),
            "news": [{"headline": "SanDisk NAND flash powers AI datacenter storage"}]*8,
            "valuation_rerating": 0.15, "narrative_saturation": 0.2,
        }, {"attn": 78, "ret12": 0.4}),

        ("SanDisk — TODAY (June 2026)", {
            "profile": {"finnhubIndustry": "Semiconductors", "marketCapitalization": 230000,
                        "ipo": "2025-02-01"},
            "financials": fins_inflecting(),
            "news": [{"headline": "SanDisk AI memory NAND storage datacenter surge"}]*10,
            "valuation_rerating": 0.9, "narrative_saturation": 0.95,
        }, {"attn": 85, "ret12": 4.0}),

        ("Junk microcap claiming 'AI'", {
            "profile": {"finnhubIndustry": "Technology", "marketCapitalization": 80,
                        "ipo": "2026-01-01"},
            "financials": [{"revenue": 1, "gross_margin": 0.05, "eps": -1.0}]*9,
            "news": [{"headline": "TinyCo pivots to AI blockchain quantum datacenter"}]*9,
            "valuation_rerating": 0.3, "narrative_saturation": 0.5,
        }, {"attn": 70, "ret12": 2.0}),

        ("Solid company, unrelated to trend", {
            "profile": {"finnhubIndustry": "Consumer Staples", "marketCapitalization": 50000,
                        "ipo": "1995-06-01"},
            "financials": [{"revenue": 100+i, "gross_margin": 0.40, "eps": 2.0+i*0.05}
                           for i in range(9)],
            "news": [{"headline": "Company reports steady quarterly dividend"}]*5,
            "valuation_rerating": 0.1, "narrative_saturation": 0.1,
        }, {"attn": 78, "ret12": 0.1}),
    ]

    for name, data, params in cases:
        result = compute_beneficiary_score(
            "ai_infrastructure", name.split(" —")[0],
            profile=data["profile"], financials=data["financials"],
            recent_news=data["news"],
            theme_attention_score=params["attn"],
            price_return_12m=params["ret12"],
            valuation_rerating=data["valuation_rerating"],
            narrative_saturation=data["narrative_saturation"],
        )
        print(f"\n── {name} ──")
        print(f"  Exposure score: {result['exposure_score']}/100   "
              f"Cycle stage: {result['cycle_stage']}")
        c = result["components"]
        print(f"  Components: theme={c['theme_exposure']} cycle={c['cycle_inflection']} "
              f"struct={c['structural_setup']} attn={c['trend_attention']} "
              f"quality={c['quality']}")
        print(f"  → {result['interpretation']}")

    print("\n" + "="*70)
    print("The key result: SanDisk-EARLY scores high + EARLY (the find);")
    print("SanDisk-TODAY scores high exposure but REALIZED (move already done);")
    print("the junk microcap is excluded by the quality gate; the solid")
    print("unrelated company scores low (no business linkage). The engine")
    print("finds early exposure — it does not chase what already ran.")
    print("="*70)


if __name__ == "__main__":
    run_demo()
