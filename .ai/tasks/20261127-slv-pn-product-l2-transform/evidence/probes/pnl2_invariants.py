# Probe R3 — đếm bất biến Silver L2. Chỉ đọc. Fabric DEV.
# Không in quá 50 dòng. Không in dữ liệu cá nhân.
# Dán kết quả vào evidence/results/pnl2_invariants.txt
# Pass: mọi count = 0, và mỗi bảng không có cột _is_deleted.

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
        "l1_missing_on_l2": f"""
            SELECT COUNT(*) AS n FROM {src} s
            LEFT ANTI JOIN {fq} t ON s.id = t.{key}
        """,
        "deleted_at_set_but_l1_live": f"""
            SELECT COUNT(*) AS n FROM {fq} t
            JOIN {src} s ON s.id = t.{key}
            WHERE t.deleted_at IS NOT NULL AND s.deleted = false
        """,
        "deleted_at_null_but_l1_deleted": f"""
            SELECT COUNT(*) AS n FROM {fq} t
            JOIN {src} s ON s.id = t.{key}
            WHERE t.deleted_at IS NULL AND s.deleted = true
        """,
        "is_bookable_null": f"SELECT COUNT(*) AS n FROM {fq} WHERE is_bookable IS NULL"
        if target != "slv_pn_hotel_rate_offer" else None,
        "updated_before_created": f"SELECT COUNT(*) AS n FROM {fq} WHERE updated_at < created_at",
    }
    if prices:
        pred = " OR ".join(f"{col} IS NOT NULL" for col in prices)
        checks["price_without_post"] = f"SELECT COUNT(*) AS n FROM {fq} WHERE product_post_id IS NULL AND ({pred})"
    for name, sql in checks.items():
        if sql is None:
            continue
        print(target, name, spark.sql(sql).first()["n"])
