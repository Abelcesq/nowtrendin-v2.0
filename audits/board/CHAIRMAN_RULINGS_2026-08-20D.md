# CHAIRMAN RULINGS — board round 4 (2026-08-20). Implementation ledger.
### Rulings given on the ten options in `BOARD_round4_2026-08-20D.md`. This file is the
### authority on WHAT WAS ORDERED vs WHAT IS DONE. A row is DONE only when its verification
### line is satisfied — not when the code is written. (Board round 4's own lesson.)

| # | Ruling | Status |
|---|---|---|
| 1a | Snapshot pre-flip cohort | **DONE** `e4215d4` |
| 1b | Raise `SIGNAL_RETENTION_DAYS` | **DONE** 7 → 30, engine |
| 1c | Run paired A/B (w/ rank-1 caveat) | **TODO** |
| 1d | Record in `REGIME_LEDGER.md` | **TODO** |
| 2c | Release phase **AND** schema stamp | **TODO** |
| 3b+3c | OPEN row + stage-2 disclosure, **and** backtest toward neutral baseline | **TODO** |
| 4c | NULL tri-state: serve fix **AND** backfill | **TODO** |
| 5 | CJK `_title_sig`: backtest + board note | **TODO** |
| 6 | Register truthfulness (six sub-items) | **TODO** |
| 7 | Runtime invariant **AND** synthetic probe | **TODO** |
| 8 | Accuracy figures — reverse the lead | **TODO** |
| 9 | Erratum **AND** auth **AND** log drain on `/scores` | **TODO** |
| 10 | Board on a schedule | **TODO** |

---

## 1c — PAIRED A/B RECOMPUTE
Build `tools/d_plumbing_ab.py`, runnable **offline against the frozen snapshot**
(`audits/ab-attribution/*.jsonl`) so it no longer races retention.
- Force `_D_PLUMBING_V2` True/False over identical rows. **Verify first** that the flag is read
  at compute time and not baked into stored columns — if it is baked, the arm is void.
- Run the **T3 null-treatment check FIRST** (Statistician): per `f5b1956` Reddit was 403-ing for
  two months; if pre-window Reddit rows ≈ 0, T3 drops and the confound set falls 5 → 4 for free.
- Pre-register ONE primary contrast (T5 main effect on D, pooled). The other 14 are exploratory
  under Benjamini–Hochberg. **Uncorrected, P(≥1 false positive) = 53.7%.**
- Report the **paired within-topic difference** with a bootstrap CI over topics. The recompute is
  deterministic over identical rows, so the T5 delta is EXACT, not estimated; the uncertainty is
  over *which topics*.
- Any cohort under ~30 rows with resolved authors → output **"underpowered, not estimable."**
- **MANDATORY OUTPUT LANGUAGE:** the result identifies ONE of five treatments, conditionally
  (`E[T5 | T1..T4 = ON]`). T1–T4 main effects are **permanently unidentified by design, not by
  data loss.** The artifact must say so or it will be misread as an untangling.

## 1d — REGIME LEDGER
Record: the flip, the five treatments, the snapshot (counts + sha256), the rank-1 limitation, and
that the written 08-27 deadline was wrong by ~6 days (oldest surviving row 08-14 → pruned 08-21).

## 2c — BOTH REMEDIES (the board split; Chairman took both)
- **(a) Expansionist:** `release: python maint_precompute.py` in `transfer/Procfile`.
- **(b) Executioner's dissent stands and must be honoured in the implementation:**
  `_precompute_serve_payloads` NULLs every payload FIRST. A mid-run release failure leaves every
  payload NULL against the pool that caused the 2026-07-06 outage. **Therefore the release-phase
  form must be made non-destructive (build-then-swap, or skip-on-error) before it ships.** Do not
  ship (a) in its current destructive-first form.
- **(c) `PAYLOAD_SCHEMA_VERSION`** as a code LITERAL, added to `SEALED_CONSTANTS` (so L1 guards it
  against becoming an env var), stamped into each blob; serve-side mismatch → ignore blob, fall
  through to live calibration. Makes `[payload-rebuilt]` redundant — retire the marker after.

## 3b + 3c — THE D SCORE FLOOR
- **3b (not score-affecting, do now):** OPEN register row + `DEFERRED_ITEMS.md` row + §16a stage-2
  disclosure. `compute_dark_matter` returns `0.0` on the unmeasured path; the docstring's "count at
  the neutral value" is false — **0 is the floor, not neutral, on 0–100.**
  Guard `WhyScoresDiverge.tsx:21-22` (no `d_measured` reference at all) and `Grade.tsx:51`.
  Fix `DarkMatterPanel.tsx:78-90`: the ternary evaluates `ftr >= 0.35` BEFORE `dUnmeasured`.
- **3c (score-affecting, gated):** backtest toward neutral-baseline treatment; board note; never
  an env flip. §16a forbids skipping stages 1–2 to reach 3.

## 4c — NULL TRI-STATE (largest live blast radius, est. >90% of topics)
- **Serve fix:** treat `d_measured is None` as unmeasured-**unknown** — `first_timer_ratio: null`,
  no affirmative `_explain_d`, distinct note ("never measured" ≠ "measured and blind").
  Executioner: **no rebuild needed**, this path is live-computed.
- **Backfill** the column so the stratum stops growing; dormant topics otherwise stay NULL forever.
- Verify on a topic last scored **before** 2026-08-20.

## 5 — CJK `_title_sig` (score-affecting)
CJK has no spaces → `" ".join(t.split()[:10])` is a no-op → exact-string, not prefix, matching.
Five CJK mastheads on one wire story read as five voices → `mainstream_confirmed`, where English
correctly collapses to one and stays a Dark-Matter trigger. **Fails OPEN** in the largest
non-Latin market. Segment via ICU/jieba or character-bigram signatures. Backtest + board note.
Ranked FIRST among gated items because failing open eats early signal invisibly.

## 6 — REGISTER TRUTHFULNESS
1. Move the count **after** the lints (today it prints from `bad_ids` at :208 while L1/L2/L3 append
   afterwards with `L1:` prefixes that never collide with `C-` ids → green on a run that exits 1).
2. **Freeze the denominator:** ASSERTED→OPEN keeps the row in the denominator with a `demoted`
   flag, so the ratio cannot be improved by demotion. (The gate's own failure text currently
   *instructs* the demotion that inflates it.)
3. Publish `N enforced / M asserted / K open / **J falsification-tested**`. J = 1 of 15 today.
   Delete the percentage from every board-facing and external artifact.
4. `kind="hookgate"` must **execute the hook against a violating fixture and require exit 1** —
   the Forecaster deleted the whole enforcement block and the row still printed OK on a comment.
5. `kind="lint"` is `ref in ("L1","L2","L3")` — **constant True, 3 of 15 rows.** Make it run the lint.
6. `kind="test"` must RUN the test, not grep a marker. Fail on `len(CLAIMS)==0` (verified: an
   emptied register prints `0 of 0` and PASSES).
7. **Adopt the Forecaster's NO-NET-GREEN AMENDMENT RULE:** an amendment made after a row was
   observed false may not reduce the count of red rows. Wording is amendable; redness is not.
   `C-DMEASURED-SERVED` gets a red/OPEN sibling until an enforcer FAILS on a fixture reproducing
   the incident (its T2 test currently fails: replay the incident and nothing goes red).
8. L3: enumerate every surface reading `firstTimerRatio`/`darkMatter`, require each to reference
   the flag, fail closed on a new unlisted component. Stop `break`-ing on the first hit (which is
   a **comment** at `Screener.tsx:134`). Extend the hook trigger to `web-terminal/src` + `frontend`
   — today a commit deleting the guard from `Screener.tsx` alone never runs the enforcer.
9. `sealed` enforcer must recompute the cited `text_sha256` via `pit_store.verify()`. The seal IS
   intact (Economist reproduced `403b6a7e..` from `body[:4065]`) but he mutated `demote`→`PROMOTE`
   and the gate stayed green. Also: record exact extraction byte-boundaries, as the **2026-08-18
   board already prescribed** and this seal, written 48h later, did not carry forward.
10. Schedule `pit_store.verify()` — it exists at `:373` and nothing calls it but an endpoint param.

## 7 — RUNTIME ENFORCEMENT (the Guardian's kind-change: commit-time cannot observe run-time)
- **Guardian:** extend `monitoring_agents.py:483` from staleness-shape to **contradiction-shape** —
  no served object may carry `d_measured=false`/`null` beside affirmative origin prose, or a
  measured badge on a floor value. Alarm at `>0`, census not sample (today: `detection_score` only,
  |Δ|>2.0, 40-row sample — structurally blind to payload SHAPE).
- **Expansionist:** scheduled **synthetic production probe** over a fixture set — one row per
  script, per region, per lane (the Cyrillic row is a fine first member) — asserting the invariant
  and writing a dated pass/fail. This is what makes "dated observation" an instrument: the
  Forecaster puts its true half-life at **≈8 hours** (v367→v370 same day), so it must auto-demote
  to OPEN at 48h **or on engine-version change**, whichever is first.
- Widen the serve-payload gate to `_explain_*`, `plain_english`, and `nowtrend_integration.py`
  (editing `_explain_d` — the function that emitted the incident text — does NOT trigger it today).
- Commit `.gitattributes` with `*.py diff=python`; the hunk-header trigger currently rides git's
  undeclared default heuristic and silently misses methods and nested functions.

## 8 — ACCURACY FIGURES (free, do first among the non-clock items)
`docs/buyer-diligence/ACCURACY_FIGURES_SCOPED.md` §4 leads with 27.1% / 48 races while §1 discloses
that 76 of 111 resolved rows come from the **retired v1 engine** and the current engine reads
**2.9% blended / 5.0% tracked, n=20**. Reverse it: lead with 5.0% (n=20, current engine); offer v1
as history. This is the App Annie shape — misdescribing methodology to buyers — and costs nothing.
Also surface from the footnote: **0 of 13 LED wins corroborated by the referee**; 10 on ambiguous
single-word queries.

## 9 — ERRATUM + AUTH + LOG DRAIN
- **Erratum row** (standing incident register): window `a650e18` 21:22:25 → v370 precompute, the
  field pair, surfaces, **the CORRECTED mechanism** (deploy-version window, NOT INV-1), and the
  §10a violation. Buyer's Desk: this converts the worst fact in the pack into the best control
  evidence in it.
- **Auth on `/scores/{topic}`** — today it has no auth dependency (contrast `/usage`).
- **Log drain** — none configured; Heroku router logs are ephemeral, so "who received it" is
  currently *unanswerable*, not merely unanswered. Also needed for the index determination record.

## 10 — BOARD ON A SCHEDULE
The round's yield: nine independent seats found six defects the enforcement machinery found zero
of, two larger than the incident under investigation, and falsified the root cause four ways.
**Independent-seat convergence is currently the only control in this system that works.** Put it
on a cadence (with `/improve-system`, Sat 06:01), not on demand.

---

# SECTION B — BOARD ITEMS WITH NO HOME IN THE TEN OPTIONS
### Raised by seats in round 4, outside the ten items ruled on. Recorded here because the
### Guardian's REJECT was precisely that known-open work living in prose is a TODO in a drawer.
### NOT independently re-verified by me — these are as-reported by the seats. Verify before acting.

## B1 — THE FOUR "FREE NOW, IMPOSSIBLE LATER" ITEMS (same class as 1a; highest priority)
- **IDX-RC4 — index self-influence baseline (Operator).** The null is measurable ONLY at AUM=0
  and zero readership. The first demo, newsletter, or licensing conversation showing an index
  value destroys the baseline **permanently**. Every unpublished day without the monitor is
  baseline forgone. Build the monitor while it is still free.
- **IDX-RC3 — capacity cap (Operator).** Written as "freeze before the first license is signed."
  Correction: **freeze before any CONVERSATION.** At signature you have the least freedom you
  will ever have.
- **Tail-conditioned arm of the D kill criterion (Economist P3, Taleb).** Attention lives in
  Extremistan; a mean-based threshold kills a detector that is right about the 2% that matter.
  Pre-commit a hit rate restricted to topics whose eventual peak lands in the top decile,
  alongside the blended rate. **Worth nothing unless sealed before results are knowable.**
- **D's manipulation cost (Economist P8, Adam Smith).** D rewards first-timers and low-breadth
  signals — the profile an adversary manufactures most cheaply, since **sockpuppets are
  first-timers by construction**. Seal the dollar cost to move a topic's D by a stated amount
  BEFORE D is scored, or the threshold gets chosen after the answer is known.

## B2 — COMMERCIAL BLOCKERS (Buyer's Desk, both outright REJECT)
- **Gate 6 IDENTIFIERS.** Ticker strings only; no FIGI/CUSIP/permID; the attention leg has **no
  instrument identifier at all**. *"A fund cannot join topics to its book."* Everything upstream
  is unmonetizable until a mapping layer exists. Decide: OpenFIGI on the instrument legs + a
  curated topic→issuer map, or sell the attention leg only to non-quant buyers.
- **Gate 7 COVERAGE.** Distinct-mapped-ticker count and coverage-by-month series **never
  compiled**; nothing run against the 75-ticker quant threshold. Deliverable: one chart —
  mapped instruments per month since inception, **degenerate share shaded** (§16a means coverage
  and USABLE coverage are different numbers, and neither is charted).

## B3 — COMPLIANCE / LEGAL
- **Rights H3:** the direct-RSS class (FT, Economist, BBC, CNBC, Guardian, ~20 more) has **no
  outlet-level permission document**. Metadata-only ingestion with derived-aggregate output is a
  defensible posture; it is not a right. **H8:** Google Trends arrives only via Apify with no
  Google-side license. Answer point-blank: *if the FT sends a letter next month, which feeds turn
  off, and what happens to the score that day?*
- **PII erasure path.** The author store has **no retention limit and no deletion mechanism**,
  while D is computed FROM resolved authors. Answer mechanically: a named forum user requests
  deletion — what happens, and does the first-timer ratio change?
- **`D_dark_matter` / `darkMatter` API field name.** Display was renamed to "Under-the-Radar"
  (`cb44e04`); **the payload was not** — and under ruling (f) the payload IS the licensed
  product. "Dark matter" reads to a CCO as "information other people can't see." Finish the
  rename in the payload.
- **Trial-license notification trigger** — write it now, while no customer exists and it is free.

## B4 — ECONOMICS
Cost Sentinel **CRITICAL $718.82 vs the $700 cap**, and the accuracy ledger — the moat —
resolves through a **single metered vendor**. Unanswered: *if Apify triples its price, does the
ledger stop resolving, and what is the second source for that validation curve?*

## B5 — MEASUREMENT (each changes what may be CLAIMED)
- **Construct validity of `d_measured` (Statistician).** Everything tested so far is whether the
  DISPLAY discriminates. Nothing tests whether the flag is **assigned correctly**. Needs an
  independent labelled audit of the author-resolution path.
- **Publish `n` + the unmeasured count beside EVERY rate (Economist P7).** A rate whose
  denominator silently includes unreadable rows is the A3 sin relocated from the score to the
  statistics.
- **Recurrence ledger (Economist P6).** Append-only; one CLASS id per defect; a row per
  recurrence with date, costume, and the register it hid in. **The row count IS the metric.**
  Today's was roughly the sixth instance of one class and nobody has counted — *"that absent
  count is the whole disease."*
- **Time-to-detect (Operator S5).** Stop scoring "we caught it ourselves"; a run of self-caught
  defects is equally consistent with a change rate manufacturing defects faster than review finds
  them. Today's contradiction was live for hours; that metric has n=1 and no instrument.
- **Captured, hashed probe artifacts (Challenger).** The probed blob no longer exists — no
  retained JSON, no hash, no request id — in a codebase that PIT-seals its forecasts.

## B6 — HYGIENE
- `rsd.py` and `maint_precompute.py` call `_precompute_serve_payloads(600)` **outside the gate and
  outside the endpoint's auth**. Consolidate or delete.
- The five hand-maintained lists (`SRC_FILES`, `UNIV_FILES`, `SEALED_CONSTANTS`, `SERVED_FIELDS`,
  `NETWORK_TESTS`) **fail silently OPEN when they shrink** — the Forecaster's P3 prediction
  (p=0.55 by 2026-10-05).
- Deploy skill gains the sequence: full suite → deploy → `POST /precompute` → re-probe →
  **check `/prewarm last_run`** (the wedged-prewarm outage class).

---

## STANDING CORRECTIONS TO THE RECORD (carry forward; do not re-assert the old forms)
- **INV-1 did NOT cause the 2026-08-20 contradiction.** Deploy-version window. `s = json.loads(
  _payload)` at `:11680` → all four D fields come from ONE dict, so a stale blob makes them
  consistently stale, never contradictory. The exact sub-mechanism at probe time (fleet split vs
  `≤120s CACHE_TTL_DETAIL`) is **still not traced to a line** — do not assert either.
- **`[payload-rebuilt]` would not have prevented it.** The rebuild ran every cycle and propagated
  the half-state each time.
- **"Same dict literal" is a valid ELIMINATOR, an invalid SELECTOR.** It rules out partial code
  application *within one process*; it does not rule out two processes on different code.
- Suite is **9 passed / 1 skipped**, not 10/10. `test_etf_issuer_pages.py` is run by no gate.
- Verification was at `top_n=800`; the scheduler rebuilds **600**. Verified state ≠ steady state.
- **Not yet checked, do not act on it unverified:** the outside review's claim that the fabricated
  D zero invalidates our `D_KILL_CRITERION`. Ours judges race rates and lead times between arms,
  not D magnitudes, and `shadow_enroll` enrolls on first-crossing, not a D threshold — so the
  contamination binds only if arm assignment or enrollment touches D. **Verify before amending
  anything sealed.**
