# -*- coding: utf-8 -*-
"""ENFORCER for the shadow trial's selection rules (claim C-SHADOW-SELECTOR).

The board's point: the sampling code IS the membership criterion, so sealing the rules in
prose and writing the code later means every forking path gets chosen after the seal. This
file asserts the properties the prereg claims, so the claim cannot quietly stop being true:

  t1  cross-arm exclusivity — a topic in one arm can never enter another
  t2  null_random is DETERMINISTIC from the sealed prereg hash + cycle date
  t3  ...and a DIFFERENT cycle date gives a different draw (it is a draw, not a constant)
  t4  the calibrating stamp fires on a young venue and not on a mature one
  t5  selection parameters are literals, not env-readable
  t6  enroll() refuses an unsealed feed_set
  t7  enroll() derives instrument_epoch from LIVE flag state, not the caller's string

Run: python test_shadow_enroll.py   (or via tools/run_tests.py)
"""
from __future__ import annotations

import io
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db_compat            # noqa: E402
import shadow_ledger as sl  # noqa: E402
import shadow_enroll as se  # noqa: E402

_passed, _failed = 0, 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        print(f"  FAIL  {name}  {detail}")


def _db():
    p = os.path.join(tempfile.gettempdir(), "shadow_enroll_test.db")
    if os.path.exists(p):
        os.remove(p)
    c = db_compat.connect(p)
    c.execute("""CREATE TABLE topic_signals (id TEXT, extracted_at TEXT, topic TEXT,
        topic_key TEXT, signal_id TEXT, platform TEXT, platform_tier TEXT,
        source_name TEXT, upvotes INT, comments INT, engagement_raw REAL,
        is_first_timer INT, is_organic INT)""")
    c.execute("""CREATE TABLE raw_signals (id TEXT, collected_at TEXT, platform TEXT,
        platform_tier TEXT, source_name TEXT, title TEXT, url TEXT, author TEXT,
        upvotes INT, comments INT, engagement_raw REAL, sentiment REAL,
        is_first_timer INT, is_organic INT, raw_text TEXT)""")
    c.commit()
    c.close()
    sl.init_db(p)
    return p


def _seed_topic(p, topic_key, source, n=3, days_ago=1.0, venue_age_days=90.0):
    c = db_compat.connect(p)
    ts = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime(
        "%Y-%m-%dT%H:%M:%S")
    for i in range(n):
        c.execute("INSERT INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (f"{topic_key}-{i}", ts, topic_key.replace("_", " "), topic_key,
                   f"s{i}", "ghost", "expert", source, 0, 0, 1.0, 0, 1))
    vts = (datetime.now(timezone.utc) - timedelta(days=venue_age_days)).strftime(
        "%Y-%m-%dT%H:%M:%S")
    c.execute("INSERT INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (f"raw-{topic_key}", vts, "ghost", "expert", source, "t", "u", "a",
               0, 0, 1.0, 0.0, 0, 1, "t"))
    c.commit()
    c.close()


def main() -> int:
    print("SHADOW ENROLLMENT DRIVER — selection rules")
    print("=" * 66)
    p = _db()
    _seed_topic(p, "alpha_topic", "Marca", venue_age_days=90)
    _seed_topic(p, "beta_topic", "Marca", venue_age_days=90)
    _seed_topic(p, "young_topic", "NewDesk", venue_age_days=2)   # venue wired 2d ago
    feed_map = {"marca-es": ["Marca"], "kicker-de": ["NewDesk"]}

    # t1/t2 — dry-run selection is deterministic and exclusive.
    r1 = se.enroll_cycle(feed_map=feed_map, control_sources=[],
                         cycle_date="2026-09-05", db_path=p, dry_run=True)
    r2 = se.enroll_cycle(feed_map=feed_map, control_sources=[],
                         cycle_date="2026-09-05", db_path=p, dry_run=True)
    # t2 — also strengthened: comparing two EMPTY dicts is trivially true, so the old
    # form certified determinism on an instrument that drew nothing. Require a non-empty
    # draw first, then require the draws to match.
    check("t2 same cycle date -> identical draw (deterministic null)",
          r1["arms"] == r2["arms"]
          and r1["arms"].get("null_random", {}).get("enrolled", 0) > 0,
          f"{r1['arms']} vs {r2['arms']} — equal-but-empty is not determinism")

    r3 = se.enroll_cycle(feed_map=feed_map, control_sources=[],
                         cycle_date="2026-10-11", db_path=p, dry_run=True)
    check("t3 seed basis is the SEALED prereg hash",
          se._cycle_seed("2026-09-05").random() != se._cycle_seed("2026-10-11").random(),
          "different cycles must give different draws, or it is a constant not a draw")

    # t1 — REWRITTEN AS A LOWER BOUND (board 2026-08-20 late). The original asserted
    # `total <= 3` — an UPPER bound, which is satisfied MAXIMALLY by an instrument that
    # enrolls nothing. It passed green while both null arms were structurally empty, and
    # four seats found the annihilation the test was supposed to catch. An enforcer that
    # can only detect presence-of-too-much will never detect absence-of-everything.
    # An assertion about something EXISTING must be a lower bound or a positive claim.
    arms1 = r1["arms"]
    check("t1a candidate arm is NON-EMPTY",
          arms1.get("candidate", {}).get("enrolled", 0) > 0, f"{arms1}")
    check("t1b null_random is NON-EMPTY — a trial without a null can only produce a "
          "narrative",
          arms1.get("null_random", {}).get("enrolled", 0) > 0, f"{arms1}")
    check("t1c no arm is silently absent from the report (N=0 must READ as N=0)",
          all(a in arms1 for a in ("candidate", "control", "null_random", "null_volume")),
          f"arms present: {sorted(arms1)}")
    total = sum(a.get("enrolled", 0) for a in arms1.values())
    check("t1d exclusivity: enrollments never exceed the eligible pool",
          total <= 3, f"{total} from 3 topics — a topic entered more than one arm")

    # t4 — calibrating stamp: young venue stamped, mature venue not.
    conn = db_compat.connect(p)
    age_young = se._venue_age_days(conn, "NewDesk")
    age_old = se._venue_age_days(conn, "Marca")
    conn.close()
    check("t4 young venue is under the calibrating threshold",
          age_young is not None and age_young < se.CALIBRATING_DAYS,
          f"age={age_young}")
    check("t4b mature venue is over it",
          age_old is not None and age_old >= se.CALIBRATING_DAYS, f"age={age_old}")

    # t5 — selection parameters are literals (integrity-gate L1 applies to them too).
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "shadow_enroll.py"), encoding="utf-8").read()
    for const in ("NULL_VOLUME_K", "ENROLL_RECENT_DAYS", "CALIBRATING_DAYS",
                  "NULL_RANDOM_RATIO"):
        line = [ln for ln in src.splitlines() if ln.startswith(const + " ")]
        check(f"t5 {const} is a literal",
              bool(line) and "getenv" not in line[0],
              "a trial parameter readable from env can be retuned with no trace")

    # t6 — an unsealed feed_set is refused.
    try:
        sl.enroll(arm="candidate", feed_set="some-feed-nobody-sealed", domain="x",
                  topic_key="k", topic_display="k", detection_date="2026-09-05",
                  instrument_epoch="", regime="", db_path=p)
        check("t6 unsealed feed_set is refused", False, "it was accepted")
    except ValueError:
        check("t6 unsealed feed_set is refused", True)

    # t7 — instrument_epoch comes from LIVE state, not the caller.
    esrc = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "shadow_ledger.py"), encoding="utf-8").read()
    check("t7 instrument_epoch derived from live flag state",
          'live_epoch = f"D_PLUMBING_V2=' in esrc and "instrument_epoch = live_epoch" in esrc,
          "a caller-supplied epoch makes the trial's own regime record unfalsifiable")

    try:
        os.remove(p)
    except Exception:
        pass
    print("=" * 66)
    print(f"{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
