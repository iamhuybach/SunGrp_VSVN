# GET /api/v1/pois/{poi_id}/summary

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Chi tiết một POI cho phần header của màn POI detail (hiển thị metadata khi người dùng mở POI Detail). |
| Method | GET |
| Endpoint | /api/v1/pois/{poi_id}/summary |
| Trạng thái | (ood) |
| Thay bằng | /api/v1/pois/{poi_id}/practical_info |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | Authorization | string | có | Bearer token service-to-service của BE |
| 2 | Accept-Language | string | không | Dùng khi query `lang` trống. Cả hai trống thì `vi`. |
| 3 | X-Request-Id | string | không | Mã định danh request |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | poi_id | string | có | path. ID của POI cần lấy thông tin tóm tắt |
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
| 7 | data.cover | object | không | không có cột | Object rỗng nếu POI chỉ có ảnh placeholder. Lấy từ `srv_poi_media_gallery` với `is_cover = true` |
| 8 | data.cover.id | integer | có | `apps.srv_poi_media_gallery.media_id` | ID media |
| 9 | data.cover.file_key | string | có | `apps.srv_poi_media_gallery.blob_url` | Khóa file để BE resolve URL |
| 10 | data.ratings.source | string | có | `apps.srv_poi_info.source_name` | Nguồn đánh giá |
| 11 | data.ratings.ratings_count | integer | có | `apps.srv_poi_info.rating_count` | Số đánh giá của nguồn đó |
| 12 | data.ratings.ratings_avg_score | number | có | `apps.srv_poi_info.rating_overall` | Điểm đánh giá |
| 13 | data.business_tags | object | có | không có cột |  |
| 14 | data.business_tags.business_sector | string | có | `apps.srv_poi_info.business_sector` | Enum chuẩn từ `ref_business_category` |
| 15 | data.business_tags.business_category | string | có | `apps.srv_poi_info.business_category` |  |
| 16 | data.status | object | có | không có cột |  |
| 17 | data.status.operating_status | string | có | `apps.srv_poi_info.operating_status` | `operating` / `temporarily_closed` / `permanently_closed` |
| 18 | data.status.is_verified | boolean | có | `apps.srv_poi_info.is_verified` |  |
| 19 | data.status.is_recommended | boolean | có | `apps.srv_poi_info.is_recommended` |  |
| 20 | data.status.is_bookable | boolean | có | `apps.srv_poi_info.is_bookable` |  |
| 21 | data.operating_hours | array | không | `apps.srv_poi_info.operating_hours` | Lịch mở cửa tuần |
| 22 | data.operating_hours.day_of_week | integer | có | `apps.srv_poi_info.operating_hours.day_of_week` | 1 = Thứ Hai … 7 = Chủ Nhật |
| 23 | data.operating_hours.open_time | string | không | `apps.srv_poi_info.operating_hours.open_time` | HH:mm |
| 24 | data.operating_hours.close_time | string | không | `apps.srv_poi_info.operating_hours.close_time` | HH:mm |
| 25 | data.operating_hours.is_open_all_day | boolean | có | `apps.srv_poi_info.operating_hours.is_open_all_day` |  |
| 26 | data.operating_hours.is_closed | boolean | có | `apps.srv_poi_info.operating_hours.is_closed` |  |
| 27 | data.holiday_exceptions | array | không | `apps.srv_poi_info.holiday_exceptions` | Ngày nghỉ lễ hoặc ngoại lệ đối tác khai báo |
| 28 | data.holiday_exceptions.date | string | có | `apps.srv_poi_info.holiday_exceptions.date` | YYYY-MM-DD |
| 29 | data.holiday_exceptions.name | string | không | `apps.srv_poi_info.holiday_exceptions.title` | Tên ngày lễ |
| 30 | data.holiday_exceptions.open_time | string | không | `apps.srv_poi_info.holiday_exceptions.open_time` | HH:mm |
| 31 | data.holiday_exceptions.close_time | string | không | `apps.srv_poi_info.holiday_exceptions.close_time` | HH:mm |
| 32 | data.address | object | không | không có cột |  |
| 33 | data.address.full_address | string | không | `apps.srv_poi_info.full_address` |  |
| 34 | data.address.street | string | không | `apps.srv_poi_info.street` |  |
| 35 | data.address.ward | string | không | `apps.srv_poi_info.ward` |  |
| 36 | data.address.district | string | không | `apps.srv_poi_info.district` |  |
| 37 | data.address.city | string | không | `apps.srv_poi_info.city` |  |
| 38 | data.address.country_code | string | có | `apps.srv_poi_info.country_code` |  |
| 39 | data.geo_location | object | không | không có cột |  |
| 40 | data.geo_location.latitude | number | có | `apps.srv_poi_info.lat` |  |
| 41 | data.geo_location.longitude | number | có | `apps.srv_poi_info.lng` |  |
| 42 | data.phone | string | không | `apps.srv_poi_info.phone` | Không có thì app ẩn nút Liên hệ |
| 43 | data.email | string | không | `apps.srv_poi_info.email` |  |
| 44 | data.website_url | string | không | `apps.srv_poi_info.website_url` | `null` nếu chưa có |
| 45 | data.destinations.id | string | có | `apps.srv_poi_info.destination_id` | destination_id |
| 46 | meta | object | có | envelope |  |
| 47 | meta.timestamp | integer | có | envelope | Spec nguồn gọi `server_time`. |
| 48 | meta.trace_id | string | có | envelope | Từ `X-Request-Id`. Spec nguồn gọi `request_id`. |

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

không có trong file nguồn
