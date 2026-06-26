"""
Alpha Vantage Dark-Positioning — HELD-OUT research module (imported by NOTHING in scoring).

Per-ticker DARK MATTER money-movement from Alpha Vantage, the data Databento canNOT provide:
  • INSIDER_TRANSACTIONS    — corporate insider Form-4 trades (officers / directors / 10% owners).
  • INSTITUTIONAL_HOLDINGS  — 13F institutional holders + the CHANGE (increased/decreased) by ticker.

Filters to MATERIAL moves (≥ $250K) and computes NET DIRECTION (inflow/outflow), surfacing where
informed/institutional money is moving. RESEARCH-ONLY: build held-out, research the output,
BACKTEST-BEFORE-SHIP, THEN integrate into positioning_intel as additional Dark-Matter inputs
(alongside congress + curated 13F). Non-circular (external filings); a FACT, never advice.

Reads ALPHAVANTAGE_RESEARCH_KEY (dedicated research key) first so production NEWS_SENTIMENT
(ALPHAVANTAGE_API_KEY) is untouched. Free tier = 25 req/day · 5/min — research a handful of tickers
(2 calls each) and cache 24h (insider/13F change slowly).
"""
from __future__ import annotations
import os
import json
import time
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime, timezone, timedelta

AV_KEY = os.getenv("ALPHAVANTAGE_RESEARCH_KEY") or os.getenv("ALPHAVANTAGE_API_KEY", "")
_BASE = "https://www.alphavantage.co/query"
MIN_USD = float(os.getenv("AV_DARKPOS_MIN_USD", "250000"))          # $250K materiality floor
INSIDER_WINDOW_DAYS = int(os.getenv("AV_INSIDER_WINDOW_DAYS", "90"))
_TTL = float(os.getenv("AV_DARKPOS_TTL_SEC", "86400"))             # 24h cache
_CACHE: dict = {}


def available() -> bool:
    return bool(AV_KEY)


def source_available() -> bool:
    """True if ANY Dark-Matter insider source is usable: Alpha Vantage (AV_KEY) OR Finviz Elite
    (FINVIZ_INSIDER=1 + FINVIZ_API_KEY). Lets the insider signal run on Finviz alone — AV no longer
    required now that Finviz is the uncapped primary. (Institutional 13F still needs AV.)"""
    if AV_KEY:
        return True
    if os.getenv("FINVIZ_INSIDER", "0") == "1":
        try:
            import finviz_data
            return finviz_data.available()
        except Exception:
            return False
    return False


_last_call = [0.0]
# Free tier = 5 req/min → ≥12s/call. Default safe; lower it (e.g. 1) on a premium key.
_MIN_INTERVAL = float(os.getenv("AV_MIN_INTERVAL_SEC", "13"))


def _get(params: dict):
    if not AV_KEY:
        return None
    # Self-throttle: AV free tier rejects bursts (≤1 req/sec) with a Note instead of data.
    _wait = _MIN_INTERVAL - (time.time() - _last_call[0])
    if _wait > 0:
        time.sleep(_wait)
    _last_call[0] = time.time()
    try:
        url = f"{_BASE}?{urlencode({**params, 'apikey': AV_KEY})}"
        with urlopen(url, timeout=20) as r:
            d = json.loads(r.read().decode("utf-8"))
        # AV signals a throttle/limit via a Note/Information field, not an HTTP error.
        if isinstance(d, dict) and (d.get("Note") or d.get("Information")):
            print(f"[av-darkpos] limit/note: {(d.get('Note') or d.get('Information'))[:160]}")
            return None
        return d
    except Exception as e:
        print(f"[av-darkpos] {params.get('function')}: {e}")
        return None


def _num(x):
    try:
        return float(str(x).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return None


def insider_signal(ticker: str) -> dict:
    """Net insider (Form-4) money movement over the recent window — MATERIAL trades only (≥$250K),
    priced common-stock transactions (RSU/option comp grants with no market price are excluded).
    Direction: A (acquisition/buy) → inflow, D (disposal/sell) → outflow."""
    d = _get({"function": "INSIDER_TRANSACTIONS", "symbol": ticker.upper()})
    rows = (d or {}).get("data") or []
    cutoff = (datetime.now(timezone.utc) - timedelta(days=INSIDER_WINDOW_DAYS)).strftime("%Y-%m-%d")
    buy_usd = sell_usd = 0.0
    buy_n = sell_n = 0
    for r in rows:
        dt = (r.get("transaction_date") or "")[:10]
        if not dt or dt < cutoff:
            continue
        sh, px = _num(r.get("shares")), _num(r.get("share_price"))
        if not sh or not px:
            continue                                   # comp grant / no market price → skip
        val = sh * px
        if val < MIN_USD:
            continue
        ad = (r.get("acquisition_or_disposal") or "").upper()
        if ad == "A":
            buy_usd += val; buy_n += 1
        elif ad == "D":
            sell_usd += val; sell_n += 1
    net = buy_usd - sell_usd
    flow = "inflow" if net > MIN_USD else "outflow" if net < -MIN_USD else "neutral"
    # Insider BUYING is the rare high-conviction signal; routine net selling is low-information →
    # neutral, not bearish (matches finviz_data.insider_signal). flow/net_usd kept as factual context.
    signal = "accumulation" if buy_usd >= MIN_USD else "neutral"
    return {"available": bool(rows), "source": "alphavantage", "window_days": INSIDER_WINDOW_DAYS,
            "buy_usd": round(buy_usd), "sell_usd": round(sell_usd), "net_usd": round(net),
            "buys": buy_n, "sells": sell_n, "flow": flow, "signal": signal}


def institutional_signal(ticker: str) -> dict:
    """Net 13F institutional flow (breadth + share-change direction) for the ticker. Institutional
    moves are inherently ≥$250K, so the materiality floor is effectively always met here."""
    d = _get({"function": "INSTITUTIONAL_HOLDINGS", "symbol": ticker.upper()})
    # The SUMMARY fields are always present; the per-holder `data` array is sometimes omitted,
    # so key off the summary (that's all we need for net flow), not on `data`.
    if not isinstance(d, dict) or d.get("total_institutional_holders") is None:
        return {"available": False}
    inc = _num(d.get("holders_with_increased_holdings")) or 0
    dec = _num(d.get("holders_with_decreased_holdings")) or 0
    sh_inc = _num(d.get("shares_with_increased_holdings")) or 0
    sh_dec = _num(d.get("shares_with_decreased_holdings")) or 0
    net_shares = sh_inc - sh_dec
    flow = "inflow" if net_shares > 0 else "outflow" if net_shares < 0 else "neutral"
    as_of = ""
    for h in (d.get("data") or [])[:80]:
        lr = h.get("last_reported") or ""
        if lr > as_of:
            as_of = lr
    return {"available": True, "as_of": as_of,
            "total_holders": _num(d.get("total_institutional_holders")),
            "holders_increased": int(inc), "holders_decreased": int(dec),
            "shares_increased": sh_inc, "shares_decreased": sh_dec,
            "net_shares": net_shares, "flow": flow}


def _best_insider(ticker: str, name: str = "") -> dict:
    """Insider Form-4 from the PRIMARY source, AV as fallback. Finviz Elite (uncapped, market-wide
    Form-4) is primary when FINVIZ_INSIDER=1 and configured; otherwise Alpha Vantage (25/day). Both
    return the same shape, so this is a transparent swap. Flag default OFF → byte-identical to AV."""
    if os.getenv("FINVIZ_INSIDER", "0") == "1":
        try:
            import finviz_data
            if finviz_data.available():
                s = finviz_data.insider_signal(ticker, name)
                if s.get("available"):
                    return s
        except Exception as e:
            print(f"[av-darkpos] finviz insider unavailable, falling back to AV: {e}")
    return insider_signal(ticker)


def signal_for(ticker: str, name: str = "") -> dict:
    """Combined per-ticker Dark-Matter read = insider (Form-4) + institutional (13F). HELD-OUT.
    Insider leg uses the best available source (Finviz primary when FINVIZ_INSIDER=1, else AV)."""
    tkr = ticker.upper().strip()
    ent = _CACHE.get(tkr)
    if ent and (time.time() - ent["ts"] < _TTL):
        return ent["data"]
    ins = _best_insider(tkr, name)
    inst = institutional_signal(tkr)
    flows = [s.get("flow") for s in (ins, inst) if s.get("available") and s.get("flow") in ("inflow", "outflow")]
    if flows and all(f == "inflow" for f in flows):
        combined = "inflow"
    elif flows and all(f == "outflow" for f in flows):
        combined = "outflow"
    elif "inflow" in flows and "outflow" in flows:
        combined = "mixed"
    else:
        combined = "neutral"
    out = {"ticker": tkr, "name": name or tkr, "insider": ins, "institutional": inst,
           "combined_flow": combined, "min_usd": MIN_USD,
           "insider_source": ins.get("source", "alphavantage"),
           "note": f"HELD-OUT Dark-Matter research ({ins.get('source','alphavantage')} insider Form-4 + "
                   "AV 13F institutional, ≥$250K). A FACT from filings — not advice. NOT in any score yet "
                   "(backtest-before-ship)."}
    _CACHE[tkr] = {"data": out, "ts": time.time()}
    return out


def research(tickers: list, pace_sec: float = 13.0) -> dict:
    """Run signal_for over a few tickers, paced for the free tier (5/min; 2 calls/ticker)."""
    sigs = []
    for i, t in enumerate(tickers):
        sigs.append(signal_for(t))
        if i < len(tickers) - 1:
            time.sleep(pace_sec)
    return {"available": bool(AV_KEY), "held_out": True, "count": len(sigs), "signals": sigs,
            "note": "Held-out research — NOT integrated into any score. Backtest-before-ship."}


if __name__ == "__main__":
    import sys
    tks = sys.argv[1:] or ["AAPL", "NVDA"]
    r = research(tks)
    for s in r["signals"]:
        ins, inst = s["insider"], s["institutional"]
        print(f"{s['ticker']:6} combined={s['combined_flow']:7} | "
              f"insider net=${ins.get('net_usd', 0):>14,.0f} ({ins.get('buys')}b/{ins.get('sells')}s {ins.get('flow')}) "
              f"| inst {inst.get('holders_increased')}+/{inst.get('holders_decreased')}- {inst.get('flow')} as_of {inst.get('as_of')}")
