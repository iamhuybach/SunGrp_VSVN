# NB_EXTRACT_CMS_CDC_BRZ_TO_SLV — Extract `cms_raw_data` → `slv_cms_*`

> Cập nhật: 08/11/2026. Bản code: `notebooks/NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.ipynb`.
> Hàm dùng chung: `NB_LIB_EXTRACT_RAWDATA.md`. Tên có "CDC" để cùng mẫu notebook theo nguồn. Nguồn này là snapshot `DOC`.

## 1. Mô tả

Đọc `lh_vv_bronze.dbo.cms_raw_data` và ghi bốn bảng `lh_vv_silver.dbo.slv_cms_*`. Mỗi bảng chỉ nhận một `source_name`. Không đọc `type` hay `ingested_date`. Không có gold.

| | |
|---|---|
| Gọi bởi | Không có activity trong `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`. Chạy tay |
| Đọc | `raw_payload`, `event_id`, `source_name`, `crawled_at`; ctrl config, registry, watermark, state |
| Ghi | Bốn bảng silver (MERGE, không xoá), `ctrl_cdc_state`, `ctrl_cdc_reject`, log, watermark |
| Song song | 4 bảng active cùng priority 1 |
| Chạy lại | State theo khoá (`document_id`, `locale`). Watermark chỉ tiến khi mọi bảng SUCCESS hoặc NO_DATA |
| Chạy chồng | Khoá `wm_transform_cms_raw_data` |

## 2. Định tuyến

`TABLE_SOURCE` gắn bảng với `source_name`:

| trg_tbl | source_name |
|---|---|
| `slv_cms_blog` | `strapi_blog` |
| `slv_cms_destination` | `strapi_destination` |
| `slv_cms_news` | `strapi_news` |
| `slv_cms_promotion_article` | `strapi_ph_promotion_article` |

`presence` so `lower(trim(source_name))` với giá trị đó. Không có nhánh nhận mọi tài liệu. `source_name` ngoài `sources` là IGNORED `OUT_OF_SCOPE`.

## 3. Phân loại và reject

Thứ tự: `source_name` rỗng → `MISSING_ENTITY_KEY`; ngoài `sources` → `OUT_OF_SCOPE`; payload rỗng, hở, hỏng hoặc không phải object → `INVALID_PAYLOAD`; `crawled_at` cast NULL → `MISSING_EVENT_ORDER`.

Dòng reject có `src_tbl = cms_raw_data`, `src_db = source_name`, `entity_key = source_name|event_id`. `event_hash` là sha256 của JSON gồm `event_id`, `source_name`, `crawled_at`, payload. `source_payload` chỉ có `event_id`, `source_name`, `crawled_at`.

Phần tử thiếu `document_id` hoặc parse lỗi vẫn reject. `locale` null hoặc rỗng không reject.

## 4. Khoá và thứ tự

Khoá MERGE là `document_id` rồi `locale`. `ON` dùng `<=>` cho mọi cột khoá. `locale` null vẫn được ghi. `locale` rỗng giữ `''`.

`resolve_latest` chọn bản mới nhất theo `cms_updated_at` (NULL thấp nhất), rồi thời điểm crawl, rồi `event_id`. Guard MERGE dùng cùng thứ tự. State vẫn so theo thứ tự crawl của lib: event crawl cũ hơn bản đã áp dụng bị bỏ qua dù `updatedAt` mới hơn.

## 5. Cổng dry run

`cast_null_policy` mặc định `FAIL`. Dry run (`dry_run = True`, `allow_full_scan = True`) không ghi và không tiến watermark. Nếu log bảng `slv_cms_blog` có `cast_null > 0`, dừng trước lần chạy thật, chạy probe P4, rồi mới chọn U6.

## 6. Truy vấn reject

```sql
SELECT trg_tbl, reject_reason, COUNT(*) AS so_dong
FROM lh_vv_ctrl.dbo.ctrl_cdc_reject
WHERE src_tbl = 'cms_raw_data' AND NOT is_resolved
GROUP BY trg_tbl, reject_reason
ORDER BY so_dong DESC;
```
