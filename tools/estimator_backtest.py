# -*- coding: utf-8 -*-
"""
estimator_backtest.py — D1 offline replay backtest (board-gated, Chairman-ordered 2026-07-19)
=============================================================================================
Replays the dual-pathway blend weight w under PRE-REGISTERED candidate baseline estimators
against the incumbent (upper-median of the prior 12 RAW history rows) using ONLY stored,
served per-cycle inputs. READ-ONLY: endpoints only, zero writes, zero engine surface.
Nothing here changes a served score; the output is the GATE TABLE the founder reviews
before any flag exists, per BOARD_estimator-fdm-snapshot2_2026-07-19.md (D1).

SCOPE LIMITATION (stated, not hidden): the engine serves 30 history rows per topic, so the
replay window is ~5–7 days per topic across ~150 topics (~4,000+ cycles), not the full 365d
panel. A deeper engine-side replay remains available later; these gates are evaluated on the
servable window and say so.

PRE-REGISTERED CANDIDATES (do not add post-hoc):
  INC  incumbent: upper-median (sorted[n//2]) over prior 12 RAW rows (dups included)
  C1   dedup:     upper-median over prior 12 SLOT-DEDUPED rows (one row per cycle hour)
  C2   interp:    linear-interpolated median over 12 slot-deduped rows
  C3a/b/c slew:   baseline chases the C2 median with per-cycle UP rate cap Δ/16, Δ/8, Δ/4
                  (Δ = 35 mag / 3 breadth), DOWN unlimited (revulsion stays fast)
  +H   hysteresis overlay on the best C: after a w release (drop >= 0.3), an upward
       re-crossing within REFRACTORY=4 cycles must clear the factor by H_MARGIN
       (H_MARGIN = fleet median absolute one-cycle factor change, computed and printed
       BEFORE any gate is read — registered, not tuned).

GATES (pass/fail, registered before the run):
  G1 enrollment invariance: first det>=70 and first det>=85 crossings never LATER (zero).
  G2 no inflation: candidate det mean/p95 <= incumbent + 0.5; max per-cycle uplift printed.
  G3 flap down: full-swing reversals (|Δ|>=30 alternating within <=2 cycles) strictly lower.
  G4 tails: where mag collapses (>=20 below prior) and incumbent releases, candidate reaches
     w<=0.1 within +1 cycle.
  G5 cliff bound: max single-cycle |Δdet| with static args (|Δmag|<2, Δnplat=0) <= 20.
  P  plateau exposure (Outsider): cycles inside >=3-identical-det runs ending in a >=30 drop
     — must not increase.

det reconstruction (Executioner's pathway-recovery): at stored w~1 cycles det==mainstream_
detection; at w~0 det==expert_detection; both quasi-static (replay-verified). Candidate
det_c = (1-w_c)*expert_est + w_c*md_est using the nearest known anchors; cycles without
both anchors are SKIPPED and counted honestly.
"""
from __future__ import annotations
import json, os, sys, time, urllib.request, urllib.parse, statistics
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENGINE = os.getenv("ASSESSOR_ENGINE_URL",
                   "https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com")
UA = "NowTrendInEstimatorBacktest/1.0 (read-only; abelc.esq@gmail.com)"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.getenv("BACKTEST_OUT_DIR") or os.path.join(REPO, "audits", "backtests")

MAG_DELTA, BR_DELTA = 35.0, 3.0
REFRACTORY = 4
COHORT19 = ["spain", "mamdani", "white_house", "andy_burnham", "shutting", "japan", "rikers",
            "jordan", "google", "cyclosporiasis_outbreak", "youtube", "cyclosporiasis_cases",
            "amnesty", "america", "russia", "tillis", "texas", "trump_fires", "taco",
            "britain", "final_del_mundial"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=90))


def fetch_corpus():
    keys = []
    for off in (0, 100):
        d = get(f"{ENGINE}/scores?limit=100&offset={off}")
        keys += [r["topic_key"] for r in d.get("results", []) if r.get("topic_key")]
        time.sleep(0.4)
    keys = list(dict.fromkeys(COHORT19 + keys))[:150]
    corpus = {}
    for k in keys:
        try:
            d = get(f"{ENGINE}/scores/{urllib.parse.quote(k)}")
        except Exception:
            continue
        time.sleep(0.25)
        rows = []
        for h in (d.get("score_history") or []):
            if h.get("detection_score") is None or not h.get("scored_at"):
                continue
            rows.append({"ts": str(h["scored_at"]), "det": float(h["detection_score"]),
                         "w": h.get("mainstream_ratio"),
                         "mag": float(h.get("attention_magnitude") or 0),
                         "n": float(h.get("n_mainstream_platforms") or 0)})
        rows.sort(key=lambda r: r["ts"])                 # oldest -> newest
        if len(rows) >= 15:
            corpus[k] = rows
    return corpus


def upper_median(vals):
    s = sorted(vals)
    return s[len(s) // 2] if s else None


def interp_median(vals):
    s = sorted(vals)
    if not s:
        return None
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def dedup_rows(prior):
    out, seen = [], set()
    for r in reversed(prior):                            # newest-first for slot pick
        slot = r["ts"][:13]
        if slot in seen:
            continue
        seen.add(slot)
        out.append(r)
    return list(reversed(out))                           # back to oldest->newest


def w_from(baseline_mag, baseline_n, cur_mag, cur_n):
    mf = max(0.0, min(1.0, (cur_mag - baseline_mag) / MAG_DELTA))
    bf = max(0.0, min(1.0, (cur_n - baseline_n) / BR_DELTA))
    return round(max(mf, bf), 3)


def replay(rows, mode, up_frac=None, h_margin=0.0, use_hyst=False):
    """Return per-cycle candidate w list (None where <3 baseline rows)."""
    ws, slew_m, slew_n = [], None, None
    last_release_i = -99
    for i, cur in enumerate(rows):
        prior = rows[:i]
        base_rows = prior[-12:] if mode == "raw" else dedup_rows(prior)[-12:]
        if len(base_rows) < 3:
            ws.append(None)
            continue
        mags = [r["mag"] for r in base_rows]
        ns = [r["n"] for r in base_rows]
        if mode in ("raw", "dedup"):
            bm, bn = upper_median(mags), upper_median(ns)
        else:                                            # interp / slew share interp target
            bm, bn = interp_median(mags), interp_median(ns)
        if mode == "slew":
            tgt_m, tgt_n = bm, bn
            if slew_m is None:
                slew_m, slew_n = tgt_m, tgt_n
            else:
                slew_m = slew_m + min(max(tgt_m - slew_m, -1e9), MAG_DELTA * up_frac) \
                    if tgt_m > slew_m else tgt_m         # up: capped, down: instant
                slew_n = slew_n + min(max(tgt_n - slew_n, -1e9), BR_DELTA * up_frac) \
                    if tgt_n > slew_n else tgt_n
            bm, bn = slew_m, slew_n
        w = w_from(bm, bn, cur["mag"], cur["n"])
        if use_hyst and ws:
            prev = next((x for x in reversed(ws) if x is not None), None)
            if prev is not None:
                if prev - w >= 0.3:
                    last_release_i = i
                elif w - prev >= 0.3 and (i - last_release_i) <= REFRACTORY:
                    # re-crossing inside the refractory window must clear the margin
                    mf = max(0.0, min(1.0, (cur["mag"] - bm) / MAG_DELTA))
                    bf = max(0.0, min(1.0, (cur["n"] - bn) / BR_DELTA))
                    if max(mf, bf) < prev + h_margin:
                        w = prev                          # hold prior regime this cycle
        ws.append(w)
    return ws


def det_series(rows, ws):
    """Executioner pathway recovery: candidate det from anchors; None where unknown."""
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


def metrics(rows, dets):
    """Gate metrics over a det series (None entries skipped)."""
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
    def first_cross(th):
        for i, v in d:
            if v >= th:
                return i
        return None
    plateau = 0
    run = 1
    for a in range(1, len(d)):
        if abs(d[a][1] - d[a - 1][1]) <= 0.5 and d[a][0] - d[a - 1][0] == 1:
            run += 1
        else:
            if run >= 3 and d[a - 1][1] - d[a][1] >= 30:
                plateau += run
            run = 1
    vals = [v for _, v in d]
    return {"flaps": flaps, "cliff": cliff, "cross70": first_cross(70),
            "cross85": first_cross(85), "plateau": plateau,
            "mean": statistics.fmean(vals) if vals else 0,
            "p95": sorted(vals)[int(0.95 * (len(vals) - 1))] if vals else 0}


def main():
    print("Fetching corpus (150 topics, paced)...")
    corpus = fetch_corpus()
    print(f"corpus: {len(corpus)} topics with >=15 cycles")

    # ── REPRODUCTION GATE (precondition): incumbent replay must match stored w ──
    match = tot = 0
    for k, rows in corpus.items():
        ws = replay(rows, "raw")
        for r, w in zip(rows, ws):
            if w is None or r["w"] is None:
                continue
            tot += 1
            if abs(float(r["w"]) - w) <= 0.15 or (float(r["w"]) >= 0.97 and w >= 0.85) \
               or (float(r["w"]) <= 0.03 and w <= 0.15):
                match += 1
    repro = 100 * match / tot if tot else 0
    print(f"REPRODUCTION GATE: {repro:.1f}% of {tot} cycles match stored w "
          f"(tier-migration +0.3 and expert-community effects are not served, so "
          f"perfect reproduction is impossible; 95% registered bar, note deviations)")

    # H_MARGIN registered from fleet dispersion BEFORE gates are read:
    diffs = []
    for rows in corpus.values():
        for a in range(1, len(rows)):
            diffs.append(abs(rows[a]["mag"] - rows[a - 1]["mag"]) / MAG_DELTA)
            diffs.append(abs(rows[a]["n"] - rows[a - 1]["n"]) / BR_DELTA)
    h_margin = round(statistics.median(diffs), 3) if diffs else 0.05
    print(f"H_MARGIN (registered, fleet median abs one-cycle factor change): {h_margin}")

    candidates = {
        "INC": dict(mode="raw"),
        "C1_dedup": dict(mode="dedup"),
        "C2_interp": dict(mode="interp"),
        "C3a_slew16": dict(mode="slew", up_frac=1 / 16),
        "C3b_slew8": dict(mode="slew", up_frac=1 / 8),
        "C3c_slew4": dict(mode="slew", up_frac=1 / 4),
        "C2H_interp_hyst": dict(mode="interp", use_hyst=True, h_margin=h_margin),
        "C3bH_slew8_hyst": dict(mode="slew", up_frac=1 / 8, use_hyst=True, h_margin=h_margin),
    }
    results = {}
    for name, cfg in candidates.items():
        agg = {"flaps": 0, "cliff": 0.0, "plateau": 0, "delayed70": 0, "delayed85": 0,
               "earlier": 0, "mean": [], "p95": [], "uplift": 0.0, "skipped": 0,
               "tail_fail": 0}
        base_metrics = {}
        for k, rows in corpus.items():
            ws = replay(rows, cfg["mode"], cfg.get("up_frac"),
                        cfg.get("h_margin", 0.0), cfg.get("use_hyst", False))
            dets, skipped = det_series(rows, ws)
            m = metrics(rows, dets)
            agg["skipped"] += skipped
            agg["flaps"] += m["flaps"]
            agg["cliff"] = max(agg["cliff"], m["cliff"])
            agg["plateau"] += m["plateau"]
            agg["mean"].append(m["mean"])
            agg["p95"].append(m["p95"])
            if name == "INC":
                base_metrics[k] = m
            else:
                b = results["INC"]["per_topic"].get(k)
                if b:
                    for th, key in ((70, "delayed70"), (85, "delayed85")):
                        bi, ci = b[f"cross{th}"], m[f"cross{th}"]
                        if bi is not None and (ci is None or ci > bi):
                            agg[key] += 1
                        elif bi is not None and ci is not None and ci < bi:
                            agg["earlier"] += 1
                # G4 tails: incumbent releases (w-ish det drop>=30 w/ mag collapse) —
                # candidate must be within +1 cycle. Approximated via cliff cycles where
                # mag fell >=20: compare candidate det at i+1 <= incumbent det at i + 5.
            if name != "INC":
                bdets = results["INC"]["per_topic_dets"].get(k)
                if bdets:
                    for i in range(1, len(rows)):
                        if rows[i]["mag"] <= rows[i - 1]["mag"] - 20:
                            bi, ci = bdets[i], dets[i] if i < len(dets) else None
                            ni = dets[i + 1] if i + 1 < len(dets) else None
                            if bi is not None and ci is not None and ci - bi > 5 \
                               and (ni is None or (ni - bi) > 5):
                                agg["tail_fail"] += 1
                    for bi, ci in zip(bdets, dets):
                        if bi is not None and ci is not None:
                            agg["uplift"] = max(agg["uplift"], ci - bi)
            if name == "INC":
                results.setdefault("INC", {"per_topic": {}, "per_topic_dets": {}})
                results["INC"]["per_topic"][k] = m
                results["INC"]["per_topic_dets"][k] = dets
        agg["mean"] = round(statistics.fmean(agg["mean"]), 2) if agg["mean"] else 0
        agg["p95"] = round(statistics.fmean(agg["p95"]), 2) if agg["p95"] else 0
        if name == "INC":
            results["INC"]["agg"] = agg
        else:
            results[name] = {"agg": agg}
        a = agg
        print(f"{name:18} flaps={a['flaps']:3d} cliffMax={a['cliff']:5.1f} "
              f"plateau={a['plateau']:4d} mean={a['mean']:6.2f} p95={a['p95']:6.2f} "
              f"delayed70={a['delayed70']} delayed85={a['delayed85']} earlier={a['earlier']} "
              f"maxUplift={a['uplift']:4.1f} tailFail={a['tail_fail']} skipped={a['skipped']}")

    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y-%m-%d")
    out = {"run_at_utc": datetime.utcnow().isoformat(timespec="seconds"),
           "corpus_topics": len(corpus), "reproduction_pct": round(repro, 1),
           "h_margin_registered": h_margin,
           "gates": {"G1": "zero delayed 70/85 crossings", "G2": "mean/p95 <= INC+0.5",
                     "G3": "flaps strictly < INC", "G4": "tail_fail == 0",
                     "G5": "cliffMax <= 20", "P": "plateau <= INC"},
           "results": {k: v["agg"] for k, v in results.items()}}
    p = os.path.join(OUT_DIR, f"ESTIMATOR_BACKTEST_{stamp}.json")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    print(f"\nresults -> {p}")


if __name__ == "__main__":
    main()
