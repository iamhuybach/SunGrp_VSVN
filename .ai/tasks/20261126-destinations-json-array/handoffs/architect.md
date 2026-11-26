# Architect handoff: 20261126-destinations-json-array

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261126-destinations-json-array --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261126-destinations-json-array/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261126-destinations-json-array | phase=triage

## STATE

id: 20261126-destinations-json-array
title: Parse destinations id and name into JSON arrays
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
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/CompactPoiResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiPracticalInfoResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/PoiControllerIntegrationTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java
- docs/context/api-mapping/compact.md
- docs/context/api-mapping/practical_info.md
- docs/context/api-mapping/practical_info_list.md

## VALIDATION

PASS

## REQUEST

# Request

## User outcome

`destinations.id` and `destinations.name` in the POI serving API are JSON arrays of strings. A stored text value that is already a JSON array is parsed. The response no longer wraps that array in a string.

## Scope

### In scope

- `CompactPoiResponse.Destinations`, used by compact and practical info, including `POST /api/v1/pois/practical_info`.
- The mapping from `apps.srv_poi_info.destination_id` and `destination_name`.
- Tests and `docs/context/api-mapping/compact.md`, `practical_info.md`, and `practical_info_list.md`.
- `scope.systems`: `poi-serving-api`.

### Out of scope

- Gold columns, tables, and keys. The columns stay `text`.
- `docs/poi-serving-api/`.
- Fast lane. The HTTP response shape changes.

## Yêu cầu nguyên văn

Vậy hãy sửa như bạn khuyến nghị.

Khuyến nghị đã chốt: parse `destination_id` và `destination_name` thành mảng JSON. `null` hoặc chuỗi rỗng vẫn là `null`. Không xóa ký tự `\` trong chuỗi. Không bịa mảng khi giá trị không phải mảng JSON.

## Acceptance criteria

- A column value `["a","b"]` is returned as a JSON array `["a","b"]`, not as a string.
- `null` and blank text become JSON `null`.
- A value that is not a JSON array becomes JSON `null`. The list or detail request still returns 200. Do not invent elements.
- An array element that is not a JSON string becomes JSON `null` for that field. Do not coerce numbers or objects into strings.
- Compact and practical info use the same shape.
- The mapping docs show `id` and `name` as arrays before review.

## Constraints

- The API follows gold. Do not add columns, tables, or keys.
- Do not read `docs/poi-serving-api/`.
- Do not copy credentials or hosts into the repository or task artifacts.
- Do not commit. Do not run `docker compose` unless the user asks in the current turn.

## Classification rationale

- Complexity: medium. One shared DTO and the two service mappings change, plus tests and three mapping docs. No SQL or grain change.
- Risk: medium. Clients that read `destinations.id` as a string must read an array. Rollback is reverting the DTO.
- Architecture: required. A20 requires architecture when the HTTP contract changes.
- Evidence: not required. The user sample shows a JSON array stored in the text column, and `gld_srv_serve.pg.sql` types both columns as `text`.
- Runtime proof: required. Signal `runtime_proof_required`.
- Reviewer routing: `api-contract-reviewer` because `api/dto` changes. `jpa-performance-reviewer` because `service/PoiService` changes. `app-security-reviewer` only if the diff touches `common/web/`. Risk is medium, so `risk-gate` is not required.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | destinations là mảng | `destinations.id` và `destinations.name` là mảng chuỗi JSON. `null` hoặc chuỗi rỗng thành `null`. Chuỗi là mảng JSON thì parse. Không phải mảng JSON, hoặc phần tử không phải chuỗi JSON, thì field đó là `null` và request vẫn 200. Không xóa ký tự `\`. Không bịa phần tử. Compact và practical info dùng cùng hình. | `request.md` Yêu cầu nguyên văn | 2026-11-26 |

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
- decision.md | 1319 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- request.md | 2734 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1930 bytes

## NEXT

python scripts/vv.py run-gate 20261126-destinations-json-array
