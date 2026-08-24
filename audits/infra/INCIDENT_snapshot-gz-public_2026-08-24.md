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
