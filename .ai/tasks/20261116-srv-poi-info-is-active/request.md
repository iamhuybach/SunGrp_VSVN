# Request

## User outcome

`gld_srv_poi_info` gains `is_active`, and `NB_GLD_SRV_POI_INFO` writes `true` on every output row. The repository matches the PostgreSQL changes the user already applied: `apps.srv_poi_info.is_active` and `ingestion_ts` on every `apps` table in `sql/postgres/gld_srv_serve.pg.sql`. JSON API responses stay unchanged.

## Scope

### In scope

- Gold DDL for `lh_vv_gold.dbo.gld_srv_poi_info.is_active` BOOLEAN in `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables` and the matching `NB_CREATE_DDL` contract.
- `OUT_COLS` in `notebooks/NB_GLD_SRV_POI_INFO.ipynb` cell `srvinfobuild`, `docs/context/mapping_gld_srv_poi_info.md`, and `tests/test_gld_srv_poi_contract.py`.
- `sql/postgres/gld_srv_serve.pg.sql`: `apps.srv_poi_info.is_active` and `ingestion_ts timestamp without time zone` on every `CREATE TABLE apps`. Current tables: `apps.srv_poi_info`, `apps.srv_poi_multi_lang`, `apps.srv_poi_amenity`, `apps.srv_poi_media_gallery`, `apps.srv_poi_review`. Any further `CREATE TABLE apps` in that file is included. `apps.srv_poi_media_gallery.is_active` already exists and stays.
- JPA entities `SrvPoiInfo`, `SrvPoiMultiLang`, `SrvPoiAmenity`, `SrvPoiMediaGallery`, `SrvPoiReview` map the new PostgreSQL columns.
- `tests/test_srv_poi_serving_contract.py` allows the contract exception in Constraints.
- A Vietnamese `runtime-runbook.md` for the later Fabric DEV gold-column add. This session stops before that step.

### Out of scope

- Grain, keys, and JSON API fields.
- `docs/context/api-mapping/` and `docs/poi-serving-api/`.
- `is_active` or `ingestion_ts` on silver or on any gold table other than `gld_srv_poi_info.is_active`.
- A job, notebook, or pipeline that writes `ingestion_ts`.
- Task `20261112-enr-poi-append-to-merge`.
- Running a notebook, pipeline, Copy Job, or `ALTER` in this session.
- Credentials or hosts in the repository.

## Acceptance criteria

- Gold DDL, `OUT_COLS` of `NB_GLD_SRV_POI_INFO`, `docs/context/mapping_gld_srv_poi_info.md`, and `tests/test_gld_srv_poi_contract.py` include `is_active` BOOLEAN, and the value written is `true`.
- `sql/postgres/gld_srv_serve.pg.sql` and the entities include `apps.srv_poi_info.is_active` and `ingestion_ts` on every `apps` table.
- `python scripts/vv.py verify 20261116-srv-poi-info-is-active` passes when Docker is available.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `api-contract-reviewer`, `jpa-performance-reviewer`.

## Constraints

- Add `gld_srv_poi_info.is_active` BOOLEAN, nullable, immediately after `is_bookable`. `NB_GLD_SRV_POI_INFO` assigns `true` on every row it writes. Do not read it from a source and do not tie it to `deleted_at`.
- `apps.srv_poi_info.is_active` is a copy of that gold column, boolean, nullable, immediately after `is_bookable`. The user already added the column. Do not run ALTER.
- Every `apps` table in `sql/postgres/gld_srv_serve.pg.sql` receives `ingestion_ts timestamp without time zone`, nullable, immediately after `deleted_at`. The user already ran `ADD COLUMN ingestion_ts timestamp without time zone`. Do not run ALTER. Do not add `ingestion_ts` to silver or gold. Do not invent a job that writes this column.
- `CREATE TABLE` in that file must contain every column needed for a fresh install. A manual ALTER note only records columns the user already added. It is not a command for the agent to run.
- `tests/test_srv_poi_serving_contract.py` may allow `ingestion_ts` on every apps table even though gold has no such column. `apps.srv_poi_info.is_active` must match `gld_srv_poi_info`. Record this exception in `model-design.md` and `decision.md`.
- Entities map every new PostgreSQL column. Do not put `is_active` or `ingestion_ts` into the JSON API or `docs/context/api-mapping/`.
- Do not change grain or keys. Do not copy credentials or hosts into the repository.

## Classification rationale

- Complexity: medium. Signal `data_model_change` because the task adds columns. The edit spans gold DDL, one gold notebook, PostgreSQL DDL, the serving contract test, and five entities, so it is not a fast lane. No new state machine, lock, watermark, or recovery design.
- Risk: medium. The gold write is a constant boolean and the API JSON does not change. Rollback of the Fabric column is a later runbook step. Not high or critical: no data-loss path and no cross-system state machine.
- Architecture: required. `data_model_change` needs `model-design.md` before the Architect. Column ownership is split (`is_active` on gold and PostgreSQL, `ingestion_ts` on PostgreSQL only), and the change exceeds eight source files.
- Evidence: not required. Types, nullability, and the literal `true` are specified. Correctness is repository inspection plus `python scripts/vv.py verify`. No Fabric probe.
- Runtime proof: required for the gold column on Fabric DEV. This session writes `runtime-runbook.md` and stops before that step. PostgreSQL columns are already applied by the user; this session does not run `ALTER`.
- Reviewer routing: `sql-data-reviewer` for gold and PostgreSQL DDL; `spark-runtime-reviewer` for `NB_GLD_SRV_POI_INFO`; `api-contract-reviewer` because `gld_srv_serve.pg.sql` and entities change; `jpa-performance-reviewer` because entities change. No pipeline JSON, no `common/web/` or config change, risk is medium so no risk gate.
