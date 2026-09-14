---
name: scoring-assessor
description: NowTrendIn Scoring Assessor — the assessor/teacher over the monitoring fleet. Runs tools/scoring_assessor.py (read-only, endpoints-only) to grade source tracking, score movement, score accuracy, trend lifecycle, and outside-trending recall; then enforces the MANDATORY BOARD ANALYSIS GATE (independent critique + fresh outside-data cross-check) and the Chairman's final say before ANY finding teaches or is implemented. Use when the user says "run the assessor", "scoring assessment", "are we tracking accurately", "grade the system", "assessor snapshot", or on the weekly/monthly cadence.
---

# /scoring-assessor — Assessor/Teacher + the Board Analysis Gate

Born from the founder's four questions (are sources tracking accurately · how are
scores moving · how accurate are the scores · where is each trend now) and rebuilt to
the board specification (`audits/board/BOARD_scoring-assessor_2026-07-17.md`).
Concept source: `07 17 2026 - nowtrendin_scoring_assessor.py` (never run that file
live — superseded).

## Hard rules (board + Chairman, enforced)
1. **THE accuracy number is the held-out ledger** (`/accuracy/ledger` tracked-race,
   epoch-segmented). The assessor's percentages are INTERNAL-ONLY operational hygiene
   — never published externally (same rule as the catch-all %). The payment-portal
   gate is a LEDGER number, optionally AND-ed with assessor hygiene.
2. **Endpoints only, free sources only.** The tool reads deployed surfaces
   (/health/collectors, /scores, /accuracy/ledger, /aliases, /crypto) + free outside
   data (Wikimedia pageviews REST, Google daily-trending RSS). No SQL, no Apify, no
   paid pulls, never scheduled on deploy/boot.
3. **Findings DIAGNOSE — they never tune.** Task classes: OPERATIONAL (safe ops
   follow-ups) · SCORE_AFFECTING (requires founder sign-off + held-out backtest +
   serve_payload regeneration) · RULED (touches a Chairman ruling — blocked; the
   rulings registry inside the tool fails any solution that contradicts a ruling).
   Referee-derived findings carry `held_out_derived: true` — the referee is a
   validator, never a tuning signal. Watch the drift alarm: RISING engine–referee
   correlation across snapshots = converging on a lagging fame index — escalate.
4. **Series integrity:** `param_version` embeds the check-manifest hash. Never edit
   checks/thresholds casually — any change bumps the version and starts a new
   comparable series (state it in the report). New checks onboard as SHADOW first.

## Procedure

### 1. Run the tool (read-only)
```powershell
python "tools/scoring_assessor.py"            # live snapshot
python "tools/scoring_assessor.py" --demo     # synthetic, watermarked — mechanics test only
```
Output: `audits/assessor/ASSESSOR_<date>.json` + `.md` (append-only; COMMIT both —
the git history is the tamper-evident trend line). The snapshot is born
`status: UNVERIFIED_PENDING_BOARD_REVIEW`.

### 2. THE BOARD ANALYSIS GATE (MANDATORY — Chairman directive 2026-07-17)
Before ANY finding teaches Claude Code or is implemented:
- Convene the advisory board (/advisory-board pattern: six independent archetypes,
  identical evidence pack = the snapshot + the raw endpoint data it graded).
- The board MUST: (a) independently critique each finding (is the check itself sound?
  is the evidence real?), (b) CROSS-CHECK against freshly-obtained outside data —
  today's highly-trending items (Google trending RSS), market movers, crypto movers
  (/crypto change_7d_pct; FMP where keyed) — gathered AT REVIEW TIME, not reused from
  the snapshot, (c) verify or refute each work-queue item, (d) produce the VERIFIED
  work queue with per-item verdicts.
- Collate to `audits/board/BOARD_assessor-<date>.md`, commit.
### 3. CHAIRMAN RULING (final say — always)
Present the verified queue. Only items the Chairman approves proceed:
- OPERATIONAL items → normal fixes.
- SCORE_AFFECTING items → held-out backtest FIRST, then founder-approved deploy, then
  serve_payload regeneration (memory: serve-payload-cache-gotcha).
- RULED items → never implemented; rewrite or discard.
Update the snapshot JSON `status` → `BOARD_VERIFIED · CHAIRMAN_RULED <date>` and
re-commit. Log the ruling in SESSION_LOG.

## Cadence
- WEEKLY internal work-queue run (can pre-step the /improve-system audit).
- MONTHLY official snapshot = the trend-line point (both committed).
- Never auto-scheduled on deploy; never a hot engine endpoint.

## Focus (the founder's stated goal)
Accuracy of tracking data and accuracy of scoring methods, so every score can be
explained and supported. The assessor finds candidate gaps; the board verifies them
against the outside world; the Chairman decides; the ledger proves the outcome.
