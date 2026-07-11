# Advisory Board Review — Catch-All EOD Report (2026-07-10)

**Convened:** 2026-07-10 (auditor data ran 2026-07-11 05:36 UTC)
**Material:** The scheduled daily "Catch-All EOD" monitoring report + its 5 recommended actions.
**Mechanics:** Six independent archetype agents, identical evidence pack, no cross-talk. Collation only — the Chairman rules.

## What is being decided

The daily catch-all report reported **33.6% catch-all (2,015/6,000)**, flagged **157 "misclassified tracked calls" as HIGHEST priority**, and proposed five actions (hand-add non-Latin WC-2026 sports terms to `_LEX`; add broadcom/القدم; hold bare countries; no floor purge; ignore fragment noise). The board reviewed the report against engine ground truth.

## Ground truth established before convening (verified in source by multiple archetypes)

- **A.** `_LEX` (`topic_categories.py:57`, matched at `:261` on `blob.lower()`) is a **Latin-script keyword lexicon**. Cyrillic/Arabic topic strings (`هالاند`, `новак джокович`) can **never** match — `.lower()` is a no-op on non-Latin — so they fall to `general` **by construction**. The 157 "misclassified" items are almost entirely non-Latin.
- **B.** The 70.2% (2026-07-06) → 33.6% (2026-07-10) drop coincides with two flag flips **2026-07-08**: the **"B moat-strict" scoring-pool cleanup** (flagged "major scoring-pool cleanup — expect junk drop") and the **GHOST_RESEARCH_FEEDS** trial. Both under open board review (07-14, 07-21).
- **C.** The auditor measures over `CATCHALL_WORKING_SET=6000` **most-recent** topics (`monitoring_agents.py:766`, `ORDER BY scored_at DESC LIMIT 6000`) — a **moving window**, so the two figures are not over the same topics.
- **D. (Executioner, new)** Non-Latin terms arrive **double-encoded** from Apify and are repaired by `_demojibake` (`gravitational_anomaly_detector.py:2194`), which **falls back to raw mojibake** when repair introduces a replacement char (line 2206). A clean Arabic literal in `_LEX` would match only the cleanly-repaired subset — so the 157 count is **unverified against the actual stored strings**.
- Category is **display-only, non-circular** metadata — it never feeds the Gradient Score or the held-out ledger.

---

## The six memos (condensed)

### 1. The Challenger (accuracy skeptic)
- **33.6% "baseline" → REJECT.** The 36-point drop is confounded three ways (junk purge shrinks the least-classifiable topics → mechanically lowers catch-all with zero classifier gain; drifting 6,000-most-recent denominator; GHOST feeds added same day). "Different measurement window" is the whole story, not a footnote. Change-my-mind: a **frozen panel** — recompute the 33.6% definition over the identical pre-purge topic set.
- **157 highest-priority → APPROVE-WITH-CONDITIONS.** "Misclassified" is factually wrong (unclassifiable by construction); restate as "157 tracked calls carry the 'general' label, no ledger/score impact," confirm distinct-topic count, drop from "highest priority."
- **Hand-add native-script → REJECT (as approach).** Transient WC-2026 vocabulary manufactures a future fake "improvement" that evaporates post-tournament; short native tokens (القدم) overmatch; can't QA labels in languages the team can't read. Segment non-Latin into its own honest bucket instead.
- **User-facing risk:** score/ledger safe; the danger is anyone quoting the catch-all % externally as an accuracy KPI. Stamp it internal-only.

### 2. The First-Principles Guardian (vision + ledger)
- **157 highest-priority → REJECT the framing.** A display-bucket label defect cannot be the top integrity item — it never touches the score or the time-stamped ledger. Severity inflation.
- **Hand-curate foreign sports lexicon → APPROVE-WITH-CONDITIONS, but demote.** Mechanically principle-neutral (display-only, non-circular), but an unbounded manual-curation treadmill chasing a **cosmetic vanity metric**. Condition: never let "catch-all %" masquerade as engine-health/accuracy.
- **Ledger/circularity risk:** none created; recs #3/#4/#5 are correctly protective. **The buried story:** a display metric doesn't halve because you tightened the *scoring pool* — unless the scored population itself changed. The report reads a 36-point swing as "STABLE" while a scoring-admission flip landed 2 days prior — **monitoring the wrong variable.** Reconcile before trusting "STABLE."
- **Founder's priority reorder:** (1) reconcile the swing vs the moat-strict + GHOST flips; (2) verify the 157 are correctly enrolled/stamped in the ledger (not their display bucket); (3) lexicon edits = low-priority nav polish.

### 3. The Expansionist (global scale)
- **Hand-curate per-language `_LEX` → REJECT.** O(entities × languages × scripts) manual labor against a stream that generates new trending strings daily. Already breaking at 1×.
- **Real gap:** the platform **ingests globally but classifies mono-lingually** — no script detection, normalization, transliteration, or entity resolution anywhere. Measurement moat intact; the *legibility layer* is monolingual, and it's what a global buyer sees first (EMEA/LATAM/APAC topics dumped in "General" → lost demo).
- **Highest-leverage move (sequenced):** (1) script/language detection at ingest (days, `unicodedata`/`langdetect`-class, zero API cost) → turns "33.6% general" into an honest coverage map; (2) ICU transliteration to canonical form; (3) language-agnostic entity resolver (classify the *entity*, not the string). Never hand-add WC terms.

### 4. The Outsider (VC / hedge-fund banker, plain English)
- **33.6% "fresh baseline" → APPROVE-WITH-CONDITIONS, but "smells managed."** A number halved in 4 days, explained by "don't compare it, this is the new baseline" — that language launders an unexplained 2× move. Ratio over a moving denominator, unverified. Condition: rerun on a constant pool first.
- **157 as highest priority → REJECT.** Tags are display-only; the fix is whack-a-mole against a structural wall (English-only dictionary). It's a diagnostic finding, not a task.
- **Point-blank question:** "Did the classifier get better, or did the denominator move under you? Run the same measurement both ways. And why is a cosmetic tag on the priority list at all?"
- **Worth/works:** unchanged — this is all downstream of the moat. But it's a **governance flag on how the team reports to itself**; diligence would dig into whether the *ledger* hit-rate ever uses "fresh baseline" resets or moving denominators.

### 5. The Economist (canon)
- **(i) Baseline/halving → REJECT** (Friedman & Schwartz + Malkiel + anchoring). A discontinuity dressed as a starting point; a 36-pt move 48h after changing what enters the pool is a composition effect until proven otherwise. Honest prior = noise from a regime change.
- **(ii) 157 highest-priority → REJECT** (Taleb silent evidence). Unclassifiable by construction, not misclassified. The real question the report is silent on: **how much genuine before-it-arrives signal are we losing by reading only Latin script?** Non-Latin is where an international fat-tail surge shows up *first*.
- **(iii) Raw-count list → REJECT** (Malkiel null). Counts with no expected-rate baseline; "norway 13 / broadcom 9" are meaningless without lift. Reclassify on **lift over expected rate**, not raw frequency.
- **(iv) Corroboration floor → APPROVE.** The one methodologically honest instrument — a genuine null-hypothesis gate that de-noises the body while exempting the fat tail. The template the rest should be rebuilt to.
- **Prescriptions:** version/stamp the metric & break the series visibly at each flag flip; reclassify on lift not count; **segment the non-Latin artifact out of the headline**; treat the non-Latin stream as a **leading indicator** — measure lead time between first non-Latin sighting and first English sighting, validate held-out on the ledger; extend ≥2-distinct-source logic from admission to weight; mandatory "null hypothesis" line on every catch-all report.

### 6. The Executioner (delivery)
- **#1 non-Latin sports layer → SHIP-LATER, NOT safe as-described.** Three defects: (a) `_demojibake` fallback means clean Arabic literals silently no-op on mojibake'd rows — the 157 count is unverified; (b) **القدم = "the foot," overmatches** anatomy/medical Arabic (football = كرة القدم); مباراة = generic "match"; (c) Arabic clitic prefixes (و/ب/ل/ال) break `\b` boundary matching. Requires: pull the actual 157 strings, confirm clean UTF-8, verify each term against its topic's own signals, run `classify_topic` offline first.
- **#2 → SPLIT.** `broadcom`→technology = **SHIP** (distinctive Latin token, `nvidia` precedent). `القدم` = **CUT** from this action (fold into #1's verification bucket).
- **#3 hold countries → SHIP (ratify, no-op).** #4 no purge → **SHIP (ratify)** — a purge would also violate the 365-day no-quality-delete rule. #5 fragment noise → **SHIP (ratify)**.
- **Ship order:** (1) ratify #3/#4/#5 no-deploy; (2) deploy broadcom only; (3) revisit #1 + القدم *after* the 07-14/07-21 flips resolve and the baseline settles.
- **Rollback:** pure `git revert` + redeploy; category recomputed at serve-time → instantly restores labels, no re-score, no ledger touch. Blast radius = one display string.
- **CUT:** القدم standalone; the "highest-leverage" framing on #1; any report of the catch-all drop as a lexicon win before the flips clear.

---

## DISAGREEMENTS (signal, not noise)

The board is **unusually convergent** — all six independently rejected the report's two headline framings. The differences are of emphasis, not direction:

- **On the 157 items — how alarmed to be:** Challenger & Outsider = "cosmetic, near-ignore." Guardian = "demote, but verify the underlying ledger enrollment is fine." Expansionist & Economist = "the OPPOSITE of ignore — this is the roadmap-defining finding: we're structurally blind to the language attention originates in, and that's a fat-tail *detection* gap, not just a display one." **This is the one real tension for the Chairman:** is non-Latin coverage a cosmetic to demote or a moat opportunity to escalate?
- **On broadcom:** Executioner explicitly SHIPs it; Economist would gate even it on a lift-vs-baseline check ("broadcom 9" is meaningless without its expected rate). Minor.
- **Everyone agrees:** do NOT hand-patch native-script terms as-described; do NOT publish the catch-all % externally; the corroboration floor and the three no-ops are correct.

---

## Decision table — Chairman rules per item

| # | Item under review | Challenger | Guardian | Expansionist | Outsider | Economist | Executioner |
|---|---|---|---|---|---|---|---|
| A | 33.6% as a clean "baseline" / the halving | REJECT | (flag) reconcile | — | APPROVE-w/-COND | REJECT | gate on flips |
| B | "157 misclassified tracked calls = HIGHEST priority" | APPROVE-w/-COND (reframe) | REJECT framing | ESCALATE (as structural) | REJECT | REJECT framing | reframe |
| C | Rec #1: hand-add non-Latin WC terms to `_LEX` | REJECT (approach) | APPROVE-w/-COND (demote) | REJECT | REJECT | REJECT | SHIP-LATER (not as-described) |
| D | Rec #2: broadcom→tech | (n/a) | — | — | — | APPROVE-w/-COND | **SHIP** |
| D' | Rec #2: القدم→sports | REJECT | — | REJECT | — | REJECT | **CUT** |
| E | Rec #3 hold bare countries | — | APPROVE | — | — | APPROVE | SHIP (ratify) |
| F | Rec #4 no floor purge | — | APPROVE | — | — | APPROVE | SHIP (ratify) |
| G | Rec #5 fragment noise, don't add | — | APPROVE | — | — | APPROVE | SHIP (ratify) |
| H | Corroboration floor design | — | — | — | — | **APPROVE (template)** | SHIP (ratify) |
| I | Publish catch-all % externally as accuracy KPI | **NEVER** | never | — | never | never (segment) | never |

### Board-consensus recommendations to the Chairman (informational — you decide)
1. **Do NOT treat 33.6% as an improvement or a baseline** until it is recomputed on a **frozen panel** and the drop is attributed to the 07-08 flips vs classifier work. Stamp catch-all % as an internal ops metric, barred from any external accuracy claim.
2. **Reframe the 157** honestly: not "misclassified," but "non-Latin, unclassifiable by the current lexicon — zero score/ledger impact." Verify their **ledger enrollment** is intact (that's the only moat-relevant part).
3. **Ship broadcom→technology only** now (trivial, reversible, `nvidia` precedent). **Cut القدم** (overmatch). **Ratify the three no-ops** (#3/#4/#5).
4. **Do NOT hand-patch native-script terms.** If non-Latin coverage matters, the durable fix is **script-detection at ingest → transliteration → entity resolution** — and there is a live encoding bug (`_demojibake` fallback) to fix first.
5. **The open question for the Chairman:** treat non-Latin as (a) cosmetic display to demote, or (b) a fat-tail early-detection opportunity to escalate (measure non-Latin→English lead time, validate held-out on the ledger). The board split 4-vs-2 toward "escalate as opportunity," and it is the highest-value idea surfaced.

**Chairman — your decision per item.**
