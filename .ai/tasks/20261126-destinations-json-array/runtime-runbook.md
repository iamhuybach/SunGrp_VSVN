# Runtime runbook: 20261126-destinations-json-array

## Phạm vi và môi trường

Runbook này kiểm tra lúc chạy thay đổi của task `20261126-destinations-json-array`: `CompactPoiResponse.Destinations.id` và `name` đổi từ chuỗi sang `List<String>`. Giá trị được parse chặt từ cột text `apps.srv_poi_info.destination_id` và `destination_name`. Thay đổi này phá vỡ hình dạng response cũ (breaking change): mảng chuỗi JSON hợp lệ trả về mảng giữ nguyên thứ tự, còn null, chuỗi rỗng hoặc giá trị không phải mảng chuỗi trả về `null`.

- Phạm vi: chỉ Serving API. Task không có notebook, pipeline, ctrl table hay watermark.
- Thư mục làm việc: `services/data-serving-service`.
- Môi trường: Docker do người dùng tự chạy bằng `docker compose` theo `services/data-serving-service/docker-compose.yml`. Container `data-serving-postgres` (image `postgres:18-alpine`) và `data-serving-service`.
- API: `http://localhost:8080`.
- Database: `vv_data_serving`, schema `apps`. Service kết nối với `currentSchema=apps`.
- Secret lấy từ biến môi trường của phiên: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POI_API_BEARER_TOKEN`. Không in giá trị, không ghi token, mật khẩu hay host vào runbook hoặc evidence.
- Shell: PowerShell 7 trở lên (cần `Invoke-WebRequest -SkipHttpErrorCheck`). Mọi lệnh chạy từ `services/data-serving-service`.
- Endpoint được kiểm tra (đường dẫn JSON lấy theo `PoiControllerIntegrationTest`):
  - `POST /api/v1/pois/compact`, kết quả ở `$.data[0].destinations`.
  - `GET /api/v1/pois/{poi_id}/practical_info`, kết quả ở `$.data.destinations`.
  - `POST /api/v1/pois/practical_info?required_fields=destinations`, kết quả ở `$.data[0].destinations`.

Main không chạy `docker compose`. Người dùng chạy tất cả các bước dưới đây.

## Điều kiện tiên quyết

1. Code của task đã có trong working tree và test đã pass:
   ```
   cd services/data-serving-service
   mvnw.cmd -q -B test -Dtest=PoiServiceTest,PoiControllerIntegrationTest
   mvnw.cmd -q -B test
   ```
2. Docker Desktop đang chạy.
3. Ba biến môi trường đã được đặt trong phiên PowerShell hiện tại. Lệnh sau chỉ kiểm tra là biến có giá trị hay không, không in giá trị:
   ```powershell
   'POSTGRES_USER','POSTGRES_PASSWORD','POI_API_BEARER_TOKEN' | ForEach-Object { "{0} set={1}" -f $_, [bool][Environment]::GetEnvironmentVariable($_) }
   ```
   Kỳ vọng cả ba dòng là `set=True`. Nếu `POI_API_BEARER_TOKEN` là `False`, compose vẫn chạy (mặc định chuỗi rỗng), nhưng bước kiểm tra token trong log sẽ bị bỏ qua. Hãy ghi rõ điều đó trong kết quả.
4. Port `8080` và port Postgres (`POSTGRES_PORT`, mặc định `55432`) đang trống.
5. Định nghĩa helper gọi API dùng trong các bước sau. Helper này không in header hay token:
   ```powershell
   $Base = 'http://localhost:8080'
   function Invoke-Vv([string]$Method, [string]$Path, [string]$Body) {
     $h = @{ Authorization = "Bearer $env:POI_API_BEARER_TOKEN" }
     $p = @{ Method = $Method; Uri = "$Base$Path"; Headers = $h; SkipHttpErrorCheck = $true }
     if ($Body) { $p.ContentType = 'application/json'; $p.Body = $Body }
     Invoke-WebRequest @p
   }
   function Show-Dest($label, $d) {
     $idT   = if ($null -eq $d.id)   { 'null' } elseif ($d.id   -is [array]) { 'array' } else { $d.id.GetType().Name }
     $nameT = if ($null -eq $d.name) { 'null' } elseif ($d.name -is [array]) { 'array' } else { $d.name.GetType().Name }
     $id0   = if ($d.id   -is [array]) { $d.id[0] }   else { '-' }
     $name0 = if ($d.name -is [array]) { $d.name[0] } else { '-' }
     "$label id_type=$idT name_type=$nameT id[0]=$id0 name[0]=$name0"
   }
   ```
   Lưu ý: `ConvertFrom-Json` của PowerShell có thể làm mất dạng mảng 1 phần tử ở một số phiên bản. Mảng tổng hợp ở đây có 2 phần tử nên không bị ảnh hưởng. Muốn chắc chắn thì đối chiếu thêm với chuỗi `.Content` (xem `Kiểm tra kết quả`).

## Baseline trước khi chạy

Tất cả truy vấn trong phần này chỉ đọc.

1. Khởi động stack (đây là bước chạy dịch vụ):
   ```powershell
   docker compose up -d --build
   docker compose ps
   ```
   Kỳ vọng: `data-serving-postgres` ở trạng thái healthy và `data-serving-service` đang chạy.
2. Kiểm tra bảng `apps.srv_poi_info` đã tồn tại chưa:
   ```powershell
   docker exec data-serving-postgres psql -U $env:POSTGRES_USER -d vv_data_serving -tA -c "SELECT to_regclass('apps.srv_poi_info') IS NOT NULL;"
   ```
   - `t`: bỏ qua DDL.
   - `f`: cần tạo schema và bảng bằng DDL của repo. Đường dẫn file DDL không có trong các file đã đọc: `<CẦN NGƯỜI DÙNG CUNG CẤP: đường dẫn file DDL tạo apps.srv_poi_info và lệnh áp dụng>`. Sau khi áp dụng, chạy lại kiểm tra này.
3. Đếm các dòng tổng hợp trước khi insert:
   ```powershell
   docker exec data-serving-postgres psql -U $env:POSTGRES_USER -d vv_data_serving -tA -c "SELECT count(*) FROM apps.srv_poi_info WHERE poi_id IN ('poi-dest-array','poi-dest-null');"
   ```
   Kỳ vọng `0`. Nếu khác `0`, dừng lại và hỏi người dùng. Không ghi đè hay xóa dòng đang có.
4. Baseline log: đếm số dòng cảnh báo destination trước khi chạy.
   ```powershell
   (docker logs data-serving-service 2>&1 | Select-String -SimpleMatch 'stored_json_parse_failed' | Select-String -SimpleMatch 'field=destination_' | Measure-Object).Count
   ```
   Ghi lại con số này làm `baseline_warn`. Không dán dòng log.

## Các bước thực hiện

1. Insert dữ liệu tổng hợp (bước ghi duy nhất của runbook). `destination_id` và `destination_name` là cột text:
   ```powershell
   docker exec data-serving-postgres psql -U $env:POSTGRES_USER -d vv_data_serving -v ON_ERROR_STOP=1 -c "INSERT INTO apps.srv_poi_info (poi_id, poi_name, destination_id, destination_name) VALUES ('poi-dest-array', 'Dest Array', '[""dest-a"",""dest-b""]', '[""Quan A"",""Quan B""]'), ('poi-dest-null', 'Dest Null', NULL, NULL);"
   ```
   Kỳ vọng `INSERT 0 2`. Nếu lỗi do cột NOT NULL khác, dừng lại và hỏi người dùng: `<CẦN NGƯỜI DÙNG CUNG CẤP: giá trị cho các cột bắt buộc khác của apps.srv_poi_info, nếu có>`. Không tự đoán giá trị.

   Câu SQL gốc là:
   `INSERT INTO apps.srv_poi_info (poi_id, poi_name, destination_id, destination_name) VALUES ('poi-dest-array', 'Dest Array', '["dest-a","dest-b"]', '["Quan A","Quan B"]'), ('poi-dest-null', 'Dest Null', NULL, NULL);`
   Trong lệnh PowerShell ở trên, dấu `"` bên trong được viết thành `""`.

2. Bước 1 của author input: health check.
   ```powershell
   $r = Invoke-Vv GET '/actuator/health'; "health status=$($r.StatusCode) body_status=$(($r.Content | ConvertFrom-Json).status)"
   ```
   Kỳ vọng `body_status=UP`.

3. Bước 2: compact cho POI có mảng.
   ```powershell
   $r2 = Invoke-Vv POST '/api/v1/pois/compact' '{"ids":["poi-dest-array"]}'
   "compact_array status=$($r2.StatusCode)"; Show-Dest 'compact_array' (($r2.Content | ConvertFrom-Json).data[0].destinations)
   ```
   Kỳ vọng: status `200`, `id_type=array name_type=array id[0]=dest-a name[0]=Quan A`.

4. Bước 3: practical info detail.
   ```powershell
   $r3 = Invoke-Vv GET '/api/v1/pois/poi-dest-array/practical_info'
   "detail status=$($r3.StatusCode)"; Show-Dest 'detail' (($r3.Content | ConvertFrom-Json).data.destinations)
   ```
   Kỳ vọng: status `200`, kiểu và phần tử đầu giống bước 3.

5. Bước 4: practical info list với `required_fields=destinations`.
   ```powershell
   $r4 = Invoke-Vv POST '/api/v1/pois/practical_info?required_fields=destinations' '{"ids":["poi-dest-array"]}'
   "list status=$($r4.StatusCode)"; Show-Dest 'list' (($r4.Content | ConvertFrom-Json).data[0].destinations)
   ```
   Kỳ vọng: status `200`, subtree `destinations` giống bước 3.

6. Bước 5: compact cho POI có cột destination null.
   ```powershell
   $r5 = Invoke-Vv POST '/api/v1/pois/compact' '{"ids":["poi-dest-null"]}'
   "compact_null status=$($r5.StatusCode) has_null_subtree=$($r5.Content.Contains('""destinations"":{""id"":null,""name"":null}'))"
   ```
   Kỳ vọng: status `200`, `has_null_subtree=True`, tức body chứa đúng `"destinations":{"id":null,"name":null}`. Nếu `False` (ví dụ do serializer định dạng khác), dùng `Show-Dest` và kiểm tra rằng cả hai khóa có mặt với giá trị `null`.

## Kiểm tra kết quả

| Kiểm tra | Kỳ vọng |
|---|---|
| Health (R0) | `UP` |
| Compact `poi-dest-array` (R1) | 200; `destinations.id` và `destinations.name` là mảng; phần tử đầu là `dest-a` và `Quan A` |
| Detail `poi-dest-array` (R2) | 200; giống R1 |
| List `required_fields=destinations` (R3) | 200; giống R1 |
| Compact `poi-dest-null` (R4) | 200; `"destinations":{"id":null,"name":null}` |

Đối chiếu thêm bằng chuỗi thô để chắc rằng đây là mảng JSON chứ không phải chuỗi. Lệnh chỉ in `True`/`False`:
```powershell
"r2_raw_array=$($r2.Content.Contains('""id"":[""dest-a"",""dest-b""]'))"
"r3_raw_array=$($r3.Content.Contains('""id"":[""dest-a"",""dest-b""]'))"
"r4_raw_array=$($r4.Content.Contains('""id"":[""dest-a"",""dest-b""]'))"
```
Kỳ vọng cả ba là `True`. Nếu bất kỳ kiểm tra nào không đạt, ghi lại status và kiểu JSON rồi dừng. Không sửa code trong lúc chạy runbook.

## Chạy lại để kiểm tra idempotency

Bước 6 của author input: lặp lại bước 2 và đếm số dòng (chỉ đọc).
```powershell
$r6 = Invoke-Vv POST '/api/v1/pois/compact' '{"ids":["poi-dest-array"]}'
"compact_repeat status=$($r6.StatusCode)"; Show-Dest 'compact_repeat' (($r6.Content | ConvertFrom-Json).data[0].destinations)
docker exec data-serving-postgres psql -U $env:POSTGRES_USER -d vv_data_serving -tA -c "SELECT count(*) FROM apps.srv_poi_info WHERE poi_id IN ('poi-dest-array','poi-dest-null');"
```
Kỳ vọng: status `200`, `id[0]=dest-a` giống lần đầu, và số dòng vẫn là `2`. Service chỉ đọc nên gọi lại không được làm thay đổi dữ liệu.

## Kiểm tra log và watermark

- Watermark: task này không có watermark hay ctrl table, nên không có gì để kiểm tra.
- Bước 7 của author input: đếm số dòng cảnh báo parse destination sau khi chạy. Chỉ ghi số, không dán dòng log:
  ```powershell
  $after = (docker logs data-serving-service 2>&1 | Select-String -SimpleMatch 'stored_json_parse_failed' | Select-String -SimpleMatch 'field=destination_' | Measure-Object).Count
  "destination_warn_after=$after"
  ```
  Kỳ vọng: `destination_warn_after - baseline_warn = 0`, vì dữ liệu tổng hợp là mảng chuỗi hợp lệ hoặc NULL (NULL không sinh cảnh báo). Định dạng dòng cảnh báo theo architecture là `stored_json_parse_failed poi_id={} field={destination_id|destination_name} reason={INVALID_JSON|NOT_ARRAY|BAD_ELEMENT}`.
- Stop S3: nếu trên dữ liệu thật, phần lớn dòng có giá trị khác null lại sinh cảnh báo `reason=NOT_ARRAY` (ví dụ chuỗi bị encode hai lần hoặc dạng CSV), dừng lại và hỏi người dùng. Không tự thêm logic unwrap. Để đếm theo reason mà không dán log:
  ```powershell
  docker logs data-serving-service 2>&1 | Select-String -SimpleMatch 'field=destination_' | ForEach-Object { if ($_ -match 'reason=(\w+)') { $Matches[1] } } | Group-Object | Select-Object Name,Count
  ```
- Token không được xuất hiện trong log. Lệnh sau chỉ in số đếm, và chỉ chạy khi token có giá trị:
  ```powershell
  if ($env:POI_API_BEARER_TOKEN) { "token_in_logs=" + (docker logs data-serving-service 2>&1 | Select-String -SimpleMatch $env:POI_API_BEARER_TOKEN | Measure-Object).Count } else { 'token_in_logs=SKIPPED (token rỗng)' }
  ```
  Kỳ vọng `token_in_logs=0`.

## Rollback và forward recovery

- Rollback code (theo architecture): revert các hunk DTO, `PoiService`, test và doc của task này. Không có dữ liệu cần migrate và gold không thay đổi. Cẩn thận không đụng đến các hunk chưa commit của task khác trong cùng file, ví dụ `PoiControllerIntegrationTest.java` và `practical_info_list.md`.
- Rollback môi trường runtime: chỉ chạy `docker compose down -v` sau khi người dùng xác nhận rõ ràng rằng volume `postgres_data` có thể bị xóa. Lệnh này xóa toàn bộ dữ liệu Postgres trong volume, bao gồm cả dữ liệu không phải tổng hợp. Chưa có xác nhận thì không chạy, và để nguyên stack cùng các dòng tổng hợp.
  ```powershell
  # CHỈ chạy sau khi người dùng xác nhận được phép xóa volume
  docker compose down -v
  ```
- Forward recovery: nếu runtime cho thấy gold lưu dạng double-encoded hoặc không phải mảng (Stop S3), dừng lại và hỏi người dùng. Không thêm unwrapping một cách âm thầm và không nới lỏng quy tắc parse.

## Kết quả người dùng ghi nhận

Main chạy local ngày 2026-11-26 theo yêu cầu. Không có token, mật khẩu, host, dòng log thô hay dữ liệu cá nhân. `docker compose down -v` không chạy. Stack vẫn đang chạy.

```
baseline_table_exists=apps.srv_poi_info
baseline_synthetic_rows=0
baseline_warn=0
insert_result=INSERT 0 2
health status=200 body_status=UP
compact_array status=200 id_type=array name_type=array id[0]=dest-a name[0]=Quan A
detail status=200 id_type=array name_type=array id[0]=dest-a name[0]=Quan A
list status=200 id_type=array name_type=array id[0]=dest-a name[0]=Quan A
compact_null status=200 has_null_subtree=True
r2_raw_array=True r3_raw_array=True r4_raw_array=True
compact_repeat status=200 id[0]=dest-a
synthetic_rows_after=2
destination_warn_after=0
token_in_logs=0
service_error_lines=0
```

Kết luận: PASS. `destinations.id` và `destinations.name` là mảng JSON, không còn là chuỗi.
