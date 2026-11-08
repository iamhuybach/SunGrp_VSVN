# Environment: Fabric DEV. PySpark notebook whose lakehouse is lh_vv_bronze.
# Read-only. Replaces the failed ORDER section of cms-format-census.py. Closed payloads only.
# Parameters: source_name in strapi_blog, strapi_destination, strapi_news, strapi_ph_promotion_article.
# Steps: paste this cell and run it. Copy the printed lines.
# Pass: ORDER prints keys_with_crawled_at_tie and keys_updated_order_ne_crawled_order for each source_name.
# Fail: the cell raises, a source_name is missing, or the output contains payload text or a URL.
# Paste the printout into .ai/tasks/20261104-extract-cms-raw-data/evidence/results/cms-event-order.txt.
# Limits: four aggregate rows. No personal data, secrets, URLs, names, or description text.

sources = (
    "'strapi_blog', 'strapi_destination', "
    "'strapi_news', 'strapi_ph_promotion_article'"
)
sql = (
    "WITH closed AS ("
    " SELECT source_name, event_id, crawled_at,"
    " regexp_extract(raw_payload, '\"documentId\"\\\\s*:\\\\s*\"([^\"]*)\"', 1) AS document_id,"
    " regexp_extract(raw_payload, '\"locale\"\\\\s*:\\\\s*\"([^\"]*)\"', 1) AS locale,"
    " regexp_extract(raw_payload, '\"updatedAt\"\\\\s*:\\\\s*\"([^\"]*)\"', 1) AS updated_at"
    " FROM lh_vv_bronze.dbo.cms_raw_data"
    " WHERE source_name IN (" + sources + ")"
    " AND substring(raw_payload, length(raw_payload), 1) = '}'"
    "), ranked AS ("
    " SELECT source_name, document_id, locale, event_id, crawled_at, updated_at,"
    " ROW_NUMBER() OVER (PARTITION BY source_name, document_id, locale"
    " ORDER BY crawled_at DESC, event_id DESC) AS rn_crawled,"
    " ROW_NUMBER() OVER (PARTITION BY source_name, document_id, locale"
    " ORDER BY updated_at DESC, event_id DESC) AS rn_updated,"
    " COUNT(*) OVER (PARTITION BY source_name, document_id, locale, crawled_at) AS same_crawled"
    " FROM closed"
    " WHERE document_id <> '' AND locale <> ''"
    ") "
    "SELECT source_name,"
    " COUNT(DISTINCT CASE WHEN same_crawled > 1 THEN CONCAT(document_id, '|', locale) END)"
    " AS keys_with_crawled_at_tie,"
    " SUM(CASE WHEN rn_crawled = 1 AND rn_updated > 1 THEN 1 ELSE 0 END)"
    " AS keys_updated_order_ne_crawled_order"
    " FROM ranked GROUP BY source_name ORDER BY source_name"
)
print("ORDER")
for row in spark.sql(sql).collect():
    print("\t".join("" if value is None else str(value) for value in row))
