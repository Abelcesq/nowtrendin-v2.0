# Football-Feed Post-Mortem — why three live niche sources produced ~zero niche mentions
### Chairman-ordered (A4 item 3, run in parallel per the recorded Operator mitigation) · 2026-08-19 · read-only

## The question

The Operator's board finding: **Guardian Football, ESPN Soccer and Football365 have been live at
`tier: "niche"` since 2026-06-12** (`blog_collectors.NEWSLETTER_FEEDS`) — through the entire World
Cup — and yet across all 532 stored `world_cup` cycles `dark_matter` never exceeded 9/100 and
`niche_mentions` reads 0. Three candidate mechanisms were named, each implying a different build at
a different cost: (a) extraction failure on sports headlines, (b) the first-timer numerator reading
0 on already-seen topics, (c) collector under-delivery.

**Answer: (a). It is extraction, and the defect is upstream of everything else — the feeds deliver,
the tier is correct, and the topics those headlines produce are not the entities anyone would
search for.** Nothing needs to be inferred about D's numerator until this is fixed, because the
canonical topic mostly never gets created in the first place.

## What was ruled out first

**Routing is CORRECT.** The three desks carry `"tier": "niche"`
(`blog_collectors.py:159-161`), and the collector passes that tier straight through to the writer
(`tier = cfg.get("tier", "mainstream")` → `_write_signal(...)` / `_write_topics(..., tier, ...)`).
This is *not* the `_news_write` failure mode from §15 where everything is stamped `mainstream` and
the early read is suppressed. Had the tier been wrong, D would still have been 0 — but it isn't
wrong, so that explanation is dead.

**Delivery is real.** The Guardian Football feed returns live, fresh, well-formed items on the
production UA (verified this session, 11 headlines pulled).

## The mechanism, demonstrated on live headlines

The sports desks are collected by the newsletter/medium path, which uses the **generic n-gram
extractor** (`extract_topics`). Run against today's real Guardian Football headlines it emits
~10 fragments per headline:

| Live headline | What the generic extractor produces |
|---|---|
| "Fifth Fifa vice-president turns against Infantino…" | `against infantino saying`, `president turns against`, `turns against infantino`, `vice president turns`, `fifa vice president`, … (10) |
| "Manchester City target Roma's Manu Koné as Spurs talk over Savinho…" | `talk over savinho`, `kone spurs talk`, `city target roma`, `target roma manu`, … (10) |
| "Arsenal agree £51m deal to sign Ezri Konsa from Aston Villa" | `arsenal agree 51m`, `agree 51m deal`, `deal sign ezri`, `konsa from aston`, … (10) |
| "Mourinho says Real Madrid did not want Rodri…" | `mourinho says real`, `says real madrid`, `hesitation over move`, `rodri after hesitation`, … (10) |

**5 headlines → 49 extracted "topics", almost all of them headline fragments anchored on filler
verbs and prepositions.** This is precisely the FORMAT-gate failure §16 records for NBER
("academic titles extract to noise") and for the research feeds, whose fix was the entity-anchored
extractor.

### The quality gate half-catches it — and that is the worse half

Running `_is_quality_topic` over the extractor's own output:

- **Correctly killed:** `talk over savinho`, `kone spurs talk`, `deal sign`, `agree 51m deal`,
  `president turns against`.
- **LEAKED (junk kept):** `against infantino saying`, `turns against infantino`.
- **FALSE NEGATIVE — a real entity rejected:** **`real madrid` → killed.**

That last line is the load-bearing one. Even on the occasions when the generic extractor *does*
surface a canonical football entity, the gate can reject it. So niche football coverage cannot
accumulate against the canonical topic: the junk that survives is unique per headline (it never
aggregates into a topic anyone tracks), and some of the real entities are discarded outright.
`world cup` and `premier league` both PASS the gate — they were simply never produced often enough
by an extractor that spends its output budget on `turns against infantino`.

## The remedy already exists in-house

`blog_collectors.research_entity_topics` — built 2026-07-07 when the research feeds failed this
exact gate — is entity-anchored and behaves correctly on the same headlines:

| Headline | generic (first 5 of 10) | **entity-anchored** |
|---|---|---|
| Fifa vice-president / Infantino | `against infantino saying`, `turns against infantino`, … | **`fifth fifa`, `infantino`** |
| Man City / Koné / Spurs / Savinho | `talk over savinho`, `kone spurs talk`, … | **`roma manu kone`, `savinho`, `marmoush`** |
| Arsenal / Ezri Konsa / Aston Villa | `arsenal agree 51m`, `deal sign ezri`, … | **`ezri konsa`, `aston villa`** |
| Mourinho / Real Madrid / Rodri | `mourinho says real`, `says real madrid`, … | **`rodri`** |

Entities instead of fragments, and 2–3 per headline instead of 10. It is not perfect for this
domain (it missed `real madrid` and `arsenal` in the samples above, and `fifth fifa` is a bad
split), which is exactly why this is a **§16 gate-3 exercise for a new `mode="sports_entity"`**,
not a one-line swap.

## What this changes for A4

**The Operator's predicted failure is real and now evidenced.** Any shadow trial or backtest that
adds MORE sports feeds through the generic extractor would run them into this same silencer, and
its null would read as *"no edge"* when the truth is *"no measurement."* Under the recorded
mitigation, this post-mortem's answer must be in hand before step 1's result is interpreted — it
now is, and the answer is: **do not interpret any sports-domain null until the extractor path is
fixed.**

## Recommended follow-ups (no code shipped by this document)

1. **Build `mode="sports_entity"`** on the `research_entity_topics` pattern, and run the full §16
   five gates on it — the FORMAT gate is the one that matters and it is the one that has failed
   twice now (NBER, and this).
2. **Fix the `_is_quality_topic` false negative on two-word club/person entities** (`real madrid`).
   This is score-adjacent — it changes which topics exist — so it needs backtest-before-ship.
   Note the asymmetry: leaking junk costs catch-all congestion; rejecting real entities costs
   *coverage we cannot see we are missing*, which is the more expensive error and the invisible one.
3. **Re-run this post-mortem's extractor comparison as an acceptance test** for any new domain
   roster before it ships — a cheap, reusable §16 gate-3 harness.
4. Only then reconsider whether D's first-timer numerator has a second, independent defect. It may;
   this post-mortem simply proves it is not the FIRST defect and cannot be measured until (1) lands.
