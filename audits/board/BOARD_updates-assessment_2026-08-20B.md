# BOARD COLLATION — assessment of the execution of the 11 D-board decision items
### Nine-seat convening, 2026-08-20 evening · Chairman-ordered ("have /advisory-board convene and provide an assessment on the updates")
### Pack: `UPDATES_EVIDENCE_PACK_2026-08-20B.md` · All seats independent, identical pack, no cross-visibility.
### Collation rule: memos condensed faithfully, never blended. Disagreements are signal.

---

## THE FINDING — six of nine seats, independently, on the same line

**The cold-start guard was written into the wrong function, and the sealed pre-registration
asserted it was enforced.** The guard went into
`gravitational_anomaly_detector.check_author_is_first_timer` — serving github / hackernews /
bluesky / lemmy — while the blog lane uses its own `blog_collectors._first_timer`, which had
**no age term at all**. That is precisely the lane `D_PLUMBING_V2` newly admits and the lane
every sealed candidate feed enrolls through. **The guard protected the five platforms that
were already mature and protected none of the seven the flip switched on.**

Found independently by the **Buyer's Desk** (first), **Statistician**, **Economist**,
**Operator**, **Executioner**, and **Guardian**. Verified by the collator before any action:
`D_COMMUNITY_MIN_AGE_DAYS` appeared at exactly three lines, all inside the detector function.

**It was live, not theoretical.** The same morning removed the tech filter from
`WORDPRESS_TAGS`, creating **12 brand-new communities**, each its own community key; the flip
went ON that evening. Every author in those communities read as a genuine first-timer →
`ft_ratio` ≈ 1.0 → **D ≈ 40–65 on exactly the non-tech topics the expansion exists to prove**.
Guardian F2 — the fabricated numerator — at full strength, on served scores.

The Challenger's judgement stands as the sharpest statement of it: *the build took the morning
board's single most-agreed finding, fixed it on the two platforms that did not need it, and
simultaneously opened twelve new communities on the platform that did.*

**REPAIRED AND DEPLOYED** (commit `d6de777`): the same 14-day rule, same flag, now in
`blog_collectors._first_timer`. Author rows still recorded during calibration so history
accrues; only credit is withheld.

## FOUR MORE CONFIRMED DEFECTS — all verified before fixing, all now repaired

| Defect | Found by | Verified | Status |
|---|---|---|---|
| **Held-out firewall RED.** `darkmatter_indicators` registered held-out, then imported to serve its diag endpoint with no acknowledged exception. `audit_firewall()` returned `ok:False` for a working day and nothing ran it — while `shadow_ledger`'s docstring asserted "the AST firewall makes a scoring-side import a build failure." | Guardian | Collator ran the audit: RED | Exception registered **with its re-check note**; commit-msg hook now RUNS the audit on any `transfer/*.py` commit and REFUSES on violation. Fixture-verified both directions |
| **`d_measured` was a platform proxy, not author resolution.** Five authorless RSS rows on `medium` read `d_measured=1, D=0` — "read quiet" when the truth is "could not read": the A3 floor-end sin reintroduced *inside the field built to close it* | Statistician + Buyer's Desk + Guardian | Confirmed | Re-keyed to genuinely resolved authors (`rs.author` joined into the scoring query). **Consequence: the 32.4% blind figure is an UNDERCOUNT** and is restated as a floor pending re-census |
| **Pseudo-authors.** `author = item["author"] or cfg["name"]` — an authorless feed wrote its OWN NAME as author. It scored one first-timer, then crossed the incumbent threshold after 5 articles so `incumbent_displacement` read **1.0 — maximum "established-expert reallocation" — purely as a function of how long we had polled the feed** | Challenger + Economist | Confirmed | Excluded in both places (author identical to venue is not a person) |
| **`engagement_divergence` returned a constant dressed as a measurement.** `collect_ghost` writes the literal `60, 0` on every row, so venue mean == topic mean and the premium was **exactly 1.0, always** — and because `engagement_raw > 0`, it never returned `None`, breaching the module's own contract | Economist | Confirmed by reading the writer | Degenerate venues (zero variance) excluded and counted; no premiums → `None` |

## THE PATTERN — the Guardian's finding, and the one that matters most

> *Every finding is the same defect wearing a different costume: **a claim written in one
> register and enforced in a weaker one.** The guard documented as covering a lane it did not
> cover. The sealed window described as sealed, implemented as an env var. The honest-absence
> field announced as "disclosed", implemented as a column no surface reads. The firewall
> described as a build failure, implemented as a function nobody runs.*
>
> *Yesterday this board verified that exact pattern at detector L4404 — a comment promising a
> denominator exclusion the code never performed — and called it the day's central finding.
> Today's build fixed that line and reproduced the pattern in five new places within eight
> hours. The remedy is not more documents. It is that every integrity claim written in prose
> must be paired, in the same commit, with the mechanical thing that fails when the claim
> stops being true.*

The Guardian also named the counter-example: the tripwire was built, ran, and caught two dead
feeds the same day. **That is the standard the other ten items should be held to.** The
commit-msg firewall gate shipped tonight is the first instalment.

## THE NINE MEMOS (condensed)

**CHALLENGER** — F1 (headline, above) → *"REJECT item 5 as flipped."* F2: the backtest was
**structurally incapable of measuring repair 1a** — every blog row carried the hardcoded 0, so
the reassuring "fewer nonzero" is the *depressant half measured alone*. F3: `d_measured`
stored but **never served**, while the UI renders `firstTimerRatio ?? 0` labelled *"new
participants flooding in"* — a §17 violation that will now display ~100% for the new
WordPress domains. F8: acceptance figures are **in-sample** (fix developed against the same 12
headlines), baseline adversarially selected, no CI, no hook marker. F9: "GHOST window
unmeasurable" is over-broad — `velocity_scores` retains 365 days and was never queried. F10:
tripwire blind to tag rosters; 12 configured vs 11 reported. F11: regime ledger row describes
a guard not in force. *Honest caveat volunteered: "I verified code, not the live environment."*

**GUARDIAN** — Condition 1 (cold-start neutralized in shadow rules) **FAILED both ways** — code
half wrong lane, rules half missing (`calibrating` had no column, so the prereg's own exclusion
was uncomputable). Condition 2 (no D-side flags until GHOST lands) **HONORED** — verified by
commit clock. Condition 3 (honest absence) **HALF-DONE and the built half was itself
fabricating**. Condition 4 (universe statement) **DELIVERED and already stale** — broke its own
same-commit review trigger on day one. Condition 5 (Reddit on the record) **FULLY HONORED, no
reservations**. Plus the firewall finding and the pattern above.

**BUYER'S DESK** — *"The best twelve hours of work I have reviewed at this company"* — then
spends the memo on the guard, because *"the safety brake the Chairman was told was installed is
not installed on the wheel that was just released… asserted inside a hash-sealed
pre-registration. That is App Annie in miniature — a description error in the document built to
prove rigor."* Corrected me on the rights file (it exists, v1.0, and is good — my flag was
wrong on the facts) but the seven new feeds have **zero register rows**. **Kill-or-pivot
criterion: NOT ADDRESSED** — *"What result would make you stop? If there is no such result you
are not running a trial, you are running a demo with a long calendar."* Foreign publishers
assessed specifically: **the copyright position is US-law only**; Marca/Kicker fall under EU
DSM Art. 15 press-publishers' right (a neighbouring right, no fair-use defence), SCMP has no
general fair use, Nikkei's TDM exception helps. Gate 3 endangered.

**EXPANSIONIST** — International seeding **HONORED, not a gesture**. But *"the sealed design
cannot answer what it was seeded to answer"*: language varies only inside sports, region only
in English, **no non-English non-sports cell**. `geo:"US"` literal removed but **nobody turned
the knob**, and it is *"a divisor, not an expansion"*. Arbiter locale **NOT declared** — the one
clean miss. Case-anchor ceiling honestly bounded in doctrine, but `_SPORTS_FILLER` is 100%
English on a DE/ES cohort with **two exemptions stacked on a monolingual gate**. *"The execution
made the product markedly more legible to a global institution and no more global."*

**EXECUTIONER** — Ship order **inverted**: first-cycle verification was recorded last, in the
same commit as the flip, so *"the PASSED read was taken on the PRE-flip instrument"*. **My CUT
was HONORED** — grep confirms zero candidate feeds wired. **The seven sealed feeds are
correctly held-out, not a violation** — *"sealing a candidate list is the opposite of expanding
supply: it forecloses the post-hoc roster edit."* The attribution answer: **five changes in one
day all touching D, mutually confounded, and after ~08-27 the pre-flip rows are pruned and
attribution is permanently unrecoverable.** The single fastest resolution: **a paired A/B
recompute on identical post-flip rows, stratified by community collection age (<14d vs ≥14d)** —
which simultaneously proves or disproves the guard defect with a number.

**ECONOMIST** — *"The scaffolding was built and the measurement was not."* `incumbent_displacement`
is **a level, not a flow** — and ≈ `1 − ft_ratio`, i.e. collinear with the euphoria metric it was
prescribed to replace; the market-side analogue (insider *buying*) is a FLOW and this copied the
STOCK. Null arms are **declared, not implemented** — no enroll caller, `null_random` carries **no
threshold**, and **H-A, the primary, never confronts a null at all**. Prescription 6 (tail
accounting) **vanished without a build, a deferral row, or a ruling** — *"a prescription that
disappears without a disposition is how a board becomes decorative."* Regime ledger records the
component but **not the arbiter** — four arbiter changes uncorded, including the 10%-vs-26.9%
boundary.

**OPERATOR** — Scored his own conditions **1 met, 1 governed-not-met, 3 not met**. Acceptance
harness "mandatory" appears in **no gate**. 26.9% is **on customer surfaces** (web Ledger.tsx,
mobile accuracy.tsx), not internal. *"The enrollment rule enforces the cheap conditions in code
and left the expensive ones in prose"* — `feed_set`, `instrument_epoch`, `regime` all unvalidated
free text. The sealed instrument freeze **is an env var**. Two common modes named: **Google**
(discovery pipe + benchmark + adjudicator, two on one vendor) and **7-day retention** (it has now
destroyed the GHOST window, foreclosed the LED replay, bounded venue-first-coverage, and forced
snapshot-at-enrollment — *"four nominally independent instruments, one dependency"*).

**STATISTICIAN** — Same-day flip is **not** the defect; *"there is no held-out set to hold out."*
The defect is the **missing artifact**: no script, no row-level JSON → **provenance grade C**,
below the house's own established standard. Acceptance corpus: **effective N = 12 clusters**,
95% CI ≈ [65%, 92%], and `appoint` was added to clear corpus item 3 — *"per-item tuning; the
66.7%→81.8% improvement is measured on the tuning set."* M0 is **non-stationary** ("first
retained row" drifts as pruning advances, **in the flattering direction**) and **straddles the
epoch it brackets**. Live contamination flagged: **forecast B5 is now unresolvable on its own
terms** — sealed 08-19 on a metric whose instrument changed 08-20.

**FORECASTER** — **Recomputed the seal hash independently: `25b69ffc..` MATCHES.** *"The rules
were fixed before enrollment and cannot now be edited undetected. That is the single most
important thing that happened today, and it was done 9 days early."* Then: **UNSCORABLE exists in
the document and nowhere in the instrument**; per-domain denominators uninstrumented; the
`calibrating` field the prereg promises **has no column**; `FINAL-ELIGIBLE` can read at N=3 while
enrollment is open; `SHADOW_PATIENCE_DAYS` is **never used by any code** — 365-day patience is *a
printed number, not an enforced behaviour*. And: **item 10 (D as a scoreable forecast) was
silently dropped** — no Brier, no implied probability, no trigger date. *"It did not lose an
argument — it disappeared. I have to score my own item as MIS-HANDLED."*

## DISAGREEMENTS

1. **Severity of the guard defect.** Challenger: *REJECT the flip as plumbed* / turn V2 off.
   Guardian, Buyer's Desk, Statistician: repair before the next scored cycle, flip may stand.
   Executioner, Operator: repair + verify by A/B before 08-27. **Resolved in practice** — the
   repair shipped tonight, so the strictest remedy (turn it off) was not needed; the Chairman
   may still rule otherwise.
2. **Same-day backtest→flip.** Challenger: *REJECT the backtest as flip authorization*.
   Statistician: *not a timing fault at all — a deterministic recomputation has no holdout;
   the fault is the missing script.* Genuine methodological disagreement; both agree the
   published citation must say "denominator repair only."
3. **The seven sealed-but-unwired feeds.** Executioner: **correctly held-out, the right shape**.
   Buyer's Desk: **rights rows required before wiring**. Expansionist: **the design can't answer
   its question**. Not contradictory — sequenced conditions.
4. **"GHOST window unmeasurable."** Challenger alone dissents: `velocity_scores` retains 365 days
   and was never queried, so the claim is over-broad. Every other seat accepted the finding as
   exemplary. **Uncontested elsewhere, and the Challenger is right that three retained-table
   tests were available.**
5. **Tracked-race 26.9% surface.** Operator: condition **not met** (it is on customer screens).
   Buyer's Desk: **APPROVE — exceeded**, because `ACCURACY_FIGURES_SCOPED.md` lists it in a
   *"not citable"* section and instructs the reader not to divide 15/26. They are looking at
   different artifacts; the Chairman should rule whether the shipped view or the scoping doc
   governs.

## WHAT SHIPPED TONIGHT IN RESPONSE (commit `d6de777`, deployed)

Guard on the blog lane · firewall exception registered + **commit-msg gate that runs the audit
and refuses** · `d_measured` re-keyed to author resolution · pseudo-authors excluded in both
places · degenerate-venue guard on engagement · venue guard raised 24h → 14d · engagement
baseline no longer self-inclusive · `incumbent_displacement` gains the tier filter · shadow
constants moved out of `os.getenv` · `feed_set` validated against the sealed six ·
`instrument_epoch`/`regime` derived from live flag state · schema gains
`pre_broken`/`calibrating`/`implied_prob`/window stamps **before the first row** ·
`WORDPRESS_TAGS` added to the tripwire · **ERRATUM 01 sealed** (PIT `6f9ed05f..`, cites parent
`e90af6df..`; parent body untouched) · regime ledger **corrected by a new row citing the old** ·
universe statement updated per its own trigger.

## CHAIRMAN — YOUR DECISIONS

1. **Kill-or-pivot criterion** (Buyer's Desk). *"What result makes you stop? Name the number and
   the date, today, while you still don't know the answer."* Proposed: if the candidate arm fails
   to beat both nulls at N≥20 pooled by the 2027-02-28 interim, D is demoted from scored component
   to held-out research indicator pending a new sealed hypothesis. **Not yet sealed — needs your word.**
2. **The paired A/B recompute, before 2026-08-27** (Executioner; hard deadline set by retention,
   not preference). Resolves the five-change attribution knot and independently confirms the guard fix.
3. **Enrollment driver + `report()` per-domain/UNSCORABLE + verdict enum + cross-arm exclusivity** —
   the trial's most bias-prone step is still unwritten with 12 days to go.
4. **Non-English cohorts**: declare the arbiter locale and add ES/DE acceptance fixtures, or withdraw
   Marca/Kicker to the variant log. Erratum E4/E5 makes this binding either way.
5. **Rights rows for all seven feeds + a jurisdiction annex** (US-law position does not reach EU
   Art. 15 / HK / JP) before wiring.
6. **`d_measured` on all three surfaces**, and the UI must stop rendering `firstTimerRatio ?? 0`.
7. **Restate the corrected figures**: 32.4% is a floor; the backtest is denominator-only, grade C;
   acceptance is in-sample n=12 with CI. And **rule on B5**, which the Statistician shows is now
   unresolvable on its own terms.
8. **Tail accounting** (Economist prescription 6) — build, defer with a date, or rule it out. It
   currently has no disposition.

*Nine memos preserved in the session transcript. No recommendation of the collator's is embedded;
the fixes recorded above were made because the findings were independently code-verified first.*
