# Runtime runbook: 20261026-pl-name-cadence-suffix

Runbook này chưa được chạy. Mọi kết quả dưới đây là kết quả mong đợi. Người dùng điền kết quả thật vào mục `Kết quả người dùng ghi nhận`.

## Phạm vi và môi trường

- Môi trường: Fabric DEV. Workspace: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>`.
- Commit code đã sync: `<CẦN NGƯỜI DÙNG CUNG CẤP: commit hash chứa thay đổi của task; lúc viết runbook các thay đổi còn chưa commit>`.
- Mục tiêu cần chứng minh:
  1. Cell `plcadpy` trong `notebooks/NB_CREATE_DDL.ipynb` đổi tên các dòng ctrl.
  2. Chạy `plcadpy` lần hai không ghi gì.
  3. PLAN của hai tên mới không có WARN `Không đọc được nhịp`.
- Hai cặp đổi tên, lấy từ hằng `RENAMES` của `plcadpy`:

| pl_name cũ | pl_name mới | Hạn khoá (phút) | Id khoá cũ | Id khoá mới |
|---|---|---|---|---|
| `PL_VV_TRANS_SLV_TO_ENR_15P` | `PL_VV_TRANS_SLV_TO_ENR_15M` | 35 | `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` | `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M` |
| `PL_VV_TRANS_SLV_TO_GLD_30P` | `PL_VV_TRANS_SLV_TO_GLD_30M` | 90 | `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P` | `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` |

- Các bảng ctrl liên quan:
  - `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`: cell ghi cột `pl_name`.
  - `lh_vv_ctrl.dbo.ctrl_mng_watermark`: cell ghi `watermark_id` và `src_tbl` của dòng `wm_flow__`, cùng các cột khoá.
  - `lh_vv_ctrl.dbo.ctrl_log_run`: cell chỉ đọc, không sửa.
- Cell không đụng tới:
  - dòng cạnh `wm_e__`
  - log
  - lib `NB_LIB_TRANSFORM_SLV_GLD`
  - bảng dữ liệu silver và gold
- Cấm:
  - DROP, DELETE, TRUNCATE.
  - Xoá dòng watermark.
  - Run all `NB_CREATE_DDL`.
  - Chạy lại các cell cũ của `NB_CREATE_DDL` có tên `_15P` / `_30P`.
  - Chạy `NB_SETUP_POI_*` trước hoặc trong lúc chạy `plcadpy`.
- Mọi truy vấn kiểm tra trong runbook đều chỉ đọc. Chỉ có ba loại bước ghi:
  - hai lần chạy `plcadpy`
  - thao tác đổi tên và lịch pipeline trên Fabric
  - lần RUN theo lịch của `PL_VV_TRANS_SLV_TO_ENR_15M` sau khi resume
- Mẫu kết quả dán vào runbook tối đa 50 dòng. Bảng ctrl không có dữ liệu cá nhân. Không dán `run_params` hay `error_message` nếu trong đó có thông tin định danh người dùng.

## Điều kiện tiên quyết

1. Người chạy có quyền sửa workspace Fabric DEV: đổi tên pipeline, pause và resume lịch.
2. Kiểm thử local đã pass theo architecture:
   - `python -m pytest tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py tests/test_poi_media_amenity_contract.py tests/test_gld_srv_poi_contract.py -q`
   - `python -m pytest -q`
   - Kết quả: `<CẦN NGƯỜI DÙNG CUNG CẤP: output pytest>`.
3. Repo có pipeline JSON `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json` với các giá trị sau (đọc từ file):
   - `resources[0].name = PL_VV_TRANS_SLV_TO_ENR_15M`
   - activity `NB_00_ORCHES_SLV_TO_ENR_15P`, `policy.timeout = 0.00:32:00`, `retry = 0`
   - `concurrency = 1`
   - `p_pl_name = @pipeline().Pipeline`, `p_run_id = @pipeline().RunId`
   - `p_mode = RUN`, `p_max_parallel = 2`, `p_node_timeout_min = 15`, `p_dag_timeout_min = 25`, `p_lock_timeout_min = 35`
   - `p_force_nodes = ""`, `p_history_limit = 1000`, `p_non_data_ops = ""`
   - tham số pipeline `nb_orches_id`, `workspace_id`
   - guard `Validate_Notebook_Binding`
4. Giá trị `nb_orches_id` và `workspace_id` hiện đang gắn với pipeline Fabric `PL_VV_TRANS_SLV_TO_ENR_15P`: `<CẦN NGƯỜI DÙNG CUNG CẤP: hai giá trị này, ghi lại để giữ nguyên khi đổi tên>`.
5. Repo không có pipeline JSON `_30M`. Pipeline Fabric 30 phút hiện có: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên pipeline Fabric 30 phút hiện có (nếu có), lịch chạy, và có đang dùng p_pl_name = @pipeline().Pipeline không>`.
6. Cách sync notebook lên workspace: `<CẦN NGƯỜI DÙNG CUNG CẤP: Git integration / import / deploy>`.

## Baseline trước khi chạy

Bước R0. Chạy các truy vấn chỉ đọc sau trong một notebook Spark SQL trên `lh_vv_ctrl`. `LIMIT`, `<=>` và `DESCRIBE HISTORY` là cú pháp Spark. Không dùng `NB_CREATE_DDL` cho việc này. Lưu kết quả vào mục `Kết quả người dùng ghi nhận` (B1–B6).

B1. Số dòng cấu hình theo tên pl:

```sql
SELECT pl_name, count(*) AS n, sum(is_active) AS n_active
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name IN ('PL_VV_TRANS_SLV_TO_ENR_15P', 'PL_VV_TRANS_SLV_TO_ENR_15M',
                  'PL_VV_TRANS_SLV_TO_GLD_30P', 'PL_VV_TRANS_SLV_TO_GLD_30M')
GROUP BY pl_name
ORDER BY pl_name;
```

B2. Dòng khoá luồng:

```sql
SELECT watermark_id, src_tbl, flow_name, status, lock_exec_id, lock_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_flow__PL_VV_TRANS_SLV_TO_%'
   OR src_tbl IN ('PL_VV_TRANS_SLV_TO_ENR_15P', 'PL_VV_TRANS_SLV_TO_ENR_15M',
                  'PL_VV_TRANS_SLV_TO_GLD_30P', 'PL_VV_TRANS_SLV_TO_GLD_30M')
ORDER BY watermark_id
LIMIT 50;
```

B3. Số dòng cạnh. Con số này phải không đổi suốt runbook.

```sql
SELECT count(*) AS n_wm_e
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_e__%';
```

B4. Khoá logic có ở cả tên cũ và tên mới. Kết quả mong đợi: 0 dòng. Có dòng nào thì cell sẽ dừng trước khi ghi.

```sql
SELECT o.pl_name AS old_pl, o.src_tbl, o.trg_schema, o.trg_tbl
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config o
JOIN lh_vv_ctrl.dbo.ctrl_mng_pipeline_config n
  ON o.src_schema <=> n.src_schema AND o.src_tbl <=> n.src_tbl
 AND o.trg_schema <=> n.trg_schema AND o.trg_tbl <=> n.trg_tbl
WHERE (o.pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND n.pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15M')
   OR (o.pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30P' AND n.pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30M')
LIMIT 50;
```

B5. Run log `RUNNING` dưới tên cũ. Đây chỉ là con số đối chiếu với dòng in của cell; cell không sửa log.

```sql
SELECT pl_name, count(*) AS n_running
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name IN ('PL_VV_TRANS_SLV_TO_ENR_15P', 'PL_VV_TRANS_SLV_TO_GLD_30P')
  AND status = 'RUNNING'
GROUP BY pl_name;
```

B6. Version Delta mới nhất của hai bảng ctrl mà cell ghi:

```sql
DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_pipeline_config LIMIT 1;
DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_watermark LIMIT 1;
```

Ghi lại `version` và `timestamp` của từng bảng.

## Các bước thực hiện

### Bước 1 (R1): Pause lịch và xác nhận khoá trống

1. Trong Fabric DEV, pause lịch của pipeline `PL_VV_TRANS_SLV_TO_ENR_15P`.
2. Nếu pipeline 30 phút có lịch (điều kiện tiên quyết 5), pause luôn lịch đó: `<CẦN NGƯỜI DÙNG CUNG CẤP: xác nhận có / không có lịch 30 phút cần pause>`.
3. Trong Fabric Monitor, xác nhận không còn run nào đang chạy của các pipeline này.
4. Chạy lại truy vấn chỉ đọc:

```sql
SELECT watermark_id, lock_exec_id, lock_at, status
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN ('wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P', 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P');
```

5. Điều kiện để đi tiếp: mọi dòng trả về đều có `lock_exec_id` NULL. Nếu dòng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P` không tồn tại thì vẫn được đi tiếp; khi đó cell sẽ tạo `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`.
6. **DỪNG lấy bằng chứng.** Dán kết quả vào R1. Nếu `lock_exec_id` khác NULL, không chạy tiếp và không tự nhả khoá. Chờ run kết thúc, hoặc dừng lại để người dùng quyết định.

### Bước 2 (R2, R3): Sync notebook và chạy `plcadpy` lần một

1. Sync lên workspace các notebook đã đổi:
   - `NB_CREATE_DDL`
   - `NB_00_ORCHES_SLV_TO_ENR_15P`
   - `NB_SETUP_INITIAL_DDL`
   - `NB_SETUP_POI_ENTITY`
   - `NB_SETUP_POI_AMENITY`

   Không chạy `NB_SETUP_POI_ENTITY` hay `NB_SETUP_POI_AMENITY`. `plcadpy` phải chạy trước chúng.
2. Mở `NB_CREATE_DDL`. Kiểm tra hai cell cuối là `plcadmd` (markdown) và `plcadpy` (code), và `RENAMES` trong `plcadpy` đúng như bảng ở mục `Phạm vi và môi trường`.
3. Chỉ chạy cell `plcadpy`, bằng Run cell. Không Run all, không chạy cell nào khác của `NB_CREATE_DDL`.
4. Lưu nguyên văn output của cell vào R3.
5. Output mong đợi khi DEV đang ở trạng thái tên cũ, mỗi cặp một dòng:
   - `PL_VV_TRANS_SLV_TO_ENR_15P -> PL_VV_TRANS_SLV_TO_ENR_15M: cạnh <số dòng B1 của 15P>, khoá đổi id, run log RUNNING tên cũ <số B5 của 15P> (không sửa log)`
   - `PL_VV_TRANS_SLV_TO_GLD_30P -> PL_VV_TRANS_SLV_TO_GLD_30M: cạnh <số dòng B1 của 30P>, khoá <đổi id | giữ wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M>, run log RUNNING tên cũ <số B5 của 30P> (không sửa log)`

   Khoá là `đổi id` nếu B2 có `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P`, và `giữ wm_flow__…_30M` nếu chưa có.
6. Nếu một cặp không còn dòng tên cũ nào, dòng của cặp đó là `<cũ> -> <mới>: đã đổi, không ghi`.
7. Điểm dừng:
   - Output có `Dừng trước khi ghi`: **DỪNG chờ người dùng quyết định.** Cặp đó chưa ghi gì. Đây có thể là trường hợp có cả hai dòng khoá, id khoá trùng, dòng watermark lạ có `src_tbl` là tên pl, hoặc cạnh có ở cả tên cũ và tên mới. Không tự xoá dòng nào. Người dùng chọn một trong hai: tự gỡ dòng thừa, hoặc giữ nguyên và revert.
   - Output có `đang giữ khoá … chạy lại sau`: có run khác đang giữ khoá. Quay lại Bước 1.
   - Output có `mất khoá` hoặc `Sau khi ghi`: **DỪNG.** Chạy các probe ở mục `Kiểm tra kết quả` và không tự sửa gì.
   - Lỗi Delta tạm thời (`ConcurrentAppend` / `ConcurrentDeleteRead`): chạy lại cell `plcadpy`. Cell hội tụ khi chạy lại.

### Bước 3 (R4): Chạy `plcadpy` lần hai

1. Ghi lại B6 (DESCRIBE HISTORY) ngay trước lần chạy này. Đây là mốc A0.
2. Chạy lại cell `plcadpy`, chỉ cell này.
3. Output mong đợi, đúng hai dòng:
   - `PL_VV_TRANS_SLV_TO_ENR_15P -> PL_VV_TRANS_SLV_TO_ENR_15M: đã đổi, không ghi`
   - `PL_VV_TRANS_SLV_TO_GLD_30P -> PL_VV_TRANS_SLV_TO_GLD_30M: đã đổi, không ghi`
4. Kiểm tra theo mục `Chạy lại để kiểm tra idempotency`.

### Bước 4 (R5): Đổi tên pipeline ENR trên Fabric và resume lịch

1. Đổi tên pipeline Fabric `PL_VV_TRANS_SLV_TO_ENR_15P` thành `PL_VV_TRANS_SLV_TO_ENR_15M`. Cách khác là import `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json`.
2. Kiểm tra trên Fabric:
   - Activity tên `NB_00_ORCHES_SLV_TO_ENR_15P`, không đổi.
   - `p_pl_name = @pipeline().Pipeline`, nên sau khi đổi tên sẽ tự ra `PL_VV_TRANS_SLV_TO_ENR_15M`.
   - Timeout `0.00:32:00`.
   - `p_lock_timeout_min = 35`.
   - `concurrency = 1`.
   - `nb_orches_id` và `workspace_id` giữ đúng giá trị đã ghi ở điều kiện tiên quyết 4, không trống và không chứa `PENDING`.
3. Kiểm tra lịch vẫn gắn với pipeline đã đổi tên, rồi resume lịch.
4. Không đổi tên pipeline trước Bước 2. Nếu NB_00 chạy với tên mới khi config còn tên cũ, nó sẽ raise `ConfigError` vì không có cạnh. Run đó không ghi gì nhưng vẫn là lỗi.

### Bước 5 (R6): Pipeline 30 phút

1. Repo không có JSON `_30M`. Tạo mới hoặc đổi tên pipeline Fabric 30 phút thành `PL_VV_TRANS_SLV_TO_GLD_30M` trước mọi lần chạy tay với `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_30M`. Cấu hình activity: `<CẦN NGƯỜI DÙNG CUNG CẤP: notebook đích, nb_orches_id, workspace_id, lịch của pipeline 30M>`.
2. Nếu pipeline dùng `p_pl_name = @pipeline().Pipeline`, tên pipeline phải đúng chính xác `PL_VV_TRANS_SLV_TO_GLD_30M`.
3. Chưa resume lịch 30M trước khi xong Bước 6 và có điều kiện R8 (Bước 7).

### Bước 6 (R7): PLAN kiểm tra nhịp

PLAN chỉ in kế hoạch và DAG. Nó không khoá, không ghi bảng và không ghi `ctrl_log_run`. Đặt tham số trong phiên chạy và không lưu thay đổi tham số vào notebook trên workspace.

PLAN 1. Notebook `NB_00_ORCHES_SLV_TO_ENR_15P`, tham số:

| Tham số | Giá trị |
|---|---|
| `p_pl_name` | `PL_VV_TRANS_SLV_TO_ENR_15M` |
| `p_run_id` | `""` |
| `p_mode` | `PLAN` |
| `p_max_parallel` | `2` |
| `p_node_timeout_min` | `15` |
| `p_dag_timeout_min` | `25` |
| `p_lock_timeout_min` | `35` |
| `p_force_nodes` | `""` |
| `p_history_limit` | `1000` |
| `p_non_data_ops` | `""` |

Các giá trị này trùng với parameter cell trong repo, chỉ khác `p_mode` (repo là `RUN`).

PLAN 2. Notebook `NB_00_ORCHES_SLV_TO_GLD`. Chỉ đổi hai tham số, các tham số khác giữ như parameter cell trong repo:

| Tham số | Giá trị |
|---|---|
| `p_pl_name` | `PL_VV_TRANS_SLV_TO_GLD_30M` (repo đang là `PL_VV_TRANSFORM_SLV_TO_GLD_1H`) |
| `p_mode` | `PLAN` (repo đang là `RUN`) |
| `p_run_id` | `""` (giữ) |
| `p_max_parallel` | `3` (giữ) |
| `p_node_timeout_min` | `20` (giữ) |
| `p_dag_timeout_min` | `45` (giữ) |
| `p_lock_timeout_min` | `90` (giữ) |
| `p_force_nodes` | `""` (giữ) |
| `p_history_limit` | `1000` (giữ) |
| `p_non_data_ops` | `""` (giữ) |

Tiêu chí đạt cho cả hai lần PLAN:
- Không có WARN `Không đọc được nhịp` nhắc tới `PL_VV_TRANS_SLV_TO_ENR_15M` hoặc `PL_VV_TRANS_SLV_TO_GLD_30M`.
- Không có `ConfigError`.

Điểm dừng:
- `ConfigError` về nhịp (`đọc node … của luồng chậm hơn`): đây là vi phạm cấu hình thật trên DEV. **DỪNG chờ người dùng quyết định.** Không sửa config trong task này.
- `ConfigError` vì không có cạnh `RECOMPUTE`: config chưa đổi tên. **DỪNG**, quay lại kiểm tra R3 và R4.
- WARN `(node của PL_VV_TRANS_SLV_TO_ENR_15M) chưa có output_versions_json` trong PLAN 2: chấp nhận được. WARN này hết sau khi ENR_15M có một RUN SUCCESS hoặc NO_DATA (Bước 7).

PLAN 3 (tuỳ chọn). Chạy `NB_00_ORCHES_SLV_TO_GLD` với `p_mode = PLAN` và `p_pl_name` của luồng 1 giờ. Mong đợi: hết WARN về ENR. Parameter cell trong repo ghi `PL_VV_TRANSFORM_SLV_TO_GLD_1H`, còn architecture ghi `PL_VV_TRANS_SLV_TO_GLD_1H`. Tên đúng trên DEV: `<CẦN NGƯỜI DÙNG CUNG CẤP: pl_name thật của luồng gold 1 giờ>`.

### Bước 7 (R8): Thứ tự RUN đầu tiên

1. Để `PL_VV_TRANS_SLV_TO_ENR_15M` hoàn tất một RUN theo lịch, với trạng thái `SUCCESS` hoặc `NO_DATA`. RUN này phải xong trước RUN kế tiếp của `PL_VV_TRANS_SLV_TO_GLD_30M` hoặc luồng GLD_1H.
2. Xác nhận bằng truy vấn L2 ở mục `Kiểm tra log và watermark`.
3. Sau đó mới resume hoặc chạy pipeline 30M. Với GLD_1H: `<CẦN NGƯỜI DÙNG CUNG CẤP: lịch GLD_1H có cần pause tạm đến khi ENR_15M có RUN đầu tiên không>`.

## Kiểm tra kết quả

Chạy sau Bước 2 (R3), mỗi truy vấn đều chỉ đọc.

K1. Chạy lại B1. Mong đợi:
- Không có dòng `PL_VV_TRANS_SLV_TO_ENR_15P` hay `PL_VV_TRANS_SLV_TO_GLD_30P`.
- `n` của `PL_VV_TRANS_SLV_TO_ENR_15M` = B1(15P) + B1(15M).
- `n` của `PL_VV_TRANS_SLV_TO_GLD_30M` = B1(30P) + B1(30M).
- `n_active` cộng dồn tương tự.

K2. Chạy lại B2. Mong đợi:
- Không còn dòng `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` hay `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P`.
- Không còn dòng có `src_tbl` là tên cũ.
- Có đúng 1 dòng `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M` với `src_tbl = PL_VV_TRANS_SLV_TO_ENR_15M`, và đúng 1 dòng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` với `src_tbl = PL_VV_TRANS_SLV_TO_GLD_30M`.
- Cả hai có `lock_exec_id` NULL, `lock_at` NULL, `status = SUCCESS`.

K3. Chạy lại B3. Mong đợi: `n_wm_e` bằng đúng giá trị baseline.

K4. Khoá logic trùng dưới tên mới. Mong đợi: 0 dòng.

```sql
SELECT pl_name, src_schema, src_tbl, trg_schema, trg_tbl, count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name IN ('PL_VV_TRANS_SLV_TO_ENR_15M', 'PL_VV_TRANS_SLV_TO_GLD_30M')
GROUP BY pl_name, src_schema, src_tbl, trg_schema, trg_tbl
HAVING count(*) > 1
LIMIT 50;
```

K5. Mẫu cạnh dưới tên mới. Chỉ để đối chiếu, tối đa 50 dòng.

```sql
SELECT pl_name, src_tbl, trg_schema, trg_tbl, is_active, load_mode
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name IN ('PL_VV_TRANS_SLV_TO_ENR_15M', 'PL_VV_TRANS_SLV_TO_GLD_30M')
ORDER BY pl_name, trg_tbl, src_tbl
LIMIT 50;
```

Nếu một tiêu chí không đạt: **DỪNG**, dán kết quả, không tự sửa.

## Chạy lại để kiểm tra idempotency

Sau Bước 3 (R4):

1. Output của `plcadpy` lần hai có đúng hai dòng kết thúc bằng `đã đổi, không ghi`.
2. Chạy lại B6. Mong đợi: `version` mới nhất của `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` và của `lh_vv_ctrl.dbo.ctrl_mng_watermark` bằng đúng mốc A0. Lần chạy hai không nhận khoá, nên `status` và `updated_at` của dòng khoá cũng không đổi.
3. Chạy lại B1, B2, B3. Kết quả phải giống hệt K1, K2, K3, kể cả `updated_at` của hai dòng `wm_flow__…M`. Đây là bộ probe "after" của R4.

Nếu version Delta tăng, hoặc output khác `đã đổi, không ghi`: **DỪNG**, dán bằng chứng.

## Kiểm tra log và watermark

L1. Run log dưới tên cũ:

```sql
SELECT pl_name, status, count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name IN ('PL_VV_TRANS_SLV_TO_ENR_15P', 'PL_VV_TRANS_SLV_TO_GLD_30P')
GROUP BY pl_name, status
ORDER BY pl_name, status;
```

Mong đợi: số dòng `RUNNING` bằng B5 và bằng con số `run log RUNNING tên cũ` mà `plcadpy` in ra. Các dòng này chỉ là log, cell không sửa chúng và chúng không ảnh hưởng điều khiển.

L2. Các run dưới tên mới, chạy sau khi resume lịch (Bước 4 và Bước 7):

```sql
SELECT exec_id, run_id, pl_name, status, started_at, ended_at, duration_ms,
       tbl_total_count, tbl_success_count, tbl_failed_count, tbl_no_data_count,
       output_versions_json IS NOT NULL AS has_output_versions
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name IN ('PL_VV_TRANS_SLV_TO_ENR_15M', 'PL_VV_TRANS_SLV_TO_GLD_30M')
ORDER BY started_at DESC
LIMIT 50;
```

Mong đợi:
- RUN đầu tiên của `PL_VV_TRANS_SLV_TO_ENR_15M` có `status` `SUCCESS` hoặc `NO_DATA` và `has_output_versions = true`.
- `started_at` của RUN đầu tiên của `PL_VV_TRANS_SLV_TO_GLD_30M` (nếu có) muộn hơn `ended_at` của RUN đó.
- Lần PLAN không tạo dòng log.

L3. Dòng khoá sau RUN ENR_15M: chạy lại B2. Mong đợi:
- `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M` có `lock_exec_id` NULL sau khi run kết thúc, và `status` bằng trạng thái run.
- Không xuất hiện lại `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`. Nếu nó xuất hiện lại, có cell cũ hoặc pipeline tên cũ vừa chạy. **DỪNG.**

L4. Chạy lại B3. `n_wm_e` có thể đổi sau RUN thật nếu NB_00 chèn cạnh mới. Bản thân `plcadpy` không được làm đổi con số này, nên so sánh với K3 chứ không so với giá trị sau RUN.

## Rollback và forward recovery

- **Forward recovery (ưu tiên):**
  - Nếu PLAN cho thấy vi phạm nhịp thật, sửa config trong một task mới.
  - Việc đổi tên không đổi dữ liệu, không đổi hộp thư `wm_e__` và không đổi append marker. Không cần tính lại node nào.
- **Dừng giữa chừng:**
  - Cell hội tụ khi chạy lại, nên sửa nguyên nhân rồi chạy lại riêng `plcadpy`.
  - Nếu driver chết khi đang giữ khoá, chờ hết hạn khoá (35 phút cho ENR, 90 phút cho GLD30) rồi chạy lại.
  - Không tự nhả khoá và không xoá dòng.
- **Rollback:**
  - Repo: `git revert` commit code (`<CẦN NGƯỜI DÙNG CUNG CẤP: commit hash>`).
  - Fabric: đổi tên pipeline về `PL_VV_TRANS_SLV_TO_ENR_15P`, và pipeline 30 phút về tên cũ nếu đã đổi, giữ nguyên `nb_orches_id` và `workspace_id`.
  - ctrl: chạy cùng thuật toán với cặp đảo ngược (mới → cũ). Thuật toán này phải được giao dưới dạng một cell `NB_CREATE_DDL` mới có ngày, thuộc một task id mới, và chưa có trong repo. Không viết UPDATE tay. Không DROP, không DELETE, không xoá watermark.
- Sau rollback, kiểm tra nhịp quay về chế độ WARN rồi bỏ qua. Dòng cạnh không bị đụng nên không node nào phải tính lại.

## Kết quả người dùng ghi nhận

Điền sau khi chạy. Mỗi mẫu tối đa 50 dòng, không có dữ liệu cá nhân.

- Người chạy / thời điểm (UTC): `<CẦN NGƯỜI DÙNG CUNG CẤP>`
- Workspace DEV / commit đã sync: `<CẦN NGƯỜI DÙNG CUNG CẤP>`

| Mục | Kết quả |
|---|---|
| B1 cấu hình theo pl (trước) | `ENR_15P` 21 dòng, 20 active. `GLD_30P` 12 dòng, 12 active. Không có dòng `15M`/`30M`. |
| B2 dòng khoá (trước) | `wm_flow__ENR_15P` `NO_DATA`, `lock_exec_id` null. `wm_flow__GLD_30P` `PARTIAL_FAILED`, `lock_exec_id` null. Thêm `wm_flow__PL_VV_TRANS_SLV_TO_GLD_1H` `NO_DATA`, `lock_exec_id` null. |
| B3 `n_wm_e` (trước) | 34 |
| B4 khoá logic trùng cũ/mới | 0 dòng |
| B5 run log RUNNING tên cũ | 0 dòng |
| B6 version Delta (trước) | config: 24, watermark: 225 |
| R1 đã pause lịch 15P (và 30 phút nếu có), Monitor không có run | `<có/không + ảnh/ghi chú>` |
| R1 `lock_exec_id` của hai khoá cũ | `<dán>` |
| R3 output `plcadpy` lần 1 (nguyên văn) | Lần lỗi: `DELTA_UNSUPPORTED_SUBQUERY`, không ghi. Lần chạy lại sau khi bỏ subquery: `ENR_15P -> ENR_15M: cạnh 21, khoá đổi id, run log RUNNING tên cũ 0`. `GLD_30P -> GLD_30M: cạnh 12, khoá đổi id, run log RUNNING tên cũ 0`. |
| K1–K5 | K1: `ENR_15M` 21/20, `GLD_30M` 12/12, không còn tên cũ. K2: đúng một khóa mỗi tên mới, `lock_exec_id` null, `status` `SUCCESS`; `GLD_1H` còn, `updated_at` 2026-10-26T04:13:48Z. K3: `n_wm_e` 34. K4: 0 dòng. K5: 33 cạnh, một cạnh inactive `slv_3p_poi_opening_hours` -> `gld_enr_poi_info`. |
| A0 version Delta trước lần 2 | config: 26 lúc 2026-10-26T07:32:19Z, watermark: 238 lúc 2026-10-26T07:32:29Z |
| R4 output `plcadpy` lần 2 (nguyên văn) | `ENR_15P -> ENR_15M: đã đổi, không ghi`. `GLD_30P -> GLD_30M: đã đổi, không ghi`. |
| R4 version Delta sau lần 2 | config: 26 lúc 2026-10-26T07:32:19Z, watermark: 238 lúc 2026-10-26T07:32:29Z. Bằng A0. |
| R4 probe B1/B2/B3 sau lần 2 | B1 giống K1: `ENR_15M` 21/20, `GLD_30M` 12/12. B2 ba khóa và `updated_at` không đổi. B3 `n_wm_e` 34. |
| R5 pipeline đã đổi tên `PL_VV_TRANS_SLV_TO_ENR_15M`, binding giữ nguyên, lịch đã resume | Pipeline Fabric được đổi thành `PL_VV_TRANS_SLV_TO_ENR` để dùng lại. Ctrl vẫn là `PL_VV_TRANS_SLV_TO_ENR_15M`. Activity phải truyền literal `p_pl_name = PL_VV_TRANS_SLV_TO_ENR_15M`. `@pipeline().Pipeline` sẽ ra `PL_VV_TRANS_SLV_TO_ENR` và không có cạnh. |
| R6 pipeline `PL_VV_TRANS_SLV_TO_GLD_30M` đã tạo/đổi tên | `<có/không + ghi chú>` |
| R7 PLAN ENR_15M: có WARN `Không đọc được nhịp`? có ConfigError? | Không. Log `NB_00 PL_VV_TRANS_SLV_TO_ENR_15M mode PLAN`: 4 node, 20 cạnh, 0 Dirty Edge, `status` `PLAN`. |
| R7 PLAN GLD_30M: có WARN `Không đọc được nhịp`? có ConfigError? | Không. Log `NB_00 PL_VV_TRANS_SLV_TO_GLD_30M mode PLAN`: 4 node, 12 cạnh, `status` `PLAN`. WARN được chấp nhận: `slv_poi_entity_non_enrich` của `PL_VV_TRANS_SLV_TO_ENR_15M` chưa có `output_versions_json`, đọc version 4. 3 Dirty Edge `NEW_EDGE` vào `gld_srv_poi_multi_lang`, 1 node ứng viên `NB_GLD_SRV_POI_MULTI_LANG`. Lần PLAN trước đó là `PL_VV_TRANS_SLV_TO_GLD_1H`, không tính. |
| R8 / L2 RUN đầu của ENR_15M xong trước RUN GLD_30M / GLD_1H | Pipeline `PL_VV_TRANS_SLV_TO_ENR`, `p_pl_name` literal `PL_VV_TRANS_SLV_TO_ENR_15M`, `p_mode` `RUN`. Log `NB_00 PL_VV_TRANS_SLV_TO_ENR_15M mode RUN`: 4 node, 20 cạnh, 0 Dirty Edge. Kết thúc `NO_DATA` sau 53s, `error` null, `tbl_failed_count` 0. Chưa có RUN `GLD_30M` sau mốc này. |
| L1 run log tên cũ | `<dán>` |
| L3 dòng khoá sau RUN | `<dán>` |
| Điểm dừng đã gặp (nếu có) và quyết định của người dùng | 2026-10-26: chấp nhận bỏ review round 4. |
