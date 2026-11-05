# Hướng dẫn kiểm chứng runtime

Trạng thái: `PASS`.

## Phạm vi và môi trường

Fabric DEV. Notebook `NB_00_ORCHES_SLV_TO_GLD`. Pipeline `PL_VV_TRANS_SLV_TO_GLD_30M`, cùng pipeline của exec `c2a9f0ef-6d48-4241-b1fb-c9e25eddd4fe`.

## Điều kiện tiên quyết

Workspace đang mở ba notebook đã sửa: `NB_GLD_SRV_POI_INFO` có `len(hours) > 2`; `NB_SLV_POI_MEDIA_INFO` có `def collapse`; `NB_GLD_SRV_POI_MEDIA_GALLERY` có `pk=("media_id", "poi_id")`. Không thấy các dấu này thì đồng bộ git của workspace trước khi bấm Run.

## Baseline trước khi chạy

Exec `c2a9f0ef` là `PARTIAL_FAILED`. `gld_srv_poi_review` và `gld_srv_poi_multi_lang` đã SUCCESS và năm cạnh của chúng đã advance. `gld_srv_poi_info` và `slv_poi_media_info` FAILED nên cạnh của chúng không advance. `gld_srv_poi_media_gallery` là `NOT_RUN`.

## Các bước thực hiện

1. Mở `NB_00_ORCHES_SLV_TO_GLD` trên Fabric DEV.
2. Sửa cell 1 thành đúng các dòng sau, rồi Run all.

```python
p_pl_name = "PL_VV_TRANS_SLV_TO_GLD_30M"
p_run_id = ""
p_mode = "RUN"
p_max_parallel = "3"
p_node_timeout_min = "20"
p_dag_timeout_min = "45"
p_lock_timeout_min = "90"
p_force_nodes = ""
p_history_limit = "1000"
p_non_data_ops = ""
```

`p_force_nodes` để trống. Điền `gld_srv_poi_review` hoặc `gld_srv_poi_multi_lang` sẽ ép hai node đã thành công chạy lại.

## Kiểm tra kết quả

Đạt khi status là `SUCCESS`. `gld_srv_poi_info` không còn `PARTNER_MULTI_HOURS`. `slv_poi_media_info` không còn `pk_duplicate`. `gld_srv_poi_media_gallery` có dòng log, không còn `NOT_RUN`. Log có dòng `Tiến N cạnh` với N bằng số cạnh của các node `SUCCESS` trong lần này.

## Chạy lại để kiểm tra idempotency

Không chạy thêm trong lượt này.

## Kiểm tra log và watermark

Dán `exec_id`, status, dòng từng node (`status`, `inserted`, `updated`, `deactivated`, `trg_version`) và dòng `Tiến N cạnh`.

## Rollback và forward recovery

Không có bước xóa bảng. Nếu lần chạy `PARTIAL_FAILED`, lần sau với cùng `p_force_nodes` trống chỉ chọn node còn bẩn.

## Kết quả người dùng ghi nhận

Exec `34516f98-b674-474a-9a66-a7e328431bea`, 2026-11-05, Fabric DEV. Status `SUCCESS`, 237s. Bốn node ứng viên đều `SUCCESS`. `Tiến 12 cạnh`. `gld_srv_poi_info` inserted 268, updated 23, deactivated 0, trg_version 6. `gld_srv_poi_multi_lang` inserted 0, updated 0, deactivated 0, trg_version 3. `slv_poi_media_info` inserted 241303, updated 17, deactivated 0, trg_version 2. `gld_srv_poi_media_gallery` inserted 241303, updated 17, deactivated 0, trg_version 2. Không có `PARTNER_MULTI_HOURS`, `pk_duplicate`, hay `NOT_RUN`.
