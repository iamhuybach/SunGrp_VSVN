# Hướng dẫn kiểm chứng runtime

Trạng thái: `PASS`.

## Phạm vi và môi trường

API đọc POI trên `services/data-serving-service`, cổng `8080`, Postgres local của `docker-compose.yml` trong thư mục đó, database `vv_data_serving`, schema `apps`. Không đụng Fabric. Không ghi host, user, password vào file kết quả.

## Điều kiện tiên quyết

JDK 26. Docker Desktop đang chạy. Trong thư mục `services/data-serving-service`, process env có `POSTGRES_USER`, `POSTGRES_PASSWORD`, và `POSTGRES_PORT=55432`. Không commit các giá trị đó. File `.env` của service dùng key `POSTGRES__DP_POI__*`; compose đọc `POSTGRES_USER` và `POSTGRES_PASSWORD`, nên phải gán vào process env trước `docker compose`.

## Baseline trước khi chạy

`docker compose ps` trong `services/data-serving-service` chưa có container `data-serving-service` healthy, hoặc volume local chưa có schema `apps`. Ghi một dòng trạng thái vào `evidence/runtime/baseline.txt`.

## Các bước thực hiện

1. Từ `services/data-serving-service`, chạy `docker compose up -d --build`. Đợi `data-serving-postgres` healthy và `data-serving-service` lên cổng `8080`.
2. Tạo schema nếu chưa có: `CREATE SCHEMA IF NOT EXISTS apps;` trong database `vv_data_serving`.
3. Áp `sql/postgres/gld_srv_serve.pg.sql` từ gốc repo bằng `psql -v ON_ERROR_STOP=1`. File đã có `BEGIN`/`COMMIT`. Lần chạy lại trên DB đã có bảng sẽ lỗi `already exists` và rollback; khi đó bỏ qua bước này.
4. Chạy fixture tổng hợp dưới đây một lần. Id cố định, không có dữ liệu cá nhân.

```sql
INSERT INTO apps.srv_poi_info (
    poi_id, poi_name, source_name, business_sector, business_category,
    is_recommended, is_verified, rating_overall, rating_count,
    cover_id, cover_blob_url, destination_id, operating_hours, holiday_exceptions,
    lat, lng, full_address, created_at
) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'POI Attraction', 'partner', 'attraction', 'landmark',
 true, true, NULL, NULL, 'cover-a', 'pois/a.jpg', 'dest-1', NULL,
 '[{"date":"02/09/2026","hours":["08:00-17:00"],"title":"Quoc khanh","status":false}]',
 21.02, 105.85, '1 Pho Fixture', TIMESTAMP '2026-01-03 00:00:00'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 'POI FnB', 'partner', 'f_n_b', 'restaurant',
 true, true, NULL, NULL, NULL, NULL, 'dest-1', NULL, '[]',
 NULL, NULL, NULL, TIMESTAMP '2026-01-02 00:00:00'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', 'POI Event', 'other', 'event', 'show',
 false, false, 4.80, 120, 'cover-c', 'pois/c.jpg', 'dest-2',
 '[{"day_of_week":1,"open_time":"09:00","close_time":"18:00","is_open_all_day":false,"is_closed":false}]',
 '[]', 10.00, 106.00, NULL, TIMESTAMP '2026-01-01 00:00:00');

INSERT INTO apps.srv_poi_multi_lang (poi_id, lang, source_name, description, experience, time_to_spend, cost_vnd, best_time)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'vi', 'partner', 'Mo ta vi',
 '[{"title":"Dao pho","description":"Di bo","keyword":"walk"}]',
 '{"Thoi gian":"1 gio"}', NULL, NULL),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'en', 'partner', 'English text',
 '[{"title":"Walk","description":"On foot"}]', NULL, NULL, NULL);

INSERT INTO apps.srv_poi_media_gallery (media_id, poi_id, blob_url, display_order, is_cover, is_active)
VALUES
('media-a', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'pois/gallery-a.jpg', 1, true, true),
('media-b', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'pois/gallery-b.jpg', 2, false, true);

INSERT INTO apps.srv_poi_review (review_id, poi_id, rating, rating_overall, rating_count, review_text, review_date, author_name)
VALUES
('rev-1', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 4.50, 4.20, 3, 'Tot', '2026-04-15', 'Fixture');
```

5. Gọi lần lượt, header `X-Request-Id: 22222222-2222-2222-2222-222222222222`:

- `POST http://localhost:8080/api/v1/pois/compact` body `{"lang":"vi","ids":["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1"]}`, `Content-Type: application/json`.
- `POST` body `{}`.
- `POST` body không phải JSON, ví dụ `{`.
- `GET http://localhost:8080/api/v1/pois/compact`.
- `GET http://localhost:8080/api/v1/pois/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1/gallery?page=0&size=20`.
- `GET http://localhost:8080/api/v1/pois/00000000-0000-0000-0000-000000000000/gallery`.
- `GET http://localhost:8080/api/v1/pois/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1/reviews?page=0&size=10`.
- `GET http://localhost:8080/api/v1/pois/00000000-0000-0000-0000-000000000000/reviews`.
- `GET http://localhost:8080/api/v1/pois/features?page=0&size=10`.
- `GET http://localhost:8080/api/v1/pois/features?size=101`.
- `GET http://localhost:8080/api/v1/pois/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1/experiences?lang=vi`.
- `GET http://localhost:8080/api/v1/pois/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1/practical_info?lang=vi`.
- `GET http://localhost:8080/api/v1/pois/00000000-0000-0000-0000-000000000000/practical_info`.

## Kiểm tra kết quả

- Compact id `...aaa1` HTTP 200, `data[0].cover.id` = `cover-a`, `data[0].cover.file_key` = `pois/a.jpg`, không có `meta.pagination`.
- Body `{}` HTTP 422 `ERR_VALIDATION_FAILED`. Body `{` HTTP 400 `ERR_BAD_REQUEST`, message `Malformed or missing request body.`
- `GET /compact` HTTP 405.
- Gallery POI fixture HTTP 200, `data` có `id`, `file_key`, `display_order`. Gallery POI không tồn tại HTTP 200, `data` `[]`, `total_items` 0.
- Reviews HTTP 200, `rating_summary` một phần tử `rating_count` 3 và `rating_avg_score` 4.2. POI không tồn tại HTTP 200, `data` và `rating_summary` đều `[]`.
- Features HTTP 200, có `meta.pagination`. `size=101` HTTP 422.
- Experiences HTTP 200, `data.items` không rỗng, `source` = `partner`.
- Practical info HTTP 200, `holiday_exceptions` đúng text `apps.srv_poi_info.holiday_exceptions` của fixture, `cover.id` = `media-a`, `cover.file_key` = `pois/gallery-a.jpg`. POI không tồn tại HTTP 404 `POI_NOT_FOUND`.

Mỗi response một file dưới `.ai/tasks/20261110-serving-poi-read-apis/evidence/runtime/`. Tối đa 50 dòng mỗi file. Không dán điện thoại, email, secret, hay chuỗi kết nối.

## Chạy lại để kiểm tra idempotency

Gọi lại đúng `POST /compact` và `GET /practical_info` của POI fixture. Body trùng lần một. Không có dòng mới trong bốn bảng fixture.

## Kiểm tra log và watermark

API này không có watermark. Trong log container `data-serving-service`, không có dòng chứa `Dao pho`, `Di bo`, `1 Pho Fixture`, hay nội dung fixture. WARN `stored_json_parse_failed` nếu có chỉ gồm `poi_id`, `field`, `reason`.

## Rollback và forward recovery

Rollback: tắt `docker compose down` trong `services/data-serving-service` nếu chỉ cần gỡ runtime local. Code: revert commit rồi deploy lại. Không có đổi schema trong task này. Caller compact phải gọi lại `GET` cùng lúc nếu rollback code.

Forward: lỗi parse một trường JSON chỉ làm trường đó null hoặc mảng rỗng. Sửa code rồi deploy tiếp, không cần xóa bảng.

## Kết quả người dùng ghi nhận

PASS, 2026-11-11. Người dùng yêu cầu Main tự chạy. Kết quả nằm ở `.ai/tasks/20261110-serving-poi-read-apis/evidence/runtime/`. Sau D-7, `12-practical.json` và `15-practical-rerun.json` được gọi lại: `holiday_exceptions` là JSON nguyên của cột, không bọc thành chuỗi.

PASS, 2026-11-11. Người dùng yêu cầu test mọi API trên Dev. Process local cổng `18081` đọc Postgres Dev từ `.env`, không ghi host hay secret. Bằng chứng đã làm sạch: `evidence/runtime/dev-api-summary.json`. Bảy API đều HTTP 200. Compact rỗng HTTP 422, body hỏng HTTP 400, GET compact HTTP 405, features `size=101` HTTP 422, practical_info POI không có HTTP 404 `POI_NOT_FOUND`. `holiday_exceptions` là mảng JSON, khóa `date`, `hours`, `title`, `status` giữ nguyên.
