RESULT: PASS

## Main brief

### Decision
`CompactPoiResponse.Destinations.id` and `name` become `List<String>`. A strict parser in `PoiService` (`destinationArray`, shared through `destinationsOf`) builds them for compact, practical-info detail, the practical-info list, and the projection. It returns `null` for null or blank text, invalid JSON, trailing tokens, any non-array value, or any non-string element. Otherwise it returns the elements verbatim, in order. Nothing changes in SQL, entities, or gold. `StoredJsonParser` is out of scope, so the parser stays inside `PoiService`.

### Invariants Main must preserve
- Null or blank raw → JSON `null`, with no warning logged.
- A valid array of strings → the same elements, same order, no trim, filter, or de-duplication. `[]` → `[]`.
- `["a\\b"]` keeps its backslash (decoded value `a\b`, serialized `"a\\b"`). No `replace` or stripping on raw.
- Invalid JSON, `["a"] x`, a scalar, an object, a JSON string (including double-encoded `"[\"a\"]"`), or the `null` literal → `null`.
- Any element that is a number, boolean, null, object, or array → the whole field is `null`. No coercion, no partial array.
- A bad `destination_id` does not affect `destination_name`, other POIs, or the 200 status.
- `destinations` always has both keys `id` and `name` (`@JsonInclude(ALWAYS)` stays).
- Compact, detail, list, and projection produce identical `destinations` subtrees for the same row.
- No new repository call or SQL, and no new constructor dependency in `PoiService`.
- Warning log lines contain `poi_id`, `field`, and `reason` only, never the raw value.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| E1 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/CompactPoiResponse.java | `record Destinations` | `String id, String name` → `List<String>`, with `@ArraySchema` (nullable array of strings); add the `ArraySchema` import. Code: doc §Implementation plan › DTO change (E1) | compiles; OpenAPI shows an array |
| E2 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java | class fields and imports | add a static `Logger` and a static `DESTINATION_JSON` mapper with `FAIL_ON_TRAILING_TOKENS`. Code: doc §Parser and shared mapper (E2, E3) | no constructor change |
| E3 | same | new `destinationsOf`, `destinationArray` (package-private static), `warnDestination` | add the parser exactly as written in the doc §Parser and shared mapper | unit tests U3–U6 pass |
| E4 | same | `buildPracticalInfo`, last constructor argument | replace `new CompactPoiResponse.Destinations(...)` with `destinationsOf(poi)` | U8 passes |
| E5 | same | `mapToCompactResponse`, last constructor argument | same replacement | U1 and U7 pass |
| E6 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiPracticalInfoResponse.java | `destinations` component | no edit unless the compiler demands one; it already reuses the shared type | unchanged |
| E7 | services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java | `shouldReturnCompactPoisSuccessfully`, `shouldReturnPracticalInfoDestinationsAndNoTopLevelBusinessSector` | change fixtures to `"[\"dest_01\"]"` and `"[\"Ha Noi\"]"`; assert arrays | pass |
| E8 | same | new tests | U3–U9 below | pass |
| E9 | services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/PoiControllerIntegrationTest.java | `shouldReturnCompactPois`, `shouldReturnPracticalInfoWithoutTopLevelBusinessSector`, new `postPracticalInfoReturnsDestinationsAsArrays` | build with `List.of(...)`; jsonPath `isArray()` and `[0]`. Do not touch the other task's uncommitted hunks | pass |
| E10 | docs/context/api-mapping/compact.md | Field table row 17 and the Sample response section | add `destinations.id` and `destinations.name` rows typed `array<string>` with the null rule; add an illustrative fragment and leave the Dev capture unchanged | the doc shows arrays |
| E11 | docs/context/api-mapping/practical_info.md | Field table row 19 and the sample | same as E10 | same |
| E12 | docs/context/api-mapping/practical_info_list.md | the `destinations` field row (around line 52) and the sample (around line 202) | add the array rule and an illustrative fragment; keep the other task's edits | same |

### Order and stop points
1. E1–E5 (DTO and service). Compile with `mvnw.cmd -q -B test-compile`.
2. E7–E9 (tests). Run the targeted tests. **Stop S1 (evidence):** if `["a"] x` is not rejected, switch the read to a `JsonParser` that requires `nextToken()==null` (doc §Parser…), then rerun. Never relax the rule.
3. Run the full test suite. **Stop S2 (evidence):** save the test output to task evidence.
4. E10–E12 (docs) before review.
5. The user runs R1–R5 from doc §Runtime proof. Main does not run `docker compose`. **Stop S3 (user decision):** if real non-null rows mostly log `NOT_ARRAY` (for example double-encoded or CSV values), stop and ask the user. Do not add unwrapping.
6. Hand off to `api-contract-reviewer` and `jpa-performance-reviewer`. Report as a follow-up that `docs/context/api-mapping/(ood).summary.md` row 45 still says `string` (out of scope).

### Tests and verification
Unit tests in `PoiServiceTest` (some update existing tests, others are new):
- U1 `shouldReturnCompactPoisSuccessfully` (updated)
- U2 `shouldReturnCompactDestinationsObjectWhenColumnsNull` (unchanged; must pass)
- U3 `destinationArrayParsesStringArrayInOrder`: `["a","b"]`; `[" a ","","a"]` kept verbatim; `[]` → empty list
- U4 `destinationArrayKeepsBackslash`
- U5 `destinationArrayReturnsNullForBlankOrNonArray` (parameterized): null, `""`, `"   "`, `null` literal, `dest_01`, double-encoded string, object, `1`, `["a"`, `["a"] x`
- U6 `destinationArrayReturnsNullWhenElementNotString`: `["a",1]`, `["a",null]`, `[true]`, `[["a"]]`, `[{"id":"a"}]`
- U7 `compactKeepsOtherFieldWhenOneDestinationInvalid`
- U8 `shouldReturnPracticalInfoDestinationsAndNoTopLevelBusinessSector` (updated) and `compactAndPracticalInfoShareDestinationsShape`
- U9 `searchPracticalInfoProjectionKeepsDestinationsArray`

Controller tests in `PoiControllerIntegrationTest`: `shouldReturnCompactPois`, `shouldReturnPracticalInfoWithoutTopLevelBusinessSector`, `postPracticalInfoReturnsDestinationsAsArrays`, and `shouldSupportGetCompactPoisWithIdsAndAcceptLanguage` (unchanged).

Commands:
```
cd services/data-serving-service
mvnw.cmd -q -B test -Dtest=PoiServiceTest,PoiControllerIntegrationTest
mvnw.cmd -q -B test
```
Runtime: R1–R5 in doc §Runtime proof. Record only types, statuses, and counts; no hosts or tokens.

### Read only if needed
- §Invariants → E3, E8
- §Alternatives considered → E2, E3 (why the parser is not in `StoredJsonParser` and why there is no raw pass-through)
- §Implementation plan › DTO change (E1) → E1
- §Implementation plan › Parser and shared mapper → E2, E3, Stop S1
- §Implementation plan › Docs → E10–E12
- §Concurrency → E9, E12 (another task's uncommitted hunks)
- §Partial failure, §Observability, §Security → E3
- §Rollout, §Rollback and forward recovery → Stop S3
- §Verification → E7–E9 and runtime proof R1–R5

# Architecture: 20261126-destinations-json-array

Decision D-1 in `decision.md` is the contract. This design covers how to build it. No model design is needed: no table, column, grain, or key changes. `apps.srv_poi_info.destination_id` and `destination_name` stay `text` and are read as they are today.

## Scope

- `CompactPoiResponse.Destinations`: the type of `id` and `name` changes from `String` to `List<String>`, and the OpenAPI annotations are updated to match.
- `PoiService`: one shared mapper, `destinationsOf(SrvPoiInfo)`, plus a package-private parser, `destinationArray(poiId, field, raw)`. Both current construction sites use it: `buildPracticalInfo` (detail GET `practical_info` and list POST `practical_info`) and `mapToCompactResponse` (POST `compact`).
- `PoiPracticalInfoResponse`: no field change, because it already reuses `CompactPoiResponse.Destinations`. It is in scope only so the shared type is visibly the same. Do not edit it unless the compiler requires it.
- `PracticalInfoProjection` (`required_fields=destinations`) returns `dto.destinations()` without change. It inherits the new shape and is not edited (it is not in `scope.files`).
- Tests: `PoiServiceTest` and `PoiControllerIntegrationTest`.
- Docs: `docs/context/api-mapping/compact.md`, `practical_info.md`, and `practical_info_list.md`.

## Non-goals

- Gold or serving DDL, ETL, and notebooks.
- `StoredJsonParser` and `SubcategoryTagsParser`. Both are outside `scope.files`, so the parser is not moved into `service/util`. A follow-up may move it.
- Unwrapping double-encoded values such as `"[\"a\"]"` stored as a JSON string, splitting CSV, trimming elements, removing blanks, or de-duplicating. Any of these would invent or change elements, which D-1 forbids.
- `docs/poi-serving-api/` and `docs/context/api-mapping/(ood).summary.md`. Row 45 of the summary still says `string`, but the file is out of scope. Main reports it as a follow-up and does not edit it.
- `common/web/` and filters, so `app-security-reviewer` is not triggered.

## Invariants

1. I1: if raw is `null` or `raw.isBlank()`, the field is JSON `null`.
2. I2: if raw parses as exactly one JSON array and every element is a JSON string, the field is a JSON array with the same elements in the same order. Elements are not trimmed, filtered, or de-duplicated. `[]` becomes `[]`.
3. I3: escapes are decoded once by the JSON parser and re-encoded once by the serializer, so a backslash in the decoded value survives the round trip. Stored `["a\\b"]` comes back as the JSON text `["a\\b"]` (element value `a\b`). No code calls `replace` or strips `\` on raw.
4. I4: if raw is invalid JSON, has trailing tokens after the array, or is a scalar, object, JSON string, or JSON `null` literal, the field is `null`.
5. I5: if any element is not textual (number, boolean, `null`, object, or array), the whole field is `null`. Elements are not coerced and there are no partial arrays.
6. I6: a bad value in one field does not affect the other field, other POIs, the HTTP status (still 200), or the envelope.
7. I7: the `destinations` object is always present with both keys `id` and `name`. That is today's `@JsonInclude(ALWAYS)` behavior and it stays.
8. I8: compact, practical-info detail, the practical-info list, and the `required_fields` projection all produce byte-identical `destinations` subtrees for the same row.
9. I9: no new SQL, repository call, or entity field. Parsing is pure CPU on columns that are already loaded.
10. I10: warning logs never include the raw column value.

## State ownership

Gold owns the column values. The service is a read-only projection. The parser keeps no state; its `ObjectMapper` is an immutable static that is safe to share across threads.

## Grain and keys

One `destinations` object per `apps.srv_poi_info` row (`poi_id`), the same as today. There is no `model-design.md` and none is required, because grain and keys do not change.

## Ordering

Element order is the order stored in the JSON array. The order of POIs in responses does not change.

## Transaction and commit boundaries

Not applicable: these are read-only `@Transactional(readOnly = true)` methods, and parsing runs inside the existing read transaction without database work.

## Idempotency

Not applicable: reads are pure functions of the stored text.

## Concurrency

Jackson `ObjectMapper` reads are thread-safe once the mapper is configured. The mapper is built once in a `static final` field and never reconfigured. The working tree also holds uncommitted edits from tasks `20261126-practical-info-poi-name-*` in `PoiControllerIntegrationTest.java` and `practical_info_list.md`. Main edits only the anchors named here and must not revert or reformat those other changes.

## Retry and recovery

Not applicable: a parse failure is not retried. The field becomes `null` and a warning is logged.

## Partial failure

This is per-field degradation (I5, I6). A malformed `destination_id` with a valid `destination_name` returns `{"id": null, "name": [...]}`. Jackson errors are caught as `JsonProcessingException`, which includes `StreamConstraintsException` for oversized or deeply nested input, so they never reach `GlobalExceptionHandler`.

## Observability

On each rejection, log a `WARN` line with the same token `StoredJsonParser` uses, so existing log searches still match:
`stored_json_parse_failed poi_id={} field={destination_id|destination_name} reason={INVALID_JSON|NOT_ARRAY|BAD_ELEMENT}`.
A JSON `null` literal returns `null` without a warning, the same as `StoredJsonParser`. Blank or `null` raw values do not log. No new metrics.

## Security

- The raw value is not logged (I10), and no request input reaches the parser. Values come only from gold.
- Jackson 2's default `StreamReadConstraints` (nesting and string-length limits) bound the parse cost. No new endpoint or authentication change, no host or credential in artifacts.

## Rollout

- This is a breaking change to the response shape: `destinations.id` and `destinations.name` change from string to array or null. The `api-contract-reviewer` signs off. The mapping docs mark the change before review.
- The service deploys normally; there is no flag. Runtime proof is user-run per `runtime-runbook.md`. Main does not run `docker compose`.

## Rollback and forward recovery

- Rollback: revert the DTO, `PoiService`, test, and doc hunks of this task. There is no data to migrate and nothing in gold changes.
- Forward recovery, if runtime shows gold stores double-encoded or non-array values: stop and ask the user (Stop S3). Do not add unwrapping silently.

## Alternatives considered

| Option | Verdict | Why |
|---|---|---|
| A. Parse in `PoiService` to `List<String>` with strict element checks (selected) | Selected | Meets I4 and I5 exactly, stays within `scope.files`, uses one mapper for every endpoint, and is unit-testable from the same package. |
| B. `@JsonRawValue` pass-through, like `holiday_exceptions` | Rejected | Cannot reject non-string elements (violates I5), sends unvalidated text into the response, and leaves the OpenAPI items type unclear. |
| C. Move the parser into `StoredJsonParser` | Deferred | Cleaner reuse, but the file is outside `scope.files`. Possible follow-up. |
| D. Static factory on the `Destinations` record | Rejected | Puts parsing and logging in the `api/dto` layer, which no other DTO does. |
| E. Lenient parsing (CSV fallback, unwrapping, coercion) | Rejected | Invents or changes elements, which D-1 forbids. |

## Implementation plan

### DTO change (E1)

In `CompactPoiResponse.Destinations`:

```java
    @JsonInclude(JsonInclude.Include.ALWAYS)
    @Schema(description = "Điểm đến")
    public record Destinations(
            @ArraySchema(
                    arraySchema = @Schema(types = {"array", "null"},
                            description = "apps.srv_poi_info.destination_id, mảng JSON chuỗi. Không phải mảng chuỗi JSON thì null."),
                    schema = @Schema(type = "string"))
            List<String> id,
            @ArraySchema(
                    arraySchema = @Schema(types = {"array", "null"},
                            description = "apps.srv_poi_info.destination_name, mảng JSON chuỗi. Không phải mảng chuỗi JSON thì null."),
                    schema = @Schema(type = "string"))
            List<String> name
    ) {}
```

Add `import io.swagger.v3.oas.annotations.media.ArraySchema;`. `java.util.List` is already imported. If springdoc rejects `types` inside `arraySchema`, fall back to `@Schema(types = {"array", "null"}, description = ...)` on each component. The JSON contract does not depend on this choice.

### Parser and shared mapper in `PoiService` (E2, E3)

Add these imports: `com.fasterxml.jackson.core.JsonProcessingException`, `com.fasterxml.jackson.databind.DeserializationFeature`, `com.fasterxml.jackson.databind.JsonNode`, `com.fasterxml.jackson.databind.ObjectMapper`, `com.fasterxml.jackson.databind.json.JsonMapper`, `org.slf4j.Logger`, and `org.slf4j.LoggerFactory`. Do not add a constructor dependency, so the `@InjectMocks` wiring in `PoiServiceTest` keeps working.

```java
    private static final Logger log = LoggerFactory.getLogger(PoiService.class);
    private static final ObjectMapper DESTINATION_JSON = JsonMapper.builder()
            .enable(DeserializationFeature.FAIL_ON_TRAILING_TOKENS)
            .build();

    private static CompactPoiResponse.Destinations destinationsOf(SrvPoiInfo poi) {
        return new CompactPoiResponse.Destinations(
                destinationArray(poi.getPoiId(), "destination_id", poi.getDestinationId()),
                destinationArray(poi.getPoiId(), "destination_name", poi.getDestinationName()));
    }

    /** Mảng chuỗi JSON nguyên thứ tự. Null, rỗng, không phải mảng, hoặc phần tử không phải chuỗi thì null. */
    static List<String> destinationArray(String poiId, String field, String raw) {
        if (raw == null || raw.isBlank()) {
            return null;
        }
        JsonNode node;
        try {
            node = DESTINATION_JSON.readTree(raw);
        } catch (JsonProcessingException ex) {
            warnDestination(poiId, field, "INVALID_JSON");
            return null;
        }
        if (node == null || node.isNull() || node.isMissingNode()) {
            return null;
        }
        if (!node.isArray()) {
            warnDestination(poiId, field, "NOT_ARRAY");
            return null;
        }
        List<String> out = new ArrayList<>(node.size());
        for (JsonNode element : node) {
            if (!element.isTextual()) {
                warnDestination(poiId, field, "BAD_ELEMENT");
                return null;
            }
            out.add(element.textValue());
        }
        return Collections.unmodifiableList(out);
    }

    private static void warnDestination(String poiId, String field, String reason) {
        log.warn("stored_json_parse_failed poi_id={} field={} reason={}", poiId, field, reason);
    }
```

Do not use `List.copyOf`. The element check already rules out nulls, but `unmodifiableList` keeps the code obviously safe. If the test for `["a"] x` shows that `readTree` ignores trailing tokens in this Jackson version, replace the read with a `JsonParser` loop: read the tree, then require `parser.nextToken() == null`. Do not relax I4.

### Call sites (E4, E5)

- `buildPracticalInfo`: replace `new CompactPoiResponse.Destinations(poi.getDestinationId(), poi.getDestinationName())` with `destinationsOf(poi)`.
- `mapToCompactResponse`: make the same replacement.

### Docs (E10–E12)

- `compact.md` row 17: keep `object`, and change the note to `Luôn {id, name}. id, name là mảng chuỗi JSON hoặc null (D-1 task 20261126-destinations-json-array).` Add rows `17a data[].destinations.id | array<string> | có | apps.srv_poi_info.destination_id | Parse mảng JSON trong text. Null/rỗng/không phải mảng/phần tử không phải chuỗi → null. Không bịa phần tử, không bỏ \.` and `17b data[].destinations.name`, which is the same with `destination_name`. Use the file's existing numbering style. If letter suffixes clash with it, insert the rows and renumber.
- `practical_info.md` row 19: make the same change, adding `data.destinations.id` and `data.destinations.name` rows.
- `practical_info_list.md`: add a sentence under the field list (the `destinations` row around line 52) saying `id` and `name` are arrays of strings or `null`, with the same rule. The captured samples dated 2026-11-11 show `null`, which is still a valid value. Keep the capture honest by not editing captured values. Next to each sample add a short block labelled `Ví dụ minh hoạ (không phải bản chụp Dev)`: `"destinations": {"id": ["dest_01"], "name": ["Hà Nội"]}`. Apply the same to `compact.md` and `practical_info.md`. After runtime proof, Main may replace the illustration with a real captured fragment, with no host or token.

## Verification

### Unit tests: `PoiServiceTest`

Update existing tests:
- `shouldReturnCompactPoisSuccessfully`: change the fixtures to `.destinationId("[\"dest_01\"]")` and `.destinationName("[\"Ha Noi\"]")`, and assert `containsExactly("dest_01")` and `containsExactly("Ha Noi")`.
- `shouldReturnCompactDestinationsObjectWhenColumnsNull`: no change. It must still pass and still contain `"destinations":{"id":null,"name":null}`.
- `shouldReturnPracticalInfoDestinationsAndNoTopLevelBusinessSector`: use array fixtures, then assert `node.path("destinations").path("id").isArray()` and `node.path("destinations").path("name").get(0).asText()` equals `Ha Noi`.

Add new tests:
- `destinationArrayParsesStringArrayInOrder`: `["a","b"]` → `[a, b]`; `[" a ","","a"]` → exactly `[" a ", "", "a"]`; `[]` → empty list (not null).
- `destinationArrayKeepsBackslash`: raw Java literal `"[\"a\\\\b\"]"` → element equals `"a\\b"` (one backslash). Serializing a `Destinations` with that list through `new ObjectMapper()` gives `["a\\b"]`.
- `destinationArrayReturnsNullForBlankOrNonArray`, as a `@ParameterizedTest` with `@NullSource` and `@ValueSource`: `""`, `"   "`, `"null"`, `"dest_01"`, `"\"[\\\"a\\\"]\""`, `"{\"a\":1}"`, `"1"`, `"[\"a\""`, `"[\"a\"] x"` → `null`.
- `destinationArrayReturnsNullWhenElementNotString`, parameterized: `["a",1]`, `["a",null]`, `[true]`, `[["a"]]`, `[{"id":"a"}]` → `null`.
- `compactKeepsOtherFieldWhenOneDestinationInvalid`: `destinationId("not-json")` and `destinationName("[\"Ha Noi\"]")` → `id()` is null, `name()` equals `[Ha Noi]`, and no exception is thrown.
- `compactAndPracticalInfoShareDestinationsShape`: one `SrvPoiInfo` with array values, run through `getCompactPois` and `getPracticalInfo`. The serialized `destinations` subtrees are equal `JsonNode`s.
- `searchPracticalInfoProjectionKeepsDestinationsArray`: fields `EnumSet.of(DESTINATIONS)`. The serialized `items[0]` has `destinations.id` as an array.

### Controller tests: `PoiControllerIntegrationTest`

- `shouldReturnCompactPois`: build `Destinations(List.of("dest_01"), List.of("Hoan Kiem"))`. Assert `$.data[0].destinations.id` `isArray()`, `$.data[0].destinations.id[0]` is `dest_01`, and `$.data[0].destinations.name[0]` is `Hoan Kiem`.
- `shouldSupportGetCompactPoisWithIdsAndAcceptLanguage`: no change (null and null).
- `shouldReturnPracticalInfoWithoutTopLevelBusinessSector`: use list arguments. Assert `$.data.destinations.id` `isArray()` and `$.data.destinations.name[0]` is `Ha Noi`.
- New `postPracticalInfoReturnsDestinationsAsArrays`: stub `searchPracticalInfo` to return `PracticalInfoPage(List.of(PracticalInfoProjection.select(dto, EnumSet.of(PracticalInfoQuery.Field.DESTINATIONS))), 1)`. Assert `$.data[0].destinations.id` `isArray()` and `$.data[0].destinations.name[0]`.

### Commands

```
cd services/data-serving-service
mvnw.cmd -q -B test -Dtest=PoiServiceTest,PoiControllerIntegrationTest
mvnw.cmd -q -B test
```

### Runtime proof (user-run, per `runtime-runbook.md`)

- R1: POST `/api/v1/pois/compact` for a POI whose `destination_id` holds a stored JSON array. `destinations.id` is a JSON array, not a string.
- R2: GET `/api/v1/pois/{id}/practical_info` for the same POI. `destinations` matches R1.
- R3: POST `/api/v1/pois/practical_info` with `required_fields` containing `destinations`. Same subtree as R1.
- R4: a POI with `null` destination columns. The response has `"destinations":{"id":null,"name":null}` and status 200.
- R5: count service log lines matching `stored_json_parse_failed` with `field=destination_`. If most rows with a non-null value warn `NOT_ARRAY`, gold stores a different format. Go to Stop S3.
- Record only status, the JSON types, and the counts in the task evidence. No hosts, tokens, or raw personal data.
