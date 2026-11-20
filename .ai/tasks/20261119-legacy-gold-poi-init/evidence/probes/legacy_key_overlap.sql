-- P2. Chỉ đọc. Cũ: sgr_visitvn_prd_batch. Mới: sgr_visitvn_dev.
-- uuid_format không có trong phiên SQL này. Dùng regexp_replace(md5(...)) như uuid_md5 của NB_LIB_TRANSFORM_SLV_GLD.
-- Không in khóa. Dán vào evidence/results/legacy_key_overlap.txt.
WITH ids AS (
  SELECT 'google' AS ingestion_source,
         regexp_replace(md5(concat('google', source_id)), '^(.{8})(.{4})(.{4})(.{4})(.{12})$', '$1-$2-$3-$4-$5') AS poi_id
  FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master
  WHERE ingestion_source = 'google'
    AND source_id IS NOT NULL AND TRIM(source_id) <> ''
  UNION
  SELECT 'partner_portal',
         regexp_replace(md5(concat(source_id, 'partner')), '^(.{8})(.{4})(.{4})(.{4})(.{12})$', '$1-$2-$3-$4-$5')
  FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master
  WHERE ingestion_source = 'partner_portal'
    AND source_id IS NOT NULL AND TRIM(source_id) <> ''
)
SELECT i.ingestion_source,
       COUNT(DISTINCT i.poi_id) AS legacy_ids,
       COUNT(DISTINCT CASE WHEN t.deleted_at IS NULL THEN t.poi_id END) AS live_on_info,
       COUNT(DISTINCT CASE WHEN t.deleted_at IS NOT NULL THEN t.poi_id END) AS deleted_on_info
FROM ids i
LEFT JOIN sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info t
  ON t.poi_id = i.poi_id
GROUP BY i.ingestion_source
ORDER BY i.ingestion_source;

WITH ids AS (
  SELECT ingestion_source, lang,
         CASE
           WHEN ingestion_source = 'google'
             THEN regexp_replace(md5(concat('google', source_id)), '^(.{8})(.{4})(.{4})(.{4})(.{12})$', '$1-$2-$3-$4-$5')
           ELSE regexp_replace(md5(concat(source_id, 'partner')), '^(.{8})(.{4})(.{4})(.{4})(.{12})$', '$1-$2-$3-$4-$5')
         END AS poi_id
  FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master
  WHERE ingestion_source IN ('google', 'partner_portal')
    AND source_id IS NOT NULL AND TRIM(source_id) <> ''
)
SELECT i.ingestion_source,
       COUNT(*) AS legacy_rows,
       SUM(CASE WHEN t.poi_id IS NOT NULL AND t.deleted_at IS NULL THEN 1 ELSE 0 END) AS live_pair,
       SUM(CASE WHEN t.poi_id IS NOT NULL AND t.deleted_at IS NOT NULL THEN 1 ELSE 0 END) AS deleted_pair
FROM ids i
LEFT JOIN sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang t
  ON t.poi_id = i.poi_id AND t.lang = i.lang
GROUP BY i.ingestion_source
ORDER BY i.ingestion_source;
