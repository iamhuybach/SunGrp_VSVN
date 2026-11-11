# Kịch bản kiểm tra API POI trên Dev

`.env` của `services/data-serving-service` là kết nối Postgres Dev. API HTTP vẫn chạy trên máy này. Cổng `8080` là compose local, không đọc `.env`.

Chạy một lần, trong PowerShell, rồi để cửa sổ đó mở:

```powershell
Set-Location d:\git\SunGrp_VSVN\services\data-serving-service
Get-Content .env | ForEach-Object {
  $line = $_.Trim()
  if ($line -match '^\s*([A-Za-z0-9_]+)\s*=\s*"(.*)"\s*$') {
    Set-Item -Path "Env:$($Matches[1])" -Value $Matches[2]
  }
}
$env:SERVER_PORT = '18081'
.\mvnw.cmd -q -B spring-boot:run
```

Đợi log `Started DataServingApplication`. Base URL của mọi cURL: `http://localhost:18081`.

Trong Postman: **Import → Raw text**, dán một ô cột cURL. Chạy dòng 6 trước. Lấy `data[0].id` và `data[1].id`, thay vào body dòng 1 nếu hai id dưới đây không còn trong kết quả features.

| Stt | Kịch bản | Kỳ vọng | cURL Postman |
|---|---|---|---|
| 1 | Compact hai POI Dev | HTTP 200. Không có `meta.pagination`. Không có `business_sector_label`. `cover` null hoặc chỉ có `id` và `file_key`. | `curl --location 'http://localhost:18081/api/v1/pois/compact' --header 'Content-Type: application/json' --header 'Accept-Language: vi' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222' --data '{"lang":"vi","ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a","013cbb79-4407-b2fb-e4f4-67b78d2ff69e"]}'` |
| 2 | Compact thiếu lang và Accept-Language | HTTP 200. Mô tả lấy tiếng Việt. | `curl --location 'http://localhost:18081/api/v1/pois/compact' --header 'Content-Type: application/json' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222' --data '{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}'` |
| 3 | Compact body rỗng | HTTP 422. `meta.error_code` = `ERR_VALIDATION_FAILED`. | `curl --location 'http://localhost:18081/api/v1/pois/compact' --header 'Content-Type: application/json' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222' --data '{}'` |
| 4 | Compact JSON hỏng | HTTP 400. Message `Malformed or missing request body.` | `curl --location 'http://localhost:18081/api/v1/pois/compact' --header 'Content-Type: application/json' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222' --data '{'` |
| 5 | GET compact | HTTP 405. | `curl --location 'http://localhost:18081/api/v1/pois/compact' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222'` |
| 6 | Features | HTTP 200. Có `meta.pagination` với `type`, `page`, `per_page`, `total_items`, `total_pages`, `has_next`, `has_prev`. `cover` null hoặc chỉ có `id` và `file_key`. | `curl --location 'http://localhost:18081/api/v1/pois/features?page=0&size=10' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222'` |
| 7 | Features size quá 100 | HTTP 422. `meta.error_code` = `ERR_VALIDATION_FAILED`. | `curl --location 'http://localhost:18081/api/v1/pois/features?size=101' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222'` |
| 8 | Gallery | HTTP 200. `data` rỗng hoặc mỗi phần tử chỉ có `id`, `file_key`, `display_order`. | `curl --location 'http://localhost:18081/api/v1/pois/14b2e2c4-95a8-d851-240f-c25e4e8cdb7a/gallery?page=0&size=20' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222'` |
| 9 | Gallery POI không có | HTTP 200. `data` = `[]`. `total_items` = 0. | `curl --location 'http://localhost:18081/api/v1/pois/00000000-0000-0000-0000-000000000000/gallery' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222'` |
| 10 | Reviews | HTTP 200. `rating_summary` là `[]`, hoặc một phần tử có `rating_count` và `rating_avg_score`. | `curl --location 'http://localhost:18081/api/v1/pois/14b2e2c4-95a8-d851-240f-c25e4e8cdb7a/reviews?page=0&size=10' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222'` |
| 11 | Reviews POI không có | HTTP 200. `data` và `rating_summary` đều `[]`. | `curl --location 'http://localhost:18081/api/v1/pois/00000000-0000-0000-0000-000000000000/reviews' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222'` |
| 12 | Experiences | HTTP 200. `data.items` rỗng, hoặc mỗi item có `title`, `description`, `source`. | `curl --location 'http://localhost:18081/api/v1/pois/14b2e2c4-95a8-d851-240f-c25e4e8cdb7a/experiences?lang=vi' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222'` |
| 13 | Practical info | HTTP 200. `holiday_exceptions` là `null` hoặc một giá trị JSON. Có dữ liệu thì khóa bên trong giữ nguyên. | `curl --location 'http://localhost:18081/api/v1/pois/14b2e2c4-95a8-d851-240f-c25e4e8cdb7a/practical_info?lang=vi' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222'` |
| 14 | Practical info POI không có | HTTP 404. `meta.error_code` = `POI_NOT_FOUND`. | `curl --location 'http://localhost:18081/api/v1/pois/00000000-0000-0000-0000-000000000000/practical_info' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222'` |
| 15 | Amenities | HTTP 200. | `curl --location 'http://localhost:18081/api/v1/pois/14b2e2c4-95a8-d851-240f-c25e4e8cdb7a/amenities' --header 'X-Request-Id: 22222222-2222-2222-2222-222222222222'` |
