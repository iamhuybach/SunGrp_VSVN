# GET /api/v1/pois/{poi_id}/practical_info

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Thông tin thực tế của một POI còn `apps.srv_poi_info.deleted_at` null. Không có dòng thì HTTP 404. Trường đa ngôn ngữ đọc `apps.srv_poi_multi_lang` theo ngôn ngữ đã resolve, rồi `vi` khi trường đó null. `holiday_exceptions` ghi nguyên text khi đó là đúng một giá trị JSON, còn JSON hỏng thì null. |
| Method | GET |
| Endpoint | /api/v1/pois/{poi_id}/practical_info |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | Accept-Language | string | không | Dùng khi không có query `lang`. Thiếu cả hai thì `vi`. |
| 2 | X-Request-Id | string | không | Ghi vào `meta.trace_id`. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | poi_id | string | có | path. `apps.srv_poi_info.poi_id`. |
| 2 | lang | string | không | query. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | `true` khi HTTP 200. |
| 2 | code | integer | có | envelope | Thành công là `200`. |
| 3 | message | string | có | envelope | `POI practical info retrieved successfully`. |
| 4 | data | object | có | envelope | |
| 5 | data.id | string | có | apps.srv_poi_info.poi_id | |
| 6 | data.name | string | có | apps.srv_poi_info.poi_name | |
| 7 | data.description | string | có | apps.srv_poi_multi_lang.description | |
| 8 | data.time_to_spend | object | có | apps.srv_poi_multi_lang.time_to_spend | Một key text thành `{label, value}`. Khác shape thì null. |
| 9 | data.cost | object | có | apps.srv_poi_multi_lang.cost_vnd | Cùng quy tắc `time_to_spend`. |
| 10 | data.best_time | object | có | apps.srv_poi_multi_lang.best_time | Cùng quy tắc `time_to_spend`. |
| 11 | data.cover | object | có | apps.srv_poi_media_gallery.media_id; apps.srv_poi_media_gallery.blob_url | Ảnh `is_cover` true, `is_active` true, `deleted_at` null. Không có thì null. |
| 12 | data.ratings | object | có | apps.srv_poi_info.source_name; apps.srv_poi_info.rating_overall; apps.srv_poi_info.rating_count | Luôn là object. |
| 13 | data.business_tags | object | có | apps.srv_poi_info.business_sector; apps.srv_poi_info.business_category | |
| 14 | data.status | object | có | apps.srv_poi_info.operating_status; apps.srv_poi_info.is_verified; apps.srv_poi_info.is_recommended; apps.srv_poi_info.is_bookable | |
| 15 | data.operating_hours | object | có | apps.srv_poi_info.operating_hours | `{value: [...]}` hoặc null khi cột null. |
| 16 | data.holiday_exceptions | json | có | apps.srv_poi_info.holiday_exceptions | Đúng một giá trị JSON thì ghi nguyên text cột. JSON hỏng hoặc có token thừa thì null. Không đổi khóa bên trong. |
| 17 | data.address | object | có | apps.srv_poi_info.full_address; apps.srv_poi_info.city; apps.srv_poi_info.district | |
| 18 | data.geo_location | object | có | apps.srv_poi_info.lat; apps.srv_poi_info.lng | |
| 19 | data.destinations | object | có | apps.srv_poi_info.destination_id; apps.srv_poi_info.destination_name | Luôn `{id, name}`. |
| 20 | data.phone | string | có | apps.srv_poi_info.phone | Không ghi log. |
| 21 | data.email | string | có | apps.srv_poi_info.email | Không ghi log. |
| 22 | data.website_url | string | có | apps.srv_poi_info.website_url | Không ghi log. |
| 23 | meta | object | có | envelope | Không có `meta.pagination`. |
| 24 | meta.timestamp | string | có | envelope | |
| 25 | meta.trace_id | string | có | envelope | |
| 26 | errors | array | có | envelope | Null khi thành công. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| 200 | null | POI còn hiệu lực. |
| 404 | POI_NOT_FOUND | Không có `apps.srv_poi_info.poi_id` với `deleted_at` null. |
| 500 | INTERNAL_SERVER_ERROR | Lỗi không phân loại. JSON hỏng ở một trường chỉ làm trường đó null hoặc mảng rỗng. |

## Sample request

```http
GET /api/v1/pois/14b2e2c4-95a8-d851-240f-c25e4e8cdb7a/practical_info?lang=vi HTTP/1.1
X-Request-Id: 22222222-2222-2222-2222-222222222222
```

## Sample response

Lấy từ Dev ngày 2026-11-11. `phone` và `email` có giá trị trên Dev và được để `null` trong file này.

```json
{
  "success": true,
  "code": 200,
  "message": "POI practical info retrieved successfully",
  "data": {
    "id": "14b2e2c4-95a8-d851-240f-c25e4e8cdb7a",
    "name": "French Village Ba Na Hills Viewpoint",
    "description": "French Village Ba Na Hills Viewpoint là điểm ngắm cảnh lý tưởng với kiến trúc châu Âu cổ kính mang đến trải nghiệm như lạc bước giữa lòng nước Pháp trên đỉnh núi Bà Nà",
    "time_to_spend": null,
    "cost": null,
    "best_time": null,
    "cover": {
      "id": "743d1739d195cf9a6bb428dd1c411a3cac900b958bed055bdc713f8dfe2c990e",
      "file_key": "partner_biz_service/2026/07/30/f4266e87-804a-43bd-8941-6eb6cb4aff9e_PsqwmsyU9R_38ada1a2-784c-49a0-b83f-0e8cc69f556f_datacollector_media_ChIJl-l3UgD3QTEREh-UpumcwQA_Ab43msK6J9g96mYK03fP.jpg"
    },
    "ratings": {
      "source": "partner",
      "ratings_count": null,
      "ratings_avg_score": null
    },
    "business_tags": {
      "business_sector": "attraction",
      "business_category": null
    },
    "status": {
      "operating_status": "",
      "is_verified": null,
      "is_recommended": true,
      "is_bookable": null
    },
    "operating_hours": {
      "value": [
        {
          "day_of_week": 1,
          "open_time": "08:00",
          "close_time": "22:00",
          "is_open_all_day": false,
          "is_closed": false
        },
        {
          "day_of_week": 2,
          "open_time": "08:00",
          "close_time": "22:00",
          "is_open_all_day": false,
          "is_closed": false
        },
        {
          "day_of_week": 3,
          "open_time": "08:00",
          "close_time": "22:00",
          "is_open_all_day": false,
          "is_closed": false
        },
        {
          "day_of_week": 4,
          "open_time": "08:00",
          "close_time": "22:00",
          "is_open_all_day": false,
          "is_closed": false
        },
        {
          "day_of_week": 5,
          "open_time": "08:00",
          "close_time": "22:00",
          "is_open_all_day": false,
          "is_closed": false
        },
        {
          "day_of_week": 6,
          "open_time": "08:00",
          "close_time": "22:00",
          "is_open_all_day": false,
          "is_closed": false
        },
        {
          "day_of_week": 7,
          "open_time": "08:00",
          "close_time": "22:00",
          "is_open_all_day": false,
          "is_closed": false
        }
      ]
    },
    "holiday_exceptions": [
      {
        "date": "30/07/2026",
        "hours": [
          {
            "open_time": "08:00",
            "close_time": "12:00"
          }
        ],
        "title": "Quốc Khánh",
        "status": true
      }
    ],
    "address": {
      "full_address": "00, Hòa Ninh, Xã Bà Nà, Thành phố Đà Nẵng",
      "street": "Hòa Ninh",
      "ward": "Xã Bà Nà",
      "district": null,
      "city": "Thành phố Đà Nẵng",
      "country_code": null
    },
    "geo_location": null,
    "phone": null,
    "email": null,
    "website_url": "https://partner-portal.visitvietnam.asia/",
    "destinations": {
      "id": null,
      "name": null
    }
  },
  "meta": {
    "timestamp": "2026-11-11T06:59:23.581325900Z",
    "trace_id": "22222222-2222-2222-2222-222222222222"
  },
  "errors": null
}
```
