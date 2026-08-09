"""Unit regressions for etf_issuer_pages guards (board conditions, Chairman-approved
2026-08-09): identity check, page_asof staleness, unparseable-asof leniency, and the
pre-declared ETHA epoch stamp. Pure-function tests — no network, no DB."""
import os
import sys
from datetime import datetime, timedelta, timezone

os.environ.setdefault("GAD_DB_PATH", ":memory:")
import etf_issuer_pages as ip

PASSED = []


def ok(name, cond, detail=""):
    if not cond:
        print(f"  FAIL {name}: {detail}")
        sys.exit(1)
    PASSED.append(name)
    print(f"  ok {name}")


def _patch_fetch(parsed):
    """Route fetch_one's fetch+parse through a stub page/parser pair."""
    ip._get = lambda url: "<html>stub</html>"
    ip.ADAPTERS["IBIT"] = ("issuer_ishares", "stub://ibit", lambda html: parsed)


def t1_identity_check():
    good = {"shares": 1_000_000.0, "nav": 40.0, "aum": 40_000_000.0, "asof": None}
    _patch_fetch(dict(good))
    ok("identity pass", ip.fetch_one("IBIT") is not None)
    bad = dict(good, aum=90_000_000.0)          # shares*nav off by >15%
    _patch_fetch(bad)
    ok("identity reject (mis-parse)", ip.fetch_one("IBIT") is None)
    noaum = dict(good, aum=None)
    _patch_fetch(noaum)
    ok("no-AUM funds unaffected", ip.fetch_one("IBIT") is not None)


def t2_staleness_guard():
    fresh = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    _patch_fetch({"shares": 1e6, "nav": 40.0, "aum": 4e7, "asof": fresh})
    ok("fresh as-of passes", ip.fetch_one("IBIT") is not None)
    stale = (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%Y-%m-%d")
    _patch_fetch({"shares": 1e6, "nav": 40.0, "aum": 4e7, "asof": stale})
    ok("stale as-of -> declared absence", ip.fetch_one("IBIT") is None)
    _patch_fetch({"shares": 1e6, "nav": 40.0, "aum": 4e7, "asof": "gibberish!!"})
    ok("unparseable as-of kept (identity still guards)",
       ip.fetch_one("IBIT") is not None)


def t3_etha_epoch():
    pre = datetime(2026, 10, 5, 23, 0, tzinfo=timezone.utc)    # ET evening Oct 5
    ok("pre-split keeps base src",
       ip._epoch_src("ETHA", "issuer_ishares", pre) == "issuer_ishares")
    post = datetime(2026, 10, 6, 23, 0, tzinfo=timezone.utc)   # ET evening Oct 6
    ok("post-split stamps epoch r1",
       ip._epoch_src("ETHA", "issuer_ishares", post) == "issuer_ishares_r1")
    # Pre-dawn ET on Oct 6 belongs to Oct 5's book (mirrors t_of) — still base src.
    predawn = datetime(2026, 10, 6, 8, 0, tzinfo=timezone.utc)  # 04:00 ET
    ok("pre-dawn Oct 6 = prior book, base src",
       ip._epoch_src("ETHA", "issuer_ishares", predawn) == "issuer_ishares")
    ok("non-break fund untouched",
       ip._epoch_src("IBIT", "issuer_ishares", post) == "issuer_ishares")


if __name__ == "__main__":
    print("=== etf_issuer_pages guard regressions ===")
    t1_identity_check()
    t2_staleness_guard()
    t3_etha_epoch()
    print(f"\nALL {len(PASSED)} CHECKS PASSED")
