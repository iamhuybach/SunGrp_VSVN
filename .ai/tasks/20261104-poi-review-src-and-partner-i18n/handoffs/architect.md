# Architect handoff: 20261104-poi-review-src-and-partner-i18n

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261104-poi-review-src-and-partner-i18n --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261104-poi-review-src-and-partner-i18n/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261104-poi-review-src-and-partner-i18n | phase=triage

## STATE

id: 20261104-poi-review-src-and-partner-i18n
title: Inactive enrich review, drop info duration columns, serve 3p reviews, partner from vi i18n
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=False, runtime_required=False
signals: data_model_change, stateful_logic, cross_state_impact, idempotency
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=not_required
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, state-correctness-reviewer, spark-runtime-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_ENR_POI_INFO.ipynb
- notebooks/NB_GLD_SRV_POI_REVIEW.ipynb
- notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb
- docs/context/gld_enr_poi_info_review.md
- docs/context/mapping_gld_srv_poi_review.md
- docs/context/01_DATA_MODEL.md
- docs/context/03_OPERATOR_GUIDE.md
- tests/test_enr_poi_contract.py
- tests/test_gld_srv_poi_contract.py
- tests/test_initial_ddl_contract.py
- tests/test_poi_entity_contract.py

## VALIDATION

PASS

## RESUME

# Resume

Status: user_decision. Architecture not started. Author model not run.

Done this session: Classified high/high with signals data_model_change, stateful_logic, cross_state_impact, idempotency. Wrote request.md, decision D-SRV-LANG, and handoffs/author-input.md. Confirmed slv_3p_poi_review registry columns are review_id, poi_id, author_name, rating, text, time, published_at. No notebooks/ trg_tbl writes slv_enr_poi_review_multi_lang.

Next action: After the user names the source of gld_srv_poi_review.title and review_text, overwrite handoffs/author-input.md with that sentence, then run `python scripts/vv.py run-author 20261104-poi-review-src-and-partner-i18n --kind model`. On success, transition to waiting_architecture and run `python scripts/vv.py run-gate 20261104-poi-review-src-and-partner-i18n`. Do not map title or review_text onto text or any other slv_3p_poi_review column.

Read next: `.ai/tasks/20261104-poi-review-src-and-partner-i18n/request.md` section `### Blocker`; `decision.md` `## Quyết định hiện hành`.

Waiting on: User source for title and review_text. Options stay in the closeout.

## REQUEST

# Request

## User outcome

Partner POI rows in `slv_poi_entity_non_enrich` start from a live Vietnamese `slv_pn_business_service_i18ns` row. Serving reviews in `gld_srv_poi_review` are read from third-party `slv_3p_poi_review`, not from `slv_enr_poi_review_multi_lang`. The enrich-review flow is inactive. `time_to_spend`, `best_time`, and `cost_vnd` leave `gld_enr_poi_info`. `cost` stays. User confirmed 2026-11-04.

## Scope

### In scope

- Ctrl edges whose target is `gld_enr_poi_review`: set `is_active = 0` in both `notebooks/NB_SETUP_INITIAL_DDL.ipynb` and `notebooks/NB_CREATE_DDL.ipynb`. Tuple order in setup is `(pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, align_path, dedup_order, nb_name)`. Known edges: `slv_3p_poi_review` and `slv_enr_poi_review_multi_lang` to `lh_vv_gold.enr.gld_enr_poi_review`, `APPEND`, `NB_ENR_POI_REVIEW`, pipeline `PL_VV_TRANS_SLV_TO_ENR_15M`. No DROP. No data delete.
- `gld_enr_poi_info`: remove `time_to_spend`, `best_time`, and `cost_vnd` from DDL, select, and the transform that builds them. Keep `cost`. Notebook `NB_ENR_POI_INFO` cell `id:36415d3b` (`_time_to_spend_text`, `_best_time_text`, `_cost_vnd`). Contract `docs/context/gld_enr_poi_info_review.md`.
- `gld_srv_poi_review`: drop `lang`. Read review rows from `slv_3p_poi_review`. Do not read `slv_enr_poi_review_multi_lang`. Keep the `slv_3p_poi_rating` join for `rating_overall` and `rating_count`. Notebook `NB_GLD_SRV_POI_REVIEW` cell `id:srvrvbuild`. Mapping `docs/context/mapping_gld_srv_poi_review.md`.
- `slv_enr_poi_review_multi_lang`: do not DROP. No notebook under `notebooks/` sets `trg_tbl` to this table. Current in-scope readers are `NB_ENR_POI_REVIEW` (flag input) and `NB_GLD_SRV_POI_REVIEW` (driving input). Inactivate a producer only when no active consumer remains outside the flow inactivated above. There is no in-repo producer edge to inactivate.
- `slv_poi_entity_non_enrich`, partner branch only (`source_name = partner`), in `NB_SLV_POI_ENTITY_NON_ENRICH` cell `id:b1entitybuild` def `_partner`. Google branch unchanged. This branch does not read `slv_3p_poi`, address, contact, or opening hours.
- Docs that state the changed grain or the enrich-review flow: `docs/context/gld_enr_poi_info_review.md`, `docs/context/mapping_gld_srv_poi_review.md`, `docs/context/01_DATA_MODEL.md` (N6 and partner `poi_id`), `docs/context/03_OPERATOR_GUIDE.md` §2.1 and §2.2. Mapping and the enrich contract must be updated before review.
- Contract tests that encode the current columns, edges, or partner join, once implementation starts: `tests/test_enr_poi_contract.py`, `tests/test_gld_srv_poi_contract.py`, `tests/test_initial_ddl_contract.py`, `tests/test_poi_entity_contract.py`.

### Out of scope

- Editing `sql/postgres/gld_srv_serve.pg.sql` in triage. Name it only as impact. Ledger `20261029-pg-ddl-gld-srv-serve` D-LANG: PostgreSQL `apps.srv_poi_review` has no `lang`; that ledger kept gold `lang`. This task drops gold `lang`.
- DROP of `gld_enr_poi_review`, `slv_enr_poi_review_multi_lang`, or any other table. No data delete.
- Google branch of `NB_SLV_POI_ENTITY_NON_ENRICH`.
- Pipeline JSON. `NB_LIB_*` unless a later architecture brief names a library change.
- Mapping `title` or `review_text` onto another `slv_3p_poi_review` column. See the blocker below.

## Acceptance criteria

- Every ctrl edge to `gld_enr_poi_review` has `is_active = 0` in both DDL notebooks.
- `gld_enr_poi_info` has no `time_to_spend`, `best_time`, or `cost_vnd` in DDL, select, or mapping. `cost` remains.
- `gld_srv_poi_review` has no `lang` and does not read `slv_enr_poi_review_multi_lang`.
- Partner branch of `NB_SLV_POI_ENTITY_NON_ENRICH` uses the join direction and coalesce below. Google branch unchanged.
- `docs/context/mapping_gld_srv_poi_review.md` and `docs/context/gld_enr_poi_info_review.md` are updated before review.

## Constraints

Partner branch after the change:

- Driving table: live `slv_pn_business_service_i18ns` (`deleted` null or false) and `locale = 'vi'`.
- Left join live `slv_pn_business_services` on `i18n.business_service_id = svc.id`. A deleted service, or no service row, makes every service-sourced column NULL. A deleted Vietnamese i18n row emits no row. A service with no Vietnamese i18n row emits no row.
- `name = coalesce(i18n.name, svc.name)`.
- `amentities = coalesce(i18n.amentities, svc.amentities)`. Fallback is the whole JSON value. When the i18n block is not NULL, `main_category`, opening hours, and holidays are read from that block, including when an inner key is absent.
- After `primary_type` is known, the three `ref_dictionary_place_type` lookups stay: left join the partner dictionary on `primary_type`, then the two `category_group` steps. Duplicate partner `place_type` stops the node before the join. More than one category, or more than one group, stops the node.
- `phone`, `email`, `business_sector`, `operation_status`, `address`, and `website_urls` exist only on `slv_pn_business_services`. They are NULL when the live service row does not join.
- The old rule "no remaining row means the whole node stops and does not write" is not part of the new request. Do not keep it. If idempotency requires it, record `USER_DECISION` and stop.

Current partner behavior, for contrast only, must not remain: driving table `slv_pn_business_services` inner join live `slv_pn_business_service_i18ns` on `svc.id = i18n.business_service_id` and `locale = 'vi'`; a service without Vietnamese i18n is dropped; if no live service has a Vietnamese row, the node stops and does not write; `primary_type` comes from the service `amentities` JSON; left join `ref_dictionary_place_type` with `is_active = true`, `lower(trim(source_name)) = 'partner'`, and `place_type` equal to `primary_type`; duplicate partner `place_type` stops before the join; category_group step 1 collects `business_category` across every active source for that `place_type`; step 2 runs only when step 1 yields exactly one `business_category`, against the Google dictionary grouped by `business_category`, set of `category_group` other than `Other`.

`poi_id` partner stays `uuid_format(md5(concat(id, 'partner')))` 8-4-4-4-12. For an i18n-driven row the id input is `business_service_id`, which `docs/context/01_DATA_MODEL.md` §8 already treats as the same value as `slv_pn_business_services.id`.

Columns or keys absent from this request are `MISSING`. Do not invent them.

### Review text source

`slv_3p_poi_review` has no `title` and no `review_text`. Registry columns are `review_id`, `poi_id`, `author_name`, `rating`, `text`, `time`, `published_at`. User 2026-11-04, verbatim:

- slv_3p_poi_review.title gán là null
- gld_srv_poi_review.review_text lấy từ slv_3p_poi_review.text

Do not add a `title` column to `slv_3p_poi_review`. Gold `title` is null. Gold `review_text` is `slv_3p_poi_review.text`. Ledger row D-SRV-TEXT.

## Classification rationale

- Complexity: `high`. Signals `data_model_change`, `stateful_logic`, `cross_state_impact`, `idempotency`. The partner branch changes its driving table. Gold columns and a ctrl active flag change.
- Risk: `high`. Ctrl `is_active` and target-column removal change what a rerun writes. Rollback is the prior DDL seed plus a notebook rerun, not a DROP. Not `critical`: the request forbids DROP and data delete.
- Architecture: required. Grain of the partner entity row changes. `gld_srv_poi_review` changes source and drops `lang`. The enrich-review edges change from active to inactive. `gld_enr_poi_info` drops three columns.
- Evidence: not required for this blocker. Column absence is in the repository registry, not an unknown runtime distribution.
- Runtime proof: not required by the acceptance list. Acceptance is repository DDL, notebook SQL, and the two mapping docs.
- Reviewer routing: `sql-data-reviewer` (joins, DDL, grain, MERGE), `state-correctness-reviewer` (ctrl active flag, idempotent rerun, partner rows that disappear), `spark-runtime-reviewer` (notebook build cells). `fabric-pipeline-reviewer` is not routed: pipeline JSON is unchanged. Risk gate is required because risk is `high`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-SRV-LANG | Cột lang của gold review | Yêu cầu này bỏ lang trên gold. File `sql/postgres/gld_srv_serve.pg.sql` chỉ được nêu trong tác động; chưa sửa ở phase triage. | User 2026-11-04; request.md `## Out of scope` | 2026-11-04 |
| D-SRV-TEXT | title và review_text của gold review | slv_3p_poi_review.title gán là null. gld_srv_poi_review.review_text lấy từ slv_3p_poi_review.text. | User 2026-11-04 | 2026-11-04 |

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
- decision.md | 1778 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/author-input.md | 1590 bytes
- model-design.md | 16532 bytes
- request.md | 8211 bytes
- resume.md | 1142 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1951 bytes

## NEXT

python scripts/vv.py run-gate 20261104-poi-review-src-and-partner-i18n

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (226470 bytes)

[0] markdown id=init_md json=unknown lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=unknown lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=unknown lines=501 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=unknown lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=unknown lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=unknown lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=unknown lines=90 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[8] code id=init_seed_place_type json=unknown lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=unknown lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=unknown lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=unknown lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=unknown lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=unknown lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=unknown lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (287630 bytes)

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
[44] markdown id=mediaddlmd json=unknown lines=3 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[45] code id=mediaddlpy json=unknown lines=186 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[46] markdown id=amenddlmd json=unknown lines=3 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[47] code id=amenddlpy json=unknown lines=177 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[48] markdown id=plcadmd json=unknown lines=4 | [THÊM 26/10] 20261026-pl-name-cadence-suffix | defs: none
[49] code id=plcadpy json=unknown lines=240 | import uuid | defs: _n, _lock_rows, _refresh_lock, _issues
[50] markdown id=mlexpmd json=unknown lines=2 | [THÊM 26/10] 20261026-add-poi-multi-lang-experience | defs: none
[51] code id=mlexppy json=unknown lines=138 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[52] markdown id=srvrevmd json=unknown lines=3 | [THÊM 27/10] 20261026-gld-srv-poi-review | defs: none
[53] code id=srvrevpy json=unknown lines=195 | import uuid | defs: _want, _schema, _edge_rows, _create_sql, _refresh_lock

### notebooks/NB_ENR_POI_INFO.ipynb (21919 bytes)

[0] markdown id=8cef70ac json=47-54 lines=1 | APPEND lh_vv_gold.enr.gld_enr_poi_info từ lh_vv_silver.dbo.slv_poi_entity_non_en | defs: none
[1] code id=6afb4f0e json=55-79 lines=8 | p_exec_id = "" | defs: none
[2] code id=32337f4f json=80-94 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=36415d3b json=95-378 lines=270 | SECTOR_LABELS = { | defs: _keys, _flag_keys, _present, _label, _time_to_spend_text, _best_time_text, _cost, _cost_vnd, _review_json, _service_flag, _vi_i18n, _i18n_keys, _role_keys, _require, build
[4] code id=71915be4 json=379-393 lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[5] code id=33e2a64a json=394-408 lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb (27050 bytes)

[0] markdown id=b1entitymd json=unknown lines=6 | NB_SLV_POI_ENTITY_NON_ENRICH | defs: none
[1] code id=b1entityparam json=unknown lines=8 | p_exec_id = "" | defs: none
[2] code id=b1entityrun json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=b1entityjson json=unknown lines=83 | import json | defs: _first_text, first_child_value, top_level_text
[4] code id=b1entitybuild json=unknown lines=212 | GOOGLE = "google" | defs: _live, _google, pick, _partner, build
[5] code id=b1entityres json=unknown lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=b1entityexit json=unknown lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### docs/context/01_DATA_MODEL.md (35724 bytes)

# 01 — Data Model mới của Visit Vietnam (POI) trên Microsoft Fabric | L1-L404
## 1. Bối cảnh nền tảng | L7-L18
## 2. Nguyên tắc phân tầng (đã chốt) | L19-L35
## 3. Sơ đồ tổng | L36-L75
## 4. Bronze — bảng raw | L76-L253
### Cấu trúc `normalized_payload` | L86-L253
## 5. Silver L1 — extract (đúng cấu trúc nguồn) | L254-L318
### 5.1 Partner `slv_pn_*` (23 bảng, `load_mode = CDC`) | L256-L289
### 5.2 3rd-party `slv_3p_poi_*` (9 bảng trong registry, 9 active, snapshot) | L290-L318
## 6. Silver L2 — tích hợp POI (7 node) | L319-L348
### 6.1 Bảng ref (rule dạng dữ liệu) | L335-L348
## 7. Gold hiện hành (`lh_vv_gold.enr`) | L349-L359
## 8. Định danh | L360-L372
## 9. Model cũ (vẫn chạy song song) và lý do đổi | L373-L382
## 10. Ý nghĩa của model mới | L383-L392
## 11. Hướng sắp tới (chưa làm) | L393-L404

### docs/context/03_OPERATOR_GUIDE.md (51959 bytes)

# Hướng dẫn vận hành nền tảng | L1-L659
## 1. Bảng ctrl | L5-L232
### 1.1 `ctrl_mng_pipeline_config` | L9-L43
### 1.2 `ctrl_mng_watermark` | L44-L75
### 1.3 `ctrl_cfg_schema_registry` | L76-L120
### 1.4 `ctrl_log_run` | L121-L156
### 1.5 `ctrl_log_table_run` | L157-L185
### 1.6 `ctrl_cdc_state` | L186-L202
### 1.7 `ctrl_cdc_reject` | L203-L232
## 2. Data lineage | L233-L346
### 2.1 `gld_enr_poi_info` | L237-L262
### 2.2 `gld_enr_poi_review` | L263-L276
### 2.3 `gld_srv_poi_multi_lang` | L277-L292
### 2.4 `gld_srv_poi_info` | L293-L312
### 2.5 `gld_srv_poi_media_gallery` | L313-L320
### 2.6 `gld_srv_poi_amenity` | L321-L328
### 2.7 `gld_srv_poi_review` | L329-L346
## 3. Thêm một field bronze sang silver | L347-L433
### Step 1. Ghi một dòng vào `ctrl_cfg_schema_registry` | L351-L392
### Step 2. Giá trị phải qua được kiểm tra của extract | L393-L408
### Step 3. Chạy notebook extract để thêm cột vật lý | L409-L422
### Step 4. Nạp dữ liệu cũ của cột mới | L423-L433
## 4. Thêm một bảng bronze sang silver | L434-L542
### Step 1. Ghi một dòng `ctrl_mng_pipeline_config` | L438-L471
### Step 2. Ghi mọi cột, kể cả khoá, vào registry | L472-L475
### Step 3. Watermark chỉ khi đây là raw mới | L476-L507
### Step 4. Kiểm tra trước lần ghi dữ liệu | L508-L511
### Step 5. Chạy extract lần đầu | L512-L530
### Step 6. Tắt bảng | L531-L542
## 5. Tham số notebook | L543-L659
### 5.1 `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` | L547-L571
### 5.2 `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` | L572-L594
### 5.3 `NB_00_ORCHES_SLV_TO_ENR` | L595-L602
### 5.4 `NB_00_ORCHES_SLV_TO_GLD` | L603-L659
