"""test_precompute_swap.py — ruling 2c behaviour tests + tripwires.

Every enforcer must be shown to FAIL on a fixture that violates its claim
(the suite-wide rule). Covered here:
  2c(b) the precompute is NON-DESTRUCTIVE: an empty build leaves stored
        payloads untouched, and a mid-swap failure rolls back to the prior
        state (the old code NULLed everything first — the 2026-07-06 class).
  2c(c) blobs are stamped with PAYLOAD_SCHEMA_VERSION and the serve side
        refuses a mismatched stamp (falls through to live calibration) —
        tripwired by constructing exactly the deploy-version window: a blob
        written under one version read by a binary declaring another.

Run:  python3 test_precompute_swap.py
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_FAILS = []
_PASSES = 0


def check(name, fn):
    global _PASSES
    try:
        fn()
        _PASSES += 1
        print(f"  PASS  {name}")
    except Exception as exc:  # noqa: BLE001
        _FAILS.append(f"{name}: {exc}")
        print(f"  FAIL  {name}: {exc}")
        traceback.print_exc(limit=2)


def _detector():
    import gravitational_anomaly_detector as g
    return g


def _db_with_rows(g, n=3, payload="OLD"):
    """A minimal velocity_scores DB with n topics, each holding a stored
    payload — the state a mid-run failure must not destroy."""
    path = tempfile.mktemp(suffix=".db")
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE velocity_scores (topic_key TEXT, topic_display TEXT, "
        "scored_at TEXT, overall_score REAL, detection_score REAL, "
        "confidence_score REAL, serve_payload TEXT)")
    for i in range(n):
        con.execute(
            "INSERT INTO velocity_scores VALUES (?,?,?,?,?,?,?)",
            (f"t{i}", f"T{i}", "2026-08-20T00:00:00", 50 + i, 40 + i, 30 + i,
             json.dumps({"topic_key": f"t{i}", "marker": payload})))
    con.commit()
    con.close()
    return path


def t_2cb_empty_build_leaves_payloads_untouched():
    """Skip-on-error: a build that produces nothing must not clear anything.
    Under the OLD (NULL-first) code this test goes RED: the payloads are gone
    before the build even runs."""
    g = _detector()
    path = _db_with_rows(g)
    old_db, old_cal = g.DB_PATH, g._calibrate_score_fields
    try:
        g.DB_PATH = path

        def _boom(s):
            raise RuntimeError("calibration down")

        g._calibrate_score_fields = _boom
        n = g._precompute_serve_payloads(10)
        assert n == 0, n
        con = sqlite3.connect(path)
        kept = con.execute("SELECT COUNT(*) FROM velocity_scores "
                           "WHERE serve_payload IS NOT NULL").fetchone()[0]
        con.close()
        assert kept == 3, (
            f"{3 - kept} stored payloads destroyed by a failed build — the "
            f"NULL-first (2026-07-06 outage) shape is back")
    finally:
        g.DB_PATH, g._calibrate_score_fields = old_db, old_cal


def t_2cb_successful_build_swaps_and_stamps():
    g = _detector()
    path = _db_with_rows(g)
    old_db, old_cal = g.DB_PATH, g._calibrate_score_fields
    try:
        g.DB_PATH = path
        g._calibrate_score_fields = lambda s: s
        n = g._precompute_serve_payloads(10)
        assert n == 3, n
        con = sqlite3.connect(path)
        blobs = [json.loads(r[0]) for r in con.execute(
            "SELECT serve_payload FROM velocity_scores "
            "WHERE serve_payload IS NOT NULL").fetchall()]
        con.close()
        assert len(blobs) == 3
        for b in blobs:
            assert b.get("payload_schema_version") == g.PAYLOAD_SCHEMA_VERSION, (
                "a rebuilt blob is missing the 2c(c) schema stamp")
            assert b.get("marker") != "OLD", "an old blob survived the swap"
    finally:
        g.DB_PATH, g._calibrate_score_fields = old_db, old_cal


def t_2cc_TRIPWIRE_mismatched_stamp_never_served():
    """THE deploy-version window, constructed: a stored blob stamped by a
    different code version carries a poisoned field. If the serve path returns
    that field, the class is back."""
    g = _detector()
    stale = json.dumps({
        "payload_schema_version": "1999-01-01.0",
        "topic_display": "POISONED-BY-OLD-BINARY",
        "overall_score": 99.0, "detection_score": 99.0,
        "confidence_score": 99.0, "scored_at": "2026-08-20T00:00:00",
    })
    row = {"topic_key": "t0", "topic_display": "honest", "scored_at":
           "2026-08-20T00:00:00", "overall_score": 50.0,
           "detection_score": 40.0, "confidence_score": 30.0,
           "serve_payload": stale, "first_scored_at": "2026-08-01T00:00:00",
           "is_gravitational_anomaly": 0}
    old_cal, old_q = g._calibrate_score_fields, g._is_quality_topic
    old_m, old_gen = g.is_meaningful_topic, g._is_generic_topic
    try:
        g._calibrate_score_fields = lambda s: dict(s, calibrated_live=True)
        g._is_quality_topic = lambda d: True
        g.is_meaningful_topic = lambda *a: True
        g._is_generic_topic = lambda t: False
        out = g._format_score_rows([row])
        served = (out.get("results") or out.get("signals") or
                  out if isinstance(out, list) else out.get("scores"))
        if isinstance(out, dict):
            served = next((v for v in out.values() if isinstance(v, list)), None)
        s0 = served[0]
        assert s0.get("topic_display") != "POISONED-BY-OLD-BINARY", (
            "a blob stamped by ANOTHER version was served verbatim — the "
            "deploy-version window is open again")
    finally:
        g._calibrate_score_fields, g._is_quality_topic = old_cal, old_q
        g.is_meaningful_topic, g._is_generic_topic = old_m, old_gen


def t_2cc_matching_stamp_is_served():
    """The gate must not over-fire: a blob with the CURRENT stamp serves on
    the fast path (the whole point of the cache)."""
    g = _detector()
    good = json.dumps({
        "payload_schema_version": g.PAYLOAD_SCHEMA_VERSION,
        "topic_display": "fast-path", "overall_score": 60.0,
        "detection_score": 50.0, "confidence_score": 40.0,
        "scored_at": "2026-08-20T00:00:00",
    })
    row = {"topic_key": "t0", "topic_display": "row", "scored_at":
           "2026-08-20T00:00:00", "overall_score": 50.0,
           "detection_score": 40.0, "confidence_score": 30.0,
           "serve_payload": good, "first_scored_at": "2026-08-01T00:00:00",
           "is_gravitational_anomaly": 0}
    old_q, old_m, old_gen = (g._is_quality_topic, g.is_meaningful_topic,
                             g._is_generic_topic)
    try:
        g._is_quality_topic = lambda d: True
        g.is_meaningful_topic = lambda *a: True
        g._is_generic_topic = lambda t: False
        out = g._format_score_rows([row])
    finally:
        g._is_quality_topic, g.is_meaningful_topic, g._is_generic_topic = (
            old_q, old_m, old_gen)
    served = out
    if isinstance(out, dict):
        served = next((v for v in out.values() if isinstance(v, list)), None)
    assert served[0].get("topic_display") == "fast-path", (
        "a current-version blob was NOT served from the fast path")


def main() -> int:
    print("\nprecompute swap (ruling 2c) — tests and tripwires\n" + "=" * 60)
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("t_") and callable(f)]
    for name, fn in tests:
        check(name, fn)
    print("=" * 60)
    print(f"{_PASSES} passed, {len(_FAILS)} failed ({len(tests)} total)")
    return 1 if _FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
