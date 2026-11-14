# Hướng dẫn kiểm chứng runtime

Trạng thái: `CHỜ CHẠY`. Task không chạy các bước Fabric này.

## Phạm vi và môi trường

Fabric DEV, lakehouse `lh_vv_gold`, schema `enr`. Hai bảng: `gld_enr_poi_info` (khoá `poi_id`) và `gld_enr_poi_review` (khoá `review_id`). Pipeline `PL_VV_TRANS_SLV_TO_ENR_15M`, notebook `NB_00_ORCHES_SLV_TO_ENR`. Tham số node: `p_mode` mặc định `RUN`, `p_force` mặc định `false`. Init: `p_apply` mặc định `false`.

MERGE review không có bằng chứng runtime khi mọi cạnh review còn `is_active = 0`. Không bật cạnh. Không chạy `NB_ENR_POI_REVIEW` trên bảng đang trùng khoá.

## Điều kiện tiên quyết

Lịch pipeline đang tắt và khoá `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M` trống. Notebook trên workspace là bản của nhánh này, gồm ô `enrmergepy`. Không xoá `gld_enr_poi_info`.

`source-uniqueness.sql` đã chạy ngày 2026-11-14 và đạt. SQL-001 và SQL-002 đã đóng.

## Baseline trước khi chạy

Ghi `version` của `DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_info LIMIT 1`. Đó là mốc rollback. Chạy `evidence/probes/key-uniqueness.sql` và giữ hai dòng tổng hợp.

## Các bước thực hiện

1. Tạm dừng lịch `PL_VV_TRANS_SLV_TO_ENR_15M`. Xác nhận khoá luồng trống.
2. `DELETE FROM lh_vv_gold.enr.gld_enr_poi_review`. Không chạy câu này với `gld_enr_poi_info`.
3. Chạy ô `enrmergepy` của `NB_CREATE_DDL`. Kết quả in phải là `RECOMPUTE` cho cả hai bảng.
4. Chạy `NB_SETUP_INITIAL_DDL` với `p_apply = "false"`, rồi `p_apply = "true"`. Không có lệch schema. `to_insert = 0` cho `pipeline_config`.
5. Chạy `NB_ENR_POI_INFO` với `p_mode = DRY_RUN`, `p_force = true`, lịch pipeline đang tắt. QG phải qua. `inserted` bằng số khoá spine mới, `updated` xấp xỉ 20829, `deactivated` bằng số khoá info không còn trên spine. Ghi duration, số dòng, bytes, shuffle, spill, peak memory, và mức dùng capacity. Dừng nếu QG chặn, quá 15 phút, OOM, throttling, hoặc spill kéo dài. SPARK-002 cần bản ghi này trước khi review vòng 2.
6. Chạy `NB_ENR_POI_INFO` với `p_mode = RUN`, `p_force = true`.
7. Bật lại lịch. Một vòng `NB_00` phải `SUCCESS` hoặc `NO_DATA`, và cạnh phải tiến watermark.

## Kiểm tra kết quả

Sau bước 6, chạy lại `evidence/probes/key-uniqueness.sql`. Info: `row_count = distinct_key_count` và `null_key_count = 0`. Review: 0 dòng. Người đọc hai bảng lọc `deleted_at IS NULL`.

## Chạy lại để kiểm tra idempotency

Chạy lại bước 6. `inserted_rows`, `updated_rows`, `deactivated_rows` phải là 0/0/0 và `trg_version` không đổi.

## Kiểm tra log và watermark

`ctrl_log_table_run` của node info có `inserted_rows`, `updated_rows`, `deactivated_rows`, `trg_version`, `qg_json`. `qg_json` không còn `basis`. Ô `enrmergepy` in map `load_mode` và dòng khoá ghi `SUCCESS` hoặc `FAILED` kèm lỗi. Sau vòng `NB_00`, watermark cạnh info tiến.

## Rollback và forward recovery

Trước bước 6 (`RUN`): hoàn code, `UPDATE` `load_mode` về `APPEND` cho hai bảng đích, rồi `RESTORE TABLE lh_vv_gold.enr.gld_enr_poi_info TO VERSION AS OF` mốc baseline để bỏ hai cột mới. `RESTORE` info cần người dùng chấp nhận tại thời điểm đó.

Sau bước 6: chỉ đi tiếp. Sửa build hoặc nguồn rồi chạy lại. MERGE toàn bộ tự vá dòng lệch. Không `RESTORE` sau khi đã có commit MERGE.

## Kết quả người dùng ghi nhận

2026-11-14, người dùng đã chạy trên DEV:

- `enrmergepy` in `RECOMPUTE` cho 11 dòng: info active 8, info inactive 1, review inactive 2. `row_hash` string, `deleted_at` timestamp.
- `NB_ENR_POI_INFO` `p_mode = DRY_RUN`, `p_force = true`: SUCCESS 53s. Diff insert 0, update 20829, xoá mềm 0, nguồn 20829. QG chỉ cảnh báo. Không commit.

D-SPARK-2: người dùng cho qua spill và Capacity Metrics. Không ghi các số đó bằng 0.

`DESCRIBE HISTORY` trước khi ghi: version 2, 2026-11-14T03:09:56Z, `ADD COLUMNS` (`row_hash`, `deleted_at`).

`p_mode = RUN`, `p_force = true`, exec `2e0a8893-b62b-48d4-8bb7-c548d3b0bfef`: SUCCESS 53s. insert 0, update 20829, xoá mềm 0, `trg_version` 3. Đã commit.

Chạy lại, exec `aa283b4c-73a8-4a19-a628-8c6233100a99`: SUCCESS 41s. insert 0, update 0, xoá mềm 0. Log bỏ qua MERGE vì không có dòng đổi. `trg_version` vẫn 3.

`NB_00_ORCHES_SLV_TO_ENR`, exec `fec95fa4-bc99-4ff2-96c2-aa4b018f6a4e`: SUCCESS 276s. Hai node ứng viên đều SUCCESS. `gld_enr_poi_info` insert 0, update 0, xoá mềm 0, `trg_version` 3. `slv_poi_amenity` insert 0, update 0, xoá mềm 0, `trg_version` 4. Log tiến 11 cạnh. `gld_enr_poi_review` không nằm trong kế hoạch.

Chưa ghi nhận việc bật lại lịch `PL_VV_TRANS_SLV_TO_ENR_15M`. Không chạy `NB_ENR_POI_REVIEW`.
