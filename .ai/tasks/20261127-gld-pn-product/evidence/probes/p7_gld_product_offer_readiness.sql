-- Probe P-7 for 20261127-gld-pn-product
-- Environment: Fabric DEV. Spark SQL. Read only. Aggregates only.
-- (a) pass when every n is 0. (b) pass when both counts are above 0.
-- (c) information only. (d) pass when the three L2 targets have active _GLD30 rows.
-- Limits: no sample rows, no personal data, no secrets.
-- Paste sanitized output at:
-- .ai/tasks/20261127-gld-pn-product/evidence/results/p7_gld_product_offer_readiness.txt
-- Q-04: source timestamps in year 58774. Spark 3 fails to parse them unless this session uses LEGACY.

SET spark.sql.legacy.timeParserPolicy = LEGACY;

-- (a) lookup duplicates
SELECT 'product_tr' AS t, count(*) AS n
FROM (
    SELECT product_id, locale
    FROM lh_vv_silver.dbo.slv_pn_product_translations
    WHERE locale IN ('en', 'vi')
    GROUP BY product_id, locale
    HAVING count(*) > 1
)
UNION ALL
SELECT 'variant_tr', count(*)
FROM (
    SELECT variant_id
    FROM lh_vv_silver.dbo.slv_pn_product_variant_translations
    WHERE locale = 'vi'
    GROUP BY variant_id
    HAVING count(*) > 1
)
UNION ALL
SELECT 'products', count(*)
FROM (
    SELECT id FROM lh_vv_silver.dbo.slv_pn_products
    GROUP BY id
    HAVING count(*) > 1
)
UNION ALL
SELECT 'posts', count(*)
FROM (
    SELECT id FROM lh_vv_silver.dbo.slv_pn_product_posts
    GROUP BY id
    HAVING count(*) > 1
)
UNION ALL
SELECT 'room_types', count(*)
FROM (
    SELECT id FROM lh_vv_silver.dbo.slv_pn_hotel_room_types
    GROUP BY id
    HAVING count(*) > 1
)
UNION ALL
SELECT 'rate_plans', count(*)
FROM (
    SELECT id FROM lh_vv_silver.dbo.slv_pn_hotel_rate_plans
    GROUP BY id
    HAVING count(*) > 1
)
UNION ALL
SELECT 'variants', count(*)
FROM (
    SELECT id FROM lh_vv_silver.dbo.slv_pn_product_variants
    WHERE deleted = false
    GROUP BY id
    HAVING count(*) > 1
);

-- (a) destination duplicates among poi_id the build actually joins
WITH live_sale AS (
    SELECT product_id, product_post_id
    FROM lh_vv_silver.dbo.slv_pn_product_sale
    WHERE deleted_at IS NULL
),
rel AS (
    SELECT
        product_id,
        count(*) AS rel_rows,
        count(DISTINCT business_service_id) AS rel_n,
        max(business_service_id) AS rel_bsid
    FROM lh_vv_silver.dbo.slv_pn_product_business_service_relation
    WHERE deleted = false
    GROUP BY product_id
),
kept AS (
    SELECT sale.product_id, sale.product_post_id, rel.rel_rows, rel.rel_n, rel.rel_bsid
    FROM live_sale AS sale
    LEFT JOIN rel ON sale.product_id = rel.product_id
    WHERE coalesce(rel.rel_n, 0) <= 1
),
holiday_bsid AS (
    SELECT
        CASE
            WHEN kept.rel_rows IS NULL THEN posts.business_service_id
            WHEN kept.rel_n = 1 THEN kept.rel_bsid
        END AS business_service_id
    FROM kept
    LEFT JOIN lh_vv_silver.dbo.slv_pn_product_posts AS posts
        ON kept.product_post_id = posts.id
),
hotel_bsid AS (
    SELECT room_types.business_service_id
    FROM lh_vv_silver.dbo.slv_pn_hotel_room_offer AS room_offer
    LEFT JOIN lh_vv_silver.dbo.slv_pn_hotel_room_types AS room_types
        ON room_offer.room_type_id = room_types.id
    WHERE room_offer.deleted_at IS NULL
),
poi AS (
    SELECT DISTINCT regexp_replace(
        md5(concat(business_service_id, 'partner')),
        '^(.{8})(.{4})(.{4})(.{4})(.{12})$',
        '$1-$2-$3-$4-$5'
    ) AS poi_id
    FROM (
        SELECT business_service_id FROM holiday_bsid
        UNION
        SELECT business_service_id FROM hotel_bsid
    ) AS keys
    WHERE business_service_id IS NOT NULL
)
SELECT 'destination' AS t, count(*) AS n
FROM (
    SELECT destination.poi_id
    FROM lh_vv_silver.dbo.slv_enr_poi_destination AS destination
    INNER JOIN poi ON destination.poi_id = poi.poi_id
    GROUP BY destination.poi_id
    HAVING count(*) > 1
) AS duplicate_destination;

-- (b) branch sizes
SELECT 'sale' AS t, count(*) AS n
FROM lh_vv_silver.dbo.slv_pn_product_sale
WHERE deleted_at IS NULL
UNION ALL
SELECT 'room_offer', count(*)
FROM lh_vv_silver.dbo.slv_pn_hotel_room_offer
WHERE deleted_at IS NULL;

-- (c) deleted rows on lookups that the mapping does not filter
SELECT 'product_tr' AS t, sum(CASE WHEN deleted THEN 1 ELSE 0 END) AS n
FROM lh_vv_silver.dbo.slv_pn_product_translations
UNION ALL
SELECT 'variant_tr', sum(CASE WHEN deleted THEN 1 ELSE 0 END)
FROM lh_vv_silver.dbo.slv_pn_product_variant_translations
UNION ALL
SELECT 'attributes', sum(CASE WHEN deleted THEN 1 ELSE 0 END)
FROM lh_vv_silver.dbo.slv_pn_product_attributes
UNION ALL
SELECT 'attribute_values', sum(CASE WHEN deleted THEN 1 ELSE 0 END)
FROM lh_vv_silver.dbo.slv_pn_product_attribute_values
UNION ALL
SELECT 'attribute_value_tr', sum(CASE WHEN deleted THEN 1 ELSE 0 END)
FROM lh_vv_silver.dbo.slv_pn_product_attribute_value_translations;

-- (d) L2 parents
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
