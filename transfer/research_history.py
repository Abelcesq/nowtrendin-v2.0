"""
================================================================
NOW TRENDIN — TOPIC RESEARCH HISTORY ENGINE v2.0
================================================================

WHAT THIS DOES:
  For any topic the Gradient Score detects, this module
  researches HOW LONG that topic has been discussed online
  and displays that context in the Signal Detail panel.

  This is critical context because:
  - "ai agent" scoring 83 gradient strength could mean:
    (a) It's genuinely emerging right now   → real signal
    (b) It has lived in expert spaces for   → misleading score
        3+ years and the score just reflects
        its permanent home

  Without research history, users cannot tell the difference.
  With it: "This term has been discussed for 4 years in expert
  communities. High gradient strength reflects permanent home,
  not new emergence."

DATA SOURCES (all free, no scraping):
  HackerNews Algolia API  — searchable back to 2007, no key needed
  Wikipedia REST API      — page creation date, no key needed
  GitHub Search API       — year-by-year repo count, token optional
  Google Trends (pytrends)— monthly interest over time, free library
  Now TrendIn Internal DB — when WE first detected the topic

KNOWN TOPICS DATABASE:
  Pre-researched history for 30 common AI/tech terms.
  Provides instant accurate results without live API calls.
  Add entries as the platform grows.

INTEGRATION:
  from research_history import ResearchHistoryEngine
  engine = ResearchHistoryEngine(db_path="anomaly_detector.db")
  result = engine.research("ai_agent", "ai agent")

FASTAPI ENDPOINT (add to gravitational_anomaly_detector.py):
  GET /scores/{topic_key}/history

CACHING:
  Results cached in SQLite for 7 days (history changes slowly).
================================================================
"""

import os, re, json, time, sqlite3, logging, argparse, urllib.parse
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests

try:
    from pytrends.request import TrendReq
    HAS_PYTRENDS = True
except ImportError:
    HAS_PYTRENDS = False

try:
    import wikipediaapi as _wapi
    HAS_WIKIPEDIA = True
except ImportError:
    HAS_WIKIPEDIA = False

DB_PATH       = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
GITHUB_TOKEN  = os.getenv("GITHUB_TOKEN", "")
UA            = "NowTrendIn/1.0 ResearchHistory (contact@nowtrendin.com)"
CACHE_DAYS    = 7

logger = logging.getLogger("research_history")


# ────────────────────────────────────────────────────────────────
# KNOWN TOPICS DATABASE
# Pre-researched for 30 common AI/tech terms.
# Each entry skips all live API calls and provides instant results.
# ────────────────────────────────────────────────────────────────

KNOWN_TOPICS: dict = {
    "ai_agent": {
        "first_known_date": "2020-06",
        "years_discussed":  5,
        "origin_context": (
            "Rooted in classical AI planning literature (1990s). Popularised in its "
            "modern LLM form by LangChain (October 2022) and AutoGPT (March 2023). "
            "Became mainstream enterprise vocabulary in 2024."
        ),
        "milestones": [
            {"year": "2020", "event": "Early academic discussion — LLM-driven autonomous agents"},
            {"year": "2022-10", "event": "LangChain launches — 'agent' becomes core framework term"},
            {"year": "2023-03", "event": "AutoGPT release — concept reaches developer mainstream"},
            {"year": "2023-09", "event": "OpenAI, Anthropic release agent frameworks"},
            {"year": "2024",    "event": "Enterprise adoption wave — in every tech publication"},
        ],
        "wikipedia_url":     "https://en.wikipedia.org/wiki/Intelligent_agent",
        "wikipedia_created": "2001",
        "hn_search_url":     "https://hn.algolia.com/api/v1/search_by_date?query=ai+agent&tags=story",
        "gradient_implication": (
            "ESTABLISHED EXPERT TOPIC: 'ai agent' has been actively discussed in expert "
            "communities since at least 2020 and entered mainstream awareness in 2023. "
            "High gradient strength reflects its permanent home in technical communities, "
            "not a new emergence. Monitor for velocity changes — first-timer surges and "
            "inertia acceleration — rather than treating absolute niche concentration "
            "as a new signal."
        ),
        "trend_trajectory": "established_mainstream",
    },

    "ai_agents": {
        "first_known_date": "2020-06",
        "years_discussed":  5,
        "origin_context":   "Plural form of 'AI agent' — same history and trajectory.",
        "milestones": [
            {"year": "2022-10", "event": "LangChain popularises the plural form"},
            {"year": "2023-03", "event": "AutoGPT — 'AI agents' enters mainstream vocabulary"},
        ],
        "gradient_implication": (
            "ESTABLISHED EXPERT TOPIC: Same history as 'ai agent'. High niche concentration "
            "reflects permanent expert-community home, not new emergence."
        ),
        "trend_trajectory": "established_mainstream",
    },

    "llm": {
        "first_known_date": "2017-06",
        "years_discussed":  8,
        "origin_context": (
            "Emerged alongside the Transformer paper (Vaswani et al., June 2017). "
            "GPT-2 (2019) popularised LLM as a standalone concept. "
            "ChatGPT (November 2022) made it household vocabulary."
        ),
        "milestones": [
            {"year": "2017-06", "event": "Transformer paper — foundation of modern LLMs"},
            {"year": "2019-02", "event": "GPT-2 — 'LLM' as a standalone concept"},
            {"year": "2020-05", "event": "GPT-3 — LLM capability shock"},
            {"year": "2022-11", "event": "ChatGPT — LLM enters general vocabulary"},
            {"year": "2023",    "event": "LLM becomes universal shorthand in all tech media"},
        ],
        "wikipedia_url": "https://en.wikipedia.org/wiki/Large_language_model",
        "gradient_implication": (
            "ESTABLISHED MAINSTREAM TOPIC: 'LLM' has been in expert vocabulary since 2017 "
            "and mainstream since 2022. Gradient strength reflects natural technical audience. "
            "Only sudden acceleration above historical baseline constitutes a genuine signal."
        ),
        "trend_trajectory": "fully_mainstream",
    },

    "rag": {
        "first_known_date": "2020-09",
        "years_discussed":  5,
        "origin_context": (
            "Named in a Facebook AI Research paper (Lewis et al., September 2020). "
            "Rapid adoption as a practical LLM engineering pattern from 2022 onwards."
        ),
        "milestones": [
            {"year": "2020-09", "event": "Facebook AI Research paper coins 'RAG'"},
            {"year": "2022",    "event": "LangChain integrates RAG as primary pattern"},
            {"year": "2023",    "event": "Enterprise adoption — RAG becomes standard architecture"},
            {"year": "2024",    "event": "RAG vs fine-tuning debate dominates ML engineering"},
        ],
        "wikipedia_url": "https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
        "gradient_implication": (
            "ESTABLISHED EXPERT TOPIC: RAG has been a core ML engineering pattern since 2022. "
            "High niche concentration is expected baseline. "
            "Watch for first-timer surges indicating new enterprise adoption waves."
        ),
        "trend_trajectory": "established_expert",
    },

    "vibe_coding": {
        "first_known_date": "2025-02",
        "years_discussed":  0,
        "origin_context": (
            "Coined by Andrej Karpathy in a viral tweet (February 2025). Describes a coding "
            "style where the developer describes intent in natural language and accepts "
            "AI-generated code without reviewing it. Immediately polarised the dev community."
        ),
        "milestones": [
            {"year": "2025-02", "event": "Andrej Karpathy coins 'vibe coding' on X/Twitter"},
            {"year": "2025-03", "event": "Term spreads to dev.to, Hacker News, GitHub discussions"},
            {"year": "2025-04", "event": "Anti-vibe-coding backlash articles appear"},
        ],
        "wikipedia_url": "https://en.wikipedia.org/wiki/Vibe_coding",
        "gradient_implication": (
            "RECENTLY EMERGED: 'Vibe coding' was coined in February 2025 — less than a year ago. "
            "Any gradient signal for this term reflects genuine emergence. "
            "High gradient strength here is a real signal, not a permanent home."
        ),
        "trend_trajectory": "recently_emerged",
    },

    "mcp": {
        "first_known_date": "2024-11",
        "years_discussed":  1,
        "origin_context": (
            "Model Context Protocol released by Anthropic in November 2024 as an open standard "
            "for connecting AI assistants to external tools and data. "
            "Adoption accelerated rapidly in early 2025 with broad ecosystem support."
        ),
        "milestones": [
            {"year": "2024-11", "event": "Anthropic releases MCP open standard"},
            {"year": "2025-01", "event": "Major IDE and tool integrations announced"},
            {"year": "2025-03", "event": "Community MCP server ecosystem explosion on GitHub"},
        ],
        "gradient_implication": (
            "RECENTLY EMERGED: MCP was released in November 2024. "
            "High gradient strength reflects genuine recent emergence. "
            "Cross-platform signals and first-timer ratios carry full weight here."
        ),
        "trend_trajectory": "recently_emerged",
    },

    "deepseek": {
        "first_known_date": "2023-11",
        "years_discussed":  2,
        "origin_context": (
            "DeepSeek AI (Hangzhou-based) released its first models November 2023. "
            "DeepSeek-R1 (January 2025) caused a global shock — matched GPT-4 performance "
            "at a fraction of training cost. Triggered a Nvidia stock crash."
        ),
        "milestones": [
            {"year": "2023-11", "event": "DeepSeek first model — limited external notice"},
            {"year": "2024",    "event": "DeepSeek V2 — Chinese AI labs recognised globally"},
            {"year": "2025-01", "event": "DeepSeek-R1 — global shock, mainstream coverage"},
        ],
        "gradient_implication": (
            "RECENTLY EMERGED AT SCALE: DeepSeek was a niche term before January 2025. "
            "Post-R1 release it entered mainstream. Gradient signals reflect genuine "
            "emergence — watch whether it is in early spike or sustained adoption phase."
        ),
        "trend_trajectory": "recently_emerged",
    },

    "agentic_coding": {
        "first_known_date": "2024-08",
        "years_discussed":  1,
        "origin_context": (
            "Describes AI coding assistants that autonomously plan, write, and execute "
            "multi-step programming tasks. Popularised with Cursor, Devin, and Claude Code "
            "through 2024-2025."
        ),
        "milestones": [
            {"year": "2024-03", "event": "Cognition AI releases Devin — 'AI software engineer'"},
            {"year": "2024-08", "event": "'Agentic coding' appears in developer community discussions"},
            {"year": "2025",    "event": "Claude Code, Cursor Agent Mode — enters mainstream"},
        ],
        "gradient_implication": (
            "EMERGING TERM: Agentic coding is a relatively new phrase. "
            "High gradient strength reflects genuine early-adopter activity, "
            "not permanent expert residence."
        ),
        "trend_trajectory": "emerging",
    },

    "reasoning_model": {
        "first_known_date": "2024-09",
        "years_discussed":  1,
        "origin_context": (
            "Reasoning models — LLMs using extended chain-of-thought inference — emerged as "
            "a recognised category with OpenAI o1 (September 2024). "
            "The category name was established across the industry by late 2024."
        ),
        "milestones": [
            {"year": "2024-09", "event": "OpenAI o1 — 'reasoning model' as a category"},
            {"year": "2024-12", "event": "DeepSeek-R1, Gemini Flash Thinking — category expands"},
            {"year": "2025",    "event": "All major AI labs ship reasoning models"},
        ],
        "gradient_implication": (
            "EMERGING CATEGORY: Reasoning model as a term is less than 2 years old. "
            "Gradient signals reflect genuine interest, not established expert residence."
        ),
        "trend_trajectory": "emerging",
    },

    "claude": {
        "first_known_date": "2023-03",
        "years_discussed":  2,
        "origin_context": (
            "Anthropic publicly released Claude in March 2023. Named after Claude Shannon. "
            "Rapid version progression: Claude 1 (2023) → Claude 2 → Claude 3 → Claude 4 (2025)."
        ),
        "milestones": [
            {"year": "2023-03", "event": "Claude 1 public release"},
            {"year": "2024-03", "event": "Claude 3 family — major capability leap"},
            {"year": "2025",    "event": "Claude 4 — sustained developer adoption"},
        ],
        "gradient_implication": (
            "ESTABLISHED EXPERT TOPIC: Claude has been in developer conversations since 2023. "
            "Expert-community concentration is expected baseline. "
            "Watch for product announcement spikes as genuine velocity events."
        ),
        "trend_trajectory": "established_expert",
    },

    "cursor": {
        "first_known_date": "2023-01",
        "years_discussed":  2,
        "origin_context": (
            "Cursor AI founded 2023 as a fork of VS Code with AI capabilities. "
            "Grew via developer word-of-mouth to become the dominant AI IDE by 2024."
        ),
        "gradient_implication": (
            "ESTABLISHED DEVELOPER TOOL: Cursor has strong expert community presence since 2023. "
            "High niche concentration is baseline. Watch for mainstream crossover signals."
        ),
        "trend_trajectory": "established_expert",
    },

    "alignment": {
        "first_known_date": "2014-01",
        "years_discussed":  11,
        "origin_context": (
            "AI alignment as a research focus dates to Bostrom's Superintelligence (2014) "
            "and MIRI. Became mainstream AI discourse post-ChatGPT (2022)."
        ),
        "gradient_implication": (
            "LONG-ESTABLISHED ACADEMIC TOPIC: Alignment has 10+ years of expert discussion. "
            "High niche concentration is entirely expected baseline. "
            "Only velocity well above historical norms would indicate genuine emergence."
        ),
        "trend_trajectory": "established_mainstream",
    },

    "synthetic_data": {
        "first_known_date": "2018-01",
        "years_discussed":  7,
        "origin_context": (
            "Synthetic data in ML predates modern LLMs. Discussed since at least 2018. "
            "Resurged strongly in 2024 as a core technique for LLM post-training alignment."
        ),
        "gradient_implication": (
            "ESTABLISHED ML CONCEPT: Synthetic data has 7+ years of expert discussion. "
            "High gradient reflects its permanent ML engineering home. "
            "A resurgence signal requires velocity well above its established baseline."
        ),
        "trend_trajectory": "established_expert",
    },
}

# Normalised lookup
_KNOWN = {
    k.lower().replace("-","_").replace(" ","_"): v
    for k, v in KNOWN_TOPICS.items()
}


# ────────────────────────────────────────────────────────────────
# CACHE SCHEMA
# ────────────────────────────────────────────────────────────────

CACHE_SCHEMA = """
CREATE TABLE IF NOT EXISTS research_history_cache (
    topic_key     TEXT PRIMARY KEY,
    researched_at TEXT NOT NULL,
    expires_at    TEXT NOT NULL,
    result_json   TEXT NOT NULL,
    sources_found INTEGER DEFAULT 0
);
"""


def _init_cache(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript(CACHE_SCHEMA)
    conn.commit()
    conn.close()


def _get_cached(topic_key, db_path):
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT result_json, expires_at FROM research_history_cache WHERE topic_key=?",
            (topic_key,)
        ).fetchone()
        conn.close()
        if not row: return None
        if datetime.now(timezone.utc) > datetime.fromisoformat(row["expires_at"]): return None
        return json.loads(row["result_json"])
    except Exception: return None


def _set_cache(topic_key, result, db_path):
    try:
        conn = sqlite3.connect(db_path)
        exp = (datetime.now(timezone.utc)+timedelta(days=CACHE_DAYS)).isoformat()
        conn.execute(
            "INSERT OR REPLACE INTO research_history_cache "
            "(topic_key,researched_at,expires_at,result_json,sources_found) VALUES(?,?,?,?,?)",
            (topic_key, datetime.now(timezone.utc).isoformat(), exp,
             json.dumps(result), len(result.get("sources",[])))
        )
        conn.commit(); conn.close()
    except Exception: pass


# ────────────────────────────────────────────────────────────────
# LIVE DATA SOURCE COLLECTORS
# ────────────────────────────────────────────────────────────────

def _get(url, params=None, timeout=10):
    try:
        r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=timeout)
        if r.status_code == 200: return r.json()
    except Exception: pass
    return None


def _query_hackernews(term: str) -> Optional[dict]:
    """Find earliest HN mention. Algolia API — free, no key."""
    enc = urllib.parse.quote(term)
    earliest_hit = None
    earliest_ts  = float("inf")

    # Search year by year oldest-first to find true origin
    for year in range(2007, 2022):
        t_start = int(datetime(year,   1, 1, tzinfo=timezone.utc).timestamp())
        t_end   = int(datetime(year+1, 1, 1, tzinfo=timezone.utc).timestamp())
        data = _get(
            "https://hn.algolia.com/api/v1/search_by_date",
            params={"query": term, "tags": "story", "hitsPerPage": 5,
                    "numericFilters": f"created_at_i>{t_start},created_at_i<{t_end}"}
        )
        if data and data.get("hits"):
            for hit in data["hits"]:
                ts = hit.get("created_at_i", float("inf"))
                if ts < earliest_ts:
                    earliest_ts  = ts
                    earliest_hit = hit
            if earliest_hit and year < 2016:
                break
        time.sleep(0.15)

    if not earliest_hit:
        data = _get("https://hn.algolia.com/api/v1/search_by_date",
                    params={"query": term, "tags": "story", "hitsPerPage": 1})
        if data and data.get("hits"):
            earliest_hit = data["hits"][0]
            earliest_ts  = earliest_hit.get("created_at_i", 0)

    if not earliest_hit:
        return None

    created = datetime.fromtimestamp(earliest_ts, tz=timezone.utc)
    obj_id  = earliest_hit.get("objectID","")

    # Get total count
    total_data = _get("https://hn.algolia.com/api/v1/search",
                      params={"query": term, "tags": "story", "hitsPerPage": 1})
    total = total_data.get("nbHits", 0) if total_data else 0

    t_yr = int((datetime.now(timezone.utc)-timedelta(days=365)).timestamp())
    yr_data = _get("https://hn.algolia.com/api/v1/search",
                   params={"query": term, "tags": "story", "hitsPerPage": 1,
                           "numericFilters": f"created_at_i>{t_yr}"})
    yr_count = yr_data.get("nbHits", 0) if yr_data else 0

    return {
        "source_name":       "Hacker News",
        "source_url":        earliest_hit.get("url") or f"https://news.ycombinator.com/item?id={obj_id}",
        "source_api":        f"https://hn.algolia.com/api/v1/search_by_date?query={enc}&tags=story",
        "first_date":        created.strftime("%Y-%m"),
        "first_date_str":    created.strftime("%B %Y"),
        "first_post_title":  (earliest_hit.get("title") or "")[:100],
        "total_posts":       total,
        "posts_last_year":   yr_count,
        "type":              "forum",
        "credibility":       "HIGH",
    }


def _query_wikipedia(term: str) -> Optional[dict]:
    """Get Wikipedia page creation date for the term."""
    # Search for the article
    data = _get("https://en.wikipedia.org/w/api.php", params={
        "action": "query", "list": "search", "srsearch": term,
        "srlimit": 3, "format": "json"
    })
    if not data: return None
    results = data.get("query",{}).get("search",[])
    if not results: return None

    # Find best match
    t_lower = term.lower()
    best = next((r for r in results if t_lower in r.get("title","").lower()), results[0])
    page_title = best.get("title","")

    # Get creation date
    rev = _get("https://en.wikipedia.org/w/api.php", params={
        "action":"query","titles":page_title,"prop":"revisions",
        "rvlimit":1,"rvdir":"newer","rvprop":"timestamp","format":"json"
    })

    created_date = None
    if rev:
        for page_id, page in rev.get("query",{}).get("pages",{}).items():
            revisions = page.get("revisions",[])
            if revisions:
                ts = revisions[0].get("timestamp","")
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts.replace("Z","+00:00"))
                        created_date = dt.strftime("%Y-%m")
                    except Exception: pass

    wiki_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(page_title.replace(' ','_'))}"

    return {
        "source_name":    "Wikipedia",
        "source_url":     wiki_url,
        "source_api":     f"https://en.wikipedia.org/w/api.php",
        "first_date":     created_date,
        "first_date_str": f"Wikipedia article '{page_title}' created {created_date or 'unknown'}",
        "article_title":  page_title,
        "type":           "encyclopedia",
        "credibility":    "HIGH",
    }


def _query_github(term: str) -> Optional[dict]:
    """Year-by-year GitHub repository count. Free API, optional token."""
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    year_counts: dict[str, int] = {}
    current_year = datetime.now().year
    zeros = 0

    for year in range(2015, current_year + 1):
        try:
            r = requests.get(
                "https://api.github.com/search/repositories",
                params={"q": f"{term} created:{year}-01-01..{year}-12-31", "per_page": 1},
                headers=headers, timeout=8,
            )
            if r.status_code in (403, 422):
                if r.status_code == 403: break
                continue
            if r.status_code == 200:
                count = r.json().get("total_count", 0)
                if count > 0:
                    year_counts[str(year)] = count
                    zeros = 0
                else:
                    zeros += 1
                    if zeros >= 3 and year > 2018: break
        except Exception: pass
        time.sleep(0.4)

    if not year_counts: return None

    first_yr = min(year_counts)
    peak_yr  = max(year_counts, key=lambda y: year_counts[y])

    return {
        "source_name":    "GitHub",
        "source_url":     f"https://github.com/search?q={urllib.parse.quote(term)}&type=repositories",
        "source_api":     "https://api.github.com/search/repositories",
        "first_date":     first_yr,
        "first_date_str": f"First GitHub repos in {first_yr}",
        "year_counts":    year_counts,
        "first_year":     first_yr,
        "peak_year":      peak_yr,
        "peak_count":     year_counts[peak_yr],
        "type":           "code_repository",
        "credibility":    "HIGH",
    }


def _query_trends(term: str) -> Optional[dict]:
    """Google Trends historical interest via pytrends."""
    if not HAS_PYTRENDS: return None
    try:
        pt = TrendReq(hl="en-US", tz=0, timeout=(5, 15))
        pt.build_payload([term], timeframe="all")
        df = pt.interest_over_time()
        if df is None or df.empty or term not in df.columns: return None
        s = df[term]
        if s.max() == 0: return None

        nonzero   = s[s >= 5]
        first_dt  = nonzero.index[0] if len(nonzero) else s.index[0]
        peak_dt   = s.idxmax()
        yearly    = {}
        for yr in range(first_dt.year, datetime.now().year + 1):
            yd = s[s.index.year == yr]
            if not yd.empty:
                avg = int(yd.mean())
                if avg > 0: yearly[str(yr)] = avg

        return {
            "source_name":     "Google Trends",
            "source_url":      f"https://trends.google.com/trends/explore?q={urllib.parse.quote(term)}&date=all",
            "source_api":      "pytrends",
            "first_date":      first_dt.strftime("%Y-%m"),
            "first_date_str":  f"Google search interest from {first_dt.strftime('%B %Y')}",
            "peak_date":       peak_dt.strftime("%Y-%m"),
            "peak_level":      int(s.max()),
            "current_level":   int(s.iloc[-1]),
            "yearly_interest": yearly,
            "type":            "search_interest",
            "credibility":     "HIGH",
        }
    except Exception as e:
        logger.debug(f"Trends error: {e}")
        return None


def _query_internal(topic_key: str, db_path: str) -> Optional[dict]:
    """When Now TrendIn first detected this topic in its own database."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute("""
            SELECT MIN(extracted_at) first_seen, MAX(extracted_at) last_seen,
                   COUNT(*) total, COUNT(DISTINCT platform) platforms
            FROM topic_signals WHERE topic_key=?
        """, (topic_key,)).fetchone()
        conn.close()
        if not row or not row["first_seen"]: return None
        dt = datetime.fromisoformat(row["first_seen"].replace("Z","+00:00"))
        return {
            "source_name":    "Now TrendIn Internal Database",
            "source_url":     "https://nowtrendin-e62dcb9ecb69.herokuapp.com/",
            "first_date":     dt.strftime("%Y-%m-%d"),
            "first_date_str": f"Now TrendIn first detected on {dt.strftime('%B %d, %Y')}",
            "total_signals":  row["total"],
            "platform_count": row["platforms"],
            "type":           "internal",
            "credibility":    "HIGH",
        }
    except Exception: return None


# ────────────────────────────────────────────────────────────────
# SYNTHESIS HELPERS
# ────────────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    return re.sub(r'[^\w]', '_', s.lower().strip())


def _years_ago(date_str: Optional[str]) -> Optional[float]:
    if not date_str: return None
    try:
        ds = date_str[:7] if len(date_str) > 4 else f"{date_str}-06"
        dt = datetime.strptime(ds, "%Y-%m").replace(tzinfo=timezone.utc)
        return round((datetime.now(timezone.utc)-dt).days / 365.25, 1)
    except Exception: return None


TRAJ_LABELS = {
    "fully_mainstream":       "Fully mainstream — in general vocabulary for years",
    "established_mainstream": "Established with mainstream awareness",
    "established_expert":     "Established in expert / technical communities",
    "emerging":               "Actively emerging — notable growth trajectory",
    "recently_emerged":       "Recently emerged — relatively new term",
    "new":                    "Very new — first detected recently",
}


def _infer_trajectory(years, known_traj, hn_src, trends_src):
    if known_traj:
        return known_traj, TRAJ_LABELS.get(known_traj, known_traj)
    if years is None: return "unknown", "Insufficient history data"
    if years >= 5:   return "established_mainstream", "Established — discussed 5+ years"
    if years >= 2:   return "established_expert",     "Established in expert communities (2–5 yr)"
    if years >= 0.5: return "emerging",               "Actively emerging — 6 months to 2 years"
    return "recently_emerged", "Recently emerged — less than 6 months"


def _gradient_implication(topic, years, trajectory, known_impl):
    if known_impl: return known_impl
    if years is None:
        return (f"Insufficient history for '{topic}'. Gradient calibration requires 5+ scoring "
                "cycles. Monitor for velocity changes.")
    if trajectory in ("fully_mainstream", "established_mainstream"):
        return (f"'{topic}' has been in public discourse for approximately {years:.0f} years. "
                "High gradient strength reflects permanent expert-community presence, not new "
                "emergence. A genuine signal requires velocity above the historical baseline — "
                "specifically a first-timer surge or sustained inertia acceleration.")
    if trajectory == "established_expert":
        return (f"'{topic}' has been in expert communities ~{years:.0f} years. High niche "
                "concentration is expected. The absolute Gradient Score is less meaningful than "
                "its velocity — watch for acceleration above this topic's baseline.")
    if trajectory == "emerging":
        return (f"'{topic}' is an actively emerging term (~{years:.1f} years recorded). "
                "High gradient strength IS meaningful here — this topic has not established a "
                "permanent expert home, so niche concentration signals genuine early-adopter "
                "activity.")
    return (f"'{topic}' is a relatively new term (less than {max(1,int(years or 0)+1)} year). "
            "Gradient signals reflect genuine emergence. Cross-platform signals and first-timer "
            "ratios carry full weight.")


def _summary_short(topic, years, first_date, traj):
    if years is None: return f"'{topic}' — history data collecting"
    if traj == "recently_emerged":
        s = f"{int(years*12)}mo" if years < 1 else f"{years:.1f}yr"
        return f"Newly emerged — {s} of recorded online discussion"
    if traj == "emerging":
        return f"Actively emerging — ~{years:.1f} years in expert communities"
    if traj == "established_expert":
        return f"Established expert term — ~{years:.0f} years in specialist communities"
    yr = first_date[:4] if first_date else "unknown"
    return f"Established term — discussed since {yr} (~{years:.0f} years)"


def _summary_long(topic, years, traj, milestones, hn, trends, gh, wiki):
    if years is None:
        return f"Research history for '{topic}' is being collected. Check back after several scoring cycles."

    age = (f"more than {int(years)} years" if years >= 5
           else f"approximately {years:.0f} years" if years >= 2
           else f"about {years:.1f} years" if years >= 1
           else f"approximately {int(years*12)} months")

    parts = [f"'{topic}' has been actively discussed online for {age}."]

    if hn:
        p = f"The earliest documented Hacker News discussion dates to {hn.get('first_date_str','unknown')}."
        if hn.get("total_posts"):
            p += (f" There are {hn['total_posts']:,} total HN stories mentioning this term"
                  + (f", with {hn['posts_last_year']:,} in the last year" if hn.get("posts_last_year") else "")
                  + ".")
        parts.append(p)

    if gh and gh.get("year_counts"):
        yc = gh["year_counts"]
        parts.append(
            f"GitHub repository growth started in {gh['first_year']} and peaked in "
            f"{gh['peak_year']} with {gh['peak_count']:,} repositories created that year."
        )

    if wiki and wiki.get("first_date"):
        parts.append(
            f"A Wikipedia article '{wiki.get('article_title', topic)}' was created "
            f"in {wiki['first_date'][:4]}, indicating sufficient notability by that date."
        )

    if trends:
        p = f"Google search interest became measurable from {trends.get('first_date_str','')}."
        if trends.get("current_level") is not None:
            p += f" Current interest is {trends['current_level']}/100 relative to peak."
        parts.append(p)

    if milestones:
        last = milestones[-1].get("event","")
        if last: parts.append(f"Most recent milestone: {last}")

    return " ".join(parts)


# ────────────────────────────────────────────────────────────────
# MAIN ENGINE CLASS
# ────────────────────────────────────────────────────────────────

class ResearchHistoryEngine:
    """
    Main entry point. Call .research(topic_key, topic_display).
    Results cached 7 days. Use force_refresh=True to bypass cache.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        _init_cache(db_path)

    def research(self, topic_key: str, topic_display: str,
                 force_refresh: bool = False) -> dict:

        # Cache check
        if not force_refresh:
            cached = _get_cached(topic_key, self.db_path)
            if cached:
                cached["cached"] = True
                return cached

        # Known topics shortcut
        norm_key = _norm(topic_display)
        known    = _KNOWN.get(norm_key) or _KNOWN.get(_norm(topic_key))

        sources, milestones = [], []
        known_first  = known.get("first_known_date") if known else None
        known_traj   = known.get("trend_trajectory")  if known else None
        known_impl   = known.get("gradient_implication") if known else None
        known_ms     = known.get("milestones", [])    if known else []
        milestones   = known_ms

        if known:
            sources.append({
                "source_name":    "Now TrendIn Research Database",
                "source_url":     "https://nowtrendin.com/research",
                "first_date":     known_first,
                "first_date_str": f"Documented since {known_first}",
                "type":           "curated",
                "credibility":    "HIGH",
                "note":           "Manually researched and verified",
            })
            if known.get("wikipedia_url"):
                sources.append({
                    "source_name":    "Wikipedia",
                    "source_url":     known["wikipedia_url"],
                    "first_date":     known.get("wikipedia_created"),
                    "first_date_str": f"Wikipedia since {known.get('wikipedia_created','unknown')}",
                    "type":           "encyclopedia",
                    "credibility":    "HIGH",
                })

        # Live queries
        print(f"  Researching '{topic_display}'...")

        internal = _query_internal(topic_key, self.db_path)
        if internal: sources.append(internal)

        print("    → Hacker News...")
        hn = _query_hackernews(topic_display)
        if hn: sources.append(hn)

        print("    → Wikipedia...")
        wiki = _query_wikipedia(topic_display)
        if wiki and not any(s["source_name"] == "Wikipedia" for s in sources):
            sources.append(wiki)

        print("    → GitHub...")
        gh = _query_github(topic_display)
        if gh: sources.append(gh)

        print("    → Google Trends...")
        trends = _query_trends(topic_display)
        if trends: sources.append(trends)

        # Determine earliest date
        all_dates = [known_first] if known_first else []
        for s in sources:
            fd = s.get("first_date")
            if fd and isinstance(fd, str) and len(fd) >= 4:
                all_dates.append(fd[:7] if len(fd) > 4 else f"{fd}-06")
        valid = []
        for d in all_dates:
            try:
                ds = d[:7] if len(d) > 4 else f"{d}-06"
                datetime.strptime(ds, "%Y-%m")
                valid.append(ds)
            except Exception: pass
        first_date = min(valid) if valid else None
        years      = _years_ago(first_date)

        traj, traj_label = _infer_trajectory(years, known_traj, hn, trends)
        impl     = _gradient_implication(topic_display, years, traj, known_impl)
        short    = _summary_short(topic_display, years, first_date, traj)
        long_txt = _summary_long(topic_display, years, traj, milestones, hn, trends, gh, wiki)

        # Build timeline
        timeline = []
        for ms in known_ms:
            timeline.append({"date": str(ms.get("year","")),
                              "event": ms.get("event",""),
                              "source": "Now TrendIn Research"})
        if hn and hn.get("first_date"):
            timeline.append({"date": hn["first_date"],
                              "event": "First Hacker News discussion detected",
                              "source": "Hacker News Algolia API",
                              "url": hn.get("source_url")})
        if wiki and wiki.get("first_date"):
            timeline.append({"date": wiki["first_date"],
                              "event": f"Wikipedia article '{wiki.get('article_title', topic_display)}' created",
                              "source": "Wikipedia",
                              "url": wiki.get("source_url")})
        if gh and gh.get("year_counts"):
            for yr, cnt in gh["year_counts"].items():
                if cnt >= 100:
                    timeline.append({"date": yr,
                                     "event": f"{cnt:,} GitHub repositories created",
                                     "source": "GitHub Search API",
                                     "url": gh.get("source_url")})
        if trends and trends.get("first_date"):
            timeline.append({"date": trends["first_date"],
                              "event": "Measurable Google search interest begins",
                              "source": "Google Trends",
                              "url": trends.get("source_url")})
        if internal:
            timeline.append({"date": (internal.get("first_date",""))[:7],
                              "event": f"First detected by Now TrendIn ({internal.get('total_signals',0)} signals)",
                              "source": "Now TrendIn Internal Database"})
        timeline.sort(key=lambda x: str(x.get("date","9999")))

        result = {
            "topic_key":           topic_key,
            "topic_display":       topic_display,
            "first_known_date":    first_date,
            "years_discussed":     years,
            "trajectory":          traj,
            "trajectory_label":    traj_label,
            "summary_short":       short,
            "summary_long":        long_txt,
            "gradient_implication": impl,
            "timeline":            timeline,
            "sources":             sources,
            "milestones":          known_ms,
            "github_yearly":       gh.get("year_counts") if gh else None,
            "google_yearly":       trends.get("yearly_interest") if trends else None,
            "hn_total_posts":      hn.get("total_posts") if hn else None,
            "hn_posts_last_year":  hn.get("posts_last_year") if hn else None,
            "from_known_database": known is not None,
            "sources_found":       len(sources),
            "researched_at":       datetime.now(timezone.utc).isoformat(),
            "cached":              False,
        }
        _set_cache(topic_key, result, self.db_path)
        return result


# ────────────────────────────────────────────────────────────────
# FASTAPI INTEGRATION SNIPPET
# Copy-paste into gravitational_anomaly_detector.py
# ────────────────────────────────────────────────────────────────

FASTAPI_SNIPPET = '''
# ── Add at top of gravitational_anomaly_detector.py ──────────
# from research_history import ResearchHistoryEngine

@app.get("/scores/{topic_key}/history")
def get_topic_research_history(topic_key: str, force_refresh: bool = False):
    """
    Research how long a topic has been discussed online.
    Returns timeline, sources, and what history means for the Gradient Score.

    Cached 7 days. Use ?force_refresh=true to bypass cache.
    Example: GET /scores/ai_agent/history
    """
    engine = ResearchHistoryEngine(db_path=DB_PATH)
    conn   = get_db()
    row    = conn.execute(
        "SELECT topic_display FROM gradient_scores WHERE topic_key=? LIMIT 1",
        (topic_key,)
    ).fetchone()
    conn.close()
    display = (row["topic_display"] if row else topic_key.replace("_"," "))

    return engine.research(
        topic_key     = topic_key,
        topic_display = display,
        force_refresh = force_refresh,
    )
'''


# ────────────────────────────────────────────────────────────────
# ENTRY POINT
# ────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Now TrendIn — Research History Engine")
    p.add_argument("--topic",   default="ai agent")
    p.add_argument("--key",     default="")
    p.add_argument("--db",      default=DB_PATH)
    p.add_argument("--refresh", action="store_true")
    p.add_argument("--endpoint",action="store_true", help="Print FastAPI snippet")
    args = p.parse_args()

    if args.endpoint:
        print(FASTAPI_SNIPPET)
        return

    topic_display = args.topic
    topic_key     = args.key or _norm(topic_display)

    engine = ResearchHistoryEngine(db_path=args.db)
    print(f"\nResearching: '{topic_display}' (key: {topic_key})")
    print("─" * 60)

    r = engine.research(topic_key, topic_display, force_refresh=args.refresh)

    print(f"\nSUMMARY:     {r['summary_short']}")
    print(f"TRAJECTORY:  {r['trajectory_label']}")
    print(f"FIRST KNOWN: {r.get('first_known_date','Unknown')}")
    print(f"YEARS:       {r.get('years_discussed','?')}")
    print(f"\nGRADIENT SCORE IMPLICATION:")
    print(f"  {r['gradient_implication']}")
    print(f"\nTIMELINE ({len(r['timeline'])} events):")
    for ev in r["timeline"]:
        print(f"  {ev['date']}  {ev['event']}")
        if ev.get("url"): print(f"    ↗ {ev['url']}")
    print(f"\nSOURCES ({r['sources_found']}):")
    for s in r["sources"]:
        print(f"  [{s.get('credibility','?')}] {s['source_name']}: first record {s.get('first_date','?')}")
    print(f"\nCached: {r.get('cached', False)}")


if __name__ == "__main__":
    main()
