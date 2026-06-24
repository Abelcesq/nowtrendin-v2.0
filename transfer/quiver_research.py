"""
QuiverQuant congressional-trading research — HELD-OUT.

Imported by NOTHING in the scoring path (like sec_13f_research / referee_wikipedia). Surfaces
where CONGRESS trades — a political-smart-money positioning signal.

Source Onboarding Protocol (CLAUDE.md §16) — verified 2026-06-24, all 5 gates PASS:
  1. TYPE      — MARKET POSITIONING (congressional / political smart-money trades).
  2. ENGINE    — Market Signal "Dark Positioning" (financial_risk_gradient), alongside SEC 13F +
                 insider Form-4. NOT wired yet — research-before-integrate, then backtest.
  3. FORMAT    — clean structured JSON (ticker · transaction · size · date · party · chamber ·
                 excess_return). Trade dates → ISO via gate_date() at integration time.
  4. CURRENCY  — api.quiverquant.com, Bearer token (env QUIVER_API_KEY); /bulk = 113k+ rows,
     + ACCESS    current to the day; /live = recent feed (also works token-less). HTTP 200.
  5. TEST      — this module + /research/congress is the review surface. Backtest before any
                 integration into positioning_concentration.

Replaces the 4 raw URLs that FAILED onboarding (House/Senate Stock Watcher S3 = 403 dead;
CapitolTrades = 429; QuiverQuant HTML page = unstructured) with the structured API.
"""
from __future__ import annotations
import os
import requests
from collections import defaultdict

QUIVER_API_KEY = os.getenv("QUIVER_API_KEY", "")
_BASE = "https://api.quiverquant.com"


def _get(path: str):
    headers = {"Accept": "application/json", "User-Agent": "NowTrendIn/1.0 (research)"}
    if QUIVER_API_KEY:
        headers["Authorization"] = f"Bearer {QUIVER_API_KEY}"
    try:
        r = requests.get(_BASE + path, headers=headers, timeout=30)
        if r.status_code != 200:
            return {"_error": f"HTTP {r.status_code}", "_body": r.text[:160]}
        return r.json()
    except Exception as e:
        return {"_error": str(e)}


def _field(r: dict, *names):
    for n in names:
        v = r.get(n)
        if v not in (None, ""):
            return v
    return ""


def congress_recent(limit: int = 25, top_n: int = 15) -> dict:
    """Recent congressional trades + per-ticker aggregation (who's buying/selling what).
    Uses the /live feed. Read-only, held-out — never feeds a score."""
    data = _get("/beta/live/congresstrading")
    if not isinstance(data, list):
        return {"available": False, "source": "QuiverQuant /beta/live/congresstrading",
                "reason": (data or {}).get("_error", "fetch failed") if isinstance(data, dict) else "no data"}

    by_ticker = defaultdict(lambda: {"buys": 0, "sells": 0, "members": set(), "usd": 0.0})
    for r in data:
        t = (_field(r, "Ticker") or "").upper()
        if not t:
            continue
        a = by_ticker[t]
        tx = (_field(r, "Transaction") or "").lower()
        if "purchase" in tx or "buy" in tx:
            a["buys"] += 1
        elif "sale" in tx or "sell" in tx:
            a["sells"] += 1
        a["members"].add(_field(r, "Representative", "Name"))
        try:
            a["usd"] += float(_field(r, "Trade_Size_USD") or 0)
        except Exception:
            pass

    top = sorted(by_ticker.items(), key=lambda kv: (len(kv[1]["members"]), kv[1]["buys"] + kv[1]["sells"]),
                 reverse=True)[:top_n]
    return {
        "available": True,
        "source": "QuiverQuant /beta/live/congresstrading",
        "held_out": True,
        "rows": len(data),
        "distinct_tickers": len(by_ticker),
        # "where political money is concentrating": tickers most members traded
        "top_tickers": [
            {"ticker": t, "members": len(v["members"]), "buys": v["buys"], "sells": v["sells"],
             "net": v["buys"] - v["sells"]}
            for t, v in top
        ],
        "recent_trades": [
            {"member": _field(r, "Representative", "Name"),
             "party": _field(r, "Party"), "chamber": _field(r, "Chamber"),
             "ticker": _field(r, "Ticker"), "transaction": _field(r, "Transaction"),
             "traded": _field(r, "TransactionDate", "Traded"),
             "reported": _field(r, "ReportDate", "Filed"),
             "range": _field(r, "Range")}
            for r in data[:limit]
        ],
        "note": "HELD-OUT research — not wired into any score. /bulk has 113k+ historical rows "
                "for the backtest step. Review before integration into Market Signal Dark Positioning.",
    }


if __name__ == "__main__":
    import json
    r = congress_recent()
    print("auth key present:", bool(QUIVER_API_KEY))
    print(json.dumps({k: v for k, v in r.items() if k not in ("recent_trades",)}, indent=2, default=str))
    for x in r.get("recent_trades", [])[:8]:
        print(f"  {str(x['member'])[:24]:24} {x['transaction']:9} {x['ticker']:6} traded {x['traded']}")
