# Runtime runbook: CT-4 local compose smoke (D-12)

Task: `20261106-agent-system-unify-api`, mục 4.17 trong `architecture.md` (Main brief). Runbook này do người dùng tự chạy trên máy local. Kết quả ghi vào mục cuối và là bằng chứng cho `gates.runtime` của CT-4.

## Phạm vi và môi trường

- Mục tiêu: chứng minh `services/data-serving-service` khởi động được bằng `docker compose` với DDL của repo (`sql/postgres/gld_srv_serve.pg.sql`, không có Flyway), và các thay đổi hợp đồng của CT-4 đúng khi chạy thật:
  - khóa `(media_id, poi_id)` của `srv_poi_media_gallery` (D-09);
  - review không có `source_name` (D-10);
  - POI không tồn tại trả về envelope 404 của `GlobalExceptionHandler`;
  - OpenAPI chỉ có server Local.
- Chỉ chạy trên máy local. Không dùng Fabric, không dùng database DEV hay production, không dùng ctrl table.
- Shell: Windows PowerShell. Thư mục làm việc cho mọi lệnh: `services/data-serving-service`, tức `D:\git\SunGrp_VSVN\services\data-serving-service`.
- Các thành phần lấy từ `docker-compose.yml`:
  - Service `postgres`: image `postgres:18-alpine`, container `data-serving-postgres`, database `vv_data_serving`, cổng host `${POSTGRES_PORT:-55432}` → `5432`, volume `postgres_data` (mount `/var/lib/postgresql`).
  - Healthcheck của postgres: `pg_isready -U ${POSTGRES_USER} -d vv_data_serving`, interval 3s, retries 10.
  - Service `data-serving-service`: image `data-serving-service:latest`, container `data-serving-service`, cổng `8080:8080`, chỉ chạy sau khi `postgres` ở trạng thái `service_healthy`.
  - Biến truyền vào container: `POSTGRES__DP_POI__URL=jdbc:postgresql://postgres:5432/vv_data_serving?currentSchema=apps&sslmode=disable`, `POSTGRES__DP_POI__USERNAME`/`POSTGRES__DP_POI__PASSWORD` lấy từ `POSTGRES_USER`/`POSTGRES_PASSWORD`, `SERVER_PORT=8080`, `LOG_LEVEL=INFO`.
- Image được build trong Docker (`Dockerfile`):
  - Stage build dùng `maven:3.9-eclipse-temurin-26` chạy `mvn clean package -DskipTests -q`.
  - Stage runtime dùng `eclipse-temurin:26-jre`, chạy bằng user `app`, có `HEALTHCHECK` gọi `curl --fail http://localhost:8080/actuator/health`.
- Ứng dụng (`application.yml`): `spring.jpa.hibernate.ddl-auto: none`, `hibernate.default_schema: apps`, springdoc tại `/v3/api-docs` và `/swagger-ui.html`, actuator mở `health,info,metrics,prometheus`.
- `OPENAPI_GATEWAY_URL` được `OpenApiConfig` đọc (mặc định rỗng), nhưng compose không truyền biến này vào container. Vì vậy `/v3/api-docs` chỉ có server `http://localhost:8080` (Local). Không sửa compose.
- Endpoint kiểm tra (`PoiController`):
  - API 1: `GET /api/v1/pois/compact` với `ids`, `lang`, `page` (mặc định 0), `size` (mặc định 20, tối đa 100), `sort` (mặc định `createdAt` desc).
  - API 3: `GET /api/v1/pois/{poi_id}/gallery`.
  - API 9: `GET /api/v1/pois/{poi_id}/reviews` với `page` (mặc định 0), `size` (mặc định 10, tối đa 100).
  - API 10: `GET /api/v1/pois/{poi_id}/amenities` với `lang`.
- Ba endpoint gallery, reviews và amenities đều gọi `validatePoiExists`. Nếu không có POI với `deleted_at IS NULL`, service ném `ResourceNotFoundException("POI not found with id: <poi_id>")` và `GlobalExceptionHandler` trả HTTP 404 với `success=false`, `code=404`, `data=null`, `meta.error_code="POI_NOT_FOUND"`.
- Runbook không sửa file nào trong repo. File seed tạm nằm ở `$env:TEMP`, ngoài repo.

## Điều kiện tiên quyết

1. Docker Desktop đang chạy và có `docker compose` v2.
2. Không cần cài JDK trên máy. Image tự build Maven/JDK 26 bên trong Docker, nên không cần chạy `java -version` ở host.
3. Cổng `8080` và cổng PostgreSQL (`55432`, hoặc giá trị `POSTGRES_PORT` nếu người dùng đặt) phải đang trống.
4. Máy có kết nối mạng để kéo image `postgres:18-alpine`, `maven:3.9-eclipse-temurin-26`, `eclipse-temurin:26-jre` và các dependency Maven trong lần build đầu.
5. Đặt biến môi trường cho phiên PowerShell hiện tại. Giá trị chỉ do người dùng biết; không ghi vào runbook, vào file nào hay vào mục kết quả.

```powershell
Set-Location D:\git\SunGrp_VSVN\services\data-serving-service
$env:POSTGRES_USER = '<CẦN NGƯỜI DÙNG CUNG CẤP: tên user PostgreSQL local>'
# Nhập mật khẩu không hiện lên màn hình và không lưu vào lịch sử lệnh:
$sec = Read-Host -AsSecureString 'POSTGRES_PASSWORD'
$env:POSTGRES_PASSWORD = [System.Net.NetworkCredential]::new('', $sec).Password
Remove-Variable sec
# Chỉ đặt khi cổng 55432 đang bận:
# $env:POSTGRES_PORT = '<CẦN NGƯỜI DÙNG CUNG CẤP: cổng host trống khác>'
```

Bạn cũng có thể dùng file `.env` đặt cạnh `docker-compose.yml` (đã được git-ignore) nếu muốn, nhưng runbook này không tạo `.env`. Biến môi trường của tiến trình được ưu tiên hơn `.env`.

## Baseline trước khi chạy

Mọi lệnh ở mục này chỉ đọc.

```powershell
docker version --format '{{.Server.Version}}'
docker compose version
Get-NetTCPConnection -State Listen -LocalPort 8080 -ErrorAction SilentlyContinue
Get-NetTCPConnection -State Listen -LocalPort 55432 -ErrorAction SilentlyContinue
docker ps -a --filter "name=data-serving" --format "{{.Names}} {{.Status}}"
docker volume ls --filter "name=postgres_data"
Test-Path .env
git -C D:\git\SunGrp_VSVN status --short -- services/data-serving-service sql/postgres
```

Kết quả mong đợi:

- Hai lệnh `Get-NetTCPConnection` không in gì. Nếu cổng `55432` bận, đặt `POSTGRES_PORT` như ở mục trên rồi kiểm tra lại cổng đó.
- Không có container `data-serving-postgres` hoặc `data-serving-service`.
- Volume chứa `postgres_data` của project này không tồn tại. Nếu nó còn từ lần chạy trước, bảng có thể đã có sẵn, nên chạy `docker compose down -v` trước. Lệnh này xóa dữ liệu local của compose này; hãy xem kỹ tên volume trước khi xóa.
- `Test-Path .env` cho biết compose có đọc thêm `.env` hay không. Chỉ ghi True hoặc False, không ghi nội dung file.
- Ghi lại output của `git status` để so sánh sau khi chạy. Runbook không được làm thay đổi output này.

## Các bước thực hiện

### Bước 1. Build và khởi động

```powershell
docker compose up -d --build
docker compose ps
```

Chờ đến khi `docker compose ps` hiện `data-serving-postgres` ở trạng thái `(healthy)` và `data-serving-service` ở trạng thái `Up`. Sau đó gọi health:

```powershell
Invoke-RestMethod http://localhost:8080/actuator/health
```

Mong đợi `status` = `UP`. Nếu lệnh lỗi kết nối, đợi 10–30 giây rồi thử lại. Healthcheck của image có `start-period=30s`. Nếu sau khoảng 2 phút vẫn không `UP`, chuyển sang mục "Kiểm tra log và watermark" để lấy dòng lỗi đầu tiên.

### Bước 2. Nạp schema và DDL của repo

DDL không tạo schema `apps` và bọc 5 bảng trong một khối `BEGIN … COMMIT`. Copy file vào container thay vì pipe qua PowerShell, vì pipe sẽ mã hóa lại UTF-8.

```powershell
docker compose exec -T postgres psql -U $env:POSTGRES_USER -d vv_data_serving -v ON_ERROR_STOP=1 -c "CREATE SCHEMA IF NOT EXISTS apps"
docker compose cp ../../sql/postgres/gld_srv_serve.pg.sql postgres:/tmp/gld_srv_serve.pg.sql
docker compose exec -T postgres psql -U $env:POSTGRES_USER -d vv_data_serving -v ON_ERROR_STOP=1 -f /tmp/gld_srv_serve.pg.sql
$LASTEXITCODE
```

Mong đợi: lệnh đầu in `CREATE SCHEMA`, lệnh `-f` in `BEGIN`, 5 dòng `CREATE TABLE`, rồi `COMMIT`. `$LASTEXITCODE` = `0`.

Kiểm tra bảng (chỉ đọc):

```powershell
docker compose exec -T postgres psql -U $env:POSTGRES_USER -d vv_data_serving -c "\dt apps.*"
docker compose exec -T postgres psql -U $env:POSTGRES_USER -d vv_data_serving -At -c "SELECT to_regclass('apps.flyway_schema_history') IS NULL"
```

Mong đợi:

- Có đúng 5 bảng: `srv_poi_amenity`, `srv_poi_info`, `srv_poi_media_gallery`, `srv_poi_multi_lang`, `srv_poi_review`.
- Lệnh thứ hai in `t`, tức không có bảng lịch sử Flyway.

### Bước 3. Chèn dữ liệu synthetic

Mọi dữ liệu đều là dữ liệu giả, chỉ gồm ký tự ASCII, không có tên thật. File được ghi ra `$env:TEMP`, ngoài repo, với encoding ASCII để không có BOM.

Giá trị cố định dùng cho cả runbook:

- `poi1` = `11111111-1111-4111-8111-111111111111`
- `poi2` = `22222222-2222-4222-8222-222222222222`
- POI không tồn tại = `99999999-9999-4999-8999-999999999999`
- `media_id` dùng chung cho cả hai POI = `ct4-smoke-media-0001`

```powershell
$seed = @'
BEGIN;
INSERT INTO apps.srv_poi_info (poi_id, poi_name, business_sector, business_category, full_address, street, city, country_code, lat, lng, operating_status, rating_overall, rating_count, review_count, created_at, updated_at) VALUES
 ('11111111-1111-4111-8111-111111111111', 'CT4 Smoke POI One', 'SMOKE', 'SMOKE_CATEGORY', 'Synthetic Address 1', 'Synthetic Street 1', 'Synthetic City', 'VN', 10.0, 106.0, 'OPERATIONAL', 4.25, 2, 2, TIMESTAMP '2026-11-01 00:00:00', TIMESTAMP '2026-11-01 00:00:00'),
 ('22222222-2222-4222-8222-222222222222', 'CT4 Smoke POI Two', 'SMOKE', 'SMOKE_CATEGORY', 'Synthetic Address 2', 'Synthetic Street 2', 'Synthetic City', 'VN', 11.0, 107.0, 'OPERATIONAL', 3.50, 0, 0, TIMESTAMP '2026-11-02 00:00:00', TIMESTAMP '2026-11-02 00:00:00');
INSERT INTO apps.srv_poi_multi_lang (poi_id, lang, description, created_at, updated_at) VALUES
 ('11111111-1111-4111-8111-111111111111', 'vi', 'Synthetic description one', TIMESTAMP '2026-11-01 00:00:00', TIMESTAMP '2026-11-01 00:00:00'),
 ('22222222-2222-4222-8222-222222222222', 'vi', 'Synthetic description two', TIMESTAMP '2026-11-02 00:00:00', TIMESTAMP '2026-11-02 00:00:00');
INSERT INTO apps.srv_poi_media_gallery (media_id, poi_id, photo_api_uri, display_order, width_px, height_px, blob_url, is_cover, is_active, created_at, updated_at) VALUES
 ('ct4-smoke-media-0001', '11111111-1111-4111-8111-111111111111', NULL, 1, 800, 600, 'https://example.invalid/ct4-smoke/media-0001-poi1.jpg', true, true, TIMESTAMP '2026-11-01 00:00:00', TIMESTAMP '2026-11-01 00:00:00'),
 ('ct4-smoke-media-0001', '22222222-2222-4222-8222-222222222222', NULL, 1, 800, 600, 'https://example.invalid/ct4-smoke/media-0001-poi2.jpg', true, true, TIMESTAMP '2026-11-02 00:00:00', TIMESTAMP '2026-11-02 00:00:00');
INSERT INTO apps.srv_poi_review (review_id, poi_id, title, review_text, rating, review_date, author_name, created_at, updated_at) VALUES
 ('ct4-smoke-review-0001', '11111111-1111-4111-8111-111111111111', 'Synthetic title one', 'Synthetic review text one', 4.50, '2026-11-01', 'Smoke Tester A', TIMESTAMP '2026-11-01 00:00:00', TIMESTAMP '2026-11-01 00:00:00'),
 ('ct4-smoke-review-0002', '11111111-1111-4111-8111-111111111111', 'Synthetic title two', 'Synthetic review text two', 4.00, '2026-11-02', 'Smoke Tester B', TIMESTAMP '2026-11-02 00:00:00', TIMESTAMP '2026-11-02 00:00:00');
INSERT INTO apps.srv_poi_amenity (poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_vi, service_flags, created_at, updated_at) VALUES
 ('11111111-1111-4111-8111-111111111111', 'SMOKE', 'FACILITY', 'smoke_wifi_raw', 'smoke_wifi', 'Wifi thu nghiem', NULL, TIMESTAMP '2026-11-01 00:00:00', TIMESTAMP '2026-11-01 00:00:00');
COMMIT;
'@
Set-Content -Path "$env:TEMP\ct4_smoke_seed.sql" -Value $seed -Encoding ascii
docker compose cp "$env:TEMP\ct4_smoke_seed.sql" postgres:/tmp/ct4_smoke_seed.sql
docker compose exec -T postgres psql -U $env:POSTGRES_USER -d vv_data_serving -v ON_ERROR_STOP=1 -f /tmp/ct4_smoke_seed.sql
$LASTEXITCODE
```

Mong đợi: `BEGIN`, rồi `INSERT 0 2` bốn lần, `INSERT 0 1`, `COMMIT`. `$LASTEXITCODE` = `0`.

Insert thứ hai vào `srv_poi_media_gallery` chỉ thành công khi khóa là `(media_id, poi_id)`, đúng theo D-09. Đây là bằng chứng ở mức DDL.

Không chạy lại file seed. Lần chạy thứ hai sẽ lỗi khóa chính và rollback toàn khối.

Đếm số dòng sau khi seed (chỉ đọc):

```powershell
docker compose exec -T postgres psql -U $env:POSTGRES_USER -d vv_data_serving -At -c "SELECT 'info', count(*) FROM apps.srv_poi_info UNION ALL SELECT 'multi_lang', count(*) FROM apps.srv_poi_multi_lang UNION ALL SELECT 'media', count(*) FROM apps.srv_poi_media_gallery UNION ALL SELECT 'review', count(*) FROM apps.srv_poi_review UNION ALL SELECT 'amenity', count(*) FROM apps.srv_poi_amenity"
```

Mong đợi: `info|2`, `multi_lang|2`, `media|2`, `review|2`, `amenity|1`.

### Bước 4. Gọi API

Windows PowerShell 5.1 có thể hiển thị sai chữ tiếng Việt có dấu trong JSON. Khi cần đọc nhãn tiếng Việt, dùng `curl.exe -o` rồi đọc file bằng `Get-Content -Encoding utf8`. Luôn đặt URL có `&` trong dấu nháy.

```powershell
$base = 'http://localhost:8080'
$poi1 = '11111111-1111-4111-8111-111111111111'
$poi2 = '22222222-2222-4222-8222-222222222222'
$unknown = '99999999-9999-4999-8999-999999999999'

# 4.1 API 1 compact
$r1 = Invoke-RestMethod "$base/api/v1/pois/compact?ids=$poi1,$poi2&lang=vi"
$r1 | ConvertTo-Json -Depth 10

# 4.2 API 3 gallery poi1 và poi2
$r2a = Invoke-RestMethod "$base/api/v1/pois/$poi1/gallery"
$r2a | ConvertTo-Json -Depth 10
$r2b = Invoke-RestMethod "$base/api/v1/pois/$poi2/gallery"
$r2b | ConvertTo-Json -Depth 10

# 4.3 API 9 reviews
$r3 = Invoke-RestMethod "$base/api/v1/pois/$poi1/reviews?page=0&size=10"
$r3 | ConvertTo-Json -Depth 10

# 4.4 API 10 amenities (lưu UTF-8 để đọc nhãn tiếng Việt)
curl.exe -s -o "$env:TEMP\ct4_amenities.json" "$base/api/v1/pois/$poi1/amenities?lang=vi"
Get-Content -Encoding utf8 "$env:TEMP\ct4_amenities.json"

# 4.5 reviews của POI không tồn tại (lấy cả mã HTTP)
curl.exe -s -w "`nHTTP %{http_code}`n" "$base/api/v1/pois/$unknown/reviews?page=0&size=10"

# 4.6 OpenAPI
$r6 = Invoke-RestMethod "$base/v3/api-docs"
$r6.servers | ConvertTo-Json -Depth 5
```

## Kiểm tra kết quả

Tiêu chí PASS cho từng lệnh gọi:

| # | Lệnh gọi | PASS khi |
|---|---|---|
| 0 | `GET /actuator/health` | `status` = `UP` |
| 4.1 | `GET /api/v1/pois/compact?ids=<poi1>,<poi2>&lang=vi` | HTTP 200; `success` = true; `data` có 2 phần tử, sắp theo `createdAt` desc nên `poi2` đứng trước `poi1`; `name` = `CT4 Smoke POI Two` / `CT4 Smoke POI One`; `description` = `Synthetic description two` / `Synthetic description one`; `cover.id` = `ct4-smoke-media-0001` ở cả hai; `cover.file_key` là URL `…-poi2.jpg` / `…-poi1.jpg`; `cover.mime_type` = `image/jpeg`; `meta.pagination` có tổng 2 |
| 4.2a | `GET /api/v1/pois/<poi1>/gallery` | HTTP 200; `data` có 1 phần tử: `id` = `ct4-smoke-media-0001`, `file_key` = `https://example.invalid/ct4-smoke/media-0001-poi1.jpg`, `width` 800, `height` 600, `mime_type` = `image/jpeg`, `display_order` = 1 |
| 4.2b | `GET /api/v1/pois/<poi2>/gallery` | HTTP 200; `data` có 1 phần tử với cùng `id` = `ct4-smoke-media-0001` và `file_key` = `https://example.invalid/ct4-smoke/media-0001-poi2.jpg`. Hai POI dùng chung `media_id` mà vẫn tách được, đúng theo D-09 |
| 4.3 | `GET /api/v1/pois/<poi1>/reviews?page=0&size=10` | HTTP 200; `data` có 2 phần tử sắp theo `review_date` desc (`ct4-smoke-review-0002` rồi `ct4-smoke-review-0001`); mỗi phần tử có đúng các khóa `review_id`, `author_name`, `rating`, `review_text`, `review_date`; không có `source_name`, đúng theo D-10; `rating` = 4.0 / 4.5 |
| 4.4 | `GET /api/v1/pois/<poi1>/amenities?lang=vi` | HTTP 200; `data` có 1 nhóm `amenity_group` = `FACILITY`, nhãn nhóm `Tiện nghi cơ sở`; 1 item có `amenity_code` = `smoke_wifi`, `amenity_label` = `Wifi thu nghiem`, `service_flags` = null |
| 4.5 | `GET /api/v1/pois/<unknown>/reviews?page=0&size=10` | `HTTP 404`; body `success` = false, `code` = 404, `message` = `POI not found with id: 99999999-9999-4999-8999-999999999999`, `data` = null, `meta.error_code` = `POI_NOT_FOUND` |
| 4.6 | `GET /v3/api-docs` | HTTP 200; `servers` chỉ có 1 phần tử: `url` = `http://localhost:8080`, `description` = `Local` |

Lệnh nhanh để xác nhận D-10 (chỉ đọc):

```powershell
$r3.data | ForEach-Object { ($_.PSObject.Properties.Name | Sort-Object) -join ',' }
($r3 | ConvertTo-Json -Depth 10) -match 'source_name'
```

Mong đợi: mỗi dòng in `author_name,rating,review_date,review_id,review_text`, và lệnh thứ hai in `False`.

Kết quả là FAIL nếu gặp một trong các trường hợp sau:

- bất kỳ mã HTTP nào khác với bảng trên;
- lỗi thiếu bảng (`relation "apps.…" does not exist`);
- có `source_name` trong review;
- gallery của `poi2` rỗng;
- `servers` có nhiều hơn server Local;
- service không khởi động được.

Khi FAIL, chỉ ghi dòng lỗi đầu tiên và không ghi credential.

## Chạy lại để kiểm tra idempotency

1. Các lệnh GET không ghi gì nên phải cho cùng kết quả. Chạy lại toàn bộ Bước 4, rồi so sánh phần `data`. `meta.timestamp` và `meta.trace_id` được phép khác.

```powershell
$a = (Invoke-RestMethod "$base/api/v1/pois/compact?ids=$poi1,$poi2&lang=vi").data | ConvertTo-Json -Depth 10 -Compress
$b = (Invoke-RestMethod "$base/api/v1/pois/compact?ids=$poi1,$poi2&lang=vi").data | ConvertTo-Json -Depth 10 -Compress
$a -eq $b
$c = (Invoke-RestMethod "$base/api/v1/pois/$poi1/reviews?page=0&size=10").data | ConvertTo-Json -Depth 10 -Compress
$d = (Invoke-RestMethod "$base/api/v1/pois/$poi1/reviews?page=0&size=10").data | ConvertTo-Json -Depth 10 -Compress
$c -eq $d
```

Mong đợi: cả hai lệnh so sánh in `True`. Làm tương tự với gallery của `poi1` và `poi2`, amenities, và lệnh gọi 404 bằng `curl.exe` (vẫn phải là `HTTP 404`).

2. Chạy lại DDL phải lỗi và không thay đổi gì. Đây là bước chạy có chủ đích; nó không ghi được dữ liệu vì khối giao dịch bị hủy.

```powershell
docker compose exec -T postgres psql -U $env:POSTGRES_USER -d vv_data_serving -v ON_ERROR_STOP=1 -f /tmp/gld_srv_serve.pg.sql
$LASTEXITCODE
```

Mong đợi: lỗi `relation "srv_poi_info" already exists` và `$LASTEXITCODE` khác 0. Chạy lại lệnh đếm số dòng ở Bước 3, kết quả vẫn phải là `info|2`, `multi_lang|2`, `media|2`, `review|2`, `amenity|1`. Gọi lại 4.2a và 4.3, kết quả vẫn như cũ.

## Kiểm tra log và watermark

- Ctrl table và watermark: Không áp dụng. Runbook này không chạm vào Fabric, `ctrl_*` hay bất kỳ watermark nào.
- Log của service (chỉ đọc):

```powershell
docker compose logs data-serving-service --tail 200
docker compose logs data-serving-service --tail 200 | Select-String -Pattern 'ERROR'
docker compose logs data-serving-service --tail 200 | Select-String -Pattern 'flyway'
```

Mong đợi:

- Có dòng Spring Boot báo đã khởi động trên cổng `8080`.
- Lệnh lọc `ERROR` không in dòng nào. Riêng lệnh gọi 404 có chủ đích không được tính là lỗi khởi động.
- Lệnh lọc `flyway` không in dòng nào. `Select-String` không phân biệt hoa thường theo mặc định.

Nếu có lỗi, chỉ ghi dòng lỗi đầu tiên, bỏ credential và JDBC URL có user hoặc mật khẩu nếu xuất hiện.

- Phiên bản Java trong container, để ghi kết quả:

```powershell
docker compose exec -T data-serving-service java -version
```

## Rollback và forward recovery

Dọn môi trường local sau khi ghi xong kết quả:

```powershell
docker compose down -v
# Tùy chọn: xóa image đã build
docker image rm data-serving-service:latest
# Xóa file tạm ngoài repo do runbook tạo
Remove-Item "$env:TEMP\ct4_smoke_seed.sql", "$env:TEMP\ct4_amenities.json" -ErrorAction SilentlyContinue
# Xóa biến môi trường khỏi phiên
Remove-Item Env:POSTGRES_USER, Env:POSTGRES_PASSWORD -ErrorAction SilentlyContinue
Remove-Item Env:POSTGRES_PORT -ErrorAction SilentlyContinue
```

`docker compose down -v` xóa hai container `data-serving-postgres`, `data-serving-service` và volume `postgres_data` của project này. Mọi dữ liệu synthetic sẽ mất. Kiểm tra lại bằng `docker ps -a --filter "name=data-serving"` và `docker volume ls --filter "name=postgres_data"`; cả hai không còn dòng nào.

Rollback repository cho CT-4 theo `architecture.md` (mục Rollout, rollback, and forward recovery, hàng 4): người dùng tự revert bằng git các thay đổi Java, test và pom. `V1__init_srv_poi_tables.sql` có thể lấy lại từ source repo nếu cần. Source repo `D:\git\SunGrp_VSVN_API` không bị đụng tới. Runbook này không ghi file nào trong repo; chạy lại `git -C D:\git\SunGrp_VSVN status --short -- services/data-serving-service sql/postgres` và output phải giống baseline.

Forward recovery theo `architecture.md`: áp dụng lại các mục 4.x theo thứ tự, rồi chạy lại runbook này từ Bước 1 trên volume sạch. Fabric và PostgreSQL ở DEV hay production không bị ảnh hưởng.

Khi FAIL:

- Ghi dòng lỗi đầu tiên.
- Chạy `docker compose down -v` để dọn.
- Báo lại cho Main để mở task điều tra.
- Không sửa DDL `sql/postgres/gld_srv_serve.pg.sql` trong task này. Theo `architecture.md`, việc đổi cột phải đi qua một data task riêng.

## Kết quả người dùng ghi nhận

Không ghi dữ liệu cá nhân, giá trị credential, host DEV hay production. Mẫu kết quả không quá 50 dòng.

Người chạy: Main (agent), được người dùng cho phép trong lượt ngày 2026-11-06 ("Accept tự chạy runbook"). Credential là giá trị ngẫu nhiên chỉ tồn tại trong phiên shell, không in ra, không ghi file, đã xóa khi dọn.

- Ngày chạy: `2026-11-06`
- Docker Server version / `docker compose version`: `29.7.2` / `5.5.0`
- `java -version` trong container: `openjdk 26.0.2.1 (Temurin-26.0.2.1+1)`
- `POSTGRES_PORT` dùng (mặc định `55432`): `55432`
- `.env` có tồn tại (True/False): `False`

| # | Kiểm tra | PASS/FAIL | Ghi chú (mã HTTP, số phần tử) |
|---|---|---|---|
| 0 | `/actuator/health` = `UP` | PASS | `UP`; app start 8.4 s |
| 2 | DDL nạp 5 bảng, không có `flyway_schema_history` | PASS | `BEGIN`, 5 `CREATE TABLE`, `COMMIT`, exit 0; `to_regclass` = `t` |
| 3 | Seed synthetic (media cùng `media_id` khác `poi_id`) | PASS | exit 0; info 2, multi_lang 2, media 2, review 2, amenity 1 |
| 4.1 | compact `ids=poi1,poi2&lang=vi` | PASS | 200; 2 phần tử, poi2 trước poi1; cover `ct4-smoke-media-0001` đúng file_key từng POI; total_items 2 |
| 4.2a | gallery `poi1` | PASS | 200; 1 phần tử, file_key `…-poi1.jpg`, 800x600, image/jpeg, display_order 1 |
| 4.2b | gallery `poi2` (cùng `media_id`) | PASS | 200; 1 phần tử, cùng id, file_key `…-poi2.jpg` |
| 4.3 | reviews `poi1` (không có `source_name`) | PASS | 200; review-0002 rồi review-0001; khóa `author_name,rating,review_date,review_id,review_text`; rating 4.0 / 4.5 |
| 4.4 | amenities `poi1` `lang=vi` | PASS | 200; 1 nhóm `FACILITY`, `amenity_vi` = `Tiện nghi cơ sở`; item `smoke_wifi` / `Wifi thu nghiem`, service_flags null |
| 4.5 | reviews POI không tồn tại → 404 `POI_NOT_FOUND` | PASS | 404; success false, code 404, data null, error_code `POI_NOT_FOUND`, message đúng |
| 4.6 | OpenAPI `servers` chỉ có Local | PASS | 1 server: `http://localhost:8080` / `Local` |
| R1 | Gọi lại GET, `data` giống nhau | PASS | 5/5 endpoint `True`; 404 lặp lại vẫn 404 |
| R2 | Chạy lại DDL lỗi "already exists", số dòng không đổi | PASS | `relation "srv_poi_info" already exists`, exit 3; số dòng không đổi |
| L | Log không có `ERROR` và `flyway` | PASS | `Tomcat started on port 8080`; ERROR 0 dòng, flyway 0 dòng |
| C | `docker compose down -v` đã dọn xong | PASS | không còn container/volume; file tạm và biến env đã xóa; `git status` giống baseline (`?? services/data-serving-service/`); image `data-serving-service:latest` được giữ lại |

- Kết luận chung (PASS/FAIL): `PASS`
- Dòng lỗi đầu tiên nếu có (không có credential): `Không có`
