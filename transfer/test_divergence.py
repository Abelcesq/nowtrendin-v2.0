# -*- coding: utf-8 -*-
"""ENFORCER for the sealed Positioning-vs-Price residual (`transfer/divergence.py`,
sealed prereg `audits/board/DIVERGENCE_PREREG_2026-09-14.md`).

WHAT THIS FILE MAKES MECHANICAL, per test:
  a  SEAL BINDING — sha256 of the prereg file must equal divergence.PARAM_VERSION.
     Editing a sealed section without minting a new param_version is a BUILD
     FAILURE, not a memo violation.
  b  RESIDUAL RECOVERY — a q-jump with flat price yields a positive D peaking at
     the episode; deleveraging (q drop, flat price) yields a negative D. The sign
     must be able to go negative (07-29 degeneracy rule, prereg §2).
  c  THEIL–SEN ROBUSTNESS — one gross outlier moves an OLS slope materially and
     the Theil–Sen slope immaterially.
  d  FORWARD-ONLY — appending altered future observations leaves every already-
     computed row byte-identical (no forward-looking joins, prereg §8).
  e  MAD == 0 — a zero-variance stretch serves measured:false / D None: honest
     absence, never a fabricated z (§16a stage-2).
  f  SUSPECT EXCLUSION — the crypto adapter drops suspect=1 rows (K14) and
     survives an old-schema SQLite file with no `suspect` column.

Run: python test_divergence.py   (or via tools/run_tests.py)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import sqlite3
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# The adapter goes through db_compat, which routes to Postgres when DATABASE_URL is
# set. This fixture builds throwaway SQLite files, so force the SQLite path BEFORE
# any project import.
os.environ.pop("DATABASE_URL", None)

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import divergence  # noqa: E402

_passed, _failed = 0, 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        print(f"  FAIL  {name}  {detail}")


def _dates(n):
    # Synthetic ascending date labels; the core treats them as opaque sort keys.
    return [f"2026-{1 + i // 28:02d}-{1 + i % 28:02d}-{i:04d}"[:10] + f"#{i:04d}"
            for i in range(n)]


def _synthetic(n=420, seed=7, beta=0.8, noise=0.01):
    """ln(p) random walk; ln(q) = beta*ln(p) + small noise. Returns (q_raw, p_raw)."""
    rng = random.Random(seed)
    lp, lq_noise = 0.0, 0.0
    q_raw, p_raw = [], []
    for _ in range(n):
        lp += rng.gauss(0, 0.02)
        lq_noise = 0.6 * lq_noise + rng.gauss(0, noise)
        p_raw.append(math.exp(lp) * 100.0)
        q_raw.append(math.exp(beta * lp + lq_noise) * 1000.0)
    return q_raw, p_raw


def main() -> int:
    print("DIVERGENCE — sealed §2 residual: seal binding + honest mechanics")
    print("=" * 70)

    # ── (a) SEAL BINDING ────────────────────────────────────────────────────────
    prereg = os.path.normpath(os.path.join(
        _HERE, "..", "audits", "board", "DIVERGENCE_PREREG_2026-09-14.md"))
    try:
        with open(prereg, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
    except OSError as e:
        digest = f"UNREADABLE: {e}"
    check("a1 prereg file exists and hashes", isinstance(digest, str)
          and len(digest) == 64, str(digest))
    check("a2 sha256(prereg) == PARAM_VERSION (the seal is the build gate)",
          digest == divergence.PARAM_VERSION,
          f"prereg={digest[:16]}... PARAM_VERSION={divergence.PARAM_VERSION[:16]}... "
          "— a sealed section was edited without minting a new param_version")
    check("a3 theta is the sealed +1.5, BTC/ETH only",
          divergence.THETA == 1.5 and tuple(divergence.FLAG_COINS) == ("BTC", "ETH"))

    # ── (b) RESIDUAL RECOVERY ───────────────────────────────────────────────────
    n = 420
    q_raw, p_raw = _synthetic(n)
    ep_lo, ep_hi = 320, 340          # well past the ~186-obs warm-up
    q_up = list(q_raw)
    for i in range(ep_lo, n):
        q_up[i] *= 1.6               # q jumps, price untouched (flat vs baseline)
    up = divergence.divergence_series(_dates(n), q_up, p_raw)
    measured = [r for r in up if r["measured"]]
    check("b1 warm-up produces measured rows on a 420-obs series",
          len(measured) > 100, f"only {len(measured)} measured")
    dmax_row = max(measured, key=lambda r: r["D"])
    dmax_i = up.index(dmax_row)
    check("b2 +divergence episode -> D positive and largest AT the episode",
          dmax_row["D"] > 0 and ep_lo <= dmax_i < ep_hi,
          f"argmax D at index {dmax_i} (episode {ep_lo}-{ep_hi}), D={dmax_row['D']}")

    q_dn = list(q_raw)
    for i in range(ep_lo, n):
        q_dn[i] *= 0.6               # deleveraging: q drops, price flat
    dn = divergence.divergence_series(_dates(n), q_dn, p_raw)
    dn_measured = [r for r in dn if r["measured"]]
    dmin_row = min(dn_measured, key=lambda r: r["D"])
    dmin_i = dn.index(dmin_row)
    check("b3 deleveraging episode -> D NEGATIVE (signed residual, 07-29 rule)",
          dmin_row["D"] < 0 and ep_lo <= dmin_i < ep_hi,
          f"argmin D at index {dmin_i}, D={dmin_row['D']}")

    # ── (c) THEIL–SEN vs one gross outlier ──────────────────────────────────────
    rng = random.Random(3)
    xs = [rng.gauss(0, 1) for _ in range(90)]
    ys = [0.5 * x + rng.gauss(0, 0.05) for x in xs]
    _, b_clean = divergence.theil_sen(xs, ys)
    ys_out = list(ys)
    mx0 = sum(xs) / len(xs)
    out_i = max(range(len(xs)), key=lambda k: abs(xs[k] - mx0))  # high-leverage point
    ys_out[out_i] += 50.0            # one gross outlier
    _, b_dirty = divergence.theil_sen(xs, ys_out)
    # OLS for contrast
    mx, my = sum(xs) / len(xs), sum(ys_out) / len(ys_out)
    b_ols = (sum((x - mx) * (y - my) for x, y in zip(xs, ys_out))
             / sum((x - mx) ** 2 for x in xs))
    check("c1 Theil-Sen slope moves immaterially under one gross outlier",
          abs(b_dirty - b_clean) < 0.05,
          f"clean={b_clean:.4f} dirty={b_dirty:.4f}")
    check("c2 ...where OLS moves materially (the contrast that earns TS)",
          abs(b_ols - b_clean) > 0.1, f"ols={b_ols:.4f} clean={b_clean:.4f}")

    # ── (d) FORWARD-ONLY: altered future never rewrites the past ────────────────
    t_cut = 300
    partial = divergence.divergence_series(_dates(t_cut), q_raw[:t_cut], p_raw[:t_cut])
    q_alt = q_raw[:t_cut] + [v * 7.7 for v in q_raw[t_cut:]]
    p_alt = p_raw[:t_cut] + [v * 0.13 for v in p_raw[t_cut:]]
    full = divergence.divergence_series(_dates(n), q_alt, p_alt)
    same = all(json.dumps(partial[i], sort_keys=True)
               == json.dumps(full[i], sort_keys=True) for i in range(t_cut))
    check("d1 rows <= t byte-identical after appending altered future data",
          same, "a past row changed — a forward-looking dependency exists")

    # ── (e) MAD == 0 -> honest absence ──────────────────────────────────────────
    q_flat = list(q_raw)
    for i in range(150, 280):
        q_flat[i] = 1000.0           # constant OI: q_chg = 0 across the z window
    flat = divergence.divergence_series(_dates(n), q_flat, p_raw)
    # deep inside the stretch the trailing q_chg window is all-zero -> MAD == 0
    probe = flat[270]
    check("e1 zero-variance stretch -> zq None (no fabricated z)",
          probe["zq"] is None, str(probe))
    check("e2 ...and measured:false with D None (honest absence)",
          probe["measured"] is False and probe["D"] is None, str(probe))
    check("e3 robust_z itself returns None at the MAD floor",
          divergence.robust_z([0.0] * 90, 0.0) is None)

    # ── (f) SUSPECT-ROW EXCLUSION in the crypto adapter ─────────────────────────
    tmp = tempfile.mkdtemp()
    db = os.path.join(tmp, "derivs.db")
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE coinapi_derivs (coin TEXT, signal_date TEXT, "
                 "open_interest REAL, suspect INTEGER DEFAULT 0, "
                 "PRIMARY KEY (coin, signal_date))")
    days = [f"2026-08-{d:02d}" for d in range(1, 21)]
    for i, day in enumerate(days):
        conn.execute("INSERT INTO coinapi_derivs VALUES (?,?,?,?)",
                     ("BTC", day, 100000.0 + i * 10,
                      1 if day == "2026-08-10" else 0))
    conn.commit()
    conn.close()
    prices = {"BTC": {d: 50000.0 + i for i, d in enumerate(days)}}
    res = divergence.crypto_divergence(db, prices)
    served_dates = [r["date"] for r in res["coins"]["BTC"]["series"]]
    check("f1 suspect=1 row is EXCLUDED from the residual series",
          "2026-08-10" not in served_dates and len(served_dates) == 19,
          f"{len(served_dates)} dates; suspect present={'2026-08-10' in served_dates}")
    check("f2 param_version stamped on adapter output",
          res.get("param_version") == divergence.PARAM_VERSION)
    check("f3 short series stays honest: no measured rows before full windows",
          all(r["measured"] is False and r["D"] is None
              for r in res["coins"]["BTC"]["series"]))

    # old-schema file: no `suspect` column at all — adapter must not crash
    db2 = os.path.join(tmp, "derivs_old.db")
    conn = sqlite3.connect(db2)
    conn.execute("CREATE TABLE coinapi_derivs (coin TEXT, signal_date TEXT, "
                 "open_interest REAL, PRIMARY KEY (coin, signal_date))")
    for i, day in enumerate(days):
        conn.execute("INSERT INTO coinapi_derivs VALUES (?,?,?)",
                     ("ETH", day, 5000.0 + i))
    conn.commit()
    conn.close()
    res2 = divergence.crypto_divergence(
        db2, {"ETH": {d: 3000.0 + i for i, d in enumerate(days)}})
    check("f4 old SQLite schema (no suspect column) handled, rows treated clean",
          len(res2["coins"]["ETH"]["series"]) == 20, str(len(
              res2["coins"].get("ETH", {}).get("series", []))))

    # ── flag scope: BTC/ETH only, and only on the internal/shadow marker ────────
    flagged = divergence.divergence_series(
        _dates(n), q_up, p_raw, flag_theta=divergence.THETA)
    unflagged = divergence.divergence_series(_dates(n), q_up, p_raw)
    check("g1 theta-flag rows exist under flag_theta and NONE without it",
          any(r.get("flag") for r in flagged)
          and not any("flag" in r for r in unflagged))
    check("g2 every flag sits at D >= +1.5 (theta by construction, never fitted)",
          all(r["D"] >= 1.5 for r in flagged if r.get("flag")))

    print("=" * 70)
    print(f"{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
