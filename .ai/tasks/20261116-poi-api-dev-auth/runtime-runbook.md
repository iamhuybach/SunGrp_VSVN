# Hướng dẫn kiểm chứng runtime

Trạng thái: `ĐÃ CHẠY`

## Phạm vi và môi trường

PowerShell, thư mục `services/data-serving-service`. Compose local: PostgreSQL và `data-serving-service` trên cổng `8080`. Không chạy `docker compose config`, vì lệnh đó in token.

## Điều kiện tiên quyết

- `.env` cạnh `docker-compose.yml` có `POSTGRES_USER`, `POSTGRES_PASSWORD`, và `POI_API_BEARER_TOKEN`.
- Schema `apps` và DDL serving đã áp một lần (xem `services/data-serving-service/AGENTS.md`).
- Không dán output có chứa giá trị token. Chỉ ghi status code và lý do log.

## Baseline trước khi chạy

Không có baseline dữ liệu. POI `smoke-poi` không cần tồn tại: amenities trả `data` rỗng khi không có dòng.

## Các bước thực hiện

1. `docker compose up -d --build`
2. `docker compose exec data-serving-service sh -c 'test -n "$POI_API_BEARER_TOKEN" && echo token=set || echo token=EMPTY'`
3. `$t = ((Select-String -Path .env -Pattern '^POI_API_BEARER_TOKEN=(.*)$').Matches[0].Groups[1].Value).Trim()`
4. `curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:8080/actuator/health`
5. `curl.exe -s -i http://localhost:8080/api/v1/pois/smoke-poi/amenities`
6. `curl.exe -s -i -H "Authorization: Bearer wrong-token" http://localhost:8080/api/v1/pois/smoke-poi/amenities`
7. `curl.exe -s -i -H "Authorization: Bearer $t" http://localhost:8080/api/v1/pois/smoke-poi/amenities`
8. `docker compose logs data-serving-service | Select-String poi_api_auth_rejected`

## Kiểm tra kết quả

- Bước 2: `token=set`.
- Bước 4: `200`.
- Bước 5: HTTP `401`, header `WWW-Authenticate: Bearer`, body có `"success":false`, `"code":401`, `"error_code":"ERR_UNAUTHORIZED"`.
- Bước 6: HTTP `401`, cùng envelope.
- Bước 7: HTTP `200`, `"success":true`, `"data":[]`.
- Bước 8: hai dòng, `MISSING_HEADER` và `TOKEN_MISMATCH`. Không dòng nào chứa token.

## Chạy lại để kiểm tra idempotency

Không áp dụng. Mỗi request được kiểm tra riêng. Không có watermark hay commit.

## Kiểm tra log và watermark

Xem bước 8. Không có watermark.

## Rollback và forward recovery

- Rollback: revert thay đổi. Endpoint mở lại. Biến môi trường còn lại không làm hỏng bản cũ.
- Forward recovery: token sai hoặc trống thì sửa giá trị và restart. Token lộ thì sinh giá trị mới, cập nhật `.env` hoặc môi trường deploy và caller, rồi restart. Caller giữ token cũ nhận 401 cho đến khi đổi, vì chỉ có một token.

## Kết quả người dùng ghi nhận

- 2026-11-16, Main chạy smoke trong `services/data-serving-service` theo yêu cầu. `docker compose up -d --build` exit 0. Postgres healthy, service started.
- Bước 2: `token=set`.
- Bước 4: `GET /actuator/health` HTTP 200, `status=UP`. Không token.
- Bước 5: HTTP 401, `WWW-Authenticate: Bearer`, `success=false`, `code=401`, `error_code=ERR_UNAUTHORIZED`, `data=null`. Body không chứa token.
- Bước 6: HTTP 401, cùng envelope. Body không chứa token.
- Bước 7: HTTP 200, `success=true`, `data=[]`. Body không chứa token. Không cần áp DDL lần này.
- Bước 8: hai dòng `poi_api_auth_rejected`, lý do `MISSING_HEADER` và `TOKEN_MISMATCH`. Token không có trong hai dòng đó và không có trong toàn bộ log container.
