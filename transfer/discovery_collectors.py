"""
================================================================
NOW TRENDIN — OPEN-WORLD DISCOVERY COLLECTORS  (Phase A)
================================================================

WHY THIS EXISTS:
  Every other collector in the system is seeded toward AI/dev/tech
  (DEV.to AI tags, HuggingFace forums, AI newsletters, GitHub, HN).
  As a result the engine is blind to general-culture trends — the
  FIFA World Cup, a breakout athlete, a viral film — because that
  content is never ingested, and even when it is (via news) it gets
  shredded into low-salience n-grams by the tech-biased extractor.

WHAT THIS DOES:
  Pulls CATEGORY-AGNOSTIC "what is trending right NOW" feeds that are
  not keyed off any seed list:

    1. Google Trends — Daily Trending Searches (RSS, free, no key)
       → the single highest-ROI discovery feed. Returns the actual
         rising search terms with approx traffic + related headlines.
    2. Wikipedia — top pageviews yesterday (REST API, free, no key)
       → a breakout-ENTITY detector across every subject on earth.

KEY DESIGN — TRUST THE SOURCE ENTITY:
  These feeds give us a PRE-RESOLVED entity ("FIFA World Cup" as one
  string). We store that string directly as the canonical topic
  instead of running it through extract_topics_from_text() — which
  would fragment "FIFA World Cup 2026" into "2026 kicks off", "fifa
  world", etc. This is a deliberate mini entity-resolution step that
  pre-empts the Phase-B NER work for discovery items.

INTEGRITY (per project standard):
  - Sources are reputable + free + category-neutral (no tech bias).
  - This collector only WRITES raw_signals / topic_signals (the same
    objective intake every other collector uses). It does NOT touch
    the Gradient Score math — scoring stays downstream and unchanged.
  - No circular metrics: these are external attention signals,
    independent of anything the engine itself produces.

INTEGRATION:
  Self-contained, mirrors blog_collectors.py. The host detector calls
  collect_all_discovery(conn). Tables are created by the main detector;
  every insert is INSERT OR IGNORE so this is safe to run on top.
================================================================
"""

import os
import re
import time
import math
import hashlib
import sqlite3
from datetime import datetime, timezone, timedelta

try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    _HAS_REQUESTS = False

try:
    import xml.etree.ElementTree as ET
except Exception:
    ET = None


# ── Helpers ────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _topic_key(topic: str) -> str:
    """Normalize a topic to a grouping key (matches the host engine)."""
    key = topic.lower().strip()
    key = re.sub(r'[^\w\s]', '', key)
    key = re.sub(r'\s+', '_', key)
    return key[:80]


def _parse_traffic(s: str) -> int:
    """'200K+' -> 200000, '1M+' -> 1000000, '5,000+' -> 5000."""
    if not s:
        return 0
    s = s.strip().upper().replace("+", "").replace(",", "").strip()
    mult = 1
    if s.endswith("K"):
        mult, s = 1_000, s[:-1]
    elif s.endswith("M"):
        mult, s = 1_000_000, s[:-1]
    try:
        return int(float(s) * mult)
    except ValueError:
        return 0


def _write_signal(conn, *, sig_id, platform, tier, source, title, url,
                  engagement, sentiment=0.0, upvotes=0, comments=0,
                  raw_text=None):
    conn.execute(
        "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (sig_id, _now(), platform, tier, source, title[:500], url, "",
         upvotes, comments, round(engagement, 4), round(sentiment, 4),
         0, 1, (raw_text or title)[:500]),
    )


def _write_topic(conn, *, sig_id, topic, platform, tier, source,
                 engagement, upvotes=0, comments=0):
    t_key = _topic_key(topic)
    if len(t_key) < 3:
        return 0
    t_id = hashlib.md5(f"{sig_id}-{t_key}".encode()).hexdigest()[:16]
    conn.execute(
        "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (t_id, _now(), topic[:120], t_key, sig_id, platform, tier, source,
         upvotes, comments, round(engagement, 4), 0, 1),
    )
    return 1


# ── 1. Google Trends — Daily Trending Searches (RSS) ───────────────

# Trending-now RSS (no API key). Google moved this off the legacy
# /trends/trendingsearches/daily/rss path (now 404) to /trending/rss.
_GT_RSS = "https://trends.google.com/trending/rss?geo={geo}"
_GT_NS = {"ht": "https://trends.google.com/trending/trendingsearches/daily"}


def collect_google_trends_hot(conn, geo: str = "US") -> int:
    """The actual rising search terms right now — fully category-agnostic."""
    if not (_HAS_REQUESTS and ET):
        print("  [discovery] google_trends_hot skipped (missing deps)")
        return 0
    platform, tier, source = "google_trends_hot", "mainstream", f"daily_{geo}"
    written = 0
    try:
        r = requests.get(_GT_RSS.format(geo=geo), timeout=12,
                         headers={"User-Agent": "NowTrendIn/2.0 (+discovery)"})
        if r.status_code != 200:
            print(f"  [discovery] google_trends_hot HTTP {r.status_code}")
            return 0
        root = ET.fromstring(r.content)
        for item in root.iter("item"):
            term = (item.findtext("title") or "").strip()
            if len(term) < 3:
                continue
            traffic = _parse_traffic(item.findtext("ht:approx_traffic", default="",
                                                    namespaces=_GT_NS))
            # engagement from approx traffic (log-scaled, like other collectors)
            engagement = math.log1p(max(traffic, 1))
            sig_id = hashlib.md5(f"gth-{geo}-{term}".encode()).hexdigest()[:16]
            url = f"https://www.google.com/search?q={term.replace(' ', '+')}"
            _write_signal(conn, sig_id=sig_id, platform=platform, tier=tier,
                          source=source, title=term, url=url,
                          engagement=engagement, upvotes=traffic)
            # TRUST THE SOURCE ENTITY — store the trending term verbatim.
            written += _write_topic(conn, sig_id=sig_id, topic=term,
                                    platform=platform, tier=tier, source=source,
                                    engagement=engagement, upvotes=traffic)
            # Also capture related-news entities (they sharpen the topic cluster)
            for ni in item.findall("ht:news_item", _GT_NS):
                headline = (ni.findtext("ht:news_item_title", default="",
                                        namespaces=_GT_NS) or "").strip()
                if 6 <= len(headline) <= 140:
                    written += _write_topic(conn, sig_id=sig_id, topic=headline,
                                            platform=platform, tier=tier,
                                            source=source, engagement=engagement)
        conn.commit()
    except Exception as e:
        print(f"  [discovery] google_trends_hot error: {e}")
    print(f"  [discovery] google_trends_hot: {written} topic signals")
    return written


# ── 2. Wikipedia — top pageviews yesterday ─────────────────────────

_WIKI_TOP = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/top/"
             "en.wikipedia/all-access/{y}/{m}/{d}")
# Skip MediaWiki namespaces, the main page, bare numbers, and TLD stubs (.xyz).
_WIKI_NS = ("Special:", "Wikipedia:", "Portal:", "Help:", "Category:",
            "Template:", "File:", "Talk:", "Draft:")


def _wiki_skip(article: str) -> bool:
    if not article or article == "Main_Page" or article == "-":
        return True
    if article.startswith(_WIKI_NS) or article.startswith("."):
        return True
    if re.fullmatch(r"\d+", article):
        return True
    return False


def collect_wikipedia_hot(conn, top_n: int = 120) -> int:
    """Top Wikipedia articles by views yesterday — breakout entity detector."""
    if not _HAS_REQUESTS:
        return 0
    platform, tier, source = "wikipedia_hot", "mainstream", "top_pageviews"
    written = 0
    y = datetime.now(timezone.utc) - timedelta(days=1)
    url = _WIKI_TOP.format(y=y.year, m=f"{y.month:02d}", d=f"{y.day:02d}")
    try:
        r = requests.get(url, timeout=12,
                         headers={"User-Agent": "NowTrendIn/2.0 (+discovery)"})
        if r.status_code != 200:
            print(f"  [discovery] wikipedia_hot HTTP {r.status_code}")
            return 0
        articles = (r.json().get("items") or [{}])[0].get("articles", [])
        for a in articles[:top_n]:
            raw = a.get("article", "")
            if _wiki_skip(raw):
                continue
            entity = raw.replace("_", " ").strip()
            if len(entity) < 3:
                continue
            views = int(a.get("views", 0))
            engagement = math.log1p(max(views, 1))
            sig_id = hashlib.md5(f"wiki-{raw}".encode()).hexdigest()[:16]
            page = f"https://en.wikipedia.org/wiki/{raw}"
            _write_signal(conn, sig_id=sig_id, platform=platform, tier=tier,
                          source=source, title=entity, url=page,
                          engagement=engagement, upvotes=views)
            written += _write_topic(conn, sig_id=sig_id, topic=entity,
                                    platform=platform, tier=tier, source=source,
                                    engagement=engagement, upvotes=views)
        conn.commit()
    except Exception as e:
        print(f"  [discovery] wikipedia_hot error: {e}")
    print(f"  [discovery] wikipedia_hot: {written} topic signals")
    return written


# ── 3. Firecrawl — Web Search Discovery (credit-budgeted, 6h rotation) ──
#
# Budget math: 1 search/cycle × 4 cycles/day × 31 days × 2 credits = 248/month
# (free tier = 500 credits/month — leaves 252 buffer for AI grade calls)
#
# 5 category queries rotate on (hour // 6) % 5 so every dimension gets
# fresh coverage each week without exceeding 1 call per cycle.

_FC_ENDPOINT = "https://api.firecrawl.dev/v2/search"
_FC_QUERIES = [
    "latest breakthrough AI technology emerging trend 2026",
    "trending finance crypto market movement 2026",
    "new health biotech science discovery 2026",
    "viral culture entertainment sports trend 2026",
    "growing startup business economy trend 2026",
]


def collect_firecrawl_discovery(conn) -> int:
    """1 rotating category search per 6h cycle = 2 credits = 248 credits/month."""
    if not _HAS_REQUESTS:
        return 0
    api_key = os.getenv("FIRECRAWL_API_KEY", "")
    if not api_key:
        print("  [discovery] firecrawl_web skipped (no FIRECRAWL_API_KEY)")
        return 0

    hour = datetime.now(timezone.utc).hour
    query_idx = (hour // 6) % len(_FC_QUERIES)
    query = _FC_QUERIES[query_idx]
    platform, tier, source = "firecrawl_web", "niche", f"search_q{query_idx}"

    written = 0
    try:
        r = requests.post(
            _FC_ENDPOINT,
            headers={"Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"},
            json={"query": query, "limit": 5},
            timeout=20,
        )
        if r.status_code != 200:
            print(f"  [discovery] firecrawl_web HTTP {r.status_code}: {r.text[:200]}")
            return 0
        body = r.json()
        # Response: {"success": true, "data": {"web": [...]}, "creditsUsed": N}
        results = (body.get("data") or {}).get("web") or []
        credits_used = int(body.get("creditsUsed") or 0)

        for item in results:
            title = (item.get("title") or item.get("url") or "").strip()
            url = (item.get("url") or "").strip()
            if len(title) < 4 or not url:
                continue
            desc = (item.get("description") or "").strip()
            raw_text = f"{title}. {desc}" if desc else title
            sig_id = hashlib.md5(f"fc-{url}".encode()).hexdigest()[:16]
            # Firecrawl returns no engagement count; use a uniform non-zero baseline
            engagement = math.log1p(5)
            _write_signal(conn, sig_id=sig_id, platform=platform, tier=tier,
                          source=source, title=title, url=url,
                          engagement=engagement, raw_text=raw_text[:500])
            written += _write_topic(conn, sig_id=sig_id, topic=title,
                                    platform=platform, tier=tier, source=source,
                                    engagement=engagement)
        conn.commit()
        print(f"  [discovery] firecrawl_web: {written} topic signals "
              f"({credits_used} credits used, query_idx={query_idx})")
    except Exception as e:
        print(f"  [discovery] firecrawl_web error: {e}")
    return written


# ── Google Custom Search JSON API (web-index search; NOT Google Trends) ──────
# Searches Google's WEB INDEX for emerging-topic content — a web-presence signal,
# complementary to firecrawl_web. NOTE: this is the *web search* JSON API, which is
# different from Google TRENDS (handled free above by collect_google_trends_hot) and
# from the embeddable Programmable Search *Element* (a JS widget, not a data API).
# DORMANT until CUSTOM_SEARCH_CX is set: it needs (1) the Custom Search API enabled in
# the Cloud project and (2) a Programmable Search Engine (programmablesearchengine.
# google.com) configured to "Search the entire web" → its Search-engine ID (cx).
# Quota: 100 queries/day FREE. 1 rotating query per 6h cycle = 4/day, well within it.
_CS_ENDPOINT = "https://www.googleapis.com/customsearch/v1"
_CS_QUERIES = [
    "emerging AI technology breakthrough",
    "trending finance crypto market shift",
    "new biotech health science discovery",
    "viral culture entertainment sports moment",
    "fast growing startup business trend",
]


def collect_google_search_discovery(conn) -> int:
    """Google Custom Search JSON API web-search discovery. Returns 0 (skips) until
    CUSTOM_SEARCH_CX + CUSTOM_SEARCH_API_KEY are set."""
    if not _HAS_REQUESTS:
        return 0
    cx = os.getenv("CUSTOM_SEARCH_CX", "")
    api_key = os.getenv("CUSTOM_SEARCH_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
    if not cx or not api_key:
        print("  [discovery] google_search skipped "
              "(set CUSTOM_SEARCH_CX + CUSTOM_SEARCH_API_KEY to enable)")
        return 0

    hour = datetime.now(timezone.utc).hour
    query_idx = (hour // 6) % len(_CS_QUERIES)
    query = _CS_QUERIES[query_idx]
    platform, tier, source = "google_web", "niche", f"cse_q{query_idx}"

    written = 0
    try:
        r = requests.get(_CS_ENDPOINT, params={
            "key": api_key, "cx": cx, "q": query,
            "num": 10, "dateRestrict": "d7", "safe": "off",
        }, timeout=20)
        if r.status_code != 200:
            print(f"  [discovery] google_search HTTP {r.status_code}: {r.text[:200]}")
            return 0
        for item in (r.json().get("items") or []):
            title = (item.get("title") or "").strip()
            url = (item.get("link") or "").strip()
            if len(title) < 4 or not url:
                continue
            snippet = (item.get("snippet") or "").strip()
            raw_text = f"{title}. {snippet}" if snippet else title
            sig_id = hashlib.md5(f"cse-{url}".encode()).hexdigest()[:16]
            engagement = math.log1p(5)   # no engagement count from web search
            _write_signal(conn, sig_id=sig_id, platform=platform, tier=tier,
                          source=source, title=title, url=url,
                          engagement=engagement, raw_text=raw_text[:500])
            written += _write_topic(conn, sig_id=sig_id, topic=title,
                                    platform=platform, tier=tier, source=source,
                                    engagement=engagement)
        conn.commit()
        print(f"  [discovery] google_search: {written} topic signals (query_idx={query_idx})")
    except Exception as e:
        print(f"  [discovery] google_search error: {e}")
    return written


# ── Orchestrator ───────────────────────────────────────────────────

def collect_all_discovery(conn, geos=("US",)) -> dict:
    """Run every open-world discovery collector. Returns per-source counts."""
    out = {}
    for geo in geos:
        out[f"google_trends_hot:{geo}"] = collect_google_trends_hot(conn, geo)
    out["wikipedia_hot"] = collect_wikipedia_hot(conn)
    out["firecrawl_web"] = collect_firecrawl_discovery(conn)
    out["google_web"] = collect_google_search_discovery(conn)
    out["_total"] = sum(v for v in out.values() if isinstance(v, int))
    print(f"  [discovery] TOTAL: {out['_total']} topic signals")
    return out


if __name__ == "__main__":
    # Local smoke test against a throwaway DB.
    db = os.getenv("DISCOVERY_TEST_DB", ":memory:")
    c = sqlite3.connect(db)
    c.executescript("""
      CREATE TABLE IF NOT EXISTS raw_signals (
        id TEXT PRIMARY KEY, collected_at TEXT, platform TEXT, platform_tier TEXT,
        source_name TEXT, title TEXT, url TEXT, author TEXT, upvotes INTEGER,
        comments INTEGER, engagement_raw REAL, sentiment REAL,
        is_first_timer INTEGER, is_organic INTEGER, raw_text TEXT);
      CREATE TABLE IF NOT EXISTS topic_signals (
        id TEXT PRIMARY KEY, extracted_at TEXT, topic TEXT, topic_key TEXT,
        signal_id TEXT, platform TEXT, platform_tier TEXT, source_name TEXT,
        upvotes INTEGER, comments INTEGER, engagement_raw REAL,
        is_first_timer INTEGER, is_organic INTEGER);
    """)
    res = collect_all_discovery(c)
    print("\nRESULT:", res)
    rows = c.execute("SELECT topic, platform, upvotes FROM topic_signals "
                     "ORDER BY upvotes DESC LIMIT 30").fetchall()
    print("\nTop discovered topics:")
    for t, p, u in rows:
        print(f"  {u:>10,}  [{p}]  {t}")
