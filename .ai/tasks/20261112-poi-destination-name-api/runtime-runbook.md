# Runtime runbook — 20261112-poi-destination-name-api

Người dùng tự chạy runbook này trên máy local. Tài liệu này không khẳng định lệnh nào đã được chạy. Mọi mục "Kết quả" để trống cho người dùng tự điền.

## Phạm vi và môi trường

- Chỉ chạy trên runtime local, dùng `services/data-serving-service/docker-compose.yml`. Runbook không chạy Fabric notebook, cell nào (kể cả `NB_CREATE_DDL` cell `poidestpy`), pipeline hay Copy Job. Các bước 2–4 của Rollout trên Fabric và trên PostgreSQL DEV/PROD nằm ngoài runbook này. Người dùng sẽ làm sau.
- Các thay đổi cần kiểm tra trên runtime:
  - `apps.srv_poi_info.destination_name text` nằm sau `destination_id`. Hiện chưa có nguồn đổ vào, nên giá trị luôn là null.
  - `apps.srv_poi_review.source_name text` nằm sau `author_name`. Trong transform, giá trị này được gán cứng là `'google'`.
  - POST `/api/v1/pois/compact`: `data[].destinations` luôn là object `{id, name}`.
  - GET `/api/v1/pois/{poi_id}/practical_info`: không còn `data.business_sector` ở top-level. `data.business_tags.business_sector` vẫn giữ. Có `data.destinations.name`.
  - GET `/api/v1/pois/{poi_id}/amenities`: `items[]` chỉ còn `amenity_code` và `service_flags`, không còn `amenity_label_en` hay `amenity_label_vi`.
  - GET `/api/v1/pois/{poi_id}/experiences`: `data.items[].icon_key` lấy từ `keyword` của chính phần tử đó trong `apps.srv_poi_multi_lang.experience`. Nếu không có `keyword` thì `icon_key` là null.
  - GET `/api/v1/pois/{poi_id}/reviews`: `data[].source_name`.
- Môi trường, lấy từ các file:
  - Service compose `postgres`: image `postgres:18-alpine`, container `data-serving-postgres`, DB `vv_data_serving`, cổng host `${POSTGRES_PORT:-55432}` → `5432`, volume `postgres_data`.
  - Service compose `data-serving-service`: container `data-serving-service`, image `data-serving-service:latest`, cổng `8080:8080`. JDBC trong compose là `jdbc:postgresql://postgres:5432/vv_data_serving?currentSchema=apps&sslmode=disable`.
  - `spring.jpa.hibernate.ddl-auto: none`, `default_schema: apps`. Service không tự tạo bảng hay cột. Phải áp DDL trước khi start service.
  - API: `http://localhost:8080`. Ngôn ngữ mặc định của service là `vi` (`LanguageResolver.DEFAULT_LANG`).
- Shell: các lệnh dưới đây viết cho Git Bash (hoặc WSL), chạy trong thư mục `services/data-serving-service`. Nếu dùng PowerShell, hãy dùng `curl.exe` và tự chuyển cách quote JSON.

## Điều kiện tiên quyết

1. Code của task đã có trong working tree: entity, DTO, `PoiService`, `StoredJsonParser`, `sql/postgres/gld_srv_serve.pg.sql`. Targeted test Maven `-Dtest=PoiServiceTest,PoiControllerIntegrationTest` đã pass hoặc đã được người dùng chấp nhận. Kết quả: `<CẦN NGƯỜI DÙNG CUNG CẤP: kết quả pytest và targeted Maven test trước khi chạy runtime>`.
2. Docker Desktop đang chạy (`docker info` không lỗi).
3. File `services/data-serving-service/.env` đã tồn tại, có `POSTGRES_USER` và `POSTGRES_PASSWORD` (có thể thêm `POSTGRES_PORT`). Không commit file này. Không dán giá trị của nó vào runbook, prompt hay artifact nào.
4. Cổng `8080` và `${POSTGRES_PORT:-55432}` trên máy đang trống.
5. Mở shell tại thư mục service và khai báo helper `psql` chạy trong container. Helper lấy user từ biến môi trường của container nên không cần ghi credential:

```bash
cd services/data-serving-service
pgq() { docker compose exec -T postgres sh -c 'psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d vv_data_serving' ; }
```

Nếu muốn dùng `psql` cài trên host thay cho helper, nạp `.env` vào shell mà không in ra màn hình (`set -a; . ./.env; set +a`). Sau đó dùng `PGPASSWORD="$POSTGRES_PASSWORD" psql -h localhost -p "${POSTGRES_PORT:-55432}" -U "$POSTGRES_USER" -d vv_data_serving -v ON_ERROR_STOP=1 ...`. Host chỉ được là `localhost`.

## Baseline trước khi chạy

Mọi lệnh trong mục này đều chỉ đọc.

B1. Trạng thái compose và volume:

```bash
docker compose ps
docker volume ls --filter name=postgres_data
```

B2. Chỉ start `postgres` để đọc baseline. Bước này không tạo bảng:

```bash
docker compose up -d postgres
docker compose ps postgres   # chờ STATUS = healthy
```

B3. Phân loại volume là "mới" hay "đã có bảng":

```bash
pgq <<'SQL'
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'apps';
SELECT table_name FROM information_schema.tables WHERE table_schema = 'apps' ORDER BY table_name;
SQL
```

- Không có schema `apps`, hoặc có schema nhưng không có bảng nào: đi theo **nhánh A (volume mới)** ở bước 2.
- Có đủ 5 bảng `srv_poi_amenity`, `srv_poi_info`, `srv_poi_media_gallery`, `srv_poi_multi_lang`, `srv_poi_review`: đi theo **nhánh B (volume đã có)** ở bước 2.
- Chỉ có một phần trong 5 bảng: DỪNG. Ghi lại trạng thái và hỏi lại trước khi làm tiếp.

B4. Kiểm tra cột hiện có. Chỉ chạy khi có schema `apps`:

```bash
pgq <<'SQL'
SELECT table_name, column_name, ordinal_position
FROM information_schema.columns
WHERE table_schema = 'apps' AND column_name IN ('destination_name','source_name')
ORDER BY table_name, ordinal_position;
SQL
```

B5. Đếm dòng synthetic còn sót từ lần chạy trước. Prefix `rb_` chỉ dành cho runbook này:

```bash
pgq <<'SQL'
SELECT 'srv_poi_info' t, count(*) FROM apps.srv_poi_info WHERE poi_id LIKE 'rb\_%'
UNION ALL SELECT 'srv_poi_multi_lang', count(*) FROM apps.srv_poi_multi_lang WHERE poi_id LIKE 'rb\_%'
UNION ALL SELECT 'srv_poi_amenity', count(*) FROM apps.srv_poi_amenity WHERE poi_id LIKE 'rb\_%'
UNION ALL SELECT 'srv_poi_review', count(*) FROM apps.srv_poi_review WHERE poi_id LIKE 'rb\_%';
SQL
```

Ghi kết quả B1–B5 vào mục `Kết quả người dùng ghi nhận`.

## Các bước thực hiện

**Bước 1 — Dừng service cũ nếu đang chạy.** Service mới không được chạy trước khi có cột. Nếu chạy trước, Hibernate select `destination_name` hoặc `source_name` sẽ lỗi và API trả HTTP 500.

```bash
docker compose stop data-serving-service
```

**Bước 2A — Volume mới.** Tạo schema, rồi chạy toàn bộ file DDL:

```bash
pgq <<'SQL'
CREATE SCHEMA IF NOT EXISTS apps;
SQL
pgq < ../../sql/postgres/gld_srv_serve.pg.sql
```

Nếu dùng psql trên host thì lệnh tương đương là `psql -v ON_ERROR_STOP=1 -f ../../sql/postgres/gld_srv_serve.pg.sql`, kèm các tham số kết nối ở mục Điều kiện tiên quyết. Kỳ vọng: `BEGIN`, 5 lần `CREATE TABLE`, rồi `COMMIT`.

**Bước 2B — Volume đã có bảng.** Chạy transaction hai ALTER, lấy từ dòng 18 trong header của `sql/postgres/gld_srv_serve.pg.sql`. Bỏ qua bước này nếu B4 đã cho thấy cả `srv_poi_info.destination_name` và `srv_poi_review.source_name`.

```bash
pgq <<'SQL'
BEGIN;
ALTER TABLE apps.srv_poi_info ADD COLUMN destination_name text;
ALTER TABLE apps.srv_poi_review ADD COLUMN source_name text;
COMMIT;
SQL
```

Nếu báo `already exists` thì transaction đã rollback và DB không đổi gì. Khi đó chạy lại B4 để xem cột nào còn thiếu. Nếu chỉ thiếu một cột, chạy riêng đúng một `ALTER` cho cột đó, trong `BEGIN; ... COMMIT;`.

Lưu ý cho volume rất cũ: nếu thiếu `cover_id` hoặc `cover_blob_url`, áp thêm dòng 17 của header: `ALTER TABLE apps.srv_poi_info ADD COLUMN cover_id text, ADD COLUMN cover_blob_url text;`. Khi đó, vị trí cột trên volume cũ sẽ khác với file DDL. Điều này không ảnh hưởng tới Hibernate.

**Bước 3 — Kiểm tra cột sau DDL.** Câu kiểm tra lấy từ Rollout của architecture.md:

```bash
pgq <<'SQL'
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema='apps' AND column_name IN ('destination_name','source_name')
ORDER BY table_name, column_name;
SQL
```

Kỳ vọng có tối thiểu `srv_poi_info.destination_name text` và `srv_poi_review.source_name text`. Ngoài ra còn có `source_name` sẵn có của `srv_poi_info`, `srv_poi_multi_lang` và `srv_poi_media_gallery`.

**Bước 4 — Seed dữ liệu synthetic.** Bước này có ghi dữ liệu. Toàn bộ là dữ liệu giả, không có dữ liệu cá nhân. `destination_name` để null. Review có `source_name = 'google'`. Experience có một phần tử có `keyword` và một phần tử không có.

```bash
pgq <<'SQL'
BEGIN;
INSERT INTO apps.srv_poi_info
  (poi_id, poi_name, source_name, business_sector, business_category, subcategory_tags,
   destination_id, destination_name, full_address, city, country_code, lat, lng,
   operating_status, is_verified, is_recommended, is_bookable,
   rating_overall, rating_count, review_count, created_at, updated_at, deleted_at)
VALUES
  ('rb_poi_destname_001', 'Runbook Synthetic POI', 'google', 'attraction', 'park', NULL,
   'rb_dest_001', NULL, 'Synthetic address', 'Synthetic City', 'VN', 21.0, 105.8,
   'OPERATIONAL', true, false, false,
   4.50, 10, 1, now(), now(), NULL)
ON CONFLICT (poi_id) DO NOTHING;

INSERT INTO apps.srv_poi_multi_lang
  (poi_id, lang, source_name, description, experience, created_at, updated_at, deleted_at)
VALUES
  ('rb_poi_destname_001', 'vi', 'google', 'Mo ta synthetic',
   '[{"title":"Di bo","description":"Trai nghiem synthetic 1","keyword":"walk"},{"title":"Ngam canh","description":"Trai nghiem synthetic 2"}]',
   now(), now(), NULL)
ON CONFLICT (poi_id, lang) DO NOTHING;

INSERT INTO apps.srv_poi_amenity
  (poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_en, amenity_vi, service_flags,
   created_at, updated_at, deleted_at)
VALUES
  ('rb_poi_destname_001', 'attraction', 'parking', 'rb_free_parking', 'free_parking', 'Free parking', 'Bai do xe mien phi', NULL,
   now(), now(), NULL)
ON CONFLICT (poi_id, business_sector, amenity_group, amenity_raw) DO NOTHING;

INSERT INTO apps.srv_poi_review
  (review_id, poi_id, rating_overall, rating_count, title, review_text, rating, review_date, author_name, source_name,
   created_at, updated_at, deleted_at)
VALUES
  ('rb_review_001', 'rb_poi_destname_001', 4.50, 10, NULL, 'Synthetic review text', 5.00, '2026-11-12', 'Synthetic Author', 'google',
   now(), now(), NULL)
ON CONFLICT (review_id) DO NOTHING;
COMMIT;
SQL
```

**Bước 5 — Build và start service.** Thời điểm này cột đã có trong DB.

```bash
docker compose up -d --build data-serving-service
docker compose ps
curl -s http://localhost:8080/actuator/health
```

Kỳ vọng: container `data-serving-service` ở trạng thái running, health trả `"status":"UP"`.

**Bước 6 — Gọi 5 endpoint.** Lưu response vào thư mục tạm ngoài repo:

```bash
OUT="${TMPDIR:-/tmp}/rb-poi-destname"; mkdir -p "$OUT"
curl -s -X POST http://localhost:8080/api/v1/pois/compact \
  -H 'Content-Type: application/json' \
  --data-raw '{"lang":"vi","ids":["rb_poi_destname_001"]}' > "$OUT/compact_1.json"
curl -s 'http://localhost:8080/api/v1/pois/rb_poi_destname_001/practical_info?lang=vi' > "$OUT/practical_info.json"
curl -s 'http://localhost:8080/api/v1/pois/rb_poi_destname_001/amenities' > "$OUT/amenities.json"
curl -s 'http://localhost:8080/api/v1/pois/rb_poi_destname_001/experiences?lang=vi' > "$OUT/experiences.json"
curl -s 'http://localhost:8080/api/v1/pois/rb_poi_destname_001/reviews?page=0&size=10' > "$OUT/reviews.json"
```

## Kiểm tra kết quả

Nếu máy có `jq` thì dùng `jq`. Nếu không, mở file JSON và đối chiếu bằng mắt.

| # | Endpoint | Lệnh kiểm tra | Kỳ vọng |
|---|---|---|---|
| K1 | compact | `jq '.data[0].destinations' "$OUT/compact_1.json"` | `{"id":"rb_dest_001","name":null}`. Key `name` có mặt dù giá trị là null. |
| K2 | practical_info | `jq '.data \| has("business_sector")' "$OUT/practical_info.json"` | `false` |
| K3 | practical_info | `jq '.data.business_tags.business_sector' "$OUT/practical_info.json"` | `"attraction"` |
| K4 | practical_info | `jq '.data.destinations' "$OUT/practical_info.json"` | `{"id":"rb_dest_001","name":null}` |
| K5 | amenities | `jq '[.data[].items[] \| keys] \| add \| unique' "$OUT/amenities.json"` | Chỉ có `amenity_code` và `service_flags`. Không có `amenity_label_en`, `amenity_label_vi`. |
| K6 | amenities | `jq '.data[0].items[0].amenity_code' "$OUT/amenities.json"` | `"free_parking"` |
| K7 | experiences | `jq '[.data.items[].icon_key]' "$OUT/experiences.json"` | `["walk", null]` |
| K8 | reviews | `jq '[.data[].source_name]' "$OUT/reviews.json"` | `["google"]` |
| K9 | tất cả | `grep -L '"success"' "$OUT"/*.json` hoặc đọc HTTP status | Không có response 500. Cả 5 response đều thành công. |

Kiểm tra DB sau seed. Câu này chỉ đọc:

```bash
pgq <<'SQL'
SELECT poi_id, destination_id, destination_name FROM apps.srv_poi_info WHERE poi_id LIKE 'rb\_%' LIMIT 50;
SELECT review_id, poi_id, source_name FROM apps.srv_poi_review WHERE poi_id LIKE 'rb\_%' LIMIT 50;
SQL
```

Kỳ vọng: `destination_name` là null, `source_name` là `google`.

Nếu bất kỳ dòng K1–K9 nào sai: dừng lại, giữ nguyên DB, rồi chuyển sang mục `Kiểm tra log và watermark`.

## Chạy lại để kiểm tra idempotency

I1. Chạy lại file DDL. Kỳ vọng là lỗi và DB không thay đổi:

```bash
pgq < ../../sql/postgres/gld_srv_serve.pg.sql
```

Kỳ vọng: lỗi `relation "srv_poi_info" already exists`, psql thoát với mã khác 0, transaction rollback. Chạy lại câu ở Bước 3 để xác nhận tập cột giữ nguyên.

Với volume đã có bảng (nhánh B), nếu chạy lại transaction hai ALTER thì kỳ vọng lỗi `column "destination_name" of relation "srv_poi_info" already exists`, rollback và không đổi gì.

I2. Chạy lại seed ở Bước 4. Nhờ `ON CONFLICT ... DO NOTHING`, mọi `INSERT` báo `INSERT 0 0`. Số dòng ở B5 sau lần seed thứ hai phải bằng số dòng sau lần đầu: 1 / 1 / 1 / 1.

I3. Gọi compact lần hai với body giống hệt lần đầu, rồi so sánh với lần đầu:

```bash
curl -s -X POST http://localhost:8080/api/v1/pois/compact \
  -H 'Content-Type: application/json' \
  --data-raw '{"lang":"vi","ids":["rb_poi_destname_001"]}' > "$OUT/compact_2.json"
jq -S '.data' "$OUT/compact_1.json" > "$OUT/c1.json"; jq -S '.data' "$OUT/compact_2.json" > "$OUT/c2.json"
diff "$OUT/c1.json" "$OUT/c2.json" && echo IDENTICAL
```

Kỳ vọng `IDENTICAL`. Service chỉ đọc, nên gọi lại không ghi gì vào DB.

## Kiểm tra log và watermark

- Task này không dùng watermark (`wm_flow__*`) hay bảng control log của Fabric (`ctrl_*`) trong runtime local, vì không chạy notebook, pipeline hay Copy Job nào. Vì vậy không có watermark hay ctrl log nào để kiểm tra trong runbook này. Lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` của cell `poidestpy` chỉ áp dụng khi người dùng chạy trên Fabric sau này.
- Log service. Chỉ đọc, và chỉ dán tối đa 50 dòng:

```bash
docker compose logs --no-color --tail 200 data-serving-service | grep -E 'ERROR|WARN|stored_json_parse_failed|does not exist' | head -n 50
```

  Kỳ vọng: không có `ERROR`. Không có `column ... does not exist`; nếu có, nghĩa là Bước 2 chưa được áp. Không có `stored_json_parse_failed poi_id=rb_poi_destname_001 field=experience`.
- Log postgres:

```bash
docker compose logs --no-color --tail 100 postgres | grep -E 'ERROR|FATAL' | head -n 50
```

  Lỗi `already exists` từ bước I1 là lỗi được kỳ vọng. Ngoài lỗi đó thì không nên có lỗi nào khác.

## Rollback và forward recovery

Theo mục `Rollback and forward recovery` của architecture.md, áp dụng cho môi trường local:

1. **Service:** revert commit code, rồi build và start lại bằng `docker compose up -d --build data-serving-service`. Chỉ code bị revert. Hai cột PostgreSQL vừa thêm không ảnh hưởng tới entity cũ, vì Hibernate bỏ qua cột không được map.
2. **PostgreSQL** (tùy chọn): chỉ thực hiện **sau khi** service cũ đã chạy ổn. Nếu drop cột khi service mới còn chạy, API sẽ trả 500.

```bash
pgq <<'SQL'
BEGIN;
ALTER TABLE apps.srv_poi_info DROP COLUMN destination_name;
ALTER TABLE apps.srv_poi_review DROP COLUMN source_name;
COMMIT;
SQL
```

3. **Dọn dữ liệu synthetic.** Bước này có ghi. Chỉ xóa các dòng có prefix `rb_`:

```bash
pgq <<'SQL'
BEGIN;
DELETE FROM apps.srv_poi_review WHERE review_id = 'rb_review_001';
DELETE FROM apps.srv_poi_amenity WHERE poi_id = 'rb_poi_destname_001';
DELETE FROM apps.srv_poi_multi_lang WHERE poi_id = 'rb_poi_destname_001';
DELETE FROM apps.srv_poi_info WHERE poi_id = 'rb_poi_destname_001';
COMMIT;
SQL
```

4. **Forward recovery cho local:**
   - Nếu Bước 2 lỗi giữa chừng: transaction đã rollback. Chạy lại B4 để xem cột nào thiếu, rồi chỉ chạy `ALTER` cho cột còn thiếu.
   - Nếu service đã start trước DDL và trả 500: chạy `docker compose stop data-serving-service`, áp Bước 2, rồi chạy lại Bước 5.
5. **Delta/Fabric:** nằm ngoài runbook. Ở đó chỉ có forward-only: không drop cột, vì việc đó cần column mapping mà repo cấm. Muốn lùi notebook thì revert notebook và giữ cột. Cách sửa tiếp theo là land lại thay đổi. Xem chi tiết ở architecture.md.

## Kết quả người dùng ghi nhận

Người dùng tự dán kết quả vào đây. Tối đa 50 dòng mỗi mục. Không có dữ liệu cá nhân, không có user/password/host khác `localhost`, không có nội dung `.env`.

| Mục | Kết quả |
|---|---|
| Nhánh đã chạy (A: volume mới / B: volume đã có) | B. Volume `data-serving-service_postgres_data`, đủ 5 bảng. |
| B1–B5 baseline | Compose chưa chạy. Schema `apps` có 5 bảng. Chưa có `destination_name` và chưa có `srv_poi_review.source_name`. Đếm `rb_` = 0. |
| Bước 2 output (CREATE TABLE / ALTER) | `ALTER TABLE` ×2, `COMMIT`. |
| Bước 3 danh sách cột | `srv_poi_info.destination_name text`, `srv_poi_review.source_name text`. `cover_id` và `cover_blob_url` đã có. |
| Bước 4 seed (`INSERT 0 1` ×4) | `INSERT 0 1` ×4, `COMMIT`. |
| Bước 5 health | `{"status":"UP"}` sau khi build lại image từ source đã restore. |
| K1 compact `destinations` | `{"id":"rb_dest_001","name":null}` |
| K2–K4 practical_info | không có `data.business_sector`; `business_tags.business_sector` = `attraction`; `destinations` = `{"id":"rb_dest_001","name":null}` |
| K5–K6 amenities | keys chỉ `amenity_code`, `service_flags`; `amenity_code` = `free_parking` |
| K7 experiences `icon_key` | `["walk", null]` |
| K8 reviews `source_name` | `["google"]` |
| K9 HTTP status 5 endpoint | cả 5 `success=true` |
| I1 rerun DDL (`already exists`, rollback) | `ERROR: relation "srv_poi_info" already exists`, psql exit 3. Cột giữ nguyên. |
| I2 rerun seed (`INSERT 0 0`) | `INSERT 0 0` ×4. Đếm `rb_` vẫn 1/1/1/1. |
| I3 compact lần 2 (`IDENTICAL`) | `IDENTICAL` |
| Log service/postgres (≤ 50 dòng) | Service không có `ERROR`, `does not exist`, hay `stored_json_parse_failed`. Postgres chỉ có lỗi `already exists` của I1. |
| Rollback/dọn seed đã làm? | Không. Cột và dòng `rb_` vẫn còn. |
| Kết luận PASS/FAIL | PASS các mục K1–K9 và I1–I3. Người dùng xác nhận `gates.runtime` PASS ngày 2026-11-13. |
