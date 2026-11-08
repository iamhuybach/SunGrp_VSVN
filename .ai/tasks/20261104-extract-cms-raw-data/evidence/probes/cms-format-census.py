# Environment: Fabric DEV. PySpark notebook whose lakehouse is lh_vv_bronze.
# Read-only. P2 from architecture.md ## Required probes and decisions. Closed payloads only.
# Parameters: source_name in strapi_blog, strapi_destination, strapi_news, strapi_ph_promotion_article.
# Steps: paste this cell and run it. Copy every printed line.
# Pass: FORMAT has one row per source_name, LOCALE lists values with counts, ORDER prints two counts per source.
# Fail: the cell raises, a source_name is missing, or the output contains payload text or a URL.
# Paste the printout into .ai/tasks/20261104-extract-cms-raw-data/evidence/results/cms-format-census.txt.
# Limits: aggregates only. No personal data, secrets, URLs, names, or description text.

sources = (
    "'strapi_blog', 'strapi_destination', "
    "'strapi_news', 'strapi_ph_promotion_article'"
)

def field_expr(name):
    pattern = '"%s"\\\\s*:\\\\s*"([^"]*)"' % name
    return "regexp_extract(raw_payload, '%s', 1)" % pattern

def class_counts(alias):
    value = alias
    iso_z = value + " RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\\\.[0-9]+)?Z$'"
    iso_off = value + " RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\\\.[0-9]+)?[+-][0-9]{2}:[0-9]{2}$'"
    ymd = value + " RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'"
    return (
        " SUM(CASE WHEN %s <> '' THEN 1 ELSE 0 END) AS %s_nonblank,"
        " SUM(CASE WHEN %s THEN 1 ELSE 0 END) AS %s_iso_z,"
        " SUM(CASE WHEN %s THEN 1 ELSE 0 END) AS %s_iso_offset,"
        " SUM(CASE WHEN %s THEN 1 ELSE 0 END) AS %s_ymd,"
        " SUM(CASE WHEN %s <> '' AND NOT (%s) AND NOT (%s) AND NOT (%s) THEN 1 ELSE 0 END) AS %s_other"
    ) % (
        value, alias,
        iso_z, alias,
        iso_off, alias,
        ymd, alias,
        value, iso_z, iso_off, ymd, alias,
    )

fields = [
    "createdAt", "updatedAt", "publishedAt",
    "promotionStartDateTime", "promotionEndDateTime",
    "usageStartDateTime", "usageEndDateTime",
    "first_publish_date",
]
select_fields = ", ".join(
    field_expr(name) + " AS " + name for name in fields
)
format_cols = ", ".join(class_counts(name) for name in fields)
base = (
    "WITH closed AS ("
    " SELECT source_name, event_id, crawled_at, raw_payload, "
    + select_fields +
    " FROM lh_vv_bronze.dbo.cms_raw_data"
    " WHERE source_name IN (" + sources + ")"
    " AND substring(raw_payload, length(raw_payload), 1) = '}'"
    ") "
)

def show(label, sql):
    print(label)
    for row in spark.sql(sql).collect():
        print("\t".join("" if value is None else str(value) for value in row))

show(
    "FORMAT",
    base + "SELECT source_name, " + format_cols + " FROM closed GROUP BY source_name ORDER BY source_name",
)
show(
    "CRAWLED_AT",
    (
        "SELECT source_name,"
        " SUM(CASE WHEN try_cast(crawled_at AS TIMESTAMP) IS NULL THEN 1 ELSE 0 END) AS try_cast_null,"
        " SUM(CASE WHEN crawled_at RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\\\.[0-9]+)?Z$' THEN 1 ELSE 0 END) AS iso_z,"
        " SUM(CASE WHEN crawled_at RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\\\.[0-9]+)?[+-][0-9]{2}:[0-9]{2}$' THEN 1 ELSE 0 END) AS iso_offset,"
        " COUNT(*) AS rows"
        " FROM lh_vv_bronze.dbo.cms_raw_data"
        " WHERE source_name IN (" + sources + ")"
        " GROUP BY source_name ORDER BY source_name"
    ),
)
show(
    "LOCALE",
    base + (
        "SELECT source_name,"
        " CASE WHEN locale = '' THEN '<blank>' ELSE locale END AS locale,"
        " COUNT(*) AS cnt FROM ("
        " SELECT source_name, regexp_extract(raw_payload, '\"locale\"\\\\s*:\\\\s*\"([^\"]*)\"', 1) AS locale"
        " FROM closed"
        ") t GROUP BY source_name, locale ORDER BY source_name, cnt DESC"
    ),
)
show(
    "ORDER",
    base + (
        "SELECT source_name,"
        " SUM(CASE WHEN event_cnt > distinct_crawled THEN 1 ELSE 0 END) AS keys_with_crawled_at_tie,"
        " SUM(CASE WHEN top_crawled_event <> top_updated_event THEN 1 ELSE 0 END) AS keys_updated_order_ne_crawled_order"
        " FROM ("
        " SELECT source_name, document_id, locale,"
        " COUNT(*) AS event_cnt,"
        " COUNT(DISTINCT crawled_at) AS distinct_crawled,"
        " MAX(STRUCT(crawled_at, event_id)) AS top_crawled_event,"
        " MAX(STRUCT(updated_at, event_id)) AS top_updated_event"
        " FROM ("
        " SELECT source_name, crawled_at, event_id, updatedAt AS updated_at,"
        " regexp_extract(raw_payload, '\"documentId\"\\\\s*:\\\\s*\"([^\"]*)\"', 1) AS document_id,"
        " regexp_extract(raw_payload, '\"locale\"\\\\s*:\\\\s*\"([^\"]*)\"', 1) AS locale"
        " FROM closed"
        ") e"
        " WHERE document_id <> '' AND locale <> ''"
        " GROUP BY source_name, document_id, locale"
        ") k GROUP BY source_name ORDER BY source_name"
    ),
)
