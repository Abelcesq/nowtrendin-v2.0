"""
nowtrendin_data_adapter.py
==========================
Concrete NowTrendInDataAdapter wired to the NowTrendIn v2 engine's SQLite DB
(anomaly_detector.db, accessed via GAD_DB_PATH env var).

Reuses the loaders already implemented in calibration_agent.py for the
ledger/detection-series/epoch methods. Adds the lead_moat_agent wiring:
  • gt_series        — google_trends_validation.fetch_trends_curve → (date, value) list
  • topic_sources    — topic_signals table, distinct platforms per topic
  • leading_source_feeds — topic_signals grouped by leading platform × day × topic
  • is_already_tracked   — topic_registry lookup
  • gt_has_broken_out    — reuses LMA.detect_gt_breakout on the GT series

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

    # ── reuse calibration_agent's already-wired loaders ──────────────────────

    def live_trend_topics(self) -> list:
        return CA.load_live_topics()

    def live_market_instruments(self) -> list:
        return CA.load_live_instruments()

    def ledger_rows(self) -> list:
        return CA.load_ledger_rows()

    def detection_series(self, topic: str):
        return CA.load_detection_series(topic)

    def source_first_seen(self, topic: str) -> dict:
        return CA.load_source_first_seen(topic)

    def methodology_version(self) -> str:
        return CA.get_methodology_version()

    def append_calibration_epoch(self, record: dict) -> None:
        CA.write_calibration_epoch(record)

    # ── lead_moat_agent wiring ───────────────────────────────────────────────

    def gt_series(self, topic: str) -> list:
        """[(date, value)] daily Google Trends. Cached once per run per topic."""
        if topic in self._gt_cache:
            return self._gt_cache[topic]
        series = []
        try:
            from google_trends_validation import fetch_trends_curve
            curve = fetch_trends_curve(topic) or []
            for pt in curve:
                try:
                    ds = str(pt.get("date", ""))[:10]
                    if ds:
                        d = date.fromisoformat(ds)
                        series.append((d, float(pt.get("value", 0))))
                except Exception:
                    pass
        except Exception as e:
            log.debug("gt_series(%s) error: %s", topic, e)
        self._gt_cache[topic] = series
        return series

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
        """Already mainstream? Use the same breakout rule as the ledger."""
        return LMA.detect_gt_breakout(self.gt_series(term)) is not None


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
    strict = os.getenv("NOWTRENDIN_AGENT_STRICT") == "1"
    return 2 if (strict and rep.alerts) else 0


if __name__ == "__main__":
    raise SystemExit(main())
