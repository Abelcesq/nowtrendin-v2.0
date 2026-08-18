"""Behavior tests for attention_index.py against register r1.

Run:  python test_attention_index.py
"""
import json
import os
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import attention_index as ai  # noqa: E402
import pit_store              # noqa: E402

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def fresh_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.unlink(path)
    pit_store._init_done = False
    c = sqlite3.connect(path)
    c.execute("CREATE TABLE velocity_scores (id TEXT PRIMARY KEY, "
              "scored_at TEXT, topic_key TEXT, detection_score REAL)")
    c.commit()
    c.close()
    return path


def seed(db, topic, detection, hours_ago, rid=None):
    ts = (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat()
    c = sqlite3.connect(db)
    c.execute("INSERT INTO velocity_scores VALUES (?,?,?,?)",
              (rid or f"{topic}-{hours_ago}", ts, topic, detection))
    c.commit()
    c.close()


def t1_basic_value_and_embargo():
    print("t1: value = mean of top-N ELIGIBLE detection; embargo excludes new topics")
    db = fresh_db()
    # 12 embargo-passing topics (old row + fresh row), detections 10..120
    for i in range(12):
        seed(db, f"old{i}", 10.0 * (i + 1), hours_ago=2, rid=f"o{i}-new")
        seed(db, f"old{i}", 5.0, hours_ago=60, rid=f"o{i}-old")
    # 1 brand-new topic with the HIGHEST detection — must be embargo-excluded
    seed(db, "brandnew", 99.9, hours_ago=1)
    r = ai.compute_and_record(db_path=db)
    expect = round(sum(10.0 * (i + 1) for i in range(12)) / 12, 2)
    check("value excludes embargoed topic", r["value"] == expect,
          f"got {r['value']} want {expect}")
    check("universe counts the new topic, eligible does not",
          r["universe_count"] == 13 and r["eligible_count"] == 12)
    c = sqlite3.connect(db)
    c.row_factory = sqlite3.Row
    row = c.execute("SELECT * FROM pit_observations WHERE kind='index_value'").fetchone()
    p = json.loads(row["payload"])
    check("sealed payload reproduces the value",
          round(sum(x["d"] for x in p["constituents"]) / len(p["constituents"]), 2)
          == p["value"])
    check("rules_version stamped", p["rules_version"] == ai.RULES_VERSION)
    c.close()


def t2_idempotent_one_per_day():
    print("t2: one value per UTC day (second run skips)")
    db = fresh_db()
    for i in range(12):
        seed(db, f"t{i}", 50.0, hours_ago=2, rid=f"t{i}-new")
        seed(db, f"t{i}", 5.0, hours_ago=60, rid=f"t{i}-old")
    r1 = ai.compute_and_record(db_path=db)
    r2 = ai.compute_and_record(db_path=db)
    check("first run records", r1.get("recorded"))
    check("second run skips", "skipped" in r2)
    c = sqlite3.connect(db)
    n = c.execute("SELECT COUNT(*) FROM pit_observations "
                  "WHERE kind='index_value'").fetchone()[0]
    check("exactly one sealed row", n == 1)
    c.close()


def t3_absent_on_thin_universe():
    print("t3: eligible < MIN_ELIGIBLE -> honest ABSENT, never fabricated")
    db = fresh_db()
    for i in range(3):
        seed(db, f"few{i}", 80.0, hours_ago=2, rid=f"f{i}-new")
        seed(db, f"few{i}", 5.0, hours_ago=60, rid=f"f{i}-old")
    r = ai.compute_and_record(db_path=db)
    check("value is None + absent", r.get("value") is None and r.get("absent"))
    c = sqlite3.connect(db)
    c.row_factory = sqlite3.Row
    row = c.execute("SELECT payload FROM pit_observations "
                    "WHERE kind='index_value'").fetchone()
    p = json.loads(row["payload"])
    check("absent day still sealed with reason",
          p["absent"] and "eligible universe" in p["reason"])
    c.close()


def t4_topn_and_ties():
    print("t4: top-N cut + deterministic tie-break by topic_key")
    db = fresh_db()
    # 60 eligible topics: 55 at detection 40.0 (ties), 5 at 90.0
    for i in range(60):
        d = 90.0 if i < 5 else 40.0
        seed(db, f"z{i:02d}", d, hours_ago=2, rid=f"z{i}-new")
        seed(db, f"z{i:02d}", 5.0, hours_ago=60, rid=f"z{i}-old")
    r = ai.compute_and_record(db_path=db)
    check("exactly TOP_N constituents", r["n_constituents"] == ai.TOP_N)
    expect = round((5 * 90.0 + 45 * 40.0) / 50, 2)
    check("value over the top-50", r["value"] == expect,
          f"got {r['value']} want {expect}")
    c = sqlite3.connect(db)
    c.row_factory = sqlite3.Row
    p = json.loads(c.execute("SELECT payload FROM pit_observations "
                             "WHERE kind='index_value'").fetchone()["payload"])
    tied = [x["k"] for x in p["constituents"] if x["d"] == 40.0]
    check("ties resolved topic_key-ascending (deterministic)",
          tied == sorted(tied))
    c.close()


def t5_latest_row_per_topic():
    print("t5: a topic's LATEST row in the window is its reading")
    db = fresh_db()
    for i in range(11):
        seed(db, f"s{i}", 30.0, hours_ago=2, rid=f"s{i}-new")
        seed(db, f"s{i}", 5.0, hours_ago=60, rid=f"s{i}-old")
    # topic s0 has an older-in-window row at 90 and a newer one at 10
    seed(db, "s0", 90.0, hours_ago=10, rid="s0-mid")
    seed(db, "s0", 10.0, hours_ago=1, rid="s0-latest")
    r = ai.compute_and_record(db_path=db)
    c = sqlite3.connect(db)
    c.row_factory = sqlite3.Row
    p = json.loads(c.execute("SELECT payload FROM pit_observations "
                             "WHERE kind='index_value'").fetchone()["payload"])
    s0 = [x for x in p["constituents"] if x["k"] == "s0"]
    check("latest row wins (10.0, not 90.0 or 30.0)",
          s0 and s0[0]["d"] == 10.0, str(s0))
    c.close()


if __name__ == "__main__":
    t1_basic_value_and_embargo()
    t2_idempotent_one_per_day()
    t3_absent_on_thin_universe()
    t4_topn_and_ties()
    t5_latest_row_per_topic()
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)
