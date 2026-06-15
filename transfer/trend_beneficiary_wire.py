"""
NOW TRENDIN — TREND BENEFICIARY WIRING

Thin integration layer that connects trend_beneficiary.py (the SanDisk-pattern
exposure engine) to the live Now TrendIn data pipeline. Three jobs:

  1) Theme detection — pick the most relevant theme for a company from its
     news + sector, against the THEMES dict.
  2) Theme attention — read the LIVE Now TrendIn Gradient Score for the
     theme's main keyword from velocity_scores (the elegant link: the
     financial engine is the financial expression of the same trend we detect).
  3) Cycle-stage inputs — pull Finnhub price-1y and valuation metrics
     (gracefully, with caching) so cycle_stage isn't UNKNOWN.

Output slots into the risk positioning_payload as `beneficiary` — same
disclaimer pattern as the rest of the financial side. Every output is a
measurement of business exposure + cycle position, NOT a price prediction.

Caching: Finnhub price/metric pulls cached 6h per ticker (rate-limit safe).
"""
import os
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

try:
    from collector_health import log_api_call as _api
except Exception:
    def _api(*a, **k): pass

try:
    import trend_beneficiary as tb
except Exception as e:
    tb = None
    print(f"[beneficiary] trend_beneficiary import failed: {e}")

try:
    import db_compat
except Exception:
    db_compat = None

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
_BENEFICIARY_TTL = int(os.getenv("BENEFICIARY_TTL_SEC", "21600"))  # 6h
_PRICE_CACHE: dict = {}
_METRIC_CACHE: dict = {}
_THEME_ATTN_CACHE: dict = {"ts": 0, "data": {}}


def _finnhub_get(path: str, params: dict, timeout: int = 12):
    if not FINNHUB_API_KEY:
        return None
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
    params = {**params, "token": FINNHUB_API_KEY}
    url = f"https://finnhub.io/api/v1/{path}?{urlencode(params)}"
    try:
        _api("finnhub")
        with urlopen(Request(url, headers={"User-Agent": "NowTrendIn/2.0"}),
                     timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"  [beneficiary] finnhub {path} error: {e}")
        return None


def fetch_price_return_12m(ticker: str) -> Optional[float]:
    """Fractional 12-month return (e.g. 0.4 = +40%). Cached 6h."""
    cached = _PRICE_CACHE.get(ticker)
    if cached and (time.time() - cached["ts"] < _BENEFICIARY_TTL):
        return cached["value"]
    # Finnhub free tier doesn't include candles, but quote+metric gives us
    # 52-week high/low; we use them as a proxy for cycle-position lateness.
    # /stock/metric returns 52WeekPriceReturnDaily (1y total return %).
    m = _finnhub_get("stock/metric", {"symbol": ticker, "metric": "all"})
    val = None
    if m and isinstance(m.get("metric"), dict):
        ret = m["metric"].get("52WeekPriceReturnDaily")
        if ret is not None:
            try:
                val = float(ret) / 100.0  # convert pct to fraction
            except (TypeError, ValueError):
                val = None
    _PRICE_CACHE[ticker] = {"ts": time.time(), "value": val}
    return val


def fetch_valuation_rerating(ticker: str) -> Optional[float]:
    """Proxy for how far valuation has expanded vs its own recent history.
    0 = compressed, 1 = stretched. Cached 6h."""
    cached = _METRIC_CACHE.get(ticker)
    if cached and (time.time() - cached["ts"] < _BENEFICIARY_TTL):
        return cached["value"]
    m = _finnhub_get("stock/metric", {"symbol": ticker, "metric": "valuation"})
    val = None
    if m and isinstance(m.get("metric"), dict):
        metric = m["metric"]
        pe = metric.get("peNormalizedAnnual") or metric.get("peBasicExtraTtm")
        pe_10y_high = metric.get("peExclExtraHigh10Y")
        pe_10y_low = metric.get("peExclExtraLow10Y")
        if pe and pe_10y_high and pe_10y_low and pe_10y_high > pe_10y_low:
            try:
                ratio = (float(pe) - float(pe_10y_low)) / (float(pe_10y_high) - float(pe_10y_low))
                val = max(0.0, min(1.0, ratio))
            except (TypeError, ValueError, ZeroDivisionError):
                val = None
    _METRIC_CACHE[ticker] = {"ts": time.time(), "value": val}
    return val


def _attention_for_theme(theme_key: str) -> float:
    """Look up live Now TrendIn Gradient detection_score for the theme's
    main keyword. Returns 50 (neutral) if not found. Cached 30 min."""
    if tb is None or db_compat is None:
        return 50.0
    now = time.time()
    if (now - _THEME_ATTN_CACHE["ts"]) > 1800:
        conn = None
        try:
            conn = db_compat.connect(DB_PATH)
            rows = conn.execute(
                "SELECT topic_key, detection_score FROM velocity_scores "
                "WHERE scored_at > ? ORDER BY scored_at DESC",
                ((datetime.now(timezone.utc) - timedelta(hours=48)).isoformat(),)
            ).fetchall()
            best = {}
            for r in rows:
                k = (r["topic_key"] if hasattr(r, "keys") else r[0]) or ""
                v = (r["detection_score"] if hasattr(r, "keys") else r[1]) or 0
                if k and k not in best:
                    best[k] = float(v)
            _THEME_ATTN_CACHE["data"] = best
            _THEME_ATTN_CACHE["ts"] = now
        except Exception as e:
            print(f"  [beneficiary] attention cache error: {e}")
        finally:
            if conn is not None:
                try: conn.close()
                except Exception: pass

    cache = _THEME_ATTN_CACHE["data"]
    # Merge auto-promoted themes so the beneficiary engine sees them.
    try:
        import theme_extension as _te
        all_themes = _te.load_all_themes(DB_PATH)
    except Exception:
        all_themes = tb.THEMES
    theme = all_themes.get(theme_key, {})
    # Try every keyword in the theme; take the highest current score.
    best = 50.0
    found = False
    for kw in theme.get("keywords", []):
        kkey = kw.lower().strip().replace(" ", "_")
        if kkey in cache:
            best = max(best if found else 0, cache[kkey])
            found = True
    return best if found else 50.0


def _detect_theme(profile: dict, recent_news: list) -> Optional[str]:
    """Pick the THEME with the highest theme_exposure score for this company.
    Returns None if no theme reaches the minimum exposure threshold."""
    if tb is None:
        return None
    try:
        import theme_extension as _te
        all_themes = _te.load_all_themes(DB_PATH)
        # Inject auto-themes into tb.THEMES so compute_theme_exposure sees them
        for k, v in all_themes.items():
            if k not in tb.THEMES:
                tb.THEMES[k] = v
    except Exception:
        pass
    best_key, best_score = None, 0.0
    for theme_key in tb.THEMES.keys():
        te = tb.compute_theme_exposure(theme_key, profile, recent_news)
        if te["score"] > best_score:
            best_score = te["score"]
            best_key = theme_key
    # Require at least sector match OR clear keyword density
    return best_key if best_score >= 0.25 else None


def score_company_beneficiary(ticker: str, display_name: str = "") -> Optional[dict]:
    """Full integration call — score one watchlist company against the
    best-matched theme. Pulls live company data + live theme attention +
    Finnhub cycle inputs. Returns the beneficiary payload or None on no-match."""
    if tb is None or not ticker:
        return None
    try:
        data = tb.fetch_company_data(ticker)
        theme_key = _detect_theme(data.get("profile") or {}, data.get("news") or [])
        if not theme_key:
            return None  # no theme exposure → don't pollute the payload
        attention = _attention_for_theme(theme_key)
        price_ret = fetch_price_return_12m(ticker)
        valuation = fetch_valuation_rerating(ticker)
        # narrative_saturation: proxy from attention — if Now TrendIn shows
        # the theme is already STAGE 4-5 mainstream, saturation is high.
        narrative = max(0.0, min(1.0, (attention - 50.0) / 50.0)) if attention > 50 else 0.2

        result = tb.compute_beneficiary_score(
            theme_key, ticker,
            profile=data.get("profile") or {},
            financials=data.get("financials") or [],
            recent_news=data.get("news") or [],
            theme_attention_score=attention,
            price_return_12m=price_ret,
            valuation_rerating=valuation,
            narrative_saturation=narrative,
        )
        result["display"] = display_name or ticker
        result["theme_key"] = theme_key
        result["live_inputs"] = {
            "theme_attention_score": round(attention, 1),
            "price_return_12m": price_ret,
            "valuation_rerating": valuation,
            "narrative_saturation": round(narrative, 2),
        }
        return result
    except Exception as e:
        print(f"  [beneficiary] {ticker} error: {e}")
        return None
