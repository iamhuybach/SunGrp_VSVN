# Probe E3: đối chiếu registry partner đang chạy với schema và miền giá trị silver.
# Môi trường: Fabric DEV, notebook Spark. Gắn lh_vv_ctrl và lh_vv_silver. Chỉ đọc.
# Thứ tự: sau E1. Không phụ thuộc E2.
# Idempotent: không ghi bảng, không MERGE, không sửa registry.
# In 3 khối TSV. Không in điện thoại, email, tên, địa chỉ, payload.
# Lưu stdout vào evidence/results/e3_partner_registry_vs_silver.txt.

from pyspark.sql import functions as F

REG = "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry"
SILVER = "lh_vv_silver.dbo"

TIME_COLUMNS = {
    "created_at", "updated_at", "deleted_at", "last_updated_at",
    "last_in_activated_at", "last_verify_at", "valid_from", "valid_to",
    "expire_at", "usage_date", "check_in_date", "checkout_date",
    "departure_time", "arrival_time", "_ingested_at",
}


def cell(value):
    if value is None:
        return ""
    return str(value).replace("\t", " ").replace("\n", " ")


registry = spark.sql(f"""
    SELECT trg_tbl, trg_column, data_type, convert_rule, json_path,
           CAST(is_key AS STRING) AS is_key,
           CAST(key_order AS STRING) AS key_order,
           CAST(is_active AS STRING) AS is_active,
           CAST(column_order AS STRING) AS column_order
    FROM {REG}
    WHERE src_schema = 'lh_vv_bronze.dbo'
      AND src_tbl = 'partner_raw_data'
      AND src_object_schema = 'public'
    ORDER BY trg_tbl, column_order
""").collect()

by_table = {}
for row in registry:
    by_table.setdefault(row["trg_tbl"], []).append(row)

print("## registry_rows")
print("trg_tbl\ttrg_column\tdata_type\tconvert_rule\tjson_path\tis_key\tkey_order\tis_active\tcolumn_order")
for row in registry:
    print("\t".join(cell(row[name]) for name in (
        "trg_tbl", "trg_column", "data_type", "convert_rule", "json_path",
        "is_key", "key_order", "is_active", "column_order",
    )))

schema_lines = []
shape_lines = []

for trg_tbl in sorted(by_table):
    fq = f"{SILVER}.{trg_tbl}"
    try:
        described = spark.sql(f"DESCRIBE TABLE {fq}").collect()
    except Exception as exc:
        schema_lines.append(f"{trg_tbl}\t\t\t\t\tMISSING_TABLE {cell(exc)}")
        continue
    silver = {}
    for item in described:
        name = item["col_name"]
        if not name or name.startswith("#"):
            break
        silver[name] = item["data_type"]
    reg_names = {row["trg_column"]: row for row in by_table[trg_tbl]}
    for name, row in reg_names.items():
        if name not in silver:
            status = "MISSING_IN_SILVER"
            silver_type = ""
        elif silver[name].lower() != row["data_type"].lower():
            status = "TYPE_MISMATCH"
            silver_type = silver[name]
        else:
            status = "MATCH"
            silver_type = silver[name]
        schema_lines.append(
            f"{trg_tbl}\t{name}\t{cell(row['data_type'])}\t{cell(row['convert_rule'])}\t"
            f"{silver_type}\t{status}"
        )
    for name, silver_type in silver.items():
        if name not in reg_names:
            schema_lines.append(f"{trg_tbl}\t{name}\t\t\t{silver_type}\tEXTRA_IN_SILVER")

    present = [name for name in TIME_COLUMNS if name in silver]
    if not present:
        continue
    frame = spark.table(fq)
    aggs = [F.count(F.lit(1)).alias("__rows")]
    for name in present:
        column = F.col(name)
        aggs.append(F.sum(F.when(column.isNull(), 1).otherwise(0)).alias(f"{name}__null"))
        dtype = silver[name].lower()
        if dtype in {"bigint", "int", "smallint", "long", "integer"} or dtype.startswith("decimal"):
            aggs.append(F.sum(F.when(column == 0, 1).otherwise(0)).alias(f"{name}__zero"))
            aggs.append(F.min(column).cast("string").alias(f"{name}__min"))
            aggs.append(F.max(column).cast("string").alias(f"{name}__max"))
        else:
            aggs.append(F.lit(None).cast("long").alias(f"{name}__zero"))
            aggs.append(F.min(column).cast("string").alias(f"{name}__min"))
            aggs.append(F.max(column).cast("string").alias(f"{name}__max"))
    summary = frame.agg(*aggs).collect()[0]
    n_rows = summary["__rows"]
    for name in present:
        shape_lines.append(
            f"{trg_tbl}\t{name}\t{silver[name]}\t{n_rows}\t"
            f"{cell(summary[f'{name}__null'])}\t{cell(summary[f'{name}__zero'])}\t"
            f"{cell(summary[f'{name}__min'])}\t{cell(summary[f'{name}__max'])}"
        )

print("## schema_diff")
print("trg_tbl\tcolumn_name\tregistry_type\tconvert_rule\tsilver_type\tstatus")
print("\n".join(schema_lines))
print("## time_shapes")
print("trg_tbl\tcolumn_name\tsilver_type\tn_rows\tn_null\tn_zero\tv_min\tv_max")
print("\n".join(shape_lines))
