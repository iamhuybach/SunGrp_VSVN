-- Probe P1–P6 for 20261127-gld-pn-product
-- Environment: Fabric DEV. Spark SQL. Three-part names below.
-- Read only. Aggregates only. No sample rows.
-- Decision: architecture.md §16. P1 duplicate relation pairs (Q2).
-- P2 deleted counts (Q3). P3 blank business_service_id (Q5).
-- P4 sale rows with no relation (Q4). P5 destination match and duplicates (Q6).
-- P6 L2 schema and pipeline edges (Q10).
-- Pass/fail is not a single bit. Paste every result set, including a missing-table error.
-- Limits: aggregates only, no personal data, no secrets, no production extract.
-- Paste sanitized output at:
-- .ai/tasks/20261127-gld-pn-product/evidence/results/p1_p6_gold_product_keys.txt

-- P1. 0 rows means no repeated (product_id, business_service_id, deleted).
SELECT deleted, count(*) AS n
FROM (
    SELECT product_id, business_service_id, deleted
    FROM lh_vv_silver.dbo.slv_pn_product_business_service_relation
    GROUP BY 1, 2, 3
    HAVING count(*) > 1
)
GROUP BY deleted;

-- P2.
SELECT deleted, count(*) AS n
FROM lh_vv_silver.dbo.slv_pn_product_business_service_relation
GROUP BY deleted;

-- P3.
SELECT 'rel' AS t, count_if(business_service_id IS NULL OR trim(business_service_id) = '') AS n
FROM lh_vv_silver.dbo.slv_pn_product_business_service_relation
UNION ALL
SELECT 'room', count_if(business_service_id IS NULL OR trim(business_service_id) = '')
FROM lh_vv_silver.dbo.slv_pn_hotel_room_types
WHERE deleted = false
UNION ALL
SELECT 'rate', count_if(business_service_id IS NULL OR trim(business_service_id) = '')
FROM lh_vv_silver.dbo.slv_pn_hotel_rate_plans
WHERE deleted = false;

-- P4. Sale rows with deleted_at NULL and no relation row.
SELECT count(*) AS n
FROM (
    SELECT product_id
    FROM lh_vv_silver.dbo.slv_pn_product_sale
    WHERE deleted_at IS NULL
) s
LEFT ANTI JOIN lh_vv_silver.dbo.slv_pn_product_business_service_relation r
    ON s.product_id = r.product_id;

-- P5. K(x) is the SQL form of uuid_md5(x, 'partner').
-- tied_or_null: matched poi_id with more than one destination row,
-- and updated_at NULL on one of those rows, or more than one row at max(updated_at).
WITH keys AS (
    SELECT business_service_id
    FROM lh_vv_silver.dbo.slv_pn_product_business_service_relation
    UNION ALL
    SELECT business_service_id
    FROM lh_vv_silver.dbo.slv_pn_hotel_room_types
    UNION ALL
    SELECT business_service_id
    FROM lh_vv_silver.dbo.slv_pn_hotel_rate_plans
),
k AS (
    SELECT DISTINCT regexp_replace(
        md5(concat(business_service_id, 'partner')),
        '^(.{8})(.{4})(.{4})(.{4})(.{12})$',
        '$1-$2-$3-$4-$5'
    ) AS poi_id
    FROM keys
),
dest AS (
    SELECT d.poi_id, d.updated_at
    FROM lh_vv_silver.dbo.slv_enr_poi_destination d
    INNER JOIN k ON k.poi_id = d.poi_id
),
ranked AS (
    SELECT
        poi_id,
        updated_at,
        count(*) OVER (PARTITION BY poi_id) AS n,
        max(updated_at) OVER (PARTITION BY poi_id) AS max_ts,
        sum(CASE WHEN updated_at IS NULL THEN 1 ELSE 0 END) OVER (PARTITION BY poi_id) AS n_null
    FROM dest
),
dup_poi AS (
    SELECT
        poi_id,
        max(n) AS n,
        max(n_null) AS n_null,
        sum(CASE WHEN updated_at = max_ts THEN 1 ELSE 0 END) AS n_at_max
    FROM ranked
    GROUP BY poi_id
    HAVING max(n) > 1
)
SELECT
    (SELECT count(*) FROM k WHERE poi_id IS NOT NULL) AS distinct_poi,
    (SELECT count(DISTINCT poi_id) FROM dest) AS matched_poi,
    (SELECT count(*) FROM dup_poi) AS matched_poi_many_rows,
    (SELECT count_if(n_null > 0 OR n_at_max > 1) FROM dup_poi) AS tied_or_null,
    (
        SELECT count(*)
        FROM k
        LEFT ANTI JOIN lh_vv_silver.dbo.slv_poi_entity_non_enrich e
            ON e.poi_id = k.poi_id
    ) AS poi_absent_from_entity;

-- P6.
DESCRIBE TABLE lh_vv_silver.dbo.slv_pn_product_sale;
DESCRIBE TABLE lh_vv_silver.dbo.slv_pn_hotel_room_offer;
DESCRIBE TABLE lh_vv_silver.dbo.slv_pn_hotel_rate_offer;

SELECT pl_name, src_tbl, trg_tbl, is_active
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_tbl IN (
    'slv_pn_product_sale',
    'slv_pn_hotel_room_offer',
    'slv_pn_hotel_rate_offer'
);
