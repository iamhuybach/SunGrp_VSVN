# Environment: Fabric DEV. Paste this file into one notebook cell. Read-only.
# Run it after NB_CREATE_DDL cell srvpoipy has been run twice.
# Pass: edge_n is 6, each n is 1, and each line matches one expected payload below.
# Fail: edge_n is not 6, any n is not 1, a payload field differs, or a listed column is missing.
# Prerequisite: srvpoipy completed twice on lh_vv_ctrl, lh_vv_silver, lh_vv_gold.
# Save: .ai/tasks/20261024-gld-srv-poi-from-mapping/evidence/results/gld_srv_edge_payload.txt
# Limits: paste the count lines and the payload lines only. No personal data, no table samples.

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
PL = "PL_VV_TRANS_SLV_TO_GLD_30P"
SLV, GLD = "lh_vv_silver.dbo", "lh_vv_gold.dbo"
EXPECT = [
    (PL, SLV, "slv_enr_poi_info_multi_lang", GLD, "gld_srv_poi_multi_lang", 1, 1, "RECOMPUTE", "NB_GLD_SRV_POI_MULTI_LANG"),
    (PL, SLV, "slv_poi_entity_non_enrich", GLD, "gld_srv_poi_multi_lang", 1, 1, "RECOMPUTE", "NB_GLD_SRV_POI_MULTI_LANG"),
    (PL, SLV, "slv_pn_business_service_i18ns", GLD, "gld_srv_poi_multi_lang", 1, 1, "RECOMPUTE", "NB_GLD_SRV_POI_MULTI_LANG"),
    (PL, SLV, "slv_poi_entity_non_enrich", GLD, "gld_srv_poi_info", 1, 1, "RECOMPUTE", "NB_GLD_SRV_POI_INFO"),
    (PL, SLV, "slv_enr_poi_destination", GLD, "gld_srv_poi_info", 1, 1, "RECOMPUTE", "NB_GLD_SRV_POI_INFO"),
    (PL, SLV, "slv_enr_poi_info_multi_lang", GLD, "gld_srv_poi_info", 1, 1, "RECOMPUTE", "NB_GLD_SRV_POI_INFO"),
]
FIELDS = ("pl_name", "src_schema", "src_tbl", "trg_schema", "trg_tbl", "is_active", "priority", "load_mode", "nb_name")
rows = spark.sql(f"""
SELECT pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name, count(*) AS n
FROM {CFG}
WHERE pl_name = '{PL}'
GROUP BY pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name
ORDER BY trg_tbl, src_tbl
""").collect()
print("edge_n", len(rows))
got = []
for row in rows:
    item = tuple(row[name] for name in FIELDS)
    got.append(item)
    print("edge", "|".join(str(part) for part in item), "n", row["n"])
print("payload_match", sorted(got) == sorted(EXPECT) and all(row["n"] == 1 for row in rows))

checks = {
    f"{SLV}.slv_enr_poi_destination": [
        "poi_id", "street", "ward", "district", "city", "full_address", "created_at", "updated_at",
        "destination_id", "country_code", "postal_code", "lat", "lng",
    ],
    f"{GLD}.gld_srv_poi_multi_lang": [
        "poi_id", "lang", "source_name", "time_to_spend", "best_time", "cost_vnd", "description",
        "row_hash", "created_at", "updated_at", "deleted_at",
    ],
    f"{GLD}.gld_srv_poi_info": [
        "poi_id", "poi_name", "source_name", "business_sector", "business_category", "subcategory_tags",
        "destination_id", "full_address", "street", "ward", "district", "city", "country_code", "postal_code",
        "lat", "lng", "phone", "email", "website_url", "operating_status", "is_verified", "is_recommended",
        "is_bookable", "operating_hours", "holiday_exceptions", "row_hash", "created_at", "updated_at", "deleted_at",
    ],
}
for fq, names in checks.items():
    got_names = [field.name for field in spark.table(fq).schema.fields] if spark.catalog.tableExists(fq) else None
    print("cols", fq, "match", got_names == names)
