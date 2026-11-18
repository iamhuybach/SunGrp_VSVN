# Runtime runbook: 20261117-pipeline-precheck-flows

Runbook này do người dùng chạy trên Fabric DEV. Tác giả chưa chạy bước nào trên Fabric, nên mọi kết quả ở mục cuối đều để trống cho người chạy ghi.

## Phạm vi và môi trường

**Phạm vi.** Kiểm tra ba pipeline có pre-check, theo sáu case C1–C6 của architecture §16:

| Pipeline | Vai trò | Notebook gọi trong nhánh có việc |
|---|---|---|
| `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` | Extract bốn nguồn bronze, mỗi nguồn một `Wave_*` chạy tuần tự | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, `NB_EXTRACT_CMS_CDC_BRZ_TO_SLV`, `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` |
| `PL_VV_TRANS_SLV_TO_ENR_15M` | Gate SQL rồi orchestrator ENR | `NB_00_ORCHES_SLV_TO_ENR` (activity `NB_00_ORCHES_SLV_TO_ENR_15P`) |
| `PL_VV_TRANS_SLV_TO_GLD_30M` (mới) | Gate SQL rồi orchestrator GLD | `NB_00_ORCHES_SLV_TO_GLD` (activity `NB_00_ORCHES_SLV_TO_GLD_30M`) |

Cả ba pipeline có `concurrency = 1`. Thứ tự nguồn trong FL_00 là `partner_raw_data` (1), `brz_3rd_crawler_poi_stream` (2), `cms_raw_data` (3), `brz_enrichment_result` (4).

**Môi trường.**

- Workspace Fabric DEV: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace DEV>`.
- Capacity: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên capacity DEV>`. Architecture nhắc F16 ở rủi ro R3; hãy xác nhận SKU thực tế.
- Lakehouse: `lh_vv_bronze`, `lh_vv_ctrl`, `lh_vv_silver`.
- Bảng control: `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`, `ctrl_mng_watermark`, `ctrl_log_run`.
- Commit chứa ba file JSON đã merge: `<CẦN NGƯỜI DÙNG CUNG CẤP: commit sau khi merge>`. Lúc viết runbook, các thay đổi còn nằm ở working tree trên `main`, chưa commit.

**Quy ước truy vấn.** Mọi truy vấn kiểm tra chạy trên SQL analytics endpoint, database `lh_vv_ctrl`, cú pháp T-SQL, chỉ đọc, tối đa 50 dòng. Các truy vấn chỉ đọc bảng control và không chứa dữ liệu cá nhân. Thời gian trong `ctrl_log_run` là UTC. SQL endpoint có thể đồng bộ trễ so với bảng Delta; khi kết quả chưa thấy dòng mới, chờ rồi chạy lại truy vấn và ghi độ trễ.

**Không làm trong runbook này.** Không bật schedule trước khi C1–C6 đều đạt. Không sửa seed `ctrl`. Không chép GUID nào vào runbook hay vào ghi chú kết quả.

## Điều kiện tiên quyết

Làm theo thứ tự. Dừng lại nếu một mục chưa đạt.

1. **Shortcut bronze.** Trong `lh_vv_bronze` có ba shortcut, mỗi shortcut có thư mục `_delta_log`:
   - `Files/_delta_src/brz_3rd_crawler_poi_stream`
   - `Files/_delta_src/cms_raw_data`
   - `Files/_delta_src/brz_enrichment_result`

   `GM_DeltaLog` cũng đọc `Files/_delta_src/partner_raw_data/_delta_log`; xác nhận thư mục này còn đó.
2. **Dòng watermark.** Mỗi nguồn có đúng một dòng `wm_transform_<src_tbl>` với `trg_tbl IS NULL` (truy vấn B2 ở mục baseline): `wm_transform_partner_raw_data`, `wm_transform_brz_3rd_crawler_poi_stream`, `wm_transform_cms_raw_data`, `wm_transform_brz_enrichment_result`.
3. **Publish notebook.** Bốn notebook extract, `NB_00_ORCHES_SLV_TO_ENR` và `NB_00_ORCHES_SLV_TO_GLD` đã publish. Hai lib `NB_LIB_EXTRACT_RAWDATA` và `NB_LIB_TRANSFORM_SLV_GLD` nằm cùng workspace.
4. **Nạp lần đầu bằng tay cho ba nguồn mới.** Chạy tay từng notebook với giá trị trong parameter cell, trong đó `allow_full_scan = True`. Đây là bước ghi dữ liệu.

   | Notebook | `src_tbl` | `allow_full_scan` | `max_parallel` | Tham số riêng |
   |---|---|---|---|---|
   | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` | `brz_3rd_crawler_poi_stream` | `True` | `12` | `sources = "google"`, `doc_key_column = "poi_id"`, `state_key = "doc"` |
   | `NB_EXTRACT_CMS_CDC_BRZ_TO_SLV` | `cms_raw_data` | `True` | `4` | `sources = "strapi_blog,strapi_destination,strapi_news,strapi_ph_promotion_article"` |
   | `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` | `brz_enrichment_result` | `True` | `2` | không có |

   Tham số chung của cả ba khi chạy tay: `pl_name = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"`, `run_id = ""`, `src_schema = "lh_vv_bronze.dbo"`, `max_retries = 1`, `table_filter = ""`, `full_reload = False`, `dry_run = False`, `stop_on_failure = False`, `cast_null_policy = "FAIL"`, `running_timeout_minutes = 780`.

   Đạt khi dòng watermark của nguồn có `last_src_version` khác NULL và `status = SUCCESS`. Nếu bỏ bước này, pre-check trả `FIRST_RUN`, pipeline gọi notebook với `allow_full_scan = false` và notebook báo lỗi.
5. **Import ba pipeline** từ ba file JSON của commit đã merge.
6. **Bind tham số.** Không ghi GUID vào runbook.

   | Pipeline | Tham số | Giá trị |
   |---|---|---|
   | FL_00 | `conn_lh_vv_bronze_by_sqlep` (tham số template) | `<CẦN NGƯỜI DÙNG CUNG CẤP: connection tới SQL endpoint>` |
   | FL_00 | `lh_vv_ctrl`, `lh_vv_bronze` (tham số template, artifact id lakehouse) | `<CẦN NGƯỜI DÙNG CUNG CẤP: id lakehouse lh_vv_ctrl và lh_vv_bronze>` |
   | FL_00 | `p_pipeline_code` | `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` (mặc định, giữ nguyên) |
   | FL_00 | `nb_extract_3p_id` | `<CẦN NGƯỜI DÙNG CUNG CẤP: id notebook NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV>` |
   | FL_00 | `nb_extract_cms_id` | `<CẦN NGƯỜI DÙNG CUNG CẤP: id notebook NB_EXTRACT_CMS_CDC_BRZ_TO_SLV>` |
   | FL_00 | `nb_extract_enr_id` | `<CẦN NGƯỜI DÙNG CUNG CẤP: id notebook NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV>` |
   | FL_00 | `workspace_id` | `<CẦN NGƯỜI DÙNG CUNG CẤP: id workspace DEV>` |
   | ENR_15M | `conn_lh_vv_bronze_by_sqlep` | `<CẦN NGƯỜI DÙNG CUNG CẤP: connection tới SQL endpoint>` |
   | ENR_15M | `nb_orches_id` | `<CẦN NGƯỜI DÙNG CUNG CẤP: id notebook NB_00_ORCHES_SLV_TO_ENR>` |
   | ENR_15M | `workspace_id` | `<CẦN NGƯỜI DÙNG CUNG CẤP: id workspace DEV>` |
   | ENR_15M | `p_force_run` | `false` (mặc định) |
   | ENR_15M | `p_max_idle_min` | `0` (mặc định) |
   | GLD_30M | `conn_lh_vv_bronze_by_sqlep` | `<CẦN NGƯỜI DÙNG CUNG CẤP: connection tới SQL endpoint>` |
   | GLD_30M | `nb_orches_id` | `<CẦN NGƯỜI DÙNG CUNG CẤP: id notebook NB_00_ORCHES_SLV_TO_GLD>` |
   | GLD_30M | `workspace_id` | `<CẦN NGƯỜI DÙNG CUNG CẤP: id workspace DEV>` |
   | GLD_30M | `p_force_run` | `false` (mặc định) |
   | GLD_30M | `p_max_idle_min` | `0` (mặc định) |

   Activity partner `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` giữ nguyên notebook id và workspace id đang nằm trong JSON của FL_00; không sửa, không chép ra ngoài.
7. **Tham số activity đã cố định trong JSON** (chỉ đối chiếu sau import, không sửa):

   | Activity | Timeout | `retry` | Tham số truyền vào notebook |
   |---|---|---|---|
   | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` | `0.12:00:00` | 0 | `pl_name = PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`, `run_id = ""`, `src_schema = lh_vv_bronze.dbo`, `src_tbl = partner_raw_data`, `overlap_minutes = 10`, `allow_full_scan = false`, `max_parallel = 12`, `max_retries = 1`, `table_filter = ""`, `full_reload = false`, `dry_run = false`, `stop_on_failure = false`, `cast_null_policy = FAIL`, `running_timeout_minutes = 60` |
   | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` | `0.00:59:00` | 0 | `run_id = @pipeline().RunId`, `src_tbl = brz_3rd_crawler_poi_stream`, `allow_full_scan = false`, `max_parallel = 12`, `max_retries = 1`, `running_timeout_minutes = 60`, `sources = google`, `doc_key_column = poi_id`, `state_key = doc`; còn lại như partner, không có `overlap_minutes` |
   | `NB_EXTRACT_CMS_CDC_BRZ_TO_SLV` | `0.00:59:00` | 0 | `run_id = @pipeline().RunId`, `src_tbl = cms_raw_data`, `allow_full_scan = false`, `max_parallel = 4`, `max_retries = 1`, `running_timeout_minutes = 60`, `sources = strapi_blog,strapi_destination,strapi_news,strapi_ph_promotion_article` |
   | `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` | `0.00:59:00` | 0 | `run_id = @pipeline().RunId`, `src_tbl = brz_enrichment_result`, `allow_full_scan = false`, `max_parallel = 2`, `max_retries = 1`, `running_timeout_minutes = 60`; không truyền `sources` |
   | `NB_00_ORCHES_SLV_TO_ENR_15P` | `0.00:32:00` | 0 | `p_pl_name = @pipeline().Pipeline`, `p_run_id = @pipeline().RunId`, `p_mode = RUN`, `p_max_parallel = 2`, `p_node_timeout_min = 15`, `p_dag_timeout_min = 25`, `p_lock_timeout_min = 35`, `p_force_nodes = ""`, `p_history_limit = 1000`, `p_non_data_ops = ""` |
   | `NB_00_ORCHES_SLV_TO_GLD_30M` | `0.00:52:00` | 0 | `p_pl_name = @pipeline().Pipeline`, `p_run_id = @pipeline().RunId`, `p_mode = RUN`, `p_max_parallel = 3`, `p_node_timeout_min = 20`, `p_dag_timeout_min = 45`, `p_lock_timeout_min = 90`, `p_force_nodes = ""`, `p_history_limit = 1000`, `p_non_data_ops = ""` |
   | `Get_Flow_Gate_ENR`, `Get_Flow_Gate_GLD` | `0.00:05:00` | 1 (30 giây) | Script chỉ đọc, database `lh_vv_ctrl` |

8. **Schedule.** Cả ba pipeline để schedule tắt trong suốt runbook.

## Baseline trước khi chạy

Chạy các truy vấn sau và lưu kết quả trước case đầu tiên. Chạy lại B2, B3, B5 trước mỗi case để có mốc so sánh.

**B1. Cấu hình ba pipeline.** Kỳ vọng FL_00 có đủ bốn `src_tbl` active; ENR và GLD có dòng active.

```sql
SELECT TOP 50 pl_name, src_tbl, COUNT(*) AS so_dong
FROM dbo.ctrl_mng_pipeline_config
WHERE is_active = 1
  AND pl_name IN ('PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00', 'PL_VV_TRANS_SLV_TO_ENR_15M', 'PL_VV_TRANS_SLV_TO_GLD_30M')
GROUP BY pl_name, src_tbl
ORDER BY pl_name, src_tbl;
```

**B2. Watermark nguồn và khoá luồng.** Kỳ vọng bốn dòng `wm_transform_*` có `last_src_version` khác NULL, `lock_exec_id` NULL.

```sql
SELECT TOP 50 watermark_id, src_tbl, status, last_src_version, last_success_at, last_run_id,
       lock_exec_id, lock_at, updated_at
FROM dbo.ctrl_mng_watermark
WHERE watermark_id IN ('wm_transform_partner_raw_data', 'wm_transform_brz_3rd_crawler_poi_stream',
                       'wm_transform_cms_raw_data', 'wm_transform_brz_enrichment_result',
                       'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M', 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M')
ORDER BY watermark_id;
```

**B3. Các run gần nhất.**

```sql
SELECT TOP 50 exec_id, run_id, pl_name, nb_name, src_tbl, run_mode, status, started_at, ended_at, duration_ms,
       src_version_from, src_version_to, read_mode
FROM dbo.ctrl_log_run
WHERE pl_name IN ('PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00', 'PL_VV_TRANS_SLV_TO_ENR_15M', 'PL_VV_TRANS_SLV_TO_GLD_30M')
ORDER BY started_at DESC;
```

**B4. Commit bronze so với watermark.** Trong Lakehouse explorer của `lh_vv_bronze`, mở `Files/_delta_src/<src_tbl>/_delta_log` cho từng nguồn và ghi tên file `.json` lớn nhất (tên dài 25 ký tự: 20 chữ số và `.json`). Nguồn "không có việc" khi không có file nào có tên lớn hơn `last_src_version` đệm đủ 20 chữ số cộng `.json`.

**B5. Mốc đếm log.** Dùng để chứng minh không có dòng mới.

```sql
SELECT pl_name, COUNT(*) AS so_dong, MAX(started_at) AS started_at_moi_nhat
FROM dbo.ctrl_log_run
WHERE pl_name IN ('PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00', 'PL_VV_TRANS_SLV_TO_ENR_15M', 'PL_VV_TRANS_SLV_TO_GLD_30M')
GROUP BY pl_name;
```

**B6. Xem trước gate (chỉ đọc).** Đây là câu SQL của `Get_Flow_Gate_*` với `p_max_idle_min = 0`. Chạy một lần với `PL_VV_TRANS_SLV_TO_ENR_15M`, một lần thay cả hai chỗ bằng `PL_VV_TRANS_SLV_TO_GLD_30M`.

```sql
WITH up_pl AS (
    SELECT DISTINCT p.pl_name
    FROM dbo.ctrl_mng_pipeline_config AS m
    INNER JOIN dbo.ctrl_mng_pipeline_config AS p
        ON p.trg_schema = m.src_schema AND p.trg_tbl = m.src_tbl
    WHERE m.pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15M'
      AND m.is_active = 1 AND p.is_active = 1 AND p.pl_name <> m.pl_name
),
me AS (
    SELECT MAX(CASE WHEN status IN ('SUCCESS', 'NO_DATA') THEN started_at END) AS ok_started_at,
           MAX(started_at) AS last_started_at
    FROM dbo.ctrl_log_run
    WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15M' AND run_mode = 'RUN' AND status <> 'SKIPPED_CONCURRENT'
),
up AS (
    SELECT MAX(r.ended_at) AS up_at
    FROM dbo.ctrl_log_run AS r
    INNER JOIN up_pl AS u ON u.pl_name = r.pl_name
    WHERE r.status NOT IN ('NO_DATA', 'SKIPPED_CONCURRENT', 'RUNNING')
      AND COALESCE(r.run_mode, '') <> 'DRY_RUN' AND r.ended_at IS NOT NULL
)
SELECT CASE
           WHEN me.ok_started_at IS NULL THEN 'FIRST_RUN'
           WHEN me.last_started_at > me.ok_started_at THEN 'LAST_RUN_NOT_OK'
           WHEN up.up_at >= DATEADD(MINUTE, -2, me.ok_started_at) THEN 'UPSTREAM_CHANGED'
           ELSE 'NO_DATA'
       END AS gate_reason,
       me.ok_started_at, me.last_started_at, up.up_at
FROM me CROSS JOIN up;
```

**B7. Capacity.** Trong Fabric Capacity Metrics app, ghi mức CU và trạng thái throttling của capacity DEV trước khi bắt đầu.

## Các bước thực hiện

Mỗi lần chạy pipeline, ghi lại `RunId` của pipeline và giờ bắt đầu (UTC). Chạy bằng nút Run thủ công; schedule vẫn tắt.

### C1 — Extract không có dữ liệu

1. Xác nhận bằng B2 và B4: bốn watermark đã hiện hành, không có commit bronze mới. Ghi B5.
2. Chạy `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` với tham số mặc định đã bind.
3. Mở `ForEach_PARTNER`, `ForEach_3P`, `ForEach_CMS`, `ForEach_ENRICH`. Vòng nào không có data thì đọc `v_msg_skip` ở `Set_Msg_Skip_<nguồn>`.

### C2 — Extract có dữ liệu

1. Chọn một nguồn: `<CẦN NGƯỜI DÙNG CUNG CẤP: nguồn dùng cho C2>`. Nên chọn một trong ba nguồn mới (`brz_3rd_crawler_poi_stream`, `cms_raw_data`, `brz_enrichment_result`), vì chỉ ba activity mới truyền `run_id = @pipeline().RunId`. Activity partner truyền `run_id` rỗng, nên dòng log partner có `run_id = exec_id` và không khớp `RunId` của pipeline.
2. Tạo đúng một commit mới trên bảng bronze của nguồn đó: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách tạo một commit mới trên nguồn đã chọn ở DEV>`. Xác nhận bằng B4 rằng có một file `_delta_log` mới trên nguồn này và không có file mới ở ba nguồn kia.
3. Chạy FL_00. Ghi `RunId`.
4. Đọc `v_msg` ở `Set_Msg_Run` của nguồn đã chọn và `v_msg_skip` của ba nguồn còn lại.
5. Chạy FL_00 lần hai ngay sau khi lần một xong (bước này cũng là phần idempotency).

### C3 — Transform không có dữ liệu

1. Chạy B6 cho ENR. Nếu kết quả khác `NO_DATA` (ví dụ `FIRST_RUN`, `LAST_RUN_NOT_OK`, `UPSTREAM_CHANGED`), chạy `PL_VV_TRANS_SLV_TO_ENR_15M` một lần với `p_force_run = false`, `p_max_idle_min = 0`, chờ notebook kết thúc `SUCCESS` hoặc `NO_DATA`, rồi chạy lại B6 cho tới khi ra `NO_DATA`. Ghi số lần chạy chuẩn bị này; chúng không tính vào C3.
2. Không chạy FL_00 trong lúc làm C3.
3. Chạy `PL_VV_TRANS_SLV_TO_ENR_15M` với `p_force_run = false`, `p_max_idle_min = 0`. Đọc output của `Get_Flow_Gate_ENR` và `v_msg_skip` ở `Set_Msg_Skip_ENR`.
4. Lặp lại bước 1–3 cho `PL_VV_TRANS_SLV_TO_GLD_30M` (`Get_Flow_Gate_GLD`, `Set_Msg_Skip_GLD`). Upstream của GLD lấy từ config và có thể gồm cả luồng khác ngoài FL_00; ghi `up_at` gate trả về.

### C4 — Transform có dữ liệu

1. Làm sau C2, hoặc lặp lại C2 bước 1–3 để có một run extract mới không phải `NO_DATA`. Ghi `ended_at` của dòng extract đó (truy vấn K2).
2. Chạy `PL_VV_TRANS_SLV_TO_ENR_15M` với `p_force_run = false`, `p_max_idle_min = 0`. Ghi giờ bắt đầu của `Get_Flow_Gate_ENR`, `gate_reason` và `up_at`.
3. Nếu gate trả `NO_DATA` vì SQL endpoint chưa thấy run extract, ghi lại, chờ, rồi chạy lại cho tới khi thấy `UPSTREAM_CHANGED`. Độ trễ cần ghi là khoảng từ `ended_at` của extract tới giờ bắt đầu của lần gate đầu tiên trả `UPSTREAM_CHANGED`.
4. Chờ `NB_00_ORCHES_SLV_TO_ENR_15P` xong. Chạy ENR thêm một lần và, nếu notebook vẫn chạy, thêm một lần nữa.
5. Chạy ENR một lần với `p_force_run = true`, `p_max_idle_min = 0`. Đọc `v_msg` ở `Set_Msg_Run_ENR`. Sau lần này, các lần chạy tiếp theo dùng lại `p_force_run = false`.
6. Chạy `PL_VV_TRANS_SLV_TO_GLD_30M` một lần với `p_force_run = false` và ghi `gate_reason`.

### C5 — Capacity

1. Ghi giờ bắt đầu cửa sổ đo (UTC).
2. Tạo một commit mới như C2 bước 2, chạy FL_00, và trong lúc notebook extract còn chạy thì chạy ENR với `p_force_run = true` để hai phiên Spark chồng nhau. Có thể chạy thêm GLD với `p_force_run = true` để kiểm tra ba phiên đồng thời (rủi ro R3); ghi rõ có làm hay không.
3. Sau khi các run xong, để hệ thống nghỉ đủ một giờ. Trong giờ nghỉ, chạy tay mỗi pipeline theo nhịp dự kiến để đo chi phí của run chỉ có pre-check: `<CẦN NGƯỜI DÙNG CUNG CẤP: số lần chạy tay mỗi pipeline trong giờ nghỉ>`.
4. Mở Capacity Metrics app cho cửa sổ đo và ghi số liệu theo mục kiểm tra kết quả.

### C6 — Lỗi và chạy chồng

1. **Id rỗng.** Chạy FL_00 với `nb_extract_cms_id` để rỗng, ba tham số bind còn lại giữ nguyên. Chạy ENR với `nb_orches_id` để rỗng. Sau khi ghi kết quả, bind lại giá trị đúng.
2. **Notebook lỗi.** Ép một notebook extract lỗi: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách ép lỗi và nguồn bị ép lỗi>`. Nguồn bị ép lỗi phải đứng trước ít nhất một nguồn khác trong thứ tự chạy (không chọn `brz_enrichment_result`), và nguồn đó phải có commit mới để notebook được gọi. Nên tạo thêm một commit mới trên một nguồn đứng sau để thấy notebook của nguồn sau vẫn chạy. Chạy FL_00 và ghi trạng thái từng vòng lặp. Sau case này, gỡ nguyên nhân lỗi và kiểm tra B2: `lock_exec_id` của nguồn đó phải NULL trước khi chạy tiếp.
3. **Trigger thứ hai.** Chạy ENR với `p_force_run = true`. Khi `NB_00_ORCHES_SLV_TO_ENR_15P` đang chạy, bấm Run lần hai với `p_force_run = false`. Ghi Fabric xếp hàng hay từ chối lần hai. Có thể lặp lại trên FL_00 trong lúc một notebook extract đang chạy.

## Kiểm tra kết quả

**K1. C1 đạt khi** có đủ bốn giá trị `v_msg_skip` dạng `SKIP | lh_vv_bronze.dbo.<src_tbl> | reason=NO_NEW_COMMITS | last_src_version=<n> | new_commits=0 | since=<...>`; không activity notebook nào chạy; B5 không đổi số dòng và `started_at_moi_nhat`; Monitoring hub không có phiên Spark mới trong khoảng thời gian chạy.

**K2. C2 đạt khi** chỉ notebook của nguồn đã chọn chạy, `v_msg` của nguồn đó có `reason=NEW_COMMITS | ... | new_commits=1`, ba nguồn kia có `SKIP`, và truy vấn sau trả đúng một dòng có `src_tbl` là nguồn đã chọn:

```sql
SELECT TOP 50 exec_id, run_id, pl_name, nb_name, src_tbl, run_mode, status, started_at, ended_at,
       src_version_from, src_version_to, read_mode
FROM dbo.ctrl_log_run
WHERE run_id = '<RunId của pipeline ở C2>'
ORDER BY started_at DESC;
```

Lần chạy thứ hai phải có bốn `SKIP` và không thêm dòng log.

**K3. C3 đạt khi** output của `Get_Flow_Gate_ENR` có `gate_reason = NO_DATA`, `v_msg_skip` là `SKIP | PL_VV_TRANS_SLV_TO_ENR_15M | reason=NO_DATA | last_ok_started_at=<...> | upstream_at=<...>`, notebook không chạy, B5 không đổi cho ENR. Tương tự cho GLD với `Get_Flow_Gate_GLD` và tên `PL_VV_TRANS_SLV_TO_GLD_30M`.

**K4. C4 đạt khi** lần ENR đầu tiên sau extract có `gate_reason = UPSTREAM_CHANGED` và notebook chạy. Lần kế tiếp hoặc skip với `NO_DATA`, hoặc chạy thêm đúng một lần mà dòng `ctrl_log_run` của lần đó có `status = NO_DATA`, rồi lần sau nữa skip. Lần chạy thêm này do biên 2 phút của gate và là hành vi được chấp nhận. Lần `p_force_run = true` phải có `v_msg` bắt đầu bằng `RUN | PL_VV_TRANS_SLV_TO_ENR_15M | reason=FORCE` và notebook khởi động. Nếu biểu thức `If_HasWork_ENR` lỗi kiểu dữ liệu với tham số bool, ghi là không đạt (rủi ro R5). Kiểm tra log:

```sql
SELECT TOP 50 exec_id, run_id, pl_name, run_mode, status, started_at, ended_at, duration_ms,
       tbl_total_count, tbl_success_count, tbl_failed_count, tbl_no_data_count
FROM dbo.ctrl_log_run
WHERE pl_name IN ('PL_VV_TRANS_SLV_TO_ENR_15M', 'PL_VV_TRANS_SLV_TO_GLD_30M')
ORDER BY started_at DESC;
```

**K5. C5 đạt khi** Capacity Metrics không ghi nhận throttling trong cửa sổ đo. Ghi CU của các thao tác pipeline (item `PL_VV_*`) và CU của Spark (các notebook) cho giờ chồng và cho giờ nghỉ. Runbook không đưa ra ngưỡng CU; chỉ ghi số đo.

**K6. C6 đạt khi:**

- Id rỗng: FL_00 lỗi ở `Fail_Bad_Extract_Binding`, ENR lỗi ở `Fail_Bad_Binding`, mã lỗi `BAD_NOTEBOOK_BINDING`; `ForEach_PARTNER` và `Get_Flow_Gate_ENR` không chạy; B5 không đổi.
- Notebook lỗi: `Wave` của nguồn đó Failed, `Set_Failed_ForEach_<nguồn>` ghi `v_any_failed = true`, các `Wave` sau vẫn chạy vì phụ thuộc `Completed`. Sau `Wave_ENRICH`, `If_Any_Failed` chạy `Fail_Extract_Waves` và pipeline kết thúc Failed. `last_src_version` của nguồn lỗi không đổi so với B2.
- Trigger thứ hai: không có notebook thứ hai khởi động trong lúc run đầu còn chạy. Nếu Fabric xếp hàng, run thứ hai chạy sau và tự đánh giá lại trạng thái; ghi `gate_reason` của nó. Nếu có dòng `SKIPPED_CONCURRENT` trong `ctrl_log_run`, tức notebook thứ hai đã khởi động: ghi là không đạt.

## Chạy lại để kiểm tra idempotency

1. Sau C1, chạy FL_00 thêm một lần. Kỳ vọng vẫn bốn `SKIP`, B5 không đổi.
2. Sau C2, lần chạy thứ hai (C2 bước 5) phải skip cả bốn nguồn. Kiểm tra B2: `last_src_version` của nguồn đã chọn tăng đúng một lần và không đổi sau lần chạy lại.
3. Sau C3, chạy ENR và GLD thêm mỗi pipeline một lần. Kỳ vọng `NO_DATA`, không có dòng log mới.
4. Sau C4, khi ENR đã skip, chạy thêm một lần nữa. Kỳ vọng vẫn skip.
5. Kiểm tra không có run trùng cho cùng một `run_id` pipeline:

```sql
SELECT TOP 50 run_id, pl_name, COUNT(*) AS so_dong
FROM dbo.ctrl_log_run
WHERE pl_name IN ('PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00', 'PL_VV_TRANS_SLV_TO_ENR_15M', 'PL_VV_TRANS_SLV_TO_GLD_30M')
  AND started_at >= '<giờ bắt đầu runbook, UTC>'
GROUP BY run_id, pl_name
HAVING COUNT(*) > 1
ORDER BY so_dong DESC;
```

Với ENR và GLD, kỳ vọng 0 dòng. Với FL_00, một `run_id` có thể có nhiều dòng khi nhiều nguồn mới cùng có việc trong một run; mỗi `src_tbl` chỉ được có một dòng.

## Kiểm tra log và watermark

**L1. Watermark sau mỗi case.** Chạy lại B2. Kỳ vọng: run skip không đổi dòng nào; run extract thành công tăng `last_src_version`, cập nhật `last_success_at`, `status = SUCCESS`, `lock_exec_id` NULL; run extract lỗi giữ nguyên `last_src_version`. Hai dòng `wm_flow__*` có `lock_exec_id` NULL khi không còn run nào chạy.

**L2. Run lỗi hoặc treo.**

```sql
SELECT TOP 50 exec_id, run_id, pl_name, nb_name, src_tbl, status, started_at, ended_at,
       LEFT(error_message, 300) AS error_message
FROM dbo.ctrl_log_run
WHERE pl_name IN ('PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00', 'PL_VV_TRANS_SLV_TO_ENR_15M', 'PL_VV_TRANS_SLV_TO_GLD_30M')
  AND status IN ('FAILED', 'PARTIAL_FAILED', 'RUNNING', 'ABANDONED', 'SKIPPED_CONCURRENT')
  AND started_at >= '<giờ bắt đầu runbook, UTC>'
ORDER BY started_at DESC;
```

Kỳ vọng chỉ có các dòng do C6 tạo ra.

**L3. Kiểm tra stall (rủi ro R1).** So run FL_00 mới nhất đã xong và không phải `NO_DATA` với run tốt mới nhất của từng luồng transform.

```sql
SELECT 'FL_00' AS luong, MAX(ended_at) AS moc
FROM dbo.ctrl_log_run
WHERE pl_name = 'PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00'
  AND status NOT IN ('NO_DATA', 'SKIPPED_CONCURRENT', 'RUNNING')
  AND COALESCE(run_mode, '') <> 'DRY_RUN' AND ended_at IS NOT NULL
UNION ALL
SELECT pl_name, MAX(started_at)
FROM dbo.ctrl_log_run
WHERE pl_name IN ('PL_VV_TRANS_SLV_TO_ENR_15M', 'PL_VV_TRANS_SLV_TO_GLD_30M')
  AND run_mode = 'RUN' AND status IN ('SUCCESS', 'NO_DATA')
GROUP BY pl_name;
```

Stall là khi mốc FL_00 cũ hơn hai nhịp (30 phút với ENR, 60 phút với GLD) mà luồng transform không có run tốt nào bắt đầu sau mốc đó. Với `p_max_idle_min = 0`, luồng nghỉ không tự mở Spark, nên truy vấn này là cách phát hiện chính.

**L4. Run skip không ghi log.** Một lần skip của transform không tạo dòng `ctrl_log_run`. Bằng chứng skip chỉ có trong monitoring của pipeline (`v_msg_skip`); hãy chụp lại giá trị này cho C1 và C3.

## Rollback và forward recovery

**Rollback.** Pipeline không ghi state, nên không cần sửa dữ liệu.

1. Tắt schedule của cả ba pipeline (nếu đã bật).
2. FL_00 và ENR_15M: import lại JSON cũ từ Git commit `9a62b9f`. Lấy file bằng `git show 9a62b9f:pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json` và `git show 9a62b9f:pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json`. Bind lại tham số theo đúng file đó.
3. GLD_30M là pipeline mới: tắt hoặc xoá.
4. Sau rollback, FL_00 bản cũ chỉ gọi notebook partner; ba nguồn mới quay về chạy tay.

**Forward recovery.** Các lệnh `UPDATE` dưới đây ghi vào bảng control, chạy bằng Spark SQL trong notebook, và chỉ chạy khi người dùng đã xác nhận không còn run nào đang chạy.

- **Transform bị stall:** chạy pipeline một lần với `p_force_run = true`, hoặc chạy tay `NB_00`. Khi chạy tay `NB_00_ORCHES_SLV_TO_GLD`, phải đặt `p_pl_name = "PL_VV_TRANS_SLV_TO_GLD_30M"`, vì giá trị mặc định trong parameter cell là `PL_VV_TRANSFORM_SLV_TO_GLD_1H`. `NB_00_ORCHES_SLV_TO_ENR` có mặc định `PL_VV_TRANS_SLV_TO_ENR_15M`.
- **Gate trả `LAST_RUN_NOT_OK` liên tục:** luồng sẽ chạy lại mỗi nhịp cho tới khi có một run `SUCCESS` hoặc `NO_DATA`. Xử lý nguyên nhân lỗi của node rồi để run kế tiếp tự chạy.
- **Extract treo khoá sau khi activity bị huỷ:** các lần sau của nguồn đó lỗi `SKIPPED_CONCURRENT` tối đa 60 phút. Chờ hết hạn, hoặc nhả khoá theo `CTRL_TABLES_CONTEXT.md` §4:

  ```sql
  UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark SET lock_exec_id = NULL, lock_at = NULL
  WHERE watermark_id = '<wm_transform_...>' AND lock_exec_id = '<exec_id trong lỗi SKIPPED_CONCURRENT>';
  ```

- **Extract bị stall sau khi raw bị tạo lại** (pre-check không thấy file nào lớn hơn version đang lưu và skip mãi): reset dòng watermark theo §4, rồi chạy tay notebook của nguồn đó với `allow_full_scan = True`.

  ```sql
  UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark
  SET watermark_value = NULL, last_success_at = NULL, last_src_version = NULL, last_src_table_id = NULL,
      lock_exec_id = NULL, lock_at = NULL, status = 'INITIALIZED'
  WHERE watermark_id = '<wm_transform_...>';
  ```

  Không để pipeline chạy giữa lúc reset và lúc nạp tay: `last_src_version` NULL làm pre-check trả `FIRST_RUN`, pipeline gọi notebook với `allow_full_scan = false` và notebook lỗi.
- **Nguồn có dòng config nhưng thiếu dòng watermark:** notebook báo lỗi rõ ràng. Tạo dòng `wm_transform_<src_tbl>` theo seed rồi nạp lần đầu như mục điều kiện tiên quyết.

**Bật schedule.** Chỉ bật sau khi C1–C6 đều đạt, bật sau cùng và đặt lệch giờ giữa ba pipeline: `<CẦN NGƯỜI DÙNG CUNG CẤP: nhịp của FL_00 và phút lệch của từng pipeline>`.

## Kết quả người dùng ghi nhận

Người chạy điền bảng này. Không ghi GUID notebook hay workspace; `RunId` của pipeline thì được ghi.

| Mục | Giá trị ghi nhận |
|---|---|
| Người chạy, ngày giờ (UTC) | |
| Commit đã import | |
| Workspace và capacity DEV | |
| Điều kiện tiên quyết 1–8 | Đạt / Không đạt, ghi chú |
| Baseline B1–B7 | Đã lưu ở đâu |

| Case | RunId pipeline | Kết quả quan sát | Đạt / Không đạt |
|---|---|---|---|
| C1 extract không dữ liệu | | Bốn `v_msg_skip`; số dòng log trước và sau; phiên Spark | |
| C2 extract có dữ liệu | | Nguồn đã chọn; `v_msg`; số dòng theo `run_id`; lần hai skip | |
| C3 transform không dữ liệu (ENR) | | `gate_reason`, `ok_started_at`, `up_at` | |
| C3 transform không dữ liệu (GLD) | | `gate_reason`, `ok_started_at`, `up_at` | |
| C4 transform có dữ liệu | | `ended_at` của extract; giờ gate thấy `UPSTREAM_CHANGED`; độ trễ (phút); số lần chạy thêm với `NO_DATA`; kết quả `p_force_run = true` | |
| C5 capacity | | Throttling có hay không; CU pipeline và CU Spark giờ chồng; CU pipeline và CU Spark giờ nghỉ; số phiên Spark đồng thời | |
| C6 id rỗng | | Activity lỗi, mã lỗi, có activity nào khác chạy không | |
| C6 notebook lỗi | | Nguồn bị ép lỗi, cách ép; trạng thái các vòng lặp sau; trạng thái pipeline | |
| C6 trigger thứ hai | | Xếp hàng hay từ chối; có notebook thứ hai không | |
| Idempotency 1–5 | | | |
| Log và watermark L1–L4 | | | |

| Quyết định sau khi chạy | Giá trị |
|---|---|
| Giữ `p_max_idle_min = 0` ở DEV hay đổi (rủi ro R1) | |
| Ba phiên Spark đồng thời có chấp nhận được không (rủi ro R3) | |
| Hành vi ForEach sau vòng lặp lỗi, `concurrency = 1`, tham số bool (rủi ro R5) | |
| Schedule đã bật, giờ lệch | |
| Có rollback hay forward recovery không, lý do | |
