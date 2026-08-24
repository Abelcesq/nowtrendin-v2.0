# REGIME LEDGER — append-only collection-regime events
### Board-ordered 2026-08-20 (Economist prescription 7; Friedman & Schwartz discipline:
### long panels settle arguments only if the observer knows when the instrument changed).
### RULES: APPEND-ONLY — rows are never edited or deleted; corrections are new rows citing
### the old. EVERY backtest, case study, mining run, and trial readout MUST cite the regime
### rows spanning its window. A published number whose window silently crosses a regime
### boundary is a defect (the A2.2 as-of lesson, generalized).

| Date (UTC) | Event | Effect on series |
|---|---|---|
| 2026-06-12 | Reddit credentials deferred (founder) | First-timer numerator loses its primary author surface; unnoticed: stale creds kept the collector attempting (403s) rather than disabled |
| 2026-06-12 | Sports/culture desks added to NEWSLETTER_FEEDS (niche tier) | Football365 URL dead from day one (0 rows ever, found 2026-08-20) |
| 2026-06-26 | Mainstream v2 (`MAINSTREAM_V2=1`) | News corroboration becomes quorum-based; syndication collapse via `_title_sig` (ASCII-only — see 2026-08-20) |
| 2026-07-15 | `GHOST_RESEARCH_FEEDS=1` (founder flip) | 4 research outlets live at expert tier, entity-anchored extractor |
| 2026-08-05 | X scan cadence 12h + post budget 4,800/mo | X depth reduced; movers-only deep pulls |
| 2026-08-17 | Sealed ledger epoch begins; sealed queries/referee articles at enrollment | Resolution-time hindsight removed from new rows |
| 2026-08-19 | Quorum v2.1 (`MAINSTREAM_SPIKE_AS_OUTLET=1`) | Spike = one vote toward 5, never a standalone pass (backtested, 0 flips) |
| 2026-08-20 | Unicode fixes: `_title_sig` NFKD+unicode, tokenizer, `_ENTITY_RUN` (commits d4d73e0/1473e1c, engine v363) | Non-ASCII titles (17.9% of news) produce real signatures — corroboration counts for non-English topics are UNDERSTATED before this date; entity extraction no longer amputates diacritics |
| 2026-08-20 | `SPORTS_ENTITY_FEEDS=1` (engine v364); Football365 /feed→/rss (first rows ever); The Batch removed (dead) | 3 football desks route via entity extractor; niche sports topics become creatable |
| 2026-08-20 | Tech filter removed: WordPress tags +12 domains, Blogger terms +12, socialcrawl seeds 6→12 (same budget — per-seed cadence halves) | Non-tech collection begins on general platforms; incumbent seed cadence ~daily→~2d |
| 2026-08-20 | **Reddit FORMALLY RETIRED** (Chairman; stale creds unset, engine v365) | Author-bearing universe = GitHub/HN/bluesky/lemmy (+blog lane under D_PLUMBING_V2). Reactivation = new ruling + §16 re-onboarding |
| 2026-08-20 | `d_measured` column live (tri-state; NULL = rows before this date) | D honest-absence begins accruing; pre-epoch rows' D=0 is unlabeled (unknown blind-vs-quiet) |
| 2026-08-20 | `D_PLUMBING_V2` BUILT, default OFF (writer ft, author-bearing denominator, community-age guard) — backtested, flip pending Chairman | While OFF: series unchanged. THE FLIP DATE (when ruled) is D's largest-ever epoch boundary — record it here the day it happens |
| 2026-08-20 | **`D_PLUMBING_V2 = ON`** (Chairman-ruled, engine v367, ~22:2x UTC) | **D's largest epoch boundary**: real ft bits from blog lane; author-bearing denominator; community-age guard. First scored cycle on the new regime = the first post-22:30 cycle. D series NOT comparable across this row |
| 2026-08-20 | GHOST_RESEARCH_FEEDS: **KEEP** (Chairman-ruled at close-out) | Research feeds permanent roster; trial question transferred to shadow trial as UNANSWERED |
| 2026-08-20 | Ben's Bites + Wired AI URLs repointed (tripwire catches #1/#2 on its first production run) | Two silently-dead mainstream feeds resume |
| 2026-08-20 | Shadow-trial prereg SEALED (PIT `e90af6df..`) + M0 baseline sealed (`77d49c00..`) | Trial rules frozen before window opens 09-01 |

| 2026-08-20 (eve) | **CORRECTION to the row above** (this ledger's own rule: corrections are NEW rows citing the old). The `D_PLUMBING_V2=ON` row described the community-age guard as in force. It was NOT in force on the blog lane — the guard sat in the detector's function (github/HN/bluesky/lemmy) while the blog lane uses its own. Six board seats found it independently. | For any window between the flip (~22:2x UTC) and commit `d6de777`, first-timer credit on devto/hashnode/discourse/wordpress/blogger/medium/ghost was UNGUARDED — 12 new WordPress communities in particular could read ft≈1.0. Any analysis spanning that window must say so |
| 2026-08-20 (eve) | Guard landed on the blog lane; held-out firewall exception registered + commit-msg gate added; `d_measured` re-keyed to author resolution; pseudo-authors excluded; `engagement_divergence` degenerate-venue guard (`d6de777`) | `d_measured`'s 32.4% blind figure is an UNDERCOUNT until re-censused. Indicator values computed before this row are not comparable |
| 2026-08-20 (eve) | Shadow-trial prereg **ERRATUM 01** sealed (PIT `6f9ed05f..`, cites parent `e90af6df..`) | Operative trial epoch is now `d6de777`; non-English cohorts blocked pending arbiter-locale declaration and ES/DE acceptance fixtures |

| 2026-08-24 | **Paired A/B recompute RUN (ruling 1c)** — `tools/d_plumbing_ab.py`, offline over the frozen snapshot (`audits/ab-attribution/`, window 08-14→08-19, 274,185 joined rows / 168,983 topics / 17,471 scoring-eligible), seed 1082, row-level JSON retained locally (52 MB, sha256 `8534a2bf0391a085…`, not committed — deterministically reproducible from the committed script + seed + hash-manifested snapshot). T3 null check: **0 reddit rows → T3 drops; the confound set is 4, not 5**. Arm validity proven at compute time (fixture D 30.13 OFF vs 65.00 ON). | **PRIMARY (preregistered): pooled paired ΔD = −0.2418, bootstrap 95% CI [−0.3021, −0.1835], p≈0.0005**; `d_measured` flips 805 gained / 0 lost. **This identifies E[T5.compute \| T1..T4 = ON, pre-flip writer stamps] — the COMPUTE-side of ONE treatment, conditionally.** The writer-side of T5 (real ft bits) is NOT identifiable from pre-flip stamps; T1–T4 main effects are permanently unidentified BY DESIGN (rank-1). Exploratory (BH): positive ΔD concentrates in author-bearing blog/creator lanes (youtube +5.77, creator +3.47, newsdata +2.50, ghost +1.86), negative in rss/lemmy; ft-by-community-age NOT ESTIMABLE from the snapshot (ages not among its columns) |
| 2026-08-24 | **Snapshot PII incident** (see `audits/infra/INCIDENT_snapshot-gz-public_2026-08-24.md`): both preflip `.jsonl.gz` files had been on the PUBLIC repo tip since `fe6712b` (08-22), silently, against `e4215d4`'s own written intent (`.gitignore` matched `*.jsonl`, files were `*.jsonl.gz`). Measured 40.9% of raw_signals rows carry author handles (the recorded 30% was an estimate) | Tip removal + pattern fix executed under PII_POLICY §4. History purge / fork / Drive second copy = founder decisions, listed in the incident record. No series effect — inputs unchanged |

*Next expected entries: candidate-feed wiring dates; wiki-v3/GDELT referee arm; the
post-flip re-census of `d_measured`.*
