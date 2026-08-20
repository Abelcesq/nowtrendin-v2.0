# sports_entity extractor — §16 gate-3 ACCEPTANCE DOCUMENT
### 2026-08-20 · closes the missing-document finding from the nine-seat D board (Statistician + Challenger)
### Instrument: `tools/extractor_acceptance.py` (standing gate-3 fixture — REQUIRED for every future domain roster / extractor change)

## What this documents

`sports_entity` shipped flag-on 2026-08-20 (Chairman-ordered coverage expansion) with the
gate-3 comparison run informally and no acceptance document — the board correctly called
that a §16 gate-5 lapse. This document closes it: a hand-labeled 12-headline sports corpus
(labels written before reading extractor output) + a 5-headline research corpus, scored for
precision/recall through the SERVE-TIME quality gate exactly as production applies it.

## Results (after the board-found segment-initial fix + subject-verb rule + `appoint` filler)

| Extractor | Corpus | Precision | Recall | tp / fp / fn |
|---|---|---|---|---|
| generic n-gram | sports | **10.2%** | **18.2%** | 6 / 53 / 27 |
| **sports_entity** | sports | **87.1%** | **81.8%** | 27 / 4 / 6 |
| generic n-gram | research | 29.4% | 83.3% | 5 / 12 / 1 |
| research_entity | research | **100.0%** | 83.3% | 5 / 0 / 1 |

The generic extractor's 10% precision on sports headlines is the quantified form of the
football post-mortem's finding: ~10 fragments per headline, junk that never aggregates.

## The board-verified defect, fixed and re-measured

The Challenger's verified finding — filler-trim ran before the segment-initial check, and
sentence-case club-first grammar produced bare segment-initial runs — dropped the club in
the DOMINANT headline form. Fix (two rules, both in `_keep`): (i) a lone word reached by
trimming a longer capitalized run keeps its proper-noun evidence; (ii) a segment-initial
lone word followed by a sports verb/role from `_SPORTS_FILLER` is subject-verb grammar and
the subject is the entity. Before → after on the corpus: recall 66.7% → **81.8%**; now
extracted: `arsenal`, `liverpool`, `chelsea`, `mourinho`, `england`, `barcelona`, `inter`.

## Remaining known misses (recorded, not hidden — 6 of 33 expected entities)

- `fifa` in "Fifth Fifa vice-president…" → bad split `fifth fifa` (Title-Case run chaining).
- `roma` + `manu koné` merge across the possessive ("Roma's Manu Koné" → `roma manu koné`).
- `serie a`, `ligue 1`, `psg`: single-letter/numeric competition suffixes and chained
  all-caps club names — the letters-only tokenizer ceiling, recorded at ship (d4d73e0).
- False positives (4): `psg ligue`, `fifth fifa`, `roma manu koné`, `serie` — all
  malformed-entity variants of real entities, none filler junk.

Verdict: PASS at trial grade. The remaining misses are bounded, named classes suitable for
the shadow-trial window (frozen instrument); refinement is post-trial work, never mid-window.

## Standing rule (board decision item 7)

Any new domain roster, extractor mode, filler-list change, or quality-gate change on an
entity-anchored path MUST run `tools/extractor_acceptance.py` (extended with a labeled
corpus for the new domain) and commit the resulting acceptance document BEFORE wiring.
The FORMAT gate has failed three times ad hoc; this fixture is its permanent enforcement.
