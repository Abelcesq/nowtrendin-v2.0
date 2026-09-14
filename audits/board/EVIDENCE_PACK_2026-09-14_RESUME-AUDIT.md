# EVIDENCE PACK — 2026-09-14 resume audit + deploy (for the nine-seat board)

**What is being decided:** the founder returned from a 3-week absence (laptop off,
08-24 → 09-14) and asks the board to assess the data collected and the actions taken in
today's resume session, and to recommend priorities. Eight items (I1–I8) are under review.
This pack states only what was OBSERVED, with the observation method; seats are expected
to verify independently against the repo at HEAD (`b49cad1` on main).

## Session facts (each with its verification method)

- **Repo state:** `origin/main` sat at `e1336be` (08-23) until today; `claude/resume-kp9t5p`
  (`1d732d0`, 8 commits, 08-24) was never merged — the 08-24 handoff (merge + engine deploy)
  died when the laptop shut down. Verified: `git ls-remote`, `git merge-base`. Today main was
  fast-forwarded `e1336be` → `1d732d0` → `167d849` → `b49cad1` (founder-authorized).
- **Local gates at `1d732d0`/HEAD:** `tools/run_tests.py` **16/16 pass**;
  `tools/integrity_gate.py` **passes** (all asserted claims enforced; ruling-6 sub-items on
  the register's own truthfulness remain open, so treat as asserted-and-checked, not
  falsification-tested). §13 stale-window rule HOLDS (risk 420=360+60; issuer_* 360 rides
  the 4h ETF loop). §14 `[:10]` scan: 8 string-date slice sites flagged for one-look traces
  (arrival_clock.py:108,113,148,169,384; av_dark_positioning.py:98; calibration_agent.py:230;
  coinmetrics_onchain.py:120) — flagged, NOT asserted as defects.
- **ENGINE DEPLOY EXECUTED 2026-09-14 00:46 UTC** — the item owed since `4d5aa97` (08-22).
  Method: new `.github/workflows/deploy-engine.yml` (push to main touching transfer/** →
  test gate → `git subtree split --prefix transfer` → force-push to
  git.heroku.com/nowtrendin-v2-engine). Run 34793568793 green end-to-end. Release-phase log
  (verbatim): `[precompute] serve_payload written for 600 topics (schema 2026-08-24.1, swap
  transactional)`; also `[prune] anomaly_log: removed 542 old unconfirmed rows`. This puts
  rounds 4/5/6/8 fixes, the 4c tri-state, 2c's release phase, and ruling-7's
  `payload_contradiction_auditor` on the wire. **Re-probe NOT yet performed** (see network
  constraint) — ledger rows 2c/4c/7 record DEPLOYED, with re-probe owed.
- **Network constraint:** this cloud session's egress proxy 403-blocks `*.herokuapp.com`
  (verified: curl + WebFetch both denied). No live engine endpoint was read this session.
  Every claim about production comes from the deploy log, the founder's screenshots, or
  repo state — never from a live probe.
- **Production incident (founder-observed 09-13 ~20:26 ET, screenshot):** web terminal
  `/topics?limit=100&offset=0 → HTTP 503` against nowtrendin-v2-engine. Cause NOT
  diagnosed (§10a): consistent with cold cache/warming, wedged prewarm, pool exhaustion,
  dyno/billing, or Postgres-plan pressure. The deploy restarted dynos + precomputed 600
  payloads AFTER the screenshot. Founder asks specifically whether the **Prewarm Agent** is
  running; only a browser read of `/prewarm` (last_run age) can answer it.
- **Data-continuity evidence over the absence:** (1) founder's Apify billing screenshot:
  DAILY paid usage 09-01→09-14, ~$2.3–3.1/day (pay-per-event + actor CU + residential
  proxy + dataset ops) — the scheduled Trends pulls fired every day; RAM/usage panel showed
  $19/$200. (2) Release-phase precompute read live Postgres and wrote 600 topic payloads —
  DB up and populated as of 00:46 UTC today. (3) Retention: velocity_scores 365d;
  `SIGNAL_RETENTION_DAYS=30` (raised from 7 in round 5, floor sealed under L1) — the whole
  absence window is inside retention. NOT verified: per-collector health (token expiries,
  X budget, GDELT, ghost feeds), /monitor alert backlog, catchall_floor_log continuity.
- **Scheduled board round (ruling 10):** Routine `trig_01RJfPrxbGoFcdFdwhqQ4omn` fired
  2026-09-01 06:33 UTC, run status SUCCEEDED (finished 06:48), but **no
  `claude/board-round-*` branch exists on GitHub** (verified `git ls-remote`) — the round
  delivered nothing; run status tracks the session, not delivery. Next fire 10-01.
- **Skills:** the laptop-only skill roster (21 backups in `docs/skills/`; 2 with no backup)
  was installed into repo `.claude/skills/` (23 skills) — cloud + laptop sessions now load
  them. `/engine-recovery` + `/improve-system` rebuilt from SESSION_LOG/audit README.
- **Doc drift found:** AGENT_CHARTER.md documents Agents 1–16; the live engine roster
  additionally ships 8 undocumented agents (heldout_firewall, flow_integrity,
  similar_fragmentation_agent, etf_reconcile_watch, crypto_price_referee,
  payload_contradiction_auditor, scoring_contract_auditor, feed-silence tripwire).
  The `/nowtrendin2.0` skill text also still carries stale lines (e.g. "90-day retention,
  365 pending confirmation" vs CLAUDE.md §13's canonical 365).
- **Platform parity ("calibrated into all platforms"):** engine payloads regenerated at
  deploy (schema-stamped). Web terminal: last gh-pages deploy 2026-08-23 == last
  web-terminal source change (2026-08-23, `e1336be`, includes the 4c Screener tri-state) —
  no undeployed web changes. Desktop (Tauri) wraps the same web build. Mobile: frontend/
  source current at main (4c guards `4d5aa97` in frontend/components/trends/); serving via
  Expo depends on the founder's Metro session. Local web-terminal build: **CLEAN**
  (`npm ci && npm run build` → `✓ built in 3.35s`, this session).
- **Open founder decisions (from 08-24, unchanged):** PII incident
  (`audits/infra/INCIDENT_snapshot-gz-public_2026-08-24.md`): the two author-handle `.gz`
  snapshots are off the tip but IN public git history; 1 fork exists; history purge vs
  written acceptance undecided. Drive second copy of the snapshots still owed.
- **Deadlines during the gap:** FMP re-eval 09-05 passed unread; D-REMINE due 09-30;
  `/monitor/deferred-triggers` unread since 08-24; A4-SEQ shadow trial opened 09-01
  (state unknown).

## Items under review (verdict per item, per seat)

- **I1 — Data-continuity conclusion.** Proposed finding: "no evidence of data loss over
  the absence; collection continued (Apify daily spend, live precompute); the empty UI was
  a serving failure, not missing data." Is this conclusion sound on the evidence offered,
  and what would falsify it?
- **I2 — The deploy.** The owed deploy was executed via the new pipeline; release-phase
  precompute succeeded; re-probe still owed. Assess the action and its remaining risk.
- **I3 — Skills-in-repo migration.** 23 skills now repo-tracked (.claude/skills), two
  rebuilt from logs. Assess correctness/completeness/risks of the migration.
- **I4 — The cloud deploy workflow itself.** GitHub Actions, HEROKU_API_KEY repo secret,
  test-gate-then-force-push-subtree, fires on push to main touching transfer/**. Repo is
  PUBLIC. Assess design, safety, failure modes, and what guardrails are missing.
- **I5 — Scheduled board round delivered nothing.** Fired, SUCCEEDED, no branch pushed.
  Assess the delivery-verification gap and remedy (the run-status-is-not-delivery class).
- **I6 — Outstanding queue prioritization.** Open: rulings 3c (gated), 5 (CJK quorum,
  score-affecting, fails open), 6 (register truthfulness sub-items), 9 (needs production),
  Section B (18 items), charter rows 17–24, [:10] traces, stale-skill refresh. Recommend
  the order and what, if anything, should be cut.
- **I7 — PII incident decisions.** History purge vs written acceptance; the fork; the
  Drive copy. What does each seat recommend the Chairman decide?
- **I8 — Prewarm/503 posture.** Founder suspects the Prewarm Agent is not running. From
  this session nothing engine-side is verifiable. Assess the proposed posture: founder
  browser reads `/prewarm` + `/monitor` first (evidence before intervention), single
  restart only if prewarm is wedged, and a standing external uptime check so a serving
  outage is DETECTED without a human looking at the site. Improve or replace it.

**Chairman = the founder.** Memos inform; the founder rules.
