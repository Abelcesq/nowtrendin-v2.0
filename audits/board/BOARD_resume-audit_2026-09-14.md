# BOARD COLLATION — resume audit + deploy + data continuity — 2026-09-14

Nine seats convened in parallel on `EVIDENCE_PACK_2026-09-14_RESUME-AUDIT.md` (items I1–I8),
each in isolation, each instructed to reproduce pack figures from the repo (HEAD `b49cad1`;
engine endpoints egress-blocked — every seat marked production claims unverifiable-from-here).
Per protocol this is a COLLATION, not a blend. **Chairman — your decision per item.**

Independent reproduction: five seats re-ran `tools/run_tests.py` (16/16) and
`tools/integrity_gate.py` (PASSED; several noted 21/21 enforced + 1 deliberately-OPEN
`C-DFLOOR-SCORE`) — the pack's gate figures held for every seat that checked.

---

## THE HEADLINE THE CHAIRMAN SHOULD READ FIRST

**The pack's data-continuity conclusion (I1) did not survive the board.** No seat accepted
"no evidence of data loss" as written. The sharpest finding (Statistician, code-verified):
the Apify billing screenshot evidences the **ledger/validation path only — 1 of 28 rows in
`COLLECTOR_EXPECTATIONS`** — because primary Google-Trends discovery
(`discovery_collectors.py:137`) is keyless RSS, not Apify. And "600 payloads written" is the
configured ceiling `PRECOMPUTE_TOP_N=600` with no freshness predicate
(`maint_precompute.py:34`, `gravitational_anomaly_detector.py:13157`) — a DB frozen since
08-24 emits the identical line (Challenger + Statistician independently). The honest current
statement: **"database up; Trends-validation billing continuous (1 of 28 collectors);
continuity of the other 27 unmeasured."** The settling test every seat converged on, and it
is cheap: per-collector, per-day row histograms over 08-24→09-14 from
`velocity_scores`/signal tables (retention covers the whole window) plus one
`/health/collectors` read.

---

## MEMOS (faithful condensations; full texts in the session transcript)

### 1. CHALLENGER (accuracy attack)
I1 **REJECT as worded** — spend is an invocation metric; 600 is a saturating cap; precompute
proves reachability, not freshness; absence-of-evidence published as evidence-of-absence.
I2 **A-W-C** — no build-provenance stamp exists (`"version": "1.0.0"` hardcoded; no slug
commit on `/health`), so the re-probe cannot establish WHICH commit serves; require a slug
SHA match before saying "on the wire." I3 A-W-C — diff rebuilt skill text against code
definitions before any figure they produce is published. I4 A-W-C — `integrity_gate.py` is
NOT in the CI gate; `paths: transfer/**` lets repo-HEAD and engine drift. I5 APPROVE —
the class infects every green-run citation including I2. I6 priorities: (1) **anomaly_log
survivorship** — `_prune_anomaly_log` (`:1252`) deletes >30d rows but preserves
`was_confirmed=1` forever → any confirmation rate over a >30d window is structurally
inflated; 542 rows just deleted; only COUNT(*) reads it today — fix before a figure is
built on it. (2) **Sweep retroactive-denominator edit** — today's `_is_quality_topic` is
applied to PENDING rows only (~:590), never to resolved LED rows; exclusion preferentially
removes rows heading for FALSE_POSITIVE → direction flatters; stamp the gate version,
publish the excluded count. (3) `[:10]` in `arrival_clock.py` TRUNCATES timestamps — ±1
calendar-day shift ≈ 100% error on a 1-day lead; highest-value trace of the eight.
(4) Ruling 5. I8 **REJECT the posture** — `/prewarm` is in-process memory; the deploy
restarted dynos, so the 09-13 outage is retrospectively unanswerable; say so; persist
status+latency to a retained store.

### 2. FIRST-PRINCIPLES GUARDIAN
I1 A-W-C — inference dressed as conclusion; promote the "NOT verified" list to a stated
exclusion boundary. I2 A-W-C — **`transfer/requirements.txt` is unpinned (30 `>=`, no
`==`)**: CI and Heroku resolve dependencies independently, so a green gate does not
describe what serves, and an upstream bump can move scores with no commit — a moat defect;
pin, and record the resolved set beside `PAYLOAD_SCHEMA_VERSION`. I3 A-W-C — rebuilt
skills sit beside genuine backups with no marker; label reconstructions. I4 A-W-C — add
`integrity_gate.py` to the gate; `workflow_dispatch` needs a protected environment.
I5 **REJECT as assurance** — delivery must be a committed artifact, absence alarms.
I6: ruling 5 first (only open item that can silently corrupt the detection history).
I7 — purge; "history never deleted" protects the ledger, not the source repo. I8 A-W-C —
the external check must assert payload freshness + schema stamp, not HTTP 200.
**NEW DEFECT:** `anomaly_log` asymmetric retention (confirmed-kept/unconfirmed-pruned)
makes the served `gravitational_anomalies` count survivorship-biased; ledger itself
unaffected; fix symmetry or stop serving the count.

### 3. EXPANSIONIST
I1 A-W-C — continuity is only claimed for the US/English lane
(`collect_all_discovery(geos=("US",))`); name the universe. I2 A-W-C — add a release
smoke-read; human re-probes don't survive scale. I3 APPROVE — put the skill roster under
the integrity gate. I4 A-W-C — **the workflow's "guard against forks" comment has no
matching condition** (only an empty-secret check): add `if: github.repository == ...`;
pin `actions/checkout` to a SHA (public repo + secret); app/region hard-coded — 
parameterize now. I5 finding APPROVE / status-quo REJECT. I6 **REJECT current order —
ruling 5 FIRST**: reproduced `_title_sig` (`dual_pathway.py:173-191`) — the final
space-tokenized step is a no-op for CJK/Thai → exact-string matching → five mastheads on
one wire story read as five voices → `mainstream_confirmed` inflates ONLY in non-Latin
markets; already blocks `_corroboration_at_enroll` re-enable. Fix = grapheme/character-
window signature, backtested ASCII-byte-identical. I7 — GDPR conversation in every EU
deal; acceptance alone won't clear enterprise DDQ. I8 A-W-C — the external check is the
only non-optional part. **Standing locale blockers (for the queue):** `language=en`
hard-coded ×3 in news collectors; `youtube_transcript.py:54`; `fastlane_recheck.py:73`
geo=US no param; 16-name US-only `WATCHLIST_TICKERS`; **Apify Trends payload declares no
geo (`google_trends_validation.py:193`) — the proof asset's lead-times cite no market**;
GDELT is the one multilingual lane already owned.

### 4. OUTSIDER / BUYER'S DESK
One-liner for partners: "a measurement vendor that scores attention acceleration and keeps
a held-out ledger of whether it flagged moves before Google Trends." I1 A-W-C (gates 7/1) —
which collectors, by name, have a dated row inside the window? I2 A-W-C (gate 2/App-Annie) —
a schema-stamped artifact nobody verified is a methodology claim without evidence.
I3 APPROVE — label reconstructions; stale retention text becomes wrong DDQ answers.
I4 **REJECT as written** (gates 2/9) — public repo + force-push to prod + no environment
protection/reviewer/rollback/pinned SHAs; the fork guard is a comment. I5 APPROVE finding
(gate 2) — which other green signals confirm invocation rather than output? I6 buyer's
order: I4 secrets → I7 PII → ruling 5 (fails open is unacceptable in a scored product) →
uptime → 6/9 → B. I7 — disclosure is the most credible document here, BUT: **PII_POLICY §2
and the FISD DDQ both cite a `PII-AUTHOR-HISTORY` tracking row in `audits/DEFERRED_ITEMS.md`
that DOES NOT EXIST** — a buyer-facing control claim with no backing artifact is App Annie
verbatim; purge, contact the fork, complete the Drive copy, create the row or delete the
sentence. I8 A-W-C — no uptime check exists anywhere in the repo (verified); make it the
deliverable; "how would you have learned about the 503 without opening the site?"

### 5. EXECUTIONER
Reproduced the release strings and the transactional swap (`:13210` zero-build guard,
rollback-on-exception) — genuinely non-destructive. **The through-defect (I2/I4/I5): the
success signal never observes the outcome** — `maint_precompute.py:41` returns 0 by
contract, so a failed release cannot fail a deploy; no post-deploy smoke check. **Ship
order: I8a (external uptime probe — only durable artifact, no engine change; verify by
forcing a fail) → I4 hardening (PR CI on `pull_request`; pin Python across CI/runner/
Heroku — no `runtime.txt` exists; post-push `/health` + schema assert; document
`heroku releases:rollback` as THE rollback — force-push is not git-revertible) → I2-close
(browser re-probe; until then 2c/4c/7 are DEPLOYED-UNVERIFIED, never DONE) → I5 (Routine
asserts its artifact via `git ls-remote`, else fail loudly; verify by disabling delivery
once) → I3 (invoke both rebuilt skills once) → I6 → I1 (narrow wording; gate on one
`/health/collectors` read). I7: **CUT purge-vs-acceptance from the ship queue** (counsel/
Chairman call, no executable step; a fork makes purge non-total) — **SHIP the Drive copy
today (~10 min)**. Cut for now: 3c (gated), 6 (self-referential), 9 (blocked; revisit
after I8a).

### 6. ECONOMIST
I1 A-W-C (Taleb, silent evidence) — invoices ≠ rows; a wedged actor still bills; falsifier
is the per-day `signal_date` series. I2 A-W-C (R&R) — mark rows DEPLOYED-UNPROBED; a green
run is a push receipt. I3 A-W-C — 23-vs-"21+2" reconciliation and the stale retention line
are live routes to a wrong public number. I4 A-W-C (Bernstein) — only workflow in the
repo → gate runs at deploy never on PR; unpinned pip + live NLTK download inside the
deploy path; no prior-SHA record; add a protected Environment. I5 **REJECT the mechanism**
(Smith — a distorted price) — each fire should verify the PREVIOUS fire's artifact; n=1,
conclude nothing about the cadence either way. I6 order by tail loss: I1 falsifier →
ruling 5 → I8 external detection → I5 → ruling 6 → charter rows → `[:10]`. I7 **purge**
(Kindleberger — delay compounds); sequence: Drive copy FIRST (the only unreproducible
asset the purge endangers) → purge → notify fork owner. I8 A-W-C — primary detector must
be an external synthetic probe of the exact failing call, 5-min cadence, phone alert,
**writing a retained availability series**. PRESCRIPTIONS: (1) make the H13 null-baseline
a publication gate, not a footnote; (2) headline top-decile-by-magnitude capture +
magnitude-weighted lead time, not blended hit rate; (3) build the per-collector continuity
series as the ledger's sibling — the next absence becomes self-diagnosing; (4) stage-tag
detections (displacement vs euphoria); (5) pre-register each sweep's expected lead-time
distribution, score realized-vs-predicted — and log predictions before probes in our own
audits; (6) estimate and publish inorganic share per signal.

### 7. OPERATOR (edge + survival)
EDGES: the ledger is the only durable edge (expiry: the day the rate stops being
reproducible from rows; capacity constraint is CONFIRMATION COST, which scales with
coverage — sampling it kills it; it is already thinning: 3 weeks of unadjudicated pending
rows, and no report segments hit-rate by provider or param_version). Plumbing continuity
is partially evidenced; the workflow and skills are not edges. **SURVIVAL — THE HIDDEN
COMMON FACTOR: `APIFY_TOKEN` + the single actor `apify~google-trends-scraper` feed the
detection path AND its own ground truth** (validation, calibration, fastlane, lead-moat,
monitoring); the provider fallback chain degrades silently to "manual" — the ledger stops
confirming rather than screaming, and a mid-series provider switch blends two measurement
instruments. **PRE-COMMITTED RULE: no aggregate hit-rate published across more than one
`provider` or `LEDGER_PARAM_VERSION` value — segment or refuse.** S2: the laptop SPOF was
traded for `HEROKU_API_KEY`-in-public-repo force-push with no environment gate and no
recorded prior SHA — same founder dependency, relocated. S3: no restart before `/prewarm`
age is captured. S4 (TCI): trust damage lands after the fix; undecided-past-30-days
auto-escalates to purge — that clock expired ~09-23. Verdicts: I1 DECAYING · I2 durable-
action/open-risk (48h trigger: unprobed → mark UNVERIFIED) · I3 not-an-edge (mark
reconstructions) · I4 DECAYING · I5 class defect (10-01 fire delivers nothing → disable
the Routine rather than keep a green light lying) · I6 order: provider-segmentation rule →
ruling 5 → re-probe → ruling 6 → I4 guardrails → 9 → B · I7 DECAYING · I8 durable-but-
incomplete (uptime check off-Heroku off-laptop; add a second Heroku collaborator — the
founder is a single point of failure for recovery itself). The winning streak is the
poison: today went well; apply MORE scrutiny.

### 8. STATISTICIAN
I1 **UNSUPPORTED** — the 1-of-28 scope finding (headline above); disclosure grade C
(vendor invoice); the per-day histogram doubles as the reflexivity instrument — a 3-week
attention gap changes the baselines the score deviates from. I2 SOUND-as-action,
verification incomplete — Heroku release failures land AFTER the push and never fail the
job; release log line is grade C until re-probed. I3 SOUND, one defect — stamp the two
rebuilds RECONSTRUCTED; diff the 21 against backups. I4 **OVERFIT-RISK (unmeasured
pipeline)** — N=1 and no instrument; note the `paths:` filter did NOT match `167d849`
(mode-change only) — it fired on the push's other commits; fragile both directions; log
every deploy to a retained table with the deployed SHA. I5 UNSUPPORTED — do not claim a
cadence until ≥3 consecutive fires deliver. I6: continuity read first (every other
number's denominator depends on it) → delivery-verification → ruling 5 → ruling 6 (the
register is asserted-and-checked, never falsification-tested — that is the folklore risk)
→ rest. I7 — if purged, record hashes of what was removed; recommends acceptance + Drive
copy. I8 UNSUPPORTED as posed — N=1 browser read cannot separate the four 503 causes;
retained time series with N, window, grade.

### 9. FORECASTER
I1 MIS-SCORED — criterion sealed after the fact and only partially; per-collector daily
coverage with Wilson intervals, not a global pass/fail; state "per-collector continuity
UNRESOLVED." I2 UNSCORABLE until re-probe — the criterion WAS sealed before the fact
(ruling 4c's "DONE only after it"); keep DEPLOYED ≠ DONE; any summary saying "on the wire"
converts an unresolved instance into a win. I3 WELL-SCORED narrowly — the rebuilds'
criterion ("behaves as the laptop copy") is unsealed and now unsealable; score them
unresolved, not migrated. I4 MIS-SCORED, same defect as I5 in code — "green" = push
accepted; seal: release SUCCEEDED + `/health` 200 within N minutes or the job fails.
I5 MIS-SCORED (the reference case) — record Sept-1 as **RESOLVED NO**, never rolled
forward. I6 — order by resolvability: ruling 5 → 9 + the waiting re-probes (sealed
criteria close cheaply) → ruling 6; **A4-SEQ's prereg already writes UNSCORABLE and
forbids silent extension — honor it, the absence must not become an unsealed extension.**
I7 UNSCORABLE as posed — becomes scorable the moment either option carries a dated
criterion. I8 MIS-SCORED — the single-restart construction is right (cheap, reversible,
asymmetric); the uptime check has no sealed criterion and does not exist; "site was up
when I looked" is survivorship sampling by a human. Standing objection: the 365-day
windows are load-bearing; the urge to show progress fast after an absence is the exact
pressure that shortens windows. Hold them.

---

## DISAGREEMENTS (signal, not noise)

1. **I1 severity** — a clean gradient from APPROVE-WITH-CONDITIONS (Guardian, Expansionist,
   Buyer's Desk, Economist) through REJECT-as-worded (Challenger), DECAYING (Operator),
   MIS-SCORED (Forecaster), to UNSUPPORTED (Statistician). No seat defends the original
   wording; all converge on the same settling test (per-collector per-day histogram +
   `/health/collectors`). The disagreement is only how bad the current sentence is.
2. **What comes FIRST in the queue** — four camps: ruling 5 first (Guardian, Expansionist,
   Economist, Forecaster); the I1 continuity read first (Statistician); the external uptime
   probe first (Executioner, and Operator's S3 leans there); I4 secrets/environment first
   (Buyer's Desk). Not actually incompatible: the uptime probe and continuity read are
   founder-browser/hours-scale, ruling 5 is a build — they can run in parallel lanes.
3. **Ruling 6 (register truthfulness)** — Executioner CUTS it for now (self-referential);
   Guardian, Statistician and Forecaster rank it high (the folklore risk). 
4. **The `[:10]` traces** — Challenger elevates the `arrival_clock.py` truncation
   (±1-day error on a 1-day lead) to near the top; Operator and Economist cut/defer all
   eight as hygiene.
5. **I7 PII** — purge now (Economist, Guardian, Expansionist-by-implication, Buyer's Desk;
   Operator's pre-committed rule says the 30-day undecided clock ALREADY expired →
   auto-escalate to purge) vs written acceptance + recorded hashes (Statistician) vs
   remove-from-ship-queue-except-Drive-copy (Executioner) vs make-either-option-scorable
   (Forecaster). Unanimous subset: **the Drive copy happens first, today, under every
   option.**
6. **I4 verdict** — REJECT as written (Buyer's Desk) vs harden-in-place (everyone else).
   The union of asks is one worklist: GitHub Environment + required reviewer; PR CI;
   `integrity_gate.py` in the gate; pin actions/Python/requirements; real fork condition;
   post-deploy smoke assert (release outcome + schema stamp + slug SHA); record prior
   Heroku SHA; parameterize app/region; log deploys to a retained table.

## NEW DEFECTS THE BOARD FOUND (not in the pack)

| # | Finding | Seats | Where |
|---|---|---|---|
| N1 | Apify billing evidences 1 of 28 collectors (validation path, not discovery) | Statistician | `google_trends_validation.py` vs `discovery_collectors.py:137` |
| N2 | "600 payloads" = configured cap, no freshness predicate — zero diagnostic power | Challenger, Statistician | `maint_precompute.py:34`, `:13157` |
| N3 | `anomaly_log` asymmetric retention → served count survivorship-biased (ledger unaffected) | Guardian, Challenger | `_prune_anomaly_log` `:1252` |
| N4 | Sweep applies today's quality gate to PENDING rows only → direction flatters | Challenger | sweep ~`:590` |
| N5 | `requirements.txt` unpinned (30 `>=`) — CI ≠ wire; scores movable with no commit | Guardian, Economist | `transfer/requirements.txt` |
| N6 | No build-provenance stamp — `/health` can't say which commit serves | Challenger | hardcoded `"version": "1.0.0"` |
| N7 | Workflow: fork-guard comment has no condition; checkout unpinned; no PR CI; no post-deploy assert; `integrity_gate.py` not in gate; no `runtime.txt`; prior SHA unrecorded; app/region hardcoded; paths-filter fragility (didn't match `167d849` itself) | Expansionist, Executioner, Economist, Challenger, Statistician, Buyer's Desk | `.github/workflows/deploy-engine.yml` |
| N8 | `PII-AUTHOR-HISTORY` row cited by PII_POLICY §2 + FISD DDQ does not exist in DEFERRED_ITEMS — buyer-facing control claim without artifact | Buyer's Desk | `docs/buyer-diligence/` |
| N9 | Apify single-vendor common factor under detection AND ground truth; silent provider fallback; no hit-rate segmentation by provider/param_version | Operator | provider chain `google_trends_validation.py:69` |
| N10 | Locale hard-codes throughout (geo=US, language=en, no-geo Trends payload on the proof asset) | Expansionist | multiple, listed in memo |
| N11 | `maint_precompute.py` returns 0 by contract → a failed release can never fail a deploy | Executioner | `maint_precompute.py:41` |
| N12 | 09-13 503 is retrospectively undiagnosable — deploy restarted dynos, `/prewarm` is in-process memory | Challenger, Statistician, Executioner | `_PREWARM_STATUS` `:6629` |

## VERDICT TABLE

| Item | Chal | Guard | Expan | Buyer | Exec | Econ | Oper | Stat | Fore |
|---|---|---|---|---|---|---|---|---|---|
| I1 continuity | REJECT-wording | AWC | AWC | AWC | SHIP-LATER | AWC | DECAYING | UNSUPPORTED | MIS-SCORED |
| I2 deploy | AWC | AWC | AWC | AWC | SHIP/not-closed | AWC | open-risk | SOUND-action | UNSCORABLE-yet |
| I3 skills | AWC | AWC | APPROVE | APPROVE | SHIP | AWC | not-edge | SOUND | WELL-SCORED |
| I4 workflow | AWC | AWC | AWC | **REJECT** | SHIP-LATER | AWC | DECAYING | OVERFIT-RISK | MIS-SCORED |
| I5 board round | APPROVE-finding | REJECT-mech | APPROVE-finding | APPROVE-finding | SHIP-fix | REJECT-mech | class-defect | UNSUPPORTED | MIS-SCORED |
| I6 queue | reorder | reorder | REJECT-order | reorder | reorder | AWC | reorder | reorder | reorder |
| I7 PII | (lens) | purge | (GDPR note) | purge+fix-row | Drive-now | purge | purge-clock | accept+hashes | make-scorable |
| I8 prewarm | REJECT-posture | AWC | AWC | AWC | resequence | AWC | incomplete | UNSUPPORTED | MIS-SCORED |

**Convergent board asks (no seat dissents):** (a) external uptime probe, off-Heroku,
retained time series, phone alert — build first or nearly-first; (b) per-collector
continuity read before the continuity claim is repeated; (c) the founder browser re-probe
closes I2 or the ledger rows read UNVERIFIED; (d) ruling 5 near the top — score-affecting
and fails open; (e) delivery = artifact-verified for every automation (I4+I5 are one
defect class); (f) Drive copy today; (g) mark the two rebuilt skills RECONSTRUCTED and fix
the stale retention line.

**Chairman — your decision per item.**

---

## POST-COLLATION LIVE EVIDENCE (founder screenshots, arrived AFTER all nine memos — noted here for the record, memos above are untouched)

Heroku dashboard, app `nowtrendin-v2-engine`, read ~01:07 UTC 09-14:

- **Deploy v374 = slug `2d42c905` — exactly the subtree SHA the Actions run force-pushed.**
  This answers the Challenger's "which commit serves" for THIS deploy (grade B, dashboard-read):
  the rounds-4/5/6/8 + 4c + 2c + ruling-7 code IS the running slug. Prior head v373 = `6f6d76ad`
  (Aug 23) matches the recorded pre-push SHA. `SIGNAL_RETENTION_DAYS` config var set Aug 20 (1b)
  visible in activity.
- **Engine UP, database serving reads:** `GET /monitor/catchall → 200` in 10.7s;
  `GET /prewarm → 200` in 2ms (602 bytes — CONTENT not captured; still the open question).
- **The 503 signature, precisely:** `GET /topics?limit=100` and `GET /categories` both
  returned **503 after exactly ~25.0s service time** — the single-flight wait-then-honest-503
  pattern: the superset build did not complete within the wait window. Dashboard shows
  repeated ~25s response-time spikes and **6 critical errors over 24h** → this is recurring,
  not a one-off cold boot.
- Dynos: professional 2X, web=1 green; memory ~45%; add-ons Postgres **Essential-1** +
  Heroku Scheduler.
- **Leading hypothesis (UNTESTED — §10a, do not deploy on it):** ruling 1b raised
  `SIGNAL_RETENTION_DAYS` 7→30 on Aug 20; the signal tables then grew toward ~4× their
  historical serving size across the unattended window; the `/topics` superset build may now
  exceed the single-flight wait budget on the Essential-1 Postgres. Discriminating tests:
  `/prewarm` JSON (per-feed build durations / last_run), "[prewarm]" log lines over one loop,
  and per-day row counts. Competing hypotheses not excluded: pool contention, a slow query
  introduced in the new slug, plan throttling.
