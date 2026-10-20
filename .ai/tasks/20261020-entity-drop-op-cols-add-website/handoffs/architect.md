# Architect handoff: 20261020-entity-drop-op-cols-add-website

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261020-entity-drop-op-cols-add-website --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261020-entity-drop-op-cols-add-website/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261020-entity-drop-op-cols-add-website | phase=triage

## STATE

id: 20261020-entity-drop-op-cols-add-website
title: Drop op columns and add website_url on slv_poi_entity_non_enrich
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: data_model_change, stateful_logic, idempotency, cross_state_impact, runtime_proof_required
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb
- notebooks/NB_SLV_POI_AMENITY.ipynb
- notebooks/NB_SETUP_POI_ENTITY.ipynb
- notebooks/NB_SETUP_POI_AMENITY.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- tests/test_poi_entity_contract.py
- tests/test_poi_amenity_contract.py
- tests/test_initial_ddl_contract.py
- docs/context/01_DATA_MODEL.md
- docs/context/CTRL_TABLES_CONTEXT.md

## VALIDATION

PASS

## RESUME

# Resume

Status: waiting_architecture

Done this session: D9 names the partner dictionary row. The user chose Cursor Opus 5.5 and required effort medium. That combination is not a Cursor subagent model. The Task tool has no separate effort parameter. The only Opus 5.5 slug is effort low. No subagent was launched. No `exceptions` entry. `architecture.md` is still the placeholder.

Next action: User accepts Opus 5.5 low, accepts Sonnet 5.5 medium, or says to run `python scripts/vv.py run-gate 20261020-entity-drop-op-cols-add-website` after the Claude limit reset (15:10 Asia/Bangkok).

Read next: `.ai/tasks/20261020-entity-drop-op-cols-add-website/decision.md` heading `Quyết định hiện hành` row D9.

Waiting on: an available Architect model. Not a Fabric DEV step.

## REQUEST

# Request

## User outcome

Bảng slv_poi_entity_non_enrich đang thừa những cột _crawled_at, _event_id, _first_seen_at, _last_seen_at. Đây là cột op của nguồn 3rd, không lấy vào bảng này.
Thêm cột website_url với 3p (google) lấy từ slv_3p_poi_contact.website_url và partner lấy từ slv_pn_business_services.website_urls (lấy đường dẫn trong key website_url; data sample {"website_url":"https://stg-partner-portal-internal.visitvietnam.asia/"}).
Hãy sửa lại, có thể drop bảng, delete watermark để chạy lại như một lần init vì đây là môi trường dev.

Yêu cầu bổ sung:

- Thêm những cột sau cho bảng slv_poi_entity_non_enrich:
  - range_low_min = ref_dictionary_place_type.range_low_min
  - range_high_min = ref_dictionary_place_type.range_high_min
  - avg_range_min = ref_dictionary_place_type.avg_range_min
  - candidate_best_time_code = ref_dictionary_place_type.candidate_best_time_code
  - canonical_candidate = ref_dictionary_place_type.canonical_candidate
- Thêm cột service_flags = ref_dictionary_amenities.service_flags cho bảng slv_poi_amenity.
- Vẫn có thể drop bảng, delete watermark để chạy lại như một lần init vì đây là môi trường dev.

## Scope

### In scope

- Remove `_crawled_at`, `_event_id`, `_first_seen_at`, and `_last_seen_at` from `lh_vv_silver.dbo.slv_poi_entity_non_enrich` only.
- Add nullable STRING `website_url` on that table: google from `slv_3p_poi_contact.website_url` by `poi_id`; partner from JSON key `website_url` in `slv_pn_business_services.website_urls`.
- Copy `range_low_min`, `range_high_min`, `avg_range_min`, `candidate_best_time_code`, and `canonical_candidate` onto `slv_poi_entity_non_enrich` from the `ref_dictionary_place_type` row the entity already matched. No second match rule.
- Copy `service_flags` onto `slv_poi_amenity` from the `ref_dictionary_amenities` row the amenity already matched. Do not reseed either dictionary.
- DEV drop and watermark delete only for `slv_poi_entity_non_enrich` and `slv_poi_amenity`, then rerun as init. User runs Fabric DEV.

### Out of scope

- The four op columns on `slv_3p_*`.
- Dropping source tables, `ref_dictionary_place_type`, or `ref_dictionary_amenities`.
- Reseeding either dictionary.
- Writing the sample URL into a seed or a test.
- Marking `gates.runtime`.

## Acceptance criteria

- `slv_poi_entity_non_enrich` no longer has the four op columns and has nullable STRING `website_url`.
- Google rows take `slv_3p_poi_contact.website_url` through `poi_id`. Partner rows take the `website_url` key inside `website_urls`; a missing key is null.
- `slv_3p_*` still has the four op columns.
- `slv_poi_entity_non_enrich` also has the five estimate columns from the dictionary row it already matched.
- `slv_poi_amenity` has `service_flags` from the dictionary row it already matched.
- A DEV runbook drops only `slv_poi_entity_non_enrich` and `slv_poi_amenity`, deletes only those tables' watermarks, and reruns as init. `p_apply` defaults to false. The apply step is separate.

## Constraints

- Schema is `lh_vv_silver.dbo`. Contact grain in the data model is `poi_id`. If more than one contact row exists for one `poi_id`, record `USER_DECISION` and do not pick a row.
- Do not write the sample URL into a seed or a test.
- The five estimate columns come from the `ref_dictionary_place_type` row the entity already matched. Do not add a second match rule.
- `service_flags` comes from the `ref_dictionary_amenities` row `slv_poi_amenity` already matched. Do not reseed either dictionary.
- Drop and delete watermarks only for `slv_poi_entity_non_enrich` and `slv_poi_amenity` on DEV. Do not drop `ref_dictionary_place_type` or `ref_dictionary_amenities`.
- The runbook names DEV, a count before delete, the drop statement, which watermark rows are deleted, how to rebuild, and how to roll back. The user runs Fabric DEV. The agent does not set `gates.runtime`.

## Classification rationale

- Complexity: high. Column removal and a new column change the silver L2 grain projection, the node input set, and the pipeline edges that amenity setup counts.
- Risk: high. The change alters silver columns and edge watermarks. DEV recovery is drop-and-reinit of one table.
- Architecture: required. A silver column change and a watermark change are not a fast lane.
- Evidence: not required at triage. Contact grain is `poi_id` in `docs/context/01_DATA_MODEL.md` and the registry key is `poi_id`. A duplicate `poi_id` in contact is a `USER_DECISION`, not a row-picking rule. Probe only if the architecture gate returns `EVIDENCE_REQUIRED`.
- Runtime proof: required. The user runs the DEV drop, watermark delete, and init rerun. `gates.runtime` stays pending.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, and `risk-gate` (risk high).


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D1 | Cột op trên entity | Chỉ bỏ `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at` khỏi `lh_vv_silver.dbo.slv_poi_entity_non_enrich`. Giữ nguyên bốn cột trên các bảng `slv_3p_*`. | request.md User outcome | 2026-10-20 |
| D2 | `website_url` | `website_url` là STRING, nullable. Dòng google lấy `slv_3p_poi_contact.website_url` qua `poi_id`. Dòng partner lấy giá trị của key `website_url` trong JSON `slv_pn_business_services.website_urls`. Không có key thì null. Không ghi URL mẫu vào seed hay test. | request.md Constraints | 2026-10-20 |
| D3 | Grain contact | Grain `slv_3p_poi_contact` trong data model và registry là `poi_id`. Nhiều dòng contact cho một `poi_id` thì ghi `USER_DECISION`, không chọn dòng. | request.md Constraints | 2026-10-20 |
| D4 | DEV drop và watermark | Drop và xóa watermark chỉ với `slv_poi_entity_non_enrich` và `slv_poi_amenity` trên DEV để chạy lại như init. Không drop bảng nguồn, `ref_dictionary_place_type`, hay `ref_dictionary_amenities`. Runbook ghi môi trường DEV, bước đếm trước khi xóa, lệnh drop, watermark bị xóa, cách dựng lại và cách quay lại. User chạy Fabric DEV. Agent không đánh `gates.runtime`. | request.md Yêu cầu bổ sung | 2026-10-20 |
| D5 | Watermark được xóa | Xóa dòng watermark có `trg_tbl` là `slv_poi_entity_non_enrich` hoặc `slv_poi_amenity` (`wm_e__<trg_tbl>__<src_tbl>`). Không xóa `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`. | CTRL_TABLES_CONTEXT.md §4; request.md Yêu cầu bổ sung | 2026-10-20 |
| D6 | Nguồn model | Task không có `proposal.md`. `model-design.md` bám D1–D5. Không chạy lane proposal. Không đổi công thức `poi_id` partner và không sửa `AGENTS.md` trong task này. | model-design.md Conflicts 1–2 | 2026-10-20 |
| D7 | Join contact | Google không có dòng `slv_3p_poi_contact`: left join, `website_url` null. Không inner join, vì grain entity vẫn một dòng mỗi `poi_id`. `slv_3p_poi_contact` là input bắt buộc của node (thiếu bảng thì fail). Trùng `poi_id`: fail run, không chọn dòng, không ghi entity. | D2, D3; model-design.md Conflicts 3–4, 7 | 2026-10-20 |
| D8 | JSON partner | Lấy key top-level `$.website_url` bằng `get_json_object`. Không có key, JSON null, JSON không hợp lệ, hoặc giá trị không phải chuỗi JSON thì null. Chuỗi rỗng giữ nguyên. Không tìm key ở độ sâu khác. `website_url` đứng ngay sau `primary_type`. | D2; model-design.md Conflicts 5–6 | 2026-10-20 |
| D9 | Cột estimate | `slv_poi_entity_non_enrich` thêm `range_low_min`, `range_high_min`, `avg_range_min`, `candidate_best_time_code`, `canonical_candidate` từ đúng dòng `ref_dictionary_place_type` mà entity đã khớp. Không thêm rule khớp thứ hai. Không seed lại từ điển. Với partner: dòng `ref_dictionary_place_type` partner mà entity đã khớp qua `primary_type`. | request.md Yêu cầu bổ sung; user 2026-10-20 | 2026-10-20 |
| D10 | `service_flags` | `slv_poi_amenity` thêm `service_flags` từ đúng dòng `ref_dictionary_amenities` mà amenity đã khớp. Không thêm rule khớp thứ hai. Không seed lại từ điển. | request.md Yêu cầu bổ sung | 2026-10-20 |

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
- decision.md | 7537 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 25924 bytes | large: use toc/show
- handoffs/author-input.md | 1968 bytes
- model-design.md | 9748 bytes
- request.md | 4961 bytes
- resume.md | 791 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1840 bytes

## NEXT

python scripts/vv.py run-gate 20261020-entity-drop-op-cols-add-website

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SLV_POI_AMENITY.ipynb (20632 bytes)

[0] markdown id=d1amenmd json=47-56 lines=3 | NB_SLV_POI_AMENITY | defs: none
[1] code id=d1amenparam json=57-73 lines=8 | p_exec_id = "" | defs: none
[2] code id=d1amenrun json=74-83 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=d1amenmatch json=84-218 lines=126 | import re | defs: resolve_condition, is_legacy_form, match_conditions, legacy_blocks_write, match_coverage
[4] code id=d1amenbuild json=219-295 lines=68 | GOOGLE = "google" | defs: build
[5] code id=d1amenres json=296-305 lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=d1amenexit json=306-315 lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### notebooks/NB_SETUP_POI_ENTITY.ipynb (80989 bytes)

[0] markdown id=a1setupmd json=47-58 lines=5 | NB_SETUP_POI_ENTITY | defs: none
[1] code id=a1setupparam json=59-76 lines=1 | p_apply = "false" | defs: none
[2] code id=a1setuprun json=77-91 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=a1setupseed json=92-557 lines=452 | import re | defs: validate_seed
[4] code id=a1setupplan json=558-628 lines=57 | import json | defs: none
[5] code id=a1setupddl json=629-679 lines=37 | spark.sql(""" | defs: none
[6] code id=a1setupmerge json=680-753 lines=60 | def _seed_merge(): | defs: _seed_merge
[7] code id=a1setupedges json=754-954 lines=187 | import uuid | defs: setup_edge_issues, _write_edges
[8] code id=a1setupexit json=955-979 lines=11 | import json | defs: none

### notebooks/NB_SETUP_POI_AMENITY.ipynb (57122 bytes)

[0] markdown id=c1setupmd json=47-56 lines=3 | NB_SETUP_POI_AMENITY | defs: none
[1] code id=c1setupparam json=57-66 lines=1 | p_apply = "false" | defs: none
[2] code id=c1setuprun json=67-76 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=c1setupseed json=77-345 lines=260 | import re | defs: amenity_keys, validate_seed
[4] code id=c1setupplan json=346-412 lines=58 | import json | defs: none
[5] code id=c1setupddl json=413-479 lines=58 | spark.sql(""" | defs: none
[6] code id=c1setupmerge json=480-556 lines=68 | def _seed_merge(): | defs: _seed_merge
[7] code id=c1setupedges json=557-742 lines=177 | import uuid | defs: setup_edge_issues, _write_edges
[8] code id=c1setupexit json=743-763 lines=12 | import json | defs: none

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (206393 bytes)

[0] markdown id=init_md json=47-54 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=55-72 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=73-87 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=88-432 lines=331 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=433-447 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=448-645 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=646-660 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=661-741 lines=67 | _FL00, _ENR, _SLV1H = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV | defs: none
[8] code id=init_seed_place_type json=742-1210 lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=1211-1486 lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=1487-1644 lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=1645-1659 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=1660-1853 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=1854-1868 lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=1869-1883 lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (138337 bytes)

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

### docs/context/01_DATA_MODEL.md (32726 bytes)

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

### docs/context/CTRL_TABLES_CONTEXT.md (45812 bytes)

# CTRL_TABLES_CONTEXT — 7 bảng control `lh_vv_ctrl.dbo` | L1-L568
## 1. Tổng quan | L7-L24
## 2. Quan hệ | L25-L48
## 3. `ctrl_mng_pipeline_config` | L49-L143
### DDL | L54-L73
### Cột | L74-L89
### Dữ liệu hiện có | L90-L133
### Thao tác thường gặp | L134-L143
## 4. `ctrl_mng_watermark` | L144-L234
### DDL | L154-L178
### Cột theo loại dòng | L179-L203
### Ghi chú migration — số đo watermark trước 08/10 tại `lh_vv_bronze.ctrl` (dòng 3P cũ `wm_transform_poi_raw_event`) | L204-L212
### Thao tác thường gặp | L213-L234
## 5. `ctrl_cfg_schema_registry` | L235-L324
### DDL | L240-L264
### Luật cấu hình (lib kiểm tra, sai → `ConfigError` trước khi ghi) | L265-L275
### Dữ liệu hiện có (seed `NB_CREATE_DDL`, cấu hình chốt 04/10 chiều) | L276-L324
## 6. `ctrl_log_run` — 1 dòng / lần chạy notebook (khoá `exec_id`) | L325-L395
### DDL | L329-L369
### Cột khác nghĩa giữa extract và NB_00 | L370-L384
### Ghi chú migration — log đã thấy trước 08/10 tại vị trí control cũ | L385-L395
## 7. `ctrl_log_table_run` — 1 dòng / bảng đích (hoặc node) / lần chạy | L396-L451
### DDL | L398-L451
## 8. `ctrl_cdc_state` — 1 dòng / entity / bảng đích (chỉ extract) | L452-L491
### DDL | L456-L491
## 9. `ctrl_cdc_reject` — 1 dòng / event (hoặc phần tử) lỗi (chỉ extract) | L492-L545
### DDL | L494-L545
## 10. Lịch sử thay đổi (tóm tắt) | L546-L558
## 11. Việc còn lại liên quan ctrl | L559-L568
