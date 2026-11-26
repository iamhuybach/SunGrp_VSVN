# Architect handoff: 20261126-practical-info-poi-name-body

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261126-practical-info-poi-name-body --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261126-practical-info-poi-name-body/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261126-practical-info-poi-name-body | phase=triage

## STATE

id: 20261126-practical-info-poi-name-body
title: Move practical_info poi_name from query string to JSON body
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: runtime_proof_required
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: api-contract-reviewer, app-security-reviewer
open findings: none
exceptions: none
scope.files:
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PracticalInfoSearchRequest.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PracticalInfoQuery.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/common/web/PracticalInfoBodyLimitFilter.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryImpl.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/PoiControllerIntegrationTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/LegacyAndPracticalInfoIntegrationTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/common/web/PracticalInfoBodyLimitFilterTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/domain/repository/PoiRepositoryIntegrationTest.java
- docs/context/api-mapping/practical_info_list.md

## VALIDATION

PASS

## REQUEST

# Request

## User outcome

`POST /api/v1/pois/practical_info` accepts `poi_name` in the JSON body next to `ids`, applies both filters together, and no longer filters on the `poi_name` query parameter. `GET /api/v1/pois/{poi_id}/practical_info` stays unchanged.

## Scope

### In scope

- `POST /api/v1/pois/practical_info`: move `poi_name` from the query string into the JSON body, beside `ids`.
- Validation, body-size ceiling, mapping doc `docs/context/api-mapping/practical_info_list.md`, and tests for that contract.
- `scope.systems`: `poi-serving-api`.

### Out of scope

- `GET /api/v1/pois/{poi_id}/practical_info`.
- Query parameters `required_fields`, `source`, `lang`, `page`, `size`, `sort_field`, `sort_order`.
- Gold schema, new columns, tables, or keys.
- `docs/poi-serving-api/`.
- Fast lane. An HTTP contract change is in scope.

## Yêu cầu nguyên văn

POST /api/v1/pois/practical_info thay đổi:
- Đưa poi_name vào Body Request giống ids. Để có thể query theo cả body và poi_name.

Diễn giải đã chốt cho hợp đồng hiện tại:
- Body JSON hiện chỉ có ids. poi_name đang là query, chuỗi, không bắt buộc, tối đa 128, rỗng thì không lọc, khớp không phân biệt hoa thường trên apps.srv_poi_info.poi_name, escape %, _ và \.
- Chuyển poi_name vào body, cùng cấp với ids. Vẫn một chuỗi, không thành mảng. Bỏ query poi_name.
- ids giữ nguyên: bắt buộc, 1 đến 500 chuỗi, mỗi chuỗi không rỗng, dài tối đa 128.
- Một request lọc bằng cả ids và poi_name. poi_name rỗng hoặc vắng thì chỉ lọc theo ids, đúng hành vi hiện tại.
- GET /api/v1/pois/{poi_id}/practical_info không đổi. required_fields, source, lang, page, size, sort_field, sort_order giữ là query.

Tiêu chí nghiệm thu:
- POST nhận {"ids":[...], "poi_name":"..."} và áp cả hai điều kiện.
- Query poi_name không còn tác dụng lọc.
- Trần và cách khớp poi_name giữ như docs/context/api-mapping/practical_info_list.md.
- ids vẫn 422 khi rỗng hoặc quá 500. poi_name dài hơn 128 thì 422.
- PracticalInfoBodyLimitFilter vẫn chặn body quá lớn trước khi gọi service, và vẫn đủ chỗ cho 500 id cộng poi_name tối đa.
- docs/context/api-mapping/practical_info_list.md cập nhật trước review: poi_name sang mục Request body, sample request đổi theo.
- Verify PASS trước review. P0/P1 được xử lý trong cap 2 vòng.

## Acceptance criteria

- `POST` accepts `{"ids":[...], "poi_name":"..."}` and applies both conditions.
- A `poi_name` query parameter no longer filters.
- The `poi_name` length ceiling and match rules stay as in `docs/context/api-mapping/practical_info_list.md`.
- `ids` still returns 422 when empty or longer than 500. `poi_name` longer than 128 returns 422.
- `PracticalInfoBodyLimitFilter` still rejects an oversized body before the service runs, and the ceiling still fits 500 ids plus a maximum-length `poi_name`.
- `docs/context/api-mapping/practical_info_list.md` is updated before review: `poi_name` moves to the Request body section and the sample request matches.
- Local verification PASS before review. P0/P1 findings are handled within two review rounds.

## Constraints

- The API follows gold. Do not add columns, tables, or keys.
- Do not read `docs/poi-serving-api/`.
- Do not copy credentials or hosts into the repository or task artifacts.
- Do not commit. Do not run `docker compose`. The user runs runtime steps from `runtime-runbook.md`.
- Fast lane does not apply: the HTTP contract changes.

## Classification rationale

- Complexity: medium. The change moves one filter across the controller, request DTO, query object, body-limit filter, tests, and the mapping doc. No concurrency, CDC, watermark, or grain change.
- Risk: medium. Bounded HTTP behavior change. Rollback is reverting the endpoint. Local tests can prove the contract. `WORKFLOW.md` §5 low is a change with no behavior change or a narrower local proof; this changes which request part filters `poi_name`.
- Architecture: required. `docs/AGENT_PROMPT_SAMPLES.md` A20 requires architecture when the HTTP contract changes. Evidence does not block architecture: the match rule is already in the mapping doc and the repository.
- Evidence: not required. Correctness of the existing `poi_name` match (case-insensitive, escape `%`, `_`, and `\`) is already written in `docs/context/api-mapping/practical_info_list.md` and the repository. Local tests can prove the new binding.
- Runtime proof: required. The user runs `docker compose` from `runtime-runbook.md`. Signal: `runtime_proof_required`.
- Reviewer routing (`WORKFLOW.md` §7): `api-contract-reviewer` because the diff touches `api/` and `dto/`. `app-security-reviewer` because the acceptance criterion names `PracticalInfoBodyLimitFilter` under `common/web/`. `jpa-performance-reviewer` is added before review only if the diff touches `domain/repository/` or SQL. Risk is medium, so `risk-gate` is not required.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Hợp đồng poi_name | `poi_name` chuyển từ query sang body JSON, cùng cấp với `ids`, vẫn một chuỗi. Query `poi_name` bị bỏ. Rỗng hoặc vắng thì chỉ lọc theo `ids`. Trần 128 và cách khớp giữ như mapping hiện tại. `GET` và các query còn lại không đổi. | `request.md` Yêu cầu nguyên văn | 2026-11-26 |

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
- decision.md | 1320 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- request.md | 5124 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 2594 bytes

## NEXT

python scripts/vv.py run-gate 20261126-practical-info-poi-name-body
