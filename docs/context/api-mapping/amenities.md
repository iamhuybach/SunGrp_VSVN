# GET /api/v1/pois/{poi_id}/amenities

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Truy vấn tiện ích của một POI theo nhóm. Chỉ dòng `apps.srv_poi_amenity.deleted_at` null, và bỏ dòng `amenity_raw` chứa `json_type`. POI phải còn trong `apps.srv_poi_info` với `deleted_at` null. |
| Method | GET |
| Endpoint | /api/v1/pois/{poi_id}/amenities |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | Accept-Language | string | không | Dùng khi query `lang` trống. `LanguageResolver` lấy tag đầu tiên, cắt subtag. Cả hai trống thì `vi`. Nhãn nhóm và nhãn item dùng map tiếng Anh khi lang resolve là `en`, các lang khác dùng map tiếng Việt. |
| 2 | X-Request-Id | string | không | `RequestIdFilter` đọc header này, hoặc `X-Request-ID`, ghi vào `meta.trace_id`. Thiếu thì server tạo UUID. |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | poi_id | string | có | path. `apps.srv_poi_info.poi_id`. |
| 2 | lang | string | không | query. Ưu tiên hơn `Accept-Language`. Rỗng thì fallback `vi`. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | success | boolean | có | envelope | `true` khi HTTP 200. |
| 2 | code | integer | có | envelope | Số HTTP trong body. Thành công là `200`. |
| 3 | message | string | có | envelope | Thành công: `POI amenities retrieved successfully`. |
| 4 | data | array | có | envelope | Danh sách `PoiAmenityGroupResponse`. Rỗng khi POI tồn tại mà không còn dòng hợp lệ. Null khi lỗi. |
| 5 | data[].amenity_group | string | có | apps.srv_poi_amenity.amenity_group | `amenity_group` null thì giá trị JSON là `GENERAL`. |
| 6 | data[].amenity_vi | string | có | không có cột | Nhãn nhóm. Lang `en` lấy `AMENITY_GROUP_LABELS_EN`, lang khác lấy `AMENITY_GROUP_LABELS_VI`. Không có trong map thì trả lại mã nhóm. Không lấy cột `amenity_vi`. |
| 7 | data[].items | array | có | không có cột | Các dòng trong nhóm. |
| 8 | data[].items[].amenity_code | string | có | apps.srv_poi_amenity.amenity; apps.srv_poi_amenity.amenity_raw | `amenity` khi khác blank, còn lại `amenity_raw`. |
| 9 | data[].items[].amenity_label | string | có | apps.srv_poi_amenity.amenity_vi; apps.srv_poi_amenity.amenity; apps.srv_poi_amenity.amenity_raw | Lang `en`: `amenity`, rồi `amenity_vi`, rồi `amenity_raw`. Lang khác: `amenity_vi`, rồi `amenity`, rồi `amenity_raw`. Bỏ qua giá trị blank. |
| 10 | data[].items[].service_flags | string | có | apps.srv_poi_amenity.service_flags | Giá trị có thể null. |
| 11 | meta | object | có | envelope | |
| 12 | meta.timestamp | string | có | envelope | ISO-8601 UTC. |
| 13 | meta.trace_id | string | có | envelope | Từ `X-Request-Id` hoặc UUID server tạo. |
| 14 | meta.error_code | string | không | envelope | Null khi thành công, key bị bỏ. Khi lỗi là chuỗi ở bảng Status code. |
| 15 | meta.pagination | object | không | envelope | `success` không gắn pagination. Null nên key bị bỏ. |
| 16 | errors | array | có | envelope | Null khi thành công. |
| 17 | errors[].field | string | không | envelope | Có khi HTTP 422. |
| 18 | errors[].code | string | không | envelope | Mã field error hoặc tên constraint, viết hoa. Không phải `meta.error_code`. |
| 19 | errors[].message | string | không | envelope | Message validation. |

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
GET /api/v1/pois/11111111-1111-1111-1111-111111111111/amenities?lang=vi HTTP/1.1
Accept-Language: vi
X-Request-Id: 22222222-2222-2222-2222-222222222222
```

## Sample response

```json
{
  "success": true,
  "code": 200,
  "message": "POI amenities retrieved successfully",
  "data": [
    {
      "amenity_group": "FACILITY",
      "amenity_vi": "Tiện nghi cơ sở",
      "items": [
        {
          "amenity_code": "ma_mau",
          "amenity_label": "Nhan mau",
          "service_flags": "mau"
        }
      ]
    }
  ],
  "meta": {
    "timestamp": "2026-11-09T04:28:00Z",
    "trace_id": "22222222-2222-2222-2222-222222222222"
  },
  "errors": null
}
```
