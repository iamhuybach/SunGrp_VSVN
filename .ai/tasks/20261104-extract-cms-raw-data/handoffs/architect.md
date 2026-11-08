# Architect handoff: 20261104-extract-cms-raw-data

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261104-extract-cms-raw-data --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261104-extract-cms-raw-data/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261104-extract-cms-raw-data | phase=triage

## STATE

id: 20261104-extract-cms-raw-data
title: Extract cms_raw_data with existing load modes
status/owner: waiting_architecture/architect
complexity/risk: low/low
required: architecture_required=True, evidence_required=True, runtime_required=False
signals: data_model_change
gates: evidence=evidence_required, architecture=pending, local_verification=pending, specialist_review=not_required, risk_gate=not_required, runtime=not_required
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: none
open findings: none
exceptions: none
scope.files:
- notebooks/NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- tests/test_cms_l1_contract.py
- tests/test_initial_ddl_contract.py
- docs/context/NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.md
- docs/context/CTRL_TABLES_CONTEXT.md

## VALIDATION

PASS

## RESUME

# Resume

Status: waiting_architecture

Done this session: D-18 approved one more architecture round. `rounds.architecture` was set to 1. Status moved `user_decision` → `triage` → `waiting_architecture`. `run-gate` stopped after 5 seconds because the Claude CLI login expired. The round was not counted.

Next action: After the user signs in again, run `python scripts/vv.py run-gate 20261104-extract-cms-raw-data`. Do not reset the round. Do not implement.

Read next: `.ai/tasks/20261104-extract-cms-raw-data/architecture.md` — `### PASS criteria for the next round`; `model-design.md` — `## Conflicts and questions`

Waiting on: a successful Architect run. The user must renew the Claude CLI login first.

## REQUEST

# Request

## User outcome

A solution proposal for extracting `lh_vv_bronze.dbo.cms_raw_data` by reusing an existing load mode. This phase does not change runtime behavior.

## Scope

### In scope

- Problem analysis and a solution proposal for a new per-source extract notebook and registry rows that use only the current load modes.
- A key tree of the one sample row, with no values and no URLs.

### Out of scope

- Adding a value to `LOAD_MODES`.
- Changing the mode signature in `NB_LIB_EXTRACT_RAWDATA` when `DOC` or `DOC_ARRAY` is enough.
- Attaching `cms_raw_data` to the `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` activity that runs `partner_raw_data`.
- Interpreting the parenthetical names in D-05, or inventing grain, kept columns, or a `json_path`.
- A `json_path` for a key that was not seen.
- A POI table designed from `pois[]`, whose sample element is empty.
- Architecture and specialist review for this proposal-only phase.

## Acceptance criteria

- `problem-analysis.md` and `proposal.md` exist and were written by `run-author`.
- The proposal chooses only among `CDC`, `DOC`, and `DOC_ARRAY`.
- The proposal lists which payload blocks are `DOC` and which are `DOC_ARRAY`, then stops for the user to lock target tables.
- `evidence/payload-shape.md` records the sample key tree. Unseen columns and keys are `MISSING_EVIDENCE`.

## Constraints

- `LOAD_MODES` is only `CDC`, `DOC`, `DOC_ARRAY`. The proposal must choose one of these three. Do not add a new value.
- The sample row has no `before`, `after`, `op`, `source.schema`, or `source.table`. Do not assign `CDC` until a real Debezium event exists.
- The envelope is close to `brz_3rd_crawler_poi_stream` but has no `source_id`, `normalized_payload`, or `language_code`, and it adds a `type` column. Do not treat `type` as `language_code` or as an entity type from one value.
- `NB_EXTRACT_<SOURCE>_CDC_BRZ_TO_SLV` is the per-source notebook name, not a new load mode.
- `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` runs only `partner_raw_data`. Do not attach `cms_raw_data` to that activity.
- On 2026-11-05 the user said invalid records are written to `ctrl_cdc_reject` the same way as the partner flow. `notebooks_lgc/cms_transform/nb_cms_transformation.ipynb` is a business reference from the old model, not the code or table-structure standard. Extract targets are `slv_cms_blog`, `slv_cms_destination`, `slv_cms_news`, and `slv_cms_promotion_article`. The MERGE key of each table is `document_id` together with `locale`. Gold is out of scope.
- One row is not a schema contract. Do not write URLs, signatures, proper names, or description text into an artifact.

## Classification rationale

- Complexity: `low`. No runtime behavior has changed. The accepted names and key are recorded; model design waits on the remaining choices.
- Risk: `low`. No runtime behavior changes.
- Architecture: required before implementation, because the task now names four target tables and key `id`. Gate stays `pending`. Do not call the Architect until `model-design.md` exists and the open choices are closed.
- Evidence: required. One row does not establish the payload shape of the four `source_name` values. Probe `evidence/probes/cms-source-sample.sql` is read-only and has not been run.
- Runtime proof: not required. Nothing is deployed or executed.
- Reviewer routing: none until implementation. This phase still does not change behavior.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | load_mode | `load_mode` của mọi dòng `cms_raw_data` chỉ nhận `DOC` hoặc `DOC_ARRAY`. Không dùng `CDC` khi chưa có event Debezium thật. Không thêm giá trị vào `LOAD_MODES`. | proposal.md ## Ràng buộc cho Architect, mục 1 | 2026-11-04 |
| D-02 | Chữ ký mode | Không sửa chữ ký mode trong `NB_LIB_EXTRACT_RAWDATA`. Notebook mới gọi `load_table_specs` với `SNAPSHOT_MODES`. | proposal.md ## Ràng buộc cho Architect, mục 2 | 2026-11-04 |
| D-03 | Pipeline | Không gắn `cms_raw_data` vào activity của `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`. | proposal.md ## Ràng buộc cho Architect, mục 4 | 2026-11-04 |
| D-04 | Khối chưa thấy | Không thiết kế bảng từ `pois[]`. Không đặt `json_path` cho khóa con `cover_gallery[].formats.*` vì chưa có bằng chứng. | proposal.md ## Ràng buộc cho Architect, mục 7 | 2026-11-04 |
| D-05 | Bảng đích | Chấp nhận phương án C. Có 4 bảng: cms_blog (strapi_blog), cms_destination (strapi_destination), cms_news (strapi_news), cms_promotion_article (strapi_ph_promotion_article). Trong ngoặc là giá trị của source_name và tên ngoài ngoặc thêm tiền tố slv_ là tên bảng mong muốn. raw_payload chính là cột cần extract. Dùng document_id cùng locale như nb cũ. | decision.md ## Quyết định của người dùng | 2026-11-05 |
| D-06 | Kiểu bronze và số dòng | Statement 1: `event_id`, `source_name`, `type`, `crawled_at`, `ingested_date`, and `raw_payload` are `string`. Statement 2: `strapi_blog` 91207, `strapi_destination` 93820, `strapi_news` 236, `strapi_ph_promotion_article` 8160. Statement 3 failed with `DATATYPE_MISMATCH.NON_FOLDABLE_INPUT` because `schema_of_json` requires a foldable `STRING`. Statement 4 was not stored. | evidence/results/cms-source-sample.md ## Recorded result | 2026-11-05 |
| D-07 | Khóa đã parse | `strapi_blog`: 50 rows, 50 `PARSE_FAIL`, no key set. `strapi_destination`: 50 rows, 46 `PARSE_FAIL`, 4 rows with one key set. `strapi_news`: 50 rows, 13 `PARSE_FAIL`, 37 rows with one key set. `strapi_ph_promotion_article`: 50 rows, 0 `PARSE_FAIL`, 50 rows with one key set. Listed `PARSE_FAIL` columns are between 6546 and 7999. | evidence/results/cms-payload-keys.md ## Recorded result | 2026-11-05 |
| D-08 | Độ dài 50 dòng | On 50 rows, closed-object counts equal parsed-row counts: `strapi_blog` CLOSED 0 MAX 7988, `strapi_destination` CLOSED 4 MAX 8000, `strapi_news` CLOSED 37 MAX 14575, `strapi_ph_promotion_article` CLOSED 50 MAX 6805. News shows a `raw_payload` longer than 8000 characters. | evidence/results/cms-payload-length.md ## Recorded result | 2026-11-05 |
| D-09 | Tỷ lệ chuỗi đóng | Full table: `strapi_blog` 91207 rows, 0 null, 79766 closed, 11441 open, min_len 490, max_len 62361. `strapi_destination` 93820 rows, 0 null, 37174 closed, 56646 open, min_len 2724, max_len 107130. `strapi_news` 236 rows, 0 null, 223 closed, 13 open, min_len 4861, max_len 18033. `strapi_ph_promotion_article` 8160 rows, 0 null, 8023 closed, 137 open, min_len 638, max_len 7501. | evidence/results/cms-payload-close-rate.md ## Recorded result | 2026-11-05 |
| D-10 | Reject và phạm vi extract | Những bản ghi lỗi sẽ xử lý giống luồng partner: ghi ra ctrl_cdc_reject. Tham khảo notebook notebooks_lgc/cms_transform/nb_cms_transformation.ipynb để lấy nghiệp vụ; code đó là model cũ, không phải code chuẩn. Format code và cấu trúc bảng theo model và rule hiện tại. Extract ra 4 bảng silver: slv_cms_blog, slv_cms_destination, slv_cms_news, slv_cms_promotion_article. Không cần xử lý ra gold. | decision.md ## Quyết định reject và phạm vi | 2026-11-05 |
| D-11 | Payload hở | Open lengths: `strapi_blog` 11441 in 1000–7999. `strapi_destination` 39004 in 1000–7999 and 17642 at length 8000. `strapi_news` 10 in 1000–7999 and 3 at length 8000. `strapi_ph_promotion_article` 137 at length 7501. `EVENT_BOTH` returned no rows. Regex key pairs: blog 169 (152 with a closed event, 17 with none, 17 latest open), destination 236 (99, 137, 138), news 16 (16, 0, 1), promotion 59 (59, 0, 0). Rows missing `documentId` or `locale`: blog 5110, destination 0, news 2, promotion 0. | evidence/results/cms-open-payload-cause.md ## Recorded result | 2026-11-06 |
| D-12 | Định dạng thời gian | On closed rows, `createdAt`, `updatedAt`, and `publishedAt` match ISO-with-Z: blog 79765, 79765, and 79764; destination 37174; news 223; promotion 8023. Blog `first_publish_date` matches `yyyy-MM-dd` on 79756 rows. The four promotion datetimes match ISO-with-Z on 8023 rows. `crawled_at` matches ISO-with-Z on every row and `try_cast` null count is 0. Closed `locale` values are `vi`, `en`, and `ko`, plus 9 blank blog rows. `ORDER` failed with `DATATYPE_MISMATCH.BINARY_OP_DIFF_TYPES`. | evidence/results/cms-format-census.md ## Recorded result | 2026-11-06 |
| D-13 | Khóa trên dòng đóng | Blog: 40 of 50 parsed, 10 failed, one key set. Destination: 50 parsed, one key set, and `rank`, `tags`, `hooks`, `sections` absent. News: 50 parsed, one key set; `SEO` is null on 42 and object on 8; `news_category` is null on 20 and object on 30. Promotion: 50 parsed, one key set. | evidence/results/cms-closed-key-census.md ## Recorded result | 2026-11-06 |
| D-14 | Thứ tự event | `keys_with_crawled_at_tie` is 0 for every source. `keys_updated_order_ne_crawled_order`: `strapi_blog` 146, `strapi_destination` 99, `strapi_news` 12, `strapi_ph_promotion_article` 27. | evidence/results/cms-event-order.md ## Recorded result | 2026-11-06 |
| D-15 | U1–U4 | U1 Chấp nhận ghi chúng vào ctrl_cdc_reject. U2 tên notebook NB_EXTRACT_CMS_CDC_BRZ_TO_SLV và pl_name PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00, không gắn activity partner. U3 Chấp nhận. U4 Chấp nhận nhưng local null vẫn lấy. | decision.md ## Quyết định U1 đến U4 | 2026-11-06 |
| D-16 | Vòng architecture | Cho phép thêm một vòng architecture. | decision.md ## Quyết định vòng architecture | 2026-11-06 |
| D-17 | U5 | Không còn khóa luồng. Hãy tiếp tục chạy theo workflow. | decision.md ## Quyết định U5 | 2026-11-07 |
| D-18 | Vòng architecture | Cho phép. Main đưa rounds.architecture về 1 và chạy python scripts/vv.py run-gate 20261104-extract-cms-raw-data. | decision.md ## Quyết định vòng architecture tiếp theo | 2026-11-08 |
| D-19 | Vòng architecture | Đã hoàn tất đăng nhập lại Claude Code/Claude CLI. Cho phép thêm một vòng architecture. | decision.md ## Quyết định sau khi đăng nhập lại | 2026-11-08 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 30604 bytes

## FILES

- architecture.md | 30604 bytes | large: use toc/show
- decision.md | 16224 bytes
- evidence/payload-shape.md | 4099 bytes
- evidence/plan.md | 3338 bytes
- evidence/probes/cms-closed-key-census.py | 3029 bytes
- evidence/probes/cms-event-order.py | 2368 bytes
- evidence/probes/cms-format-census.py | 4860 bytes
- evidence/probes/cms-open-payload-cause.py | 4250 bytes
- evidence/probes/cms-payload-close-rate.sql | 1350 bytes
- evidence/probes/cms-payload-keys.py | 2363 bytes
- evidence/probes/cms-payload-length.py | 1748 bytes
- evidence/probes/cms-source-sample.sql | 2368 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/cms-closed-key-census.md | 1672 bytes
- evidence/results/cms-event-order.md | 305 bytes
- evidence/results/cms-format-census.md | 1164 bytes
- evidence/results/cms-open-payload-cause.md | 1742 bytes
- evidence/results/cms-payload-close-rate.md | 823 bytes
- evidence/results/cms-payload-keys.md | 2484 bytes
- evidence/results/cms-payload-length.md | 932 bytes
- evidence/results/cms-source-sample.md | 2861 bytes
- handoffs/architect.md | 28352 bytes | large: use toc/show
- handoffs/author-input.md | 1680 bytes
- model-design.md | 17907 bytes
- problem-analysis.md | 16064 bytes
- proposal.md | 11786 bytes
- request.md | 3458 bytes
- resume.md | 727 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1553 bytes

## NEXT

python scripts/vv.py run-gate 20261104-extract-cms-raw-data

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (226782 bytes)

[0] markdown id=init_md json=unknown lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=unknown lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=unknown lines=499 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
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

### notebooks/NB_CREATE_DDL.ipynb (313155 bytes)

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
[58] markdown id=mlsrcmd json=unknown lines=3 | [THÊM 04/11] 20261104-gld-srv-multi-lang-i18n-without-enr | defs: none
[59] code id=mlsrcpy json=unknown lines=105 | import uuid | defs: _want, _schema, _refresh_lock

### docs/context/CTRL_TABLES_CONTEXT.md (46825 bytes)

# CTRL_TABLES_CONTEXT — 7 bảng control `lh_vv_ctrl.dbo` | L1-L582
## 1. Tổng quan | L7-L24
## 2. Quan hệ | L25-L48
## 3. `ctrl_mng_pipeline_config` | L49-L151
### DDL | L54-L73
### Cột | L74-L89
### Dữ liệu hiện có | L90-L141
### Thao tác thường gặp | L142-L151
## 4. `ctrl_mng_watermark` | L152-L244
### DDL | L162-L186
### Cột theo loại dòng | L187-L211
### Ghi chú migration — số đo watermark trước 08/10 tại `lh_vv_bronze.ctrl` (dòng 3P cũ `wm_transform_poi_raw_event`) | L212-L220
### Thao tác thường gặp | L221-L244
## 5. `ctrl_cfg_schema_registry` | L245-L334
### DDL | L250-L274
### Luật cấu hình (lib kiểm tra, sai → `ConfigError` trước khi ghi) | L275-L285
### Dữ liệu hiện có (seed `NB_CREATE_DDL`, cấu hình chốt 04/10 chiều) | L286-L334
## 6. `ctrl_log_run` — 1 dòng / lần chạy notebook (khoá `exec_id`) | L335-L405
### DDL | L339-L379
### Cột khác nghĩa giữa extract và NB_00 | L380-L394
### Ghi chú migration — log đã thấy trước 08/10 tại vị trí control cũ | L395-L405
## 7. `ctrl_log_table_run` — 1 dòng / bảng đích (hoặc node) / lần chạy | L406-L461
### DDL | L408-L461
## 8. `ctrl_cdc_state` — 1 dòng / entity / bảng đích (chỉ extract) | L462-L501
### DDL | L466-L501
## 9. `ctrl_cdc_reject` — 1 dòng / event (hoặc phần tử) lỗi (chỉ extract) | L502-L555
### DDL | L504-L555
## 10. Lịch sử thay đổi (tóm tắt) | L556-L572
## 11. Việc còn lại liên quan ctrl | L573-L582
