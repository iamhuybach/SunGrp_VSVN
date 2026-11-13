# GET /api/v1/pois/{poi_id}/reviews

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Đánh giá của một POI. Không kiểm tra POI có trong `apps.srv_poi_info`. Không có review thì `data` và `rating_summary` đều rỗng. Sắp `apps.srv_poi_review.review_date` giảm dần, rồi `apps.srv_poi_review.review_id` tăng dần. Chỉ dòng `apps.srv_poi_review.deleted_at` null. |
| Method | GET |
| Endpoint | /api/v1/pois/{poi_id}/reviews |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | X-Request-Id | string | không | Ghi vào `meta.trace_id`. Thiếu thì server tạo UUID. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | poi_id | string | có | path. Lọc `apps.srv_poi_review.poi_id`. |
| 2 | page | integer | không | query. Mặc định `0`. `@Min(0)`. |
| 3 | size | integer | không | query. Mặc định `10`. `@Min(1)` `@Max(100)`. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | `true` khi HTTP 200. |
| 2 | code | integer | có | envelope | Thành công là `200`. |
| 3 | message | string | có | envelope | `POI reviews retrieved successfully`. |
| 4 | data | array | có | envelope | Một phần tử là một review. |
| 5 | data[].review_id | string | có | apps.srv_poi_review.review_id | |
| 6 | data[].author_name | string | có | apps.srv_poi_review.author_name | Có thể null. |
| 7 | data[].rating | number | có | apps.srv_poi_review.rating; apps.srv_poi_review.rating_overall | `rating` khi khác null, còn lại `rating_overall`. |
| 8 | data[].review_text | string | có | apps.srv_poi_review.review_text | Có thể null. |
| 9 | data[].review_date | string | có | apps.srv_poi_review.review_date | Có thể null. |
| 10 | data[].source_name | string | có | apps.srv_poi_review.source_name | Gold literal google (D-3). |
| 11 | rating_summary | array | có | apps.srv_poi_review.rating_count; apps.srv_poi_review.rating_overall | Ngang hàng với `data`. Đúng một phần tử khi trang hiện tại có review, hoặc trang rỗng nhưng tổng lớn hơn 0. Cả hai rỗng thì mảng rỗng. |
| 12 | rating_summary[].rating_count | integer | có | apps.srv_poi_review.rating_count | |
| 13 | rating_summary[].rating_avg_score | number | có | apps.srv_poi_review.rating_overall | |
| 14 | meta | object | có | envelope | |
| 15 | meta.timestamp | string | có | envelope | ISO-8601 UTC. |
| 16 | meta.trace_id | string | có | envelope | |
| 17 | meta.pagination | object | có | envelope | |
| 18 | meta.pagination.type | string | có | envelope | `offset`. |
| 19 | meta.pagination.page | integer | có | envelope | |
| 20 | meta.pagination.per_page | integer | có | envelope | |
| 21 | meta.pagination.total_items | integer | có | envelope | |
| 22 | meta.pagination.total_pages | integer | có | envelope | |
| 23 | meta.pagination.has_next | boolean | có | envelope | |
| 24 | meta.pagination.has_prev | boolean | có | envelope | |
| 25 | errors | array | có | envelope | Null khi thành công. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| 200 | null | Thành công, kể cả POI không tồn tại. HTTP 404 không xảy ra. |
| 422 | ERR_VALIDATION_FAILED | `page` hoặc `size` ngoài khoảng. |
| 500 | INTERNAL_SERVER_ERROR | Lỗi không phân loại. |

## Sample request

```http
GET /api/v1/pois/85c1a13a-9c11-a579-0a07-dfd8337596dd/reviews?page=0&size=1 HTTP/1.1
X-Request-Id: 22222222-2222-2222-2222-222222222222
```

## Sample response

Lấy từ Dev ngày 2026-11-11.

```json
{
  "success": true,
  "code": 200,
  "message": "POI reviews retrieved successfully",
  "data": [
    {
      "review_id": "ead223471cdc9cf4074fac347963e6024513085b5328c30fe84f6006c9555547",
      "author_name": "Quốc",
      "rating": 5.0,
      "review_text": "Rất tốt",
      "review_date": "2026-10-05T11:31:49.575119426Z",
      "source_name": "google"
    }
  ],
  "rating_summary": [
    {
      "rating_count": 89,
      "rating_avg_score": 3.0
    }
  ],
  "meta": {
    "timestamp": "2026-11-11T06:59:23.198149500Z",
    "trace_id": "22222222-2222-2222-2222-222222222222",
    "pagination": {
      "type": "offset",
      "page": 0,
      "per_page": 1,
      "total_items": 9,
      "total_pages": 9,
      "has_next": true,
      "has_prev": false
    }
  },
  "errors": null
}
```
