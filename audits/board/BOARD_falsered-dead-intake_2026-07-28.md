# ADVISORY BOARD — THE FALSE-RED CLASS + THE DEAD LEDGER INTAKE
**Convened:** 2026-07-28 · **Six archetypes, independent** · engine **v296**
**Outcome:** Finding B ruled **BLOCKING** (5 of 6 say P0). Finding A's *finding* upheld, its
*proposed remedy* **rejected as scoped**. Three corrections to the pack, and one defect nobody
had seen.

---

## 0. CORRECTIONS TO THE PACK (all re-verified by the Chairman's agent)

| Pack claim | Truth |
|---|---|
| "fresh crossers are **permanently lost**" | **Overstated.** Eligibility is `first_seen >= now−14d`, so an outage shorter than 14 days loses only topics that decay below the detection floor before intake resumes — *fast-decaying spikes*, not crossers generally. With `LEDGER_ENROLL_NEW_CAP=3`, the verified loss ceiling is **≤9 rows against a pool of 1098** (Challenger). |
| "`topic_maturity` is empty → delete §14's claim" | **Premature.** The table has **live writers** (`calibration_engine.py:1249`, `signal_calibration_integration.py:576`). An empty table with active writers is a **read/join or writer-firing defect**, not a missing producer. Verify the read before amending canon (Expansionist). |
| "both rows read DOWN because they haven't run since the deploy" | **Unverified as stated, and I could not have known it from the pack.** `FINNHUB_API_KEY` **is** set (len 40), and a risk cycle ran ~69m ago — but on **v295**, under the *old* single-row name. The new names genuinely have no row yet. The explanation survives only once the deploy boundary is accounted for; I asserted it without checking. |

## 1. THE DEFECT NOBODY HAD SEEN (Challenger)

`get_health_report` collapses **four** states, not three — and the fourth is the dangerous one:

```python
if not rec or not rec.get("last_success_at"):
    status = "DOWN", "never recorded a successful run"
elif fails >= 3: ...        # <-- UNREACHABLE for a source that never succeeded
```

**A collector that has run many times and failed every time can never reach the `fails >= 3`
escalation**, because the NULL-success branch short-circuits first. It reports *"never recorded
a successful run"* — which is **factually false**; it ran, and failed, repeatedly. That is
`finnhub_congress` exactly: 403 ×4 per cycle, `consecutive_failures` climbing, permanently
un-escalatable. **Verified in code.**

**Consequence for the proposed fix:** naive UNKNOWN (`no last_success_at → UNKNOWN`) would
convert today's false RED into a **permanent false GREY on the one row that is genuinely dead**.
The remedy must key on **run evidence**, never on success alone.

## 2. FINDING B — RULINGS

**Unanimous: the status quo is rejected.** Five of six rule P0/BLOCKING; the Challenger rules P1
on magnitude but concurs on every remedy.

**Verified mechanics:**
- The error text comes from the **outer** handler — reachable only if the **fallback also
  raised**. *Both arms died.* The fail-open retry keeps both full aggregates and merely drops a
  LEFT JOIN, so it is **doomed by construction** (Executioner).
- Each dead cycle burns **~10 minutes** of a pooled Postgres connection (2 × 300 s
  `statement_timeout`) starting the instant `score_all_topics()` returns — peak write pressure,
  `PG_POOL_MAX=8`. **This is the 2026-07-06 convoy precondition: a read-path risk, not only a
  measurement loss.**
- The `MIN(scored_at)` aggregate (`fs`) is an INNER JOIN to a subquery on the *same* table —
  **every row matches; it restricts nothing.** It exists to fill a fallback that
  `_update_topic_lifecycle` already closes in the same transaction. **Pure waste** (Executioner).
- `enroll_ab_log` is written **inside** the `try`, so failed cycles write **no row at all** — the
  D9 experiment's audit log has no denominator, and arms are assigned by deterministic
  wall-clock parity, not randomisation. **Suspend D9** (Challenger).

**A genuine disagreement, unresolved, and worth preserving:**
- **Economist:** the outage preferentially deletes *surge-cycle* first-crossers — the fast, fat-tail
  detections the thesis lives on. The right tail is deleted → published rates are **deflated**.
- **Challenger:** the permanently-lost class is *fast-decaying spikes*, which would never have
  confirmed → their loss **flatters** the rates.
Both are verified reasoning over the same mechanism, differing on which subpopulation dominates.
**Neither can be settled without the intake log — which is itself the first deliverable.**

**Both agree on the disclosure instrument, and that it is NOT an era label:** the data is clean;
the *intake* stopped. The remedy is a **cycle-level attempt log** (the ledger's shutter log) plus
an `enrollmentCompleteness` series published beside every rate — Friedman & Schwartz's rule that
a long series is evidence only if collection was consistent, and *labelled* where it was not.
**Never impute or backfill what was not enrolled** (Guardian).

## 3. FINDING A — RULINGS

Finding upheld; remedy rejected as scoped. Converged state model — **keyed on run evidence**:
- **UNKNOWN** — registered, `last_run_at` NULL, and within `2 × max_gap` of a persisted
  `registered_at`. Never `critical`, never counted in `down`. **Must expire** → DOWN.
- **DOWN** — grace expired, *or* `last_run_at` set with zero successes ("ran N times, 0
  successes"). **UNKNOWN must be unreachable once `last_run_at` is non-null** (Challenger).
- **DISABLED** — intentionally off. Live today `reddit` reads `DEGRADED — 0 signals`, a standing
  false amber (Executioner, Expansionist).
- Blast radius today is **bounded**: both rows are `critical: false`, `critical_problems: []`,
  `trust: true`. The class is the risk, not today's reading — the pack overstated "manufactures
  alarms" (Challenger, Economist, Guardian all noted this independently).

## 4. THE PRINCIPLE, AND THE CULTURE FINDING

**Guardian's proposed CLAUDE.md §18 — NO NULL COLLISION (hard rule):** *any output that can mean
both "nothing to report" and "we failed to look" MUST carry a separate outcome discriminator
written on the failure path, never inferred from the value. The failure path must WRITE.*
This unifies all four defects: `recorded 0`, `DOWN`, a rate over surviving rows, and an audit log
written only on the happy path.

**Outsider — culture finding recorded, precisely scoped:** *"a control is called done when the
code is written, not when its output has been watched on live data."* Not an honesty problem —
every one of these was **found by our own verification and self-reported**. The closing rule:
> **No control is finished until someone has forced it to fail on purpose and seen it correctly
> report the failure. Green on a working system proves nothing.**

**Expansionist — the class, not the instance:** ~15 sites share the O(N-history) shape
(`INNER JOIN (SELECT key, MAX(ts) … GROUP BY key)`), **two on the serve path**. `gad.py:7821`
documents this class being recognised and fixed **at one call site on 2026-07-15** — thirteen
days later it took down the moat's intake somewhere else. *"A class fixed at one instance is not
fixed."* Retention went 90→365d and we have paid only **~9%** of that growth; B fired at 9%.
Proposed: a `topic_current` head table retiring the class across all sites.

## 5. S3 — THE CONVERGED SCOPE (order is near-unanimous: INSTRUMENT BEFORE REMEDIATE)

1. **S3-a — `ledger_intake_log` + distinct outcomes.** One row per cycle: `ok | empty | failed`,
   with candidates/enrolled/duration/error_class. Written in a **`finally`, on its OWN fresh
   connection** (a timed-out PG transaction is aborted — reusing it loses the audit write).
   Kill the unconditional "recorded N" print. `empty` is written **only** when the query
   succeeded and returned zero. Move `enroll_ab_log` into the same `finally`.
2. **S3-b — fail CLOSED.** Classify the exception: operational (timeout/pool) → enroll nothing,
   record the gap, **no same-shape retry**. Only a genuine missing-table error may fail open,
   once, **stamped** on the row (fail-*labelled*, not fail-open).
3. **S3-c — alarm.** `monitoring_agents` reads the intake log: last cycle `failed`, or ≥2 of last
   4 → critical; newest `cycle_at` older than 2 × `COLLECT_INTERVAL_MIN` → warn. A legitimately
   empty cycle is silent *because success and emptiness are now separate fields*.
4. **S3-d — collector_health state model** (§1/§3): `registered_at`, time-boxed UNKNOWN, the
   never-succeeded → DOWN fix, DISABLED for intentionally-off sources.
5. **S3-e — `enrollmentCompleteness` on `/accuracy/ledger`**, rendered beside every rate.
6. **DEFERRED to S4 with a written gate:** the query rewrite (recency off `topic_lifecycle`, drop
   the `MIN()` scan), gated on proving `first_detected_at ≡ MIN(scored_at)` on the live
   population — because that value becomes `detection_date`. Ship behind `LEDGER_ENROLL_FAST`.
   **Also S4:** `topic_current` head table; the `topic_maturity` read investigation; D9 restart
   with real randomisation. **NOT in S3:** populating `topic_maturity`, any stored-row change,
   any reweighting.

---
*Six memos, faithfully collated; full texts in the session record. Corrections in §0 and the
defect in §1 were independently re-verified before adoption.*
