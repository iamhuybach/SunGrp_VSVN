# Architect handoff: 20261024-gld-srv-poi-from-mapping

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261024-gld-srv-poi-from-mapping --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261024-gld-srv-poi-from-mapping/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261024-gld-srv-poi-from-mapping | phase=triage

## STATE

id: 20261024-gld-srv-poi-from-mapping
title: Gold serving POI multi-lang and info from mapping
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: transaction_boundaries, idempotency, design_tradeoffs, runtime_proof_required, data_evidence_required, data_model_change
gates: evidence=evidence_required, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb
- notebooks/NB_GLD_SRV_POI_INFO.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- tests/test_initial_ddl_contract.py
- .ai/tasks/20261024-gld-srv-poi-from-mapping/evidence/probes/partner_hours_shape.py
- docs/context/mapping_gld_srv_poi_multi_lang.md
- docs/context/mapping_gld_srv_poi_info.md
- .ai/tasks/20261024-gld-srv-poi-from-mapping/evidence/probes/gld_srv_input_shape.py

## VALIDATION

PASS

## RESUME

Status: user_decision
Done this session: Recorded D-SRV-24 (write path A) and D-SRV-25 (Google null hours become null). Mapping §1.3 rule 8 added. multi_period_day is explained and still open. Did not re-run model.
Next action: After the user names the multi-period rule, update decision.md and mapping §1.3. Then run-author --kind model and run-gate. Do not implement before architecture PASS.
Read next: docs/context/mapping_gld_srv_poi_info.md §1.3; .ai/tasks/20261024-gld-srv-poi-from-mapping/decision.md (D-SRV-24, D-SRV-25, Còn mở)
Waiting on: rule for Google rows whose opening_hours_text repeats a day_of_week

## REQUEST

# Request

## User outcome

One task creates two gold serving tables from the two mapping files: `lh_vv_gold.dbo.gld_srv_poi_multi_lang` and `lh_vv_gold.dbo.gld_srv_poi_info`. Gold reads enriched POI attributes and the enriched address, then transforms opening hours. Those two tables are the external product. Silver does not recompute them.

## Scope

### In scope

- `gld_srv_poi_multi_lang` per `docs/context/mapping_gld_srv_poi_multi_lang.md` §1.1 and §1.2.
- `gld_srv_poi_info` per `docs/context/mapping_gld_srv_poi_info.md` §1.1, §1.2, §1.3, and each case in §1.4.
- Lakehouse.schema `lh_vv_gold.dbo`. Neither table goes in schema `enr`.
- Columns and transforms only from those two mapping files. `is_verified` and `is_bookable` are null. `created_at` and `updated_at` are system timestamps.
- Where `docs/context/01_DATA_MODEL.md` §7 disagrees on columns or sources, the two mapping files win. Do not create `gld_srv_poi_registry` or `gld_srv_poi_destination_membership`.
- New node notebooks `NB_GLD_SRV_POI_MULTI_LANG` and `NB_GLD_SRV_POI_INFO`. One notebook, one target table. No extra orchestration tier.
- DDL in both `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL`. Setup edits the definition in place. Create appends one markdown `[THÊM dd/mm] <task-id>` and one self-contained patch cell at the end. No `DROP` of either table.
- `operating_hours` is STRING and follows §1.3, matching the JSON of each §1.4 case.
- If a named source lacks a mapping column, do not add that silver column and do not drop the gold column.
- Update `tests/test_initial_ddl_contract.py` because §2.1 requires the initial-DDL contract test to track a new `TABLE_SPECS` entry.

### Out of scope

- Attaching either table to `PL_VV_TRANS_SLV_TO_ENR_15P`. The mapping does not say to.
- A new orchestration tier.
- Adding silver columns or dropping gold columns to paper over a mapping gap.
- Rewriting the multi-lang join from `poi_id` to `business_service_id` unless the user says so.
- `notebooks_lgc/`, `docs/context/3p-google/*.txt`, pipeline manifests, and other tasks' artifacts.

## Acceptance criteria

- The two notebooks exist under the target-table names above, one target each.
- Both DDL notebooks contain the two gold tables. Setup changes the in-place definition. Create only appends the dated markdown and one idempotent patch cell. Neither notebook drops a table.
- `operating_hours` matches §1.3 and the JSON of each §1.4 case, type STRING.
- A source column missing from the repo spec is not invented on silver, and the mapped gold column is not removed.

## Constraints

- Domain: lib transform/gold and DDL/registry.
- Signal: `data_model_change`.
- D-SRV-10 through D-SRV-22 are recorded. Info grain is `poi_id`. Duplicate destination rows keep the greater `updated_at`. `pl_name` is `PL_VV_TRANS_SLV_TO_GLD_30P`. Equal or null `updated_at` is unspecified.
- Do not invent data properties. A missing runtime shape becomes the smallest probe and a stop.

## Classification rationale

- Complexity: medium. New gold grain and keys, a contradictory hours transform, and DDL in two notebooks. Bounded to two new tables.
- Risk: medium. New serving tables only. No drop of existing tables. Rollback is a runbook concern, not an in-place overwrite of silver.
- Architecture: required. Grain, key, gold commit, and several file-backed implementation forks change. `data_model_change` requires `model-design.md` before the Architect.
- Evidence: required. D-SRV-18 asks for a partner hours rule. The repo only has the path `$.policies.operating_hours`. The JSON shape is not in the named files.
- Runtime proof: required. The notebooks and DDL must be run in Fabric DEV. Local checks can cover the §1.4 JSON cases after the hours choices are fixed.
- Reviewer routing: `sql-data-reviewer` (DDL, joins, types, grain, and the write match once Q10 chooses MERGE or APPEND), `spark-runtime-reviewer` (Fabric notebooks and Delta writes), `state-correctness-reviewer` (commit and rerun). No `fabric-pipeline-reviewer`: no pipeline attachment. Risk is medium, so no risk gate.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-SRV-01 | Phạm vi | Một task. Tạo và ghi hai bảng gold serving theo đúng hai file mapping. Không tách mỗi bảng một task. | Yêu cầu người dùng | 2026-10-24 |
| D-SRV-02 | Schema | Lakehouse.schema là `lh_vv_gold.dbo`. Không đặt hai bảng này vào schema `enr`. | Yêu cầu người dùng | 2026-10-24 |
| D-SRV-03 | Cột | Cột và phép biến đổi chỉ lấy từ hai file mapping. `is_verified` và `is_bookable` là null. `created_at` và `updated_at` là timestamp hệ thống. | Yêu cầu người dùng; mapping info §1.2 | 2026-10-24 |
| D-SRV-04 | Model cũ | `docs/context/01_DATA_MODEL.md` §7 đang mô tả `gld_srv_poi_multi_lang` kiểu cũ. Hai file mapping thắng §7 khi lệch cột hoặc nguồn. Không tạo `gld_srv_poi_registry` hay `gld_srv_poi_destination_membership`. | Yêu cầu người dùng | 2026-10-24 |
| D-SRV-05 | Notebook | Notebook mới theo tên bảng: `NB_GLD_SRV_POI_MULTI_LANG` và `NB_GLD_SRV_POI_INFO`. Một notebook một bảng đích. Không thêm tầng điều phối. Không gắn hai bảng vào `PL_VV_TRANS_SLV_TO_ENR_15P` khi mapping không nói vậy. | Yêu cầu người dùng; `02_NAMING_CONVENTION.md` §2 | 2026-10-24 |
| D-SRV-06 | DDL | DDL ở cả `NB_SETUP_INITIAL_DDL` và `NB_CREATE_DDL`. Setup sửa định nghĩa tại chỗ. Create chỉ thêm markdown `[THÊM dd/mm] <task-id>` và một cell patch tự chứa ở cuối. Không `DROP` bảng. §2.1 mục 7 nói bảng gold qua `ensure_target` không có DDL ở hai notebook; yêu cầu này vẫn bắt có DDL. | Yêu cầu người dùng; `02_NAMING_CONVENTION.md` §2.1 | 2026-10-24 |
| D-SRV-07 | Giờ mở cửa | `operating_hours` làm đúng mục 1.3 và ra đúng JSON của từng case ở 1.4. Kiểu STRING. | Yêu cầu người dùng; mapping info §1.3, §1.4 | 2026-10-24 |
| D-SRV-08 | Cột thiếu | Nguồn thiếu cột so với mapping thì không tự thêm cột silver và không bỏ cột gold. | Yêu cầu người dùng | 2026-10-24 |
| D-SRV-09 | Tầng | Gold serving đọc thuộc tính POI đã enrich và địa chỉ enrich, rồi mới biến đổi giờ mở cửa. Hai bảng kia là sản phẩm đưa ra ngoài, không tính lại ở silver. | Yêu cầu người dùng | 2026-10-24 |
| D-SRV-10 | source_name | lấy source_name từ slv_poi_entity_non_enrich theo poi_id | Câu trả lời Q1 | 2026-10-24 |
| D-SRV-11 | Cột destination | thêm các cột này destination_id, country_code, postal_code, lat, lng vào slv_enr_poi_destination | Câu trả lời Q2 | 2026-10-24 |
| D-SRV-12 | poi_id i18n | poi_id của slv_pn_business_service_i18ns cũng tính giống như cách đang xử lý poi_id của slv_pn_business_service_i18ns ở slv_poi_entity_non_enrich. | Câu trả lời Q3 | 2026-10-24 |
| D-SRV-13 | description | Partner thì description lấy bio. Khi bio null, lấy description của slv_enr_poi_info_multi_lang | Câu trả lời Q4 | 2026-10-24 |
| D-SRV-14 | is_recommended | is_recommended là true khi source_name = partner. Nguồn khác là false | Câu trả lời Q5 | 2026-10-24 |
| D-SRV-15 | Nhãn ngày | Tôi đã nhầm. Nguồn 0 là chủ nhật, 1-6 là thứ 2 đến thứ 7. Label đi theo 2 cách là giống nhau. | Câu trả lời Q6 | 2026-10-24 |
| D-SRV-16 | is_closed | Ngược lại là false. | Câu trả lời Q7 | 2026-10-24 |
| D-SRV-17 | close_time | Sửa lại sample, sample của tôi nhầm. Chỉnh lại ý 5: close_time = close_hour và close_minute (sample: nếu "close_time": 7 và "close_minute": 0 -> 07:00). Mapping ghi sample bằng `close_hour` vì cùng câu nói `close_hour` và case 1 dùng `close_hour`. | Câu trả lời 2026-10-24; mapping info §1.3 ý 5 | 2026-10-24 |
| D-SRV-18 | Giờ partner | Rule Google là mục 1.3. Partner theo mục 1.5: object bảy thứ, giờ lấy từ một phần tử `hours`, chuỗi `open_time`/`close_time` giữ nguyên. Không đọc `status`. Nhiều phần tử trong một ngày thì dừng. | Probe partner_hours_shape; mapping info §1.5 | 2026-10-24 |
| D-SRV-19 | Grain multi_lang | Merge theo grain multi_lang (poi_id, lang). | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-20 | Grain info | gld_srv_poi_info có grain là poi_id | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-21 | Destination trùng | destination trùng poi_id ưu tiên bản ghi đến sau (updated_at lớn hơn) | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-22 | pl_name | PL_VV_TRANS_SLV_TO_GLD_30P | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-23 | Khung trước data | 2 bảng slv_enr_poi_destination, slv_enr_poi_info_multi_lang hiện tại chưa có data, tôi đang dựng trước khung, khi nào có tôi sẽ làm task mới để review và test lại sau | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-24 | Write path | Chọn A. MERGE qua `run_node`: cột mapping cộng `row_hash`, `created_at`, `updated_at`, `deleted_at`. Không thêm `is_active`. Dòng không còn trong build thì gán `deleted_at`. Khoá MERGE NOT NULL. | Câu trả lời 2026-10-24; `TECH_COLUMNS` lib | 2026-10-24 |
| D-SRV-25 | Google null | Google opening_hours_text null -> Để operating_hours null | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-26 | Nhiều period | Nếu có nhiều phần tử trở lên cùng một số day_of_week, vẫn xử lý đầy đủ, không gom. Mỗi phần tử thành một object đích, cùng day_of_week và label. | Câu trả lời 2026-10-24; mapping info §1.3 ý 9 | 2026-10-24 |
| D-SRV-27 | Khoá null | `poi_id` hoặc `lang` null thì dừng lần chạy. Không bỏ dòng và không ghi khoá null. | Hệ quả D-SRV-24 | 2026-10-24 |
| D-SRV-28 | Không có entity | Dòng `slv_enr_poi_info_multi_lang` không có entity thì giữ. `source_name` null. `description` lấy bảng enr. | Mapping multi_lang §1.1 | 2026-10-24 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

### Còn mở

- D-SRV-21 không nói `updated_at` bằng nhau hoặc null. Không tự thêm khoá sắp xếp thứ hai.
- Repo không có pipeline tên `PL_VV_TRANS_SLV_TO_GLD_30P`. Giữ đúng tên này. Không gắn `PL_VV_TRANS_SLV_TO_ENR_15P`.
- `NB_SLV_POI_ENTITY_NON_ENRICH` cell 4 có `pk=("poi_id",)`. Registry `slv_pn_business_service_i18ns` có khoá `business_service_id`, `locale`.
- D-SRV-11 chỉ thêm cột. Không có notebook ghi `destination_id`, `country_code`, `postal_code`, `lat`, `lng`. Gold lấy 1-1, nên null khi landing null.
- Mapping không lọc `deleted_at`. Không thêm lọc đó.
- Probe `gld_srv_input_shape`: entity 24 partner và 41 google, không `deleted`, không trùng `poi_id`. Google có 1 null, 8 `multi_period_day`, 3 `all_day_exact`, 2 `close_day_differs`. Partner có 13 null, 10 một phần tử `hours`, 1 thiếu `hours`, không có mảng dài hơn 1. `slv_enr_poi_destination` và `slv_enr_poi_info_multi_lang` 0 dòng theo D-SRV-23.
- `updated_at` bằng nhau hoặc null: không có khoá sắp xếp thứ hai, lần chạy dừng. Không chọn dòng.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 43622 bytes

## FILES

- architecture.md | 43622 bytes | large: use toc/show
- decision.md | 9520 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/gld_srv_input_shape.py | 5661 bytes
- evidence/probes/partner_hours_shape.py | 2321 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/gld_srv_input_shape.txt | 854 bytes
- evidence/results/partner_hours_shape.txt | 1178 bytes
- handoffs/architect.md | 23151 bytes | large: use toc/show
- handoffs/author-input.md | 2483 bytes
- model-design.md | 13584 bytes
- request.md | 4136 bytes
- resume.md | 629 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1913 bytes

## NEXT

python scripts/vv.py run-gate 20261024-gld-srv-poi-from-mapping

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (209044 bytes)

[0] markdown id=init_md json=47-54 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=55-72 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=73-87 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=88-474 lines=373 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=475-489 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=490-687 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=688-702 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=703-786 lines=70 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[8] code id=init_seed_place_type json=787-1255 lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=1256-1531 lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=1532-1689 lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=1690-1704 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=1705-1898 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=1899-1913 lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=1914-1928 lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (205034 bytes)

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
[38] markdown id=peholmd json=3125-3132 lines=1 | [THÊM 23/10] 20261023-entity-phone-email-holiday | defs: none
[39] code id=peholpy json=3133-3196 lines=50 | ENTITY_FQ = "lh_vv_silver.dbo.slv_poi_entity_non_enrich" | defs: _fields, _issues
