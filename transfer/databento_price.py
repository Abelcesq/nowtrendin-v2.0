"""
Databento price connector — consolidated EOD close for the MARKET-SIGNAL accuracy ledger.

Same interface as fmp_data.historical_close (`{YYYY-MM-DD: close}`) so the market ledger can
use either source or CROSS-CHECK both. Uses Databento's historical HTTP API, dataset
`EQUS.SUMMARY` schema `ohlcv-1d` = ONE consolidated bar per US-equity trading day (DBEQ.BASIC
emits per-venue bars; EQUS.SUMMARY is the clean consolidated daily). Exchange-direct, so the
authoritative "how the market ended" read for verification.

REFEREE / GROUND-TRUTH ONLY — never feeds a score (same role as FMP). Metered but negligible
(~$0.0003/ticker/window) with NO daily request cap. Degrades to None when DATABENTO_API_KEY is
absent or the symbol has no data.

Format adapter: Databento `ts_event` is a nanosecond UTC epoch → ISO date; prices are 1e-9
fixed-point integers → float. HTTP Basic auth, the API key as username (empty password).
"""
from __future__ import annotations
import os
import json
import time
import base64
from datetime import datetime, timezone, timedelta
from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DATABENTO_API_KEY = os.getenv("DATABENTO_API_KEY", "")
_BASE = "https://hist.databento.com/v0"
_DATASET = os.getenv("DATABENTO_DATASET", "EQUS.SUMMARY")
_TTL = int(os.getenv("DATABENTO_TTL_SEC", "21600"))   # 6h
_CACHE: dict = {}


def available() -> bool:
    return bool(DATABENTO_API_KEY)


def _auth_header() -> str:
    # Databento historical API: HTTP Basic, API key as username, empty password.
    token = base64.b64encode(f"{DATABENTO_API_KEY}:".encode()).decode()
    return f"Basic {token}"


def _to_iso_date(ts_event) -> Optional[str]:
    """Databento ts_event = nanoseconds since the UTC epoch → 'YYYY-MM-DD'."""
    try:
        secs = int(ts_event) / 1e9
        return datetime.fromtimestamp(secs, tz=timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return None


def _to_price(val) -> Optional[float]:
    """Databento prices are 1e-9 fixed-point integers."""
    try:
        if val in (None, ""):
            return None
        return round(int(val) / 1e9, 4)
    except (TypeError, ValueError):
        return None


def historical_close(ticker: str, frm: str = "", to: str = "") -> Optional[dict]:
    """Daily EOD close `{YYYY-MM-DD: close}` from Databento EQUS.SUMMARY ohlcv-1d — the SAME
    shape as fmp_data.historical_close. Cached 6h. Returns None when the key is absent or the
    symbol has no data (so the ledger can fall back to FMP)."""
    if not DATABENTO_API_KEY or not ticker:
        return None
    tkr = ticker.upper().strip()
    # Default to a ~150-day window when no range is given (the ledger always passes both).
    if not to:
        to = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not frm:
        frm = (datetime.now(timezone.utc) - timedelta(days=150)).strftime("%Y-%m-%d")
    cache_key = f"{tkr}:{frm}:{to}"
    ent = _CACHE.get(cache_key)
    if ent and (time.time() - ent["ts"] < _TTL):
        return ent["data"]

    params = {
        "dataset": _DATASET, "symbols": tkr, "schema": "ohlcv-1d",
        "start": frm, "end": to, "stype_in": "raw_symbol", "encoding": "json",
    }
    out: dict = {}
    try:
        req = Request(f"{_BASE}/timeseries.get_range?{urlencode(params)}",
                      headers={"Authorization": _auth_header(),
                               "User-Agent": "NowTrendIn/2.0"})
        with urlopen(req, timeout=20) as r:
            body = r.read().decode("utf-8")
        # JSON-lines: one OHLCV record per line.
        for line in body.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            ts = rec.get("ts_event") or (rec.get("hd") or {}).get("ts_event")
            d = _to_iso_date(ts)
            close = _to_price(rec.get("close"))
            if d and close is not None:
                out[d] = close   # one consolidated bar/day for EQUS.SUMMARY
    except Exception as e:
        print(f"[databento] {tkr}: {e}")
        # Cache the failure briefly too, so a flaky call doesn't hammer the API every sweep row.
        _CACHE[cache_key] = {"data": None, "ts": time.time()}
        return None
    res = out or None
    _CACHE[cache_key] = {"data": res, "ts": time.time()}
    return res


if __name__ == "__main__":
    import sys
    sym = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    closes = historical_close(sym, frm="2026-06-08", to="2026-06-24")
    print(f"{sym}: {len(closes) if closes else 0} daily closes")
    for d in sorted((closes or {}).keys())[-6:]:
        print("  ", d, "->", closes[d])
