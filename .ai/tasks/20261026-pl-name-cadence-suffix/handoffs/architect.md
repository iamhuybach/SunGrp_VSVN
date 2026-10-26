# Architect handoff: 20261026-pl-name-cadence-suffix

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261026-pl-name-cadence-suffix --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261026-pl-name-cadence-suffix/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261026-pl-name-cadence-suffix | phase=triage

## STATE

id: 20261026-pl-name-cadence-suffix
title: Rename recompute pl_name cadence suffix P to M
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: cross_system, idempotency, runtime_proof_required
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: state-correctness-reviewer, sql-data-reviewer, spark-runtime-reviewer, fabric-pipeline-reviewer
open findings: none
exceptions: none
scope.files:
- AGENTS.md
- docs/context/02_NAMING_CONVENTION.md
- docs/context/CTRL_TABLES_CONTEXT.md
- notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_00_ORCHES_SLV_TO_ENR_15P.ipynb
- notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb
- notebooks/NB_SETUP_POI_ENTITY.ipynb
- notebooks/NB_SETUP_POI_AMENITY.ipynb
- pipelines/PL_VV_TRANS_SLV_TO_ENR_15P/PL_VV_TRANS_SLV_TO_ENR_15P.json
- tests/test_initial_ddl_contract.py
- tests/test_enr_poi_contract.py
- tests/test_poi_entity_contract.py
- tests/test_poi_amenity_contract.py
- tests/test_poi_media_amenity_contract.py

## VALIDATION

PASS

## REQUEST

# Request

## User outcome

Every active `pl_name` that ends in `_15P` or `_30P` uses the cadence suffix `CADENCE_RE` already accepts, so the transform library applies the fast-flow versus slow-flow node check. The business reason: the library reads cadence from the suffix and skips that check when the suffix is `P`.

## Scope

### In scope

- Rename only the suffix, keeping the prefix and the number: `_15P` becomes `_15M`, `_30P` becomes `_30M`.
- `PL_VV_TRANS_SLV_TO_ENR_15P` becomes `PL_VV_TRANS_SLV_TO_ENR_15M`.
- `PL_VV_TRANS_SLV_TO_GLD_30P` becomes `PL_VV_TRANS_SLV_TO_GLD_30M`.
- Active `pl_name` values in notebooks, pipeline JSON, tests, the standard sentence in `AGENTS.md`, and `docs/context/02_NAMING_CONVENTION.md` §3.
- `NB_SETUP_INITIAL_DDL`: edit the seed in place.
- `NB_CREATE_DDL`: leave existing cells unchanged. Append one markdown cell `[THÊM 26/10] 20261026-pl-name-cadence-suffix` and one self-contained patch cell at the end.
- The patch updates existing ctrl rows to the new name, including watermark rows that carry the old `pl_name`. A second run does not change the result. No `DROP` of a table. No delete of a watermark row.
- Ctrl `pl_name` matches the pipeline name that calls the notebook.
- Rename the folder and file `pipelines/PL_VV_TRANS_SLV_TO_ENR_15P/PL_VV_TRANS_SLV_TO_ENR_15P.json` to the new pipeline name, and make the activity parameter `p_pl_name` follow that name.
- Notebooks that assign the operational name, including `NB_SETUP_POI_ENTITY` and `NB_SETUP_POI_AMENITY`.
- The default `p_pl_name` in `NB_00_ORCHES_SLV_TO_ENR_15P`. The notebook file name stays.

### Out of scope

- Widening `CADENCE_RE`, or treating `P` as minutes. Do not edit the cadence check in `NB_LIB_TRANSFORM_SLV_GLD`.
- `pl_name` values that already end in `_1H`, `_1D`, `_15M`, or `FL_00`. `NB_00_ORCHES_SLV_TO_GLD` cell 1 defaults to `PL_VV_TRANSFORM_SLV_TO_GLD_1H` and stays.
- Creating a pipeline JSON for the 30-minute flow. The repo has none for `_30P`. The runbook tells the user to create or rename the matching Fabric pipeline before a manual run with the new `p_pl_name`.
- Renaming notebook files. `NB_00_ORCHES_SLV_TO_ENR_15P` is a notebook name, not a `pl_name`. The §2 example of that notebook name stays.
- Other tasks' artifacts, `notebooks_lgc/`, `docs/context/3p-google/*.txt`, and pipeline manifests.
- `data_model_change`. No `model-design.md`.
- Rewriting historical mentions in requirements, mapping docs, or `CTRL_TABLES_CONTEXT.md`.

## Acceptance criteria

- The repo has no active `pl_name` ending in `_15P` or `_30P` in notebooks, pipeline JSON, tests, the standard sentence in `AGENTS.md`, and `docs/context/02_NAMING_CONVENTION.md` §3.
- `NB_SETUP_INITIAL_DDL` seeds the new names in place. `NB_CREATE_DDL` adds only the dated markdown cell and one self-contained patch cell. Old cells stay byte-for-byte.
- The patch renames existing ctrl rows, including watermark rows attached to the old `pl_name`. Rerun does not change the result. No table `DROP`. No watermark delete.
- Ctrl `pl_name` equals the calling pipeline name. The enrich pipeline JSON folder, file, and activity `p_pl_name` follow `PL_VV_TRANS_SLV_TO_ENR_15M`.
- The activity already passes `p_pl_name` as `@pipeline().Pipeline`. Keep that expression. Change the pipeline resource name so the expression yields the new name.
- There is still no `_30M` pipeline JSON. The runbook states that the user creates or renames the Fabric pipeline before a manual run with `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_30M`.
- `CADENCE_RE` in `NB_LIB_TRANSFORM_SLV_GLD` is unchanged.

## Constraints

- Domain: pipeline, ctrl, lib transform/gold.
- Watermark key, from the repo, is not an evidence gap. `flow_lock_id(pl_name)` returns `wm_flow__{pl_name}`. `ensure_lock_row` writes `watermark_id`, `src_tbl = pl_name`, and `flow_name` as the notebook name. Lock updates match `watermark_id`. Edge ids `wm_e__<trg_tbl>__<src_tbl>` do not contain `pl_name`. `ctrl_mng_pipeline_config` logical key includes `pl_name` (`docs/context/02_NAMING_CONVENTION.md` §4, `docs/context/CTRL_TABLES_CONTEXT.md` §3 and §4).
- `NB_SETUP_INITIAL_DDL` seeds with `MERGE … WHEN NOT MATCHED THEN INSERT` only. The in-place seed change is for a new environment. The `NB_CREATE_DDL` patch is what renames rows that already exist (`docs/context/02_NAMING_CONVENTION.md` §2.1).
- Do not invent an `UPDATE` for a watermark column the repo does not use as the lock key.
- Historical `NB_CREATE_DDL` cells still contain the old names. That text is history, not the active `pl_name`. Tests must expect the active name after the seed and the new patch, not require `_15P` or `_30P` as the live value.
- Known mentions outside the acceptance surface stay: other `.ai/tasks/`, `docs/requirements/`, mapping docs, `docs/context/CTRL_TABLES_CONTEXT.md`, `docs/context/00_README.md`, `docs/context/01_DATA_MODEL.md`, `docs/context/NB_00_ORCHES_SLV_TO_GLD.md`.

## Classification rationale

- Complexity: high. The rename crosses pipeline JSON, ctrl seed and patch, orchestrator parameters, setup notebooks, tests, and the naming standard.
- Risk: high. The flow-lock id and `src_tbl` change with `pl_name`. A wrong rename can leave two lock rows or point a run at the wrong flow. Rollback is a reverse rename, and the cadence check starts to run only after the suffix matches.
- Architecture: required. The control key and the pipeline resource name change, and watermark identity moves with `pl_name`. Pipeline orchestration identity changes. Not a table grain or column change, so no `data_model_change`.
- Evidence: not required. The lock key is `wm_flow__{pl_name}` plus `src_tbl = pl_name` in `NB_LIB_TRANSFORM_SLV_GLD`. DEV row counts are not required to write an idempotent rename of that key.
- Runtime proof: required. After the user renames or creates the Fabric pipelines and runs the patch, one `PLAN` of `PL_VV_TRANS_SLV_TO_ENR_15M` and one `PLAN` of `PL_VV_TRANS_SLV_TO_GLD_30M` should show no WARN `Không đọc được nhịp` for those two names.
- Reviewer routing: `state-correctness-reviewer` (lock id, idempotent rename), `sql-data-reviewer` (patch statements), `spark-runtime-reviewer` (notebook parameter and patch cell), `fabric-pipeline-reviewer` (pipeline resource name and `p_pl_name`). Risk is high, so `risk-gate` runs. Signal: `cross_system`, plus `idempotency` and `runtime_proof_required`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: missing
size: 483 bytes

## FILES

- architecture.md | 483 bytes | placeholder
- decision.md | 721 bytes | placeholder
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/author-input.md | 2642 bytes
- request.md | 6459 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 2023 bytes

## NEXT

python scripts/vv.py run-gate 20261026-pl-name-cadence-suffix

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### docs/context/CTRL_TABLES_CONTEXT.md (46571 bytes)

# CTRL_TABLES_CONTEXT — 7 bảng control `lh_vv_ctrl.dbo` | L1-L581
## 1. Tổng quan | L7-L24
## 2. Quan hệ | L25-L48
## 3. `ctrl_mng_pipeline_config` | L49-L151
### DDL | L54-L73
### Cột | L74-L89
### Dữ liệu hiện có | L90-L141
### Thao tác thường gặp | L142-L151
## 4. `ctrl_mng_watermark` | L152-L244
### DDL | L162-L186
### Cột theo loại dòng | L187-L211
### Ghi chú migration — số đo watermark trước 08/10 tại `lh_vv_bronze.ctrl` (dòng 3P cũ `wm_transform_poi_raw_event`) | L212-L220
### Thao tác thường gặp | L221-L244
## 5. `ctrl_cfg_schema_registry` | L245-L334
### DDL | L250-L274
### Luật cấu hình (lib kiểm tra, sai → `ConfigError` trước khi ghi) | L275-L285
### Dữ liệu hiện có (seed `NB_CREATE_DDL`, cấu hình chốt 04/10 chiều) | L286-L334
## 6. `ctrl_log_run` — 1 dòng / lần chạy notebook (khoá `exec_id`) | L335-L405
### DDL | L339-L379
### Cột khác nghĩa giữa extract và NB_00 | L380-L394
### Ghi chú migration — log đã thấy trước 08/10 tại vị trí control cũ | L395-L405
## 7. `ctrl_log_table_run` — 1 dòng / bảng đích (hoặc node) / lần chạy | L406-L461
### DDL | L408-L461
## 8. `ctrl_cdc_state` — 1 dòng / entity / bảng đích (chỉ extract) | L462-L501
### DDL | L466-L501
## 9. `ctrl_cdc_reject` — 1 dòng / event (hoặc phần tử) lỗi (chỉ extract) | L502-L555
### DDL | L504-L555
## 10. Lịch sử thay đổi (tóm tắt) | L556-L571
## 11. Việc còn lại liên quan ctrl | L572-L581

### notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb (125971 bytes)

[0] markdown id=026c3072 json=3-55 lines=46 | NB_LIB_TRANSFORM_SLV_GLD — Thư viện dùng chung cho luồng silver → silver L2 → go | defs: none
[1] code id=9ff87eee json=56-141 lines=72 | import json | defs: none
[2] markdown id=bf3d6ad5 json=142-149 lines=1 | 2. common — thời gian, tham số, log, retry, tên bảng, append | defs: none
[3] code id=649c6944 json=150-301 lines=138 | _LOG_LOCK = threading.Lock() | defs: ConfigError, QualityGateError, utc_now, to_bool, split_csv, short_error, log, is_transient, with_retry, is_identifier, is_fq_name, quote_name, table_exists, table_columns, append_rows, json_dumps, current_notebook_name, cadence_minutes, edge_wm_id, flow_lock_id, require_ctrl_columns
[4] markdown id=10ad924b json=302-317 lines=9 | 3. delta — trạng thái bảng, history, commit đổi dữ liệu, đọc theo version | defs: none
[5] code id=5217686f json=318-422 lines=91 | def table_state(fq: str) -> Optional[dict]: | defs: table_state, table_history, is_data_change, HistoryCache, __init__, changes, read_at, read_current
[6] markdown id=4accd2b3 json=423-436 lines=7 | 4. config / DAG | defs: none
[7] code id=b3673b19 json=437-629 lines=179 | @dataclass(frozen=True) | defs: Edge, src_fq, trg_fq, wm_id, Dag, descendants, node_by_name, load_config_rows, node_owner, build_dag
[8] markdown id=176b794b json=630-646 lines=10 | 5. ctrl — hộp thư cạnh, khoá luồng, run log, table log | defs: none
[9] code id=5cd650fc json=647-930 lines=270 | WM_EDGE_SCHEMA = T.StructType([ | defs: load_edge_wm, edge_status, sql_merge_edge_wm, merge_edge_wm, sql_ensure_lock_row, ensure_lock_row, _lock_expired_sql, read_flow_lock, _update_lock_row, acquire_flow_lock, release_flow_lock, refresh_flow_lock, close_stale_runs, write_run_log, update_run_log, write_node_log, node_logs, last_output_versions
[10] markdown id=191e1851 json=931-959 lines=22 | 6. node — `NodeSpec`, `NodeContext`, QG, MERGE row_hash, `run_node` | defs: none
[11] code id=926a3f9c json=960-1664 lines=691 | @dataclass | defs: NodeSpec, NodeContext, __init__, input, is_empty, current_target, warn, _input_at, changed, _hash_expr, add_row_hash, quality_gate, diff_counts, target_ddl, ensure_target, sql_merge_target, merge_target, _resolve_node, choose_append_baseline, append_history_stops, parse_append_marker, _version_unavailable, _align_snapshot, find_append_marker, check_append_schema, _reject_append_build, append_target, _once, execute_append, run_node, finish_node
[12] markdown id=3650f3b1 json=1665-1684 lines=13 | 7. orchestrator — `plan_run`, DAG runMultiple, gom kết quả, tiến cạnh, `orchestr | defs: none
[13] code id=294534d1 json=1685-1968 lines=270 | @dataclass | defs: Plan, plan_run, plan_summary, print_plan, build_run_multiple_dag, collect_outcomes, advance_edges, _validate_orch_params, orchestrate
[14] markdown id=46eb3baf json=1969-1988 lines=13 | 8. build helpers — chuẩn hoá chữ, bỏ dấu, slug, uuid md5, epoch, JSON | defs: none
[15] code id=4938ec32 json=1989-2098 lines=96 | TOAST_SENTINEL = "__debezium_unavailable_value" | defs: _build_unaccent_map, clean_str, norm_text, norm_admin, unaccent, slugify, uuid_md5, epoch_to_ts, json_scalar, json_array_at, json_sorted_array, iso_utc_ts

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (224627 bytes)

[0] markdown id=init_md json=unknown lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=unknown lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=unknown lines=480 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=unknown lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=unknown lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=unknown lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=unknown lines=85 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[8] code id=init_seed_place_type json=unknown lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=unknown lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=unknown lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=unknown lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=unknown lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=unknown lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=unknown lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (251153 bytes)

[0] markdown id=b0b1203a-7c40-48bf-bfc9-7b29d7064bdc json=unknown lines=6 | NB_CREATE_DDL — 7 bảng control `lh_vv_ctrl.dbo` | defs: none
[1] markdown id=b7e4c1a0-6f28-4d3e-9a15-2c8d0e4f6a91 json=unknown lines=4 | Ghi chú migration 08/10 | defs: none
[2] markdown id=d20a367e-98da-4b91-9237-dd2b2cebfeae json=unknown lines=1 | Tạo bảng ctrl_mng_pipeline_config | defs: none
[3] code id=80154b61-ea1a-415b-834c-3c07d689d036 json=unknown lines=108 | %%sql | defs: none
[4] markdown id=<none> json=unknown lines=5 | Reset silver (DROP/DELETE) không nằm trong luồng tạo bảng. | defs: none
[5] code id=502cd242 json=unknown lines=40 | %%sql | defs: none
[6] markdown id=a0c11600-5f15-4ec4-ab3b-cd590b5ce6a8 json=unknown lines=1 | Tạo bảng ctrl_mng_watermark | defs: none
[7] markdown id=e80b9799-8de0-4319-8c62-be8096d373c8 json=unknown lines=11 | **[SỬA 03/10] Bỏ cell MERGE watermark từ `lh_vv_bronze.partner.brz_watermark`**  | defs: none
[8] code id=3ea73e14-6a1f-42a5-b960-34123b0a3fc4 json=unknown lines=43 | %%sql | defs: none
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
[46] markdown id=amenddlmd json=unknown lines=3 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[47] code id=amenddlpy json=unknown lines=177 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql

### notebooks/NB_SETUP_POI_ENTITY.ipynb (81268 bytes)

[0] markdown id=a1setupmd json=47-58 lines=5 | NB_SETUP_POI_ENTITY | defs: none
[1] code id=a1setupparam json=59-76 lines=1 | p_apply = "false" | defs: none
[2] code id=a1setuprun json=77-91 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=a1setupseed json=92-557 lines=452 | import re | defs: validate_seed
[4] code id=a1setupplan json=558-628 lines=57 | import json | defs: none
[5] code id=a1setupddl json=629-679 lines=37 | spark.sql(""" | defs: none
[6] code id=a1setupmerge json=680-753 lines=60 | def _seed_merge(): | defs: _seed_merge
[7] code id=a1setupedges json=754-956 lines=189 | import uuid | defs: setup_edge_issues, _write_edges
[8] code id=a1setupexit json=957-981 lines=11 | import json | defs: none

### notebooks/NB_SETUP_POI_AMENITY.ipynb (57271 bytes)

[0] markdown id=c1setupmd json=47-56 lines=3 | NB_SETUP_POI_AMENITY | defs: none
[1] code id=c1setupparam json=57-66 lines=1 | p_apply = "false" | defs: none
[2] code id=c1setuprun json=67-76 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=c1setupseed json=77-345 lines=260 | import re | defs: amenity_keys, validate_seed
[4] code id=c1setupplan json=346-412 lines=58 | import json | defs: none
[5] code id=c1setupddl json=413-481 lines=60 | spark.sql(""" | defs: none
[6] code id=c1setupmerge json=482-558 lines=68 | def _seed_merge(): | defs: _seed_merge
[7] code id=c1setupedges json=559-744 lines=177 | import uuid | defs: setup_edge_issues, _write_edges
[8] code id=c1setupexit json=745-765 lines=12 | import json | defs: none
