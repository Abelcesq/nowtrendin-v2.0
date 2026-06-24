"""
Return-prediction probe for the Congress signal — HELD-OUT, transparency record.

⚠ FRAMING (corrected 2026-06-24): this asks "does Congressional trading PREDICT forward
returns?" — an INVESTMENT-ALPHA question Now TrendIn does NOT ask. We do not predict prices
or recommend trades. The platform MEASURES MOVEMENT (attention + money) and states leverage
FACTS; it is not a financial/investment service. So this is NOT the integration gate. It is
kept only as an honest transparency record (and it confirms, usefully, that the public
Congressional feed carries no return edge — which is exactly why we make no such claim).

The REAL criterion for the dark-positioning signal is MEASUREMENT FIDELITY: does it faithfully
report where institutional/Congressional money is moving (in/out + intensity), straight from
the filings? It does, by construction (positioning_intel reads the filings directly). That is
the basis for integration — as a money-MOVEMENT input, never as a price predictor.

[Original probe below — does the signal predict forward returns, no-lookahead, vs Yahoo prices?]

INTEGRITY — NO LOOKAHEAD:
  • The signal at decision date T uses ONLY trades whose **Filed** date <= T (the date the
    trade became PUBLIC under the STOCK Act), NOT the Traded date. Using Traded would leak
    the future (the public can't act on a trade before it's disclosed).
  • Forward return is measured from T (a date in the past) to T+horizon, from an INDEPENDENT
    price source (Yahoo chart API) — not from QuiverQuant's own excess_return field.

Data: QuiverQuant /bulk congresstrading (113k rows, 2014→present, Ticker/Transaction/Filed).
Output: per-cohort forward returns (net-buy vs net-sell vs neutral), long-short spread, the
information coefficient (rank corr of signal vs return), hit rate, and sample sizes.
"""
from __future__ import annotations
import os
import time
import json
import math
import urllib.request
from datetime import datetime, timedelta
from collections import defaultdict

QUIVER_API_KEY = os.getenv("QUIVER_API_KEY", "")
_PRICE_CACHE: dict = {}
_BULK_CACHE: list = []


def _http_json(url, headers=None, timeout=40):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def congress_bulk():
    global _BULK_CACHE
    if _BULK_CACHE:
        return _BULK_CACHE
    data = _http_json("https://api.quiverquant.com/beta/bulk/congresstrading",
                      headers={"Authorization": f"Bearer {QUIVER_API_KEY}",
                               "User-Agent": "NowTrendIn/1.0"})
    _BULK_CACHE = data if isinstance(data, list) else []
    return _BULK_CACHE


def _iso(d):
    return d if isinstance(d, str) else d.strftime("%Y-%m-%d")


def prices(ticker: str) -> dict:
    """{YYYY-MM-DD: close} daily, ~6y, from Yahoo. Cached; sleeps to be polite."""
    t = ticker.upper()
    if t in _PRICE_CACHE:
        return _PRICE_CACHE[t]
    out = {}
    try:
        time.sleep(0.4)
        d = _http_json(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=6y&interval=1d")
        res = (d.get("chart", {}).get("result") or [None])[0]
        if res:
            ts = res.get("timestamp", []) or []
            cl = (res.get("indicators", {}).get("quote", [{}])[0].get("close", []) or [])
            for u, c in zip(ts, cl):
                if c is not None:
                    out[datetime.utcfromtimestamp(u).strftime("%Y-%m-%d")] = float(c)
    except Exception as e:
        print(f"[bt] price {t}: {e}")
    _PRICE_CACHE[t] = out
    return out


def _close_on_or_after(px: dict, date_str: str, max_skip: int = 6):
    d0 = datetime.strptime(date_str, "%Y-%m-%d")
    for i in range(max_skip):
        k = (d0 + timedelta(days=i)).strftime("%Y-%m-%d")
        if k in px:
            return px[k]
    return None


def fwd_return(ticker: str, asof: str, horizon_days: int):
    px = prices(ticker)
    if not px:
        return None
    p0 = _close_on_or_after(px, asof)
    p1 = _close_on_or_after(px, (datetime.strptime(asof, "%Y-%m-%d") + timedelta(days=horizon_days)).strftime("%Y-%m-%d"))
    if not p0 or not p1 or p0 <= 0:
        return None
    return (p1 - p0) / p0


def signals_by_ticker_date(window_days: int):
    """Pre-index: for every ticker, the trades grouped — returns a function net(ticker, asof)
    using only trades FILED <= asof within the trailing window. NO LOOKAHEAD."""
    by_ticker = defaultdict(list)   # ticker -> [(filed_date, +1 buy / -1 sell, member)]
    for r in congress_bulk():
        t = (r.get("Ticker") or "").upper().strip()
        filed = (r.get("Filed") or "")[:10]
        tx = (r.get("Transaction") or "").lower()
        if not t or not filed or len(filed) != 10:
            continue
        sgn = 1 if ("purchase" in tx or "buy" in tx) else -1 if ("sale" in tx or "sell" in tx) else 0
        if sgn:
            by_ticker[t].append((filed, sgn, r.get("Name")))

    def net(ticker, asof):
        lo = (datetime.strptime(asof, "%Y-%m-%d") - timedelta(days=window_days)).strftime("%Y-%m-%d")
        buys = sells = 0
        for filed, sgn, _m in by_ticker.get(ticker.upper(), []):
            if lo <= filed <= asof:                      # Filed in (asof-window, asof] — public by T
                if sgn > 0: buys += 1
                else: sells += 1
        return buys, sells
    return net, by_ticker


def run(top_tickers: int = 30, window_days: int = 90, horizon_days: int = 21,
        start: str = "2022-01-01", months: int = 50, min_trades: int = 3) -> dict:
    bulk = congress_bulk()
    if not bulk:
        return {"available": False, "reason": "congress bulk fetch failed"}
    # universe = most-traded tickers (liquid; have price history)
    cnt = defaultdict(int)
    for r in bulk:
        t = (r.get("Ticker") or "").upper().strip()
        if t and t.isalpha() and len(t) <= 5:
            cnt[t] += 1
    universe = [t for t, _ in sorted(cnt.items(), key=lambda kv: -kv[1])[:top_tickers]]

    net_fn, _ = signals_by_ticker_date(window_days)
    # monthly decision dates, leaving forward room
    dates = []
    d = datetime.strptime(start, "%Y-%m-%d")
    cutoff = datetime.utcnow() - timedelta(days=horizon_days + 7)
    for _ in range(months):
        if d > cutoff:
            break
        dates.append(d.strftime("%Y-%m-%d"))
        d = (d.replace(day=1) + timedelta(days=32)).replace(day=1)

    obs = []   # (signal_net, fwd_return, cohort)
    for t in universe:
        for T in dates:
            buys, sells = net_fn(t, T)
            if buys + sells < min_trades:
                continue
            ret = fwd_return(t, T, horizon_days)
            if ret is None:
                continue
            net = buys - sells
            cohort = "buy" if net > 0 else "sell" if net < 0 else "neutral"
            obs.append((net, ret, cohort, buys, sells))

    if len(obs) < 20:
        return {"available": False, "reason": f"too few observations ({len(obs)})"}

    def avg(xs): return sum(xs) / len(xs) if xs else 0.0
    buy_r = [r for n, r, c, b, s in obs if c == "buy"]
    sell_r = [r for n, r, c, b, s in obs if c == "sell"]
    neu_r = [r for n, r, c, b, s in obs if c == "neutral"]
    # information coefficient: rank corr of net signal vs forward return (Spearman-ish)
    nets = [n for n, r, c, b, s in obs]
    rets = [r for n, r, c, b, s in obs]
    def _rank(xs):
        order = sorted(range(len(xs)), key=lambda i: xs[i])
        rk = [0] * len(xs)
        for pos, i in enumerate(order): rk[i] = pos
        return rk
    rn, rr = _rank(nets), _rank(rets)
    mn, mr = avg(rn), avg(rr)
    num = sum((rn[i] - mn) * (rr[i] - mr) for i in range(len(obs)))
    den = math.sqrt(sum((x - mn) ** 2 for x in rn) * sum((x - mr) ** 2 for x in rr)) or 1
    ic = num / den

    return {
        "available": True, "held_out": True,
        "universe_size": len(universe), "observations": len(obs),
        "window_days": window_days, "horizon_days": horizon_days,
        "decision_dates": f"{dates[0]} .. {dates[-1]}",
        "fwd_return_pct": {
            "net_buy": round(100 * avg(buy_r), 2),
            "net_sell": round(100 * avg(sell_r), 2),
            "neutral": round(100 * avg(neu_r), 2),
        },
        "cohort_n": {"buy": len(buy_r), "sell": len(sell_r), "neutral": len(neu_r)},
        "long_short_spread_pct": round(100 * (avg(buy_r) - avg(sell_r)), 2),
        "information_coefficient": round(ic, 3),
        "hit_rate_pct": {
            "net_buy_positive": round(100 * avg([1 if r > 0 else 0 for r in buy_r]), 1),
            "net_sell_negative": round(100 * avg([1 if r < 0 else 0 for r in sell_r]), 1),
        },
        "verdict_hint": "predictive if spread > 0 and IC > ~0.03 with adequate N",
    }


if __name__ == "__main__":
    import sys
    r = run(top_tickers=int(sys.argv[1]) if len(sys.argv) > 1 else 30)
    print(json.dumps(r, indent=2))
