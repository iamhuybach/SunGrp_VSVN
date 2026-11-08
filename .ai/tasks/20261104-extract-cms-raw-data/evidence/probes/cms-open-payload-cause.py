# Environment: Fabric DEV. PySpark notebook whose lakehouse is lh_vv_bronze.
# Read-only. P1 from architecture.md ## Required probes and decisions. Aggregates only.
# Parameters: source_name in strapi_blog, strapi_destination, strapi_news, strapi_ph_promotion_article.
# Steps: paste this cell and run it. Copy every printed line.
# Pass: each source_name prints HIST, TOP_LEN, EVENT_BOTH, and KEYS. No payload text and no document id.
# Fail: the cell raises, a source_name is missing, or the output contains payload text or a URL.
# Paste the printout into .ai/tasks/20261104-extract-cms-raw-data/evidence/results/cms-open-payload-cause.txt.
# Limits: aggregate rows only. No personal data, secrets, URLs, names, or description text.

sources = (
    "'strapi_blog', 'strapi_destination', "
    "'strapi_news', 'strapi_ph_promotion_article'"
)
base = (
    "WITH base AS ("
    " SELECT source_name, event_id, crawled_at,"
    " length(raw_payload) AS payload_len,"
    " substring(raw_payload, length(raw_payload), 1) = '}' AS closed_object,"
    " regexp_extract(raw_payload, '\"documentId\"\\\\s*:\\\\s*\"([^\"]*)\"', 1) AS document_id,"
    " regexp_extract(raw_payload, '\"locale\"\\\\s*:\\\\s*\"([^\"]*)\"', 1) AS locale"
    " FROM lh_vv_bronze.dbo.cms_raw_data"
    " WHERE source_name IN (" + sources + ")"
    ") "
)

def show(label, sql):
    print(label)
    for row in spark.sql(sql).collect():
        print("\t".join("" if value is None else str(value) for value in row))

show(
    "HIST",
    base + (
        "SELECT source_name,"
        " SUM(CASE WHEN payload_len < 1000 THEN 1 ELSE 0 END) AS lt_1000,"
        " SUM(CASE WHEN payload_len BETWEEN 1000 AND 7999 THEN 1 ELSE 0 END) AS b_1000_7999,"
        " SUM(CASE WHEN payload_len BETWEEN 8000 AND 15999 THEN 1 ELSE 0 END) AS b_8000_15999,"
        " SUM(CASE WHEN payload_len BETWEEN 16000 AND 31999 THEN 1 ELSE 0 END) AS b_16000_31999,"
        " SUM(CASE WHEN payload_len BETWEEN 32000 AND 63999 THEN 1 ELSE 0 END) AS b_32000_63999,"
        " SUM(CASE WHEN payload_len >= 64000 THEN 1 ELSE 0 END) AS ge_64000"
        " FROM base WHERE closed_object = false"
        " GROUP BY source_name ORDER BY source_name"
    ),
)
show(
    "TOP_LEN",
    base + (
        "SELECT source_name, payload_len, cnt FROM ("
        " SELECT source_name, payload_len, COUNT(*) AS cnt,"
        " ROW_NUMBER() OVER (PARTITION BY source_name ORDER BY COUNT(*) DESC, payload_len) AS rn"
        " FROM base WHERE closed_object = false"
        " GROUP BY source_name, payload_len"
        ") t WHERE rn <= 5 ORDER BY source_name, rn"
    ),
)
show(
    "EVENT_BOTH",
    base + (
        "SELECT source_name, COUNT(*) AS event_ids_in_both FROM ("
        " SELECT source_name, event_id FROM base"
        " GROUP BY source_name, event_id"
        " HAVING SUM(CASE WHEN closed_object THEN 1 ELSE 0 END) > 0"
        " AND SUM(CASE WHEN closed_object THEN 0 ELSE 1 END) > 0"
        ") t GROUP BY source_name ORDER BY source_name"
    ),
)
show(
    "KEYS",
    base + (
        "SELECT source_name,"
        " COUNT(*) AS key_pairs,"
        " SUM(CASE WHEN closed_events > 0 THEN 1 ELSE 0 END) AS keys_with_closed,"
        " SUM(CASE WHEN closed_events = 0 THEN 1 ELSE 0 END) AS keys_with_no_closed,"
        " SUM(CASE WHEN latest_open THEN 1 ELSE 0 END) AS keys_latest_open"
        " FROM ("
        " SELECT source_name, document_id, locale,"
        " SUM(CASE WHEN closed_object THEN 1 ELSE 0 END) AS closed_events,"
        " MAX(CASE WHEN rn = 1 AND closed_object = false THEN 1 ELSE 0 END) = 1 AS latest_open"
        " FROM ("
        " SELECT source_name, document_id, locale, closed_object,"
        " ROW_NUMBER() OVER (PARTITION BY source_name, document_id, locale"
        " ORDER BY crawled_at DESC, event_id DESC) AS rn"
        " FROM base WHERE document_id <> '' AND locale <> ''"
        " ) ranked"
        " GROUP BY source_name, document_id, locale"
        ") keys GROUP BY source_name ORDER BY source_name"
    ),
)
show(
    "KEYS_UNPARSED",
    base + (
        "SELECT source_name,"
        " SUM(CASE WHEN document_id = '' OR locale = '' THEN 1 ELSE 0 END) AS rows_missing_id_or_locale"
        " FROM base GROUP BY source_name ORDER BY source_name"
    ),
)
