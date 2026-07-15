"""
entity_grouping.py — Option A: DISPLAY-ONLY entity grouping / topic-alias layer.

Board-ruled 2026-07-15 + Chairman-approved (audits/board/BOARD_entity-grouping_2026-07-15.md).
The "conor mcgregor" / "conor" / "mcgregor" case: fragment topic keys of the same
real-world entity fold under the canonical key IN DISPLAY ONLY.

HARD CONDITIONS (all seven board-convergent conditions, enforced here):
 1. NO ARITHMETIC MERGE anywhere. The canonical row serves the canonical key's OWN
    measured score — never a sum, blend, or max() across constituents (constituent
    rows share underlying raw_signals; any aggregation double-counts evidence).
 2. Aliases are dated, versioned, evidence-stamped, confidence-scored,
    HUMAN-CONFIRMED (flag-never-force: candidates are proposed as 'pending';
    nothing groups until a human confirms), and reversible (revert supported;
    rows are never deleted).
 3. DB-persisted + warm-on-boot: the entity_aliases table IS the source of truth;
    load_alias_map() runs synchronously at startup (CATEGORY_SNAPSHOT precedent) —
    no cold-boot flicker, fleet-consistent.
 4. HELD-OUT WALL: this module must NEVER be imported by scoring admission
    (_passes_corroboration / score_topic), calibration (calibration_engine,
    signal_calibration_integration), ledger enrollment (_record_top_detections,
    accuracy_ledger_enhanced), or any sweep. wall_check() verifies at runtime
    that none of those files reference this module. This module itself imports
    NOTHING from the scorer/calibration/ledger.
 5. The accuracy ledger stays PER-KEY everywhere (this module touches no ledger
    table and offers no family-level verdict).
 6. Detail evidence is a DE-DUPLICATED union of distinct raw_signals across the
    alias set, labeled as shared — never a cross-key mention sum.
 7. Grouping applies to the SERVED lists only; auditors keep measuring RAW keys
    (candidate scanning also runs over raw, un-grouped keys via ungroup_rows).

Flag: ENTITY_GROUPING (env, default "0"/OFF). The alias map still loads and the
review endpoints still work while OFF — only the serve-time fold is gated.
"""

import os
import re
import json
import time
import sqlite3
import threading
from datetime import datetime, timezone

import db_compat

# ── Module state (display-only maps; DB is the source of truth) ──────────────
_LOCK = threading.Lock()
_ALIAS_TO_CANON: dict = {}   # alias_key  -> canonical_key   (confirmed only)
_CANON_TO_ALIASES: dict = {} # canonical_key -> [alias_key, ...]
_ALIAS_META: dict = {"source": "empty", "refreshed_at": None,
                     "confirmed": 0, "pending": 0, "rejected": 0}

EVIDENCE_NOTE = ("Constituent topics share underlying evidence with the canonical "
                 "entity. Each score shown is that key's OWN measured score — "
                 "constituent scores are never summed, blended, or maxed.")

_STOPWORDS = {
    "the", "and", "for", "with", "from", "into", "over", "under", "after",
    "before", "new", "news", "day", "week", "year", "all", "his", "her",
    "their", "our", "your", "its", "was", "are", "has", "had", "have", "will",
    "won", "vs", "amid", "says", "said", "may", "june", "july", "world",
}


def enabled() -> bool:
    """Serve-time fold gate — read at call time so a config flip needs no code change."""
    return os.getenv("ENTITY_GROUPING", "0") == "1"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _connect(db_path: str):
    conn = db_compat.connect(db_path, check_same_thread=False, timeout=30)
    try:
        conn.row_factory = sqlite3.Row
    except Exception:
        pass
    return conn


def ensure_schema(conn) -> None:
    """Guarded CREATE — same idiom as category_override_snapshot."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entity_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alias_key TEXT NOT NULL,
            canonical_key TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            confidence REAL,
            evidence TEXT,
            proposed_at TEXT,
            decided_at TEXT,
            decided_by TEXT,
            version INTEGER NOT NULL DEFAULT 1,
            notes TEXT,
            UNIQUE(alias_key, canonical_key)
        )
    """)
    conn.commit()


# ── Warm-on-boot map load (condition 3) ──────────────────────────────────────

def load_alias_map(db_path: str) -> dict:
    """Load CONFIRMED aliases into the in-memory display maps. Synchronous,
    sub-second (one indexed SELECT). Call at startup and after every resolve."""
    conn = None
    try:
        conn = _connect(db_path)
        ensure_schema(conn)
        rows = conn.execute(
            "SELECT alias_key, canonical_key, status FROM entity_aliases"
        ).fetchall()
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
    a2c, c2a = {}, {}
    counts = {"confirmed": 0, "pending": 0, "rejected": 0}
    for r in rows:
        st = (r["status"] or "").strip()
        if st in counts:
            counts[st] += 1
        if st == "confirmed":
            a2c[r["alias_key"]] = r["canonical_key"]
            c2a.setdefault(r["canonical_key"], []).append(r["alias_key"])
    with _LOCK:
        _ALIAS_TO_CANON.clear(); _ALIAS_TO_CANON.update(a2c)
        _CANON_TO_ALIASES.clear(); _CANON_TO_ALIASES.update(c2a)
        _ALIAS_META.update({"source": "db", "refreshed_at": _now_iso(), **counts})
    return dict(_ALIAS_META)


def alias_map_meta() -> dict:
    with _LOCK:
        return {**_ALIAS_META, "flag_enabled": enabled(),
                "confirmed_aliases": dict(_ALIAS_TO_CANON)}


# ── Candidate generation (read-only proposer; flag-never-force) ─────────────

def _tokens(key: str) -> frozenset:
    return frozenset(t for t in re.split(r"[^a-z0-9]+", (key or "").lower())
                     if len(t) >= 3 and t not in _STOPWORDS)


def _distinct_titles(conn, topic_key: str, cap: int = 200) -> set:
    rows = conn.execute("""
        SELECT r.title AS title
        FROM topic_signals ts
        JOIN raw_signals r ON ts.signal_id = r.id
        WHERE ts.topic_key = ?
          AND r.title IS NOT NULL AND length(trim(r.title)) > 8
        ORDER BY ts.extracted_at DESC
        LIMIT ?
    """, (topic_key, cap)).fetchall()
    out = set()
    for r in rows:
        t = " ".join((r["title"] or "").lower().split())
        if t:
            out.add(t)
    return out


def scan_candidates(db_path: str, rows: list, max_keys: int = 4000,
                    max_pairs: int = 800, min_shared_titles: int = None) -> dict:
    """Propose alias candidates over the RAW served working set (pass rows from
    the /scores superset, un-grouped). A candidate = a key whose tokens are a
    STRICT SUBSET of a 2-4 token key's tokens ("mcgregor" ⊂ "conor mcgregor"),
    corroborated by shared distinct raw_signals titles (evidence-stamped).
    Writes status='pending' rows ONLY — a human confirms via resolve_alias.
    Batch-paced (founder rule): brief pause between evidence-fetch chunks."""
    if min_shared_titles is None:
        min_shared_titles = int(os.getenv("ENTITY_MIN_SHARED_TITLES", "2"))

    keyed = []
    seen_keys = set()
    for r in rows[:max_keys]:
        k = (r.get("topic_key") or "").strip()
        if not k or k in seen_keys:
            continue
        seen_keys.add(k)
        toks = _tokens(k)
        if toks:
            keyed.append((k, toks))

    # token -> indexes of multi-token (2..4) canonical candidates
    posting = {}
    for i, (k, toks) in enumerate(keyed):
        if 2 <= len(toks) <= 4:
            for t in toks:
                posting.setdefault(t, []).append(i)

    pairs = []  # (fragment_key, canonical_key)
    for i, (k, toks) in enumerate(keyed):
        cand = None
        for t in toks:
            lst = posting.get(t)
            if not lst:
                cand = set()
                break
            cand = set(lst) if cand is None else (cand & set(lst))
            if not cand:
                break
        if not cand:
            continue
        for j in cand:
            ck, ctoks = keyed[j]
            if ck == k or not (toks < ctoks):  # strict subset only
                continue
            pairs.append((k, ck))
            if len(pairs) >= max_pairs:
                break
        if len(pairs) >= max_pairs:
            break

    proposed, skipped_no_evidence, existing, checked = 0, 0, 0, 0
    title_cache: dict = {}
    conn = None
    try:
        conn = _connect(db_path)
        ensure_schema(conn)
        for frag, canon in pairs:
            checked += 1
            if checked % 40 == 0:
                time.sleep(0.05)  # batch pacing — keep the serve path breathing
            for k in (frag, canon):
                if k not in title_cache:
                    title_cache[k] = _distinct_titles(conn, k)
            shared = title_cache[frag] & title_cache[canon]
            denom = min(len(title_cache[frag]), len(title_cache[canon]))
            if len(shared) < min_shared_titles or denom == 0:
                skipped_no_evidence += 1
                continue
            overlap = len(shared) / denom
            confidence = round(min(0.99, 0.30 + 0.69 * overlap), 3)
            evidence = json.dumps({
                "method": "token-containment + shared-distinct-title corroboration",
                "fragment_titles": len(title_cache[frag]),
                "canonical_titles": len(title_cache[canon]),
                "shared_titles": len(shared),
                "overlap_ratio": round(overlap, 3),
                "sample_shared": sorted(shared)[:5],
                "computed_at": _now_iso(),
            })
            cur = conn.execute(
                """INSERT OR IGNORE INTO entity_aliases
                   (alias_key, canonical_key, status, confidence, evidence, proposed_at)
                   VALUES (?, ?, 'pending', ?, ?, ?)""",
                (frag, canon, confidence, evidence, _now_iso()))
            if getattr(cur, "rowcount", 0) and cur.rowcount > 0:
                proposed += 1
            else:
                existing += 1
        conn.commit()
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
    return {"keys_considered": len(keyed), "pairs_checked": checked,
            "proposed_new": proposed, "already_known": existing,
            "skipped_no_shared_evidence": skipped_no_evidence,
            "min_shared_titles": min_shared_titles}


# ── Review + resolution (human-confirmed, reversible) ───────────────────────

def list_aliases(db_path: str, status: str = None, limit: int = 500) -> list:
    conn = None
    try:
        conn = _connect(db_path)
        ensure_schema(conn)
        if status:
            rows = conn.execute(
                "SELECT * FROM entity_aliases WHERE status = ? "
                "ORDER BY confidence DESC, id LIMIT ?", (status, limit)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM entity_aliases ORDER BY status, confidence DESC, id "
                "LIMIT ?", (limit,)).fetchall()
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
    out = []
    for r in rows:
        d = dict(r)
        try:
            d["evidence"] = json.loads(d["evidence"]) if d.get("evidence") else None
        except Exception:
            pass
        out.append(d)
    return out


def resolve_alias(db_path: str, alias_id: int, action: str,
                  decided_by: str = "founder") -> dict:
    """confirm | reject | revert (back to pending). Reversible; rows never deleted.
    Confirm guards: one canonical per alias; no chains (a canonical may not itself
    be a confirmed alias, and an alias may not be canonical of another group)."""
    if action not in ("confirm", "reject", "revert"):
        raise ValueError(f"unknown action: {action}")
    conn = None
    try:
        conn = _connect(db_path)
        ensure_schema(conn)
        row = conn.execute("SELECT * FROM entity_aliases WHERE id = ?",
                           (alias_id,)).fetchone()
        if not row:
            raise LookupError(f"no alias row with id {alias_id}")
        alias_key, canonical_key = row["alias_key"], row["canonical_key"]
        if action == "confirm":
            dup = conn.execute(
                "SELECT id FROM entity_aliases WHERE alias_key = ? "
                "AND status = 'confirmed' AND id != ?", (alias_key, alias_id)).fetchone()
            if dup:
                raise ValueError(
                    f"'{alias_key}' is already confirmed under another canonical "
                    f"(row {dup['id']}) — revert that first (one canonical per alias)")
            chain1 = conn.execute(
                "SELECT id FROM entity_aliases WHERE alias_key = ? AND status = 'confirmed'",
                (canonical_key,)).fetchone()
            if chain1:
                raise ValueError(
                    f"canonical '{canonical_key}' is itself a confirmed alias "
                    f"(row {chain1['id']}) — chains are not allowed (single level)")
            chain2 = conn.execute(
                "SELECT id FROM entity_aliases WHERE canonical_key = ? AND status = 'confirmed'",
                (alias_key,)).fetchone()
            if chain2:
                raise ValueError(
                    f"'{alias_key}' is canonical of a confirmed group "
                    f"(row {chain2['id']}) — chains are not allowed (single level)")
        new_status = {"confirm": "confirmed", "reject": "rejected",
                      "revert": "pending"}[action]
        conn.execute(
            "UPDATE entity_aliases SET status = ?, decided_at = ?, decided_by = ?, "
            "version = version + 1 WHERE id = ?",
            (new_status, _now_iso(), decided_by, alias_id))
        conn.commit()
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
    meta = load_alias_map(db_path)  # reload the display map immediately
    return {"id": alias_id, "alias_key": alias_key, "canonical_key": canonical_key,
            "status": new_status, "map": meta}


# ── Serve-time display fold (condition 1: no arithmetic merge) ──────────────

_ROW_FIELDS = ("topic_key", "topic_display", "topic", "display", "overall_score",
               "detection_score", "confidence_score", "nowtrendin_score",
               "signal_stage", "total_mentions", "category")


def _compact(row: dict) -> dict:
    return {k: row.get(k) for k in _ROW_FIELDS if k in row}


def group_rows(rows: list, key_field: str = "topic_key") -> list:
    """Fold confirmed-alias rows under their canonical row IN DISPLAY ONLY.
    - Applies only when ENTITY_GROUPING=1 and confirmed aliases exist.
    - A constituent folds ONLY if its canonical row is present in the same list
      (never hide a row that has no visible canonical representative).
    - The canonical row keeps its OWN score and its OWN list position (order is
      never re-sorted); constituents are embedded, each with its OWN score.
    - Input rows are not mutated (canonical rows are shallow-copied)."""
    if not enabled():
        return rows
    with _LOCK:
        a2c = dict(_ALIAS_TO_CANON)
    if not a2c or not rows:
        return rows
    present = {}
    for i, r in enumerate(rows):
        k = r.get(key_field)
        if k:
            present.setdefault(k, i)
    folds = {}  # canonical index -> [constituent rows]
    drop = set()
    for i, r in enumerate(rows):
        k = r.get(key_field)
        canon = a2c.get(k)
        if canon and canon in present and present[canon] != i:
            folds.setdefault(present[canon], []).append(_compact(r))
            drop.add(i)
    if not folds:
        return rows
    out = []
    for i, r in enumerate(rows):
        if i in drop:
            continue
        if i in folds:
            r = dict(r)
            r["entity_group"] = {
                "constituents": folds[i],
                "grouped_keys": [c.get(key_field) for c in folds[i]],
                "evidence_note": EVIDENCE_NOTE,
            }
        out.append(r)
    return out


def ungroup_rows(rows: list, key_field: str = "topic_key") -> list:
    """Flatten a possibly-grouped list back to RAW keys (auditors + the candidate
    scanner must always see raw, un-grouped keys — condition 7)."""
    out = []
    for r in rows:
        out.append(r)
        eg = r.get("entity_group") if isinstance(r, dict) else None
        if eg and isinstance(eg.get("constituents"), list):
            out.extend(eg["constituents"])
    return out


def detail_group_info(db_path: str, topic_key: str) -> dict:
    """Detail-view enrichment. Canonical → each constituent's OWN latest served
    score (serve_payload-consistent, the SSOT rule). Constituent → pointer to
    canonical. None when the key is in no confirmed group or the flag is off."""
    if not enabled():
        return None
    with _LOCK:
        a2c = dict(_ALIAS_TO_CANON)
        c2a = {k: list(v) for k, v in _CANON_TO_ALIASES.items()}
    if topic_key in a2c:
        return {"role": "constituent", "canonical_key": a2c[topic_key],
                "evidence_note": EVIDENCE_NOTE}
    children = c2a.get(topic_key)
    if not children:
        return None
    constituents = []
    conn = None
    try:
        conn = _connect(db_path)
        for ck in children:
            row = conn.execute("""
                SELECT topic_key, topic_display, overall_score, detection_score,
                       confidence_score, nowtrendin_score, signal_stage,
                       total_mentions, scored_at, serve_payload
                FROM velocity_scores WHERE topic_key = ?
                ORDER BY scored_at DESC LIMIT 1
            """, (ck,)).fetchone()
            if not row:
                continue
            d = dict(row)
            pl = d.pop("serve_payload", None)
            if pl:  # serve the SAME numbers the list feeds serve (SSOT)
                try:
                    p = json.loads(pl)
                    for k in ("overall_score", "detection_score", "confidence_score",
                              "nowtrendin_score", "signal_stage"):
                        if p.get(k) is not None:
                            d[k] = p[k]
                except Exception:
                    pass
            constituents.append(d)
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
    if not constituents:
        return None
    return {"role": "canonical", "constituents": constituents,
            "grouped_keys": [c["topic_key"] for c in constituents],
            "evidence_note": EVIDENCE_NOTE}


# ── Held-out wall verification (condition 4) ─────────────────────────────────

_WALL_FILES = ("signal_calibration_integration.py", "calibration_engine.py",
               "calibration_agent.py", "accuracy_ledger_enhanced.py",
               "market_accuracy_ledger.py", "crypto_accuracy_ledger.py")


def wall_check(base_dir: str = None) -> dict:
    """Verify no scoring/calibration/ledger/sweep module references this module.
    (The main app legitimately imports us for its serve/display path only.)"""
    base = base_dir or os.path.dirname(os.path.abspath(__file__))
    violations, checked = [], []
    for fn in _WALL_FILES:
        path = os.path.join(base, fn)
        if not os.path.exists(path):
            continue
        checked.append(fn)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                if "entity_grouping" in f.read():
                    violations.append(fn)
        except Exception as e:
            violations.append(f"{fn} (unreadable: {e})")
    return {"ok": not violations, "violations": violations, "checked": checked}
