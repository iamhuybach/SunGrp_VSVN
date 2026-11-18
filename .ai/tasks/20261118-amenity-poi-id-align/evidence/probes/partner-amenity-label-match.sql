-- Fabric DEV. Read-only. Spark SQL. Lakehouses lh_vv_silver. Probe P2.
-- Mục đích: đếm nhãn trong $.facilities khớp amenity_raw của từ điển partner. Không ghi bảng.
-- Path from P1: facilities is an object. Its child key names match dictionary amenity_group.
-- Partner L1 live row: coalesce(deleted, false) = false. Entity live row: deleted_at IS NULL.
-- Dictionary active: is_active = true. This table has no deleted_at.
-- 1. Open a Fabric notebook on DEV that can read lh_vv_silver. Parameters: none.
-- 2. Run query kinds, then query counts, then query sample. Do not run a notebook that writes.
-- 3. Paste all three into .ai/tasks/20261118-amenity-poi-id-align/evidence/results/partner-amenity-label-match.txt
-- 4. Pass: child-value kinds, match counts by business_sector, and at most 50 unmatched labels.
-- Sample columns: business_sector, amenity_group, amenity_raw. No other fields.

-- kinds of $.facilities child values
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
fac AS (
    SELECT vi.id AS id, get_json_object(coalesce(vi.am, svc.am), '$.facilities') AS fac
    FROM vi
    LEFT JOIN svc ON vi.id = svc.id
),
child AS (
    SELECT child_key, get_json_object(fac, concat('$.', child_key)) AS v
    FROM fac
    LATERAL VIEW explode(json_object_keys(fac)) t AS child_key
    WHERE left(trim(fac), 1) = '{'
)
SELECT child_key,
       CASE
           WHEN v IS NULL THEN 'null'
           WHEN left(trim(v), 1) = '{' THEN 'object'
           WHEN left(trim(v), 1) = '[' THEN 'array'
           ELSE 'scalar'
       END AS json_kind,
       SUM(CASE WHEN left(trim(v), 1) = '[' AND from_json(v, 'array<string>') IS NULL THEN 1 ELSE 0 END) AS array_not_string,
       COUNT(*) AS rows
FROM child
GROUP BY child_key,
         CASE
             WHEN v IS NULL THEN 'null'
             WHEN left(trim(v), 1) = '{' THEN 'object'
             WHEN left(trim(v), 1) = '[' THEN 'array'
             ELSE 'scalar'
         END
ORDER BY child_key, rows DESC;

-- label match counts. Exact and case-insensitive compare trim(amenity_raw).
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
fac AS (
    SELECT vi.id AS id, get_json_object(coalesce(vi.am, svc.am), '$.facilities') AS fac
    FROM vi
    LEFT JOIN svc ON vi.id = svc.id
),
child AS (
    SELECT id, child_key, get_json_object(fac, concat('$.', child_key)) AS v
    FROM fac
    LATERAL VIEW explode(json_object_keys(fac)) t AS child_key
    WHERE left(trim(fac), 1) = '{'
),
labels AS (
    SELECT id, child_key AS amenity_group, trim(label) AS amenity_raw
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
    SELECT trim(amenity_raw) AS amenity_raw, lower(trim(amenity_raw)) AS amenity_raw_ci
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
           l.amenity_raw,
           MAX(CASE WHEN d.amenity_raw IS NOT NULL THEN 1 ELSE 0 END) AS exact_hit,
           MAX(CASE WHEN ci.amenity_raw_ci IS NOT NULL THEN 1 ELSE 0 END) AS ci_hit
    FROM labels l
    LEFT JOIN ent e ON l.id = e.source_id
    LEFT JOIN dict d ON d.amenity_raw = l.amenity_raw
    LEFT JOIN dict ci ON ci.amenity_raw_ci = lower(l.amenity_raw)
    GROUP BY CASE
                 WHEN e.source_id IS NULL THEN '<no_entity>'
                 WHEN e.business_sector IS NULL THEN '<null>'
                 WHEN trim(e.business_sector) = '' THEN '<empty>'
                 ELSE e.business_sector
             END,
             l.amenity_raw
)
SELECT business_sector,
       COUNT(*) AS labels,
       SUM(exact_hit) AS exact_matched,
       SUM(CASE WHEN exact_hit = 0 THEN 1 ELSE 0 END) AS exact_unmatched,
       SUM(ci_hit) AS ci_matched,
       SUM(CASE WHEN ci_hit = 0 THEN 1 ELSE 0 END) AS ci_unmatched
FROM joined
GROUP BY business_sector
ORDER BY business_sector;

-- up to 50 labels with no exact amenity_raw match
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
fac AS (
    SELECT vi.id AS id, get_json_object(coalesce(vi.am, svc.am), '$.facilities') AS fac
    FROM vi
    LEFT JOIN svc ON vi.id = svc.id
),
child AS (
    SELECT id, child_key, get_json_object(fac, concat('$.', child_key)) AS v
    FROM fac
    LATERAL VIEW explode(json_object_keys(fac)) t AS child_key
    WHERE left(trim(fac), 1) = '{'
),
labels AS (
    SELECT id, child_key AS amenity_group, trim(label) AS amenity_raw
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
    SELECT trim(amenity_raw) AS amenity_raw
    FROM lh_vv_silver.dbo.ref_dictionary_amenities
    WHERE is_active = true
      AND lower(trim(source_name)) = 'partner'
)
SELECT CASE
           WHEN e.source_id IS NULL THEN '<no_entity>'
           WHEN e.business_sector IS NULL THEN '<null>'
           WHEN trim(e.business_sector) = '' THEN '<empty>'
           ELSE e.business_sector
       END AS business_sector,
       l.amenity_group,
       l.amenity_raw
FROM labels l
LEFT JOIN ent e ON l.id = e.source_id
WHERE NOT EXISTS (
    SELECT 1 FROM dict d WHERE d.amenity_raw = l.amenity_raw
)
GROUP BY CASE
             WHEN e.source_id IS NULL THEN '<no_entity>'
             WHEN e.business_sector IS NULL THEN '<null>'
             WHEN trim(e.business_sector) = '' THEN '<empty>'
             ELSE e.business_sector
         END,
         l.amenity_group,
         l.amenity_raw
ORDER BY business_sector, amenity_group, amenity_raw
LIMIT 50;
