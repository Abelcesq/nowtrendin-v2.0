# -*- coding: utf-8 -*-
"""
scoring_assessor.py — v2 (board-rebuilt, 2026-07-17)
====================================================
The ASSESSOR/TEACHER: grades the live system on the founder's four questions and,
for every failure, emits the GAP and a DIAGNOSTIC next step. Rebuilt to the
six-memo board specification (audits/board/BOARD_scoring-assessor_2026-07-17.md)
from the concept file `07 17 2026 - nowtrendin_scoring_assessor.py`.

THE FOUR QUESTIONS (+ the outside cross-check)
  A. SOURCE TRACKING  — are the sources tracking topics? (annotates /health/collectors)
  B. SCORE MOVEMENT   — how are scores moving? (freeze/volatility over a fixed cohort)
  C. SCORE ACCURACY   — are the scores right? (gap invariant · alias-family sanity ·
                        SURGE-vs-motion referee — never fame-level)
  D. TREND LIFECYCLE  — where is each trend now? (quantile-based, WARN-only v1)
  E. OUTSIDE RECALL   — do today's external trending items exist in our feed?
                        (Google daily-trending RSS · crypto movers via our own feed)

BOARD-MANDATED DESIGN (non-negotiable, enforced in code):
  * ENDPOINTS ONLY — reads the deployed engine's public surfaces; zero SQL, zero
    second read path. Free outside sources only (Wikimedia REST, Google trending
    RSS). NEVER a paid pull (Apify clock-slot rule untouched).
  * CHECK MANIFEST — every check is registered below; param_version embeds the
    manifest hash. Changing any check/threshold changes the version and BREAKS the
    trend line loudly (Friedman–Schwartz series protocol). New checks onboard as
    SHADOW (reported, excluded from the pass % for their first snapshot).
  * THE LEDGER IS THE ACCURACY NUMBER. This tool's `operational_check_pass_pct`
    is INTERNAL-ONLY (never published externally — same rule as the catch-all %).
    Every report quotes /accuracy/ledger's tracked-race rate as THE headline.
  * TASK CLASSES + RULINGS REGISTRY — every finding is classed OPERATIONAL /
    SCORE_AFFECTING / RULED. SCORE_AFFECTING items require founder sign-off + a
    held-out backtest + serve_payload regeneration; RULED items name the Chairman
    ruling they touch and are never auto-implemented. Solutions DIAGNOSE — they
    never prescribe tuning a weight, cap, or threshold.
  * HELD-OUT WALL — referee-derived findings carry held_out_derived=true. The
    referee diagnoses; it never tunes. The DRIFT ALARM tracks engine–referee rank
    correlation across snapshots: a RISING trend means the system is converging
    toward a lagging fame index (the opposite of the thesis) — alarm, not victory.
  * BOARD ANALYSIS REQUIREMENT (Chairman directive 2026-07-17): every snapshot is
    born status=UNVERIFIED_PENDING_BOARD_REVIEW. Before ANY finding teaches or is
    implemented, the advisory board must (1) independently critique the findings,
    (2) cross-check them against freshly-obtained outside data (current highly-
    trending items, market/crypto movers), (3) verify or refute each item. The
    CHAIRMAN has final say before any implementation. The /scoring-assessor skill
    codifies this gate; this tool enforces the status field.

RUN
  python tools/scoring_assessor.py --demo          # synthetic, watermarked
  python tools/scoring_assessor.py                 # live, read-only
  Output -> audits/assessor/ASSESSOR_<UTC date>.json + .md (append-only; commit them).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import statistics
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta

# UTF-8 hard requirement (the v1 file crashed on Windows cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENGINE = os.getenv("ASSESSOR_ENGINE_URL",
                   "https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com")
UA = "NowTrendInAssessor/2.0 (read-only instrument; abelc.esq@gmail.com)"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "audits", "assessor")

# ── CHECK MANIFEST (registered; hash -> param_version; SHADOW = excluded from %) ──
CHECK_MANIFEST = {
    "A.freshness":        {"module": "A_SOURCES",   "shadow": False},
    "A.silent_absence":   {"module": "A_SOURCES",   "shadow": False},
    "B.freeze":           {"module": "B_MOVEMENT",  "shadow": False},
    "B.volatility":       {"module": "B_MOVEMENT",  "shadow": False},
    "C.gap_arithmetic":   {"module": "C_ACCURACY",  "shadow": False},
    "C.alias_families":   {"module": "C_ACCURACY",  "shadow": False},
    "C.referee_surge":    {"module": "C_ACCURACY",  "shadow": True},   # shadow: first snapshot
    "D.lifecycle":        {"module": "D_LIFECYCLE", "shadow": True},   # WARN-only until it beats the null
    "E.trending_recall":  {"module": "E_OUTSIDE",   "shadow": False},
    "E.crypto_agreement": {"module": "E_OUTSIDE",   "shadow": True},
}
THRESHOLDS = {
    "FREEZE_CYCLES": 6, "HIGH_VOL_STD": 12.0, "GAP_TOL": 0.6,
    "SURGE_MULT": 3.0, "SURGE_FLOOR": 200,          # referee_wikipedia convention
    "LIFE_REF_QUANTILE": 0.9, "LIFE_ABS_FLOOR": 200,
    "FADE_RATIO": 0.5, "ENDED_RATIO": 0.25, "MIN_N": 5,
    "COHORT_MOVEMENT": 60, "COHORT_REFEREE": 20, "RECALL_TOP": 10,
}
_manifest_hash = hashlib.sha256(
    json.dumps({"checks": CHECK_MANIFEST, "thresholds": THRESHOLDS},
               sort_keys=True).encode()).hexdigest()[:10]
PARAM_VERSION = f"assessor-v2.{_manifest_hash}"

# ── RULINGS REGISTRY (Chairman rulings a solution must NEVER contradict) ──
RULINGS = [
    {"id": "2026-07-15-alias-display-only",
     "rule": "Topic-alias consolidation is DISPLAY-ONLY (Option A). Score-time or "
             "extraction-time merging (Options B/C) is rejected/deferred.",
     "forbidden": r"merge.*(before|into).*scor|normalize_topic.*alias|consolidat.*before scor"},
    {"id": "no-circular-N",
     "rule": "N (nowtrendin_score) never feeds or validates the Gradient Score.",
     "forbidden": r"fold.*\bN\b.*(into|score)|use N to (validate|confirm)"},
    {"id": "flag-never-force",
     "rule": "No agent tunes weights/caps/thresholds; scoring changes need founder + backtest.",
     "forbidden": r"(raise|soften|tune|adjust).*(cap|weight|threshold)"},
    {"id": "retention-365",
     "rule": "velocity_scores rows younger than 365d are never deleted.",
     "forbidden": r"delete.*(velocity_scores|scored data|history)"},
]

def _ruled(solution: str):
    for r in RULINGS:
        if re.search(r["forbidden"], solution, re.IGNORECASE):
            return r["id"]
    return None


@dataclass
class Finding:
    check: str
    status: str                # PASS | FAIL | WARN | INSUFFICIENT | DEFERRED
    subject: str
    evidence: str              # measured, with numbers + denominator
    gap: str = ""
    solution: str = ""         # DIAGNOSTIC next step — never a tuning instruction
    severity: str = "low"      # low | medium | high
    task_class: str = "OPERATIONAL"   # OPERATIONAL | SCORE_AFFECTING | RULED
    held_out_derived: bool = False
    shadow: bool = False
    ruling_id: str = ""

    def finalize(self):
        self.shadow = CHECK_MANIFEST.get(self.check, {}).get("shadow", False)
        rid = _ruled(self.solution)
        if rid:
            # A solution contradicting a Chairman ruling fails the ASSESSOR, not the system.
            self.ruling_id = rid
            self.task_class = "RULED"
            self.status = "FAIL"
            self.subject = f"ASSESSOR-SELF-CHECK ({self.subject})"
            self.gap = f"this finding's solution contradicts ruling {rid}"
            self.solution = "rewrite the solution text; rulings registry blocked it"
        return self


def http_json(url: str, timeout: int = 45, tries: int = 3):
    """GET json with gentle 503-warming handling (engine-recovery rule: poll,
    never hammer — one retry every 25s, bounded)."""
    last = None
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 503 and attempt < tries - 1:
                time.sleep(25)
                continue
            raise
    raise last


def http_text(url: str, timeout: int = 45) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


# ═════════════════════════════ A · SOURCE TRACKING ═══════════════════════════
def assess_sources(live: bool) -> list:
    out = []
    if not live:
        out.append(Finding("A.freshness", "PASS", "demo-source", "DEMO synthetic pass"))
        out.append(Finding("A.silent_absence", "FAIL", "demo-guardian",
                           "DEMO: configured source with zero signals",
                           gap="DEMO gap", solution="DEMO diagnostic", severity="high"))
        return out
    d = http_json(f"{ENGINE}/health/collectors")
    cols = d.get("collectors") or {}
    DEFERRED = {"reddit", "guardian"}   # founder-deferred keys — never a failure
    for name, c in cols.items():
        st = (c.get("status") or "").upper()
        detail = str(c.get("detail") or "")[:90]
        if name in DEFERRED and st != "HEALTHY":
            out.append(Finding("A.freshness", "DEFERRED", name,
                               f"{st} — founder-deferred credentials ({detail})"))
        elif st == "HEALTHY":
            out.append(Finding("A.freshness", "PASS", name, detail or "healthy"))
        elif st in ("DEGRADED", "STALE"):
            out.append(Finding("A.freshness", "WARN", name, f"{st}: {detail}",
                gap="this channel's current signal is thin or late in the scores",
                solution="read collector logs + collector_health.consecutive_failures; "
                         "diagnose credential/quota/format causes (no config change from here)",
                severity="medium"))
        elif st == "DOWN":
            out.append(Finding("A.freshness", "FAIL", name, f"DOWN: {detail}",
                gap="an entire channel is absent from every score right now",
                solution="diagnose via /health/collectors detail + engine logs; "
                         "if key-related, surface to the founder (keys are founder-gated)",
                severity="high"))
    summ = d.get("summary") or {}
    if summ:
        out.append(Finding("A.silent_absence",
                           "PASS" if not summ.get("down") else "FAIL",
                           "collector fleet",
                           f"{summ.get('healthy', 0)} healthy / {summ.get('degraded', 0)} degraded / "
                           f"{summ.get('stale', 0)} stale / {summ.get('down', 0)} down "
                           f"(of {summ.get('total', 0)}; trust: {d.get('trust_reason', '')[:60]})",
                           gap="" if not summ.get("down") else "dead channels detected",
                           solution="" if not summ.get("down") else "see per-collector findings",
                           severity="high" if summ.get("down") else "low"))
    return out


# ═════════════════════════════ COHORT (fixed, stratified) ════════════════════
def build_cohort(live: bool) -> dict:
    """cohort_spec is persisted with every snapshot (board condition)."""
    if not live:
        return {"spec": "DEMO", "topics": [
            {"topic_key": "demo_frozen", "topic_display": "Demo Frozen",
             "detection_score": 74, "confidence_score": 70, "nowtrendin_score": 100},
        ]}
    rows = []
    for off in (0, 100):
        d = http_json(f"{ENGINE}/scores?limit=100&offset={off}")
        rows += d.get("results") or []
        time.sleep(0.3)
    led = http_json(f"{ENGINE}/accuracy/ledger/detail?limit=200")
    ledger_keys = {r.get("topic_key") for r in (led.get("rows") or [])}
    by_key = {r.get("topic_key"): r for r in rows if r.get("topic_key")}
    picked, seen = [], set()
    for k in by_key:                                   # ledger-enrolled first (always-in)
        if k in ledger_keys and k not in seen:
            picked.append(by_key[k]); seen.add(k)
    for r in rows:                                     # then top served rows
        k = r.get("topic_key")
        if k and k not in seen:
            picked.append(r); seen.add(k)
        if len(picked) >= THRESHOLDS["COHORT_MOVEMENT"]:
            break
    return {"spec": f"ledger-enrolled(∩top200)={len(ledger_keys & set(by_key))} + "
                    f"top-served fill; n={len(picked)}",
            "topics": picked}


# ═════════════════════════════ B · SCORE MOVEMENT ════════════════════════════
def assess_movement(cohort: dict, live: bool) -> list:
    out = []
    if not live:
        out.append(Finding("B.freeze", "FAIL", "demo_frozen",
                           "DEMO: Detection identical 6 cycles while mentions changed",
                           gap="DEMO gap", solution="DEMO diagnostic", severity="high"))
        return out
    n_checked = 0
    for row in cohort["topics"][:THRESHOLDS["COHORT_MOVEMENT"]]:
        key = row.get("topic_key")
        try:
            d = http_json(f"{ENGINE}/scores/{urllib.parse.quote(key)}")
        except Exception:
            out.append(Finding("B.freeze", "INSUFFICIENT", key, "detail fetch failed"))
            continue
        time.sleep(0.25)
        hist = d.get("score_history") or []
        dets = [h.get("detection_score") for h in hist if h.get("detection_score") is not None]
        if len(dets) < THRESHOLDS["FREEZE_CYCLES"]:
            continue
        n_checked += 1
        tail = dets[:THRESHOLDS["FREEZE_CYCLES"]]      # history is newest-first
        mentions = [h.get("total_mentions") for h in hist[:THRESHOLDS["FREEZE_CYCLES"]]
                    if isinstance(h, dict)]
        mentions = [m for m in (mentions or []) if m is not None]
        if max(tail) - min(tail) == 0:
            # NULL CONDITION (board): a frozen score is only a defect if the
            # INPUTS moved. Static inputs -> static score is correct behavior.
            inputs_moved = len(set(mentions)) > 1 if mentions else None
            if inputs_moved:
                out.append(Finding("B.freeze", "FAIL", key,
                    f"Detection identical at {tail[0]} for {len(tail)} cycles while "
                    f"mentions varied {min(mentions)}–{max(mentions)}",
                    gap="score not responding to changing inputs (possible cached "
                        "serve or saturated components)",
                    solution="check INV-1 serve-stored rules + serve_payload freshness "
                             "for this row; inspect component values in the detail; "
                             "report findings to the founder before any scoring change",
                    severity="high", task_class="SCORE_AFFECTING"))
            else:
                out.append(Finding("B.freeze", "INSUFFICIENT", key,
                    f"score static {len(tail)} cycles but inputs static too — no verdict"))
        else:
            vol = statistics.pstdev(tail)
            if vol > THRESHOLDS["HIGH_VOL_STD"]:
                out.append(Finding("B.volatility", "WARN", key,
                    f"per-cycle std {vol:.1f} over last {len(tail)} cycles "
                    f"(range {min(tail)}–{max(tail)})",
                    gap="a score this jumpy is hard to act on",
                    solution="inspect input volume per cycle for this topic; diagnose "
                             "whether a single flapping source drives it",
                    severity="medium"))
            else:
                out.append(Finding("B.volatility", "PASS", key,
                    f"moving normally (range {min(tail)}–{max(tail)}, std {vol:.1f})"))
    out.append(Finding("B.freeze", "PASS" if n_checked else "INSUFFICIENT",
                       "cohort", f"{n_checked} topics had >= {THRESHOLDS['FREEZE_CYCLES']} cycles of history"))
    return out


# ═════════════════════════════ C · SCORE ACCURACY ════════════════════════════
def assess_accuracy(cohort: dict, live: bool) -> list:
    out = []
    if not live:
        out.append(Finding("C.gap_arithmetic", "PASS", "demo", "DEMO synthetic pass"))
        return out
    rows = cohort["topics"]
    bad = []
    for r in rows:
        det, conf = r.get("detection_score"), r.get("confidence_score")
        gap = r.get("heisenberg_gap")
        if det is None or conf is None or gap is None:
            continue
        if abs(abs(float(gap)) - abs(float(det) - float(conf))) > THRESHOLDS["GAP_TOL"]:
            bad.append((r.get("topic_key"), gap, det, conf))
    if bad:
        k, g, dv, cv = bad[0]
        out.append(Finding("C.gap_arithmetic", "FAIL", f"{len(bad)}/{len(rows)} rows",
            f"served gap disagrees with |Det-Conf| (e.g. {k}: gap {g} vs {abs(dv-cv):.1f})",
            gap="the served gap contradicts its own scores",
            solution="verify gap write-time computation on these rows; add the invariant "
                     "to the Scoring Contract checks if absent",
            severity="high", task_class="SCORE_AFFECTING"))
    else:
        out.append(Finding("C.gap_arithmetic", "PASS", f"{len(rows)} rows",
                           "served gap = |Detection-Confidence| within tolerance on every row"))
    # alias-family display sanity (DISPLAY-ONLY lane — per the Chairman ruling)
    try:
        al = http_json(f"{ENGINE}/aliases?status=pending&limit=500")
        pend = al.get("count", 0)
        out.append(Finding("C.alias_families",
                           "PASS" if pend == 0 else "WARN",
                           "alias review queue",
                           f"{pend} pending alias candidates awaiting HUMAN review",
                           gap="" if pend == 0 else
                               "unreviewed fragment families can split one story across rows "
                               "in the DISPLAY (scores stay per-key by ruling)",
                           solution="" if pend == 0 else
                               "founder reviews via GET /aliases (display-only Option A; "
                               "never merged before scoring)",
                           severity="low"))
    except Exception as e:
        out.append(Finding("C.alias_families", "INSUFFICIENT", "alias endpoint", str(e)[:80]))
    return out


def assess_referee_surge(cohort: dict, live: bool) -> list:
    """SURGE-vs-motion (board condition: never fame-level). Wikipedia pageviews,
    free REST, held-out. Shadow check on its first snapshot. Diagnoses only."""
    out = []
    if not live:
        return [Finding("C.referee_surge", "INSUFFICIENT", "demo", "DEMO: referee not simulated")]
    end = datetime.now(timezone.utc).date() - timedelta(days=1)
    start = end - timedelta(days=30)
    fmt = "%Y%m%d"
    corr_pairs = []
    subset = cohort["topics"][:THRESHOLDS["COHORT_REFEREE"]]
    for r in subset:
        disp = (r.get("topic_display") or r.get("topic_key") or "").strip()
        title = urllib.parse.quote(disp.replace(" ", "_"))
        url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
               f"en.wikipedia/all-access/user/{title}/daily/{start.strftime(fmt)}00/{end.strftime(fmt)}00")
        try:
            d = http_json(url, timeout=30)
            views = [it.get("views", 0) for it in d.get("items", [])]
        except Exception:
            out.append(Finding("C.referee_surge", "INSUFFICIENT", disp,
                               "no en-wiki article resolved (fail-open)"))
            continue
        time.sleep(0.3)
        if len(views) < 10:
            out.append(Finding("C.referee_surge", "INSUFFICIENT", disp, "thin pageview history"))
            continue
        med = statistics.median(views[:-3]) or 0
        recent = statistics.fmean(views[-3:])
        surging = med >= 0 and recent >= max(THRESHOLDS["SURGE_FLOOR"],
                                             THRESHOLDS["SURGE_MULT"] * max(med, 1))
        det = r.get("detection_score")
        surge_ratio = recent / max(med, 1)
        if det is not None:
            corr_pairs.append((float(det), surge_ratio))
        if surging and det is not None and det < 55:
            out.append(Finding("C.referee_surge", "WARN", disp,
                f"referee shows a genuine surge (recent {recent:.0f}/day vs median {med:.0f}) "
                f"but Detection reads {det}",
                gap="possible late/muted read on an externally-surging topic "
                    "(motion-vs-motion disagreement, not fame-level)",
                solution="diagnose source coverage (module A) and per-component reads "
                         "for this topic; log for the ledger race — never tune to match "
                         "the referee",
                severity="medium", task_class="SCORE_AFFECTING", held_out_derived=True))
        else:
            out.append(Finding("C.referee_surge", "PASS", disp,
                f"surge-agreement ok (referee ratio {surge_ratio:.1f}x, Detection {det})",
                held_out_derived=True))
    # DRIFT ALARM data point (Economist): rank correlation engine-vs-referee.
    if len(corr_pairs) >= 8:
        def ranks(xs):
            order = sorted(range(len(xs)), key=lambda i: xs[i])
            rk = [0.0] * len(xs)
            for pos, i in enumerate(order):
                rk[i] = pos
            return rk
        ra, rb = ranks([p[0] for p in corr_pairs]), ranks([p[1] for p in corr_pairs])
        n = len(ra)
        rho = 1 - 6 * sum((a - b) ** 2 for a, b in zip(ra, rb)) / (n * (n * n - 1))
        out.append(Finding("C.referee_surge", "PASS", "drift-alarm datapoint",
            f"engine-referee rank correlation rho={rho:.2f} on n={n} (tracked across "
            f"snapshots; a RISING trend = converging on a lagging fame index — alarm)",
            held_out_derived=True))
    return out


# ═════════════════════════════ D · TREND LIFECYCLE (WARN-only v1) ════════════
def assess_lifecycle(cohort: dict, live: bool) -> list:
    """Quantile-referenced, abs-floored, RECURRENT-aware. WARN-only until it beats
    the STEADY-monkey null across 3 snapshots (board condition)."""
    out = []
    if not live:
        return [Finding("D.lifecycle", "INSUFFICIENT", "demo", "DEMO: lifecycle not simulated")]
    # v1 uses the engine's own score_history shape as the motion series (external
    # referee series at scale is deferred; referee surge above covers the outside view)
    for r in cohort["topics"][:15]:
        key = r.get("topic_key")
        try:
            d = http_json(f"{ENGINE}/scores/{urllib.parse.quote(key)}")
        except Exception:
            continue
        time.sleep(0.2)
        hist = list(reversed(d.get("score_history") or []))   # oldest -> newest
        vals = [h.get("detection_score") for h in hist if h.get("detection_score") is not None]
        if len(vals) < 8:
            out.append(Finding("D.lifecycle", "INSUFFICIENT", key, "under 8 cycles of history"))
            continue
        ref = sorted(vals)[int(THRESHOLDS["LIFE_REF_QUANTILE"] * (len(vals) - 1))]  # p90, not max
        recent = statistics.fmean(vals[-3:])
        prior = statistics.fmean(vals[-8:-3])
        if ref <= 0:
            phase = "DORMANT"
        elif recent >= 0.9 * ref and recent > prior:
            phase = "PEAKING"
        elif recent > prior * 1.25:
            phase = "RISING"
        elif recent < THRESHOLDS["ENDED_RATIO"] * ref:
            phase = "ENDED?"
        elif recent < THRESHOLDS["FADE_RATIO"] * ref or recent < prior * 0.75:
            phase = "FADING"
        else:
            phase = "STEADY"
        stage = (r.get("signal_stage") or "?").upper()
        if phase in ("ENDED?", "FADING") and stage in ("BREAKOUT", "STRONG"):
            out.append(Finding("D.lifecycle", "WARN", key,
                f"internal motion {phase} (recent {recent:.0f} vs p90 {ref:.0f}) while "
                f"stage still {stage}",
                gap="possible stale-active read; NOTE bursty topics can re-surge "
                    "(RECURRENT) — treat as a look, not a verdict",
                solution="compare against the referee surge check + freshness inputs; "
                         "no stage rule change without founder + backtest",
                severity="low"))
        else:
            out.append(Finding("D.lifecycle", "PASS", key, f"{phase} — stage {stage} consistent"))
    return out


# ═════════════════════════════ E · OUTSIDE RECALL ════════════════════════════
def assess_outside(cohort: dict, live: bool) -> list:
    out = []
    if not live:
        return [Finding("E.trending_recall", "PASS", "demo", "DEMO synthetic pass")]
    # 1) Google daily-trending RSS (free) — do today's top external topics exist in our feed?
    try:
        xml = http_text("https://trends.google.com/trending/rss?geo=US", timeout=30)
        titles = re.findall(r"<title>(.*?)</title>", xml)[1:THRESHOLDS["RECALL_TOP"] + 1]
        served = " ".join((r.get("topic_display") or "") + " " + (r.get("topic_key") or "")
                          for r in cohort["topics"]).lower()
        # broaden with a larger served sample
        misses, hits = [], []
        for t in titles:
            words = [w for w in re.split(r"\W+", t.lower()) if len(w) > 3]
            if words and any(w in served for w in words):
                hits.append(t)
            else:
                misses.append(t)
        denom = len(titles)
        if denom >= THRESHOLDS["MIN_N"]:
            status = "PASS" if len(misses) <= denom * 0.4 else "WARN"
            out.append(Finding("E.trending_recall", status, "google daily trending",
                f"{len(hits)}/{denom} of today's top external trends have a matching served "
                f"topic (misses: {', '.join(misses[:4])[:90]})",
                gap="" if status == "PASS" else
                    "external top-trending items missing from the served feed — recall gap",
                solution="" if status == "PASS" else
                    "check the discovery collectors for the missed terms; candidates for "
                    "the catch-all/lexicon worklist",
                severity="medium" if status == "WARN" else "low"))
        else:
            out.append(Finding("E.trending_recall", "INSUFFICIENT", "google daily trending",
                               f"only {denom} items parsed from the RSS"))
    except Exception as e:
        out.append(Finding("E.trending_recall", "INSUFFICIENT", "google daily trending",
                           f"fetch failed: {str(e)[:60]}"))
    # 2) crypto movers agreement — our own served feed (free)
    try:
        c = http_json(f"{ENGINE}/crypto")
        coins = c.get("coins") or c.get("results") or []
        movers = [x for x in coins
                  if abs(float(x.get("change_7d_pct") or 0)) >= 20]
        flagged = [x for x in movers
                   if (x.get("tier") or x.get("intensity_tier") or "").upper()
                   not in ("DORMANT", "")]
        denom = len(movers)
        if denom >= 1:
            out.append(Finding("E.crypto_agreement",
                "PASS" if len(flagged) >= max(1, denom // 2) else "WARN",
                "crypto 20% movers",
                f"{len(flagged)}/{denom} coins moving >=20% (7d) carry a non-dormant "
                f"money-movement tier",
                gap="" if len(flagged) >= max(1, denom // 2) else
                    "big realized moves with dormant reads — check the crypto ledger lens",
                solution="" if len(flagged) >= max(1, denom // 2) else
                    "cross-check /crypto/accuracy resolutions for these coins",
                severity="low"))
        else:
            out.append(Finding("E.crypto_agreement", "INSUFFICIENT", "crypto movers",
                               "no 20% movers this week (nothing to grade)"))
    except Exception as e:
        out.append(Finding("E.crypto_agreement", "INSUFFICIENT", "crypto feed", str(e)[:60]))
    return out


# ═════════════════════════════ GRADE + REPORT ════════════════════════════════
SEV_W = {"high": 3.0, "medium": 2.0, "low": 1.0}

def grade(findings: list) -> dict:
    mods = {}
    for f in findings:
        mod = CHECK_MANIFEST.get(f.check, {}).get("module", "?")
        mods.setdefault(mod, []).append(f)
    modules, floors = {}, []
    for mod, fs in mods.items():
        graded = [f for f in fs if f.status in ("PASS", "FAIL", "WARN") and not f.shadow]
        if not graded:
            modules[mod] = {"grade": "N/A", "passed": 0, "graded": 0, "insufficient":
                            sum(1 for f in fs if f.status == "INSUFFICIENT")}
            continue
        wsum = sum(SEV_W[f.severity] for f in graded)
        wbad = sum(SEV_W[f.severity] * (1.0 if f.status == "FAIL" else 0.5 if f.status == "WARN" else 0)
                   for f in graded)
        score = 1 - (wbad / wsum) if wsum else 0
        letter = ("A" if score >= 0.9 else "B" if score >= 0.75 else
                  "C" if score >= 0.5 else "D" if score >= 0.25 else "F")
        floors.append(score)
        modules[mod] = {"grade": letter,
                        "passed": sum(1 for f in graded if f.status == "PASS"),
                        "graded": len(graded),
                        "insufficient": sum(1 for f in fs if f.status == "INSUFFICIENT"),
                        "severity_weighted_score": round(score, 3)}
    overall = round(100 * min(floors), 1) if floors else 0   # worst-module FLOOR (board)
    return modules, overall


def run(live: bool) -> dict:
    now = datetime.now(timezone.utc)
    findings = []
    findings += assess_sources(live)
    cohort = build_cohort(live)
    findings += assess_movement(cohort, live)
    findings += assess_accuracy(cohort, live)
    findings += assess_referee_surge(cohort, live)
    findings += assess_lifecycle(cohort, live)
    findings += assess_outside(cohort, live)
    findings = [f.finalize() for f in findings]

    modules, floor_pct = grade(findings)
    graded = [f for f in findings if f.status in ("PASS", "FAIL", "WARN") and not f.shadow]
    pass_pct = round(100 * sum(1 for f in graded if f.status == "PASS") / len(graded), 1) if graded else 0

    ledger_headline = {}
    if live:
        try:
            L = http_json(f"{ENGINE}/accuracy/ledger")
            ledger_headline = {
                "tracked_race_hit_rate_pct": L.get("trackedRaceHitRate"),
                "tracked_race_sample": L.get("trackedRaceSample"),
                "blended_hit_rate_pct": L.get("hitRate"),
                "epoch_boundary": L.get("epochBoundary"),
                "by_epoch": L.get("byEpoch"),
            }
        except Exception:
            ledger_headline = {"error": "ledger fetch failed"}

    work_queue = sorted([f for f in findings if f.status in ("FAIL", "WARN")],
                        key=lambda f: ({"high": 0, "medium": 1, "low": 2}[f.severity],
                                       f.task_class != "SCORE_AFFECTING"))
    return {
        "run_at": now.isoformat(timespec="seconds"),
        "param_version": PARAM_VERSION,
        "mode": "LIVE" if live else "DEMO — SYNTHETIC DATA (never act on this)",
        # BOARD ANALYSIS REQUIREMENT (Chairman directive 2026-07-17):
        "status": "UNVERIFIED_PENDING_BOARD_REVIEW",
        "board_gate": ("REQUIRED before any finding teaches or is implemented: the advisory "
                       "board independently critiques these findings, cross-checks them "
                       "against freshly-obtained outside data (current trending items, "
                       "market/crypto movers), and verifies or refutes each. The CHAIRMAN "
                       "has final say before any implementation."),
        "accuracy_headline": {"note": "THE accuracy number is the held-out ledger, not this tool",
                              **ledger_headline},
        "operational_check_pass_pct": pass_pct,
        "worst_module_floor_pct": floor_pct,
        "internal_only": "never publish these percentages externally (catch-all-% rule)",
        "modules": modules,
        "cohort_spec": cohort["spec"],
        "findings": [asdict(f) for f in findings],
        "work_queue": [asdict(f) for f in work_queue],
    }


def render_md(r: dict) -> str:
    L = []
    L.append(f"# SCORING ASSESSOR SNAPSHOT — {r['run_at']}")
    L.append("")
    L.append(f"**mode:** {r['mode']} · **param:** {r['param_version']} · "
             f"**status:** {r['status']}")
    L.append("")
    L.append(f"> **BOARD GATE:** {r['board_gate']}")
    L.append("")
    ah = r["accuracy_headline"]
    L.append(f"**THE ACCURACY NUMBER (held-out ledger):** tracked-race "
             f"{ah.get('tracked_race_hit_rate_pct')}% (n={ah.get('tracked_race_sample')}) · "
             f"blended {ah.get('blended_hit_rate_pct')}% · epoch-segmented at {ah.get('epoch_boundary')}")
    L.append("")
    L.append(f"Internal operational checks: pass {r['operational_check_pass_pct']}% · "
             f"worst-module floor {r['worst_module_floor_pct']}% (internal-only; "
             f"cohort: {r['cohort_spec']})")
    L.append("")
    L.append("| module | grade | passed/graded | insufficient |")
    L.append("|---|---|---|---|")
    for mod, m in r["modules"].items():
        L.append(f"| {mod} | {m['grade']} | {m['passed']}/{m['graded']} | {m['insufficient']} |")
    L.append("")
    L.append("## Work queue (UNVERIFIED — pending board cross-check + Chairman ruling)")
    for i, f in enumerate(r["work_queue"], 1):
        L.append(f"{i}. [{f['severity'].upper()} · {f['task_class']}] **{f['subject']}** — {f['evidence']}")
        if f["gap"]:
            L.append(f"   - gap: {f['gap']}")
            L.append(f"   - diagnostic: {f['solution']}")
        if f["held_out_derived"]:
            L.append("   - held_out_derived: true (referee diagnoses; never tunes)")
    if not r["work_queue"]:
        L.append("(empty)")
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="synthetic, watermarked run")
    args = ap.parse_args()
    live = not args.demo
    report = run(live)
    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    suffix = "DEMO." if not live else ""
    jpath = os.path.join(OUT_DIR, f"ASSESSOR_{stamp}.{suffix}json")
    mpath = os.path.join(OUT_DIR, f"ASSESSOR_{stamp}.{suffix}md")
    with open(jpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=1)
    with open(mpath, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(report))
    print(render_md(report))
    print(f"\nsnapshot -> {jpath}")
