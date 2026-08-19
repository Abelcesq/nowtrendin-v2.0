# FORECAST REGISTER — sealed, append-only

**Rules of this register** (pattern: `audits/index/INDEX_RULEBOOK_REGISTER.md`): entries are
APPEND-ONLY and never edited — a correction or re-forecast is a NEW superseding entry that cites
the old one; every entry is Brier-scored at its horizon; **unresolved at horizon RESOLVES NO** and
is scored as such (never "pending", never rolled forward silently); resolutions are recorded as new
entries citing the original. Entries are additionally sealed to the bitemporal PIT store
(`kind='forecast'`, server-stamped `knowable_at`, daily hash-chain seals) — the PIT row's
`row_sha256` is recorded here; the dual anchor makes silent edits detectable in both directions.
This register is INTERNAL ONLY: no entry or outcome appears in sales material in any form
(METER_DECISION_MINUTE_2026-08-18.md standing consequence 2); a business-milestone outcome confers
zero accuracy-claim rights and never counts toward or appears beside the ≥50-sealed-races citation
bar. Company-milestone forecasts (this file) are a register class permanently segregated from the
detection accuracy ledgers — no aggregate ever blends them.

---

## F1–F4 — Staged probabilities (Forecaster seat, sealed 2026-08-18 in `audits/board/BOARD_1M-month_2026-08-18.md`; migrated here verbatim as the register's founding entries — the board doc remains the original seal)

- **F1** — Stage 1 (licensable administrator posture complete): **P ≈ 75–85% by 2027-08-31.**
- **F2** — Stage 2 (first benchmark/monitoring subscription): **P ≈ 25–40% by 2028-08-31.**
- **F3** — Stage 3 (first issuer): **P ≈ 8–15% by 2029-08-31.**
- **F4** — Stage 4 ($12M/yr): **P ≈ 1–2%**; acquisition instead: **P ≈ 5–10%** (the fatter tail).
  Plan-of-record = Stages 1–2 only; F3/F4 live here as sealed, dated, Brier-scored forecasts,
  never silently rolled forward.

## F5 — First paying API/agent licensee under structure (f)
**Forecaster seat · sealed 2026-08-18 · pursuant to METER_DECISION_MINUTE_2026-08-18.md standing
consequence 3 · convening record: `audits/board/BOARD_worldcup-casestudy_2026-08-18.md`**

**(1) Resolution criterion — resolves YES if and only if ALL of the following are true on or
before the horizon date:**
- An **executed written license agreement** exists granting a counterparty access to NowTrendIn's
  API and/or proprietary agents operating over NowTrendIn's data and sealed record (the
  structure-(f) product);
- The counterparty is **arm's-length**: no family/personal relationship to the founder; no entity
  in which the founder, a board seat, or an advisor holds any economic interest; not procured by
  consideration flowing back from NowTrendIn;
- **Real consideration received: ≥ USD 5,000 in cumulative cash actually settled**
  (bank/processor record), not merely invoiced or pledged;
- **Explicitly NOT counting:** related parties; token/nominal payments below the $5,000 floor;
  unpaid or discounted-to-zero pilots and free trials; LOIs, MOUs, or "intent to license"; barter
  or in-kind exchange; grants, prizes, or credits; revenue-share agreements with $0 settled; and
  the existing Consumer/Business/Enterprise app-tier subscriptions (the app product, not a
  structure-(f) API/agent license).

**(2) Horizon:** **2028-08-31** (chosen to coincide with the sealed F2/Stage-2 horizon — the two
entries score on the same clock).

**(3) Base rate and provenance (stated honestly):** reference class = *single-founder, pre-revenue
data/analytics vendors reaching a first arm's-length paid contract within ~24 months of
go-to-market readiness*. No clean published dataset for this class exists — this is a
judgment-assembled anchor and is recorded as such (base-rate provenance grade C). Assembly:
alt-data first-contract latency typically 18–36 months from credible product; a large fraction
never convert absent a sales function; single-founder pushes low; the built-and-deployed sealed
record (PIT store + frozen-rule index) pushes up. Anchor band: **~20–35%**.

**(4) Sealed probability: P = 0.30** that criterion (1) resolves YES by 2028-08-31. Brier-scored
at horizon against the binary outcome. Reconciliation with F2: same underlying event class (first
arm's-length paid contract) under a different interface — 0.30 sits inside F2's sealed 25–40% band
by construction; placed mid, not high (+ broader buyer set under (f); − the agent-terminal product
does not yet exist as a sellable artifact; − no citable accuracy claim before the earliest
citation-bar pass ~Dec 2026; − no sales function). F3/F4 unaffected.

**(5) Resolution mechanics:** the Chairman presents the evidence — executed agreement + settlement
record ≥ floor + a one-line counterparty-independence attestation — at the first board convening
after the event (or after horizon +7 days); the Forecaster seat (or successor) scores it; the
Chairman signs the resolution minute. The Forecaster never resolves their own forecast. Evidence
document hashes (sha256) are recorded with the resolution; the resolution is a NEW PIT row
(`kind='forecast_resolution'`) citing this entry's `row_sha256`. Unresolved at horizon = NO.
Early YES resolution is permitted the moment all criterion elements are evidenced.

**PIT seal:** `kind='forecast'`, `item_key='FCAST-F5-first-paying-licensee-structure-f'`,
`event_date='2026-08-18'`, sealed via `POST /diag/pit/forecast` on 2026-08-18 (the sealed text =
this entry's sections (1)–(5) verbatim, 3,386 chars). `row_sha256`:
`9531d484d29840c26097104ee5f2ba9383696f38570a1bca41307934795f619c`

**Board conditions attached (recorded for the resolution file; ruled 2026-08-18 — "proceed
with all fixes"):** the
Operator's four rules (criterion firewall — sealed above; no commercial action may cite the
forecast date, and a deal discussion that invokes it disqualifies that deal from resolving the
forecast; base rate authored blind to pipeline — attested; conditional-form option declined by the
seat, noted); the Statistician's reflexivity log (any non-standard pricing/terms concession within
60 days of the horizon is logged alongside the resolution); disagreement on horizon (three seats
argued 12 months) is before the Chairman — any additional 12-month entry would be F6, appended,
with this entry standing as written.

---

## F6 — Point-probability convention for F1–F4 + resolution criteria (appended 2026-08-18; board-ordered at the updates-review convening, Chairman-approved "proceed with all fixes")

**Why (Challenger/Economist/Statistician, independently):** this register's own header
promises Brier scoring, and a band ("P ≈ 75–85%") is not Brier-scorable — at horizon someone
must pick a number, and picking it after the outcome is known is the post-hoc degree of
freedom the register exists to eliminate. Fixed NOW, while every horizon is distant and no
edge flatters. The original band entries stand as written (append-only); this entry fixes
their SCORING convention at the band midpoint:

- **F1 scores at P = 0.80** (band 75–85%) by 2027-08-31.
  *Resolution criterion (board-drafted to the F5 standard; the Forecaster seat may refine by
  superseding entry BEFORE 2027-06-30, never after):* resolves YES iff, by the horizon, the
  Stage-1 items that survived ruling (e) are ALL complete and board-attested: (b) PIT store
  built + live [done 2026-08-18], (c) frozen-rule unmarketed index calculating [done
  2026-08-18], conflicts/controls/complaints policy drafts existing as internal documents,
  the A4/A5 one-number work delivered, and the reflexivity pre-commitments recorded [done
  2026-08-18, register r1 RC1–RC4]. Self-graded items require the attestation minute of a
  board convening, not the founder's word alone.
- **F2 scores at P = 0.325** (band 25–40%) by 2028-08-31.
  *Criterion:* first paying benchmark/monitoring SUBSCRIPTION — arm's-length counterparty
  (F5's definition), ≥ USD 5,000 cumulative cash settled, for the benchmark/monitoring data
  product (as distinct from F5's structure-(f) API/agent license; if one contract satisfies
  both, both resolve YES on it — they are correlated by design, sharing the F2/F5 clock).
- **F3 scores at P = 0.115** (band 8–15%) by 2029-08-31.
  *Criterion:* first ISSUER executes a license to use an NTI index as the basis of a listed
  or offered product (fund, note, or certificate), arm's-length, real consideration.
- **F4 is SPLIT into two separately scorable entries** (a compound forecast cannot be
  Brier-scored as one number):
  - **F4a — Stage-4 revenue: P = 0.015** (band 1–2%): trailing-12-month revenue ≥ USD 12M
    by 2030-08-31, per books-and-records.
  - **F4b — acquisition: P = 0.075** (band 5–10%): a definitive agreement for the sale of
    substantially all of NowTrendIn's assets or equity executed by 2030-08-31.
  F4a and F4b may both resolve, either, or neither; they are scored independently.

All F6 conventions inherit the register's standing rules: unresolved at horizon = NO;
never rolled forward silently; internal-only; zero accuracy-claim rights. Reference-class
provenance for F1–F4 remains as sealed in the founding entries (grade C, judgment-assembled
— stated there, restated here).

## F5-a1 — Anchor annotation (appended 2026-08-18; closes the dual-anchor loop in both directions)

The F5 PIT row's `row_sha256` (recorded above) folds the server-stamped `knowable_at` and is
NOT offline-recomputable; the sealed payload's **`text_sha256`** IS recomputable from this
file alone. Recorded here after live verification against the sealed row:

- **Sealed text extraction recipe:** the register file as committed at `c1e75a4`, from the
  first byte of the line `## F5 — First paying API/agent licensee under structure (f)`
  through the byte immediately before the line beginning `**PIT seal:**`, trailing
  whitespace stripped; 3,386 characters as transmitted at seal time.
- **text_sha256:** `(recorded upon live verification — see the line appended below)`

Standing census rule (Statistician, anti-file-drawer): any `kind='forecast'` PIT row not
reflected in this register within 7 days of its `knowable_at` is VOID for all purposes;
the periodic anchor export (`tools/anchor_pit_seals.py` → `audits/pit-anchors/`) lists every
forecast row, so an unregistered seal is visible by inspection.
