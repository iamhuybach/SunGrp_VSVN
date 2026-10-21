# Architect handoff: 20261021-refresh-gld-enr-poi-info

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261021-refresh-gld-enr-poi-info --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261021-refresh-gld-enr-poi-info/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261021-refresh-gld-enr-poi-info | phase=triage

## STATE

id: 20261021-refresh-gld-enr-poi-info
title: Refresh gld_enr_poi_info from slv_poi_entity_non_enrich
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: data_model_change, cross_system, cross_state_impact, idempotency, design_tradeoffs, runtime_proof_required
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_ENR_POI_INFO.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- tests/test_enr_poi_contract.py
- tests/test_initial_ddl_contract.py

## VALIDATION

PASS

## RESUME

# Resume

## Status

waiting_architecture, round 2. D-17 join is uuid_md5(business_service_id, 'partner') = poi_id and locale = vi. D-18 drops gld_enr_poi_info on DEV and recreates it like init. Coordinate is not dropped. Round 1 CREATE OR REPLACE is superseded. Source not edited.

## Done this session

Recorded D-17 and D-18. Set gates.architecture back to pending. Moved to waiting_architecture.

## Next action

`python scripts/vv.py run-gate 20261021-refresh-gld-enr-poi-info` is the current or next command. Do not edit source while it runs. On PASS, implement the new Edit list. On another USER_DECISION, stop.

## Read next

- .ai/tasks/20261021-refresh-gld-enr-poi-info/decision.md — D-17, D-18
- .ai/tasks/20261021-refresh-gld-enr-poi-info/architecture.md — Main brief after the gate

## Waiting on

Claude Architect, round 2.

## REQUEST

# Request

## User outcome

3 phần xử lý của 3 bảng sau đã out of date:
- gld_enr_poi_coordinate
- gld_enr_poi_info
- gld_enr_poi_review
Hãy cập nhật lại theo logic mới:
Với gld_enr_poi_coordinate: Bỏ
Với gld_enr_poi_review: Giữ nguyên
Với gld_enr_poi_info:
- Lấy toàn bộ các cột (trừ các cột op như row_hash, created_at, updated_at, deleted_at) của bảng slv_poi_entity_non_enrich thay cho slv_pn_poi.
- Bỏ các fields: subcategory_tags, short_address, best_time_from_month, best_time_to_month, best_time_type.
- district = slv_poi_entity_non_enrich.ward, destination_name = slv_poi_entity_non_enrich.city
- rating, userRatingCount (đổi thành user_rating_count), priceLevel (đổi thành price_level), opening_hours_text, review_json với slv_poi_entity_non_enrich.source_name = 'google' xử lý như cũ.
- left join slv_poi_amenity on slv_poi_entity_non_enrich.poi_id = slv_poi_amenity.poi_id để lấy slv_poi_amenity.service_flags
- lấy thêm 2 cột price_min và price_max khi join với slv_3p_poi_price -> tính cost theo mục 1.9.3 trong docs/context/3p-google/mapping_place_type.md
- time_to_spend, best_time, cost_vnd transform theo D:\git\SunGrp_VSVN\docs\context\3p-google\mapping_gld_enr_poi_info.md
- Các phần xử lý còn lại vẫn giữ nguyên.

## Cách hiểu đã chốt

- Schema gold là lh_vv_gold.enr. Nguồn info là lh_vv_silver.dbo.slv_poi_entity_non_enrich. Bỏ slv_pn_poi khỏi nguồn của ba bảng này.
- gld_enr_poi_coordinate: bỏ khỏi xử lý. Tắt cạnh ctrl tới bảng này. Notebook NB_ENR_POI_COORDINATE không còn được pipeline gọi. Không DROP bảng vì request không cho phép xóa bảng.
- gld_enr_poi_review: giữ nguyên logic NB_ENR_POI_REVIEW và hợp đồng cột.
- Cột op không đưa sang gold: row_hash, created_at, updated_at, deleted_at. Cột nghiệp vụ của entity, gồm website_url và các cột estimate, vẫn lấy.
- Bỏ khỏi gld_enr_poi_info: subcategory_tags, short_address, best_time_from_month, best_time_to_month, best_time_type. canonical_candidate chỉ đi vào best_time theo mục 1.2 của mapping_gld_enr_poi_info.md. Không tạo lại cột best_time_type.
- district lấy ward, destination_name lấy city của entity.
- Năm cột rating, user_rating_count, price_level, opening_hours_text, review_json chỉ áp rule google hiện có khi source_name = google. Đổi tên userRatingCount thành user_rating_count và priceLevel thành price_level.
- cost chỉ tính khi có đủ price_min và price_max, theo mục 1.9.3: ROUND((price_min + price_max) / 2), cost_method = observed_average, cost_confidence = high. Không gọi LLM. Thiếu một trong hai giá thì ghi USER_DECISION.
- time_to_spend, best_time, cost_vnd làm theo mục 1.1, 1.2, 1.3 và mục 2 của mapping_gld_enr_poi_info.md. cost null thì JSON null, không phải object có value null.
- Mục 1.3 mới chỉ có tiêu đề "round về 1,000 VND", chưa có công thức. Ghi USER_DECISION, không tự đặt cách làm tròn.
- Join amenity và join price không được nhân dòng gold. slv_poi_amenity có nhiều dòng cho một poi_id. Chưa có quy tắc gộp service_flags. Ghi USER_DECISION, không chọn mảng, concat hay một dòng.

## Scope

### In scope

- `notebooks/NB_ENR_POI_INFO.ipynb`: đổi nguồn và hợp đồng cột theo các quyết định đã chốt.
- Cạnh `ctrl_mng_pipeline_config` của `PL_VV_TRANS_SLV_TO_ENR_15P` trong `notebooks/NB_SETUP_INITIAL_DDL.ipynb` và một cell patch mới của `notebooks/NB_CREATE_DDL.ipynb`.
- Hợp đồng cột `lh_vv_gold.enr.gld_enr_poi_info` ở cả hai notebook DDL.
- `tests/test_enr_poi_contract.py` và phần gold enr của `tests/test_initial_ddl_contract.py` khi hợp đồng hoặc cạnh đổi.

### Out of scope

- Sửa logic hoặc hợp đồng cột `NB_ENR_POI_REVIEW`.
- DROP bảng `gld_enr_poi_coordinate` hoặc sửa logic `NB_ENR_POI_COORDINATE`.
- Sửa JSON `pipelines/PL_VV_TRANS_SLV_TO_ENR_15P` khi tắt cạnh ctrl đã đủ để orchestrator không gọi notebook coordinate.
- Gọi LLM để sinh cost.
- Tự đặt công thức làm tròn mục 1.3 hoặc quy tắc gộp `service_flags`.

## Acceptance criteria

- `gld_enr_poi_info` đọc `lh_vv_silver.dbo.slv_poi_entity_non_enrich` và không còn đọc `slv_pn_poi`.
- Ba cạnh ctrl tới `gld_enr_poi_coordinate` có `is_active = 0`. Bảng coordinate còn trong DDL. Pipeline không gọi `NB_ENR_POI_COORDINATE`.
- `gld_enr_poi_review` giữ nguyên logic và danh sách cột.
- Các USER_DECISION trong `decision.md` được người dùng chốt trước khi viết architecture.

## Constraints

- Không DROP bảng.
- Không nhân dòng gold khi join amenity hoặc price.
- Không bịa công thức làm tròn, quy tắc gộp `service_flags`, hoặc cách ghi cost khi thiếu `price_min` hoặc `price_max`.
- DDL: sửa định nghĩa tại chỗ trong `NB_SETUP_INITIAL_DDL`; `NB_CREATE_DDL` chỉ thêm cell patch mới. Cell `enrddlpy` giữ nguyên.

## Classification rationale

- Complexity: high. Đổi grain nguồn của gold info, đổi hợp đồng cột, tắt cạnh ctrl và giữ idempotency của seed. Signals: `data_model_change`, `cross_system`, `cross_state_impact`, `idempotency`, `design_tradeoffs`, `runtime_proof_required`.
- Risk: high. Đổi nguồn gold và tắt cạnh làm orchestrator bỏ một node trong khi bảng cũ vẫn còn; chạy lại trên DEV mới chứng minh được cạnh đã tắt.
- Architecture: required. Đổi nguồn gold, tắt cạnh coordinate, đổi hợp đồng cột info. Không fast lane.
- Evidence: not required ở triage. Grain `slv_poi_amenity` đã có trong `docs/context/01_DATA_MODEL.md` §6. `slv_3p_poi_price` là DOC khóa `poi_id`. Ba điểm chặn là quyết định nghiệp vụ, không phải probe.
- Runtime proof: required. Sau review, runbook chạy lại `gld_enr_poi_info` trên Fabric DEV và kiểm tra cạnh coordinate đã tắt. `p_apply` mặc định false.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, rồi `risk-gate`. Không thêm `fabric-pipeline-reviewer`: pipeline JSON chỉ gọi orchestrator `NB_00_ORCHES_SLV_TO_ENR_15P`; việc tắt node nằm ở cạnh ctrl.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Nguồn info | Schema gold là lh_vv_gold.enr. Nguồn info là lh_vv_silver.dbo.slv_poi_entity_non_enrich. Bỏ slv_pn_poi khỏi nguồn của ba bảng này. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-02 | Coordinate | gld_enr_poi_coordinate: bỏ khỏi xử lý. Tắt cạnh ctrl tới bảng này. Notebook NB_ENR_POI_COORDINATE không còn được pipeline gọi. Không DROP bảng vì request không cho phép xóa bảng. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-03 | Review | gld_enr_poi_review: giữ nguyên logic NB_ENR_POI_REVIEW và hợp đồng cột. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-04 | Cột entity | Cột op không đưa sang gold: row_hash, created_at, updated_at, deleted_at. Cột nghiệp vụ của entity, gồm website_url và các cột estimate, vẫn lấy. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-05 | Cột bỏ | Bỏ khỏi gld_enr_poi_info: subcategory_tags, short_address, best_time_from_month, best_time_to_month, best_time_type. canonical_candidate chỉ đi vào best_time theo mục 1.2 của mapping_gld_enr_poi_info.md. Không tạo lại cột best_time_type. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-06 | Địa danh | district lấy ward, destination_name lấy city của entity. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-07 | Cột google | Năm cột rating, user_rating_count, price_level, opening_hours_text, review_json chỉ áp rule google hiện có khi source_name = google. Đổi tên userRatingCount thành user_rating_count và priceLevel thành price_level. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-08 | Cost đủ giá | cost chỉ tính khi có đủ price_min và price_max: ROUND((price_min + price_max) / 2). Không gọi LLM. cost_method và cost_confidence không phải cột gold: trong mapping gld_enr_poi_info và xử lý cũ đều không có. | mapping_place_type.md mục 1.9.3; user 2026-10-21 | 2026-10-21 |
| D-09 | JSON hiển thị | time_to_spend, best_time, cost_vnd làm theo mục 1.1, 1.2, 1.3 và mục 2 của mapping_gld_enr_poi_info.md. cost null thì JSON null, không phải object có value null. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-10 | Thiếu giá | Thiếu price_min hoặc price_max thì cost null và cost_vnd là JSON null. | user 2026-10-21 | 2026-10-21 |
| D-11 | Làm tròn 1.3 | Làm tròn về phần nghìn. Ví dụ 545899 làm tròn thành 546000; 5455 làm tròn thành 5000. | user 2026-10-21 | 2026-10-21 |
| D-12 | service_flag | Join amenity và join price không được nhân dòng gold. Cột gold service_flag là một mảng JSON; value trong JSON không bị trùng. Sort chữ tăng dần, bỏ null, POI không có value thì []. | user 2026-10-21 phương án B | 2026-10-21 |
| D-13 | types | Giữ tên types, giá trị lấy từ types_json. Không tạo thêm cột types_json. | user 2026-10-21 phương án B | 2026-10-21 |
| D-14 | destination_context | Bỏ cột destination_context. | user 2026-10-21 phương án A | 2026-10-21 |
| D-15 | cost_vnd chữ | cost_vnd là object JSON, key theo mục 2. Value dạng Từ 546,000đ khi số đã làm tròn là 546000. | user 2026-10-21; mapping_gld_enr_poi_info.md mục 1 | 2026-10-21 |
| D-16 | time_to_spend chữ | null hoặc ≤ 0: Không cố định, xét trước các nhánh khác. accommodation và giá trị > 0: ceil(avg_range_min / 1440) rồi {n} ngày. tour_n_activities và > 420: Cả ngày. < 60: {n} phút. Đúng 60: 1 tiếng. > 60: {h} tiếng khi dư 0 phút, còn lại {h} tiếng {m} phút. Sector ngoài mục 2 dùng nhãn other. Không thêm cột time_to_spend_minutes. | user 2026-10-21 phương án A | 2026-10-21 |
| D-17 | Giờ và cột không google | source_name khác google: rating, user_rating_count, price_level, review_json là null. opening_hours_text của partner lấy từ slv_pn_business_service_i18ns.amentities. Join bằng hash business_service_id + 'partner' như poi_id partner của slv_poi_entity_non_enrich: uuid_md5(business_service_id, 'partner') = entity.poi_id. Chỉ locale = vi. Lấy key operating_hours trong policies; không có thì null. Nguồn khác google và partner thì opening_hours_text null. | user 2026-10-21 | 2026-10-21 |
| D-18 | DROP info trên DEV | Đây là môi trường dev và đang phát triển. Xóa bảng gld_enr_poi_info và chạy lại như lần init đầu tiên. Không DROP gld_enr_poi_coordinate. Không dùng CREATE OR REPLACE. | user 2026-10-21 | 2026-10-21 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: PASS
size: 61463 bytes

## FILES

- architecture.md | 61463 bytes | large: use toc/show
- decision.md | 12347 bytes
- evidence/plan.md | 894 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 23214 bytes | large: use toc/show
- handoffs/author-input.md | 2213 bytes
- model-design.md | 12809 bytes
- request.md | 6470 bytes
- resume.md | 864 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1687 bytes

## NEXT

python scripts/vv.py run-gate 20261021-refresh-gld-enr-poi-info

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (206675 bytes)

[0] markdown id=init_md json=47-54 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=55-72 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=73-87 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=88-435 lines=334 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=436-450 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=451-648 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=649-663 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=664-745 lines=68 | _FL00, _ENR, _SLV1H = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV | defs: none
[8] code id=init_seed_place_type json=746-1214 lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=1215-1490 lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=1491-1648 lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=1649-1663 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=1664-1857 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=1858-1872 lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=1873-1887 lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (144743 bytes)

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
