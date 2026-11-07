# data-serving-service

Spring Boot read-only API over PostgreSQL schema `apps` (`srv_poi_info`, `srv_poi_multi_lang`, `srv_poi_amenity`, `srv_poi_media_gallery`, `srv_poi_review`). Root `AGENTS.md` applies first; this file adds the API rules. Stack: Java 26, Spring Boot 4.1.x (`pom.xml`), Spring Data JPA, springdoc, Testcontainers. Imported from ADO repo `data-serving-service` commit `20bca8a` on 2026-11-06.

## Contract

- Columns and types come from gold `lh_vv_gold.dbo.gld_srv_poi_*` (`notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables`); primary keys come from NodeSpec `pk` in `notebooks/NB_GLD_SRV_POI_*.ipynb`. `sql/postgres/gld_srv_serve.pg.sql` is the PostgreSQL DDL derived from them. Entities and DTOs expose only columns that exist there. `tests/test_srv_poi_serving_contract.py` enforces this.
- Keys: `srv_poi_info(poi_id)`, `srv_poi_multi_lang(poi_id, lang)`, `srv_poi_amenity(poi_id, business_sector, amenity_group, amenity_raw)`, `srv_poi_media_gallery(media_id, poi_id)`, `srv_poi_review(review_id)`. Composite keys use `@IdClass`.
- `poi_id` never includes language. `srv_poi_review` has no `source_name`, `source`, or `lang` (D-10 of task `20261106-agent-system-unify-api`).
- Read-only: no writes, `spring.jpa.hibernate.ddl-auto: none`, no Flyway, no DDL at runtime. The schema and tables are created by the data side with the repo DDL.
- Query schema `apps` only. Never join to `public`, `poi_mgmt`, `destination_mgmt`, or `admin_ref`.
- Every list endpoint is paginated (`size` ≤ 100). Filters go through `PoiSpecifications`; never concatenate request values into JPQL.
- Responses use `ApiResponse` / `PageResponse`; errors go through `GlobalExceptionHandler`; `lang` resolves through `LanguageResolver`.
- Do not log or return `email`, `phone`, or `author_name` beyond the fields a DTO already exposes. Test fixtures are synthetic.

## Layout

`src/main/java/vn/visitvietnam/dataserving/`: `api/` + `api/dto/`; `service/` + `service/util/`; `domain/entity/` + `domain/repository/`; `common/` envelope, exceptions, filters; `config/`. Tests mirror the tree. `@WebMvcTest` needs no Docker; `@SpringBootTest` uses `TestcontainersConfiguration` (`postgres:18-alpine`, init scripts `db/00_create_schema_apps.sql` then `gld_srv_serve.pg.sql` from `../../sql/postgres` via Maven test resources).

## Commands

- Tests: `mvnw.cmd -q -B test` (POSIX `./mvnw -q -B test`). Needs JDK 26 and a running Docker daemon.
- Package: `mvnw.cmd -q -B package`. Image: `docker build -t data-serving-service .`
- Local run: create `.env` next to `docker-compose.yml` with `POSTGRES_USER` and `POSTGRES_PASSWORD` (never commit it), then `docker compose up -d`. Service on `8080`, PostgreSQL on `${POSTGRES_PORT:-55432}`. Apply the DDL once: `psql -c "CREATE SCHEMA IF NOT EXISTS apps"` then `psql -v ON_ERROR_STOP=1 -f ../../sql/postgres/gld_srv_serve.pg.sql`.
- Health: `GET /actuator/health`. OpenAPI: `/v3/api-docs`, `/swagger-ui.html`.

## Environment variables

`POSTGRES__DP_POI__URL`, `POSTGRES__DP_POI__HOST`, `POSTGRES__DP_POI__PORT`, `POSTGRES__DP_POI__DBNAME`, `POSTGRES__DP_POI__SSLMODE`, `POSTGRES__DP_POI__USERNAME`, `POSTGRES__DP_POI__PASSWORD`, `HIKARI_MAX_POOL_SIZE`, `HIKARI_MIN_IDLE`, `SERVER_PORT`, `LOG_LEVEL`, `OPENAPI_GATEWAY_URL`. Compose: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`. Values live only in the environment or an ignored `.env`; never in the repository, never in a prompt or task artifact.

## Local database for agents

The Cursor MCP server `vv-serving-postgres-local` (`.cursor/mcp.json`) is read-only and reads `VV_SERVING_PG_URL` from the OS environment. Point it at the compose database only. A DEV or production database needs the user's explicit approval for that run, as for Fabric probes.

## Review and verification

`vv.py verify` runs the `maven` lane for changes here and fails without JDK 26 or Docker. Reviewers: `api-contract-reviewer`, `app-security-reviewer`, `jpa-performance-reviewer` (WORKFLOW §7). Runtime proof: user-run `docker compose` smoke in `runtime-runbook.md`.
