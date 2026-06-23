# SITUATION MODEL — Topics, Not Words

**Status: RECOMMENDED DESIGN (2026-06-23).** Builds directly on the last 24h of work
(single-source weights `scoring_weights.py`, the scoring/date data-contracts, the held-out
referee, `situation_clustering.py`). Prototype of the hard part (hub disambiguation) is
**built + proven** in `transfer/situation_clustering.py`. Scoring impact is **🔒 backtest-
gated** — nothing here moves a live score until validated.

---

## 1. The problem (the "japan" case)

The engine models **words**, not **topics**. The same word fails two opposite ways at once:

- **Over-aggregation** — bare `japan` is ONE "STRONG, 16,066 mentions" blob that smears three
  unrelated stories together: the Emperor's Belgium visit (politics), the Bank of Japan rate
  hike (economics), and Japan vs Sweden at the World Cup (sports). The number is contextless.
- **Fragmentation** — `bank japan` splits off as its own topic; `japan vs sweden` doesn't
  surface at all; the BOJ story is scattered across `japan`, `bank japan`, `interest rate`.

Root cause (confirmed in code): `extract_topics_from_text` emits token/n-gram fragments per
document; `_canonicalize_topic` consolidates only **surface** variants (morphology + a hand
alias map). There is **no layer that knows those fragments are one event** — even though
`topic_signals.signal_id` already records which fragments co-occur in the same document.

---

## 2. The three-level model

```
ENTITY            SITUATION / EVENT (the scoreable unit)             FRAGMENTS
"japan"  ──┬──►  japan · Belgium royal visit   [Politics]   ◄── belgium, naruhito, masako, visit
           ├──►  japan · BOJ rate hike          [Economics]  ◄── bank of japan, interest rate, policy
           └──►  japan · World Cup vs Sweden     [Sports]     ◄── sweden, world cup, match
```

- **ENTITY** — the searchable anchor (a name/place/term a user types). Searchable, NOT the
  scoreable unit (scoring a bare entity is the smear above).
- **SITUATION / EVENT** — *entity + distinguishing context + category + time window.* **This is
  what we score, rank, and show.** It is a coherent real-world event.
- **FRAGMENT** — the words/phrases that compose a situation. Stay individually **searchable**
  and remain the unit of **early/niche detection** (the thesis — we must still catch
  "diffusion models" spiking on its own).

Cardinality: an entity anchors **1..N** situations; a situation has 1 anchor + many fragments;
a fragment (esp. a shared anchor) can belong to **1..N** situations.

---

## 3. How situations form — the algorithm (proven in `situation_clustering.py`)

1. **Co-occurrence** from `topic_signals.signal_id` (already recorded — zero new data/cost).
2. **Jaccard-normalized edges** over the documents each pair shares — so a popular word can't
   glue everything together (raw counts would).
3. **Hub detection** — an entity whose removal splits its own neighborhood into ≥2 groups is a
   hub (`japan`). Hubs are what cause the smear.
4. **Cluster WITHOUT hubs** → the distinct situation **cores** (the distinguishing context).
5. **Re-attach each hub** to every core it touches → the entity fans out into its situations as
   a **shared, searchable anchor — never a merge.** *(Demonstrated: search "japan" → 3
   situations, each anchored by japan, separated by belgium / bank-of-japan / world-cup.)*
6. **Category per situation** — run the existing classifier on the situation's aggregate text,
   so Politics/Economics/Sports is a per-**situation** tag. This fixes the "everything → News
   catch-all" smear visible today.
7. **Time-windowed** (rolling) — a situation is an event in time; a recurring entity (Japan at
   the next World Cup) forms a NEW situation each cycle rather than reviving the old one.
8. *(Optional later layers, additive)* semantic embeddings link related terms that don't
   directly co-occur; an LLM names the top-N situations in human-readable form. Co-occurrence
   alone is the zero-cost foundation; these improve the tail as AI improves.

---

## 4. Data model + DB-redundancy reduction

New tables (the granular `velocity_scores`/`topic_signals` are UNCHANGED — additive):

- **`situations`** — `situation_key` (PK), `label`, `anchor_entity`, `category`, `signal_stage`,
  `detection_score`, `confidence_score`, `nowtrendin_score`, `member_count`, `first_seen`
  (= earliest member first-seen), `window_start`, `window_end`, `scored_at`, `serve_payload`.
- **`situation_members`** — `situation_key`, `topic_key`, `role` (`anchor`|`core`), `weight`.
  Many-to-many (shared anchors map to several situations).

**Redundancy / space:** the served board moves to the **situation grain** — the long tail of
redundant fragments (`japan`, `bank japan`, `japan rates`, `boj`, `interest rate japan`) rolls
into ONE situation row instead of five. The granular rows are retained for early detection but
the **served, scored, ranked** universe is situations → fewer rows surfaced, no smear, the
90-day retention rule still applies to the granular layer untouched.

---

## 5. Search + disambiguation (the user picks the situation)

- **Search an entity** (`japan`) → an entity card that **expands to its N situations**, each
  with its category, stage, situation-score, and freshness. The user selects which event to
  score/inspect. (Like a search engine returning distinct results, not one contextless number.)
- **Search a fragment** (`belgium`, `sweden`) → the situation(s) it belongs to.
- The bare-entity aggregate may still be shown but is **clearly labeled "entity aggregate —
  spans N situations,"** never sold as a single topic score.
- Default ordering of an entity's situations: strongest + freshest first.

---

## 6. Scoring at the situation level (🔒 backtest-gated)

- A situation's components aggregate its members: **union** of source documents (dedup so
  shared anchors don't double-count), aggregate magnitude/breadth, earliest first-seen.
- Detection / Confidence / Overall via the **single-source** 6-component formula
  (`scoring_weights.py`) — identical machinery, applied at the situation grain.
- **Gate:** `SITUATION_SCORING_ENABLED` (default off), validated against the held-out referee
  **at the situation level** before any flip — mirrors the `SCORE_QUARANTINE_ENABLED` pattern.
  Granular early detection is preserved; situations never replace the niche signal, they
  contextualize it.

---

## 7. Filter & sort taxonomy (explicit — the same on every surface)

**FILTERS** (composable): **Level** {entity · situation · fragment} · **Category** {Politics ·
Economics · Sports · Tech · Health · …} · **Stage** {Breakout · Strong · Indicating · Marginal ·
Monitoring} · **Recency** {live · 12h · 24h · 7d} · **Anchor entity** · **Source-class**
{mainstream(M) · dark-matter(D)}.

**SORTS:** situation **Detection** (default — *All Signals*) · **N** (*Now TrendIn* view) ·
**Confidence** · **Recency** · **Discovery-lead**. Always within the active Category/Entity scope.

**Invariant INV-1′ (extends INV-1):** one situation → the **same** situation-score on every
surface (web/desktop/mobile), read from the situation `serve_payload`.

---

## 8. The Situation Contract — communication protocol for ALL agents & scoring

The lever that keeps "the last 24h" coherent: every system speaks **one declared situation
format**, exactly as `scoring_contract.py` did for scoring fields.

- **`situation_key`** is the new canonical join key; every fragment maps to it; every agent
  and the frontend reference situations by it (no per-surface re-derivation).
- A declared **SITUATION_CONTRACT** (in `scoring_contract.py` style): required fields, types,
  ranges, enums (category, stage), and the derived rules (e.g. `first_seen` = min member
  first-seen; `member_count` = |members|).
- **Agent protocol:**
  - *Pipeline Integrity* — situations serve consistently across surfaces (INV-1′).
  - *Topic Quality* — a situation must have ≥2 real fragments and a resolved category (no
    single-fragment "situations," no catch-all smear).
  - *The referee* — measures **arrival at the situation level** (query the situation's context
    terms, not the lone word) → dissolves the "hormuz"/"DeepSeek" single-word blind spot.
  - *Scorer* — reads situation members, writes the situation `serve_payload`.
  - **Situation Contract Auditor (Agent 18)** — audits live situations against the contract
    (off-enum category/stage, orphan fragments, derived-field drift), beside Agents 16/17.

---

## 9. Integrity · clarity · accuracy (non-negotiable)

- **Additive, not a rewrite** — granular topics preserved; early/niche detection intact.
- **Real relationships only** — clusters come from measured co-occurrence (later, embeddings);
  never a guessed or hand-asserted link.
- **Disambiguation is honest** — show the distinct situations; never collapse to one
  contextless number, never hide that an entity spans several events.
- **No laundering** — situation-level measurement is more honest but never turns a genuine
  scoring miss into a win (the ledger/referee gate is unchanged).
- **Descriptive, not predictive** — a situation is a measured grouping; predictability remains a
  goal that improves as AI/data improve, not a claim made today.
- **Backtest-before-ship** — any situation-level scoring change is gated + validated first.

---

## 10. Phased rollout

| Phase | Scope | Score impact |
|---|---|---|
| **A** (now) | `situation_clustering` on REAL `topic_signals` → `situations` table, READ-ONLY. Validate clusters on the live corpus. | none (held-out) |
| **B** | Search → entity→situations disambiguation; per-situation category tags. | display only |
| **C** | Situation-level scoring behind `SITUATION_SCORING_ENABLED`, backtested vs the referee. | 🔒 gated |
| **D** | Referee at situation level; Situation Contract Auditor (Agent 18); served board moves to situation grain (redundancy reduction). | gated |

**Next concrete step (Phase A):** run `build_situations()` against a rolling window of real
`topic_signals` co-occurrence (a held-out engine job or a one-shot export) and review the
situations it forms on our actual data — the synthetic proof (japan → 3 situations) holds;
the live-corpus validation is what gates Phase B.
