# Hướng dẫn kiểm chứng runtime

Trạng thái: `ĐÃ CHẤP NHẬN RỦI RO`. Schedule `PL_VV_TRANS_SLV_TO_ENR_15P` vẫn tắt. D-16.

Chỉ Fabric DEV. Không chạy trên staging hay production. Agent không chạy các bước này. Tối đa 50 dòng mỗi kết quả, không dữ liệu cá nhân, không secret. Gặp `Dừng trước khi ghi` thì dừng và dán lỗi. Không sửa cell để vòng qua lỗi đó.

## Phạm vi và môi trường

Fabric DEV, workspace đang đồng bộ repo này. Lakehouse `lh_vv_ctrl`, `lh_vv_silver`, `lh_vv_gold`. Pipeline `PL_VV_TRANS_SLV_TO_ENR_15P`. Notebook `NB_CREATE_DDL` cell `mvpoipy`, `NB_00_ORCHES_SLV_TO_ENR_15P`, `NB_SETUP_POI_AMENITY`.

R0 đến R5 là lần chạy này. Dừng sau R5. R6 chỉ chạy sau khi người dùng xác nhận backup. R7 và R8 chạy sau DROP.

## Điều kiện tiên quyết

- Review vòng 3 đã PASS. Change set đã có cell `mvpoipy` và đã xóa `NB_SLV_PN_POI`, `NB_ENR_POI_COORDINATE`.
- Commit và đẩy change set lên đúng nhánh mà workspace DEV đồng bộ. Repo local đang ở nhánh `main`.
- `PL_VV_TRANS_SLV_TO_SLV_1H` không phải item pipeline. Không tắt item đó.
- Không chạy cell lịch sử `entwebpy` hay `enrddlpy`.

## Baseline trước khi chạy

Probe 2026-10-21: `gld_enr_poi_coordinate` 94 dòng, `slv_pn_poi` 30 dòng. Số dòng tại R0 là mốc so với backup. Khoá `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` phải null trước R2.

## Các bước thực hiện

### R0. Pre-flight, chỉ đọc

Chạy từng câu trong notebook Spark DEV. Dán vào `.ai/tasks/20261021-move-poi-nodes-enr-15p-cleanup/evidence/results/runtime-r0.txt`.

1. Khoá luồng:

```sql
SELECT watermark_id, lock_exec_id, lock_at, status
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_flow__PL_VV_TRANS_SLV_TO_%'
```

2. Registry. Đạt khi `n = 0`. `n` khác 0 là quyết định của người dùng. Dừng, không sang R1.

```sql
SELECT count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_cfg_schema_registry
WHERE src_tbl IN ('slv_pn_poi', 'gld_enr_poi_coordinate')
   OR trg_tbl IN ('slv_pn_poi', 'gld_enr_poi_coordinate')
```

3. Ghi `V_cfg` và `V_wm` là cột `version` của mỗi câu:

```sql
DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_pipeline_config LIMIT 1
```

```sql
DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_watermark LIMIT 1
```

4. Với `lh_vv_gold.enr.gld_enr_poi_coordinate` và `lh_vv_silver.dbo.slv_pn_poi`, chạy `DESCRIBE TABLE`, `DESCRIBE DETAIL`, và `count(*)`. Ghi hai số dòng này. Đó là mốc backup. Không dùng `SHOW CREATE TABLE`: Spark trên Fabric trả `DELTA_OPERATION_NOT_ALLOWED` với bảng Delta.

### R1. Tạm dừng schedule

Tắt schedule của `PL_VV_TRANS_SLV_TO_ENR_15P` trên DEV. Chạy lại câu khoá cho đúng một id:

```sql
SELECT watermark_id, lock_exec_id, lock_at, status
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P'
```

Đạt khi `lock_exec_id` null. Nếu chưa null, chờ run hiện tại kết thúc. Không chiếm khoá. Lease tối đa 35 phút.

### R2. Đồng bộ workspace

Đồng bộ workspace DEV từ git. Xác nhận item `NB_SLV_PN_POI` và `NB_ENR_POI_COORDINATE` không còn. Cell `mvpoipy` có trong `NB_CREATE_DDL`.

### R3. Chạy patch một lần

Trong `NB_CREATE_DDL`, chỉ chạy cell `mvpoipy`. Không chạy cell khác.

Đạt khi output có `đã xoá cạnh=8 watermark=6; watermark giữ lại=17`.

### R4. Chạy lại patch

Chạy lại chỉ cell `mvpoipy`.

Đạt khi output có `đã xoá cạnh=0 watermark=0; watermark giữ lại=17`.

### R5. PLAN

Chạy `NB_00_ORCHES_SLV_TO_ENR_15P` với tham số:

- `p_pl_name` = `PL_VV_TRANS_SLV_TO_ENR_15P`
- `p_run_id` = `""`
- `p_mode` = `PLAN`
- `p_max_parallel` = `2`
- `p_node_timeout_min` = `15`
- `p_dag_timeout_min` = `25`
- `p_lock_timeout_min` = `35`
- `p_force_nodes` = `""`
- `p_history_limit` = `1000`
- `p_non_data_ops` = `""`

Dán plan và `run_multiple_dag`. Đạt khi activity amenity phụ thuộc entity, activity info phụ thuộc cả hai, không có activity `slv_pn_poi` hay coordinate, không có ConfigError.

Chạy `NB_SETUP_POI_AMENITY` với `p_apply` = `false`. Đạt khi `entity_edges_ok=6`. Không đặt `p_apply` thành `true`.

PLAN chỉ đưa node ứng viên vào `activities`. Khi không có Dirty Edge và `p_force_nodes` trống, `activities` rỗng là kết quả của lần đọc này. Lần đó chưa chứng minh thứ tự entity, amenity, info.

### R5b. PLAN có ép node, chỉ đọc

Chạy lại `NB_00_ORCHES_SLV_TO_ENR_15P`. Giữ tham số R5, đổi `p_force_nodes` = `slv_poi_entity_non_enrich,slv_poi_amenity,gld_enr_poi_info`. `p_mode` vẫn là `PLAN`. PLAN trả trước khi ghi.

Đạt khi activity amenity có dependency tới entity, và activity info có dependency tới cả entity và amenity. Không có activity `slv_pn_poi` hay coordinate. Không ConfigError.

Chạy `NB_SETUP_POI_AMENITY` với `p_apply` = `false` nếu lần R5 chưa dán `entity_edges_ok`. Đạt khi `entity_edges_ok=6`.

Trước R6, hai số dòng đã có: coordinate 94, `slv_pn_poi` 30. Số backup phải bằng đúng hai số này.

Dừng tại đây. Không chạy R6 cho đến khi được xác nhận.

### R6. Backup và DROP

Chỉ chạy sau xác nhận của người dùng. DROP xóa file của bảng managed. Time travel không khôi phục được.

1. Câu cửa. Chỉ tiếp tục khi `n = 0`:

```sql
SELECT count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE src_tbl IN ('slv_pn_poi', 'gld_enr_poi_coordinate')
   OR trg_tbl IN ('slv_pn_poi', 'gld_enr_poi_coordinate')
```

2. Lưu cột trước khi backup. `SHOW CREATE TABLE` không chạy trên Delta. Dán `col_name` và `data_type`. Với `DESCRIBE DETAIL`, chỉ dán `format`, `partitionColumns`, `numFiles`. Bỏ đường dẫn `abfss`.

```sql
DESCRIBE TABLE lh_vv_gold.enr.gld_enr_poi_coordinate
```

```sql
DESCRIBE DETAIL lh_vv_gold.enr.gld_enr_poi_coordinate
```

```sql
DESCRIBE TABLE lh_vv_silver.dbo.slv_pn_poi
```

```sql
DESCRIBE DETAIL lh_vv_silver.dbo.slv_pn_poi
```

3. Backup:

```sql
CREATE TABLE lh_vv_silver.dbo.gld_enr_poi_coordinate_bak_20261021
AS SELECT * FROM lh_vv_gold.enr.gld_enr_poi_coordinate
```

```sql
CREATE TABLE lh_vv_silver.dbo.slv_pn_poi_bak_20261021
AS SELECT * FROM lh_vv_silver.dbo.slv_pn_poi
```

4. `count(*)` mỗi bảng backup phải bằng đúng số dòng R0 của bảng gốc: coordinate 94, `slv_pn_poi` 30.

5. Sau khi người dùng xác nhận số backup:

```sql
DROP TABLE IF EXISTS lh_vv_gold.enr.gld_enr_poi_coordinate
```

```sql
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_pn_poi
```

6. `spark.catalog.tableExists`: coordinate False, `slv_pn_poi` False, `gld_enr_poi_info` True, `gld_enr_poi_review` True.

### R7. RUN cưỡng bức hai node

Chạy `NB_00_ORCHES_SLV_TO_ENR_15P`. Giữ mọi tham số R5, đổi:

- `p_mode` = `RUN`
- `p_force_nodes` = `slv_poi_entity_non_enrich,slv_poi_amenity`

Không đưa `gld_enr_poi_info` vào `p_force_nodes`.

Dán các dòng `ctrl_log_table_run` của `exec_id` đó:

```sql
SELECT exec_id, trg_tbl, status, started_at, ended_at
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE exec_id = '<exec_id của lần RUN>'
ORDER BY started_at
```

Đạt khi entity kết thúc trước lúc amenity bắt đầu, và status của run là SUCCESS.

### R8. Bật lại schedule

Bật schedule `PL_VV_TRANS_SLV_TO_ENR_15P`. Dán dòng `ctrl_log_run` của lần schedule kế tiếp. SUCCESS hoặc NO_DATA đều đạt. Chạy lại `evidence/probes/ctrl-inventory.sql`. Đạt khi INV-1 = 16, INV-3 = 17, INV-5 và INV-6 báo không tìm thấy bảng, INV-7 và INV-8 trả một số đếm.

## Kiểm tra kết quả

- R0: registry `n = 0`, hai version history đã ghi, hai `count(*)` đã ghi.
- R3: `cạnh=8 watermark=6`, watermark giữ lại `17`.
- R4: `cạnh=0 watermark=0`, watermark giữ lại `17`.
- R5: DAG entity rồi amenity rồi info. `entity_edges_ok=6`.
- R6 đến R8: theo từng bước ở trên, sau khi được phép chạy.

## Chạy lại để kiểm tra idempotency

R4 là lần chạy lại của R3. Lần hai không xóa thêm cạnh hay watermark. Không chạy R3 thêm lần thứ ba nếu R4 đã in `0/0`.

## Kiểm tra log và watermark

R3 và R4 in số cạnh và watermark đã xóa. Sau mỗi lần, khoá `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` được nhả: `lock_exec_id` null. Nếu cell dừng giữa hai `DELETE`, watermark mồ côi còn lại. Chạy lại `mvpoipy`. Không `RESTORE` bảng ctrl.

R7 kiểm tra `ctrl_log_table_run`. R8 kiểm tra `ctrl_log_run` của lần schedule.

## Rollback và forward recovery

Ưu tiên chạy lại bước lỗi. Cửa sổ rollback là retention Delta của bảng ctrl, mặc định 7 ngày, cộng hai bảng backup.

Thứ tự rollback:

1. Tắt schedule `PL_VV_TRANS_SLV_TO_ENR_15P`.
2. `git revert` change set và đồng bộ workspace, để `NB_SLV_PN_POI` và `NB_ENR_POI_COORDINATE` trở lại trước các cạnh.
3. Tạo lại hai bảng bằng CTAS từ backup, vì `SHOW CREATE TABLE` không chạy trên Delta. Với riêng `slv_pn_poi`, có thể để NB_00 tính lại sau khi cạnh được khôi phục.

```sql
CREATE TABLE lh_vv_gold.enr.gld_enr_poi_coordinate
AS SELECT * FROM lh_vv_silver.dbo.gld_enr_poi_coordinate_bak_20261021
```

```sql
CREATE TABLE lh_vv_silver.dbo.slv_pn_poi
AS SELECT * FROM lh_vv_silver.dbo.slv_pn_poi_bak_20261021
```
4. Chèn lại dòng ctrl từ version R0. Không `RESTORE` cả bảng, vì lệnh đó lùi luôn watermark do NB_00 ghi sau đó. Thay `<V_cfg>` và `<V_wm>` bằng số đã ghi ở R0.

```sql
INSERT INTO lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
SELECT * FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config VERSION AS OF <V_cfg>
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND src_schema = 'lh_vv_silver.dbo' AND (
  (trg_tbl = 'slv_pn_poi' AND src_tbl IN ('slv_pn_business_services', 'slv_pn_business_service_i18ns'))
  OR (trg_tbl = 'gld_enr_poi_coordinate' AND src_tbl IN ('slv_3p_poi', 'slv_3p_poi_address', 'slv_pn_poi'))
  OR (trg_tbl = 'gld_enr_poi_info' AND src_tbl IN ('slv_3p_poi', 'slv_3p_poi_address', 'slv_3p_poi_contact')));
```

```sql
INSERT INTO lh_vv_ctrl.dbo.ctrl_mng_watermark
SELECT * FROM lh_vv_ctrl.dbo.ctrl_mng_watermark VERSION AS OF <V_wm>
WHERE watermark_id IN (
  'wm_e__gld_enr_poi_coordinate__slv_3p_poi',
  'wm_e__gld_enr_poi_coordinate__slv_3p_poi_address',
  'wm_e__gld_enr_poi_coordinate__slv_pn_poi',
  'wm_e__slv_pn_poi__slv_pn_business_service_i18ns',
  'wm_e__slv_pn_poi__slv_pn_business_services');
```

Để `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H` đã xóa. Không tạo lại, vì không có pipeline dùng nó. Sau khi khôi phục, chạy NB_00 với `p_mode` = `PLAN`, rồi bật schedule.

## Kết quả người dùng ghi nhận

- R0 registry n: 0
- R0 V_cfg: 17
- R0 V_wm: 140
- R0 count coordinate: 94
- R0 count slv_pn_poi: 30
- R1 lock_exec_id: null
- R2 hai notebook đã mất: có
- R3 output: đã xoá cạnh=8 watermark=6; watermark giữ lại=17
- R4 output: đã xoá cạnh=0 watermark=0; watermark giữ lại=17
- R5 DAG và entity_edges_ok: amenity phụ thuộc entity; info phụ thuộc amenity và entity; entity_edges_ok=6
- R6 backup counts và tableExists: backup 94 và 30. coordinate False, `slv_pn_poi` False, info True, review True.
- R7 exec_id và thứ tự entity, amenity: `5edc3634-ad7a-4545-8465-d0c7830dc543`. Entity kết thúc `03:18:02Z`, amenity bắt đầu `03:18:16Z`.
- R8 ctrl_log_run và INV-1, INV-3: INV-1 = 16, INV-3 = 17. Có một dòng chạy tay `5edc3634-ad7a-4545-8465-d0c7830dd555`, SUCCESS, `03:19:44Z`–`03:23:23Z`, `run_id = exec_id`. Dòng schedule chưa có. Người dùng chấp nhận rủi ro này (D-16).
