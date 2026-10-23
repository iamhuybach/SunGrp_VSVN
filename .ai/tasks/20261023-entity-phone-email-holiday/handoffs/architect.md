# Architect handoff: 20261023-entity-phone-email-holiday

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261023-entity-phone-email-holiday --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261023-entity-phone-email-holiday/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261023-entity-phone-email-holiday | phase=triage

## STATE

id: 20261023-entity-phone-email-holiday
title: Add phone, email, and holiday_exceptions to slv_poi_entity_non_enrich
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: data_model_change, runtime_proof_required
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: spark-runtime-reviewer, sql-data-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- tests/test_poi_entity_contract.py
- tests/test_initial_ddl_contract.py
- docs/context/01_DATA_MODEL.md

## VALIDATION

PASS

## REQUEST

# Request

## User outcome

`slv_poi_entity_non_enrich` stores `phone`, `email`, and `holiday_exceptions` for each POI. Google and partner each have one rule. Gold does not recompute these attributes.

## Scope

### In scope

- Add `phone`, `email`, and `holiday_exceptions` to `slv_poi_entity_non_enrich` in `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_SETUP_INITIAL_DDL`, and `NB_CREATE_DDL`.
- Keep the uncommitted `20261023-entity-opening-hours-passthrough` diff. This task edits that working tree and does not revert the hours change.
- When runtime is reached, one new runbook covers both the not-yet-applied `ohpasspy` cell and the three-column patch.

### Out of scope

- Gold columns, gold formulas, and `NB_ENR_POI_INFO`.
- The `opening_hours_text` formula, the hours ctrl edges, and cell `ohpasspy`.
- Extract-column additions, a new orchestration tier, and `DROP` of an existing table.
- Running the hours-task runbook or `run-gate` on `20261023-entity-opening-hours-passthrough`.
- A new ctrl edge unless architecture names a source that is not already an entity input.

## Acceptance criteria

- `phone`, `email`, and `holiday_exceptions` are `STRING`, nullable, in that order, after `opening_hours_text` and before `row_hash`.
- Google: `phone` is `slv_3p_poi_contact.phone` for the same `poi_id`, on the join frame that already supplies `website_url`. `email` is null. `holiday_exceptions` is null.
- Partner: `phone` is `slv_pn_business_services.phone`. `email` is `slv_pn_business_services.email`. `holiday_exceptions` is `get_json_object(amentities, '$.policies.holiday_exceptions')` on the i18n `vi` row, the same row and the same access as `operating_hours` at `$.policies.operating_hours`. Keep the JSON string. Do not parse it further.
- Any other source leaves all three columns null, using the same branch style as hours.
- The contact duplicate-`poi_id` quality gate stays as it is.
- `NB_SETUP_INITIAL_DDL` updates the `slv_poi_entity_non_enrich` spec in place. `NB_CREATE_DDL` appends one markdown cell `[THÊM 23/10] 20261023-entity-phone-email-holiday` and one self-contained patch cell after `ohpasspy`. The patch only `ALTER`s in missing nullable columns. It does not edit `ohpasspy` and does not `DROP` the table.
- `slv_3p_poi_contact`, `slv_pn_business_services`, and `slv_pn_business_service_i18ns` stay the inputs they already are.

## Constraints

- Domain: lib transform/gold and DDL/registry. Signal: `data_model_change`.
- Registry already declares the source columns as string. `NB_SETUP_INITIAL_DDL` cell 4 `slv_pn_business_services` has `phone` (`path` `phone`) and `email` (`path` `email`). Cell 5 `slv_3p_poi_contact` has `phone` = `_str("nationalPhoneNumber")` and no `email`. `NB_CREATE_DDL` cells 11 and 14 carry the same mappings. Extract notebooks project `spec.columns` from `ctrl_cfg_schema_registry` through `load_table_specs`. Do not add extract columns and do not invent a type.
- `holiday_exceptions` is not its own registry column. It is a JSON path on `amentities`, which the entity notebook already reads for hours.
- Setup and create DDL follow `docs/context/02_NAMING_CONVENTION.md` §2.1.
- The hours task records the runtime pause in its own `decision.md` and stays `waiting_runtime`.

## Classification rationale

- Complexity: medium. The change adds three columns to a silver node and both DDL notebooks. It does not add a new orchestration tier.
- Risk: medium. The entity output gains values, rollback is a nullable add, and the hours patch is still unapplied on DEV.
- Architecture: required. The silver table's committed column set changes, and those attributes are owned by `slv_poi_entity_non_enrich`, not by gold.
- Evidence: not required. The source `phone` and `email` columns and their string types are in both registry seeds. Extract follows that registry. `holiday_exceptions` reuses `amentities`.
- Runtime proof: required. DEV must apply `ohpasspy` and the new nullable `ALTER`, then the entity recompute.
- Reviewer routing: `spark-runtime-reviewer` for the entity notebook; `sql-data-reviewer` for the DDL patch and the column expressions. No pipeline reviewer. No state-correctness reviewer unless architecture adds a ctrl or lock change.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-PEH-01 | Cột silver | `phone`, `email`, `holiday_exceptions` là STRING, nullable, trên `slv_poi_entity_non_enrich`, đúng thứ tự đó, sau `opening_hours_text` và trước `row_hash`. Không thêm cột gold. | Lịch sử D-PEH-01 | 2026-10-23 |
| D-PEH-02 | Nguồn Google | Google: `phone` = `slv_3p_poi_contact.phone` của cùng `poi_id`, cùng khung join đang lấy `website_url`. `email` = null. `holiday_exceptions` = null. | Lịch sử D-PEH-02 | 2026-10-23 |
| D-PEH-03 | Nguồn partner | Partner: `phone` = `slv_pn_business_services.phone`. `email` = `slv_pn_business_services.email`. `holiday_exceptions` = `get_json_object(amentities, '$.policies.holiday_exceptions')` trên bản i18n `vi`, cùng dòng và cùng cách đang lấy `operating_hours` tại `$.policies.operating_hours`. Giữ nguyên chuỗi JSON, không parse thêm. | Lịch sử D-PEH-03 | 2026-10-23 |
| D-PEH-04 | Phần giờ giữ nguyên | Không đổi công thức `opening_hours_text`, không đổi cạnh giờ, không sửa cell `ohpasspy`. | Lịch sử D-PEH-04 | 2026-10-23 |
| D-PEH-05 | Nguồn khác và QG contact | Quality gate trùng `poi_id` của contact giữ nguyên. Nguồn khác `google` và `partner` để ba cột null, cùng kiểu nhánh giờ. | Lịch sử D-PEH-05 | 2026-10-23 |
| D-PEH-06 | Registry đã đủ | Registry đã có `slv_3p_poi_contact.phone`, `slv_pn_business_services.phone` và `slv_pn_business_services.email`, kiểu string. Notebook extract lấy cột từ registry. Không thêm cột extract và không cần probe. Ba bảng nguồn đã là input của entity. | Lịch sử D-PEH-06 | 2026-10-23 |

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
- decision.md | 4926 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/author-input.md | 2631 bytes
- model-design.md | 9411 bytes
- request.md | 4262 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1574 bytes

## NEXT

python scripts/vv.py run-gate 20261023-entity-phone-email-holiday

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb (23156 bytes)

[0] markdown id=b1entitymd json=47-58 lines=5 | NB_SLV_POI_ENTITY_NON_ENRICH | defs: none
[1] code id=b1entityparam json=59-83 lines=8 | p_exec_id = "" | defs: none
[2] code id=b1entityrun json=84-98 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=b1entityjson json=99-195 lines=83 | import json | defs: _first_text, first_child_value, top_level_text
[4] code id=b1entitybuild json=196-399 lines=190 | GOOGLE = "google" | defs: _live, _google, pick, _partner, build
[5] code id=b1entityres json=400-414 lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=b1entityexit json=415-429 lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (208896 bytes)

[0] markdown id=init_md json=47-54 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=55-72 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=73-87 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=88-471 lines=370 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=472-486 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=487-684 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=685-699 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=700-783 lines=70 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[8] code id=init_seed_place_type json=784-1252 lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=1253-1528 lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=1529-1686 lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=1687-1701 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=1702-1895 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=1896-1910 lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=1911-1925 lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (201246 bytes)

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
[36] markdown id=ohpassmd json=2913-2920 lines=1 | [THÊM 23/10] 20261023-entity-opening-hours-passthrough | defs: none
[37] code id=ohpasspy json=2921-3124 lines=190 | import uuid | defs: _rows, _active, _refresh_lock, _column

### docs/context/01_DATA_MODEL.md (34378 bytes)

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
