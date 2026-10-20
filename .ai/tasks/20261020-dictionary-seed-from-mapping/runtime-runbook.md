# Hướng dẫn kiểm chứng runtime

Trạng thái: `CHỜ CHẠY`.

User chạy trên Fabric DEV. Agent không đánh `gates.runtime`. R3 là điểm dừng trước mọi lệnh DROP.

## Phạm vi và môi trường

- Môi trường: Fabric DEV, lakehouse `lh_vv_silver`.
- Notebook: `NB_SETUP_POI_ENTITY`, `NB_SETUP_POI_AMENITY`, `NB_SETUP_INITIAL_DDL`, cell `dictseedpy` của `NB_CREATE_DDL`.
- Bảng: `lh_vv_silver.dbo.ref_dictionary_place_type`, `lh_vv_silver.dbo.ref_dictionary_amenities`.
- Pipeline cần tạm dừng: `PL_VV_TRANS_SLV_TO_SLV_1H`.

## Điều kiện tiên quyết

- R0. Commit đã sync lên DEV. `python scripts/vv.py verify 20261020-dictionary-seed-from-mapping` xanh. D-07 đã ghi trong `decision.md`.
- R1. Tắt schedule `PL_VV_TRANS_SLV_TO_SLV_1H` và xác nhận Fabric Monitor không còn lần chạy đang active.

## Baseline trước khi chạy

R2. Chạy SQL sau và ghi số. Kỳ vọng place type: google 297, partner 59. Amenity: google 84, partner 74.

Nếu `ref_dictionary_place_type_bak_20261020` hoặc `ref_dictionary_amenities_bak_20261020` đã tồn tại thì dừng. Không xoá và không dùng lại bản cũ.

```sql
SELECT source_name, count(*) n FROM lh_vv_silver.dbo.ref_dictionary_place_type GROUP BY 1;
SELECT source_name, count(*) n FROM lh_vv_silver.dbo.ref_dictionary_amenities GROUP BY 1;
SELECT category_group, count(*) n FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich WHERE deleted_at IS NULL GROUP BY 1;
SELECT count(*) n FROM lh_vv_silver.dbo.slv_poi_amenity WHERE deleted_at IS NULL;
CREATE TABLE lh_vv_silver.dbo.ref_dictionary_place_type_bak_20261020 USING DELTA AS
SELECT source_name, place_type, business_sector, business_category, business_category_vi, is_active, updated_at, category_group
FROM lh_vv_silver.dbo.ref_dictionary_place_type;
CREATE TABLE lh_vv_silver.dbo.ref_dictionary_amenities_bak_20261020 USING DELTA AS
SELECT source_name, business_sector, amenity_group, amenity_raw, amenity, amenity_vi, is_active, updated_at
FROM lh_vv_silver.dbo.ref_dictionary_amenities;
```

Đối chiếu hai chiều. Mỗi câu phải ra 0 dòng rồi mới được DROP.

```sql
SELECT source_name, place_type, business_sector, business_category, business_category_vi, is_active, updated_at, category_group
FROM lh_vv_silver.dbo.ref_dictionary_place_type
EXCEPT ALL
SELECT source_name, place_type, business_sector, business_category, business_category_vi, is_active, updated_at, category_group
FROM lh_vv_silver.dbo.ref_dictionary_place_type_bak_20261020;
SELECT source_name, place_type, business_sector, business_category, business_category_vi, is_active, updated_at, category_group
FROM lh_vv_silver.dbo.ref_dictionary_place_type_bak_20261020
EXCEPT ALL
SELECT source_name, place_type, business_sector, business_category, business_category_vi, is_active, updated_at, category_group
FROM lh_vv_silver.dbo.ref_dictionary_place_type;
SELECT source_name, business_sector, amenity_group, amenity_raw, amenity, amenity_vi, is_active, updated_at
FROM lh_vv_silver.dbo.ref_dictionary_amenities
EXCEPT ALL
SELECT source_name, business_sector, amenity_group, amenity_raw, amenity, amenity_vi, is_active, updated_at
FROM lh_vv_silver.dbo.ref_dictionary_amenities_bak_20261020;
SELECT source_name, business_sector, amenity_group, amenity_raw, amenity, amenity_vi, is_active, updated_at
FROM lh_vv_silver.dbo.ref_dictionary_amenities_bak_20261020
EXCEPT ALL
SELECT source_name, business_sector, amenity_group, amenity_raw, amenity, amenity_vi, is_active, updated_at
FROM lh_vv_silver.dbo.ref_dictionary_amenities;
```

## Các bước thực hiện

1. R3. Plan, không ghi.
   - `NB_SETUP_POI_ENTITY`, parameter `p_apply` = `false`. Kỳ vọng exit `PLAN`, `google=328`, `partner=59`, `missing_keys=31`, `unseeded_rows=-1`.
   - `NB_SETUP_POI_AMENITY`, parameter `p_apply` = `false`. Kỳ vọng `google=101`, `partner=74`, `missing_keys=17`, `stale_keys=0`.
   - Dừng. User xem số trước khi DROP.
2. R4. `DROP TABLE lh_vv_silver.dbo.ref_dictionary_place_type;`
3. R5. `NB_SETUP_POI_ENTITY`, `p_apply` = `true`. Kỳ vọng `inserted=387`, `drift=0`, status `SUCCESS`.
4. R6 và R6b đã xong ngày 2026-10-20. `slv_poi_amenity` đã DROP và tạo lại. Lần seed `inserted=175`, `drift=0` chưa có cột `service_flags`. Không DROP lại `slv_poi_amenity`. Không DROP `ref_dictionary_place_type`. Giữ 1H tắt.
5. R6c đã xong ngày 2026-10-20. `inserted=175`, `drift=0`. `service_flags`: NULL 107, Accessibility 9, Derived amenities 12, Food/service 20, Parking 12, Payment 3, Suitability 12. Không DROP lại.
6. R8 đã xong ngày 2026-10-20. `NB_SETUP_INITIAL_DDL`, `p_apply` = `false`. User xác nhận đạt: không `ConfigError`, `to_insert=0`.
7. R9 đã xong. `dictseedpy` in `có cột service_flags` và `đủ cột và giá trị 1.9`.
8. Idempotency đã xong khi 1H vẫn tắt. Hai notebook setup `p_apply` = `true`, user xác nhận `inserted=0`, `drift=0`.
9. R10 bị bỏ qua theo D-10 ngày 2026-10-20. Chưa chạy `PL_VV_TRANS_SLV_TO_SLV_1H`. `gates.runtime` vẫn `pending`.

## Kiểm tra kết quả

R7, sau R6:

```sql
SELECT source_name, count(*) FROM lh_vv_silver.dbo.ref_dictionary_place_type GROUP BY 1;
SELECT count(*) FROM lh_vv_silver.dbo.ref_dictionary_place_type
 WHERE category_group IS NULL OR range_low_min IS NULL OR range_high_min IS NULL OR avg_range_min IS NULL
    OR candidate_best_time_code IS NULL OR canonical_candidate IS NULL;
SELECT category_group, count(*) FROM lh_vv_silver.dbo.ref_dictionary_place_type GROUP BY 1 ORDER BY 1;
SELECT candidate_best_time_code, canonical_candidate, count(*) FROM lh_vv_silver.dbo.ref_dictionary_place_type GROUP BY 1, 2 ORDER BY 1;
SELECT place_type, category_group, range_low_min, range_high_min, avg_range_min FROM lh_vv_silver.dbo.ref_dictionary_place_type
 WHERE source_name = 'partner' AND place_type IN ('Hotel', 'Homestay', 'Café', 'Vietnamese', 'Car with Driver');
SELECT source_name, business_sector, count(*) FROM lh_vv_silver.dbo.ref_dictionary_amenities GROUP BY 1, 2;
SELECT service_flags, count(*) FROM lh_vv_silver.dbo.ref_dictionary_amenities GROUP BY 1 ORDER BY 1;
```

Pass: place type google 328 và partner 59; câu đếm NULL = 0; amenity google/other = 17, tổng google 101 và partner 74. Partner: Hotel Lodging 1200/1200/1200, Homestay Lodging 1200/1200/1200, Café Light Snacks / Cafe 45/60/60, Vietnamese Other 60/90/75, Car with Driver Other 60/90/75. `service_flags`: `Food/service` 20, `Suitability` 12, `Payment` 3, `Parking` 12, `Accessibility` 9, `Derived amenities` 12, NULL 107.

R10: chạy lại hai câu downstream của R2. Phân bố `category_group` của `slv_poi_entity_non_enrich` bằng baseline. `slv_poi_amenity` đã DROP ở R6b nên đang 0 dòng cho đến khi 1H tính lại; ghi số mới, không so với 58 dòng cũ.

## Chạy lại để kiểm tra idempotency

Làm bước này trước R10, khi `PL_VV_TRANS_SLV_TO_SLV_1H` vẫn tắt và Monitor không có run active.

Chạy lại `NB_SETUP_POI_ENTITY` rồi `NB_SETUP_POI_AMENITY` với `p_apply` = `true`. Kỳ vọng mỗi notebook `inserted=0`, `drift=0`.

## Kiểm tra log và watermark

R10 ghi reason cạnh `TABLE_RECREATED` trên `ctrl_mng_pipeline_edge` (hoặc log notebook 1H). Không đổi watermark nguồn. Không có run 1H active ở R1.

## Rollback và forward recovery

RB, khi cần quay lại:

1. Tắt schedule 1H.
2. `git revert` commit này và sync DEV về bản đó.
3. `DROP` hai bảng vừa dựng lại.
4. Tạo lại từng bảng bằng DDL cũ trong `a1setupddl` / `c1setupddl` của bản revert. Giữ `NOT NULL`. Không dùng CTAS.
5. `INSERT INTO <bảng> (<cột cũ>) SELECT <cột cũ> FROM <bảng>_bak_20261020`.
6. Chạy hai notebook setup bản cũ với `p_apply` = `true`. Kỳ vọng `inserted=0`. Drift bằng drift trước khi đổi, nếu R2 đã ghi.
7. So số dòng với R2.
8. Bật lại 1H. Cạnh thấy `TABLE_RECREATED` và tính lại.

R12. `DROP` hai bảng `*_bak_20261020` chỉ sau khi user chấp nhận kết quả.

## Kết quả người dùng ghi nhận

Dán output đã làm sạch vào `.ai/tasks/20261020-dictionary-seed-from-mapping/evidence/results/`. Tối đa 50 dòng mỗi mẫu. Không dữ liệu cá nhân, không secret. User tự đánh `gates.runtime` sau khi đối chiếu R3–R10.
