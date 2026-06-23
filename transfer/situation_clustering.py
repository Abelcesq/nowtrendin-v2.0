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


# ── 3. Build situations ─────────────────────────────────────────────────────────
def build_situations(signal_topics: dict, first_seen: Optional[dict] = None,
                     min_pair_docs: int = 3, min_jaccard: float = 0.18) -> list[dict]:
    """Cluster co-occurring topics into situations. `first_seen` (topic_key → ISO date)
    lets each situation carry its EARLIEST member first-seen (the situation-level discovery
    date). Returns [{situation, members, anchor, doc_freq, first_seen}] sorted by size."""
    doc_freq, pair_docs = cooccurrence(signal_topics)
    edges = jaccard_edges(doc_freq, pair_docs, min_pair_docs, min_jaccard)
    nodes = set(doc_freq)
    clusters = _cluster(nodes, edges)
    out = []
    for c in clusters:
        anchor = max(c, key=lambda t: doc_freq.get(t, 0))   # most-covered member = the label
        sit = {
            "situation": anchor,
            "anchor": anchor,
            "members": sorted(c, key=lambda t: -doc_freq.get(t, 0)),
            "size": len(c),
            "member_doc_freq": {t: doc_freq.get(t, 0) for t in c},
        }
        if first_seen:
            seen = [first_seen[t] for t in c if first_seen.get(t)]
            if seen:
                sit["first_seen"] = min(seen)                # situation discovery = earliest facet
                sit["first_seen_by_member"] = {t: first_seen.get(t) for t in c}
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

if __name__ == "__main__":
    import json
    # Realistic co-occurrence: Middle-East situation + an unrelated AI situation, plus a
    # popular topic ("ai") that touches many docs (must NOT glue the two together).
    signal_topics = {
        "d1": ["iran", "strait of hormuz", "nuclear", "us"],
        "d2": ["oil", "iran", "strait of hormuz", "oil prices"],
        "d3": ["us", "iran", "nuclear", "peace talks"],
        "d4": ["iran", "oil", "strait of hormuz", "blockade"],
        "d5": ["nuclear", "iran", "us", "peace talks"],
        "d6": ["oil prices", "oil", "iran", "blockade"],
        "d7": ["openai", "diffusion models", "ai"],
        "d8": ["diffusion models", "world models", "ai"],
        "d9": ["openai", "world models", "deepseek", "ai"],
        "d10": ["deepseek", "diffusion models", "ai"],
        "d11": ["world models", "openai", "ai"],
        "d12": ["us", "ai"],   # a stray cross-link — normalization should keep clusters apart
    }
    first_seen = {"iran": "2026-06-01", "nuclear": "2026-06-02", "us": "2026-06-01",
                  "oil": "2026-06-04", "strait of hormuz": "2026-06-09", "hormuz": "2026-06-09",
                  "peace talks": "2026-06-05", "oil prices": "2026-06-06", "blockade": "2026-06-08",
                  "openai": "2026-05-20", "diffusion models": "2026-05-22"}
    sits = build_situations(signal_topics, first_seen=first_seen)
    for s in sits:
        print(json.dumps({k: s[k] for k in ("situation", "members", "first_seen")
                          if k in s}, ensure_ascii=False))
