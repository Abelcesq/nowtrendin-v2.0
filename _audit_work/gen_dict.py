"""Regenerate DB_DATA_DICTIONARY.md from the LIVE schema (/schema) + the Canonical Date
Auditor (/monitor/datecanon). One-off generator kept in _audit_work/ (not the engine).
Run after fetching _audit_work/live_schema.json and _audit_work/datecanon.json."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
schema = json.load(open(os.path.join(HERE, "live_schema.json")))
canon = json.load(open(os.path.join(HERE, "datecanon.json")))

# date-semantic columns the Canonical Date Auditor verifies (table.column -> info)
bycol = {c["column"]: c for c in canon.get("summary", {}).get("by_column", [])}

# Postgres extension tables — not part of the app schema.
SKIP = {"pg_stat_statements", "pg_stat_statements_info"}

def fmt_note(table, col, typ):
    key = f"{table}.{col}"
    if key in bycol:
        b = bycol[key]
        return f"**canonical `signal_date` (ISO YYYY-MM-DD)** · datecanon: {b['non_canonical']}/{b['rows']} non-canonical"
    if col.endswith("_date") or col == "snapshot_date":
        return "canonical date (ISO YYYY-MM-DD) via `gate_date()`"
    if col in ("source_time", "signal_time"):
        return "24h-UTC time `HH:MM:SS` (§14 secondary)"
    if col.endswith("_at"):
        return "ISO datetime (operational instant via `to_iso_dt`)"
    return ""

tables = [t for t in schema["tables"] if t["table"] not in SKIP]

out = []
out.append("# NowTrendIn DB — Data Dictionary")
out.append("")
out.append("_Regenerated **2026-06-24** from the LIVE Postgres schema "
           "(`GET /schema`) + the Canonical Date Auditor (`GET /monitor/datecanon`). "
           "This is the source of truth — earlier versions were pre-migration "
           "(showed dropped columns like `market_signal_history.cycle_at` and mixed date "
           "formats the live schema no longer has). To refresh: re-fetch both endpoints "
           "and re-run `_audit_work/gen_dict.py`._")
out.append("")
out.append(f"**{len(tables)} app tables** (Postgres `pg_stat_statements*` extension tables "
           "excluded). Row counts are planner estimates (`reltuples`; `-1`/`?` = not yet "
           "analyzed). Engine: `nowtrendin-v2-engine`.")
out.append("")
out.append("> **Canonical date model (§14):** every date-semantic value normalizes to a "
           "PRIMARY `signal_date` = ISO `YYYY-MM-DD`; secondary `source_time` (source's own "
           "HH:MM:SS) + `signal_time` (our fetch). Enforced by `ingestion_gate.gate_date()`. "
           "Live: **0 non-canonical across all declared date columns**.")
out.append("> **Retention:** `velocity_scores` rows kept **365 days** (canonical, 2026-06-24); "
           "never deleted within the window.")
out.append("")
out.append("---")
out.append("")

for t in tables:
    n = t.get("row_estimate")
    nlabel = "?" if (n is None or n < 0) else f"{n:,}"
    out.append(f"## `{t['table']}`  ({nlabel} rows · {len(t['columns'])} cols)")
    out.append("")
    out.append("| column | type | null | notes |")
    out.append("|---|---|---|---|")
    for c in t["columns"]:
        note = fmt_note(t["table"], c["column"], c["type"])
        nul = "" if c["nullable"] else "NOT NULL"
        out.append(f"| `{c['column']}` | {c['type']} | {nul} | {note} |")
    out.append("")

# date-canon compliance appendix
out.append("---")
out.append("")
out.append("## Canonical date columns (datecanon-verified)")
out.append("")
out.append("| column | rows | non-canonical |")
out.append("|---|---|---|")
for c in canon.get("summary", {}).get("by_column", []):
    out.append(f"| `{c['column']}` | {c.get('rows')} | {c.get('non_canonical')} |")
out.append("")

doc = "\n".join(out) + "\n"
with open(os.path.join(os.path.dirname(HERE), "DB_DATA_DICTIONARY.md"), "w", encoding="utf-8") as f:
    f.write(doc)
print(f"wrote DB_DATA_DICTIONARY.md — {len(tables)} tables, {sum(len(t['columns']) for t in tables)} columns")
