"""
scoring_contract.py — the declared FORMAT CONTRACT for every scoring field, plus a
data auditor. The generalization of the canonical-date model (date_utils +
ingestion_gate, which formalized ONLY dates) to ALL scoring inputs/outputs.

WHY: the project hit a non-obvious bug class — data written in a format the scoring
model/agent could not read, silently coerced to a default (None/0/""), so the score
was computed on MISSING data while looking fine (the canonical-date bug was one
instance; the AI-grade N-weight, engagement_asymmetry key drift, risk_stage dual-enum,
and heisenberg_gap staleness were others). This module makes the format requirement
EXPLICIT and machine-checkable per field, and the Scoring Contract Auditor (monitoring
Agent 17) audits the LIVE DATA against it — so a silent misread is caught no matter
which code path produced it, and a NEW scoring field is flagged for classification.

CONTRACT SPEC per field: type ('scalar'|'enum'|'bool'|'count'|'json'), unit/range
(min/max), enum (allowed values, exact casing), required (non-null on every row),
derived (an expression that must equal the stored value, e.g. heisenberg_gap), and
in_composite (False = must never enter the Gradient, the no-circularity guard).
Read-only: this module validates + reports; it never writes a score.
"""
from __future__ import annotations

SCALAR = {"type": "scalar", "min": 0.0, "max": 100.0}
STAGE_ENUM = ["BREAKOUT", "STRONG", "EMERGING", "MARGINAL", "WATCHING", "MONITORING"]
# MODERATE is the user-facing relabel of BUILDING (Market-Signal de-Congress reframe, 2026-06-26).
# BUILDING is retained for historical rows (365-day retention) + the financial_risk_gradient module
# which still emits it; both are valid stages.
MARKET_TIER_ENUM = ["ELEVATED", "ACTIVE", "MODERATE", "BUILDING", "ROUTINE", "DORMANT"]

# table -> column -> spec.  The declared, single-source-of-truth format for scoring fields.
SCORING_CONTRACT = {
    "velocity_scores": {
        "detection_score":  {**SCALAR, "required": True,  "producer": "score_topic -> apply_calibration"},
        "confidence_score": {**SCALAR, "required": True,  "producer": "score_topic -> apply_calibration"},
        "overall_score":    {**SCALAR, "required": True,  "producer": "score_topic -> apply_calibration"},
        "heisenberg_gap":   {"type": "scalar", "min": -100.0, "max": 100.0,
                             "derived": ("detection_score", "confidence_score")},  # = det - conf (signed)
        "gradient_strength":  {**SCALAR, "producer": "compute_gradient_strength"},
        "inertia_score":      {**SCALAR, "producer": "compute_inertia"},
        "platform_diversity": {**SCALAR, "producer": "compute_platform_diversity"},
        "dark_matter_score":  {**SCALAR, "producer": "compute_dark_matter"},
        "confidence_decay":   {**SCALAR, "producer": "compute_confidence_decay"},
        "persistence_score":  {**SCALAR, "producer": "compute_persistence"},
        "nowtrendin_score":   {**SCALAR, "in_composite": False, "producer": "compute_nowtrendin_score"},
        "signal_stage":       {"type": "enum", "enum": STAGE_ENUM, "required": True, "producer": "stage_of"},
        "is_gravitational_anomaly": {"type": "bool", "producer": "score_topic"},
    },
    "risk_scores": {
        "detection_score":  {**SCALAR, "producer": "compute_market_signal / risk gradient"},
        "confidence_score": {**SCALAR, "producer": "compute_market_signal / risk gradient"},
        "risk_stage":       {"type": "enum", "enum": MARKET_TIER_ENUM, "required": True,
                             "producer": "market tier (risk vocab mapped via _RISK_TO_MARKET_TIER)"},
        "total_signals":    {"type": "count", "min": 0, "producer": "risk collection"},
    },
}

# Columns whose NAME looks like a scoring field (for discovery / drift). A live column
# matching this that is NOT in SCORING_CONTRACT is flagged 'classify it'.
import re
_SCORING_NAME = re.compile(r"(_score|_diversity|_strength|_decay|_gap|_stage|score|detection|confidence)$", re.I)
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DEGENERATE_SHARE = 0.90   # a scalar field identical on >=90% of rows = silent-misread fingerprint
DEGENERATE_MINROWS = 20


def _is_num(v):
    try:
        float(v); return True
    except (TypeError, ValueError):
        return False


def check_value(spec, v):
    """Return None if OK, else a short violation reason for value v under spec."""
    t = spec.get("type")
    empty = v is None or (isinstance(v, str) and v.strip() == "")
    if empty:
        return "required-but-null" if spec.get("required") else None
    if t in ("scalar", "count"):
        if not _is_num(v):
            return f"non-numeric ({v!r})"
        fv = float(v)
        if "min" in spec and fv < spec["min"] - 1e-6:
            return f"below-min ({fv} < {spec['min']})"
        if "max" in spec and fv > spec["max"] + 1e-6:
            return f"above-max ({fv} > {spec['max']})"
        if t == "count" and abs(fv - round(fv)) > 1e-6:
            return f"non-integer count ({fv})"
        return None
    if t == "enum":
        if str(v) not in spec["enum"]:
            return f"off-enum ({v!r} not in {spec['enum']})"
        return None
    if t == "bool":
        if v in (0, 1, True, False) or str(v) in ("0", "1", "True", "False", "true", "false"):
            return None
        return f"non-bool ({v!r})"
    return None


def _rows_dict(rows):
    out = []
    for r in rows:
        out.append(dict(r) if hasattr(r, "keys") else r)
    return out


def _live_columns(conn, table):
    try:
        import db_compat
        if getattr(db_compat, "USE_PG", False):
            rs = conn.execute("SELECT column_name FROM information_schema.columns "
                              "WHERE table_schema='public' AND table_name=%s" if False else
                              "SELECT column_name FROM information_schema.columns "
                              "WHERE table_schema='public' AND table_name=?", (table,)).fetchall()
            return {(r["column_name"] if hasattr(r, "keys") else r[0]) for r in rs}
        rs = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return {(r["name"] if hasattr(r, "keys") else r[1]) for r in rs}
    except Exception:
        return set()


def _fetch(conn, table, limit=800):
    """Latest row per entity for the table (velocity_scores keyed on topic_key,
    risk_scores on risk_topic), newest first."""
    key = "topic_key" if table == "velocity_scores" else "risk_topic"
    for q in (
        f"SELECT v.* FROM {table} v INNER JOIN (SELECT {key}, MAX(scored_at) m FROM {table} "
        f"GROUP BY {key}) l ON v.{key}=l.{key} AND v.scored_at=l.m LIMIT {int(limit)}",
        f"SELECT * FROM {table} ORDER BY scored_at DESC LIMIT {int(limit)}",
        f"SELECT * FROM {table} LIMIT {int(limit)}",
    ):
        try:
            return _rows_dict(conn.execute(q).fetchall())
        except Exception:
            continue
    return []


def audit(conn) -> dict:
    """Audit the live data against SCORING_CONTRACT. Returns structured findings:
    per-field conformance, derived-field consistency, degenerate (flat) fields, and
    unregistered scoring-shaped columns. Read-only."""
    from collections import Counter
    report = {"fields": [], "violations": [], "degenerate": [], "derived_mismatch": [],
              "unregistered_columns": [], "tables": {}}

    for table, fields in SCORING_CONTRACT.items():
        rows = _fetch(conn, table)
        report["tables"][table] = len(rows)
        if not rows:
            continue
        live_cols = _live_columns(conn, table)

        # discovery: scoring-shaped live columns not declared
        for c in sorted(live_cols):
            if _SCORING_NAME.search(c) and c not in fields and _IDENT.match(c):
                report["unregistered_columns"].append(f"{table}.{c}")

        for col, spec in fields.items():
            if live_cols and col not in live_cols:
                report["fields"].append({"field": f"{table}.{col}", "rows": 0,
                                         "note": "declared but ABSENT from live schema"})
                report["violations"].append({"field": f"{table}.{col}", "kind": "missing-column",
                                              "detail": "declared in contract but not in table"})
                continue
            vals = [r.get(col) for r in rows]
            bad = []
            for v in vals:
                why = check_value(spec, v)
                if why:
                    bad.append((v, why))
            present = [v for v in vals if not (v is None or (isinstance(v, str) and v.strip() == ""))]
            entry = {"field": f"{table}.{col}", "rows": len(vals),
                     "violations": len(bad), "null_or_empty": len(vals) - len(present)}
            if bad:
                exs = list({f"{w} e.g.{v!r}" for v, w in bad})[:3]
                entry["examples"] = exs
                report["violations"].append({"field": f"{table}.{col}", "kind": "value",
                                              "count": len(bad), "examples": exs})
            # degenerate (flat) numeric scoring field = silent-misread fingerprint (C3 class)
            if spec.get("type") == "scalar" and len(present) >= DEGENERATE_MINROWS:
                nums = [round(float(v), 3) for v in present if _is_num(v)]
                if nums:
                    val, cnt = Counter(nums).most_common(1)[0]
                    share = cnt / len(nums)
                    entry["flat_share"] = round(share, 3)
                    if share >= DEGENERATE_SHARE:
                        report["degenerate"].append({"field": f"{table}.{col}", "value": val,
                                                     "share": round(share, 3), "rows": len(nums)})
            # derived-field consistency (e.g. heisenberg_gap == detection - confidence)
            if "derived" in spec:
                a, b = spec["derived"]
                mism = 0
                for r in rows:
                    try:
                        exp = round(float(r.get(a) or 0) - float(r.get(b) or 0), 1)
                        got = float(r.get(col)) if _is_num(r.get(col)) else None
                        if got is None or abs(got - exp) > 0.2:
                            mism += 1
                    except Exception:
                        mism += 1
                entry["derived_mismatch"] = mism
                if mism:
                    report["derived_mismatch"].append({"field": f"{table}.{col}",
                        "rule": f"{col} == {a} - {b}", "mismatched_rows": mism, "of": len(rows)})
            report["fields"].append(entry)

    return report
