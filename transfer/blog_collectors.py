"""
================================================================
NOW TRENDIN — BLOG COMMUNITY DARK MATTER COLLECTORS
================================================================

TEST COMMIT — VISIBILITY CHECK
----------------------------------------------------------------
This block was added to produce a visible code diff.
Lines added: 5
Lines removed: 0
Status: prototype repository sync confirmed ✓
----------------------------------------------------------------

PLATFORMS COVERED:
  ┌──────────────────┬──────────────────────────────┬──────────┬────────┐
  │ Platform         │ API Type                     │ Auth     │ Tier   │
  ├──────────────────┼──────────────────────────────┼──────────┼────────┤
  │ DEV.to           │ REST JSON (Forem API v1)     │ None*    │ expert │
  │ Hashnode         │ GraphQL (gql.hashnode.com)   │ None     │ expert │
  │ Discourse        │ JSON REST (/latest.json)     │ None     │ niche  │
  │ WordPress.com    │ REST API v1.2                │ None     │ main   │
  │ Blogger (Google) │ REST API v3                  │ API key  │ main   │
  │ Medium           │ RSS tag feeds                │ None     │ main   │
  │ Ghost blogs      │ RSS feeds                    │ None     │ expert │
  └──────────────────┴──────────────────────────────┴──────────┴────────┘
  * DEV.to optional API key raises rate limit to 10 req/s
  * Blogger requires FREE Google Cloud API key (10,000 req/day quota)

NOT INCLUDED (require per-server permissioning):
  - Discord: bot must be invited to each server individually
  - Slack: requires app install per workspace
  - Circle / Tribe: paid plan required for API
  - Reddit: already in gravitational_anomaly_detector.py

HOW TO RUN:
  python blog_collectors.py --mode=collect        # all platforms
  python blog_collectors.py --mode=devto          # one at a time
  python blog_collectors.py --mode=stats          # contribution stats
  python blog_collectors.py --mode=collect --skip blogger,wordpress

BLOGGER SETUP (free API key):
  1. console.cloud.google.com → select/create project
  2. APIs & Services → Library → search "Blogger API v3" → Enable
  3. Credentials → Create credentials → API Key → copy it
  4. Add to .env:  BLOGGER_API_KEY=your_key_here
  Quota: 10,000 requests/day — more than enough.

INSTALL:
  pip install requests vaderSentiment python-dotenv feedparser
================================================================
"""

import os, re, sys, json, math, time, uuid, hashlib, sqlite3, argparse
import xml.etree.ElementTree as ET

# Use the shared SQLite/Postgres shim so blog signals land in the SAME database
# the scorer reads. On Heroku (DATABASE_URL set) this writes to Postgres; without
# it, falls back to local SQLite. Critical: with raw sqlite3 the blog signals
# went to an ephemeral local file and never reached the scored data.
try:
    import db_compat as _db_compat
    _DBCOMPAT = True
except Exception:
    _DBCOMPAT = False
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict
from typing import Optional

import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False

load_dotenv()

DEVTO_API_KEY   = os.getenv("DEVTO_API_KEY", "")
BLOGGER_API_KEY = os.getenv("BLOGGER_API_KEY", "")
HASHNODE_TOKEN  = os.getenv("HASHNODE_TOKEN", "")   # optional — enables search queries
DB_PATH         = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
UA              = "NowTrendIn/1.0 BlogCollector (contact@nowtrendin.com)"

_sent_analyzer = SentimentIntensityAnalyzer()


# ── Topic lists per platform ──────────────────────────────────────

DEVTO_TAGS = [
    "ai","machinelearning","llm","artificialintelligence","programming",
    "python","javascript","typescript","webdev","devops","opensource",
    "productivity","career","startup","beginners","showdev","discuss",
]

HASHNODE_TAGS = [
    "machine-learning","artificial-intelligence","llm","python",
    "javascript","web-development","devops","programming","open-source","startup",
]

HASHNODE_SEARCH_TERMS = [
    "llm","ai agent","fine tuning","local llm","vibe coding",
    "mcp","rag","open source ai","reasoning model","multimodal",
]

DISCOURSE_INSTANCES = [
    {"name":"Hugging Face Forums", "base_url":"https://discuss.huggingface.co","tier":"expert"},
    {"name":"PyTorch Forums",      "base_url":"https://discuss.pytorch.org",   "tier":"expert"},
    {"name":"FastAI Forums",       "base_url":"https://forums.fast.ai",        "tier":"expert"},
    {"name":"Python Discuss",      "base_url":"https://discuss.python.org",    "tier":"expert"},
    {"name":"Discourse Meta",      "base_url":"https://meta.discourse.org",    "tier":"niche"},
]

WORDPRESS_TAGS = [
    "artificial-intelligence","machine-learning","chatgpt","llm",
    "programming","technology","startup","productivity","python","javascript",
]

# Known tech-focused Blogger blog IDs (public — no auth needed to read)
BLOGGER_BLOGS = [
    {"name":"Google AI Blog",       "blog_id":"1565197994926998442", "tier":"expert"},
    {"name":"Official Google Blog", "blog_id":"2399953",             "tier":"mainstream"},
    {"name":"Google Developers",    "blog_id":"596072307862157202",  "tier":"expert"},
]

BLOGGER_SEARCH_TERMS = [
    "artificial intelligence","machine learning","large language model",
    "ChatGPT","AI agent","open source AI","LLM","generative AI",
]

# Medium tag RSS (https://medium.com/tag/*/feed) is blocked by Medium since 2023.
# Replaced with curated AI/tech newsletter RSS feeds that return live content.
NEWSLETTER_FEEDS = [
    {"name": "Ben's Bites",            "url": "https://bensbites.beehiiv.com/feed",                      "tier": "mainstream"},
    {"name": "The Batch (DeepLearning.AI)", "url": "https://www.deeplearning.ai/the-batch/feed/",        "tier": "expert"},
    {"name": "Latent Space",           "url": "https://www.latent.space/feed",                           "tier": "expert"},
    {"name": "AI Snake Oil",           "url": "https://aisnakeoil.substack.com/feed",                    "tier": "expert"},
    {"name": "Last Week in AI",        "url": "https://lastweekin.ai/feed",                              "tier": "expert"},
    {"name": "VentureBeat AI",         "url": "https://venturebeat.com/category/ai/feed/",               "tier": "mainstream"},
    {"name": "MIT Tech Review AI",     "url": "https://www.technologyreview.com/feed/",                  "tier": "mainstream"},
    {"name": "The Sequence",           "url": "https://thesequence.substack.com/feed",                   "tier": "expert"},
    {"name": "Ars Technica Tech",      "url": "https://feeds.arstechnica.com/arstechnica/technology-lab","tier": "mainstream"},
    {"name": "Wired AI",               "url": "https://www.wired.com/feed/tag/artificial-intelligence/rss","tier":"mainstream"},
    # ── Sports + culture desks (added 2026-06-12) — with Reddit disabled these
    #    are the niche-tier sensors for non-tech domains. "Tier" is per-domain:
    #    a dedicated football/music desk is the devotee tier relative to general
    #    news, so domain-specialist feeds are niche; broad-brand sport/culture
    #    sections are mainstream. All free, keyless RSS. ──
    {"name": "Guardian Football",      "url": "https://www.theguardian.com/football/rss",               "tier": "niche"},
    {"name": "ESPN Soccer",            "url": "https://www.espn.com/espn/rss/soccer/news",              "tier": "niche"},
    {"name": "Football365",            "url": "https://www.football365.com/feed",                       "tier": "niche"},
    {"name": "BBC Sport Football",     "url": "https://feeds.bbci.co.uk/sport/football/rss.xml",        "tier": "mainstream"},
    {"name": "Sky Sports News",        "url": "https://www.skysports.com/rss/12040",                    "tier": "mainstream"},
    {"name": "Guardian Sport",         "url": "https://www.theguardian.com/sport/rss",                  "tier": "mainstream"},
    {"name": "Pitchfork News",         "url": "https://pitchfork.com/feed/feed-news/rss",               "tier": "niche"},
    {"name": "Variety",                "url": "https://variety.com/feed/",                              "tier": "mainstream"},
    {"name": "Billboard",              "url": "https://www.billboard.com/feed/",                        "tier": "mainstream"},
    {"name": "Hollywood Reporter",     "url": "https://www.hollywoodreporter.com/feed/",                "tier": "mainstream"},
]

GHOST_FEEDS = [
    {"name":"The Gradient",            "url":"https://thegradient.pub/rss/",                        "tier":"expert"},
    {"name":"Interconnects AI",        "url":"https://www.interconnects.ai/feed",                   "tier":"expert"},
    {"name":"Ahead of AI",             "url":"https://magazine.sebastianraschka.com/feed",           "tier":"expert"},
    {"name":"Import AI",               "url":"https://importai.substack.com/feed",                  "tier":"expert"},
    {"name":"The Pragmatic Engineer",  "url":"https://newsletter.pragmaticengineer.com/feed",        "tier":"mainstream"},
    {"name":"Towards Data Science",    "url":"https://towardsdatascience.com/feed",                  "tier":"mainstream"},
    {"name":"AI Supremacy",            "url":"https://aisupremacy.substack.com/feed",                "tier":"expert"},
]


# ── Stop words & domain terms (mirrors gravitational_anomaly_detector.py) ──

STOP_WORDS = {
    'the','a','an','and','or','but','in','on','at','to','for','of','with',
    'by','from','is','was','are','were','be','been','have','has','had',
    'do','does','did','will','would','could','should','may','might','this',
    'that','these','those','i','you','he','she','it','we','they','what',
    'which','who','when','where','why','how','all','each','every','both',
    'few','more','most','other','some','such','no','nor','not','only','own',
    'same','so','than','too','very','just','now','then','here','there',
    'about','after','before','between','through','without','up','down',
    'my','your','his','her','its','our','their','can','also','use','using',
    'used','make','get','like','even','well','still','back','way','much',
    'many','any','need','want','work','good','great','best','better','new',
    'first','last','long','right','high','low','day','time','year','come',
    'post','article','blog','read','write','written','published','author',
    'comment','share','view','click','subscribe','newsletter','email',
    'update','learn','learning','know','try','trying','example','tutorial',
    'guide','introduction','intro','overview','quick','simple','easy',
    'basic','advanced','part','section','series','chapter',
}

DOMAIN_TERMS = {
    "llm","gpt","llama","claude","gemini","mistral","phi","deepseek",
    "rag","agent","agentic","embedding","embeddings","fine-tuning",
    "fine tuning","finetuning","lora","qlora","quantization","inference",
    "transformer","attention","multimodal","diffusion","stable diffusion",
    "ai agent","ai agents","autonomous agent","language model",
    "large language model","small language model","foundation model",
    "open source llm","local llm","on-device ai","edge ai",
    "prompt engineering","chain of thought","function calling","tool use",
    "retrieval augmented","vector database","vector db","mcp",
    "model context protocol","vllm","ollama","hugging face","huggingface",
    "pytorch","vibe coding","vibecoding","agentic coding","ai coding",
    "synthetic data","constitutional ai","alignment","ai safety",
    "mechanistic interpretability","superintelligence","agi","asi",
    "reasoning model","mixture of experts","moe","speculative decoding",
    "context window","long context","multiagent","computer use",
    "structured output","cursor","copilot","perplexity","elevenlabs",
    "open source","generative ai","genai","ai startup","ai tools",
    "machine learning","deep learning","neural network","natural language",
    "nlp","computer vision","reinforcement learning",
}


# ── Database schema ────────────────────────────────────────────────
# Defines only the tables this module writes to.
# The main gravitational_anomaly_detector.py defines the full schema;
# these CREATE IF NOT EXISTS statements are safe to run on top of it.

SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_signals (
    id TEXT PRIMARY KEY, collected_at TEXT NOT NULL,
    platform TEXT NOT NULL, platform_tier TEXT NOT NULL,
    source_name TEXT, title TEXT, url TEXT, author TEXT,
    upvotes INTEGER DEFAULT 0, comments INTEGER DEFAULT 0,
    engagement_raw REAL DEFAULT 0, sentiment REAL DEFAULT 0,
    is_first_timer INTEGER DEFAULT 0, is_organic INTEGER DEFAULT 1,
    raw_text TEXT
);
CREATE TABLE IF NOT EXISTS topic_signals (
    id TEXT PRIMARY KEY, extracted_at TEXT NOT NULL,
    topic TEXT NOT NULL, topic_key TEXT NOT NULL,
    signal_id TEXT, platform TEXT NOT NULL,
    platform_tier TEXT NOT NULL, source_name TEXT,
    upvotes INTEGER DEFAULT 0, comments INTEGER DEFAULT 0,
    engagement_raw REAL DEFAULT 0,
    is_first_timer INTEGER DEFAULT 0, is_organic INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS author_history (
    author TEXT NOT NULL, platform TEXT NOT NULL,
    community TEXT NOT NULL, first_seen_at TEXT,
    post_count INTEGER DEFAULT 1,
    PRIMARY KEY (author, platform, community)
);
CREATE TABLE IF NOT EXISTS blog_collection_log (
    id TEXT PRIMARY KEY, collected_at TEXT DEFAULT (datetime('now')),
    platform TEXT NOT NULL, source_name TEXT,
    signals_collected INTEGER DEFAULT 0,
    topics_extracted INTEGER DEFAULT 0, error_message TEXT
);
CREATE INDEX IF NOT EXISTS idx_ts_key  ON topic_signals (topic_key, extracted_at);
CREATE INDEX IF NOT EXISTS idx_ts_plat ON topic_signals (platform, extracted_at);
"""


def get_conn(path=DB_PATH):
    """Open the SHARED database (Postgres on Heroku via db_compat, else SQLite).
    Routing through db_compat is what makes blog signals actually reach the
    scored data instead of an ephemeral local SQLite file."""
    if _DBCOMPAT:
        c = _db_compat.connect(path)
        try:
            c.executescript(SCHEMA)   # CREATE TABLE IF NOT EXISTS — no-op when present
        except Exception:
            pass
        return c
    c = sqlite3.connect(path, check_same_thread=False, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA cache_size=-32768")
    c.execute("PRAGMA synchronous=NORMAL")
    c.executescript(SCHEMA)
    return c

def _now():      return datetime.now(timezone.utc).isoformat()
def _id(p, u):   return hashlib.md5(f"{p}-{u}".encode()).hexdigest()[:16]
def _key(t):
    k = re.sub(r'[^\w\s]', '', t.lower().strip())
    return re.sub(r'\s+', '_', k)[:80]
def _eng(u, c):  return round(math.log1p(max(0, u)) + math.log1p(max(0, c) * 2), 4)
def _sent(t):    return round(_sent_analyzer.polarity_scores(t or '')['compound'], 4)

def _http_get(url, params=None, headers=None, timeout=12):
    h = {"User-Agent": UA}
    if headers: h.update(headers)
    try:
        r = requests.get(url, params=params, headers=h, timeout=timeout)
        if r.status_code == 429:
            print(f"    Rate limited — sleeping 20s"); time.sleep(20); return None
        return r if r.status_code == 200 else None
    except Exception as e:
        print(f"    HTTP error: {e}"); return None

def _first_timer(conn, author, platform, community):
    if not author: return False
    row = conn.execute(
        "SELECT post_count FROM author_history WHERE author=? AND platform=? AND community=?",
        (author, platform, community)).fetchone()
    if row:
        conn.execute(
            "UPDATE author_history SET post_count=post_count+1 "
            "WHERE author=? AND platform=? AND community=?",
            (author, platform, community)); return False
    conn.execute(
        "INSERT INTO author_history (author,platform,community,first_seen_at) VALUES (?,?,?,?)",
        (author, platform, community, _now())); return True

def _write_signal(conn, sig_id, platform, tier, source, title, url, author,
                  upvotes, comments, ft, organic, raw_text=""):
    conn.execute(
        "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
        sig_id, _now(), platform, tier, source,
        (title or "")[:500], url, (author or "")[:100],
        upvotes, comments, _eng(upvotes, comments), _sent(title),
        1 if ft else 0, 1 if organic else 0, (raw_text or title or "")[:500]))

def _write_topics(conn, sig_id, topics, platform, tier, source, upvotes, comments, organic):
    eng = _eng(upvotes, comments)
    n = 0
    for topic in topics:
        k = _key(topic)
        t_id = _id(sig_id, k)
        conn.execute(
            "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            t_id, _now(), topic, k, sig_id,
            platform, tier, source,
            upvotes, comments, eng, 0, 1 if organic else 0))
        n += 1
    return n

def _log(conn, platform, source, sigs, topics, error=None):
    conn.execute(
        "INSERT OR IGNORE INTO blog_collection_log "
        "(id,platform,source_name,signals_collected,topics_extracted,error_message) "
        "VALUES (?,?,?,?,?,?)",
        (_id("log", f"{platform}-{_now()}"), platform, source, sigs, topics, error))


def extract_topics(text, tags=None):
    if not text: return []
    topics = set()
    tl = text.lower()
    for term in DOMAIN_TERMS:
        if term in tl: topics.add(term)
    if tags:
        for t in tags:
            tc = re.sub(r'[-_]', ' ', t).lower().strip()
            if len(tc) >= 3 and tc not in STOP_WORDS: topics.add(tc)
    clean = re.sub(r'https?://\S+', '', tl)
    clean = re.sub(r'[^\w\s]', ' ', clean)
    tokens = [w for w in clean.split() if len(w) >= 3 and not w.isdigit()]
    for tok in tokens:
        if tok not in STOP_WORDS and len(tok) >= 5: topics.add(tok)
    for i in range(len(tokens) - 1):
        w1, w2 = tokens[i], tokens[i + 1]
        if w1 not in STOP_WORDS and w2 not in STOP_WORDS: topics.add(f"{w1} {w2}")
    for i in range(len(tokens) - 2):
        w1, w2, w3 = tokens[i], tokens[i + 1], tokens[i + 2]
        if w1 not in STOP_WORDS and w3 not in STOP_WORDS:
            tr = f"{w1} {w2} {w3}"
            if len(tr) <= 60: topics.add(tr)
    seen, result = set(), []
    for t in sorted(topics, key=len, reverse=True):
        k = _key(t)
        if k not in seen and len(k) >= 3:
            seen.add(k); result.append(t.strip())
    return result[:10]

def _parse_rss(url):
    r = _http_get(url, headers={"Accept": "application/rss+xml, application/xml"})
    if not r: return []
    if HAS_FEEDPARSER:
        feed = feedparser.parse(r.content)
        return [{"title": e.get("title", ""), "link": e.get("link", ""),
                 "author": e.get("author", ""), "summary": e.get("summary", ""),
                 "tags": [t.get("term", "") for t in e.get("tags", [])]}
                for e in feed.entries]
    try:
        root = ET.fromstring(r.content)
        items = root.findall(".//item") or \
                root.findall(".//{http://www.w3.org/2005/Atom}entry")
        return [{"title": (i.findtext("title") or "").strip(),
                 "link":  (i.findtext("link")  or "").strip(),
                 "author": "", "summary": (i.findtext("description") or "").strip(),
                 "tags": []}
                for i in items]
    except Exception:
        return []


# ════════════════════════════════════════════════════════════════════
# COLLECTOR 1: DEV.TO
# REST API — https://developers.forem.com/api/v1
# No auth needed for public data · Rate: 10 req/s unauthenticated
# ════════════════════════════════════════════════════════════════════

def collect_devto(conn):
    """
    DEV.to — largest developer blogging community (Forem platform).

    Dark matter signals:
    - Developer articles = INTENTIONAL writing (hours of effort)
    - Engagement asymmetry: comments > reactions × 0.30 = genuine debate
    - First-timer authors writing about a NEW topic = strongest signal
    - New tags trending = developers choosing new vocabulary
    """
    headers = {"Accept": "application/vnd.forem.api-v1+json", "User-Agent": UA}
    if DEVTO_API_KEY: headers["api-key"] = DEVTO_API_KEY
    BASE = "https://dev.to/api/articles"
    total_s, total_t = 0, 0
    print(f"  [DEV.to] {len(DEVTO_TAGS)} tag feeds + trending...")

    def process(articles, src):
        nonlocal total_s, total_t
        for a in articles:
            title    = a.get("title", "")
            url      = a.get("url", "")
            author   = (a.get("user") or {}).get("username", "")
            upvotes  = a.get("public_reactions_count", 0)
            comments = a.get("comments_count", 0)
            tags     = a.get("tag_list", [])
            aid      = str(a.get("id", ""))
            asymmetric = comments > upvotes * 0.30 and upvotes > 8
            organic    = upvotes > 0 or comments > 0
            ft = _first_timer(conn, author, "devto", src)
            sid = _id("dt", f"{aid}-{src}")
            text = f"{title} {a.get('description', '')}"
            _write_signal(conn, sid, "devto", "expert", src, title, url, author,
                          upvotes, comments * 2 if asymmetric else comments, ft, organic, text)
            n = _write_topics(conn, sid, extract_topics(text, tags=tags),
                              "devto", "expert", src, upvotes, comments, organic)
            total_s += 1; total_t += n

    for tag in DEVTO_TAGS:
        r = _http_get(BASE, params={"tag": tag, "top": 7, "per_page": 30}, headers=headers)
        if r: process(r.json(), f"devto/tag/{tag}")
        time.sleep(0.15)

    r = _http_get(BASE, params={"top": 1, "per_page": 50}, headers=headers)
    if r: process(r.json(), "devto/trending")

    conn.commit(); _log(conn, "devto", "all", total_s, total_t)
    print(f"  [DEV.to] {total_s} articles -> {total_t} topics")
    return total_s, total_t


# ════════════════════════════════════════════════════════════════════
# COLLECTOR 2: HASHNODE
# GraphQL API — https://apidocs.hashnode.com
# No auth needed · POST https://gql.hashnode.com
# ════════════════════════════════════════════════════════════════════

def _hn_query(gql, variables=None, auth_token=None):
    headers = {"Content-Type": "application/json", "User-Agent": UA}
    if auth_token:
        headers["Authorization"] = auth_token
    try:
        r = requests.post("https://gql.hashnode.com",
            json={"query": gql, "variables": variables or {}},
            headers=headers, timeout=15)
        if r.status_code == 429: time.sleep(20); return None
        if r.status_code != 200: return None
        d = r.json()
        return None if "errors" in d else d.get("data")
    except Exception as e:
        print(f"    Hashnode error: {e}"); return None

_HN_TAG_GQL = """
query TagPosts($slug:String!,$first:Int!){
  tag(slug:$slug){
    posts(first:$first){
      edges{node{
        id title brief url reactionCount responseCount
        tags{name} author{username}
      }}
    }
  }
}"""

_HN_SEARCH_GQL = """
query Search($query:String!,$first:Int!){
  searchPosts(input:{query:$query,first:$first}){
    edges{node{
      id title brief url reactionCount responseCount
      tags{name} author{username}
    }}
  }
}"""

def collect_hashnode(conn):
    """
    Hashnode — developer-focused blogging community.

    Dark matter signals:
    - Independent developer blogs chosen by genuine interest
    - responses > reactions × 0.35 = deep engagement asymmetry
    - First-time authors on a NEW topic = very high signal
    """
    total_s, total_t = 0, 0
    print(f"  [Hashnode] {len(HASHNODE_TAGS)} tags + {len(HASHNODE_SEARCH_TERMS)} search terms...")

    def process_edges(edges, src):
        nonlocal total_s, total_t
        for edge in edges:
            node      = edge.get("node", {})
            title     = node.get("title", "")
            url       = node.get("url", "")
            author    = (node.get("author") or {}).get("username", "")
            reactions = node.get("reactionCount", 0)
            responses = node.get("responseCount", 0)
            tags      = [t["name"] for t in node.get("tags", [])]
            nid       = str(node.get("id", ""))
            asymmetric = responses > reactions * 0.35 and reactions > 4
            ft = _first_timer(conn, author, "hashnode", src)
            sid = _id("hn", nid)
            text = f"{title} {node.get('brief', '')}"
            _write_signal(conn, sid, "hashnode", "expert", src, title, url, author,
                          reactions, responses * 2 if asymmetric else responses, ft, True, text)
            n = _write_topics(conn, sid, extract_topics(text, tags=tags),
                              "hashnode", "expert", src, reactions, responses, True)
            total_s += 1; total_t += n

    # Tag-based queries: public, no auth required
    for slug in HASHNODE_TAGS:
        data = _hn_query(_HN_TAG_GQL, {"slug": slug, "first": 20})
        if data and data.get("tag"):
            process_edges(data["tag"]["posts"]["edges"], f"hashnode/tag/{slug}")
        time.sleep(0.3)

    # Search queries: require Hashnode personal access token (changed ~late 2023)
    # Set HASHNODE_TOKEN env var to enable. Free token at hashnode.com/settings/developer
    if HASHNODE_TOKEN:
        for term in HASHNODE_SEARCH_TERMS:
            data = _hn_query(_HN_SEARCH_GQL, {"query": term, "first": 15}, auth_token=HASHNODE_TOKEN)
            if data:
                edges = (data.get("searchPosts") or {}).get("edges", [])
                process_edges(edges, f"hashnode/search/{term}")
            time.sleep(0.3)
    else:
        print("  [Hashnode] Search queries skipped — set HASHNODE_TOKEN to enable"
              " (free at hashnode.com/settings/developer)")

    conn.commit(); _log(conn, "hashnode", "all", total_s, total_t)
    print(f"  [Hashnode] {total_s} posts -> {total_t} topics")
    return total_s, total_t


# ════════════════════════════════════════════════════════════════════
# COLLECTOR 3: DISCOURSE
# JSON REST — https://docs.discourse.org
# No auth needed for public instances · Append .json to any URL
# ════════════════════════════════════════════════════════════════════

def collect_discourse(conn):
    """
    Public Discourse forum instances for AI/ML communities.

    Dark matter signals:
    - Specialist forums where practitioners discuss problems before solutions
    - Reply-to-view ratio > 5% = community was anticipating this topic
    - First-time posters in niche forums bring external knowledge
    - New terminology appearing = a concept crystallizing in expert minds
    """
    total_s, total_t = 0, 0
    print(f"  [Discourse] {len(DISCOURSE_INSTANCES)} forum instances...")

    for inst in DISCOURSE_INSTANCES:
        base = inst["base_url"].rstrip("/")
        name = inst["name"]
        tier = inst.get("tier", "niche")
        count = 0

        for endpoint, label in [("/latest.json", "latest"), ("/top/weekly.json", "weekly")]:
            r = _http_get(f"{base}{endpoint}")
            if not r: continue
            topics_list = r.json().get("topic_list", {}).get("topics", [])
            for t in topics_list[:40]:
                title   = t.get("title", "")
                tid     = t.get("id")
                slug    = t.get("slug", "")
                url     = f"{base}/t/{slug}/{tid}"
                author  = str(t.get("last_poster_username", "") or "")
                replies = t.get("reply_count", 0)
                views   = t.get("views", 0)
                likes   = t.get("like_count", 0)
                asymmetric = replies / max(views, 1) > 0.05 and views > 15
                ft = _first_timer(conn, author, "discourse", name)
                sid = _id("dc", f"{base}-{tid}-{label}")
                _write_signal(conn, sid, "discourse", tier, f"{name}/{label}",
                              title, url, author, likes,
                              replies * 2 if asymmetric else replies, ft, True, title)
                n = _write_topics(conn, sid, extract_topics(title),
                                  "discourse", tier, f"{name}/{label}",
                                  likes, replies, True)
                total_s += 1; total_t += n; count += 1
            time.sleep(0.3)

        print(f"    {name}: {count} topics")

    conn.commit(); _log(conn, "discourse", "all", total_s, total_t)
    print(f"  [Discourse] {total_s} topics -> {total_t} signals")
    return total_s, total_t


# ════════════════════════════════════════════════════════════════════
# COLLECTOR 4: WORDPRESS.COM
# REST API — https://developer.wordpress.com/docs/api/
# No auth needed for public search
# ════════════════════════════════════════════════════════════════════

def collect_wordpress(conn):
    """
    WordPress.com — searches across millions of independent blogs.

    Dark matter signals:
    - Same concept appearing across INDEPENDENT WordPress blogs =
      strong convergent validation (uncoordinated writers)
    - Mainstream tier — cross-blog convergence confirms what niche sources detected
    """
    BASE = "https://public-api.wordpress.com/rest/v1.2/read/search"
    total_s, total_t = 0, 0
    print(f"  [WordPress] Searching {len(WORDPRESS_TAGS)} topics...")

    for tag in WORDPRESS_TAGS:
        r = _http_get(BASE, params={"q": tag, "sort": "date", "number": 20})
        if not r: time.sleep(0.5); continue
        for post in r.json().get("posts", []):
            title    = post.get("title", "")
            url      = post.get("URL", "")
            author   = (post.get("author") or {}).get("login", "")
            likes    = post.get("like_count", 0)
            comments = post.get("comment_count", 0)
            tags_raw = list((post.get("tags") or {}).keys())
            ft = _first_timer(conn, author, "wordpress", f"wp/{tag}")
            sid = _id("wp", post.get("global_ID", url))
            text = f"{title} {post.get('excerpt', '')}"
            organic = likes > 0 or comments > 0 or len(title) > 10
            _write_signal(conn, sid, "wordpress", "mainstream", f"wordpress/{tag}",
                          title, url, author, likes, comments, ft, organic, text)
            n = _write_topics(conn, sid, extract_topics(text, tags=tags_raw),
                              "wordpress", "mainstream", f"wordpress/{tag}",
                              likes, comments, organic)
            total_s += 1; total_t += n
        time.sleep(0.3)

    conn.commit(); _log(conn, "wordpress", "search", total_s, total_t)
    print(f"  [WordPress] {total_s} posts -> {total_t} topics")
    return total_s, total_t


# ════════════════════════════════════════════════════════════════════
# COLLECTOR 5: BLOGGER (Google Blogger API v3)
# REST API — https://developers.google.com/blogger/docs/3.0
# REQUIRES FREE Google API key (10,000 req/day quota)
# ════════════════════════════════════════════════════════════════════

def collect_blogger(conn):
    """
    Google Blogger — institutional tech blogs (Google AI Blog, etc.).

    Dark matter signals:
    - Google AI Blog publishes on Blogger BEFORE news sites cover announcements
    - New terminology in Blogger posts = concept reaching long-form writers
    - Comments on Blogger = higher-quality engagement than social reactions
    """
    if not BLOGGER_API_KEY:
        print("  [Blogger] SKIPPED — set BLOGGER_API_KEY in .env")
        print("  [Blogger] Free key: console.cloud.google.com -> Blogger API v3")
        return 0, 0

    BASE = "https://www.googleapis.com/blogger/v3"
    KEY  = BLOGGER_API_KEY
    total_s, total_t = 0, 0
    print(f"  [Blogger] {len(BLOGGER_BLOGS)} blogs + search terms...")

    def process_posts(posts, src, tier):
        nonlocal total_s, total_t
        for post in posts:
            title    = post.get("title", "")
            url      = post.get("url", "")
            author   = (post.get("author") or {}).get("displayName", "")
            replies  = post.get("replies", {}).get("totalItems", "0")
            comments = int(replies) if str(replies).isdigit() else 0
            labels   = post.get("labels", [])
            pid      = post.get("id", "")
            ft = _first_timer(conn, author, "blogger", src)
            sid = _id("bl", pid)
            text = f"{title} {post.get('content', '')[:300]}"
            _write_signal(conn, sid, "blogger", tier, src,
                          title, url, author, 0, comments, ft, True, text)
            n = _write_topics(conn, sid, extract_topics(text, tags=labels),
                              "blogger", tier, src, 0, comments, True)
            total_s += 1; total_t += n

    for blog in BLOGGER_BLOGS:
        r = _http_get(f"{BASE}/blogs/{blog['blog_id']}/posts",
                      params={"key": KEY, "maxResults": 20, "status": "live",
                              "orderBy": "published"})
        if r:
            posts = r.json().get("items", [])
            process_posts(posts, f"blogger/{blog['name']}", blog.get("tier", "mainstream"))
            print(f"    {blog['name']}: {len(posts)} posts")
        time.sleep(0.5)

    for blog in BLOGGER_BLOGS[:2]:
        for term in BLOGGER_SEARCH_TERMS[:5]:
            r = _http_get(f"{BASE}/blogs/{blog['blog_id']}/posts/search",
                          params={"key": KEY, "q": term, "maxResults": 10})
            if r:
                process_posts(r.json().get("items", []),
                              f"blogger/{blog['name']}/search",
                              blog.get("tier", "mainstream"))
            time.sleep(0.4)

    conn.commit(); _log(conn, "blogger", "all", total_s, total_t)
    print(f"  [Blogger] {total_s} posts -> {total_t} topics")
    return total_s, total_t


# ════════════════════════════════════════════════════════════════════
# COLLECTOR 6: MEDIUM (RSS feeds per tag)
# No auth needed · RSS: https://medium.com/tag/{tag}/feed
# ════════════════════════════════════════════════════════════════════

def collect_medium(conn):
    """
    AI/tech newsletter RSS feeds — replaces blocked Medium tag feeds.

    Medium's tag RSS (medium.com/tag/*/feed) has been blocked since ~2023.
    This collector now pulls from NEWSLETTER_FEEDS — a curated list of
    AI/tech publication and newsletter RSS feeds that return live content.

    Dark matter signals:
    - Long-form analysis = topic graduated from tweets to serious writing
    - Independent newsletters covering the same NEW concept by DIFFERENT
      authors = "compression artifact" — independent convergence on a shared
      understanding that hasn't yet been publicly crystallized
    - Expert newsletters (Latent Space, The Batch) detect and NAME trends
      weeks before mainstream coverage
    """
    total_s, total_t = 0, 0
    print(f"  [Newsletters/Medium] {len(NEWSLETTER_FEEDS)} feeds...")

    for cfg in NEWSLETTER_FEEDS:
        items = _parse_rss(cfg["url"])
        count = 0
        tier = cfg.get("tier", "mainstream")
        src  = f"newsletter/{cfg['name']}"
        for item in items:
            title  = item["title"]
            url    = item["link"]
            author = item["author"] or cfg["name"]
            tags   = item["tags"]
            if not title: continue
            quality = min(80, len(item.get("summary", "")) // 10)
            ft = _first_timer(conn, author, "medium", src)
            sid = _id("med", url or title)
            text = f"{title} {item.get('summary', '')[:300]}"
            _write_signal(conn, sid, "medium", tier, src,
                          title, url, author, quality, 0, ft, True, text)
            n = _write_topics(conn, sid, extract_topics(text, tags=tags),
                              "medium", tier, src, quality, 0, True)
            total_s += 1; total_t += n; count += 1
        if count:
            print(f"    {cfg['name']}: {count} articles")
        time.sleep(0.4)

    conn.commit(); _log(conn, "medium", "rss", total_s, total_t)
    print(f"  [Newsletters/Medium] {total_s} articles -> {total_t} topics")
    return total_s, total_t


# ════════════════════════════════════════════════════════════════════
# COLLECTOR 7: GHOST BLOGS (RSS feeds)
# No auth needed · Standard RSS at {blog}/rss or /feed
# ════════════════════════════════════════════════════════════════════

def collect_ghost(conn):
    """
    Major Ghost-powered AI/tech expert blogs via RSS.

    Dark matter signals:
    - Expert newsletters (Import AI, The Gradient, Ahead of AI)
      detect and name trends WEEKS before mainstream coverage
    - When a NEW TERM appears in one of these expert blogs, it signals
      the concept has been validated by someone tracking the field daily
    - "Expert" tier: highest source quality in the system
    """
    total_s, total_t = 0, 0
    print(f"  [Ghost RSS] {len(GHOST_FEEDS)} expert blog feeds...")

    for cfg in GHOST_FEEDS:
        items = _parse_rss(cfg["url"])
        count = 0
        for item in items:
            title  = item["title"]
            link   = item["link"]
            author = item["author"] or cfg["name"]
            tags   = item["tags"]
            if not title: continue
            tier = cfg.get("tier", "expert")
            ft = _first_timer(conn, author, "ghost", cfg["name"])
            sid = _id("ghost", link or title)
            text = f"{title} {item.get('summary', '')[:300]}"
            _write_signal(conn, sid, "ghost", tier, cfg["name"],
                          title, link, author, 60, 0, ft, True, text)
            n = _write_topics(conn, sid, extract_topics(text, tags=tags),
                              "ghost", tier, cfg["name"], 60, 0, True)
            total_s += 1; total_t += n; count += 1
        print(f"    {cfg['name']}: {count} articles")
        time.sleep(0.4)

    conn.commit(); _log(conn, "ghost", "rss", total_s, total_t)
    print(f"  [Ghost] {total_s} articles -> {total_t} topics")
    return total_s, total_t


# ════════════════════════════════════════════════════════════════════
# MASTER ORCHESTRATOR
# ════════════════════════════════════════════════════════════════════

COLLECTORS = {
    "devto":     ("DEV.to (Forem API)",   "expert",     collect_devto),
    "hashnode":  ("Hashnode (GraphQL)",   "expert",     collect_hashnode),
    "discourse": ("Discourse Forums",     "niche",      collect_discourse),
    "wordpress": ("WordPress.com REST",   "mainstream", collect_wordpress),
    "blogger":   ("Blogger API v3",       "mainstream", collect_blogger),
    "medium":    ("Medium RSS",           "mainstream", collect_medium),
    "ghost":     ("Ghost Blog RSS",       "expert",     collect_ghost),
}

BLOG_PLATFORM_NAMES = set(COLLECTORS.keys())


def collect_all_blogs(conn=None, skip=None):
    """
    Run all blog collectors using the provided connection (or create one).
    Returns a summary dict with per-platform signal/topic counts.
    """
    skip = skip or []
    close_conn = False
    if conn is None:
        conn = get_conn()
        close_conn = True

    results = {}
    grand_s = grand_t = 0
    order = ["devto", "hashnode", "discourse", "wordpress", "blogger", "medium", "ghost"]

    for key in order:
        if key in skip:
            continue
        name, tier, fn = COLLECTORS[key]
        print(f"  [{key}] collecting...")
        try:
            s, t = fn(conn)
            results[key] = {"signals": s, "topics": t}
            grand_s += s; grand_t += t
        except Exception as e:
            print(f"  ERROR in {name}: {e}")
            results[key] = {"signals": 0, "topics": 0, "error": str(e)}

    if close_conn:
        conn.close()

    results["_total"] = {"signals": grand_s, "topics": grand_t}
    return results


def collect_all(skip=None):
    """Legacy CLI entry point — creates its own connection."""
    skip = skip or []
    print("\n" + "=" * 62)
    print("BLOG COMMUNITY DARK MATTER COLLECTION")
    print(f"Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("-" * 62)
    for key, (name, tier, _) in COLLECTORS.items():
        auth    = "Free Google API key" if key == "blogger" else "None"
        skipped = " [SKIP]" if key in skip else ""
        print(f"  {name:22} {tier:12} {auth}{skipped}")
    print("=" * 62)

    results = collect_all_blogs(skip=skip)
    grand = results.get("_total", {})

    print("\n" + "=" * 62)
    print(f"DONE: {grand.get('signals',0)} signals, {grand.get('topics',0)} topic extractions")
    print("Next: python gravitational_anomaly_detector.py --mode=score")
    print("or:   curl -X POST http://localhost:8000/score-all")
    print("=" * 62)
    return results


def show_stats():
    """Print dark matter contribution stats per blog platform."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT platform,
               COUNT(*) signals,
               COUNT(DISTINCT topic_key) unique_topics,
               SUM(is_first_timer) first_timers,
               AVG(engagement_raw) avg_eng,
               SUM(CASE WHEN comments > upvotes*0.3 AND upvotes > 3 THEN 1 ELSE 0 END) asymmetric
        FROM topic_signals
        WHERE platform IN ('devto','hashnode','discourse','wordpress','blogger','medium','ghost')
        GROUP BY platform ORDER BY signals DESC
    """).fetchall()
    conn.close()

    print(f"\n{'Platform':15} {'Signals':>8} {'Topics':>8} "
          f"{'1st-Timer%':>11} {'Asymmetric':>11} {'Avg Eng':>8}")
    print("-" * 65)
    for r in rows:
        ft = r["first_timers"] / max(r["signals"], 1)
        print(f"{r['platform']:15} {r['signals']:>8} {r['unique_topics']:>8} "
              f"{ft:>10.1%}  {r['asymmetric']:>10} {r['avg_eng']:>8.2f}")

    print("\nKey:")
    print("  1st-Timer%   % of signal mentions by authors new to that community")
    print("  Asymmetric   Posts where comments > upvotes x 0.30 (deep engagement)")
    print("  Avg Eng      Log-scale engagement score (combined upvotes + comments)")


def main():
    p = argparse.ArgumentParser(
        description="Now TrendIn Blog Community Dark Matter Collectors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python blog_collectors.py --mode=collect
  python blog_collectors.py --mode=collect --skip blogger,wordpress
  python blog_collectors.py --mode=devto
  python blog_collectors.py --mode=stats
        """)
    p.add_argument("--mode",
        choices=["collect", "devto", "hashnode", "discourse",
                 "wordpress", "blogger", "medium", "ghost", "stats"],
        default="collect")
    p.add_argument("--skip", default="",
        help="Comma-separated platforms to skip, e.g. 'blogger,medium'")
    args = p.parse_args()
    skip = [s.strip() for s in args.skip.split(",") if s.strip()]

    if args.mode == "collect":
        collect_all(skip=skip)
    elif args.mode in COLLECTORS:
        conn = get_conn()
        _, _, fn = COLLECTORS[args.mode]
        s, t = fn(conn)
        conn.close()
        print(f"\nDone: {s} signals, {t} topics extracted")
    elif args.mode == "stats":
        show_stats()


if __name__ == "__main__":
    main()
