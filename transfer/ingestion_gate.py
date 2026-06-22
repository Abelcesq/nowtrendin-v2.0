"""
ingestion_gate.py — the CONDITION-PRECEDENT format filter for data entering the DB.

Every date-semantic value should pass through gate_date() BEFORE it is written. The
gate is the single enforcement point for the canonical-date rule:

  • it normalizes the value to the canonical PRIMARY ISO 'YYYY-MM-DD' (via date_utils);
  • on a NON-empty value it cannot confidently parse, it does NOT guess — it QUARANTINES
    the raw value to the format_review_queue (so a human decides the mapping) and returns
    a safe default (today) instead of a corrupt date; nothing corrupt ever reaches a
    scoring/sort column;
  • a human decision saved to format_rules is auto-applied to identical future inputs.

The nightly audit surfaces pending reviews (pending_reviews) as an alert — the human
escalation channel the operator answers. Forward-only: it gates NEW writes and never
deletes or rewrites existing rows (respects the 90-day retention + no-quality-delete
rules). It changes ONLY the date string — never a score, weight, component, or which
data feeds a formula.

CONTRACT — date-semantic columns (canonical primary 'YYYY-MM-DD'):
  accuracy_ledger.detection_date, accuracy_ledger.breakout_date,
  pending_detections.detection_date, risk_signals.signal_date,
  pull_history.snapshot_date, score_archive.snapshot_date, topic_baselines.snapshot_date
Operational TIMESTAMP columns (scored_at, collected_at, validated_at, cycle_at, *_at …)
keep their precise instant as the SECONDARY value via date_utils.to_iso_dt.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib

from date_utils import to_iso_date

# date-semantic columns → canonical primary 'YYYY-MM-DD' (the sort/score key)
DATE_SEMANTIC = {
    "accuracy_ledger":    ["detection_date", "breakout_date"],
    "pending_detections": ["detection_date"],
    "risk_signals":       ["signal_date"],
    "pull_history":       ["snapshot_date"],
    "score_archive":      ["snapshot_date"],
    "topic_baselines":    ["snapshot_date"],
}


def ensure_tables(conn) -> None:
    """Idempotent DDL for the escalation queue + learned rules. Creates only;
    writes no value rows."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS format_review_queue (
            id           TEXT PRIMARY KEY,
            created_at   TEXT NOT NULL,
            table_name   TEXT NOT NULL,
            column_name  TEXT NOT NULL,
            raw_value    TEXT,
            source       TEXT,
            field_class  TEXT,
            candidates   TEXT,
            status       TEXT DEFAULT 'pending',
            resolved_at  TEXT,
            chosen_value TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS format_rules (
            id           TEXT PRIMARY KEY,
            created_at   TEXT NOT NULL,
            table_name   TEXT,
            column_name  TEXT,
            raw_pattern  TEXT,
            normalized   TEXT
        )
    """)


def _candidates(raw: str) -> str:
    """Plausible normalizations to offer the human (e.g. start-of-range for a
    'May 22 – 28, 2026' week label)."""
    out = []
    for variant in (raw.split("–")[0].strip(), raw.split(" - ")[0].strip(),
                    raw.replace(",", "")):
        iso = to_iso_date(variant)
        if iso and iso not in out:
            out.append(iso)
    return "; ".join(out)


def _record_review(conn, table, column, raw_value, source, candidates) -> None:
    rid = hashlib.md5(f"{table}.{column}|{raw_value}|{source}".encode()).hexdigest()[:16]
    conn.execute(
        "INSERT OR IGNORE INTO format_review_queue "
        "(id, created_at, table_name, column_name, raw_value, source, field_class, "
        " candidates, status) VALUES (?,?,?,?,?,?,?,?, 'pending')",
        (rid, datetime.now(timezone.utc).isoformat(), table, column,
         str(raw_value)[:200], source or "", "date_semantic", candidates or ""))


def gate_date(value, *, table=None, column=None, source=None, conn=None,
              default_today: bool = True):
    """CONDITION-PRECEDENT for a date-semantic value. Returns canonical 'YYYY-MM-DD'.

    success  → the parsed ISO date.
    empty    → safe default (today) or None — not a format defect.
    UNPARSEABLE non-empty → quarantine to format_review_queue (if conn given) for a
        human decision, and return today's date (default_today) or None. NEVER a
        corrupt value."""
    iso = to_iso_date(value)
    if iso:
        return iso
    raw = "" if value is None else str(value).strip()
    if not raw:
        return to_iso_date("", default_today=default_today)
    # unparseable, non-empty → ESCALATE to a human
    if conn is not None:
        try:
            ensure_tables(conn)
            _record_review(conn, table or "?", column or "?", raw, source, _candidates(raw))
        except Exception:
            pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d") if default_today else None


def pending_reviews(conn, limit: int = 50) -> list:
    """The human escalation feed — unresolved format decisions. Surfaced by the
    nightly audit."""
    try:
        ensure_tables(conn)
        rows = conn.execute(
            "SELECT id, table_name, column_name, raw_value, source, candidates, created_at "
            "FROM format_review_queue WHERE status='pending' ORDER BY created_at DESC LIMIT ?",
            (limit,)).fetchall()
    except Exception:
        return []
    out = []
    for r in rows:
        if hasattr(r, "keys"):
            out.append(dict(r))
        else:
            out.append({"id": r[0], "table_name": r[1], "column_name": r[2],
                        "raw_value": r[3], "source": r[4], "candidates": r[5],
                        "created_at": r[6]})
    return out


def resolve_review(conn, review_id: str, chosen_value: str, *, save_rule: bool = True) -> None:
    """Apply a human decision: mark the review resolved and (optionally) learn a rule
    so identical future inputs auto-normalize."""
    ensure_tables(conn)
    conn.execute(
        "UPDATE format_review_queue SET status='resolved', resolved_at=?, chosen_value=? "
        "WHERE id=?",
        (datetime.now(timezone.utc).isoformat(), chosen_value, review_id))
    if save_rule:
        row = conn.execute(
            "SELECT table_name, column_name, raw_value FROM format_review_queue WHERE id=?",
            (review_id,)).fetchone()
        if row:
            d = dict(row) if hasattr(row, "keys") else {
                "table_name": row[0], "column_name": row[1], "raw_value": row[2]}
            rid = hashlib.md5(
                f"rule|{d['table_name']}.{d['column_name']}|{d['raw_value']}".encode()
            ).hexdigest()[:16]
            conn.execute(
                "INSERT OR IGNORE INTO format_rules "
                "(id, created_at, table_name, column_name, raw_pattern, normalized) "
                "VALUES (?,?,?,?,?,?)",
                (rid, datetime.now(timezone.utc).isoformat(), d["table_name"],
                 d["column_name"], str(d["raw_value"]), chosen_value))
    conn.commit()
