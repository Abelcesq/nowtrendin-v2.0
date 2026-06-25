"""
FMP (Financial Modeling Prep) connector — income statement + profile
→ fundamental score for Market Confidence.

Measurement only — NOT investment advice.  Degraded gracefully when
FMP_API_KEY is absent or the ticker has no data.

Scoring model (0–100, higher = stronger fundamentals):
  Revenue growth YoY  40% — acceleration ahead of mainstream coverage
  Net income margin   35% — profitability quality
  DCF vs price        25% — intrinsic-value alignment

Cache: 6 h (fundamentals change quarterly; we hit FMP once per ticker
per collection cycle, not per request).
"""
from __future__ import annotations
import os, json, math, time
from typing import Optional
from urllib.request import Request, urlopen

FMP_API_KEY: str = os.getenv("FMP_API_KEY", "")
_BASE = "https://financialmodelingprep.com/stable"
_TTL  = int(os.getenv("FMP_TTL_SEC", "21600"))   # 6 h default

_CACHE: dict = {}


def _get(endpoint: str, params: dict) -> Optional[object]:
    if not FMP_API_KEY:
        return None
    from urllib.parse import urlencode
    qs  = urlencode({**params, "apikey": FMP_API_KEY})
    url = f"{_BASE}/{endpoint}?{qs}"
    try:
        req = Request(url, headers={"User-Agent": "NowTrendIn/2.0"})
        with urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as exc:
        print(f"[fmp] {endpoint} {params}: {exc}")
        return None


def _cached(key: str, fn):
    entry = _CACHE.get(key)
    if entry and time.time() - entry["ts"] < _TTL:
        return entry["data"]
    data = fn()
    _CACHE[key] = {"data": data, "ts": time.time()}
    return data


# ── Public helpers ────────────────────────────────────────────────

def income_statement(ticker: str) -> Optional[list]:
    """Latest 2 annual income statements (limit=2 to minimise API quota)."""
    tkr = ticker.upper()
    raw = _cached(f"is:{tkr}", lambda: _get("income-statement",
                                             {"symbol": tkr, "limit": 2}))
    return raw if isinstance(raw, list) else None


def profile(ticker: str) -> Optional[dict]:
    """Company profile: P/E, beta, DCF, mktCap, price, sector."""
    tkr = ticker.upper()
    raw = _cached(f"pr:{tkr}", lambda: _get("profile", {"symbol": tkr}))
    if isinstance(raw, list) and raw:
        return raw[0]
    if isinstance(raw, dict):
        return raw
    return None


def historical_close(ticker: str, frm: str = "", to: str = "") -> Optional[dict]:
    """Daily EOD close prices as {YYYY-MM-DD: close}. The ground-truth price series
    for the MARKET-SIGNAL accuracy ledger (did the realized close move in the detected
    direction?). FMP /stable 'historical-price-eod/light' = date + close + volume.

    Cached 6h; degrades to None when FMP_API_KEY is absent or the ticker has no data.
    A MEASUREMENT input only — never investment advice."""
    tkr = ticker.upper()
    params = {"symbol": tkr}
    if frm:
        params["from"] = frm
    if to:
        params["to"] = to
    key = f"hc:{tkr}:{frm}:{to}"
    raw = _cached(key, lambda: _get("historical-price-eod/light", params))
    if not isinstance(raw, list):
        return None
    out = {}
    for row in raw:
        d = (row.get("date") or "")[:10]
        px = row.get("price", row.get("close"))
        if d and px is not None:
            try:
                out[d] = float(px)
            except (TypeError, ValueError):
                continue
    return out or None


def fundamental_score(ticker: str) -> Optional[dict]:
    """
    Composite 0-100 fundamental score from FMP income statement + profile.

    Returns None when < 2 components can be computed (not enough data to score
    honestly — matches the verify-before-ship rule: never surface a made-up
    number).
    """
    stmts = income_statement(ticker)
    prof  = profile(ticker)

    parts: list[tuple[float, float]] = []   # (score 0-100, weight)
    notes: dict = {}

    # ── Revenue growth YoY (40%) ──────────────────────────────────
    if stmts and len(stmts) >= 2:
        rev_cur  = float(stmts[0].get("revenue") or 0)
        rev_prev = float(stmts[1].get("revenue") or 0)
        if rev_prev > 0 and rev_cur > 0:
            growth = (rev_cur - rev_prev) / rev_prev
            # 0% → 50, +20% → 100, -20% → 0
            g_score = max(0.0, min(100.0, 50.0 + growth * 250.0))
            parts.append((g_score, 0.40))
            notes["revenue_growth_pct"] = round(growth * 100, 1)
            notes["revenue_current"]    = rev_cur

    # ── Net income margin (35%) ───────────────────────────────────
    if stmts and stmts[0]:
        rev = float(stmts[0].get("revenue") or 0)
        ni  = float(stmts[0].get("netIncome") or 0)
        if rev > 0:
            margin = ni / rev
            m_score = max(0.0, min(100.0, 50.0 + margin * 250.0))
            parts.append((m_score, 0.35))
            notes["net_margin_pct"] = round(margin * 100, 1)

    # ── DCF vs price (25%) ────────────────────────────────────────
    if prof:
        dcf   = prof.get("dcf")
        price = prof.get("price") or prof.get("priceAvg50")
        try:
            dcf_f   = float(dcf)   if dcf   is not None else None
            price_f = float(price) if price is not None else None
        except (TypeError, ValueError):
            dcf_f = price_f = None
        if dcf_f and price_f and price_f > 0:
            ratio   = dcf_f / price_f
            d_score = max(0.0, min(100.0, 50.0 + (ratio - 1.0) * 100.0))
            parts.append((d_score, 0.25))
            notes["dcf"]             = round(dcf_f, 2)
            notes["price"]           = round(price_f, 2)
            notes["dcf_premium_pct"] = round((ratio - 1.0) * 100.0, 1)

    if len(parts) < 2:
        return None    # need ≥2 components to score honestly

    wsum  = sum(w for _, w in parts)
    score = sum(v * w for v, w in parts) / wsum

    return {
        "score":            round(score, 1),
        "score_normalized": round(score / 100.0, 4),
        "components":       notes,
        "ticker":           ticker.upper(),
        "source":           "Financial Modeling Prep",
    }
