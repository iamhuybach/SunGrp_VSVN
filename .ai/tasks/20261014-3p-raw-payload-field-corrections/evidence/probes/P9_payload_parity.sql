-- P9: normalized_payload parity. Fabric DEV, read-only.
-- Save counts only to evidence/results/P9_payload_parity.md.
WITH b AS (
  SELECT raw_payload AS r, normalized_payload AS n
  FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
  WHERE lower(trim(source_name)) = 'google'
),
p AS (
  SELECT r, n,
         from_json(r, 'map<string,string>') AS mr,
         from_json(n, 'map<string,string>') AS mn,
         from_json(get_json_object(r, '$.photos'), 'array<string>') AS rp,
         from_json(get_json_object(n, '$.photos'), 'array<string>') AS np
  FROM b
)
SELECT count(*) AS docs,
  sum(CASE WHEN (n IS NULL OR trim(n) = '') AND r IS NOT NULL AND trim(r) <> ''
      THEN 1 ELSE 0 END) AS norm_blank_when_raw_ok,
  sum(CASE WHEN NOT (
        array_sort(map_entries(map_filter(mr, (k, v) -> k <> 'photos')))
        <=> array_sort(map_entries(map_filter(mn, (k, v) -> k <> 'photos')))
      ) THEN 1 ELSE 0 END) AS top_mismatch_docs,
  sum(CASE WHEN NOT (size(rp) <=> size(np))
      THEN 1 ELSE 0 END) AS photo_size_mismatch_docs,
  sum(size(filter(sequence(1, greatest(size(np), 1)), i ->
      i <= size(np) AND NOT (
        array_sort(map_entries(from_json(try_element_at(rp, i), 'map<string,string>')))
        <=> array_sort(map_entries(map_filter(
              from_json(try_element_at(np, i), 'map<string,string>'),
              (k, v) -> k <> 'blob_url'
            )))
      )))) AS photo_elem_mismatch,
  sum(size(filter(coalesce(np, array()), e ->
      NOT array_contains(map_keys(from_json(e, 'map<string,string>')), 'blob_url')
  ))) AS photo_no_blob_key,
  sum(size(filter(coalesce(np, array()), e ->
      get_json_object(e, '$.blob_url') RLIKE '[?]|sig='
  ))) AS blob_signed
FROM p;

-- Chỉ chạy câu dưới nếu top_mismatch_docs > 0. Tối đa 50 dòng, chỉ tên khóa.
WITH b AS (
  SELECT raw_payload AS r, normalized_payload AS n
  FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
  WHERE lower(trim(source_name)) = 'google'
),
p AS (
  SELECT from_json(r, 'map<string,string>') AS mr,
         from_json(n, 'map<string,string>') AS mn
  FROM b
)
SELECT k, count(*) AS docs
FROM p
LATERAL VIEW explode(array_union(map_keys(mr), map_keys(mn))) x AS k
WHERE k <> 'photos' AND NOT (mr[k] <=> mn[k])
GROUP BY k
ORDER BY docs DESC
LIMIT 50;
