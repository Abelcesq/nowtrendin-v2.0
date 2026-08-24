"""test_payload_probe.py — ruling 7 behaviour tests + tripwires.

The census must SEE a stored contradiction; the probe must FAIL when the serve
formatter violates the invariant (negative control via an injected violating
formatter — the probe is not allowed to be a green light wired to nothing);
and a passing probe must leave a DATED row carrying release + schema, because
a green observation decays (~8h half-life) and readers demote on age/release.

Run:  python3 test_payload_probe.py
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


def _db(blobs):
    path = tempfile.mktemp(suffix=".db")
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE velocity_scores (topic_key TEXT, serve_payload TEXT)")
    for tk, blob in blobs:
        con.execute("INSERT INTO velocity_scores VALUES (?,?)",
                    (tk, json.dumps(blob) if blob is not None else None))
    con.commit()
    return con


def _agent():
    import monitoring_agents as ma
    return ma


def t_census_TRIPWIRE_sees_stored_contradiction():
    """A blob with numeric first_timer_ratio beside d_measured NULL is the
    incident substrate. If the census reports 0 on it, the census is blind."""
    ma = _agent()
    import gravitational_anomaly_detector as g
    con = _db([
        ("bad", {"d_measured": None, "first_timer_ratio": 0.4,
                 "payload_schema_version": g.PAYLOAD_SCHEMA_VERSION}),
        ("ok", {"d_measured": 1, "first_timer_ratio": 0.2,
                "payload_schema_version": g.PAYLOAD_SCHEMA_VERSION}),
    ])
    out = ma.payload_contradiction_auditor(con, fmt=lambda rows: {"results": []},
                                           write_probe=False)
    assert out["summary"]["payload_contradictions_stored"] == 1, out["summary"]
    assert any("first_timer_ratio" in a["msg"] for a in out["alerts"])


def t_census_counts_foreign_schema_blobs():
    ma = _agent()
    con = _db([("old", {"d_measured": 1, "payload_schema_version": "1999-01-01.0"})])
    out = ma.payload_contradiction_auditor(con, fmt=lambda rows: {"results": []},
                                           write_probe=False)
    assert out["summary"]["payload_foreign_schema"] == 1, out["summary"]


def t_probe_TRIPWIRE_fails_on_violating_formatter():
    """Negative control on the control: a formatter that serves the ratio on an
    unmeasured row MUST turn the probe red. If this passes green, the probe is
    decoration."""
    ma = _agent()
    con = _db([])

    def violating_fmt(rows):
        # serve everything verbatim — the pre-4c behavior
        return {"results": [dict(r) for r in rows]}

    out = ma.payload_contradiction_auditor(con, fmt=violating_fmt,
                                           write_probe=False)
    assert out["summary"]["probe_passed"] is False, (
        "the probe stayed green against a formatter serving numeric ratios on "
        "unmeasured rows — a green light wired to nothing")
    assert out["status"] == "critical", out["status"]


def t_probe_passes_and_writes_dated_row():
    """Against a compliant formatter the probe passes AND leaves the dated
    pass/fail row with release + schema — the demotion metadata."""
    ma = _agent()
    con = _db([])

    def compliant_fmt(rows):
        served = []
        for r in rows:
            s = dict(r)
            if s.get("d_measured") in (1, True):
                s["d_measured"] = True
            else:
                s["first_timer_ratio"] = None
            served.append(s)
        return {"results": served}

    out = ma.payload_contradiction_auditor(con, fmt=compliant_fmt,
                                           write_probe=True)
    assert out["summary"]["probe_passed"] is True, out["summary"]["probe_failures"]
    assert out["summary"]["probe_stale_h"] == 48
    row = con.execute("SELECT probe_at, engine_release, payload_schema, passed "
                      "FROM payload_invariant_probes").fetchone()
    assert row is not None and row["passed"] == 1, "no dated probe row written"
    assert row["probe_at"], "probe row carries no date — undated observations decay invisibly"


def main() -> int:
    print("\npayload contradiction auditor (ruling 7) — tests and tripwires\n" + "=" * 60)
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("t_") and callable(f)]
    for name, fn in tests:
        check(name, fn)
    print("=" * 60)
    print(f"{_PASSES} passed, {len(_FAILS)} failed ({len(tests)} total)")
    return 1 if _FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
