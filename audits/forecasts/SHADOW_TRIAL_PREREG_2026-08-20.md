# PRE-REGISTRATION — A4 Shadow Trial (Dark Matter candidate feeds)
### Drafted 2026-08-20, to be PIT-SEALED on Chairman approval and NO LATER than 2026-08-29.
### Ruled sequence: A4-SEQ step 1 (Chairman 2026-08-19); contents per the nine-seat D board 2026-08-20 (decision item 6), all seat conditions incorporated.
### Instrument: `transfer/shadow_ledger.py` (held-out; registered in `heldout_registry`).

> **STATUS: SEALED 2026-08-20** (Chairman order: "fix the seal issue") — PIT row
> (`kind='forecast'`, `item_key=PREREG-shadow-trial-2026`), hashes in the seal block
> below, recorded BEFORE any enrollment (window opens 09-01). M0 baseline sealed
> separately (`M0-dark-early-2026-08-20`, row `77d49c00..`).

---

## 1. THE QUESTION (named pathway — Challenger condition)

**Does candidate-feed supply, measured through the repaired D instrument and the expert
pathway, surface topics that subsequently break out on Google Trends EARLIER than the
existing roster does?** The pathway under test is the EXPERT PATHWAY (G/detection via
expert-tier supply) **plus** the D component under `D_PLUMBING_V2` **plus** the four
held-out authorless indicators as measured covariates. This trial does NOT test the old
D-as-wired (its numerator was disconnected — testing it would be theater).

## 2. HYPOTHESES (sealed before data)

- **H-A (primary):** candidate-arm races achieve a LEAD-TIME DISTRIBUTION shifted earlier
  than control-arm races (Forecaster: distribution shift is the primary metric, not
  binary LED).
- **H-B:** candidate-arm race rate (races run / topics enrolled) exceeds each null arm's.
- **H-C (covariate, exploratory):** enrollments with venue-first-coverage or
  incumbent-displacement or breadth-velocity signals at enrollment show better lead-time
  than those without. Exploratory — informs the NEXT prereg, never this trial's verdict.

## 3. ARMS (all enrolled under IDENTICAL sealed rules, same window)

| Arm | Population |
|---|---|
| `candidate` | First-crossings from the candidate feed sets (§6) |
| `control` | First-crossings from the existing roster, same rules, same window |
| `null_random` | Random topics from the SAME candidate feeds (no signal logic) |
| `null_volume` | Topics with ≥3 expert-tier mentions, no D logic (dumb-volume rule) |

If candidate does not beat BOTH nulls, D-guided selection is noise dressed as insight
(Economist). An absolute rate from any single arm is NOT a result.

## 4. THRESHOLDS — every one with its DENOMINATOR (the referee-prereg drafting lesson)

- **Success (H-A):** median lead-time of RESOLVED candidate races ≥ 3 days earlier than
  median of RESOLVED control races, at minimum N per §5. Denominator: resolved races in
  the arm, pre-broken excluded (never a race), censored rows excluded AND counted beside.
- **Success (H-B):** candidate race rate > null_volume race rate + 10 points.
  Denominator: topics ENROLLED per arm.
- **UNSCORABLE** is a written verdict (Forecaster): if any compared arm has fewer than
  the minimum resolved N at a readout, that comparison reads UNSCORABLE — never "no
  edge," never extended silently. Extension is a new sealed note.

## 5. POWER / MINIMUM N (Statistician + Challenger condition)

Per-domain minimum resolved races for any comparison: **N ≥ 10 per arm per domain;
N ≥ 20 per arm pooled**. Domains are never pooled ACROSS (no scope-averaging); "pooled"
means the all-domain pre-declared aggregate only. Base-rate context (sealed honestly): the
real ledger produced 7 LED rows in ~2.5 months — single-digit resolved races per cell by
11-30 is LIKELY, which is why readouts are staged (§8) and UNSCORABLE exists.

## 6. CANDIDATE FEED SETS (each through §16 five gates + the extractor acceptance harness BEFORE enrollment — Operator condition, mandatory per roster)

**SEALED FEED SETS (frozen for the window; gate-4 access verified live 2026-08-20;
gates 1–3 + the extractor acceptance harness run per feed BEFORE its first enrollment,
wiring held-out):**

| Cohort | Feeds (feed_set id) | Domain |
|---|---|---|
| NON-ENGLISH (Latin-script per the case-anchor ceiling) | Marca (`marca-es`, 74 items), Kicker (`kicker-de`, 20) | sports |
| NON-US MARKET (English) | Nikkei Asia (`nikkei-asia`, 51), SCMP News (`scmp-hk`, 50) | geopolitics/business |
| NON-TECH DOMAIN | STAT News (`stat-health`, 20), Deadline (`deadline-ent`, 12), ScienceAlert (`scialert-sci`, 10) | health / entertainment / science |

**VARIANT LOG (every alternative considered — the forking-paths defense):** L'Équipe
(REJECTED at gate 4: /rss/actu_rss.xml 404 on the production UA, 2026-08-20); NBER
(REJECTED: two documented §16 FORMAT failures); Pew Research (REJECTED: report sub-page
pollution, 2026-07-07); any CJK/Arabic/Hebrew feed (DEFERRED: the case-anchor extraction
ceiling makes their null uninterpretable — D_UNIVERSE_STATEMENT §4); Reddit-based
candidates (EXCLUDED: platform formally retired 2026-08-20). No other variants were
tried; any variant appearing later must be appended here BEFORE its data is used.

## 7. INSTRUMENT FREEZE + REGIME (sealed facts)

- **Epoch:** engine code through commit 8716502 (v363–v367 releases) with
  **`D_PLUMBING_V2 = ON` (Chairman-ruled 2026-08-20, engine v367)** — the trial runs
  entirely on the repaired instrument and never straddles the boundary. NO mid-window changes to
  extractors, tiers, seeds, quality gates, or quorum constants on any enrolled feed's
  path; an emergency hotfix voids affected cells and is logged here.
- **Regime facts every analysis must carry:** Reddit FORMALLY RETIRED 2026-08-20
  (author-bearing universe = GitHub/HN/bluesky/lemmy + blog lane under V2);
  `_title_sig` unicode fix live; sports_entity live on 3 desks; the operational signal
  tables carry ~7-day retention, hence snapshot-at-enrollment (§9).
- **Cold-start guard (Guardian F2, non-negotiable):** candidate-feed communities carry NO
  first-timer credit until their collection age ≥ 14 days (`D_COMMUNITY_MIN_AGE_DAYS`,
  enforced in code under V2). Candidate feeds should therefore be WIRED (collecting,
  held-out) ≥ 14 days before 09-01 where possible; feeds wired later have their
  first-14-day enrollments stamped `calibrating` and excluded from H-A/H-B denominators.

## 8. READOUTS — censoring-honest (Forecaster condition, the largest defect fixed)

Enrollment closes **2026-11-30**. **Races run to the 365-day patience window.** The 11-30
readout is **INTERIM**, labeled so, with the censoring rate printed beside every number.
Scheduled readouts: **2026-11-30 (interim) · 2027-02-28 (interim) · 2027-05-31 (interim)
· 2027-11-30 (final)**. No shadow row appears in any UI, report, memo, or marketing
figure at any time; unresolved is never a pending win.

## 9. EVIDENCE + ADJUDICATION

- Snapshot-at-enrollment: every row stores signals/venues/D-indicators/d_measured at
  enrollment inside the shadow table (non-pruned) — the GHOST close-out lesson encoded.
- Arbiter: Google Trends sweep under the SAME match-validity stamps as the real ledger
  (`sweep_query`, `query_ambiguous` recorded; results always reported with the
  ambiguity split — Challenger condition).
- **Referee statement (sealed up front):** wiki-v2 is proven blind on the niche/early
  cohort (0/15 adjudicable). Unless wiki-v3+GDELT is live before a readout, shadow wins
  are Trends-adjudicated only and independently uncorroborated — reported as ABSENCE of
  referee measurement, never as doubt and never as support (§15a).
- M0 baseline: sealed pre-09-01 snapshot of D-at-each-ledger-row (`/diag/dark-early`),
  so before/after attribution is provenance-grade B, not reconstructed.

## 10. WHAT THIS TRIAL CAN NEVER DO (sealed exclusions)

Change any verdict, score, weight, or published rate; feed any indicator into scoring
(that requires its own sealed backtest + board + flip); rescue an underpowered cell by
pooling, extending, or re-defining after data; count a business or demo consideration as
evidence. A null with the extractor acceptance harness unrun on the affected roster is
UNINTERPRETABLE, not "no edge" (the Operator's standing rule, third invocation).

---
**PIT SEAL:** `row_sha256 e90af6df909de1393fc580622fecca53bdacf7a0cb056d0ec5b54a2c7789cf98` ·
`text_sha256 25b69ffc8e88d393348b73081477c586ff5ba7fa49d822541534ac9b497f6e3e` (document body
through the line before this block) · sealed 2026-08-20 UTC · `D_PLUMBING_V2 = ON` (engine
v367) · feed sets + variant log frozen above · M0 baseline row `77d49c00..` · sealed BEFORE
any enrollment (window opens 2026-09-01).
