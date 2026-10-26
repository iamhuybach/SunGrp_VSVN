# Architect handoff: 20261025-poi-media-and-srv-amenity

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261025-poi-media-and-srv-amenity --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261025-poi-media-and-srv-amenity/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261025-poi-media-and-srv-amenity | phase=triage

## STATE

id: 20261025-poi-media-and-srv-amenity
title: POI media info, media gallery, and serving amenity
status/owner: waiting_architecture/architect
complexity/risk: high/medium
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: data_model_change, data_evidence_required, design_tradeoffs, idempotency, runtime_proof_required, cross_system
gates: evidence=pass, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer
open findings: none
exceptions: none
scope.files:
- docs/context/mapping_poi_media_info.md
- docs/context/mapping_gld_srv_poi_amenity.md
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_SLV_POI_MEDIA_INFO.ipynb
- notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb
- notebooks/NB_GLD_SRV_POI_AMENITY.ipynb

## VALIDATION

PASS

## RESUME

# Resume

Status: waiting_evidence

Done this session: Recorded U1–U7, Q9, Q10, and Q11. Set mapping `is_cover` to boolean and wrote the U5 rule. P1 shows 940 unique `media_dedup_key` values and `poi_with_min_tie = 5`. P2 shows one `vi` row per id and zero `deleted`. P3 shows 47 empty `vi` media values and 0 fallback hits. P4 failed because `uuid_md5` was not defined; P5 did not run. The probe now copies `uuid_md5` from `NB_LIB_TRANSFORM_SLV_GLD`. `PL_VV_TRANS_SLV_TO_GLD_1H` is not in the repo; the orchestrator default is `PL_VV_TRANSFORM_SLV_TO_GLD_1H`. Did not rerun Author.

Next action: Record the tie-break column and the exact 1H `pl_name`. Interpret a new P4/P5 stdout. Then rerun `run-author --kind model` and `run-gate`.

Read next: `decision.md` rows U-TIE and U1-1H; `evidence/probes/media_key_grain.py`; `docs/context/mapping_poi_media_info.md` §1.2 `is_cover`.

Waiting on: tie-break column, 1H pipeline token, and Fabric DEV P4/P5.

## REQUEST

# Request

## User outcome

Xử lý 3 bảng `slv.slv_poi_media_info`, `gld_srv_poi_media_gallery` và `gld_srv_poi_amenity` theo 2 file mapping sau:

- `docs/context/mapping_poi_media_info.md`
- `docs/context/mapping_gld_srv_poi_amenity.md`

Ngoài ra, bổ sung nghiệp vụ và mapping hiện tại của `slv.slv_poi_amenity` vào `docs/context/mapping_gld_srv_poi_amenity.md`.

Đọc mapping thế này:

- `slv.` là nhãn tầng silver, bảng vật lý `lh_vv_silver.dbo`. `gld_srv_*` là `lh_vv_gold.dbo`. Không tạo schema SQL tên `slv`.
- `slv_poi_media_info` là bảng silver mới. Nguồn là union `slv_3p_poi_media` với nhánh partner trong §1.1. Chữ "Append" trong mapping là gộp nguồn, không phải Delta append-only.
- `gld_srv_poi_media_gallery` là gold mới, transform 1-1 từ `slv_poi_media_info`, chỉ khác `created_at` và `updated_at`.
- `gld_srv_poi_amenity` là gold mới, transform 1-1 từ `lh_vv_silver.dbo.slv_poi_amenity`, chỉ khác `created_at` và `updated_at`.
- Không đổi logic, grain, khóa hay cạnh ctrl của `slv_poi_amenity`. Chỉ mô tả hiện trạng của bảng đó vào `mapping_gld_srv_poi_amenity.md`, rồi mới ghi rule gold 1-1.

Một task cho đủ ba bảng. Không tách media và amenity.

## Scope

### In scope

- DDL, registry, cạnh ctrl và node notebook `NB_<UPPER(trg_tbl)>` cho `slv_poi_media_info`, `gld_srv_poi_media_gallery`, `gld_srv_poi_amenity`.
- `NB_CREATE_DDL` và `NB_SETUP_INITIAL_DDL` cùng một bộ bảng và cạnh.
- Test contract của ba bảng đích.
- Mô tả hiện trạng `slv_poi_amenity` trong `docs/context/mapping_gld_srv_poi_amenity.md`, lấy từ notebook, DDL và test. Thiếu trong code thì ghi `MISSING`.
- Miền: lib transform/gold và DDL/registry.

### Out of scope

- Đổi logic, grain, khóa hoặc cạnh ctrl của `slv_poi_amenity`.
- Sửa notebook trước khi architecture `PASS`.
- Gán `pl_name` từ mẫu `gld_srv_poi_info` hoặc từ chỗ mapping không ghi.
- Tách task media và task amenity.
- Fast lane.
- Đọc `docs/context/3p-google/*.txt`. Chỉ mở `docs/context/3p-google/poi_amenity_mapping.md` khi notebook amenity trích đúng file đó.

## Acceptance criteria

- Ba bảng đích có DDL, registry, node notebook `NB_<UPPER(trg_tbl)>`, cạnh ctrl không nhân đôi, và test contract.
- `NB_CREATE_DDL` và `NB_SETUP_INITIAL_DDL` cùng một bộ bảng và cạnh.
- Media partner: `locale = vi`; `media` của i18n null hoặc rỗng thì lấy `slv_pn_business_services.media` cùng `poi_id`. `poi_id` partner giữ công thức đã có `uuid_md5(id, 'partner')`.
- Gallery và amenity gold không thêm cột nghiệp vụ ngoài bảng nguồn. Timestamp là field hệ thống của gold.
- Ghi MERGE idempotent theo khóa đã chốt. Không INSERT append-only.
- Phần amenity trong mapping tách bạch: hiện trạng silver lấy từ code, rule gold chỉ là 1-1.

## Constraints

- Có `data_model_change`. Trước `run-gate` architecture phải có `model-design.md` qua `run-author --kind model`.
- Không bịa `pl_name`, khóa MERGE, shape JSON `media`, hay cách căn lại bảng field.
- Mapping không ghi pipeline. Mẫu `gld_srv_poi_info` không được dùng để gán pipeline cho ba bảng này.
- Bảng field §1.2 của media đang lệch hàng: nguồn 3P, nguồn partner, kiểu và target không cùng một cột. `is_cover` chỉ ghi "chọn theo order bé nhất", chưa có kiểu boolean, grain, hay giá trị của dòng còn lại. Coi đó là `CONFLICT`. Dừng ở `user_decision` trước model-design và architecture. Không tự dịch hàng.
- Shape `slv_pn_business_service_i18ns.media` và `slv_pn_business_services.media` không có trong repo thì viết probe nhỏ nhất và dừng ở `waiting_evidence`. Không bịa array hay object.
- Registry hiện ghi cả hai cột `media` là `string`. Shape bên trong chuỗi chưa có trong repo. Probe chỉ viết sau khi hết CONFLICT.

## Classification rationale

- Complexity: `high`. Ba bảng mới, union silver, hai gold 1-1, DDL ở cả hai notebook setup, cạnh ctrl, MERGE idempotent, và spec §1.2 chưa căn được.
- Risk: `medium`. Thêm bảng mới. Logic, grain, khóa và cạnh ctrl của `slv_poi_amenity` giữ nguyên. Rollback của bảng mới là drop bảng và xóa cạnh mới. Không phải `high` vì không đổi recovery của bảng đang chạy.
- Architecture: required. Grain và khóa bảng mới, logic silver sang gold, nhiều hơn tám file, và `is_cover` còn nhiều cách đọc. `data_model_change` nên cần `model-design.md` trước Architect. Fast lane không áp dụng.
- Evidence: required. Cột partner `media` chỉ là `string`. Array hay object, và field `url` / `order`, không có trong registry. Grain `media_id` / `media_dedup_key` cũng chưa chốt vì §1.2 lệch hàng. Probe chờ hết CONFLICT.
- Runtime proof: required. DDL, registry và MERGE trên Fabric DEV chưa chứng minh được bằng test local.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`. `risk_gate` không bắt buộc vì risk `medium`. `fabric-pipeline-reviewer` chưa đưa vào: mapping không ghi pipeline và `pl_name` không được suy từ `gld_srv_poi_info`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-MEDIA-12 | Rule `is_cover` | Boolean. Một bản ghi: `display_order` null vẫn là cover. Nhiều bản ghi: order nhỏ nhất khác null. Hòa order: dòng gặp trước. | Chat U5, U-TIE, Q10, 2026-10-26 | 2026-10-26 |
| D-MEDIA-SHAPE | Shape `media` partner trên Fabric DEV | Phần tử có dữ liệu là JSON array of objects. `url` string, `order` int. Không có object gốc. `preview` có hoặc không. | `evidence/results/partner_media_shape.txt` | 2026-10-26 |
| U1 | `pl_name` | `slv_poi_media_info` và `gld_srv_poi_media_gallery`: `PL_VV_TRANS_SLV_TO_GLD_30P`. `gld_srv_poi_amenity`: `PL_VV_TRANS_SLV_TO_GLD_1H`. | Chat U1 và U1-1H, 2026-10-26 | 2026-10-26 |
| U2 | Khóa MERGE media và gallery | `media_id` | Chat U2, 2026-10-26 | 2026-10-26 |
| U3 | Phần tử `url` null hoặc trắng | Bỏ phần tử. Nguồn url: i18n, hoặc services khi media i18n rỗng. | Chat U3, 2026-10-26 | 2026-10-26 |
| U4 | `[]` và JSON null | Tính là rỗng, lấy `slv_pn_business_services.media`. | Chat U4, 2026-10-26 | 2026-10-26 |
| U6 | Soft delete `is_active` | Chuyển `false`. | Chat U6, 2026-10-26 | 2026-10-26 |
| U7 | Partner `deleted` | Loại khỏi silver media. | Chat U7, 2026-10-26 | 2026-10-26 |
| Q9 | `source_name` | `google` và `partner`. | Chat Q9, 2026-10-26 | 2026-10-26 |
| Q11 | `blob_url` partner | Giữ nguyên chuỗi, không trim. | Chat Q11, 2026-10-26 | 2026-10-26 |
| U-TIE | Hòa `display_order` nhỏ nhất | Dòng nào gặp trước là `is_cover`. Không thêm cột sắp. P1: `poi_with_min_tie = 5`. | Chat U-TIE, 2026-10-26 | 2026-10-26 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 26047 bytes

## FILES

- architecture.md | 26047 bytes | large: use toc/show
- decision.md | 12494 bytes
- evidence/plan.md | 1296 bytes
- evidence/probes/media_key_grain.py | 3919 bytes
- evidence/probes/partner_media_shape.py | 4586 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/media_key_grain.txt | 1103 bytes
- evidence/results/media_key_grain_partial.txt | 934 bytes
- evidence/results/partner_media_shape.txt | 2624 bytes
- handoffs/architect.md | 20268 bytes
- handoffs/author-input.md | 2663 bytes
- model-design.md | 14772 bytes
- request.md | 5432 bytes
- resume.md | 966 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1725 bytes

## NEXT

python scripts/vv.py run-gate 20261025-poi-media-and-srv-amenity

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_CREATE_DDL.ipynb (229810 bytes)

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

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (220889 bytes)

[0] markdown id=init_md json=unknown lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=unknown lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=unknown lines=427 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=unknown lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=unknown lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=unknown lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=unknown lines=80 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[8] code id=init_seed_place_type json=unknown lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=unknown lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=unknown lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=unknown lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=unknown lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=unknown lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=unknown lines=7 | summary = { | defs: none
