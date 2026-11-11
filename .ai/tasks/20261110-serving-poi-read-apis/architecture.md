RESULT: PASS

## Main brief

### Decision
RESULT: PASS. D-2 to D-6 and probes P-1 to P-4 cover everything except one field, `practical_info.holiday_exceptions`. The stored keys are `{date, hours, title, status}`, and nothing defines what `status` means. That field becomes user decision D-7, with both branches fully designed in architecture.md §6.6.1. D-7 blocks only row 14 and the `holiday_exceptions` rows of `practical_info.md`.
Design choices: features selection uses one native SQL with bound parameters; the reviews envelope is a nested record, so `common/dto` is untouched; the multi-language fallback is per field. scope.files does not change.

### Invariants Main must preserve
- Reads go only to `apps.srv_poi_*`. Every service method is `@Transactional(readOnly = true)`. No DDL, entity, or `common/dto` change. `tests/test_srv_poi_serving_contract.py` passes unchanged.
- Required = có appears only on path `poi_id` and on compact body `ids`. Everything else is optional and keeps its default. `lang` and `Accept-Language` both missing resolves to `vi`.
- Compact `ids` must have 1 to 20 items: `{}`, `[]`, 21 ids, or a blank id return 422 `ERR_VALIDATION_FAILED`. A malformed or absent body returns 400 `ERR_BAD_REQUEST` with a fixed message that never echoes `e.getMessage()`. `GET /compact` returns 405.
- Every ORDER BY ends on a unique key. Compact: `createdAt DESC, poiId ASC`. Gallery: `displayOrder ASC NULLS LAST, mediaId ASC`. Reviews: `reviewDate DESC, reviewId ASC`. Features: `sector_seq, sector_rank, poi_id`.
- Gallery and reviews never call `validatePoiExists`: an unknown POI returns 200 with `[]`. Practical info returns 404 for an unknown POI.
- Cover for compact and features comes from `srv_poi_info.cover_id`/`cover_blob_url`. Gallery `file_key` comes only from `blob_url`. Experiences `source` comes from `srv_poi_multi_lang.source_name`.
- `rating_summary` is a sibling of `data`. It has one element `{rating_count, rating_avg_score}` when the POI has any review row, else `[]`. It does not depend on `page`.
- Request values are always bound. Sector values match `^[a-z0-9_]{1,64}$` before they are joined into `:sectorsCsv`.
- A malformed stored JSON value degrades only that field (null, `[]`, or a skipped element), with a WARN `stored_json_parse_failed poi_id field reason` that carries no content. It never causes a 500.
- Mapping JSON names equal the DTO `@JsonProperty` names. Samples use synthetic values only.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | api/dto/CompactPoiRequest.java (new) | record | `(String lang, @NotEmpty @Size(max=20) List<@NotBlank @Size(max=128) String> ids)` (§6.1) | Compiles. 422 cases pass |
| 2 | api/dto/CompactPoiResponse.java | Cover, BusinessTags | Cover becomes `(id, file_key)`; delete the 5-arg constructor. Drop `business_sector_label` and `primaryCategoryLabel()` | No width, height, mime_type, blur_hash, or label keys in the JSON |
| 3 | api/PoiController.java | getCompactPois | `@PostMapping(value="/compact", consumes=APPLICATION_JSON)`, `@Valid @RequestBody`, header `Accept-Language`. Return `ApiResponse.success`, no pagination (§6.1) | POST 200. GET 405. Non-JSON 415 |
| 4 | service/PoiService.java | getCompactPois, mapToCompactResponse | `findAll(spec, Sort desc createdAt, asc poiId)` returning a List. Cover from info. Remove the gallery batch, `parseSort`, and `resolveMimeType` if unused | Service tests pass |
| 5 | common/web/GlobalExceptionHandler.java | handleNotReadable (new) | Code from §6.7 | Malformed body returns 400 `ERR_BAD_REQUEST` |
| 6 | domain/repository/SrvPoiMediaGalleryRepository.java | findActivePageByPoiId, findActiveCoverByPoiId | Code from §6.2. Delete the two old queries | Repository test passes |
| 7 | api/dto/PoiGalleryItemResponse.java | record | `(id, file_key, display_order)`, `@JsonInclude(ALWAYS)` | Exactly 3 keys |
| 8 | api/PoiController.java | getGallery | `page` (0, `@Min 0`), `size` (20, `@Min 1`, `@Max 100`). Return `successList` with `PaginationMeta.offset` | Full pagination meta |
| 9 | service/PoiService.java | getGallery | No existence check. `PageRequest.of(page,size)` with no Sort. `file_key = blobUrl` | Unknown POI returns 200 `[]` |
| 10 | api/dto/PoiReviewItemResponse.java | RatingSummary, ReviewsResponse (nested) | Code from §6.3.1 | JSON key order includes `rating_summary` after `data` |
| 11 | service/PoiService.java | getReviews, ReviewsPage (nested record) | Remove the existence check. Sort per the invariant. Summary rule per §6.3, using the existing `findByPoiIdAndDeletedAtIsNull(poiId, PageRequest.of(0,1,Sort.by("reviewId")))` when the page is empty and total > 0 | Unknown POI returns `[]`/`[]`. Page past the end still has the summary |
| 12 | api/PoiController.java | getReviews | Return `ResponseEntity<PoiReviewItemResponse.ReviewsResponse>` via `ReviewsResponse.of(...)` | Controller test passes |
| 13 | service/util/StoredJsonParser.java (new) | operatingHours, labelValue, experiences | Static utility with one `private static final ObjectMapper` (pattern of `SubcategoryTagsParser`). Rules in §6.5 and §6.6 | Parser cases in PoiServiceTest pass |
| 14 | service/util/StoredJsonParser.java | holidayExceptions | BLOCKED until D-7. Option A or B exactly as in §6.6.1 | D-7 parser test passes |
| 15 | domain/repository/SrvPoiInfoRepository.java | FEATURE_WHERE, findFeatureIds, countFeatures | Native SQL from §6.4.1 | Round-robin repository tests pass |
| 16 | api/dto/PoiFeatureResponse.java (new) | record + Cover, Rating, BusinessTags, Status, OperatingHour | Fields from §6.4. Reuse `CompactPoiResponse.Address` and `GeoLocation`. `OperatingHour` is NON_NULL | JSON matches features.md |
| 17 | service/PoiService.java, api/PoiController.java | getFeatures | Parameters, normalization, and response per §6.4. Map items in SQL id order | Features tests pass |
| 18 | api/dto/PoiExperiencesResponse.java (new), PoiService, PoiController | getExperiences | §6.5: candidate rows target then vi; at most 3 items; `source` from `source_name`; 200 with `{items:[]}` when empty | Tests pass |
| 19 | api/dto/PoiPracticalInfoResponse.java (new), PoiService, PoiController | getPracticalInfo | §6.6: 404 when the POI is missing; per-field language fallback; cover via `findActiveCoverByPoiId`; `holiday_exceptions` per row 14 | Tests pass |
| 20 | docs/context/api-mapping/compact.md | all sections | §6.8 compact | pytest passes |
| 21 | docs/context/api-mapping/gallery.md | params, Response, Status code, samples | §6.8 gallery | pytest passes |
| 22 | docs/context/api-mapping/reviews.md | Response, Status code, samples | §6.8 reviews | pytest passes |
| 23 | docs/context/api-mapping/features.md | all sections | §6.8 features | pytest passes |
| 24 | docs/context/api-mapping/experiences.md | header, Response, Status code, sample | §6.8 experiences | pytest passes |
| 25 | docs/context/api-mapping/practical_info.md | header, Response, Status code, sample | §6.8 practical_info. `holiday_exceptions` rows after D-7 | pytest passes |
| 26 | tests/test_srv_poi_api_mapping_required.py (new) | whole file | Save the FILE block verbatim | pytest passes |
| 27 | PoiControllerIntegrationTest, PoiServiceTest, PoiRepositoryIntegrationTest, GlobalExceptionHandlerTest | test methods | Replace or add the tests listed below | mvnw passes |
| 28 | runtime-runbook.md (task artifact) | whole file | §12 steps with a synthetic fixture; no hosts or credentials | The user can run it |
| 29 | decision.md (task artifact) | ledger | D-ARCH-2 PASS. D-7 when the user answers. `backlog` entry for missing indexes (§11) | Ledger updated |

### Order and stop points
1. Record D-ARCH-2 (row 29). Rows 1–12, then `mvnw.cmd -q -B test -Dtest=PoiControllerIntegrationTest,PoiServiceTest,GlobalExceptionHandlerTest` (WebMvc and Mockito, no Docker needed).
2. STOP (user decision D-7): ask the user to choose option A (recommended) or B from §6.6.1. Confirm two points: `status=false` means closed, and `value` reads "Đóng cửa" in every language. Record the answer in decision.md. Rows 13 and 15–19 continue in the meantime. Row 19 leaves `holiday_exceptions` null until row 14 lands.
3. Rows 13, 15–19, then the full `mvnw.cmd -q -B test` with Docker.
4. Row 14 and the D-7 parts of row 25, after step 2 is answered.
5. Rows 20–26, then pytest.
6. Row 28, then `python scripts/vv.py verify 20261110-serving-poi-read-apis` with Docker.
7. STOP (evidence): the user runs `runtime-runbook.md` and saves the output under `evidence/runtime/`. Reviewers: api-contract-reviewer, jpa-performance-reviewer, app-security-reviewer.

### Tests and verification
- `cd services/data-serving-service && mvnw.cmd -q -B test`
- PoiControllerIntegrationTest:
  - shouldReturnCompactPoisForPostBody (replaces shouldReturnCompactPois and shouldSupportGetCompactPoisWithIdsAndAcceptLanguage)
  - shouldResolveCompactLangFromAcceptLanguageWhenBodyLangMissing
  - shouldReturn422WhenCompactIdsMissing, shouldReturn422WhenCompactIdsEmpty, shouldReturn422WhenCompactIdsExceed20 (replaces shouldReturn422WhenCompactSizeExceedsMax)
  - shouldReturn400WhenCompactBodyMalformed, shouldReturn400WhenCompactBodyMissing
  - shouldReturn405ForGetCompact, shouldReturn415WhenCompactContentTypeNotJson
  - shouldPropagateTraceIdHeader (switch to POST)
  - shouldReturnPagedGallery (replaces shouldReturnGallerySuccessfully)
  - shouldReturnEmptyGalleryWhenPoiHasNoMedia
  - shouldReturnEmptyGalleryForUnknownPoi (replaces shouldReturn404WhenGalleryPoiNotFound)
  - shouldReturn422WhenGallerySizeExceedsMax
  - shouldReturnReviewsWithRatingSummary (replaces shouldReturnReviewsSuccessfully)
  - shouldReturnEmptyReviewsAndRatingSummaryForUnknownPoi (replaces shouldReturn404WhenReviewsPoiNotFound)
  - shouldReturn422WhenReviewsSizeExceedsMax
  - shouldReturnFeaturesWithPagination, shouldApplyDefaultFeatureParams, shouldReturn422WhenFeaturesSizeExceedsMax
  - shouldReturnExperiences, shouldReturnPracticalInfo, shouldReturn404WhenPracticalInfoPoiNotFound
- PoiServiceTest:
  - shouldMapCompactCoverFromPoiInfo, shouldOrderCompactByCreatedAtDescThenPoiId, shouldReturnEmptyCompactWhenNoMatch (replaces shouldReturnEmptyPageWhenNoPois)
  - shouldMapGalleryFileKeyFromBlobUrlOnly (replaces shouldReturnGallerySuccessfully), shouldNotCheckPoiExistenceForGallery (replaces shouldThrowWhenPoiNotFoundInGallery)
  - shouldTakeRatingSummaryFromFirstRow, shouldTakeRatingSummaryWhenPageBeyondLast, shouldReturnEmptyRatingSummaryWhenNoReviews (replaces shouldThrowWhenPoiNotFoundInReviews)
  - shouldKeepFeatureOrderFromRepository, shouldNormalizeSectorPriority, shouldRejectInvalidSectorValue
  - shouldFallBackExperiencesToViWhenTargetEmpty, shouldCapExperiencesAtThree, shouldSkipBlankExperienceItems
  - shouldMapPracticalInfo, shouldThrowWhenPracticalInfoPoiMissing
  - shouldParseLabelValueSingleKeyObject, shouldParseOperatingHours, shouldDegradeMalformedStoredJsonToNull, shouldMapHolidayExceptions (after D-7)
- PoiRepositoryIntegrationTest:
  - shouldPageGalleryByDisplayOrderThenMediaId (update testSrvPoiMediaGalleryRepository), shouldFindActiveCoverByPoiId
  - shouldRoundRobinFeaturesBySectorPriority, shouldPreferPartnerPoolThenFallbackWithinSector, shouldFilterFallbackByRatingSource
  - shouldExcludeNullBlankAndUnlistedSectors, shouldCountFeatureCandidates
- GlobalExceptionHandlerTest: shouldHandleNotReadable. Construct the exception with `new HttpMessageNotReadableException("x", new MockHttpInputMessage(new byte[0]))`.
- `python -m pytest tests/test_srv_poi_serving_contract.py tests/test_srv_poi_api_mapping_required.py -q`
- `python scripts/vv.py verify 20261110-serving-poi-read-apis` (needs Docker; only this sets local_verification to pass)

### Read only if needed
- §5 Alternatives: rows 10, 15, 17, 19, and the reviewer questions
- §6.1 Compact: rows 1–4
- §6.2 Gallery: rows 6–9
- §6.3 and §6.3.1 Reviews: rows 10–12
- §6.4 and §6.4.1 Features SQL: rows 15–17
- §6.5 Experiences: rows 13 and 18
- §6.6 Practical info: rows 13 and 19
- §6.6.1 holiday_exceptions (D-7): step 2 and row 14
- §6.7 Malformed body: row 5
- §6.8 Mapping files: rows 20–25
- §9 Observability and §10 Security: rows 5, 13, 17
- §11 Performance: rows 6, 15, 29
- §12 Rollout and runbook: row 28 and step 7

# Architecture: 20261110-serving-poi-read-apis (round 2)

The user closed D-2 to D-6, and P-1 to P-4 have results (D-PROBE-1). The design is complete. One gap remains, and it affects one field only: `practical_info.holiday_exceptions`. The stored keys are `{date, hours, title, status}`, but `practical_info.md` cites `.value`, `.open_time`, `.close_time`, `.is_open_all_day`, `.is_closed`, which are not stored. No convention exists for `status` (decision.md "Giả định còn lại", and gap G6 in `docs/poi-serving-api/HANDOFF.md`). §6.6.1 designs both branches in full as user decision D-7. D-7 is a stop point before one edit row. It does not block the rest of the work. No table, column, grain, or key changes, so no `model-design.md` is needed.

## 1. Scope

- Compact: `GET` becomes `POST` with a JSON body `{lang, ids}`. `ids` must have 1 to 20 items (D-4). Order is `created_at DESC, poi_id ASC`. Cover comes from `srv_poi_info.cover_id`/`cover_blob_url` (D-1). No pagination. A malformed or missing body returns 400 (D-6).
- Gallery: no existence check. Add `page`/`size`. Items are `{id, file_key, display_order}`, with `file_key` from `blob_url` only. Offset pagination.
- Reviews: no existence check. `rating_summary` is a sibling of `data` (D-5).
- Features: new endpoint using the D-2 selection, the `ApiResponse` envelope, and full pagination (D-3).
- Experiences and practical_info: new endpoints that follow their mapping files, using `ApiResponse` (D-3).
- All six mapping files follow the Required rule (D-4), D-1, D-3, and D-5. A new pytest locks them.

## 2. Non-goals

- No DDL, index, entity, or column change. `tests/test_srv_poi_serving_contract.py` stays unchanged and must pass.
- No `Authorization` enforcement. The header is documented with Required = không and is not read.
- No change to `/amenities`, `common/dto`, `PoiSpecifications`, `SrvPoiReviewRepository`, config, `pom.xml`, or Docker.
- No `experience.keyword` in the response, because the mapping response table has no such field. No truncation of experience titles or descriptions (§6.5).
- Compact keeps its current per-row language fallback, because the request does not change it.

## 3. Invariants

1. Reads go only to `apps.srv_poi_*`. Every service method is `@Transactional(readOnly = true)`.
2. Every source column cited by code or mapping exists in `sql/postgres/gld_srv_serve.pg.sql` and in the entity. The pytest `test_cited_source_columns_exist_in_ddl` checks this.
3. Required = có appears only on path `poi_id`, and on compact body `ids`. Every other header, param, and body field is optional and keeps its default.
4. When `lang` and `Accept-Language` are both missing or blank, the language is `vi` (`LanguageResolver`).
5. Every result is bounded. Compact returns at most 20 rows. Gallery, reviews, and features have `size` ≤ 100. Experiences returns at most 3 items. `business_sector_priority` has at most 20 values.
6. Order is deterministic, and every ORDER BY ends on a unique key (`poi_id`, `media_id`, `review_id`).
7. Rows with `deleted_at` set never appear. Gallery also requires `is_active IS NULL OR is_active = true`.
8. Request values are bound as parameters. Sector values match `^[a-z0-9_]{1,64}$` before they are joined into the bound CSV parameter.
9. A malformed stored JSON value degrades only its own field, to null, `[]`, or a skipped element, and logs one WARN with no content. It never causes a 500.
10. Mapping JSON names equal the DTO `@JsonProperty` names. Success bodies are `ApiResponse`, or the D-5 reviews variant with the same keys plus `rating_summary`.

## 4. State ownership, grain, and keys

Not applicable as a change: the API owns no state. The keys are fixed by the DDL and `services/data-serving-service/AGENTS.md` "Contract": `srv_poi_info(poi_id)`, `srv_poi_multi_lang(poi_id, lang)`, `srv_poi_media_gallery(media_id, poi_id)`, `srv_poi_review(review_id)`. Output grain is one item per `poi_id` for compact and features, per `(media_id, poi_id)` for gallery, and per `review_id` for reviews. Experiences and practical_info return one object per `poi_id`. Review `rating_count`/`rating_overall` are POI-level: gold joins one `slv_3p_poi_rating` row per `poi_id` and stops on duplicates (`docs/context/mapping_gld_srv_poi_review.md` line 7).

## 5. Alternatives (material)

1. **Features selection: one native SQL query with a window rank (selected), versus Java interleaving, versus Specifications.**
   - Java interleaving loads every eligible row per request. Memory grows with the table, and paging is done in memory.
   - Specifications cannot express `row_number()`.
   - Native SQL takes one round trip, pages exactly, and bounds memory to `size`.
   - Cost: this is the first native query in the service. It departs from the AGENTS rule "filters go through `PoiSpecifications`", although it keeps that rule's purpose, which is bound parameters only. `jpa-performance-reviewer` must accept it.
2. **Sector array binding: CSV plus `string_to_array` (selected), versus a bound `String[]`.**
   - Hibernate 7 native array binding relies on type inference that this repository has not tested.
   - A text parameter is safe once sector values are regex-checked, so they cannot contain a comma.
3. **Reviews envelope (D-5): a nested record in `PoiReviewItemResponse.java` (selected), versus a new file, versus a change to `common/dto/ApiResponse`.**
   - The nested record keeps scope unchanged and leaves the shared envelope untouched.
   - The trade-off is a slightly unusual type location, `PoiReviewItemResponse.ReviewsResponse`.
4. **Compact absent body: 400 `ERR_BAD_REQUEST` (selected) versus 422.**
   - Spring raises `HttpMessageNotReadableException` for a missing body, so the D-6 handler covers it.
   - `{}` and `{"ids":[]}` return 422, which satisfies D-4 "missing or empty `ids`".
5. **Multi-language fallback for features, experiences, and practical_info: per field (selected) versus per row.**
   - Probe P-3 shows many `en`/`ko` rows where `experience` is JSON `null` but `vi` has data.
   - Per-row fallback would return empty sections for those POIs.
6. **`holiday_exceptions` mapping: serving map (D-7 option A, recommended) versus gold normalization first (option B).** See §6.6.1.

## 6. Design per endpoint

### 6.1 Compact (`POST /api/v1/pois/compact`)

- `@PostMapping(value = "/compact", consumes = MediaType.APPLICATION_JSON_VALUE)` with `@Valid @RequestBody CompactPoiRequest request` and `@RequestHeader("Accept-Language", required = false)`. Remove `page`, `size`, and `sort`.
- `consumes` matters: a wrong `Content-Type` then fails during handler mapping, which gives Spring's 415, and does not reach the catch-all 500 handler.
- `CompactPoiRequest(String lang, @NotEmpty @Size(max = 20) List<@NotBlank @Size(max = 128) String> ids)`.
  - `{}`, `[]`, 21 ids, or a blank id: 422 `ERR_VALIDATION_FAILED`, through `MethodArgumentNotValidException` or `HandlerMethodValidationException`. Both are already mapped.
  - Malformed or absent body: 400 (§6.7).
  - `GET /compact`: 405. The advice has `basePackages`, so it does not apply when no handler is found, and Spring's default resolver returns 405.
- Service: `getCompactPois(List<String> ids, String lang)` returns `List<CompactPoiResponse>`.
  - Calls `poiInfoRepository.findAll(PoiSpecifications.filter(ids), Sort.by(Sort.Order.desc("createdAt"), Sort.Order.asc("poiId")))`. There is no page and no count. The result has at most 20 rows, because `ids` are distinct primary keys.
  - Remove the gallery batch query, `parseSort`, and `resolveMimeType`, if nothing else uses them.
- Cover: `new Cover(poi.getCoverId(), poi.getCoverBlobUrl())`, or `null` when both are null.
  - `Cover` becomes `(id, file_key)`. Remove the 5-argument constructor.
  - `BusinessTags` drops `business_sector_label` and `primaryCategoryLabel()`. Search for callers of all removed members.
- Response: `ApiResponse.success(items, "Compact POIs retrieved successfully")`. There is no `meta.pagination`, because `ApiMeta` is `NON_NULL`.

### 6.2 Gallery (`GET /{poi_id}/gallery`)

- Controller: `page` (default 0, `@Min(0)`) and `size` (default 20, `@Min(1) @Max(100)`). Returns `ApiResponse.successList(items, PaginationMeta.offset(page, size, total), ...)`.
- Repository (replaces both existing gallery queries):

```java
String ACTIVE = "m.poiId = :poiId AND (m.isActive IS NULL OR m.isActive = true) AND m.deletedAt IS NULL";

@Query(value = "SELECT m FROM SrvPoiMediaGallery m WHERE " + ACTIVE
        + " ORDER BY m.displayOrder ASC NULLS LAST, m.mediaId ASC",
       countQuery = "SELECT count(m) FROM SrvPoiMediaGallery m WHERE " + ACTIVE)
Page<SrvPoiMediaGallery> findActivePageByPoiId(@Param("poiId") String poiId, Pageable pageable);

@Query("SELECT m FROM SrvPoiMediaGallery m WHERE " + ACTIVE + " AND m.isCover = true"
        + " ORDER BY m.displayOrder ASC NULLS LAST, m.mediaId ASC")
List<SrvPoiMediaGallery> findActiveCoverByPoiId(@Param("poiId") String poiId, Pageable pageable);
```

  Pass `PageRequest.of(page, size)` with no `Sort`. Call `findActiveCoverByPoiId` with `PageRequest.of(0, 1)`. Delete `findActiveByPoiIdInOrderByDisplayOrderAsc` and `findActiveByPoiIdOrderByDisplayOrderAsc`, and update `PoiRepositoryIntegrationTest`.
- `PoiGalleryItemResponse(@JsonProperty("id") String id, @JsonProperty("file_key") String fileKey, @JsonProperty("display_order") Integer displayOrder)` with `@JsonInclude(ALWAYS)`. `file_key` is `blob_url` exactly as stored, with no `photo_api_uri` fallback.
- An unknown `poi_id` returns 200, `data: []`, and `total_items: 0`. The service never calls `poiInfoRepository`.

### 6.3 Reviews (`GET /{poi_id}/reviews`)

- Remove `validatePoiExists`. Sort with `Sort.by(Sort.Order.desc("reviewDate"), Sort.Order.asc("reviewId"))` through the existing `findByPoiIdAndDeletedAtIsNull`.
- `rating_summary`:
  - If the page has content, take `content.getFirst()`.
  - Else, if `total > 0` (page past the end), take the first row of `findByPoiIdAndDeletedAtIsNull(poiId, PageRequest.of(0, 1, Sort.by("reviewId")))`.
  - Else return `[]`.
  - When a source row exists, return exactly one element `{rating_count: Long, rating_avg_score: Double}`. The values may be null.
  - The summary does not depend on `page`, because the values are POI-level (§4).
- `PoiService.ReviewsPage(PageResponse<PoiReviewItemResponse> page, List<PoiReviewItemResponse.RatingSummary> ratingSummary)` is a nested record.
- Controller: `ReviewsResponse.of(ApiResponse.successList(...), summary)`.

#### 6.3.1 Reviews DTO additions (inside `PoiReviewItemResponse.java`)

```java
@JsonInclude(JsonInclude.Include.ALWAYS)
public record RatingSummary(
        @JsonProperty("rating_count") Long ratingCount,
        @JsonProperty("rating_avg_score") Double ratingAvgScore) {}

@JsonInclude(JsonInclude.Include.ALWAYS)
@JsonPropertyOrder({"success", "code", "message", "data", "rating_summary", "meta", "errors"})
public record ReviewsResponse(boolean success, int code, String message,
        List<PoiReviewItemResponse> data,
        @JsonProperty("rating_summary") List<RatingSummary> ratingSummary,
        ApiMeta meta, List<ApiErrorDetail> errors) {
    public static ReviewsResponse of(ApiResponse<List<PoiReviewItemResponse>> base, List<RatingSummary> summary) {
        return new ReviewsResponse(base.success(), base.code(), base.message(), base.data(),
                summary == null ? List.of() : summary, base.meta(), base.errors());
    }
}
```

### 6.4 Features (`GET /features`)

- Parameters, all optional:
  - `lang`, plus header `Accept-Language`.
  - `page`: default 0, `@Min(0)`.
  - `size`: default 10, `@Min(1) @Max(100)`.
  - `business_sector_priority`: `List<String>`, default `attraction,f_n_b,event,tour_n_activities`, `@Size(max = 20)`.
  - `fallback_min_rating`: `BigDecimal`, default 4.5, `@DecimalMin("0") @DecimalMax("5")`.
  - `fallback_min_review_count`: `int`, default 100, `@Min(0)`.
  - `rating_source`: `String`, `@Size(max = 64)`.
- Normalization in the service:
  - Sectors: lowercase and trim, drop blanks, dedupe in first-seen order. Any value outside `^[a-z0-9_]{1,64}$` throws `IllegalArgumentException("business_sector_priority contains an invalid value")`, which returns 400 without echoing the value. An empty list after cleaning uses the default.
  - `rating_source`: lowercase and trim. Blank becomes `""`.
- Selection follows D-2 and §6.4.1.
  - Sector filtering already excludes stored null and blank sectors, and excludes `accommodation` unless the client lists it.
  - Within a sector, the partner pool (`is_recommended`) comes first, then fallback rows.
  - The global order takes one POI per sector per round, in priority order. `page`/`size` slice that order.
  - `total_items` comes from a count query with the same predicate.
- Then `findAllById(ids)`, skipping any row whose `deletedAt` is set, plus a batch multi-lang query (`findByPoiIdInAndLangIn`). Map items in the id order the SQL returned.
- `PoiFeatureResponse`, top level `@JsonInclude(ALWAYS)`:
  - `id`, `name`.
  - `description`: per-field fallback (§5.5).
  - `cover {id, file_key}`: from `cover_id`/`cover_blob_url`. Always an object, with null members when there is no cover.
  - `ratings`: `List<Rating{source, ratings_count, ratings_avg_score}>`. One element from info `source_name`/`rating_count`/`rating_overall` when either rating is non-null, else `[]`.
  - `business_tags {business_sector, business_category, subcategory_tags}`: `subcategory_tags` through `SubcategoryTagsParser`.
  - `status {operating_status, is_verified, is_recommended, is_bookable}`.
  - `operating_hours`: `List<OperatingHour>` or null (§6.6).
  - `address` and `geo_location`: reuse `CompactPoiResponse.Address` and `CompactPoiResponse.GeoLocation` with the same null rules as compact.
- Response: `ApiResponse.successList(items, PaginationMeta.offset(page, size, total), "Featured POIs retrieved successfully")`.

#### 6.4.1 Features SQL (constants in `SrvPoiInfoRepository`)

```java
String FEATURE_WHERE = """
    i.deleted_at IS NULL
    AND lower(trim(i.business_sector)) = ANY (string_to_array(:sectorsCsv, ','))
    AND ( i.is_recommended IS TRUE
       OR ( i.rating_overall >= :minRating
        AND i.rating_count >= :minReviewCount
        AND (:ratingSource = '' OR lower(trim(i.source_name)) = :ratingSource) ) )
    """;

@Query(nativeQuery = true, value = """
    SELECT c.poi_id FROM (
      SELECT i.poi_id,
             array_position(string_to_array(:sectorsCsv, ','), lower(trim(i.business_sector))) AS sector_rank,
             row_number() OVER (PARTITION BY lower(trim(i.business_sector))
                 ORDER BY CASE WHEN i.is_recommended IS TRUE THEN 0 ELSE 1 END,
                          i.rating_overall DESC NULLS LAST, i.rating_count DESC NULLS LAST, i.poi_id) AS sector_seq
      FROM apps.srv_poi_info i WHERE """ + FEATURE_WHERE + """
    ) c ORDER BY c.sector_seq, c.sector_rank, c.poi_id
    LIMIT :limit OFFSET :offset
    """)
List<String> findFeatureIds(@Param("sectorsCsv") String sectorsCsv, @Param("minRating") BigDecimal minRating,
        @Param("minReviewCount") int minReviewCount, @Param("ratingSource") String ratingSource,
        @Param("limit") int limit, @Param("offset") long offset);

@Query(nativeQuery = true, value = "SELECT count(*) FROM apps.srv_poi_info i WHERE " + FEATURE_WHERE)
long countFeatures(@Param("sectorsCsv") String sectorsCsv, @Param("minRating") BigDecimal minRating,
        @Param("minReviewCount") int minReviewCount, @Param("ratingSource") String ratingSource);
```

Pass `offset` as `(long) page * size`. `ratingSource` is never null (`""` when absent), so PostgreSQL needs no cast to infer its type.

### 6.5 Experiences (`GET /{poi_id}/experiences`)

- Parameters: `lang` and header `Accept-Language`. The language resolves through `LanguageResolver`. There is no existence check.
- One `findByPoiIdInAndLangIn(List.of(poiId), langs)` call, where `langs` is `{lang, vi}`.
- Candidate rows: the target row, then the `vi` row. The first row whose `StoredJsonParser.experiences(...)` result is non-empty wins. `source` is that row's `source_name` (D-1) on every item.
- Parser rules:
  - SQL null or JSON `null` gives `[]`.
  - Invalid JSON or a non-array gives `[]` and a WARN.
  - Elements that are not objects are skipped.
  - `title` and `description` are read as text. Non-text gives null.
  - An element is skipped when both are blank.
  - Keep the first 3 elements in stored order. Text is not truncated: the 50/150-character limit is the producer's rule, and the mapping states this.
- `PoiExperiencesResponse(items: List<Item{title, description, source}>)`. Nothing found gives 200 with `{items: []}`.
- Response: `ApiResponse.success(data, "POI experiences retrieved successfully")`.

### 6.6 Practical info (`GET /{poi_id}/practical_info`)

- Parameters: `lang` and header `Accept-Language`.
- `findByPoiIdAndDeletedAtIsNull`. If no row is found, `ResourceNotFoundException` gives 404 `POI_NOT_FOUND`, because this is a single-resource read.
- Multi-lang uses per-field fallback, target language then `vi`:
  - `description`: the first non-blank value.
  - `time_to_spend`, `cost` (from `cost_vnd`), `best_time`: `StoredJsonParser.labelValue`. A JSON object with exactly one text-valued entry gives `{label: key, value: text}` (probe P-4: `{"Thời gian đưa đón":"1 tiếng 15 phút"}`). Anything else gives null, with a WARN unless the stored value is SQL or JSON null.
- `cover`: the first row of `findActiveCoverByPoiId(poiId, PageRequest.of(0, 1))` gives `{id: media_id, file_key: blob_url}`, or null when there is no row. The gallery source is kept per D-1. The mapping type of `data.cover.id` changes from integer to string, because `media_id` is `text`.
- `ratings`: always an object, `{source: source_name, ratings_count, ratings_avg_score}` from info.
- `business_tags {business_sector, business_category}` and `status {…}`, as in features.
- `operating_hours`: `{value: List<OperatingHour>}`, or null when the stored value is null.
  - `StoredJsonParser.operatingHours` uses the gold shape (`docs/context/mapping_gld_srv_poi_info.md` §1.3).
  - Each element has `day_of_week` (int), `open_time`/`close_time` (string), and `is_open_all_day`/`is_closed` (boolean). Gold `label`/`value` are dropped.
  - An element without `day_of_week` or either boolean is skipped with a WARN. Invalid JSON or a non-array gives null and a WARN.
  - `OperatingHour` is `NON_NULL`, so closed days omit their times.
- `holiday_exceptions`: §6.6.1 (D-7).
- `address`, `geo_location`, `phone`, `email`, `website_url`, and `destinations {id: destination_id}` come from info. `destinations` is always an object.
- Response: `ApiResponse.success(data, "POI practical info retrieved successfully")`.

#### 6.6.1 `holiday_exceptions` (user decision D-7)

Stored shape (P-4 and p-shape): `[]`, or `[{"date":"02/09/2026","hours":[{"open_time":"09:30","close_time":"22:00"}],"title":"Ngày lễ","status":true}]`. There are 5 non-empty arrays, and every sampled element has `status: true` with hours present.

**Option A (recommended): map in serving.** `StoredJsonParser.holidayExceptions`:

1. SQL null gives null. `[]` gives `[]`. Invalid JSON or a non-array gives null and a WARN.
2. For each object element:
   - `date`: `dd/MM/yyyy` becomes `yyyy-MM-dd`. A value already in `yyyy-MM-dd` is kept. Anything else skips the element with WARN `BAD_DATE`.
   - `name`: `title`, with blank becoming null.
3. A closed day is `status == false`, or `hours` missing or empty. It produces one object: `{date, name, value: "Đóng cửa", is_open_all_day: false, is_closed: true}`.
4. Otherwise, each `hours[i]` in array order produces one object: `{date, name, open_time, close_time, value: open_time + " - " + close_time, is_open_all_day: false, is_closed: false}`. This mirrors the gold partner `operating_hours` rule (`mapping_gld_srv_poi_info.md` lines 96 and 324–325). An hours element missing either time is skipped with a WARN.

`HolidayException` is `NON_NULL`.

The user confirms two things: `status = false` means closed, and `value` reads "Đóng cửa" for every language, as gold `operating_hours` does.

**Option B: wait for gold normalization (G6).** A data task normalizes gold. Until then, `holiday_exceptions` is always null, and mapping rows 31–38 read "chờ G6". This leaves the Required = có fields unmet, so it is not recommended.

Only edit row 14 and the `holiday_exceptions` rows and sample in `practical_info.md` wait for D-7.

### 6.7 Malformed body (D-6)

```java
@ExceptionHandler(HttpMessageNotReadableException.class)
public ResponseEntity<ApiResponse<Void>> handleNotReadable(HttpMessageNotReadableException e) {
    return ResponseEntity.status(HttpStatus.BAD_REQUEST)
            .body(ApiResponse.error(HttpStatus.BAD_REQUEST, "Malformed or missing request body.", "ERR_BAD_REQUEST", null));
}
```

The handler uses a fixed message and never echoes `e.getMessage()`, which can contain payload fragments or class names. It is placed before the `Exception` handler, although the order does not matter because Spring matches the most specific type.

### 6.8 Mapping files

All six files get the same treatment:

- Required follows invariant 3. `Authorization` becomes không.
- Envelope rows follow `reviews.md`: `success`, `code` 200, ISO `meta.timestamp`, `meta.trace_id`, `meta.error_code`, `errors[]`. Each file gets a Status code table: 200, 400, 404 (or "không xảy ra"), 409, 422, 500.
- Samples equal the DTO JSON. Use only synthetic values.

Per file:

- **compact.md:** Method POST. A new `## Request body` table (`ids` có, 1–20; `lang` không). No `## Request param` section. Remove the cover rows for width, height, mime_type, and blur_hash, plus `business_sector_label` and every `meta.pagination` row. Cover sources are `apps.srv_poi_info.cover_id`/`cover_blob_url`. State the order.
  - 400 covers a malformed or absent body. 405 covers GET. 415 covers a non-JSON `Content-Type`. 422 covers `ids` that are missing, empty, longer than 20, or contain a blank element.
  - Do not mention `srv_poi_media_gallery` in `## Response`.
- **gallery.md:** Add `page` and `size`. Data rows are `id`, `file_key` (`apps.srv_poi_media_gallery.blob_url`), and `display_order`. Add the pagination rows. Order is `display_order ASC NULLS LAST, media_id ASC`. 404 reads "không xảy ra: không gọi `validatePoiExists`; POI không tồn tại trả 200, `data` rỗng". Do not mention `photo_api_uri` in `## Response`.
- **reviews.md:** Add `rating_summary` (array, sibling of `data`), `rating_summary[].rating_count` (`apps.srv_poi_review.rating_count`), and `rating_summary[].rating_avg_score` (`apps.srv_poi_review.rating_overall`), with the §6.3 rules. Order is `review_date DESC, review_id ASC`. 404 reads "không xảy ra".
- **features.md:** Remove `limit`. Rows are `data[].ratings[]`, the cover per D-1, and the selection text per D-2 (§6.4). Add full `meta.pagination`. 400 covers an invalid sector value.
- **experiences.md:** `data.items.source` comes from `apps.srv_poi_multi_lang.source_name`. Describe the fallback and the 3-item limit. A POI with no data returns 200 with `items: []`.
- **practical_info.md:** `data.cover.id` is a string. Add `data.ratings` and `data.destinations` object rows. Add 404 `POI_NOT_FOUND`. The `holiday_exceptions` rows follow D-7.

## 7. Ordering, transactions, idempotency, concurrency

- **Ordering:** §6. Every list ends on its primary key.
- **Transactions:** one read-only transaction per request, at the service method. Under READ COMMITTED, each statement sees its own snapshot.
  - Features: a gold sync between the id query and the count query can shift `total_items` by a few rows. A row deleted in between is skipped. This is accepted for a read API.
  - Reviews past the last page: the summary query runs in the same transaction.
- **Idempotency:** every endpoint is a pure read, including `POST /compact`. Repeating any request is harmless.
- **Concurrency:** no mutable shared state. `StoredJsonParser` follows `SubcategoryTagsParser`: a static utility with one `private static final ObjectMapper`, which is thread-safe once configured.

## 8. Retry, recovery, and partial failure

- **Retry:** callers may retry anything. The service adds no retries.
- **Partial failure:** a malformed stored field degrades only that field (invariant 9). A database error returns 500 through `handleUnexpected` and sends no partial body.
- **Recovery:** Not applicable: no state.

## 9. Observability

- `meta.trace_id` comes from `RequestIdFilter`, unchanged.
- `StoredJsonParser` logs a WARN line `stored_json_parse_failed poi_id={} field={} reason={}`, where `reason` is one of INVALID_JSON, NOT_ARRAY, NOT_OBJECT, BAD_ELEMENT, BAD_DATE. The line never includes content, because values may hold partner text.
- No metrics change.

## 10. Security (app-security-reviewer)

- **Input bounds:**
  - `ids`: 1 to 20 items, each ≤ 128 characters.
  - `size`: ≤ 100. `page`: ≥ 0.
  - `business_sector_priority`: ≤ 20 values, each matching the regex.
  - `rating_source`: ≤ 64 characters.
  - `fallback_*`: bounded.
  - `consumes` is JSON only.
- **SQL:** JPQL and native SQL use bound parameters only. Nothing is concatenated from the request. The sector CSV is built only from regex-validated values.
- **Errors:** the 400 body has a fixed message. 405 and 415 come from Spring's default resolver, as for any unmapped route. That is existing behavior.
- **PII:** `practical_info` returns `phone` and `email` because the user's mapping requires them. They are never logged. Flag this for `api-contract-reviewer` and `app-security-reviewer` (AGENTS "Do not log or return email, phone…").
- **Authorization:** documented, not enforced. This is the existing posture.

## 11. Performance (jpa-performance-reviewer)

- No N+1. Compact and features batch-load multi-lang with `IN`. Compact no longer queries the gallery.
- Practical info runs 3 single-row reads. Experiences runs 1.
- There are no indexes on `srv_poi_media_gallery.poi_id`, `srv_poi_review.poi_id`, or `srv_poi_info.business_sector`. Gallery and review page and count queries, and the features query, scan sequentially. P-1 counts about 292 live info rows, so this is acceptable now. This task cannot add DDL. Record a `backlog` entry for a data task: gallery index `(poi_id, display_order, media_id)`, review index `(poi_id)`.
- The features window function sorts only the filtered candidates. `LIMIT` bounds the rows returned.

## 12. Rollout

- One service deploy. `GET /compact` returns 405 afterwards, so every compact caller must switch to `POST` in the same release.
- `GET /gallery` and `GET /reviews` for an unknown POI change from 404 to 200 with an empty list.
- The mapping files ship in the same commit.
- **Runtime proof:** the user runs `runtime-runbook.md`. Main does not run `docker compose`. Steps:
  1. `docker compose up -d`.
  2. Apply the DDL per AGENTS "Commands".
  3. Load a synthetic fixture SQL, kept in the runbook, with no credentials or hosts: three sectors, partner and fallback rows, gallery rows with `is_cover`, reviews, multi-lang `en`/`vi` with `experience` JSON, and one `holiday_exceptions` element.
  4. Run curl for each endpoint, including the negative cases:
     - compact `{}` gives 422, malformed body gives 400, GET gives 405;
     - unknown gallery and reviews give 200 with `[]`;
     - unknown practical_info gives 404;
     - features `size=101` gives 422.
  5. Save the responses under `evidence/runtime/`.

## 13. Rollback and forward recovery

- **Rollback:** revert the commit and redeploy. There is no data or state change, so the rollback is complete. Compact callers must revert to GET at the same time.
- **Forward recovery:** a parser defect degrades one field only (invariant 9). Fix it forward.

## 14. Implementation plan

Follow the Main brief, "Order and stop points". Build compact, gallery, and reviews first, then run the maven lane. Next build the parser, features, experiences, and practical_info. Then update the mappings and run pytest. `holiday_exceptions` lands after D-7.

## 15. Verification

- `cd services/data-serving-service && mvnw.cmd -q -B test` (JDK 26 and Docker), including the test names in the brief.
- `python -m pytest tests/test_srv_poi_serving_contract.py tests/test_srv_poi_api_mapping_required.py -q`.
- `python scripts/vv.py verify 20261110-serving-poi-read-apis` with Docker. Only this sets `gates.local_verification = pass`.
- Runtime: the user runs the §12 runbook.

FILE: tests/test_srv_poi_api_mapping_required.py
"""Mapping contract for the six POI serving read APIs (task 20261110-serving-poi-read-apis).

Checks the Required rule (D-4), the ApiResponse envelope (D-3), the D-1 source columns,
the D-5 rating_summary placement, and that every cited apps.srv_poi_* column exists in the DDL.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MAPPING_DIR = ROOT / "docs" / "context" / "api-mapping"
DDL = ROOT / "sql" / "postgres" / "gld_srv_serve.pg.sql"
FILES = ("compact", "gallery", "reviews", "features", "experiences", "practical_info")
PATH_POI_ID_FILES = ("gallery", "reviews", "experiences", "practical_info")
REQUEST_SECTIONS = ("Request header", "Request param", "Request body")
ENVELOPE_KEYS = {"success", "code", "message", "data", "meta", "errors"}
PAGINATION_KEYS = {"type", "page", "per_page", "total_items", "total_pages", "has_next", "has_prev"}


def _text(name: str) -> str:
    return (MAPPING_DIR / f"{name}.md").read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str | None:
    match = re.search(rf"^## {re.escape(heading)}[ \t]*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return match.group(1) if match else None


def _rows(section: str | None) -> list[dict[str, str]]:
    if not section:
        return []
    lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        return []
    header = [cell.strip() for cell in lines[0].strip("|").split("|")]
    return [dict(zip(header, (cell.strip() for cell in line.strip("|").split("|")))) for line in lines[2:]]


def _request_rows(name: str) -> list[tuple[str, dict[str, str]]]:
    text = _text(name)
    return [(heading, row) for heading in REQUEST_SECTIONS for row in _rows(_section(text, heading))]


def _sample_response(name: str) -> dict:
    section = _section(_text(name), "Sample response")
    assert section, f"{name}.md has no Sample response section"
    match = re.search(r"```json[ \t]*\n(.*?)\n```", section, re.S)
    assert match, f"{name}.md Sample response has no json block"
    return json.loads(match.group(1))


def _ddl_columns() -> dict[str, set[str]]:
    tables: dict[str, set[str]] = {}
    ddl = DDL.read_text(encoding="utf-8")
    for table, body in re.findall(r"CREATE TABLE apps\.(\w+) \((.*?)\n\);", ddl, re.S):
        tables[table] = {m.group(1) for m in re.finditer(r"^\s+(\w+)\s+\w", body, re.M) if m.group(1) != "PRIMARY"}
    return tables


@pytest.mark.parametrize("name", FILES)
def test_only_path_poi_id_or_compact_body_ids_is_required(name):
    rows = _request_rows(name)
    assert rows, f"{name}.md has no request table"
    for heading, row in rows:
        field, required = row.get("Field", ""), row.get("Required", "")
        assert required in {"có", "không"}, f"{name}.md {heading} {field}: Required={required!r}"
        if required == "có":
            expected = ("Request body", "ids") if name == "compact" else ("Request param", "poi_id")
            assert (heading, field) == expected, f"{name}.md {heading} {field} must be Required = không"


@pytest.mark.parametrize("name", PATH_POI_ID_FILES)
def test_path_poi_id_is_required(name):
    params = {row["Field"]: row for heading, row in _request_rows(name) if heading == "Request param"}
    assert params["poi_id"]["Required"] == "có"


def test_compact_is_post_with_required_body_ids():
    text = _text("compact")
    assert re.search(r"^\|\s*Method\s*\|\s*POST\s*\|", _section(text, "Tổng quan") or "", re.M)
    body = {row["Field"]: row for row in _rows(_section(text, "Request body"))}
    assert body["ids"]["Required"] == "có"
    assert body["lang"]["Required"] == "không"
    other = {row["Field"] for heading, row in _request_rows("compact") if heading != "Request body"}
    assert not other & {"ids", "page", "size", "sort", "poi_id"}


@pytest.mark.parametrize("name", FILES)
def test_sample_response_uses_api_response_envelope(name):
    body = _sample_response(name)
    expected = ENVELOPE_KEYS | ({"rating_summary"} if name == "reviews" else set())
    assert set(body) == expected
    assert body["success"] is True
    assert body["code"] == 200
    assert body["errors"] is None
    assert isinstance(body["meta"]["timestamp"], str)
    assert isinstance(body["meta"]["trace_id"], str)


@pytest.mark.parametrize("name", ("gallery", "reviews", "features"))
def test_paged_sample_has_full_offset_pagination(name):
    assert set(_sample_response(name)["meta"]["pagination"]) == PAGINATION_KEYS


@pytest.mark.parametrize("name", ("compact", "experiences", "practical_info"))
def test_unpaged_sample_has_no_pagination(name):
    assert "pagination" not in _sample_response(name)["meta"]


def test_compact_sample_drops_omitted_fields():
    item = _sample_response("compact")["data"][0]
    assert set(item["cover"]) == {"id", "file_key"}
    assert "business_sector_label" not in item["business_tags"]


def test_gallery_sample_item_has_three_keys():
    assert set(_sample_response("gallery")["data"][0]) == {"id", "file_key", "display_order"}


def test_reviews_rating_summary_is_one_element_sibling_of_data():
    body = _sample_response("reviews")
    assert isinstance(body["data"], list)
    assert len(body["rating_summary"]) == 1
    assert set(body["rating_summary"][0]) == {"rating_count", "rating_avg_score"}


def test_d1_source_columns():
    for name in ("compact", "features"):
        response = _section(_text(name), "Response") or ""
        assert "apps.srv_poi_info.cover_id" in response, name
        assert "apps.srv_poi_info.cover_blob_url" in response, name
        assert "srv_poi_media_gallery" not in response, name
    experiences = _section(_text("experiences"), "Response") or ""
    assert "apps.srv_poi_multi_lang.source_name" in experiences
    assert not re.search(r"apps\.srv_poi_multi_lang\.source(?!_name)", experiences)
    gallery = _section(_text("gallery"), "Response") or ""
    assert "apps.srv_poi_media_gallery.blob_url" in gallery
    assert "photo_api_uri" not in gallery


@pytest.mark.parametrize("name", FILES)
def test_cited_source_columns_exist_in_ddl(name):
    tables = _ddl_columns()
    for table, column in re.findall(r"apps\.(srv_poi_\w+)\.(\w+)", _text(name)):
        assert table in tables, f"{name}.md cites unknown table apps.{table}"
        assert column in tables[table], f"{name}.md cites missing column apps.{table}.{column}"
END_FILE
