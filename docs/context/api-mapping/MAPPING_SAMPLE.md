# Mapping sample

Mẫu cấu trúc cho bốn tài liệu API. Endpoint dưới đây là GET minh họa, không phải API đang chạy. Bốn file API giữ đúng tên mục và đúng cột của các bảng này.

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | GET minh họa, đủ các mục để copy cấu trúc. Không có handler tương ứng trong code. |
| Method | GET |
| Endpoint | /api/v1/example/items/{item_id} |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | Accept-Language | string | không | Minh họa một header tùy chọn. API thật không khai báo header thì một dòng, Field = không có, Description = không có. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | item_id | string | có | path. Minh họa tham số path. `poi_id` của API thật ghi là path ở cột này. |
| 2 | lang | string | không | query. Minh họa tham số query. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | Minh họa field envelope. |
| 2 | code | integer | có | envelope | Số HTTP trong body. Không đổi `meta.error_code` thành số. |
| 3 | message | string | có | envelope | Chuỗi message của envelope. |
| 4 | data | array | có | envelope | Mảng nghiệp vụ. |
| 5 | data[].id | string | có | `apps.<bảng>.<cột>` | Minh họa JSON path. Bốn API thay bằng cột có thật, dạng `apps.<bảng>.<cột>`. |
| 6 | meta | object | có | envelope | Metadata kỹ thuật. |
| 7 | meta.timestamp | string | có | envelope | ISO-8601. |
| 8 | meta.trace_id | string | có | envelope | JSON name là `trace_id`. |
| 9 | meta.error_code | string | không | envelope | JSON name là `error_code`. Null khi thành công thì key bị bỏ. |
| 10 | meta.pagination | object | không | envelope | Có khi API gọi `successList`. |
| 11 | meta.pagination.type | string | không | envelope | Ví dụ `offset`. |
| 12 | meta.pagination.page | integer | không | envelope | Trang hiện tại. |
| 13 | meta.pagination.per_page | integer | không | envelope | JSON name là `per_page`. |
| 14 | meta.pagination.total_items | integer | không | envelope | JSON name là `total_items`. |
| 15 | meta.pagination.total_pages | integer | không | envelope | JSON name là `total_pages`. |
| 16 | meta.pagination.has_next | boolean | không | envelope | JSON name là `has_next`. |
| 17 | meta.pagination.has_prev | boolean | không | envelope | JSON name là `has_prev`. |
| 18 | errors | array | có | envelope | Null khi thành công. Key vẫn có vì `ApiResponse` dùng `JsonInclude.ALWAYS`. |
| 19 | errors[].field | string | không | envelope | Có khi handler validation trả `ApiErrorDetail`. |
| 20 | errors[].code | string | không | envelope | Mã chi tiết trong `errors`, không phải `meta.error_code`. |
| 21 | errors[].message | string | không | envelope | Message chi tiết. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| 200 | null | Thành công. `meta.error_code` null. |
| 400 | ERR_BAD_REQUEST | `GlobalExceptionHandler` map `MethodArgumentTypeMismatchException` và `IllegalArgumentException`. |
| 404 | POI_NOT_FOUND | `GlobalExceptionHandler` map `ResourceNotFoundException`. |
| 409 | STATE_CONFLICT | `GlobalExceptionHandler` map `IllegalStateException`. |
| 422 | ERR_VALIDATION_FAILED | `GlobalExceptionHandler` map các exception validation. Message `Validation failed`. |
| 500 | INTERNAL_SERVER_ERROR | `GlobalExceptionHandler` map `Exception` còn lại. |
| 401 | không có | không có trong code |
| 403 | không có | không có trong code |
| 429 | không có | không có trong code |

## Sample request

```http
GET /api/v1/example/items/11111111-1111-1111-1111-111111111111?lang=vi HTTP/1.1
Accept-Language: vi
```

## Sample response

```json
{
  "success": true,
  "code": 200,
  "message": "Example retrieved successfully",
  "data": [
    {
      "id": "11111111-1111-1111-1111-111111111111"
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
