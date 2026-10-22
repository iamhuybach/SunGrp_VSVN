# Architect handoff: 20261021-move-poi-nodes-enr-15p-cleanup

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261021-move-poi-nodes-enr-15p-cleanup --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261021-move-poi-nodes-enr-15p-cleanup/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261021-move-poi-nodes-enr-15p-cleanup | phase=triage

## STATE

id: 20261021-move-poi-nodes-enr-15p-cleanup
title: Move amenity and entity nodes to ENR 15P and drop unused POI objects
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: stateful_logic, idempotency, cross_system, design_tradeoffs, cross_state_impact, runtime_proof_required, data_evidence_required, data_model_change
gates: evidence=pass, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: fabric-pipeline-reviewer, state-correctness-reviewer, sql-data-reviewer, spark-runtime-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_SETUP_POI_ENTITY.ipynb
- notebooks/NB_SETUP_POI_AMENITY.ipynb
- notebooks/NB_SLV_PN_POI.ipynb
- notebooks/NB_ENR_POI_COORDINATE.ipynb
- tests/test_poi_entity_contract.py
- tests/test_poi_amenity_contract.py
- tests/test_initial_ddl_contract.py
- tests/test_enr_poi_contract.py
- docs/context/CTRL_TABLES_CONTEXT.md
- docs/context/01_DATA_MODEL.md

## VALIDATION

PASS

## RESUME

# Resume

## Status

waiting_evidence. gates.evidence is pending. Architecture has not started.

## Done this session

Opened `20261021-move-poi-nodes-enr-15p-cleanup`. Classified high/high with architecture, evidence, and runtime required. Wrote the working scope in `request.md` and a read-only DEV probe.

## Next action

Read `evidence/results/ctrl-inventory.txt`. If the user corrects the working scope, update `decision.md` before any design. Then `run-author --kind model`, then `transition` to `waiting_architecture` and `run-gate`.

## Read next

- `.ai/tasks/20261021-move-poi-nodes-enr-15p-cleanup/request.md` — Cách hiểu đang dùng
- `.ai/tasks/20261021-move-poi-nodes-enr-15p-cleanup/evidence/probes/ctrl-inventory.sql`
- `.ai/tasks/20261021-move-poi-nodes-enr-15p-cleanup/evidence/results/ctrl-inventory.txt`

## Waiting on

The user confirms or corrects the working scope, and pastes the DEV probe output. Open a new chat for that phase.

## REQUEST

# Request

## User outcome

Chuyển `slv_poi_amenity` và `slv_poi_entity_non_enrich` từ `PL_VV_TRANS_SLV_TO_SLV_1H` sang `PL_VV_TRANS_SLV_TO_ENR_15P`, vì hai bảng này là đầu vào của các bảng đích trong luồng 15 phút.

Làm sạch môi trường: xóa bảng và cấu hình không còn dùng.

- Bảng: `gld_enr_poi_coordinate`, `slv_pn_poi`.
- Luồng `gld_enr_poi_info` cũ, chạy bằng `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_3p_poi`.
- Luồng `slv_pn_poi`.

## Cách hiểu đang dùng

Chưa phải quyết định đã chốt. Sửa lại nếu khác ý.

- Chuyển mọi cạnh `ctrl_mng_pipeline_config` có `trg_tbl` là `slv_poi_amenity` hoặc `slv_poi_entity_non_enrich` từ `PL_VV_TRANS_SLV_TO_SLV_1H` sang `PL_VV_TRANS_SLV_TO_ENR_15P`. Mỗi node chỉ thuộc một pipeline active. Seed hiện có 6 cạnh vào entity và 3 cạnh vào amenity, gồm cạnh `slv_3p_poi_contact` → `slv_poi_entity_non_enrich`.
- `PL_VV_TRANS_SLV_TO_ENR_15P` chỉ gọi `NB_00_ORCHES_SLV_TO_ENR_15P`. Thứ tự node lấy từ cạnh ctrl. Hai node silver phải chạy trong cùng DAG với `gld_enr_poi_info`.
- Không đổi pipeline JSON. Không có file pipeline cho `PL_VV_TRANS_SLV_TO_SLV_1H`.
- Xóa cấu hình nghĩa là xóa dòng ctrl, không chỉ đặt `is_active = 0`.
- Luồng info cũ là 3 cạnh đã tắt: `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact` → `gld_enr_poi_info`. Không DROP ba bảng silver L1 đó. Không tắt các cạnh info đang active (`slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_review`, `slv_poi_entity_non_enrich`, `slv_poi_amenity`, `slv_pn_business_service_i18ns`).
- Luồng `slv_pn_poi` là 2 cạnh active trên `PL_VV_TRANS_SLV_TO_ENR_15P`: `slv_pn_business_services` và `slv_pn_business_service_i18ns` → `slv_pn_poi`, notebook `NB_SLV_PN_POI`.
- Luồng coordinate là 3 cạnh đã tắt tới `gld_enr_poi_coordinate`, notebook `NB_ENR_POI_COORDINATE`.
- DROP `lh_vv_gold.enr.gld_enr_poi_coordinate` và `lh_vv_silver.dbo.slv_pn_poi` trên Fabric DEV. Gỡ DDL, seed, notebook và test tương ứng trong repo.
- Watermark cạnh `wm_e__<trg>__<src>` và khoá `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H` nằm trong phạm vi dọn nếu probe thấy chúng. Không xóa `ctrl_log_run` hay `ctrl_log_table_run`.
- Không đụng `gld_enr_poi_review`, `slv_poi_entity`, hay các cạnh extract `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`.
- Sau khi chuyển, seed không còn cạnh `PL_VV_TRANS_SLV_TO_SLV_1H`.

## Scope

### In scope

- Cạnh ctrl và seed của hai node `slv_poi_amenity`, `slv_poi_entity_non_enrich`.
- Xóa cạnh và notebook của `slv_pn_poi` và `gld_enr_poi_coordinate`.
- DROP hai bảng đó trên Fabric DEV, có rollback trong runbook.
- `NB_SETUP_INITIAL_DDL` sửa định nghĩa tại chỗ. `NB_CREATE_DDL` chỉ thêm cell patch mới.
- `NB_SETUP_POI_ENTITY`, `NB_SETUP_POI_AMENITY`, và test contract đang khóa tên pipeline hoặc hai bảng bị xóa.
- Đoạn mô tả pipeline trong `docs/context/CTRL_TABLES_CONTEXT.md` và `docs/context/01_DATA_MODEL.md` cho đúng seed mới.

### Out of scope

- Logic build của `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_SLV_POI_AMENITY`, `NB_ENR_POI_INFO`, `NB_ENR_POI_REVIEW`.
- DROP `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_poi_entity`.
- Xóa log lịch sử.
- Commit, merge, hoặc chạy notebook trên Fabric. Người dùng chạy probe và runbook.

## Acceptance criteria

- Mọi cạnh active của `slv_poi_amenity` và `slv_poi_entity_non_enrich` có `pl_name = PL_VV_TRANS_SLV_TO_ENR_15P`. Không còn cạnh active nào của hai bảng này trên `PL_VV_TRANS_SLV_TO_SLV_1H`.
- `NB_00_ORCHES_SLV_TO_ENR_15P` xếp `slv_poi_entity_non_enrich` trước `slv_poi_amenity`, và cả hai trước `gld_enr_poi_info`.
- Không còn dòng ctrl tới `slv_pn_poi` hoặc `gld_enr_poi_coordinate`.
- Không còn 3 cạnh info cũ từ `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`.
- Trên Fabric DEV, hai bảng `gld_enr_poi_coordinate` và `slv_pn_poi` không còn. `gld_enr_poi_info` và `gld_enr_poi_review` còn.
- Chạy lại cell patch không tạo lại cạnh đã xóa và không nhân đôi cạnh đã chuyển.
- Repo không còn `NB_SLV_PN_POI` và `NB_ENR_POI_COORDINATE`.

## Constraints

- Chỉ Fabric DEV. Không đụng staging hay production.
- Không bịa dòng ctrl hoặc watermark còn sống ngoài probe.
- `NB_CREATE_DDL`: thêm cell patch, không viết lại cell lịch sử.
- Một node không được có cạnh active ở hai pipeline.
- Probe và runbook do người dùng chạy. Agent không ghi nhận là đã chạy Fabric.

## Classification rationale

- Complexity: high. Đổi pipeline của node có cạnh, watermark và notebook setup; đồng thời DROP bảng và xóa cấu hình.
- Risk: high. Xóa bảng và đổi DAG ctrl có thể làm lệch watermark hoặc thứ tự chạy. Rollback bằng Delta time travel và seed đã biết, nên không xếp critical.
- Architecture: required. Đổi cấu trúc orchestration, chủ sở hữu trạng thái ctrl, và ranh giới commit giữa patch config và DROP.
- Evidence: required. Tập cạnh và watermark đang sống trên DEV quyết định patch xóa gì. Seed trong repo không chứa mọi dòng đã retire trên DEV.
- Runtime proof: required. Phải thấy DAG 15 phút chạy đúng thứ tự và hai bảng đã DROP.
- Reviewer routing: `fabric-pipeline-reviewer`, `state-correctness-reviewer`, `sql-data-reviewer`, `spark-runtime-reviewer`, rồi `risk-gate`.
- `data_model_change`: sau evidence, `model-design.md` phải có trước Architect.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Probe | INV-1 = 24 và INV-2 có 24 dòng. INV-3 = 23 và INV-4 có 23 dòng. Không câu nào chạm 50 dòng. INV-5 đến INV-8 đều trả một số đếm. Mọi `lock_exec_id` và `lock_at` đều null. | evidence/results/ctrl-inventory.txt | 2026-10-21 |
| D-02 | Pipeline hai node | Trên DEV, 3 cạnh `slv_poi_amenity` và 6 cạnh `slv_poi_entity_non_enrich` đã có `pl_name = PL_VV_TRANS_SLV_TO_ENR_15P`, `is_active = 1`. Không có dòng ctrl nào thuộc `PL_VV_TRANS_SLV_TO_SLV_1H`. Seed repo vẫn gán 9 cạnh đó cho `PL_VV_TRANS_SLV_TO_SLV_1H`. Repo phải đổi theo DEV. Patch DEV không được nhân đôi cạnh đã ở ENR. | evidence/results/ctrl-inventory.txt INV-2; notebooks/NB_SETUP_INITIAL_DDL.ipynb cell `init_seed_ctrl` | 2026-10-21 |
| D-03 | Cạnh và watermark xóa | Xóa 3 cạnh `gld_enr_poi_coordinate` (`is_active = 0`), 3 cạnh info cũ từ `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact` (`is_active = 0`), và 2 cạnh `slv_pn_poi` (`is_active = 1`). Xóa 3 watermark coordinate, 2 watermark `slv_pn_poi`, và `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H` (`status = NO_DATA`, `flow_name = NB_SLV_POI_ENTITY`). Ba cạnh info cũ không có watermark. Giữ 7 watermark info đang active, 9 watermark của hai node, và `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`. | evidence/results/ctrl-inventory.txt INV-2, INV-4 | 2026-10-21 |
| D-04 | DROP | DROP trên Fabric DEV: `lh_vv_gold.enr.gld_enr_poi_coordinate` (94 dòng) và `lh_vv_silver.dbo.slv_pn_poi` (30 dòng). Giữ `slv_poi_amenity` (58 dòng) và `slv_poi_entity_non_enrich` (65 dòng). Không đổi grain hay cột của hai bảng giữ. | evidence/results/ctrl-inventory.txt INV-5 đến INV-8; request.md User outcome | 2026-10-21 |
| D-05 | Model | `model-design.md` là hợp đồng model. Không có `proposal.md` vì task không đi lane proposal. `NB_SETUP_INITIAL_DDL` cell `init_tables` không có `target_table` cho hai bảng bị xóa. Câu hỏi 4 và 5 trong model không chặn DROP: cột coordinate nằm ở cell `init_tables`; cột business của `slv_pn_poi` nằm ở `NB_SLV_PN_POI` cell `379af200`. `architecture.md` hiện là template, chưa phải output của Architect. | model-design.md Conflicts and questions; notebooks/NB_SETUP_INITIAL_DDL.ipynb cell `init_tables` | 2026-10-21 |

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
- decision.md | 3932 bytes
- evidence/plan.md | 1876 bytes
- evidence/probes/ctrl-inventory.sql | 3859 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/ctrl-inventory.txt | 6676 bytes
- handoffs/author-input.md | 1551 bytes
- model-design.md | 13466 bytes
- request.md | 5813 bytes
- resume.md | 982 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1990 bytes

## NEXT

python scripts/vv.py run-gate 20261021-move-poi-nodes-enr-15p-cleanup

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (208032 bytes)

[0] markdown id=init_md json=47-54 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=55-72 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=73-87 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=88-452 lines=351 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=453-467 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=468-665 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=666-680 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=681-766 lines=72 | _FL00, _ENR, _SLV1H = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV | defs: none
[8] code id=init_seed_place_type json=767-1235 lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=1236-1511 lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=1512-1669 lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=1670-1684 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=1685-1878 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=1879-1893 lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=1894-1908 lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (158162 bytes)

[0] markdown id=b0b1203a-7c40-48bf-bfc9-7b29d7064bdc json=3-25 lines=6 | NB_CREATE_DDL — 7 bảng control `lh_vv_ctrl.dbo` | defs: none
[1] markdown id=b7e4c1a0-6f28-4d3e-9a15-2c8d0e4f6a91 json=26-36 lines=4 | Ghi chú migration 08/10 | defs: none
[2] markdown id=d20a367e-98da-4b91-9237-dd2b2cebfeae json=37-54 lines=1 | Tạo bảng ctrl_mng_pipeline_config | defs: none
[3] code id=80154b61-ea1a-415b-834c-3c07d689d036 json=55-177 lines=108 | %%sql | defs: none
[4] markdown id=<none> json=178-188 lines=5 | Reset silver (DROP/DELETE) không nằm trong luồng tạo bảng. | defs: none
[5] code id=502cd242 json=189-242 lines=40 | %%sql | defs: none
[6] markdown id=a0c11600-5f15-4ec4-ab3b-cd590b5ce6a8 json=243-260 lines=1 | Tạo bảng ctrl_mng_watermark | defs: none
[7] markdown id=e80b9799-8de0-4319-8c62-be8096d373c8 json=261-288 lines=11 | **[SỬA 03/10] Bỏ cell MERGE watermark từ `lh_vv_bronze.partner.brz_watermark`**  | defs: none
[8] code id=3ea73e14-6a1f-42a5-b960-34123b0a3fc4 json=289-346 lines=43 | %%sql | defs: none
[9] markdown id=ed3d2dc0-d9f4-4cd7-b5aa-5e65afb7aca0 json=347-364 lines=1 | Tạo bảng ctrl_cfg_schema_registry | defs: none
[10] code id=d06c9671-6b88-4afa-97a8-d028f6b9e936 json=365-408 lines=30 | CONFIG_TABLE = "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry" | defs: none
[11] code id=28e2be98-7f9a-41d5-b7f8-b4d4a5baf5ff json=409-957 lines=535 | TABLE_CONFIGS = [ | defs: none
[12] code id=0f228dc1-7bc8-4ed2-a10f-e6125a806e83 json=958-1158 lines=186 | from pyspark.sql.types import ( | defs: resolve_type, flatten_table_configs, validate_rows, seed_registry, show_registry
[13] markdown id=7517dd85-f292-4361-9d9d-6bad3f2e4f34 json=1159-1179 lines=4 | **[THÊM 03/10 - 3P] Seed registry nguồn 3rd-party `brz_3rd_crawler_poi_stream`** | defs: none
[14] code id=e9c137c5-c9fc-4f8f-a925-bc511cfd71a7 json=1180-1377 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[15] code id=0271d481-4188-43ab-8cb4-03acd3452550 json=1378-1397 lines=5 | seed_registry(TABLE_CONFIGS_3P, "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream" | defs: none
[16] markdown id=5c2996a4-3ddc-4924-8645-c0cc545cdd63 json=1398-1415 lines=1 | Tạo các bảng log & debug | defs: none
[17] code id=7dad05d9-20f0-4ab4-af1e-dec1dfe5d8cb json=1416-1557 lines=127 | %%sql | defs: none
[18] code id=ea524452-c135-4ef4-b4a8-3a076fa67ee7 json=1558-1593 lines=22 | GOLD_LOG_COLUMNS = ( | defs: none
[19] markdown id=de14c4c2-7925-4582-b080-8b0a660fb99c json=1594-1611 lines=1 | Kiểm tra cấu hình | defs: none
[20] code id=6e95fc60-2ef9-47af-a250-95844179c188 json=1612-1697 lines=71 | %%sql | defs: none
[21] code id=5784a286-d45c-4be8-8223-5a43800b6e2b json=1698-1732 lines=17 | %%sql | defs: none
[22] markdown id=enrddlmd json=1733-1742 lines=3 | [THÊM 13/10] Gold enr và cạnh PL_VV_TRANS_SLV_TO_ENR_15P | defs: none
[23] code id=enrddlpy json=1743-1886 lines=130 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _ddl, _expected_type
[24] markdown id=nonenrmd json=1887-1899 lines=1 | [THÊM 19/10] 20261019-poi-entity-non-enrich | defs: none
[25] code id=nonenrpy json=1900-1977 lines=64 | import re | defs: category_group, with_category_group
[26] markdown id=dictseedmd json=1978-1985 lines=1 | [THÊM 20/10] 20261020-dictionary-seed-from-mapping | defs: none
[27] code id=dictseedpy json=1986-2036 lines=37 | AM_FQ = "lh_vv_silver.dbo.ref_dictionary_amenities" | defs: none
[28] markdown id=entwebmd json=2037-2044 lines=1 | [THÊM 20/10] 20261020-entity-drop-op-cols-add-website | defs: none
[29] code id=entwebpy json=2045-2160 lines=102 | CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: lock_is_free
[30] markdown id=enrinfomd json=2161-2168 lines=1 | [THÊM 21/10] 20261021-refresh-gld-enr-poi-info | defs: none
[31] code id=enrinfopy json=2169-2395 lines=213 | import uuid | defs: _schema, _create

### notebooks/NB_SETUP_POI_ENTITY.ipynb (81238 bytes)

[0] markdown id=a1setupmd json=47-58 lines=5 | NB_SETUP_POI_ENTITY | defs: none
[1] code id=a1setupparam json=59-76 lines=1 | p_apply = "false" | defs: none
[2] code id=a1setuprun json=77-91 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=a1setupseed json=92-557 lines=452 | import re | defs: validate_seed
[4] code id=a1setupplan json=558-628 lines=57 | import json | defs: none
[5] code id=a1setupddl json=629-679 lines=37 | spark.sql(""" | defs: none
[6] code id=a1setupmerge json=680-753 lines=60 | def _seed_merge(): | defs: _seed_merge
[7] code id=a1setupedges json=754-956 lines=189 | import uuid | defs: setup_edge_issues, _write_edges
[8] code id=a1setupexit json=957-981 lines=11 | import json | defs: none

### notebooks/NB_SETUP_POI_AMENITY.ipynb (57239 bytes)

[0] markdown id=c1setupmd json=47-56 lines=3 | NB_SETUP_POI_AMENITY | defs: none
[1] code id=c1setupparam json=57-66 lines=1 | p_apply = "false" | defs: none
[2] code id=c1setuprun json=67-76 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=c1setupseed json=77-345 lines=260 | import re | defs: amenity_keys, validate_seed
[4] code id=c1setupplan json=346-412 lines=58 | import json | defs: none
[5] code id=c1setupddl json=413-481 lines=60 | spark.sql(""" | defs: none
[6] code id=c1setupmerge json=482-558 lines=68 | def _seed_merge(): | defs: _seed_merge
[7] code id=c1setupedges json=559-744 lines=177 | import uuid | defs: setup_edge_issues, _write_edges
[8] code id=c1setupexit json=745-765 lines=12 | import json | defs: none

### docs/context/CTRL_TABLES_CONTEXT.md (46219 bytes)

# CTRL_TABLES_CONTEXT — 7 bảng control `lh_vv_ctrl.dbo` | L1-L572
## 1. Tổng quan | L7-L24
## 2. Quan hệ | L25-L48
## 3. `ctrl_mng_pipeline_config` | L49-L144
### DDL | L54-L73
### Cột | L74-L89
### Dữ liệu hiện có | L90-L134
### Thao tác thường gặp | L135-L144
## 4. `ctrl_mng_watermark` | L145-L237
### DDL | L155-L179
### Cột theo loại dòng | L180-L204
### Ghi chú migration — số đo watermark trước 08/10 tại `lh_vv_bronze.ctrl` (dòng 3P cũ `wm_transform_poi_raw_event`) | L205-L213
### Thao tác thường gặp | L214-L237
## 5. `ctrl_cfg_schema_registry` | L238-L327
### DDL | L243-L267
### Luật cấu hình (lib kiểm tra, sai → `ConfigError` trước khi ghi) | L268-L278
### Dữ liệu hiện có (seed `NB_CREATE_DDL`, cấu hình chốt 04/10 chiều) | L279-L327
## 6. `ctrl_log_run` — 1 dòng / lần chạy notebook (khoá `exec_id`) | L328-L398
### DDL | L332-L372
### Cột khác nghĩa giữa extract và NB_00 | L373-L387
### Ghi chú migration — log đã thấy trước 08/10 tại vị trí control cũ | L388-L398
## 7. `ctrl_log_table_run` — 1 dòng / bảng đích (hoặc node) / lần chạy | L399-L454
### DDL | L401-L454
## 8. `ctrl_cdc_state` — 1 dòng / entity / bảng đích (chỉ extract) | L455-L494
### DDL | L459-L494
## 9. `ctrl_cdc_reject` — 1 dòng / event (hoặc phần tử) lỗi (chỉ extract) | L495-L548
### DDL | L497-L548
## 10. Lịch sử thay đổi (tóm tắt) | L549-L562
## 11. Việc còn lại liên quan ctrl | L563-L572

### docs/context/01_DATA_MODEL.md (33200 bytes)

# 01 — Data Model mới của Visit Vietnam (POI) trên Microsoft Fabric | L1-L399
## 1. Bối cảnh nền tảng | L7-L18
## 2. Nguyên tắc phân tầng (đã chốt) | L19-L35
## 3. Sơ đồ tổng | L36-L75
## 4. Bronze — bảng raw | L76-L253
### Cấu trúc `normalized_payload` | L86-L253
## 5. Silver L1 — extract (đúng cấu trúc nguồn) | L254-L317
### 5.1 Partner `slv_pn_*` (23 bảng, `load_mode = CDC`) | L256-L287
### 5.2 3rd-party `slv_3p_poi_*` (10 bảng trong registry, 9 active, snapshot) | L288-L317
## 6. Silver L2 — tích hợp POI (7 node) | L318-L347
### 6.1 Bảng ref (rule dạng dữ liệu) | L334-L347
## 7. Gold — 3 bảng phục vụ (`lh_vv_gold.dbo`) | L348-L357
## 8. Định danh | L358-L370
## 9. Model cũ (vẫn chạy song song) và lý do đổi | L371-L380
## 10. Ý nghĩa của model mới | L381-L390
## 11. Hướng sắp tới (chưa làm) | L391-L399
