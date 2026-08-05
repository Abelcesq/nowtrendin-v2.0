# FLOW LEDGER PRE-REGISTRATION — AMENDMENT A1
**Date:** 2026-08-04 PT (America/Los_Angeles) · **Prereg:** `2d65eac796c28476` (active, unchanged)
**Status at adoption: PRE-ENROLLMENT — FLOW_ENROLL=0, zero treated rows, zero control rows,
zero ledger rows.** An amendment before any subject is enrolled is a legitimate protocol
amendment; the same change after first enrollment would be a cohort break requiring a new SHA.

**Authority:** Chairman ruling on the 2026-08-04 board review
(`BOARD_status-review_2026-08-04.md`), adopting the Challenger's F1 condition (b) and the
identity-fragmentation fix.

## A1.1 — Qualification window floor: `window_start >= panel_start`

`qualify_clusters` now REFUSES any qualification window that extends before the insider
panel's first coverage watermark (`flow_enrollment.qualification_floor`). Rationale (the
Challenger): a 10-session window evaluated over a 3-day panel is left-censored — controls
"with no qualifying disclosure of their own in the window" would pass on unverifiable
cleanliness, and first-era rows would be measured under different information conditions
than all later rows under the same prereg SHA.

Effect: FLOW_ENROLL may be flipped at any time; enrollment mechanically begins only when the
trailing window is fully inside the panel's lifetime (panel first ingest 2026-08-01 PT →
first spannable window ≈ 2026-08-14/15). The floor is code, surfaced in `/flow/status`
(`qualification_floor`), not a human reminder.

## A1.2 — Distinct-buyer counting on context-confirmed canonical identities

The registered trigger (≥3 DISTINCT open-market buyers / 10 trading days) is unchanged; what
"distinct" measures is corrected. `actor_id()` hashes the exact name string, so formatting
variants of one person ("John Smith" / "John A. Smith" / "SMITH JOHN A") counted as separate
buyers — noise inflating the enrollment trigger itself (the Challenger's U1 attack).

Counting now runs over canonical identities (`insider_flow.identity_map`):
- variants merge ONLY when the normalized name matches AND on the SAME ticker AND role
  categories are compatible (equal, or one side unclassified);
- same-name groups with CONFLICTING roles (director vs officer — the father/son signature)
  are NEVER auto-merged; they are flagged for human review (flag-never-force) by the new
  read-only **similar_fragmentation agent** (`/monitor` run_all);
- merged identities aggregate — one buyer, the sum of their purchases;
- the append-only panel is untouched: resolution applies at COUNTING time only.

Direction of the correction is strictly conservative for enrollment (canonical count ≤ raw
count; it can only PREVENT fabricated clusters, never create one).

## A1.3 — Jurisdiction stamped from row one

`insider_events`, `flow_pending_detections`, and `flow_ledger` carry `jurisdiction`
(default `'US'`; the live feed is SEC Form 4). Board 2026-08-04 (Expansionist): an
append-only panel must never need this migration after a year of accrual. Additive,
display/provenance only; no scoring or enrollment semantics change.

## A1.4 — Timestamp convention (Chairman ruling, same session)

Narrative documents, board records, and code comments stamp **Pacific Time
(America/Los_Angeles)**, with UTC in parentheses where minute precision matters. The §14
canonical data model is UNCHANGED: all stored data timestamps (`signal_date`, `signal_time`,
`ingested_at`, coverage watermarks) remain UTC — the canon governs data, this convention
governs prose. The 08-04-vs-08-05 discrepancy four archetypes flagged was exactly this
boundary left implicit; it is now explicit.
