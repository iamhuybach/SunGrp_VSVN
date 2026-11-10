# GET /api/v1/pois/{poi_id}/practical_info

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Một POI: header detail và thông tin cần biết. Thay `summary`, `general-information` và `must-know`. |
| Method | GET |
| Endpoint | /api/v1/pois/{poi_id}/practical_info |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | Authorization | string | có | Bearer token service-to-service của BE |
| 2 | Accept-Language | string | không | Dùng khi query `lang` trống. Cả hai trống thì `vi`. |
| 3 | X-Request-Id | string | không | Mã định danh request |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | poi_id | string | có | path. ID của POI |
| 2 | lang | string | không | query. Ưu tiên hơn `Accept-Language`. Rỗng thì fallback `vi`. Bản dịch lấy `apps.srv_poi_multi_lang` theo lang đó, thiếu thì fallback `vi`. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | code | integer | có | không có cột | `0` = success |
| 2 | message | string | có | không có cột | `success` hoặc mô tả lỗi |
| 3 | data | object | có | không có cột | Object thông tin POI |
| 4 | data.id | string | có | `apps.srv_poi_info.poi_id` | poi_id |
| 5 | data.name | string | có | `apps.srv_poi_info.poi_name` | Tên POI |
| 6 | data.description | string | không | `apps.srv_poi_multi_lang.description` | Mô tả ngắn (filter by lang) |
| 7 | data.business_sector | string | có | `apps.srv_poi_info.business_sector` | Quyết định bộ nhãn hiển thị |
| 8 | data.time_to_spend | object | không | `apps.srv_poi_multi_lang.time_to_spend` |  |
| 9 | data.cost | object | không | `apps.srv_poi_multi_lang.cost_vnd` | Cột `cost_vnd`. |
| 10 | data.best_time | object | không | `apps.srv_poi_multi_lang.best_time` |  |
| 11 | data.cover | object | không | không có cột | Object rỗng nếu POI chỉ có ảnh placeholder. Lấy từ `srv_poi_media_gallery` với `is_cover = true` |
| 12 | data.cover.id | integer | có | `apps.srv_poi_media_gallery.media_id` | ID media |
| 13 | data.cover.file_key | string | có | `apps.srv_poi_media_gallery.blob_url` | Khóa file để BE resolve URL |
| 14 | data.ratings.source | string | có | `apps.srv_poi_info.source_name` | Nguồn đánh giá |
| 15 | data.ratings.ratings_count | integer | có | `apps.srv_poi_info.rating_count` | Số đánh giá của nguồn đó |
| 16 | data.ratings.ratings_avg_score | number | có | `apps.srv_poi_info.rating_overall` | Điểm đánh giá |
| 17 | data.business_tags | object | có | không có cột |  |
| 18 | data.business_tags.business_sector | string | có | `apps.srv_poi_info.business_sector` | Enum chuẩn từ `ref_business_category` |
| 19 | data.business_tags.business_category | string | có | `apps.srv_poi_info.business_category` |  |
| 20 | data.status | object | có | không có cột |  |
| 21 | data.status.operating_status | string | có | `apps.srv_poi_info.operating_status` | `operating` / `temporarily_closed` / `permanently_closed` |
| 22 | data.status.is_verified | boolean | có | `apps.srv_poi_info.is_verified` |  |
| 23 | data.status.is_recommended | boolean | có | `apps.srv_poi_info.is_recommended` |  |
| 24 | data.status.is_bookable | boolean | có | `apps.srv_poi_info.is_bookable` |  |
| 25 | data.operating_hours | object | không | `apps.srv_poi_info.operating_hours` |  |
| 26 | data.operating_hours.value.day_of_week | integer | có | `apps.srv_poi_info.operating_hours.day_of_week` | 1 = Thứ Hai … 7 = Chủ Nhật |
| 27 | data.operating_hours.value.open_time | string | không | `apps.srv_poi_info.operating_hours.open_time` | HH:mm |
| 28 | data.operating_hours.value.close_time | string | không | `apps.srv_poi_info.operating_hours.close_time` | HH:mm |
| 29 | data.operating_hours.value.is_open_all_day | boolean | có | `apps.srv_poi_info.operating_hours.is_open_all_day` |  |
| 30 | data.operating_hours.value.is_closed | boolean | có | `apps.srv_poi_info.operating_hours.is_closed` |  |
| 31 | data.holiday_exceptions | array | không | `apps.srv_poi_info.holiday_exceptions` | Ngày nghỉ lễ hoặc ngoại lệ đối tác khai báo |
| 32 | data.holiday_exceptions.date | string | có | `apps.srv_poi_info.holiday_exceptions.date` | YYYY-MM-DD |
| 33 | data.holiday_exceptions.name | string | không | `apps.srv_poi_info.holiday_exceptions.title` | Tên ngày lễ |
| 34 | data.holiday_exceptions.value | string | có | `apps.srv_poi_info.holiday_exceptions.value` | Giờ mở cửa dạng hiển thị hoặc "Đóng cửa" |
| 35 | data.holiday_exceptions.open_time | string | không | `apps.srv_poi_info.holiday_exceptions.open_time` | HH:mm |
| 36 | data.holiday_exceptions.close_time | string | không | `apps.srv_poi_info.holiday_exceptions.close_time` | HH:mm |
| 37 | data.holiday_exceptions.is_open_all_day | boolean | có | `apps.srv_poi_info.holiday_exceptions.is_open_all_day` |  |
| 38 | data.holiday_exceptions.is_closed | boolean | có | `apps.srv_poi_info.holiday_exceptions.is_closed` |  |
| 39 | data.address | object | không | không có cột |  |
| 40 | data.address.full_address | string | không | `apps.srv_poi_info.full_address` |  |
| 41 | data.address.street | string | không | `apps.srv_poi_info.street` |  |
| 42 | data.address.ward | string | không | `apps.srv_poi_info.ward` |  |
| 43 | data.address.district | string | không | `apps.srv_poi_info.district` |  |
| 44 | data.address.city | string | không | `apps.srv_poi_info.city` |  |
| 45 | data.address.country_code | string | có | `apps.srv_poi_info.country_code` |  |
| 46 | data.geo_location | object | không | không có cột |  |
| 47 | data.geo_location.latitude | number | có | `apps.srv_poi_info.lat` |  |
| 48 | data.geo_location.longitude | number | có | `apps.srv_poi_info.lng` |  |
| 49 | data.phone | string | không | `apps.srv_poi_info.phone` | Không có thì app ẩn nút Liên hệ |
| 50 | data.email | string | không | `apps.srv_poi_info.email` |  |
| 51 | data.website_url | string | không | `apps.srv_poi_info.website_url` | `null` nếu chưa có |
| 52 | data.destinations.id | string | có | `apps.srv_poi_info.destination_id` | destination_id |
| 53 | meta | object | có | envelope |  |
| 54 | meta.timestamp | integer | có | envelope | Spec nguồn gọi `server_time`. |
| 55 | meta.trace_id | string | có | envelope | Từ `X-Request-Id`. Spec nguồn gọi `request_id`. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| không có | không có | không có trong file nguồn |

## Sample request

```json
{
  "poi_id": "3f1a2b9c-5d6e-4f70-8a91-b2c3d4e5f601"
}
```

## Sample response

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "3f1a2b9c-5d6e-4f70-8a91-b2c3d4e5f601",
    "name": "Vịnh Hạ Long",
    "description": "Di sản thiên nhiên thế giới với hàng nghìn đảo đá vôi.",
    "business_sector": "attraction",
    "time_to_spend": { "label": "Thời gian tham quan", "value": "1 - 2 giờ" },
    "cost": { "label": "Chi phí tham khảo", "value": "120.000đ" },
    "best_time": { "label": "Mùa đẹp nhất", "value": "Tháng 10 - Tháng 4" },
    "cover": {
      "id": 918301,
      "file_key": "pois/c5d6e7f8-0a1b-4c2d-9e3f-4a5b6c7d8e9f/media/918301.jpg"
    },
    "ratings": { "source": "google", "ratings_count": 21480, "ratings_avg_score": 4.8 },
    "business_tags": {
      "business_sector": "attraction",
      "business_category": "bay"
    },
    "status": {
      "operating_status": "operating",
      "is_verified": true,
      "is_recommended": true,
      "is_bookable": true
    },
    "operating_hours": {
      "value": [
        { "day_of_week": 1, "open_time": "08:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false },
        { "day_of_week": 2, "open_time": "08:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false },
        { "day_of_week": 3, "open_time": "08:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false },
        { "day_of_week": 4, "open_time": "08:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false },
        { "day_of_week": 5, "open_time": "08:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false },
        { "day_of_week": 6, "open_time": "08:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false },
        { "day_of_week": 7, "is_open_all_day": false, "is_closed": true }
      ]
    },
    "holiday_exceptions": [
      { "date": "2026-11-20", "name": "Ngày Nhà giáo Việt Nam", "value": "09:00 - 15:00", "open_time": "09:00", "close_time": "15:00", "is_open_all_day": false, "is_closed": false },
      { "date": "2027-02-06", "name": "Mùng 1 Tết Nguyên Đán", "value": "Đóng cửa", "is_open_all_day": false, "is_closed": true }
    ],
    "address": {
      "full_address": "Phường Hạ Long, Quảng Ninh",
      "street": "",
      "ward": "Phường Hạ Long",
      "district": "",
      "city": "Quảng Ninh",
      "country_code": "VN"
    },
    "geo_location": { "latitude": 20.9101, "longitude": 107.1839 },
    "phone": null,
    "email": null,
    "website_url": null
  },
  "meta": {
    "timestamp": 1791947160,
    "trace_id": "9f1c1e2a-7a1b-4e34-9b7f-0a9d3b2c1d45"
  }
}
```
