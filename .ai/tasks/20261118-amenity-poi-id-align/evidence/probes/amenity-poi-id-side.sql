-- Fabric DEV. Read-only. Lakehouses lh_vv_silver and lh_vv_gold. Spark SQL.
-- Decision D-1: where the 15995 amenity poi_id values sit, since none are on live gld_srv_poi_info.
-- Live row means deleted_at IS NULL. Counts only. No sample. No personal data.
-- 1. Open a Fabric notebook on DEV that can read both lakehouses. Parameters: none.
-- 2. Run the three queries in order. Do not run an amenity or info notebook.
-- 3. Paste all three results into .ai/tasks/20261118-amenity-poi-id-align/evidence/results/amenity-poi-id-side.txt
-- 4. Pass: info counts by source_name, amenity counts by entity source, and one overlap ignoring info.deleted_at.

-- 1. live gld_srv_poi_info poi_id by source_name
SELECT coalesce(lower(trim(source_name)), '<null>') AS source_name,
       COUNT(DISTINCT poi_id) AS live_poi_id
FROM lh_vv_gold.dbo.gld_srv_poi_info
WHERE deleted_at IS NULL
GROUP BY coalesce(lower(trim(source_name)), '<null>')
ORDER BY source_name;

-- 2. live slv_poi_amenity poi_id against live slv_poi_entity_non_enrich
SELECT CASE
           WHEN e.poi_id IS NULL THEN '<no_entity>'
           ELSE coalesce(lower(trim(e.source_name)), '<null>')
       END AS entity_source,
       COUNT(*) AS amenity_poi_id
FROM (
    SELECT DISTINCT poi_id
    FROM lh_vv_silver.dbo.slv_poi_amenity
    WHERE deleted_at IS NULL
) a
LEFT JOIN (
    SELECT poi_id, source_name
    FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich
    WHERE deleted_at IS NULL
) e
    ON a.poi_id = e.poi_id
GROUP BY CASE
             WHEN e.poi_id IS NULL THEN '<no_entity>'
             ELSE coalesce(lower(trim(e.source_name)), '<null>')
         END
ORDER BY entity_source;

-- 3. same amenity poi_id values on gld_srv_poi_info, ignoring info.deleted_at
SELECT COUNT(*) AS amenity_poi_id,
       COUNT(i.poi_id) AS on_info_any_deleted_at
FROM (
    SELECT DISTINCT poi_id
    FROM lh_vv_silver.dbo.slv_poi_amenity
    WHERE deleted_at IS NULL
) a
LEFT JOIN (
    SELECT DISTINCT poi_id
    FROM lh_vv_gold.dbo.gld_srv_poi_info
) i
    ON a.poi_id = i.poi_id;

-- 4. post-check: live amenity poi_id on live gld_srv_poi_info, by entity source
SELECT CASE
           WHEN e.poi_id IS NULL THEN '<no_entity>'
           ELSE coalesce(lower(trim(e.source_name)), '<null>')
       END AS entity_source,
       COUNT(*) AS amenity_poi_id,
       COUNT(i.poi_id) AS in_gld_srv_poi_info
FROM (
    SELECT DISTINCT poi_id
    FROM lh_vv_silver.dbo.slv_poi_amenity
    WHERE deleted_at IS NULL
) a
LEFT JOIN (
    SELECT poi_id, source_name
    FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich
    WHERE deleted_at IS NULL
) e
    ON a.poi_id = e.poi_id
LEFT JOIN (
    SELECT DISTINCT poi_id
    FROM lh_vv_gold.dbo.gld_srv_poi_info
    WHERE deleted_at IS NULL
) i
    ON a.poi_id = i.poi_id
GROUP BY CASE
             WHEN e.poi_id IS NULL THEN '<no_entity>'
             ELSE coalesce(lower(trim(e.source_name)), '<null>')
         END
ORDER BY entity_source;
