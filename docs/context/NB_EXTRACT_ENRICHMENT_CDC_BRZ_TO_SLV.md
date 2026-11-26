# NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV — Extract `brz_enrichment_result` → hai bảng `slv_enr_*`

> Cập nhật: 17/11/2026. Bản code: `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb`.
> Hàm dùng chung: `NB_LIB_EXTRACT_RAWDATA`. Nguồn là snapshot `DOC`.

## 1. Mô tả

Đọc `lh_vv_bronze.dbo.brz_enrichment_result`. `event_type = LANG` ghi `slv_enr_poi_info_multi_lang`. `event_type = DESTINATION` ghi `slv_enr_poi_destination`.

| | |
|---|---|
| Gọi bởi | Không có activity trong `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`. Chạy tay |
| Đọc | `data`, `event_id`, `poi_id`, `event_type`, `version`, `EventProcessedUtcTime`; ctrl config, registry, watermark, state |
| Ghi | Hai bảng silver (MERGE, không xoá), `ctrl_cdc_state`, `ctrl_cdc_reject`, log, watermark |
| Song song | `max_parallel = 2` |
| Chạy lại | MERGE chỉ khi bộ (`_src_version`, `_event_processed_at`, `_event_id`) lớn hơn nghiêm ngặt |
| Chạy chồng | Khoá `wm_transform_brz_enrichment_result` |

`cdc_ts_ms` của lib nhận `version`. `_raw_ingested_at` là `EventProcessedUtcTime`. `cdc_op` giữ `event_id`. Event cũ hơn bộ `(version, EventProcessedUtcTime, event_id)` không ghi đè. `event_id` rỗng bị reject. Cùng bộ đó mà payload khác thì notebook dừng.

## 2. Định tuyến

`presence` so `trim(event_type)` đúng bằng `LANG` hoặc `DESTINATION`. Không có nhánh `lit(True)`.

| trg_tbl | event_type |
|---|---|
| `slv_enr_poi_info_multi_lang` | `LANG` |
| `slv_enr_poi_destination` | `DESTINATION` |

## 3. Phân loại

Thứ tự: `poi_id` rỗng → `MISSING_ENTITY_KEY`; `event_type` khác hai giá trị trên → `OUT_OF_SCOPE`; `data` rỗng, hỏng hoặc không phải object → `INVALID_PAYLOAD`; `version` null hoặc `EventProcessedUtcTime` null → `MISSING_EVENT_ORDER`.

`state_key = row`. Mọi cột khoá đều được kiểm. `NULLABLE_KEYS` rỗng.

## 4. Cột đặc biệt

`strapi_document_id` chiếu vào `destination_id`, `id` chiếu vào `destination_portal_id`, `name` chiếu vào `destination_name`, bằng `from_json`, `transform`, `to_json`. Phần tử null giữ nguyên vị trí. Ba cột cùng độ dài và cùng thứ tự. `country_code` và `postal_code` không có trong registry; extract ghi NULL.

Ba dòng đã có trên `slv_enr_poi_info_multi_lang` tại probe P-1 được giữ. Cell `enrbrzpy` đổi schema tại chỗ, không tạo lại bảng.

## 5. Cổng trước ghi

Bảng đích phải đã có. Còn `cost_vnd` hoặc `street`, hoặc thiếu `country_code` / `postal_code`, thì `ConfigError` và yêu cầu chạy `enrbrzpy`. Registry đã có `destination_portal_id` mà bảng chưa có cột thì `ConfigError` và yêu cầu chạy `destportalpy`. Dry run cũng đi qua cổng này và không ghi.

`cast_null > 0` hoặc `other > 0` thì dừng, không MERGE bảng đó.
