# Môi trường: notebook Fabric DEV, workspace sgr_visitvn_dev, một cell Python, chỉ đọc. Không tham số.
# Gộp P-DEST, P-AI, P-LEGDEST. SQL là mục 13 của architecture.md. <ws> = sgr_visitvn_dev.
# Thứ tự: P-DEST-1, P-DEST-2, P-AI-1, P-AI-2, P-LEGDEST-1, P-LEGDEST-2.
# Cần đọc được lh_vv_bronze, lh_vv_silver, sgr_visitvn_dev.lh_vv_gold và sgr_visitvn_prd_batch.lh_vv_gold.
# Đạt: stdout có sáu SECTION và sáu END. ERROR trên một section là fail của section đó.
# Dán: .ai/tasks/20261126-legacy-init-enriched-cols-and-dest-portal/evidence/results/p_gaps.txt
# Chỉ số đếm và mã lang. Không địa chỉ, story, tips, id. Tối đa 50 dòng mỗi section.
# Chạy lại an toàn: script chỉ đọc, không ghi bảng.

def _run(name, sql):
    print("SECTION\t" + name)
    try:
        frame = spark.sql(sql)
        rows = frame.limit(50).collect()
        print("COLUMNS\t" + "\t".join(frame.columns))
        for row in rows:
            print("ROW\t" + "\t".join("" if value is None else str(value) for value in row))
        print("END\t" + name + "\t" + str(len(rows)))
    except Exception as exc:
        print("ERROR\t" + name + "\t" + type(exc).__name__ + "\t" + str(exc).splitlines()[0][:240])

_run("P-DEST-1", """
WITH ev AS (
  SELECT poi_id, CAST(version AS BIGINT) v, CAST(EventProcessedUtcTime AS TIMESTAMP) ts, CAST(event_id AS STRING) eid,
         get_json_object(data, '$.destinations') blk
  FROM lh_vv_bronze.dbo.brz_enrichment_result WHERE trim(event_type) = 'DESTINATION'),
s AS (SELECT poi_id, _src_version, _event_processed_at, _event_id, destination_id, destination_name
      FROM lh_vv_silver.dbo.slv_enr_poi_destination),
m AS (SELECT s.*, ev.blk, ev.eid IS NOT NULL has_ev,
        to_json(transform(from_json(ev.blk,'array<struct<id:string,name:string,strapi_document_id:string>>'), x -> x.id)) id_p,
        to_json(transform(from_json(ev.blk,'array<struct<id:string,name:string,strapi_document_id:string>>'), x -> x.name)) name_p,
        to_json(transform(from_json(ev.blk,'array<struct<id:string,name:string,strapi_document_id:string>>'), x -> x.strapi_document_id)) sd_p
      FROM s LEFT JOIN ev ON ev.poi_id = s.poi_id AND ev.v <=> s._src_version
                         AND ev.ts <=> s._event_processed_at AND ev.eid <=> s._event_id)
SELECT count(DISTINCT poi_id) silver_n, count(*) joined_rows,
       count_if(NOT has_ev) no_event_n,
       count_if(has_ev AND id_p <=> destination_id) id_eq_n,
       count_if(has_ev AND name_p <=> destination_name) name_eq_n,
       count_if(has_ev AND blk IS NULL) blk_null_n,
       count_if(has_ev AND sd_p IS NOT NULL AND NOT exists(from_json(sd_p,'array<string>'), x -> x IS NULL)) sd_full_n,
       count_if(has_ev AND exists(from_json(sd_p,'array<string>'), x -> x IS NULL)
                AND exists(from_json(sd_p,'array<string>'), x -> x IS NOT NULL)) sd_partial_n,
       count_if(has_ev AND sd_p IS NOT NULL AND NOT exists(from_json(sd_p,'array<string>'), x -> x IS NOT NULL)) sd_none_n
FROM m
""")

_run("P-DEST-2", r"""
SELECT count(*) elem_n, count_if(e IS NULL) elem_null_n,
       count_if(e RLIKE '"strapi_document_id"\s*:\s*"') sd_string_n,
       count_if(e RLIKE '"strapi_document_id"\s*:\s*-?[0-9]') sd_number_n,
       count_if(e RLIKE '"id"\s*:\s*"') id_string_n, count_if(e RLIKE '"id"\s*:\s*-?[0-9]') id_number_n,
       min(CASE WHEN e RLIKE '"strapi_document_id"' THEN ts END) sd_first_seen
FROM (SELECT CAST(EventProcessedUtcTime AS TIMESTAMP) ts,
             explode(from_json(get_json_object(data,'$.destinations'),'array<string>')) e
      FROM lh_vv_bronze.dbo.brz_enrichment_result WHERE trim(event_type) = 'DESTINATION')
""")

_run("P-AI-1", """
WITH ai AS (SELECT * FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.ai_enriched_poi),
pm AS (SELECT poi_id, lang FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master),
mp AS (SELECT legacy_poi_id, lang, poi_id, poi_id_status FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map),
nid AS (SELECT DISTINCT poi_id FROM mp)
SELECT count(*) ai_n, count_if(pm.poi_id IS NOT NULL) pm_hit_n, count_if(pm.lang <=> ai.lang AND pm.poi_id IS NOT NULL) pm_same_lang_n,
       count_if(mp.legacy_poi_id IS NOT NULL) map_hit_n, count_if(mp.lang <=> ai.lang AND mp.legacy_poi_id IS NOT NULL) map_same_lang_n,
       count_if(mp.poi_id_status = 'OK') map_ok_n, count_if(nid.poi_id IS NOT NULL) new_id_hit_n,
       count_if(ai.price_min > ai.price_max) price_inverted_n
FROM ai LEFT JOIN pm ON pm.poi_id = ai.poi_id LEFT JOIN mp ON mp.legacy_poi_id = ai.poi_id
LEFT JOIN nid ON nid.poi_id = ai.poi_id
""")

_run("P-AI-2", """
SELECT ai.lang, count(*) n, count_if(ai.story IS NOT NULL) story_n, count_if(ai.local_tips_or_neighborhood IS NOT NULL) tips_n,
       count_if(ai.address_line_2 IS NOT NULL) addr2_n, count_if(ai.price_level IS NOT NULL) price_n,
       count_if(g.load_origin = 'LEGACY_INIT') ml_legacy_n, count_if(g.poi_id IS NOT NULL AND g.load_origin IS NULL) ml_pipeline_n
FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.ai_enriched_poi ai
JOIN sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map mp ON mp.legacy_poi_id = ai.poi_id
LEFT JOIN sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang g ON g.poi_id = mp.poi_id AND g.lang = ai.lang
GROUP BY ai.lang
""")

_run("P-LEGDEST-1", """
WITH leg AS (SELECT DISTINCT v FROM (SELECT explode(from_json(destination_ids,'array<string>')) v
             FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master WHERE destination_ids IS NOT NULL)),
br AS (SELECT explode(from_json(get_json_object(data,'$.destinations'),'array<struct<id:string,strapi_document_id:string>>')) d
       FROM lh_vv_bronze.dbo.brz_enrichment_result WHERE trim(event_type) = 'DESTINATION'),
ids AS (SELECT DISTINCT d.id v FROM br), sds AS (SELECT DISTINCT d.strapi_document_id v FROM br)
SELECT count(*) leg_values, count_if(ids.v IS NOT NULL) in_portal_id, count_if(sds.v IS NOT NULL) in_strapi
FROM leg LEFT JOIN ids ON ids.v = leg.v LEFT JOIN sds ON sds.v = leg.v
""")

_run("P-LEGDEST-2", """
SELECT load_origin, count(*) n, count_if(destination_id IS NOT NULL) dest_n
FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info GROUP BY load_origin
""")
