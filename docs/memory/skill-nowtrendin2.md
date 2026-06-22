---
name: skill-nowtrendin2
description: "The /nowtrendin2.0 session-startup skill — when to invoke it, what it does, and how auto-save works"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 365856a3-a15a-4e81-b551-17dcfef7ec5c
---

# /nowtrendin2.0 — Session Startup Skill

**Skill file:** `C:\Users\acinv\.claude\skills\nowtrendin2.0\SKILL.md`
**Invoke:** `/nowtrendin2.0` at the start of every Claude Code session

## What it does (in order)

1. **Memory load** — reads MEMORY.md + every linked memory file
2. **MD file sweep** — reads CLAUDE.md, ENGINE_AND_REPO_FREEZE.md, DATA_BUILDING_BLOCKS.md, AGENT_CHARTER.md, SESSION_LOG.md, COST_MODEL.md
3. **Git state check** — `git status` + `git log --oneline -15` + `git stash list` in v2.0 repo + gh-pages worktree
4. **Health checks** — Engine API, Backend API, GitHub Pages (web terminal), web-terminal build
5. **Skills inventory** — lists all 19 skills and confirms each SKILL.md exists
6. **Agents inventory** — lists Claude Code agent types + 7 fleet monitoring agents
7. **Session report** — compact status card: services up/down, last commit, open work, active rules

## Auto-save protocol

**GitHub IS the cloud backup.** Push frequently — do not batch to "later."
- After every completed task: stage by name → commit → `git push origin main`
- After web-terminal changes: also build + deploy to gh-pages
- After significant findings: update SESSION_LOG.md → push
- Before closing: `git status` to confirm nothing uncommitted, then push

## Why: the guarantee

If the local drive fails, all pushed code is safe on GitHub. Memory files are local
only — export key findings to SESSION_LOG.md or docs/SESSION_MEMORY_EXPORT.md
and push to origin to protect them.
