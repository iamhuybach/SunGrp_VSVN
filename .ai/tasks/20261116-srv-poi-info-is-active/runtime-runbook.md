# Runbook: thêm `gld_srv_poi_info.is_active` trên Fabric DEV

Agent không chạy notebook, pipeline, Copy Job, hay `ALTER`. Mọi bước Fabric dưới đây do người dùng chạy. Ghi kết quả vào mục cuối. Không chép host, credential, hay dữ liệu cá nhân. Mẫu tối đa 50 dòng.

## Phạm vi và môi trường

- Môi trường: Fabric DEV, workspace đang dùng cho `lh_vv_gold`.
- Notebook: `NB_CREATE_DDL`, chỉ cell `srvactivepy`.
- Bảng: `lh_vv_gold.dbo.gld_srv_poi_info`.
- Cột thêm: `is_active` BOOLEAN, cho phép NULL, ngay sau `is_bookable`.
- Khoá giữ suốt cell: `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` trên `lh_vv_ctrl.dbo.ctrl_mng_watermark`.
- `LEASE_MINUTES = 90`. Pipeline: `PL_VV_TRANS_SLV_TO_GLD_30M`.
- PostgreSQL: cột `apps.srv_poi_info.is_active` và `ingestion_ts` đã có. File DDL trong repo chỉ để cài mới. Không chạy `ALTER`.

## Điều kiện tiên quyết

- Nhánh chứa cell `srvactivepy` đã được merge và sync vào workspace.
- PostgreSQL DEV đã có cột mới. Kiểm tra đọc:

```sql
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'apps'
  AND column_name IN ('is_active', 'ingestion_ts')
ORDER BY table_name, column_name;
```

Kỳ vọng 6 dòng: `srv_poi_media_gallery.is_active` đã có từ trước, thêm `srv_poi_info.is_active`, và `ingestion_ts` trên cả 5 bảng `apps`.

## Baseline trước khi chạy

- Tắt trigger `PL_VV_TRANS_SLV_TO_GLD_30M`.
- `lock_exec_id` của `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` là NULL.
- Ghi số dòng sống của `gld_srv_poi_info` (`deleted_at IS NULL`) trước khi chạy, để đối chiếu `updated` sau pipeline.

## Các bước thực hiện

1. Tắt trigger `PL_VV_TRANS_SLV_TO_GLD_30M`. Đợi `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` có `lock_exec_id` NULL.
2. Sync notebook `NB_CREATE_DDL` bản có cell `srvactivepy` vào workspace.
3. Chạy riêng cell `srvactivepy`. Không chạy `poidestpy`. Không chạy `NB_GLD_SRV_POI_INFO` trước cell này.
4. Bật lại trigger sau khi backfill xong. Một lần `RUN` với `p_force_nodes` trống không ghi `is_active`: orchestrator chỉ chạy node có cạnh bẩn. Backfill: chạy `NB_00_ORCHES_SLV_TO_GLD` với cùng tham số, riêng `p_force_nodes = "gld_srv_poi_info"` (`trg_tbl`, `split_csv`). Node con của bảng này trong cùng pipeline cũng chạy.
5. Smoke service theo `services/data-serving-service/AGENTS.md`: `docker compose` rồi `GET /api/v1/pois` với bearer token. JSON không có `is_active` hay `ingestion_ts`.

## Kiểm tra kết quả

- Cell in `srvactive: +lh_vv_gold.dbo.gld_srv_poi_info.is_active` ở lần đầu. Lần đã có cột đúng chỗ in `srvactive: =...`.
- `DESCRIBE lh_vv_gold.dbo.gld_srv_poi_info`: `is_active` kiểu boolean, ngay sau `is_bookable`.
- Sau pipeline: `SELECT count_if(deleted_at IS NULL AND is_active IS NOT TRUE) FROM lh_vv_gold.dbo.gld_srv_poi_info` trả 0. Dòng có `deleted_at` có thể còn NULL.
- `GET /api/v1/pois` trả 200 và JSON không có `is_active` hay `ingestion_ts`.
- Việc nạp gold sang PostgreSQL có mang `is_active` theo tên cột hay không nằm ngoài task này. Thứ tự cột `apps` trên DB đã `ALTER` tay khác `CREATE TABLE`.

## Chạy lại để kiểm tra idempotency

Chạy lại đúng cell `srvactivepy` khi khoá đang tự do. Kỳ vọng in `srvactive: =lh_vv_gold.dbo.gld_srv_poi_info.is_active` và schema không đổi.

## Kiểm tra log và watermark

- Sau pipeline, `ctrl_log_table_run` của `gld_srv_poi_info` có `updated` xấp xỉ số dòng sống. Đó là lần cập nhật `row_hash` một lần vì `is_active` nằm trong hash.
- Sau cell, dòng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` có `lock_exec_id` NULL. Thành công thì `status = SUCCESS`. Thất bại thì `status = FAILED` và `error_message` có lý do.

Cell dừng trước khi ghi khi: khoá đang bị giữ, bảng chưa có, hoặc schema khác hợp đồng. `is_active` có nhưng sai chỗ: dừng, kèm gợi ý `ALTER COLUMN is_active AFTER is_bookable`, rồi chạy lại cell. Không tự sửa schema lệch kiểu khác.

## Rollback và forward recovery

- Gold không `DROP` cột và không bật column mapping. Gỡ `is_active` khỏi `OUT_COLS` rồi chạy notebook làm `ensure_target` cảnh báo cột thừa, cột giữ giá trị cũ, dòng insert mới để NULL, và `row_hash` đổi thêm một lần. Hướng xử lý là đi tiếp, không rollback cột.
- PostgreSQL thuộc người dùng. DDL trong repo chỉ ghi nhận cài mới.
- Image service cũ vẫn chạy trên DB đã thêm cột. Image mới cần các cột đó. Nếu service mới gặp DB chưa có cột: rollback image, hoặc người dùng thêm cột. Không mất dữ liệu.
- `NB_GLD_SRV_POI_INFO` lỗi sau khi cột đã thêm: cột tồn tại, giá trị còn NULL; sửa notebook rồi chạy lại. `MERGE` lặp lại được.

## Kết quả người dùng ghi nhận

- Ngày chạy: 2026-11-16, Fabric DEV.
- PostgreSQL `information_schema`: người dùng xác nhận đúng kỳ vọng (6 dòng).
- Trigger `PL_VV_TRANS_SLV_TO_GLD_30M`: đã tắt trước cell.
- `srvactivepy` in: `srvactive: +lh_vv_gold.dbo.gld_srv_poi_info.is_active`
- Vị trí `is_active` sau `DESCRIBE`: `boolean`, ngay sau `is_bookable`, trước `operating_hours`.
- `count_if` dòng sống `is_active` không phải true: 292 sau lần `RUN` không ép node; 0 sau lần ép node.
- `ctrl_log_table_run.updated`: exit node `gld_srv_poi_info` là `updated` 292, `inserted` 0, `deactivated` 0, `trg_version` 12, `status` `SUCCESS`. Exec ép node `de0decbc-28a2-436e-8572-9d1d73191da6`. Plan: 0 Dirty Edge, 1 node ứng viên `L1 gld_srv_poi_info (NB_GLD_SRV_POI_INFO)`, ép `['gld_srv_poi_info']`, tiến 6 cạnh. `NB_00` `SUCCESS`, `tbl_success_count` 1. Lần trước, exec `679e2273-b5f2-4591-8bbf-7450362e832f`, `NO_DATA`.
- `lock_exec_id` sau cell: null. `lock_at` null, `status` `SUCCESS`, `error_message` trống, `updated_at` `2026-11-16T13:54:11Z`.
- `GET /api/v1/pois/features`: người dùng xác nhận đã pass. HTTP 200, JSON không có `is_active` hay `ingestion_ts`.
- Trigger sau backfill: chưa báo lại. Trước cell thì đang tắt.
- Lần chạy lại idempotent: `srvactive: =lh_vv_gold.dbo.gld_srv_poi_info.is_active`
