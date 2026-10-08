# Hướng dẫn kiểm chứng runtime

Trạng thái: `CHỜ CHẠY`

Audit này không đổi notebook, pipeline hay bảng. Các bước dưới đây chỉ đọc Fabric DEV để giải các mục `NOT_VERIFIABLE`. Không chạy cho tới khi người dùng thực hiện.

## Phạm vi và môi trường

- Workspace Fabric DEV.
- Lakehouse `lh_vv_bronze`, schema `ctrl`.
- Không lấy mẫu dòng nghiệp vụ. Chỉ schema và số đếm.

## Điều kiện tiên quyết

- Quyền đọc SQL analytics endpoint của `lh_vv_bronze`.
- Không chạy `NB_CREATE_DDL` và không `ALTER` bảng.

## Baseline trước khi chạy

- Ghi nhận task `20261008-context-implementation-consistency-review`.
- Không có baseline dòng dữ liệu vì probe không đọc dữ liệu nghiệp vụ.

## Các bước thực hiện

1. Probe `ctrl-column-presence`. Chạy trong Fabric DEV:

```sql
SELECT column_name
FROM lh_vv_bronze.information_schema.columns
WHERE table_schema = 'ctrl'
  AND table_name IN ('ctrl_log_run', 'ctrl_log_table_run')
  AND column_name IN (
    'output_versions_json', 'src_versions_json', 'trg_version',
    'deactivated_rows', 'qg_json'
  )
ORDER BY table_name, column_name;
```

Nếu endpoint không có `information_schema`, dùng `DESCRIBE TABLE lh_vv_bronze.ctrl.ctrl_log_run` và `DESCRIBE TABLE lh_vv_bronze.ctrl.ctrl_log_table_run`, rồi chỉ ghi tên cột.

2. Probe `fl00-active-sources`:

```sql
SELECT src_tbl, COUNT(*) AS active_rows
FROM lh_vv_bronze.ctrl.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00'
  AND is_active = 1
GROUP BY src_tbl
ORDER BY src_tbl;
```

3. Probe `fl00-schedule-overlap`: mở lịch hoặc trigger của pipeline `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` và ghi khoảng lặp lại. Không cần mở notebook.

## Kiểm tra kết quả

- Đủ 5 cột gold-log: ghi `PRESENT`. Thiếu cột nào: ghi đúng tên cột `ABSENT`.
- `active_rows` theo `src_tbl`. Nếu có `poi_raw_event`, finding F-P1-02 áp vào DEV, không chỉ vào seed trong repo.
- Nếu lịch cho phép lần chạy mới trước khi activity 12 giờ kết thúc, giả thuyết hai writer của F-P1-01 được củng cố. Nếu lịch dài hơn 12 giờ và cấm chạy chồng, ghi `NO_OVERLAP`.

## Chạy lại để kiểm tra idempotency

Không áp dụng. Probe chỉ đọc. Chạy lại phải ra cùng schema và cùng số đếm nếu không có người khác sửa config.

## Kiểm tra log và watermark

Không cập nhật watermark. Không ghi `ctrl_log_run`.

## Rollback và forward recovery

Không có thay đổi để rollback. Nếu lỡ chạy nhầm notebook ghi, dừng ngay và không dùng audit này làm runbook phục hồi.

## Kết quả người dùng ghi nhận

- Chưa chạy.
- Khi có kết quả, đặt file tại `evidence/results/` và không dán dữ liệu cá nhân.
