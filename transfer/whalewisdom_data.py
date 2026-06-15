"""
NOW TRENDIN — WHALEWISDOM INSTITUTIONAL HOLDINGS (13F)

Adds a SMART-MONEY / institutional-positioning signal to the risk engine. While
FINRA short interest shows the bears and OFR repo shows system-wide leverage,
WhaleWisdom's 13F data shows what the large institutional managers (the "whales")
are actually holding — the late, slow, high-conviction end of the diffusion model.

Auth: WhaleWisdom uses HMAC-SHA1 signed GET requests. The signature is the
base64 HMAC-SHA1 of "<args_json>\n<rfc1123_timestamp>" keyed by the secret.

COST DISCIPLINE: this account is on a metered tier with a hard period limit
("Subscription limit reached"). We therefore cache aggressively (24h+) and only
pull for watchlist tickers — 13F data changes quarterly, so daily is overkill.
On limit/empty the module degrades to {available: False} and never breaks risk
collection. Every call is metered via collector_health.log_api_call("whalewisdom").
"""
import os
import json
import time
import hmac
import base64
import hashlib
import urllib.parse
import urllib.request
from datetime import datetime, timezone

try:
    from collector_health import log_api_call as _api
except Exception:
    def _api(*a, **k): pass

SHARED_KEY = os.getenv("WHALEWISDOM_SHARED_KEY", "")
SECRET_KEY = os.getenv("WHALEWISDOM_SECRET_KEY", "")
BASE_URL = "https://whalewisdom.com/shell/command.json"
TTL = int(os.getenv("WHALEWISDOM_TTL_SEC", "86400"))  # 24h

_CACHE: dict = {}          # ticker -> {"ts": epoch, "data": dict}
_STOCK_ID_CACHE: dict = {} # ticker -> stock_id


def is_available() -> bool:
    return bool(SHARED_KEY and SECRET_KEY)


def _call(argdict: dict, timeout: int = 25):
    """Signed WhaleWisdom command. Returns parsed JSON or {'errors': [...]}.."""
    args = json.dumps(argdict)
    ts = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    digest = hmac.new(SECRET_KEY.encode(), (args + "\n" + ts).encode(),
                      hashlib.sha1).digest()
    sig = base64.b64encode(digest).decode()
    q = urllib.parse.urlencode({"args": args, "api_shared_key": SHARED_KEY,
                                "api_sig": sig, "timestamp": ts})
    _api("whalewisdom")
    req = urllib.request.Request(BASE_URL + "?" + q,
                                 headers={"User-Agent": "NowTrendIn/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8"))
        except Exception:
            return {"errors": [f"HTTP {e.code}"]}
    except Exception as e:
        return {"errors": [str(e)]}


def _stock_id(ticker: str):
    tkr = (ticker or "").upper()
    if not tkr:
        return None
    if tkr in _STOCK_ID_CACHE:
        return _STOCK_ID_CACHE[tkr]
    res = _call({"command": "stock_lookup", "symbol": tkr})
    sid = None
    for s in (res.get("stocks") or []):
        if (s.get("ticker") or "").upper() == tkr:
            sid = s.get("id")
            break
    if sid:
        _STOCK_ID_CACHE[tkr] = sid
    return sid


def institutional_holdings(ticker: str) -> dict:
    """Institutional 13F positioning for a ticker (smart-money signal).
    Returns {available, ticker, holders_count, shares_held, shares_change_pct,
    top_holders[], sentiment, label} — or {available: False} on limit/empty."""
    if not is_available():
        return {"available": False}
    tkr = (ticker or "").upper()
    cached = _CACHE.get(tkr)
    if cached and (time.time() - cached["ts"] < TTL):
        return cached["data"]

    out = {"available": False, "ticker": tkr}
    sid = _stock_id(tkr)
    if not sid:
        _CACHE[tkr] = {"ts": time.time(), "data": out}
        return out

    res = _call({"command": "holders", "stock_ids": [sid]})
    errs = res.get("errors")
    if errs:
        # Subscription-limit / access errors: cache the negative briefly so we
        # don't hammer the metered quota, but shorter than full TTL.
        out["detail"] = "; ".join(errs)[:160]
        _CACHE[tkr] = {"ts": time.time() - TTL + 3600, "data": out}  # retry in ~1h
        return out

    records = (res.get("records") or res.get("holdings") or
               (res.get("results") or {}).get("records") or [])
    if not records and isinstance(res.get("stocks"), list):
        records = res["stocks"]
    top = []
    total_shares = 0
    total_change = 0.0
    n_change = 0
    for h in records[:200]:
        name = (h.get("filer_name") or h.get("name") or h.get("filer") or "")
        shares = h.get("current_shares") or h.get("shares") or h.get("current_mv") or 0
        chg = h.get("shares_change_percent")
        if chg is None:
            chg = h.get("position_change_type_pct")
        try:
            total_shares += int(shares or 0)
        except Exception:
            pass
        if chg is not None:
            try:
                total_change += float(chg)
                n_change += 1
            except Exception:
                pass
        if name and len(top) < 10:
            top.append({"name": str(name)[:80],
                        "shares": shares,
                        "change_pct": chg})

    avg_change = round(total_change / n_change, 2) if n_change else None
    if avg_change is None:
        sentiment, label = "neutral", "Institutional positioning available"
    elif avg_change > 2:
        sentiment, label = "accumulating", "Institutions accumulating (13F)"
    elif avg_change < -2:
        sentiment, label = "distributing", "Institutions reducing (13F)"
    else:
        sentiment, label = "neutral", "Institutional positioning stable (13F)"

    out = {
        "available": True,
        "ticker": tkr,
        "holders_count": len(records),
        "shares_held": total_shares,
        "shares_change_pct": avg_change,
        "top_holders": top,
        "sentiment": sentiment,
        "label": label,
        "source": "WhaleWisdom 13F",
        "as_of": datetime.now(timezone.utc).isoformat(),
    }
    _CACHE[tkr] = {"ts": time.time(), "data": out}
    return out


if __name__ == "__main__":
    import sys
    t = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    print(json.dumps(institutional_holdings(t), indent=2))
