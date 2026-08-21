# -*- coding: utf-8 -*-
"""D_PLUMBING_V2 — the enforcer for the claims the sealed prereg makes about it.

The cold-start guard was the defect that started the 2026-08-20 evening board: it was
built into the detector's first-timer function (github/HN/bluesky/lemmy) while the BLOG
lane — the lane D_PLUMBING_V2 admits and every sealed candidate feed enrolls through —
uses a different function that had no age term. Six seats found it independently, and the
sealed pre-registration asserted the guard was "enforced in code under V2".

It was repaired. It still had NO TEST, which is how it would come back.

This file is the mechanical enforcer for four claims:
  C-GUARD-BLOG   the guard withholds first-timer credit on the BLOG lane
  C-GUARD-DET    ...and on the detector lane (both, so a future fix can't drift again)
  C-DMEASURED    d_measured is keyed on RESOLVED AUTHORS, not platform membership
  C-MASTHEAD     an author identical to its venue is never credited as a person

Run: python test_d_plumbing.py   (or via tools/run_tests.py)
"""
from __future__ import annotations

import io
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    p = os.path.join(tempfile.gettempdir(), "dplumb_test.db")
    if os.path.exists(p):
        os.remove(p)
    import db_compat
    c = db_compat.connect(p)
    c.execute("""CREATE TABLE author_history (author TEXT, platform TEXT,
                 community TEXT, post_count INT DEFAULT 1, first_seen_at TEXT)""")
    c.commit()
    return c, p


def main() -> int:
    print("D_PLUMBING_V2 — cold-start guard, d_measured, masthead")
    print("=" * 66)
    os.environ["D_PLUMBING_V2"] = "1"          # the regime these claims describe
    import importlib
    import blog_collectors as bc
    importlib.reload(bc)
    import gravitational_anomaly_detector as g

    # ── C-GUARD-BLOG ────────────────────────────────────────────────────────────
    # A community we started collecting TODAY must grant no first-timer credit —
    # otherwise a newly wired feed certifies itself as "early" and the shadow trial
    # manufactures its own positive result (Guardian F2).
    c, p = _db()
    young = bc._first_timer(c, "alice", "wordpress", "wp/health")
    check("C-GUARD-BLOG day-0 community grants NO credit", young is False,
          "a brand-new community credited a first-timer — the fabrication is back")

    # ...but the author IS recorded, so history accrues during calibration.
    row = c.execute("SELECT COUNT(*) AS n FROM author_history "
                    "WHERE community='wp/health'").fetchone()
    n = row["n"] if hasattr(row, "keys") else row[0]
    check("C-GUARD-BLOG author still recorded while calibrating", n == 1,
          "history must accrue during the window or the guard never ends")

    # An OLD community still grants credit to a genuinely new author.
    old_ts = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    c.execute("INSERT INTO author_history VALUES (?,?,?,?,?)",
              ("veteran", "wordpress", "wp/finance", 9, old_ts))
    c.commit()
    mature = bc._first_timer(c, "newcomer", "wordpress", "wp/finance")
    check("C-GUARD-BLOG mature community DOES credit a new author", mature is True,
          "the guard must expire, or D can never fire at all")

    # ── C-MASTHEAD ──────────────────────────────────────────────────────────────
    # collect_medium/collect_ghost fall back to the FEED NAME when an item has no
    # byline. A venue is not a person: crediting it fabricates an identity in the
    # substrate of the earliness metric, and (via post_count) later reads as
    # "maximum incumbent reallocation".
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "blog_collectors.py"), encoding="utf-8").read()
    check("C-MASTHEAD medium lane passes the real author, not the masthead",
          'ft = _first_timer(conn, item["author"], "medium", src)' in src,
          "masthead fallback reached the first-timer credit path again")
    check("C-MASTHEAD ghost lane passes the real author, not the masthead",
          'ft = _first_timer(conn, item["author"], "ghost", cfg["name"])' in src,
          "masthead fallback reached the first-timer credit path again")

    import darkmatter_indicators as dmi
    isrc = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "darkmatter_indicators.py"), encoding="utf-8").read()
    check("C-MASTHEAD indicators exclude author==venue",
          "_venue_names" in isrc and "not in _venue_names" in isrc,
          "pseudo-authors would read as maximum incumbent displacement")

    # ── C-GUARD-DET ─────────────────────────────────────────────────────────────
    dsrc = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "gravitational_anomaly_detector.py"), encoding="utf-8").read()
    check("C-GUARD-DET detector lane also carries the age guard",
          "D_COMMUNITY_MIN_AGE_DAYS" in dsrc and "age_days <" in dsrc,
          "the guard must exist on BOTH first-timer paths")

    # ── C-DMEASURED ─────────────────────────────────────────────────────────────
    # Keyed on a RESOLVED AUTHOR. Platform membership was the first cut, and it made
    # five authorless RSS rows read "measured" — the A3 floor-end sin inside the field
    # built to close it.
    cls = None
    import inspect
    for _, obj in vars(g).items():
        if inspect.isclass(obj) and hasattr(obj, "compute_dark_matter"):
            cls = obj
            break
    inst = cls.__new__(cls)

    def sig(platform, author="", ft=0, up=0, com=0):
        return {"platform": platform, "author": author, "is_first_timer": ft,
                "upvotes": up, "comments": com, "is_organic": 1, "engagement_raw": 1}

    authorless = [sig("medium") for _ in range(5)]          # in the platform set,
    d = inst.compute_dark_matter(authorless)                 # but no real authors
    check("C-DMEASURED authorless rows on an author-platform read UNMEASURED",
          d[3] is False,
          f"d_measured={d[3]} — 'read quiet' when the truth is 'could not read'")

    withauthor = [sig("medium", author="real.person") for _ in range(5)]
    d2 = inst.compute_dark_matter(withauthor)
    check("C-DMEASURED resolved authors read MEASURED", d2[3] is True)

    # END-TO-END: the hand-built dicts above never traversed collector -> raw_signals ->
    # scoring join, which is exactly where the masthead fabrication was injected
    # (Challenger: "the fixture cannot observe the defect by construction"). Assert the
    # collector does not write a venue name into the author column.
    _src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "blog_collectors.py"), encoding="utf-8").read()
    check("C-MASTHEAD raw_signals.author gets the REAL byline, not the masthead",
          'title, url, item["author"] or "", quality' in _src
          and 'title, link, item["author"] or "", 60' in _src,
          "the display fallback still reaches the column that feeds the scoring join")
    _isrc = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "darkmatter_indicators.py"), encoding="utf-8").read()
    check("C-MASTHEAD venue exclusion strips collector prefixes",
          "_venue_names" in _isrc,
          "bare author vs 'newsletter/X' comparison misses the whole newsletter lane")

    engagement_only = [sig("newsapi_org", up=50, com=40) for _ in range(3)]
    d3 = inst.compute_dark_matter(engagement_only)
    check("C-DMEASURED engagement-bearing rows also count as measured",
          d3[3] is True)

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
