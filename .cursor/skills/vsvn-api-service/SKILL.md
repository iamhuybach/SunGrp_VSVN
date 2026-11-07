---
name: vsvn-api-service
description: Add or change an endpoint, DTO, entity, repository, Specification, or test in the POI serving API under services/data-serving-service (Spring Boot, JPA, PostgreSQL schema apps). Use for API tasks, the maven verify lane, and the local docker compose runtime check. Do not use for notebooks, pipelines, Fabric DDL, ctrl tables, gold column or key changes, or the gold to PostgreSQL loader.
---

# VSVN API service

Read `services/data-serving-service/AGENTS.md` first (rule `40-java-api` loads it). This skill adds the working order.

## 1. Endpoint

1. Controller in `api/` only parses and validates parameters (`@Min`, `@Max`, `size` ≤ 100), resolves `lang` with `LanguageResolver`, and delegates to `service/`.
2. Service method is `@Transactional(readOnly = true)`, calls `validatePoiExists` for `/{poi_id}/...` routes, batches child reads (one repository call per table per request), and maps entities to records in `api/dto/`.
3. DTO is a Java `record` with `@JsonProperty` snake_case names and `@Schema` descriptions. Every field maps to a gold column or a derived value named in the record's Javadoc.
4. Errors: throw `ResourceNotFoundException` for an unknown or soft-deleted `poi_id`; `GlobalExceptionHandler` renders the envelope. Do not add a new handler for a new endpoint.
5. Filters: extend `PoiSpecifications`; never build JPQL from request strings. Sorting is whitelisted in `parseSort`.
6. Tests: `@WebMvcTest(PoiController.class)` with `@MockitoBean PoiService` for the contract (status, envelope, JSON names, 404 and 422 paths); a Mockito unit test for the service mapping; a repository test only when a query or key changes.

## 2. Entity, key, or column

- The API never adds a column, table, or key. Confirm it exists in `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables` and in `sql/postgres/gld_srv_serve.pg.sql`. Missing → stop, open a data task (`data_model_change`, `run-author --kind model`).
- One `@Column(name = "...")` per line, `name` always set; composite keys use `@IdClass` with every key column marked `@Id`. `tests/test_srv_poi_serving_contract.py` parses this layout.
- Repository generic id type matches the entity key (`String` or the `@IdClass` type).
- After the edit: `pytest -q tests/test_srv_poi_serving_contract.py`, then `mvnw.cmd -q -B test`.

## 3. Tests and verification

- `cd services/data-serving-service && mvnw.cmd -q -B test` with JDK 26 and Docker running. `@SpringBootTest` classes import `TestcontainersConfiguration`, which starts `postgres:18-alpine` and runs `db/00_create_schema_apps.sql` then `gld_srv_serve.pg.sql`.
- `python scripts/vv.py verify <task-id>` repeats the Maven run in the `maven` lane and fails without JDK 26 or Docker. `--allow-no-docker` is diagnostic only and never backs a `local_verification: pass`.
- Fixtures are synthetic: no real names, emails, phones, review texts, or URLs from production.

## 4. Runtime check (D-12)

The user runs it; Main writes `handoffs/author-input.md` and calls `python scripts/vv.py run-author <task-id> --kind runbook`. The runbook: `POSTGRES_USER`/`POSTGRES_PASSWORD` as session environment variables (or a git-ignored `.env`), values never written down; `docker compose up -d --build`; `docker compose exec -T postgres psql ... -c "CREATE SCHEMA IF NOT EXISTS apps"`; `docker compose cp ../../sql/postgres/gld_srv_serve.pg.sql postgres:/tmp/` then `psql -v ON_ERROR_STOP=1 -f /tmp/gld_srv_serve.pg.sql` (`psql` runs in the container and cannot see host paths); optional synthetic rows (≤ 50 per table) copied the same way; `curl /actuator/health` and one request per endpoint; check logs for personal data; `docker compose down -v`. The user pastes sanitized results into `runtime-runbook.md` → `Kết quả người dùng ghi nhận`.

## 5. Review routing

`api/`, `dto/`, entities → `api-contract-reviewer`. `common/web/`, `config/`, `application*.yml`, `pom.xml`, Docker files → `app-security-reviewer`. `domain/repository/`, `service/`, entities → `jpa-performance-reviewer`. Cross-system or key changes add `risk-gate` (`risk_level: high`).

## 6. Stop points

Missing gold column; JDK or Docker absent; a credential or host appears in any file; a contract test failure that points at `sql/postgres/gld_srv_serve.pg.sql` rather than the API.
