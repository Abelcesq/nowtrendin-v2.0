# ERRATUM 01 to the sealed Shadow-Trial Pre-Registration
### Appended 2026-08-20 (evening UTC) · the sealed body is NEVER edited — this is a separate, separately-sealed document that cites it.
### Parent: `SHADOW_TRIAL_PREREG_2026-08-20.md` · PIT row `e90af6df..` · text `25b69ffc..` (hash re-verified by the Forecaster seat this evening: MATCHES).
### Cause: nine-seat assessment convening, 2026-08-20 evening. Six seats independently found the same defect.

---

## E1. §7's COLD-START SENTENCE WAS FALSE AT SEAL TIME. This is the erratum's reason for existing.

**What §7 says (sealed, unaltered):** *"Cold-start guard (Guardian F2, non-negotiable):
candidate-feed communities carry NO first-timer credit until their collection age ≥ 14
days (`D_COMMUNITY_MIN_AGE_DAYS`, **enforced in code under V2**)."*

**What was true when that was sealed:** the guard existed in
`gravitational_anomaly_detector.check_author_is_first_timer`, whose callers are
github / hackernews / bluesky / lemmy (and reddit, retired the same day). The blog lane —
devto, hashnode, discourse, wordpress, blogger, **medium, ghost** — uses a *different*
function, `blog_collectors._first_timer`, which had **no age term at all**. Every sealed
candidate feed (Marca, Kicker, Nikkei Asia, SCMP, STAT, Deadline, ScienceAlert) enrolls
through `NEWSLETTER_FEEDS`/`GHOST_FEEDS` → `collect_medium`/`collect_ghost` →
`_first_timer`. **The guard the prereg calls non-negotiable did not cover the lane the
trial runs on.** Had a candidate feed been wired and enrolled, its every author would have
read as a first-timer, `ft_ratio` → ~1.0, and the candidate arm would have manufactured
its own positive result — indistinguishable from the finding the trial exists to test.

**Repaired** 2026-08-20 evening, commit `d6de777`: the same 14-day rule, behind the same
`D_PLUMBING_V2` flag, now lives in `blog_collectors._first_timer`. The author row is still
recorded during the calibration window so history accrues; only *credit* is withheld.

**Status of the 09-01 start: HOLDS.** No row had been enrolled — the window had not
opened — so no trial data is affected, and the repair precedes the first enrollment. This
erratum exists because the seal's *description of the instrument* was wrong, not because
any result was.

## E2. The sealed epoch commit is superseded.

§7 pins the instrument at "engine code through commit `8716502`". The Chairman's
`D_PLUMBING_V2` flip landed in `d5b6ebf`, and this erratum's repairs land in `d6de777` —
both later, both touching the trial's lane. **Operative epoch: `d6de777` (engine release
to follow), `D_PLUMBING_V2 = ON`.** Every enrollment stamps its epoch **derived from live
flag state**, not from a caller-supplied string, so this can no longer drift silently.

## E3. Regime fact omitted from §7 — the single-vendor common mode.

Google is simultaneously a primary discovery pipe, the benchmark the product claims to
beat, and this trial's arbiter; Apify carries two of the three. **A Google- or Apify-side
change degrades the candidate arm, the control arm, and the scoreboard together, and would
present as a null result rather than an outage.** This is recorded in code but was absent
from the trial's own governing document. It is now a sealed regime fact.

## E4. Arbiter locale is undeclared — and until it is declared, the language arms are confounded.

The Trends sweep posts `searchTerms` / `timeRange` / `isPublic` — **no `geo`, no `hl`**.
A Spanish-language Marca topic and an English control topic are judged on the same
undeclared default curve, and the ambiguity heuristics are monolingual. **Binding rule:
no non-English cohort may be enrolled until the arbiter's locale is declared per
`feed_set` and recorded here.** If it is not declared before 09-01, the non-English
cohorts do not enroll and that is recorded as a coverage decision, not a result.

## E5. Acceptance-harness coverage does not extend to the non-English cohort.

`tools/extractor_acceptance.py` carries 17 hand-labeled headlines, **all English**;
`_SPORTS_FILLER` is entirely English and the club-restore rule keys on English verbs.
German capitalizes all nouns. §10 already rules that *"a null with the harness unrun is
UNINTERPRETABLE, not no-edge"* — an English-only harness on a Spanish or German feed **is
unrun**. **Binding: Marca and Kicker do not enroll until the harness carries a labeled
Spanish and German fixture block, or they are withdrawn to the variant log.**

## E6. Design limits of the sealed cohorts, recorded now rather than discovered at readout.

Each international axis is confounded with exactly one domain, and §5 forbids pooling
across domains: **language varies only inside sports; region varies only in English**
(Nikkei and SCMP publish in English — that tests market, not language); **there is no
non-English non-sports cell.** Against the sealed base rate (7 LED rows in ~2.5 months),
the language cell is more likely than not to read **UNSCORABLE**. That is an honest
outcome under §4 and it is written here in advance so it cannot later be reported as a
finding about international coverage.

## E7. Statistical-claim corrections carried by this erratum.

- The `D_PLUMBING_V2` backtest measured the **denominator repair only**. The writer repair
  is forward-only, so no stored row could exercise it; the age guard runs at collection
  time and a recomputation cannot reach it. **The backtest's reassuring direction (fewer
  nonzero topics) is the depressant half measured alone** and places no bound on the
  live post-flip effect. It must be cited as *"n=800, 72h, denominator repair only,
  provenance grade C (no script or row data retained)."*
- The acceptance figures are **in-sample**: the fix was developed against the same 12
  headlines it is scored on, and the baseline corpus was selected because the generic
  extractor failed on it. Citation form: *"87.1% / 81.8% on 12 hand-labeled headlines
  (33 entities, 12 independent clusters), in-sample, grade B; 95% CI ≈ [65%, 92%]."*
  **Never outside its own document without that qualifier.**
- **`d_measured`'s 32.4% blind fraction is an UNDERCOUNT**: it was computed from platform
  membership, not author resolution. Re-census after the fix; restate wherever quoted.

## E8. Open items this erratum does NOT close (recorded so they cannot be forgotten).

The **enrollment driver does not exist** — the four arm populations are sealed as prose,
and the selection code is the real membership criterion. Also outstanding: cross-arm
exclusivity (a topic could enroll as both `candidate` and `null_random`, biasing the very
difference the trial measures toward zero); a verdict vocabulary enum; `report()` emitting
per-domain cells and `UNSCORABLE`; `FINAL-ELIGIBLE` gated on the enrollment close;
`d_measured` surfaced on all three platforms; and a decision on whether a proper scoring
rule (implied probability + Brier) attaches to D in this trial or a successor. **The
schema fields these need were added before the first row**, so none requires a mid-window
instrument change — but the code does not exist yet, and the window opens in 12 days.

---
**PIT SEAL:** `kind='forecast'`, `item_key=PREREG-shadow-trial-2026-ERRATUM-01`,
`row_sha256 6f9ed05fb268d68efd2d3c4afb0ee4c4376e4446dc62a0e32afa9512da3eeabc`,
`text_sha256 2b34596ca0426f45fbaf8900e4aeb343be542af9e0ec3b7a84aed82a25192bf0` (body above
this block). Cites parent row `e90af6df..`. Sealed 2026-08-20, **before any enrollment**.
The parent document's body and hash are UNTOUCHED — a correction is a new sealed entry
that cites the old one, never an edit.
