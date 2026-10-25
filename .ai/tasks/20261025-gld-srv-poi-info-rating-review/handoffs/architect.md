# Architect handoff: 20261025-gld-srv-poi-info-rating-review

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261025-gld-srv-poi-info-rating-review --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261025-gld-srv-poi-info-rating-review/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261025-gld-srv-poi-info-rating-review | phase=triage

## STATE

id: 20261025-gld-srv-poi-info-rating-review
title: Add rating and review count to gld_srv_poi_info
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: data_model_change, data_evidence_required, runtime_proof_required
gates: evidence=pass, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, fabric-pipeline-reviewer
open findings: none
exceptions: none
scope.files:
- docs/context/mapping_gld_srv_poi_info.md
- notebooks/NB_GLD_SRV_POI_INFO.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- tests/test_gld_srv_poi_contract.py

## VALIDATION

PASS

## RESUME

Status: waiting_architecture
Done this session: Probe rating_grain passed (345 rows, 345 poi_id, 0 null, 0 duplicate groups). Evidence gate is pass. Ledger D-01 to D-05 records the grain, COUNT(*), INT overflow fail, partner NULL, and no 01_DATA_MODEL.md edit. model-design.md is the merged author output. run-gate did not save architecture.md.
Next action: Rerun python scripts/vv.py run-gate 20261025-gld-srv-poi-info-rating-review when no other session is writing the repo. The 496s Architect run was rejected because git status changed during the run. Tracked files were unchanged. architecture.md is still the placeholder. Do not implement.
Read next: .ai/tasks/20261025-gld-srv-poi-info-rating-review/model-design.md (Columns, Conflicts and questions); decision.md (Quyết định hiện hành)
Waiting on: a clean architecture run-gate. Parallel writes landed in 20261025-poi-media-and-srv-amenity and docs/context/mapping_poi_media_info.md while the gate was running.

## REQUEST

# Request

## User outcome

Bổ sung nghiệp vụ `gld_srv_poi_info`:

Nếu có poi_id thỏa mãn điều kiện slv_poi_entity_non_enrich.source_name = 'google' chỉ lấy khi poi_id có cả trong cả 2 bảng slv_enr_poi_destination và slv_enr_poi_info_multi_lang, left join với 2 bảng slv_3p_poi_rating và slv_3p_poi_review với logic sau:

- slv_3p_poi_rating.rating_overall, decimal(4,2), transform 1-1 → rating_overall
- slv_3p_poi_rating.rating_count, integer, transform 1-1 → rating_count
- slv_3p_poi_review, integer, count số lượng review theo poi_id → review_count

Khóa join của hai bảng mới là poi_id. Grain đích vẫn một dòng poi_id. MERGE vẫn theo poi_id.

Đã có trong repository, phải giữ, không viết lại:

- docs/context/mapping_gld_srv_poi_info.md §1.1 đã có rule Google giao hai bảng enriched và rule partner lấy full.
- notebooks/NB_GLD_SRV_POI_INFO.ipynb def:build đã lọc ~is_google | _both.

Việc mới là ba cột và hai nguồn left join. Partner và mọi dòng không khớp rating hoặc review để NULL. Không coalesce review_count thành 0. Không đổi rule operating_hours, is_recommended, hay các cột §1.2 hiện có.

## Scope

### In scope

- Three gold columns and two left joins: `rating_overall`, `rating_count`, `review_count`.
- `docs/context/mapping_gld_srv_poi_info.md` §1.2.
- `notebooks/NB_GLD_SRV_POI_INFO.ipynb` `OUT_COLS`, `SPEC.inputs`, and the build select.
- `notebooks/NB_CREATE_DDL.ipynb` and `notebooks/NB_SETUP_INITIAL_DDL.ipynb`: target DDL and the node input registry.
- `tests/test_gld_srv_poi_contract.py` for `gld_srv_poi_info`.

### Out of scope

- Rewriting the Google intersection rule or the partner-full rule in §1.1 or `build`.
- Changing `operating_hours`, `is_recommended`, or any current §1.2 column.
- Coalescing a missing `review_count` to 0.
- Choosing a `slv_3p_poi_rating` row when one `poi_id` has more than one row.
- A separate analysis task or a separate mapping task.

## Acceptance criteria

- source_name google, sau lower/trim như notebook hiện tại, chỉ còn khi poi_id có trong cả slv_enr_poi_destination và slv_enr_poi_info_multi_lang.
- Dòng partner vẫn lấy full.
- rating_overall và rating_count là transform 1-1 từ slv_3p_poi_rating; kiểu decimal(4,2) và integer.
- review_count là count review theo poi_id từ slv_3p_poi_review, kiểu integer; không có review thì NULL.
- Không match rating hoặc review không loại poi_id.
- slv_3p_poi_rating lệch grain 1 dòng / poi_id thì không tự chọn dòng; dừng để probe hoặc quyết định.
- DDL bảng đích, OUT_COLS, mapping §1.2, contract test và registry input của node cùng một bộ cột.
- File mapping (`docs/context/mapping_gld_srv_poi_info.md`), NB_CREATE_DDL và NB_SETUP_INITIAL_DDL cùng được cập nhật.

## Constraints

- One task: TRIAGE → EVIDENCE if required → model-design → ARCHITECTURE → IMPLEMENT → LOCAL VERIFY → REVIEW.
- Do not edit the notebook before architecture PASS.
- `data_model_change` is set because gold columns are added. Before the architecture `run-gate`, write `handoffs/author-input.md` and run `python scripts/vv.py run-author <task-id> --kind model`.
- Evidence is required when the repository does not prove that `slv_3p_poi_rating` has one row per `poi_id`.
- Architecture is required. No fast lane.
- A deviation from the Main brief is recorded in `decision.md` before code changes.
- Save `FILE:` blocks with `python scripts/vv.py materialize <task-id> --write`.
- Task `20261024-gld-srv-poi-from-mapping` is `ready_to_merge` and is not still editing `NB_GLD_SRV_POI_INFO`, so this work is a new task.

## Classification rationale

- Complexity: `medium`. Signals: `data_model_change`, `data_evidence_required`, `runtime_proof_required`. The target grain and MERGE key stay `poi_id`. The change adds columns, two left joins, a review count, DDL, registry inputs, mapping §1.2, and the contract test. That is a behavior change across more than two files, so it is not `low` and not a fast lane.
- Risk: `medium`. The behavior change is bounded to three additive columns and left joins. Rollback is reverting the notebook and dropping those columns. No new lock, watermark, or retry design.
- Architecture: required. The user forbids the fast lane. A rating grain other than one row per `poi_id` would multiply the MERGE source. `data_model_change` also requires `model-design.md` before `run-gate`.
- Evidence: required. `docs/context/01_DATA_MODEL.md` §5.2 and the 3rd-party registry in both DDL notebooks declare `slv_3p_poi_rating` as `DOC` with key `poi_id`, `rating_overall` `decimal(4,2)`, and `rating_count` `bigint`. `slv_3p_poi_review` is `DOC_ARRAY` with key `review_id`, so many reviews per `poi_id` is the declared shape. Neither DDL notebook creates a UNIQUE constraint, and the repository has no measured row count. Declared key is not proof of current cardinality.
- Runtime proof: required after implementation. Local tests can align columns; the live left joins need a Fabric DEV run of the gold node.
- Reviewer routing: `sql-data-reviewer` (join, count, types, MERGE-source grain), `spark-runtime-reviewer` (notebook contract and Delta DDL), `fabric-pipeline-reviewer` (new `ctrl_mng_pipeline_config` inputs change what triggers `NB_GLD_SRV_POI_INFO`). No `state-correctness-reviewer`: lock, watermark, and retry stay on the existing `run_node` path. No `risk-gate`: risk is `medium`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Grain `slv_3p_poi_rating` | Fabric DEV 2026-10-26: 345 dòng, distinct_poi_id 345, null_poi_id_rows 0, duplicate_poi_id_groups 0. Cột đo được: poi_id string, rating_overall decimal(4,2), rating_count bigint. Grain hiện tại một dòng mỗi poi_id; left join 1-1 được dùng. Lệch grain sau này thì không chọn dòng. | evidence/results/rating_grain.txt | 2026-10-26 |
| D-02 | `review_count` | `review_count` là count số lượng review theo `poi_id`: `COUNT(*)` nhóm theo `poi_id`, cast `INT`. Không dùng `COUNT(DISTINCT review_id)`. Dòng `review_id` NULL vẫn đếm. Không có dòng thì NULL sau left join. | request.md User outcome | 2026-10-26 |
| D-03 | Cast integer | `rating_count` và `review_count` là integer (`INT`). Transform 1-1 từ `bigint` hoặc từ count. Giá trị ngoài miền `INT` làm node dừng. Không ghi NULL thay giá trị và không đổi cột thành `bigint`. | request.md User outcome | 2026-10-26 |
| D-04 | NULL partner | Dòng partner, sau lower/trim như notebook, để NULL ở cả ba cột. Mọi dòng không khớp rating hoặc review cũng NULL và vẫn giữ `poi_id`. | request.md User outcome | 2026-10-26 |
| D-05 | Nguồn mô tả cột | Cột mới ghi ở mapping §1.2, DDL, `OUT_COLS`, contract test và registry input. Không sửa `docs/context/01_DATA_MODEL.md` trong task này. | request.md Acceptance criteria | 2026-10-26 |

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
- decision.md | 2995 bytes
- evidence/plan.md | 1786 bytes
- evidence/probes/rating_grain.py | 1252 bytes
- evidence/probes/README.md | 310 bytes
- evidence/results/rating_grain.txt | 498 bytes
- handoffs/architect.md | 20839 bytes | large: use toc/show
- handoffs/author-input.md | 4128 bytes
- model-design.md | 8557 bytes
- request.md | 5605 bytes
- resume.md | 982 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1562 bytes

## NEXT

python scripts/vv.py run-gate 20261025-gld-srv-poi-info-rating-review

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_CREATE_DDL.ipynb (218684 bytes)

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
[40] markdown id=srvpoimd json=3197-3208 lines=5 | [THÊM 24/10] 20261024-gld-srv-poi-from-mapping | defs: none
[41] code id=srvpoipy json=3209-3427 lines=205 | import uuid | defs: _want, _schema, _create_sql, _edge_rows, _refresh_lock

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (212673 bytes)

[0] markdown id=init_md json=47-54 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=55-72 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=73-87 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=88-525 lines=424 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=526-540 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=541-738 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=739-753 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=754-845 lines=78 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[8] code id=init_seed_place_type json=846-1314 lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=1315-1590 lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=1591-1748 lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=1749-1763 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=1764-1957 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=1958-1972 lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=1973-1987 lines=7 | summary = { | defs: none
