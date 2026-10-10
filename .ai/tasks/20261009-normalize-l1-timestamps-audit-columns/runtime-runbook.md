# Hướng dẫn kiểm chứng runtime

Trạng thái: `CHỜ CHẠY`

## Phạm vi và môi trường

Fabric DEV. Lakehouse `lh_vv_ctrl`, `lh_vv_silver`. Không chạy trên production. Không `DROP` bảng. Không `VACUUM` bảng L1 và `ctrl_cfg_schema_registry` cho đến khi kết quả được chấp nhận.

## Điều kiện tiên quyết

- Đã deploy `NB_LIB_EXTRACT_RAWDATA`, rồi `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, `NB_CREATE_DDL`, `NB_SETUP_L1_TS_AUDIT`.
- Tạm `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` và lịch chạy 3P.
- Hai dòng watermark nguồn không ở `RUNNING`. `ctrl_log_run` gần nhất của mỗi nguồn đã kết thúc.

## Baseline trước khi chạy

Ghi `version` hiện tại của `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry` và từng bảng `slv_pn_*`, `slv_3p_poi_*` đang tồn tại:

```sql
DESCRIBE HISTORY <bảng> LIMIT 1
```

Chọn một khóa partner và một khóa 3P. Ghi `src_created_at` hoặc `created_at` cũ, `_ingested_at`, và `_crawled_at` nếu là 3P.

## Các bước thực hiện

1. Trong `NB_CREATE_DDL`, chỉ chạy hai cell seed registry: partner, rồi 3P. Không chạy cell DDL, pipeline config, watermark.
2. `NB_SETUP_L1_TS_AUDIT` với `p_apply = false`. Dừng nếu có bảng `FAILED`.
3. Chạy lại với `p_apply = true`. Mỗi bảng một commit `userMetadata = L1_TS_AUDIT_BACKFILL`.
4. Chạy mỗi notebook extract một lần `dry_run = true`, rồi một lần incremental thật.
5. Chạy lại đúng lần incremental đó thêm một lần. So `created_at` của khóa đã chọn với lần trước: phải giống nhau. `updated_at` được phép đổi.
6. Một bảng partner nhỏ: `full_reload = true`, `table_filter` đúng bảng đó. `created_at` của khóa cũ vẫn giữ. `updated_at` đổi.

`slv_pn_business_locations` và `slv_pn_product_post_translations` chưa có bảng. Backfill ghi `MISSING`. Lần extract sau tạo bảng mới.

## Kiểm tra kết quả

- Exit JSON của backfill: không có `FAILED`.
- Mọi cột instant và `created_at`, `updated_at` khác null khớp `yyyy-MM-dd'T'HH:mm:ss.SSS'Z'`.
- `created_at` và `updated_at` không null. `created_at` không lớn hơn `updated_at` theo thứ tự chữ.
- Không còn cột `_ingested_at` trên bảng L1.
- `orders.src_created_at` là milli giây đã cắt về `.SSS`. Cột giây có đuôi `.000` khi nguồn không có phần lẻ.
- Giá trị `0` cũ thành null. Chuỗi ISO `1970-01-01T00:00:00Z` thành `1970-01-01T00:00:00.000Z`.
- `_crawled_at`, `_first_seen_at`, `_last_seen_at` vẫn là `timestamp`.
- `ingested_date` bronze không đổi. `slv_3p_poi_review.time` không đổi dạng.

## Chạy lại để kiểm tra idempotency

Backfill lần hai: bảng đã đúng schema ra `SKIPPED`, không thêm commit overwrite.

Extract incremental lần hai: `created_at` không đổi trên khóa đã có. Partner không áp dụng event cũ hơn `ctrl_cdc_state`. 3P không cập nhật khi `(_crawled_at, _event_id)` cũ hơn.

## Kiểm tra log và watermark

`ctrl_log_run` của hai nguồn sau cut-over là `SUCCESS` hoặc `NO_DATA`. `watermark` không nhỏ hơn giá trị baseline. Log có dòng self-check UTC. Không có `CastNullError` từ epoch `0`.

## Rollback và forward recovery

Chưa bật lại lịch:

- `RESTORE TABLE <fq> TO VERSION AS OF <version trước backfill>` cho từng bảng đã convert và cho registry.
- Deploy lại notebook cũ, lib trước.

Đã bật lịch và đã có MERGE mới: không lùi watermark. Tạm pipeline, `RESTORE` bảng và registry, deploy code cũ, chạy mỗi luồng một lần `full_reload = true` và `allow_full_scan = true`, rồi bật lịch.

Sửa tiến: `RESTORE` riêng bảng lỗi về version trước backfill, sửa notebook, chạy lại `NB_SETUP_L1_TS_AUDIT` với `p_tables` chỉ bảng đó.

## Kết quả người dùng ghi nhận

- Khóa partner trước / sau:
- Khóa 3P trước / sau:
- `created_at` sau lần MERGE thứ hai:
- Version backfill:
- Kết luận: `PASS` hoặc `FAIL`
