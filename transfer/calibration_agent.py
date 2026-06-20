"""
calibration_agent.py
====================
Read-only calibration & viability agent for Now TrendIn.

ROLE / INTENTION
  A scheduled VERIFIER and EVIDENCE-BUILDER. It runs every objective check in the
  calibration spec (Parts A–D of nowtrendin_calibration_instructions.md), produces
  ONE reproducible report, and writes an append-only "calibration epoch" the Accuracy
  Ledger can reference. It is NOT part of the scoring path and never makes the product
  early — it measures whether it is, and tells the dev exactly what to change.

WHAT IT DOES
  1. ENGINE-HEALTH SWEEP   — runs the trend + market diagnostics over the live universe,
                             tallies verdicts (saturation, what-if-N, leaks, cold-start…).
  2. LEDGER INTEGRITY AUDIT — checks same-surge matching, FP timeout, cohort maturity.
                             Flags defects; does NOT recompute the official hit rate.
  3. VIABILITY GATE        — Detection-vs-Trends lead/lag cross-correlation on the matured,
                             matched cohort → PASS / FAIL / INSUFFICIENT vs frozen bars.
  4. SOURCE ATTRIBUTION    — per-source lead distribution (which feeds actually lead).
  5. CALIBRATION EPOCH     — append-only record + per-row enrichment payload for the ledger.

HOW IT ADDS TO THE ACCURACY LEDGER  (additive only)
  • provenance stamp (methodology version + data-quality flags) so untrustworthy-score
    rows can be annotated/excluded;
  • an INDEPENDENT earliness metric (cross-correlation lead) beside LED/LAGGED;
  • source-origin tags explaining WHY a row led or lagged;
  • the engine state behind every number, for auditors.

WHAT IT DOES NOT DO
  • does NOT change any score, weight, tier, threshold, or ledger verdict;
  • does NOT generate detections or set breakout dates;
  • does NOT compute/overwrite the official honest hit rate (the ledger owns it);
  • does NOT tune the engine or "make it early";
  • does NOT declare viability on vibes — only PASS/FAIL/INSUFFICIENT vs frozen bars;
  • does NOT backfill or mutate historical ledger rows.

SUCCESS (for the AGENT, not the product)
  A run succeeds when it diagnoses every topic/instrument, audits the ledger, computes the
  gate on a matured cohort (or returns INSUFFICIENT), attributes sources, writes one epoch,
  and — re-run on identical inputs — produces IDENTICAL numbers. A successful run can and
  often will report the PRODUCT as FAIL or INSUFFICIENT. Keep the two ideas separate.

GOTCHAS
  • Freeze every threshold before running — tuning to pass voids the gate.
  • Cold-start topics can't be lead/lag tested (too little overlap) — excluded, not scored.
  • Google Trends is renormalized per query window — pull consistent windows.
  • Immature cohorts (younger than FP_TIMEOUT) are labeled IMMATURE and excluded from gate.
  • Enforce MATCH_WINDOW before computing leads or stale matches contaminate everything.
  • Read-only: never write to production score tables or ledger verdict columns.
  • Segment source attribution by provider (apify vs sweep) — different latency.
  • Use as-logged scores for lead/lag, never future-revised values (look-ahead leakage).
  • Below GATE_MIN_RESOLVED → INSUFFICIENT; a small-N PASS is never valid.
"""

from __future__ import annotations
import hashlib
import json
import math
import os
import statistics
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional, Callable

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

# diagnostics are twins of this file; degrade gracefully if not importable
try:
    import trend_signal_diagnostic as TSD
    import market_signal_diagnostic as MSD
    _DIAGS = True
except Exception:
    _DIAGS = False


# ─────────────────────────────────────────────────────────────────────────────
# FROZEN PARAMETERS  (version these; never tune to pass)
# ─────────────────────────────────────────────────────────────────────────────
MATCH_WINDOW_DAYS    = 30
FP_TIMEOUT_DAYS      = 90
LEADLAG_MAX_LAG_DAYS = 21
GATE_MEDIAN_LEAD_MIN = 3.0     # days; positive = early
GATE_LED_RATE_MIN    = 0.35
GATE_FP_RATE_MAX     = 0.30
GATE_MIN_RESOLVED    = 100
PARAM_VERSION        = "calib-params-v1"


# ─────────────────────────────────────────────────────────────────────────────
# INPUT SHAPES
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class LedgerRow:
    topic: str
    detection_date: date
    breakout_date: Optional[date]      # None = still pending
    verdict: Optional[str] = None      # LED | LAGGED | FP | None(pending)
    provider: Optional[str] = None
    logged_date: Optional[date] = None # when the detection was first logged

@dataclass
class Series:
    """Two day-aligned series over the SAME dates."""
    dates: list                         # list[date], ascending, equal spacing
    detection: list                     # engine Detection(t), as-logged
    trends: list                        # Google Trends interest(t)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _parse_date_cal(s: str) -> date:
    """Parse date string to date — tolerates ISO datetime and bare date."""
    s = (s or "").strip().replace("Z", "")
    if not s:
        raise ValueError("empty date string")
    # strip time component if present
    day = s.split("T")[0].split(" ")[0]
    for fmt in ("%Y-%m-%d", "%b %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(day, fmt).date()
        except ValueError:
            continue
    return datetime.fromisoformat(day).date()


# ─────────────────────────────────────────────────────────────────────────────
# LOADER FUNCTIONS — wired to live DB
# ─────────────────────────────────────────────────────────────────────────────

def load_live_topics() -> list:
    """A1: Load TopicInput for every active topic in velocity_scores."""
    if not _DIAGS:
        return []
    try:
        conn = db_compat.connect(DB_PATH)
        keys = [r[0] for r in conn.execute(
            "SELECT DISTINCT topic_key FROM velocity_scores LIMIT 200"
        ).fetchall()]
        conn.close()
    except Exception as e:
        print(f"[calibration] load_live_topics query error: {e}")
        return []
    result = []
    for k in keys:
        try:
            inp = TSD.load_diagnostic_input(k)
            if inp:
                result.append(inp)
        except Exception:
            pass
    return result


def load_live_instruments() -> list:
    """A2: Load InstrumentInput for every active instrument in market_signal_history."""
    if not _DIAGS:
        return []
    try:
        conn = db_compat.connect(DB_PATH)
        symbols = [r[0] for r in conn.execute(
            "SELECT DISTINCT item_key FROM market_signal_history LIMIT 100"
        ).fetchall()]
        conn.close()
    except Exception as e:
        print(f"[calibration] load_live_instruments query error: {e}")
        return []
    result = []
    for sym in symbols:
        try:
            inp = MSD.load_diagnostic_input(sym)
            if inp:
                result.append(inp)
        except Exception:
            pass
    return result


def load_detection_series(topic: str) -> Optional[Series]:
    """Load day-aligned Detection + Google Trends series for cross-correlation.
    Returns None if no trends data is available (cold start or no API key)."""
    try:
        conn = db_compat.connect(DB_PATH)
        rows = conn.execute(
            "SELECT scored_at, detection_score FROM velocity_scores "
            "WHERE topic_key = ? ORDER BY scored_at ASC",
            (topic,)
        ).fetchall()
        conn.close()
        if len(rows) < 5:
            return None

        from google_trends_validation import fetch_trends_curve
        curve = fetch_trends_curve(topic)
        if not curve:
            return None

        det_by_date = {}
        for r in rows:
            try:
                d = _parse_date_cal(str(r["scored_at"] if hasattr(r, "__getitem__") else r[0]))
                det_by_date[d] = float(r["detection_score"] if hasattr(r, "__getitem__") else r[1] or 0)
            except Exception:
                pass

        tr_by_date = {}
        for pt in curve:
            try:
                ds = str(pt.get("date", ""))[:10]
                if ds:
                    d = _parse_date_cal(ds)
                    tr_by_date[d] = float(pt.get("value", 0))
            except Exception:
                pass

        common = sorted(set(det_by_date) & set(tr_by_date))
        if len(common) < 5:
            return None

        return Series(
            dates=common,
            detection=[det_by_date[d] for d in common],
            trends=[tr_by_date[d] for d in common],
        )
    except Exception as e:
        print(f"[calibration] load_detection_series({topic}) error: {e}")
        return None


def load_ledger_rows() -> list:
    """Load all rows from accuracy_ledger + pending_detections as LedgerRow objects."""
    try:
        conn = db_compat.connect(DB_PATH)
        resolved = [dict(r) for r in conn.execute("SELECT * FROM accuracy_ledger").fetchall()]
        pending = [dict(r) for r in conn.execute(
            "SELECT * FROM pending_detections WHERE status='pending'"
        ).fetchall()]
        conn.close()
    except Exception as e:
        print(f"[calibration] load_ledger_rows error: {e}")
        return []

    rows = []
    for r in resolved:
        # Skip LATE_REDETECTION rows — already excluded from the honest denominator
        if r.get("verdict") == "LATE_REDETECTION":
            continue
        try:
            det_d = _parse_date_cal(str(r.get("detection_date") or ""))
            brk_d = _parse_date_cal(str(r["breakout_date"])) if r.get("breakout_date") else None
            log_d = _parse_date_cal(str(r["validated_at"])) if r.get("validated_at") else det_d
            rows.append(LedgerRow(
                topic=r["topic_key"],
                detection_date=det_d,
                breakout_date=brk_d,
                verdict=r.get("verdict"),
                provider=r.get("provider"),
                logged_date=log_d,
            ))
        except Exception:
            pass
    for p in pending:
        try:
            det_d = _parse_date_cal(str(p.get("detection_date") or ""))
            log_d = _parse_date_cal(str(p["last_checked"])) if p.get("last_checked") else det_d
            rows.append(LedgerRow(
                topic=p["topic_key"],
                detection_date=det_d,
                breakout_date=None,
                verdict=None,
                provider=None,
                logged_date=log_d,
            ))
        except Exception:
            pass
    return rows


def load_source_first_seen(topic: str) -> dict:
    """Return first-seen date per source for a topic.
    Stub — source_first_seen table is not yet built; returns empty dict."""
    return {}


def get_methodology_version() -> str:
    return os.getenv("ENGINE_VERSION", "grad-v2.x / mkt-v1.x")


def write_calibration_epoch(record: dict) -> None:
    """Append-only insert of a calibration epoch. One row per run_at timestamp."""
    try:
        conn = db_compat.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS calibration_epochs (
                id TEXT PRIMARY KEY,
                run_at TEXT NOT NULL,
                methodology_version TEXT,
                param_version TEXT,
                gate_status TEXT,
                gate_n INTEGER,
                gate_median_lead REAL,
                led_rate REAL,
                fp_rate REAL,
                payload TEXT
            )
        """)
        run_at = record.get("run_at", "")
        ep_id = hashlib.md5(run_at.encode()).hexdigest()[:16]
        gate = record.get("gate", {})
        conn.execute("""
            INSERT INTO calibration_epochs
                (id, run_at, methodology_version, param_version,
                 gate_status, gate_n, gate_median_lead, led_rate, fp_rate, payload)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT (id) DO NOTHING
        """, (
            ep_id, run_at,
            record.get("methodology_version", ""),
            record.get("param_version", PARAM_VERSION),
            gate.get("status"),
            gate.get("n_matched"),
            gate.get("median_lead"),
            gate.get("led_rate"),
            gate.get("fp_rate"),
            json.dumps(record),
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[calibration] write_calibration_epoch error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# CORE MATH (pure, reproducible)
# ─────────────────────────────────────────────────────────────────────────────
def _pearson(a, b):
    n = len(a)
    if n < 3:
        return 0.0
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    da = [x - ma for x in a]; db = [y - mb for y in b]
    num = sum(x * y for x, y in zip(da, db))
    den = math.sqrt(sum(x * x for x in da) * sum(y * y for y in db))
    return num / den if den else 0.0

def crosscorr_lead(s: Series, max_lag: int = LEADLAG_MAX_LAG_DAYS):
    """Lag (days) at which Detection best aligns with Trends.
    POSITIVE = Detection leads the breakout (early). Returns (lead_days, corr)."""
    det, tr, best, best_lag = s.detection, s.trends, -2.0, 0
    for lag in range(-max_lag, max_lag + 1):
        # align det[t] with trends[t+lag]; positive lag -> det leads
        if lag >= 0:
            a, b = det[:len(det) - lag], tr[lag:]
        else:
            a, b = det[-lag:], tr[:len(tr) + lag]
        if len(a) >= 5:
            c = _pearson(a, b)
            if c > best:
                best, best_lag = c, lag
    return best_lag, round(best, 3)

def _bootstrap_ci(vals, lo=2.5, hi=97.5, iters=2000, seed=11):
    import random
    if len(vals) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed); meds = []
    for _ in range(iters):
        sample = [vals[rng.randrange(len(vals))] for _ in vals]
        meds.append(statistics.median(sample))
    meds.sort()
    pick = lambda p: meds[min(len(meds) - 1, int(p / 100 * len(meds)))]
    return (pick(lo), pick(hi))


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 1 — ENGINE HEALTH SWEEP
# ─────────────────────────────────────────────────────────────────────────────
def engine_health(trend_inputs: list, market_inputs: list) -> dict:
    tally = {}
    def bump(v): tally[v] = tally.get(v, 0) + 1
    if _DIAGS:
        for t in trend_inputs:  bump("TREND:"  + TSD.diagnose(t).verdict)
        for m in market_inputs: bump("MARKET:" + MSD.diagnose(m).verdict)
    else:
        tally["diagnostics_unavailable"] = 1
    return tally


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 2 — LEDGER INTEGRITY AUDIT  (flags only; never recomputes hit rate)
# ─────────────────────────────────────────────────────────────────────────────
def ledger_audit(rows: list, today: date) -> dict:
    stale, fp_overdue, immature, matched = [], [], 0, []
    for r in rows:
        if r.breakout_date is not None:
            lag = (r.breakout_date - r.detection_date).days
            if abs(lag) > MATCH_WINDOW_DAYS:
                stale.append((r.topic, lag))     # C1 violation
            else:
                matched.append(r)
        else:  # pending
            age = (today - (r.logged_date or r.detection_date)).days
            if age > FP_TIMEOUT_DAYS:
                fp_overdue.append(r.topic)        # C3 violation
            else:
                immature += 1
    return {"stale_matches": stale, "fp_overdue": fp_overdue,
            "immature_pending": immature, "matched_resolved": matched}


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 3 — VIABILITY GATE
# ─────────────────────────────────────────────────────────────────────────────
def viability_gate(matched_rows: list, series_for: Callable[[str], Optional[Series]]) -> dict:
    leads, led, fp = [], 0, 0
    per_topic = []
    for r in matched_rows:
        s = series_for(r.topic)
        cc_lead, corr = (crosscorr_lead(s) if s else (None, None))
        ledger_lead = (r.breakout_date - r.detection_date).days if r.breakout_date else None
        if r.verdict == "FP":
            fp += 1
        if ledger_lead is not None and ledger_lead >= 1:
            led += 1
        if cc_lead is not None:
            leads.append(cc_lead)
        per_topic.append({"topic": r.topic, "ledger_lead": ledger_lead,
                          "xcorr_lead": cc_lead, "xcorr_r": corr, "verdict": r.verdict})

    n = len(matched_rows)
    med = statistics.median(leads) if leads else None
    ci = _bootstrap_ci(leads) if len(leads) >= 2 else (None, None)
    led_rate = led / n if n else 0.0
    fp_rate = fp / n if n else 0.0

    if n < GATE_MIN_RESOLVED:
        status, note = "INSUFFICIENT", f"matured matched events {n} < {GATE_MIN_RESOLVED}"
    else:
        passed = (med is not None and med >= GATE_MEDIAN_LEAD_MIN and ci[0] is not None
                  and ci[0] > 0 and led_rate >= GATE_LED_RATE_MIN and fp_rate <= GATE_FP_RATE_MAX)
        status = "PASS" if passed else "FAIL"
        note = "all bars cleared" if passed else "one or more bars missed"

    return {"status": status, "note": note, "n_matched": n,
            "median_lead": med, "lead_ci95": ci, "led_rate": round(led_rate, 3),
            "fp_rate": round(fp_rate, 3), "per_topic": per_topic,
            "provisional": (None if n >= GATE_MIN_RESOLVED else
                            ("PASS" if (med is not None and med >= GATE_MEDIAN_LEAD_MIN
                                        and led_rate >= GATE_LED_RATE_MIN
                                        and fp_rate <= GATE_FP_RATE_MAX) else "FAIL"))}


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 4 — SOURCE ATTRIBUTION
# ─────────────────────────────────────────────────────────────────────────────
def source_attribution(rows: list, first_seen_for: Callable[[str], dict]) -> dict:
    by_source = {}
    for r in rows:
        if r.breakout_date is None:
            continue
        fs = first_seen_for(r.topic) or {}
        for src, seen in fs.items():
            by_source.setdefault(src, []).append((r.breakout_date - seen).days)
    out = {}
    for src, leads in by_source.items():
        med = statistics.median(leads)
        out[src] = {"median_lead": med, "n": len(leads),
                    "verdict": "LEADING" if med > 0 else "LAGGING"}
    return out


# ─────────────────────────────────────────────────────────────────────────────
# ORCHESTRATION
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class AgentReport:
    methodology_version: str
    run_at: str
    health: dict
    audit: dict
    gate: dict
    sources: dict


def run(trend_inputs=None, market_inputs=None, ledger_rows=None,
        series_for=None, first_seen_for=None,
        methodology_version=None, today=None, write=False) -> AgentReport:
    """Run the full calibration suite. Uses live DB loaders by default."""
    today = today or date.today()
    methodology_version = methodology_version or get_methodology_version()

    trend_inputs   = trend_inputs   if trend_inputs   is not None else load_live_topics()
    market_inputs  = market_inputs  if market_inputs  is not None else load_live_instruments()
    ledger_rows    = ledger_rows    if ledger_rows    is not None else load_ledger_rows()
    series_for     = series_for     if series_for     is not None else load_detection_series
    first_seen_for = first_seen_for if first_seen_for is not None else load_source_first_seen

    health = engine_health(trend_inputs, market_inputs)
    audit = ledger_audit(ledger_rows, today)
    gate = viability_gate(audit["matched_resolved"], series_for)
    sources = source_attribution(ledger_rows, first_seen_for)

    rep = AgentReport(methodology_version=methodology_version,
                      run_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                      health=health, audit={k: (len(v) if isinstance(v, list) else v)
                                            for k, v in audit.items()},
                      gate={k: v for k, v in gate.items() if k != "per_topic"},
                      sources=sources)
    if write:
        epoch = {"methodology_version": methodology_version, "param_version": PARAM_VERSION,
                 "run_at": rep.run_at, "health": health, "gate": rep.gate,
                 "sources": sources, "row_enrichment": gate["per_topic"]}
        write_calibration_epoch(epoch)
    return rep


def print_report(r: AgentReport, audit_detail: dict) -> None:
    L = "═" * 76
    print(f"\n{L}\n CALIBRATION AGENT · {r.run_at} · engine {r.methodology_version}\n{L}")
    print(" ENGINE HEALTH (verdict tallies)")
    for k, v in sorted(r.health.items()):
        print(f"   {k:<34} {v}")
    print("\n LEDGER INTEGRITY")
    print(f"   stale matches (>±{MATCH_WINDOW_DAYS}d)   : {r.audit['stale_matches']}"
          + (f"  {audit_detail['stale_matches']}" if audit_detail.get('stale_matches') else ""))
    print(f"   FP overdue (>{FP_TIMEOUT_DAYS}d pending) : {r.audit['fp_overdue']}")
    print(f"   immature pending                : {r.audit['immature_pending']}")
    print(f"   matured matched resolved        : {r.audit['matched_resolved']}")
    g = r.gate
    print("\n VIABILITY GATE")
    print(f"   matured matched events : {g['n_matched']}  (need ≥ {GATE_MIN_RESOLVED})")
    print(f"   median xcorr lead      : {g['median_lead']}  (bar ≥ +{GATE_MEDIAN_LEAD_MIN}d)")
    print(f"   lead 95% CI            : {g['lead_ci95']}  (lower must be > 0)")
    print(f"   LED rate / FP rate     : {g['led_rate']} / {g['fp_rate']}  "
          f"(bars ≥ {GATE_LED_RATE_MIN} / ≤ {GATE_FP_RATE_MAX})")
    prov = f"   (provisional read on this small sample: {g['provisional']})" if g['provisional'] else ""
    print(f"\n   >>> GATE: {g['status']} — {g['note']}")
    if prov:
        print(prov)
    print("\n SOURCE ATTRIBUTION (lead = breakout − first-seen; + = leads)")
    for src, d in sorted(r.sources.items(), key=lambda kv: -kv[1]['median_lead']):
        print(f"   {src:<14} median_lead {d['median_lead']:+.0f}d  n={d['n']}  {d['verdict']}")
    print(f"{L}\n")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT — runs against live DB when called directly
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("[calibration] Running against live DB…")
    audit_rows = load_ledger_rows()
    audit_detail = ledger_audit(audit_rows, date.today())
    rep = run(write=True)
    print_report(rep, audit_detail)
