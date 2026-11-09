# GET /api/v1/pois/{poi_id}/reviews

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Truy vấn đánh giá của một POI, có phân trang. Sắp `reviewDate` giảm dần. Chỉ review có `apps.srv_poi_review.deleted_at` null. POI phải còn trong `apps.srv_poi_info` với `deleted_at` null. |
| Method | GET |
| Endpoint | /api/v1/pois/{poi_id}/reviews |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | X-Request-Id | string | không | `RequestIdFilter` đọc header này, hoặc `X-Request-ID`, ghi vào `meta.trace_id`. Thiếu thì server tạo UUID. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | poi_id | string | có | path. `apps.srv_poi_info.poi_id`. |
| 2 | page | integer | không | query. Mặc định `0`. `@Min(0)`. |
| 3 | size | integer | không | query. Mặc định `10`. `@Min(1)` `@Max(100)`. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | `true` khi HTTP 200. |
| 2 | code | integer | có | envelope | Số HTTP trong body. Thành công là `200`. |
| 3 | message | string | có | envelope | Thành công: `POI reviews retrieved successfully`. |
| 4 | data | array | có | envelope | Danh sách `PoiReviewItemResponse`. Rỗng khi POI tồn tại mà không có review. Null khi lỗi. |
| 5 | data[].review_id | string | có | apps.srv_poi_review.review_id | |
| 6 | data[].author_name | string | có | apps.srv_poi_review.author_name | Giá trị có thể null. |
| 7 | data[].rating | number | có | apps.srv_poi_review.rating; apps.srv_poi_review.rating_overall | `rating` khi khác null, còn lại `rating_overall`. Cả hai là `numeric(4, 2)`. Cả hai null thì giá trị JSON null. |
| 8 | data[].review_text | string | có | apps.srv_poi_review.review_text | Giá trị có thể null. |
| 9 | data[].review_date | string | có | apps.srv_poi_review.review_date | Cột `text`. Giá trị có thể null. |
| 10 | meta | object | có | envelope | |
| 11 | meta.timestamp | string | có | envelope | ISO-8601 UTC. |
| 12 | meta.trace_id | string | có | envelope | Từ `X-Request-Id` hoặc UUID server tạo. |
| 13 | meta.error_code | string | không | envelope | Null khi thành công, key bị bỏ. Khi lỗi là chuỗi ở bảng Status code. |
| 14 | meta.pagination | object | có | envelope | `successList` luôn gắn pagination. |
| 15 | meta.pagination.type | string | có | envelope | Giá trị `offset`. |
| 16 | meta.pagination.page | integer | có | envelope | Bằng query `page`. |
| 17 | meta.pagination.per_page | integer | có | envelope | Bằng query `size`. |
| 18 | meta.pagination.total_items | integer | có | envelope | Tổng review sau filter. |
| 19 | meta.pagination.total_pages | integer | có | envelope | `ceil(total_items / per_page)`. |
| 20 | meta.pagination.has_next | boolean | có | envelope | |
| 21 | meta.pagination.has_prev | boolean | có | envelope | `true` khi `page` > 0. |
| 22 | errors | array | có | envelope | Null khi thành công. |
| 23 | errors[].field | string | không | envelope | Có khi HTTP 422. |
| 24 | errors[].code | string | không | envelope | Mã field error hoặc tên constraint, viết hoa. Không phải `meta.error_code`. |
| 25 | errors[].message | string | không | envelope | Message validation. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| 200 | null | Truy vấn thành công. `meta.error_code` null. |
| 400 | ERR_BAD_REQUEST | `@ApiResponses` ghi tham số truy vấn không hợp lệ. Handler map `MethodArgumentTypeMismatchException` và `IllegalArgumentException`. `errors` null. |
| 404 | POI_NOT_FOUND | `@ApiResponses` ghi không tìm thấy POI. `validatePoiExists` ném `ResourceNotFoundException` khi không có `apps.srv_poi_info.poi_id` với `deleted_at` null. Message `POI not found with id: ` cộng `poi_id`. |
| 409 | STATE_CONFLICT | Handler map `IllegalStateException`. Message là message của exception. |
| 422 | ERR_VALIDATION_FAILED | `@ApiResponses` ghi vi phạm validation. `@Min` `@Max` trên `page` và `size` vào `HandlerMethodValidationException`. Message `Validation failed`. |
| 500 | INTERNAL_SERVER_ERROR | Handler map `Exception` còn lại. Message `An unexpected error occurred. Please contact support with the trace ID.` |
| 401 | không có | không có trong code |
| 403 | không có | không có trong code |
| 429 | không có | không có trong code |

## Sample request

```http
GET /api/v1/pois/11111111-1111-1111-1111-111111111111/reviews?page=0&size=10 HTTP/1.1
X-Request-Id: 22222222-2222-2222-2222-222222222222
```

## Sample response

```json
{
  "success": true,
  "code": 200,
  "message": "POI reviews retrieved successfully",
  "data": [
    {
      "review_id": "44444444-4444-4444-4444-444444444444",
      "author_name": "Tac gia mau",
      "rating": 4.5,
      "review_text": "Nhan xet mau",
      "review_date": "2026-01-01"
    }
  ],
  "meta": {
    "timestamp": "2026-11-09T04:28:00Z",
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
