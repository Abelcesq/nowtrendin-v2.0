"""
test_etf_reconcile_a2.py — COMMITTED regression harness for reconciliation AMENDMENT A2
(Chairman-ruled 2026-08-05 PT; spec CRYPTO_FLOW_SPEC_A2_AMENDMENT_2026-08-05.md, 51adb9d).

Proves, from the repo, with no network and no engine:
  1. t_of() settled-through mapping (evening ET / pre-dawn ET / weekend captures)
  2. interval PASS in band · direction FAIL · EMPTY_INTERVAL phantom flow
  3. NO_DERIVED — a frozen source reads as FAILURE, never silence (d#1)
  4. PENDING_FINAL on the still-moving newest interval
  5. the A2.3 splice rule — latest_delta refuses a delta across a src seam
  6. the first-pass A1.5 log is FROZEN — reconcile_a2 never writes it (d#2)

    python test_etf_reconcile_a2.py        (sqlite temp DB)
"""
import os
import tempfile
from datetime import date, timedelta

os.environ["GAD_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "a2test.db")

import etf_flow as EF                     # noqa: E402
import etf_flow_reconcile as REC          # noqa: E402
import db_compat                          # noqa: E402

EF.init_etf_db()
REC.init_reconcile_db()                   # the frozen A1.5 table (must stay empty)
REC.init_reconcile_db2()

PASSED = []


def ok(name, cond, detail=""):
    assert cond, f"FAIL {name}: {detail}"
    PASSED.append(name)
    print(f"  ok {name}")


def _conn():
    return db_compat.connect(os.environ["GAD_DB_PATH"])


def _wipe():
    c = _conn()
    for t in ("etf_share_snapshots", "etf_share_observations",
              "etf_reconcile_log2", "etf_reconcile_log"):
        c.execute(f"DELETE FROM {t}")
    c.commit()
    c.close()


def _strike(tkr, e_date, shares, aum, nav, src=None):
    """One strike whose capture is 20:00 ET on trading day e_date → T = prev bday."""
    cap = f"{e_date.isoformat()}T20:00:00-04:00"
    c = _conn()
    c.execute("INSERT INTO etf_share_snapshots "
              "(ticker,snapshot_date,shares,aum,nav,captured_at,src) "
              "VALUES (?,?,?,?,?,?,?)",
              (tkr, e_date.isoformat(), shares, aum, nav, cap, src))
    c.commit()
    c.close()


# trading-day ladder ending at today's settled-through date
T0 = REC._prev_bday(REC._last_bday(date.today()))
TD = [T0]
while len(TD) < 12:
    TD.append(REC._prev_bday(TD[-1]))     # TD[i] = i trading days before T0


def t1_t_of_mapping():
    t = REC.t_of("2026-08-05T20:00:00-04:00")            # Wed evening ET
    ok("t_of evening", t == date(2026, 8, 4), t)
    t = REC.t_of("2026-08-06T01:00:00-04:00")            # Thu pre-dawn ET → Wed book
    ok("t_of pre-dawn", t == date(2026, 8, 4), t)
    t = REC.t_of("2026-08-01T18:00:00-04:00")            # Saturday → Friday book
    ok("t_of weekend", t == date(2026, 7, 30), t)


def _stub_published():
    by = {}
    for d in TD[:11]:
        by[d.isoformat()] = {"IBIT": 0.0, "FBTC": 0.0, "BITB": 0.0}
    by[TD[7].isoformat()].update({"IBIT": 50e6, "FBTC": 60e6, "BITB": 0.0})
    by[TD[3].isoformat()]["HODL"] = 80e6
    return {"available": True, "source": "farside", "url": "stub",
            "by_date": by, "days": len(by)}


def t2_full_pass():
    _wipe()
    # IBIT: interval covering TD[7] derived +48M vs published +50M → PASS; then a
    # newest tiny pair → PENDING_FINAL.
    _strike("IBIT", TD[7], 1_000_000_000, 18e9, 40.0)
    _strike("IBIT", TD[6], 1_001_200_000, 18e9, 40.1)    # Δ +1.2M sh ≈ +$48.1M
    _strike("IBIT", TD[1], 1_001_225_000, 18e9, 40.2)
    # FBTC: derived −55M vs published +60M → direction FAIL; newest pair pending.
    _strike("FBTC", TD[7], 500_000_000, 19e9, 44.0)
    _strike("FBTC", TD[6], 498_750_000, 19e9, 44.1)      # Δ −1.25M sh ≈ −$55.1M
    _strike("FBTC", TD[1], 498_760_000, 19e9, 44.2)
    # BITB: derived +30M while the issuer published a measured-quiet 0.0 → phantom
    # flow (EMPTY_INTERVAL fails).
    _strike("BITB", TD[7], 100_000_000, 4e9, 40.0)
    _strike("BITB", TD[6], 100_750_000, 4e9, 40.1)       # Δ +0.75M sh ≈ +$30.1M
    _strike("BITB", TD[1], 100_751_000, 4e9, 40.2)
    # HODL: frozen after one early pair; the +$80M published day at TD[3] has NO
    # derived coverage → NO_DERIVED.
    _strike("HODL", TD[9], 58_000_000, 1e9, 17.8)
    _strike("HODL", TD[8], 58_001_000, 1e9, 17.9)

    real_fetch = REC.fetch_published
    REC.fetch_published = lambda coin, source="farside": (
        _stub_published() if coin == "BTC" else
        {"available": False, "reason": "no_comparator"})
    try:
        s = REC.reconcile_a2(coins={"BTC"})
    finally:
        REC.fetch_published = real_fetch

    ok("summary pass", s["pass"] == 1, s)
    ok("summary fail", s["fail"] == 1, s)
    ok("summary phantom", s["empty_interval"] == 1, s)
    ok("summary no_derived", s["no_derived"] == 1, s)
    ok("summary pending", s["pending_final"] >= 3, s)

    c = _conn()
    rows = {(r[0], r[1]): r[2] for r in c.execute(
        "SELECT ticker, interval_end_date, verdict FROM etf_reconcile_log2").fetchall()}
    va = {r[0]: r[1] for r in c.execute(
        "SELECT ticker, verdict_at FROM etf_reconcile_log2 "
        "WHERE verdict='PASS'").fetchall()}
    old_count = c.execute("SELECT COUNT(*) FROM etf_reconcile_log").fetchone()[0]
    c.close()
    ok("IBIT PASS row", rows.get(("IBIT", TD[7].isoformat())) == "PASS", rows)
    ok("FBTC FAIL row", rows.get(("FBTC", TD[7].isoformat())) == "FAIL", rows)
    ok("BITB phantom row", rows.get(("BITB", TD[7].isoformat())) == "EMPTY_INTERVAL",
       rows)
    ok("HODL NO_DERIVED row", rows.get(("HODL", TD[3].isoformat())) == "NO_DERIVED",
       rows)
    ok("verdict_at stamped", all(v for v in va.values()), va)
    ok("first-pass log frozen", old_count == 0, old_count)     # d#2: never written

    rep = REC.report_a2(days=30)
    ok("gate FAIL", rep["gate_status"] == "FAIL", rep["gate_status"])
    ok("material=2", rep["material_comparisons"] == 2, rep["material_comparisons"])
    ok("fmp fails counted", rep["open_failures_fmp"] == 2, rep["open_failures_fmp"])
    ok("re-arm not ready", rep["re_arm"]["ready"] is False and
       rep["re_arm"]["pass_comparisons"] == 0, rep["re_arm"])


def t3_splice_rule():
    _wipe()
    _strike("IBIT", TD[3], 1_000_000_000, 18e9, 40.0, src="fmp")
    _strike("IBIT", TD[2], 1_010_000_000, 18e9, 40.1, src="issuer_ishares")
    d = EF.latest_delta("IBIT")
    ok("splice refused", d.get("available") is False and d.get("splice") is True, d)


def t4_no_derived_era_attribution():
    """2026-08-08 source-swap defect: NO_DERIVED days must be blamed on the source
    whose ERA covered them, never on the latest src — otherwise the new issuer
    source inherits every FMP-era uncovered day at takeover (open_bad pollution
    that permanently blocks re-arm, violating A2.4's 'no FMP-era row counts')."""
    _wipe()
    # FMP era: two early strikes, then frozen (leaves TD[5] uncovered).
    _strike("IBIT", TD[9], 58_000_000, 1e9, 17.8, src="fmp")
    _strike("IBIT", TD[8], 58_001_000, 1e9, 17.9, src="fmp")
    # Issuer era: takeover with strikes at TD[2]/TD[1]; era starts at
    # T(first issuer strike) = TD[3] — days ≤ TD[3] stay FMP-era.
    _strike("IBIT", TD[2], 60_000_000, 1e9, 18.0, src="issuer_ishares")
    _strike("IBIT", TD[1], 60_010_000, 1e9, 18.1, src="issuer_ishares")

    by = {d.isoformat(): {"IBIT": 0.0} for d in TD[:11]}
    by[TD[5].isoformat()]["IBIT"] = 80e6      # FMP-era uncovered material day
    by[TD[3].isoformat()]["IBIT"] = 70e6      # boundary day = issuer baseline
    stub = {"available": True, "source": "farside", "url": "stub",
            "by_date": by, "days": len(by)}
    real_fetch = REC.fetch_published
    REC.fetch_published = lambda coin, source="farside": (
        stub if coin == "BTC" else {"available": False, "reason": "no_comparator"})
    try:
        REC.reconcile_a2(coins={"BTC"})
    finally:
        REC.fetch_published = real_fetch

    c = _conn()
    nd = {r[0]: r[1] for r in c.execute(
        "SELECT interval_end_date, src FROM etf_reconcile_log2 "
        "WHERE ticker='IBIT' AND verdict='NO_DERIVED'").fetchall()}
    c.close()
    ok("fmp-era day blamed on fmp", nd.get(TD[5].isoformat()) == "fmp", nd)
    ok("boundary day stays prior era", nd.get(TD[3].isoformat()) == "fmp", nd)
    rep = REC.report_a2(days=30)
    ok("re-arm open_bad clean of fmp-era days",
       rep["re_arm"]["open_bad"] == 0, rep["re_arm"])


if __name__ == "__main__":
    print("=== A2 reconciliation regression harness ===")
    t1_t_of_mapping()
    t2_full_pass()
    t3_splice_rule()
    t4_no_derived_era_attribution()
    print(f"\nALL {len(PASSED)} CHECKS PASSED")
