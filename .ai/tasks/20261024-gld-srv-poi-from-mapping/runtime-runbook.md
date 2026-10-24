# Runtime runbook: 20261024-gld-srv-poi-from-mapping

## Phạm vi và môi trường

- Môi trường: Fabric DEV. Workspace: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>`.
- Lakehouse: `lh_vv_ctrl`, `lh_vv_silver`, `lh_vv_gold` (schema `dbo`).
- Runbook này chạy các bước sau, đúng thứ tự:
  0. Chạy lại cell `srvpoipy` (notebook `NB_CREATE_DDL`) một lần sau khi cell được thêm `_refresh_lock()` trước `ALTER`, trước mỗi `CREATE` và trước `INSERT`.
  1. `NB_SETUP_INITIAL_DDL` với `p_apply = "false"`.
  2. `NB_GLD_SRV_POI_INFO` chạy `DRY_RUN`, rồi `RUN`, rồi `RUN` lần nữa.
  3. `NB_GLD_SRV_POI_MULTI_LANG` chạy `RUN`. Kết quả mong đợi là FAILED (D-SRV-23).
  4. `NB_00_ORCHES_SLV_TO_GLD` chạy `p_mode = "PLAN"` cho `PL_VV_TRANS_SLV_TO_GLD_30P`.
  5. Bộ đếm mã lỗi giờ mở cửa Google, chạy chỉ đọc trong một phiên nháp.
- Bảng liên quan:
  - đích gold: `lh_vv_gold.dbo.gld_srv_poi_info`, `lh_vv_gold.dbo.gld_srv_poi_multi_lang`;
  - silver: `lh_vv_silver.dbo.slv_enr_poi_destination` (có thêm 5 cột `destination_id`, `country_code`, `postal_code`, `lat`, `lng`), `lh_vv_silver.dbo.slv_poi_entity_non_enrich`, `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang`, `lh_vv_silver.dbo.slv_pn_business_service_i18ns`;
  - ctrl: `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`, `lh_vv_ctrl.dbo.ctrl_mng_watermark`, `lh_vv_ctrl.dbo.ctrl_log_run`, `lh_vv_ctrl.dbo.ctrl_log_table_run`.
- Khoá luồng: `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P`. `srvpoipy`, mỗi lần chạy tay một node bằng `RUN` và NB_00 khi `RUN` đều giữ khoá này. Hạn khoá là 90 phút (`LEASE_MINUTES = 90`, bằng `p_lock_timeout_min` mặc định của NB_00).
- Những việc không làm trong runbook này:
  - không tạo và không đặt lịch pipeline `PL_VV_TRANS_SLV_TO_GLD_30P`;
  - không gắn hai bảng gold vào `PL_VV_TRANS_SLV_TO_ENR_15P`;
  - không `DROP` bảng nào và không bỏ 5 cột destination;
  - không chạy lại `enrflagpy` (hợp đồng `slv_enr_poi_destination` trong cell đó là bản 8 cột);
  - không sửa cell nào của notebook.
- Trạng thái đã biết trước runbook (`evidence/results/gld_srv_edge_payload.txt`, ngày 2026-10-24):
  - `srvpoipy` lần 1: tạo 2 bảng gold, `destination +5`, `cạnh 6`;
  - `srvpoipy` lần 2: `destination +0; gold tạo []; cạnh 6`;
  - probe `gld_srv_edge_payload`: `edge_n 6`, `payload_match True`, và ba dòng `cols … match True` cho destination, multi_lang và info.
- Rủi ro đã chấp nhận: D-SRV-30 (`STATE-001`, `accepted-risk`). `_refresh_lock` giữ nguyên trong cell.

## Điều kiện tiên quyết

1. Bản notebook đã deploy lên DEV phải trùng bản trong repo, gồm cả các thay đổi chưa commit của `NB_CREATE_DDL`, `NB_SETUP_INITIAL_DDL` và hai notebook mới `NB_GLD_SRV_POI_INFO`, `NB_GLD_SRV_POI_MULTI_LANG`. Commit hoặc mốc deploy: `<CẦN NGƯỜI DÙNG CUNG CẤP: commit hash hoặc thời điểm deploy notebook lên DEV>`.
2. Kiểm thử local đã pass:
   - `python -m pytest tests/test_initial_ddl_contract.py tests/test_gld_srv_poi_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py -q`
   - `python -m pytest -q`
3. Trong lúc chạy:
   - không có run nào của `PL_VV_TRANS_SLV_TO_GLD_30P`;
   - các tác vụ ghi của luồng enrichment (`PL_VV_TRANS_SLV_TO_ENR_15P`) đang nghỉ, vì `srvpoipy` không giữ khoá ENR_15P.
4. Notebook đã gắn ba lakehouse `lh_vv_ctrl`, `lh_vv_silver`, `lh_vv_gold`.
5. Mọi truy vấn kiểm tra đều chỉ đọc. Chạy chúng trong một notebook nháp riêng, không chạy trong các notebook của task.

## Baseline trước khi chạy

Chạy các truy vấn dưới đây trước bước 0 và ghi kết quả vào mục `Kết quả người dùng ghi nhận`. Các truy vấn chỉ đọc và trả về tối đa 50 dòng. Chúng chỉ lấy số đếm, định danh bảng và trạng thái, không lấy dữ liệu POI.

B1. Dòng khoá luồng:

```sql
SELECT watermark_id, status, lock_exec_id IS NOT NULL AS locked, lock_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P'
```

Kỳ vọng: `locked = false`. Nếu `locked = true` thì dừng lại. Chờ hết hạn khoá 90 phút hoặc hỏi xem ai đang chạy luồng.

B2. Cạnh của hai bảng gold:

```sql
SELECT pl_name, src_schema, src_tbl, trg_tbl, is_active, priority, load_mode, nb_name, count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_schema = 'lh_vv_gold.dbo' AND trg_tbl IN ('gld_srv_poi_multi_lang', 'gld_srv_poi_info')
GROUP BY pl_name, src_schema, src_tbl, trg_tbl, is_active, priority, load_mode, nb_name
ORDER BY trg_tbl, src_tbl
```

Kỳ vọng: 6 dòng. Mọi dòng có `pl_name = PL_VV_TRANS_SLV_TO_GLD_30P`, `src_schema = lh_vv_silver.dbo`, `is_active = 1`, `priority = 1`, `load_mode = RECOMPUTE` và `n = 1`. `nb_name` là `NB_GLD_SRV_POI_INFO` hoặc `NB_GLD_SRV_POI_MULTI_LANG` tuỳ bảng đích. Không có dòng nào thuộc `PL_VV_TRANS_SLV_TO_ENR_15P`.

B3. Tổng số dòng config, dùng để phát hiện một lần INSERT thừa:

```sql
SELECT count(*) AS n, max(id) AS max_id FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
```

B4. Schema destination:

```sql
DESCRIBE TABLE lh_vv_silver.dbo.slv_enr_poi_destination
```

Kỳ vọng: 13 cột theo thứ tự `poi_id` (NOT NULL), `street`, `ward`, `district`, `city`, `full_address`, `created_at`, `updated_at`, `destination_id`, `country_code`, `postal_code`, `lat`, `lng`.

B5. Version Delta gần nhất. Chạy bằng PySpark và chỉ lấy ba cột:

```python
for fq in ["lh_vv_silver.dbo.slv_enr_poi_destination",
           "lh_vv_gold.dbo.gld_srv_poi_info",
           "lh_vv_gold.dbo.gld_srv_poi_multi_lang"]:
    print(fq)
    spark.sql(f"DESCRIBE HISTORY {fq}").select("version", "timestamp", "operation").limit(5).show(truncate=False)
```

B6. Số dòng của đích và đầu vào:

```sql
SELECT 'gld_srv_poi_info' AS t, count(*) AS n FROM lh_vv_gold.dbo.gld_srv_poi_info
UNION ALL SELECT 'gld_srv_poi_multi_lang', count(*) FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang
UNION ALL SELECT 'slv_enr_poi_destination', count(*) FROM lh_vv_silver.dbo.slv_enr_poi_destination
UNION ALL SELECT 'slv_enr_poi_info_multi_lang', count(*) FROM lh_vv_silver.dbo.slv_enr_poi_info_multi_lang
UNION ALL SELECT 'slv_pn_business_service_i18ns', count(*) FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns
```

```sql
SELECT source_name, count(*) AS n
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich
GROUP BY source_name ORDER BY source_name
```

Theo probe `gld_srv_input_shape`, entity có 24 dòng `partner` và 41 dòng `google`, còn `slv_enr_poi_destination` và `slv_enr_poi_info_multi_lang` có 0 dòng (D-SRV-23). Nếu số đo khác probe thì ghi lại. Các kỳ vọng 24/13/11 ở bước 2 dựa trên đúng các số này.

B7. Dòng watermark cạnh của hai node:

```sql
SELECT watermark_id, status, last_src_version, last_success_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE trg_tbl IN ('gld_srv_poi_multi_lang', 'gld_srv_poi_info')
ORDER BY watermark_id
```

B8. Log node gần nhất và log run của luồng:

```sql
SELECT left(exec_id, 8) AS exec8, pl_name, trg_tbl, status, entity_rows, inserted_rows, updated_rows,
       deactivated_rows, trg_version, started_at, left(error_message, 300) AS err
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_schema = 'lh_vv_gold.dbo' AND trg_tbl IN ('gld_srv_poi_multi_lang', 'gld_srv_poi_info')
ORDER BY started_at DESC LIMIT 10
```

```sql
SELECT count(*) AS n, max(started_at) AS last_started
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30P'
```

## Các bước thực hiện

### Bước 0: chạy lại `srvpoipy` (bản đã thêm `_refresh_lock()`)

- Notebook `NB_CREATE_DDL`. Chỉ chạy một cell `srvpoipy`, một lần. Không chạy các cell khác, nhất là `enrflagpy`. Cell này không có tham số.
- Pass:
  - output in `destination +0; gold tạo []; cạnh …`;
  - không có dòng `…: đã tạo`;
  - cell không raise lỗi.
- Phần `cạnh …` trong output in danh sách cạnh active. Ghi nguyên văn phần này. Số cạnh sẽ được đối chiếu lại bằng B2.
- Fail khi có bất kỳ dấu hiệu nào sau đây:
  - `destination +N` với N > 0;
  - `gold tạo` không rỗng;
  - B5 cho thấy version mới với operation `ADD COLUMNS` hoặc `CREATE TABLE` trên destination hoặc gold;
  - B3 đổi `n` hoặc `max_id`.
- Khi fail: dừng runbook, không chạy bước 1 và không tự sửa. Ghi output cùng B3 và B5 rồi báo người dùng.
- Các lỗi dừng an toàn, tức là chưa ghi gì:
  - `Luồng PL_VV_TRANS_SLV_TO_GLD_30P đang giữ khoá (…): chạy lại sau`: chờ khoá được nhả hoặc hết hạn 90 phút, rồi chạy lại cell;
  - `Luồng PL_VV_TRANS_SLV_TO_GLD_30P mất khoá trước khi ghi`: chạy lại cell một lần;
  - `Dừng trước khi ghi: …`: ghi lại thông điệp và báo người dùng.
- Sau khi chạy: lặp lại B1 (kỳ vọng `locked = false`), B2, B3 và B5. `ctrl_mng_watermark` có thể có version mới vì cell cập nhật dòng khoá. Điều đó đúng thiết kế.

### Bước 1: `NB_SETUP_INITIAL_DDL`, chỉ lập kế hoạch

- Tham số: `p_apply = "false"`.
- Pass:
  - 18 spec, tất cả `EXISTS_OK`;
  - không có `schema_issues`;
  - không ghi gì: B3 và B5 không đổi so với sau bước 0.

### Bước 2: `NB_GLD_SRV_POI_INFO`

Tham số dùng chung cho cả ba lần chạy:

| Tham số | Giá trị |
|---|---|
| `p_exec_id` | `""` |
| `p_run_id` | `""` |
| `p_pl_name` | `""` |
| `p_trg_fq` | `""` |
| `p_pinned_json` | `""` |
| `p_force` | `"false"` |
| `p_history_limit` | `"1000"` |

2a. `p_mode = "DRY_RUN"`.
- Pass: không có lỗi; B5 cho `gld_srv_poi_info` không có version mới; B6 cho `gld_srv_poi_info` giữ nguyên số dòng baseline; B7 không đổi.
- Ghi nhận dòng log mới trong `ctrl_log_table_run` (B8), nếu có.

2b. `p_mode = "RUN"` (lần 1).
- Pass:
  - log node `status = SUCCESS`;
  - truy vấn K1 của mục `Kiểm tra kết quả` đạt mọi kỳ vọng;
  - B5 cho `gld_srv_poi_info` có đúng một version mới (MERGE).
- Ghi lại `trg_version` của lần chạy này.

2c. `p_mode = "RUN"` (lần 2). Xem mục `Chạy lại để kiểm tra idempotency`.

### Bước 3: `NB_GLD_SRV_POI_MULTI_LANG`

- Tham số giống bước 2, với `p_mode = "RUN"`.
- Pass, theo D-SRV-23:
  - run kết thúc `FAILED` với lý do đầu vào bắt buộc rỗng (`Đầu vào bắt buộc rỗng`);
  - `gld_srv_poi_multi_lang` có 0 dòng;
  - B5 cho bảng này không có version mới.
- Fail: run SUCCESS, bảng đích có dòng, hoặc run lỗi với lý do khác.

### Bước 4: `NB_00_ORCHES_SLV_TO_GLD`, PLAN

| Tham số | Giá trị |
|---|---|
| `p_pl_name` | `"PL_VV_TRANS_SLV_TO_GLD_30P"` (giá trị mặc định trong cell là `PL_VV_TRANSFORM_SLV_TO_GLD_1H`, phải đổi) |
| `p_run_id` | `""` |
| `p_mode` | `"PLAN"` |
| `p_max_parallel` | `"3"` |
| `p_node_timeout_min` | `"20"` |
| `p_dag_timeout_min` | `"45"` |
| `p_lock_timeout_min` | `"90"` |
| `p_force_nodes` | `""` |
| `p_history_limit` | `"1000"` |
| `p_non_data_ops` | `""` |

- Pass:
  - DAG có 2 node, `gld_srv_poi_multi_lang` và `gld_srv_poi_info`;
  - không có lỗi;
  - `PLAN` không ghi gì: B1, B7 và truy vấn `ctrl_log_run` của B8 không đổi.
- Ghi nhận các WARN về kiểm tra nhịp (`_30P` không khớp `CADENCE_RE`). WARN này đã được chấp nhận và không làm bước này fail.

### Bước 5: bộ đếm mã lỗi giờ mở cửa Google (chỉ đọc)

1. Mở một phiên notebook nháp mới, không dùng notebook của task. Fabric không hiện cell id. Trong `NB_GLD_SRV_POI_INFO`, ô cần copy là ô code ngay dưới `%run NB_LIB_TRANSFORM_SLV_GLD`. Dòng đầu của ô là `# BEGIN_HOURS_PURE`, rồi `import json` và `DAY_LABELS`. Ô kế tiếp bắt đầu bằng `ENT_COLS`; không copy ô đó. Dán cả ô vào phiên nháp và chạy để định nghĩa `operating_hours`. Cell này là Python thuần và không ghi gì.
2. Chạy đoạn sau, lấy nguyên văn từ mục `Verification` của architecture.md:

```python
from collections import Counter
rows = spark.table("lh_vv_silver.dbo.slv_poi_entity_non_enrich").select("source_name", "opening_hours_text").collect()
print(Counter(operating_hours(r[0], r[1])[1] for r in rows))
```

- Pass: Counter chỉ có khoá `None`. Theo B6 baseline, tổng số đếm là 65 (24 partner và 41 google).
- Chỉ in Counter. Không in `rows` và không in JSON giờ mở cửa.

## Kiểm tra kết quả

K1. Sau bước 2b, trên các dòng live của `gld_srv_poi_info`:

```sql
SELECT count(*) AS n_live,
       count(DISTINCT poi_id) AS n_poi,
       sum(CASE WHEN is_recommended = true THEN 1 ELSE 0 END) AS rec_true,
       sum(CASE WHEN operating_hours IS NULL THEN 1 ELSE 0 END) AS hours_null,
       sum(CASE WHEN json_array_length(operating_hours) = 7 THEN 1 ELSE 0 END) AS hours_len7,
       sum(CASE WHEN is_verified IS NOT NULL THEN 1 ELSE 0 END) AS verified_not_null,
       sum(CASE WHEN is_bookable IS NOT NULL THEN 1 ELSE 0 END) AS bookable_not_null,
       sum(CASE WHEN destination_id IS NOT NULL OR country_code IS NOT NULL OR postal_code IS NOT NULL
                  OR lat IS NOT NULL OR lng IS NOT NULL THEN 1 ELSE 0 END) AS dest_cols_not_null
FROM lh_vv_gold.dbo.gld_srv_poi_info
WHERE deleted_at IS NULL
```

Kỳ vọng: `n_live = 24`, `n_poi = 24`, `rec_true = 24`, `hours_null = 13`, `hours_len7 = 11`, `verified_not_null = 0`, `bookable_not_null = 0`, `dest_cols_not_null = 0`.

K2. Không có dòng xoá mềm sau lần RUN đầu tiên:

```sql
SELECT count(*) AS n_all, sum(CASE WHEN deleted_at IS NOT NULL THEN 1 ELSE 0 END) AS n_deleted
FROM lh_vv_gold.dbo.gld_srv_poi_info
```

Kỳ vọng: `n_all = 24`, `n_deleted = 0`.

K3. Sau bước 3:

```sql
SELECT count(*) AS n FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang
```

Kỳ vọng: `n = 0`.

K4. Sau mọi bước: chạy lại B2. Kỳ vọng vẫn là 6 cạnh của GLD_30P và không có cạnh nào thuộc ENR_15P.

## Chạy lại để kiểm tra idempotency

- `srvpoipy` (bước 0) là lần chạy thứ ba của cell. Pass là `destination +0; gold tạo []`, không có ALTER, CREATE hay INSERT config mới (B3, B5).
- `NB_SETUP_INITIAL_DDL` với `p_apply = "false"` không ghi gì (bước 1).
- `NB_GLD_SRV_POI_INFO` RUN lần 2 (bước 2c), với tham số giống 2b:
  - log node có `inserted_rows = 0`, `updated_rows = 0` và `deactivated_rows = 0`;
  - B5 cho `gld_srv_poi_info` không có version mới so với sau 2b;
  - K1 và K2 cho đúng các số như sau 2b.
- Fail: có diff khác 0 hoặc có version Delta mới. Khi fail thì dừng lại. Ghi log node (B8) cùng `get_json_object(qg_json, '$.metrics')` và báo người dùng. Không chạy RUN thêm lần nữa.

## Kiểm tra log và watermark

L1. Log node, sau mỗi bước 2a, 2b, 2c và 3. Truy vấn này lấy mã, số đếm và metric, không lấy dữ liệu:

```sql
SELECT left(exec_id, 8) AS exec8, pl_name, trg_tbl, status, entity_rows, inserted_rows, updated_rows,
       deactivated_rows, trg_version, started_at,
       get_json_object(qg_json, '$.mode') AS mode,
       get_json_object(qg_json, '$.metrics') AS metrics,
       get_json_object(qg_json, '$.warns') AS warns,
       left(error_message, 300) AS err
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_schema = 'lh_vv_gold.dbo' AND trg_tbl IN ('gld_srv_poi_multi_lang', 'gld_srv_poi_info')
ORDER BY started_at DESC LIMIT 10
```

Kỳ vọng:
- 2b: `SUCCESS` với `inserted_rows = 24`.
- 2c: `SUCCESS` với 0/0/0.
- 3: `FAILED`, `err` nêu đầu vào bắt buộc rỗng.
- `metrics` của info gồm `destination_dup_poi`, `partner_rows`, `google_rows_kept`, `operating_hours_null`. Ghi giá trị lại; architecture.md không đặt số kỳ vọng cho các metric này.
- Có thể có WARN `multi_lang_source_name_null`.

L2. Khoá luồng: chạy lại B1 sau bước 0, sau mỗi lần RUN của bước 2 và 3, và sau bước 4.
- Kỳ vọng `locked = false` sau mỗi bước.
- `status` của dòng khoá có thể đổi sau mỗi RUN (nhả khoá thì ghi trạng thái run). Riêng bước 4 (PLAN) không được làm đổi dòng này.

L3. Watermark cạnh: chạy lại B7 sau bước 2, 3 và 4. Kỳ vọng không đổi so với baseline, vì chạy node bằng tay không tiến cạnh và `PLAN` không ghi.

L4. Log run của luồng: chạy lại truy vấn `ctrl_log_run` của B8 sau bước 4. Kỳ vọng `n` và `last_started` không đổi, vì `PLAN` không ghi.

## Rollback và forward recovery

- Không `DROP` hai bảng gold và không bỏ 5 cột destination. Năm cột này cho phép NULL và có thể giữ nguyên.
- Không có bước rollback dữ liệu nào trong runbook này. Mọi lỗi dừng trước MERGE đều giữ nguyên bảng đích và ghi `FAILED` vào `ctrl_log_table_run`.
- Forward recovery là chạy lại node hỏng với đúng tham số của bước đó, sau khi sửa nguyên nhân:
  - `NB_GLD_SRV_POI_INFO` lỗi ở 2b hoặc 2c (ví dụ QG `pk_null`/`pk_duplicate`, mã lỗi giờ mở cửa, hoặc destination có `poi_id` trùng với max `updated_at` null hay bằng nhau): sửa code ở task khác, rồi chạy lại `RUN`. Build tính lại toàn bộ, MERGE ghi đè theo `row_hash`, và các dòng biến mất bị xoá mềm.
  - `NB_GLD_SRV_POI_MULTI_LANG` FAILED vì đầu vào rỗng là kết quả đúng. Không xử lý gì cho đến task theo dõi D-SRV-23.
  - `srvpoipy` bị ngắt giữa chừng: chạy lại cell. Mọi trạng thái dở dang đều qua được bước kiểm tra trước khi ghi.
- Khoá treo `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P`: chờ hết hạn 90 phút rồi chạy lại. Không tự `UPDATE` dòng khoá. Nếu cần nhả khoá sớm: `<CẦN NGƯỜI DÙNG CUNG CẤP: xác nhận không còn run nào giữ khoá và phê duyệt nhả khoá thủ công>`.
- Muốn ngừng phục vụ hai bảng: cần một patch cell sau này đặt 6 cạnh GLD_30P về `is_active = 0`. Việc này nằm ngoài runbook và cần task riêng.
- Nếu bước 0 lại thực hiện ALTER, CREATE hoặc INSERT config: không hoàn tác. Dừng runbook, ghi B3, B5 và output cell, rồi báo người dùng.

## Kết quả người dùng ghi nhận

Dán kết quả đã làm sạch vào đây: tối đa 50 dòng, chỉ số đếm, định danh bảng, trạng thái và mã, không có dữ liệu cá nhân hay JSON giờ mở cửa thô.

Đã có từ trước (evidence `gld_srv_edge_payload.txt`, 2026-10-24):

```
srvpoipy run 1: destination +5; gold tạo ['lh_vv_gold.dbo.gld_srv_poi_multi_lang', 'lh_vv_gold.dbo.gld_srv_poi_info']; cạnh 6
srvpoipy run 2: destination +0; gold tạo []; cạnh 6
edge_n 6; payload_match True; cols destination/multi_lang/info match True
```

| Mục | Kỳ vọng | Kết quả thực tế |
|---|---|---|
| Thời điểm chạy, người chạy | — | `<CẦN NGƯỜI DÙNG CUNG CẤP: thời điểm, người chạy>` |
| B1 khoá luồng | `locked = false` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| B2 cạnh | 6 dòng GLD_30P, `is_active = 1`, `n = 1` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| B3 config `n`, `max_id` | — | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| B5 version destination, info, multi_lang | — | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| B6 số dòng | entity 24 partner / 41 google; destination 0; info_multi_lang 0 | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| Bước 0 `srvpoipy` | `destination +0; gold tạo []`; B3 và B5 không đổi | 2026-10-25: `destination +0; gold tạo []`; 6 cạnh GLD_30P, `RECOMPUTE`, `n` ngầm 1 theo payload. B3 và B5 không có trong paste. |
| Bước 1 `NB_SETUP_INITIAL_DDL` | 18 spec, `EXISTS_OK`, không có `schema_issues`, không ghi | 2026-10-25: `status=PLAN`, `p_apply=false`, 18 `EXISTS_OK`, seed `to_insert=0` (pipeline 59, watermark 2, registry 354, place_type 387, amenities 175). Exit không có `schema_issues`. |
| Bước 2a DRY_RUN | không ghi bảng đích | 2026-10-25 17:06: SUCCESS, diff insert 24 / update 0 / xoá mềm 0. WARN nhịp `_30P` và `_15P` đã chấp nhận. RUN sau đó `trg_version = 1`, nên DRY_RUN không commit. |
| Bước 2b RUN, K1 và K2 | SUCCESS; 24/24/24/13/11/0/0/0; `n_deleted = 0` | 2026-10-25 18:03: SUCCESS, inserted 24, updated 0, deactivated 0, `trg_version = 1`. K1: 24, 24, 24, 13, 11, 0, 0, 0. K2 không có query riêng; cả hai RUN `deactivated = 0`. |
| Bước 2b `trg_version`, metrics | ghi nhận | `trg_version = 1`. Metrics chưa có trong paste. |
| Bước 2c RUN lần 2 | 0/0/0, không có version mới | 2026-10-25: inserted 0, updated 0, deactivated 0, `trg_version` vẫn 1. |
| Bước 3 multi_lang | FAILED vì đầu vào rỗng; 0 dòng | 2026-10-25 17:34: FAILED, `Đầu vào bắt buộc rỗng: slv_enr_poi_info_multi_lang`. Đúng D-SRV-23. Số dòng đích chưa có trong paste. |
| Bước 4 NB_00 PLAN | 2 node, không lỗi, không ghi | 2026-10-25 19:13: `status=PLAN`. Log `PL_VV_TRANS_SLV_TO_GLD_30P`: 2 node, 6 cạnh, 6 Dirty Edge, 2 ứng viên `gld_srv_poi_info` và `gld_srv_poi_multi_lang`. WARN nhịp đã chấp nhận. Lần 19:06 fail vì tên `TRANSFORM` thì bỏ. |
| Bước 5 Counter | chỉ `None` (65) | 2026-10-25: `Counter({None: 65})`. |
| L2 khoá sau các bước | `locked = false` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| L3 watermark cạnh | không đổi | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| L4 `ctrl_log_run` sau PLAN | không đổi | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| Kết luận | PASS / FAIL kèm bước fail | PASS các bước 0–5. K3 không có `count(*)` riêng; multi_lang FAILED trước MERGE và không có lần ghi SUCCESS. B1, B3, B5 history, L2–L4 không có query riêng. |
