"""
================================================================
NOW TRENDIN — GRADIENT SCORE + PIPELINE INTEGRATION
================================================================

WHAT THIS FILE DOES:
Wires gradient_engine_backend.py and nowtrend_pipeline_architecture.py
into one unified system. Every Gradient Score the engine computes
automatically enters the pipeline tracker, gets pushed to Snowflake,
formatted for Bloomberg, and served through the institutional API.

FILE RELATIONSHIPS:
  gradient_engine_backend.py      → Collects signals, computes scores
  nowtrend_pipeline_architecture.py → Tracks scores to financial outcomes
  THIS FILE                        → Connects them end to end

HOW TO RUN:
  # Step 1: Collect signals and compute scores
  python integration.py --mode=collect

  # Step 2: Score all topics and auto-enter pipeline
  python integration.py --mode=score

  # Step 3: Validate pipeline with historical cases
  python integration.py --mode=validate

  # Step 4: View current alpha metrics (your institutional sales pitch)
  python integration.py --mode=alpha

  # Step 5: Start the unified API (gradient + pipeline + institutional)
  python integration.py --mode=api

INSTALL:
  pip install praw requests fastapi uvicorn vaderSentiment
  python-dotenv snowflake-connector-python pandas numpy scipy
================================================================
"""

import os
import sys
import json
import uuid
import sqlite3
import argparse
from datetime import datetime, timezone, timedelta
from typing import Optional
from dataclasses import asdict

# ── Import both modules ───────────────────────────────────────────
# Adjust paths if files are in subdirectories
sys.path.insert(0, os.path.dirname(__file__))

from gradient_engine_backend import (
    # Data models
    GradientScore,
    RawSignal,
    # Database functions
    init_db as init_gradient_db,
    get_db as get_gradient_db,
    insert_signals,
    save_gradient_score,
    fetch_top_scores,
    fetch_score_history,
    fetch_recent_signals,
    fetch_all_topics_with_signals,
    # Collectors
    get_reddit_client,
    collect_reddit,
    collect_github,
    collect_hackernews,
    # Scoring
    compute_gradient_score,
    normalize_topic,
    # App
    app as gradient_app,
)

from nowtrend_pipeline_architecture import (
    # Pipeline tracking
    PipelineTracker,
    AlphaCalculator,
    # Distribution
    SnowflakePublisher,
    BloombergFormatter,
    # Institutional API
    create_institutional_api,
    # Validation
    run_historical_validation,
    HISTORICAL_VALIDATION_CASES,
    # Database
    init_pipeline_db,
)

import uvicorn
from fastapi import FastAPI, HTTPException, Header, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ── Extensions layer (auditability, calibration, scenarios) ───────
try:
    from gradient_engine_extensions import (
        init_extensions,
        ext_router as _ext_router,
    )
    _EXTENSIONS_AVAILABLE = True
except ImportError:
    _EXTENSIONS_AVAILABLE = False

# ── Configuration ─────────────────────────────────────────────────
GRADIENT_DB   = os.getenv("GRADIENT_DB",  "gradient_scores.db")
PIPELINE_DB   = os.getenv("PIPELINE_DB",  "pipeline_tracker.db")
API_PORT      = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))  # $PORT on Heroku
INST_API_PORT = int(os.getenv("INST_API_PORT", "8001"))


# ==================================================================
# SECTION 1: THE FIVE GRADIENT SCORE VARIABLES — EXPLICIT MAPPING
#
# These are the variables defined in this conversation and how
# they flow from the engine into the pipeline tracker.
# ==================================================================

"""
VARIABLE MAP: GradientScore → Pipeline + Downstream Systems
===============================================================

COMPONENT         | ENGINE FIELD              | WEIGHT | PURPOSE
──────────────────┼───────────────────────────┼────────┼────────────────────────────
Gradient Strength | gradient_strength         | 30%    | Niche vs mainstream ratio
                  |                           |        | HIGH = still in expert layer
                  |                           |        | LOW  = already mainstream
                  |                           |        |
Inertia           | inertia_score             | 25%    | Self-reinforcing momentum
                  |                           |        | HIGH = sustained acceleration
                  |                           |        | LOW  = one-day spike
                  |                           |        |
Medium Sequence   | medium_sequence_score     | 20%    | Platform diffusion pattern
                  |                           |        | Pattern A = Builder→Buyer
                  |                           |        | Pattern B = Culture spread
                  |                           |        | Pattern C = Research→Commerce
                  |                           |        |
Dark Matter       | dark_matter_score         | 15%    | Hidden private conversation
                  |                           |        | Measured via:
                  |                           |        | - first_timer_ratio
                  |                           |        | - engagement_asymmetry
                  |                           |        | - vocabulary_clustering
                  |                           |        |
Confidence Decay  | confidence_decay          | 10%    | Signal freshness + direction
                  |                           |        | HIGH = fresh + rising
                  |                           |        | LOW  = old or declining

DUAL OUTPUT (Heisenberg Split):
  detection_score   = G(0.40) + D(0.25) + I(0.20) + M(0.10) + C(0.05)
                      → Optimized for EARLINESS (accepts more false alarms)
                      → For creators, marketers, fast-moving brands

  confidence_score  = I(0.35) + M(0.30) + G(0.20) + C(0.10) + D(0.05)
                      → Optimized for PRECISION (fewer false alarms)
                      → For hedge funds, institutions, strategic planners

OVERALL SCORE (balanced):
  overall_score = G(0.30) + I(0.25) + M(0.20) + D(0.15) + C(0.10)

DOWNSTREAM ROUTING:
  overall_score  ≥ 85 → BREAKOUT: pipeline_tracker + Snowflake + Bloomberg + push alert
  overall_score  ≥ 70 → ANOMALY:  pipeline_tracker + Snowflake + push alert
  overall_score  ≥ 55 → RISING:   pipeline_tracker + Snowflake
  overall_score  < 20 → DECAY:    pipeline_tracker (decay flag)
"""


# ==================================================================
# SECTION 2: THE INTEGRATION BRIDGE
# Routes every scored signal into the full downstream stack
# ==================================================================

class GradientPipelineBridge:
    """
    THE CENTRAL INTEGRATION POINT.

    Every time the Gradient Score Engine produces a score,
    this bridge routes it to:
      1. Pipeline Tracker  (proof document building)
      2. Snowflake         (marketplace distribution)
      3. Bloomberg         (terminal integration queue)
      4. Alert System      (push notifications for breakouts)

    Usage:
        bridge = GradientPipelineBridge()
        bridge.process_score(gradient_score_object)
    """

    def __init__(self):
        # Initialize both databases
        init_gradient_db(GRADIENT_DB)
        init_pipeline_db(PIPELINE_DB)

        self.tracker   = PipelineTracker(PIPELINE_DB)
        self.snowflake = SnowflakePublisher()
        self.bloomberg = BloombergFormatter()

        print("[OK] GradientPipelineBridge initialized")
        print(f"  Gradient DB: {GRADIENT_DB}")
        print(f"  Pipeline DB: {PIPELINE_DB}")

    def process_score(self, gs: GradientScore, auto_publish: bool = True):
        """
        THE MAIN INTEGRATION METHOD.

        Takes a completed GradientScore object from the engine
        and routes it through the entire downstream stack.

        Args:
            gs:           Completed GradientScore from compute_gradient_score()
            auto_publish: Push to Snowflake immediately (False = queue for batch)
        """
        print(f"\n>> Processing: '{gs.topic}' | Score: {gs.overall_score}")

        # ── Step 1: Save to gradient database ────────────────────
        save_gradient_score(gs)

        # ── Step 2: Enter pipeline tracker ───────────────────────
        # This starts the 5-stage tracking journey
        event_id = self.tracker.record_gradient_detection(
            topic              = gs.topic,
            topic_normalized   = normalize_topic(gs.topic),
            gradient_score     = gs.overall_score,
            detection_score    = gs.detection_score,
            confidence_score   = gs.confidence_score,
            dark_matter_score  = gs.dark_matter_score,
            diffusion_pattern  = gs.diffusion_pattern,
            category           = "ai_consumer_tech",
        )
        print(f"  [OK]Pipeline entry created: {event_id}")

        # ── Step 3: Route by score threshold ─────────────────────
        action = self._classify_action(gs)
        print(f"  [OK]Action: {action}")

        # ── Step 4: Snowflake (breakout + anomaly signals) ───────
        if auto_publish and gs.overall_score >= 55:
            score_dict = asdict(gs)
            published = self.snowflake.publish_score(score_dict)
            if published:
                print(f"  [OK]Published to Snowflake Marketplace")

        # ── Step 5: Bloomberg queue (breakout signals only) ───────
        if gs.overall_score >= 70:
            self._queue_for_bloomberg(gs)
            print(f"  [OK]Queued for Bloomberg submission")

        # ── Step 6: Alert for high-confidence breakouts ───────────
        if gs.confidence_score >= 70 and gs.overall_score >= 85:
            self._fire_institutional_alert(gs)
            print(f"  [OK]Institutional alert fired")
        elif gs.detection_score >= 84:
            self._fire_consumer_alert(gs)
            print(f"  [OK]Consumer alert fired (high detection)")

        return {
            "topic":          gs.topic,
            "overall_score":  gs.overall_score,
            "detection_score": gs.detection_score,
            "confidence_score": gs.confidence_score,
            "action":         action,
            "pipeline_id":    event_id,
            "components": {
                "G_gradient_strength":  gs.gradient_strength,
                "I_inertia":            gs.inertia_score,
                "M_medium_sequence":    gs.medium_sequence_score,
                "D_dark_matter":        gs.dark_matter_score,
                "C_confidence_decay":   gs.confidence_decay,
            }
        }

    def _classify_action(self, gs: GradientScore) -> str:
        """Maps score thresholds to actionable labels."""
        if gs.overall_score >= 85 and gs.confidence_score >= 65:
            return "BREAKOUT_CONFIRMED"       # Both scores agree: high conviction
        elif gs.overall_score >= 85:
            return "BREAKOUT_DETECTED"        # Early detection, not yet confirmed
        elif gs.overall_score >= 70:
            return "ANOMALY"                  # Strong signal, building confidence
        elif gs.overall_score >= 55:
            return "RISING"                   # Moving, worth watching
        elif gs.overall_score < 20:
            return "DECAY"                    # Was active, now declining
        else:
            return "MONITORING"               # Normal activity range

    def _queue_for_bloomberg(self, gs: GradientScore):
        """Queue a score for Bloomberg Data License submission."""
        conn = sqlite3.connect(PIPELINE_DB)
        conn.execute("""
            INSERT OR IGNORE INTO bloomberg_submissions (
                id, submitted_at, submission_type, records_count, status
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4())[:16],
            datetime.now(timezone.utc).isoformat(),
            "queued",
            1,
            "pending"
        ))
        conn.commit()
        conn.close()

    def _fire_institutional_alert(self, gs: GradientScore):
        """
        Fires an alert for institutional API clients.
        In production: POST to webhook URLs registered by clients,
        or publish to a Redis pub/sub channel.
        For now: logs to alert_log.json for monitoring.
        """
        alert = {
            "timestamp":        datetime.now(timezone.utc).isoformat(),
            "alert_type":       "BREAKOUT_CONFIRMED",
            "topic":            gs.topic,
            "overall_score":    gs.overall_score,
            "detection_score":  gs.detection_score,
            "confidence_score": gs.confidence_score,
            "lead_time_days":   gs.lead_time_estimate_days,
            "diffusion_pattern": gs.diffusion_pattern,
            "dark_matter_flag": gs.dark_matter_score >= 60,
            "first_timer_ratio": gs.first_timer_ratio,
            "components": {
                "G": gs.gradient_strength,
                "I": gs.inertia_score,
                "M": gs.medium_sequence_score,
                "D": gs.dark_matter_score,
                "C": gs.confidence_decay,
            },
            "why":              gs.why_this_matters,
            "what_to_watch":    gs.what_to_watch,
            "target_audience":  "institutional",  # Both scores above threshold
        }
        _append_alert_log(alert)

    def _fire_consumer_alert(self, gs: GradientScore):
        """Fires alert for consumer/creator tier (detection score only)."""
        alert = {
            "timestamp":        datetime.now(timezone.utc).isoformat(),
            "alert_type":       "EARLY_SIGNAL",
            "topic":            gs.topic,
            "detection_score":  gs.detection_score,
            "confidence_score": gs.confidence_score,
            "heisenberg_gap":   gs.detection_score - gs.confidence_score,
            "gap_meaning": (
                "Very early — detected but not yet confirmed"
                if gs.detection_score - gs.confidence_score > 35
                else "Building — confirmation arriving"
            ),
            "lead_time_days":   gs.lead_time_estimate_days,
            "target_audience":  "consumer",  # Detection score high, confidence building
        }
        _append_alert_log(alert)

    def run_collection_cycle(self) -> dict:
        """Run one full collection + scoring cycle end-to-end."""
        print("\n" + "=" * 60)
        print("COLLECTION CYCLE STARTING")
        print("=" * 60)

        # Collect from all three free sources
        reddit = get_reddit_client()
        all_signals = []

        if reddit:
            reddit_signals = collect_reddit(reddit)
            all_signals.extend(reddit_signals)
            print(f"Reddit: {len(reddit_signals)} signals")

        gh_signals = collect_github()
        all_signals.extend(gh_signals)
        print(f"GitHub: {len(gh_signals)} signals")

        hn_signals = collect_hackernews()
        all_signals.extend(hn_signals)
        print(f"HN:     {len(hn_signals)} signals")

        # Store all signals
        insert_signals(all_signals)
        print(f"\nTotal collected: {len(all_signals)} signals")

        # Score all active topics
        topics = fetch_all_topics_with_signals(hours=48)
        print(f"Active topics to score: {len(topics)}")

        results = []
        breakouts = []

        for topic in topics:
            gs = compute_gradient_score(topic)
            if gs:
                result = self.process_score(gs, auto_publish=True)
                results.append(result)
                if result["action"] in ("BREAKOUT_CONFIRMED", "BREAKOUT_DETECTED"):
                    breakouts.append(result)

        print(f"\n{'=' * 60}")
        print(f"CYCLE COMPLETE")
        print(f"  Topics scored:  {len(results)}")
        print(f"  Breakouts:      {len(breakouts)}")
        if breakouts:
            print(f"\n  BREAKOUT SIGNALS:")
            for b in breakouts:
                print(f"    '{b['topic']}'")
                print(f"      Overall: {b['overall_score']:.1f} | "
                      f"Detection: {b['detection_score']:.1f} | "
                      f"Confidence: {b['confidence_score']:.1f}")
                c = b["components"]
                print(f"      G={c['G_gradient_strength']:.0f} "
                      f"I={c['I_inertia']:.0f} "
                      f"M={c['M_medium_sequence']:.0f} "
                      f"D={c['D_dark_matter']:.0f} "
                      f"C={c['C_confidence_decay']:.0f}")
        print("=" * 60)

        return {
            "collected":   len(all_signals),
            "scored":      len(results),
            "breakouts":   len(breakouts),
            "breakout_topics": [b["topic"] for b in breakouts],
        }


def _append_alert_log(alert: dict):
    """Append alert to the local log file for monitoring."""
    log_path = "alert_log.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(alert) + "\n")


# ==================================================================
# SECTION 3: THE UNIFIED API
# One server. All endpoints. Gradient + Pipeline + Institutional.
# ==================================================================

def create_unified_api() -> FastAPI:
    """
    One API to rule them all.

    Combines:
    - Gradient Score endpoints (from gradient_engine_backend.py)
    - Pipeline proof endpoints (from nowtrend_pipeline_architecture.py)
    - Institutional intelligence endpoints (new, in this file)
    - Heisenberg dual-score visualization endpoints

    Port 8000: This unified API
    """
    app = FastAPI(
        title="Now TrendIn — Unified Intelligence API",
        description=(
            "Gradient Score Engine + Cultural-to-Commercial Pipeline. "
            "The upstream intelligence layer for Palantir, Snowflake, and Bloomberg."
        ),
        version="2.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    bridge = GradientPipelineBridge()

    # ── Startup auto-collect ─────────────────────────────────────
    # If the DB is empty on boot (first deploy, ephemeral Heroku dyno reset)
    # kick off a background collection so real data appears without needing
    # a manual /collect-and-score POST.
    @app.on_event("startup")
    async def startup_collect():
        import threading
        try:
            topics = fetch_all_topics_with_signals(hours=24)
        except Exception:
            topics = []
        if not topics:
            print("[startup] DB empty — triggering background collection…")
            def _collect():
                try:
                    bridge.run_collection_cycle()
                    print("[startup] Background collection complete.")
                except Exception as e:
                    print(f"[startup] Collection error: {e}")
            threading.Thread(target=_collect, daemon=True).start()
        else:
            print(f"[startup] DB has {len(topics)} topic(s) — skipping auto-collect.")

    # ── Health ──────────────────────────────────────────────────
    @app.get("/health")
    def health():
        return {
            "status": "operational",
            "version": "2.0.0",
            "databases": {
                "gradient_scores": GRADIENT_DB,
                "pipeline_tracker": PIPELINE_DB,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ── Collection + Scoring ────────────────────────────────────
    @app.post("/collect-and-score")
    def collect_and_score(background_tasks: BackgroundTasks):
        """
        Runs the full collection cycle in the background.
        Returns immediately with a job ID.
        Collect → Score → Pipeline entry → Snowflake → Bloomberg queue
        """
        job_id = str(uuid.uuid4())[:12]
        background_tasks.add_task(bridge.run_collection_cycle)
        return {
            "job_id": job_id,
            "status": "started",
            "message": "Collection and scoring running in background. Check /scores in 2 min.",
        }

    @app.post("/score/{topic}")
    def score_single_topic(topic: str):
        """Score one specific topic and run it through the full pipeline."""
        topic_norm = normalize_topic(topic)
        gs = compute_gradient_score(topic_norm)
        if not gs:
            raise HTTPException(404, f"Insufficient signals for: {topic}")
        result = bridge.process_score(gs)
        return result

    # ── GRADIENT SCORE ENDPOINTS ────────────────────────────────
    @app.get("/scores")
    def get_top_scores(
        limit: int = Query(20, ge=1, le=100),
        min_score: float = Query(0.0),
    ):
        """Top Gradient Scores, all five components visible."""
        rows = fetch_top_scores(limit)
        result = []
        for r in rows:
            if isinstance(r, dict):
                row = r
            else:
                row = dict(r)
            if row.get("overall_score", 0) < min_score:
                continue
            for f in ["active_platforms", "platform_sequence", "top_signals"]:
                if isinstance(row.get(f), str):
                    try:
                        row[f] = json.loads(row[f])
                    except Exception:
                        row[f] = []
            # Add Heisenberg gap for every score
            row["heisenberg_gap"] = round(
                (row.get("detection_score", 0) or 0)
                - (row.get("confidence_score", 0) or 0),
                1
            )
            row["heisenberg_interpretation"] = _interpret_gap(
                row["heisenberg_gap"]
            )
            result.append(row)
        return {"count": len(result), "scores": result}

    @app.get("/scores/{topic}/components")
    def get_score_components(topic: str):
        """
        Returns all five Gradient Score components for one topic,
        with plain-English explanation of each.
        This is the explainability layer that makes the score trustworthy.
        """
        topic_norm = normalize_topic(topic)
        history = fetch_score_history(topic_norm, limit=1)
        if not history:
            raise HTTPException(404, f"No score found for: {topic}")

        s = dict(history[0])
        gap = (s.get("detection_score", 0) or 0) - (s.get("confidence_score", 0) or 0)

        return {
            "topic":         topic,
            "computed_at":   s.get("computed_at"),
            "overall_score": s.get("overall_score"),

            # THE FIVE COMPONENTS — fully explained
            "components": {
                "G_gradient_strength": {
                    "score":   s.get("gradient_strength"),
                    "weight":  "30%",
                    "meaning": "Concentration of signal in expert/niche vs mainstream",
                    "interpretation": _explain_gradient(s.get("gradient_strength", 0)),
                    "niche_signals":  s.get("niche_signal_count"),
                    "mainstream_signals": s.get("mainstream_signal_count"),
                },
                "I_inertia": {
                    "score":   s.get("inertia_score"),
                    "weight":  "25%",
                    "meaning": "Self-reinforcing momentum across consecutive time windows",
                    "interpretation": _explain_inertia(s.get("inertia_score", 0)),
                    "vocab_expansion": s.get("vocabulary_expansion_rate"),
                },
                "M_medium_sequence": {
                    "score":    s.get("medium_sequence_score"),
                    "weight":   "20%",
                    "meaning":  "Platform diffusion pattern match",
                    "pattern":  s.get("diffusion_pattern"),
                    "pattern_label": _pattern_label(s.get("diffusion_pattern", "")),
                    "platforms": json.loads(s.get("active_platforms", "[]"))
                                 if isinstance(s.get("active_platforms"), str)
                                 else s.get("active_platforms", []),
                },
                "D_dark_matter": {
                    "score":               s.get("dark_matter_score"),
                    "weight":              "15%",
                    "meaning":             "Inferred private conversation from public anomalies",
                    "first_timer_ratio":   s.get("first_timer_ratio"),
                    "asymmetry_detected":  bool(s.get("engagement_asymmetry_detected")),
                    "vocab_clustering":    s.get("vocabulary_expansion_rate"),
                    "interpretation":      _explain_dark_matter(
                                              s.get("dark_matter_score", 0),
                                              s.get("first_timer_ratio", 0),
                                              bool(s.get("engagement_asymmetry_detected"))
                                          ),
                },
                "C_confidence_decay": {
                    "score":   s.get("confidence_decay"),
                    "weight":  "10%",
                    "meaning": "Signal freshness and directional momentum",
                    "interpretation": _explain_decay(s.get("confidence_decay", 0)),
                },
            },

            # HEISENBERG DUAL SCORE
            "heisenberg": {
                "detection_score":  s.get("detection_score"),
                "confidence_score": s.get("confidence_score"),
                "gap":              round(gap, 1),
                "gap_interpretation": _interpret_gap(gap),
                "who_should_act": {
                    "detection_score": "Creators, marketers, trend-forward brands (act fast, accept some noise)",
                    "confidence_score": "Institutional analysts, investors, strategic planners (wait for proof)",
                },
            },

            # WHAT IT MEANS IN PLAIN ENGLISH
            "plain_english": {
                "why_this_matters": s.get("why_this_matters"),
                "what_to_watch":    s.get("what_to_watch"),
                "lead_time_est":    f"~{s.get('lead_time_estimate_days')} days before mainstream",
                "confidence_level": s.get("confidence_level"),
                "false_positive_risk": s.get("false_positive_risk"),
            },
        }

    # ── PIPELINE PROOF ENDPOINTS ────────────────────────────────
    @app.get("/pipeline/proof")
    def get_proof_document():
        """
        The institutional sales document.
        Shows every tracked signal, detection date, and outcome dates.
        This is what you show hedge funds in due diligence calls.
        """
        calc = AlphaCalculator(PIPELINE_DB)
        proof = calc.generate_proof_document()
        alpha = calc.compute_alpha_metrics(lookback_days=90)
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary":      alpha.get("headline", "Collecting data — check back in 30 days"),
            "alpha_metrics": alpha,
            "pipeline_events": proof,
        }

    @app.get("/pipeline/alpha")
    def get_alpha_metrics(lookback_days: int = Query(180)):
        """
        Returns the quantified lead time advantage with statistics.
        Average days ahead of Google Trends, media, and financial signals.
        """
        calc = AlphaCalculator(PIPELINE_DB)
        return calc.compute_alpha_metrics(lookback_days=lookback_days)

    @app.post("/pipeline/update-outcome")
    def update_outcome(
        topic: str,
        outcome_type: str,  # google_trends | media | financial | false_positive
        outcome_date: str,
        outlet_or_ticker: str = "",
        magnitude: float = 0.0,
    ):
        """
        Manually record when a tracked signal's outcome materialized.
        This builds the proof document over time.
        Called by you (or an automated script) when you see confirmation.
        """
        topic_norm = normalize_topic(topic)

        if outcome_type == "google_trends":
            days = bridge.tracker.update_google_trends_outcome(
                topic_norm, outcome_date, magnitude or 75.0
            )
        elif outcome_type == "media":
            days = bridge.tracker.update_media_outcome(
                topic_norm, outcome_date, outlet_or_ticker
            )
        elif outcome_type == "financial":
            days = bridge.tracker.update_financial_outcome(
                topic_norm, outcome_date, "stock_movement",
                outlet_or_ticker, magnitude
            )
        elif outcome_type == "false_positive":
            bridge.tracker.mark_false_positive(topic_norm, outlet_or_ticker)
            days = 0
        else:
            raise HTTPException(400, f"Unknown outcome_type: {outcome_type}")

        return {
            "topic":        topic,
            "outcome_type": outcome_type,
            "outcome_date": outcome_date,
            "lead_days":    days,
            "message":      f"Pipeline updated. Lead time: {days} days ahead."
        }

    # ── HEISENBERG VISUALIZATION ENDPOINT ──────────────────────
    @app.get("/heisenberg/{topic}")
    def get_heisenberg_view(topic: str):
        """
        Returns the dual-score view for one topic.
        Powers the Heisenberg split UI shown in the app prototype.
        """
        topic_norm = normalize_topic(topic)
        history = fetch_score_history(topic_norm, limit=10)
        if not history:
            raise HTTPException(404, f"No scores for: {topic}")

        current = dict(history[0])
        gap = (current.get("detection_score") or 0) - (current.get("confidence_score") or 0)

        # Time series for convergence chart
        time_series = []
        for h in reversed(history):
            h = dict(h)
            d = h.get("detection_score") or 0
            c = h.get("confidence_score") or 0
            time_series.append({
                "timestamp":       h.get("computed_at"),
                "detection_score": d,
                "confidence_score": c,
                "gap":             round(d - c, 1),
                "overall_score":   h.get("overall_score"),
            })

        return {
            "topic": topic,
            "current": {
                "detection_score":        current.get("detection_score"),
                "confidence_score":       current.get("confidence_score"),
                "gap":                    round(gap, 1),
                "gap_interpretation":     _interpret_gap(gap),
                # Board ruling 2026-07-08: former FP-rate fields were unmeasured
                # constants — removed (no fabricated accuracy claims).
                "lead_time_estimate_days": current.get("lead_time_estimate_days"),
            },
            "components": {
                # What DIFFERS between detect/confirm (threshold differences)
                "identical_in_both": ["G_gradient_strength", "C_confidence_decay"],
                "differs_by_threshold": {
                    "I_inertia": {
                        "detect_threshold":  "2 consecutive accelerating windows",
                        "confirm_threshold": "4 consecutive accelerating windows",
                        "detect_score":  _calc_component_detect("I", current),
                        "confirm_score": current.get("inertia_score"),
                    },
                    "M_medium_sequence": {
                        "detect_threshold":  "Partial pattern match accepted",
                        "confirm_threshold": "Full 3-platform match required",
                        "detect_score":  _calc_component_detect("M", current),
                        "confirm_score": current.get("medium_sequence_score"),
                    },
                    "D_dark_matter": {
                        "detect_threshold":  "First-timer ratio ≥ 25%",
                        "confirm_threshold": "First-timer ratio ≥ 40%",
                        "detect_score":  _calc_component_detect("D", current),
                        "confirm_score": current.get("dark_matter_score"),
                    },
                },
            },
            "convergence_forecast": _forecast_convergence(time_series),
            "time_series": time_series,
        }

    # ── DOWNSTREAM DISTRIBUTION ENDPOINTS ──────────────────────
    @app.post("/distribute/bloomberg-batch")
    def run_bloomberg_batch():
        """
        Generates a Bloomberg Data License submission file
        from today's high-scoring signals.
        """
        rows = fetch_top_scores(50)
        scores = []
        for r in rows:
            r = dict(r) if not isinstance(r, dict) else r
            if (r.get("overall_score") or 0) >= 70:
                scores.append(r)

        if not scores:
            return {"status": "no_signals", "message": "No signals above threshold today"}

        formatter = BloombergFormatter()
        filepath = formatter.save_bloomberg_file(scores)
        return {
            "status":    "file_generated",
            "filepath":  filepath,
            "records":   len(scores),
            "next_step": "Upload file to Bloomberg BEAP via SFTP",
            "sftp_host": "bbg-sftp-prod.bloomberg.com",
        }

    @app.post("/distribute/snowflake-push")
    def push_to_snowflake():
        """Push all high-scoring signals to Snowflake Marketplace."""
        if not bridge.snowflake.conn:
            return {
                "status": "not_configured",
                "message": "Set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD in .env",
            }
        rows = fetch_top_scores(100)
        published = 0
        for r in rows:
            r = dict(r) if not isinstance(r, dict) else r
            if bridge.snowflake.publish_score(r):
                published += 1
        return {"status": "published", "records": published}

    # ── ALERT LOG ───────────────────────────────────────────────
    @app.get("/alerts/recent")
    def get_recent_alerts(limit: int = Query(20)):
        """Returns recent breakout alerts from the log."""
        alerts = []
        if os.path.exists("alert_log.jsonl"):
            with open("alert_log.jsonl") as f:
                for line in f:
                    try:
                        alerts.append(json.loads(line.strip()))
                    except Exception:
                        pass
        return {
            "count":  len(alerts[-limit:]),
            "alerts": list(reversed(alerts))[:limit],
        }

    # ── SCORE HISTORY ────────────────────────────────────────────
    @app.get("/scores/{topic}/history")
    def get_score_history(
        topic: str,
        hours: int = Query(168, ge=1, le=720),
    ):
        """Score history for a topic — powers the Heisenberg sparkline."""
        topic_norm = normalize_topic(topic)
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        conn = get_gradient_db(GRADIENT_DB)
        rows = conn.execute(
            """
            SELECT computed_at, overall_score, detection_score, confidence_score,
                   gradient_strength, inertia_score, medium_sequence_score,
                   dark_matter_score, confidence_decay, lead_time_estimate_days
            FROM gradient_scores
            WHERE topic = ? AND computed_at >= ?
            ORDER BY computed_at ASC
            """,
            (topic_norm, cutoff),
        ).fetchall()
        conn.close()
        return {
            "topic":   topic,
            "hours":   hours,
            "count":   len(rows),
            "history": [dict(r) for r in rows],
        }

    # ── EXTENSIONS (audit / calibration / scenarios) ─────────────
    if _EXTENSIONS_AVAILABLE:
        init_extensions(GRADIENT_DB)
        app.include_router(_ext_router)

    # ── STATIC FRONTEND (production build) ───────────────────────
    # Served last so API routes always take priority.
    _static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(_static_dir):
        app.mount("/", StaticFiles(directory=_static_dir, html=True), name="frontend")

    return app


# ==================================================================
# SECTION 4: PLAIN-ENGLISH EXPLAINERS
# Used by the API to explain scores without jargon
# ==================================================================

def _explain_gradient(score: float) -> str:
    if score >= 80:
        return ("Almost entirely in expert and niche communities. "
                "The signal has maximum runway — mainstream has not discovered it yet.")
    elif score >= 60:
        return ("Primarily in specialist communities with early mainstream awareness building. "
                "The window is open and significant.")
    elif score >= 40:
        return ("Spreading from specialist communities into broader awareness. "
                "The opportunity window is narrowing.")
    else:
        return ("Widely distributed across mainstream platforms. "
                "The gradient has flattened — early positioning window has passed.")


def _explain_inertia(score: float) -> str:
    if score >= 70:
        return ("Strong self-reinforcing momentum confirmed across multiple time windows. "
                "New vocabulary is emerging around the topic. This is a real trend, not a spike.")
    elif score >= 45:
        return ("Moderate momentum building. Showing acceleration but not yet "
                "confirmed across 4+ consecutive windows. Monitor closely.")
    elif score >= 20:
        return ("Early movement detected. Fewer than 2 consecutive accelerating "
                "windows — could be a spike. Watch for sustained acceleration.")
    else:
        return ("No sustained momentum detected. Signal may be a one-day event. "
                "High false-positive risk at this inertia level.")


def _explain_dark_matter(score: float, ft_ratio: float, asymmetry: bool) -> str:
    indicators = []
    if ft_ratio and ft_ratio >= 0.35:
        indicators.append(
            f"{round(ft_ratio * 100)}% of commenters are new to this community "
            f"(suggests external traffic from private source)"
        )
    if asymmetry:
        indicators.append(
            "Comments exceed normal upvote ratios (community already engaged privately)"
        )
    if score >= 60 and not indicators:
        indicators.append("Vocabulary clustering detected across unrelated accounts")

    if not indicators:
        return "No dark matter signatures detected. Signal appears to originate in public spaces."
    return ("Private conversation inferred from: " + " · ".join(indicators) + ". "
            "High dark matter score suggests the visible signal is the tip of a larger "
            "private conversation that has not yet crossed to public platforms.")


def _explain_decay(score: float) -> str:
    if score >= 75:
        return "Signal is fresh and trending upward. Full confidence in recency."
    elif score >= 50:
        return "Signal is moderately fresh. Score is stable or slightly declining."
    elif score >= 25:
        return ("Signal is aging. If not confirmed by other components, "
                "consider this a declining opportunity.")
    else:
        return ("Signal has aged significantly or has crossed into mainstream. "
                "Mainstream penalty applied. Early positioning window has closed.")


def _pattern_label(pattern: str) -> str:
    labels = {
        "A_builder_to_buyer":        "Pattern A — Builder to Buyer (Technology commercialization)",
        "B_enthusiast_to_mainstream": "Pattern B — Enthusiast to Mainstream (Cultural spread)",
        "C_research_to_commerce":    "Pattern C — Research to Commerce (Science → market)",
        "multi_platform":            "Multi-Platform — Active but pattern unclear",
        "single_platform":           "Single Platform — Early or isolated signal",
        "unknown":                   "Emerging — Insufficient platform data",
    }
    return labels.get(pattern, pattern)


def _interpret_gap(gap: float) -> str:
    if gap <= 15:
        return ("Both scores agree. High conviction — this signal is either "
                "clearly real (both high) or clearly weak (both low).")
    elif gap <= 35:
        return ("Confirmation is building. Detection sees it; confidence is "
                "accumulating evidence. Signal is 1-3 days from full confirmation.")
    elif gap <= 60:
        return ("Very early stage. The engine detected something before the "
                "confirmation data has arrived. High potential, not yet proven. "
                "This is the ideal Heisenberg window for early actors.")
    else:
        return ("Speculative. Primarily dark matter signal. The detection fires "
                "but insufficient public confirmation exists. Highest risk, "
                "highest potential lead time if correct.")


def _calc_component_detect(component: str, score_dict: dict) -> float:
    """
    Approximate Detection Score version of each component.
    In Detection mode, thresholds are lower — scores are generally higher.
    This approximates the difference for the API response.
    """
    base = {
        "I": score_dict.get("inertia_score", 0),
        "M": score_dict.get("medium_sequence_score", 0),
        "D": score_dict.get("dark_matter_score", 0),
    }.get(component, 0)

    # Detection mode boosts: lower threshold → higher component score
    detection_boost = {"I": 1.35, "M": 1.30, "D": 1.25}.get(component, 1.0)
    return round(min(100, (base or 0) * detection_boost), 1)


def _forecast_convergence(time_series: list) -> dict:
    """
    Forecasts when Detection and Confidence scores will converge.
    If the gap is closing consistently, estimate when both scores agree.
    """
    if len(time_series) < 2:
        return {"status": "insufficient_data"}

    gaps = [t["gap"] for t in time_series]
    if len(gaps) >= 3:
        # Simple linear trend on the gap
        recent_change = gaps[-1] - gaps[-2]
        if recent_change < -3:
            hours_to_converge = max(0, gaps[-1] / abs(recent_change)) * 6
            return {
                "status":              "converging",
                "current_gap":         gaps[-1],
                "gap_change_per_window": round(recent_change, 1),
                "est_hours_to_converge": round(hours_to_converge, 0),
                "interpretation": (
                    f"Gap closing at {abs(recent_change):.1f} points per 6-hour window. "
                    f"Both scores expected to align in ~{round(hours_to_converge, 0):.0f} hours."
                ),
            }
        elif recent_change > 3:
            return {
                "status":        "diverging",
                "current_gap":   gaps[-1],
                "interpretation": "Gap is widening — signal may be strengthening in detection "
                                  "while confidence layer awaits more windows.",
            }

    return {
        "status":        "stable",
        "current_gap":   gaps[-1] if gaps else 0,
        "interpretation": "Gap is stable. Monitor over next 24-48 hours.",
    }


# ==================================================================
# SECTION 5: ENTRY POINT
# ==================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Now TrendIn — Integrated Gradient Score + Pipeline System"
    )
    parser.add_argument(
        "--mode",
        choices=["collect", "score", "validate", "alpha", "api", "bloomberg"],
        default="api",
        help=(
            "collect  = run one collection + scoring cycle\n"
            "score    = score all active topics\n"
            "validate = seed pipeline with historical cases\n"
            "alpha    = print current alpha metrics\n"
            "api      = start unified API server\n"
            "bloomberg= generate Bloomberg submission file"
        ),
    )
    args = parser.parse_args()

    if args.mode == "collect":
        bridge = GradientPipelineBridge()
        result = bridge.run_collection_cycle()
        print(json.dumps(result, indent=2))

    elif args.mode == "score":
        bridge = GradientPipelineBridge()
        topics = fetch_all_topics_with_signals(hours=48)
        print(f"Scoring {len(topics)} active topics...")
        for topic in topics:
            gs = compute_gradient_score(topic)
            if gs:
                bridge.process_score(gs)

    elif args.mode == "validate":
        run_historical_validation(PIPELINE_DB, HISTORICAL_VALIDATION_CASES)

    elif args.mode == "alpha":
        calc = AlphaCalculator(PIPELINE_DB)
        alpha = calc.compute_alpha_metrics()
        print(json.dumps(alpha, indent=2, default=str))

    elif args.mode == "bloomberg":
        bridge = GradientPipelineBridge()
        rows = fetch_top_scores(50)
        scores = [dict(r) if not isinstance(r, dict) else r
                  for r in rows
                  if (r.get("overall_score") or 0) >= 70]
        formatter = BloombergFormatter()
        path = formatter.save_bloomberg_file(scores)
        print(f"\nBloomberg file ready: {path}")
        print(f"Records: {len(scores)}")
        print("Next: SFTP to bbg-sftp-prod.bloomberg.com")

    elif args.mode == "api":
        print("\n" + "=" * 60)
        print("NOW TRENDIN UNIFIED API")
        print("=" * 60)
        print(f"Gradient + Pipeline + Institutional endpoints")
        print(f"URL:  http://localhost:{API_PORT}")
        print(f"Docs: http://localhost:{API_PORT}/docs")
        print("=" * 60)
        # Heroku's Python buildpack sets WEB_CONCURRENCY which causes newer
        # uvicorn to require an import string instead of an app instance.
        # Pop it so uvicorn runs single-process with our in-process app object.
        os.environ.pop("WEB_CONCURRENCY", None)
        app = create_unified_api()
        uvicorn.run(app, host="0.0.0.0", port=API_PORT, log_level="info")


if __name__ == "__main__":
    main()
