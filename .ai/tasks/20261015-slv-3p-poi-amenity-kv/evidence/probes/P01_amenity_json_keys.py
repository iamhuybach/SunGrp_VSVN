# Probe: P01_amenity_json_keys
# Environment: Fabric DEV. Attach lakehouse lh_vv_silver. Read-only.
# Table: lh_vv_silver.dbo.slv_3p_poi_amenity
# Decision: which string column has JSON key facilities or terms_and_conditions.
# Pass: exactly one string column has $.facilities or $.terms_and_conditions.
# Fail: no such column, or more than one column.
# Output: column, type, key path, row count. No JSON values and no enum text.
# Limits: every target path is printed. Top-level keys stop after 50 lines.
# Steps: new PySpark notebook, paste this file into one cell, run, copy stdout.
# Paste COLUMN_INVENTORY, MATCH_SUMMARY, and TARGET_PATHS into the result file.
# Trim TOP_LEVEL_KEYS so the file stays within 50 lines. No personal data. No secrets.

import json

from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType

TABLE = "lh_vv_silver.dbo.slv_3p_poi_amenity"
META_NAMES = ("enum", "item_type", "required", "type")
TARGET_PREFIXES = ("$.facilities", "$.terms_and_conditions")


def structural_paths(text):
    if text is None:
        return []
    try:
        obj = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return ["__parse_error__"]
    if not isinstance(obj, dict):
        return ["__not_object__"]
    paths = [f"$.{key}" for key in obj]
    facilities = obj.get("facilities")
    if isinstance(facilities, dict):
        for name, child in facilities.items():
            paths.append(f"$.facilities.{name}")
            if isinstance(child, dict):
                paths.extend(
                    f"$.facilities.{name}.{meta}"
                    for meta in META_NAMES
                    if meta in child
                )
                enum_values = child.get("enum")
                if "enum" in child:
                    if isinstance(enum_values, list):
                        state = "empty" if len(enum_values) == 0 else "nonempty"
                    else:
                        state = "not_array"
                    paths.append(f"$.facilities.{name}.enum.{state}")
    terms = obj.get("terms_and_conditions")
    if isinstance(terms, dict):
        paths.extend(
            f"$.terms_and_conditions.{meta}"
            for meta in META_NAMES
            if meta in terms
        )
        enum_values = terms.get("enum")
        if "enum" in terms:
            if isinstance(enum_values, list):
                state = "empty" if len(enum_values) == 0 else "nonempty"
            else:
                state = "not_array"
            paths.append(f"$.terms_and_conditions.enum.{state}")
    return paths


path_udf = F.udf(structural_paths, ArrayType(StringType()))
frame = spark.table(TABLE)  # noqa: F821 - Fabric notebook session
row_count = frame.count()
print("ROW_COUNT\t%d" % row_count)
print("COLUMN_INVENTORY")
string_columns = []
for field in frame.schema.fields:
    null_count = frame.where(F.col(field.name).isNull()).count()
    print("%s\t%s\tnulls=%d" % (field.name, field.dataType.simpleString(), null_count))
    if isinstance(field.dataType, StringType) and field.name != "poi_id":
        string_columns.append(field.name)

column_rows = {}
for column in string_columns:
    counted = (
        frame.select(path_udf(F.col(column)).alias("paths"))
        .select(F.explode("paths").alias("key_path"))
        .groupBy("key_path")
        .count()
        .orderBy("key_path")
    )
    column_rows[column] = counted.collect()

matched_columns = [
    column
    for column, rows in column_rows.items()
    if any(row["key_path"] in ("$.facilities", "$.terms_and_conditions") for row in rows)
]
print("MATCH_SUMMARY")
print("matched_columns\t%s" % ",".join(matched_columns))
print("matched_count\t%d" % len(matched_columns))
print("VERDICT\t%s" % ("PASS" if len(matched_columns) == 1 else "FAIL"))

print("TARGET_PATHS")
for column, rows in column_rows.items():
    target_rows = [
        row for row in rows if row["key_path"].startswith(TARGET_PREFIXES)
    ]
    print("COLUMN\t%s\tdistinct_paths=%d\ttarget_paths=%d" % (
        column, len(rows), len(target_rows),
    ))
    if not target_rows:
        print("%s\t__no_target_path__\t0" % column)
    for row in target_rows:
        print("%s\t%s\t%d" % (column, row["key_path"], row["count"]))

print("TOP_LEVEL_KEYS")
shown = 0
for column, rows in column_rows.items():
    top_rows = [
        row for row in rows
        if row["key_path"].count(".") == 1 and not row["key_path"].startswith("__")
    ]
    for row in top_rows:
        if shown >= 50:
            print("__truncated_top_level__\tshown=50")
            break
        print("%s\t%s\t%d" % (column, row["key_path"], row["count"]))
        shown += 1
    else:
        continue
    break
