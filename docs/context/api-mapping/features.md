# GET /api/v1/pois/features

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Danh sách POI nổi bật theo số lượng BE yêu cầu, xếp theo quy tắc xoay vòng nhóm (xử lý logic fallback cho section Điểm đến nổi bật). |
| Method | GET |
| Endpoint | /api/v1/pois/features |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | Authorization | string | có | Bearer token service-to-service của BE |
| 2 | Accept-Language | string | không | Dùng khi query `lang` trống. Cả hai trống thì `vi`. |
| 3 | X-Request-Id | string | không | Mã định danh request |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | lang | string | không | query. Ưu tiên hơn `Accept-Language`. Rỗng thì fallback `vi`. Bản dịch lấy `apps.srv_poi_multi_lang` theo lang đó, thiếu thì fallback `vi`. |
| 2 | page | integer | không | query. Mặc định `0`. `@Min(0)` |
| 3 | size | integer | không | query. Mặc định `10`. `@Min(1)` `@Max(100)` |
| 4 | business_sector_priority | array | không | query. Thứ tự ưu tiên nhóm khi xoay vòng. Default: `attraction`, `f_n_b`, `event`, `tour_n_activities` |
| 5 | fallback_min_rating | number | không | Rating tối thiểu khi bù ngoài pool partner. Default: `4.5` |
| 6 | fallback_min_review_count | integer | không | Số đánh giá tối thiểu khi bù ngoài pool partner. Default: `100` |
| 7 | rating_source | string | không | Nguồn review |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | code | integer | có | không có cột | `0` = success |
| 2 | message | string | có | không có cột | `success` hoặc mô tả lỗi |
| 3 | data | array | có | không có cột | Theo thứ tự xoay vòng, tối đa limit phần tử |
| 4 | data[].id | string | có | `apps.srv_poi_info.poi_id` | ID của POI |
| 5 | data[].name | string | có | `apps.srv_poi_info.poi_name` | Tên POI |
| 6 | data[].description | string | không | `apps.srv_poi_multi_lang.description` | Mô tả ngắn (filter by lang) |
| 7 | data[].cover | object | có | không có cột | Object rỗng nếu POI chỉ có ảnh placeholder. Lấy từ `srv_poi_media_gallery` với `is_cover = true` |
| 8 | data[].cover.id | string | không | `apps.srv_poi_media_gallery.media_id` | Có khi `cover` khác null. Ưu tiên dòng `is_cover` = true, không thì phần tử đầu theo `display_order`. |
| 9 | data[].cover.file_key | string | không | `apps.srv_poi_media_gallery.blob_url`; `apps.srv_poi_media_gallery.photo_api_uri` | Có khi `cover` khác null. `blob_url` khi khác blank, còn lại `photo_api_uri`. |
| 10 | data[].ratings.source | string | có | `apps.srv_poi_info.source_name` | Nguồn đánh giá |
| 11 | data[].ratings.ratings_count | integer | có | `apps.srv_poi_info.rating_count` | Số đánh giá của nguồn đó |
| 12 | data[].ratings.ratings_avg_score | number | có | `apps.srv_poi_info.rating_overall` | Điểm đánh giá trung bình |
| 13 | data[].business_tags | object | có | không có cột |  |
| 14 | data[].business_tags.business_sector | string | có | `apps.srv_poi_info.business_sector` | Nhóm ngành kinh doanh |
| 15 | data[].business_tags.business_category | string | có | `apps.srv_poi_info.business_category` | Danh mục kinh doanh |
| 16 | data[].business_tags.subcategory_tags | array | không | `apps.srv_poi_info.subcategory_tags` | Các tag danh mục con |
| 17 | data[].status | object | có | không có cột |  |
| 18 | data[].status.operating_status | string | có | `apps.srv_poi_info.operating_status` | `operating` / `temporarily_closed` / `permanently_closed` |
| 19 | data[].status.is_verified | boolean | có | `apps.srv_poi_info.is_verified` |  |
| 20 | data[].status.is_recommended | boolean | có | `apps.srv_poi_info.is_recommended` |  |
| 21 | data[].status.is_bookable | boolean | có | `apps.srv_poi_info.is_bookable` |  |
| 22 | data[].operating_hours | array | không | `apps.srv_poi_info.operating_hours` | Giờ mở cửa cả tuần. Không có thì BE coi POI luôn hoạt động |
| 23 | data[].operating_hours.day_of_week | integer | có | `apps.srv_poi_info.operating_hours.day_of_week` | 1 = Thứ Hai … 7 = Chủ Nhật |
| 24 | data[].operating_hours.open_time | string | không | `apps.srv_poi_info.operating_hours.open_time` | HH:mm |
| 25 | data[].operating_hours.close_time | string | không | `apps.srv_poi_info.operating_hours.close_time` | HH:mm |
| 26 | data[].operating_hours.is_open_all_day | boolean | có | `apps.srv_poi_info.operating_hours.is_open_all_day` | Mở cả ngày |
| 27 | data[].operating_hours.is_closed | boolean | có | `apps.srv_poi_info.operating_hours.is_closed` | Đóng cửa |
| 28 | data[].address | object | không | không có cột |  |
| 29 | data[].address.full_address | string | không | `apps.srv_poi_info.full_address` |  |
| 30 | data[].address.street | string | không | `apps.srv_poi_info.street` |  |
| 31 | data[].address.ward | string | không | `apps.srv_poi_info.ward` |  |
| 32 | data[].address.district | string | không | `apps.srv_poi_info.district` |  |
| 33 | data[].address.city | string | không | `apps.srv_poi_info.city` |  |
| 34 | data[].address.country_code | string | có | `apps.srv_poi_info.country_code` |  |
| 35 | data[].geo_location | object | không | không có cột |  |
| 36 | data[].geo_location.latitude | number | có | `apps.srv_poi_info.lat` |  |
| 37 | data[].geo_location.longitude | number | có | `apps.srv_poi_info.lng` |  |
| 38 | meta | object | có | envelope |  |
| 39 | meta.timestamp | integer | có | envelope | Unix timestamp. Spec nguồn gọi `server_time`. |
| 40 | meta.trace_id | string | có | envelope | Từ `X-Request-Id`. Spec nguồn gọi `request_id`. |
| 41 | meta.pagination | object | không | envelope |  |
| 42 | meta.pagination.total_items | integer | không | envelope | Spec nguồn gọi `count`. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| không có | không có | không có trong file nguồn |

## Sample request

```json
{
  "limit": 10,
  "business_sector_priority": ["attraction", "f_n_b", "event", "tour_n_activities"],
  "fallback_min_rating": 4.5,
  "fallback_min_review_count": 100,
  "rating_source": "google"
}
```

## Sample response

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": "c5d6e7f8-0a1b-4c2d-9e3f-4a5b6c7d8e9f",
      "name": "Vịnh Hạ Long",
      "description": "Di sản thiên nhiên thế giới với hàng nghìn đảo đá vôi.",
      "cover": {
        "id": 918301,
        "file_key": "pois/c5d6e7f8-0a1b-4c2d-9e3f-4a5b6c7d8e9f/media/918301.jpg"
      },
      "ratings": [
        {
          "source": "google",
          "ratings_count": 21480,
          "ratings_avg_score": 4.8
        }
      ],
      "business_tags": {
        "business_sector": "attraction",
        "business_category": "bay",
        "subcategory_tags": [
          "nature",
          "cruise"
        ]
      },
      "status": {
        "operating_status": "operating",
        "is_verified": true,
        "is_recommended": true,
        "is_bookable": true
      },
      "operating_hours": [
        {
          "day_of_week": 1,
          "is_open_all_day": true,
          "is_closed": false
        },
        {
          "day_of_week": 2,
          "is_open_all_day": true,
          "is_closed": false
        },
        {
          "day_of_week": 3,
          "is_open_all_day": true,
          "is_closed": false
        },
        {
          "day_of_week": 4,
          "is_open_all_day": true,
          "is_closed": false
        },
        {
          "day_of_week": 5,
          "is_open_all_day": true,
          "is_closed": false
        },
        {
          "day_of_week": 6,
          "is_open_all_day": true,
          "is_closed": false
        },
        {
          "day_of_week": 7,
          "is_open_all_day": true,
          "is_closed": false
        }
      ],
      "address": {
        "full_address": "Phường Hạ Long, Quảng Ninh",
        "street": "",
        "ward": "Phường Hạ Long",
        "district": "",
        "city": "Quảng Ninh",
        "country_code": "VN"
      },
      "geo_location": {
        "latitude": 20.9101,
        "longitude": 107.1839
      }
    }
  ],
  "meta": {
    "timestamp": 1791947160,
    "trace_id": "9f1c1e2a-7a1b-4e34-9b7f-0a9d3b2c1d45",
    "pagination": {
      "total_items": 3
    }
  }
}
```
