# Architect handoff: 20261126-practical-info-poi-name-or-ids

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261126-practical-info-poi-name-or-ids --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261126-practical-info-poi-name-or-ids/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261126-practical-info-poi-name-or-ids | phase=triage

## STATE

id: 20261126-practical-info-poi-name-or-ids
title: Query practical_info by poi_name or ids
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: runtime_proof_required
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: api-contract-reviewer, jpa-performance-reviewer
open findings: none
exceptions: none
scope.files:
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PracticalInfoSearchRequest.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PracticalInfoQuery.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryImpl.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryCustom.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/PoiControllerIntegrationTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/LegacyAndPracticalInfoIntegrationTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/domain/repository/PoiRepositoryIntegrationTest.java
- docs/context/api-mapping/practical_info_list.md

## VALIDATION

PASS

## REQUEST

# Request

## User outcome

`POST /api/v1/pois/practical_info` accepts `poi_name` or `ids` in the JSON body as alternative selectors. A name does not filter the id set. `GET /api/v1/pois/{poi_id}/practical_info` stays unchanged.

## Scope

### In scope

- `POST /api/v1/pois/practical_info` body contract, validation, SQL selection, tests, and `docs/context/api-mapping/practical_info_list.md`.
- `scope.systems`: `poi-serving-api`.
- Replace the AND behavior shipped by task `20261126-practical-info-poi-name-body`.

### Out of scope

- `GET /api/v1/pois/{poi_id}/practical_info`.
- Query parameters `required_fields`, `source`, `lang`, `page`, `size`, `sort_field`, `sort_order`.
- Gold schema, new columns, tables, or keys.
- `docs/poi-serving-api/`.
- Fast lane. The HTTP contract changes.
- The deploy repo `D:\git\SunGrp_VSVN_API` until this task's contract is implemented here.

## Yêu cầu nguyên văn

poi_name bạn đã làm sai yêu cầu. Tôi muốn nó được query tương đương với ids chứ không phải được filter từ ids. Ở body request có thể nhập poi_name hoặc ids.

## Acceptance criteria

- A body with only `ids` selects those POIs and does not apply a name predicate.
- A body with only `poi_name` selects by name and does not require `ids`.
- A body with both selectors returns the union of the two selections. It does not return the intersection.
- A body with neither selector returns 422.
- `poi_name` stays one string, maximum 128. Longer than 128 returns 422. A non-string JSON value returns 400.
- The name match stays the documented rule: contains, case-insensitive, on `apps.srv_poi_info.poi_name`, with `%`, `_`, and `\` escaped.
- When `ids` is present it keeps the current rules: 1 to 500 strings, each non-empty and at most 128 characters. An empty `ids` array is "no id selector", not a 422, when `poi_name` is present.
- The `poi_name` query parameter still does not filter.
- `source`, paging, and sort still apply to the selected rows.
- `docs/context/api-mapping/practical_info_list.md` matches this contract before review.
- Local verification PASS before review. P0/P1 findings are handled within two review rounds.

## Constraints

- The API follows gold. Do not add columns, tables, or keys.
- Do not read `docs/poi-serving-api/`.
- Do not copy credentials or hosts into the repository or task artifacts.
- Do not commit. Do not run `docker compose` unless the user asks in the current turn.
- `SrvPoiLegacyIdMapRepositoryImpl.findPracticalInfoPage` currently returns an empty page when `ids` is empty before the name predicate is applied. That is the behavior to replace.

## Classification rationale

- Complexity: medium. The selector moves from "ids required, name filters those ids" to "ids or name, union when both are present". The repository SQL changes. No CDC, watermark, or grain change.
- Risk: medium. Bounded HTTP and query behavior change. Rollback is reverting the endpoint. Local tests can prove the selectors.
- Architecture: required. `docs/AGENT_PROMPT_SAMPLES.md` A20 requires architecture when the HTTP contract changes. The previous architecture of `20261126-practical-info-poi-name-body` specified AND and is withdrawn.
- Evidence: not required. The name match rule is already in `docs/context/api-mapping/practical_info_list.md` and `containsPattern`. This change is which predicate is applied, not an unknown data distribution.
- Runtime proof: required. Signal `runtime_proof_required`. The user runs `docker compose` from `runtime-runbook.md` unless a later turn says otherwise.
- Reviewer routing (`WORKFLOW.md` §7): `api-contract-reviewer` because `api/` and `dto/` change. `jpa-performance-reviewer` because the repository SQL changes. `app-security-reviewer` is added before review only if the diff touches `common/web/`. Risk is medium, so `risk-gate` is not required.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Selector poi_name hoặc ids | `poi_name` và `ids` là hai cách chọn POI. Không dùng `poi_name` để lọc giao với `ids`. Chỉ `ids`: chọn theo id, không có vị từ tên. Chỉ `poi_name`: chọn theo tên, không bắt buộc `ids`. Có cả hai: hợp (union), không giao (intersection). Không có selector nào: 422. `poi_name` vẫn một chuỗi, tối đa 128, khớp chứa không phân biệt hoa thường, escape `%`, `_` và `\`. Query `poi_name` không lọc. `GET` và các query còn lại không đổi. | `request.md` Yêu cầu nguyên văn | 2026-11-26 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: missing
size: 483 bytes

## API

service: services/data-serving-service (rules: services/data-serving-service/AGENTS.md)
test: cd services/data-serving-service && mvnw.cmd -q -B test  (JDK 26, Docker)
jdk: 26 | docker: up
runtime: user-run docker compose per runtime-runbook.md (D-12)

## FILES

- architecture.md | 483 bytes | placeholder
- decision.md | 1619 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- request.md | 3934 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 2465 bytes

## NEXT

python scripts/vv.py run-gate 20261126-practical-info-poi-name-or-ids
