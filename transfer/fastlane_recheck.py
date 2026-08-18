# -*- coding: utf-8 -*-
"""
fastlane_recheck.py — D10 free-source fast-lane recheck (flag-gated OFF by default)
===================================================================================
Implements audits/ledger-research/FASTLANE_RECHECK_DESIGN_2026-07-19.md exactly.

INTEGRITY CONTRACT (hard):
  * Google Trends stays the SOLE judge. This lane NEVER writes accuracy_ledger,
    NEVER computes a verdict, NEVER calls Apify. It only (a) logs its free-source
    observation to the held-out `fastlane_recheck_log` and (b) PROMOTES a pending
    row into the existing paid rotation by setting last_checked=NULL — the sweep's
    own ordering (`last_checked IS NULL DESC`) then rechecks it at the next paid
    clock slot. Zero marginal spend.
  * Caps: FASTLANE_TRIGGER_MAX (2) promotions per run — of the 8 paid sweep slots,
    at most 2 are fast-lane-directed; FASTLANE_COOLDOWN_H (72) per topic.
  * Rows it promotes are stamped in the log so /accuracy/ledger reporting can
    segment fastlane_triggered rows (param stamp `|fastlane1`); disclosure, not
    silent mixing.
  * FASTLANE_RECHECK=0 default — the code ships INERT (flag-never-force; the
    founder flips after the board gate on live evidence).

Runs from the aux scheduler every 6h at :10 UTC — deliberately OFF the :30/:45
paid clock-slot family (Apify clock-slot rule untouched).
"""
from __future__ import annotations
import json
import os
import re
import statistics
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

FASTLANE_RECHECK = os.getenv("FASTLANE_RECHECK", "0") == "1"
SCAN_LIMIT = int(os.getenv("FASTLANE_SCAN_LIMIT", "40"))
RECENT_DAYS = int(os.getenv("FASTLANE_RECENT_DAYS", "21"))
TRIGGER_MAX = int(os.getenv("FASTLANE_TRIGGER_MAX", "2"))
COOLDOWN_H = int(os.getenv("FASTLANE_COOLDOWN_H", "72"))
SURGE_MULT = 3.0          # referee_wikipedia convention (frozen; never tuned here)
SURGE_FLOOR = 200
UA = "NowTrendInFastlane/1.0 (free sources only; abelc.esq@gmail.com)"

_TABLE = """CREATE TABLE IF NOT EXISTS fastlane_recheck_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_key TEXT, detection_date TEXT, checked_at TEXT,
    wiki_ratio REAL, wiki_recent REAL, trending_hit INTEGER,
    triggered INTEGER, reason TEXT)"""


def _wiki_series(display: str, days: int = 14):
    """Free Wikimedia pageviews via the engine's own resolver (fail-open)."""
    try:
        import referee_wikipedia as rw
        art = rw.resolve_article(display)
        if not art:
            return None
        end = datetime.now(timezone.utc).date() - timedelta(days=1)
        start = end - timedelta(days=days)
        curve = rw.fetch_pageviews(art, datetime.combine(start, datetime.min.time(), timezone.utc),
                                   datetime.combine(end, datetime.min.time(), timezone.utc))
        if not curve or len(curve) < 7:
            return None
        views = [c.get("views", 0) for c in curve]
        med = statistics.median(views[:-3]) or 0
        recent = statistics.fmean(views[-3:])
        return {"ratio": recent / max(med, 1), "recent": recent, "median": med}
    except Exception:
        return None


def _trending_titles():
    try:
        req = urllib.request.Request("https://trends.google.com/trending/rss?geo=US",
                                     headers={"User-Agent": UA})
        xml = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        return [t.lower() for t in re.findall(r"<title>(.*?)</title>", xml)[1:26]]
    except Exception:
        return []


def run_once(get_db, db_path) -> dict:
    """One scan pass. Reads pending_detections; writes ONLY fastlane_recheck_log and
    (on trigger) pending_detections.last_checked=NULL. Verdict-free by construction."""
    if not FASTLANE_RECHECK:
        return {"enabled": False, "note": "FASTLANE_RECHECK=0 — lane inert (default)"}
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=RECENT_DAYS)).date().isoformat()
    cool = (now - timedelta(hours=COOLDOWN_H)).isoformat()
    conn = get_db(db_path)
    out = {"enabled": True, "scanned": 0, "triggered": 0, "log_rows": 0}
    try:
        conn.execute(_TABLE)
        conn.commit()
        rows = conn.execute(
            """SELECT p.id, p.topic_key, p.topic_display, p.detection_date
               FROM pending_detections p
               WHERE p.status = 'pending' AND p.detection_date >= ?
                 AND NOT EXISTS (SELECT 1 FROM fastlane_recheck_log f
                                 WHERE f.topic_key = p.topic_key
                                   AND f.detection_date = p.detection_date
                                   AND f.checked_at >= ?)
               ORDER BY p.last_checked ASC NULLS FIRST
               LIMIT ?""", (cutoff, cool, SCAN_LIMIT)).fetchall()
        trending = _trending_titles()
        triggered = 0
        for r in rows:
            rid = r["id"] if hasattr(r, "keys") else r[0]
            tk = r["topic_key"] if hasattr(r, "keys") else r[1]
            disp = (r["topic_display"] if hasattr(r, "keys") else r[2]) or tk.replace("_", " ")
            ddate = r["detection_date"] if hasattr(r, "keys") else r[3]
            out["scanned"] += 1
            wiki = _wiki_series(disp)
            t_hit = int(any(disp.lower() in t or t in disp.lower() for t in trending))
            surging = bool(wiki and wiki["recent"] >= max(SURGE_FLOOR,
                                                          SURGE_MULT * max(wiki["median"], 1)))
            fire = (surging or t_hit) and triggered < TRIGGER_MAX
            reason = ("wiki_surge" if surging else "") + ("+trending" if t_hit else "")
            conn.execute(
                "INSERT INTO fastlane_recheck_log (topic_key, detection_date, checked_at, "
                "wiki_ratio, wiki_recent, trending_hit, triggered, reason) VALUES (?,?,?,?,?,?,?,?)",
                (tk, ddate, now.isoformat(timespec="seconds"),
                 round(wiki["ratio"], 2) if wiki else None,
                 round(wiki["recent"], 1) if wiki else None,
                 t_hit, int(fire), reason or "no_signal"))
            out["log_rows"] += 1
            if fire:
                # PROMOTE into the existing paid rotation — the sweep judges, we never do.
                conn.execute("UPDATE pending_detections SET last_checked = NULL WHERE id = ?",
                             (rid,))
                triggered += 1
        conn.commit()
        out["triggered"] = triggered
        return out
    except Exception as e:
        return {"enabled": True, "error": str(e)[:200]}
    finally:
        try:
            conn.close()
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════════════════════
# LEVER B REBUILD — PRE-ENROLLMENT near-crosser lane (credibility board 2026-08-17,
# Chairman-approved). The board's Executioner finding: a post-enrollment recheck can
# move NOTHING the ledger judges (detection_date = first sighting, sealed at
# enrollment). The honest value is PRE-enrollment: topics sitting just UNDER the
# enrollment floor get an early FREE re-collect + rescore between the 6h cycles, so
# a genuinely-crossing topic enrolls before it ages out (14-day window) and its race
# starts sooner.
#
# INTEGRITY CONTRACT (board conditions, hard):
#   * FREE, NON-ORACLE sources only: the re-collect is collect_for_term (HN Algolia +
#     GitHub search — the engine's own free collectors). NO Wikipedia (it is the
#     REFEREE — Operator's common-mode finding), NO Google trending (the VALIDATOR's
#     family — Challenger's leakage finding), NO Apify (clock-slot rule untouched).
#   * Attribution: every row enrolled via this lane carries
#     enroll_arm='fastlane_nearcross' — the cadence epoch is separable in every rate
#     (Challenger: never compare pre/post-cadence like-for-like).
#   * The lane never writes accuracy_ledger, never computes a verdict, never touches
#     detection_date semantics: detection_date remains the topic's canonical
#     first-seen, exactly as the base enrollment path computes it.
#   * Caps + pacing: NEARCROSS_MAX topics/run, 10s between topics (§13 batch-paced),
#     per-topic cooldown; scoring runs through the engine's own normal pipeline.
# ════════════════════════════════════════════════════════════════════════════════
FASTLANE_NEARCROSS = os.getenv("FASTLANE_NEARCROSS", "1") == "1"
NEARCROSS_BAND = float(os.getenv("FASTLANE_NEARCROSS_BAND", "10"))     # points below floor
NEARCROSS_MAX = int(os.getenv("FASTLANE_NEARCROSS_MAX", "10"))         # topics per run
NEARCROSS_COOLDOWN_H = int(os.getenv("FASTLANE_NEARCROSS_COOLDOWN_H", "12"))
NEARCROSS_PAUSE_S = float(os.getenv("FASTLANE_NEARCROSS_PAUSE_S", "10"))

_NC_TABLE = """CREATE TABLE IF NOT EXISTS fastlane_nearcross_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_key TEXT, checked_at TEXT, score_before REAL, score_after REAL,
    collected INTEGER, crossed INTEGER, enrolled INTEGER, note TEXT)"""


def nearcross_once(get_db, db_path) -> dict:
    """One pre-enrollment pass: re-collect + rescore up to NEARCROSS_MAX near-floor
    topics via free sources; enroll any that cross, arm-stamped. Fail-open per topic."""
    if not FASTLANE_NEARCROSS:
        return {"enabled": False, "note": "FASTLANE_NEARCROSS=0 — lane inert"}
    import time as _t
    floor = float(os.getenv("LEDGER_DETECTION_FLOOR", "10"))
    recent_days = int(os.getenv("LEDGER_ENROLL_RECENT_DAYS", "14"))
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=recent_days)).isoformat()
    cool = (now - timedelta(hours=NEARCROSS_COOLDOWN_H)).isoformat()
    conn = get_db(db_path)
    out = {"enabled": True, "candidates": 0, "refreshed": 0, "crossed": 0, "enrolled": 0}
    try:
        conn.execute(_NC_TABLE)
        conn.commit()
        rows = conn.execute(
            """SELECT v.topic_key, v.topic_display, v.detection_score,
                      COALESCE(lc.first_detected_at, fs.first_at) AS det_date
               FROM velocity_scores v
               INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores
                           GROUP BY topic_key) l
                 ON v.topic_key=l.topic_key AND v.scored_at=l.m
               INNER JOIN (SELECT topic_key, MIN(scored_at) first_at FROM velocity_scores
                           GROUP BY topic_key) fs ON v.topic_key=fs.topic_key
               LEFT JOIN topic_lifecycle lc ON v.topic_key=lc.topic_key
               LEFT JOIN topic_maturity tm ON v.topic_key=tm.topic_key
               WHERE v.detection_score >= ? AND v.detection_score < ?
                 AND COALESCE(lc.first_detected_at, fs.first_at) >= ?
                 AND UPPER(COALESCE(tm.maturity_class, '')) NOT IN ('ESTABLISHED','MONITORING')
                 AND NOT EXISTS (SELECT 1 FROM pending_detections p
                                 WHERE p.topic_key = v.topic_key)
                 AND NOT EXISTS (SELECT 1 FROM accuracy_ledger a
                                 WHERE a.topic_key = v.topic_key)
                 AND NOT EXISTS (SELECT 1 FROM fastlane_nearcross_log f
                                 WHERE f.topic_key = v.topic_key AND f.checked_at >= ?)
               ORDER BY COALESCE(lc.first_detected_at, fs.first_at) DESC
               LIMIT ?""",
            (max(0.0, floor - NEARCROSS_BAND), floor, cutoff, cool,
             NEARCROSS_MAX)).fetchall()
        cands = [dict(r) if hasattr(r, "keys") else
                 dict(zip(("topic_key", "topic_display", "detection_score", "det_date"), r))
                 for r in rows]
    except Exception as e:
        out["error"] = str(e)[:200]
        try:
            conn.close()
        except Exception:
            pass
        return out
    finally:
        pass
    out["candidates"] = len(cands)
    for i, c in enumerate(cands):
        if i:
            _t.sleep(max(0.0, NEARCROSS_PAUSE_S))       # §13 batch pacing
        tk = c["topic_key"]
        disp = c["topic_display"] or tk.replace("_", " ")
        before = float(c["detection_score"] or 0)
        after = None
        collected = 0
        crossed = enrolled = 0
        note = ""
        try:
            import gravitational_anomaly_detector as _gad
            collected, after = _gad.fastlane_refresh_topic(tk, disp)
            out["refreshed"] += 1
            if after is not None and after >= floor:
                crossed = 1
                out["crossed"] += 1
                try:
                    import date_utils
                    dd = date_utils.to_iso_date(c["det_date"])
                except Exception:
                    dd = None
                if dd:
                    import accuracy_ledger_enhanced as _al
                    _al.record_detection(tk, disp, dd, after, db_path=db_path,
                                         enroll_arm="fastlane_nearcross")
                    enrolled = 1
                    out["enrolled"] += 1
                else:
                    note = "uncanonical_first_seen"
        except Exception as e:
            note = str(e)[:120]
        try:
            conn.execute(
                "INSERT INTO fastlane_nearcross_log (topic_key, checked_at, score_before, "
                "score_after, collected, crossed, enrolled, note) VALUES (?,?,?,?,?,?,?,?)",
                (tk, datetime.now(timezone.utc).isoformat(timespec="seconds"), before,
                 after, collected, crossed, enrolled, note or "ok"))
            conn.commit()
        except Exception:
            pass
    try:
        conn.close()
    except Exception:
        pass
    return out


def nearcross_status(get_db, db_path) -> dict:
    conn = get_db(db_path)
    try:
        conn.execute(_NC_TABLE)
        n = conn.execute("SELECT COUNT(*) AS c, SUM(crossed) AS x, SUM(enrolled) AS e "
                         "FROM fastlane_nearcross_log").fetchone()
        last = conn.execute("SELECT MAX(checked_at) AS m FROM fastlane_nearcross_log").fetchone()
        d = dict(n) if hasattr(n, "keys") else {"c": n[0], "x": n[1], "e": n[2]}
        return {"enabled": FASTLANE_NEARCROSS,
                "checked": d.get("c") or 0, "crossed": d.get("x") or 0,
                "enrolled": d.get("e") or 0,
                "last_run": (last["m"] if hasattr(last, "keys") else last[0]),
                "caps": {"band": NEARCROSS_BAND, "max_per_run": NEARCROSS_MAX,
                         "cooldown_h": NEARCROSS_COOLDOWN_H},
                "sources": "collect_for_term (HN Algolia + GitHub) — no Wikipedia, "
                           "no Google, no Apify"}
    except Exception as e:
        return {"enabled": FASTLANE_NEARCROSS, "error": str(e)[:120]}
    finally:
        try:
            conn.close()
        except Exception:
            pass


def status(get_db, db_path) -> dict:
    conn = get_db(db_path)
    try:
        conn.execute(_TABLE)
        n = conn.execute("SELECT COUNT(*) AS c, SUM(triggered) AS t "
                         "FROM fastlane_recheck_log").fetchone()
        last = conn.execute("SELECT MAX(checked_at) AS m FROM fastlane_recheck_log").fetchone()
        return {"enabled": FASTLANE_RECHECK,
                "log_rows": (n["c"] if hasattr(n, "keys") else n[0]) or 0,
                "total_triggered": (n["t"] if hasattr(n, "keys") else n[1]) or 0,
                "last_run": (last["m"] if hasattr(last, "keys") else last[0]),
                "caps": {"scan": SCAN_LIMIT, "trigger_max": TRIGGER_MAX,
                         "cooldown_h": COOLDOWN_H, "recent_days": RECENT_DAYS}}
    except Exception as e:
        return {"enabled": FASTLANE_RECHECK, "error": str(e)[:120]}
    finally:
        try:
            conn.close()
        except Exception:
            pass
