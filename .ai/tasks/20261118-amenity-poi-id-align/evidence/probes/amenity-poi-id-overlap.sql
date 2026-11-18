-- Fabric DEV. Read-only. Lakehouses lh_vv_silver and lh_vv_gold. Spark SQL.
-- Decision D-1: count live amenity poi_id values on live gld_srv_poi_info, and those absent.
-- Live row means deleted_at IS NULL. Do not infer counts. No personal data.
-- 1. Open a Fabric notebook on DEV that can read both lakehouses. Parameters: none.
-- 2. Run the counts query, then the sample query. Do not run an amenity notebook.
-- 3. Paste both results into .ai/tasks/20261118-amenity-poi-id-align/evidence/results/amenity-poi-id-overlap.txt
-- 4. Pass: four counts (slv and gld, in_info and not_in_info) and at most 50 sample rows.
-- Sample columns: amenity_table, poi_id. Cap 50. No names, addresses, or secrets.

-- counts
SELECT d.amenity_table,
       COUNT(*) AS amenity_poi_id,
       COUNT(i.poi_id) AS in_gld_srv_poi_info,
       COUNT(*) - COUNT(i.poi_id) AS not_in_gld_srv_poi_info
FROM (
    SELECT DISTINCT 'slv_poi_amenity' AS amenity_table, poi_id
    FROM lh_vv_silver.dbo.slv_poi_amenity
    WHERE deleted_at IS NULL
    UNION ALL
    SELECT DISTINCT 'gld_srv_poi_amenity', poi_id
    FROM lh_vv_gold.dbo.gld_srv_poi_amenity
    WHERE deleted_at IS NULL
) d
LEFT JOIN (
    SELECT DISTINCT poi_id
    FROM lh_vv_gold.dbo.gld_srv_poi_info
    WHERE deleted_at IS NULL
) i
    ON d.poi_id = i.poi_id
GROUP BY d.amenity_table
ORDER BY d.amenity_table;

-- sample: amenity poi_id values absent from gld_srv_poi_info
SELECT amenity_table, poi_id
FROM (
    SELECT 'slv_poi_amenity' AS amenity_table, a.poi_id
    FROM (
        SELECT DISTINCT poi_id
        FROM lh_vv_silver.dbo.slv_poi_amenity
        WHERE deleted_at IS NULL
    ) a
    WHERE NOT EXISTS (
        SELECT 1
        FROM lh_vv_gold.dbo.gld_srv_poi_info i
        WHERE i.deleted_at IS NULL
          AND i.poi_id = a.poi_id
    )
    UNION ALL
    SELECT 'gld_srv_poi_amenity', a.poi_id
    FROM (
        SELECT DISTINCT poi_id
        FROM lh_vv_gold.dbo.gld_srv_poi_amenity
        WHERE deleted_at IS NULL
    ) a
    WHERE NOT EXISTS (
        SELECT 1
        FROM lh_vv_gold.dbo.gld_srv_poi_info i
        WHERE i.deleted_at IS NULL
          AND i.poi_id = a.poi_id
    )
) missing
ORDER BY amenity_table, poi_id
LIMIT 50;
