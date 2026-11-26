Sau mỗi thay đổi nghiệp vụ của bảng trong file này, cùng task cập nhật file này trước review.

# Mapping GLD Service POI

## 1. Table: `gld_srv_poi_info`

Lakehouse.schema: `lh_vv_gold.dbo`.

### 1.1. Xử lý

- `SPEC.inputs`: `entity` = `slv_poi_entity_non_enrich`, `destination` = `slv_enr_poi_destination`, `multi_lang` = `slv_enr_poi_info_multi_lang`, `rating` = `slv_3p_poi_rating`, `review` = `slv_3p_poi_review`, `media` = `slv_poi_media_info`, `price` = `slv_3p_poi_price`. `required_inputs` = (`entity`,). `entity`, `destination`, `multi_lang` gọi `live_only=False`. `rating`, `review`, `media` và `price`: notebook không truyền `live_only` (chỉ dòng `deleted_at IS NULL`). `write_mode = MERGE`.
- `source_name` lấy từ `ent.source_name`. `DEST_COLS` không có `source_name`. Entity đã đổi bronze `sgm` thành `google` trước khi lọc, nên gold thấy các dòng đó là `google`.
- So khớp nguồn bằng `lower(trim(source_name))`. Dòng không phải `google` được giữ. Dòng `google` chỉ khi `poi_id` có trong cả `slv_enr_poi_destination` và `slv_enr_poi_info_multi_lang`.
- Sau lọc, LEFT JOIN `des` theo `poi_id`.
- D-SRV-22. `is_partner` = `coalesce(lower(trim(source_name)) = 'partner', false)`. Sau `_destination`, dòng destination còn lại gắn `_has_dest = true`. Không có dòng cùng `poi_id` khi `_has_dest` null sau LEFT JOIN. Dòng destination còn nhưng cột null vẫn `_has_dest` true, không thuộc nhánh này.
- Nhánh `is_partner` và `_has_dest` null: mỗi cột trong `DEST_COLS` trừ `poi_id` và `updated_at`, tên có trong `ENTITY_OUT_COLS` thì lấy `_e_<cột>` từ `slv_poi_entity_non_enrich` rồi cast về `des.dtypes`; tên không có thì null. Không đọc bảng khác. Không coalesce với destination.
- `ENTITY_OUT_COLS` là bản chép `OUT_COLS` của `NB_SLV_POI_ENTITY_NON_ENRICH`. `FROM_ENTITY` = tên `DEST_COLS[2:]` nằm trong `ENTITY_OUT_COLS`: `full_address`, `ward`, `city`, `lat`, `lng`. `street` không nằm trong `DEST_COLS`. Gold lấy `street` từ `slv_poi_entity_non_enrich.street` trên mọi dòng. Null trên nhánh partner chưa có destination: `destination_id`, `destination_name`, `district`, `country_code`, `postal_code`.
- Partner đã có dòng destination, Google, nguồn khác: `ward`, `district`, `city` lấy cột mới của `slv_enr_poi_destination`; null hoặc trim rỗng thì lấy `old_ward`, `old_district`, `old_city`. Cả hai trống thì null. Các cột destination còn lại vẫn 1-1. `operating_hours`, `holiday_exceptions`, `is_verified`, `is_recommended`, `is_bookable`, `rating_overall`, `rating_count`, `review_count`, `cover_id`, `cover_blob_url` không đổi.
- `destination_name` là chuỗi JSON của mảng `destinations.name`, kể cả phần tử null, cùng thứ tự. Extract `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` ghi cột này. Gold copy 1-1. Partner chưa có dòng destination thì null.
- Lý do nghiệp vụ trong notebook: MISSING.
- Kiểu literal của cột entity trong notebook gold: MISSING. Notebook cast về `des.dtypes` của cột destination.
- `NB_CREATE_DDL` cell `srvpoipy` thêm `destination_id`, `country_code`, `postal_code`, `lat`, `lng` vào `slv_enr_poi_destination`. Gold lấy 1-1 các cột đó.
- Grain một dòng `poi_id`. MERGE theo `poi_id`. `poi_id` nguồn `slv_poi_entity_non_enrich` là `STRING`; DDL không ghi `NOT NULL`. Target `gld_srv_poi_info.poi_id` là `STRING NOT NULL`. `quality_gate` chặn khóa NULL.
- `des` nhiều dòng cùng `poi_id`: giữ dòng `updated_at` lớn nhất khi max duy nhất và không có `updated_at` null. Có `updated_at` null hoặc nhiều dòng cùng max thì dừng, không chọn dòng.
- `pl_name` hiện hành: `PL_VV_TRANS_SLV_TO_GLD_30M` (`plcadpy` đổi từ `PL_VV_TRANS_SLV_TO_GLD_30P`). `load_mode = RECOMPUTE`, `priority = 1`. Cạnh: `slv_poi_entity_non_enrich`, `slv_enr_poi_destination`, `slv_enr_poi_info_multi_lang`, `slv_3p_poi_rating`, `slv_3p_poi_review`, `slv_poi_media_info`, `slv_3p_poi_price` → `gld_srv_poi_info`, `nb_name = NB_GLD_SRV_POI_INFO`. Không gắn `PL_VV_TRANS_SLV_TO_ENR_15M`.
- `cover_id`, `cover_blob_url` (D-01): LEFT JOIN dòng `slv_poi_media_info` có `is_cover = true` cùng `poi_id`, cùng dòng `gld_srv_poi_media_gallery` chiếu. `is_cover` do `with_cover` của `NB_SLV_POI_MEDIA_INFO` tính; notebook gold không tính lại. Mọi nguồn. Không có dòng cover thì cả hai null, vẫn giữ một dòng `poi_id`. Hơn một dòng cover cho một `poi_id` thì dừng, không chọn dòng. Metric `cover_matched`. Không thuộc `required_inputs`.
- `is_active` (D-1): `true` mọi dòng build trả. Dòng đã xoá mềm trước khi có cột (không còn trong build) giữ NULL. Lần chạy đầu sau khi thêm cột đổi `row_hash` mọi dòng sống (cập nhật toàn bộ một lần).
- `price_level`, `price_min`, `price_max`: LEFT JOIN 1-1 `slv_3p_poi_price` theo `poi_id`, mọi nguồn, không lọc `source_name`. Không có dòng thì null. Hơn một dòng cùng `poi_id` thì dừng, không chọn dòng. Giữ kiểu nguồn `int` và `decimal(18,2)`, có type guard. Metric `price_matched`. Không thuộc `required_inputs`.
- `old_address`, `price_level`, `price_min`, `price_max` chỉ ở gold. PostgreSQL và API không có các cột này, cùng `story` và `local_tips` của `gld_srv_poi_multi_lang`. Lần chạy đầu sau khi thêm cột đổi `row_hash` mọi dòng sống.

### 1.6 Grain và địa chỉ đã chốt — 20261116-enr-lang-destination-from-bronze

Người dùng chốt ngày 2026-11-16. §1.1 và §1.2 theo notebook sau task này.

- `slv_enr_poi_destination`: một dòng cho `poi_id`. MERGE theo `poi_id`. `version` không nằm trong khoá. Cùng khoá thì giữ `version` lớn hơn; bằng `version` thì giữ `EventProcessedUtcTime` lớn hơn.
- `gld_srv_poi_info.street` lấy từ `slv_poi_entity_non_enrich.street`.
- Có dòng destination: `ward` lấy `slv_enr_poi_destination.ward`, null hoặc trim rỗng thì `old_ward`. `district` lấy `district`, null hoặc trim rỗng thì `old_district`. `city` lấy `city`, null hoặc trim rỗng thì `old_city`.
- `gld_srv_poi_info.full_address` ghép bằng `, ` (phẩy và một dấu cách). Một field null, hoặc `house_number` hay `street` chỉ còn khoảng trắng sau trim, thì bỏ cả nhóm. Nhóm 1: `house_number` + `street` + `formatted_address`. Nhóm 2: `house_number` + `street` + `ward_with_type` + `city_with_type`. Nhóm 3: `slv_enr_poi_destination.full_address`. Ba nhóm chỉ áp khi có dòng destination. Không có dòng destination thì giữ `full_address` của `slv_poi_entity_non_enrich`.
- `gld_srv_poi_info.old_address` (D-OLD-ADDR): cùng luật bỏ nhóm. Có dòng destination: nhóm 1 `house_number` + `street` + `old_formatted_address`; nhóm 2 `house_number` + `street` + `old_ward_with_type` + `old_city_with_type`; nhóm 3 `slv_enr_poi_destination.full_address`. Không có dòng destination thì null, kể cả partner. Không lấy `full_address` của entity. Metric `old_address_g1`, `old_address_g2`, `old_address_g3`, `old_address_null`.

### 1.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| slv_poi_entity_non_enrich.poi_id | string | transform 1-1 | poi_id |
| slv_poi_entity_non_enrich.poi_name | string | transform 1-1 | poi_name |
| slv_poi_entity_non_enrich.source_name | string | transform 1-1 | source_name |
| slv_poi_entity_non_enrich.business_sector | string | transform 1-1 | business_sector |
| slv_poi_entity_non_enrich.business_category | string | transform 1-1 | business_category |
| slv_poi_entity_non_enrich.types_json | string | transform 1-1 | subcategory_tags |
| slv_enr_poi_destination.destination_id | string | partner chưa có dòng destination: null; còn lại transform 1-1 | destination_id |
| slv_enr_poi_destination.destination_name | string | partner chưa có dòng destination: null; còn lại chuỗi JSON mảng, cùng thứ tự, kể cả null | destination_name |
| slv_poi_entity_non_enrich.full_address khi không có dòng destination; khi có dòng destination: house_number + street + formatted_address, rồi house_number + street + ward_with_type + city_with_type, rồi slv_enr_poi_destination.full_address | string | Có dòng destination: coalesce ba nhóm, nối bằng `, `. Field null hoặc house_number/street chỉ còn khoảng trắng thì bỏ cả nhóm. Không có dòng destination: 1-1 từ entity. Không coalesce | full_address |
| house_number + street + old_formatted_address, rồi house_number + street + old_ward_with_type + old_city_with_type, rồi slv_enr_poi_destination.full_address; house_number và street từ slv_poi_entity_non_enrich | string | Chỉ gold (D-OLD-ADDR). Có dòng destination: coalesce ba nhóm, nối bằng `, `. Field null hoặc house_number/street chỉ còn khoảng trắng thì bỏ cả nhóm. Không có dòng destination: null, kể cả partner. Không lấy full_address của entity | old_address |
| slv_poi_entity_non_enrich.street | string | 1-1 trên mọi dòng. Không đọc slv_enr_poi_destination.street | street |
| slv_enr_poi_destination.ward, rồi old_ward; partner chưa có dòng destination: slv_poi_entity_non_enrich.ward | string | Có dòng destination: coalesce sau trim. Null hoặc trim rỗng thì old_ward. Partner chưa có dòng destination: 1-1 từ entity, cast des.dtypes | ward |
| slv_enr_poi_destination.district, rồi old_district | string | Có dòng destination: coalesce sau trim. Null hoặc trim rỗng thì old_district. Partner chưa có dòng destination: null | district |
| slv_enr_poi_destination.city, rồi old_city; partner chưa có dòng destination: slv_poi_entity_non_enrich.city | string | Có dòng destination: coalesce sau trim. Null hoặc trim rỗng thì old_city. Partner chưa có dòng destination: 1-1 từ entity, cast des.dtypes | city |
| slv_enr_poi_destination.country_code | string | partner chưa có dòng destination: null; còn lại transform 1-1 | country_code |
| slv_enr_poi_destination.postal_code | string | partner chưa có dòng destination: null; còn lại transform 1-1 | postal_code |
| slv_enr_poi_destination.lat; partner chưa có dòng destination: slv_poi_entity_non_enrich.lat | Double | partner chưa có dòng destination: 1-1 từ entity, cast des.dtypes; còn lại transform 1-1. Không coalesce | lat |
| slv_enr_poi_destination.lng; partner chưa có dòng destination: slv_poi_entity_non_enrich.lng | Double | partner chưa có dòng destination: 1-1 từ entity, cast des.dtypes; còn lại transform 1-1. Không coalesce | lng |
| slv_poi_entity_non_enrich.phone | string | transform 1-1 | phone |
| slv_poi_entity_non_enrich.email | string | transform 1-1 | email |
| slv_poi_entity_non_enrich.website_url | string | transform 1-1 | website_url |
| slv_poi_entity_non_enrich.operating_status | string | transform 1-1 | operating_status |
| is_verified | boolean | null | is_verified |
| is_recommended | boolean | true khi lower(trim(source_name)) = 'partner'; null hoặc nguồn khác thì false | is_recommended |
| is_bookable | boolean | null | is_bookable |
| | boolean | true: hằng cho mọi dòng NB_GLD_SRV_POI_INFO ghi; không đọc nguồn, không theo deleted_at (D-1) | is_active |
| slv_poi_entity_non_enrich.opening_hours_text | string | Google theo mục 1.3; partner theo mục 1.5 | operating_hours |
| slv_poi_entity_non_enrich.holiday_exceptions | string | transform 1-1 | holiday_exceptions |
| slv_3p_poi_rating.rating_overall | decimal(4,2) | transform 1-1 | rating_overall |
| slv_3p_poi_rating.rating_count | integer | transform 1-1 | rating_count |
| slv_3p_poi_review | integer | count review theo poi_id | review_count |
| slv_3p_poi_price.price_level | integer | Chỉ gold. LEFT JOIN theo poi_id, mọi nguồn; không có dòng thì null; hơn một dòng thì dừng | price_level |
| slv_3p_poi_price.price_min | decimal(18,2) | Chỉ gold. LEFT JOIN theo poi_id, mọi nguồn; không có dòng thì null; hơn một dòng thì dừng | price_min |
| slv_3p_poi_price.price_max | decimal(18,2) | Chỉ gold. LEFT JOIN theo poi_id, mọi nguồn; không có dòng thì null; hơn một dòng thì dừng | price_max |
| slv_poi_media_info.media_id | string | LEFT JOIN dòng is_cover = true cùng poi_id; không có dòng thì null | cover_id |
| slv_poi_media_info.blob_url | string | cùng dòng cover với cover_id, transform 1-1; không có dòng thì null | cover_blob_url |
| | timestamp | field hệ thống | created_at |
| | timestamp | field hệ thống | updated_at |

`rating_overall`, `rating_count`, `review_count`: `slv_3p_poi_rating` và `slv_3p_poi_review` LEFT JOIN qua `poi_id`, chỉ điền cho dòng `source_name` google (lower/trim). Dòng partner và dòng không khớp để NULL, vẫn giữ `poi_id`. `review_count` = `COUNT(*)` theo `poi_id`, kể cả `review_id` NULL; không coalesce 0. `slv_3p_poi_rating` có hơn một dòng cho một `poi_id` thì dừng, không chọn dòng. `rating_count`, `review_count` ngoài miền INT (`-2147483648` đến `2147483647`) thì dừng.

### 1.3. Operating Hours Transform

**Source Field:** `slv_poi_entity_non_enrich.opening_hours_text`

**Data Type:** `string`

**Target Field:** `operating_hours`

**Xử lý lại key-value với rule sau:**

Nguồn Google:

1. Nguồn `day_of_week`: 0 = Chủ Nhật, 1 = Thứ Hai, 2 = Thứ Ba, 3 = Thứ Tư, 4 = Thứ Năm, 5 = Thứ Sáu, 6 = Thứ Bảy. Số trên JSON đích: 0 thành 7, các số 1–6 giữ nguyên.

2. `label` theo đúng ngày đó. Số nguồn và số đích là cùng một ngày: 1 = Thứ Hai, 2 = Thứ Ba, 3 = Thứ Tư, 4 = Thứ Năm, 5 = Thứ Sáu, 6 = Thứ Bảy, 7 = Chủ Nhật.

3. `is_open_all_day`:
   - 3.1. `is_open_all_day = true` nếu `opening_hours_text` có dạng:
     ```json
     [{"open_hour":0,"open_minute":0,"day_of_week":0}]
     ```
   - 3.2. Còn lại là `is_open_all_day = false`.
   - 3.3. Dạng 3.1 ra đủ bảy ngày như case 2: `is_open_all_day = true`, `is_closed = false`, không ghi `open_time`, `close_time`, `value`.

4. `open_time = open_hour` và `open_minute` (sample: nếu `"open_hour": 7` và `"open_minute": 0` -> `07:00`).

5. `close_time = close_hour` và `close_minute` (sample: nếu `"close_hour": 7` và `"close_minute": 0` -> `07:00`).

6. `"is_closed": true` nếu `day_of_week` thiếu một ngày; ngược lại là `false`.

7. `value` = `open_time` + ` - ` + `close_time` khi ngày mở. Ngày đóng: `value` = `Đóng cửa`, không ghi `open_time` và `close_time`. Đúng case 1.

8. `opening_hours_text` null thì `operating_hours` null.

9. Nhiều phần tử cùng một số `day_of_week`: xử lý đầy đủ, không gom. Mỗi phần tử nguồn thành một object đích, theo thứ tự trong mảng. `day_of_week` và `label` lặp lại. Ví dụ value:

```json
[
  {"day_of_week": 1, "label": "Thứ Hai", "value": "08:00 - 12:00", "open_time": "08:00", "close_time": "12:00", "is_open_all_day": false, "is_closed": false},
  {"day_of_week": 1, "label": "Thứ Hai", "value": "13:00 - 17:00", "open_time": "13:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false}
]
```

Ngày không có phần tử nào vẫn là một object đóng cửa, như case 1.

`close_day` không đọc. Nhánh cả ngày chỉ khi đúng một phần tử bằng `{"open_hour": 0, "open_minute": 0, "day_of_week": 0}` và mọi value là int.

Dừng, không ghi `operating_hours`, khi: `GOOGLE_INVALID_JSON`, `GOOGLE_NOT_ARRAY`, `GOOGLE_BAD_ELEMENT`, `GOOGLE_BAD_DAY`, `GOOGLE_BAD_TIME`. `source_name` sau `strip().lower()` không phải `google` hay `partner` thì dừng `SOURCE_NOT_GOOGLE_PARTNER`.

### 1.4. Operating Hours Examples

#### Case 1

**Trước:**

```json
[
  {
    "close_hour": 17,
    "close_day": 0,
    "open_hour": 8,
    "close_minute": 0,
    "open_minute": 0,
    "day_of_week": 0
  },
  {
    "close_hour": 17,
    "close_day": 1,
    "open_hour": 8,
    "close_minute": 0,
    "open_minute": 0,
    "day_of_week": 1
  },
  {
    "close_hour": 17,
    "close_day": 2,
    "open_hour": 8,
    "close_minute": 0,
    "open_minute": 0,
    "day_of_week": 2
  },
  {
    "close_hour": 17,
    "close_day": 3,
    "open_hour": 8,
    "close_minute": 0,
    "open_minute": 0,
    "day_of_week": 3
  },
  {
    "close_hour": 17,
    "close_day": 5,
    "open_hour": 8,
    "close_minute": 0,
    "open_minute": 0,
    "day_of_week": 5
  },
  {
    "close_hour": 17,
    "close_day": 6,
    "open_hour": 8,
    "close_minute": 0,
    "open_minute": 0,
    "day_of_week": 6
  }
]
```

**Sau:**

```json
[
  {
    "day_of_week": 1,
    "label": "Thứ Hai",
    "value": "08:00 - 17:00",
    "open_time": "08:00",
    "close_time": "17:00",
    "is_open_all_day": false,
    "is_closed": false
  },
  {
    "day_of_week": 2,
    "label": "Thứ Ba",
    "value": "08:00 - 17:00",
    "open_time": "08:00",
    "close_time": "17:00",
    "is_open_all_day": false,
    "is_closed": false
  },
  {
    "day_of_week": 3,
    "label": "Thứ Tư",
    "value": "08:00 - 17:00",
    "open_time": "08:00",
    "close_time": "17:00",
    "is_open_all_day": false,
    "is_closed": false
  },
  {
    "day_of_week": 4,
    "label": "Thứ Năm",
    "value": "Đóng cửa",
    "is_open_all_day": false,
    "is_closed": true
  },
  {
    "day_of_week": 5,
    "label": "Thứ Sáu",
    "value": "08:00 - 17:00",
    "open_time": "08:00",
    "close_time": "17:00",
    "is_open_all_day": false,
    "is_closed": false
  },
  {
    "day_of_week": 6,
    "label": "Thứ Bảy",
    "value": "08:00 - 17:00",
    "open_time": "08:00",
    "close_time": "17:00",
    "is_open_all_day": false,
    "is_closed": false
  },
  {
    "day_of_week": 7,
    "label": "Chủ Nhật",
    "value": "08:00 - 17:00",
    "open_time": "08:00",
    "close_time": "17:00",
    "is_open_all_day": false,
    "is_closed": false
  }
]
```

#### Case 2

**Trước:**

```json
[
  {
    "open_hour": 0,
    "open_minute": 0,
    "day_of_week": 0
  }
]
```

**Sau:**

```json
[
  {
    "day_of_week": 1,
    "label": "Thứ Hai",
    "is_open_all_day": true,
    "is_closed": false
  },
  {
    "day_of_week": 2,
    "label": "Thứ Ba",
    "is_open_all_day": true,
    "is_closed": false
  },
  {
    "day_of_week": 3,
    "label": "Thứ Tư",
    "is_open_all_day": true,
    "is_closed": false
  },
  {
    "day_of_week": 4,
    "label": "Thứ Năm",
    "is_open_all_day": true,
    "is_closed": false
  },
  {
    "day_of_week": 5,
    "label": "Thứ Sáu",
    "is_open_all_day": true,
    "is_closed": false
  },
  {
    "day_of_week": 6,
    "label": "Thứ Bảy",
    "is_open_all_day": true,
    "is_closed": false
  },
  {
    "day_of_week": 7,
    "label": "Chủ Nhật",
    "is_open_all_day": true,
    "is_closed": false
  }
]
```

### 1.5. Operating Hours Transform — partner

**Source Field:** `slv_poi_entity_non_enrich.opening_hours_text`

Chuỗi này là object JSON, cùng path `$.policies.operating_hours` đã ghi vào entity. Probe `partner_hours_shape` (2026-10-24): 36 giá trị không null, toàn object. 33 object có bảy key `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday`; mỗi key có `status` boolean và `hours` là mảng `{open_time, close_time}` kiểu string. 3 object chỉ có bảy `status`, không có `hours`. Probe không trả giá trị `status`, không trả độ dài mảng, không trả dạng chuỗi giờ. Rule không đọc `status`. Probe `partner_multi_hours` (2026-11-04, task 20261104-poi-review-src-and-partner-i18n): 8 dòng có `hours` dài 2, không dòng nào dài hơn 2.

JSON đích cùng dạng mục 1.4, thứ tự Thứ Hai → Chủ Nhật. Mỗi ngày một phần tử. Ngày có hai phần tử `hours` ra hai phần tử liền nhau.

| Key nguồn | day_of_week | label |
|---|---|---|
| monday | 1 | Thứ Hai |
| tuesday | 2 | Thứ Ba |
| wednesday | 3 | Thứ Tư |
| thursday | 4 | Thứ Năm |
| friday | 5 | Thứ Sáu |
| saturday | 6 | Thứ Bảy |
| sunday | 7 | Chủ Nhật |

- `opening_hours_text` null thì `operating_hours` null.
- Đúng một phần tử `hours`: `open_time` và `close_time` lấy nguyên chuỗi nguồn, không tách giờ/phút. `value` = `open_time` + ` - ` + `close_time`. `is_closed = false`. `is_open_all_day = false`.
- Đúng hai phần tử `hours`: ra hai object cùng `day_of_week`, mỗi object theo rule một phần tử ở trên, giữ thứ tự mảng nguồn (`hours[0]` rồi `hours[1]`), không sắp theo giờ, không ghép chuỗi. Ví dụ `monday` `08:00`–`09:00` và `11:00`–`22:00` ra hai object Thứ Hai `08:00 - 09:00` rồi `11:00 - 22:00`. Một phần tử sai kiểu thì dừng `PARTNER_BAD_HOURS`.
- Không có key ngày, không có `hours`, hoặc `hours` rỗng: cùng object ngày đóng của case 1. `is_closed = true`. `is_open_all_day = false`. `value` = `Đóng cửa`. Không ghi `open_time`, `close_time`.
- Hơn hai phần tử `hours` trong một ngày: dừng `PARTNER_MULTI_HOURS`, không chọn phần tử, không ghép chuỗi.
- JSON không đọc được: `PARTNER_INVALID_JSON`. Không phải object: `PARTNER_NOT_OBJECT`. Ngày không phải object: `PARTNER_BAD_DAY`. `hours` không phải list, hoặc `open_time` / `close_time` không phải string: `PARTNER_BAD_HOURS`.

---
