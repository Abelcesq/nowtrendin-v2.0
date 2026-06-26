"""
finviz_insider_backtest.py — HELD-OUT backtest harness for the Finviz insider Dark-Matter source.

Validates Finviz as a drop-in PRIMARY insider source before flipping FINVIZ_INSIDER=1 (§16
backtest-before-ship). This is a SOURCE-SWAP for an already-vetted signal, so it checks:
  1. Data soundness  — Finviz insider produces a sane, non-degenerate flow distribution at scale.
  2. Source equivalence — Finviz agrees DIRECTIONALLY with Alpha Vantage where AV data exists.
  3. Directional sanity — net insider SELLING tends to sit with weaker trailing performance
     (a sanity check, not a causal claim; insider buys are the stronger known predictor).

Run:  FINVIZ_API_KEY=... python finviz_insider_backtest.py
      (add ALPHAVANTAGE_RESEARCH_KEY=... to include the AV cross-check; AV is 25/day-capped.)
"""
from __future__ import annotations
import os

import finviz_data as fv

BASKET = ["MSTR", "COIN", "NVDA", "AAPL", "TSLA", "META", "AMZN", "MSFT",
          "GOOGL", "AMD", "PLTR", "CRWD", "JPM", "XOM", "WMT"]


def _perf_map(tickers: list) -> dict:
    """One screener call (Performance view v=141) → {ticker: {change, perf_month, perf_year}}."""
    rows = fv.screener(view="141", tickers=",".join(tickers))
    out = {}
    for r in rows:
        out[r.get("Ticker", "").upper()] = {
            "change": r.get("Change"), "perf_month": r.get("Perf Month"),
            "perf_year": r.get("Perf Year"), "price": r.get("Price"),
        }
    return out


def run() -> dict:
    if not fv.available():
        return {"error": "FINVIZ_API_KEY not set"}
    perf = _perf_map(BASKET)
    rows = []
    dist = {"inflow": 0, "outflow": 0, "neutral": 0, "no_data": 0}       # raw net flow (degenerate — context only)
    sig_dist = {"accumulation": 0, "neutral": 0, "no_data": 0}            # interpreted signal (the real read)
    for t in BASKET:
        s = fv.insider_signal(t)
        flow = s["flow"] if s.get("available") else "no_data"
        sig = s.get("signal", "no_data") if s.get("available") else "no_data"
        dist[flow] = dist.get(flow, 0) + 1
        sig_dist[sig] = sig_dist.get(sig, 0) + 1
        p = perf.get(t, {})
        rows.append({"ticker": t, "flow": flow, "signal": sig, "net_usd": s.get("net_usd"),
                     "buy_usd": s.get("buy_usd"), "buys": s.get("buys"), "sells": s.get("sells"),
                     "perf_month": p.get("perf_month"), "perf_year": p.get("perf_year")})

    # Directional sanity: of names with a clear insider direction AND a parseable monthly perf,
    # how often does OUTFLOW sit with a down month / INFLOW with an up month?
    aligned = comparable = 0
    for r in rows:
        pm = fv._num(r.get("perf_month"))
        if r["flow"] in ("inflow", "outflow") and pm is not None:
            comparable += 1
            if (r["flow"] == "outflow" and pm < 0) or (r["flow"] == "inflow" and pm > 0):
                aligned += 1

    # AV cross-check (optional; AV-capped). Compare direction on as many as the budget allows.
    av_cmp = []
    if os.getenv("ALPHAVANTAGE_RESEARCH_KEY") or os.getenv("ALPHAVANTAGE_API_KEY"):
        try:
            import av_dark_positioning as avdp
            for t in ["MSTR", "COIN", "NVDA"]:
                a = avdp.insider_signal(t)
                f = next((x for x in rows if x["ticker"] == t), {})
                av_cmp.append({"ticker": t, "finviz": f.get("flow"),
                               "av": a.get("flow") if a.get("available") else "no_data",
                               "agree": a.get("available") and a.get("flow") == f.get("flow")})
        except Exception as e:
            av_cmp = [{"error": str(e)}]

    return {"basket": len(BASKET), "net_flow_distribution": dist, "signal_distribution": sig_dist,
            "rows": rows,
            "directional_sanity": {"aligned": aligned, "comparable": comparable,
                                   "rate": round(aligned / comparable, 2) if comparable else None},
            "av_cross_check": av_cmp}


if __name__ == "__main__":
    import json
    r = run()
    if r.get("error"):
        print("ERROR:", r["error"]); raise SystemExit(1)
    print(f"BASKET={r['basket']}")
    print(f"  raw net-flow dist (degenerate, context): {r['net_flow_distribution']}")
    print(f"  INTERPRETED signal dist (the real read):  {r['signal_distribution']}")
    print(f"\n{'TICKER':7}{'SIGNAL':13}{'NET_USD':>16}{'BUY_USD':>14}  {'b/s':7}")
    for x in r["rows"]:
        net, buy = x["net_usd"], x.get("buy_usd")
        print(f"{x['ticker']:7}{x['signal']:13}{(('$%0.0f'%net) if net is not None else '-'):>16}"
              f"{(('$%0.0f'%buy) if buy is not None else '-'):>14}  {str(x['buys'])+'/'+str(x['sells']):7}")
    ds = r["directional_sanity"]
    print(f"\nDirectional sanity (outflow~down / inflow~up): {ds['aligned']}/{ds['comparable']} = {ds['rate']}")
    if r["av_cross_check"]:
        print("AV cross-check:", json.dumps(r["av_cross_check"]))
