# Memory backup (cloud mirror)

These are **read-only cloud backups** of the local Claude Code memory at
`~/.claude/projects/C--Users-acinv-...-NowTrendin-v2-0/memory/`.

- **Source of truth = the local memory folder.** Claude reads/writes there during a
  session; this folder is a snapshot pushed to GitHub so the notes survive a drive loss
  or a move to another machine.
- `MEMORY.md` is the index (one line per memory). Each `*.md` is one durable fact.
- To restore on a new machine: copy these back into the local memory path above
  (the project-path hash must match), or just read them here.
- No secrets: API-key values never live in memory or in this repo — only key *names*
  (see `docs/ENV_REFERENCE.md`). Values live only in Heroku Config Vars / local `.env`.

_Last synced: 2026-06-22._
