"""
referee_gdelt.py — GDELT referee provider (Phase 2, the SECOND independent source).

WHY GDELT (alongside Wikipedia Pageviews):
  Wikipedia can't referee what it doesn't cover — 38% of our niche-early-tech ledger
  (fastembed, hyperliquid, "context compression") has no confident article. GDELT's
  Global Knowledge Graph indexes worldwide NEWS coverage, so it catches breaking/niche
  topics Wikipedia lacks — and it is INDEPENDENT of both Wikipedia AND of search-trend
  signals. The founder froze the arrival rule as EARLIEST of (Wikipedia surge OR GDELT
  surge): if EITHER independent source shows a topic already surged, we don't get to
  claim we were early. This is the strictest, least-self-flattering definition.

INTEGRITY: held-out, read-only to the score (imported by nothing in the scoring path).
Arrival is dated from GDELT's FULL history (back to 2017), so a pre-launch arrival is
seen as pre-launch — never mis-scored as a miss. Never guesses: an unparseable/empty
timeline → no_data, never a fabricated date.

SOURCE: GDELT DOC 2.0 API (free, no key) — mode=timelinevol returns the daily share of
worldwide coverage mentioning the query (a normalized 0-100 "volume intensity").
"""
from __future__ import annotations

import json
import statistics
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Optional

try:
    from date_utils import to_iso_date
except Exception:
    def to_iso_date(s):
        return (str(s)[:10] if s else None)

_UA = "NowTrendIn-Referee/1.0 (https://abelcesq.github.io/nowtrendin-v2.0/; abelc.esq@gmail.com)"
_DOC = "https://api.gdeltproject.org/api/v2/doc/doc"

# Frozen surge params — version-stamped, mirror the Wikipedia referee's DEFINITION of
# "arrival" (first sustained breach over a lowest-40% quiet baseline) but on a percentage
# series, so the absolute floor is a coverage-share floor, not a pageview count.
GDELT_PARAM_VERSION = "gdelt-v1-2026-06-23"
SURGE_MULT = 3.0
SURGE_MIN_ABS = 0.05          # >= 0.05% of global coverage (kills percentage noise)


def _get(url: str, timeout: int = 25) -> Optional[bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception:
        return None


def fetch_volume(query: str, start_date, end_date) -> Optional[list[dict]]:
    """Daily 'volume intensity' (share of worldwide coverage, 0-100) for `query` over
    [start_date, end_date]. Phrase-quoted for multi-word so GDELT matches the phrase, not
    the loose OR of tokens. Returns [{date: YYYY-MM-DD, views: float}] or None."""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date[:10], "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date[:10], "%Y-%m-%d").date()
    q = query.strip()
    if " " in q and not (q.startswith('"') and q.endswith('"')):
        q = f'"{q}"'
    params = urllib.parse.urlencode({
        "query": q, "mode": "timelinevol", "format": "json",
        "startdatetime": start_date.strftime("%Y%m%d") + "000000",
        "enddatetime": end_date.strftime("%Y%m%d") + "000000",
    })
    raw = _get(f"{_DOC}?{params}")
    if not raw:
        return None
    try:
        tl = json.loads(raw.decode("utf-8")).get("timeline", [])
        series = tl[0].get("data", []) if tl else []
    except Exception:
        return None
    curve = []
    for pt in series:
        d = to_iso_date(str(pt.get("date", ""))[:8].replace("T", "")) if pt.get("date") else None
        if not d and pt.get("date"):
            ds = str(pt["date"])               # 'YYYYMMDDT...' or ISO
            d = f"{ds[0:4]}-{ds[4:6]}-{ds[6:8]}" if len(ds) >= 8 else None
        if d:
            curve.append({"date": d, "views": float(pt.get("value", 0) or 0)})
    return curve or None


def detect_arrival_date(curve: list[dict], since: object = None) -> Optional[dict]:
    """First SUSTAINED surge in GDELT coverage over a lowest-40% quiet baseline — the SAME
    definition of 'arrival' the Wikipedia referee uses, on the coverage-share series.
    `since` floors the search (same-surge matching). Returns {arrival_date, ...} or None."""
    if not curve or len(curve) < 5:
        return None
    curve = sorted(curve, key=lambda p: p["date"])
    vals = [p["views"] for p in curve]
    quiet = sorted(vals)[:max(2, int(len(vals) * 0.4))]
    base = max(1e-6, statistics.mean(quiet) if quiet else 1e-6)
    threshold = max(base * SURGE_MULT, SURGE_MIN_ABS)
    since_iso = to_iso_date(since) if since is not None else None
    for i in range(len(curve) - 2):
        if since_iso and curve[i]["date"] < since_iso:
            continue
        if vals[i] >= threshold and vals[i+1] >= threshold * 0.8 and vals[i+2] >= threshold * 0.7:
            return {"arrival_date": to_iso_date(curve[i]["date"]), "surge_value": round(vals[i], 3),
                    "baseline": round(base, 4), "multiple": round(vals[i] / base, 1) if base else None,
                    "param_version": GDELT_PARAM_VERSION}
    return None


def true_arrival(query: str, history_start="2024-01-01") -> dict:
    """The topic's FIRST clean arrival in GDELT's full history (so a pre-launch arrival is
    dated as pre-launch). Returns {status, arrival_date}. status ∈ {ok, no_data, no_surge}.
    Never raises."""
    end = datetime.now(timezone.utc).date()
    curve = fetch_volume(query, history_start, end)
    if not curve:
        return {"status": "no_data", "arrival_date": None}
    arr = detect_arrival_date(curve)
    if not arr:
        return {"status": "no_surge", "arrival_date": None}
    return {"status": "ok", "arrival_date": arr["arrival_date"], "detail": arr}


if __name__ == "__main__":
    import sys
    for t in (sys.argv[1:] or ["fastembed", "DeepSeek", "Strait of Hormuz", "hyperliquid"]):
        print(t, "->", json.dumps(true_arrival(t)))
