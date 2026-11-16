# Architect handoff: 20261116-poi-api-dev-auth

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261116-poi-api-dev-auth --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261116-poi-api-dev-auth/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261116-poi-api-dev-auth | phase=triage

## STATE

id: 20261116-poi-api-dev-auth
title: Bearer token for /api/v1/pois
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: design_tradeoffs, runtime_proof_required
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: app-security-reviewer, api-contract-reviewer
open findings: none
exceptions: none
scope.files:
- services/data-serving-service/AGENTS.md
- services/data-serving-service/pom.xml
- services/data-serving-service/docker-compose.yml
- services/data-serving-service/.env.example
- services/data-serving-service/.gitignore
- services/data-serving-service/k8s/configmap.yaml
- services/data-serving-service/src/main/resources/application.yml
- services/data-serving-service/src/test/resources/application.yml
- services/data-serving-service/src/test/resources/poi-api-bearer-token.txt
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/config/OpenApiConfig.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/config/SecurityConfig.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/config/ApiBearerTokenProperties.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/common/web/GlobalExceptionHandler.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/common/web/RequestIdFilter.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/common/web/BearerTokenAuthenticationEntryPoint.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/PoiControllerIntegrationTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/DataServingApplicationTests.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/common/web/GlobalExceptionHandlerTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/common/web/RequestIdFilterTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/config/ApiBearerAuthTest.java
- docs/context/api-mapping/compact.md
- docs/context/api-mapping/gallery.md
- docs/context/api-mapping/reviews.md
- docs/context/api-mapping/features.md
- docs/context/api-mapping/experiences.md
- docs/context/api-mapping/practical_info.md
- docs/context/api-mapping/amenities.md

## VALIDATION

PASS

## REQUEST

# Request

## User outcome

Every endpoint under `/api/v1/pois` rejects a call that has no `Authorization` header, a scheme other than Bearer, or a token that does not match the configured secret, with HTTP 401 and the existing `GlobalExceptionHandler` error envelope. A request with `Authorization: Bearer <token>` continues with the same status and body as today. `GET /actuator/health` stays open with no token. A blank or missing token configuration does not open `/api`. The secret is never logged and never returned in a response body.

## Scope

### In scope

- One shared environment variable for local dev and Kubernetes deploy, declared in `services/data-serving-service/src/main/resources/application.yml` and in a new `services/data-serving-service/.env.example`, both with an empty value.
- Local dev: `services/data-serving-service/.env` (already gitignored) receives one generated random token. `docker-compose.yml` passes that variable through from `.env` and does not hard-code a token.
- Deploy: one Kubernetes ConfigMap manifest whose data is a placeholder, not the generated token, and which references the same variable name.
- Constant-time comparison of the presented token with the configured value.
- Java tests use a fixed token stored under `services/data-serving-service/src/test/resources`. Tests do not read `.env`.
- Request-header tables in `docs/context/api-mapping/compact.md`, `gallery.md`, `reviews.md`, `features.md`, `experiences.md`, `practical_info.md`, and `amenities.md`: add `Authorization` with Required = `có`. Do not change the Required value of any other field.
- `scope.systems`: `poi-serving-api`.

### Out of scope

- Query text, business DTOs, entities, gold columns, and PostgreSQL DDL.
- Files under `docs/poi-serving-api/`.
- Mapping files whose names start with `(ood)`.
- Task `20261110-serving-poi-read-apis`.
- Committing `.env`, or committing any change in this task until the user asks.
- Writing the generated token into `request.md`, `decision.md`, `resume.md`, mapping docs, tests, the verify log, or `evidence/`.

## Acceptance criteria

- For each current `/api/v1/pois` endpoint (compact, features, gallery, reviews, experiences, practical_info, amenities): missing token and wrong token return HTTP 401 with the existing error envelope; the correct Bearer token keeps the status the endpoint had before this change.
- `GET /actuator/health` returns without a token.
- `python scripts/vv.py verify 20261116-poi-api-dev-auth` passes when Docker is available.
- Reviewers: `app-security-reviewer` and `api-contract-reviewer`.
- `.env` is not committed. The generated token appears only in `.env` and once in the final chat message.

## Constraints

- Do not log the token and do not put it in the response body.
- Compare tokens in constant time.
- A blank or absent configuration must not let `/api/v1/pois` succeed. `GET /actuator/health` must still respond without a token, including when the token is blank, because the healthcheck calls that path. Paths outside `/api/v1/pois` keep their current unauthenticated behavior unless a listed file must change to keep health and the POI routes apart.
- The 401 body is the existing `ApiResponse` error envelope from `GlobalExceptionHandler` (`success`, `code`, `message`, `data`, `meta`, `errors`). `meta` still carries `trace_id` from `RequestIdFilter`.
- One variable name for dev and deploy. `.env.example` and the ConfigMap data value are empty or a non-secret placeholder. The random token is written only to the gitignored `.env`.
- Tests must not read `.env`. The fixed test token lives under `src/test/resources`.
- Do not read `services/data-serving-service/.env` into an artifact. It may already hold local database secrets.
- No `data_model_change`. Do not change query, business DTO, or DDL.
- Runtime proof is a user-run `docker compose` smoke. Main stops before that command. The runbook covers loading `.env`, one POI call with no token, one with a wrong token, one with the correct token, and `GET /actuator/health`.

## Classification rationale

- Complexity: `medium`. The change adds an auth boundary on every POI route, a new Kubernetes manifest, compose wiring, and seven mapping tables. It is still one service and one comparison.
- Risk: `medium`. HTTP behavior changes on every POI endpoint, rollback is removing the filter and the variable, and local tests can prove 401 versus the previous success status. It is not high: there is no CDC, watermark, lock, or data-loss path.
- Architecture: required. The HTTP contract changes, and the same secret is attached in two ways (gitignored `.env` for dev, ConfigMap for deploy). Material design choices remain: how a filter or `SecurityFilterChain` renders the existing envelope (controller advice does not see a filter rejection), how a blank secret closes `/api` while `/actuator/health` stays up, and which paths stay anonymous. `design_tradeoffs` applies. The edit set is also more than eight source files. `data_model_change` does not apply.
- Evidence: not required. Correctness is the configured string and the HTTP contract, both provable from the repository and deterministic tests. No Fabric probe.
- Runtime proof: required. Acceptance includes a user-run compose smoke. `runtime_proof_required` applies. Main does not run `docker compose`.
- Reviewer routing: `app-security-reviewer` because the diff touches `common/web/`, `config/`, `application.yml`, `pom.xml`, and Docker or Kubernetes files. `api-contract-reviewer` because the HTTP status and error envelope of `/api/v1/pois` change and the mapping tables change. `jpa-performance-reviewer` is not required: no repository, service query, entity, or DDL edit. `risk-gate` is not required at `medium` risk.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|

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
- decision.md | 721 bytes | placeholder
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- request.md | 5812 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 3287 bytes

## NEXT

python scripts/vv.py run-gate 20261116-poi-api-dev-auth
