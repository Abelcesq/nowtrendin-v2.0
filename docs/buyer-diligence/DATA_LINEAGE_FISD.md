# NowTrendIn — Data Lineage Statement (FISD Alternative Data Council standard)
**Version 1.0 · 2026-08-09 · compiled from a full code-level inventory (engine `transfer/`, deployed) · Owner: Founder**

> FISD's lineage standard asks a vendor to document whether data was backfilled,
> whether missing values were interpolated, whether values were altered for schema
> alignment, and whether outliers were removed — with audit trails of when and by
> whom. This document answers those four questions for the NowTrendIn pipeline,
> precisely and including the exceptions. Per SEC v. App Annie, this document states
> only verified behavior; anything not re-verified at compile time is excluded.

## 0. Pipeline shape

collect (raw fetch) → ingestion gate (canonical dates; quarantine) → topic
extraction/normalization → admission gates (quality, corroboration) → score →
calibrate → store (365-day panel) → precompute serve payloads → serve — with a
HELD-OUT measurement layer (three accuracy ledgers + independent referees)
mechanically firewalled from scoring (AST-audited import registry: scoring modules
must never import ledger/referee modules).

## 1. Backfill — NO, with two disclosed, labeled exceptions

The system's default is explicitly anti-backfill: the accuracy-ledger intake "never
imputes or backfills what was not enrolled — we do not know what we did not see"
(code comment, enforced). The two exceptions, both from REAL published history,
both labeled at row level:
1. **Market baseline seeding** (manual, internal-key-gated): seeds two components'
   baselines from FINRA's published bi-monthly short-interest series and reported
   quarterly financials, recorded AT their historical settlement/period dates, with
   an empty fetch-time marking each row as a bare-date seed. Idempotent; never
   invents values.
2. **Topic-maturity backfill** (manual): derives maturity rows from existing
   lifecycle data; every row stamped `maturity_reason='backfill…'` with documented
   rollback.
Point-in-time capture discipline elsewhere is strict: ETF share observations are
append-only with capture instants; a competitor starting later cannot manufacture
our capture stamps.

## 2. Interpolation — NO (in production)

Missing values are declared absent, never estimated: an absent market component
records NOTHING (a fabricated 0 would poison the baseline); zero-variance/
degenerate baselines serve `score: null, absent: true` (the cold-start posture);
issuer-page parse failures are declared absence (fail-closed, incl. a
shares×NAV≈AUM identity check and a page-staleness guard); UI components render an
explicit "n/a", never NaN. The one interpolating estimator in the repo lives in a
held-out research-replay module that writes only its own results table and never
touches serve paths or ledgers.

## 3. Values altered for schema alignment — YES, format-level, disclosed, never guessed

- **Dates:** every date-semantic value normalizes to canonical `YYYY-MM-DD` through
  a single gate. Whole-string parsing only; ambiguous dates (e.g., both slash
  fields ≤12 and unequal) are REFUSED and quarantined for human review — never
  coerced. Unparseable non-empty values quarantine to a review queue; a human's
  resolution is learned as a reusable rule ("chosen by a human, never guessed").
- **Time:** the source's own time-of-day is kept in a separate column from our
  fetch time — additive, the source instant is preserved.
- **Topic text:** display text normalizes to a grouping key; the as-extracted text
  is retained. Morphological variant keys are folded onto one canonical key so a
  trend is scored once (the one retroactive key rewrite in the system; raw records
  untouched).
- **Units:** parser-level unit expansion only (currency-symbol/comma stripping,
  M/B suffix multiplication). Derived scores are clamped to 0–100.
- Source-of-record numerics (engagement counts, shares, NAV, AUM, prices) are
  stored as fetched.

## 4. Outlier handling — refused at admission or read time; kept, not deleted

**At admission:** a shared quality gate rejects fragments/boilerplate; a
corroboration floor requires ≥2 distinct sources for catch-all-classified topics
(with disclosed exemptions, incl. protection of anything already tracked in a
ledger); non-reputable sources are admitted at a ~1% quarantine weight and promoted
only on corroboration by a vetted source within 72h; weak flows never enroll in the
market/crypto ledgers (pre-declared intensity floors).
**At read/vote time (rows kept):** ETF discontinuity guard (>20%/day = corporate-
action-scale step, refuses to vote), staleness guard (>5 trading-day gap), splice
rule (no delta across a data-source seam — the new source re-earns its history),
move thresholds on ledger resolutions (5% equity / 8% crypto) so price noise never
scores as a hit, and a same-surge matching floor with an asymmetric lead window so
wrong-surge matches never enter verdicts.
**Retroactive removals that DO exist (complete list, none quality-of-score
judgments):** age-based retention prunes (the scored panel keeps 365 days —
count-based pruning is refused IN CODE with a hard SystemExit citing the governing
rule); a per-cycle junk-key prune limited to non-canonical/fragment score rows;
unconfirmed anomaly-log rows at 30 days (confirmed rows are kept — they are the
track record); and display-cache rebuilds. Deleting scored history on quality
judgments is expressly forbidden and mechanically refused.

## 5. Audit trails — when, and by whom

- **When:** every mutation carries a UTC stamp (collected/scored/captured/
  validated/resolved). Measurement definitions are frozen into version stamps that
  ride with the data: the ledger's parameter version carries every
  measurement-defining constant (patience window, lead window, match floor,
  pre-broken grace); the referee's surge parameters are version-frozen; data-source
  lineage is stamped per row (`src`, series epochs, pre-declared corporate-action
  epochs).
- **By whom:** single-operator company; machine writers stamp their identity
  (`provider`, `src`, `source`); human decisions exist only at named choke points —
  the date-quarantine resolution endpoint, founder-ruled flags, and board-ruled
  changes documented in committed board memos with commit-hook-enforced markers.
  Stated plainly for diligence: DB rows do not carry a per-user identity column;
  attribution of human decisions rests on the git history and the board record.
- **Intake honesty:** ledger enrollment writes an intake log on EVERY exit path
  (including failures), and operational errors fail CLOSED with a labeled
  relaxation — "fail-labelled, never fail-open-and-silent." Enrollment
  completeness is itself published (69.6% as of 2026-08-09) rather than hidden.
- **Monitoring writers** are guarded against writing garbage: the catch-all trend
  auditor refuses to record readings while its classifier maps are cold, so a
  restart artifact never poisons the recorded trajectory.

## 6. Quarantine / human-review loop (the flag-never-force mechanism)

Unparseable date → quarantine row (raw value + machine-proposed candidates) →
surfaced by the nightly audit → human resolves via an endpoint → the resolution is
recorded (who-chose-what, when) and learned as a rule that auto-applies to
identical future inputs. Nothing changes until a human posts.

## 7. Known limitations (stated, per the accuracy-of-description rule)

- The unverified→mainstream tier promotion (a 72h-window annotation upgrade) lacks
  a durable per-row promotion audit column (log-level only today).
- The per-cycle junk-key prune keeps no row-level tombstone register.
- Two backfill classes exist (disclosed above); everything else is live-capture.
- Human-actor attribution is via git/board records, not DB columns.
