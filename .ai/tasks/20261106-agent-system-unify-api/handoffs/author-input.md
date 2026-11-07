# Author input: runtime runbook, CT-4 local compose smoke (D-12)

Goal: the user proves on the local machine that `services/data-serving-service` starts with docker compose against the repo DDL (no Flyway), and that the CT-4 contract changes hold at runtime. No Fabric, no DEV or production database.

## Files to read (only these)

- `services/data-serving-service/docker-compose.yml`, `Dockerfile`, `src/main/resources/application.yml`
- `sql/postgres/gld_srv_serve.pg.sql` (column lists for synthetic INSERTs)
- `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java`, `service/PoiService.java` (endpoints, 404 rules, response fields)
- `services/data-serving-service/AGENTS.md` §Commands, §Environment variables
- `architecture.md` → Main brief row 4.17 and `## Rollout, rollback, and forward recovery` (CT-4 row)

## Facts from the files (verify, do not change)

- Shell: Windows PowerShell; working directory `services/data-serving-service`.
- Compose requires `POSTGRES_USER` and `POSTGRES_PASSWORD` (`${VAR:?}`); optional `POSTGRES_PORT` (default `55432`). Service port `8080`. Database `vv_data_serving`, schema `apps`. Containers `data-serving-postgres`, `data-serving-service`; volume `postgres_data`; image `data-serving-service:latest`.
- `OPENAPI_GATEWAY_URL` is read by the app but compose does not pass it to the container; the runbook checks that `/v3/api-docs` `servers` lists only `http://localhost:8080`. Do not tell the user to edit compose.
- The DDL does not create schema `apps` and wraps all tables in one `BEGIN … COMMIT`; re-running it fails with "already exists" and changes nothing.

## Required steps

1. Prerequisites: Docker running, ports 8080 and the PostgreSQL port free, `java -version` not needed (image builds with Maven inside Docker).
2. User sets `POSTGRES_USER`, `POSTGRES_PASSWORD` as process environment variables in the PowerShell session (`$env:POSTGRES_USER = '<CẦN NGƯỜI DÙNG CUNG CẤP>'`). Never write values in the runbook, a file, or the result section. Do not create `.env` in the repo unless the user prefers it (it is git-ignored).
3. `docker compose up -d --build`; wait for `postgres` healthy and `GET /actuator/health` = `UP`.
4. Load schema: `docker compose exec -T postgres psql -U $env:POSTGRES_USER -d vv_data_serving -v ON_ERROR_STOP=1 -c "CREATE SCHEMA IF NOT EXISTS apps"`, then `docker compose cp ../../sql/postgres/gld_srv_serve.pg.sql postgres:/tmp/gld_srv_serve.pg.sql` and `psql … -f /tmp/gld_srv_serve.pg.sql` (avoid PowerShell pipes: they re-encode UTF-8).
5. Insert synthetic rows only (no real names): 2 POIs in `srv_poi_info`; 2 media rows with the same `media_id` and different `poi_id` (proves key `(media_id, poi_id)`, D-09); 2 review rows; 1 amenity row; matching `srv_poi_multi_lang` rows for `vi`. Use `poi_id` values in UUID 8-4-4-4-12 form. Use a single SQL file copied into the container like step 4.
6. Calls (PowerShell `Invoke-RestMethod` or `curl.exe`): `GET /api/v1/pois/compact?ids=<poi1>,<poi2>&lang=vi`; `GET /api/v1/pois/<poi1>/gallery`; `GET /api/v1/pois/<poi1>/reviews?page=0&size=10` (API 9); `GET /api/v1/pois/<poi1>/amenities?lang=vi`; one unknown `poi_id` on reviews; `GET /v3/api-docs`.

## Pass / fail criteria

- PASS: health `UP`; each call 200 with the inserted synthetic data; gallery of poi1 returns its media row and gallery of poi2 returns the row with the same `media_id`; review items have `review_id`, `author_name`, `rating`, `review_text`, `review_date` and no `source_name` (D-10); unknown POI returns the 404 envelope from `GlobalExceptionHandler`; OpenAPI servers = Local only; service log has no `flyway` line.
- FAIL: any other status, a missing table error, `source_name` present, or a startup error. Record the first error line only (no credentials).

## Idempotency, log, watermark

- Re-run step 6: same responses. Re-running the DDL must fail with "already exists" and leave tables intact.
- No ctrl tables or watermark: write "Không áp dụng" in that section; log check = `docker compose logs data-serving-service --tail 200` for ERROR and flyway.

## Rollback and cleanup

- `docker compose down -v` (removes containers and volume `postgres_data`); optional `docker image rm data-serving-service:latest`. Remove the env vars from the session. Repository rollback for CT-4 is the user's git revert per architecture; source repo untouched.

## Result section

User records: date, PASS/FAIL per call, Java/Docker versions, first error line if any. No personal data, no credential values, ≤ 50 rows of samples.
