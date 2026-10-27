# Runtime runbook: 20261026-gld-srv-poi-review

Trạng thái: người dùng đã chạy trên Fabric DEV ngày 2026-10-27. `srvrevpy` đạt. Node dừng vì `slv_enr_poi_review_multi_lang` có 0 dòng. D-04: task này chỉ chốt khung bảng và khung transform.

## Phạm vi và môi trường

- Môi trường: chỉ Fabric DEV. Workspace DEV: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV dùng để chạy>`. Runbook không cần workspace id hay lakehouse id. Không điền id tự đoán vào tham số.
- Bảng đích: `lh_vv_gold.dbo.gld_srv_poi_review`. Grain là một dòng cho mỗi `review_id`.
- Pipeline `PL_VV_TRANS_SLV_TO_GLD_30M`, `load_mode` `RECOMPUTE`, notebook `NB_GLD_SRV_POI_REVIEW`, `priority` 1.
- Nguồn theo thứ tự: `lh_vv_silver.dbo.slv_enr_poi_review_multi_lang`, `lh_vv_silver.dbo.slv_3p_poi_review`, `lh_vv_silver.dbo.slv_3p_poi_rating`.
- Bảng ctrl liên quan: `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` (3 cạnh), `lh_vv_ctrl.dbo.ctrl_mng_watermark` (dòng khoá `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`), `lh_vv_ctrl.dbo.ctrl_log_table_run` và `lh_vv_ctrl.dbo.ctrl_log_run` (chỉ đọc).
- Thao tác ghi chỉ có hai loại:
  1. Cell `srvrevpy` trong `notebooks/NB_CREATE_DDL.ipynb`, chạy hai lần.
  2. Notebook `notebooks/NB_GLD_SRV_POI_REVIEW.ipynb`, chạy ba lần: `DRY_RUN`, `RUN`, `RUN`.
  Mọi câu SQL khác trong runbook đều chỉ đọc.
- Không chạy cả notebook `NB_CREATE_DDL`. Không chạy lại cell `enrflagpy`, vì hợp đồng `slv_enr_poi_review_multi_lang` trong cell đó là bản cũ.
- Mỗi mẫu kết quả tối đa 50 dòng. Không dán dữ liệu cá nhân. Các cột `author_name`, `review_text` và `title` không được đưa vào mẫu.
- P1 và P2 đã có kết quả: `sql-001` trả về 0 dòng (`evidence/results/sql-001.txt`). Không chạy lại.

## Điều kiện tiên quyết

1. Code của task đã nằm trong workspace DEV, gồm cell `srvrevmd`/`srvrevpy` ở cuối `NB_CREATE_DDL` và notebook `NB_GLD_SRV_POI_REVIEW` với các cell `srvrvmd`, `srvrvparam`, `srvrvrun`, `srvrvbuild`, `srvrvres`, `srvrvexit`. Cách đồng bộ hoặc commit đã dùng: `<CẦN NGƯỜI DÙNG CUNG CẤP: commit/cách đồng bộ notebook lên Fabric DEV>`.
2. `lh_vv_ctrl.dbo.ctrl_mng_watermark` có đúng 1 dòng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`. Nếu không, `srvrevpy` sẽ dừng với lỗi "chạy plcadpy trước".
3. `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` đã có cột `nb_name`. Nếu chưa có, `srvrevpy` sẽ dừng với lỗi "chạy enrddlpy trước".
4. Không có run nào của `PL_VV_TRANS_SLV_TO_GLD_30M` đang giữ khoá. Lease của `srvrevpy` là 90 phút (`LEASE_MINUTES = 90`).
5. Probe P4 ở bước 1 phải cho kết quả cho phép chạy tiếp, rồi mới được ghi.

## Baseline trước khi chạy

Chạy các câu sau trước bước 1 và lưu kết quả để so sánh về sau. Tất cả đều chỉ đọc.

B1. Dòng khoá luồng:
```sql
SELECT watermark_id, src_tbl, status, lock_exec_id, lock_at, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M';
```
Kỳ vọng: đúng 1 dòng. `lock_exec_id` là NULL, hoặc `lock_at` đã cũ hơn 90 phút.

B2. Cạnh hiện có của bảng đích:
```sql
SELECT id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_schema = 'lh_vv_gold.dbo' AND trg_tbl = 'gld_srv_poi_review'
ORDER BY id;
```
Ghi lại số dòng và `SELECT max(id) FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`.

B3. Schema silver trước khi patch:
```sql
DESCRIBE lh_vv_silver.dbo.slv_enr_poi_review_multi_lang;
```
`srvrevpy` chỉ chấp nhận ba trạng thái:
- đủ cột `review_id, poi_id, lang, title, review_text, created_at, updated_at`;
- thiếu `title`;
- thiếu cả `lang` và `title`.

Trạng thái khác sẽ làm cell dừng trước khi ghi.

B4. Bảng gold đã tồn tại hay chưa:
```sql
SHOW TABLES IN lh_vv_gold.dbo LIKE 'gld_srv_poi_review';
```

B5. Số dòng nguồn (chỉ đếm):
```sql
SELECT 'multi_lang' AS src, count(*) AS n FROM lh_vv_silver.dbo.slv_enr_poi_review_multi_lang
UNION ALL SELECT 'review', count(*) FROM lh_vv_silver.dbo.slv_3p_poi_review
UNION ALL SELECT 'rating', count(*) FROM lh_vv_silver.dbo.slv_3p_poi_rating;
```

B6. Run đang chạy của luồng GLD_30M:
```sql
SELECT exec_id, pl_name, nb_name, run_mode, status, started_at, ended_at
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30M'
ORDER BY started_at DESC
LIMIT 10;
```
Nếu có dòng `RUNNING` chưa quá 90 phút, đợi run đó kết thúc rồi mới chạy bước 3.

## Các bước thực hiện

### Bước 1: Probe P4, bắt buộc trước mọi thao tác ghi

```sql
SELECT version, timestamp, operation, operationParameters
FROM (DESCRIBE HISTORY lh_vv_silver.dbo.slv_enr_poi_review_multi_lang LIMIT 20);
```
Nếu môi trường không hỗ trợ subquery trên `DESCRIBE HISTORY`, chạy `DESCRIBE HISTORY lh_vv_silver.dbo.slv_enr_poi_review_multi_lang LIMIT 20` rồi chỉ đọc hai cột `operation` và `operationParameters`.

Quyết định:
- Có lệnh SQL `INSERT` ghi theo vị trí cột (positional): **DỪNG**. Không chạy `srvrevpy`. Báo lại kết quả.
- Chỉ có `WRITE` ghi theo tên cột (by-name) hoặc `MERGE`: được chạy tiếp bước 2.
- Không xác định được là by-name hay positional: **DỪNG** và hỏi lại.

Dán tối đa 50 dòng vào `evidence/results/runtime-p4.txt`.

### Bước 2: Probe P3, kiểm tra kiểu (tuỳ chọn)

```sql
DESCRIBE lh_vv_silver.dbo.slv_3p_poi_review;
DESCRIBE lh_vv_silver.dbo.slv_3p_poi_rating;
```
Kỳ vọng:
- `slv_3p_poi_review.rating` là `decimal(4,2)`.
- `slv_3p_poi_rating.rating_overall` là `decimal(4,2)`.
- `slv_3p_poi_rating.rating_count` là `bigint`.

Nếu kiểu khác, node sẽ dừng với `ConfigError` trước khi ghi. Khi đó không chạy bước 4 và báo lại. Dán kết quả vào `evidence/results/runtime-p3.txt`.

### Bước 3: Cell `srvrevpy`, chạy hai lần

1. Mở `notebooks/NB_CREATE_DDL.ipynb` trên Fabric DEV. Chỉ chạy cell `srvrevpy`. Không chạy cả notebook và không chạy `enrflagpy`.
2. Cell này không có tham số. Các hằng số cố định trong cell:
   - `PL = "PL_VV_TRANS_SLV_TO_GLD_30M"`
   - `WID = "wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M"`
   - `LEASE_MINUTES = 90`
   - `ML_FQ = "lh_vv_silver.dbo.slv_enr_poi_review_multi_lang"`
   - `REVIEW_FQ = "lh_vv_gold.dbo.gld_srv_poi_review"`
   - `EDGES_ON`: (1, `slv_enr_poi_review_multi_lang`), (2, `slv_3p_poi_review`), (3, `slv_3p_poi_rating`). Cả ba cạnh đều có `trg_schema` `lh_vv_gold.dbo`, `trg_tbl` `gld_srv_poi_review`, `load_mode` `RECOMPUTE`, `nb_name` `NB_GLD_SRV_POI_REVIEW` và `priority` 1.
3. Lần 1: kỳ vọng dòng in ra có dạng `cột +[...]; tạo gold=...; cạnh ['slv_3p_poi_rating', 'slv_3p_poi_review', 'slv_enr_poi_review_multi_lang']`.
   - `cột +` là `[]`, `['title']` hoặc `['lang', 'title']`, tuỳ trạng thái ở B3.
   - `tạo gold=True` nếu ở B4 bảng gold chưa có.
4. Lần 2: chạy lại đúng cell `srvrevpy`. Kỳ vọng `cột +[]; tạo gold=False; cạnh ['slv_3p_poi_rating', 'slv_3p_poi_review', 'slv_enr_poi_review_multi_lang']`. Lần này không thêm cột, không CREATE, không thêm cạnh.
5. Dán dòng in ra của cả hai lần (cột, cờ tạo gold, cạnh) vào `evidence/results/runtime-ddl.txt`.

Nếu cell báo `Dừng trước khi ghi: ...`, `Luồng ... đang giữ khoá` hoặc `Sau khi ghi: ...`, dừng lại. Dán lỗi vào file và xử lý theo mục `Rollback và forward recovery`.

Lưu ý: sau lần chạy 1, ba cạnh đã active, nên tick NB_00 của GLD_30M có thể tự chạy node trước bước 4. Nếu điều đó xảy ra, ghi lại `exec_id` của run đó (xem `Kiểm tra log và watermark`).

### Bước 4: Notebook `NB_GLD_SRV_POI_REVIEW`, chạy ba lần

Tham số mặc định trong cell `srvrvparam`: `p_exec_id = ""`, `p_run_id = ""`, `p_pl_name = ""`, `p_trg_fq = ""`, `p_pinned_json = ""`, `p_mode = "RUN"`, `p_force = "false"`, `p_history_limit = "1000"`.

Khi chạy tay, giữ các giá trị mặc định ở trên, chỉ đổi các tham số sau:

| Lần | p_exec_id | p_run_id | p_pl_name | p_trg_fq | p_pinned_json | p_mode | p_force | p_history_limit |
|---|---|---|---|---|---|---|---|---|
| 4a | `""` | `""` | `"PL_VV_TRANS_SLV_TO_GLD_30M"` | `"lh_vv_gold.dbo.gld_srv_poi_review"` | `""` | `"DRY_RUN"` | `"false"` | `"1000"` |
| 4b | `""` | `""` | `"PL_VV_TRANS_SLV_TO_GLD_30M"` | `"lh_vv_gold.dbo.gld_srv_poi_review"` | `""` | `"RUN"` | `"false"` | `"1000"` |
| 4c | `""` | `""` | `"PL_VV_TRANS_SLV_TO_GLD_30M"` | `"lh_vv_gold.dbo.gld_srv_poi_review"` | `""` | `"RUN"` | `"false"` | `"1000"` |

- Trước 4a, sau 4b và sau 4c, chạy câu H1 ở mục `Chạy lại để kiểm tra idempotency` để ghi version của bảng gold.
- 4a (`DRY_RUN`): kỳ vọng các block `pk_null` và `pk_duplicate` trong `qg_json` đều bằng 0 và bảng gold không có version mới.
- 4b (`RUN`): ghi bằng MERGE theo `review_id`.
- 4c (`RUN` lần 2): không được commit. Version mới nhất của bảng gold phải giữ nguyên như sau 4b.
- Nếu node báo `QualityGateError` (trùng `poi_id` trong `slv_3p_poi_rating`, `pk_null` hoặc `pk_duplicate`) hoặc `ConfigError` (thiếu cột hoặc sai kiểu), node dừng trước khi ghi. Khi đó không chạy các lần tiếp theo và báo lại.
- Dán `qg_json` (câu L2) và exit payload của cả ba lần vào `evidence/results/runtime-node.txt`. Exit payload là giá trị trả về từ cell `srvrvexit`. Trước khi dán, xoá mọi giá trị văn bản tự do hoặc tên người nếu có.

## Kiểm tra kết quả

Chạy sau 4b. Tất cả đều chỉ đọc.

K1. Grain:
```sql
SELECT count(*) AS n, count(DISTINCT review_id) AS n_review_id,
       sum(CASE WHEN deleted_at IS NULL THEN 1 ELSE 0 END) AS n_live
FROM lh_vv_gold.dbo.gld_srv_poi_review;
```
Đạt khi `n = n_review_id`.

K2. Dòng gold không có trong `slv_3p_poi_review`:
```sql
SELECT count(*) AS n_missing
FROM lh_vv_gold.dbo.gld_srv_poi_review g
LEFT ANTI JOIN lh_vv_silver.dbo.slv_3p_poi_review r ON g.review_id = r.review_id;
```
Đạt khi `n_missing = 0`.

K3. Kiểu cột:
```sql
DESCRIBE lh_vv_gold.dbo.gld_srv_poi_review;
```
Đạt khi `rating` là `decimal(4,2)`, `rating_overall` là `decimal(4,2)` và `rating_count` là `bigint`. Thứ tự cột phải là `review_id, poi_id, lang, rating_overall, rating_count, title, review_text, rating, review_date, author_name, row_hash, created_at, updated_at, deleted_at`.

K4. Cạnh:
```sql
SELECT pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name, count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_schema = 'lh_vv_gold.dbo' AND trg_tbl = 'gld_srv_poi_review'
GROUP BY pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name;
```
Đạt khi có đúng 3 dòng, mỗi dòng `n = 1`, tất cả `pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30M'`, `src_schema = 'lh_vv_silver.dbo'`, `is_active = 1`, `priority = 1`, `load_mode = 'RECOMPUTE'` và `nb_name = 'NB_GLD_SRV_POI_REVIEW'`. Không có dòng nào thuộc pipeline khác.

K5. Schema silver sau patch:
```sql
DESCRIBE lh_vv_silver.dbo.slv_enr_poi_review_multi_lang;
```
Đạt khi thứ tự cột là `review_id, poi_id, lang, title, review_text, created_at, updated_at`.

K6. Mẫu dữ liệu không chứa dữ liệu cá nhân (tối đa 50 dòng):
```sql
SELECT review_id, poi_id, lang, rating, rating_overall, rating_count, deleted_at
FROM lh_vv_gold.dbo.gld_srv_poi_review
WHERE deleted_at IS NULL
ORDER BY review_id
LIMIT 50;
```

K7. Phân bố, chỉ đếm:
```sql
SELECT lang, count(*) AS n, sum(CASE WHEN rating_overall IS NULL THEN 1 ELSE 0 END) AS n_no_rating
FROM lh_vv_gold.dbo.gld_srv_poi_review
WHERE deleted_at IS NULL
GROUP BY lang
ORDER BY n DESC
LIMIT 50;
```

## Chạy lại để kiểm tra idempotency

H1. Lịch sử bảng gold. Chạy trước 4a, sau 4a, sau 4b và sau 4c:
```sql
SELECT version, timestamp, operation, operationMetrics
FROM (DESCRIBE HISTORY lh_vv_gold.dbo.gld_srv_poi_review LIMIT 20);
```
- Sau 4a: không có version mới so với trước 4a.
- Sau 4b: có version `MERGE` mới, trừ khi build không có dòng nào thay đổi.
- Sau 4c: version mới nhất giống hệt sau 4b. Nếu xuất hiện version mới, idempotency **không đạt**.

H2. Kiểm tra `srvrevpy` lần 2 không ghi gì:
- So với kết quả ngay sau lần 1, câu K4 vẫn trả về 3 dòng và `n = 1`.
- `SELECT max(id) FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` không đổi.
- K5 không đổi.
- Dòng in ra là `cột +[]; tạo gold=False; ...`.

H3. Kiểm tra chỉ số của lần 4c trong `ctrl_log_table_run` (câu L2): `inserted_rows`, `updated_rows` và `deactivated_rows` đều phải bằng 0. Giá trị `status` của lần 4c thì ghi đúng như trong log, không suy đoán.

## Kiểm tra log và watermark

L1. Khoá luồng. Chạy sau bước 3 và sau bước 4:
```sql
SELECT watermark_id, status, lock_exec_id, lock_at, error_message, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M';
```
- Sau `srvrevpy`, kỳ vọng `lock_exec_id` NULL, `lock_at` NULL và `status = 'SUCCESS'`. Cell nhả khoá trong `finally` và chỉ nhả khi khoá vẫn là `srvrev-...` của chính nó.
- Sau các lần chạy node, kỳ vọng `lock_exec_id` NULL. Ghi `status` đúng như thấy.

L2. Log node:
```sql
SELECT exec_id, run_id, pl_name, trg_tbl, status, entity_rows, inserted_rows, updated_rows, deactivated_rows,
       trg_version, started_at, ended_at, error_message, qg_json
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_tbl = 'gld_srv_poi_review'
ORDER BY started_at DESC
LIMIT 10;
```
- Kỳ vọng có một dòng cho mỗi lần 4a, 4b, 4c. Nếu có thêm dòng từ NB_00 thì ghi chú riêng.
- Trong `qg_json`, `mode` khớp `DRY_RUN`/`RUN`, và `blocks.pk_null = 0`, `blocks.pk_duplicate = 0`.
- Ghi lại `warns.enrich_without_review`, `warns.review_poi_id_mismatch` và `metrics.rating_matched`.

L3. Log run của luồng GLD_30M: chạy lại câu B6. Ghi lại các run NB_00 xuất hiện xen giữa bước 3 và bước 4, nếu có.

L4. Watermark cạnh, chỉ để đọc:
```sql
SELECT watermark_id, status, last_src_version, last_success_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_e__gld_srv_poi_review__%'
ORDER BY watermark_id
LIMIT 50;
```
Dòng `wm_e__` chỉ do NB_00 ghi, nên các lần chạy tay ở bước 4 không tạo dòng này. Sau tick NB_00 GLD_30M đầu tiên (bước 6 của Rollout), kỳ vọng có 3 dòng ứng với ba nguồn. Thời điểm kiểm tra sau tick: `<CẦN NGƯỜI DÙNG CUNG CẤP: thời điểm tick NB_00 GLD_30M đã quan sát>`.

## Rollback và forward recovery

- Rollback chỉ đi tiến. Task này không DROP, không DELETE, không TRUNCATE và không UPDATE `ctrl_mng_pipeline_config`. Bảng gold được giữ lại. Bên đọc lọc `deleted_at IS NULL`. Các cột silver nullable `lang` và `title` cũng được giữ, vì bên đọc hiện có chọn cột theo tên.
- Muốn ngừng lập lịch thì giao cho một task sau: đặt `is_active = 0` cho ba cạnh `gld_srv_poi_review` của `PL_VV_TRANS_SLV_TO_GLD_30M`. Không làm việc này trong task hiện tại.
- P4 cho thấy positional INSERT: không chạy `srvrevpy`. Chưa có gì được ghi. Báo lại để xử lý ở task khác.
- `srvrevpy` báo `Dừng trước khi ghi`: chưa có gì được ghi và khoá đã được nhả với `status = 'FAILED'`. Sửa nguyên nhân theo thông báo (thiếu nguồn, lệch schema silver, lệch cột gold, cạnh sai hoặc cạnh active ở pipeline khác), rồi chạy lại `srvrevpy`. Cell không tự sửa cạnh hoặc schema bị lệch.
- `srvrevpy` lỗi giữa chừng sau khi đã ghi một phần (ví dụ đã ALTER nhưng chưa CREATE hoặc INSERT): chạy lại `srvrevpy`. Lần chạy lại chấp nhận trạng thái thiếu `title`, thiếu `lang` và `title`, hoặc đủ cột. Nó dùng `CREATE TABLE IF NOT EXISTS` và `INSERT ... WHERE NOT EXISTS`, nên sẽ hoàn tất phần còn thiếu. Nếu lần chạy lại báo `Sau khi ghi: ...`, dừng và báo lại.
- `srvrevpy` báo `Luồng PL_VV_TRANS_SLV_TO_GLD_30M đang giữ khoá`: đợi run đang giữ khoá kết thúc rồi chạy lại.
- Khoá bị treo vì kernel bị dừng giữa cell: đợi hết lease 90 phút tính từ `lock_at`, rồi chạy lại. Runbook này không UPDATE tay dòng khoá.
- Node lỗi `QualityGateError` hoặc `ConfigError`: chưa ghi gì vào gold. Không thêm `.cast(` và không chọn dòng thủ công. Báo lỗi cùng `qg_json` để xử lý ở task sau.
- Lần 4c tạo version mới: idempotency không đạt. Không xoá version đó. Dán H1 và L2 rồi báo lại.
- Kiểu cột gold sai thì không sửa tại chỗ được. Invariant về kiểu dữ liệu chặn trường hợp này trước khi ghi. Nếu K3 vẫn sai, dừng và báo lại.

## Kết quả người dùng ghi nhận

Người dùng báo cáo 2026-10-27. Không suy đoán mục chưa được báo.

| Mục | Kết quả | File evidence |
|---|---|---|
| Workspace DEV | không nêu tên | |
| Baseline B1–B6 | B1 khoá SUCCESS, `lock_exec_id` null. B2 không có cạnh. B3 silver chưa có `lang`, `title`. B4 chưa có gold. B5 `multi_lang` 0, `review` 285, `rating` 345. B6 một run cũ `PARTIAL_FAILED`, không phải `RUNNING` | `evidence/results/runtime-baseline.txt` |
| Bước 1, P4: by-name/MERGE hay positional INSERT | WRITE Append và DELETE theo predicate. Không có positional INSERT | `evidence/results/runtime-p4.txt` |
| Bước 2, P3: kiểu `rating`, `rating_overall`, `rating_count` | `decimal(4,2)`, `decimal(4,2)`, `bigint` | `evidence/results/runtime-p3.txt` |
| Bước 3, `srvrevpy` lần 1: dòng in ra | `cột +['lang', 'title']; tạo gold=True; cạnh ['slv_3p_poi_rating', 'slv_3p_poi_review', 'slv_enr_poi_review_multi_lang']` | `evidence/results/runtime-ddl.txt` |
| Bước 3, `srvrevpy` lần 2: dòng in ra | `cột +[]; tạo gold=False; cạnh ['slv_3p_poi_rating', 'slv_3p_poi_review', 'slv_enr_poi_review_multi_lang']` | `evidence/results/runtime-ddl.txt` |
| Bước 4a, DRY_RUN: `qg_json`, exit payload, version gold | FAILED trước khi ghi. `QualityGateError`: đầu vào bắt buộc rỗng `slv_enr_poi_review_multi_lang`. exec `d76ab49d-09cb-4ba8-a867-931a56aac64d` | `evidence/results/runtime-node.txt` |
| Bước 4b, RUN: `qg_json`, exit payload, version gold | FAILED trước khi ghi. Cùng `QualityGateError`. exec `8a22bbac-8270-4a3d-a31c-fb4045e88b03` | `evidence/results/runtime-node.txt` |
| Bước 4c, RUN lần 2: `qg_json`, exit payload, version gold không đổi? | không chạy | |
| K1: `n` = `n_review_id` | không chạy. Node không ghi dòng | |
| K2: `n_missing` = 0 | không chạy | |
| K3: `rating decimal(4,2)`, `rating_count bigint` | không `DESCRIBE` lại gold. `tạo gold=True` ở lần 1 | |
| K4: 3 cạnh active, `n = 1` | không query lại. Lần 2 in đủ 3 cạnh và không thêm gì | |
| K5: thứ tự cột silver | không `DESCRIBE` lại. Lần 1 in `cột +['lang', 'title']` | |
| L1: khoá đã nhả, `status` | không báo lại sau khi chạy | |
| L3: run NB_00 xen giữa (nếu có) | không báo | |
| L4: `wm_e__` sau tick NB_00 | không chạy | |
| Kết luận PASS/FAIL và ghi chú | Khung DDL đạt và lần chạy lại không ghi thêm. Node dừng vì enrich rỗng. D-04 nhận khung bảng và khung transform; lần chạy khi có data thuộc task khác | |
