# Request

## User outcome

Every silver L1 timestamp, partner and third-party, is stored as UTC `yyyy-MM-dd'T'HH:mm:ss.SSS'Z'`. Epoch values use the proven `EPOCH_S_TS`, `EPOCH_MS_TS`, or `EPOCH_US_TS` rule before that format. Existing ISO instants keep the same instant and only change format. Every silver L1 table gains audit `created_at` (first INSERT only) and `updated_at` (every MERGE), and drops `_ingested_at`.

## Scope

### In scope

- `ctrl_cfg_schema_registry` seed in `notebooks/NB_CREATE_DDL.ipynb`.
- Partner L1 `slv_pn_*` (23 tables), `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_LIB_EXTRACT_RAWDATA`.
- Third-party L1 `slv_3p_poi_*`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`.
- Context: `02_NAMING_CONVENTION.md` first, then the context files that describe L1 technical columns.
- A sanitized third-party sample in context: keys, types, and non-personal examples only.

### Out of scope

- L2 and gold `created_at` / `updated_at` / `deleted_at` semantics (`updated_at` still changes only when `row_hash` changes).
- MERGE keys, grain, partner no-regress event order, and the 3P `(_crawled_at, _event_id)` guard.
- Watermark rewind, and either flow overwriting the other flow's `src_tbl` partition.
- Dropping L1 tables. Backfill is a runtime runbook, not a DROP.

## Acceptance criteria

- Each L1 timestamp column has a unit-correct `convert_rule`, or is recorded as ISO that only needs format normalization.
- No L1 column still stores an instant as a numeric epoch.
- Both L1 flows have `created_at` and `updated_at`. No L1 `_ingested_at`.
- MERGE INSERT sets both audit columns. MERGE UPDATE changes `updated_at` and keeps `created_at`.
- `02_NAMING_CONVENTION.md` documents the timestamp format and the two audit columns.
- Context contains the sanitized 3P sample.
- `python scripts/vv.py verify <task-id>` passes.

## Constraints

- Do not infer an epoch unit from a column name. Unproven units stay on a Fabric DEV probe and the task stays at `waiting_evidence`.
- The attached 3P sample is not a schema contract.
- `DATE_DAYS` stays a date when the source value is a date. Do not invent a time of day.
- Audit timestamps are the MERGE clock, not source business timestamps.
- 3P `_first_seen_at` and `_last_seen_at` keep their current meaning. `created_at` is the silver insert time.
- New audit columns stay out of L2/gold `row_hash`. The first L2 run after backfill can change gold `updated_at` when a business timestamp changes format.
- Business `created_at` / `updated_at` already exist on partner L1. The library rejects a business column whose name matches a technical column. Those source fields must be renamed before the audit names are added. The 3P precedent is `source_created_at`.
- No commit, push, or merge.

## Classification rationale

- Complexity: high. Type changes, MERGE audit behavior, registry rules, and both extract flows. Not a fast lane.
- Risk: high. Wrong epoch unit corrupts instants; MERGE and idempotency change; formatted timestamps can change downstream `row_hash`. Rollback exists and tables are not dropped, so this is not critical.
- Architecture: required. Column types, technical columns, and MERGE behavior change.
- Evidence: required. Partner epoch units are not in the repository. See `evidence/plan.md`.
- Runtime proof: required. Backfill of existing rows, rerun, `created_at` stability, and rollback.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, then `risk-gate`.
