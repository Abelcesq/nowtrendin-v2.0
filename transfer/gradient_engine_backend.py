"""
gradient_engine_backend.py
==========================
Now TrendIn — Gradient Score Engine
Full backend: data collection, scoring, FastAPI server

Run:
  pip install praw requests fastapi uvicorn vaderSentiment python-dotenv
  python gradient_engine_backend.py

API available at: http://localhost:8000/docs
"""

import os
import re
import math
import time
import json
import sqlite3
import hashlib
import statistics
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
from typing import Optional
from dataclasses import dataclass, field, asdict

import praw
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────

DB_PATH = os.getenv("DB_PATH", "gradient_scores.db")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "NowTrendIn/1.0 Gradient Engine")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

NICHE_SUBREDDITS = [
    "LocalLLaMA", "MachineLearning", "artificial", "singularity",
    "ChatGPT", "ClaudeAI", "OpenAI", "StableDiffusion",
    "SideProject", "startups", "Entrepreneur",
    "bioinformatics", "neuralnetworks", "reinforcementlearning",
    "programming", "learnprogramming",
]

MAINSTREAM_SUBREDDITS = [
    "technology", "Futurology", "worldnews", "science",
    "todayilearned", "explainlikeimfive", "news",
]

ALL_SUBREDDITS = NICHE_SUBREDDITS + MAINSTREAM_SUBREDDITS

GITHUB_TOPICS = [
    "llm", "large-language-model", "ai-agent", "rag",
    "generative-ai", "diffusion-model", "fine-tuning",
    "multimodal", "vector-database", "embeddings",
    "autonomous-agent", "ai-safety", "open-source-llm",
]

# ── Data Models ────────────────────────────────────────────────────────────────

@dataclass
class RawSignal:
    id: str
    collected_at: str
    source: str
    source_subtype: str
    source_tier: str
    topic: str
    raw_title: str
    url: str
    engagement_score: float
    comment_count: int
    upvote_count: int
    is_first_timer: bool
    comments_per_upvote: float
    sentiment_score: float
    is_organic: bool
    extra: dict = field(default_factory=dict)


@dataclass
class GradientScore:
    topic: str
    computed_at: str
    overall_score: float
    gradient_strength: float
    inertia_score: float
    medium_sequence_score: float
    dark_matter_score: float
    confidence_decay: float
    detection_score: float
    confidence_score: float
    signal_count: int
    niche_signal_count: int
    mainstream_signal_count: int
    active_platforms: list
    platform_sequence: list
    first_timer_ratio: float
    engagement_asymmetry_detected: bool
    vocabulary_expansion_rate: float
    lead_time_estimate_days: float
    diffusion_pattern: str
    top_signals: list
    why_this_matters: str
    what_to_watch: str
    confidence_level: str
    false_positive_risk: str


# ── Database Setup ─────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS raw_signals (
    id TEXT PRIMARY KEY,
    collected_at TEXT NOT NULL,
    source TEXT NOT NULL,
    source_subtype TEXT NOT NULL,
    source_tier TEXT NOT NULL,
    topic TEXT NOT NULL,
    raw_title TEXT,
    url TEXT,
    engagement_score REAL DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    upvote_count INTEGER DEFAULT 0,
    is_first_timer INTEGER DEFAULT 0,
    comments_per_upvote REAL DEFAULT 0,
    sentiment_score REAL DEFAULT 0,
    is_organic INTEGER DEFAULT 1,
    extra TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS gradient_scores (
    topic TEXT NOT NULL,
    computed_at TEXT NOT NULL,
    overall_score REAL,
    gradient_strength REAL,
    inertia_score REAL,
    medium_sequence_score REAL,
    dark_matter_score REAL,
    confidence_decay REAL,
    detection_score REAL,
    confidence_score REAL,
    signal_count INTEGER,
    niche_signal_count INTEGER,
    mainstream_signal_count INTEGER,
    first_timer_ratio REAL,
    engagement_asymmetry_detected INTEGER,
    vocabulary_expansion_rate REAL,
    lead_time_estimate_days REAL,
    diffusion_pattern TEXT,
    active_platforms TEXT,
    platform_sequence TEXT,
    top_signals TEXT,
    why_this_matters TEXT,
    what_to_watch TEXT,
    confidence_level TEXT,
    false_positive_risk TEXT,
    PRIMARY KEY (topic, computed_at)
);

CREATE INDEX IF NOT EXISTS idx_signals_topic ON raw_signals (topic, collected_at);
CREATE INDEX IF NOT EXISTS idx_signals_source ON raw_signals (source, collected_at);
CREATE INDEX IF NOT EXISTS idx_scores_topic ON gradient_scores (topic, computed_at DESC);
"""

def init_db(path: str = DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()

def get_db(path: str = None):
    conn = sqlite3.connect(path or DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def insert_signals(signals: list, db_path: str = None):
    if not signals:
        return
    conn = get_db(db_path)
    rows = [(s.id, s.collected_at, s.source, s.source_subtype, s.source_tier,
             s.topic, s.raw_title, s.url, s.engagement_score, s.comment_count,
             s.upvote_count, 1 if s.is_first_timer else 0, s.comments_per_upvote,
             s.sentiment_score, 1 if s.is_organic else 0, json.dumps(s.extra))
            for s in signals]
    conn.executemany(
        "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    conn.close()

def save_gradient_score(gs: GradientScore, db_path: str = None):
    conn = get_db(db_path)
    conn.execute("""
        INSERT OR REPLACE INTO gradient_scores VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        gs.topic, gs.computed_at, gs.overall_score, gs.gradient_strength,
        gs.inertia_score, gs.medium_sequence_score, gs.dark_matter_score,
        gs.confidence_decay, gs.detection_score, gs.confidence_score,
        gs.signal_count, gs.niche_signal_count, gs.mainstream_signal_count,
        gs.first_timer_ratio, 1 if gs.engagement_asymmetry_detected else 0,
        gs.vocabulary_expansion_rate, gs.lead_time_estimate_days,
        gs.diffusion_pattern, json.dumps(gs.active_platforms),
        json.dumps(gs.platform_sequence), json.dumps(gs.top_signals),
        gs.why_this_matters, gs.what_to_watch, gs.confidence_level,
        gs.false_positive_risk
    ))
    conn.commit()
    conn.close()

def fetch_recent_signals(topic: str, hours: int = 72, db_path: str = None) -> list:
    conn = get_db(db_path)
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rows = conn.execute("""
        SELECT * FROM raw_signals
        WHERE topic = ? AND collected_at >= ?
        ORDER BY collected_at ASC
    """, (topic, cutoff)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def fetch_all_topics(hours: int = 48, db_path: str = None) -> list:
    conn = get_db(db_path)
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rows = conn.execute(
        "SELECT DISTINCT topic FROM raw_signals WHERE collected_at >= ?",
        (cutoff,)
    ).fetchall()
    conn.close()
    return [r["topic"] for r in rows]

# Alias used by nowtrend_integration.py
def fetch_all_topics_with_signals(hours: int = 48, db_path: str = None) -> list:
    return fetch_all_topics(hours=hours, db_path=db_path)

def fetch_score_history(topic: str, limit: int = 50, db_path: str = None) -> list:
    conn = get_db(db_path)
    rows = conn.execute("""
        SELECT * FROM gradient_scores WHERE topic = ?
        ORDER BY computed_at DESC LIMIT ?
    """, (topic, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def fetch_top_scores(limit: int = 20, db_path: str = None) -> list:
    conn = get_db(db_path)
    rows = conn.execute("""
        SELECT g1.* FROM gradient_scores g1
        INNER JOIN (
            SELECT topic, MAX(computed_at) as max_at
            FROM gradient_scores GROUP BY topic
        ) g2 ON g1.topic = g2.topic AND g1.computed_at = g2.max_at
        ORDER BY g1.overall_score DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Topic Utilities ────────────────────────────────────────────────────────────

def normalize_topic(text: str) -> str:
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'[@#]', '', text)
    text = re.sub(r'[^\w\s-]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip().lower()[:60]

def extract_topics(title: str) -> list:
    topics = []
    topics.extend(re.findall(r'#(\w{3,40})', title))
    topics.extend(re.findall(r'"([^"]{3,50})"', title))
    tech = re.findall(
        r'\b(AI|LLM|GPT|Claude|Gemini|Llama|Mistral|RAG|agent|embedding|'
        r'diffusion|multimodal|fine.tun\w+|autonomous|open.source)\b',
        title, re.IGNORECASE
    )
    topics.extend([m if isinstance(m, str) else m[0] for m in tech])
    if 5 <= len(title) <= 80:
        topics.append(title)
    seen, result = set(), []
    for t in topics:
        n = normalize_topic(t)
        if n and len(n) >= 3 and n not in seen:
            seen.add(n)
            result.append(n)
    return result[:4]

_sentiment = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str) -> float:
    return _sentiment.polarity_scores(text)['compound']


# ── Data Collectors ────────────────────────────────────────────────────────────

def get_reddit_client():
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        print("Reddit credentials not set — skipping Reddit collection")
        return None
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

def collect_reddit(reddit, limit_per_sub: int = 50) -> list:
    if not reddit:
        return []
    signals = []
    print(f"Collecting Reddit from {len(ALL_SUBREDDITS)} subreddits...")
    for sub_name in ALL_SUBREDDITS:
        tier = "niche" if sub_name in NICHE_SUBREDDITS else "mainstream"
        try:
            subreddit = reddit.subreddit(sub_name)
            recent_authors = set()
            try:
                for old in subreddit.new(limit=200):
                    if old.author:
                        recent_authors.add(str(old.author).lower())
            except Exception:
                pass
            for post in subreddit.hot(limit=limit_per_sub):
                if post.stickied or not post.author:
                    continue
                is_first_timer = str(post.author).lower() not in recent_authors
                comments_per_upvote = post.num_comments / max(post.score, 1)
                engagement = math.log1p(post.score) + math.log1p(post.num_comments * 2)
                is_organic = (post.upvote_ratio >= 0.60 and
                              not (post.score > 5000 and post.num_comments < 10))
                topics = extract_topics(post.title) or [normalize_topic(post.title[:60])]
                sentiment = analyze_sentiment(post.title)
                for topic in topics:
                    sig_id = hashlib.md5(f"{post.id}-{topic}".encode()).hexdigest()[:16]
                    signals.append(RawSignal(
                        id=sig_id,
                        collected_at=datetime.now(timezone.utc).isoformat(),
                        source="reddit", source_subtype=sub_name,
                        source_tier=tier, topic=topic,
                        raw_title=post.title[:500],
                        url=f"https://reddit.com{post.permalink}",
                        engagement_score=round(engagement, 4),
                        comment_count=post.num_comments, upvote_count=post.score,
                        is_first_timer=is_first_timer,
                        comments_per_upvote=round(comments_per_upvote, 4),
                        sentiment_score=round(sentiment, 4), is_organic=is_organic,
                        extra={"subreddit": sub_name, "upvote_ratio": post.upvote_ratio}
                    ))
            time.sleep(0.5)
        except Exception as e:
            print(f"  r/{sub_name} error: {e}")
    print(f"  Reddit: {len(signals)} signals")
    return signals

def collect_github(lookback_hours: int = 48) -> list:
    signals = []
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    since_date = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).strftime("%Y-%m-%d")
    print("Collecting GitHub...")
    for topic in GITHUB_TOPICS:
        try:
            resp = requests.get(
                f"https://api.github.com/search/repositories"
                f"?q=topic:{topic}+created:>{since_date}&sort=stars&order=desc&per_page=30",
                headers=headers, timeout=10
            )
            if resp.status_code == 403:
                time.sleep(60)
                continue
            if resp.status_code != 200:
                continue
            for repo in resp.json().get("items", []):
                stars = repo.get("stargazers_count", 0)
                forks = repo.get("forks_count", 0)
                open_issues = repo.get("open_issues_count", 0)
                created_at = repo.get("created_at", "")
                days_old = 1
                if created_at:
                    try:
                        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        days_old = max(1, (datetime.now(timezone.utc) - created).days)
                    except Exception:
                        pass
                star_velocity = stars / days_old
                engagement = math.log1p(star_velocity) + math.log1p(forks * 2)
                description = repo.get("description", "") or ""
                text = f"{repo.get('full_name','')} {description} {' '.join(repo.get('topics',[]))}"
                topics = extract_topics(text) or [normalize_topic(topic)]
                sentiment = analyze_sentiment(description)
                for t in topics:
                    sig_id = hashlib.md5(f"gh-{repo['id']}-{t}".encode()).hexdigest()[:16]
                    signals.append(RawSignal(
                        id=sig_id,
                        collected_at=datetime.now(timezone.utc).isoformat(),
                        source="github", source_subtype=topic, source_tier="expert",
                        topic=t, raw_title=f"{repo.get('full_name','')}: {description[:200]}",
                        url=repo.get("html_url", ""),
                        engagement_score=round(engagement, 4),
                        comment_count=open_issues, upvote_count=stars,
                        is_first_timer=False,
                        comments_per_upvote=round(open_issues / max(stars, 1), 4),
                        sentiment_score=round(sentiment, 4), is_organic=True,
                        extra={"star_velocity": round(star_velocity, 2), "forks": forks}
                    ))
            time.sleep(1)
        except Exception as e:
            print(f"  GitHub {topic}: {e}")
    print(f"  GitHub: {len(signals)} signals")
    return signals

def collect_hackernews(hours_back: int = 24, min_score: int = 50) -> list:
    signals = []
    cutoff_ts = int((datetime.now(timezone.utc) - timedelta(hours=hours_back)).timestamp())
    print("Collecting Hacker News...")
    try:
        resp = requests.get(
            "https://hn.algolia.com/api/v1/search"
            f"?tags=story&numericFilters=points>{min_score},created_at_i>{cutoff_ts}"
            "&hitsPerPage=100",
            timeout=10
        )
        if resp.status_code != 200:
            return []
        for hit in resp.json().get("hits", []):
            title = hit.get("title", "")
            if not title:
                continue
            points = hit.get("points", 0)
            num_comments = hit.get("num_comments", 0)
            created_ts = hit.get("created_at_i", 0)
            age_hours = max(1, (time.time() - created_ts) / 3600)
            point_velocity = points / age_hours
            engagement = math.log1p(point_velocity * 10) + math.log1p(num_comments)
            sentiment = analyze_sentiment(title)
            topics = extract_topics(title) or [normalize_topic(title[:60])]
            object_id = hit.get("objectID", "")
            story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
            for t in topics:
                sig_id = hashlib.md5(f"hn-{object_id}-{t}".encode()).hexdigest()[:16]
                signals.append(RawSignal(
                    id=sig_id,
                    collected_at=datetime.now(timezone.utc).isoformat(),
                    source="hackernews", source_subtype="front_page", source_tier="expert",
                    topic=t, raw_title=title[:500], url=story_url,
                    engagement_score=round(engagement, 4),
                    comment_count=num_comments, upvote_count=points,
                    is_first_timer=False,
                    comments_per_upvote=round(num_comments / max(points, 1), 4),
                    sentiment_score=round(sentiment, 4), is_organic=True,
                    extra={"point_velocity": round(point_velocity, 2), "age_hours": round(age_hours, 1)}
                ))
    except Exception as e:
        print(f"  HN error: {e}")
    print(f"  HN: {len(signals)} signals")
    return signals


# ── Scoring Components ─────────────────────────────────────────────────────────

def compute_gradient_strength(signals: list) -> float:
    if not signals:
        return 0.0
    niche_eng = sum(s["engagement_score"] for s in signals if s["source_tier"] in ("niche","expert"))
    total_eng = sum(s["engagement_score"] for s in signals)
    if total_eng == 0:
        return 0.0
    niche_ratio = niche_eng / total_eng
    count_bonus = min(1.0, len(signals) / 20)
    return round(min(100, niche_ratio * 100 * (0.7 + 0.3 * count_bonus)), 2)

def compute_inertia_score(signals: list, window_hours: int = 6) -> float:
    if len(signals) < 5:
        return 0.0
    now = datetime.now(timezone.utc)
    windows = defaultdict(list)
    for sig in signals:
        try:
            ts = datetime.fromisoformat(sig["collected_at"].replace("Z", "+00:00"))
            window_idx = int((now - ts).total_seconds() / 3600 / window_hours)
            windows[window_idx].append(sig)
        except Exception:
            continue
    if len(windows) < 2:
        return 0.0
    counts = [len(windows.get(i, [])) for i in range(min(12, max(windows.keys()) + 1))]
    counts.reverse()
    consecutive = max_consecutive = 0
    for i in range(1, len(counts)):
        if counts[i] >= counts[i-1] * 0.9:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 0
    cutoff = now - timedelta(hours=window_hours)
    recent_words, older_words = set(), set()
    for sig in signals:
        try:
            ts = datetime.fromisoformat(sig["collected_at"].replace("Z", "+00:00"))
            words = set(re.findall(r'\b\w{4,}\b', sig.get("raw_title","").lower()))
            (recent_words if ts >= cutoff else older_words).update(words)
        except Exception:
            continue
    vocab_expansion = min(1.0, len(recent_words - older_words) / 20)
    return round(min(100, max_consecutive * 20 + vocab_expansion * 20), 2)

def compute_medium_sequence_score(signals: list) -> tuple:
    if not signals:
        return 0.0, "unknown", []
    platform_first = {}
    for sig in signals:
        key = f"{sig['source']}_{sig['source_tier']}"
        try:
            ts = datetime.fromisoformat(sig["collected_at"].replace("Z", "+00:00"))
            if key not in platform_first or ts < platform_first[key]:
                platform_first[key] = ts
        except Exception:
            continue
    sequence = sorted(platform_first.keys(), key=lambda k: platform_first[k])
    has_github = any("github" in s for s in sequence)
    has_hn = any("hackernews" in s for s in sequence)
    has_niche = any("niche" in s or "expert" in s for s in sequence)
    has_mainstream = any("mainstream" in s for s in sequence)
    if has_github and has_hn:
        gidx = next((i for i, s in enumerate(sequence) if "github" in s), 99)
        hidx = next((i for i, s in enumerate(sequence) if "hackernews" in s), 99)
        if gidx <= hidx:
            score = 92.0 if has_niche else 85.0
            return round(score, 2), "A_builder_to_buyer", sequence
    if has_niche and not has_github:
        nidx = next((i for i, s in enumerate(sequence) if "niche" in s or "expert" in s), 99)
        midx = next((i for i, s in enumerate(sequence) if "mainstream" in s), 99)
        if nidx < midx:
            return (82.0 if has_hn else 75.0), "B_enthusiast_to_mainstream", sequence
    if has_github and not has_hn and has_niche:
        return 70.0, "C_research_to_commerce", sequence
    count = len(set(s.split("_")[0] for s in sequence))
    return (round(min(100, 40 + count * 10), 2), "multi_platform", sequence) if count >= 2 else (20.0, "single_platform", sequence)

def compute_dark_matter_score(signals: list) -> tuple:
    if len(signals) < 3:
        return 0.0, 0.0, False, 0.0
    reddit_sigs = [s for s in signals if s["source"] == "reddit"]
    first_timer_ratio = (sum(1 for s in reddit_sigs if s.get("is_first_timer",0)) / len(reddit_sigs)
                         if reddit_sigs else 0.0)
    asymmetry_count = sum(1 for s in signals
                          if s.get("comment_count",0) > s.get("upvote_count",0) * 0.3
                          and s.get("upvote_count",0) > 10)
    asymmetry_detected = asymmetry_count >= max(2, len(signals) * 0.25)
    word_counter = Counter()
    for sig in signals:
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{5,}\b', sig.get("raw_title",""))
        word_counter.update(w.lower() for w in words)
    threshold = max(2, len(signals) * 0.3)
    vocab_rate = min(1.0, sum(1 for w, c in word_counter.items() if c >= threshold) / 10)
    dark_score = min(100,
        min(100, first_timer_ratio * 150) * 0.45
        + (70 if asymmetry_detected else 0) * 0.35
        + vocab_rate * 100 * 0.20
    )
    return round(dark_score, 2), round(first_timer_ratio, 4), asymmetry_detected, round(vocab_rate, 4)

def compute_confidence_decay(signals: list, score_history: list) -> float:
    if not signals:
        return 50.0
    timestamps = []
    for sig in signals:
        try:
            timestamps.append(datetime.fromisoformat(sig["collected_at"].replace("Z","+00:00")))
        except Exception:
            continue
    if not timestamps:
        return 50.0
    hours_since = (datetime.now(timezone.utc) - max(timestamps)).total_seconds() / 3600
    freshness = max(0, 100 - (hours_since / 72) * 100)
    trajectory = 0
    if len(score_history) >= 2:
        delta = score_history[0].get("overall_score",50) - score_history[-1].get("overall_score",50)
        trajectory = max(-20, min(20, delta * 0.5))
    return round(min(100, max(0, freshness + trajectory)), 2)

def estimate_lead_time(gradient: float, medium_seq: float, dark_matter: float) -> float:
    base = 10 if gradient >= 80 else 6 if gradient >= 60 else 3 if gradient >= 40 else 1
    if dark_matter >= 70: base += 4
    elif dark_matter >= 50: base += 2
    if medium_seq >= 85: base -= 1
    return round(max(1, base), 1)


# ── Master Scoring Function ────────────────────────────────────────────────────

def compute_gradient_score(topic: str, db_path: str = None) -> Optional[GradientScore]:
    signals = fetch_recent_signals(topic, hours=72, db_path=db_path)
    if len(signals) < 3:
        return None
    history = fetch_score_history(topic, limit=10, db_path=db_path)

    G = compute_gradient_strength(signals)
    I = compute_inertia_score(signals)
    M, pattern, sequence = compute_medium_sequence_score(signals)
    D, ft_ratio, asymmetry, vocab_rate = compute_dark_matter_score(signals)
    C = compute_confidence_decay(signals, history)

    overall = round(min(100, G*0.30 + I*0.25 + M*0.20 + D*0.15 + C*0.10), 2)

    # Detection: optimized for earliness
    detection = round(min(100, G*0.40 + D*0.25 + I*0.20 + M*0.10 + C*0.05), 2)

    # Confidence: optimized for precision
    confidence = round(min(100, I*0.35 + M*0.30 + G*0.20 + C*0.10 + D*0.05), 2)

    active_platforms = list(set(s["source"] for s in signals))
    niche_count = sum(1 for s in signals if s["source_tier"] in ("niche","expert"))
    mainstream_count = sum(1 for s in signals if s["source_tier"] == "mainstream")

    confidence_level = ("high" if confidence >= 70 and I >= 50
                        else "medium" if confidence >= 50 or I >= 40
                        else "low")
    fp_risk = ("low" if confidence_level == "high"
               else "medium" if confidence_level == "medium"
               else "high")

    lead_time = estimate_lead_time(G, M, D)

    # Evidence: top 5 signals by engagement
    top_sigs = []
    seen_urls = set()
    for sig in sorted(signals, key=lambda s: s.get("engagement_score",0), reverse=True):
        url = sig.get("url","")
        if url not in seen_urls and len(top_sigs) < 5:
            seen_urls.add(url)
            top_sigs.append({
                "source": sig["source"], "platform": sig["source_subtype"],
                "tier": sig["source_tier"], "title": sig.get("raw_title","")[:150],
                "url": url, "upvotes": sig.get("upvote_count",0),
                "comments": sig.get("comment_count",0)
            })

    return GradientScore(
        topic=topic,
        computed_at=datetime.now(timezone.utc).isoformat(),
        overall_score=overall,
        gradient_strength=G, inertia_score=I,
        medium_sequence_score=M, dark_matter_score=D, confidence_decay=C,
        detection_score=detection, confidence_score=confidence,
        signal_count=len(signals), niche_signal_count=niche_count,
        mainstream_signal_count=mainstream_count,
        active_platforms=active_platforms, platform_sequence=sequence,
        first_timer_ratio=ft_ratio, engagement_asymmetry_detected=asymmetry,
        vocabulary_expansion_rate=vocab_rate, lead_time_estimate_days=lead_time,
        diffusion_pattern=pattern, top_signals=top_sigs,
        why_this_matters=f"Detected across {len(active_platforms)} platform(s). Pattern: {pattern}. Lead time est: {lead_time} days.",
        what_to_watch="Monitor for platform spread and inertia confirmation over next 48h.",
        confidence_level=confidence_level, false_positive_risk=fp_risk
    )


# ── FastAPI Server ─────────────────────────────────────────────────────────────

app = FastAPI(title="Now TrendIn — Gradient Score API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/collect")
def run_collection():
    reddit = get_reddit_client()
    all_signals = []
    if reddit:
        all_signals.extend(collect_reddit(reddit))
    all_signals.extend(collect_github())
    all_signals.extend(collect_hackernews())
    insert_signals(all_signals)
    return {"collected": len(all_signals),
            "reddit": len([s for s in all_signals if s.source == "reddit"]),
            "github": len([s for s in all_signals if s.source == "github"]),
            "hackernews": len([s for s in all_signals if s.source == "hackernews"])}

@app.post("/score/{topic}")
def score_topic(topic: str):
    topic = normalize_topic(topic)
    gs = compute_gradient_score(topic)
    if not gs:
        raise HTTPException(404, f"Insufficient signals for: {topic}")
    save_gradient_score(gs)
    return asdict(gs)

@app.post("/score-all")
def score_all():
    topics = fetch_all_topics(hours=48)
    scored = []
    for topic in topics:
        gs = compute_gradient_score(topic)
        if gs:
            save_gradient_score(gs)
            scored.append({"topic": topic, "score": gs.overall_score})
    return {"scored": len(scored), "results": sorted(scored, key=lambda x: x["score"], reverse=True)}

@app.get("/scores")
def get_top_scores(limit: int = Query(20, ge=1, le=100)):
    return fetch_top_scores(limit)

@app.get("/scores/{topic}")
def get_topic_detail(topic: str):
    topic = normalize_topic(topic)
    history = fetch_score_history(topic, limit=50)
    if not history:
        raise HTTPException(404, f"No scores for: {topic}")
    latest = history[0]
    for f in ["active_platforms","platform_sequence","top_signals"]:
        if isinstance(latest.get(f), str):
            try:
                latest[f] = json.loads(latest[f])
            except Exception:
                latest[f] = []
    return {"latest": latest, "history": history}

@app.get("/signals/{topic}")
def get_signals(topic: str, hours: int = Query(48, ge=1, le=168)):
    topic = normalize_topic(topic)
    signals = fetch_recent_signals(topic, hours=hours)
    return {"topic": topic, "count": len(signals), "signals": signals[:50]}

@app.get("/topics")
def list_topics(hours: int = Query(48, ge=1, le=168)):
    return {"topics": fetch_all_topics(hours=hours)}


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("API running at http://localhost:8000")
    print("Docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
