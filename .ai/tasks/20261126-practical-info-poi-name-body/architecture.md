RESULT: PASS

## Main brief

### Decision
- `poi_name` moves into `PracticalInfoSearchRequest` as `@JsonProperty("poi_name") @Size(max = 128) String poiName`, at the same level as `ids` (option A). The `@RequestParam("poi_name")` is deleted, so a query `poi_name` is silently ignored, per D-1.
- The controller normalizes blank→null from `body.poiName()`. `PracticalInfoQuery`, `PoiService`, the repository, and the SQL stay unchanged, so the LIKE escape and the AND semantics are preserved and `jpa-performance-reviewer` is not triggered.
- `MAX_BYTES` stays 96 KiB. The worst case (500 × 128 ASCII ids plus a 128-char `\uXXXX` `poi_name`) is about 66.3 KB. Only the Javadoc changes, and a test proves the fit.

### Invariants Main must preserve
- I1: The body `poi_name` "x" → `PracticalInfoQuery.poiName()=="x"` (not trimmed). `ids` are unchanged.
- I2: A body `poi_name` that is absent, null, "", or whitespace-only → `poiName()==null`, giving the ids-only result.
- I3: `?poi_name=` is never read. The captured `poiName()` is null, and the data equals the same request without the param.
- I4: A body `poi_name` of 129 chars → 422 `ERR_VALIDATION_FAILED`, and the service is not called. 128 → 200.
- I5: The `ids` rules are unchanged: empty → 422, 501 → 422, 500 → 200.
- I6: The filters are AND-ed. A name-matching row outside `ids` is never returned.
- I7: LIKE escaping is unchanged: `100%_` matches only the literal substring, case-insensitively.
- I8: A body larger than `MAX_BYTES` → 400 `ERR_BODY_TOO_LARGE` before the service runs. The worst-case valid body is ≤ `MAX_BYTES` and reaches the chain.
- I9: A `poi_name` that is an array or object → 400 `ERR_BAD_REQUEST`.
- I10: GET practical_info and all other query params are unchanged. Nothing logs `poi_name` or the body.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| E1 | api/dto/PracticalInfoSearchRequest.java | whole record | Save the FILE block verbatim: add `@JsonProperty("poi_name") @Size(max = 128) String poiName` | Compiles; `ids` annotations unchanged |
| E2a | api/PoiController.java | `searchPracticalInfo` params | Delete the `@RequestParam(name = "poi_name", …) @Size(max = 128) String poiName` line | No `@RequestParam` for poi_name remains |
| E2b | api/PoiController.java | `new PracticalInfoQuery(` arg 4 | Use `body.poiName() == null \|\| body.poiName().isBlank() ? null : body.poiName()` | I1/I2 tests pass |
| E2c | api/PoiController.java | `@ApiResponses` 400 description | Change to "Body không đọc được (kể cả poi_name không phải chuỗi), quá lớn, hoặc page/size không phải số." Leave 422 as is | Text updated |
| E3 | common/web/PracticalInfoBodyLimitFilter.java | class Javadoc | Say the ceiling fits 500 ASCII ids of 128 chars plus a 128-char poi_name in JSON unicode-escape form. Do NOT write a literal backslash-u in the comment (Java compile error). `MAX_BYTES` is unchanged | Compiles; constant unchanged |
| E4 | test/api/PoiControllerIntegrationTest.java | new tests after `postPracticalInfoRejectsOversizedBody` | Add `postPracticalInfoPassesBodyPoiNameToQuery`, `postPracticalInfoIgnoresQueryPoiName`, `postPracticalInfoBlankBodyPoiNameMeansNoFilter`, `postPracticalInfoRejectsPoiNameOver128` (plus 128 OK), `postPracticalInfoRejectsNonStringPoiName`, `postPracticalInfoAcceptsMaxIdsAndMaxPoiNameWithinBodyLimit` using an `ArgumentCaptor<PracticalInfoQuery>` | All pass; existing tests unchanged |
| E5a | test/service/LegacyAndPracticalInfoIntegrationTest.java | `postFiltersBySourceAndPoiNameCaseInsensitiveEscaped` | Move `"100%_"` from `.param` into the body `poi_name`; keep `source=partner` | Still returns only `pct` |
| E5b | same | new `postAppliesIdsAndBodyPoiNameTogether` | Insert pct "100%_Cafe", wide "100X Cafe", outside "100%_Outside"; body ids [pct,wide] with poi_name "100%_cAFE" → [pct] | `outside` absent (I6) |
| E5c | same | new `postQueryPoiNameNoLongerFilters` | The same ids with `?poi_name=100%_` versus no param → equal data | I3 proven on the DB |
| E6 | test/common/web/PracticalInfoBodyLimitFilterTest.java | new `maxValidBodyWithPoiNameReachesChain` | Worst-case body: assert `length <= MAX_BYTES` and that the chain is reached (the `IOException("reached")` pattern) | Passes |
| E7 | docs/context/api-mapping/practical_info_list.md | `## Tổng quan`, `## Request param`, `## Request body`, `## Status code`, `## Sample request` | Per the full doc section "E8. Mapping doc": remove param row 4 and renumber; add body row 2 `poi_name`; update the 400 row; set the sample body to `{"ids":[…],"poi_name":"French Village"}` and add the lead sentence | The doc matches I1–I9 |
| E8 | PoiService, PracticalInfoQuery, SrvPoiLegacyIdMapRepositoryImpl, PoiServiceTest, PoiRepositoryIntegrationTest | none | No edit | Untouched |

### Order and stop points
1. E1, then E2a–c, then E3. Compile with `mvnw.cmd -q -B test-compile`.
2. E4, E6 (no DB needed), then E5a–c.
3. Run the full test suite. STOP (evidence): attach the failing output if anything fails. Do not loosen the assertions.
4. STOP (user decision) if any test forces an edit under E8 files: report it, because that changes the routing (adds jpa-performance-reviewer).
5. E7 doc update. It must land before review.
6. Write the runtime probes into `runtime-runbook.md` (listed in full-doc Verification → Runtime). STOP (evidence): the user runs them; there is no `docker compose` from Main.
7. Review with `api-contract-reviewer` and `app-security-reviewer`. The reviewers must confirm the stale-client note (a query `poi_name` is silently ignored).

### Tests and verification
- `cd services/data-serving-service && mvnw.cmd -q -B test` (JDK 26, Docker up): everything must pass.
- Targeted: `mvnw.cmd -q -B test -Dtest=PoiControllerIntegrationTest`, `-Dtest=LegacyAndPracticalInfoIntegrationTest`, `-Dtest=PracticalInfoBodyLimitFilterTest`, regression `-Dtest=ApiBearerAuthTest,PracticalInfoProjectionTest`.
- New test names: `postPracticalInfoPassesBodyPoiNameToQuery`, `postPracticalInfoIgnoresQueryPoiName`, `postPracticalInfoBlankBodyPoiNameMeansNoFilter`, `postPracticalInfoRejectsPoiNameOver128`, `postPracticalInfoRejectsNonStringPoiName`, `postPracticalInfoAcceptsMaxIdsAndMaxPoiNameWithinBodyLimit`, `postAppliesIdsAndBodyPoiNameTogether`, `postQueryPoiNameNoLongerFilters`, `maxValidBodyWithPoiNameReachesChain`; plus the modified `postFiltersBySourceAndPoiNameCaseInsensitiveEscaped`.
- Assert only the status and `meta.error_code` for 422. The `errors[].field` is `poiName`, which is existing handler behavior.
- Runtime (user): body poi_name matching → 1 item; non-matching → []; `?poi_name=` non-matching with no body poi_name → 1 item; 129 chars → 422; more than 96 KiB → 400 `ERR_BODY_TOO_LARGE`; GET unchanged.

### Read only if needed
- `Invariants`: E2b, E4, E5.
- `Alternatives` and `Body-size budget`: E3, E6, and why `MAX_BYTES` is unchanged and why the query is ignored rather than returning 422.
- `Implementation plan` → E4 and `Test code sketch`: E4 and E6 (captor pattern, `maxBody()` builder, the `\\u00e9` escaping note).
- `Implementation plan` → E8 (Mapping doc): E7 exact row text.
- `Security` and `Observability`: E2 and E3 (no logging, bound parameter, unknown-property tolerance).
- `Rollout` and `Rollback and forward recovery`: the review summary note for stale clients.
- `Non-goals`: E8 (why the service, repository, and SQL stay untouched; the `!` escape covers `\`).

# Architecture: move practical_info `poi_name` from query to JSON body

Decision ledger: D-1. No `model-design.md` is required because no table, column, grain, or key changes.

## Scope

- `POST /api/v1/pois/practical_info` reads `poi_name` from the JSON body (`PracticalInfoSearchRequest.poiName`, JSON name `poi_name`) instead of `@RequestParam("poi_name")`.
- The `poi_name` filter keeps its current semantics: optional string, `@Size(max = 128)`, blank or absent means no filter, a case-insensitive contains match on `apps.srv_poi_info.poi_name`, with LIKE metacharacters escaped. It is combined (AND) with `ids` and with `source`.
- `PracticalInfoBodyLimitFilter`: the ceiling value stays the same, the Javadoc is updated, and a test proves the ceiling fits 500 × 128-char ids plus a worst-case 128-char `poi_name`.
- Mapping doc `docs/context/api-mapping/practical_info_list.md`, plus controller, filter, and integration tests.

## Non-goals

- `GET /api/v1/pois/{poi_id}/practical_info`.
- Other query params (`required_fields`, `source`, `lang`, `page`, `size`, `sort_field`, `sort_order`), plus `Accept-Language`, auth, and the envelope.
- SQL, `SrvPoiLegacyIdMapRepositoryImpl`, `PoiService`, and `PracticalInfoQuery`. These are not edited: `PracticalInfoQuery.poiName` already carries the value end to end (`PoiService.searchPracticalInfo` → `findPracticalInfoPage(ids, source, poiName, …)`). Because neither the SQL nor `domain/repository/` changes, `jpa-performance-reviewer` is not triggered.
- Changing the LIKE escape character. The repository uses `ESCAPE '!'` and escapes `!`, `%`, `_`. With that escape, `\` is literal in PostgreSQL, so the doc's "escape `%`, `_`, `\`" still holds as observable behavior. No change.
- Making `poi_name` an array. Keeping a deprecated query fallback.
- Gold schema and `docs/poi-serving-api/`.

## Invariants

1. I1: The body `{"ids":[...],"poi_name":"x"}` produces `PracticalInfoQuery.poiName == "x"` (not trimmed, as today) and `ids` unchanged.
2. I2: A body `poi_name` that is absent, `null`, `""`, or whitespace-only produces `PracticalInfoQuery.poiName == null`. The result equals the ids-only result.
3. I3: A query param `poi_name` is never read. A request with `?poi_name=…` and no body `poi_name` gives `PracticalInfoQuery.poiName == null` and the same data as the same request without the param.
4. I4: A body `poi_name` longer than 128 UTF-16 units returns 422 `ERR_VALIDATION_FAILED`, and the service is not called. Exactly 128 is accepted.
5. I5: `ids` keeps `@NotEmpty @Size(max = 500) List<@NotBlank @Size(max = 128) String>`. Empty → 422, 501 → 422, 500 → 200.
6. I6: Filters are conjunctive: `ids` AND `deleted_at IS NULL` AND `source` AND `poi_name`. A row whose name matches but whose id is not in `ids` is never returned.
7. I7: LIKE escaping is unchanged. `100%_` matches only the literal `100%_` substring, case-insensitively.
8. I8: `PracticalInfoBodyLimitFilter.MAX_BYTES` (96 KiB = 98,304 bytes) rejects with 400 `ERR_BODY_TOO_LARGE` before the controller or service runs. A worst-case valid body (500 ASCII ids of 128 chars plus `poi_name` of 128 `\uXXXX`-escaped chars) is ≤ `MAX_BYTES` and reaches the chain.
9. I9: A non-string JSON `poi_name` (array or object) returns 400 `ERR_BAD_REQUEST` through `HttpMessageNotReadableException`. A JSON number or boolean is coerced to a string by Jackson's default scalar coercion. That is accepted, documented as-is, and not tightened.
10. I10: GET practical_info and the other query params behave exactly as before. The existing tests pass unmodified, except the one that used `.param("poi_name", …)`.

## State ownership

Not applicable: the endpoint is read-only. The service writes no state. Gold and serving tables are owned by the pipeline.

## Grain and keys

Not applicable: the response grain stays one element per resolved `poi_id`, as the mapping doc already states. No table, column, or key changes.

## Ordering

The request pipeline order is unchanged: bearer auth → `PracticalInfoBodyLimitFilter` (`LOWEST_PRECEDENCE`, which reads at most `MAX_BYTES + 1` bytes) → Jackson deserialize → bean validation of the body and params → controller mapping → service. Because `poi_name` now arrives in the body, it is size-capped by the filter before Jackson parses it. Before this change, the query-string `poi_name` was bounded only by the container's header and URI limits. The result sort order is unchanged.

## Transaction and commit boundaries

Not applicable: the call is a single `@Transactional(readOnly = true)` read in `PoiService.searchPracticalInfo`, unchanged.

## Idempotency

Not applicable: a read-only POST. The same body and query return the same page for the same data.

## Concurrency

Not applicable: no shared mutable state is added. The filter still allocates a per-request buffer.

## Retry and recovery

Not applicable: no retries or background work.

## Partial failure

Not applicable: one read query. A failure surfaces through `GlobalExceptionHandler` exactly as today.

## Observability

- No new logs or metrics. `poi_name` is user free text and must not be logged. The current code does not log it, and the new code must not add a log line containing the body.
- Validation errors keep the existing envelope. The `errors[].field` name comes from the existing handler: `poiName` (the Java property or parameter name). That is the same as today's query-param violation, so it is not a contract change. Tests assert only the status and `meta.error_code`.

## Security

- Input bound: `poi_name` ≤ 128 by bean validation, and the whole body ≤ 96 KiB by the filter before parsing. This tightens the attack surface compared with the URI-only bound.
- SQL: the value is still passed as a bound parameter (`:namePattern`) and escaped by `containsPattern`. There is no string concatenation into SQL.
- Unknown JSON properties are tolerated (the Spring Boot default `FAIL_ON_UNKNOWN_PROPERTIES=false`, unchanged).
- Auth is unchanged. `ApiBearerAuthTest` still covers the POST.
- No credentials or hosts in the code, docs, or tests.

## Alternatives

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| A. Body-only `poi_name` with `@JsonProperty("poi_name")` on the record; normalize blank→null in the controller (selected) | Smallest diff. Matches D-1. Validation stays declarative. The service, query object, and repository are untouched. | Stale clients that still send `?poi_name=` silently lose the filter and get a broader result. | Selected: D-1 says "query `poi_name` bị bỏ". The risk is handled in Rollout. |
| B. Accept both the body and the query during a deprecation window (body wins) | Zero-break for old clients | Contradicts D-1 and the acceptance criterion "Query poi_name không còn tác dụng lọc". Leaves two inputs to validate. | Rejected |
| C. Reject `?poi_name=` with 422 | Surfaces stale clients loudly | Adds a contract rule nobody requested. Other unknown query params are ignored, so this would be inconsistent. Changing it would mean revisiting D-1. | Rejected. It can be raised as a follow-up if a reviewer asks. |
| D. Normalize blank→null in a compact record constructor | The DTO is self-normalizing | `@Size` would then validate the normalized value. It also moves the existing controller-side normalization pattern used for `source`. | Rejected for consistency |
| E. Raise `MAX_BYTES` | More headroom | Not needed: the worst case is about 65.8 KB against 98.3 KB (see Body-size budget). | Rejected |

### Body-size budget

- `{"ids":[` + `]}`: 10 bytes. Each id: `"` + 128 ASCII chars + `"` + `,` = 131 bytes, minus 1 trailing comma. 500 ids ≈ 65,499 bytes.
- `,"poi_name":""` = 14 bytes. Worst-case value: 128 chars each written as `\uXXXX` = 768 bytes. Raw UTF-8 is at most 3 bytes per BMP char, which is 384 bytes, and a surrogate pair is 4 bytes per 2 units.
- Total ≈ 66,281 bytes, which is under 98,304. The headroom is about 32 KB. `MAX_BYTES` stays 96 KiB. Only the Javadoc changes.
- Pre-existing limitation, out of scope: non-ASCII or `\u`-escaped ids can exceed the cap. Real ids are ASCII UUIDs or legacy codes.

## Rollout

1. Deploy the server. Because unknown body properties are already ignored by the old server, clients may start sending `poi_name` in the body before or after the deploy without errors. Before the deploy, that filter has no effect.
2. Consumers move `poi_name` from the query to the body. Until they do, their `?poi_name=` is ignored (I3) and they get the ids-only (and source-filtered) result. This is a behavior change that api-contract-reviewer should confirm is communicated, through the mapping doc update and the release note in the review summary.
3. Runtime proof: the user runs `runtime-runbook.md`. The runbook is not in this architecture's scope, but the probes Main should list there are under Verification → Runtime.

## Rollback and forward recovery

- Rollback: revert the controller, DTO, filter Javadoc, tests, and doc. There is no data migration, so a revert is instant. After a rollback, clients already sending a body `poi_name` lose the filter (it is ignored) until they also send the query param. That is symmetric with the forward risk.
- Forward recovery: if a consumer cannot migrate, the fix is option B as a new decision in the ledger, not an ad-hoc patch.

## Implementation plan

### E1. DTO `PracticalInfoSearchRequest.java`

Replace the file with the FILE block below. `@JsonProperty("poi_name")` on the record component binds the JSON key. Jackson applies it to the canonical constructor parameter and the accessor. `@Size(max = 128)` applies to the raw value, so 129 spaces is a 422 (the same as today's query rule, where `@Size` ran before normalization).

### E2. Controller `PoiController.searchPracticalInfo`

- Delete the parameter `@RequestParam(name = "poi_name", required = false) @Size(max = 128) String poiName,`.
- In the `new PracticalInfoQuery(...)` call, replace `poiName == null || poiName.isBlank() ? null : poiName` with `body.poiName() == null || body.poiName().isBlank() ? null : body.poiName()`.
- Leave the `@ApiResponses` 422 description as is (it still lists `poi_name`). Change the 400 description to `"Body không đọc được (kể cả poi_name không phải chuỗi), quá lớn, hoặc page/size không phải số."`.
- Keep the `@Size` import if other params still use it (`required_fields` does).

### E3. Filter `PracticalInfoBodyLimitFilter` Javadoc only

Replace the class comment with:
`/** Chặn body POST practical_info trước khi Jackson đọc. Trần đủ cho 500 id ASCII dài 128 ký tự cộng poi_name 128 ký tự viết dạng \\uXXXX. */`
(Inside a Javadoc, write `\uXXXX` as `\\uXXXX` or `{@code \uXXXX}`. A raw `\u` followed by non-hex characters is a Java compile error, even in comments. Main must use the wording `dạng escape unicode JSON` instead of a literal backslash-u to be safe.) Do not change `MAX_BYTES`.

### E4. Tests: `PoiControllerIntegrationTest` (mocked `PoiService`)

Add these, using `ArgumentCaptor<PracticalInfoQuery>` (see Test code sketch):
- `postPracticalInfoPassesBodyPoiNameToQuery`: body `{"ids":["poi_01"],"poi_name":"Ba Na"}` → 200; captured `poiName()` is `"Ba Na"` and `ids()` is `["poi_01"]`.
- `postPracticalInfoIgnoresQueryPoiName`: `.queryParam("poi_name","Ba Na")` with body `{"ids":["poi_01"]}` → 200; captured `poiName()` is null.
- `postPracticalInfoBlankBodyPoiNameMeansNoFilter`: body `poi_name` `"   "`, then `null` → captured `poiName()` is null both times.
- `postPracticalInfoRejectsPoiNameOver128`: a 129-char `poi_name` → 422 `ERR_VALIDATION_FAILED`, `verifyNoInteractions(poiService)`. A 128-char value → 200.
- `postPracticalInfoRejectsNonStringPoiName`: `"poi_name":["a"]` → 400 `ERR_BAD_REQUEST`, no service call.
- `postPracticalInfoAcceptsMaxIdsAndMaxPoiNameWithinBodyLimit`: 500 ids of 128 ASCII chars plus `poi_name` of 128 `é` escapes → assert `body.getBytes(UTF_8).length <= PracticalInfoBodyLimitFilter.MAX_BYTES`, then 200 with captured `poiName().length() == 128`.

The existing `postPracticalInfoRejectsEmptyAndOver500Ids`, `postPracticalInfoAccepts500Ids`, and `postPracticalInfoRejectsOversizedBody` stay unchanged.

### E5. Tests: `LegacyAndPracticalInfoIntegrationTest` (real DB)

- Modify `postFiltersBySourceAndPoiNameCaseInsensitiveEscaped`: remove `.param("poi_name", "100%_")` and put the value in the body: `{"ids":[NEW_ID,"pct","wide"],"poi_name":"100%_"}`. Keep `.param("source","partner")`. The expected result is still only `pct`.
- Add `postAppliesIdsAndBodyPoiNameTogether`: insert `pct` `"100%_Cafe"`, `wide` `"100X Cafe"`, and `outside` `"100%_Outside"` (all `partner`). Body `{"ids":["pct","wide"],"poi_name":"100%_cAFE"}` → exactly `[pct]`. `outside` is absent even though its name matches (I6), and the case-insensitive match is proven.
- Add `postQueryPoiNameNoLongerFilters`: the same ids with `?poi_name=100%_` versus no param → equal `data`, and the size equals the number of resolvable ids.

### E6. `PracticalInfoBodyLimitFilterTest`

Add `maxValidBodyWithPoiNameReachesChain`: build the worst-case body from E4 (shared logic, built inline; there is no cross-test helper), call `request.setContent(bytes)`, and assert that the chain is reached (the same `IOException("reached")` pattern as `smallBodyReachesChain`) and that `bytes.length <= MAX_BYTES`.

### E7. `PoiServiceTest`, `PoiRepositoryIntegrationTest`, `PoiService`, `PracticalInfoQuery`, `SrvPoiLegacyIdMapRepositoryImpl`

No edits expected. They are in scope only as a safety margin. If Main finds it must edit any of them, stop and report: that would mean the SQL or query path changed, and the `jpa-performance-reviewer` routing applies.

### E8. Mapping doc `docs/context/api-mapping/practical_info_list.md`

- `## Tổng quan` Description: change "sau lọc `source` và `poi_name`." to "sau lọc `source` (query) và `poi_name` (body)."
- `## Request param`: delete row 4 `poi_name` and renumber `page`→4, `size`→5, `sort_field`→6, `sort_order`→7.
- `## Request body`: add row
  `| 2 | poi_name | string | không | Cùng cấp với `ids`. Tối đa 128. Vắng, `null`, rỗng hoặc chỉ khoảng trắng thì không lọc. Khớp chứa, không phân biệt hoa thường trên `apps.srv_poi_info.poi_name`. `%`, `_` và `\` được escape. Kết hợp AND với `ids` và `source`. Mảng hoặc object trả HTTP 400. Query `poi_name` không còn được đọc. |`
- `## Status code`: change the 400 row to "Body không đọc được (kể cả `poi_name` không phải chuỗi), body quá lớn (`ERR_BODY_TOO_LARGE`), hoặc `page`/`size` không phải số." Keep `poi_name` in the 422 row.
- `## Sample request`: change the body to `{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"],"poi_name":"French Village"}`. Append to the lead paragraph: "`poi_name` là `French Village`, chứa trong `name` của bản ghi Dev, nên response giữ như dưới." Leave the other samples ids-only.

## Test code sketch

The captor pattern for E4 (Main adapts the names and imports):

```java
@Test
@DisplayName("POST practical_info lấy poi_name từ body, bỏ qua query")
void postPracticalInfoPassesBodyPoiNameToQuery() throws Exception {
    when(poiService.searchPracticalInfo(any())).thenReturn(new PoiService.PracticalInfoPage(List.of(), 0));
    mockMvc.perform(authorized(post("/api/v1/pois/practical_info")
                    .contentType("application/json")
                    .queryParam("poi_name", "ignored")
                    .content("{\"ids\":[\"poi_01\"],\"poi_name\":\"Ba Na\"}")))
            .andExpect(status().isOk());
    ArgumentCaptor<PracticalInfoQuery> captor = ArgumentCaptor.forClass(PracticalInfoQuery.class);
    verify(poiService).searchPracticalInfo(captor.capture());
    assertThat(captor.getValue().poiName()).isEqualTo("Ba Na");
    assertThat(captor.getValue().ids()).containsExactly("poi_01");
}

private static String maxBody() {
    StringBuilder body = new StringBuilder("{\"ids\":[");
    String pad = "x".repeat(124);
    for (int i = 0; i < 500; i++) {
        if (i > 0) body.append(',');
        body.append('"').append(String.format("%04d", i)).append(pad).append('"');
    }
    body.append("],\"poi_name\":\"");
    for (int i = 0; i < 128; i++) body.append("\\u00e9");
    return body.append("\"}").toString();
}
```

The `"\\u00e9"` in Java source is a backslash followed by `u00e9`, which is the six bytes `é` in the JSON. It is not a Java unicode escape, because the preceding backslash is doubled.

## Verification

- Local: `cd services/data-serving-service && mvnw.cmd -q -B test` (JDK 26, Docker up for the Testcontainers ITs). Everything must pass. Targeted runs:
  - `mvnw.cmd -q -B test -Dtest=PoiControllerIntegrationTest`
  - `mvnw.cmd -q -B test -Dtest=LegacyAndPracticalInfoIntegrationTest`
  - `mvnw.cmd -q -B test -Dtest=PracticalInfoBodyLimitFilterTest`
  - `mvnw.cmd -q -B test -Dtest=ApiBearerAuthTest,PracticalInfoProjectionTest` (regression)
- Static check: `Grep` for `"poi_name"` under `src/main/java/.../api/PoiController.java`. Expect zero `@RequestParam` matches.
- Runtime, run by the user per `runtime-runbook.md` (Main writes the runbook steps; no hosts or tokens in artifacts):
  1. POST with `ids=[<known id>]` and body `poi_name` = a substring of its name → 1 item.
  2. The same request with a non-matching body `poi_name` → `data` is `[]` and `total_items` is 0.
  3. The same ids, with no body `poi_name` and `?poi_name=<non-matching>` → 1 item (the query is ignored).
  4. A body `poi_name` of 129 chars → 422 `ERR_VALIDATION_FAILED`.
  5. A body larger than 96 KiB → 400 `ERR_BODY_TOO_LARGE`.
  6. GET `/api/v1/pois/<id>/practical_info` → unchanged 200.

FILE: services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PracticalInfoSearchRequest.java
package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;

import java.util.List;

/**
 * Body POST practical_info. poi_name cùng cấp với ids; vắng hoặc rỗng thì không lọc tên.
 */
public record PracticalInfoSearchRequest(
        @NotEmpty @Size(max = 500) List<@NotBlank @Size(max = 128) String> ids,
        @JsonProperty("poi_name") @Size(max = 128) String poiName
) {}
END_FILE
