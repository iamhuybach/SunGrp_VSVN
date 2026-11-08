-- Environment: Fabric DEV. Spark SQL cell in a notebook whose lakehouse is lh_vv_bronze.
-- Read-only. Resolves row presence and the key shape of one raw_payload per source_name.
-- Parameters: source_name in strapi_blog, strapi_destination, strapi_news, strapi_ph_promotion_article.
-- Steps: run statements 1, 2, and 3 in order. Statement 4 is for on-screen viewing only.
-- Pass: statement 2 shows a row_count for each source_name that exists, and statement 3 returns one payload_schema per existing source_name.
-- Fail: the cell errors, or a named source_name is missing from statement 2.
-- Paste statements 1-3 into .ai/tasks/20261104-extract-cms-raw-data/evidence/results/cms-source-sample.txt.
-- Limits: at most 50 rows. No personal data, secrets, raw_payload text, URLs, proper names, or description text.

-- 1. Delta column types
DESCRIBE TABLE lh_vv_bronze.dbo.cms_raw_data;

-- 2. Row count per source_name
SELECT source_name, COUNT(*) AS row_count
FROM lh_vv_bronze.dbo.cms_raw_data
WHERE source_name IN (
    'strapi_blog',
    'strapi_destination',
    'strapi_news',
    'strapi_ph_promotion_article'
)
GROUP BY source_name
ORDER BY source_name;

-- 3. Key shape of one raw_payload per source_name. schema_of_json returns types, not values.
SELECT source_name, schema_of_json(raw_payload) AS payload_schema
FROM (
    SELECT
        source_name,
        raw_payload,
        ROW_NUMBER() OVER (PARTITION BY source_name ORDER BY event_id) AS sample_rn
    FROM lh_vv_bronze.dbo.cms_raw_data
    WHERE source_name IN (
        'strapi_blog',
        'strapi_destination',
        'strapi_news',
        'strapi_ph_promotion_article'
    )
) sample_rows
WHERE sample_rn = 1
ORDER BY source_name;

-- 4. View only in the notebook. Do not copy this result into the repository.
SELECT
    source_name,
    event_id,
    `type`,
    crawled_at,
    ingested_date,
    raw_payload
FROM (
    SELECT
        source_name,
        event_id,
        `type`,
        crawled_at,
        ingested_date,
        raw_payload,
        ROW_NUMBER() OVER (PARTITION BY source_name ORDER BY event_id) AS sample_rn
    FROM lh_vv_bronze.dbo.cms_raw_data
    WHERE source_name IN (
        'strapi_blog',
        'strapi_destination',
        'strapi_news',
        'strapi_ph_promotion_article'
    )
) sample_rows
WHERE sample_rn <= 5
ORDER BY source_name, sample_rn;
