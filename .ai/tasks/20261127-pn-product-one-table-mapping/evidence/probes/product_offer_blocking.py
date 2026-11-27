# Fabric DEV. One Spark cell. Lakehouse lh_vv_silver in the same workspace.
# Runs P-1 through P-5. Read only. Paste the whole console into
# evidence/results/product_offer_blocking.txt
# Set LEGACY once. Spark 3 rejects timestamp year 58774.
# Aggregates only. Do not paste ids or price strings. No secrets.

spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
print("timeParserPolicy", spark.conf.get("spark.sql.legacy.timeParserPolicy"))


def show(title, sql):
    print("\n==", title)
    try:
        spark.sql(sql).show(50, truncate=False)
    except Exception as exc:
        print("ERROR", type(exc).__name__)
        print(str(exc)[:2000])


show("P-1 product_id_collision", """
SELECT
  (SELECT count(*) FROM lh_vv_silver.dbo.slv_pn_products p
     JOIN lh_vv_silver.dbo.slv_pn_hotel_room_types h ON p.id = h.id) AS cross_collisions,
  (SELECT count(*) - count(DISTINCT id) FROM lh_vv_silver.dbo.slv_pn_products) AS dup_products,
  (SELECT count(*) - count(DISTINCT id) FROM lh_vv_silver.dbo.slv_pn_hotel_room_types) AS dup_rooms
""")

show("P-2 holiday_bsid_fallback", """
WITH r AS (
  SELECT product_id, count(DISTINCT business_service_id) n
  FROM lh_vv_silver.dbo.slv_pn_product_business_service_relation
  GROUP BY product_id
),
s AS (
  SELECT product_id, product_post_id
  FROM lh_vv_silver.dbo.slv_pn_product_sale
  WHERE deleted_at IS NULL
),
po AS (
  SELECT id, business_service_id
  FROM lh_vv_silver.dbo.slv_pn_product_posts
)
SELECT
  CASE
    WHEN r.n > 1 THEN 'relation_2plus'
    WHEN r.n = 1 THEN 'relation_1'
    WHEN po.business_service_id IS NOT NULL THEN 'post_only'
    ELSE 'none'
  END AS cls,
  count(*) AS product_count
FROM s
LEFT JOIN r ON r.product_id = s.product_id
LEFT JOIN po ON po.id = s.product_post_id
GROUP BY
  CASE
    WHEN r.n > 1 THEN 'relation_2plus'
    WHEN r.n = 1 THEN 'relation_1'
    WHEN po.business_service_id IS NOT NULL THEN 'post_only'
    ELSE 'none'
  END
ORDER BY cls
""")

show("P-3 coverage", """
WITH ids AS (
  SELECT 'holiday' AS src, business_service_id
  FROM lh_vv_silver.dbo.slv_pn_product_business_service_relation
  WHERE business_service_id IS NOT NULL
  UNION
  SELECT 'hotel', business_service_id
  FROM lh_vv_silver.dbo.slv_pn_hotel_room_types
  WHERE deleted = false AND business_service_id IS NOT NULL
),
keyed AS (
  SELECT src, business_service_id,
    concat_ws('-', substr(m, 1, 8), substr(m, 9, 4), substr(m, 13, 4), substr(m, 17, 4), substr(m, 21, 12)) AS poi_id
  FROM (
    SELECT src, business_service_id, md5(concat(business_service_id, 'partner')) AS m
    FROM ids
  )
)
SELECT
  k.src,
  CASE
    WHEN d.poi_id IS NULL THEN 'unmatched'
    WHEN d.destination_id IS NULL THEN 'destination_null'
    ELSE 'matched'
  END AS coverage,
  count(*) AS business_service_count
FROM keyed k
LEFT JOIN lh_vv_silver.dbo.slv_enr_poi_destination d
  ON d.poi_id = k.poi_id
GROUP BY k.src,
  CASE
    WHEN d.poi_id IS NULL THEN 'unmatched'
    WHEN d.destination_id IS NULL THEN 'destination_null'
    ELSE 'matched'
  END
ORDER BY src, coverage
""")

show("P-3 destination_count", """
WITH ids AS (
  SELECT 'holiday' AS src, business_service_id
  FROM lh_vv_silver.dbo.slv_pn_product_business_service_relation
  WHERE business_service_id IS NOT NULL
  UNION
  SELECT 'hotel', business_service_id
  FROM lh_vv_silver.dbo.slv_pn_hotel_room_types
  WHERE deleted = false AND business_service_id IS NOT NULL
),
keyed AS (
  SELECT src,
    concat_ws('-', substr(m, 1, 8), substr(m, 9, 4), substr(m, 13, 4), substr(m, 17, 4), substr(m, 21, 12)) AS poi_id
  FROM (
    SELECT src, business_service_id, md5(concat(business_service_id, 'partner')) AS m
    FROM ids
  )
)
SELECT
  k.src,
  size(from_json(d.destination_id, 'array<string>')) AS destination_count,
  count(*) AS business_service_count
FROM keyed k
JOIN lh_vv_silver.dbo.slv_enr_poi_destination d
  ON d.poi_id = k.poi_id
GROUP BY k.src, size(from_json(d.destination_id, 'array<string>'))
ORDER BY src, destination_count
""")

show("P-4 variant_counts", """
WITH sale AS (
  SELECT product_id
  FROM lh_vv_silver.dbo.slv_pn_product_sale
  WHERE deleted_at IS NULL
),
per_product AS (
  SELECT
    s.product_id,
    count(v.id) AS n_var,
    sum(CASE WHEN v.deleted = true THEN 1 ELSE 0 END) AS n_deleted
  FROM sale s
  LEFT JOIN lh_vv_silver.dbo.slv_pn_product_variants v
    ON v.product_id = s.product_id
  GROUP BY s.product_id
)
SELECT
  sum(CASE WHEN n_var = 0 THEN 1 ELSE 0 END) AS products_with_0_variants,
  sum(CASE WHEN n_var > 0 AND n_deleted = n_var THEN 1 ELSE 0 END) AS products_all_variants_deleted,
  sum(n_deleted) AS deleted_variant_rows
FROM per_product
""")

show("P-4 variants_without_vi", """
WITH sale AS (
  SELECT product_id
  FROM lh_vv_silver.dbo.slv_pn_product_sale
  WHERE deleted_at IS NULL
),
var AS (
  SELECT v.id AS variant_id
  FROM lh_vv_silver.dbo.slv_pn_product_variants v
  JOIN sale s ON s.product_id = v.product_id
)
SELECT count(*) AS variants_without_vi
FROM var v
LEFT JOIN lh_vv_silver.dbo.slv_pn_product_variant_translations t
  ON t.variant_id = v.variant_id AND t.locale = 'vi'
WHERE t.variant_id IS NULL
""")

show("P-5 hotel_rate_attach", """
WITH rooms AS (
  SELECT id, business_service_id
  FROM lh_vv_silver.dbo.slv_pn_hotel_room_types
  WHERE deleted = false
),
rates AS (
  SELECT business_service_id, count(*) AS n
  FROM lh_vv_silver.dbo.slv_pn_hotel_rate_plans
  WHERE deleted = false
  GROUP BY business_service_id
)
SELECT
  sum(CASE WHEN coalesce(rates.n, 0) = 0 THEN 1 ELSE 0 END) AS rooms_with_0_live_rate_plans,
  max(coalesce(rates.n, 0)) AS max_rate_plans_per_business_service_id
FROM rooms
LEFT JOIN rates ON rooms.business_service_id = rates.business_service_id
""")
