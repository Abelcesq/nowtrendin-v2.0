# -*- coding: utf-8 -*-
"""SHADOW-TRIAL ENROLLMENT DRIVER — the selection code, which is the real membership rule.

Board 2026-08-20 evening, claim C-SHADOW-SELECTOR. Every seat that looked at the trial
said a version of the same thing: the four arm populations were sealed as PROSE, and
"the sampling code is the real membership criterion" (Forecaster). Sealing rules before
writing the code that implements them protects against nothing, because every forking
path in the selection gets chosen after the seal — by whoever writes it, under deadline.

This module is that code, written BEFORE the window opens (2026-09-01) so the seal
governs it rather than the reverse.

THE FOUR ARMS (prereg §3, enforced here rather than described):
  candidate    first-crossings from the SEALED candidate feed sets
  control      first-crossings from the existing roster, identical rules, same window
  null_random  random topics from the SAME candidate feeds — no D logic, no signal logic
  null_volume  the dumb-volume rule: >= NULL_VOLUME_K expert-tier mentions, no D logic

DETERMINISM (Statistician + Economist): `null_random` draws from a seed derived from the
sealed prereg text hash plus the cycle date. A human choosing "random" topics is not
random, and a human choosing WHEN to draw is a forking path. Same cycle, same draw,
re-runnable by anyone holding the prereg.

CROSS-ARM EXCLUSIVITY (Challenger F7.2): a topic enrolled in one arm can never enter
another. `candidate` and `null_random` draw from the same feeds, so without this the
primary comparison — a candidate-vs-null DIFFERENCE — would share rows with its own
control, biasing the difference toward zero and making its variance uninterpretable.

CALIBRATING (prereg §7 via ERRATUM 01): a topic whose venue's collection age is under
D_COMMUNITY_MIN_AGE_DAYS is enrolled and STAMPED `calibrating=1`, and excluded from the
H-A/H-B denominators at readout. Enrolled, not dropped — the graveyard is the evidence.

This module WRITES ONLY to the shadow ledger. It never touches a score, a verdict, a
served payload, or the real ledger. Registered held-out.
"""
from __future__ import annotations

import hashlib
import os
import random
from datetime import datetime, timedelta, timezone
from typing import Optional

import db_compat
import shadow_ledger as sl

DB_PATH = os.getenv("DB_PATH", "anomaly_detector.db")

# Sealed selection parameters. LITERALS by rule (integrity gate lint L1): a trial
# parameter readable from the environment is one the beneficiary can retune with no
# commit and no trace.
NULL_VOLUME_K = 3              # "dumb volume": >= K expert-tier mentions, no D logic
ENROLL_RECENT_DAYS = 14        # first-crossing freshness, mirrors the real ledger
CALIBRATING_DAYS = 14          # venue-age threshold; matches D_COMMUNITY_MIN_AGE_DAYS
NULL_RANDOM_RATIO = 1.0        # draw size = this * the cycle's candidate count

_D_TIERS = ("expert", "niche")
ARMS_ALL = ("candidate", "control", "null_random", "null_volume")


def _ph() -> str:
    return "%s" if db_compat.USE_PG else "?"


def _cycle_seed(cycle_date: str) -> random.Random:
    """Deterministic per cycle, derived from the SEALED prereg hash. Anyone holding the
    prereg can reproduce the exact draw — which is what makes it a null and not a choice."""
    h = hashlib.sha256(f"{sl.PREREG_TEXT_SHA256}|{cycle_date}".encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def _venue_age_days(conn, source_name: str) -> Optional[float]:
    ph = _ph()
    r = conn.execute(
        f"SELECT MIN(collected_at) AS m FROM raw_signals WHERE source_name = {ph}",
        (source_name,)).fetchone()
    m = (r["m"] if r and hasattr(r, "keys") else (r[0] if r else None))
    if not m:
        return None
    try:
        first = datetime.fromisoformat(str(m).replace("Z", "")).replace(
            tzinfo=timezone.utc)
    except Exception:
        return None
    return (datetime.now(timezone.utc) - first).total_seconds() / 86400.0


def _already_enrolled(conn) -> set:
    """Cross-arm exclusivity: every topic_key already in the shadow ledger, ANY arm."""
    try:
        rows = conn.execute("SELECT DISTINCT topic_key FROM shadow_ledger").fetchall()
    except Exception:
        return set()
    return {(r["topic_key"] if hasattr(r, "keys") else r[0]) for r in rows}


def _first_crossings(conn, feed_sets: list, cutoff_iso: str) -> list:
    """Topics first SEEN within ENROLL_RECENT_DAYS that are carried by the given feeds
    at expert/niche tier. Mirrors the real ledger's first-crossing enrollment: we are
    testing whether a feed surfaces something EARLY, so an already-established topic is
    not a race (the 2026-07-07 pre-broken lesson, applied at selection time)."""
    ph = _ph()
    tiers = ",".join([ph] * len(_D_TIERS))
    marks = ",".join([ph] * len(feed_sets))
    rows = conn.execute(
        f"SELECT ts.topic_key, MIN(ts.topic) AS topic, MIN(ts.extracted_at) AS first_seen,"
        f" COUNT(*) AS n, COUNT(DISTINCT ts.source_name) AS venues,"
        f" MIN(ts.source_name) AS a_source"
        f" FROM topic_signals ts"
        f" WHERE ts.platform_tier IN ({tiers}) AND ts.source_name IN ({marks})"
        f" GROUP BY ts.topic_key HAVING MIN(ts.extracted_at) >= {ph}",
        (*_D_TIERS, *feed_sets, cutoff_iso)).fetchall()
    # sqlite3.Row is not directly dict()-able across drivers; db_compat hands back
    # RealDictRow on PG and sqlite3.Row locally. Normalise explicitly rather than
    # relying on whichever driver happens to be live.
    out = []
    for r in rows:
        if hasattr(r, "keys"):
            out.append({k: r[k] for k in r.keys()})
        else:
            out.append({"topic_key": r[0], "topic": r[1], "first_seen": r[2],
                        "n": r[3], "venues": r[4], "a_source": r[5]})
    return out


def enroll_cycle(*, feed_map: dict, control_sources: list,
                 cycle_date: Optional[str] = None, db_path: str = DB_PATH,
                 dry_run: bool = False) -> dict:
    """Run ONE enrollment cycle across all four arms.

    `feed_map`: {feed_set_id: [stored source_name, ...]} — feed_set ids must be in
    shadow_ledger.SEALED_FEED_SETS or enroll() refuses them.
    `control_sources`: stored source_names of the EXISTING roster (the control arm).

    Returns a per-arm summary. `dry_run=True` selects and reports without writing, so the
    selection can be inspected before the window opens.
    """
    cycle_date = cycle_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rng = _cycle_seed(cycle_date)
    cutoff = (datetime.now(timezone.utc)
              - timedelta(days=ENROLL_RECENT_DAYS)).strftime("%Y-%m-%dT%H:%M:%S")
    conn = db_compat.connect(db_path)
    out = {"cycle_date": cycle_date, "dry_run": dry_run, "arms": {},
           "prereg": sl.PREREG_DOC, "seed_basis": "prereg_text_sha256|cycle_date"}
    try:
        taken = _already_enrolled(conn)          # cross-arm exclusivity, ledger-wide

        def _enroll(arm, cand, feed_set, domain):
            """One row, with the calibrating stamp computed from venue age."""
            if cand["topic_key"] in taken:
                return None
            age = _venue_age_days(conn, cand.get("a_source") or "")
            calibrating = 1 if (age is not None and age < CALIBRATING_DAYS) else 0
            taken.add(cand["topic_key"])
            if dry_run:
                return {"topic_key": cand["topic_key"], "calibrating": calibrating}
            rid = sl.enroll(
                arm=arm, feed_set=feed_set, domain=domain,
                topic_key=cand["topic_key"],
                topic_display=cand.get("topic") or cand["topic_key"],
                detection_date=str(cand.get("first_seen"))[:10],
                instrument_epoch="", regime=f"cycle={cycle_date}",
                signals_at_enroll=int(cand.get("n") or 0),
                venues_at_enroll=int(cand.get("venues") or 0),
                calibrating=calibrating, db_path=db_path)
            return {"topic_key": cand["topic_key"], "row": rid,
                    "calibrating": calibrating}

        # ── PARTITION FIRST, THEN FILL (board 2026-08-20 late — FATAL defect found
        # independently by the Statistician, Economist, Forecaster and Guardian, and
        # reproduced by probe: candidate 30 / null_random 0 / null_volume 0).
        # The first cut enrolled EVERY candidate before building the nulls, adding each
        # topic to `taken` — so `pool = [c for c in cand_all if c not in taken]` was
        # empty BY CONSTRUCTION. Cross-arm exclusivity, applied in enrollment order,
        # annihilated the very nulls it was written to protect, and the trial's firing
        # condition (beat BOTH nulls at N>=20) became unreachable rather than unlikely.
        # Exclusivity is now a property of a PARTITION computed before any arm enrolls,
        # never of the order in which arms are filled.
        # ALLOCATION BIAS also fixed: drawing candidate first deterministically gave the
        # arm-under-test every topic that overlapped the control roster — and overlap
        # topics have broader supply, hence higher breakout probability.
        cand_all = []
        for feed_set, sources in feed_map.items():
            for c in _first_crossings(conn, sources, cutoff):
                c["_feed_set"] = feed_set
                c["_domain"] = _DOMAIN_OF.get(feed_set, "unknown")
                cand_all.append(c)
        # Deterministic split of the SAME pool: seeded from the sealed prereg hash +
        # cycle date, so anyone holding the prereg reproduces this exact partition.
        eligible = [c for c in cand_all if c["topic_key"] not in taken]
        eligible.sort(key=lambda c: c["topic_key"])      # stable base order before shuffle
        rng.shuffle(eligible)
        half = len(eligible) // 2
        cand_slice = eligible[:half] if half else eligible[:1]
        null_slice = eligible[half:]

        cand_rows = [r for r in (_enroll("candidate", c, c["_feed_set"], c["_domain"])
                                 for c in cand_slice) if r]
        out["arms"]["candidate"] = {"enrolled": len(cand_rows),
                                    "calibrating": sum(r["calibrating"] for r in cand_rows)}

        # ── control: the existing roster, identical rules ────────────────────────
        ctrl_found = _first_crossings(conn, control_sources, cutoff)
        ctrl_rows = [r for r in (_enroll("control", c, "existing-roster", "mixed")
                                 for c in ctrl_found) if r]
        out["arms"]["control"] = {"enrolled": len(ctrl_rows),
                                  "calibrating": sum(r["calibrating"] for r in ctrl_rows)}

        # ── null_random: the OTHER half of the partition, no signal logic ────────
        # PROVENANCE FIX (Forecaster): null rows keep their TRUE feed_set and domain.
        # Recording a topic drawn from Marca as "existing-roster/mixed" is a
        # misstatement in the row itself, and it destroys §5's per-domain
        # stratification permanently — rows are immutable.
        n_draw = int(round(len(cand_rows) * NULL_RANDOM_RATIO)) or len(null_slice)
        nr_rows = [r for r in (_enroll("null_random", c, c["_feed_set"], c["_domain"])
                               for c in null_slice[:n_draw]) if r]
        out["arms"]["null_random"] = {"enrolled": len(nr_rows), "draw_target": n_draw,
                                      "pool": len(null_slice)}

        # ── null_volume: the dumb-volume rule over the UNCLAIMED remainder ───────
        nv_pool = [c for c in null_slice[n_draw:]
                   if int(c.get("n") or 0) >= NULL_VOLUME_K
                   and c["topic_key"] not in taken]
        nv_rows = [r for r in (_enroll("null_volume", c, c["_feed_set"], c["_domain"])
                               for c in nv_pool) if r]
        out["arms"]["null_volume"] = {"enrolled": len(nv_rows), "k": NULL_VOLUME_K,
                                      "pool": len(nv_pool)}
        # ZERO-ARM DISCLOSURE (Forecaster §4): an arm with no rows must read N=0, never
        # be absent — absence in a report is the §15a floor-end sin inside the
        # instrument built to police it.
        for _arm in ARMS_ALL:
            out["arms"].setdefault(_arm, {"enrolled": 0, "note": "N=0 — NO-TEST"})
        return out
    finally:
        try:
            conn.close()
        except Exception:
            pass


# feed_set -> domain, per the sealed prereg §6 table.
_DOMAIN_OF = {
    "marca-es": "sports", "kicker-de": "sports",
    "nikkei-asia": "geopolitics", "scmp-hk": "geopolitics",
    "stat-health": "health", "deadline-ent": "entertainment",
    "scialert-sci": "science", "existing-roster": "mixed",
}
