# -*- coding: utf-8 -*-
"""FIXTURE FOR THE PER-FEED ZERO-ROW TRIPWIRE — and a correction of the record.

`monitoring_agents.py` carried the comment "Verified on a fixture that fires
(test_feed_tripwire)". **That file did not exist.** The Challenger seat found it at the
2026-08-20 evening board while auditing exactly the class of claim the board had spent the
day naming: an integrity assertion written in prose with nothing mechanical behind it. The
verification HAD been run — inline, in a session, once — which is precisely the failure
mode, because an inline run proves nothing tomorrow.

This file makes the citation true. It is the tripwire's fixture-that-fires, per the
standing dead-control rule: a monitor that has never been shown to fire is unproven, and
a monitor whose proof cannot be re-run is unproven again the next day.

Run: python test_feed_tripwire.py      (or via tools/run_tests.py)
"""
from __future__ import annotations

import io
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db_compat                      # noqa: E402
import monitoring_agents as ma        # noqa: E402
import blog_collectors as bc          # noqa: E402

_passed, _failed = 0, 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        print(f"  FAIL  {name}  {detail}")


def _fixture_db():
    p = os.path.join(tempfile.gettempdir(), "tripwire_fixture.db")
    if os.path.exists(p):
        os.remove(p)
    c = db_compat.connect(p)
    c.execute("""CREATE TABLE raw_signals (
        id TEXT, collected_at TEXT, platform TEXT, platform_tier TEXT,
        source_name TEXT, title TEXT, url TEXT, author TEXT, upvotes INT,
        comments INT, engagement_raw REAL, sentiment REAL, is_first_timer INT,
        is_organic INT, raw_text TEXT)""")
    c.commit()
    return c, p


def _add_row(c, source_name: str, days_ago: float = 0.0) -> None:
    ts = (datetime.now(timezone.utc)
          - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%S")
    c.execute("INSERT INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              ("id" + str(abs(hash((source_name, ts))))[:8], ts, "medium", "niche",
               source_name, "t", "u", "a", 0, 0, 0.0, 0.0, 0, 1, "t"))
    c.commit()


def main() -> int:
    print("PER-FEED ZERO-ROW TRIPWIRE — fixture that fires")
    print("=" * 66)

    # t1 — THE CORE PROPERTY: it fires. A configured feed with no rows must alarm.
    c, p = _fixture_db()
    alerts = ma._feed_silence_tripwire(conn=c)
    check("t1 fires on an all-silent roster", len(alerts) > 0,
          "a tripwire that never fires is not a control")

    # t2 — a LIVE feed is exempt. (Guards against the opposite failure: an alarm that
    # fires on everything is equally useless — it trains the reader to ignore it.)
    _add_row(c, "newsletter/Guardian Football", days_ago=0)
    alerts = ma._feed_silence_tripwire(conn=c)
    names = {a["source"] for a in alerts}
    check("t2 live feed is exempt", "Guardian Football" not in names,
          f"Guardian Football wrongly flagged; flagged={sorted(names)[:4]}")
    check("t2b silent feeds still flagged", len(names) > 0)

    # t3 — PREFIX MATCHING. Stored names carry collector prefixes (newsletter/X,
    # blogger/X, X/latest); an exact-name comparison would flag every live feed. This is
    # the naming lesson from the 2026-08-20 source census.
    check("t3 matches through the 'newsletter/' stored prefix",
          "Guardian Football" not in names,
          "prefix matching regressed — exact-name compare would false-alarm")

    # t4 — THE WINDOW BINDS. A feed whose last row predates the silence window must
    # alarm; the tripwire is about RECENT delivery, not lifetime delivery. (The Batch had
    # zero rows EVER; Football365's URL was dead from onboarding — both invisible before
    # this control existed.)
    _add_row(c, "newsletter/ESPN Soccer", days_ago=ma._FEED_SILENCE_DAYS + 3)
    alerts = ma._feed_silence_tripwire(conn=c)
    names = {a["source"] for a in alerts}
    check("t4 stale-but-present feed still fires",
          "ESPN Soccer" in names,
          "a feed that stopped delivering must alarm even though rows exist")

    # t5 — ROSTER COVERAGE. The roster must include WORDPRESS_TAGS: the 12-domain
    # expansion of 2026-08-20 was the one lane the tripwire could not see, found by the
    # Buyer's Desk and Expansionist seats independently.
    feeds = ma._configured_feeds()
    wp = [f for f in feeds if f.startswith("wordpress/")]
    check("t5 roster covers WORDPRESS_TAGS",
          len(wp) >= len(getattr(bc, "WORDPRESS_TAGS", [])) and len(wp) > 0,
          f"wordpress lanes in roster: {len(wp)}, configured tags: "
          f"{len(getattr(bc, 'WORDPRESS_TAGS', []))}")
    check("t5b roster covers the newsletter + ghost feeds",
          any("Guardian Football" in f for f in feeds)
          and any("Gradient" in f or "Import AI" in f for f in feeds))

    # t6 — FAIL LOUD, NEVER SILENT. A broken tripwire must surface as an alert, not as
    # an empty list that reads identically to "everything is healthy".
    class _Boom:
        def execute(self, *a, **k):
            raise RuntimeError("simulated DB failure")
    try:
        out = ma.source_watchdog(conn=_Boom())
        msgs = " ".join(a.get("msg", "") for a in out.get("alerts", []))
        check("t6 a broken tripwire alarms rather than reading healthy",
              "tripwire errored" in msgs or out.get("status") in ("warn", "critical"),
              f"status={out.get('status')} msgs={msgs[:80]}")
    except Exception as e:                                     # noqa: BLE001
        check("t6 a broken tripwire alarms rather than reading healthy", False,
              f"raised instead of alerting: {e}")

    try:
        c.close()
        os.remove(p)
    except Exception:
        pass

    print("=" * 66)
    print(f"{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
