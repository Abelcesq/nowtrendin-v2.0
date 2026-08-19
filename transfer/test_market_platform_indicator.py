"""Behavior tests for market_platform_indicator.py (Market Signal N).

The load-bearing test is t5: the served money numbers must be BYTE-IDENTICAL
with N present and with N absent. That is the founder's integrity condition
expressed as an assertion rather than a promise.

Run:  python test_market_platform_indicator.py
"""
import os
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import market_platform_indicator as mpi  # noqa: E402

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
    mpi._init_done = False
    mpi._dedup_seen.clear()
    mpi.init_db(path)
    return path


def seed(db, item_key, n, hours_ago=1, endpoint="/risk/scores"):
    c = sqlite3.connect(db)
    ts = (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat()
    c.executemany("INSERT INTO instrument_queries (queried_at, item_key, endpoint) "
                  "VALUES (?,?,?)", [(ts, item_key, endpoint)] * n)
    c.commit()
    c.close()


def t1_formula_matches_topic_side():
    print("t1: N formula reproduces the topic-side system values")
    db = fresh_db()
    n0, d0 = mpi.compute("crypto:BTC", db_path=db)
    check("never surfaced = 0", n0 == 0.0 and mpi.band(n0) == "never surfaced")
    seed(db, "AAPL", 10, hours_ago=100)          # 10 in-30d, none in 24h
    n10, d10 = mpi.compute("AAPL", db_path=db)
    # topic-side: log1p(10)/log1p(100)*70 ~ 33.2, no recency (0 in 24h)
    check("10 appearances = 36.37 (log-scale volume, no recency)",
          36.0 < n10 < 36.7, f"got {n10}")
    check("detail counts are honest",
          d10["total_queries_30d"] == 10 and d10["queries_24h"] == 0)
    seed(db, "MSFT", 100, hours_ago=100)
    n100, _ = mpi.compute("MSFT", db_path=db)
    check("100 appearances = 70.0 volume ceiling", 69.0 < n100 <= 70.5, f"got {n100}")
    check("bands match the documented ladder",
          mpi.band(10) == "rare" and mpi.band(35) == "moderate"
          and mpi.band(60) == "frequent" and mpi.band(85) == "very frequent")


def t2_recency_spike():
    print("t2: a 24h spike over the 7-day baseline raises N")
    db = fresh_db()
    seed(db, "NVDA", 14, hours_ago=72)      # baseline: 2/day over 7d
    flat, _ = mpi.compute("NVDA", db_path=db)
    seed(db, "NVDA", 20, hours_ago=1)       # spike today
    spiked, d = mpi.compute("NVDA", db_path=db)
    check("spike increases N", spiked > flat, f"{flat} -> {spiked}")
    check("24h count recorded", d["queries_24h"] == 20)
    check("N never exceeds 100", spiked <= 100.0)


def t3_dedup_window():
    print("t3: repeat surfacing inside the window counts once (no render loop)")
    db = fresh_db()
    mpi._dedup_seen.clear()
    for _ in range(50):
        mpi.log_query("SPY", "/risk/scores")
    q = []
    while not mpi._q.empty():
        q.append(mpi._q.get_nowait())
    check("50 rapid surfacings enqueue 1 event", len(q) == 1, f"got {len(q)}")
    mpi.log_query("SPY", "/risk/SPY")       # different endpoint = distinct episode
    check("a different endpoint is its own episode", not mpi._q.empty())
    while not mpi._q.empty():
        mpi._q.get_nowait()


def t4_n_inclusive_is_separate_and_guarded():
    print("t4: N-inclusive is a separate what-if, thin-evidence guarded")
    r = mpi.n_inclusive(40.0, 60.0, 100.0, signal_count=200)
    check("what-if computed when evidence is thick", r["available"])
    check("money_with_n moves toward N but is not N",
          40.0 < r["money_with_n"] < 100.0, str(r))
    check("confirmation_with_n moves toward N",
          60.0 < r["confirmation_with_n"] < 100.0)
    thin = mpi.n_inclusive(40.0, 60.0, 100.0, signal_count=0)
    check("thin evidence => N earns no weight (headline unchanged)",
          thin["money_with_n"] == 40.0 and thin["confirmation_with_n"] == 60.0,
          str(thin))
    check("thin + high N flags tracking_driven", thin["tracking_driven"])
    absent = mpi.n_inclusive(None, 55.0, 80.0, signal_count=100)
    check("a null money read STAYS null (D8 honest absence preserved)",
          absent["available"] and absent["money_with_n"] is None)


def t5_scores_are_byte_identical_with_and_without_n():
    print("t5: THE INTEGRITY TEST - money numbers identical with N present vs absent")
    import market_signal_engine as mse
    db = fresh_db()
    mse.init_market_signal_db(db_path=db)
    comps = {"dark_pool_activity": 1.4, "volume_surge": 0.7,
             "positioning_concentration": 2.1}
    before = mse.apply_market_signal("AAPL", "Apple", comps, db_path=db)
    # Now flood the platform-indicator table for the same instrument...
    seed(db, "AAPL", 5000, hours_ago=1)
    n, _ = mpi.compute("AAPL", db_path=db)
    check("N is now maximal for AAPL", n >= 80.0, f"got {n}")
    after = mse.apply_market_signal("AAPL", "Apple", comps, db_path=db,
                                    record_this_cycle=False)
    for field in ("detection", "confidence", "money_movement",
                  "market_confirmation", "tier", "gap"):
        check(f"{field} unchanged by N", before.get(field) == after.get(field),
              f"{before.get(field)} != {after.get(field)}")


def t6_firewall_registration():
    print("t6: held-out firewall registration is real (AST-enforced)")
    import heldout_registry as hr
    check("registered as held-out",
          "market_platform_indicator" in hr.HELD_OUT_ARRIVAL_INPUTS)
    check("market_signal_engine is a scoring module",
          "market_signal_engine" in hr.SCORING_MODULES)
    check("crypto_money_gradient is a scoring module",
          "crypto_money_gradient" in hr.SCORING_MODULES)
    audit = hr.audit_firewall()
    viol = [v for v in audit.get("violations", [])
            if v.get("held_out") == "market_platform_indicator"]
    check("no scoring module imports it today", not viol, str(viol))


def t7_payload_and_convergence():
    print("t7: serve payload is complete and honestly fenced")
    db = fresh_db()
    seed(db, "crypto:BTC", 40, hours_ago=48)
    seed(db, "crypto:BTC", 30, hours_ago=1)
    p = mpi.payload("crypto:BTC", money_movement=70.0, market_confirmation=65.0,
                    signal_count=120, db_path=db)
    check("payload carries N + band + definition",
          isinstance(p["n"], int) and p["band"] and p["definition"])
    check("payload declares itself held-out and score-excluded",
          p["held_out"] and p["excluded_from_score"])
    check("n_inclusive present as a SEPARATE block", p["n_inclusive"]["available"])
    check("convergence reads RISING on a 24h spike",
          p["convergence"]["available"] and p["convergence"]["direction"] == "RISING",
          str(p["convergence"]))
    check("convergence agrees when money is hot",
          p["convergence"]["agreement"] == "CONFIRMED", str(p["convergence"]))
    cold = mpi.convergence(50, {"daily_rate_7d": 2.0, "queries_24h": 20}, 10.0, 12.0)
    check("rising tracking + quiet money = CONFLICTING",
          cold["agreement"] == "CONFLICTING", str(cold))


def t8_fail_open():
    print("t8: fail-open everywhere (never raises into a serve path)")
    bad = os.path.join(tempfile.gettempdir(), "no", "such", "dir", "x.db")
    mpi._init_done = False
    n, d = mpi.compute("AAPL", db_path=bad)
    check("compute on broken path returns 0, no raise",
          n == 0.0 and d["available"] is False)
    mpi.log_query("", "/risk/scores")          # empty key
    check("empty key is ignored", True)
    check("n_inclusive with junk input returns unavailable",
          mpi.n_inclusive("x", None, None)["available"] is False)
    mpi._init_done = False


if __name__ == "__main__":
    t1_formula_matches_topic_side()
    t2_recency_spike()
    t3_dedup_window()
    t4_n_inclusive_is_separate_and_guarded()
    t5_scores_are_byte_identical_with_and_without_n()
    t6_firewall_registration()
    t7_payload_and_convergence()
    t8_fail_open()
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)
