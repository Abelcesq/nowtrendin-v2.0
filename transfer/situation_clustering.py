"""
situation_clustering.py — TOPICS, not words: assemble co-occurring topic fragments into
coherent SITUATIONS. (Research prototype / analysis layer — held-out, changes no score.)

THE PROBLEM (founder, 2026-06):
  The engine extracts word/phrase fragments per document ("hormuz", "iran", "nuclear",
  "oil") and consolidates them only by SPELLING (japanese→japan, an alias map). It has no
  notion that those four fragments are ONE real-world situation: the US–Iran conflict over
  nuclear capability → oil distribution → the Strait of Hormuz blockade. Tracking the lone
  word "hormuz" and asking where the context went is the "$1,000,000 → just the middle
  zero" error. We must calculate TOPICS (situations), not words.

THE ASSET WE ALREADY HAVE (no new data, no AI, no cost):
  topic_signals.signal_id is the FK to the source document. Every topic extracted from the
  SAME document shares a signal_id → CO-OCCURRENCE is already recorded. Topics that keep
  appearing in the same documents are facets of the same situation. This module turns that
  latent co-occurrence into explicit situation clusters.

WHY THIS RECONCILES THE DISCOVERY-LATENCY FINDING:
  A situation's "first seen" = the EARLIEST first-seen across ALL its member fragments. We
  may have surfaced "iran nuclear" on Jun-01 even though the specific word "hormuz" only
  appeared Jun-09 — so at the SITUATION level we discovered the story 8 days earlier. Word-
  level measurement undercounts how early we actually were. (Integrity caveat: this is a
  more honest measurement, NOT a way to back-date a miss — see GUARDRAILS at the bottom.)

METHOD (transparent, no black box):
  1. Co-occurrence counts from (signal_id → [topics]).
  2. Edge weight = JACCARD over the documents each pair appears in (so a frequent topic
     like "ai" doesn't glue everything together — normalized, not raw counts).
  3. Cluster = connected components over edges above a frozen threshold (union-find).
  4. Name = the highest-document-frequency member (the situation's anchor term).
  Deliberately simple + explainable; embeddings / LLM naming are an optional later layer.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Optional

try:
    from date_utils import to_iso_date
except Exception:
    def to_iso_date(s):
        return (str(s)[:10] if s else None)


# ── 1. Co-occurrence ────────────────────────────────────────────────────────────
def cooccurrence(signal_topics: dict) -> tuple[dict, dict]:
    """signal_topics: {signal_id: [topic_key, ...]} (topics sharing a signal_id co-occur).
    Returns (doc_freq, pair_docs): doc_freq[t] = # documents containing t;
    pair_docs[(a,b)] = # documents containing BOTH a and b (a<b)."""
    doc_freq = defaultdict(int)
    pair_docs = defaultdict(int)
    for _sig, topics in signal_topics.items():
        uniq = sorted(set(topics))
        for t in uniq:
            doc_freq[t] += 1
        for i in range(len(uniq)):
            for j in range(i + 1, len(uniq)):
                pair_docs[(uniq[i], uniq[j])] += 1
    return dict(doc_freq), dict(pair_docs)


def jaccard_edges(doc_freq: dict, pair_docs: dict,
                  min_pair_docs: int = 3, min_jaccard: float = 0.18) -> dict:
    """Edge weight = |A∩B| / |A∪B| over documents. Normalizing defeats the 'popular topic
    glues everything' failure of raw co-occurrence counts. Keep edges with enough joint
    support AND enough overlap (both frozen thresholds)."""
    edges = {}
    for (a, b), both in pair_docs.items():
        if both < min_pair_docs:
            continue
        union = doc_freq[a] + doc_freq[b] - both
        j = both / union if union else 0.0
        if j >= min_jaccard:
            edges[(a, b)] = round(j, 3)
    return edges


# ── 2. Cluster (union-find over the edges) ──────────────────────────────────────
def _cluster(nodes: set, edges: dict) -> list[set]:
    parent = {n: n for n in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for (a, b) in edges:
        if a in parent and b in parent:
            union(a, b)
    groups = defaultdict(set)
    for n in nodes:
        groups[find(n)].add(n)
    return [g for g in groups.values() if len(g) >= 2]


# ── 2b. Hub detection (the "japan" problem) ─────────────────────────────────────
# A hub is an entity (e.g. "japan") that co-occurs across SEVERAL otherwise-distinct
# situations — Belgium royal visit, BOJ rate hike, World Cup vs Sweden — and would
# otherwise GLUE them into one meaningless "japan" blob. We detect a hub as a node whose
# removal splits its own neighborhood into >=2 disconnected groups, then we CLUSTER WITHOUT
# hubs (so the situations separate by their distinguishing context) and RE-ATTACH each hub
# to every situation it touches, as a SHARED, SEARCHABLE ANCHOR — never a merger. This is
# what lets one searchable entity ("japan") fan out into multiple scoreable situations.
def _adjacency(edges: dict) -> dict:
    adj = defaultdict(set)
    for (a, b) in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def _components(nodes: set, adj: dict) -> list[set]:
    seen, comps = set(), []
    for n in nodes:
        if n in seen:
            continue
        stack, comp = [n], set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x); comp.add(x)
            for y in adj.get(x, ()):
                if y in nodes and y not in seen:
                    stack.append(y)
        comps.append(comp)
    return comps


def hub_nodes(nodes: set, edges: dict, min_degree: int = 3) -> set:
    """Entities whose removal fractures their neighborhood into >=2 groups = situation hubs."""
    adj = _adjacency(edges)
    hubs = set()
    for n in nodes:
        nb = adj.get(n, set())
        if len(nb) < min_degree:
            continue
        sub = defaultdict(set)
        for (a, b) in edges:
            if a == n or b == n:
                continue
            if a in nb and b in nb:
                sub[a].add(b); sub[b].add(a)
        if len(_components(nb, sub)) >= 2:
            hubs.add(n)
    return hubs


# ── 3. Build situations (hub-aware) ─────────────────────────────────────────────
def build_situations(signal_topics: dict, first_seen: Optional[dict] = None,
                     min_pair_docs: int = 3, min_jaccard: float = 0.18) -> list[dict]:
    """Cluster co-occurring topics into situations. `first_seen` (topic_key → ISO date)
    lets each situation carry its EARLIEST member first-seen (the situation-level discovery
    date). One ENTITY (hub, e.g. "japan") can anchor MULTIPLE situations; it is attached to
    each as a shared, searchable anchor, never merging them. Returns
    [{situation_key, label, anchor, core_members, shared_anchors, members, first_seen}]."""
    doc_freq, pair_docs = cooccurrence(signal_topics)
    edges = jaccard_edges(doc_freq, pair_docs, min_pair_docs, min_jaccard)
    nodes = set(doc_freq)
    hubs = hub_nodes(nodes, edges)
    # Cluster WITHOUT hubs so distinct situations separate by their distinguishing context.
    core_nodes = nodes - hubs
    core_edges = {e: w for e, w in edges.items() if e[0] not in hubs and e[1] not in hubs}
    cores = _cluster(core_nodes, core_edges)
    out = []
    for c in cores:
        # Re-attach every hub that connects to this core (shared anchor, not a merge).
        attached = sorted(
            {h for h in hubs if any((min(h, m), max(h, m)) in edges for m in c)},
            key=lambda t: -doc_freq.get(t, 0))
        core_sorted = sorted(c, key=lambda t: -doc_freq.get(t, 0))
        # Label: anchor entity + the most-distinguishing core term (the context that
        # separates THIS situation from the entity's other situations).
        top_core = core_sorted[0]
        anchor = attached[0] if attached else top_core
        label = f"{anchor} · {top_core}" if attached else top_core
        skey = (f"{anchor}__{top_core}" if attached else top_core).replace(" ", "_")
        members = core_sorted + attached
        sit = {
            "situation_key": skey,
            "label": label,
            "anchor": anchor,
            "core_members": core_sorted,       # the distinguishing context (what makes it THIS situation)
            "shared_anchors": attached,        # searchable entities shared with other situations
            "members": members,
            "size": len(members),
            "member_doc_freq": {t: doc_freq.get(t, 0) for t in members},
        }
        if first_seen:
            seen = [first_seen[t] for t in members if first_seen.get(t)]
            if seen:
                sit["first_seen"] = min(seen)              # situation discovery = earliest facet
                sit["first_seen_by_member"] = {t: first_seen.get(t) for t in members}
        out.append(sit)
    return sorted(out, key=lambda s: -s["size"])


# GUARDRAILS (integrity — this is an ADD-ON layer, not a rewrite of the score):
#   • The granular word/phrase topics are PRESERVED — they remain the unit of EARLY/niche
#     detection (the product thesis). Situations are an ADDITIONAL context layer, never a
#     replacement; we never lose the ability to see "diffusion models" spike on its own.
#   • Clusters come from REAL co-occurrence in real documents — never a guessed or
#     hand-asserted relationship. An unsupported link is not drawn.
#   • Situation-level first-seen is a more HONEST discovery measurement, but it does NOT
#     turn a genuine scoring miss into a win: if we were watching a situation before its
#     arrival and still scored it late, that stays LAGGED (the ledger gate is unchanged).
#   • Descriptive only — a situation is a measured grouping, not a prediction.

# ── 4. Phase A — build from the REAL corpus (held-out, READ-ONLY) ───────────────
def build_from_db(conn, window_hours: int = 120, min_doc_freq: int = 5,
                  min_pair_docs: int = 3, min_jaccard: float = 0.18,
                  max_signals: int = 120000, display_lookup: Optional[dict] = None,
                  quality_only: bool = True, registry_only: bool = True, gate=None) -> dict:
    """Assemble situations from REAL topic_signals co-occurrence over a rolling window.
    READ-ONLY: SELECTs topic_signals (+ topic_registry); writes NOTHING and touches no score.
    Topics sharing a signal_id co-occurred in the same source document. Long-tail one-off
    fragments (doc_freq < min) are dropped. QUALITY GATE: `quality_only` runs each topic
    through the engine's single shared `_is_quality_topic` (drops spam/boilerplate);
    `registry_only` requires the topic to be a real TRACKED entity (in topic_registry) —
    which structurally removes the multilingual SEO spam the vocabulary list can't enumerate.
    Returns {window_hours, documents, candidates, topics_kept, dropped_quality, situations}."""
    from datetime import datetime, timezone, timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=window_hours)).isoformat()

    def _val(r, i, k):
        return (r[k] if hasattr(r, "keys") else r[i])

    # 1. co-occurrence (topics per source document), most-recent-bounded for a fast preview
    rows = conn.execute(
        "SELECT signal_id, topic_key FROM topic_signals "
        "WHERE signal_id IS NOT NULL AND extracted_at >= ? "
        "ORDER BY extracted_at DESC LIMIT ?", (cutoff, int(max_signals))).fetchall()
    sig_topics = defaultdict(list)
    for r in rows:
        sid, tk = _val(r, 0, "signal_id"), _val(r, 1, "topic_key")
        if sid and tk:
            sig_topics[sid].append(tk)

    # 2. drop the long tail (one-off fragments) — candidates seen in >= min_doc_freq docs
    df = defaultdict(int)
    for tks in sig_topics.values():
        for t in set(tks):
            df[t] += 1
    candidates = {t for t, c in df.items() if c >= min_doc_freq}

    # 3. registry pass (first-seen + display + tracked-entity membership) for candidates
    first_seen, display, registered = {}, dict(display_lookup or {}), set()
    try:
        for r in conn.execute(
                "SELECT topic_key, first_seen_at, topic_display FROM topic_registry").fetchall():
            tk, fs, disp = _val(r, 0, "topic_key"), _val(r, 1, "first_seen_at"), _val(r, 2, "topic_display")
            if tk in candidates:
                registered.add(tk)
                if fs:
                    first_seen[tk] = to_iso_date(fs)
                if disp and tk not in display:
                    display[tk] = disp
    except Exception:
        pass

    # 4. QUALITY GATE — the engine's ONE shared gate (spam/boilerplate/fragments) + the
    #    tracked-entity requirement. Same function every scorer/agent uses, so the cluster
    #    layer can never disagree with what the rest of the engine considers a real topic.
    #    The caller passes `gate` directly (robust); fall back to import only if not given.
    if quality_only and gate is None:
        try:
            from gravitational_anomaly_detector import _is_quality_topic as gate
        except Exception:
            gate = None

    def _ok(t):
        if registry_only and t not in registered:
            return False
        if gate is not None and not gate(display.get(t) or t.replace("_", " ")):
            return False
        return True

    keep = {t for t in candidates if _ok(t)}
    pruned = {s: [t for t in set(tks) if t in keep] for s, tks in sig_topics.items()}
    pruned = {s: tks for s, tks in pruned.items() if len(tks) >= 2}

    sits = build_situations(pruned, first_seen={t: first_seen[t] for t in first_seen if t in keep},
                            min_pair_docs=min_pair_docs, min_jaccard=min_jaccard)
    for s in sits:
        s["label_display"] = " · ".join(
            display.get(m, m) for m in ([s["anchor"]] + s["core_members"][:1]))
    return {"window_hours": window_hours, "documents": len(pruned),
            "candidates": len(candidates), "topics_kept": len(keep),
            "dropped_quality": len(candidates) - len(keep),
            "situation_count": len(sits), "situations": sits}


if __name__ == "__main__":
    import json
    # The "japan" problem: ONE entity, THREE distinct situations across THREE categories.
    # "japan" co-occurs with all of them and must NOT glue them into one blob — it stays a
    # shared, searchable anchor while the three situations score separately.
    signal_topics = {
        # Politics — royal visit to Belgium
        "p1": ["japan", "belgium", "naruhito", "royal visit"],
        "p2": ["japan", "belgium", "naruhito", "masako", "state visit"],
        "p3": ["japan", "belgium", "royal visit", "masako"],
        # Economics — Bank of Japan rate hike
        "e1": ["japan", "bank of japan", "interest rate", "monetary policy"],
        "e2": ["japan", "bank of japan", "interest rate", "inflation"],
        "e3": ["japan", "monetary policy", "interest rate", "bank of japan"],
        # Sports — World Cup vs Sweden
        "w1": ["japan", "sweden", "world cup"],
        "w2": ["japan", "sweden", "world cup", "match"],
        "w3": ["japan", "world cup", "sweden", "knockout"],
    }
    first_seen = {"japan": "2026-06-01", "belgium": "2026-06-08", "naruhito": "2026-06-09",
                  "bank of japan": "2026-06-18", "interest rate": "2026-06-18",
                  "sweden": "2026-06-20", "world cup": "2026-06-12"}
    print("Search 'japan' resolves to these distinct, separately-scoreable situations:\n")
    for s in build_situations(signal_topics, first_seen=first_seen, min_pair_docs=2):
        print(f"  • {s['label']:24}  key={s['situation_key']:22} "
              f"context={s['core_members']}  anchors={s['shared_anchors']}  "
              f"first_seen={s.get('first_seen')}")
