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


# ── Agent K: SCORER WATCHDOG (B4 process liveness) ──────────────────────────
# The scoring-PROCESS counterpart to Source Watchdog (which watches collectors).
# A topic is only as fresh as the scorer that wrote it. Scoring is hybrid: a LOCAL
# worker scores every SCORE_INTERVAL_MIN (free hardware), and the Heroku CLOUD dyno
# collect+scores every COLLECT_INTERVAL_MIN AND failover-scores if the local
# heartbeat goes stale (> SCORE_STALE_MIN). This agent reads the worker_heartbeat
# PROCESS signal — distinct from Pipeline Integrity B4, which checks the DATA
# freshness (MAX scored_at) — and answers: is a scorer alive, WHICH one, and is the
# failover posture healthy? It catches the "no local worker AND cloud stalled →
# scores frozen" case that a data-only check explains only after the fact.
def scorer_watchdog(conn=None, db_path=None) -> dict:
    import os as _os
    import gravitational_anomaly_detector as g
    alerts = []
    BIG = 1e8
    try:
        age       = g._heartbeat_age_min("score")        # any scorer
        age_local = g._heartbeat_age_min("score_local")  # local worker
        age_cloud = g._heartbeat_age_min("score_cloud")  # Heroku cloud/failover
    except Exception as e:
        return {"agent": "scorer_watchdog", "status": "warn",
                "alerts": [{"level": "warn", "block": "B4", "msg": f"heartbeat read failed: {e}"}],
                "summary": {}, "checked_at": _now().isoformat()}

    warn_min = float(_os.getenv("SCORER_WARN_MIN", "420"))   # 7h  (matches B4 warn)
    crit_min = float(_os.getenv("SCORER_CRIT_MIN", "720"))   # 12h (matches B4 critical)
    last_scorer = "unknown"
    if min(age_local, age_cloud) < BIG:
        last_scorer = "local worker" if age_local <= age_cloud else "Heroku cloud"

    if age >= crit_min:
        alerts.append({"level": "critical", "block": "B4",
                       "msg": f"NO scorer heartbeat in {age:.0f}m (>{crit_min:.0f}m) — both the local "
                              f"worker AND the Heroku failover appear down; scores are FROZEN"})
    elif age >= warn_min:
        alerts.append({"level": "warn", "block": "B4",
                       "msg": f"scorer quiet {age:.0f}m (>{warn_min:.0f}m) — last scorer was {last_scorer}; "
                              f"a cycle was missed (local worker offline? cloud cadence slow?)"})

    summary = {
        "score_heartbeat_min_ago": round(age, 1) if age < BIG else None,
        "last_scorer": last_scorer,
        "local_worker_min_ago": round(age_local, 1) if age_local < BIG else None,
        "cloud_min_ago": round(age_cloud, 1) if age_cloud < BIG else None,
        "failover_stale_min": float(_os.getenv("SCORE_STALE_MIN", "45")),
        "note": "Local worker scores every SCORE_INTERVAL_MIN; the Heroku cloud collect+scores every "
                "COLLECT_INTERVAL_MIN and failover-scores if the local heartbeat is stale. Process-"
                "liveness signal — pairs with Pipeline Integrity B4 (data freshness).",
    }
    return {"agent": "scorer_watchdog", "status": _roll_up(alerts),
            "alerts": alerts, "summary": summary, "checked_at": _now().isoformat()}


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
            SELECT v.*
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

    # B8 (serve-SCORE consistency) — THE SAME TOPIC MUST SERVE THE SAME SCORE on
    # every surface. /scores, /scores/{key} and /topics all read the precomputed
    # serve_payload (single source of truth); two ways that silently breaks:
    #   • STALE PAYLOAD — a scoring/calibration change shipped WITHOUT regenerating
    #     serve_payload, so the payload (what surfaces serve) drifts from a fresh
    #     calibration. This exact gotcha masked a fix on 2026-06-18. Detected by
    #     re-running _calibrate_score_fields live and comparing to the stored payload.
    #   • MAINSTREAM COLLAPSE — the pathway gate in apply_calibration regresses and a
    #     mainstream topic's served detection falls far below its stored dual-pathway
    #     value (every mainstream topic ≈27, unrankable). If the scoring is not
    #     matching, there is a problem — this is the alarm.
    # Sub-sampled (live calibration is costly): the top rows only.
    import json as _json, os as _os
    stale, collapsed, checked = [], [], 0
    for r in rows[:int(_os.getenv("SERVE_CONSISTENCY_SAMPLE", "40"))]:
        rd = dict(r)
        payload = rd.pop("serve_payload", None)
        stored_det = rd.get("detection_score") or 0
        pathway = (rd.get("detection_pathway") or "").lower()
        try:
            live = g._calibrate_score_fields(dict(rd))
            live_det = live.get("detection_score") or 0
        except Exception:
            continue
        checked += 1
        served_det = live_det
        if payload:
            try:
                served_det = (_json.loads(payload) or {}).get("detection_score") or live_det
                if abs(served_det - live_det) > 2.0:
                    stale.append((rd.get("topic_key"), round(served_det, 1), round(live_det, 1)))
            except Exception:
                pass
        if pathway in ("mainstream", "blended") and stored_det >= 50 and served_det < stored_det * 0.6:
            collapsed.append((rd.get("topic_key"), round(stored_det, 1), round(served_det, 1)))
    summary["serve_consistency_checked"] = checked
    summary["serve_stale_payload"] = len(stale)
    summary["serve_mainstream_collapse"] = len(collapsed)
    if stale:
        alerts.append({"level": "warn", "block": "B8",
                       "msg": f"{len(stale)} topic(s) serve a STALE serve_payload (payload≠fresh "
                              f"calibration, e.g. {stale[:4]}) — regenerate _precompute_serve_payloads "
                              f"after ANY scoring/calibration change (GOTCHA)"})
    if collapsed:
        alerts.append({"level": "critical", "block": "B8",
                       "msg": f"{len(collapsed)} mainstream topic(s) served with COLLAPSED detection "
                              f"(≪ stored dual-pathway, e.g. {collapsed[:4]}) — the pathway gate in "
                              f"apply_calibration (signal_calibration_integration.py) regressed; served "
                              f"detection must match across /topics, /scores, /scores/{{key}}"})

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

    # 5) Firecrawl credits — 2 credits per AI grade (on-demand only, not automated cycle)
    fc_line = {}
    if os.getenv("FIRECRAWL_API_KEY"):
        try:
            fc_cap = int(os.getenv("FIRECRAWL_CREDITS_CAP", "500"))
            # Count AI grades this month from the cost ledger and multiply by 2 credits/grade
            month_iso = g._month_start_iso()
            conn_fc = g.get_db(g.DB_PATH)
            grade_row = conn_fc.execute(
                "SELECT COUNT(*) AS n FROM ai_grade_costs WHERE created_at >= ?",
                (month_iso,)).fetchone()
            conn_fc.close()
            grades_mtd = int((grade_row or {}).get("n") or 0)
            fc_used = grades_mtd * 2   # Firecrawl charges 2 credits per /search call
            pct = fc_used / fc_cap if fc_cap else 0
            fc_line = {"credits_used": fc_used, "credits_cap": fc_cap,
                       "grades_mtd": grades_mtd, "pct": round(pct * 100, 1),
                       "note": "estimated: grades_mtd × 2 credits/grade"}
            lines.append({"item": "Firecrawl (grade web search)", "credits": fc_used,
                          "cap": fc_cap, "source": "estimated"})
            if pct >= 1.0:
                alerts.append({"level": "critical", "block": "B7",
                               "msg": f"Firecrawl credits likely EXHAUSTED: ~{fc_used}/{fc_cap} used this month"})
            elif pct >= 0.8:
                alerts.append({"level": "warn", "block": "B7",
                               "msg": f"Firecrawl credits at ~{pct*100:.0f}% of {fc_cap}/mo cap — consider upgrading"})
        except Exception as _fce:
            alerts.append({"level": "warn", "block": "B7",
                           "msg": f"Firecrawl credit check failed: {_fce}"})

    grand_cap = float(os.getenv("COST_TOTAL_MONTHLY_CAP", "0") or 0)
    if grand_cap and total >= grand_cap:
        alerts.append({"level": "critical", "block": "B7",
                       "msg": f"TOTAL monthly cost ${total:.2f} ≥ cap ${grand_cap:.0f}"})

    summary = {
        "total_monthly_usd": round(total, 2),
        "total_cap_usd": grand_cap or None,
        "lines": lines,
        "x_posts": x_line,
        "firecrawl": fc_line,
        "note": "AI + Apify are live-metered; Heroku/subscriptions/GitHub are env-configured "
                "(set COST_HEROKU_USD / COST_SUBSCRIPTIONS_USD / COST_GITHUB_USD / COST_TOTAL_MONTHLY_CAP). "
                "Firecrawl credits estimated from monthly grade count × 2 credits/grade "
                "(set FIRECRAWL_CREDITS_CAP to override the 500-credit default).",
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
    ("Currents",             "CURRENTS_API_KEY",     None, "free",
     "multi-source news aggregator (free tier 1000 req/day; hard-capped via "
     "CURRENTS_DAILY_CAP, ~4 calls/day in practice)"),
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


# ── Agent I: CATCH-ALL AUDITOR (B3 — the news/general catch-all, specialised) ─
# A dedicated specialist for the topic/post catch-all congestion. Where the Topic
# Quality Auditor reports a single news_catchall_pct, this agent DIAGNOSES it:
#   • catch-all % + counts (the headline metric, tracked daily for trend)
#   • FLOOR HEALTH — single-source catch-all topics that leaked past the
#     CATCHALL_MIN_SOURCES corroboration floor (should be ~0; a climb means the
#     floor is disabled or a purge is overdue)
#   • MISCLASSIFIED TRACKED CALLS — accuracy-ledger / pending detections stuck in
#     the catch-all (real signals the thin lexicon mis-sorted — highest priority)
#   • LEXICON CANDIDATES — the most frequent meaningful tokens across catch-all
#     topics (common words / filler / numbers excluded). These are the terms to
#     add to topic_categories._LEX so the topics leave the catch-all for their
#     true category — the real lever on the catch-all %.
# Designed to be run end-of-day: its summary is a worklist, not just a number.
def catchall_auditor(conn) -> dict:
    import datetime, collections
    import gravitational_anomaly_detector as g
    alerts = []
    nf = getattr(g, "NEWS_FILLER", set())
    min_src = getattr(g, "CATCHALL_MIN_SOURCES", 2)
    catch_cats = getattr(g, "_CATCHALL_CATS", ("news", "general", ""))

    # corroboration per topic (distinct sources + any expert-tier signal), 72h
    agg = {}
    try:
        cut = (datetime.datetime.utcnow() - datetime.timedelta(hours=72)).isoformat()
        for r in conn.execute(
            "SELECT topic_key, COUNT(DISTINCT source_name) nsrc, "
            "MAX(CASE WHEN platform_tier IN ('expert','niche') THEN 1 ELSE 0 END) hasx "
            "FROM topic_signals WHERE extracted_at >= ? GROUP BY topic_key", (cut,)).fetchall():
            agg[r["topic_key"]] = (int(r["nsrc"] or 0), int(r["hasx"] or 0))
    except Exception as e:
        alerts.append({"level": "warn", "block": "B3", "msg": f"corroboration read failed: {e}"})

    # tracked calls (never legitimately catch-all junk) — for misclassified detect
    protect = set()
    for t in ("accuracy_ledger", "pending_detections"):
        try:
            for r in conn.execute(f"SELECT DISTINCT topic_key FROM {t}").fetchall():
                protect.add(r["topic_key"])
        except Exception:
            pass

    try:
        rows = conn.execute(
            "SELECT v.topic_key, v.topic_display FROM velocity_scores v "
            "INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores "
            "GROUP BY topic_key) l ON v.topic_key=l.topic_key AND v.scored_at=l.m").fetchall()
    except Exception as e:
        return {"agent": "catchall_auditor", "status": "warn",
                "alerts": [{"level": "warn", "block": "B3", "msg": f"scored read failed: {e}"}],
                "summary": {}, "checked_at": _now().isoformat()}

    total = len(rows) or 1
    catch = single_src = 0
    misclassified_real, samples = [], []
    token_freq = collections.Counter()
    for r in rows:
        k = r["topic_key"]
        disp = (r["topic_display"] or k or "")
        try:
            cat = g._topic_category(disp) or ""
        except Exception:
            cat = ""
        if cat not in catch_cats:
            continue
        catch += 1
        nsrc, hasx = agg.get(k, (0, 0))
        if nsrc < min_src and not hasx and k not in protect:
            single_src += 1                       # floor leak (≈0 expected)
        if k in protect:
            misclassified_real.append(disp)       # tracked call stuck in catch-all
        for tok in disp.lower().split():          # lexicon-candidate tally
            tok = tok.strip(".,:;!?\"'()[]")
            if (len(tok) >= 4 and not tok.isdigit()
                    and tok not in nf and not g._is_common_word(tok)):
                token_freq[tok] += 1
        if len(samples) < 15:
            samples.append(disp)

    catch_pct = round(catch / total * 100, 1)
    top_terms = token_freq.most_common(25)

    # ── Persist time-series row and compute trend ──────────────────────────────
    trend = "STABLE"
    leak_delta = None
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS catchall_floor_log (
                logged_at TEXT PRIMARY KEY,
                total_scored INTEGER,
                catchall_count INTEGER,
                catchall_pct REAL,
                single_source_leak INTEGER,
                misclassified_tracked INTEGER,
                min_sources INTEGER
            )
        """)
        conn.commit()
        prev_rows = conn.execute(
            "SELECT single_source_leak FROM catchall_floor_log "
            "ORDER BY logged_at DESC LIMIT 2"
        ).fetchall()
        now_str = _now().isoformat()
        conn.execute("""
            INSERT OR IGNORE INTO catchall_floor_log
                (logged_at, total_scored, catchall_count, catchall_pct,
                 single_source_leak, misclassified_tracked, min_sources)
            VALUES (?,?,?,?,?,?,?)
        """, (now_str, total, catch, catch_pct, single_src,
              len(misclassified_real), min_src))
        conn.commit()
        if prev_rows:
            prev_leak = prev_rows[0]["single_source_leak"] or 0
            leak_delta = single_src - prev_leak
            if leak_delta > 10:
                trend = "WORSENING"
            elif leak_delta < -10:
                trend = "IMPROVING"
    except Exception as _e:
        alerts.append({"level": "warn", "block": "B3",
                       "msg": f"catchall_floor_log write failed: {_e}"})

    summary = {
        "total_scored": total, "catchall_count": catch, "catchall_pct": catch_pct,
        "floor_min_sources": min_src,
        "single_source_catchall_leak": single_src,
        "floor_trend": trend,
        "floor_leak_delta": leak_delta,
        "misclassified_tracked": len(misclassified_real),
        "misclassified_examples": misclassified_real[:15],
        "lexicon_candidates": [{"term": t, "count": c} for t, c in top_terms],
        "samples": samples,
    }
    if catch_pct >= 70:
        alerts.append({"level": "warn", "block": "B3",
                       "msg": f"catch-all at {catch_pct}% ({catch}/{total}) — still congested. "
                              f"Top lexicon candidates to reclassify: {[t for t, _ in top_terms[:10]]}"})
    if single_src > 50:
        alerts.append({"level": "warn", "block": "B3",
                       "msg": f"{single_src} single-source catch-all topics leaked past the "
                              f"corroboration floor (min_sources={min_src}) — floor disabled or purge overdue"})
    if trend == "WORSENING":
        alerts.append({"level": "warn", "block": "B3",
                       "msg": f"catch-all floor trend WORSENING: single-source leaks grew by "
                              f"{leak_delta} since last check (now {single_src}) — "
                              f"floor may be disabled or new junk is entering"})
    if misclassified_real:
        alerts.append({"level": "warn", "block": "B3",
                       "msg": f"{len(misclassified_real)} TRACKED call(s) (ledger/pending) stuck in the "
                              f"catch-all — reclassify first: {misclassified_real[:8]}"})
    return {"agent": "catchall_auditor", "status": _roll_up(alerts),
            "alerts": alerts, "summary": summary, "checked_at": _now().isoformat()}


# ── Agent J: MARKET UNIVERSE COVERAGE (B1 — Market Signal completeness) ──────
# Catches the "SpaceX problem": a real publicly-traded company is trending in the
# attention data but is MISSING from the curated Market Signal universe
# (WATCHLIST_TICKERS) — e.g. a fresh IPO the static list never got. It scans the
# top business/economy/technology trending topics, and for any NOT already
# tracked, asks the ticker resolver (Finnhub Common-Stock search) whether it's a
# real public company. Real ticker + trending + untracked = a coverage GAP to add.
#
# Integrity: it FLAGS candidates with their resolved ticker for human confirmation
# — it never auto-adds (a wrong/ambiguous resolve must not silently enter the
# universe) and never force-injects a score. Private companies (Anthropic, etc.)
# don't resolve to a Common Stock, so they're correctly NOT flagged. NOT in
# run_all — the per-candidate Finnhub calls are too costly for every /monitor;
# run it on its own endpoint / on a schedule.
def market_universe_coverage(conn, sample: int = 250, max_resolve: int = 20) -> dict:
    import gravitational_anomaly_detector as g
    alerts = []
    if not getattr(g, "_RISK_AVAILABLE", False) or not hasattr(g, "risk"):
        return {"agent": "market_universe_coverage", "status": "warn",
                "alerts": [{"level": "warn", "block": "B1", "msg": "risk module unavailable"}],
                "summary": {}, "checked_at": _now().isoformat()}
    wl = g.risk.WATCHLIST_TICKERS if hasattr(g.risk, "WATCHLIST_TICKERS") else {}
    wl_disp = {d.lower() for d in wl}
    wl_tkr = {t.upper() for t in wl.values()}
    try:
        rows = conn.execute(
            """SELECT v.topic_key, v.topic_display, v.total_mentions FROM velocity_scores v
               INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores
                           GROUP BY topic_key) l
                 ON v.topic_key = l.topic_key AND v.scored_at = l.m
               ORDER BY COALESCE(v.total_mentions, 0) DESC LIMIT ?""", (sample,)).fetchall()
    except Exception as e:
        return {"agent": "market_universe_coverage", "status": "warn",
                "alerts": [{"level": "warn", "block": "B1", "msg": f"query failed: {e}"}],
                "summary": {}, "checked_at": _now().isoformat()}

    # company-like candidates not already tracked (capped to limit Finnhub calls)
    candidates = []
    for r in rows:
        disp = (r["topic_display"] or "").strip()
        if not disp or disp.lower() in wl_disp:
            continue
        if disp == disp.lower():          # proper nouns only (companies are capitalised)
            continue
        try:
            cat = g._topic_category(disp) or ""
        except Exception:
            cat = ""
        if cat not in ("business", "economy", "technology"):
            continue
        candidates.append((disp, int(r["total_mentions"] or 0)))
        if len(candidates) >= max_resolve:
            break

    gaps = []
    for disp, mentions in candidates:
        try:
            tkr, rdisp = g.risk.resolve_ticker(disp)
        except Exception:
            tkr = None
        if tkr and tkr.upper() not in wl_tkr:
            gaps.append({"topic": disp, "ticker": tkr.upper(),
                         "resolved_as": rdisp, "mentions": mentions})

    summary = {
        "scanned": len(rows),
        "company_candidates_checked": len(candidates),
        "tracked_universe": len(wl),
        "coverage_gaps": len(gaps),
        "gaps": gaps,
        "note": "Gaps are publicly-traded companies trending now but absent from "
                "WATCHLIST_TICKERS. Confirm each ticker, then add to "
                "financial_risk_gradient.WATCHLIST_TICKERS (+ _TICKER_SECTOR) and run a "
                "risk collection. Flag only — never auto-add (avoid a wrong resolve).",
    }
    if gaps:
        alerts.append({"level": "warn", "block": "B1",
                       "msg": f"{len(gaps)} publicly-traded compan{'y' if len(gaps)==1 else 'ies'} "
                              f"trending but MISSING from the Market universe: "
                              f"{[(x['topic'], x['ticker']) for x in gaps[:8]]} — add to WATCHLIST_TICKERS"})
    return {"agent": "market_universe_coverage", "status": _roll_up(alerts),
            "alerts": alerts, "summary": summary, "checked_at": _now().isoformat()}


# ── Combined run ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Canonical Date Auditor (Agent 16) — owns B3a (the canonical date/time model).
# Verifies every STORED date-semantic value is canonical 'YYYY-MM-DD' across ALL
# sources. Coverage is by COLUMN (the funnel every source writes into) PLUS live-
# schema discovery of every '*_date' column — so a NEW source is audited the moment
# it writes a date, with NO per-source list to maintain. This closes the structural
# blind spot in the gate: the gate only sees values that PASS THROUGH it, so a path
# that bypasses gate_date() (e.g. a hand-rolled [:10]) was invisible. The auditor
# checks the DATA, so a bad date is caught no matter which code path produced it.
# Read-only.
# ─────────────────────────────────────────────────────────────────────────────
import re as _re
_IDENT_RE = _re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _discover_date_columns(conn) -> set:
    """Every column in the live schema whose name ends in '_date' (the canonical
    primary-date naming convention) → set of (table, column). Works on Postgres
    (information_schema) and SQLite (sqlite_master + PRAGMA)."""
    found = set()
    try:
        import db_compat
        use_pg = bool(getattr(db_compat, "USE_PG", False))
    except Exception:
        use_pg = False
    try:
        if use_pg:
            for r in conn.execute(
                "SELECT table_name, column_name FROM information_schema.columns "
                "WHERE table_schema='public' AND column_name LIKE '%_date'").fetchall():
                t = r["table_name"] if hasattr(r, "keys") else r[0]
                c = r["column_name"] if hasattr(r, "keys") else r[1]
                found.add((t, c))
        else:
            for tr in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'").fetchall():
                t = tr["name"] if hasattr(tr, "keys") else tr[0]
                if not _IDENT_RE.match(str(t)):
                    continue
                for cr in conn.execute(f"PRAGMA table_info({t})").fetchall():
                    c = cr["name"] if hasattr(cr, "keys") else cr[1]
                    if str(c).endswith("_date"):
                        found.add((t, c))
    except Exception:
        pass
    return found


def canon_date_auditor(conn=None, db_path=None) -> dict:
    """Agent 16 — Canonical Date Auditor (B3a). Read-only. Confirms every stored
    date-semantic value is canonical 'YYYY-MM-DD', for ALL sources at once: it audits
    the COLUMNS every source funnels into and DISCOVERS new '*_date' columns from the
    live schema, so new sources are covered automatically. Flags: (a) non-canonical
    values per column, (b) a '*_date' column NOT registered in ingestion_gate.
    DATE_SEMANTIC (an ungated write path / unwired new source), (c) values the gate
    quarantined for a human format decision."""
    own = conn is None
    try:
        import db_compat
        from date_utils import is_iso_date
        import ingestion_gate
    except Exception as e:
        return {"agent": "canon_date_auditor", "status": "warn",
                "alerts": [{"level": "warn", "block": "B3a", "msg": f"deps unavailable: {e}"}],
                "summary": {}, "checked_at": _now().isoformat()}
    if own:
        conn = db_compat.connect(db_path)
    alerts = []
    declared = ingestion_gate.DATE_SEMANTIC
    declared_set = {(t, c) for t, cols in declared.items() for c in cols}
    # Date-NAMED columns that are intentionally operational INSTANTS (full ISO datetime),
    # NOT canonical primary sort keys — §14 allows these to keep their precise instant.
    # Allowlisted so they are neither flagged as drift nor value-audited as bare dates.
    operational = {("pending_detections", "timeout_date")}
    discovered = _discover_date_columns(conn) - operational
    # (b) drift — a date-named column nobody registered/gated (likely a new source).
    #     WARN (classify it: gate + register it, OR add to the operational allowlist) —
    #     NOT critical, since an unclassified column might be an operational instant.
    undeclared = sorted(discovered - declared_set)
    if undeclared:
        alerts.append({"level": "warn", "block": "B3a",
            "msg": f"{len(undeclared)} '*_date' column(s) NOT in the gate registry "
                   f"(classify: gate_date + add to DATE_SEMANTIC, or allowlist as "
                   f"operational): " + ", ".join(f"{t}.{c}" for t, c in undeclared[:8])})
    # (a) canonical compliance per column. CRITICAL only for DECLARED canonical columns
    #     (a bad value there is a real §14 violation — the bug this agent exists to catch);
    #     undeclared columns are covered by the WARN above (values shown for context).
    by_col, total_bad = [], 0
    for t, c in sorted(declared_set | discovered):
        if not (_IDENT_RE.match(str(t)) and _IDENT_RE.match(str(c))):
            continue
        try:
            rows = conn.execute(
                f"SELECT {c} AS v FROM {t} WHERE {c} IS NOT NULL AND {c} <> ''").fetchall()
        except Exception:
            continue   # column/table absent on this DB - skip silently
        vals = [(r["v"] if hasattr(r, "keys") else r[0]) for r in rows]
        bad = [v for v in vals if not is_iso_date(v)]
        is_declared = (t, c) in declared_set
        if is_declared:
            total_bad += len(bad)
        rec = {"column": f"{t}.{c}", "declared": is_declared,
               "rows": len(vals), "non_canonical": len(bad)}
        if bad:
            rec["examples"] = sorted({str(v) for v in bad})[:3]
            if is_declared:
                alerts.append({"level": "critical", "block": "B3a",
                    "msg": f"{t}.{c}: {len(bad)}/{len(vals)} non-canonical date(s), "
                           f"e.g. {rec['examples']}"})
        by_col.append(rec)
    # (c) gate escalations awaiting a human decision
    try:
        pend = ingestion_gate.pending_reviews(conn, limit=50)
    except Exception:
        pend = []
    if pend:
        alerts.append({"level": "warn", "block": "B3a",
            "msg": f"{len(pend)} date value(s) quarantined awaiting a human format decision"})
    if own:
        try: conn.close()
        except Exception: pass
    return {"agent": "canon_date_auditor", "status": _roll_up(alerts), "alerts": alerts,
            "summary": {"columns_audited": len(by_col), "non_canonical_total": total_bad,
                        "undeclared_date_columns": [f"{t}.{c}" for t, c in undeclared],
                        "pending_reviews": len(pend), "by_column": by_col},
            "checked_at": _now().isoformat()}


def scoring_contract_auditor(conn=None, db_path=None) -> dict:
    """Agent 17 — Scoring Contract Auditor (block B3b). Read-only. Audits every scoring
    field against the declared SCORING_CONTRACT (type / unit / range / enum / required /
    derived-rule), across all live rows, so a silent FORMAT misread is caught no matter
    which code path produced it - and a new scoring-shaped column is flagged to classify.
    Generalizes the Canonical Date Auditor (Agent 16) from dates to ALL scoring inputs/
    outputs. Catches: out-of-range/wrong-type values, off-enum stages/tiers, required-but-
    null fields, a derived field gone stale (e.g. heisenberg_gap != detection-confidence),
    and DEGENERATE fields (one value across >=90% of rows = the missing-as-zero fingerprint
    that flattened Positioning Concentration)."""
    own = conn is None
    try:
        import db_compat, scoring_contract
    except Exception as e:
        return {"agent": "scoring_contract_auditor", "status": "warn",
                "alerts": [{"level": "warn", "block": "B3b", "msg": f"deps unavailable: {e}"}],
                "summary": {}, "checked_at": _now().isoformat()}
    if own:
        conn = db_compat.connect(db_path)
    try:
        rep = scoring_contract.audit(conn)
    except Exception as e:
        rep = None
        err = str(e)
    finally:
        if own:
            try: conn.close()
            except Exception: pass
    if rep is None:
        return {"agent": "scoring_contract_auditor", "status": "warn",
                "alerts": [{"level": "warn", "block": "B3b", "msg": f"audit error: {err}"}],
                "summary": {}, "checked_at": _now().isoformat()}
    alerts = []
    for v in rep.get("violations", []):
        lvl = "critical" if v.get("kind") in ("value", "missing-column") else "warn"
        msg = f"{v['field']}: {v.get('kind')}"
        if v.get("count"): msg += f" x{v['count']} {v.get('examples')}"
        if v.get("detail"): msg += f" - {v['detail']}"
        alerts.append({"level": lvl, "block": "B3b", "msg": msg})
    for d in rep.get("derived_mismatch", []):
        alerts.append({"level": "critical", "block": "B3b",
            "msg": f"{d['field']} derived-rule broken ({d['rule']}): {d['mismatched_rows']}/{d['of']} rows"})
    for g in rep.get("degenerate", []):
        alerts.append({"level": "warn", "block": "B3b",
            "msg": f"{g['field']} DEGENERATE: value {g['value']} on {int(g['share']*100)}% of "
                   f"{g['rows']} rows (silent-misread fingerprint)"})
    for u in rep.get("unregistered_columns", []):
        alerts.append({"level": "warn", "block": "B3b",
            "msg": f"unregistered scoring-shaped column {u} (classify: add to SCORING_CONTRACT)"})
    summary = {"tables": rep.get("tables"), "fields_audited": len(rep.get("fields", [])),
               "value_violations": sum(1 for v in rep.get("violations", []) if v.get("kind") == "value"),
               "derived_mismatches": len(rep.get("derived_mismatch", [])),
               "degenerate_fields": [g["field"] for g in rep.get("degenerate", [])],
               "unregistered_columns": rep.get("unregistered_columns", [])}
    return {"agent": "scoring_contract_auditor", "status": _roll_up(alerts),
            "alerts": alerts, "summary": summary, "checked_at": _now().isoformat()}


def run_all(conn, db_path=None) -> dict:
    # HEAVY DATA-SCANNING auditors excluded from this synchronous roll-up — they
    # do full-table scans that push /monitor past Heroku's 30s router limit (503):
    #   • canon_date_auditor (16)       → /monitor/datecanon       (24s+ on 228k rows)
    #   • scoring_contract_auditor (17) → /monitor/scoringcontract
    #   • catchall_auditor (I)          → /monitor/catchall         (full velocity_scores +
    #                                       topic_signals 72h; designed for end-of-day)
    # run_all stays the FAST liveness/health roll-up (~3–5s).
    agents = [source_watchdog(conn=conn, db_path=db_path), scorer_watchdog(conn=conn, db_path=db_path),
              pipeline_integrity(conn),
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
