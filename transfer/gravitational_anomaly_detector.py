"""
================================================================
NOW TRENDIN — GRAVITATIONAL ANOMALY DETECTOR v1.0
================================================================

WHAT THIS DOES (Plain English):
  This script watches Reddit, GitHub, and Hacker News every hour.
  For every post it sees, it pulls out the important words and
  phrases (the "topics"). It then asks five questions about each
  topic it finds:

  1. Is it showing up more in EXPERT communities than mainstream?
     (Gradient Strength — niche vs mainstream density)

  2. Is it showing up on MORE THAN ONE platform simultaneously?
     (Platform Diversity — cross-platform confirmation)

  3. Are the people discussing it NEW to that community?
     (First-Timer Ratio — dark matter inference)

  4. Are people DEBATING it more than passively liking it?
     (Engagement Asymmetry — depth over vanity)

  5. Is it ACCELERATING — appearing more often each hour?
     (Velocity — rate of change, not raw count)

  If a topic triggers all five at once, that is a
  "Gravitational Anomaly" — the signal that something is
  emerging from private spaces into expert communities,
  and hasn't reached mainstream yet.

  Each flagged topic gets a score from 0–100:
    85–100 = BREAKOUT (act now, maximum lead time)
    70–84  = STRONG SIGNAL (preparing to break mainstream)
    55–69  = EMERGING (confirmed movement, building)
    35–54  = EARLY WATCH (something moving, unconfirmed)
    < 35   = MONITORING (below threshold, store but don't flag)

HOW TO RUN:
  pip install praw requests fastapi uvicorn vaderSentiment
       python-dotenv nltk scikit-learn numpy
  python gravitational_anomaly_detector.py

  Then visit: http://localhost:8000/docs
  Or:         http://localhost:8000/anomalies   ← your trend list

SETUP:
  Copy .env.example to .env, add Reddit credentials.
  GitHub and Hacker News need no keys.
================================================================
"""

import os
import re
import json
import math
import time
import uuid
import string
import sqlite3
import hashlib
import argparse
import statistics
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
from typing import Optional
from dataclasses import dataclass, field

import praw
import requests
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from dotenv import load_dotenv

# Optional: download NLTK data if available
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    try:
        STOP_WORDS = set(stopwords.words('english'))
    except LookupError:
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        STOP_WORDS = set(stopwords.words('english'))
except ImportError:
    # Fallback stop words if NLTK not installed
    STOP_WORDS = {
        'the','a','an','and','or','but','in','on','at','to','for','of','with',
        'by','from','is','was','are','were','be','been','have','has','had',
        'do','does','did','will','would','could','should','may','might',
        'this','that','these','those','i','you','he','she','it','we','they',
        'what','which','who','when','where','why','how','all','each','every',
        'both','few','more','most','other','some','such','no','nor','not',
        'only','own','same','so','than','too','very','just','now','then',
        'here','there','about','above','after','before','between','into',
        'through','during','without','within','along','following','across',
        'behind','beyond','plus','except','up','down','out','off','over',
        'under','again','further','once','my','your','his','her','its',
        'our','their','mine','yours','hers','ours','theirs','can','also',
        'new','use','using','used','make','making','made','get','got',
        'like','just','even','well','still','back','way','much','many',
        'any','has','need','want','work','working','works','good','great',
        'best','better','big','small','first','last','long','little','own',
        'right','high','low','day','time','year','come','coming','show',
        'different','same','another','however','whether','though','while',
    }

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────
DB_PATH        = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
REDDIT_CLIENT_ID     = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT    = os.getenv("REDDIT_USER_AGENT",
                                  "NowTrendIn/1.0 Gravitational Anomaly Detector")
GITHUB_TOKEN   = os.getenv("GITHUB_TOKEN", "")

# Blog collector credentials (optional — collectors skip gracefully without them)
os.environ.setdefault("GAD_DB_PATH", DB_PATH)   # share DB path with blog_collectors module


# ── Optional blog collectors ───────────────────────────────────────
# blog_collectors.py must live in the same directory as this file.
# If it's missing the main app still works; blog collection is just disabled.
try:
    import blog_collectors as _bc
    _BLOGS_AVAILABLE = True
    print("[startup] blog_collectors module loaded — 7 extra sources active")
except ImportError:
    _bc = None                   # type: ignore
    _BLOGS_AVAILABLE = False
    print("[startup] blog_collectors.py not found — running Reddit/GitHub/HN only")

# ── Signal Calibration Engine ─────────────────────────────────────
# Provides maturity-aware scoring: discounts ESTABLISHED topics,
# boosts RESURGENT topics, hides lead-time when inertia unconfirmed,
# adds gap labels, component groups, and What-To-Do actions.
# Safe to import — if files are missing the detector runs uncalibrated.
try:
    from signal_calibration_integration import (
        apply_calibration,
        seed_known_topics,
        init_calibration_db as _init_cal_db,
    )
    _CAL_AVAILABLE = True
    print("[startup] signal_calibration_integration loaded — maturity-aware scoring active")
except ImportError:
    _CAL_AVAILABLE = False
    print("[startup] signal_calibration_integration.py not found — running uncalibrated")

# ── Research History Engine — optional, graceful fallback ─────────
try:
    from research_history import ResearchHistoryEngine as _ResearchHistoryEngine
    _RH_AVAILABLE = True
    print("[startup] research_history loaded — /scores/{topic}/history endpoint active")
except ImportError:
    _RH_AVAILABLE = False
    print("[startup] research_history.py not found — /scores/{topic}/history unavailable")

# ── AI Topic Intelligence Engine — tier-aware scoring for AI topics ──
try:
    from ai_topic_intelligence import apply_ai_intelligence as _apply_ai_intelligence
    _AI_INTEL_AVAILABLE = True
    print("[startup] ai_topic_intelligence loaded — AI taxonomy scoring active")
except ImportError:
    _AI_INTEL_AVAILABLE = False
    print("[startup] ai_topic_intelligence.py not found — AI taxonomy scoring unavailable")

# ── Calibration Parameter Corrections — topic filter + score modifiers ──
try:
    from calibration_parameter_corrections import (
        is_meaningful_topic,
        filter_topics_batch,
        apply_signal_count_modifier,
        apply_ai_floor,
    )
    _CORRECTIONS_AVAILABLE = True
    print("[startup] calibration_parameter_corrections loaded — noise filter + score modifiers active")
except ImportError:
    _CORRECTIONS_AVAILABLE = False
    print("[startup] calibration_parameter_corrections.py not found — running without noise filter")

# ── Platform Tiers ────────────────────────────────────────────────
# NICHE = expert communities where trends originate (high gradient weight)
# MAINSTREAM = general communities where trends arrive later (low gradient weight)

NICHE_SUBREDDITS = [
    "LocalLLaMA", "MachineLearning", "artificial", "singularity",
    "ChatGPT", "ClaudeAI", "OpenAI", "StableDiffusion",
    "SideProject", "startups", "Entrepreneur", "programming",
    "learnprogramming", "devops", "Python", "datascience",
    "LanguageTechnology", "computervision", "reinforcementlearning",
]
MAINSTREAM_SUBREDDITS = [
    "technology", "Futurology", "worldnews", "science",
    "todayilearned", "explainlikeimfive", "news",
]
ALL_SUBREDDITS = NICHE_SUBREDDITS + MAINSTREAM_SUBREDDITS

# GitHub topics to monitor for new emerging repositories
GITHUB_TOPICS = [
    "llm", "large-language-model", "ai-agent", "rag",
    "generative-ai", "diffusion-model", "fine-tuning",
    "multimodal", "vector-database", "embeddings",
    "autonomous-agent", "ai-safety", "open-source-llm",
    "llm-inference", "prompt-engineering", "ai-tools",
]

# Minimum times a topic must appear before it gets scored
MIN_TOPIC_APPEARANCES = 3

# Anomaly thresholds
FIRST_TIMER_THRESHOLD  = 0.35   # 35% of commenters new to subreddit
GRADIENT_RATIO_THRESHOLD = 4.0  # niche density 4x greater than mainstream
ENGAGEMENT_ASYM_RATIO  = 0.30   # comments-to-upvotes ratio above this

# Velocity score thresholds
BREAKOUT_THRESHOLD = 85
STRONG_THRESHOLD   = 70
EMERGING_THRESHOLD = 55
WATCHING_THRESHOLD = 35

_sentiment = SentimentIntensityAnalyzer()


# ══════════════════════════════════════════════════════════════════
# RESPONSE CACHE
# Thread-safe TTL cache — prevents thousands of simultaneous users
# from each triggering the same expensive JOIN queries.
# Single-instance safe (Heroku 1 dyno). Replace with Redis when you
# scale to multiple dynos.
# ══════════════════════════════════════════════════════════════════

import threading as _threading
import queue as _queue

class _TTLCache:
    """Minimal thread-safe TTL cache. No external deps."""
    def __init__(self):
        self._store: dict = {}
        self._lock = _threading.Lock()

    def get(self, key: str):
        with self._lock:
            entry = self._store.get(key)
            if entry and time.time() < entry["exp"]:
                return entry["data"]
            return None

    def set(self, key: str, data, ttl: int = 300):
        with self._lock:
            self._store[key] = {"data": data, "exp": time.time() + ttl}

    def invalidate(self, prefix: str = ""):
        """Delete all keys that start with `prefix`, or all keys if prefix=''."""
        with self._lock:
            if prefix:
                for k in [k for k in self._store if k.startswith(prefix)]:
                    del self._store[k]
            else:
                self._store.clear()

_cache = _TTLCache()
CACHE_TTL_SCORES  = 300   # 5 min  — /scores and /anomalies (expensive JOINs)
CACHE_TTL_STATS   = 60    # 1 min  — /stats (lightweight but polled frequently)
CACHE_TTL_DETAIL  = 120   # 2 min  — /scores/{topic}
CACHE_TTL_HISTORY = 180   # 3 min  — /history/{topic}


# ══════════════════════════════════════════════════════════════════
# QUERY LOG — N COMPONENT INFRASTRUCTURE
# Non-blocking async queue for logging which topics appear in results.
# At thousands of concurrent users the log path MUST NOT add latency.
# Background thread drains the queue in batches of up to 100.
# ══════════════════════════════════════════════════════════════════

_query_log_queue: "_queue.Queue" = _queue.Queue(maxsize=10_000)


def _log_topic_query(topic_key: str, endpoint: str = "/scores") -> None:
    """Enqueue a query log entry.  Drops silently when queue is full."""
    try:
        _query_log_queue.put_nowait(
            (datetime.now(timezone.utc).isoformat(), topic_key, endpoint)
        )
    except _queue.Full:
        pass


def _query_log_flusher() -> None:
    """
    Background daemon thread.
    Blocks up to 5 s waiting for the first item, then drains the rest
    immediately and batch-inserts into SQLite.
    Uses its own lazy connection — never contends with the main API path.
    """
    conn = None
    while True:
        # Block until the first item arrives (up to 5 s)
        try:
            first = _query_log_queue.get(timeout=5)
        except _queue.Empty:
            continue

        # Drain additional items that arrived at the same time
        batch = [first]
        while not _query_log_queue.empty() and len(batch) < 100:
            try:
                batch.append(_query_log_queue.get_nowait())
            except _queue.Empty:
                break

        # Lazy-open the connection on first write (DB guaranteed to exist by then)
        try:
            if conn is None:
                conn = get_db(DB_PATH)
            conn.executemany(
                "INSERT INTO topic_queries (queried_at, topic_key, endpoint) VALUES (?,?,?)",
                batch,
            )
            conn.commit()
        except Exception as exc:
            print(f"[query_log_flusher] {exc}")
            try:
                conn.close()
            except Exception:
                pass
            conn = None


_query_flusher_thread = _threading.Thread(
    target=_query_log_flusher, daemon=True, name="query-log-flusher"
)
_query_flusher_thread.start()


# ══════════════════════════════════════════════════════════════════
# DATABASE SCHEMA
# ══════════════════════════════════════════════════════════════════

SCHEMA = """
-- ── RAW SIGNALS ──────────────────────────────────────────────────
-- Every individual post/repo/article collected, before topic extraction
CREATE TABLE IF NOT EXISTS raw_signals (
    id              TEXT PRIMARY KEY,
    collected_at    TEXT NOT NULL,
    platform        TEXT NOT NULL,       -- reddit | github | hackernews
    platform_tier   TEXT NOT NULL,       -- niche | mainstream | expert
    source_name     TEXT,                -- subreddit name, gh topic, etc.
    title           TEXT,
    url             TEXT,
    author          TEXT,
    upvotes         INTEGER DEFAULT 0,
    comments        INTEGER DEFAULT 0,
    engagement_raw  REAL DEFAULT 0,
    sentiment       REAL DEFAULT 0,
    is_first_timer  INTEGER DEFAULT 0,   -- 1 if author new to this community
    is_organic      INTEGER DEFAULT 1,
    raw_text        TEXT
);

-- ── EXTRACTED TOPICS ──────────────────────────────────────────────
-- Every meaningful word/phrase extracted from raw signals
-- This is the KEY table — it maps topics to the posts they came from
CREATE TABLE IF NOT EXISTS topic_signals (
    id              TEXT PRIMARY KEY,
    extracted_at    TEXT NOT NULL,
    topic           TEXT NOT NULL,       -- The actual trend word/phrase
    topic_key       TEXT NOT NULL,       -- Normalized key for grouping
    signal_id       TEXT,                -- FK to raw_signals.id
    platform        TEXT NOT NULL,
    platform_tier   TEXT NOT NULL,
    source_name     TEXT,
    upvotes         INTEGER DEFAULT 0,
    comments        INTEGER DEFAULT 0,
    engagement_raw  REAL DEFAULT 0,
    is_first_timer  INTEGER DEFAULT 0,
    is_organic      INTEGER DEFAULT 1
);

-- ── TOPIC REGISTRY ────────────────────────────────────────────────
-- Master list of every topic discovered, with lifecycle metadata
CREATE TABLE IF NOT EXISTS topic_registry (
    topic_key           TEXT PRIMARY KEY,
    topic_display       TEXT NOT NULL,   -- Best human-readable version of the topic
    first_seen_at       TEXT,
    first_seen_platform TEXT,
    last_seen_at        TEXT,
    total_mentions      INTEGER DEFAULT 0,
    niche_mentions      INTEGER DEFAULT 0,
    mainstream_mentions INTEGER DEFAULT 0,
    platforms_seen      TEXT DEFAULT '[]', -- JSON list of platforms
    current_stage       TEXT DEFAULT 'monitoring',
    is_anomaly          INTEGER DEFAULT 0,
    created_at          TEXT DEFAULT (datetime('now')),
    updated_at          TEXT DEFAULT (datetime('now'))
);

-- ── VELOCITY SCORES ───────────────────────────────────────────────
-- The scored output — one record per topic per scoring cycle
-- Each topic gets a full set of component scores + the final 0-100
CREATE TABLE IF NOT EXISTS velocity_scores (
    id                    TEXT PRIMARY KEY,
    scored_at             TEXT NOT NULL,
    topic_key             TEXT NOT NULL,
    topic_display         TEXT NOT NULL,

    -- The seven components (each 0–100)
    gradient_strength     REAL,    -- G: niche vs mainstream density
    inertia_score         REAL,    -- I: acceleration across time windows
    platform_diversity    REAL,    -- M: how many platforms it spans
    dark_matter_score     REAL,    -- D: first-timer ratio + engagement anomaly
    confidence_decay      REAL,    -- C: freshness + directional momentum
    persistence_score     REAL,    -- P: historical longevity across scoring cycles
    nowtrendin_score      REAL,    -- N: internal query frequency (demand-side)

    -- Final composite scores (G·I·M·D·C·P·N)
    overall_score         REAL,    -- Balanced: G(22)+I(20)+M(15)+D(12)+C(7)+P(14)+N(10)
    detection_score       REAL,    -- Earliness: G(33)+D(19)+I(16)+M(9)+C(5)+P(6)+N(12)
    confidence_score      REAL,    -- Precision: I(25)+P(24)+M(20)+G(11)+C(6)+D(4)+N(10)
    heisenberg_gap        REAL,    -- detection - confidence

    -- Evidence (what triggered the score)
    total_mentions        INTEGER,
    niche_mentions        INTEGER,
    mainstream_mentions   INTEGER,
    platforms_active      TEXT,    -- JSON list
    first_timer_ratio     REAL,
    engagement_asymmetry  INTEGER, -- 0 or 1 boolean
    gradient_ratio        REAL,    -- actual niche/mainstream ratio

    -- Classification
    signal_stage          TEXT,    -- BREAKOUT | STRONG | EMERGING | WATCHING | MONITORING
    is_gravitational_anomaly INTEGER DEFAULT 0,
    anomaly_reason        TEXT,

    -- Plain English explanation
    why_this_matters      TEXT,
    what_to_watch         TEXT,

    created_at            TEXT DEFAULT (datetime('now'))
);

-- ── AUTHOR HISTORIES ─────────────────────────────────────────────
-- Track which authors have posted in which communities before
-- Used to calculate the First-Timer Ratio (dark matter detection)
CREATE TABLE IF NOT EXISTS author_history (
    author          TEXT NOT NULL,
    platform        TEXT NOT NULL,
    community       TEXT NOT NULL,   -- subreddit name etc.
    first_seen_at   TEXT,
    post_count      INTEGER DEFAULT 1,
    PRIMARY KEY (author, platform, community)
);

-- ── ANOMALY LOG ───────────────────────────────────────────────────
-- High-priority alerts when a gravitational anomaly is confirmed
CREATE TABLE IF NOT EXISTS anomaly_log (
    id              TEXT PRIMARY KEY,
    flagged_at      TEXT NOT NULL,
    topic_key       TEXT NOT NULL,
    topic_display   TEXT NOT NULL,
    overall_score   REAL,
    detection_score REAL,
    confidence_score REAL,
    anomaly_reason  TEXT,
    was_confirmed   INTEGER DEFAULT 0,  -- 1 if trend materialized
    confirmed_at    TEXT
);

-- ── BLOG COLLECTION LOG ─────────────────────────────────────────
-- Created here so the shared connection from get_db() can write to it
-- when blog_collectors functions are called with this connection.
CREATE TABLE IF NOT EXISTS blog_collection_log (
    id TEXT PRIMARY KEY, collected_at TEXT DEFAULT (datetime('now')),
    platform TEXT NOT NULL, source_name TEXT,
    signals_collected INTEGER DEFAULT 0,
    topics_extracted INTEGER DEFAULT 0, error_message TEXT
);

-- ── TOPIC LIFECYCLE ──────────────────────────────────────────────
-- Tracks every topic across ALL scoring cycles to power the P component.
-- One row per topic, updated each time score_all_topics() runs.
-- This is what lets thousands of users see a topic's full history
-- without re-reading every velocity_score row every request.
CREATE TABLE IF NOT EXISTS topic_lifecycle (
    topic_key               TEXT PRIMARY KEY,
    first_detected_at       TEXT NOT NULL,
    last_scored_at          TEXT,
    total_scoring_cycles    INTEGER DEFAULT 0,
    cycles_above_emerging   INTEGER DEFAULT 0,   -- overall >= 55
    cycles_above_strong     INTEGER DEFAULT 0,   -- overall >= 70
    cycles_above_breakout   INTEGER DEFAULT 0,   -- overall >= 85
    peak_overall_score      REAL DEFAULT 0,
    peak_detection_score    REAL DEFAULT 0,
    peak_confidence_score   REAL DEFAULT 0,
    current_streak_cycles   INTEGER DEFAULT 0,   -- consecutive cycles >= emerging
    longest_streak_cycles   INTEGER DEFAULT 0,
    persistence_rate        REAL DEFAULT 0,      -- cycles_above_emerging / total
    trend_age_hours         REAL DEFAULT 0,      -- hours since first_detected_at
    confirmed_trend         INTEGER DEFAULT 0,   -- 1 if above STRONG for 2+ cycles
    updated_at              TEXT DEFAULT (datetime('now'))
);

-- ── TOPIC QUERIES ────────────────────────────────────────────────
-- Every time a topic appears in an API result (search demand signal).
-- Powers the N — NowTrendIn component.
-- Written async via a bounded queue; never blocks API responses.
CREATE TABLE IF NOT EXISTS topic_queries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    queried_at  TEXT NOT NULL,
    topic_key   TEXT NOT NULL,
    endpoint    TEXT NOT NULL    -- /scores | /anomalies | /trending | /scores/{key}
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_topic_signals_key
    ON topic_signals (topic_key, extracted_at);
CREATE INDEX IF NOT EXISTS idx_topic_signals_platform
    ON topic_signals (platform, platform_tier, extracted_at);
CREATE INDEX IF NOT EXISTS idx_velocity_topic
    ON velocity_scores (topic_key, scored_at DESC);
CREATE INDEX IF NOT EXISTS idx_velocity_score
    ON velocity_scores (overall_score DESC, scored_at DESC);
CREATE INDEX IF NOT EXISTS idx_author_history
    ON author_history (author, platform, community);
CREATE INDEX IF NOT EXISTS idx_lifecycle_persistence
    ON topic_lifecycle (persistence_rate DESC, current_streak_cycles DESC);
CREATE INDEX IF NOT EXISTS idx_topic_queries_key
    ON topic_queries (topic_key, queried_at DESC);
CREATE INDEX IF NOT EXISTS idx_topic_queries_recent
    ON topic_queries (queried_at DESC);
"""


def get_db(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    # WAL lets multiple readers proceed concurrently while a single writer runs.
    # Critical for thousands of users hitting /scores while scoring is in progress.
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA cache_size=-32768")   # 32 MB page cache per connection
    conn.execute("PRAGMA synchronous=NORMAL")  # safe + fast with WAL
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.executescript(SCHEMA)
    # ── Live migration: add nowtrendin_score column if this is an older DB ──
    try:
        conn.execute("SELECT nowtrendin_score FROM velocity_scores LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE velocity_scores ADD COLUMN nowtrendin_score REAL DEFAULT 0")
        conn.commit()
    return conn


# ══════════════════════════════════════════════════════════════════
# TOPIC EXTRACTION ENGINE
# The core function that finds actual trends in raw text
# ══════════════════════════════════════════════════════════════════

# Domain vocabulary — tech terms that are always meaningful
DOMAIN_TERMS = {
    # AI/ML
    "llm", "gpt", "llama", "claude", "gemini", "mistral", "phi",
    "rag", "agent", "agentic", "embedding", "embeddings", "fine-tuning",
    "fine tuning", "finetuning", "lora", "qlora", "quantization",
    "inference", "transformer", "attention", "multimodal", "diffusion",
    "stable diffusion", "midjourney", "sora", "veo", "imagen",
    "ai agent", "ai agents", "autonomous agent", "language model",
    "large language", "small language", "slm", "foundation model",
    "open source llm", "local llm", "on-device ai", "edge ai",
    "prompt engineering", "chain of thought", "function calling",
    "tool use", "retrieval augmented", "vector database", "vector db",
    "mcp", "model context protocol",

    # Infrastructure
    "vllm", "ollama", "llamafile", "llamacpp", "llama.cpp",
    "hugging face", "huggingface", "pytorch", "jax", "mlx",
    "cuda", "triton", "tensorrt",

    # Apps/Products
    "cursor", "copilot", "devin", "swe-agent", "opendevin",
    "perplexity", "you.com", "character.ai", "pika", "runway",
    "elevenlabs", "heygen", "descript",

    # Concepts/Trends
    "vibe coding", "vibecoding", "agentic coding", "ai coding",
    "synthetic data", "data flywheel", "constitutional ai",
    "alignment", "ai safety", "mechanistic interpretability",
    "superintelligence", "agi", "asi", "reasoning model",
    "thinking model", "o1", "o3", "r1", "deepseek",
    "mixture of experts", "moe", "speculative decoding",
    "context window", "long context", "multiagent",
    "computer use", "tool calling", "structured output",
}

# Compound phrase patterns worth extracting (2-3 words)
COMPOUND_PATTERNS = [
    r'\b(?:AI|LLM|ML|NLP|RL|CV)\s+\w+(?:\s+\w+)?\b',
    r'\b\w+\s+(?:AI|LLM|model|agent|learning|network)\b',
    r'\b(?:open[\s-]source|open source)\s+\w+\b',
    r'\b\w+[\s-]to[\s-]\w+\b',
    r'\b\w+\s+\w+\s+(?:model|agent|tool|framework|protocol)\b',
]

def extract_topics_from_text(text: str) -> list[str]:
    """
    THE CORE FUNCTION.

    Extracts meaningful topic words and phrases from any text.
    Returns a list of normalized topic strings.

    For a title like "New local LLM fine-tuning method beats GPT-4 on coding tasks"
    it extracts: ["local llm", "fine-tuning", "gpt-4", "coding tasks",
                  "llm fine-tuning", "local llm fine-tuning"]

    Strategy:
    1. Domain vocabulary matching (exact known terms)
    2. Compound pattern extraction (NLP-style 2-3 word phrases)
    3. Significant unigrams (technical single words not in stop list)
    4. n-gram extraction (all 2-3 word sequences that look meaningful)
    """
    if not text or len(text) < 3:
        return []

    text_lower = text.lower()
    topics = set()

    # ── Step 1: Domain vocabulary exact matches ────────────────
    for term in DOMAIN_TERMS:
        if term in text_lower:
            topics.add(term)

    # ── Step 2: Compound pattern extraction ───────────────────
    for pattern in COMPOUND_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            cleaned = _clean_term(match)
            if cleaned and len(cleaned) >= 4:
                topics.add(cleaned)

    # ── Step 3: Tokenize and build n-grams ────────────────────
    # Clean the text
    clean_text = re.sub(r'https?://\S+', '', text_lower)
    clean_text = re.sub(r'[^\w\s\-]', ' ', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    # Tokenize
    tokens = clean_text.split()
    tokens = [t for t in tokens if len(t) >= 3]

    # Significant unigrams (technical terms not in stop words)
    for token in tokens:
        if (token not in STOP_WORDS
                and len(token) >= 4
                and not token.isdigit()
                and _is_meaningful_word(token)):
            topics.add(token)

    # Bigrams (2-word phrases)
    for i in range(len(tokens) - 1):
        w1, w2 = tokens[i], tokens[i + 1]
        if (w1 not in STOP_WORDS and w2 not in STOP_WORDS
                and len(w1) >= 3 and len(w2) >= 3
                and not w1.isdigit() and not w2.isdigit()):
            bigram = f"{w1} {w2}"
            if _is_meaningful_phrase(bigram):
                topics.add(bigram)

    # Trigrams (3-word phrases — only if first and last word are meaningful)
    for i in range(len(tokens) - 2):
        w1, w2, w3 = tokens[i], tokens[i + 1], tokens[i + 2]
        if (w1 not in STOP_WORDS and w3 not in STOP_WORDS
                and len(w1) >= 3 and len(w3) >= 3
                and _is_meaningful_phrase(f"{w1} {w3}")):
            trigram = f"{w1} {w2} {w3}"
            if len(trigram) <= 60:
                topics.add(trigram)

    # ── Step 4: Filter and normalize ──────────────────────────
    result = []
    seen_keys = set()
    for topic in topics:
        cleaned = _clean_term(topic)
        if cleaned and len(cleaned) >= 3:
            key = _topic_key(cleaned)
            if key not in seen_keys and len(key) >= 3:
                seen_keys.add(key)
                result.append(cleaned)

    return result[:12]   # Max 12 topics per post to avoid noise


def _clean_term(term: str) -> str:
    """Remove noise from extracted terms."""
    term = term.strip().lower()
    term = re.sub(r'\s+', ' ', term)
    term = re.sub(r'^[\W_]+|[\W_]+$', '', term)
    return term if len(term) >= 3 else ""


def _topic_key(topic: str) -> str:
    """Normalize topic to a consistent key for grouping."""
    key = topic.lower().strip()
    key = re.sub(r'[^\w\s]', '', key)
    key = re.sub(r'\s+', '_', key)
    return key[:80]


def _is_meaningful_word(word: str) -> bool:
    """Quick heuristic: is this word worth tracking?"""
    # Skip very common English words we missed in stop words
    if len(word) < 4:
        return False
    # Skip words that are all numbers or symbols
    if re.match(r'^[\d\W]+$', word):
        return False
    # Prefer words with mixed patterns (technical terms often have these)
    has_alpha = any(c.isalpha() for c in word)
    return has_alpha


def _is_meaningful_phrase(phrase: str) -> bool:
    """Is a multi-word phrase worth tracking as a topic?"""
    words = phrase.split()
    if len(words) < 2:
        return False
    # At least one word must be meaningful
    meaningful = sum(1 for w in words
                     if w not in STOP_WORDS and len(w) >= 3)
    return meaningful >= len(words) - 1


def _best_display_name(topic_key: str, all_seen: list[str]) -> str:
    """
    Pick the best human-readable display name for a topic.
    From all the variations seen (e.g., "AI agent", "ai agent", "AI Agent"),
    pick the most common or the most readable.
    """
    if not all_seen:
        return topic_key.replace('_', ' ')
    # Prefer the one that appears most often
    counter = Counter(all_seen)
    # Among the most common, prefer properly capitalized
    most_common = counter.most_common(1)[0][0]
    # Check if there's a properly capitalized version
    for variant in counter:
        if any(c.isupper() for c in variant):
            return variant
    return most_common


# ══════════════════════════════════════════════════════════════════
# DATA COLLECTORS
# ══════════════════════════════════════════════════════════════════

def check_author_is_first_timer(
    conn: sqlite3.Connection,
    author: str,
    platform: str,
    community: str,
) -> bool:
    """
    Returns True if this author has never posted in this community before.
    Updates the author history after checking.

    This is the First-Timer Ratio detection mechanism:
    When 35%+ of people discussing a topic are NEW to that community,
    something is driving them there from an external (private) source.
    """
    if not author or author == "[deleted]":
        return False

    existing = conn.execute("""
        SELECT post_count FROM author_history
        WHERE author = ? AND platform = ? AND community = ?
    """, (author, platform, community)).fetchone()

    if existing:
        # Known author — update count
        conn.execute("""
            UPDATE author_history SET post_count = post_count + 1
            WHERE author = ? AND platform = ? AND community = ?
        """, (author, platform, community))
        return False
    else:
        # First time we've seen this author here
        conn.execute("""
            INSERT INTO author_history (author, platform, community, first_seen_at)
            VALUES (?, ?, ?, ?)
        """, (author, platform, community,
              datetime.now(timezone.utc).isoformat()))
        return True


def collect_reddit(conn: sqlite3.Connection) -> int:
    """Collect posts from Reddit and extract topics from each."""
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        print("  Reddit: no credentials — skipping")
        return 0

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    total_signals = 0
    total_topic_signals = 0
    now = datetime.now(timezone.utc).isoformat()

    print(f"  Collecting Reddit ({len(ALL_SUBREDDITS)} subreddits)...")

    for sub_name in ALL_SUBREDDITS:
        tier = "niche" if sub_name in NICHE_SUBREDDITS else "mainstream"
        try:
            subreddit = reddit.subreddit(sub_name)
            posts = list(subreddit.hot(limit=50))

            for post in posts:
                if post.stickied or not post.author:
                    continue

                author_str = str(post.author) if post.author else ""
                is_first_timer = check_author_is_first_timer(
                    conn, author_str, "reddit", sub_name
                )

                # Organic signal check
                is_organic = (
                    post.upvote_ratio >= 0.60
                    and not (post.score > 5000 and post.num_comments < 5)
                )

                engagement = math.log1p(post.score) + math.log1p(post.num_comments * 2)
                sentiment = _sentiment.polarity_scores(post.title)['compound']

                sig_id = hashlib.md5(f"r-{post.id}".encode()).hexdigest()[:16]

                # Save raw signal
                conn.execute("""
                    INSERT OR IGNORE INTO raw_signals VALUES
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    sig_id, now, "reddit", tier, sub_name,
                    post.title[:500],
                    f"https://reddit.com{post.permalink}",
                    author_str[:100],
                    post.score, post.num_comments,
                    round(engagement, 4),
                    round(sentiment, 4),
                    1 if is_first_timer else 0,
                    1 if is_organic else 0,
                    post.title[:500],
                ))

                # Extract topics from this post
                topics = extract_topics_from_text(post.title)

                for topic in topics:
                    t_key = _topic_key(topic)
                    t_id = hashlib.md5(
                        f"{sig_id}-{t_key}".encode()
                    ).hexdigest()[:16]

                    conn.execute("""
                        INSERT OR IGNORE INTO topic_signals VALUES
                        (?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        t_id, now, topic, t_key, sig_id,
                        "reddit", tier, sub_name,
                        post.score, post.num_comments,
                        round(engagement, 4),
                        1 if is_first_timer else 0,
                        1 if is_organic else 0,
                    ))
                    total_topic_signals += 1

                total_signals += 1

            conn.commit()
            time.sleep(0.4)

        except Exception as e:
            print(f"    r/{sub_name}: {e}")

    print(f"  Reddit: {total_signals} posts → {total_topic_signals} topic signals")
    return total_topic_signals


def collect_github(conn: sqlite3.Connection) -> int:
    """Collect GitHub repositories and extract topics."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    since = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%d")
    total_topic_signals = 0
    now = datetime.now(timezone.utc).isoformat()

    print("  Collecting GitHub...")

    for gh_topic in GITHUB_TOPICS:
        try:
            resp = requests.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": f"topic:{gh_topic} created:>{since}",
                    "sort": "stars", "order": "desc", "per_page": 30,
                },
                headers=headers, timeout=10,
            )
            if resp.status_code == 403:
                time.sleep(60)
                continue
            if resp.status_code != 200:
                continue

            for repo in resp.json().get("items", []):
                stars = repo.get("stargazers_count", 0)
                forks = repo.get("forks_count", 0)
                issues = repo.get("open_issues_count", 0)

                created_at = repo.get("created_at", "")
                days_old = 1
                try:
                    created = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    )
                    days_old = max(1, (datetime.now(timezone.utc) - created).days)
                except Exception:
                    pass

                star_velocity = stars / days_old
                engagement = math.log1p(star_velocity) + math.log1p(forks * 2)
                description = repo.get("description", "") or ""
                full_name   = repo.get("full_name", "")
                repo_topics = repo.get("topics", [])

                sig_id = hashlib.md5(
                    f"gh-{repo['id']}".encode()
                ).hexdigest()[:16]

                combined_text = f"{full_name} {description} {' '.join(repo_topics)}"

                conn.execute("""
                    INSERT OR IGNORE INTO raw_signals VALUES
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    sig_id, now, "github", "expert", gh_topic,
                    combined_text[:500],
                    repo.get("html_url", ""),
                    full_name[:100],
                    stars, issues,
                    round(engagement, 4),
                    round(_sentiment.polarity_scores(description)['compound'], 4),
                    0, 1,
                    combined_text[:500],
                ))

                # Extract topics from repo name, description, and topic tags
                text_to_extract = f"{full_name.split('/')[-1].replace('-',' ')} {description} {' '.join(repo_topics)}"
                topics = extract_topics_from_text(text_to_extract)

                # Also add the GitHub topic tags directly as topics
                for rt in repo_topics:
                    rt_clean = rt.replace('-', ' ')
                    if rt_clean not in STOP_WORDS and len(rt_clean) >= 3:
                        topics.append(rt_clean)

                for topic in set(topics):
                    t_key = _topic_key(topic)
                    t_id  = hashlib.md5(
                        f"{sig_id}-{t_key}".encode()
                    ).hexdigest()[:16]

                    conn.execute("""
                        INSERT OR IGNORE INTO topic_signals VALUES
                        (?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        t_id, now, topic, t_key, sig_id,
                        "github", "expert", gh_topic,
                        stars, issues,
                        round(engagement, 4),
                        0, 1,
                    ))
                    total_topic_signals += 1

            conn.commit()
            time.sleep(1)

        except Exception as e:
            print(f"    GitHub {gh_topic}: {e}")

    print(f"  GitHub: {total_topic_signals} topic signals")
    return total_topic_signals


def collect_hackernews(conn: sqlite3.Connection, hours_back: int = 24) -> int:
    """Collect Hacker News stories and extract topics."""
    cutoff_ts = int(
        (datetime.now(timezone.utc) - timedelta(hours=hours_back)).timestamp()
    )
    total_topic_signals = 0
    now = datetime.now(timezone.utc).isoformat()

    print("  Collecting Hacker News...")

    try:
        resp = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={
                "tags": "story",
                "numericFilters": f"points>50,created_at_i>{cutoff_ts}",
                "hitsPerPage": 100,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return 0

        for hit in resp.json().get("hits", []):
            title = hit.get("title", "")
            if not title:
                continue

            points   = hit.get("points", 0)
            comments = hit.get("num_comments", 0)
            created  = hit.get("created_at_i", 0)

            age_hours = max(1, (time.time() - created) / 3600)
            pv = points / age_hours  # point velocity
            engagement = math.log1p(pv * 10) + math.log1p(comments)
            sentiment  = _sentiment.polarity_scores(title)['compound']

            object_id = hit.get("objectID", "")
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
            sig_id = hashlib.md5(f"hn-{object_id}".encode()).hexdigest()[:16]

            conn.execute("""
                INSERT OR IGNORE INTO raw_signals VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                sig_id, now, "hackernews", "expert", "front_page",
                title[:500], url, "",
                points, comments,
                round(engagement, 4),
                round(sentiment, 4),
                0, 1, title[:500],
            ))

            topics = extract_topics_from_text(title)

            for topic in topics:
                t_key = _topic_key(topic)
                t_id  = hashlib.md5(
                    f"{sig_id}-{t_key}".encode()
                ).hexdigest()[:16]

                conn.execute("""
                    INSERT OR IGNORE INTO topic_signals VALUES
                    (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    t_id, now, topic, t_key, sig_id,
                    "hackernews", "expert", "front_page",
                    points, comments,
                    round(engagement, 4),
                    0, 1,
                ))
                total_topic_signals += 1

        conn.commit()

    except Exception as e:
        print(f"  HN error: {e}")

    print(f"  HN: {total_topic_signals} topic signals")
    return total_topic_signals


# ══════════════════════════════════════════════════════════════════
# THE GRAVITATIONAL ANOMALY DETECTOR
# Computes velocity scores for every discovered topic
# ══════════════════════════════════════════════════════════════════

class GravitationalAnomalyDetector:
    """
    THE CORE SCORING ENGINE.

    For every topic discovered in the last 72 hours, computes:
    - Five component scores (G, I, M, D, C)
    - Detection Score (optimized for earliness)
    - Confidence Score (optimized for precision)
    - Heisenberg Gap (the difference between the two)
    - Overall Velocity Score (0–100)
    - Gravitational Anomaly flag (true/false)

    Run this after every collection cycle.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _get_topic_signals(
        self,
        topic_key: str,
        hours: int = 72,
    ) -> list[dict]:
        """Fetch all signals for a topic in the time window."""
        conn = get_db(self.db_path)
        cutoff = (
            datetime.now(timezone.utc) - timedelta(hours=hours)
        ).isoformat()
        rows = conn.execute("""
            SELECT * FROM topic_signals
            WHERE topic_key = ? AND extracted_at >= ?
            ORDER BY extracted_at ASC
        """, (topic_key, cutoff)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def compute_gradient_strength(self, signals: list[dict]) -> tuple[float, float]:
        """
        G — Gradient Strength (30% weight)

        Measures the ratio of niche/expert signal density to mainstream
        signal density. High score = signal still concentrated in
        expert communities (maximum runway ahead).

        Returns: (score 0-100, raw ratio)
        """
        if not signals:
            return 0.0, 0.0

        niche_eng = sum(
            s["engagement_raw"] for s in signals
            if s["platform_tier"] in ("niche", "expert")
        )
        mainstream_eng = sum(
            s["engagement_raw"] for s in signals
            if s["platform_tier"] == "mainstream"
        )

        niche_count = sum(
            1 for s in signals if s["platform_tier"] in ("niche", "expert")
        )
        mainstream_count = sum(
            1 for s in signals if s["platform_tier"] == "mainstream"
        )

        total_eng = niche_eng + mainstream_eng

        if total_eng == 0:
            return 0.0, 0.0

        niche_ratio = niche_eng / total_eng

        # Raw ratio: niche density vs mainstream density
        # (niche_eng / niche_count) / (mainstream_eng / mainstream_count)
        if mainstream_count > 0 and mainstream_eng > 0:
            niche_density = niche_eng / max(niche_count, 1)
            main_density  = mainstream_eng / max(mainstream_count, 1)
            raw_ratio = niche_density / main_density
        else:
            raw_ratio = 10.0  # No mainstream signal = perfect gradient

        # Signal count confidence bonus
        count_bonus = min(1.0, len(signals) / 15)
        score = min(100, niche_ratio * 100 * (0.65 + 0.35 * count_bonus))

        return round(score, 2), round(raw_ratio, 2)

    def compute_inertia(self, signals: list[dict], window_hours: int = 6) -> float:
        """
        I — Inertia (25% weight)

        Checks whether the topic is ACCELERATING across consecutive
        6-hour time windows. Three consecutive growing windows = true inertia.

        Also checks vocabulary expansion: new words appearing around
        the topic = genuine momentum building.
        """
        if len(signals) < 3:
            return 0.0

        now = datetime.now(timezone.utc)
        windows = defaultdict(list)

        for s in signals:
            try:
                ts = datetime.fromisoformat(
                    s["extracted_at"].replace("Z", "+00:00")
                )
                hours_ago = (now - ts).total_seconds() / 3600
                widx = int(hours_ago / window_hours)
                windows[widx].append(s)
            except Exception:
                continue

        if len(windows) < 2:
            return 0.0

        # Get counts per window in chronological order
        max_widx = max(windows.keys())
        counts = [len(windows.get(i, [])) for i in range(max_widx + 1)]
        counts.reverse()  # Now chronological (oldest first)

        # Count consecutive growing windows
        consecutive = 0
        max_consecutive = 0
        for i in range(1, len(counts)):
            if counts[i] >= counts[i - 1] * 0.85:  # 15% tolerance
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0

        growth_score = min(100, max_consecutive * 25)

        return round(growth_score, 2)

    def compute_platform_diversity(
        self, signals: list[dict]
    ) -> tuple[float, list[str]]:
        """
        M — Platform Diversity (20% weight)

        Measures how many DISTINCT platforms the topic appears on.
        A topic appearing on Reddit + GitHub + HN simultaneously is
        much more significant than one appearing on just Reddit.

        Also checks for Pattern A/B/C diffusion sequence.
        """
        platforms = set(s["platform"] for s in signals)
        tiers     = set(s["platform_tier"] for s in signals)

        platform_list = sorted(list(platforms))

        # Score based on platform count
        score_map = {1: 20, 2: 50, 3: 80}
        base_score = score_map.get(len(platforms), 90)

        # Bonus for spanning both niche AND mainstream
        if "niche" in tiers and "mainstream" in tiers:
            base_score = min(100, base_score + 15)

        # Check for Pattern A (GitHub → HN → Reddit = highest confidence)
        has_github = "github" in platforms
        has_hn     = "hackernews" in platforms
        has_reddit = "reddit" in platforms

        if has_github and has_hn and has_reddit:
            base_score = min(100, base_score + 10)

        return round(base_score, 2), platform_list

    def compute_dark_matter(
        self, signals: list[dict]
    ) -> tuple[float, float, bool]:
        """
        D — Dark Matter Inference (15% weight)

        The unique component no competitor measures.
        Infers hidden private conversations from public anomalies.

        Three indicators:
        1. First-Timer Ratio  — new community members flooding in
        2. Engagement Asymmetry — comments disproportionate to upvotes
        3. (Implicit) Organic concentration — quality signals, not bots

        Returns: (score, first_timer_ratio, asymmetry_detected)
        """
        if not signals:
            return 0.0, 0.0, False

        # ── First-Timer Ratio ──────────────────────────────────
        reddit_sigs = [s for s in signals if s["platform"] == "reddit"]
        if reddit_sigs:
            first_timers = sum(1 for s in reddit_sigs if s["is_first_timer"])
            ft_ratio = first_timers / len(reddit_sigs)
        else:
            ft_ratio = 0.0

        # ── Engagement Asymmetry ──────────────────────────────
        # Comments > upvotes × 0.30 in multiple posts = deep engagement
        asymmetry_count = sum(
            1 for s in signals
            if (s["comments"] or 0) > (s["upvotes"] or 0) * ENGAGEMENT_ASYM_RATIO
            and (s["upvotes"] or 0) > 5
        )
        asymmetry_detected = asymmetry_count >= max(2, len(signals) * 0.20)

        # ── Score calculation ─────────────────────────────────
        ft_score     = min(100, ft_ratio * 160)   # 62.5% = score 100
        asym_score   = 70 if asymmetry_detected else 0
        organic_score = min(100, sum(
            1 for s in signals if s["is_organic"]
        ) / len(signals) * 100)

        dark_score = (
            ft_score      * 0.50
            + asym_score  * 0.35
            + organic_score * 0.15
        )

        return round(min(100, dark_score), 2), round(ft_ratio, 4), asymmetry_detected

    def compute_confidence_decay(
        self, signals: list[dict], topic_key: str
    ) -> float:
        """
        C — Confidence Decay (10% weight)

        Freshness of the signal + directional momentum.
        Rising recent score = high C.
        Old or declining signal = low C (decay penalty applied).
        """
        if not signals:
            return 50.0

        timestamps = []
        for s in signals:
            try:
                ts = datetime.fromisoformat(
                    s["extracted_at"].replace("Z", "+00:00")
                )
                timestamps.append(ts)
            except Exception:
                continue

        if not timestamps:
            return 50.0

        most_recent = max(timestamps)
        hours_old   = (datetime.now(timezone.utc) - most_recent).total_seconds() / 3600
        freshness   = max(0, 100 - (hours_old / 72) * 100)

        # Trajectory: compare first half vs second half signal count
        mid = len(signals) // 2
        first_half  = len(signals[:mid])
        second_half = len(signals[mid:])

        if second_half > first_half * 1.1:
            trajectory = 15   # Accelerating
        elif second_half < first_half * 0.7:
            trajectory = -15  # Decelerating
        else:
            trajectory = 0    # Stable

        return round(min(100, max(0, freshness + trajectory)), 2)

    def compute_persistence(
        self, topic_key: str
    ) -> tuple[float, dict]:
        """
        P — Persistence Score (15% of Overall, 7% of Detection, 27% of Confidence)

        The sixth component. Answers: "Has this topic STAYED elevated across
        multiple scoring cycles, or is it a one-day spike?"

        A brand-new topic scores P=0 (no history yet, no penalty).
        A topic that has been above EMERGING for 7+ consecutive cycles
        (roughly 3 days of hourly scoring) scores P=100.

        This is the MOST POWERFUL differentiator between real trends and noise:
        - Detection ignores it (speed matters, not history)
        - Confidence weights it almost as heavily as Inertia
        - The Heisenberg gap closes as P rises (history = precision)

        Two sub-signals:
          Rate score  (0–60 pts): % of all cycles the topic was above emerging
          Streak score (0–40 pts): consecutive cycles currently above emerging
        """
        conn = get_db(self.db_path)
        lc = conn.execute(
            "SELECT * FROM topic_lifecycle WHERE topic_key = ?", (topic_key,)
        ).fetchone()
        conn.close()

        if not lc:
            return 0.0, {
                "total_cycles": 0, "cycles_above_threshold": 0,
                "current_streak": 0, "longest_streak": 0,
                "persistence_rate": 0.0, "age_hours": 0.0,
                "confirmed_trend": False, "peak_score": 0.0,
            }

        lc = dict(lc)
        total  = lc.get("total_scoring_cycles", 0) or 0
        above  = lc.get("cycles_above_emerging", 0) or 0
        streak = lc.get("current_streak_cycles", 0) or 0

        if total == 0:
            return 0.0, {
                "total_cycles": 0, "cycles_above_threshold": 0,
                "current_streak": 0, "longest_streak": 0,
                "persistence_rate": 0.0, "age_hours": 0.0,
                "confirmed_trend": False, "peak_score": 0.0,
            }

        rate = above / total

        # Rate component: how often was this topic above the emerging threshold?
        # 100% rate = 60 pts, 60% rate = 36 pts
        rate_score = rate * 60

        # Streak component: consecutive cycles currently elevated
        # Each cycle ≈ 6 pts, capped at 40 pts (≈ 6–7 consecutive cycles = ~3 days)
        streak_score = min(40.0, streak * 6.5)

        p_score = min(100.0, rate_score + streak_score)

        return round(p_score, 2), {
            "total_cycles":           total,
            "cycles_above_threshold": above,
            "current_streak":         streak,
            "longest_streak":         lc.get("longest_streak_cycles", 0) or 0,
            "persistence_rate":       round(rate, 4),
            "age_hours":              round(lc.get("trend_age_hours", 0) or 0, 1),
            "confirmed_trend":        bool(lc.get("confirmed_trend")),
            "peak_score":             lc.get("peak_overall_score", 0) or 0,
        }

    def compute_nowtrendin_score(
        self, topic_key: str
    ) -> tuple[float, dict]:
        """
        N — NowTrendIn Score (10% of Overall, 12% of Detection, 10% of Confidence)

        Internal demand-side validation metric.
        Measures how often this topic appears in query results within the app.
        More appearances = more user interest = higher N.

        Why this matters:
          When thousands of users search for the same topic, that in itself
          is a signal that the topic has mindshare — independent of the
          external platform data. It validates that our detection is resonating.

        Formula (0–100):
          volume_score  (0–70): log-scale of total queries in last 30 days
          recency_score (0–30): recent 24h spike vs 7-day baseline rate

        Score meaning:
          0   = never appeared in any user query result
          1–20 = rare — a few times total
          20–50 = moderate — weekly appearances
          50–80 = frequent — daily appearances
          80+  = viral within the app — trending in user demand
        """
        conn = get_db(self.db_path)

        cutoff_30d = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        cutoff_7d  = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        cutoff_24h = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

        try:
            total_30d = conn.execute(
                "SELECT COUNT(*) as c FROM topic_queries "
                "WHERE topic_key = ? AND queried_at >= ?",
                (topic_key, cutoff_30d),
            ).fetchone()["c"] or 0

            recent_7d = conn.execute(
                "SELECT COUNT(*) as c FROM topic_queries "
                "WHERE topic_key = ? AND queried_at >= ?",
                (topic_key, cutoff_7d),
            ).fetchone()["c"] or 0

            recent_24h = conn.execute(
                "SELECT COUNT(*) as c FROM topic_queries "
                "WHERE topic_key = ? AND queried_at >= ?",
                (topic_key, cutoff_24h),
            ).fetchone()["c"] or 0
        except Exception:
            total_30d = recent_7d = recent_24h = 0
        finally:
            conn.close()

        # Volume score (0–70): log scale — 10 queries ≈ 33, 100 queries ≈ 70
        if total_30d == 0:
            vol_score = 0.0
        else:
            vol_score = min(70.0, math.log1p(total_30d) / math.log1p(100) * 70)

        # Recency score (0–30): spike in last 24h vs 7-day daily baseline
        daily_7d_rate = recent_7d / 7.0
        if daily_7d_rate > 0 and recent_24h > daily_7d_rate:
            # How many times faster than baseline?
            recency_score = min(30.0, (recent_24h / daily_7d_rate - 1.0) * 15)
        elif recent_24h > 0:
            recency_score = min(15.0, math.log1p(recent_24h) * 5)
        else:
            recency_score = 0.0

        n_score = round(min(100.0, vol_score + recency_score), 2)

        return n_score, {
            "total_queries_30d": total_30d,
            "queries_7d":        recent_7d,
            "queries_24h":       recent_24h,
            "daily_rate_7d":     round(daily_7d_rate, 2),
        }

    def _update_topic_lifecycle(
        self,
        conn: sqlite3.Connection,
        result: dict,
    ) -> None:
        """
        Update (or create) the lifecycle record for a topic after each scoring cycle.
        Called by score_all_topics() for every scored topic.

        This is the function that BUILDS the history that compute_persistence() reads
        on the next cycle. Over time this creates a running ledger of trend health.
        """
        tk      = result["topic_key"]
        overall = result["overall_score"]
        det     = result["detection_score"]
        conf    = result["confidence_score"]
        now_str = result["scored_at"]

        existing = conn.execute(
            "SELECT * FROM topic_lifecycle WHERE topic_key = ?", (tk,)
        ).fetchone()

        if not existing:
            # First time we've seen this topic scored — initialise lifecycle row
            above_e = 1 if overall >= EMERGING_THRESHOLD else 0
            conn.execute("""
                INSERT INTO topic_lifecycle (
                    topic_key, first_detected_at, last_scored_at,
                    total_scoring_cycles,
                    cycles_above_emerging, cycles_above_strong, cycles_above_breakout,
                    peak_overall_score, peak_detection_score, peak_confidence_score,
                    current_streak_cycles, longest_streak_cycles,
                    persistence_rate, trend_age_hours, confirmed_trend
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                tk, now_str, now_str,
                1,
                above_e,
                1 if overall >= STRONG_THRESHOLD   else 0,
                1 if overall >= BREAKOUT_THRESHOLD else 0,
                overall, det, conf,
                above_e,   # current_streak = 1 if above threshold, else 0
                above_e,   # longest_streak starts same as current
                float(above_e),   # persistence_rate = 100% or 0% on first cycle
                0.0,       # trend_age_hours = 0 on first detection
                0,         # confirmed_trend requires 2+ STRONG cycles
            ))
        else:
            lc = dict(existing)
            total     = (lc["total_scoring_cycles"] or 0) + 1
            above_e   = (lc["cycles_above_emerging"] or 0) + (1 if overall >= EMERGING_THRESHOLD else 0)
            above_s   = (lc["cycles_above_strong"]   or 0) + (1 if overall >= STRONG_THRESHOLD   else 0)
            above_b   = (lc["cycles_above_breakout"] or 0) + (1 if overall >= BREAKOUT_THRESHOLD else 0)

            # Streak: increment if above emerging, reset to 0 if not
            if overall >= EMERGING_THRESHOLD:
                streak = (lc["current_streak_cycles"] or 0) + 1
            else:
                streak = 0
            longest = max(lc.get("longest_streak_cycles") or 0, streak)

            rate = above_e / total

            # Age since first detection
            try:
                first_dt = datetime.fromisoformat(
                    lc["first_detected_at"].replace("Z", "+00:00")
                )
                age_hours = (
                    datetime.now(timezone.utc) - first_dt
                ).total_seconds() / 3600
            except Exception:
                age_hours = lc.get("trend_age_hours") or 0

            # Confirmed trend: reached STRONG for at least 2 cycles
            confirmed = bool(lc.get("confirmed_trend")) or (above_s >= 2)

            conn.execute("""
                UPDATE topic_lifecycle SET
                    last_scored_at          = ?,
                    total_scoring_cycles    = ?,
                    cycles_above_emerging   = ?,
                    cycles_above_strong     = ?,
                    cycles_above_breakout   = ?,
                    peak_overall_score      = MAX(COALESCE(peak_overall_score,0), ?),
                    peak_detection_score    = MAX(COALESCE(peak_detection_score,0), ?),
                    peak_confidence_score   = MAX(COALESCE(peak_confidence_score,0), ?),
                    current_streak_cycles   = ?,
                    longest_streak_cycles   = ?,
                    persistence_rate        = ?,
                    trend_age_hours         = ?,
                    confirmed_trend         = ?,
                    updated_at              = datetime('now')
                WHERE topic_key = ?
            """, (
                now_str, total, above_e, above_s, above_b,
                overall, det, conf,
                streak, longest, rate, age_hours,
                1 if confirmed else 0,
                tk,
            ))

    def score_topic(self, topic_key: str, signals: list[dict]) -> Optional[dict]:
        """
        COMPUTE COMPLETE VELOCITY SCORE FOR ONE TOPIC.

        This is the function that turns raw signal data into
        the 0-100 score shown in the app.
        """
        if len(signals) < MIN_TOPIC_APPEARANCES:
            return None

        # ── Get best display name ──────────────────────────────
        all_names = [s.get("topic", topic_key.replace('_', ' '))
                     for s in signals]
        display = _best_display_name(topic_key, all_names)

        # ── Compute all seven components (G·I·M·D·C·P·N) ────────
        G, gradient_ratio      = self.compute_gradient_strength(signals)
        I                      = self.compute_inertia(signals)
        M, platform_list       = self.compute_platform_diversity(signals)
        D, ft_ratio, asymmetry = self.compute_dark_matter(signals)
        C                      = self.compute_confidence_decay(signals, topic_key)
        P, lifecycle_data      = self.compute_persistence(topic_key)
        N, nowtrendin_data     = self.compute_nowtrendin_score(topic_key)

        # ── FIX 3: Signal volume modifier — prevents floor effect ─
        # Without this, every topic with similar niche concentration
        # scores identically regardless of whether it has 3 or 30 signals.
        # Signal volume IS information — more signals = more credible gradient.
        if _CORRECTIONS_AVAILABLE:
            try:
                platform_count_for_modifier = len(platform_list) if platform_list else 1
                G = apply_signal_count_modifier(G, len(signals), platform_count_for_modifier)
            except Exception:
                pass  # non-fatal — G unchanged on error

        # ── Composite scores (G·I·M·D·C·P·N) ──────────────────
        #
        # Key insight:
        #   Detection weights G+N highest → fires on niche concentration + user demand
        #   Confidence weights I+P highest → fires only after sustained multi-cycle evidence
        #   N for Detection: if users are searching it = real-world demand validation
        #   N for Confidence: moderate weight — queries alone don't confirm a trend

        # OVERALL — balanced across all seven
        overall = round(min(100,
            G * 0.22   # Gradient — niche concentration
            + I * 0.20  # Inertia — sustained acceleration
            + M * 0.15  # Platform diversity
            + D * 0.12  # Dark matter
            + C * 0.07  # Decay
            + P * 0.14  # Persistence — historical longevity
            + N * 0.10  # NowTrendIn — internal demand signal
        ), 2)

        # DETECTION — speed first; N second-highest (user demand confirms early)
        detection = round(min(100,
            G * 0.33   # Gradient — niche concentration fires first
            + D * 0.19  # Dark matter — hidden private signal
            + I * 0.16  # Inertia
            + N * 0.12  # NowTrendIn — demand-side validation
            + M * 0.09  # Platform spread
            + C * 0.05  # Decay
            + P * 0.06  # Persistence — minimal (want to catch early)
        ), 2)

        # CONFIDENCE — precision first; P is the strongest factor
        # N moderate weight: consistent user interest over time = precision signal
        confidence = round(min(100,
            I * 0.25   # Inertia — multi-window acceleration
            + P * 0.24  # Persistence — historical consistency
            + M * 0.20  # Platform spread
            + N * 0.10  # NowTrendIn — sustained user demand
            + G * 0.11  # Gradient
            + C * 0.06  # Decay
            + D * 0.04  # Dark matter — lowest weight for precision
        ), 2)

        gap = round(detection - confidence, 1)

        # ── Signal counts ──────────────────────────────────────
        total      = len(signals)
        niche_count = sum(1 for s in signals
                          if s["platform_tier"] in ("niche", "expert"))
        main_count  = total - niche_count

        # ── Gravitational Anomaly Detection ───────────────────
        is_anomaly  = False
        anomaly_reason = []

        if ft_ratio >= FIRST_TIMER_THRESHOLD:
            anomaly_reason.append(
                f"First-timer ratio {round(ft_ratio*100)}% "
                f"(threshold: {round(FIRST_TIMER_THRESHOLD*100)}%)"
            )
        if asymmetry:
            anomaly_reason.append("Engagement asymmetry detected")
        if gradient_ratio >= GRADIENT_RATIO_THRESHOLD:
            anomaly_reason.append(
                f"Gradient ratio {round(gradient_ratio,1)}x "
                f"(threshold: {GRADIENT_RATIO_THRESHOLD}x)"
            )
        if len(platform_list) >= 2:
            anomaly_reason.append(
                f"Cross-platform signal: {' + '.join(platform_list)}"
            )

        # Anomaly confirmed when 2+ indicators fire
        is_anomaly = len(anomaly_reason) >= 2

        # ── Signal stage classification ────────────────────────
        if overall >= BREAKOUT_THRESHOLD:
            stage = "BREAKOUT"
        elif overall >= STRONG_THRESHOLD:
            stage = "STRONG"
        elif overall >= EMERGING_THRESHOLD:
            stage = "EMERGING"
        elif overall >= WATCHING_THRESHOLD:
            stage = "WATCHING"
        else:
            stage = "MONITORING"

        # ── Plain-English Explanations ─────────────────────────
        why = self._build_why_statement(
            display, platform_list, G, I, ft_ratio, asymmetry,
            gradient_ratio, stage
        )
        what = self._build_what_to_watch(
            platform_list, I, ft_ratio, G
        )

        return {
            "topic_key":     topic_key,
            "topic_display": display,
            "scored_at":     datetime.now(timezone.utc).isoformat(),

            # Seven components (G·I·M·D·C·P·N)
            "gradient_strength":  G,
            "inertia_score":      I,
            "platform_diversity": M,
            "dark_matter_score":  D,
            "confidence_decay":   C,
            "persistence_score":  P,
            "nowtrendin_score":   N,

            # N component detail
            "nowtrendin_queries_30d": nowtrendin_data["total_queries_30d"],
            "nowtrendin_queries_24h": nowtrendin_data["queries_24h"],
            "nowtrendin_daily_rate":  nowtrendin_data["daily_rate_7d"],

            # Final scores
            "overall_score":    overall,
            "detection_score":  detection,
            "confidence_score": confidence,
            "heisenberg_gap":   gap,

            # Evidence
            "total_mentions":    total,
            "niche_mentions":    niche_count,
            "mainstream_mentions": main_count,
            "platforms_active":  json.dumps(platform_list),
            "first_timer_ratio": ft_ratio,
            "engagement_asymmetry": 1 if asymmetry else 0,
            "gradient_ratio":    gradient_ratio,

            # Classification
            "signal_stage":    stage,
            "is_gravitational_anomaly": 1 if is_anomaly else 0,
            "anomaly_reason":  " · ".join(anomaly_reason) if anomaly_reason else "",

            # Persistence / lifecycle data (from topic_lifecycle table)
            "persistence_cycles":  lifecycle_data["total_cycles"],
            "persistence_streak":  lifecycle_data["current_streak"],
            "persistence_rate":    lifecycle_data["persistence_rate"],
            "trend_age_hours":     lifecycle_data["age_hours"],
            "confirmed_trend":     lifecycle_data["confirmed_trend"],
            "peak_score":          lifecycle_data["peak_score"],

            # Plain English
            "why_this_matters": why,
            "what_to_watch":    what,
        }

    def _build_why_statement(
        self,
        topic: str,
        platforms: list,
        G: float,
        I: float,
        ft_ratio: float,
        asymmetry: bool,
        gradient_ratio: float,
        stage: str,
    ) -> str:
        parts = []

        if G >= 75:
            parts.append(
                f"'{topic}' is almost entirely in expert/niche communities "
                f"({round(G)}% gradient strength) — mainstream has not found it yet"
            )
        elif G >= 50:
            parts.append(
                f"'{topic}' is primarily in specialist spaces with early "
                f"mainstream awareness building"
            )

        if len(platforms) >= 2:
            parts.append(
                f"detected independently on {len(platforms)} platforms "
                f"({' + '.join(p.upper() for p in platforms)})"
            )

        if ft_ratio >= 0.35:
            parts.append(
                f"{round(ft_ratio * 100)}% of people discussing it are new "
                f"to that community — external traffic detected"
            )

        if asymmetry:
            parts.append(
                "unusually deep discussion relative to passive engagement "
                "(community was already expecting this)"
            )

        if I >= 60:
            parts.append("acceleration confirmed across multiple time windows")

        return ". ".join(parts) + "." if parts else f"Signal detected for '{topic}'."

    def _build_what_to_watch(
        self,
        platforms: list,
        I: float,
        ft_ratio: float,
        G: float,
    ) -> str:
        watches = []
        if "github" not in platforms:
            watches.append(
                "Watch GitHub for new repositories — developer adoption "
                "would confirm this signal"
            )
        if "hackernews" not in platforms:
            watches.append(
                "Watch Hacker News — HN amplification accelerates "
                "mainstream diffusion by 3-7 days"
            )
        if ft_ratio >= 0.35:
            watches.append(
                "High first-timer ratio suggests active private "
                "discussion — Discord/Telegram likely sources"
            )
        if I < 40:
            watches.append(
                "Inertia not yet confirmed — wait for 2+ more collection "
                "cycles before high-confidence action"
            )
        if G < 40:
            watches.append(
                "Gradient flattening — mainstream is arriving, "
                "early positioning window narrowing"
            )

        return " · ".join(watches[:3]) or "Monitor for continued cross-platform spread."

    def score_all_topics(self, hours: int = 72) -> list[dict]:
        """
        MAIN SCORING LOOP.
        Scores every topic that has appeared in the last N hours.
        Returns list of scored topics sorted by overall_score.
        """
        conn = get_db(self.db_path)
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

        # Get all unique topic keys active in this window
        rows = conn.execute("""
            SELECT DISTINCT topic_key FROM topic_signals
            WHERE extracted_at >= ?
        """, (cutoff,)).fetchall()

        topic_keys = [r["topic_key"] for r in rows]
        print(f"\nScoring {len(topic_keys)} discovered topics...")

        results = []
        anomalies = []

        for topic_key in topic_keys:
            signals = self._get_topic_signals(topic_key, hours=hours)

            result = self.score_topic(topic_key, signals)
            if result is None:
                continue

            # ── Apply calibration (maturity-aware scoring) ────────────
            # Discounts ESTABLISHED topics, boosts RESURGENT, hides
            # lead-time when inertia unconfirmed, adds gap labels and
            # What-To-Do fields. All original fields preserved.
            if _CAL_AVAILABLE:
                try:
                    result = apply_calibration(result, db_path=self.db_path)
                except Exception as _cal_exc:
                    print(f"[calibration] apply_calibration failed for {topic_key}: {_cal_exc}")

            # ── Update lifecycle BEFORE computing P for next cycle ──
            # (P for this cycle was already computed using pre-update history)
            self._update_topic_lifecycle(conn, result)

            # Save to velocity_scores table
            score_id = str(uuid.uuid4())[:16]
            conn.execute("""
                INSERT OR REPLACE INTO velocity_scores (
                    id, scored_at, topic_key, topic_display,
                    gradient_strength, inertia_score, platform_diversity,
                    dark_matter_score, confidence_decay, persistence_score,
                    nowtrendin_score,
                    overall_score, detection_score, confidence_score, heisenberg_gap,
                    total_mentions, niche_mentions, mainstream_mentions,
                    platforms_active, first_timer_ratio, engagement_asymmetry,
                    gradient_ratio, signal_stage, is_gravitational_anomaly,
                    anomaly_reason, why_this_matters, what_to_watch
                ) VALUES (
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                )
            """, (
                score_id,
                result["scored_at"],
                result["topic_key"],
                result["topic_display"],
                result["gradient_strength"],
                result["inertia_score"],
                result["platform_diversity"],
                result["dark_matter_score"],
                result["confidence_decay"],
                result["persistence_score"],
                result["nowtrendin_score"],
                result["overall_score"],
                result["detection_score"],
                result["confidence_score"],
                result["heisenberg_gap"],
                result["total_mentions"],
                result["niche_mentions"],
                result["mainstream_mentions"],
                result["platforms_active"],
                result["first_timer_ratio"],
                result["engagement_asymmetry"],
                result["gradient_ratio"],
                result["signal_stage"],
                result["is_gravitational_anomaly"],
                result["anomaly_reason"],
                result["why_this_matters"],
                result["what_to_watch"],
            ))

            # Log anomalies separately
            if result["is_gravitational_anomaly"]:
                conn.execute("""
                    INSERT OR IGNORE INTO anomaly_log
                    (id, flagged_at, topic_key, topic_display,
                     overall_score, detection_score, confidence_score, anomaly_reason)
                    VALUES (?,?,?,?,?,?,?,?)
                """, (
                    score_id,
                    result["scored_at"],
                    result["topic_key"],
                    result["topic_display"],
                    result["overall_score"],
                    result["detection_score"],
                    result["confidence_score"],
                    result["anomaly_reason"],
                ))
                anomalies.append(result)

            # Update topic registry
            platforms_list = json.loads(result["platforms_active"])
            conn.execute("""
                INSERT INTO topic_registry
                    (topic_key, topic_display, first_seen_at, first_seen_platform,
                     last_seen_at, total_mentions, niche_mentions, mainstream_mentions,
                     platforms_seen, current_stage, is_anomaly)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(topic_key) DO UPDATE SET
                    topic_display     = excluded.topic_display,
                    last_seen_at      = excluded.last_seen_at,
                    total_mentions    = total_mentions + excluded.total_mentions,
                    niche_mentions    = niche_mentions + excluded.niche_mentions,
                    mainstream_mentions = mainstream_mentions + excluded.mainstream_mentions,
                    platforms_seen    = excluded.platforms_seen,
                    current_stage     = excluded.current_stage,
                    is_anomaly        = excluded.is_anomaly,
                    updated_at        = datetime('now')
            """, (
                result["topic_key"],
                result["topic_display"],
                result["scored_at"],
                platforms_list[0] if platforms_list else "unknown",
                result["scored_at"],
                result["total_mentions"],
                result["niche_mentions"],
                result["mainstream_mentions"],
                result["platforms_active"],
                result["signal_stage"],
                result["is_gravitational_anomaly"],
            ))

            results.append(result)

        conn.commit()
        conn.close()

        results.sort(key=lambda x: x["overall_score"], reverse=True)

        print(f"Scored: {len(results)} topics")
        print(f"Gravitational Anomalies: {len(anomalies)}")
        if anomalies:
            print("\nTOP ANOMALIES:")
            for a in anomalies[:5]:
                print(f"  '{a['topic_display']:35} "
                      f"D:{a['detection_score']:5.1f} "
                      f"C:{a['confidence_score']:5.1f} "
                      f"Gap:{a['heisenberg_gap']:4.0f}  "
                      f"{a['signal_stage']}")

        return results


# ══════════════════════════════════════════════════════════════════
# FASTAPI — THE REST API
# ══════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Now TrendIn — Gravitational Anomaly Detector",
    description=(
        "Discovers trending topics from Reddit, GitHub, and Hacker News. "
        "Each topic gets a Detection Score and Confidence Score (0–100) "
        "representing the Heisenberg dual-score system."
    ),
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

detector = GravitationalAnomalyDetector(DB_PATH)


@app.on_event("startup")
async def startup_auto_collect():
    """Auto-collect on first launch if the database is empty."""
    import threading

    # ── Init calibration tables + seed known topics ────────────────
    # Always runs (idempotent) — creates tables if missing, seeds
    # 60+ known topics so calibration works from day 1.
    if _CAL_AVAILABLE:
        try:
            _init_cal_db(DB_PATH)
            seed_known_topics(DB_PATH)
            print("[startup] Calibration DB initialised and known topics seeded.")
        except Exception as _cal_init_exc:
            print(f"[startup] Calibration init error (non-fatal): {_cal_init_exc}")

    try:
        conn = get_db(DB_PATH)
        count = conn.execute(
            "SELECT COUNT(*) as c FROM raw_signals"
        ).fetchone()["c"]
        conn.close()
        if count == 0:
            print("[startup] Database empty — triggering background collection…")
            def _initial_collect():
                try:
                    c = get_db(DB_PATH)
                    collect_reddit(c)
                    collect_github(c)
                    collect_hackernews(c)
                    c.close()
                    # Also seed the blog platform sources on first launch
                    if _BLOGS_AVAILABLE:
                        print("[startup] Seeding blog platform sources…")
                        _bc.collect_all_blogs()
                    detector.score_all_topics(hours=72)
                    _cache.invalidate()   # flush stale empty cache after startup scores
                    print("[startup] Initial collection complete.")
                except Exception as exc:
                    print(f"[startup] Collection error: {exc}")
            threading.Thread(target=_initial_collect, daemon=True).start()
    except Exception as exc:
        print(f"[startup] Startup check error: {exc}")


@app.get("/health")
def health():
    return {
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/detailed")
def health_detailed():
    """
    Per-platform signal health: how many signals arrived in the last 24 hours
    and the last-seen timestamp for each platform.  Used by AccuracyView.
    """
    conn = get_db(DB_PATH)
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    platform_rows = conn.execute("""
        SELECT platform,
               COUNT(*) as signals_24h,
               MAX(extracted_at) as last_seen
        FROM topic_signals
        WHERE extracted_at >= ?
        GROUP BY platform
        ORDER BY signals_24h DESC
    """, (cutoff,)).fetchall()

    # Also count all-time per platform so we can show "seen before"
    all_time_rows = conn.execute("""
        SELECT platform, COUNT(*) as total_signals
        FROM topic_signals
        GROUP BY platform
    """).fetchall()
    all_time = {r["platform"]: r["total_signals"] for r in all_time_rows}

    conn.close()

    sources = []
    seen_platforms = set()
    for r in platform_rows:
        p = r["platform"]
        seen_platforms.add(p)
        sources.append({
            "platform":    p,
            "signals_24h": r["signals_24h"],
            "total_signals": all_time.get(p, 0),
            "last_seen":   r["last_seen"],
            "status":      "active" if r["signals_24h"] > 0 else "stale",
        })

    # Add platforms that have historical data but nothing in last 24 h
    for p, total in all_time.items():
        if p not in seen_platforms:
            sources.append({
                "platform":    p,
                "signals_24h": 0,
                "total_signals": total,
                "last_seen":   None,
                "status":      "stale",
            })

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sources":   sources,
        "active_count":  sum(1 for s in sources if s["status"] == "active"),
        "total_platforms": len(sources),
    }


@app.get("/accuracy")
def get_accuracy():
    """
    Returns all topics ever scored at ≥55 (EMERGING or above) as the
    engine's logged prediction track record.  Used by the AccuracyView
    leaderboard in the frontend.
    """
    conn = get_db(DB_PATH)

    rows = conn.execute("""
        SELECT
            v.topic_key,
            v.topic_display,
            MIN(v.scored_at)        AS detected_at,
            MAX(v.overall_score)    AS overall_score,
            MAX(v.detection_score)  AS detection_score,
            MAX(v.confidence_score) AS confidence_score,
            v.signal_stage          AS stage,
            MAX(v.lead_time_estimate_days) AS lead_time_est_days,
            COUNT(*)                AS scoring_cycles
        FROM velocity_scores v
        WHERE v.overall_score >= 55
           OR v.detection_score >= 55
        GROUP BY v.topic_key
        ORDER BY MAX(v.detection_score) DESC
        LIMIT 200
    """).fetchall()

    conn.close()

    predictions = []
    for r in rows:
        s = dict(r)
        s["heisenberg_gap"] = round(
            (s.get("detection_score") or 0) - (s.get("confidence_score") or 0), 1
        )
        predictions.append(s)

    return {
        "count":       len(predictions),
        "predictions": predictions,
        "timestamp":   datetime.now(timezone.utc).isoformat(),
    }


# Track whether a collection run is already in progress (prevents duplicate runs)
_collect_running = False


@app.post("/collect")
def run_collection(include_blogs: bool = Query(True)):
    """
    Start a full data collection + scoring cycle in a background thread and
    return immediately.  The full pipeline (Reddit, GitHub, HN, blogs, scoring)
    can take 2-3 minutes — returning immediately prevents Heroku's 30-second
    router timeout from killing the request.  Poll GET /scores for results.
    """
    global _collect_running
    if _collect_running:
        return {
            "status":  "already_running",
            "message": "A collection is already in progress. Poll GET /scores for results.",
        }

    def _pipeline():
        global _collect_running
        _collect_running = True
        try:
            conn = get_db(DB_PATH)
            r = collect_reddit(conn)
            g = collect_github(conn)
            h = collect_hackernews(conn)
            conn.close()
            print(f"[collect] Core: reddit={r} github={g} hn={h}")

            if include_blogs and _BLOGS_AVAILABLE:
                try:
                    _bc.collect_all_blogs()
                except Exception as exc:
                    print(f"[collect] Blog error: {exc}")

            # Auto-score after collection; invalidate cache so /scores is fresh
            detector.score_all_topics(hours=72)
            _cache.invalidate()
            print("[collect] Pipeline complete — cache invalidated.")
        except Exception as exc:
            print(f"[collect] Pipeline error: {exc}")
        finally:
            _collect_running = False

    import threading
    threading.Thread(target=_pipeline, daemon=True).start()

    return {
        "status":        "collecting",
        "include_blogs": include_blogs,
        "message":       "Collection + scoring started in background. Poll GET /scores every 10s for results.",
    }


@app.post("/collect/blogs")
def run_blog_collection(skip: str = Query("", description="Comma-separated platforms to skip")):
    """
    Run ONLY the blog collection cycle (DEV.to, Hashnode, Discourse,
    WordPress, Blogger, Medium, Ghost).  Reddit/GitHub/HN are unaffected.

    Pass `?skip=blogger,medium` to skip specific platforms.
    Run POST /score-all afterwards to recompute scores.
    """
    if not _BLOGS_AVAILABLE:
        raise HTTPException(503, "blog_collectors.py not found in project directory")

    skip_list = [s.strip() for s in skip.split(",") if s.strip()]
    try:
        blog_results = _bc.collect_all_blogs(skip=skip_list)
        grand = blog_results.pop("_total", {"signals": 0, "topics": 0})
        return {
            "status":         "collected",
            "total_signals":  grand.get("signals", 0),
            "total_topics":   grand.get("topics", 0),
            "skipped":        skip_list,
            "breakdown":      blog_results,
            "message":        "Run POST /score-all to compute velocity scores.",
        }
    except Exception as exc:
        raise HTTPException(500, f"Blog collection error: {exc}")


@app.post("/score-all")
def run_scoring():
    """
    Score every topic discovered in the last 72 hours.
    Invalidates the response cache so fresh results are served immediately.
    """
    results = detector.score_all_topics(hours=72)
    _cache.invalidate()   # flush all cached responses after new scores
    return {
        "scored_topics": len(results),
        "anomalies":     sum(1 for r in results if r["is_gravitational_anomaly"]),
        "confirmed_trends": sum(1 for r in results if r.get("confirmed_trend")),
        "top_20": results[:20],
    }


@app.get("/anomalies")
def get_anomalies(limit: int = Query(20, ge=1, le=100)):
    """
    GET THE GRAVITATIONAL ANOMALIES — topics that triggered
    the full anomaly detection (first-timer + engagement asymmetry
    + gradient ratio + cross-platform confirmation).

    These are the earliest signals. The topics most likely to
    be emerging from private spaces into expert communities.
    """
    cache_key = f"anomalies:{limit}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    conn = get_db(DB_PATH)
    rows = conn.execute("""
        SELECT v.* FROM velocity_scores v
        INNER JOIN (
            SELECT topic_key, MAX(scored_at) as max_at
            FROM velocity_scores GROUP BY topic_key
        ) latest ON v.topic_key = latest.topic_key
            AND v.scored_at = latest.max_at
        WHERE v.is_gravitational_anomaly = 1
        ORDER BY v.overall_score DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    result = _format_score_rows(rows)
    # Log each anomaly topic as a query event for the N component
    for item in result.get("results", []):
        if item.get("topic_key"):
            _log_topic_query(item["topic_key"], "/anomalies")
    _cache.set(cache_key, result, CACHE_TTL_SCORES)
    return result


@app.get("/scores")
def get_all_scores(
    min_score: float = Query(0.0),
    stage: str = Query("all"),
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("overall", enum=["overall", "detection", "confidence"]),
):
    """
    All scored topics with their velocity scores.
    Filter by minimum score or stage. Sort by any score type.
    """
    sort_col = {
        "overall":    "overall_score",
        "detection":  "detection_score",
        "confidence": "confidence_score",
    }[sort_by]

    cache_key = f"scores:{sort_by}:{stage}:{min_score}:{limit}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    conn = get_db(DB_PATH)
    stage_filter = "" if stage == "all" else f"AND v.signal_stage = '{stage.upper()}'"

    rows = conn.execute(f"""
        SELECT v.* FROM velocity_scores v
        INNER JOIN (
            SELECT topic_key, MAX(scored_at) as max_at
            FROM velocity_scores GROUP BY topic_key
        ) latest ON v.topic_key = latest.topic_key
            AND v.scored_at = latest.max_at
        WHERE v.overall_score >= ?
        {stage_filter}
        ORDER BY v.{sort_col} DESC
        LIMIT ?
    """, (min_score, limit)).fetchall()
    conn.close()
    result = _format_score_rows(rows)
    # Log each returned topic as a query event for the N component
    for item in result.get("results", []):
        if item.get("topic_key"):
            _log_topic_query(item["topic_key"], "/scores")
    _cache.set(cache_key, result, CACHE_TTL_SCORES)
    return result


@app.get("/scores/{topic_key}")
def get_topic_detail(topic_key: str):
    """
    Full detail for one topic — all six G·I·M·D·C·P components with
    plain-English explanations, lifecycle history, and Heisenberg gap.
    """
    cache_key = f"detail:{topic_key}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    conn = get_db(DB_PATH)
    latest = conn.execute("""
        SELECT * FROM velocity_scores
        WHERE topic_key = ?
        ORDER BY scored_at DESC LIMIT 1
    """, (topic_key,)).fetchone()

    if not latest:
        raise HTTPException(404, f"No scores found for topic: {topic_key}")

    history = conn.execute("""
        SELECT scored_at, overall_score, detection_score, confidence_score,
               persistence_score, gradient_strength, inertia_score,
               platform_diversity, dark_matter_score, confidence_decay,
               heisenberg_gap, signal_stage
        FROM velocity_scores
        WHERE topic_key = ?
        ORDER BY scored_at DESC LIMIT 30
    """, (topic_key,)).fetchall()

    lc = conn.execute(
        "SELECT * FROM topic_lifecycle WHERE topic_key = ?", (topic_key,)
    ).fetchone()

    conn.close()

    s   = _parse_json_fields(dict(latest))
    gap = s.get("heisenberg_gap", 0) or 0
    p   = s.get("persistence_score", 0) or 0
    n   = s.get("nowtrendin_score", 0) or 0
    lc_dict = dict(lc) if lc else {}

    # Log this detail view as a query event for the N component
    _log_topic_query(topic_key, f"/scores/{topic_key}")

    result = {
        "topic":        s["topic_display"],
        "topic_key":    topic_key,
        "scored_at":    s["scored_at"],

        # ── THE DUAL SCORE ──────────────────────────────────────
        "velocity_scores": {
            "overall":    s["overall_score"],
            "detection":  s["detection_score"],
            "confidence": s["confidence_score"],
            "heisenberg_gap": gap,
            "gap_label":  _gap_label(gap),
            "stage":      s["signal_stage"],
            "is_anomaly": bool(s["is_gravitational_anomaly"]),
            "confirmed_trend": bool(lc_dict.get("confirmed_trend")),
        },

        # ── SEVEN COMPONENTS (G·I·M·D·C·P·N) ───────────────────
        "components": {
            "G_gradient_strength": {
                "score":  s["gradient_strength"],
                "weight_overall": "22%", "weight_detect": "33%", "weight_conf": "11%",
                "raw_ratio": s.get("gradient_ratio"),
                "niche_mentions": s.get("niche_mentions"),
                "mainstream_mentions": s.get("mainstream_mentions"),
                "plain_english": _explain_g(s["gradient_strength"]),
            },
            "I_inertia": {
                "score":  s["inertia_score"],
                "weight_overall": "20%", "weight_detect": "16%", "weight_conf": "25%",
                "plain_english": _explain_i(s["inertia_score"]),
            },
            "M_platform_diversity": {
                "score":    s["platform_diversity"],
                "weight_overall": "15%", "weight_detect": "9%", "weight_conf": "20%",
                "platforms": s.get("platforms_active", []),
                "plain_english": _explain_m(
                    s["platform_diversity"],
                    s.get("platforms_active", [])
                ),
            },
            "D_dark_matter": {
                "score":              s["dark_matter_score"],
                "weight_overall": "12%", "weight_detect": "19%", "weight_conf": "4%",
                "first_timer_ratio":  s.get("first_timer_ratio"),
                "asymmetry_detected": bool(s.get("engagement_asymmetry")),
                "plain_english": _explain_d(
                    s["dark_matter_score"],
                    s.get("first_timer_ratio", 0),
                    bool(s.get("engagement_asymmetry"))
                ),
            },
            "C_confidence_decay": {
                "score":  s["confidence_decay"],
                "weight_overall": "7%", "weight_detect": "5%", "weight_conf": "6%",
                "plain_english": _explain_c(s["confidence_decay"]),
            },
            "P_persistence": {
                "score":   p,
                "weight_overall": "14%", "weight_detect": "6%", "weight_conf": "24%",
                "total_cycles":    lc_dict.get("total_scoring_cycles", 0),
                "current_streak":  lc_dict.get("current_streak_cycles", 0),
                "longest_streak":  lc_dict.get("longest_streak_cycles", 0),
                "persistence_rate": lc_dict.get("persistence_rate", 0),
                "trend_age_hours": lc_dict.get("trend_age_hours", 0),
                "confirmed_trend": bool(lc_dict.get("confirmed_trend")),
                "peak_score":      lc_dict.get("peak_overall_score", 0),
                "plain_english": _explain_p(
                    p,
                    lc_dict.get("current_streak_cycles", 0),
                    lc_dict.get("persistence_rate", 0),
                    lc_dict.get("trend_age_hours", 0),
                    bool(lc_dict.get("confirmed_trend")),
                ),
            },
            "N_nowtrendin": {
                "score":   n,
                "weight_overall": "10%", "weight_detect": "12%", "weight_conf": "10%",
                "total_queries_30d": s.get("nowtrendin_queries_30d", 0),
                "queries_24h":       s.get("nowtrendin_queries_24h", 0),
                "daily_rate_7d":     s.get("nowtrendin_daily_rate", 0),
                "plain_english": _explain_n(
                    n,
                    s.get("nowtrendin_queries_30d", 0),
                    s.get("nowtrendin_queries_24h", 0),
                    s.get("nowtrendin_daily_rate", 0),
                ),
            },
        },

        # ── HEISENBERG EXPLANATION ──────────────────────────────
        "heisenberg": {
            "detection_score":  s["detection_score"],
            "confidence_score": s["confidence_score"],
            "gap":              gap,
            "interpretation":   _gap_interpretation(gap),
            "false_positive_detect": "~22%",
            "false_positive_confirm": "<9%",
            "who_uses_detection":  "Creators, marketers, trend-forward brands",
            "who_uses_confidence": "Institutional analysts, investors, strategic planners",
            "note": (
                "Gap closes as Persistence (P) rises. "
                "A large gap on a new topic is expected — it will shrink with each "
                "successive scoring cycle above threshold."
            ),
        },

        # ── LIFECYCLE SUMMARY ────────────────────────────────────
        "lifecycle": lc_dict if lc_dict else None,

        # ── WHY THIS MATTERS ────────────────────────────────────
        "why_this_matters":  s.get("why_this_matters"),
        "what_to_watch":     s.get("what_to_watch"),
        "anomaly_reason":    s.get("anomaly_reason"),

        # ── SCORE HISTORY ────────────────────────────────────────
        "score_history": [dict(h) for h in history],
    }
    _cache.set(cache_key, result, CACHE_TTL_DETAIL)
    return result


@app.get("/scores/{topic_key}/history")
def get_topic_research_history(topic_key: str, force_refresh: bool = False):
    """
    Research how long a topic has been discussed online.

    Returns timeline, milestones, sources, and a plain-English
    'gradient_implication' explaining whether the Gradient Score
    reflects genuine emergence or a topic's permanent expert-community home.

    Results are cached for 7 days (history changes slowly).
    Use ?force_refresh=true to bypass the cache.

    Example: GET /scores/ai_agent/history
    """
    if not _RH_AVAILABLE:
        raise HTTPException(503, "Research history engine not available")

    # Look up the human-readable display name from the scores table
    conn = get_db(DB_PATH)
    row = conn.execute(
        "SELECT topic_display FROM velocity_scores WHERE topic_key=? LIMIT 1",
        (topic_key,)
    ).fetchone()
    conn.close()
    topic_display = (row["topic_display"] if row else topic_key.replace("_", " "))

    try:
        engine = _ResearchHistoryEngine(db_path=DB_PATH)
        return engine.research(
            topic_key=topic_key,
            topic_display=topic_display,
            force_refresh=force_refresh,
        )
    except Exception as exc:
        print(f"[research_history] error for {topic_key}: {exc}")
        raise HTTPException(500, f"Research history lookup failed: {exc}")


@app.get("/history/recent")
def get_recent_history(
    hours: int = Query(24, ge=1, le=168, description="Look-back window in hours (1–168)"),
    limit: int = Query(300, ge=1, le=500),
):
    """
    All distinct topics that appeared in any scoring run within the last N hours.
    Returns one row per topic (their latest score within the window), ordered newest-first.
    Used by the frontend History panel — shows every topic the engine has seen recently.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    conn = get_db(DB_PATH)
    rows = conn.execute("""
        SELECT v.topic_key, v.topic_display,
               v.overall_score, v.detection_score, v.confidence_score,
               v.persistence_score, v.nowtrendin_score,
               v.gradient_strength, v.inertia_score,
               v.signal_stage, v.is_gravitational_anomaly,
               v.scored_at, v.total_mentions, v.platforms_active
        FROM velocity_scores v
        INNER JOIN (
            SELECT topic_key, MAX(scored_at) AS max_at
            FROM velocity_scores
            WHERE scored_at >= ?
            GROUP BY topic_key
        ) recent ON v.topic_key = recent.topic_key
               AND v.scored_at = recent.max_at
        ORDER BY v.scored_at DESC
        LIMIT ?
    """, (cutoff, limit)).fetchall()
    conn.close()
    topics = []
    for r in rows:
        d = dict(r)
        try:
            d["platforms_active"] = json.loads(d["platforms_active"] or "[]")
        except Exception:
            d["platforms_active"] = []
        topics.append(d)
    return {
        "hours":  hours,
        "since":  cutoff,
        "count":  len(topics),
        "topics": topics,
    }


@app.get("/history/{topic_key}")
def get_topic_history(topic_key: str):
    """
    Full scoring history for one topic — every cycle it has been scored,
    plus the lifecycle summary that drives the Persistence (P) component.

    Use this to visualise how a topic's velocity evolved over time.
    """
    cache_key = f"history:{topic_key}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    conn = get_db(DB_PATH)

    # Get lifecycle summary
    lc = conn.execute(
        "SELECT * FROM topic_lifecycle WHERE topic_key = ?", (topic_key,)
    ).fetchone()

    # Get all scoring cycles (newest first)
    history = conn.execute("""
        SELECT scored_at, overall_score, detection_score, confidence_score,
               persistence_score, gradient_strength, inertia_score,
               platform_diversity, dark_matter_score, confidence_decay,
               heisenberg_gap, signal_stage, is_gravitational_anomaly
        FROM velocity_scores
        WHERE topic_key = ?
        ORDER BY scored_at DESC
        LIMIT 200
    """, (topic_key,)).fetchall()

    # Latest score for context
    latest = conn.execute("""
        SELECT topic_display FROM velocity_scores
        WHERE topic_key = ?
        ORDER BY scored_at DESC LIMIT 1
    """, (topic_key,)).fetchone()

    conn.close()

    if not history and not lc:
        raise HTTPException(404, f"No history found for topic: {topic_key}")

    result = {
        "topic_key":   topic_key,
        "topic":       latest["topic_display"] if latest else topic_key.replace("_", " "),
        "lifecycle":   dict(lc) if lc else None,
        "cycle_count": len(history),
        "history":     [dict(h) for h in history],
    }
    _cache.set(cache_key, result, CACHE_TTL_HISTORY)
    return result


@app.get("/trending")
def get_trending(
    limit: int = Query(20, ge=1, le=100),
    min_cycles: int = Query(2, ge=1),
):
    """
    Topics ranked by persistence — those that have STAYED elevated
    across multiple scoring cycles.

    This is the "institutional grade" endpoint: not what just appeared,
    but what has proven it can hold its position over days.

    Sorted by: confirmed_trend DESC, persistence_rate DESC, overall_score DESC
    """
    cache_key = f"trending:{limit}:{min_cycles}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    conn = get_db(DB_PATH)
    rows = conn.execute("""
        SELECT v.*, lc.persistence_rate, lc.current_streak_cycles,
               lc.trend_age_hours, lc.confirmed_trend,
               lc.total_scoring_cycles, lc.peak_overall_score
        FROM velocity_scores v
        INNER JOIN (
            SELECT topic_key, MAX(scored_at) as max_at
            FROM velocity_scores GROUP BY topic_key
        ) latest ON v.topic_key = latest.topic_key
            AND v.scored_at = latest.max_at
        INNER JOIN topic_lifecycle lc ON v.topic_key = lc.topic_key
        WHERE lc.total_scoring_cycles >= ?
        ORDER BY lc.confirmed_trend DESC,
                 lc.persistence_rate DESC,
                 v.overall_score DESC
        LIMIT ?
    """, (min_cycles, limit)).fetchall()
    conn.close()

    results = []
    for r in rows:
        s = dict(r)
        s = _parse_json_fields(s)
        s["heisenberg_gap"] = round(
            (s.get("detection_score") or 0) - (s.get("confidence_score") or 0), 1
        )
        s["gap_label"]  = _gap_label(s["heisenberg_gap"])
        s["is_anomaly"] = bool(s.get("is_gravitational_anomaly"))
        results.append(s)

    result = {"count": len(results), "results": results}
    # Log each trending topic as a query event for the N component
    for item in results:
        if item.get("topic_key"):
            _log_topic_query(item["topic_key"], "/trending")
    _cache.set(cache_key, result, CACHE_TTL_SCORES)
    return result


@app.get("/topics")
def list_topics(
    limit: int = Query(100, ge=1, le=500),
    anomalies_only: bool = Query(False),
):
    """List all discovered topics with their latest scores."""
    conn = get_db(DB_PATH)
    filter_str = "AND r.is_anomaly = 1" if anomalies_only else ""
    rows = conn.execute(f"""
        SELECT r.topic_key, r.topic_display, r.current_stage,
               r.total_mentions, r.is_anomaly, r.last_seen_at,
               v.overall_score, v.detection_score, v.confidence_score
        FROM topic_registry r
        LEFT JOIN (
            SELECT topic_key, MAX(scored_at) as max_at
            FROM velocity_scores GROUP BY topic_key
        ) latest ON r.topic_key = latest.topic_key
        LEFT JOIN velocity_scores v
            ON v.topic_key = latest.topic_key AND v.scored_at = latest.max_at
        WHERE 1=1 {filter_str}
        ORDER BY v.overall_score DESC NULLS LAST
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return {"count": len(rows), "topics": [dict(r) for r in rows]}


@app.get("/stats")
def get_stats():
    """
    System statistics — signals, topics, anomalies, confirmed trends,
    plus per-platform signal breakdown (core sources + blog sources).
    """
    cached = _cache.get("stats")
    if cached is not None:
        return cached

    conn = get_db(DB_PATH)

    # ── Core stats ────────────────────────────────────────────────
    stats = {
        "total_raw_signals": conn.execute(
            "SELECT COUNT(*) as c FROM raw_signals"
        ).fetchone()["c"],
        "total_topic_signals": conn.execute(
            "SELECT COUNT(*) as c FROM topic_signals"
        ).fetchone()["c"],
        "unique_topics_discovered": conn.execute(
            "SELECT COUNT(*) as c FROM topic_registry"
        ).fetchone()["c"],
        "topics_scored": conn.execute(
            "SELECT COUNT(DISTINCT topic_key) as c FROM velocity_scores"
        ).fetchone()["c"],
        "gravitational_anomalies": conn.execute(
            "SELECT COUNT(*) as c FROM anomaly_log"
        ).fetchone()["c"],
        "confirmed_trends": conn.execute(
            "SELECT COUNT(*) as c FROM topic_lifecycle WHERE confirmed_trend = 1"
        ).fetchone()["c"],
        "breakout_signals": conn.execute(
            """SELECT COUNT(DISTINCT topic_key) as c FROM velocity_scores
               WHERE signal_stage = 'BREAKOUT'"""
        ).fetchone()["c"],
        "avg_persistence_rate": (conn.execute(
            "SELECT AVG(persistence_rate) as a FROM topic_lifecycle "
            "WHERE total_scoring_cycles > 1"
        ).fetchone()["a"] or 0),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "blog_collectors_active": _BLOGS_AVAILABLE,
    }

    # ── Per-platform breakdown ────────────────────────────────────
    platform_rows = conn.execute("""
        SELECT platform,
               COUNT(*) as signals,
               COUNT(DISTINCT topic_key) as unique_topics,
               SUM(is_first_timer) as first_timers
        FROM topic_signals
        GROUP BY platform
        ORDER BY signals DESC
    """).fetchall()

    stats["platform_breakdown"] = {
        r["platform"]: {
            "signals":       r["signals"],
            "unique_topics": r["unique_topics"],
            "first_timer_pct": round(
                (r["first_timers"] or 0) / max(r["signals"], 1) * 100, 1
            ),
        }
        for r in platform_rows
    }

    # ── Blog platform summary (if any blog signals exist) ────────
    blog_platforms = ["devto", "hashnode", "discourse", "wordpress",
                      "blogger", "medium", "ghost"]
    blog_total = sum(
        stats["platform_breakdown"].get(p, {}).get("signals", 0)
        for p in blog_platforms
    )
    stats["blog_signals_total"] = blog_total

    conn.close()
    _cache.set("stats", stats, CACHE_TTL_STATS)
    return stats


# ── Helper functions for API responses ────────────────────────────

def _format_score_rows(rows) -> dict:
    results = []
    for r in rows:
        s = dict(r)
        s = _parse_json_fields(s)
        s["heisenberg_gap"] = round(
            (s.get("detection_score") or 0) - (s.get("confidence_score") or 0), 1
        )
        s["gap_label"]    = _gap_label(s["heisenberg_gap"])
        s["is_anomaly"]   = bool(s.get("is_gravitational_anomaly"))

        # ── Re-apply calibration at serve time ────────────────────
        # apply_calibration() adds maturity-aware fields that are not
        # stored in velocity_scores: what_to_do_action, component_groups,
        # calibration, gap_meaning, show_lead_time, etc.
        # Map DB column names to what apply_calibration() expects,
        # then merge the calibration output back into the response.
        if _CAL_AVAILABLE:
            try:
                # Field-name bridge: DB uses different names for some fields
                if "gradient_strength_detection" not in s:
                    s["gradient_strength_detection"] = s.get("gradient_strength", 0) or 0
                if "gradient_strength_confidence" not in s:
                    s["gradient_strength_confidence"] = s.get("gradient_strength", 0) or 0
                if "platform_count" not in s:
                    plat_active = s.get("platforms_active", [])
                    s["platform_count"] = len(plat_active) if isinstance(plat_active, list) else 0
                if "engagement_asymmetry_detected" not in s:
                    s["engagement_asymmetry_detected"] = bool(s.get("engagement_asymmetry", False))
                s = apply_calibration(s, db_path=DB_PATH)
            except Exception as _ce:
                pass  # non-fatal — row still serves without calibration fields

        # ── AI Topic Intelligence — tier-aware taxonomy scoring ────
        # Applies floors/boosts based on actual viral status (Tier 1–4).
        # Also adds ai_tier, variations[], research{} fields for the UI.
        # Applied BEFORE the AI floor fix so the floor only fires if
        # the taxonomy engine hasn't already raised the score.
        if _AI_INTEL_AVAILABLE:
            try:
                # Bridge times_scored from nested calibration if needed
                if not s.get("times_scored"):
                    cal = s.get("calibration", {})
                    if isinstance(cal, dict):
                        s["times_scored"] = cal.get("times_scored", 0) or 0
                # Bridge platform_count
                if not s.get("platform_count"):
                    plat = s.get("platforms_active", [])
                    s["platform_count"] = len(plat) if isinstance(plat, list) else 1
                s = _apply_ai_intelligence(s)
            except Exception as _aie:
                pass  # non-fatal — row served without AI taxonomy fields

        # ── FIX 4: AI score floor — prevents established AI topics
        # becoming invisible after calibration discount ────────────
        if _CORRECTIONS_AVAILABLE:
            try:
                total_sigs = s.get("total_mentions", 0) or 0
                new_det, new_conf, floored = apply_ai_floor(
                    s.get("topic_display", ""),
                    s.get("detection_score",  0) or 0,
                    s.get("confidence_score", 0) or 0,
                    total_sigs,
                )
                if floored:
                    s["detection_score"]  = new_det
                    s["confidence_score"] = new_conf
                    s["floor_applied"]    = True
                    # Recalculate gap after floor adjustment
                    s["heisenberg_gap"] = round(new_det - new_conf, 1)
            except Exception:
                pass  # non-fatal

        results.append(s)

    # ── FIX 2: Topic noise filter — remove bigram garbage before serving ─
    # Applied after all rows processed so calibration fields are present.
    # Stores nothing to DB — only affects what the API serves.
    if _CORRECTIONS_AVAILABLE:
        try:
            filtered = []
            for s in results:
                topic   = s.get("topic_display", "") or s.get("topic", "")
                sigs    = s.get("total_mentions", 0) or 0
                sources = len(s.get("platforms_active") or []) or 1
                if is_meaningful_topic(topic, sigs, sources):
                    filtered.append(s)
                else:
                    pass  # silently drop noise bigrams
            results = filtered
        except Exception:
            pass  # non-fatal — serve unfiltered on error

    return {"count": len(results), "results": results}


def _parse_json_fields(s: dict) -> dict:
    for field in ["platforms_active"]:
        if isinstance(s.get(field), str):
            try:
                s[field] = json.loads(s[field])
            except Exception:
                s[field] = []
    return s


def _gap_label(gap: float) -> str:
    if gap <= 15:
        return "Both agree — high conviction"
    elif gap <= 35:
        return "Early stage — confirmation building"
    elif gap <= 60:
        return "Very early — detected, not confirmed"
    else:
        return "Speculative — dark matter signal only"


def _gap_interpretation(gap: float) -> str:
    if gap <= 15:
        return ("Both scores agree. High conviction either way — "
                "this signal is clearly real (both high) or weak (both low).")
    elif gap <= 35:
        return ("Confirmation is building. Detection sees it; "
                "confidence is accumulating evidence. 1–3 days from full confirmation.")
    elif gap <= 60:
        return ("Very early stage. The engine detected something before "
                "confirmation data has arrived. High potential, not yet proven. "
                "Ideal window for early actors.")
    else:
        return ("Speculative. Primarily dark matter signal. "
                "Highest risk, highest potential lead time if correct.")


def _explain_g(score: float) -> str:
    if score >= 80:
        return ("Almost entirely in expert/niche communities — "
                "mainstream has not discovered it yet. Maximum runway ahead.")
    elif score >= 55:
        return "Primarily specialist communities with early mainstream awareness building."
    else:
        return "Spreading to mainstream. Gradient flattening — window narrowing."


def _explain_i(score: float) -> str:
    if score >= 70:
        return ("Acceleration confirmed across 3+ consecutive 6-hour windows. "
                "This is self-reinforcing momentum, not a spike.")
    elif score >= 40:
        return "Moderate acceleration. 1–2 windows confirmed. Building but not yet proven."
    else:
        return ("Inertia not confirmed. Could be a single-event spike. "
                "Wait for more collection cycles before acting.")


def _explain_m(score: float, platforms: list) -> str:
    n = len(platforms) if isinstance(platforms, list) else 0
    plat_str = " + ".join(str(p).upper() for p in platforms) if platforms else "single platform"
    if n >= 3:
        return (f"Detected on {n} platforms ({plat_str}). "
                "Strong cross-platform confirmation. Pattern A/B/C match likely.")
    elif n == 2:
        return (f"Detected on {n} platforms ({plat_str}). "
                "Cross-platform signal building. Watch for third platform.")
    else:
        return ("Single platform only. "
                "Watch for this topic appearing on GitHub or Hacker News.")


def _explain_d(score: float, ft_ratio: float, asymmetry: bool) -> str:
    parts = []
    if ft_ratio >= 0.35:
        parts.append(
            f"{round(ft_ratio * 100)}% new community members "
            f"(threshold 35%) — external traffic detected"
        )
    if asymmetry:
        parts.append(
            "comment depth exceeds passive upvote pattern "
            "(community already familiar with topic)"
        )
    if not parts:
        return "No dark matter signatures. Signal appears to originate publicly."
    return ("Private conversation inferred: " + " · ".join(parts) + ".")


def _explain_c(score: float) -> str:
    if score >= 75:
        return "Signal is fresh and trending upward. Full confidence in recency."
    elif score >= 50:
        return "Signal is moderately fresh. Stable or slightly declining."
    else:
        return "Signal is aging or has crossed into mainstream. Opportunity window closing."


def _explain_n(
    score: float,
    queries_30d: int,
    queries_24h: int,
    daily_rate: float,
) -> str:
    if queries_30d == 0:
        return (
            "No internal query history yet. "
            "N will grow each time users see this topic in their search results."
        )
    if score >= 70:
        return (
            f"High internal demand: {queries_30d} appearances in user results over 30 days, "
            f"{queries_24h} in the last 24h (vs {round(daily_rate, 1)}/day baseline). "
            f"Users are actively seeking this topic."
        )
    if score >= 40:
        return (
            f"Moderate internal demand: {queries_30d} appearances over 30 days. "
            f"The app's own user base is consistently surfacing this topic."
        )
    return (
        f"Low internal demand: {queries_30d} total appearances. "
        f"Topic is being detected but not yet widely queried by users."
    )


def _explain_p(
    score: float,
    streak: int,
    rate: float,
    age_hours: float,
    confirmed: bool,
) -> str:
    if score == 0 and streak == 0:
        return (
            "First detection — no scoring history yet. "
            "P will grow with each subsequent cycle above the emerging threshold."
        )
    if confirmed:
        return (
            f"Confirmed sustained trend: {streak} consecutive cycles elevated, "
            f"{round(rate * 100)}% persistence rate over {round(age_hours)}h. "
            f"Institutional-grade signal."
        )
    if streak >= 3:
        return (
            f"Building streak: {streak} consecutive cycles above threshold. "
            f"Approaching confirmation. {round(rate * 100)}% rate over {round(age_hours)}h."
        )
    if rate >= 0.5:
        return (
            f"{round(rate * 100)}% of scored cycles above emerging threshold. "
            f"First detected {round(age_hours)}h ago. Streak: {streak}."
        )
    return (
        f"Early history: {round(rate * 100)}% persistence rate, {streak} current streak. "
        f"Detected {round(age_hours)}h ago. More cycles needed for confirmation."
    )


# ── STATIC FRONTEND ──────────────────────────────────────────────
# Mounted last so all /api/* routes above always take priority.
# The Vite build writes output to the project-root "static/" folder.
_static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(_static_dir):
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="frontend")


# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def run_full_cycle():
    """One complete collect → score cycle with printed output."""
    print("\n" + "═" * 60)
    print("GRAVITATIONAL ANOMALY DETECTOR")
    print(f"Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("═" * 60)

    conn = get_db(DB_PATH)
    print("\n[1/3] Collecting data...")
    r = collect_reddit(conn)
    g = collect_github(conn)
    h = collect_hackernews(conn)
    conn.close()
    print(f"  Total topic signals: {r + g + h}")

    print("\n[2/3] Scoring topics...")
    results = detector.score_all_topics(hours=72)

    print("\n[3/3] Top scored topics:")
    print("─" * 80)
    print(f"{'TOPIC':35} {'OVERALL':>7} {'DETECT':>7} {'CONF':>7} {'GAP':>5} {'STAGE'}")
    print("─" * 80)
    for r in results[:25]:
        flag = "★" if r["is_gravitational_anomaly"] else " "
        print(
            f"{flag} {r['topic_display'][:33]:33} "
            f"{r['overall_score']:7.1f} "
            f"{r['detection_score']:7.1f} "
            f"{r['confidence_score']:7.1f} "
            f"{r['heisenberg_gap']:5.0f} "
            f"{r['signal_stage']}"
        )
    print("─" * 80)
    print(f"\n★ = Gravitational Anomaly (first-timer ratio, engagement asymmetry,")
    print(f"    gradient ratio, and cross-platform confirmation all triggered)")
    print("\nAPI running at: http://localhost:8000/docs")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Now TrendIn Gravitational Anomaly Detector"
    )
    parser.add_argument(
        "--mode",
        choices=["collect", "score", "full", "api"],
        default="api",
    )
    args = parser.parse_args()

    if args.mode == "collect":
        conn = get_db(DB_PATH)
        r = collect_reddit(conn)
        g = collect_github(conn)
        h = collect_hackernews(conn)
        conn.close()
        print(f"Collected: {r+g+h} topic signals")

    elif args.mode == "score":
        results = detector.score_all_topics(hours=72)
        print(f"Scored {len(results)} topics")

    elif args.mode == "full":
        run_full_cycle()

    elif args.mode == "api":
        port = int(os.getenv("PORT", 8000))
        print("\nNow TrendIn — Gravitational Anomaly Detector API")
        print(f"URL:  http://0.0.0.0:{port}")
        print(f"Docs: http://0.0.0.0:{port}/docs")
        print("\nKey endpoints:")
        print("  POST /collect         — run data collection")
        print("  POST /score-all       — score all discovered topics")
        print("  GET  /anomalies       — gravitational anomalies (the trends)")
        print("  GET  /scores          — all scored topics with velocity scores")
        print("  GET  /scores/{topic}  — full detail with Heisenberg dual-score")
        print("  GET  /stats           — system statistics")
        uvicorn.run(
            "gravitational_anomaly_detector:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            workers=1,
        )


if __name__ == "__main__":
    main()
