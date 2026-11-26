# Architect handoff: 20261125-practical-info-query-legacy-poi-id

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261125-practical-info-query-legacy-poi-id --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261125-practical-info-query-legacy-poi-id/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261125-practical-info-query-legacy-poi-id | phase=triage

## STATE

id: 20261125-practical-info-query-legacy-poi-id
title: Practical info query and legacy poi_id
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: cross_system, design_tradeoffs, runtime_proof_required, data_model_change
gates: evidence=not_required, architecture=pending, local_verification=pass, specialist_review=fix_required, risk_gate=fix_required, runtime=pending
rounds: verification=2, review=2, architecture=1, runtime_failure=0
reviewers: api-contract-reviewer, app-security-reviewer, jpa-performance-reviewer
open findings: JPA-002 P1
exceptions: none
scope.files:
- sql/postgres/gld_srv_serve.pg.sql
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiLegacyIdMap.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepository.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiIdResolver.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiSpecifications.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiMediaGalleryRepository.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PracticalInfoQuery.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PracticalInfoSearchRequest.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PracticalInfoProjection.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PracticalInfoListEnvelope.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/common/web/PracticalInfoBodyLimitFilter.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryCustom.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryImpl.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/common/web/PracticalInfoBodyLimitFilterTest.java
- tests/test_srv_poi_serving_contract.py
- tests/test_srv_poi_api_mapping_required.py
- docs/context/api-mapping/practical_info_list.md
- docs/context/api-mapping/practical_info.md
- docs/context/api-mapping/gallery.md
- docs/context/api-mapping/reviews.md
- docs/context/api-mapping/experiences.md
- docs/context/api-mapping/amenities.md
- docs/context/api-mapping/compact.md
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/domain/repository/PoiRepositoryIntegrationTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/LegacyAndPracticalInfoIntegrationTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/PoiControllerIntegrationTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/dto/PracticalInfoProjectionTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java
- +5 more

## VALIDATION

PASS

## RESUME

# Resume

Status: user_decision

Done this session:
- D-LEGACY-MAP accepted. Implemented POST /api/v1/pois/practical_info, legacy id resolution, mapping docs, and tests.
- Verify PASS twice (maven with Docker, not skipped). rounds.verification is 2.
- Review round 1 FIX_REQUIRED: API-001, SEC-001, JPA-001 fixed.
- Review round 2 FIX_REQUIRED: JPA-002 only. arrayContains emits `? @> ARRAY[column]`. Reviewer wants `scalar = ANY(:ids)`.
- rounds.review is 2. No third review or verify fits task-state caps.

Next action:
- If the user accepts the risk, record JPA-002 as accepted-risk, clear that open finding, and move to waiting_runtime. Do not mark specialist_review pass unless the disposition is recorded.
- If the user wants the ANY() predicate, stop until the verification cap can record another verify. Do not increment rounds.verification past 2.
- Runtime remains the user's docker compose runbook. Main does not run compose.

Read next:
- .ai/tasks/20261125-practical-info-query-legacy-poi-id/reviews/round-2.md — JPA-002
- .ai/tasks/20261125-practical-info-query-legacy-poi-id/decision.md — Xử lý findings
- .ai/tasks/20261125-practical-info-query-legacy-poi-id/runtime-runbook.md

Waiting on: user decision for JPA-002, and whether the list endpoint stays POST or becomes GET with comma-separated ids. Recommendation: keep POST; change the predicate to column = ANY(:ids) only after the user authorizes one more verify cycle, because rounds.verification is already 2.

## REQUEST

# Request

## User outcome

Redesign `GET /api/v1/pois/{poi_id}/practical_info`. A new endpoint based on this one is allowed. Choose the option with the best fit and performance. Every `/api/v1/pois/**` endpoint returns the same mapped record for a legacy `poi_id` and for the new-model `poi_id`.

## Requirements (verbatim)

1. Thiết kế lại GET /api/v1/pois/{poi_id}/practical_info. Được tạo endpoint mới dựa trên endpoint này. Chọn phương án tối ưu và hiệu năng tốt.
   - id nhập được với biên dưới 0 và biên trên 500.
   - Thêm query required_fields. Không nhập thì trả toàn bộ field như hiện tại. Có nhập thì chỉ trả các field được chọn. Danh sách được chọn là phần detail của response hiện tại (các field data.* trong docs/context/api-mapping/practical_info.md). Không thêm field ngoài danh sách đó.
   - Thêm query source (partner hoặc google), lang, poi_name. lang đã có trên endpoint này; giữ cách resolve hiện tại.
   - Thêm phân trang page, size. meta của response có pagination tương ứng envelope hiện có (mẫu reviews).
   - Thêm sort_field (đúng một field) và sort_order (asc hoặc desc).
2. Mọi API: poi_id model cũ hoặc model mới đều trả được dữ liệu. Data poi_id model cũ đã được map sang model mới và khớp data model mới. Không bịa công thức poi_id thứ hai.

## Scope

### In scope

- `scope.systems`: `poi-serving-api`
- HTTP contract for practical info: `required_fields`, `source`, `lang`, `poi_name`, `page`, `size`, `sort_field`, `sort_order`, and an `id` input whose lower bound is 0 and upper bound is 500.
- Legacy and new `poi_id` on every `/api/v1/pois/**` endpoint, using the existing map. No second `poi_id` formula.
- API mapping docs updated before review. Tests named by the acceptance criteria.

### Out of scope

- Inventing a second `poi_id` formula.
- Adding a column, table, or key from the API side. If PostgreSQL DDL and the entity lack a legacy `poi_id` key, set `data_model_change` and do not patch the entity to fill the gap.
- Assigning the 0 and 500 bounds to `poi_id` (UUID text) or to `size`.
- Reading `docs/poi-serving-api/`, `notebooks_lgc/`, or pipeline manifests.
- Copying credentials or hosts into the repo or task artifacts.
- Commit. `docker compose`. Fabric DEV probes unless correctness depends on data that is not in the repo.

## Acceptance criteria

- Hợp đồng HTTP, JSON, lỗi, phân trang và lang khớp entity và gold contract (tests/test_srv_poi_serving_contract.py).
- required_fields rỗng hoặc vắng mặt trả đủ field detail như practical_info hiện tại. Có giá trị thì chỉ các field nằm trong whitelist detail.
- source chỉ nhận partner và google. sort_field chỉ một field trong whitelist sort. sort_order chỉ asc hoặc desc.
- page và size đi cùng meta.pagination. Trần size giữ theo AGENTS.md của service (size ≤ 100) trừ khi architecture ghi lệch và decision.md đã nhận.
- Mọi endpoint /api/v1/pois/** nhận poi_id cũ và poi_id mới, cùng một bản ghi đã map.
- Tài liệu mapping API được cập nhật trước review.
- Verify PASS trước review. P0/P1 của review được xử lý trong cap 2 vòng.

## Constraints

- API theo gold. Không thêm cột, bảng, khóa từ phía API. Thiếu khóa poi_id cũ trong DDL postgres và entity thì bật data_model_change, không sửa entity cho đủ.
- Không đọc docs/poi-serving-api/, notebooks_lgc/, manifest pipeline.
- Không chép credential hay host vào repo hay artifact.
- Không commit. Không chạy docker compose. Runtime để người dùng chạy theo runtime-runbook.md.
- Fast lane không áp dụng: có đổi hành vi và hợp đồng HTTP.
- id biên 0 và 500: D-ID-UNIT quyết định đây là số lượng giá trị `poi_id` trong một request, tối thiểu 1 và tối đa 500. Không phải miền số, không phải độ dài chuỗi, không phải `size` phân trang.
- Grain hiện tại của practical_info là một POI, một object, không có meta.pagination. Phân trang, source, poi_name và sort chỉ đứng trên response danh sách. Architect chọn giữ GET một POI và thêm endpoint danh sách, hoặc đổi endpoint hiện tại. Main không chọn trước.
- poi_id cũ: dùng map đã có trong mapping_legacy_gold_to_gld_srv.md. Nếu apps.srv_poi_* và gld_srv_serve.pg.sql chưa có khóa để resolve id cũ, viết handoffs/author-input.md và chạy python scripts/vv.py run-author --kind model (effort medium) trước Architect. Main không viết model-design.md.
- Evidence chỉ khi đúng/sai phụ thuộc dữ liệu chưa có trong repo. Không đoán tỉ lệ null, uniqueness hay dạng id cũ trên DEV.

## Classification rationale

- Complexity: high. Signals `design_tradeoffs` (keep the single-POI GET and add a list endpoint, or change the current endpoint; `poi_name` filter; sort whitelist) and `data_model_change` (serving PostgreSQL has no legacy key).
- Risk: high. Signal `cross_system`: legacy identity is `gld_poi_legacy_id_map` in `docs/context/mapping_legacy_gold_to_gld_srv.md` and `ref_poi_legacy_id` / `legacy_poi_id` in `docs/context/01_DATA_MODEL.md` §6.1 and §8. `sql/postgres/gld_srv_serve.pg.sql` and `apps.srv_poi_*` only key `poi_id`. A key change crosses gold and the serving API. `risk-gate` is required.
- Architecture: required. HTTP contract change and more than one viable implementation. Grain is an Architect choice. Main does not choose it in triage.
- Evidence: not required. The missing key and the published map are in the repository. The unbound unit of `id` is a user decision, not a data probe. Do not infer null rate, uniqueness, or the shape of legacy ids on DEV.
- Runtime proof: required. Behavior and the HTTP contract change. The service rule is a user-run `docker compose` smoke in `runtime-runbook.md`. Signal `runtime_proof_required`. Main does not run compose.
- Reviewer routing: `api-contract-reviewer` (paths, DTO, errors, paging, `lang`). `jpa-performance-reviewer` (the change touches `PoiService`, `PoiSpecifications`, and may touch an entity after the model). `app-security-reviewer` (`required_fields` and `sort_field` are request input that must stay on a whitelist, not dynamic JPQL built from raw strings).
- `id` bounds: `GET /{poi_id}/practical_info` takes only path `poi_id` and query `lang`. Serving DDL numeric columns (`rating_overall`, `rating_count`, `review_count`, `display_order`, `width_px`, `height_px`) have no 0..500 domain. Text columns have no length 500. Controller bounds that do exist are `page` `@Min(0)`, `size` `@Max(100)`, and other `@Size` caps (20, 64, 128). None is the pair 0 and 500. Stop for the unit before `run-gate`.
- Legacy key: confirmed absent from `sql/postgres/gld_srv_serve.pg.sql` and from Java entities. Model author runs after this decision, before the Architect. Main does not write `model-design.md`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-ID-UNIT | Số `poi_id` một request được nhập | Ý tôi là có thể nhập min 1 poi_id và max là 500 poi_id, không phải lấy khoảng số hay độ dài | Quyết định của người dùng | 2026-11-25 |
| D-LEGACY-MAP | Bảng map serving và job copy | Đồng ý cả 4. (a) Tên bảng `apps.srv_poi_legacy_id_map`, và được mirror bảng gold ngoài họ `gld_srv_*` vào schema `apps`. (b) Khóa chính `legacy_poi_id` lấy từ MERGE key của `lgpmain`, không lấy từ NodeSpec. (c) Phía data sở hữu job copy: copy đủ 1:1 mọi dòng gold map, kể cả dòng không `OK`, trong một transaction. API chỉ đọc và lọc `OK`. (d) `services/data-serving-service/AGENTS.md` mở từ năm bảng thành sáu bảng. | Quyết định của người dùng | 2026-11-25 |
| D-ANY | Predicate resolve và lọc id | Đồng ý sửa qua ANY(:ids). Chấp nhận thêm một vòng sửa, verify và review. | Quyết định của người dùng | 2026-11-25 |
| D-PERF | Vòng architecture hiệu năng | Cần quét thêm một vòng architecture để tối ưu hiệu năng vì endpoint này nhiều request và cần phản hồi nhanh | Quyết định của người dùng | 2026-11-25 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| API-001 | P1 | fixed | POST practical_info khai báo envelope 200/400/401/415/422/500. Schema 200 là PracticalInfoListEnvelope. | |
| SEC-001 | P1 | fixed | PracticalInfoBodyLimitFilter chặn body trước Jackson: Content-Length vượt trần không đọc stream; chunked dừng ở trần. Test filter và MockMvc oversized. | |
| JPA-001 | P1 | fixed | Resolve và lọc poi_id dùng arrayContains, không IN. Page lang/cover chỉ IN id của trang, size ≤ 100. Test 120 id: tối đa 5 câu SQL và mỗi câu ≤ 100 placeholder. | |
| JPA-002 | P1 |  | Người dùng chốt D-ANY: sửa sang `cột = ANY(:ids)`, một tham số mảng. D-PERF: vòng architecture thứ hai thiết kế đường nhanh trước khi Main sửa. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: PASS
size: 39497 bytes

## API

service: services/data-serving-service (rules: services/data-serving-service/AGENTS.md)
test: cd services/data-serving-service && mvnw.cmd -q -B test  (JDK 26, Docker)
jdk: 26 | docker: down
runtime: user-run docker compose per runtime-runbook.md (D-12)

## FILES

- architecture.md | 39497 bytes | large: use toc/show
- decision.md | 5125 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 14898 bytes
- handoffs/author-input.md | 2371 bytes
- handoffs/review-round-1.md | 1609 bytes
- handoffs/review-round-2.md | 5427 bytes
- model-design.md | 9378 bytes
- request.md | 7147 bytes
- resume.md | 1511 bytes
- reviews/README.md | 157 bytes | placeholder
- reviews/round-1.json | 4726 bytes
- reviews/round-1.md | 1560 bytes
- reviews/round-2.json | 5585 bytes
- reviews/round-2.md | 1302 bytes
- runtime-runbook.md | 3396 bytes
- task-state.yaml | 4647 bytes
- verification/verify.log | 17998 bytes

## NEXT

python scripts/vv.py run-gate 20261125-practical-info-query-legacy-poi-id
