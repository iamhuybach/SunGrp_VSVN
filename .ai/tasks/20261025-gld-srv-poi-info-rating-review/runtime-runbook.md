# Runtime runbook — 20261025-gld-srv-poi-info-rating-review (Fabric DEV)

## Phạm vi và môi trường

- Môi trường: Fabric DEV, workspace `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>`. Các lakehouse là `lh_vv_ctrl`, `lh_vv_silver`, `lh_vv_gold`, tất cả dùng schema `dbo`.
- Mục tiêu: thêm 3 cột `rating_overall` DECIMAL(4,2), `rating_count` INT, `review_count` INT vào `lh_vv_gold.dbo.gld_srv_poi_info`, đặt ngay sau `holiday_exceptions`. Thêm 2 cạnh `PL_VV_TRANS_SLV_TO_GLD_30P` (`slv_3p_poi_rating`, `slv_3p_poi_review` → `gld_srv_poi_info`). Sau đó chạy node `NB_GLD_SRV_POI_INFO` để điền giá trị, chỉ cho dòng Google.
- Notebook liên quan:
  - `NB_CREATE_DDL`: chỉ chạy cell `srvratepy`. Cell này không có cell tham số.
  - `NB_SETUP_INITIAL_DDL`: chạy với `p_apply="false"`, chỉ in kế hoạch và không ghi.
  - `NB_GLD_SRV_POI_INFO`: node, chạy tay.
  - `NB_00_ORCHES_SLV_TO_GLD`: chỉ chạy `PLAN`.
- Khoá luồng dùng chung: `watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P'`, lease 90 phút (`LEASE_MINUTES = 90` trong `srvratepy`, bằng `p_lock_timeout_min` mặc định của NB_00).
- Ngoài phạm vi:
  - Không tạo hay sửa schedule. Luồng GLD_30P vẫn không có lịch.
  - Không chạy NB_00 ở `RUN`.
  - Không chạy lại `srvpoipy`.
  - Không DROP, DELETE hay `UPDATE` ctrl bằng tay.
  - Không sửa code notebook trên DEV.
- Mọi truy vấn kiểm tra đều chỉ đọc. Chỉ các bước "chạy" được đánh dấu mới ghi dữ liệu. Mỗi kết quả lấy tối đa 50 dòng, chỉ gồm số đếm, tên bảng, tên cột, version và trạng thái, không có dữ liệu cá nhân.

## Điều kiện tiên quyết

1. Local test đã pass, gồm `python -m pytest tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py -q` và `python -m pytest -q`. Output pytest đã được lưu vào verification log (bước 4 của architecture).
2. `decision.md` đã ghi quyết định stop 1: đưa 3 file test ngoài `scope.files` vào phạm vi.
3. Không có run nào đang giữ khoá GLD_30P (truy vấn W1 ở mục "Kiểm tra log và watermark"). Điều kiện đạt khi `lock_exec_id IS NULL`, hoặc khi `lock_at` cũ hơn 90 phút và chắc chắn không còn run nào sống. Không tự nhả khoá bằng tay.
4. Không có run GLD_30P nào ở trạng thái `RUNNING` (truy vấn L1).
5. Triển khai cùng lúc 3 notebook `NB_CREATE_DDL`, `NB_SETUP_INITIAL_DDL` và `NB_GLD_SRV_POI_INFO` lên DEV, theo cách `<CẦN NGƯỜI DÙNG CUNG CẤP: cách deploy lên DEV (Git sync / deployment pipeline) và commit được deploy>`. Sau khi deploy, mở notebook trên DEV và xác nhận bằng mắt:
   - Cell cuối của `NB_CREATE_DDL` là `srvratepy` và cell ngay trước nó là `srvratemd`.
   - Cell `srvinfobuild` của `NB_GLD_SRV_POI_INFO` có `RATING_COLS`, và `SPEC.inputs` có 5 vai trò (`entity`, `destination`, `multi_lang`, `rating`, `review`).
6. Chạy `srvratepy` (bước 1) ngay sau khi lấy baseline. Khoảng thời gian giữa lúc deploy và lúc chạy `srvratepy` là an toàn, vì node sẽ dừng bằng ConfigError `spec.inputs lệch config` trước khi ghi. Dù vậy, đừng chạy node trong khoảng này.
7. Cảnh báo cố định: **sau bước 1 không được chạy lại `srvpoipy` trên DEV**. Hợp đồng `gld_srv_poi_info` trong `srvpoipy` vẫn là bản 29 cột, nên cell sẽ dừng an toàn với `lệch cột` / `Cell không tự bật cạnh`. Đây là hành vi đã chấp nhận, cùng mẫu với `enrflagpy` sau `srvpoipy`. Không bao giờ dùng "Run all" trên `NB_CREATE_DDL`.

## Baseline trước khi chạy

Chạy sau khi deploy và trước bước 1. Tất cả đều là truy vấn chỉ đọc. Ghi kết quả vào mục "Kết quả người dùng ghi nhận".

**B0 — mốc log (T0).** Lấy mốc để lọc các dòng log mới:

```sql
SELECT (SELECT max(started_at) FROM lh_vv_ctrl.dbo.ctrl_log_table_run) AS t0_table_run,
       (SELECT max(started_at) FROM lh_vv_ctrl.dbo.ctrl_log_run) AS t0_run
```

**B1 — schema bảng gold.** Kỳ vọng 29 cột, `holiday_exceptions` ở vị trí 25 và `row_hash` ở vị trí 26:

```python
fields = spark.table("lh_vv_gold.dbo.gld_srv_poi_info").schema.fields
print(len(fields))
for i, f in enumerate(fields, 1):
    if 24 <= i <= 32:
        print(i, f.name, f.dataType.simpleString(), f.nullable)
```

**B2 — cạnh (query B2 của task 20261024).** Kỳ vọng 6 dòng: 3 cạnh `gld_srv_poi_multi_lang` và 3 cạnh `gld_srv_poi_info`, mỗi dòng `n = 1`.

```sql
SELECT pl_name, src_schema, src_tbl, trg_tbl, is_active, priority, load_mode, nb_name, count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_schema = 'lh_vv_gold.dbo' AND trg_tbl IN ('gld_srv_poi_multi_lang', 'gld_srv_poi_info')
GROUP BY pl_name, src_schema, src_tbl, trg_tbl, is_active, priority, load_mode, nb_name
ORDER BY trg_tbl, src_tbl
```

**B3 — tổng config.** Kỳ vọng `n = 59`.

```sql
SELECT count(*) AS n FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
```

**B4 — version cuối của bảng gold.** Ghi lại `version` mới nhất. Chỉ chọn 3 cột, không lấy `userName`.

```python
spark.sql("DESCRIBE HISTORY lh_vv_gold.dbo.gld_srv_poi_info LIMIT 5").select("version", "timestamp", "operation").show(truncate=False)
```

**B5 — số dòng live trước thay đổi.** R6 dùng số này làm chuẩn:

```sql
SELECT count(*) AS n_live, count(DISTINCT poi_id) AS n_poi
FROM lh_vv_gold.dbo.gld_srv_poi_info WHERE deleted_at IS NULL
```

**B6 — khoá luồng và watermark cạnh.** Chạy W1 và W2 (mục "Kiểm tra log và watermark") và ghi lại trạng thái hiện tại.

Điểm dừng: nếu B1 khác 29 cột, B2 khác 6 dòng hoặc B3 khác 59, thì dừng và báo người dùng. Không chạy bước 1.

## Các bước thực hiện

Mỗi bước bắt đầu bằng W1. Chỉ chạy khi khoá trống, hoặc đã quá 90 phút và không còn run nào sống. Nếu notebook báo `Luồng PL_VV_TRANS_SLV_TO_GLD_30P đang giữ khoá (...): chạy lại sau` thì chưa có gì được ghi. Chờ rồi chạy lại đúng bước đó.

**Bước 1 — `srvratepy` lần 1 (R1). Bước này GHI dữ liệu.**
- Mở `NB_CREATE_DDL` trên DEV. Chỉ chạy **một cell `srvratepy`** (cell cuối). Không có tham số. Không chạy cell nào khác, nhất là `srvpoipy`.
- Output kỳ vọng: `gld_srv_poi_info +['rating_overall', 'rating_count', 'review_count']; cạnh ['slv_3p_poi_rating', 'slv_3p_poi_review']`.
- Ngay sau đó chạy K1, K2, K3 (mục "Kiểm tra kết quả").
- Điểm dừng:
  - Output có `không khớp hợp đồng`: dừng và chờ người dùng quyết định. Không sửa bảng.
  - Có lỗi `Dừng trước khi ghi` hoặc `Sau khi ghi`: dừng và ghi nguyên văn thông báo lỗi.
  - Nếu cell bị ngắt giữa chừng (sau 1–2 ALTER, hoặc sau ALTER nhưng trước INSERT): chạy lại chính cell `srvratepy`. Pre-check chấp nhận việc còn thiếu một tập con cột theo đúng thứ tự.

**Bước 2 — `srvratepy` lần 2 (R2). Chạy lại để kiểm tra idempotency.** Chi tiết ở mục I1.

**Bước 3 — `NB_SETUP_INITIAL_DDL` (R3). Bước này không ghi.**
- Tham số: `p_apply="false"`. Kiểm tra kỹ giá trị này trước khi chạy cả notebook.
- Kỳ vọng:
  - 18 `EXISTS_OK`;
  - không có `schema_issues`;
  - pipeline seed `to_insert=0` với 61 dòng.
- Điểm dừng: bất kỳ sai khác nào.

**Bước 4 — probe helper (R4) trong một phiên nháp. Bước này không ghi.**
- Tạo một notebook nháp gắn cùng các lakehouse DEV. Không lưu notebook này vào repo.
- Cell 1: `%run NB_LIB_TRANSFORM_SLV_GLD`.
- Cell 2: dán nguyên văn cell `srvinfohours` (dòng đầu `# BEGIN_HOURS_PURE`, dòng cuối `# END_HOURS_PURE`). Cell này không định nghĩa `_rating`.
- Cell 3: dán nguyên văn cell `srvinfobuild`. Dòng đầu là `ENT_COLS = ("poi_id", ...`. Cell này có `def _rating` và `def _reviews`.
- Cell 4:

```python
ent = spark.table("lh_vv_silver.dbo.slv_poi_entity_non_enrich")
keys = ent.where(F.coalesce(F.lower(F.trim(F.col("source_name"))) == "google", F.lit(False))).select("poi_id").distinct()
rt = spark.table("lh_vv_silver.dbo.slv_3p_poi_rating")
rv = spark.table("lh_vv_silver.dbo.slv_3p_poi_review")
print("google_keys", keys.count())
print("rating_rows", _rating(rt, keys).count())
print("review_poi", _reviews(rv, keys).count())
print("max_review_count", _reviews(rv, keys).agg(F.max("review_count")).first()[0])
```

- Kỳ vọng: không raise lỗi, và chỉ in ra số đếm.
- Điểm dừng: nếu gặp `QualityGateError ... slv_3p_poi_rating {n} poi_id có hơn một dòng` thì dừng và chờ người dùng quyết định. Không đổi code để chọn dòng.

**Bước 5 — node DRY_RUN (R5). Bước này không ghi bảng đích.**
- Mở `NB_GLD_SRV_POI_INFO` và đặt cell `srvinfoparam`: `p_exec_id=""`, `p_run_id=""`, `p_pl_name=""`, `p_trg_fq=""`, `p_pinned_json=""`, `p_mode="DRY_RUN"`, `p_force="false"`, `p_history_limit="1000"`. Sau đó chạy cả notebook.
- Kỳ vọng: SUCCESS, không có version mới trên bảng đích (K3 cho cùng version với sau bước 2).
- Ghi lại kết quả L2.

**Bước 6 — node RUN 1 (R5). Bước này GHI dữ liệu.**
- Giữ nguyên các tham số của bước 5, chỉ đổi `p_mode="RUN"`. Chạy cả notebook.
- Kỳ vọng:
  - SUCCESS;
  - `updated_rows` ≤ `google_with_value` (K5);
  - `qg_json.metrics` có `rating_matched` và `review_matched`.
- Điểm dừng: `QualityGateError` về grain rating (`có hơn một dòng`) hoặc miền INT (`ngoài miền INT`), hoặc ConfigError về kiểu `rating_overall`. Khi đó dừng và chờ người dùng quyết định, không sửa code để chọn dòng. Mọi điểm dừng này đều xảy ra trước khi ghi.

**Bước 7 — node RUN 2 (R5). Chạy lại để kiểm tra idempotency.** Chi tiết ở mục I2.

**Bước 8 — R6. Bước này không ghi.**
- Chạy K4 (2 câu SQL của architecture) và K6 ngay sau bước 7.
- RUN 2 không đổi dữ liệu, nên dữ liệu lúc này chính là kết quả của RUN 1.

**Bước 9 — NB_00 PLAN (R7). Bước này không ghi và không lấy khoá.**
- Mở `NB_00_ORCHES_SLV_TO_GLD` và đặt cell `3485be21`:
  - `p_pl_name = "PL_VV_TRANS_SLV_TO_GLD_30P"`. Mặc định của cell là `PL_VV_TRANSFORM_SLV_TO_GLD_1H`, phải sửa.
  - `p_run_id = ""`
  - `p_mode = "PLAN"`. Mặc định của cell là `"RUN"`, phải sửa.
  - `p_max_parallel = "3"`
  - `p_node_timeout_min = "20"`
  - `p_dag_timeout_min = "45"`
  - `p_lock_timeout_min = "90"`
  - `p_force_nodes = ""`
  - `p_history_limit = "1000"`
  - `p_non_data_ops = ""`
- Chạy cả notebook.
- Kỳ vọng:
  - kế hoạch có 2 node (`gld_srv_poi_multi_lang`, `gld_srv_poi_info`);
  - `gld_srv_poi_info` có 5 cạnh;
  - chỉ có các WARN về nhịp (cadence) đã được chấp nhận;
  - không có dòng mới trong `ctrl_log_run` (PLAN không ghi log).
- Lưu `RUN_SUMMARY` dạng JSON, chỉ phần số node, số cạnh và WARN.
- Điểm dừng: WARN hoặc lỗi khác loại cadence, hoặc số node / số cạnh sai.

## Kiểm tra kết quả

**K1 — schema sau bước 1.** Chạy lại đoạn python ở B1. Kỳ vọng:
- 32 cột;
- vị trí 25 là `holiday_exceptions`;
- vị trí 26 là `rating_overall decimal(4,2) True`;
- vị trí 27 là `rating_count int True`;
- vị trí 28 là `review_count int True`;
- vị trí 29–32 lần lượt là `row_hash`, `created_at`, `updated_at`, `deleted_at`.

**K2 — config sau bước 1 và bước 2.** Chạy lại B2 và B3. Kỳ vọng:
- B2 có 8 dòng: 6 dòng cũ cộng 2 dòng mới `slv_3p_poi_rating`, `slv_3p_poi_review`. Hai dòng mới có `trg_tbl = gld_srv_poi_info`, `pl_name = PL_VV_TRANS_SLV_TO_GLD_30P`, `src_schema = lh_vv_silver.dbo`, `is_active = 1`, `priority = 1`, `load_mode = RECOMPUTE`, `nb_name = NB_GLD_SRV_POI_INFO`, `n = 1`.
- `gld_srv_poi_info` có 5 cạnh active.
- B3 cho `n = 61`.

**K3 — version bảng gold.** Chạy lại đoạn python ở B4. Kỳ vọng:
- Sau bước 1 có thêm version ALTER (tối đa 3, mỗi cột một commit).
- Sau bước 2 và bước 5, version mới nhất không đổi.
- Sau bước 6 có tối đa 1 version MERGE mới.
- Sau bước 7 version không đổi.

**K4 — R6, trên các dòng live.**

```sql
SELECT count(*) n_live, count(DISTINCT poi_id) n_poi,
  sum(CASE WHEN coalesce(lower(trim(source_name)),'') <> 'google' AND (rating_overall IS NOT NULL OR rating_count IS NOT NULL OR review_count IS NOT NULL) THEN 1 ELSE 0 END) non_google_filled,
  sum(CASE WHEN review_count = 0 THEN 1 ELSE 0 END) review_zero
FROM lh_vv_gold.dbo.gld_srv_poi_info WHERE deleted_at IS NULL
```

Kỳ vọng: `n_live = n_poi =` giá trị `n_live` ở B5, `non_google_filled = 0`, `review_zero = 0`.

```sql
SELECT count(*) mismatches FROM lh_vv_gold.dbo.gld_srv_poi_info g
LEFT JOIN lh_vv_silver.dbo.slv_3p_poi_rating r ON g.poi_id = r.poi_id
LEFT JOIN (SELECT poi_id, count(*) c FROM lh_vv_silver.dbo.slv_3p_poi_review GROUP BY poi_id) v ON g.poi_id = v.poi_id
WHERE g.deleted_at IS NULL AND lower(trim(g.source_name)) = 'google'
  AND NOT (g.rating_overall <=> r.rating_overall AND g.rating_count <=> CAST(r.rating_count AS INT) AND g.review_count <=> CAST(v.c AS INT))
```

Kỳ vọng: `mismatches = 0`. Nếu khác 0 thì chạy K6 để xem FL_00 có ghi rating/review sau RUN 1 hay không. Nếu có, ghi lại các version nguồn và báo người dùng. Không chạy lại node để "sửa" khi chưa có quyết định.

**K5 — số dòng Google có giá trị, để đối chiếu với `updated_rows` của RUN 1.**

```sql
SELECT sum(CASE WHEN lower(trim(source_name)) = 'google' THEN 1 ELSE 0 END) AS google_live,
       sum(CASE WHEN lower(trim(source_name)) = 'google' AND (rating_overall IS NOT NULL OR rating_count IS NOT NULL OR review_count IS NOT NULL) THEN 1 ELSE 0 END) AS google_with_value
FROM lh_vv_gold.dbo.gld_srv_poi_info WHERE deleted_at IS NULL
```

Kỳ vọng: `updated_rows` của RUN 1 (L2) ≤ `google_with_value`. Dòng có cả 3 giá trị NULL giữ nguyên `row_hash` nên không bị ghi lại. Đây là hành vi đúng.

**K6 — kiểm tra drift nguồn.** So sánh version mới nhất của nguồn với `src_versions_json` của RUN 1 (L2):

```python
for t in ("lh_vv_silver.dbo.slv_3p_poi_rating", "lh_vv_silver.dbo.slv_3p_poi_review"):
    print(t, spark.sql(f"DESCRIBE HISTORY {t} LIMIT 1").select("version").first()[0])
```

## Chạy lại để kiểm tra idempotency

**I1 — `srvratepy` lần 2 (bước 2, R2). Bước này chạy lại một bước ghi, nhưng kỳ vọng không ghi gì.**
- Chạy W1. Sau đó trong `NB_CREATE_DDL` chỉ chạy cell `srvratepy`.
- Output kỳ vọng: `gld_srv_poi_info +[]; cạnh ['slv_3p_poi_rating', 'slv_3p_poi_review']`.
- K3: bảng gold không có version mới.
- K2: B2 vẫn 8 dòng với `n = 1`, B3 vẫn 61.
- Điểm dừng: có ALTER, có version mới, config khác 61, hoặc có lỗi.

**I2 — node RUN 2 (bước 7, R5).**
- Chạy W1. Giữ nguyên tham số `srvinfoparam` của bước 6 (`p_mode="RUN"`, các tham số khác như bước 5) và chạy cả notebook.
- Kỳ vọng:
  - SUCCESS hoặc trạng thái không ghi;
  - L2 cho `inserted_rows = 0`, `updated_rows = 0`, `deactivated_rows = 0` (0/0/0);
  - K3 không có version mới.
- Điểm dừng: bất kỳ số nào khác 0, hoặc có version mới.

Không có lần chạy lại nào khác. Đặc biệt, **không chạy lại `srvpoipy`** sau `srvratepy`.

## Kiểm tra log và watermark

Mọi truy vấn trong mục này đều chỉ đọc. Thay `<T0_TABLE_RUN>` và `<T0_RUN>` bằng giá trị lấy ở B0.

**W1 — khoá luồng GLD_30P.** Chạy trước mỗi bước và sau mỗi bước.

```sql
SELECT watermark_id, status, flow_name, lock_exec_id, lock_at, last_run_id, error_message, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P'
```

Kỳ vọng:
- Trước khi chạy: `lock_exec_id` là NULL.
- Sau bước 1 và bước 2: `lock_exec_id` NULL, `status = 'SUCCESS'`, `error_message` rỗng.
- Sau mỗi lần chạy node: `lock_exec_id` NULL, `status` là trạng thái của run đó.
- Bước 9 (PLAN) không thay đổi dòng này.

Nếu một bước lỗi khi đang giữ khoá, `srvratepy` sẽ nhả khoá với `status = 'FAILED'` và `error_message` cắt còn 500 ký tự. Khi đó ghi lại `error_message`.

**W2 — watermark cạnh của `gld_srv_poi_info`.**

```sql
SELECT watermark_id, src_tbl, status, last_src_version, last_success_at, last_run_id, error_message
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_e__gld_srv_poi_info__%'
ORDER BY watermark_id
LIMIT 50
```

Kỳ vọng: không đổi so với baseline B6 sau toàn bộ runbook. Lý do là chỉ NB_00 ở `RUN` mới ghi dòng cạnh, còn node chạy tay và PLAN thì không. Chưa có dòng `wm_e__gld_srv_poi_info__slv_3p_poi_rating` và `wm_e__gld_srv_poi_info__slv_3p_poi_review`. Hai dòng này sẽ được tạo ở lần NB_00 `RUN` đầu tiên, nằm ngoài runbook này.

**L1 — log run cấp luồng.**

```sql
SELECT exec_id, run_id, pl_name, nb_name, run_mode, status, tbl_total_count, tbl_success_count, tbl_failed_count, started_at, ended_at, error_message
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30P' AND (status = 'RUNNING' OR started_at > TIMESTAMP '<T0_RUN>')
ORDER BY started_at
LIMIT 50
```

Kỳ vọng:
- Trước bước 1: không có dòng nào `RUNNING`.
- Bước 9 (PLAN) không thêm dòng.
- Ghi lại mọi dòng mới phát sinh trong lúc chạy node.

**L2 — log node.**

```sql
SELECT exec_id, pl_name, status, entity_rows, inserted_rows, updated_rows, deactivated_rows, trg_version,
       get_json_object(qg_json, '$.mode') AS mode,
       get_json_object(qg_json, '$.metrics') AS metrics,
       get_json_object(qg_json, '$.blocks') AS blocks,
       get_json_object(qg_json, '$.warns') AS warns,
       src_versions_json, error_message, started_at
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_tbl = 'gld_srv_poi_info' AND started_at > TIMESTAMP '<T0_TABLE_RUN>'
ORDER BY started_at
LIMIT 50
```

Kỳ vọng:
- Mỗi lần chạy node có 1 dòng, theo thứ tự DRY_RUN, RUN 1, RUN 2.
- RUN 1: `metrics` có `rating_matched` và `review_matched`, cùng các metric cũ (`destination_dup_poi`, `partner_rows`, `google_rows_kept`, `operating_hours_null`).
- RUN 2: 0/0/0.
- `src_versions_json` có cả `slv_3p_poi_rating` và `slv_3p_poi_review`.

## Rollback và forward recovery

- **Ưu tiên forward recovery.** Sửa build qua một thay đổi code mới (theo quy trình task, không sửa trực tiếp trên DEV), deploy, rồi chạy lại node bằng `p_mode="RUN"` với các tham số như bước 6. Build là recompute toàn phần. Mọi điểm dừng của node đều nằm trước khi ghi.
- **Phục hồi theo điểm lỗi:**
  - Đã deploy nhưng chưa chạy `srvratepy`: node báo ConfigError `spec.inputs lệch config` và không ghi. Cách xử lý: chạy `srvratepy`.
  - Đã chạy `srvratepy` nhưng DEV vẫn là notebook node cũ: gặp cùng ConfigError và không ghi. Cách xử lý: deploy `NB_GLD_SRV_POI_INFO` mới.
  - Đã chạy một phần ALTER nhưng chưa INSERT: node gặp ConfigError. Cách xử lý: chạy lại cell `srvratepy`.
  - Khoá do người khác giữ, hoặc cell mất khoá: chưa ghi gì. Cách xử lý: chạy lại sau.
  - Cột bị thêm sau `deleted_at` qua một đường khác: `srvratepy` báo `không khớp hợp đồng`. Cách xử lý: dừng, chờ người dùng quyết định.
  - `QualityGateError` về grain rating hoặc miền INT: dừng, chờ người dùng quyết định. Không sửa code để chọn dòng.
- **Rollback.** Chỉ làm khi người dùng yêu cầu, và cần đủ 3 việc:
  1. Một task vá mới đặt 2 cạnh `slv_3p_poi_rating` và `slv_3p_poi_review` về `is_active = 0`, với điều kiện chỉ cập nhật khi giá trị khác. Thiếu việc này thì SPEC cũ sẽ lỗi ConfigError.
  2. Deploy lại phiên bản `NB_GLD_SRV_POI_INFO` trước đó.
  3. 3 cột vẫn ở lại, vì chúng nullable và quy tắc 5 cấm DROP. Giá trị cũ trên các dòng Google sẽ trở nên cũ (stale), vì build cũ không ghi các cột này. Muốn xoá các giá trị đó cần một lệnh `UPDATE … SET … = NULL` chạy một lần, và lệnh này phải được người dùng phê duyệt riêng. Runbook này không chứa lệnh đó.
- `review_count = 0` không bao giờ xuất hiện, nên NULL luôn mang nghĩa "không biết / không có".
- Không DROP bảng. Không xoá dòng `wm_flow__`. Không sửa `ctrl_mng_pipeline_config` bằng tay.

## Kết quả người dùng ghi nhận

- Người thực hiện: ______
- Thời gian bắt đầu và kết thúc (UTC): ______
- Workspace DEV: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>`
- Commit đã deploy: `<CẦN NGƯỜI DÙNG CUNG CẤP: commit/hash đã deploy lên DEV>`
- B0: `t0_table_run` = 2026-10-24T18:03:38Z ; `t0_run` = 2026-10-23T10:48:00Z

Ghi số đếm, version và trạng thái. Mỗi kết quả tối đa 50 dòng, không có dữ liệu cá nhân.

| Mục | Kỳ vọng | Thực tế | Đạt? |
|---|---|---|---|
| B1 số cột gold | 29 | 29. Vị trí 25 `holiday_exceptions`, 26 `row_hash` | đạt |
| B2 số dòng cạnh | 6, mỗi dòng n=1 | 6 dòng GLD_30P, `n=1`, 3 info + 3 multi_lang | đạt |
| B3 tổng config | 59 | 59 | đạt |
| B4 version cuối gold | (ghi số) | version 1 MERGE; version 0 CREATE TABLE | đã ghi |
| B5 n_live / n_poi | (ghi số) | 24 / 24 | đã ghi |
| B6 / W1 khoá trước khi chạy | lock_exec_id NULL | chưa có trong bản dán | |
| Bước 1 output `srvratepy` | `+['rating_overall', 'rating_count', 'review_count']` | `gld_srv_poi_info +['rating_overall', 'rating_count', 'review_count']; cạnh ['slv_3p_poi_rating', 'slv_3p_poi_review']` | đạt |
| K1 schema | 32 cột; vị trí 26–28 là decimal(4,2)/int/int, nullable | 32 cột. 26 `rating_overall decimal(4,2)`, 27 `rating_count int`, 28 `review_count int`, đều nullable. 29–32 là `row_hash`, `created_at`, `updated_at`, `deleted_at` | đạt |
| K2 sau bước 1 | B2 8 dòng; info 5 cạnh active n=1; tổng 61 | R3 `defined=61 to_insert=0`; PLAN liệt kê 5 cạnh info | đạt |
| K3 sau bước 1 | ≤3 version ALTER mới, version = ______ | version cuối quan sát được là 4. Các RUN sau đó không tạo commit. Chưa có `DESCRIBE HISTORY` | đã ghi |
| Bước 2 output `srvratepy` | `+[]` | bản dán: `+[]` | đạt phần output |
| K2/K3 sau bước 2 | 61; không có version mới | chưa có trong bản dán | |
| Bước 3 R3 | 18 `EXISTS_OK`; không có `schema_issues`; `to_insert=0`, 61 dòng | 18 `EXISTS_OK`; exit `PLAN`, `p_apply=false`; `pipeline_config defined=61 to_insert=0`; không có `ConfigError` | đạt |
| Bước 4 R4 | không raise; google_keys / rating_rows / review_poi / max_review_count = ______ | 41 / 41 / 41 / 5 | đạt |
| Bước 5 DRY_RUN | SUCCESS; không có version mới | SUCCESS; insert 0, update 0, xoá mềm 0; `trg_version` null; exec `bb572231-5d9c-4488-916f-f2318eb2a31d` | đạt |
| Bước 6 RUN 1 | SUCCESS; inserted / updated / deactivated = ______; rating_matched / review_matched = ______ | SUCCESS; 0 / 0 / 0; `trg_version` 4; exec `645c7547-710f-45e5-907a-d7fd6b71416b`. metrics `rating_matched` 0, `review_matched` 0, `google_rows_kept` 0, `partner_rows` 24 | đạt |
| K5 google_live / google_with_value | updated_rows ≤ google_with_value | google_live 0; google_with_value 0; updated_rows 0 | đạt |
| Bước 7 RUN 2 | 0/0/0; không có version mới | SUCCESS; 0/0/0; bỏ qua MERGE; `trg_version` 4; exec `85b6ea66-47eb-425c-91d7-97ba5f3c59db` | đạt |
| K4 n_live / n_poi | = B5 n_live | 24 / 24 | đạt |
| K4 non_google_filled | 0 | 0 | đạt |
| K4 review_zero | 0 | 0 | đạt |
| K4 mismatches | 0 | 0 | đạt |
| K6 version nguồn rating / review so với RUN 1 | giống nhau (nếu khác thì ghi lại) | RUN 1, RUN 2 và lần NB_00 cùng rating version 4, review version 4 | đạt |
| Bước 9 PLAN | 2 node; info 5 cạnh; chỉ WARN cadence đã chấp nhận | 2 node, 8 cạnh; info 5 cạnh gồm rating và review; một WARN nhịp. exec `fb155ae1-1ba9-458b-b921-a6dc9c30a858` | đạt |
| W1 sau cùng | lock_exec_id NULL | `lock_exec_id` null. `status` PARTIAL_FAILED. `flow_name` NB_CREATE_DDL. `last_run_id` `8f8da0f2-175e-4e9d-bd0e-6bb3756f5a06`. `updated_at` 2026-10-25T19:44:40Z | khoá đã nhả |
| W2 sau cùng | không đổi so với B6; chưa có dòng cạnh rating/review | 5 cạnh info SUCCESS, gồm rating version 4 và review version 4, cùng `last_run_id` của NB_00 RUN | đã ghi; ngoài runbook |
| L1 khi PLAN | không có dòng mới | | |

Ghi chú hoặc thông báo lỗi nguyên văn (nếu có): 2026-10-26. L2 có DRY_RUN, RUN 1, RUN 2 và lần con của NB_00. Cả bốn lần metrics đều `rating_matched` 0, `review_matched` 0, `google_rows_kept` 0, `partner_rows` 24. Nguồn rating và review giữ version 4. NB_00 RUN ngoài runbook, exec `8f8da0f2-175e-4e9d-bd0e-6bb3756f5a06`, để `gld_srv_poi_multi_lang` FAILED vì `slv_enr_poi_info_multi_lang` rỗng và luồng PARTIAL_FAILED. Node info trong lần đó vẫn SUCCESS. Khoá luồng đã nhả.

Quyết định của người dùng tại các điểm dừng (nếu có): ______
