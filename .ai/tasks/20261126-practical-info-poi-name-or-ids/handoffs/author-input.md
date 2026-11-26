# Author input

Task `20261126-practical-info-poi-name-or-ids`. Serving API only. No notebook, pipeline, or ctrl table.

Environment: `services/data-serving-service`. User runs Docker. Do not write tokens, passwords, or hosts.

From `services/data-serving-service/AGENTS.md` and `docker-compose.yml`:
- Session env `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POI_API_BEARER_TOKEN`. Never print the values.
- `docker compose up -d --build` from that directory. API `http://localhost:8080`. Postgres `${POSTGRES_PORT:-55432}`.
- Database name `vv_data_serving`. Schema `apps`. DDL `sql/postgres/gld_srv_serve.pg.sql`.
- If `apps.srv_poi_info` already exists, skip replaying the DDL.

Synthetic rows only. `poi_id` is the only NOT NULL column.
`INSERT INTO apps.srv_poi_info (poi_id, poi_name) VALUES ('poi-name-cafe', 'Sample Cafe'), ('poi-name-tea', 'Tea House');`

Checks. Header `Authorization: Bearer` from the env var. `Content-Type: application/json`.
1. `GET /actuator/health` → `UP`.
2. Body `{"poi_name":"Cafe"}` → HTTP 200, `total_items` 1, `data[0].id` `poi-name-cafe`.
3. Body `{"ids":["poi-name-tea"]}` → HTTP 200, `total_items` 1, `data[0].id` `poi-name-tea`.
4. Body `{"ids":["poi-name-tea"],"poi_name":"Cafe"}` → HTTP 200, `total_items` 2, ids `poi-name-cafe` and `poi-name-tea`.
5. Body `{}` → HTTP 422, `meta.error_code` `ERR_VALIDATION_FAILED`.
6. Query `?poi_name=Tea` with body `{"ids":["poi-name-cafe"]}` → HTTP 200, `total_items` 1, id `poi-name-cafe`.
7. Repeat step 2. Same status and `total_items`. `count(*)` of the two ids stays 2.

Latency baseline, read-only, inside the postgres container. Do not print the plan if it contains a secret (it will not). Record timing and whether the plan says `Seq Scan` on `srv_poi_info`:
`EXPLAIN (ANALYZE, BUFFERS)` for the name-only predicate `lower(poi_name) LIKE lower('%Cafe%') ESCAPE '!'` and for the union of `poi_id = 'poi-name-tea'` with that name predicate. Limit the pasted plan to 50 lines.

No watermark. Logs must not contain the token or `Cafe`. Rollback is `docker compose down -v` only after the user confirms the local volume can be deleted. Forward recovery is compose up, schema, DDL if needed, and the same insert.
Paste sanitized output into `Kết quả người dùng ghi nhận`.
