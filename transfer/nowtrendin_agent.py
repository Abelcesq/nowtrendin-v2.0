"""
nowtrendin_agent.py
===================
THE single scheduled entry point. Runs the whole grading-and-tracking audit in one
pass and emits one combined nightly report.

It composes the two agents you already have:
  • calibration_agent  (defense) — engine health, ledger integrity, viability gate,
                                    source attribution.
  • lead_moat_agent    (offense) — audited lead vs Google Trends + receipts, the
                                    source lead gate, and open-world discovery.

WHY ONE ENTRY POINT
  Your dev wires data in EXACTLY ONE place — the DataAdapter below — and schedules
  ONE command. The agent fans that out to every check and folds the results into a
  single report, a single structured record (for the dashboard/ledger), and a single
  alerts list (for paging).

WHAT IT PRODUCES EACH RUN
  1. Engine-health tallies          (saturation, what-if-N, cold-start, leaks…)
  2. Ledger integrity flags         (stale matches, FP-overdue, immature cohort)
  3. Viability gate                 (Detection-vs-Trends lead/lag → PASS/FAIL/INSUFFICIENT)
  4. Source attribution             (which feeds genuinely lead)
  5. Audited lead vs Google Trends  (receipts + scorecard — the moat artifact)
  6. Source-gated honest rate       (leadable universe vs full coverage, BOTH shown)
  7. Open-world discovery           (pre-mainstream candidates to log as early calls)
  8. A plain-English "where we stand" line + an alerts list.

WHAT IT DOES NOT DO
  • No score/weight/tier/verdict changes. Read-only except an append-only epoch write.
  • No fabricated lead, no hidden denominators, no claim the GT audit hasn't earned.
  • Does not decide product viability by vibes — only by the frozen gate bars.
  • A clean run can and will report the product as FAIL/INSUFFICIENT. That is correct.

SUCCESS (for the agent)
  A run succeeds when every section computes (or correctly abstains on small N), one
  epoch is written, and re-running on identical inputs yields identical numbers. Agent
  success ≠ product viability — keep them separate.

PARAMETERS
  Thresholds are frozen inside calibration_agent and lead_moat_agent (versioned there).
  This orchestrator adds only: STRICT (env NOWTRENDIN_AGENT_STRICT=1) → exit non-zero
  when integrity defects exist, so a scheduler can page on them.

GOTCHAS
  • Run order matters: source attribution (from the ledger) must compute BEFORE the
    source gate uses it — the agent enforces this.
  • The gate classifies on attribution; below the per-source minimum it abstains
    (UNKNOWN), so don't read source verdicts off a tiny ledger.
  • Lead sign: lead = breakout − detection, POSITIVE = early. One convention throughout.
  • Read-only: the only write is append_calibration_epoch (separate store, never the
    ledger's verdict columns or production score tables).

DEPLOY (Heroku — backend + engine are both there)
  • Engine SQLite (worker dyno):  python nowtrendin_agent.py --sqlite
  • Backend Postgres (Heroku Scheduler): python nowtrendin_agent.py --postgres
    (requires DATABASE_URL env var and nowtrendin_data_adapter.py configured)
  • Or wrap run_nightly(adapter) in a Django management command.

Run `python nowtrendin_agent.py` with no args to see the full combined report on
synthetic data.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime, timezone, timedelta
from typing import Optional
import json, logging, os, sys

import calibration_agent as CA
import lead_moat_agent as LMA
try:
    import trend_signal_diagnostic as TSD
    import market_signal_diagnostic as MSD
    _DIAGS = True
except Exception:
    _DIAGS = False

log = logging.getLogger("nowtrendin_agent")


# ═════════════════════════════════════════════════════════════════════════════
# THE ONE THING YOUR DEV IMPLEMENTS
# ═════════════════════════════════════════════════════════════════════════════
class NowTrendInDataAdapter(ABC):
    """Implement once against your DB. Every method is read-only except the last."""

    # — engine health —
    @abstractmethod
    def live_trend_topics(self) -> list: ...          # list[TSD.TopicInput]
    @abstractmethod
    def live_market_instruments(self) -> list: ...    # list[MSD.InstrumentInput]

    # — ledger + viability —
    @abstractmethod
    def ledger_rows(self) -> list: ...                # list[CA.LedgerRow]
    @abstractmethod
    def detection_series(self, topic: str): ...       # CA.Series | None  (Detection vs Trends)
    @abstractmethod
    def source_first_seen(self, topic: str) -> dict: ...

    # — audited lead vs Google Trends —
    @abstractmethod
    def gt_series(self, topic: str) -> list: ...      # list[(date, value)]
    @abstractmethod
    def topic_sources(self, topic: str) -> list: ...

    # — discovery —
    @abstractmethod
    def leading_source_feeds(self) -> dict: ...       # {source: [(term, recent_counts)]}
    @abstractmethod
    def is_already_tracked(self, term: str) -> bool: ...
    @abstractmethod
    def gt_has_broken_out(self, term: str) -> bool: ...

    # — meta —
    @abstractmethod
    def methodology_version(self) -> str: ...
    @abstractmethod
    def append_calibration_epoch(self, record: dict) -> None: ...   # append-only, separate store


# ═════════════════════════════════════════════════════════════════════════════
# COMBINED REPORT
# ═════════════════════════════════════════════════════════════════════════════
@dataclass
class CombinedReport:
    run_at: str
    methodology_version: str
    health: dict = field(default_factory=dict)
    ledger: dict = field(default_factory=dict)
    gate: dict = field(default_factory=dict)
    sources: dict = field(default_factory=dict)
    lead_vs_gt: dict = field(default_factory=dict)
    source_gate: dict = field(default_factory=dict)
    discovery: list = field(default_factory=list)
    alerts: list = field(default_factory=list)
    standing: str = ""

    def to_json(self) -> str:
        d = dict(self.__dict__)
        d["discovery"] = [c.__dict__ if not isinstance(c, dict) else c for c in self.discovery]
        return json.dumps(d, default=str, indent=2)


# ═════════════════════════════════════════════════════════════════════════════
# THE RUN
# ═════════════════════════════════════════════════════════════════════════════
def run_nightly(adapter: NowTrendInDataAdapter, today: Optional[date] = None) -> CombinedReport:
    today = today or date.today()
    rep = CombinedReport(run_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                         methodology_version=adapter.methodology_version())

    # 1–4 · defense (calibration_agent)
    rep.health = CA.engine_health(adapter.live_trend_topics(), adapter.live_market_instruments())
    rows = adapter.ledger_rows()
    audit = CA.ledger_audit(rows, today)
    rep.ledger = {k: (len(v) if isinstance(v, list) else v) for k, v in audit.items()}
    rep.gate = {k: v for k, v in
                CA.viability_gate(audit["matched_resolved"], adapter.detection_series).items()
                if k != "per_topic"}
    rep.sources = CA.source_attribution(rows, adapter.source_first_seen)

    # 5–6 · offense (lead_moat_agent) — attribution MUST precede the gate
    # For resolved rows the ledger already has the breakout_date — build the receipt
    # directly without a live GT call. Only pending rows need GT to check for breakout.
    receipts = []
    for r in rows:
        if r.breakout_date is not None:
            # Already resolved: use stored breakout_date — no API call needed.
            lead = (r.breakout_date - r.detection_date).days
            verdict = "LED" if lead >= 1 else ("SAME_DAY" if lead == 0 else "LAGGED")
            text = (f"{r.topic}: we flagged it {r.detection_date}; "
                    f"Google Trends broke out {r.breakout_date} → lead {lead:+d}d ({verdict}).")
            receipts.append(LMA.Receipt(r.topic, r.detection_date, r.breakout_date,
                                        lead, verdict, adapter.topic_sources(r.topic), text))
        else:
            # Still pending: call GT to see if it has broken out since last run.
            receipts.append(LMA.audit_topic(r.topic, r.detection_date,
                                            adapter.gt_series(r.topic),
                                            adapter.topic_sources(r.topic)))
    rep.lead_vs_gt = LMA.gt_scorecard(receipts)
    attribution = {s: d["median_lead"] for s, d in rep.sources.items()}
    counts = {s: d["n"] for s, d in rep.sources.items()}
    classification = LMA.classify_sources(attribution, counts)
    rep.source_gate = {"classification": classification,
                       **LMA.segmented_scorecard(receipts, classification, adapter.topic_sources)}

    # 7 · discovery
    rep.discovery = LMA.discover(adapter.leading_source_feeds(),
                                 adapter.is_already_tracked, adapter.gt_has_broken_out, today)

    # 8 · alerts + standing
    rep.alerts = _alerts(rep, audit)
    rep.standing = _standing(rep)

    # append-only epoch (the only write)
    try:
        adapter.append_calibration_epoch({
            "run_at": rep.run_at, "methodology_version": rep.methodology_version,
            "param_versions": [CA.PARAM_VERSION, LMA.PARAM_VERSION],
            "health": rep.health, "ledger": rep.ledger, "gate": rep.gate,
            "lead_vs_gt": {k: v for k, v in rep.lead_vs_gt.items() if k != "receipts"},
            "source_gate": rep.source_gate,
            "discovery": [c.__dict__ for c in rep.discovery],
            "alerts": rep.alerts, "standing": rep.standing,
            "row_receipts": rep.lead_vs_gt.get("receipts", []),
        })
    except Exception as e:
        log.warning("epoch write skipped: %s", e)

    return rep


def _alerts(rep: CombinedReport, audit: dict) -> list:
    a = []
    if audit["stale_matches"]:
        a.append(f"{len(audit['stale_matches'])} stale ledger matches (>±{CA.MATCH_WINDOW_DAYS}d) "
                 f"— fix same-surge matching before trusting lead numbers.")
    if audit["fp_overdue"]:
        a.append(f"{len(audit['fp_overdue'])} detections overdue past FP timeout — resolve as False Positive.")
    for v, n in rep.health.items():
        if v.endswith("UNDOCUMENTED_INPUT") and n:
            a.append(f"{n} topics: score doesn't reconcile to G/I/M/D/C (N/P leak?) — governance check.")
        if v.endswith("WHATIF_N_INVERTED") and n:
            a.append(f"{n} topics: what-if-N inverted (high demand lowers the score).")
        if v.endswith("CONTRADICTION") and n:
            a.append(f"{n} instruments: tier vs deviation contradiction.")
    return a


def _standing(rep: CombinedReport) -> str:
    g = rep.gate.get("status", "?")
    lg = rep.lead_vs_gt
    seg = rep.source_gate.get("leadable_universe", {})
    parts = [f"Viability gate: {g}"]
    if lg.get("n_resolved"):
        parts.append(f"Audited lead vs Google Trends: LED {lg['led']}/{lg['n_resolved']} "
                     f"(rate {lg['led_rate']}, median {lg['median_lead']}d, max {lg['max_lead']}d)")
    if seg:
        parts.append(f"Leadable-universe LED-rate {seg.get('led_rate')} (median {seg.get('median_lead')}d)")
    parts.append(f"{len(rep.discovery)} new pre-mainstream candidates")
    return " · ".join(parts)


# ═════════════════════════════════════════════════════════════════════════════
# REPORT PRINTING
# ═════════════════════════════════════════════════════════════════════════════
def print_report(rep: CombinedReport) -> None:
    L = "█" * 78
    print(f"\n{L}\n  NOW TRENDIN — NIGHTLY AUDIT · {rep.run_at}\n  engine {rep.methodology_version}\n{L}")
    print(f"\n  ▸ WHERE WE STAND\n    {rep.standing}")
    if rep.alerts:
        print("\n  ⚠ ALERTS")
        for x in rep.alerts:
            print(f"    • {x}")

    print("\n  ▸ ENGINE HEALTH")
    for k, v in sorted(rep.health.items()):
        print(f"    {k:<34} {v}")

    print("\n  ▸ LEDGER INTEGRITY")
    print(f"    stale matches {rep.ledger.get('stale_matches')} · "
          f"FP overdue {rep.ledger.get('fp_overdue')} · "
          f"immature {rep.ledger.get('immature_pending')} · "
          f"matured matched {rep.ledger.get('matched_resolved')}")

    g = rep.gate
    print("\n  ▸ VIABILITY GATE")
    print(f"    status {g.get('status')} — {g.get('note')}")
    print(f"    n={g.get('n_matched')} (need ≥ {CA.GATE_MIN_RESOLVED}) · "
          f"median lead {g.get('median_lead')} (bar ≥ +{CA.GATE_MEDIAN_LEAD_MIN}) · "
          f"CI {g.get('lead_ci95')} · LED {g.get('led_rate')} / FP {g.get('fp_rate')}")

    print("\n  ▸ AUDITED LEAD vs GOOGLE TRENDS")
    lg = rep.lead_vs_gt
    print(f"    resolved {lg.get('n_resolved')} · pending {lg.get('n_pending')} · "
          f"LED {lg.get('led')} · rate {lg.get('led_rate')} · "
          f"median {lg.get('median_lead')}d · max {lg.get('max_lead')}d · {lg.get('verdict_breakdown')}")
    for line in lg.get("receipts", [])[:6]:
        print(f"      • {line}")

    print("\n  ▸ SOURCE LEAD GATE")
    print(f"    classification {rep.source_gate.get('classification')}")
    print(f"    leadable universe : {rep.source_gate.get('leadable_universe')}")
    print(f"    full coverage     : {rep.source_gate.get('full_coverage')}")

    print("\n  ▸ OPEN-WORLD DISCOVERY")
    if not rep.discovery:
        print("    (none cleared the bar)")
    for c in rep.discovery[:8]:
        print(f"    • {c.term:<24} via {c.source:<10} {c.velocity}×  → log as early detection")
    print(f"\n{L}\n")


# ═════════════════════════════════════════════════════════════════════════════
# DEMO ADAPTER  (so the file runs end-to-end with no wiring)
# ═════════════════════════════════════════════════════════════════════════════
class _DemoAdapter(NowTrendInDataAdapter):
    def __init__(self):
        self.D = lambda d: date(2026, 6, 1) + timedelta(days=d)
        self.epochs = []

    def _gt(self, breakout_offset, base=8, spike=60):
        return [(self.D(i), base if (breakout_offset is None or i < breakout_offset) else spike)
                for i in range(-30, 18)]

    def live_trend_topics(self):
        return [TSD._example_fifa(), TSD._example_musk(), TSD._example_healthy()] if _DIAGS else []
    def live_market_instruments(self):
        return [MSD._example_spcx(), MSD._example_healthy()] if _DIAGS else []

    def ledger_rows(self):
        D = self.D
        return [
            CA.LedgerRow("rust async runtime", D(3), D(11), "LED", "github", D(3)),
            CA.LedgerRow("model context protocol", D(1), D(-4), "LAGGED", "sweep", D(1)),
            CA.LedgerRow("Donald Trump", D(12), D(-2), "LAGGED", "apify", D(12)),
            CA.LedgerRow("nukes", D(10), D(-90), "LAGGED", "apify", D(10)),       # stale -> flagged
            CA.LedgerRow("neuromorphic inference", D(6), None, None, "arxiv", D(6)),  # pending
        ]

    def detection_series(self, topic):
        m = {"rust async runtime": 8, "model context protocol": -6, "Donald Trump": -14}
        if topic not in m:
            return None
        lead = m[topic]
        dts = [self.D(i) for i in range(-20, 20)]
        det = [max(0, 60 - abs(i) * 4) for i in range(-20, 20)]
        tr = [max(0, 60 - abs(i - lead) * 4) for i in range(-20, 20)]
        return CA.Series(dts, det, tr)

    def source_first_seen(self, topic):
        D = self.D
        return {"rust async runtime": {"github": D(-2), "hackernews": D(0)},
                "model context protocol": {"github": D(-1), "sweep": D(1)},
                "Donald Trump": {"apify": D(12)},
                "nukes": {"apify": D(10)},
                "neuromorphic inference": {"arxiv": D(-3)}}.get(topic, {})

    def gt_series(self, topic):
        return {"rust async runtime": self._gt(11), "model context protocol": self._gt(-4),
                "Donald Trump": self._gt(-2), "nukes": self._gt(-12),
                "neuromorphic inference": self._gt(None)}.get(topic, self._gt(None))

    def topic_sources(self, topic):
        return {"rust async runtime": ["github", "hackernews"],
                "model context protocol": ["github", "sweep"],
                "Donald Trump": ["apify"], "nukes": ["apify"],
                "neuromorphic inference": ["arxiv", "hackernews"]}.get(topic, [])

    def leading_source_feeds(self):
        return {"arxiv": [("state space models v2", [1, 1, 2, 3, 7, 11]),
                          ("retrieval pretraining", [2, 2, 2, 2, 2, 2])],
                "github": [("ziglang orm", [0, 1, 1, 4, 9, 14])],
                "apify": [("celebrity gossip x", [5, 9, 20, 40, 80, 120])]}
    def is_already_tracked(self, term): return term == "retrieval pretraining"
    def gt_has_broken_out(self, term): return False

    def methodology_version(self): return "grad-v2.4 / mkt-v1.2"
    def append_calibration_epoch(self, record): self.epochs.append(record)


# ═════════════════════════════════════════════════════════════════════════════
# SQLITE RUNNER — uses the calibration_agent's already-wired loaders
# ═════════════════════════════════════════════════════════════════════════════
def run_sqlite(today: Optional[date] = None) -> Optional[CombinedReport]:
    """Run the nightly audit against the live SQLite engine DB.
    Uses the loaders already wired in calibration_agent.py.
    For a full adapter with discovery wiring, use nowtrendin_data_adapter.py."""
    try:
        from nowtrendin_data_adapter import SQLiteAdapter
        adapter = SQLiteAdapter()
        rep = run_nightly(adapter, today)
        return rep
    except ImportError:
        log.warning("nowtrendin_data_adapter not found — SQLite adapter unavailable")
        return None
    except Exception as e:
        log.error("run_sqlite error: %s", e)
        return None


# ═════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════
def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    strict = os.getenv("NOWTRENDIN_AGENT_STRICT") == "1"

    if "--sqlite" in sys.argv:
        rep = run_sqlite()
        if rep is None:
            print("SQLite adapter unavailable — check nowtrendin_data_adapter.py")
            return 1
    elif "--demo" in sys.argv or len(sys.argv) == 1:
        adapter = _DemoAdapter()
        rep = run_nightly(adapter, today=adapter.D(25))
    else:
        print("Usage: python nowtrendin_agent.py [--demo | --sqlite]")
        print("  --demo    run on synthetic data (no DB needed)")
        print("  --sqlite  run on live engine SQLite DB (requires nowtrendin_data_adapter.py)")
        return 0

    print_report(rep)
    return 2 if (strict and rep.alerts) else 0


if __name__ == "__main__":
    sys.exit(main())
