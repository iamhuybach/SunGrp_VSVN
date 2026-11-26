# Runtime runbook — 20261126-gld-srv-old-address-price-story

Runbook này để người dùng tự chạy trên Fabric DEV. Tài liệu không ghi nhận lần chạy nào. Mọi kết quả ở mục cuối do người dùng điền sau khi chạy.

Nguồn: `architecture.md` (mục `Main brief`, `Ordering`, `Idempotency`, `Partial failure`, `Rollout`, `Rollback and forward recovery`, `Verification`), `decision.md` (`D-OLD-ADDR`, `D-E0`), cell `oldpricemd` và `oldpricepy` của `NB_CREATE_DDL` (theo code trong `architecture.md`), cell `srvinfoparam` của `NB_GLD_SRV_POI_INFO`, cell `srvmlparam` của `NB_GLD_SRV_POI_MULTI_LANG`, `pipelines/PL_VV_TRANS_SLV_TO_GLD_30M/PL_VV_TRANS_SLV_TO_GLD_30M.json`, cell tham số của `NB_00_ORCHES_SLV_TO_GLD`, và `docs/context/CTRL_TABLES_CONTEXT.md` §3, §4, §6, §7.

## Phạm vi và môi trường

- Môi trường: chỉ Fabric DEV. Không chạy ở STG hay PROD.
- Người chạy: người dùng. Agent không chạy bước nào.
- Thay đổi trong lần triển khai:
  - `lh_vv_gold.dbo.gld_srv_poi_info` có thêm `old_address` STRING, đặt sau `full_address`. Bảng cũng có thêm `price_level` INT, `price_min` DECIMAL(18,2) và `price_max` DECIMAL(18,2), đặt sau `review_count`. Cả bốn cột cho phép NULL.
  - `lh_vv_gold.dbo.gld_srv_poi_multi_lang` có thêm `story` STRING và `local_tips` STRING, đặt sau `experience`. Cả hai cột cho phép NULL.
  - `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` có thêm một cạnh: `PL_VV_TRANS_SLV_TO_GLD_30M`, `lh_vv_silver.dbo.slv_3p_poi_price` → `lh_vv_gold.dbo.gld_srv_poi_info`, `is_active = 1`, `priority = 1`, `load_mode = 'RECOMPUTE'`, `nb_name = 'NB_GLD_SRV_POI_INFO'`.
- Sáu cột mới chỉ nằm ở gold. Lần này không đổi PostgreSQL (`apps.srv_poi_info`, `apps.srv_poi_multi_lang`), Java entity hay API.
- `old_address` theo `D-OLD-ADDR`. Khi có dòng destination, giá trị là `coalesce(G1', G2', G3)`, các phần nối bằng `", "`:
  - G1' = `house_number, street, old_formatted_address`
  - G2' = `house_number, street, old_ward_with_type, old_city_with_type`
  - G3 = `slv_enr_poi_destination.full_address`
  
  Khi không có dòng destination thì `old_address` là NULL. Không có cột `old_house_number`, `old_street` hay `old_full_address`.
- Giá lấy từ `slv_3p_poi_price` bằng LEFT JOIN 1:1 theo `poi_id`. Join chỉ đọc dòng còn sống, không lọc theo `source_name`. Nếu một `poi_id` có hơn một dòng giá thì node dừng và không ghi gì.
- `story` và `local_tips` chỉ lấy từ `slv_pn_business_service_i18ns`, qua cùng phép join partner với `bio` và `usps`. Hai cột này không có fallback.
- Thứ tự bắt buộc: P1 → cell `oldpricepy` → publish hai notebook → `PL_VV_TRANS_SLV_TO_GLD_30M` → R1–R6. **Chỉ publish notebook sau khi `oldpricepy` thành công.**
- Workspace DEV: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>`.

## Điều kiện tiên quyết

1. Nhánh `main` có đủ code của task này: `NB_CREATE_DDL` có hai cell cuối `oldpricemd` và `oldpricepy`; `NB_GLD_SRV_POI_INFO` (`srvinfobuild`) và `NB_GLD_SRV_POI_MULTI_LANG` (`srvmlbuild`) là bản 26/11. Lúc này hai notebook node **chưa** được publish lên DEV.
2. Local test đã pass:
   `python -m pytest tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_srv_poi_serving_contract.py tests/test_enr_extract_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py -q` và `python -m pytest tests -q`.
   Kết quả: `<CẦN NGƯỜI DÙNG CUNG CẤP: kết quả pytest>`.
3. Trên DEV đã có những thứ sau. Nếu thiếu, `oldpricepy` sẽ dừng trước khi ghi:
   - đúng 1 dòng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` trong `lh_vv_ctrl.dbo.ctrl_mng_watermark`. Nếu chưa có thì chạy `plcadpy` trước.
   - cột `nb_name` trong `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`. Nếu chưa có thì chạy `enrddlpy` trước.
   - bảng `lh_vv_silver.dbo.slv_3p_poi_price` với kiểu `poi_id string`, `price_level int`, `price_min decimal(18,2)`, `price_max decimal(18,2)`. Bảng này chỉ do `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` ghi.
   - sáu cạnh active cũ của `gld_srv_poi_info` trên `PL_VV_TRANS_SLV_TO_GLD_30M`: `slv_poi_entity_non_enrich`, `slv_enr_poi_destination`, `slv_enr_poi_info_multi_lang`, `slv_3p_poi_rating`, `slv_3p_poi_review`, `slv_poi_media_info`.
4. Lúc chạy `oldpricepy`, luồng `PL_VV_TRANS_SLV_TO_GLD_30M` không chạy. Cell giữ khoá `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` với lease 90 phút. Nếu luồng đang giữ khoá, cell dừng với lỗi `Luồng PL_VV_TRANS_SLV_TO_GLD_30M đang giữ khoá (...)`.
   - Trigger lịch của pipeline 30M trên DEV có đang bật không, và có cần tạm dừng không: `<CẦN NGƯỜI DÙNG CUNG CẤP: trạng thái trigger lịch PL_VV_TRANS_SLV_TO_GLD_30M trên DEV>`.
   - `architecture.md` không mô tả trường hợp một run theo lịch chạy notebook cũ sau khi đã có cạnh giá mà notebook chưa publish. Nên publish ngay sau bước 2 (`oldpricepy`). Nếu được thì tạm dừng lịch từ bước 2 đến hết bước 4.
5. Tham số pipeline cần biết trước. Hai giá trị này không có trong repo:
   - `nb_orches_id`: `<CẦN NGƯỜI DÙNG CUNG CẤP: id notebook NB_00_ORCHES_SLV_TO_GLD trên DEV>`
   - `workspace_id`: `<CẦN NGƯỜI DÙNG CUNG CẤP: id workspace DEV>`
6. Không chạy lại `srvactivepy` hay `srvcoverpy` sau `oldpricepy`. Contract của hai cell này là bản cũ, nên chúng sẽ dừng an toàn nhưng tốn công chạy.

## Baseline trước khi chạy

Mọi query dưới đây chỉ đọc. Chạy trong notebook Spark SQL trên DEV. Ghi kết quả vào mục `Kết quả người dùng ghi nhận`.

B1. Schema hiện tại. Kỳ vọng: chưa có sáu cột mới, và `load_origin` có mặt.
```sql
DESCRIBE lh_vv_gold.dbo.gld_srv_poi_info;
DESCRIBE lh_vv_gold.dbo.gld_srv_poi_multi_lang;
```

B2. Version Delta và thời điểm commit cuối của hai bảng gold:
```sql
SELECT version, timestamp, operation FROM (DESCRIBE HISTORY lh_vv_gold.dbo.gld_srv_poi_info) ORDER BY version DESC LIMIT 5;
SELECT version, timestamp, operation FROM (DESCRIBE HISTORY lh_vv_gold.dbo.gld_srv_poi_multi_lang) ORDER BY version DESC LIMIT 5;
```
Nếu Fabric không cho `SELECT` trên `DESCRIBE HISTORY`, chạy `DESCRIBE HISTORY lh_vv_gold.dbo.gld_srv_poi_info LIMIT 5`.

B3. Số dòng sống và mốc `updated_at`. Mốc này dùng để kiểm tra idempotency:
```sql
SELECT count(*) AS live_rows, max(updated_at) AS max_updated_at
FROM lh_vv_gold.dbo.gld_srv_poi_info WHERE deleted_at IS NULL;
SELECT count(*) AS live_rows, max(updated_at) AS max_updated_at
FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang WHERE deleted_at IS NULL;
```
Ghi lại `T0` là thời điểm UTC ngay trước bước 4.

B4. Các cạnh vào `gld_srv_poi_info`. Kỳ vọng: 6 cạnh active trên `PL_VV_TRANS_SLV_TO_GLD_30M`, chưa có `slv_3p_poi_price`.
```sql
SELECT id, pl_name, src_schema, src_tbl, is_active, priority, load_mode, nb_name
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_schema = 'lh_vv_gold.dbo' AND trg_tbl = 'gld_srv_poi_info'
ORDER BY id;
```

B5. Chủ sở hữu `slv_3p_poi_price`. Kỳ vọng: chỉ có `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` với `is_active = 1`.
```sql
SELECT pl_name, src_tbl, is_active, load_mode
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_schema = 'lh_vv_silver.dbo' AND trg_tbl = 'slv_3p_poi_price';
```

B6. Dòng khoá luồng. Kỳ vọng: đúng 1 dòng, `lock_exec_id` là NULL.
```sql
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M';
```

B7. Kiểu cột của nguồn giá:
```sql
DESCRIBE lh_vv_silver.dbo.slv_3p_poi_price;
```

## Các bước thực hiện

### Bước 1 — Probe P1 (pre-flight, chỉ đọc)
```sql
SELECT count(*) AS dup_poi
FROM (SELECT poi_id FROM lh_vv_silver.dbo.slv_3p_poi_price
      GROUP BY poi_id HAVING count(*) > 1);
```
- Kỳ vọng `dup_poi = 0`.
- Bảng `slv_3p_poi_price` trên DEV không có `deleted_at` (DESCRIBE ngày 2026-11-26). Đếm mọi dòng. `ctx.input` chỉ lọc `deleted_at` khi bảng có cả `row_hash` và `deleted_at`.
- Nếu khác 0, **dừng**. Node info sẽ dừng đúng thiết kế với lỗi `slv_3p_poi_price {n} poi_id có hơn một dòng`. Cần sửa dữ liệu nguồn trước, việc này ngoài task. Để xem `poi_id` bị trùng (tối đa 50 dòng, không có dữ liệu cá nhân):
```sql
SELECT poi_id, count(*) AS n FROM lh_vv_silver.dbo.slv_3p_poi_price
GROUP BY poi_id HAVING count(*) > 1 ORDER BY n DESC LIMIT 50;
```

### Bước 2 — Chạy cell `oldpricepy` của `NB_CREATE_DDL`
- Mở `NB_CREATE_DDL` trên DEV. Chỉ chạy **một cell** `oldpricepy`, là cell cuối, ngay sau `oldpricemd`. Không chạy cả notebook.
- Cell không có tham số. Các hằng số cố định trong cell:
  - `CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"`
  - `WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"`
  - `PL = "PL_VV_TRANS_SLV_TO_GLD_30M"`
  - `WID = "wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M"`
  - `LEASE_MINUTES = 90`
  - `OWNER_COL = "load_origin"`
  - `PRICE_FQ = "lh_vv_silver.dbo.slv_3p_poi_price"`
  - `PRICE_OWNER = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"`
  - `EDGES_ON = [(1, "slv_3p_poi_price", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1)]`
- Thứ tự trong cell: nhận khoá, kiểm tra mọi điều kiện, rồi mới ghi. Phần ghi gồm ALTER `gld_srv_poi_info` (`old_address`, `price_level`, `price_min`, `price_max`, mỗi cột `AFTER` cột trước nó theo contract), ALTER `gld_srv_poi_multi_lang` (`story`, `local_tips`), rồi INSERT cạnh (`WHERE NOT EXISTS`). Sau đó cell chạy hậu kiểm và nhả khoá trong `finally`.
- Output kỳ vọng ở lần chạy đầu:
  `oldprice: +['gld_srv_poi_info.old_address', 'gld_srv_poi_info.price_level', 'gld_srv_poi_info.price_min', 'gld_srv_poi_info.price_max', 'gld_srv_poi_multi_lang.story', 'gld_srv_poi_multi_lang.local_tips']; cạnh ['slv_3p_poi_price']`
- Nếu cột đã có sẵn nhưng sai vị trí, cell in thêm `WARN oldprice: cột có sẵn nhưng lệch vị trí [...]; cell không tự dời`. Đây là cảnh báo, không phải lỗi. Cell không dời cột.
- Các lỗi có thể gặp:
  - `Dừng trước khi ghi: ...`: cell chưa ghi gì. Sửa nguyên nhân trong thông báo rồi chạy lại.
  - `Sau khi ghi: ...`: xem mục `Rollback và forward recovery`.
  - `Luồng PL_VV_TRANS_SLV_TO_GLD_30M đang giữ khoá (...)`: đợi run 30M kết thúc rồi chạy lại.
- **Chỉ sang bước 3 khi bước 2 in ra `oldprice: +[...]` và không có lỗi.**

### Bước 3 — Publish hai notebook node
- Publish `NB_GLD_SRV_POI_INFO` và `NB_GLD_SRV_POI_MULTI_LANG` bản 26/11 lên DEV. Cách publish (Git sync hay deployment pipeline): `<CẦN NGƯỜI DÙNG CUNG CẤP: cách publish notebook lên Fabric DEV>`.
- Không sửa cell tham số. Giá trị mặc định trong repo giống nhau ở `srvinfoparam` và `srvmlparam`; `NB_00_ORCHES_SLV_TO_GLD` truyền giá trị khi chạy:
  - `p_exec_id = ""`
  - `p_run_id = ""`
  - `p_pl_name = ""`
  - `p_trg_fq = ""`
  - `p_pinned_json = ""`
  - `p_mode = "RUN"`
  - `p_force = "false"`
  - `p_history_limit = "1000"`
- Không chạy tay hai notebook node. Chạy qua luồng 30M ở bước 4.

### Bước 4 — Chạy `PL_VV_TRANS_SLV_TO_GLD_30M` một lần

4a. (Tuỳ chọn, không ghi.) Xem kế hoạch: chạy tay `NB_00_ORCHES_SLV_TO_GLD` với
- `p_pl_name = "PL_VV_TRANS_SLV_TO_GLD_30M"`
- `p_mode = "PLAN"`
- các tham số khác giữ mặc định của cell: `p_run_id = ""`, `p_max_parallel = "3"`, `p_node_timeout_min = "20"`, `p_dag_timeout_min = "45"`, `p_lock_timeout_min = "90"`, `p_force_nodes = ""`, `p_history_limit = "1000"`, `p_non_data_ops = ""`

`PLAN` chỉ in kế hoạch và DAG, không nhận khoá, không ghi. Ghi lại hai node `gld_srv_poi_info` và `gld_srv_poi_multi_lang` có nằm trong danh sách node ứng viên không.

4b. Chạy pipeline `PL_VV_TRANS_SLV_TO_GLD_30M` với tham số:
- `nb_orches_id = <CẦN NGƯỜI DÙNG CUNG CẤP: id notebook NB_00_ORCHES_SLV_TO_GLD trên DEV>`
- `workspace_id = <CẦN NGƯỜI DÙNG CUNG CẤP: id workspace DEV>`
- `p_force_run = true`. Mặc định trong JSON là `false`. Đặt `true` để cổng `Get_Flow_Gate_GLD` không bỏ qua lần chạy với `reason=NO_DATA`.
- `p_max_idle_min = 0` (mặc định).

Pipeline gọi `NB_00_ORCHES_SLV_TO_GLD` với các giá trị cố định trong JSON: `p_pl_name = @pipeline().Pipeline`, `p_run_id = @pipeline().RunId`, `p_mode = "RUN"`, `p_max_parallel = "3"`, `p_node_timeout_min = "20"`, `p_dag_timeout_min = "45"`, `p_lock_timeout_min = "90"`, `p_force_nodes = ""`, `p_history_limit = "1000"`, `p_non_data_ops = ""`. Timeout của activity là 52 phút và `retry` là 0.

4c. Nếu sau 4b một trong hai node không có dòng `SUCCESS` trong `ctrl_log_table_run` của run đó, thì chạy tay `NB_00_ORCHES_SLV_TO_GLD`. Lý do: pipeline luôn truyền `p_force_nodes = ""`, nên node không có cạnh bẩn sẽ không chạy. Node `gld_srv_poi_multi_lang` không có cạnh mới. Xem truy vấn L2.

Tham số cho lần chạy tay:
- `p_pl_name = "PL_VV_TRANS_SLV_TO_GLD_30M"`
- `p_mode = "RUN"`
- `p_force_nodes`: CSV, chỉ ghi node còn thiếu, ví dụ `"gld_srv_poi_multi_lang"` hoặc `"gld_srv_poi_info,gld_srv_poi_multi_lang"`
- `p_run_id = ""`
- các tham số khác giống 4b: `p_max_parallel = "3"`, `p_node_timeout_min = "20"`, `p_dag_timeout_min = "45"`, `p_lock_timeout_min = "90"`, `p_history_limit = "1000"`, `p_non_data_ops = ""`

Chỉ làm bước này một lần, cho đúng những node còn thiếu.

## Kiểm tra kết quả

Các probe dưới đây chỉ đọc và chạy sau bước 4.

R1. Schema. Chạy:
```sql
DESCRIBE lh_vv_gold.dbo.gld_srv_poi_info;
DESCRIBE lh_vv_gold.dbo.gld_srv_poi_multi_lang;
```
Kỳ vọng:
- Info có `old_address string` ngay sau `full_address`, và `price_level int`, `price_min decimal(18,2)`, `price_max decimal(18,2)` ngay sau `review_count`, trước `cover_id`.
- Multi_lang có `story string`, `local_tips string` ngay sau `experience`.
- Cả sáu cột cho phép NULL. `load_origin` vẫn còn.

R2. Giá theo nguồn. Kỳ vọng: với `source_name` partner, cả ba cột đếm giá đều bằng 0.
```sql
SELECT source_name, count(*) AS n, count(price_level) AS n_level, count(price_min) AS n_min, count(price_max) AS n_max
FROM lh_vv_gold.dbo.gld_srv_poi_info WHERE deleted_at IS NULL GROUP BY 1;
```

R3. Kỳ vọng `0`: không có `old_address` nào mà thiếu dòng destination.
```sql
SELECT count(*) FROM lh_vv_gold.dbo.gld_srv_poi_info i
LEFT ANTI JOIN lh_vv_silver.dbo.slv_enr_poi_destination d ON i.poi_id = d.poi_id
WHERE i.old_address IS NOT NULL;
```

R4. Kỳ vọng `0`: dòng không phải partner không có `story` hay `local_tips`.
```sql
SELECT count(*) FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang
WHERE coalesce(lower(trim(source_name)), '') <> 'partner' AND (story IS NOT NULL OR local_tips IS NOT NULL);
```

R5. Metric của node info lấy từ `qg_json` (xem L2). Kỳ vọng:
- `old_address_g1 + old_address_g2 + old_address_g3 + old_address_null` bằng số dòng build (`entity_rows`).
- `price_matched` không lớn hơn số dòng Google cộng số dòng không phải partner khác. Đếm theo `source_name` ở R2.

Mẫu kiểm tra bằng mắt (tối đa 50 dòng; chỉ có id, nguồn, địa chỉ cũ và giá; không lấy phone, email hay website):
```sql
SELECT poi_id, source_name, full_address, old_address, price_level, price_min, price_max
FROM lh_vv_gold.dbo.gld_srv_poi_info WHERE deleted_at IS NULL AND (old_address IS NOT NULL OR price_level IS NOT NULL)
LIMIT 50;
SELECT poi_id, lang, source_name, left(story, 200) AS story_head, left(local_tips, 200) AS local_tips_head
FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang WHERE story IS NOT NULL OR local_tips IS NOT NULL LIMIT 50;
```

R6. Gồm ba phần:
- Chạy lại `oldpricepy` theo mục `Chạy lại để kiểm tra idempotency`. Kỳ vọng in ra `+[]`.
- Có đúng một cạnh active `slv_3p_poi_price → gld_srv_poi_info`, và tổng cộng có 7 cạnh active của `PL_VV_TRANS_SLV_TO_GLD_30M` vào `gld_srv_poi_info` (truy vấn L3).
- Lần nạp serving gold→PostgreSQL kế tiếp chạy thành công, và schema PostgreSQL không đổi. Sink này không nằm trong repo. Tên job hoặc pipeline serving: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên job/pipeline nạp serving gold→PostgreSQL trên DEV>`. Kiểm tra schema PostgreSQL bằng query chỉ đọc:
```sql
SELECT table_name, column_name, data_type FROM information_schema.columns
WHERE table_schema = 'apps' AND table_name IN ('srv_poi_info', 'srv_poi_multi_lang')
  AND column_name IN ('old_address', 'price_level', 'price_min', 'price_max', 'story', 'local_tips');
```
Kỳ vọng: 0 dòng.

## Chạy lại để kiểm tra idempotency

I1. Chạy lại một lần cell `oldpricepy`, sau khi R1–R5 đạt.
- Kỳ vọng in ra `oldprice: +[]; cạnh ['slv_3p_poi_price']`. Cell không có commit ALTER mới.
- Kiểm tra bằng B2: version của hai bảng gold không tăng do cell. INSERT có `NOT EXISTS`, nên không có dòng cạnh mới; L3 vẫn đúng 7 cạnh active.
- Có thể có commit trên `ctrl_mng_watermark` do cell nhận và nhả khoá. Đây là commit bình thường.

I2. Chạy lại một lần luồng 30M, giống bước 4b. Nếu cần thì thêm 4c với cùng `p_force_nodes`.
- Kỳ vọng: lần chạy đầu sau publish đã đổi `row_hash` của mọi dòng sống ở cả hai bảng, đúng một lần, và `updated_at` đã thay đổi. Kiểm tra:
```sql
SELECT count(*) AS live_rows, count_if(updated_at > TIMESTAMP '<T0 ghi ở baseline>') AS touched
FROM lh_vv_gold.dbo.gld_srv_poi_info WHERE deleted_at IS NULL;
SELECT count(*) AS live_rows, count_if(updated_at > TIMESTAMP '<T0 ghi ở baseline>') AS touched
FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang WHERE deleted_at IS NULL;
```
  Sau lần chạy đầu, kỳ vọng `touched = live_rows`.
- Ở lần chạy lại, với cùng đầu vào, `updated_rows = 0` cho cả hai node trong `ctrl_log_table_run` (L2), hoặc node có `NO_DATA`. `max(updated_at)` không đổi so với sau lần chạy đầu.
- Ảnh hưởng một lần được chấp nhận: consumer incremental phía sau sẽ đọc lại toàn bộ các dòng một lần. Tiền lệ là `is_active`.

## Kiểm tra log và watermark

L1. Run của luồng (tối đa 50 dòng):
```sql
SELECT exec_id, run_id, run_mode, table_filter, status, tbl_total_count, tbl_success_count, tbl_failed_count,
       tbl_no_data_count, started_at, ended_at, left(error_message, 300) AS error_head
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30M' AND started_at >= TIMESTAMP '<T0 ghi ở baseline>'
ORDER BY started_at DESC LIMIT 50;
```
Kỳ vọng: run ở bước 4 có `status = 'SUCCESS'`.

L2. Node và metric (tối đa 50 dòng):
```sql
SELECT exec_id, trg_tbl, status, entity_rows, inserted_rows, updated_rows, deactivated_rows, trg_version,
       get_json_object(qg_json, '$.metrics') AS metrics, get_json_object(qg_json, '$.warns') AS warns,
       left(error_message, 300) AS error_head, started_at
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30M'
  AND trg_tbl IN ('gld_srv_poi_info', 'gld_srv_poi_multi_lang')
  AND started_at >= TIMESTAMP '<T0 ghi ở baseline>'
ORDER BY started_at DESC LIMIT 50;
```
Kỳ vọng:
- Ở lần chạy đầu, `gld_srv_poi_info` có `SUCCESS` và `metrics` chứa `old_address_g1`, `old_address_g2`, `old_address_g3`, `old_address_null`, `price_matched`.
- `gld_srv_poi_multi_lang` có `SUCCESS`, và `warns` không có cảnh báo mới ngoài các `multi_lang_i18n_*` đã có.
- Thông báo lỗi có thể gặp: `slv_3p_poi_price {n} poi_id có hơn một dòng` và `slv_3p_poi_price kiểu {...}, cần {...}`.

L3. Cạnh. Kỳ vọng: 7 dòng active trên `PL_VV_TRANS_SLV_TO_GLD_30M`, `n = 1` ở mỗi dòng. Cạnh `slv_3p_poi_price` có `priority = 1`, `RECOMPUTE` và `NB_GLD_SRV_POI_INFO`.
```sql
SELECT pl_name, src_schema, src_tbl, is_active, priority, load_mode, nb_name, count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_schema = 'lh_vv_gold.dbo' AND trg_tbl = 'gld_srv_poi_info'
GROUP BY pl_name, src_schema, src_tbl, is_active, priority, load_mode, nb_name ORDER BY src_tbl;
```

L4. Khoá luồng và watermark của cạnh. Kỳ vọng:
- `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` có `lock_exec_id` NULL và `status` là `SUCCESS`, ghi sau `oldpricepy` hoặc sau run.
- Có dòng `wm_e__gld_srv_poi_info__slv_3p_poi_price` với `status = 'SUCCESS'` và `last_src_version` khác NULL. Dòng này do NB_00 INSERT lần đầu.
```sql
SELECT watermark_id, status, lock_exec_id, lock_at, last_src_version, last_run_id, left(error_message, 300) AS error_head, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M'
   OR watermark_id LIKE 'wm_e__gld_srv_poi_info__%'
   OR watermark_id LIKE 'wm_e__gld_srv_poi_multi_lang__%'
ORDER BY watermark_id LIMIT 50;
```

## Rollback và forward recovery

Nguyên tắc:
- Không DROP cột. Muốn xoá cột trên Delta phải bật `delta.columnMapping.mode = name`, mà patch cell không được dùng thiết lập này.
- Ưu tiên forward-fix: sửa notebook, qua local test, rồi publish lại.

Rollback:
1. Publish lại bản trước của `NB_GLD_SRV_POI_INFO` và `NB_GLD_SRV_POI_MULTI_LANG`. Bản hoặc commit cần quay về: `<CẦN NGƯỜI DÙNG CUNG CẤP: version/commit notebook trước 26/11 trên DEV>`.
2. Sau đó `ensure_target` ghi WARN cho các cột có trong bảng nhưng build không tạo ra. Sáu cột giữ giá trị cũ (stale).
3. Tuỳ chọn, ngoài phạm vi task, và chỉ khi người dùng quyết định riêng: chạy tay `UPDATE … SET <cột> = NULL` trên sáu cột, và đặt cạnh `slv_3p_poi_price → gld_srv_poi_info` thành `is_active = 0`. Runbook này không cung cấp lệnh ghi cho phần này. Quyết định: `<CẦN NGƯỜI DÙNG CUNG CẤP: có làm bước tuỳ chọn hay không>`.

Forward recovery theo điểm lỗi:

| Điểm lỗi | Trạng thái còn lại | Cách xử lý |
|---|---|---|
| `oldpricepy` báo `Dừng trước khi ghi` | Chưa ghi gì | Sửa nguyên nhân trong thông báo, chạy lại cell |
| Lỗi sau một số ALTER info | Đã thêm một phần cột, chưa có cạnh | Chạy lại cell. Cell chỉ thêm cột còn thiếu |
| Lỗi sau mọi ALTER, trước INSERT | Đã có cột, chưa có cạnh | Chạy lại cell. Notebook cũ vẫn chạy được và bỏ qua cột mới |
| Lỗi `Sau khi ghi` | Đã ghi cột hoặc cạnh, hậu kiểm thấy lệch | Đọc thông báo, đối chiếu L3 và R1, rồi chạy lại cell. Nếu vẫn lệch thì dừng và báo lại |
| Lỗi `mất khoá trước khi ghi` | Dừng trước lần ghi kế tiếp | Chạy lại cell khi luồng 30M không chạy |
| Lỡ publish notebook trước khi chạy cell | `ensure_target` thêm cột ở cuối bảng, input giá không có cạnh (có thể `ConfigError` ở `run_node`) | Chạy `oldpricepy`. Cell chấp nhận cột có sẵn, in WARN lệch vị trí, và thêm cạnh |
| Chỉ một node được publish | Bảng còn lại có NULL ở cột mới | Publish node còn lại, rồi làm lại bước 4c cho node đó |
| Node info dừng vì trùng giá (`QualityGateError`) | Không ghi MERGE | Sửa dữ liệu `slv_3p_poi_price`, kiểm tra lại P1, chạy lại luồng |
| Node dừng vì lệch kiểu hoặc thiếu cột (`ConfigError`) | Không ghi MERGE | Sửa schema theo thông báo, chạy lại luồng. Lib không tự retry |
| Khoá `wm_flow__…_30M` bị treo do cell bị kill | `lock_exec_id` bắt đầu bằng `oldprice-` | Đợi hết lease 90 phút, rồi chạy lại cell. Không sửa tay dòng khoá khi chưa chắc không còn run nào |

## Kết quả người dùng ghi nhận

Người dùng điền sau khi chạy. Agent không điền mục này.

| Mục | Kỳ vọng | Kết quả thực tế |
|---|---|---|
| Ngày giờ chạy (UTC), T0 | — | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| Local pytest | pass | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| B1–B7 baseline | 6 cạnh cũ, chưa có 6 cột, khoá trống | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| P1 `dup_poi` | 0 | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| `oldpricepy` lần 1, output | `+[6 cột]; cạnh ['slv_3p_poi_price']` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| WARN lệch vị trí | không có | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| Publish hai notebook | xong sau `oldpricepy` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| Run 30M (run_id, status) | SUCCESS | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| Có cần 4c không, `p_force_nodes` đã dùng | — | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| R1 schema | đúng vị trí, kiểu, nullable; còn `load_origin` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| R2 giá partner | 0 | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| R3 | 0 | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| R4 | 0 | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| R5 metric (g1/g2/g3/null, `entity_rows`, `price_matched`) | tổng = `entity_rows`; `price_matched` ≤ số dòng không phải partner | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| R6 `oldpricepy` lần 2 | `+[]` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| R6 cạnh active | 7, có đúng 1 cạnh giá | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| R6 serving load và schema PG | thành công; 0 cột mới ở `apps.*` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| I2 lần chạy đầu `touched = live_rows` | đúng cho cả hai bảng | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| I2 lần chạy lại `updated_rows` | 0 hoặc NO_DATA | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| L4 khoá và `wm_e__gld_srv_poi_info__slv_3p_poi_price` | khoá trống; cạnh SUCCESS | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| Ghi chú hoặc lỗi | — | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
