# INCIDENT — AB-ATTRIBUTION snapshot published to the PUBLIC repo (2026-08-24)

**Class:** PII exposure (policy §4 — executes immediately, flag-never-force does not apply).
**Status:** tip removal DONE this commit; history purge and fork remediation are FOUNDER
DECISIONS, listed below.

## What happened (verified from the git record, not inferred)

- `e4215d4` (2026-08-20, round-4 item 1a) preserved the pre-flip cohort and **promised in
  its own commit message**: "The 126MB payload is gitignored; the MANIFEST … is committed,
  so the snapshot's integrity is checkable **without the repo carrying the data**." Its
  `.gitignore` line was `audits/ab-attribution/*.jsonl`.
- The snapshot files on disk were **`.jsonl.gz`** — the pattern does not match them.
- `fe6712b` (2026-08-22, round 6) swept both `.gz` files into the commit **silently**: the
  commit message (which is itself about fixing a PII denial) never mentions them.
  `preflip_raw_signals.jsonl.gz` (4.6 MB) and `preflip_topic_signals.jsonl.gz` (10.2 MB)
  have been on the public tip since.
- The repo `Abelcesq/nowtrendin-v2.0` is **public** (verified via the GitHub API,
  `"visibility": "public"`) and has **1 fork**, which retains whatever history it was
  forked with.

## What is exposed

Measured from the committed artifact itself (round-6 rule: figures are computed, never
propagated): `raw_signals` carries **18,674 of 45,625 rows (40.9%) with a non-empty
`author` handle** (top platforms: gdelt, lemmy, broadcast, wordpress, bluesky, medium,
github, devto). The round-4 record's "30%" figure was an estimate; 40.9% is the measured
value. These are public bylines/handles (attribution metadata under policy §2), but the
round-4 decision — recorded in CLAUDE.md and SESSION_LOG — was explicitly to keep this
payload OFF public GitHub because the author column cannot be redacted (D's first-timer
ratio is computed from it).

## Actions taken this commit (within policy §4 authority)

1. `git rm --cached` on both `.gz` files — the public **tip** no longer serves them.
2. `.gitignore` pattern corrected to `audits/ab-attribution/*.jsonl*` so no compressed
   variant can ride along again.
3. This record; PII_POLICY cross-reference added.

Tip removal loses nothing unreproducible: the blobs remain in git history (recoverable
from any clone at `fe6712b`), and the founder's laptop copy plus the Drive manifest are
unchanged. The snapshot's second-location problem (round 4's open risk) is therefore
still OPEN — the laptop copy plus recoverable-from-history is not a durable second home.

## Founder decisions owed (not executed — outside this session's authority)

1. **History purge or accept**: removing the blobs from public history requires a rewrite
   (BFG/filter-repo) + force-push + a GitHub Support request to drop cached views — a
   destructive, coordination-heavy operation touching every clone. Alternatively, accept
   that history carries them and record that acceptance here.
2. **The fork**: one fork of the repo exists. If purging, the fork needs separate handling
   (owner contact or GitHub Support); if accepting, note that the fork is outside our
   control either way.
3. **Second location**: complete the original 1a closure — drag-drop the two `.gz` files
   from `audits/ab-attribution/` (laptop) to the Drive folder holding the manifest.

## Lesson (same class as the round-4 finding)

A gitignore promise is enforced by the PATTERN, not the intent — and a commit that stages
`-A` under a message about something else is how a documented decision reverses silently.
The corrected pattern plus this record is the guard; the claim register's
C-SNAPSHOT-NOT-IN-REPO (if adopted) should assert `git ls-files audits/ab-attribution/`
returns only MANIFEST.json.

---

## ADDENDUM 2026-09-16 — the fork is IDENTIFIED and founder-verified as an authorized user

Founder reviewed the live Forks page (Insights → Forks) on 2026-09-16 and reported:

- The single fork is **`josejlrdesigner-stack/nowtrendin-v2.0`** — the founder states this
  account is an **authorized user** (known to the project). Recorded as the founder's own
  verification, not independently confirmed from this session.
- **Timing observation (materially narrows the exposure, pending one check):** the Forks
  page shows the fork was **created ~3 months before 2026-09-16 (≈June 2026)** and
  **updated ~2 months before (≈July 2026)**. The PII blobs entered history at `fe6712b`
  (2026-08-22). A fork contains only the history it was created with / last synced to —
  so **if the fork's newest commit predates 2026-08-22, the fork does NOT contain the PII
  blobs at all**, and item 2 of the founder-decisions list collapses to a verification.
- **Verification step (founder browser, one minute):** open the fork's commit list and
  read the date of its newest commit. Before 2026-08-22 → record here that the fork is
  clean; on/after → the fork carries the blobs and the purge decision must include it.
- Unchanged either way: the blobs remain in THIS repo's public history until the item-1
  purge-or-accept decision; any NEW fork or clone taken today would carry them.

## ADDENDUM 2026-09-16 (b) — FOUNDER RULING: the fork is FORMALLY ACCEPTED as authorized

Founder ruling, 2026-09-16 (in-session, recorded verbatim in intent): *"go ahead and
formally accept the fork as authorized and prevent any further forks without my
authorization."*

1. **Item 2 of the founder-decisions list is CLOSED — ACCEPTED.** The single existing fork,
   `josejlrdesigner-stack/nowtrendin-v2.0`, is formally accepted as an AUTHORIZED fork held
   by an authorized user (founder-verified 2026-09-16). The optional newest-commit-date
   verification (does the fork predate `fe6712b`?) remains available but no longer gates
   anything.
2. **Standing policy adopted:** no further forks of this repository without the founder's
   authorization. Enforcement, honestly stated:
   - **Detection + alarm (in force on merge to main):** `.github/workflows/fork-watch.yml`
     — daily check of the live fork list against the authorized list (currently exactly
     `josejlrdesigner-stack`); any unauthorized fork fails the run, which emails the
     repository owner. Authorizing a future fork = adding the account to the workflow's
     list in a commit recording the founder's approval.
   - **Prevention limit (GitHub platform fact):** a PUBLIC repository cannot have forking
     disabled — GitHub offers no such setting. The ONLY true prevention is making the
     repository PRIVATE (founder browser: Settings → General → Danger Zone → Change
     visibility). Trade-offs recorded for that decision: private visibility instantly ends
     the public-clone exposure of the PII history (strengthens item 1), keeps GitHub
     Actions working, but GitHub Pages (the canonical web terminal at
     abelcesq.github.io/nowtrendin-v2.0) requires a paid GitHub plan on private repos —
     on the free plan the Pages site stops publishing (the Heroku terminal mirror
     `nowtrendin-terminal` is the ready fallback). The existing authorized fork, made
     while public, becomes an independent repository either way.
3. **NOT closed by this ruling:** item 1 (history purge vs written acceptance of the PII
   blobs in THIS repo's public history) and item 3 (Drive second copy). Accepting the fork
   is not acceptance of the public history; item 1 remains the founder's open decision.
