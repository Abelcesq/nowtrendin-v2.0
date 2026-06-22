"""
nowtrendin_data_adapter.py
==========================
Concrete NowTrendInDataAdapter wired to the NowTrendIn v2 engine's SQLite DB
(anomaly_detector.db, accessed via GAD_DB_PATH env var).

READ-ONLY CALIBRATOR — STORED DATA ONLY. This adapter never fires a live
Google-Trends/Apify pull or a live ticker lookup. It CALIBRATES the data the
engine already collected (accuracy_ledger, velocity_scores, topic_signals); the
Apify spend lives in the engine's own 6h validation cycle, not here. Abstaining
(returning [] / None) where stored data is absent is required by the charter's
reproducibility rule — a fresh GT pull renormalizes per window and would make the
same run non-reproducible.

Reuses the loaders already implemented in calibration_agent.py for the
ledger/epoch methods. Adds the lead_moat_agent wiring:
  • gt_series        — STORED-ONLY abstain → [] (no live pull; lead comes from ledger)
  • detection_series — STORED-ONLY abstain → None (no cached GT curve to align to)
  • topic_sources    — topic_signals table, distinct platforms per topic
  • leading_source_feeds — topic_signals grouped by leading platform × day × topic
  • is_already_tracked   — topic_registry / velocity_scores lookup
  • gt_has_broken_out    — accuracy_ledger breakout_date lookup (no live pull)

Schema notes (all in anomaly_detector.db):
  velocity_scores : topic_key, topic_display, scored_at, detection_score,
                    confidence_score, overall_score, gradient_strength,
                    inertia_score, platform_diversity, dark_matter_score,
                    confidence_decay, persistence_score, nowtrendin_score
  topic_signals   : topic, topic_key, platform, source_name, extracted_at,
                    signal_id, upvotes, comments, engagement_raw,
                    is_first_timer, is_organic
  topic_registry  : topic_key, topic_display, first_seen_at, first_seen_platform
  accuracy_ledger : (via accuracy_ledger_enhanced.py)
  pending_detections: (via accuracy_ledger_enhanced.py)

Run `python nowtrendin_data_adapter.py` to execute the nightly audit on live data.
"""

from __future__ import annotations
from datetime import date, datetime, timezone, timedelta
from typing import Optional
import os, logging

import db_compat
import calibration_agent as CA
import lead_moat_agent as LMA
import nowtrendin_agent as AGENT

log = logging.getLogger("nowtrendin_data_adapter")

# ── Google Trends window — keep constant across runs (GT is renormalized per window)
GT_LOOKBACK_DAYS = 180

# ── Platform → leading-source canonical name mapping
_PLATFORM_TO_LEADING = {
    "github": "github",
    "hackernews": "hackernews",
    "hn": "hackernews",
    "arxiv": "arxiv",
    "devto": "dev",
    "dev_to": "dev",
    "dev.to": "dev",
    "dev": "dev",
    "firecrawl_web": "dev",   # Firecrawl web discovery treated as pre-mainstream (dev-tier)
}
LEADING_SOURCES = set(_PLATFORM_TO_LEADING.values())   # {"github","hackernews","arxiv","dev"}

# ── Rolling window for discovery velocity calculation (days)
DISCOVERY_WINDOW_DAYS = 14


class SQLiteAdapter(AGENT.NowTrendInDataAdapter):
    """Concrete adapter for the engine's SQLite DB. Read-only except epoch write."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv("GAD_DB_PATH", "anomaly_detector.db")
        self._gt_cache: dict = {}   # topic → list[(date, float)]; cached per run
        # Read-only calibrator: NEVER resolve tickers via the live API. The market
        # engine-health sweep reads market_signal_history by its stored item_key
        # only (resolve_ticker's 429 retries hung the job for 50 min). See the
        # MSD_SKIP_RESOLVE guard in market_signal_diagnostic.load_diagnostic_input.
        os.environ["MSD_SKIP_RESOLVE"] = "1"

    # ── reuse calibration_agent's already-wired loaders ──────────────────────

    def live_trend_topics(self) -> list:
        return CA.load_live_topics()

    def live_market_instruments(self) -> list:
        return CA.load_live_instruments()

    def ledger_rows(self) -> list:
        return CA.load_ledger_rows()

    def detection_series(self, topic: str):
        """STORED-ONLY abstain. The cross-correlation viability gate needs a
        day-aligned (Detection, Google Trends) series, but the engine does NOT
        persist the GT interest curve — so producing one would require a fresh
        Apify pull, which this read-only calibrator must never do (cost +
        non-reproducible, since GT renormalizes per window). Returns None; the
        gate counts it as no-series and falls through to INSUFFICIENT. The
        headline lead-vs-GT comes from the STORED ledger, not this path.
        (Follow-up: have the engine cache GT curves so the gate can read them.)"""
        return None

    def source_first_seen(self, topic: str) -> dict:
        return CA.load_source_first_seen(topic)

    def methodology_version(self) -> str:
        return CA.get_methodology_version()

    def append_calibration_epoch(self, record: dict) -> None:
        CA.write_calibration_epoch(record)

    # ── lead_moat_agent wiring ───────────────────────────────────────────────

    def gt_series(self, topic: str) -> list:
        """STORED-ONLY: returns []. The engine does not cache the GT interest
        curve, so the audit abstains here rather than firing a fresh Apify pull.
        A live pull would (a) cost credits on every run and (b) break the charter's
        reproducibility rule (GT is renormalized per query window, so the same
        topic returns different numbers each pull). The audited lead vs Google
        Trends is taken from the engine's STORED accuracy_ledger
        (breakout_date / verdict / lead_time_days) in run_nightly, NOT recomputed
        here. The Apify spend lives in the engine's own 6h validation cycle."""
        return []

    def topic_sources(self, topic: str) -> list:
        """Distinct platforms that produced signals for this topic."""
        try:
            conn = db_compat.connect(self.db_path)
            # Match both by topic_key and by fuzzy display-name
            key = topic.lower().strip().replace(" ", "_")[:80]
            rows = conn.execute(
                "SELECT DISTINCT platform FROM topic_signals "
                "WHERE topic_key = ? OR lower(topic) = ? LIMIT 20",
                (key, topic.lower().strip())
            ).fetchall()
            conn.close()
            # Normalize to canonical leading-source names where applicable
            seen, out = set(), []
            for row in rows:
                p = row["platform"] if hasattr(row, "keys") else row[0]
                canonical = _PLATFORM_TO_LEADING.get((p or "").lower(), p)
                if canonical and canonical not in seen:
                    seen.add(canonical)
                    out.append(canonical)
            return out
        except Exception as e:
            log.debug("topic_sources(%s) error: %s", topic, e)
            return []

    def leading_source_feeds(self) -> dict:
        """
        {source: [(term, recent_daily_counts)]} for the LEADING sources only.
        Pulls topic_signals from the last DISCOVERY_WINDOW_DAYS days, groups by
        platform → topic → day, and computes daily counts. Only platforms that map
        to a leading source are included; the 'apify' and 'news' family are excluded.
        """
        out: dict = {src: [] for src in LEADING_SOURCES}
        try:
            conn = db_compat.connect(self.db_path)
            since = (datetime.now(timezone.utc) - timedelta(days=DISCOVERY_WINDOW_DAYS)).isoformat()
            rows = conn.execute("""
                SELECT platform, topic, date(extracted_at) AS day, COUNT(*) AS n
                FROM   topic_signals
                WHERE  extracted_at >= ?
                GROUP  BY platform, topic, day
                ORDER  BY platform, topic, day ASC
            """, (since,)).fetchall()
            conn.close()

            # Build {canonical_src: {topic: [daily_counts ordered by day]}}
            by_src: dict = {}
            for row in rows:
                if hasattr(row, "keys"):
                    platform, topic, n = row["platform"], row["topic"], row["n"]
                else:
                    platform, topic, _day, n = row
                canonical = _PLATFORM_TO_LEADING.get((platform or "").lower())
                if canonical is None:
                    continue   # not a leading source
                by_src.setdefault(canonical, {}).setdefault(topic, []).append(int(n))

            for src, topics in by_src.items():
                out[src] = [(t, counts) for t, counts in topics.items()
                            if len(counts) >= 2]    # need ≥ 2 days for velocity
        except Exception as e:
            log.debug("leading_source_feeds error: %s", e)
        return out

    def is_already_tracked(self, term: str) -> bool:
        """True if the term already exists in topic_registry or velocity_scores."""
        try:
            conn = db_compat.connect(self.db_path)
            key = term.lower().strip().replace(" ", "_")[:80]
            row = conn.execute(
                "SELECT 1 FROM topic_registry "
                "WHERE lower(topic_key) = ? OR lower(topic_display) = ? LIMIT 1",
                (key, term.lower().strip())
            ).fetchone()
            if row:
                conn.close()
                return True
            # also check velocity_scores for topics scored without a registry entry
            row2 = conn.execute(
                "SELECT 1 FROM velocity_scores "
                "WHERE lower(topic_key) = ? OR lower(topic_display) = ? LIMIT 1",
                (key, term.lower().strip())
            ).fetchone()
            conn.close()
            return row2 is not None
        except Exception as e:
            log.debug("is_already_tracked(%s) error: %s", term, e)
            return False

    def gt_has_broken_out(self, term: str) -> bool:
        """STORED-ONLY: already mainstream? Read the engine's accuracy_ledger —
        no live GT pull. The engine's own validation cycle records breakout_date
        when a topic breaks out on Google Trends; if such a row exists, the term
        is already mainstream and is NOT a pre-mainstream discovery candidate.
        Unknown (no ledger row) ⇒ treat as not-yet-broken-out: discovery only
        PROPOSES candidates, and the engine's cycle validates them later."""
        try:
            conn = db_compat.connect(self.db_path)
            key = term.lower().strip().replace(" ", "_")[:80]
            row = conn.execute(
                "SELECT 1 FROM accuracy_ledger "
                "WHERE (lower(topic_key) = ? OR lower(topic_display) = ?) "
                "AND breakout_date IS NOT NULL AND breakout_date != '' LIMIT 1",
                (key, term.lower().strip())
            ).fetchone()
            conn.close()
            return row is not None
        except Exception as e:
            log.debug("gt_has_broken_out(%s) error: %s", term, e)
            return False


# ═════════════════════════════════════════════════════════════════════════════
# ENTRY POINT — runs the full nightly audit on live data (Postgres or SQLite)
# ═════════════════════════════════════════════════════════════════════════════
def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    use_pg = bool(os.getenv("DATABASE_URL"))
    db = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
    # When DATABASE_URL is set, db_compat ignores the file path and uses Postgres.
    # Only gate on file existence for pure-SQLite setups.
    if not use_pg and not os.path.exists(db):
        print(f"[adapter] DB not found at {db!r} — set GAD_DB_PATH or DATABASE_URL.")
        print("[adapter] To see a synthetic demo run:  python nowtrendin_agent.py --demo")
        return 1

    adapter = SQLiteAdapter(db)
    rep = AGENT.run_nightly(adapter, today=date.today())
    AGENT.print_report(rep)

    # Ingestion Gate — surface any quarantined format values awaiting a human decision.
    pending = []
    try:
        import ingestion_gate
        conn = db_compat.connect(db)
        pending = ingestion_gate.pending_reviews(conn)
        conn.close()
    except Exception as e:
        log.debug("format-review surface error: %s", e)
    if pending:
        print(f"\n  ⚠ FORMAT REVIEW QUEUE — {len(pending)} value(s) need a human decision:")
        for p in pending[:20]:
            print(f"      • {p['table_name']}.{p['column_name']}  raw={p['raw_value']!r}  "
                  f"source={p['source']}  candidates=[{p['candidates']}]  (id {p['id']})")
        print("      Resolve with ingestion_gate.resolve_review(conn, id, 'YYYY-MM-DD').")

    strict = os.getenv("NOWTRENDIN_AGENT_STRICT") == "1"
    return 2 if (strict and (rep.alerts or pending)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
