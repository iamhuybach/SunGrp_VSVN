# Architect handoff: 20261126-legacy-init-enriched-cols-and-dest-portal

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261126-legacy-init-enriched-cols-and-dest-portal --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261126-legacy-init-enriched-cols-and-dest-portal/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261126-legacy-init-enriched-cols-and-dest-portal | phase=triage

## STATE

id: 20261126-legacy-init-enriched-cols-and-dest-portal
title: Init six gold columns from ai_enriched_poi and add destination_portal_id
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: data_model_change, data_evidence_required, runtime_proof_required
gates: evidence=pass, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: spark-runtime-reviewer, sql-data-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb
- notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- docs/context/mapping_legacy_gold_to_gld_srv.md
- docs/context/mapping_gld_srv_poi_info.md
- tests/test_initial_ddl_contract.py
- tests/test_enr_poi_contract.py
- tests/test_gld_srv_poi_contract.py
- tests/test_srv_poi_serving_contract.py
- tests/test_enr_extract_contract.py
- tests/test_legacy_gold_poi_init_contract.py
- docs/context/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md

## VALIDATION

PASS

## RESUME

Status: user_decision

Done this session: Explained the three open choices. Recommendation, not yet chosen: D-DEST-BACKFILL 1, D-LEGACY-DEST 1, G4 1. Evidence pass. Architecture remains evidence_required. D-INIT-KEY, D-INIT-INFO-VI, D-INIT-ENRICH-ONLY are already on the ledger.

Next action: On the three answers, write D-DEST-BACKFILL, D-LEGACY-DEST, and the G4 scope paths. Rerun run-author --kind model, then run-gate once. Do not implement before architecture PASS.

Read next: decision.md ## Câu hỏi đang mở; evidence/results/p_gaps.txt; architecture.md ## 6.

Waiting on: D-DEST-BACKFILL 1, 2, or 3; D-LEGACY-DEST 1 or a verbatim 2; G4 1, 2, or 3.

## REQUEST

# Request

## User outcome

One legacy init run fills six existing gold columns from `ai_enriched_poi`, matched on `(poi_id, lang)` for `story` and `local_tips`. `slv_enr_poi_destination.destination_id` becomes each destination element's `strapi_document_id`, and the element's `id` is stored only as silver `destination_portal_id`. Gold `destination_id` keeps its 1-1 copy from silver, so its values follow the new silver source.

## Scope

### In scope

- `NB_SETUP_LEGACY_GOLD_POI` and `docs/context/mapping_legacy_gold_to_gld_srv.md`: map the six existing gold columns from `ai_enriched_poi`. Other legacy tables stay unread for load.
- `slv_enr_poi_destination`: add `destination_portal_id` in `TABLE_SPECS` and one new patch cell in `NB_CREATE_DDL`. Extract enrichment projects `strapi_document_id` to `destination_id` and `id` to `destination_portal_id`, with matching registry/config. `destination_id`, `destination_portal_id`, and `destination_name` stay JSON array strings in the same element order, including null elements.
- `docs/context/mapping_gld_srv_poi_info.md`: gold `destination_id` is the silver copy after silver changes source. Do not describe `destination_portal_id` on gold.
- Contract tests: `tests/test_initial_ddl_contract.py`, `tests/test_enr_poi_contract.py`, `tests/test_gld_srv_poi_contract.py`, `tests/test_srv_poi_serving_contract.py`.

### Out of scope

- New gold columns, grain changes, and MERGE key changes.
- The `old_address` formula in `NB_GLD_SRV_POI_INFO` (D-OLD-ADDR).
- PostgreSQL, Java, and `docs/context/api-mapping/` for the six gold-only columns and for `destination_portal_id`.
- `notebooks_lgc/`, `docs/poi-serving-api/`, and `services/data-serving-service/` except the serving contract test.
- `pipelines/*.json` unless a later edit touches them.

## Acceptance criteria

- Init writes the six mappings. `story` and `local_tips` match `(poi_id, lang)`. A second init run does not multiply rows.
- `docs/context/mapping_legacy_gold_to_gld_srv.md` documents the six columns. Other legacy tables remain unread for load.
- `TABLE_SPECS` and one new `NB_CREATE_DDL` patch cell add `destination_portal_id`. Extract enrichment and registry/config match the two source keys.
- `docs/context/mapping_gld_srv_poi_info.md` states that gold `destination_id` is copied from silver after the silver source change, and does not describe `destination_portal_id` on gold.
- DDL, extract enrichment, legacy init, and serving contract tests are updated. `test_gold_and_pg_columns_and_types_match` still matches. `destination_portal_id` and the six gold-only columns are exceptions in the right place.
- `python scripts/vv.py verify` is PASS before review. P0/P1 findings are handled within two rounds.

## Constraints

- One task for both changes. Signal `data_model_change` because of `destination_portal_id`.
- The language column name on `ai_enriched_poi` comes from a schema already in the repo. If that schema or the JSON keys are absent, write the smallest probe and stop at `waiting_evidence`. Do not invent the column name.
- `price_level`, `price_min`, and `price_max` keep the current gold types.
- Requirements source is this request. Task `20261126-gld-srv-old-address-price-story` is only the ledger for D-OLD-ADDR and the gold-only scope of the six columns.
- No commit. No Fabric DEV execution by Main. The user runs probes and the runtime runbook.
- Reviewers: `spark-runtime-reviewer` and `sql-data-reviewer`. Add `fabric-pipeline-reviewer` only if `pipelines/*.json` changes.

## Classification rationale

- Complexity: medium. Two notebook behaviors and a new silver column, across extract, DDL, and gold init. Not low: the change is a behavior change and more than two files.
- Risk: medium. Bounded value change with local contract tests and a later runtime runbook. MERGE keys and grain stay as they are. Rollback is a forward rerun from the previous mapping. Not high: no new lock, watermark, or retry protocol, and PostgreSQL/API contracts do not gain columns.
- Architecture: required. Code scope is four notebooks and four contract tests (eight source files), plus two mapping docs. `data_model_change` also requires `model-design.md` before the Architect.
- Evidence: required. Current notebooks, `docs/context/`, `sql/`, and `tests/` do not define `ai_enriched_poi` columns or `poi_address_json` keys. `docs/context/mapping_legacy_ai_product.md` only uses `ai_enriched_poi.source_id`. `notebooks_lgc/` is out of scope and is not a schema source. Gold types for the six columns are already in `NB_SETUP_INITIAL_DDL` `TABLE_SPECS`.
- Runtime proof: required after review PASS, for the init write and the idempotent rerun. Not run in this phase.
- Reviewer routing: `spark-runtime-reviewer` (Fabric notebook and Delta write) and `sql-data-reviewer` (Spark SQL projection, DDL, MERGE match keys). No pipeline JSON, so no `fabric-pipeline-reviewer`. Risk is medium, so no risk gate.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-ONE-TASK | Phạm vi | Một task, không tách hai việc. | request.md ## User outcome | 2026-11-26 |
| D-OLD-ADDR | old_address | Không sửa công thức old_address của NB_GLD_SRV_POI_INFO (D-OLD-ADDR). | request.md ## Constraints | 2026-11-26 |
| D-NO-GOLD-COL | Cột gold | Không thêm cột gold, không đổi grain hay khóa MERGE. | request.md ## Scope | 2026-11-26 |
| D-MAP-OLD-ADDR | old_address init | old_address lấy address_line_2 | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-MAP-PRICE-LEVEL | price_level init | price_level lấy cột cùng tên | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-MAP-PRICE-MIN | price_min init | price_min lấy cột cùng tên | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-MAP-PRICE-MAX | price_max init | price_max lấy cột cùng tên | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-MAP-STORY | story init | story lấy story. Khớp (poi_id, lang). | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-MAP-TIPS | local_tips init | local_tips lấy local_tips_or_neighborhood. Khớp (poi_id, lang). | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-LANG-ROW | Khớp lang | story và local_tips gắn đúng dòng (poi_id, lang). Không nhân một giá trị sang mọi lang của POI. | request.md ## Acceptance criteria | 2026-11-26 |
| D-PRICE-TYPE | Kiểu giá | Gold giữ INT và DECIMAL(18,2); nguồn giá là int. | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-GOLD-ONLY | Sáu cột | Sáu cột vẫn gold-only: PostgreSQL, Java, docs/context/api-mapping/ không nhận chúng. | request.md ## Constraints | 2026-11-26 |
| D-LEGACY-READ | Bảng legacy | Các bảng legacy khác vẫn không được đọc để nạp. | request.md ## Acceptance criteria | 2026-11-26 |
| D-DEST-ID | destination_id | destination_id = strapi_document_id của từng phần tử | request.md ## User outcome | 2026-11-26 |
| D-DEST-PORTAL | destination_portal_id | destination_portal_id = id của từng phần tử. Payload có khóa id, không có khóa destination_id | request.md ## User outcome | 2026-11-26 |
| D-DEST-NAME | destination_name | destination_name giữ nguyên | request.md ## Scope | 2026-11-26 |
| D-DEST-ARRAY | Thứ tự mảng | destination_id, destination_portal_id, destination_name cùng dạng chuỗi JSON mảng, cùng thứ tự phần tử, kể cả phần tử null | request.md ## Scope | 2026-11-26 |
| D-DEST-SCOPE | Phạm vi cột mới | destination_portal_id chỉ có trên slv_enr_poi_destination. Không thêm sang gld_srv_poi_info, PostgreSQL, API | request.md ## Scope | 2026-11-26 |
| D-DEST-GOLD | Gold copy | gld_srv_poi_info.destination_id vẫn copy 1-1 từ silver, nên giá trị gold đổi theo strapi_document_id | request.md ## User outcome | 2026-11-26 |
| D-SCHEMA | Schema ai_enriched_poi | Người dùng chọn mục 1. old_address lấy address_line_2. price_level, price_min, price_max lấy cột cùng tên. story lấy story. local_tips lấy local_tips_or_neighborhood. Khớp (poi_id, lang). Gold giữ INT và DECIMAL(18,2); nguồn giá là int. | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-INIT-KEY | Khóa init | ai_enriched_poi.poi_id = gld_poi_legacy_id_map.legacy_poi_id, và ai_enriched_poi.lang phải bằng map.lang. Lệch lang thì RUN dừng. | architecture.md ## 2; evidence/results/p_gaps.txt P-AI-1 | 2026-11-26 |
| D-INIT-INFO-VI | Bốn cột info | Bốn cột gld_srv_poi_info lấy từ dòng ai_enriched_poi lang vi mà vi_key đã chọn. | architecture.md ## 2 và ## 6 | 2026-11-26 |
| D-INIT-ENRICH-ONLY | Không tạo dòng mới | Sáu cột chỉ điền dòng init đã dựng. Thiếu nguồn thì NULL. Không tạo dòng gold chỉ từ ai_enriched_poi. | architecture.md ## 2 | 2026-11-26 |
| D-DEST-BACKFILL | Backfill silver | B. Backfill tại chỗ từ event bronze đã sinh dòng silver. Hai dòng không có phần tử strapi_document_id ghi mảng rỗng. | decision.md ## Câu hỏi đang mở, D-DEST-BACKFILL mục 1 | 2026-11-26 |
| D-LEGACY-DEST | destination_id init | Giữ mapping destination_id của init legacy. destination_id của phần INIT đã đúng, không cần thay đổi hay chạy lại. Ghi chú ở mapping_legacy_gold_to_gld_srv.md tại dòng destination_id của init: giá trị LEGACY_INIT đứng ngoài id portal, và 1/24 giá trị trùng strapi. | Người dùng, 2026-11-26 | 2026-11-26 |
| D-G4 | Scope thêm | Thêm tests/test_enr_extract_contract.py, tests/test_legacy_gold_poi_init_contract.py và docs/context/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md vào scope.files. | decision.md ## Câu hỏi đang mở, G4 mục 2 | 2026-11-26 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 42446 bytes

## FILES

- architecture.md | 42446 bytes | large: use toc/show
- decision.md | 8909 bytes
- evidence/plan.md | 2218 bytes
- evidence/probes/ai_enriched_poi_schema.py | 3952 bytes
- evidence/probes/p_gaps.py | 6187 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/ai_enriched_poi_schema.txt | 2971 bytes
- evidence/results/p_gaps.txt | 970 bytes
- handoffs/architect.md | 31365 bytes | large: use toc/show
- handoffs/author-input.md | 3076 bytes
- model-design.md | 15879 bytes
- request.md | 4989 bytes
- resume.md | 670 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1945 bytes

## NEXT

python scripts/vv.py run-gate 20261126-legacy-init-enriched-cols-and-dest-portal

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb (53840 bytes)

[0] markdown id=lgpmd json=3-14 lines=5 | NB_SETUP_LEGACY_GOLD_POI | defs: none
[1] code id=lgpparams json=15-31 lines=3 | p_mode = "PLAN" | defs: none
[2] code id=lgplib json=32-46 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=lgpconst json=47-76 lines=16 | import re | defs: none
[4] code id=lgphours json=77-189 lines=99 | import json | defs: _int, _open, _closed, _all_day, _dump, google_hours, partner_hours, operating_hours
[5] code id=lgppure json=190-330 lines=127 | ORIGIN = "LEGACY_INIT" | defs: legacy_source_name, new_poi_id, insert_only_sql, single_payload, legacy_upsert_sql, legacy_hours, amenity_enum_values, add, walk, destination_ids_shape
[6] code id=lgpmain json=331-892 lines=548 | import inspect | defs: _workspace_name, _history_version, old, present_counts, to_target, _metrics, _commit_lookup, write_insert_only, _j

### notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb (60412 bytes)

[0] markdown id=enr00 json=3-10 lines=14 | NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV | defs: none
[1] code id=enr01 json=11-28 lines=16 | pl_name                 = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"   # @pipeline | defs: none
[2] code id=enr02 json=29-43 lines=1 | %run NB_LIB_EXTRACT_RAWDATA | defs: none
[3] markdown id=enr03 json=44-61 lines=11 | Hằng số nguồn `cms_raw_data` | defs: none
[4] code id=enr04 json=62-76 lines=32 | import uuid | defs: none
[5] markdown id=enr05 json=77-107 lines=24 | A. Đọc raw, phân loại và dựng tài liệu | defs: none
[6] code id=enr06 json=108-122 lines=261 | def event_is_newer(candidate, applied): | defs: event_is_newer, path_value, block_col, doc_value, spec_paths, is_scoped, top_fields, doc_columns, read_raw, classify_docs, blank, presence, bad_shape, profile_docs, reject_frame, doc_source_payload, doc_reject_rows
[7] markdown id=enr07 json=123-154 lines=25 | B. Xử lý 1 bảng: tách dòng → chuyển kiểu, khoá → lọc theo state → bản mới nhất → | defs: none
[8] code id=enr08 json=155-169 lines=355 | def expand_rows(spec: TableSpec, docs: DataFrame) -> DataFrame: | defs: expand_rows, part_value, build_table_rows, typed, table_stats, as_int, resolve_latest, build_merge_sql, merge_into_target, doc_state_latest, element_reject_rows, _run_table, process_table
[9] markdown id=enr09 json=170-181 lines=5 | C. Commit | defs: none
[10] code id=enr10 json=182-207 lines=12 | def commit(classified: DataFrame, profile: Profile, results: list, ctx: RunConte | defs: commit
[11] markdown id=enr11 json=208-219 lines=5 | Main | defs: none
[12] code id=enr12 json=220-237 lines=129 | def build_context() -> RunContext: | defs: build_context, check_config, process_run, run_extract
[13] code id=enr13 json=238-259 lines=8 | _summary_json = json.dumps(RUN_SUMMARY, ensure_ascii=False, default=str) | defs: none
[14] markdown id=enr14 json=260-272 lines=6 | Vận hành | defs: none

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (237583 bytes)

[0] markdown id=init_md json=unknown lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=unknown lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=unknown lines=541 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=unknown lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=unknown lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_cfg_cms json=unknown lines=44 | def _cms_ts(path): | defs: _cms_ts, _cms
[7] code id=init_cfg_enr json=unknown lines=45 | def _enr(path, typ="string", rule=None): | defs: _enr
[8] code id=init_registry_pure json=unknown lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[9] code id=init_seed_ctrl json=unknown lines=111 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[10] code id=init_seed_place_type json=unknown lines=455 | import re | defs: validate_seed
[11] code id=init_seed_amenity json=unknown lines=291 | import re | defs: amenity_keys, amenity_code, amenity_seed_rows, validate_seed
[12] code id=init_plan json=unknown lines=148 | import json | defs: _missing, _dup_keys, _target_dup_keys
[13] code id=init_ddl json=unknown lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[14] code id=init_seed_write json=unknown lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[15] code id=init_verify json=unknown lines=30 | verify_errors = [] | defs: none
[16] code id=init_exit json=unknown lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (433836 bytes)

[0] markdown id=b0b1203a-7c40-48bf-bfc9-7b29d7064bdc json=3-25 lines=6 | NB_CREATE_DDL — 7 bảng control `lh_vv_ctrl.dbo` | defs: none
[1] markdown id=b7e4c1a0-6f28-4d3e-9a15-2c8d0e4f6a91 json=26-36 lines=4 | Ghi chú migration 08/10 | defs: none
[2] markdown id=d20a367e-98da-4b91-9237-dd2b2cebfeae json=37-54 lines=1 | Tạo bảng ctrl_mng_pipeline_config | defs: none
[3] code id=80154b61-ea1a-415b-834c-3c07d689d036 json=55-177 lines=108 | %%sql | defs: none
[4] markdown id=<none> json=178-188 lines=5 | Reset silver (DROP/DELETE) không nằm trong luồng tạo bảng. | defs: none
[5] code id=502cd242 json=189-242 lines=40 | %%sql | defs: none
[6] markdown id=a0c11600-5f15-4ec4-ab3b-cd590b5ce6a8 json=243-260 lines=1 | Tạo bảng ctrl_mng_watermark | defs: none
[7] markdown id=e80b9799-8de0-4319-8c62-be8096d373c8 json=261-288 lines=11 | **[SỬA 03/10] Bỏ cell MERGE watermark từ `lh_vv_bronze.partner.brz_watermark`**  | defs: none
[8] code id=3ea73e14-6a1f-42a5-b960-34123b0a3fc4 json=289-304 lines=51 | %%sql | defs: none
[9] markdown id=ed3d2dc0-d9f4-4cd7-b5aa-5e65afb7aca0 json=305-322 lines=1 | Tạo bảng ctrl_cfg_schema_registry | defs: none
[10] code id=d06c9671-6b88-4afa-97a8-d028f6b9e936 json=323-366 lines=30 | CONFIG_TABLE = "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry" | defs: none
[11] code id=28e2be98-7f9a-41d5-b7f8-b4d4a5baf5ff json=367-915 lines=535 | TABLE_CONFIGS = [ | defs: none
[12] code id=0f228dc1-7bc8-4ed2-a10f-e6125a806e83 json=916-1116 lines=186 | from pyspark.sql.types import ( | defs: resolve_type, flatten_table_configs, validate_rows, seed_registry, show_registry
[13] markdown id=7517dd85-f292-4361-9d9d-6bad3f2e4f34 json=1117-1137 lines=4 | **[THÊM 03/10 - 3P] Seed registry nguồn 3rd-party `brz_3rd_crawler_poi_stream`** | defs: none
[14] code id=e9c137c5-c9fc-4f8f-a925-bc511cfd71a7 json=1138-1335 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[15] code id=0271d481-4188-43ab-8cb4-03acd3452550 json=1336-1355 lines=5 | seed_registry(TABLE_CONFIGS_3P, "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream" | defs: none
[16] markdown id=5c2996a4-3ddc-4924-8645-c0cc545cdd63 json=1356-1373 lines=1 | Tạo các bảng log & debug | defs: none
[17] code id=7dad05d9-20f0-4ab4-af1e-dec1dfe5d8cb json=1374-1515 lines=127 | %%sql | defs: none
[18] code id=ea524452-c135-4ef4-b4a8-3a076fa67ee7 json=1516-1551 lines=22 | GOLD_LOG_COLUMNS = ( | defs: none
[19] markdown id=de14c4c2-7925-4582-b080-8b0a660fb99c json=1552-1569 lines=1 | Kiểm tra cấu hình | defs: none
[20] code id=6e95fc60-2ef9-47af-a250-95844179c188 json=1570-1655 lines=71 | %%sql | defs: none
[21] code id=5784a286-d45c-4be8-8223-5a43800b6e2b json=1656-1690 lines=17 | %%sql | defs: none
[22] markdown id=enrddlmd json=1691-1700 lines=3 | [THÊM 13/10] Gold enr và cạnh PL_VV_TRANS_SLV_TO_ENR_15P | defs: none
[23] code id=enrddlpy json=1701-1844 lines=130 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _ddl, _expected_type
[24] markdown id=nonenrmd json=1845-1857 lines=1 | [THÊM 19/10] 20261019-poi-entity-non-enrich | defs: none
[25] code id=nonenrpy json=1858-1935 lines=64 | import re | defs: category_group, with_category_group
[26] markdown id=dictseedmd json=1936-1943 lines=1 | [THÊM 20/10] 20261020-dictionary-seed-from-mapping | defs: none
[27] code id=dictseedpy json=1944-1994 lines=37 | AM_FQ = "lh_vv_silver.dbo.ref_dictionary_amenities" | defs: none
[28] markdown id=entwebmd json=1995-2002 lines=1 | [THÊM 20/10] 20261020-entity-drop-op-cols-add-website | defs: none
[29] code id=entwebpy json=2003-2118 lines=102 | CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: lock_is_free
[30] markdown id=amenpnmd json=2119-2132 lines=7 | [THÊM 18/11] 20261118-amenity-poi-id-align | defs: none
[31] code id=amenpnpy json=2133-2281 lines=140 | import uuid | defs: _refresh_lock, _edges
[32] markdown id=enrinfomd json=2282-2289 lines=1 | [THÊM 21/10] 20261021-refresh-gld-enr-poi-info | defs: none
[33] code id=enrinfopy json=2290-2516 lines=213 | import uuid | defs: _schema, _create
[34] markdown id=mvpoimd json=2517-2524 lines=1 | [THÊM 21/10] 20261021-move-poi-nodes-enr-15p-cleanup | defs: none
[35] code id=mvpoipy json=2525-2758 lines=220 | import uuid | defs: _names, _n, _node_edges, _info_edges
[36] markdown id=enrflagmd json=2759-2766 lines=1 | [THÊM 22/10] 20261022-enr-landing-and-gld-flags | defs: none
[37] code id=enrflagpy json=2767-3033 lines=253 | import uuid | defs: _want, _schema, _create_sql, _missing_flags, _add_flags, _edge_rows
[38] markdown id=ohpassmd json=3034-3041 lines=1 | [THÊM 23/10] 20261023-entity-opening-hours-passthrough | defs: none
[39] code id=ohpasspy json=3042-3245 lines=190 | import uuid | defs: _rows, _active, _refresh_lock, _column
[40] markdown id=peholmd json=3246-3253 lines=1 | [THÊM 23/10] 20261023-entity-phone-email-holiday | defs: none
[41] code id=peholpy json=3254-3317 lines=50 | ENTITY_FQ = "lh_vv_silver.dbo.slv_poi_entity_non_enrich" | defs: _fields, _issues
[42] markdown id=srvpoimd json=3318-3329 lines=5 | [THÊM 24/10] 20261024-gld-srv-poi-from-mapping | defs: none
[43] code id=srvpoipy json=3330-3548 lines=205 | import uuid | defs: _want, _schema, _create_sql, _edge_rows, _refresh_lock
[44] markdown id=srvratemd json=3549-3560 lines=5 | [THÊM 26/10] 20261025-gld-srv-poi-info-rating-review | defs: none
[45] code id=srvratepy json=3561-3741 lines=167 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[46] markdown id=mediaddlmd json=3742-3751 lines=3 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[47] code id=mediaddlpy json=3752-3951 lines=186 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[48] markdown id=amenddlmd json=3952-3963 lines=5 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[49] code id=amenddlpy json=3964-4155 lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[50] markdown id=plcadmd json=4156-4166 lines=4 | [THÊM 26/10] 20261026-pl-name-cadence-suffix | defs: none
[51] code id=plcadpy json=4167-4420 lines=240 | import uuid | defs: _n, _lock_rows, _refresh_lock, _issues
[52] markdown id=mlexpmd json=4421-4429 lines=2 | [THÊM 26/10] 20261026-add-poi-multi-lang-experience | defs: none
[53] code id=mlexppy json=4430-4581 lines=138 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[54] markdown id=srvrevmd json=4582-4591 lines=3 | [THÊM 27/10] 20261026-gld-srv-poi-review | defs: none
[55] code id=srvrevpy json=4592-4800 lines=195 | import uuid | defs: _want, _schema, _edge_rows, _create_sql, _refresh_lock
[56] markdown id=rvi18nenrmd json=4801-4810 lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (1/2) | defs: none
[57] code id=rvi18nenrpy json=4811-4973 lines=149 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[58] markdown id=rvi18ngldmd json=4974-4983 lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (2/2) | defs: none
[59] code id=rvi18ngldpy json=4984-5136 lines=139 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[60] markdown id=mlsrcmd json=5137-5146 lines=3 | [THÊM 04/11] 20261104-gld-srv-multi-lang-i18n-without-enr | defs: none
[61] code id=mlsrcpy json=5147-5265 lines=105 | import uuid | defs: _want, _schema, _refresh_lock
[62] markdown id=cmscfgmd json=5266-5275 lines=3 | [THÊM 08/11] 20261104-extract-cms-raw-data | defs: none
[63] code id=cmscfgpy json=5276-5385 lines=96 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _cms_ts, _cms
[64] markdown id=srvcovermd json=5386-5396 lines=4 | [THÊM 08/11] 20261108-gld-srv-poi-info-cover | defs: none
[65] code id=srvcoverpy json=5397-5588 lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[66] markdown id=poidestmd json=5589-5599 lines=4 | [THÊM 12/11] 20261112-poi-destination-name-api | defs: none
[67] code id=poidestpy json=5600-5765 lines=152 | import uuid | defs: _want, _schema, _accepted, _anchor, _refresh_lock
[68] markdown id=enrmergemd json=5766-5773 lines=1 | [THÊM 12/11] 20261112-enr-poi-append-to-merge | defs: none
[69] code id=enrmergepy json=5774-5950 lines=163 | import uuid | defs: _release_lock, _refresh_lock, _types, _modes, _run
[70] markdown id=srvactivemd json=5951-5961 lines=4 | [THÊM 16/11] 20261116-srv-poi-info-is-active | defs: none
[71] code id=srvactivepy json=5962-6089 lines=114 | import uuid | defs: _want, _schema, _refresh_lock
[72] markdown id=enrbrzcfgmd json=6090-6101 lines=5 | B3 — cell `enrbrzcfgpy` | defs: none
[73] code id=enrbrzcfgpy json=6102-6116 lines=96 | def _enr(path, typ="string", rule=None): | defs: _enr
[74] markdown id=enrbrzmd json=6117-6128 lines=5 | B2 — cell `enrbrzpy` | defs: none
[75] code id=enrbrzpy json=6129-6143 lines=269 | def plan_rewrite(current, target, renames, drops): | defs: plan_rewrite, should_auto_restore, _touch_locks, _head, _fence, _confirm_skip, rewrite_table, _norm, _take
[76] markdown id=enrgldmd json=6144-6155 lines=5 | B5 — cell `enrgldpy` | defs: none
[77] code id=enrgldpy json=6156-6170 lines=257 | def plan_rewrite(current, target, renames, drops): | defs: plan_rewrite, should_auto_restore, _touch_locks, _head, _fence, _confirm_skip, rewrite_table, _norm
[78] markdown id=legacyidmd json=6171-6185 lines=3 | [THÊM 19/11] 20261119-legacy-gold-poi-init | defs: none
[79] code id=legacyidpy json=6186-6321 lines=122 | import uuid | defs: _want, _schema, _exists, _refresh_lock
[80] markdown id=lgpnamemd json=6322-6329 lines=1 | [THÊM 25/11] 20261125-legacy-init-destination-and-poi-name — thêm `poi_name` STR | defs: none
[81] code id=lgpnamepy json=6330-6435 lines=97 | import uuid | defs: _fields, _exists, _refresh_lock
[82] markdown id=oldpricemd json=6436-6446 lines=4 | [THÊM 26/11] 20261126-gld-srv-old-address-price-story | defs: none
[83] code id=oldpricepy json=6447-6681 lines=221 | import uuid | defs: _want, _fields, _names, _edge_rows, _refresh_lock

### docs/context/mapping_gld_srv_poi_info.md (21992 bytes)

# Mapping GLD Service POI | L3-L350
## 1. Table: `gld_srv_poi_info` | L5-L350
### 1.1. Xử lý | L9-L30
### 1.6 Grain và địa chỉ đã chốt — 20261116-enr-lang-destination-from-bronze | L31-L40
### 1.2. Field Mapping | L41-L85
### 1.3. Operating Hours Transform | L86-L134
### 1.4. Operating Hours Examples | L135-L324
#### Case 1 | L137-L261
#### Case 2 | L262-L324
### 1.5. Operating Hours Transform — partner | L325-L350
