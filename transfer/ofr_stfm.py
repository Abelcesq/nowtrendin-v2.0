"""
OFR Short-Term Funding Monitor (STFM) — leverage & funding-stress overlay.

The U.S. Office of Financial Research publishes the plumbing of the financial
system: repo rates and repo transaction VOLUME. Repo is where leverage in the
system is financed, so:
  - rising repo VOLUME  -> leverage building in the system
  - repo RATE spikes / spreads -> funding stress (the classic early-warning of
    a deleveraging event, e.g. Sept-2019 repo blowup)

Free, public, no token. Data updates <= once/day, so we cache 12h.
Used as a macro RISK / leverage-analysis overlay (not company-specific).
"""
import os
import json
import statistics
from datetime import datetime, timezone

try:
    from collector_health import log_api_call as _api
except Exception:
    def _api(*a, **k): pass

_BASE = "https://data.financialresearch.gov/v1/series/timeseries?mnemonic="

# Verified working series (funding cost + leverage volume).
SERIES = {
    "tri_party_repo_rate": "REPO-TRI_AR_OO-P",   # tri-party avg rate, overnight
    "dvp_repo_rate":       "REPO-DVP_AR_OO-P",   # DVP avg rate, overnight
    "gcf_repo_rate":       "REPO-GCF_AR_OO-P",   # GCF avg rate, overnight
    "dvp_repo_volume":     "REPO-DVP_TV_TOT-P",  # DVP total value transacted ($)
}

_CACHE: dict = {}
_TTL = int(os.getenv("OFR_TTL_SEC", "43200"))  # 12h


def _series(mnemonic: str):
    """Return clean (date, value) pairs, nulls dropped, oldest-first."""
    try:
        from urllib.request import urlopen
        _api("ofr")
        with urlopen(_BASE + mnemonic, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
        return [(d, float(v)) for d, v in data if v is not None]
    except Exception as e:
        print(f"[ofr] {mnemonic} error: {e}")
        return []


def _metric(pairs, lookback=21):
    if not pairs:
        return None
    latest_date, latest = pairs[-1]
    prev = pairs[-min(lookback, len(pairs))][1]
    pct = round((latest - prev) / prev * 100, 1) if prev else None
    return {"latest": round(latest, 4), "as_of": latest_date,
            "prior": round(prev, 4), "change_pct_21obs": pct}


def leverage_snapshot() -> dict:
    """Macro leverage + funding-stress read from OFR repo data. Cached 12h."""
    import time as _t
    c = _CACHE.get("snap")
    if c and (_t.time() - c["ts"] < _TTL):
        return c["data"]

    m = {k: _metric(_series(v)) for k, v in SERIES.items()}

    # Leverage signal — driven by repo transaction VOLUME trend.
    vol = m.get("dvp_repo_volume") or {}
    vol_chg = vol.get("change_pct_21obs")
    if vol_chg is None:
        lev_label, lev_score = "n/a", None
    elif vol_chg >= 8:
        lev_label, lev_score = "Leverage building (repo volume rising)", min(100, 50 + vol_chg)
    elif vol_chg <= -8:
        lev_label, lev_score = "Leverage unwinding (repo volume falling)", max(0, 50 + vol_chg)
    else:
        lev_label, lev_score = "Leverage stable", 50

    # Funding stress — rate dispersion across repo venues + recent rate move.
    rates = [m[k]["latest"] for k in ("tri_party_repo_rate", "dvp_repo_rate", "gcf_repo_rate")
             if m.get(k) and m[k].get("latest") is not None]
    spread_bps = round((max(rates) - min(rates)) * 100, 1) if len(rates) >= 2 else None
    gcf = m.get("gcf_repo_rate") or {}
    rate_move = gcf.get("change_pct_21obs")
    if spread_bps is None:
        stress_label = "n/a"
    elif spread_bps >= 15 or (rate_move is not None and rate_move >= 25):
        stress_label = "Elevated funding stress"
    elif spread_bps >= 6:
        stress_label = "Mild funding stress"
    else:
        stress_label = "Calm funding markets"

    data = {
        "source": "U.S. Office of Financial Research — Short-Term Funding Monitor",
        "as_of": vol.get("as_of") or (m.get("gcf_repo_rate") or {}).get("as_of"),
        "leverage": {"label": lev_label, "score": lev_score,
                     "repo_volume_usd": vol.get("latest"),
                     "repo_volume_change_pct": vol_chg},
        "funding_stress": {"label": stress_label,
                           "repo_rate_spread_bps": spread_bps,
                           "gcf_rate_change_pct": rate_move},
        "series": m,
        "note": ("Macro systemic-leverage and funding-stress read from OFR repo "
                 "market data. Descriptive analysis only — not investment advice."),
    }
    _CACHE["snap"] = {"data": data, "ts": _t.time()}
    return data
