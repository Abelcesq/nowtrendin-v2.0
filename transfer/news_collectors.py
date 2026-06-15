"""
================================================================
NOW TRENDIN — NEWS COLLECTORS (GDELT + FINNHUB)
================================================================

Adds two legitimate, free news data sources to the collection pipeline:

  GDELT   — Stage 4 (Media Coverage) for BOTH attention and risk modes.
            Free, no registration, no rate limit, no commercial
            restriction. Structured for trend/event detection.

  FINNHUB — Multi-stage for RISK mode:
            Stage 1 (Dark Positioning):  insider + congressional trading
            Stage 3 (Consumer Concern):  social sentiment
            Stage 4 (Media Coverage):    market + company news
            Free tier: 60 calls/min. Requires free API key.

DESIGN (matches existing collectors):
  - Every signal tagged with diffusion_stage
  - Every signal records source_provenance for audit
  - Graceful degradation: a missing key or premium-gated endpoint
    logs and skips, never crashes
  - Output shape matches what unified_collector and signal_integrity expect

INTEGRATION into unified_collector.py:
  In run_attention_collect(), add:
      from news_collectors import collect_gdelt_attention
      total += collect_gdelt_attention(conn, topics)
  In run_risk_collect(), add:
      from news_collectors import collect_gdelt_risk, collect_finnhub_risk
      total += collect_gdelt_risk(conn, risk_topics)
      total += collect_finnhub_risk(conn, risk_topics, tickers)

ENV VARS:
  FINNHUB_API_KEY   — free key from finnhub.io (GDELT needs none)
================================================================
"""

import os
import json
import time
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote

FINNHUB_API_KEY  = os.getenv("FINNHUB_API_KEY", "")
GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY", "")
GDELT_BASE       = "https://api.gdeltproject.org/api/v2"
FINNHUB_BASE     = "https://finnhub.io/api/v1"
GUARDIAN_BASE    = "https://content.guardianapis.com"

# GDELT throttles cloud IPs (429). Circuit breaker: after a 429, skip GDELT for
# this many seconds so we don't add retry latency to every query. Auto-recovers.
_GDELT_COOLDOWN_S    = int(os.getenv("GDELT_COOLDOWN_S", "600"))
_gdelt_cooldown_until = 0.0


# ════════════════════════════════════════════════════════════════
# SECTION 1: GDELT COLLECTOR (Stage 4 — Media Coverage)
# Free, no key, no rate limit, no commercial restriction.
# ════════════════════════════════════════════════════════════════

def _gdelt_get(endpoint: str, params: dict) -> Optional[dict]:
    """Make a GDELT DOC 2.0 API request. No auth required.

    GDELT throttles shared/cloud IPs (HTTP 429), so we pace requests and retry
    once with backoff. Callers should also cache results to minimize calls.
    """
    global _gdelt_cooldown_until
    if time.time() < _gdelt_cooldown_until:
        return None  # in cooldown after a recent 429 — skip without latency
    params["format"] = "json"
    url = f"{GDELT_BASE}/{endpoint}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "NowTrendIn/2.0 Research"})
    for attempt in range(2):
        try:
            time.sleep(1.0 if attempt == 0 else 4.0)  # pace + backoff on retry
            with urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else None
        except Exception as e:
            if "429" in str(e):
                if attempt == 0:
                    continue  # back off and retry once
                _gdelt_cooldown_until = time.time() + _GDELT_COOLDOWN_S
                print(f"  GDELT 429 — cooling down {_GDELT_COOLDOWN_S}s")
                return None
            print(f"  GDELT error for '{params.get('query','')}': {e}")
            return None
    return None


def collect_gdelt_signal(topic: str) -> Optional[dict]:
    """
    Collect GDELT media-coverage signal for a topic.

    Single artlist call (minimizes 429s from cloud IPs) → article count,
    source breadth, tone. Stage 4 media-coverage signal.

    Key insight for the gradient: a topic with HIGH GDELT volume is
    mainstream-covered — which should LOWER its gradient strength
    (the opposite of niche concentration). This is exactly what
    fixes the SpaceX "mainstream hasn't found it" distortion.
    """
    timeline = None  # skip the second call — too many GDELT requests => 429

    # ── Article list (for source breadth + tone) ──────────────────
    # Multi-word topics: GDELT exact-phrase quoting is restrictive. Quote only
    # short topics; let longer phrases match on terms to avoid empty results.
    q = f'"{topic}"' if len(topic.split()) <= 2 else topic
    articles = _gdelt_get("doc/doc", {
        "query":      q,
        "mode":       "artlist",
        "maxrecords": "75",
        "timespan":   "7d",
        "sort":       "datedesc",
    })

    if not timeline and not articles:
        return None

    # Parse volume timeline → total + velocity
    total_volume = 0
    velocity     = 0.0
    if timeline and timeline.get("timeline"):
        try:
            points = timeline["timeline"][0].get("data", [])
            vols   = [p.get("value", 0) for p in points]
            total_volume = sum(vols)
            if len(vols) >= 4:
                mid = len(vols) // 2
                earlier = sum(vols[:mid]) / max(1, mid)
                recent  = sum(vols[mid:]) / max(1, len(vols) - mid)
                velocity = round((recent - earlier) / max(0.1, earlier) * 100, 1)
        except (IndexError, KeyError):
            pass

    # Parse article list → unique source domains + tone
    source_domains = set()
    tones          = []
    article_count  = 0
    if articles and articles.get("articles"):
        for a in articles["articles"]:
            article_count += 1
            domain = a.get("domain", "")
            if domain:
                source_domains.add(domain)
            if "tone" in a:
                try:
                    tones.append(float(a["tone"]))
                except (ValueError, TypeError):
                    pass

    avg_tone = round(sum(tones) / len(tones), 2) if tones else 0.0

    return {
        "type":            "media_coverage",
        "source":          "gdelt",
        "topic":           topic,
        "diffusion_stage": 4,
        "total_volume":    total_volume or article_count,
        "article_count":   article_count,
        "source_breadth":  len(source_domains),   # distinct outlets = mainstream reach
        "avg_tone":        avg_tone,              # GDELT tone: negative=bad news
        "velocity":        velocity,
        "raw_signal":      f"GDELT: {article_count} articles across "
                           f"{len(source_domains)} outlets, tone {avg_tone}",
    }


def collect_gdelt_attention(conn, topics: list[str]) -> int:
    """Collect GDELT signals for attention-mode topics. Returns count stored."""
    stored = 0
    for topic in topics:
        sig = collect_gdelt_signal(topic)
        if sig and sig["article_count"] > 0:
            _store_news_signal(conn, "attention", topic, sig)
            stored += 1
            print(f"  [gdelt] '{topic}': {sig['article_count']} articles, "
                  f"{sig['source_breadth']} outlets")
    return stored


def collect_gdelt_risk(conn, risk_topics: list[str]) -> int:
    """Collect GDELT signals for risk-mode topics. Returns count stored."""
    stored = 0
    for topic in risk_topics:
        sig = collect_gdelt_signal(topic)
        if sig and sig["article_count"] > 0:
            # For risk, negative tone is itself a signal
            sig["risk_topic"] = topic
            _store_news_signal(conn, "risk", topic, sig)
            stored += 1
    return stored


# ════════════════════════════════════════════════════════════════
# SECTION 1b: GUARDIAN COLLECTOR (Stage 4 — Media Coverage)
# Cloud-friendly mainstream-news source. Free key, works from Heroku
# (unlike GDELT's rate-limited DOC API). Same role: mainstream weight.
# ════════════════════════════════════════════════════════════════

def collect_guardian_signal(topic: str) -> Optional[dict]:
    """
    Guardian media-coverage signal for a topic. Returns article count, distinct
    section breadth, and recency — a MAINSTREAM (Stage 4) signal. Like GDELT,
    high Guardian volume should LOWER niche concentration.
    """
    if not GUARDIAN_API_KEY:
        return None
    from_date = (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%Y-%m-%d")
    params = {
        "q": topic, "api-key": GUARDIAN_API_KEY,
        "page-size": "50", "from-date": from_date,
        "order-by": "newest", "show-fields": "none",
    }
    url = f"{GUARDIAN_BASE}/search?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "NowTrendIn/2.0"})
    try:
        time.sleep(0.2)
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  Guardian error for '{topic}': {e}")
        return None

    r = (data or {}).get("response", {})
    results = r.get("results", []) or []
    total = int(r.get("total", len(results)) or 0)
    sections = {a.get("sectionName", "") for a in results if a.get("sectionName")}
    if total <= 0 and not results:
        return None
    return {
        "type":            "media_coverage",
        "source":          "guardian",
        "topic":           topic,
        "diffusion_stage": 4,
        "total_volume":    total,
        "article_count":   len(results),
        "source_breadth":  len(sections),
        "avg_tone":        0.0,
        "raw_signal":      f"Guardian: {total} articles across {len(sections)} sections",
    }


# ════════════════════════════════════════════════════════════════
# SECTION 2: FINNHUB COLLECTOR (Stages 1, 3, 4 — Risk mode)
# 60 calls/min free. Bundles insider, congressional, sentiment, news.
# ════════════════════════════════════════════════════════════════

def _finnhub_get(endpoint: str, params: dict) -> Optional[dict]:
    """Make a Finnhub API request with the free-tier key."""
    if not FINNHUB_API_KEY:
        print("  FINNHUB_API_KEY not set — skipping Finnhub collection")
        return None
    params["token"] = FINNHUB_API_KEY
    url = f"{FINNHUB_BASE}/{endpoint}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "NowTrendIn/2.0"})
    try:
        time.sleep(1.1)  # stay well under 60/min
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        # 403 often = premium-gated endpoint on free tier; degrade gracefully
        print(f"  Finnhub error for {endpoint}: {e}")
        return None


def collect_finnhub_insider(ticker: str) -> list[dict]:
    """
    Collect insider transactions — STAGE 1 (Dark Positioning).
    Smart-money signal: insiders buying/selling before the public knows.
    """
    data = _finnhub_get("stock/insider-transactions", {"symbol": ticker})
    if not data or not data.get("data"):
        return []

    signals = []
    cutoff = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    for tx in data["data"][:50]:
        tx_date = tx.get("transactionDate", "")
        if tx_date >= cutoff:
            change = tx.get("change", 0)
            signals.append({
                "type":            "insider_transaction",
                "source":          "finnhub",
                "ticker":          ticker,
                "diffusion_stage": 1,
                "direction":       "sell" if change < 0 else "buy",
                "shares":          abs(change),
                "tx_date":         tx_date,
                "raw_signal":      f"Insider {('sell' if change<0 else 'buy')} "
                                   f"{abs(change):,} shares of {ticker}",
            })
    return signals


def collect_finnhub_congressional(ticker: str) -> list[dict]:
    """
    Collect congressional trading — STAGE 1 (Dark Positioning).
    May be premium-gated on free tier; degrades gracefully if so.
    """
    data = _finnhub_get("stock/congressional-trading", {"symbol": ticker})
    if not data or not data.get("data"):
        return []

    signals = []
    for tx in data["data"][:30]:
        signals.append({
            "type":            "congressional_trade",
            "source":          "finnhub",
            "ticker":          ticker,
            "diffusion_stage": 1,
            "direction":       tx.get("transactionType", "").lower(),
            "tx_date":         tx.get("transactionDate", ""),
            "raw_signal":      f"Congressional {tx.get('transactionType','')} of {ticker}",
        })
    return signals


def collect_finnhub_news(ticker: str) -> list[dict]:
    """Collect company news — STAGE 4 (Media Coverage)."""
    to_date   = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    data = _finnhub_get("company-news", {
        "symbol": ticker, "from": from_date, "to": to_date,
    })
    if not data or not isinstance(data, list):
        return []

    signals = []
    for article in data[:40]:
        signals.append({
            "type":            "market_news",
            "source":          "finnhub",
            "ticker":          ticker,
            "diffusion_stage": 4,
            "headline":        article.get("headline", "")[:200],
            "published":       datetime.fromtimestamp(
                                   article.get("datetime", 0), tz=timezone.utc
                               ).strftime("%Y-%m-%d") if article.get("datetime") else "",
            "raw_signal":      f"News: {article.get('source','')}",
        })
    return signals


def collect_finnhub_risk(conn, risk_topics: list[str],
                        topic_tickers: dict) -> int:
    """
    Collect Finnhub risk signals for topics mapped to tickers.

    topic_tickers: {"regional banks": ["USB", "HBAN"], ...}
    Returns count stored.
    """
    stored = 0
    for topic in risk_topics:
        tickers = topic_tickers.get(topic, [])
        for ticker in tickers:
            # Stage 1 — the high-value smart-money signals
            for sig in collect_finnhub_insider(ticker):
                sig["risk_topic"] = topic
                _store_news_signal(conn, "risk", topic, sig)
                stored += 1
            for sig in collect_finnhub_congressional(ticker):
                sig["risk_topic"] = topic
                _store_news_signal(conn, "risk", topic, sig)
                stored += 1
            # Stage 4 — media coverage
            for sig in collect_finnhub_news(ticker):
                sig["risk_topic"] = topic
                _store_news_signal(conn, "risk", topic, sig)
                stored += 1
    return stored


# ════════════════════════════════════════════════════════════════
# SECTION 3: SHARED STORAGE (matches unified_collector schema)
# ════════════════════════════════════════════════════════════════

def _store_news_signal(conn, mode: str, topic: str, signal: dict):
    """Store a news signal with provenance. Works with either signal table."""
    now = datetime.now(timezone.utc).isoformat()
    sig_id = hashlib.md5(
        f"{mode}-{topic}-{signal.get('raw_signal','')}-{now}".encode()
    ).hexdigest()[:16]

    table = "risk_signals" if mode == "risk" else "topic_signals"
    date_val = (signal.get("tx_date") or signal.get("published") or now[:10])

    try:
        if table == "risk_signals":
            conn.execute("""
                INSERT OR IGNORE INTO risk_signals
                    (id, risk_topic, signal_type, source, diffusion_stage,
                     raw_signal, signal_date, collected_at)
                VALUES (?,?,?,?,?,?,?,?)
            """, (sig_id, topic, signal.get("type", "news"),
                  signal.get("source", "gdelt"), signal.get("diffusion_stage", 4),
                  signal.get("raw_signal", ""), date_val, now))
        else:
            # Attention signals table — adapt to your actual schema
            conn.execute("""
                INSERT OR IGNORE INTO topic_signals
                    (id, topic, source, diffusion_stage, raw_signal, collected_at)
                VALUES (?,?,?,?,?,?)
            """, (sig_id, topic, signal.get("source", "gdelt"),
                  signal.get("diffusion_stage", 4),
                  signal.get("raw_signal", ""), now))
        conn.commit()
    except Exception as e:
        # Schema mismatch is non-fatal — log and continue
        print(f"  storage note: {e}")


# ════════════════════════════════════════════════════════════════
# SECTION 4: DEMO
# ════════════════════════════════════════════════════════════════

def run_demo():
    print("\n" + "="*66)
    print("NOW TRENDIN — NEWS COLLECTORS (GDELT + FINNHUB) — DEMO")
    print("="*66)

    print("\nGDELT requires no API key — attempting a live call...")
    sig = collect_gdelt_signal("artificial intelligence")
    if sig:
        print(f"  ✓ GDELT returned: {sig['article_count']} articles, "
              f"{sig['source_breadth']} outlets, tone {sig['avg_tone']}, "
              f"velocity {sig['velocity']}%")
        print(f"    Diffusion stage: {sig['diffusion_stage']} (Media Coverage)")
        print(f"    Provenance: {sig['source']}")
    else:
        print("  (No network in this environment — live call skipped)")
        print("  In production, this returns real media-coverage volume.")

    print("\nFinnhub requires a free API key (FINNHUB_API_KEY)...")
    if FINNHUB_API_KEY:
        insider = collect_finnhub_insider("AAPL")
        print(f"  ✓ Finnhub insider transactions: {len(insider)} signals (Stage 1)")
    else:
        print("  Key not set — skipping (graceful degradation working).")

    print("\n" + "="*66)
    print("KEY POINT — how this fixes the SpaceX distortion:")
    print("  GDELT feeds Stage 4 media-coverage volume. A widely-covered")
    print("  topic now registers mainstream presence, so its gradient")
    print("  strength correctly DROPS instead of falsely reading 'niche.'")
    print("  Finnhub insider/congressional data feeds Stage 1 — the")
    print("  smart-money signal that makes risk mode credible to funds.")
    print("="*66)


if __name__ == "__main__":
    run_demo()
