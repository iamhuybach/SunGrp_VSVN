# POST /api/v1/pois/compact

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Truy vấn POI rút gọn theo danh sách `poi_id`. Thứ tự `apps.srv_poi_info.created_at` giảm dần, rồi `apps.srv_poi_info.poi_id` tăng dần. Chỉ dòng `apps.srv_poi_info.deleted_at` null. Ảnh bìa lấy từ `apps.srv_poi_info`, không đọc gallery. |
| Method | POST |
| Endpoint | /api/v1/pois/compact |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | Content-Type | string | không | Phải là `application/json`. Sai kiểu trả HTTP 415. |
| 2 | Accept-Language | string | không | Dùng khi body không có `lang`. Thiếu cả hai thì `vi`. |
| 3 | X-Request-Id | string | không | Ghi vào `meta.trace_id`. Thiếu thì server tạo UUID. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | không có | không có | không | Không có path hay query. `GET /api/v1/pois/compact` trả HTTP 405. |

## Request body

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | lang | string | không | Ngôn ngữ mô tả. Thiếu thì dùng `Accept-Language`, rồi `vi`. |
| 2 | ids | array | không | `apps.srv_poi_info.poi_id`. Tối thiểu 1, tối đa 20 phần tử. Mỗi phần tử không rỗng, dài tối đa 128. Thiếu, rỗng, quá 20, hoặc phần tử blank trả HTTP 422. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | `true` khi HTTP 200. |
| 2 | code | integer | có | envelope | Thành công là `200`. |
| 3 | message | string | có | envelope | `Compact POIs retrieved successfully`. |
| 4 | data | array | có | envelope | Danh sách POI. Id không có trong bảng thì vắng khỏi mảng. |
| 5 | data[].id | string | có | apps.srv_poi_info.poi_id | |
| 6 | data[].name | string | có | apps.srv_poi_info.poi_name | |
| 7 | data[].description | string | có | apps.srv_poi_multi_lang.description | Chuỗi không rỗng đầu tiên theo ngôn ngữ đã resolve rồi `vi`. Không có thì null. |
| 8 | data[].cover | object | có | apps.srv_poi_info.cover_id; apps.srv_poi_info.cover_blob_url | Null khi cả hai cột null. |
| 9 | data[].cover.id | string | có | apps.srv_poi_info.cover_id | |
| 10 | data[].cover.file_key | string | có | apps.srv_poi_info.cover_blob_url | |
| 11 | data[].rating | object | có | apps.srv_poi_info.rating_overall; apps.srv_poi_info.rating_count | Null khi cả hai null. |
| 12 | data[].rating.ratings_avg_score | number | có | apps.srv_poi_info.rating_overall | |
| 13 | data[].rating.ratings_count | integer | có | apps.srv_poi_info.rating_count | |
| 14 | data[].business_tags | object | có | apps.srv_poi_info.business_sector; apps.srv_poi_info.business_category; apps.srv_poi_info.subcategory_tags | Không có `business_sector_label`. |
| 15 | data[].address | object | có | apps.srv_poi_info.full_address; apps.srv_poi_info.city; apps.srv_poi_info.district | Null khi cả ba null hoặc rỗng. |
| 16 | data[].geo_location | object | có | apps.srv_poi_info.lat; apps.srv_poi_info.lng | Null khi thiếu một trong hai. |
| 17 | meta | object | có | envelope | Không có `meta.pagination`. |
| 18 | meta.timestamp | string | có | envelope | ISO-8601 UTC. |
| 19 | meta.trace_id | string | có | envelope | |
| 20 | errors | array | có | envelope | Null khi thành công. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| 200 | null | Truy vấn thành công. |
| 400 | ERR_BAD_REQUEST | Body JSON hỏng hoặc thiếu. Message cố định `Malformed or missing request body.` Không echo nội dung body. |
| 405 | không có | `GET /api/v1/pois/compact` không có mapping. |
| 415 | không có | Content-Type không phải JSON. |
| 422 | ERR_VALIDATION_FAILED | `ids` thiếu, rỗng, quá 20, hoặc phần tử blank. |
| 500 | INTERNAL_SERVER_ERROR | Lỗi không phân loại. |

## Sample request

```http
POST /api/v1/pois/compact HTTP/1.1
Content-Type: application/json
Accept-Language: vi
X-Request-Id: 22222222-2222-2222-2222-222222222222

{"lang":"vi","ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}
```

## Sample response

Lấy từ Dev ngày 2026-11-11.

```json
{
  "success": true,
  "code": 200,
  "message": "Compact POIs retrieved successfully",
  "data": [
    {
      "id": "14b2e2c4-95a8-d851-240f-c25e4e8cdb7a",
      "name": "French Village Ba Na Hills Viewpoint",
      "description": "French Village Ba Na Hills Viewpoint là điểm ngắm cảnh lý tưởng với kiến trúc châu Âu cổ kính mang đến trải nghiệm như lạc bước giữa lòng nước Pháp trên đỉnh núi Bà Nà",
      "cover": {
        "id": "743d1739d195cf9a6bb428dd1c411a3cac900b958bed055bdc713f8dfe2c990e",
        "file_key": "partner_biz_service/2026/07/30/f4266e87-804a-43bd-8941-6eb6cb4aff9e_PsqwmsyU9R_38ada1a2-784c-49a0-b83f-0e8cc69f556f_datacollector_media_ChIJl-l3UgD3QTEREh-UpumcwQA_Ab43msK6J9g96mYK03fP.jpg"
      },
      "rating": null,
      "business_tags": {
        "business_sector": "attraction",
        "business_category": null,
        "subcategory_tags": null
      },
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
    "timestamp": "2026-11-11T06:59:22.652473500Z",
    "trace_id": "22222222-2222-2222-2222-222222222222"
  },
  "errors": null
}
```
