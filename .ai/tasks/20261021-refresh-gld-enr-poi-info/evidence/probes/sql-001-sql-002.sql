-- Environment: Fabric DEV. Lakehouse lh_vv_silver. Read-only. Do not run outside DEV.
-- Resolves: SQL-001 (one non-null poi_id on slv_poi_entity_non_enrich) and SQL-002 (one live vi row per business_service_id).
-- Prerequisite: silver tables exist. No notebook parameter. No write.
-- Pass: each result set has 0 rows. Fail: any returned row.
-- Output columns: key, n. At most 50 rows per query. No personal data, no secrets.
-- Paste both results into .ai/tasks/20261021-refresh-gld-enr-poi-info/evidence/results/sql-001-sql-002.txt
-- Run in a Spark notebook on DEV, one statement at a time.

-- SQL-001
SELECT poi_id, COUNT(*) AS n
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich
GROUP BY poi_id
HAVING poi_id IS NULL OR COUNT(*) > 1
LIMIT 50;

-- SQL-002
SELECT business_service_id, COUNT(*) AS n
FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns
WHERE locale = 'vi' AND NOT COALESCE(deleted, false)
GROUP BY business_service_id
HAVING business_service_id IS NULL OR COUNT(*) > 1
LIMIT 50;
