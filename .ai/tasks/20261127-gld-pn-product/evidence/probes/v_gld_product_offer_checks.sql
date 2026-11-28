-- V3, V4, V5, V7 for 20261127-gld-pn-product
-- Fabric DEV. Spark SQL. Read only. One result table.
-- Run this whole file in one session. Pass when every row named below is 0,
-- and v3_rows equals v3_distinct_id.
-- v3_rows = 464 and v2_other = 41 and v2_hotel = 423 matches the SUCCESS run.
-- Paste the result at:
-- .ai/tasks/20261127-gld-pn-product/evidence/results/v_gld_product_offer_checks.txt
-- At most 50 rows. No personal data. No secrets.
-- V6 is not in this file. It reruns NB_GLD_SRV_PRODUCT_OFFER with p_force = true
-- and the p_pinned_json of exec ff15ac6b-1e09-4ce4-9ad7-b958944a890f.

SET spark.sql.legacy.timeParserPolicy = LEGACY;

WITH gold AS (
    SELECT *
    FROM lh_vv_gold.dbo.gld_srv_product_offer
    WHERE deleted_at IS NULL
),
sale AS (
    SELECT product_id, original_price, marketing_price, markup_percent
    FROM lh_vv_silver.dbo.slv_pn_product_sale
    WHERE deleted_at IS NULL
),
holiday AS (
    SELECT product_id, original_price, marketing_price, markup_percent
    FROM gold
    WHERE product_type = 'other'
),
gold_poi AS (
    SELECT poi_id, destination_id
    FROM gold
    WHERE poi_id IS NOT NULL
),
dest_for_gold AS (
    SELECT d.poi_id, d.destination_id
    FROM lh_vv_silver.dbo.slv_enr_poi_destination AS d
    INNER JOIN (SELECT DISTINCT poi_id FROM gold_poi) AS g
        ON d.poi_id = g.poi_id
)
SELECT 'v2_other' AS check_name, count(*) AS n FROM gold WHERE product_type = 'other'
UNION ALL
SELECT 'v2_hotel', count(*) FROM gold WHERE product_type = 'hotel'
UNION ALL
SELECT 'v3_rows', count(*) FROM gold
UNION ALL
SELECT 'v3_distinct_id', count(DISTINCT product_id) FROM gold
UNION ALL
SELECT 'v4_gold_minus_sale', count(*) FROM (
    SELECT * FROM holiday
    EXCEPT
    SELECT * FROM sale
)
UNION ALL
SELECT 'v4_sale_minus_gold', count(*) FROM (
    SELECT * FROM sale
    EXCEPT
    SELECT * FROM holiday
)
UNION ALL
SELECT 'v4_hotel_price_not_null', count(*)
FROM gold
WHERE product_type = 'hotel'
  AND (
      original_price IS NOT NULL
      OR marketing_price IS NOT NULL
      OR markup_percent IS NOT NULL
  )
UNION ALL
SELECT 'v5_gold_minus_dest', count(*) FROM (
    SELECT * FROM gold_poi
    EXCEPT
    SELECT * FROM dest_for_gold
)
UNION ALL
SELECT 'v5_dest_minus_gold', count(*) FROM (
    SELECT * FROM dest_for_gold
    EXCEPT
    SELECT * FROM gold_poi
)
UNION ALL
SELECT 'v7_bad_json', count(*)
FROM gold
WHERE from_json(variants_json, 'array<struct<variant_id:string>>') IS NULL
UNION ALL
SELECT 'v7_bad_hotel_ts', count(*)
FROM (
    SELECT explode(
        from_json(variants_json, 'array<struct<attributes:struct<valid_from:string>>>')
    ) AS item
    FROM gold
    WHERE product_type = 'hotel'
)
WHERE item.attributes.valid_from IS NOT NULL
  AND item.attributes.valid_from NOT RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$';
