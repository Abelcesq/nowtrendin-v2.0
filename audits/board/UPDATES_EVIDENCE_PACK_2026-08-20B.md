# EVIDENCE PACK — Updates review: the Dark-Matter board's decision items, BUILT and RULED
### Prepared 2026-08-20 (evening UTC) for the nine-seat assessment convening.
### Material under review: everything built/ruled since the D-board collation (`BOARD_darkmatter_2026-08-20.md`) this morning. Commits: 9289ed2, b39f2e3, 8716502, d5b6ebf. Engine releases v363→v367.

The prior convening produced 11 decision items. The Chairman ruled: build all; Reddit
retire; D_PLUMBING_V2 flip ON; GHOST KEEP; seal the prereg. All are now EXECUTED. This
convening's question: **assess the execution — is each item built correctly, honestly,
and per its sealed conditions? What did the execution miss?**

## ITEM-BY-ITEM STATE (verify everything against the repo/live system; all paths repo-relative)

1. **Doctrine correction** — CLAUDE.md §footer + memory re-scoped to "D as instrumented
   never measured early; hypothesis untested," with code-verified reasons attached.
2. **Reddit FORMALLY RETIRED** — root cause found before acting: STALE credentials had
   defeated the collector's own no-creds guard since June (403 every cycle, never the
   "disabled" print). Creds unset (v365); docstring = retired; reactivation = new ruling
   + §16. Consequence recorded in `docs/D_UNIVERSE_STATEMENT.md`.
3. **GHOST close-out** (`audits/source-onboarding/GHOST_RESEARCH_CLOSEOUT_2026-08-20.md`) —
   headline: the advertised 07-15→07-29 window is UNMEASURABLE (operational tables ~7-day
   retention; oldest row 08-13 — the delay destroyed the evidence). Observable week: 136
   topics, 1 gate failure, 0 fragments, 0 attributable ledger contact. Chairman ruled KEEP.
4. **sports_entity completed** — Challenger's segment-initial club drop fixed (trim-residue
   rule + subject-verb rule); `tools/extractor_acceptance.py` = standing gate-3 fixture,
   hand-labeled corpora; measured 87.1% precision / 81.8% recall vs generic 10.2%/18.2%;
   acceptance doc written (`audits/source-onboarding/SPORTS_ENTITY_ACCEPTANCE_2026-08-20.md`).
5. **D_PLUMBING_V2** — all three verified defects repaired behind one flag: writer ft
   (7 call sites), author-bearing denominator (regime-dependent platform set), community-age
   guard (14d). Behavior-tested bit-identical off. Backtest
   (`audits/backtests/D_PLUMBING_V2_BACKTEST_2026-08-20.md`): 800 topics, median stays 0,
   FEWER nonzero (268→245), movers = the mixed news+expert cohort (nvidia 9→40, openai
   22→47). **FLIPPED ON by Chairman ruling (engine v367).** Limit stated: 7-day retention
   foreclosed an LED-cohort replay.
6. **d_measured honest absence** — tri-state column live via migration; stored by both
   INSERT paths; 32.4% of the working set structurally D-blind, now disclosed.
7. **Authorless indicators** (`transfer/darkmatter_indicators.py`, held-out, registered) —
   venue first-coverage (with the new-venue exclusion), incumbent displacement, breadth
   velocity, engagement divergence; None-not-zero on absent inputs; non-pruned snapshot
   table; `/diag/d-indicators`.
8. **Shadow ledger** (`transfer/shadow_ledger.py`, held-out, registered) — 4 arms enforced,
   enrollment window enforced in code (refusal verified), immutable resolutions,
   snapshot-at-enrollment, censoring-beside-every-rate INTERIM reports.
9. **Prereg SEALED** (`audits/forecasts/SHADOW_TRIAL_PREREG_2026-08-20.md`; PIT row
   `e90af6df..`, text `25b69ffc..`) — 9 days early, before any enrollment: named pathway,
   H-A lead-time distribution shift primary, thresholds with denominators, UNSCORABLE
   verdict, N≥10/arm/domain with honest base-rate context, instrument freeze at
   D_PLUMBING_V2=ON, censoring-honest readouts to 2027-11-30, referee-blindness statement,
   FROZEN candidate feed sets (Marca/Kicker · Nikkei/SCMP · STAT/Deadline/ScienceAlert —
   gate-4 verified live) + variant log (L'Équipe 404, NBER, Pew, CJK-deferred, Reddit).
   **M0 baseline sealed separately** (row `77d49c00..`: LED 8-zero/7-positive of 15, with
   the retention-erosion caveat stamped).
10. **Per-feed tripwire** — fixture-verified (34 silent flagged, live exempt), then on its
    FIRST production run caught two unknown dead feeds (Ben's Bites 404, Wired AI 400);
    both repointed to verified-live URLs same day.
11. **Registers** — `audits/REGIME_LEDGER.md` (append-only, 06-12→today, flip recorded);
    `docs/D_UNIVERSE_STATEMENT.md` (exclusion boundary as doctrine); DEFERRED_ITEMS +
    D-REMINE (dated 09-30) + D-RIGHTS (blocks licensing); socialcrawl `geo:"US"`
    parameterized (`SOCIALCRAWL_GEOS`, default preserves live behavior).

## FIRST-CYCLE VERIFICATION (live production, post-flag)

Football365: first 40 rows EVER. Sports topics aggregate as ENTITIES (`man utd` n=14,
`arsenal`, `premier league`, `xabi alonso`, `fabrizio romano`) — zero fragments observed.
All 11 new WordPress domains producing (17–32 rows each). Most recent cycle 22:18 UTC.

## KNOWN OPEN ITEMS (not claimed done)

Candidate feeds are SEALED but not yet WIRED (gates 1–3 + acceptance per feed before first
enrollment; window opens 09-01 — wiring this week keeps most of the 14-day age guard);
wiki-v3+GDELT referee arm (task #15) not started; D-REMINE re-run due 09-30; the first
scored cycle under D_PLUMBING_V2=ON had not yet completed at pack time; sweep-starvation
rewire (#16), commonMode surfaces (#17), CoinAPI harness (#18, gate ~08-24) outstanding.

## FILES (verify freely, read-only)

All cited above, plus `transfer/gravitational_anomaly_detector.py` (compute_dark_matter
~L4400, migrations ~L1634, tripwire in `transfer/monitoring_agents.py` ~L91),
`BOARD_darkmatter_2026-08-20.md` (the morning collation with the original conditions).
