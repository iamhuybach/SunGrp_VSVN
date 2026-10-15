# Probe: P02_amenity_enum_groups
# Environment: Fabric DEV. Attach lakehouse lh_vv_silver. Read-only.
# Table: lh_vv_silver.dbo.slv_3p_poi_amenity. Column: source_flags_json.
# Decision: which nested objects contain an enum key. Wrappers are not groups.
# Pass: at least one object path has an enum key.
# Fail: no object contains enum.
# Output: key path, value kind, enum empty or nonempty. No enum text.
# Limits: child-key lines stop after 50. Enum-group lines are complete.
# Steps: new PySpark notebook, paste this file into one cell, run, copy stdout.
# Paste ENUM_GROUPS and MATCH_SUMMARY. Trim CHILD_KEYS so the file stays within 50 lines.
# No personal data. No secrets.

import json

from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType

TABLE = "lh_vv_silver.dbo.slv_3p_poi_amenity"
COLUMN = "source_flags_json"


def value_kind(value):
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, bool):
        return "bool"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    return "other"


def structural_tokens(text):
    if text is None:
        return ["STATUS\tnull"]
    try:
        root = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return ["STATUS\tparse_error"]
    if not isinstance(root, dict):
        return ["STATUS\tnot_object"]
    tokens = ["STATUS\tobject"]

    def walk(obj, path, depth):
        if not isinstance(obj, dict) or depth > 4:
            return
        if "enum" in obj:
            enum_values = obj.get("enum")
            if isinstance(enum_values, list):
                state = "empty" if len(enum_values) == 0 else "nonempty"
            else:
                state = "not_array"
            meta = [
                name for name in ("item_type", "required", "type") if name in obj
            ]
            tokens.append(
                "ENUM\t%s\tenum.%s\tmeta=%s" % (path, state, ",".join(meta))
            )
        if depth == 1:
            for key, value in obj.items():
                tokens.append("CHILD\t%s.%s\tkind=%s" % (path, key, value_kind(value)))
        for key, value in obj.items():
            if key == "enum" or not isinstance(value, dict):
                continue
            walk(value, "%s.%s" % (path, key), depth + 1)

    for key, value in root.items():
        tokens.append("CHILD\t$.%s\tkind=%s" % (key, value_kind(value)))
        if isinstance(value, dict):
            walk(value, "$.%s" % key, 1)
    return tokens


token_udf = F.udf(structural_tokens, ArrayType(StringType()))
frame = spark.table(TABLE)  # noqa: F821 - Fabric notebook session
counted = (
    frame.select(token_udf(F.col(COLUMN)).alias("tokens"))
    .select(F.explode("tokens").alias("token"))
    .groupBy("token")
    .count()
    .orderBy("token")
)
rows = counted.collect()
enum_rows = [row for row in rows if row["token"].startswith("ENUM\t")]
child_rows = [row for row in rows if row["token"].startswith("CHILD\t")]
status_rows = [row for row in rows if row["token"].startswith("STATUS\t")]

print("ROW_TOKENS\t%d" % len(rows))
print("MATCH_SUMMARY")
for row in status_rows:
    print("%s\t%d" % (row["token"], row["count"]))
print("enum_paths\t%d" % len(enum_rows))
print("VERDICT\t%s" % ("PASS" if enum_rows else "FAIL"))

print("ENUM_GROUPS")
if not enum_rows:
    print("__no_enum_group__\t0")
for row in enum_rows:
    print("%s\t%d" % (row["token"], row["count"]))

print("CHILD_KEYS")
for row in child_rows[:50]:
    print("%s\t%d" % (row["token"], row["count"]))
if len(child_rows) > 50:
    print("__truncated_child_keys__\tshown=50\ttotal=%d" % len(child_rows))
