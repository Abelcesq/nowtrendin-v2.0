# -*- coding: utf-8 -*-
"""
SHADOW LEDGER — the A4 trial instrument. HELD OUT. Sealed races for candidate feeds.

Nine-seat board 2026-08-20 (decision item 6), Chairman-ordered build. A prospective
shadow trial manufactures real sealed races — the thing no retro backtest can do. This
module is the infrastructure; the RULES live in the pre-registration document
(`audits/forecasts/SHADOW_TRIAL_PREREG_2026-08-20.md`), sealed to the PIT store BEFORE
the first enrollment. Code enforces what code can enforce:

  - ARMS, first-class: every enrollment carries an arm —
      'candidate'   candidate-feed first-crossings (the cohort under test)
      'control'     existing-roster first-crossings, identical rules, same window
      'null_random' random topics drawn from the SAME candidate feeds
      'null_volume' dumb-volume rule (>=k expert-tier mentions, no D logic)
    An absolute rate from one arm is uninterpretable; the DIFFERENCE is the result
    (Economist: "a shadow trial without a null arm can only produce a narrative").
  - IMMUTABLE rows: no UPDATE path exists for enrollment fields; resolution appends
    resolution fields once, exactly like the real ledger. Failed candidates are
    preserved forever (the graveyard is the evidence).
  - SNAPSHOT-AT-ENROLLMENT: every row stores its own evidence (signals count, venues,
    D-indicator snapshot, d_measured, regime stamp) at enrollment time — never
    dependent on the 7-day operational tables (the GHOST close-out lesson).
  - CENSORING-HONEST readouts: races run to the same 365-day patience window as the
    real ledger. `report()` always returns the censoring rate beside every rate and
    labels any pre-resolution read INTERIM (Forecaster: a 90-day calendar must never
    quietly re-impose itself on a 365-day forecast).
  - NEVER blends: nothing here is read by scoring, the published ledgers, or any
    served accuracy figure. Registered in heldout_registry; the AST firewall makes a
    scoring-side import a build failure.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Optional

import db_compat

DB_PATH = os.getenv("DB_PATH", "anomaly_detector.db")

ARMS = ("candidate", "control", "null_random", "null_volume")
# Same patience the real ledger runs (365d); enrollment window per the prereg.
SHADOW_PATIENCE_DAYS = int(os.getenv("SHADOW_PATIENCE_DAYS", "365"))
ENROLL_OPEN = os.getenv("SHADOW_ENROLL_OPEN", "2026-09-01")
ENROLL_CLOSE = os.getenv("SHADOW_ENROLL_CLOSE", "2026-11-30")
PREREG_DOC = "audits/forecasts/SHADOW_TRIAL_PREREG_2026-08-20.md"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _ph() -> str:
    return "%s" if db_compat.USE_PG else "?"


def init_db(db_path: str = DB_PATH) -> None:
    conn = db_compat.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS shadow_ledger (
                id TEXT PRIMARY KEY,
                arm TEXT, feed_set TEXT, domain TEXT,
                topic_key TEXT, topic_display TEXT,
                enrolled_at TEXT, detection_date TEXT,
                instrument_epoch TEXT, regime TEXT,
                d_measured INTEGER, d_indicators TEXT,
                signals_at_enroll INTEGER, venues_at_enroll INTEGER,
                sealed_query TEXT, sealed_wiki_article TEXT,
                -- resolution fields: written ONCE by resolve(), NULL until then
                resolved_at TEXT, breakout_date TEXT, lead_time_days INTEGER,
                verdict TEXT, query_ambiguous INTEGER, referee_note TEXT)
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_shadow_arm "
                     "ON shadow_ledger(arm, enrolled_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_shadow_open "
                     "ON shadow_ledger(verdict)")
        conn.commit()
    finally:
        conn.close()


def _row_id(arm: str, topic_key: str, detection_date: str) -> str:
    return hashlib.sha256(
        f"shadow|{arm}|{topic_key}|{detection_date}".encode()).hexdigest()[:20]


def enroll(*, arm: str, feed_set: str, domain: str, topic_key: str,
           topic_display: str, detection_date: str, instrument_epoch: str,
           regime: str, d_measured: Optional[int] = None,
           d_indicators: Optional[dict] = None, signals_at_enroll: int = 0,
           venues_at_enroll: int = 0, sealed_query: Optional[str] = None,
           sealed_wiki_article: Optional[str] = None,
           db_path: str = DB_PATH) -> Optional[str]:
    """Append one shadow race. Refuses outside the sealed enrollment window and
    refuses unknown arms — the window and arms are prereg'd, not parameters.
    Idempotent per (arm, topic, detection_date). Returns row id or None."""
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r} — arms are sealed in the prereg")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not (ENROLL_OPEN <= today <= ENROLL_CLOSE):
        return None   # outside the sealed window: a refusal, not an error
    init_db(db_path)
    conn = db_compat.connect(db_path)
    ph = _ph()
    try:
        rid = _row_id(arm, topic_key, detection_date)
        conn.execute(
            f"INSERT OR IGNORE INTO shadow_ledger (id, arm, feed_set, domain, "
            f"topic_key, topic_display, enrolled_at, detection_date, "
            f"instrument_epoch, regime, d_measured, d_indicators, "
            f"signals_at_enroll, venues_at_enroll, sealed_query, "
            f"sealed_wiki_article) VALUES "
            f"({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},"
            f"{ph},{ph},{ph},{ph})",
            (rid, arm, feed_set, domain, topic_key, topic_display, _now_iso(),
             detection_date, instrument_epoch, regime, d_measured,
             json.dumps(d_indicators, default=str) if d_indicators else None,
             signals_at_enroll, venues_at_enroll,
             sealed_query or topic_display, sealed_wiki_article))
        conn.commit()
        return rid
    finally:
        conn.close()


def resolve(row_id: str, *, breakout_date: Optional[str], verdict: str,
            lead_time_days: Optional[int] = None,
            query_ambiguous: Optional[int] = None,
            referee_note: Optional[str] = None,
            db_path: str = DB_PATH) -> bool:
    """Write resolution ONCE. A row that already has a verdict is never rewritten —
    same immutability as the real ledger."""
    conn = db_compat.connect(db_path)
    ph = _ph()
    try:
        cur = conn.execute(
            f"UPDATE shadow_ledger SET resolved_at = {ph}, breakout_date = {ph}, "
            f"lead_time_days = {ph}, verdict = {ph}, query_ambiguous = {ph}, "
            f"referee_note = {ph} WHERE id = {ph} AND verdict IS NULL",
            (_now_iso(), breakout_date, lead_time_days, verdict,
             query_ambiguous, referee_note, row_id))
        conn.commit()
        return bool(getattr(cur, "rowcount", 0))
    finally:
        conn.close()


def report(db_path: str = DB_PATH) -> dict:
    """Per-arm state with censoring printed beside every rate. Any read before all
    rows resolve is INTERIM by construction and says so. Rates are per-arm only —
    the RESULT of the trial is the candidate-vs-control/null DIFFERENCE, computed at
    readout per the prereg's sealed thresholds (never here, never early)."""
    init_db(db_path)
    conn = db_compat.connect(db_path)
    try:
        rows = [dict(r) for r in conn.execute(
            "SELECT arm, verdict, COUNT(*) AS n FROM shadow_ledger "
            "GROUP BY arm, verdict").fetchall()]
    finally:
        conn.close()
    arms = {}
    for r in rows:
        a = arms.setdefault(r["arm"], {"enrolled": 0, "resolved": 0,
                                       "by_verdict": {}})
        a["enrolled"] += r["n"]
        if r["verdict"]:
            a["resolved"] += r["n"]
            a["by_verdict"][r["verdict"]] = r["n"]
    for a in arms.values():
        a["censored_unresolved"] = a["enrolled"] - a["resolved"]
        a["censoring_rate_pct"] = (round(100.0 * a["censored_unresolved"]
                                         / a["enrolled"], 1)
                                   if a["enrolled"] else None)
    total = sum(a["enrolled"] for a in arms.values())
    resolved = sum(a["resolved"] for a in arms.values())
    return {
        "status": "INTERIM" if resolved < total or total == 0 else "FINAL-ELIGIBLE",
        "note": ("Races run to the 365-day patience window; the 11-30 date closes "
                 "ENROLLMENT, not races. No rate here is a result — results are the "
                 "candidate-vs-control differences at the prereg'd readouts, with "
                 "censoring always printed beside them. UNRESOLVED IS NEVER A "
                 "PENDING WIN."),
        "prereg": PREREG_DOC,
        "enrollment_window": [ENROLL_OPEN, ENROLL_CLOSE],
        "patience_days": SHADOW_PATIENCE_DAYS,
        "arms": arms,
        "total_enrolled": total,
        "total_resolved": resolved,
    }
