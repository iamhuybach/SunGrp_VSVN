# POST /api/v1/pois/practical_info

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Danh sách thông tin thực tế. `ids` nhận `apps.srv_poi_info.poi_id` hoặc `apps.srv_poi_legacy_id_map.legacy_poi_id` khi `apps.srv_poi_legacy_id_map.poi_id_status` là `OK` và `apps.srv_poi_legacy_id_map.poi_id` khác null, trừ khi giá trị đó đã là `apps.srv_poi_info.poi_id`. `data.id` là `poi_id` mới. Một phần tử cho mỗi `poi_id` đã resolve, `deleted_at` null, sau lọc `source` và `poi_name`. |
| Method | POST |
| Endpoint | /api/v1/pois/practical_info |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | Accept-Language | string | không | Dùng khi không có query `lang`. Thiếu cả hai thì `vi`. |
| 2 | X-Request-Id | string | không | Ghi vào `meta.trace_id`. |
| 3 | Authorization | string | có | `Bearer <token>`. Token khớp biến môi trường `POI_API_BEARER_TOKEN` của server. Thiếu header, scheme khác `Bearer`, hoặc token sai trả HTTP 401. |
| 4 | Content-Type | string | không | `application/json`. Sai kiểu trả HTTP 415. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | required_fields | string | không | id, name, description, time_to_spend, cost, best_time, cover, ratings, business_tags, status, operating_hours, holiday_exceptions, address, geo_location, destinations, phone, email, website_url |
| 2 | source | string | không | `partner`, `google`. Rỗng thì không lọc. So `lower(trim(apps.srv_poi_info.source_name))`. |
| 3 | lang | string | không | `vi`, `en`, `ko`. Query ưu tiên hơn `Accept-Language`. Thiếu cả hai thì `vi`. `en-US` lấy `en`. |
| 4 | poi_name | string | không | query. Tối đa 128. Rỗng thì không lọc. Khớp không phân biệt hoa thường trên `apps.srv_poi_info.poi_name`. `%`, `_` và `\` được escape. |
| 5 | page | integer | không | query. Mặc định `0`. `@Min(0)`. |
| 6 | size | integer | không | query. Mặc định `10`. `@Min(1)` `@Max(100)`. |
| 7 | sort_field | string | không | `id`, `name`, `ratings_avg_score`, `ratings_count`. Đúng một giá trị. Vắng thì `poi_id` tăng dần. |
| 8 | sort_order | string | không | `asc`, `desc`. Mặc định `asc`. Null đứng cuối, rồi `poi_id` tăng dần. |

## Giá trị param

`required_fields` lặp hoặc CSV. Vắng hoặc rỗng thì đủ field detail. Có giá trị thì chỉ các khóa được chọn, theo thứ tự detail, giữ null.

| Giá trị | Ý nghĩa |
|---|---|
| `id` | `poi_id` mới |
| `name` | Tên POI |
| `description` | Mô tả theo `lang`, thiếu thì `vi` |
| `time_to_spend` | Thời gian tham quan |
| `cost` | Chi phí |
| `best_time` | Thời điểm nên đến |
| `cover` | Ảnh bìa |
| `ratings` | Nguồn điểm, số lượt, điểm trung bình |
| `business_tags` | `business_sector`, `business_category` |
| `status` | Trạng thái vận hành và các cờ |
| `operating_hours` | Giờ mở cửa |
| `holiday_exceptions` | Ngoại lệ ngày lễ, giữ nguyên JSON |
| `address` | Địa chỉ |
| `geo_location` | Tọa độ |
| `destinations` | Điểm đến |
| `phone` | Số điện thoại. Không ghi log |
| `email` | Email. Không ghi log |
| `website_url` | Website |

`source` chỉ hai giá trị. So khớp sau khi viết thường và cắt khoảng trắng ở `apps.srv_poi_info.source_name`.

| Giá trị | Lọc |
|---|---|
| `partner` | POI partner |
| `google` | POI google |

`lang` là mã ngôn ngữ nội dung. Ba mã có bản ghi trong policy là `vi`, `en`, `ko`. Trường đa ngôn ngữ thiếu bản `lang` đã chọn thì đọc bản `vi`.

| Giá trị | Khi dùng |
|---|---|
| `vi` | Mặc định khi không có query và không có `Accept-Language` |
| `en` | Bản tiếng Anh. `en-US` cũng thành `en` |
| `ko` | Bản tiếng Hàn |

`sort_field` đúng một field. Đi cùng `sort_order` = `asc` hoặc `desc`.

| Giá trị | Cột sắp |
|---|---|
| `id` | `apps.srv_poi_info.poi_id` |
| `name` | `apps.srv_poi_info.poi_name` |
| `ratings_avg_score` | `apps.srv_poi_info.rating_overall` |
| `ratings_count` | `apps.srv_poi_info.rating_count` |

## Request body

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | ids | array | có | Từ 1 đến 500 chuỗi. Mỗi phần tử không rỗng, dài tối đa 128. Đếm cả phần tử trùng. `apps.srv_poi_info.poi_id` hoặc `apps.srv_poi_legacy_id_map.legacy_poi_id`. `data.id` là `poi_id` mới. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | `true` khi HTTP 200. |
| 2 | code | integer | có | envelope | Thành công là `200`. |
| 3 | message | string | có | envelope | `POI practical info list retrieved successfully`. |
| 4 | data | array | có | envelope | Một phần tử là một POI. Có thể rỗng. |
| 5 | data[] | object | có | GET practical_info `data` | Đủ field khi `required_fields` vắng hoặc rỗng. Có chọn thì chỉ các khóa được chọn, giữ null. |
| 6 | meta | object | có | envelope | |
| 7 | meta.timestamp | string | có | envelope | ISO-8601 UTC. |
| 8 | meta.trace_id | string | có | envelope | |
| 9 | meta.pagination | object | có | envelope | |
| 10 | meta.pagination.type | string | có | envelope | `offset`. |
| 11 | meta.pagination.page | integer | có | envelope | |
| 12 | meta.pagination.per_page | integer | có | envelope | |
| 13 | meta.pagination.total_items | integer | có | envelope | |
| 14 | meta.pagination.total_pages | integer | có | envelope | |
| 15 | meta.pagination.has_next | boolean | có | envelope | |
| 16 | meta.pagination.has_prev | boolean | có | envelope | |
| 17 | errors | array | có | envelope | Null khi thành công. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| 200 | null | Thành công, kể cả `data` rỗng. |
| 400 | null | Body không đọc được hoặc `page`/`size` không phải số. |
| 401 | ERR_UNAUTHORIZED | Thiếu `Authorization`, scheme khác `Bearer`, token sai, hoặc server chưa cấu hình token. Kiểm tra trước mọi mã khác. Message `Missing or invalid bearer token.` Header `WWW-Authenticate: Bearer`. |
| 415 | null | `Content-Type` khác `application/json`. |
| 422 | ERR_VALIDATION_FAILED | `ids`, `required_fields`, `source`, `poi_name`, `page`, `size`, `sort_field` hoặc `sort_order` ngoài hợp đồng. |
| 500 | INTERNAL_SERVER_ERROR | Lỗi không phân loại. |

## Sample request

Không truyền `required_fields`, `source`, `lang`, `sort_field`. `data[0]` lấy từ Dev ngày 2026-11-11 trong `practical_info.md`. `phone` và `email` có giá trị trên Dev và được để `null` trong file này.

```http
POST /api/v1/pois/practical_info?page=0&size=10 HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json
Accept-Language: vi
X-Request-Id: 22222222-2222-2222-2222-222222222222

{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}
```

## Sample response

```json
{
  "success": true,
  "code": 200,
  "message": "POI practical info list retrieved successfully",
  "data": [
    {
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
          {"day_of_week": 1, "open_time": "08:00", "close_time": "22:00", "is_open_all_day": false, "is_closed": false},
          {"day_of_week": 2, "open_time": "08:00", "close_time": "22:00", "is_open_all_day": false, "is_closed": false},
          {"day_of_week": 3, "open_time": "08:00", "close_time": "22:00", "is_open_all_day": false, "is_closed": false},
          {"day_of_week": 4, "open_time": "08:00", "close_time": "22:00", "is_open_all_day": false, "is_closed": false},
          {"day_of_week": 5, "open_time": "08:00", "close_time": "22:00", "is_open_all_day": false, "is_closed": false},
          {"day_of_week": 6, "open_time": "08:00", "close_time": "22:00", "is_open_all_day": false, "is_closed": false},
          {"day_of_week": 7, "open_time": "08:00", "close_time": "22:00", "is_open_all_day": false, "is_closed": false}
        ]
      },
      "holiday_exceptions": [
        {
          "date": "30/07/2026",
          "hours": [{"open_time": "08:00", "close_time": "12:00"}],
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
      "destinations": {"id": null, "name": null}
    }
  ],
  "meta": {
    "timestamp": "2026-11-11T06:59:23.581325900Z",
    "trace_id": "22222222-2222-2222-2222-222222222222",
    "pagination": {
      "type": "offset",
      "page": 0,
      "per_page": 10,
      "total_items": 1,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "errors": null
}
```

## Sample required_fields

Chọn `id` và `name` từ cùng bản ghi Dev.

```http
POST /api/v1/pois/practical_info?required_fields=id,name HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}
```

```json
{
  "success": true,
  "code": 200,
  "message": "POI practical info list retrieved successfully",
  "data": [
    {
      "id": "14b2e2c4-95a8-d851-240f-c25e4e8cdb7a",
      "name": "French Village Ba Na Hills Viewpoint"
    }
  ],
  "meta": {
    "timestamp": "2026-11-11T06:59:23.581325900Z",
    "trace_id": "22222222-2222-2222-2222-222222222222",
    "pagination": {
      "type": "offset",
      "page": 0,
      "per_page": 10,
      "total_items": 1,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "errors": null
}
```

## Sample source

`source=partner` giữ POI Dev ở trên vì `ratings.source` là `partner`.

```http
POST /api/v1/pois/practical_info?source=partner&required_fields=id,name,ratings HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}
```

```json
{
  "success": true,
  "code": 200,
  "message": "POI practical info list retrieved successfully",
  "data": [
    {
      "id": "14b2e2c4-95a8-d851-240f-c25e4e8cdb7a",
      "name": "French Village Ba Na Hills Viewpoint",
      "ratings": {
        "source": "partner",
        "ratings_count": null,
        "ratings_avg_score": null
      }
    }
  ],
  "meta": {
    "timestamp": "2026-11-11T06:59:23.581325900Z",
    "trace_id": "22222222-2222-2222-2222-222222222222",
    "pagination": {
      "type": "offset",
      "page": 0,
      "per_page": 10,
      "total_items": 1,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "errors": null
}
```

`source=google` dùng `poi_id` trong sample reviews Dev ngày 2026-11-11. File này không có bản practical info của POI đó, nên không ghi body response.

```http
POST /api/v1/pois/practical_info?source=google&required_fields=id,name,ratings HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{"ids":["85c1a13a-9c11-a579-0a07-dfd8337596dd"]}
```

## Sample lang

`lang=vi` trả `description` tiếng Việt của bản ghi Dev.

```http
POST /api/v1/pois/practical_info?lang=vi&required_fields=id,description HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}
```

```json
{
  "success": true,
  "code": 200,
  "message": "POI practical info list retrieved successfully",
  "data": [
    {
      "id": "14b2e2c4-95a8-d851-240f-c25e4e8cdb7a",
      "description": "French Village Ba Na Hills Viewpoint là điểm ngắm cảnh lý tưởng với kiến trúc châu Âu cổ kính mang đến trải nghiệm như lạc bước giữa lòng nước Pháp trên đỉnh núi Bà Nà"
    }
  ],
  "meta": {
    "timestamp": "2026-11-11T06:59:23.581325900Z",
    "trace_id": "22222222-2222-2222-2222-222222222222",
    "pagination": {
      "type": "offset",
      "page": 0,
      "per_page": 10,
      "total_items": 1,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "errors": null
}
```

`lang=en` và `lang=ko` dùng cùng `poi_id`. File này không có câu chữ `en` hoặc `ko` từ Dev, nên không ghi body response.

```http
POST /api/v1/pois/practical_info?lang=en&required_fields=id,description HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}
```

```http
POST /api/v1/pois/practical_info?lang=ko&required_fields=id,description HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}
```

## Sample sort_field

Một POI thì thứ tự không đổi. Bốn request dưới đây là đủ giá trị `sort_field`. `data[0].id` và `data[0].name` vẫn là bản ghi Dev ở sample response đầu.

```http
POST /api/v1/pois/practical_info?sort_field=id&sort_order=asc&required_fields=id,name HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}
```

```http
POST /api/v1/pois/practical_info?sort_field=name&sort_order=desc&required_fields=id,name HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}
```

```http
POST /api/v1/pois/practical_info?sort_field=ratings_avg_score&sort_order=desc&required_fields=id,name,ratings HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}
```

```http
POST /api/v1/pois/practical_info?sort_field=ratings_count&sort_order=asc&required_fields=id,name,ratings HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{"ids":["14b2e2c4-95a8-d851-240f-c25e4e8cdb7a"]}
```
