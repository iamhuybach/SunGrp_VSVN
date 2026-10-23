# Architect handoff: 20261023-entity-opening-hours-passthrough

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261023-entity-opening-hours-passthrough --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261023-entity-opening-hours-passthrough/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261023-entity-opening-hours-passthrough | phase=triage

## STATE

id: 20261023-entity-opening-hours-passthrough
title: Pass opening_hours_text through slv_poi_entity_non_enrich
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: data_model_change, runtime_proof_required
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: spark-runtime-reviewer, sql-data-reviewer, state-correctness-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb
- notebooks/NB_ENR_POI_INFO.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_00_ORCHES_SLV_TO_ENR_15P.ipynb
- docs/context/01_DATA_MODEL.md
- tests/test_enr_poi_contract.py
- tests/test_poi_entity_contract.py
- tests/test_initial_ddl_contract.py

## VALIDATION

PASS

## REQUEST

# Request

## User outcome

`opening_hours_text` is computed once, on `slv_poi_entity_non_enrich`. `gld_enr_poi_info.opening_hours_text` for a `poi_id` is that silver value, with the same column name, `STRING` type, and column position. One POI is not given opening hours twice.

## Scope

### In scope

- Add nullable `opening_hours_text` (`STRING`) on `lh_vv_silver.dbo.slv_poi_entity_non_enrich`.
- Move the opening-hours formula that `NB_ENR_POI_INFO` cell 3 runs today into `NB_SLV_POI_ENTITY_NON_ENRICH`.
- Pass that column through `NB_ENR_POI_INFO` with no Google/partner branch and no `_partner_hours` call when no remaining gold column uses them.
- Put the new silver column in `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL`.
- Move ctrl edges, and the `NB_00_ORCHES_SLV_TO_ENR_15P` dependency only if architecture changes it, so the entity node recomputes when the hours source changes and gold runs after the entity node.
- Move the hours-formula quality checks to the silver notebook. Gold checks that its value matches the silver column.
- Update `tests/test_enr_poi_contract.py`, `tests/test_poi_entity_contract.py`, and the initial-DDL contract test if those contracts assert columns, inputs, or edges.

### Out of scope

- A new gold column, a gold column rename, or a change to the gold `opening_hours_text` type or position.
- A new transform for sources other than the branch that cell 3 already uses.
- A new orchestration tier, pipeline JSON, or `pipelines/*/manifest.json`.
- Removing `slv_pn_business_service_i18ns` from gold while another gold column or changed-key path still reads it.
- Tasks `20261022-enr-landing-and-gld-flags` and `20261022-agent-speed-and-context-review`.
- `notebooks_lgc/` and `docs/context/3p-google/*.txt`.
- The dirty file `docs/context/gld_enr_poi_info_review.md`.

## Acceptance criteria

- `slv_poi_entity_non_enrich` has `opening_hours_text`. Google uses `slv_3p_poi_opening_hours.periods_json`. Partner uses the current `def _partner_hours` (D-17) in `NB_ENR_POI_INFO` cell 3. Any other source keeps the current behavior of that branch. Do not invent a new transform.
- `gld_enr_poi_info.opening_hours_text` equals `slv_poi_entity_non_enrich.opening_hours_text` for the same `poi_id`.
- Remove the Google/partner `when` branch and the `_partner_hours` call from the gold notebook when no remaining gold column uses them.
- Keep the gold column name, `STRING` type, and position. Add no gold column.
- The new silver column is in both `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL`. Setup edits the definition in place. Create adds only a markdown cell `[THÊM 23/10] 20261023-entity-opening-hours-passthrough` and one self-contained patch cell at the end. An `ALTER` that adds a column to an existing table must make that column nullable. No `DROP` of a table.
- The entity node reads `slv_3p_poi_opening_hours` when the Google formula needs it. `slv_pn_business_service_i18ns` is already an entity input.
- Ctrl edges, and the orchestrator when architecture changes them, recompute the entity when the hours source changes, then run gold after the entity. Do not add an orchestration tier.
- Drop the gold edge from `slv_3p_poi_opening_hours` only when no remaining gold column reads that table. Do not drop `slv_pn_business_service_i18ns` from gold while another column still uses it.
- Quality checks for the hours formula live on the silver notebook. Gold only checks that the value matches the silver column.
- The column contract comes from the current `NB_CREATE_DDL` patch cell (`cell 35`, id `enrflagpy`, `INFO_COLS`), not from cell `enrddlpy`.

## Constraints

- The current Google branch is `F.when(google, F.col("oh.periods_json")).when(source == F.lit(PARTNER), F.col("ph.partner_hours"))` with no `otherwise` (`NB_ENR_POI_INFO` cell 3). Partner hours are non-deleted `i18n` rows, `_vi_i18n` (`locale = vi`, `poi_id = uuid_md5(business_service_id, 'partner')`), then `get_json_object(amentities, '$.policies.operating_hours')`. A missing key stays null.
- `i18n` on gold is also used for changed keys (`_vi_i18n(ctx.changed("i18n"))`). Removing `_partner_hours` does not by itself remove that input.
- `02_NAMING_CONVENTION.md` §2.1 point 7 says `ensure_target` adds a new node column and a `NB_CREATE_DDL` patch is not required. This task still requires the patch named above.
- Do not mix a dirty notebook or test from another task into this diff. At triage, `git status` showed only `docs/context/gld_enr_poi_info_review.md` dirty.
- `poi_id` never includes language. Do not use `poi_uid`. Partner `poi_id` on this entity stays the formula N6 and `_partner` already use, not `partner_portal`.

## Classification rationale

- Complexity: `medium`. The formula moves from gold to silver and a column is added. The change is one column and the edges that feed it.
- Risk: `medium`. Gold must keep the same value, type, and position. Rollback is reverting the notebooks; the new silver column is nullable and no table is dropped.
- Architecture: required. Logic moves from gold to silver, and ctrl edges change so the entity recomputes before gold.
- Evidence: not required to start. The formula, the `STRING` contract, and the current null-for-other-sources branch are in the notebooks. Do not infer unseen data shapes. A gate that lacks a fact still gets the smallest probe.
- Runtime proof: required. The patch alters a live silver table and gold must show the passthrough value after a DEV run.
- Reviewer routing: `spark-runtime-reviewer` (both node notebooks), `sql-data-reviewer` (DDL, grain, and the hours expression), `state-correctness-reviewer` (recompute edges and gold-after-entity order). `fabric-pipeline-reviewer` is not routed: pipeline JSON is out of scope. Risk is not `high` or `critical`, so `risk-gate` is not required.
- Signals: `data_model_change`, `runtime_proof_required`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-OH-01 | Vị trí cột silver | `opening_hours_text` là cột build cuối của `slv_poi_entity_non_enrich`, sau `canonical_candidate` và trước `row_hash`, trong `OUT_COLS` và `TABLE_SPECS`. `ALTER` thêm cột nullable; bảng đã có nhận cột ở cuối. Khớp theo tên cột. | Lịch sử D-OH-01 | 2026-10-23 |
| D-OH-02 | Nguồn partner | Giờ partner lấy `amentities` của `slv_pn_business_service_i18ns`, không lấy `slv_pn_business_services.amentities`. Cột i18n đi vào build bằng alias riêng. | Lịch sử D-OH-02 | 2026-10-23 |
| D-OH-03 | Grain giờ Google | Registry khóa `slv_3p_poi_opening_hours` là `poi_id`. Giữ left join theo `poi_id` như `NB_ENR_POI_INFO` cell 3. Không thêm quality gate dừng khi trùng `poi_id`. | Lịch sử D-OH-03 | 2026-10-23 |
| D-OH-04 | Kiểu periods_json | Registry khai báo `periods_json` kiểu `string`. Cột silver và gold là `STRING`. Không thêm cast mới. | Lịch sử D-OH-04 | 2026-10-23 |
| D-OH-05 | Kiểm tra gold | Gold có block check `opening_hours_text_mismatch`: giá trị gold khác `slv_poi_entity_non_enrich.opening_hours_text` của cùng `poi_id`, kể cả một bên null. | Lịch sử D-OH-05 | 2026-10-23 |

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
- decision.md | 4111 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/author-input.md | 2515 bytes
- model-design.md | 11220 bytes
- request.md | 5920 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1728 bytes

## NEXT

python scripts/vv.py run-gate 20261023-entity-opening-hours-passthrough

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb (21230 bytes)

[0] markdown id=b1entitymd json=47-57 lines=4 | NB_SLV_POI_ENTITY_NON_ENRICH | defs: none
[1] code id=b1entityparam json=58-82 lines=8 | p_exec_id = "" | defs: none
[2] code id=b1entityrun json=83-97 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=b1entityjson json=98-194 lines=83 | import json | defs: _first_text, first_child_value, top_level_text
[4] code id=b1entitybuild json=195-380 lines=172 | GOOGLE = "google" | defs: _live, _google, pick, _partner, build
[5] code id=b1entityres json=381-395 lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=b1entityexit json=396-410 lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### notebooks/NB_ENR_POI_INFO.ipynb (22248 bytes)

[0] markdown id=8cef70ac json=47-54 lines=1 | APPEND lh_vv_gold.enr.gld_enr_poi_info từ lh_vv_silver.dbo.slv_poi_entity_non_en | defs: none
[1] code id=6afb4f0e json=55-79 lines=8 | p_exec_id = "" | defs: none
[2] code id=32337f4f json=80-94 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=36415d3b json=95-382 lines=274 | SECTOR_LABELS = { | defs: _keys, _flag_keys, _present, _label, _time_to_spend_text, _best_time_text, _cost, _cost_vnd, _review_json, _service_flag, _vi_i18n, _partner_hours, _i18n_keys, _role_keys, _require, build
[4] code id=71915be4 json=383-397 lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[5] code id=33e2a64a json=398-412 lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (208587 bytes)

[0] markdown id=init_md json=47-54 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=55-72 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=73-87 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=88-470 lines=369 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=471-485 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=486-683 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=684-698 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=699-780 lines=68 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[8] code id=init_seed_place_type json=781-1249 lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=1250-1525 lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=1526-1683 lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=1684-1698 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=1699-1892 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=1893-1907 lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=1908-1922 lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (188396 bytes)

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
[32] markdown id=mvpoimd json=2396-2403 lines=1 | [THÊM 21/10] 20261021-move-poi-nodes-enr-15p-cleanup | defs: none
[33] code id=mvpoipy json=2404-2637 lines=220 | import uuid | defs: _names, _n, _node_edges, _info_edges
[34] markdown id=enrflagmd json=2638-2645 lines=1 | [THÊM 22/10] 20261022-enr-landing-and-gld-flags | defs: none
[35] code id=enrflagpy json=2646-2912 lines=253 | import uuid | defs: _want, _schema, _create_sql, _missing_flags, _add_flags, _edge_rows

### docs/context/01_DATA_MODEL.md (34115 bytes)

# 01 — Data Model mới của Visit Vietnam (POI) trên Microsoft Fabric | L1-L402
## 1. Bối cảnh nền tảng | L7-L18
## 2. Nguyên tắc phân tầng (đã chốt) | L19-L35
## 3. Sơ đồ tổng | L36-L75
## 4. Bronze — bảng raw | L76-L253
### Cấu trúc `normalized_payload` | L86-L253
## 5. Silver L1 — extract (đúng cấu trúc nguồn) | L254-L316
### 5.1 Partner `slv_pn_*` (23 bảng, `load_mode = CDC`) | L256-L287
### 5.2 3rd-party `slv_3p_poi_*` (9 bảng trong registry, 9 active, snapshot) | L288-L316
## 6. Silver L2 — tích hợp POI (7 node) | L317-L346
### 6.1 Bảng ref (rule dạng dữ liệu) | L333-L346
## 7. Gold hiện hành (`lh_vv_gold.enr`) | L347-L357
## 8. Định danh | L358-L370
## 9. Model cũ (vẫn chạy song song) và lý do đổi | L371-L380
## 10. Ý nghĩa của model mới | L381-L390
## 11. Hướng sắp tới (chưa làm) | L391-L402
