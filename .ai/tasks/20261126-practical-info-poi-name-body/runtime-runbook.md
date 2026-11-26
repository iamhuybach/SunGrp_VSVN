# Runtime runbook: 20261126-practical-info-poi-name-body

## Phạm vi và môi trường

- Task: `20261126-practical-info-poi-name-body`. Thay đổi chỉ nằm ở Serving API. `poi_name` của `POST /api/v1/pois/practical_info` được chuyển từ query param vào JSON body, cùng cấp với `ids` (`@JsonProperty("poi_name") @Size(max = 128)`). Server không còn đọc query `poi_name` nữa (I3).
- Task này không có notebook, pipeline, ctrl table hay watermark nào, nên không có parameter cell và cũng không có pipeline JSON để đọc.
- Thư mục làm việc: `services/data-serving-service`. Mọi lệnh `docker compose` đều chạy từ thư mục này.
- Môi trường: Docker local trên máy người dùng, dùng `docker-compose.yml` của service.
  - Service DB: `postgres` (container `data-serving-postgres`), database `vv_data_serving`, cổng host `${POSTGRES_PORT:-55432}`.
  - Service API: `data-serving-service` (container `data-serving-service`), `http://localhost:8080`, kết nối `currentSchema=apps`.
- Dữ liệu: chỉ dùng một dòng tổng hợp (synthetic) `poi_id = 'poi-practical-name-1'`, `poi_name = 'French Village Sample'`. Không có số điện thoại, email hay tên người thật.
- Các lệnh `curl` và `grep` bên dưới viết theo cú pháp bash. Trên Windows, hãy chạy chúng trong Git Bash hoặc WSL. Riêng các lệnh `docker compose` chạy được ở cả PowerShell lẫn bash.
- Runbook không ghi token, password hay host nội bộ nào. Đừng dùng `curl -v` vì nó in header `Authorization` ra màn hình.

## Điều kiện tiên quyết

1. Code của task đã nằm trong working tree (DTO, controller, Javadoc của filter, test, mapping doc) và bộ test đã pass theo architecture: `mvnw.cmd -q -B test` trong `services/data-serving-service`.
2. Docker Desktop đang chạy.
3. Trong session shell đã set ba biến môi trường sau. Không in giá trị của chúng ra:
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POI_API_BEARER_TOKEN`
   
   Để kiểm tra mà không lộ giá trị (bash), chạy lệnh sau. Mỗi biến phải in ra `set`:
   ```bash
   for v in POSTGRES_USER POSTGRES_PASSWORD POI_API_BEARER_TOKEN; do if [ -n "${!v}" ]; then echo "$v set"; else echo "$v MISSING"; fi; done
   ```
4. Có `python` trên PATH để sinh body cho bước 5 và bước 6. Lệnh này chỉ ghi file vào `/tmp` và không đọc dữ liệu ngoài.
5. Cổng `8080` và `${POSTGRES_PORT:-55432}` trên host phải đang trống.
6. Bước rollback dùng `docker compose down -v`, lệnh này xóa volume `postgres_data`. Hãy chắc chắn volume này chỉ chứa dữ liệu thử nghiệm local: <CẦN NGƯỜI DÙNG CUNG CẤP: xác nhận volume postgres_data local không chứa dữ liệu cần giữ>.

## Baseline trước khi chạy

Các lệnh dưới đây đều chỉ đọc, không ghi gì.

1. Ghi lại commit và trạng thái working tree:
   ```bash
   git rev-parse --short HEAD
   git status --short
   ```
2. Trạng thái container. Nếu stack chưa chạy thì kết quả rỗng:
   ```bash
   docker compose ps
   ```
3. Nếu stack đã chạy từ trước, kiểm tra xem dòng synthetic đã tồn tại chưa. Kỳ vọng `0`. Nếu ra `1` thì bỏ qua lệnh INSERT ở bước thực hiện.
   ```bash
   docker compose exec -T postgres psql -U "$POSTGRES_USER" -d vv_data_serving -c "SELECT count(*) FROM apps.srv_poi_info WHERE poi_id = 'poi-practical-name-1';"
   ```
   Nếu schema hoặc bảng chưa tồn tại, lệnh sẽ báo lỗi `relation ... does not exist`. Đây là kết quả bình thường trên một volume mới.

## Các bước thực hiện

Từ bước A1 đến A4 là chuẩn bị môi trường, và chỉ ở các bước này mới có thao tác ghi. Từ B1 đến B7 là các probe API.

A1. Build và khởi động stack:
```bash
cd services/data-serving-service
docker compose up -d --build
docker compose ps
```

A2. Tạo schema:
```bash
docker compose exec -T postgres psql -U "$POSTGRES_USER" -d vv_data_serving -c "CREATE SCHEMA IF NOT EXISTS apps"
```

A3. Chạy DDL:
```bash
docker compose cp ../../sql/postgres/gld_srv_serve.pg.sql postgres:/tmp/gld_srv_serve.pg.sql
docker compose exec -T postgres psql -U "$POSTGRES_USER" -d vv_data_serving -v ON_ERROR_STOP=1 -f /tmp/gld_srv_serve.pg.sql
```

A4. Chèn dòng synthetic. Chỉ chạy một lần, và bỏ qua bước này nếu baseline bước 3 đã ra `1`:
```bash
docker compose exec -T postgres psql -U "$POSTGRES_USER" -d vv_data_serving -c "INSERT INTO apps.srv_poi_info (poi_id, poi_name) VALUES ('poi-practical-name-1', 'French Village Sample');"
```
Kiểm tra lại (chỉ đọc), kỳ vọng `1`:
```bash
docker compose exec -T postgres psql -U "$POSTGRES_USER" -d vv_data_serving -c "SELECT poi_id, poi_name, deleted_at FROM apps.srv_poi_info WHERE poi_id = 'poi-practical-name-1' LIMIT 50;"
```

Các probe API dùng chung biến sau. Biến này không in token ra:
```bash
API=http://localhost:8080
AUTH="Authorization: Bearer $POI_API_BEARER_TOKEN"
CT="Content-Type: application/json"
FMT='\nHTTP %{http_code}\n'
```

B1. Health:
```bash
curl -s -w "$FMT" "$API/actuator/health"
```

B2. Body `poi_name` khớp tên:
```bash
curl -s -w "$FMT" -X POST "$API/api/v1/pois/practical_info" -H "$AUTH" -H "$CT" \
  --data-binary '{"ids":["poi-practical-name-1"],"poi_name":"French Village"}'
```

B3. Body `poi_name` không khớp tên:
```bash
curl -s -w "$FMT" -X POST "$API/api/v1/pois/practical_info" -H "$AUTH" -H "$CT" \
  --data-binary '{"ids":["poi-practical-name-1"],"poi_name":"ZZZ-NO-MATCH"}'
```

B4. Gửi query `poi_name` không khớp và không có `poi_name` trong body. Kỳ vọng query bị bỏ qua:
```bash
curl -s -w "$FMT" -X POST "$API/api/v1/pois/practical_info?poi_name=ZZZ-NO-MATCH" -H "$AUTH" -H "$CT" \
  --data-binary '{"ids":["poi-practical-name-1"]}'
```

B5. Body `poi_name` dài 129 ký tự `x`:
```bash
python -c "import json;print(json.dumps({'ids':['poi-practical-name-1'],'poi_name':'x'*129}))" > /tmp/pi_body_129.json
curl -s -w "$FMT" -X POST "$API/api/v1/pois/practical_info" -H "$AUTH" -H "$CT" \
  --data-binary @/tmp/pi_body_129.json
```

B6. Body thô dài hơn `98304` byte (`PracticalInfoBodyLimitFilter.MAX_BYTES = 96 * 1024`):
```bash
python -c "import sys;sys.stdout.write('{\"ids\":[\"'+'a'*100000+'\"]}')" > /tmp/pi_body_big.json
wc -c /tmp/pi_body_big.json
curl -s -w "$FMT" -X POST "$API/api/v1/pois/practical_info" -H "$AUTH" -H "$CT" \
  --data-binary @/tmp/pi_body_big.json
```
`wc -c` phải lớn hơn `98304`.

B7. GET practical_info không thay đổi:
```bash
curl -s -w "$FMT" "$API/api/v1/pois/poi-practical-name-1/practical_info" -H "$AUTH"
```

## Kiểm tra kết quả

| Bước | Kỳ vọng |
|---|---|
| A2–A3 | Không có lỗi. Riêng A3 không dừng vì `ON_ERROR_STOP`. |
| A4 | `INSERT 0 1`. SELECT trả về 1 dòng `poi-practical-name-1 | French Village Sample | (null)`. |
| B1 | `HTTP 200`, body có `"status":"UP"`. |
| B2 | `HTTP 200`, `data` có đúng 1 phần tử, `meta.pagination.total_items` = `1`. |
| B3 | `HTTP 200`, `data` = `[]`, `meta.pagination.total_items` = `0`. |
| B4 | `HTTP 200`, `data` có 1 phần tử. Kết quả này chứng minh query `poi_name` không lọc (I3). |
| B5 | `HTTP 422`, `meta.error_code` = `ERR_VALIDATION_FAILED` (I4). |
| B6 | `HTTP 400`, `meta.error_code` = `ERR_BODY_TOO_LARGE` (I8). |
| B7 | `HTTP 200`, `data.id` = `poi-practical-name-1`, `data.name` = `French Village Sample` (I10). |

Nếu có bất kỳ bước nào lệch kỳ vọng thì dừng lại và dán output đã làm sạch vào phần `Kết quả người dùng ghi nhận`. Không sửa kỳ vọng cho khớp với kết quả.

Nếu B1 không trả `UP` vì service khởi động trước khi DDL chạy xong, hãy chạy `docker compose restart data-serving-service`, chờ service lên rồi chạy lại B1. Ghi việc này vào phần kết quả.

## Chạy lại để kiểm tra idempotency

- Chạy lại nguyên lệnh B2, không đổi gì. Không chạy lại A4, vì việc chèn trùng `poi_id` không nằm trong phép thử này.
- Kỳ vọng kết quả giống hệt lần đầu: `HTTP 200`, `data` có 1 phần tử, `meta.pagination.total_items` = `1`.
- Đây là API chỉ đọc nên lần chạy lại không làm thay đổi dữ liệu. Có thể xác nhận bằng lệnh chỉ đọc sau, kỳ vọng vẫn là `1`:
  ```bash
  docker compose exec -T postgres psql -U "$POSTGRES_USER" -d vv_data_serving -c "SELECT count(*) FROM apps.srv_poi_info WHERE poi_id = 'poi-practical-name-1';"
  ```

## Kiểm tra log và watermark

- Watermark: không áp dụng, vì task này không có ctrl table hay watermark.
- Log: kiểm tra rằng log không chứa token hay giá trị `poi_name`. Các lệnh dưới chỉ in số dòng khớp, không in nội dung:
  ```bash
  docker compose logs --no-color data-serving-service > /tmp/pi_service.log
  grep -c -F "$POI_API_BEARER_TOKEN" /tmp/pi_service.log
  grep -c -F "French Village" /tmp/pi_service.log
  grep -c -F "ZZZ-NO-MATCH" /tmp/pi_service.log
  grep -c "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" /tmp/pi_service.log
  ```
  Cả bốn lệnh đều phải in ra `0`. Lệnh cuối tìm chuỗi 128 ký tự `x`.
- Nếu một lệnh in ra số khác `0`, đừng dán dòng log đó, vì nó có thể chứa secret. Chỉ ghi số đếm và tên logger hoặc class (đã làm sạch), rồi dừng để xử lý.
- Sau khi kiểm tra xong, xóa file tạm: `rm -f /tmp/pi_service.log /tmp/pi_body_129.json /tmp/pi_body_big.json`.

## Rollback và forward recovery

Rollback môi trường runtime local:
```bash
docker compose down -v
```
Lệnh này dừng container và xóa volume `postgres_data`, kéo theo cả dòng synthetic. Chỉ chạy khi đã xác nhận ở phần Điều kiện tiên quyết, mục 6.

Rollback code, theo architecture:
- Revert controller, DTO, Javadoc của filter, test và mapping doc. Task không có migration dữ liệu nên revert có hiệu lực ngay.
- Sau rollback, client nào đã gửi `poi_name` trong body sẽ mất bộ lọc tên, vì server cũ bỏ qua property lạ trong body. Bộ lọc chỉ hoạt động lại khi client gửi lại query param. Rủi ro này đối xứng với rủi ro khi triển khai tới.
- Commit hoặc branch cần revert: <CẦN NGƯỜI DÙNG CUNG CẤP: commit SHA của thay đổi task này sau khi commit>.

Forward recovery cho môi trường local: chạy lại theo thứ tự A1 (`docker compose up -d --build`), A2 (schema), A3 (DDL) rồi A4 (cùng lệnh INSERT), sau đó chạy lại B1 đến B7.

Forward recovery về hợp đồng API: nếu có consumer không chuyển được `poi_name` sang body, cách xử lý là ghi option B thành một quyết định mới trong ledger, không vá tạm.

## Kết quả người dùng ghi nhận

Main chạy local ngày 2026-11-26 theo yêu cầu. Không có dữ liệu cá nhân, token, password hay host. `docker compose down -v` không chạy. Stack vẫn đang chạy.

- Commit (`git rev-parse --short HEAD`): `2e19e39`. Thay đổi của task chưa commit.
- Thời điểm chạy: 2026-11-26, khoảng 11:14 ICT.

| Bước | HTTP / kết quả | `meta.error_code` / `total_items` / ghi chú |
|---|---|---|
| A1 | image rebuilt, service started | postgres đã healthy sẵn |
| A2 | CREATE SCHEMA | schema `apps` đã có |
| A3 | bỏ qua | `apps.srv_poi_info` đã tồn tại, không chạy lại DDL |
| A4 | INSERT 0 1 | `poi-practical-name-1`, `French Village Sample`, `deleted_at` null |
| B1 | HTTP 200 | `status` = `UP` |
| B2 | HTTP 200 | `total_items` = 1, `data` 1 phần tử, `id` = `poi-practical-name-1` |
| B3 | HTTP 200 | `total_items` = 0, `data` rỗng |
| B4 | HTTP 200 | `total_items` = 1. Query `poi_name=ZZZ-NO-MATCH` không lọc |
| B5 | HTTP 422 | `ERR_VALIDATION_FAILED` |
| B6 | HTTP 400 | body 100012 byte, `ERR_BODY_TOO_LARGE` |
| B7 | HTTP 200 | `data.id` = `poi-practical-name-1`, `data.name` = `French Village Sample` |
| Chạy lại B2 | HTTP 200 | `total_items` = 1. `count(*)` vẫn 1 |
| Log grep (token / French Village / ZZZ-NO-MATCH / 128x) | 0 / 0 / 0 / 0 | |
| Rollback `down -v` | không chạy | |

Output thô đã làm sạch (≤ 50 dòng):
```
A4 INSERT 0 1
B1 http=200 status=UP
B2 http=200 total_items=1 data_len=1
B3 http=200 total_items=0 data_len=0
B4 http=200 total_items=1 data_len=1
B5 http=422 ERR_VALIDATION_FAILED
B6 http=400 ERR_BODY_TOO_LARGE bytes=100012
B7 http=200 id=poi-practical-name-1
B2-rerun http=200 total_items=1 row_count=1
log_token=0 log_french=0 log_zzz=0 log_x128=0
```
