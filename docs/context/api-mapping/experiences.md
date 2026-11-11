# GET /api/v1/pois/{poi_id}/experiences

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Tối đa 3 trải nghiệm. Không kiểm tra POI tồn tại. Đọc `apps.srv_poi_multi_lang` theo ngôn ngữ đã resolve rồi `vi`. Dùng hàng đầu tiên có mảng experience không rỗng. `source` của mọi phần tử là `apps.srv_poi_multi_lang.source_name` của hàng đó. |
| Method | GET |
| Endpoint | /api/v1/pois/{poi_id}/experiences |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | Accept-Language | string | không | Dùng khi không có query `lang`. Thiếu cả hai thì `vi`. |
| 2 | X-Request-Id | string | không | Ghi vào `meta.trace_id`. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | poi_id | string | có | path. Lọc `apps.srv_poi_multi_lang.poi_id`. |
| 2 | lang | string | không | query. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | `true` khi HTTP 200. |
| 2 | code | integer | có | envelope | Thành công là `200`. |
| 3 | message | string | có | envelope | `POI experiences retrieved successfully`. |
| 4 | data | object | có | envelope | |
| 5 | data.items | array | có | apps.srv_poi_multi_lang.experience | Mảng rỗng khi không có hàng, JSON null, JSON hỏng, hoặc không phải mảng. Bỏ phần tử không phải object và phần tử cả `title` lẫn `description` trống. |
| 6 | data.items[].title | string | có | apps.srv_poi_multi_lang.experience | Text trong object. Không phải text thì null. |
| 7 | data.items[].description | string | có | apps.srv_poi_multi_lang.experience | Text trong object. |
| 8 | data.items[].source | string | có | apps.srv_poi_multi_lang.source_name | Cùng một giá trị cho mọi phần tử của hàng được chọn. |
| 9 | meta | object | có | envelope | Không có `meta.pagination`. |
| 10 | meta.timestamp | string | có | envelope | |
| 11 | meta.trace_id | string | có | envelope | |
| 12 | errors | array | có | envelope | Null khi thành công. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| 200 | null | Thành công, kể cả `items` rỗng. HTTP 404 không xảy ra. JSON hỏng không trả HTTP 500. |
| 500 | INTERNAL_SERVER_ERROR | Lỗi không phân loại. |

## Sample request

```http
GET /api/v1/pois/00000000-0000-0000-0000-000000000001/experiences?lang=vi HTTP/1.1
X-Request-Id: 22222222-2222-2222-2222-222222222222
```

## Sample response

Lấy từ Dev ngày 2026-11-11.

```json
{
  "success": true,
  "code": 200,
  "message": "POI experiences retrieved successfully",
  "data": {
    "items": [
      {
        "title": "Di chuyển thuận tiện giữa các tỉnh",
        "description": "Xe khách phục vụ tuyến cố định giúp hành khách dễ dàng đi lại giữa Thanh Hóa và các khu vực khác.",
        "source": "google"
      },
      {
        "title": "Đặt vé nhanh chóng tại văn phòng",
        "description": "Khách có thể mua vé trực tiếp tại văn phòng, thuận tiện cho việc lên kế hoạch di chuyển.",
        "source": "google"
      },
      {
        "title": "Chuyến xe đúng giờ",
        "description": "Dịch vụ đảm bảo thời gian xuất phát đúng giờ, phù hợp với lịch trình của hành khách.",
        "source": "google"
      }
    ]
  },
  "meta": {
    "timestamp": "2026-11-11T06:59:23.326835800Z",
    "trace_id": "22222222-2222-2222-2222-222222222222"
  },
  "errors": null
}
```
