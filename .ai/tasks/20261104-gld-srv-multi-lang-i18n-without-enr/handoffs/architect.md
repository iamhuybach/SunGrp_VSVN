# Architect handoff: 20261104-gld-srv-multi-lang-i18n-without-enr

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261104-gld-srv-multi-lang-i18n-without-enr --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261104-gld-srv-multi-lang-i18n-without-enr/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261104-gld-srv-multi-lang-i18n-without-enr | phase=triage

## STATE

id: 20261104-gld-srv-multi-lang-i18n-without-enr
title: Partner i18n rows in gld_srv_poi_multi_lang without enrich multi-lang
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=False, runtime_required=False
signals: data_model_change, stateful_logic, idempotency
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=not_required
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, state-correctness-reviewer, spark-runtime-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb
- docs/context/mapping_gld_srv_poi_multi_lang.md
- tests/test_gld_srv_poi_contract.py
- notebooks/NB_ENR_POI_INFO.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- docs/context/gld_enr_poi_info_review.md
- tests/test_enr_poi_contract.py
- tests/test_initial_ddl_contract.py

## VALIDATION

PASS

## RESUME

# Resume

Status: waiting_architecture. `rounds.architecture` is 0. The gate did not write a new `architecture.md`.

Done this session: Recorded D-ML-NOMATCH. `gld_enr_poi_info.source_name` stays `slv_poi_entity_non_enrich.source_name`. The new silver column is DDL only. Refreshed `model-design.md`. `run-gate` failed: Claude exit 1, `api_error` `connection_failed`, after 1352 s. The round counter was not incremented.

Next action: Run `python scripts/vv.py run-gate 20261104-gld-srv-multi-lang-i18n-without-enr` again. Do not implement the old Main brief. The old file still starts with `RESULT: PASS` from the previous design.

Read next: `.ai/tasks/20261104-gld-srv-multi-lang-i18n-without-enr/decision.md` row D-ML-NOMATCH. `model-design.md` `## Scope`.

Waiting on: a retry of the Architect gate.

## REQUEST

# Request

## User outcome

A `slv_pn_business_service_i18ns` row with no matching `slv_enr_poi_info_multi_lang` row still produces a `gld_srv_poi_multi_lang` row. Partner i18n text must not disappear from serving only because the enrich multi-lang row is absent. User supplement 2026-11-04, attached to task `20261104-poi-review-src-and-partner-i18n`. This task does not change that task's ledger rows D-SRV-LANG, D-SRV-TEXT, or D-REINIT, and does not change that task's status, gates, `scope.files`, or `resume.md`.

## Acceptance criteria

- A partner row that has only i18n is present in `gld_srv_poi_multi_lang`, with `description` from `bio` and `experience` from `usps`.
- A row that already has `slv_enr_poi_info_multi_lang`, and every non-partner branch, keep the current rule.
- `docs/context/mapping_gld_srv_poi_multi_lang.md` is updated before review.

## Scope

### In scope

- `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb` cell `id:srvmlbuild`: add the partner i18n row that the current left join drops.
- `docs/context/mapping_gld_srv_poi_multi_lang.md`.
- `tests/test_gld_srv_poi_contract.py` assertions that pin `srvmlbuild`.

### Out of scope

- Any edit to task `20261104-poi-review-src-and-partner-i18n`.
- D-SRV-LANG, D-SRV-TEXT, and D-REINIT.
- New gold columns.
- Changing the transform of a row that already matches `slv_enr_poi_info_multi_lang`, including the `bio` / `usps` fallback.
- Driving the non-partner branch from anything other than `slv_enr_poi_info_multi_lang`.
- `docs/context/03_OPERATOR_GUIDE.md` §2.3. It still says `slv_enr_poi_info_multi_lang` is the driving table. Updating it is a later scope change.
- `NB_CREATE_DDL.ipynb` and `NB_SETUP_INITIAL_DDL.ipynb` keep the three existing ctrl edges. D-ML-WRITER adds the `source_name` column on `slv_enr_poi_info_multi_lang` in both DDL notebooks. No notebook writer.

## Current behavior

From `docs/context/mapping_gld_srv_poi_multi_lang.md` and cell `id:srvmlbuild`:

- The row source is `slv_enr_poi_info_multi_lang` LEFT JOIN `slv_poi_entity_non_enrich` on `poi_id`, then a partner LEFT JOIN to `slv_pn_business_service_i18ns` when `poi_id = uuid_md5(business_service_id, 'partner')` and `lang = locale`.
- `required_inputs` are `multi_lang` and `entity`. `i18n` is not required. All three inputs use `live_only=False`.
- Partner: `description` is `bio`, and when `bio` is null, enrich `description`. `experience` is `usps`, and when `usps` is null, enrich `experience`.
- MERGE grain is `(poi_id, lang)`.
- `docs/context/01_DATA_MODEL.md` §8: partner `poi_id` is `uuid_format(md5(concat(<id>, 'partner')))` 8-4-4-4-12. For `slv_pn_business_service_i18ns`, `<id>` is `business_service_id`. `NB_GLD_SRV_POI_MULTI_LANG` already calls `uuid_md5(business_service_id, lit('partner'))`.
- `docs/context/CTRL_TABLES_CONTEXT.md` §3 lists edges for `PL_VV_TRANS_SLV_TO_ENR_15M` and does not list `PL_VV_TRANS_SLV_TO_GLD_30M`. The mapping §1.1 states the three edges `slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich`, and `slv_pn_business_service_i18ns` into `gld_srv_poi_multi_lang` on `PL_VV_TRANS_SLV_TO_GLD_30M`, `load_mode = RECOMPUTE`, `priority = 1`, `nb_name = NB_GLD_SRV_POI_MULTI_LANG`. §5 records `slv_pn_business_service_i18ns` key `(business_service_id, locale)`.

## Decided

- One `slv_pn_business_service_i18ns` row with no `slv_enr_poi_info_multi_lang` row matching the partner `poi_id` and `lang = locale` still creates a `gld_srv_poi_multi_lang` row.
- The i18n values kept are the gold columns that already come from i18n: `description` from `bio`, `experience` from `usps`. No new gold column.
- `poi_id` of that row is `uuid_md5(business_service_id, 'partner')`. `lang` is `locale`.
- A row that already has multi-lang keeps the current transform, including the `bio` / `usps` fallback.
- The non-partner branch stays driven by `slv_enr_poi_info_multi_lang`.

## User decisions

Decided by the user on 2026-11-04. The verbatim text is in `decision.md`. Use that text. Do not replace it with a paraphrase.

D-ML-SRC, added the same day: add column `source_name` on `slv_enr_poi_info_multi_lang`. An i18n-only row still uses every locale and `source_name` `partner`. D-ML-NOMATCH is later: `gld_enr_poi_info` keeps `slv_poi_entity_non_enrich.source_name`.

## Constraints

Columns or keys absent from this request and from `decision.md` are `MISSING`. Do not invent them. D-ML-WRITER: this task only adds the DDL column on `slv_enr_poi_info_multi_lang`. The external enrich job is not implemented here. Do not add a notebook writer. D-ML-NOMATCH, later than D-ML-SRC and D-ML-GATE: `gld_enr_poi_info` keeps `slv_poi_entity_non_enrich.source_name`. Do not read the new column from `NB_ENR_POI_INFO`.

## Classification rationale

- Complexity: `high`. The MERGE key set gains partner rows the current left join drops, while matched multi-lang rows and the non-partner branch stay. The six UD rows are now set in `decision.md`.
- Risk: `high`. Signals `stateful_logic` and `idempotency`: MERGE will emit rows it does not emit today.
- Architecture: required. The state owner of those new gold keys changes, and the MERGE commit set changes. Grain stays `(poi_id, lang)`. No new column.
- Evidence: not required. The current transform, partner `poi_id` formula, and i18n key `(business_service_id, locale)` are in the repository. The open items are user choices, not unknown data shapes.
- Runtime proof: not required. The acceptance rule is a deterministic notebook change with local contract checks.
- Signals: `data_model_change`, `stateful_logic`, `idempotency`.
- Reviewer routing: `sql-data-reviewer` (MERGE grain, joins, and the new branch), `state-correctness-reviewer` (idempotent MERGE of keys that used to be absent), `spark-runtime-reviewer` (Fabric notebook node). `risk_level=high` routes `risk-gate` after those specialists. No pipeline JSON change, so no `fabric-pipeline-reviewer`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-I18N-ROW | Dòng gold khi không có multi_lang khớp | Một dòng slv_pn_business_service_i18ns không có dòng slv_enr_poi_info_multi_lang khớp theo poi_id partner và lang = locale vẫn tạo dòng gld_srv_poi_multi_lang. | User 2026-11-04; request.md `## Decided` | 2026-11-04 |
| D-I18N-COLS | Cột gold lấy từ i18n | Thông tin i18n được giữ là đúng các cột gold hiện lấy từ i18n: description từ bio, experience từ usps. Không thêm cột gold mới. | User 2026-11-04; request.md `## Decided` | 2026-11-04 |
| D-I18N-KEY | poi_id và lang của dòng chỉ có i18n | poi_id của dòng này là uuid_md5(business_service_id, 'partner'), lang là locale. | User 2026-11-04; request.md `## Decided` | 2026-11-04 |
| D-KEEP | Dòng đã khớp và nhánh không phải partner | Dòng đã có multi_lang giữ transform hiện tại, kể cả fallback bio/usps. Nhánh không phải partner vẫn do slv_enr_poi_info_multi_lang dẫn. | User 2026-11-04; request.md `## Decided` | 2026-11-04 |
| D-REF | Task dẫn chiếu | Không thay các quyết định D-SRV-LANG, D-SRV-TEXT, D-REINIT của task 20261104-poi-review-src-and-partner-i18n. | User 2026-11-04; request.md `## User outcome` | 2026-11-04 |
| UD-SRC | source_name khi không có entity | lấy từ bảng slv_pn_business_service_i18ns nên source_name vẫn là 'partner' | User 2026-11-04 | 2026-11-04 |
| UD-MEASURES | time_to_spend, best_time, cost_vnd khi không có multi_lang | slv_pn_business_service_i18ns có data nhưng time_to_spend, best_time, cost_vnd khi không có multi_lang nhưng slv_enr_poi_info_multi_lang thì time_to_spend, best_time, cost_vnd để null. | User 2026-11-04 | 2026-11-04 |
| UD-LOCALE | Locale nào được phát dòng | Lấy mọi locale vì đây là bảng chứa những thông tin đa ngôn ngữ. | User 2026-11-04 | 2026-11-04 |
| UD-DELETED | Lọc deleted | Giữ như hiện tại | User 2026-11-04 | 2026-11-04 |
| UD-INPUT | Bảng multi_lang vắng mặt | Nếu slv_pn_business_service_i18ns có data (của bio và usps), nhưng slv_enr_poi_info_multi_lang không có poi_id khớp thì vẫn hiển thị nhưng những fields lấy từ slv_enr_poi_info_multi_lang sẽ null | User 2026-11-04 | 2026-11-04 |
| UD-BLANK | Khoá blank | Chốt theo kiến trúc | User 2026-11-04 | 2026-11-04 |
| D-ML-SRC | source_name trên multi_lang và dòng i18n | Tạo thêm 1 cột source_name ở bảng slv_enr_poi_info_multi_lang. Dòng chỉ có i18n vẫn lấy mọi locale và source_name là partner. | User 2026-11-04; câu giữa bị D-ML-NOMATCH thay | 2026-11-04 |
| D-ML-CAP | Thêm một vòng architecture | Đồng ý cho thêm một vòng architecture | User 2026-11-04 | 2026-11-04 |
| D-ML-PICK | source_name theo poi_id | 1 poi_id có thể nhiều lang nhưng đều thuộc 1 source. | User 2026-11-04 | 2026-11-04 |
| D-ML-GATE | Điều kiện google của NB_ENR_POI_INFO | gld_enr_poi_info vẫn lấy slv_poi_entity_non_enrich.source_name | User 2026-11-04; D-ML-NOMATCH thay câu "Dùng source_name mới" | 2026-11-04 |
| D-ML-WRITER | Ai ghi source_name lên multi_lang | Chỉ cần thêm cột DDL. Hiện tại đổ vào bảng đấy là job enrich ngoài và chưa implement | User 2026-11-04 | 2026-11-04 |
| D-ML-NOMATCH | source_name của gld_enr_poi_info | gld_enr_poi_info vẫn lấy slv_poi_entity_non_enrich.source_name | User 2026-11-04 | 2026-11-04 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: PASS
size: 33616 bytes

## FILES

- architecture.md | 33616 bytes | large: use toc/show
- decision.md | 6493 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 25281 bytes | large: use toc/show
- handoffs/author-input.md | 1401 bytes
- model-design.md | 13407 bytes
- request.md | 5980 bytes
- resume.md | 816 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1763 bytes

## NEXT

python scripts/vv.py run-gate 20261104-gld-srv-multi-lang-i18n-without-enr

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_CREATE_DDL.ipynb (301049 bytes)

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
[54] markdown id=rvi18nenrmd json=unknown lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (1/2) | defs: none
[55] code id=rvi18nenrpy json=unknown lines=149 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[56] markdown id=rvi18ngldmd json=unknown lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (2/2) | defs: none
[57] code id=rvi18ngldpy json=unknown lines=139 | import uuid | defs: _want, _schema, _edges, _refresh_lock

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (226617 bytes)

[0] markdown id=init_md json=unknown lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=unknown lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=unknown lines=497 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=unknown lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=unknown lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=unknown lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=unknown lines=93 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[8] code id=init_seed_place_type json=unknown lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=unknown lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=unknown lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=unknown lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=unknown lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=unknown lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=unknown lines=7 | summary = { | defs: none
