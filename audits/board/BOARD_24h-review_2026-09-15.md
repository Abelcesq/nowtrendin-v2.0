# BOARD COLLATION — 24-hour review + the two data questions (round 4 of session)

**2026-09-15 · Nine seats, isolated, identical pack (`EVIDENCE_PACK_24h_2026-09-15.md`).
Items: R1–R6 (the 24h updates) · Q1 (Positioning-vs-Price data path) · Q2 (Tier data path).
This is a COLLATION, not a blend. Chairman decides per item at the end.**

Independent verification note: five seats re-verified primary artifacts themselves rather than
trusting the pack — Challenger and Guardian re-hashed the sealed prereg (matches PARAM_VERSION);
Executioner and Statistician re-ran `test_divergence.py` (18/18) in-session; Forecaster verified
in git that the seal commit (17:22:39 UTC) strictly precedes the first analysis code (17:35:47);
Challenger/Guardian/Economist/Executioner/Statistician/Forecaster each independently confirmed the
R6 "money absent" strings are engine-served at `crypto_money_gradient.py:233-234,319`.

---

## VERDICT TABLE

| Item | Challenger | Guardian | Expansionist | Buyer's Desk | Executioner | Economist | Operator | Statistician | Forecaster |
|---|---|---|---|---|---|---|---|---|---|
| R1 divergence tool | APPROVE-W-C | APPROVE | APPROVE | APPROVE-W-C | SHIP | APPROVE | DURABLE | SOUND | WELL-SCORED |
| R2 test program | APPROVE-W-C | APPROVE-W-C | APPROVE | APPROVE | SHIP (open obligations) | APPROVE-W-C | DURABLE | SOUND (2 defects) | WELL-SCORED |
| R3 merge+verify+stage-2 | APPROVE | APPROVE | APPROVE | APPROVE | SHIP | APPROVE | DURABLE | SOUND (B/C prov.) | WELL-SCORED |
| R4 all-pages audit+fixes | APPROVE-W-C | APPROVE | APPROVE-W-C | APPROVE-W-C | SHIP (1 hazard) | APPROVE | DURABLE | SOUND (1 defect) | WELL-SCORED |
| R5 CoinAPI rights | APPROVE-W-C | APPROVE-W-C | APPROVE | APPROVE | SHIP (letter is the item) | APPROVE | DURABLE | SOUND (grade C legal) | WELL-SCORED |
| R6 residuals | APPROVE-W-C | APPROVE-W-C | APPROVE-W-C | APPROVE-W-C | R6a SHIP-LATER / R6b SHIP-cond. | APPROVE-W-C | DECAYING (as a class) | SOUND (2 conds) | UNSCORABLE-as-intended |
| Q2 option (c) M-only tier | REJECT | REJECT | REJECT | REJECT | CUT | REJECT | REJECT (badge) | REJECT | REJECT |
| Q2 option (d) status quo | APPROVE interim | APPROVE default | APPROVE interim | APPROVE now | SHIP (keep) | APPROVE interim | correct posture | only SOUND option today | acceptable, hold |

**No REJECT was cast on any of R1–R6. Option (c) drew nine rejections — the only unanimous
negative of the round. Every seat endorsed (a) as the eventual Tier path, all with conditions.**

---

## MEMOS (faithful, condensed — full texts in the session transcript)

### 1 · CHALLENGER
R1 A-W-C — two silent semantics gaps that will mint a wrong-but-"measured" D the first
irregular day: **(i) unbounded fit staleness** (α̂/β̂ never expire; a failed refit silently
reuses coefficients weeks old while stamping `measured:true`); **(ii) observation-index
windows drift off the calendar** (Δln over 7 *observations*, not 7 days; the first gap turns
the sealed statistic into a different one, undisclosed). Both are hardening outside the sealed
sections; both MUST land before graduation, with fixtures. R2 A-W-C — **pseudo-replication**:
"n=432" is really n_eff≈36 day-clusters; never cite pooled n; the **K14 unit guard has never
run against the 36 accrued days** (prod columns exist only since f60fad8) → one-time
retroactive unit-sanity backscan required before those rows seed any baseline. R4 A-W-C —
fabricated tiers/zeros were SERVED for some window: produce a dated **incident note** (intro
commit → fix commit per class) and sweep external artifacts/screenshots captured inside the
windows; record when the History disclaimer diverged. R5 A-W-C — "CLEARED" is an in-house
legal reading (say so in the row); counsel's scope must include the *internal-use* posture
too (the pass-through says "any use"). R6 — never rename the `gap_state` enum (payload
contract); fix via display strings/copy map; one-time audit of other "LIVE" claims in
CLAUDE.md. **Q1 trap the pack missed:** FMP would build D's price leg AND resolve outcomes —
a shared vendor error correlates predictor with outcome and manufactures skill the seal
cannot detect → the §16 note must pick a distinct resolution source or explicitly rule the
shared-vendor risk with an independent cross-check referee. Dates: displayable D ~2027-02 if
pre-seal context survives the backscan, else ~2027-03-19; published rate 2028 at the earliest.

### 2 · FIRST-PRINCIPLES GUARDIAN
R1 APPROVE — most principle-faithful build reviewed; exclusion boundary written into the seal
(BTC/ETH only, funding disqualified); shadow flags must never be quoted anywhere served. R2
A-W-C — the missingness audit was **not testable, not passed** (banned phrasing: "passed");
timing PARTIAL is a proxy, never satisfies K12; the 3-offset gate is currently *unstartable*,
which is worse than unpassed. R4 APPROVE — strongest item: fabrication-by-default excised at
both platforms; hidden-drift check negative (fixes are display-only; semantics untouched);
annotate—never rewrite—the stale line in the dated test report. R5 A-W-C — letter must be
**widened before sending** (residual + tier chip; one round-trip); a drafted letter is a step
described, not taken; counsel reads reply + pass-through together. R6 A-W-C — engine string
pass under the round-4 **atomic field-and-prose rule**: string + every interpreting sentence
in one coordinated change, `gap_state` values stable, chosen to be non-contradictory beside
BOTH old and new client prose during the Expo lag. Q1 — FMP price leg: storage independence
is textual, **same-vendor common-mode risk remains** — disclose in the onboarding note and
cross-check with the CoinGecko referee; pre-seal rows usable as warm-up *context* if the
graduation note discloses it. Q2 — (a) with rights-consistency (no de-minimis exception to
"silence is not a grant"); (b): REJECT resurrecting the shelved-as-noise Coinbase leg to
clear a floor — a noise vote corroborates nothing; (c) REJECT — `confidence_level` already
exists, show it under its own name if wanted; tail coins' absence is likely **permanent** and
the display should eventually say so. Universe question: single-venue positioning is the
structural blind spot; state it on the surface at graduation.

### 3 · EXPANSIONIST
R1 APPROVE — the most exportable asset: locale-free statistic, §7 proves per-market
instantiation; codify "new asset class = new instantiation + own seal + own rights row" as
the expansion template; single-venue = single-jurisdiction (multi-venue OI before global
marketing). R2 APPROVE — evidence and deploys off the laptop is the point; US-parochial
context legs (CFTC/FINRA) must not calcify into "positioning ground truth"; CG pacing dies at
100 coins. R3 APPROVE — make the plan-flip a monitored invariant (scheduled EXPLAIN alarm).
R4 A-W-C — the audit style is artisanal; absence-state vocabulary needs ONE shared rendering
contract (component/token/string-table) enforced by frontend-consistency, or the classes
reopen per page. R5 APPROVE — rights row in exhibit form is sellable; **add a jurisdiction
column to the register now at 12 rows, not at 50**; put a date on the letter. R6 A-W-C —
**codes-not-copy**: engine serves semantic state codes, surfaces own rendering (the only path
to localization); Expo publish → EAS/CI. Q1 — ask CoinAPI for the grant jurisdiction-scoped
or worldwide in one letter; 60-day stall → budget a vendor whose standard terms include
derived display. Q2 — (a) ≫ (d); (c) REJECT; CoinMetrics free tier is a rights dead end —
buy commercial or drop. Tier date ~year-end 2026 stated with its assumptions.

### 4 · OUTSIDER / BUYER'S DESK
One-sentence product: "measures attention and leveraged positioning building BEFORE Google
and price confirm it, keeps a tamper-evident scorecard including the misses, and sells the
measurements plus the paper trail to funds too small to build a data desk." Numbers don't
smell managed — *nobody fakes a report that says we have nothing yet* — but: the 26.9%
tracked-race figure **never appears externally without the 10% blended in the same sentence**,
and pooled ρ/n figures are instrument checks, never statistical evidence. R1 A-W-C — anchor
the seal EXTERNALLY (signed tag to a third party / OpenTimestamps / email to counsel): "could
you prove the prereg predates the code by anything other than your own commit timestamps?"
R4 A-W-C — the CLAUDE.md false-live record is **the App Annie failure mode in embryo**; put
doc-vs-code reconciliation on a cadence. R5 APPROVE — riders: the letter has value only sent
(dated deadline); the register's LARGEST hole is untouched — **OPEN item 3, the direct-RSS
class** (get the counsel memo or reclassify the load-bearing feeds). R6 A-W-C — forbidden-words
check must run at the **served-payload layer**, not only client bundles. Q1/Q2 — as pack,
correctly ordered; tier realistically **Q1 2027**; the NOT MEASURED column "is the demo."
Diligence list beyond R1–R6, in order: **(0) the open PII decision** (purge-or-accept + fork +
Drive copy — no institutional buyer signs while open), (1) direct-RSS rights memo, (2) finish
the laptop-SPOF list, (3) external seal anchoring, (4) record-drift reconciliation cadence.

### 5 · EXECUTIONER
Re-verified in-tree (tests 18/18, gates, register row, uncommitted R6a diff — since committed
as d5323f9). R1 SHIP (ratify) — verify the seal-binding test runs in **CI on every push**, red-team
it once. R2 SHIP as a program with owners+dates: 3-offset collector is the longest-lead unstarted
item (assign NOW; pass earliest ~mid-Oct if shipped this week); instrument-audit re-run over
stamped rows ~2026-10-14; put the research re-run on a monthly Routine. R3 SHIP — put
`ops-platform-verify` on a weekly schedule. R4 SHIP — **hazard: production mobile still serves
the audited defects until the founder's next Expo publish**; make the publish a dated founder
action carrying R4+R6a together, with a 3-point on-device spot-check. R5 SHIP — the LETTER is
the item: send this week, 14-day follow-up Routine, file any answer (refusals included) as a
snapshot. R6b SHIP narrowly: strings only; `gap_state` enum untouched; **check whether
interpretation text persists in stored payloads** (deploy alone may not flip old rows — the
deploy-version-window lesson); verify after re-warm via the runner. Ship order: R6a → R6b →
3-offset collector → founder batch (letter+counsel+Expo publish) → Routines → price-leg §16
note. Q1 — the §16 price note must decide ONE question explicitly: does vendor backfill satisfy
"stored by us," or does the clock start at our first self-stored row? Q2 — (a) SHIP-LATER
(backtest window Oct–Nov; rights govern the flip, not the build); **(b)-Coinbase CUT**;
(c) CUT; (d) keep. Tier earliest ~**Nov 2026** (later clock of backtest/rights governs).

### 6 · ECONOMIST
R1 APPROVE (declared interest: authored §2 — weight accordingly; the seal-binding test is the
independent evidence). R2 A-W-C — the missingness pass is **vacuous**; define the stress
condition now (a top-decile |ret| day in-window) before "passed" may ever be written; 3-offset
build is the only unstarted clock. R3/R4 APPROVE (R4: fixes at the data layer = right
altitude; the premise correction is silent evidence caught in our own records). R5 APPROVE —
widen the letter to composite indicators before sending. R6 A-W-C — display-string-only by
demonstrated diff scope; atomic field-and-prose; closure evidence for the mobile panel is a
git ref + a device render, never a doc line. Q2 — (b) REJECT as strategy (floor-gaming;
Malkiel's null wearing a vote); (c) REJECT; (a) with the widened letter + backtest; earliest
honest tier statement: "**2–6 weeks contingent on CoinAPI's answer; if silence, ABSENT
stands**" — no firmer date may be promised. PRESCRIPTIONS: (1) continuity tripwire on every
accruing series (a gap resets the 186-day clock — extend collector_health to the divergence
collectors); (2) pre-register a tail-capture metric beside Brier (of the k largest drawdowns/
breakouts, how many were flagged in advance) as a sealed addendum; (3) log the dark
denominator (count un-computable coin-days so no hit rate is ever "days we could measure");
(4) codify "≥2 floor = ≥2 *validated* votes" (a source votes only after beating Null A
held-out); (5) per-leg instrument error budget + second venue on the §16 roadmap; (6) turn
the fabricated-default class into a CI lint (`?? '<LITERAL>'` on display-state fields);
(7) schedule `ops-fetch-legal` monthly + alarm on ToS diff; (8) held-out Kindleberger stage
annotation linking attention surges to positioning residuals — measure the thesis, never
assert it.

### 7 · OPERATOR
EDGES: E1 the seal-and-register discipline (compounds under scrutiny; near-miss precedent:
the never-scheduled PIT verifier — add a weekly CI job re-verifying prereg hash == deployed
slug's PARAM_VERSION); E2 the rights register as procurement plumbing; E3 the honest-absence
surface itself; E4 the CFTC COT leg (rights-cleanest series in the program, free); E5 the
divergence signal is **NOT yet an edge** — zero measured values; a story with excellent
hygiene, price it at zero until 30 flags resolve. SURVIVAL: S1 the empty flagship column IS
the forcing function (demo-shaped pressure toward option-c; prereg §6 is the pre-committed
rule — refuse to weaken it); **S2 hidden common factor #1: one venue** — funding, OI, the
tier fix, and the rights posture all resolve to Binance-via-CoinAPI (one dependency wearing
four names) → no crypto positioning display graduates without a second, RIGHTS-independent
leg for BTC/ETH at minimum; S3 hidden common factor #2: the founder's queue (letter, Expo,
secrets, Drive copy) — date every founder-only item, convert what's convertible to CI this
quarter; S4 the record fabricated shipped-state twice in one pack — "LIVE" claims cite a
commit hash, weekly grep; S5 vocabulary lives in two layers and the gate watched the wrong
one — run forbidden-words against served payloads; S6 the trivially-passing audit — record
missingness PARTIAL until it has seen a failure it detected. Verdicts: R1–R5 DURABLE, R6
DECAYING as a class (count open residuals at next board: falling = holds). **Q1 panic
clause (pre-commit now, while calm): if CoinAPI refuses or stalls past 60 days, the column's
first inhabitant becomes a CFTC-COT-based residual for BTC/ETH (public, rights-clean, weekly,
honestly labeled the coarser instrument) and the CoinAPI leg stays internal.** Q2 — (a) with
rights-first + per-coin source provenance printed on the tier (the marginal coins' "two
sources" are one-venue-underneath); tier earliest ~**Nov–Dec 2026**; minute the sentence
"there is no rights-clean shortcut to a positioning tier."

### 8 · STATISTICIAN
R1 SOUND — best statistical machinery shipped; production-probe claims are provenance C from
this chair; grade A requires publishing sealed input hashes. R2 SOUND with two number-hygiene
defects: **effective-N overstatement** (n=432 → n_eff≈36; the timing CI includes zero AND
values that matter — "underpowered," never "pass") and the vacuous missingness pass
(pre-register a minimum exposure, e.g. ≥180 coin-days of missingness opportunity, before
"passed" may be cited). **New finding from the committed CSV: intra-day capture spread up to
~17 hours (ADA)** — the "daily" series is irregularly sampled; a 7-day window spans 6.3–7.7
effective days; argues for pinning a fixed UTC capture slot inside the 3-offset change.
R3 SOUND — re-verify the query plan persists across a dyno restart (verified-state ≠
steady-state). R4 SOUND, one method defect: **unit of audit ≠ unit of exposure** — the
forbidden-words pass grepped client bundles while the pixels came from engine strings; add a
served-string check to the integrity gate; watch the Inflow/Outflow chips one column from
"Positioning vs Price" once D renders. R5 SOUND — in-house legal reading = grade C: fine for
a BLOCKING determination, insufficient for any future GRANT; buyer documents say display
rights "not held," never "pending." **Q2 — sharpest dissent on (a): there is currently
nothing to backtest against** — ~36 days, all seen by the people who would design the wiring
(K16 taint applies to the composite too); a backtest on that window is in-sample by
construction. Defensible path: **pre-register the composite-inclusion protocol NOW** (wiring
rule, weights, validation criterion vs the held-out crypto ledger — sealed BEFORE any
candidate is computed), validate on ≥90 POST-seal obs → earliest validation read
**2026-12-14**, shipped tier realistically **Q1 2027**. Never design the wiring on the
window used to validate it. Closing: this round again proved defects are found by
experiment and committed raw artifacts (the CSV yielded the 17-hour finding) — keep
committing the raw numbers; the audit surface is the product.

### 9 · FORECASTER
R1 WELL-SCORED — the first artifact satisfying the full Tetlock standard, seal verified real
in git (17:22:39 vs 17:35:47); resolution criteria sealed before any flag exists; unresolved
RESOLVES NO; Brier/Murphy over all flags; N in episodes. Notes: θ=+1.5 is by construction —
never describe as evidence-derived (the §15a Q=5 rule); the hypothesis is one-sided — any
negative-tail claim is a NEW seal, not a free extension. R2 WELL-SCORED — the None-filled
preview is the system refusing to fabricate; a test that cannot yet fail is not evidence.
R4 WELL-SCORED — fabricated defaults were "fabricated resolutions of absent data," the seat's
own error class at the display layer; premise correction kept the error visible (correct
Brier hygiene). R5 — "silence is not a grant" IS "unresolved is never a pending win" applied
to rights; the DRAFT letter is not progress and must never be counted. R6 UNSCORABLE-as-
intended; string pass: strings only + the replacement text must still say **absent, not
zero**. Q1 — **seal the price-source choice BEFORE D values exist** (choosing after readings
are visible makes source selection a fitted parameter); the 186-day accrual is the negative
carry, the held-out structure is what makes being early survivable — defend both against
every demo. Q2 — **seal the tier-backtest acceptance criteria BEFORE running it** (the
accrued history has been seen; the pass bar is the only thing left sealable); whether a
coarse 5-level chip is "non-reverse-engineerable enough" is **counsel's** determination, not
engineering's; (c) REJECT — an M-only read may exist only as a visibly different object under
its own name, never in the Tier column.

---

## DISAGREEMENTS (signal, not noise)

1. **Earliest honest Tier date (Q2-a).** Economist: "2–6 weeks contingent on CoinAPI's
   answer." Executioner/Operator: ~Nov–Dec 2026 (backtest on 60–90 days of accrual + rights).
   Challenger: ~Jan 2027. **Statistician (strictest): the accrued window is K16-tainted for
   composite design — seal the inclusion protocol first, validate on ≥90 POST-seal obs →
   Q1 2027**, Forecaster aligned (seal the acceptance bar before computing candidates). The
   spread is not about optimism; it is a genuine methodological question the Chairman must
   rule: **may the pre-flip accrued window inform the composite backtest, or only post-seal
   data after a sealed acceptance bar?**
2. **Pre-seal rows as D-display warm-up context (Q1).** Guardian: usable with disclosure.
   Challenger: only after a retroactive unit-sanity backscan — otherwise the date slides to
   ~2027-03-19. Statistician: K16-strict posture. Needs a ruling.
3. **FMP as the sealed price leg.** Executioner/Economist/Expansionist: acceptable with the
   §16 note. Challenger (strongest form): FMP also RESOLVES outcomes — shared-vendor error
   correlates predictor with outcome; require a distinct resolution source or an explicit
   board ruling with an independent cross-check referee. Guardian: same-vendor common-mode
   must be disclosed + CoinGecko cross-check. Forecaster: whatever is chosen, seal the choice
   before any D exists.
4. **A separately-labeled M-only chip (the honest variant of rejected option c).**
   Buyer's Desk/Guardian/Forecaster: permissible as a visibly different, own-name object.
   Executioner: CUT — not worth the surface when (a) lands within months. Operator: defer —
   shipping it removes the pressure that gets the rights letter sent. Statistician: default
   don't (two-taxonomy confusion). Chairman's call.
5. **R4 exposure accounting.** Only the Challenger demands a dated incident note for the
   period fabricated tiers/zeros were actually served + a sweep of external artifacts; other
   seats treat the fixes as closure. Cheap to do; the Chairman should rule whether it is owed.

## CONVERGENCES (9/9 or near)

- **Send ONE widened CoinAPI letter this week** (derived residual + tier/composite chips +
  jurisdiction scope), founder-only action; counsel engaged on the Binance pass-through IN
  PARALLEL (and, per Challenger/Statistician, countersigning the internal-use reading).
- **Build the K12 3-offset collector NOW** — the only gate that is both unbuilt and
  time-accruing; include a pinned UTC capture slot (Statistician's 17-hour jitter finding).
- **Option (c) M-only tier in the Tier column: rejected 9/9.**
- **Option (d) honest ABSENT: unanimously the correct interim** — several seats call the NOT
  MEASURED column a diligence asset, not a cost.
- **Q1 dates are fixed by the seals, not negotiable:** displayable D ~Feb 2027 (conditional),
  internal correlation ≥2026-12-14, published rate only at 30 resolved flags (years; the
  8–15-year horizon is the honest public posture).
- **Never-do (common core):** no enrolling of historical/pre-seal data; no window/θ retuning
  under this param_version; no display on internal-use clearance or on silence; no default/
  fallback tier values ever again; no env-flag flip of a score-affecting composite; no
  quoting preview/harness D values anywhere served.

---

## DECISION TABLE — Chairman, your decision per item

| # | Decision needed | Board's input (not a recommendation) |
|---|---|---|
| D1 | Ratify R1–R5 verdicts | No REJECT cast; conditions listed per memo |
| D2 | R1 pre-graduation hardening: fit-staleness bound + calendar-gap guard + fixtures | Challenger conditions; no seat objected |
| D3 | Order the K12 3-offset collector built this week (incl. pinned UTC capture slot) | 9/9 convergence; the only unstarted clock |
| D4 | Founder sends the WIDENED CoinAPI letter + engages counsel (pass-through + countersign); optionally adopt the Operator's 60-day panic clause (CFTC fallback pre-commitment) | 9/9 on the letter; panic clause is Operator's proposal |
| D5 | §16 six-gate onboarding of the sealed price leg — and rule the FMP independence question (distinct resolution source vs disclosed shared-vendor + cross-check referee) + the backfill-vs-self-stored clock question | Disagreement 3; Executioner's one-question framing |
| D6 | Engine display-string pass: strings-only diff, `gap_state` enum untouched, atomic field-and-prose, "absent not zero" preserved, forbidden-words check added at the SERVED layer | All seats approve with these conditions |
| D7 | Doc-integrity rule: every "LIVE/shipped" claim in CLAUDE.md cites a commit hash; periodic doc-vs-code grep | Operator/Buyer's Desk/Statistician/Guardian/Forecaster |
| D8 | Tier path ruling: adopt (a) — and RULE the backtest-window question (pre-flip accrual usable vs sealed-acceptance-bar + post-seal-only validation); (d) stands interim; rule on the separately-labeled M-only chip variant | Disagreements 1 + 4 |
| D9 | Challenger's R4 exposure accounting: dated incident note for the served-fabrication windows + external-artifact sweep + disclaimer-divergence date | Disagreement 5 |
| D10 | Retroactive unit-sanity backscan of pre-f60fad8 `coinapi_derivs` rows; rule whether pre-seal rows may serve as D-display warm-up context | Disagreement 2 |
| D11 | Ops adoptions (cheap, several seats each): weekly platform-verify schedule · monthly research-runner Routine · weekly deployed-slug seal re-verify · EXPLAIN plan monitor · monthly ToS-snapshot diff alarm · register jurisdiction column · continuity tripwire on accruing collectors · fabricated-default CI lint · Expo→EAS/CI publish · dated deadlines on all founder-only items | Executioner/Operator/Economist/Expansionist/Statistician lists |
| D12 | Buyer's Desk standing items (outside this 24h but flagged as item-zero class): the open PII decision; the direct-RSS rights memo (OPEN item 3); external anchoring of sealed hashes | Buyer's Desk diligence list |

**Chairman — your decision per item.**
