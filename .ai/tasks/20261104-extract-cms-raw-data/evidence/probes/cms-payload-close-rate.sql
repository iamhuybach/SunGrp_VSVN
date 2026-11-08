-- Environment: Fabric DEV. Spark SQL cell in a notebook whose lakehouse is lh_vv_bronze.
-- Read-only. Counts, for the whole table, how many payloads end with a closing brace.
-- Parameters: source_name in strapi_blog, strapi_destination, strapi_news, strapi_ph_promotion_article.
-- Steps: run the statement below.
-- Pass: four rows, one per source_name, with row_count, closed_object, open_object, min_len, and max_len.
-- Fail: the cell errors or a named source_name is missing.
-- Paste the grid into .ai/tasks/20261104-extract-cms-raw-data/evidence/results/cms-payload-close-rate.txt.
-- Limits: four aggregate rows. No payload text, personal data, secrets, URLs, names, or description text.

SELECT
    source_name,
    COUNT(*) AS row_count,
    SUM(CASE WHEN raw_payload IS NULL THEN 1 ELSE 0 END) AS null_payload,
    SUM(CASE WHEN substring(raw_payload, length(raw_payload), 1) = '}' THEN 1 ELSE 0 END) AS closed_object,
    SUM(CASE WHEN raw_payload IS NOT NULL AND substring(raw_payload, length(raw_payload), 1) <> '}' THEN 1 ELSE 0 END) AS open_object,
    MIN(length(raw_payload)) AS min_len,
    MAX(length(raw_payload)) AS max_len
FROM lh_vv_bronze.dbo.cms_raw_data
WHERE source_name IN (
    'strapi_blog',
    'strapi_destination',
    'strapi_news',
    'strapi_ph_promotion_article'
)
GROUP BY source_name
ORDER BY source_name;
