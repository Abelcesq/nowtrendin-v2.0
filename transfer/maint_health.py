"""Read-only health probe (run via heroku run python maint_health.py)."""
import os, psycopg2, psycopg2.extras, statistics
from datetime import datetime, timezone, timedelta

c = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")
cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def q(sql, args=()):
    cur.execute(sql, args)
    return cur.fetchall()


def cols(t):
    return [r['column_name'] for r in q(
        "SELECT column_name FROM information_schema.columns WHERE table_name=%s ORDER BY ordinal_position", (t,))]


print("=== raw_signals columns ===")
rs = cols("raw_signals")
print(" ", rs)

# pick a source-ish column
src = next((x for x in ("platform", "source", "source_name") if x in rs), None)
tier = next((x for x in ("source_tier", "tier") if x in rs), None)
ts = next((x for x in ("collected_at", "created_at", "fetched_at") if x in rs), None)
print(f"\n=== raw_signals by {src}/{tier} (last 48h via {ts}) ===")
if src and ts:
    cut = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    sel = f"{src}" + (f", {tier}" if tier else "")
    for r in q(f"SELECT {sel}, count(*) c FROM raw_signals WHERE {ts} >= %s GROUP BY {sel} ORDER BY c DESC LIMIT 20", (cut,)):
        print("  ", dict(r))
    for r in q(f"SELECT count(*) total, max({ts}) newest, min({ts}) oldest FROM raw_signals"):
        print("  totals:", dict(r))

print("\n=== velocity_scores: latest-per-topic score distribution ===")
rows = q("""
  SELECT v.overall_score, v.detection_score, v.topic_display, v.total_mentions
  FROM velocity_scores v
  INNER JOIN (SELECT topic_key, MAX(scored_at) m FROM velocity_scores GROUP BY topic_key) l
    ON v.topic_key=l.topic_key AND v.scored_at=l.m
""")
ov = [r['overall_score'] or 0 for r in rows]
if ov:
    print(f"  topics={len(rows)} max={max(ov):.1f} mean={statistics.mean(ov):.1f} median={statistics.median(ov):.1f}")
    print(f"  >=70:{sum(1 for x in ov if x>=70)} 55-70:{sum(1 for x in ov if 55<=x<70)} 35-55:{sum(1 for x in ov if 35<=x<55)} <35:{sum(1 for x in ov if x<35)}")
    print("  top 12 by overall:")
    for r in sorted(rows, key=lambda r: -(r['overall_score'] or 0))[:12]:
        print(f"    {(r['topic_display'] or '')[:34]:34} ov={r['overall_score']:.1f} det={r['detection_score']:.1f} mentions={r['total_mentions']}")

print("\n=== topic_queries (N source) ===")
for r in q("SELECT count(*) total, count(distinct topic_key) topics, max(queried_at) newest FROM topic_queries"):
    print(" ", dict(r))

print("\n=== table sizes ===")
for r in q("""SELECT relname, n_live_tup, pg_size_pretty(pg_total_relation_size(relid)) sz
              FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 14"""):
    print(f"  {r['relname']:26} rows={r['n_live_tup']:>8} {r['sz']}")

cur.close(); c.close(); print("DONE")
