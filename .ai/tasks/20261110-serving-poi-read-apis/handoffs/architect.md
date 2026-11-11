# Architect handoff: 20261110-serving-poi-read-apis

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261110-serving-poi-read-apis --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261110-serving-poi-read-apis/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261110-serving-poi-read-apis | phase=triage

## STATE

id: 20261110-serving-poi-read-apis
title: POI serving read API contract
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: design_tradeoffs, runtime_proof_required
gates: evidence=pass, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: api-contract-reviewer, jpa-performance-reviewer, app-security-reviewer
open findings: none
exceptions: none
scope.files:
- docs/context/api-mapping/compact.md
- docs/context/api-mapping/gallery.md
- docs/context/api-mapping/reviews.md
- docs/context/api-mapping/features.md
- docs/context/api-mapping/experiences.md
- docs/context/api-mapping/practical_info.md
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/common/web/GlobalExceptionHandler.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/common/web/GlobalExceptionHandlerTest.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/CompactPoiResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiGalleryItemResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiReviewItemResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/CompactPoiRequest.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiFeatureResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiExperiencesResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiPracticalInfoResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiInfoRepository.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiMediaGalleryRepository.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiMultiLangRepository.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/util/StoredJsonParser.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/PoiControllerIntegrationTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/domain/repository/PoiRepositoryIntegrationTest.java
- tests/test_srv_poi_api_mapping_required.py
- sql/postgres/gld_srv_serve.pg.sql

## VALIDATION

PASS

## RESUME

# Resume

## Status

user_decision. D-2, D-3, D-4, and D-6 are recorded. D-5 is open. gates: evidence=pass, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending. rounds.architecture=1.

## Done this session

Recorded the 2026-11-11 choices. Compact `ids` is 1 to 20 items; empty `ids` is an error, read as HTTP 422. Added `app-security-reviewer` and `GlobalExceptionHandler` to scope for D-6. No API code change.

## Next action

After the user places `rating_summary` on `GET /api/v1/pois/{poi_id}/reviews`, record D-5, `transition` to `triage` then `waiting_architecture`, and `run-gate`. One architecture round remains.

## Read next

- `.ai/tasks/20261110-serving-poi-read-apis/decision.md` section `D-2, D-3, D-4, D-6 — người dùng 2026-11-11`
- `.ai/tasks/20261110-serving-poi-read-apis/request.md` section `User outcome`

## Waiting on

D-5 only. No commit unless asked.

## REQUEST

# Request

## User outcome

The six POI serving read APIs return the JSON contract below, and the six mapping files describe that same contract.

1. `POST /api/v1/pois/compact` accepts a JSON body `lang` (string) and `ids` (array of `poi_id` strings). `ids` has 1 to 20 items (user decision D-4, 2026-11-11). A missing or empty `ids`, or more than 20 items, is HTTP 422 `ERR_VALIDATION_FAILED`. Rows are ordered `created_at DESC, poi_id ASC`. `data[].cover.id` comes from `apps.srv_poi_info.cover_id`. `data[].cover.file_key` comes from `apps.srv_poi_info.cover_blob_url` (user decision D-1, 2026-11-10). The response and the mapping omit `data[].cover.blur_hash`, `data[].cover.width`, `data[].cover.height`, `data[].cover.mime_type`, `data[].business_tags.business_sector_label`, and `meta.pagination`. A malformed JSON body is HTTP 400 `ERR_BAD_REQUEST` (user decision D-6, 2026-11-11).
2. `GET /api/v1/pois/{poi_id}/gallery` does not call `validatePoiExists`. Query `page` and `size` are added. Rows are ordered by `display_order` ascending. `data[]` contains only `id`, `file_key`, and `display_order`. `file_key` comes only from `apps.srv_poi_media_gallery.blob_url`. `meta.pagination` uses the reviews envelope shape: `type`, `page`, `per_page`, `total_items`, `total_pages`, `has_next`, `has_prev`.
3. `GET /api/v1/pois/{poi_id}/reviews` does not call `validatePoiExists`. `rating_summary` is a sibling of `data`: one element `{rating_count, rating_avg_score}` (user decision D-5, 2026-11-11). `rating_count` comes from `apps.srv_poi_review.rating_count`. `rating_avg_score` comes from `apps.srv_poi_review.rating_overall`.
4. `GET /api/v1/pois/features` follows `docs/context/api-mapping/features.md` (overview, request header, request param, response, status code, sample request, sample response), after that file is updated so `data[].cover.id` comes from `apps.srv_poi_info.cover_id` and `data[].cover.file_key` comes from `apps.srv_poi_info.cover_blob_url` (user decision D-1, 2026-11-10). Selection follows user decision D-2, 2026-11-11.
5. `GET /api/v1/pois/{poi_id}/experiences` follows `docs/context/api-mapping/experiences.md`, same sections, after that file is updated so `data.items.source` comes from `apps.srv_poi_multi_lang.source_name` (user decision D-1, 2026-11-10).
6. `GET /api/v1/pois/{poi_id}/practical_info` follows `docs/context/api-mapping/practical_info.md`, same sections.

Required-field rule for all six APIs and all six mapping files: the only request field with Required = có is path `poi_id`, except compact body `ids`, which is required with 1 to 20 items (user decision D-4, 2026-11-11). Every other request header and request param stays, keeps its current default, and has Required = không. Missing `lang` and `Accept-Language` resolve to `vi`, as the mapping already states. Compact has no path `poi_id`. Body `lang` has Required = không.

All six success responses use `ApiResponse`, and the six mapping files are updated to that envelope (user decision D-3, 2026-11-11). Features includes full `meta.pagination`.

## Scope

### In scope

- `services/data-serving-service` read endpoints, DTOs, service mapping, and repository queries needed for the six contracts.
- `docs/context/api-mapping/compact.md`, `gallery.md`, `reviews.md`, `features.md`, `experiences.md`, `practical_info.md` (overview, params, response, samples), after lowering Required as above.
- Java tests for the changed endpoints and `tests/test_srv_poi_serving_contract.py` on the maven lane.
- `runtime-runbook.md` for a user-run `docker compose` smoke. Main does not run `docker compose`.

### Out of scope

- Splitting this into one task per API.
- `docs/context/api-mapping/MAPPING_SAMPLE.md`, `amenities.md`, `(ood).summary.md`, `(ood).must-know.md`, `(ood).general-information.md`.
- `docs/poi-serving-api/`.
- Task `20261110-split-api-mapping`.
- New columns, tables, keys, or `ALTER` in this task.
- Credentials or database hosts in the repository.

## Acceptance criteria

- Behavior and JSON match items 1–3 and the three mapping files in items 4–6, after the Required rule above.
- Every named source column exists in `sql/postgres/gld_srv_serve.pg.sql` and the matching entity.
- Changed-endpoint Java tests and `tests/test_srv_poi_serving_contract.py` pass on the maven lane. `gates.local_verification` is `pass` only when `python scripts/vv.py verify` runs with Docker.
- Reviewers: `api-contract-reviewer`. Add `jpa-performance-reviewer` when the diff touches a repository or a query. Add no other reviewer unless routing requires it.

## Constraints

- The API reads gold only through PostgreSQL `apps.srv_poi_*`.
- A missing source column stops the task: record it in `decision.md`, do not invent the column, do not open `ALTER` here.
- Main model is Grok 4.7 Medium. No approved `exceptions` entry.
- Commit only when the user asks in the current turn.

## Classification rationale

- Complexity: medium. Six read-contract changes in one service, with prescribed JSON for compact, gallery, and reviews. Features rotation and fallback are not fully specified in `features.md`.
- Risk: medium. Bounded read-behavior change. Rollback is reverting the API and the six mapping files. Local proof is the maven lane once the column contract is real.
- Architecture: required. The change spans one service and more than eight source files (controller, service, compact/gallery/review DTOs, three new response types, gallery or info repository queries, and the endpoint tests). Features rotation versus fallback is a material design tradeoff (`design_tradeoffs`). No grain, key, or CDC change, so `data_model_change` is not set.
- Evidence: not required to prove the missing columns. `sql/postgres/gld_srv_serve.pg.sql` and the entities already show `apps.srv_poi_media_gallery` has no `cover_id` or `cover_blob_url`, and `apps.srv_poi_multi_lang` has no `source`. Those names exist only as `apps.srv_poi_info.cover_id`, `apps.srv_poi_info.cover_blob_url`, and `apps.srv_poi_multi_lang.source_name`.
- Runtime proof: required after implementation. The user runs `docker compose` from `runtime-runbook.md`. `runtime_proof_required` is set. This session stops before that runbook because the column contract is absent.
- Reviewer routing: `api-contract-reviewer` because the diff touches `api/` and `dto/`. `jpa-performance-reviewer` because the diff touches `service/` and repository queries (gallery page and order, features selection). `app-security-reviewer` stays off the plan: the planned diff does not touch `common/web/`, `config/`, `application*.yml`, `pom.xml`, or Docker files. `risk_level` is medium, so `risk-gate` is not required.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Cột nguồn compact, features, experiences | Compact và Features dùng apps.srv_poi_info.cover_id (data[].cover.id) và apps.srv_poi_info.cover_blob_url (data[].cover.file_key). Experiences lấy source từ apps.srv_poi_multi_lang.source_name. | User, 2026-11-10 | 2026-11-10 |
| D-ARCH-1 | Architecture vòng 1 | RESULT: EVIDENCE_REQUIRED. Do not change code yet. | architecture.md Main brief Decision | 2026-11-10 |
| D-PROBE-1 | Probe P-1 đến P-4 | Probe trên database của .env (phê duyệt 2026-11-10): 292 dòng info còn sống đều partner và is_recommended, rating_overall null. experience là mảng JSON {title, keyword, description}. holiday_exceptions là [] hoặc {date, hours, title, status}. time_to_spend, best_time, cost_vnd là object một khóa. | evidence/results/p-1.txt, p-2.txt, p-3.txt, p-4.txt, p-shape.txt | 2026-11-10 |
| D-2 | Features selection | Đồng ý theo khuyến nghị. Pool chính là is_recommended = true. Fallback là dòng còn lại với rating_overall và rating_count đạt ngưỡng, và source_name khớp rating_source khi param có giá trị. Xoay một POI mỗi business_sector theo thứ tự ưu tiên, rồi page/size cắt chuỗi đó. null và chuỗi trắng bị loại. accommodation chỉ vào kết quả khi client đưa vào business_sector_priority. | User, 2026-11-11 | 2026-11-11 |
| D-3 | Envelope sáu API | Đồng ý theo khuyến nghị. Sửa cả mapping. Cả sáu API dùng ApiResponse như reviews. Features có đủ meta.pagination. | User, 2026-11-11 | 2026-11-11 |
| D-4 | Compact ids | ids Tối thiểu 1, tối đa 20 items, ids rỗng báo lỗi, thứ tự created_at DESC, poi_id ASC. | User, 2026-11-11 | 2026-11-11 |
| D-6 | JSON body hỏng của compact | Đồng ý theo khuyến nghị. HTTP 400, ERR_BAD_REQUEST, sửa GlobalExceptionHandler, thêm app-security-reviewer. | User, 2026-11-11 | 2026-11-11 |
| D-5 | rating_summary của reviews | Đồng ý Mảng rating_summary ngang hàng với data, một phần tử {rating_count, rating_avg_score}. API là GET /api/v1/pois/{poi_id}/reviews. | User, 2026-11-11 | 2026-11-11 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 34840 bytes

## API

service: services/data-serving-service (rules: services/data-serving-service/AGENTS.md)
test: cd services/data-serving-service && mvnw.cmd -q -B test  (JDK 26, Docker)
jdk: 26 | docker: down
runtime: user-run docker compose per runtime-runbook.md (D-12)

## FILES

- architecture.md | 34840 bytes | large: use toc/show
- decision.md | 10568 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/p-1.sql | 692 bytes
- evidence/probes/p-2.sql | 735 bytes
- evidence/probes/p-3.sql | 694 bytes
- evidence/probes/p-4.sql | 1303 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/p-1.txt | 403 bytes
- evidence/results/p-2.txt | 253 bytes
- evidence/results/p-3.txt | 5715 bytes
- evidence/results/p-4.txt | 1429 bytes
- evidence/results/p-shape.txt | 894 bytes
- handoffs/architect.md | 14301 bytes
- request.md | 6733 bytes
- resume.md | 979 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 3684 bytes

## NEXT

python scripts/vv.py run-gate 20261110-serving-poi-read-apis
