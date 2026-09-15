---
name: improve-system
description: Weekly system-improvement audit for NowTrendIn 2.0 — eight-lens internal review (engineer, auditor, attorney, banker, VC, advisor, board, fiduciary) of system health, integrity/non-circularity, agent productivity, and accuracy vs external ground truth. Writes a dated report to audits/improve-system/. Use when asked to run the weekly audit, improve the system, or assess overall health.
---

> **RECONSTRUCTED 2026-09-14** from audits/improve-system/README.md — the laptop original was never
> committed and no backup survives, so "behaves as the original" is unverifiable
> (board ruling I3, `BOARD_resume-audit_2026-09-14.md`). Treat as a rebuild, not a restoration.

# /improve-system — weekly eight-lens internal audit

Rebuilt 2026-09-14 from `audits/improve-system/README.md` (the laptop-local original was
never committed). Output: `audits/improve-system/IMPROVE_SYSTEM_<YYYY-MM-DD>.md`.
**INTERNAL founder document. Read-only / flag-never-force — this audit never changes
scores, data, or config; it ranks findings and recommends.**

## Protocol

1. **Orient** — read CLAUDE.md (§10a first), SESSION_LOG.md newest entry,
   `audits/board/CHAIRMAN_RULINGS_2026-08-20D.md` status table, `audits/DEFERRED_ITEMS.md`.
2. **Health** — `GET /monitor` (agent roll-up), `/monitor/datecanon`, `/monitor/catmaps`,
   `/monitor/deferred-triggers` (the weekly walk — every trigger gets a read),
   `/monitor/degenerate-census`, `/x/budget`, `/prewarm`. From a cloud session (egress
   blocked) request these from the founder's browser, or run the repo-local equivalents:
   `python tools/run_tests.py` + `python tools/integrity_gate.py`.
3. **Accuracy vs external ground truth** — `/accuracy/ledger` (trend, maturity-segmented +
   tracked-race), market + crypto ledgers. Never quote the catch-all % as an accuracy KPI
   (congestion gauge only). Harness/what-if reads carry their source (§15a evidence rule).
4. **Eight lenses** — engineer (defects, debt), auditor (integrity, non-circularity,
   held-out walls), attorney (claims, disclaimers, PII), banker (cost vs $700/mo cap),
   VC (moat: the accuracy ledger), advisor (priorities), board (open rulings ledger),
   fiduciary (is anything overstated to users?).
5. **Report** — ranked findings + recommendations, honest denominators, every figure
   computed this run (never propagated from a prior report). Commit to
   `audits/improve-system/`.

## Hard rules inherited
- §10a VERIFY-BEFORE-FIX: findings are hypotheses until traced to a line/data.
- Flag-never-force; deploy nothing from this skill.
- Deadlines currently on the shelf are listed in `audits/DEFERRED_ITEMS.md` — walk them
  every run and say plainly which fired, which are late, which are unreadable.
- **DOC-vs-CODE RECONCILIATION (board D7, Chairman-ruled 2026-09-15):** each run, sample
  "LIVE / shipped / ✅" claims in CLAUDE.md + SESSION_LOG and verify each against git
  (the shipping commit must exist and contain the claimed surface). Two false "recorded
  live" claims were caught in one 24h period (mobile SignalAnalysis never wired; "mobile
  has no crypto screen" 28 days stale) — the record must meet the same standard as the
  ledger. New rule: a "LIVE/shipped" sentence entering CLAUDE.md cites its commit hash.
