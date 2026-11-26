# Codex review handoff: 20261125-practical-info-query-legacy-poi-id, round 3

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

## Round 2 carry-over

`vv.py` generated this block. Use it instead of opening past review files. Re-check each round-2 P0/P1 against its disposition, then review only the changed files below for regressions caused by the fixes.

### Round 2 P0/P1 findings

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| JPA-002 | P1 | `PoiSpecifications.java:45`; `SrvPoiLegacyIdMapRepositoryImpl.java:33` | `arrayContains(idsArray, scalarColumn)` sinh dạng `? @> ARRAY[column]`, không tạo access path trực tiếp qua B-tree PK và có nguy cơ quét cả hai bảng khi tải đồng thời tăng. | Đổi cả hai predicate sang `scalar_column = ANY(:ids)` với một PostgreSQL array parameter; giữ tối đa 5 statement và không tạo `IN` quá 100 phần tử. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| JPA-002 | P1 |  | Người dùng chốt D-ANY: sửa sang `cột = ANY(:ids)`, một tham số mảng. D-PERF: vòng architecture thứ hai thiết kế đường nhanh trước khi Main sửa. | |

### Files changed since round 2

- services/data-serving-service/AGENTS.md | modified
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryCustom.java | modified
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryImpl.java | modified
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiIdResolver.java | modified
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java | modified
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiSpecifications.java | modified
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PracticalInfoQuery.java | modified
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/domain/repository/PoiRepositoryIntegrationTest.java | modified
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/LegacyAndPracticalInfoIntegrationTest.java | modified
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java | modified
