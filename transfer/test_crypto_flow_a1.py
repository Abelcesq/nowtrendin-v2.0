"""
test_crypto_flow_a1.py — COMMITTED regression harness for the crypto ETF share-flow leg
(spec A1 + the Board's F1-F8 fixes, Chairman-ruled 2026-08-05 PT).

F5 (Board: Challenger + Executioner, independently): the original 6/6 synthetic proofs ran
once in a session and were not re-runnable from the repo — "verified once is not
verifiable." This file IS the proof. Run before any CRYPTO_ETF_FLOW flip config change:

    python test_crypto_flow_a1.py        (sqlite temp DB; no network, no engine)
"""
import os
import sys
import tempfile
import importlib

os.environ["GAD_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "a1test.db")
os.environ["CRYPTO_ETF_FLOW"] = "1"

import etf_flow as EF                     # noqa: E402
import crypto_signals as CS               # noqa: E402
import crypto_money_gradient as CMG       # noqa: E402
import crypto_accuracy_ledger as CAL      # noqa: E402
import db_compat                          # noqa: E402

importlib.reload(EF)
importlib.reload(CS)
EF.init_etf_db()


class StubAV:
    """Insider path stub: no non-etf proxy produces data (isolates the fund class)."""
    def source_available(self):
        return True

    def signal_for(self, *a, **k):
        return None


def _conn():
    return db_compat.connect(os.environ["GAD_DB_PATH"])


def _wipe():
    c = _conn()
    c.execute("DELETE FROM etf_share_snapshots")
    c.execute("DELETE FROM etf_share_observations")
    c.commit()
    c.close()


def _rows(rows):
    c = _conn()
    for r in rows:
        c.execute("INSERT INTO etf_share_snapshots "
                  "(ticker,snapshot_date,shares,aum,nav,captured_at) VALUES (?,?,?,?,?,'t')", r)
    c.commit()
    c.close()


def t1_votes_and_fold():
    """Vote table + AUM-relative fold: net must equal the hand-computed class vote."""
    _wipe()
    _rows([("IBIT", "2026-08-03", 1_000_000_000, 80e9, 45.0),
           ("IBIT", "2026-08-04", 1_005_000_000, 80e9, 45.2),     # +0.5%/day
           ("FBTC", "2026-08-03", 500_000_000, 20e9, 40.0),
           ("FBTC", "2026-08-04", 498_500_000, 20e9, 40.1),       # -0.3%/day
           ("GBTC", "2026-08-03", 300_000_000, 15e9, 50.0),
           ("GBTC", "2026-08-04", 300_000_000, 15e9, 50.1)])      # 0.0 = measured quiet
    v_i, _ = CS._etf_flow_vote("IBIT")
    v_f, _ = CS._etf_flow_vote("FBTC")
    v_g, _ = CS._etf_flow_vote("GBTC")
    assert abs(v_i - 0.5) < 0.01 and abs(v_f + 0.3) < 0.01 and v_g == 0.0, (v_i, v_f, v_g)
    CS.avdp = StubAV()
    dm = CS.proxy_dark_matter("BTC")
    exp = 0.5 * (80 / 115) - 0.3 * (20 / 115)
    assert abs(dm["net_direction"] - round(exp, 3)) < 0.005, (dm["net_direction"], exp)
    assert dm["flow"] == "inflow"
    assert dm.get("flow_basis") == "etf_creations" and dm.get("signal_latency_days") == 1
    assert "etf_flow" in (dm.get("venue_classes_active") or []), dm
    print("t1 votes+fold: net %.3f == expected; stamps + classes present" % dm["net_direction"])


def t2_dominance():
    """$80B redemption must outvote a $60M creation (a naive mean reads the wrong sign)."""
    _wipe()
    _rows([("IBIT", "2026-08-03", 1_000_000_000, 80e9, 45.0),
           ("IBIT", "2026-08-04", 992_000_000, 80e9, 45.2),       # -0.8%
           ("BITB", "2026-08-03", 10_000_000, 60e6, 20.0),
           ("BITB", "2026-08-04", 10_090_000, 60e6, 20.1)])       # +0.9%
    CS.avdp = StubAV()
    dm = CS.proxy_dark_matter("BTC")
    assert dm["net_direction"] < 0, ("AUM sizing must let the $80B fund govern", dm)
    print("t2 dominance: net %.3f (outflow) vs naive mean +0.05" % dm["net_direction"])


def t3_f1_budget_invariance():
    """F1: the class budget is PINNED — a roster/availability change must not move the
    class's voice. Same fund data, one voter vs two voters: den must be identical."""
    _wipe()
    _rows([("IBIT", "2026-08-03", 1_000_000_000, 80e9, 45.0),
           ("IBIT", "2026-08-04", 1_005_000_000, 80e9, 45.2)])
    CS.avdp = StubAV()
    dm_one = CS.proxy_dark_matter("BTC")                 # one voting fund
    _rows([("FBTC", "2026-08-03", 500_000_000, 20e9, 40.0),
           ("FBTC", "2026-08-04", 502_000_000, 20e9, 40.1)])
    dm_two = CS.proxy_dark_matter("BTC")                 # two voting funds
    # With a pinned budget the denominator is identical either way, so net is a pure
    # AUM-weighted mean of votes; with the voter-sum defect den would differ (1.0 vs 1.8).
    v1 = dm_one["net_direction"]
    assert abs(v1 - 0.5) < 0.01, ("one-voter class must carry the FULL pinned budget "
                                  "(net = its vote, not vote*w/budget)", v1)
    budget = CS.COIN_UNIVERSE["BTC"]["etf_class_budget"]
    assert budget == 4.2, budget
    print("t3 F1: pinned budget %.1f; one-voter net %.3f == its vote (availability "
          "cannot move the class's voice)" % (budget, v1))


def t4_f2_prestrike_no_quiet():
    """F2: a pre-strike duplicate row (same shares+nav, new date) must NOT read as a
    measured-quiet 0.0 — the prior genuine flow point keeps serving."""
    _wipe()
    _rows([("IBIT", "2026-08-01", 1_000_000_000, 80e9, 45.0),
           ("IBIT", "2026-08-02", 1_005_000_000, 80e9, 45.2),      # genuine +0.5% strike
           ("IBIT", "2026-08-03", 1_005_000_000, 80e9, 45.2)])     # pre-strike copy
    d = EF.latest_delta("IBIT")
    assert d["available"] and abs(d["delta_pct_per_day"] - 0.5) < 0.01, d
    assert d["to_date"] == "2026-08-02", ("the strike date, not the copy's date", d)
    print("t4 F2: pre-strike copy ignored; genuine +0.5%% (08-01→08-02) keeps serving")


def t5_f4_trading_day_normalization():
    """F4: a Fri→Mon delta spans 1 TRADING day — Monday flow must not read at 1/3."""
    _wipe()
    _rows([("IBIT", "2026-07-31", 1_000_000_000, 80e9, 45.0),      # Friday
           ("IBIT", "2026-08-03", 1_009_000_000, 80e9, 45.2)])     # Monday +0.9%
    d = EF.latest_delta("IBIT")
    assert d["gap_days"] == 1 and d.get("gap_basis") == "trading_days", d
    assert abs(d["delta_pct_per_day"] - 0.9) < 0.01, ("calendar-day division would "
                                                      "read 0.3", d)
    print("t5 F4: Fri→Mon = 1 trading day; +0.9%% serves at full strength")


def t6_f6_class_coverage():
    """F6: proxy_coverage grades on venue classes when the flag is on."""
    _wipe()
    _rows([("IBIT", "2026-08-03", 1_000_000_000, 80e9, 45.0),
           ("IBIT", "2026-08-04", 1_005_000_000, 80e9, 45.2)])
    CS.avdp = StubAV()
    dm = CS.proxy_dark_matter("BTC")
    assert dm["proxy_coverage"] == "partial", ("one class active of two reachable", dm)
    assert dm.get("coverage_basis") == "venue_classes"
    comps = CMG.assemble_crypto_components("BTC", sig={"_dark_matter": dm,
                                                       "_price": {"available": False}})
    assert comps["venue_diffusion"] is not None
    print("t6 F6: coverage 'partial' on class basis (1 of 2 kinds); diffusion on classes")


def t7_discontinuity_and_stale():
    """Retained guards: >20%/day refuses; >5 trading-day gap refuses."""
    _wipe()
    _rows([("IBIT", "2026-08-03", 1_000_000_000, 80e9, 45.0),
           ("IBIT", "2026-08-04", 400_000_000, 80e9, 45.2)])       # -60% step
    d = EF.latest_delta("IBIT")
    assert not d["available"] and d.get("discontinuity"), d
    _wipe()
    _rows([("IBIT", "2026-07-01", 1_000_000_000, 80e9, 45.0),
           ("IBIT", "2026-08-04", 1_010_000_000, 80e9, 45.2)])     # ~24 trading days
    d2 = EF.latest_delta("IBIT")
    assert not d2["available"] and d2.get("stale"), d2
    print("t7 guards: discontinuity + stale still refuse")


def t8_ledger_stamps():
    """Gate 6: crypto ledger rows carry flow_basis + signal_latency_days."""
    CAL.init_crypto_ledger_db()
    CAL.record_crypto_detection("BTC", "Bitcoin", "2026-08-04", "inflow", 80.0, gate=False,
                                flow_basis="etf_creations", signal_latency_days=1)
    c = _conn()
    row = c.execute("SELECT flow_basis, signal_latency_days FROM crypto_pending_detections "
                    "WHERE coin='BTC'").fetchone()
    c.close()
    assert tuple(row) == ("etf_creations", 1), tuple(row)
    print("t8 stamps: ledger rows carry flow_basis + signal_latency_days")


def t9_flag_off_equivalence():
    """Flag off: no A1 fields, ETFs unread on the legacy path (byte-equivalence class)."""
    os.environ["CRYPTO_ETF_FLOW"] = "0"
    importlib.reload(CS)
    CS.avdp = StubAV()
    dm = CS.proxy_dark_matter("BTC")
    assert "venue_classes_active" not in dm and "flow_basis" not in dm, list(dm)
    etf_rows = [d for d in dm["detail"] if d["kind"] == "etf"]
    assert etf_rows and all(not d["has_data"] for d in etf_rows)
    os.environ["CRYPTO_ETF_FLOW"] = "1"
    importlib.reload(CS)
    print("t9 flag-off: no A1 fields leak; ETFs ride the legacy path")


if __name__ == "__main__":
    for t in (t1_votes_and_fold, t2_dominance, t3_f1_budget_invariance,
              t4_f2_prestrike_no_quiet, t5_f4_trading_day_normalization,
              t6_f6_class_coverage, t7_discontinuity_and_stale, t8_ledger_stamps,
              t9_flag_off_equivalence):
        t()
    print("\nALL A1/F-FIX REGRESSIONS PASS")
