# Architect handoff: 20261105-partner-hours-both-media-grain

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261105-partner-hours-both-media-grain --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261105-partner-hours-both-media-grain/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261105-partner-hours-both-media-grain | phase=triage

## STATE

id: 20261105-partner-hours-both-media-grain
title: Emit both partner hour intervals and key media by media_id plus poi_id
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=False, runtime_required=False
signals: data_model_change, stateful_logic, idempotency, cross_state_impact
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=not_required
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, state-correctness-reviewer, spark-runtime-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_GLD_SRV_POI_INFO.ipynb
- notebooks/NB_SLV_POI_MEDIA_INFO.ipynb
- notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb
- docs/context/mapping_gld_srv_poi_info.md
- docs/context/mapping_poi_media_info.md
- tests/test_gld_srv_poi_contract.py
- tests/test_poi_media_amenity_contract.py

## VALIDATION

PASS

## REQUEST

# Request

## User outcome

Partner opening hours with two intervals in one day are written, and silver plus gold media use the grain `media_id` + `poi_id`. User 2026-11-05, verbatim:

- Với những block có 2 mảng hours, vẫn phải xử lý cả 2.
- Với bảng slv_poi_media_info, grain/key sẽ gồm media_id và poi_id. Ở phần DataFrame nguồn sẽ xử lý merge trước, grain/key sẽ gồm media_id và poi_id và lấy theo updated_at lớn nhất.
- Khi nhiều dòng cùng media_id, cùng poi_id và cùng updated_at => Chọn dòng bất kỳ.
- Gallery đổi thành media_id + poi_id như silver.

The Monday record that produced `PARTNER_MULTI_HOURS` has `policies.operating_hours.monday.hours` of length 2: `08:00`–`09:00` and `11:00`–`22:00`. The other six days in that record have one element. Both Monday intervals must appear in the partner `operating_hours` output. The node must not raise `PARTNER_MULTI_HOURS` for that shape.

`slv_poi_media_info` and `gld_srv_poi_media_gallery` MERGE on `media_id` and `poi_id`. Before that MERGE, the media source DataFrame is reduced to one row per `media_id`, `poi_id`, keeping the greatest `updated_at`. Equal `updated_at` may keep any of the tied rows. A rerun with the same input must keep the same row.

## Scope

### In scope

- Partner hours transform in `NB_GLD_SRV_POI_INFO` and `docs/context/mapping_gld_srv_poi_info.md` §1.5.
- `NB_SLV_POI_MEDIA_INFO` source reduction and MERGE key.
- `NB_GLD_SRV_POI_MEDIA_GALLERY` MERGE key.
- `docs/context/mapping_poi_media_info.md`.
- Contract tests that currently require `PARTNER_MULTI_HOURS` or `pk == ("media_id",)`.

### Out of scope

- `NB_SLV_POI_ENTITY_NON_ENRICH`, review notebooks, enrich notebooks, and the orchestrator.
- PostgreSQL `sql/postgres/gld_srv_serve.pg.sql`.
- Changing the partner `media_id` hash or the Google `media_dedup_key` assignment.
- A day whose `hours` array has a length other than 2. Length 0 and length 1 stay on the current §1.5 rules. Length greater than 2 is not decided here.

## Acceptance criteria

- A partner day with exactly two `hours` elements emits both intervals and does not raise `PARTNER_MULTI_HOURS`.
- `NB_SLV_POI_MEDIA_INFO` and `NB_GLD_SRV_POI_MEDIA_GALLERY` use `pk` `("media_id", "poi_id")`.
- The media build output contains one row per `media_id`, `poi_id` before `quality_gate`.
- The kept row is one of the rows with the greatest source `updated_at`. The choice is stable across reruns.
- Mapping text matches the notebooks.

## Constraints

- Source `updated_at` is the technical column written by extract, not `src_updated_at` and not `last_updated_at`. Partner CDC tables and the 3p snapshot table both carry that column (`NB_LIB_EXTRACT_RAWDATA` `TECH_COLUMNS` and `SNAPSHOT_TECH_COLUMNS`). The media build must carry it onto each exploded element from its parent row.
- Three exploded elements from one i18n row share that parent's `updated_at`. The tie rule applies.
- Do not invent columns. The single-interval partner object shape in mapping §1.5 stays. Two intervals are two of those objects.
- Idempotency: "chọn dòng bất kỳ" allows any tied business row, and forbids a pick that changes between reruns.
- Task `20261104-poi-review-src-and-partner-i18n` already used review round 2. Do not edit its notebooks for this change.

## Classification rationale

- Complexity: high. Hours output shape and a MERGE grain change across silver and gold.
- Risk: high. MERGE key, source collapse, and rerun stability.
- Architecture: required. The grain and the commit key change.
- Evidence: not required. The eight hour keys and two media keys are in the parent task results. Column `updated_at` is in the extract contract.
- Runtime proof: not required. The hours function and the collapse are locally testable.
- Reviewer routing: `sql-data-reviewer`, `state-correctness-reviewer`, `spark-runtime-reviewer`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-HOURS-2 | Hai phần tử hours | Với những block có 2 mảng hours, vẫn phải xử lý cả 2. | User 2026-11-05 | 2026-11-05 |
| D-MEDIA-KEY | Grain media | Với bảng slv_poi_media_info, grain/key sẽ gồm media_id và poi_id. Ở phần DataFrame nguồn sẽ xử lý merge trước, grain/key sẽ gồm media_id và poi_id và lấy theo updated_at lớn nhất. | User 2026-11-05 | 2026-11-05 |
| D-MEDIA-TIE | Hòa updated_at | Khi nhiều dòng cùng media_id, cùng poi_id và cùng updated_at => Chọn dòng bất kỳ. | User 2026-11-05 | 2026-11-05 |
| D-GALLERY-KEY | Grain gallery | Gallery đổi thành media_id + poi_id như silver. | User 2026-11-05 | 2026-11-05 |
| D-HOURS-ORDER | Thứ tự hai ca | Hai object giờ của một ngày giữ thứ tự trong mảng nguồn, phần tử 0 rồi phần tử 1. Ngày có hơn 2 phần tử vẫn dừng `PARTNER_MULTI_HOURS`. | request.md `## Out of scope`; model-design.md Conflicts 7 | 2026-11-05 |
| D-MEDIA-PARENT | updated_at của phần tử | `updated_at` là cột kỹ thuật extract của đúng dòng cha đã nổ mảng: i18n khi dùng media i18n, services khi fallback, `slv_3p_poi_media` với Google. Null xếp sau mọi giá trị có mốc. | NB_LIB_EXTRACT_RAWDATA TECH_COLUMNS, SNAPSHOT_TECH_COLUMNS | 2026-11-05 |

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
- decision.md | 3314 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/author-input.md | 1910 bytes
- model-design.md | 10488 bytes
- request.md | 3970 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1691 bytes

## NEXT

python scripts/vv.py run-gate 20261105-partner-hours-both-media-grain
