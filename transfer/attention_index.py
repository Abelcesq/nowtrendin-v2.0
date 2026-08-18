"""
attention_index.py — NTI Same-Day Attention 50 (`NTI-SD50`).

Chairman ruling (c), 2026-08-18: frozen, register-appended rules -> daily
UNMARKETED index calculation, accruing the un-backfillable live record.

THE RULES ARE FROZEN. The authority is the register:
`audits/index/INDEX_RULEBOOK_REGISTER.md`, entry r1 (`idx-r1-2026-08-18`).
Do NOT change any constant or query below without a NEW register entry (r2, ...)
with a new RULES_VERSION — forward-only, never retroactive.

Standing constraints implemented here:
- NO BACK-HISTORY, EVER: a day the calculation missed stays ABSENT forever;
  compute() refuses to run for any day but the current UTC day.
- Detection only; N is never read (anti-circularity).
- No ledger reads (evidence separation).
- The value is recorded solely to the bitemporal PIT store (kind='index_value')
  — append-only, trigger-enforced, hash-chain-sealed. Reproducible from its own
  sealed payload (full constituent list included).
- UNMARKETED: nothing here is served to any user surface.

HELD-OUT: reads stored scores, writes only the PIT record. Nothing here feeds
back into scoring, calibration, or any served value.
"""
from __future__ import annotations

import os
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import db_compat
import pit_store

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

# ── FROZEN (register r1) — see module docstring before touching ─────────────
INDEX_KEY = "NTI-SD50"
RULES_VERSION = "idx-r1-2026-08-18"
WINDOW_H = 24          # R2: universe = topics scored in the trailing 24h
EMBARGO_H = 48         # R3: must have a row at least this old (reflexivity RC1)
TOP_N = 50             # R4
MIN_ELIGIBLE = 10      # R4: below this the day is ABSENT, never fabricated
CALC_FROM_HOUR_UTC = 1  # R1: at or after 01:00 UTC
# ─────────────────────────────────────────────────────────────────────────────


def _connect(db_path):
    conn = db_compat.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _already_recorded(day: str, db_path: str) -> bool:
    pit_store._ensure_init(db_path)
    conn = _connect(db_path)
    try:
        r = conn.execute(
            "SELECT 1 FROM pit_observations WHERE kind = 'index_value' "
            "AND item_key = ? AND event_date = ? LIMIT 1",
            (INDEX_KEY, day)).fetchone()
        return r is not None
    finally:
        conn.close()


def compute_and_record(db_path: str = DB_PATH) -> dict:
    """Compute today's (UTC) index value per register r1 and seal it into the
    PIT store. Idempotent — a day already recorded is never recomputed.
    Refuses to compute for any day but today (no back-history, ever)."""
    t_calc = _utcnow()
    day = t_calc.strftime("%Y-%m-%d")
    if _already_recorded(day, db_path):
        return {"day": day, "skipped": "already recorded (one value per UTC day)"}

    cut24 = (t_calc - timedelta(hours=WINDOW_H)).isoformat()
    cut48 = (t_calc - timedelta(hours=EMBARGO_H)).isoformat()

    conn = _connect(db_path)
    try:
        # R2: latest row per topic within the 24h window (Detection only — R7).
        rows = conn.execute(
            "SELECT topic_key, detection_score, scored_at FROM velocity_scores "
            "WHERE scored_at >= ? ORDER BY scored_at DESC", (cut24,)).fetchall()
        latest = {}
        for r in rows:
            k = r["topic_key"]
            if k not in latest:            # first hit is the latest (DESC order)
                latest[k] = r["detection_score"] or 0.0
        universe_count = len(latest)

        # R3: embargo — topic must predate t_calc − 48h in the system.
        eligible = set()
        keys = list(latest.keys())
        for i in range(0, len(keys), 400):
            chunk = keys[i:i + 400]
            ph = ",".join("?" * len(chunk))
            got = conn.execute(
                f"SELECT DISTINCT topic_key FROM velocity_scores "
                f"WHERE scored_at <= ? AND topic_key IN ({ph})",
                [cut48] + chunk).fetchall()
            eligible.update(g["topic_key"] for g in got)
        eligible_count = len(eligible)
    finally:
        conn.close()

    if eligible_count < MIN_ELIGIBLE:
        payload = {"value": None, "absent": True,
                   "reason": f"eligible universe {eligible_count} < {MIN_ELIGIBLE}",
                   "rules_version": RULES_VERSION, "t_calc": t_calc.isoformat(),
                   "universe_count": universe_count,
                   "eligible_count": eligible_count}
        pit_store.record("index_value", INDEX_KEY, day, payload, db_path=db_path)
        return {"day": day, "value": None, "absent": True, **payload}

    # R4: top-50 by detection desc, ties by topic_key asc (deterministic).
    ranked = sorted(((latest[k], k) for k in eligible),
                    key=lambda t: (-t[0], t[1]))[:TOP_N]
    # R5: equal-weight mean, 2dp.
    value = round(sum(d for d, _ in ranked) / len(ranked), 2)

    payload = {
        "value": value, "rules_version": RULES_VERSION,
        "t_calc": t_calc.isoformat(),
        "universe_count": universe_count, "eligible_count": eligible_count,
        "n_constituents": len(ranked),
        # R8: the full constituent list — the value is reproducible from its
        # own sealed record.
        "constituents": [{"k": k, "d": round(d, 1)} for d, k in ranked],
    }
    sha = pit_store.record("index_value", INDEX_KEY, day, payload,
                           db_path=db_path)
    return {"day": day, "value": value, "n_constituents": len(ranked),
            "universe_count": universe_count, "eligible_count": eligible_count,
            "recorded": bool(sha), "rules_version": RULES_VERSION}


def recent(days: int = 14, db_path: str = DB_PATH) -> list:
    """Last N recorded index values (read-only, from the sealed record)."""
    pit_store._ensure_init(db_path)
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT event_date, knowable_at, payload, row_sha256 "
            "FROM pit_observations WHERE kind = 'index_value' AND item_key = ? "
            "ORDER BY event_date DESC LIMIT ?", (INDEX_KEY, days)).fetchall()
        import json
        out = []
        for r in rows:
            p = json.loads(r["payload"])
            out.append({"event_date": r["event_date"],
                        "value": p.get("value"),
                        "absent": bool(p.get("absent")),
                        "n_constituents": p.get("n_constituents"),
                        "rules_version": p.get("rules_version"),
                        "row_sha256": r["row_sha256"]})
        return out
    finally:
        conn.close()


def daily_loop(interval_s: int = 1800, db_path: str = DB_PATH) -> None:
    """Wake every 30 min; once past 01:00 UTC, compute today's value if it is
    not already sealed (idempotent). A day that never got a run stays ABSENT
    forever — this loop never reaches backward."""
    time.sleep(40)   # let the app boot
    while True:
        try:
            now = _utcnow()
            if now.hour >= CALC_FROM_HOUR_UTC:
                r = compute_and_record(db_path)
                if "skipped" not in r:
                    print(f"[attention_index] {r.get('day')}: "
                          f"value={r.get('value')} "
                          f"(n={r.get('n_constituents')}, "
                          f"universe={r.get('universe_count')})")
        except Exception as e:
            print(f"[attention_index] loop error: {e}")
        time.sleep(interval_s)
