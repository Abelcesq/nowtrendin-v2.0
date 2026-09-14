---
name: grade-agent
description: NowTrendIn Grade Agent — pool-first topic grading that serves all 3 platforms. Searches the live data pool FIRST (returns the MEASURED Gradient Score + N if already scored, no AI cost), else runs the AI grade. Communicates with the other data agents (data pool, topic classifier, dual-pathway) and determines mainstream-vs-niche — from our own data when in-pool, from live open-web research when not. Always returns a Gradient Score AND an N score with provenance. Use when the user says "grade a topic", "how does grade work", "is grade searching our data", "mainstream or niche", "grade endpoint", or after changing grade/scoring/N.
---

# /grade-agent — pool-first grading (measured Gradient + N), all 3 platforms

The Grade Agent (`transfer/grade_agent.py`, `resolve_grade(topic)`) is the single
brain behind `/grade`. It exists because the raw AI grade ALWAYS spent a
Perplexity+Claude call to *estimate* a score — even for topics already measured in
our own data pool. The agent fixes that.

## What it does (the contract every platform relies on)
1. **Canonicalize** the topic (`_topic_key`).
2. **Search the data pool** — `velocity_scores` by exact canonical key, then by
   display match.
3. **If IN the pool → MEASURED:** return the engine's OWN Gradient Score
   (detection/confidence/overall/stage) + the MEASURED **N** (`nowtrendin_score`),
   plus signal-quality components, maturity, and the full live row.
   `source='measured'`, `in_data_pool=true`, **`charge_token=false`** (no AI ran).
4. **If NOT in the pool → AI_PROPOSED:** run `ai_grade.grade_topic` (proposed
   score + research + citations) and attach the live **N** (0 until demand accrues;
   the grade query logs N). `source='ai_proposed'`, `charge_token=true`.
5. **Always returns BOTH** a `gradient_score` {detection, confidence, overall, stage}
   AND an `n_score`. Companies also get the measured `market_signal` attached.

**Engine:** `POST /grade` (internal-key gated) → `grade_agent.resolve_grade`.
**Backend proxy:** Django `GradeView` honours `charge_token` — a measured lookup is
FREE; only an AI-proposed grade burns a grade credit.
**Platforms:** web `Grade.tsx`, mobile `GradeTool.tsx`, desktop (web build) all read
`source` / `gradient_score` / `n_score` and render the MEASURED vs AI-ESTIMATE badge.

## Steps (audit / verify)
1. Pick a topic KNOWN to be in the pool (e.g. `iran`, `copilot`) and one NOT in it
   (e.g. a made-up phrase). For an authenticated check use the backend
   `/api/grade/`; for the engine directly (internal key):
   ```bash
   curl -s -X POST $ENGINE/grade -H "X-Internal-Key: $INTERNAL_API_KEY" \
        -H 'content-type: application/json' -d '{"topic":"iran"}'
   ```
2. **Verify:**
   - in-pool topic → `source='measured'`, `charge_token=false`, real `gradient_score`
     + `n_score`, no `cost` recorded.
   - off-pool topic → `source='ai_proposed'`, `charge_token=true`, `proposed` score,
     `n_score` present (likely 0), citations.
3. **Report** any drift: an in-pool topic returning `ai_proposed` (canonicalization
   miss — check `_topic_key`/aliases), a measured result with `charge_token=true`
   (would wrongly bill), or a missing `n_score` on either path.

## Integrity
A measured return is the engine's objective score — never an AI estimate dressed as
one (always flag `source`). N stays a SEPARATE demand signal, never folded into the
Gradient (no demand feedback loop). Never charge a credit when no AI ran. Part of the
monitoring fleet (DATA_BUILDING_BLOCKS.md).
