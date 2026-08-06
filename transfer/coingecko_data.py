"""
coingecko_data.py — CoinGecko (+ CoinMarketCap second-opinion) keyless client.

§16 ONBOARDED 2026-08-05 PT (founder-approved; review + live tests:
audits/source-onboarding/COINGECKO_CMC_KEYLESS_REVIEW_2026-08-05.md).
ROLE (strict): DISPLAY-ONLY supply/market facts (C1/C2 `supply_facts` — Chairman ruling
2026-08-05: CoinGecko REPLACES FMP where FMP is proven inaccurate; first proven case =
circulating supply, FMP's marketCap basis ~7 months stale for BTC) + the HELD-OUT
price/supply REFEREE in the monitor fleet. NEVER a scoring input; NEVER volume-as-flow
(C5/C6 prohibition). §15's no-aggregators rule governs scoring inputs, not display
facts or verifiers.

Keyless limits (official docs): CoinGecko ~10-30 calls/min; CMC shared IP pool.
We make ONE batched call per vendor per TTL window (default 15 min) for the whole
universe — orders of magnitude inside the limits. FAIL-OPEN: any error returns None;
callers fall back (supply_facts → FMP) or report "referee unavailable" — never block,
never fabricate.
"""
from __future__ import annotations

import json
import os
import time
from urllib.request import Request, urlopen

_UA = os.getenv("RECONCILE_UA", "NowTrendIn/2.0 (data verification)")
_TTL_S = int(os.getenv("COINGECKO_TTL_S", "900"))

#: Coin symbol → CoinGecko id (the tracked 12-coin universe).
GECKO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "XRP": "ripple",
    "BNB": "binancecoin", "DOGE": "dogecoin", "ADA": "cardano",
    "AVAX": "avalanche-2", "LINK": "chainlink", "DOT": "polkadot",
    "LTC": "litecoin", "BCH": "bitcoin-cash",
}

#: Coin symbol → CoinMarketCap id (verified against /v1/cryptocurrency/map).
CMC_IDS = {
    "BTC": 1, "ETH": 1027, "SOL": 5426, "XRP": 52, "BNB": 1839, "DOGE": 74,
    "ADA": 2010, "AVAX": 5805, "LINK": 1975, "DOT": 6636, "LTC": 2, "BCH": 1831,
}

_cache: dict = {}


def _get_json(url: str, timeout: int = 20):
    req = Request(url, headers={"User-Agent": _UA, "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def _cached(key: str, fetch):
    now = time.time()
    hit = _cache.get(key)
    if hit and now - hit[0] < _TTL_S:
        return hit[1]
    try:
        val = fetch()
    except Exception:
        # Serve a stale hit rather than nothing, but stamp it; else None (fail-open).
        return hit[1] if hit else None
    _cache[key] = (now, val)
    return val


def markets() -> dict | None:
    """{SYMBOL: {price, market_cap, circulating_supply, total_supply, max_supply,
    last_updated}} — ONE batched CoinGecko /coins/markets call for the whole universe."""
    def _fetch():
        ids = ",".join(GECKO_IDS.values())
        rows = _get_json("https://api.coingecko.com/api/v3/coins/markets"
                         f"?vs_currency=usd&ids={ids}&per_page=250")
        by_id = {r.get("id"): r for r in rows if isinstance(r, dict)}
        out = {}
        for sym, gid in GECKO_IDS.items():
            r = by_id.get(gid)
            if not r:
                continue
            out[sym] = {
                "price": r.get("current_price"),
                "market_cap": r.get("market_cap"),
                "circulating_supply": r.get("circulating_supply"),
                "total_supply": r.get("total_supply"),
                "max_supply": r.get("max_supply"),
                "last_updated": r.get("last_updated"),
                "source": "CoinGecko",
            }
        return out or None
    return _cached("cg:markets", _fetch)


def coin_market(symbol: str) -> dict | None:
    m = markets()
    return (m or {}).get(symbol.upper())


def cmc_prices() -> dict | None:
    """{SYMBOL: price} — ONE batched CoinMarketCap keyless call (referee second
    opinion ONLY; nothing served reads this)."""
    def _fetch():
        ids = ",".join(str(i) for i in CMC_IDS.values())
        d = _get_json("https://pro-api.coinmarketcap.com/public-api/v1/simple/price"
                      f"?ids={ids}&convert=USD")
        by_id = {int(r.get("id")): r.get("price")
                 for r in (d.get("data") or []) if isinstance(r, dict)}
        out = {sym: by_id.get(cid) for sym, cid in CMC_IDS.items()
               if by_id.get(cid) is not None}
        return out or None
    return _cached("cmc:prices", _fetch)


if __name__ == "__main__":
    print(json.dumps({"markets": markets(), "cmc": cmc_prices()}, indent=1)[:1600])
