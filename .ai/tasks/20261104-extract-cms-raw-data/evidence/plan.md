# Evidence plan

## Decision to resolve

- Whether `strapi_blog`, `strapi_destination`, `strapi_news`, and `strapi_ph_promotion_article` each have rows in `lh_vv_bronze.dbo.cms_raw_data`.
- The Delta types of the bronze columns, and the JSON key shape of one `raw_payload` per `source_name`. One schema row is not a schema contract.

## Existing evidence

- `evidence/payload-shape.md`: key tree of one `cms_raw_data` row. No values and no URLs.
- `evidence/results/cms-source-sample.md`: sanitized statements 1 and 2. Statement 3 failed. Statement 4 was not stored.
- `evidence/results/cms-payload-keys.md`: sanitized key census. `strapi_blog` had no parsed row in the 50-row sample.
- `evidence/results/cms-payload-length.md`: on 50 rows, `CLOSED` equals the parsed-row count. `strapi_news` max length is 14575.
- `evidence/results/cms-payload-close-rate.md`: full-table closed and open counts. Max lengths exceed 8000 for blog, destination, and news. The cause of an open string is not established.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `evidence/probes/cms-source-sample.sql` | Fabric DEV, Spark SQL, lakehouse `lh_vv_bronze` | Row counts and Delta column types | Statements 1 and 2 returned. Statement 3 failed and does not need to be rerun. | `evidence/results/cms-source-sample.md` |
| `evidence/probes/cms-payload-keys.py` | Fabric DEV, PySpark, lakehouse `lh_vv_bronze` | Top-level keys in up to 50 rows per `source_name`, skipping invalid JSON | Returned. `strapi_blog` had 50 parse failures and no key set. | `evidence/results/cms-payload-keys.md` |
| `evidence/probes/cms-payload-length.py` | Fabric DEV, PySpark, lakehouse `lh_vv_bronze` | Length and closing brace on 50 rows per `source_name` | Returned. `CLOSED` matches the parsed-row counts. | `evidence/results/cms-payload-length.md` |
| `evidence/probes/cms-payload-close-rate.sql` | Fabric DEV, Spark SQL, lakehouse `lh_vv_bronze` | Full-table count of payloads that end with `}` | Returned. Four rows are in D-09. | `evidence/results/cms-payload-close-rate.md` |
| `evidence/probes/cms-open-payload-cause.py` | Fabric DEV, PySpark, lakehouse `lh_vv_bronze` | P1: open-row lengths and lost or stale (`document_id`, `locale`) keys | Returned in D-11. `EVENT_BOTH` had no rows. | `evidence/results/cms-open-payload-cause.md` |
| `evidence/probes/cms-format-census.py` | Fabric DEV, PySpark, lakehouse `lh_vv_bronze` | P2: timestamp, date, `crawled_at`, and `locale` formats on closed payloads | `FORMAT`, `CRAWLED_AT`, and `LOCALE` returned in D-12. `ORDER` failed. | `evidence/results/cms-format-census.md` |
| `evidence/probes/cms-closed-key-census.py` | Fabric DEV, PySpark, lakehouse `lh_vv_bronze` | P3: key sets and types on 50 closed rows per `source_name` | Returned in D-13. | `evidence/results/cms-closed-key-census.md` |
| `evidence/probes/cms-event-order.py` | Fabric DEV, PySpark, lakehouse `lh_vv_bronze` | Whether `updatedAt` order and `crawled_at` order pick the same event | Returned in D-14. Tie count is 0. | `evidence/results/cms-event-order.md` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
