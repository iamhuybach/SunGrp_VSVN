# API source inventory: `D:\git\SunGrp_VSVN_API` (read-only, 2026-11-06)

Read-only listing; nothing copied. `.git/`, `target/`, IDE folders excluded. 62 files. `.env.example` exists and was not opened.

## 1. Files

Package root `src/main/java/vn/visitvietnam/dataserving/` is written `main/`; `src/test/java/vn/visitvietnam/dataserving/` is written `test/`.

| Path | KB | Role |
|---|---:|---|
| `pom.xml` | 4.4 | Maven build: parent `spring-boot-starter-parent` 4.1.1, `java.version` 26, artifact `data-serving-service` |
| `mvnw`, `mvnw.cmd` | 11.8, 8.3 | Maven wrapper scripts |
| `.mvn/wrapper/maven-wrapper.properties` | 0.2 | Wrapper 3.3.4, Maven 3.9.16 |
| `Dockerfile` | 1.3 | Two-stage image build |
| `docker-compose.yml` | 1.1 | Local PostgreSQL + service |
| `.dockerignore`, `.gitignore` | 0.3, 0.7 | Ignore lists |
| `.env.example` | 1.0 | Env template (not read) |
| `main/DataServingApplication.java` | 0.3 | Spring Boot entry point |
| `main/api/PoiController.java` | 9.4 | REST controller `/api/v1/pois` |
| `main/api/dto/CompactPoiResponse.java` | 6.0 | Response DTO |
| `main/api/dto/PoiAmenityGroupResponse.java` | 1.4 | Response DTO |
| `main/api/dto/PoiGalleryItemResponse.java` | 1.6 | Response DTO |
| `main/api/dto/PoiReviewItemResponse.java` | 1.2 | Response DTO |
| `main/common/dto/ApiErrorDetail.java`, `ApiMeta.java`, `ApiResponse.java`, `PageResponse.java`, `PaginationMeta.java` | 0.6, 1.0, 2.9, 1.2, 1.7 | Response envelope and paging |
| `main/common/exception/ResourceNotFoundException.java` | 0.4 | Domain exception |
| `main/common/web/GlobalExceptionHandler.java` | 6.9 | Error mapping |
| `main/common/web/RequestContext.java`, `RequestIdFilter.java` | 1.2, 1.7 | Request-id propagation |
| `main/config/OpenApiConfig.java` | 4.1 | springdoc OpenAPI config |
| `main/domain/entity/SrvPoiInfo.java` | 2.8 | JPA entity `apps.srv_poi_info` |
| `main/domain/entity/SrvPoiMultiLang.java`, `PoiMultiLangId.java` | 1.5, 0.5 | Entity `apps.srv_poi_multi_lang` + `@IdClass` |
| `main/domain/entity/SrvPoiAmenity.java`, `PoiAmenityId.java` | 1.5, 0.6 | Entity `apps.srv_poi_amenity` + `@IdClass` |
| `main/domain/entity/SrvPoiMediaGallery.java` | 1.7 | Entity `apps.srv_poi_media_gallery` |
| `main/domain/entity/SrvPoiReview.java` | 1.6 | Entity `apps.srv_poi_review` |
| `main/domain/repository/SrvPoi{Info,MultiLang,Amenity,MediaGallery,Review}Repository.java` | 0.7, 0.9, 0.7, 1.1, 0.6 | Spring Data JPA repositories |
| `main/service/PoiService.java` | 16.8 | Query and assembly logic |
| `main/service/PoiSpecifications.java` | 1.0 | JPA Specifications (filters) |
| `main/service/util/BusinessSectorDictionary.java`, `LanguageResolver.java`, `SubcategoryTagsParser.java` | 1.8, 1.4, 2.2 | Helpers |
| `src/main/resources/application.yml` | 2.1 | Runtime config |
| `src/main/resources/db/migration/V1__init_srv_poi_tables.sql` | 4.3 | Flyway V1: schema `apps`, 5 tables, 10 indexes |
| `test/DataServingApplicationTests.java` | 1.9 | `@SpringBootTest` + Testcontainers (Docker) |
| `test/TestcontainersConfiguration.java` | 0.6 | `@ServiceConnection` `PostgreSQLContainer` image `postgres:18-alpine` |
| `test/api/PoiControllerIntegrationTest.java` | 17.7 | `@WebMvcTest(PoiController)` (no Docker) |
| `test/domain/repository/PoiRepositoryIntegrationTest.java` | 9.7 | `@SpringBootTest` + Testcontainers (Docker) |
| `test/service/PoiServiceTest.java` | 15.2 | Mockito unit test |
| `test/common/dto/ApiResponseTest.java`, `test/common/web/GlobalExceptionHandlerTest.java`, `RequestIdFilterTest.java` | 3.2, 5.7, 4.4 | Unit tests |
| `test/service/util/{BusinessSectorDictionary,LanguageResolver,SubcategoryTagsParser}Test.java` | 1.6, 1.7, 1.5 | Unit tests |
| `src/test/resources/application.yml` | 0.3 | Test config (Flyway enabled) |
| `docs/poi-serving-api/API-GAPS.md` | 16.1 | Vietnamese: contract for 11 APIs, gaps vs model, questions |
| `docs/poi-serving-api/DESIGN-AND-PLAN.md` | 26.7 | Vietnamese: target architecture, plan, DB ownership (§C.4), blockers (§G) |
| `docs/poi-serving-api/FEED-SERVICE-GROUND-TRUTH.md` | 12.3 | Vietnamese: behavior of legacy `feed-service`/`go-common` APIs |
| `docs/poi-serving-api/HANDOFF.md` | 23.3 | Vietnamese: system map, gap register, `poi_id` blast radius (§7), decisions (§10) |
| `docs/poi-serving-api/scripts/check-gaps.py` | 6.1 | Gap probe against PostgreSQL via `PG*` env; docstring names a DEV host |
| `docs/poi-serving-api/scripts/list-repos.sh` | 1.0 | Lists Azure DevOps repos; reads a PAT from env |

Size totals: Java main ≈ 79 KB (33 files), Java test ≈ 63 KB (11 files), docs ≈ 85 KB (6 files).

## 2. Real build, test, and run commands

| Source | Command or setting |
|---|---|
| `mvnw` / `pom.xml` | `./mvnw test` (Windows `mvnw.cmd test`). No surefire/failsafe override, so default Surefire includes `*Test`/`*Tests`; the two `@SpringBootTest` + Testcontainers classes need a running Docker daemon |
| `pom.xml` | `./mvnw package`; compiler annotation processors: Lombok, `spring-boot-configuration-processor` |
| `Dockerfile` stage 1 | Image `maven:3.9-eclipse-temurin-26`; `mvn dependency:go-offline -q`; `mvn clean package -DskipTests -q` |
| `Dockerfile` stage 2 | Image `eclipse-temurin:26-jre`; non-root user; `EXPOSE 8080`; JVM flags ZGC, `MaxRAMPercentage=75`; `HEALTHCHECK` on `/actuator/health` |
| `docker-compose.yml` | `docker compose up`: `postgres` (`postgres:18-alpine`, DB `vv_data_serving`, host port `${POSTGRES_PORT:-55432}`, healthcheck `pg_isready`) and `data-serving-service` (port 8080, env `POSTGRES__DP_POI__URL/USERNAME/PASSWORD`, `SERVER_PORT`, `LOG_LEVEL`). Local credentials are inline (values not copied) |
| `src/main/resources/application.yml` | Datasource from `POSTGRES__DP_POI__{URL,HOST,PORT,DBNAME,SSLMODE,USERNAME,PASSWORD}` with inline defaults (values not copied), `currentSchema=apps`; Hikari pool env `HIKARI_MAX_POOL_SIZE`, `HIKARI_MIN_IDLE`; `ddl-auto: none`; `open-in-view: false`; virtual threads on; **`flyway.enabled: false`**; actuator `health,info,metrics,prometheus`; springdoc `/swagger-ui.html`, `/v3/api-docs` |
| `src/test/resources/application.yml` | **`flyway.enabled: true`**, schema `apps`, `baseline-on-migrate` |

Endpoints (`PoiController`): `GET /api/v1/pois/compact`, `GET /api/v1/pois/{poi_id}/gallery`, `GET /api/v1/pois/{poi_id}/reviews`, `GET /api/v1/pois/{poi_id}/amenities`.

## 3. Tables and columns (Flyway V1 vs entities)

All five entities use `@Table(schema = "apps")`; every Flyway column has a matching `@Column` (names and Java types consistent: `TEXT`→`String`, `DOUBLE PRECISION`→`Double`, `NUMERIC(4,2)`→`BigDecimal`, `INTEGER`→`Integer`, `BIGINT`→`Long`, `TIMESTAMP`→`LocalDateTime`).

| Table | Cols | Primary key (Flyway = entity) | Columns |
|---|---:|---|---|
| `apps.srv_poi_info` | 32 | `poi_id` | poi_id, poi_name, source_name, business_sector, business_category, subcategory_tags, destination_id, full_address, street, ward, district, city, country_code, postal_code, lat, lng, phone, email, website_url, operating_status, is_verified, is_recommended, is_bookable, operating_hours, holiday_exceptions, rating_overall, rating_count, review_count, row_hash, created_at, updated_at, deleted_at |
| `apps.srv_poi_multi_lang` | 12 | `(poi_id, lang)` `@IdClass PoiMultiLangId` | poi_id, lang, source_name, time_to_spend, best_time, cost_vnd, description, experience, row_hash, created_at, updated_at, deleted_at |
| `apps.srv_poi_amenity` | 11 | `(poi_id, business_sector, amenity_group, amenity_raw)` `@IdClass PoiAmenityId` | poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_vi, service_flags, row_hash, created_at, updated_at, deleted_at |
| `apps.srv_poi_media_gallery` | 16 | `media_id` | media_id, poi_id, source_name, photo_api_uri, display_order, width_px, height_px, photographer, blob_url, thumbnail_url, is_cover, is_active, row_hash, created_at, updated_at, deleted_at |
| `apps.srv_poi_review` | 14 | `review_id` | review_id, poi_id, source_name, rating_overall, rating_count (BIGINT), title, review_text, rating, review_date, author_name, row_hash, created_at, updated_at, deleted_at |

Flyway also creates schema `apps` and 10 indexes (info: destination_id, business_category, (lat,lng), (is_recommended,is_verified,is_bookable), row_hash, deleted_at; one `poi_id` index per child table; gallery on `(poi_id, display_order)`).

## 4. Join points with gold in `SunGrp_VSVN`

| Object in `SunGrp_VSVN` | Relation to the API |
|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_{info,multi_lang,amenity,media_gallery,review}` — `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `init_tables` (source lines 361–479), `notebooks/NB_CREATE_DDL.ipynb`; nodes `NB_GLD_SRV_POI_*` | Gold source of the five `apps.srv_poi_*` tables (same names minus `gld_`) |
| `sql/postgres/gld_srv_serve.pg.sql` (task `20261029-pg-ddl-gld-srv-serve`) | Second PostgreSQL DDL for the same five `apps` tables, derived from gold; states schema must pre-exist and creates no index |
| `docs/context/mapping_gld_srv_poi_{info,multi_lang,amenity,review}.md`, `docs/context/mapping_poi_media_info.md` | Silver → gold column mapping (5.6–15.8 KB each) |
| `tests/test_gld_srv_poi_contract.py`, `tests/test_initial_ddl_contract.py`, `tests/test_poi_media_amenity_contract.py` | Python contract tests on gold DDL/notebooks; none reads Flyway or entities |
| Gold → PostgreSQL load | No pipeline, notebook, or script in the repo writes `apps.srv_poi_*` (grep for `apps.srv_poi` matches only `sql/postgres/gld_srv_serve.pg.sql`) |

Measured drift (local probe `evidence/probes/api_schema_diff.py`, Flyway V1 vs `sql/postgres/gld_srv_serve.pg.sql`):

| Table | Drift |
|---|---|
| `srv_poi_media_gallery` | PK: Flyway `media_id`; repo PG DDL `(media_id, poi_id)` |
| `srv_poi_review` | `source_name` in Flyway and entity; absent in repo PG DDL and in gold `gld_srv_poi_review` (`NB_SETUP_INITIAL_DDL` lines 464–479) and in `mapping_gld_srv_poi_review.md` |
| `srv_poi_review.rating_count` | `BIGINT` vs `int8` — same type, not drift |
| DDL ownership | Flyway creates schema + indexes (tests only, `flyway.enabled: false` at runtime); repo PG DDL creates neither |
| Other three tables | Same column names and types |
