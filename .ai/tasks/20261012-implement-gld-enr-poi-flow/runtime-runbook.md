# Hướng dẫn kiểm chứng runtime

Trạng thái: `PASS`

Chưa chạy lần đầu. `gld_enr_poi_info` chỉ có nguồn 3rd-party. `destination_context` ghép câu và đổi chỗ NULL thành chuỗi rỗng.

## Phạm vi và môi trường

- Fabric DEV, workspace đang dùng cho lakehouse `lh_vv_bronze`, `lh_vv_silver`, `lh_vv_gold`, `lh_vv_ctrl`.
- Notebook: `NB_LIB_TRANSFORM_SLV_GLD`, `NB_CREATE_DDL`, `NB_00_ORCHES_SLV_TO_ENR_15P`, `NB_SLV_PN_POI`, `NB_ENR_POI_INFO`, `NB_ENR_POI_COORDINATE`, `NB_ENR_POI_REVIEW`.
- Pipeline: `PL_VV_TRANS_SLV_TO_ENR_15P`. Tham số pipeline `nb_orches_id` là id notebook `NB_00_ORCHES_SLV_TO_ENR_15P` trên Fabric. `workspace_id` là id workspace DEV. Không truyền chuỗi `PENDING`.
- Không in review text, địa chỉ, tên. Chỉ số đếm, id, version, timestamp. Tối đa 50 dòng.

## Điều kiện tiên quyết

1. Deploy `NB_LIB_TRANSFORM_SLV_GLD` trước mọi notebook gọi nó. Notebook gọi lib phải có default lakehouse `lh_vv_bronze`. Thiếu lakehouse thì Spark báo `No default context found`. `runMultiple` truyền `useRootDefaultLakehouse` để notebook node dùng lakehouse của `NB_00`.
2. Bảng silver nguồn đã có dữ liệu. Không sửa tay bảng do notebook extract sở hữu.

## Baseline trước khi chạy

1. Chạy `NB_00_ORCHES_SLV_TO_GLD` với `p_mode = PLAN`. Đạt khi vẫn `ConfigError` vì pl cũ chưa có cạnh `RECOMPUTE`, và lỗi xảy ra trước khi tạo khóa.
2. Ghi số dòng hiện tại của ba bảng `gld_enr_*` nếu đã có. Lần đầu sau DDL thì bảng vừa tạo, số dòng là 0.

## Các bước thực hiện

1. Chạy cell mới cuối `NB_CREATE_DDL`. Đạt khi không raise. Ba bảng tồn tại. `ctrl_mng_pipeline_config` có 13 dòng `pl_name = PL_VV_TRANS_SLV_TO_ENR_15P`.
2. Chạy `NB_00_ORCHES_SLV_TO_ENR_15P` với `p_mode = PLAN`, `p_pl_name = PL_VV_TRANS_SLV_TO_ENR_15P`. Đạt khi kế hoạch có 4 node, 13 cạnh, cạnh mới là `NEW_EDGE`. `gld_enr_poi_info` không phụ thuộc `slv_pn_poi`.
3. Chạy cùng notebook với `p_mode = RUN` và các mặc định: `p_max_parallel = 2`, `p_node_timeout_min = 15`, `p_dag_timeout_min = 25`, `p_lock_timeout_min = 35`, `p_history_limit = 1000`, `p_force_nodes` trống.
4. Chạy lại `p_mode = RUN` ngay, không có commit silver mới.
5. Chạy `p_mode = RUN` với `p_force_nodes = gld_enr_poi_review`. Lặp cho `gld_enr_poi_info` và `gld_enr_poi_coordinate` nếu cần kiểm từng bảng.
6. Khi silver có commit mới tự nhiên, chạy `p_mode = RUN` một lần nữa.
7. Tạo pipeline trên Fabric. Truyền `nb_orches_id` là id notebook `NB_00_ORCHES_SLV_TO_ENR_15P` và `workspace_id` là id workspace DEV. Không dùng chuỗi `PENDING`. Trigger một lần. Lịch 15 phút chỉ bật sau khi các bước trên đạt.

## Kiểm tra kết quả

- Lần `RUN` đầu: `ctrl_log_run.status` là `SUCCESS`. Mỗi bảng gold có đúng một `updated_at` cho batch đó. `created_at = updated_at`.
- `GROUP BY poi_id, updated_at` trên info và coordinate, và `GROUP BY review_id, updated_at` trên review, không có nhóm `count(*) > 1`.
- Số dòng info bằng số `poi_id` của `slv_3p_poi`. Số dòng coordinate bằng số đó cộng số dòng live `slv_pn_poi`. Số dòng review bằng số `review_id` của `slv_3p_poi_review`.
- `DESCRIBE HISTORY` của bảng gold chỉ có `WRITE` Append với `userMetadata` chứa `vv_append`. Không có `MERGE`, `UPDATE`, `DELETE`.
- Nếu `userMetadata` không hiện trên history: dừng, phân loại `architecture`.
- `review_poi_not_in_slv_3p_poi` và `review_date_ne_published_at` trong `qg_json` bằng 0, hoặc ghi lý do.

## Chạy lại để kiểm tra idempotency

- `RUN` lần hai khi silver không có commit mới: status `NO_DATA`, không có commit gold mới, dòng cũ giữ nguyên `created_at` và `updated_at`.
- `p_force_nodes` một bảng: số dòng bảng đó tăng thêm một batch. Dòng cũ không đổi timestamp. Bảng không ép thì không tăng.

## Kiểm tra log và watermark

- `ctrl_log_run`: một dòng cho mỗi `exec_id`. `read_mode = VERSION_INBOX`.
- `ctrl_log_table_run`: một dòng cho mỗi node. `inserted_rows` bằng số dòng append. `updated_rows = 0`. `deactivated_rows = 0`.
- `ctrl_mng_watermark`: khóa `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` không còn `lock_exec_id` sau khi chạy xong. Cạnh `wm_e__<trg_tbl>__<src_tbl>` có `last_src_version` bằng version đã đọc trong `src_versions_json`.

## Rollback và forward recovery

Dừng lịch pipeline, rồi:

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
SET is_active = 0
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'
```

Batch sai, chỉ sau khi người dùng chấp nhận một trong hai lệnh:

1. `DESCRIBE HISTORY <bảng>` lấy version của commit có `exec_id` cần bỏ.
2. `RESTORE TABLE <bảng> TO VERSION AS OF <version - 1>` nếu đó là commit mới nhất, hoặc `DELETE FROM <bảng> WHERE updated_at = <batch_ts>`.
3. Marker cũ hết hiệu lực. Chạy `NB_00` với `p_force_nodes = <trg_tbl>` để append lại toàn bộ snapshot đúng.

Gỡ hẳn luồng:

1. Tắt lịch và `is_active = 0`.
2. Xóa dòng config `pl_name = PL_VV_TRANS_SLV_TO_ENR_15P`.
3. Xóa watermark `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`, `wm_e__gld_enr_poi_%`, `wm_e__slv_pn_poi__%`.
4. `DROP TABLE` ba bảng gold và `slv_pn_poi`.
5. Giữ cột `nb_name`. Không drop cột Delta khi chưa bật column mapping.

Phục hồi phía trước: deploy notebook đã sửa, rồi `p_force_nodes` đúng bảng cần tính lại. Bảng gold bị tạo lại thì chạy cell DDL rồi force node đó.

## Kết quả người dùng ghi nhận

Lần `RUN` đầu, 2026-10-13, `exec_id` `bfa377b3-6294-483c-ac0d-9c267ff4e344`. `status` `SUCCESS`. `tbl_success_count` 4. `Tiến 13 cạnh`.

| Node | status | inserted | updated | deactivated | trg_version |
|---|---|---|---|---|---|
| `gld_enr_poi_info` | `SUCCESS` | 17 | 0 | 0 | 1 |
| `gld_enr_poi_review` | `SUCCESS` | 85 | 0 | 0 | 1 |
| `slv_pn_poi` | `SUCCESS` | 30 | 0 | 0 | 1 |
| `gld_enr_poi_coordinate` | `SUCCESS` | 47 | 0 | 0 | 1 |

Coordinate 47 = info 17 + `slv_pn_poi` 30.

Lần `RUN` thứ hai, 2026-10-13, `exec_id` `b98cfec5-48a5-491a-8f16-84d27979b945`. `status` `NO_DATA`. 13 cạnh, 0 Dirty Edge, 0 node ứng viên. Không ghi thêm.

Ba lần force, 2026-10-13. Mỗi lần 0 Dirty Edge, chỉ node được ép chạy, `updated` 0, `deactivated` 0.

| `p_force_nodes` | `exec_id` | inserted lần này | `trg_version` | cạnh tiến | Số dòng suy ra |
|---|---|---|---|---|---|
| `gld_enr_poi_review` | `85e5431c-c336-4fcf-8343-4d7079aaebdc` | 85 | 2 | 1 | 170 |
| `gld_enr_poi_info` | `b003ae85-8c7f-4ea0-861a-7bfe8d7295da` | 17 | 2 | 7 | 34 |
| `gld_enr_poi_coordinate` | `e98b1132-1209-4398-8ed6-a9f801ca957b` | 47 | 2 | 3 | 94 |

`DESCRIBE HISTORY` ngày 2026-10-13. Mỗi bảng có version 0 `CREATE TABLE`, version 1 `WRITE` Append (`force` false, `exec_id` `bfa377b3-6294-483c-ac0d-9c267ff4e344`), version 2 `WRITE` Append (`force` true). `isBlindAppend` = 1. `userMetadata` có `vv_append` = 1. Không có `MERGE`, `UPDATE`, `DELETE`.

| Bảng | version 1 rows | version 2 rows | `exec_id` version 2 |
|---|---|---|---|
| `gld_enr_poi_info` | 17 | 17 | `b003ae85-8c7f-4ea0-861a-7bfe8d7295da` |
| `gld_enr_poi_coordinate` | 47 | 47 | `e98b1132-1209-4398-8ed6-a9f801ca957b` |
| `gld_enr_poi_review` | 85 | 85 | `85e5431c-c336-4fcf-8343-4d7079aaebdc` |

Chưa trigger pipeline. Chưa có commit silver mới để kiểm tra append chỉ các khóa đổi.
