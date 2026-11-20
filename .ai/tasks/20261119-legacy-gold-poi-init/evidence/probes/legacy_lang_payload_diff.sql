-- P4. Chỉ đọc. Gold cũ sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master.
-- Đếm source_id có hơn một lang mà cột nghiệp vụ không giống nhau.
-- Dán vào evidence/results/legacy_lang_payload_diff.txt.
WITH per_id AS (
  SELECT source_id,
         COUNT(*) AS rows_n,
         COUNT(poi_name) AS poi_name_n,
         COUNT(DISTINCT poi_name) AS poi_name_d,
         MIN(poi_name) AS poi_name_min,
         MAX(poi_name) AS poi_name_max,
         COUNT(business_sector) AS business_sector_n,
         COUNT(DISTINCT business_sector) AS business_sector_d,
         MIN(business_sector) AS business_sector_min,
         MAX(business_sector) AS business_sector_max,
         COUNT(business_category) AS business_category_n,
         COUNT(DISTINCT business_category) AS business_category_d,
         MIN(business_category) AS business_category_min,
         MAX(business_category) AS business_category_max,
         COUNT(operating_status) AS operating_status_n,
         COUNT(DISTINCT operating_status) AS operating_status_d,
         MIN(operating_status) AS operating_status_min,
         MAX(operating_status) AS operating_status_max,
         COUNT(district) AS district_n,
         COUNT(DISTINCT district) AS district_d,
         MIN(district) AS district_min,
         MAX(district) AS district_max,
         COUNT(DISTINCT CAST(is_verified AS STRING)) AS is_verified_d,
         COUNT(DISTINCT CAST(is_bookable AS STRING)) AS is_bookable_d,
         COUNT(DISTINCT CAST(is_active AS STRING)) AS is_active_d,
         COUNT(DISTINCT CAST(rating_overall AS STRING)) AS rating_overall_d,
         COUNT(DISTINCT CAST(rating_count AS STRING)) AS rating_count_d
  FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master
  WHERE ingestion_source = 'google'
    AND source_id IS NOT NULL AND TRIM(source_id) <> ''
  GROUP BY source_id
  HAVING COUNT(DISTINCT lang) > 1
)
SELECT COUNT(*) AS multi_lang_ids,
       SUM(CASE WHEN poi_name_d > 1 OR (poi_name_n > 0 AND poi_name_n < rows_n) OR poi_name_min <> poi_name_max THEN 1 ELSE 0 END) AS poi_name_diff,
       SUM(CASE WHEN business_sector_d > 1 OR (business_sector_n > 0 AND business_sector_n < rows_n) OR business_sector_min <> business_sector_max THEN 1 ELSE 0 END) AS business_sector_diff,
       SUM(CASE WHEN business_category_d > 1 OR (business_category_n > 0 AND business_category_n < rows_n) OR business_category_min <> business_category_max THEN 1 ELSE 0 END) AS business_category_diff,
       SUM(CASE WHEN operating_status_d > 1 OR (operating_status_n > 0 AND operating_status_n < rows_n) OR operating_status_min <> operating_status_max THEN 1 ELSE 0 END) AS operating_status_diff,
       SUM(CASE WHEN district_d > 1 OR (district_n > 0 AND district_n < rows_n) OR district_min <> district_max THEN 1 ELSE 0 END) AS district_diff,
       SUM(CASE WHEN is_verified_d > 1 THEN 1 ELSE 0 END) AS is_verified_diff,
       SUM(CASE WHEN is_bookable_d > 1 THEN 1 ELSE 0 END) AS is_bookable_diff,
       SUM(CASE WHEN is_active_d > 1 THEN 1 ELSE 0 END) AS is_active_diff,
       SUM(CASE WHEN rating_overall_d > 1 THEN 1 ELSE 0 END) AS rating_overall_diff,
       SUM(CASE WHEN rating_count_d > 1 THEN 1 ELSE 0 END) AS rating_count_diff
FROM per_id;

-- Partner: source_id có hai poi_id cùng lang. Tối đa 5 khóa, không tên.
SELECT source_id, lang, COUNT(*) AS poi_ids
FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master
WHERE ingestion_source = 'partner_portal'
GROUP BY source_id, lang
HAVING COUNT(*) > 1
LIMIT 5;
