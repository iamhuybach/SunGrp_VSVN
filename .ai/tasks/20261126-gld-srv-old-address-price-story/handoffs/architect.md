# Architect handoff: 20261126-gld-srv-old-address-price-story

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261126-gld-srv-old-address-price-story --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261126-gld-srv-old-address-price-story/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261126-gld-srv-old-address-price-story | phase=triage

## STATE

id: 20261126-gld-srv-old-address-price-story
title: Add gold-only old_address, price, story, and local_tips
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: data_model_change
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: spark-runtime-reviewer, sql-data-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_GLD_SRV_POI_INFO.ipynb
- notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb
- docs/context/mapping_gld_srv_poi_info.md
- docs/context/mapping_gld_srv_poi_multi_lang.md
- tests/test_gld_srv_poi_contract.py
- tests/test_initial_ddl_contract.py
- tests/test_srv_poi_serving_contract.py

## VALIDATION

PASS

## RESUME

# Resume

## Status
waiting_architecture / architect. gates.architecture=pending. rounds.architecture=0. architecture.md is still the placeholder. model-design.md is present.

## Done this session
D-OLD-ADDR is recorded. model-design.md was written by claude-opus-5-5 medium. Two prior run-gate calls did not persist architecture because Git status changed during the read-only run. The user said those extra files stay out of this task.

## Next action
Run `python scripts/vv.py run-gate 20261126-gld-srv-old-address-price-story`. Architect returns the document in the JSON response only. Do not read or write any path outside the scope file list, model-design.md, request.md, and decision.md.

## Read next
- `.ai/tasks/20261126-gld-srv-old-address-price-story/decision.md` — `Quyết định của người dùng`
- `.ai/tasks/20261126-gld-srv-old-address-price-story/model-design.md` — `Columns`

## Waiting on
Architect gate result.

## REQUEST

# Request

## User outcome

Add gold-only columns on `gld_srv_poi_info` (`old_address`, `price_level`, `price_min`, `price_max`) and `gld_srv_poi_multi_lang` (`story`, `local_tips`). Grain and MERGE keys stay as they are. PostgreSQL, Java entities, DTOs, and `docs/context/api-mapping/` do not gain these columns.

`old_address` follows `decision.md` row `D-OLD-ADDR`: keep `house_number`, `street`, and `full_address`; do not invent `old_house_number`, `old_street`, or `old_full_address`.

## Scope

### In scope

- `gld_srv_poi_info`: `old_address`, `price_level`, `price_min`, `price_max`.
- `gld_srv_poi_multi_lang`: `story`, `local_tips`.
- `NB_SETUP_INITIAL_DDL` `TABLE_SPECS`, one new patch cell at the end of `NB_CREATE_DDL`, `OUT_COLS` and build of `NB_GLD_SRV_POI_INFO` and `NB_GLD_SRV_POI_MULTI_LANG`.
- `slv_3p_poi_price` as an input of `NB_GLD_SRV_POI_INFO` and an edge in the `PL_VV_TRANS_SLV_TO_GLD_30M` seed.
- Mapping docs `docs/context/mapping_gld_srv_poi_info.md` and `docs/context/mapping_gld_srv_poi_multi_lang.md`.
- Contract tests, with the six columns as gold-only exceptions in `tests/test_srv_poi_serving_contract.py`.

### Out of scope

- `sql/postgres/gld_srv_serve.pg.sql`, Java entities, DTOs, `docs/context/api-mapping/`.
- `currency`. Extra `source_name` filter on price. Choosing one price row when several share `poi_id`.
- Fallback of `story` or `local_tips` to `slv_enr_poi_info_multi_lang`.
- Inventing `old_house_number`, `old_street`, or `old_full_address`. Using entity `full_address` as `old_address`.
- `notebooks_lgc/`, `docs/poi-serving-api/`, and `services/data-serving-service/` except the serving contract test.
- Fast lane. Commit. Fabric DEV execution by Main.

## Acceptance criteria

- Bốn cột info và hai cột multi_lang có trong `TABLE_SPECS` của `NB_SETUP_INITIAL_DDL`, một cell patch mới ở cuối `NB_CREATE_DDL`, `OUT_COLS` và build của `NB_GLD_SRV_POI_INFO` và `NB_GLD_SRV_POI_MULTI_LANG`.
- `slv_3p_poi_price` thành input của `NB_GLD_SRV_POI_INFO` và có cạnh trong seed `PL_VV_TRANS_SLV_TO_GLD_30M`. `story` và `local_tips` dùng cạnh i18n đang có.
- Kiểu lấy từ nguồn: `old_address`, `story`, `local_tips` là `STRING`; `price_level`, `price_min`, `price_max` giữ kiểu cột `slv_3p_poi_price`.
- PostgreSQL và API không có sáu cột này. `test_gold_and_pg_columns_and_types_match` vẫn khớp mọi cột gold khác; sáu cột này là ngoại lệ gold-only trong `tests/test_srv_poi_serving_contract.py`.
- `docs/context/mapping_gld_srv_poi_info.md` và `docs/context/mapping_gld_srv_poi_multi_lang.md` cập nhật trước review.
- Verify PASS trước review. P0/P1 được xử lý trong cap 2 vòng.

## Constraints

- Signal `data_model_change`. Main không viết `model-design.md`.
- Không bịa cột `old_house_number`, `old_street`, `old_full_address`. Không lấy `full_address` của entity làm `old_address`.
- Không đọc `notebooks_lgc/`, `docs/poi-serving-api/`, `services/data-serving-service/` ngoài test hợp đồng serving.
- Không commit. Không chạy Fabric DEV. Runtime để người dùng chạy theo `runtime-runbook.md`.
- Fast lane không áp dụng.
- Architecture bắt buộc vì thêm cột gold và thêm cạnh `slv_3p_poi_price`. Evidence không bắt buộc cho kiểu và grain đã có trong DDL và data model. Reviewer: `spark-runtime-reviewer` và `sql-data-reviewer`. `fabric-pipeline-reviewer` chỉ khi sửa `pipelines/*.json`.

## Verbatim request

Update bảng gld_srv_poi_info:
- Thêm field old_address: transform như full address nhưng lấy các field có tiền tố old_
- Thêm price_level, price_min, price_max lấy từ slv_3p_poi_price (price_level, price_min, price_max)

Update bảng gld_srv_poi_multi_lang:
- Thêm field story (hiện tại chỉ có của partner): slv_pn_business_service_i18ns.story
- Thêm field local_tips (hiện tại chỉ có của partner): slv_pn_business_service_i18ns.local_tips

2 bảng này không cần sink xuống db serving và api không sử dụng.

Diễn giải đã chốt:
- Grain giữ nguyên: gld_srv_poi_info một dòng poi_id; gld_srv_poi_multi_lang một dòng (poi_id, lang). MERGE giữ khóa hiện tại.
- old_address, price_level, price_min, price_max, story, local_tips chỉ ở gold. Không thêm vào sql/postgres/gld_srv_serve.pg.sql, entity Java, DTO, hay docs/context/api-mapping/.
- price_level, price_min, price_max lấy đúng ba cột slv_3p_poi_price. Không thêm currency. Không có dòng giá thì null. Không lọc thêm source_name. Nhiều dòng cùng poi_id thì dừng, không chọn dòng.
- story và local_tips chỉ từ slv_pn_business_service_i18ns, cùng cách nối partner đang dùng cho bio và usps: poi_id = uuid_md5(business_service_id, 'partner') và lang = locale. P1 partner lấy hai cột đó, không fallback sang slv_enr_poi_info_multi_lang. P1 không phải partner thì null. P2 lấy thẳng từ i18n, không fallback.
- full_address hiện tại, docs/context/mapping_gld_srv_poi_info.md §1.6: có dòng destination thì coalesce ba nhóm, nối bằng ", ". Nhóm 1: house_number + street + formatted_address. Nhóm 2: house_number + street + ward_with_type + city_with_type. Nhóm 3: slv_enr_poi_destination.full_address. Field null, hoặc house_number hay street chỉ còn khoảng trắng sau trim, thì bỏ cả nhóm. Không có dòng destination thì full_address của slv_poi_entity_non_enrich.
- Cột old_* đã có trên slv_enr_poi_destination: old_ward, old_ward_with_type, old_district, old_district_with_type, old_city, old_city_with_type, old_formatted_address. Không có old_house_number, old_street, old_full_address. Entity không có cột old_* cho địa chỉ.

## Classification rationale

- Complexity: medium. Column add plus one new gold input, grain unchanged. More than a two-file fast-lane edit. Fast lane does not apply.
- Risk: medium. Bounded gold behavior change. MERGE keys stay. Rollback is a column drop and notebook revert. Local contract tests prove the column contract; Fabric apply is a separate runtime step.
- Architecture: required. New gold columns and a new `slv_3p_poi_price` → `gld_srv_poi_info` edge. Signal `data_model_change`, so `model-design.md` is required before the Architect.
- Evidence: not required. Types and grain for the named source columns are already in `NB_SETUP_INITIAL_DDL` `TABLE_SPECS` and the data-model docs named in the prompt. `old_address` is a formula choice, not a missing runtime fact.
- Runtime proof: required after implementation. Notebook DDL and recompute must run on Fabric DEV by the user, from `runtime-runbook.md`.
- Reviewer routing: `spark-runtime-reviewer`, `sql-data-reviewer`. `fabric-pipeline-reviewer` only if `pipelines/*.json` changes. The gold edge seed lives in `NB_CREATE_DDL`, so the pipeline reviewer is not required at triage.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-OLD-ADDR | old_address | Lấy house_number, street, full_address chứ không phải old_house_number, old_street, old_full_address | Quyết định của người dùng | 2026-11-26 |

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
- decision.md | 5852 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 27519 bytes | large: use toc/show
- handoffs/author-input.md | 3367 bytes
- model-design.md | 10282 bytes
- request.md | 7009 bytes
- resume.md | 959 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1658 bytes

## NEXT

python scripts/vv.py run-gate 20261126-gld-srv-old-address-price-story

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (228845 bytes)

[0] markdown id=init_md json=3-10 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=11-28 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=29-43 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=44-592 lines=535 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=593-607 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=608-805 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_cfg_cms json=806-863 lines=44 | def _cms_ts(path): | defs: _cms_ts, _cms
[7] code id=init_cfg_enr json=864-878 lines=45 | def _enr(path, typ="string", rule=None): | defs: _enr
[8] code id=init_registry_pure json=879-893 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[9] code id=init_seed_ctrl json=894-1016 lines=109 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[10] code id=init_seed_place_type json=1017-1485 lines=455 | import re | defs: validate_seed
[11] code id=init_seed_amenity json=1486-1790 lines=291 | import re | defs: amenity_keys, amenity_code, amenity_seed_rows, validate_seed
[12] code id=init_plan json=1791-1805 lines=148 | import json | defs: _missing, _dup_keys, _target_dup_keys
[13] code id=init_ddl json=1806-1820 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[14] code id=init_seed_write json=1821-2014 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[15] code id=init_verify json=2015-2029 lines=30 | verify_errors = [] | defs: none
[16] code id=init_exit json=2030-2044 lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (418400 bytes)

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

### notebooks/NB_GLD_SRV_POI_INFO.ipynb (25102 bytes)

[0] markdown id=srvinfomd json=unknown lines=11 | NB_GLD_SRV_POI_INFO | defs: none
[1] code id=srvinfoparam json=unknown lines=8 | p_exec_id = "" | defs: none
[2] code id=srvinforun json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=srvinfohours json=unknown lines=99 | import json | defs: _int, _open, _closed, _all_day, _dump, google_hours, partner_hours, operating_hours
[4] code id=srvinfobuild json=unknown lines=182 | ENT_COLS = ("poi_id", "poi_name", "source_name", "business_sector", "business_ca | defs: _require, _destination, _rating, _reviews, _cover, build, _text_or_null
[5] code id=srvinfores json=unknown lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=srvinfoexit json=unknown lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none
