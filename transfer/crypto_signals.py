"""
crypto_signals.py — HELD-OUT Crypto Money Gradient research (Phase 1; imported by NOTHING in scoring).

A per-coin MONEY GRADIENT for crypto, mirroring the equity Money Gradient (Market Signal v2) but with
crypto-appropriate sources. We do NOT read on-chain wallet flows directly (that needs a new paid source —
Glassnode/Nansen); v1 reads institutional / informed money via crypto-EXPOSURE PROXY securities:

  MONEY MOVEMENT (Detection / D) — informed money into crypto exposure, via proxies:
    • Spot-crypto ETF 13F flow         IBIT/FBTC/GBTC (BTC) · ETHA/ETHE (ETH) — institutions reporting crypto-ETF positions
    • Crypto-treasury / exchange names MSTR (largest corporate BTC holder) · COIN (Coinbase) — insider Form-4 + 13F
    • (Phase 2) Congress crypto trades (Quiver) · CME BTC/ETH futures positioning + microstructure (Databento GLBX.MDP3)

  MARKET CONFIRMATION (Confidence / M) — the coin's OWN price / volume momentum (the broad crypto market
    confirming the move), via FMP (BTCUSD…) with AV DIGITAL_CURRENCY_DAILY as fallback.

  FLOW (inflow / outflow) — consensus direction of D (proxy accumulation / distribution) and M (price momentum).

Dark Matter for crypto is STRONGEST for BTC (multiple ETFs + MSTR + COIN) and ETH (ETFs + COIN); altcoins
beyond these have only COIN as a proxy — an honest limitation surfaced per coin (`proxy_coverage`).

Discipline: HELD-OUT (imported by nothing in scoring) → research the output → BACKTEST-BEFORE-SHIP against a
crypto accuracy ledger (realized coin price direction) → only then a flag-gated Crypto Money Gradient + /crypto
page + nav. A FACT of where money is moving — NEVER advice, never a buy/sell signal, never a price prediction.
"""
from __future__ import annotations
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

try:
    import fmp_data
except Exception:                       # pragma: no cover - import shape varies by entrypoint
    fmp_data = None
try:
    import av_dark_positioning as avdp
except Exception:                       # pragma: no cover
    avdp = None

# ── Coin universe + crypto-exposure proxies ────────────────────────────────────────────────
# kind: etf (spot-crypto ETF 13F) · treasury (corp holding the coin) · exchange (crypto venue).
# weight: how directly the proxy tracks THIS coin's institutional flow (1.0 = a dedicated spot ETF).
COIN_UNIVERSE: dict = {
    "BTC": {
        "name": "Bitcoin", "fmp": "BTCUSD", "av": "BTC",
        "proxies": [
            {"ticker": "IBIT", "kind": "etf",      "weight": 1.0},   # BlackRock spot BTC ETF (largest)
            {"ticker": "FBTC", "kind": "etf",      "weight": 0.8},   # Fidelity spot BTC ETF
            {"ticker": "GBTC", "kind": "etf",      "weight": 0.7},   # Grayscale BTC trust/ETF
            {"ticker": "MSTR", "kind": "treasury", "weight": 0.9},   # MicroStrategy — largest corp BTC holder
            {"ticker": "COIN", "kind": "exchange", "weight": 0.5},   # Coinbase — broad crypto exposure
        ],
    },
    "ETH": {
        "name": "Ethereum", "fmp": "ETHUSD", "av": "ETH",
        "proxies": [
            {"ticker": "ETHA", "kind": "etf",      "weight": 1.0},   # BlackRock spot ETH ETF
            {"ticker": "ETHE", "kind": "etf",      "weight": 0.7},   # Grayscale ETH trust/ETF
            {"ticker": "COIN", "kind": "exchange", "weight": 0.5},
        ],
    },
    "SOL": {
        "name": "Solana", "fmp": "SOLUSD", "av": "SOL",
        "proxies": [
            {"ticker": "COIN", "kind": "exchange", "weight": 0.5},   # no dedicated spot ETF in roster → thin
        ],
    },
    "XRP": {
        "name": "XRP", "fmp": "XRPUSD", "av": "XRP",
        "proxies": [
            {"ticker": "COIN", "kind": "exchange", "weight": 0.4},
        ],
    },
    "DOGE": {
        "name": "Dogecoin", "fmp": "DOGEUSD", "av": "DOGE",
        "proxies": [
            {"ticker": "COIN", "kind": "exchange", "weight": 0.3},
        ],
    },
    # Additional majors (FMP price verified). Proxy = COIN only (broad crypto-exposure) → Dark Matter
    # is THIN / shared for alts: Money Movement reads institutional crypto sentiment via Coinbase, while
    # Market Confirmation (price/volume) is coin-specific. Per-coin proxies improve as spot ETFs list.
    "BNB":  {"name": "BNB",          "fmp": "BNBUSD",  "av": "BNB",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.3}]},
    "ADA":  {"name": "Cardano",      "fmp": "ADAUSD",  "av": "ADA",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.4}]},
    "AVAX": {"name": "Avalanche",    "fmp": "AVAXUSD", "av": "AVAX",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.4}]},
    "LINK": {"name": "Chainlink",    "fmp": "LINKUSD", "av": "LINK",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.4}]},
    "DOT":  {"name": "Polkadot",     "fmp": "DOTUSD",  "av": "DOT",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.4}]},
    "LTC":  {"name": "Litecoin",     "fmp": "LTCUSD",  "av": "LTC",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.4}]},
    "BCH":  {"name": "Bitcoin Cash", "fmp": "BCHUSD",  "av": "BCH",
             "proxies": [{"ticker": "COIN", "kind": "exchange", "weight": 0.4}]},
}

PRICE_LOOKBACK_DAYS = int(os.getenv("CRYPTO_PRICE_LOOKBACK_DAYS", "45"))


def available() -> dict:
    """Which data legs are wired (held-out plumbing check)."""
    return {
        "price_fmp": bool(fmp_data and getattr(fmp_data, "FMP_API_KEY", "")),
        "dark_matter_av": bool(avdp and avdp.available()),
    }


# ── MARKET CONFIRMATION (M): the coin's own price/volume momentum ────────────────────────────
def _pct(a: float, b: float) -> Optional[float]:
    return None if not b else (a - b) / b * 100.0


def _closest_on_or_before(series: dict, target: str) -> Optional[float]:
    """Latest close at or before `target` (handles weekends/gaps; crypto trades 7d but FMP can gap)."""
    keys = sorted(k for k in series if k <= target)
    return series[keys[-1]] if keys else None


_AV_PRICE_CACHE: dict = {}


def _av_crypto_series(coin: str) -> Optional[dict]:
    """AV DIGITAL_CURRENCY_DAILY → {date: close_usd}. Fallback when FMP is throttled (free-tier 429).
    AV has headroom now that Finviz owns the insider pulls. Cached per process (daily series)."""
    import time as _t
    key = os.getenv("ALPHAVANTAGE_RESEARCH_KEY") or os.getenv("ALPHAVANTAGE_API_KEY", "")
    if not key:
        return None
    sym = (COIN_UNIVERSE.get(coin.upper()) or {}).get("av") or coin.upper()
    ent = _AV_PRICE_CACHE.get(sym)
    if ent and (_t.time() - ent["ts"] < 21600):       # 6h cache
        return ent["data"]
    import json as _json, urllib.request as _ur, urllib.parse as _up
    url = "https://www.alphavantage.co/query?" + _up.urlencode(
        {"function": "DIGITAL_CURRENCY_DAILY", "symbol": sym, "market": "USD", "apikey": key})
    out = None
    try:
        with _ur.urlopen(url, timeout=20) as r:
            d = _json.loads(r.read().decode("utf-8"))
        ts = d.get("Time Series (Digital Currency Daily)") or {}
        parsed = {}
        for date, row in ts.items():
            v = row.get("4. close") or row.get("4a. close (USD)")
            try:
                parsed[date] = float(v)
            except (TypeError, ValueError):
                continue
        out = parsed or None
    except Exception as e:
        print(f"[crypto av-price] {sym}: {e}")
    _AV_PRICE_CACHE[sym] = {"data": out, "ts": _t.time()}
    return out


def price_momentum(coin: str) -> dict:
    """The coin's price trend = the broad crypto market CONFIRMING (or not) the move. A measurement.
    FMP primary; AV DIGITAL_CURRENCY_DAILY fallback when FMP is throttled (free-tier 429)."""
    c = COIN_UNIVERSE.get(coin.upper())
    if not c:
        return {"available": False, "reason": "unknown coin"}
    today = datetime.now(timezone.utc).date()
    frm = (today - timedelta(days=PRICE_LOOKBACK_DAYS)).isoformat()
    series, src = None, ""
    if fmp_data and getattr(fmp_data, "FMP_API_KEY", ""):
        series = fmp_data.historical_close(c["fmp"], frm=frm, to=today.isoformat())
        if series:
            src = "fmp"
    if not series:                                     # FMP empty/throttled → AV crypto fallback
        series = _av_crypto_series(coin)
        if series:
            src = "alphavantage"
    if not series:
        return {"available": False, "reason": "no price series (FMP+AV)", "symbol": c["fmp"]}
    dates = sorted(series)
    last_d = dates[-1]
    last = series[last_d]
    d7 = (datetime.fromisoformat(last_d).date() - timedelta(days=7)).isoformat()
    d30 = (datetime.fromisoformat(last_d).date() - timedelta(days=30)).isoformat()
    c7 = _closest_on_or_before(series, d7)
    c30 = _closest_on_or_before(series, d30)
    m7 = _pct(last, c7) if c7 else None
    m30 = _pct(last, c30) if c30 else None
    trend = "flat"
    if m7 is not None:
        trend = "up" if m7 > 1.0 else "down" if m7 < -1.0 else "flat"
    # Confirmation strength 0-100: scaled |7d move|, bonus when 7d and 30d agree (sustained, not a blip).
    base = min(100.0, abs(m7) * 6.0) if m7 is not None else 0.0   # ~16.7% move → 100
    aligned = m7 is not None and m30 is not None and (m7 > 0) == (m30 > 0)
    confirmation = round(min(100.0, base * (1.15 if aligned else 0.85)), 1)
    return {
        "available": True, "symbol": c["fmp"], "source": src, "as_of": last_d, "last_close": round(last, 4),
        "change_7d_pct": None if m7 is None else round(m7, 2),
        "change_30d_pct": None if m30 is None else round(m30, 2),
        "trend": trend, "aligned_7d_30d": aligned, "confirmation": confirmation,
    }


# ── MONEY MOVEMENT (D): informed money via proxy securities ─────────────────────────────────
def _proxy_vote(sig: dict) -> Optional[float]:
    """Signed [-1,1] directional vote for ONE proxy from av_dark_positioning.signal_for output.
    Insider: BUYING (signal=='accumulation') → +1; routine net selling is low-information → no insider
    vote (insider net is structurally sell-dominated, so it's not treated as bearish). Institutional
    13F is genuinely two-sided → +1/-1 on net share flow. None = no usable signal."""
    if not sig:
        return None
    votes = []
    ins = sig.get("insider") or {}
    if ins.get("available") and ins.get("signal") == "accumulation":
        votes.append(1.0)                       # rare, high-conviction insider BUY
    inst = sig.get("institutional") or {}
    if inst.get("available"):
        ns = inst.get("net_shares") or 0
        if ns > 0:
            votes.append(1.0)
        elif ns < 0:
            votes.append(-1.0)
    if not votes:
        return None
    return sum(votes) / len(votes)


def proxy_dark_matter(coin: str, max_proxies: Optional[int] = None) -> dict:
    """Aggregate informed-money direction across the coin's crypto-exposure proxies.
    Returns a weighted net direction (inflow/outflow), an intensity 0-100, and per-proxy detail.
    HELD-OUT — a FACT from filings, not advice. `max_proxies` trims AV calls during testing."""
    c = COIN_UNIVERSE.get(coin.upper())
    if not c:
        return {"available": False, "reason": "unknown coin"}
    if not (avdp and avdp.source_available()):
        return {"available": False, "reason": "no dark-positioning source configured (AV or Finviz)"}
    proxies = c["proxies"][: max_proxies] if max_proxies else c["proxies"]
    detail = []
    num = 0.0          # weighted signed direction
    den = 0.0          # sum of weights that produced a usable vote
    for p in proxies:
        sig = avdp.signal_for(p["ticker"], name=p["ticker"])
        vote = _proxy_vote(sig)
        ins = (sig or {}).get("insider") or {}
        inst = (sig or {}).get("institutional") or {}
        detail.append({
            "ticker": p["ticker"], "kind": p["kind"], "weight": p["weight"],
            "vote": vote, "combined_flow": (sig or {}).get("combined_flow"),
            "insider_net_usd": ins.get("net_usd"), "inst_net_shares": inst.get("net_shares"),
            "has_data": vote is not None,
        })
        if vote is not None:
            num += p["weight"] * vote
            den += p["weight"]
    covered = sum(1 for d in detail if d["has_data"])
    total = len(c["proxies"])
    net = (num / den) if den else 0.0
    flow = "inflow" if net > 0.15 else "outflow" if net < -0.15 else ("mixed" if den else "no_data")
    # Intensity: direction magnitude × coverage confidence (more proxies reporting = more defensible).
    coverage_conf = covered / total if total else 0.0
    intensity = round(min(100.0, abs(net) * 100.0 * (0.5 + 0.5 * coverage_conf)), 1)
    return {
        "available": den > 0, "flow": flow, "net_direction": round(net, 3), "intensity": intensity,
        "proxies_covered": covered, "proxies_total": total,
        "proxy_coverage": "strong" if total >= 4 and covered >= 2 else "thin" if total <= 1 else "partial",
        "detail": detail,
    }


# ── Combined per-coin Money Gradient ────────────────────────────────────────────────────────
def signal_for(coin: str, with_dark_matter: bool = True, max_proxies: Optional[int] = None) -> dict:
    """Per-coin Crypto Money Gradient = Money Movement (D, proxies) + Market Confirmation (M, price).
    HELD-OUT research output — a measurement of where money is moving, NEVER advice."""
    coin = coin.upper()
    c = COIN_UNIVERSE.get(coin)
    if not c:
        return {"available": False, "reason": "unknown coin", "coin": coin}
    m = price_momentum(coin)
    d = proxy_dark_matter(coin, max_proxies=max_proxies) if with_dark_matter else {"available": False, "reason": "skipped"}

    # Overall flow = consensus of D (informed) and M (market). D leads (it's the early read); M confirms.
    d_flow = d.get("flow") if d.get("available") else None
    m_trend = m.get("trend") if m.get("available") else None
    m_dir = {"up": "inflow", "down": "outflow", "flat": "neutral"}.get(m_trend or "")
    if d_flow in ("inflow", "outflow") and m_dir in ("inflow", "outflow"):
        consensus = d_flow if d_flow == m_dir else "divergent"
    else:
        consensus = d_flow or m_dir or "no_data"

    return {
        "available": bool(m.get("available") or d.get("available")),
        "coin": coin, "name": c["name"], "held_out": True,
        "money_movement": {                       # D — informed money (proxies)
            "flow": d.get("flow"), "intensity": d.get("intensity"),
            "coverage": d.get("proxy_coverage"), "proxies_covered": d.get("proxies_covered"),
            "available": d.get("available", False),
        },
        "market_confirmation": {                  # M — the coin's own price
            "trend": m.get("trend"), "strength": m.get("confirmation"),
            "change_7d_pct": m.get("change_7d_pct"), "change_30d_pct": m.get("change_30d_pct"),
            "available": m.get("available", False),
        },
        "consensus_flow": consensus,
        "_price": m, "_dark_matter": d,
        "note": "HELD-OUT crypto research (proxy-based Dark Matter + price momentum). NOT in any score yet; "
                "backtest-before-ship. A FACT of where money is moving — not advice, not a prediction.",
    }


def research(coins: Optional[list] = None, with_dark_matter: bool = False,
             max_proxies: Optional[int] = None, pace_sec: float = 1.5) -> dict:
    """Run signal_for over the universe. `with_dark_matter=False` keeps it to cheap FMP price calls;
    enable it (paced, AV 25/day) only when researching the proxy Dark Matter. `pace_sec` spaces the
    per-coin FMP price calls so the free-tier burst limit (HTTP 429) isn't tripped on a multi-coin run."""
    coins = coins or list(COIN_UNIVERSE)
    out = []
    for i, c in enumerate(coins):
        out.append(signal_for(c, with_dark_matter=with_dark_matter, max_proxies=max_proxies))
        if pace_sec and i < len(coins) - 1:
            time.sleep(pace_sec)
    return {"held_out": True, "available": available(), "count": len(out), "signals": out,
            "note": "Held-out crypto Money Gradient research — NOT integrated into any score. Backtest-before-ship."}


if __name__ == "__main__":
    import sys, json
    dm = "--dm" in sys.argv
    mp = None
    for a in sys.argv:
        if a.startswith("--max="):
            mp = int(a.split("=", 1)[1])
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    coins = [a.upper() for a in args] or None
    print("available:", available())
    r = research(coins, with_dark_matter=dm, max_proxies=mp)
    for s in r["signals"]:
        mm, mc = s.get("money_movement", {}), s.get("market_confirmation", {})
        print(f"\n{s.get('coin'):5} {s.get('name','')}")
        print(f"   Market Confirmation (M): {mc.get('trend')} strength={mc.get('strength')} "
              f"7d={mc.get('change_7d_pct')}% 30d={mc.get('change_30d_pct')}%")
        print(f"   Money Movement (D):      flow={mm.get('flow')} intensity={mm.get('intensity')} "
              f"coverage={mm.get('coverage')} ({mm.get('proxies_covered')} proxies)")
        print(f"   Consensus flow:          {s.get('consensus_flow')}")
        if dm and s.get("_dark_matter", {}).get("detail"):
            for d in s["_dark_matter"]["detail"]:
                print(f"      - {d['ticker']:5} {d['kind']:9} vote={d['vote']} "
                      f"insider=${d.get('insider_net_usd')} inst_sh={d.get('inst_net_shares')}")
