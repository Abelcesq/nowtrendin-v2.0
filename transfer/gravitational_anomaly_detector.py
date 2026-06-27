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

  Each flagged topic gets a score from 0–100 (a MEASUREMENT, not advice):
    85–100 = BREAKOUT (strongest early movement measured)
    70–84  = STRONG SIGNAL (strong movement, not yet mainstream)
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
import db_compat
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
from fastapi import FastAPI, Query, HTTPException, Body, Depends, Header
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

# discovery_collectors.py — open-world, category-agnostic intake (Phase A).
# Surfaces general-culture trends (sports, entertainment, etc.) the seeded tech
# feeds miss, via Google Trends trending-searches + Wikipedia top pageviews.
try:
    import discovery_collectors as _dc
    _DISCOVERY_AVAILABLE = True
    print("[startup] discovery_collectors module loaded — open-world feeds active")
except ImportError:
    _dc = None                   # type: ignore
    _DISCOVERY_AVAILABLE = False
    print("[startup] discovery_collectors.py not found — tech-only intake")

# topic_categories.py — content-category classifier (Sports/Tech/Business/…).
# Metadata only: labels topics for UI navigation, never feeds the Gradient Score.
try:
    from topic_categories import classify_topic as _classify_topic
    _CATEGORIES_AVAILABLE = True
    print("[startup] topic_categories loaded — content-category classification active")
except ImportError:
    _CATEGORIES_AVAILABLE = False
    def _classify_topic(topic, text="", hints=None):   # type: ignore
        return {"category": "general", "label": "General", "confidence": 0.0, "matched": []}

# community_tiers.py — community-LEVEL tier (r/SpaceX expert vs r/all mainstream)
# instead of a fixed per-platform tier. Lets the gradient + tier-migration read
# where a signal actually sits, not just which platform it came from.
try:
    from community_tiers import community_tier as _community_tier
except ImportError:
    def _community_tier(platform, community=""):   # type: ignore
        return "expert" if (platform or "").lower() in ("github", "hackernews") else "mainstream"


def _topic_category(display: str) -> str:
    """Best-effort content category for a topic display name (safe fallback)."""
    try:
        return _classify_topic(display or "")["category"]
    except Exception:
        return "general"

# ── Situation → category routing (drains the news/general catch-all) ──────────────
# A topic_key→category OVERRIDE built from the held-out situation clustering: a
# context-dependent entity (a bare country, a name) is routed by its SITUATION's
# category — "canada" in a hockey situation reads Sports, in an election situation
# reads Politics — which the bare-word lexicon structurally cannot do. Refreshed by a
# background thread (below). DISPLAY-ONLY navigation metadata: it never feeds the
# Gradient Score (no circularity), consistent with the held-out situation layer.
_SITUATION_CAT: dict = {}
SITUATION_CATEGORY_ENABLED = os.getenv("SITUATION_CATEGORY_ENABLED", "1") == "1"
SITUATION_CAT_REFRESH_MIN = int(os.getenv("SITUATION_CAT_REFRESH_MIN", "30"))
_CATCHALL_CATS = ("general", "news", "")

# ── Context → category (drains the UNCLASSIFIED 'general' bucket) ──────────────────
# The bare-word classifier only ever sees the topic STRING, so a context-dependent
# entity ("hokit", "lilly") with no lexicon hit falls through to 'general'. This map
# classifies a topic against its OWN signal HEADLINES (raw_signals.title) — real source
# text the topic actually appeared in — so "hokit" reading "Hokit raises $40M Series B"
# resolves to business. Built by a background thread (below); conservative confidence
# floor so only a confident headline read overrides. DISPLAY-ONLY, non-circular (uses
# source text, never the score).
_CONTEXT_CAT: dict = {}
CONTEXT_CATEGORY_ENABLED = os.getenv("CONTEXT_CATEGORY_ENABLED", "1") == "1"
CONTEXT_CAT_MIN_CONF = float(os.getenv("CONTEXT_CAT_MIN_CONF", "0.35"))


def _category_for(topic_key: str, display: str) -> str:
    """Serve-time category with three context layers, strongest first, all DISPLAY-ONLY
    (no scoring impact, no circularity):
      1. SITUATION category — the topic's co-occurring EVENT context (canada+hockey→sports)
      2. CONTEXT category — the topic's own signal HEADLINES (hokit raises $40M→business)
      3. bare-word lexicon — and finally the honest 'general' bucket if nothing matches."""
    if topic_key:
        if SITUATION_CATEGORY_ENABLED:
            c = _SITUATION_CAT.get(topic_key)
            if c and c not in _CATCHALL_CATS:
                return c
        if CONTEXT_CATEGORY_ENABLED:
            c = _CONTEXT_CAT.get(topic_key)
            if c and c not in _CATCHALL_CATS:
                return c
    return _topic_category(display or "")


def _refresh_situation_categories() -> int:
    """Rebuild the topic_key→category override map from the current situation clustering.
    Best-effort: on any error the previous map is kept (never wiped to empty)."""
    if not SITUATION_CATEGORY_ENABLED:
        return 0
    try:
        import situation_clustering
        conn = get_db()
        try:
            res = situation_clustering.category_map_from_db(
                conn, gate=_is_quality_topic, categorizer=_topic_category)
        finally:
            try:
                conn.close()
            except Exception:
                pass
        new_map = res.get("map", {})
        if new_map:
            global _SITUATION_CAT
            _SITUATION_CAT = new_map
        print(f"[situation-cat] refreshed: {len(new_map)} topic→category overrides "
              f"from {res.get('situations', 0)} situations")
        return len(new_map)
    except Exception as e:
        print(f"[situation-cat] refresh skipped: {e}")
        return 0


def _refresh_context_categories(window_hours: int = 120, max_rows: int = 200000,
                                heads_per_topic: int = 6) -> int:
    """Rebuild the topic_key→category map from each topic's own signal HEADLINES.
    Joins topic_signals→raw_signals for recent titles, aggregates up to N per topic, and
    classifies with the headline text as context. Only a SPECIFIC category above the
    confidence floor is kept (catch-all results are dropped so the bare lexicon still
    governs them). Best-effort: previous map kept on error. Display-only."""
    if not CONTEXT_CATEGORY_ENABLED:
        return 0
    try:
        from topic_categories import classify_topic
        from collections import defaultdict
        conn = get_db()
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=window_hours)).isoformat()
            rows = conn.execute(
                "SELECT ts.topic_key AS tk, ts.topic AS topic, rs.title AS title "
                "FROM topic_signals ts JOIN raw_signals rs ON rs.id = ts.signal_id "
                "WHERE ts.extracted_at >= ? AND rs.title IS NOT NULL AND rs.title <> '' "
                "ORDER BY ts.extracted_at DESC LIMIT ?",
                (cutoff, int(max_rows))).fetchall()
        finally:
            try:
                conn.close()
            except Exception:
                pass
        heads, disp = defaultdict(list), {}
        for r in rows:
            tk = r["tk"] if hasattr(r, "keys") else r[0]
            if not tk:
                continue
            if tk not in disp:
                disp[tk] = (r["topic"] if hasattr(r, "keys") else r[1]) or tk.replace("_", " ")
            lst = heads[tk]
            if len(lst) < heads_per_topic:
                lst.append((r["title"] if hasattr(r, "keys") else r[2]) or "")
        out = {}
        for tk, titles in heads.items():
            try:
                res = classify_topic(disp.get(tk, ""), text=" | ".join(titles))
            except Exception:
                continue
            cat = res.get("category")
            if cat and cat not in _CATCHALL_CATS and res.get("confidence", 0) >= CONTEXT_CAT_MIN_CONF:
                out[tk] = cat
        if out:
            global _CONTEXT_CAT
            _CONTEXT_CAT = out
        print(f"[context-cat] refreshed: {len(out)} topic→category from headlines "
              f"({len(heads)} topics with titles)")
        return len(out)
    except Exception as e:
        print(f"[context-cat] refresh skipped: {e}")
        return 0


def _situation_category_loop():
    """Daemon: refresh the situation→ and context→category maps on startup, then every
    N minutes. Both are display-only catch-all drains (event-context + headline-context)."""
    import time as _t
    while True:
        try:
            _refresh_situation_categories()
        except Exception as e:
            print(f"[situation-cat] loop error: {e}")
        try:
            _refresh_context_categories()
        except Exception as e:
            print(f"[context-cat] loop error: {e}")
        _t.sleep(max(5, SITUATION_CAT_REFRESH_MIN) * 60)

# dual_pathway.py — Phase C recalibration. Mainstream-origin topics (consumer
# culture surfaced by discovery feeds) are scored by attention MAGNITUDE +
# velocity instead of the expert-gradient that is structurally ~0 for them.
# Expert-origin (tech) topics are untouched — the moat is preserved.
try:
    import dual_pathway as _dual
    _DUAL_PATHWAY = os.getenv("DUAL_PATHWAY", "1") == "1"
    print(f"[startup] dual_pathway loaded — mainstream-magnitude detection {'ON' if _DUAL_PATHWAY else 'OFF'}")
except ImportError:
    _dual = None  # type: ignore
    _DUAL_PATHWAY = False
    print("[startup] dual_pathway.py not found — gradient-only detection")

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

try:
    import financial_risk_gradient as risk
    _RISK_AVAILABLE = True
    print("[startup] financial_risk_gradient loaded — Risk Gradient Score active")
except Exception as _risk_exc:
    _RISK_AVAILABLE = False
    print(f"[startup] financial_risk_gradient unavailable: {_risk_exc}")

try:
    import google_trends_validation as accuracy
    _ACCURACY_AVAILABLE = True
    print("[startup] google_trends_validation loaded — Accuracy Ledger active")
except Exception as _acc_exc:
    _ACCURACY_AVAILABLE = False

try:
    import accuracy_ledger_enhanced as ledger_plus
    _LEDGER_PLUS_AVAILABLE = True
    print("[startup] accuracy_ledger_enhanced loaded — honest-denominator ledger active")
except Exception as _lpe:
    _LEDGER_PLUS_AVAILABLE = False
    print(f"[startup] accuracy_ledger_enhanced unavailable: {_lpe}")

try:
    import market_accuracy_ledger as market_ledger
    _MARKET_LEDGER_AVAILABLE = True
    print("[startup] market_accuracy_ledger loaded — Money Gradient track record (EOD-price validated)")
except Exception as _mle:
    _MARKET_LEDGER_AVAILABLE = False
    print(f"[startup] market_accuracy_ledger unavailable: {_mle}")

try:
    import crypto_money_gradient as crypto_engine
    _CRYPTO_AVAILABLE = True
    print(f"[startup] crypto_money_gradient loaded — Crypto Money Gradient (CRYPTO_SIGNAL={crypto_engine.CRYPTO_SIGNAL})")
except Exception as _cme:
    _CRYPTO_AVAILABLE = False
    print(f"[startup] crypto_money_gradient unavailable: {_cme}")

try:
    import crypto_accuracy_ledger as crypto_ledger
    _CRYPTO_LEDGER_AVAILABLE = True
    print("[startup] crypto_accuracy_ledger loaded — Crypto Money Gradient track record (coin-price validated)")
except Exception as _cle:
    _CRYPTO_LEDGER_AVAILABLE = False
    print(f"[startup] crypto_accuracy_ledger unavailable: {_cle}")


def _apify_sweep_budget_ok(reserve_usd: float = None) -> dict:
    """Budget guard for the held-out accuracy-ledger sweep. The sweep shares the Apify
    account with the MAIN collection pipeline, so it must never spend the last dollars
    collection needs. Reads live Apify monthly usage vs the account cap and returns
    {ok, used, cap, reserve}: the sweep may spend paid Trends fetches only while
    used < cap - reserve. Fail-OPEN (ok=True) when usage can't be read — a sweep fetch is
    cheap ($0.001/result) and a monitoring hiccup must not silently stall the moat's
    measurement. Reserve = LEDGER_APIFY_RESERVE_USD (default 20)."""
    import os as _os
    reserve = reserve_usd if reserve_usd is not None else float(_os.getenv("LEDGER_APIFY_RESERVE_USD", "20"))
    tok = _os.getenv("APIFY_TOKEN")
    if not tok:
        return {"ok": True, "used": None, "cap": None, "reserve": reserve, "note": "no APIFY_TOKEN"}
    try:
        import requests as _rq
        r = _rq.get(f"https://api.apify.com/v2/users/me/limits?token={tok}", timeout=12)
        d = (r.json() or {}).get("data", {})
        used = d.get("current", {}).get("monthlyUsageUsd")
        cap = d.get("limits", {}).get("maxMonthlyUsageUsd")
        if used is None or cap is None:
            return {"ok": True, "used": used, "cap": cap, "reserve": reserve, "note": "usage unreadable"}
        return {"ok": float(used) < (float(cap) - reserve), "used": float(used),
                "cap": float(cap), "reserve": reserve}
    except Exception as e:
        return {"ok": True, "used": None, "cap": None, "reserve": reserve, "note": f"read error: {e}"}


def _record_top_detections(limit=20, min_detection=None):
    """Log the engine's strongest current detections as PENDING ledger entries
    (starts the clock for every call, not just the winners). Uses each topic's
    true first-seen as the detection date. Idempotent."""
    if not _LEDGER_PLUS_AVAILABLE:
        return 0
    floor = float(min_detection if min_detection is not None
                  else os.getenv("LEDGER_DETECTION_FLOOR", "10"))
    conn = get_db(DB_PATH)
    n = 0
    try:
        rows = conn.execute("""
            SELECT v.topic_key, v.topic_display, v.detection_score,
                   COALESCE(lc.first_detected_at, fs.first_at) AS det_date
            FROM velocity_scores v
            INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores GROUP BY topic_key) l
              ON v.topic_key=l.topic_key AND v.scored_at=l.m
            INNER JOIN (SELECT topic_key, MIN(scored_at) first_at FROM velocity_scores GROUP BY topic_key) fs
              ON v.topic_key=fs.topic_key
            LEFT JOIN topic_lifecycle lc ON v.topic_key=lc.topic_key
            WHERE v.detection_score >= ?
            ORDER BY v.detection_score DESC LIMIT ?
        """, (floor, limit)).fetchall()
        import date_utils
        for r in rows:
            # Canonical PRIMARY date (§14): never raw [:10] — to_iso_date tries
            # whole-string formats and returns None (skip) on an unparseable value
            # rather than a corrupt/guessed date, so the ledger's detection_date
            # (a canonical date-semantic column) stays a clean YYYY-MM-DD.
            dd = date_utils.to_iso_date(r["det_date"])
            if not dd:
                continue
            ledger_plus.record_detection(r["topic_key"], r["topic_display"], dd,
                                         r["detection_score"] or 0, conn=conn)
            n += 1
    except Exception as e:
        print(f"[ledger] record_top_detections error: {e}")
    finally:
        conn.close()
    print(f"[ledger] recorded {n} pending detections")
    return n
    print(f"[startup] google_trends_validation unavailable: {_acc_exc}")

try:
    import x_signal_module as xsig
    _X_AVAILABLE = True
    print("[startup] x_signal_module loaded — X dual-role signal active")
except Exception as _x_exc:
    _X_AVAILABLE = False
    print(f"[startup] x_signal_module unavailable: {_x_exc}")

try:
    import ai_grade
    _AI_GRADE_AVAILABLE = True
    print("[startup] ai_grade loaded — AI Grade (Perplexity+Claude) active")
except Exception as _ag_exc:
    _AI_GRADE_AVAILABLE = False
    print(f"[startup] ai_grade unavailable: {_ag_exc}")

try:
    import grade_agent
    _GRADE_AGENT_AVAILABLE = True
    print("[startup] grade_agent loaded — pool-first grading (measured Gradient + N)")
except Exception as _gax:
    _GRADE_AGENT_AVAILABLE = False
    print(f"[startup] grade_agent unavailable: {_gax}")

try:
    import market_signal_diagnostic as _mkt_diag
    import trend_signal_diagnostic as _trd_diag
    _DIAG_AVAILABLE = True
    print("[startup] signal diagnostics loaded — market + trend calibration agents")
except Exception as _dx:
    _DIAG_AVAILABLE = False
    print(f"[startup] signal diagnostics unavailable: {_dx}")

try:
    import news_collectors as _news
    _NEWS_AVAILABLE = True
    print("[startup] news_collectors loaded — GDELT (Stage 4) media coverage active")
except Exception as _nc_exc:
    _NEWS_AVAILABLE = False
    print(f"[startup] news_collectors unavailable: {_nc_exc}")

try:
    import ofr_stfm
    _OFR_AVAILABLE = True
    print("[startup] ofr_stfm loaded — OFR leverage/funding-stress overlay active")
except Exception as _ofe:
    _OFR_AVAILABLE = False
    print(f"[startup] ofr_stfm unavailable: {_ofe}")

try:
    import collector_health as _health
    _HEALTH_AVAILABLE = True
    print("[startup] collector_health loaded — pipeline safety net active")
except Exception as _h_exc:
    _HEALTH_AVAILABLE = False
    print(f"[startup] collector_health unavailable: {_h_exc}")

try:
    import monitoring_agents as _monitor
    _MONITOR_AVAILABLE = True
    print("[startup] monitoring_agents loaded — Source Watchdog + Pipeline Integrity active")
except Exception as _mon_exc:
    _MONITOR_AVAILABLE = False
    print(f"[startup] monitoring_agents unavailable: {_mon_exc}")


def _log_health(name, count, status="success", conn=None):
    """Best-effort collector-health logging (never breaks a collection cycle)."""
    if not _HEALTH_AVAILABLE:
        return
    try:
        _health.log_collector_run(name, count or 0, status, db_path=DB_PATH, conn=conn)
    except Exception as _le:
        print(f"[health] log error {name}: {_le}")


def _count_api(source, n=1, conn=None):
    """Best-effort external-API call counter (usage/cost monitoring)."""
    if not _HEALTH_AVAILABLE:
        return
    try:
        _health.log_api_call(source, n, db_path=DB_PATH, conn=conn)
    except Exception:
        pass

# ── Generic / evergreen topics ────────────────────────────────────
# Categories too broad to be an actionable emerging trend (like generic "ai"
# or "software development"). They are perpetually present, so a high score on
# them is noise, not a signal. Filtered out of the served feed. Override the
# list via env GENERIC_TOPICS (comma-separated) or disable with
# GENERIC_TOPIC_FILTER=0.
GENERIC_TOPICS = {
    t.strip().lower() for t in os.getenv(
        "GENERIC_TOPICS",
        "ai,artificial intelligence,software,software development,software engineering,"
        "technology,tech,programming,coding,developer,development,computer,computers,"
        "machine learning,data,data science,startup,startups,business,internet,web,"
        "app,apps,application,cloud,security,open source,framework,library,api,"
        "news,update,updates,release,product,company,market,markets,money,finance,"
        "list,setup,across,structured,guide,tutorial,overview,intro,introduction,"
        "tips,best practices,how to,review,comparison,example,examples"
    ).split(",") if t.strip()
}


def _is_generic_topic(topic: str) -> bool:
    if os.getenv("GENERIC_TOPIC_FILTER", "1") != "1":
        return False
    return (topic or "").strip().lower() in GENERIC_TOPICS


# ── Platform Tiers ────────────────────────────────────────────────
# NICHE = expert communities where trends originate (high gradient weight)
# MAINSTREAM = general communities where trends arrive later (low gradient weight)

NICHE_SUBREDDITS = [
    # ── Tech / AI (original core) ──
    "LocalLLaMA", "MachineLearning", "artificial", "singularity",
    "ChatGPT", "ClaudeAI", "OpenAI", "StableDiffusion",
    "SideProject", "startups", "Entrepreneur", "programming",
    "learnprogramming", "devops", "Python", "datascience",
    "LanguageTechnology", "computervision", "reinforcementlearning",
    # ── Sports — devotee communities where sports narratives originate.
    #    Added 2026-06-11: the niche array was 100% tech, so non-tech topics
    #    had niche_ratio≈0 → Gradient Strength≈0 → could never score as early
    #    signal (FIFA World Cup invisible while it was actively underway).
    #    "Niche" is per-domain: r/soccer is the devotee tier vs r/news. ──
    "soccer", "worldcup", "nfl", "nba", "baseball",
    # ── Culture / entertainment devotee communities ──
    "movies", "television", "popculturechat",
]
MAINSTREAM_SUBREDDITS = [
    "technology", "Futurology", "worldnews", "science",
    "todayilearned", "explainlikeimfive", "news",
    # General-audience arrival tier for the sports/culture domains above.
    "sports", "entertainment",
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
# A single signal this strong (log1p of ~20,000 views/traffic) is its own
# evidence — a mass-attention discovery entity (e.g. a 777K-view Wikipedia
# article) qualifies for scoring even below the multi-mention count floor.
HIGH_MAGNITUDE_ENG = 9.9
# Catch-all CORROBORATION floor (de-congests the 'news'/general catch-all).
# A topic that classifies into the catch-all must be carried by at least this
# many DISTINCT sources to be scored — single-source single-mention noise
# (foreign hashtag spam, number fragments, "forget subscribe channel") is the
# bulk of catch-all congestion. This is a SOURCE-corroboration floor, NOT a raw
# post-volume floor: 500 raw posts would admit ~1 topic in 200k and would gate
# on absolute size (breaking early detection), whereas distinct-source breadth
# is platform-agnostic and already how the gradient measures mainstreaming.
# HARD EXEMPTIONS (never dropped — moat protection, backtest-verified 0 loss):
#   • any expert-tier signal (early niche-community signals are the moat)
#   • high-magnitude single signal (mass attention is its own evidence)
#   • any topic already in accuracy_ledger / pending_detections (a tracked call)
# Set to 0 or 1 to DISABLE the floor (safe rollback).
CATCHALL_MIN_SOURCES = int(os.getenv("CATCHALL_MIN_SOURCES", "2"))
_CATCHALL_CATS = ("news", "general", "")

# Anomaly thresholds
FIRST_TIMER_THRESHOLD  = 0.35   # 35% of commenters new to subreddit
GRADIENT_RATIO_THRESHOLD = 4.0  # niche density 4x greater than mainstream
ENGAGEMENT_ASYM_RATIO  = 0.30   # comments-to-upvotes ratio above this

# Velocity score thresholds
BREAKOUT_THRESHOLD = 85
STRONG_THRESHOLD   = 70
EMERGING_THRESHOLD = 55
WATCHING_THRESHOLD = 35

# ── Composite weight vectors — SINGLE SOURCE OF TRUTH (scoring_weights.py) ─────
# The Gradient Score composite (G·I·M·D·C·P, N excluded by design) is computed from
# these three vectors. They live in scoring_weights.py so EVERY consumer — this
# primary scorer, ai_grade, enterprise_intel, the calibration recompute — reads the
# SAME numbers; a recalibration changes one file and propagates everywhere. The
# fallback below is value-identical so behavior is preserved if the import ever fails.
try:
    from scoring_weights import (
        WEIGHTS_OVERALL    as _W_OVERALL,
        WEIGHTS_DETECTION  as _W_DETECTION,
        WEIGHTS_CONFIDENCE as _W_CONFIDENCE,
    )
except Exception:
    _W_OVERALL    = {"G": 0.244, "I": 0.222, "M": 0.167, "D": 0.133, "C": 0.078, "P": 0.156}
    _W_DETECTION  = {"G": 0.375, "D": 0.216, "I": 0.182, "M": 0.102, "C": 0.057, "P": 0.068}
    _W_CONFIDENCE = {"I": 0.278, "P": 0.267, "M": 0.222, "G": 0.122, "C": 0.067, "D": 0.044}


def _weighted(comp: dict, weights: dict) -> float:
    """Naive left-to-right accumulation in the weight vector's declared key order.
    Deliberately NOT Python's sum() — sum() uses compensated (Neumaier) summation on
    CPython 3.12+, which differs from the historical inline `a*w1 + b*w2 + ...` chain by
    ~1 ULP and would shift the 2nd decimal on a handful of rows. This explicit fold is
    bit-identical to the prior inline formula (verified across 50k vectors: 0 mismatches),
    so routing weights through scoring_weights.py is a provably zero-score-impact change."""
    s = 0.0
    for k in weights:
        s += comp[k] * weights[k]
    return s


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
# The FULL /scores feed is computed once and cached limit/offset-independently so
# pagination is O(1) slicing. The worker invalidates the cache when fresh scores
# land, so a long TTL is safe and keeps every page instant between cycles.
CACHE_TTL_SCORES_FULL = int(os.getenv("CACHE_TTL_SCORES_FULL", "1800"))  # 30 min
# Prewarm Agent — refreshes the superset caches just under the TTL so the cache
# (in THIS, the request-serving, process) is always hot AND at most this-many
# minutes stale. Set PREWARM_ENABLED=0 to disable.
PREWARM_INTERVAL_MIN = int(os.getenv("PREWARM_INTERVAL_MIN", "25"))
CACHE_TTL_STATS   = 60    # 1 min  — /stats (lightweight but polled frequently)
CACHE_TTL_DETAIL  = 120   # 2 min  — /scores/{topic}
CACHE_TTL_HISTORY = 180   # 3 min  — /history/{topic}
CACHE_TTL_XSIGNAL = 43200 # 12 h   — /signal-x (conserves X post-cap quota)


# ══════════════════════════════════════════════════════════════════
# QUERY LOG — N COMPONENT INFRASTRUCTURE
# Non-blocking async queue for logging which topics appear in results.
# At thousands of concurrent users the log path MUST NOT add latency.
# Background thread drains the queue in batches of up to 100.
# ══════════════════════════════════════════════════════════════════

_query_log_queue: "_queue.Queue" = _queue.Queue(maxsize=10_000)


def _prune_anomaly_log(keep_days: int = 30) -> int:
    """Delete anomaly_log rows older than `keep_days`, preserving confirmed
    ones (was_confirmed=1) since those are the accuracy track record.
    Returns rows deleted."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=keep_days)).isoformat()
    conn = get_db(DB_PATH)
    try:
        cur = conn.execute(
            "DELETE FROM anomaly_log WHERE flagged_at < ? AND COALESCE(was_confirmed,0) = 0",
            (cutoff,),
        )
        deleted = cur.rowcount or 0
        conn.commit()
        if deleted:
            print(f"[prune] anomaly_log: removed {deleted} old unconfirmed rows")
        return deleted
    finally:
        conn.close()


def _prune_velocity_scores(retention_days: int = 365) -> int:
    """Delete velocity_scores rows older than retention_days (canonical 365).

    DATA RETENTION RULE — never delete scores within the 365-day window (extended
    from 90 on 2026-06-24, founder decision). A full year of historical scores is
    required for tracking trend progression, accuracy-ledger validation, and
    calibration. Only rows beyond the retention window are removed. Do NOT change
    this to a count-based prune; count-based deletes valid history whenever a topic
    is scored frequently.
    """
    conn = get_db(DB_PATH)
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()
        cur = conn.execute(
            "DELETE FROM velocity_scores WHERE scored_at < ?",
            (cutoff,),
        )
        deleted = cur.rowcount or 0
        conn.commit()
        if deleted:
            print(f"[prune] velocity_scores: removed {deleted} rows older than {retention_days}d")
        return deleted
    finally:
        conn.close()


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
    nowtrendin_score      REAL,    -- N: platform-tracking frequency (how often the topic is
                                   --    triggered/surfaced as a tracked topic; NOT user demand)

    -- Final composite scores — SIX external components (G·I·M·D·C·P), renormalized
    -- to sum to 1.0. N (platform tracking) is DELIBERATELY EXCLUDED to avoid a
    -- feedback loop (see the composite in score_topic ~line 3012 for live weights —
    -- kept in code only, trade secret). N is stored above as a separate signal.
    overall_score         REAL,    -- Balanced (external only)
    detection_score       REAL,    -- Earliness (external only; G/D weighted highest)
    confidence_score      REAL,    -- Precision (external only; I/P weighted highest)
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
-- Logged every time a topic is SURFACED in an API result (the /scores feed, /anomalies,
-- /trending), an on-demand /scores/{topic} query, or a grade — i.e. platform tracking
-- (NOT a user-demand claim). Powers the N — NowTrendIn component.
-- Written async via a bounded queue; never blocks API responses.
CREATE TABLE IF NOT EXISTS topic_queries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    queried_at  TEXT NOT NULL,
    topic_key   TEXT NOT NULL,
    endpoint    TEXT NOT NULL    -- /scores | /anomalies | /trending | /scores/{key}
);

-- ── SCORE ARCHIVE ────────────────────────────────────────────────
-- Periodic (monthly) research snapshot of the latest score per topic.
-- Retained ~1 year for research/backtesting; survives velocity_scores pruning.
CREATE TABLE IF NOT EXISTS score_archive (
    snapshot_date    TEXT NOT NULL,
    topic_key        TEXT NOT NULL,
    topic_display    TEXT,
    detection_score  REAL,
    confidence_score REAL,
    overall_score    REAL,
    signal_stage     TEXT,
    scored_at        TEXT,
    total_mentions   INTEGER,
    PRIMARY KEY (snapshot_date, topic_key)
);

-- ── 12-MONTH PULL HISTORY ─────────────────────────────────────────
-- A durable daily snapshot of every scored item across BOTH feeds
-- (attention + risk), retained for 12 months. One row per
-- (day, feed, topic). Records the score and the engine timestamp of the
-- pull so movement can be charted and audited over a full year. This is
-- the long-term store; velocity_scores stays short (pruned ~30d).
CREATE TABLE IF NOT EXISTS pull_history (
    snapshot_date    TEXT NOT NULL,
    feed             TEXT NOT NULL,   -- 'attention' | 'risk'
    topic_key        TEXT NOT NULL,
    topic_display    TEXT,
    detection_score  REAL,
    confidence_score REAL,
    overall_score    REAL,            -- positioning_score for the risk feed
    signal_stage     TEXT,
    total_signals    INTEGER,
    scored_at        TEXT,            -- engine timestamp of the pull
    archived_at      TEXT,
    PRIMARY KEY (snapshot_date, feed, topic_key)
);
CREATE INDEX IF NOT EXISTS idx_pull_history_topic ON pull_history (topic_key, snapshot_date);
CREATE INDEX IF NOT EXISTS idx_pull_history_date ON pull_history (snapshot_date);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_topic_signals_key
    ON topic_signals (topic_key, extracted_at);
CREATE INDEX IF NOT EXISTS idx_score_archive
    ON score_archive (snapshot_date, overall_score DESC);
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


_SERVE_PAYLOAD_MIGRATED = False
_BASELINE_COLS_MIGRATED = False


def get_db(path: str = DB_PATH) -> sqlite3.Connection:
    conn = db_compat.connect(path, check_same_thread=False, timeout=30)
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
    # ── Live migration: serve_payload (precomputed calibrated /scores row) ──
    # Postgres-safe + once-per-process (broad except: psycopg2 raises its own
    # error class, not sqlite3.OperationalError, and a failed SELECT aborts the
    # current transaction so we must roll back before the ALTER).
    global _SERVE_PAYLOAD_MIGRATED
    if not _SERVE_PAYLOAD_MIGRATED:
        try:
            conn.execute("SELECT serve_payload FROM velocity_scores LIMIT 1")
            _SERVE_PAYLOAD_MIGRATED = True
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE velocity_scores ADD COLUMN serve_payload TEXT")
                conn.commit()
                _SERVE_PAYLOAD_MIGRATED = True
            except Exception:
                try:
                    conn.rollback()
                except Exception:
                    pass
    # ── Live migration: baseline-relative breadth/magnitude history columns ──
    # Stored each cycle so the dual-pathway can compute mainstreaming as a
    # DEVIATION from the topic's own baseline (fame vs. diffusion).
    global _BASELINE_COLS_MIGRATED
    if not _BASELINE_COLS_MIGRATED:
        for _col, _ddl in (("attention_magnitude",
                            "ALTER TABLE velocity_scores ADD COLUMN attention_magnitude REAL DEFAULT 0"),
                           ("n_mainstream_platforms",
                            "ALTER TABLE velocity_scores ADD COLUMN n_mainstream_platforms INTEGER DEFAULT 0"),
                           # Dual-pathway audit fields — make the news/mainstream
                           # calibration visible & auditable (and surfaceable to clients).
                           ("detection_pathway",
                            "ALTER TABLE velocity_scores ADD COLUMN detection_pathway TEXT DEFAULT 'expert'"),
                           ("mainstream_ratio",
                            "ALTER TABLE velocity_scores ADD COLUMN mainstream_ratio REAL DEFAULT 0"),
                           ("mainstream_breadth",
                            "ALTER TABLE velocity_scores ADD COLUMN mainstream_breadth REAL DEFAULT 0"),
                           ("news_outlets",
                            "ALTER TABLE velocity_scores ADD COLUMN news_outlets INTEGER DEFAULT 0"),
                           ("mainstream_confirmed",
                            "ALTER TABLE velocity_scores ADD COLUMN mainstream_confirmed INTEGER DEFAULT 0"),
                           ("tier_migration",
                            "ALTER TABLE velocity_scores ADD COLUMN tier_migration INTEGER DEFAULT 0")):
            try:
                conn.execute(f"SELECT {_col} FROM velocity_scores LIMIT 1")
            except Exception:
                try:
                    conn.rollback()
                except Exception:
                    pass
                try:
                    conn.execute(_ddl)
                    conn.commit()
                except Exception:
                    try:
                        conn.rollback()
                    except Exception:
                        pass
        _BASELINE_COLS_MIGRATED = True
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

# Phase B — news-filler words that must NEVER anchor (start/end) a topic phrase.
# These are the generic verbs/adverbs that glue headlines together and produce
# the junk n-gram fragments ("announce deal", "announce deal end", "grips north")
# that bloated the topic pool. They are NOT in STOP_WORDS (they're contentful
# mid-phrase) but a topic that begins or ends with one is almost always noise.
NEWS_FILLER = {
    "announce", "announces", "announced", "announcement", "say", "says", "said",
    "report", "reports", "reported", "deal", "deals", "end", "ends", "ended",
    "hit", "hits", "grip", "grips", "set", "sets", "win", "wins", "won", "back",
    "backs", "plan", "plans", "planned", "move", "moves", "call", "calls",
    "called", "show", "shows", "reveal", "reveals", "claim", "claims", "warn",
    "warns", "urge", "urges", "face", "faces", "slam", "slams", "vow", "vows",
    "push", "pushes", "mark", "marks", "hold", "holds", "give", "gives", "find",
    "finds", "told", "tell", "tells", "add", "adds", "put", "puts", "expect",
    "expects", "could", "would", "amid", "latest", "live", "update", "updates",
    "video", "watch", "photos", "news", "today", "week", "year", "day",
    # verbs/nouns that anchor headline fragments ("iran deal signed",
    # "leaders meet", "nuclear talks", "ceo eyes deal")
    "sign", "signs", "signed", "agree", "agrees", "agreed", "agreement",
    "meet", "meets", "met", "talk", "talks", "visit", "visits", "eye", "eyes",
    "seek", "seeks", "launch", "launches", "launched", "unveil", "unveils",
    "reach", "reaches", "reached", "near", "nears", "weigh", "weighs",
}

# Profanity / slurs — never surface as topics in an institutional product.
PROFANITY = {
    "fuck", "fucking", "fucked", "fuckin", "shit", "shitty", "bullshit",
    "bitch", "cunt", "dick", "pussy", "asshole", "bastard", "damn", "crap",
    "piss", "slut", "whore", "nigger", "nigga", "faggot", "retard", "cock",
}

# Common English words that leak through extraction but are not real topics.
# A SINGLE common word is never a meaningful trend (proper nouns / brands /
# multi-word entities / domain terms still pass). Broad set so the filter
# generalises instead of whack-a-mole. The discriminator: "epstein"/"knicks"
# (proper nouns) are NOT here and pass; "level"/"section"/"done" are and drop.
GENERIC_JUNK = {
    # observed junk
    "well","draw","game","games","seen","brings","bring","every","single",
    "favorite","favourite","kids","kid","american","americans","school",
    "schools","lawn","level","section","done","right","always","rich","four",
    "baby","jail","sports","really","people","person","thing","things","stuff",
    # pronouns / determiners / quantifiers
    "everyone","everything","anything","something","nothing","someone","anyone",
    "nobody","somebody","another","other","others","each","both","either",
    "neither","many","much","more","most","some","any","none","several","few",
    # common verbs
    "make","makes","made","making","get","gets","got","go","goes","going",
    "went","come","comes","came","take","takes","took","give","gives","gave",
    "want","wants","need","needs","know","knows","knew","think","thinks",
    "thought","say","says","said","tell","tells","told","look","looks","find",
    "finds","feel","feels","keep","keeps","let","lets","put","puts","mean",
    "means","start","starts","stop","stops","help","helps","try","tries",
    "call","calls","work","works","play","plays","run","runs","move","moves",
    "live","lives","believe","happen","happens","become","becomes","leave",
    "leaves","bring","turn","turns","talk","talks","ask","asks","show","shows",
    # common adjectives / adverbs
    "good","bad","great","best","worst","better","worse","big","small","large",
    "huge","tiny","old","new","young","high","low","long","short","early","late",
    "hard","easy","real","true","false","sure","crazy","weird","funny","nice",
    "cool","hot","cold","full","empty","clean","free","busy","ready","happy",
    "sad","angry","scared","tired","sick","fine","okay","very","really","just",
    "even","still","also","too","quite","rather","pretty","almost","always",
    "never","often","sometimes","usually","maybe","perhaps","actually","simply",
    # generic nouns / time / media
    "guy","guys","man","woman","men","women","boy","girl","lady","kid","baby",
    "lot","lots","way","ways","day","days","today","tonight","week","weekend",
    "month","year","years","time","times","morning","night","story","stories",
    "video","videos","watch","photo","photos","picture","post","posts","thread",
    "comment","comments","news","update","updates","stuff","place","places",
    "home","house","world","life","money","work","job","jobs","love","hate",
    "friend","friends","family","car","cars","food","water","money","part",
    "parts","case","point","points","line","lines","side","fact","facts",
    "idea","ideas","reason","kind","sort","type","number","group","area",
    # stray abbreviations / non-English fragments observed leaking into the feed
    "dept","asi","gov","sen","rep","inc","ltd","corp","mln","bln","pct",
}


# ── Common-word dictionary (generated by _gen_common_words.py from wordfreq) ──
# The ~10k most frequent ENGLISH common words (nouns/verbs/adjectives), with
# proper nouns (countries, demonyms, major geography, key figures) SUBTRACTED so
# real entities ('japan', 'japanese', 'trump') survive. This is what distinguishes
# a generic common word ("suffering", "saying", "exclusive") from an actual trend:
# a single common word is NEVER a trend, no matter how many times it is posted.
# Tech/domain terms are exempted at runtime against DOMAIN_TERMS.
def _load_common_words() -> set:
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "common_words.txt")
        with open(path, encoding="utf-8") as f:
            return {ln.strip().lower() for ln in f if ln.strip()}
    except Exception as _e:
        print(f"[startup] common_words.txt not loaded ({_e}) — common-word filter degraded")
        return set()


COMMON_WORDS = _load_common_words()
print(f"[startup] common-word dictionary: {len(COMMON_WORDS)} words")


def _is_common_word(w: str) -> bool:
    """A frequent English common word that is NOT a domain/tech term — i.e.
    generic vocabulary, never a standalone trend."""
    w = (w or "").strip().lower()
    return w in COMMON_WORDS and w not in DOMAIN_TERMS


# ── Junk classes the SITUATION layer exposed (2026-06-23) — high-precision gates ──
# The co-occurrence clustering made visible two pollutant classes that the per-word view
# hid: (a) multilingual casino/SEO spam, (b) HTML/JSON/code boilerplate n-gram fragments.
# These sets reject them at the ONE gate every consumer shares (extraction, scoring,
# serve, Pipeline Integrity, situation builder). Tuned for PRECISION — verified to reject
# zero real topics (strait of hormuz / bank of japan / diffusion models / giannis … pass).
SPAM_TERMS = {
    "casino", "casinos", "slot", "slots", "slotmachine", "spielautomat", "spielautomaten",
    "sweepstake", "sweepstakes", "sweepnext", "sweepcoins", "pokies", "roulette",
    "blackjack", "jackpot", "jackpots", "freispiel", "freispiele", "bonuscode",
    "auszahlung", "auszahlungsquote", "auszahlungsquoten", "vermittlungsgebuhr",
    "einzahlung", "gewinnchance", "hitnspin", "wagering",
}
# Clause-fragment indicators — in extraction DEBRIS ("reviewer that runs", "years you
# probably") but ~never in a clean noun-phrase topic. Pure connectors (of/the/and/for/in)
# are intentionally EXCLUDED so "bank of japan" / "strait of hormuz" pass.
CLAUSE_FILLER = {
    "that", "you", "your", "such", "have", "has", "having", "will", "this", "these",
    "those", "which", "who", "whom", "whose", "what", "when", "where", "why", "how",
    "been", "being", "were", "into", "than", "then", "very", "just", "even", "they",
    "them", "their", "probably", "cannot", "because", "however", "regarding", "depending",
    "einen", "eine", "einer", "eines", "dem", "des", "les", "une", "diese", "dieser",
}
# Web/structured-data/code boilerplate that leaks from HTML/JSON feeds — reject the
# fragment, keep the real entity.
BOILERPLATE_BIGRAMS = {
    "article date", "article type", "article id", "show article", "related articles",
    "section related", "related article", "show article date", "article date false",
}
BOILERPLATE_TOKENS = {"provenance", "commenter", "commenters", "redaction", "permalink",
                      "breadcrumb", "onlinedynamicbatching"}
MAX_TOPIC_WORDS = 5     # 6+ words = a headline/boilerplate fragment, not a topic
MAX_TOKEN_LEN   = 20    # a 21+ char single token = concatenated junk (onlinedynamicbatching)

# Real CONCEPT PHRASES built entirely from common words — legit topics the all-common-words
# rule would otherwise drop (surfaced by the situation layer: "interest rate", "world cup").
# A whitelist can only ADD recall, never cause a false reject. Extensible; keep curated.
KNOWN_CONCEPT_PHRASES = {
    # economics / markets
    "interest rate", "interest rates", "monetary policy", "fiscal policy", "central bank",
    "rate hike", "rate cut", "rate hikes", "quantitative easing", "yield curve",
    "basis points", "inflation rate", "supply chain", "trade war", "debt ceiling",
    # sports
    "world cup", "champions league", "super bowl", "grand slam", "formula one",
    "premier league", "stanley cup", "world series",
    # tech / AI
    "vector search", "semantic search", "model context protocol", "large language model",
    "world model", "world models", "context window", "machine learning", "deep learning",
    "neural network", "reinforcement learning", "self driving", "quantum computing",
    "artificial intelligence", "retrieval augmented generation", "natural language",
    "computer vision", "language model", "sentence transformers", "context compression",
    # geo / geopolitical entities that are common-word phrases (real topics, not generic)
    "west bank", "gaza strip", "middle east", "south china sea", "north korea",
    "south korea", "hong kong", "new york", "white house", "united nations",
}


def _is_quality_topic(display: str) -> bool:
    """Reject profanity, spam, boilerplate fragments, generic common words, and bare junk
    so the grid reads clean. Applied at extraction AND serve-time (clears the existing pool
    without re-collection) AND by the Pipeline Integrity / situation layers — the ONE shared
    quality gate. Multi-word entities, brands, and domain terms pass.

    The common-word gate separates real trends from everyday vocabulary:
    'japan'/'chatgpt'/'ozempic' pass; 'suffering'/'saying'/'exclusive' do not — and volume
    can never rescue a generic word (the gate ignores signal count)."""
    t = (display or "").strip().lower()
    if not t:
        return False
    # Split on whitespace + underscores (sources emit underscored field-name fragments
    # like "show_article_date"). HYPHENS ARE KEPT INSIDE TOKENS so a hyphenated compound
    # ("computer-vision", "retrieval-augmented-generation") stays ONE unit — splitting it
    # shatters it into common words and the all-common-words rule wrongly drops a real
    # tech topic (an /audit/topics finding: junk rose 20.6%->22.2% on hyphen-split).
    toks = [w for w in re.split(r"[\s_]+", t) if w]
    if any(w in PROFANITY for w in toks):
        return False
    # concatenated-junk token (onlinedynamicbatching) — but a HYPHENATED long token is a
    # legit compound term ("retrieval-augmented-generation"), so exempt it.
    if any(len(w) > MAX_TOKEN_LEN and "-" not in w for w in toks):
        return False
    if any(w in SPAM_TERMS for w in toks):
        return False
    # Known real concept-phrase (recall whitelist) — passes the all-common-words rule.
    # Normalize hyphens/underscores to spaces so "artificial-intelligence" matches.
    if re.sub(r"[\s_\-]+", " ", t) in KNOWN_CONCEPT_PHRASES:
        return True
    if len(toks) == 1:
        w = toks[0]
        if w in DOMAIN_TERMS:
            return True
        # reject curated junk OR any frequent common word — a single common word
        # is never a trend, no matter how many times it is posted.
        return not (w in GENERIC_JUNK or _is_common_word(w))
    # multi-word: reject over-long fragments, clause debris, and web/code boilerplate
    # BEFORE the entity exemptions (a boilerplate n-gram must never pass on a domain token).
    if len(toks) > MAX_TOPIC_WORDS:
        return False
    if any(w in CLAUSE_FILLER for w in toks):
        return False
    if any(w in BOILERPLATE_TOKENS for w in toks):
        return False
    if {f"{toks[i]} {toks[i+1]}" for i in range(len(toks) - 1)} & BOILERPLATE_BIGRAMS:
        return False
    # reject HEADLINE FRAGMENTS anchored by a news-filler verb/noun at either end
    # ("iran deal", "says iran deal", "leaders meet") — the real entity survives as its
    # own unigram. Then keep the phrase UNLESS every token is generic vocabulary.
    if toks[0] in NEWS_FILLER or toks[-1] in NEWS_FILLER:
        return False
    if any(w in DOMAIN_TERMS for w in toks):
        return True
    return not all((w in STOP_WORDS or w in GENERIC_JUNK or _is_common_word(w))
                   for w in toks)


# Capitalized entity runs (FIFA World Cup, New York Knicks, Elon Musk) and
# all-caps acronyms (FIFA, NASA, UFC, NBA) — lightweight NER from headline case.
_ENTITY_RUN = re.compile(
    r'\b([A-Z][\w&.-]*(?:\s+(?:of|the|and|for|&|de|van|der|[A-Z][\w&.-]*)){1,5})')
_ACRONYM = re.compile(r'\b([A-Z]{2,6})(?:\b|\d)')


def _extract_entities(text: str) -> list[str]:
    """Capitalized named entities from ORIGINAL-CASE text — high precision."""
    ents = []
    for m in _ENTITY_RUN.finditer(text):
        run = m.group(1).strip()
        # must contain >= 2 capitalized tokens (a real multi-word entity), not
        # just a Sentence-initial Word.
        caps = sum(1 for w in run.split() if w[:1].isupper())
        if caps >= 2 and 4 <= len(run) <= 60:
            ents.append(run)
    for m in _ACRONYM.finditer(text):
        ac = m.group(1)
        if 2 <= len(ac) <= 6 and ac not in ("THE", "AND", "FOR", "USA", "USB"):
            ents.append(ac)
        elif ac == "USA":
            ents.append(ac)   # keep USA; drop the truly generic ones above
    return ents


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

    # ── Step 0: Capitalized named entities (Phase B, highest quality) ──
    # Pull clean entities ("FIFA World Cup", "Elon Musk", "NASA") from the
    # ORIGINAL-CASE text BEFORE lowercasing, so real entities win over the
    # generic lowercase n-gram fragments built later.
    for ent in _extract_entities(text):
        topics.add(ent.lower())

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
        if cleaned and len(cleaned) >= 3 and _is_quality_topic(cleaned):
            key = _topic_key(cleaned)
            if key not in seen_keys and len(key) >= 3:
                seen_keys.add(key)
                result.append(cleaned)

    # Cap topics per post to limit fragmentation. 12 spawned too many overlapping
    # micro-topics (unigram+bigram+trigram of the same phrase); 8 keeps the most
    # specific candidates while reducing the long tail. Env-tunable.
    return result[:int(os.getenv("MAX_TOPICS_PER_POST", "8"))]


def _clean_term(term: str) -> str:
    """Remove noise from extracted terms."""
    term = term.strip().lower()
    term = re.sub(r'\s+', ' ', term)
    term = re.sub(r'^[\W_]+|[\W_]+$', '', term)
    return term if len(term) >= 3 else ""


# ── Topic consolidation (refinement): map morphological/entity VARIANTS of the
# same trend to ONE canonical key BEFORE scoring, so the dyno scores "japan" once
# instead of scoring "japan" + "japanese" + "japan's" as three separate topics.
# Conservative on purpose — only demonym→country, possessive, and a small
# explicit synonym map (no blind plural/stem stripping, which mis-merges
# "news"→"new", "physics"→"physic").
_DEMONYM_TO_COUNTRY = {
    "american": "america", "british": "britain", "english": "england",
    "scottish": "scotland", "irish": "ireland", "welsh": "wales",
    "french": "france", "german": "germany", "italian": "italy",
    "spanish": "spain", "portuguese": "portugal", "dutch": "netherlands",
    "belgian": "belgium", "swiss": "switzerland", "austrian": "austria",
    "swedish": "sweden", "norwegian": "norway", "danish": "denmark",
    "finnish": "finland", "polish": "poland", "russian": "russia",
    "ukrainian": "ukraine", "greek": "greece", "turkish": "turkey",
    "chinese": "china", "japanese": "japan", "korean": "korea",
    "indian": "india", "pakistani": "pakistan", "vietnamese": "vietnam",
    "thai": "thailand", "filipino": "philippines", "indonesian": "indonesia",
    "malaysian": "malaysia", "israeli": "israel", "iranian": "iran",
    "iraqi": "iraq", "saudi": "saudiarabia", "egyptian": "egypt",
    "mexican": "mexico", "canadian": "canada", "brazilian": "brazil",
    "argentine": "argentina", "argentinian": "argentina", "chilean": "chile",
    "colombian": "colombia", "australian": "australia", "nigerian": "nigeria",
    "kenyan": "kenya", "ethiopian": "ethiopia", "moroccan": "morocco",
}

# Explicit synonym/alias merges (left → canonical right).
_TOPIC_ALIASES = {
    "gpt": "chatgpt", "openai gpt": "chatgpt",
    "us": "united states", "usa": "united states", "u s": "united states",
    "uk": "united kingdom",
    # Geographic fragments: bare "hormuz" is ambiguous (island vs strait).
    # Fold into the unambiguous canonical geographic entity.
    "hormuz": "strait of hormuz",
    # Protocol / acronym: MCP overwhelmingly means Model Context Protocol in this corpus.
    "mcp": "model context protocol",
    # High-profile people — fold FULL NAME onto the surname the feed uses, so
    # "Donald Trump" and "trump" are one topic. Curated/current on purpose
    # (blind surname-stemming would mis-merge common surnames).
    "donald trump": "trump", "president trump": "trump",
    "joe biden": "biden", "kamala harris": "harris", "barack obama": "obama",
    "elon musk": "musk", "vladimir putin": "putin",
    "volodymyr zelensky": "zelensky", "volodymyr zelenskyy": "zelensky",
    "zelenskyy": "zelensky", "benjamin netanyahu": "netanyahu",
    "jerome powell": "powell", "narendra modi": "modi",
    "zohran mamdani": "mamdani", "xi jinping": "xi jinping",
    "keir starmer": "starmer", "emmanuel macron": "macron",
}


def _canonicalize_topic(topic: str) -> str:
    """Fold variants of the same entity to one canonical surface form."""
    t = (topic or "").lower().strip()
    if not t:
        return t
    if t in _TOPIC_ALIASES:
        return _TOPIC_ALIASES[t]
    out = []
    for w in t.split():
        w = w.rstrip("'’")            # strip trailing apostrophe
        if w.endswith("'s") or w.endswith("’s"):
            w = w[:-2]                       # possessive: japan's → japan
        w = _DEMONYM_TO_COUNTRY.get(w, w)    # demonym → country
        out.append(w)
    return " ".join(out).strip() or t


def _topic_key(topic: str) -> str:
    """Normalize topic to a consistent key for grouping, after consolidating
    morphological/entity variants (japanese→japan) so duplicates collapse."""
    key = _canonicalize_topic(topic)
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
    # Phase B: reject phrases ANCHORED by a news-filler word. A topic that
    # begins or ends with "announce"/"deal"/"end"/"says"/... is a headline
    # fragment, not a topic ("announce deal", "deal end", "grips north").
    if words[0] in NEWS_FILLER or words[-1] in NEWS_FILLER:
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


def _reddit_posts_for_sub(reddit, sub_name: str) -> list:
    """Hot posts for one subreddit as plain namespaces (praw only — errors are
    printed per-sub instead of vanishing). NOTE: a public hot.json fallback was
    tried 2026-06-12 and removed the same day: Reddit 403s unauthenticated JSON
    even from residential IPs, so it only burned ~15s/sub in timeouts."""
    from types import SimpleNamespace
    posts = []
    if reddit is not None:
        try:
            for p in reddit.subreddit(sub_name).hot(limit=50):
                posts.append(SimpleNamespace(
                    id=p.id, title=p.title or "", stickied=bool(p.stickied),
                    author=str(p.author) if p.author else "",
                    score=int(p.score or 0),
                    num_comments=int(p.num_comments or 0),
                    upvote_ratio=float(getattr(p, "upvote_ratio", 1.0) or 1.0),
                    permalink=p.permalink or ""))
        except Exception as e:
            print(f"    r/{sub_name}: praw error ({e})")
    return posts


def collect_reddit(conn: sqlite3.Connection) -> int:
    """Collect posts from Reddit and extract topics from each.

    DISABLED unless REDDIT_CLIENT_ID/SECRET are set (2026-06-12, user call:
    API access not secured). When creds land in Heroku config the collector —
    including the sports/culture niche subs — reactivates with no code change."""
    if not (REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET):
        print("  Reddit: disabled — no API credentials (set REDDIT_CLIENT_ID/"
              "SECRET to reactivate)")
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
            posts = _reddit_posts_for_sub(reddit, sub_name)

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
    _count_api("github", conn=conn)
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

                # First-timer: is this repo owner new to this GitHub topic-community?
                gh_owner = full_name.split('/')[0] if full_name else ""
                gh_first = check_author_is_first_timer(conn, gh_owner, "github", gh_topic)

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
                    1 if gh_first else 0, 1,
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
                        1 if gh_first else 0, 1,
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
    _count_api("hackernews", conn=conn)
    cutoff_ts = int(
        (datetime.now(timezone.utc) - timedelta(hours=hours_back)).timestamp()
    )
    total_topic_signals = 0
    now = datetime.now(timezone.utc).isoformat()

    print("  Collecting Hacker News...")

    try:
        # Use /search_by_date, NOT /search: as of 2026-06 the /search endpoint returns 0
        # hits for `points>50` numericFilters (verified live — `points>50` alone → 0 on
        # /search but 5 on /search_by_date), which silently zeroed the HN collector. The
        # by-date endpoint applies the same filters AND surfaces the newest high-signal
        # stories — better for an early-detection feed anyway.
        resp = requests.get(
            "https://hn.algolia.com/api/v1/search_by_date",
            params={
                "tags": "story",
                "numericFilters": f"points>50,created_at_i>{cutoff_ts}",
                "hitsPerPage": 100,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            print(f"  Hacker News: API HTTP {resp.status_code} — 0 signals this cycle")
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

            # First-timer: is this HN author new to the front-page community?
            hn_author = hit.get("author") or ""
            hn_first = check_author_is_first_timer(conn, hn_author, "hackernews", "front_page")

            conn.execute("""
                INSERT OR IGNORE INTO raw_signals VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                sig_id, now, "hackernews", "expert", "front_page",
                title[:500], url, hn_author[:100],
                points, comments,
                round(engagement, 4),
                round(sentiment, 4),
                1 if hn_first else 0, 1, title[:500],
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
                    1 if hn_first else 0, 1,
                ))
                total_topic_signals += 1

        conn.commit()

    except Exception as e:
        print(f"  HN error: {e}")

    print(f"  HN: {total_topic_signals} topic signals")
    return total_topic_signals


def _demojibake(s: str) -> str:
    """Repair text that was UTF-8 encoded but decoded as latin-1/cp1252.

    The realtime-trends actor returns non-Latin scripts (Arabic, etc.) double-
    encoded, e.g. Arabic arrives as 'Ø¨ÙƒØ§Ù„ÙˆØ±ÙŠØ§'. Re-encoding to latin-1 and
    decoding as UTF-8 recovers the original. Pure-ASCII text round-trips
    unchanged. Falls back to the original on any failure."""
    if not s:
        return ""
    try:
        repaired = s.encode("latin-1").decode("utf-8")
        # Only accept the repair if it didn't introduce replacement chars.
        return repaired if "�" not in repaired else s
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def collect_google_trends(conn) -> int:
    """Discover what is trending RIGHT NOW via the Apify realtime-trends actor
    (easyapi/google-realtime-trends-data-scraper). Returns one row per country,
    each a comma-separated keyword list; we fan those out into topic signals so
    they enter the Gradient scoring pipeline.

    Runs every 6h on the scheduler. One actor run (~$0.57) returns all ~125
    countries regardless of how many we keep, so cost is fixed per pull."""
    token = os.getenv("APIFY_TOKEN", "")
    if not token:
        print("  Google Trends: no APIFY_TOKEN — skipping")
        return 0

    # Immutable actor ID (survives a rename); override via env if needed.
    actor = os.getenv("APIFY_REALTIME_ACTOR", "oOHXMAv8kImUCpHff")
    max_terms = int(os.getenv("GOOGLE_TRENDS_MAX_TERMS", "300"))
    per_country_cap = int(os.getenv("GOOGLE_TRENDS_PER_COUNTRY", "10"))
    run_timeout = int(os.getenv("APIFY_REALTIME_TIMEOUT", "120"))

    try:
        from urllib.request import Request, urlopen
        url = (f"https://api.apify.com/v2/acts/{actor}/"
               f"run-sync-get-dataset-items?token={token}")
        # The actor scrapes all countries with default (empty) input.
        req = Request(url, data=b"{}",
                      headers={"Content-Type": "application/json"})
        _count_api("apify_realtime")
        with urlopen(req, timeout=run_timeout) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  Google Trends: actor error: {e}")
        return 0

    # Tally cross-country frequency so the most globally-trending terms win when
    # we cap. Keep per (country, term) provenance for the signal rows.
    from collections import defaultdict
    freq: dict = defaultdict(int)
    occurrences = []  # (country, term, rank_within_country)
    for row in rows:
        country = _demojibake(str(row.get("country") or "")).strip() or "global"
        kw = _demojibake(str(row.get("keywordsText") or ""))
        terms = [t.strip() for t in kw.split(",") if t.strip()]
        for rank, term in enumerate(terms[:per_country_cap]):
            if len(term) < 2 or len(term) > 80:
                continue
            occurrences.append((country, term, rank))
            freq[_topic_key(term)] += 1

    # Cap distinct terms by global frequency (most widely trending first).
    allowed_keys = set()
    for tkey, _ in sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:max_terms]:
        allowed_keys.add(tkey)
    dropped = len(freq) - len(allowed_keys)

    now = datetime.now(timezone.utc).isoformat()
    total_topic_signals = 0
    seen_sig = set()
    for country, term, rank in occurrences:
        tkey = _topic_key(term)
        if tkey not in allowed_keys:
            continue
        # Rank-weighted engagement: earlier in a country's list = stronger.
        weight = max(1, per_country_cap - rank)
        try:
            sentiment = _sentiment.polarity_scores(term)["compound"]
        except Exception:
            sentiment = 0.0
        sig_id = hashlib.md5(f"gt-{country}-{tkey}".encode()).hexdigest()[:16]
        if sig_id in seen_sig:
            continue
        seen_sig.add(sig_id)
        engagement = round(math.log1p(weight * 5), 4)
        try:
            conn.execute(
                "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (sig_id, now, "google_trends", "mainstream", country,
                 term[:500], "https://trends.google.com/trending", "",
                 weight, 0, engagement, round(sentiment, 4), 0, 1, term[:500]),
            )
            t_id = hashlib.md5(f"{sig_id}-{tkey}".encode()).hexdigest()[:16]
            conn.execute(
                "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (t_id, now, term, tkey, sig_id, "google_trends", "mainstream",
                 country, weight, 0, engagement, 0, 1),
            )
            total_topic_signals += 1
        except Exception as e:
            print(f"    GT insert error ({term}): {e}")
    conn.commit()
    print(f"  Google Trends: {len(rows)} countries → {len(allowed_keys)} terms "
          f"({dropped} less-common dropped) → {total_topic_signals} topic signals")
    return total_topic_signals


def collect_mainstream_news(conn, limit: int = 12) -> int:
    """Add a MAINSTREAM-tier coverage signal for the top recent topics, so
    broad/well-covered topics stop reading as niche-only.

    The engine otherwise collects only developer-publishing platforms (all
    niche/expert tier), so gradient_strength had no mainstream denominator and
    every topic looked niche — the "mainstream hasn't found it" distortion.

    Primary source: YouTube Data API (reliable from Heroku; key already set).
    Fallback: GDELT (free/public, but its DOC API frequently 429s from cloud
    IPs, so it's best-effort only). Runs on a slow cadence with a hard cap to
    respect the YouTube daily quota (search ≈ 100 units/call)."""
    if os.getenv("MAINSTREAM_NEWS_ENABLED", "1") != "1":
        return 0
    try:
        rows = conn.execute("""
            SELECT v.topic_key, v.topic_display FROM velocity_scores v
            INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores GROUP BY topic_key) l
              ON v.topic_key = l.topic_key AND v.scored_at = l.m
            WHERE COALESCE(v.total_mentions,0) >= 5
            ORDER BY v.overall_score DESC LIMIT ?
        """, (limit,)).fetchall()
    except Exception as e:
        print(f"  mainstream-news: topic fetch error: {e}")
        return 0

    yt_key = os.getenv("YOUTUBE_API_KEY", "")
    now = datetime.now(timezone.utc).isoformat()
    stored = 0
    for r in rows:
        tkey = r["topic_key"]
        display = r["topic_display"] or tkey.replace("_", " ")
        platform, channel, vol, engagement, raw = None, None, 0, 0.0, ""

        # ── Primary: YouTube (mainstream/consumer) ──
        if yt_key:
            try:
                _count_api("youtube")
                resp = requests.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={"part": "snippet", "q": display, "type": "video",
                            "maxResults": 15, "order": "relevance", "key": yt_key},
                    timeout=10)
                if resp.status_code == 200:
                    items = resp.json().get("items", [])
                    vol = len(items)
                    if vol > 0:
                        platform, channel = "youtube", "search"
                        engagement = round(math.log1p(vol * 2), 4)
                        raw = f"YouTube: {vol} videos for '{display}'"
            except Exception as e:
                print(f"  mainstream-news: youtube error '{display}': {e}")

        # ── Fallback: GDELT (best-effort; often 429s from cloud) ──
        if platform is None and _NEWS_AVAILABLE:
            try:
                sig = _news.collect_gdelt_signal(display)
                if sig and (sig.get("article_count") or 0) > 0:
                    vol = sig["article_count"]
                    platform, channel = "gdelt", "news"
                    engagement = round(math.log1p(vol) + math.log1p((sig.get("source_breadth", 0) or 0) * 2), 4)
                    raw = sig.get("raw_signal", "")[:500]
            except Exception:
                pass

        if platform is None:
            continue
        sig_id = hashlib.md5(f"{platform}-{tkey}-{now[:10]}".encode()).hexdigest()[:16]
        try:
            conn.execute(
                "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (sig_id, now, platform, "mainstream", channel, raw[:500], "", "",
                 vol, 0, engagement, 0.0, 0, 1, raw[:500]),
            )
            t_id = hashlib.md5(f"{sig_id}-{tkey}".encode()).hexdigest()[:16]
            conn.execute(
                "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (t_id, now, display, tkey, sig_id, platform, "mainstream", channel,
                 vol, 0, engagement, 0, 1),
            )
            stored += 1
        except Exception as e:
            print(f"  mainstream-news: insert error '{display}': {e}")
        time.sleep(0.3)
    conn.commit()
    print(f"  Mainstream coverage: {stored}/{len(rows)} topics enriched")
    return stored


# ── News aggregator feeds (NewsAPI.org, NewsAPI.ai, NewsData.io) ──────
# Genuine MAINSTREAM-tier contributors: each article's headline is mined for
# topics that flow into the gradient like any other platform. News is
# deliberately NOT first-timer/dark-matter (it is broad, public, late-stage),
# so a press release can never masquerade as early "dark matter".
#
# Spam/bot authenticity guard: identical or near-identical headlines syndicated
# across many outlets (the classic PR-wire blast) are counted ONCE and flagged
# non-organic, so manufactured breadth cannot inflate the signal. Known wire/PR
# and aggregator domains are also marked non-organic.
_NEWS_SPAM_SOURCES = {
    "globenewswire", "prnewswire", "businesswire", "accesswire", "newsfile",
    "ein presswire", "einpresswire", "pr newswire", "marketscreener",
    "newsbtc", "24-7 press release", "ad hoc news",
}

# INTEGRITY ALLOWLIST (hard rule): the news aggregators (newsapi.org/.ai,
# newsdata.io) and Yahoo Finance surface a broad pool that can include
# low-quality outlets. NowTrendIn sells to hedge funds, banks, and businesses —
# client trust depends on only ingesting REPUTABLE, authoritative publishers.
# A blocklist only catches named spam; this allowlist guarantees provenance.
# Matched as a substring of the (lowercased) source name. Extend deliberately —
# adding a source here is asserting it meets the institutional-grade bar.
_NEWS_REPUTABLE_SOURCES = {
    # Wire services / agencies (gold standard)
    "reuters", "associated press", "ap news", "bloomberg", "agence france",
    "afp", "dow jones", "pa media", "press association",
    # Financial press
    "wall street journal", "wsj", "financial times", "ft.com", "barron",
    "marketwatch", "cnbc", "the economist", "forbes", "fortune", "morningstar",
    "investing.com", "investopedia", "kiplinger", "the motley fool", "moody",
    "s&p global", "fitch", "yahoo finance", "yahoo! finance",
    # Central banks / official institutions (primary macro sources)
    "federal reserve", "the fed", "ecb", "european central bank", "fomc",
    # National / international press of record
    "new york times", "nytimes", "washington post", "the guardian", "bbc",
    "npr", "pbs", "the times", "los angeles times", "usa today", "axios",
    "politico", "the atlantic", "the new yorker", "national public radio",
    "abc news", "cbs news", "nbc news", "msnbc", "cnn", "sky news",
    "al jazeera", "deutsche welle", "dw.com", "france 24", "nhk", "cbc",
    "the telegraph", "the independent", "newsweek", "time",
    # Spanish / international press of record
    "el país", "el pais", "elpais", "cinco días", "cinco dias", "cincodias",
    # Reputable tech / science press
    "techcrunch", "the verge", "ars technica", "wired", "mit technology",
    "ieee", "nature", "science", "the information", "engadget", "venturebeat",
    "zdnet", "cnet", "protocol",
    # Multi-source aggregator (reputable-filtered upstream)
    "currents",
}

# Default ON — the integrity standard. Set NEWS_REPUTABLE_ONLY=0 only to debug.
_NEWS_REPUTABLE_ONLY = os.getenv("NEWS_REPUTABLE_ONLY", "1") == "1"


def _is_reputable_source(source: str) -> bool:
    """True if the publisher is on the vetted reputable allowlist."""
    s = (source or "").lower().strip()
    if not s:
        return False
    return any(rep in s for rep in _NEWS_REPUTABLE_SOURCES)


def _news_norm_title(t: str) -> str:
    return " ".join((t or "").lower().split())[:140]


# Provenance weighting (the integrity balance the founder asked for):
#   reputable  → full weight, enters corpus normally.
#   unverified → admitted but QUARANTINED at ~1% weight; CANNOT meaningfully move
#                a score alone. Promoted to ~10% ONLY when independently
#                corroborated (see corroborate_unverified_news). Routed by path:
#                reputable/curated corroboration → mainstream (M); organic
#                dark-matter corroboration → Dark Matter (D). Keeps D pristine.
#   spam       → dropped entirely.
_NEWS_FULL_W       = round(math.log1p(120), 4)                       # ~4.79
_NEWS_QUARANTINE_W = float(os.getenv("NEWS_QUARANTINE_W", "0.05"))   # ~1%
_NEWS_PROMOTE_W    = float(os.getenv("NEWS_PROMOTE_W", "0.48"))      # ~10%
# Admit unverified sources at quarantine weight (vs dropping them outright).
_NEWS_ADMIT_UNVERIFIED = os.getenv("NEWS_ADMIT_UNVERIFIED", "1") == "1"


def _news_write(conn, platform: str, items: list) -> int:
    """Write news headlines into raw_signals + topic_signals, with PROVENANCE
    TIERING: reputable publishers enter at full weight; broad/unverified sources
    are admitted but quarantined at ~1% (promoted later only if independently
    corroborated); spam is dropped. items: list of {title, source}."""
    now = datetime.now(timezone.utc).isoformat()
    seen_titles: dict = {}
    total_topic_signals = 0
    dropped_spam = 0
    quarantined = 0
    for it in items:
        title = (it.get("title") or "").strip()
        if len(title) < 12:        # too short to be a real headline
            continue
        source = (it.get("source") or "").strip()
        src_l = source.lower()

        # Spam / PR-wire → dropped entirely (never enters the corpus).
        if any(s in src_l for s in _NEWS_SPAM_SOURCES):
            dropped_spam += 1
            continue

        reputable = _is_reputable_source(source)
        # A non-reputable source is QUARANTINED, not dropped — unless unverified
        # admission is disabled, in which case it is dropped (strict mode).
        if not reputable:
            if not _NEWS_ADMIT_UNVERIFIED:
                dropped_spam += 1
                continue

        norm = _news_norm_title(title)
        dup_count = seen_titles.get(norm, 0)
        seen_titles[norm] = dup_count + 1
        if dup_count >= 1:
            continue  # count a syndicated headline only once

        try:
            sentiment = _sentiment.polarity_scores(title)["compound"]
        except Exception:
            sentiment = 0.0

        # Provenance tiering:
        if reputable:
            tier = "mainstream"
            is_organic = 1
            engagement = _NEWS_FULL_W
        else:
            tier = "unverified"        # quarantined — can't move a score alone
            is_organic = 0             # cannot touch Dark Matter on its own
            engagement = round(_NEWS_QUARANTINE_W, 4)
            quarantined += 1

        sig_id = hashlib.md5(f"{platform}-{norm}-{now[:10]}".encode()).hexdigest()[:16]
        conn.execute(
            "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (sig_id, now, platform, tier, source[:100] or "news",
             title[:500], "", "", 0, 0, engagement, round(sentiment, 4),
             0, is_organic, title[:500]),
        )
        for topic in extract_topics_from_text(title):
            tkey = _topic_key(topic)
            t_id = hashlib.md5(f"{sig_id}-{tkey}".encode()).hexdigest()[:16]
            conn.execute(
                "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (t_id, now, topic, tkey, sig_id, platform, tier,
                 source[:100] or "news", 0, 0, engagement, 0, is_organic),
            )
            total_topic_signals += 1
    conn.commit()
    notes = []
    if quarantined:   notes.append(f"{quarantined} quarantined@1% (unverified)")
    if dropped_spam:  notes.append(f"{dropped_spam} dropped (spam/strict)")
    note = (" [" + "; ".join(notes) + "]") if notes else ""
    print(f"  {platform}: {len(items)} articles → {total_topic_signals} topic signals{note}")
    return total_topic_signals


def corroborate_unverified_news(conn, hours: int = 72) -> dict:
    """Promote quarantined unverified-source news signals — but ONLY when the same
    topic is independently corroborated, and route the promoted weight by PATH:

      • organic DARK-MATTER corroboration (first-timer organic activity on the
        topic from a vetted source) → set is_organic=1 → contributes to Dark
        Matter (D). This is genuine early signal.
      • REPUTABLE / curated corroboration (the topic is independently carried by
        ANY vetted, non-unverified source) → set tier='mainstream' →
        contributes to platform breadth (M). This is mainstream confirmation.

    Dark-matter routing is preferred when both apply (the more valuable early
    read). Uncorroborated unverified signals stay at ~1% (inert) — an unverified
    source can never stand alone. Runs before scoring so the weights are live.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    promoted_dm = promoted_main = left_inert = 0
    try:
        rows = conn.execute(
            "SELECT DISTINCT topic_key FROM topic_signals "
            "WHERE platform_tier = 'unverified' AND extracted_at >= ?",
            (cutoff,)).fetchall()
        topic_keys = [(r["topic_key"] if hasattr(r, "keys") else r[0]) for r in rows]

        for tk in topic_keys:
            # Capture the unverified signal ids for this topic up front.
            sig_rows = conn.execute(
                "SELECT signal_id FROM topic_signals "
                "WHERE topic_key = ? AND platform_tier = 'unverified' AND extracted_at >= ?",
                (tk, cutoff)).fetchall()
            sig_ids = [(r["signal_id"] if hasattr(r, "keys") else r[0]) for r in sig_rows]
            sig_ids = [s for s in sig_ids if s]

            dm = conn.execute(
                "SELECT 1 FROM topic_signals WHERE topic_key = ? "
                "AND platform_tier != 'unverified' AND is_first_timer = 1 "
                "AND is_organic = 1 AND extracted_at >= ? LIMIT 1",
                (tk, cutoff)).fetchone()
            rep = conn.execute(
                "SELECT 1 FROM topic_signals WHERE topic_key = ? "
                "AND platform_tier != 'unverified' AND extracted_at >= ? LIMIT 1",
                (tk, cutoff)).fetchone()

            if dm:  # → Dark Matter
                # Move OUT of 'unverified' (so scoring includes it) AND mark
                # organic so it raises Dark Matter's organic quality gate. It's a
                # mainstream-news source by nature, so it also lands in the
                # mainstream tier (adds a mainstream denominator → does NOT
                # inflate niche G). is_first_timer stays 0 — the outlet is not a
                # first-timer; we only credit the organic alignment.
                conn.execute(
                    "UPDATE topic_signals SET platform_tier = 'mainstream', is_organic = 1, engagement_raw = ? "
                    "WHERE topic_key = ? AND platform_tier = 'unverified' AND extracted_at >= ?",
                    (_NEWS_PROMOTE_W, tk, cutoff))
                if sig_ids:
                    ph = ",".join("?" * len(sig_ids))
                    conn.execute(
                        f"UPDATE raw_signals SET platform_tier = 'mainstream', is_organic = 1, engagement_raw = ? WHERE id IN ({ph})",
                        (_NEWS_PROMOTE_W, *sig_ids))
                promoted_dm += 1
            elif rep:  # → mainstream (platform breadth / M)
                conn.execute(
                    "UPDATE topic_signals SET platform_tier = 'mainstream', engagement_raw = ? "
                    "WHERE topic_key = ? AND platform_tier = 'unverified' AND extracted_at >= ?",
                    (_NEWS_PROMOTE_W, tk, cutoff))
                if sig_ids:
                    ph = ",".join("?" * len(sig_ids))
                    conn.execute(
                        f"UPDATE raw_signals SET platform_tier = 'mainstream', engagement_raw = ? WHERE id IN ({ph})",
                        (_NEWS_PROMOTE_W, *sig_ids))
                promoted_main += 1
            else:
                left_inert += 1
        conn.commit()
    except Exception as e:
        print(f"  [corroborate] error: {e}")
    result = {"promoted_dark_matter": promoted_dm,
              "promoted_mainstream": promoted_main,
              "left_inert": left_inert}
    if promoted_dm or promoted_main or left_inert:
        print(f"  Corroboration: {result}")
    return result


def collect_newsapi_org(conn) -> int:
    """NewsAPI.org top headlines (mainstream-tier genuine contributor)."""
    key = os.getenv("NEWSAPI_ORG_KEY", "")
    if not key:
        return 0
    try:
        from urllib.request import Request, urlopen
        _count_api("newsapi_org")
        url = ("https://newsapi.org/v2/top-headlines?language=en&pageSize=100"
               f"&apiKey={key}")
        req = Request(url, headers={"User-Agent": "NowTrendIn/1.0"})
        with urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        items = [{"title": a.get("title", ""),
                  "source": ((a.get("source") or {}).get("name") or "")}
                 for a in data.get("articles", [])]
        return _news_write(conn, "newsapi_org", items)
    except Exception as e:
        print(f"  newsapi_org error: {e}")
        return 0


def collect_newsapi_ai(conn) -> int:
    """NewsAPI.ai (Event Registry) recent articles (mainstream-tier contributor)."""
    key = os.getenv("NEWSAPI_AI_KEY", "")
    if not key:
        return 0
    try:
        from urllib.request import Request, urlopen
        from urllib.parse import urlencode
        q = urlencode({"action": "getArticles", "resultType": "articles",
                       "articlesSortBy": "date", "articlesCount": "100",
                       "lang": "eng", "apiKey": key})
        _count_api("newsapi_ai")
        url = f"https://eventregistry.org/api/v1/article/getArticles?{q}"
        req = Request(url, headers={"User-Agent": "NowTrendIn/1.0"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        results = ((data.get("articles") or {}).get("results")) or []
        items = [{"title": a.get("title", ""),
                  "source": ((a.get("source") or {}).get("title") or "")}
                 for a in results]
        return _news_write(conn, "newsapi_ai", items)
    except Exception as e:
        print(f"  newsapi_ai error: {e}")
        return 0


def collect_newsdata_io(conn) -> int:
    """NewsData.io latest news (mainstream-tier genuine contributor)."""
    key = os.getenv("NEWSDATA_IO_KEY", "")
    if not key:
        return 0
    try:
        from urllib.request import Request, urlopen
        _count_api("newsdata_io")
        url = f"https://newsdata.io/api/1/latest?apikey={key}&language=en"
        req = Request(url, headers={"User-Agent": "NowTrendIn/1.0"})
        with urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        items = [{"title": a.get("title", ""),
                  "source": (a.get("source_id") or a.get("source_name") or "")}
                 for a in (data.get("results") or [])]
        return _news_write(conn, "newsdata_io", items)
    except Exception as e:
        print(f"  newsdata_io error: {e}")
        return 0


def _calls_today(source: str) -> int:
    """Today's logged API calls for a source (from the api_usage ledger)."""
    try:
        if _HEALTH_AVAILABLE:
            u = _health.get_api_usage(DB_PATH)
            return int(((u.get("sources", {}).get(source, {})) or {}).get("today", 0) or 0)
    except Exception:
        pass
    return 0


def _domain_name(url: str) -> str:
    """Bare domain from a URL (for reputable-source matching), e.g.
    https://elpais.com/x → 'elpais.com'."""
    try:
        from urllib.parse import urlparse
        host = (urlparse(url).netloc or "").lower().lstrip("www.")
        return host or "currents"
    except Exception:
        return "currents"


# Currents free tier = 1000 requests/day. Hard guard keeps us safely under it:
# we stop calling once today's logged calls reach this cap (default 900 = margin).
_CURRENTS_DAILY_CAP = int(os.getenv("CURRENTS_DAILY_CAP", "900"))


def collect_currents_news(conn) -> int:
    """Currents News API — multi-source aggregator (120k+ outlets incl. reputable
    Spanish media like EL PAÍS). A firehose; the reputable-source filter keeps only
    vetted publishers. HARD daily cap: never exceeds _CURRENTS_DAILY_CAP/day (free
    tier is 1000/day), enforced from the api_usage ledger so we cannot overrun."""
    key = os.getenv("CURRENTS_API_KEY", "")
    if not key:
        return 0
    used = _calls_today("currents")
    if used >= _CURRENTS_DAILY_CAP:
        print(f"  currents: daily cap reached ({used}/{_CURRENTS_DAILY_CAP}) — skipping to stay under 1000/day")
        return 0
    try:
        from urllib.request import Request, urlopen
        _count_api("currents")
        url = f"https://api.currentsapi.services/v1/latest-news?language=en&apiKey={key}"
        req = Request(url, headers={"User-Agent": "NowTrendIn/1.0"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        items = [{"title": a.get("title", ""),
                  "source": _domain_name(a.get("url") or "")}
                 for a in (data.get("news") or []) if a.get("title")]
        return _news_write(conn, "currents", items)
    except Exception as e:
        print(f"  currents error: {e}")
        return 0


# Direct RSS feeds — verified live (06/18/26). FT Alphaville (paywall teaser, 1 item)
# and Reuters agency feed (discontinued, 301) were tested and EXCLUDED. Each fetch is
# 1 request; runs on the slow news cadence.
_RSS_FEEDS = [
    ("El País",    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"),
    ("TechCrunch", "https://techcrunch.com/feed/"),
    # BBC News — OFFICIAL feeds.bbci.co.uk verticals (verified live 06/22/26, fresh within
    # hours). All tagged the single outlet "BBC News" so the 4 verticals add breadth
    # (tech/business/world/top) WITHOUT inflating the corroboration source-count — BBC is
    # one outlet, not four. Direct from BBC (syndication feeds); no third-party scraper.
    ("BBC News", "https://feeds.bbci.co.uk/news/rss.xml"),
    ("BBC News", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("BBC News", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("BBC News", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    # LA Times — OFFICIAL rss2.0.xml verticals (verified live 06/22/26, all fresh <1d,
    # 96-100 items each). One outlet label "LA Times" (breadth without inflating the
    # corroboration source-count). WSJ RSS was dead (~17mo stale) and SF Chronicle 404'd,
    # so those were excluded; NewsAPI rejected (24h-delayed + production-banned).
    ("LA Times", "https://www.latimes.com/local/rss2.0.xml"),
    ("LA Times", "https://www.latimes.com/california/rss2.0.xml"),
    ("LA Times", "https://www.latimes.com/politics/rss2.0.xml"),
    ("LA Times", "https://www.latimes.com/business/rss2.0.xml"),
    ("LA Times", "https://www.latimes.com/business/technology/rss2.0.xml"),
    ("LA Times", "https://www.latimes.com/entertainment-arts/rss2.0.xml"),
    # CNBC / Guardian / DW / ABC / Verge / InfoQ — OFFICIAL feeds, verified live & fresh
    # (06/22/26, <3d). One label per outlet (no corroboration inflation). These are the
    # main-trend ARTICLE feeds — complementary to the same outlets' YouTube finance-risk
    # signal. CNN excluded (its rss.cnn.com is 2-9yr dead → stays YouTube-only). Each is
    # tagged with a name the reputable-source filter already recognizes.
    ("CNBC",         "https://www.cnbc.com/id/100727362/device/rss/rss.html"),
    ("CNBC",         "https://www.cnbc.com/id/20910258/device/rss/rss.html"),
    ("CNBC",         "https://www.cnbc.com/id/19854910/device/rss/rss.html"),
    ("CNBC",         "https://www.cnbc.com/id/10000664/device/rss/rss.html"),
    ("The Guardian", "https://www.theguardian.com/international/rss"),
    ("The Guardian", "https://www.theguardian.com/world/rss"),
    ("The Guardian", "https://www.theguardian.com/world/usa/rss"),
    ("The Guardian", "https://www.theguardian.com/uk/business/rss"),
    ("The Guardian", "https://www.theguardian.com/uk/technology/rss"),
    ("DW News",      "https://rss.dw.com/rdf/rss-en-top"),
    ("ABC Australia","https://www.abc.net.au/news/feed/51892/rss.xml"),
    ("ABC News",     "https://abcnews.go.com/abcnews/topstories"),
    ("The Verge",    "https://www.theverge.com/rss/index.xml"),
    # The Verge topic feeds (Atom; verified live & fresh 06/22/26). Same outlet label.
    # AI + Tech + Cyber are high-value for the AI/tech thesis; dedup by title handles
    # overlap with the main feed. (Requires the Atom <entry> parsing in collect_rss_news.)
    ("The Verge",    "https://www.theverge.com/rss/tech/index.xml"),
    ("The Verge",    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("The Verge",    "https://www.theverge.com/rss/business/index.xml"),
    ("The Verge",    "https://www.theverge.com/rss/cyber-security/index.xml"),
    ("The Verge",    "https://www.theverge.com/rss/reviews/index.xml"),
    ("The Verge",    "https://www.theverge.com/rss/games/index.xml"),
    ("InfoQ",        "https://feed.infoq.com/"),
    # Financial Times — official ?format=rss section feeds (verified live & fresh
    # 06/22/26, 25 items each). Premium finance/markets/economy signal; the paywall is
    # irrelevant since we extract topics from HEADLINES only. "Financial Times" is
    # already in the reputable-source list. Reuters-via-GoogleNews was assessed and
    # SKIPPED (not an official feed, redirect links, redundant with GDELT).
    ("Financial Times", "https://www.ft.com/news-feed?format=rss"),
    ("Financial Times", "https://www.ft.com/world?format=rss"),
    ("Financial Times", "https://www.ft.com/companies?format=rss"),
    ("Financial Times", "https://www.ft.com/global-economy?format=rss"),
    ("Financial Times", "https://www.ft.com/markets?format=rss"),
    ("Financial Times", "https://www.ft.com/technology?format=rss"),
    # The Economist — CORRECT domain economist.com (the 'theeconomist.com' URLs were a
    # dead domain). Verified live/fresh 06/22/26, 300 items each. Premium analysis;
    # headlines only (paywall irrelevant). Already in the reputable-source list.
    ("The Economist", "https://www.economist.com/finance-and-economics/rss.xml"),
    ("The Economist", "https://www.economist.com/business/rss.xml"),
    ("The Economist", "https://www.economist.com/science-and-technology/rss.xml"),
    ("The Economist", "https://www.economist.com/leaders/rss.xml"),
    ("The Economist", "https://www.economist.com/international/rss.xml"),
    # Federal Reserve — OFFICIAL .gov feeds (FOMC/rate decisions, speeches, testimony).
    # Low-volume, high-signal primary macro source. (FOMC-specific path 404'd; Press All
    # carries FOMC announcements.)
    ("Federal Reserve", "https://www.federalreserve.gov/feeds/press_all.xml"),
    ("Federal Reserve", "https://www.federalreserve.gov/feeds/speeches.xml"),
    ("Federal Reserve", "https://www.federalreserve.gov/feeds/testimony.xml"),
    # ECB — OFFICIAL feeds at the CORRECT /rss/ paths (the press/shared/rss URLs 404'd).
    # EU monetary-policy primary source, complements the Fed.
    ("ECB", "https://www.ecb.europa.eu/rss/press.html"),
    ("ECB", "https://www.ecb.europa.eu/rss/pub.html"),
    # The New Yorker — OFFICIAL Condé Nast feeds (news + business desks). Long-form
    # reputable reporting; complements the wire/financial-press roster.
    ("The New Yorker", "https://www.newyorker.com/feed/news"),
    ("The New Yorker", "https://www.newyorker.com/feed/business"),
    # The Independent — OFFICIAL section feeds (work with our UA; Telegraph 403s edge-blocked,
    # MSNBC siren-api host is dead). UK national paper; overlap deduped by _news_norm_title.
    ("The Independent", "https://www.independent.co.uk/news/rss"),
    ("The Independent", "https://www.independent.co.uk/news/uk/rss"),
    ("The Independent", "https://www.independent.co.uk/news/world/rss"),
    ("The Independent", "https://www.independent.co.uk/news/uk/politics/rss"),
    # NBC News — OFFICIAL feed (the live substitute for the dead MSNBC siren-api URLs).
    ("NBC News", "https://feeds.nbcnews.com/nbcnews/public/news"),
]


def collect_rss_news(conn) -> int:
    """Native RSS→items for specific trusted outlets (El País, TechCrunch). Parses
    item titles (CDATA-safe) and tags each with the outlet so the reputable filter +
    corroboration count credit them. No third-party aggregator dependency."""
    import re as _re
    import html as _html
    from urllib.request import Request, urlopen
    total = 0
    for label, url in _RSS_FEEDS:
        try:
            _count_api("rss")
            req = Request(url, headers={"User-Agent": "NowTrendIn/1.0"})
            with urlopen(req, timeout=15) as resp:
                xml = resp.read().decode("utf-8", "ignore")
            # entry-level titles only (RSS <item> AND Atom <entry>; skip the feed/channel
            # <title>). <title[^>]*> tolerates Atom's <title type="html"> attribute.
            raw_titles = _re.findall(r"<(?:item|entry)\b.*?<title[^>]*>(.*?)</title>",
                                     xml, _re.DOTALL | _re.IGNORECASE)
            items = []
            for t in raw_titles[:40]:
                # Strip a CDATA wrapper allowing surrounding whitespace (The Economist
                # uses '<title> <![CDATA[...]]> </title>' — flush-only matching leaked
                # a "cdata" token), then HTML-unescape so entities (&#x27; etc.) don't
                # tokenize into junk. Both fixes apply to every RSS/Atom outlet.
                t = _re.sub(r"^\s*<!\[CDATA\[\s*", "", t)
                t = _re.sub(r"\s*\]\]>\s*$", "", t)
                t = _html.unescape(t).strip()
                if t:
                    items.append({"title": t, "source": label})
            total += _news_write(conn, "rss", items)
        except Exception as e:
            print(f"  rss {label} error: {e}")
    return total


def collect_yahoo_finance_news(conn) -> int:
    """Yahoo Finance news (RapidAPI, yahoo-finance166) → mainstream-tier genuine
    contributor. Finance-focused headlines complement the general news feeds."""
    # DISABLED 2026-06-24 — yahoo-finance166 (RapidAPI) returns HTTP 429 every cycle
    # (quota exhausted), 0 signals. Removed from production. Flip YAHOO_FINANCE_ENABLED=1
    # to re-enable if/when the RapidAPI quota is restored.
    if os.getenv("YAHOO_FINANCE_ENABLED", "0") != "1":
        return 0
    key = os.getenv("RAPIDAPI_YF_KEY", "")
    if not key:
        return 0
    try:
        from urllib.request import Request, urlopen
        _count_api("yahoo_finance")
        url = ("https://yahoo-finance166.p.rapidapi.com/api/news/list"
               "?snippetCount=100&region=US")
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
            title = content.get("title", "")
            prov = (content.get("provider") or {}).get("displayName", "") or "Yahoo Finance"
            if title:
                items.append({"title": title, "source": prov})
        return _news_write(conn, "yahoo_finance", items)
    except Exception as e:
        print(f"  yahoo_finance error: {e}")
        return 0


def collect_creator_trends(conn) -> int:
    """Mine retail-finance creators' (Meet Kevin, Andrei Jikh) recent YouTube
    titles into the TRENDS feed — a genuine mainstream/retail-tier contributor,
    like X. Authenticity: creator content is attributed and broad → tier
    'mainstream', is_first_timer=0 (cannot fake first-timer dark matter)."""
    if not _RISK_AVAILABLE or not os.getenv("YOUTUBE_API_KEY"):
        return 0
    now = datetime.now(timezone.utc).isoformat()
    total = 0
    try:
        creators = getattr(risk, "CREATORS", [])
        for cr in creators:
            for v in risk._creator_recent(cr["handle"], 25):
                title = (v.get("title") or "").strip()
                if len(title) < 8:
                    continue
                try:
                    sentiment = _sentiment.polarity_scores(title)["compound"]
                except Exception:
                    sentiment = 0.0
                eng = round(math.log1p(40), 4)
                sig_id = hashlib.md5(f"creator-{cr['handle']}-{title[:60]}".encode()).hexdigest()[:16]
                conn.execute(
                    "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (sig_id, now, "creator", "mainstream", cr["name"], title[:500],
                     v.get("url", ""), cr["name"][:100], 0, 0, eng, round(sentiment, 4),
                     0, 1, title[:500]),
                )
                for topic in extract_topics_from_text(title):
                    tkey = _topic_key(topic)
                    t_id = hashlib.md5(f"{sig_id}-{tkey}".encode()).hexdigest()[:16]
                    conn.execute(
                        "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (t_id, now, topic, tkey, sig_id, "creator", "mainstream",
                         cr["name"], 0, 0, eng, 0, 1),
                    )
                    total += 1
        conn.commit()
    except Exception as e:
        print(f"  creator trends error: {e}")
    print(f"  Creator trends: {total} topic signals")
    return total


def collect_broadcast_trends(conn) -> int:
    """Mine broadcast/institutional news channels' (CNBC, CNN, Bloomberg, Reuters,
    etc.) recent YouTube titles into the TRENDS feed — mainstream tier, attributed.
    These are late-stage public-awareness signals: high engagement but NOT first-
    timer dark matter (broadcast = the crowd already knows)."""
    if not _RISK_AVAILABLE or not os.getenv("YOUTUBE_API_KEY"):
        return 0
    now = datetime.now(timezone.utc).isoformat()
    total = 0
    try:
        channels = getattr(risk, "BROADCAST_CHANNELS", [])
        for bc in channels:
            for v in risk._broadcast_recent(bc["handle"], 20):
                title = (v.get("title") or "").strip()
                if len(title) < 8:
                    continue
                try:
                    sentiment = _sentiment.polarity_scores(title)["compound"]
                except Exception:
                    sentiment = 0.0
                eng = round(math.log1p(200), 4)  # broadcast gets higher base weight
                sig_id = hashlib.md5(f"broadcast-{bc['handle']}-{title[:60]}".encode()).hexdigest()[:16]
                conn.execute(
                    "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (sig_id, now, "broadcast", "mainstream", bc["name"], title[:500],
                     v.get("url", ""), bc["name"][:100], 0, 0, eng, round(sentiment, 4),
                     0, 1, title[:500]),
                )
                for topic in extract_topics_from_text(title):
                    tkey = _topic_key(topic)
                    t_id = hashlib.md5(f"{sig_id}-{tkey}".encode()).hexdigest()[:16]
                    conn.execute(
                        "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (t_id, now, topic, tkey, sig_id, "broadcast", "mainstream",
                         bc["name"], 0, 0, eng, 0, 1),
                    )
                    total += 1
        conn.commit()
    except Exception as e:
        print(f"  broadcast trends error: {e}")
    print(f"  Broadcast trends: {total} topic signals")
    return total


# ── Social / open-network collectors (added 2026-06-12) ──────────────────
# Keyless, free APIs that replace Reddit's role as the niche-tier early-chatter
# sensor. Bluesky + Lemmy carry AUTHOR identity, so the first-timer / dark-matter
# math works on them exactly as it did on Reddit.

def _social_write_signal(conn, *, sig_id, platform, tier, community, title, url,
                         author, ups, comments, is_first_timer, is_organic) -> int:
    """Shared raw_signals + topic_signals writer for the social collectors.
    Returns the number of topic signals written."""
    now = datetime.now(timezone.utc).isoformat()
    try:
        sentiment = _sentiment.polarity_scores(title)["compound"]
    except Exception:
        sentiment = 0.0
    eng = round(math.log1p(max(0, ups)) + math.log1p(max(0, comments) * 2), 4)
    conn.execute(
        "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (sig_id, now, platform, tier, community, title[:500], url[:500],
         (author or "")[:100], ups, comments, eng, round(sentiment, 4),
         1 if is_first_timer else 0, 1 if is_organic else 0, title[:500]),
    )
    n = 0
    for topic in extract_topics_from_text(title):
        tkey = _topic_key(topic)
        t_id = hashlib.md5(f"{sig_id}-{tkey}".encode()).hexdigest()[:16]
        conn.execute(
            "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (t_id, now, topic, tkey, sig_id, platform, tier, community,
             ups, comments, eng, 1 if is_first_timer else 0,
             1 if is_organic else 0),
        )
        n += 1
    return n


def collect_bluesky(conn) -> int:
    """Bluesky What's Hot feed via the public AppView (no auth). Early-adopter
    network → niche tier. Author handles enable real first-timer detection."""
    feed_uri = os.getenv(
        "BLUESKY_FEED_URI",
        "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot")
    total = 0
    try:
        r = requests.get(
            "https://public.api.bsky.app/xrpc/app.bsky.feed.getFeed",
            params={"feed": feed_uri, "limit": 100},
            headers={"User-Agent": REDDIT_USER_AGENT}, timeout=20)
        r.raise_for_status()
        items = (r.json() or {}).get("feed", []) or []
    except Exception as e:
        print(f"  Bluesky: feed error: {e}")
        return 0
    for it in items:
        post = (it or {}).get("post") or {}
        text = ((post.get("record") or {}).get("text") or "").strip()
        handle = ((post.get("author") or {}).get("handle") or "").strip()
        uri = post.get("uri", "")
        if len(text) < 12 or not uri:
            continue
        likes = int(post.get("likeCount") or 0)
        replies = int(post.get("replyCount") or 0)
        ft = check_author_is_first_timer(conn, handle, "bluesky", "whats-hot") if handle else False
        organic = not (likes > 5000 and replies < 5)
        sig_id = hashlib.md5(f"bsky-{uri}".encode()).hexdigest()[:16]
        web_url = "https://bsky.app/profile/" + handle if handle else "https://bsky.app"
        total += _social_write_signal(
            # General social microblog = mainstream chatter, NOT specialist
            # dark matter. Dark matter is reserved for pre-mainstream expert
            # communities (GitHub/HN/specialist forums); broad social media is
            # part of the mainstreaming wave a topic rides AFTER its niche phase.
            conn, sig_id=sig_id, platform="bluesky", tier="mainstream",
            community="whats-hot", title=text, url=web_url, author=handle,
            ups=likes, comments=replies, is_first_timer=ft, is_organic=organic)
    conn.commit()
    print(f"  Bluesky: {total} topic signals")
    return total


def collect_lemmy(conn) -> int:
    """Lemmy (open-source Reddit) hot posts via the open REST API (no auth).
    Mainstream tier (general social media, not specialist dark matter);
    creator names enable first-timer detection."""
    instances = [s.strip() for s in os.getenv(
        "LEMMY_INSTANCES", "lemmy.world,lemmy.ml").split(",") if s.strip()]
    total = 0
    for inst in instances:
        try:
            r = requests.get(
                f"https://{inst}/api/v3/post/list",
                params={"type_": "All", "sort": "Hot", "limit": 50},
                headers={"User-Agent": REDDIT_USER_AGENT}, timeout=20)
            r.raise_for_status()
            posts = (r.json() or {}).get("posts", []) or []
        except Exception as e:
            print(f"  Lemmy {inst}: error: {e}")
            continue
        for pv in posts:
            p = (pv or {}).get("post") or {}
            counts = (pv or {}).get("counts") or {}
            creator = ((pv or {}).get("creator") or {}).get("name") or ""
            community = ((pv or {}).get("community") or {}).get("name") or inst
            title = (p.get("name") or "").strip()
            if len(title) < 8 or not p.get("id"):
                continue
            score = int(counts.get("score") or 0)
            comments = int(counts.get("comments") or 0)
            ft = check_author_is_first_timer(conn, creator, "lemmy", community) if creator else False
            sig_id = hashlib.md5(f"lemmy-{inst}-{p['id']}".encode()).hexdigest()[:16]
            total += _social_write_signal(
                # Community-level tier: a specialist Lemmy community (e.g.
                # machinelearning@) is expert/dark-matter; a general one
                # (world, technology) is mainstream.
                conn, sig_id=sig_id, platform="lemmy",
                tier=_community_tier("lemmy", community),
                community=community, title=title,
                url=p.get("ap_id") or f"https://{inst}/post/{p['id']}",
                author=creator, ups=score, comments=comments,
                is_first_timer=ft, is_organic=True)
    conn.commit()
    print(f"  Lemmy: {total} topic signals")
    return total


def collect_mastodon(conn) -> int:
    """Mastodon trending tags + links via the public trends API (no auth).
    Trend-level (no authors → no first-timer signal), mainstream tier
    (general social media, not specialist dark matter)."""
    inst = os.getenv("MASTODON_INSTANCE", "mastodon.social")
    total = 0
    for kind, path in (("tag", "tags"), ("link", "links")):
        try:
            r = requests.get(f"https://{inst}/api/v1/trends/{path}",
                             params={"limit": 20},
                             headers={"User-Agent": REDDIT_USER_AGENT}, timeout=20)
            r.raise_for_status()
            rows = r.json() or []
        except Exception as e:
            print(f"  Mastodon {path}: error: {e}")
            continue
        for row in rows:
            if kind == "tag":
                title = (row.get("name") or "").strip()
                url = row.get("url") or f"https://{inst}/tags/{title}"
            else:
                title = (row.get("title") or "").strip()
                url = row.get("url") or ""
            if len(title) < 4:
                continue
            hist = row.get("history") or []
            uses = sum(int(h.get("uses") or 0) for h in hist[:2])
            accounts = sum(int(h.get("accounts") or 0) for h in hist[:2])
            day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            sig_id = hashlib.md5(f"masto-{kind}-{title.lower()}-{day}".encode()).hexdigest()[:16]
            total += _social_write_signal(
                conn, sig_id=sig_id, platform="mastodon", tier="mainstream",
                community=f"trending-{path}", title=title, url=url, author="",
                ups=accounts, comments=uses, is_first_timer=False,
                is_organic=True)
    conn.commit()
    print(f"  Mastodon: {total} topic signals")
    return total


def collect_gdelt_trends(conn) -> int:
    """GDELT Doc API (free, no key) as independent MAINSTREAM corroboration of
    the engine's newest emerging topics. The attention-mode 'gdelt' health entry
    previously had no producer at all ('never recorded a successful run').
    Bounded: ≤15 topic queries per cycle, paced 1s."""
    try:
        topics = _x_candidate_topics(int(os.getenv("GDELT_TOPIC_LIMIT", "15")))
    except Exception:
        topics = []
    total = 0
    for i, t in enumerate(topics):
        if i:
            time.sleep(1.0)
        try:
            r = requests.get(
                "https://api.gdeltproject.org/api/v2/doc/doc",
                params={"query": t, "mode": "ArtList", "format": "json",
                        "timespan": "24h", "maxrecords": 10, "sort": "hybridrel"},
                headers={"User-Agent": REDDIT_USER_AGENT}, timeout=20)
            r.raise_for_status()
            arts = (r.json() or {}).get("articles", []) or []
        except Exception as e:
            print(f"  GDELT '{t}': error: {e}")
            continue
        for a in arts:
            title = (a.get("title") or "").strip()
            url = a.get("url") or ""
            domain = (a.get("domain") or "").strip() or "gdelt"
            if len(title) < 12 or not url:
                continue
            sig_id = hashlib.md5(f"gdelt-{url}".encode()).hexdigest()[:16]
            total += _social_write_signal(
                conn, sig_id=sig_id, platform="gdelt", tier="mainstream",
                community=domain, title=title, url=url, author=domain,
                ups=0, comments=0, is_first_timer=False, is_organic=True)
    conn.commit()
    print(f"  GDELT trends: {total} topic signals")
    return total


def collect_for_term(conn, term: str) -> int:
    """
    Targeted, on-demand collection for a single queried topic
    (Enterprise direct query). Searches Hacker News (Algolia) and GitHub for
    the exact term and attributes every hit to that topic's key.
    """
    tkey = _topic_key(term)
    now = datetime.now(timezone.utc).isoformat()
    count = 0

    # ── Hacker News (Algolia full-text search) ──────────────────────
    try:
        resp = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={"query": term, "tags": "story", "hitsPerPage": 50},
            timeout=10,
        )
        if resp.status_code == 200:
            for hit in resp.json().get("hits", []):
                title = hit.get("title", "")
                if not title:
                    continue
                points = hit.get("points", 0) or 0
                comments = hit.get("num_comments", 0) or 0
                created = hit.get("created_at_i", 0) or 0
                age_hours = max(1, (time.time() - created) / 3600)
                engagement = math.log1p((points / age_hours) * 10) + math.log1p(comments)
                sentiment = _sentiment.polarity_scores(title)['compound']
                oid = hit.get("objectID", "")
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={oid}"
                sig_id = hashlib.md5(f"q-hn-{oid}-{tkey}".encode()).hexdigest()[:16]
                conn.execute(
                    "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (sig_id, now, "hackernews", "expert", "search", title[:500], url, "",
                     points, comments, round(engagement, 4), round(sentiment, 4), 0, 1, title[:500]),
                )
                t_id = hashlib.md5(f"{sig_id}-{tkey}".encode()).hexdigest()[:16]
                conn.execute(
                    "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (t_id, now, term, tkey, sig_id, "hackernews", "expert", "search",
                     points, comments, round(engagement, 4), 0, 1),
                )
                count += 1
    except Exception as e:
        print(f"[query] HN error: {e}")

    # ── GitHub (repository search) ──────────────────────────────────
    try:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        resp = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": term, "sort": "stars", "order": "desc", "per_page": 30},
            headers=headers, timeout=10,
        )
        if resp.status_code == 200:
            for repo in resp.json().get("items", []):
                stars = repo.get("stargazers_count", 0) or 0
                forks = repo.get("forks_count", 0) or 0
                issues = repo.get("open_issues_count", 0) or 0
                days_old = 1
                try:
                    created = datetime.fromisoformat(repo.get("created_at", "").replace("Z", "+00:00"))
                    days_old = max(1, (datetime.now(timezone.utc) - created).days)
                except Exception:
                    pass
                engagement = math.log1p(stars / days_old) + math.log1p(forks * 2)
                desc = repo.get("description", "") or ""
                full_name = repo.get("full_name", "")
                combined = f"{full_name} {desc}"
                sig_id = hashlib.md5(f"q-gh-{repo.get('id')}-{tkey}".encode()).hexdigest()[:16]
                conn.execute(
                    "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (sig_id, now, "github", "expert", "search", combined[:500],
                     repo.get("html_url", ""), full_name[:100], stars, issues,
                     round(engagement, 4), round(_sentiment.polarity_scores(desc)['compound'], 4),
                     0, 1, combined[:500]),
                )
                t_id = hashlib.md5(f"{sig_id}-{tkey}".encode()).hexdigest()[:16]
                conn.execute(
                    "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (t_id, now, term, tkey, sig_id, "github", "expert", "search",
                     stars, issues, round(engagement, 4), 0, 1),
                )
                count += 1
    except Exception as e:
        print(f"[query] GitHub error: {e}")

    # ── YouTube (mainstream/consumer platform) ──────────────────────
    # Adds a MAINSTREAM source so platform diversity + the niche-vs-mainstream
    # gradient reflect reality instead of an expert-only (HN+GitHub) view.
    yt_key = os.getenv("YOUTUBE_API_KEY", "")
    if yt_key:
        try:
            resp = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={"part": "snippet", "q": term, "type": "video",
                        "maxResults": 15, "order": "relevance", "key": yt_key},
                timeout=10,
            )
            if resp.status_code == 200:
                for item in resp.json().get("items", []):
                    sn = item.get("snippet", {})
                    title = sn.get("title", "")
                    vid = (item.get("id") or {}).get("videoId", "")
                    if not title or not vid:
                        continue
                    try:
                        pub = datetime.fromisoformat(sn.get("publishedAt", "").replace("Z", "+00:00"))
                        age_days = max(1, (datetime.now(timezone.utc) - pub).days)
                    except Exception:
                        age_days = 30
                    engagement = math.log1p(30 / age_days)  # recency proxy
                    sentiment = _sentiment.polarity_scores(title)['compound']
                    url = f"https://www.youtube.com/watch?v={vid}"
                    sig_id = hashlib.md5(f"q-yt-{vid}-{tkey}".encode()).hexdigest()[:16]
                    conn.execute(
                        "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (sig_id, now, "youtube", "mainstream", "search", title[:500], url,
                         sn.get("channelTitle", "")[:100], 0, 0, round(engagement, 4),
                         round(sentiment, 4), 0, 0, title[:500]),
                    )
                    t_id = hashlib.md5(f"{sig_id}-{tkey}".encode()).hexdigest()[:16]
                    conn.execute(
                        "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (t_id, now, term, tkey, sig_id, "youtube", "mainstream", "search",
                         0, 0, round(engagement, 4), 0, 0),
                    )
                    count += 1
        except Exception as e:
            print(f"[query] YouTube error: {e}")

    # ── Reddit (consumer platform; best-effort — datacenter IPs often blocked) ──
    try:
        resp = requests.get(
            "https://www.reddit.com/search.json",
            params={"q": term, "sort": "relevance", "limit": 25, "t": "month"},
            headers={"User-Agent": "nowtrendin/1.0 (+https://nowtrendin.com)"},
            timeout=10,
        )
        if resp.status_code == 200:
            for child in resp.json().get("data", {}).get("children", []):
                post = child.get("data", {})
                title = post.get("title", "")
                if not title:
                    continue
                ups = post.get("ups", 0) or 0
                comments = post.get("num_comments", 0) or 0
                created = post.get("created_utc", 0) or 0
                age_hours = max(1, (time.time() - created) / 3600)
                engagement = math.log1p((ups / age_hours) * 10) + math.log1p(comments)
                sentiment = _sentiment.polarity_scores(title)['compound']
                pid = post.get("id", "")
                url = f"https://reddit.com{post.get('permalink', '')}"
                sig_id = hashlib.md5(f"q-rd-{pid}-{tkey}".encode()).hexdigest()[:16]
                conn.execute(
                    "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (sig_id, now, "reddit", "mainstream", "search", title[:500], url,
                     post.get("subreddit", "")[:100], ups, comments, round(engagement, 4),
                     round(sentiment, 4), 0, 0, title[:500]),
                )
                t_id = hashlib.md5(f"{sig_id}-{tkey}".encode()).hexdigest()[:16]
                conn.execute(
                    "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (t_id, now, term, tkey, sig_id, "reddit", "mainstream", "search",
                     ups, comments, round(engagement, 4), 0, 0),
                )
                count += 1
    except Exception as e:
        print(f"[query] Reddit error: {e}")

    # ── Mainstream news (Stage 4) — corrects the niche-gradient distortion ──
    # Registers how widely the mainstream press covers a topic, inserted as
    # MAINSTREAM signals so a widely-covered topic (e.g. SpaceX) carries real
    # mainstream weight and its niche-concentration gradient correctly drops.
    # Sources: Guardian API (key-gated) + NYT RSS (free, no key) are merged;
    # GDELT is last resort only (rate-limited from cloud/Heroku IPs).
    if _NEWS_AVAILABLE:
        try:
            news_key = f"news:{term.strip().lower()}"
            gd = _cache.get(news_key)
            if gd is None:
                gd_guardian = _news.collect_guardian_signal(term)
                gd_nyt = _news.collect_nyt_signal(term)
                gd = (_news.merge_media_signals(gd_guardian, gd_nyt)
                      or _news.collect_gdelt_signal(term)
                      or {})
                _cache.set(news_key, gd, CACHE_TTL_XSIGNAL)  # 12h — coverage is stable
            if gd and gd.get("article_count", 0) > 0:
                # One mainstream signal per unit of coverage (capped). Engagement
                # scales with coverage volume; sentiment from tone if present.
                src = gd.get("source", "news")
                n = min(25, int(gd.get("article_count", 0)))
                vol = gd.get("total_volume", 0) or gd.get("article_count", 0)
                per_eng = round(math.log1p(vol / max(1, n)), 4)
                tone = gd.get("avg_tone", 0.0) or 0.0
                for k in range(n):
                    sig_id = hashlib.md5(f"q-{src}-{tkey}-{k}".encode()).hexdigest()[:16]
                    txt = f"{src} media coverage: {term}"
                    conn.execute(
                        "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (sig_id, now, src, "mainstream", "news", txt, "", "",
                         0, 0, per_eng, round(tone / 10.0, 4), 0, 0, txt),
                    )
                    t_id = hashlib.md5(f"{sig_id}-{tkey}".encode()).hexdigest()[:16]
                    conn.execute(
                        "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (t_id, now, term, tkey, sig_id, src, "mainstream", "news",
                         0, 0, per_eng, 0, 0),
                    )
                    count += 1
                print(f"[query] {src} '{term}': {gd.get('article_count')} articles, "
                      f"{gd.get('source_breadth')} outlets -> {n} mainstream signals")
        except Exception as e:
            print(f"[query] news error: {e}")

    conn.commit()
    return count


def persist_velocity_score(conn, result) -> None:
    """Write one scored result into velocity_scores (used by on-demand query)."""
    # SINK-HARDEN the heisenberg_gap invariant (persisted gap == stored detection -
    # confidence, SIGNED). The /query caller runs apply_calibration AFTER score_topic;
    # apply_calibration overwrites detection_score/confidence_score but inherits the
    # score-time heisenberg_gap from **raw_result and never refreshes it — so this path
    # persisted a STALE gap (the Scoring Contract Auditor's 50/800 derived-mismatch, the
    # ongoing leak the main cycle kept re-healing). Recompute here at the write sink so
    # the invariant holds no matter which caller built `result`. Mirrors line ~4370 of
    # the main scoring path. Zero score impact — gap is a derived display field.
    result["heisenberg_gap"] = round(
        (result.get("detection_score", 0) or 0) - (result.get("confidence_score", 0) or 0), 1)
    score_id = str(uuid.uuid4())[:16]
    conn.execute("""
        INSERT INTO velocity_scores (
            id, scored_at, topic_key, topic_display,
            gradient_strength, inertia_score, platform_diversity,
            dark_matter_score, confidence_decay, persistence_score,
            nowtrendin_score,
            overall_score, detection_score, confidence_score, heisenberg_gap,
            total_mentions, niche_mentions, mainstream_mentions,
            platforms_active, first_timer_ratio, engagement_asymmetry,
            gradient_ratio, signal_stage, is_gravitational_anomaly,
            anomaly_reason, why_this_matters, what_to_watch
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        score_id, result["scored_at"], result["topic_key"], result["topic_display"],
        result["gradient_strength"], result["inertia_score"], result["platform_diversity"],
        result["dark_matter_score"], result["confidence_decay"], result["persistence_score"],
        result["nowtrendin_score"],
        result["overall_score"], result["detection_score"], result["confidence_score"], result["heisenberg_gap"],
        result["total_mentions"], result["niche_mentions"], result["mainstream_mentions"],
        result["platforms_active"], result["first_timer_ratio"], result["engagement_asymmetry"],
        result["gradient_ratio"], result["signal_stage"], result["is_gravitational_anomaly"],
        result["anomaly_reason"], result["why_this_matters"], result["what_to_watch"],
    ))
    conn.commit()


# ══════════════════════════════════════════════════════════════════
# RESEARCH ARCHIVAL + RETENTION
# Keep full score detail ~30 days; snapshot latest scores monthly and
# retain those snapshots ~1 year for research/backtesting.
# ══════════════════════════════════════════════════════════════════

def archive_scores_snapshot(db_path: str = DB_PATH) -> int:
    """Save a research snapshot (latest score per topic) tagged with today's date."""
    snap = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = get_db(db_path)
    conn.execute("""
        INSERT INTO score_archive
            (snapshot_date, topic_key, topic_display, detection_score,
             confidence_score, overall_score, signal_stage, scored_at, total_mentions)
        SELECT ?, v.topic_key, v.topic_display, v.detection_score,
               v.confidence_score, v.overall_score, v.signal_stage, v.scored_at, v.total_mentions
        FROM velocity_scores v
        INNER JOIN (
            SELECT topic_key, MAX(scored_at) AS m FROM velocity_scores GROUP BY topic_key
        ) l ON v.topic_key = l.topic_key AND v.scored_at = l.m
        ON CONFLICT (snapshot_date, topic_key) DO NOTHING
    """, (snap,))
    conn.commit()
    n = conn.execute(
        "SELECT COUNT(*) AS c FROM score_archive WHERE snapshot_date = ?", (snap,)
    ).fetchone()["c"]
    conn.close()
    print(f"[archive] snapshot {snap}: {n} topics archived")
    return n


def archive_pull_history(db_path: str = DB_PATH) -> dict:
    """Persist a daily snapshot of the latest score per topic for BOTH feeds
    into pull_history (12-month durable store). Idempotent per day via the
    (snapshot_date, feed, topic_key) primary key. Run daily on the scheduler."""
    snap = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db(db_path)
    out = {"attention": 0, "risk": 0}
    # ── Attention feed (velocity_scores) ──
    try:
        conn.execute("""
            INSERT INTO pull_history
                (snapshot_date, feed, topic_key, topic_display, detection_score,
                 confidence_score, overall_score, signal_stage, total_signals, scored_at, archived_at)
            SELECT ?, 'attention', v.topic_key, v.topic_display, v.detection_score,
                   v.confidence_score, v.overall_score, v.signal_stage, v.total_mentions, v.scored_at, ?
            FROM velocity_scores v
            INNER JOIN (
                SELECT topic_key, MAX(scored_at) AS m FROM velocity_scores GROUP BY topic_key
            ) l ON v.topic_key = l.topic_key AND v.scored_at = l.m
            ON CONFLICT (snapshot_date, feed, topic_key) DO NOTHING
        """, (snap, now))
        conn.commit()
        out["attention"] = conn.execute(
            "SELECT COUNT(*) AS c FROM pull_history WHERE snapshot_date=? AND feed='attention'",
            (snap,)).fetchone()["c"]
    except Exception as e:
        print(f"[pull_history] attention archive error: {e}")
    # ── Risk feed (risk_scores) — positioning score stored in overall_score ──
    try:
        conn.execute("""
            INSERT INTO pull_history
                (snapshot_date, feed, topic_key, topic_display, detection_score,
                 confidence_score, overall_score, signal_stage, total_signals, scored_at, archived_at)
            SELECT ?, 'risk', r.risk_topic, r.risk_display, r.detection_score,
                   r.confidence_score, r.detection_score, r.risk_stage, r.total_signals, r.scored_at, ?
            FROM risk_scores r
            INNER JOIN (
                SELECT risk_topic, MAX(scored_at) AS m FROM risk_scores GROUP BY risk_topic
            ) l ON r.risk_topic = l.risk_topic AND r.scored_at = l.m
            ON CONFLICT (snapshot_date, feed, topic_key) DO NOTHING
        """, (snap, now))
        conn.commit()
        out["risk"] = conn.execute(
            "SELECT COUNT(*) AS c FROM pull_history WHERE snapshot_date=? AND feed='risk'",
            (snap,)).fetchone()["c"]
    except Exception as e:
        print(f"[pull_history] risk archive error: {e}")
    conn.close()
    print(f"[pull_history] {snap}: attention={out['attention']} risk={out['risk']} archived")
    return out


def prune_pull_history(db_path: str = DB_PATH, days: int = 365) -> int:
    """Drop pull_history rows older than 12 months (with a small buffer)."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    conn = get_db(db_path)
    cur = conn.execute("DELETE FROM pull_history WHERE snapshot_date < ?", (cutoff,))
    deleted = getattr(cur, "rowcount", 0) or 0
    conn.commit()
    conn.close()
    print(f"[pull_history] pruned {deleted} rows older than {days}d")
    return deleted


def prune_velocity_scores(db_path: str = DB_PATH, days: int = 30) -> int:
    """Delete velocity_scores older than `days`, always keeping the latest row per topic."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    conn = get_db(db_path)
    cur = conn.execute("""
        DELETE FROM velocity_scores
        WHERE scored_at < ?
          AND id NOT IN (
            SELECT v.id FROM velocity_scores v
            INNER JOIN (
                SELECT topic_key, MAX(scored_at) AS m FROM velocity_scores GROUP BY topic_key
            ) l ON v.topic_key = l.topic_key AND v.scored_at = l.m
          )
    """, (cutoff,))
    deleted = getattr(cur, "rowcount", 0) or 0
    conn.commit()
    conn.close()
    print(f"[retention] pruned {deleted} velocity_scores rows older than {days}d")
    return deleted


def prune_archive(db_path: str = DB_PATH, days: int = 395) -> int:
    """Drop research snapshots older than ~1 year."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    conn = get_db(db_path)
    cur = conn.execute("DELETE FROM score_archive WHERE snapshot_date < ?", (cutoff,))
    deleted = getattr(cur, "rowcount", 0) or 0
    conn.commit()
    conn.close()
    print(f"[retention] pruned {deleted} archive rows older than {days}d")
    return deleted


def run_retention() -> None:
    """Monthly job: snapshot latest scores for research, prune old detail, and
    reset membership credits (query + AI-grade) to each tier's allowance."""
    try:
        archive_scores_snapshot(DB_PATH)
        # 365-day per-cycle retention (canonical, founder decision 2026-06-24; matches
        # VELOCITY_KEEP_DAYS) — was a hardcoded 30 that would have silently overridden it.
        prune_velocity_scores(DB_PATH, days=int(os.getenv("VELOCITY_KEEP_DAYS", "365")))
        prune_archive(DB_PATH, days=395)
        # Reset monthly membership credits via the backend (internal-key gated).
        reset_url = os.getenv("CREDITS_RESET_URL")
        if reset_url:
            try:
                requests.post(reset_url,
                              headers={"X-Internal-Key": os.getenv("INTERNAL_API_KEY", "")},
                              timeout=30)
                print("[retention] monthly credit reset triggered.")
            except Exception as _cre:
                print(f"[retention] credit reset error: {_cre}")
    except Exception as exc:
        print(f"[retention] error: {exc}")


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
        """Fetch all signals for a topic in the time window.

        Excludes signals still tagged 'unverified' — these are uncorroborated
        broad-source headlines that the corroboration pass did NOT promote. By
        design they never enter the scoring set (an unverified source can never
        stand alone, and excluding them removes any count-padding leak into G).
        Corroborated ones were already re-tiered to 'mainstream' or made organic,
        so they ARE included."""
        conn = get_db(self.db_path)
        cutoff = (
            datetime.now(timezone.utc) - timedelta(hours=hours)
        ).isoformat()
        # LEFT JOIN raw_signals.title so dual_pathway can collapse wire-syndication
        # (identical headlines across outlets) when counting the mainstream news quorum (v2).
        # LEFT JOIN keeps every signal even if the raw row is gone (title → None, no collapse).
        rows = conn.execute("""
            SELECT ts.*, rs.title AS title
            FROM topic_signals ts
            LEFT JOIN raw_signals rs ON rs.id = ts.signal_id
            WHERE ts.topic_key = ? AND ts.extracted_at >= ?
              AND ts.platform_tier != 'unverified'
            ORDER BY ts.extracted_at ASC
        """, (topic_key, cutoff)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _consolidate_window_keys(self, conn, cutoff: str) -> int:
        """Fold morphological/entity VARIANT keys onto their canonical key
        (japanese→japan, japan's→japan, gpt→chatgpt) so a trend is scored — and
        served — ONCE. New pulls already write canonical keys; this self-heals the
        pool collected before the rule existed. Returns the number of keys folded.

        Two independent passes (the second is essential): variant signals may have
        been remapped in a PRIOR cycle, leaving an orphaned variant row in
        velocity_scores that no longer appears in topic_signals — so we clean
        velocity_scores by its OWN keys, not only the ones still in topic_signals."""
        folded = 0
        # ── 1) Fold variant SIGNALS in the window onto the canonical key ──
        for r in conn.execute(
                "SELECT DISTINCT topic_key FROM topic_signals WHERE extracted_at >= ?",
                (cutoff,)).fetchall():
            old = r["topic_key"]
            if not old:
                continue
            canon = _topic_key(old.replace("_", " "))
            if canon and canon != old:
                conn.execute("UPDATE topic_signals SET topic_key = ? WHERE topic_key = ?",
                             (canon, old))
                folded += 1
        # ── 2) Drop non-canonical SCORE rows (prior-cycle orphans) + single-word
        # common-word JUNK rows ('destroyed', 'novel') that were scored before the
        # quality gate ran at scoring. Multi-word keys are left alone (may be names).
        pruned = 0
        for r in conn.execute("SELECT DISTINCT topic_key FROM velocity_scores").fetchall():
            old = r["topic_key"]
            if not old:
                continue
            d = old.replace("_", " ")
            toks = d.split()
            non_canon = _topic_key(d) != old
            single_junk = (len(toks) <= 1) and not _is_quality_topic(d)
            frag = len(toks) >= 2 and (toks[0] in NEWS_FILLER or toks[-1] in NEWS_FILLER)
            if non_canon or single_junk or frag:
                conn.execute("DELETE FROM velocity_scores WHERE topic_key = ?", (old,))
                pruned += 1
        conn.commit()
        if folded or pruned:
            print(f"  [score] consolidated {folded} variant keys; pruned {pruned} stale/junk score rows")
        return folded

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

        # Score based on platform count. The old map pinned EVERY 4+-platform
        # topic at a flat 90 — no resolution at the top, a primary cause of
        # Detection saturating (a well-spread topic's M could never move, so the
        # M-weighted score froze). Keep the original anchors for 1-3 platforms,
        # but for 4+ use a continuous curve that passes through exactly 90 at 4
        # platforms (anchor preserved) and then climbs toward 100, so 4 vs 6 vs 9
        # platforms are distinguishable. Env-revertible for A/B + accuracy sweep.
        n_plat = len(platforms)
        if os.getenv("PLATFORM_DIVERSITY_CONTINUOUS", "1") == "1" and n_plat >= 4:
            base_score = 100 - 40.0 / n_plat   # 4→90, 5→92, 6→93.3, 9→95.6 …
        else:
            base_score = {1: 20, 2: 50, 3: 80}.get(n_plat, 90 if n_plat >= 4 else 0)

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
        # Across ALL platforms that carry author identity (not Reddit-only —
        # Reddit is off, which silently forced this to 0 on every topic). We
        # require a minimum sample so a 1-author topic can't read a spurious
        # 100%. Signals whose collector cannot resolve an author are excluded
        # from the denominator rather than counted as non-first-timers.
        MIN_FT_SAMPLE = 3
        if len(signals) >= MIN_FT_SAMPLE:
            first_timers = sum(1 for s in signals if s.get("is_first_timer"))
            ft_ratio = first_timers / len(signals)
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
        # Dark matter = evidence of HIDDEN activity, expressed by the two real
        # indicators: a first-timer surge and engagement asymmetry. With neither
        # present there is no hidden-activity evidence, so the score is ~0.
        #
        # First-timer score uses a CONCAVE curve (100 * ratio^0.7) rather than a
        # linear-with-hard-clip. The prior `ratio * 160` saturated at 62.5%, so a
        # 62.5% surge and a 100% flood scored identically — the engine had no
        # resolution at the high end. The power curve rewards early first-timers
        # generously, preserves full resolution up to a true 100% flood, and is
        # interpretable (100 is reserved for a total first-timer takeover).
        ft_score   = round(100 * (ft_ratio ** 0.7), 2)
        asym_score = 70 if asymmetry_detected else 0
        evidence   = ft_score * 0.65 + asym_score * 0.35

        # Organic concentration is an AUTHENTICITY GATE, not an additive floor.
        # It scales the evidence down when signals look manufactured (bots/spam),
        # but it can never CREATE dark matter on its own. Previously it added a
        # flat 15 to every organic topic, which made the score contradict the
        # "0% first-timer / normal asymmetry" indicators shown to the user.
        organic_ratio = (sum(1 for s in signals if s["is_organic"]) / len(signals)) if signals else 0.0
        quality = 0.4 + 0.6 * organic_ratio   # fully organic → 1.0, fully inorganic → 0.4

        dark_score = evidence * quality

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

        PLATFORM-TRACKING metric (NOT a user-demand claim). Measures how often this topic is
        TRIGGERED + SURFACED as a tracked topic across the platform — every time it appears in
        an API result (the /scores feed, /anomalies, /trending), in an on-demand /scores/{topic}
        query, or in a grade. `topic_queries` logs each such appearance (see _log_topic_query).
        It is therefore a platform-internal tracking/appearance frequency — do NOT describe it as
        "how often users asked about the topic"; the bulk is the engine surfacing the topic in
        its own feeds plus on-demand lookups/grades.

        Why it's kept SEPARATE: it is a platform-internal read with no public source, shown
        alongside every score but DELIBERATELY EXCLUDED from the Gradient (a score can't be
        validated by a signal produced by engagement with that score — no circular/feedback loop).

        Formula (0–100):
          volume_score  (0–70): log-scale of total appearances in last 30 days
          recency_score (0–30): recent 24h spike vs 7-day baseline rate

        Score meaning:
          0   = never surfaced/tracked
          1–20 = rare — a few appearances total
          20–50 = moderate — weekly appearances
          50–80 = frequent — daily appearances
          80+  = very frequently surfaced/tracked across the platform
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

            # Compute running peaks in Python (cross-engine: avoids SQLite's
            # 2-arg MAX() vs Postgres GREATEST() incompatibility).
            peak_overall = max(lc.get("peak_overall_score") or 0, overall)
            peak_det     = max(lc.get("peak_detection_score") or 0, det)
            peak_conf    = max(lc.get("peak_confidence_score") or 0, conf)

            conn.execute("""
                UPDATE topic_lifecycle SET
                    last_scored_at          = ?,
                    total_scoring_cycles    = ?,
                    cycles_above_emerging   = ?,
                    cycles_above_strong     = ?,
                    cycles_above_breakout   = ?,
                    peak_overall_score      = ?,
                    peak_detection_score    = ?,
                    peak_confidence_score   = ?,
                    current_streak_cycles   = ?,
                    longest_streak_cycles   = ?,
                    persistence_rate        = ?,
                    trend_age_hours         = ?,
                    confirmed_trend         = ?,
                    updated_at              = datetime('now')
                WHERE topic_key = ?
            """, (
                now_str, total, above_e, above_s, above_b,
                peak_overall, peak_det, peak_conf,
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
            # Admit a single mass-attention signal (e.g. a 777K-view discovery
            # entity) even below the count floor — magnitude is its own evidence.
            if not any(float(s.get("engagement_raw", 0) or 0) >= HIGH_MAGNITUDE_ENG
                       for s in signals):
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

        # ── Honest momentum (single source: the stored velocity_scores history) ──
        # Replaces (a) an inertia calc that read ~100 on a FLAT trace and (b) a
        # persistence value tied to a lifecycle counter that disagreed with the
        # stored history — the root cause of the false "first collection cycle"
        # message, persistence 0 on a 12-cycle-held topic, and inertia 100 on a
        # flat one. Computed from prior cycles (current row not yet inserted), so
        # both the displayed components AND the composite below use honest values.
        momentum_signal_read = None
        momentum_cycle_count = 0
        if os.getenv("MOMENTUM_ENGINE", "1") == "1":
            try:
                import momentum_engine as _mom
                _hist = _mom.read_scoring_history(topic_key, db_path=self.db_path)
                momentum_cycle_count = len(_hist)
                _in = _mom.compute_inertia(_hist)
                _pe = _mom.compute_persistence(_hist)
                if momentum_cycle_count >= 2:
                    I = _in["inertia"]
                    P = _pe["persistence"]
                momentum_signal_read = _mom.generate_signal_read(_hist, _in, _pe)
            except Exception as _mex:
                print(f"  momentum: skipped ({_mex})")

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
        # Re-cap G at 100 after the signal-count modifier (it's a MULTIPLIER and
        # was pushing high-volume topics' Gradient Strength past 100, e.g.
        # claude_code stored G=112 — a 0-100 component must never exceed its cap,
        # and the uncapped value also inflated the Detection composite input).
        G = max(0.0, min(100.0, G))

        # ── Composite scores (G·I·M·D·C·P·N) ──────────────────
        #
        # Key insight:
        #   Detection weights G+N highest → fires on niche concentration + user demand
        #   Confidence weights I+P highest → fires only after sustained multi-cycle evidence
        #   N for Detection: if users are searching it = real-world demand validation
        #   N for Confidence: moderate weight — queries alone don't confirm a trend

        # ── N (internal demand) is DELIBERATELY EXCLUDED from the composite ──
        # The Gradient Score measures EXTERNAL-WORLD attention only. Blending our
        # own users' demand (N) would create a feedback loop (users search → score
        # rises → they search more) and compromise the objectivity institutions pay
        # for. N is computed and DISPLAYED as a separate "community demand" signal,
        # never folded into Detection/Confidence/Overall. The six external
        # components below are renormalized to sum to 1.0 (was 7-component w/ N).

        # Composite scores from the SINGLE-SOURCE weight vectors (_W_* imported from
        # scoring_weights.py at module top). Component emphasis per vector:
        #   OVERALL     — balanced across the six external components
        #   DETECTION   — speed first (G + D weighted highest, fires early)
        #   CONFIDENCE  — precision first (I + P weighted highest, confirms late)
        # N (internal demand) is excluded by design (no-circularity); the six are
        # renormalized to sum to 1.0 in scoring_weights.py.
        # Iterate each vector in ITS OWN declared key order (scoring_weights.py declares
        # them in the historical inline order: OVERALL G,I,M,D,C,P · DETECTION G,D,I,M,C,P
        # · CONFIDENCE I,P,M,G,C,D) so float accumulation is bit-identical to the prior
        # inline formula — a provably zero-score-impact refactor (verified across 20k vectors).
        _comp = {"G": G, "I": I, "M": M, "D": D, "C": C, "P": P}
        overall    = round(min(100, _weighted(_comp, _W_OVERALL)),    2)
        detection  = round(min(100, _weighted(_comp, _W_DETECTION)),  2)
        confidence = round(min(100, _weighted(_comp, _W_CONFIDENCE)), 2)

        # ── Phase C: dual-pathway recalibration ───────────────────
        # For mainstream-origin topics (consumer culture from discovery feeds),
        # replace the expert-gradient detection — which is structurally ~0 for
        # them — with one driven by absolute attention MAGNITUDE + breadth +
        # acceleration. Expert-origin topics (mainstream_ratio ~ 0) are left
        # IDENTICAL, so the tech early-detection moat is untouched. Diagnostics
        # are surfaced on the row so the pathway is auditable.
        # Dual-pathway diagnostics default here; the actual blend runs AFTER
        # apply_calibration in score_all_topics (calibration recomputes
        # detection, so blending at this point would be overwritten downstream).
        pathway = "expert"
        mainstream_ratio = 0.0
        attention_magnitude = 0.0
        mainstream_breadth = 0.0
        n_mainstream_platforms = 0

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
            "category":      _topic_category(display),
            "detection_pathway":   pathway,            # expert | blended | mainstream
            "mainstream_ratio":    mainstream_ratio,   # effective mainstream weight (max of breadth, magnitude)
            "attention_magnitude": attention_magnitude,
            "mainstream_breadth":  mainstream_breadth, # cross-platform corroboration 0-1
            "n_mainstream_platforms": n_mainstream_platforms,
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

            # Persistence / lifecycle data. cycle count prefers the momentum
            # engine's real count (from stored history) over the lifecycle
            # counter, which could lag and falsely trigger "first collection cycle".
            "persistence_cycles":  max(lifecycle_data["total_cycles"], momentum_cycle_count),
            "momentum_cycle_count": momentum_cycle_count,
            "momentum_signal_read": json.dumps(momentum_signal_read) if momentum_signal_read else None,
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

        # Express concentration via the MEASURED niche:mainstream ratio
        # (== the component's raw_ratio field) so the narrative and the
        # "Niche Concentration" component never cite conflicting numbers. The
        # earlier "{G}% niche concentration" used the raw pre-calibration score,
        # which disagreed with the calibrated value shown on the component bar.
        ratio_txt = (f"about {gradient_ratio:.0f}x more discussion in expert/niche "
                     f"than mainstream spaces") if gradient_ratio and gradient_ratio >= 2 \
            else "concentrated in expert/niche spaces"
        if G >= 75:
            parts.append(
                f"'{topic}' is heavily concentrated in expert/niche communities "
                f"({ratio_txt}) — limited mainstream pickup in the sources we track so far"
            )
        elif G >= 50:
            parts.append(
                f"'{topic}' is concentrated in specialist spaces ({ratio_txt}) "
                f"with early mainstream presence building"
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

        # Provenance promotion (runs before scoring): quarantined unverified-source
        # news signals are promoted to their corroborated weight + routed to the
        # right component (D vs M), or left inert at ~1% if uncorroborated. This is
        # the integrity balance — broad sources earn weight only by independent
        # confirmation, never standing alone.
        try:
            corroborate_unverified_news(conn, hours=hours)
        except Exception as _ce:
            print(f"  [score] corroboration skipped: {_ce}")

        # ── Consolidate variant keys in the window BEFORE scoring ──
        # New pulls already write canonical keys (_topic_key), but the existing
        # 72h pool can still hold variants (japanese vs japan) collected before
        # the rule existed. Fold them now so the dyno scores each trend ONCE.
        try:
            self._consolidate_window_keys(conn, cutoff)
        except Exception as _cwe:
            print(f"  [score] key consolidation skipped: {_cwe}")

        # Get unique topic keys active in this window that are actually
        # SCOREABLE. score_topic() returns None for topics with fewer than
        # MIN_TOPIC_APPEARANCES signals, so filtering at the SQL level (instead
        # of iterating + discarding) is a pure performance fix — identical
        # output, but it stops the scorer drowning in the ~200k single-mention
        # fragment n-grams that the extractor produces. A high-magnitude single
        # signal (e.g. a 777K-view Wikipedia entity) is also admitted via the
        # MAX(engagement_raw) clause so genuine mass-attention discovery items
        # are never starved by the count gate.
        # Candidate query also returns the corroboration signals the catch-all
        # floor needs (distinct sources, peak engagement, any expert-tier row) so
        # we don't re-query per topic.
        rows = conn.execute("""
            SELECT topic_key,
                   COUNT(DISTINCT source_name) AS nsrc,
                   MAX(engagement_raw)         AS maxe,
                   MAX(CASE WHEN platform_tier IN ('expert','niche') THEN 1 ELSE 0 END) AS hasx
            FROM topic_signals
            WHERE extracted_at >= ?
            GROUP BY topic_key
            HAVING COUNT(*) >= ? OR MAX(engagement_raw) >= ?
        """, (cutoff, MIN_TOPIC_APPEARANCES, HIGH_MAGNITUDE_ENG)).fetchall()

        topic_keys = [r["topic_key"] for r in rows]
        _corro = {r["topic_key"]: (int(r["nsrc"] or 0), float(r["maxe"] or 0.0),
                                   int(r["hasx"] or 0)) for r in rows}
        # Quality gate at SCORING (not just serve), so junk never gets stored:
        #   • single-word common-word junk ("destroyed", "novel")
        #   • multi-word HEADLINE FRAGMENTS anchored by a news-filler token
        #     ("end iran war", "media starmer announces")
        # Multi-word NON-fragment keys pass (may be proper-noun names like
        # "michael chandler" the lowercase filter can't disambiguate — let serve
        # decide those).
        def _scoreable(tk: str) -> bool:
            d = (tk or "").replace("_", " ")
            toks = d.split()
            if len(toks) >= 2 and (toks[0] in NEWS_FILLER or toks[-1] in NEWS_FILLER):
                return False
            if len(toks) <= 1:
                return _is_quality_topic(d)
            return True
        _pre = len(topic_keys)
        topic_keys = [tk for tk in topic_keys if _scoreable(tk)]
        _skipped = _pre - len(topic_keys)

        # ── Catch-all CORROBORATION floor (de-congest the 'news'/general pile) ──
        # Drop a catch-all topic carried by < CATCHALL_MIN_SOURCES distinct
        # sources. Backtest-verified to remove ~43% single-source catch-all noise
        # with ZERO loss to the accuracy ledger / pending detections (the moat).
        _corro_dropped = 0
        if CATCHALL_MIN_SOURCES > 1:
            # tracked calls are never dropped (a detection we committed to)
            _protected = set()
            for _t in ("accuracy_ledger", "pending_detections"):
                try:
                    for _rr in conn.execute(f"SELECT DISTINCT topic_key FROM {_t}").fetchall():
                        _protected.add(_rr["topic_key"])
                except Exception:
                    pass

            def _passes_corroboration(tk: str) -> bool:
                nsrc, maxe, hasx = _corro.get(tk, (0, 0.0, 0))
                # moat / mass-attention / tracked-call exemptions — always keep
                if hasx or maxe >= HIGH_MAGNITUDE_ENG or tk in _protected:
                    return True
                try:
                    cat = _topic_category((tk or "").replace("_", " ")) or ""
                except Exception:
                    cat = ""
                if cat in _CATCHALL_CATS:
                    return nsrc >= CATCHALL_MIN_SOURCES
                return True  # non-catch-all: unchanged

            _pre2 = len(topic_keys)
            topic_keys = [tk for tk in topic_keys if _passes_corroboration(tk)]
            _corro_dropped = _pre2 - len(topic_keys)

        print(f"\nScoring {len(topic_keys)} scoreable topics "
              f"(filtered from raw fragment pool"
              f"{f'; skipped {_skipped} single-word junk' if _skipped else ''}"
              f"{f'; dropped {_corro_dropped} single-source catch-all' if _corro_dropped else ''})...")

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

            # ── Phase C: dual-pathway recalibration (runs LAST, after
            # calibration, so it isn't overwritten). Mainstream-origin topics
            # (broad cross-platform corroboration OR mass attention magnitude)
            # are scored on magnitude+breadth instead of the expert gradient
            # that is structurally ~0 for them; expert-origin topics are
            # untouched (the moat). Stage is recomputed from the new overall. ──
            if _DUAL_PATHWAY and _dual is not None:
                try:
                    # Baseline-relative inputs: the topic's OWN rolling footprint
                    # (prior cycles only — the current row isn't written yet), so
                    # mainstreaming is measured as deviation, not absolute (fame).
                    _brd_base = _mag_base = None
                    _base_cycles = 0
                    try:
                        _hist = conn.execute(
                            "SELECT attention_magnitude, n_mainstream_platforms "
                            "FROM velocity_scores WHERE topic_key = ? "
                            "ORDER BY scored_at DESC LIMIT 12", (topic_key,)).fetchall()
                        if _hist:
                            _base_cycles = len(_hist)
                            _mags = sorted(float(r["attention_magnitude"] or 0) for r in _hist)
                            _brs = sorted(float(r["n_mainstream_platforms"] or 0) for r in _hist)
                            _mag_base = _mags[len(_mags) // 2]   # median footprint
                            _brd_base = _brs[len(_brs) // 2]
                    except Exception:
                        pass
                    _b = _dual.blend(
                        result.get("detection_score", 0) or 0,
                        result.get("overall_score", 0) or 0,
                        {"M": result.get("platform_diversity", 0) or 0,
                         "I": result.get("inertia_score", 0) or 0,
                         "P": result.get("persistence_score", 0) or 0},
                        signals,
                        breadth_baseline=_brd_base,
                        magnitude_baseline=_mag_base,
                        baseline_cycles=_base_cycles,
                        expert_confidence=result.get("confidence_score", 0) or 0)
                    result["detection_score"] = _b["detection"]
                    result["overall_score"]   = _b["overall"]
                    # Fix #3: blend CONFIDENCE through the mainstream pathway too, so a
                    # mainstream topic's confidence reflects its magnitude/breadth
                    # instead of the ~constant expert value (FIFA vs obama both 58).
                    if _b.get("confidence") is not None:
                        result["confidence_score"] = _b["confidence"]
                    result["heisenberg_gap"]  = round(
                        _b["detection"] - (result.get("confidence_score", 0) or 0), 1)
                    result["detection_pathway"]      = _b["pathway"]
                    result["mainstream_ratio"]       = _b["mainstream_ratio"]
                    result["attention_magnitude"]    = _b["magnitude"]
                    result["mainstream_breadth"]     = _b["breadth"]
                    result["n_mainstream_platforms"] = _b["n_mainstream_platforms"]
                    result["news_outlets"]           = _b.get("news_outlets", 0)
                    result["mainstream_confirmed"]   = _b.get("mainstream_confirmed", False)
                    result["tier_migration"]         = _b.get("tier_migration", False)
                    result["n_expert_communities"]   = _b.get("n_expert_communities", 0)
                    _ov = _b["overall"]
                    result["signal_stage"] = (
                        "BREAKOUT"  if _ov >= BREAKOUT_THRESHOLD else
                        "STRONG"    if _ov >= STRONG_THRESHOLD   else
                        "EMERGING"  if _ov >= EMERGING_THRESHOLD else
                        "WATCHING"  if _ov >= WATCHING_THRESHOLD else
                        "MONITORING")
                except Exception as _de:
                    print(f"  dual_pathway(post-cal) {topic_key}: skipped ({_de})")

            # ── Update lifecycle BEFORE computing P for next cycle ──
            # (P for this cycle was already computed using pre-update history)
            self._update_topic_lifecycle(conn, result)

            # FINAL stored-gap recompute (invariant: persisted heisenberg_gap == stored
            # detection - confidence, SIGNED). apply_calibration and the dual-pathway
            # blend both move det/conf AFTER the score-time gap was set at line ~4036;
            # the dual-pathway branch recomputes it only when it fires, so expert/niche
            # rows were left stale (the Scoring Contract Auditor flagged 33/800). Recompute
            # unconditionally here so the persisted column can never drift from its inputs.
            result["heisenberg_gap"] = round(
                (result.get("detection_score", 0) or 0) - (result.get("confidence_score", 0) or 0), 1)

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
                    anomaly_reason, why_this_matters, what_to_watch,
                    attention_magnitude, n_mainstream_platforms,
                    detection_pathway, mainstream_ratio, mainstream_breadth,
                    news_outlets, mainstream_confirmed, tier_migration
                ) VALUES (
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?
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
                result.get("attention_magnitude", 0) or 0,
                result.get("n_mainstream_platforms", 0) or 0,
                result.get("detection_pathway", "expert") or "expert",
                result.get("mainstream_ratio", 0) or 0,
                result.get("mainstream_breadth", 0) or 0,
                int(result.get("news_outlets", 0) or 0),
                1 if result.get("mainstream_confirmed") else 0,
                1 if result.get("tier_migration") else 0,
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
                    total_mentions    = topic_registry.total_mentions + excluded.total_mentions,
                    niche_mentions    = topic_registry.niche_mentions + excluded.niche_mentions,
                    mainstream_mentions = topic_registry.mainstream_mentions + excluded.mainstream_mentions,
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


def _require_internal(x_internal_key: str = Header(None)):
    """Gate expensive/write endpoints to our own backend. Enforces ONLY when
    INTERNAL_API_KEY is set on the engine (so an unset key can never lock us
    out); rejects mismatches with 403. Read endpoints are NOT gated."""
    expected = os.getenv("INTERNAL_API_KEY", "")
    if expected and x_internal_key != expected:
        raise HTTPException(status_code=403, detail="Forbidden — internal endpoint")
    return True

# ── Enterprise intelligence layer (methodology versioning, per-component
# audit attribution, scenario projections) — ported from the v1 extensions
# layer onto the live 7-component Postgres engine. Read-only, no new tables.
try:
    from enterprise_intel import build_router as _build_ent_router
    # Lambda defers the name lookup to request time (_calibrate_score_fields is
    # defined later in this module than this mount point).
    app.include_router(_build_ent_router(
        get_db, DB_PATH, calibrate_fn=lambda r: _calibrate_score_fields(r)))
    print("[startup] enterprise_intel loaded — methodology/audit/scenarios active")
except Exception as _ent_exc:
    print(f"[startup] enterprise_intel unavailable: {_ent_exc}")


_SCHEDULER_STARTED = False


# ── Hybrid worker heartbeat ───────────────────────────────────────────────
# The heavy SCORING job runs on a local worker (free hardware); the Heroku
# worker COLLECTS every 6h and only SCORES as failover when the local scorer
# goes quiet. The local scorer stamps a heartbeat after each cycle; the Heroku
# failover reads it. One shared DB, so the heartbeat coordinates both.
def _write_heartbeat(role: str) -> None:
    try:
        conn = get_db(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS worker_heartbeat "
                     "(role TEXT PRIMARY KEY, beat_at TEXT)")
        now = datetime.now(timezone.utc).isoformat()
        try:
            conn.execute("INSERT INTO worker_heartbeat (role, beat_at) VALUES (?, ?) "
                         "ON CONFLICT (role) DO UPDATE SET beat_at = EXCLUDED.beat_at",
                         (role, now))
        except Exception:
            conn.rollback()
            conn.execute("UPDATE worker_heartbeat SET beat_at=? WHERE role=?", (now, role))
            if conn.execute("SELECT 1 FROM worker_heartbeat WHERE role=?", (role,)).fetchone() is None:
                conn.execute("INSERT INTO worker_heartbeat (role, beat_at) VALUES (?,?)", (role, now))
        conn.commit(); conn.close()
    except Exception as _hbe:
        print(f"[heartbeat] write {role} failed: {_hbe}")


def _heartbeat_age_min(role: str) -> float:
    """Minutes since `role` last beat; large number if never."""
    try:
        conn = get_db(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS worker_heartbeat "
                     "(role TEXT PRIMARY KEY, beat_at TEXT)")
        row = conn.execute("SELECT beat_at FROM worker_heartbeat WHERE role=?", (role,)).fetchone()
        conn.close()
        if not row:
            return 1e9
        # Rows are dict-keyed on this DB (psycopg DictRow), so positional row[0]
        # raises KeyError → the old code silently returned 1e9 ("never") for EVERY
        # heartbeat, breaking failover detection + the Scorer Watchdog. Read by name,
        # fall back to positional for sqlite tuple rows.
        try:
            beat_at = row["beat_at"]
        except (KeyError, TypeError, IndexError):
            beat_at = row[0]
        if not beat_at:
            return 1e9
        beat = datetime.fromisoformat(str(beat_at))
        if beat.tzinfo is None:
            beat = beat.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - beat).total_seconds() / 60.0
    except Exception:
        return 1e9


def start_scheduler():
    """Build and start the background APScheduler. Role-gated for the hybrid:
      WORKER_COLLECT (default 1)  — run the collectors (Heroku, every
        COLLECT_INTERVAL_MIN, default 360 = 6h).
      WORKER_SCORE   (default 1)  — "1" always score every SCORE_INTERVAL_MIN
        (the LOCAL scorer); "failover" score only when the local heartbeat is
        older than SCORE_STALE_MIN (the Heroku safety net); "0" never score.
    The local worker runs COLLECT=0 SCORE=1; the Heroku worker runs COLLECT=1
    SCORE=failover. Safe to call once per process."""
    global _SCHEDULER_STARTED
    if _SCHEDULER_STARTED:
        return None
    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        def _collect_phase():
            """Pull data only (the always-on cloud job). No heavy scoring."""
            try:
                c = get_db(DB_PATH)
                for _nm, _fn in (("reddit", collect_reddit),
                                 ("github", collect_github),
                                 ("hackernews", collect_hackernews),
                                 ("newsapi_org", collect_newsapi_org),
                                 ("newsapi_ai", collect_newsapi_ai),
                                 ("newsdata_io", collect_newsdata_io),
                                 ("currents", collect_currents_news),
                                 ("rss_direct", collect_rss_news),
                                 ("yahoo_finance", collect_yahoo_finance_news),
                                 ("bluesky", collect_bluesky),
                                 ("lemmy", collect_lemmy),
                                 ("mastodon", collect_mastodon),
                                 ("gdelt", collect_gdelt_trends),
                                 # YouTube trend collectors — now FREE (channel RSS,
                                 # 0 API quota), so they run in the reliable main
                                 # cycle (boot + every 6h) instead of a fragile
                                 # quota-bound cron that kept them DOWN.
                                 ("creators", collect_creator_trends),
                                 ("broadcast", collect_broadcast_trends)):
                    try:
                        _n = _fn(c) or 0
                        _log_health(_nm, _n, "success", conn=c)
                    except Exception as _ce:
                        _log_health(_nm, 0, "failure", conn=c)
                        print(f"[scheduler] {_nm} error: {_ce}")
                # Mainstream-news/YouTube coverage for top topics (separate arg).
                try:
                    _mn = collect_mainstream_news(c, limit=int(os.getenv("MAINSTREAM_NEWS_LIMIT", "12"))) or 0
                    _log_health("youtube", _mn, "success", conn=c)
                except Exception as _mne:
                    _log_health("youtube", 0, "failure", conn=c)
                    print(f"[scheduler] mainstream-news error: {_mne}")
                c.close()
                if _BLOGS_AVAILABLE:
                    try:
                        _blog_res = _bc.collect_all_blogs() or {}
                        _bn = int((_blog_res.get("_total") or {}).get("signals", 0) or 0)
                        _log_health("blogs", _bn, "success")
                    except Exception as _be:
                        _log_health("blogs", 0, "failure")
                        print(f"[scheduler] blog collect error: {_be}")
                if _DISCOVERY_AVAILABLE:
                    try:
                        c2 = get_db(DB_PATH); _dc.collect_all_discovery(c2); c2.close()
                    except Exception as _de:
                        print(f"[scheduler] discovery error: {_de}")
                if _RISK_AVAILABLE:
                    try:
                        _rres = risk.run_risk_collection(DB_PATH) or {}
                        _rn = sum(v for v in _rres.values() if isinstance(v, (int, float)))
                        risk.score_all_risks(DB_PATH)
                        _log_health("risk", int(_rn), "success")
                        print("[scheduler] risk cycle complete.")
                    except Exception as _rce:
                        _log_health("risk", 0, "failure")
                        print(f"[scheduler] risk error: {_rce}")
                # Crypto Money Gradient — record a cycle per coin so baseline-relative z-scores
                # build over time (reads CALIBRATING until ~3 cycles). Gated on CRYPTO_SIGNAL.
                if _CRYPTO_AVAILABLE and crypto_engine.CRYPTO_SIGNAL:
                    try:
                        _cr = crypto_engine.serve_crypto(record=True, db_path=DB_PATH)
                        print(f"[scheduler] crypto cycle: recorded {_cr.get('count', 0)} coins")
                        # Held-out accuracy ledger: log falsifiable detections + resolve pending vs
                        # realized coin price (no-lookahead). Never feeds the score.
                        if _CRYPTO_LEDGER_AVAILABLE:
                            crypto_ledger.record_from_serve(_cr, db_path=DB_PATH)
                            crypto_ledger.sweep_crypto_pending(DB_PATH, limit=60)
                    except Exception as _cce:
                        print(f"[scheduler] crypto error: {_cce}")
                print("[scheduler] collect phase complete.")
            except Exception as _ce:
                print(f"[scheduler] collect phase error: {_ce}")

        def _score_phase():
            """The heavy job: score every topic, record ledger, prune, precompute,
            fire alerts. Runs on the local worker (or Heroku failover). Stamps the
            'score' heartbeat so the failover knows the scorer is alive."""
            try:
                detector.score_all_topics(hours=72)
                _cache.invalidate()
                print("[scheduler] score cycle complete.")
                try:
                    _record_top_detections(limit=int(os.getenv("LEDGER_RECORD_TOP", "20")))
                except Exception as _lre:
                    print(f"[scheduler] ledger record error: {_lre}")
                try:
                    _prune_velocity_scores(int(os.getenv("VELOCITY_RETENTION_DAYS", "365")))
                    _prune_anomaly_log(int(os.getenv("KEEP_ANOMALY_DAYS", "30")))
                except Exception as _pe:
                    print(f"[scheduler] prune error: {_pe}")
                try:
                    _precompute_serve_payloads(int(os.getenv("PRECOMPUTE_TOP_N", "600")))
                    _cache.invalidate()
                    # NOTE: the superset /scores + /topics caches are kept hot by the
                    # dedicated Prewarm Agent thread in the API process (per-process
                    # cache), not here in the worker — see _prewarm_loop / startup.
                except Exception as _ppe:
                    print(f"[scheduler] precompute error: {_ppe}")
                _exp_n = int(os.getenv("EXPLAINER_BACKFILL_PER_CYCLE", "0"))
                if _exp_n > 0:
                    try:
                        _backfill_explainers(limit=_exp_n)
                    except Exception as _ee:
                        print(f"[scheduler] explainer backfill error: {_ee}")
                eval_url = os.getenv("ALERT_EVAL_URL")
                if eval_url:
                    try:
                        requests.post(
                            eval_url,
                            headers={"X-Internal-Key": os.getenv("INTERNAL_API_KEY", "dev-internal-key")},
                            timeout=25,
                        )
                    except Exception as _ae:
                        print(f"[scheduler] alert eval error: {_ae}")
                _write_heartbeat("score")
                # Stamp WHICH scorer ran (local worker vs Heroku cloud/failover) so
                # the Scorer Watchdog can report who is alive — read from env at call
                # time (no closure dependency). WORKER_COLLECT=0 == the local score-
                # only worker; otherwise this is the Heroku cloud collect+score dyno.
                _is_local = os.getenv("WORKER_COLLECT", "1").lower() not in ("1", "true", "yes")
                _write_heartbeat("score_local" if _is_local else "score_cloud")
            except Exception as _ce:
                print(f"[scheduler] score phase error: {_ce}")

        def _scheduled_cycle():
            """Full collect+score (single-role / dev fallback)."""
            _collect_phase()
            _score_phase()

        def _failover_score():
            """Heroku safety net: score ONLY if the local scorer has gone quiet."""
            age = _heartbeat_age_min("score")
            stale = float(os.getenv("SCORE_STALE_MIN", "45"))
            if age > stale:
                print(f"[scheduler] local scorer stale ({age:.0f}m > {stale:.0f}m) — failover scoring.")
                _score_phase()

        def _scheduled_velocities():
            try:
                from signal_calibration_integration import recompute_velocities
                recompute_velocities(DB_PATH)
                print("[scheduler] velocities recomputed.")
            except Exception as _ve:
                print(f"[scheduler] velocity error: {_ve}")
            if _ACCURACY_AVAILABLE:
                try:
                    accuracy.validate_recent_detections(DB_PATH)
                except Exception as _ae:
                    print(f"[scheduler] accuracy error: {_ae}")
            # NOTE: the honest-denominator ledger sweep moved OUT of this once-daily
            # velocity recompute into its own job (_scheduled_ledger_sweep), so it can
            # run several times a day and drain the pending pool faster — see below.

        def _scheduled_ledger_sweep():
            """Resolve pending detections into hits / counted misses — a capped batch
            per run (LEDGER_SWEEP_LIMIT), rotating OLDEST-CHECKED-FIRST so the whole
            pool drains over time (fix #1) instead of re-checking the same head rows.
            Decoupled from the daily velocity recompute and run every
            LEDGER_SWEEP_INTERVAL_HOURS so the slow-to-confirm LED wins surface sooner.
            COST: each still-in-window row spends one Apify Trends fetch; rows already
            past their timeout resolve FREE — no fetch (fix #2). Tune cadence/limit
            against the Apify budget (Cost Sentinel /monitor/cost, apify_trends)."""
            if _LEDGER_PLUS_AVAILABLE:
                try:
                    # Uncapped by default (LEDGER_SWEEP_LIMIT=0 → drain the whole pool); a positive
                    # value bounds each run for operational latency. Raised from the old 8 now that the
                    # per-result Trends fetch is known-cheap ($0.001) — that cap throttled the held-out
                    # MEASUREMENT only (never a score). Budget-guarded so it can't starve collection.
                    _lim_env = int(os.getenv("LEDGER_SWEEP_LIMIT", "300"))
                    _lim = None if _lim_env <= 0 else _lim_env
                    _g = _apify_sweep_budget_ok()
                    if _g["ok"]:
                        out = ledger_plus.sweep_pending(DB_PATH, limit=_lim)
                        print(f"[scheduler] ledger sweep (apify {_g.get('used')}/{_g.get('cap')}): {out}")
                    else:
                        # Near the Apify cap → resolve FREE timeouts only (fetch_fn→None, no paid Trends
                        # fetch), so the sweep never starves the main collection pipeline.
                        out = ledger_plus.sweep_pending(DB_PATH, limit=_lim, fetch_fn=lambda *_a, **_k: None)
                        print(f"[scheduler] ledger sweep BUDGET-GUARDED (apify {_g.get('used')}/{_g.get('cap')}, "
                              f"reserve ${_g.get('reserve')}): timeouts-only {out}")
                except Exception as _se:
                    print(f"[scheduler] ledger sweep error: {_se}")
            # MARKET-SIGNAL ledger sweep (Money Gradient) — validates money-movement
            # detections against realized EOD price direction (FMP), DISTINCT from the
            # Google-Trends attention sweep above. Only when MARKET_SIGNAL_V2 is on. FMP
            # calls are cheap/free-tier; past-deadline rows resolve without a fetch.
            if _MARKET_LEDGER_AVAILABLE and os.getenv("MARKET_SIGNAL_V2", "0") == "1":
                try:
                    mout = market_ledger.sweep_market_pending(
                        DB_PATH, limit=int(os.getenv("MARKET_LEDGER_SWEEP_LIMIT", "20")))
                    print(f"[scheduler] market ledger sweep: {mout}")
                except Exception as _mse2:
                    print(f"[scheduler] market ledger sweep error: {_mse2}")

        _sched = BackgroundScheduler(timezone="UTC")
        # ── Hybrid role gating ──
        _w_collect = os.getenv("WORKER_COLLECT", "1").lower() in ("1", "true", "yes")
        _w_score = os.getenv("WORKER_SCORE", "1").lower()
        _collect_min = int(os.getenv("COLLECT_INTERVAL_MIN", "30"))
        # ── Stale window safety check ─────────────────────────────────────────────
        # collector_health max_gap_minutes MUST exceed the actual collection cadence
        # + 1h margin or it fires STALE on every cycle (the source of the false
        # CRITICAL alert on the risk collector — see collector_health.py comment).
        # Risk runs inside _collect_phase, so its window must track COLLECT_INTERVAL_MIN.
        try:
            from collector_health import COLLECTOR_EXPECTATIONS as _CE
            _gap_margin = 60
            for _cn, _ce in _CE.items():
                if _ce.get("critical") and _ce.get("max_gap_minutes", 9999) < (_collect_min + _gap_margin):
                    print(f"[scheduler] WARNING: collector_health '{_cn}' max_gap_minutes="
                          f"{_ce['max_gap_minutes']} < COLLECT_INTERVAL_MIN={_collect_min}"
                          f"+{_gap_margin}m margin — will fire STALE every cycle. "
                          f"Set max_gap_minutes >= {_collect_min + _gap_margin}.")
        except Exception as _she:
            print(f"[scheduler] stale-window check skipped: {_she}")
        _score_min = int(os.getenv("SCORE_INTERVAL_MIN", "30"))
        _soon = datetime.now(timezone.utc) + timedelta(seconds=20)  # fire shortly after boot
        if _w_collect:
            # Score WITH collect (default): scoring runs only when fresh data is
            # pulled (every COLLECT_INTERVAL_MIN, default 6h) — not on its own
            # frequent cadence. On-demand Enterprise pulls hit /collect, which
            # also collects+scores. Set SCORE_WITH_COLLECT=0 to collect only.
            _score_with = os.getenv("SCORE_WITH_COLLECT", "1").lower() in ("1", "true", "yes")
            _collect_fn = _scheduled_cycle if _score_with else _collect_phase
            _sched.add_job(_collect_fn, "interval", minutes=_collect_min,
                           id="collect", max_instances=1, coalesce=True,
                           misfire_grace_time=600, next_run_time=_soon)
            print(f"[scheduler] COLLECT job every {_collect_min}m" + (" + SCORE" if _score_with else ""))
        if _w_score in ("1", "true", "yes"):
            _sched.add_job(_score_phase, "interval", minutes=_score_min,
                           id="score", max_instances=1, coalesce=True,
                           misfire_grace_time=600, next_run_time=_soon)
            print(f"[scheduler] SCORE job every {_score_min}m (primary scorer)")
        elif _w_score == "failover":
            _fail_min = int(os.getenv("FAILOVER_CHECK_MIN", "20"))
            _sched.add_job(_failover_score, "interval", minutes=_fail_min,
                           id="failover_score", max_instances=1, coalesce=True,
                           misfire_grace_time=300, next_run_time=_soon)
            print(f"[scheduler] SCORE failover every {_fail_min}m (if local stale > "
                  f"{os.getenv('SCORE_STALE_MIN', '45')}m)")
        # Local scorer (WORKER_COLLECT=0): score-only. Skip ALL the cloud aux
        # jobs below (velocities, X scan, google-trends, retention, vacuum, …) —
        # those run on the always-on Heroku collect worker, never duplicated
        # locally (they spend API budget and do destructive retention).
        if not _w_collect:
            _sched.start()
            _SCHEDULER_STARTED = True
            print("[scheduler] started — LOCAL SCORER (score job only; cloud aux jobs skipped).")
            return _sched
        _sched.add_job(_scheduled_velocities, "cron", hour=6, minute=0,
                       id="recompute_velocities", max_instances=1,
                       coalesce=True)
        # Ledger sweep on its OWN cadence (default every 6h = 4×/day, up from the old
        # once-daily piggyback) so pending detections — especially the slow-to-confirm
        # LED wins — drain faster. Capped at LEDGER_SWEEP_LIMIT/run; timed-out rows
        # resolve without a fetch. Cadence/limit are env-tunable against the Apify
        # Trends budget (each in-window row = one Apify run; watch /monitor/cost).
        _ledger_sweep_h = int(os.getenv("LEDGER_SWEEP_INTERVAL_HOURS", "6"))
        _sched.add_job(_scheduled_ledger_sweep, "interval", hours=_ledger_sweep_h,
                       id="ledger_sweep", max_instances=1, coalesce=True,
                       misfire_grace_time=600, next_run_time=_soon)
        print(f"[scheduler] LEDGER SWEEP job every {_ledger_sweep_h}h "
              f"(limit {os.getenv('LEDGER_SWEEP_LIMIT', '8')}/run, oldest-checked-first)")
        # X velocity-trigger scan every 6h over the top-N topics. The volume
        # scan (counts/recent) is FREE vs the post cap; deep author-gradient
        # pulls are spent only on movers AND capped by the monthly post budget.
        if _X_AVAILABLE and os.getenv("X_BEARER_TOKEN"):
            def _scheduled_x_scan():
                try:
                    _x_velocity_scan(limit=int(os.getenv("X_SCAN_LIMIT", "100")))
                except Exception as _xe:
                    print(f"[scheduler] x-scan error: {_xe}")
            # Fixed clock times (00:00 / 06:00 / 12:00 / 18:00 UTC) instead of a
            # boot-relative interval, so the every-6h pull lands at predictable
            # times and the external monitor can run a deterministic 10 minutes
            # after each pull (00:10 / 06:10 / 12:10 / 18:10 UTC).
            _sched.add_job(_scheduled_x_scan, "cron", hour="0,6,12,18", minute=0,
                           id="x_velocity_scan", max_instances=1,
                           coalesce=True, misfire_grace_time=600)
        # Google realtime-trends discovery every 6h. One Apify actor run (~$0.57)
        # returns all ~125 countries; at 6h cadence that's ~$68/mo. Discovered
        # terms feed the scoring pipeline; the next collect+score cycle picks
        # them up. (Trend validation stays capped at ACCURACY_BATCH per day.)
        if os.getenv("APIFY_TOKEN") and os.getenv("GOOGLE_TRENDS_ENABLED", "1") == "1":
            def _scheduled_google_trends():
                # ONLY the paid Apify Google-Trends discovery here (kept on a
                # controlled clock cadence to bound cost). The YouTube collectors
                # (creators/broadcast/mainstream-news) moved to the main collect
                # cycle now that they're free (RSS) — so they fire reliably on
                # boot + every 6h instead of only at these clock slots.
                try:
                    c = get_db(DB_PATH)
                    try:
                        _gn = collect_google_trends(c) or 0
                        _log_health("google_trends", _gn, "success", conn=c)
                    except Exception as _gce:
                        _log_health("google_trends", 0, "failure", conn=c)
                        print(f"[scheduler] google-trends collect error: {_gce}")
                    c.close()
                except Exception as _gte:
                    print(f"[scheduler] google-trends error: {_gte}")
            # Fixed clock times (00:30/06:30/12:30/18:30 UTC), NOT a boot-relative
            # interval. An "interval, hours=6" job first fires 6h AFTER boot, so a
            # dyno restart (deploy or Heroku's ~daily cycle) before that resets the
            # timer and the job can stall for a day+ — exactly what stranded these
            # four collectors. Cron fires at the next clock slot regardless of
            # restarts; the 15-min grace catches a restart landing near a slot.
            _sched.add_job(_scheduled_google_trends, "cron", hour="0,6,12,18", minute=30,
                           id="google_trends_discovery", max_instances=1,
                           coalesce=True, misfire_grace_time=900)
        # Daily pull-history snapshot (both feeds) — permanent record from inception.
        # DATA RETENTION RULE: pull_history is NEVER pruned. It is the durable
        # daily archive of every topic's score from the day it was first detected.
        # Pruning it would permanently destroy the trend history the product is built on.
        def _scheduled_pull_history():
            try:
                archive_pull_history(DB_PATH)
            except Exception as _phe:
                print(f"[scheduler] pull-history error: {_phe}")
        _sched.add_job(_scheduled_pull_history, "cron", hour=2, minute=15,
                       id="pull_history_archive", max_instances=1, coalesce=True,
                       misfire_grace_time=3600)
        # Daily auto-theme extension — promote sustained BREAKOUT/STRONG
        # topics into the trend_beneficiary THEMES dict so the beneficiary
        # engine grows with trend discovery (instead of needing manual edits).
        def _scheduled_theme_extension():
            try:
                import theme_extension as _te
                result = _te.run_extension_cycle(DB_PATH)
                print(f"[scheduler] theme-extension: {result}")
            except Exception as _tee:
                print(f"[scheduler] theme-extension error: {_tee}")
        _sched.add_job(_scheduled_theme_extension, "cron", hour=3, minute=30,
                       id="theme_extension", max_instances=1, coalesce=True,
                       misfire_grace_time=3600)
        # Monthly research snapshot + retention prune (1st of month, 03:00 UTC).
        _sched.add_job(run_retention, "cron", day=1, hour=3, minute=0,
                       id="retention", max_instances=1, coalesce=True)
        # Daily signal-table retention (04:10 UTC) — keeps raw_signals/
        # topic_signals bounded so the 1GB Postgres plan can't fill up again
        # (they were unbounded; scoring only reads the last 72h).
        def _scheduled_signal_retention():
            try:
                _prune_signal_tables()
                # velocity_scores is the largest table on the 1GB plan: per-cycle
                # rows are wide (many TEXT cols). We now keep 365 days of per-cycle
                # scores (canonical, founder decision 2026-06-24) for backtesting/
                # calibration. ⚠ STORAGE: ~5.4GB at 90d → ~22GB at 365d, which EXCEEDS
                # the 10GB Essential-1 plan — a larger Postgres plan (or a
                # downsample-after-90d policy) is required before the tail fills in.
                # Weekly VACUUM FULL keeps the file true-sized; pull_history carries the
                # durable 12-month record.
                prune_velocity_scores(
                    DB_PATH, days=int(os.getenv("VELOCITY_KEEP_DAYS", "365")))
            except Exception as _sre:
                print(f"[scheduler] signal retention error: {_sre}")
        _sched.add_job(_scheduled_signal_retention, "cron", hour=4, minute=10,
                       id="signal_retention", max_instances=1, coalesce=True,
                       misfire_grace_time=3600)
        # Weekly VACUUM FULL (Sun 04:30 UTC) — DELETE marks rows dead but doesn't
        # return space to the OS; only VACUUM FULL shrinks the file Heroku meters.
        # Without this the file creeps up to the cap even with daily deletes (it
        # hit 101% overnight). Briefly locks each table; Sunday-night quiet window.
        def _scheduled_vacuum():
            if not os.getenv("DATABASE_URL"):
                return
            try:
                import psycopg2
                vconn = psycopg2.connect(os.getenv("DATABASE_URL"))
                vconn.autocommit = True
                vcur = vconn.cursor()
                for table in ("velocity_scores", "topic_signals", "raw_signals",
                              "anomaly_log", "topic_queries"):
                    try:
                        vcur.execute(f"VACUUM FULL {table}")
                    except Exception as _ve:
                        print(f"[vacuum] {table}: {_ve}")
                vconn.close()
                print("[scheduler] weekly VACUUM FULL complete.")
            except Exception as _vce:
                print(f"[scheduler] vacuum error: {_vce}")
        _sched.add_job(_scheduled_vacuum, "cron", day_of_week="sun", hour=4,
                       minute=30, id="weekly_vacuum", max_instances=1,
                       coalesce=True, misfire_grace_time=3600)
        _sched.start()
        _SCHEDULER_STARTED = True
        print("[scheduler] APScheduler started — collect+score every 30 min.")
        return _sched
    except Exception as _sched_exc:
        print(f"[scheduler] start error (non-fatal): {_sched_exc}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# PREWARM AGENT — dedicated, READ-ONLY, single-purpose.
# Keeps the full /scores + /topics superset caches hot in THIS request-serving
# process so the first page every platform (mobile, web, desktop) loads is instant
# — never the ~20s cold compute that was timing the mobile app out. It only READS
# the DB to recompute the cache; it never writes to or mutates the database (no
# scores changed, no rows touched), so it cannot affect any served data.
# ─────────────────────────────────────────────────────────────────────────────
_PREWARM_STATUS: dict = {"last_run": None, "warmed": [], "elapsed_s": None}

def _prewarm_caches() -> dict:
    """Recompute + cache the default /scores and /topics supersets (read-only)."""
    import time as _t
    warmed = []
    t0 = _t.time()
    try:
        full = _compute_scores_full("overall", "all", 0.0)
        _cache.set("scores_full:overall:all:0.0", full, CACHE_TTL_SCORES_FULL)
        warmed.append({"feed": "scores", "rows": len(full)})
    except Exception as e:
        warmed.append({"feed": "scores", "error": str(e)})
    try:
        grid = _compute_topics_full("", False)
        _cache.set("topics_full::0", grid, CACHE_TTL_SCORES_FULL)
        warmed.append({"feed": "topics", "rows": len(grid)})
    except Exception as e:
        warmed.append({"feed": "topics", "error": str(e)})
    # History view (web + mobile): warm every user-facing window at the default
    # points=12 so the heavy trajectory build never blocks a load. Shorter windows
    # are cheaper; all stay hot because prewarm re-runs inside the cache TTL.
    for _win in ("7d", "24h", "12h"):
        try:
            hist = _compute_history_full(_win, 12)
            _cache.set(f"history_full:{_win}:12", hist, CACHE_TTL_SCORES_FULL)
            warmed.append({"feed": f"history:{_win}", "rows": len(hist)})
        except Exception as e:
            warmed.append({"feed": f"history:{_win}", "error": str(e)})
    # Market Signal (/risk/scores): warm the full instrument universe so the Market
    # tab paints instantly too — full parity with scores/topics/history.
    try:
        rf = _compute_risk_full()
        _cache.set("risk_full", rf, CACHE_TTL_SCORES_FULL)
        warmed.append({"feed": "risk", "rows": len(rf.get("results") or [])})
    except Exception as e:
        warmed.append({"feed": "risk", "error": str(e)})
    # Crypto Money Gradient (/crypto): warm the coin roster so the page paints instantly. The live
    # compute does FMP price + Finviz/AV-throttled proxy Dark Matter across the roster — far too slow
    # per-request, so it MUST be served from this prewarmed cache (parity with scores/topics/risk).
    if _CRYPTO_AVAILABLE and crypto_engine.CRYPTO_SIGNAL:
        try:
            cf = crypto_engine.serve_crypto(record=False, db_path=DB_PATH)
            _cache.set("crypto_full", cf, CACHE_TTL_SCORES_FULL)
            warmed.append({"feed": "crypto", "rows": len(cf.get("coins") or [])})
        except Exception as e:
            warmed.append({"feed": "crypto", "error": str(e)})
    dt = round(_t.time() - t0, 2)
    _PREWARM_STATUS.update({"last_run": datetime.now(timezone.utc).isoformat(),
                            "warmed": warmed, "elapsed_s": dt})
    print(f"[prewarm-agent] warmed {warmed} in {dt}s (every {PREWARM_INTERVAL_MIN}m)")
    return {"agent": "prewarm", "read_only": True, "interval_min": PREWARM_INTERVAL_MIN,
            "ttl_s": CACHE_TTL_SCORES_FULL, **_PREWARM_STATUS}

def _prewarm_loop():
    import time as _t
    while True:
        try:
            _prewarm_caches()
        except Exception as _e:
            print(f"[prewarm-agent] loop error: {_e}")
        _t.sleep(max(60, PREWARM_INTERVAL_MIN * 60))


@app.get("/prewarm")
def prewarm_now():
    """Kick a fresh warm in the BACKGROUND (non-blocking) + return the most recent
    agent status. Warming all supersets (scores + topics + history×3) synchronously
    exceeds Heroku's 30s router limit, so the manual endpoint must not block on it;
    the background loop warms on its own schedule regardless. Read-only."""
    _threading.Thread(target=_prewarm_caches, daemon=True, name="prewarm-manual").start()
    return {"agent": "prewarm", "read_only": True, "kicked": True,
            "interval_min": PREWARM_INTERVAL_MIN, "ttl_s": CACHE_TTL_SCORES_FULL,
            **_PREWARM_STATUS}


@app.on_event("startup")
async def startup_auto_collect():
    """Auto-collect on first launch if the database is empty."""
    import threading

    # Prewarm Agent: warm the superset caches now (background, non-blocking) and
    # then on a fixed interval, in THIS request-serving process.
    if os.getenv("PREWARM_ENABLED", "1").lower() in ("1", "true", "yes"):
        try:
            threading.Thread(target=_prewarm_loop, daemon=True, name="prewarm-agent").start()
            print(f"[startup] prewarm-agent started (every {PREWARM_INTERVAL_MIN}m).")
        except Exception as _pwe:
            print(f"[startup] prewarm-agent failed to start: {_pwe}")

    # Category enrichment: build the topic_key→category override maps (situation
    # EVENT-context + own-HEADLINE context), then refresh on an interval. Both drain the
    # news/general catch-all by context — display-only, never feed the score.
    if SITUATION_CATEGORY_ENABLED or CONTEXT_CATEGORY_ENABLED:
        try:
            threading.Thread(target=_situation_category_loop, daemon=True,
                             name="category-enrich").start()
            print(f"[startup] category-enrich router started (situation={SITUATION_CATEGORY_ENABLED}, "
                  f"context={CONTEXT_CATEGORY_ENABLED}, every {SITUATION_CAT_REFRESH_MIN}m).")
        except Exception as _sce:
            print(f"[startup] category-enrich router failed to start: {_sce}")

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

    # Create auxiliary tables ONCE at startup (not per request) so the explainer
    # endpoint never runs DDL under a concurrent feed load.
    try:
        _c = get_db(DB_PATH)
        # NOTE: column is `full_text`, NOT `full` — `full` is a PostgreSQL
        # reserved word (FULL OUTER JOIN) and breaks unquoted DDL/DML.
        _c.execute("""CREATE TABLE IF NOT EXISTS topic_explainers (
            topic_key TEXT PRIMARY KEY, topic_display TEXT,
            short TEXT, full_text TEXT, created_at TEXT)""")
        # Defensive migration: if an older table exists, ensure the column is
        # present (idempotent — harmless if it already exists).
        try:
            _c.execute("ALTER TABLE topic_explainers ADD COLUMN full_text TEXT")
            _c.commit()
        except Exception:
            # PG raises DuplicateColumn when the column already exists, which ABORTS the
            # transaction — every later statement then fails with "current transaction is
            # aborted" and the whole aux block (incl. the ledger inits) is skipped. Roll
            # back to clear the aborted txn so the rest of the block runs. (SQLite no-op.)
            try:
                _c.rollback()
            except Exception:
                pass
        _c.execute("CREATE TABLE IF NOT EXISTS x_post_usage (month TEXT PRIMARY KEY, posts INTEGER)")
        _c.execute("""CREATE TABLE IF NOT EXISTS ai_grade_costs (
            id TEXT PRIMARY KEY, topic TEXT,
            perplexity_cost REAL, anthropic_cost REAL, total_cost REAL, created_at TEXT)""")
        _c.commit()
        _c.close()
        print("[startup] auxiliary tables ensured (explainers, x_post_usage, ai_grade_costs).")
        if _HEALTH_AVAILABLE:
            try:
                _health.init_health_db(DB_PATH)
                print("[startup] collector_health table ensured.")
            except Exception as _he:
                print(f"[startup] collector_health init error: {_he}")
        # Ensure the auto-theme tables exist at startup (not only when the daily
        # extension job first runs) — otherwise load_all_themes errors noisily on
        # every beneficiary scoring with "relation themes_extension does not exist".
        try:
            import theme_extension as _te
            _te.init_theme_db(DB_PATH)
            print("[startup] themes_extension tables ensured.")
        except Exception as _tee:
            print(f"[startup] theme_extension init error: {_tee}")
        try:
            import market_signal_engine as _mse
            _mse.init_market_signal_db(DB_PATH)
            print("[startup] market_signal_history table ensured.")
        except Exception as _msee:
            print(f"[startup] market_signal init error: {_msee}")
        if _LEDGER_PLUS_AVAILABLE:
            try:
                ledger_plus.init_pending_db(DB_PATH)
                print("[startup] accuracy ledger (pending + ledger) tables ensured.")
            except Exception as _le:
                print(f"[startup] ledger init error: {_le}")
        if _MARKET_LEDGER_AVAILABLE:
            try:
                market_ledger.init_market_ledger_db(DB_PATH)
                print("[startup] market accuracy ledger (Money Gradient, EOD-price validated) tables ensured.")
            except Exception as _mli:
                print(f"[startup] market ledger init error: {_mli}")
    except Exception as _aux_exc:
        print(f"[startup] aux table init error (non-fatal): {_aux_exc}")

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

    # ── Continuous collection scheduler ───────────────────────────────
    # By default the scheduler runs on a SEPARATE worker dyno (Procfile
    # `worker:` → --mode=worker) so background collection/scoring/scans never
    # contend with web request serving. Set RUN_SCHEDULER_IN_WEB=1 to run it
    # in-process on the web dyno (single-dyno / dev setups).
    if os.getenv("RUN_SCHEDULER_IN_WEB", "").lower() in ("1", "true", "yes"):
        start_scheduler()
    else:
        print("[startup] Scheduler NOT started on web dyno (handled by worker). "
              "Set RUN_SCHEDULER_IN_WEB=1 to run it here.")


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

    # NOTE: every non-grouped column must be aggregated — Postgres (production)
    # rejects bare columns under GROUP BY that SQLite silently tolerates; the
    # bare topic_display/signal_stage here were 500-ing the endpoint.
    rows = conn.execute("""
        SELECT
            v.topic_key,
            MAX(v.topic_display)    AS topic_display,
            MIN(v.scored_at)        AS detected_at,
            MAX(v.overall_score)    AS overall_score,
            MAX(v.detection_score)  AS detection_score,
            MAX(v.confidence_score) AS confidence_score,
            MAX(v.signal_stage)     AS stage,
            NULL                    AS lead_time_est_days,
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


@app.post("/collect", dependencies=[Depends(_require_internal)])
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
            # Social/open-network collectors (keyless) — Reddit's replacement
            # as the niche early-chatter tier + GDELT mainstream corroboration.
            for _sfn in (collect_bluesky, collect_lemmy, collect_mastodon,
                         collect_gdelt_trends):
                try:
                    _sfn(conn)
                except Exception as _se:
                    print(f"[collect] {_sfn.__name__} error: {_se}")
            conn.close()
            print(f"[collect] Core: reddit={r} github={g} hn={h}")

            if include_blogs and _BLOGS_AVAILABLE:
                try:
                    _bc.collect_all_blogs()
                except Exception as exc:
                    print(f"[collect] Blog error: {exc}")

            if _DISCOVERY_AVAILABLE:
                try:
                    conn2 = get_db(DB_PATH)
                    _dc.collect_all_discovery(conn2)
                    conn2.close()
                except Exception as exc:
                    print(f"[collect] Discovery error: {exc}")

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


@app.post("/collect/blogs", dependencies=[Depends(_require_internal)])
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


@app.post("/collect/discovery", dependencies=[Depends(_require_internal)])
def run_discovery_collection(geos: str = Query("US", description="Comma-separated geos, e.g. US,GB")):
    """
    Run ONLY the open-world discovery collectors (Google Trends trending-searches
    + Wikipedia top pageviews). Category-agnostic intake that surfaces
    general-culture trends (sports, entertainment, politics) the seeded tech
    feeds miss. Run POST /score-all afterwards to recompute scores.
    """
    if not _DISCOVERY_AVAILABLE:
        raise HTTPException(503, "discovery_collectors.py not found in project directory")
    geo_list = tuple(g.strip() for g in geos.split(",") if g.strip()) or ("US",)
    try:
        conn = get_db(DB_PATH)
        results = _dc.collect_all_discovery(conn, geos=geo_list)
        conn.close()
        return {
            "status":        "collected",
            "total_signals": results.pop("_total", 0),
            "breakdown":     results,
            "geos":          list(geo_list),
            "message":       "Run POST /score-all to compute velocity scores.",
        }
    except Exception as exc:
        raise HTTPException(500, f"Discovery collection error: {exc}")


@app.post("/score-all", dependencies=[Depends(_require_internal)])
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


@app.post("/precompute", dependencies=[Depends(_require_internal)])
def precompute_payloads(top_n: int = 600):
    """Regenerate velocity_scores.serve_payload (GOTCHA G1) WITHOUT a full re-score — so the
    strengthened serve-time quality gate + latest calibration are baked into every cached
    list immediately rather than waiting for the next 6h cycle. Non-blocking: kicks the
    rebuild on a background thread (clears all payloads, rebuilds the top-N; ~30-60s) and
    returns at once. No score is changed — only the precomputed serve blob is refreshed."""
    import threading

    def _job():
        try:
            n = _precompute_serve_payloads(int(top_n))
            try:
                _cache.invalidate()
            except Exception:
                pass
            print(f"[precompute] serve_payload rebuilt: {n} rows")
        except Exception as exc:
            print(f"[precompute] error: {exc}")

    threading.Thread(target=_job, daemon=True).start()
    return {"status": "started", "top_n": top_n,
            "note": "serve_payload rebuild running in background (~30-60s); no score changed"}


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


RISK_FULL_CAP = int(os.getenv("RISK_FULL_CAP", "300"))

def _compute_risk_full() -> dict:
    """Full Market-Signal universe computed at the cap (limit-INDEPENDENT) so the
    endpoint can cache it once + serve O(1) slices. Read-only: get_risk_scores reads
    risk_signals/serve payloads, writes nothing."""
    if not _RISK_AVAILABLE:
        return {"count": 0, "results": []}
    return risk.get_risk_scores(DB_PATH, RISK_FULL_CAP)

@app.get("/risk/scores")
def risk_scores(limit: int = Query(50, ge=1, le=300), offset: int = Query(0, ge=0)):
    """Risk Gradient Scores — emerging financial risks scored by diffusion stage;
    the Market Signal data source. Superset-cached and kept hot by the Prewarm
    Agent, then sliced to (offset, limit) so the web can page 100 at a time instead
    of pulling the whole rich payload at once. Read-only; same shape + ordering."""
    full = _cache.get("risk_full")
    if full is None:
        full = _compute_risk_full()
        _cache.set("risk_full", full, CACHE_TTL_SCORES_FULL)
    all_results = full.get("results") or []
    page = all_results[offset: offset + limit]
    return {"count": len(page), "total": len(all_results),
            "offset": offset, "limit": limit, "results": page}


@app.get("/macro/leverage")
def macro_leverage():
    """OFR Short-Term Funding Monitor — systemic leverage + funding-stress read
    from repo-market data (transaction volume + rates). Macro risk overlay."""
    if not _OFR_AVAILABLE:
        return {"available": False}
    try:
        return {"available": True, **ofr_stfm.leverage_snapshot()}
    except Exception as e:
        return {"available": False, "error": str(e)}


@app.get("/beneficiary/{ticker}")
def beneficiary_lookup(ticker: str):
    """Trend Beneficiary score — measures whether the COMPANY's business is
    positioned to benefit from a Now TrendIn detected trend, and whether the
    cycle is EARLY (window open) or LATE/REALIZED (move already done). The
    SanDisk-pattern engine. Measurement, NOT investment advice."""
    try:
        import trend_beneficiary_wire as _tbw
        out = _tbw.score_company_beneficiary(ticker.upper(), ticker.upper())
        return out or {"available": False, "ticker": ticker.upper(),
                       "reason": "no theme exposure detected for this company"}
    except Exception as e:
        return {"available": False, "error": str(e)}


@app.get("/convergence/{topic_key}")
def signal_convergence(topic_key: str):
    """Signal Convergence — downstream directional validation. Reads the Gradient
    Score's recent trajectory + raw volume + niche concentration and reports
    whether the score's direction is CONFIRMED / MIXED / CONFLICTING by the
    underlying data. Read-only; never feeds the score; independent of N demand."""
    try:
        import now_trending_direction as _ntd
        return _ntd.compute_convergence(topic_key, DB_PATH)
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/themes")
def list_themes():
    """List all THEMES the trend_beneficiary engine knows about — hand-curated
    + auto-promoted. Auto-promoted themes are flagged."""
    try:
        import theme_extension as _te
        themes = _te.load_all_themes(DB_PATH)
        return {"count": len(themes),
                "hand_curated": [k for k, v in themes.items() if not v.get("auto_promoted")],
                "auto_promoted": [k for k, v in themes.items() if v.get("auto_promoted")],
                "themes": themes}
    except Exception as e:
        return {"error": str(e), "themes": {}}


@app.post("/themes/extend", dependencies=[Depends(_require_internal)])
def themes_extend():
    """Manually trigger the auto-theme extension cycle (founder-only).
    Normally runs daily at 03:30 UTC via the scheduler."""
    try:
        import theme_extension as _te
        return _te.run_extension_cycle(DB_PATH)
    except Exception as e:
        return {"error": str(e)}


@app.get("/beneficiary/backtest/{theme_key}")
def beneficiary_backtest(theme_key: str, lookback_days: int = 365,
                         tickers: str = ""):
    """Backtest the Trend Beneficiary engine against historical pull_history.
    For each ticker the caller supplies (comma-separated), replays the
    beneficiary score against the theme's attention trajectory and reports
    when (if ever) the company would have been flagged EARLY vs LATE.

    THIS IS THE HONEST VALIDATION — without it, every weight is a guess."""
    try:
        import trend_beneficiary_wire as _tbw
        import trend_beneficiary as _tb
        if theme_key not in _tb.THEMES:
            try:
                import theme_extension as _te
                merged = _te.load_all_themes(DB_PATH)
                if theme_key not in merged:
                    return {"error": f"unknown theme: {theme_key}",
                            "known_themes": list(_tb.THEMES.keys())}
            except Exception:
                return {"error": f"unknown theme: {theme_key}"}

        ticker_list = [t.strip().upper() for t in (tickers or "").split(",") if t.strip()]
        if not ticker_list:
            return {"error": "supply at least one ticker via ?tickers=AAPL,NVDA"}

        conn = get_db(DB_PATH)
        cutoff = (datetime.now(timezone.utc) -
                  timedelta(days=lookback_days)).isoformat()
        # Build the theme's attention trajectory over time
        attention_curve = []
        try:
            kws = _tb.THEMES.get(theme_key, {}).get("keywords", [])
            for kw in kws[:5]:
                kkey = kw.lower().strip().replace(" ", "_")
                rows = conn.execute(
                    "SELECT scored_at, detection_score, signal_stage FROM pull_history "
                    "WHERE topic_key = ? AND scored_at > ? "
                    "ORDER BY scored_at",
                    (kkey, cutoff)
                ).fetchall()
                for r in rows:
                    rd = dict(r) if hasattr(r, "keys") else {
                        "scored_at": r[0], "detection_score": r[1], "signal_stage": r[2]
                    }
                    # Normalize to "stage"; pull_history stores it as signal_stage.
                    attention_curve.append({
                        "scored_at": rd.get("scored_at"),
                        "detection_score": rd.get("detection_score"),
                        "stage": rd.get("signal_stage") or "",
                    })
        except Exception as e:
            print(f"[backtest] attention curve error: {e}")
        conn.close()

        # Score each ticker NOW (live), and report what the cycle stage would
        # have implied at each point in the attention curve. Simplified — a
        # full backtest needs historical financial snapshots which Finnhub
        # gives via /stock/financials-reported across quarters.
        results = []
        for tkr in ticker_list:
            live = _tbw.score_company_beneficiary(tkr, tkr)
            if not live:
                results.append({"ticker": tkr, "skipped": "no theme match"})
                continue
            # First-EARLY: earliest scored_at where stage was BREAKOUT/STRONG
            earliest_breakout = None
            for pt in attention_curve:
                if pt["stage"] in ("BREAKOUT", "STRONG"):
                    earliest_breakout = pt["scored_at"]
                    break
            results.append({
                "ticker": tkr,
                "live_exposure": live.get("exposure_score"),
                "live_cycle_stage": live.get("cycle_stage"),
                "would_have_flagged_early_at": earliest_breakout,
                "live_attention_score": live.get("live_inputs", {}).get("theme_attention_score"),
                "theme_attention_history_points": len(attention_curve),
            })
        return {"theme_key": theme_key, "lookback_days": lookback_days,
                "attention_curve_size": len(attention_curve),
                "results": results,
                "caveat": "Live exposure score uses today's Finnhub data. "
                          "Full historical backtest requires period-matched "
                          "financial snapshots — this version shows whether "
                          "the company would currently match the theme and "
                          "when the attention signal first peaked."}
    except Exception as e:
        return {"error": str(e)}


@app.get("/broadcast/topics")
def broadcast_topics(hours: int = 24, min_sources: int = 3, limit: int = 25):
    """Common topics being covered RIGHT NOW across the 22 broadcast channels
    (CNBC, BBC, Bloomberg, Reuters, etc.). Surfaces what mainstream news is
    aligned on — useful as a confirmation/divergence signal vs niche topics."""
    try:
        conn = get_db(DB_PATH)
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        rows = conn.execute(
            # topic_signals has no author column — source_name carries the
            # broadcast channel; Postgres (unlike SQLite) hard-errors on the
            # missing column, which 500'd this endpoint.
            "SELECT topic, topic_key, COUNT(DISTINCT source_name) AS sources, "
            "COUNT(*) AS mentions, MAX(extracted_at) AS last_seen "
            "FROM topic_signals "
            "WHERE platform = 'broadcast' AND extracted_at > ? "
            "GROUP BY topic, topic_key "
            "HAVING COUNT(DISTINCT source_name) >= ? "
            "ORDER BY sources DESC, mentions DESC LIMIT ?",
            (cutoff, min_sources, limit)
        ).fetchall()
        conn.close()
        topics = []
        for r in rows:
            d = dict(r) if hasattr(r, "keys") else {
                "topic": r[0], "topic_key": r[1], "sources": r[2],
                "mentions": r[3], "last_seen": r[4]
            }
            topics.append(d)
        return {"hours": hours, "min_sources": min_sources,
                "channel_pool": 22, "topics": topics,
                "note": "Topics covered by >= N distinct broadcast channels "
                        "in the lookback window — mainstream-consensus signal."}
    except Exception as e:
        return {"error": str(e), "topics": []}


@app.post("/market/backfill", dependencies=[Depends(_require_internal)])
def market_backfill():
    """Founder-only: seed the Market Signal per-component baselines from FINRA
    short-interest history so the baseline-relative scores aren't CALIBRATING for
    days. Runs synchronously over the watchlist (small)."""
    if not _RISK_AVAILABLE:
        return {"status": "unavailable"}
    try:
        import market_signal_engine as _mse
        wl = getattr(risk, "WATCHLIST_TICKERS", {}) or {}
        items = [(risk._risk_key(disp) if hasattr(risk, "_risk_key") else disp, tkr)
                 for disp, tkr in wl.items()]
        finra = _mse.backfill_from_finra(items, DB_PATH)
        finnhub = _mse.backfill_from_finnhub(items, DB_PATH)
        return {"status": "ok", "finra": finra, "finnhub": finnhub}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/risk/collect", dependencies=[Depends(_require_internal)])
def risk_collect():
    """Run the risk collectors (SEC/GDELT/Reddit/FRED/YouTube) + score, in the background."""
    if not _RISK_AVAILABLE:
        return {"status": "unavailable"}

    def _job():
        try:
            _rres = risk.run_risk_collection(DB_PATH) or {}
            risk.score_all_risks(DB_PATH)
            _cache.invalidate()
            # Log health here too — this manual path (the app's Pull Market
            # Trends button) previously never logged, so even successful manual
            # collections left the risk collector looking DOWN.
            _rn = sum(v for v in _rres.values() if isinstance(v, (int, float)))
            if _HEALTH_AVAILABLE:
                _log_health("risk", int(_rn), "success")
            print("[risk] manual collect+score complete.")
        except Exception as exc:
            if _HEALTH_AVAILABLE:
                _log_health("risk", 0, "failure")
            print(f"[risk] collect error: {exc}")

    import threading
    threading.Thread(target=_job, daemon=True).start()
    return {"status": "started", "message": "Risk collection running. Poll GET /risk/scores."}


@app.get("/risk/{risk_topic}")
def risk_detail(risk_topic: str):
    if not _RISK_AVAILABLE:
        raise HTTPException(404, "Risk module unavailable")
    d = risk.get_risk_detail(risk_topic, DB_PATH)
    if not d:
        raise HTTPException(404, f"No risk score for {risk_topic}")
    return d


@app.get("/accuracy/ledger")
def accuracy_ledger_report():
    """The Accuracy Ledger — documented lead time vs Google Trends breakout.
    Prefers the HONEST report (counts fizzles/false-positives in the
    denominator); falls back to the base report, then empty-with-pending."""
    if _LEDGER_PLUS_AVAILABLE:
        try:
            h = ledger_plus.generate_honest_report(DB_PATH)
            if h.get("status") == "ok":
                return {
                    "status": "ok",
                    "hitRate": h["honest_hit_rate_pct"],
                    "naiveHitRate": h["naive_hit_rate_pct"],
                    "avgLead": h["mean_lead_days"],
                    "medianLead": h["median_lead_days"],
                    "maxLead": h["max_lead_days"],
                    "total": h["sample_size"],
                    "led": h["hits_led"],
                    "sameDay": h["same_day"],
                    "lagged": h["misses_lagged"],
                    "falsePositives": h["misses_false_positive"],
                    "pending": h["still_pending"],
                    "smallSample": h["small_sample_warning"],
                    "best": [{"topic": b["topic"], "leadDays": b["lead_days"]}
                             for b in h.get("best", [])],
                    # Maturity-segmented — early detection of EMERGING topics is the claim;
                    # established topics can only resolve LAGGED (coverage latency, not the thesis).
                    "byMaturity": h.get("by_maturity"),
                    "earlyDetectionHitRate": h.get("early_detection_hit_rate_pct"),
                    "earlyDetectionSample": h.get("early_detection_sample"),
                    "maturityCoverage": h.get("maturity_coverage"),
                }
            # No resolved rows yet — surface the pending count so the empty
            # state can honestly say "N calls in flight".
            return {"status": "empty", "pending": h.get("pending", 0)}
        except Exception as _hre:
            print(f"[accuracy] honest report error: {_hre}")
    if _ACCURACY_AVAILABLE:
        return accuracy.generate_accuracy_report(DB_PATH)
    return {"status": "unavailable"}


# Phase A — situation model preview. HELD-OUT + READ-ONLY: assembles co-occurring topic
# fragments into candidate SITUATIONS from the live topic_signals corpus, writes NOTHING
# and touches no score. Lets us review whether the situation layer forms clean clusters on
# real data before any of it influences scoring/serving (SITUATION_MODEL.md, Phase A).
_SITUATIONS_CACHE = {"key": None, "at": 0.0, "data": None}


def _situations_cached(window_hours: int, min_doc_freq: int, min_jaccard: float):
    """Build (or return cached, ~10 min) the held-out situation set on the REAL corpus.
    Read-only. Passes the engine's shared quality gate AND category classifier so the
    situation layer agrees with the rest of the engine on what's a topic + its category."""
    import time as _t
    import situation_clustering
    ck = (window_hours, min_doc_freq, round(min_jaccard, 3))
    if _SITUATIONS_CACHE["data"] and _SITUATIONS_CACHE["key"] == ck \
            and (_t.time() - _SITUATIONS_CACHE["at"]) < 600:
        return _SITUATIONS_CACHE["data"], situation_clustering
    conn = get_db(DB_PATH)
    try:
        res = situation_clustering.build_from_db(
            conn, window_hours=window_hours, min_doc_freq=min_doc_freq,
            min_jaccard=min_jaccard, gate=_is_quality_topic, categorizer=_topic_category)
    finally:
        conn.close()
    _SITUATIONS_CACHE.update(key=ck, at=_t.time(), data=res)
    return res, situation_clustering


def _situation_public(s: dict) -> dict:
    return {
        "situation_key": s["situation_key"],
        "label": s.get("label_display") or s["label"],
        "anchor": s["anchor"],
        "category": s.get("category", "general"),        # Phase B — per-situation category
        "category_votes": s.get("category_votes"),
        "size": s["size"],
        "shared_anchors": s["shared_anchors"],
        "core_members": s["core_members"][:12],
        "first_seen": s.get("first_seen"),
    }


@app.get("/situations/preview", dependencies=[Depends(_require_internal)])
def situations_preview(window_hours: int = 120, min_doc_freq: int = 5,
                       min_jaccard: float = 0.18, limit: int = 60, category: str = None):
    """Held-out preview of the situation layer (topics-not-words) on the REAL corpus,
    now category-tagged (Phase B). Read-only: no score is read or written."""
    try:
        res, _ = _situations_cached(window_hours, min_doc_freq, min_jaccard)
    except Exception as e:
        return {"status": "unavailable", "error": str(e)}
    rows = res["situations"]
    if category:                                          # optional category filter
        rows = [s for s in rows if s.get("category") == category]
    sits = [_situation_public(s) for s in rows[:int(limit)]]
    return {"status": "ok", "held_out": True, "note": "read-only preview — affects no score",
            "window_hours": res["window_hours"], "documents": res["documents"],
            "candidates": res.get("candidates"), "topics_kept": res["topics_kept"],
            "dropped_quality": res.get("dropped_quality"),
            "situation_count": res["situation_count"], "situations": sits}


@app.get("/situations/search", dependencies=[Depends(_require_internal)])
def situations_search(q: str, window_hours: int = 120, min_doc_freq: int = 5,
                      min_jaccard: float = 0.18, limit: int = 25):
    """Entity/fragment DISAMBIGUATION (Phase B): the distinct situations a user could mean
    by `q` — e.g. q=japan → the Belgium-visit / BOJ-rate-hike / World-Cup situations, each
    with its own category + score-eligible context. Held-out, read-only."""
    if not (q or "").strip():
        raise HTTPException(400, "q is required")
    try:
        res, sc = _situations_cached(window_hours, min_doc_freq, min_jaccard)
    except Exception as e:
        return {"status": "unavailable", "error": str(e)}
    hits = sc.search_situations(res["situations"], q, limit=limit)
    return {"status": "ok", "held_out": True, "query": q,
            "situation_count": len(hits),
            "situations": [_situation_public(s) for s in hits]}


@app.get("/audit/topics", dependencies=[Depends(_require_internal)])
def audit_topics(days: int = 7, max_topics: int = 9000):
    """READ-ONLY audit of the current scored-topic universe (latest score per topic within
    `days`). Writes NOTHING, deletes NOTHING (respects the 365-day retention rule). Reports:
    quality (junk vs real via the shared gate), category distribution + catch-all %, and
    duplicate-spelling groups — so a human can decide the compliant cleanups (serve-filter is
    already live; this surfaces what to consolidate / what lexicon terms to add)."""
    from datetime import datetime, timezone, timedelta
    from collections import Counter, defaultdict
    cutoff = (datetime.now(timezone.utc) - timedelta(days=int(days))).isoformat()
    conn = get_db(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT v.topic_key AS topic_key, v.topic_display AS topic_display "
            "FROM velocity_scores v INNER JOIN ("
            "  SELECT topic_key, MAX(scored_at) m FROM velocity_scores "
            "  WHERE scored_at >= ? GROUP BY topic_key) l "
            "ON v.topic_key=l.topic_key AND v.scored_at=l.m LIMIT ?",
            (cutoff, int(max_topics))).fetchall()
    finally:
        conn.close()

    def _v(r, k, i):
        return (r[k] if hasattr(r, "keys") else r[i])

    total = len(rows)
    real = 0
    junk, cats, cats_routed, groups = [], Counter(), Counter(), defaultdict(set)
    routed_moved = 0
    for r in rows:
        tk = _v(r, "topic_key", 0)
        disp = _v(r, "topic_display", 1) or (tk or "").replace("_", " ")
        if _is_quality_topic(disp):
            real += 1
        elif len(junk) < 40:
            junk.append(disp)
        raw_cat = _topic_category(disp) or "general"
        routed_cat = _category_for(tk, disp) or "general"
        cats[raw_cat] += 1
        cats_routed[routed_cat] += 1
        if routed_cat != raw_cat:                     # situation layer reclassified this topic
            routed_moved += 1
        groups[_topic_key(disp)].add(disp)            # same canonical key, different spellings
    dup = {k: sorted(v) for k, v in groups.items() if len(v) > 1}
    _catchall_of = lambda c: c.get("news", 0) + c.get("general", 0) + c.get("", 0)
    catchall = _catchall_of(cats)
    catchall_routed = _catchall_of(cats_routed)
    pct = lambda n: (round(100 * n / total, 1) if total else 0.0)
    return {
        "status": "ok", "held_out": True, "read_only": True,
        "note": "audit only — no rows written or deleted (365-day retention rule respected)",
        "window_days": days, "total_topics_scored": total,
        "quality": {"real": real, "junk": total - real, "junk_pct": pct(total - real),
                    "junk_examples": junk},
        "category": {"distribution": dict(cats.most_common()),
                     "catchall_pct": pct(catchall),
                     "note": "catch-all = news/general; high % => lexicon gaps to enrich"},
        # Situation→category routing effect (display-only): how much the held-out
        # situation layer drains the catch-all by context-routing bare entities.
        "category_routed": {
            "distribution": dict(cats_routed.most_common()),
            "catchall_pct": pct(catchall_routed),
            "catchall_drained_pts": round(pct(catchall) - pct(catchall_routed), 1),
            "topics_reclassified": routed_moved,
            "situation_overrides_loaded": len(_SITUATION_CAT),
            "context_overrides_loaded": len(_CONTEXT_CAT),
            "enabled": {"situation": SITUATION_CATEGORY_ENABLED, "context": CONTEXT_CATEGORY_ENABLED},
            "note": "routed = served category after situation(event) + context(headline) "
                    "routing; display-only, no scoring impact",
        },
        "duplicates": {"groups": len(dup),
                       "examples": dict(sorted(dup.items(), key=lambda kv: -len(kv[1]))[:15])},
    }


@app.get("/accuracy/ledger/detail")
def accuracy_ledger_detail(limit: int = Query(300, ge=1, le=1000),
                           verdict: str = Query("", description="LED|SAME_DAY|LAGGED|FALSE_POSITIVE")):
    """
    Per-detection rows of the Accuracy Ledger — the institutional auditable
    track record (topic, detection date+score, breakout date, lead time,
    verdict, provider). Powers the flagship Ledger table in the terminal.
    """
    try:
        conn = get_db(DB_PATH)
        where = ""
        params = []
        if verdict.strip():
            where = "WHERE verdict = ?"
            params.append(verdict.strip().upper())
        params.append(limit)
        rows = [dict(r) for r in conn.execute(f"""
            SELECT topic_key, topic_display, detection_date, detection_score,
                   breakout_date, breakout_multiple, lead_time_days, verdict,
                   validated_at, provider
            FROM accuracy_ledger {where}
            ORDER BY validated_at DESC
            LIMIT ?
        """, params).fetchall()]
        conn.close()
        return {"status": "ok", "count": len(rows), "rows": rows}
    except Exception as e:
        return {"status": "empty", "count": 0, "rows": [], "note": str(e)[:140]}


@app.post("/accuracy/validate", dependencies=[Depends(_require_internal)])
def accuracy_validate(sync: int = 0):
    """Run a validation pass (checks top detections against Google Trends)."""
    if not _ACCURACY_AVAILABLE:
        return {"status": "unavailable"}

    if sync:
        return accuracy.validate_recent_detections(DB_PATH)

    def _job():
        try:
            accuracy.validate_recent_detections(DB_PATH)
        except Exception as exc:
            print(f"[accuracy] validate error: {exc}")

    import threading
    threading.Thread(target=_job, daemon=True).start()
    return {"status": "started", "provider": accuracy.TRENDS_PROVIDER}


@app.get("/market/accuracy")
def market_accuracy_report():
    """The MARKET-SIGNAL Accuracy Ledger (the Money Gradient's track record) — DISTINCT
    from /accuracy/ledger (attention/Google-Trends). Ground truth = realized EOD close
    direction (FMP): did the market move the way the detected money flow indicated, and how
    many days after. MEASUREMENT of our own accuracy — never a forecast or advice."""
    if not _MARKET_LEDGER_AVAILABLE:
        return {"status": "unavailable"}
    try:
        rep = market_ledger.report(DB_PATH)
        rep["status"] = "ok" if rep.get("resolved") else "empty"
        return rep
    except Exception as _mare:
        # Self-heal if the table is missing (brand-new ledger, first deploy): init once
        # and retry. Avoids per-request DDL on the happy path — only the error path inits.
        try:
            market_ledger.init_market_ledger_db(DB_PATH)
            rep = market_ledger.report(DB_PATH)
            rep["status"] = "ok" if rep.get("resolved") else "empty"
            return rep
        except Exception as _mare2:
            print(f"[market-accuracy] report error: {_mare2}")
            return {"status": "error", "detail": str(_mare2)}


@app.get("/market/accuracy/detail")
def market_accuracy_detail(limit: int = Query(300, ge=1, le=1000), verdict: str = ""):
    """Per-detection rows of the Money-Gradient ledger (ticker, flow, scores, realized price
    move, lead, verdict). Distinct from /accuracy/ledger/detail (the attention ledger)."""
    if not _MARKET_LEDGER_AVAILABLE:
        return {"rows": [], "count": 0, "status": "unavailable"}
    try:
        return market_ledger.detail(DB_PATH, limit=limit, verdict=(verdict or None))
    except Exception as _mde:
        try:
            market_ledger.init_market_ledger_db(DB_PATH)
            return market_ledger.detail(DB_PATH, limit=limit, verdict=(verdict or None))
        except Exception as _mde2:
            print(f"[market-accuracy] detail error: {_mde2}")
            return {"rows": [], "count": 0, "status": "error"}


@app.get("/crypto")
def crypto_feed():
    """Crypto Money Gradient feed (BTC/ETH…): Money Movement (D — crypto-exposure proxies: spot-ETF
    13F + MSTR/COIN insider[Finviz]+13F) + Market Confirmation (M — coin price/volume), per-coin flow.
    Flag-gated CRYPTO_SIGNAL. MEASUREMENT only — not advice, not a buy/sell signal, not a price forecast."""
    if not _CRYPTO_AVAILABLE:
        return {"available": False, "status": "unavailable", "coins": []}
    if not crypto_engine.CRYPTO_SIGNAL:
        return {"available": False, "status": "disabled", "coins": [],
                "note": "Crypto Money Gradient is in held-out research (CRYPTO_SIGNAL=0)."}
    # Served from the PREWARMED cache (parity with scores/topics/risk) — the live compute (FMP price +
    # Finviz/AV-throttled proxy Dark Matter across the roster) is too slow per-request and would time out.
    cached = _cache.get("crypto_full")
    if cached is not None:
        return cached
    # Cold cache (fresh boot, before the first prewarm completes): kick a background warm and return a
    # FAST "warming" response so the page never hangs. The client polls until the roster is ready.
    def _crypto_warm():
        try:
            _cache.set("crypto_full", crypto_engine.serve_crypto(db_path=DB_PATH), CACHE_TTL_SCORES_FULL)
        except Exception as _cwe:
            print(f"[crypto] warm error: {_cwe}")
    try:
        threading.Thread(target=_crypto_warm, daemon=True, name="crypto-warm").start()
    except Exception as _cte:
        print(f"[crypto] warm thread error: {_cte}")
    return {"available": True, "status": "warming", "model": "crypto-money-gradient-v1",
            "section": "Crypto", "coins": [], "count": 0,
            "note": "Warming the crypto money gradient — refresh in a moment."}


@app.get("/crypto/accuracy")
def crypto_accuracy_report():
    """Crypto Money Gradient ACCURACY LEDGER — DISTINCT from /accuracy/ledger (attention / Google
    Trends) and /market/accuracy (equity EOD price). Ground truth = realized COIN price direction
    (FMP crypto + AV). MUST precede /crypto/{coin} so it isn't captured as coin='accuracy'."""
    if not _CRYPTO_LEDGER_AVAILABLE:
        return {"status": "unavailable"}
    try:
        rep = crypto_ledger.report(DB_PATH)
        rep["status"] = "ok" if rep.get("resolved") else "empty"
        return rep
    except Exception as _car:
        try:
            crypto_ledger.init_crypto_ledger_db(DB_PATH)
            rep = crypto_ledger.report(DB_PATH)
            rep["status"] = "ok" if rep.get("resolved") else "empty"
            return rep
        except Exception as _car2:
            print(f"[crypto-ledger] report error: {_car2}")
            return {"status": "error", "detail": str(_car2)}


@app.get("/crypto/{coin}")
def crypto_detail(coin: str):
    """Per-coin Crypto Money Gradient detail (dual-ring + components + flow + price/Dark-Matter facts)."""
    if not _CRYPTO_AVAILABLE:
        return {"available": False, "status": "unavailable"}
    if not crypto_engine.CRYPTO_SIGNAL:
        return {"available": False, "status": "disabled"}
    try:
        c = (coin or "").upper()
        if c not in crypto_engine.cs.COIN_UNIVERSE:
            return {"available": False, "status": "unknown_coin", "coin": c}
        return crypto_engine.apply_crypto_signal(c, record_this_cycle=False, db_path=DB_PATH)
    except Exception as _cde:
        print(f"[crypto] detail error: {_cde}")
        return {"available": False, "status": "error", "detail": str(_cde)}


@app.post("/crypto/collect", dependencies=[Depends(_require_internal)])
def crypto_collect():
    """Record one crypto cycle per coin so the baseline-relative z-scores build over time (the coin
    reads CALIBRATING until ~3 cycles, like the market signal). Cron/scheduler calls this; internal-only."""
    if not (_CRYPTO_AVAILABLE and crypto_engine.CRYPTO_SIGNAL):
        return {"status": "disabled"}
    try:
        r = crypto_engine.serve_crypto(record=True, db_path=DB_PATH)
        # Record falsifiable crypto money-movement detections into the held-out accuracy ledger
        # (validated later vs realized coin price direction). Held-out — never feeds the score.
        led = {}
        if _CRYPTO_LEDGER_AVAILABLE:
            try:
                led = crypto_ledger.record_from_serve(r, db_path=DB_PATH)
            except Exception as _cle2:
                print(f"[crypto] ledger record error: {_cle2}")
        return {"status": "ok", "recorded": r.get("count", 0), "ledger": led,
                "coins": [c.get("coin") for c in r.get("coins", [])]}
    except Exception as _cce:
        print(f"[crypto] collect error: {_cce}")
        return {"status": "error", "detail": str(_cce)}


@app.get("/crypto/accuracy/detail")
def crypto_accuracy_detail(limit: int = Query(300, ge=1, le=1000), verdict: str = ""):
    """Per-detection rows of the crypto ledger (coin, flow, money_movement, realized price move, lead,
    verdict). Distinct from the attention + market ledgers."""
    if not _CRYPTO_LEDGER_AVAILABLE:
        return {"rows": [], "count": 0, "status": "unavailable"}
    try:
        return crypto_ledger.detail(DB_PATH, limit=limit, verdict=(verdict or None))
    except Exception:
        try:
            crypto_ledger.init_crypto_ledger_db(DB_PATH)
            return crypto_ledger.detail(DB_PATH, limit=limit, verdict=(verdict or None))
        except Exception as _cde:
            print(f"[crypto-ledger] detail error: {_cde}")
            return {"rows": [], "count": 0, "status": "error"}


@app.post("/crypto/accuracy/sweep", dependencies=[Depends(_require_internal)])
def crypto_accuracy_sweep(limit: int = Query(60, ge=1, le=500)):
    """Resolve pending crypto detections against realized coin price direction (FMP crypto + AV).
    Internal-only; cron/scheduler calls it. No-lookahead, honest denominator."""
    if not _CRYPTO_LEDGER_AVAILABLE:
        return {"status": "unavailable"}
    try:
        crypto_ledger.init_crypto_ledger_db(DB_PATH)
        return crypto_ledger.sweep_crypto_pending(DB_PATH, limit=limit)
    except Exception as _cse:
        print(f"[crypto-ledger] sweep error: {_cse}")
        return {"status": "error", "detail": str(_cse)}


@app.post("/market/accuracy/sweep", dependencies=[Depends(_require_internal)])
def market_accuracy_sweep(sync: int = 0, limit: int = Query(50, ge=1, le=500)):
    """Resolve pending money-movement detections against realized EOD price direction (FMP).
    Gated by MARKET_SIGNAL_V2 (the Money Gradient must be live to have detections to sweep)."""
    if not _MARKET_LEDGER_AVAILABLE:
        return {"status": "unavailable"}
    if os.getenv("MARKET_SIGNAL_V2", "0") != "1":
        return {"status": "disabled", "reason": "MARKET_SIGNAL_V2 is off — no money detections recorded yet"}
    if sync:
        return market_ledger.sweep_market_pending(DB_PATH, limit=limit)

    def _job():
        try:
            market_ledger.sweep_market_pending(DB_PATH, limit=limit)
        except Exception as exc:
            print(f"[market-accuracy] sweep error: {exc}")

    import threading
    threading.Thread(target=_job, daemon=True).start()
    return {"status": "started"}


@app.post("/accuracy/ledger/sweep", dependencies=[Depends(_require_internal)])
def accuracy_ledger_sweep(sync: int = 0, limit: int = Query(300, ge=1, le=5000)):
    """Resolve pending ATTENTION (Google-Trends) detections — hits / counted misses against the
    realized Google-Trends breakout. BUDGET-GUARDED against the shared Apify cap so this held-out
    measurement never starves the main collection pipeline (near the cap → free timeouts only).
    Internal-only; background by default. Each in-window row spends one $0.001 Trends fetch;
    timed-out rows resolve free. This is the on-demand drain for the pending backlog."""
    if not _LEDGER_PLUS_AVAILABLE:
        return {"status": "unavailable"}
    g = _apify_sweep_budget_ok()
    fetch_fn = None if g["ok"] else (lambda *_a, **_k: None)  # near cap → free timeouts only
    if sync:
        out = ledger_plus.sweep_pending(DB_PATH, limit=limit, fetch_fn=fetch_fn)
        return {"status": "done", "budget": g, "result": out}

    def _job():
        try:
            r = ledger_plus.sweep_pending(DB_PATH, limit=limit, fetch_fn=fetch_fn)
            print(f"[accuracy-ledger] manual sweep (apify {g.get('used')}/{g.get('cap')}): {r}")
        except Exception as exc:
            print(f"[accuracy-ledger] sweep error: {exc}")

    import threading
    threading.Thread(target=_job, daemon=True).start()
    return {"status": "started", "limit": limit, "budget": g}


@app.get("/research/mainstream-v2")
def research_mainstream_v2(topics: str = "world cup,mexico world cup,footballer", hours: int = 336):
    """HELD-OUT backtest (read-only, changes NO score): compares v1 vs v2 mainstream classification
    for each topic using its LIVE signals. v2 = the founder's trigger-vs-corroborator rule (a credible
    outlet is a dark-matter TRIGGER until ≥NEWS_QUORUM_V2 distinct outlets corroborate, or magnitude
    spikes). Also lists the distinct news outlets carrying each topic (eyeball real corroboration vs
    wire-syndication). expert_detection is held at a fixed 70 reference so the PATHWAY/weight shift is
    the meaningful output. The basis to review BEFORE flipping MAINSTREAM_V2."""
    try:
        import dual_pathway as dp
    except Exception as e:
        return {"available": False, "reason": f"dual_pathway unavailable: {e}"}
    out = []
    conn = get_db(DB_PATH)
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    try:
        for disp in [t.strip() for t in (topics or "").split(",") if t.strip()]:
            try:
                tk = _topic_key(disp)
            except Exception:
                tk = disp.lower().replace(" ", "_")
            q = ("SELECT ts.platform, ts.platform_tier, ts.source_name, ts.engagement_raw, "
                 "rs.title AS title FROM topic_signals ts "
                 "LEFT JOIN raw_signals rs ON rs.id = ts.signal_id "
                 "WHERE ts.topic_key = ? AND ts.extracted_at >= ? AND ts.platform_tier != 'unverified'")
            sig = [dict(r) for r in conn.execute(q, (tk, cutoff)).fetchall()]
            if not sig:
                row = conn.execute("SELECT topic_key FROM velocity_scores WHERE LOWER(topic_display)=? "
                                   "ORDER BY scored_at DESC LIMIT 1", (disp.lower(),)).fetchone()
                if row:
                    tk = row["topic_key"]
                    sig = [dict(r) for r in conn.execute(q, (tk, cutoff)).fetchall()]
            if not sig:
                out.append({"topic": disp, "topic_key": tk, "available": False, "reason": "no live signals"})
                continue
            hist = conn.execute("SELECT attention_magnitude, n_mainstream_platforms FROM velocity_scores "
                                "WHERE topic_key=? ORDER BY scored_at DESC LIMIT 12", (tk,)).fetchall()
            mags = sorted(float(h["attention_magnitude"] or 0) for h in hist)
            brs = sorted(float(h["n_mainstream_platforms"] or 0) for h in hist)
            mag_base = mags[len(mags) // 2] if mags else 0.0
            brd_base = brs[len(brs) // 2] if brs else 0.0

            def _run(v2: bool):
                dp.MAINSTREAM_V2 = v2
                return dp.blend(70, 65, {"M": 40, "I": 30, "P": 50}, sig,
                                breadth_baseline=brd_base, magnitude_baseline=mag_base,
                                baseline_cycles=len(hist), expert_confidence=60)
            b1, b2 = _run(False), _run(True)
            dp.MAINSTREAM_V2 = (os.getenv("MAINSTREAM_V2", "0") == "1")   # restore live state
            news = sorted({(s.get("source_name") or s.get("platform")) for s in sig
                           if (s.get("platform") or "").lower() in dp._NEWS_PLATFORMS})
            out.append({
                "topic": disp, "topic_key": tk, "available": True,
                "n_signals": len(sig), "n_news_outlets": len(news),
                "n_news_independent": b2.get("news_outlets_independent"),   # wire-syndication collapsed
                "magnitude": b1["magnitude"],
                "news_outlets_sample": news[:15],
                "v1": {"detection": b1["detection"], "pathway": b1["pathway"],
                       "w": b1["mainstream_ratio"], "mainstream_confirmed": b1["mainstream_confirmed"]},
                "v2": {"detection": b2["detection"], "pathway": b2["pathway"],
                       "w": b2["mainstream_ratio"], "mainstream_confirmed": b2["mainstream_confirmed"]},
            })
    except Exception as e:
        print(f"[mainstream-v2] {e}")
    finally:
        conn.close()
    return {"held_out": True, "news_quorum_v2": dp.NEWS_QUORUM_V2,
            "note": "v1 vs v2 mainstream on LIVE signals — read-only, no score change. expert_detection "
                    "fixed at 70 so the pathway/weight shift is the signal. Review before flipping MAINSTREAM_V2.",
            "comparison": out}


@app.get("/signal-x/{topic}")
def signal_x(topic: str):
    """Live X (Twitter) dual-role analysis for a topic (gated on X_BEARER_TOKEN).

    Cached 12h per topic to conserve the X post-cap quota (Basic tier =
    15,000 posts/month; each pull costs ~100). Repeated views of the same
    topic within the window cost zero extra posts. Only successful pulls are
    cached, so a rate-limited/empty response retries on the next request.
    """
    if not _X_AVAILABLE:
        return {"available": False, "reason": "X module unavailable"}
    cache_key = f"signal-x:{(topic or '').strip().lower()}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached
    # Budget guard + ledger (2026-06-12): this detail-page path spends a full
    # ~100-post search pull but previously neither checked nor recorded budget —
    # an uncounted leak against the monthly X post cap.
    if _x_posts_spent_this_month() + _X_POSTS_PER_PULL > _X_MONTHLY_POST_BUDGET:
        return {"available": False, "reason": "monthly X post budget exhausted"}
    result = xsig.build_x_gradient_contribution(topic)
    if isinstance(result, dict) and result.get("available"):
        _cache.set(cache_key, result, CACHE_TTL_XSIGNAL)
        _x_record_posts(_X_POSTS_PER_PULL)
        _x_record_pull()
    return result


def _x_candidate_topics(limit: int = None) -> list:
    """Universe the X velocity-trigger scan watches.

    Was: top-N by detection only — which self-reinforced the existing leaders
    (X could deepen topics already ranked but never diversify into new ones).
    Now a three-way blend, sized by X_SCAN_UNIVERSE. Widening costs nothing:
    the volume poll is FREE against the post cap, and deep pulls remain
    hard-capped by the monthly budget.
      • top third  — by detection (current leaders, unchanged behaviour)
      • mid third  — recent gravitational anomalies (first-timer surges +
        engagement asymmetry: the dark-matter-rich set where private chat
        is leaking into public — the highest-value X targets)
      • last third — newest first-detected topics (discovery tier: catches
        cross-domain entrants like sports/news before they rank anywhere)"""
    limit = int(limit or os.getenv("X_SCAN_UNIVERSE", "30"))
    per = max(3, limit // 3)
    out, seen = [], set()

    def _add(rows):
        for r in rows:
            td = r["topic_display"]
            key = (td or "").strip().lower()
            if td and key not in seen:
                seen.add(key)
                out.append(td)

    base = """
        SELECT v.topic_display
        FROM velocity_scores v
        INNER JOIN (
            SELECT topic_key, MAX(scored_at) AS m
            FROM velocity_scores GROUP BY topic_key
        ) l ON v.topic_key = l.topic_key AND v.scored_at = l.m
        INNER JOIN (
            SELECT topic_key, MIN(scored_at) AS f
            FROM velocity_scores GROUP BY topic_key
        ) fs ON v.topic_key = fs.topic_key
        WHERE COALESCE(v.total_mentions, 0) >= 5
    """
    try:
        conn = get_db(DB_PATH)
        _add(conn.execute(base + " ORDER BY v.detection_score DESC LIMIT ?",
                          (per,)).fetchall())
        _add(conn.execute(base + " AND v.is_gravitational_anomaly = 1 "
                          "ORDER BY v.scored_at DESC LIMIT ?",
                          (per,)).fetchall())
        _add(conn.execute(base + " ORDER BY fs.f DESC LIMIT ?",
                          (per,)).fetchall())
        conn.close()
        return out[:limit]
    except Exception as e:
        print(f"[x-scan] candidate query error: {e}")
        return out[:limit]


# Monthly X post-budget guard. Each deep author-gradient pull (search/recent)
# costs ~100 posts against X's 15,000/month cap. We hard-cap spend at this
# budget so a 100-topic scan can never overrun the cap — once exhausted, the
# scan keeps doing FREE volume checks but spends no more search pulls.
_X_POSTS_PER_PULL      = int(os.getenv("X_POSTS_PER_PULL", "120"))
# Cadence: 120 posts every 6h (1 pull/scan x 4 scans/day) = 480 posts/day.
# 480 x 31 = 14,880 posts/mo — the most a 31-day month can spend, still under
# the hard 15,000-post monthly cap (~120-post safety margin). Must match the
# X module's X_SAMPLE_SIZE so budget accounting stays accurate.
_X_MONTHLY_POST_BUDGET = int(os.getenv("X_MONTHLY_POST_BUDGET", "14880"))
# Daily ceiling: 4 pulls/day x 120 = 480 posts/day. With per-scan cap of 1 and
# 4 scans/day this is the natural rate; it also guards against bursts.
_X_DAILY_PULL_CAP      = int(os.getenv("X_DAILY_PULL_CAP", "4"))


def _x_pulls_today() -> int:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        conn = get_db(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS x_pull_usage "
                     "(day TEXT PRIMARY KEY, pulls INTEGER)")
        row = conn.execute("SELECT pulls FROM x_pull_usage WHERE day = ?",
                           (day,)).fetchone()
        conn.commit()
        conn.close()
        return int(row["pulls"]) if row and row["pulls"] is not None else 0
    except Exception as e:
        print(f"[x-budget] daily read error: {e}")
        return 0


def _x_record_pull() -> None:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        conn = get_db(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS x_pull_usage "
                     "(day TEXT PRIMARY KEY, pulls INTEGER)")
        conn.execute(
            "INSERT INTO x_pull_usage (day, pulls) VALUES (?, 1) "
            "ON CONFLICT(day) DO UPDATE SET pulls = x_pull_usage.pulls + 1",
            (day,),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[x-budget] daily write error: {e}")


def _x_posts_spent_this_month() -> int:
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    try:
        conn = get_db(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS x_post_usage (month TEXT PRIMARY KEY, posts INTEGER)")
        row = conn.execute("SELECT posts FROM x_post_usage WHERE month = ?", (month,)).fetchone()
        conn.commit()
        conn.close()
        return int(row["posts"]) if row and row["posts"] is not None else 0
    except Exception as e:
        print(f"[x-budget] read error: {e}")
        return 0


def _x_record_posts(n: int) -> None:
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    try:
        conn = get_db(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS x_post_usage (month TEXT PRIMARY KEY, posts INTEGER)")
        conn.execute(
            "INSERT INTO x_post_usage (month, posts) VALUES (?, ?) "
            "ON CONFLICT(month) DO UPDATE SET posts = x_post_usage.posts + ?",
            (month, n, n),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[x-budget] write error: {e}")


@app.get("/x/budget")
def x_budget():
    """Monthly X post-budget status (guards the 15k post cap).
    Note: path is /x/budget (NOT /signal-x/budget, which collides with the
    /signal-x/{topic} route)."""
    spent = _x_posts_spent_this_month()
    return {"month": datetime.now(timezone.utc).strftime("%Y-%m"),
            "posts_spent": spent, "budget": _X_MONTHLY_POST_BUDGET,
            "remaining": max(0, _X_MONTHLY_POST_BUDGET - spent),
            "posts_per_pull": _X_POSTS_PER_PULL}


def _x_write_feed_signal(topic: str, res: dict) -> None:
    """Write an X signal into the trends feed (raw_signals + topic_signals) so X
    contributes to the topic's gradient like other platforms. Tier reflects the
    dual role: expert-concentrated X = expert tier; viral/broad X = mainstream."""
    raw = res.get("raw") or {}
    vol = raw.get("volume") or {}
    grad = raw.get("gradient") or {}
    total = int(vol.get("total", 0) or 0)
    engagement = round(math.log1p(float(grad.get("total_engagement", 0) or 0)), 4)
    role = (res.get("x_role") or "").lower()
    tier = "expert" if "expert" in role or "insider" in role else "mainstream"
    # Spam/bot authenticity guard (mirrors the news writer): use the X signal-
    # integrity assessment to flag manufactured/coordinated chatter as NON-organic
    # so it cannot count toward dark matter. multiplier 1.0 = authentic, low = bot.
    integ = res.get("signal_integrity") or {}
    mult = integ.get("multiplier")
    classification = (integ.get("classification") or "").lower()
    is_organic = 1
    if (mult is not None and mult < 0.5) or any(
            w in classification for w in ("manufactured", "coordinated", "bot", "astroturf", "suspicious")):
        is_organic = 0
    tkey = _topic_key(topic)
    now = datetime.now(timezone.utc).isoformat()
    sig_id = hashlib.md5(f"x-{tkey}-{now[:13]}".encode()).hexdigest()[:16]  # hourly-deduped
    conn = get_db(DB_PATH)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO raw_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (sig_id, now, "x", tier, "search", topic[:500],
             "https://x.com/search?q=" + topic.replace(" ", "%20"), "",
             total, 0, engagement, 0.0, 0, is_organic, topic[:500]),
        )
        t_id = hashlib.md5(f"{sig_id}-{tkey}".encode()).hexdigest()[:16]
        conn.execute(
            "INSERT OR IGNORE INTO topic_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (t_id, now, topic, tkey, sig_id, "x", tier, "search",
             total, 0, engagement, 0, is_organic),
        )
        conn.commit()
        if _HEALTH_AVAILABLE:
            _log_health("x", total, "success", conn=conn)
    finally:
        conn.close()


def _x_velocity_scan(topics=None, threshold=None, limit=10) -> dict:
    """
    Cheap-trigger / expensive-confirm X monitor with a monthly post-budget cap.

    Polls counts/recent (FREE against the 15k post cap) for each candidate
    topic's volume velocity, and only spends a ~100-post search/recent pull
    when a topic is accelerating past `threshold`, isn't already cached, AND
    the monthly post budget still has room. The free volume scan continues even
    after the budget is exhausted, so the top-N are always monitored for $0.
    """
    if not _X_AVAILABLE:
        return {"available": False}
    # Trigger default lowered 40 → 25 (2026-06-12): with only ~7% of the monthly
    # post budget being spent, the scan was too conservative — the hard budget
    # cap below remains the real spend guard.
    threshold = float(threshold if threshold is not None
                      else os.getenv("X_VELOCITY_TRIGGER", "25"))
    topics = topics or _x_candidate_topics(limit if limit != 10 else None)
    spent = _x_posts_spent_this_month()
    pulls_today = _x_pulls_today()
    # Per-scan deep-pull cap. Runs every 6h, so 1 pull/scan = 100 posts/6h =
    # 400 posts/day = ~12,400/mo — matching the planned budget under the 15k cap.
    per_scan_cap = int(os.getenv("X_PULLS_PER_SCAN", "1"))
    # Pace the free volume polls — hitting counts/recent for many topics
    # back-to-back rate-limits after ~5 and silently shrinks the scan.
    pace_s = float(os.getenv("X_SCAN_PACE_S", "2.5"))

    # ── Phase 1: FREE volume/velocity poll for every candidate (counts/recent
    # does NOT draw down the 15k post cap) ──
    scanned = []
    for i, t in enumerate(topics):
        if i and pace_s > 0:
            time.sleep(pace_s)
        vol = xsig.collect_x_volume(t)
        if not vol:
            continue
        scanned.append({"topic": t, "velocity": vol.get("velocity", 0) or 0,
                        "total": vol.get("total", 0)})

    # ── Phase 2: spend the limited deep pulls (~100 posts each) on the TOP
    # trending movers — ranked by velocity desc so the per-scan/day/month budget
    # always goes to the highest-accelerating topics first ──
    movers = sorted([e for e in scanned if e["velocity"] >= threshold],
                    key=lambda e: e["velocity"], reverse=True)
    triggered, pulls, budget_skips = len(movers), 0, 0
    for entry in movers:
        t = entry["topic"]
        cache_key = f"signal-x:{(t or '').strip().lower()}"
        cached = _cache.get(cache_key)
        if cached is not None:
            entry["role"] = cached.get("x_role"); entry["pulled"] = False
            entry["cached"] = True
            continue
        if (pulls >= per_scan_cap
                or spent + _X_POSTS_PER_PULL > _X_MONTHLY_POST_BUDGET
                or pulls_today + pulls >= _X_DAILY_PULL_CAP):
            entry["budget_skipped"] = True; budget_skips += 1
            continue
        res = xsig.build_x_gradient_contribution(t)  # spends ~100 posts
        if isinstance(res, dict) and res.get("available"):
            _cache.set(cache_key, res, CACHE_TTL_XSIGNAL)
            spent += _X_POSTS_PER_PULL
            _x_record_posts(_X_POSTS_PER_PULL)
            _x_record_pull()
            entry["role"] = res.get("x_role"); entry["pulled"] = True; pulls += 1
            # Write X into the TRENDS FEED so it contributes to this topic's
            # gradient like any other platform.
            try:
                _x_write_feed_signal(t, res)
            except Exception as _xfe:
                print(f"[x-scan] feed write error '{t}': {_xfe}")
    print(f"[x-scan] scanned={len(scanned)} triggered={triggered} pulls={pulls} "
          f"per_scan_cap={per_scan_cap} budget_skips={budget_skips} "
          f"spent_month={spent}/{_X_MONTHLY_POST_BUDGET}")
    return {"available": True, "scanned": len(scanned), "triggered": triggered,
            "search_pulls_spent": pulls, "budget_skipped": budget_skips,
            "per_scan_cap": per_scan_cap,
            "posts_spent_month": spent, "monthly_budget": _X_MONTHLY_POST_BUDGET,
            "threshold": threshold, "results": scanned}


def _topic_source_context(topic_key: str, limit: int = 10) -> str:
    """Sample of how a term is ACTUALLY appearing — recent distinct headlines/post
    titles + the platform & community they came from. Fed to the AI explainer so
    it defines the SPECIFIC trend (e.g. 'japan' from World-Cup blogs = the team's
    run) instead of a generic dictionary definition of the bare word."""
    conn = None
    try:
        conn = get_db(DB_PATH)
        rows = conn.execute(
            """
            SELECT r.title AS title, ts.platform AS platform, ts.source_name AS src
            FROM topic_signals ts
            JOIN raw_signals r ON ts.signal_id = r.id
            WHERE ts.topic_key = ?
              AND r.title IS NOT NULL AND length(trim(r.title)) > 8
            ORDER BY ts.extracted_at DESC
            LIMIT 60
            """,
            (topic_key,),
        ).fetchall()
    except Exception as e:
        print(f"[explainer] context read error: {e}")
        return ""
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass

    lines, seen = [], set()
    for r in rows:
        title = " ".join((r["title"] or "").split())[:160]
        key = title.lower()
        if not title or key in seen:
            continue
        seen.add(key)
        venue = (r["src"] or r["platform"] or "").strip()
        plat = (r["platform"] or "").strip()
        tag = f"{plat}/{venue}" if venue and venue != plat else (venue or plat)
        lines.append(f"- [{tag}] {title}")
        if len(lines) >= limit:
            break
    return "\n".join(lines)


def _clean_explainer(short, full):
    """Repair an explainer whose `short` is a raw/fenced JSON blob (the
    '```json {"short": ...}' leak). Strips the fence and recovers the real short
    + full fields. Applied at SERVE time so already-persisted bad rows display
    cleanly without re-generating. No-op on already-clean text."""
    s = (short or "").strip()
    f = (full or "").strip()
    blob = s
    if blob.startswith("```"):
        blob = re.sub(r"^```[a-zA-Z0-9]*\s*", "", blob)
        blob = re.sub(r"```\s*$", "", blob).strip()
    if blob.startswith("{") and '"short"' in blob:
        def _un(x):
            try:
                return json.loads('"' + x + '"')
            except Exception:
                return x.replace("\\n", " ").replace('\\"', '"')
        sm = re.search(r'"short"\s*:\s*"((?:[^"\\]|\\.)*)"', blob, re.DOTALL)
        fm = re.search(r'"full"\s*:\s*"((?:[^"\\]|\\.)*)"', blob, re.DOTALL)
        if sm:
            s = _un(sm.group(1))
        if fm and (not f or f.startswith("```") or f.startswith("{")):
            f = _un(fm.group(1))
    return s, f


@app.get("/explainer/{topic_key}")
def topic_explainer(topic_key: str, topic: str = ""):
    """Evergreen plain-English explainer for a topic (what it is + why it
    matters), generated once via Perplexity and PERSISTED + in-memory cached so
    it's reused for all users at ~zero cost. Returns {short, full}.

    Connection-safe: in-memory cache avoids the DB on repeat calls (a 20-card
    feed previously opened ~40 connections and exhausted the pool); the table is
    created once at startup, not per call; connections use try/finally."""
    cache_key = f"explainer:{topic_key}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    # ── DB read (single pooled connection, always returned) ──
    conn = None
    try:
        conn = get_db(DB_PATH)
        row = conn.execute(
            "SELECT short, full_text FROM topic_explainers WHERE topic_key = ?", (topic_key,)
        ).fetchone()
        if row and row["short"]:
            _s, _f = _clean_explainer(row["short"], row["full_text"] or "")
            out = {"available": True, "short": _s, "full": _f, "cached": True}
            _cache.set(cache_key, out, CACHE_TTL_XSIGNAL)
            return out
    except Exception as e:
        print(f"[explainer] read error: {e}")
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass

    if not _AI_GRADE_AVAILABLE:
        return {"available": False, "reason": "explainer unavailable"}
    # Monthly AI-spend cap: once the budget is reached, do NOT make new paid
    # definition calls — only cached/persisted explainers are served.
    if not _ai_budget_ok():
        return {"available": False, "reason": "monthly AI budget reached",
                "budget": AI_MONTHLY_BUDGET_USD}
    name = (topic or topic_key.replace("_", " ")).strip()
    # Source-aware: feed the real headlines/posts + their platforms so the
    # explainer describes the SPECIFIC trend, not a dictionary definition.
    _ctx = _topic_source_context(topic_key)
    ex = ai_grade.explain_topic(name, context=_ctx)   # no DB connection held during this call
    if ex.get("available") and ex.get("short"):
        _record_ai_cost("definition", name, ex.get("cost") or {})
        conn = None
        try:
            conn = get_db(DB_PATH)
            conn.execute(
                "INSERT OR IGNORE INTO topic_explainers (topic_key, topic_display, short, full_text, created_at) "
                "VALUES (?,?,?,?,?)",
                (topic_key, name, ex["short"], ex.get("full", ""),
                 datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
        except Exception as e:
            print(f"[explainer] persist error: {e}")
        finally:
            if conn is not None:
                try: conn.close()
                except Exception: pass
        _s, _f = _clean_explainer(ex.get("short"), ex.get("full"))
        ex["short"], ex["full"] = _s, _f
        _cache.set(cache_key, ex, CACHE_TTL_XSIGNAL)
    return ex


def _backfill_explainers(limit: int = 12, pace: float = 3.5) -> int:
    """Generate + persist explainers for the highest-detection topics that don't
    have one yet. Runs each cycle so new topics get explained automatically as
    they appear in the scored list. Paced to respect Perplexity rate limits."""
    if not _AI_GRADE_AVAILABLE:
        return 0
    try:
        conn = get_db(DB_PATH)
        conn.execute("""CREATE TABLE IF NOT EXISTS topic_explainers (
            topic_key TEXT PRIMARY KEY, topic_display TEXT,
            short TEXT, full_text TEXT, created_at TEXT)""")
        conn.commit()
        rows = conn.execute("""
            SELECT v.topic_key, v.topic_display FROM velocity_scores v
            INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores GROUP BY topic_key) l
              ON v.topic_key = l.topic_key AND v.scored_at = l.m
            LEFT JOIN topic_explainers e ON v.topic_key = e.topic_key
            WHERE e.topic_key IS NULL AND v.topic_display IS NOT NULL
            ORDER BY v.detection_score DESC
            LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
    except Exception as e:
        print(f"[explainer] backfill query error: {e}")
        return 0

    done = 0
    for r in rows:
        # Stop backfilling the moment the monthly AI budget is reached.
        if not _ai_budget_ok():
            print(f"[explainer] backfill halted — monthly AI budget "
                  f"${AI_MONTHLY_BUDGET_USD} reached")
            break
        name = (r["topic_display"] or r["topic_key"].replace("_", " ")).strip()
        try:
            # Source-aware: same context the on-demand endpoint uses.
            ex = ai_grade.explain_topic(name, context=_topic_source_context(r["topic_key"]))
            if ex.get("available") and ex.get("short"):
                _record_ai_cost("definition", name, ex.get("cost") or {})
                c = get_db(DB_PATH)
                c.execute(
                    "INSERT OR IGNORE INTO topic_explainers (topic_key, topic_display, short, full_text, created_at) "
                    "VALUES (?,?,?,?,?)",
                    (r["topic_key"], name, ex["short"], ex.get("full", ""),
                     datetime.now(timezone.utc).isoformat()),
                )
                c.commit()
                c.close()
                done += 1
        except Exception as e:
            print(f"[explainer] backfill error for '{name}': {e}")
        time.sleep(pace)
    if done:
        print(f"[explainer] backfilled {done} explainers")
    return done


@app.post("/explainer/backfill", dependencies=[Depends(_require_internal)])
def explainer_backfill(payload: dict = Body(default={})):
    """Pre-generate explainers for top topics missing one (background)."""
    if not _AI_GRADE_AVAILABLE:
        return {"status": "unavailable"}
    limit = int(payload.get("limit", 100))

    def _job():
        try:
            n = _backfill_explainers(limit=limit)
            print(f"[explainer] manual backfill complete: {n}")
        except Exception as exc:
            print(f"[explainer] backfill job error: {exc}")

    import threading
    threading.Thread(target=_job, daemon=True).start()
    return {"status": "started", "limit": limit}


@app.post("/grade", dependencies=[Depends(_require_internal)])
def grade_topic_endpoint(payload: dict = Body(...)):
    """GRADE AGENT — pool-first grading. Searches the live data pool FIRST: if the
    topic is already scored, returns the MEASURED Gradient Score + N (no AI cost,
    charge_token=False); otherwise runs the AI grade (PROPOSED score + research +
    citations) and attaches the live N. Always returns a Gradient Score AND an N
    score with `source` ('measured'|'ai_proposed'). Serves all 3 platforms; token
    metering handled by the Django proxy (honour `charge_token`)."""
    topic = (str(payload.get("topic") or "")).strip()
    if not topic:
        raise HTTPException(400, "topic is required")
    cache_key = f"grade:{topic.lower()}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    if _GRADE_AGENT_AVAILABLE:
        result = grade_agent.resolve_grade(topic)
    else:
        # Fallback to the raw AI grade if the agent module didn't load.
        if not _AI_GRADE_AVAILABLE:
            return {"available": False, "reason": "AI grade module unavailable"}
        if not _ai_budget_ok():
            return {"available": False, "reason": "monthly AI budget reached"}
        result = ai_grade.grade_topic(topic)
        if isinstance(result, dict):
            result.setdefault("source", "ai_proposed")
            result.setdefault("charge_token", bool(result.get("available") and result.get("proposed")))

    if not isinstance(result, dict):
        return {"available": False, "reason": "grade failed"}

    src = result.get("source")
    if src == "measured" and result.get("available"):
        # Live data — short cache so it tracks the engine (no AI cost recorded).
        _cache.set(cache_key, result, CACHE_TTL_DETAIL)
    elif result.get("available") and result.get("proposed"):
        # AI research is stable — cache 12h + record the paid-call cost.
        _cache.set(cache_key, result, CACHE_TTL_XSIGNAL)
        _record_grade_cost(topic, result.get("cost") or {})
    return result


# ── AI spend ledger + monthly budget cap ─────────────────────────────────────
# ALL paid AI calls (topic DEFINITIONS via Perplexity + GRADES via Perplexity &
# Anthropic) are metered here against a hard monthly budget so spend never
# exceeds the cap. Default $20/mo, override with AI_MONTHLY_BUDGET_USD.
AI_MONTHLY_BUDGET_USD = float(os.getenv("AI_MONTHLY_BUDGET_USD", "20"))


def _ai_costs_table(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_costs (
            id TEXT PRIMARY KEY, kind TEXT, topic TEXT,
            perplexity_cost REAL, anthropic_cost REAL, total_cost REAL,
            created_at TEXT
        )
    """)


def _month_start_iso() -> str:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()


def _record_ai_cost(kind: str, topic: str, cost: dict) -> None:
    """Persist one paid AI call (kind = 'definition' | 'grade') by provider."""
    try:
        p = float((cost or {}).get("perplexity", 0) or 0)
        a = float((cost or {}).get("anthropic", 0) or 0)
        t = float((cost or {}).get("total", 0) or 0) or (p + a)
        conn = get_db(DB_PATH)
        _ai_costs_table(conn)
        conn.execute(
            "INSERT OR IGNORE INTO ai_costs VALUES (?,?,?,?,?,?,?)",
            (str(uuid.uuid4())[:24], kind, topic, p, a, t,
             datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ai-cost] record error: {e}")


def _ai_spend_this_month() -> dict:
    """Month-to-date AI spend by provider (UTC calendar month)."""
    try:
        conn = get_db(DB_PATH)
        _ai_costs_table(conn)
        conn.commit()
        row = conn.execute(
            "SELECT COALESCE(SUM(perplexity_cost),0) p, COALESCE(SUM(anthropic_cost),0) a, "
            "COALESCE(SUM(total_cost),0) t, COUNT(*) n FROM ai_costs WHERE created_at >= ?",
            (_month_start_iso(),)).fetchone()
        conn.close()
        return {"perplexity": float(row["p"] or 0), "anthropic": float(row["a"] or 0),
                "total": float(row["t"] or 0), "calls": int(row["n"] or 0)}
    except Exception as e:
        print(f"[ai-cost] month read error: {e}")
        return {"perplexity": 0.0, "anthropic": 0.0, "total": 0.0, "calls": 0}


def _ai_budget_ok() -> bool:
    """True if month-to-date AI spend is still under the monthly budget. New paid
    AI calls (definitions/grades) are SKIPPED once this returns False — cached/
    persisted results are still served, so the cap never breaks the product."""
    if AI_MONTHLY_BUDGET_USD <= 0:
        return True
    return _ai_spend_this_month().get("total", 0.0) < AI_MONTHLY_BUDGET_USD


def _record_grade_cost(topic: str, cost: dict) -> None:
    """Persist per-provider AI grade cost (unified ledger + legacy table)."""
    _record_ai_cost("grade", topic, cost)
    try:
        conn = get_db(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_grade_costs (
                id TEXT PRIMARY KEY, topic TEXT,
                perplexity_cost REAL, anthropic_cost REAL, total_cost REAL,
                created_at TEXT
            )
        """)
        conn.execute(
            "INSERT OR IGNORE INTO ai_grade_costs VALUES (?,?,?,?,?,?)",
            (str(uuid.uuid4())[:24], topic,
             float(cost.get("perplexity", 0) or 0), float(cost.get("anthropic", 0) or 0),
             float(cost.get("total", 0) or 0), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[grade] cost record error: {e}")


@app.get("/grade/costs")
def grade_costs():
    """Cumulative AI grade cost by provider — to compare Anthropic vs Perplexity
    and decide whether both are worth keeping."""
    try:
        conn = get_db(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_grade_costs (
                id TEXT PRIMARY KEY, topic TEXT,
                perplexity_cost REAL, anthropic_cost REAL, total_cost REAL,
                created_at TEXT
            )
        """)
        conn.commit()
        row = conn.execute("""
            SELECT COUNT(*) AS grades,
                   COALESCE(SUM(perplexity_cost),0) AS perplexity,
                   COALESCE(SUM(anthropic_cost),0)  AS anthropic,
                   COALESCE(SUM(total_cost),0)      AS total
            FROM ai_grade_costs
        """).fetchone()
        conn.close()
        n = row["grades"] or 0
        pplx, anth, total = row["perplexity"], row["anthropic"], row["total"]
        return {
            "grades": n,
            "perplexity_total": round(pplx, 4),
            "anthropic_total":  round(anth, 4),
            "total":            round(total, 4),
            "avg_per_grade":    round(total / n, 5) if n else 0,
            "perplexity_share": round(pplx / total * 100, 1) if total else 0,
            "anthropic_share":  round(anth / total * 100, 1) if total else 0,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/ai/costs")
def ai_costs():
    """Month-to-date AI spend (topic DEFINITIONS + GRADES, Perplexity + Anthropic)
    against the monthly budget. This is the cap that keeps AI spend under control —
    once `over_budget` is true, new paid AI calls are skipped (cached results still
    serve)."""
    mtd = _ai_spend_this_month()
    budget = AI_MONTHLY_BUDGET_USD
    total = round(mtd.get("total", 0.0), 4)
    # Per-kind breakdown for the current month.
    by_kind = {}
    try:
        conn = get_db(DB_PATH)
        _ai_costs_table(conn)
        conn.commit()
        for r in conn.execute(
            "SELECT kind, COALESCE(SUM(total_cost),0) t, COUNT(*) n FROM ai_costs "
            "WHERE created_at >= ? GROUP BY kind", (_month_start_iso(),)).fetchall():
            by_kind[r["kind"] or "unknown"] = {"total": round(float(r["t"] or 0), 4),
                                               "calls": int(r["n"] or 0)}
        conn.close()
    except Exception as e:
        print(f"[ai-cost] by-kind error: {e}")
    return {
        "month": _month_start_iso()[:7],
        "budget_usd": budget,
        "spent_usd": total,
        "remaining_usd": round(max(0.0, budget - total), 4) if budget > 0 else None,
        "pct_used": round(total / budget * 100, 1) if budget > 0 else None,
        "over_budget": (budget > 0 and total >= budget),
        "calls": mtd.get("calls", 0),
        "perplexity_usd": round(mtd.get("perplexity", 0.0), 4),
        "anthropic_usd": round(mtd.get("anthropic", 0.0), 4),
        "by_kind": by_kind,
    }


@app.post("/signal-x/scan", dependencies=[Depends(_require_internal)])
def signal_x_scan(payload: dict = Body(default={})):
    """Run the X velocity-trigger scan. Volume checks are free vs the post cap;
    a full author pull is spent only on topics accelerating past the threshold."""
    if not _X_AVAILABLE:
        return {"available": False, "reason": "X module unavailable"}
    return _x_velocity_scan(
        topics=payload.get("topics"),
        threshold=payload.get("velocity_threshold"),
        limit=int(payload.get("limit", 10)),
    )


@app.post("/query", dependencies=[Depends(_require_internal)])
def query_topic(payload: dict = Body(...)):
    """
    On-demand: collect signals for an arbitrary topic and score it
    (Enterprise direct query). Persists the result so it then appears in /scores.
    """
    topic = (str(payload.get("topic") or "")).strip()
    if not topic:
        raise HTTPException(400, "topic is required")
    tkey = _topic_key(topic)

    conn = get_db(DB_PATH)
    collected = collect_for_term(conn, topic)
    signals = detector._get_topic_signals(tkey, hours=72)
    result = detector.score_topic(tkey, signals)
    if result is None:
        conn.close()
        return {
            "found": False, "topic": topic, "topic_key": tkey,
            "signals_collected": collected,
            "detail": "Not enough signal to score this topic yet. Try a broader or more active term.",
        }
    if _CAL_AVAILABLE:
        try:
            result = apply_calibration(result, db_path=DB_PATH)
        except Exception:
            pass
    try:
        detector._update_topic_lifecycle(conn, result)
    except Exception:
        pass
    persist_velocity_score(conn, result)
    row = conn.execute(
        "SELECT * FROM velocity_scores WHERE topic_key=? ORDER BY scored_at DESC LIMIT 1",
        (tkey,),
    ).fetchone()
    conn.close()
    _cache.invalidate()
    formatted = _format_score_rows([row])
    res = formatted["results"][0] if formatted.get("results") else dict(row)
    return {"found": True, "topic": topic, "topic_key": tkey, "signals_collected": collected, "result": res}


def _compute_scores_full(sort_by: str, stage: str, min_score: float) -> list:
    """Heavy path — runs ONCE, result cached limit/offset-independently. Pulls the
    candidate window, applies calibration + the AI/noise filter, and returns the
    FULL sorted/filtered feed. /scores then serves O(1) page slices, so mobile and
    web can pull the whole feed 100 at a time with no per-page recompute."""
    sort_col = {
        "overall":    "overall_score",
        "detection":  "detection_score",
        "confidence": "confidence_score",
    }[sort_by]
    conn = get_db(DB_PATH)
    stage_filter = "" if stage == "all" else f"AND v.signal_stage = '{stage.upper()}'"
    # Over-fetch candidates: the noise filter in _format_score_rows drops
    # single-word/bigram garbage AFTER the SQL window, so pull a large candidate
    # set, filter, then page. (Cap independent of `limit` now — we compute the
    # full feed once and slice it.)
    candidate_cap = int(os.getenv("SCORES_CANDIDATE_CAP", "5000"))
    mentions_floor = int(os.getenv("MENTIONS_FLOOR", "5"))
    rows = conn.execute(f"""
        SELECT v.*, COALESCE(lc.first_detected_at, fs.first_at) AS first_scored_at,
               COALESCE(lc.total_scoring_cycles, 0) AS total_scoring_cycles
        FROM velocity_scores v
        INNER JOIN (
            SELECT topic_key, MAX(scored_at) as max_at
            FROM velocity_scores GROUP BY topic_key
        ) latest ON v.topic_key = latest.topic_key
            AND v.scored_at = latest.max_at
        INNER JOIN (
            SELECT topic_key, MIN(scored_at) as first_at
            FROM velocity_scores GROUP BY topic_key
        ) fs ON v.topic_key = fs.topic_key
        LEFT JOIN topic_lifecycle lc ON v.topic_key = lc.topic_key
        WHERE v.overall_score >= ?
          AND COALESCE(v.total_mentions, 0) >= ?
        {stage_filter}
        ORDER BY v.{sort_col} DESC, v.total_mentions DESC, v.scored_at DESC
        LIMIT ?
    """, (min_score, mentions_floor, candidate_cap)).fetchall()
    conn.close()
    result = _format_score_rows(rows)
    return result.get("results", [])


@app.get("/scores")
def get_all_scores(
    min_score: float = Query(0.0),
    stage: str = Query("all"),
    limit: int = Query(600, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("overall", enum=["overall", "detection", "confidence"]),
):
    """
    All scored topics with their velocity scores — PAGINATED.
    The full filtered/calibrated feed is computed once and cached; `limit` + `offset`
    return an O(1) slice so the clients can load the whole feed 100 at a time with
    no delay. Response includes `total` so the client knows when it has them all.
    """
    super_key = f"scores_full:{sort_by}:{stage}:{min_score}"
    full = _cache.get(super_key)
    if full is None:
        full = _compute_scores_full(sort_by, stage, min_score)
        _cache.set(super_key, full, CACHE_TTL_SCORES_FULL)

    total = len(full)
    page = full[offset: offset + limit]
    # Log the FIRST page as query events for the N component (paging through the
    # tail must not inflate N — that's not real user demand).
    if offset == 0:
        for item in page:
            if item.get("topic_key"):
                _log_topic_query(item["topic_key"], "/scores")
    return {"results": page, "count": len(page), "total": total,
            "offset": offset, "limit": limit}


@app.get("/history")
def get_pull_history(
    topic_key: str = Query(None),
    feed: str = Query("attention", enum=["attention", "risk"]),
    days: int = Query(1825, ge=1, le=36500),
    limit: int = Query(5000, ge=1, le=100000),
):
    """Full pull history (daily score snapshots) from inception. Pass a topic_key
    for one topic's full time series, or omit it for the most recent rows across
    the feed. No artificial day cap — pull_history is the permanent record."""
    conn = get_db(DB_PATH)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    cols = ("snapshot_date, feed, topic_key, topic_display, detection_score, "
            "confidence_score, overall_score, signal_stage, total_signals, scored_at")
    try:
        if topic_key:
            rows = conn.execute(
                f"SELECT {cols} FROM pull_history WHERE topic_key=? AND feed=? "
                f"AND snapshot_date>=? ORDER BY snapshot_date DESC LIMIT ?",
                (topic_key, feed, cutoff, limit)).fetchall()
        else:
            rows = conn.execute(
                f"SELECT {cols} FROM pull_history WHERE feed=? AND snapshot_date>=? "
                f"ORDER BY snapshot_date DESC, overall_score DESC LIMIT ?",
                (feed, cutoff, limit)).fetchall()
    except Exception as e:
        conn.close()
        return {"count": 0, "results": [], "error": str(e)}
    conn.close()
    return {"count": len(rows), "results": [dict(r) for r in rows]}


@app.get("/health/collectors")
def get_collector_health():
    """Collector-health report + a single trust gate the dashboard can use for
    an honest 'LIVE DATA' badge. Surfaces half-blind collection before it
    reaches a scored card."""
    if not _HEALTH_AVAILABLE:
        return {"available": False, "trust": True,
                "reason": "health monitor not loaded"}
    try:
        report = _health.get_health_report(DB_PATH)
        trust = _health.should_trust_scores(DB_PATH)
        return {"available": True, **report, "trust": trust["trust"],
                "trust_reason": trust["reason"]}
    except Exception as e:
        return {"available": False, "error": str(e), "trust": True}


# ── Monitoring agents (DATA_BUILDING_BLOCKS.md) — automated checks for the two
# recurring failure classes: data not pulling (Source Watchdog) and scores
# wrong/absent (Pipeline Integrity). Public read-only health, no secrets. ──
@app.get("/monitor")
def monitor_all():
    """Combined monitoring report — overall status + every agent's alerts. The
    one call an agent/dashboard polls to know if data + scoring are healthy."""
    if not _MONITOR_AVAILABLE:
        return {"available": False, "reason": "monitoring_agents not loaded"}
    conn = None
    try:
        conn = get_db(DB_PATH)
        return {"available": True, **_monitor.run_all(conn, db_path=DB_PATH)}
    except Exception as e:
        return {"available": False, "error": str(e)}
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass


@app.get("/monitor/datecanon")
def monitor_datecanon():
    """Canonical Date Auditor — is every stored date-semantic value canonical
    YYYY-MM-DD, across ALL sources? Audits the date COLUMNS (the funnel every source
    writes into) + discovers new *_date columns from the live schema, so new sources
    are covered automatically. Flags non-canonical values, ungated *_date columns,
    and pending human format reviews. (block B3a)"""
    if not _MONITOR_AVAILABLE:
        return {"available": False, "reason": "monitoring_agents not loaded"}
    conn = None
    try:
        conn = get_db(DB_PATH)
        return {"available": True, **_monitor.canon_date_auditor(conn=conn, db_path=DB_PATH)}
    except Exception as e:
        return {"available": False, "error": str(e)}
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass


@app.get("/quarantine/dates", dependencies=[Depends(_require_internal)])
def quarantine_dates(limit: int = Query(50, ge=1, le=500)):
    """The date-format human-review queue: values gate_date() could not parse, escalated
    to format_review_queue, each with candidate normalizations. This is the REVIEW
    interface the quarantine was missing — read-only; resolve via the POST below."""
    try:
        import ingestion_gate
        conn = get_db(DB_PATH)
        try:
            pending = ingestion_gate.pending_reviews(conn, limit=limit)
        finally:
            try: conn.close()
            except Exception: pass
        return {"available": True, "count": len(pending), "pending": pending,
                "note": "POST /quarantine/dates/resolve {id, chosen_value} to apply a "
                        "human decision (learns a rule so identical inputs auto-normalize)"}
    except Exception as e:
        return {"available": False, "error": str(e)}


@app.post("/quarantine/dates/resolve", dependencies=[Depends(_require_internal)])
def quarantine_dates_resolve(payload: dict = Body(...)):
    """Apply a HUMAN decision to a quarantined date and learn a format_rule so identical
    future inputs auto-normalize (gate_date consults it). Body: {id, chosen_value,
    save_rule?}. chosen_value must be canonical (validated) or empty to discard.
    Flag-never-force: nothing changes until a human posts here."""
    rid = (payload.get("id") or "").strip()
    chosen = (payload.get("chosen_value") or "").strip()
    save_rule = bool(payload.get("save_rule", True))
    if not rid:
        raise HTTPException(status_code=400, detail="id required")
    if chosen:                                   # validate — never learn a non-canonical rule
        from date_utils import to_iso_date
        norm = to_iso_date(chosen)
        if not norm:
            raise HTTPException(status_code=400,
                                detail=f"chosen_value '{chosen}' is not a parseable date")
        chosen = norm
    learn = save_rule and bool(chosen)           # discard (empty) marks resolved, learns nothing
    try:
        import ingestion_gate
        conn = get_db(DB_PATH)
        try:
            ingestion_gate.resolve_review(conn, rid, chosen, save_rule=learn)
        finally:
            try: conn.close()
            except Exception: pass
        return {"status": "resolved", "id": rid, "chosen_value": chosen,
                "rule_learned": learn}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/research/13f", dependencies=[Depends(_require_internal)])
def research_13f(fund: str = Query("", description="fund name or CIK; '' = Berkshire, 'all' = curated list"),
                 limit_funds: int = Query(10, ge=1, le=10)):
    """HELD-OUT institutional-positioning research: the latest 13F-HR holdings for mega-cap
    funds, straight from SEC EDGAR. NOT wired into any score (research-before-integrate per the
    Source Onboarding Protocol §16). Lazy-imports the held-out module so the scoring path never
    pulls it in."""
    try:
        import sec_13f_research as _f
    except Exception as e:
        return {"available": False, "error": f"module load: {e}"}
    q = (fund or "").strip()
    if q.lower() == "all":
        return _f.research_funds(limit_funds=limit_funds)
    if not q:
        return _f.latest_13f(_f.FUND_CIKS["Berkshire Hathaway"], "Berkshire Hathaway")
    # resolve by CIK or (case-insensitive) name
    cik, name = (q, "") if q.isdigit() else (None, q)
    if cik is None:
        for n, c in _f.FUND_CIKS.items():
            if n.lower() == q.lower():
                cik, name = c, n
                break
    if cik is None:
        return {"available": False, "reason": f"unknown fund '{q}'",
                "known_funds": list(_f.FUND_CIKS.keys())}
    return _f.latest_13f(cik, name)


@app.get("/research/dark-positioning", dependencies=[Depends(_require_internal)])
def research_dark_positioning(top_congress: int = Query(25, ge=0, le=80)):
    """HELD-OUT combined dark-positioning signal: per-ticker smart-money (curated 13F funds)
    + political (Congress) positioning, ranked. This is the EXACT signal that augments Market
    Signal `positioning_concentration` when DARK_POSITIONING_V2=1 — review it here first.
    Not wired into any score while the flag is off (default)."""
    try:
        import positioning_intel as _pi
        wl = risk.WATCHLIST_TICKERS if (_RISK_AVAILABLE and hasattr(risk, "WATCHLIST_TICKERS")) else {}
        return _pi.all_signals(wl, top_congress=top_congress)
    except Exception as e:
        return {"available": False, "error": str(e)}


@app.get("/research/congress", dependencies=[Depends(_require_internal)])
def research_congress(limit: int = Query(25, ge=1, le=100), top_n: int = Query(15, ge=1, le=50)):
    """HELD-OUT congressional-trading research (QuiverQuant) — recent trades + per-ticker
    concentration (where political money moves). NOT wired into any score (research-before-
    integrate per §16). Token from env QUIVER_API_KEY. Lazy-import keeps it out of scoring."""
    try:
        import quiver_research as _q
    except Exception as e:
        return {"available": False, "error": f"module load: {e}"}
    return _q.congress_recent(limit=limit, top_n=top_n)


@app.get("/schema", dependencies=[Depends(_require_internal)])
def db_schema():
    """Live DB schema introspection (information_schema + planner row estimates) — the
    source of truth for regenerating DB_DATA_DICTIONARY.md so it never drifts stale again.
    Read-only."""
    conn = get_db(DB_PATH)
    try:
        cols = conn.execute(
            "SELECT table_name, column_name, data_type, is_nullable, ordinal_position "
            "FROM information_schema.columns WHERE table_schema='public' "
            "ORDER BY table_name, ordinal_position").fetchall()
        est = {}
        try:
            for r in conn.execute(
                "SELECT relname, reltuples::bigint AS n FROM pg_class c "
                "JOIN pg_namespace ns ON ns.oid=c.relnamespace "
                "WHERE ns.nspname='public' AND c.relkind='r'").fetchall():
                est[(r["relname"] if hasattr(r, "keys") else r[0])] = \
                    int(r["n"] if hasattr(r, "keys") else r[1])
        except Exception:
            pass
    finally:
        try: conn.close()
        except Exception: pass

    def _g(r, k, i):
        return (r[k] if hasattr(r, "keys") else r[i])
    tables = {}
    for r in cols:
        t = _g(r, "table_name", 0)
        tables.setdefault(t, []).append({
            "column": _g(r, "column_name", 1),
            "type": _g(r, "data_type", 2),
            "nullable": _g(r, "is_nullable", 3) == "YES"})
    out = [{"table": t, "row_estimate": est.get(t), "columns": c}
           for t, c in sorted(tables.items())]
    return {"table_count": len(out), "generated_for": "DB_DATA_DICTIONARY.md", "tables": out}


@app.get("/monitor/scoringcontract")
def monitor_scoringcontract():
    """Scoring Contract Auditor — is every scoring field in the declared format
    (type/unit/range/enum/required), is a derived field (heisenberg_gap) consistent,
    and is any scoring field DEGENERATE (one value across the universe = missing-as-zero
    fingerprint)? Audits the live DATA against SCORING_CONTRACT; new scoring-shaped
    columns are flagged to classify. (block B3b)"""
    if not _MONITOR_AVAILABLE:
        return {"available": False, "reason": "monitoring_agents not loaded"}
    conn = None
    try:
        conn = get_db(DB_PATH)
        return {"available": True, **_monitor.scoring_contract_auditor(conn=conn, db_path=DB_PATH)}
    except Exception as e:
        return {"available": False, "error": str(e)}
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass


@app.get("/monitor/sources")
def monitor_sources():
    """Source Watchdog — are all sources pulling within SLA? (blocks B1, B2)"""
    if not _MONITOR_AVAILABLE:
        return {"available": False, "reason": "monitoring_agents not loaded"}
    conn = None
    try:
        conn = get_db(DB_PATH)
        return {"available": True, **_monitor.source_watchdog(conn=conn, db_path=DB_PATH)}
    except Exception as e:
        return {"available": False, "error": str(e)}
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass


@app.get("/monitor/scorer")
def monitor_scorer():
    """Scorer Watchdog — is a scorer alive, WHICH one (local worker vs Heroku
    cloud/failover), and is the failover posture healthy? (block B4, process
    liveness — pairs with /monitor/pipeline's data-freshness check)."""
    if not _MONITOR_AVAILABLE:
        return {"available": False, "reason": "monitoring_agents not loaded"}
    try:
        return {"available": True, **_monitor.scorer_watchdog(db_path=DB_PATH)}
    except Exception as e:
        return {"available": False, "error": str(e)}


@app.get("/monitor/pipeline")
def monitor_pipeline():
    """Pipeline Integrity Monitor — scoring fresh? topics clean + deduped? serve
    fields present? (blocks B3, B4, B8)"""
    if not _MONITOR_AVAILABLE:
        return {"available": False, "reason": "monitoring_agents not loaded"}
    conn = None
    try:
        conn = get_db(DB_PATH)
        return {"available": True, **_monitor.pipeline_integrity(conn)}
    except Exception as e:
        return {"available": False, "error": str(e)}
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass


@app.get("/monitor/cost")
def monitor_cost():
    """Cost Sentinel — AI ($/mo) + X (posts/mo) budgets vs cap. (block B7)"""
    if not _MONITOR_AVAILABLE:
        return {"available": False, "reason": "monitoring_agents not loaded"}
    try:
        return {"available": True, **_monitor.cost_sentinel()}
    except Exception as e:
        return {"available": False, "error": str(e)}


@app.get("/monitor/calibration")
def monitor_calibration():
    """Calibration Auditor — Accuracy Ledger honest + denominator-backed? (block B5)"""
    if not _MONITOR_AVAILABLE:
        return {"available": False, "reason": "monitoring_agents not loaded"}
    try:
        return {"available": True, **_monitor.calibration_auditor()}
    except Exception as e:
        return {"available": False, "error": str(e)}


@app.get("/monitor/quality")
def monitor_quality():
    """Topic Quality Auditor — news-filler/multi-word fragments + geo/country
    category mis-sorts + category clarity (block B3 deep)."""
    if not _MONITOR_AVAILABLE:
        return {"available": False, "reason": "monitoring_agents not loaded"}
    conn = None
    try:
        conn = get_db(DB_PATH)
        return {"available": True, **_monitor.fragment_category_auditor(conn)}
    except Exception as e:
        return {"available": False, "error": str(e)}
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass


@app.get("/monitor/catchall")
def monitor_catchall():
    """Catch-All Auditor — specialist for the news/general catch-all congestion:
    catch-all %, corroboration-floor health, misclassified tracked calls, and the
    top lexicon-candidate terms to reclassify (block B3)."""
    if not _MONITOR_AVAILABLE:
        return {"available": False, "reason": "monitoring_agents not loaded"}
    conn = None
    try:
        conn = get_db(DB_PATH)
        return {"available": True, **_monitor.catchall_auditor(conn)}
    except Exception as e:
        return {"available": False, "error": str(e)}
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass


@app.get("/diagnostic/market/{symbol}")
def diagnostic_market(symbol: str):
    """Market Signal Diagnostic — audits ONE instrument's scoring: baseline depth,
    stdev-floor binding, provenance, and tier/deviation contradiction. Read-only;
    catches cold-start artifacts like SPCX (INSUFFICIENT_HISTORY)."""
    if not _DIAG_AVAILABLE:
        return {"available": False, "reason": "diagnostics not loaded"}
    try:
        return {"available": True, **_mkt_diag.run(symbol)}
    except Exception as e:
        return {"available": False, "error": str(e)}


@app.get("/diagnostic/trend/{topic}")
def diagnostic_trend(topic: str):
    """Trend Signal Diagnostic — audits ONE topic's Gradient Score: saturation,
    N-discipline reconcile (expert pathway), what-if-N inversion, frozen range.
    Read-only."""
    if not _DIAG_AVAILABLE:
        return {"available": False, "reason": "diagnostics not loaded"}
    try:
        return {"available": True, **_trd_diag.run(topic)}
    except Exception as e:
        return {"available": False, "error": str(e)}


@app.get("/diagnostic/trend-distribution")
def diagnostic_trend_distribution(limit: int = Query(30, ge=5, le=200)):
    """Trend Signal cross-topic distribution — is Detection/Confidence actually
    separating topics, or collapsing them onto shared values? Read-only."""
    if not _DIAG_AVAILABLE:
        return {"available": False, "reason": "diagnostics not loaded"}
    try:
        return {"available": True, **_trd_diag.run_distribution(limit)}
    except Exception as e:
        return {"available": False, "error": str(e)}


@app.get("/monitor/market-coverage")
def monitor_market_coverage():
    """Market Universe Coverage — publicly-traded companies trending in attention
    but MISSING from the Market Signal universe (the 'SpaceX problem'). Standalone
    (not in /monitor) because it makes per-candidate Finnhub ticker lookups (block B1)."""
    if not _MONITOR_AVAILABLE:
        return {"available": False, "reason": "monitoring_agents not loaded"}
    conn = None
    try:
        conn = get_db(DB_PATH)
        return {"available": True, **_monitor.market_universe_coverage(conn)}
    except Exception as e:
        return {"available": False, "error": str(e)}
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass


@app.get("/monitor/subscriptions")
def monitor_subscriptions():
    """Data Subscriptions — every external data API: configured?, billing class,
    and whether each paid one has a tracked cost (block B7)."""
    if not _MONITOR_AVAILABLE:
        return {"available": False, "reason": "monitoring_agents not loaded"}
    try:
        return {"available": True, **_monitor.data_subscriptions()}
    except Exception as e:
        return {"available": False, "error": str(e)}


@app.get("/usage", dependencies=[Depends(_require_internal)])
def api_usage_report():
    """INTERNAL / founder-only: per-source external-API call counts (today / 7d /
    30d / all-time) for cost + financial-viability monitoring. Gated by
    X-Internal-Key — never exposed to app users."""
    if not _HEALTH_AVAILABLE:
        return {"available": False}
    try:
        return {"available": True, **_health.get_api_usage(DB_PATH)}
    except Exception as e:
        return {"available": False, "error": str(e)}


# ── Signal-table retention (added 2026-06-12, Heroku 1GB plan alert) ─────
# raw_signals + topic_signals were UNBOUNDED (every other table had pruning).
# Scoring reads only the last 72h of signals, so anything older is dead weight
# except author_history (first-timer memory — separate table, untouched).

def _prune_signal_tables(days: int = None) -> dict:
    """DELETE raw_signals/topic_signals older than `days` (floor 4 to protect
    the 72h scoring window) and topic_queries older than 45d (N uses 30d).
    Returns per-table deleted row counts."""
    days = max(4, int(days or os.getenv("SIGNAL_RETENTION_DAYS", "7")))
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    q_cutoff = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
    out = {"retention_days": days}
    conn = get_db(DB_PATH)
    try:
        for table, col, cut in (("topic_signals", "extracted_at", cutoff),
                                ("raw_signals", "collected_at", cutoff),
                                ("topic_queries", "queried_at", q_cutoff)):
            try:
                cur = conn.execute(f"DELETE FROM {table} WHERE {col} < ?", (cut,))
                out[table] = cur.rowcount
            except Exception as e:
                out[table] = f"error: {e}"
        conn.commit()
    finally:
        conn.close()
    print(f"[retention] signals pruned: {out}")
    return out


@app.get("/maint/db", dependencies=[Depends(_require_internal)])
def maint_db_size():
    """INTERNAL: per-table disk usage — shows what is eating the Postgres plan."""
    if not os.getenv("DATABASE_URL"):
        return {"available": False, "reason": "not running on Postgres"}
    conn = get_db(DB_PATH)
    try:
        rows = conn.execute("""
            SELECT c.relname AS table_name,
                   pg_total_relation_size(c.oid) AS bytes
            FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public' AND c.relkind = 'r'
            ORDER BY pg_total_relation_size(c.oid) DESC
        """).fetchall()
        db = conn.execute(
            "SELECT pg_database_size(current_database()) AS b").fetchone()
        return {"available": True,
                "database_mb": round((db["b"] or 0) / 1048576.0, 1),
                "tables": [{"table": r["table_name"],
                            "mb": round((r["bytes"] or 0) / 1048576.0, 1)}
                           for r in rows[:20]]}
    except Exception as e:
        return {"available": False, "error": str(e)}
    finally:
        conn.close()


@app.post("/maint/prune", dependencies=[Depends(_require_internal)])
def maint_prune(days: int = Query(None, ge=4), vacuum: int = Query(0),
                vel_days: int = Query(None, ge=3)):
    """INTERNAL: prune the high-volume tables. Pass vacuum=1 to also
    VACUUM FULL them (Postgres only) — DELETE alone frees space for reuse but
    Heroku measures file size, which only VACUUM FULL shrinks. VACUUM briefly
    locks each table; run during a quiet window.

    velocity_scores (598MB at the 1GB alert) keeps per-cycle rows: the durable
    12-month record lives in pull_history (daily snapshots), the app's
    score-history view shows the last 30 CYCLES (~15h), and momentum reads
    recent cycles only — so 14d of per-cycle detail is ample."""
    result = {"pruned": _prune_signal_tables(days)}
    try:
        _vd = int(vel_days or os.getenv("VELOCITY_KEEP_DAYS", "365"))
        result["velocity_scores"] = prune_velocity_scores(DB_PATH, days=_vd)
    except Exception as e:
        result["velocity_scores"] = f"error: {e}"
    if vacuum and os.getenv("DATABASE_URL"):
        try:
            import psycopg2
            vconn = psycopg2.connect(os.getenv("DATABASE_URL"))
            vconn.autocommit = True  # VACUUM cannot run inside a transaction
            vcur = vconn.cursor()
            for table in ("velocity_scores", "topic_signals", "raw_signals",
                          "topic_queries", "anomaly_log"):
                try:
                    vcur.execute(f"VACUUM FULL {table}")
                    result[f"vacuum_{table}"] = "ok"
                except Exception as ve:
                    result[f"vacuum_{table}"] = f"error: {ve}"
            vconn.close()
        except Exception as e:
            result["vacuum"] = f"error: {e}"
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
    # SINGLE SOURCE OF TRUTH: serve the SAME fully-calibrated row the /scores list
    # serves (mainstream dual-pathway preserved, expert calibrated), so the detail
    # headline + components can NEVER diverge from the list/feed. Prefer the
    # precomputed serve_payload (identical to /scores); fall back to live
    # calibration for long-tail topics that have no payload yet.
    _payload = s.pop("serve_payload", None)
    if _payload:
        try:
            s = _parse_json_fields(json.loads(_payload))
        except Exception:
            s = _calibrate_score_fields(s)
    else:
        s = _calibrate_score_fields(s)
    gap = s.get("heisenberg_gap", 0) or 0
    p   = s.get("persistence_score", 0) or 0
    n   = s.get("nowtrendin_score", 0) or 0
    lc_dict = dict(lc) if lc else {}

    # Log this detail view as a query event for the N component
    _log_topic_query(topic_key, f"/scores/{topic_key}")

    result = {
        "topic":        s["topic_display"],
        "topic_key":    topic_key,
        "category":     _category_for(topic_key, s["topic_display"]),
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

        # ── SIX EXTERNAL COMPONENTS (G·I·M·D·C·P) — weights renormalized to 100%.
        # N (internal demand) is shown below but is NOT part of the composite.
        "components": {
            "G_gradient_strength": {
                "score":  s["gradient_strength"],
                "weight_overall": "24%", "weight_detect": "38%", "weight_conf": "12%",
                "raw_ratio": s.get("gradient_ratio"),
                "niche_mentions": s.get("niche_mentions"),
                "mainstream_mentions": s.get("mainstream_mentions"),
                "plain_english": _explain_g(s["gradient_strength"]),
            },
            "I_inertia": {
                "score":  s["inertia_score"],
                "weight_overall": "22%", "weight_detect": "18%", "weight_conf": "28%",
                "plain_english": _explain_i(s["inertia_score"]),
            },
            "M_platform_diversity": {
                "score":    s["platform_diversity"],
                "weight_overall": "17%", "weight_detect": "10%", "weight_conf": "22%",
                "platforms": s.get("platforms_active", []),
                "plain_english": _explain_m(
                    s["platform_diversity"],
                    s.get("platforms_active", [])
                ),
            },
            "D_dark_matter": {
                "score":              s["dark_matter_score"],
                "weight_overall": "13%", "weight_detect": "22%", "weight_conf": "4%",
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
                "weight_overall": "8%", "weight_detect": "6%", "weight_conf": "7%",
                "plain_english": _explain_c(s["confidence_decay"]),
            },
            "P_persistence": {
                "score":   p,
                "weight_overall": "16%", "weight_detect": "7%", "weight_conf": "27%",
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
                # Displayed-only signal — NOT part of the Gradient composite (kept
                # external-only to preserve objectivity / avoid a demand feedback loop).
                "weight_overall": "—", "weight_detect": "—", "weight_conf": "—",
                "in_composite": False,
                "label": "Community demand (separate signal)",
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

    # ── Separate "Now Trending Gradient Score" (demand-inclusive what-if) ──
    # The default dual score above stays N-free; this folds N in as an extra
    # factor. Only the resulting numbers are exposed (N weighting stays internal).
    _ntd, _ntc, _ndd = _now_trending_gradient(
        s.get("detection_score"), s.get("confidence_score"), n, s.get("total_mentions"))
    if _ntd is not None:
        result["velocity_scores"]["nowtrending_gradient_detection"]  = _ntd
        result["velocity_scores"]["nowtrending_gradient_confidence"] = _ntc
        result["velocity_scores"]["nowtrending_gradient_demand_driven"] = _ndd

    # ── Rich parity payload: attach the SAME serialized row the mobile /scores
    # list renders, so the web detail can show maturity / AI tier / variations /
    # N + Now-Trending-Gradient / dark-matter detail without a second shape.
    # Best-effort — a failure here must never break the core detail response. ──
    try:
        conn2 = get_db(DB_PATH)
        rrow = conn2.execute("""
            SELECT v.*, COALESCE(lc.first_detected_at, fs.first_at) AS first_scored_at,
                   COALESCE(lc.total_scoring_cycles, 0) AS total_scoring_cycles
            FROM velocity_scores v
            INNER JOIN (SELECT topic_key, MAX(scored_at) max_at FROM velocity_scores
                        WHERE topic_key = ? GROUP BY topic_key) latest
              ON v.topic_key = latest.topic_key AND v.scored_at = latest.max_at
            INNER JOIN (SELECT topic_key, MIN(scored_at) first_at FROM velocity_scores
                        WHERE topic_key = ? GROUP BY topic_key) fs
              ON v.topic_key = fs.topic_key
            LEFT JOIN topic_lifecycle lc ON v.topic_key = lc.topic_key
            WHERE v.topic_key = ? ORDER BY v.scored_at DESC LIMIT 1
        """, (topic_key, topic_key, topic_key)).fetchall()
        conn2.close()
        _rich = _format_score_rows(rrow)
        if _rich.get("results"):
            result["rich"] = _rich["results"][0]
    except Exception as _re:
        print(f"[detail] rich attach skipped for {topic_key}: {_re}")

    # ── Trade-secret hygiene: never expose the component weighting or the
    # calibration false-positive rates over the public API. The app renders
    # component SCORES, not weights, so dropping these is UI-safe. ──
    for _comp in result.get("components", {}).values():
        if isinstance(_comp, dict):
            for _wk in ("weight_overall", "weight_detect", "weight_conf"):
                _comp.pop(_wk, None)
    _heis = result.get("heisenberg")
    if isinstance(_heis, dict):
        _heis.pop("false_positive_detect", None)
        _heis.pop("false_positive_confirm", None)

    _cache.set(cache_key, result, CACHE_TTL_DETAIL)
    return result


@app.get("/scores/{topic_key}/score-history")
def get_topic_score_history(topic_key: str, limit: int = 30):
    """
    Per-collection-run scoring events for a topic (newest first).
    Each row is a real scoring event from velocity_scores.
    """
    conn = get_db(DB_PATH)
    # Select full rows so the SAME serve-time calibration applied to the headline
    # score can be applied to each historical row — otherwise the history shows
    # raw pre-calibration values (e.g. DET 10) that contradict the headline (43).
    rows = conn.execute(
        """
        SELECT * FROM velocity_scores
        WHERE topic_key = ?
        ORDER BY scored_at DESC
        LIMIT ?
        """,
        (topic_key, limit),
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        s = _parse_json_fields(dict(r))
        s = _calibrate_score_fields(s)   # same calibration as /scores
        det = round(s.get("detection_score") or 0)
        conf = round(s.get("confidence_score") or 0)
        # Per-cycle FACTORS that explain why the score moved between points — surfaced
        # so the detail chart can annotate each data point (volume, diffusion, stage).
        pa = s.get("platforms_active")
        if isinstance(pa, str):
            try:
                pa = json.loads(pa or "[]")
            except Exception:
                pa = []
        out.append({
            "scored_at": s.get("scored_at"),
            "detection": det,
            "confidence": conf,
            "overall": round(s.get("overall_score") or 0),
            "gap": abs(det - conf),
            # explanatory factors (best-effort; null when a column is absent)
            "mentions": int(s.get("total_mentions") or 0),
            "platforms": len(pa) if isinstance(pa, list) else 0,
            "stage": s.get("signal_stage") or "",
            "inertia": round(s.get("inertia_score") or 0),
            "dark_matter": round(s.get("dark_matter_score") or 0),
        })
    return {"topic_key": topic_key, "count": len(out), "rows": out, "calibrated": True}


HISTORY_FULL_CAP = int(os.getenv("HISTORY_FULL_CAP", "2000"))

def _compute_history_full(window: str, points: int) -> list:
    """Heavy per-topic trajectory build for the History view — computed at the full
    cap (limit-INDEPENDENT) so the endpoint can cache it once per (window, points)
    and serve O(1) slices. Read-only: pulls from velocity_scores, writes nothing."""
    import datetime as _dt
    hours = {"12h": 12, "24h": 24, "7d": 168, "30d": 720}.get(window, 168)
    cut = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=hours)).isoformat()
    cap = HISTORY_FULL_CAP
    conn = get_db(DB_PATH)
    try:
        latest = conn.execute(
            """
            SELECT v.* FROM velocity_scores v
            INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores
                        WHERE scored_at >= ? GROUP BY topic_key) l
              ON v.topic_key = l.topic_key AND v.scored_at = l.m
            ORDER BY v.overall_score DESC NULLS LAST
            LIMIT ?
            """, (cut, cap * 3)).fetchall()
        picked = []
        for r in latest:
            disp = r["topic_display"] or r["topic_key"]
            if not _is_quality_topic(disp):
                continue
            picked.append(dict(r))
            if len(picked) >= cap:
                break
        keys = [r["topic_key"] for r in picked]
        series = {}
        if keys:
            ph = ",".join(["?"] * len(keys))
            for h in conn.execute(
                f"""SELECT topic_key, scored_at, overall_score, detection_score, confidence_score
                    FROM velocity_scores WHERE topic_key IN ({ph}) AND scored_at >= ?
                    ORDER BY scored_at ASC""", (*keys, cut)).fetchall():
                series.setdefault(h["topic_key"], []).append({
                    "t": h["scored_at"],
                    "overall": round(h["overall_score"] or 0, 1),
                    "det": round(h["detection_score"] or 0, 1),
                    "conf": round(h["confidence_score"] or 0, 1),
                })
    finally:
        conn.close()
    out = []
    for r in picked:
        cur = r
        pl = r.get("serve_payload")
        if pl:
            try:
                cur = json.loads(pl)
            except Exception:
                cur = r
        s = series.get(r["topic_key"], [])[-points:]
        ys = [p["overall"] for p in s]
        slope = round(ys[-1] - ys[0], 1) if len(ys) >= 2 else 0.0
        trend = "up" if slope >= 3 else "down" if slope <= -3 else "flat"
        out.append({
            "topic_key": r["topic_key"],
            "topic_display": r["topic_display"] or r["topic_key"],
            "category": _category_for(r["topic_key"], r["topic_display"] or ""),
            "overall": round(cur.get("overall_score") or 0),
            "det": round(cur.get("detection_score") or 0),
            "conf": round(cur.get("confidence_score") or 0),
            "n": round(cur.get("nowtrendin_score") or 0),
            "stage": cur.get("signal_stage"),
            "is_anomaly": bool(cur.get("is_gravitational_anomaly")),
            "scored_at": r["scored_at"], "series": s, "trend": trend, "slope": slope,
        })
    return out


@app.get("/history/recent")
def history_recent(window: str = Query("7d"), limit: int = Query(300, ge=1, le=2000),
                   offset: int = Query(0, ge=0), points: int = Query(12, ge=2, le=40)):
    """Recent scoring TRAJECTORY per topic — powers the History view (web + mobile,
    one shared source). One call returns each topic's current score (from the
    calibrated serve_payload, so it matches /scores) plus its last `points` cycles
    within `window` and a slope-based up/down/flat trend, so clients draw sparklines
    without N requests.

    Superset-cached per (window, points) and kept hot by the Prewarm Agent, then
    sliced to (offset, limit) — so the heavy per-topic trajectory build runs at most
    once per cache window instead of on every load (was ~6s/2MB uncached on the 7d
    view), and the web can page 100 at a time instead of pulling 2MB at once.
    Same shape, fields, and ordering as before; cache is read-only."""
    super_key = f"history_full:{window}:{points}"
    full = _cache.get(super_key)
    if full is None:
        full = _compute_history_full(window, points)
        _cache.set(super_key, full, CACHE_TTL_SCORES_FULL)
    page = full[offset: offset + limit]
    return {"window": window, "count": len(page), "total": len(full),
            "offset": offset, "limit": limit, "results": page}


@app.get("/history/{topic_key}/analysis")
def history_analysis(topic_key: str, topic: str = ""):
    """AI explanation of WHY a topic's score has been moving — grounded in its real
    recent trajectory + the actual coverage driving it. Measurement, not advice.
    Cached (in-memory) + capped by the monthly AI budget; generated on demand."""
    ck = f"histanalysis:{topic_key}"
    cached = _cache.get(ck)
    if cached is not None:
        return cached
    if not _AI_GRADE_AVAILABLE:
        return {"available": False, "reason": "AI analysis unavailable"}
    if not _ai_budget_ok():
        return {"available": False, "reason": "monthly AI budget reached", "budget": AI_MONTHLY_BUDGET_USD}
    conn = None
    try:
        conn = get_db(DB_PATH)
        rows = conn.execute(
            "SELECT scored_at, detection_score, confidence_score FROM velocity_scores "
            "WHERE topic_key = ? ORDER BY scored_at DESC LIMIT 14", (topic_key,)).fetchall()
    finally:
        if conn is not None:
            try: conn.close()
            except Exception: pass
    if not rows or len(rows) < 2:
        return {"available": False, "reason": "not enough history yet"}
    series = list(reversed([dict(r) for r in rows]))
    d0, d1 = round(series[0]["detection_score"] or 0), round(series[-1]["detection_score"] or 0)
    c0, c1 = round(series[0]["confidence_score"] or 0), round(series[-1]["confidence_score"] or 0)
    direction = "rising" if (d1 - d0) >= 3 else "falling" if (d1 - d0) <= -3 else "flat"
    movement = (f"Detection {d0} to {d1}, Confidence {c0} to {c1} over the last "
                f"{len(series)} scoring cycles")
    name = (topic or topic_key.replace("_", " ")).strip()
    ctx = _topic_source_context(topic_key)
    res = ai_grade.analyze_movement(name, movement, direction, context=ctx)
    if res.get("available") and res.get("short"):
        _record_ai_cost("history_analysis", name, res.get("cost") or {})
        out = {"available": True, "direction": direction, "movement": movement,
               "short": res["short"], "full": res.get("full", ""),
               "citations": res.get("citations", [])}
        _cache.set(ck, out, int(os.getenv("HISTORY_ANALYSIS_TTL", "21600")))
        return out
    # Never surface a raw provider error (e.g. "401 ... api.perplexity.ai") to the UI —
    # log it, return a clean, user-safe reason.
    if res.get("error"):
        print(f"[history-analysis] {name}: {res.get('error')}")
    return {"available": False, "reason": "Driving-factor analysis is temporarily unavailable."}


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

    # Get all scoring cycles (newest first) — include all fields needed for calibration
    history = conn.execute("""
        SELECT scored_at, overall_score, detection_score, confidence_score,
               persistence_score, gradient_strength, inertia_score,
               platform_diversity, dark_matter_score, confidence_decay,
               heisenberg_gap, signal_stage, is_gravitational_anomaly,
               topic_key, topic_display, total_mentions, platforms_active
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

    # Apply the same calibration pipeline used by /scores so history scores
    # match what the user sees on the main dashboard (raw DB values differ
    # from served values because calibration is applied at serve time).
    def _calibrate_history_row(h: dict) -> dict:
        try:
            # Parse platforms_active for signal count modifier
            pa = h.get("platforms_active")
            if isinstance(pa, str):
                try:
                    h["platforms_active"] = json.loads(pa or "[]")
                except Exception:
                    h["platforms_active"] = []

            # 1. Maturity-aware score multiplier
            if _CAL_AVAILABLE:
                try:
                    h = apply_calibration(h)
                except Exception:
                    pass

            # 2. AI tier-aware score overrides
            if _AI_INTEL_AVAILABLE:
                try:
                    if not h.get("times_scored"):
                        cal = h.get("calibration", {})
                        if isinstance(cal, dict):
                            h["times_scored"] = cal.get("times_scored", 0) or 0
                    if not h.get("platform_count"):
                        plat = h.get("platforms_active", [])
                        h["platform_count"] = len(plat) if isinstance(plat, list) else 1
                    h = _apply_ai_intelligence(h)
                except Exception:
                    pass

            # 3. AI minimum score floor
            if _CORRECTIONS_AVAILABLE:
                try:
                    new_det, new_conf, floored = apply_ai_floor(
                        h.get("topic_display", ""),
                        h.get("detection_score", 0) or 0,
                        h.get("confidence_score", 0) or 0,
                        h.get("total_mentions", 0) or 0,
                    )
                    if floored:
                        h["detection_score"]  = new_det
                        h["confidence_score"] = new_conf
                        h["heisenberg_gap"]   = round(new_det - new_conf, 1)
                except Exception:
                    pass

            # Recompute gap after all adjustments — SIGNED (Detection - Confidence),
            # never abs(): the sign IS the signal (positive = detected early/ahead of
            # confirmation; negative = lagging). abs() here previously stomped the
            # correct signed value set above and inverted the gap's meaning.
            det  = h.get("detection_score",  0) or 0
            conf = h.get("confidence_score", 0) or 0
            h["heisenberg_gap"] = round(det - conf, 1)

        except Exception:
            pass
        return h

    calibrated_history = [_calibrate_history_row(dict(h)) for h in history]

    result = {
        "topic_key":   topic_key,
        "topic":       latest["topic_display"] if latest else topic_key.replace("_", " "),
        "lifecycle":   dict(lc) if lc else None,
        "cycle_count": len(calibrated_history),
        "history":     calibrated_history,
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
        if not _is_quality_topic(s.get("topic_display", "")):
            continue   # drop profanity / bare-generic junk
        s["gap_label"]  = _gap_label(s["heisenberg_gap"])
        s["is_anomaly"] = bool(s.get("is_gravitational_anomaly"))
        s["category"]   = _category_for(s.get("topic_key", ""), s.get("topic_display", ""))
        results.append(s)

    result = {"count": len(results), "results": results}
    # Log each trending topic as a query event for the N component
    for item in results:
        if item.get("topic_key"):
            _log_topic_query(item["topic_key"], "/trending")
    _cache.set(cache_key, result, CACHE_TTL_SCORES)
    return result


def _compute_topics_full(cat: str, anomalies_only: bool) -> list:
    """The full quality+category-filtered topic grid, computed once and cached so
    /topics pagination is O(1) slicing (web loads the whole grid 100 at a time)."""
    conn = get_db(DB_PATH)
    filter_str = "AND r.is_anomaly = 1" if anomalies_only else ""
    # Wide candidate scan before the quality + category filters so quality topics
    # still surface even when the top-by-score rows are junk.
    scan = 2000
    rows = conn.execute(f"""
        SELECT r.topic_key, r.topic_display, r.current_stage,
               r.total_mentions, r.is_anomaly, r.last_seen_at,
               v.overall_score, v.detection_score, v.confidence_score,
               v.nowtrendin_score, v.signal_stage, v.serve_payload
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
    """, (scan,)).fetchall()
    conn.close()
    topics = []
    for r in rows:
        d = dict(r)
        if not _is_quality_topic(d.get("topic_display", "")):
            continue   # drop profanity / bare-generic junk from the institutional grid
        # SINGLE SOURCE OF TRUTH: the grid must show the SAME detection/confidence
        # the /scores feed serves. Override raw v.* with the precomputed
        # serve_payload when present (top-N); long-tail keeps the stored value.
        _pl = d.pop("serve_payload", None)
        if _pl:
            try:
                _p = json.loads(_pl)
                for _k in ("overall_score", "detection_score", "confidence_score",
                           "nowtrendin_score", "signal_stage"):
                    if _p.get(_k) is not None:
                        d[_k] = _p[_k]
            except Exception:
                pass
        d["category"] = _category_for(d.get("topic_key", ""), d.get("topic_display", ""))
        if cat and d["category"] != cat:
            continue
        topics.append(d)
    return topics


@app.get("/topics")
def list_topics(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    anomalies_only: bool = Query(False),
    category: str = Query("", description="Filter by content category, e.g. sports, technology"),
):
    """
    List discovered topics with their latest scores — PAGINATED.
    The full quality-filtered grid is computed once and cached; `limit` + `offset`
    return an O(1) slice so the web can load the whole grid 100 at a time with no
    cap and no delay. Response includes `total`. Pass ?category= to scope a chip.
    """
    cat = category.strip().lower()
    super_key = f"topics_full:{cat}:{int(anomalies_only)}"
    full = _cache.get(super_key)
    if full is None:
        full = _compute_topics_full(cat, anomalies_only)
        _cache.set(super_key, full, CACHE_TTL_SCORES_FULL)
    total = len(full)
    page = full[offset: offset + limit]
    return {"count": len(page), "topics": page, "category": cat or "all",
            "total": total, "offset": offset, "limit": limit}


@app.get("/categories")
def list_categories():
    """
    Canonical content categories (Now TrendIn 1.0 taxonomy) with live topic
    counts, for building the category chip row + customization UI. Counts are
    over the most recently scored topics (classified at serve-time).
    """
    cached = _cache.get("categories")
    if cached is not None:
        return cached
    from collections import Counter
    conn = get_db(DB_PATH)
    rows = conn.execute("""
        SELECT r.topic_key, r.topic_display
        FROM topic_registry r
        LEFT JOIN (
            SELECT topic_key, MAX(scored_at) as max_at
            FROM velocity_scores GROUP BY topic_key
        ) latest ON r.topic_key = latest.topic_key
        LEFT JOIN velocity_scores v
            ON v.topic_key = latest.topic_key AND v.scored_at = latest.max_at
        ORDER BY v.overall_score DESC NULLS LAST
        LIMIT 2000
    """).fetchall()
    conn.close()
    counts = Counter(_category_for(r["topic_key"], r["topic_display"]) for r in rows
                     if _is_quality_topic(r["topic_display"]))
    cats = []
    try:
        from topic_categories import CATEGORIES, CATEGORY_LABELS
        ordered = CATEGORIES + ["news", "general"]
        seen = set()
        for k in ordered:
            if k in seen:
                continue
            seen.add(k)
            cats.append({"key": k, "label": CATEGORY_LABELS.get(k, k.title()),
                         "count": counts.get(k, 0)})
    except Exception:
        cats = [{"key": k, "label": k.title(), "count": n} for k, n in counts.most_common()]
    result = {"categories": cats, "total_classified": sum(counts.values())}
    _cache.set("categories", result, CACHE_TTL_SCORES)
    return result


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
        "discovery_collectors_active": _DISCOVERY_AVAILABLE,
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

# Internal-demand (N) weighting for the SEPARATE "Now Trending Gradient Score".
# TRADE SECRET — kept server-side, never serialized as a breakdown to clients.
# The DEFAULT Detection/Confidence deliberately EXCLUDE N (external-world only,
# no demand feedback loop). This alternate pair folds N in as an extra factor:
#   score_with_n = score * (1 - w_N) + N * w_N
# which is the proper renormalized blend (the base score already sums to 1.0).
_N_DET_WEIGHT  = float(os.getenv("N_DET_WEIGHT", "0.12"))
_N_CONF_WEIGHT = float(os.getenv("N_CONF_WEIGHT", "0.10"))
# External-evidence count at which N earns its FULL weight. Below this, N's
# weight scales down linearly toward 0 so a topic with little/no external
# footprint cannot be lifted by internal demand alone (thin-data reflexivity
# guard — a fixed % of a near-zero base would otherwise be dominated by N).
_N_SUFFICIENCY_FULL = float(os.getenv("N_SUFFICIENCY_FULL", "30"))


def _now_trending_gradient(detection, confidence, n_val, total_mentions=None):
    """Demand-inclusive 'Now Trending Gradient Score'. N's weight is scaled DOWN
    when external evidence is thin, so internal demand cannot inflate a topic with
    little external footprint. Returns (det_with_n, conf_with_n, demand_driven) —
    (None, None, False) on bad input. `demand_driven` flags a thin-evidence topic
    where demand exceeds the external read (show a transparency note)."""
    if n_val is None or detection is None or confidence is None:
        return None, None, False
    try:
        n = max(0.0, min(100.0, float(n_val)))
        det = max(0.0, min(100.0, float(detection)))
        conf = max(0.0, min(100.0, float(confidence)))
        # External-evidence sufficiency 0..1 (full once a topic carries enough
        # independent external mentions; →0 for thin data).
        suff = max(0.0, min(1.0, float(total_mentions or 0) / _N_SUFFICIENCY_FULL))
        wd, wc = _N_DET_WEIGHT * suff, _N_CONF_WEIGHT * suff
        demand_driven = suff < 0.5 and n > det
        return (round(det * (1 - wd) + n * wd, 1),
                round(conf * (1 - wc) + n * wc, 1),
                demand_driven)
    except Exception:
        return None, None, False


def _calibrate_score_fields(s: dict) -> dict:
    """Apply the full serve-time calibration pipeline to one score row dict:
    calibration → AI taxonomy → AI floor → 0-100 clamp. Used for both the
    headline /scores rows and per-cycle scoring history so they stay consistent."""
    s["heisenberg_gap"] = round(
        (s.get("detection_score") or 0) - (s.get("confidence_score") or 0), 1
    )
    s["gap_label"]    = _gap_label(s["heisenberg_gap"])
    s["is_anomaly"]   = bool(s.get("is_gravitational_anomaly"))

    # ── Re-apply calibration at serve time ────────────────────
    if _CAL_AVAILABLE:
        try:
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
            # OBSERVABLE swallow (C8): the module IS present (guarded above), so a raise
            # here is a real runtime failure that would otherwise serve a RAW, uncalibrated
            # row indistinguishable from a calibrated one. Log it + stamp a machine-readable
            # marker so /scores and the monitoring agents can DETECT the downgrade.
            print(f"[serve-cal] apply_calibration failed topic={s.get('topic_key')}: {_ce}")
            s.setdefault("calibration_errors", []).append("apply_calibration")
            cal = s.get("calibration")
            s["calibration"] = {**cal, "applied": False, "error": str(_ce)[:160]} if isinstance(cal, dict) \
                else {"applied": False, "error": str(_ce)[:160]}

    # ── AI Topic Intelligence — tier-aware taxonomy scoring ────
    if _AI_INTEL_AVAILABLE:
        try:
            if not s.get("times_scored"):
                cal = s.get("calibration", {})
                if isinstance(cal, dict):
                    s["times_scored"] = cal.get("times_scored", 0) or 0
            if not s.get("platform_count"):
                plat = s.get("platforms_active", [])
                s["platform_count"] = len(plat) if isinstance(plat, list) else 1
            s = _apply_ai_intelligence(s)
        except Exception as _ie:
            print(f"[serve-cal] ai_intelligence failed topic={s.get('topic_key')}: {_ie}")
            s.setdefault("calibration_errors", []).append("ai_intelligence")

    # ── AI score floor ────────────────────────────────────────
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
                s["heisenberg_gap"] = round(new_det - new_conf, 1)
        except Exception as _fe:
            print(f"[serve-cal] ai_floor failed topic={s.get('topic_key')}: {_fe}")
            s.setdefault("calibration_errors", []).append("ai_floor")

    # Clamp 0-100 fields so calibration can't surface an impossible value.
    for _f in ("gradient_strength", "platform_diversity", "inertia_score",
               "dark_matter_score", "confidence_decay", "persistence_score",
               "detection_score", "confidence_score", "overall_score"):
        if s.get(_f) is not None:
            try:
                s[_f] = max(0.0, min(100.0, float(s[_f])))
            except Exception:
                pass

    # Separate "Now Trending Gradient Score" — demand-inclusive what-if read.
    # Computed from the FINAL (post-floor, post-clamp) Detection/Confidence so it
    # stays consistent with the served headline scores. Only the resulting numbers
    # are serialized — the N weighting itself is never exposed.
    _ntd, _ntc, _ndd = _now_trending_gradient(
        s.get("detection_score"), s.get("confidence_score"),
        s.get("nowtrendin_score"), s.get("total_mentions"))
    if _ntd is not None:
        s["nowtrending_gradient_detection"]  = _ntd
        s["nowtrending_gradient_confidence"] = _ntc
        s["nowtrending_gradient_demand_driven"] = _ndd

    # FINAL gap recompute — the ONE authoritative source (invariant: stored
    # heisenberg_gap == served Detection - Confidence, SIGNED). apply_calibration +
    # AI-taxonomy can move det/conf WITHOUT the AI floor firing, which left the gap
    # set from the RAW scores at the top of this function stale (e.g. mcp served
    # det 74.5 / conf 73.0 but gap -23). Recomputing here, after the 0-100 clamp,
    # guarantees /scores, /scores/{key}, serve_payload, and score-history all agree.
    s["heisenberg_gap"] = round(
        (s.get("detection_score") or 0) - (s.get("confidence_score") or 0), 1
    )
    s["gap_label"] = _gap_label(s["heisenberg_gap"])
    return s


def _format_score_rows(rows) -> dict:
    results = []
    for r in rows:
        s = dict(r)
        # Fast path: the worker precomputes the fully-calibrated serve row into
        # serve_payload each cycle (see _precompute_serve_payloads). Reading it
        # back is a cheap json.loads instead of re-running the per-row
        # calibration + AI pipeline (which made cold /scores 6–11s).
        payload = s.get("serve_payload")
        if payload:
            try:
                p = json.loads(payload)
                # The precomputed payload omits first_scored_at (added later for
                # tier data-aging). Inject the true first-seen from the joined row
                # so Consumer/Business tiers age in correctly — without it the
                # fast path returned None and every topic looked "fresh", locking
                # lower tiers out of all data.
                fsa = s.get("first_scored_at")
                if fsa:
                    p["first_scored_at"] = fsa
                results.append(p)
                continue
            except Exception:
                pass  # corrupt/absent → fall through to live calibration
        s = _parse_json_fields(s)
        s = _calibrate_score_fields(s)
        results.append(s)

    # Inject content category + quality filter on EVERY served row. The /scores
    # list powers the mobile feed, so the content-category chips and the
    # profanity/junk cleanup must apply here too (consistent with /topics).
    cleaned = []
    for s in results:
        disp = s.get("topic_display") or s.get("topic") or ""
        if not _is_quality_topic(disp):
            continue
        if not s.get("category"):
            s["category"] = _category_for(s.get("topic_key", ""), disp)
        cleaned.append(s)
    results = cleaned

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
                if is_meaningful_topic(topic, sigs, sources) and not _is_generic_topic(topic):
                    filtered.append(s)
                else:
                    pass  # silently drop noise bigrams + generic evergreen topics
            results = filtered
        except Exception:
            pass  # non-fatal — serve unfiltered on error

    return {"count": len(results), "results": results}


def _precompute_serve_payloads(top_n: int = 600) -> int:
    """Precompute the fully-calibrated /scores row for the top `top_n` latest
    topics and store it in velocity_scores.serve_payload as JSON.

    Run once per worker cycle. The /scores serve path then reads serve_payload
    directly (cheap json.loads) instead of recalibrating 160–200 candidate rows
    per request, which is what made cold /scores 6–11s. Long-tail topics without
    a payload fall back to live calibration in _format_score_rows.

    First clears ALL existing payloads so none can go stale: topics that drop out
    of the top-N (e.g. AI-taxonomy topics that rank high on display but low on raw
    score) would otherwise keep an old cached payload forever. Cleared rows simply
    fall back to live calibration until the next cycle refreshes them.
    """
    pconn = get_db(DB_PATH)
    try:
        pconn.execute("UPDATE velocity_scores SET serve_payload = NULL WHERE serve_payload IS NOT NULL")
        pconn.commit()
    finally:
        pconn.close()
    conn = get_db(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT v.* FROM velocity_scores v
            INNER JOIN (
                SELECT topic_key, MAX(scored_at) AS m
                FROM velocity_scores GROUP BY topic_key
            ) l ON v.topic_key = l.topic_key AND v.scored_at = l.m
            ORDER BY (CASE WHEN v.overall_score >= v.detection_score
                           THEN v.overall_score ELSE v.detection_score END) DESC
            LIMIT ?
            """,
            (top_n,),
        ).fetchall()
    finally:
        conn.close()

    updates = []
    for r in rows:
        s = _parse_json_fields(dict(r))
        s.pop("serve_payload", None)  # don't nest the column inside its own payload
        try:
            s = _calibrate_score_fields(s)
            updates.append((json.dumps(s, default=str), r["topic_key"], r["scored_at"]))
        except Exception:
            continue

    if not updates:
        return 0
    w = get_db(DB_PATH)
    try:
        w.executemany(
            "UPDATE velocity_scores SET serve_payload = ? WHERE topic_key = ? AND scored_at = ?",
            updates,
        )
        w.commit()
    finally:
        w.close()
    print(f"[precompute] serve_payload written for {len(updates)} topics")
    return len(updates)


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
        return ("Heavily concentrated in expert/niche communities, with limited "
                "mainstream pickup in the sources we track so far.")
    elif score >= 55:
        return "Primarily specialist communities with some mainstream presence."
    else:
        return "Meaningful mainstream presence — niche/mainstream gradient is flattening."


def _explain_i(score: float) -> str:
    if score >= 70:
        return ("Acceleration confirmed across 3+ consecutive 6-hour windows. "
                "This is self-reinforcing momentum, not a spike.")
    elif score >= 40:
        return "Moderate acceleration. 1–2 windows confirmed. Building but not yet proven."
    else:
        return ("Inertia not confirmed. Could be a single-event spike. "
                "More collection cycles needed before the trend is confirmed.")


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
        choices=["collect", "score", "full", "api", "archive", "risk", "validate", "worker"],
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

    elif args.mode == "archive":
        run_retention()

    elif args.mode == "risk":
        if _RISK_AVAILABLE:
            risk.run_risk_collection(DB_PATH)
            risk.score_all_risks(DB_PATH)
        else:
            print("Risk module unavailable")

    elif args.mode == "validate":
        if _ACCURACY_AVAILABLE:
            print(accuracy.validate_recent_detections(DB_PATH))
            print(accuracy.generate_accuracy_report(DB_PATH))
        else:
            print("Accuracy module unavailable")

    elif args.mode == "worker":
        # Dedicated worker dyno: runs ONLY the scheduler (collect/score/scan),
        # so the web dyno stays free to serve requests. No HTTP server here.
        import time as _time
        print("\nNow TrendIn — Scheduler Worker")
        # Ensure calibration tables exist (web dyno normally seeds them, but the
        # worker may boot first).
        if _CAL_AVAILABLE:
            try:
                _init_cal_db(DB_PATH)
                seed_known_topics(DB_PATH)
                print("[worker] Calibration DB initialised.")
            except Exception as _wexc:
                print(f"[worker] calibration init error (non-fatal): {_wexc}")
        sched = start_scheduler()
        if sched is None:
            print("[worker] Scheduler failed to start — exiting.")
            return
        print("[worker] Scheduler running. Jobs: collect+score 30m · velocities 06:00 UTC · "
              "X scan 1am/1pm PT · retention monthly.")
        try:
            while True:
                _time.sleep(3600)
        except (KeyboardInterrupt, SystemExit):
            print("[worker] shutting down scheduler.")
            sched.shutdown(wait=False)

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
