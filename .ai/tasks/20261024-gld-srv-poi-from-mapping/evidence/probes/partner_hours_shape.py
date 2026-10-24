# Environment: Fabric DEV. Paste this file into one notebook cell. Read-only. Lakehouse names stay three-part.
# Decision: D-SRV-18. Shape of partner opening hours at amentities path $.policies.operating_hours.
# Pass: output has row counts, shape counts, and key-path counts. Fail: the query errors, or the paste contains raw JSON or personal data.
# Prerequisite: lh_vv_silver.dbo.slv_pn_business_service_i18ns with column amentities.
# Save: .ai/tasks/20261024-gld-srv-poi-from-mapping/evidence/results/partner_hours_shape.txt
# Limits: inspect at most 50 non-null values. Paste counts and key paths only. No raw JSON, names, bios, phones, emails, or addresses.

import json
from collections import Counter

from pyspark.sql import functions as F

src = spark.table("lh_vv_silver.dbo.slv_pn_business_service_i18ns")
hours = src.select(
    F.col("locale").alias("locale"),
    F.get_json_object(F.col("amentities"), "$.policies.operating_hours").alias("h"),
)
print("rows", hours.count())
filled = hours.where("h IS NOT NULL AND trim(h) <> ''")
print("non_null", filled.count())
filled.groupBy("locale").count().orderBy(F.desc("count")).show(20, truncate=False)

def kind(text):
    body = text.strip()
    if body.startswith("["):
        return "array"
    if body.startswith("{"):
        return "object"
    return "other"

def walk(value, prefix):
    if isinstance(value, dict):
        if not value:
            yield prefix + ":empty_object"
            return
        for key in sorted(value):
            yield from walk(value[key], prefix + "." + str(key))
    elif isinstance(value, list):
        yield prefix + ":array"
        if value:
            yield from walk(value[0], prefix + "[]")
    else:
        yield prefix + ":" + type(value).__name__

shapes = Counter()
paths = Counter()
invalid = 0
sample = filled.limit(50).collect()
for row in sample:
    text = row["h"]
    shapes[kind(text)] += 1
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        invalid += 1
        continue
    paths[" | ".join(sorted(set(walk(parsed, "$"))))] += 1

print("sample_rows", len(sample))
print("invalid_json", invalid)
for name, count in shapes.most_common():
    print(f"shape {name} {count}")
for signature, count in paths.most_common():
    print(f"paths {count} {signature}")
