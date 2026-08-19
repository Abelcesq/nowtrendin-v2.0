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

### F5-a1 VERIFICATION RECORD (appended 2026-08-19 UTC / 2026-08-18 PT — machine-verified, both directions)

- **Sealed `text_sha256`:** `465d9f3d7c5fb848968d5eabb0a0868e18683065559f730a9e3d4494250e4fb2`
  (fetched from the live PIT row via `/diag/pit/anchors`).
- **Recomputed independently from git and MATCHED exactly:** the register file's bytes at
  commit `c1e75a4`, **decoded as cp1252** (the PowerShell 5.1 `Get-Content -Raw` default
  used at seal time on a BOM-less UTF-8 file — recorded honestly: multibyte characters in
  the sealed text are their cp1252 mojibake forms), substring from `'## F5'` to the byte
  before `'**PIT seal:**'`, trailing whitespace stripped, encoded UTF-8 → sha256. 3,386
  characters. Any future dispute recomputes by this exact recipe.
- The CONTENT-canonical text remains this file's F5 sections (1)–(5) as committed at
  `c1e75a4` (byte-identical under utf-8 decode, 3,353 chars, sha256
  `cca4b7e9338ba443560f6f1fdad93886aceb096c6c684b7de0b85e2aa91020c0` — recorded so both
  readings are pinned). Future seals use `tools`-scripted UTF-8 extraction so text and
  seal encodings coincide.
- **Numbering note:** F5's board-conditions paragraph reserved "F6" for a possible
  12-month-horizon variant; F6 was subsequently used for the point-convention entry
  above. Any Chairman-ordered 12-month first-licensee entry is therefore **F7**.

**F6 PIT seal:** `item_key='FCAST-F6-point-convention-F1-F4'`, sealed 2026-08-19 UTC via
`POST /diag/pit/forecast` — extraction: this file UTF-8, from `'## F6'` to the byte before
`'## F5-a1'`, trailing whitespace stripped, 2,876 chars;
`text_sha256 881becd6b17707ea0d075f4bc9699aa82b1608fc272743727d20e932dd8c17cc`;
`row_sha256 3e755832de65ce419ddaad8e8033ce20ba3c9a7fc79efaf95cb3573564233a19`.

---

## F7 — QUARTERLY BENCHMARK PROTOCOL + Q1 sealed set (Chairman ruling 2026-08-18: "we need 3 month (quarterly) benchmarks — 2 years or even 12 months is too far out")

**The protocol (standing, from this entry forward).** Every quarter this register seals a
small set of benchmarks that are (a) objectively resolvable from our own instruments,
(b) about the ACCURACY MACHINERY rather than commercial outcomes, and (c) short enough that
being wrong is discovered while it still costs little. At each quarter end we do two things
in one sitting: **score the expiring set with Brier** (all of it, survivors and misses alike)
and **seal the next set**. A benchmark unresolved at its horizon resolves NO, per the
register's standing rule. This is the calibration engine for the founder's standing
instruction that we must *continuously* test whether the system tracks human attention —
four scored checkpoints a year instead of one distant bet.

**Why these particular numbers.** They are the measurable gates of the Chairman's Benchmark
Register (P-1…P-6) plus the two integrity streaks the moat now rests on. Each is stated with
its live baseline as of the seal, so the movement — not the level — is what gets scored.

### Q1 — horizon **2026-11-30** (all probabilities sealed 2026-08-19 UTC; base-rate provenance grade C, judgment-assembled from the live baselines shown)

| # | Benchmark (resolves YES iff…) | Live baseline at seal | Sealed P |
|---|---|---|---|
| **B1** | **≥30 SEALED-EPOCH resolved races** in the attention ledger (epoch began 2026-08-17; only sealed-epoch rows are citable) | ~0 sealed-epoch resolved; 125 resolved lifetime; 1,320 pending; enrollment ~12/day | **0.55** |
| **B2** | **Index determination streak unbroken** — every UTC day from 2026-08-18 through the horizon carries either a sealed value or an honest ABSENT, with no missing day | 2 days (75.45, 76.50), daemon live, missed days are ABSENT forever by rule | **0.85** |
| **B3** | **A2.4 flow re-arm reaches 5/2/3** — ≥5 material in-band issuer-source comparisons, ≥2 funds, ≥3 trading days, zero bad | 1 / 1 / 1, open_bad 0, first issuer PASS landed within a day of A2.2 | **0.55** |
| **B4** | **Enrollment completeness ≥95%** measured over the quarter (failed enrollment cycles silently drop first-crossing candidates, which then age out at 14 days — a hole in the ledger's own denominator) | **83.5%** (17 of last 103 cycles FAILED, last 2026-08-01) | **0.70** |
| **B5** | **D-early inversion corrected** — median Dark Matter at first sighting is HIGHER for LED winners than for pre-broken rows | inverted: LED median 0.0 vs pre-broken 14.3 | **0.20** |
| **B6** | **PIT chain clean + externally anchored ≥90 distinct days** — `verify()` passes at horizon AND the git anchor file carries ≥90 day-seal heads | chain verifies; 1 seal anchored (day 1 of the anchor era) | **0.88** |
| **B7** | **≥1 LED win independently corroborated** by the Wikipedia referee (today every win is honestly "unchecked") | ledCorroborated 0, ledUnchecked ≥1 | **0.45** |

**Explicitly NOT a Q1 benchmark:** P-1 (beating the null). The tracked-race rate sits below
its naive null at p≈0.001 on a pre-sealed-epoch cohort, and the sealed-epoch cohort will not
reach the ≥120-race sample inside one quarter. Sealing a probability on it now would invite
reading a small-sample swing as progress. It re-enters as a benchmark the first quarter B1's
successor puts ≥120 sealed-epoch races in reach — and until then no accuracy claim leaves the
building, per the citation bar.

**Scoring note (honesty about correlation):** B1, B4 and B7 are not independent — a fixed
enrollment pipeline lifts all three. They are scored separately anyway, and the correlation
is recorded here so a "3 of 7 hit" is never read as three independent successes.

**Resolution:** on 2026-11-30 the Forecaster seat scores each benchmark from the live
instruments (ledger endpoint, `/diag/index`, `/diag/etf-reconcile`, `/diag/pit`, the anchor
file), records the Brier score for the set, and seals Q2. The Chairman signs the scoring
minute. No benchmark may be revised, dropped, or reinterpreted after this seal; a benchmark
discovered to be badly posed is scored as sealed and *replaced* in the next quarter, never
retroactively amended.

**F7 PIT seal:** item_key=`FCAST-F7-quarterly-benchmarks-Q1-2026-11-30`, sealed 2026-08-19 UTC.
Extraction: this file UTF-8, from `## F7` to end-of-file at seal time, trailing whitespace
stripped, 4275 chars; `text_sha256 9fbd47cbc86d2f631fae206a278c20d095321ef21608b49fe41fe77ac58358b9`;
`row_sha256 c298322ba49f5f6d72d595c49c05f795ca1081d1d21eb0619d2b0d268e1b6c37`.
