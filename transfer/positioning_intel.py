"""
Dark-positioning intelligence — per-TICKER smart-money + political positioning.

Inverts the two held-out positioning sources into ONE per-ticker signal:
  • SEC 13F (curated mega-cap funds, sec_13f_research) — how many funds HOLD the name +
    how concentrated (matched to a ticker by issuer NAME, since 13F is keyed by issuer/CUSIP).
  • Congress trades (QuiverQuant, quiver_research) — how many members traded the TICKER
    recently + net buy/sell DIRECTION (keyed by ticker directly).

OUTPUT (a 0-1 `positioning_signal` + a net `direction`) is what OPTIONALLY augments Market
Signal `positioning_concentration` — but ONLY behind the DARK_POSITIONING_V2 flag (default off),
after the backtest validates it. Non-circular: both inputs are EXTERNAL (fund/Congress filings),
independent of any Now TrendIn score. Cached + refreshed (filings are quarterly/periodic).
"""
from __future__ import annotations
import os
import re
import time as _time
from collections import defaultdict

_CACHE = {"maps": None, "built_at": 0.0}
_TTL = float(os.getenv("DARK_POS_TTL_SEC", "86400"))   # rebuild daily


def _norm_name(s: str) -> str:
    """Normalize a company/issuer name for 13F<->ticker matching: lowercase, drop the
    corporate suffixes + punctuation, collapse spaces."""
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\b(inc|incorporated|corp|corporation|co|company|ltd|plc|the|class|com|"
               r"holdings|group|sa|nv|ag|lp|llc|trust|tr)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _build_smart_money():
    """{normalized issuer name -> {funds:set, value:float}} across the curated 13F funds."""
    import sec_13f_research as _sec
    by_name = defaultdict(lambda: {"funds": set(), "value": 0.0})
    for fund, cik in _sec.FUND_CIKS.items():
        try:
            r = _sec.latest_13f(cik, fund)
        except Exception:
            continue
        if not r.get("available"):
            continue
        for h in r.get("top_holdings", []):
            nm = _norm_name(h.get("issuer", ""))
            if not nm:
                continue
            by_name[nm]["funds"].add(fund)
            by_name[nm]["value"] += float(h.get("value_usd") or 0)
    return by_name


def _build_congress():
    """{TICKER -> {members:set, buys:int, sells:int}} from recent congressional trades."""
    import quiver_research as _q
    data = _q._get("/beta/live/congresstrading")
    out = defaultdict(lambda: {"members": set(), "buys": 0, "sells": 0})
    if isinstance(data, list):
        for r in data:
            t = (_q._field(r, "Ticker") or "").upper().strip()
            if not t or not re.match(r"^[A-Z.\-]{1,6}$", t):
                continue
            a = out[t]
            tx = (_q._field(r, "Transaction") or "").lower()
            if "purchase" in tx or "buy" in tx:
                a["buys"] += 1
            elif "sale" in tx or "sell" in tx:
                a["sells"] += 1
            a["members"].add(_q._field(r, "Representative", "Name"))
    return out


def _build():
    sm = _build_smart_money()
    cg = _build_congress()
    _CACHE["maps"] = {"smart_money": sm, "congress": cg}
    _CACHE["built_at"] = _time.time()
    return _CACHE["maps"]


def _maps():
    if _CACHE["maps"] is None or (_time.time() - _CACHE["built_at"]) > _TTL:
        try:
            return _build()
        except Exception as e:
            print(f"[dark-pos] build error: {e}")
            return _CACHE["maps"] or {"smart_money": {}, "congress": {}}
    return _CACHE["maps"]


def signal_for(ticker: str, name: str = "") -> dict:
    """Per-ticker dark-positioning signal. ticker = symbol (for Congress); name = company
    display name (for the 13F issuer-name match). Returns intensity 0-1 + net direction."""
    m = _maps()
    tkr = (ticker or "").upper().strip()
    cg = m["congress"].get(tkr, {"members": set(), "buys": 0, "sells": 0})
    n_members = len(cg["members"])
    net = cg["buys"] - cg["sells"]                       # + = net buying

    # 13F: match the company name against held issuers (substring on normalized names).
    sm_funds, sm_value = set(), 0.0
    qn = _norm_name(name or ticker)
    if qn:
        for nm, v in m["smart_money"].items():
            if qn and (qn == nm or qn in nm or nm in qn):
                sm_funds |= v["funds"]
                sm_value += v["value"]

    import math
    # INTENSITY of money MOVEMENT: breadth of smart-money holders + congressional interest.
    # This is a MEASUREMENT of where money is moving — NOT a prediction or a buy/sell call.
    sm_norm = min(1.0, len(sm_funds) / 6.0)             # 6+ curated funds = saturated
    cg_norm = min(1.0, n_members / 8.0)                 # 8+ members trading = saturated
    positioning_signal = round(min(1.0, 0.6 * sm_norm + 0.4 * cg_norm), 3)
    # DIRECTION of flow (a fact about what the filings show): money moving IN vs OUT.
    flow = ("inflow" if net > 1 else "outflow" if net < -1 else "neutral")
    out = {
        "ticker": tkr, "name": name,
        "movement_intensity": positioning_signal,       # 0-1: how much money is moving here
        "positioning_signal": positioning_signal,       # (alias, kept for the flag-gated blend)
        "flow": flow,                                    # inflow | outflow | neutral (factual)
        "dark_matter_inputs": "congress + curated_13F",
        "smart_money": {"funds_holding": len(sm_funds), "funds": sorted(sm_funds),
                        "total_value_usd": round(sm_value, 0)},
        "congress": {"members": n_members, "buys": cg["buys"], "sells": cg["sells"], "net": net},
    }

    # ── AV Dark-Matter blend — flag-gated, DEFAULT OFF (AV_DARKPOS_ENABLED). Adds Alpha Vantage
    #    insider Form-4 + 13F-by-ticker on top of curated-13F + congress. INERT when off →
    #    byte-identical to the current signal. Weights are PROVISIONAL — tune in the backtest
    #    BEFORE flipping the flag (this is score-affecting). Operational note: AV free tier is
    #    25/day·5/min, so flipping this on requires a prewarm that rotates the watchlist (~12
    #    tickers/day) or a premium AV key; av_dark_positioning caches 24h per ticker.
    if os.getenv("AV_DARKPOS_ENABLED", "0") == "1":
        try:
            import av_dark_positioning as _av

            def _f(x):
                try:
                    return float(x)
                except (TypeError, ValueError):
                    return 0.0

            av = _av.signal_for(tkr, name)
            ins = av.get("insider") or {}
            inst = av.get("institutional") or {}
            insider_norm = min(1.0, abs(_f(ins.get("net_usd"))) / 250_000_000.0)   # $250M net = saturated
            tot = _f(inst.get("total_holders"))
            inst_skew = (abs(_f(inst.get("holders_increased")) - _f(inst.get("holders_decreased"))) / tot) if tot else 0.0
            inst_norm = min(1.0, inst_skew * 4.0)                                  # 25% net-holder skew = saturated
            blended = 0.30 * sm_norm + 0.25 * cg_norm + 0.30 * insider_norm + 0.15 * inst_norm
            out["movement_intensity"] = out["positioning_signal"] = round(min(1.0, blended), 3)
            # Flow CONSENSUS across the directional inputs (congress + insider + institutional).
            votes = [f for f in (flow, ins.get("flow"), inst.get("flow")) if f in ("inflow", "outflow")]
            inflow_n, outflow_n = votes.count("inflow"), votes.count("outflow")
            out["flow"] = ("inflow" if inflow_n > outflow_n else "outflow" if outflow_n > inflow_n
                           else (flow if flow in ("inflow", "outflow") else ("mixed" if votes else "neutral")))
            out["av_insider"] = {"net_usd": ins.get("net_usd"), "flow": ins.get("flow"),
                                 "buys": ins.get("buys"), "sells": ins.get("sells")}
            out["av_institutional"] = {"net_shares": inst.get("net_shares"), "flow": inst.get("flow"),
                                       "holders_increased": inst.get("holders_increased"),
                                       "holders_decreased": inst.get("holders_decreased")}
            out["dark_matter_inputs"] = "congress + curated_13F + av_insider + av_institutional"
        except Exception as _ave:
            print(f"[positioning_intel] AV blend {tkr}: {_ave}")
    return out


def all_signals(watchlist: dict, top_congress: int = 25) -> dict:
    """Signals for every watchlist (name->ticker) item PLUS the most-traded Congress tickers.
    watchlist: {display_name: ticker}. Held-out research output."""
    m = _maps()
    sigs = {}
    for name, tkr in (watchlist or {}).items():
        sigs[tkr] = signal_for(tkr, name)
    # add the busiest congress tickers not already covered
    busy = sorted(m["congress"].items(), key=lambda kv: len(kv[1]["members"]), reverse=True)
    for tkr, _ in busy[:top_congress]:
        if tkr not in sigs:
            sigs[tkr] = signal_for(tkr, tkr)
    ranked = sorted(sigs.values(), key=lambda s: s["movement_intensity"], reverse=True)
    return {"available": True, "held_out": True,
            "built_at": _CACHE["built_at"], "count": len(ranked),
            "signals": ranked,
            "note": "MONEY-MOVEMENT measurement (where institutional + Congressional money is "
                    "moving IN/OUT + how intensely) — a FACT from filings, NOT a prediction or "
                    "buy/sell signal. Feeds Market Signal as a movement input when "
                    "DARK_POSITIONING_V2=1."}


if __name__ == "__main__":
    import json
    try:
        import financial_risk_gradient as _frg
        wl = getattr(_frg, "WATCHLIST_TICKERS", {})
    except Exception:
        wl = {"Apple": "AAPL", "Nvidia": "NVDA", "Microsoft": "MSFT", "Tesla": "TSLA"}
    out = all_signals(wl, top_congress=10)
    print("signals:", out["count"])
    for s in out["signals"][:18]:
        print(f"  {s['ticker']:6} intensity={s['movement_intensity']:.2f} flow={s['flow']:8} "
              f"funds={s['smart_money']['funds_holding']} congress={s['congress']['members']}m "
              f"net{s['congress']['net']:+d}")
