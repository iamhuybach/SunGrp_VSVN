# Hướng dẫn kiểm chứng runtime

Trạng thái: `PASS`.

Môi trường: Fabric DEV. Lakehouse `lh_vv_silver`, `lh_vv_gold`, `lh_vv_ctrl`. Không chạy production.

`STATE-001` đã `accepted-risk`. `specialist_review` vẫn là `fix_required`. Chưa có pipeline lịch nào truyền `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_1H`. Đến lúc đó `gld_srv_poi_amenity` chỉ đổi khi chạy tay notebook điều phối. Không tạo pipeline mới.

## Phạm vi và môi trường

Ba bảng mới: `lh_vv_silver.dbo.slv_poi_media_info`, `lh_vv_gold.dbo.gld_srv_poi_media_gallery`, `lh_vv_gold.dbo.gld_srv_poi_amenity`.

Notebook trên workspace DEV phải là bản trong repo: `NB_LIB_TRANSFORM_SLV_GLD`, `NB_CREATE_DDL`, `NB_SLV_POI_MEDIA_INFO`, `NB_GLD_SRV_POI_MEDIA_GALLERY`, `NB_GLD_SRV_POI_AMENITY`, `NB_00_ORCHES_SLV_TO_GLD`.

Không chạy toàn bộ `NB_SETUP_INITIAL_DDL`. DEV đã có lakehouse. Chỉ chạy hai cell patch.

## Điều kiện tiên quyết

Bốn bảng nguồn đã có: `lh_vv_silver.dbo.slv_3p_poi_media`, `slv_pn_business_service_i18ns`, `slv_pn_business_services`, `slv_poi_amenity`.

Không có run `PL_VV_TRANS_SLV_TO_GLD_30P` hoặc `PL_VV_TRANS_SLV_TO_GLD_1H` đang giữ khóa `wm_flow__`.

Tham số giữ nguyên default của notebook, trừ hai giá trị ghi ở từng bước. Default `NB_00_ORCHES_SLV_TO_GLD`:

- `p_run_id = ""`
- `p_max_parallel = "3"`
- `p_node_timeout_min = "20"`
- `p_dag_timeout_min = "45"`
- `p_lock_timeout_min = "90"`
- `p_force_nodes = ""`
- `p_history_limit = "1000"`
- `p_non_data_ops = ""`

Default trong file của `p_pl_name` là `PL_VV_TRANSFORM_SLV_TO_GLD_1H`. Không dùng token đó. Điền đúng token `TRANS` ở các bước dưới.

## Baseline trước khi chạy

Ghi lại, không cần dán URL:

1. `DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_amenity` — version mới nhất. Sau bước 1H, version này không được tăng.
2. Ba bảng đích chưa có, hoặc đã có từ một lần chạy thử trước. Nếu đã có, ghi version mới nhất của mỗi bảng.

## Các bước thực hiện

1. Trong `NB_CREATE_DDL`, chạy cell `mediaddlpy` (`PL_VV_TRANS_SLV_TO_GLD_30P`). Chạy lại cell đó lần hai.
2. Chạy cell `amenddlpy` (`PL_VV_TRANS_SLV_TO_GLD_1H`). Chạy lại cell đó lần hai.
3. Notebook Spark DEV, không ghi bảng:
   - Cell 1: `%run NB_LIB_TRANSFORM_SLV_GLD`
   - Cell 2: dán riêng code cell `slvmediabuild` của `NB_SLV_POI_MEDIA_INFO`
   - Cell 3: dán `.ai/tasks/20261025-poi-media-and-srv-amenity/evidence/probes/media_build_fixture.py`
4. `NB_00_ORCHES_SLV_TO_GLD` với `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_30P`, `p_mode = PLAN`.
5. Cùng notebook, `p_mode = RUN`. Chạy lần hai với cùng `p_pl_name` và `p_mode = RUN`.
6. `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_1H`, `p_mode = PLAN`.
7. `p_mode = RUN`. Chạy lần hai với cùng `p_pl_name` và `p_mode = RUN`.

`PLAN` không khóa và không ghi. Mỗi `RUN` dùng `exec_id` mới do notebook in ra. Ghi `exec_id` của lần RUN đầu cho từng `pl_name`.

## Kiểm tra kết quả

Đạt khi tất cả mục dưới đúng. Dán stdout đã rút gọn vào mục `Kết quả người dùng ghi nhận`. Tối đa 50 dòng mỗi mục. Không URL, không dữ liệu cá nhân, không secret.

- Fixture: mỗi dòng `F1` đến `F11` là `PASS`, dòng cuối `fixture_fail 0`. `F7` là một cover ở `_pos` 0 khi cả hai `display_order` đều null.
- R1: lần chạy thứ hai của `mediaddlpy` và của `amenddlpy` không thêm cạnh và không đổi schema. Log cell in danh sách tạo rỗng.
- R2:

```sql
SELECT trg_tbl, collect_set(pl_name) AS owners, count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE is_active = 1
  AND trg_tbl IN ('slv_poi_media_info', 'gld_srv_poi_media_gallery', 'gld_srv_poi_amenity')
GROUP BY trg_tbl
```

Kỳ vọng: `slv_poi_media_info` một owner `PL_VV_TRANS_SLV_TO_GLD_30P` và `n = 3`; gallery một owner cùng pipeline và `n = 1`; `gld_srv_poi_amenity` một owner `PL_VV_TRANS_SLV_TO_GLD_1H` và `n = 1`.

- R3: `DESCRIBE HISTORY` của ba bảng đích. Version của lần RUN thứ hai có `numTargetRowsInserted = 0` và `numTargetRowsUpdated = 0`, hoặc không có version mới.
- R4. Rule A8: mỗi `poi_id` còn sống có đúng một cover.

```sql
SELECT poi_id
FROM lh_vv_silver.dbo.slv_poi_media_info
WHERE deleted_at IS NULL
GROUP BY poi_id
HAVING sum(CAST(is_cover AS INT)) <> 1
```

Kỳ vọng 0 dòng.

- R5. So cột nghiệp vụ, cả hai chiều. Gallery với silver còn sống:

```sql
SELECT media_id, poi_id, source_name, photo_api_uri, display_order, width_px, height_px,
       photographer, blob_url, thumbnail_url, is_cover, is_active
FROM lh_vv_gold.dbo.gld_srv_poi_media_gallery WHERE deleted_at IS NULL
EXCEPT
SELECT media_id, poi_id, source_name, photo_api_uri, display_order, width_px, height_px,
       photographer, blob_url, thumbnail_url, is_cover, is_active
FROM lh_vv_silver.dbo.slv_poi_media_info WHERE deleted_at IS NULL
```

Chạy thêm chiều silver `EXCEPT` gallery. Amenity:

```sql
SELECT poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_vi, service_flags
FROM lh_vv_gold.dbo.gld_srv_poi_amenity WHERE deleted_at IS NULL
EXCEPT
SELECT poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_vi, service_flags
FROM lh_vv_silver.dbo.slv_poi_amenity WHERE deleted_at IS NULL
```

Chạy thêm chiều silver `EXCEPT` gold. Cả bốn câu kỳ vọng 0 dòng.

- R6: version `slv_poi_amenity` ghi ở baseline không tăng sau hai lần RUN `_1H`.
- R7: trong `exec_id` của RUN `_30P` đầu:

```sql
SELECT trg_tbl, status
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE exec_id = '<exec_id RUN 30P đầu>'
  AND trg_tbl IN ('gld_srv_poi_info', 'gld_srv_poi_multi_lang', 'slv_poi_media_info', 'gld_srv_poi_media_gallery')
```

`gld_srv_poi_info` và `gld_srv_poi_multi_lang` là `SUCCESS`. Hai bảng media mới cũng là `SUCCESS` hoặc `NO_DATA`.

- R8: `qg_json` của `slv_poi_media_info` trong cùng exec. Kỳ vọng `partner_url_dropped` lớn hơn hoặc bằng 1 và `poi_without_cover = 0`.

## Chạy lại để kiểm tra idempotency

Lần RUN thứ hai của từng `pl_name` là bước kiểm tra này. Không đổi dữ liệu nguồn giữa hai lần. R3 là tiêu chí đạt.

## Kiểm tra log và watermark

```sql
SELECT watermark_id, status, lock_exec_id
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN (
    'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P',
    'wm_flow__PL_VV_TRANS_SLV_TO_GLD_1H'
)
```

Sau khi notebook kết thúc, `lock_exec_id` là null. `status` của run thành công là `SUCCESS`.

Năm cạnh mới có dòng watermark `status = SUCCESS`:

- `wm_e__slv_poi_media_info__slv_3p_poi_media`
- `wm_e__slv_poi_media_info__slv_pn_business_service_i18ns`
- `wm_e__slv_poi_media_info__slv_pn_business_services`
- `wm_e__gld_srv_poi_media_gallery__slv_poi_media_info`
- `wm_e__gld_srv_poi_amenity__slv_poi_amenity`

`ctrl_log_run` của hai `exec_id` RUN đầu có `status` `SUCCESS`. `PARTIAL_FAILED` hoặc `FAILED` là không đạt.

## Rollback và forward recovery

Ưu tiên sửa rồi chạy lại. `RECOMPUTE` tính lại mọi dòng. `row_hash` đổi thì MERGE cập nhật tại chỗ. Không cần xóa bảng khi chỉ sai logic build.

Rollback chỉ khi phải gỡ ba bảng mới khỏi DEV. Chạy khi không có pipeline đang giữ khóa. Không dùng cell patch để sửa cạnh, vì cell đó không được `UPDATE` bảng config.

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
SET is_active = 0
WHERE is_active = 1
  AND trg_tbl IN ('slv_poi_media_info', 'gld_srv_poi_media_gallery', 'gld_srv_poi_amenity')
  AND pl_name IN ('PL_VV_TRANS_SLV_TO_GLD_30P', 'PL_VV_TRANS_SLV_TO_GLD_1H')
```

Sau đó, và chỉ sau đó:

```sql
DROP TABLE IF EXISTS lh_vv_gold.dbo.gld_srv_poi_media_gallery;
DROP TABLE IF EXISTS lh_vv_gold.dbo.gld_srv_poi_amenity;
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_poi_media_info;
```

Không đụng `slv_poi_amenity`, `gld_srv_poi_info`, `gld_srv_poi_multi_lang`. Trên git, hoàn tác đúng commit của task này.

Chạy lại sau rollback: sửa notebook, chạy lại từ bước 1 của mục các bước thực hiện.

## Kết quả người dùng ghi nhận

Ngày 2026-10-26, Fabric DEV. Không có URL.

- R1 đạt. `mediaddlpy` lần 1 tạo hai bảng và bốn cạnh `_30P`. Lần 2: `tạo []`, cùng bốn cạnh. `amenddlpy` lần 1 tạo `gld_srv_poi_amenity` và một cạnh `_1H`. Lần 2: `tạo []`, cùng một cạnh.
- Fixture đạt. `F1` đến `F11` đều `PASS`. `fixture_fail 0`.
- `_30P` PLAN `57a3c84f-cc03-48c0-817b-c6bdd8fdba24`: 3 node ứng viên, gallery phụ thuộc `slv_poi_media_info`. Có WARN nhịp vì hậu tố `_30P`.
- `_30P` RUN 1 `34636520-8ac5-4141-8050-09e8ed616a8d`: `slv_poi_media_info` SUCCESS, insert 1131, update 0, version 1. Gallery SUCCESS, insert 1131, update 0, version 1. Tiến 4 cạnh. Run `PARTIAL_FAILED` vì `gld_srv_poi_multi_lang` FAILED: `slv_enr_poi_info_multi_lang` rỗng. Người dùng bỏ qua lỗi này.
- `_30P` RUN 2 `add8d40c-a265-4d9b-9700-cb7856ce87a6`: không còn ứng viên media. Chỉ `gld_srv_poi_multi_lang` FAILED cùng lỗi. Tiến 0 cạnh. R3 của hai bảng media đạt vì không có lần ghi thứ hai.
- `_1H` PLAN `63ae76e6-2e4b-460f-a01d-ec797f163e5e`: một node `gld_srv_poi_amenity`. WARN nhịp vì nguồn thuộc `_ENR_15P`.
- `_1H` RUN 1 `b2f12a0c-c7cd-4ce1-b487-a4ab75f532e7`: SUCCESS, insert 58, update 0, version 1. Tiến 1 cạnh.
- `_1H` RUN 2 `81714db3-d6b9-4c8a-9c22-0775ec485cd7`: `NO_DATA`, 0 ứng viên. R3 của amenity đạt.
- R2 đạt theo log cell patch: đúng năm cạnh, một `pl_name` mỗi bảng đích.
- R4 đạt. Câu cover trả 0 dòng.
- R5 đạt. Bốn câu `EXCEPT` không có dòng.
- R6 đạt. `slv_poi_amenity` version mới nhất là 1, `2026-10-20T10:24:49Z`, `MERGE`, insert 58, update 0. Không có version ngày 2026-10-26.
- R7: `gld_srv_poi_info` không nằm trong exec vì không dirty. `gld_srv_poi_multi_lang` FAILED vì input bắt buộc rỗng. Người dùng xác nhận bỏ qua.
- R8 đạt. `rows 1131`. `partner_url_dropped 1`. `poi_without_cover 0`. `partner_media_unparsed 0`. `partner_fallback_docs 0`. Bốn block quality gate đều 0.
