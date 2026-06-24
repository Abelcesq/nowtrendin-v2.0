"""
SEC EDGAR 13F-HR institutional-holdings research — HELD-OUT.

Imported by NOTHING in the scoring path (like referee_wikipedia.py). It surfaces WHERE
mega-cap institutional managers move billions, from the funds' own quarterly 13F-HR filings.

Source Onboarding Protocol (CLAUDE.md §16) status for this source:
  1. TYPE      — MARKET POSITIONING (institutional holdings; smart-money concentration).
  2. ENGINE    — would feed Market Signal `positioning_concentration` (financial_risk_gradient).
                 NOT wired yet — research-before-integrate per founder instruction.
  3. FORMAT    — parses the 13F information table into STRUCTURED holdings
                 (issuer · cusip · value · shares). Filing/report dates → ISO via the caller's
                 gate_date() at integration time.
  4. CURRENCY  — SEC EDGAR, quarterly 13F cadence, HTTP 200 with the REQUIRED descriptive
     + ACCESS    User-Agent (SEC policy; 10 req/s — we sleep 0.12s). Verified live.
  5. TEST      — this module + /research/13f is the TEST gate. Review the output, THEN decide
                 integration (and backtest-before-ship, since it is score-affecting).

Units note: from 2023-Q1 the SEC reports 13F `value` in DOLLARS (pre-2023 it was THOUSANDS).
We surface the report period so the unit is unambiguous; the latest filing is always dollars.
"""
from __future__ import annotations
import os
import re
import html
import time
import requests
from typing import Optional

SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "NowTrendIn Research contact@nowtrendin.com")

# Curated mega-cap institutional managers (13F filers) — the funds whose moves matter.
# CIK = the FUND's SEC Central Index Key (NOT a portfolio company's).
FUND_CIKS = {
    "Berkshire Hathaway":       "0001067983",
    "Bridgewater Associates":   "0001350694",
    "Renaissance Technologies": "0001037389",
    "BlackRock":                "0001364742",
    "Vanguard Group":           "0000102909",
    "State Street":             "0000093751",
    "Citadel Advisors":         "0001423053",
    "Two Sigma Investments":    "0001179392",
    "Tiger Global Management":  "0001167483",
    "Soros Fund Management":    "0001029160",
}


def _get(url: str, as_json: bool):
    """Rate-limited, properly-identified SEC request (SEC requires a descriptive UA)."""
    try:
        time.sleep(0.12)  # respect SEC's 10 req/s policy
        r = requests.get(url, headers={"User-Agent": SEC_USER_AGENT,
                                       "Accept-Encoding": "gzip, deflate"}, timeout=25)
        if r.status_code != 200:
            return None
        return r.json() if as_json else r.text
    except Exception as e:
        print(f"[13f] SEC fetch error {url}: {e}")
        return None


def _num(s: str) -> float:
    try:
        return float(re.sub(r"[^0-9.\-]", "", s or "")) if s else 0.0
    except Exception:
        return 0.0


def _tag(block: str, tag: str) -> str:
    """Namespace-agnostic single-tag value (handles <value>, <ns1:value>, etc.)."""
    m = re.search(rf"<(?:\w+:)?{tag}\b[^>]*>\s*(.*?)\s*</(?:\w+:)?{tag}>", block, re.S | re.I)
    return m.group(1).strip() if m else ""


def _parse_info_table(xml: str) -> list:
    """Parse a 13F information table XML into a list of holdings (namespace-agnostic)."""
    out = []
    for b in re.findall(r"<(?:\w+:)?infoTable\b[^>]*>(.*?)</(?:\w+:)?infoTable>", xml, re.S | re.I):
        issuer = _tag(b, "nameOfIssuer")
        if not issuer:
            continue
        issuer = re.sub(r"\s+", " ", html.unescape(issuer)).strip()   # FORMAT gate: decode &amp; etc.
        out.append({
            "issuer": issuer,
            "class": _tag(b, "titleOfClass"),
            "cusip": _tag(b, "cusip"),
            "value": _num(_tag(b, "value")),          # dollars (filings from 2023-Q1 on)
            "shares": _num(_tag(b, "sshPrnamt")),
            "put_call": _tag(b, "putCall"),
        })
    return out


def _find_info_table_url(cik: str, acc_nodash: str) -> Optional[str]:
    """Locate the information-table XML inside a 13F-HR filing folder via index.json."""
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_nodash}"
    idx = _get(f"{base}/index.json", as_json=True)
    names = []
    if idx:
        names = [it.get("name", "") for it in (idx.get("directory", {}).get("item", []))]
    # Prefer an explicit info-table XML; else any .xml that is not the primary cover doc.
    xmls = [n for n in names if n.lower().endswith(".xml")]
    pref = [n for n in xmls if "infotable" in n.lower() or "form13f" in n.lower()]
    for n in (pref or xmls):
        if "primary_doc" in n.lower():
            continue
        return f"{base}/{n}"
    return None


def latest_13f(cik: str, fund_name: str = "") -> dict:
    """Most recent 13F-HR holdings + concentration summary for a fund CIK. Read-only."""
    cik10 = str(cik).zfill(10)
    sub = _get(f"https://data.sec.gov/submissions/CIK{cik10}.json", as_json=True)
    if not sub:
        return {"available": False, "fund": fund_name, "cik": cik, "reason": "submissions fetch failed"}
    name = fund_name or sub.get("name", "")
    recent = sub.get("filings", {}).get("recent", {})
    forms = recent.get("form", []) or []
    accs = recent.get("accessionNumber", []) or []
    fdates = recent.get("filingDate", []) or []
    rdates = recent.get("reportDate", []) or []
    i = next((j for j, f in enumerate(forms) if f in ("13F-HR", "13F-HR/A")), None)
    if i is None:
        return {"available": False, "fund": name, "cik": cik, "reason": "no 13F-HR on file"}
    acc = accs[i]
    info_url = _find_info_table_url(cik, acc.replace("-", ""))
    if not info_url:
        return {"available": False, "fund": name, "cik": cik, "reason": "info-table XML not found",
                "filed": fdates[i] if i < len(fdates) else ""}
    xml = _get(info_url, as_json=False)
    rows = _parse_info_table(xml) if xml else []
    # Aggregate by security (cusip) — a 13F lists separate rows per investment manager /
    # discretion, so one issuer (e.g. Apple) appears several times; sum them to the TRUE
    # position the fund holds.
    agg: dict = {}
    for h in rows:
        key = h["cusip"] or h["issuer"]
        a = agg.setdefault(key, {"issuer": h["issuer"], "cusip": h["cusip"],
                                 "value": 0.0, "shares": 0.0, "put_call": h["put_call"]})
        a["value"] += h["value"]
        a["shares"] += h["shares"]
        if h["put_call"] and not a["put_call"]:
            a["put_call"] = h["put_call"]
    holdings = list(agg.values())
    holdings.sort(key=lambda h: h["value"], reverse=True)
    total = sum(h["value"] for h in holdings)
    top = holdings[:10]
    top_concentration = round(100 * sum(h["value"] for h in top) / total, 1) if total else 0.0
    return {
        "available": bool(holdings),
        "fund": name, "cik": cik,
        "report_period": rdates[i] if i < len(rdates) else "",
        "filed": fdates[i] if i < len(fdates) else "",
        "accession": acc,
        "holdings_count": len(holdings),
        "total_value_usd": round(total, 0),
        "top10_concentration_pct": top_concentration,
        "top_holdings": [
            {"issuer": h["issuer"], "cusip": h["cusip"], "value_usd": round(h["value"], 0),
             "shares": round(h["shares"], 0),
             "weight_pct": round(100 * h["value"] / total, 2) if total else 0.0,
             "put_call": h["put_call"]}
            for h in top
        ],
        "source": "SEC EDGAR 13F-HR", "held_out": True,
    }


def research_funds(only: Optional[list] = None, limit_funds: int = 10) -> dict:
    """Pull the latest 13F for the curated fund list (or a subset). Research output only."""
    items = [(n, c) for n, c in FUND_CIKS.items() if (not only or n in only or c in only)]
    results = []
    for name, cik in items[:limit_funds]:
        results.append(latest_13f(cik, name))
    ok = [r for r in results if r.get("available")]
    return {"funds_requested": len(items[:limit_funds]), "funds_ok": len(ok),
            "results": results, "held_out": True,
            "note": "HELD-OUT research — not wired into any score. Review before integration."}


if __name__ == "__main__":
    import json
    r = latest_13f(FUND_CIKS["Berkshire Hathaway"], "Berkshire Hathaway")
    print(json.dumps({k: v for k, v in r.items() if k != "top_holdings"}, indent=2))
    for h in r.get("top_holdings", [])[:10]:
        print(f"  {h['issuer'][:34]:34} ${h['value_usd']:>16,.0f}  {h['weight_pct']:>5}%  {h['shares']:>14,.0f} sh")
