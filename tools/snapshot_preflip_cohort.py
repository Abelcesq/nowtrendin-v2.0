# -*- coding: utf-8 -*-
"""AB-ATTRIBUTION input preservation — Chairman ruling 2026-08-20, board round 4, item 1(a).

WHY THIS EXISTS. Five treatments landed on D on 2026-08-20 (sports_entity flip; 12 WordPress
lanes + the `_title_sig` unicode fix; Reddit retirement; two feed repoints; D_PLUMBING_V2 ON).
`velocity_scores` is retained 365 days, but `topic_signals`/`raw_signals` are pruned at
SIGNAL_RETENTION_DAYS (default 7) EVERY worker cycle. So the OUTPUTS survive and the INPUTS do
not: once the pre-flip window prunes, the 2026-08-20 treatments become permanently
unattributable, and the D kill criterion sealed for 2027-02-28 would be read against a
treatment nobody can decompose. The Economist's framing: a sealed criterion with an
unattributable treatment is a ceremony wearing the costume of an experiment.

Two seats (Economist P5, Forecaster) prescribed this independently and unprompted: export the
cohort to a file and the HARD data-expiry deadline becomes a SOFT scheduling deadline. Minutes
of work. Worth doing even if the A/B never runs, which is why it is preservation, not analysis.

THE FORECASTER'S DATE CORRECTION IS WHY THIS RUNS TODAY: the cohort arm needs signals collected
BEFORE the flip, and at 7-day retention those prune around 2026-08-26 — one day EARLIER than the
08-27 written in DEFERRED_ITEMS. The Statistician puts it more sharply still: for any pre/post
arm the effective deadline is NOW, and the window loses a day per day.

THE STATISTICIAN'S CAVEAT, RECORDED HERE SO THE ARTIFACT CARRIES IT (Chairman-ordered):
five treatments at one switch point give a design matrix of RANK 1. A single switch point
identifies the SUM, never the five parts. This snapshot buys OPTIONALITY and nothing more —
it does NOT make five treatments identifiable, and no post-hoc analysis recovers what the
design never encoded. The recompute arm identifies exactly ONE treatment (D_PLUMBING_V2), and
only as E[T5 | T1..T4 = ON] — a conditional effect, not a main effect, not extrapolable to the
pre-flip regime. Anyone reading this file later must not mistake it for an untangling.

This script is READ-ONLY against production. It writes files. It changes no score, no row, and
no served value.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# The flip. Everything strictly BEFORE this instant is the pre-treatment cohort.
FLIP_UTC = "2026-08-20T00:00:00"

# Tables whose rows are pruned by _prune_signal_tables() and therefore need preserving.
# (velocity_scores is NOT here — it is retained 365 days and is not at risk.)
TARGETS = [
    ("topic_signals", "extracted_at"),
    ("raw_signals", "collected_at"),
]


def _dsn() -> str:
    dsn = os.getenv("DATABASE_URL", "").strip()
    if not dsn:
        sys.exit("DATABASE_URL not set — pass it in the environment, never hard-code it here.")
    # Heroku hands out postgres://; psycopg2 wants postgresql://
    if dsn.startswith("postgres://"):
        dsn = "postgresql://" + dsn[len("postgres://"):]
    return dsn


def main() -> int:
    import psycopg2
    import psycopg2.extras

    outdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "audits", "ab-attribution")
    os.makedirs(outdir, exist_ok=True)

    conn = psycopg2.connect(_dsn(), connect_timeout=30)
    conn.set_session(readonly=True, autocommit=True)      # belt and braces: cannot write
    manifest = {
        "purpose": "AB-ATTRIBUTION pre-flip input preservation (board round 4, item 1a)",
        "flip_utc": FLIP_UTC,
        "taken_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "read_only": True,
        "caveat_rank1": ("Five treatments at one switch point = design matrix rank 1. This "
                         "snapshot preserves optionality only; it does NOT make the five "
                         "treatments identifiable. The recompute arm identifies exactly one "
                         "(D_PLUMBING_V2), conditionally on the other four being ON."),
        "tables": {},
    }

    for table, tscol in TARGETS:
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT COUNT(*) AS n, MIN({t}) AS oldest, MAX({t}) AS newest "
                    "FROM {tbl} WHERE {t} < %s".format(t=tscol, tbl=table), (FLIP_UTC,))
                head = cur.fetchone()
                n = int(head["n"] or 0)
                print(f"  {table}: {n} pre-flip rows "
                      f"({head['oldest']} .. {head['newest']})")

                path = os.path.join(outdir, f"preflip_{table}.jsonl")
                written = 0
                sha = hashlib.sha256()
                with open(path, "w", encoding="utf-8") as fh:
                    cur.itersize = 2000
                    cur.execute("SELECT * FROM {tbl} WHERE {t} < %s ORDER BY {t}".format(
                        tbl=table, t=tscol), (FLIP_UTC,))
                    for row in cur:
                        line = json.dumps(row, default=str, ensure_ascii=False,
                                          sort_keys=True)
                        fh.write(line + "\n")
                        sha.update(line.encode("utf-8"))
                        written += 1

                manifest["tables"][table] = {
                    "time_column": tscol,
                    "rows_counted": n,
                    "rows_written": written,
                    "oldest": str(head["oldest"]),
                    "newest": str(head["newest"]),
                    "file": os.path.basename(path),
                    "sha256_of_lines": sha.hexdigest(),
                }
                print(f"    -> {written} rows  sha256 {sha.hexdigest()[:16]}..")
        except Exception as exc:                          # a missing table is a fact, not a crash
            manifest["tables"][table] = {"error": str(exc)[:300]}
            print(f"  {table}: ERROR {str(exc)[:160]}")

    conn.close()
    mpath = os.path.join(outdir, "MANIFEST.json")
    with open(mpath, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    print(f"\nmanifest -> {mpath}")

    ok = any("rows_written" in v and v["rows_written"] > 0
             for v in manifest["tables"].values())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
