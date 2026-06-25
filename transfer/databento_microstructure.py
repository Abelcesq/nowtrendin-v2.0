"""
Databento microstructure — HELD-OUT Dark-Matter PROTOTYPE (imported by nothing in scoring).

A DIFFERENT kind of Dark Matter than the filing-based signals (congress / insider Form-4 / 13F):
institutional footprints in the actual TAPE. From Databento `trades` it measures, per ticker:
  • BLOCK activity   — prints ≥ $250K notional (block_notional, block_share of volume, n_blocks).
  • DIRECTION        — a tick test (uptick=buy, downtick=sell, size-weighted) → net imbalance →
                       inflow / outflow (this consolidated feed tags side='N', so we infer it).
  • intensity        — how block-heavy the tape is (0-1).

Informed/large money hides size in blocks; a block-heavy, one-sided tape is an early footprint.
RESEARCH-ONLY: prototype, NOT in any score — research → backtest-before-ship → then (optionally)
integrate flag-gated into positioning_intel. Measurement (a FACT from the tape), not advice.

NOTES / production path:
  - Full-day trades for a liquid name is huge over HTTP JSON, so this samples a WINDOW (default a
    midday hour). Production should use the Databento Python client (DBN binary) for full-day, and a
    publisher_id→venue map for true dark-pool / off-exchange share (omitted here — needs the map).
  - Cost ~ $0.027/ticker/day of trades (≈ $0.001 for a 1-hour window). DATABENTO_API_KEY.
"""
from __future__ import annotations
import os
import json
import time
import base64
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DATABENTO_API_KEY = os.getenv("DATABENTO_API_KEY", "")
_BASE = "https://hist.databento.com/v0"
_DATASET = os.getenv("DATABENTO_DATASET", "DBEQ.BASIC")     # consolidated US equities (has off-exch prints)
BLOCK_USD = float(os.getenv("DBN_BLOCK_USD", "250000"))     # $250K notional = a "block"
_TTL = int(os.getenv("DBN_MICRO_TTL_SEC", "21600"))         # 6h
_CACHE: dict = {}


def available() -> bool:
    return bool(DATABENTO_API_KEY)


def _auth() -> str:
    return "Basic " + base64.b64encode(f"{DATABENTO_API_KEY}:".encode()).decode()


def _recent_window(window_min: int) -> tuple:
    """A midday window on the most recent weekday (UTC 15:00 ≈ 11:00 ET)."""
    d = datetime.now(timezone.utc).date()
    while d.weekday() >= 5:                       # back up off the weekend
        d = d - timedelta(days=1)
    d = d - timedelta(days=1)                      # use the prior completed session
    while d.weekday() >= 5:
        d = d - timedelta(days=1)
    start = datetime(d.year, d.month, d.day, 15, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=window_min)
    return start.strftime("%Y-%m-%dT%H:%M:%S"), end.strftime("%Y-%m-%dT%H:%M:%S")


def _fetch_trades(ticker: str, start_iso: str, end_iso: str) -> list:
    params = {"dataset": _DATASET, "symbols": ticker.upper(), "schema": "trades",
              "start": start_iso, "end": end_iso, "stype_in": "raw_symbol", "encoding": "json"}
    req = Request(f"{_BASE}/timeseries.get_range?{urlencode(params)}",
                  headers={"Authorization": _auth(), "User-Agent": "NowTrendIn/2.0"})
    out = []
    with urlopen(req, timeout=40) as r:
        for line in r.read().decode("utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                t = json.loads(line)
            except Exception:
                continue
            try:
                price = int(t.get("price")) / 1e9
                size = int(t.get("size") or 0)
            except (TypeError, ValueError):
                continue
            if price > 0 and size > 0:
                out.append((t.get("sequence") or 0, price, size))
    return out


def microstructure_signal(ticker: str, window_min: int = 60) -> dict:
    """Block + direction read from the tape over a sampled window. HELD-OUT."""
    if not DATABENTO_API_KEY:
        return {"available": False, "reason": "no databento key"}
    tkr = ticker.upper().strip()
    ck = f"{tkr}:{window_min}"
    ent = _CACHE.get(ck)
    if ent and time.time() - ent["ts"] < _TTL:
        return ent["data"]
    start_iso, end_iso = _recent_window(window_min)
    try:
        trades = _fetch_trades(tkr, start_iso, end_iso)
    except Exception as e:
        print(f"[dbn-micro] {tkr}: {e}")
        return {"available": False, "error": str(e)}
    if not trades:
        out = {"available": False, "reason": "no trades in window", "window": [start_iso, end_iso]}
        _CACHE[ck] = {"data": out, "ts": time.time()}
        return out

    trades.sort(key=lambda x: x[0])                          # by sequence (tape order)
    total_vol = total_notional = 0.0
    block_vol = block_notional = 0.0
    n_blocks = 0
    buy_notional = sell_notional = 0.0
    prev_price = None
    last_dir = 0
    for _seq, price, size in trades:
        notional = price * size
        total_vol += size
        total_notional += notional
        if notional >= BLOCK_USD:
            n_blocks += 1
            block_vol += size
            block_notional += notional
        # Tick test: uptick→buy, downtick→sell, zero-tick→carry the last direction.
        if prev_price is not None:
            if price > prev_price:
                last_dir = 1
            elif price < prev_price:
                last_dir = -1
        if last_dir > 0:
            buy_notional += notional
        elif last_dir < 0:
            sell_notional += notional
        prev_price = price

    block_share = (block_vol / total_vol) if total_vol else 0.0
    classified = buy_notional + sell_notional
    imbalance = ((buy_notional - sell_notional) / classified) if classified else 0.0   # -1..+1
    flow = ("inflow" if imbalance > 0.15 else "outflow" if imbalance < -0.15 else "neutral")
    intensity = round(min(1.0, block_share / 0.30), 3)        # 30% block share = saturated (provisional)

    out = {
        "available": True, "held_out": True, "ticker": tkr,
        "window": [start_iso, end_iso], "window_min": window_min,
        "trades": len(trades), "total_volume": int(total_vol),
        "total_notional_usd": round(total_notional),
        "n_blocks": n_blocks, "block_notional_usd": round(block_notional),
        "block_share": round(block_share, 3),
        "tick_imbalance": round(imbalance, 3),
        "intensity": intensity, "flow": flow, "block_usd_floor": BLOCK_USD,
        "note": "HELD-OUT microstructure prototype (block + tick-test direction from the tape). NOT "
                "in any score. Direction inferred via tick test (feed tags side='N'); dark-pool share "
                "omitted (needs a publisher→venue map). Measurement, not advice.",
    }
    _CACHE[ck] = {"data": out, "ts": time.time()}
    return out


if __name__ == "__main__":
    import sys
    for sym in (sys.argv[1:] or ["AAPL"]):
        s = microstructure_signal(sym)
        if s.get("available"):
            print(f"{sym}: trades={s['trades']} vol={s['total_volume']:,} | blocks={s['n_blocks']} "
                  f"(${s['block_notional_usd']:,.0f}, share={s['block_share']}) | imbalance={s['tick_imbalance']} "
                  f"flow={s['flow']} intensity={s['intensity']}  [{s['window'][0]}..{s['window'][1].split('T')[1]}]")
        else:
            print(f"{sym}: {s}")
