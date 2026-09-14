"""Release-phase + manual maintenance: prune anomaly_log, precompute serve_payloads.

Ruling 2c(a), board round 4: this runs in the Heroku RELEASE PHASE (see Procfile),
so every deploy rebuilds the payload cache with the NEW code before the new dynos
serve — the deploy-version window (a binary serving blobs built by another binary)
is closed at the process level, and the schema stamp (2c(c)) closes it at the
data level for anything this phase misses.

The Executioner's condition (2c(b)) is honoured in the function itself:
_precompute_serve_payloads is non-destructive — new payloads are built in memory
first and swapped in one transaction, so a mid-release failure leaves yesterday's
payloads serving instead of a NULL wasteland (the 2026-07-06 outage class).

RELEASE-SAFE BY CONTRACT: this script always exits 0. A failed maintenance pass
must not block the deploy — the in-cycle worker precompute self-heals within one
cycle, and blocking a deploy on cache warmth would turn a cache into a
single point of failure. Failures are printed loudly for the release log.

Manual run: heroku run python maint_precompute.py -a nowtrendin-v2-engine
"""
import os
import sys
import traceback


def _build_diagnostics(g) -> None:
    """Stage-2 evidence for the 2026-09-14 statement-timeout outage (§10a: measure
    before rewriting). Prints, into the RELEASE LOG the deploy workflow captures:
    table health (dead tuples, autovacuum age, on-disk size — the serve_payload
    churn-bloat hypothesis), the indexes that actually exist in prod, the planner's
    PLAN (no ANALYZE — never runs the slow query here) for the classic scores
    build, and the resource settings this Postgres plan grants. Read-only; PG-only;
    a few ms. The same query ran in 1.1s on a clean local PG16 at 2.4M rows, so
    these numbers are what separates prod's ~11 min from that."""
    import db_compat
    if not getattr(db_compat, "USE_PG", False):
        print("[diag] not PG — skipped")
        return
    conn = g.get_db(g.DB_PATH)
    try:
        print("== [diag] table health (pg_stat_user_tables) ==")
        for r in conn.execute("""
            SELECT relname, n_live_tup, n_dead_tup, last_autovacuum, last_vacuum,
                   pg_size_pretty(pg_total_relation_size(relid)) AS total_size
            FROM pg_stat_user_tables
            WHERE relname IN ('velocity_scores','topic_lifecycle','topic_signals',
                              'raw_signals','topic_registry')
            ORDER BY relname""").fetchall():
            print("   ", dict(r))
        print("== [diag] velocity_scores indexes ==")
        for r in conn.execute(
                "SELECT indexname FROM pg_indexes WHERE tablename='velocity_scores'").fetchall():
            print("   ", dict(r))
        print("== [diag] settings ==")
        for r in conn.execute("""
            SELECT name, setting FROM pg_settings
            WHERE name IN ('shared_buffers','work_mem','max_parallel_workers_per_gather',
                           'autovacuum_vacuum_scale_factor','statement_timeout')""").fetchall():
            print("   ", dict(r))
        print("== [diag] classic scores-build PLAN (no execution) ==")
        for r in conn.execute("""
            EXPLAIN
            SELECT v.*, COALESCE(lc.first_detected_at, agg.first_at) AS first_scored_at,
                   COALESCE(lc.total_scoring_cycles, 0) AS total_scoring_cycles
            FROM velocity_scores v
            INNER JOIN (SELECT topic_key, MAX(scored_at) AS max_at, MIN(scored_at) AS first_at
                        FROM velocity_scores GROUP BY topic_key) agg
              ON v.topic_key = agg.topic_key AND v.scored_at = agg.max_at
            LEFT JOIN topic_lifecycle lc ON v.topic_key = lc.topic_key
            WHERE v.overall_score >= 0 AND COALESCE(v.total_mentions,0) >= 5
            ORDER BY v.overall_score DESC, v.total_mentions DESC, v.scored_at DESC
            LIMIT 5000""").fetchall():
            print("   ", list(r)[0] if not isinstance(r, dict) else list(r.values())[0])
    finally:
        conn.close()


def main() -> int:
    try:
        import gravitational_anomaly_detector as g
        try:
            print("anomaly_log pruned:", g._prune_anomaly_log(30))
        except Exception:
            print("[maint] anomaly_log prune FAILED (continuing):")
            traceback.print_exc()
        n = g._precompute_serve_payloads(int(os.getenv("PRECOMPUTE_TOP_N", "600")))
        print(f"serve_payloads written: {n} (schema {g.PAYLOAD_SCHEMA_VERSION})")
        try:
            _build_diagnostics(g)
        except Exception:
            print("[maint] diagnostics FAILED (continuing):")
            traceback.print_exc()
        print("DONE")
    except Exception:
        print("[maint] precompute FAILED — stored payloads untouched (the swap "
              "is transactional); worker cycle will retry:")
        traceback.print_exc()
    return 0


if __name__ == "__main__":
    sys.exit(main())
