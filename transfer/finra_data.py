"""
FINRA leverage / distress indicator — Consolidated Short Interest.

FINRA (Financial Industry Regulatory Authority) publishes bi-monthly short
interest by security. High / rising short interest and a high days-to-cover are
classic signals of distress or a crowded short — useful for flagging
potentially over-leveraged or stressed names and industries.

Auth: single bearer API key (no OAuth). Free tier — MONITOR USAGE/COST after
30 days (FINRA pricing TBD). Data updates ~twice a month; cached 24h.

NOTE: "FINRA" is a registered trademark of the Financial Industry Regulatory
Authority, Inc. Used here only to attribute the public data source.
"""
import os
import csv
import io
import json
from datetime import datetime, timezone, timedelta

try:
    from collector_health import log_api_call as _api
except Exception:
    def _api(*a, **k): pass

_KEY = os.getenv("FINRA_API_KEY", "")
_URL = "https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest"
_CACHE: dict = {}
_TTL = int(os.getenv("FINRA_TTL_SEC", "86400"))  # 24h


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def short_interest(ticker: str) -> dict:
    """Latest consolidated short interest for a ticker (cached 24h)."""
    if not _KEY or not ticker:
        return None
    import time as _t
    tkr = ticker.upper()
    c = _CACHE.get(tkr)
    if c and (_t.time() - c["ts"] < _TTL):
        return c["data"]
    try:
        from urllib.request import Request, urlopen
        start = (datetime.now(timezone.utc) - timedelta(days=180)).strftime("%Y-%m-%d")
        end = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        body = json.dumps({
            "limit": 30,
            "compareFilters": [{"compareType": "EQUAL", "fieldName": "symbolCode", "fieldValue": tkr}],
            "dateRangeFilters": [{"fieldName": "settlementDate", "startDate": start, "endDate": end}],
        }).encode("utf-8")
        req = Request(_URL, data=body, headers={
            "Authorization": f"Bearer {_KEY}", "Content-Type": "application/json"})
        _api("finra")
        with urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8")
        rows = list(csv.DictReader(io.StringIO(text)))
        if not rows:
            data = {"available": False, "ticker": tkr,
                    "note": "No recent FINRA short-interest record."}
        else:
            rows.sort(key=lambda x: x.get("settlementDate", ""), reverse=True)
            r0 = rows[0]
            cur = _num(r0.get("currentShortPositionQuantity"))
            prev = _num(r0.get("previousShortPositionQuantity"))
            dtc = _num(r0.get("daysToCoverQuantity"))
            chg = _num(r0.get("changePercent"))
            # Distress/leverage read: high days-to-cover + rising short interest.
            if dtc is not None and dtc >= 5 and (chg or 0) > 0:
                label = "Elevated short interest (rising, crowded)"
            elif dtc is not None and dtc >= 5:
                label = "Elevated short interest"
            elif chg is not None and chg >= 25:
                label = "Short interest rising sharply"
            else:
                label = "Short interest normal"
            data = {
                "available": True, "ticker": tkr,
                "short_position": cur, "previous_position": prev,
                "change_pct": chg, "days_to_cover": dtc,
                "avg_daily_volume": _num(r0.get("averageDailyVolumeQuantity")),
                "settlement_date": r0.get("settlementDate"),
                "label": label, "source": "FINRA Consolidated Short Interest",
                "note": ("Short interest from FINRA (a registered trademark of the "
                         "Financial Industry Regulatory Authority). Descriptive "
                         "leverage/distress indicator — not investment advice."),
            }
    except Exception as e:
        print(f"[finra] {tkr} error: {e}")
        return c["data"] if c else None
    _CACHE[tkr] = {"data": data, "ts": _t.time()}
    return data


def short_interest_series(ticker: str) -> list:
    """Full ~180-day bi-monthly short-interest series for a ticker (for baseline
    backfill). Returns [{settlement_date, change_pct, days_to_cover,
    short_position}, ...] oldest-first. Best-effort; empty list on failure."""
    import io, csv
    from urllib.request import Request, urlopen
    from datetime import datetime as _dt, timedelta as _td
    key = os.getenv("FINRA_API_KEY", "")
    if not key or not ticker:
        return []
    tkr = ticker.upper()
    end = _dt.utcnow().strftime("%Y-%m-%d")
    start = (_dt.utcnow() - _td(days=180)).strftime("%Y-%m-%d")
    body = {
        "compareFilters": [{"compareType": "EQUAL", "fieldName": "symbolCode", "fieldValue": tkr}],
        "dateRangeFilters": [{"fieldName": "settlementDate", "startDate": start, "endDate": end}],
        "limit": 50,
    }
    try:
        import json as _json
        req = Request("https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest",
                      data=_json.dumps(body).encode("utf-8"),
                      headers={"Authorization": f"Bearer {key}",
                               "Content-Type": "application/json", "Accept": "text/plain"})
        with urlopen(req, timeout=15) as r:
            rows = list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))
        rows.sort(key=lambda x: x.get("settlementDate", ""))  # oldest-first
        out = []
        for r0 in rows:
            sd = r0.get("settlementDate")
            if not sd:
                continue
            out.append({
                "settlement_date": sd,
                "change_pct": _num(r0.get("changePercent")),
                "days_to_cover": _num(r0.get("daysToCoverQuantity")),
                "short_position": _num(r0.get("currentShortPositionQuantity")),
            })
        return out
    except Exception as e:
        print(f"[finra] {tkr} series error: {e}")
        return []
