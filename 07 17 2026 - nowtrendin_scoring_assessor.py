"""
nowtrendin_scoring_assessor.py
==============================
The ASSESSOR/TEACHER agent — the fourth member of the fleet.

  calibration_agent   (defense)  : engine health, ledger integrity, viability gate
  lead_moat_agent     (offense)  : audited lead vs Google Trends, source gate, discovery
  nowtrendin_agent    (orchestr.): one nightly run of the above
  THIS FILE           (teacher)  : grades the system on 4 questions and, for every
                                   failure, emits the GAP and the SOLUTION in a form
                                   both a developer and Claude Code can act on.

THE FOUR QUESTIONS (one module each)
  A. SOURCE TRACKING  — are the data sources accurately tracking topics?
       (freshness, volume trend, coverage of tracked topics, silent-absence gaps)
  B. SCORE MOVEMENT   — how are scores moving?
       (frozen scores, saturation at caps, volatility, stage-transition sanity)
  C. SCORE ACCURACY   — are the scores right?
       (no-gap test vs the held-out referee, gap arithmetic, duplicate variants,
        mid-band collapse signature)
  D. TREND LIFECYCLE  — where is the trend now, and is it over?
       (RISING / PEAKING / FADING / ENDED / DORMANT, engine-vs-referee agreement)

OUTPUT
  • A human report (sections A–D, PASS/FAIL per check, gap + solution per failure)
  • A machine JSON (findings list) that Claude Code can ingest as a work queue.
  • An overall letter grade per module + one combined "Phase-1 readiness" percent.

INTEGRITY RULES (inherited from the charter)
  Read-only. Abstains (INSUFFICIENT) below minimum N instead of guessing.
  Every rate ships with its denominator. Never tunes a threshold to pass.
  A failing grade is a SUCCESSFUL run — the agent's job is truth, not comfort.

WIRING — implement AssessorAdapter (bottom). Run bare for the synthetic demo.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone, timedelta
from typing import Optional
import json, statistics, sys

# ── frozen thresholds (version-stamped; never tune to pass) ──────────────────
PARAM_VERSION            = "assessor-v1"
STALE_SOURCE_HOURS       = 24        # a source silent longer than this is STALE
VOLUME_DROP_ALERT        = 0.5       # latest-day volume < 50% of its 7d mean → falling
MIN_COVERAGE_RATIO       = 0.6       # a source should see ≥60% of tracked topics it historically covers
FREEZE_CYCLES            = 6         # identical score this many consecutive cycles → FROZEN
SATURATION_BAND          = 1.0       # within 1.0 of a component cap → saturated
HIGH_VOLATILITY_STD      = 12.0      # per-cycle std above this → unstable score
MAINSTREAM_REFEREE_LVL   = 4.0       # log10 median daily pageviews ≥ this → already mainstream
COLLAPSE_DET_BAND        = (40, 50)  # the known mid-band collapse signature
COLLAPSE_CONF_BAND       = (60, 72)
GAP_TOLERANCE            = 0.5       # |stored_gap - (det-conf)| beyond this = arithmetic bug
FADE_DROP_RATIO          = 0.5       # referee interest < 50% of its own peak → fading
ENDED_DROP_RATIO         = 0.25      # < 25% of peak, sustained → ended
MIN_N_FOR_VERDICT        = 5


@dataclass
class Finding:
    module: str            # A_SOURCES | B_MOVEMENT | C_ACCURACY | D_LIFECYCLE
    check: str
    status: str            # PASS | FAIL | WARN | INSUFFICIENT
    subject: str           # source / topic / component
    evidence: str          # the measured fact, with numbers
    gap: str = ""          # what this means is missing/broken (teaching)
    solution: str = ""     # the prescribed fix (teaching)
    severity: str = "low"  # low | medium | high

    def line(self) -> str:
        mark = {"PASS": "✓", "FAIL": "✗", "WARN": "!", "INSUFFICIENT": "…"}[self.status]
        s = f"  {mark} [{self.severity.upper():6}] {self.subject}: {self.evidence}"
        if self.status in ("FAIL", "WARN") and self.gap:
            s += f"\n      GAP      → {self.gap}\n      SOLUTION → {self.solution}"
        return s


# ═════════════════════════════════════════════════════════════════════════════
# A · SOURCE TRACKING — are the sources accurately tracking topics?
# ═════════════════════════════════════════════════════════════════════════════
def assess_sources(source_health: dict, expected_sources: list,
                   coverage: dict, now: datetime) -> list:
    """
    source_health: {source: {"last_success": datetime, "daily_counts": [ints, oldest→newest]}}
    expected_sources: sources that SHOULD be feeding (from config/keys)
    coverage: {source: (topics_seen_30d, topics_expected_30d)}
    """
    out = []
    # silent absence — a configured source with no health record at all
    for src in expected_sources:
        if src not in source_health:
            out.append(Finding("A_SOURCES", "silent_absence", "FAIL", src,
                "configured but produced ZERO signals (no health record)",
                gap="an entire channel is silently missing from every score (like the "
                    "GUARDIAN_API_KEY gap — mainstream-media signal absent)",
                solution="verify the API key/env var is set on the engine app; add this "
                         "source to collector_health so absence is loud, not silent",
                severity="high"))
    for src, h in source_health.items():
        age_h = (now - h["last_success"]).total_seconds() / 3600
        if age_h > STALE_SOURCE_HOURS:
            out.append(Finding("A_SOURCES", "freshness", "FAIL", src,
                f"last successful collection {age_h:.0f}h ago (> {STALE_SOURCE_HOURS}h)",
                gap="scores are being computed without this channel's current signal",
                solution="check collector logs/credentials; alert on consecutive_failures "
                         "in collector_health", severity="high"))
        else:
            out.append(Finding("A_SOURCES", "freshness", "PASS", src,
                f"fresh ({age_h:.0f}h since last success)"))
        counts = h.get("daily_counts", [])
        if len(counts) >= 7:
            base = statistics.fmean(counts[-8:-1])
            if base > 0 and counts[-1] < VOLUME_DROP_ALERT * base:
                out.append(Finding("A_SOURCES", "volume", "WARN", src,
                    f"today's volume {counts[-1]} is {counts[-1]/base:.0%} of its 7d mean {base:.0f}",
                    gap="a quietly shrinking feed starves Detection's earliest components",
                    solution="inspect rate limits / API quota / actor budget for this provider",
                    severity="medium"))
        seen, expected = coverage.get(src, (None, None))
        if seen is not None and expected:
            ratio = seen / expected
            if ratio < MIN_COVERAGE_RATIO:
                out.append(Finding("A_SOURCES", "coverage", "FAIL", src,
                    f"sees only {seen}/{expected} ({ratio:.0%}) of tracked topics it historically covers",
                    gap="topic-level blind spots — trends can move in this channel unseen",
                    solution="widen the query set / keyword expansion for this source; "
                             "check per-topic collection errors", severity="medium"))
            else:
                out.append(Finding("A_SOURCES", "coverage", "PASS", src,
                    f"covers {seen}/{expected} ({ratio:.0%}) of its tracked topics"))
    return out


# ═════════════════════════════════════════════════════════════════════════════
# B · SCORE MOVEMENT — how are the scores moving?
# ═════════════════════════════════════════════════════════════════════════════
def assess_movement(score_histories: dict, component_states: dict) -> list:
    """
    score_histories: {topic: [detection per cycle, oldest→newest]}
    component_states: {topic: {component: (value, cap)}}
    """
    out = []
    for topic, hist in score_histories.items():
        if len(hist) < FREEZE_CYCLES:
            out.append(Finding("B_MOVEMENT", "freeze", "INSUFFICIENT", topic,
                f"only {len(hist)} cycles of history"))
            continue
        tail = hist[-FREEZE_CYCLES:]
        if max(tail) - min(tail) == 0:
            caps_hit = [c for c, (v, cap) in component_states.get(topic, {}).items()
                        if cap - v <= SATURATION_BAND]
            out.append(Finding("B_MOVEMENT", "freeze", "FAIL", topic,
                f"Detection frozen at exactly {tail[-1]} for {FREEZE_CYCLES}+ cycles"
                + (f"; components at cap: {caps_hit}" if caps_hit else ""),
                gap="a frozen score carries no information — the known cause is component "
                    "caps hitting their ceilings (e.g. Niche Concentration, Platform "
                    "Diversity), so real movement can't register",
                solution="raise/soften the saturating component caps or re-scale so headroom "
                         "exists; verify score recomputes each cycle rather than serving a "
                         "cached value", severity="high"))
        else:
            vol = statistics.pstdev(tail)
            if vol > HIGH_VOLATILITY_STD:
                out.append(Finding("B_MOVEMENT", "volatility", "WARN", topic,
                    f"per-cycle std {vol:.1f} over last {FREEZE_CYCLES} cycles",
                    gap="a score this jumpy can't be acted on — likely thin signal or a "
                        "flapping input",
                    solution="check input volume for this topic; consider smoothing window "
                             "or minimum-signal floor", severity="medium"))
            else:
                out.append(Finding("B_MOVEMENT", "movement", "PASS", topic,
                    f"moving normally (range {min(tail)}–{max(tail)}, std {vol:.1f})"))
    return out


# ═════════════════════════════════════════════════════════════════════════════
# C · SCORE ACCURACY — are the scores right? (vs the held-out referee)
# ═════════════════════════════════════════════════════════════════════════════
def assess_accuracy(snapshot: list, referee_level: dict, variants: list) -> list:
    """
    snapshot: [{"topic","detection","confidence","stored_gap"}]
    referee_level: {topic: log10 median daily pageviews (held-out Wikipedia)}
    variants: [ [surface forms of same story], ... ]
    """
    out = []
    by_topic = {r["topic"]: r for r in snapshot}
    # 1) gap arithmetic
    bad = [r for r in snapshot
           if abs(r["stored_gap"] - (r["detection"] - r["confidence"])) > GAP_TOLERANCE]
    if bad:
        ex = bad[0]
        out.append(Finding("C_ACCURACY", "gap_arithmetic", "FAIL",
            f"{len(bad)}/{len(snapshot)} rows",
            f"stored gap ≠ Detection−Confidence (e.g. {ex['topic']}: stored "
            f"{ex['stored_gap']} vs actual {ex['detection']-ex['confidence']:+.1f})",
            gap="the served gap contradicts its own scores — breaks 'both scores explain "
                "each other' and any gap-based product claim",
            solution="recompute gap at write time as signed Detection−Confidence on every "
                     "row; add the invariant to the Scoring Contract Auditor",
            severity="high"))
    else:
        out.append(Finding("C_ACCURACY", "gap_arithmetic", "PASS",
            f"{len(snapshot)} rows", "stored gap = Detection−Confidence on every row"))
    # 2) no-gap test against the referee (mainstream must read high/high)
    checked = failed = 0
    for topic, lvl in referee_level.items():
        r = by_topic.get(topic)
        if r is None or lvl < MAINSTREAM_REFEREE_LVL:
            continue
        checked += 1
        det, conf = r["detection"], r["confidence"]
        collapsed = (COLLAPSE_DET_BAND[0] <= det <= COLLAPSE_DET_BAND[1]
                     and COLLAPSE_CONF_BAND[0] <= conf <= COLLAPSE_CONF_BAND[1])
        if det < 70 or conf < 70 or collapsed:
            failed += 1
            out.append(Finding("C_ACCURACY", "no_gap", "FAIL", topic,
                f"referee says mainstream (lvl {lvl:.1f}) but engine reads {det}/{conf}"
                + (" — the known ~45/67 collapse signature" if collapsed else ""),
                gap="an already-arrived topic is mis-read as early/uncertain — the exact "
                    "failure that invalidates the gap metric for buyers",
                solution="extend the dual-pathway anti-collapse preservation across the "
                         "mid-mainstream band (audit rec); verify mainstream_ratio w isn't "
                         "collapsing for these rows", severity="high"))
    if checked >= MIN_N_FOR_VERDICT:
        out.append(Finding("C_ACCURACY", "no_gap_summary",
            "PASS" if failed == 0 else "FAIL", "mainstream cohort",
            f"{checked-failed}/{checked} referee-confirmed mainstream topics read high/high",
            gap="" if failed == 0 else "mid-band accuracy below the credibility floor",
            solution="" if failed == 0 else "see per-topic no_gap failures above",
            severity="high" if failed else "low"))
    else:
        out.append(Finding("C_ACCURACY", "no_gap_summary", "INSUFFICIENT",
            "mainstream cohort", f"only {checked} referee-confirmed topics (need ≥{MIN_N_FOR_VERDICT})"))
    # 3) duplicate surface forms
    for group in variants:
        scores = [by_topic[t]["detection"] for t in group if t in by_topic]
        if len(scores) >= 2 and (max(scores) - min(scores)) > 10:
            out.append(Finding("C_ACCURACY", "variants", "FAIL", " / ".join(group),
                f"same story scores {min(scores):.0f}–{max(scores):.0f} across spellings",
                gap="surface-form fragmentation splits one story into competing topics, "
                    "collapsing the canonical phrase",
                solution="add the alias-consolidation layer to normalize_topic() so variants "
                         "merge before scoring", severity="medium"))
        elif len(scores) >= 2:
            out.append(Finding("C_ACCURACY", "variants", "PASS", " / ".join(group),
                f"variants aligned ({min(scores):.0f}–{max(scores):.0f})"))
    return out


# ═════════════════════════════════════════════════════════════════════════════
# D · TREND LIFECYCLE — where is the trend now, and is it over?
# ═════════════════════════════════════════════════════════════════════════════
def classify_lifecycle(referee_series: list) -> str:
    """referee_series: [(date, interest)] oldest→newest, held-out external interest."""
    vals = [v for _, v in referee_series]
    if len(vals) < 8:
        return "INSUFFICIENT"
    peak = max(vals)
    if peak <= 0:
        return "DORMANT"
    recent = statistics.fmean(vals[-3:])
    prior = statistics.fmean(vals[-8:-3])
    if recent >= 0.9 * peak and recent > prior:
        return "PEAKING"
    if recent > prior * 1.25:
        return "RISING"
    if recent < ENDED_DROP_RATIO * peak:
        return "ENDED"
    if recent < FADE_DROP_RATIO * peak or recent < prior * 0.75:
        return "FADING"
    return "STEADY"


def assess_lifecycle(topics: dict, engine_stage: dict) -> list:
    """
    topics: {topic: referee_series}; engine_stage: {topic: current engine stage label}
    Grades whether the engine's stage agrees with the external lifecycle.
    """
    out = []
    ENGINE_ACTIVE = {"BREAKOUT", "STRONG", "EMERGING", "INDICATING"}
    for topic, series in topics.items():
        phase = classify_lifecycle(series)
        stage = engine_stage.get(topic, "?")
        if phase == "INSUFFICIENT":
            out.append(Finding("D_LIFECYCLE", "phase", "INSUFFICIENT", topic,
                "not enough external history to place the trend"))
            continue
        # disagreement checks (teachable moments)
        if phase in ("ENDED", "FADING") and stage in ENGINE_ACTIVE:
            out.append(Finding("D_LIFECYCLE", "agreement", "FAIL", topic,
                f"externally {phase} but engine still shows {stage}",
                gap="the engine keeps a dead/dying trend 'active' — stale scores erode "
                    "trust and pollute the ledger with unwinnable calls",
                solution="drive stage decay from freshness/decline (Confidence-Decay path); "
                         "verify the topic is re-scoring and its inputs aren't cached",
                severity="medium"))
        elif phase == "RISING" and stage in ("MONITORING", "WATCHING", "MARGINAL"):
            out.append(Finding("D_LIFECYCLE", "agreement", "WARN", topic,
                f"externally RISING but engine only shows {stage}",
                gap="possible late detection — rising outside while the engine still "
                    "watches; this is the discovery-latency lever",
                solution="check source coverage for this topic (module A) and component "
                         "headroom (module B); log for the lead audit", severity="medium"))
        else:
            out.append(Finding("D_LIFECYCLE", "agreement", "PASS", topic,
                f"{phase} — engine stage {stage} is consistent"))
    return out


# ═════════════════════════════════════════════════════════════════════════════
# ADAPTER + RUN
# ═════════════════════════════════════════════════════════════════════════════
class AssessorAdapter(ABC):
    @abstractmethod
    def source_health(self) -> dict: ...
    @abstractmethod
    def expected_sources(self) -> list: ...
    @abstractmethod
    def source_coverage(self) -> dict: ...
    @abstractmethod
    def score_histories(self) -> dict: ...
    @abstractmethod
    def component_states(self) -> dict: ...
    @abstractmethod
    def score_snapshot(self) -> list: ...
    @abstractmethod
    def referee_mainstream_levels(self) -> dict: ...
    @abstractmethod
    def variant_groups(self) -> list: ...
    @abstractmethod
    def referee_series(self) -> dict: ...
    @abstractmethod
    def engine_stages(self) -> dict: ...


def run_assessment(a: AssessorAdapter, now: Optional[datetime] = None) -> dict:
    now = now or datetime.now(timezone.utc)
    findings: list = []
    findings += assess_sources(a.source_health(), a.expected_sources(), a.source_coverage(), now)
    findings += assess_movement(a.score_histories(), a.component_states())
    findings += assess_accuracy(a.score_snapshot(), a.referee_mainstream_levels(), a.variant_groups())
    findings += assess_lifecycle(a.referee_series(), a.engine_stages())

    def grade(mod):
        f = [x for x in findings if x.module == mod and x.status != "INSUFFICIENT"]
        if not f:
            return "N/A", 0, 0
        fails = sum(1 for x in f if x.status == "FAIL")
        warns = sum(1 for x in f if x.status == "WARN")
        score = (len(f) - fails - 0.5 * warns) / len(f)
        letter = "A" if score >= 0.9 else "B" if score >= 0.75 else "C" if score >= 0.5 else "D" if score >= 0.25 else "F"
        return letter, len(f) - fails - warns, len(f)

    modules = {}
    for mod, label in [("A_SOURCES", "Source tracking"), ("B_MOVEMENT", "Score movement"),
                       ("C_ACCURACY", "Score accuracy"), ("D_LIFECYCLE", "Trend lifecycle")]:
        letter, passed, total = grade(mod)
        modules[mod] = {"label": label, "grade": letter, "passed": passed, "total": total}

    gradeable = [x for x in findings if x.status != "INSUFFICIENT"]
    readiness = round(100 * sum(1 for x in gradeable if x.status == "PASS") / len(gradeable)) if gradeable else 0
    work_queue = sorted([x for x in findings if x.status in ("FAIL", "WARN")],
                        key=lambda x: {"high": 0, "medium": 1, "low": 2}[x.severity])
    return {"run_at": now.isoformat(timespec="seconds"), "param_version": PARAM_VERSION,
            "modules": modules, "phase1_readiness_pct": readiness,
            "findings": findings, "work_queue": work_queue}


def print_report(r: dict) -> None:
    L = "═" * 78
    print(f"\n{L}\n SCORING ASSESSOR · {r['run_at']} · {r['param_version']}\n{L}")
    print(f"\n PHASE-1 READINESS: {r['phase1_readiness_pct']}%  (share of gradeable checks passing)\n")
    for mod, m in r["modules"].items():
        print(f"   {m['label']:<16} grade {m['grade']}   ({m['passed']}/{m['total']} checks pass)")
    for mod, label in [("A_SOURCES", "A · SOURCE TRACKING"), ("B_MOVEMENT", "B · SCORE MOVEMENT"),
                       ("C_ACCURACY", "C · SCORE ACCURACY"), ("D_LIFECYCLE", "D · TREND LIFECYCLE")]:
        print(f"\n {label}")
        for f in [x for x in r["findings"] if x.module == mod]:
            print(f.line())
    print(f"\n WORK QUEUE (teach list — highest severity first)")
    if not r["work_queue"]:
        print("   (empty — all gradeable checks pass)")
    for i, f in enumerate(r["work_queue"], 1):
        print(f"   {i}. [{f.severity.upper()}] {f.subject} — {f.gap}")
        print(f"      FIX: {f.solution}")
    print(f"{L}\n")


def to_claude_code_json(r: dict) -> str:
    """Machine-readable work queue for Claude Code / the dev."""
    return json.dumps({
        "run_at": r["run_at"], "phase1_readiness_pct": r["phase1_readiness_pct"],
        "modules": r["modules"],
        "tasks": [asdict(f) for f in r["work_queue"]],
    }, indent=2)


# ═════════════════════════════════════════════════════════════════════════════
# DEMO (synthetic — mirrors the known live failure modes)
# ═════════════════════════════════════════════════════════════════════════════
class _Demo(AssessorAdapter):
    def __init__(self):
        self.now = datetime(2026, 7, 16, 12, 0, tzinfo=timezone.utc)
        D = lambda d: date(2026, 6, 1) + timedelta(days=d)
        self.D = D

    def source_health(self):
        h = lambda hrs, counts: {"last_success": self.now - timedelta(hours=hrs),
                                 "daily_counts": counts}
        return {"hackernews": h(2, [40, 42, 39, 41, 44, 43, 40, 41]),
                "github":     h(3, [60, 62, 65, 61, 63, 60, 64, 62]),
                "reddit":     h(50, [30, 31, 29, 30, 28, 30, 29, 12]),   # stale + falling
                "apify":      h(1, [80, 82, 81, 79, 83, 80, 82, 30])}    # fresh but volume cliff
    def expected_sources(self):
        return ["hackernews", "github", "reddit", "apify", "guardian"]   # guardian silently absent
    def source_coverage(self):
        return {"hackernews": (45, 50), "github": (48, 50), "reddit": (20, 50), "apify": (44, 50)}

    def score_histories(self):
        return {"mcp": [74, 74, 74, 74, 74, 74, 74],                      # frozen at 74
                "iran": [82, 84, 83, 86, 85, 87, 86],
                "bonkers": [30, 55, 22, 61, 18, 52, 40]}                  # unstable
    def component_states(self):
        return {"mcp": {"NicheConcentration": (99.5, 100), "PlatformDiversity": (99.8, 100)}}

    def score_snapshot(self):
        return [
            {"topic": "trump",  "detection": 94.6, "confidence": 94.2, "stored_gap": 0.4},
            {"topic": "china",  "detection": 45.6, "confidence": 67.5, "stored_gap": -21.9},
            {"topic": "apple",  "detection": 45.2, "confidence": 67.2, "stored_gap": -22.0},
            {"topic": "openai", "detection": 45.4, "confidence": 67.1, "stored_gap": -21.7},
            {"topic": "india",  "detection": 45.6, "confidence": 67.5, "stored_gap": -21.9},
            {"topic": "fifa",   "detection": 93.7, "confidence": 93.7, "stored_gap": 0.0},
            {"topic": "mcp",    "detection": 74.5, "confidence": 73.0, "stored_gap": -23.0},  # bad gap
            {"topic": "hormuz", "detection": 72.3, "confidence": 83.2, "stored_gap": -10.9},
            {"topic": "strait of hormuz", "detection": 23.9, "confidence": 54.3, "stored_gap": -30.4},
        ]
    def referee_mainstream_levels(self):
        return {"trump": 5.6, "china": 5.1, "apple": 5.3, "openai": 4.8, "india": 5.0, "fifa": 5.2}
    def variant_groups(self):
        return [["hormuz", "strait of hormuz"]]

    def referee_series(self):
        D = self.D
        rising  = [(D(i), 5 + i * 3) for i in range(20)]
        fading  = [(D(i), 100 if i < 8 else max(5, 100 - (i - 7) * 12)) for i in range(20)]
        ended   = [(D(i), 90 if i < 5 else (40 if i < 8 else 6)) for i in range(20)]
        steady  = [(D(i), 60 + (i % 3)) for i in range(20)]
        return {"quantum sdk": rising, "juneteenth": fading, "daveigh chase": ended, "iran": steady}
    def engine_stages(self):
        return {"quantum sdk": "WATCHING",      # rising outside, engine still watching → late
                "juneteenth": "STRONG",          # fading outside, engine still active → stale
                "daveigh chase": "MONITORING",   # ended, engine correctly demoted
                "iran": "BREAKOUT"}


if __name__ == "__main__":
    demo = _Demo()
    report = run_assessment(demo, now=demo.now)
    print_report(report)
    # machine output for Claude Code:
    with open("assessor_work_queue.json", "w") as f:
        f.write(to_claude_code_json(report))
    print("machine work-queue written → assessor_work_queue.json")
    sys.exit(0)
