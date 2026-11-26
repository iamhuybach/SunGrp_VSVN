RESULT: PASS

## Main brief

### Decision
The repository chooses one of three constant SQL variants in Java: `IDS`, `NAME`, or `IDS_OR_NAME`. `IDS_OR_NAME` is `i.poi_id IN (id_set UNION name_set)`, followed by the `deleted_at`, `source`, sort, and paging rules that already exist. Each variant binds only its own parameters.
`ids`-only keeps today's SQL text, so the primary-key plan does not change. The GET path passes `List.of(poiId)` and hits `IDS`.
The DTO drops `@NotEmpty` and adds `@AssertTrue isSelectorPresent()`. The controller turns null `ids` into `List.of()`.
Rejected options: a single OR query (forces a seq scan on id-only calls), a single UNION with a gating parameter (generic plans keep the seq scan node), and an in-memory merge.
No schema or index change. A name selection is a full scan of `srv_poi_info`, which this change accepts. Runtime proof records a latency baseline.

### Invariants Main must preserve
- `HIT_CTE`, `RESOLVE_SQL`, `containsPattern`, `distinctNonBlank`, and the `findPracticalInfoPage` signature stay as they are.
- `ids` only: no `:namePattern` in the SQL. `EXPLAIN` with `enable_seqscan=off` still uses `srv_poi_legacy_id_map_pkey` and `srv_poi_info_pkey`.
- `poi_name` only: `ids` is not bound or required, and the selection is the escaped contains match on `lower(i.poi_name)`.
- Both selectors give the union. A POI in both sets appears once, and `total_items` counts distinct `poi_id`.
- `deleted_at IS NULL`, `source`, sort, and paging apply once, after the union.
- No selector gives 422 `ERR_VALIDATION_FAILED` and the service is not called. That covers `ids` absent, null, or `[]` together with `poi_name` absent, null, or blank.
- When `ids` is non-empty: at most 500, each `@NotBlank` and at most 128 characters, whether or not `poi_name` is present.
- `poi_name` over 128 gives 422. A non-string value gives 400 `ERR_BAD_REQUEST`. The query `poi_name` is ignored.
- `%`, `_`, and `!` are escaped with `!`. `\` matches literally. ORDER BY comes only from `SortColumn` constants, with `i.poi_id ASC` as tie-break.
- No edits under `common/web/`, and no schema changes.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PracticalInfoSearchRequest.java | record `PracticalInfoSearchRequest` | Apply the full doc `## DTO code`: remove `@NotEmpty`, keep `@Size(max=500)` and the element constraints, add `@JsonIgnore @AssertTrue isSelectorPresent()`, update the javadoc | `{}` returns 422 and `{"poi_name":"x"}` returns 200 |
| 2 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java | `searchPracticalInfo` | Pass `body.ids() == null ? List.of() : body.ids()`. Add "hoặc thiếu cả ids và poi_name" to the 422 `@ApiResponse` description | The captor shows empty `ids` on name-only bodies |
| 3 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryImpl.java | `PRACTICAL_INFO_FROM`…`bind` (SQL constants, static init, `pageSql`, `findPracticalInfoPage`, `count`, `bind`) | Replace with the full doc `## Repository SQL code`: `ID_SET`, `NAME_SET`, `enum Selection`, `COUNT_SQL`/`DEFAULT_PAGE_SQL`/`ASC_PAGE_SQL`/`DESC_PAGE_SQL` keyed by `Selection`, `selection()`, and a selection-aware `bind` | Repository tests pass for all three selections |
| 4 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiLegacyIdMapRepositoryCustom.java | `findPracticalInfoPage` | Javadoc only: "ids rỗng và poiName trắng thì trả trang rỗng; có cả hai thì hợp hai tập." | Signature unchanged |
| 5 | services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/domain/repository/PoiRepositoryIntegrationTest.java | `practicalInfoPageSqlOrderByComesOnlyFromConstants`, `idPredicatesUsePrimaryKeyIndexesWhenSeqScanDisabled`, `explain`, new tests | Loop over `Selection.values()`. Use `COUNT_SQL.get(Selection.IDS)`. `explain` binds only `source`. Add 4 tests (Tests section) | Green |
| 6 | services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/LegacyAndPracticalInfoIntegrationTest.java | `postAppliesIdsAndBodyPoiNameTogether`, `postFiltersBySourceAndPoiNameCaseInsensitiveEscaped`, new tests | Replace the AND test with the union test. Rewrite the source test as name-only. Add the dedup/paging and backslash/bang tests | Green |
| 7 | services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/PoiControllerIntegrationTest.java | practical_info POST tests | Add 3 tests and extend 2 (Tests section) | Green |
| 8 | services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java | optional new test | Optional: `searchPracticalInfoForwardsNameOnlySelection` | Green, or not added |
| 9 | docs/context/api-mapping/practical_info_list.md | `## Tổng quan`, `## Request body`, `## Status code`, `## Sample request`, new `## Sample poi_name` | Apply the full doc `## Documentation change` items 1–4 | The doc states the union, `ids` optional, and 422 when there is no selector, with no AND wording left |
| 10 | services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java, PracticalInfoQuery.java | — | No edit | Unchanged |

### Order and stop points
1. Rows 1–2 (DTO and controller).
2. Rows 3–4 (repository).
3. Rows 5–8 (tests).
4. Row 9 (docs).
5. Run the full module tests. STOP (evidence): local verification must PASS before review. If `idPredicatesUsePrimaryKeyIndexesWhenSeqScanDisabled` fails for `IDS`, stop and report. Do not loosen the assertion.
6. STOP (user): the user runs the runtime proof with `docker compose` per `runtime-runbook.md`, covering name-only, ids-only, union, and the 422 for no selector, plus EXPLAIN ANALYZE and latency for name-only and union. Record no hosts or tokens.
7. Review by `api-contract-reviewer` and `jpa-performance-reviewer`. Add `app-security-reviewer` only if the diff touches `common/web/` (it should not).

### Tests and verification
- Full suite: `cd services/data-serving-service && mvnw.cmd -q -B test`
- Focused: `mvnw.cmd -q -B test -Dtest=PoiControllerIntegrationTest,LegacyAndPracticalInfoIntegrationTest,PoiRepositoryIntegrationTest,PoiServiceTest`
- PoiControllerIntegrationTest:
  - Add `postPracticalInfoAcceptsPoiNameWithoutIds`: `{"poi_name":"Ba Na"}`, `{"ids":[],…}`, and `{"ids":null,…}` each give 200 with empty ids.
  - Add `postPracticalInfoRejectsMissingSelectors`: `{}`, `{"ids":null}`, `{"poi_name":null}`, `{"poi_name":"   "}`, and `{"ids":[],"poi_name":""}` each give 422 with no service call.
  - Add `postPracticalInfoKeepsIdRulesWhenPoiNamePresent`: `[""]` with a name gives 422, and 501 ids with a name give 422.
  - Extend `postPracticalInfoRejectsPoiNameOver128` with a no-ids body of 129 characters (422).
  - Extend `postPracticalInfoRejectsNonStringPoiName` with `{"poi_name":123}` (400).
  - Keep `postPracticalInfoRejectsEmptyAndOver500Ids`.
- LegacyAndPracticalInfoIntegrationTest:
  - `postReturnsUnionOfIdsAndBodyPoiName` (replaces the AND test): `{pct, wide}`, total 2.
  - `postFiltersBySourceAndPoiNameCaseInsensitiveEscaped`, rewritten as name-only with source=partner: returns `pct` only.
  - `postUnionDedupesOverlapAndPagesOverUnion`: legacy `OLD_ID` plus the name "cafe" give `{NEW_ID, pct, wide}`, total 3, with page 1 at size 1 sorted by name.
  - `postBodyPoiNameMatchesBackslashAndBangLiterally`.
  - Keep `postQueryPoiNameNoLongerFilters`.
- PoiRepositoryIntegrationTest:
  - Updated: `practicalInfoPageSqlOrderByComesOnlyFromConstants`, `idPredicatesUsePrimaryKeyIndexesWhenSeqScanDisabled`.
  - New: `practicalInfoPageSelectsByNameOnly`, `practicalInfoPageUnionsIdsAndName`, `practicalInfoPageFallbackCountBindsEverySelection`, `practicalInfoPageWithoutSelectorIsEmpty`.
- Fixture details for each test are in the full doc `## Verification`.

### Read only if needed
- `## Repository SQL code`: row 3 (exact code and the enum-init note).
- `## DTO code`: row 1.
- `## Controller change`: row 2.
- `## Documentation change (practical_info_list.md)`: row 9 (exact Vietnamese replacement text).
- `## Alternatives`: rows 3 and 5 (why there are three variants and why the plan test changes).
- `## Invariants`: I9 for the backslash/bang test in row 6, and I2 for row 5.
- `## Verification`: rows 5–8 (fixtures and expected ids).
- `## Security`, `## Observability`: step 6 runtime proof and the reviewer questions on scan cost.
- `## Rollout`, `## Rollback and forward recovery`: the uncommitted AND baseline and the trigram-index follow-up.

# Architecture: 20261126-practical-info-poi-name-or-ids

## Scope

- `POST /api/v1/pois/practical_info`: the body selects POIs by `ids`, by `poi_name`, or by both. When both are present the result is the union of the two selections (ledger D-1).
- Files: `PracticalInfoSearchRequest` (validation), `PoiController.searchPracticalInfo` (normalization), `SrvPoiLegacyIdMapRepositoryImpl` (per-selection SQL), `SrvPoiLegacyIdMapRepositoryCustom` (javadoc only), the tests in scope, and `docs/context/api-mapping/practical_info_list.md`.
- `PoiService`, `PracticalInfoQuery`, and the repository method signature stay as they are. `PoiService.java` is in scope only so Main can confirm that no edit is needed there.

## Non-goals

- `GET /api/v1/pois/{poi_id}/practical_info`. It keeps calling `findPracticalInfoPage(List.of(poiId), null, null, …)`, which selects `IDS` and gets the same SQL text as today.
- Query parameters (`required_fields`, `source`, `lang`, `page`, `size`, `sort_field`, `sort_order`). The query `poi_name` is still not read.
- Schema, indexes, columns, keys, and `docs/poi-serving-api/`. No trigram index is added. See Alternatives and Observability.
- `PracticalInfoBodyLimitFilter` and `common/web/`. The diff must not touch them, so `app-security-reviewer` is not added.
- Model design. There is no table, column, grain, or key change, so `model-design.md` is not needed.

## Invariants

- I1. Legacy id resolution keeps `HIT_CTE` and `RESOLVE_SQL` byte for byte. An id that is already `srv_poi_info.poi_id` wins over a map row.
- I2. `ids` only: the SQL text is exactly today's text without the `:namePattern` line. There is no name predicate, and the plan keeps using `srv_poi_legacy_id_map_pkey` and `srv_poi_info_pkey`.
- I3. `poi_name` only: the selection is `lower(i.poi_name) LIKE lower(:namePattern) ESCAPE '!'`, with `:namePattern = containsPattern(poi_name)`. `ids` is not required and is not bound.
- I4. Both selectors: the result is `{resolved ids} ∪ {name matches}`. A POI matched by both appears once. `total_items` counts distinct `poi_id` values.
- I5. `deleted_at IS NULL` and the `source` filter apply once, after the union, to the selected rows. Sort, paging, and `count(*) OVER ()` also run over the union.
- I6. No selector means 422 `ERR_VALIDATION_FAILED`, and the service is not called. "No selector" means `ids` is absent, null, or `[]`, and `poi_name` is absent, null, `""`, or whitespace only.
- I7. When `ids` is non-empty, the current rules still apply: at most 500 entries counting duplicates, each `@NotBlank`, each at most 128 characters. `[]` counts as "no id selector".
- I8. `poi_name` longer than 128 returns 422. A non-string JSON value returns 400 `ERR_BAD_REQUEST`, because the parse happens before validation. Whether `ids` is present does not change either result.
- I9. Escaping: `%`, `_`, and `!` get a `!` prefix. `\` is not an escape character under `ESCAPE '!'`, so it matches literally. This meets "`\` escaped" in the request as observable behavior. `containsPattern` does not change.
- I10. ORDER BY text comes only from the `SortColumn` constants. The tie-break stays `i.poi_id ASC`, with `NULLS LAST`.

## State ownership

Not applicable: the endpoint is read-only over `apps.srv_poi_info` and `apps.srv_poi_legacy_id_map`, and the pipeline owns both.

## Grain and keys

- Grain does not change: the response has one row per `apps.srv_poi_info.poi_id` (PK). The union is a semi-join on that PK (`i.poi_id IN (… UNION …)` or `= ANY(ARRAY(…))`), so duplicates cannot appear.
- Model design is not cited because no table, column, grain, or key changes.

## Ordering

- Default order is `i.poi_id ASC`. With a sort field it is `<col> ASC|DESC NULLS LAST, i.poi_id ASC`, the same as today. With two selectors, the order applies to the union and not separately to each branch.
- Paging is deterministic because `poi_id` breaks every tie.

## Transaction and commit boundaries

Not applicable: there is one `@Transactional(readOnly = true)` service call, as today, and no writes. The page query and the fallback count query (used only when an offset runs past the end) both run in that call.

## Idempotency

Not applicable: the endpoint is a read-only POST, and the same input over the same data gives the same page.

## Concurrency

Not applicable: no shared state changes. A pipeline write between the page query and the fallback count can change `total`. That window already exists today and this task does not widen it.

## Retry and recovery

Not applicable: requests are stateless and there is no retry logic in this path.

## Partial failure

Not applicable: there is one SQL statement per page. If it fails, the existing handler returns 500.

## Alternatives

| # | Option | Verdict |
|---|---|---|
| A | One SQL text: `i.poi_id = ANY(ids) OR (:namePattern <> '' AND name LIKE …)` | Rejected. The OR with a branch that cannot use an index forces a seq scan of `srv_poi_info` even for id-only calls. That breaks I2 and `idPredicatesUsePrimaryKeyIndexesWhenSeqScanDisabled`. With 500 ids, `= ANY(array)` is then checked once per row. |
| B | One SQL text with a `UNION` whose name branch is gated by `:namePattern <> ''` | Rejected. A custom plan removes the gated branch, but a generic plan (pgjdbc server-prepared after 5 runs) keeps a `Seq Scan on srv_poi_info n` node behind a one-time filter. The plan becomes hard to assert, and the existing seq-scan test fails. |
| C | Three SQL variants chosen in Java (`IDS`, `NAME`, `IDS_OR_NAME`), each with only its own bind parameters | **Selected.** The `IDS` text equals today's id path, so the plan does not move. `NAME` is a single direct predicate. `IDS_OR_NAME` combines PK lookups and one name scan through `UNION`, then semi-joins on the PK. The cost is 27 precomputed page strings and 3 count strings instead of 9 and 1. They are still constants, so I10 holds. |
| D | Run two queries in Java and merge or page in memory | Rejected. Sort and paging would have to run in memory over an unbounded name result. |
| E | Add a `pg_trgm` GIN index on `lower(poi_name)` | Out of scope, because the request does not allow schema changes. It is recorded as forward recovery if the name scan latency becomes a problem. |

Trade-off: a name selection always scans `srv_poi_info` sequentially. A contains match with a leading `%` cannot use a btree index. This is the documented match rule, and the request accepts it with no schema change. Paging keeps the response at most 100 rows. `count(*) OVER ()` is computed over the filtered set and not over the whole table.

## Repository SQL code

Replace `PRACTICAL_INFO_FROM`, `PRACTICAL_INFO_COUNT_SQL`, `DEFAULT_PAGE_SQL`, `ASC_PAGE_SQL`, `DESC_PAGE_SQL`, `pageSql`, `findPracticalInfoPage`, `count`, and `bind` in `SrvPoiLegacyIdMapRepositoryImpl` with the code below. Keep `HIT_CTE`, `RESOLVE_SQL`, `findResolvable`, `distinctNonBlank`, and `containsPattern` unchanged. Add `import java.util.Objects` only if it is used.

```java
    /** Tập poi_id từ ids: id cũ resolve qua hit, còn lại giữ nguyên. Cần HIT_CTE và :ids. */
    static final String ID_SET = """
            SELECT COALESCE(h.poi_id, u.id)
                    FROM unnest(CAST(:ids AS text[])) AS u(id)
                    LEFT JOIN hit h ON h.legacy_poi_id = u.id""";

    /** Tập poi_id khớp tên. :namePattern lấy từ containsPattern. */
    static final String NAME_SET = """
            SELECT n.poi_id
                    FROM apps.srv_poi_info n
                    WHERE lower(n.poi_name) LIKE lower(:namePattern) ESCAPE '!'""";

    /** Cách chọn POI. Chỉ ids, chỉ tên, hoặc hợp cả hai. */
    enum Selection { IDS, NAME, IDS_OR_NAME }

    static final String DEFAULT_ORDER_BY = "i.poi_id ASC";

    static final Map<Selection, String> COUNT_SQL;
    static final Map<Selection, String> DEFAULT_PAGE_SQL;
    static final Map<Selection, Map<SortColumn, String>> ASC_PAGE_SQL;
    static final Map<Selection, Map<SortColumn, String>> DESC_PAGE_SQL;

    static {
        Map<Selection, String> count = new EnumMap<>(Selection.class);
        Map<Selection, String> def = new EnumMap<>(Selection.class);
        Map<Selection, Map<SortColumn, String>> ascAll = new EnumMap<>(Selection.class);
        Map<Selection, Map<SortColumn, String>> descAll = new EnumMap<>(Selection.class);
        for (Selection selection : Selection.values()) {
            count.put(selection, withClause(selection) + "SELECT count(*) " + fromClause(selection));
            def.put(selection, pageSql(selection, DEFAULT_ORDER_BY));
            Map<SortColumn, String> asc = new EnumMap<>(SortColumn.class);
            Map<SortColumn, String> desc = new EnumMap<>(SortColumn.class);
            for (SortColumn column : SortColumn.values()) {
                asc.put(column, pageSql(selection, column.sql() + " ASC NULLS LAST, i.poi_id ASC"));
                desc.put(column, pageSql(selection, column.sql() + " DESC NULLS LAST, i.poi_id ASC"));
            }
            ascAll.put(selection, Collections.unmodifiableMap(asc));
            descAll.put(selection, Collections.unmodifiableMap(desc));
        }
        COUNT_SQL = Collections.unmodifiableMap(count);
        DEFAULT_PAGE_SQL = Collections.unmodifiableMap(def);
        ASC_PAGE_SQL = Collections.unmodifiableMap(ascAll);
        DESC_PAGE_SQL = Collections.unmodifiableMap(descAll);
    }

    static String withClause(Selection selection) {
        return selection == Selection.NAME ? "" : "WITH " + HIT_CTE;
    }

    static String fromClause(Selection selection) {
        String selector = switch (selection) {
            case IDS -> "i.poi_id = ANY (ARRAY(\n        " + ID_SET + "))";
            case NAME -> "lower(i.poi_name) LIKE lower(:namePattern) ESCAPE '!'";
            case IDS_OR_NAME -> "i.poi_id IN (\n        " + ID_SET + "\n        UNION\n        " + NAME_SET + ")";
        };
        return "FROM apps.srv_poi_info i\nWHERE " + selector + "\n"
                + "  AND i.deleted_at IS NULL\n"
                + "  AND (:source = '' OR lower(trim(i.source_name)) = :source)\n";
    }

    static String pageSql(Selection selection, String orderBy) {
        return withClause(selection) + "SELECT {i.*}, count(*) OVER () AS total_items " + fromClause(selection)
                + "ORDER BY " + orderBy + " LIMIT :limit OFFSET :offset";
    }

    /** null khi không có selector nào. */
    static Selection selection(String[] ids, String pattern) {
        boolean byId = ids.length > 0;
        boolean byName = !pattern.isEmpty();
        if (byId && byName) {
            return Selection.IDS_OR_NAME;
        }
        if (byId) {
            return Selection.IDS;
        }
        return byName ? Selection.NAME : null;
    }

    @Override
    public PracticalInfoSlice findPracticalInfoPage(Collection<String> ids, String source, String poiName,
            SortColumn sort, boolean descending, int limit, long offset) {
        String[] array = distinctNonBlank(ids);
        String pattern = containsPattern(poiName);
        Selection selection = selection(array, pattern);
        if (selection == null) {
            return new PracticalInfoSlice(List.of(), 0);
        }
        String sourceValue = source == null ? "" : source.trim().toLowerCase(Locale.ROOT);
        String sql = sort == null
                ? DEFAULT_PAGE_SQL.get(selection)
                : (descending ? DESC_PAGE_SQL : ASC_PAGE_SQL).get(selection).get(sort);
        NativeQuery<?> page = entityManager.createNativeQuery(sql).unwrap(NativeQuery.class);
        page.addEntity("i", SrvPoiInfo.class);
        page.addScalar("total_items", StandardBasicTypes.LONG);
        bind(page, selection, array, sourceValue, pattern);
        page.setParameter("limit", limit);
        page.setParameter("offset", offset);
        List<?> rows = page.getResultList();
        if (rows.isEmpty()) {
            long total = offset == 0 ? 0 : count(selection, array, sourceValue, pattern);
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

    private long count(Selection selection, String[] ids, String source, String pattern) {
        NativeQuery<?> query = entityManager.createNativeQuery(COUNT_SQL.get(selection)).unwrap(NativeQuery.class);
        bind(query, selection, ids, source, pattern);
        return ((Number) query.getSingleResult()).longValue();
    }

    /** Chỉ bind tham số có trong SQL của selection; Hibernate từ chối tên tham số lạ. */
    private static void bind(NativeQuery<?> query, Selection selection, String[] ids, String source, String pattern) {
        if (selection != Selection.NAME) {
            query.setParameter("ids", ids, String[].class);
        }
        if (selection != Selection.IDS) {
            query.setParameter("namePattern", pattern);
        }
        query.setParameter("source", source);
    }
```

Notes for Main:
- The enum has no fields, and the SQL text is built in static methods. This avoids reading outer statics while the enum is still initializing.
- Keep `IDS` equivalent to today's statement. Whitespace may differ, but the predicates, joins, and casts must match.
- `SrvPoiLegacyIdMapRepositoryCustom.findPracticalInfoPage` keeps its signature. Add a javadoc line: "ids rỗng và poiName trắng thì trả trang rỗng; có cả hai thì hợp hai tập."

## DTO code

```java
public record PracticalInfoSearchRequest(
        @Size(max = 500) List<@NotBlank @Size(max = 128) String> ids,
        @JsonProperty("poi_name")
        @JsonDeserialize(using = PracticalInfoNameDeserializer.class)
        @Size(max = 128) String poiName
) {
    /** ids không rỗng hoặc poi_name có chữ. Thiếu cả hai trả 422. */
    @JsonIgnore
    @AssertTrue(message = "ids hoặc poi_name phải có giá trị")
    public boolean isSelectorPresent() {
        return (ids != null && !ids.isEmpty()) || (poiName != null && !poiName.isBlank());
    }
}
```

- Remove `@NotEmpty` and its import. Add `com.fasterxml.jackson.annotation.JsonIgnore` and `jakarta.validation.constraints.AssertTrue`. Replace the record javadoc with: "Body POST practical_info. ids hoặc poi_name là selector; có cả hai thì hợp."
- Hibernate Validator treats `isSelectorPresent()` as a getter (property `selectorPresent`). `@JsonIgnore` keeps it out of the Jackson and springdoc schema. `PracticalInfoNameDeserializer` does not change.
- The error surfaces through the existing `HandlerMethodValidationException` or `MethodArgumentNotValidException` handlers as 422 `ERR_VALIDATION_FAILED`. The test asserts only status and `error_code`, not `errors[].field`.

## Controller change

In `PoiController.searchPracticalInfo`, replace the `body.ids()` argument with `body.ids() == null ? List.of() : body.ids()`. Keep the `poiName` normalization (blank becomes null). In the `@ApiResponses` 422 description, add "hoặc thiếu cả ids và poi_name". The 400 description does not change.

## Documentation change (`practical_info_list.md`)

Edit these four places. Everything else stays.

1. `## Tổng quan`, Description: replace the sentence that begins "Một phần tử cho mỗi `poi_id` đã resolve…" with: "Body chọn POI theo `ids`, theo `poi_name`, hoặc cả hai. Có cả hai thì lấy hợp, không lấy giao. Một phần tử cho mỗi `poi_id` đã chọn, `deleted_at` null, sau lọc `source` (query)."
2. `## Request body`, row 1 `ids`: change Required to `không`. Description: "Selector theo id. Có phần tử thì từ 1 đến 500 chuỗi, mỗi phần tử không rỗng, dài tối đa 128, đếm cả phần tử trùng. Vắng, `null` hoặc `[]` là không chọn theo id. `apps.srv_poi_info.poi_id` hoặc `apps.srv_poi_legacy_id_map.legacy_poi_id`. `data.id` là `poi_id` mới."
   Row 2 `poi_name`, Description: "Selector theo tên, ngang hàng với `ids`, không lọc tập `ids`. Tối đa 128. Vắng, `null`, rỗng hoặc chỉ khoảng trắng là không chọn theo tên. Khớp chứa, không phân biệt hoa thường trên `apps.srv_poi_info.poi_name`. `%`, `_` và `\` khớp đúng ký tự. Có cả `ids` thì kết quả là hợp hai tập, mỗi `poi_id` một lần. Số, boolean, mảng hoặc object trả HTTP 400. Query `poi_name` không được đọc."
   Add one line below the table: "Phải có ít nhất một selector: `ids` không rỗng hoặc `poi_name` có chữ. Thiếu cả hai trả HTTP 422. `source`, `sort_field`, `sort_order`, `page`, `size` áp lên tập đã chọn."
3. `## Status code`, row 422: "`ids`, `required_fields`, `source`, `poi_name`, `page`, `size`, `sort_field` hoặc `sort_order` ngoài hợp đồng, hoặc thiếu cả `ids` và `poi_name`."
4. `## Sample request`: change the body to `{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}` and drop the sentence about `poi_name` being `French Village`. Under the union rule, `total_items` = 1 is no longer proven for a name. Add a new section `## Sample poi_name` after `## Sample source`. It holds two request-only blocks with no response body, using the same wording as the `source=google` sample ("File này không có kết quả Dev cho selector tên, nên không ghi body response."): body `{"poi_name":"French Village"}`, and body `{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"],"poi_name":"French Village"}`. Each block has the `Authorization: Bearer <token>` and `Content-Type` headers, like the other samples.

## Observability

- No new logs or metrics. Do not log `poi_name` or `ids` values. The existing request logging and `meta.trace_id` stay.
- Runtime proof records the latency and `EXPLAIN (ANALYZE, BUFFERS)` output of a name-only and a union call on the user's Docker runtime. These form the baseline for deciding later whether option E is needed. They do not block this task.

## Security

- Every value is a bind parameter. SQL text comes only from `Selection` and `SortColumn` constants. `containsPattern` neutralizes LIKE wildcards, so a user cannot send `%` to match every row.
- A name-only call can now select up to the whole table, but it returns at most `size` (100) rows per page. A single character or `" a"` makes that easy. This is accepted because paging bounds the response and the scan is linear with no amplification. Bearer auth, the body limit filter, and the order 401 → 400 → 415 → 422 do not change.
- `common/web/` is not touched, so no security reviewer is added.

## Rollout

- The previous task's AND implementation is uncommitted in the working tree (`git status` M files). This task edits on top of it. Nothing is committed.
- This is a breaking contract change for clients that relied on AND. The ledger D-1 decision says the AND behavior was wrong. Callers who send only `ids` see no change.
- The user runs the runtime proof with `docker compose`, following `runtime-runbook.md`. The deploy repo is out of scope until this contract passes here.

## Rollback and forward recovery

- Rollback: restore the in-scope files to their previous state (the AND version in the working tree, or `HEAD` for the version before `poi_name`). There is no data or schema to revert.
- Forward recovery for name scan latency: a `pg_trgm` GIN index on `lower(poi_name)`, owned by the schema owner, as a separate task. The SQL `lower(i.poi_name) LIKE …` already has the shape such an index can serve.

## Implementation plan

1. DTO: apply the DTO code.
2. Controller: normalize `ids` and update the 422 description.
3. Repository impl and interface javadoc: apply the repository SQL code.
4. Tests: the edits listed in Verification.
5. Docs: the four documentation edits.
6. Run the full module test suite, then hand over the runtime proof.

## Verification

Commands: `cd services/data-serving-service && mvnw.cmd -q -B test` (JDK 26, Docker for Testcontainers). Focused runs: `mvnw.cmd -q -B test -Dtest=PoiControllerIntegrationTest,LegacyAndPracticalInfoIntegrationTest,PoiRepositoryIntegrationTest,PoiServiceTest`.

`PoiControllerIntegrationTest` (service mocked):
- Keep `postPracticalInfoRejectsEmptyAndOver500Ids`. `{"ids":[]}` is still 422 because there is no name.
- Add `postPracticalInfoAcceptsPoiNameWithoutIds`: bodies `{"poi_name":"Ba Na"}`, `{"ids":[],"poi_name":"Ba Na"}`, and `{"ids":null,"poi_name":"Ba Na"}` each return 200. The captor shows `ids()` empty and `poiName()` = `"Ba Na"`.
- Add `postPracticalInfoRejectsMissingSelectors`: bodies `{}`, `{"ids":null}`, `{"poi_name":null}`, `{"poi_name":"   "}`, and `{"ids":[],"poi_name":""}` each return 422 `ERR_VALIDATION_FAILED`, with `verifyNoInteractions(poiService)`.
- Add `postPracticalInfoKeepsIdRulesWhenPoiNamePresent`: `{"ids":[""],"poi_name":"x"}` returns 422, and 501 ids plus `poi_name` return 422.
- Extend `postPracticalInfoRejectsPoiNameOver128` with a body that has no ids and 129 characters, which returns 422.
- Extend `postPracticalInfoRejectsNonStringPoiName` with `{"poi_name":123}` and no ids, which returns 400 `ERR_BAD_REQUEST`.
- Keep the other existing practical_info tests as they are.

`LegacyAndPracticalInfoIntegrationTest` (real database):
- Replace `postAppliesIdsAndBodyPoiNameTogether` with `postReturnsUnionOfIdsAndBodyPoiName`. Insert `pct` "100%_Cafe", `wide` "100X Cafe", and `outside` "100%_Outside", all partner. Body `{"ids":["wide"],"poi_name":"100%_cAFE"}` returns ids {`pct`,`wide`} with `total_items` 2. `outside` and `NEW_ID` are absent.
- Rewrite `postFiltersBySourceAndPoiNameCaseInsensitiveEscaped` as name-only. Insert `pct` "100%_Cafe" Partner, `wide` "100X Cafe" partner, and `pctg` "100%_cafe g" google. `source=partner` with body `{"poi_name":"100%_CAFE"}` returns only `pct`.
- Add `postUnionDedupesOverlapAndPagesOverUnion`. Body ids [`pct`, `OLD_ID`] with `poi_name` "cafe" matches `pct`, `wide`, and `NEW_ID` "Sample Cafe". `NEW_ID` comes through both the legacy id and the name. The result is {`NEW_ID`, `pct`, `wide`}, `total_items` 3. With `sort_field=name&sort_order=asc&size=1&page=1`, the response holds one row: the second by name, ties broken by `poi_id`.
- Add `postBodyPoiNameMatchesBackslashAndBangLiterally`. Insert `bs` "A\B", `plain` "AB", and `bang` "A!B". Body `{"poi_name":"\\"}` (JSON string `\`) returns only `bs`. `{"poi_name":"!"}` returns only `bang`.
- Keep `postQueryPoiNameNoLongerFilters` (ids-only, no name predicate) and the other tests as they are.

`PoiRepositoryIntegrationTest`:
- Update `practicalInfoPageSqlOrderByComesOnlyFromConstants` to loop over `Selection.values()`, asserting the regex on `DEFAULT_PAGE_SQL.get(s)` and on every value of `ASC_PAGE_SQL.get(s)` and `DESC_PAGE_SQL.get(s)`.
- Update `idPredicatesUsePrimaryKeyIndexesWhenSeqScanDisabled` to use `COUNT_SQL.get(Selection.IDS)`. Change `explain` so it binds `source` only. Binding `namePattern` now throws for `IDS`. The assertions stay unchanged.
- Add `practicalInfoPageSelectsByNameOnly`. Insert A "Cafe One", B "cafe two" (deleted), and C "Tea". `findPracticalInfoPage(List.of(), null, "CAFE", null, false, 10, 0)` returns [A] with total 1.
- Add `practicalInfoPageUnionsIdsAndName`. ids [`C`], name "cafe" returns [A, C] with total 2. ids [`A`], name "cafe" returns [A] with total 1 (dedup).
- Add `practicalInfoPageFallbackCountBindsEverySelection`: offset 5, limit 1, for `IDS`, `NAME`, and `IDS_OR_NAME` inputs. The rows are empty and the totals are correct, which exercises `COUNT_SQL` binding for each selection.
- Add `practicalInfoPageWithoutSelectorIsEmpty`: `(List.of(), null, "  ", …)` returns empty with total 0.

`PoiServiceTest`: no change is required, because the signature is the same. Optionally, add `searchPracticalInfoForwardsNameOnlySelection`, where the repository is called with an empty ids list and `"Ba Na"`.

Runtime proof (user-run, `runtime-runbook.md`): name-only, ids-only, union, and no-selector (422) calls, each with status and `total_items`, plus the latency or EXPLAIN baseline from Observability. Do not record hosts or tokens.
