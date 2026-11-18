-- Fabric DEV. Read-only. Spark SQL. Lakehouses lh_vv_silver and lh_vv_gold. Probe P3.
-- Decision: live partner entity rows, NULL business_sector, sector distribution, overlap with live gld_srv_poi_info.
-- Live row: deleted_at IS NULL. Counts only. No personal data. No sample.
-- 1. Open a Fabric notebook on DEV that can read both lakehouses. Parameters: none.
-- 2. Run query totals, then query sectors. Do not run a notebook that writes.
-- 3. Paste both into .ai/tasks/20261118-amenity-poi-id-align/evidence/results/partner-entity-coverage.txt
-- 4. Pass: one totals row and one row per business_sector, including a null bucket if any.

-- totals
SELECT COUNT(*) AS partner_entity,
       SUM(CASE WHEN e.business_sector IS NULL THEN 1 ELSE 0 END) AS null_business_sector,
       SUM(CASE WHEN i.poi_id IS NOT NULL THEN 1 ELSE 0 END) AS on_gld_srv_poi_info
FROM (
    SELECT poi_id, business_sector
    FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich
    WHERE deleted_at IS NULL
      AND lower(trim(source_name)) = 'partner'
) e
LEFT JOIN (
    SELECT DISTINCT poi_id
    FROM lh_vv_gold.dbo.gld_srv_poi_info
    WHERE deleted_at IS NULL
) i
    ON e.poi_id = i.poi_id;

-- sectors
SELECT coalesce(business_sector, '<null>') AS business_sector,
       COUNT(*) AS rows
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich
WHERE deleted_at IS NULL
  AND lower(trim(source_name)) = 'partner'
GROUP BY coalesce(business_sector, '<null>')
ORDER BY rows DESC;
