
# Mapping GLD Service POI

## 1. Table: `gld_srv_poi_info`

Lakehouse.schema: `lh_vv_gold.dbo`.

### 1.1. Xử lý

- `slv_poi_entity_non_enrich ent` LEFT JOIN `slv_enr_poi_destination des` qua `ent.poi_id = des.poi_id`.
- `source_name` lấy từ `ent.source_name`. `des` không có cột này.
- `poi_id` với `ent.source_name = 'partner'` lấy full.
- Những `poi_id` với `ent.source_name = 'google'` chỉ lấy khi `poi_id` có cả trong cả 2 bảng `slv_enr_poi_destination` và `slv_enr_poi_info_multi_lang`.
- Thêm `destination_id`, `country_code`, `postal_code`, `lat`, `lng` vào `slv_enr_poi_destination`. Gold vẫn lấy 1-1 từ các cột đó.
- Grain một dòng `poi_id`. MERGE theo `poi_id`.
- `des` trùng `poi_id`: ưu tiên bản ghi đến sau (`updated_at` lớn hơn).
- `pl_name`: `PL_VV_TRANS_SLV_TO_GLD_30P`. Không gắn `PL_VV_TRANS_SLV_TO_ENR_15P`.

### 1.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| slv_poi_entity_non_enrich.poi_id | string | transform 1-1 | poi_id |
| slv_poi_entity_non_enrich.poi_name | string | transform 1-1 | poi_name |
| slv_poi_entity_non_enrich.source_name | string | transform 1-1 | source_name |
| slv_poi_entity_non_enrich.business_sector | string | transform 1-1 | business_sector |
| slv_poi_entity_non_enrich.business_category | string | transform 1-1 | business_category |
| slv_poi_entity_non_enrich.types_json | string | transform 1-1 | subcategory_tags |
| slv_enr_poi_destination.destination_id | string | transform 1-1 | destination_id |
| slv_enr_poi_destination.full_address | string | transform 1-1 | full_address |
| slv_enr_poi_destination.street | string | transform 1-1 | street |
| slv_enr_poi_destination.ward | string | transform 1-1 | ward |
| slv_enr_poi_destination.district | string | transform 1-1 | district |
| slv_enr_poi_destination.city | string | transform 1-1 | city |
| slv_enr_poi_destination.country_code | string | transform 1-1 | country_code |
| slv_enr_poi_destination.postal_code | string | transform 1-1 | postal_code |
| slv_enr_poi_destination.lat | Double | transform 1-1 | lat |
| slv_enr_poi_destination.lng | Double | transform 1-1 | lng |
| slv_poi_entity_non_enrich.phone | string | transform 1-1 | phone |
| slv_poi_entity_non_enrich.email | string | transform 1-1 | email |
| slv_poi_entity_non_enrich.website_url | string | transform 1-1 | website_url |
| slv_poi_entity_non_enrich.operating_status | string | transform 1-1 | operating_status |
| is_verified | boolean | null | is_verified |
| is_recommended | boolean | true khi source_name = 'partner', nguồn khác false | is_recommended |
| is_bookable | boolean | null | is_bookable |
| slv_poi_entity_non_enrich.opening_hours_text | string | Google theo mục 1.3; partner theo mục 1.5 | operating_hours |
| slv_poi_entity_non_enrich.holiday_exceptions | string | transform 1-1 | holiday_exceptions |
| | timestamp | field hệ thống | created_at |
| | timestamp | field hệ thống | updated_at |

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

Chuỗi này là object JSON, cùng path `$.policies.operating_hours` đã ghi vào entity. Probe `partner_hours_shape` (2026-10-24): 36 giá trị không null, toàn object. 33 object có bảy key `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday`; mỗi key có `status` boolean và `hours` là mảng `{open_time, close_time}` kiểu string. 3 object chỉ có bảy `status`, không có `hours`. Probe không trả giá trị `status`, không trả độ dài mảng, không trả dạng chuỗi giờ. Rule không đọc `status`.

JSON đích cùng dạng mục 1.4: bảy phần tử, thứ tự Thứ Hai → Chủ Nhật.

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
- Không có key ngày, không có `hours`, hoặc `hours` rỗng: cùng object ngày đóng của case 1. `is_closed = true`. `is_open_all_day = false`. `value` = `Đóng cửa`. Không ghi `open_time`, `close_time`.
- Nhiều hơn một phần tử `hours` trong một ngày: dừng, không chọn phần tử, không ghép chuỗi.

---
