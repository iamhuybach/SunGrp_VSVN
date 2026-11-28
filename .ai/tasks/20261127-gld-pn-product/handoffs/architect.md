# Architect handoff: 20261127-gld-pn-product

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261127-gld-pn-product --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261127-gld-pn-product/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261127-gld-pn-product | phase=triage

## STATE

id: 20261127-gld-pn-product
title: Gold partner product from silver L2
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=True, runtime_required=False
signals: data_model_change
gates: evidence=evidence_required, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=not_required
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer
open findings: none
exceptions: none
scope.files:

## VALIDATION

PASS

## RESUME

# Resume 20261127-gld-pn-product

Status: blocked / main. Gates unchanged: evidence=evidence_required, architecture=evidence_required (round 1).

Done this session: User chose one table like the old model (D-A). Mapping rewrite is a new task, slug `pn-product-one-table-mapping`. This task does not implement and does not run probes P1–P6. Three-table model-design is not the target.

Next action: New chat for the mapping task, using the prompt in the user reply. After that task finishes, a new chat resumes this task: read its `## Quyết định hiện hành` and the rewritten mapping, re-run `run-author --kind model`, then the architecture gate.

Read next: `.ai/tasks/20261127-gld-pn-product/decision.md` row D-A; `docs/context/mapping_legacy_ai_product.md` `## 1. Table: ai_product`; the mapping task's `decision.md` once it exists.

Waiting on: the mapping task `pn-product-one-table-mapping` to finish, including answers to the open shape questions.

## REQUEST

# Request

## User outcome

One gold serving table, `lh_vv_gold.dbo.gld_srv_product_offer`. One row per `product_id`. Holiday and hotel share the table. Variant facts sit in `variants_json`. Gold attaches `poi_id` and copies `destination_id` from `slv_enr_poi_destination`.

## Scope

### In scope

- The table, grain, and columns in `docs/context/mapping_gld_srv_product_offer.md` §1.
- A recompute gold transform that reads silver only. Sources are the three Q-19 L2 tables plus the L1 tables named in that mapping, then `slv_enr_poi_destination`.
- DDL for `gld_srv_product_offer` and the pipeline edge named by the Architect `Main brief`.

### Out of scope

- A destination column on any silver table.
- Reading any gold table. `gld_srv_poi_info` is a type contract for `destination_id` only.
- Joining `ai_poi`, remapping `destination_id`, or a fallback destination constant.
- Decoding or changing prices. The L2 decoder change in D-1 is another task.
- A sale flag derived from `valid_from` and `valid_to`.
- A new proposal or problem analysis.

## Acceptance criteria

- The gold table is `gld_srv_product_offer`. Grain is one row per `product_id` (U-02, D-0). Holiday `product_type` is `other`. Hotel `product_type` is `hotel`.
- `poi_id = uuid_md5(business_service_id, 'partner')`. Left join `slv_enr_poi_destination` on `poi_id`. A missing POI or destination keeps the row and leaves `destination_id` NULL (D-4). `destination_id` is the JSON array string copied unchanged (D-5).
- Prices pass through from `slv_pn_product_sale`. NULL stays NULL. Gold does not decode them (U-06, D-1).
- `variants_json` is built as mapping §1.3 and §1.5. `valid_from` and `valid_to` are inside the hotel element. No sale flag is derived from them (U-07).
- `is_bookable` is copied 1-1 from L2. `is_active` is the technical flag paired with `deleted_at` (D-8).
- A holiday product with more than one distinct `business_service_id` on `deleted = false` relation rows is dropped entirely (U-04, D-10).

## Constraints

- Do not add a business rule that is absent from `docs/context/mapping_gld_srv_product_offer.md` or from the received ledger. Record the question and stop that line.
- Mapping items still open: attribute value codes, epoch unit of `valid_from` and `valid_to`, and the shape of room `tags` and `amenities`. Do not close them in this task.
- Do not run `run-author --kind analysis` or `run-author --kind proposal`.
- The three-table `model-design.md` from 2026-11-27 is withdrawn.
- Domain for edits: the paths named by the `Main brief`.

## Classification rationale

- Complexity: medium. One gold grain over holiday and hotel silver sources.
- Risk: medium. New gold table and recompute write, with rollback by not publishing the table.
- Architecture: required. Grain, key, and the silver-to-gold boundary change.
- Evidence: the mapping task closed the shape questions. The Architect may still require a probe. Do not rerun P1–P6 unless the new architecture names them.
- Runtime proof: not required at triage.
- Reviewer routing: `sql-data-reviewer` for the gold SQL grain, join, and types; `spark-runtime-reviewer` for the Fabric recompute notebook.
- Signal: `data_model_change`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| Q-13 | `source_id` thô hay `poi_id` đã hash | Không thêm `source_id` trên silver L1. Khi nối product sang POI: `poi_id = uuid_md5(business_service_id, 'partner')`. | 20261127-slv-pn-product-business-mapping `## Quyết định hiện hành` Q-13 | 2026-11-27 |
| Q-14 | `destination_id` khi bỏ `ai_poi` | Giữ destination ngoài mapping L1. Nếu map được theo `slv_enr_poi_destination` thông qua map product với POI, xử lý transform ở Gold. | 20261127-slv-pn-product-business-mapping `## Quyết định hiện hành` Q-14 | 2026-11-27 |
| Q-15 | Giá NULL giữ NULL hay thành 0 | Giữ NULL. | 20261127-slv-pn-product-business-mapping `## Quyết định hiện hành` Q-15 | 2026-11-27 |
| Q-19 | Ba bảng Silver L2 | Đồng ý tách theo khuyến nghị: `slv_pn_product_sale`, `slv_pn_hotel_room_offer`, `slv_pn_hotel_rate_offer`. `valid_from` và `valid_to` chỉ chuyển 1-1. Không suy cờ bán từ hai cột vì code cũ không dùng chúng. | 20261127-slv-pn-product-business-mapping `## Quyết định hiện hành` Q-19 | 2026-11-27 |
| D-A | Một bảng như model cũ | Mapping đã xong ở task `20261127-pn-product-one-table-mapping`, file `docs/context/mapping_gld_srv_product_offer.md`. Nhận nguyên văn các dòng U-01 đến D-9 bên dưới. Không mở rule mới. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` | 2026-11-28 |
| U-01 | Lớp và tên bảng | Bảng ở Gold. Tên `lh_vv_gold.dbo.gld_srv_product_offer`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-01 | 2026-11-27 |
| U-02 | Grain | Như mục 1.1: một dòng một `product_id`. Mỗi variant là một phần tử `{variant_id, name, status, attributes}` trong `variants_json`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-02 | 2026-11-27 |
| U-03 | Hotel | Hotel cùng bảng. Holiday: grain `products.id`. Hotel: grain `hotel_room_types.id`, `product_type = hotel`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-03 | 2026-11-27 |
| U-05 | Destination | Gold nối product sang POI bằng `poi_id = uuid_md5(business_service_id, 'partner')`, rồi tới `slv_enr_poi_destination`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-05 | 2026-11-27 |
| U-07 | `valid_from` và `valid_to` | Nằm trong `variants_json` của rate plan, không suy cờ bán. Cột riêng chỉ hợp grain một dòng một rate plan. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-07 | 2026-11-27 |
| U-04 | Nhiều `business_service_id` | Ở bảng đích, product có hơn một `business_service_id` thì loại cả product. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-04 | 2026-11-27 |
| U-06 | Giá | Không transform, giải mã được cho fail job để tìm cách giải mã khác khắc phục. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-06 | 2026-11-27 |
| U-08 | Ba bảng Q-19 | Ba bảng Q-19 còn là nguồn. Bảng gold gom từ L1 và ba bảng đó. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-08 | 2026-11-27 |
| D-0 | Khoá khi id holiday trùng id hotel | P-1: `cross_collisions` 0, `dup_products` 0, `dup_rooms` 0. Khoá giữ `product_id`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-0 | 2026-11-28 |
| D-1 | Chỗ fail job khi giải mã giá | Đồng ý khuyến nghị (c): sửa decoder của `slv_pn_product_sale` để lỗi giải mã fail job thay vì ghi NULL. Gold không giải mã và không đổi giá. Việc sửa L2 nằm ngoài task này. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-1 | 2026-11-28 |
| D-2 | `product_type` holiday | Đồng ý khuyến nghị: `'other'`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-2 | 2026-11-28 |
| D-3 | Fallback `business_service_id` | Relation trước, post chỉ khi không có dòng relation `deleted = false`. U-04 đếm các dòng relation `deleted = false` trước fallback. Product không có id vẫn giữ dòng theo D-4. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-3 | 2026-11-28 |
| D-4 | Dòng thiếu POI hoặc destination | Chọn D-4. `poi_id` NULL vẫn giữ dòng. Có `poi_id` mà không có dòng destination thì giữ dòng, `destination_id` NULL. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-4 | 2026-11-28 |
| D-10 | Relation đã xoá | Đồng ý khuyến nghị: U-04 và bước «relation không có dòng» chỉ tính dòng `deleted = false`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-10 | 2026-11-28 |
| D-5 | Dạng `destination_id` | Đồng ý khuyến nghị: copy nguyên chuỗi JSON array, cùng contract `gld_srv_poi_info.destination_id`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-5 | 2026-11-28 |
| D-6 | `variants_json` holiday | Đồng ý khuyến nghị: `name` locale `vi`; `attributes` là JSON thô; bỏ variant `deleted = true`; product không có variant vẫn có dòng, `variants_json = []`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-6 | 2026-11-28 |
| D-7 | `variants_json` hotel | Đồng ý khuyến nghị: khoá `meal_plan` (số), `kind`, `valid_from`, `valid_to` (ISO-8601 UTC), `include_tax`, `include_service_charge`. Phòng không có rate plan thì `[]`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-7 | 2026-11-28 |
| D-8 | `is_active` và `is_bookable` | Đồng ý khuyến nghị: `is_active` chỉ là cờ kỹ thuật. `is_bookable` copy 1-1 từ L2, không thêm cửa. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-8 | 2026-11-28 |
| D-9 | Danh sách cột | Giữ nguyên, không bỏ cột nào: `name`, `lang`, `product_line`, `price_level`, `variant_count`, `active_variant_count`, `variant_tickets`, `variant_dates`, `variant_hotels`, `variant_age_groups`, `variant_room_types`, `variant_departures`, `variant_statuses`, `product_attributes`, `source_id`, `business_service_id`, `product_post_id`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-9 | 2026-11-28 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 28748 bytes

## FILES

- architecture.md | 28748 bytes | large: use toc/show
- decision.md | 8281 bytes
- evidence/plan.md | 872 bytes
- evidence/probes/p1_p6_gold_product_keys.sql | 4109 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 9767 bytes
- handoffs/author-input.md | 2052 bytes
- model-design.md | 15349 bytes
- request.md | 3249 bytes
- resume.md | 974 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1273 bytes

## NEXT

python scripts/vv.py run-gate 20261127-gld-pn-product
