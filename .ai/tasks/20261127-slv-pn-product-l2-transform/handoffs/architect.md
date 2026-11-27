# Architect handoff: 20261127-slv-pn-product-l2-transform

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261127-slv-pn-product-l2-transform --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261127-slv-pn-product-l2-transform/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261127-slv-pn-product-l2-transform | phase=triage

## STATE

id: 20261127-slv-pn-product-l2-transform
title: Silver L2 product sale and hotel offer transforms
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=False
signals: data_model_change, idempotency, stateful_logic
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=not_required
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: state-correctness-reviewer, spark-runtime-reviewer, sql-data-reviewer
open findings: none
exceptions: none
scope.files:

## VALIDATION

PASS

## REQUEST

# Request

## User outcome

Three Silver L2 tables exist and recompute from the closed L1 product mapping: `slv_pn_product_sale`, `slv_pn_hotel_room_offer`, and `slv_pn_hotel_rate_offer`. The shared transform library can soft-delete a row that is still present in the build when the build supplies a delete flag. Existing nodes keep today's MERGE behavior.

## Scope

### In scope

- The three L2 tables, their grain and keys, technical columns, and the node notebooks that own them.
- Registering those tables only where the architecture edit list names a `TABLE_SPECS` or ctrl row.
- One opt-in delete-flag branch in `NB_LIB_TRANSFORM_SLV_GLD`, default off.

### Out of scope

- Changing columns, grain, or keys of the 13 `slv_pn_product*` and `slv_pn_hotel*` L1 tables.
- Re-deciding business rules or the silver/gold layer split.
- `variants_json`, an LLM, destination, `source_id`, and `poi_id` on the three L2 tables.
- Task `20261127-slv-pn-product-business-mapping` (read-only source of Q-19 through Q-24 and option B).

## Acceptance criteria

- L1 tables above stay unchanged in columns, grain, and keys.
- Names and grain: `slv_pn_product_sale` (`product_id`), `slv_pn_hotel_room_offer` (`room_type_id`), `slv_pn_hotel_rate_offer` (`rate_plan_id`).
- `valid_from` and `valid_to` copy 1-1. NULL stays NULL. No sale flag is derived from those columns. The open `EPOCH_S_TS` unit is inherited from L1 and is not assigned here.
- A NULL price stays NULL. The value 0 is not written in its place.
- `slv_pn_product_sale.is_bookable` is false when no variant has `status = active` and `deleted = false`.
- `row_hash` covers the key and the business columns in Field Mapping order. Timestamps inside the hash use `unix_micros`. Outside the struct: `row_hash`, `created_at`, `updated_at`, `deleted_at`, and the delete flag.
- `deleted_at` keeps the timestamp of the first run that sees a delete. A later run sets it to NULL when L1 `deleted = false`. When an id disappears from L1, business columns keep the last computed values.
- The delete flag comes from the build and is not stored as a column. The lib default still soft-deletes only ids missing from the build. Old nodes do not change behavior while the flag defaults off.
- The three L2 tables have no `variants_json`, LLM output, destination, `source_id`, or `poi_id`.

## Constraints

- Q-19 through Q-24 and `docs/context/mapping_slv_pn_product_l2.md` win when current code disagrees.
- A rule that is not in those sources, or in option B of the prior architecture, stops that line as a question.
- No `run-author --kind analysis` and no `run-author --kind proposal`.
- Do not edit task `20261127-slv-pn-product-business-mapping`.

## Classification rationale

- Complexity: medium. Three new tables and one opt-in MERGE branch. Not a fast lane.
- Risk: medium. The new branch is opt-in and existing nodes stay on the default path. Rollback is reverting the notebooks. Local tests can prove the branch.
- Architecture: required. New grain and keys, plus a MERGE delete branch in the shared lib.
- Evidence: not required. L1 shape, the post-id probe, and Q-19 through Q-24 are already closed. The epoch unit stays unresolved because the copy is 1-1.
- Runtime proof: not required at classification. A Fabric run is only added if architecture requires it.
- Reviewer routing: `sql-data-reviewer` for the MERGE, `spark-runtime-reviewer` for the lib and node notebooks, `state-correctness-reviewer` for `deleted_at` retention and missing-id soft delete. Signals: `data_model_change`, `idempotency`, `stateful_logic`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| C-01 | Phân loại trước gate | Signal `data_model_change`, `idempotency`, `stateful_logic`. `architecture_required` = true. `evidence_required` = false. `runtime_required` = false. Complexity medium. Risk medium. Reviewer: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`. | user 2026-11-27; WORKFLOW.md §5 và §7 | 2026-11-27 |
| C-02 | `updated_at` khi `deleted_at` đổi | Field Mapping L2 thắng §5.2 trên ba bảng này: `updated_at` đổi khi `row_hash` đổi hoặc khi `deleted_at` đổi giữa NULL và khác NULL. | mapping_slv_pn_product_l2.md Field Mapping | 2026-11-27 |
| C-03 | Tên notebook node | §2: một notebook một bảng đích, tên `NB_<UPPER(trg_tbl)>`: `NB_SLV_PN_PRODUCT_SALE`, `NB_SLV_PN_HOTEL_ROOM_OFFER`, `NB_SLV_PN_HOTEL_RATE_OFFER`. | 02_NAMING_CONVENTION.md §2 | 2026-11-27 |
| C-04 | Tiền tố `slv_pn_` trên L2 | Giữ đúng tên Q-19. Không đổi tên bảng. Task này không sửa §1. | mapping_slv_pn_product_l2.md dòng mở đầu; Q-19 | 2026-11-27 |
| C-05 | Kiểu `deleted_at` | Cột đích là `timestamp`. Ô Data Type `boolean` trên dòng Field Mapping là kiểu cờ `deleted` nguồn, không phải kiểu cột L2. | mapping_slv_pn_product_l2.md dòng cột kỹ thuật; 02_NAMING_CONVENTION.md §5.2 | 2026-11-27 |
| C-06 | Giải mã giá | Làm đúng `mapping_slv_pn_product_l2.md` §1.3. Không mở file legacy ngoài tóm tắt đó. NULL giữ NULL. Không ghi 0. | mapping_slv_pn_product_l2.md §1.3; Q-15 | 2026-11-27 |
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
- decision.md | 5683 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/author-input.md | 3304 bytes
- model-design.md | 16293 bytes
- request.md | 3625 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1356 bytes

## NEXT

python scripts/vv.py run-gate 20261127-slv-pn-product-l2-transform
