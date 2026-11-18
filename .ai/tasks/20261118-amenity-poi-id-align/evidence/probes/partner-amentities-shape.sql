-- Fabric DEV. Read-only. Spark SQL. Lakehouse lh_vv_silver. Probe P1.
-- Mục đích: đếm key của amentities partner. Không ghi bảng. Chạy lại sau lỗi deleted_at.
-- Decision: top-level keys of the partner amentities block, plus schema of keys other than policies and main_category.
-- Partner L1 live row: NOT coalesce(deleted, false), same as _live in NB_SLV_POI_ENTITY_NON_ENRICH.
-- These two tables have no deleted_at. Counts and schema strings only. No personal data. No sample of values.
-- 1. Open a Fabric notebook on DEV that can read lh_vv_silver. Parameters: none.
-- 2. Run query keys, then query shape, then query child keys. Do not run a notebook that writes.
-- 3. Paste both into .ai/tasks/20261118-amenity-poi-id-align/evidence/results/partner-amentities-shape.txt
-- 4. Pass: one row per top-level key with a count, one row per key kind, and child-key counts for objects.
-- schema_of_json cannot take a column. Child key names replace it. No values.

-- keys
WITH vi AS (
    SELECT business_service_id AS id, amentities AS am
    FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns
    WHERE coalesce(deleted, false) = false AND locale = 'vi'
),
svc AS (
    SELECT id, amentities AS am
    FROM lh_vv_silver.dbo.slv_pn_business_services
    WHERE coalesce(deleted, false) = false
),
blk AS (
    SELECT vi.id, coalesce(vi.am, svc.am) AS am
    FROM vi
    LEFT JOIN svc ON vi.id = svc.id
)
SELECT k AS top_key, COUNT(*) AS rows
FROM blk
LATERAL VIEW explode(json_object_keys(am)) t AS k
WHERE am IS NOT NULL
GROUP BY k
ORDER BY rows DESC;

-- shape: kind of each other top-level value, then child keys of object values. No values.
WITH vi AS (
    SELECT business_service_id AS id, amentities AS am
    FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns
    WHERE coalesce(deleted, false) = false AND locale = 'vi'
),
svc AS (
    SELECT id, amentities AS am
    FROM lh_vv_silver.dbo.slv_pn_business_services
    WHERE coalesce(deleted, false) = false
),
blk AS (
    SELECT vi.id, coalesce(vi.am, svc.am) AS am
    FROM vi
    LEFT JOIN svc ON vi.id = svc.id
),
keyed AS (
    SELECT k, get_json_object(am, concat('$.', k)) AS v
    FROM blk
    LATERAL VIEW explode(json_object_keys(am)) t AS k
    WHERE am IS NOT NULL AND k NOT IN ('policies', 'main_category')
)
SELECT k AS top_key,
       CASE
           WHEN v IS NULL THEN 'null'
           WHEN left(trim(v), 1) = '{' THEN 'object'
           WHEN left(trim(v), 1) = '[' THEN 'array'
           ELSE 'scalar'
       END AS json_kind,
       COUNT(*) AS rows
FROM keyed
GROUP BY k,
         CASE
             WHEN v IS NULL THEN 'null'
             WHEN left(trim(v), 1) = '{' THEN 'object'
             WHEN left(trim(v), 1) = '[' THEN 'array'
             ELSE 'scalar'
         END
ORDER BY top_key, rows DESC;

-- child keys of object values
WITH vi AS (
    SELECT business_service_id AS id, amentities AS am
    FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns
    WHERE coalesce(deleted, false) = false AND locale = 'vi'
),
svc AS (
    SELECT id, amentities AS am
    FROM lh_vv_silver.dbo.slv_pn_business_services
    WHERE coalesce(deleted, false) = false
),
blk AS (
    SELECT vi.id, coalesce(vi.am, svc.am) AS am
    FROM vi
    LEFT JOIN svc ON vi.id = svc.id
),
objects AS (
    SELECT k, get_json_object(am, concat('$.', k)) AS v
    FROM blk
    LATERAL VIEW explode(json_object_keys(am)) t AS k
    WHERE am IS NOT NULL
      AND k NOT IN ('policies', 'main_category')
      AND left(trim(get_json_object(am, concat('$.', k))), 1) = '{'
)
SELECT k AS top_key, child_key, COUNT(*) AS rows
FROM objects
LATERAL VIEW explode(json_object_keys(v)) c AS child_key
GROUP BY k, child_key
ORDER BY top_key, rows DESC;

