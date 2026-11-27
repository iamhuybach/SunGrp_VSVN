# Fabric DEV. R2 rồi R3. Ba bảng L2 đã có sau RUN 2026-11-27, version 1.
# Không chạy lại RUN lần đầu. Không in giá.

import json

spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
NODES = ("NB_SLV_PN_PRODUCT_SALE", "NB_SLV_PN_HOTEL_ROOM_OFFER", "NB_SLV_PN_HOTEL_RATE_OFFER")
TARGETS = ("slv_pn_product_sale", "slv_pn_hotel_room_offer", "slv_pn_hotel_rate_offer")


def version_of(name):
    row = spark.sql(f"DESCRIBE HISTORY lh_vv_silver.dbo.{name} LIMIT 1").select("version").first()
    return None if row is None else int(row["version"])


def run_nb(nb):
    args = {
        "p_exec_id": "", "p_run_id": "", "p_pl_name": "", "p_trg_fq": "",
        "p_pinned_json": "", "p_mode": "RUN", "p_force": "true", "p_history_limit": "1000",
        "useRootDefaultLakehouse": True,
    }
    print(nb, notebookutils.notebook.run(nb, 14400, args))


print("== R2 before")
before = {name: version_of(name) for name in TARGETS}
print(before)
print("== R2 run")
for nb in NODES:
    run_nb(nb)
print("== R2 after")
for name in TARGETS:
    after = version_of(name)
    print(name, "V_BEFORE", before[name], "V_AFTER", after, "same" if after == before[name] else "CHANGED")

print("== qg")
rows = spark.sql("""
SELECT trg_tbl, status, inserted_rows, updated_rows, deactivated_rows, qg_json
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_tbl IN ('slv_pn_product_sale', 'slv_pn_hotel_room_offer', 'slv_pn_hotel_rate_offer')
  AND started_at > current_timestamp() - INTERVAL 2 HOURS
ORDER BY started_at DESC
LIMIT 6
""").collect()
for row in rows:
    qg = json.loads(row["qg_json"] or "{}")
    print(row["trg_tbl"], row["status"], row["inserted_rows"], row["updated_rows"], row["deactivated_rows"],
          "blocks", qg.get("blocks"), "delete_flag", qg.get("delete_flag"), "warns", qg.get("warns"))

print("== R3")
TABLES = {
    "slv_pn_product_sale": ("product_id", "slv_pn_products", ("product_post_id", "original_price", "marketing_price", "markup_percent")),
    "slv_pn_hotel_room_offer": ("room_type_id", "slv_pn_hotel_room_types", ()),
    "slv_pn_hotel_rate_offer": ("rate_plan_id", "slv_pn_hotel_rate_plans", ()),
}
SLV = "lh_vv_silver.dbo"
for target, (key, source, prices) in TABLES.items():
    fq, src = f"{SLV}.{target}", f"{SLV}.{source}"
    cols = [field.name for field in spark.table(fq).schema.fields]
    print(target, "columns", cols)
    print(target, "_is_deleted", "_is_deleted" in cols)
    checks = {
        "l1_missing_on_l2": f"SELECT COUNT(*) AS n FROM {src} s LEFT ANTI JOIN {fq} t ON s.id = t.{key}",
        "deleted_at_set_but_l1_live": f"""
            SELECT COUNT(*) AS n FROM {fq} t JOIN {src} s ON s.id = t.{key}
            WHERE t.deleted_at IS NOT NULL AND s.deleted = false""",
        "deleted_at_null_but_l1_deleted": f"""
            SELECT COUNT(*) AS n FROM {fq} t JOIN {src} s ON s.id = t.{key}
            WHERE t.deleted_at IS NULL AND s.deleted = true""",
        "updated_before_created": f"SELECT COUNT(*) AS n FROM {fq} WHERE updated_at < created_at",
    }
    if target != "slv_pn_hotel_rate_offer":
        checks["is_bookable_null"] = f"SELECT COUNT(*) AS n FROM {fq} WHERE is_bookable IS NULL"
    if prices:
        pred = " OR ".join(f"{col} IS NOT NULL" for col in prices)
        checks["price_without_post"] = f"SELECT COUNT(*) AS n FROM {fq} WHERE product_post_id IS NULL AND ({pred})"
    for label, sql in checks.items():
        print(target, label, spark.sql(sql).first()["n"])

print("== K3")
try:
    n = spark.sql("""
        SELECT COUNT(*) AS n
        FROM lh_vv_silver.dbo.slv_pn_hotel_rate_offer t
        JOIN lh_vv_silver.dbo.slv_pn_hotel_rate_plans s ON s.id = t.rate_plan_id
        WHERE NOT (t.valid_from <=> s.valid_from) OR NOT (t.valid_to <=> s.valid_to)
    """).first()["n"]
    print("valid_from_valid_to_mismatch", n)
except Exception as exc:
    print("K3 FAIL", type(exc).__name__, str(exc)[:300])
