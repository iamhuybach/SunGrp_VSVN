# Env: Fabric DEV. Read-only PySpark. Do not run on Prod.
# 1. Open a notebook that can read workspace sgr_visitvn_dev (D-03, new model).
# 2. Paste this file into one cell. Leave TARGET_WORKSPACE = sgr_visitvn_dev.
# 3. Run the cell. It prints the column type and shape counts only.
# Pass: type string; non-null shapes only json_array_string, json_array_null_elem, or json_array_empty.
# not_json, blank, json_not_array, or json_array_other -> stop for user_decision.
# All three JSON-array counts 0 means the populated shape is still unobserved.
# Paste the full stdout at evidence/results/destination_id_non_legacy_shape.txt.
# Limit: counts only, at most 50 lines, no destination_id values, no UUIDs.
# Re-run: schema_of_json cannot take a column here. This cell classifies with rlike.

from pyspark.sql import functions as F

TARGET_WORKSPACE = "sgr_visitvn_dev"
FQ = f"{TARGET_WORKSPACE}.lh_vv_gold.dbo.gld_srv_poi_info"
STR_ELEM = r'"(?:[^"\\]|\\.)*"'
ARRAY_EMPTY = r"^\[\s*\]$"
ARRAY_STRINGS = rf"^\[{STR_ELEM}(?:\s*,\s*{STR_ELEM})*\]$"
ARRAY_STR_OR_NULL = rf"^\[(?:null|{STR_ELEM})(?:\s*,\s*(?:null|{STR_ELEM}))*\]$"

if not spark.catalog.tableExists(FQ):
    raise RuntimeError(f"missing table {FQ}")

fields = {item.name: item for item in spark.table(FQ).schema.fields}
if "destination_id" not in fields or "load_origin" not in fields:
    raise RuntimeError(
        "missing column "
        f"destination_id={'destination_id' in fields} load_origin={'load_origin' in fields}"
    )

dest = fields["destination_id"]
df = spark.table(FQ)
non = df.where(F.col("load_origin").isNull() | (F.col("load_origin") != F.lit("LEGACY_INIT")))
trimmed = F.trim(F.col("destination_id"))
shape = (
    F.when(F.col("destination_id").isNull(), F.lit("null"))
    .when(trimmed == "", F.lit("blank"))
    .when(trimmed.rlike(ARRAY_EMPTY), F.lit("json_array_empty"))
    .when(trimmed.rlike(ARRAY_STRINGS), F.lit("json_array_string"))
    .when(trimmed.rlike(ARRAY_STR_OR_NULL), F.lit("json_array_null_elem"))
    .when(trimmed.startswith("["), F.lit("json_array_other"))
    .when(
        trimmed.startswith("{") | trimmed.startswith('"') | trimmed.rlike(r"^-?\d")
        | trimmed.isin("true", "false", "null"),
        F.lit("json_not_array"),
    )
    .otherwise(F.lit("not_json"))
)

print(f"column_type\tdestination_id\t{dest.dataType.simpleString()}\tnullable={dest.nullable}")
print("load_origin\tcount")
origin_rows = (
    df.groupBy(F.col("load_origin").alias("load_origin"))
    .count()
    .orderBy(F.desc("count"))
    .limit(20)
    .collect()
)
for row in origin_rows:
    print(f"{row['load_origin']}\t{row['count']}")

print("shape\tcount")
shape_rows = (
    non.select(shape.alias("shape"))
    .groupBy("shape")
    .count()
    .orderBy(F.desc("count"))
    .limit(40)
    .collect()
)
for row in shape_rows:
    print(f"{row['shape']}\t{row['count']}")

print(f"non_legacy_rows\t{non.count()}")
populated = sum(row["count"] for row in shape_rows if row["shape"] == "json_array_string")
null_elem = sum(row["count"] for row in shape_rows if row["shape"] == "json_array_null_elem")
empty_arrays = sum(row["count"] for row in shape_rows if row["shape"] == "json_array_empty")
bad = {"blank", "not_json", "json_not_array", "json_array_other"}
bad_count = sum(row["count"] for row in shape_rows if row["shape"] in bad)
observed = populated + null_elem + empty_arrays
if dest.dataType.simpleString() != "string" or bad_count:
    verdict = "stop_user_decision"
elif observed == 0:
    verdict = "populated_shape_unobserved"
else:
    verdict = "keep_string"
print(
    f"verdict\t{verdict}\tjson_array_string={populated}\tjson_array_null_elem={null_elem}"
    f"\tjson_array_empty={empty_arrays}\tbad={bad_count}"
)
