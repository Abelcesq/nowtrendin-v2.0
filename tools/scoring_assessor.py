# -*- coding: utf-8 -*-
"""
scoring_assessor.py — v2.1 (board-gate fixes, Chairman-ruled 2026-07-18)
========================================================================
v2.1 (per BOARD_assessor-2026-07-17.md + the Chairman's "proceed" ruling; the
manifest change bumps param_version and STARTS A NEW COMPARABLE SERIES):
  * B.volatility is SHAPE-AWARE: sign-flip discriminator separates ALTERNATOR
    (real flap candidate -> WARN) from burst step/cliff dynamics (expected for
    bursty attention -> PASS with the shape named). Threshold is the max of the
    registered floor and the cohort's own p90 dispersion. Raw series stored in
    the finding. (The 2026-07-18 diagnostic: 17/19 flagged topics were
    burst-plateau-cliff, only 1 true alternator — see VOLATILITY_DIAG_2026-07-18.md.)
  * Wikipedia referee TITLE RESOLUTION fixed (lowercase common-noun keys failed
    silently as "thin pageview history") via MediaWiki opensearch fallback; every
    INSUFFICIENT now carries a truthful CAUSE CODE (resolution_failed /
    fetch_error / thin_history / mentions_unavailable ...).
  * E.trending_recall rebuilt: full-feed scan (paginated, capped + denominator
    pinned in the evidence), phrase/single-topic token matching (the substring-
    blob matcher produced false hits), "X vs Y" matchup class registered and
    excluded, traffic floor registered, and misses only count when the
    independent Wikipedia referee confirms attention actually arrived.
  * Letter grades suppressed below MIN_GRADED_N (an "A" on 2/20 is not a grade).
  * Ledger headline now carries the Wilson 95% interval on the tracked-race rate
    and the 0-false-positives-by-construction disclosure (365d patience window).
  * Engine–referee rank correlation persisted append-only to
    audits/assessor/REFEREE_CORR_SERIES.json (the drift alarm needs a baseline);
    3 consecutive rises -> WARN.
  * D.lifecycle WARNs require a non-INSUFFICIENT referee for the topic (an
    instrument-blind referee must not leave lifecycle looks un-refereeable).
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
# ASSESSOR_OUT_DIR override (v2.1.2): verification runs write to a scratch dir so a
# same-day BOARD_VERIFIED snapshot in the repo is never clobbered by a fresh
# UNVERIFIED run (the 2026-07-19 stamped-snapshot collision).
OUT_DIR = os.getenv("ASSESSOR_OUT_DIR") or os.path.join(REPO, "audits", "assessor")

# ── CHECK MANIFEST (registered; hash -> param_version; SHADOW = excluded from %) ──
# Board condition (Economist P2): every check states its NULL HYPOTHESIS and its
# threshold PROVENANCE here, in the manifest, so the hash covers them.
CHECK_MANIFEST = {
    "A.freshness":        {"module": "A_SOURCES",   "shadow": False,
        "null": "collectors report HEALTHY; DEFERRED sources are decisions, not failures"},
    "A.silent_absence":   {"module": "A_SOURCES",   "shadow": False,
        "null": "no configured source silently absent"},
    "B.freeze":           {"module": "B_MOVEMENT",  "shadow": False,
        "null": "a static score on static inputs is CORRECT behavior (no verdict)"},
    "B.volatility":       {"module": "B_MOVEMENT",  "shadow": False,
        "null": "bursty attention IS volatile: monotone surge steps and post-burst "
                "cliff rolloff are EXPECTED dynamics, not defects. Only ALTERNATING "
                "(sawtooth) movement above the dispersion threshold is a flap candidate.",
        "provenance": "threshold = max(HIGH_VOL_STD floor, cohort p90 dispersion); "
                      "shape rule from VOLATILITY_DIAG_2026-07-18 (17/19 flags were bursts)"},
    "C.gap_arithmetic":   {"module": "C_ACCURACY",  "shadow": False,
        "null": "served gap equals |Detection-Confidence| within GAP_TOL"},
    "C.alias_families":   {"module": "C_ACCURACY",  "shadow": False,
        "null": "alias queue pending is normal; only humans merge (display-only ruling)"},
    "C.referee_surge":    {"module": "C_ACCURACY",  "shadow": True,   # shadow: probation
        "null": "engine Detection and the held-out pageview referee agree on SURGE "
                "(motion), never graded on fame level",
        "provenance": "SURGE_MULT/SURGE_FLOOR follow the referee_wikipedia convention"},
    "D.lifecycle":        {"module": "D_LIFECYCLE", "shadow": True,   # WARN-only until it beats the null
        "null": "STEADY-monkey: a bursty topic's dip is not an ending (RECURRENT); "
                "no WARN without a non-INSUFFICIENT referee for the same topic"},
    "E.trending_recall":  {"module": "E_OUTSIDE",   "shadow": False,
        "null": "most daily-trending queries are ephemeral noise (Malkiel); a miss "
                "counts only when the independent referee confirms attention arrived; "
                "scheduled matchups (X vs Y) are excluded by class",
        "provenance": "RECALL_TRAFFIC_FLOOR registered 2026-07-18 (board condition); "
                      "coverage gauge ONLY — never an accuracy KPI (catch-all-% rule)"},
    "E.crypto_agreement": {"module": "E_OUTSIDE",   "shadow": True,
        "null": "no 20% movers = nothing to grade (honest INSUFFICIENT)"},
    # v2.1.2 (board R3 patch, Chairman-ruled 2026-07-19):
    "B.dup_cycles":       {"module": "B_MOVEMENT",  "shadow": True,
        "null": "one scoring row per cycle slot; duplicate same-hour rows shorten the "
                "12-row baseline window in TIME and can transiently move the median "
                "(the britain 07-18T10 glitch suspect)",
        "provenance": "Executioner finding, BOARD_estimator-fdm-snapshot2_2026-07-19"},
    # v2.1.1 shadow checks (board Q1/Q2 session, Chairman-ruled item 7, 2026-07-18):
    "B.asymmetry":        {"module": "B_MOVEMENT",  "shadow": True,
        "null": "Kindleberger: attention decay is asymmetric (down faster than up) but "
                "CONTINUOUS. Instant transitions BOTH ways, quantized to cycle boundaries, "
                "is the standing signature of a measurement-window/estimator artifact — "
                "not of the attention process.",
        "provenance": "Economist prescription 4, BOARD_q1q2-cliff-plateau_2026-07-18"},
    "C.saturation_gauge": {"module": "C_ACCURACY",  "shadow": True,
        "null": "Bernstein: variance destroyed by clamps is measurement error you are "
                "choosing not to see. Top-decile topics pinned at caps/floors cannot be "
                "ranked where clients look hardest.",
        "provenance": "Economist prescription 5, BOARD_q1q2-cliff-plateau_2026-07-18"},
}
THRESHOLDS = {
    "FREEZE_CYCLES": 6, "HIGH_VOL_STD": 12.0, "GAP_TOL": 0.6,
    "SURGE_MULT": 3.0, "SURGE_FLOOR": 200,          # referee_wikipedia convention
    "LIFE_REF_QUANTILE": 0.9, "LIFE_ABS_FLOOR": 200,
    "FADE_RATIO": 0.5, "ENDED_RATIO": 0.25, "MIN_N": 5,
    "COHORT_MOVEMENT": 60, "COHORT_REFEREE": 20, "RECALL_TOP": 10,
    # v2.1 (Chairman-ruled 2026-07-18):
    "VOL_FLIPS_MIN": 3,          # sign-flips >= this = ALTERNATOR (flap candidate)
    "VOL_DIFF_MIN": 2.0,         # |cycle diff| below this is noise, not a flip leg
    "VOL_PCTL": 0.9,             # dispersion threshold percentile over the cohort
    "MIN_GRADED_N": 5,           # no letter grade below this many graded checks
    "RECALL_TRAFFIC_FLOOR": 10000,   # grade only external items >= this approx_traffic
    "RECALL_SCAN_CAP": 4000,     # full-corpus scan (board R3 condition 2026-07-19: was
                                 # 2000/3353 — a miss in the tail was structurally invisible)
    # v2.1.1 (board item 7):
    "ASYM_STEP": 30.0,           # single-cycle step >= this counts as an instant transition
                                 # PROVENANCE (registered 2026-07-19): matches the replay's
                                 # |Δdet|>=30 transition definition (MEDIAN_REPLAY_2026-07-18)
    "SAT_PIN": 99.5,             # detection/confidence >= this counts as cap-pinned
    "SAT_TOP_DECILE_WARN": 0.2,  # shadow-WARN when >20% of the top decile is pinned
    # v2.1.2 (board R3 patch, 2026-07-19):
    "W_MOVE_MIN": 0.3,           # blend-weight move >= this at a big-delta cycle = the
                                 # confirmed median-w-flip mechanism signature
}
# RECALL_TRAFFIC_FLOOR provenance (registered 2026-07-19): board condition "grade only
# the tail that matters" (Economist, Taleb/Extremistan) — 10k chosen as the smallest
# Google approx_traffic tier that excludes scheduled-fixture/ephemera days observed
# 2026-07-17..19 (all items 500+–2000+). Change = new comparable series.
_manifest_hash = hashlib.sha256(
    json.dumps({"checks": CHECK_MANIFEST, "thresholds": THRESHOLDS},
               sort_keys=True).encode()).hexdigest()[:10]
PARAM_VERSION = f"assessor-v2.1.2.{_manifest_hash}"  # v2.1.2 = board R3 patch (Chairman-ruled
                                                     # 2026-07-19): formula-arguments freeze null,
                                                     # known-mechanism ruling tags, dup-cycle
                                                     # hygiene, flip-gated burst label

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
    cause: str = ""            # truthful cause code on INSUFFICIENT (board N1/N3:
                               # resolution_failed | fetch_error | thin_history |
                               # mentions_unavailable | referee_unavailable | ...)

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


# ── Wikipedia referee resolver (v2.1 — board finding N1: the blind referee) ──
# The v2 path built the pageviews URL straight from topic_display; lowercase
# common-noun keys ("spain", "japan", "fifa") 404 on the case-sensitive REST API
# and the failure was mislabeled "thin pageview history". Resolution order:
# as-is -> Title Case -> MediaWiki opensearch (free, no key). Returns
# (views_list, resolved_title, cause) — cause is "" on success, else a truthful code.
def _wiki_resolve_title(name: str) -> str | None:
    q = urllib.parse.quote(name)
    url = (f"https://en.wikipedia.org/w/api.php?action=opensearch&search={q}"
           f"&limit=1&namespace=0&format=json")
    try:
        d = http_json(url, timeout=20)
        titles = d[1] if isinstance(d, list) and len(d) > 1 else []
        return titles[0] if titles else None
    except Exception:
        return None


def _wiki_daily_series(name: str, days: int = 30):
    end = datetime.now(timezone.utc).date() - timedelta(days=1)
    start = end - timedelta(days=days)
    fmt = "%Y%m%d"
    candidates = [name.replace(" ", "_")]
    tc = name.title().replace(" ", "_")
    if tc not in candidates:
        candidates.append(tc)
    last_cause = "resolution_failed"
    for attempt, cand in enumerate(candidates + ["__OPENSEARCH__"]):
        if cand == "__OPENSEARCH__":
            resolved = _wiki_resolve_title(name)
            if not resolved:
                return [], None, "resolution_failed"
            cand = resolved.replace(" ", "_")
        title = urllib.parse.quote(cand, safe="")
        url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
               f"en.wikipedia/all-access/user/{title}/daily/"
               f"{start.strftime(fmt)}00/{end.strftime(fmt)}00")
        try:
            d = http_json(url, timeout=30)
            views = [it.get("views", 0) for it in d.get("items", [])]
            if len(views) >= 10:
                return views, cand, ""
            last_cause = f"thin_history(n={len(views)})"
        except urllib.error.HTTPError as e:
            last_cause = "resolution_failed" if e.code == 404 else f"fetch_error({e.code})"
        except Exception as e:
            last_cause = f"fetch_error({type(e).__name__})"
        time.sleep(0.3)
    return [], None, last_cause


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
    # PASS 1 — collect every topic's window (so the threshold can be derived from
    # the cohort's OWN dispersion, board condition: no universal constant across strata).
    # v2.1.2: rows carry the BLEND ARGUMENTS (w, magnitude, n_mainstream, M/I/P) so the
    # freeze null tests inputs-vs-inputs, and rows are DEDUPED per cycle slot (hour) —
    # duplicate same-hour rows are counted for the B.dup_cycles hygiene check.
    windows, n_checked = [], 0
    dup_examples, dup_total = [], 0
    for row in cohort["topics"][:THRESHOLDS["COHORT_MOVEMENT"]]:
        key = row.get("topic_key")
        try:
            d = http_json(f"{ENGINE}/scores/{urllib.parse.quote(key)}")
        except Exception:
            out.append(Finding("B.freeze", "INSUFFICIENT", key, "detail fetch failed",
                               cause="fetch_error"))
            continue
        time.sleep(0.25)
        hist = d.get("score_history") or []
        rows6, seen_slots, dups_here = [], set(), 0
        for h in hist:                                  # newest-first
            if not isinstance(h, dict) or h.get("detection_score") is None:
                continue
            slot = str(h.get("scored_at") or "")[:13]   # hour bucket = cycle slot
            if slot in seen_slots:
                dups_here += 1
                continue                                # dedupe: keep the newest per slot
            seen_slots.add(slot)
            rows6.append({
                "ts": slot,
                "det": h.get("detection_score"),
                "w": h.get("mainstream_ratio"),
                "pathway": h.get("detection_pathway"),
                "mag": h.get("attention_magnitude"),
                "nplat": h.get("n_mainstream_platforms"),
                "mentions": h.get("total_mentions"),
                "M": h.get("platform_diversity"),
                "I": h.get("inertia_score"),
                "P": h.get("persistence_score"),
            })
            if len(rows6) >= THRESHOLDS["FREEZE_CYCLES"]:
                break
        if dups_here:
            dup_total += dups_here
            if len(dup_examples) < 6:
                dup_examples.append(f"{key}(+{dups_here})")
        if len(rows6) < THRESHOLDS["FREEZE_CYCLES"]:
            continue
        n_checked += 1
        windows.append((key, rows6))
    stds = sorted(statistics.pstdev([r["det"] for r in rows6])
                  for _, rows6 in windows
                  if max(r["det"] for r in rows6) - min(r["det"] for r in rows6) > 0)
    p90_std = stds[int(THRESHOLDS["VOL_PCTL"] * (len(stds) - 1))] if stds else 0.0
    vol_threshold = max(THRESHOLDS["HIGH_VOL_STD"], p90_std)

    # Known-mechanism signature (board-confirmed 2026-07-18, ruled 2026-07-19): a big
    # single-cycle |Δdet| whose cycle also moved the blend weight w (or flipped the
    # pathway) is the median-of-12 w-flip mechanism — a TRACKED instance citing the
    # ruling, never a fresh page-one alarm.
    _MECH_RULING = "2026-07-18-median-w-flip"
    def _mechanism_cycles(series_rows):
        hits = 0
        for i in range(1, len(series_rows)):
            a, b = series_rows[i - 1], series_rows[i]
            if a["det"] is None or b["det"] is None:
                continue
            if abs(b["det"] - a["det"]) >= THRESHOLDS["ASYM_STEP"]:
                wa, wb = a.get("w"), b.get("w")
                w_moved = (wa is not None and wb is not None
                           and abs(float(wb) - float(wa)) >= THRESHOLDS["W_MOVE_MIN"])
                if w_moved or (a.get("pathway") != b.get("pathway")):
                    hits += 1
        return hits

    # PASS 2 — classify. SHAPE RULE (v2.1) + v2.1.2 formula-arguments freeze null,
    # known-mechanism tagging, and the flip-gated burst label.
    for key, rows6 in windows:
        tail = [r["det"] for r in rows6]               # newest-first
        series_rows = list(reversed(rows6))            # oldest -> newest
        series = [r["det"] for r in series_rows]
        mentions = [r["mentions"] for r in rows6 if r["mentions"] is not None]
        if max(tail) - min(tail) == 0:
            # v2.1.2 NULL (board R2 ruling): a freeze is judged against the FORMULA'S
            # ARGUMENTS (w, magnitude, n_mainstream, M/I/P), never against raw mention
            # counts (not an input of the w=1.0 pathway — the final_del_mundial lesson).
            def _static(field):
                vals = [r.get(field) for r in rows6 if r.get(field) is not None]
                return (len(set(round(float(v), 2) for v in vals)) <= 1) if vals else None
            args = {f: _static(f) for f in ("w", "mag", "nplat", "M", "I", "P")}
            known = [f for f, s in args.items() if s is not None]
            if known and all(args[f] for f in known):
                mnote = (f"; mentions varied {min(mentions)}–{max(mentions)} (context only "
                         f"— not a formula argument)") if mentions and len(set(mentions)) > 1 else ""
                out.append(Finding("B.freeze", "INSUFFICIENT", key,
                    f"score static {len(tail)} cycles with ALL formula arguments static "
                    f"({', '.join(known)}) — deterministic recompute, expected behavior"
                    f"{mnote}",
                    cause="formula_args_static"))
            elif known:
                moved = [f for f in known if not args[f]]
                # Saturation-awareness (board R2 condition): platform-count movement
                # entirely ABOVE the breadth saturation knee (>=4) while w is pinned at
                # 1.0 cannot reach the formula — the derived breadth term is 1.0
                # throughout. Not a defect; the argument moved in a dead zone.
                nplats = [r.get("nplat") for r in rows6 if r.get("nplat") is not None]
                ws = [r.get("w") for r in rows6 if r.get("w") is not None]
                sat_dead_zone = (moved == ["nplat"] and nplats and min(nplats) >= 4
                                 and ws and all(abs(float(w) - 1.0) < 0.01 for w in ws))
                if sat_dead_zone:
                    out.append(Finding("B.freeze", "INSUFFICIENT", key,
                        f"score static {len(tail)} cycles; only nplat moved "
                        f"({min(nplats):g}–{max(nplats):g}) — entirely above the breadth "
                        f"saturation knee (>=4) with w pinned 1.0, so the movement cannot "
                        f"reach the formula (saturation dead zone; expected)",
                        cause="formula_args_static"))
                else:
                    out.append(Finding("B.freeze", "FAIL", key,
                        f"Detection identical at {tail[0]} for {len(tail)} cycles while "
                        f"formula arguments MOVED ({', '.join(moved)})",
                        gap="score not responding to its own moving inputs",
                        solution="inspect the blend wiring for this topic; report to the "
                                 "founder before any scoring change",
                        severity="high", task_class="SCORE_AFFECTING"))
            else:
                out.append(Finding("B.freeze", "INSUFFICIENT", key,
                    f"score static {len(tail)} cycles; no formula-argument fields "
                    f"served for this topic — null untestable",
                    cause="args_unavailable"))
            continue
        vol = statistics.pstdev(tail)
        raw_diffs = [series[i + 1] - series[i] for i in range(len(series) - 1)]
        diffs = [d if abs(d) >= THRESHOLDS["VOL_DIFF_MIN"] else 0 for d in raw_diffs]
        moves = [d for d in diffs if d != 0]
        flips = sum(1 for i in range(len(moves) - 1)
                    if (moves[i] > 0) != (moves[i + 1] > 0))
        shape = ("ALTERNATOR" if flips >= THRESHOLDS["VOL_FLIPS_MIN"]
                 else "burst-step" if vol > THRESHOLDS["HIGH_VOL_STD"]
                 else "normal")
        sr = ",".join(f"{v:g}" for v in series)
        mech = _mechanism_cycles(series_rows)
        mech_note = (f" — KNOWN MECHANISM ({mech} transition(s) coincide with the blend "
                     f"weight/pathway moving; board {_MECH_RULING}); tracked instance, "
                     f"not a new alarm") if mech else ""
        if shape == "ALTERNATOR" and vol > vol_threshold:
            f = Finding("B.volatility", "WARN", key,
                f"ALTERNATING movement: {flips} sign-flips, per-cycle std {vol:.1f} "
                f"over {len(tail)} cycles (threshold {vol_threshold:.1f} = cohort p90; "
                f"series oldest->newest: {sr}){mech_note}",
                gap=("boundary flap of the confirmed w-flip mechanism — evidence for "
                     "the held estimator item" if mech else
                     "score swings exceed plausible attention dynamics — sawtooth "
                     "alternation is a flap candidate, not a burst"),
                solution="hold for the estimator work (board D1); no change outside "
                         "its gates" if mech else
                         "verify input integrity per cycle for this topic — diagnose only",
                severity="low" if mech else "medium")
            if mech:
                f.ruling_id = _MECH_RULING
            out.append(f)
        elif shape == "burst-step":
            # v2.1.2 flip-gate (Challenger): "monotone" only when flips == 0.
            label = ("monotone step/cliff, expected for bursty attention" if flips == 0
                     else f"large-dispersion series with {flips} flip(s) — NOT monotone")
            out.append(Finding("B.volatility", "PASS", key,
                f"burst dynamics (std {vol:.1f}, {flips} flips, range "
                f"{min(tail):g}–{max(tail):g}; series: {sr}) — {label}{mech_note}",
                ruling_id=_MECH_RULING if mech else ""))
        elif vol < 1.0:
            out.append(Finding("B.volatility", "PASS", key,
                f"near-static (std {vol:.1f}, range {min(tail):g}–{max(tail):g}) — "
                f"see B.freeze null condition; NOT asserted as 'moving normally'"))
        else:
            out.append(Finding("B.volatility", "PASS", key,
                f"within normal dispersion (std {vol:.1f}, range "
                f"{min(tail):g}–{max(tail):g}, {flips} flips)"))
    out.append(Finding("B.freeze", "PASS" if n_checked else "INSUFFICIENT",
                       "cohort", f"{n_checked} topics had >= {THRESHOLDS['FREEZE_CYCLES']} cycles of history"))
    # B.dup_cycles (SHADOW, v2.1.2): duplicate same-hour rows found while collecting.
    out.append(Finding("B.dup_cycles",
        "WARN" if dup_total else "PASS",
        "cycle-slot hygiene",
        (f"{dup_total} duplicate same-hour history rows across the cohort "
         f"(e.g. {', '.join(dup_examples)}) — deduped before analysis here, but they "
         f"shorten the engine's 12-row baseline window in time" if dup_total else
         f"no duplicate cycle-slot rows in the cohort's served history"),
        gap="" if not dup_total else
            "double-scored cycles distort the median baseline (britain-glitch class)",
        solution="" if not dup_total else
            "read-only dedup diagnostic first (board D2); any engine-side dedup is a "
            "query-level fix, never a row deletion",
        severity="low"))

    # B.asymmetry (SHADOW — Kindleberger audit, board item 7): instant transitions in
    # BOTH directions inside one window = window/estimator-artifact signature. Genuine
    # attention may crash fast (revulsion) — but it does not also ARRIVE in one cycle.
    inst_up = inst_down = both = 0
    for key, rows6 in windows:
        series = [r["det"] for r in reversed(rows6)]
        diffs = [series[i + 1] - series[i] for i in range(len(series) - 1)]
        up = max(diffs) if diffs else 0
        dn = min(diffs) if diffs else 0
        u = up >= THRESHOLDS["ASYM_STEP"]
        d = -dn >= THRESHOLDS["ASYM_STEP"]
        inst_up += bool(u); inst_down += bool(d)
        if u and d:
            both += 1
            out.append(Finding("B.asymmetry", "WARN", key,
                f"instant transitions BOTH ways in one window (max up {up:.1f}, max down "
                f"{dn:.1f} in single cycles) — artifact signature, not attention dynamics",
                gap="quantized bistability: the estimator, not the phenomenon, is moving",
                solution="hold for the cohort replay verification (board Q1/Q2 item 3); "
                         "no estimator change without founder + backtest (item 6 HELD)",
                severity="low"))
    out.append(Finding("B.asymmetry", "PASS", "cohort asymmetry profile",
        f"{inst_up} topics with instant up-steps, {inst_down} with instant down-steps, "
        f"{both} with BOTH in one window (n={len(windows)}; step floor "
        f"{THRESHOLDS['ASYM_STEP']})"))
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

    # C.saturation_gauge (SHADOW — Bernstein gauge, board item 7): share of the
    # top decile pinned at caps/floors. Pinned scores cannot rank the leaders.
    dets = sorted((r for r in rows if r.get("detection_score") is not None),
                  key=lambda r: -float(r["detection_score"]))
    top = dets[:max(1, len(dets) // 10)]
    pinned = [r["topic_key"] for r in top
              if float(r.get("detection_score") or 0) >= THRESHOLDS["SAT_PIN"]
              or float(r.get("confidence_score") or 0) >= THRESHOLDS["SAT_PIN"]]
    ratio = len(pinned) / len(top) if top else 0
    out.append(Finding("C.saturation_gauge",
        "WARN" if ratio > THRESHOLDS["SAT_TOP_DECILE_WARN"] else "PASS",
        "top-decile cap pinning",
        f"{len(pinned)}/{len(top)} top-decile topics at >= {THRESHOLDS['SAT_PIN']} "
        f"({', '.join(pinned[:5])})" if pinned else
        f"0/{len(top)} top-decile topics pinned at caps",
        gap="" if ratio <= THRESHOLDS["SAT_TOP_DECILE_WARN"] else
            "ranking resolution destroyed where clients look hardest (cap saturation)",
        solution="" if ratio <= THRESHOLDS["SAT_TOP_DECILE_WARN"] else
            "quantify the flat segment over stored history before any curve change "
            "(SCORE_AFFECTING; founder + backtest)",
        severity="low"))
    return out


def assess_referee_surge(cohort: dict, live: bool) -> list:
    """SURGE-vs-motion (board condition: never fame-level). Wikipedia pageviews,
    free REST, held-out. Shadow check on its first snapshot. Diagnoses only."""
    out = []
    if not live:
        return [Finding("C.referee_surge", "INSUFFICIENT", "demo", "DEMO: referee not simulated")]
    corr_pairs = []
    subset = cohort["topics"][:THRESHOLDS["COHORT_REFEREE"]]
    for r in subset:
        disp = (r.get("topic_display") or r.get("topic_key") or "").strip()
        views, resolved, cause = _wiki_daily_series(disp, days=30)
        if not views:
            out.append(Finding("C.referee_surge", "INSUFFICIENT", disp,
                               f"referee unavailable ({cause}) — fail-open, and the "
                               f"cause is recorded truthfully (board N1)",
                               cause=cause))
            continue
        time.sleep(0.3)
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
        # v2.1 (board N4): PERSIST the series append-only — the drift alarm needs a
        # baseline. Three consecutive rises -> WARN (converging on a lagging fame index).
        series_path = os.path.join(OUT_DIR, "REFEREE_CORR_SERIES.json")
        series = []
        try:
            with open(series_path, encoding="utf-8") as fh:
                series = json.load(fh)
        except Exception:
            series = []
        series.append({"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                       "rho": round(rho, 3), "n": n, "param_version": PARAM_VERSION})
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(series_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(series, fh, indent=1)
        rhos = [s.get("rho") for s in series if isinstance(s.get("rho"), (int, float))]
        rising = len(rhos) >= 4 and all(rhos[-i] > rhos[-i - 1] for i in (1, 2, 3))
        out.append(Finding("C.referee_surge", "WARN" if rising else "PASS",
            "drift-alarm datapoint",
            f"engine-referee rank correlation rho={rho:.2f} on n={n} "
            f"(series length {len(rhos)}; persisted to REFEREE_CORR_SERIES.json; "
            f"a RISING trend = converging on a lagging fame index — alarm)",
            gap="" if not rising else
                "rho has risen 3 consecutive snapshots — the system may be converging "
                "toward the lagging fame index (the opposite of the thesis)",
            solution="" if not rising else
                "escalate to the founder; audit recent scoring/source changes for "
                "anything that couples the score to mainstream fame level",
            severity="high" if rising else "low",
            held_out_derived=True))
    return out


# ═════════════════════════════ D · TREND LIFECYCLE (WARN-only v1) ════════════
def assess_lifecycle(cohort: dict, live: bool, referee_findings: list = None) -> list:
    """Quantile-referenced, abs-floored, RECURRENT-aware. WARN-only until it beats
    the STEADY-monkey null across 3 snapshots (board condition). v2.1: a WARN
    requires a non-INSUFFICIENT referee for the same topic (board condition — an
    instrument-blind referee must not leave lifecycle looks un-refereeable; the
    2026-07-17 spain WARN was refuted by the referee the tool itself couldn't reach)."""
    out = []
    if not live:
        return [Finding("D.lifecycle", "INSUFFICIENT", "demo", "DEMO: lifecycle not simulated")]
    ref_status = {f.subject: f.status for f in (referee_findings or [])
                  if f.check == "C.referee_surge"}
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
            disp = (r.get("topic_display") or key or "").strip()
            rstat = ref_status.get(disp) or ref_status.get(key)
            if rstat is None or rstat == "INSUFFICIENT":
                out.append(Finding("D.lifecycle", "INSUFFICIENT", key,
                    f"internal motion {phase} (recent {recent:.0f} vs p90 {ref:.0f}) "
                    f"while stage {stage} — but the referee is unavailable for this "
                    f"topic, so no look is emitted (board condition)",
                    cause="referee_unavailable"))
            else:
                out.append(Finding("D.lifecycle", "WARN", key,
                    f"internal motion {phase} (recent {recent:.0f} vs p90 {ref:.0f}) while "
                    f"stage still {stage} (referee status for this topic: {rstat})",
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
    # 1) Google daily-trending RSS (free) — COVERAGE gauge, never an accuracy KPI.
    # v2.1 rebuild (board-ruled): full-feed scan with a pinned denominator; phrase /
    # single-topic token matching (the v2 substring-blob matcher produced false hits:
    # "boston" credited for "aliyah boston"); "X vs Y" matchup class registered and
    # EXCLUDED; registered traffic floor; a miss only counts when the independent
    # Wikipedia referee confirms attention actually arrived (the null: most daily-
    # trending queries are noise — Brady flat / Piastri declining refuted the v2 misses).
    try:
        xml = http_text("https://trends.google.com/trending/rss?geo=US", timeout=30)
        raw_titles = re.findall(r"<title>(.*?)</title>", xml)[1:THRESHOLDS["RECALL_TOP"] + 1]
        traffics = re.findall(r"<ht:approx_traffic>([\d,+]+)", xml)
        def _traffic(i):
            try:
                return int(traffics[i].replace(",", "").replace("+", ""))
            except Exception:
                return 0
        items = [(t, _traffic(i)) for i, t in enumerate(raw_titles)]

        # full-feed scan, batch-paced, denominator PINNED in the evidence
        topics_scanned, total_served = [], None
        off = 0
        while off < THRESHOLDS["RECALL_SCAN_CAP"]:
            d = http_json(f"{ENGINE}/scores?limit=100&offset={off}")
            rows = d.get("results") or []
            total_served = d.get("total")
            topics_scanned += [
                ((r.get("topic_key") or "").replace("_", " ") + " " +
                 (r.get("topic_display") or "")).lower().strip()
                for r in rows]
            off += 100
            if not rows or (total_served is not None and off >= total_served):
                break
            time.sleep(0.25)

        STOP = {"2026", "2025", "with", "from", "what", "when", "will", "this", "that"}
        def _matches(title: str) -> bool:
            tl = re.sub(r"\W+", " ", title.lower()).strip()
            toks = [w for w in tl.split() if len(w) > 3 and w not in STOP]
            for s in topics_scanned:
                if tl and tl in s:                       # whole phrase in ONE topic
                    return True
                if toks and all(re.search(r"\b" + re.escape(w), s) for w in toks):
                    return True                          # all tokens in ONE topic
            return False

        matchups = [t for t, _ in items if re.search(r"\b(vs|v)\b", t.lower())]
        graded = [(t, tr) for t, tr in items
                  if t not in matchups and tr >= THRESHOLDS["RECALL_TRAFFIC_FLOOR"]]
        below_floor = [t for t, tr in items
                       if t not in matchups and tr < THRESHOLDS["RECALL_TRAFFIC_FLOOR"]]
        scan_note = (f"scanned {len(topics_scanned)}/{total_served} served topics; "
                     f"{len(matchups)} matchup-class excluded; {len(below_floor)} below "
                     f"the {THRESHOLDS['RECALL_TRAFFIC_FLOOR']:,} traffic floor")
        if not graded:
            out.append(Finding("E.trending_recall", "INSUFFICIENT", "google daily trending",
                f"no external items qualified today ({scan_note}) — an honest no-grade "
                f"day, like the crypto check's 'no 20% movers'",
                cause="no_qualifying_items"))
        else:
            hits, confirmed_misses, unconfirmed = [], [], []
            for t, tr in graded:
                if _matches(t):
                    hits.append(t)
                    continue
                views, resolved, cause = _wiki_daily_series(t, days=21)
                time.sleep(0.3)
                if views:
                    med = statistics.median(views[:-3]) or 0
                    recent = statistics.fmean(views[-3:])
                    if recent >= max(THRESHOLDS["SURGE_FLOOR"],
                                     THRESHOLDS["SURGE_MULT"] * max(med, 1)):
                        confirmed_misses.append(t)       # referee says attention ARRIVED
                    else:
                        unconfirmed.append(f"{t} (no referee surge — the null won)")
                else:
                    unconfirmed.append(f"{t} (referee {cause})")
            denom = len(hits) + len(confirmed_misses)
            if denom == 0:
                out.append(Finding("E.trending_recall", "INSUFFICIENT",
                    "google daily trending",
                    f"0 gradable items after referee confirmation ({scan_note}; "
                    f"unconfirmed: {'; '.join(unconfirmed[:3])[:120]})",
                    cause="no_referee_confirmed_items"))
            else:
                status = "PASS" if len(confirmed_misses) <= denom * 0.4 else "WARN"
                out.append(Finding("E.trending_recall", status, "google daily trending",
                    f"{len(hits)}/{denom} referee-confirmed external trends have a "
                    f"matching served topic ({scan_note}; confirmed misses: "
                    f"{', '.join(confirmed_misses[:4])[:90]})",
                    gap="" if status == "PASS" else
                        "referee-confirmed attention arrivals missing from the served "
                        "feed — a genuine coverage gap (internal gauge only)",
                    solution="" if status == "PASS" else
                        "check the discovery collectors for the missed terms; candidates "
                        "for the catch-all/lexicon worklist; any NEW SOURCE goes through "
                        "the §16 five-gate onboarding protocol",
                    severity="medium" if status == "WARN" else "low",
                    held_out_derived=True))
    except Exception as e:
        out.append(Finding("E.trending_recall", "INSUFFICIENT", "google daily trending",
                           f"fetch failed: {str(e)[:60]}", cause="fetch_error"))
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
        if len(graded) < THRESHOLDS["MIN_GRADED_N"]:
            # v2.1 (board): a letter on a tiny denominator is not a grade ("A" on 2/20
            # abstentions flattered a broken referee). Counts only, no letter, no floor.
            modules[mod] = {"grade": f"N/A (n={len(graded)}<{THRESHOLDS['MIN_GRADED_N']})",
                            "passed": sum(1 for f in graded if f.status == "PASS"),
                            "graded": len(graded),
                            "insufficient": sum(1 for f in fs if f.status == "INSUFFICIENT")}
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
    referee_findings = assess_referee_surge(cohort, live)
    findings += referee_findings
    findings += assess_lifecycle(cohort, live, referee_findings)
    findings += assess_outside(cohort, live)
    findings = [f.finalize() for f in findings]

    modules, floor_pct = grade(findings)
    graded = [f for f in findings if f.status in ("PASS", "FAIL", "WARN") and not f.shadow]
    pass_pct = round(100 * sum(1 for f in graded if f.status == "PASS") / len(graded), 1) if graded else 0

    ledger_headline = {}
    if live:
        try:
            L = http_json(f"{ENGINE}/accuracy/ledger")
            # v2.1 (board N6): the rate always ships with its Wilson 95% interval —
            # on n=33 most of the number is interval (Bernstein: risk is what remains).
            led, sample = L.get("led"), L.get("trackedRaceSample")
            interval = None
            if isinstance(led, int) and isinstance(sample, int) and sample > 0:
                z = 1.959964
                p = led / sample
                den = 1 + z * z / sample
                ctr = (p + z * z / (2 * sample)) / den
                hw = z * ((p * (1 - p) / sample + z * z / (4 * sample * sample)) ** 0.5) / den
                interval = [round(100 * (ctr - hw), 1), round(100 * (ctr + hw), 1)]
            ledger_headline = {
                "tracked_race_hit_rate_pct": L.get("trackedRaceHitRate"),
                "tracked_race_sample": sample,
                "tracked_race_wilson95_pct": interval,
                "blended_hit_rate_pct": L.get("hitRate"),
                "false_positives": L.get("falsePositives"),
                "false_positives_note": ("structurally 0 until the 365d patience window "
                                         "matures rows — not a quality signal yet"),
                # D6 (board 2026-07-19): corroboration status travels WITH the rate.
                "led_referee": {
                    "corroborated": L.get("ledCorroborated"),
                    "uncorroborated": L.get("ledUncorroborated"),
                    "unchecked": L.get("ledUnchecked"),
                    "note": ("uncorroborated = the independent Wikipedia referee found no "
                             "confirming surge (verified honest refutations, 2026-07-18 "
                             "re-run) — the wins stand on Google Trends alone"),
                },
                "epoch_boundary": L.get("epochBoundary"),
                "by_epoch": L.get("byEpoch"),
                "by_epoch_note": ("v2-epoch rates are dominated by YOUNG races: 1,100+ "
                                  "pending under the 365d patience window resolve toward "
                                  "fast Google breakouts first (adverse selection). Read "
                                  "as a series, not a point."),
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
    w = ah.get("tracked_race_wilson95_pct")
    L.append(f"**THE ACCURACY NUMBER (held-out ledger):** tracked-race "
             f"{ah.get('tracked_race_hit_rate_pct')}% (n={ah.get('tracked_race_sample')}"
             f"{'; 95% interval ' + str(w[0]) + '–' + str(w[1]) + '%' if w else ''}) · "
             f"blended {ah.get('blended_hit_rate_pct')}% · epoch-segmented at {ah.get('epoch_boundary')}")
    L.append("")
    if ah.get("false_positives") == 0:
        L.append("*(false positives: 0 — structurally guaranteed until the 365d patience "
                 "window matures rows; not a quality signal yet)*")
        L.append("")
    lr = ah.get("led_referee") or {}
    if lr and lr.get("corroborated") is not None:
        L.append(f"*(LED referee corroboration: {lr.get('corroborated')} corroborated · "
                 f"{lr.get('uncorroborated')} uncorroborated · {lr.get('unchecked')} "
                 f"unchecked — {lr.get('note')})*")
        L.append("")
    if ah.get("by_epoch"):
        L.append(f"*(per-epoch note: {ah.get('by_epoch_note')})*")
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
