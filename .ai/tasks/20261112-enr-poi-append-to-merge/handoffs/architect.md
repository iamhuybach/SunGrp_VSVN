# Architect handoff: 20261112-enr-poi-append-to-merge

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261112-enr-poi-append-to-merge --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261112-enr-poi-append-to-merge/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261112-enr-poi-append-to-merge | phase=triage

## STATE

id: 20261112-enr-poi-append-to-merge
title: Switch gld_enr_poi_info and gld_enr_poi_review from APPEND to the existing gold MERGE
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: idempotency, data_evidence_required, runtime_proof_required, data_model_change
gates: evidence=pass, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: state-correctness-reviewer, spark-runtime-reviewer, sql-data-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_ENR_POI_INFO.ipynb
- notebooks/NB_ENR_POI_REVIEW.ipynb
- notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- tests/test_enr_poi_contract.py
- docs/context/gld_enr_poi_info_review.md
- docs/context/CTRL_TABLES_CONTEXT.md
- docs/context/01_DATA_MODEL.md
- docs/context/00_README.md
- docs/context/03_OPERATOR_GUIDE.md
- tests/test_initial_ddl_contract.py

## VALIDATION

PASS

## RESUME

# Resume

Status: waiting_architecture
Branch: task/20261112-enr-poi-append-to-merge at 1cadc3a
Stash: stash@{0} still holds the earlier 20261112-poi-destination-name-api snapshot. Do not pop it here.

Done this session:
- User accepted D-COL-1: row_hash STRING and deleted_at TIMESTAMP on both enr tables. Signal data_model_change is set. evidence gate is pass.
- tests/test_initial_ddl_contract.py is in scope.files.
- run-author --kind model wrote model-design.md. Claude Opus 5.5 medium, 64 s. models.author.actual = claude-opus-5-5.
- Architecture round 2 did not save. run-gate failed immutability after 455 s. rounds.architecture is still 1. architecture.md is still the round-1 EVIDENCE_REQUIRED text.
- During that run the other task's files reappeared in this working tree. The stash was not popped.

Next action:
- Do not rerun run-gate until this working tree is stable and the other task's edits are not being written here.
- Then: python scripts/vv.py run-gate 20261112-enr-poi-append-to-merge
- Round 2 must replace architecture.md using model-design.md and D-COL-1. Do not implement before PASS. Do not run Fabric.

Read next:
- .ai/tasks/20261112-enr-poi-append-to-merge/model-design.md (Conflicts and questions)
- .ai/tasks/20261112-enr-poi-append-to-merge/decision.md (D-COL-1)
- .ai/tasks/20261112-enr-poi-append-to-merge/architecture.md (round 1 only)

Waiting on:
- A quiet working tree, then a new chat to rerun the Architect gate. No Fabric step.

## REQUEST

# Request

## User outcome

Rerunning the same grain key updates the existing row in `lh_vv_gold.enr.gld_enr_poi_info` (`poi_id`) and `lh_vv_gold.enr.gld_enr_poi_review` (`review_id`). It does not insert a second row for that key.

## Scope

### In scope

- Switch those two gold targets from the current APPEND write to the MERGE contract already used by the other gold tables in `NB_LIB_TRANSFORM_SLV_GLD` and the gold `srv` notebooks.
- Keep the documented grain, columns, sources, and enrich flags. Keep every review edge `is_active = 0`.
- D-RISK-1 (updated 2026-11-12): the extra `gld_enr_poi_review` rows are old APPEND data. A correct test deletes that table's data and runs init again. Do not delete `gld_enr_poi_info`. The delete and init are a Fabric DEV runbook step, not a step this task executes. Do not turn the review edges on.
- Write mode is per target or per edge. Other APPEND targets, including `gld_enr_poi_coordinate`, stay APPEND.
- Update the places that pin APPEND for these two tables: the ctrl seed, the enrich notebooks, the library branch that is specific to them, `tests/test_enr_poi_contract.py`, `docs/context/gld_enr_poi_info_review.md`, `docs/context/CTRL_TABLES_CONTEXT.md`, `docs/context/01_DATA_MODEL.md`, `docs/context/00_README.md`, and `docs/context/03_OPERATOR_GUIDE.md`.
- Change pipeline JSON only if the write mode is stored in that file. `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json` does not contain `load_mode`, `APPEND`, or these table names.

### Out of scope

- `gld_enr_poi_coordinate` and any other remaining APPEND target.
- Turning the review flow back on.
- Column, grain, or source changes.
- `services/`, `notebooks_lgc/`, and task `20261110-serving-poi-read-apis`.
- Running a Fabric notebook or pipeline in this task.
- A new MERGE design. `sql_merge_edge_wm` is the watermark MERGE, not a second gold-target write.

## Acceptance criteria

- A rerun of the same key updates the row in place and does not add a second row.
- The MERGE key matches the grain in `docs/context/gld_enr_poi_info_review.md`: `poi_id` for info, `review_id` for review.
- `tests/test_enr_poi_contract.py` and `python scripts/vv.py verify` pass.
- No Fabric notebook or pipeline run is claimed for this task.

## Constraints

- Reuse the live gold MERGE rules for the match key, update on change, rerun, source-row disappearance, watermark, and log.
- Stop if the library has two different target-MERGE contracts. Do not pick one.
- MERGE correctness depends on the current target rows being unique on the grain key. The repository does not prove that. Do not invent row counts.
- Do not copy credentials or hosts into the repository.
- Do not change grain or the inactive review edges. D-COL-1 accepts only `row_hash` STRING and `deleted_at` TIMESTAMP on `gld_enr_poi_info` and `gld_enr_poi_review`.

## Classification rationale

- Complexity: high. The write, rerun, and watermark behavior of two gold targets changes, and the edit spans the library, ctrl seed, notebooks, tests, and operator docs.
- Risk: high. The change is idempotency of a durable gold write, and the in-place rerun is proven only at runtime.
- Architecture: required. Watermark and rerun behavior change, and the user required an architecture gate for this write-mode change. Grain and key stay as documented, so `data_model_change` is not set.
- Evidence: required. `CTRL_TABLES_CONTEXT.md` states Delta has no primary key, and these targets are APPEND. Intended grain in `docs/context/gld_enr_poi_info_review.md` does not prove the current Fabric rows are unique. Probe `evidence/probes/key-uniqueness.sql` is the smallest read-only check.
- Runtime proof: required after implementation, as a runbook only. Stop before any Fabric DEV execution.
- Reviewer routing: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`. No `fabric-pipeline-reviewer` unless a later diff touches pipeline JSON. No API reviewer. Risk is high, so the risk gate is required by the workflow.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-MERGE-1 | Hợp đồng MERGE đích | Lib có một MERGE bảng đích, `sql_merge_target`, khi `load_mode = RECOMPUTE` và `write_mode = MERGE`. Notebook gold srv gọi cùng lib. `sql_merge_edge_wm` là MERGE watermark, không phải kiểu ghi gold thứ hai. Không dừng để chọn kiểu MERGE. | Lịch sử quyết định, D-MERGE-1 | 2026-11-12 |
| D-RISK-1 | Phạm vi sau probe khóa | Sửa code MERGE cho cả hai bảng. Dòng thừa của `gld_enr_poi_review` là dữ liệu APPEND cũ. Để test đúng, xóa dữ liệu bảng đó và chạy init lại. Không xóa `gld_enr_poi_info`. Không bật cạnh review. Bước xóa và init nằm trong runbook Fabric DEV, không chạy trong task này. | Quyết định của người dùng, D-RISK-1 | 2026-11-12 |
| D-COL-1 | Hai cột kỹ thuật MERGE | Đồng ý, chấp nhận hai cột kỹ thuật. Thêm `row_hash` STRING và `deleted_at` TIMESTAMP vào `gld_enr_poi_info` và `gld_enr_poi_review`, đúng `TECH_COLUMNS` của MERGE hiện có. Không thêm cột nghiệp vụ. Không đổi grain. | Quyết định của người dùng, D-COL-1 | 2026-11-12 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 31177 bytes

## FILES

- architecture.md | 31177 bytes | large: use toc/show
- decision.md | 4961 bytes
- evidence/plan.md | 2702 bytes
- evidence/probes/key-uniqueness.sql | 1280 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/key-uniqueness.txt | 149 bytes
- handoffs/architect.md | 30615 bytes | large: use toc/show
- handoffs/author-input.md | 1807 bytes
- model-design.md | 9817 bytes
- request.md | 4077 bytes
- resume.md | 1496 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1889 bytes

## NEXT

python scripts/vv.py run-gate 20261112-enr-poi-append-to-merge

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

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

### notebooks/NB_CREATE_DDL.ipynb (343410 bytes)

[0] markdown id=b0b1203a-7c40-48bf-bfc9-7b29d7064bdc json=3-25 lines=6 | NB_CREATE_DDL — 7 bảng control `lh_vv_ctrl.dbo` | defs: none
[1] markdown id=b7e4c1a0-6f28-4d3e-9a15-2c8d0e4f6a91 json=26-36 lines=4 | Ghi chú migration 08/10 | defs: none
[2] markdown id=d20a367e-98da-4b91-9237-dd2b2cebfeae json=37-54 lines=1 | Tạo bảng ctrl_mng_pipeline_config | defs: none
[3] code id=80154b61-ea1a-415b-834c-3c07d689d036 json=55-177 lines=108 | %%sql | defs: none
[4] markdown id=<none> json=178-188 lines=5 | Reset silver (DROP/DELETE) không nằm trong luồng tạo bảng. | defs: none
[5] code id=502cd242 json=189-242 lines=40 | %%sql | defs: none
[6] markdown id=a0c11600-5f15-4ec4-ab3b-cd590b5ce6a8 json=243-260 lines=1 | Tạo bảng ctrl_mng_watermark | defs: none
[7] markdown id=e80b9799-8de0-4319-8c62-be8096d373c8 json=261-288 lines=11 | **[SỬA 03/10] Bỏ cell MERGE watermark từ `lh_vv_bronze.partner.brz_watermark`**  | defs: none
[8] code id=3ea73e14-6a1f-42a5-b960-34123b0a3fc4 json=289-350 lines=47 | %%sql | defs: none
[9] markdown id=ed3d2dc0-d9f4-4cd7-b5aa-5e65afb7aca0 json=351-368 lines=1 | Tạo bảng ctrl_cfg_schema_registry | defs: none
[10] code id=d06c9671-6b88-4afa-97a8-d028f6b9e936 json=369-412 lines=30 | CONFIG_TABLE = "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry" | defs: none
[11] code id=28e2be98-7f9a-41d5-b7f8-b4d4a5baf5ff json=413-961 lines=535 | TABLE_CONFIGS = [ | defs: none
[12] code id=0f228dc1-7bc8-4ed2-a10f-e6125a806e83 json=962-1162 lines=186 | from pyspark.sql.types import ( | defs: resolve_type, flatten_table_configs, validate_rows, seed_registry, show_registry
[13] markdown id=7517dd85-f292-4361-9d9d-6bad3f2e4f34 json=1163-1183 lines=4 | **[THÊM 03/10 - 3P] Seed registry nguồn 3rd-party `brz_3rd_crawler_poi_stream`** | defs: none
[14] code id=e9c137c5-c9fc-4f8f-a925-bc511cfd71a7 json=1184-1381 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[15] code id=0271d481-4188-43ab-8cb4-03acd3452550 json=1382-1401 lines=5 | seed_registry(TABLE_CONFIGS_3P, "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream" | defs: none
[16] markdown id=5c2996a4-3ddc-4924-8645-c0cc545cdd63 json=1402-1419 lines=1 | Tạo các bảng log & debug | defs: none
[17] code id=7dad05d9-20f0-4ab4-af1e-dec1dfe5d8cb json=1420-1561 lines=127 | %%sql | defs: none
[18] code id=ea524452-c135-4ef4-b4a8-3a076fa67ee7 json=1562-1597 lines=22 | GOLD_LOG_COLUMNS = ( | defs: none
[19] markdown id=de14c4c2-7925-4582-b080-8b0a660fb99c json=1598-1615 lines=1 | Kiểm tra cấu hình | defs: none
[20] code id=6e95fc60-2ef9-47af-a250-95844179c188 json=1616-1701 lines=71 | %%sql | defs: none
[21] code id=5784a286-d45c-4be8-8223-5a43800b6e2b json=1702-1736 lines=17 | %%sql | defs: none
[22] markdown id=enrddlmd json=1737-1746 lines=3 | [THÊM 13/10] Gold enr và cạnh PL_VV_TRANS_SLV_TO_ENR_15P | defs: none
[23] code id=enrddlpy json=1747-1890 lines=130 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _ddl, _expected_type
[24] markdown id=nonenrmd json=1891-1903 lines=1 | [THÊM 19/10] 20261019-poi-entity-non-enrich | defs: none
[25] code id=nonenrpy json=1904-1981 lines=64 | import re | defs: category_group, with_category_group
[26] markdown id=dictseedmd json=1982-1989 lines=1 | [THÊM 20/10] 20261020-dictionary-seed-from-mapping | defs: none
[27] code id=dictseedpy json=1990-2040 lines=37 | AM_FQ = "lh_vv_silver.dbo.ref_dictionary_amenities" | defs: none
[28] markdown id=entwebmd json=2041-2048 lines=1 | [THÊM 20/10] 20261020-entity-drop-op-cols-add-website | defs: none
[29] code id=entwebpy json=2049-2164 lines=102 | CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: lock_is_free
[30] markdown id=enrinfomd json=2165-2172 lines=1 | [THÊM 21/10] 20261021-refresh-gld-enr-poi-info | defs: none
[31] code id=enrinfopy json=2173-2399 lines=213 | import uuid | defs: _schema, _create
[32] markdown id=mvpoimd json=2400-2407 lines=1 | [THÊM 21/10] 20261021-move-poi-nodes-enr-15p-cleanup | defs: none
[33] code id=mvpoipy json=2408-2641 lines=220 | import uuid | defs: _names, _n, _node_edges, _info_edges
[34] markdown id=enrflagmd json=2642-2649 lines=1 | [THÊM 22/10] 20261022-enr-landing-and-gld-flags | defs: none
[35] code id=enrflagpy json=2650-2916 lines=253 | import uuid | defs: _want, _schema, _create_sql, _missing_flags, _add_flags, _edge_rows
[36] markdown id=ohpassmd json=2917-2924 lines=1 | [THÊM 23/10] 20261023-entity-opening-hours-passthrough | defs: none
[37] code id=ohpasspy json=2925-3128 lines=190 | import uuid | defs: _rows, _active, _refresh_lock, _column
[38] markdown id=peholmd json=3129-3136 lines=1 | [THÊM 23/10] 20261023-entity-phone-email-holiday | defs: none
[39] code id=peholpy json=3137-3200 lines=50 | ENTITY_FQ = "lh_vv_silver.dbo.slv_poi_entity_non_enrich" | defs: _fields, _issues
[40] markdown id=srvpoimd json=3201-3212 lines=5 | [THÊM 24/10] 20261024-gld-srv-poi-from-mapping | defs: none
[41] code id=srvpoipy json=3213-3431 lines=205 | import uuid | defs: _want, _schema, _create_sql, _edge_rows, _refresh_lock
[42] markdown id=srvratemd json=3432-3443 lines=5 | [THÊM 26/10] 20261025-gld-srv-poi-info-rating-review | defs: none
[43] code id=srvratepy json=3444-3624 lines=167 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[44] markdown id=mediaddlmd json=3625-3634 lines=3 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[45] code id=mediaddlpy json=3635-3834 lines=186 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[46] markdown id=amenddlmd json=3835-3846 lines=5 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[47] code id=amenddlpy json=3847-4038 lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[48] markdown id=plcadmd json=4039-4049 lines=4 | [THÊM 26/10] 20261026-pl-name-cadence-suffix | defs: none
[49] code id=plcadpy json=4050-4303 lines=240 | import uuid | defs: _n, _lock_rows, _refresh_lock, _issues
[50] markdown id=mlexpmd json=4304-4312 lines=2 | [THÊM 26/10] 20261026-add-poi-multi-lang-experience | defs: none
[51] code id=mlexppy json=4313-4464 lines=138 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[52] markdown id=srvrevmd json=4465-4474 lines=3 | [THÊM 27/10] 20261026-gld-srv-poi-review | defs: none
[53] code id=srvrevpy json=4475-4683 lines=195 | import uuid | defs: _want, _schema, _edge_rows, _create_sql, _refresh_lock
[54] markdown id=rvi18nenrmd json=4684-4693 lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (1/2) | defs: none
[55] code id=rvi18nenrpy json=4694-4856 lines=149 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[56] markdown id=rvi18ngldmd json=4857-4866 lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (2/2) | defs: none
[57] code id=rvi18ngldpy json=4867-5019 lines=139 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[58] markdown id=mlsrcmd json=5020-5029 lines=3 | [THÊM 04/11] 20261104-gld-srv-multi-lang-i18n-without-enr | defs: none
[59] code id=mlsrcpy json=5030-5148 lines=105 | import uuid | defs: _want, _schema, _refresh_lock
[60] markdown id=cmscfgmd json=5149-5158 lines=3 | [THÊM 08/11] 20261104-extract-cms-raw-data | defs: none
[61] code id=cmscfgpy json=5159-5268 lines=96 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _cms_ts, _cms
[62] markdown id=srvcovermd json=5269-5279 lines=4 | [THÊM 08/11] 20261108-gld-srv-poi-info-cover | defs: none
[63] code id=srvcoverpy json=5280-5471 lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[64] markdown id=poidestmd json=5472-5482 lines=4 | [THÊM 12/11] 20261112-poi-destination-name-api | defs: none
[65] code id=poidestpy json=5483-5648 lines=152 | import uuid | defs: _want, _schema, _accepted, _anchor, _refresh_lock

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (224884 bytes)

[0] markdown id=init_md json=3-10 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=11-28 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=29-43 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=44-564 lines=507 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=565-579 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=580-777 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_cfg_cms json=778-835 lines=44 | def _cms_ts(path): | defs: _cms_ts, _cms
[7] code id=init_registry_pure json=836-850 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[8] code id=init_seed_ctrl json=851-966 lines=102 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[9] code id=init_seed_place_type json=967-1435 lines=455 | import re | defs: validate_seed
[10] code id=init_seed_amenity json=1436-1740 lines=291 | import re | defs: amenity_keys, amenity_code, amenity_seed_rows, validate_seed
[11] code id=init_plan json=1741-1900 lines=146 | import json | defs: _missing, _dup_keys, _target_dup_keys
[12] code id=init_ddl json=1901-1915 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[13] code id=init_seed_write json=1916-2109 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[14] code id=init_verify json=2110-2124 lines=30 | verify_errors = [] | defs: none
[15] code id=init_exit json=2125-2139 lines=7 | summary = { | defs: none

### docs/context/CTRL_TABLES_CONTEXT.md (47988 bytes)

# CTRL_TABLES_CONTEXT — 7 bảng control `lh_vv_ctrl.dbo` | L1-L595
## 1. Tổng quan | L7-L24
## 2. Quan hệ | L25-L48
## 3. `ctrl_mng_pipeline_config` | L49-L160
### DDL | L54-L73
### Cột | L74-L89
### Dữ liệu hiện có | L90-L150
### Thao tác thường gặp | L151-L160
## 4. `ctrl_mng_watermark` | L161-L254
### DDL | L171-L195
### Cột theo loại dòng | L196-L220
### Ghi chú migration — số đo watermark trước 08/10 tại `lh_vv_bronze.ctrl` (dòng 3P cũ `wm_transform_poi_raw_event`) | L221-L230
### Thao tác thường gặp | L231-L254
## 5. `ctrl_cfg_schema_registry` | L255-L346
### DDL | L260-L284
### Luật cấu hình (lib kiểm tra, sai → `ConfigError` trước khi ghi) | L285-L295
### Dữ liệu hiện có (seed `NB_CREATE_DDL`, cấu hình chốt 04/10 chiều) | L296-L346
## 6. `ctrl_log_run` — 1 dòng / lần chạy notebook (khoá `exec_id`) | L347-L417
### DDL | L351-L391
### Cột khác nghĩa giữa extract và NB_00 | L392-L406
### Ghi chú migration — log đã thấy trước 08/10 tại vị trí control cũ | L407-L417
## 7. `ctrl_log_table_run` — 1 dòng / bảng đích (hoặc node) / lần chạy | L418-L473
### DDL | L420-L473
## 8. `ctrl_cdc_state` — 1 dòng / entity / bảng đích (chỉ extract) | L474-L513
### DDL | L478-L513
## 9. `ctrl_cdc_reject` — 1 dòng / event (hoặc phần tử) lỗi (chỉ extract) | L514-L567
### DDL | L516-L567
## 10. Lịch sử thay đổi (tóm tắt) | L568-L585
## 11. Việc còn lại liên quan ctrl | L586-L595

### docs/context/01_DATA_MODEL.md (36856 bytes)

# 01 — Data Model mới của Visit Vietnam (POI) trên Microsoft Fabric | L1-L406
## 1. Bối cảnh nền tảng | L7-L18
## 2. Nguyên tắc phân tầng (đã chốt) | L19-L35
## 3. Sơ đồ tổng | L36-L75
## 4. Bronze — bảng raw | L76-L253
### Cấu trúc `normalized_payload` | L86-L253
## 5. Silver L1 — extract (đúng cấu trúc nguồn) | L254-L318
### 5.1 Partner `slv_pn_*` (23 bảng, `load_mode = CDC`) | L256-L289
### 5.2 3rd-party `slv_3p_poi_*` (9 bảng trong registry, 9 active, snapshot) | L290-L318
## 6. Silver L2 — tích hợp POI (7 node) | L319-L348
### 6.1 Bảng ref (rule dạng dữ liệu) | L335-L348
## 7. Gold hiện hành (`lh_vv_gold.enr`) | L349-L361
## 8. Định danh | L362-L374
## 9. Model cũ (vẫn chạy song song) và lý do đổi | L375-L384
## 10. Ý nghĩa của model mới | L385-L394
## 11. Hướng sắp tới (chưa làm) | L395-L406

### docs/context/03_OPERATOR_GUIDE.md (51970 bytes)

# Hướng dẫn vận hành nền tảng | L1-L663
## 1. Bảng ctrl | L5-L232
### 1.1 `ctrl_mng_pipeline_config` | L9-L43
### 1.2 `ctrl_mng_watermark` | L44-L75
### 1.3 `ctrl_cfg_schema_registry` | L76-L120
### 1.4 `ctrl_log_run` | L121-L156
### 1.5 `ctrl_log_table_run` | L157-L185
### 1.6 `ctrl_cdc_state` | L186-L202
### 1.7 `ctrl_cdc_reject` | L203-L232
## 2. Data lineage | L233-L350
### 2.1 `gld_enr_poi_info` | L237-L264
### 2.2 `gld_enr_poi_review` | L265-L280
### 2.3 `gld_srv_poi_multi_lang` | L281-L296
### 2.4 `gld_srv_poi_info` | L297-L316
### 2.5 `gld_srv_poi_media_gallery` | L317-L324
### 2.6 `gld_srv_poi_amenity` | L325-L332
### 2.7 `gld_srv_poi_review` | L333-L350
## 3. Thêm một field bronze sang silver | L351-L437
### Step 1. Ghi một dòng vào `ctrl_cfg_schema_registry` | L355-L396
### Step 2. Giá trị phải qua được kiểm tra của extract | L397-L412
### Step 3. Chạy notebook extract để thêm cột vật lý | L413-L426
### Step 4. Nạp dữ liệu cũ của cột mới | L427-L437
## 4. Thêm một bảng bronze sang silver | L438-L546
### Step 1. Ghi một dòng `ctrl_mng_pipeline_config` | L442-L475
### Step 2. Ghi mọi cột, kể cả khoá, vào registry | L476-L479
### Step 3. Watermark chỉ khi đây là raw mới | L480-L511
### Step 4. Kiểm tra trước lần ghi dữ liệu | L512-L515
### Step 5. Chạy extract lần đầu | L516-L534
### Step 6. Tắt bảng | L535-L546
## 5. Tham số notebook | L547-L663
### 5.1 `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` | L551-L575
### 5.2 `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` | L576-L598
### 5.3 `NB_00_ORCHES_SLV_TO_ENR` | L599-L606
### 5.4 `NB_00_ORCHES_SLV_TO_GLD` | L607-L663
