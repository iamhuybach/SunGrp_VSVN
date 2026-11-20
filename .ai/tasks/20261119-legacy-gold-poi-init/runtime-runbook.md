# Runtime runbook: 20261119-legacy-gold-poi-init

Runbook này dành cho người vận hành chạy tay trên Fabric. Agent không chạy bước Fabric nào. Mọi giá trị lấy từ `architecture.md` (`## Main brief`, `## Rollout`, `## Rollback and forward recovery`, `## Verification`), cell `lgpparams` và `lgpconst` của `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb`, header cell `legacyidpy` của `notebooks/NB_CREATE_DDL.ipynb`, và `docs/context/CTRL_TABLES_CONTEXT.md` (mục `ctrl_mng_watermark`, `ctrl_log_table_run`). Giá trị không có trong các file này được ghi là `<CẦN NGƯỜI DÙNG CUNG CẤP: …>`.

GATE-004 và GATE-005 là rủi ro đã chấp nhận (người dùng ghi "Accept risk"), không phải lỗi còn mở. Runbook không yêu cầu sửa code. Mục `Kiểm tra log và watermark` chỉ cách phát hiện hai trường hợp đó.

## Phạm vi và môi trường

- Workspace cũ, chỉ đọc: `sgr_visitvn_prd_batch`. Gold cũ: `sgr_visitvn_prd_batch.lh_vv_gold.dbo` (hằng `OLD`). Chỉ đọc bằng `VERSION AS OF <pin>` trên hai bảng `poi_master` và `poi_enrichment_display`.
- Workspace mới, nơi ghi: `sgr_visitvn_dev`. Notebook phải mở ở workspace này, nếu không thì dừng với lỗi `Notebook phải mở ở workspace sgr_visitvn_dev`.
- Các bảng init ghi (tên bốn phần, lấy từ `lgpconst`):
  - `MAP_FQ` = `sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map`, khoá `legacy_poi_id`
  - `INFO_FQ` = `sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info`, khoá `poi_id`
  - `ML_FQ` = `sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang`, khoá `(poi_id, lang)`
- `REV_FQ` = `sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_review` chỉ được thêm cột `load_origin`. Init không ghi dòng nào vào bảng này: `summary.review.inserted = 0`.
- Khoá luồng: `PL = "PL_VV_TRANS_SLV_TO_GLD_30M"`, dòng `watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M'` trong `sgr_visitvn_dev.lh_vv_ctrl.dbo.ctrl_mng_watermark`. Hạn khoá (lease) là 90 phút (`LEASE_MINUTES = 90` trong `legacyidpy`, bằng giá trị mặc định của `NB_00_ORCHES_SLV_TO_GLD`; node chạy tay cũng 90 phút theo `CTRL_TABLES_CONTEXT.md`).
- Mọi dòng init ghi có `load_origin = 'LEGACY_INIT'`. Mỗi commit Delta có `userMetadata = 'LEGACY_INIT:<exec_id>'`, với `exec_id` dạng `lgp-<hex>`.
- Tham số notebook init (cell `lgpparams`), giá trị mặc định: `p_mode = "PLAN"`, `p_pin_json = ""`. `p_mode` chỉ nhận `PLAN` hoặc `RUN`.
- Chỉ chạy trên DEV. Không gắn notebook init vào lịch 15 hay 30 phút.

## Điều kiện tiên quyết

1. Local đã xanh: `python -m pytest tests -q` và `python scripts/vv.py run-gate 20261119-legacy-gold-poi-init`. Người vận hành ghi lại commit dùng để publish: `<CẦN NGƯỜI DÙNG CUNG CẤP: commit hash của bản lib, DDL và notebook init đã duyệt>`.
2. Cách publish notebook lên `sgr_visitvn_dev` (git sync hay deployment pipeline): `<CẦN NGƯỜI DÙNG CUNG CẤP: cách publish notebook lên sgr_visitvn_dev>`.
3. Tài khoản chạy có quyền đọc `sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master` và `.poi_enrichment_display`, và quyền ghi `sgr_visitvn_dev.lh_vv_gold.dbo` và `sgr_visitvn_dev.lh_vv_ctrl.dbo`.
4. Khoá luồng đang trống, hoặc không có run 30M nào đang chạy, trước bước DDL và trước mỗi lần RUN. Chạy truy vấn sau (chỉ đọc):

```sql
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, updated_at
FROM sgr_visitvn_dev.lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M';
```

   Kỳ vọng: `lock_exec_id` là NULL, hoặc `lock_at` cũ hơn 90 phút.
5. Tên notebook của ba node gold dùng ở R2 và R6 là `NB_GLD_SRV_POI_INFO`, `NB_GLD_SRV_POI_MULTI_LANG`, `NB_GLD_SRV_POI_REVIEW`, chạy với `p_mode = DRY_RUN`, `p_force = true`. Các tham số khác của ba notebook này không nằm trong các file đã đọc: `<CẦN NGƯỜI DÙNG CUNG CẤP: tham số còn lại của NB_GLD_SRV_POI_* nếu khác mặc định>`.

## Baseline trước khi chạy

Tất cả truy vấn trong mục này chỉ đọc. Ghi lại kết quả vào `Kết quả người dùng ghi nhận`.

B1. Version hiện tại của gold cũ, để đối chiếu với pin mà PLAN sẽ chọn:

```sql
DESCRIBE HISTORY sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master LIMIT 1;
DESCRIBE HISTORY sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_enrichment_display LIMIT 1;
```

B2. Version và số dòng của các bảng đích mới:

```sql
DESCRIBE HISTORY sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info LIMIT 1;
DESCRIBE HISTORY sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang LIMIT 1;
SELECT count(*) AS n, count_if(deleted_at IS NULL) AS live FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info;
SELECT count(*) AS n, count_if(deleted_at IS NULL) AS live FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang;
```

B3. Baseline của R2: chạy forced `DRY_RUN` cho ba node sau khi publish lib (xem bước 2). Lấy `inserted_rows`, `updated_rows`, `deactivated_rows` từ log:

```sql
SELECT exec_id, trg_tbl, status, inserted_rows, updated_rows, deactivated_rows, started_at
FROM sgr_visitvn_dev.lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_tbl IN ('gld_srv_poi_info', 'gld_srv_poi_multi_lang', 'gld_srv_poi_review')
ORDER BY started_at DESC
LIMIT 50;
```

B4. Checksum V4 ngay trước R4, chỉ trên dòng do pipeline sở hữu (`load_origin IS NULL`):

```sql
SELECT count(*) AS n, sum(crc32(concat_ws('|', poi_id, row_hash))) AS chk
FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info
WHERE load_origin IS NULL;

SELECT count(*) AS n, sum(crc32(concat_ws('|', poi_id, lang, row_hash))) AS chk
FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang
WHERE load_origin IS NULL;
```

## Các bước thực hiện

### Bước 1 (R1): DDL, cell `legacyidpy`

1. Mở `NB_CREATE_DDL` ở workspace `sgr_visitvn_dev`. Chỉ chạy cell `legacyidpy` (và cell markdown `legacyidmd` nếu muốn). Không chạy các cell khác.
2. Cell này giữ khoá `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` trong lúc chạy. Nó tạo `sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map` (`CREATE TABLE IF NOT EXISTS`) với các cột `MAP_COLS`:
   - `legacy_poi_id STRING NOT NULL`
   - `lang STRING`
   - `legacy_ingestion_source STRING`
   - `source_id STRING`
   - `source_name STRING`
   - `poi_id STRING`
   - `poi_id_status STRING NOT NULL`
3. Cell thêm `load_origin STRING` vào cuối `gld_srv_poi_info`, `gld_srv_poi_multi_lang` và `gld_srv_poi_review`, có điều kiện chặn nên chạy lại không ghi gì. Cell không ghi dòng và không đổi cạnh hay registry.
4. Kiểm tra V1 (chỉ đọc):

```sql
DESCRIBE TABLE sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map;
DESCRIBE TABLE sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info;
DESCRIBE TABLE sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang;
DESCRIBE TABLE sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_review;
```

   Kỳ vọng: cột của map khớp `MAP_COLS`, và `load_origin` có kiểu `string` trên ba bảng.
5. **DỪNG nếu Fabric từ chối `CREATE` hoặc `ALTER` dùng tên bốn phần.** Ghi lỗi lại. Người dùng quyết định có cho cell này dùng tên ba phần hay không. Không tự sửa.
6. Dán output `DESCRIBE` vào mục kết quả.

### Bước 2 (R2): publish lib và kiểm tra luồng xuống

1. Publish `NB_LIB_TRANSFORM_SLV_GLD` lên `sgr_visitvn_dev` theo điều kiện tiên quyết 2.
2. Chạy `NB_GLD_SRV_POI_INFO`, `NB_GLD_SRV_POI_MULTI_LANG`, `NB_GLD_SRV_POI_REVIEW` với `p_mode = DRY_RUN`, `p_force = true`. Ghi `inserted`, `updated`, `deactivated` làm baseline (B3).
3. Đợi một run 30M bình thường của `PL_VV_TRANS_SLV_TO_GLD_30M` chạy xong. Kiểm tra V2 (chỉ đọc):

```sql
SELECT 'info' AS t, count_if(load_origin IS NOT NULL) AS owned FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info
UNION ALL SELECT 'multi_lang', count_if(load_origin IS NOT NULL) FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang
UNION ALL SELECT 'review', count_if(load_origin IS NOT NULL) FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_review;
```

   Kỳ vọng: `owned = 0` trên cả ba bảng.
4. **DỪNG lấy bằng chứng.** Người dùng xác nhận Copy Job gold → PostgreSQL chạy thành công khi đã có cột mới. Mapping của Copy Job nằm ngoài repo: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên Copy Job và run id đã xác nhận>`.

### Bước 3 (R3): init với `p_mode = PLAN`

1. Mở `NB_SETUP_LEGACY_GOLD_POI` ở workspace `sgr_visitvn_dev`. Đặt cell `lgpparams`:

```python
p_mode = "PLAN"
p_pin_json = ""
```

2. Chạy toàn bộ notebook. PLAN không nhận khoá và không ghi gì. Khi `p_pin_json = ""`, notebook tự lấy pin là version mới nhất của `poi_master` và `poi_enrichment_display` ở gold cũ.
3. Sao chép toàn bộ JSON summary mà notebook in ra (cũng là giá trị exit). Lấy giá trị `summary.pins` làm pin cho các lần chạy sau, ví dụ dạng:

```json
{"poi_master": <CẦN NGƯỜI DÙNG CUNG CẤP: version poi_master trong summary.pins của PLAN>, "poi_enrichment_display": <CẦN NGƯỜI DÙNG CUNG CẤP: version poi_enrichment_display trong summary.pins của PLAN>}
```

4. **DỪNG để người dùng quyết định** nếu có bất kỳ điều kiện nào dưới đây:
   - `map.missing_evidence_n > 0`
   - `info.cast_fail_n > 0` (notebook đã dừng ở stage `info`)
   - `info.old_inactive_n > 0` (Conflict 6)
   - `multi_lang.cost_loaded = false` (Conflict 7)
   - `multi_lang.lang_mismatch_n > 0`
   - `multi_lang.no_parent_n` hoặc `multi_lang.conflict_n` lớn hơn dự kiến. P2 giới hạn info insert tối đa 25927 google và 4 partner.

   Ghi thêm `map.drift_n`, `info.cmp_conflict_n`, `info.vi_conflict_n`, `info.no_vi_n`, `info.to_insert`, `multi_lang.to_insert`, `multi_lang.orphan_n` và `multi_lang.null_lang_n`.
5. Hệ quả người dùng đã chấp nhận với D-04: khoảng 26k dòng info legacy không có `destination_id`, địa chỉ hay toạ độ sẽ hiển thị ở serving cho đến khi pipeline tự sinh ra chúng. Số chính xác là `info.to_insert`.
6. Người dùng ghi "Duyệt RUN" vào mục kết quả. Chỉ sau đó mới làm bước 4.

### Bước 4 (R4): init với `p_mode = RUN`

1. Lấy checksum V4 (B4) và kiểm tra khoá trống (điều kiện tiên quyết 4).
2. Đặt `lgpparams` và dán đúng pin của PLAN. Không để `p_pin_json` rỗng, vì khi rỗng notebook sẽ lấy version mới nhất và có thể khác pin đã duyệt.

```python
p_mode = "RUN"
p_pin_json = '{"poi_master": <CẦN NGƯỜI DÙNG CUNG CẤP: pin poi_master từ PLAN>, "poi_enrichment_display": <CẦN NGƯỜI DÙNG CUNG CẤP: pin poi_enrichment_display từ PLAN>}'
```

3. Chạy toàn bộ notebook. Thứ tự ghi là map, rồi info, rồi multi-lang. Mỗi bảng có đúng một commit MERGE chỉ-INSERT, gắn tag `LEGACY_INIT:<exec_id>`. RUN dừng trước khi ghi nếu:
   - `map.drift_n > 0`
   - `cast_fail_n > 0`
   - có khoá trùng payload
   - không nhận được khoá (`Không nhận khoá PL_VV_TRANS_SLV_TO_GLD_30M: …`)
4. Sao chép JSON summary. Với mỗi slot `map`, `info`, `multi_lang`, ghi lại `v_pre`, `v_post`, `inserted`, `commit`. Kỳ vọng `commit = "COMMITTED"`. Ghi thêm `exec_id`, cùng `failed_stage`, `unlock_error`, `cleanup_error`, `history_error` nếu có.

### Bước 5 (R5): RUN lần hai với cùng `p_pin_json`

Xem mục `Chạy lại để kiểm tra idempotency`.

### Bước 6 (R6): soak

1. Chạy forced `DRY_RUN` (`p_mode = DRY_RUN`, `p_force = true`) cho `NB_GLD_SRV_POI_INFO` và `NB_GLD_SRV_POI_MULTI_LANG`. `deactivated` phải nằm trong baseline R2, tức không tăng thêm bằng số dòng legacy.
2. Đợi một run 30M bình thường chạy xong, rồi kiểm tra V7 trong `Kiểm tra kết quả`.
3. Tiếp theo là reviewer (`sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`) và `risk-gate`.

## Kiểm tra kết quả

Tất cả truy vấn chỉ đọc. Các mẫu giới hạn 50 dòng và chỉ có cột khoá hoặc trạng thái: không có tên, địa chỉ, điện thoại, email hay nội dung review.

V5 (sau R4):

```sql
-- Số dòng map phải bằng số poi_id phân biệt của gold cũ tại pin
SELECT count(DISTINCT poi_id) AS old_distinct
FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master VERSION AS OF <CẦN NGƯỜI DÙNG CUNG CẤP: pin poi_master từ PLAN>;

SELECT count(*) AS map_rows, count_if(poi_id_status = 'OK') AS ok_n, count_if(poi_id_status = 'MISSING_EVIDENCE') AS missing_n
FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map;

-- Số dòng LEGACY_INIT phải bằng inserted của từng bảng
SELECT count_if(load_origin = 'LEGACY_INIT') AS legacy_n FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info;
SELECT count_if(load_origin = 'LEGACY_INIT') AS legacy_n FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang;

-- Không có khoá trùng (kỳ vọng 0 dòng)
SELECT poi_id, count(*) AS c FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info
GROUP BY poi_id HAVING count(*) > 1 LIMIT 50;
SELECT poi_id, lang, count(*) AS c FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang
GROUP BY poi_id, lang HAVING count(*) > 1 LIMIT 50;
SELECT legacy_poi_id, count(*) AS c FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map
GROUP BY legacy_poi_id HAVING count(*) > 1 LIMIT 50;

-- Mẫu map, chỉ cột khoá và trạng thái
SELECT legacy_poi_id, source_name, poi_id, poi_id_status
FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map LIMIT 50;
```

Kỳ vọng V5:
- `map_rows = old_distinct`
- `inserted = to_insert` cho info và multi-lang
- `legacy_n = inserted` cho từng bảng
- không có khoá trùng

V4 (sau R5, trước bất kỳ run định kỳ nào): chạy lại hai truy vấn của B4. `n` và `chk` phải bằng giá trị trước R4. Điều này chứng minh init không đổi dòng nào của pipeline.

V7 (R6, sau một run bình thường):

```sql
SELECT count_if(load_origin = 'LEGACY_INIT' AND deleted_at IS NOT NULL) AS legacy_deleted
FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info;
SELECT count_if(load_origin = 'LEGACY_INIT' AND deleted_at IS NOT NULL) AS legacy_deleted
FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang;

SELECT trg_tbl, status, inserted_rows, updated_rows, deactivated_rows, started_at
FROM sgr_visitvn_dev.lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_tbl IN ('gld_srv_poi_info', 'gld_srv_poi_multi_lang')
ORDER BY started_at DESC LIMIT 50;
```

Kỳ vọng V7:
- `legacy_deleted = 0`
- forced `DRY_RUN` cho `deactivated` nằm trong baseline R2
- số dòng pipeline bị xoá mềm trong khoảng bình thường
- khoá nào run vừa sinh ra đều có `load_origin` NULL (đã bàn giao), nên `legacy_n` chỉ giảm hoặc giữ nguyên so với sau R4

## Chạy lại để kiểm tra idempotency

1. Kiểm tra khoá trống (điều kiện tiên quyết 4). Không chạy run định kỳ nào giữa R4 và R5.
2. Đặt `lgpparams` bằng **đúng** giá trị của lần chạy thứ hai, tức cùng pin của PLAN:

```python
p_mode = "RUN"
p_pin_json = '{"poi_master": <CẦN NGƯỜI DÙNG CUNG CẤP: pin poi_master từ PLAN>, "poi_enrichment_display": <CẦN NGƯỜI DÙNG CUNG CẤP: pin poi_enrichment_display từ PLAN>}'
```

3. Chạy toàn bộ notebook. Kỳ vọng V6: `map.inserted = 0`, `info.inserted = 0`, `multi_lang.inserted = 0`, `map.drift_n = 0`, `info.to_insert = 0`, `multi_lang.to_insert = 0`. Lý do: mọi MERGE chỉ có `WHEN NOT MATCHED THEN INSERT`, nên khoá đã có, dù đang sống hay đã xoá mềm, đều bị bỏ qua.
4. Lấy lại checksum V4 và so với giá trị trước R4.
5. Nếu `inserted > 0` ở bất kỳ bảng nào, hoặc `drift_n > 0`: DỪNG, không chạy thêm, và ghi summary vào mục kết quả.

## Kiểm tra log và watermark

Notebook init không ghi `ctrl_log_run` hay `ctrl_log_table_run`. Có ba nguồn bằng chứng:
- JSON summary (được in ra và là giá trị exit của notebook)
- Delta history của ba bảng đích
- dòng khoá `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`

Commit của init (chỉ đọc):

```sql
SELECT version, timestamp, operation, userMetadata, operationMetrics.numTargetRowsInserted AS inserted
FROM (DESCRIBE HISTORY sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info LIMIT 50)
WHERE userMetadata LIKE 'LEGACY_INIT:%';
```

Nếu môi trường không cho `SELECT` trên `DESCRIBE HISTORY`, chạy `DESCRIBE HISTORY <bảng> LIMIT 50` rồi lọc bằng mắt. Lặp lại cho `gld_srv_poi_multi_lang` và `gld_poi_legacy_id_map`. Mỗi `exec_id` RUN có tối đa một commit trên mỗi bảng.

Khoá luồng sau mỗi RUN (chỉ đọc): dùng truy vấn ở điều kiện tiên quyết 4. Kỳ vọng `lock_exec_id` là NULL, và `status` là `SUCCESS` sau khi RUN thành công hoặc `FAILED` sau khi RUN lỗi.

**Rủi ro chấp nhận 1: đọc history không thấy một commit đã ghi.** Người vận hành nhận biết khi một slot trong summary có `commit = "UNKNOWN"`, hoặc có `history_error`, hoặc có `inserted` là null. Khi đó:
1. Không kết luận là "chưa ghi". Chạy truy vấn history ở trên, tìm `userMetadata = 'LEGACY_INIT:<exec_id>'` với version lớn hơn `v_pre`.
2. Đếm `count_if(load_origin = 'LEGACY_INIT')` trên bảng đó.
3. Nếu có commit, lấy `numTargetRowsInserted` từ history làm `inserted`. Nếu không có, coi là chưa ghi.
4. Có thể chạy lại RUN với cùng `p_pin_json` để hội tụ, vì RUN chỉ INSERT khoá còn thiếu.

**Rủi ro chấp nhận 2: nhả khoá lỗi, khoá 30 phút bị giữ đến hết lease 90 phút.** Người vận hành nhận biết khi summary có `unlock_error`, hoặc khi dòng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` vẫn có `lock_exec_id = '<exec_id của init>'` và `status = 'RUNNING'` sau khi notebook đã kết thúc. Một dấu hiệu khác là các run 30M sau đó không nhận được khoá hoặc bị bỏ qua. Kiểm tra bằng:

```sql
SELECT status, lock_exec_id, lock_at, updated_at,
       (lock_at < current_timestamp() - INTERVAL 90 MINUTES) AS lease_expired
FROM sgr_visitvn_dev.lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M';
```

Cách xử lý mặc định là chờ đến khi `lease_expired = true`. Run kế tiếp sẽ tự lấy lại khoá. Nhả khoá bằng tay là bước sự cố do người dùng quyết định và tự chạy. Chỉ làm khi chắc chắn không còn run nào đang chạy. Lệnh làm theo mẫu trong `CTRL_TABLES_CONTEXT.md` và lọc đúng `exec_id` của init:

```sql
UPDATE sgr_visitvn_dev.lh_vv_ctrl.dbo.ctrl_mng_watermark SET lock_exec_id = NULL, lock_at = NULL
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M' AND lock_exec_id = '<CẦN NGƯỜI DÙNG CUNG CẤP: exec_id lgp-… trong summary>';
```

## Rollback và forward recovery

Mọi thao tác trong mục này là bước sự cố do người dùng tự chạy. D-04 không có cleanup định kỳ. Không có lệnh nào ở đây xoá hay sửa dòng do pipeline sở hữu (`load_origin` NULL). Nên chạy khi khoá `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` đang trống.

1. **Trước khi có dòng init nào** (dừng ở R1 hoặc R2): có thể revert lib và DDL tự do. Cột `load_origin` NULL thừa không gây hại.
2. **Soft rollback dòng init (ưu tiên):**

```sql
UPDATE sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info
SET deleted_at = current_timestamp(), updated_at = current_timestamp()
WHERE load_origin = 'LEGACY_INIT' AND deleted_at IS NULL;

UPDATE sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang
SET deleted_at = current_timestamp(), updated_at = current_timestamp()
WHERE load_origin = 'LEGACY_INIT' AND deleted_at IS NULL;
```

   - Dòng đã bàn giao có `load_origin` NULL, nên không bị lệnh này chạm tới.
   - Nếu sau này pipeline sinh ra một khoá legacy đã xoá mềm, nhánh MATCHED của lib sẽ hồi sinh và bàn giao khoá đó.
   - `gld_poi_legacy_id_map` có thể giữ nguyên, vì không job định kỳ nào đọc nó. Bỏ map là quyết định riêng của người dùng: `<CẦN NGƯỜI DÙNG CUNG CẤP: giữ hay bỏ map>`. Nếu bỏ, phải chạy lại `legacyidpy` trước lần init sau.
3. **Hard rollback, chỉ để init lại:** lệnh chỉ nhắm dòng init. Sau đó chạy lại PLAN và RUN theo bước 3 và 4. Nếu không xoá cứng, các khoá đã xoá mềm sẽ chặn việc insert lại.

```sql
DELETE FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info WHERE load_origin = 'LEGACY_INIT';
DELETE FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang WHERE load_origin = 'LEGACY_INIT';
```

   Nếu lần init lại dùng pin khác, map đã ghi có thể làm RUN dừng với `drift_n > 0`. Cách xử lý map trong trường hợp này: `<CẦN NGƯỜI DÙNG CUNG CẤP: quyết định về map khi init lại với pin khác>`.
4. **`RESTORE TABLE … TO VERSION <v_pre>`** chỉ được dùng khi `DESCRIBE HISTORY` của bảng đó không có commit nào sau `v_post` của init. `v_pre` và `v_post` lấy từ summary của R4.
5. **Revert lib sau khi đã init** phải làm sau bước 2 hoặc 3. Nếu không, run kế tiếp sẽ xoá mềm mọi dòng `LEGACY_INIT` đang sống. Kết quả đó phục hồi được nhưng không kiểm soát được.
6. **Forward recovery:**
   - RUN lỗi giữa chừng (`failed_stage` là `map`, `info` hoặc `multi_lang`): sửa nguyên nhân, rồi chạy lại RUN với cùng `p_pin_json`. RUN chỉ insert khoá còn thiếu. Commit đã ghi ở stage trước được bỏ qua, nhờ khoá đã có và kiểm tra `drift_n`.
   - Sau khi chạy lại, kiểm tra lại V5, V6 và V4.

## Kết quả người dùng ghi nhận

| Mục | Giá trị |
|---|---|
| Commit đã publish | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| B1: version gold cũ `poi_master` / `poi_enrichment_display` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| B2: version và số dòng `gld_srv_poi_info` / `_multi_lang` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| R1 / V1: output `DESCRIBE` của map và kiểu `load_origin` trên 3 bảng | 2026-11-20, pass lần đầu: `legacyid: map +, owner +['gld_srv_poi_info', 'gld_srv_poi_multi_lang', 'gld_srv_poi_review'] / =[]`. Chạy lại cùng ngày sau D-08: `legacyid: map =, owner +['gld_srv_poi_amenity'] / =['gld_srv_poi_info', 'gld_srv_poi_multi_lang', 'gld_srv_poi_review']`. Map không đổi. `load_origin` mới chỉ thêm trên `gld_srv_poi_amenity`. Sau D-09: `legacyid: map =, owner +['gld_srv_poi_media_gallery'] / =['gld_srv_poi_info', 'gld_srv_poi_multi_lang', 'gld_srv_poi_review', 'gld_srv_poi_amenity']`. |
| R2 / B3: baseline forced `DRY_RUN` (`inserted` / `updated` / `deactivated`, 3 node) | 2026-11-20, cả ba SUCCESS, `p_mode=DRY_RUN`, `p_force=true`. `gld_srv_poi_info` exec `2f147682-09e5-4953-b035-cef25af9ae78`: 0/0/0, nguồn 19909. `gld_srv_poi_multi_lang` exec `76a3644b-fcdb-4077-9071-e4082eab5366`: 0/0/0, nguồn 59726; cảnh báo `multi_lang_source_name_null` 3 và `multi_lang_i18n_only_rows` 44. `gld_srv_poi_review` exec `4f253555-664b-49cf-bbd8-20c25b94497c`: 0/0/0, nguồn 121479. `trg_version` null vì DRY_RUN không ghi. |
| R2 / V2: `owned` sau run 30M (3 bảng) | 2026-11-20. Orchestrator `NO_DATA`, exec `78ff22b5-6f68-49f6-9504-16b41fffbe0f`. Sau đó `count_if(load_origin IS NOT NULL)` = 0 trên `gld_srv_poi_info`, `gld_srv_poi_multi_lang` và `gld_srv_poi_review`. |
| R2: xác nhận Copy Job gold → PostgreSQL | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| R3: JSON summary của PLAN (gồm `pins`) | PLAN đầu 2026-11-20, exec `lgp-3f7237139ead42ad86bfcba5339d6480`, pin 7011/5706, đã RUN. PLAN đầy đủ field, exec `lgp-b850c95589404d8091290c7c3e6082a6`. pins `poi_master` 7067, `poi_enrichment_display` 5758, `poi_detail` 6099, `poi_review` 69, `poi_rating` 63. map: missing 0, candidates 136763, drift 0, bad_key 0. info: groups 45676, cmp_conflict 200, vi_conflict 0, no_vi 0, cast_fail 0, old_inactive 2601, candidates 45476, present_live 45476, to_insert 0. multi_lang: display_rows 136562, orphan 0, null_lang 0, lang_mismatch 0, cost_loaded true, conflict 0, no_parent 30, candidates 136532, present_live 136532, to_insert 0. review: candidates 592797, conflict 0. media: candidates 246036. amenity: enum_n 279357, candidates 283, conflict 0. PLAN sau khi sửa join, exec `lgp-dffca812893c4d2e9de4545bb56cd0f2`. pins `poi_master` 7068, `poi_enrichment_display` 5759, `poi_detail` 6100, `poi_review` 69, `poi_rating` 63. map/info/multi_lang/review/media giữ cùng số. amenity: enum_n 279462, candidates 106454, conflict_n 87. Chưa duyệt RUN. |
| R3: quyết định của người dùng ("Duyệt RUN" hoặc dừng) | 2026-11-20: RUN đầu đã duyệt với pin 7011/5706. PLAN amenity 283 dòng không được duyệt, đã sửa join. PLAN `lgp-dffca812893c4d2e9de4545bb56cd0f2` được duyệt RUN với pin `poi_master` 7068, `poi_enrichment_display` 5759, `poi_detail` 6100, `poi_review` 69, `poi_rating` 63. |
| V4 trước R4 (`n`, `chk` của info / multi-lang) | 2026-11-20, trước RUN. info: n 19909, chk 42930004143378. multi-lang: n 59726, chk 128278754095081. Chỉ dòng `load_origin IS NULL`. |
| Khoá luồng sau mỗi RUN (`status`, `lock_exec_id`) | Trước RUN: status `NO_DATA`, `lock_exec_id` null, `lock_at` null, `last_run_id` `a8fe2af7-44d3-4344-9db7-ce5465fa6261`, `updated_at` 2026-11-19T17:42:39Z. |
| R4: JSON summary (`exec_id`, `v_pre` / `v_post` / `inserted` / `commit` mỗi bảng) | RUN đầu exec `lgp-3833cdc5c8e343acbecb2d3b958bbfce`, pin 7011/5706, info 25921 và multi_lang 77751 COMMITTED. RUN đầy đủ field lỗi exec `lgp-68c7bf8c505841bc8a6e7774f105bd7c`: failed_stage info, 20 khóa trùng, chưa ghi info. RUN sau sửa, exec `lgp-6659b44867464db595d1b0a2e5b44e97`, pin 7068/5759/6100/69/63. map v 1→1, inserted 0, NOT_COMMITTED. info v 18→19, inserted 0, COMMITTED, detail_conflict 0, master_conflict 0. multi_lang v 10→11, inserted 0, COMMITTED. review v 4→5, inserted 592797, COMMITTED. media v 5→6, inserted 246036, COMMITTED. amenity v 4→5, candidates 106454, inserted 72198, conflict 87, COMMITTED. |
| V5: `map_rows` / `old_distinct` / `legacy_n` / khoá trùng | 2026-11-20. `old_distinct` tại pin 7011 = 136763. map_rows 136763, ok_n 136763, missing_n 0. `legacy_n` info 25921, multi-lang 77751. Chưa chạy câu đếm khóa trùng. |
| R5 / V6: JSON summary (`inserted = 0` cả 3) | Lần idempotent đầu, exec `lgp-faecbca1210e4ecb80e1b35c0e39d55a`, pin 7011/5706, inserted 0, NOT_COMMITTED. RUN gắn `load_origin` media, exec `lgp-27633c9db2a1403d8a9b068391fdb2d0`, cùng pin 7068/5759/6100/69/63. Mọi bảng inserted 0. map v 1→1 NOT_COMMITTED. info v 20→21, multi_lang v 12→13, review v 6→7, amenity v 6→7, media v 7→8, đều COMMITTED. Đếm media sau đó: `legacy_n` 246036, `pipeline_n` 259063. |
| V4 sau R5 (phải bằng trước R4) | 2026-11-20 khớp. info n 19909, chk 42930004143378. multi-lang n 59726, chk 128278754095081. |
| Khoá luồng sau mỗi RUN (`status`, `lock_exec_id`) | Sau RUN lỗi: status `FAILED`, `lock_exec_id` null, `lock_at` null. Khóa đã nhả. |
| Có `commit = UNKNOWN`, `history_error` hoặc `unlock_error` không, và cách đã xử lý | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| R6 / V7: forced `DRY_RUN` `deactivated`, `legacy_deleted`, log run bình thường | 2026-11-20. DRY_RUN sau init: info và multi-lang deactivated 0. Sau đó `PL_VV_TRANS_SLV_TO_GLD_30M` là `NO_DATA`, không ghi gold. `legacy_deleted` = 0 trên cả `gld_srv_poi_info` và `gld_srv_poi_multi_lang`. |
| Rollback hoặc forward recovery đã chạy (nếu có) | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
