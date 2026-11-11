# GET /api/v1/pois/{poi_id}/gallery

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Ảnh đang hoạt động của một POI. Không kiểm tra POI có trong `apps.srv_poi_info`. POI không có ảnh trả `data` rỗng và `total_items` 0. Sắp `apps.srv_poi_media_gallery.display_order` tăng dần, null cuối, rồi `apps.srv_poi_media_gallery.media_id` tăng dần. |
| Method | GET |
| Endpoint | /api/v1/pois/{poi_id}/gallery |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | X-Request-Id | string | không | Ghi vào `meta.trace_id`. Thiếu thì server tạo UUID. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | poi_id | string | có | path. Lọc `apps.srv_poi_media_gallery.poi_id`. |
| 2 | page | integer | không | query. Mặc định `0`. `@Min(0)`. |
| 3 | size | integer | không | query. Mặc định `20`. `@Min(1)` `@Max(100)`. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | `true` khi HTTP 200. |
| 2 | code | integer | có | envelope | Thành công là `200`. |
| 3 | message | string | có | envelope | `POI gallery retrieved successfully`. |
| 4 | data | array | có | envelope | Chỉ ảnh `apps.srv_poi_media_gallery.is_active` true và `apps.srv_poi_media_gallery.deleted_at` null. |
| 5 | data[].id | string | có | apps.srv_poi_media_gallery.media_id | |
| 6 | data[].file_key | string | có | apps.srv_poi_media_gallery.blob_url | Giữ nguyên, kể cả null. |
| 7 | data[].display_order | integer | có | apps.srv_poi_media_gallery.display_order | Có thể null. |
| 8 | meta | object | có | envelope | |
| 9 | meta.timestamp | string | có | envelope | ISO-8601 UTC. |
| 10 | meta.trace_id | string | có | envelope | |
| 11 | meta.pagination | object | có | envelope | |
| 12 | meta.pagination.type | string | có | envelope | `offset`. |
| 13 | meta.pagination.page | integer | có | envelope | |
| 14 | meta.pagination.per_page | integer | có | envelope | |
| 15 | meta.pagination.total_items | integer | có | envelope | |
| 16 | meta.pagination.total_pages | integer | có | envelope | |
| 17 | meta.pagination.has_next | boolean | có | envelope | |
| 18 | meta.pagination.has_prev | boolean | có | envelope | |
| 19 | errors | array | có | envelope | Null khi thành công. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| 200 | null | Thành công, kể cả POI không tồn tại. HTTP 404 không xảy ra. |
| 422 | ERR_VALIDATION_FAILED | `page` hoặc `size` ngoài khoảng. |
| 500 | INTERNAL_SERVER_ERROR | Lỗi không phân loại. |

## Sample request

```http
GET /api/v1/pois/a3e34aab-af1d-eed9-9e38-87e5c18265b3/gallery?page=0&size=2 HTTP/1.1
X-Request-Id: 22222222-2222-2222-2222-222222222222
```

## Sample response

Lấy từ Dev ngày 2026-11-11.

```json
{
  "success": true,
  "code": 200,
  "message": "POI gallery retrieved successfully",
  "data": [
    {
      "id": "00f03cf65bb60964219eabd16e50e79921d32dc5cea2753e5ff4b53e7f2d392d",
      "file_key": "partner_biz_service%2F2026%2F04%2F10%2F94fc8884-beca-4f60-92bf-5f3cc8277a00_dulichtamlinh.jpg",
      "display_order": 0
    },
    {
      "id": "ece3f8bb8f12d3d5f79e015b8871c95a2b84b4ea5dde07d267b2737d39207f3e",
      "file_key": "partner_biz_service%2F2026%2F04%2F10%2F8deb6e9e-aa58-417d-ae2a-780f78b51e97_dulichque.jpg",
      "display_order": 1
    }
  ],
  "meta": {
    "timestamp": "2026-11-11T06:59:22.899341200Z",
    "trace_id": "22222222-2222-2222-2222-222222222222",
    "pagination": {
      "type": "offset",
      "page": 0,
      "per_page": 2,
      "total_items": 3,
      "total_pages": 2,
      "has_next": true,
      "has_prev": false
    }
  },
  "errors": null
}
```
