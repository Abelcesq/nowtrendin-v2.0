"""
lead_moat_agent.py
==================
The OFFENSE companion to calibration_agent.py.

calibration_agent measures whether the engine is healthy and whether it passes the
viability gate (defense). This agent operationalizes the three moves that BUILD the
moat (offense), each mapped to one recommendation:

  A. GoogleTrendsLeadAuditor  → "Make audited lead vs Google Trends the product."
       Turns every detection into a head-to-head receipt: our detection date vs the
       Google Trends breakout date, lead in days, verdict. Produces the shareable,
       denominator-backed scorecard that none of Semrush / trendtrack / Google Trends
       will ever publish about themselves.

  B. SourceLeadGate           → "Double down where search is blind."
       Classifies sources as LEADING or LAGGING from proven lead, then gates each
       detection. Topics that arrive ONLY via lagging sources (news/apify Trump,
       obama) are tagged out-of-scope for the LEAD claim so they stop dragging the
       honest rate to zero — SEGMENTED transparently, never hidden (two denominators).

  C. OpenWorldDiscovery       → "Close the discovery gap."
       Scans leading sources for emerging terms that are NOT yet tracked and NOT yet
       on Google Trends — i.e. genuinely pre-mainstream. These candidates are the only
       place a real LED row can come from. A checker validates known topics; this makes
       the engine a tracker.

THE LOOP (this is the moat):
  discover in a leading source  →  gate (leading-origin only)  →  log detection
  →  later, audit lead vs Google Trends  →  receipt.

────────────────────────────────────────────────────────────────────────────────
WHAT THIS AGENT DOES / DOES NOT DO
  DOES   : produce receipts, gate decisions, and discovery candidates; report two
           honest denominators (leadable vs full); feed the engine + ledger.
  DOES NOT: change any score/weight/tier, set breakout dates by hand, fabricate lead,
           HIDE lagging topics to flatter the number, or claim a lead the GT audit
           hasn't earned. It is read-only advice the engine/ledger choose to honor.

INTEGRITY GUARDRAIL (hard):
  The source gate SEGMENTS, it does not censor. It always reports BOTH the scoped
  (leading-source-universe) honest rate AND the full-coverage rate, and the scoped
  number is only claimable if (1) the gating rule was pre-registered and frozen and
  (2) the excluded rows stay visible in their own bucket. Anything else is gaming.

SUCCESS (for the agent, not the product):
  A run succeeds when it: audits every resolved detection against GT into a receipt,
  classifies sources and emits per-topic gate decisions, surfaces discovery
  candidates, and — re-run on identical inputs — returns identical numbers. A clean
  run can still report LED rate 0.0%; that is the product's job to fix, not the agent's
  to flatter.

PARAMETERS (freeze + version; never tune to pass)
  GT_BREAKOUT_MULT      2.5    Google Trends breakout = value ≥ mult × trailing baseline
  GT_BREAKOUT_SUSTAIN   3      …sustained this many consecutive days
  GT_BASELINE_DAYS      90     trailing window for the GT baseline
  MIN_SOURCE_LEAD       1.0    a source must lead GT by ≥ this (days, median) to be LEADING
  DISCOVERY_MIN_VELOCITY 3.0   emergence ratio (recent vs baseline) to surface a candidate
  LEADING_SOURCES       github, hackernews, arxiv, dev (the search-blind upstream feeds)

GOTCHAS
  • Lead sign: lead = breakout − detection. POSITIVE = early. One convention everywhere.
  • A discovery candidate that is ALREADY on Google Trends is not early — it's late;
    the on_gt() check is what keeps discovery honest.
  • Source classification needs enough matured events per source or it's noise — the
    gate reports n and abstains (UNKNOWN) below a minimum.
  • Excluding lagging-only topics is only legitimate with a pre-registered rule and the
    full-coverage number shown alongside. Don't ship the scoped number alone.
  • Google Trends is relative + renormalized per query window — pull consistent windows.
  • Read-only: emit candidates/decisions/receipts; the engine wires them in. No silent
    writes to production scores or ledger verdicts.

WIRING (the only functions you connect)
  load_gt_series(topic)            -> list[(date, value)] ascending
  load_topic_sources(topic)        -> list[str] sources that produced the detection
  load_source_attribution()        -> {source: median_lead_days}   (from calibration_agent)
  fetch_leading_source_items(src)  -> list[(term, recent_daily_counts)]
  is_already_tracked(term)         -> bool
  gt_has_broken_out(term)          -> bool

Run `python lead_moat_agent.py` for a synthetic end-to-end demo.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional, Callable
import statistics

# ── frozen params ───────────────────────────────────────────────────────────
GT_BREAKOUT_MULT       = 2.5
GT_BREAKOUT_SUSTAIN    = 3
GT_BASELINE_DAYS       = 90
MIN_SOURCE_LEAD        = 1.0
MIN_EVENTS_PER_SOURCE  = 5
DISCOVERY_MIN_VELOCITY = 3.0
LEADING_SOURCES        = {"github", "hackernews", "arxiv", "dev"}
PARAM_VERSION          = "moat-params-v1"


# ── shared shapes ───────────────────────────────────────────────────────────
@dataclass
class Receipt:
    topic: str
    detection_date: date
    gt_breakout_date: Optional[date]
    lead_days: Optional[int]
    verdict: str                 # LED | SAME_DAY | LAGGED | PENDING
    sources: list = field(default_factory=list)
    text: str = ""

@dataclass
class GateDecision:
    topic: str
    decision: str                # SCORE_FULL | SCORE_NOTE | EXCLUDE_FROM_LEAD
    reason: str
    leading_sources: list = field(default_factory=list)
    lagging_sources: list = field(default_factory=list)

@dataclass
class DiscoveryCandidate:
    term: str
    source: str
    velocity: float
    first_seen: date
    pre_mainstream: bool = True


# ═════════════════════════════════════════════════════════════════════════════
# MODULE A — Google Trends lead auditor  (rec #1)
# ═════════════════════════════════════════════════════════════════════════════
def detect_gt_breakout(series: list) -> Optional[date]:
    """First date Google Trends value ≥ MULT × trailing baseline, sustained SUSTAIN days.
    series: list[(date, value)] ascending. Returns breakout date or None."""
    vals = [v for _, v in series]
    n = len(vals)
    if n < GT_BREAKOUT_SUSTAIN + 5:
        return None
    for i in range(n - GT_BREAKOUT_SUSTAIN + 1):
        prior = vals[max(0, i - GT_BASELINE_DAYS):i]
        if len(prior) < 5:
            continue
        base = statistics.fmean(prior)
        thr = max(base * GT_BREAKOUT_MULT, base + 1.0)   # guard near-zero baselines
        window = vals[i:i + GT_BREAKOUT_SUSTAIN]
        if all(x >= thr for x in window):
            return series[i][0]
    return None


def audit_topic(topic: str, detection_date: date, gt_series: list,
                sources: Optional[list] = None) -> Receipt:
    """Head-to-head receipt: our detection date vs the Google Trends breakout date."""
    bo = detect_gt_breakout(gt_series)
    if bo is None:
        return Receipt(topic, detection_date, None, None, "PENDING", sources or [],
                       f"{topic}: detected {detection_date}; Google Trends has not broken "
                       f"out yet (still pending — this is where a LED can still appear).")
    lead = (bo - detection_date).days
    verdict = "LED" if lead >= 1 else ("SAME_DAY" if lead == 0 else "LAGGED")
    text = (f"{topic}: we flagged it {detection_date}; Google Trends broke out {bo} "
            f"→ lead {lead:+d}d ({verdict}).")
    return Receipt(topic, detection_date, bo, lead, verdict, sources or [], text)


def gt_scorecard(receipts: list) -> dict:
    """Audited head-to-head vs Google Trends. Resolved rows only."""
    resolved = [r for r in receipts if r.verdict != "PENDING"]
    leads = [r.lead_days for r in resolved if r.lead_days is not None]
    led = sum(1 for r in resolved if r.verdict == "LED")
    n = len(resolved)
    return {"n_resolved": n, "n_pending": len(receipts) - n,
            "led": led, "led_rate": round(led / n, 3) if n else 0.0,
            "median_lead": (statistics.median(leads) if leads else None),
            "max_lead": (max(leads) if leads else None),
            "verdict_breakdown": {v: sum(1 for r in resolved if r.verdict == v)
                                  for v in ("LED", "SAME_DAY", "LAGGED")},
            "receipts": [r.text for r in resolved]}


# ═════════════════════════════════════════════════════════════════════════════
# MODULE B — source lead gate  (rec #2)
# ═════════════════════════════════════════════════════════════════════════════
def classify_sources(attribution: dict, event_counts: Optional[dict] = None) -> dict:
    """attribution: {source: median_lead_days}. Returns {source: LEADING|LAGGING|UNKNOWN}."""
    out = {}
    for src, lead in attribution.items():
        n = (event_counts or {}).get(src, MIN_EVENTS_PER_SOURCE)
        if n < MIN_EVENTS_PER_SOURCE:
            out[src] = "UNKNOWN"
        else:
            out[src] = "LEADING" if lead >= MIN_SOURCE_LEAD else "LAGGING"
    return out


def gate_detection(topic: str, sources: list, classification: dict) -> GateDecision:
    leading = [s for s in sources if classification.get(s) == "LEADING"]
    lagging = [s for s in sources if classification.get(s) == "LAGGING"]
    if leading:
        dec, reason = "SCORE_FULL", "originates in a leading source — eligible for the lead claim"
    elif lagging and not leading:
        dec, reason = ("EXCLUDE_FROM_LEAD",
                       "only lagging sources saw this — structurally unwinnable; "
                       "out-of-scope for the lead claim, kept in full-coverage bucket")
    else:
        dec, reason = "SCORE_NOTE", "source lead unknown — score but tag as not-yet-eligible"
    return GateDecision(topic, dec, reason, leading, lagging)


def segmented_scorecard(receipts: list, classification: dict,
                        sources_for: Callable[[str], list]) -> dict:
    """TWO denominators, transparently. Leadable universe vs full coverage."""
    leadable, full = [], []
    for r in receipts:
        if r.verdict == "PENDING":
            continue
        g = gate_detection(r.topic, sources_for(r.topic), classification)
        full.append(r)
        if g.decision in ("SCORE_FULL", "SCORE_NOTE"):
            leadable.append(r)
    def rate(rows):
        n = len(rows); led = sum(1 for r in rows if r.verdict == "LED")
        leads = [r.lead_days for r in rows if r.lead_days is not None]
        return {"n": n, "led": led, "led_rate": round(led / n, 3) if n else 0.0,
                "median_lead": (statistics.median(leads) if leads else None)}
    return {"leadable_universe": rate(leadable), "full_coverage": rate(full),
            "note": "Claim only the leadable-universe number IF the gating rule is "
                    "pre-registered and the full-coverage number is shown alongside."}


# ═════════════════════════════════════════════════════════════════════════════
# MODULE C — open-world discovery  (rec #3)
# ═════════════════════════════════════════════════════════════════════════════
def emergence_velocity(recent_daily_counts: list) -> float:
    """Ratio of the latest activity to its own recent baseline. >1 = accelerating."""
    if len(recent_daily_counts) < 4:
        return 0.0
    latest = statistics.fmean(recent_daily_counts[-2:])
    base = statistics.fmean(recent_daily_counts[:-2])
    return round(latest / base, 2) if base > 0 else (DISCOVERY_MIN_VELOCITY if latest > 0 else 0.0)


def discover(feeds: dict, is_already_tracked: Callable[[str], bool],
             gt_has_broken_out: Callable[[str], bool], today: date) -> list:
    """
    feeds: {source: [(term, recent_daily_counts)]}. Surfaces terms that are
    (a) accelerating in a LEADING source, (b) not already tracked, and
    (c) NOT yet on Google Trends — i.e. genuinely pre-mainstream.
    """
    out = []
    for src, items in feeds.items():
        if src not in LEADING_SOURCES:
            continue                      # only search-blind upstream feeds can lead
        for term, counts in items:
            v = emergence_velocity(counts)
            if v < DISCOVERY_MIN_VELOCITY:
                continue
            if is_already_tracked(term):
                continue                  # not new
            if gt_has_broken_out(term):
                continue                  # already mainstream → not early, skip honestly
            out.append(DiscoveryCandidate(term, src, v, today, pre_mainstream=True))
    return sorted(out, key=lambda c: -c.velocity)


# ═════════════════════════════════════════════════════════════════════════════
# DEMO
# ═════════════════════════════════════════════════════════════════════════════
def _demo():
    today = date(2026, 6, 18)
    D = lambda d: date(2026, 6, 1) + timedelta(days=d)

    def gt(breakout_offset, base=8, spike=60):
        s = []
        for i in range(-30, 18):
            d = D(i)
            v = base if (breakout_offset is None or i < breakout_offset) else spike
            s.append((d, v))
        return s

    # ── A: audit a few detections vs Google Trends
    detections = [
        ("rust async runtime", D(2),  gt(10),   ["github", "hackernews"]),  # early -> LED
        ("model context protocol", D(1), gt(-4), ["github", "sweep"]),      # late  -> LAGGED
        ("Donald Trump", D(12), gt(-2), ["apify"]),                         # late, lagging-source -> excluded from lead claim
        ("neuromorphic inference", D(6), gt(None), ["arxiv", "hackernews"]),# pending (pre-mainstream)
    ]
    receipts = [audit_topic(t, dd, series, src) for t, dd, series, src in detections]
    sc = gt_scorecard(receipts)

    # ── B: classify sources from attribution, gate, segment
    attribution = {"hackernews": 12, "github": 3, "arxiv": 9, "sweep": -12, "apify": -36}
    cls = classify_sources(attribution, event_counts={k: 8 for k in attribution})
    src_map = {t: src for t, _, _, src in detections}
    seg = segmented_scorecard(receipts, cls, lambda t: src_map.get(t, []))

    # ── C: discover pre-mainstream candidates from leading feeds
    feeds = {
        "arxiv":      [("state space models v2", [1, 1, 2, 3, 7, 11]),
                       ("retrieval pretraining", [2, 2, 2, 2, 2, 2])],     # flat -> skip
        "github":     [("ziglang orm", [0, 1, 1, 4, 9, 14])],
        "apify":      [("celebrity gossip x", [5, 9, 20, 40, 80, 120])],   # lagging source -> ignored
    }
    cands = discover(feeds, is_already_tracked=lambda t: t == "retrieval pretraining",
                     gt_has_broken_out=lambda t: False, today=today)

    # ── report
    L = "═" * 76
    print(f"\n{L}\n LEAD MOAT AGENT · {today}\n{L}")
    print(" A. AUDITED LEAD vs GOOGLE TRENDS")
    print(f"    resolved {sc['n_resolved']} · pending {sc['n_pending']} · "
          f"LED {sc['led']} · LED-rate {sc['led_rate']} · "
          f"median lead {sc['median_lead']} · max lead {sc['max_lead']}")
    print(f"    breakdown {sc['verdict_breakdown']}")
    print("    receipts:")
    for line in sc["receipts"]:
        print(f"      • {line}")

    print("\n B. SOURCE LEAD GATE")
    print(f"    classification {cls}")
    for t, _, _, src in detections:
        g = gate_detection(t, src, cls)
        print(f"      • {t:<24} {g.decision:<17} ({g.reason})")
    print(f"    leadable universe : {seg['leadable_universe']}")
    print(f"    full coverage     : {seg['full_coverage']}")

    print("\n C. OPEN-WORLD DISCOVERY (pre-mainstream candidates from leading sources)")
    if not cands:
        print("      (none cleared the bar)")
    for c in cands:
        print(f"      • {c.term:<22} via {c.source:<10} velocity {c.velocity}×  → log as early detection")
    print(f"{L}\n")


if __name__ == "__main__":
    _demo()
