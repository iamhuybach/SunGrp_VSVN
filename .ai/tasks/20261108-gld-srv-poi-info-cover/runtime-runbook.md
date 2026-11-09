# Hướng dẫn kiểm chứng runtime

Trạng thái: `PASS`.

## Phạm vi và môi trường

Fabric DEV, workspace dùng `lh_vv_silver`, `lh_vv_gold`, `lh_vv_ctrl`. Một lần `NB_00_ORCHES_SLV_TO_GLD` với `p_mode=RUN` trên `PL_VV_TRANS_SLV_TO_GLD_30M`. Lần này MERGE `gld_srv_poi_info` và tiến watermark. Sau khi gold đạt, chạy `ALTER` trên PostgreSQL đã có `apps.srv_poi_info`, rồi deploy `data-serving-service`.

## Điều kiện tiên quyết

- Cell `srvcoverpy` đã chạy trên DEV: `gld_srv_poi_info +['cover_id', 'cover_blob_url']; cạnh ['slv_poi_media_info']`.
- `NB_GLD_SRV_POI_INFO` trên Fabric DEV là bản đã publish, cell `srvinfobuild` có `_cover` và input `media`.
- Không chạy tay `NB_GLD_SRV_POI_INFO` trong lúc orches đang `RUN`. Cả hai cùng lấy khoá `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`.
- Nếu lịch 30M sắp chạy, tạm dừng trigger đến khi lần tay này xong.

## Baseline trước khi chạy

Ghi hai số, không lấy mẫu dòng:

```sql
SELECT count(*) AS live_rows, count(DISTINCT poi_id) AS distinct_poi
FROM lh_vv_gold.dbo.gld_srv_poi_info
WHERE deleted_at IS NULL
```

`DRY_RUN` trước đó không MERGE: `exec_id` `390dc54c-7b54-4938-b319-2ec970a13db0`, `trg_version` null, update 238 trên 292 dòng nguồn.

## Các bước thực hiện

1. Mở `NB_00_ORCHES_SLV_TO_GLD` trên Fabric DEV. Cell tham số:

```text
p_pl_name = PL_VV_TRANS_SLV_TO_GLD_30M
p_run_id =
p_mode = RUN
p_max_parallel = 3
p_node_timeout_min = 20
p_dag_timeout_min = 45
p_lock_timeout_min = 90
p_force_nodes =
p_history_limit = 1000
p_non_data_ops =
```

2. Chạy toàn bộ cell một lần. `p_mode=RUN` là lần ghi. Orches gọi `NB_GLD_SRV_POI_INFO` khi cạnh `slv_poi_media_info` còn bẩn. Lần đầu sau rollout có thể cập nhật mọi dòng đổi `row_hash`, kể cả dòng cover null.
3. Nếu log báo luồng đang giữ khoá, đợi rồi chạy lại đúng tham số trên. Không đổi `p_pl_name` sang `PL_VV_TRANSFORM_SLV_TO_GLD_1H`.
4. Khi gold đạt ba câu kiểm tra bên dưới, trên PostgreSQL đã có `apps.srv_poi_info` chạy:

```sql
ALTER TABLE apps.srv_poi_info
    ADD COLUMN cover_id text,
    ADD COLUMN cover_blob_url text;
```

5. Deploy `data-serving-service` sau bước 4. Cột PostgreSQL vẫn null cho đến khi loader gold sang `apps.srv_poi_info` map theo tên cột.

## Kiểm tra kết quả

Pass khi cả ba câu sau đúng. Chạy trên Fabric DEV, SQL analytics endpoint của gold và ctrl.

```sql
SELECT count(*) AS live_rows, count(DISTINCT poi_id) AS distinct_poi
FROM lh_vv_gold.dbo.gld_srv_poi_info
WHERE deleted_at IS NULL
```

`live_rows` bằng `distinct_poi`, và bằng baseline.

```sql
SELECT count(*) AS cover_mismatch
FROM lh_vv_gold.dbo.gld_srv_poi_info i
LEFT JOIN lh_vv_gold.dbo.gld_srv_poi_media_gallery g
  ON g.poi_id = i.poi_id AND g.is_cover AND g.deleted_at IS NULL
WHERE i.deleted_at IS NULL
  AND NOT (i.cover_id <=> g.media_id AND i.cover_blob_url <=> g.blob_url)
```

`cover_mismatch` bằng 0.

`cover_matched` trong `ctrl_log_table_run` của node `gld_srv_poi_info` bằng số dòng `cover_id` không null:

```sql
SELECT count(*) AS cover_id_not_null
FROM lh_vv_gold.dbo.gld_srv_poi_info
WHERE deleted_at IS NULL AND cover_id IS NOT NULL
```

Fail khi `live_rows` khác `distinct_poi`, `cover_mismatch` lớn hơn 0, node không `SUCCESS`, hoặc notebook raise.

## Chạy lại để kiểm tra idempotency

Chạy lại `NB_00_ORCHES_SLV_TO_GLD` với cùng tham số, `p_force_nodes` vẫn trống. Node `gld_srv_poi_info` phải `NO_DATA` khi không có cạnh mới bẩn. Không có thêm một đợt update hàng loạt. Nếu lần đầu trả `NO_DATA` trước khi ba câu kiểm tra đạt, chạy lại một lần với `p_force_nodes = gld_srv_poi_info`, rồi trả `p_force_nodes` về trống cho lần idempotency.

## Kiểm tra log và watermark

Trong `RUN_SUMMARY` và `ctrl_log_table_run` của lần chạy: node `lh_vv_gold.dbo.gld_srv_poi_info` có `status` `SUCCESS` hoặc `NO_DATA` ở lần idempotency. Metric `cover_matched` có mặt trên lần `SUCCESS`. Khoá `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` được nhả sau khi notebook kết thúc. Watermark cạnh `slv_poi_media_info` sang `gld_srv_poi_info` tiến trên lần `SUCCESS`, không tiến trên `NO_DATA`.

## Rollback và forward recovery

- Service: deploy lại bản trước. Bản đó chạy được khi PostgreSQL đã có hai cột.
- PostgreSQL: hai cột nullable, có thể để nguyên. Gỡ sau khi đã rollback service: `ALTER TABLE apps.srv_poi_info DROP COLUMN cover_blob_url, DROP COLUMN cover_id;`
- Gold: publish lại `NB_GLD_SRV_POI_INFO` bản trước. Giữ khoá luồng, đặt cạnh `slv_poi_media_info` sang `gld_srv_poi_info` thành `is_active = 0`, giữ dòng. Không `DROP` cột Delta. Nếu cover cũ không được phép nằm lại: `UPDATE lh_vv_gold.dbo.gld_srv_poi_info SET cover_id = NULL, cover_blob_url = NULL` một lần, trong lúc giữ khoá.
- Forward recovery: sửa build rồi chạy lại orches. Cạnh và cột được giữ.

## Kết quả người dùng ghi nhận

Lần MERGE, Fabric DEV, 2026-11-09:

- `exec_id` `d733ea4a-95c7-49f7-bce8-df4911adf3ce`, `pl_name` `PL_VV_TRANS_SLV_TO_GLD_30M`, `mode` `RUN`, `status` `SUCCESS`, 206s.
- Kế hoạch: 5 node, 15 cạnh, 1 Dirty Edge, 1 node ứng viên. Dirty Edge: `gld_srv_poi_info` ← `lh_vv_silver.dbo.slv_poi_media_info` `NEW_EDGE` (đã đọc None, đọc 2).
- Node `gld_srv_poi_info`: `SUCCESS`, `inserted` 0, `updated` 238, `deactivated` 0, `trg_version` 9. `cover_matched` không có trong exit value.
- Log: tiến 6 cạnh. `tbl_success_count` 1, `tbl_failed_count` 0, `tbl_no_data_count` 0.

Kiểm tra sau MERGE:

- `live_rows` 292, `distinct_poi` 292.
- `cover_mismatch` 0.
- `cover_id_not_null` 238. Bằng số `updated` của lần MERGE. `cover_matched` không có trong exit value của orches.
- Lần chạy lại `exec_id` `350daf3b-87cc-4196-9bb0-480754ebe505`: 0 Dirty Edge, 0 node ứng viên, `status` `NO_DATA`, 34s. `tbl_total_count` 0.
- Người dùng đã chạy `ALTER` thêm `cover_id` và `cover_blob_url` trên `apps.srv_poi_info`.

Deploy `data-serving-service` chưa có trong kết quả này.
