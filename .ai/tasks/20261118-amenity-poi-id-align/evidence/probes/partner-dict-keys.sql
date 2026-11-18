-- Fabric DEV. Read-only. Spark SQL. Lakehouse lh_vv_silver. Probe P4.
-- Decision: active partner ref_dictionary_amenities keys, duplicate raw keys, and other/other rows.
-- Active: is_active = true AND source_name partner. This Fabric table has no deleted_at. Counts only. No personal data.
-- 1. Open a Fabric notebook on DEV that can read lh_vv_silver. Parameters: none.
-- 2. Run the three queries in order. Do not run a notebook that writes.
-- 3. Paste all three into .ai/tasks/20261118-amenity-poi-id-align/evidence/results/partner-dict-keys.txt
-- 4. Pass: group counts, one duplicate-key count, and one other/other count.
-- other/other means business_sector and amenity_group are both other.

-- groups
SELECT business_sector, amenity_group, COUNT(*) AS rows
FROM lh_vv_silver.dbo.ref_dictionary_amenities
WHERE is_active = true
  AND lower(trim(source_name)) = 'partner'
GROUP BY business_sector, amenity_group
ORDER BY business_sector, amenity_group;

-- duplicate (business_sector, amenity_group, amenity_raw)
SELECT COUNT(*) AS duplicate_keys
FROM (
    SELECT business_sector, amenity_group, amenity_raw
    FROM lh_vv_silver.dbo.ref_dictionary_amenities
    WHERE is_active = true
      AND lower(trim(source_name)) = 'partner'
    GROUP BY business_sector, amenity_group, amenity_raw
    HAVING COUNT(*) > 1
) d;

-- other/other
SELECT COUNT(*) AS other_other_rows
FROM lh_vv_silver.dbo.ref_dictionary_amenities
WHERE is_active = true
  AND lower(trim(source_name)) = 'partner'
  AND lower(trim(business_sector)) = 'other'
  AND lower(trim(amenity_group)) = 'other';
