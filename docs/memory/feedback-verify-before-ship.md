---
name: feedback-verify-before-ship
description: "Always fix failures and confirm everything is actually pulling BEFORE any commit, deploy, or MD/checkpoint write"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 46ab8dd5-70c6-49dc-8816-b88ccdd2bb93
---

Before any **commit, deploy, or writing/updating an MD/checkpoint doc**: first diagnose and **fix the real failures**, then **confirm everything is actually pulling** — every data source/endpoint, every filter and button, against the live target (e.g. the v2 engine). Diagnose from real evidence (Heroku logs, raw responses), not assumptions. Never commit/deploy/document on top of a broken or unverified state.

**Why:** A green-looking checkpoint that documents broken endpoints (or commits over a real bug) is worse than no checkpoint — it launders failures into "done." The user caught a beneficiary-backtest crash + empty data that would have been frozen into an MD. Verification is the gate, not an afterthought.

**How to apply:** When a task ends in commit/deploy/MD, run the health/skill checks + hit each endpoint first; read logs to find the actual error (e.g. R14 memory, `column "stage" does not exist`); fix it and re-verify it pulls; distinguish a true regression from inherited baseline (compare against v1) and be explicit about which is which. Only then commit → push GitHub (source of truth) → deploy Heroku. See [[project-gradient-calibration]] and [[feedback-integrity-standard]].
