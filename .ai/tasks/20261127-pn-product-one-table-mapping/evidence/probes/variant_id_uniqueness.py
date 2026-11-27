# Fabric DEV. One Spark cell. Lakehouse lh_vv_silver in the same workspace.
# Review SQL-001. Read only. Paste the console into
# evidence/results/variant_id_uniqueness.txt
# Set LEGACY once. Spark 3 rejects timestamp year 58774.
# slv_pn_hotel_rate_offer has no business_service_id. That column is on
# slv_pn_hotel_rate_plans. Join offer.rate_plan_id = plans.id.
# PASS when anomaly_count is 0. At most 50 rows. No secrets.

spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
print("timeParserPolicy", spark.conf.get("spark.sql.legacy.timeParserPolicy"))

anomalies = spark.sql("""
WITH anomalies AS (
  SELECT 'holiday' AS branch, CAST(product_id AS STRING) AS owner_id,
         CAST(id AS STRING) AS variant_id, COUNT(*) AS row_count
  FROM lh_vv_silver.dbo.slv_pn_product_variants
  WHERE deleted = false AND product_id IS NOT NULL
  GROUP BY product_id, id
  HAVING id IS NULL OR COUNT(*) > 1
  UNION ALL
  SELECT 'hotel' AS branch, CAST(plan.business_service_id AS STRING) AS owner_id,
         CAST(offer.rate_plan_id AS STRING) AS variant_id, COUNT(*) AS row_count
  FROM lh_vv_silver.dbo.slv_pn_hotel_rate_offer offer
  JOIN lh_vv_silver.dbo.slv_pn_hotel_rate_plans plan
    ON plan.id = offer.rate_plan_id
  WHERE offer.deleted_at IS NULL
    AND plan.business_service_id IS NOT NULL
  GROUP BY plan.business_service_id, offer.rate_plan_id
  HAVING offer.rate_plan_id IS NULL OR COUNT(*) > 1
)
SELECT * FROM anomalies
ORDER BY branch, owner_id, variant_id
LIMIT 50
""")
print("anomaly_count", anomalies.count())
anomalies.show(50, truncate=False)
