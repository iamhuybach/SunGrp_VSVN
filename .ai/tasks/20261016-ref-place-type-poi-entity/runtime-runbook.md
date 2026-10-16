# Hướng dẫn kiểm chứng runtime

Trạng thái: `PASS`. Fabric DEV 2026-10-16: seed, node, idempotency, từ điển, đối chiếu category và tập cột đều đúng kỳ vọng.

## Phạm vi và môi trường

Fabric DEV. Lakehouse silver `lh_vv_silver`, control `lh_vv_ctrl`. Notebook `NB_SETUP_POI_ENTITY` và `NB_SLV_POI_ENTITY` đã có trong workspace. Không xóa bảng.

## Điều kiện tiên quyết

- `lh_vv_silver.dbo.slv_3p_poi` đã có dữ liệu, gồm `primary_type` và `types_json`.
- `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` đọc được.
- Không có extract 3P đang chạy khi tới câu đối chiếu category.

## Baseline trước khi chạy

```sql
SELECT pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_tbl = 'slv_poi_entity';
```

Kỳ vọng trước lần đầu: 0 dòng. Nếu đã có dòng và `pl_name` là pipeline chu kỳ dài hơn `PL_VV_TRANS_SLV_TO_SLV_1H`, dừng setup. Chuyển bảng sang pipeline chu kỳ ngắn hơn, rồi mới chạy tiếp.

## Các bước thực hiện

1. Mở `NB_SETUP_POI_ENTITY`. Giữ `p_apply = "false"`. Run all.
2. Đọc JSON thoát. Kỳ vọng `status = PLAN`, `google = 297`, `partner = 59`. `missing_keys = 0` khi bảng chưa có.
3. Đổi `p_apply = "true"`. Run all.
4. Đọc JSON thoát. Kỳ vọng `status = SUCCESS`. Lần đầu `inserted = 356`, `edges_inserted = 2`, `drift = 0`.
5. Mở `NB_SLV_POI_ENTITY`. Đặt `p_mode = "DRY_RUN"`. Các tham số còn lại giữ nguyên: `p_exec_id = ""`, `p_run_id = ""`, `p_pl_name = ""`, `p_trg_fq = ""`, `p_pinned_json = ""`, `p_force = "false"`, `p_history_limit = "1000"`. Run all.
6. Notebook thoát thành công, có số insert/update dự kiến. Chưa ghi `slv_poi_entity`.
7. Đặt `p_mode = "RUN"`. Run all.
8. JSON thoát có `status = SUCCESS`.

## Kiểm tra kết quả

Mỗi câu dưới đây kỳ vọng 0, trừ chỗ ghi rõ. Tối đa 50 dòng, không dữ liệu cá nhân, không secret. Dán vào `Kết quả người dùng ghi nhận`.

```sql
SELECT count(*) AS dup_keys FROM (
    SELECT source_name, place_type
    FROM lh_vv_silver.dbo.ref_dictionary_place_type
    GROUP BY source_name, place_type
    HAVING count(*) > 1
);
SELECT count(*) AS bad_place_type
FROM lh_vv_silver.dbo.ref_dictionary_place_type
WHERE place_type IN ('Fallback', 'Không có', 'Partner Portal bổ sung', 'Partner Portal Bổ sung');
SELECT source_name
FROM lh_vv_silver.dbo.ref_dictionary_place_type
WHERE place_type = 'extended_stay_hotel';
SELECT count(DISTINCT updated_at) AS updated_at_values
FROM lh_vv_silver.dbo.ref_dictionary_place_type;
SELECT business_category
FROM lh_vv_silver.dbo.ref_dictionary_place_type
WHERE place_type = 'lodging' AND source_name = 'google';
```

Kỳ vọng: `dup_keys = 0`, `bad_place_type = 0`, `extended_stay_hotel` chỉ có `google`, `updated_at_values = 1`, `business_category = Accommodation`.

Đối chiếu category chỉ khi không có extract đang chạy:

```sql
WITH d AS (
    SELECT lower(trim(place_type)) pt,
           struct(business_sector, business_category, business_category_vi) c
    FROM lh_vv_silver.dbo.ref_dictionary_place_type
    WHERE lower(trim(source_name)) = 'google' AND is_active
),
p AS (
    SELECT poi_id, primary_type, types_json
    FROM lh_vv_silver.dbo.slv_3p_poi
    WHERE lower(trim(source_name)) = 'google'
),
tf AS (
    SELECT e.poi_id, min_by(d.c, e.pos) m
    FROM (
        SELECT p.poi_id, pos, ty
        FROM p
        LATERAL VIEW posexplode(from_json(p.types_json, 'array<string>')) exploded AS pos, ty
    ) e
    JOIN d ON d.pt = lower(trim(e.ty))
    GROUP BY e.poi_id
),
e AS (
    SELECT p.poi_id,
           coalesce(dp.c, tf.m, named_struct(
               'business_sector', 'other',
               'business_category', 'other',
               'business_category_vi', CAST(NULL AS STRING)
           )) c
    FROM p
    LEFT JOIN d dp ON dp.pt = lower(trim(p.primary_type))
    LEFT JOIN tf ON tf.poi_id = p.poi_id
)
SELECT count(*) AS category_mismatch
FROM e
FULL JOIN (
    SELECT * FROM lh_vv_silver.dbo.slv_poi_entity WHERE deleted_at IS NULL
) a ON a.poi_id = e.poi_id
WHERE a.poi_id IS NULL OR e.poi_id IS NULL
   OR NOT (
        e.c.business_sector <=> a.business_sector
        AND e.c.business_category <=> a.business_category
        AND e.c.business_category_vi <=> a.business_category_vi
   );
```

Kỳ vọng `category_mismatch = 0`. Trong notebook, sau `RUN`: `set(spark.table("lh_vv_silver.dbo.slv_3p_poi").columns) <= set(spark.table("lh_vv_silver.dbo.slv_poi_entity").columns)` là `True`.

## Chạy lại để kiểm tra idempotency

Chạy lại `NB_SETUP_POI_ENTITY` với `p_apply = "true"`. Kỳ vọng `inserted = 0`, `edges_inserted = 0`. `drift` được đếm, không ghi đè dòng đã có.

Chạy lại `NB_SLV_POI_ENTITY` với `p_mode = "RUN"`. Kỳ vọng `NO_DATA`, hoặc diff insert/update/xoá mềm đều 0.

## Kiểm tra log và watermark

```sql
SELECT pl_name, trg_tbl, status, started_at, error_message
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_tbl = 'slv_poi_entity'
ORDER BY started_at DESC
LIMIT 5;
```

Kỳ vọng dòng `RUN` mới nhất có `status = SUCCESS`. Watermark cạnh do lib ghi sau `RUN` thành công. Setup không advance watermark.

## Rollback và forward recovery

Dừng đọc, không xóa bảng:

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
SET is_active = 0
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H' AND trg_tbl = 'slv_poi_entity';
```

Sửa một nhãn sai: `UPDATE` đúng dòng trong `ref_dictionary_place_type`, rồi chạy lại node `p_mode = "RUN"`. Seed không ghi đè dòng đã có. Nếu lần seed trước đã ghi `business_sector = fnb`, chạy lại setup không đổi thành `f_n_b`. Khi đó:

```sql
UPDATE lh_vv_silver.dbo.ref_dictionary_place_type
SET business_sector = 'f_n_b'
WHERE business_sector = 'fnb';
```

Rồi chạy lại `NB_SLV_POI_ENTITY` với `p_mode = "RUN"`. Bật lại cạnh: `is_active = 1` trên đúng hai cạnh của `PL_VV_TRANS_SLV_TO_SLV_1H`.

## Kết quả người dùng ghi nhận

Fabric DEV, 2026-10-16. Không có dữ liệu cá nhân.

- Baseline `trg_tbl = slv_poi_entity`: 0 dòng.
- Setup `p_apply=false`: `google=297`, `partner=59`, `missing_keys=0`, `status=PLAN`.
- Setup `p_apply=true`: `inserted=356`, `drift=0`, `edges_inserted=2`, `status=SUCCESS`.
- Node `DRY_RUN`: `inserted=57`, `updated=0`, `deactivated=0`, `status=SUCCESS`, `trg_version=null`. Nguồn 57 dòng google.
- Node `RUN`: `inserted=57`, `updated=0`, `deactivated=0`, `status=SUCCESS`, `trg_version=1`. Log: `Bảng đích: CREATED`.
- Kiểm tra từ điển: `dup_keys=0`, `bad_place_type=0`, `extended_stay_hotel` chỉ `google`, `updated_at_values=1`, `business_category=Accommodation`.
- Đối chiếu category lần đầu: `PARSE_SYNTAX_ERROR` tại `JOIN` sau `LATERAL VIEW`. Câu đã sửa, explode nằm trong subquery.
- Đối chiếu category sau khi sửa câu: `category_mismatch = 0`.
- Tập cột: `set(slv_3p_poi.columns) <= set(slv_poi_entity.columns)` là `True`.
- Setup chạy lại: `inserted=0`, `drift=0`, `edges_inserted=0`, `status=SUCCESS`.
- Node `RUN` lần hai: diff insert/update/xoá mềm đều 0, bỏ qua MERGE, `trg_version=1`, `status=SUCCESS`. Log vẫn ghi `NEW_EDGE` cho cả hai nguồn.
- `ctrl_log_table_run`: ba dòng `SUCCESS`, `error_message` null. Mốc mới nhất `2026-10-16T04:05:41Z`.
