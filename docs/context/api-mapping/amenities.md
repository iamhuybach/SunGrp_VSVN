# GET /api/v1/pois/{poi_id}/amenities

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Truy vấn tiện ích của một POI theo nhóm. Chỉ dòng `apps.srv_poi_amenity.deleted_at` null, và bỏ dòng `amenity_raw` chứa `json_type`. Không kiểm tra `apps.srv_poi_info`. |
| Method | GET |
| Endpoint | /api/v1/pois/{poi_id}/amenities |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | X-Request-Id | string | không | `RequestIdFilter` đọc header này, hoặc `X-Request-ID`, ghi vào `meta.trace_id`. Thiếu thì server tạo UUID. Endpoint này không đọc `Accept-Language`. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | poi_id | string | có | path. Khóa đọc `apps.srv_poi_amenity.poi_id`. Không có query `lang`. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | `true` khi HTTP 200. |
| 2 | code | integer | có | envelope | Số HTTP trong body. Thành công là `200`. |
| 3 | message | string | có | envelope | Thành công: `POI amenities retrieved successfully`. |
| 4 | data | array | có | envelope | Danh sách `PoiAmenityGroupResponse`. Rỗng khi không còn dòng amenity hợp lệ. |
| 5 | data[].amenity_group | string | có | apps.srv_poi_amenity.amenity_group | Khóa nhóm. Không fallback `GENERAL`. |
| 6 | data[].items | array | có | không có cột | Các dòng trong nhóm, sắp theo `amenity_code` rồi `amenity_raw`. |
| 7 | data[].items[].amenity_code | string | có | apps.srv_poi_amenity.amenity | Đúng cột `amenity`. Không fallback `amenity_raw`. |
| 8 | data[].items[].service_flags | string | có | apps.srv_poi_amenity.service_flags | Đúng cột `service_flags`, không lấy `amenity_vi`. Có thể null. |
| 9 | meta | object | có | envelope | |
| 10 | meta.timestamp | string | có | envelope | ISO-8601 UTC. |
| 11 | meta.trace_id | string | có | envelope | Từ `X-Request-Id` hoặc UUID server tạo. |
| 12 | meta.error_code | string | không | envelope | Null khi thành công, key bị bỏ. Khi lỗi là chuỗi ở bảng Status code. |
| 13 | meta.pagination | object | không | envelope | `success` không gắn pagination. Null nên key bị bỏ. |
| 14 | errors | array | có | envelope | Null khi thành công. |
| 15 | errors[].field | string | không | envelope | Có khi HTTP 422. |
| 16 | errors[].code | string | không | envelope | Mã field error hoặc tên constraint, viết hoa. Không phải `meta.error_code`. |
| 17 | errors[].message | string | không | envelope | Message validation. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| 200 | null | Truy vấn thành công. `meta.error_code` null. |
| 400 | ERR_BAD_REQUEST | Handler map `MethodArgumentTypeMismatchException` và `IllegalArgumentException`. `errors` null. |
| 404 | không có | Amenities không trả 404 khi thiếu `srv_poi_info`. |
| 409 | STATE_CONFLICT | Handler map `IllegalStateException`. Message là message của exception. |
| 422 | ERR_VALIDATION_FAILED | Handler map các exception validation. Message `Validation failed`. Method này không gắn `@Min` `@Max`. |
| 500 | INTERNAL_SERVER_ERROR | Handler map `Exception` còn lại. Message `An unexpected error occurred. Please contact support with the trace ID.` |
| 401 | không có | không có trong code |
| 403 | không có | không có trong code |
| 429 | không có | không có trong code |

## Sample request

```http
GET /api/v1/pois/10b414f0-1089-8014-a0a1-612cda96cdc5/amenities HTTP/1.1
X-Request-Id: 22222222-2222-2222-2222-222222222222
```

## Sample response

Lấy từ Dev ngày 2026-11-11.

```json
{
  "success": true,
  "code": 200,
  "message": "POI amenities retrieved successfully",
  "data": [
    {
      "amenity_group": "accessibility",
      "items": [
        {
          "amenity_code": "accessible_parking",
          "service_flags": "Accessibility"
        },
        {
          "amenity_code": "wheelchair_accessible_entrance",
          "service_flags": "Accessibility"
        },
        {
          "amenity_code": "wheelchair_accessible_restroom",
          "service_flags": "Accessibility"
        },
        {
          "amenity_code": "wheelchair_accessible_seating",
          "service_flags": "Accessibility"
        }
      ]
    },
    {
      "amenity_group": "general_amenities",
      "items": [
        {
          "amenity_code": "free_street_parking",
          "service_flags": "Parking"
        },
        {
          "amenity_code": "good_for_children",
          "service_flags": "Suitability"
        },
        {
          "amenity_code": "outdoor_seating",
          "service_flags": "Food/service"
        },
        {
          "amenity_code": "parking",
          "service_flags": "Parking"
        },
        {
          "amenity_code": "restroom",
          "service_flags": "Suitability"
        }
      ]
    }
  ],
  "meta": {
    "timestamp": "2026-11-11T07:00:33.285893900Z",
    "trace_id": "22222222-2222-2222-2222-222222222222"
  },
  "errors": null
}
```
