# -*- coding: utf-8 -*-
"""
estimator_replay.py — D1 ROUND-2 engine-side replay (Chairman-commissioned 2026-07-19)
======================================================================================
HELD-OUT, READ-ONLY with respect to everything that matters: reads velocity_scores
per-cycle stored fields, writes ONLY its own results table (estimator_replay_results).
Never imports scoring, never touches serve paths, serve_payload, or any ledger.
Chunked: each step() call processes a bounded batch of topics (batch-paced pipeline
rule, CLAUDE.md §13); a driver polls until done and a report step aggregates.

ROUND-2 REGISTRATION (fixed BEFORE the run; changes = a new round):
  Candidates: INC (upper-median/12 raw rows) · C1 (upper-median/12 slot-deduped) ·
  C2 (interpolated median/12 deduped) · C3b (slew: baseline chases C2 target, up-rate
  cap Δ/8 per cycle, down instant) · C5 (C3b + SNAP on GENUINE COLLAPSE: when current
  magnitude drops >=20 vs the previous cycle, baselines snap to target immediately —
  targets the round-1 G4 tail failures without giving back the taper at median-catch-up
  cliffs; amended pre-run after the local smoke test showed the nonpositive-deviation
  variant degenerates to the incumbent exactly at the cliffs under repair) ·
  C2H/C3bH/C5H (hysteresis overlay, re-crossing within 4 cycles of a >=0.3 release
  requires factor >= prev + H).
  H = 0.05 FIXED (registered): round 1's fleet-median derivation was degenerate (0.0,
  most cycles static); 0.05 is a conservative floor well under the smallest breadth
  quantum (1 platform = 0.333 factor).
  Gates (unchanged from round 1): G1 zero delayed 70/85 crossings · G2 mean/p95 <=
  INC+0.5 · G3 flaps strictly < INC · G4 tail releases within +1 cycle · G5 cliffMax
  <= 20 · P plateau exposure <= INC.
  Limitation carried honestly: tier-migration (+0.3) and expert-community effects are
  not stored per cycle, so the reproduction rate is measured and reported, not assumed.
"""
from __future__ import annotations
import json
import statistics
import threading
from datetime import datetime, timezone

MAG_DELTA, BR_DELTA = 35.0, 3.0
H_MARGIN = 0.05
REFRACTORY = 4
ROW_CAP = 400          # most-recent rows per topic (365d retention can exceed this)
MIN_ROWS = 15
ACTIVE_DAYS = 30       # corpus = topics scored within the last N days (board corpus spec:
                       # "every topic with >=12 cycles in the last 30 days"; the unfiltered
                       # 365d tail is 43k+ topics — a full-tail panel needs a worker-side
                       # run, registered as out of scope for round 2)

_LOCK = threading.Lock()
_RUNNING = {"flag": False}

_TABLE = """CREATE TABLE IF NOT EXISTS estimator_replay_results (
    topic_key TEXT PRIMARY KEY, cycles INTEGER, payload TEXT, computed_at TEXT)"""


def _upper_median(vals):
    s = sorted(vals)
    return s[len(s) // 2] if s else None


def _interp_median(vals):
    s = sorted(vals)
    if not s:
        return None
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def _dedup(prior):
    out, seen = [], set()
    for r in reversed(prior):
        slot = r["ts"][:13]
        if slot in seen:
            continue
        seen.add(slot)
        out.append(r)
    return list(reversed(out))


def _w(bm, bn, cm, cn):
    mf = max(0.0, min(1.0, (cm - bm) / MAG_DELTA))
    bf = max(0.0, min(1.0, (cn - bn) / BR_DELTA))
    return round(max(mf, bf), 3), mf, bf


def _replay(rows, mode, up_frac=None, snap=False, hyst=False):
    ws, sm, sn = [], None, None
    last_rel = -99
    for i, cur in enumerate(rows):
        prior = rows[:i]
        base = (prior[-12:] if mode == "raw" else _dedup(prior)[-12:])
        if len(base) < 3:
            ws.append(None)
            continue
        mags = [r["mag"] for r in base]
        ns = [r["n"] for r in base]
        if mode in ("raw", "dedup"):
            bm, bn = _upper_median(mags), _upper_median(ns)
        else:
            bm, bn = _interp_median(mags), _interp_median(ns)
        if mode == "slew":
            tm, tn = bm, bn
            if sm is None:
                sm, sn = tm, tn
            else:
                sm = (min(sm + MAG_DELTA * up_frac, tm) if tm > sm else tm)
                sn = (min(sn + BR_DELTA * up_frac, tn) if tn > sn else tn)
                if snap and i > 0 and cur["mag"] <= rows[i - 1]["mag"] - 20:
                    sm, sn = tm, tn        # genuine collapse: release immediately
            bm, bn = sm, sn
        w, mf, bf = _w(bm, bn, cur["mag"], cur["n"])
        if hyst and ws:
            prev = next((x for x in reversed(ws) if x is not None), None)
            if prev is not None:
                if prev - w >= 0.3:
                    last_rel = i
                elif w - prev >= 0.3 and (i - last_rel) <= REFRACTORY \
                        and max(mf, bf) < prev + H_MARGIN:
                    w = prev
        ws.append(w)
    return ws


def _dets(rows, ws):
    expert = md = None
    out, skipped = [], 0
    for r, w in zip(rows, ws):
        sw = r["w"]
        if sw is not None:
            if float(sw) >= 0.97:
                md = r["det"]
            elif float(sw) <= 0.03:
                expert = r["det"]
        if w is None or expert is None or md is None:
            out.append(None)
            skipped += 1
            continue
        out.append(round((1 - w) * expert + w * md, 2))
    return out, skipped


def _metrics(rows, dets):
    d = [(i, v) for i, v in enumerate(dets) if v is not None]
    flaps = 0
    for a in range(1, len(d) - 1):
        (i1, v1), (i2, v2), (i3, v3) = d[a - 1], d[a], d[a + 1]
        if i2 - i1 <= 2 and i3 - i2 <= 2:
            if (v2 - v1) >= 30 and (v2 - v3) >= 30:
                flaps += 1
            if (v1 - v2) >= 30 and (v3 - v2) >= 30:
                flaps += 1
    cliff = 0.0
    for a in range(1, len(d)):
        (i1, v1), (i2, v2) = d[a - 1], d[a]
        if i2 - i1 == 1:
            r1, r2 = rows[i1], rows[i2]
            if abs(r2["mag"] - r1["mag"]) < 2 and r2["n"] == r1["n"]:
                cliff = max(cliff, abs(v2 - v1))
    def cross(th):
        for i, v in d:
            if v >= th:
                return i
        return None
    plateau, run = 0, 1
    for a in range(1, len(d)):
        if abs(d[a][1] - d[a - 1][1]) <= 0.5 and d[a][0] - d[a - 1][0] == 1:
            run += 1
        else:
            if run >= 3 and d[a - 1][1] - d[a][1] >= 30:
                plateau += run
            run = 1
    vals = [v for _, v in d]
    return {"flaps": flaps, "cliff": round(cliff, 1), "cross70": cross(70),
            "cross85": cross(85), "plateau": plateau,
            "mean": round(statistics.fmean(vals), 2) if vals else 0,
            "p95": (sorted(vals)[int(0.95 * (len(vals) - 1))] if vals else 0),
            "n_cycles": len(d)}


CANDIDATES = {
    "INC": dict(mode="raw"),
    "C1_dedup": dict(mode="dedup"),
    "C2_interp": dict(mode="interp"),
    "C3b_slew8": dict(mode="slew", up_frac=1 / 8),
    "C5_slew8_snap": dict(mode="slew", up_frac=1 / 8, snap=True),
    "C2H": dict(mode="interp", hyst=True),
    "C3bH": dict(mode="slew", up_frac=1 / 8, hyst=True),
    "C5H": dict(mode="slew", up_frac=1 / 8, snap=True, hyst=True),
}


def step(get_db, db_path, batch: int = 10, gate=None, prefilter: int = 0):
    """Process up to `batch` unprocessed topics. Single-flight; bounded; returns progress.
    gate: the engine's _is_quality_topic — the corpus is the SERVED universe, so topics
    failing the quality gate are marked skipped (never replayed). prefilter>0: instead of
    replaying, bulk-mark up to N gate-failing candidates as skipped (fast junk drain)."""
    batch = max(1, min(int(batch), 25))
    if not _LOCK.acquire(blocking=False):
        return {"status": "busy"}
    try:
        if _RUNNING["flag"]:
            return {"status": "busy"}
        _RUNNING["flag"] = True
        conn = get_db(db_path)
        try:
            conn.execute(_TABLE)
            conn.commit()
            from datetime import timedelta
            cutoff = (datetime.now(timezone.utc) - timedelta(days=ACTIVE_DAYS)).isoformat()

            def _candidates(limit):
                return [( (r["topic_key"] if hasattr(r, "keys") else r[0]),
                          (r["disp"] if hasattr(r, "keys") else r[1]) or "" )
                        for r in conn.execute(
                    """SELECT v.topic_key, MAX(v.topic_display) AS disp
                       FROM velocity_scores v
                       LEFT JOIN estimator_replay_results e ON e.topic_key = v.topic_key
                       WHERE e.topic_key IS NULL
                       GROUP BY v.topic_key
                       HAVING COUNT(*) >= ? AND MAX(v.scored_at) >= ?
                       LIMIT ?""", (MIN_ROWS, cutoff, limit)).fetchall()]

            def _mark_skipped(keys, reason):
                now = datetime.now(timezone.utc).isoformat(timespec="seconds")
                for tk in keys:
                    conn.execute("DELETE FROM estimator_replay_results WHERE topic_key=?", (tk,))
                    conn.execute("INSERT INTO estimator_replay_results "
                                 "(topic_key, cycles, payload, computed_at) VALUES (?,0,?,?)",
                                 (tk, json.dumps({"skipped": reason}), now))
                conn.commit()

            if prefilter:
                cands = _candidates(max(100, min(int(prefilter), 8000)))
                junk = [tk for tk, disp in cands
                        if gate is not None and not gate(disp or tk.replace("_", " "))]
                _mark_skipped(junk, "quality_gate")
                return {"status": "ok", "prefiltered": len(cands),
                        "junk_marked": len(junk),
                        "quality_seen": len(cands) - len(junk)}

            todo = []
            for tk, disp in _candidates(batch * 4):
                if gate is not None and not gate(disp or tk.replace("_", " ")):
                    _mark_skipped([tk], "quality_gate")
                    continue
                todo.append(tk)
                if len(todo) >= batch:
                    break
            done_ct = conn.execute(
                "SELECT COUNT(*) AS c FROM estimator_replay_results").fetchone()
            done_ct = done_ct["c"] if hasattr(done_ct, "keys") else done_ct[0]
            processed = []
            for tk in todo:
                rows = [dict(ts=str(r["scored_at"] if hasattr(r, "keys") else r[0]),
                             det=float((r["detection_score"] if hasattr(r, "keys") else r[1]) or 0),
                             w=(r["mainstream_ratio"] if hasattr(r, "keys") else r[2]),
                             mag=float((r["attention_magnitude"] if hasattr(r, "keys") else r[3]) or 0),
                             n=float((r["n_mainstream_platforms"] if hasattr(r, "keys") else r[4]) or 0))
                        for r in conn.execute(
                            """SELECT scored_at, detection_score, mainstream_ratio,
                                      attention_magnitude, n_mainstream_platforms
                               FROM velocity_scores WHERE topic_key = ?
                               ORDER BY scored_at DESC LIMIT ?""", (tk, ROW_CAP)).fetchall()]
                rows.sort(key=lambda r: r["ts"])
                if len(rows) < MIN_ROWS:
                    payload = {"skipped": "too_few_rows"}
                else:
                    payload = {}
                    # reproduction stats on INC
                    ws_inc = _replay(rows, "raw")
                    m = t = 0
                    for r, w in zip(rows, ws_inc):
                        if w is None or r["w"] is None:
                            continue
                        t += 1
                        sw = float(r["w"])
                        if abs(sw - w) <= 0.15 or (sw >= 0.97 and w >= 0.85) \
                                or (sw <= 0.03 and w <= 0.15):
                            m += 1
                    payload["repro"] = {"match": m, "total": t}
                    base_dets = None
                    for name, cfg in CANDIDATES.items():
                        ws = _replay(rows, cfg["mode"], cfg.get("up_frac"),
                                     cfg.get("snap", False), cfg.get("hyst", False))
                        dets, skipped = _dets(rows, ws)
                        met = _metrics(rows, dets)
                        met["skipped"] = skipped
                        if name == "INC":
                            base_dets = dets
                            met["uplift"] = 0.0
                            met["tail_fail"] = 0
                        else:
                            up = 0.0
                            tf = 0
                            for i in range(len(rows)):
                                bi = base_dets[i] if i < len(base_dets) else None
                                ci = dets[i] if i < len(dets) else None
                                if bi is not None and ci is not None:
                                    up = max(up, ci - bi)
                                if i and rows[i]["mag"] <= rows[i - 1]["mag"] - 20:
                                    ni = dets[i + 1] if i + 1 < len(dets) else None
                                    if bi is not None and ci is not None and ci - bi > 5 \
                                            and (ni is None or bi is None or (ni - bi) > 5):
                                        tf += 1
                            met["uplift"] = round(up, 1)
                            met["tail_fail"] = tf
                        payload[name] = met
                conn.execute("DELETE FROM estimator_replay_results WHERE topic_key=?", (tk,))
                conn.execute("INSERT INTO estimator_replay_results "
                             "(topic_key, cycles, payload, computed_at) VALUES (?,?,?,?)",
                             (tk, len(rows), json.dumps(payload),
                              datetime.now(timezone.utc).isoformat(timespec="seconds")))
                conn.commit()
                processed.append(tk)
            remaining = conn.execute(
                """SELECT COUNT(*) AS c FROM (
                     SELECT v.topic_key FROM velocity_scores v
                     LEFT JOIN estimator_replay_results e ON e.topic_key = v.topic_key
                     WHERE e.topic_key IS NULL
                     GROUP BY v.topic_key
                     HAVING COUNT(*) >= ? AND MAX(v.scored_at) >= ?) x""",
                (MIN_ROWS, cutoff)).fetchone()
            remaining = remaining["c"] if hasattr(remaining, "keys") else remaining[0]
            return {"status": "ok", "processed": processed,
                    "done_before": done_ct, "remaining": remaining}
        finally:
            try:
                conn.close()
            except Exception:
                pass
    finally:
        _RUNNING["flag"] = False
        _LOCK.release()


def report(get_db, db_path):
    """Aggregate stored per-topic results into the round-2 gate table."""
    conn = get_db(db_path)
    try:
        conn.execute(_TABLE)
        rows = conn.execute(
            "SELECT topic_key, cycles, payload FROM estimator_replay_results").fetchall()
    finally:
        try:
            conn.close()
        except Exception:
            pass
    agg = {n: {"flaps": 0, "cliff": 0.0, "plateau": 0, "mean": [], "p95": [],
               "delayed70": 0, "delayed85": 0, "earlier": 0, "uplift": 0.0,
               "tail_fail": 0, "skipped": 0, "n_cycles": 0} for n in CANDIDATES}
    rm = rt = 0
    topics = 0
    for r in rows:
        payload = json.loads((r["payload"] if hasattr(r, "keys") else r[2]) or "{}")
        if "INC" not in payload:
            continue
        topics += 1
        rp = payload.get("repro") or {}
        rm += rp.get("match", 0)
        rt += rp.get("total", 0)
        inc = payload["INC"]
        for n in CANDIDATES:
            met = payload.get(n)
            if not met:
                continue
            a = agg[n]
            a["flaps"] += met["flaps"]
            a["cliff"] = max(a["cliff"], met["cliff"])
            a["plateau"] += met["plateau"]
            a["mean"].append(met["mean"])
            a["p95"].append(met["p95"])
            a["uplift"] = max(a["uplift"], met.get("uplift", 0))
            a["tail_fail"] += met.get("tail_fail", 0)
            a["skipped"] += met.get("skipped", 0)
            a["n_cycles"] += met.get("n_cycles", 0)
            if n != "INC":
                for th in (70, 85):
                    bi, ci = inc.get(f"cross{th}"), met.get(f"cross{th}")
                    if bi is not None and (ci is None or ci > bi):
                        a[f"delayed{th}"] += 1
                    elif bi is not None and ci is not None and ci < bi:
                        a["earlier"] += 1
    for n, a in agg.items():
        a["mean"] = round(statistics.fmean(a["mean"]), 2) if a["mean"] else 0
        a["p95"] = round(statistics.fmean(a["p95"]), 2) if a["p95"] else 0
    inc = agg["INC"]
    gates = {}
    for n, a in agg.items():
        if n == "INC":
            continue
        gates[n] = {
            "G1_zero_delayed": a["delayed70"] == 0 and a["delayed85"] == 0,
            "G2_no_inflation": a["mean"] <= inc["mean"] + 0.5 and a["p95"] <= inc["p95"] + 0.5,
            "G3_flaps_down": a["flaps"] < inc["flaps"],
            "G4_tails": a["tail_fail"] == 0,
            "G5_cliff_bound": a["cliff"] <= 20,
            "P_plateau": a["plateau"] <= inc["plateau"],
        }
        gates[n]["ALL_PASS"] = all(gates[n].values())
    return {"held_out": True, "registered": "round-2 (H=0.05 fixed; C5 snap variant added)",
            "topics": topics, "reproduction_pct":
                round(100 * rm / rt, 1) if rt else None,
            "aggregates": agg, "gate_table": gates}
