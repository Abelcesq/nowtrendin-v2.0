# 1.0 DATABASE — SIGNED DISPOSITION RECORD (datastore retirement)

**Date:** 2026-07-16 · **Authorized by:** founder (Chairman ruling on
BOARD_v1-db-disposition_2026-07-16.md: Option A unanimous with conditions) ·
**Executed by:** Claude (agent), non-destructive steps; the final add-on destroy is
reserved for the founder personally (flag-never-force).

## What was archived

| Field | Value |
|---|---|
| Source | Heroku app `nowtrendin` (frozen 1.0) · add-on `postgresql-shaped-41629` (DATABASE_URL, essential-2) |
| Original size | 10.77 GB · 28 tables · **13,043,952 rows** (exact, per-table manifest) |
| Backup | Heroku `b001`, captured 2026-07-16 03:06–03:08 UTC, logical pg_dump, 777.87 MB (93% compression) |
| Dump file | `v1db_b001_2026-07-16.dump` · **815,657,151 bytes** |
| SHA-256 | `5961B00139904B541A87EDB3582370715F3B23F49C7E237EC9943871C785D00D` |
| Copy 1 | `C:\Users\acinv\NowTrendin-archives\v1-db-2026-07-16\` (local disk) |
| Copy 2 | `C:\Users\acinv\OneDrive\NowTrendin-archives\v1-db-2026-07-16\` (OneDrive cloud-synced) |
| Manifest | `MANIFEST_v1db_2026-07-16.json` alongside both copies (exact per-table counts + date ranges) |

Both copies hash-identical. (Operational note: the FIRST hash of the OneDrive copy
mismatched — a read racing OneDrive's ingest; re-read matched. Always re-hash after sync
settles.)

## Restore verification (the board's load-bearing gate) — PASSED

- Scratch add-on `postgresql-adjacent-93291` (HEROKU_POSTGRESQL_BLACK, essential-2,
  ~$0.028/h) created on the frozen app; `b001` restored into it; **28/28 tables matched
  the pre-capture manifest EXACTLY (13,043,952 / 13,043,952 rows)**; scratch destroyed
  after verification. The original DATABASE_URL add-on was never touched.

## Why retired (context, one paragraph)

v2's Postgres was seeded from this database via pg:copy on 2026-06-15 and is the living
system of record. Board review (six independent memos, unanimous) rejected any import of
the post-split 1.0 tail (epoch-mixing + held-out-ledger denominator pollution) and ruled
for archive-then-retire. Mid-review reconciliation established that v2 retains ~28% of
the pre-split rows (the rest being the pre-split junk-explosion cohort shed by v2's
early purges) — making this dump the ONLY complete original of the 1.0 record; hence the
verified archive above. Full analysis: `audits/infra/V1_DB_ASSESSMENT_2026-07-16.md`
(incl. the ⚠ CORRECTION) and `audits/board/BOARD_v1-db-disposition_2026-07-16.md`.

## Standing rules (board conditions, in force)

1. **IMPORT BAN:** rows from this dump are never imported into the v2 database. Any
   forensic use or two-engine comparison runs on a TEMPORARY scratch restore
   (`heroku addons:create heroku-postgresql:essential-2` → `pg:backups:restore` from the
   dump via a re-upload, or `pg_restore` to any Postgres), then the scratch is destroyed.
2. **Epoch boundary:** v2 rows scored before 2026-06-15 are 1.0-engine-scored; never
   publish blended rates spanning the boundary unsegmented (metadata stamp pending).
3. The freeze-doc "pre-April-2026 data" lore is WRONG — this DB's data begins 2026-06-04.

## Final step — RESERVED FOR THE FOUNDER

All non-destructive conditions are met. To retire the original add-on (−$20/mo):

```
heroku addons:destroy postgresql-shaped-41629 -a nowtrendin --confirm nowtrendin
```

After destroying, update `COST_HEROKU_USD` 112 → 92 on the engine
(`heroku config:set COST_HEROKU_USD=92 -a nowtrendin-v2-engine`).

## Reusable retirement runbook (the Expansionist's DDQ asset)

1. Manifest: exact per-table `COUNT(*)` + key date ranges → JSON beside the dump.
2. `heroku pg:backups:capture -a <app>` → note backup id + reported sizes.
3. `heroku pg:backups:url <id>` → download; byte-size must match the reported size.
4. SHA-256; copy to a second failure domain; RE-HASH the second copy after sync settles.
5. Test-restore to a scratch add-on; every table count must match the manifest exactly;
   destroy the scratch.
6. Signed disposition record in the repo (this document's format).
7. Owner personally destroys the original add-on; update the cost model.
