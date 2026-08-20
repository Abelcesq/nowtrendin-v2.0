# BOARD COLLATION — Dark Matter (D) component: complete analysis
### Nine-seat convening, 2026-08-20 · Chairman-ordered ("complete analysis on our dark matter component + recommendations to identify items and movement BEFORE they trend")
### Evidence pack: `DARKMATTER_EVIDENCE_PACK_2026-08-20.md` · All seats independent, identical pack, no cross-visibility.
### Collation rule: memos condensed faithfully, never blended. Disagreements are signal.

---

## THE HEADLINE THE BOARD PRODUCED (convergent across independent seats)

**Five of nine seats independently concluded that D has never actually been tested — because its
input plumbing is disconnected — and one seat found the disconnection at a single line.** The
Challenger traced D's numerator end-to-end: `blog_collectors._write_topics` writes a **literal
`0` into `is_first_timer` for every topic row** from the newsletter/ghost/blogger/wordpress/
discourse/football/research collectors, and the discovery writer does the same — even though the
same collectors compute a real first-timer value and store it in `raw_signals`, which D's scorer
does not read. The only collectors writing a genuine first-timer bit into `topic_signals` (what
scoring reads) are Reddit (**403-dead since 2026-06-20**), GitHub, and HackerNews.

**Post-convening §10a verification (collator, code-confirmed): TRUE.** Scoring reads
`topic_signals` (`SELECT ts.*`, detector L4184); the blog writer inserts literal `0` at the
`is_first_timer` position (blog_collectors L617–621); the discovery writer likewise
(discovery_collectors L114–117); real ft writers exist only on the reddit/github/hn paths
(+bluesky/lemmy). **D's first-timer numerator can currently be non-zero ONLY on GitHub and
HackerNews.** The engagement-asymmetry indicator additionally requires `upvotes > 5`, which RSS
rows never carry. Both of D's indicators are structurally zero for every feed-based source.

Three further code findings entered by other seats, all **verified by the collator**:

- **Denominator dilution (Guardian F1; Economist; Forecaster).** The comment at detector
  L4404–4407 says authorless signals "are excluded from the denominator"; the code computes
  `ft_ratio = first_timers / len(signals)` over ALL signals, mainstream included. Any topic with
  news coverage has its ratio mechanically diluted toward zero — D is structurally
  anti-correlated with the breadth that wins races. *(The Statistician read the comment as the
  code and reported the exclusion works; the code says otherwise — dissent resolved by
  verification, see DISAGREEMENTS.)*
- **Cold-start first-timer fabrication (Guardian F2).** `check_author_is_first_timer` has no
  collection-age guard: every author on a newly onboarded feed reads as a "first-timer" until
  history accrues. Uncorrected, the A4 shadow trial **manufactures its own positive result** —
  candidate feeds self-certify as "early." Verified: no age term in the function.
- **sports_entity segment-initial drop (Challenger).** Filler-trim runs before the
  segment-initial check, so club-first headlines ("Arsenal agree £51m…") lose the club.
  Verified empirically: the gate-3 run extracted `['ezri konsa','aston villa']` — no `arsenal`.

---

## THE NINE MEMOS (condensed faithfully)

### 1. THE CHALLENGER — (a) REJECT as wired · (b) REJECT as stated · (c) A-W-C · (d) A-W-C
Found the ft=0 writer (above) — "the board is deliberating over a component whose input is
hardcoded to zero for nearly every source under discussion." Three-layer attack on (a): the
writer defect; denominator dilution ("expanding the D roster as currently plumbed LOWERS the
served D score — the pipe only grows the denominator"); non-stationarity (`author_history` fills
forever → built-in secular ft decline with no baseline correction). On (b): "D=0 at first
sighting" is what the writer defect + Reddit-down predicts for any non-GitHub/HN topic
regardless of reality; the mining doc's own mandated re-run was never honored; the claim is
circulating unqualified — "the A1 evidence-hygiene violation the Chairman just ruled on." On
(c): `_title_sig` is the best-evidenced item in the pack; but sports_entity shipped flag-ON
same-day with no backtest document at a corroboration-exempt tier, and has the segment-initial
recall defect. On (d): the trial cannot produce "D leads" for any RSS feed as plumbed — the
prereg must name WHICH pathway it measures (D component vs expert-pathway G) or its null is
foreordained; power unaddressed (7 LED rows in 2.5 months); arbiter+referee both weak on the
target cohort. (e): fix the plumbing before buying anything; re-run the mining; define the
denominator policy; for authorless feeds first-timer is the wrong primitive — build
first-coverage/co-occurrence indicators; per-feed liveness tripwire.

### 2. THE GUARDIAN — (a) A-W-C · (b) A-W-C · (c) APPROVE/A-W-C · (d) A-W-C (strongest item)
Entered Findings 1 (denominator) and 2 (cold-start fabrication) into the record. Architecture
principled: the router genuinely protects the early read; quorum v2.1 moat-protective; the
expert exemption is held the right way (shadow-logged, not assumed). Principle at stake in both
findings: **no fabricated data — a numerator that reads high because we just started looking,
and a denominator that reads low because we counted the authorless, are both fabricated reads
wearing a measured badge.** (b) must always distinguish "D read zero" from "D could not read"
(A3 pointed inward); a false zero on D's earliness is the World Cup 41/WATCHING applied to our
own component. Process drift flagged: **the GHOST close-out is overdue while new coverage flags
flip — "flag-gated rigor decays into flag-gated theater"; no further D-side flags until the
readout lands.** Hidden drift: D's docstring poetry ("hidden private conversations") vs what D
measures — the register-mixing A1 banned. (e): honest-absence for D (serve UNMEASURED, store
`d_measured`); fix the denominator (backtested); **put the Reddit-or-boundary decision on the
record — restore it, or write technology-only into D's exclusion boundary and stop expecting
non-tech earliness from first-timers**; write D's universe/exclusion statement (closed platforms,
authorless surfaces, uncollected communities, non-Latin scripts); D-at-enrollment stamping +
fast-lane recheck.

### 3. THE EXPANSIONIST — (a) A-W-C · (b) APPROVE claim/REJECT as verdict · (c) APPROVE · (d) A-W-C
The mechanism is locale-agnostic; **the roster is the parochialism** (every feed English; forums
one vertical). Hard-code flagged: `geo: "US"` at discovery_collectors L449 — the one rising-
discovery lane is pinned to the US as a string literal; seeds are English keywords. The
case-anchor ceiling: both entity extractors anchor on `isupper()` — **CJK/Arabic/Hebrew/Thai
have no case → structural silence; German capitalizes all nouns → over-extraction.** The unicode
fixes made Latin diacritics work; they did not make the extraction STRATEGY multilingual. The
manual-mode treadmill (hand-built extractor per domain × language) is the scaling bottleneck of
the whole D thesis — make the post-mortem's acceptance harness the factory. (d) is the most
SELLABLE artifact: a region-parameterized onboarding instrument — seed the first trial with at
least one non-English, one non-US, one non-tech cohort; pre-register WHICH geo/language each race
is judged in (the arbiter is itself locale-bound). (e): **evaluate GDELT for the COLLECTION side**
(100+ languages, pre-extracted entities, sidesteps the case ceiling) — but keep collection-GDELT
and referee-GDELT as two partitioned consumers, never let the referee corroborate its sibling
pipe; first-timer velocity (derivative, not ratio); fast-lane recheck ("latency fixes generalize
to every region automatically; roster fixes must be earned region by region").

### 4. THE BUYER'S DESK — (a) A-W-C · (b) APPROVE finding/REJECT stronger inference · (c) APPROVE · (d) A-W-C
One sentence for the partners: "measures attention building in small expert communities before
it reaches Google — and keeps a sealed scorecard which today says the 'early' component
contributed nothing to the wins. That last clause is the whole meeting." D=0 is frequently
"could not be measured" — §15a's sin applied to the flagship component. Exemption enforcement
(`MOAT_EXEMPT_STRICT`) is default-OFF: "precision-as-integrity is asserted in comments; the
enforcement is optional." Point-blank questions: *"What fraction of your Dark Matter signals
carry a resolvable author identity at all — and why is the one platform built for that signal
still returning 403 two months after you deferred the credentials?"* · *"If the shadow trial
comes back and D still doesn't lead even when properly fed — is there a pre-committed
kill-or-pivot criterion?"* · *"What alerts when an individual feed goes silent?"* Gates:
strengthens PIT + MNPI; endangers COVERAGE (a general attention dataset with one instrumented
domain is a tech-attention dataset wearing a bigger label) and **RIGHTS — five onboarding gates
for format and access, none for a written redistribution right; "it's public RSS" is not a
license schedule.** Police the pairing 10%/26.9% forever (App Annie in embryo). (e): turn Reddit
back on (cheapest lead-restoring action); honest-absence state for D; first-timer ACCELERATION;
cross-expert-community propagation (D's own quorum); fast-lane recheck; domain-balance census;
paper the rights file.

### 5. THE EXECUTIONER — (c) shipped but UNVERIFIED · ship order given
Verified both halves of sports_entity wiring genuinely present now; `from_entity_run` default-off
with nine untouched call sites; commits match claims. "The change has been 'done' twice and
verified zero times against live data" — first-cycle verification checklist written (per-arm:
sports desks produce entity topics + Football365 first rows ever; non-ASCII de-collapses; new
domains stamped calibrating; auditors don't spike; rollbacks per-arm, all clean). **Seed
dilution priced: 12 seeds at the same call count halves cadence on ai/crypto/stocks — the
fastest LED lane, where 5 near-misses lost by 1–2 days.** SHIP ORDER: (1) first-cycle
verification — gates everything; (2) **GHOST close-out THIS WEEK** (verified: no close-out doc
exists anywhere in audits/); (3) Reddit decision forced (credentials or sealed exclusion —
"an un-decided decision wearing an error log"); (4) shadow-ledger build + PIT prereg **sealed by
08-29 — no shadow-ledger infrastructure exists in the codebase; slip the start rather than seal
late**; (5) per-feed zero-row tripwire (rides A3-TRIPWIRE); (6) trial 09-01→11-30 with the
enrolled path FROZEN; (7) wiki-v3+GDELT before 11-30 or the trial has no scoreboard; (8) LED
mining re-run 09-30; (9) sealed backtest after close. CUT: any new D source expansion until
(1)+(2) are green — "supply is not D's binding constraint this week; verified measurement is."

### 6. THE ECONOMIST — (a) A-W-C (architecture approved; numerator rejected as staged AND computed) · (b) A-W-C · (c) APPROVE · (d) A-W-C
Independently found the denominator dilution and named the deeper critique: **Kindleberger
mis-staging — first-timer influx is a EUPHORIA-stage phenomenon; the crowd arrives AFTER the
displacement. The displacement-stage signal is INCUMBENTS reallocating first.** The record is
exactly what Kindleberger predicts (D≈40 pre-broken = crowd arrived; D=0 LED = no crowd yet).
Market-side D already has the correct staging (insider BUYING = incumbent accumulation); trend-D
has no analog. PRESCRIPTIONS: (1) **incumbent-displacement indicator** — established expert
authors REALLOCATING attention share to a topic they didn't previously cover (the author-history
substrate already exists); (2) fix the denominator to match its own comment; (3) restore an
author-identity firehose ("a monetary history cannot be written with the banks closed");
(4) expert-tier breadth VELOCITY (first derivative of distinct expert communities carrying a
topic — converts "we win on breadth" from lagging observation to leading instrument);
(5) engagement-per-mention divergence (price of attention outrunning quantity in a thin market,
baselined per community); (6) tail accounting — report performance on the top decile of eventual
surge size ("26.9% is uninterpretable in Extremistan without knowing whether the misses were the
whales"); (7) a standing REGIME LEDGER (append-only table of collection-regime events — Reddit
down 06-20, GHOST 07-15, fixes 08-20 — every backtest cites its window); (8) shadow trial MUST
carry naive-baseline null arms (random same-feed topics + dumb-volume rule) — "a shadow trial
without a null arm can only produce a narrative."

### 7. THE OPERATOR — (a) architecture DURABLE / signal-as-fed EXPIRED outside tech · (b) DURABLE as description, STORY as verdict · (c) DURABLE · (d) DURABLE conditional
Edge named in one sentence: author-identity-resolution on expert venues — plumbing, the right
kind of edge. **Expiry condition: author-level access closes — and this expiry has ALREADY
OCCURRED for most of the universe** (Reddit 403; X capped; RSS carries no identity). "D=0 for
LED winners is not a mystery — the instrument's power supply is unplugged outside tech."
Survival findings: the dated trial window is forced-action risk (pressure to enroll feeds before
their extractor passes gate-3 — make the acceptance test mandatory per roster INSIDE the
enrollment rule); the overdue GHOST readout ("apply more scrutiny after wins — the flag went
live after a successful verify, exactly when discipline slips"); **the hidden common factor is
GOOGLE — discovery pipe, benchmark, and validation instrument are one vendor family; one
Google-side change degrades all three "independent" functions at once. Write it down.**
(e): reconnect identity spigots (PLURAL — never one platform again); **venue-level first-timing
for authorless feeds (outlet-first-covers-entity as the first-timer event at venue granularity —
"the only path to a non-tech D that does not depend on a platform vendor's mercy")**;
breadth-priority + fast-lane recheck; keep 26.9% internal (TCI: trust damage lands after the
fix works). "D did not fail its thesis — it was never plugged in outside technology."

### 8. THE STATISTICIAN — (a) OVERFIT-RISK (substrate) · (b) UNSUPPORTED as behavioral claim · (c) SOUND/one lapse · (d) SOUND with 5 conditions
"D is presently a tech-blog first-timer index wearing a general name." The load-bearing fact:
`_first_timer()` is called only from the blog-lane collectors; no news/discovery/RSS path
resolves authors. On (b): the claim is UNSUPPORTED as stated — N=7/15/43 medians without
dispersion; the sample CANNOT contain the refuting cohort (ledger enrolls floor-crossers only,
so topics where D fired early but never crossed are invisible); within tracked races D=0 for
winners AND near-misses = zero discriminating power either way; "a grade-B directional read is
circulating at grade-C confidence." Test that settles it: recode D to null where first-sighting
had zero author-identity signals and report how many rows retain a measured D at all. Gate
lapse: sports_entity shipped flag-on same-day with known defects and no backtest doc — §16
gate-5 at partial strength on the exemption-bearing tier. (d) conditions: per-domain minimum N
sealed (never pool domains); freeze the instrument at 09-01; pre-register that referee silence
on shadow wins is absence-not-weakness; every threshold with its denominator; read the GHOST
close-out BEFORE designing the shadow roster. Seal an M0 snapshot pre-09-01 (the endpoint
exists, L8280). Thorp note: World Cup detection shows plateau-and-jump attractors (24–25 / 95–96)
— rank resolution inside cohorts is thinner than the 0–100 scale advertises (→ A3-CEILING
fixture). *(Note: this seat read the denominator comment as implemented; collator verification
sides with the four seats who read the code — see DISAGREEMENTS.)*

### 9. THE FORECASTER — (a) UNSCORABLE historically · (b) MIS-SCORED as phrased · (c) WELL-SCORED + one obligation · (d) WELL-SCORED design, 4 defects + 1 overdue
"D's forecast has never been well-posed because its input was structurally unmeasured": the
legacy scorer computed first_timer_ratio over REDDIT SIGNALS ONLY with Reddit down (numerator
identically zero fleet-wide for two months; the surviving terms — asymmetry, vocabulary
convergence — fire on repetition, i.e., AFTER volume: late-confirmation BY CONSTRUCTION). The
honest sealed statement: **"D as instrumented never measured early; whether the hypothesis leads
is UNTESTED" — and the two statements dictate different remedies** (replace the hypothesis vs
repair the instrument; A4 assumes the second while the doctrine sentence asserts the first).
Trial defects: **(1) CENSORING MISMATCH — the largest: a 09-01→11-30 calendar on 365-day races
means most shadow races are unresolved at readout; enrollment closes 11-30, races run to
resolution, the 11-30 readout is INTERIM with the censoring rate printed beside every rate — "I
defend the patience window against its most subtle attacker: a trial calendar that quietly
re-imposes a 90-day window because 90 days demos better."** (2) No control arm named — enroll
the existing roster's first-crossings under identical rules and score the DIFFERENCE.
(3) Denominator with every threshold + "UNSCORABLE if fewer than N races" as a written verdict
option. (4) Blind referee — pre-register that shadow wins are Trends-adjudicated only, or ship
the second arm first. The overdue GHOST close-out "IS an unresolved instance drifting toward
pending-win status — a position held because it was never scored"; freeze its evaluation window
at the originally advertised end (~07-29). (e): **make D a scoreable forecast** (sealed event
definition: "breakout within K days of first D-trigger" + implied probability → Brier/
calibration over ALL sealed triggers); primary metric = lead-time distribution shift vs
concurrent control; restore an author-identity source; fix the denominator; per-feed tripwire;
standing re-mining obligation; shadow rows never appear anywhere until resolved.

---

## DISAGREEMENTS (explicit; signal, not noise)

1. **Denominator exclusion — FACTUAL, RESOLVED BY VERIFICATION.** Statistician: the code
   "does exclude author-less signals from the ft denominator (L4406–4407)." Guardian, Economist,
   Forecaster, Challenger: it does not — the comment claims exclusion, the code divides by
   `len(signals)`. **Collator §10a verification: the four seats are right; the exclusion exists
   only in the comment.** The Statistician's conclusions are otherwise unaffected (their verdict
   rested on substrate narrowness, which stands).
2. **How damning is "late-confirmation"?** Challenger REJECTS the sentence outright; Guardian/
   Economist/Statistician/Forecaster accept it only re-scoped ("as instrumented / untested");
   Expansionist/Buyer/Operator accept it as description while rejecting it as thesis verdict. No
   seat defends the unqualified sentence. **Unanimity in direction, disagreement in severity.**
3. **What to do first.** Executioner: verify the 08-20 deploy + close GHOST before anything;
   CUT new sources. Buyer/Operator/Economist/Forecaster: the Reddit/identity-substrate decision
   is the cheapest lever. Expansionist: internationalize the trial cohort now. These are
   compatible but compete for the same 12 days before 09-01.
4. **Seed dilution.** Only the Executioner priced the cadence halving on the incumbent fast
   lanes from the 6→12 seed expansion; no other seat raised it. Uncontested but single-sourced.
5. **sports_entity ship discipline.** Statistician and Challenger call the same-day flag-flip a
   §16 gate-5 lapse (no backtest doc, known defects at ship); Executioner treats it as shipped-
   but-unverified with a checklist; Guardian conditions future flips rather than faulting this
   one. *(Collator note, factual: the flip was Chairman-ordered "proceed with coverage
   expansion"; the seats' point about the missing acceptance/backtest document stands
   regardless of authority.)*

## CONVERGENCES (independent seats, no cross-visibility)

- **The plumbing, not the thesis** (5 seats independently: Challenger's writer trace, Guardian's
  two findings, Economist's dilution + staging, Operator's "unplugged," Forecaster's
  Reddit-only legacy numerator). D has not failed; it has not been tested.
- **The doctrine sentence must be re-scoped** (all 9, varying severity).
- **Reddit / author-identity substrate is a founder decision that must be forced** (7 seats).
- **The GHOST close-out lands before the shadow trial opens** (6 seats; Executioner verified no
  close-out document exists).
- **Per-feed zero-row tripwire** (6 seats — The Batch/Football365 class must become impossible).
- **Shadow-trial prereg needs: named pathway, control/null arms, per-domain minimum N with
  denominators, instrument freeze, censoring-honest readout, referee-blindness statement,
  cold-start guard** (assembled across Challenger, Guardian, Economist, Statistician,
  Forecaster, Operator — remarkably complementary, near-zero overlap).
- **New leading-indicator designs for authorless feeds** converge on the same family: venue-level
  first-coverage (Operator), first-coverage semantics (Statistician), incumbent displacement
  (Economist), cross-expert-community propagation/velocity (Buyer, Economist, Expansionist).

## VERDICT TABLE

| Item | Challenger | Guardian | Expansionist | Buyer | Executioner | Economist | Operator | Statistician | Forecaster |
|---|---|---|---|---|---|---|---|---|---|
| (a) D mechanism as wired | REJECT | A-W-C | A-W-C | A-W-C | (starved) | A-W-C | DURABLE arch / EXPIRED feed | OVERFIT-RISK | UNSCORABLE |
| (b) "Late-confirmation" claim | REJECT as stated | A-W-C | APPROVE/REJECT-as-verdict | APPROVE/REJECT-inference | re-test scheduled | A-W-C | DURABLE/STORY | UNSUPPORTED | MIS-SCORED |
| (c) 2026-08-20 fixes | A-W-C | APPROVE + A-W-C | APPROVE | APPROVE | SHIP (verify!) | APPROVE | DURABLE | SOUND + 1 lapse | WELL-SCORED |
| (d) A4 shadow trial | A-W-C | A-W-C | A-W-C | A-W-C | SHIP w/ order | A-W-C | DURABLE cond. | SOUND + 5 cond. | WELL-SCORED + 4 defects |

## POST-CONVENING VERIFICATION ANNEX (collator, §10a — facts, not opinion)

| Claim | Verdict | Evidence |
|---|---|---|
| ft=0 writer (blog + discovery topic rows) | **CONFIRMED** | `_write_topics` inserts literal `0`; discovery writer likewise; scoring reads `topic_signals`; real ft only on reddit/github/hn(/bluesky/lemmy) paths |
| Denominator dilution (comment ≠ code) | **CONFIRMED** | L4404–07 comment promises exclusion; L4410–11 divides by `len(signals)` |
| Cold-start first-timer (no age guard) | **CONFIRMED** | `check_author_is_first_timer`: post_count lookup + insert only; no community-age term |
| sports_entity segment-initial club drop | **CONFIRMED** | Live gate-3 output: "Arsenal agree £51m…" → no `arsenal` extracted |

## DECISION ITEMS

**Chairman — your decision per item.** The board offers these as distinct rulings; none is
bundled with another.

1. **The plumbing repair set** (score-affecting → flag-gated + held-out backtest before any
   flip): pass real `is_first_timer` through the blog/discovery topic writers; fix the ft
   denominator to its documented intent (author-capable signals only); add the community-age
   guard to first-timer status. All three verified defects.
2. **The Reddit ruling** (founder decision, 7 seats): restore credentials, or formally retire
   Reddit and write technology-only into D's stated exclusion boundary. Either is honest; the
   silent 403-every-cycle state is neither.
   > **RULED — Chairman, 2026-08-20, same day:** "please disable reddit. we will not obtain the
   > API key needed. This should have been disabled already." EXECUTED: the stale credentials
   > (which had defeated the collector's own disabled-guard and produced the two months of 403s)
   > unset at engine v365; collector docstring updated to FORMALLY RETIRED; reactivation = new
   > founder decision + §16 re-onboarding. Consequence recorded: D's author-bearing universe is
   > now GitHub/HackerNews(/bluesky/lemmy) by construction — the exclusion-boundary statement
   > (item 11) and the shadow-trial prereg must both carry this regime fact, and the
   > authorless-feed indicator designs (item 9) rise in priority accordingly.
3. **The doctrine correction** (wording, zero code): re-scope "D is late-confirmation" to "D as
   instrumented never measured early; the hypothesis is untested" everywhere it appears.
4. **GHOST close-out** before 09-01, evaluation window frozen at ~07-29; no further D-side
   coverage flags until it lands (Guardian's condition).
5. **Shadow-trial pre-registration contents** (seal by 08-29 or slip the start): named pathway
   under test; control arm (existing roster, identical rules) + null arms (random same-feed +
   dumb-volume); per-domain minimum N with denominators; UNSCORABLE as a written verdict;
   instrument freeze for the window; interim-vs-final readout with censoring rates (365-day
   races); referee-blindness statement (or wiki-v3+GDELT first); cold-start guard; Reddit regime
   recorded; epoch marker v364.
6. **Per-feed zero-row tripwire** (rides the A3-TRIPWIRE monitoring slot).
7. **sports_entity completion**: fix the segment-initial drop; run the acceptance harness
   per-desk with club/player recall; write the backtest/acceptance document the seats found
   missing; make the harness a standing §16 gate-3 fixture.
8. **D honest absence**: serve/store `d_measured: false` (UNMEASURED, not 0) when no
   author-bearing signals exist — the A3 invariant pointed inward. Display/measurement-side.
9. **New leading-indicator builds** (each §16-gated, held-out, backtest-before-ship, candidates
   for the shadow trial): venue-level first-coverage events; incumbent-displacement
   (expert-author reallocation); expert-breadth velocity; engagement-per-mention divergence;
   first-timer acceleration.
10. **D as a scoreable forecast** (Forecaster): sealed event definition + implied probability →
    Brier/calibration over all sealed triggers; primary metric = lead-time distribution shift.
11. **Supporting registers**: regime ledger (append-only collection-regime events); rights file
    (per-source use/redistribution terms); D universe/exclusion statement; LED-mining re-run
    dated 2026-09-30 + at trial close; M0 snapshot sealed pre-09-01; `geo:"US"`
    parameterization + non-Latin extraction strategy noted as the internationalization ceiling.

*Collation prepared read-only from nine independent memos; full memos preserved in the session
transcript. No recommendation of the collator's is embedded; the verification annex states
code facts only.*
