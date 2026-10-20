# Hướng dẫn kiểm chứng runtime

Trạng thái: `ĐÃ CHẠY`. R5 và lần idempotent đạt. User xác nhận `gates.runtime = pass` ngày 2026-10-20.

Môi trường: Fabric DEV. Lakehouse `lh_vv_silver`, `lh_vv_ctrl`. Agent không chạy các bước này và không đặt `gates.runtime`.

## Phạm vi và môi trường

DEV. Chỉ `slv_poi_entity_non_enrich` và `slv_poi_amenity` được DROP, rồi dựng lại. Chỉ watermark `wm_e__` của hai bảng đó bị xoá. Không đụng `slv_3p_*`, `slv_pn_*`, hai bảng từ điển, và không xoá dòng `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`.

## Điều kiện tiên quyết

Sáu notebook đã đồng bộ lên workspace DEV: `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_SLV_POI_AMENITY`, `NB_SETUP_POI_ENTITY`, `NB_SETUP_POI_AMENITY`, `NB_SETUP_INITIAL_DDL`, `NB_CREATE_DDL`.

Cell `b1entitybuild` trên Fabric có `"contact": "slv_3p_poi_contact"`.

`p_apply` mặc định `"false"`. Bước ghi (R3, R4) tách riêng, chỉ chạy sau khi R1 và R2 đúng.

## Baseline trước khi chạy

R1, chỉ đọc. Lưu kết quả. Khác kỳ vọng thì dừng.

Khoá luồng phải null:

```sql
SELECT watermark_id, lock_exec_id, lock_at, status
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H';
```

Đếm trước khi xoá, gồm số dòng `deleted_at IS NULL`:

```sql
SELECT count(*) AS n, count_if(deleted_at IS NULL) AS live
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich;
SELECT count(*) AS n, count_if(deleted_at IS NULL) AS live
FROM lh_vv_silver.dbo.slv_poi_amenity;
```

Watermark sẽ bị xoá, giữ lại để đối chiếu rollback:

```sql
SELECT watermark_id, src_tbl, trg_tbl, last_src_version, last_src_table_id, status
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE substr(watermark_id, 1, 6) = 'wm_e__'
  AND trg_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN ('slv_poi_entity_non_enrich', 'slv_poi_amenity')
ORDER BY watermark_id;
```

Contact: số `poi_id` trùng phải là 0. Lớn hơn 0 thì dừng, `USER_DECISION` theo D3, không DROP. Tổng contact phải lớn hơn 0.

```sql
SELECT count(*) AS dup_poi
FROM (
    SELECT poi_id FROM lh_vv_silver.dbo.slv_3p_poi_contact
    WHERE poi_id IS NOT NULL GROUP BY poi_id HAVING count(*) > 1
);
SELECT count(*) AS n FROM lh_vv_silver.dbo.slv_3p_poi_contact;
```

`DESCRIBE lh_vv_silver.dbo.ref_dictionary_place_type`: `range_low_min`, `range_high_min`, `avg_range_min` là `int`; `candidate_best_time_code`, `canonical_candidate` là `string`.

`DESCRIBE lh_vv_silver.dbo.ref_dictionary_amenities`: `service_flags` là `string`.

`DESCRIBE lh_vv_silver.dbo.slv_3p_poi` vẫn có `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`.

## Các bước thực hiện

R2. Chạy `NB_SETUP_POI_ENTITY` và `NB_SETUP_POI_AMENITY` với `p_apply = "false"`.

- Entity: `missing_keys = 0`, `unseeded_rows = 0`, `planned_edges` có 6 tên và có `slv_3p_poi_contact`.
- Amenity: `missing_keys = 0`.
- `missing_keys` lớn hơn 0 thì dừng. Apply lúc đó sẽ chèn dòng từ điển, tức là reseed.

R3. Apply xoá, chỉ sau R1 và R2. Giữ khoá đến khi DROP và DELETE xong và đã kiểm tra. Nhả khoá trước R4, vì notebook dựng lại tự nhận khoá. Không xoá dòng `wm_flow__`.

Bước R3a, tạo dòng khoá nếu chưa có rồi nhận khoá. Chạy riêng, chưa DROP.

```sql
MERGE INTO lh_vv_ctrl.dbo.ctrl_mng_watermark AS t
USING (SELECT 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H' AS watermark_id, 'PL_VV_TRANS_SLV_TO_SLV_1H' AS src_tbl, 'runbook-20261020-entity-reset' AS flow_name) AS s
ON t.watermark_id = s.watermark_id
WHEN NOT MATCHED THEN INSERT
    (watermark_id, src_schema, src_tbl, trg_schema, trg_tbl, watermark_column, watermark_value, last_success_at,
     status, flow_name, watermark_sequence, last_run_id, last_src_version, last_src_table_id, error_message,
     lock_exec_id, lock_at, updated_at)
VALUES
    (s.watermark_id, CAST(NULL AS STRING), s.src_tbl, CAST(NULL AS STRING), CAST(NULL AS STRING), CAST(NULL AS STRING),
     CAST(NULL AS TIMESTAMP), CAST(NULL AS TIMESTAMP), 'INITIALIZED', s.flow_name, CAST(NULL AS BIGINT),
     CAST(NULL AS STRING), CAST(NULL AS BIGINT), CAST(NULL AS STRING), CAST(NULL AS STRING), CAST(NULL AS STRING),
     CAST(NULL AS TIMESTAMP), current_timestamp());
UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark
SET lock_exec_id = 'runbook-20261020-entity-reset', lock_at = current_timestamp(), status = 'RUNNING', updated_at = current_timestamp()
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H' AND lock_exec_id IS NULL;
```

Bước R3b, chạy riêng và đọc kết quả trước khi DROP. Đúng một dòng và `lock_exec_id` đúng `runbook-20261020-entity-reset`. Khác thì DỪNG, không DROP, không DELETE.

```sql
SELECT watermark_id, lock_exec_id, lock_at, status
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H';
```

Bước R3c, chỉ sau R3b đúng.

```sql
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_poi_amenity;
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_poi_entity_non_enrich;
DELETE FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE substr(watermark_id, 1, 6) = 'wm_e__'
  AND trg_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN ('slv_poi_entity_non_enrich', 'slv_poi_amenity');
```

Bước R3d, cùng WHERE của DELETE còn 0 dòng, và `SHOW TABLES IN lh_vv_silver.dbo` không còn hai bảng. Sau đó mới nhả khoá. Nếu R3c dừng giữa chừng, chưa nhả: sửa rồi chạy tiếp R3c, hoặc nhả bằng UPDATE dưới khi chắc không còn notebook nào chạy.

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark
SET lock_exec_id = NULL, lock_at = NULL, status = 'SUCCESS', updated_at = current_timestamp()
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H' AND lock_exec_id = 'runbook-20261020-entity-reset';
```

R4. Dựng lại.

1. `NB_SETUP_POI_ENTITY`, `p_apply = "true"`. Kỳ vọng `inserted = 0`, `edges_inserted = 1`, `edges_retired = 0`.
2. `NB_SETUP_POI_AMENITY`, `p_apply = "true"`. Kỳ vọng `inserted = 0`. Notebook tạo `slv_poi_amenity` có `service_flags`.
3. `NB_00` với `p_pl_name = PL_VV_TRANS_SLV_TO_SLV_1H`. Không chạy tay từng node. `ensure_target` tạo bảng entity.

## Kiểm tra kết quả

R5.

1. `DESCRIBE lh_vv_silver.dbo.slv_poi_entity_non_enrich`: không còn bốn cột op; `website_url` ngay sau `primary_type`; năm cột ước tính ngay sau `category_group`.
2. `DESCRIBE lh_vv_silver.dbo.slv_3p_poi` vẫn có bốn cột op.
3. Dòng `deleted_at IS NULL`: `count(*) = count(DISTINCT poi_id)` trên entity.
4. Google `website_url` lệch 0:

```sql
SELECT count(*) FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich e
LEFT JOIN lh_vv_silver.dbo.slv_3p_poi_contact c ON c.poi_id = e.poi_id
WHERE e.source_name = 'google' AND NOT (e.website_url <=> c.website_url);
```

5. Partner: tổng `qg_json.metrics.partner_website` bằng `partner_rows`. Số lệch so với `get_json_object(s.website_urls, '$.website_url')` (join `s.id = e.source_id`) bằng số `NOT_STRING`. Nếu `NO_VALUE` bằng `partner_rows` mà JSON thô vẫn có khoá, dừng.
6. Google `range_low_min` lệch 0 trên dòng `business_category` khác `other`, khớp `primary_type` với dòng google active. Dòng khớp qua `types_json` xem metric `by_types`.
7. Partner `range_low_min` lệch 0 với dòng partner active có `d.place_type = e.primary_type`.
8. Amenity: `service_flags` ngay sau `amenity_vi`. Lệch 0 với dòng google active trên (`business_sector`, `amenity_group`, `amenity_raw`).
9. `wm_e__` được tạo lại: 6 dòng entity, 3 dòng amenity, `status = SUCCESS`.
10. Hai từ điển: version và số dòng bằng R1, `inserted = 0`.

## Chạy lại để kiểm tra idempotency

Chạy `NB_00` lần hai, cùng `p_pl_name = PL_VV_TRANS_SLV_TO_SLV_1H`. Cả hai node `NO_DATA`. Không có version mới của bảng đích.

## Kiểm tra log và watermark

`ctrl_log_table_run` của lần R4 có `qg_json` với `google_with_website`, `partner_website`, `dict_estimate_null`. Watermark cạnh entity là 6, amenity là 3. Dòng `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H` còn, `lock_exec_id` null.

## Rollback và forward recovery

DROP làm mất `created_at` cũ, dòng soft-delete và lịch sử Delta. Hai bảng là RECOMPUTE nên dựng lại được. Số đếm R1 và watermark đã lưu là mốc so sánh.

Rollback schema cũ. Nhận khoá trước mọi thay đổi. `NB_SETUP_POI_AMENITY` và `NB_00` tự nhận khoá, nên chỉ nhả ngay trước hai notebook đó, sau khi cạnh đã tắt và bảng đã DROP.

1. Chạy R3a rồi R3b. `lock_exec_id` phải là `runbook-20261020-entity-reset`. Khác thì dừng.
2. Revert commit của task trên Git và đồng bộ notebook cũ lên DEV. Khoá vẫn giữ.
3. Tắt cạnh contact, khoá vẫn giữ:

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
SET is_active = 0
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H'
  AND src_schema = 'lh_vv_silver.dbo' AND src_tbl = 'slv_3p_poi_contact'
  AND trg_schema = 'lh_vv_silver.dbo' AND trg_tbl = 'slv_poi_entity_non_enrich'
  AND is_active = 1;
```

4. Chạy R3c rồi kiểm tra R3d (0 dòng `wm_e__`, hai bảng không còn). Khoá vẫn giữ trong lúc DROP.
5. Nhả khoá bằng UPDATE cuối của R3d.
6. Chạy `NB_SETUP_POI_AMENITY` bản cũ, `p_apply = "true"`.
7. Chạy `NB_00`. Schema cũ, gồm cột op, được dựng từ nguồn. Không cần khôi phục watermark đã xoá: thiếu dòng nghĩa là `NEW_EDGE`. Đọc lại `lock_exec_id` của `wm_flow__`: phải null.

Forward: lỗi code thì sửa và chạy lại `NB_00`. `ConfigError` kiểu cột thì lặp R3 rồi R4. Trùng `poi_id` contact thì dừng, không có gì được ghi.

## Kết quả người dùng ghi nhận

Lần chạy 2026-10-20 trên DEV. R1–R3 đạt. R4 dựng node dừng ở `PARTIAL_FAILED`. `gates.runtime` vẫn `pending`.

R1. `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`: `lock_exec_id` null, `status = SUCCESS`. Hai bảng node `n = 0`, `live = 0`. Không có dòng `wm_e__`. `dup_poi = 0`. `slv_3p_poi_contact` có 345 dòng. Từ điển place type có 3 cột range `int` và 2 cột estimate `string`. Từ điển amenity có `service_flags string`. `slv_3p_poi` còn bốn cột op.

R2. Entity PLAN: `missing_keys = 0`, `unseeded_rows = 0`, 6 `planned_edges` gồm `slv_3p_poi_contact`. Amenity PLAN: `missing_keys = 0`, `entity_edges_ok = 5` vì cạnh contact chưa được chèn.

R3. MERGE khoá chèn 0 dòng (dòng flow đã có). UPDATE nhận khoá đụng 1 dòng. R3b: `lock_exec_id = runbook-20261020-entity-reset`, `status = RUNNING`, `lock_at = 2026-10-20T09:35:33Z`. DELETE `wm_e__` đụng 0 dòng. Nhả khoá đụng 1 dòng.

R4. `NB_SETUP_POI_ENTITY` `p_apply = true`: `inserted = 0`, `drift = 47`, `edges_inserted = 1`, `edges_retired = 0`. `drift = 47` không cập nhật dòng từ điển đã có, vì MERGE chỉ `WHEN NOT MATCHED`. `NB_SETUP_POI_AMENITY` `p_apply = true`: `inserted = 0`, `drift = 0`, `edges_inserted = 0`, và log vẫn in `entity_edges_ok = 5`. Bản trong repo dừng khi số này khác 6, nên notebook amenity trên Fabric chưa phải bản repo.

`NB_00` exec `11667d08-c12b-4980-865e-6567340c797a`, 9 cạnh `NEW_EDGE`, rồi `runMultiple` ném `NotebookExecutionException`: notebook con gắn default lakehouse khác notebook cha. Hai node `NOT_RUN`. Tiến 0 cạnh. Kết thúc `PARTIAL_FAILED` sau 61 giây. Không có bảng node mới, không có watermark cạnh mới.

Repo `NB_LIB_TRANSFORM_SLV_GLD` đã truyền `useRootDefaultLakehouse: True` cả trong args của activity và trong `runMultiple`. Log Fabric không đi qua nhánh đó. `NB_00` và lib không nằm trong sáu notebook của R0.

Lần 2, exec `4704e1a4-d6fd-446b-a320-962dc8d0dbb9`. Lakehouse đã qua. Entity `SUCCESS`: `inserted = 65`, `updated = 0`, `deactivated = 0`, `trg_version = 1`. Tiến 6 cạnh. Amenity `ConfigError`: `p_exec_id` rỗng nên notebook coi là chạy tay trong lúc exec này giữ khoá từ `2026-10-20 10:12:16`. Orchestrator ghi amenity `NOT_RUN`. `PARTIAL_FAILED` sau 223 giây. Cell `d1amenparam` thiếu tag `parameters`. D14 đã gắn tag trong repo. Không DROP entity.

Lần 3, exec `778dcf64-0015-408c-ada2-b88f1d48ccaa`. Kế hoạch còn 3 Dirty Edge, đều của amenity. Entity không còn là ứng viên. Amenity `SUCCESS`: `inserted = 58`, `updated = 0`, `deactivated = 0`, `trg_version = 1`. Tiến 3 cạnh. `NB_00` `SUCCESS` sau 123 giây, `tbl_success_count = 1`.

R5. Entity không còn bốn cột op. `website_url` ngay sau `primary_type`. Năm cột ước tính ngay sau `category_group`, đúng kiểu `int`, `int`, `int`, `string`, `string`. Amenity có `service_flags string` ngay sau `amenity_vi`. `slv_3p_poi` còn bốn cột op. Grain `n = poi = 65`. `google_website_mismatch = 0`, `partner_website_mismatch = 0`, `google_range_mismatch = 0`, `partner_range_mismatch = 0`, `amenity_flag_mismatch = 0`. Watermark entity `SUCCESS` 6 dòng, amenity `SUCCESS` 3 dòng. `wm_flow__` `lock_exec_id` null, `status = SUCCESS`.

Lần idempotent, exec `86a52eee-474c-45ec-9d3b-2483cab3b0aa`. Kế hoạch 2 node, 9 cạnh, 0 Dirty Edge, 0 node ứng viên. `NB_00` `NO_DATA` sau 81 giây. `tbl_total_count = 0`. Partner `partner_rows = 24`, `with_website = 1`, nên không rơi vào trường hợp mọi dòng partner đều null. User xác nhận `gates.runtime = pass` ngày 2026-10-20.
