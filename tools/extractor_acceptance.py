# -*- coding: utf-8 -*-
"""STANDING §16 GATE-3 (FORMAT) ACCEPTANCE HARNESS — extractor precision/recall.

Board-ordered 2026-08-20 (Dark Matter convening, decision item 7; the FORMAT gate has
failed three times — NBER, the football desks, and the sports_entity draft filler list —
and each failure was caught by an ad-hoc manual comparison). This harness makes the
comparison a checked-in, repeatable fixture: ANY new domain roster or extractor change
runs it BEFORE wiring, and its output is the acceptance document.

Usage:
    python tools/extractor_acceptance.py                 # run the labeled fixture corpus
    python tools/extractor_acceptance.py --live URL NAME # fetch a live RSS feed and show
                                                         # extraction side-by-side (no
                                                         # labels -> eyeball mode)

The fixture corpus below is HAND-LABELED: for each headline, the entities a careful human
reader would want tracked. Precision = extracted∩expected / extracted;
Recall = extracted∩expected / expected. The harness reports per-extractor, per-headline,
and aggregate. It runs the generic n-gram extractor, research_entity, and sports_entity
side by side, each followed by the serve-time quality gate exactly as production applies it
(from_entity_run=True for the entity extractors — matching collect_medium/collect_ghost).

Read-only: touches no database, writes no file.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "transfer"))

import blog_collectors as bc                     # noqa: E402
import gravitational_anomaly_detector as g       # noqa: E402

# ── Hand-labeled fixture corpus ─────────────────────────────────────────────────
# (headline, expected entities). Expected = what a tracking product should extract;
# lowercase; club/person/competition/place names. Labels chosen BEFORE reading any
# extractor's output on them (the football post-mortem + gate-3 session corpus).
SPORTS_CORPUS = [
    ("Arsenal agree £51m deal to sign Ezri Konsa from Aston Villa",
     {"arsenal", "ezri konsa", "aston villa"}),
    ("Liverpool sign Bundesliga star in £70m deal",
     {"liverpool", "bundesliga"}),
    ("Chelsea appoint new sporting director after summer overhaul",
     {"chelsea"}),
    ("Manchester City target Roma's Manu Koné as Spurs talk over Savinho",
     {"manchester city", "roma", "manu koné", "spurs", "savinho"}),
    ("Mourinho says Real Madrid did not want Rodri after hesitation over move",
     {"mourinho", "real madrid", "rodri"}),
    ("Fifth Fifa vice-president turns against Infantino saying he must go",
     {"fifa", "infantino"}),
    ("England beat Spain to win the World Cup final in Mexico",
     {"england", "spain", "world cup", "mexico"}),
    ("Kylian Mbappé scores twice as Real Madrid beat Barcelona",
     {"kylian mbappé", "real madrid", "barcelona"}),
    ("Premier League 2026-27 preview No 18: Nottingham Forest",
     {"premier league", "nottingham forest"}),
    ("Can a managerial merry-go-round in Serie A stop Inter's dominance?",
     {"serie a", "inter"}),
    ("West Ham condemn 'offensive and divisive' chant about Israel winger Manor Solomon",
     {"west ham", "israel", "manor solomon"}),
    ("PSG's Ligue 1 home opener moved to Rennes after pitch damaged by heat",
     {"psg", "ligue 1", "rennes"}),
]

RESEARCH_CORPUS = [
    ("Gathering clouds building over the Taiwan Strait", {"taiwan strait"}),
    ("Q&A with Jane Smith on nuclear posture", set()),          # staff Q&A → nothing
    ("Breaking America: how Temu won the Maldives", {"america", "temu", "maldives"}),
    ("Ukraine's drone war enters a new phase", {"ukraine"}),
    ("What Pakistan's crackdown means for the region", {"pakistan"}),
]


def _extract(kind, title):
    if kind == "generic":
        return bc.extract_topics(title)
    if kind == "research":
        return bc.research_entity_topics(title)
    if kind == "sports":
        return bc.sports_entity_topics(title)
    raise ValueError(kind)


def _gate(kind, topics):
    exempt = kind in ("research", "sports")
    return [t for t in topics if g._is_quality_topic(t, from_entity_run=exempt)]


def run_corpus(name, corpus, extractors):
    print("=" * 84)
    print(f"CORPUS: {name}  ({len(corpus)} labeled headlines)")
    print("=" * 84)
    agg = {k: {"tp": 0, "fp": 0, "fn": 0} for k in extractors}
    for title, expected in corpus:
        print(f"\n  {title[:80]}")
        print(f"    expected: {sorted(expected) if expected else '(none)'}")
        for k in extractors:
            got = set(_gate(k, _extract(k, title)))
            tp = len(got & expected)
            fp = len(got - expected)
            fn = len(expected - got)
            agg[k]["tp"] += tp
            agg[k]["fp"] += fp
            agg[k]["fn"] += fn
            missed = sorted(expected - got)
            junk = sorted(got - expected)
            print(f"    {k:9} -> {sorted(got) if got else '(none)'}"
                  + (f"   MISSED={missed}" if missed else "")
                  + (f"   JUNK={junk}" if junk else ""))
    print("\n  AGGREGATE:")
    results = {}
    for k in extractors:
        a = agg[k]
        prec = a["tp"] / (a["tp"] + a["fp"]) if (a["tp"] + a["fp"]) else float("nan")
        rec = a["tp"] / (a["tp"] + a["fn"]) if (a["tp"] + a["fn"]) else float("nan")
        results[k] = (prec, rec)
        print(f"    {k:9} precision={prec:5.1%}  recall={rec:5.1%}  "
              f"(tp={a['tp']} fp={a['fp']} fn={a['fn']})")
    return results


def run_live(url, name):
    ua = {"User-Agent": "Mozilla/5.0 (compatible; NowTrendIn/2.0; "
                        "+https://abelcesq.github.io/nowtrendin-v2.0/)"}
    raw = urllib.request.urlopen(
        urllib.request.Request(url, headers=ua), timeout=25).read().decode("utf-8", "replace")
    titles = [re.sub(r"\s+", " ", t).strip() for t in
              re.findall(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", raw, re.S)][1:13]
    print(f"LIVE FEED: {name} — {len(titles)} titles (eyeball mode, no labels)")
    for t in titles:
        print(f"\n  {t[:84]}")
        for k in ("generic", "research", "sports"):
            got = _gate(k, _extract(k, t))
            print(f"    {k:9} -> {got}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", nargs=2, metavar=("URL", "NAME"))
    args = ap.parse_args()
    if args.live:
        run_live(*args.live)
        return
    run_corpus("SPORTS (hand-labeled)", SPORTS_CORPUS, ("generic", "sports"))
    print()
    run_corpus("RESEARCH/EDITORIAL (hand-labeled)", RESEARCH_CORPUS, ("generic", "research"))


if __name__ == "__main__":
    main()
