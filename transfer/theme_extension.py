"""
NOW TRENDIN — AUTO-THEME EXTENSION

Automatically promotes BREAKOUT/STRONG topics from the attention engine into
THEMES so the Trend Beneficiary engine grows with trend discovery — no manual
THEMES dict edits needed.

DESIGN

The trend_beneficiary engine matches companies to themes. THEMES is the leverage
point — if it only contains AI Infrastructure + Energy Transition, then a real
trend in cybersecurity won't surface any beneficiaries no matter how strong its
Gradient Score. This module solves that by:

  1) Scanning velocity_scores for topics at BREAKOUT or STRONG stages.
  2) For each promoted topic, building a theme fingerprint from co-occurring
     keywords (most frequent terms in raw_signals for that topic) AND from
     dominant Finnhub industry sectors of any companies mentioned.
  3) Writing the promoted theme into a persistent themes_extension table so
     it survives engine restarts and shows up in trend_beneficiary.THEMES.

GUARDRAILS

- ALWAYS keep the hand-curated THEMES from trend_beneficiary.py (don't overwrite).
- Require a topic to be BREAKOUT or STRONG for at least N hours (default 12)
  before promotion — prevents noise spikes from polluting the theme space.
- Cap auto-themes at MAX_AUTO_THEMES (default 25) — oldest, lowest-conviction
  evicted first.
- Every auto-theme stores its promotion timestamp + the evidence (score, source
  counts) so a human can audit later.

NOT A REPLACEMENT FOR HUMAN CURATION — this is a DISCOVERY layer. The trend
intelligence team can review extracted themes weekly and either confirm
(promote to hand-curated) or reject (blocklist).
"""
import os
import re
from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import Optional

try:
    import db_compat
except Exception:
    db_compat = None

try:
    import trend_beneficiary as tb
except Exception:
    tb = None

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
MIN_PROMOTION_HOURS = int(os.getenv("THEME_MIN_HOURS", "12"))
MAX_AUTO_THEMES = int(os.getenv("THEME_MAX_AUTO", "25"))
PROMOTION_STAGES = {"BREAKOUT", "STRONG"}

# Stopwords to strip from co-occurring-keyword extraction.
_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "must", "shall", "can", "to", "of",
    "in", "for", "on", "with", "as", "by", "at", "from", "this", "that",
    "these", "those", "it", "its", "they", "them", "their", "you", "your",
    "we", "our", "us", "i", "me", "my", "new", "now", "said", "says",
    "year", "years", "week", "today", "via", "amid", "after", "before",
    "first", "last", "next", "more", "most", "less", "least", "than", "then",
    "also", "just", "even", "much", "many", "some", "any", "all", "no", "not",
    "what", "when", "where", "who", "why", "how", "which",
}


def init_theme_db(db_path: str = DB_PATH, conn=None):
    own = False
    if conn is None:
        conn = db_compat.connect(db_path)
        own = True
    conn.execute("""
        CREATE TABLE IF NOT EXISTS themes_extension (
            theme_key TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            keywords TEXT NOT NULL,
            sectors TEXT NOT NULL,
            detection_score REAL,
            source_signals INTEGER,
            stage TEXT,
            promoted_at TEXT NOT NULL,
            last_seen_at TEXT,
            confirmed_by_human INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS themes_blocklist (
            theme_key TEXT PRIMARY KEY,
            reason TEXT,
            blocked_at TEXT NOT NULL
        )
    """)
    conn.commit()
    if own:
        conn.close()


def _extract_cooccurring_keywords(conn, topic_key: str, hours: int = 24,
                                   top_n: int = 12) -> list:
    """Top co-occurring keywords from raw_signals tied to this topic."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    try:
        rows = conn.execute(
            "SELECT title FROM raw_signals r "
            "JOIN topic_signals t ON r.id = t.signal_id "
            "WHERE t.topic_key = ? AND r.collected_at > ?",
            (topic_key, cutoff)
        ).fetchall()
    except Exception:
        rows = []
    counter: Counter = Counter()
    for r in rows:
        title = (r["title"] if hasattr(r, "keys") else r[0]) or ""
        for w in re.findall(r"[a-z][a-z\-]{2,}", title.lower()):
            if w in _STOPWORDS or len(w) < 3:
                continue
            counter[w] += 1
    # Drop the topic_key itself from co-occurring set
    counter.pop(topic_key.replace("_", " ").lower(), None)
    return [w for w, _ in counter.most_common(top_n)]


def _looks_like_company_topic(topic_key: str, keywords: list) -> bool:
    """A theme should NOT be a single company name — it should be a SECTOR /
    TECHNOLOGY / TREND. Heuristic reject if topic looks like a brand."""
    # If topic_key is short single word + capitalized ticker-like, skip
    if len(topic_key) <= 5 and topic_key.isupper():
        return True
    return False


def discover_candidate_themes(db_path: str = DB_PATH, hours: int = 24,
                              min_stage: str = "STRONG") -> list:
    """Find topics that should be considered for promotion to themes.
    Returns list of {topic_key, label, detection_score, stage, signal_count}."""
    if db_compat is None:
        return []
    conn = None
    candidates = []
    try:
        conn = db_compat.connect(db_path)
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        try:
            rows = conn.execute(
                "SELECT topic_key, topic_display, detection_score, stage, "
                "scored_at, signal_count "
                "FROM velocity_scores "
                "WHERE stage IN ('BREAKOUT','STRONG') AND scored_at > ? "
                "ORDER BY detection_score DESC LIMIT 100",
                (cutoff,)
            ).fetchall()
        except Exception as e:
            print(f"[theme_extension] discover error: {e}")
            rows = []

        promotion_cutoff = (datetime.now(timezone.utc) -
                            timedelta(hours=MIN_PROMOTION_HOURS)).isoformat()
        for r in rows:
            d = dict(r) if hasattr(r, "keys") else {
                "topic_key": r[0], "topic_display": r[1], "detection_score": r[2],
                "stage": r[3], "scored_at": r[4], "signal_count": r[5],
            }
            try:
                prior = conn.execute(
                    "SELECT 1 FROM velocity_scores WHERE topic_key = ? "
                    "AND stage IN ('BREAKOUT','STRONG') AND scored_at < ? LIMIT 1",
                    (d["topic_key"], promotion_cutoff)
                ).fetchone()
            except Exception:
                prior = None
            if prior:
                d["sustained"] = True
                candidates.append(d)
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass
    return candidates


def promote_theme(topic_key: str, topic_display: str,
                  detection_score: float, stage: str, signal_count: int,
                  db_path: str = DB_PATH, conn=None) -> Optional[dict]:
    """Promote a topic to an auto-theme. Returns the theme dict or None."""
    own = False
    if conn is None:
        conn = db_compat.connect(db_path)
        own = True

    # Skip if already promoted, blocklisted, or in hand-curated THEMES
    try:
        if conn.execute("SELECT 1 FROM themes_blocklist WHERE theme_key = ?",
                        (topic_key,)).fetchone():
            return None
        existing = conn.execute(
            "SELECT theme_key FROM themes_extension WHERE theme_key = ?",
            (topic_key,)).fetchone()
    except Exception:
        existing = None
    if tb and topic_key in tb.THEMES:
        return None

    keywords = _extract_cooccurring_keywords(conn, topic_key)
    # Always include the topic itself + display words as anchor keywords
    keywords = [topic_key.replace("_", " ")] + [
        w for w in (topic_display or "").lower().split() if len(w) > 2
    ] + keywords
    # Dedup preserving order
    seen, kws = set(), []
    for k in keywords:
        if k not in seen:
            seen.add(k); kws.append(k)
    kws = kws[:15]

    if _looks_like_company_topic(topic_key, kws):
        return None

    # Sectors: best-effort — pull from co-occurring news source domains, fallback to []
    sectors: list = []  # TODO: enhance with Finnhub industry mapping later

    now_iso = datetime.now(timezone.utc).isoformat()
    label = topic_display or topic_key.replace("_", " ").title()

    if existing:
        conn.execute(
            "UPDATE themes_extension SET label = ?, keywords = ?, sectors = ?, "
            "detection_score = ?, stage = ?, source_signals = ?, last_seen_at = ? "
            "WHERE theme_key = ?",
            (label, ",".join(kws), ",".join(sectors), detection_score,
             stage, signal_count, now_iso, topic_key)
        )
    else:
        conn.execute(
            "INSERT INTO themes_extension (theme_key, label, keywords, sectors, "
            "detection_score, source_signals, stage, promoted_at, last_seen_at, "
            "confirmed_by_human) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (topic_key, label, ",".join(kws), ",".join(sectors),
             detection_score, signal_count, stage, now_iso, now_iso, 0)
        )
    conn.commit()

    if own:
        conn.close()

    return {"theme_key": topic_key, "label": label, "keywords": kws,
            "sectors": sectors, "detection_score": detection_score,
            "stage": stage}


def evict_oldest_if_full(db_path: str = DB_PATH, conn=None):
    """Cap auto-themes to MAX_AUTO_THEMES — oldest, unconfirmed first."""
    own = False
    if conn is None:
        conn = db_compat.connect(db_path)
        own = True
    try:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM themes_extension "
            "WHERE confirmed_by_human = 0"
        ).fetchone()
        n = (count["n"] if hasattr(count, "keys") else count[0]) if count else 0
        if n > MAX_AUTO_THEMES:
            to_evict = n - MAX_AUTO_THEMES
            conn.execute(
                "DELETE FROM themes_extension WHERE theme_key IN ("
                "SELECT theme_key FROM themes_extension "
                "WHERE confirmed_by_human = 0 "
                "ORDER BY last_seen_at ASC LIMIT ?)",
                (to_evict,)
            )
            conn.commit()
    except Exception as e:
        print(f"[theme_extension] evict error: {e}")
    if own:
        conn.close()


def load_all_themes(db_path: str = DB_PATH) -> dict:
    """Return the merged THEMES dict: hand-curated + auto-promoted.
    Hand-curated wins on key conflict."""
    out = dict(tb.THEMES) if tb else {}
    if db_compat is None:
        return out
    conn = None
    try:
        conn = db_compat.connect(db_path)
        rows = conn.execute(
            "SELECT theme_key, label, keywords, sectors "
            "FROM themes_extension"
        ).fetchall()
        for r in rows:
            d = dict(r) if hasattr(r, "keys") else {
                "theme_key": r[0], "label": r[1],
                "keywords": r[2], "sectors": r[3]
            }
            if d["theme_key"] in out:
                continue  # hand-curated wins
            out[d["theme_key"]] = {
                "label": d["label"],
                "keywords": [k for k in (d["keywords"] or "").split(",") if k],
                "sectors": [s for s in (d["sectors"] or "").split(",") if s],
                "auto_promoted": True,
            }
    except Exception as e:
        print(f"[theme_extension] load error: {e}")
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass
    return out


def run_extension_cycle(db_path: str = DB_PATH) -> dict:
    """One full extension pass — discover candidates, promote them, evict if
    over the cap. Safe to call on a schedule (e.g., daily)."""
    init_theme_db(db_path)
    candidates = discover_candidate_themes(db_path)
    promoted = []
    for c in candidates:
        result = promote_theme(
            c["topic_key"], c["topic_display"],
            c["detection_score"], c["stage"], c.get("signal_count") or 0,
            db_path=db_path
        )
        if result:
            promoted.append(result["theme_key"])
    evict_oldest_if_full(db_path)
    # Hot-patch the trend_beneficiary THEMES dict so the running engine picks
    # up the auto-promoted themes without a restart.
    if tb is not None:
        try:
            merged = load_all_themes(db_path)
            tb.THEMES.update({k: v for k, v in merged.items()
                              if k not in tb.THEMES})
        except Exception as e:
            print(f"[theme_extension] hot-patch error: {e}")
    return {"candidates_considered": len(candidates),
            "promoted": promoted,
            "total_auto_themes": len(promoted),
            "ran_at": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    print(run_extension_cycle())
