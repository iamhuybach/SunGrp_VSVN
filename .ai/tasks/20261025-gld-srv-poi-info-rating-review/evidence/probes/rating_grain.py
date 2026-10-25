# Fabric DEV only. Read-only. Lakehouse lh_vv_silver must be attached.
# Decision: slv_3p_poi_rating has at most one row per poi_id, and poi_id is never null.
# Pass: null_poi_id_rows = 0 and duplicate_poi_id_groups = 0.
# Fail: do not pick a row. Paste this output at
# .ai/tasks/20261025-gld-srv-poi-info-rating-review/evidence/results/rating_grain.txt
# Limits: aggregates plus at most 50 poi_id values. No personal data, secrets, or production extracts.

FQ = "lh_vv_silver.dbo.slv_3p_poi_rating"
fields = {f.name: f.dataType.simpleString() for f in spark.table(FQ).schema.fields}
print("columns", {name: fields.get(name) for name in ("poi_id", "rating_overall", "rating_count")})

spark.sql(f"""
SELECT
  COUNT(*) AS row_count,
  SUM(CASE WHEN poi_id IS NULL THEN 1 ELSE 0 END) AS null_poi_id_rows,
  COUNT(DISTINCT poi_id) AS distinct_poi_id
FROM {FQ}
""").show(truncate=False)

spark.sql(f"""
SELECT COUNT(*) AS duplicate_poi_id_groups
FROM (
  SELECT poi_id
  FROM {FQ}
  WHERE poi_id IS NOT NULL
  GROUP BY poi_id
  HAVING COUNT(*) > 1
)
""").show(truncate=False)

spark.sql(f"""
SELECT poi_id, COUNT(*) AS n
FROM {FQ}
WHERE poi_id IS NOT NULL
GROUP BY poi_id
HAVING COUNT(*) > 1
ORDER BY n DESC, poi_id
LIMIT 50
""").show(50, truncate=False)
