# Hướng dẫn kiểm chứng runtime

Trạng thái: `PASS`

## Phạm vi và môi trường

Fabric DEV. Notebook `NB_GLD_SRV_PRODUCT_OFFER`. Cell `gldprdddlpy` trong `NB_CREATE_DDL`. Pipeline `PL_VV_TRANS_SLV_TO_GLD_30M`. Bảng đích `lh_vv_gold.dbo.gld_srv_product_offer`.

## Điều kiện tiên quyết

P-7 đã đạt. Notebook đã được publish lên workspace DEV trước khi chạy cell tạo cạnh. Session Spark đọc silver đặt `spark.sql.legacy.timeParserPolicy = LEGACY` nếu gặp lại chuỗi năm `58774`.

## Baseline trước khi chạy

Bảng `gld_srv_product_offer` chưa có, hoặc đã có đúng 31 cột của `gldprdddlpy`. Chưa có cạnh active tới bảng này.

## Các bước thực hiện

1. Publish `NB_GLD_SRV_PRODUCT_OFFER`.
2. Mở `NB_CREATE_DDL`, chạy cell `gldprdddlpy`. Cell không có tham số. Nó tạo bảng và 15 cạnh `RECOMPUTE`, rồi tự kiểm tra schema và số cạnh.
3. Chờ một vòng `PL_VV_TRANS_SLV_TO_GLD_30M`. Notebook nhận tham số từ pipeline. Ô tham số trong repo: `p_mode = RUN`, `p_force = false`, `p_history_limit = 1000`. `p_exec_id`, `p_run_id`, `p_pl_name`, `p_trg_fq`, `p_pinned_json` do pipeline điền.

## Kiểm tra kết quả

Sau vòng pipeline đầu, trên Fabric DEV:

1. V1: `ctrl_log_table_run` của `gld_srv_product_offer` là `SUCCESS` và có metric mục 12 của architecture.
2. V2: `count(*)` bằng `holiday_rows + hotel_rows`. `holiday_rows` bằng số dòng `slv_pn_product_sale` còn sống trừ `dropped_multi_bsid`. `hotel_rows` bằng số dòng `slv_pn_hotel_room_offer` còn sống.
3. V3: `count(DISTINCT product_id) = count(*)`.
4. V4: ba giá `EXCEPT` hai chiều với L2 còn sống theo `product_id` ra 0 dòng.
5. V5: `destination_id` `EXCEPT` hai chiều với `slv_enr_poi_destination` theo `poi_id` đã khớp ra 0 dòng.
6. V7: `from_json(variants_json, 'array<struct<variant_id:string>>')` khác NULL trên mọi dòng. `valid_from` của phần tử hotel khớp `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$` hoặc NULL.

Đạt khi cả sáu mục trên đúng. Dán aggregate vào mục cuối. Tối đa 50 dòng, không dữ liệu cá nhân, không secret.

## Chạy lại để kiểm tra idempotency

V6: chạy lại notebook với `p_force = true` và đúng `p_pinned_json` của lần SUCCESS đầu. Kết quả `updated = 0`, `inserted = 0`. Lấy pin từ log lần đầu, không điền tay.

## Kiểm tra log và watermark

Một dòng `ctrl_log_table_run` SUCCESS cho bảng này ở lần chạy đầu. Watermark cạnh do lib ghi. Không sửa watermark bằng tay.

## Rollback và forward recovery

Rollback: dưới lease của luồng, `UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 0 WHERE trg_schema = 'lh_vv_gold.dbo' AND trg_tbl = 'gld_srv_product_offer'`. Giữ bảng. Không DROP.

Forward recovery: sửa notebook rồi chạy lại với `p_force`. MERGE hội tụ. Đổi DDL sau này chỉ là cell patch thêm cột, không DROP.

## Kết quả người dùng ghi nhận

- 2026-11-28: Cell `gldprdddlpy` tạo `lh_vv_gold.dbo.gld_srv_product_offer` và 15 cạnh active. Cùng pipeline `PL_VV_TRANS_SLV_TO_GLD_30M`, mode `RECOMPUTE`, notebook `NB_GLD_SRV_PRODUCT_OFFER`.
- 2026-11-28: Chạy tay `exec f66250d8-4c37-44ba-9b72-36b5ffc09bfa` FAILED. Spark 3 không parse `58774-09-09 16:50:00.000000`. 15 cạnh đều `NEW_EDGE`.
- 2026-11-28: `exec ff15ac6b-1e09-4ce4-9ad7-b958944a890f` SUCCESS. Insert 464, update 0, xoá mềm 0. Nguồn 464. `trg_version` 1.
- 2026-11-28: V2 = 41 và 423. V3 = 464 và 464. V4 = 0, 0, 0. V5 = 92 và 0. V7 = 0 và 0. 92 là dòng không có destination theo D-4.
- V6: 2026-11-28, người dùng xác nhận lần chạy `p_force = true` cho `updated = 0` và `inserted = 0`.
