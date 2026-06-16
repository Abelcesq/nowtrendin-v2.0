"""
================================================================
NOW TRENDIN — FINANCIAL RISK GRADIENT SCORE ENGINE
================================================================

PURPOSE:
  Extends the Gradient Score from attention/trend detection into
  FINANCIAL RISK detection — scoring emerging risks before they
  are priced in by the market. This is what makes Now TrendIn
  attractive to hedge funds, private banks, and institutional investors.

WHY THIS DATA STRATEGY (and not scraping Bloomberg/BlackRock):
  1. LEGAL: Every source below is public, government-published,
     or accessed via an official API under its terms of service.
     No scraped proprietary data. No CFAA exposure. No litigation risk.

  2. COMMERCIAL: Institutional compliance departments will reject
     any signal built on scraped Bloomberg/BlackRock data. A risk
     score built on auditable public data is the only one they can buy.

  3. STRATEGIC: Bloomberg's moat is data nobody else can recreate.
     Now TrendIn's moat is the SAME — a proprietary RISK GRADIENT
     computed from a unique combination of public signals that
     nobody else has assembled into a single score.

THE RISK DIFFUSION PIPELINE (risk flows differently than trends):
  Stage 1 — DARK POSITIONING   Insider sells (Form 4), 13F changes,
                               options skew. Smart money moves first.
                               ← NOW TRENDIN DETECTS RISK HERE
  Stage 2 — EXPERT WARNING     SEC 8-K material events, quant forums,
                               specialist analyst notes
  Stage 3 — CONSUMER CONCERN   Financial subreddits, StockTwits
  Stage 4 — MEDIA COVERAGE     Financial news, CNBC, WSJ
  Stage 5 — RETAIL AMPLIFY     YouTube finance channels (Meet Kevin et al.)

  Detecting a risk at Stage 1-2, before it hits Stage 4-5, is the alpha.
  When retail YouTubers (Stage 5) are loud about a risk, it is usually
  already priced in — BUT that signal is still valuable as a confirmation
  and as a "crowdedness" indicator.

LEGITIMATE DATA SOURCES (all public or official-API):
  - SEC EDGAR        Form 4 (insider), 8-K (material events), 13F (holdings)
  - FRED             Federal Reserve economic indicators
  - US Treasury      Yield curve, rates
  - Reddit API       r/investing, r/stocks, r/wallstreetbets, r/SecurityAnalysis
  - YouTube Data API Financial influencer topic/sentiment (official, quota-limited)
  - GDELT            Global news event database (public)
  - Google Trends    Risk-term search velocity

HOW IT INTEGRATES:
  Risk topics flow through the same scoring pipeline as trend topics,
  but with risk-specific component weights and a risk-specific
  diffusion pattern. The output is a Risk Gradient Score (0-100)
  where HIGH means "emerging risk detected early, not yet priced in."

================================================================
"""

import os
import re
import json
import math
import time
import uuid
import hashlib
import sqlite3
import statistics
from datetime import datetime, timezone, timedelta
from typing import Optional
from urllib.request import Request, urlopen
from urllib.parse import urlencode

import requests
import db_compat

# Share the main engine's database (Postgres on Heroku) so risk topics and
# trend topics live together and persist across dyno restarts.
DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

# API keys (set as environment variables — never hardcode)
FRED_API_KEY    = os.getenv("FRED_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
SEC_USER_AGENT  = os.getenv("SEC_USER_AGENT", "NowTrendIn Research contact@nowtrendin.com")
#  ^ SEC EDGAR REQUIRES a descriptive User-Agent with contact info.
#    This is their published access policy. Respect it.


# ════════════════════════════════════════════════════════════════
# SECTION 1: LEGITIMATE DATA SOURCE REGISTRY
# Every source documented with its access basis
# ════════════════════════════════════════════════════════════════

RISK_DATA_SOURCES = {
    "sec_edgar": {
        "name":        "SEC EDGAR",
        "access":      "Public — US government, no key required",
        "base_url":    "https://data.sec.gov",
        "legal_basis": "Public domain government filings. SEC explicitly "
                       "permits programmatic access with a descriptive User-Agent.",
        "rate_limit":  "10 requests/second max (SEC fair-access policy)",
        "signals":     ["insider_transactions", "material_events", "institutional_holdings"],
        "diffusion_stage": 1,  # Dark positioning
    },
    "fred": {
        "name":        "FRED (Federal Reserve)",
        "access":      "Free API key from fred.stlouisfed.org",
        "base_url":    "https://api.stlouisfed.org/fred",
        "legal_basis": "Public economic data, free API with registration.",
        "rate_limit":  "120 requests/minute",
        "signals":     ["yield_curve", "credit_spreads", "vix_proxy", "recession_indicators"],
        "diffusion_stage": 2,  # Expert warning
    },
    "reddit_finance": {
        "name":        "Reddit Finance Communities",
        "access":      "Reddit API (already integrated in main collector)",
        "base_url":    "https://oauth.reddit.com",
        "legal_basis": "Official Reddit API under their developer terms.",
        "rate_limit":  "100 requests/minute (OAuth)",
        "subreddits":  ["investing", "stocks", "SecurityAnalysis", "wallstreetbets",
                        "options", "Bogleheads", "financialindependence", "economy"],
        "diffusion_stage": 3,  # Consumer concern
    },
    "youtube_finance": {
        "name":        "YouTube Finance Channels",
        "access":      "YouTube Data API v3 (official, quota-limited)",
        "base_url":    "https://www.googleapis.com/youtube/v3",
        "legal_basis": "Official Google API under YouTube API Services Terms. "
                       "We collect video metadata and topic signals only — "
                       "NOT republishing content. Detecting what a channel "
                       "DISCUSSES is a trend signal, like any expert signal.",
        "rate_limit":  "10,000 quota units/day (default)",
        "channels":    {
            # Financial influencers tracked as Stage 5 (retail) signals
            # Channel handles → resolved to channel IDs at runtime
            "meetkevin":      "Meet Kevin — real estate, stocks, macro",
            # Add more for breadth and to avoid single-source bias:
            "GrahamStephan":  "Graham Stephan — personal finance, real estate",
            "AndreiJikh":     "Andrei Jikh — dividend investing, crypto",
            "TheCompoundNews":"The Compound — professional market commentary",
            "Bloomberg":      "Bloomberg (public YouTube channel only — "
                              "NOT the terminal/proprietary data)",
        },
        "diffusion_stage": 5,  # Retail amplification
    },
    "gdelt": {
        "name":        "GDELT Global News",
        "access":      "Public — free, no key",
        "base_url":    "https://api.gdeltproject.org/api/v2",
        "legal_basis": "Public global news event database.",
        "rate_limit":  "Reasonable use",
        "signals":     ["news_volume", "sentiment_tone", "event_detection"],
        "diffusion_stage": 4,  # Media coverage
    },
    "treasury": {
        "name":        "US Treasury",
        "access":      "Public — US government, no key",
        "base_url":    "https://home.treasury.gov",
        "legal_basis": "Public domain government data.",
        "signals":     ["yield_curve_inversion", "rate_changes"],
        "diffusion_stage": 2,
    },
}


# ════════════════════════════════════════════════════════════════
# SECTION 2: SEC EDGAR COLLECTOR (Stage 1 — Dark Positioning)
# The most valuable risk signals: what insiders and institutions
# are actually DOING, filed publicly but rarely watched in real time.
# ════════════════════════════════════════════════════════════════

def _sec_get(path: str) -> Optional[dict]:
    """Make a rate-limited, properly-identified request to SEC EDGAR."""
    url = f"https://data.sec.gov{path}"
    try:
        time.sleep(0.12)  # respect 10 req/s limit
        r = requests.get(url, headers={"User-Agent": SEC_USER_AGENT}, timeout=15)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        print(f"SEC EDGAR error for {path}: {e}")
        return None


def collect_insider_transactions(cik: str) -> list[dict]:
    """
    Collect recent Form 4 insider transactions for a company.

    Form 4 = insider buys/sells, filed within 2 business days.
    A cluster of insider SELLS before bad news is a Stage 1 risk signal.
    A cluster of insider BUYS is a positive/de-risking signal.

    cik = SEC Central Index Key (zero-padded to 10 digits)
    Returns list of transaction signals.
    """
    cik_padded = str(cik).zfill(10)
    data = _sec_get(f"/submissions/CIK{cik_padded}.json")
    if not data:
        return []

    signals = []
    recent = data.get("filings", {}).get("recent", {})
    forms       = recent.get("form", [])
    dates       = recent.get("filingDate", [])
    accessions  = recent.get("accessionNumber", [])

    cutoff = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    for i, form in enumerate(forms):
        if form == "4" and i < len(dates) and dates[i] >= cutoff:
            signals.append({
                "type":       "insider_transaction",
                "company_cik": cik,
                "filing_date": dates[i],
                "accession":   accessions[i] if i < len(accessions) else "",
                "diffusion_stage": 1,
                "raw_signal":  "Form 4 insider filing",
            })

    return signals


def collect_material_events(cik: str) -> list[dict]:
    """
    Collect recent 8-K material event filings.

    8-K = companies must disclose major events (executive departures,
    bankruptcies, material agreements, etc.) within 4 business days.
    A surge in 8-K filings across a sector is a Stage 2 risk signal.
    """
    cik_padded = str(cik).zfill(10)
    data = _sec_get(f"/submissions/CIK{cik_padded}.json")
    if not data:
        return []

    signals = []
    recent = data.get("filings", {}).get("recent", {})
    forms       = recent.get("form", [])
    dates       = recent.get("filingDate", [])
    items       = recent.get("items", [])

    cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    for i, form in enumerate(forms):
        if form == "8-K" and i < len(dates) and dates[i] >= cutoff:
            item_codes = items[i] if i < len(items) else ""
            signals.append({
                "type":            "material_event",
                "company_cik":     cik,
                "filing_date":     dates[i],
                "item_codes":      item_codes,
                "diffusion_stage": 2,
                "raw_signal":      f"8-K material event ({item_codes})",
            })

    return signals


# ════════════════════════════════════════════════════════════════
# SECTION 3: FRED COLLECTOR (Stage 2 — Macro Risk Indicators)
# ════════════════════════════════════════════════════════════════

# Key recession/risk indicators from FRED
FRED_RISK_SERIES = {
    "T10Y2Y":      "10Y-2Y Treasury spread (inversion = recession signal)",
    "T10Y3M":      "10Y-3M Treasury spread (Fed's preferred recession signal)",
    "BAMLH0A0HYM2":"High-yield credit spread (credit stress)",
    "VIXCLS":      "VIX volatility index (fear gauge)",
    "STLFSI4":     "St. Louis Fed Financial Stress Index",
    "DRSFRMACBS":  "Mortgage delinquency rate",
    "UNRATE":      "Unemployment rate",
}

def collect_fred_indicator(series_id: str) -> Optional[dict]:
    """
    Collect the latest value and recent trend for a FRED risk indicator.

    Returns the value, the 30-day change, and a risk interpretation.
    """
    if not FRED_API_KEY:
        return None

    params = urlencode({
        "series_id":         series_id,
        "api_key":           FRED_API_KEY,
        "file_type":         "json",
        "sort_order":        "desc",
        "limit":             30,
    })
    url = f"https://api.stlouisfed.org/fred/series/observations?{params}"

    try:
        with urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"FRED error for {series_id}: {e}")
        return None

    obs = data.get("observations", [])
    if len(obs) < 2:
        return None

    try:
        latest    = float(obs[0]["value"])
        prev_30d  = float(obs[-1]["value"])
        change    = latest - prev_30d
    except (ValueError, KeyError):
        return None

    return {
        "type":            "macro_indicator",
        "series_id":       series_id,
        "description":     FRED_RISK_SERIES.get(series_id, series_id),
        "latest_value":    latest,
        "change_30d":      round(change, 3),
        "diffusion_stage": 2,
        "as_of":           obs[0].get("date", ""),
    }


# ════════════════════════════════════════════════════════════════
# SECTION 4: YOUTUBE FINANCE COLLECTOR (Stage 5 — Retail Signal)
# Uses the OFFICIAL YouTube Data API v3.
# Collects what financial channels are DISCUSSING (topic signals),
# not the content itself. This is the Meet Kevin integration —
# done legitimately through the official API.
# ════════════════════════════════════════════════════════════════

try:
    from collector_health import log_api_call as _api
except Exception:
    def _api(*a, **k): pass


def _youtube_get(endpoint: str, params: dict) -> Optional[dict]:
    _api("youtube")
    """Make an official YouTube Data API v3 request."""
    if not YOUTUBE_API_KEY:
        print("YOUTUBE_API_KEY not set — skipping YouTube collection")
        return None

    params["key"] = YOUTUBE_API_KEY
    url = f"https://www.googleapis.com/youtube/v3/{endpoint}?{urlencode(params)}"

    try:
        with urlopen(url, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"YouTube API error: {e}")
        return None


def resolve_channel_id(handle: str) -> Optional[str]:
    """Resolve a channel handle (e.g. 'meetkevin') to its channel ID."""
    data = _youtube_get("channels", {
        "part":      "id",
        "forHandle": handle,
    })
    if data and data.get("items"):
        return data["items"][0]["id"]
    return None


def collect_youtube_finance_topics(channel_handle: str, max_videos: int = 15) -> list[dict]:
    """
    Collect recent video TOPICS from a finance YouTube channel.

    IMPORTANT — what we collect and why it's legitimate:
      - We collect video TITLES and DESCRIPTIONS via the official API
      - We extract TOPICS being discussed (not the video content)
      - We use this as a Stage 5 (retail amplification) trend signal
      - We do NOT download, transcribe, republish, or store video content
      - This is topic/attention detection, identical to how we detect
        what GitHub repos or Reddit threads are about

    This is the Meet Kevin integration done correctly: we measure
    WHAT retail finance attention is focused on, as one signal layer
    among many. We never present his analysis as ours.
    """
    channel_id = resolve_channel_id(channel_handle)
    if not channel_id:
        return []

    # Get the channel's uploads playlist
    ch_data = _youtube_get("channels", {
        "part": "contentDetails,statistics",
        "id":   channel_id,
    })
    if not ch_data or not ch_data.get("items"):
        return []

    uploads_playlist = (
        ch_data["items"][0]["contentDetails"]
        ["relatedPlaylists"]["uploads"]
    )

    # Get recent videos from uploads
    playlist_data = _youtube_get("playlistItems", {
        "part":       "snippet",
        "playlistId": uploads_playlist,
        "maxResults": max_videos,
    })
    if not playlist_data:
        return []

    signals = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=14)

    for item in playlist_data.get("items", []):
        snippet  = item.get("snippet", {})
        title    = snippet.get("title", "")
        desc     = snippet.get("description", "")[:500]  # first 500 chars only
        published = snippet.get("publishedAt", "")

        # Only recent videos
        try:
            pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            if pub_dt < cutoff:
                continue
        except Exception:
            pass

        # Extract financial topics from title + description
        topics = extract_financial_topics(f"{title} {desc}")

        for topic in topics:
            signals.append({
                "type":            "retail_finance_attention",
                "source":          f"youtube:{channel_handle}",
                "topic":           topic,
                "video_title":     title,   # for attribution/audit, not republishing
                "published":       published,
                "diffusion_stage": 5,
                "raw_signal":      f"{channel_handle} discussed: {topic}",
            })

    return signals


# ════════════════════════════════════════════════════════════════
# SECTION 5: FINANCIAL TOPIC EXTRACTION
# Extracts risk-relevant financial topics from text
# ════════════════════════════════════════════════════════════════

# Financial risk vocabulary — the domain anchors for risk topics
FINANCIAL_RISK_VOCABULARY = {
    # Macro risks
    "recession", "inflation", "stagflation", "deflation", "rate hike",
    "rate cut", "yield curve", "inversion", "credit crunch", "liquidity crisis",
    "debt ceiling", "default", "sovereign debt", "currency crisis",
    # Market structure
    "margin call", "deleveraging", "short squeeze", "gamma squeeze",
    "circuit breaker", "flash crash", "volatility spike", "vix spike",
    "bear market", "correction", "drawdown", "capitulation",
    # Credit / banking
    "bank run", "bank failure", "contagion", "counterparty risk",
    "duration risk", "commercial real estate", "cre", "regional banks",
    "credit spread", "high yield", "junk bonds", "default rate",
    # Sector / company
    "earnings miss", "guidance cut", "bankruptcy", "chapter 11",
    "insider selling", "share buyback", "dividend cut", "downgrade",
    "accounting fraud", "sec investigation", "delisting",
    # Asset classes
    "crypto crash", "stablecoin depeg", "real estate bubble",
    "housing crash", "bond selloff", "tech bubble",
    # Geopolitical / systemic
    "geopolitical risk", "tariff", "trade war", "sanctions", "supply chain",
    "energy crisis", "oil shock", "black swan", "tail risk", "systemic risk",
}

def extract_financial_topics(text: str) -> list[str]:
    """Extract financial risk topics from text using the risk vocabulary."""
    text_lower = text.lower()
    found = []

    for term in FINANCIAL_RISK_VOCABULARY:
        if term in text_lower:
            found.append(term)

    # Also extract ticker symbols ($AAPL style)
    tickers = re.findall(r'\$([A-Z]{1,5})\b', text)
    for ticker in tickers[:5]:  # limit
        found.append(f"${ticker}")

    return list(set(found))[:10]  # dedupe, cap at 10


# ════════════════════════════════════════════════════════════════
# SECTION 6: RISK GRADIENT SCORE COMPUTATION
# Adapts the 5-component Gradient Score for risk detection
# ════════════════════════════════════════════════════════════════

# Risk-specific component weights
# Risk detection values EARLY positioning signals (dark matter, gradient)
# more heavily than trend detection, because the alpha is in detecting
# risk BEFORE it's priced in.
RISK_WEIGHTS = {
    "detection": {
        "gradient":      0.35,  # niche analyst vs mainstream concern ratio
        "dark_matter":   0.30,  # insider/institutional positioning (HIGH weight)
        "inertia":       0.15,  # acceleration of concern
        "medium":        0.12,  # cross-stage diffusion
        "confidence":    0.08,  # signal freshness
    },
    "confidence": {
        "dark_matter":   0.30,  # confirmed insider positioning
        "inertia":       0.28,  # sustained acceleration
        "medium":        0.22,  # full diffusion pattern
        "gradient":      0.12,
        "confidence":    0.08,
    },
}


def compute_risk_gradient(risk_signals: list[dict]) -> dict:
    """
    Compute a Risk Gradient Score from a collection of risk signals.

    INPUT: list of signals from the collectors above, all relating
           to the same risk topic (e.g. "commercial real estate")

    OUTPUT: Risk Gradient Score with detection + confidence + interpretation

    The score answers: "Is this risk emerging early (smart money
    positioning, expert warning) before it's been priced in by the
    broad market — making it actionable alpha for an institutional client?"
    """
    if not risk_signals:
        return _empty_risk_score()

    # Group signals by diffusion stage
    stages = {1: [], 2: [], 3: [], 4: [], 5: []}
    for s in risk_signals:
        stage = s.get("diffusion_stage", 3)
        stages[stage].append(s)

    total = len(risk_signals)

    # ── Component 1: Gradient Strength ────────────────────────────
    # Ratio of early-stage (1-2) signals to late-stage (4-5) signals.
    # HIGH = risk is concentrated in smart-money/expert stages,
    #        not yet in mainstream media/retail = early detection.
    # Counts are LOG-DAMPED so a high-volume source (e.g. Finnhub returns
    # hundreds of routine insider rows for a large cap) saturates gracefully
    # instead of pegging the gradient — abnormality vs. the topic's OWN baseline
    # is handled separately by _compute_baseline().
    early = len(stages[1]) + len(stages[2])
    late  = len(stages[4]) + len(stages[5])
    if late == 0:
        gradient = round(min(90, 30 + math.log1p(early) * 13), 1) if early > 0 else 30
    else:
        ratio = early / max(1, late)
        gradient = round(min(100, 40 + math.log1p(ratio) * 16), 1)

    # ── Component 2: Dark Matter ──────────────────────────────────
    # Stage 1 positioning signals (insider sells, 13F changes).
    # The highest-value risk signal — but log-damped: routine insider activity
    # on a large cap (hundreds of Form-4 / Finnhub rows) is normal, so volume
    # saturates rather than maxing the component. Clustering/acceleration is what
    # the inertia + baseline layers capture.
    dark_matter = round(min(100, math.log1p(len(stages[1])) * 15), 1)

    # ── Component 3: Inertia ──────────────────────────────────────
    # Acceleration of signals over time (requires history — computed
    # by the caller across collection cycles; placeholder here)
    inertia = _compute_signal_acceleration(risk_signals)

    # ── Component 4: Medium Sequence ──────────────────────────────
    # How many diffusion stages are active? A risk appearing across
    # multiple stages (1→2→3) is confirming its diffusion.
    active_stages = sum(1 for s in stages.values() if s)
    medium = min(100, active_stages * 22)

    # ── Component 5: Confidence Decay ─────────────────────────────
    # Freshness of the newest signals
    confidence = _compute_freshness(risk_signals)

    # ── Compute Detection + Confidence scores ─────────────────────
    wd = RISK_WEIGHTS["detection"]
    detection = round(
        gradient    * wd["gradient"] +
        dark_matter * wd["dark_matter"] +
        inertia     * wd["inertia"] +
        medium      * wd["medium"] +
        confidence  * wd["confidence"],
        1
    )

    wc = RISK_WEIGHTS["confidence"]
    confidence_score = round(
        dark_matter * wc["dark_matter"] +
        inertia     * wc["inertia"] +
        medium      * wc["medium"] +
        gradient    * wc["gradient"] +
        confidence  * wc["confidence"],
        1
    )

    # ── Risk stage classification ─────────────────────────────────
    avg = (detection + confidence_score) / 2
    if avg >= 80:
        risk_stage = "ACUTE"        # Act now — risk emerging, not yet priced
        risk_action = "Smart money is positioning. Risk not yet in mainstream pricing."
    elif avg >= 60:
        risk_stage = "ELEVATED"     # Building — monitor closely
        risk_action = "Risk signals building across expert stages. Begin hedging analysis."
    elif avg >= 40:
        risk_stage = "EMERGING"     # Early warning
        risk_action = "Early risk signals detected. Monitor for confirmation."
    elif avg >= 25:
        risk_stage = "WATCH"
        risk_action = "Low-level risk chatter. No action needed yet."
    else:
        risk_stage = "BACKGROUND"
        risk_action = "Normal background risk level."

    return {
        "detection_score":   detection,
        "confidence_score":  confidence_score,
        "risk_stage":        risk_stage,
        "risk_action":       risk_action,
        "components": {
            "gradient_strength": round(gradient, 1),
            "dark_matter":       round(dark_matter, 1),
            "inertia":           round(inertia, 1),
            "medium_sequence":   round(medium, 1),
            "confidence_decay":  round(confidence, 1),
        },
        "diffusion_breakdown": {
            "stage_1_dark_positioning": len(stages[1]),
            "stage_2_expert_warning":   len(stages[2]),
            "stage_3_consumer_concern": len(stages[3]),
            "stage_4_media_coverage":   len(stages[4]),
            "stage_5_retail_amplify":   len(stages[5]),
        },
        "total_signals":     total,
        "interpretation":    _risk_interpretation(stages, risk_stage),
    }


def _compute_signal_acceleration(signals: list[dict]) -> float:
    """Estimate acceleration. Full version compares across collection cycles."""
    # Placeholder: count recent vs older signals
    now = datetime.now(timezone.utc)
    recent = 0
    for s in signals:
        date_str = s.get("filing_date") or s.get("published") or ""
        try:
            d = datetime.fromisoformat(date_str.replace("Z", "+00:00")) if "T" in date_str \
                else datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if (now - d).days <= 7:
                recent += 1
        except Exception:
            continue
    return min(100, recent * 15)


def _compute_freshness(signals: list[dict]) -> float:
    """How fresh are the signals (newer = higher)."""
    now = datetime.now(timezone.utc)
    freshest_days = 999
    for s in signals:
        date_str = s.get("filing_date") or s.get("published") or ""
        try:
            d = datetime.fromisoformat(date_str.replace("Z", "+00:00")) if "T" in date_str \
                else datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days = (now - d).days
            freshest_days = min(freshest_days, days)
        except Exception:
            continue
    if freshest_days <= 2:   return 90
    if freshest_days <= 7:   return 70
    if freshest_days <= 14:  return 50
    if freshest_days <= 30:  return 30
    return 10


def _risk_interpretation(stages: dict, risk_stage: str) -> str:
    """Plain-English interpretation of the risk signal."""
    s1 = len(stages[1])
    s5 = len(stages[5])

    # Descriptive only — reports the diffusion pattern in the data. No advice,
    # no "smart money"/"alpha"/"priced in" claims (this is not investment advice).
    if s1 > 0 and s5 == 0:
        return (
            f"EARLY-STAGE PATTERN: {s1} insider/institutional-stage signals and no "
            f"retail-stage signals yet. Activity is concentrated in the earliest "
            f"diffusion stage in the sources we track."
        )
    elif s1 > 0 and s5 > 0:
        return (
            f"DIFFUSING PATTERN: signals span both early-stage ({s1}) and "
            f"retail-stage ({s5}) channels — present across the diffusion curve."
        )
    elif s5 > 0 and s1 == 0:
        return (
            f"LATE-STAGE PATTERN: {s5} retail-stage signals and no early-stage "
            f"signals detected — activity is concentrated in later diffusion stages."
        )
    else:
        return f"Signals at the {risk_stage} stage. Monitoring for stage progression."


def _empty_risk_score() -> dict:
    return {
        "detection_score": 0, "confidence_score": 0,
        "risk_stage": "BACKGROUND", "risk_action": "No signals collected.",
        "components": {}, "diffusion_breakdown": {}, "total_signals": 0,
        "interpretation": "No risk signals available for this topic yet.",
    }


# ════════════════════════════════════════════════════════════════
# SECTION 7: DATABASE INIT
# ════════════════════════════════════════════════════════════════

def init_risk_db(db_path: str = DB_PATH):
    """Create the risk signal storage tables (routed through db_compat → Postgres)."""
    conn = db_compat.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS risk_signals (
            id TEXT PRIMARY KEY,
            risk_topic TEXT,
            risk_display TEXT,
            signal_type TEXT,
            source TEXT,
            diffusion_stage INTEGER,
            raw_signal TEXT,
            signal_date TEXT,
            collected_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS risk_scores (
            id TEXT PRIMARY KEY,
            risk_topic TEXT,
            risk_display TEXT,
            detection_score REAL,
            confidence_score REAL,
            risk_stage TEXT,
            risk_action TEXT,
            interpretation TEXT,
            components TEXT,
            diffusion TEXT,
            total_signals INTEGER,
            source_provenance TEXT,
            maturity TEXT,
            maturity_note TEXT,
            baseline_signals REAL,
            baseline_cycles INTEGER,
            abnormality REAL,
            baseline_status TEXT,
            scored_at TEXT
        )
    """)
    # Baseline history for the Positioning engine (per-item, per-stage counts/cycle).
    conn.execute("""
        CREATE TABLE IF NOT EXISTS positioning_history (
            id TEXT PRIMARY KEY,
            item_key TEXT,
            stage INTEGER,
            signal_count INTEGER,
            cycle_at TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pos_item ON positioning_history(item_key)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_risk_topic ON risk_signals(risk_topic)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_risk_scores_topic ON risk_scores(risk_topic, scored_at)")
    conn.commit()
    # Live migrations for older risk_scores tables. Each ALTER runs in its own
    # transaction: a failure (column already exists) must not abort the next one
    # (critical on Postgres, where a failed statement poisons the transaction).
    for col in ("source_provenance TEXT", "maturity TEXT", "maturity_note TEXT",
                "baseline_signals REAL", "baseline_cycles INTEGER",
                "abnormality REAL", "baseline_status TEXT",
                "positioning_json TEXT"):
        try:
            conn.execute(f"ALTER TABLE risk_scores ADD COLUMN {col}")
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
    conn.close()


# Market-tenure classification — distinguishes a NEW/emerging risk from an
# established name where the activity (e.g. insider Form 4) is routine.
_MACRO_THEMES = {
    "recession", "inflation", "credit risk", "volatility spike",
    "financial stress", "mortgage delinquency", "yield curve inversion",
}


def _risk_maturity(display: str):
    d = (display or "").lower()
    established = {v.lower() for v in SEC_WATCHLIST.values()}
    if d in established:
        return ("ESTABLISHED",
                "Established public company, listed for years. Insider Form 4 / 8-K filings are routine "
                "for large caps — this score reflects the intensity and clustering of positioning over the "
                "last 90 days, not a brand-new risk. Confirming acceleration vs. the company's own baseline "
                "needs 2+ continuous collection cycles; Now TrendIn began monitoring this name recently, so "
                "treat the current reading as a positioning snapshot rather than a confirmed emerging risk.")
    if d in _MACRO_THEMES:
        return ("MACRO",
                "Perennial macro-risk theme — always present in markets. The score reflects current signal "
                "intensity and cross-source diffusion, not first emergence.")
    return ("EMERGING",
            "Newly surfaced risk topic with limited history. Treat as an early, unconfirmed signal until it "
            "appears across more diffusion stages and additional collection cycles.")


# Baseline: a topic's own normal-activity level. We use the most RECENT N cycles
# (not a long calendar window) so that when a new high-volume source is added
# (e.g. Finnhub), the baseline re-centres within a few hours instead of staying
# depressed by stale pre-source cycles for 90 days. Cap the window in days too.
_BASELINE_WINDOW_DAYS = int(os.getenv("RISK_BASELINE_WINDOW_DAYS", "90"))
_BASELINE_CYCLES_N    = int(os.getenv("RISK_BASELINE_CYCLES", "12"))  # recent cycles
_BASELINE_MIN_CYCLES  = 2   # need at least this many prior cycles to judge


def _compute_baseline(conn, risk_topic: str, current_signals: float) -> dict:
    """
    Abnormal-vs-own-baseline detector.

    The core problem: established names (Apple, Chevron…) carry routine insider /
    8-K activity every cycle, so an ABSOLUTE signal count always looks "elevated."
    What actually matters for an *emerging* risk is whether current activity is
    abnormal relative to THAT TOPIC'S OWN historical baseline.

    Builds a baseline from the topic's prior risk_scores rows in the trailing
    window and classifies the current reading against it. Honest about history:
    with < 2 prior cycles it returns INSUFFICIENT_HISTORY rather than guessing.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=_BASELINE_WINDOW_DAYS)).isoformat()
    try:
        # Most recent N cycles only — so a new high-volume source re-centres the
        # baseline quickly rather than being diluted by stale low-volume history.
        hist = conn.execute(
            "SELECT total_signals FROM risk_scores WHERE risk_topic = ? AND scored_at >= ? "
            "ORDER BY scored_at DESC LIMIT ?",
            (risk_topic, cutoff, _BASELINE_CYCLES_N),
        ).fetchall()
    except Exception:
        hist = []

    prior = [float(h["total_signals"] or 0) for h in hist]
    cycles = len(prior)

    if cycles < _BASELINE_MIN_CYCLES:
        return {
            "baseline_signals": round(current_signals, 1),
            "baseline_cycles":  cycles,
            "abnormality":      0.0,
            "baseline_status":  "INSUFFICIENT_HISTORY",
        }

    mean = sum(prior) / cycles
    ratio = current_signals / max(1.0, mean)
    # % above (or below) the topic's own baseline
    abnormality = round((ratio - 1.0) * 100, 1)

    if ratio >= 2.0:
        status = "SPIKE_VS_SELF"        # genuine acceleration — emerging risk
    elif ratio >= 1.3:
        status = "ELEVATED_VS_SELF"
    elif ratio >= 0.8:
        status = "AT_BASELINE"          # business-as-usual for this name
    else:
        status = "BELOW_BASELINE"       # quieter than normal

    return {
        "baseline_signals": round(mean, 1),
        "baseline_cycles":  cycles,
        "abnormality":      abnormality,
        "baseline_status":  status,
    }


_BASELINE_STATUS_NOTE = {
    "INSUFFICIENT_HISTORY": "Not enough collection cycles yet to compare against this topic's own "
                            "baseline. Current reading is a positioning snapshot, not a confirmed "
                            "acceleration — the baseline builds over the next cycles.",
    "AT_BASELINE":          "Activity is in line with this topic's own normal level — routine for this "
                            "name, not an emerging acceleration.",
    "BELOW_BASELINE":       "Activity is quieter than this topic's own baseline.",
    "ELEVATED_VS_SELF":     "Activity is meaningfully above this topic's own baseline — an early sign of "
                            "acceleration distinct from its routine background level.",
    "SPIKE_VS_SELF":        "Activity is sharply above this topic's own baseline — a genuine acceleration "
                            "even for an established name. This is the high-value emerging-risk signal.",
}


# ════════════════════════════════════════════════════════════════
# SECTION 7b: PRODUCTION INTEGRATION — collectors, persistence,
# orchestration, scoring, and getters (shared Postgres via db_compat).
# ════════════════════════════════════════════════════════════════

def _risk_key(topic: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")[:80]


# SEC watchlist — notable single names to scan for insider/8-K activity.
SEC_WATCHLIST = {
    "0000320193": "Apple", "0000789019": "Microsoft", "0001318605": "Tesla",
    "0001045810": "Nvidia", "0001326801": "Meta", "0001652044": "Alphabet",
    "0001018724": "Amazon", "0000019617": "JPMorgan", "0000072971": "Wells Fargo",
    "0000831001": "Citigroup", "0000895421": "Morgan Stanley", "0000051143": "IBM",
    "0000037996": "Ford", "0000093410": "Chevron", "0000936468": "Lockheed Martin",
}

# FRED series → the risk theme it feeds, and the change direction that = stress.
FRED_THEME = {
    "T10Y2Y":       ("recession", -0.05),       # inversion deepening
    "T10Y3M":       ("recession", -0.05),
    "BAMLH0A0HYM2": ("credit risk", 0.10),       # spreads widening
    "VIXCLS":       ("volatility spike", 2.0),
    "STLFSI4":      ("financial stress", 0.10),
    "DRSFRMACBS":   ("mortgage delinquency", 0.05),
}

GDELT_RISK_QUERY = (
    '(recession OR inflation OR "credit risk" OR bankruptcy OR default OR '
    '"bank failure" OR "commercial real estate" OR layoffs OR "debt ceiling" '
    'OR contagion OR downgrade OR "liquidity crisis")'
)

REDDIT_FINANCE_SUBS = ["investing", "stocks", "wallstreetbets", "SecurityAnalysis", "economy"]


def _persist_risk_signal(conn, risk_display, signal_type, source, stage, raw, signal_date):
    key = _risk_key(risk_display)
    sig_id = hashlib.md5(f"{source}-{key}-{raw}-{signal_date}".encode()).hexdigest()[:24]
    conn.execute(
        "INSERT OR IGNORE INTO risk_signals VALUES (?,?,?,?,?,?,?,?,?)",
        (sig_id, key, risk_display, signal_type, source, stage, raw[:300], signal_date,
         datetime.now(timezone.utc).isoformat()),
    )


def collect_gdelt(conn) -> int:
    """Stage 4 — media coverage. GDELT DOC 2.0 article list (no key)."""
    count = 0
    try:
        r = requests.get(
            "https://api.gdeltproject.org/api/v2/doc/doc",
            params={"query": GDELT_RISK_QUERY, "mode": "artlist",
                    "maxrecords": 75, "timespan": "3d", "format": "json"},
            headers={"User-Agent": SEC_USER_AGENT}, timeout=20,
        )
        arts = r.json().get("articles", []) if r.status_code == 200 else []
        for a in arts:
            title = a.get("title", "") or ""
            date = a.get("seendate", "") or ""
            for topic in extract_financial_topics(title):
                _persist_risk_signal(conn, topic, "news", "gdelt", 4, f"News: {title}", date)
                count += 1
    except Exception as e:
        print(f"[risk] GDELT error: {e}")
    conn.commit()
    return count


def collect_reddit_finance(conn) -> int:
    """Stage 3 — consumer concern. Public Reddit JSON (UA only)."""
    count = 0
    now = datetime.now(timezone.utc).isoformat()
    for sub in REDDIT_FINANCE_SUBS:
        try:
            r = requests.get(
                f"https://www.reddit.com/r/{sub}/hot.json",
                params={"limit": 25}, headers={"User-Agent": SEC_USER_AGENT}, timeout=15,
            )
            if r.status_code != 200:
                continue
            for child in r.json().get("data", {}).get("children", []):
                d = child.get("data", {})
                text = f"{d.get('title','')} {d.get('selftext','')[:300]}"
                for topic in extract_financial_topics(text):
                    _persist_risk_signal(conn, topic, "social", f"reddit:{sub}", 3,
                                         f"r/{sub}: {d.get('title','')}", now)
                    count += 1
        except Exception as e:
            print(f"[risk] Reddit {sub} error: {e}")
    conn.commit()
    return count


def collect_sec_watchlist(conn) -> int:
    """Stage 1/2 — insider (Form 4) + material events (8-K) for watchlist names."""
    count = 0
    for cik, name in SEC_WATCHLIST.items():
        try:
            for s in collect_insider_transactions(cik):
                _persist_risk_signal(conn, name, "insider_transaction", "sec_edgar", 1,
                                     s["raw_signal"], s["filing_date"])
                count += 1
            for s in collect_material_events(cik):
                _persist_risk_signal(conn, name, "material_event", "sec_edgar", 2,
                                     s["raw_signal"], s["filing_date"])
                count += 1
        except Exception as e:
            print(f"[risk] SEC {name} error: {e}")
    conn.commit()
    return count


def collect_fred_risks(conn) -> int:
    """Stage 2 — macro stress indicators (needs FRED_API_KEY)."""
    if not FRED_API_KEY:
        return 0
    count = 0
    for series, (theme, thresh) in FRED_THEME.items():
        try:
            ind = collect_fred_indicator(series)
            if not ind:
                continue
            change = ind["change_30d"]
            stressed = (change <= thresh) if thresh < 0 else (change >= thresh)
            if stressed:
                _persist_risk_signal(
                    conn, theme, "macro_indicator", "fred", 2,
                    f"{ind['description']}: {ind['latest_value']} (Δ30d {change})",
                    ind.get("as_of", ""),
                )
                count += 1
        except Exception as e:
            print(f"[risk] FRED {series} error: {e}")
    conn.commit()
    return count


# Watchlist name → ticker, for Finnhub insider/congressional/news lookups.
WATCHLIST_TICKERS = {
    "Apple": "AAPL", "Microsoft": "MSFT", "Tesla": "TSLA", "Nvidia": "NVDA",
    "Meta": "META", "Alphabet": "GOOGL", "Amazon": "AMZN", "JPMorgan": "JPM",
    "Wells Fargo": "WFC", "Citigroup": "C", "Morgan Stanley": "MS", "IBM": "IBM",
    "Ford": "F", "Chevron": "CVX", "Lockheed Martin": "LMT",
}


def collect_finnhub_risks(conn) -> int:
    """Stage 1 (insider + congressional smart-money) + Stage 4 (market news) for
    watchlist names via Finnhub. Needs FINNHUB_API_KEY; degrades gracefully."""
    if not os.getenv("FINNHUB_API_KEY"):
        return 0
    try:
        import news_collectors as nc
    except Exception as e:
        print(f"[risk] finnhub import error: {e}")
        return 0
    count = 0
    for display, ticker in WATCHLIST_TICKERS.items():
        try:
            for s in nc.collect_finnhub_insider(ticker):
                _persist_risk_signal(conn, display, "insider_transaction", "finnhub", 1,
                                     s["raw_signal"], s.get("tx_date", ""))
                count += 1
            for s in nc.collect_finnhub_congressional(ticker):
                _persist_risk_signal(conn, display, "congressional_trade", "finnhub", 1,
                                     s["raw_signal"], s.get("tx_date", ""))
                count += 1
            for s in nc.collect_finnhub_news(ticker):
                _persist_risk_signal(conn, display, "market_news", "finnhub", 4,
                                     s["raw_signal"], s.get("published", ""))
                count += 1
        except Exception as e:
            print(f"[risk] Finnhub {ticker} error: {e}")
    conn.commit()
    print(f"[risk] finnhub: {count} signals")
    return count


def collect_youtube_risks(conn) -> int:
    """Stage 5 — retail amplification (needs YOUTUBE_API_KEY)."""
    if not YOUTUBE_API_KEY:
        return 0
    count = 0
    channels = RISK_DATA_SOURCES["youtube_finance"]["channels"].keys()
    for handle in channels:
        try:
            for s in collect_youtube_finance_topics(handle, max_videos=12):
                _persist_risk_signal(conn, s["topic"], "retail_finance", s["source"], 5,
                                     s["raw_signal"], s.get("published", ""))
                count += 1
        except Exception as e:
            print(f"[risk] YouTube {handle} error: {e}")
    conn.commit()
    return count


def run_risk_collection(db_path: str = DB_PATH) -> dict:
    """Run every risk collector and persist signals."""
    init_risk_db(db_path)
    conn = db_compat.connect(db_path)
    counts = {
        "sec": collect_sec_watchlist(conn),
        "gdelt": collect_gdelt(conn),
        "reddit": collect_reddit_finance(conn),
        "fred": collect_fred_risks(conn),
        "youtube": collect_youtube_risks(conn),
        "finnhub": collect_finnhub_risks(conn),
        "creators": collect_creator_risk_signals(conn),
        "broadcast": collect_broadcast_risk_signals(conn),
        "yahoo_finance": collect_yahoo_finance_risk_signals(conn),
    }
    conn.close()
    print(f"[risk] collected: {counts}")
    return counts


# ════════════════════════════════════════════════════════════════
# POSITIONING ENGINE — baseline-relative scoring (the "Other" section).
# Scores how abnormally active an item's insider/institutional positioning is
# vs its OWN baseline (z-score), NOT absolute volume. Replaces the old absolute
# "risk" score that made every mega-cap read ~77. Word "risk" removed from output.
# ════════════════════════════════════════════════════════════════

STAGE_WEIGHTS = {1: 0.40, 2: 0.30, 3: 0.15, 4: 0.10, 5: 0.05}
STAGE_LABELS  = {1: "Dark Positioning", 2: "Expert Warning", 3: "Consumer Concern",
                 4: "Media Coverage", 5: "Retail Amplify"}
MIN_BASELINE_CYCLES = 3


def positioning_record_cycle(conn, item_key: str, signals_by_stage: dict) -> None:
    now = datetime.now(timezone.utc).isoformat()
    for stage, count in signals_by_stage.items():
        rec_id = hashlib.md5(f"{item_key}-{stage}-{now}".encode()).hexdigest()[:16]
        conn.execute(
            "INSERT OR IGNORE INTO positioning_history (id, item_key, stage, signal_count, cycle_at) VALUES (?,?,?,?,?)",
            (rec_id, item_key, int(stage), int(count), now),
        )


def positioning_baseline(conn, item_key: str, lookback_cycles: int = 12) -> dict:
    """Per-stage mean/stdev over prior cycles (the most recent cycle excluded)."""
    rows = conn.execute(
        "SELECT stage, signal_count, cycle_at FROM positioning_history WHERE item_key = ? ORDER BY cycle_at DESC",
        (item_key,),
    ).fetchall()
    if not rows:
        return {"cycles": 0}
    cycle_ts = sorted({r["cycle_at"] for r in rows}, reverse=True)
    baseline_cycles = set(cycle_ts[1:lookback_cycles + 1])  # skip the most recent
    by_stage = {}
    for r in rows:
        if r["cycle_at"] in baseline_cycles:
            by_stage.setdefault(r["stage"], []).append(r["signal_count"])
    profile = {"cycles": len(baseline_cycles)}
    for stage, counts in by_stage.items():
        mean = statistics.mean(counts)
        stdev = statistics.stdev(counts) if len(counts) >= 2 else max(1.0, mean * 0.3)
        profile[stage] = {"mean": round(mean, 1), "stdev": round(max(0.5, stdev), 2), "samples": len(counts)}
    return profile


def _pos_scale(x, in_lo, in_hi, out_lo, out_hi):
    if in_hi == in_lo:
        return out_lo
    t = max(0.0, min(1.0, (x - in_lo) / (in_hi - in_lo)))
    return round(out_lo + t * (out_hi - out_lo), 1)


def _pos_z_to_score(z: float) -> float:
    if z <= 0.3:
        return _pos_scale(z, -1.0, 0.3, 5, 20)
    elif z <= 1.0:
        return _pos_scale(z, 0.3, 1.0, 20, 45)
    elif z <= 2.0:
        return _pos_scale(z, 1.0, 2.0, 45, 72)
    return min(100, _pos_scale(z, 2.0, 4.0, 72, 100))


def compute_positioning_score(conn, item_key: str, current_by_stage: dict) -> dict:
    profile = positioning_baseline(conn, item_key)
    cycles = profile.get("cycles", 0)
    if cycles < MIN_BASELINE_CYCLES:
        return {"score": 12.0, "classification": "CALIBRATING", "baseline_cycles": cycles,
                "stage_z": {}, "percent_delta": None, "total_signals": sum(current_by_stage.values()),
                "sufficient_baseline": False}
    stage_z, total_current, total_baseline = {}, 0, 0.0
    for stage, cnt in current_by_stage.items():
        total_current += cnt
        b = profile.get(stage)
        if not b:
            stage_z[stage] = None
            continue
        total_baseline += b["mean"]
        stage_z[stage] = round((cnt - b["mean"]) / max(0.5, b["stdev"]), 2)
    composite_z, weight_used = 0.0, 0.0
    for stage, z in stage_z.items():
        if z is None:
            continue
        w = STAGE_WEIGHTS.get(stage, 0.05)
        composite_z += max(0.0, z) * w
        weight_used += w
    if weight_used > 0:
        composite_z = composite_z / weight_used * sum(STAGE_WEIGHTS.values())
    score = _pos_z_to_score(composite_z)
    percent_delta = round((total_current - total_baseline) / total_baseline * 100, 1) if total_baseline > 0 else None
    cls = "ROUTINE" if score < 25 else "WATCH" if score < 50 else "ELEVATED" if score < 72 else "UNUSUAL"
    return {"score": round(score, 1), "classification": cls, "baseline_cycles": cycles,
            "stage_z": stage_z, "composite_z": round(composite_z, 2), "percent_delta": percent_delta,
            "total_signals": total_current, "total_baseline": round(total_baseline, 1),
            "sufficient_baseline": True}


def positioning_narrative(item_name: str, sr: dict, retail_active: bool) -> dict:
    cls = sr["classification"]
    delta = sr.get("percent_delta")
    zz = sr.get("stage_z", {})
    cycles = sr.get("baseline_cycles", 0)
    dstr = f"{delta:+.0f}%" if delta is not None else "n/a"
    if cls == "CALIBRATING":
        return {"headline": "Building baseline",
                "body": (f"Now TrendIn has only {cycles} prior cycle(s) for {item_name}. Anomaly detection "
                         f"needs at least {MIN_BASELINE_CYCLES} cycles to establish a normal level. This is a "
                         f"snapshot, not a confirmed signal — no positioning judgment yet."),
                "fire_early_signal": False, "tone": "neutral"}
    if cls in ("ROUTINE", "WATCH"):
        return {"headline": "Routine positioning" if cls == "ROUTINE" else "Slightly elevated",
                "body": (f"Activity is {'in line with' if cls=='ROUTINE' else 'modestly above'} {item_name}'s "
                         f"normal level ({dstr} vs baseline). "
                         f"{'Nothing unusual — routine insider and institutional filings for this name.' if cls=='ROUTINE' else 'Worth monitoring, but not yet a strong anomaly.'}"),
                "fire_early_signal": False, "tone": "neutral"}
    z1, z2, z4, z5 = (zz.get(1) or 0), (zz.get(2) or 0), (zz.get(4) or 0), (zz.get(5) or 0)
    early_concentrated = (z1 > 1.0 or z2 > 1.0)
    late_active = (z4 > 1.0 or z5 > 1.0)
    if early_concentrated and not late_active:
        awareness = " with limited public awareness so far" if retail_active else ""
        unknown = ("" if retail_active else
                   " (Note: consumer/retail collectors are not yet confirming downstream awareness — "
                   "treat the 'early' read as provisional until they are.)")
        return {"headline": "Unusual early positioning",
                "body": (f"{item_name} is showing positioning {dstr} above its normal level, concentrated in "
                         f"insider/institutional filings{awareness}. This is the higher-value detection window.{unknown}"),
                "fire_early_signal": True, "tone": "alert"}
    if late_active:
        return {"headline": "Elevated — but already surfacing",
                "body": (f"{item_name} positioning is elevated ({dstr} vs baseline), but activity is already "
                         f"appearing in media/retail stages — likely already known and partly priced in."),
                "fire_early_signal": False, "tone": "neutral"}
    return {"headline": "Elevated activity",
            "body": (f"{item_name} is showing elevated positioning ({dstr} vs baseline), spread across stages "
                     f"without a clear early concentration. Monitor for whether it sharpens into an early signal."),
            "fire_early_signal": False, "tone": "neutral"}


POSITIONING_DEFINITION = ("Where insider and institutional positioning is abnormally active relative to "
                          "this item's own baseline. Analysis only — not financial advice, and not a risk rating.")


# ════════════════════════════════════════════════════════════════
# FINANCIAL SUSTAINABILITY SCORE (1–100) — a FACTUAL fundamentals read.
# Profitability + cash/liquidity vs. leverage, computed from the company's own
# reported balance sheet (via Finnhub basic financials). This is descriptive
# data, NOT a buy/sell recommendation and NOT financial advice.
# ════════════════════════════════════════════════════════════════

SUSTAINABILITY_DEFINITION = (
    "A factual 1–100 read of balance-sheet health from the company's own reported "
    "financials: profitability, cash/liquidity, and leverage. Higher = more "
    "financially sustainable (profitable, cash-backed, low debt). Descriptive data "
    "only — not a buy/sell recommendation and not financial advice."
)


# Sector classification + sector-specific debt/equity grading scales.
# (hi, lo): D/E at `hi` scores 0 (strained for that sector), at `lo` scores 100.
_TICKER_SECTOR = {
    "JPM": "banks", "WFC": "banks", "C": "banks", "MS": "banks",
    "AAPL": "technology", "MSFT": "technology", "NVDA": "technology", "META": "technology",
    "GOOGL": "technology", "AMZN": "technology", "IBM": "technology",
    "TSLA": "autos", "F": "autos", "CVX": "energy", "LMT": "defense",
}
SECTOR_DE_SCALE = {
    "banks":      (12.0, 2.0),   # banks structurally run high leverage
    "autos":      (3.0, 0.5),    # capital-intensive, financing arms
    "energy":     (2.5, 0.4),
    "defense":    (3.0, 0.5),    # large contract/pension balance sheets
    "technology": (2.0, 0.3),    # asset-light → low debt is the norm
}
SECTOR_NOTE = {
    "banks":      "banks fund lending with debt, so a high debt/equity is normal, not strained",
    "autos":      "automakers are capital-intensive and carry financing arms, so moderate leverage is normal",
    "energy":     "energy producers carry asset-financing debt through cycles",
    "defense":    "large contract and pension balance sheets carry structural leverage",
    "technology": "asset-light tech is expected to carry low debt",
}


def _ticker_sector(ticker: str) -> str:
    return _TICKER_SECTOR.get((ticker or "").upper(), "general")


def _finnhub_metrics(ticker: str) -> Optional[dict]:
    """Fetch Finnhub basic-financials 'metric' dict for a ticker (needs FINNHUB_API_KEY)."""
    key = os.getenv("FINNHUB_API_KEY")
    if not key:
        return None
    url = f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all&token={key}"
    try:
        req = Request(url, headers={"User-Agent": "NowTrendIn/2.0"})
        _api("finnhub")
        with urlopen(req, timeout=6) as resp:   # short — fundamentals change slowly
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("metric") or None
    except Exception as e:
        print(f"[sustainability] finnhub metric error for {ticker}: {e}")
        return None


# Module-level cache: fundamentals change quarterly, so recompute at most every
# few hours. This keeps the per-cycle HTTP cost ~zero and prevents holding a DB
# connection while making 15 live Finnhub calls (which exhausted the pool).
_SUS_CACHE: dict = {}
_SUS_TTL_SEC = int(os.getenv("SUSTAINABILITY_TTL_SEC", "21600"))  # 6h


def _first_num(m: dict, *keys):
    for k in keys:
        v = m.get(k)
        if v is not None:
            try:
                return float(v)
            except Exception:
                continue
    return None


def compute_sustainability(ticker: str) -> Optional[dict]:
    """Compute the factual Financial Sustainability score (1–100) for a ticker.

    Cached for _SUS_TTL_SEC (fundamentals change quarterly). Sub-scores (0–100):
      • Profitability  — net profit margin + return on equity
      • Cash/Liquidity — current & quick ratios (ability to cover obligations)
      • Leverage health (inverted) — lower debt/equity = healthier
    """
    import time as _t
    cached = _SUS_CACHE.get(ticker)
    if cached and (_t.time() - cached[0] < _SUS_TTL_SEC):
        return cached[1]

    m = _finnhub_metrics(ticker)
    if not m:
        # Serve a slightly-stale cached value rather than nothing on a transient miss.
        return cached[1] if cached else None

    npm = _first_num(m, "netProfitMarginTTM", "netProfitMarginAnnual")          # %
    roe = _first_num(m, "roeTTM", "roeRfy", "roeAnnual")                          # %
    cur = _first_num(m, "currentRatioQuarterly", "currentRatioAnnual")
    qck = _first_num(m, "quickRatioQuarterly", "quickRatioAnnual")
    de  = _first_num(m, "totalDebt/totalEquityQuarterly", "totalDebt/totalEquityAnnual",
                     "longTermDebt/equityQuarterly", "longTermDebt/equityAnnual")

    have = [x for x in (npm, roe, cur, de) if x is not None]
    if len(have) < 2:
        return None  # not enough fundamentals to score honestly

    # ── Profitability (0–100): margin to 25% = full; ROE to 25% = full ──
    prof_parts = []
    if npm is not None:
        prof_parts.append(_pos_scale(npm, 0, 25, 0, 100))
    if roe is not None:
        prof_parts.append(_pos_scale(roe, 0, 25, 0, 100))
    profitability = round(sum(prof_parts) / len(prof_parts), 1) if prof_parts else None

    # ── Cash / liquidity (0–100): current ratio 1.0→40, 2.0→100; quick blends ──
    liq_parts = []
    if cur is not None:
        liq_parts.append(_pos_scale(cur, 0.8, 2.0, 10, 100))
    if qck is not None:
        liq_parts.append(_pos_scale(qck, 0.5, 1.5, 10, 100))
    liquidity = round(sum(liq_parts) / len(liq_parts), 1) if liq_parts else None

    # ── Leverage health (0–100, inverted) — ABSOLUTE (cross-company) ──
    # Default scale: D/E 0.3→100 (healthy), 2.0→0 (strained).
    leverage_health = round(_pos_scale(de, 2.0, 0.3, 0, 100), 1) if de is not None else None
    # ── Leverage health — SECTOR-ADJUSTED ──
    # Some sectors (banks, utilities, autos) structurally carry more debt, so a
    # raw D/E penalty mis-grades them. The sector scale grades leverage against
    # peers in the same business model instead of against the whole market.
    sector = _ticker_sector(ticker)
    s_hi, s_lo = SECTOR_DE_SCALE.get(sector, (2.0, 0.3))
    leverage_health_sector = round(_pos_scale(de, s_hi, s_lo, 0, 100), 1) if de is not None else None

    def _composite(lev):
        weights = {"p": 0.40, "l": 0.25, "g": 0.35}
        parts, wsum = 0.0, 0.0
        if profitability is not None:
            parts += profitability * weights["p"]; wsum += weights["p"]
        if liquidity is not None:
            parts += liquidity * weights["l"]; wsum += weights["l"]
        if lev is not None:
            parts += lev * weights["g"]; wsum += weights["g"]
        return max(1.0, min(100.0, round(parts / wsum, 1))) if wsum else None

    composite = _composite(leverage_health)
    composite_sector = _composite(leverage_health_sector)
    if composite is None:
        return None

    def _label(x):
        return ("Strong balance sheet" if x >= 75 else "Solid" if x >= 50 else
                "Mixed / leveraged" if x >= 30 else "Strained / highly leveraged")

    sector_explanation = (
        f"Raw score grades leverage against all companies. The sector-adjusted score "
        f"grades it against {sector} norms — {SECTOR_NOTE.get(sector, 'typical leverage for this business model')}. "
        f"Profitability and liquidity are identical in both."
    )

    result = {
        "score": composite,                       # absolute / cross-company
        "label": _label(composite),
        "sector": sector,
        "sector_adjusted_score": composite_sector,
        "sector_adjusted_label": _label(composite_sector) if composite_sector is not None else None,
        "sector_explanation": sector_explanation,
        "profitability": profitability,
        "liquidity": liquidity,
        "leverage_health": leverage_health,
        "leverage_health_sector": leverage_health_sector,
        "metrics": {
            "net_profit_margin_pct": round(npm, 1) if npm is not None else None,
            "roe_pct": round(roe, 1) if roe is not None else None,
            "current_ratio": round(cur, 2) if cur is not None else None,
            "debt_to_equity": round(de, 2) if de is not None else None,
        },
        "definition": SUSTAINABILITY_DEFINITION,
    }
    _SUS_CACHE[ticker] = (_t.time(), result)
    return result


# ════════════════════════════════════════════════════════════════
# MEET KEVIN COVERAGE — retail/influencer attention data point.
# Surfaces WHICH watchlist names Meet Kevin is publicly covering on YouTube
# (titles, dates, links via the official API) as a Stage-5 retail-attention
# signal. This is a DATA point with attribution — we do NOT extract or
# republish his buy/sell calls as Now TrendIn recommendations.
# ════════════════════════════════════════════════════════════════

_MK_CACHE: dict = {}            # {"videos": [...], "ts": epoch}
_MK_TTL_SEC = int(os.getenv("MEETKEVIN_TTL_SEC", "21600"))  # 6h
MEET_KEVIN_NOTE = ("Reflects what Meet Kevin is publicly covering on YouTube (a retail-attention "
                   "signal). Attributed third-party content for context — not Now TrendIn's analysis "
                   "or a recommendation. In the diffusion model, retail coverage is a LATE-stage signal.")


def _meet_kevin_recent(max_videos: int = 40) -> list:
    """Meet Kevin's recent uploads (title/desc/date/url), cached ~6h."""
    import time as _t
    cached = _MK_CACHE.get("videos")
    if cached is not None and (_t.time() - _MK_CACHE.get("ts", 0) < _MK_TTL_SEC):
        return cached
    vids = []
    try:
        channel_id = resolve_channel_id("meetkevin")
        if channel_id:
            ch = _youtube_get("channels", {"part": "contentDetails", "id": channel_id})
            up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"] if ch and ch.get("items") else None
            if up:
                pl = _youtube_get("playlistItems", {"part": "snippet", "playlistId": up, "maxResults": max_videos})
                for it in (pl or {}).get("items", []):
                    sn = it.get("snippet", {})
                    vid = (sn.get("resourceId") or {}).get("videoId", "")
                    vids.append({
                        "title": sn.get("title", ""),
                        "desc": (sn.get("description", "") or "")[:300],
                        "published": sn.get("publishedAt", ""),
                        "url": f"https://www.youtube.com/watch?v={vid}" if vid else "https://www.youtube.com/@MeetKevin",
                    })
    except Exception as e:
        print(f"[meetkevin] fetch error: {e}")
        return cached or []
    _MK_CACHE["videos"] = vids
    _MK_CACHE["ts"] = _t.time()
    return vids


def meet_kevin_coverage(company_name: str, ticker: str) -> Optional[dict]:
    """Find Meet Kevin's recent videos covering this company/ticker. Factual coverage only."""
    vids = _meet_kevin_recent()
    if not vids:
        return None
    name_l = (company_name or "").lower()
    tkr = (ticker or "").upper()
    # Match on company name or ticker as a whole word ($AAPL / AAPL / "Apple").
    tkr_re = re.compile(rf"(?<![A-Za-z])\$?{re.escape(tkr)}(?![A-Za-z])") if tkr else None
    hits = []
    for v in vids:
        hay = f"{v['title']} {v['desc']}"
        if (name_l and name_l in hay.lower()) or (tkr_re and tkr_re.search(hay)):
            hits.append({"title": v["title"], "published": v["published"], "url": v["url"]})
    if not hits:
        return {"covered": False, "count": 0, "note": MEET_KEVIN_NOTE,
                "channel_url": "https://www.youtube.com/@MeetKevin"}
    hits.sort(key=lambda h: h["published"], reverse=True)
    return {
        "covered": True,
        "count": len(hits),
        "latest_title": hits[0]["title"],
        "latest_published": hits[0]["published"],
        "latest_url": hits[0]["url"],
        "recent": hits[:5],
        "channel_url": "https://www.youtube.com/@MeetKevin",
        "note": MEET_KEVIN_NOTE,
    }


# ── Alpha Vantage retail/media coverage (NEWS_SENTIMENT) ──────────────
_AV_CACHE: dict = {}
_AV_TTL_SEC = int(os.getenv("ALPHAVANTAGE_TTL_SEC", "21600"))  # 6h
AV_NOTE = ("Volume and average tone of recent market-news articles mentioning this "
           "ticker (Alpha Vantage News & Sentiment). A media/retail-attention signal, "
           "descriptive only — not Now TrendIn's analysis or a recommendation.")


# ── Creator coverage (Meet Kevin + Andrei Jikh) ──────────────────────
# Retail-attention creators. Their recent YouTube uploads are an attributed
# third-party data point (NOT Now TrendIn's analysis), surfaced as Retail
# Coverage and fed into the trend + risk feeds (a LATE/retail-stage signal).
CREATORS = [
    {"handle": "meetkevin",            "name": "Meet Kevin"},
    {"handle": "AndreiJikh",           "name": "Andrei Jikh"},
    {"handle": "GrahamStephan",        "name": "Graham Stephan"},
    {"handle": "TheGrahamStephanShow", "name": "Graham Stephan (Show)"},
    {"handle": "MinorityMindset",      "name": "Minority Mindset"},
]
CREATOR_NOTE = ("Reflects what these retail-finance creators are publicly covering on "
                "YouTube — an attributed retail-attention signal, not Now TrendIn's analysis "
                "or a recommendation. In the diffusion model, retail coverage is LATE-stage.")

# Broadcast/institutional news channels — mainstream tier, NOT retail.
# These are the established journalistic orgs; coverage here signals broad
# public awareness (LATE in the diffusion curve, different from niche/creator).
BROADCAST_CHANNELS = [
    {"handle": "CNBC",               "name": "CNBC",               "region": "US"},
    {"handle": "CNN",                "name": "CNN",                 "region": "US"},
    {"handle": "Bloomberg-News",     "name": "Bloomberg News",      "region": "US"},
    {"handle": "markets",            "name": "Bloomberg Markets",   "region": "US"},
    {"handle": "bloomberglp",        "name": "Bloomberg LP",        "region": "US"},
    {"handle": "msnow",              "name": "MSNBC",               "region": "US"},
    {"handle": "AssociatedPress",    "name": "Associated Press",    "region": "US"},
    {"handle": "BBCNews",            "name": "BBC News",            "region": "UK"},
    {"handle": "wsj",                "name": "Wall Street Journal", "region": "US"},
    {"handle": "PBSNewsHour",        "name": "PBS NewsHour",        "region": "US"},
    {"handle": "FinancialTimes",     "name": "Financial Times",     "region": "UK"},
    {"handle": "theGuardian",        "name": "The Guardian",        "region": "UK"},
    {"handle": "NHKWORLDJAPAN",      "name": "NHK World Japan",     "region": "JP"},
    {"handle": "ZDFheute",           "name": "ZDF heute",           "region": "DE"},
    {"handle": "CBCNews",            "name": "CBC News",            "region": "CA"},
    {"handle": "abcnewsaustralia",   "name": "ABC News Australia",  "region": "AU"},
    {"handle": "dwnews",             "name": "DW News",             "region": "DE"},
    {"handle": "TheEconomist",       "name": "The Economist",       "region": "UK"},
    {"handle": "NZZConnect",         "name": "NZZ",                 "region": "CH"},
    {"handle": "aljazeeraenglish",   "name": "Al Jazeera English",  "region": "QA"},
    {"handle": "Reuters",            "name": "Reuters",             "region": "US"},
    {"handle": "60minutes",          "name": "60 Minutes",          "region": "US"},
]
BROADCAST_NOTE = ("Broadcast/institutional media coverage — signals broad mainstream "
                  "awareness. In the diffusion model, broadcast coverage is LATE-stage "
                  "(the crowd has already heard). Attributed data, not Now TrendIn analysis.")
_BROADCAST_CACHE: dict = {}  # shared with _CREATOR_CACHE structure
_CREATOR_CACHE: dict = {}
_CREATOR_TTL = int(os.getenv("CREATOR_TTL_SEC", "21600"))  # 6h


def _creator_recent(handle: str, max_videos: int = 40) -> list:
    """Recent uploads (title/desc/date/url) for a creator handle, cached ~6h."""
    import time as _t
    c = _CREATOR_CACHE.get(handle)
    if c is not None and (_t.time() - c.get("ts", 0) < _CREATOR_TTL):
        return c.get("videos", [])
    vids = []
    try:
        channel_id = resolve_channel_id(handle)
        if channel_id:
            ch = _youtube_get("channels", {"part": "contentDetails", "id": channel_id})
            up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"] if ch and ch.get("items") else None
            if up:
                pl = _youtube_get("playlistItems", {"part": "snippet", "playlistId": up, "maxResults": max_videos})
                for it in (pl or {}).get("items", []):
                    sn = it.get("snippet", {})
                    vid = (sn.get("resourceId") or {}).get("videoId", "")
                    vids.append({
                        "title": sn.get("title", ""),
                        "desc": (sn.get("description", "") or "")[:300],
                        "published": sn.get("publishedAt", ""),
                        "url": f"https://www.youtube.com/watch?v={vid}" if vid else f"https://www.youtube.com/@{handle}",
                    })
    except Exception as e:
        print(f"[creator] {handle} fetch error: {e}")
        return c.get("videos", []) if c else []
    _CREATOR_CACHE[handle] = {"videos": vids, "ts": _t.time()}
    return vids


def creator_coverage(company_name: str, ticker: str) -> Optional[dict]:
    """Combined coverage across all creators for a company/ticker (factual)."""
    name_l = (company_name or "").lower()
    tkr = (ticker or "").upper()
    tkr_re = re.compile(rf"(?<![A-Za-z])\$?{re.escape(tkr)}(?![A-Za-z])") if tkr else None
    creators = []
    for cr in CREATORS:
        vids = _creator_recent(cr["handle"])
        hits = []
        for v in vids:
            hay = f"{v['title']} {v['desc']}"
            if (name_l and name_l in hay.lower()) or (tkr_re and tkr_re.search(hay)):
                hits.append({"title": v["title"], "published": v["published"], "url": v["url"]})
        hits.sort(key=lambda h: h["published"], reverse=True)
        creators.append({
            "name": cr["name"],
            "handle": cr["handle"],
            "channel_url": f"https://www.youtube.com/@{cr['handle']}",
            "covered": bool(hits),
            "count": len(hits),
            "recent": hits[:5],
        })
    any_cov = any(c["covered"] for c in creators)
    return {"creators": creators, "any_covered": any_cov, "note": CREATOR_NOTE}


def collect_creator_risk_signals(conn, max_videos: int = 25) -> int:
    """Write RISK signals (stage-5 retail) for creator videos that mention a
    watchlist company/ticker — making creator content a genuine risk source."""
    now = datetime.now(timezone.utc).isoformat()
    stored = 0
    # Map display name + ticker for matching.
    pairs = [(disp, tkr) for disp, tkr in WATCHLIST_TICKERS.items()] if "WATCHLIST_TICKERS" in globals() else []
    for cr in CREATORS:
        for v in _creator_recent(cr["handle"], max_videos):
            hay = f"{v['title']} {v.get('desc','')}".lower()
            for disp, tkr in pairs:
                tkr_re = re.compile(rf"(?<![a-z])\$?{re.escape(tkr.lower())}(?![a-z])")
                if disp.lower() in hay or tkr_re.search(hay):
                    rk = _risk_key(disp)
                    sig_id = hashlib.md5(f"creator-{cr['handle']}-{rk}-{v['published'][:10]}".encode()).hexdigest()[:16]
                    try:
                        conn.execute(
                            "INSERT OR IGNORE INTO risk_signals (id, risk_topic, risk_display, signal_type, source, diffusion_stage, raw_signal, signal_date, collected_at) VALUES (?,?,?,?,?,?,?,?,?)",
                            (sig_id, rk, disp, "retail_creator", cr["name"], 5,
                             v["title"][:300], (v["published"] or now)[:10], now))
                        stored += 1
                    except Exception as e:
                        print(f"[creator] risk insert err: {e}")
                    break
    conn.commit()
    print(f"  Creator risk signals: {stored}")
    return stored


def _broadcast_recent(handle: str, max_videos: int = 30) -> list:
    """Recent uploads for a broadcast channel handle, cached ~6h (shared cache)."""
    import time as _t
    c = _BROADCAST_CACHE.get(handle)
    if c is not None and (_t.time() - c.get("ts", 0) < _CREATOR_TTL):
        return c.get("videos", [])
    vids = []
    try:
        channel_id = resolve_channel_id(handle)
        if channel_id:
            ch = _youtube_get("channels", {"part": "contentDetails", "id": channel_id})
            up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"] if ch and ch.get("items") else None
            if up:
                pl = _youtube_get("playlistItems", {"part": "snippet", "playlistId": up, "maxResults": max_videos})
                for it in (pl or {}).get("items", []):
                    sn = it.get("snippet", {})
                    vid = (sn.get("resourceId") or {}).get("videoId", "")
                    vids.append({
                        "title": sn.get("title", ""),
                        "desc": (sn.get("description", "") or "")[:300],
                        "published": sn.get("publishedAt", ""),
                        "url": f"https://www.youtube.com/watch?v={vid}" if vid else f"https://www.youtube.com/@{handle}",
                    })
    except Exception as e:
        print(f"[broadcast] {handle} fetch error: {e}")
        return c.get("videos", []) if c else []
    _BROADCAST_CACHE[handle] = {"videos": vids, "ts": _t.time()}
    return vids


def broadcast_coverage(company_name: str, ticker: str) -> Optional[dict]:
    """Combined coverage across all broadcast channels for a company/ticker."""
    name_l = (company_name or "").lower()
    tkr = (ticker or "").upper()
    tkr_re = re.compile(rf"(?<![A-Za-z])\$?{re.escape(tkr)}(?![A-Za-z])") if tkr else None
    channels = []
    for bc in BROADCAST_CHANNELS:
        vids = _broadcast_recent(bc["handle"])
        hits = []
        for v in vids:
            hay = f"{v['title']} {v['desc']}"
            if (name_l and name_l in hay.lower()) or (tkr_re and tkr_re.search(hay)):
                hits.append({"title": v["title"], "published": v["published"]})
        hits.sort(key=lambda h: h["published"], reverse=True)
        channels.append({
            "name": bc["name"],
            "handle": bc["handle"],
            "region": bc.get("region", ""),
            "covered": bool(hits),
            "count": len(hits),
            "recent": hits[:3],
        })
    any_cov = any(c["covered"] for c in channels)
    # Only return channels that actually covered — keep payload lean.
    covered = [c for c in channels if c["covered"]]
    return {"channels": covered, "total_channels": len(BROADCAST_CHANNELS),
            "any_covered": any_cov, "note": BROADCAST_NOTE}


def collect_broadcast_risk_signals(conn, max_videos: int = 20) -> int:
    """Write RISK signals (stage-5 mainstream broadcast) for broadcast channel
    videos mentioning a watchlist company/ticker."""
    now = datetime.now(timezone.utc).isoformat()
    stored = 0
    pairs = [(disp, tkr) for disp, tkr in WATCHLIST_TICKERS.items()] if "WATCHLIST_TICKERS" in globals() else []
    for bc in BROADCAST_CHANNELS:
        for v in _broadcast_recent(bc["handle"], max_videos):
            hay = f"{v['title']} {v.get('desc', '')}".lower()
            for disp, tkr in pairs:
                tkr_re = re.compile(rf"(?<![a-z])\$?{re.escape(tkr.lower())}(?![a-z])")
                if disp.lower() in hay or tkr_re.search(hay):
                    rk = _risk_key(disp)
                    sig_id = hashlib.md5(
                        f"broadcast-{bc['handle']}-{rk}-{v['published'][:10]}".encode()
                    ).hexdigest()[:16]
                    try:
                        conn.execute(
                            "INSERT OR IGNORE INTO risk_signals (id, risk_topic, risk_display, signal_type, source, diffusion_stage, raw_signal, signal_date, collected_at) VALUES (?,?,?,?,?,?,?,?,?)",
                            (sig_id, rk, disp, "broadcast_news", bc["name"], 5,
                             v["title"][:300], (v["published"] or now)[:10], now))
                        stored += 1
                    except Exception as e:
                        print(f"[broadcast] risk insert err: {e}")
                    break
    conn.commit()
    print(f"  Broadcast risk signals: {stored}")
    return stored


# Yahoo Finance (RapidAPI yahoo-finance166) — feeds BOTH pipelines. On the
# trends side, headlines drop into news topic signals via the engine's
# collect_yahoo_finance_news. On the market side (here), the same RapidAPI
# pull is mined for watchlist company mentions and stored as financial_news
# risk signals — so analysts see the same article counted as both an attention
# signal AND a positioning indicator on the company-detail page.
_YF_NEWS_CACHE: dict = {"ts": 0, "items": []}
_YF_NEWS_TTL = 21600  # 6h — same cadence as the trends-side cycle


def _yahoo_finance_news(max_items: int = 100) -> list:
    """Fetch (cached 6h) Yahoo Finance news stream. Shared with the trends side
    where possible — but this is a self-contained pull so the risk pipeline
    doesn't depend on the trend pipeline having run first."""
    import time as _t
    if _YF_NEWS_CACHE["items"] and (_t.time() - _YF_NEWS_CACHE["ts"] < _YF_NEWS_TTL):
        return _YF_NEWS_CACHE["items"]
    key = os.getenv("RAPIDAPI_YF_KEY", "")
    if not key:
        return []
    try:
        from urllib.request import Request, urlopen
        _api("yahoo_finance")
        url = ("https://yahoo-finance166.p.rapidapi.com/api/news/list"
               f"?snippetCount={max_items}&region=US")
        req = Request(url, headers={
            "x-rapidapi-host": "yahoo-finance166.p.rapidapi.com",
            "x-rapidapi-key": key,
            "User-Agent": "NowTrendIn/1.0",
        })
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        stream = (((data.get("data") or {}).get("ntk") or {}).get("stream")) or []
        items = []
        for it in stream:
            content = (it.get("content") or it.get("editorialContent") or {})
            title = content.get("title", "") or ""
            prov = (content.get("provider") or {}).get("displayName", "") or "Yahoo Finance"
            pub = content.get("pubDate") or content.get("displayTime") or ""
            if title:
                items.append({"title": title, "source": prov, "published": pub})
    except Exception as e:
        print(f"  [yahoo_finance risk] fetch error: {e}")
        return _YF_NEWS_CACHE["items"]  # fall back to last cache on error
    _YF_NEWS_CACHE["items"] = items
    _YF_NEWS_CACHE["ts"] = _t.time()
    return items


def collect_yahoo_finance_risk_signals(conn) -> int:
    """Write RISK signals (financial_news) for Yahoo Finance headlines mentioning
    a watchlist company/ticker. Same pattern as broadcast/creator risk signals —
    diffusion_stage=4 (mainstream financial press, ahead of broadcast/retail)."""
    now = datetime.now(timezone.utc).isoformat()
    stored = 0
    pairs = [(disp, tkr) for disp, tkr in WATCHLIST_TICKERS.items()] if "WATCHLIST_TICKERS" in globals() else []
    for it in _yahoo_finance_news(100):
        title = (it.get("title") or "").strip()
        if len(title) < 8:
            continue
        hay = title.lower()
        for disp, tkr in pairs:
            tkr_re = re.compile(rf"(?<![a-z])\$?{re.escape(tkr.lower())}(?![a-z])")
            if disp.lower() in hay or tkr_re.search(hay):
                rk = _risk_key(disp)
                pub = (it.get("published") or now)[:10]
                sig_id = hashlib.md5(
                    f"yfnews-{rk}-{pub}-{title[:60]}".encode()
                ).hexdigest()[:16]
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO risk_signals (id, risk_topic, risk_display, signal_type, source, diffusion_stage, raw_signal, signal_date, collected_at) VALUES (?,?,?,?,?,?,?,?,?)",
                        (sig_id, rk, disp, "financial_news", "Yahoo Finance", 4,
                         title[:300], pub, now))
                    stored += 1
                except Exception as e:
                    print(f"[yahoo_finance] risk insert err: {e}")
                break
    conn.commit()
    print(f"  Yahoo Finance risk signals: {stored}")
    return stored


def alpha_vantage_coverage(ticker: str) -> Optional[dict]:
    """Recent news-article count + average sentiment for a ticker (cached ~6h)."""
    import time as _t
    key = os.getenv("ALPHAVANTAGE_API_KEY", "")
    if not key or not ticker:
        return None
    tkr = ticker.upper()
    cached = _AV_CACHE.get(tkr)
    if cached is not None and (_t.time() - cached.get("ts", 0) < _AV_TTL_SEC):
        return cached.get("data")
    try:
        from urllib.request import urlopen
        from urllib.parse import urlencode
        q = urlencode({"function": "NEWS_SENTIMENT", "tickers": tkr,
                       "sort": "LATEST", "limit": "50", "apikey": key})
        _api("alphavantage")
        with urlopen(f"https://www.alphavantage.co/query?{q}", timeout=8) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
        feed = raw.get("feed") or []
        scores = []
        latest = []
        for art in feed:
            for ts in art.get("ticker_sentiment", []):
                if ts.get("ticker", "").upper() == tkr:
                    try:
                        scores.append(float(ts.get("ticker_sentiment_score", 0)))
                    except (TypeError, ValueError):
                        pass
                    break
            if len(latest) < 5 and art.get("title"):
                latest.append({"title": art.get("title", ""),
                               "source": art.get("source", ""),
                               "published": art.get("time_published", "")})
        n = len(feed)
        avg = round(sum(scores) / len(scores), 3) if scores else None
        label = ("Bullish tone" if (avg or 0) >= 0.15 else
                 "Bearish tone" if (avg or 0) <= -0.15 else "Neutral tone") if avg is not None else "n/a"
        data = {"covered": n > 0, "article_count": n, "avg_sentiment": avg,
                "sentiment_label": label, "recent": latest, "source": "Alpha Vantage",
                "note": AV_NOTE}
    except Exception as e:
        print(f"[alphavantage] {tkr}: {e}")
        return cached.get("data") if cached else None
    _AV_CACHE[tkr] = {"data": data, "ts": _t.time()}
    return data


# ════════════════════════════════════════════════════════════════
# MARKET GRADIENT — the Gradient-Score analog for market factors.
# Same Duality philosophy as the attention Gradient Score, but split on
# DATA TYPE instead of attention diffusion:
#   • Market Detection  (leading / soft)  = what analysts are SAYING + how
#     smart money is POSITIONING, before it's confirmed.
#   • Market Confidence (lagging / hard)  = what the FUNDAMENTALS and PRICE
#     actually reflect.
#   • Dark-Matter analog = Positioning Pressure (the earliest hidden shifts:
#     insider/13F/short-interest moves ahead of price).
# The GAP (Detection − Confidence) = how early/unconfirmed the market move is.
# Measurement only — NEVER buy/sell/risk advice. Tiers describe how unusual the
# positioning is, never what to do about it. Degrades gracefully for macro
# themes that lack ticker-level fundamentals/price.
# ════════════════════════════════════════════════════════════════

MARKET_TIERS = [(80, "ELEVATED"), (60, "ACTIVE"), (40, "BUILDING"),
                (25, "ROUTINE"), (0, "DORMANT")]


def _mclamp(v, lo=0.0, hi=100.0):
    try:
        return max(lo, min(hi, float(v)))
    except (TypeError, ValueError):
        return lo


def compute_market_gradient(payload: dict, diffusion_score: dict,
                            baseline_pos: dict) -> dict:
    """Market Gradient dual-score from the assembled positioning payload."""
    av    = payload.get("alpha_vantage") or {}
    si    = payload.get("short_interest") or {}
    iw    = payload.get("institutional_holdings") or {}
    bene  = payload.get("beneficiary") or {}
    macro = payload.get("macro_leverage") or {}
    cc    = payload.get("creator_coverage") or {}
    bcov  = payload.get("broadcast_coverage") or {}

    # ── Analyst Signal (AS) — what analysts / media are saying (leading) ──
    art = av.get("article_count") or 0
    sent = abs(av.get("avg_sentiment") or 0.0)
    creators_cov = sum(1 for c in (cc.get("creators") or []) if c.get("covered"))
    broadcast_cov = len(bcov.get("channels") or [])
    analyst = _mclamp(math.log1p(art) * 18 + sent * 35
                      + creators_cov * 6 + min(broadcast_cov, 5) * 4)
    has_analyst = bool(art or creators_cov or broadcast_cov)

    # ── Positioning Pressure (PP) — Dark-Matter analog (hidden early shifts) ──
    si_chg = abs(si.get("change_pct") or 0.0)
    inst_chg = abs(iw.get("shares_change_pct") or 0.0)
    pp = _mclamp(si_chg * 4 + inst_chg * 4)
    has_pp = bool(si or (iw and iw.get("available")))

    # ── Baseline Abnormality (BA) — activity vs the item's OWN baseline ──
    ba = _mclamp(baseline_pos.get("score") or 0)

    # ── Fundamentals (FU) — hard financials (beneficiary cycle inflection) ──
    comps = bene.get("components") or {}
    fu = _mclamp(float(comps["cycle_inflection"]) * 100) if "cycle_inflection" in comps else None

    # ── Price Action (PR) — valuation re-rating + 12m return magnitude ──
    li = bene.get("live_inputs") or {}
    pr = None
    parts = []
    if li.get("valuation_rerating") is not None:
        parts.append(_mclamp(float(li["valuation_rerating"]) * 100))
    if li.get("price_return_12m") is not None:
        parts.append(_mclamp(abs(float(li["price_return_12m"])) * 40))
    if parts:
        pr = round(sum(parts) / len(parts), 1)

    # ── Macro Context (MA) — OFR funding stress ──
    ma = None
    stress = ((macro.get("funding_stress") or {}).get("label") or "").lower()
    if stress:
        ma = (85 if ("high" in stress or "severe" in stress)
              else 60 if "moderate" in stress
              else 35 if "mild" in stress else 30)

    # ── Market Detection (leading / soft) ──
    det_parts = []
    if has_analyst: det_parts.append((analyst, 0.40))
    if has_pp:      det_parts.append((pp, 0.35))
    det_parts.append((ba, 0.25))
    wsum = sum(w for _, w in det_parts)
    detection = round(sum(v * w for v, w in det_parts) / wsum, 1) if wsum else ba

    # ── Market Confidence (lagging / hard) ──
    conf_parts = []
    if fu is not None: conf_parts.append((fu, 0.45))
    if pr is not None: conf_parts.append((pr, 0.40))
    if ma is not None: conf_parts.append((ma, 0.15))
    if conf_parts:
        wsum2 = sum(w for _, w in conf_parts)
        confidence = round(sum(v * w for v, w in conf_parts) / wsum2, 1)
        confidence_basis = "hard financials + price"
    else:
        # Macro theme with no ticker-level hard data → confirmation proxy from
        # the diffusion freshness/confidence the base engine already computed.
        confidence = round(_mclamp((diffusion_score.get("components", {}) or {})
                                    .get("confidence_decay")
                                    or diffusion_score.get("confidence_score") or 0), 1)
        confidence_basis = "diffusion confirmation (no ticker fundamentals)"

    avg = (detection + confidence) / 2
    abs_tier = next(name for thr, name in MARKET_TIERS if avg >= thr)
    # ── Deviation-aware tier (recalibration) ───────────────────────────────
    # The absolute composite is baseline-relative and realistically sits ~30-45
    # in normal conditions, so an absolute-only cut left everything in ROUTINE.
    # An item that is genuinely UNUSUAL VS ITS OWN BASELINE is what Market Signal
    # exists to surface — so promote the tier by the baseline-abnormality score
    # (`ba`), using the SAME 25/50/72 thresholds as the topic classification so
    # the two stay consistent. Take the higher of the two (never demote). This
    # surfaces real relative movement; it does NOT manufacture signal — a flat,
    # at-baseline item still reads ROUTINE/DORMANT.
    _dev_tier = ("ELEVATED" if ba >= 72 else "ACTIVE" if ba >= 50
                 else "BUILDING" if ba >= 25 else abs_tier)
    _RANK = {"DORMANT": 0, "ROUTINE": 1, "BUILDING": 2, "ACTIVE": 3, "ELEVATED": 4}
    tier = abs_tier if _RANK.get(abs_tier, 1) >= _RANK.get(_dev_tier, 1) else _dev_tier
    gap = round(detection - confidence, 1)

    components = {
        "analyst_signal":        round(analyst, 1) if has_analyst else None,
        "positioning_pressure":  round(pp, 1) if has_pp else None,
        "baseline_abnormality":  round(ba, 1),
        "fundamentals":          fu,
        "price_action":          pr,
        "macro_context":         ma,
    }
    return {
        "detection":   detection,
        "confidence":  confidence,
        "tier":        tier,
        "gap":         gap,
        "components":  components,
        "confidence_basis": confidence_basis,
        "interpretation": _market_interpretation(tier, gap, detection, confidence),
        "disclaimer": "Measurement of market positioning intensity and the gap "
                      "between leading signals and hard confirmation. Not "
                      "investment advice, not a buy/sell or risk rating.",
    }


_MARKET_TIER_DESC = {
    "ELEVATED": "Positioning is strongly elevated across leading and confirming signals.",
    "ACTIVE":   "Active positioning — signals are clearly above routine levels.",
    "BUILDING": "Positioning is building but not yet broadly elevated.",
    "ROUTINE":  "Activity is in line with this item's normal level.",
    "DORMANT":  "Quiet — little positioning activity relative to baseline.",
}


def _market_interpretation(tier: str, gap: float, det: float, conf: float) -> str:
    base = _MARKET_TIER_DESC.get(tier, "")
    if gap >= 18:
        base += (" Leading signals (analysts + positioning) are running well ahead "
                 "of what fundamentals and price confirm — an early, not-yet-confirmed "
                 "market signal.")
    elif gap <= -18:
        base += (" Fundamentals and price are stronger than the leading signals — the "
                 "move is confirmed in the hard data more than in current positioning.")
    elif abs(gap) < 8:
        base += (" Leading signals and hard confirmation are closely aligned.")
    else:
        base += (" Leading signals are modestly ahead of hard confirmation.")
    return base


def resolve_ticker(topic: str):
    """Resolve a free-text topic to (ticker, display) if it's a company.
    Tries the watchlist first, then a Finnhub symbol search. Returns (None, None)
    if the topic doesn't look like a tradable company."""
    t = (topic or "").strip()
    if not t:
        return None, None
    wl = WATCHLIST_TICKERS if "WATCHLIST_TICKERS" in globals() else {}
    for disp, tkr in wl.items():
        if disp.lower() == t.lower() or (tkr and tkr.lower() == t.lower()):
            return tkr, disp
    key = os.getenv("FINNHUB_API_KEY", "")
    if key:
        try:
            from urllib.request import urlopen
            from urllib.parse import urlencode
            url = f"https://finnhub.io/api/v1/search?{urlencode({'q': t, 'token': key})}"
            with urlopen(url, timeout=8) as r:
                data = json.loads(r.read().decode("utf-8"))
            for res in (data.get("result") or []):
                sym = res.get("symbol", "")
                if sym and "." not in sym and res.get("type") == "Common Stock":
                    return sym, res.get("description") or t
        except Exception as e:
            print(f"[resolve_ticker] {t}: {e}")
    return None, None


def market_signal_for_company(ticker: str, display: str, db_path: str = DB_PATH) -> Optional[dict]:
    """Assemble the FULL market data for a company on demand and compute its
    Market Signal — the SAME pipeline the Market section uses. Lets the Grade
    tool show a market read for a company that is identical to the Market tab.
    Does NOT record a baseline cycle (grading must not pollust history)."""
    if not ticker:
        return None
    payload: dict = {}
    try:
        sus = compute_sustainability(ticker)
        if sus:
            sus["ticker"] = ticker
            payload["sustainability"] = sus
    except Exception as e:
        print(f"[mscompany] sustainability {ticker}: {e}")
    try:
        cc = creator_coverage(display, ticker)
        if cc: payload["creator_coverage"] = cc
        bc = broadcast_coverage(display, ticker)
        if bc: payload["broadcast_coverage"] = bc
    except Exception:
        pass
    try:
        av = alpha_vantage_coverage(ticker)
        if av: payload["alpha_vantage"] = av
    except Exception:
        pass
    try:
        import finra_data
        si = finra_data.short_interest(ticker)
        if si: payload["short_interest"] = si
    except Exception:
        pass
    try:
        import whalewisdom_data
        iw = whalewisdom_data.institutional_holdings(ticker)
        if iw and iw.get("available"): payload["institutional_holdings"] = iw
    except Exception:
        pass
    try:
        import trend_beneficiary_wire as _tbw
        bene = _tbw.score_company_beneficiary(ticker, display)
        if bene: payload["beneficiary"] = bene
    except Exception:
        pass
    try:
        import ofr_stfm
        payload["macro_leverage"] = ofr_stfm.leverage_snapshot()
    except Exception:
        pass
    try:
        import market_signal_engine as _mse
        sig_summary = {"stage_counts": {}, "venue_count": 0, "newest_age_hours": None}
        mcomps = _mse.assemble_market_components(payload, sig_summary)
        item_key = _risk_key(display)
        mkt = _mse.apply_market_signal(item_key, display, mcomps,
                                       record_this_cycle=False, db_path=db_path)
        _sus = payload.get("sustainability") or {}
        _lh = _sus.get("sector_adjusted_score") or _sus.get("score")
        if _lh is not None:
            mkt["leverage_health"] = round(float(_lh), 0)
        return {"available": True, "ticker": ticker, "display": display,
                "market_gradient": mkt, "payload": payload}
    except Exception as e:
        print(f"[mscompany] signal {ticker}: {e}")
        return None


def score_all_risks(db_path: str = DB_PATH) -> int:
    """Score every risk topic with recent signals and persist risk_scores."""
    init_risk_db(db_path)
    conn = db_compat.connect(db_path)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    rows = conn.execute(
        "SELECT DISTINCT risk_topic, risk_display FROM risk_signals WHERE collected_at >= ?",
        (cutoff,),
    ).fetchall()
    # Global gate: are the downstream (consumer/media/retail, stage ≥3) collectors
    # actually producing data this window? If not, narratives must NOT claim
    # "no public awareness" — they only know the early stages were looked at.
    try:
        _late = conn.execute(
            "SELECT COUNT(*) c FROM risk_signals WHERE diffusion_stage >= 3 AND collected_at >= ?",
            (cutoff,),
        ).fetchone()
        retail_active = bool((_late["c"] if _late else 0))
    except Exception:
        retail_active = False

    scored = 0
    _av_hits = 0
    for row in rows:
        topic = row["risk_topic"]
        display = row["risk_display"] or topic
        sig_rows = conn.execute(
            "SELECT diffusion_stage, signal_date, source FROM risk_signals WHERE risk_topic = ? AND collected_at >= ?",
            (topic, cutoff),
        ).fetchall()
        signals = [{"diffusion_stage": sr["diffusion_stage"], "filing_date": sr["signal_date"]} for sr in sig_rows]
        score = compute_risk_gradient(signals)
        # Source provenance — the audit trail of which legal sources contributed.
        provenance = " · ".join(sorted({sr["source"] for sr in sig_rows if sr["source"]}))
        maturity, maturity_note = _risk_maturity(display)
        # Abnormal-vs-own-baseline (computed BEFORE inserting this cycle's row,
        # so the history reflects only prior cycles).
        base = _compute_baseline(conn, topic, float(score["total_signals"] or 0))

        # ── Positioning engine (baseline-relative, the primary "Other" score) ──
        current_by_stage = {}
        for sr in sig_rows:
            st = sr["diffusion_stage"] or 3
            current_by_stage[st] = current_by_stage.get(st, 0) + 1
        positioning_record_cycle(conn, topic, current_by_stage)   # record THIS cycle first
        pos = compute_positioning_score(conn, topic, current_by_stage)  # baseline excludes it
        narr = positioning_narrative(display, pos, retail_active)
        positioning_payload = {
            "positioning_score": pos["score"],
            "classification":    pos["classification"],
            "percent_delta":     pos.get("percent_delta"),
            "baseline_cycles":   pos["baseline_cycles"],
            "sufficient_baseline": pos["sufficient_baseline"],
            "stage_z":           pos.get("stage_z", {}),
            "headline":          narr["headline"],
            "narrative":         narr["body"],
            "early_signal":      narr["fire_early_signal"],
            "tone":              narr["tone"],
            "retail_collectors_active": retail_active,
            "definition":        POSITIONING_DEFINITION,
            "diffusion": {STAGE_LABELS[s]: {"count": current_by_stage.get(s, 0),
                                            "z": pos.get("stage_z", {}).get(s)} for s in range(1, 6)},
        }

        # ── Financial Sustainability (factual fundamentals) for watchlist companies ──
        ticker = WATCHLIST_TICKERS.get(display)
        if ticker:
            try:
                sus = compute_sustainability(ticker)
                if sus:
                    sus["ticker"] = ticker
                    positioning_payload["sustainability"] = sus
            except Exception as _se:
                print(f"[sustainability] {display}: {_se}")
            # Meet Kevin retail-attention coverage (data point, not advice)
            try:
                mk = meet_kevin_coverage(display, ticker)
                if mk:
                    positioning_payload["meet_kevin"] = mk
            except Exception as _mke:
                print(f"[meetkevin] {display}: {_mke}")
            # Combined creator coverage (Meet Kevin + Andrei Jikh)
            try:
                cc = creator_coverage(display, ticker)
                if cc:
                    positioning_payload["creator_coverage"] = cc
                bc = broadcast_coverage(display, ticker)
                if bc:
                    positioning_payload["broadcast_coverage"] = bc
            except Exception as _cce:
                print(f"[creator] {display}: {_cce}")
            # Alpha Vantage news/retail coverage (article volume + tone)
            try:
                av = alpha_vantage_coverage(ticker)
                if av:
                    positioning_payload["alpha_vantage"] = av
                    _av_hits += 1
            except Exception as _ave:
                print(f"[alphavantage] {display}: {_ave}")
            # FINRA short interest — leverage/distress indicator (over-leveraged names)
            try:
                import finra_data
                si = finra_data.short_interest(ticker)
                if si:
                    positioning_payload["short_interest"] = si
            except Exception as _fie:
                print(f"[finra] {display}: {_fie}")
            # WhaleWisdom 13F — institutional smart-money positioning (late-stage,
            # high-conviction end of the diffusion model). Heavily cached (24h).
            try:
                import whalewisdom_data
                iw = whalewisdom_data.institutional_holdings(ticker)
                if iw and iw.get("available"):
                    positioning_payload["institutional_holdings"] = iw
            except Exception as _iwe:
                print(f"[whalewisdom] {display}: {_iwe}")
            # Trend Beneficiary — SanDisk-pattern exposure: is this company's
            # BUSINESS positioned to benefit from a Now TrendIn detected trend,
            # and is it EARLY or LATE in the cycle? Measurement only, not advice.
            try:
                import trend_beneficiary_wire as _tbw
                bene = _tbw.score_company_beneficiary(ticker, display)
                if bene:
                    positioning_payload["beneficiary"] = bene
            except Exception as _bee:
                print(f"[beneficiary] {display}: {_bee}")

        # Macro leverage context (OFR repo data) — shared across the feed.
        try:
            import ofr_stfm
            positioning_payload["macro_leverage"] = ofr_stfm.leverage_snapshot()
        except Exception as _ofe:
            pass

        # ── MARKET SIGNAL (baseline-relative dual score) — primary market score. ──
        # The Gradient-Score analog for markets: every component scored vs the
        # item's OWN history (z-score), grounded in all our market sources. Records
        # this cycle's components to build the baseline, then scores. CALIBRATING
        # until 3+ cycles of history exist (seeded by the backfill). Measurement
        # only — neutral tiers, never advice.
        try:
            import market_signal_engine as _mse
            # Summarize the item's signals for the shared components.
            _venues = len({sr["source"] for sr in sig_rows if sr["source"]})
            _newest_age = None
            try:
                _dates = [datetime.fromisoformat((sr["signal_date"] or "")[:19])
                          for sr in sig_rows if sr["signal_date"]]
                if _dates:
                    _newest_age = (datetime.now(timezone.utc).replace(tzinfo=None)
                                   - max(_dates)).total_seconds() / 3600.0
            except Exception:
                _newest_age = None
            _sig_summary = {"stage_counts": current_by_stage,
                            "venue_count": _venues, "newest_age_hours": _newest_age}
            _mcomps = _mse.assemble_market_components(positioning_payload, _sig_summary)
            mkt = _mse.apply_market_signal(topic, display, _mcomps, conn=conn)
            # Leverage Health (1-100, HIGH = lower debt / healthier balance sheet)
            # from the factual sustainability read. Powers the Leverage Health
            # filter. Only present for companies with balance-sheet data.
            _sus = positioning_payload.get("sustainability") or {}
            _lh = _sus.get("sector_adjusted_score")
            if _lh is None:
                _lh = _sus.get("score")
            if _lh is not None:
                mkt["leverage_health"] = round(float(_lh), 0)
            positioning_payload["market_gradient"] = mkt
        except Exception as _mge:
            print(f"[market_signal] {display}: {_mge}")
            mkt = None

        _det = mkt["detection"] if mkt else score["detection_score"]
        _conf = mkt["confidence"] if mkt else score["confidence_score"]
        _stage = mkt["tier"] if mkt else score["risk_stage"]
        _interp = mkt["interpretation"] if mkt else score["interpretation"]
        _comps = json.dumps(mkt["components"]) if mkt else json.dumps(score["components"])
        # risk_action kept neutral (no buy/sell/hedge advice) — measurement only.
        _action = ""

        conn.execute(
            """INSERT INTO risk_scores
               (id, risk_topic, risk_display, detection_score, confidence_score,
                risk_stage, risk_action, interpretation, components, diffusion,
                total_signals, source_provenance, maturity, maturity_note,
                baseline_signals, baseline_cycles, abnormality, baseline_status,
                positioning_json, scored_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (str(uuid.uuid4())[:24], topic, display,
             _det, _conf,
             _stage, _action, _interp,
             _comps, json.dumps(score["diffusion_breakdown"]),
             score["total_signals"], provenance, maturity, maturity_note,
             base["baseline_signals"], base["baseline_cycles"],
             base["abnormality"], base["baseline_status"],
             json.dumps(positioning_payload),
             datetime.now(timezone.utc).isoformat()),
        )
        scored += 1
    conn.commit()
    conn.close()
    print(f"[risk] scored {scored} risk topics")
    # Report Alpha Vantage coverage health (best-effort; non-critical).
    try:
        import collector_health as _ch
        _ch.log_collector_run("alphavantage", _av_hits,
                              "success" if _av_hits > 0 else "failure", db_path=db_path)
    except Exception:
        pass
    return scored


def _format_risk_row(r) -> dict:
    d = dict(r)
    for f in ("components", "diffusion"):
        if isinstance(d.get(f), str):
            try:
                d[f] = json.loads(d[f])
            except Exception:
                d[f] = {}
    # Plain-English note for the baseline status (emerging vs always-present).
    status = d.get("baseline_status")
    if status:
        d["baseline_note"] = _BASELINE_STATUS_NOTE.get(status, "")
    # ── Positioning payload (baseline-relative) becomes the PRIMARY fields ──
    pj = d.pop("positioning_json", None)
    if pj:
        try:
            p = json.loads(pj) if isinstance(pj, str) else pj
            d.update(p)  # positioning_score, classification, headline, narrative, early_signal, diffusion, definition…
            # Override the legacy diffusion display with the positioning one (counts + z).
            if isinstance(p.get("diffusion"), dict):
                d["diffusion"] = p["diffusion"]
        except Exception:
            pass
    return d


def get_risk_scores(db_path: str = DB_PATH, limit: int = 50) -> dict:
    init_risk_db(db_path)
    conn = db_compat.connect(db_path)
    # first_scored_at drives the tier data-aging waterfall (Consumer ≥24h,
    # Business ≥12h). Prefer the unpruned positioning_history first cycle so the
    # age stays truthful even if risk_scores is ever pruned; fall back to the
    # earliest score row.
    rows = conn.execute(f"""
        SELECT v.*,
               CASE WHEN ph.first_cycle IS NOT NULL AND ph.first_cycle < fs.first_at
                    THEN ph.first_cycle ELSE fs.first_at END AS first_scored_at
        FROM risk_scores v
        INNER JOIN (SELECT risk_topic, MAX(scored_at) m FROM risk_scores GROUP BY risk_topic) l
          ON v.risk_topic = l.risk_topic AND v.scored_at = l.m
        INNER JOIN (SELECT risk_topic, MIN(scored_at) first_at FROM risk_scores GROUP BY risk_topic) fs
          ON v.risk_topic = fs.risk_topic
        LEFT JOIN (SELECT item_key, MIN(cycle_at) first_cycle FROM positioning_history GROUP BY item_key) ph
          ON v.risk_topic = ph.item_key
    """).fetchall()
    conn.close()
    results = [_format_risk_row(r) for r in rows]
    # Rank by the baseline-relative positioning score (anomaly), not raw volume.
    # CALIBRATING items sort below scored ones at equal value via the secondary key.
    results.sort(key=lambda d: (d.get("positioning_score") or d.get("detection_score") or 0,
                                1 if d.get("sufficient_baseline") else 0), reverse=True)
    return {"count": len(results[:limit]), "results": results[:limit]}


def get_risk_detail(risk_topic: str, db_path: str = DB_PATH) -> Optional[dict]:
    init_risk_db(db_path)
    conn = db_compat.connect(db_path)
    row = conn.execute(
        "SELECT * FROM risk_scores WHERE risk_topic = ? ORDER BY scored_at DESC LIMIT 1",
        (_risk_key(risk_topic),),
    ).fetchone()
    conn.close()
    return _format_risk_row(row) if row else None


# ════════════════════════════════════════════════════════════════
# SECTION 8: DEMO
# ════════════════════════════════════════════════════════════════

def run_demo():
    """Demonstrate the Risk Gradient Score with synthetic signals."""
    print("\n" + "="*68)
    print("NOW TRENDIN — FINANCIAL RISK GRADIENT SCORE — DEMO")
    print("="*68)

    # Scenario A: Early risk — smart money positioning, no retail awareness
    scenario_a = [
        {"diffusion_stage": 1, "filing_date": (datetime.now()-timedelta(days=2)).strftime("%Y-%m-%d"), "raw_signal": "insider sell cluster"},
        {"diffusion_stage": 1, "filing_date": (datetime.now()-timedelta(days=3)).strftime("%Y-%m-%d"), "raw_signal": "insider sell"},
        {"diffusion_stage": 1, "filing_date": (datetime.now()-timedelta(days=5)).strftime("%Y-%m-%d"), "raw_signal": "13F reduction"},
        {"diffusion_stage": 2, "filing_date": (datetime.now()-timedelta(days=4)).strftime("%Y-%m-%d"), "raw_signal": "8-K material event"},
        {"diffusion_stage": 2, "filing_date": (datetime.now()-timedelta(days=6)).strftime("%Y-%m-%d"), "raw_signal": "credit spread widening"},
    ]

    # Scenario B: Late risk — loud on YouTube, no early positioning
    scenario_b = [
        {"diffusion_stage": 5, "published": (datetime.now()-timedelta(days=1)).strftime("%Y-%m-%dT12:00:00Z"), "raw_signal": "meetkevin discussed crash"},
        {"diffusion_stage": 5, "published": (datetime.now()-timedelta(days=2)).strftime("%Y-%m-%dT12:00:00Z"), "raw_signal": "GrahamStephan discussed crash"},
        {"diffusion_stage": 4, "filing_date": (datetime.now()-timedelta(days=2)).strftime("%Y-%m-%d"), "raw_signal": "CNBC coverage"},
        {"diffusion_stage": 3, "filing_date": (datetime.now()-timedelta(days=3)).strftime("%Y-%m-%d"), "raw_signal": "reddit chatter"},
    ]

    for name, signals in [("A — EARLY (smart money, no retail)", scenario_a),
                          ("B — LATE (retail loud, no early signal)", scenario_b)]:
        score = compute_risk_gradient(signals)
        print(f"\n── SCENARIO {name} ──")
        print(f"  Detection: {score['detection_score']}  Confidence: {score['confidence_score']}")
        print(f"  Risk Stage: {score['risk_stage']}")
        print(f"  Action: {score['risk_action']}")
        print(f"  Diffusion: {score['diffusion_breakdown']}")
        print(f"  Interpretation: {score['interpretation']}")

    print("\n" + "="*68)
    print("KEY INSIGHT: Scenario A scores HIGHER on a risk basis because")
    print("the alpha is detecting risk BEFORE it's priced in. Scenario B")
    print("(loud retail, no early positioning) correctly scores as 'crowded'.")
    print("="*68)

    print("\n── LEGITIMATE DATA SOURCES IN USE ──")
    for key, src in RISK_DATA_SOURCES.items():
        print(f"  • {src['name']:<28} Stage {src['diffusion_stage']} — {src['access']}")


if __name__ == "__main__":
    run_demo()
