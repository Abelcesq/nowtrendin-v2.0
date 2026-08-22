# EVIDENCE PACK — 72-HOUR REVIEW
### Chairman-commissioned 2026-08-22. Nine seats. Question: did we ACTUALLY address your prior
### concerns, and what must be addressed next?

**33 commits, 2026-08-19 → 2026-08-22. Two full nine-seat boards (round 4, round 5) inside the
window.** Verify everything below against the repo. Where this pack is wrong, say so — it has been
wrong before, twice, and both times a seat caught it and the author had not.

---

## 0. WHAT YOU FOUND, AND WHAT WAS DONE ABOUT IT — the honest scorecard

### FIXED, WITH A NEGATIVE CONTROL PROVEN TO FIRE

| Your finding | Fix | Proof it fires |
|---|---|---|
| **Forecaster:** mutated every binding number in the sealed kill criterion; `_enforcer_live('sealed')` returned GREEN | Enforcer now RECOMPUTES `text_sha256` over a recorded byte boundary | `test_seal_enforcer.py` 8/8 — t3 is the exact Part A substitution, t5 one inserted byte, **t6 the control on the control** (append below the boundary must stay green), t7 refuses a seal publishing no digest |
| **Forecaster vs Economist:** irreconcilable dispute over whether the seal reproduced at all | **RESOLVED by exhaustive brute force over every prefix length**, not another recipe guess. Seal is INTACT: 4100 bytes LF-normalized == 4065 chars (em-dashes are 3 bytes). Both seats were right; the units differed. Byte-exact extraction recipe now recorded in the doc, below the hashed boundary | recipe verified to leave the seal green |
| **Executioner:** `SIGNAL_RETENTION_DAYS` 7→30 lived only in a Heroku config var — a rollback silently destroys the POST-flip AB-ATTRIBUTION arm | `SIGNAL_RETENTION_FLOOR_DAYS = 30` sealed literal under L1; env may RAISE, never lower | L1 goes RED when converted to `getenv`; 6-case behaviour test incl. the rollback-to-7 failure mode |
| **4 seats:** `d_at_enroll` stamps the magnitude but not the measurement flag, while `d_measured` sits in the same table unselected (live `unmeasured_fraction` 0.752) | `d_measured_at_enroll` stamped in the same SELECT. NULL when unknown, **never 0** | forward-only; every day of delay was permanently un-triageable population |
| **Statistician:** no immutable entry time; `last_checked` is overwritten by every sweep, so left-truncation is unbuildable | `enrolled_at` immutable column, carried through resolution | — |
| **Expansionist + Executioner:** `breadth_at_enroll` NULL on **every live row** (`LEDGER_AB_D9` defaults "0"), unrecoverable once `topic_signals` prunes | `corroboration_at_enroll` stamped on the LIVE path as the §15a `min(distinct sources, distinct titles)`. Deliberately NOT reusing `breadth_at_enroll`, which is a PLATFORM count — conflating them is what made it look stamped | — |
| **Buyer's Desk + Economist:** `category` assigned by `_category_for`, whose maps swing 33%↔68% on restart — two users on two dynos see different rates for the same topic | `category_at_enroll` stamped from the **stateless** `_topic_category`, fails open to NULL | — |
| **Guardian F-1:** the Market surface would violate the R1 ruling sitting verbatim in `arrival_clock.py` — *"NOT PRICE… a trading record with the P&L column hidden"* | `panel_invariants.assert_participation_clock` RAISES on any payoff ledger or non-participation event | `test_panel_invariants.py` t1 is that exact surface; **de-listing the market ledger turns the fixture RED** |
| **Economist item 8:** reflexivity — the display feeding the OUTCOME that validates it, a circularity the N-exclusion rule does not cover | R2 gate, **scale-triggered**, trip sealed at 250 while the audience is 5 seats. Three states kept distinct: publish / publish-excluding-displayed / **serve ABSENT** | making ABSENT return a rate turns the fixture RED; trip→`getenv` turns L1 RED |
| **Statistician + Executioner:** the `d_measured` NULL stratum — `None != 0` and `None == 0` both fall through, so >90% of topics served a numeric ratio + "originates publicly" | Affirmative branch now **opt-IN** (`== 1`). UNKNOWN and UNMEASURED kept DISTINCT, not pooled | `test_d_tristate.py` 9/9 — t5 no non-1 value reaches the affirmative narration; t7/t8 fail on regression to `!= 0` |
| **Guardian + Challenger:** `WhyScoresDiverge.tsx` has no `d_measured` guard at all | guarded; renders "Unmeasured" | — |
| **Economist:** `DarkMatterPanel` evaluates `ftr >= 0.35` BEFORE `dUnmeasured`, so a stale ratio at threshold renders "private-channel activity inferred" on an unreadable topic | unmeasurability checked before any threshold | — |
| **My own phantom control** (found while fixing the above): a negative control that mutated strings not present in the file, matched nothing, and reported ENFORCER BROKEN twice | **L4 lint** — a test that mutates and feeds a gate must assert the bytes changed | stripping the guards from `test_seal_enforcer.py` turns the gate RED and names the file |
| **Buyer's Desk:** accuracy doc led with 27.1% from the RETIRED v1 engine | reversed: leads with 5.0% (n=20, current engine); 0-of-15 referee corroboration promoted out of the footnote; prior sentence retained verbatim under the ratchet rule | — |
| **Two seats:** AB-ATTRIBUTION pre-flip inputs ~1 day from pruning | 342,661 rows frozen, sha256'd, manifest committed | oldest surviving row was 08-14, pruning 08-21 — the tracker said 08-27 |

**State: gate 19/19 asserted claims enforced · suite 13 files, 13 passed, 0 failed · firewall ok, 0 violations.**

### REJECTED BY YOU AND NOT BUILT
Part A (the D retirement rule) — **nine seats, nine routes, unanimous**. The sealed
`D_KILL_CRITERION_2026-08-20` stands unamended. Not built, not sealed, not registered.

### NOT DONE, AND NOT CLAIMED
`pit_store.as_of()` · the Base Rate Panel itself · CJK `_title_sig` (ruling 5, score-affecting) ·
D neutral-baseline treatment (3c, §16a stage-3 gated) · release-phase/schema-stamp (2c) ·
`tools/d_plumbing_ab.py` · auth + log drain on `/scores` (9) · board-on-a-schedule (10) ·
register truthfulness sub-items (6) beyond the `sealed` enforcer · **and the deploy+rebuild owed
on the 4c change (see §1).**

---

## 1. WHAT THE AUTHOR GOT WRONG IN THIS WINDOW — stated because you will find it anyway

1. **I asserted `d_at_enroll` did not exist.** It had been stamping rows for four days. I repeated
   it from an outside analysis without reading the schema — the §10a failure round 4 was convened
   over. **Six of nine seats caught it.** The Executioner's line stands: *"the pack argued a
   governance conflict for two pages over whether a database column exists."*
2. **I passed through Part B's claim of `as_of(t)` point-in-time integrity.** `pit_store.py` has no
   reader; its own docstring says nothing ever reads it. **Our own DDQ already said so.** I had the
   truth in the building and did not open the file.
3. **I overstated crypto absence** ("no source delivers per-coin money movement"). Current
   instrument reads absent; a subset is buildable and unbuilt. Two seats split on this and both
   were partly right.
4. **I reported the AB-ATTRIBUTION clock closed.** It was HALF closed — the snapshot covered the
   pre-flip arm; the post-flip arm was defended by an unversioned config var until yesterday.
5. **I wrote a negative control that tested nothing** and was one message from escalating a live
   defect in a seal that was intact. L4 exists because of it.
6. **I introduced an arity bug** (22 columns, 20 placeholders) that would have thrown on the first
   resolution, and caught it only by counting mechanically. Reading it is what missed it.
7. **The serve-payload gate refused my own 4c commit.** I did **not** type `[payload-rebuilt]` —
   that marker asserts a deploy+rebuild+probe I have not performed. Committed with an explicit
   searchable trailer (`Payload-Rebuild-Pending: YES`) rather than a silent `--no-verify`.
   **The 4c fix is therefore NOT live.** It is committed and unverified in production.

---

## 2. THE ARITHMETIC THAT DID NOT CHANGE

Nothing in 72 hours moved these, and every seat should weigh the fixes against them:

- **58 resolved tracked races. 15 LED. 0 of 15 corroborated by the independent referee.**
- **Tracked-race 25.9%, Wilson CI [16.3%, 38.4%], against a 50% random-order null — the interval
  excludes the coin flip FROM BELOW.**
- Portfolio credibility **Z ≈ 0.24**; the proposed 4-factor panel design **Z ≈ 0.014–0.03**.
- **3.4 years** to one credible portfolio cell; **~92 years** for 27 cells.
- Live `unmeasured_fraction` **0.752**.
- Governance throughput still exceeds measurement throughput: **two nine-seat boards and 33 commits
  in 72 hours, against 58 resolved races in thirteen months** (Operator S7).

---

## 3. THE QUESTIONS

1. **Did the fixes address the CLASS or only the INSTANCE?** Round 4's recurrence estimate was 0.83;
   the Forecaster's round-5 P26 predicted the instances would be fixed and the class would not.
   Test it: is there a register row today whose enforcer still cannot fail when its claim becomes
   false?
2. **Is the enforcement now real, or has it moved out one more level?** The `sealed` enforcer
   recomputes a hash — but the gate still runs only from a laptop-local `core.hooksPath`, and there
   is still no CI. Five of the last six remedies were commit-time artifacts.
3. **Does the L4 lint generalise, or does it catch exactly one shape?**
4. **The 4c fix is committed and NOT deployed.** Is a fix that exists only in the repo a fix? What
   is the correct disposition of the `Payload-Rebuild-Pending` trailer as a mechanism?
5. **Given §2, has anything changed that should alter your standing verdicts** on the panel, on D,
   or on what may be said to a buyer?
6. **What must be addressed NEXT** — ordered, with what you would CUT? Note the Operator's rule
   that the next convening condition should be a DATA event, not a calendar date.
7. **What is the pattern's next costume?** It has been named five times and found by experiment
   every time; source review remains 0-for-5.

**Standing constraints:** no circular metrics · held-out means held out · flag-never-force ·
measurement not advice · §16a honest absence · score-affecting changes are backtest-gated and
board-reviewed · the §15a A3 hard fence.
