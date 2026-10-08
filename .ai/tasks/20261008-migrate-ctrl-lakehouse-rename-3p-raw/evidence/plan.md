# Evidence plan

## Decision to resolve

No design decision is blocked on Fabric DEV data.

The new raw table DDL is confirmed by the user and matches the attached sample column list (`event_id`, `source_name`, `source_id`, `crawled_at`, `ingested_date`, `normalized_payload`, `raw_payload`, `language_code`, all strings). Control grain, partitions, and column comments come from `docs/context/CTRL_TABLES_CONTEXT.md`. Seed rows come from `notebooks/NB_CREATE_DDL.ipynb`, with the 3rd-party source identity renamed. The task forbids copying live `lh_vv_bronze.ctrl` rows, so a DEV row count would not change the seed.

`lh_vv_ctrl` is created by the DDL in this task. Its schema is specified, not discovered. Attaching the lakehouse and binding the SQL analytics endpoint connection are runtime rollout steps.

## Existing evidence

- User-confirmed DDL for `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream`.
- Local sample file `C:\Users\bachnh\Downloads\data_sample.json`: one exported row whose field list matches that DDL. `normalized_payload` and `raw_payload` are JSON strings. The file contains personal data and must not be copied into the repository. Only the object key tree and JSON types of `normalized_payload` may be recorded in context.
- `docs/context/CTRL_TABLES_CONTEXT.md` DDL for all seven control tables, including `PARTITIONED BY (src_tbl)` on `ctrl_cdc_state` and `ctrl_cdc_reject`.
- `notebooks/NB_CREATE_DDL.ipynb` partner `TABLE_CONFIGS` seed and 3rd-party registry seed, currently keyed by `poi_raw_event`.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|

None.

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
