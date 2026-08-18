# INDEX RULEBOOK + RULE REGISTER — NTI Same-Day Attention 50 (`NTI-SD50`)

**Status: INTERNAL + CONFIDENTIAL.** Chairman ruling (c), 2026-08-18
(`audits/buyer-diligence/METER_DECISION_MINUTE_2026-08-18.md`): a frozen,
register-appended rule set → daily **UNMARKETED** index calculation, accruing the
un-backfillable live record. Ruling (e) governs disclosure: the method is NOT
public; external materials may state only that a rules-frozen daily index is
calculated and sealed. This document is the register — **every rule variant ever
tried is an entry here; entries are append-only and never edited.**

The name encodes the PROVEN FLOOR, not the ambition (Challenger, convergence 5):
*Same-Day* Attention — the index measures attention as the system reads it today.
No before-arrival claim is embedded in the name, methodology, or record; if the
sealed epoch later validates before-arrival detection, that is a pricing upgrade,
never a restatement.

---

## Standing constraints (from the 2026-08-18 rulings; violating any = stop)

1. **No back-history, ever.** The first value is the first calculation day. A day
   the calculation did not run is ABSENT forever — never computed late, never
   interpolated, never backfilled. (Pre-sealed-epoch scores are hindsight-mutable
   — Statistician.)
2. **Rules freeze BEFORE the first published value.** This register entry r1 was
   committed before the first calculation ran (same commit gates the code).
3. **Unmarketed.** No publication, no marketing, no citation as progress. The
   calculation exists to accrue the record.
4. **Evidence separation (Statistician):** the accuracy ledgers and the index's
   own record are distinct evidence objects. The index never reads any ledger;
   ledger rates are never cited as the index's record, nor vice versa.
5. **Non-circularity:** the index reads Detection only. N (`nowtrendin_score`,
   platform tracking) is NEVER an input — folding on-platform demand into a
   published-value lineage is the circularity the integrity standard bans.
6. **The value is recorded solely to the bitemporal PIT store**
   (`kind='index_value'`, ruling (b)) — append-only, trigger-enforced, daily
   hash-chain-sealed. The record cannot be back-filled by construction.

---

## RULE REGISTER

### r1 — 2026-08-18 (INITIAL FREEZE; rules_version `idx-r1-2026-08-18`) — ACTIVE

**Identity.** Index key `NTI-SD50`; working name "NTI Same-Day Attention 50".
Level is a 0–100 gauge of the attention intensity of the current top attention
cohort. It is a MEASUREMENT of where attention is, per published-rule mechanics
(S&P/BUZZ posture) — not a prediction, not advice.

**R1 — Calculation instant.** Once per UTC day, at or after 01:00 UTC (after the
00:00 scoring slot). The actual instant `t_calc` is recorded in the sealed
payload. One value per UTC day, keyed `event_date = t_calc UTC date`.

**R2 — Universe.** Every topic with at least one `velocity_scores` row whose
`scored_at` lies in the 24h window ending at `t_calc`. For each topic, its
LATEST such row is the topic's reading.

**R3 — Inclusion embargo (reflexivity pre-commitment #1).** A topic is eligible
only if it ALSO has at least one `velocity_scores` row with
`scored_at ≤ t_calc − 48h` — no topic enters the index within its first two days
of existence in the system. Pre-committed at AUM=0, before any publication.

**R4 — Constituents.** The top **50** eligible topics by stored
`detection_score`, descending; ties broken by `topic_key` ascending
(deterministic). If fewer than 50 are eligible, all eligible topics constitute.
If fewer than **10** are eligible, the day's value is **ABSENT** — recorded
honestly with reason, never fabricated from a thin universe.

**R5 — Level.** The arithmetic mean of constituents' `detection_score`, rounded
to 2 decimal places. Equal weight; no chaining, no divisor, no smoothing.

**R6 — Reconstitution.** Full, daily, by these rules only. No discretion, no
manual inclusion/exclusion, no overrides.

**R7 — Inputs.** Stored `velocity_scores` rows exactly as scored (the engine's
primary served store). Detection only (constraint 5). No ledger reads
(constraint 4). No serve-time recalibration — stored values as written.

**R8 — Record.** Each day's result → PIT store `kind='index_value'`,
`item_key='NTI-SD50'`, `event_date = the UTC day`. The sealed payload carries:
`value`, `rules_version`, `t_calc`, `universe_count`, `eligible_count`,
`n_constituents`, and the full constituent list `[{k, d}]` — the value is
reproducible from its own sealed record. Absent days record
`{value: null, absent: true, reason}`.

**R9 — Missed days.** Absent forever (constraint 1). The seal chain shows the
gap; that honesty is the record's strength.

**Considered and rejected at r1 (registered per the every-variant rule):**
- *Top-20 instead of top-50* — thinner cohort, noisier level; rejected.
- *`overall_score` instead of `detection_score`* — blends confidence into an
  earliness gauge; Detection is the surface the product leads with; rejected.
- *Chained/divisor index (day-over-day linked)* — adds path-dependence and
  restatement surface with zero benefit while unmarketed; rejected for v0.
- *N-weighted or N-filtered constituents* — circular (constraint 5); rejected
  outright, permanently.
- *Late (retroactive) calculation of missed days from `scored_at`-bounded
  queries* — technically possible, forbidden by constraint 1; rejected.

### Reflexivity pre-commitments (convergence 6; written at AUM=0, while they cost nothing)

- **RC1 — Inclusion embargo:** R3 above (48h). Structural commitment.
- **RC2 — Immutable rebalance rules:** R6 above. Any rule change is a NEW
  register entry (r2, r3, …) with a new `rules_version`, effective only
  forward; while any product tracks the index, changes additionally require
  90 days' advance register entry before effect. Structural commitment.
- **RC3 — Capacity / AUM-share cap:** the methodology commits that
  index-linked products are capacity-capped. PLACEHOLDER PARAMETER — the
  numeric cap is frozen in a register entry before the first license is
  signed (a number chosen at AUM=0 with zero capacity data would be
  arbitrary; the COMMITMENT is structural, the number is pending).
- **RC4 — Self-influence monitor (pre-registered null, Operator seat):**
  H0: index constituency has no effect on a topic's subsequent attention.
  Design (pre-registered now, measurable only at AUM=0/unpublished): each
  day, pair constituents with the nearest-Detection non-constituents (ranks
  51–100); compare 7-day forward change in `detection_score` between the
  groups. While unpublished, any measured difference is selection dynamics,
  not influence — that distribution IS the null baseline. The monitor must be
  implemented and its baseline recorded BEFORE any publication of index
  values (trigger: add to `audits/DEFERRED_ITEMS.md` gate list). Read-only,
  held-out, never feeds any score.

---

*Register is append-only. Next entry: r2 (none planned).*
