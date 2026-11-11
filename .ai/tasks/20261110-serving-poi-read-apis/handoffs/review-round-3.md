# Codex review handoff: 20261110-serving-poi-read-apis, round 3

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
| SEC-001 | P1 | `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiPracticalInfoResponse.java:25` | Unvalidated database text emitted through `@JsonRawValue` can produce malformed response JSON or inject sibling properties. | Validate the stored value into a Jackson `JsonNode`, preserve its JSON content, degrade invalid input to JSON `null`, and add malformed/injection regression tests. |
| API-003 | P1 | `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiPracticalInfoResponse.java:25` | The Java `String` type makes generated OpenAPI describe `holiday_exceptions` as a string although the endpoint emits JSON array/null. | Declare an explicit nullable array/free-form-item OpenAPI schema and assert the field schema through `/v3/api-docs`. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SEC-001 | P1 | fixed | Kiểm tra đúng một giá trị JSON. Hợp lệ thì ghi đúng text. Hỏng hoặc có token thừa thì null. Không log nội dung. | |
| API-003 | P1 | fixed | Schema OpenAPI của holiday_exceptions không còn là string. | |

### Files changed since round 2

- docs/context/api-mapping/compact.md | modified
- docs/context/api-mapping/practical_info.md | modified
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiPracticalInfoResponse.java | modified
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java | modified
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/util/StoredJsonParser.java | modified
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/DataServingApplicationTests.java | entered the diff after round 2
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java | modified
- tests/test_srv_poi_api_mapping_required.py | modified
