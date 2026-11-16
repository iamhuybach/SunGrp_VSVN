# Architect handoff: 20261116-srv-poi-info-is-active

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261116-srv-poi-info-is-active --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261116-srv-poi-info-is-active/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

The first non-blank line is `RESULT: PASS` or `RESULT: EVIDENCE_REQUIRED`. Cover: scope, non-goals, invariants, state ownership, grain and keys, ordering, transaction and commit boundaries, idempotency, concurrency, retry and recovery, partial failure, observability, security, rollout, rollback and forward recovery, implementation plan, and verification. Compare material alternatives and explain the selected trade-off. Write a section that does not apply as one line: `Not applicable: <reason>`.

Size: for `low` or `medium` risk, keep the document under 25 KB, excluding `FILE:` blocks. For `high` or `critical` risk, use the space the failure analysis needs, without repeating the request or the evidence.

Files that Main must save verbatim go in blocks: a line `FILE: <repo-relative path>`, the exact content, then a line `END_FILE`. Every path must be in `scope.files`.

## Main brief contract

Return a separate Main brief, at most 14,000 characters, in English. It is the only part Main reads by default. Use `###` headings only, in this order:

1. `Decision`: at most 5 lines.
2. `Invariants Main must preserve`: at most 10 testable bullets.
3. `Edit list`: table `# | file | anchor (cell id, function, or heading) | change | done-when`, one row per anchor.
4. `Order and stop points`: numbered; mark each stop for evidence or a user decision.
5. `Tests and verification`: exact test names and commands.
6. `Read only if needed`: full-document headings mapped to the edit rows they justify.

Do not restate the request or the evidence in the brief. Code longer than 15 lines goes in the full document under a heading the edit list references.

If evidence is missing, list exact probes and the decisions each one blocks. Do not implement code, update task state, or fill gaps with assumptions.

## Generated context pack

`vv.py` generated this block. Do not re-read the task state, request, decision ledger, or task file list it covers.

# Context 20261116-srv-poi-info-is-active | phase=triage

## STATE

id: 20261116-srv-poi-info-is-active
title: Add gld_srv_poi_info.is_active and Postgres ingestion_ts
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: data_model_change
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, api-contract-reviewer, jpa-performance-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_GLD_SRV_POI_INFO.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- docs/context/mapping_gld_srv_poi_info.md
- sql/postgres/gld_srv_serve.pg.sql
- tests/test_gld_srv_poi_contract.py
- tests/test_srv_poi_serving_contract.py
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiInfo.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiMultiLang.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiAmenity.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiMediaGallery.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiReview.java

## VALIDATION

PASS

## REQUEST

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


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | `gld_srv_poi_info.is_active` | Add `gld_srv_poi_info.is_active` BOOLEAN, nullable, immediately after `is_bookable`. `NB_GLD_SRV_POI_INFO` assigns `true` on every row it writes. Do not read it from a source and do not tie it to `deleted_at`. | request.md Constraints | 2026-11-16 |
| D-2 | PostgreSQL `is_active` và `ingestion_ts` | `apps.srv_poi_info.is_active` is a copy of that gold column, boolean, nullable, immediately after `is_bookable`. The user already added the column. Do not run ALTER. Every `apps` table in `sql/postgres/gld_srv_serve.pg.sql` receives `ingestion_ts timestamp without time zone`, nullable, immediately after `deleted_at`. The user already ran `ADD COLUMN ingestion_ts timestamp without time zone`. Do not run ALTER. Do not add `ingestion_ts` to silver or gold. Do not invent a job that writes this column. | request.md Constraints | 2026-11-16 |
| D-3 | Ngoại lệ hợp đồng serving | `tests/test_srv_poi_serving_contract.py` may allow `ingestion_ts` on every apps table even though gold has no such column. `apps.srv_poi_info.is_active` must match `gld_srv_poi_info`. Record this exception in `model-design.md` and `decision.md`. | request.md Constraints | 2026-11-16 |
| D-4 | Entity và JSON API | Entities map every new PostgreSQL column. Do not put `is_active` or `ingestion_ts` into the JSON API or `docs/context/api-mapping/`. | request.md Constraints | 2026-11-16 |
| D-5 | Nơi ghi ngoại lệ D-3 | Record this exception in `model-design.md` and `decision.md`. | request.md Constraints | 2026-11-16 |
| D-6 | Kiểu Java của `ingestion_ts` | Java type follows the mapping for `timestamp without time zone` already used by `deleted_at` (`LocalDateTime deletedAt`; `GOLD_TO_JAVA["TIMESTAMP"]`). | model-design.md Columns | 2026-11-16 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: missing
size: 483 bytes

## API

service: services/data-serving-service (rules: services/data-serving-service/AGENTS.md)
test: cd services/data-serving-service && mvnw.cmd -q -B test  (JDK 26, Docker)
jdk: 26 | docker: up
runtime: user-run docker compose per runtime-runbook.md (D-12)

## FILES

- architecture.md | 483 bytes | placeholder
- decision.md | 3294 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/author-input.md | 2402 bytes
- model-design.md | 10857 bytes
- request.md | 5372 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 2150 bytes

## NEXT

python scripts/vv.py run-gate 20261116-srv-poi-info-is-active

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_GLD_SRV_POI_INFO.ipynb (21971 bytes)

[0] markdown id=srvinfomd json=unknown lines=8 | NB_GLD_SRV_POI_INFO | defs: none
[1] code id=srvinfoparam json=unknown lines=8 | p_exec_id = "" | defs: none
[2] code id=srvinforun json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=srvinfohours json=unknown lines=99 | import json | defs: _int, _open, _closed, _all_day, _dump, google_hours, partner_hours, operating_hours
[4] code id=srvinfobuild json=unknown lines=149 | ENT_COLS = ("poi_id", "poi_name", "source_name", "business_sector", "business_ca | defs: _require, _destination, _rating, _reviews, _cover, build
[5] code id=srvinfores json=unknown lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=srvinfoexit json=unknown lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (225239 bytes)

[0] markdown id=init_md json=3-10 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=11-28 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=29-43 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=44-568 lines=511 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=569-583 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=584-781 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_cfg_cms json=782-839 lines=44 | def _cms_ts(path): | defs: _cms_ts, _cms
[7] code id=init_registry_pure json=840-854 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[8] code id=init_seed_ctrl json=855-971 lines=103 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[9] code id=init_seed_place_type json=972-1440 lines=455 | import re | defs: validate_seed
[10] code id=init_seed_amenity json=1441-1745 lines=291 | import re | defs: amenity_keys, amenity_code, amenity_seed_rows, validate_seed
[11] code id=init_plan json=1746-1905 lines=146 | import json | defs: _missing, _dup_keys, _target_dup_keys
[12] code id=init_ddl json=1906-1920 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[13] code id=init_seed_write json=1921-2114 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[14] code id=init_verify json=2115-2129 lines=30 | verify_errors = [] | defs: none
[15] code id=init_exit json=2130-2144 lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (353354 bytes)

[0] markdown id=b0b1203a-7c40-48bf-bfc9-7b29d7064bdc json=unknown lines=6 | NB_CREATE_DDL — 7 bảng control `lh_vv_ctrl.dbo` | defs: none
[1] markdown id=b7e4c1a0-6f28-4d3e-9a15-2c8d0e4f6a91 json=unknown lines=4 | Ghi chú migration 08/10 | defs: none
[2] markdown id=d20a367e-98da-4b91-9237-dd2b2cebfeae json=unknown lines=1 | Tạo bảng ctrl_mng_pipeline_config | defs: none
[3] code id=80154b61-ea1a-415b-834c-3c07d689d036 json=unknown lines=108 | %%sql | defs: none
[4] markdown id=<none> json=unknown lines=5 | Reset silver (DROP/DELETE) không nằm trong luồng tạo bảng. | defs: none
[5] code id=502cd242 json=unknown lines=40 | %%sql | defs: none
[6] markdown id=a0c11600-5f15-4ec4-ab3b-cd590b5ce6a8 json=unknown lines=1 | Tạo bảng ctrl_mng_watermark | defs: none
[7] markdown id=e80b9799-8de0-4319-8c62-be8096d373c8 json=unknown lines=11 | **[SỬA 03/10] Bỏ cell MERGE watermark từ `lh_vv_bronze.partner.brz_watermark`**  | defs: none
[8] code id=3ea73e14-6a1f-42a5-b960-34123b0a3fc4 json=unknown lines=47 | %%sql | defs: none
[9] markdown id=ed3d2dc0-d9f4-4cd7-b5aa-5e65afb7aca0 json=unknown lines=1 | Tạo bảng ctrl_cfg_schema_registry | defs: none
[10] code id=d06c9671-6b88-4afa-97a8-d028f6b9e936 json=unknown lines=30 | CONFIG_TABLE = "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry" | defs: none
[11] code id=28e2be98-7f9a-41d5-b7f8-b4d4a5baf5ff json=unknown lines=535 | TABLE_CONFIGS = [ | defs: none
[12] code id=0f228dc1-7bc8-4ed2-a10f-e6125a806e83 json=unknown lines=186 | from pyspark.sql.types import ( | defs: resolve_type, flatten_table_configs, validate_rows, seed_registry, show_registry
[13] markdown id=7517dd85-f292-4361-9d9d-6bad3f2e4f34 json=unknown lines=4 | **[THÊM 03/10 - 3P] Seed registry nguồn 3rd-party `brz_3rd_crawler_poi_stream`** | defs: none
[14] code id=e9c137c5-c9fc-4f8f-a925-bc511cfd71a7 json=unknown lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[15] code id=0271d481-4188-43ab-8cb4-03acd3452550 json=unknown lines=5 | seed_registry(TABLE_CONFIGS_3P, "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream" | defs: none
[16] markdown id=5c2996a4-3ddc-4924-8645-c0cc545cdd63 json=unknown lines=1 | Tạo các bảng log & debug | defs: none
[17] code id=7dad05d9-20f0-4ab4-af1e-dec1dfe5d8cb json=unknown lines=127 | %%sql | defs: none
[18] code id=ea524452-c135-4ef4-b4a8-3a076fa67ee7 json=unknown lines=22 | GOLD_LOG_COLUMNS = ( | defs: none
[19] markdown id=de14c4c2-7925-4582-b080-8b0a660fb99c json=unknown lines=1 | Kiểm tra cấu hình | defs: none
[20] code id=6e95fc60-2ef9-47af-a250-95844179c188 json=unknown lines=71 | %%sql | defs: none
[21] code id=5784a286-d45c-4be8-8223-5a43800b6e2b json=unknown lines=17 | %%sql | defs: none
[22] markdown id=enrddlmd json=unknown lines=3 | [THÊM 13/10] Gold enr và cạnh PL_VV_TRANS_SLV_TO_ENR_15P | defs: none
[23] code id=enrddlpy json=unknown lines=130 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _ddl, _expected_type
[24] markdown id=nonenrmd json=unknown lines=1 | [THÊM 19/10] 20261019-poi-entity-non-enrich | defs: none
[25] code id=nonenrpy json=unknown lines=64 | import re | defs: category_group, with_category_group
[26] markdown id=dictseedmd json=unknown lines=1 | [THÊM 20/10] 20261020-dictionary-seed-from-mapping | defs: none
[27] code id=dictseedpy json=unknown lines=37 | AM_FQ = "lh_vv_silver.dbo.ref_dictionary_amenities" | defs: none
[28] markdown id=entwebmd json=unknown lines=1 | [THÊM 20/10] 20261020-entity-drop-op-cols-add-website | defs: none
[29] code id=entwebpy json=unknown lines=102 | CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: lock_is_free
[30] markdown id=enrinfomd json=unknown lines=1 | [THÊM 21/10] 20261021-refresh-gld-enr-poi-info | defs: none
[31] code id=enrinfopy json=unknown lines=213 | import uuid | defs: _schema, _create
[32] markdown id=mvpoimd json=unknown lines=1 | [THÊM 21/10] 20261021-move-poi-nodes-enr-15p-cleanup | defs: none
[33] code id=mvpoipy json=unknown lines=220 | import uuid | defs: _names, _n, _node_edges, _info_edges
[34] markdown id=enrflagmd json=unknown lines=1 | [THÊM 22/10] 20261022-enr-landing-and-gld-flags | defs: none
[35] code id=enrflagpy json=unknown lines=253 | import uuid | defs: _want, _schema, _create_sql, _missing_flags, _add_flags, _edge_rows
[36] markdown id=ohpassmd json=unknown lines=1 | [THÊM 23/10] 20261023-entity-opening-hours-passthrough | defs: none
[37] code id=ohpasspy json=unknown lines=190 | import uuid | defs: _rows, _active, _refresh_lock, _column
[38] markdown id=peholmd json=unknown lines=1 | [THÊM 23/10] 20261023-entity-phone-email-holiday | defs: none
[39] code id=peholpy json=unknown lines=50 | ENTITY_FQ = "lh_vv_silver.dbo.slv_poi_entity_non_enrich" | defs: _fields, _issues
[40] markdown id=srvpoimd json=unknown lines=5 | [THÊM 24/10] 20261024-gld-srv-poi-from-mapping | defs: none
[41] code id=srvpoipy json=unknown lines=205 | import uuid | defs: _want, _schema, _create_sql, _edge_rows, _refresh_lock
[42] markdown id=srvratemd json=unknown lines=5 | [THÊM 26/10] 20261025-gld-srv-poi-info-rating-review | defs: none
[43] code id=srvratepy json=unknown lines=167 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[44] markdown id=mediaddlmd json=unknown lines=3 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[45] code id=mediaddlpy json=unknown lines=186 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[46] markdown id=amenddlmd json=unknown lines=5 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[47] code id=amenddlpy json=unknown lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[48] markdown id=plcadmd json=unknown lines=4 | [THÊM 26/10] 20261026-pl-name-cadence-suffix | defs: none
[49] code id=plcadpy json=unknown lines=240 | import uuid | defs: _n, _lock_rows, _refresh_lock, _issues
[50] markdown id=mlexpmd json=unknown lines=2 | [THÊM 26/10] 20261026-add-poi-multi-lang-experience | defs: none
[51] code id=mlexppy json=unknown lines=138 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[52] markdown id=srvrevmd json=unknown lines=3 | [THÊM 27/10] 20261026-gld-srv-poi-review | defs: none
[53] code id=srvrevpy json=unknown lines=195 | import uuid | defs: _want, _schema, _edge_rows, _create_sql, _refresh_lock
[54] markdown id=rvi18nenrmd json=unknown lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (1/2) | defs: none
[55] code id=rvi18nenrpy json=unknown lines=149 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[56] markdown id=rvi18ngldmd json=unknown lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (2/2) | defs: none
[57] code id=rvi18ngldpy json=unknown lines=139 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[58] markdown id=mlsrcmd json=unknown lines=3 | [THÊM 04/11] 20261104-gld-srv-multi-lang-i18n-without-enr | defs: none
[59] code id=mlsrcpy json=unknown lines=105 | import uuid | defs: _want, _schema, _refresh_lock
[60] markdown id=cmscfgmd json=unknown lines=3 | [THÊM 08/11] 20261104-extract-cms-raw-data | defs: none
[61] code id=cmscfgpy json=unknown lines=96 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _cms_ts, _cms
[62] markdown id=srvcovermd json=unknown lines=4 | [THÊM 08/11] 20261108-gld-srv-poi-info-cover | defs: none
[63] code id=srvcoverpy json=unknown lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[64] markdown id=poidestmd json=unknown lines=4 | [THÊM 12/11] 20261112-poi-destination-name-api | defs: none
[65] code id=poidestpy json=unknown lines=152 | import uuid | defs: _want, _schema, _accepted, _anchor, _refresh_lock
[66] markdown id=enrmergemd json=unknown lines=1 | [THÊM 12/11] 20261112-enr-poi-append-to-merge | defs: none
[67] code id=enrmergepy json=unknown lines=163 | import uuid | defs: _release_lock, _refresh_lock, _types, _modes, _run
