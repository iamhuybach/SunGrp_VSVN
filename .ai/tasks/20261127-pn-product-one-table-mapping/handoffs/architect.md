# Architect handoff: 20261127-pn-product-one-table-mapping

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261127-pn-product-one-table-mapping --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261127-pn-product-one-table-mapping/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261127-pn-product-one-table-mapping | phase=triage

## STATE

id: 20261127-pn-product-one-table-mapping
title: Rewrite partner product mapping as one table
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=True, runtime_required=False
signals: data_model_change, data_evidence_required
gates: evidence=pass, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=not_required
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: sql-data-reviewer
open findings: none
exceptions: none
scope.files:
- docs/context/mapping_gld_srv_product_offer.md

## VALIDATION

PASS

## RESUME

# Resume

## Status
user_decision

## Done this session
Saved product_offer_blocking.txt. P-1 is all zeros, so D-0 stays product_id.
Recorded D-1..D-9. D-4 keeps a NULL poi_id row. D-9 keeps every listed column.
Re-ran run-author --kind model and replaced model-design.md.
Did not run-gate. Two items remain: deleted relation rows, and D-3 vs D-4.

## Next action
Record the two answers in decision.md. Re-run run-author --kind model if the design must change.
Then run-gate. scope.files already lists docs/context/mapping_gld_srv_product_offer.md.
Architecture round is 1 of 2.

## Read next
- .ai/tasks/20261127-pn-product-one-table-mapping/decision.md ## Quyết định hiện hành
- .ai/tasks/20261127-pn-product-one-table-mapping/model-design.md ## Conflicts and questions
- evidence/results/product_offer_blocking.txt

## Waiting on
Whether U-04 and D-3 count only relation rows with deleted = false.
Whether D-3 dropping a product with no id overrides D-4 keeping a NULL poi_id row.

## REQUEST

# Request

## User outcome

The partner product mapping documents specify one table in the shape of the legacy `ai_product` model. Task `20261127-gld-pn-product` stays blocked on D-A until that mapping exists. This task does not change a notebook, DDL, or pipeline.

## Scope

### In scope

- Rewrite the partner product mapping so the documented target is one table, using `docs/context/mapping_legacy_ai_product.md` section `## 1. Table: ai_product` as the legacy shape.
- Read-only sources: `docs/context/mapping_slv_pn_product.md`, `docs/context/mapping_slv_pn_product_l2.md`, `.ai/tasks/20261127-slv-pn-product-business-mapping/decision.md` section `## Quyết định hiện hành`, and D-A in `.ai/tasks/20261127-gld-pn-product/decision.md`.
- After the user answers the eight open choices, record those answers in this task's `decision.md`, then continue model design and architecture. The mapping file edited later is only a file named by the architecture edit list.

### Out of scope

- Notebooks, DDL, pipeline JSON, and seeds.
- Any file under `.ai/tasks/20261127-gld-pn-product/`.
- `run-author --kind analysis` and `run-author --kind proposal`.
- Implementing or unblocking the gold task in this task.

## Acceptance criteria

- Classification matches `docs/agent-system/WORKFLOW.md` §Classification and §Review routing: signal `data_model_change`, `architecture_required` true, required reviewer `sql-data-reviewer` only.
- Mapping prose is written only after all eight choices are rows in `## Quyết định hiện hành`, and only in files the architecture edit list names.
- The task stops when specialist review finishes, or earlier at `EVIDENCE_REQUIRED` or `USER_DECISION`.

## Constraints

- One chat per phase.
- Do not infer the eight choices. They are user decisions.
- Signal `data_model_change` requires `model-design.md` from `run-author --kind model` before the Architect.
- Do not route `spark-runtime-reviewer`. No notebook is in scope.

## Classification rationale

- Complexity: medium. The documented grain moves from the current L1 tables plus the three Q-19 L2 tables toward one table. That is a model change, not a wording fix.
- Risk: medium. The mapping is the contract task `20261127-gld-pn-product` will follow after D-A. This task does not write notebooks or tables. Rollback is reverting the mapping document.
- Architecture: required. WORKFLOW §5 requires architecture when a table grain or key changes. Signal `data_model_change`. `gates.architecture` is pending.
- Evidence: not required at triage. The open items are choices among options already written in the named mapping docs and decision ledgers.
- Runtime proof: not required. No notebook, pipeline, or table is changed or executed.
- Reviewer routing: `sql-data-reviewer` owns grain, joins, types, and field mapping. `spark-runtime-reviewer` is omitted because no notebook is in scope. Risk is medium, so `risk-gate` is not required.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| U-01 | Lớp và tên bảng | Bảng ở Gold. Tên `lh_vv_gold.dbo.gld_srv_product_offer`. | user 2026-11-27 | 2026-11-27 |
| U-02 | Grain | Như mục 1.1: một dòng một `product_id`. Mỗi variant là một phần tử `{variant_id, name, status, attributes}` trong `variants_json`. | user 2026-11-27 | 2026-11-27 |
| U-03 | Hotel | Hotel cùng bảng. Holiday: grain `products.id`. Hotel: grain `hotel_room_types.id`, `product_type = hotel`. | user 2026-11-27 | 2026-11-27 |
| U-05 | Destination | Gold nối product sang POI bằng `poi_id = uuid_md5(business_service_id, 'partner')`, rồi tới `slv_enr_poi_destination`. | user 2026-11-27 | 2026-11-27 |
| U-07 | `valid_from` và `valid_to` | Nằm trong `variants_json` của rate plan, không suy cờ bán. Cột riêng chỉ hợp grain một dòng một rate plan. | user 2026-11-27 | 2026-11-27 |
| U-04 | Nhiều `business_service_id` | Ở bảng đích, product có hơn một `business_service_id` thì loại cả product. | user 2026-11-27; evidence/results/product_business_service_cardinality.txt | 2026-11-27 |
| U-06 | Giá | Không transform, giải mã được cho fail job để tìm cách giải mã khác khắc phục. | user 2026-11-27; evidence/results/product_price_shape.txt | 2026-11-27 |
| U-08 | Ba bảng Q-19 | Ba bảng Q-19 còn là nguồn. Bảng gold gom từ L1 và ba bảng đó. | user 2026-11-27 | 2026-11-27 |
| D-0 | Khoá khi id holiday trùng id hotel | P-1: `cross_collisions` 0, `dup_products` 0, `dup_rooms` 0. Khoá giữ `product_id`. | evidence/results/product_offer_blocking.txt | 2026-11-28 |
| D-1 | Chỗ fail job khi giải mã giá | Đồng ý khuyến nghị (c): sửa decoder của `slv_pn_product_sale` để lỗi giải mã fail job thay vì ghi NULL. Gold không giải mã và không đổi giá. Việc sửa L2 nằm ngoài task này. | user 2026-11-28; architecture.md §2 D-1 | 2026-11-28 |
| D-2 | `product_type` holiday | Đồng ý khuyến nghị: `'other'`. | user 2026-11-28; architecture.md §2 D-2 | 2026-11-28 |
| D-3 | Fallback `business_service_id` | Relation trước, post chỉ khi không có dòng relation `deleted = false`. U-04 đếm các dòng relation `deleted = false` trước fallback. Product không có id vẫn giữ dòng theo D-4. | user 2026-11-28 | 2026-11-28 |
| D-4 | Dòng thiếu POI hoặc destination | Chọn D-4. `poi_id` NULL vẫn giữ dòng. Có `poi_id` mà không có dòng destination thì giữ dòng, `destination_id` NULL. | user 2026-11-28 | 2026-11-28 |
| D-10 | Relation đã xoá | Đồng ý khuyến nghị: U-04 và bước «relation không có dòng» chỉ tính dòng `deleted = false`. | user 2026-11-28 | 2026-11-28 |
| D-5 | Dạng `destination_id` | Đồng ý khuyến nghị: copy nguyên chuỗi JSON array, cùng contract `gld_srv_poi_info.destination_id`. | user 2026-11-28; architecture.md §2 D-5 | 2026-11-28 |
| D-6 | `variants_json` holiday | Đồng ý khuyến nghị: `name` locale `vi`; `attributes` là JSON thô; bỏ variant `deleted = true`; product không có variant vẫn có dòng, `variants_json = []`. | user 2026-11-28; architecture.md §2 D-6 | 2026-11-28 |
| D-7 | `variants_json` hotel | Đồng ý khuyến nghị: khoá `meal_plan` (số), `kind`, `valid_from`, `valid_to` (ISO-8601 UTC), `include_tax`, `include_service_charge`. Phòng không có rate plan thì `[]`. | user 2026-11-28; architecture.md §2 D-7 | 2026-11-28 |
| D-8 | `is_active` và `is_bookable` | Đồng ý khuyến nghị: `is_active` chỉ là cờ kỹ thuật. `is_bookable` copy 1-1 từ L2, không thêm cửa. | user 2026-11-28; architecture.md §2 D-8 | 2026-11-28 |
| D-9 | Danh sách cột | Giữ nguyên, không bỏ cột nào: `name`, `lang`, `product_line`, `price_level`, `variant_count`, `active_variant_count`, `variant_tickets`, `variant_dates`, `variant_hotels`, `variant_age_groups`, `variant_room_types`, `variant_departures`, `variant_statuses`, `product_attributes`, `source_id`, `business_service_id`, `product_post_id`. | user 2026-11-28 | 2026-11-28 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 21710 bytes

## FILES

- architecture.md | 21710 bytes | large: use toc/show
- decision.md | 6552 bytes
- evidence/plan.md | 1369 bytes
- evidence/probes/product_business_service_cardinality.py | 4490 bytes
- evidence/probes/product_offer_blocking.py | 5690 bytes
- evidence/probes/product_price_shape.py | 3606 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/product_business_service_cardinality.txt | 2950 bytes
- evidence/results/product_offer_blocking.txt | 677 bytes
- evidence/results/product_price_shape.txt | 447 bytes
- handoffs/architect.md | 11282 bytes
- handoffs/author-input.md | 3123 bytes
- model-design.md | 14644 bytes
- request.md | 2985 bytes
- resume.md | 1016 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1318 bytes

## NEXT

python scripts/vv.py run-gate 20261127-pn-product-one-table-mapping
