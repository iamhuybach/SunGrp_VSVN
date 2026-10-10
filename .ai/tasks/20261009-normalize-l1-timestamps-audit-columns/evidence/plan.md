# Evidence plan

## Decision to resolve

For every partner L1 column that the registry seed types as `bigint` or `string` and that the task treats as a timestamp, assign exactly one of:

- `EPOCH_S_TS` — integer seconds
- `EPOCH_MS_TS` — integer milliseconds
- `EPOCH_US_TS` — integer microseconds
- `DATE_DAYS` — integer days since 1970-01-01, only if the value is a day count and the column is a date
- ISO datetime — string already an instant; format-normalize only
- ISO date — calendar date; do not add a time
- not a timestamp — leave the current type

`slv_pn_business_services.last_verify_at` is the control. The seed maps `epoch_seconds_timestamp` to `EPOCH_S_TS`. The probe must show that population is integer seconds. If it does not, stop.

Third-party business timestamps are not assigned an epoch rule from the one attached document. Probe E2 must show the population format class.

## Existing evidence

Checked before writing probes:

- `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS` / `TABLE_CONFIGS_3P` and `resolve_type()`. Inventory: `evidence/column-inventory.md`.
- `docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` says order-item date columns are timestamptz ISO with `NONE`, and only `last_verify_at` is `EPOCH_S_TS`. That sentence does not state seconds vs millis vs micros for the `bigint` columns.
- `docs/context/01_DATA_MODEL.md` and `.ai/tasks/20261009-redesign-3p-silver-raw-payload/evidence/` describe 3P key shapes. They do not prove partner epoch units.
- No partner payload sample and no Debezium `time.precision.mode` are in the repository.
- The local file `C:\Users\bachnh\Downloads\data_sample.json` is one bronze 3P row (`event_id`, `source_name`, `source_id`, `crawled_at`, `ingested_date`, `normalized_payload`, `raw_payload`, `language_code`). The prompt body did not include a second attachment. Shapes from that file are in `evidence/3p-sample-shapes.md`. It is one document, not a contract. Personal fields were not copied.

Name collision, already proven from the seed and `NB_LIB_EXTRACT_RAWDATA`: partner business columns `created_at` and `updated_at` use the same names as the requested audit columns. `build_table_specs` raises `ConfigError` when a business column name matches a technical column. 3P already stores payload `created_at` as `source_created_at`.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `evidence/probes/e1_partner_timestamp_shapes.sql` | Fabric DEV, read-only, full scan of `lh_vv_bronze.dbo.partner_raw_data` | For each candidate column, what shape and magnitude does the non-empty JSON value have? | A column is proven only when every non-empty value is in one class: integer digit length 10 with magnitude of unix seconds; 13 and unix millis; 16 and unix micros; `iso_date`; or one ISO datetime class with one fractional-digit length. Mixed classes, `other`, or zero non-empty values are not proven. `last_verify_at` must be integer seconds. | `evidence/results/e1_partner_timestamp_shapes.txt` |
| `evidence/probes/e2_3p_timestamp_shapes.sql` | Fabric DEV, read-only, `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` | Are `crawled_at`, payload `created_at`, and `poi_review[].time` one ISO class, and is `ingested_date` a date? | Every non-empty value of each field is one shape class. `ingested_date` stays a date if it is `YYYY-MM-DD`. | `evidence/results/e2_3p_timestamp_shapes.txt` |

Columns with zero non-empty values stay unobserved. Do not copy a unit from another table. Architecture starts only after both result files are interpreted. Unobserved columns need an explicit user decision or more data.

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- The probes emit counts and, for integer/ISO classes only, min/max strings of at most 40 characters. They do not emit `other` samples, phones, review text, media URLs, or `raw_payload`.
- Do not store personal data, secrets, or production extracts.
