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


# ── Combined run ─────────────────────────────────────────────────────────────
def run_all(conn, db_path=None) -> dict:
    agents = [source_watchdog(conn=conn, db_path=db_path), pipeline_integrity(conn)]
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
