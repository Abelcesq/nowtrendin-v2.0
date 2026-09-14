---
name: engine-recovery
description: Triage and recover the Gradient Score engine (Heroku app nowtrendin-v2-engine) when /scores or /topics serve 500s/503s, time out (H12), or the web terminal shows "Could not load signals". Signature table + safe recovery sequences from the 2026-07-06 read-path outage post-mortem. Use when the engine is down, slow, cold, or a prewarm/pool problem is suspected.
---

# /engine-recovery — read-path outage triage + safe recovery

Rebuilt 2026-09-14 from the 2026-07-06 post-mortem (SESSION_LOG "read-path outage
POST-MORTEM"); the laptop-local original was never committed. Engine app:
`nowtrendin-v2-engine` (`https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com`).
Deploys now also run from GitHub Actions (`.github/workflows/deploy-engine.yml`).

## PRIME DIRECTIVES (violating these EXTENDED the July outage)

1. **Read the error SIGNATURE before acting.** The outage had three phases with three
   different causes; the fix for one worsened another. Triage once, act once, hands off.
2. **Never probe a cold `/scores` or `/topics` repeatedly** — every probe launches another
   superset build (thundering herd). Poll **`/prewarm`** instead.
3. **`heroku pg:killall` ONLY with dynos scaled to 0.** Under live dynos it poisons every
   pooled connection (Charter G5: pool slots are unrecoverable by design).
4. No restart storms. One intervention, then watch `/prewarm`.
5. §10a applies: a signal that pattern-matches a known failure may have a different cause —
   confirm the signature before the fix.

## SIGNATURE TABLE

| Signature | Meaning | Action |
|---|---|---|
| `/scores` **fast 500**, logs show `PoolError` with server well under 20 conns | Poisoned CLIENT pool (dead conns handed out / orphaned slots) | db_compat self-heals since v206 (probe / discard / bounded direct / auto-rebuild after 90s). If persisting: scale-0 → `pg:killall` → scale-1 |
| Logs: `FATAL too many connections` (server at 20/20) | Saturated SERVER role cap — stranded slots | **scale web=0 → `heroku pg:killall` → scale web=1.** Never killall under live dynos |
| **H12 timeout / 503 "warming"** on `/topics`/`/scores`, engine otherwise up | Cold superset cache; single-flight returns honest 503 while ONE build runs | Wait and poll `/prewarm`. If `last_run` keeps advancing → transient, do nothing |
| `/prewarm` `last_run` **older than ~30 min** (>3× loop interval) | **WEDGED PREWARM** — warm loop blocked inside one build; every request cold-builds (self-sustaining herd) | One dyno restart (Heroku dashboard → More → Restart all dynos, or `heroku ps:restart`). Then poll `/prewarm` — it should warm 6/7+ feeds within minutes |
| Engine unreachable entirely | Dyno down / billing / Heroku incident | Heroku dashboard: dyno state, billing, status.heroku.com; also Postgres size vs plan (365-day retention risk, §13) |

## SAFE SEQUENCES

**Pool/server recovery (the only killall-safe order):**
`heroku ps:scale web=0 -a nowtrendin-v2-engine` → `heroku pg:killall -a nowtrendin-v2-engine`
→ `heroku ps:scale web=1 -a nowtrendin-v2-engine`

**Verify recovery:** poll `GET /prewarm` until `last_run` is fresh and feeds report warm;
then ONE `GET /health`, then ONE `/scores?limit=5`. Then `GET /monitor` for the agent
roll-up (includes `payload_contradiction_auditor` since schema 2026-08-24.1).

**Log it:** append what was seen + done to SESSION_LOG.md (signature, action, timestamps) —
the outage class is diagnosed from history.

## Known constants
- `PG_POOL_MAX=8` — deliberate headroom (engine ≤12 of the 20-conn cap). Do not raise.
- Prewarm is PULL-SYNCHRONIZED (`PREWARM_AFTER_PULL_S=60`) with the 25-min loop as TTL net;
  warms are overlap-guarded.
- Cloud claude.ai sessions CANNOT reach herokuapp.com (egress 403) — recovery needs the
  founder's browser/CLI or a GitHub Actions job.
