# Hướng dẫn kiểm chứng runtime

## Phạm vi và môi trường

API `services/data-serving-service` trên máy local, PostgreSQL do `docker compose` của service tạo. Không gọi Fabric. Không ghi host, token, user hay password vào file này. Lấy giá trị từ biến môi trường của phiên hoặc file `.env` đã được git ignore.

## Điều kiện tiên quyết

- JDK 26 và Docker đang chạy.
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POI_API_BEARER_TOKEN` đã có trong môi trường phiên. Không dán các giá trị đó vào kết quả.
- Ảnh và schema được tạo bằng các bước dưới. Bảng `apps.srv_poi_legacy_id_map` phải có trước khi gọi API (R1).

## Baseline trước khi chạy

- `GET /actuator/health` trả `UP` sau khi container lên.
- `SELECT to_regclass('apps.srv_poi_legacy_id_map')` khác null.
- Bảng map đang rỗng hoặc chỉ có dòng tổng hợp của lần chạy này.

## Các bước thực hiện

1. Trong `services/data-serving-service`, chạy `docker compose up -d --build`.
2. Trong container Postgres: `CREATE SCHEMA IF NOT EXISTS apps`.
3. Copy `sql/postgres/gld_srv_serve.pg.sql` vào container rồi chạy `psql -v ON_ERROR_STOP=1 -f` file đó. Nếu bảng đã có từ trước task này, chạy đúng khối `CREATE TABLE apps.srv_poi_legacy_id_map` trong file.
4. Chèn một dòng `apps.srv_poi_info` tổng hợp (`poi_id` = `11111111-1111-1111-1111-111111111111`, `poi_name` = `Sample POI`, `source_name` = `partner`, `deleted_at` null) và một dòng map (`legacy_poi_id` = `legacy-sample`, `poi_id` = id trên, `poi_id_status` = `OK`). Không dùng tên, email, điện thoại hay URL thật.
5. Gọi mọi endpoint `/api/v1/pois/**` một lần với `legacy-sample` và một lần với `11111111-1111-1111-1111-111111111111`. Header `Authorization: Bearer` lấy từ `POI_API_BEARER_TOKEN`.
6. `POST /api/v1/pois/practical_info` với body 501 phần tử `ids` (kỳ vọng HTTP 422) và với `required_fields=id,name&sort_field=name&sort_order=desc` cùng một id (kỳ vọng HTTP 200).
7. Trong `psql` của container, kiểm tra plan. Thay `:ids` bằng `$1`. Không ghi host hay token.

```sql
PREPARE r(text[]) AS
WITH hit AS (
  SELECT m.legacy_poi_id, m.poi_id
  FROM apps.srv_poi_legacy_id_map m
  WHERE m.legacy_poi_id = ANY (CAST($1 AS text[]))
    AND m.poi_id_status = 'OK'
    AND m.poi_id IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM apps.srv_poi_info x WHERE x.poi_id = m.legacy_poi_id)
)
SELECT h.legacy_poi_id, h.poi_id FROM hit h;
EXPLAIN (ANALYZE, BUFFERS) EXECUTE r(ARRAY['legacy-sample','11111111-1111-1111-1111-111111111111']);
SET enable_seqscan = off;
EXPLAIN (ANALYZE, BUFFERS) EXECUTE r(ARRAY['legacy-sample','11111111-1111-1111-1111-111111111111']);
```

Làm tương tự câu đếm practical info: `$1` là mảng id, `$2` = `''`, `$3` = `''`, `poi_id = ANY (ARRAY(SELECT COALESCE(...)))`. Với `enable_seqscan = off`, cả hai plan phải có `srv_poi_legacy_id_map_pkey` và `srv_poi_info_pkey`. Seq Scan khi để mặc định trên dữ liệu compose nhỏ không tính là lỗi. Cho quyết định D-IDX, chạy thêm `EXPLAIN` câu cover `findActiveCoversByPoiIdIn` và ghi nhận `srv_poi_media_gallery` có bị quét cả bảng hay không.

## Kiểm tra kết quả

- Hai lần gọi cùng endpoint cho id cũ và id mới có cùng status, `data`, và `meta.pagination` nếu có. `data.id` của practical info và compact là `11111111-1111-1111-1111-111111111111`.
- 501 id trả HTTP 422, `meta.error_code` = `ERR_VALIDATION_FAILED`.
- `required_fields=id,name` chỉ còn hai khóa `id` và `name`.
- Log không chứa token, email, điện thoại.

## Chạy lại để kiểm tra idempotency

Gọi lại đúng request GET practical info với id cũ. Status và `data` không đổi. Bảng map không thêm dòng.

## Kiểm tra log và watermark

Xem log service của các request trên. Không có watermark: API chỉ đọc. Không có token hay dữ liệu cá nhân trong log.

## Rollback và forward recovery

- Rollback: triển khai lại image trước task này. Bảng map có thể để nguyên vì API cũ không đọc nó. `DROP TABLE apps.srv_poi_legacy_id_map` chỉ khi người dùng quyết định.
- Forward recovery: dòng map sai thì phía data nạp lại từ gold. API không tự sửa map. Whitelist hoặc sort sai thì sửa code và triển khai lại.

## Kết quả người dùng ghi nhận

- 2026-11-26, local `docker compose` trong `services/data-serving-service`. Không ghi user, password, token.
- Volume Postgres cũ thiếu cột entity đang dùng. Đã thêm `is_active`, `ingestion_ts`, đổi `srv_poi_multi_lang.cost_vnd` thành `cost`, và tạo `apps.srv_poi_legacy_id_map`.
- Chèn `poi_id` `11111111-1111-1111-1111-111111111111` tên `Sample POI`, source `partner`, và map `legacy-sample` status `OK`.
- `GET /actuator/health` là UP.
- GET practical info id mới và id cũ đều HTTP 200. `data` giống nhau. `data.id` là id mới. Gọi lại id cũ không thêm dòng map (vẫn 1 dòng). `meta.timestamp` đổi giữa hai lần gọi.
- POST practical info cả hai id: HTTP 200, 1 phần tử, `total_items` = 1.
- `required_fields=id,name&source=partner&poi_name=Sample`: HTTP 200, chỉ khóa `id`, `name`.
- 501 id: HTTP 422, `ERR_VALIDATION_FAILED`.
- Gallery, reviews, amenities, experiences, compact với id cũ: HTTP 200. Compact `data.id` là id mới.
- EXPLAIN resolve khi mặc định: `srv_poi_legacy_id_map_pkey`, và Seq Scan trên `srv_poi_info` (bảng nhỏ). Khi `enable_seqscan = off`: cả `srv_poi_legacy_id_map_pkey` và `srv_poi_info_pkey`.
- EXPLAIN câu đếm sau khi tắt seq scan: cả hai khóa chính.
- EXPLAIN cover: `Index Scan` trên `srv_poi_media_gallery_pkey`, không phải Seq Scan trên dữ liệu này.
- 2026-11-26, người dùng xác nhận DEV: lỗi 500 cũ hết sau khi thêm bảng `apps.srv_poi_legacy_id_map`, request chạy thành công. Không ghi host, token hay body.
