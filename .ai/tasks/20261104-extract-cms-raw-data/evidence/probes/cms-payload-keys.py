# Environment: Fabric DEV. PySpark notebook whose lakehouse is lh_vv_bronze.
# Read-only. Prints top-level key sets. Invalid JSON is counted and skipped, not printed.
# Parameters: source_name in strapi_blog, strapi_destination, strapi_news, strapi_ph_promotion_article.
# Steps: paste this cell, run it, copy the printed lines.
# Pass: the cell finishes. Each source_name prints SOURCE and PARSE_FAIL. Valid rows also print key sets and TYPE.
# Fail: the cell raises, a source_name is missing, or the output contains payload text or a URL.
# Paste the printout into .ai/tasks/20261104-extract-cms-raw-data/evidence/results/cms-payload-keys.txt.
# Limits: 50 rows read per source_name. Paste at most 50 lines. No personal data, secrets, URLs, names, or description text.

import json
from collections import Counter

sources = [
    "strapi_blog",
    "strapi_destination",
    "strapi_news",
    "strapi_ph_promotion_article",
]
table = "lh_vv_bronze.dbo.cms_raw_data"

for source_name in sources:
    rows = spark.sql(
        f"""
        SELECT raw_payload
        FROM {table}
        WHERE source_name = '{source_name}'
        LIMIT 50
        """
    ).collect()
    shapes = Counter()
    parse_fail = Counter()
    null_count = 0
    first_object = None
    for row in rows:
        text = row[0]
        if text is None:
            null_count += 1
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            parse_fail[(exc.msg, exc.colno)] += 1
            continue
        if not isinstance(payload, dict):
            shapes[("<not-object>",)] += 1
            continue
        shapes[tuple(sorted(payload))] += 1
        if first_object is None:
            first_object = payload
    print("SOURCE", source_name, "ROWS", len(rows), "NULL", null_count)
    print("PARSE_FAIL", sum(parse_fail.values()))
    for (message, column), count in parse_fail.most_common():
        print("PARSE_FAIL", count, message, "col", column)
    for keys, count in shapes.most_common():
        print(count, ",".join(keys))
    if first_object is None:
        continue
    schema = spark.read.json(
        spark.sparkContext.parallelize([json.dumps(first_object)])
    ).schema
    print("TYPE", source_name)
    for field in schema.fields:
        print(field.name, field.dataType.typeName())
