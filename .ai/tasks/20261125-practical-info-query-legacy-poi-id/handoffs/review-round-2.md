# Codex review handoff: 20261125-practical-info-query-legacy-poi-id, round 2

You are the VSVN Review Coordinator. Use the project agents in `.codex/agents/`.

Confirm the active model is `gpt-5.6-sol` with `medium` reasoning. Stop and report a model mismatch instead of silently substituting.

Read `architecture.md` when it exists, the open items in `decision.md`, and the implementation diff. Do not read the rest of the repository, past reviews, or evidence files unless one finding depends on a named path.

For round 1, invoke every reviewer named in `review_plan.required_reviewers` independently. Spawn each project custom agent without a full-history fork and without another specialist's findings. For round 2, use the generated round-1 carry-over at the end of this prompt: pass each specialist only the round-1 P0/P1 findings it owns, their dispositions, and the diff of the files listed as changed since round 1 (`git diff -- <path>`, or the file itself when untracked). Invoke `risk-gate` after the specialist results when task state requires it. Risk-gate reads those findings and the diff, not the whole repository.

Specialists are read-only. Do not edit repository files.

Return one short consolidated Markdown report:

1. Model and reviewer manifest.
2. Gate verdict: `PASS`, `FIX_REQUIRED`, `EVIDENCE_REQUIRED`, or `USER_DECISION`.
3. Deduplicated P0/P1 findings: ID, severity, `file:line`, one-sentence failure, one-sentence fix.
4. P2/P3 as a count.
5. One probe line when evidence is missing.

Do not promote style issues to P0/P1. Do not write a repository tour.

## Round 1 carry-over

`vv.py` generated this block. Use it instead of opening past review files. Re-check each round-1 P0/P1 against its disposition, then review only the changed files below for regressions caused by the fixes.

### Round 1 P0/P1 findings

- `API-001` — P1 — `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java:141`: OpenAPI của endpoint mới thiếu các response thực tế và dùng `List<Object>`, khiến client nhận contract không định kiểu và thiếu error schemas. Khắc phục bằng cách khai báo shared envelopes cho `200/400/401/415/422/500` và success schema/projection có kiểu rõ ràng.
- `SEC-001` — P1 — `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java:144`: Bean validation chạy sau khi Jackson materialize body không giới hạn byte, nên request xác thực quá lớn có thể gây áp lực heap trước khi bị từ chối. Khắc phục bằng giới hạn byte trước deserialization cho cả fixed-length và chunked body, kèm test oversized request.
- `JPA-001` — P1 — `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiIdResolver.java:37`: Resolver đưa tối đa 500 ID vào một repository `IN`, vi phạm giới hạn 100 ID mỗi repository call và tạo rủi ro hiệu năng. Khắc phục để mọi `IN` call không quá 100 ID nhưng vẫn giữ tổng số SQL không quá 5, đồng thời test cả hai invariant.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| API-001 | P1 | fixed | POST practical_info khai báo envelope 200/400/401/415/422/500. Schema 200 là PracticalInfoListEnvelope. | |
| SEC-001 | P1 | fixed | PracticalInfoBodyLimitFilter chặn body trước Jackson: Content-Length vượt trần không đọc stream; chunked dừng ở trần. Test filter và MockMvc oversized. | |
| JPA-001 | P1 | fixed | Resolve và lọc poi_id dùng arrayContains, không IN. Page lang/cover chỉ IN id của trang, size ≤ 100. Test 120 id: tối đa 5 câu SQL và mỗi câu ≤ 100 placeholder. | |

### Files changed since round 1

- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java | modified
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PracticalInfoListEnvelope.java | entered the diff after round 1
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/common/web/PracticalInfoBodyLimitFilter.java | entered the diff after round 1
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepository.java | modified
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryCustom.java | entered the diff after round 1
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryImpl.java | entered the diff after round 1
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiSpecifications.java | modified
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/PoiControllerIntegrationTest.java | modified
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/common/web/PracticalInfoBodyLimitFilterTest.java | entered the diff after round 1
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/CountingStatementInspector.java | modified
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/LegacyAndPracticalInfoIntegrationTest.java | modified
