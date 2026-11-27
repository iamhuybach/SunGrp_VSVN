# Architect handoff: 20261127-slv-pn-product-business-mapping

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261127-slv-pn-product-business-mapping --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261127-slv-pn-product-business-mapping/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261127-slv-pn-product-business-mapping | phase=triage

## STATE

id: 20261127-slv-pn-product-business-mapping
title: Map legacy partner product business onto current silver L1
status/owner: waiting_architecture/architect
complexity/risk: low/low
required: architecture_required=True, evidence_required=True, runtime_required=False
signals: data_evidence_required, data_model_change
gates: evidence=pass, architecture=pending, local_verification=pending, specialist_review=not_required, risk_gate=not_required, runtime=not_required
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: none
open findings: none
exceptions: none
scope.files:
- docs/context/mapping_slv_pn_product.md
- docs/context/mapping_slv_pn_product_l2.md

## VALIDATION

PASS

## RESUME

# Resume

## Status

`waiting_evidence`. Q-21, Q-22, and Q-23 are recorded. Architecture was not run.

## Done this session

- Recorded decision A for `deleted_at`, `is_bookable`, and `row_hash`. Updated mapping L2 to the same three rules.
- Saved the failed probe as `evidence/results/holiday_product_post_id_type_run1_fail.txt`.
- Probe now sets `spark.sql.legacy.timeParserPolicy=LEGACY` and selects only non-timestamp columns.

## Next action

User reruns the probe. A new chat interprets `holiday_product_post_id_type.txt`, then runs the Architect.

## Read next

- `decision.md` — Q-21, Q-22, Q-23
- `docs/context/mapping_slv_pn_product_l2.md` — `### 1.1. Xử lý` and the three `deleted_at` rows
- `evidence/probes/holiday_product_post_id_type.py` — header

## Waiting on

- Probe output pasted to `evidence/results/holiday_product_post_id_type.txt`.

## REQUEST

# Request

## User outcome

One document, `docs/context/mapping_slv_pn_product.md`, maps the legacy partner-product business rules onto the current silver L1 model. The frame matches `docs/context/mapping_gld_srv_poi_info.md`. A gap, a grain or key mismatch, or an open choice stays a question. It is not written as a settled rule.

## Scope

### In scope

- Take business rules only from `docs/context/mapping_legacy_ai_product.md` §1.1–§1.13 and the matching cells of `notebooks_lgc/pl_transform_partner_userprofile_cms/5. nb_prepare_product_for_ingestion.ipynb`.
- Map each current silver table that holds partner product or hotel data to one `##` section: `slv_pn_products`, `slv_pn_product_translations`, `slv_pn_product_attributes`, `slv_pn_product_attribute_translations`, `slv_pn_product_attribute_values`, `slv_pn_product_attribute_value_translations`, `slv_pn_product_variants`, `slv_pn_product_variant_translations`, `slv_pn_product_business_service_relation`, `slv_pn_product_posts`, `slv_pn_product_post_translations`, `slv_pn_hotel_room_types`, `slv_pn_hotel_rate_plans`.
- Each section states `Lakehouse.schema`, then `### Xử lý`, then `### Field Mapping` with columns `Source Field | Data Type | Transform | Target Field`, then a separate transform section when the rule does not fit the table.
- Every Field Mapping row names a column that exists in `TABLE_SPECS` of `notebooks/NB_SETUP_INITIAL_DDL.ipynb`.
- Record open choices in the document section `Câu hỏi cần chốt` and in the `decision.md` ledger.

### Out of scope

- Do not carry forward as target design: one product row with `variants_json`, joins to `ai_poi` or `ai_enriched_poi`, a hardcoded `destination_id` remap, a translation cache, or any LLM step.
- Do not map Azure OpenAI, `gpt-4.1`, `ENABLE_TRANSLATION`, or `ai_product_translation`. English names come only from a locale translation that already exists on the source. Do not add a name-generation step.
- No gold product table and no product transform notebook. Do not invent a table, column, grain, or key.
- Do not edit notebooks, DDL, pipelines, or tests. Do not commit. Do not run Fabric DEV. Do not run `run-author --kind proposal`. Do not run `run-gate`.

## Acceptance criteria

- `docs/context/mapping_slv_pn_product.md` exists. Each silver table above has one `##` section with `Lakehouse.schema`, `### Xử lý`, and `### Field Mapping`.
- A column or table that is not in `TABLE_SPECS` has no invented Field Mapping row. The legacy rule, the mismatch, and the question are in `Câu hỏi cần chốt`.
- Hotel, and every choice (target grain if it differs from silver L1, `source_id`, destination, NULL price, soft delete), stays in that question section until the user decides.
- The hotel branch of the legacy document is analyzed. Whether hotel is inside the settled mapping scope is an explicit question.

## Constraints

- Domain: partner extract and lib transform/gold. The deliverable is a document. It does not change runtime behavior.
- Current model: partner product is already silver L1, grain one source row, key `id`, written by `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`.
- Problem analysis is `run-author --kind analysis` (`claude-opus-5-5`, effort `medium`) into `problem-analysis.md`. Main does not write that analysis.
- If that analysis returns `EVIDENCE_REQUIRED` or `USER_DECISION`, stop and list each item. A missing JSON shape or a column absent from DDL gets the smallest probe and status `waiting_evidence`.
- After a completed analysis, Main writes the mapping from the analysis and the DDL.

## Classification rationale

- Complexity: `low`. No signal. The change adds one mapping document. It does not change a table, column, grain, key, or runtime behavior.
- Risk: `low`. No behavior change.
- Architecture: not required. No grain, key, state owner, transaction, CDC, watermark, lock, or orchestration change. Open choices stay questions; they are not an implementation selection.
- Evidence: not required at triage. Repository inspection of the named files is the source. A later `EVIDENCE_REQUIRED` from analysis overrides this.
- Runtime proof: not required. No Fabric DEV step.
- Reviewer routing: `required_reviewers` empty. WORKFLOW.md §7 routes specialists for code, SQL, pipeline, and API diffs. This task changes one Markdown file and does not change behavior. `risk_gate` is not required at `risk_level` `low`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| Q-01 | Nguồn cột Field Mapping | Nhận `TABLE_CONFIGS` là nguồn cột. Cột thiếu so với data hoặc model cũ thì trace nguồn. Map được theo bảng và model mới thì map. | user 2026-11-27 | 2026-11-27 |
| Q-02 | Cột silver mà rule legacy dùng | Đã trace trong mapping. Cột không có trên silver thì không có dòng Field Mapping. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-03 | Kiểu giá đã giải mã hay chuỗi | `original_price`, `marketing_price`, `markup_percent` là `string`, 36/36 `base64_like`. L1 giữ chuỗi. NULL giữ NULL. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-04 | `deleted_at` và thời điểm nguồn | `deleted_at` là chuỗi `timestamp_text` hoặc null. `src_created_at` / `src_updated_at` chưa đọc vì timestamp năm 58774. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-05 | JSON `products.metadata` | Object 41/41. Khóa `holiday_product_post_id`, `main_attribute_code` trên 41 dòng. `start_date`, `end_date` trên 15 dòng. Không tách cột. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-06 | JSON `product_variants.attributes` | Object 212/212. Khóa dạng `holiday:*`. Không in value. Không tách cột. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-07 | JSON `product_posts.raw_sync_data` | Object 27, null 9. Có `translations`, `shortDescription`, `tags`. `languageCode` quan sát: `en-VN`, `ko-VN`, `vi-VN`. Không tách cột. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-08 | Khoá join bản dịch giá trị thuộc tính | `attribute_id` có trong `TABLE_CONFIGS`. L1 giữ 1-1. Không dựng lại join của notebook cũ. | TABLE_CONFIGS | 2026-11-27 |
| Q-09 | Cột hotel mà §1.6 dùng | Cột có trong `TABLE_CONFIGS`. Room type và rate plan đã có dòng. Mapping L1, không gộp thành một dòng product. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-10 | Bảng product còn rỗng sau 04/10 | Không còn rỗng. `DESCRIBE DETAIL.numRecords` trả `None`. Số dòng lấy từ group-by của probe. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-11 | Hotel có trong phạm vi mapping đã chốt | Extract thiếu thì ghi việc extract lại. Probe: hai bảng hotel đã có dòng và nằm trong mapping L1. Logic khác extract là Silver L2. Ba bảng, tên, và file mapping nằm ở Q-19. | user 2026-11-27; Q-19 | 2026-11-27 |
| Q-12 | Grain đích khác silver L1 | Giữ silver L1: một dòng nguồn, khoá `id`. Từ L1 mới xét Silver L2 hay Gold. | user 2026-11-27 | 2026-11-27 |
| Q-13 | `source_id` thô hay `poi_id` đã hash | Không thêm `source_id` trên silver L1. Khi nối product sang POI: `poi_id = uuid_md5(business_service_id, 'partner')`. | user 2026-11-27 | 2026-11-27 |
| Q-14 | `destination_id` khi bỏ `ai_poi` | Giữ destination ngoài mapping L1. Nếu map được theo `slv_enr_poi_destination` thông qua map product với POI, xử lý transform ở Gold. | user 2026-11-27 | 2026-11-27 |
| Q-15 | Giá NULL giữ NULL hay thành 0 | Giữ NULL. | user 2026-11-27 | 2026-11-27 |
| Q-16 | Xoá mềm: `deleted`, `deleted_at`, hay cả hai | Cờ xoá của extract là `deleted` khi `op = d`. `deleted_at` là cột nguồn, giữ nguyên giá trị. | user 2026-11-27 | 2026-11-27 |
| Q-17 | So khớp `status` có phân biệt hoa thường | L1 giữ chuỗi nguồn. Product và variant: `active`. Hotel: `Active`, `Inactive`, `Draft`, `Archived`. `slv_pn_product_posts.status` null 36/36. Không đổi hoa thường. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-18 | Locale tiếng Anh trên bảng translation | Có dòng `locale = en` trên các bảng translation. Tên tiếng Anh lấy từ dòng đó. Không sinh tên. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-19 | Ba bảng Silver L2 | Đồng ý tách theo khuyến nghị: `slv_pn_product_sale`, `slv_pn_hotel_room_offer`, `slv_pn_hotel_rate_offer`. `valid_from` và `valid_to` chỉ chuyển 1-1. Không suy cờ bán từ hai cột vì code cũ không dùng chúng. | user 2026-11-27 | 2026-11-27 |
| Q-20 | Phân loại trước gate kiến trúc | Thêm signal `data_model_change`. `architecture_required` = true. `gates.architecture` = pending. Ba bảng Q-19 thêm grain và khoá. Kiểu JSON nằm ở Q-24. Chat này không sửa notebook, DDL, pipeline. | user 2026-11-27 | 2026-11-27 |
| Q-21 | `deleted_at` của ba bảng L2 | A. Dòng L2 vẫn có cho mọi id đang nằm trên L1. Ghi `deleted_at` khi L1 `deleted = true` hoặc id không còn. Lần tính sau, nếu nguồn về `deleted = false`, `deleted_at` trở lại NULL. | user 2026-11-27 | 2026-11-27 |
| Q-22 | `is_bookable` của `slv_pn_product_sale` | A. Không có variant `status = active` và `deleted = false` thì `false`. `status` và `deleted` của product không đi vào cờ này. | user 2026-11-27 | 2026-11-27 |
| Q-23 | Cột trong `row_hash` | A. Gồm khoá và các cột nghiệp vụ phía trên dòng hash, đúng thứ tự Field Mapping. Công thức `sha2(to_json(struct(...)), 256)`. `row_hash`, `created_at`, `updated_at`, `deleted_at` ở ngoài struct. | user 2026-11-27 | 2026-11-27 |
| Q-24 | Kiểu `holiday_product_post_id` | Giá trị JSON là chuỗi. 41/41 lớp `string`. So sánh chuỗi với `external_id` của post `deleted = false`: 41/41 khớp đúng một post. Không có post, hoặc nhiều hơn một post, thì `product_post_id` và ba giá vẫn NULL. | evidence/results/holiday_product_post_id_type.txt | 2026-11-27 |

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
- decision.md | 9667 bytes
- evidence/plan.md | 1263 bytes
- evidence/probes/holiday_product_post_id_type.py | 3336 bytes
- evidence/probes/product_payload_shape.py | 8460 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/holiday_product_post_id_type.txt | 127 bytes
- evidence/results/holiday_product_post_id_type_run1_fail.txt | 419 bytes
- evidence/results/product_payload_shape.txt | 1780 bytes
- evidence/results/product_payload_shape_run1_fail.txt | 284 bytes
- handoffs/author-input.md | 2937 bytes
- model-design.md | 15484 bytes
- problem-analysis.md | 20705 bytes | large: use toc/show
- request.md | 4457 bytes
- resume.md | 890 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1355 bytes

## NEXT

python scripts/vv.py run-gate 20261127-slv-pn-product-business-mapping

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### docs/context/mapping_slv_pn_product.md (23982 bytes)

# Mapping SLV Partner Product | L1-L404
## Quyết định đã chốt | L11-L21
## Câu hỏi cần chốt | L22-L28
## 1. Table: `slv_pn_products` | L29-L59
### 1.1. Xử lý | L33-L36
### 1.2. Field Mapping | L37-L55
### 1.3. `metadata` | L56-L59
## 2. Table: `slv_pn_product_translations` | L60-L83
### 2.1. Xử lý | L64-L67
### 2.2. Field Mapping | L68-L83
## 3. Table: `slv_pn_product_attributes` | L84-L108
### 3.1. Xử lý | L88-L91
### 3.2. Field Mapping | L92-L108
## 4. Table: `slv_pn_product_attribute_translations` | L109-L131
### 4.1. Xử lý | L113-L116
### 4.2. Field Mapping | L117-L131
## 5. Table: `slv_pn_product_attribute_values` | L132-L155
### 5.1. Xử lý | L136-L139
### 5.2. Field Mapping | L140-L155
## 6. Table: `slv_pn_product_attribute_value_translations` | L156-L176
### 6.1. Xử lý | L160-L163
### 6.2. Field Mapping | L164-L176
## 7. Table: `slv_pn_product_variants` | L177-L206
### 7.1. Xử lý | L181-L184
### 7.2. Field Mapping | L185-L202
### 7.3. `attributes` | L203-L206
## 8. Table: `slv_pn_product_variant_translations` | L207-L229
### 8.1. Xử lý | L211-L214
### 8.2. Field Mapping | L215-L229
## 9. Table: `slv_pn_product_business_service_relation` | L230-L251
### 9.1. Xử lý | L234-L237
### 9.2. Field Mapping | L238-L251
## 10. Table: `slv_pn_product_posts` | L252-L291
### 10.1. Xử lý | L256-L259
### 10.2. Field Mapping | L260-L287
### 10.3. `raw_sync_data` | L288-L291
## 11. Table: `slv_pn_product_post_translations` | L292-L323
### 11.1. Xử lý | L296-L299
### 11.2. Field Mapping | L300-L323
## 12. Table: `slv_pn_hotel_room_types` | L324-L365
### 12.1. Xử lý | L328-L331
### 12.2. Field Mapping | L332-L365
## 13. Table: `slv_pn_hotel_rate_plans` | L366-L404
### 13.1. Xử lý | L370-L373
### 13.2. Field Mapping | L374-L401
### 13.3. `meal_plan` | L402-L404
