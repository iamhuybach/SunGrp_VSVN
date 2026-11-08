# Environment: Fabric DEV. PySpark notebook whose lakehouse is lh_vv_bronze.
# Read-only. P3 from architecture.md ## Required probes and decisions. Closed payloads only.
# Parameters: source_name in strapi_blog, strapi_destination, strapi_news, strapi_ph_promotion_article. 50 rows each.
# Steps: paste this cell and run it. Copy every printed line.
# Pass: each source_name prints SOURCE, key-set lines, TYPE, and FIELD_TYPE. No payload text.
# Fail: the cell raises, a source_name is missing, or the output contains payload text or a URL.
# Paste the printout into .ai/tasks/20261104-extract-cms-raw-data/evidence/results/cms-closed-key-census.txt.
# Limits: 50 rows read per source_name. Paste at most 50 lines if it fits; otherwise paste SOURCE, key sets, TYPE, and FIELD_TYPE only.

import json
from collections import Counter

sources = [
    "strapi_blog",
    "strapi_destination",
    "strapi_news",
    "strapi_ph_promotion_article",
]
table = "lh_vv_bronze.dbo.cms_raw_data"
watch = ("SEO", "news_category", "rank", "tags", "hooks", "sections")

def value_type(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "other"

for source_name in sources:
    query = (
        "SELECT raw_payload FROM " + table +
        " WHERE source_name = '" + source_name + "'"
        " AND substring(raw_payload, length(raw_payload), 1) = '}'"
        " LIMIT 50"
    )
    rows = spark.sql(query).collect()
    shapes = Counter()
    field_types = {name: Counter() for name in watch}
    first_object = None
    parse_fail = 0
    for row in rows:
        try:
            payload = json.loads(row[0])
        except json.JSONDecodeError:
            parse_fail += 1
            continue
        if not isinstance(payload, dict):
            shapes[("<not-object>",)] += 1
            continue
        shapes[tuple(sorted(payload))] += 1
        if first_object is None:
            first_object = payload
        for name in watch:
            if name in payload:
                field_types[name][value_type(payload[name])] += 1
            else:
                field_types[name]["absent"] += 1
    print("SOURCE", source_name, "ROWS", len(rows), "PARSE_FAIL", parse_fail)
    for keys, count in shapes.most_common():
        print(count, ",".join(keys))
    if first_object is not None:
        schema = spark.read.json(
            spark.sparkContext.parallelize([json.dumps(first_object)])
        ).schema
        print("TYPE", source_name)
        for field in schema.fields:
            print(field.name, field.dataType.typeName())
    print("FIELD_TYPE", source_name)
    for name in watch:
        parts = ["%s=%s" % (kind, count) for kind, count in sorted(field_types[name].items())]
        print(name, ",".join(parts))
