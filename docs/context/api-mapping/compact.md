# GET /api/v1/pois/compact

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Truy vấn danh sách POI rút gọn. Có phân trang, lọc theo danh sách id, sắp xếp, và ngôn ngữ. Chỉ trả POI có `apps.srv_poi_info.deleted_at` null. |
| Method | GET |
| Endpoint | /api/v1/pois/compact |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | Accept-Language | string | không | Dùng khi query `lang` trống. `LanguageResolver` lấy tag đầu tiên, cắt subtag (`en-US` thành `en`). Cả hai trống thì `vi`. |
| 2 | X-Request-Id | string | không | `RequestIdFilter` đọc header này, hoặc `X-Request-ID`, ghi vào `meta.trace_id`. Thiếu thì server tạo UUID. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | ids | array[string] | không | query. Lọc `apps.srv_poi_info.poi_id`. Bỏ trống thì không lọc theo id. Mô tả OpenAPI ghi tối đa 100 id; code không chặn số lượng. |
| 2 | lang | string | không | query. Ưu tiên hơn `Accept-Language`. Rỗng thì fallback `vi`. Bản dịch lấy `apps.srv_poi_multi_lang` theo lang đó, thiếu thì fallback `vi`. |
| 3 | page | integer | không | query. Mặc định `0`. `@Min(0)`. |
| 4 | size | integer | không | query. Mặc định `20`. `@Min(1)` `@Max(100)`. |
| 5 | sort | string | không | query. Dạng `property,asc` hoặc `property,desc`. Bỏ trống thì `createdAt,desc`. Hướng khác `asc` được coi là `desc`. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | `true` khi HTTP 200. |
| 2 | code | integer | có | envelope | Số HTTP trong body. Thành công là `200`. |
| 3 | message | string | có | envelope | Thành công: `Compact POIs retrieved successfully`. |
| 4 | data | array | có | envelope | Danh sách `CompactPoiResponse`. Rỗng khi không có POI. Null khi lỗi. |
| 5 | data[].id | string | có | apps.srv_poi_info.poi_id | JSON name `id`. |
| 6 | data[].name | string | có | apps.srv_poi_info.poi_name | JSON name `name`. Giá trị có thể null. |
| 7 | data[].description | string | có | apps.srv_poi_multi_lang.description | Bản `lang` đã resolve, thiếu thì bản `vi`. Key luôn có; giá trị null khi không có mô tả. |
| 8 | data[].cover | object | có | không có cột | Object gộp. Null khi POI không có media active (`is_active` null hoặc true, `deleted_at` null). |
| 9 | data[].cover.id | string | không | apps.srv_poi_media_gallery.media_id | Có khi `cover` khác null. Ưu tiên dòng `is_cover` = true, không thì phần tử đầu theo `display_order`. |
| 10 | data[].cover.file_key | string | không | apps.srv_poi_media_gallery.blob_url; apps.srv_poi_media_gallery.photo_api_uri | Có khi `cover` khác null. `blob_url` khi khác blank, còn lại `photo_api_uri`. |
| 11 | data[].cover.width | integer | không | apps.srv_poi_media_gallery.width_px | Có khi `cover` khác null. |
| 12 | data[].cover.height | integer | không | apps.srv_poi_media_gallery.height_px | Có khi `cover` khác null. |
| 13 | data[].cover.mime_type | string | không | không có cột | Có khi `cover` khác null. Suy từ đuôi `file_key`: `.png`, `.webp`, `.gif`, còn lại `image/jpeg`. |
| 14 | data[].cover.blur_hash | string | không | không có cột | Có khi `cover` khác null. Code luôn gán null. |
| 15 | data[].rating | object | có | không có cột | Null khi cả `rating_overall` và `rating_count` đều null. |
| 16 | data[].rating.ratings_avg_score | number | không | apps.srv_poi_info.rating_overall | Có khi `rating` khác null. Cột `numeric(4, 2)`. |
| 17 | data[].rating.ratings_count | integer | không | apps.srv_poi_info.rating_count | Có khi `rating` khác null. |
| 18 | data[].business_tags | object | có | không có cột | Null khi cả `business_sector` và `business_category` đều null. |
| 19 | data[].business_tags.business_sector | string | không | apps.srv_poi_info.business_sector | Có khi `business_tags` khác null. |
| 20 | data[].business_tags.business_sector_label | string | không | không có cột | Có khi `business_tags` khác null. Nhãn từ `BusinessSectorDictionary`, không có cột. |
| 21 | data[].business_tags.business_category | string | không | apps.srv_poi_info.business_category | Có khi `business_tags` khác null. |
| 22 | data[].business_tags.subcategory_tags | array[string] | không | apps.srv_poi_info.subcategory_tags | Có khi `business_tags` khác null. Parser tách JSON array hoặc CSV. Rỗng thì null. |
| 23 | data[].address | object | có | không có cột | Null khi `full_address`, `city`, và `district` đều null. |
| 24 | data[].address.full_address | string | không | apps.srv_poi_info.full_address | Có khi `address` khác null. |
| 25 | data[].address.street | string | không | apps.srv_poi_info.street | Có khi `address` khác null. |
| 26 | data[].address.ward | string | không | apps.srv_poi_info.ward | Có khi `address` khác null. |
| 27 | data[].address.district | string | không | apps.srv_poi_info.district | Có khi `address` khác null. |
| 28 | data[].address.city | string | không | apps.srv_poi_info.city | Có khi `address` khác null. |
| 29 | data[].address.country_code | string | không | apps.srv_poi_info.country_code | Có khi `address` khác null. |
| 30 | data[].geo_location | object | có | không có cột | Null khi `lat` hoặc `lng` null. |
| 31 | data[].geo_location.latitude | number | không | apps.srv_poi_info.lat | Có khi `geo_location` khác null. Cột `double precision`. |
| 32 | data[].geo_location.longitude | number | không | apps.srv_poi_info.lng | Có khi `geo_location` khác null. Cột `double precision`. |
| 33 | meta | object | có | envelope | |
| 34 | meta.timestamp | string | có | envelope | ISO-8601 UTC. |
| 35 | meta.trace_id | string | có | envelope | Từ `X-Request-Id` hoặc UUID server tạo. |
| 36 | meta.error_code | string | không | envelope | Null khi thành công, key bị bỏ (`JsonInclude.NON_NULL`). Khi lỗi là chuỗi ở bảng Status code. |
| 37 | meta.pagination | object | có | envelope | `successList` luôn gắn pagination. |
| 38 | meta.pagination.type | string | có | envelope | Giá trị `offset`. |
| 39 | meta.pagination.page | integer | có | envelope | Bằng query `page`. |
| 40 | meta.pagination.per_page | integer | có | envelope | Bằng query `size`. |
| 41 | meta.pagination.total_items | integer | có | envelope | Tổng bản ghi sau filter. |
| 42 | meta.pagination.total_pages | integer | có | envelope | `ceil(total_items / per_page)`. |
| 43 | meta.pagination.has_next | boolean | có | envelope | |
| 44 | meta.pagination.has_prev | boolean | có | envelope | `true` khi `page` > 0. |
| 45 | errors | array | có | envelope | Null khi thành công. |
| 46 | errors[].field | string | không | envelope | Có khi HTTP 422. |
| 47 | errors[].code | string | không | envelope | Mã field error hoặc tên constraint, viết hoa. Không phải `meta.error_code`. |
| 48 | errors[].message | string | không | envelope | Message validation. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| 200 | null | Truy vấn thành công. `meta.error_code` null. |
| 400 | ERR_BAD_REQUEST | `@ApiResponses` ghi tham số truy vấn không hợp lệ. Handler map `MethodArgumentTypeMismatchException` và `IllegalArgumentException`. `errors` null. |
| 404 | POI_NOT_FOUND | Handler map `ResourceNotFoundException`. Method này không gọi `validatePoiExists`; không có POI thì HTTP 200 và `data` rỗng. |
| 409 | STATE_CONFLICT | Handler map `IllegalStateException`. Message là message của exception. |
| 422 | ERR_VALIDATION_FAILED | `@ApiResponses` ghi vi phạm validation. `@Min` `@Max` trên `page` và `size` vào `HandlerMethodValidationException`. Message `Validation failed`. |
| 500 | INTERNAL_SERVER_ERROR | Handler map `Exception` còn lại. Message `An unexpected error occurred. Please contact support with the trace ID.` |
| 401 | không có | không có trong code |
| 403 | không có | không có trong code |
| 429 | không có | không có trong code |

## Sample request

```http
GET /api/v1/pois/compact?ids=11111111-1111-1111-1111-111111111111&lang=vi&page=0&size=20 HTTP/1.1
Accept-Language: vi
X-Request-Id: 22222222-2222-2222-2222-222222222222
```

## Sample response

```json
{
  "success": true,
  "code": 200,
  "message": "Compact POIs retrieved successfully",
  "data": [
    {
      "id": "11111111-1111-1111-1111-111111111111",
      "name": "Dia diem mau",
      "description": "Mo ta mau",
      "cover": {
        "id": "33333333-3333-3333-3333-333333333333",
        "file_key": "https://cdn.example.invalid/mau.jpg",
        "width": 640,
        "height": 480,
        "mime_type": "image/jpeg",
        "blur_hash": null
      },
      "rating": {
        "ratings_avg_score": 4.5,
        "ratings_count": 2
      },
      "business_tags": {
        "business_sector": "OTHER",
        "business_sector_label": "Khác",
        "business_category": "mau",
        "subcategory_tags": ["mau"]
      },
      "address": {
        "full_address": "Dia chi mau",
        "street": "Duong mau",
        "ward": "Phuong mau",
        "district": "Quan mau",
        "city": "Thanh pho mau",
        "country_code": "VN"
      },
      "geo_location": {
        "latitude": 1.0,
        "longitude": 2.0
      }
    }
  ],
  "meta": {
    "timestamp": "2026-11-09T04:28:00Z",
    "trace_id": "22222222-2222-2222-2222-222222222222",
    "pagination": {
      "type": "offset",
      "page": 0,
      "per_page": 20,
      "total_items": 1,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "errors": null
}
```
