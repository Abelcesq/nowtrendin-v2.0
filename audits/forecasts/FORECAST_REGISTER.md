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

**Board conditions attached (pending Chairman ruling, recorded for the resolution file):** the
Operator's four rules (criterion firewall — sealed above; no commercial action may cite the
forecast date, and a deal discussion that invokes it disqualifies that deal from resolving the
forecast; base rate authored blind to pipeline — attested; conditional-form option declined by the
seat, noted); the Statistician's reflexivity log (any non-standard pricing/terms concession within
60 days of the horizon is logged alongside the resolution); disagreement on horizon (three seats
argued 12 months) is before the Chairman — any additional 12-month entry would be F6, appended,
with this entry standing as written.
