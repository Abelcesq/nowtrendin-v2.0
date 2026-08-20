# -*- coding: utf-8 -*-
"""
DARK MATTER LEADING-INDICATOR RESEARCH MODULE — HELD OUT. NEVER FEEDS A SCORE.

Nine-seat board 2026-08-20 (decision item 9), Chairman-ordered build. Four independent
seats converged, without cross-visibility, on the same family of indicators for the 92%
of collection that carries no author identity — the population D's first-timer mechanism
can never read (and, with Reddit formally retired 2026-08-20, the population that now
dominates every non-tech domain):

  1. VENUE FIRST-COVERAGE  (Operator; Statistician's "first-coverage semantics"):
     an OUTLET covering an entity for the first time in its own history is the
     authorless analog of a first-timer — migration measured at venue granularity.
  2. INCUMBENT DISPLACEMENT (Economist, Kindleberger): first-timer influx is a
     euphoria-stage signal — the crowd cannot lead the crowd. The displacement-stage
     signal is ESTABLISHED authors REALLOCATING attention share to a topic they did
     not previously cover (the trend-side analog of insider buying).
  3. EXPERT-BREADTH VELOCITY (Economist; Buyer's "cross-expert-community propagation";
     Expansionist's "first-timer velocity"): the FIRST DERIVATIVE of distinct
     expert/niche communities carrying a topic — converts the LED mining's one robust
     lagging finding (breadth separates winners) into a leading instrument.
  4. ENGAGEMENT-PER-MENTION DIVERGENCE (Economist, Smith): engagement is the price of
     attention, mentions its quantity; price outrunning quantity in a thin market is
     the early demand signal. Baselined per community so it works without upvote fields.

INTEGRITY CONTRACT (the same wall the ledger lives behind):
  - READ-ONLY over topic_signals/raw_signals/author_history. Writes ONLY to its own
    research table (`d_indicator_snapshots`) so shadow-trial analysis has PIT rows that
    survive the 7-day operational retention (the GHOST close-out lesson: never let a
    trial's evidence live in prunable tables).
  - NOTHING here is imported by any scoring path. The heldout registry should list this
    module beside referee_wikipedia. Wiring any of these into detection/score/weight is
    SCORE-AFFECTING and requires: sealed backtest + board note + founder flip. They are
    CANDIDATES to be measured by the A4 shadow trial, not components.
  - No fabrication: every indicator returns None (not 0) when its inputs are absent —
    the d_measured discipline applied from birth.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import db_compat

DB_PATH = os.getenv("DB_PATH", "anomaly_detector.db")

# Expert/niche = the Dark-Matter router's own definition (platform_tier).
_D_TIERS = ("expert", "niche")
# Incumbent = an author with at least this many prior posts in the community.
INCUMBENT_MIN_POSTS = int(os.getenv("DIND_INCUMBENT_MIN_POSTS", "5"))
# Venue first-coverage lookback: an entity is "new to the venue" if the venue never
# carried it before this window's start (bounded by the venue's own observed history).
SNAPSHOT_KIND = "d_indicators_v1"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _cut(hours: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime(
        "%Y-%m-%dT%H:%M:%S")


def _ph() -> str:
    return "%s" if db_compat.USE_PG else "?"


def init_db(db_path: str = DB_PATH) -> None:
    """Research snapshot table — append-only by convention; never read by scoring."""
    conn = db_compat.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS d_indicator_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapped_at TEXT, topic_key TEXT, kind TEXT,
                venue_first_coverage INTEGER, venue_total INTEGER,
                incumbent_displacement REAL, incumbents_seen INTEGER,
                expert_breadth_now INTEGER, expert_breadth_prev INTEGER,
                breadth_velocity REAL,
                engagement_divergence REAL,
                payload TEXT)
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_dind_topic "
                     "ON d_indicator_snapshots(topic_key, snapped_at)")
        conn.commit()
    finally:
        conn.close()


# ── Indicator 1: venue first-coverage ────────────────────────────────────────────

def venue_first_coverage(conn, topic_key: str, window_h: int = 24) -> Optional[dict]:
    """Of the expert/niche VENUES (source_name) carrying this topic in the window, how
    many are carrying it for the FIRST time in their own observed history? Returns None
    when the topic has no expert/niche venues in the window (absence, not zero).

    Honest limit, stated: "observed history" is bounded by the operational tables'
    retention — a venue's first observed coverage may not be its true first. The
    snapshot table exists precisely so that, going forward, this history accrues in a
    non-pruned store and the bound tightens with age. Interpret early reads under
    §16a CALIBRATING semantics."""
    ph = _ph()
    tiers = ",".join([ph] * len(_D_TIERS))
    rows = conn.execute(
        f"SELECT source_name, MIN(extracted_at) AS first_seen FROM topic_signals "
        f"WHERE topic_key = {ph} AND platform_tier IN ({tiers}) "
        f"GROUP BY source_name", (topic_key, *_D_TIERS)).fetchall()
    if not rows:
        return None
    w0 = _cut(window_h)
    in_window = [r for r in rows if str(r["first_seen"]) >= w0]
    # venue is FIRST-TIME iff its first-ever sighting of the topic is inside the window
    # AND the venue itself has older history on other topics (else the venue is new to
    # US, which is the cold-start fabrication class — excluded, Guardian F2).
    firsts = 0
    for r in in_window:
        older = conn.execute(
            f"SELECT 1 FROM topic_signals WHERE source_name = {ph} "
            f"AND extracted_at < {ph} LIMIT 1",
            (r["source_name"], w0)).fetchone()
        if older:
            firsts += 1
    return {"venue_first_coverage": firsts, "venue_total": len(rows),
            "venues_in_window": len(in_window)}


# ── Indicator 2: incumbent displacement ──────────────────────────────────────────

def incumbent_displacement(conn, topic_key: str, window_h: int = 48) -> Optional[dict]:
    """Fraction of the topic's window authors who are INCUMBENTS of their community
    (≥INCUMBENT_MIN_POSTS prior posts) — established members reallocating attention,
    the displacement-stage signal. Requires author-bearing signals; None otherwise.

    Reads author names from raw_signals joined via signal_id (topic_signals carries no
    author); post counts from author_history."""
    ph = _ph()
    w0 = _cut(window_h)
    rows = conn.execute(
        f"SELECT rs.author, rs.platform, rs.source_name FROM topic_signals ts "
        f"JOIN raw_signals rs ON rs.id = ts.signal_id "
        f"WHERE ts.topic_key = {ph} AND ts.extracted_at >= {ph} "
        f"AND rs.author IS NOT NULL AND rs.author != ''",
        (topic_key, w0)).fetchall()
    authors = {(r["author"], r["platform"], r["source_name"]) for r in rows}
    if not authors:
        return None
    incumbents = 0
    for author, platform, community in authors:
        h = conn.execute(
            f"SELECT post_count FROM author_history WHERE author = {ph} "
            f"AND platform = {ph} AND community = {ph}",
            (author, platform, community)).fetchone()
        pc = (h["post_count"] if h and hasattr(h, "keys") else (h[0] if h else 0)) or 0
        if pc >= INCUMBENT_MIN_POSTS:
            incumbents += 1
    return {"incumbent_displacement": round(incumbents / len(authors), 4),
            "incumbents_seen": incumbents, "authors_seen": len(authors)}


# ── Indicator 3: expert-breadth velocity ─────────────────────────────────────────

def expert_breadth_velocity(conn, topic_key: str, window_h: int = 24) -> Optional[dict]:
    """d/dt of distinct expert/niche communities carrying the topic: breadth in the
    current window minus breadth in the immediately preceding window of equal length.
    None when the topic has never appeared at expert/niche tier at all."""
    ph = _ph()
    tiers = ",".join([ph] * len(_D_TIERS))
    w1, w0 = _cut(window_h), _cut(2 * window_h)

    def _breadth(lo, hi):
        r = conn.execute(
            f"SELECT COUNT(DISTINCT source_name) AS b FROM topic_signals "
            f"WHERE topic_key = {ph} AND platform_tier IN ({tiers}) "
            f"AND extracted_at >= {ph} AND extracted_at < {ph}",
            (topic_key, *_D_TIERS, lo, hi)).fetchone()
        return (r["b"] if hasattr(r, "keys") else r[0]) or 0

    now_b = _breadth(w1, "9999")
    prev_b = _breadth(w0, w1)
    if now_b == 0 and prev_b == 0:
        ever = conn.execute(
            f"SELECT 1 FROM topic_signals WHERE topic_key = {ph} "
            f"AND platform_tier IN ({tiers}) LIMIT 1",
            (topic_key, *_D_TIERS)).fetchone()
        if not ever:
            return None
    return {"expert_breadth_now": now_b, "expert_breadth_prev": prev_b,
            "breadth_velocity": float(now_b - prev_b)}


# ── Indicator 4: engagement-per-mention divergence ───────────────────────────────

def engagement_divergence(conn, topic_key: str, window_h: int = 48) -> Optional[dict]:
    """Topic's engagement-per-mention at expert/niche tier vs each carrying community's
    own norm — the topic's PREMIUM over its venues, averaged. >1 means attention demand
    is outrunning mention supply in the communities carrying it. None when the topic has
    no engagement-bearing expert/niche signals."""
    ph = _ph()
    tiers = ",".join([ph] * len(_D_TIERS))
    w0 = _cut(window_h)
    rows = conn.execute(
        f"SELECT source_name, AVG(engagement_raw) AS e FROM topic_signals "
        f"WHERE topic_key = {ph} AND platform_tier IN ({tiers}) "
        f"AND extracted_at >= {ph} AND engagement_raw > 0 "
        f"GROUP BY source_name", (topic_key, *_D_TIERS, w0)).fetchall()
    if not rows:
        return None
    premiums = []
    for r in rows:
        norm = conn.execute(
            f"SELECT AVG(engagement_raw) AS e FROM topic_signals "
            f"WHERE source_name = {ph} AND extracted_at >= {ph} "
            f"AND engagement_raw > 0", (r["source_name"], w0)).fetchone()
        base = (norm["e"] if hasattr(norm, "keys") else norm[0]) or 0
        if base > 0:
            premiums.append(float(r["e"]) / float(base))
    if not premiums:
        return None
    return {"engagement_divergence": round(sum(premiums) / len(premiums), 4),
            "venues_with_norms": len(premiums)}


# ── Snapshot + serve ─────────────────────────────────────────────────────────────

def compute_all(topic_key: str, db_path: str = DB_PATH) -> dict:
    """All four indicators for one topic. Absent inputs → None per indicator, never 0."""
    conn = db_compat.connect(db_path)
    try:
        return {
            "topic_key": topic_key,
            "computed_at": _now_iso(),
            "kind": SNAPSHOT_KIND,
            "venue_first_coverage": venue_first_coverage(conn, topic_key),
            "incumbent_displacement": incumbent_displacement(conn, topic_key),
            "expert_breadth_velocity": expert_breadth_velocity(conn, topic_key),
            "engagement_divergence": engagement_divergence(conn, topic_key),
            "note": ("held-out research indicators; never a score input; shadow-trial "
                     "candidates (board 2026-08-20 item 9)"),
        }
    finally:
        conn.close()


def snapshot(topic_keys: list, db_path: str = DB_PATH) -> int:
    """Persist one research snapshot per topic to the non-pruned research table (so
    shadow-trial evidence outlives the 7-day operational retention)."""
    init_db(db_path)
    conn = db_compat.connect(db_path)
    ph = _ph()
    n = 0
    try:
        for tk in topic_keys:
            r = compute_all(tk, db_path)
            v = r.get("venue_first_coverage") or {}
            i = r.get("incumbent_displacement") or {}
            b = r.get("expert_breadth_velocity") or {}
            e = r.get("engagement_divergence") or {}
            conn.execute(
                f"INSERT INTO d_indicator_snapshots (snapped_at, topic_key, kind, "
                f"venue_first_coverage, venue_total, incumbent_displacement, "
                f"incumbents_seen, expert_breadth_now, expert_breadth_prev, "
                f"breadth_velocity, engagement_divergence, payload) "
                f"VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})",
                (r["computed_at"], tk, SNAPSHOT_KIND,
                 v.get("venue_first_coverage"), v.get("venue_total"),
                 i.get("incumbent_displacement"), i.get("incumbents_seen"),
                 b.get("expert_breadth_now"), b.get("expert_breadth_prev"),
                 b.get("breadth_velocity"), e.get("engagement_divergence"),
                 json.dumps(r, default=str)))
            n += 1
        conn.commit()
    finally:
        conn.close()
    return n
