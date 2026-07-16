# 1.0 DATABASE ASSESSMENT — transfer to 2.0? (founder research request, 2026-07-16)

**Answer: the transfer already happened.** v2's Postgres was created 2026-06-15 as a
`pg:copy` of the then-live 1.0 database (ENGINE_AND_REPO_FREEZE.md), and the live data
confirms it: v2's earliest velocity row is `2026-06-04T23:03:02` — one second after 1.0's
first row (`...:01`, the same inherited row set) — with **265,863 pre-split rows still
retained** in v2 under the 365-day rule. Everything durable that 1.0 ever produced up to
the split lives in v2 today. What accumulated in 1.0 AFTER the split (06-15 → 07-02, when
the app was disabled) is duplicative or integrity-hazardous to import. **Recommendation:
no transfer; archive a downloadable dump, then the standing −$20/mo delete can proceed.**

## What the 1.0 DB actually contains (read-only inspection, 2026-07-16)

Heroku app `nowtrendin` · essential-2 · **10.8 GB / 32 GB · 28 tables** · app at 0 dynos
since 2026-07-02, DB preserved.

| Table | Size | ~Rows | Date range |
|---|---|---|---|
| velocity_scores | **9,816 MB (91%)** | 9,718,671 | 2026-06-04 → 2026-07-02 |
| topic_signals | 378 MB | 759,880 | 06-25 → 07-02 (7-day retention) |
| anomaly_log | 276 MB | 1,102,159 | — |
| pull_history | 274 MB | 853,877 | — |
| risk_scores | 105 MB | 25,976 | — |
| raw_signals | 43 MB | 75,828 | 06-25 → 07-02 (7-day retention) |
| market_signal_history | 24 MB | 138,995 | — |
| registry/lifecycle/queries/archive/author | ~90 MB | ~330k | — |
| pending_detections | 440 kB | 1,841 | 06-02 → 07-02 |
| **accuracy_ledger** | 96 kB | **6 rows — ALL LAGGED** | 06-05 → 06-13 |

**Correction to the freeze-doc lore:** the "pre-April-2026 data" phrasing is wrong — the
1.0 DB contains NOTHING before 2026-06-04 (this add-on was created 2026-06-01; the 1.0
engine's git history starts 2026-05-28; any earlier prototype data lived elsewhere and is
not here). The 9.7M velocity rows are a 28-DAY June window, scored every 30 minutes by the
old engine with no effective pruning — bulk, not history.

## Why v2 already has everything worth having

Side-by-side (v2 read-only inspection, same day):

| | 1.0 (frozen) | v2 (live) |
|---|---|---|
| velocity_scores | 9.7M rows, 06-04 → 07-02 | 2.19M rows, **06-04** → now (365d retention) |
| pull_history | 853k rows | **1.18M rows, 06-07 → now** |
| pending_detections | 1,841 (06-02 → 07-02) | 1,684 (**06-02** → now, first-crossing enrolled) |
| accuracy_ledger | 6 rows (all LAGGED) | 90 resolved + full pipeline |
| author_history / score_archive / lifecycle | inherited at split | present from 06-04/06-05 |

## What is UNIQUE to 1.0, and why not to import it

Only the **06-15 → 07-02 tail** written by the frozen engine while v2 ran in parallel:
1. **Velocity rows for the same weeks v2 already scored itself** — a different engine +
   calibration epoch (weights/dual-pathway/INV-1 all evolved in v2). Mixing epochs breaks
   comparability/reproducibility (Foundational Principle 2) for zero analytical gain.
2. **1.0's pending detections** — enrolled by leaderboard-era logic v2 has since replaced
   with first-crossing (the structurally-LAGGED class). Importing them pollutes the honest
   ledger denominators (§14) with another engine's detections.
3. **One week of raw/topic signals** — v2 collected the same week itself.
4. **6 LAGGED ledger rows** — nothing.

Also physically: a full transfer cannot fit — 10.8 GB into v2's essential-1 (10 GB cap,
already 3.25 GB / 32.5% used). A selective transfer is possible schema-wise (the
velocity_scores schemas are byte-identical) but there is nothing left worth selecting.

## Recommendation (founder decision)

1. **Do NOT transfer** — nothing unique-and-valuable exists in 1.0 that v2 lacks.
2. **Before any deletion: capture AND DOWNLOAD a dump** (`heroku pg:backups:capture -a
   nowtrendin` then `pg:backups:url` → download; Heroku-side backups vanish with the
   add-on). The dump preserves the frozen June record for any future forensic backtest;
   restorable to a scratch DB at any time.
3. Then the standing cost-trim decision (archive+delete the essential-2, **−$20/mo**)
   can proceed whenever the founder rules. Note the 1.0 Heroku APP stays as-is — this is
   only about the database add-on; the frozen repo remains read-only reference.
