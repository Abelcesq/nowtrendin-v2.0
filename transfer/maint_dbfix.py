"""One-off DB maintenance for the Gradient engine (manual, re-runnable).

Ensures the velocity_scores indexes exist and prunes the table to the most
recent N cycles per topic. The worker now prunes automatically every cycle
(see _prune_velocity_scores), so this is only needed for a manual catch-up or
after a bulk import.

Run:  heroku run python maint_dbfix.py -a nowtrendin
Env:  KEEP_CYCLES (default 30)
"""
import os
import psycopg2

KEEP_CYCLES = int(os.getenv("KEEP_CYCLES", "30"))

conn = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")
conn.autocommit = True
cur = conn.cursor()


def show(tag):
    cur.execute("SELECT count(*), count(distinct topic_key) FROM velocity_scores")
    rows, topics = cur.fetchone()
    cur.execute("SELECT pg_size_pretty(pg_total_relation_size('velocity_scores'))")
    print(f"[{tag}] velocity_scores: {rows} rows, {topics} topics, {cur.fetchone()[0]}")


show("before")

for ddl in [
    "CREATE INDEX IF NOT EXISTS idx_vs_topic_scored ON velocity_scores (topic_key, scored_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_vs_overall ON velocity_scores (overall_score DESC)",
    "CREATE INDEX IF NOT EXISTS idx_vs_detection ON velocity_scores (detection_score DESC)",
    "CREATE INDEX IF NOT EXISTS idx_vs_scored_at ON velocity_scores (scored_at)",
]:
    cur.execute(ddl)

cur.execute(
    """
    DELETE FROM velocity_scores v
    USING (
        SELECT id, row_number() OVER (
            PARTITION BY topic_key ORDER BY scored_at DESC
        ) AS rn
        FROM velocity_scores
    ) ranked
    WHERE v.id = ranked.id AND ranked.rn > %s
    """,
    (KEEP_CYCLES,),
)
print("deleted rows:", cur.rowcount)
cur.execute("VACUUM ANALYZE velocity_scores")
show("after")
cur.close()
conn.close()
print("DONE")
