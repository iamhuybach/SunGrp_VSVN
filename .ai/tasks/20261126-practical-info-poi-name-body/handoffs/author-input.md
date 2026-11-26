# Author input

Task `20261126-practical-info-poi-name-body`. Serving API only. No notebook, pipeline, or ctrl table.

Environment: `services/data-serving-service`. User runs Docker. Do not write tokens, passwords, or hosts.

Prerequisites from `services/data-serving-service/AGENTS.md`:
- Session env `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POI_API_BEARER_TOKEN`. Never print the values.
- `docker compose up -d --build` from that directory. API `http://localhost:8080`. Postgres `${POSTGRES_PORT:-55432}`.
- `docker compose exec -T postgres psql -U "$POSTGRES_USER" -d vv_data_serving -c "CREATE SCHEMA IF NOT EXISTS apps"`.
- `docker compose cp ../../sql/postgres/gld_srv_serve.pg.sql postgres:/tmp/gld_srv_serve.pg.sql` then `psql -U "$POSTGRES_USER" -d vv_data_serving -v ON_ERROR_STOP=1 -f /tmp/gld_srv_serve.pg.sql` inside the container. Database name is `vv_data_serving` from `docker-compose.yml`.

Synthetic row only. `apps.srv_poi_info` requires `poi_id`. `poi_name` and `deleted_at` are nullable. Insert:
`INSERT INTO apps.srv_poi_info (poi_id, poi_name) VALUES ('poi-practical-name-1', 'French Village Sample');`
No phone, email, or real name.

Checks, header `Authorization: Bearer` from the env var, `Content-Type: application/json`:
1. `GET /actuator/health` → up.
2. `POST /api/v1/pois/practical_info` body `{"ids":["poi-practical-name-1"],"poi_name":"French Village"}` → HTTP 200, `data` length 1, `meta.pagination.total_items` 1.
3. Same ids, body `poi_name` `ZZZ-NO-MATCH` → HTTP 200, `data` `[]`, `total_items` 0.
4. Same ids, no body `poi_name`, query `poi_name=ZZZ-NO-MATCH` → HTTP 200, `data` length 1. The query does not filter.
5. Body `poi_name` of 129 `x` characters → HTTP 422, `meta.error_code` `ERR_VALIDATION_FAILED`.
6. Raw body longer than `98304` bytes (`PracticalInfoBodyLimitFilter.MAX_BYTES`, `96 * 1024`) → HTTP 400, `meta.error_code` `ERR_BODY_TOO_LARGE`.
7. `GET /api/v1/pois/poi-practical-name-1/practical_info` → HTTP 200, `data.id` `poi-practical-name-1`, `data.name` `French Village Sample`.

Idempotency: repeat step 2. Same status and `total_items`. No watermark. Logs must not contain the token or `poi_name` value.

Rollback: `docker compose down -v`. Forward recovery: compose up, schema, DDL, and the same insert.
Paste sanitized output into `Kết quả người dùng ghi nhận`. At most 50 rows. No personal data, no secrets.
