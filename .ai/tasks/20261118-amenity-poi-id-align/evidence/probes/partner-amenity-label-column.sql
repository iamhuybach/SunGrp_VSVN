-- Fabric DEV. Read-only. Spark SQL. Lakehouse lh_vv_silver. Probe P2b.
-- Mục đích: đếm nhãn mảng chuỗi khớp amenity_raw, amenity_en, amenity_vi, amenity. Không ghi bảng.
-- Partner L1: coalesce(deleted, false) = false. Entity: deleted_at IS NULL. Dictionary: is_active = true.
-- 1. Open a Fabric notebook on DEV that can read lh_vv_silver. Parameters: none.
-- 2. Run the one counts query. Do not run a notebook that writes.
-- 3. Paste it into .ai/tasks/20261118-amenity-poi-id-align/evidence/results/partner-amenity-label-column.txt
-- 4. Pass: one count row per business_sector, parent_key, and child_key. No label sample.

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
    SELECT vi.id AS id, coalesce(vi.am, svc.am) AS am
    FROM vi
    LEFT JOIN svc ON vi.id = svc.id
),
parents AS (
    SELECT id, parent_key, get_json_object(am, concat('$.', parent_key)) AS parent_v
    FROM blk
    LATERAL VIEW explode(json_object_keys(am)) p AS parent_key
    WHERE left(trim(get_json_object(am, concat('$.', parent_key))), 1) = '{'
),
child AS (
    SELECT id, parent_key, child_key, get_json_object(parent_v, concat('$.', child_key)) AS v
    FROM parents
    LATERAL VIEW explode(json_object_keys(parent_v)) c AS child_key
),
labels AS (
    SELECT id, parent_key, child_key, trim(label) AS label
    FROM child
    LATERAL VIEW explode(from_json(v, 'array<string>')) e AS label
    WHERE left(trim(v), 1) = '['
      AND label IS NOT NULL
      AND trim(label) <> ''
),
ent AS (
    SELECT source_id, business_sector
    FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich
    WHERE deleted_at IS NULL
      AND lower(trim(source_name)) = 'partner'
),
dict AS (
    SELECT trim(amenity_raw) AS amenity_raw,
           trim(amenity_en) AS amenity_en,
           trim(amenity_vi) AS amenity_vi,
           trim(amenity) AS amenity
    FROM lh_vv_silver.dbo.ref_dictionary_amenities
    WHERE is_active = true
      AND lower(trim(source_name)) = 'partner'
),
joined AS (
    SELECT CASE
               WHEN e.source_id IS NULL THEN '<no_entity>'
               WHEN e.business_sector IS NULL THEN '<null>'
               WHEN trim(e.business_sector) = '' THEN '<empty>'
               ELSE e.business_sector
           END AS business_sector,
           l.parent_key,
           l.child_key,
           l.label,
           MAX(CASE WHEN d.amenity_raw = l.label THEN 1 ELSE 0 END) AS hit_raw,
           MAX(CASE WHEN d.amenity_en = l.label THEN 1 ELSE 0 END) AS hit_en,
           MAX(CASE WHEN d.amenity_vi = l.label THEN 1 ELSE 0 END) AS hit_vi,
           MAX(CASE WHEN d.amenity = l.label THEN 1 ELSE 0 END) AS hit_amenity
    FROM labels l
    LEFT JOIN ent e ON l.id = e.source_id
    LEFT JOIN dict d
        ON d.amenity_raw = l.label
        OR d.amenity_en = l.label
        OR d.amenity_vi = l.label
        OR d.amenity = l.label
    GROUP BY CASE
                 WHEN e.source_id IS NULL THEN '<no_entity>'
                 WHEN e.business_sector IS NULL THEN '<null>'
                 WHEN trim(e.business_sector) = '' THEN '<empty>'
                 ELSE e.business_sector
             END,
             l.parent_key,
             l.child_key,
             l.label
)
SELECT business_sector,
       parent_key,
       child_key,
       COUNT(*) AS labels,
       SUM(hit_raw) AS hit_raw,
       SUM(hit_en) AS hit_en,
       SUM(hit_vi) AS hit_vi,
       SUM(hit_amenity) AS hit_amenity
FROM joined
GROUP BY business_sector, parent_key, child_key
ORDER BY business_sector, parent_key, child_key;
