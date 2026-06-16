"""
================================================================
NOW TRENDIN — MONITORING AGENTS  (DATA_BUILDING_BLOCKS.md)
================================================================

Automated checks for the two recurring failure classes:
  A. data not pulling      → source_watchdog()      (blocks B1, B2)
  B. scores wrong/absent   → pipeline_integrity()   (blocks B3, B4, B8)

Each agent returns a typed report:
  {agent, status: ok|warn|critical, alerts: [{level, block, ...}], summary}

Pure read-only. No external calls, no AI, no writes — safe to run every cycle or
on demand via /monitor. Grounded in the live engine: reads collector_health +
velocity_scores, and reuses the engine's own quality/canonical functions so the
checks match exactly what the pipeline does.
================================================================
"""

from datetime import datetime, timezone

try:
    import collector_health
except Exception:                       # degrade gracefully if absent
    collector_health = None


def _now():
    return datetime.now(timezone.utc)


def _mins_since(iso_str):
    if not iso_str:
        return None
    try:
        s = str(iso_str).replace("Z", "+00:00")
        d = datetime.fromisoformat(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return (_now() - d).total_seconds() / 60.0
    except Exception:
        return None


# Sources intentionally OFF (licensing) — DEGRADED/0-signal is expected, not an
# alert. Mirrors collector_health's sentinel window for reddit.
_OFF_SOURCES = {"reddit"}


def _roll_up(alerts):
    if any(a["level"] == "critical" for a in alerts):
        return "critical"
    if any(a["level"] == "warn" for a in alerts):
        return "warn"
    return "ok"


# ── Agent A: SOURCE WATCHDOG (B1 registry/SLA, B2 collection health) ─────────
def source_watchdog(conn=None, db_path=None) -> dict:
    """Are sources pulling within their SLA? Critical-down = scores half-blind."""
    if collector_health is None:
        return {"agent": "source_watchdog", "status": "warn",
                "alerts": [{"level": "warn", "block": "B2",
                            "msg": "collector_health module unavailable"}],
                "summary": {}}
    rep = collector_health.get_health_report(conn=conn) if conn is not None \
        else collector_health.get_health_report(db_path=db_path or collector_health.DB_PATH)
    cols = rep.get("collectors", {})
    alerts = []
    for name, c in cols.items():
        if name in _OFF_SOURCES:        # intentionally off — never alert
            continue
        st, crit, detail = c.get("status"), c.get("critical"), c.get("detail", "")
        if st == "DOWN" and crit:
            alerts.append({"level": "critical", "block": "B2", "source": name,
                           "msg": f"CRITICAL collector DOWN — {detail}"})
        elif st == "DOWN":
            alerts.append({"level": "warn", "block": "B2", "source": name,
                           "msg": f"DOWN — {detail}"})
        elif st == "STALE":
            lvl = "critical" if crit else "warn"
            alerts.append({"level": lvl, "block": "B2", "source": name,
                           "msg": f"STALE — {detail}"})
        elif st == "DEGRADED":
            alerts.append({"level": "warn", "block": "B2", "source": name,
                           "msg": f"DEGRADED (ran, 0 signals) — {detail}"})
    return {
        "agent": "source_watchdog",
        "status": _roll_up(alerts),
        "alerts": alerts,
        "summary": rep.get("summary", {}),
        "critical_problems": rep.get("critical_problems", []),
        "checked_at": _now().isoformat(),
    }


# ── Agent B: PIPELINE INTEGRITY MONITOR (B3 extraction, B4 scoring, B8 serve) ─
def pipeline_integrity(conn, sample: int = 300) -> dict:
    """Did scoring run, are topics clean (no junk/dupes), are serve fields present?
    Reuses the engine's own _is_quality_topic / _topic_key so the check matches
    the pipeline exactly. `conn` is required (engine passes get_db(DB_PATH))."""
    import gravitational_anomaly_detector as g   # lazy → avoids circular import
    alerts = []
    summary = {}

    # B4 — scoring freshness: latest score must be within ~1 cycle + margin.
    try:
        row = conn.execute("SELECT MAX(scored_at) m FROM velocity_scores").fetchone()
        age = _mins_since(row["m"] if row else None)
        summary["last_score_min_ago"] = round(age, 1) if age is not None else None
        if age is None:
            alerts.append({"level": "critical", "block": "B4",
                           "msg": "no scores found — scoring has never run"})
        elif age > 720:                  # > 12h = ~2 missed cycles
            alerts.append({"level": "critical", "block": "B4",
                           "msg": f"scores stale {int(age)}m (>12h) — score cycle stalled"})
        elif age > 440:                  # > 7h+ = 1 missed 6h cycle
            alerts.append({"level": "warn", "block": "B4",
                           "msg": f"scores stale {int(age)}m (>7h) — a cycle may have been missed"})
    except Exception as e:
        alerts.append({"level": "warn", "block": "B4", "msg": f"freshness check failed: {e}"})

    # Pull the latest row per topic (top by score) for the integrity sample.
    rows = []
    try:
        # NOTE: `category` is injected at serve-time (_format_score_rows), NOT a
        # velocity_scores column — so we audit detection_pathway (a real stored
        # audit field) for serve-readiness instead.
        rows = conn.execute(
            """
            SELECT v.topic_key, v.topic_display, v.detection_pathway,
                   v.scored_at, v.overall_score, v.detection_score
            FROM velocity_scores v
            INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores
                        GROUP BY topic_key) l
              ON v.topic_key = l.topic_key AND v.scored_at = l.m
            ORDER BY (CASE WHEN v.overall_score >= v.detection_score
                           THEN v.overall_score ELSE v.detection_score END) DESC
            LIMIT ?
            """, (sample,)).fetchall()
    except Exception as e:
        alerts.append({"level": "warn", "block": "B4", "msg": f"sample query failed: {e}"})
    summary["sampled"] = len(rows)

    # B3 — extraction integrity: no junk common-words, no canonical duplicates.
    # Split SINGLE-word junk (high-confidence real junk, e.g. "destroyed") from
    # MULTI-word (lower confidence — the lowercase filter can't tell a proper-noun
    # name like "Michael Chandler" from generic phrasing). Only single-word junk
    # raises the alert; multi-word is surfaced as review-only. These rows are
    # filtered at SERVE (users don't see them) but are scored+stored — the alert
    # means the quality gate should also run at scoring / old rows pruned.
    junk_single, junk_multi, canon_map = [], [], {}
    for r in rows:
        disp = r["topic_display"] or r["topic_key"] or ""
        try:
            if not g._is_quality_topic(disp):
                (junk_single if len(disp.split()) == 1 else junk_multi).append(disp)
        except Exception:
            pass
        try:
            ck = g._topic_key((r["topic_key"] or "").replace("_", " "))
            canon_map.setdefault(ck, set()).add(r["topic_key"])
        except Exception:
            pass
    dupes = {k: sorted(v) for k, v in canon_map.items() if len(v) > 1}
    summary["junk_single"] = len(junk_single)
    summary["junk_multiword_review"] = len(junk_multi)
    summary["dupe_groups"] = len(dupes)
    if junk_single:
        alerts.append({"level": "warn", "block": "B3",
                       "msg": f"{len(junk_single)} single common-word topics scored+stored "
                              f"(filtered at serve) — apply quality gate at scoring/prune: {junk_single[:5]}"})
    if dupes:
        ex = list(dupes.values())[:3]
        alerts.append({"level": "warn", "block": "B3",
                       "msg": f"{len(dupes)} unconsolidated duplicate groups (e.g. {ex})"})

    # B8 — serve consistency: scored rows carry the dual-pathway audit field, so
    # every client renders the same enriched data (category is added at serve).
    if rows:
        no_path = sum(1 for r in rows if not r["detection_pathway"])
        summary["missing_pathway"] = no_path
        if no_path > len(rows) * 0.5:
            alerts.append({"level": "warn", "block": "B8",
                           "msg": f"{no_path}/{len(rows)} scored rows missing detection_pathway "
                                  "(audit field) — re-score may be needed"})

    return {
        "agent": "pipeline_integrity",
        "status": _roll_up(alerts),
        "alerts": alerts,
        "summary": summary,
        "checked_at": _now().isoformat(),
    }


# ── Agent D: COST SENTINEL (B7 budgets) — TOTAL cost of running Now TrendIn ──
# LIVE-metered: AI (Perplexity+Anthropic) + Apify (platform usage, via API).
# CONFIGURED (env, set to your actuals — not API-readable in real time):
#   COST_HEROKU_USD          monthly Heroku dynos (engine standard-2x $50 + backend
#                            $7 + nowtrendin-web $7 ≈ $64; terminal is Pages=$0)
#   COST_SUBSCRIPTIONS_USD   paid data APIs (NewsAPI ×2, NewsData, Finnhub,
#                            WhaleWisdom, Alpha Vantage, X) — set your monthly total
#   COST_GITHUB_USD          GitHub (Pages/Actions) — $0 on public repo
#   COST_TOTAL_MONTHLY_CAP   optional grand cap to alert on
def cost_sentinel() -> dict:
    import os
    import requests
    import gravitational_anomaly_detector as g
    alerts, lines = [], []
    total = 0.0

    # 1) AI — LIVE ($/mo vs the $20 cap)
    try:
        mtd = g._ai_spend_this_month()
        ai_budget = g.AI_MONTHLY_BUDGET_USD
        ai_spent = float(mtd.get("total", 0.0) or 0)
        total += ai_spent
        lines.append({"item": "AI (Perplexity+Anthropic)", "usd": round(ai_spent, 2),
                      "budget": ai_budget, "source": "live"})
        if ai_budget and ai_spent >= ai_budget:
            alerts.append({"level": "critical", "block": "B7",
                           "msg": f"AI budget EXHAUSTED ${ai_spent:.2f}/${ai_budget:.0f} — paid AI calls skipped"})
        elif ai_budget and ai_spent / ai_budget >= 0.8:
            alerts.append({"level": "warn", "block": "B7",
                           "msg": f"AI spend at {ai_spent / ai_budget * 100:.0f}% of ${ai_budget:.0f}/mo"})
    except Exception as e:
        alerts.append({"level": "warn", "block": "B7", "msg": f"AI cost read failed: {e}"})

    # 2) Apify — LIVE (platform monthly usage vs the custom limit) via API
    tok = os.getenv("APIFY_TOKEN")
    if tok:
        try:
            r = requests.get(f"https://api.apify.com/v2/users/me/limits?token={tok}", timeout=12)
            data = (r.json() or {}).get("data", {})
            used = data.get("current", {}).get("monthlyUsageUsd")
            cap = data.get("limits", {}).get("maxMonthlyUsageUsd")
            if used is not None:
                used = float(used); total += used
                lines.append({"item": "Apify (Google-Trends actor)", "usd": round(used, 2),
                              "budget": cap, "source": "live"})
                if cap and used >= cap:
                    alerts.append({"level": "critical", "block": "B7",
                                   "msg": f"Apify usage EXHAUSTED ${used:.2f}/${cap:.0f} — platform will pause"})
                elif cap and used / cap >= 0.8:
                    alerts.append({"level": "warn", "block": "B7",
                                   "msg": f"Apify usage at {used / cap * 100:.0f}% of ${cap:.0f}/mo"})
        except Exception as e:
            alerts.append({"level": "warn", "block": "B7", "msg": f"Apify billing read failed: {e}"})

    # 3) Fixed infra — CONFIGURED (env, set to your actuals)
    # Data-API subscriptions are now ITEMIZED per provider (data_subscriptions);
    # prefer that sum, but honour a legacy lump COST_SUBSCRIPTIONS_USD if the
    # per-provider vars aren't set yet.
    subs_itemized = data_subscriptions_total()
    subs_legacy = float(os.getenv("COST_SUBSCRIPTIONS_USD", "0") or 0)
    subs_usd = subs_itemized if subs_itemized > 0 else subs_legacy
    fixed = [
        ("Heroku dynos", float(os.getenv("COST_HEROKU_USD", "64"))),
        # X (Twitter) Developer API monthly subscription — distinct from the post
        # BUDGET below (posts are the in-plan cap; this is the plan's $ fee).
        # X Basic = $200/mo; migrating to Pay-Per-Use 2026-06-21 — update then.
        ("X Developer API", float(os.getenv("COST_X_API_USD", "200"))),
        ("AWS", float(os.getenv("COST_AWS_USD", "104"))),
        ("Data API subscriptions", subs_usd),
        ("GitHub (Pages/Actions)", float(os.getenv("COST_GITHUB_USD", "0"))),
    ]
    for name, usd in fixed:
        total += usd
        src = "itemized" if (name == "Data API subscriptions" and subs_itemized > 0) else "configured"
        lines.append({"item": name, "usd": round(usd, 2), "source": src})

    # 4) X posts — operational budget (posts, not $)
    x_line = {}
    try:
        xs = g._x_posts_spent_this_month(); xb = g._X_MONTHLY_POST_BUDGET
        x_line = {"posts": xs, "budget": xb, "pct": round(xs / xb * 100, 1) if xb else 0}
        if xb and xs >= xb:
            alerts.append({"level": "critical", "block": "B7", "msg": f"X post budget EXHAUSTED {xs}/{xb}"})
        elif xb and xs / xb >= 0.8:
            alerts.append({"level": "warn", "block": "B7", "msg": f"X posts at {xs / xb * 100:.0f}% of {xb}/mo"})
    except Exception:
        pass

    grand_cap = float(os.getenv("COST_TOTAL_MONTHLY_CAP", "0") or 0)
    if grand_cap and total >= grand_cap:
        alerts.append({"level": "critical", "block": "B7",
                       "msg": f"TOTAL monthly cost ${total:.2f} ≥ cap ${grand_cap:.0f}"})

    summary = {
        "total_monthly_usd": round(total, 2),
        "total_cap_usd": grand_cap or None,
        "lines": lines,
        "x_posts": x_line,
        "note": "AI + Apify are live-metered; Heroku/subscriptions/GitHub are env-configured "
                "(set COST_HEROKU_USD / COST_SUBSCRIPTIONS_USD / COST_GITHUB_USD / COST_TOTAL_MONTHLY_CAP).",
    }
    return {"agent": "cost_sentinel", "status": _roll_up(alerts),
            "alerts": alerts, "summary": summary, "checked_at": _now().isoformat()}


# ── Agent C: CALIBRATION AUDITOR (B5 accuracy honesty) ──────────────────────
def calibration_auditor() -> dict:
    """Is the Accuracy Ledger honest + denominator-backed? Flags small-sample so
    no one publishes a hit-rate we can't defend (guardrail 5). (Backtest-before-
    ship is a deploy gate, run separately — not a runtime poll.)"""
    import gravitational_anomaly_detector as g
    alerts, summary = [], {}
    led = {}
    try:
        if getattr(g, "_LEDGER_PLUS_AVAILABLE", False):
            led = g.ledger_plus.generate_honest_report(g.DB_PATH) or {}
    except Exception as e:
        alerts.append({"level": "warn", "block": "B5", "msg": f"ledger read failed: {e}"})
    total = led.get("total", 0) or 0
    pending = led.get("pending", 0) or 0
    hit = led.get("hitRate")
    small = bool(led.get("smallSample")) or total < 30
    summary.update({"evaluated": total, "pending": pending,
                    "hit_rate": hit, "small_sample": small})
    if small:
        alerts.append({"level": "warn", "block": "B5",
                       "msg": f"Accuracy ledger small-sample (evaluated={total}, pending={pending}) "
                              "— do NOT publish a hit-rate yet (guardrail 5: denominator-backed only)"})
    return {"agent": "calibration_auditor", "status": _roll_up(alerts),
            "alerts": alerts, "summary": summary, "checked_at": _now().isoformat()}


# ── Agent G: TOPIC QUALITY AUDITOR (B3 deep) — fragments + geo/category sort ─
# Watches the failure modes that make category views messy + sources unclear:
#   (1) news-filler / multi-word headline fragments ("iran deal", "leaders meet")
#   (2) geo/country topics mis-sorted into Business/Economy (should be
#       current-events/politics) — the "iran deal → Business" bug class
#   (3) category clarity — too many topics in the catch-all "news"/"general"
# Reuses the engine's own NEWS_FILLER + _topic_category so the audit matches the
# live pipeline exactly.
_GEO_TERMS = {
    "iran", "israel", "gaza", "ukraine", "russia", "syria", "hamas", "hezbollah",
    "taiwan", "palestine", "lebanon", "yemen", "sudan", "venezuela",
    "north korea", "war", "ceasefire", "missile", "sanctions", "troops",
    "invasion", "hostage", "coup", "airstrike", "geopolitical", "nato",
}
_MISSORT_CATS = {"business", "economy"}


def fragment_category_auditor(conn, sample: int = 400) -> dict:
    import gravitational_anomaly_detector as g
    alerts, summary = [], {}
    rows = []
    try:
        rows = conn.execute(
            """
            SELECT v.topic_key, v.topic_display
            FROM velocity_scores v
            INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores
                        GROUP BY topic_key) l
              ON v.topic_key = l.topic_key AND v.scored_at = l.m
            ORDER BY (CASE WHEN v.overall_score >= v.detection_score
                           THEN v.overall_score ELSE v.detection_score END) DESC
            LIMIT ?
            """, (sample,)).fetchall()
    except Exception as e:
        return {"agent": "fragment_category_auditor", "status": "warn",
                "alerts": [{"level": "warn", "block": "B3", "msg": f"query failed: {e}"}],
                "summary": {}, "checked_at": _now().isoformat()}

    fragments, geo_missort, news_catch = [], [], 0
    nf = getattr(g, "NEWS_FILLER", set())
    for r in rows:
        disp = (r["topic_display"] or r["topic_key"] or "")
        toks = disp.lower().split()
        # (1) news-filler fragment — multi-word anchored by a filler token
        if len(toks) >= 2 and (toks[0] in nf or toks[-1] in nf):
            fragments.append(disp)
        # category (computed the same way serve does)
        try:
            cat = g._topic_category(disp) or ""
        except Exception:
            cat = ""
        if cat in ("news", "general", ""):
            news_catch += 1
        # (2) geo/country term but sorted into Business/Economy → likely mis-sort
        if cat in _MISSORT_CATS and any(t in _GEO_TERMS for t in toks):
            geo_missort.append(f"{disp} → {cat}")

    n = len(rows) or 1
    news_pct = round(news_catch / n * 100, 1)
    summary = {"sampled": len(rows), "fragments": len(fragments),
               "geo_missorted": len(geo_missort), "news_catchall_pct": news_pct}
    if fragments:
        alerts.append({"level": "warn", "block": "B3",
                       "msg": f"{len(fragments)} news-filler/multi-word fragments served "
                              f"(e.g. {fragments[:5]}) — tighten NEWS_FILLER / re-score"})
    if geo_missort:
        alerts.append({"level": "warn", "block": "B3",
                       "msg": f"{len(geo_missort)} geo/country topics mis-sorted to "
                              f"Business/Economy (e.g. {geo_missort[:5]}) — should be "
                              "current-events/politics"})
    if news_pct >= 70:
        alerts.append({"level": "warn", "block": "B3",
                       "msg": f"{news_pct}% of topics in the 'news'/general catch-all — "
                              "category sorting is thin; sources read unclear"})
    return {"agent": "fragment_category_auditor", "status": _roll_up(alerts),
            "alerts": alerts, "summary": summary, "checked_at": _now().isoformat()}


# ── Agent H: DATA SUBSCRIPTIONS (B7 — paid data-API spend & config) ─────────
# Investigates + monitors every external DATA API the engine integrates with.
# Each entry: (display, key_env, cost_env, billing_class, note). billing_class:
#   "paid"    — a paid subscription; contributes to the data-subscription total.
#             A cost_env of $0 while the key IS configured = UNTRACKED spend → warn.
#   "free"    — free / free-tier API (key present, $0 expected). Listed, not billed.
#   "metered" — usage-billed and tracked on its OWN cost line elsewhere
#             (AI ledger / Apify live / X line). Listed here for the full map,
#             NEVER added to the subs total (would double-count).
# We deliberately default every COST_*_USD to 0 — the engine must not assert a
# dollar figure it can't verify (integrity). The agent's job is to flag WHERE a
# real number is owed, not to invent one.
DATA_SUBSCRIPTIONS = [
    # paid data APIs (set the real monthly $ on each COST_*_USD)
    ("Alpha Vantage",        "ALPHAVANTAGE_API_KEY", "COST_ALPHAVANTAGE_USD", "paid",
     "market fundamentals (free tier exists — set $0 if on free)"),
    ("Finnhub",              "FINNHUB_API_KEY",      "COST_FINNHUB_USD",      "paid",
     "market/risk metrics (free tier exists — set $0 if on free)"),
    ("NewsAPI.ai",           "NEWSAPI_AI_KEY",       "COST_NEWSAPI_AI_USD",   "paid",
     "Event Registry news"),
    ("NewsAPI.org",          "NEWSAPI_ORG_KEY",      "COST_NEWSAPI_ORG_USD",  "paid",
     "news headlines (commercial use is paid)"),
    ("NewsData.io",          "NEWSDATA_IO_KEY",      "COST_NEWSDATA_IO_USD",  "paid",
     "news feed (free tier exists — set $0 if on free)"),
    ("RapidAPI (Yahoo Fin.)", "RAPIDAPI_YF_KEY",     "COST_RAPIDAPI_USD",     "paid",
     "Yahoo Finance via RapidAPI"),
    ("WhaleWisdom",          "WHALEWISDOM_SHARED_KEY", "COST_WHALEWISDOM_USD", "paid",
     "13F institutional holdings"),
    # free / free-tier data APIs (configured, $0 expected)
    ("FRED",                 "FRED_API_KEY",         None, "free", "Federal Reserve econ data (free)"),
    ("FINRA",                "FINRA_API_KEY",        None, "free", "FINRA short/market data (free)"),
    ("YouTube Data API",     "YOUTUBE_API_KEY",      None, "free", "Google API (free, quota-limited)"),
    ("The Guardian",         "GUARDIAN_API_KEY",     None, "free", "Guardian Open Platform (free)"),
    ("GitHub API",           "GITHUB_TOKEN",         None, "free", "repo/trends (free)"),
    ("Blogger",              "BLOGGER_API_KEY",      None, "free", "Google Blogger (free)"),
    ("Hashnode",             "HASHNODE_TOKEN",       None, "free", "dev blogs (free)"),
    ("Dev.to",               "DEVTO_API_KEY",        None, "free", "dev blogs (free)"),
    # usage-metered — tracked on their own cost lines (do NOT add to subs total)
    ("Perplexity",           "PERPLEXITY_API_KEY",   None, "metered", "AI research — on AI ledger line"),
    ("Anthropic",            "ANTHROPIC_API_KEY",    None, "metered", "AI synthesis — on AI ledger line"),
    ("Apify",                "APIFY_TOKEN",          None, "metered", "Google-Trends actor — live Apify line"),
    ("X (Twitter) API",      "X_BEARER_TOKEN",       None, "metered", "social — on X Developer API line"),
]


def data_subscriptions_total() -> float:
    """Sum of the PAID data-API cost env vars (each defaults to 0). This is the
    itemized replacement for the legacy lump COST_SUBSCRIPTIONS_USD."""
    import os
    t = 0.0
    for _name, _kenv, cenv, klass, _note in DATA_SUBSCRIPTIONS:
        if klass == "paid" and cenv:
            try:
                t += float(os.getenv(cenv, "0") or 0)
            except (TypeError, ValueError):
                pass
    return round(t, 2)


def data_subscriptions() -> dict:
    """Investigate + monitor every external data-API subscription: which are
    configured, how each is billed, and whether paid ones have a tracked cost.
    Honest-by-default: never invents a dollar amount — flags where one is owed."""
    import os
    alerts, items = [], []
    paid_total = 0.0
    paid_n = free_n = metered_n = 0
    untracked = []  # paid + configured + $0
    orphan_cost = []  # cost set but key missing

    for name, kenv, cenv, klass, note in DATA_SUBSCRIPTIONS:
        configured = bool(os.getenv(kenv))
        cost = None
        if cenv:
            try:
                cost = float(os.getenv(cenv, "0") or 0)
            except (TypeError, ValueError):
                cost = 0.0
        row = {"name": name, "key_env": kenv, "configured": configured,
               "billing": klass, "note": note}
        if cenv:
            row["cost_env"] = cenv
            row["usd"] = round(cost or 0, 2)
        items.append(row)

        if klass == "paid":
            paid_n += 1
            paid_total += (cost or 0)
            if configured and (cost or 0) == 0:
                untracked.append(f"{name} (set {cenv})")
            if (cost or 0) > 0 and not configured:
                orphan_cost.append(f"{name} (${cost:.2f} on {cenv}, no key)")
        elif klass == "free":
            free_n += 1
        else:
            metered_n += 1

    paid_total = round(paid_total, 2)
    if untracked:
        alerts.append({"level": "warn", "block": "B7",
                       "msg": f"{len(untracked)} paid data API(s) configured with NO tracked cost "
                              f"(untracked spend): {untracked} — set the COST_*_USD env so the "
                              "Cost Sentinel reflects real monthly spend"})
    if orphan_cost:
        alerts.append({"level": "warn", "block": "B7",
                       "msg": f"{len(orphan_cost)} cost set but API key missing "
                              f"(paying for nothing?): {orphan_cost}"})

    summary = {
        "paid_subscriptions": paid_n,
        "free_apis": free_n,
        "metered_elsewhere": metered_n,
        "paid_total_usd": paid_total,
        "untracked_paid": len(untracked),
        "items": items,
        "note": "paid_total feeds the Cost Sentinel 'Data API subscriptions' line. "
                "Metered APIs (AI/Apify/X) are billed on their own lines — excluded here "
                "to avoid double-counting. Costs default to $0 until set per provider.",
    }
    return {"agent": "data_subscriptions", "status": _roll_up(alerts),
            "alerts": alerts, "summary": summary, "checked_at": _now().isoformat()}


# ── Combined run ─────────────────────────────────────────────────────────────
def run_all(conn, db_path=None) -> dict:
    agents = [source_watchdog(conn=conn, db_path=db_path), pipeline_integrity(conn),
              fragment_category_auditor(conn), cost_sentinel(), calibration_auditor(),
              data_subscriptions()]
    overall = _roll_up([{"level": a["status"].replace("ok", "info")} for a in agents
                        if a["status"] != "ok"]) if any(a["status"] != "ok" for a in agents) else "ok"
    # overall = worst of the agent statuses
    order = {"ok": 0, "warn": 1, "critical": 2}
    overall = max((a["status"] for a in agents), key=lambda s: order.get(s, 0))
    all_alerts = [al for a in agents for al in a["alerts"]]
    return {
        "status": overall,
        "agents": {a["agent"]: a for a in agents},
        "alert_count": len(all_alerts),
        "alerts": all_alerts,
        "checked_at": _now().isoformat(),
    }
