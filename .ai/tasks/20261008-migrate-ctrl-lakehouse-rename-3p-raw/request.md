# Request

## User outcome

Third-party raw reads use `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` instead of `lh_vv_bronze.dbo.poi_raw_event`. The seven control tables live in `lh_vv_ctrl.dbo` instead of `lh_vv_bronze.ctrl`, with DDL and literal or repo-generated seed in `NB_CREATE_DDL`. Config rows for the 3rd-party source use `src_tbl = brz_3rd_crawler_poi_stream` and `watermark_id = wm_transform_brz_3rd_crawler_poi_stream`.

## Scope

### In scope

- Replace every current reference to `poi_raw_event` and `wm_transform_poi_raw_event` in notebooks, the FL_00 pipeline, context docs, seed, config, partition filters, sample SQL, and comments. Do not keep an alias or fallback to the old names.
- Replace every current `lh_vv_bronze.ctrl.<table>` reference with `lh_vv_ctrl.dbo.<table>` for:
  - `ctrl_mng_pipeline_config`
  - `ctrl_mng_watermark`
  - `ctrl_cfg_schema_registry`
  - `ctrl_log_run`
  - `ctrl_log_table_run`
  - `ctrl_cdc_state`
  - `ctrl_cdc_reject`
- Update notebook constants (`CTRL_SCHEMA`, `T_*`) and hardcoded SQL. Default lakehouse may stay `lh_vv_bronze` when the notebook still reads bronze raw data. Do not invent a Fabric lakehouse GUID for `lh_vv_ctrl`.
- `NB_CREATE_DDL` must create the seven tables in `lh_vv_ctrl.dbo` with the grain, partition, and column comments already documented in `docs/context/CTRL_TABLES_CONTEXT.md`.
- Seed configuration with `INSERT` of literal values, or by generating rows from the seed already in `NB_CREATE_DDL` (`TABLE_CONFIGS` and the 3rd-party registry seed). Do not use `INSERT ... SELECT` or `COPY` from `lh_vv_bronze.ctrl.*`.
- Rename only the 3rd-party source identity inside that seed: `src_tbl` and the derived watermark id. Partner `src_tbl = partner_raw_data` and `watermark_id = wm_transform_partner_raw_data` stay.
- `ctrl_cdc_state` and `ctrl_cdc_reject` stay partitioned by `src_tbl`. New 3rd-party rows use `src_tbl = brz_3rd_crawler_poi_stream`.
- FL_00 pre-check currently queries `ctrl.ctrl_mng_pipeline_config` and the watermark lookup with `database = lh_vv_bronze` through `conn_lh_vv_bronze_by_sqlep`. Point that read at `lh_vv_ctrl.dbo`. Keep activity identity, ForEach, and the fixed partner notebook activity. Do not add a Switch.
- Update `docs/context/CTRL_TABLES_CONTEXT.md`, `01_DATA_MODEL.md`, `02_NAMING_CONVENTION.md`, notebook context files, and `docs/context/CHECK_CTRL_SNAPSHOT.py`.
- Record the `normalized_payload` object shape (keys and JSON types) from the user-supplied sample for a later transform. Do not copy personal data, phone numbers, review text, media URLs, or the raw payload into the repository.
- Confirmed raw DDL, same columns as `poi_raw_event`, all `STRING`:

```sql
DROP TABLE IF EXISTS lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream;
CREATE TABLE IF NOT EXISTS lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream (
    event_id            STRING,
    source_name         STRING,
    source_id           STRING,
    crawled_at          STRING,
    ingested_date       STRING,
    normalized_payload  STRING,
    raw_payload         STRING,
    language_code       STRING
)
USING DELTA;
```

The table already exists on Fabric DEV. This task does not recreate bronze raw data.

### Out of scope

- Implementing the silver transform of `normalized_payload`.
- Copying live watermarks, CDC state, or logs from `lh_vv_bronze.ctrl`.
- Dropping `lh_vv_bronze.ctrl.*` or `lh_vv_bronze.dbo.poi_raw_event` in this change. The existing DROP cell in `NB_CREATE_DDL` must not be retargeted so that a setup run deletes the old control lakehouse before the new one is proven.
- Adding a Switch or calling `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` from `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`.
- Historical task artifacts under other `.ai/tasks/20261008-*` directories. They remain records of the previous names.
- Agent-system files. `AGENTS.md` section 9 names the three medallion lakehouses and does not place control tables in `lh_vv_bronze.ctrl`.
- Commit, push, or merge.

## Acceptance criteria

- Repository search shows no current `poi_raw_event`, `wm_transform_poi_raw_event`, or `lh_vv_bronze.ctrl` except a clearly marked migration note or an unchanged historical task artifact.
- `NB_CREATE_DDL` contains DDL and INSERT seed for `lh_vv_ctrl.dbo.*`.
- 3rd-party `pipeline_config`, `schema_registry`, and `watermark` seed use `src_tbl = brz_3rd_crawler_poi_stream` and `watermark_id = wm_transform_brz_3rd_crawler_poi_stream`.
- `python scripts/vv.py verify 20261008-migrate-ctrl-lakehouse-rename-3p-raw` passes.
- Context docs name `lh_vv_ctrl.dbo` and `brz_3rd_crawler_poi_stream`.
- A Vietnamese runtime runbook covers creating the control tables, rerunning the 3rd-party extract, and checking watermark and CDC state.

## Constraints

- Do not infer data distribution, uniqueness, or null rates. Seed values come from `CTRL_TABLES_CONTEXT.md` and the existing `NB_CREATE_DDL` seed.
- Do not seed with `INSERT ... SELECT` from `lh_vv_bronze.ctrl.*`.
- Keep platform invariants: pre-check reads pipeline config and watermark; extract does not move watermark or CDC state backward; `ctrl_cdc_*` partitions follow `src_tbl`.
- A fresh seed means the new lakehouse starts without the live bronze control rows. The next 3rd-party extract therefore cannot resume `last_src_version` or entity state from `poi_raw_event`. Architecture must define that cutover, including `allow_full_scan`, idempotent MERGE, and the fact that old `src_tbl = poi_raw_event` partitions are not readable under the new name.
- Do not invent `lh_vv_ctrl` workspace or lakehouse IDs. Pipeline connection binding to the `lh_vv_ctrl` SQL analytics endpoint is a Fabric DEV rollout step.
- No commit, push, or merge. No silent model substitution.

## Classification rationale

- Complexity: `high`. The change moves the control-table state owner, renames the 3rd-party source and watermark identity, and touches notebooks, seed, context, and the FL_00 pre-check. It is not a fast lane.
- Risk: `high`. Watermark, CDC state, and logs are durable state. Seeding literals instead of copying live rows changes what the next extract considers already applied. Rollback is possible while `lh_vv_bronze.ctrl` is left in place. This is not `critical` because the task does not drop the old tables or the old raw table.
- Architecture: required. State owner, `src_tbl`, watermark id, CDC partition identity, and the pipeline read location change. Commit order between DDL, seed, and the next extract must be specified.
- Evidence: not required before architecture. The new raw DDL is user-confirmed and matches the sample column list. Control grain, partitions, and column comments are in `CTRL_TABLES_CONTEXT.md`. Seed rows are generated from `NB_CREATE_DDL`, not from a DEV row count. `lh_vv_ctrl` is created by this change, so its schema is not a fact to discover. Lakehouse attachment and SQL endpoint binding are rollout steps.
- Runtime proof: required. Fabric DEV must run the DDL and seed, rerun the 3rd-party extract, and show the new watermark and `src_tbl` partition.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, `fabric-pipeline-reviewer`, and `risk-gate`.
