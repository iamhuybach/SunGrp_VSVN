# Fabric DEV. Notebook Spark đã gắn được lh_vv_silver, lh_vv_gold, lh_vv_ctrl.
# Chỉ đọc. Quyết định D-PEH-10: R1–R8 của EXEC_1.
# Dán toàn bộ stdout vào Kết quả người dùng ghi nhận. Tối đa 50 dòng mỗi bảng. Không chép phone/email.

import json

EXEC_1 = "525a64db-8c5a-46ab-acf2-2a68330bf384"
E1 = 4
V0 = 7


def show(title, sql):
    print("\n==== " + title + " ====")
    spark.sql(sql).show(50, truncate=False)


show("R1 entity", "DESCRIBE TABLE lh_vv_silver.dbo.slv_poi_entity_non_enrich")
show("R1 edges", """
SELECT id, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND src_schema = 'lh_vv_silver.dbo'
  AND src_tbl = 'slv_3p_poi_opening_hours'
ORDER BY trg_tbl
""")
show("R1 gold", "DESCRIBE TABLE lh_vv_gold.enr.gld_enr_poi_info")
show("R2", f"""
SELECT trg_tbl, status, priority, entity_rows, inserted_rows, updated_rows, deactivated_rows, trg_version,
       get_json_object(qg_json, '$.inbox') AS inbox,
       get_json_object(qg_json, '$.blocks') AS blocks,
       get_json_object(qg_json, '$.warns') AS warns,
       get_json_object(qg_json, '$.metrics.opening_hours_text_mismatch') AS oh_mismatch,
       get_json_object(qg_json, '$.metrics.google_with_hours') AS google_with_hours,
       get_json_object(qg_json, '$.metrics.partner_with_hours') AS partner_with_hours,
       get_json_object(qg_json, '$.metrics.google_with_phone') AS google_with_phone,
       get_json_object(qg_json, '$.metrics.partner_with_phone') AS partner_with_phone,
       get_json_object(qg_json, '$.metrics.partner_with_email') AS partner_with_email,
       get_json_object(qg_json, '$.metrics.partner_with_holiday') AS partner_with_holiday,
       substr(error_message, 1, 500) AS error_message,
       substr(qg_json, 1, 4000) AS qg_head
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE exec_id = '{EXEC_1}'
ORDER BY priority, trg_tbl
LIMIT 50
""")
show("R3", f"""
SELECT trg_version,
       get_json_object(src_versions_json, '$.slv_3p_poi_opening_hours.v') AS v_hours,
       get_json_object(src_versions_json, '$.slv_pn_business_service_i18ns.v') AS v_i18n,
       get_json_object(src_versions_json, '$.slv_pn_business_services.v') AS v_svc,
       get_json_object(src_versions_json, '$.slv_3p_poi_contact.v') AS v_contact,
       substr(src_versions_json, 1, 4000) AS src_versions_json
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE exec_id = '{EXEC_1}' AND trg_tbl = 'slv_poi_entity_non_enrich'
""")

raw = spark.sql(f"""
SELECT src_versions_json
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE exec_id = '{EXEC_1}' AND trg_tbl = 'slv_poi_entity_non_enrich'
""").first()["src_versions_json"]
payload = json.loads(raw)


def ver(name):
    for key, val in payload.items():
        if key == name or key.endswith("." + name):
            return int(val["v"])
    raise RuntimeError(name)


v_hours = ver("slv_3p_poi_opening_hours")
v_i18n = ver("slv_pn_business_service_i18ns")
v_svc = ver("slv_pn_business_services")
v_contact = ver("slv_3p_poi_contact")
print(f"\n==== versions E1={E1} V0={V0} v_hours={v_hours} v_i18n={v_i18n} v_svc={v_svc} v_contact={v_contact} ====")

show("R4 by source", f"""
SELECT source_name, count(*) AS n, count_if(deleted_at IS NULL) AS n_live
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF {E1}
GROUP BY source_name
ORDER BY source_name
LIMIT 50
""")
show("R4 grain", f"""
SELECT count(*) AS n, count(DISTINCT poi_id) AS n_poi
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF {E1}
""")
show("R5", f"""
SELECT count_if(e.email IS NOT NULL OR e.holiday_exceptions IS NOT NULL) AS google_email_holiday_not_null,
       count_if(NOT (e.phone <=> c.phone)) AS google_phone_mismatch
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF {E1} e
LEFT JOIN (SELECT poi_id, phone FROM lh_vv_silver.dbo.slv_3p_poi_contact VERSION AS OF {v_contact}
           WHERE poi_id IS NOT NULL) c ON c.poi_id = e.poi_id
WHERE e.deleted_at IS NULL AND lower(trim(e.source_name)) = 'google'
""")
show("R6 partner", f"""
WITH s AS (SELECT id, phone, email
           FROM lh_vv_silver.dbo.slv_pn_business_services VERSION AS OF {v_svc}
           WHERE NOT coalesce(deleted, false)),
     i AS (SELECT business_service_id,
                  get_json_object(amentities, '$.policies.operating_hours') AS hours,
                  get_json_object(amentities, '$.policies.holiday_exceptions') AS holiday
           FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns VERSION AS OF {v_i18n}
           WHERE locale = 'vi' AND NOT coalesce(deleted, false))
SELECT count_if(NOT (e.phone <=> s.phone)) AS partner_phone_mismatch,
       count_if(NOT (e.email <=> s.email)) AS partner_email_mismatch,
       count_if(NOT (e.holiday_exceptions <=> i.holiday)) AS partner_holiday_mismatch,
       count_if(NOT (e.opening_hours_text <=> i.hours)) AS partner_hours_mismatch
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF {E1} e
LEFT JOIN s ON s.id = e.source_id
LEFT JOIN i ON i.business_service_id = e.source_id
WHERE e.deleted_at IS NULL AND lower(trim(e.source_name)) = 'partner'
""")
show("R6 google hours", f"""
SELECT count(*) AS google_hours_mismatch
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF {E1} e
LEFT JOIN lh_vv_silver.dbo.slv_3p_poi_opening_hours VERSION AS OF {v_hours} oh ON oh.poi_id = e.poi_id
WHERE e.deleted_at IS NULL AND lower(trim(e.source_name)) = 'google'
  AND NOT (e.opening_hours_text <=> oh.periods_json)
""")
show("R7", f"""
SELECT count_if(coalesce(phone, email, holiday_exceptions) IS NOT NULL) AS other_detail_not_null,
       count_if(opening_hours_text IS NOT NULL) AS other_hours_not_null
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF {E1}
WHERE deleted_at IS NULL
  AND coalesce(lower(trim(source_name)), '') NOT IN ('google', 'partner')
""")
show("R8 gold = silver", """
WITH g AS (SELECT poi_id, opening_hours_text,
                  row_number() OVER (PARTITION BY poi_id ORDER BY updated_at DESC, created_at DESC) AS rn
           FROM lh_vv_gold.enr.gld_enr_poi_info)
SELECT count(*) AS gold_ne_silver FROM g JOIN lh_vv_silver.dbo.slv_poi_entity_non_enrich e
  ON e.poi_id = g.poi_id AND e.deleted_at IS NULL
WHERE g.rn = 1 AND NOT (g.opening_hours_text <=> e.opening_hours_text)
""")
show("R8 gold vs V0", f"""
WITH o AS (SELECT poi_id, opening_hours_text,
                  row_number() OVER (PARTITION BY poi_id ORDER BY updated_at DESC, created_at DESC) AS rn
           FROM lh_vv_gold.enr.gld_enr_poi_info VERSION AS OF {V0}),
     n AS (SELECT poi_id, opening_hours_text,
                  row_number() OVER (PARTITION BY poi_id ORDER BY updated_at DESC, created_at DESC) AS rn
           FROM lh_vv_gold.enr.gld_enr_poi_info)
SELECT count(*) AS gold_changed_vs_v0 FROM o JOIN n ON o.poi_id = n.poi_id
WHERE o.rn = 1 AND n.rn = 1 AND NOT (o.opening_hours_text <=> n.opening_hours_text)
""")
