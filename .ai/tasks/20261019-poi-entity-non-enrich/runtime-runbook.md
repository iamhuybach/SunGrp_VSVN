# Hướng dẫn kiểm chứng runtime

Trạng thái: `CHỜ CHẠY`.

Môi trường: Fabric DEV. Không chạy prod trong lượt này.

Kết quả đã có ở `evidence/results/setup-dev.txt` là lần setup trước khi sửa STATE-001 và SQL-001. Các notebook đổi sau lần đó phải được deploy lại rồi chạy lại. Registry 53 cột và `category_group` không NULL đã ghi nhận; chỉ chạy lại hai cell đó khi số đếm lệch.

## Phạm vi và môi trường

Fabric DEV, workspace hiện tại. Lakehouse silver `lh_vv_silver`, control `lh_vv_ctrl`. Không đụng prod. Không `DROP` `slv_poi_entity`.

## Điều kiện tiên quyết

- Notebook trên workspace là bản repo hiện tại, gồm `NB_SETUP_POI_ENTITY`, `NB_SETUP_POI_AMENITY`, `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_ENR_POI_INFO`, `NB_ENR_POI_COORDINATE`.
- `PL_VV_TRANS_SLV_TO_SLV_1H` không đang chạy. Khoá `wm_transform_brz_3rd_crawler_poi_stream` trống trước khi chạy extract 3P.
- P1 ở bước 1 bằng 0. Nếu một trong hai tổng lớn hơn 0, dừng, không chạy ENR.

## Baseline trước khi chạy

Ghi số version mới nhất của `lh_vv_silver.dbo.slv_poi_entity` từ `DESCRIBE HISTORY` và `count(*)` của `lh_vv_silver.dbo.slv_poi_amenity`. Đây là mốc cho V7 và V10.

## Các bước thực hiện

1. Probe P1, P2, P3. Chỉ đọc.
2. Nếu registry chưa là 53 cột: trong `NB_CREATE_DDL` chạy `0f228dc1`, `e9c137c5`, `0271d481`, rồi `nonenrpy`. Bản DEV đã đạt 53 và `category_group` không NULL thì bỏ qua.
3. `NB_SETUP_POI_ENTITY`: `p_apply = "false"`, đọc plan, rồi `p_apply = "true"`.
4. `NB_SETUP_POI_AMENITY`: `p_apply = "false"`, rồi `p_apply = "true"`.
5. `NB_SLV_POI_ENTITY_NON_ENRICH` với tham số cell `b1entityparam`, chỉ đổi `p_mode`:
   - `p_exec_id = ""`
   - `p_run_id = ""`
   - `p_pl_name = ""`
   - `p_trg_fq = ""`
   - `p_pinned_json = ""`
   - `p_mode = "DRY_RUN"` lần 1, `"RUN"` lần 2
   - `p_force = "false"`
   - `p_history_limit = "1000"`
6. `NB_SLV_POI_AMENITY` cùng bộ tham số, `p_mode = "RUN"`, `p_force = "false"`.
7. `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` với cell tham số sẵn có: `dry_run = False`, `full_reload = False`, `sources = "google"`, `src_tbl = "brz_3rd_crawler_poi_stream"`.
8. `NB_00_ORCHES_SLV_TO_ENR_15P` với cell tham số sẵn có: `p_pl_name = "PL_VV_TRANS_SLV_TO_ENR_15P"`, `p_mode = "RUN"`, `p_force_nodes = ""`, `p_run_id = ""`.
9. Chạy các câu V1–V10 ở mục kiểm tra.

Không chạy `NB_00` của `PL_VV_TRANS_SLV_TO_SLV_1H` trước khi bước 3 và 4 thành công.

## Kiểm tra kết quả

Dán số tổng, không dán dòng cá nhân. Tối đa 50 dòng.

- P1, trên `lh_vv_silver.dbo.slv_3p_poi_address`: `count(*)`, `sum(city IS NULL AND state_province IS NOT NULL)`, `sum(city <> state_province)`. Cả hai tổng phải bằng 0.
- P2: danh sách report, view, workspace khác còn đọc `slv_poi_entity`. Ghi "không thấy" nếu hết.
- P3: `DESCRIBE lh_vv_silver.dbo.slv_pn_business_service_i18ns` có cột `deleted`.
- V1: registry 3P = 53 dòng, 0 dòng `subcategory_tags_json` và 0 dòng `state_province`.
- V2: `category_group` NULL = 0. `(google, hotel)` = Lodging, `(google, cafe)` = Light Snacks / Cafe, `(partner, Hotel)` = Other.
- V3: cạnh active `PL_VV_TRANS_SLV_TO_SLV_1H`, schema `lh_vv_silver.dbo`: 5 vào `slv_poi_entity_non_enrich`, 3 vào `slv_poi_amenity`, 0 active có `trg_tbl = 'slv_poi_entity'` hoặc `src_tbl = 'slv_poi_entity'`.
- V4: exit entity `SUCCESS`. Dòng google bằng `count(slv_3p_poi)` với `lower(trim(source_name)) = 'google'`. Dòng partner = 24. `count(distinct poi_id) = count(*)`. `poi_id` partner khớp `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`. Mọi dòng partner có `business_category = business_sector` và `category_group = 'Other'`.
- V5: số dòng google có địa chỉ xấp xỉ số `poi_id` google trong `slv_3p_poi_address`. `DESCRIBE` đích không có `subcategory_tags_json`.
- V7: exit amenity `SUCCESS`. `count(*)` amenity bằng baseline.
- V8: exit extract `SUCCESS`. Dòng 3P mới có `subcategory_tags_json` và `state_province` là NULL. Chỉ đếm, không lấy mẫu địa chỉ.
- V9: exit ENR `SUCCESS`. Phân phối `destination_name` không đổi so với run trước khi P1 = 0.
- V10: `DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_entity` không có version mới sau mốc baseline.

Bước 3 kỳ vọng lần này: `edges_inserted = 0`, `edges_retired = 0` vì DEV đã chuyển cạnh. Lần đầu trên môi trường chưa chuyển vẫn là 5 và 2. Bước 4: `edges_inserted = 0`, `edges_retired = 0`. `drift = 6` của amenity là lệch seed đã biết, không phải lỗi cạnh.

## Chạy lại để kiểm tra idempotency

V6. Chạy lại `NB_SLV_POI_ENTITY_NON_ENRICH` khi đầu vào không đổi: `p_mode = "RUN"`, `p_force = "false"`, các tham số còn lại như bước 5. Kỳ vọng exit `NO_DATA`.

Sau đó cùng notebook với `p_force = "true"`. Kỳ vọng insert, update và delete đều 0, version Delta của đích không tăng.

## Kiểm tra log và watermark

Sau bước 5 và 6, dán status mới nhất trong `ctrl_log_table_run` của `slv_poi_entity_non_enrich` và `slv_poi_amenity`, cùng `lock_exec_id` của khoá `PL_VV_TRANS_SLV_TO_SLV_1H`. Khoá phải trống khi notebook đã thoát. Watermark cạnh mới có dạng `wm_e__<trg_tbl>__<src_tbl>`.

## Rollback và forward recovery

Ưu tiên chạy lại bước lỗi. Mỗi bước chạy lại được.

Rollback chỉ khi `PL_VV_TRANS_SLV_TO_SLV_1H` đang rảnh:

1. Deploy lại notebook cũ có `NB_SLV_POI_ENTITY`.
2. Tắt cạnh mới và bật lại cạnh cũ:

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 0
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H' AND is_active = 1
  AND (trg_tbl = 'slv_poi_entity_non_enrich'
       OR (trg_tbl = 'slv_poi_amenity' AND src_tbl = 'slv_poi_entity_non_enrich'));
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 1
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H' AND is_active = 0
  AND ((trg_tbl = 'slv_poi_entity' AND src_tbl IN ('slv_3p_poi', 'ref_dictionary_place_type'))
       OR (trg_tbl = 'slv_poi_amenity' AND src_tbl = 'slv_poi_entity'));
```

3. Chạy node entity cũ rồi amenity cũ. Watermark cũ còn, node tính lại.
4. Không `DROP` `category_group`. Không chạy `NB_SETUP_POI_ENTITY` bản cũ. `slv_poi_entity_non_enrich` để nguyên cho đến khi có quyết định khác.

## Kết quả người dùng ghi nhận

Đã ghi ở `evidence/results/runtime-dev.txt`. P1–P3, V1–V3, V6, V7, V8, V10 và khoá luồng đã có. V6 và 43 dòng amenity xoá mềm đã được chấp nhận. ENR 15P không chạy trong task này.
