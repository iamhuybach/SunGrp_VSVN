# Author input

Task `20261126-destinations-json-array`. Serving API only. No notebook, pipeline, or ctrl table.

Environment: `services/data-serving-service`. User runs Docker. Do not write tokens, passwords, or hosts.

- Session env `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POI_API_BEARER_TOKEN`. Never print values.
- `docker compose up -d --build`. API `http://localhost:8080`. Database `vv_data_serving`. Schema `apps`.
- Skip DDL if `apps.srv_poi_info` already exists.

Synthetic rows. `destination_id` and `destination_name` are text.
`INSERT INTO apps.srv_poi_info (poi_id, poi_name, destination_id, destination_name) VALUES ('poi-dest-array', 'Dest Array', '["dest-a","dest-b"]', '["Quan A","Quan B"]'), ('poi-dest-null', 'Dest Null', NULL, NULL);`

Checks. `Authorization: Bearer` from the env var. `Content-Type: application/json`. Record JSON types only, not raw names beyond these synthetic values.
1. `GET /actuator/health` → `UP`.
2. `POST /api/v1/pois/compact` body `{"ids":["poi-dest-array"]}` → 200. `destinations.id` and `destinations.name` are arrays, first elements `dest-a` and `Quan A`.
3. `GET /api/v1/pois/poi-dest-array/practical_info` → 200. Same array types as step 2.
4. `POST /api/v1/pois/practical_info?required_fields=destinations` body `{"ids":["poi-dest-array"]}` → 200. Same subtree.
5. `POST /api/v1/pois/compact` body `{"ids":["poi-dest-null"]}` → 200. `"destinations":{"id":null,"name":null}`.
6. Repeat step 2. Same status and first id. Row count of the two poi ids stays 2.
7. Count log lines `stored_json_parse_failed` with `field=destination_`. Expect 0 for these synthetic rows. Do not paste log lines.

No watermark. Logs must not contain the token. Rollback is `docker compose down -v` only after the user confirms the volume can be deleted.
Paste sanitized output into `Kết quả người dùng ghi nhận`. At most 50 lines. No personal data, no secrets.
