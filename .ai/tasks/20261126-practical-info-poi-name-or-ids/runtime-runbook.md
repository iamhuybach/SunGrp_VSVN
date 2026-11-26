# Runtime runbook: 20261126-practical-info-poi-name-or-ids

## Phạm vi và môi trường

Runbook này kiểm tra trên runtime Docker cục bộ hợp đồng mới của `POST /api/v1/pois/practical_info`. Body chọn POI theo `ids`, theo `poi_name`, hoặc cả hai. Khi có cả hai thì lấy hợp hai tập, không lấy giao. Thiếu cả hai selector thì trả 422 `ERR_VALIDATION_FAILED`. Runbook cũng ghi baseline độ trễ và `EXPLAIN (ANALYZE, BUFFERS)` cho truy vấn chỉ theo tên và truy vấn hợp (architecture.md, `## Observability`).

- Chỉ đụng tới Serving API. Task không có notebook, pipeline, ctrl table hay watermark.
- Thư mục làm việc: `services/data-serving-service`. Mọi lệnh bên dưới chạy trong PowerShell từ thư mục này.
- Compose (`docker-compose.yml`): service `postgres` (container `data-serving-postgres`, image `postgres:18-alpine`) và service `data-serving-service` (container `data-serving-service`).
- API: `http://localhost:8080`. Endpoint: `/api/v1/pois/practical_info`. Health: `/actuator/health`.
- PostgreSQL publish ra cổng host `${POSTGRES_PORT:-55432}`. Runbook này chỉ dùng `psql` bên trong container, nên không cần host hay cổng.
- Database `vv_data_serving`, schema `apps`, DDL `../../sql/postgres/gld_srv_serve.pg.sql`.
- Chỉ dùng dữ liệu tổng hợp: `poi-name-cafe` (`Sample Cafe`) và `poi-name-tea` (`Tea House`).
- Không in, không dán ra ngoài giá trị của `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POI_API_BEARER_TOKEN`. Không ghi host hay token vào kết quả.
- Không có schema change và không có index change (architecture.md, `### Decision`).

## Điều kiện tiên quyết

1. Docker daemon đang chạy, có `docker compose`.
2. Working tree đã chứa bản sửa của task. Test module đã PASS (architecture.md, `### Order and stop points` bước 5): `mvnw.cmd -q -B test`.
3. Ba biến môi trường đã đặt trong session PowerShell, hoặc trong `.env` đã được ignore. Kiểm tra là đã đặt, không in giá trị:

```powershell
foreach ($n in 'POSTGRES_USER','POSTGRES_PASSWORD','POI_API_BEARER_TOKEN') {
  "{0} set={1}" -f $n, (-not [string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable($n)))
}
```

Kết quả mong đợi là cả ba dòng `set=True`. Nếu `POI_API_BEARER_TOKEN` rỗng thì mọi lời gọi POI trả 401 (AGENTS.md).

4. Dùng `curl.exe` (không dùng alias `curl` của PowerShell). Nạp hàm trợ giúp dưới đây vào session. Hàm chỉ in status, `total_items`, danh sách `data[].id` và `meta.error_code`, không in token hay toàn bộ body:

```powershell
function Invoke-PracticalInfo([string]$Query, [string]$Body) {
  $lines = $Body | curl.exe -s -w "`n%{http_code}" -X POST "http://localhost:8080/api/v1/pois/practical_info$Query" `
    -H "Authorization: Bearer $env:POI_API_BEARER_TOKEN" -H "Content-Type: application/json" --data-binary '@-'
  $status = $lines[-1]
  $json = ($lines[0..($lines.Count-2)] -join "`n") | ConvertFrom-Json
  [pscustomobject]@{
    status      = $status
    total_items = $json.meta.pagination.total_items
    ids         = (@($json.data | ForEach-Object { $_.id }) -join ',')
    error_code  = $json.meta.error_code
  }
}
```

5. Hàm chạy SQL trong container postgres. `$POSTGRES_USER` được shell trong container đọc, không qua dòng lệnh của host:

```powershell
function Invoke-Psql([string]$Sql) {
  $Sql | docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d vv_data_serving -v ON_ERROR_STOP=1 -X'
}
```

## Baseline trước khi chạy

Mọi truy vấn ở mục này chỉ đọc.

1. Trạng thái container:

```powershell
docker compose ps
```

Nếu stack chưa chạy thì sang bước 1 của `Các bước thực hiện` trước, rồi quay lại làm baseline từ bước 2.

2. Kiểm tra bảng đã có hay chưa:

```powershell
Invoke-Psql "SELECT to_regclass('apps.srv_poi_info') AS srv_poi_info, to_regclass('apps.srv_poi_legacy_id_map') AS srv_poi_legacy_id_map;"
```

Ghi lại kết quả. Nếu `srv_poi_info` khác null thì không chạy lại DDL. Nếu `srv_poi_info` có mà `srv_poi_legacy_id_map` null thì DB được tạo trước task `20261125-practical-info-query-legacy-poi-id`. Khi đó dừng lại và làm theo chú thích dòng 24 của DDL (chạy tay đúng khối `CREATE TABLE apps.srv_poi_legacy_id_map`). Bước này cần người dùng xác nhận, nằm ngoài runbook.

3. Dòng tổng hợp đã tồn tại hay chưa, và dữ liệu khác có làm lệch số đếm mong đợi không (chỉ đếm, không in tên):

```powershell
Invoke-Psql @"
SELECT count(*) AS synthetic_rows FROM apps.srv_poi_info WHERE poi_id IN ('poi-name-cafe','poi-name-tea');
SELECT count(*) AS other_cafe_rows FROM apps.srv_poi_info
 WHERE deleted_at IS NULL AND lower(poi_name) LIKE lower('%Cafe%') ESCAPE '!' AND poi_id <> 'poi-name-cafe';
SELECT count(*) AS other_tea_rows FROM apps.srv_poi_info
 WHERE deleted_at IS NULL AND lower(poi_name) LIKE lower('%Tea%') ESCAPE '!' AND poi_id NOT IN ('poi-name-cafe','poi-name-tea');
SELECT count(*) AS legacy_map_hits FROM apps.srv_poi_legacy_id_map WHERE legacy_poi_id IN ('poi-name-cafe','poi-name-tea');
SELECT count(*) AS total_info_rows FROM apps.srv_poi_info;
"@
```

Kết quả mong đợi để các số đếm ở mục `Kiểm tra kết quả` đúng như viết: `other_cafe_rows = 0` và `legacy_map_hits = 0`. Nếu `other_cafe_rows > 0` thì `total_items` ở bước 2, 4 và 7 sẽ lớn hơn số ghi trong runbook. Khi đó ghi lại con số và báo người dùng; không xoá dữ liệu có sẵn. `total_info_rows` dùng để đọc kết quả EXPLAIN, vì truy vấn theo tên quét toàn bảng. `synthetic_rows` là 0 thì bước insert sẽ chạy, là 2 thì bỏ qua insert.

4. Ghi thời điểm bắt đầu để lọc log sau này:

```powershell
$RunStart = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'); $RunStart
```

## Các bước thực hiện

1. Build và khởi động stack:

```powershell
docker compose up -d --build
docker compose ps
```

Chờ `data-serving-postgres` ở trạng thái `healthy` và `data-serving-service` ở trạng thái `running`.

2. Tạo schema. Lệnh idempotent:

```powershell
Invoke-Psql "CREATE SCHEMA IF NOT EXISTS apps;"
```

3. DDL: chỉ chạy khi bước 2 của baseline cho `srv_poi_info` null. Nếu bảng đã có thì bỏ qua bước này và ghi "đã bỏ qua DDL":

```powershell
Get-Content -Raw ..\..\sql\postgres\gld_srv_serve.pg.sql | docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d vv_data_serving -v ON_ERROR_STOP=1 -X'
```

4. Nạp dữ liệu tổng hợp. Chỉ chạy khi `synthetic_rows = 0`. Nếu bằng 2 thì bỏ qua, vì chạy lại sẽ lỗi khoá chính:

```powershell
Invoke-Psql "INSERT INTO apps.srv_poi_info (poi_id, poi_name) VALUES ('poi-name-cafe', 'Sample Cafe'), ('poi-name-tea', 'Tea House');"
```

Kết quả mong đợi: `INSERT 0 2`.

5. Đo baseline độ trễ ở tầng DB. Lệnh chỉ đọc vì là `SELECT`. Cắt còn tối đa 50 dòng:

```powershell
Invoke-Psql @"
EXPLAIN (ANALYZE, BUFFERS)
SELECT i.poi_id FROM apps.srv_poi_info i
 WHERE lower(i.poi_name) LIKE lower('%Cafe%') ESCAPE '!';
"@ | Select-Object -First 50

Invoke-Psql @"
EXPLAIN (ANALYZE, BUFFERS)
SELECT i.poi_id FROM apps.srv_poi_info i WHERE i.poi_id = 'poi-name-tea'
UNION
SELECT i.poi_id FROM apps.srv_poi_info i WHERE lower(i.poi_name) LIKE lower('%Cafe%') ESCAPE '!';
"@ | Select-Object -First 50
```

Với mỗi plan, ghi `Planning Time`, `Execution Time`, và plan có node `Seq Scan on srv_poi_info` hay không. Với truy vấn theo tên thì `Seq Scan` là hành vi đã được chấp nhận (architecture.md, `### Decision`). Không có ngưỡng chặn; số liệu này làm baseline cho quyết định index `pg_trgm` sau này.

6. Đo độ trễ đầu-cuối qua API cho lời gọi chỉ theo tên và lời gọi hợp. Mỗi lời gọi chạy 5 lần, chỉ in thời gian:

```powershell
foreach ($b in '{"poi_name":"Cafe"}','{"ids":["poi-name-tea"],"poi_name":"Cafe"}') {
  $t = 1..5 | ForEach-Object {
    $b | curl.exe -s -o NUL -w "%{time_total}" -X POST "http://localhost:8080/api/v1/pois/practical_info" `
      -H "Authorization: Bearer $env:POI_API_BEARER_TOKEN" -H "Content-Type: application/json" --data-binary '@-'
  }
  "{0} time_total_s={1}" -f $b, ($t -join ',')
}
```

## Kiểm tra kết quả

Chạy lần lượt và so với giá trị mong đợi. Các số đếm giả định `other_cafe_rows = 0` ở baseline.

| # | Lệnh | Mong đợi |
|---|---|---|
| 1 | `curl.exe -s http://localhost:8080/actuator/health` | `"status":"UP"` |
| 2 | `Invoke-PracticalInfo '' '{"poi_name":"Cafe"}'` | status `200`, total_items `1`, ids `poi-name-cafe` |
| 3 | `Invoke-PracticalInfo '' '{"ids":["poi-name-tea"]}'` | status `200`, total_items `1`, ids `poi-name-tea` |
| 4 | `Invoke-PracticalInfo '' '{"ids":["poi-name-tea"],"poi_name":"Cafe"}'` | status `200`, total_items `2`, ids `poi-name-cafe,poi-name-tea` (sắp `poi_id` tăng dần) |
| 5 | `Invoke-PracticalInfo '' '{}'` | status `422`, error_code `ERR_VALIDATION_FAILED` |
| 6 | `Invoke-PracticalInfo '?poi_name=Tea' '{"ids":["poi-name-cafe"]}'` | status `200`, total_items `1`, ids `poi-name-cafe` (query `poi_name` không được đọc) |

Kiểm tra 4 chứng minh phép hợp: mỗi selector riêng lẻ chỉ cho một id, cả hai cho hai id. Với phép giao (AND) cũ thì kết quả sẽ là 0. Kiểm tra 6 chứng minh query `poi_name` bị bỏ qua. Nếu bất kỳ dòng nào lệch thì dừng lại, ghi output vào `Kết quả người dùng ghi nhận` và không sang bước review.

## Chạy lại để kiểm tra idempotency

API chỉ đọc. Lặp lại kiểm tra 2 rồi đếm lại dòng:

```powershell
Invoke-PracticalInfo '' '{"poi_name":"Cafe"}'
Invoke-Psql "SELECT count(*) AS synthetic_rows FROM apps.srv_poi_info WHERE poi_id IN ('poi-name-cafe','poi-name-tea');"
```

Mong đợi: status `200`, `total_items` `1` giống lần đầu, và `synthetic_rows = 2`. Không chạy lại bước insert.

## Kiểm tra log và watermark

Task không có watermark và không có ctrl table, nên không có gì để kiểm tra watermark.

Log không được chứa token hoặc chuỗi `Cafe`. Chỉ in số lần khớp, không in dòng khớp, vì dòng đó có thể chứa token:

```powershell
$svcLog = docker compose logs --no-color --since $RunStart data-serving-service 2>&1
"service token_hits={0}" -f @($svcLog | Select-String -SimpleMatch -Pattern $env:POI_API_BEARER_TOKEN).Count
"service cafe_hits={0}"  -f @($svcLog | Select-String -SimpleMatch -Pattern 'Cafe').Count
"service error_lines={0}" -f @($svcLog | Select-String -Pattern ' ERROR ').Count

$pgLog = docker compose logs --no-color --since $RunStart postgres 2>&1
"postgres token_hits={0}" -f @($pgLog | Select-String -SimpleMatch -Pattern $env:POI_API_BEARER_TOKEN).Count
"postgres cafe_hits={0}"  -f @($pgLog | Select-String -SimpleMatch -Pattern 'Cafe').Count
```

Mong đợi: `service token_hits=0`, `service cafe_hits=0`, `postgres token_hits=0`. `Select-String` mặc định không phân biệt hoa thường, nên cũng bắt cả `cafe`. Với log postgres, nếu `cafe_hits > 0` thì kiểm tra đó có phải do lệnh INSERT của runbook bị lỗi (PostgreSQL in câu lệnh lỗi vào log) hay không. Ghi rõ nguyên nhân, không dán dòng log. `service error_lines` cần bằng 0; nếu khác 0 thì ghi số lượng và mã lỗi, không ghi token hay giá trị body.

## Rollback và forward recovery

Rollback code (architecture.md, `## Rollback and forward recovery`): khôi phục các file trong phạm vi về bản trước. Đó là bản AND đang nằm trong working tree, hoặc `HEAD` nếu muốn về bản trước khi có `poi_name`. Không có dữ liệu hay schema nào cần hoàn tác. Đây là thao tác của người dùng; runbook không tự sửa file.

Rollback runtime cục bộ: chỉ chạy sau khi người dùng xác nhận rõ là được xoá volume cục bộ `postgres_data`. Lệnh xoá toàn bộ dữ liệu trong DB compose, kể cả dữ liệu không phải tổng hợp:

```powershell
docker compose down -v
```

Xác nhận của người dùng: `<CẦN NGƯỜI DÙNG CUNG CẤP: xác nhận volume postgres_data cục bộ được phép xoá>`.

Forward recovery runtime: chạy lại `docker compose up -d --build`, rồi `CREATE SCHEMA IF NOT EXISTS apps`, rồi DDL nếu `apps.srv_poi_info` chưa có, rồi đúng lệnh INSERT ở bước 4. Sau đó chạy lại toàn bộ mục `Kiểm tra kết quả`.

Forward recovery khi tìm theo tên chậm: thêm index GIN `pg_trgm` trên `lower(poi_name)`, do schema owner sở hữu, làm thành task riêng. Task này không làm việc đó.

## Kết quả người dùng ghi nhận

Main chạy local ngày 2026-11-26 theo yêu cầu. Không có token, host, mật khẩu hay dữ liệu cá nhân. `docker compose down -v` không chạy. Stack vẫn đang chạy.

- Ngày giờ chạy (UTC), `$RunStart`: `2026-11-26T06:21:35Z`
- Commit hoặc mô tả working tree: `2e19e39`. Thay đổi của task chưa commit.
- Kiểm tra biến môi trường (`set=True/False`): cả ba biến `set=True`. Không ghi giá trị.
- Baseline `to_regclass`: `apps.srv_poi_info` và `apps.srv_poi_legacy_id_map` đều có.
- Baseline `synthetic_rows`, `other_cafe_rows`, `other_tea_rows`, `legacy_map_hits`, `total_info_rows`: `0`, `0`, `0`, `0`, `6` trước khi insert.
- DDL đã chạy hay đã bỏ qua: đã bỏ qua vì bảng đã có.
- Insert: `INSERT 0 2`.
- EXPLAIN chỉ theo tên: Planning Time `0.682 ms`, Execution Time `0.028 ms`, có `Seq Scan on srv_poi_info`.
- EXPLAIN truy vấn hợp: Planning Time `1.038 ms`, Execution Time `0.233 ms`, có `Seq Scan on srv_poi_info`.
- `time_total_s` chỉ theo tên: `0.395270,0.024228,0.022535,0.021366,0.036243`. Truy vấn hợp: `0.053261,0.037528,0.026559,0.024022,0.026491`.
- Kiểm tra 1 đến 6: health `UP`. Chỉ tên `200`, total `1`, id `poi-name-cafe`. Chỉ ids `200`, total `1`, id `poi-name-tea`. Hợp `200`, total `2`, ids `poi-name-cafe,poi-name-tea`. Body `{}` là `422` `ERR_VALIDATION_FAILED`. Query `poi_name=Tea` với id cafe là `200`, total `1`, id `poi-name-cafe`.
- Idempotency: lặp kiểm tra 2 vẫn `200`, total `1`, id `poi-name-cafe`. `synthetic_rows` sau đó là `2`.
- Log: `service token_hits=0`, `service cafe_hits=0`, `service error_lines=0`, `postgres token_hits=0`, `postgres cafe_hits=0`.
- Kết luận: PASS. Không lệch kỳ vọng.
