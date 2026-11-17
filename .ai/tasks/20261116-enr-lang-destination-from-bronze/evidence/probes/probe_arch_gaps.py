# Environment: Fabric DEV. Notebook that can read lh_vv_bronze, lh_vv_silver, and lh_vv_gold. Read-only.
# Prerequisite: the three lakehouses are attached. Run this file as one cell. Paste the whole printout.
# Result: .ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_arch_gaps.txt
# Limits: counts and Delta protocol only. No addresses, names, or payload text. At most 50 rows per section.
# Decision: P-1 row counts and gold Delta protocol; P-3 bronze poi_id overlap with entity; P-4 null versus blank address fields.
# Pass: P-1 prints four counts and gold minReaderVersion, minWriterVersion, properties. P-3 prints a group for LANG and DESTINATION. P-4 prints null and blank counts.
# Fail: a section raises. Paste the error text too. A silver count above 0 is a completed result and blocks a recreate.
# Do not select data values.

from pyspark.sql import functions as F

LIMIT = 50


def show(title, frame):
    print(f"\n## {title}")
    rows = frame.limit(LIMIT).collect()
    if not rows:
        print("(0 rows)")
        return
    headers = list(rows[0].asDict().keys())
    print("\t".join(headers))
    for row in rows:
        values = row.asDict()
        print("\t".join("" if values[name] is None else str(values[name]) for name in headers))


counts = spark.sql("""
SELECT 'slv_ml' AS tbl, COUNT(*) AS n FROM lh_vv_silver.dbo.slv_enr_poi_info_multi_lang
UNION ALL SELECT 'slv_dest', COUNT(*) FROM lh_vv_silver.dbo.slv_enr_poi_destination
UNION ALL SELECT 'gld_ml', COUNT(*) FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang
UNION ALL SELECT 'gld_ml_deleted', COUNT(*) FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang WHERE deleted_at IS NOT NULL
""")
show("P1_COUNTS", counts)

detail = spark.sql("DESCRIBE DETAIL lh_vv_gold.dbo.gld_srv_poi_multi_lang")
keep = [name for name in ("minReaderVersion", "minWriterVersion", "properties") if name in detail.columns]
show("P1_GOLD_DETAIL", detail.select(*keep) if keep else detail)

overlap = spark.sql("""
WITH b AS (
  SELECT DISTINCT trim(event_type) AS et, poi_id
  FROM lh_vv_bronze.dbo.brz_enrichment_result
)
SELECT b.et, lower(trim(e.source_name)) AS src, COUNT(*) AS n, COUNT(e.poi_id) AS matched
FROM b
LEFT JOIN lh_vv_silver.dbo.slv_poi_entity_non_enrich e ON e.poi_id = b.poi_id
GROUP BY b.et, lower(trim(e.source_name))
ORDER BY b.et, src
""")
show("P3_OVERLAP", overlap)

blank_json = spark.sql("""
SELECT p,
       SUM(CASE WHEN v IS NULL THEN 1 ELSE 0 END) AS null_or_missing,
       SUM(CASE WHEN v IS NOT NULL AND trim(v) = '' THEN 1 ELSE 0 END) AS blank,
       COUNT(*) AS n
FROM (
  SELECT data FROM lh_vv_bronze.dbo.brz_enrichment_result WHERE trim(event_type) = 'DESTINATION'
) d
LATERAL VIEW explode(map(
  'formatted_address', get_json_object(data, '$.address.new.formatted_address'),
  'ward_with_type', get_json_object(data, '$.address.new.ward.name_with_type'),
  'city_with_type', get_json_object(data, '$.address.new.province.name_with_type'),
  'request_address', get_json_object(data, '$.request.address')
)) m AS p, v
GROUP BY p
ORDER BY p
""")
show("P4_DESTINATION_BLANK", blank_json)

blank_entity = spark.sql("""
SELECT lower(trim(source_name)) AS src, COUNT(*) AS n,
       SUM(CASE WHEN house_number IS NULL THEN 1 ELSE 0 END) AS hn_null,
       SUM(CASE WHEN trim(house_number) = '' THEN 1 ELSE 0 END) AS hn_blank,
       SUM(CASE WHEN street IS NULL THEN 1 ELSE 0 END) AS st_null,
       SUM(CASE WHEN trim(street) = '' THEN 1 ELSE 0 END) AS st_blank
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich
GROUP BY lower(trim(source_name))
ORDER BY src
""")
show("P4_ENTITY_BLANK", blank_entity)
