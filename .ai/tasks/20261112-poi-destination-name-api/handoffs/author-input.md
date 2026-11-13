# Author input — runtime runbook

Write only `runtime-runbook.md` in Vietnamese. Do not edit source, state, or decisions. Do not claim any command has already run.

## User comments (verbatim)

- slv_enr_poi_destination.destination_name hiện tại chỉ tạo DDL, chưa có nguồn đổ vào.
- Tôi confirm có keyword trong apps.srv_poi_multi_lang.experience. Nếu không có thì để null cho key keyword.
- Lấy source_name trong gld_srv_poi_review fix cứng trong transform là 'google' vì lấy từ bảng thuộc luồng google.
- Các phần bỏ code thực hiện ngay trong task này.

## Read

- `.ai/tasks/20261112-poi-destination-name-api/architecture.md` sections `## Rollout` and `## Rollback and forward recovery`
- `services/data-serving-service/docker-compose.yml`
- `services/data-serving-service/src/main/resources/application.yml` (`ddl-auto: none`, port 8080)
- `sql/postgres/gld_srv_serve.pg.sql` header lines 16-18 and the two CREATE TABLE blocks
- `services/data-serving-service/AGENTS.md` runtime rule: user runs compose; credentials only from the environment

## Constraints

- Local runtime only. No Fabric notebook, pipeline, or Copy Job.
- Credentials come from `services/data-serving-service/.env` (`POSTGRES_USER`, `POSTGRES_PASSWORD`). Never write a password, user, or host other than `localhost` and the compose service names.
- `hibernate.ddl-auto` is `none`. On a fresh volume, start only `postgres`, create schema `apps`, then `psql -v ON_ERROR_STOP=1 -f ../../sql/postgres/gld_srv_serve.pg.sql`, then start `data-serving-service`. On an existing volume, run the commented two-ALTER transaction from the SQL header before starting the service.
- Postgres host port is `${POSTGRES_PORT:-55432}`. API is `http://localhost:8080`.
- Seed synthetic rows only. `destination_name` stays null. Review `source_name` is `google`. Experience JSON may include `keyword`; a missing keyword yields `icon_key` null.
- Check POST `/api/v1/pois/compact` (`data[].destinations.id` and `.name`), GET `/api/v1/pois/{poi_id}/practical_info` (no top-level `data.business_sector`; `data.business_tags.business_sector` remains; `data.destinations.name`), GET amenities (no `amenity_label_en` or `amenity_label_vi`), GET experiences (`data.items[].icon_key`), GET reviews (`data[].source_name`).
- Include the required sections: Phạm vi và môi trường, Điều kiện tiên quyết, Baseline trước khi chạy, Các bước thực hiện, Kiểm tra kết quả, Chạy lại để kiểm tra idempotency, Kiểm tra log và watermark, Rollback và forward recovery, Kết quả người dùng ghi nhận.
- Watermark and Fabric control logs do not apply. Say that explicitly. Idempotency is the SQL file rerun (`already exists`) and a second API call with the same body.
- Paste-back limit: at most 50 rows, no personal data, no secrets, into `Kết quả người dùng ghi nhận`.
