RESULT: PASS

## Main brief

### Decision
Fix JPA-002 (D-ANY) and add the D-PERF fast path. Resolution, filters, sort, page and total run in one native statement in `SrvPoiLegacyIdMapRepositoryImpl`. Id predicates are `= ANY (CAST(:ids AS text[]))` on the primary-key columns, and the total comes from `count(*) OVER ()`.
GET and POST practical_info share that statement and one assembler. Budget: at most 3 statements per request, down from 4–5.
No change to the contract, DDL, docs or Python tests. No index (D-IDX is a separate, non-blocking user decision).
Rejected: keeping the Specification (it cannot express `= ANY`), one big LATERAL statement, caching, and reading cover from `srv_poi_info.cover_*` (that rule differs).

### Invariants Main must preserve
- I1: the resolution SQL exists once, in `HIT_CTE`. A deleted or live `srv_poi_info` row with `poi_id = x` keeps `x`. Only `OK` rows with a non-null `poi_id` resolve.
- No SQL statement contains `@>`. Ids bind as one `text[]`. No `IN` list has more than 100 placeholders.
- POST with all fields uses ≤3 statements. With `required_fields=id,name` it uses exactly 1. Past the last page it uses 2. GET practical_info uses ≤3, and an unknown id uses exactly 1 (404).
- POST item without `required_fields` equals GET `data` (same code path).
- A legacy id and a new id of the same POI give one item. `total_items` counts distinct, non-deleted, filtered POIs.
- Order: the column in the chosen direction with NULLS LAST, then `i.poi_id ASC`. Default order is `i.poi_id ASC`.
- ORDER BY text comes only from the `SortColumn` constants. LIKE escapes `! % _` with `!`. Request text is never concatenated.
- With `enable_seqscan = off`, the plans use `srv_poi_legacy_id_map_pkey` and `srv_poi_info_pkey`, with no Seq Scan on those tables.
- The GET 404 message still echoes the input id. HTTP contract and DDL are unchanged.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| 1 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryCustom.java | whole file | Save the FILE block verbatim (records `Resolution`, `PracticalInfoSlice`; enum `SortColumn`) | compiles |
| 2 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryImpl.java | whole file | Save the FILE block verbatim (`HIT_CTE`, `RESOLVE_SQL`, `PRACTICAL_INFO_COUNT_SQL`, page SQL maps, `findResolvable`, `findPracticalInfoPage`) | repo tests #10–#14 pass |
| 3 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiIdResolver.java | `resolveAll` | Iterate `List<Resolution>`; use `row.legacyPoiId()` and `row.poiId()`; drop the entity import | compiles; resolver behaviour unchanged |
| 4 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PracticalInfoQuery.java | `enum SortField` | Replace `attribute` with `SortColumn column`: ID→POI_ID, NAME→POI_NAME, RATINGS_AVG_SCORE→RATING_OVERALL, RATINGS_COUNT→RATING_COUNT | `sortRegexMatchesEnumKeys` green |
| 5 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java | fields | Add `private final SrvPoiLegacyIdMapRepository legacyIdMapRepository;` | compiles |
| 6 | same | `getPracticalInfo` | Per architecture §18 "Service sketch": `findPracticalInfoPage(List.of(poiId), null, null, null, false, 1, 0)`; empty result throws 404 with the input id; return `assemble(..., ALL).getFirst()` | GET tests green; ≤3 statements |
| 7 | same | `searchPracticalInfo` | Per §18 sketch: one repository call, then `assemble`, then projection | POST tests green |
| 8 | same | new private `assemble` | Batch multi_lang only if description, time_to_spend, cost or best_time is selected; batch cover only if cover is selected; call `buildPracticalInfo` per row | `searchPracticalInfoSkipsMultiLangAndCoverWhenNotSelected` green |
| 9 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiSpecifications.java | `practicalInfo`, `likePattern` | Delete both and the unused imports; keep `filter` | no `arrayContains` remains in `src/main` |
| 10 | services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/domain/repository/PoiRepositoryIntegrationTest.java | `legacyMapFindResolvableKeepsOnlyOkAndNewIdPrecedence` | Extract `Resolution::legacyPoiId` | green |
| 11 | same | new `practicalInfoPageResolvesLegacyDedupesAndExcludesDeleted`, `practicalInfoPageReturnsTotalWhenOffsetPastEnd` | Per §19 | green |
| 12 | same | new `practicalInfoPageOrdersEverySortColumnBothDirectionsNullsLastThenPoiId` | Per §19 | green |
| 13 | same | new `practicalInfoPageSqlOrderByComesOnlyFromConstants` | Regex check on `ASC_PAGE_SQL`, `DESC_PAGE_SQL`, `DEFAULT_PAGE_SQL` | green |
| 14 | same | new `idPredicatesUsePrimaryKeyIndexesWhenSeqScanDisabled` | `SET LOCAL enable_seqscan = off`; `EXPLAIN` `RESOLVE_SQL` and `PRACTICAL_INFO_COUNT_SQL` through a `NativeQuery`; assert both pkeys appear and no `Seq Scan on srv_poi_(info\|legacy_id_map)` | green |
| 15 | services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/LegacyAndPracticalInfoIntegrationTest.java | `postUsesAtMostFiveStatements` | Rename to `postUsesAtMostThreeStatements`; assert `isBetween(1, 3)` | green |
| 16 | same | `postOneHundredTwentyIdsStaysWithinStatementAndInLimits` | Bound ≤3; no SQL contains `@>`; some SQL contains `= ANY (CAST(` (case-insensitive) | green |
| 17 | same | new `getPracticalInfoUsesAtMostThreeStatements`, `postFieldsWithoutLangOrCoverUseOneStatement`, `postPastLastPageKeepsTotalItems` | Per §19 | green |
| 18 | services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java | mocks; 3 practical-info tests | Add `@Mock SrvPoiLegacyIdMapRepository`; stub `findPracticalInfoPage` and `findActiveCoversByPoiIdIn` instead of `findAll(Specification, Pageable)`, `findByPoiIdAndDeletedAtIsNull` and `findActiveCoverByPoiId` | green |
| 19 | services/data-serving-service/AGENTS.md | `## Contract`, resolution and filter bullets | Text from §18 step 7 (native-SQL exception, `= ANY` text[] rule, `HIT_CTE` as the single definition) | text present |
| 20 | .ai/tasks/20261125-practical-info-query-legacy-poi-id/runtime-runbook.md | after step 5 | Add the PREPARE/EXPLAIN probe from §19 Runtime (default and seqscan off, plus the cover query for D-IDX); no hosts or tokens | step present |

### Order and stop points
1. S0 (user stop only if blocked): D-ANY allows one more verify round (`rounds.verification` = 3). If `vv.py` refuses, stop and ask the user. Make sure Docker is running (the context pack says it is down).
2. Rows 1–4, 9, then 10–14. Run `mvnw.cmd -q -B test -Dtest=PoiRepositoryIntegrationTest`.
3. S1 (evidence, no user stop): if the `addEntity` + `addScalar` mapping fails, apply fallback F1 (§6): ids+total statement, then a JPQL `IN` load of ≤100 ids reordered in Java. Raise the bounds to 4 (all fields) and 2 (no lang or cover), and record F1 in `decision.md` `## Lịch sử quyết định`. If binding `String[]` as `text[]` fails, stop and report. Never fall back to `IN` over more than 100 ids or to CSV.
4. Rows 5–8, then 15–18. Run the full `mvnw.cmd -q -B test` and the Python tests.
5. Row 19, then row 20.
6. S2 (evidence): run `python scripts/vv.py verify 20261125-practical-info-query-legacy-poi-id` (round 3), then review round 3 with `jpa-performance-reviewer` (JPA-002) and `app-security-reviewer` (native SQL, ORDER BY constants). Set JPA-002 to `fixed` only after the review passes.
7. S3 (user): runtime per `runtime-runbook.md`.
8. S4 (user decision, non-blocking): D-IDX, a backlog task for `poi_id` indexes on `srv_poi_media_gallery` and `srv_poi_review`, decided on the runbook cover probe. Recommendation: backlog. Not part of this task.

### Tests and verification
- `python -m pytest tests/test_srv_poi_serving_contract.py tests/test_srv_poi_api_mapping_required.py -q`: unchanged, must stay green.
- `cd services/data-serving-service && mvnw.cmd -q -B test` (JDK 26, Docker).
- `PoiRepositoryIntegrationTest`:
  - `legacyMapFindResolvableKeepsOnlyOkAndNewIdPrecedence`
  - `practicalInfoPageResolvesLegacyDedupesAndExcludesDeleted`
  - `practicalInfoPageReturnsTotalWhenOffsetPastEnd`
  - `practicalInfoPageOrdersEverySortColumnBothDirectionsNullsLastThenPoiId`
  - `practicalInfoPageSqlOrderByComesOnlyFromConstants`
  - `idPredicatesUsePrimaryKeyIndexesWhenSeqScanDisabled`
- `LegacyAndPracticalInfoIntegrationTest`:
  - all existing tests;
  - `postUsesAtMostThreeStatements`
  - `postOneHundredTwentyIdsStaysWithinStatementAndInLimits`
  - `getPracticalInfoUsesAtMostThreeStatements`
  - `postFieldsWithoutLangOrCoverUseOneStatement`
  - `postPastLastPageKeepsTotalItems`
- `PoiServiceTest`: `searchPracticalInfoSkipsMultiLangAndCoverWhenNotSelected`, `shouldReturnPracticalInfoDestinationsAndNoTopLevelBusinessSector`, `shouldThrowWhenPracticalInfoPoiMissing`.
- Unchanged and expected green: `PoiControllerIntegrationTest`, `PracticalInfoProjectionTest`, `PracticalInfoBodyLimitFilterTest`, `ApiBearerAuthTest`.
- `python scripts/vv.py verify 20261125-practical-info-query-legacy-poi-id`, then review round 3.
- Runtime: the user follows the runbook probe. Pass when both pkeys are used with `enable_seqscan = off`. A Seq Scan with default settings on tiny compose data is not a failure.

### Read only if needed
- §6 "Alternatives and selected trade-off" and "Fallback F1": rows 1, 2, 6, 7; stop S1.
- §8 "Ordering and data flow" and "SQL": rows 2, 6–8, 14.
- §15 "Security": rows 2, 13, 19.
- §16 "Rollout": stops S0 and S4.
- §18 "Implementation plan" and "Service sketch": rows 3–9, 19.
- §19 "Verification" and "Runtime": rows 10–18, 20.
- FILE blocks: rows 1 and 2.

# Architecture round 2 (D-ANY, D-PERF): 20261125-practical-info-query-legacy-poi-id

This round replaces the architecture written in round 1. That design was implemented and passed verify twice. Review round 2 left one finding open, JPA-002: both id predicates render as `? @> ARRAY[column]`, which cannot use a B-tree. D-ANY settles the predicate: `column = ANY(:ids)` with one `text[]` parameter. D-PERF asks for a fast path on practical info because it serves many requests.

Nothing changes in the HTTP contract, the DTOs, the DDL, the mapping docs or the Python contract tests. The normative contract is still `docs/context/api-mapping/practical_info_list.md`, `practical_info.md`, and the `PoiController` methods `searchPracticalInfo` and `getPracticalInfo`. Grain and keys still come from `model-design.md` `## Entities and grain` and `## Keys`, implemented at `sql/postgres/gld_srv_serve.pg.sql:145-151`.

## 1. Scope

- Fix JPA-002. The id predicates become `= ANY (CAST(:ids AS text[]))`: legacy resolution on `apps.srv_poi_legacy_id_map.legacy_poi_id`, and the filter on `apps.srv_poi_info.poi_id`.
- Fast path for practical info:
  - Resolution, filters, sort, paging and total run in one SQL statement.
  - `GET /{poi_id}/practical_info` and `POST /practical_info` share that statement and one assembler.
  - With every field selected, a request runs at most 3 statements. Today the POST runs up to 5 and the GET runs 4.
- One textual definition of the resolution rule (I1). It is the SQL constant `HIT_CTE`, which both the resolver statement and the practical-info statement use.
- Tests that prove index usability, the statement budget and unchanged behaviour. One AGENTS.md rule change. A runbook probe.

## 2. Non-goals

- No change to the contract, error codes, validation, `size ≤ 100` or the 500-id cap (D-ID-UNIT).
- No DDL change and no index. The DDL header rule "không tạo ... index" stands. A `poi_id` index on `srv_poi_media_gallery` or `srv_poi_review` is the separate decision D-IDX (§16, S4).
- No cache: no response cache and no resolution cache.
- No change to the multi_lang and cover batch loads. They stay JPQL `IN` over at most 100 page ids, which round 2 accepted.
- No change to gallery, reviews, experiences, amenities or compact beyond the resolver's new SQL.
- `cover` still comes from `srv_poi_media_gallery` and not from `srv_poi_info.cover_*` (§6 B6).
- NUL bytes in body ids still produce 500, as `/compact` already does. This behaviour predates the task and is not addressed here.

## 3. Invariants

- I1. Resolution. Input `x` resolves to `m.poi_id` only when all of these hold:
  - a map row has `legacy_poi_id = x`, `poi_id_status = 'OK'` and `poi_id IS NOT NULL`;
  - no `srv_poi_info` row has `poi_id = x`, whether deleted or not.

  Otherwise `x` resolves to itself. The rule's SQL text exists once, in `SrvPoiLegacyIdMapRepositoryImpl.HIT_CTE`.
- I2. Same record. For every endpoint, a legacy id with an OK mapping and its new id give equal status, `data`, `rating_summary` and `meta.pagination`. `data.id` is the new id.
- I3. An unresolved id behaves like an unknown new id: 404 on GET practical_info, an empty 200 on the other single-id endpoints, and an omitted item on compact and the POST.
- I4. The POST returns one item per distinct resolved `poi_id` with `deleted_at IS NULL` that passes the filters. `total_items` counts those items.
- I5. With no `required_fields`, each POST item equals GET `data` for the same id and lang. Both now come from the same statement and the same assembler. With `required_fields`, an item has exactly the selected keys, in canonical order, and keeps nulls.
- I6. Whitelists are unchanged. No request text reaches SQL as text. The ORDER BY clause is one of 9 constant strings built from `SortColumn` enum constants.
- I7. Order: the chosen column in the chosen direction with `NULLS LAST`, then `i.poi_id ASC`. With no `sort_field`, the order is `i.poi_id ASC`.
- I8. Statement budget, whatever the number of ids:
  - POST: at most 3 statements. Fields without multi_lang or cover: 1. Past the last page: 2.
  - GET practical_info: at most 3. Unknown id: 1.
  - No statement contains `@>`. No `IN` list has more than 100 placeholders.
- I9. Every id predicate on a primary-key column can use the primary-key index. A test proves that the plan uses `srv_poi_info_pkey` and `srv_poi_legacy_id_map_pkey` and has no `Seq Scan` on those tables when `enable_seqscan = off`.
- I10. The service is read-only and reads only schema `apps`. An empty map table is safe.

## 4. State ownership

Unchanged from round 1. Map rows belong to the data side (D-LEGACY-MAP (c)). The API only reads them. Rule I1 belongs to `SrvPoiLegacyIdMapRepositoryImpl` and is called through `PoiIdResolver` (single-id endpoints and compact) and `findPracticalInfoPage` (practical info).

## 5. Grain and keys

No change. The tables are defined in `model-design.md` `## Entities and grain` and `## Keys`. Endpoint grain:

- GET returns one POI as one object.
- POST returns one item per resolved `poi_id`, filtered and paged.

The new statement reads only the primary keys `srv_poi_legacy_id_map(legacy_poi_id)` and `srv_poi_info(poi_id)`.

## 6. Alternatives and selected trade-off

Statement count per request:

| Path | Today | B1 minimal | **B2 selected** | B3 one statement |
|---|---|---|---|---|
| POST, all fields | 4–5 | 4–5 | **3** | 1 |
| POST, no lang or cover field | 2–3 | 2–3 | **1** | 1 |
| GET practical_info | 4 | 4 | **3** | 1 |
| Resolve + page + total consistency | separate snapshots | separate | **one snapshot** | one |

- **B1. Swap predicates only.** Use a native resolver and keep the Spring Data Specification page.
  - Criteria has no portable `= ANY(?)`. `HibernateCriteriaBuilder.arrayContains` is what renders `@>`.
  - Getting `= ANY` would need a custom `FunctionContributor`, or would rely on how `cb.function("any", …)` renders a bound array, which is undocumented.
  - It keeps two extra round trips, and the count runs on a separate snapshot.
  - Rejected.
- **B2. Selected.** One native statement does resolve, filter, sort, `LIMIT/OFFSET`, and `count(*) OVER ()` for the total. It maps `SrvPoiInfo` entities with `addEntity` and the total with `addScalar`. GET reuses it with `limit 1`. Multi_lang and cover load in batch, only when selected.
  - Cost: native SQL in a repository fragment instead of `PoiSpecifications`. `getFeatures` already sets the precedent with `FEATURE_WHERE` and `findFeatureIds`. AGENTS.md is updated (§18 step 7).
  - The window total costs at most 500 rows before `LIMIT`.
  - A count statement runs only when a page past the end comes back empty.
- **B3. One statement for everything.** Multi_lang and cover would come through `LEFT JOIN LATERAL` into a ~40-column scalar projection.
  - Rejected. It needs a parallel row type and a second assembler (risk to I5).
  - The cover lookup has no `poi_id` index (`srv_poi_media_gallery` PK is `(media_id, poi_id)`), so its cost stays the same whether it is joined or separate.
  - It saves round trips only when those fields are selected.
- **B4. Cache resolutions or responses.** Rejected. Results go stale across data-side reloads, the service has no cache dependency, and the round-1 non-goal still applies.
- **B5. Add `poi_id` indexes on `srv_poi_media_gallery` and `srv_poi_review`.** This is likely the largest remaining gain for cover and reviews. It conflicts with the DDL rule "không tạo index", and the data side applies the DDL in every environment. It goes to the user as D-IDX (S4) and is not part of this task.
- **B6. Read `cover` from `srv_poi_info.cover_id` and `cover_blob_url`.** That would need no gallery query. Rejected: `mapping_gld_srv_poi_info.md` builds those columns from `is_cover` alone, without the `is_active` and `deleted_at` filters that `practical_info.md` row 11 requires. Values would change.

Why B2: it removes the non-sargable predicate, which is the cause of JPA-002. It cuts the round trips on the hot path by 1–2. It makes the page and the total consistent. It gives GET and POST one code path, so I5 holds by construction. It touches no contract and no DDL. A single SQL text per sort variant also means stable Hibernate plan-cache and pgJDBC server-prepared-statement reuse, which a variable-length `IN` list cannot give.

### Fallback F1 (deterministic, no user stop)

The mixed mapping (`addEntity("i", SrvPoiInfo.class)` plus `addScalar("total_items", LONG)`) could fail in Hibernate 7 at the first repository test run. In that case:

1. Change the page SQL to `SELECT i.poi_id, count(*) OVER () AS total_items` with the same FROM, ORDER BY and LIMIT.
2. Load the entities with `SELECT i FROM SrvPoiInfo i WHERE i.poiId IN :ids` (at most 100 ids).
3. Reorder the entities in Java to the id order.

The I8 bounds then become 4 for all-field POST and GET, and 2 for no-lang/no-cover POST. Record F1 under `## Lịch sử quyết định` in `decision.md` and update the bounds in the tests. Every other invariant stays.

If binding the `String[]` parameter as `text[]` fails, stop and report. Do not fall back to `IN` or to CSV with `string_to_array`: the shape of legacy ids is unknown, and they may contain commas.

## 7. Contract

Not applicable: the contract is unchanged. Normative sources are `practical_info_list.md`, `practical_info.md` and `PoiController`.

## 8. Ordering and data flow

POST `searchPracticalInfo(query)`, inside one `@Transactional(readOnly = true)`:

1. `legacyIdMapRepository.findPracticalInfoPage(ids, source, poiName, sortColumn, descending, size, page*size)`. This is one statement. It returns the page entities in SQL order and the total. If the page is empty and offset > 0, the repository runs `PRACTICAL_INFO_COUNT_SQL` (one statement). If the page is empty and offset is 0, the total is 0.
2. If the page is empty, return.
3. `assemble(rows, lang, selected)`:
   - when `description`, `time_to_spend`, `cost` or `best_time` is selected, run `loadLangs(pageIds, lang)`;
   - when `cover` is selected, run `findActiveCoversByPoiIdIn(pageIds)` and keep the first row per `poi_id`;
   - call `buildPracticalInfo` per row, in page order.
4. When `required_fields` is set, apply `PracticalInfoProjection.select`.

GET `getPracticalInfo(poiId, lang)`:

1. `findPracticalInfoPage(List.of(poiId), null, null, null, false, 1, 0)`.
2. No rows: throw `ResourceNotFoundException("POI not found with id: " + poiId)`. The message echoes the input id, as today.
3. `assemble(rows, lang, ALL).getFirst()`.

Other endpoints are unchanged. They call `PoiIdResolver.resolve` or `resolveAll`, which now runs `RESOLVE_SQL`, then their existing query.

### SQL (normative; full text in the FILE block)

```sql
WITH hit AS (
  SELECT m.legacy_poi_id, m.poi_id FROM apps.srv_poi_legacy_id_map m
  WHERE m.legacy_poi_id = ANY (CAST(:ids AS text[]))
    AND m.poi_id_status = 'OK' AND m.poi_id IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM apps.srv_poi_info x WHERE x.poi_id = m.legacy_poi_id))
SELECT {i.*}, count(*) OVER () AS total_items
FROM apps.srv_poi_info i
WHERE i.poi_id = ANY (ARRAY(SELECT COALESCE(h.poi_id, u.id)
                            FROM unnest(CAST(:ids AS text[])) AS u(id)
                            LEFT JOIN hit h ON h.legacy_poi_id = u.id))
  AND i.deleted_at IS NULL
  AND (:source = '' OR lower(trim(i.source_name)) = :source)
  AND (:namePattern = '' OR lower(i.poi_name) LIKE lower(:namePattern) ESCAPE '!')
ORDER BY <constant> LIMIT :limit OFFSET :offset
```

Plan intent:

- `hit` is an index scan on `srv_poi_legacy_id_map_pkey` with `Index Cond: legacy_poi_id = ANY($ids)`, plus an anti-join probe on `srv_poi_info_pkey`.
- `ARRAY(SELECT …)` is an InitPlan.
- The main scan is an index scan on `srv_poi_info_pkey` with `Index Cond: poi_id = ANY($initplan)`. B-tree array keys are de-duplicated, so a POI that appears through both a legacy id and a new id comes back once (I4).
- `count(*) OVER ()` is evaluated before `LIMIT`.
- The `source` and `poi_name` checks run as filters over at most 500 rows.

Design notes:

- The LIKE escape character is `!`, not `\`, so that Hibernate's native-SQL parameter parser never meets a backslash inside a quoted string. The pattern is lower-cased by PostgreSQL `lower()` on both sides.
- Absent filters bind `''` as a sentinel, as `FEATURE_WHERE` already does.

## 9. Transaction and commit boundaries

Every service method stays `@Transactional(readOnly = true)`. Resolution, filters, page and total now share one statement snapshot. Multi_lang and cover are separate statements under READ COMMITTED, as GET is today. No writes, so no commits.

## 10. Idempotency

Not applicable beyond round 1: every endpoint is a read without side effects.

## 11. Concurrency

- The service is stateless.
- A data-side reload between the page statement and the satellite statements can produce null multi_lang or cover fields for one response. This was already accepted for GET.
- A non-transactional map reload can make legacy ids miss for a short time; they then follow I3. The copy rule (one transaction) is unchanged.
- No shared mutable state: the static SQL map is built once at class initialisation and never modified.

## 12. Retry and recovery

Clients may retry. The service does not retry SQL. Failures go through `GlobalExceptionHandler` as 500 with the trace id.

## 13. Partial failure

| Failure | Effect | Response |
|---|---|---|
| Map table missing | 500 on every endpoint that takes a `poi_id`, as in round 1 | Rollout precheck R1 |
| Map empty | Legacy ids follow I3; new ids unaffected | Data side loads the map |
| Mixed native mapping fails in Hibernate 7 | Test failure at S1, not at runtime | F1 |
| `text[]` binding fails | Test failure at S1 | Stop and report |
| Cover or multi_lang missing | That field is null | Accepted |
| Planner picks Seq Scan on DEV-sized data | Slower, still correct | Runbook probe (§19), then D-IDX or a statistics check by the data side |

## 14. Observability

- The `PoiIdResolver` DEBUG count line is unchanged.
- No new metrics. Statement counts are proven by tests, not exported.
- The runbook gains an `EXPLAIN (ANALYZE, BUFFERS)` probe (§19).
- No log line ever contains ids from `phone`, `email` or `author_name`, or the token.

## 15. Security

- Every value is bound: `ids` as one `text[]`; `source`, `namePattern`, `limit` and `offset` as scalars.
- ORDER BY text is taken from `ASC_PAGE_SQL`, `DESC_PAGE_SQL` or `DEFAULT_PAGE_SQL`, all built at class initialisation from `SortColumn.sql()` constants. The request only selects an enum constant, which the controller has already checked against `SORT_REGEX`.
- A test asserts each built ORDER BY clause matches `^i\.[a-z_]+ (ASC|DESC) NULLS LAST, i\.poi_id ASC$` or equals `i.poi_id ASC`.
- LIKE metacharacters `!`, `%` and `_` are escaped with `!`.
- Body-size limits (SEC-001) and bearer authentication are unchanged.
- The service AGENTS.md is amended so the native-SQL exception is explicit, not silent.

## 16. Rollout

- S0. D-ANY authorizes one more fix, verify and review round, so `rounds.verification` may go to 3 for this fix only. If `vv.py` refuses to record it, stop and ask the user.
- R1 to R4 are unchanged from round 1. No DDL change, no config change; deploy the image.
- S4 (user decision, non-blocking). D-IDX: whether to open a backlog task that adds `CREATE INDEX` on `apps.srv_poi_media_gallery (poi_id)` and `apps.srv_poi_review (poi_id)`. That would change the DDL header rule, and the data side would apply it. Recommendation: backlog, decided on the result of the runbook cover probe. This task completes without it.

## 17. Rollback and forward recovery

- Rollback: redeploy the previous image. No state to migrate.
- Forward recovery: a wrong plan or a wrong bound is fixed in code. A wrong mapping is fixed by the data side reloading from gold.

## 18. Implementation plan

1. Write `SrvPoiLegacyIdMapRepositoryCustom.java` and `SrvPoiLegacyIdMapRepositoryImpl.java` verbatim from the FILE blocks. `SrvPoiLegacyIdMapRepository` already extends the Custom interface; no edit.
2. `PoiIdResolver.resolveAll`: iterate over `List<SrvPoiLegacyIdMapRepositoryCustom.Resolution>`, using `row.legacyPoiId()` and `row.poiId()`. Drop the `SrvPoiLegacyIdMap` import.
3. `PracticalInfoQuery.SortField`:
   - replace the field and accessor `attribute` with `SrvPoiLegacyIdMapRepositoryCustom.SortColumn column`;
   - the mapping is `ID→POI_ID`, `NAME→POI_NAME`, `RATINGS_AVG_SCORE→RATING_OVERALL`, `RATINGS_COUNT→RATING_COUNT`;
   - keys and the regexes are unchanged.
4. `PoiService`, following §Service sketch:
   - add the field `private final SrvPoiLegacyIdMapRepository legacyIdMapRepository;`;
   - rewrite `getPracticalInfo` and `searchPracticalInfo`;
   - add `private List<PoiPracticalInfoResponse> assemble(...)`;
   - `buildPracticalInfo` is unchanged;
   - remove the unused imports (`Order`, and `Page` only if it becomes unused).
5. `PoiSpecifications`: delete `practicalInfo` and `likePattern`, and the imports `HibernateCriteriaBuilder`, `Collection` and `Locale`. `filter` stays.
6. `SrvPoiMediaGalleryRepository`: no change. `findActiveCoverByPoiId` becomes unused in main code; keep it.
7. `services/data-serving-service/AGENTS.md` `## Contract`:
   - Resolution bullet: append "SQL text: `SrvPoiLegacyIdMapRepositoryImpl.HIT_CTE`, used by `RESOLVE_SQL` and the practical-info page."
   - Replace the filter bullet's second sentence with: "Filters go through `PoiSpecifications`, except fixed native SQL with bound parameters in `SrvPoiInfoRepository` (`findFeatureIds`, `countFeatures`) and `SrvPoiLegacyIdMapRepositoryImpl`. There, ORDER BY comes only from enum constants. Id lists bind as one `text[]` with `= ANY`; never `@>`, never `IN` over 100 ids. Never concatenate request values into JPQL or SQL."
8. Tests (§19), then `runtime-runbook.md` (§19 Runtime).

### Service sketch (normative behaviour)

```java
@Transactional(readOnly = true)
public PoiPracticalInfoResponse getPracticalInfo(String poiId, String targetLang) {
    List<SrvPoiInfo> rows = legacyIdMapRepository
            .findPracticalInfoPage(List.of(poiId), null, null, null, false, 1, 0).rows();
    if (rows.isEmpty()) {
        throw new ResourceNotFoundException("POI not found with id: " + poiId);
    }
    return assemble(rows, blankToDefault(targetLang), EnumSet.allOf(PracticalInfoQuery.Field.class)).getFirst();
}

@Transactional(readOnly = true)
public PracticalInfoPage searchPracticalInfo(PracticalInfoQuery query) {
    boolean project = query.fields() != null && !query.fields().isEmpty();
    EnumSet<PracticalInfoQuery.Field> selected = project ? query.fields() : EnumSet.allOf(PracticalInfoQuery.Field.class);
    SrvPoiLegacyIdMapRepositoryCustom.PracticalInfoSlice slice = legacyIdMapRepository.findPracticalInfoPage(
            query.ids(), query.source(), query.poiName(),
            query.sortField() == null ? null : query.sortField().column(),
            query.direction() == Sort.Direction.DESC,
            query.size(), (long) query.page() * query.size());
    if (slice.rows().isEmpty()) {
        return new PracticalInfoPage(List.of(), slice.total());
    }
    List<Object> items = new ArrayList<>(slice.rows().size());
    for (PoiPracticalInfoResponse dto : assemble(slice.rows(), blankToDefault(query.lang()), selected)) {
        items.add(project ? PracticalInfoProjection.select(dto, selected) : dto);
    }
    return new PracticalInfoPage(items, slice.total());
}

private List<PoiPracticalInfoResponse> assemble(List<SrvPoiInfo> rows, String lang,
        EnumSet<PracticalInfoQuery.Field> selected) {
    List<String> ids = rows.stream().map(SrvPoiInfo::getPoiId).toList();
    boolean loadLang = selected.contains(PracticalInfoQuery.Field.DESCRIPTION)
            || selected.contains(PracticalInfoQuery.Field.TIME_TO_SPEND)
            || selected.contains(PracticalInfoQuery.Field.COST)
            || selected.contains(PracticalInfoQuery.Field.BEST_TIME);
    Map<String, Map<String, SrvPoiMultiLang>> langs = loadLang ? loadLangs(ids, lang) : Map.of();
    Map<String, SrvPoiMediaGallery> covers = new HashMap<>();
    if (selected.contains(PracticalInfoQuery.Field.COVER)) {
        for (SrvPoiMediaGallery row : mediaGalleryRepository.findActiveCoversByPoiIdIn(ids)) {
            covers.putIfAbsent(row.getPoiId(), row);
        }
    }
    List<PoiPracticalInfoResponse> out = new ArrayList<>(rows.size());
    for (SrvPoiInfo poi : rows) {
        SrvPoiMediaGallery media = covers.get(poi.getPoiId());
        PoiPracticalInfoResponse.Cover cover = media == null ? null
                : new PoiPracticalInfoResponse.Cover(media.getMediaId(), media.getBlobUrl());
        out.add(buildPracticalInfo(poi, langs.getOrDefault(poi.getPoiId(), Map.of()), lang, cover, selected));
    }
    return out;
}
```

## 19. Verification

Python, unchanged and expected to stay green:

```
python -m pytest tests/test_srv_poi_serving_contract.py tests/test_srv_poi_api_mapping_required.py -q
```

Java: `cd services/data-serving-service && mvnw.cmd -q -B test`. This needs JDK 26 and a running Docker daemon; the context pack reports Docker down, so start Docker first.

`PoiRepositoryIntegrationTest`. Seed with `JdbcTemplate`, or with `saveAndFlush` before any native query.

- `legacyMapFindResolvableKeepsOnlyOkAndNewIdPrecedence`: update it to `.extracting(SrvPoiLegacyIdMapRepositoryCustom.Resolution::legacyPoiId).containsExactly("old")`. Remove the `SrvPoiLegacyIdMap` import if it becomes unused.
- New `practicalInfoPageResolvesLegacyDedupesAndExcludesDeleted`:
  - ids `[legacy→A, A, B(deleted), C]` give rows `[A, C]` and total 2;
  - a MISSING_EVIDENCE legacy id is not resolved.
- New `practicalInfoPageReturnsTotalWhenOffsetPastEnd`: 2 matches with `limit 1, offset 5` give no rows and total 2. With offset 0 and no matches, total is 0.
- New `practicalInfoPageOrdersEverySortColumnBothDirectionsNullsLastThenPoiId`: for each `SortColumn` × asc/desc, null values come last and ties order by `poi_id ASC`.
- New `practicalInfoPageSqlOrderByComesOnlyFromConstants`: every value of `ASC_PAGE_SQL`, `DESC_PAGE_SQL` and `DEFAULT_PAGE_SQL` contains `ORDER BY ` followed by a clause matching the §15 regex, then ` LIMIT :limit OFFSET :offset`. Expose the maps as package-private getters, or test through `pageSql`.
- New `idPredicatesUsePrimaryKeyIndexesWhenSeqScanDisabled`:
  1. In the test transaction, run `jdbcTemplate.execute("SET LOCAL enable_seqscan = off")`.
  2. Through the injected `EntityManager`, run `"EXPLAIN " + RESOLVE_SQL` and `"EXPLAIN " + PRACTICAL_INFO_COUNT_SQL` as `NativeQuery`, binding `ids` (`String[]` with 3 values via `setParameter(name, value, String[].class)`), `source` = `""` and `namePattern` = `""`.
  3. Join the plan lines.
  4. Assert they contain `srv_poi_legacy_id_map_pkey` and `srv_poi_info_pkey`.
  5. Assert no line matches `Seq Scan on srv_poi_(info|legacy_id_map)`.

  This proves the predicates can use the index (I9). With the old `@>` predicate the plan keeps `Seq Scan`, so the test discriminates.

`LegacyAndPracticalInfoIntegrationTest`. The existing behaviour tests stay unchanged and must pass.

- Rename `postUsesAtMostFiveStatements` to `postUsesAtMostThreeStatements`. Assert `isBetween(1, 3)`.
- `postOneHundredTwentyIdsStaysWithinStatementAndInLimits`: assert `isBetween(1, 3)`, that no SQL contains `@>`, and that at least one SQL contains `= ANY (CAST(` (case-insensitive). Keep the check that each statement has at most 100 placeholders.
- New `getPracticalInfoUsesAtMostThreeStatements`: GET with `OLD_ID` takes 1 to 3 statements; GET `absent-id` takes exactly 1 and returns 404.
- New `postFieldsWithoutLangOrCoverUseOneStatement`: `required_fields=id,name` takes exactly 1 statement.
- New `postPastLastPageKeepsTotalItems`: `page=5&size=1` with 2 ids gives empty `data` and `total_items` 2.

`PoiServiceTest`:

- Add `@Mock SrvPoiLegacyIdMapRepository legacyIdMapRepository`.
- `searchPracticalInfoSkipsMultiLangAndCoverWhenNotSelected`: stub `findPracticalInfoPage(any(), any(), any(), any(), anyBoolean(), anyInt(), anyLong())` to return `new PracticalInfoSlice(List.of(poi), 1)`.
- `shouldReturnPracticalInfoDestinationsAndNoTopLevelBusinessSector` and `shouldThrowWhenPracticalInfoPoiMissing`:
  - stub `findPracticalInfoPage(eq(List.of(id)), …)` instead of `findByPoiIdAndDeletedAtIsNull`; for the missing id, return an empty slice;
  - stub `findActiveCoversByPoiIdIn(any())` instead of `findActiveCoverByPoiId`.

Unchanged and expected green: `PoiControllerIntegrationTest`, `PracticalInfoProjectionTest`, `PracticalInfoBodyLimitFilterTest`, `ApiBearerAuthTest`.

Review round 3 is for `jpa-performance-reviewer`, carrying JPA-002, and for `app-security-reviewer`, because native SQL and the ORDER BY constants are new. Main sets JPA-002 to `fixed` in `decision.md` only after the review passes.

### Runtime (user, `runtime-runbook.md`)

Add a step after step 5. In psql, against the compose database:

```sql
PREPARE r(text[]) AS <RESOLVE_SQL with $1 for :ids>;
EXPLAIN (ANALYZE, BUFFERS) EXECUTE r(ARRAY['legacy-sample','11111111-1111-1111-1111-111111111111']);
SET enable_seqscan = off;
EXPLAIN (ANALYZE, BUFFERS) EXECUTE r(ARRAY['legacy-sample','11111111-1111-1111-1111-111111111111']);
```

Do the same for the practical-info count SQL (`$1` = ids, `$2` = `''`, `$3` = `''`).

Pass criterion: with `enable_seqscan = off`, both plans use `srv_poi_legacy_id_map_pkey` and `srv_poi_info_pkey`. With the default settings, a `Seq Scan` on tiny compose tables is expected and is not a failure. For the D-IDX decision, also run `EXPLAIN` on the cover query (`findActiveCoversByPoiIdIn` SQL) and record whether `srv_poi_media_gallery` is scanned in full. Never write hosts or tokens into the runbook.

FILE: services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryCustom.java
package vn.visitvietnam.dataserving.domain.repository;

import vn.visitvietnam.dataserving.domain.entity.SrvPoiInfo;

import java.util.Collection;
import java.util.List;

public interface SrvPoiLegacyIdMapRepositoryCustom {

    /** Một poi_id cũ resolve được và poi_id mới của nó. */
    record Resolution(String legacyPoiId, String poiId) {}

    /** Một trang dòng srv_poi_info theo thứ tự SQL và tổng số dòng khớp. */
    record PracticalInfoSlice(List<SrvPoiInfo> rows, long total) {}

    /** Cột sort cho trang practical info. Text SQL chỉ lấy từ hằng này. */
    enum SortColumn {
        POI_ID("i.poi_id"),
        POI_NAME("i.poi_name"),
        RATING_OVERALL("i.rating_overall"),
        RATING_COUNT("i.rating_count");

        private final String sql;

        SortColumn(String sql) {
            this.sql = sql;
        }

        public String sql() {
            return sql;
        }
    }

    List<Resolution> findResolvable(Collection<String> ids);

    PracticalInfoSlice findPracticalInfoPage(Collection<String> ids, String source, String poiName,
            SortColumn sort, boolean descending, int limit, long offset);
}
END_FILE

FILE: services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryImpl.java
package vn.visitvietnam.dataserving.domain.repository;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import org.hibernate.query.NativeQuery;
import org.hibernate.type.StandardBasicTypes;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiInfo;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.EnumMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

public class SrvPoiLegacyIdMapRepositoryImpl implements SrvPoiLegacyIdMapRepositoryCustom {

    /** Quy tắc resolve I1. Đây là định nghĩa SQL duy nhất. */
    public static final String HIT_CTE = """
            hit AS (
              SELECT m.legacy_poi_id, m.poi_id
              FROM apps.srv_poi_legacy_id_map m
              WHERE m.legacy_poi_id = ANY (CAST(:ids AS text[]))
                AND m.poi_id_status = 'OK'
                AND m.poi_id IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM apps.srv_poi_info x WHERE x.poi_id = m.legacy_poi_id)
            )
            """;

    public static final String RESOLVE_SQL = "WITH " + HIT_CTE + "SELECT h.legacy_poi_id, h.poi_id FROM hit h";

    public static final String PRACTICAL_INFO_FROM = """
            FROM apps.srv_poi_info i
            WHERE i.poi_id = ANY (ARRAY(
                    SELECT COALESCE(h.poi_id, u.id)
                    FROM unnest(CAST(:ids AS text[])) AS u(id)
                    LEFT JOIN hit h ON h.legacy_poi_id = u.id))
              AND i.deleted_at IS NULL
              AND (:source = '' OR lower(trim(i.source_name)) = :source)
              AND (:namePattern = '' OR lower(i.poi_name) LIKE lower(:namePattern) ESCAPE '!')
            """;

    public static final String PRACTICAL_INFO_COUNT_SQL = "WITH " + HIT_CTE + "SELECT count(*) " + PRACTICAL_INFO_FROM;

    static final String DEFAULT_ORDER_BY = "i.poi_id ASC";

    static final String DEFAULT_PAGE_SQL = pageSql(DEFAULT_ORDER_BY);

    static final Map<SortColumn, String> ASC_PAGE_SQL;

    static final Map<SortColumn, String> DESC_PAGE_SQL;

    static {
        Map<SortColumn, String> asc = new EnumMap<>(SortColumn.class);
        Map<SortColumn, String> desc = new EnumMap<>(SortColumn.class);
        for (SortColumn column : SortColumn.values()) {
            asc.put(column, pageSql(column.sql() + " ASC NULLS LAST, i.poi_id ASC"));
            desc.put(column, pageSql(column.sql() + " DESC NULLS LAST, i.poi_id ASC"));
        }
        ASC_PAGE_SQL = Collections.unmodifiableMap(asc);
        DESC_PAGE_SQL = Collections.unmodifiableMap(desc);
    }

    @PersistenceContext
    private EntityManager entityManager;

    static String pageSql(String orderBy) {
        return "WITH " + HIT_CTE + "SELECT {i.*}, count(*) OVER () AS total_items " + PRACTICAL_INFO_FROM
                + "ORDER BY " + orderBy + " LIMIT :limit OFFSET :offset";
    }

    @Override
    public List<Resolution> findResolvable(Collection<String> ids) {
        String[] array = distinctNonBlank(ids);
        if (array.length == 0) {
            return List.of();
        }
        NativeQuery<?> query = entityManager.createNativeQuery(RESOLVE_SQL).unwrap(NativeQuery.class);
        query.setParameter("ids", array, String[].class);
        List<?> rows = query.getResultList();
        List<Resolution> out = new ArrayList<>(rows.size());
        for (Object row : rows) {
            Object[] cols = (Object[]) row;
            out.add(new Resolution((String) cols[0], (String) cols[1]));
        }
        return out;
    }

    @Override
    public PracticalInfoSlice findPracticalInfoPage(Collection<String> ids, String source, String poiName,
            SortColumn sort, boolean descending, int limit, long offset) {
        String[] array = distinctNonBlank(ids);
        if (array.length == 0) {
            return new PracticalInfoSlice(List.of(), 0);
        }
        String sourceValue = source == null ? "" : source.trim().toLowerCase(Locale.ROOT);
        String pattern = containsPattern(poiName);
        String sql = sort == null ? DEFAULT_PAGE_SQL : (descending ? DESC_PAGE_SQL : ASC_PAGE_SQL).get(sort);
        NativeQuery<?> page = entityManager.createNativeQuery(sql).unwrap(NativeQuery.class);
        page.addEntity("i", SrvPoiInfo.class);
        page.addScalar("total_items", StandardBasicTypes.LONG);
        bind(page, array, sourceValue, pattern);
        page.setParameter("limit", limit);
        page.setParameter("offset", offset);
        List<?> rows = page.getResultList();
        if (rows.isEmpty()) {
            long total = offset == 0 ? 0 : count(array, sourceValue, pattern);
            return new PracticalInfoSlice(List.of(), total);
        }
        List<SrvPoiInfo> infos = new ArrayList<>(rows.size());
        long total = 0;
        for (Object row : rows) {
            Object[] cols = (Object[]) row;
            infos.add((SrvPoiInfo) cols[0]);
            total = ((Number) cols[1]).longValue();
        }
        return new PracticalInfoSlice(infos, total);
    }

    private long count(String[] ids, String source, String pattern) {
        NativeQuery<?> query = entityManager.createNativeQuery(PRACTICAL_INFO_COUNT_SQL).unwrap(NativeQuery.class);
        bind(query, ids, source, pattern);
        return ((Number) query.getSingleResult()).longValue();
    }

    private static void bind(NativeQuery<?> query, String[] ids, String source, String pattern) {
        query.setParameter("ids", ids, String[].class);
        query.setParameter("source", source);
        query.setParameter("namePattern", pattern);
    }

    private static String[] distinctNonBlank(Collection<String> ids) {
        if (ids == null) {
            return new String[0];
        }
        Set<String> out = new LinkedHashSet<>();
        for (String id : ids) {
            if (id != null && !id.isBlank()) {
                out.add(id);
            }
        }
        return out.toArray(String[]::new);
    }

    static String containsPattern(String raw) {
        if (raw == null || raw.isBlank()) {
            return "";
        }
        StringBuilder escaped = new StringBuilder(raw.length() + 2).append('%');
        for (int k = 0; k < raw.length(); k++) {
            char c = raw.charAt(k);
            if (c == '!' || c == '%' || c == '_') {
                escaped.append('!');
            }
            escaped.append(c);
        }
        return escaped.append('%').toString();
    }
}
END_FILE
