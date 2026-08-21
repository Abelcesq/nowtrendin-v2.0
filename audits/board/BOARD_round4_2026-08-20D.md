# BOARD ROUND 4 — COLLATION FOR THE CHAIRMAN
### Nine seats convened 2026-08-20 (late) on commit `57e2ae7` + `EVIDENCE_PACK_2026-08-20D.md`.
### Seats ran in parallel, blind to each other. This is a COLLATION, not a blend. No recommendation.

---

## 0. THE HEADLINE — the board rejects the pack's central causal claim

**Three seats independently falsified the root cause I reported to the Chairman**, by three
different routes, having never seen each other's work:

- **Executioner:** `_explain_d` has exactly one caller (`:11776`, inside `get_topic_detail`);
  `_precompute_serve_payloads` stores a flat `velocity_scores` row with no `components` key.
  `plain_english` was never in the blob.
- **Statistician:** `get_topic_detail` sets `s = json.loads(_payload)` at `:11680-11685` — **all
  four D fields derive from ONE dict**. A stale blob makes them *consistently* stale. It cannot
  desynchronise them. The contradiction is structurally impossible from any payload age.
- **Challenger:** same dict literal, therefore by the pack's own diagnostic it cannot be a cache
  artifact.

**Verified mechanism: a DEPLOY-VERSION WINDOW.** Deployed code == `a650e18` (which added
`d_measured`/`unmeasured_note` while `plain_english` was still an unguarded `_explain_d`) before
`9b480fe` (21:22:25 → 21:34:03 PDT) reached the dyno. The blob was **fresh, not stale**. Both
halves of the reported story are inverted.

**Consequence (Statistician, Executioner):** `POST /precompute` neither caused nor cured it, so
**§4(a)'s prescribed remedy does not bind the mechanism.** The gate's *trigger* is sound; its
*remedy* is aimed at the wrong object.

**This is a CLAUDE.md §10a VERIFY-BEFORE-FIX violation** — a hypothesis shipped as a diagnosis —
and the wrong narrative is now enshrined as permanent comments in two enforcers
(`.githooks/commit-msg:130-143`, `tools/integrity_gate.py:114-123`). The next engineer inherits
the wrong lesson from the artifact built to prevent wrong lessons.

**Executioner on his own round-3 instruction:** *"No, and it failed in the way I should have
anticipated. I specified an action and a confirmation but not a mechanism check — so it was
satisfiable by a green probe with a wrong causal story attached. The pattern's next costume is a
verified result with an unverified cause."*

---

## 1. THE LIVE DEFECTS THE BOARD FOUND (not in the pack, all code-verified)

### L1 — `D_dark_matter.score` serves a fabricated 0 (Guardian + Challenger, independently)
`compute_dark_matter` returns `0.0` on the unmeasured path. Every `d_measured=0` row serves
`score: 0` **in the same dict literal** as prose saying no reading exists. Not display-only:
Challenger puts it at **13% of the composite / 22% of detection**; Guardian at weight up to
**0.216** (`scoring_weights.py:38`). §15a-A3 floor-end and §16a stage-2, violated, in the score.
Reaches users on four surfaces incl. `WhyScoresDiverge.tsx:21-22`, which has **no `d_measured`
guard at all**.
Guardian: the docstring convicts itself — *"the returned 0 means 'could not read'"* beside
*"count at the neutral value."* **0 is not neutral on a 0–100 scale.**

### L2 — the `d_measured IS NULL` stratum (Executioner + Statistician, independently)
Column added by live migration, **no backfill**. `None != 0` is True and `None == 0` is False, so
every pre-2026-08-20 row serves `d_measured: null` **+ a numeric `first_timer_ratio` + "No dark
matter signatures. Signal appears to originate publicly."** `/precompute` cannot fix it.
**Statistician's estimate: >90% of distinct topic_keys on day 1**, and dormant topics stay NULL
permanently. The probe's `WHERE d_measured = 0` **deterministically excluded this stratum** (SQL
`NULL = 0` is NULL), i.e. the frame was exactly the population in which the fix cannot fail.
*Statistician's single highest-value action: register this as an OPEN claim today.*

### L3 — §15a quorum is enforced asymmetrically by writing system (Expansionist, sole finder)
`_title_sig` truncates to 10 **space-separated** tokens. CJK has no spaces → signature is the
entire headline → exact-string match, not prefix match. Tested: Latin/Cyrillic/Arabic → 5 tokens;
**Chinese/Japanese → 1**. Five Chinese mastheads on one wire story yield `n_stories=5`, so
`min(outlets, titles)=5` → **`mainstream_confirmed`**, where identical English collapses to one
voice and correctly stays a Dark-Matter trigger. The doctrine **fails OPEN in the largest
non-English media market**, surrendering the early-detection edge exactly where expansion aims.
Score-affecting → backtest + board note, never an env flip.

### L4 — the register's own enforcers are substring searches (five seats, convergent)
`_enforcer_live`: `kind="lint"` → `ref in ("L1","L2","L3")` — **a literal tautology, constant
True, covering 3 of 15 rows**. `kind="hookgate"` → substring in `.githooks/commit-msg`; the banner
`SERVE-PAYLOAD GATE` also appears **in a comment at :130**, so deleting the entire gate body keeps
the claim green. `kind="test"` → file exists + marker substring, never runs the test
(`C-TRIPWIRE-FIRES`'s marker is `t6`, two characters). Only **one** row (`audit`) executes anything.
**Expansionist:** `.githooks/commit-msg` is a *committed file* and `integrity_gate.py` never checks
`core.hooksPath` — so three claims report **green in any clone where no gate has ever run.**

### L5 — "15 of 15" prints before the lints run (Challenger)
`verify_claims` prints at `:208` from `bad_ids`; L1/L2/L3 append to `_fail` afterwards with
`L1:`-style prefixes that never collide with `C-` ids. **The headline stays green on a run that
exits 1.** Denominator is author-controlled and the gate's own failure text *instructs* moving a
failing claim to OPEN — which removes it from the denominator. 0 OPEN rows exist. 15/15 = 100% by
construction. `CLAIMS = []` prints `0 of 0` and PASSES.

### L6 — figures I published that were false
- **"10 files, 10 passed, ~5s"** → actual **9 passed, 0 failed, 1 skipped, 4.6s**;
  `test_etf_issuer_pages.py` is run by no gate and no schedule. (Executioner, Challenger)
- **`run_tests.run_one` sets `ok = (returncode == 0)`** — a file asserting nothing counts as PASS.
  The 0-of-0 degenerate case at suite level. (Challenger)
- **Verified state ≠ steady state:** scheduler rebuilds `PRECOMPUTE_TOP_N=600`; I verified at
  **800**. Rows 601-800 revert to NULL next cycle. **The observed state had a ≤6h half-life and
  was never restored.** (Executioner, Expansionist)

### L7 — buyer-facing accuracy doc leads with a retired engine (Buyer's Desk)
`docs/buyer-diligence/ACCURACY_FIGURES_SCOPED.md` §4 leads with **27.1% / 48 races**; its own §1
says 76 of 111 resolved rows come from the **v1 engine we no longer run**, current engine reads
**2.9% blended / 5.0% tracked, n=20**. Disclosed in the subordinate clause = the App Annie shape.
Also: **0 of 13 LED wins corroborated by the independent referee**; 10 on ambiguous single-word
queries — the moat, unverified, in a footnote.

### L8 — the register enforces the screens; the customer buys the JSON (Buyer's Desk)
`gravitational_anomaly_detector.py:11769`: *"No UI renders this field, but the licensing product
IS the payload."* L3 lints `.tsx`. **The enforcer is aimed at the surface nobody buys**, and the
sentence saying so was already in the file.

### L9 — `/scores/{topic}` is public, unauthenticated, unlogged (Buyer's Desk)
No auth dependency on the route (contrast `/usage`). `api_usage` logs *outbound* vendor calls. **No
log drain configured** → Heroku router logs ephemeral. "Who received the contradiction" is not
unanswered, it is **unanswerable**. Verdict: *"'No obligation' is the right answer; 'no capability'
is the true one."*

### L10 — PII: D is computed FROM person-level identifiers (Buyer's Desk)
`x_signal_module.py` stores `handle`; `blog_collectors.py` stores forum/Medium usernames. Dark
Matter is keyed on **resolved authors and first-timer ratios**. Disclosed in `PII_POLICY.md` §2 —
but **no retention limit and no erasure path** on that store. *"A named forum user emails a
deletion request. What happens, mechanically, and does your first-timer ratio change?"*

### L11 — AB-ATTRIBUTION: the deadline is soft, and T1–T4 are ALREADY LOST
- **Operator:** `SIGNAL_RETENTION_DAYS` is env-read, floor 4, **no ceiling**. 08-27 is a default,
  not a mechanism. Raising it buys weeks for disk cost. *A deadline believed immovable is itself
  the forcing risk.*
- **Statistician:** five treatments, one switch point → **design matrix rank 1**. The recompute
  identifies **exactly 1 of 5** (T5, `D_PLUMBING_V2`), and only as `E[T5 | T1..T4 ON]` — a
  conditional, not a main effect. T1–T4 are collection-side (they change which rows exist); their
  counterfactual needs pre-flip inputs, and at 7-day retention **the pre-flip window is already
  ~08-13→08-20 and loses a day per day. For any pre/post arm the deadline is NOW, not 08-27.**
  T3 (Reddit) may be a **null treatment** — 403-ing for two months per `f5b1956`; check pre-window
  row counts and the confound set drops from 5 to 4 for free.
  Multiplicity: 15 primary contrasts uncorrected → **P(≥1 false positive) = 53.7%**.

### L12 — the seal is never recomputed (Operator, Buyer's Desk, independently)
`sealed` enforcer checks only that `PIT SEAL` and a date string are **present in the file**. It
never recomputes the published `text_sha256`. `pit_store.verify()` **exists** (`:373`) and its only
caller is an on-demand endpoint parameter — **nothing schedules it**. Byte-for-byte the
C-FIREWALL defect already fixed once, sitting on `C-KILL-CRITERION`, the claim whose late
falsification is most damaging. *A sealed pre-registration can be edited after results are known
and the gate stays green.*

---

## 2. THE PATTERN'S NEXT COSTUME — five seats, five different answers (PRESERVED, NOT MERGED)

| Seat | Named costume |
|---|---|
| **Guardian** | The **D score-side floor** (L1) — honest absence fixed in display, unfixed in score. And: *the fixes are wrong in KIND — every remedy lives at COMMIT time; every claim that keeps failing is about RUN time.* |
| **Operator** | `C-KILL-CRITERION` + the **unrun `pit_store.verify()`** (L12). |
| **Buyer's Desk** | **The register lints the screens; the product is the API payload** (L8). |
| **Challenger** | **The measuring instrument itself** — four green signals whose green means "a string was found." |
| **Statistician** | **The denominator** — the pattern moved from *claim vs enforcement* to *numerator vs denominator*: a self-authored 15/15, a 1-of-1 verification, a 1-of-1 control, a coverage figure whose base excludes the failing stratum. |
| **Expansionist** | **Locale** — every gate, lint, claim and probe reasons in one language and one writing system; nothing in the apparatus can fail on account of a script it does not read. |

---

## 3. DECISION TABLE

| Item | Challenger | Guardian | Expansionist | Buyer's Desk | Executioner | Operator | Statistician |
|---|---|---|---|---|---|---|---|
| §2 n=1 production verification | **REJECT** | — | — | credits method | SHIP method, don't bank result | **ACCEPT** | **REJECT** |
| §4(a) SERVE-PAYLOAD GATE | APPROVE-W-C | APPROVE-W-C | APPROVE-W-C | partial | **SHIP w/ corrected narrative** | ACCEPT, scope-caveated | wrong object |
| §4(b) claim narrowed | **REJECT** (still false) | APPROVE-W-C | APPROVE-W-C | earns credit | **SHIP** | ACCEPT | — |
| "dated observation" | **REJECT** (no mechanism) | APPROVE-W-C (needs decay) | APPROVE-W-C (needs field) | honest instrument | **SHIP-LATER** | honest only if it ages | best thing in the commit |
| §4(c) `C-PAYLOAD-REBUILD` | APPROVE-W-C | APPROVE-W-C | **REJECT as written** | — | **SHIP-LATER** | **ACCEPT as hygiene, REJECT as enforcement** | — |
| "15 of 15" as a figure | **REJECT** | — | 1 of 15 executes | management assertion | — | rename it | **REJECT the figure, APPROVE the register** |
| §5 open items left in prose | — | **REJECT as dispositioned** | — | — | SHIP-LATER | — | register NULL stratum today |
| CI / laptop-local gates | structural | (iii) next costume | **hiring blocker** | endangers gates 1,2,3,9 | **highest leverage in the pack** | **S1 common-mode** | 0 CI |
| AB-ATTRIBUTION | — | OPEN row | — | — | **SHIP FIRST** | decide this week | APPROVE-W-C, 1-of-5 |

**Q3 — disposition of the served contradiction (unanimous in direction, split on framing):**
Guardian *"the record is owed"* · Operator *"dated errata note; cost now near zero, cost in
diligence is the repeatability claim itself"* · Buyer's Desk *"log it in a standing incident
register — it converts the worst fact in this pack into the best control evidence in it"* ·
Statistician *"a note in the ledger — materiality low, precedent high"* · Expansionist *"display
defect; record that the window RECURS at any deploy rate above 4/day until the release phase ships"*
· Challenger **rejects the premise**: *"the window is not closed — `score: 0` beside UNMEASURED is
what the endpoint returns right now."*

---

## 4. THE ONE-LINE FIX EVERY SEAT CIRCLED

`transfer/Procfile` has **no release phase**; `backend/Procfile` already has one. Expansionist:
`release: python maint_precompute.py` makes the defect class structurally impossible and binds a
second engineer and a cloud agent. **Executioner dissents on placement:** `_precompute_serve_payloads`
NULLs every payload *first*, then rebuilds — a mid-run failure in a release dyno leaves every payload
NULL against the pool that caused the 2026-07-06 outage. His alternative: a **`PAYLOAD_SCHEMA_VERSION`
literal** stamped into each blob, with serve-side mismatch falling through to live calibration —
*"cannot serve a shape-stale blob," failure mode slower, never wrong.* **This disagreement is
unresolved and is the Chairman's call.**

---

## 4b. THE FINAL TWO SEATS (Economist, Forecaster) — findings not above

### ECONOMIST
- **Independently disproved the INV-1 attribution** from commit timestamps: `d_measured` entered
  the payload at `b39f2e3` 10:26, guard at `a650e18` 21:22 — **any blob containing `d_measured`
  was ≤11h old**, so the 48h verbatim-serve rule cannot have applied. Adds the operational
  consequence: **`[payload-rebuilt]` would not have prevented this** — the rebuild was never
  skipped; it ran every cycle and *propagated the half-state each time*.
- **The seal is cryptographically INTACT — credit.** He reproduced `text_sha256 403b6a7e…` from
  `body[:4065]`. **But he then mutated the sealed prose (`demote`→`PROMOTE`) and `_enforcer_live`
  still returned True.** A sealed forecast can be rewritten with the gate green.
  *Recurrence:* the **2026-08-18 board already prescribed recording exact extraction
  byte-boundaries**; the referee prereg complies ("5930 chars"); this seal, written 48h later,
  says only "body above this block" — he needed a brute-force sweep over ~27,000 candidate
  prefixes. **A remedy adopted and not carried forward two days later.**
- **New live defect:** `DarkMatterPanel.tsx:78-90` evaluates `ftr >= 0.35` **before**
  `dUnmeasured`. The badge is guarded; the sentence is guarded only because `ftr` happens to be 0.
  A payload with `d_measured=false` beside a stale ratio ≥0.35 renders *"X% of participants are
  new here… private-channel activity inferred"* **on an unmeasured topic.** The §3 defect survives
  inside the §3 fix.
- Verified the degenerate case **by execution**: emptied `CLAIMS`/`SEALED_CONSTANTS`/`SERVED_FIELDS`
  → `INTEGRITY GATE PASSED`, exit 0.
- **Next costume: the denominator** (converges with Statistician, independently). *"The org moved
  from claims with no enforcer to enforcers with no denominator."*
- **On "is the org telling itself this time is different?"** — *"Not in its prose, which is
  unusually candid. But structurally, yes: each round treats the recurrence as a NEW FINDING rather
  than as the n-th observation of one signature. Nobody has counted the recurrences. That absent
  count is the whole disease."*
- **P8 (unique to this seat):** D rewards first-timers and low-breadth signals — *precisely the
  profile an adversary manufactures most cheaply, since sockpuppets are first-timers by
  construction.* Seal D's dollar manipulation cost **before** D is scored.

### FORECASTER
- **Four-test instrument for "honest correction vs moved goalposts"**: T1 subset+re-assertion
  **PASS** · T2 falsifier preservation **FAIL** · T3 blind scoreability **SPLIT** · T4 ratchet
  **PASS**. *"T1 and T4 are what an author moving goalposts would not do; the author did them.
  But T2 is the test that matters."*
  **Replayed the incident: nothing in the register goes red today.** Net green INCREASED in
  response to a discovered failure — *"that is the tell, independent of intent."*
- **THE NO-NET-GREEN AMENDMENT RULE (proposed):** an amendment made after a row was observed false
  **may not reduce the count of red rows**. Amend the wording freely; **the redness is not
  amendable.** Ruled that the sealed-forecast amendment rule should NOT apply to register rows
  (they assert a present re-checkable state) — but green **is** a readout, so this rule replaces it.
- **Half-life of the dated observation is ≈8 HOURS, not 30 days** — derived from v367→v370 in ~24h
  and 5.75 commits/day since 08-01. *"A 30-day-old unrefreshed observation has survived ~90
  invalidating events. It is not weak evidence at that point; it is NO evidence, displayed green."*
  Prescribes `kind:"probe"` auto-demoting to OPEN at 48h **or on engine-version change**.
- **EXECUTED the deletion test:** removed the entire enforcement block from a copy of `commit-msg`
  (`grep -c 'payload-rebuilt'` → 0, gate physically cannot fire) → register printed
  `OK C-PAYLOAD-REBUILD`. Green on a comment at line 130. **"The remedy for 'a claim enforced by
  prose' is itself enforced by prose. The pack asks whether §4 moves the pattern one level out.
  It does, and here is the receipt."**
- **Two in-scope FALSE NEGATIVES the gate misses:** editing **`_explain_d` (:13097) — the exact
  function that emitted the incident text — does NOT trigger the gate.** Nor does
  `nowtrend_integration.py:946`, a parallel `plain_english` builder.
- **The marker cannot distinguish assertion from DENIAL:** a message reading *"note: I did NOT run
  [payload-rebuilt] yet, TODO"* passes, exit 0.
- **Credit, verified:** replaying the trigger across all 115 August commits, **exactly two would
  have fired — `a650e18` and `9b480fe`, precisely the two commits that produced the incident.**
- **Recursion base rate: 4 of 4 rounds found the class inside the prior round's remedy**;
  Laplace-corrected forward estimate **0.83**.

### FORECASTER'S SEALED PREDICTIONS (scoreable by a third party; amendment after readout void)
| id | claim | date | p |
|---|---|---|---|
| P1 | ≥1 NEW instance of the class named in a commit or board doc | 2026-09-03 | **0.93** |
| P2 | ≥1 commit lands that a gate would have refused, with **no hook run at all** (2nd clone / cloud agent / web edit / `--no-verify`, which leaves **no trailer**) | 2026-09-20 | **0.70** |
| P3 | an enforcer passes because a **hand-maintained list** shrank or failed to grow | 2026-10-05 | **0.55** |
| P4 | `_enforcer_live(kind='hookgate')` is **still a substring test** | 2026-08-27 | **0.55** |
| P5a | AB-ATTRIBUTION actually run (`tools/d_plumbing_ab.py` in main + row-level JSON) | 2026-08-27 | **0.55** |
| P5b | FULL spec delivered (all three decompositions) | 2026-08-27 | **0.30** |
| P5c | row RESOLVED either way (run, or recorded PERMANENTLY UNMEASURABLE) | 2026-08-31 | **0.85** |

**Forecaster's deadline correction:** the cohort arm needs pre-08-20 signals, which prune around
**08-26, not 08-27** — one day optimistic. The forced-flag arms need no historical rows at all.
**"Export the cohort to a file and the deadline stops being hard. Cost: minutes. This should
happen even if the A/B never runs."** *If the snapshot is not frozen by 08-24, revise P5a to ≤0.20.*

---

## 5. WHAT NO SEAT DISPUTED

The narrowing of a claim to what its enforcer proves is the correct direction (6 of 7 explicit).
Selecting the probe row by the antecedent `WHERE d_measured = 0` is methodologically correct on
that axis (Statistician: *"choosing on the DV would be `WHERE plain_english LIKE 'UNMEASURED%'`"*).
The gate-chain `exit 0` fix is real and was independently reproduced. The `$msg`/`$MSG` catch under
`set -u` is credited. **And in every round to date the defect was found by EXPERIMENT — running the
gate, probing production — never by source review. Review is 0-for-4** (Operator, S5).
