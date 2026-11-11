# GET /api/v1/pois/features

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | POI nổi bật, phân trang. Vòng 1 lấy `apps.srv_poi_info.is_recommended` true. Vòng 2, khi vòng 1 chưa đủ trang, lấy `apps.srv_poi_info.rating_overall` và `apps.srv_poi_info.rating_count` đạt ngưỡng. Trong mỗi vòng, chọn luân phiên theo `business_sector_priority`. Ảnh bìa lấy từ `apps.srv_poi_info`. |
| Method | GET |
| Endpoint | /api/v1/pois/features |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | Accept-Language | string | không | Dùng khi không có query `lang`. Thiếu cả hai thì `vi`. |
| 2 | X-Request-Id | string | không | Ghi vào `meta.trace_id`. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | lang | string | không | query. |
| 2 | page | integer | không | query. Mặc định `0`. `@Min(0)`. |
| 3 | size | integer | không | query. Mặc định `10`. `@Min(1)` `@Max(100)`. |
| 4 | business_sector_priority | array | không | query, lặp key. Mặc định `attraction`, `f_n_b`, `event`, `tour_n_activities`. Tối đa 20. Giá trị ngoài `^[a-z0-9_]{1,64}$` trả HTTP 400, message `business_sector_priority contains an invalid value`. |
| 5 | fallback_min_rating | number | không | query. Mặc định `4.5`. Từ 0 đến 5. So với `apps.srv_poi_info.rating_overall`. |
| 6 | fallback_min_review_count | integer | không | query. Mặc định `100`. `@Min(0)`. So với `apps.srv_poi_info.rating_count`. |
| 7 | rating_source | string | không | query. Tối đa 64. Rỗng nghĩa là không lọc `apps.srv_poi_info.source_name`. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | `true` khi HTTP 200. |
| 2 | code | integer | có | envelope | Thành công là `200`. |
| 3 | message | string | có | envelope | `Featured POIs retrieved successfully`. |
| 4 | data | array | có | envelope | Đúng thứ tự id SQL trả về. |
| 5 | data[].id | string | có | apps.srv_poi_info.poi_id | |
| 6 | data[].name | string | có | apps.srv_poi_info.poi_name | |
| 7 | data[].description | string | có | apps.srv_poi_multi_lang.description | |
| 8 | data[].cover | object | có | apps.srv_poi_info.cover_id; apps.srv_poi_info.cover_blob_url | Luôn là object. Thành viên null khi cột null. |
| 9 | data[].ratings | array | có | apps.srv_poi_info.rating_overall; apps.srv_poi_info.rating_count | Một phần tử khi một trong hai khác null, còn lại mảng rỗng. |
| 10 | data[].business_tags | object | có | apps.srv_poi_info.business_sector; apps.srv_poi_info.business_category; apps.srv_poi_info.subcategory_tags | |
| 11 | data[].status | object | có | apps.srv_poi_info.operating_status; apps.srv_poi_info.is_verified; apps.srv_poi_info.is_recommended; apps.srv_poi_info.is_bookable | |
| 12 | data[].operating_hours | array | có | apps.srv_poi_info.operating_hours | Null khi cột null hoặc JSON null. JSON hỏng thì mảng rỗng. |
| 13 | data[].address | object | có | apps.srv_poi_info.full_address; apps.srv_poi_info.city; apps.srv_poi_info.district | |
| 14 | data[].geo_location | object | có | apps.srv_poi_info.lat; apps.srv_poi_info.lng | |
| 15 | meta | object | có | envelope | |
| 16 | meta.timestamp | string | có | envelope | |
| 17 | meta.trace_id | string | có | envelope | |
| 18 | meta.pagination | object | có | envelope | |
| 19 | meta.pagination.type | string | có | envelope | `offset`. |
| 20 | meta.pagination.page | integer | có | envelope | |
| 21 | meta.pagination.per_page | integer | có | envelope | |
| 22 | meta.pagination.total_items | integer | có | envelope | |
| 23 | meta.pagination.total_pages | integer | có | envelope | |
| 24 | meta.pagination.has_next | boolean | có | envelope | |
| 25 | meta.pagination.has_prev | boolean | có | envelope | |
| 26 | errors | array | có | envelope | Null khi thành công. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| 200 | null | Thành công. |
| 400 | ERR_BAD_REQUEST | `business_sector_priority` có giá trị không hợp lệ. |
| 422 | ERR_VALIDATION_FAILED | `page`, `size`, ngưỡng rating, hoặc độ dài danh sách sector ngoài khoảng. |
| 500 | INTERNAL_SERVER_ERROR | Lỗi không phân loại. |

## Sample request

```http
GET /api/v1/pois/features?page=0&size=1 HTTP/1.1
Accept-Language: vi
X-Request-Id: 22222222-2222-2222-2222-222222222222
```

## Sample response

Lấy từ Dev ngày 2026-11-11. `size=1` để sample là đúng một response.

```json
{
  "success": true,
  "code": 200,
  "message": "Featured POIs retrieved successfully",
  "data": [
    {
      "id": "14b2e2c4-95a8-d851-240f-c25e4e8cdb7a",
      "name": "French Village Ba Na Hills Viewpoint",
      "description": "French Village Ba Na Hills Viewpoint là điểm ngắm cảnh lý tưởng với kiến trúc châu Âu cổ kính mang đến trải nghiệm như lạc bước giữa lòng nước Pháp trên đỉnh núi Bà Nà",
      "cover": {
        "id": "743d1739d195cf9a6bb428dd1c411a3cac900b958bed055bdc713f8dfe2c990e",
        "file_key": "partner_biz_service/2026/07/30/f4266e87-804a-43bd-8941-6eb6cb4aff9e_PsqwmsyU9R_38ada1a2-784c-49a0-b83f-0e8cc69f556f_datacollector_media_ChIJl-l3UgD3QTEREh-UpumcwQA_Ab43msK6J9g96mYK03fP.jpg"
      },
      "ratings": [],
      "business_tags": {
        "business_sector": "attraction",
        "business_category": null,
        "subcategory_tags": null
      },
      "status": {
        "operating_status": "",
        "is_verified": null,
        "is_recommended": true,
        "is_bookable": null
      },
      "operating_hours": [
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
      ],
      "address": {
        "full_address": "00, Hòa Ninh, Xã Bà Nà, Thành phố Đà Nẵng",
        "street": "Hòa Ninh",
        "ward": "Xã Bà Nà",
        "district": null,
        "city": "Thành phố Đà Nẵng",
        "country_code": null
      },
      "geo_location": null
    }
  ],
  "meta": {
    "timestamp": "2026-11-11T06:59:22.449487Z",
    "trace_id": "22222222-2222-2222-2222-222222222222",
    "pagination": {
      "type": "offset",
      "page": 0,
      "per_page": 1,
      "total_items": 88,
      "total_pages": 88,
      "has_next": true,
      "has_prev": false
    }
  },
  "errors": null
}
```
