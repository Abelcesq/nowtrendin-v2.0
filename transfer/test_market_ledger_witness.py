# -*- coding: utf-8 -*-
"""
Regression test — the at-detection WITNESS must never be fabricated (H7, board hardenings
review 2026-07-20). The market ledger's `detection_score` column is context only; when the
money-movement detection is absent it MUST store NULL, never a substituted intensity*100 (a
different quantity under the same column name — the corruption the D8 board flagged).

Run: python transfer/test_market_ledger_witness.py   (no pytest dependency)
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _fresh_db():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    return path


def run():
    import market_accuracy_ledger as m
    db = _fresh_db()
    try:
        m.init_market_ledger_db(db)
        # An enrollment with a REAL intensity but an ABSENT detection_score.
        m.record_market_detection("TESTX", "Test Instrument", "2026-07-01",
                                  "inflow", intensity=0.9, detection_score=None, db_path=db)
        conn = m._connect(db)
        row = conn.execute(
            "SELECT detection_score FROM market_pending_detections WHERE ticker='TESTX'"
        ).fetchone()
        conn.close()
        assert row is not None, "FAIL: row was not enrolled"
        ds = row["detection_score"] if hasattr(row, "keys") else row[0]
        assert ds is None, (
            f"FAIL: absent witness was fabricated — detection_score={ds!r} "
            f"(intensity*100 would be 90.0). It must be NULL.")
        # A REAL detection_score must be stored verbatim (no clobbering).
        m.record_market_detection("TESTY", "Test Instrument 2", "2026-07-01",
                                  "outflow", intensity=0.9, detection_score=44.5, db_path=db)
        conn = m._connect(db)
        row2 = conn.execute(
            "SELECT detection_score FROM market_pending_detections WHERE ticker='TESTY'"
        ).fetchone()
        conn.close()
        ds2 = row2["detection_score"] if hasattr(row2, "keys") else row2[0]
        assert ds2 == 44.5, f"FAIL: real witness altered — detection_score={ds2!r}, expected 44.5"
        print("PASS: absent witness stores NULL; real witness stored verbatim.")
        return 0
    finally:
        try:
            os.remove(db)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(run())
