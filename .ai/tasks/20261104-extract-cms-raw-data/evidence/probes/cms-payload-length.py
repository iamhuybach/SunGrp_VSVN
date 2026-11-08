# Environment: Fabric DEV. PySpark notebook whose lakehouse is lh_vv_bronze.
# Read-only. Prints payload length and whether the string ends with a closing brace. No payload text.
# Parameters: source_name in strapi_blog, strapi_destination, strapi_news, strapi_ph_promotion_article.
# Steps: paste this cell, run it, copy the printed lines.
# Pass: each source_name prints LEN with min, max, closed, and open counts.
# Fail: the cell raises, a source_name is missing, or the output contains payload text or a URL.
# Paste the printout into .ai/tasks/20261104-extract-cms-raw-data/evidence/results/cms-payload-length.txt.
# Limits: 50 rows read per source_name. Paste at most 50 lines. No personal data, secrets, URLs, names, or description text.

sources = [
    "strapi_blog",
    "strapi_destination",
    "strapi_news",
    "strapi_ph_promotion_article",
]
table = "lh_vv_bronze.dbo.cms_raw_data"

for source_name in sources:
    query = (
        "SELECT length(raw_payload) AS payload_len, "
        "substring(raw_payload, length(raw_payload), 1) = '}' AS closed_object "
        "FROM " + table + " "
        "WHERE source_name = '" + source_name + "' "
        "LIMIT 50"
    )
    rows = spark.sql(query).collect()
    lengths = [row[0] for row in rows if row[0] is not None]
    closed = sum(1 for row in rows if row[1] is True)
    opened = sum(1 for row in rows if row[1] is False)
    nulls = sum(1 for row in rows if row[0] is None)
    print(
        "LEN",
        source_name,
        "ROWS",
        len(rows),
        "NULL",
        nulls,
        "MIN",
        min(lengths) if lengths else None,
        "MAX",
        max(lengths) if lengths else None,
        "CLOSED",
        closed,
        "OPEN",
        opened,
    )
