# GET /api/v1/pois/{poi_id}/gallery

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Lấy thư viện ảnh của một POI, sắp `display_order` tăng dần. Chỉ media có `deleted_at` null và `is_active` null hoặc true. POI phải còn trong `apps.srv_poi_info` với `deleted_at` null. |
| Method | GET |
| Endpoint | /api/v1/pois/{poi_id}/gallery |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | X-Request-Id | string | không | `RequestIdFilter` đọc header này, hoặc `X-Request-ID`, ghi vào `meta.trace_id`. Thiếu thì server tạo UUID. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | poi_id | string | có | path. `apps.srv_poi_info.poi_id`. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | `true` khi HTTP 200. |
| 2 | code | integer | có | envelope | Số HTTP trong body. Thành công là `200`. |
| 3 | message | string | có | envelope | Thành công: `POI gallery retrieved successfully`. |
| 4 | data | array | có | envelope | Danh sách `PoiGalleryItemResponse`. Rỗng khi POI tồn tại mà không có ảnh. Null khi lỗi. |
| 5 | data[].id | string | có | apps.srv_poi_media_gallery.media_id | JSON name `id`. |
| 6 | data[].file_key | string | có | apps.srv_poi_media_gallery.blob_url; apps.srv_poi_media_gallery.photo_api_uri | `blob_url` khi khác blank, còn lại `photo_api_uri`. |
| 7 | data[].width | integer | có | apps.srv_poi_media_gallery.width_px | Giá trị có thể null. |
| 8 | data[].height | integer | có | apps.srv_poi_media_gallery.height_px | Giá trị có thể null. |
| 9 | data[].mime_type | string | có | không có cột | Suy từ đuôi `file_key`: `.png`, `.webp`, `.gif`, còn lại `image/jpeg`. |
| 10 | data[].blur_hash | string | có | không có cột | Code luôn gán null. Key vẫn có. |
| 11 | data[].display_order | integer | có | apps.srv_poi_media_gallery.display_order | Giá trị có thể null. |
| 12 | meta | object | có | envelope | |
| 13 | meta.timestamp | string | có | envelope | ISO-8601 UTC. |
| 14 | meta.trace_id | string | có | envelope | Từ `X-Request-Id` hoặc UUID server tạo. |
| 15 | meta.error_code | string | không | envelope | Null khi thành công, key bị bỏ. Khi lỗi là chuỗi ở bảng Status code. |
| 16 | meta.pagination | object | không | envelope | `success` không gắn pagination. Null nên key bị bỏ. |
| 17 | errors | array | có | envelope | Null khi thành công. |
| 18 | errors[].field | string | không | envelope | Có khi HTTP 422. |
| 19 | errors[].code | string | không | envelope | Mã field error hoặc tên constraint, viết hoa. Không phải `meta.error_code`. |
| 20 | errors[].message | string | không | envelope | Message validation. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| 200 | null | Truy vấn thành công. `meta.error_code` null. |
| 400 | ERR_BAD_REQUEST | Handler map `MethodArgumentTypeMismatchException` và `IllegalArgumentException`. `errors` null. |
| 404 | POI_NOT_FOUND | `@ApiResponses` ghi không tìm thấy POI. `validatePoiExists` ném `ResourceNotFoundException` khi không có `apps.srv_poi_info.poi_id` với `deleted_at` null. Message `POI not found with id: ` cộng `poi_id`. |
| 409 | STATE_CONFLICT | Handler map `IllegalStateException`. Message là message của exception. |
| 422 | ERR_VALIDATION_FAILED | Handler map các exception validation. Message `Validation failed`. Method này không gắn `@Min` `@Max`. |
| 500 | INTERNAL_SERVER_ERROR | Handler map `Exception` còn lại. Message `An unexpected error occurred. Please contact support with the trace ID.` |
| 401 | không có | không có trong code |
| 403 | không có | không có trong code |
| 429 | không có | không có trong code |

## Sample request

```http
GET /api/v1/pois/11111111-1111-1111-1111-111111111111/gallery HTTP/1.1
X-Request-Id: 22222222-2222-2222-2222-222222222222
```

## Sample response

```json
{
  "success": true,
  "code": 200,
  "message": "POI gallery retrieved successfully",
  "data": [
    {
      "id": "33333333-3333-3333-3333-333333333333",
      "file_key": "https://cdn.example.invalid/mau.jpg",
      "width": 640,
      "height": 480,
      "mime_type": "image/jpeg",
      "blur_hash": null,
      "display_order": 1
    }
  ],
  "meta": {
    "timestamp": "2026-11-09T04:28:00Z",
    "trace_id": "22222222-2222-2222-2222-222222222222"
  },
  "errors": null
}
```
