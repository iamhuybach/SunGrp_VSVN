-- Probe E1: 3P ordering and identifier contract
-- Decision: GATE-001. Close the P0 only when all three aggregates are 0
-- and an upstream contract guarantees nonblank event_id plus strictly
-- increasing crawled_at per (source_name, source_id) across commits.
-- Environment: Fabric DEV, lakehouse lh_vv_bronze, read-only.
-- Do not return payloads, phone numbers, URLs, or review text.
-- Save the single aggregate row to evidence/results/e1_3p_ordering.txt.

WITH base AS (
    SELECT
        source_name,
        source_id,
        TRY_CAST(crawled_at AS TIMESTAMP) AS crawled_ts,
        event_id,
        SHA2(CONCAT_WS('\u0001',
            COALESCE(normalized_payload, ''),
            COALESCE(language_code, '')
        ), 256) AS output_signature
    FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
),
exact_ties AS (
    SELECT source_name, source_id, crawled_ts, event_id
    FROM base
    WHERE crawled_ts IS NOT NULL
    GROUP BY source_name, source_id, crawled_ts, event_id
    HAVING COUNT(DISTINCT output_signature) > 1
),
entity_time_ties AS (
    SELECT source_name, source_id, crawled_ts
    FROM base
    WHERE crawled_ts IS NOT NULL
    GROUP BY source_name, source_id, crawled_ts
    HAVING COUNT(DISTINCT COALESCE(event_id, '<NULL>')) > 1
        OR COUNT(DISTINCT output_signature) > 1
)
SELECT
    SUM(CASE WHEN event_id IS NULL OR TRIM(event_id) = '' THEN 1 ELSE 0 END) AS missing_event_id_rows,
    (SELECT COUNT(*) FROM exact_ties) AS conflicting_exact_ties,
    (SELECT COUNT(*) FROM entity_time_ties) AS conflicting_entity_time_ties
FROM base;
