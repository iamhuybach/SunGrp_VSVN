# GET /api/v1/pois/{poi_id}/experiences

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Tối đa 3 block trải nghiệm của POI (tiêu đề, mô tả, khóa icon) cho Section [Trải nghiệm] của POI Detail. |
| Method | GET |
| Endpoint | /api/v1/pois/{poi_id}/experiences |

## Request header

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | Authorization | string | có | Bearer token service-to-service của BE |
| 2 | Accept-Language | string | không | Dùng khi query `lang` trống. Cả hai trống thì `vi`. |
| 3 | X-Request-Id | string | không | Mã định danh request |

## Request param

| Stt | Field | Type | Required | Description |
|---|---|---|---|---|
| 1 | poi_id | string | có | path. ID của POI |
| 2 | lang | string | không | query. Ưu tiên hơn `Accept-Language`. Rỗng thì fallback `vi`. Bản dịch lấy `apps.srv_poi_multi_lang` theo lang đó, thiếu thì fallback `vi`. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | code | integer | có | không có cột | `0` = success |
| 2 | message | string | có | không có cột | `success` hoặc mô tả lỗi |
| 3 | data | object | có | không có cột | Không có count |
| 4 | data.items | array | có | `apps.srv_poi_multi_lang.experience` | Tối đa 3 phần tử |
| 5 | data.items.title | string | có | `apps.srv_poi_multi_lang.experience.title` | Tiêu đề trải nghiệm, tối đa 50 ký tự |
| 6 | data.items.description | string | có | `apps.srv_poi_multi_lang.experience.description` | Mô tả trải nghiệm, tối đa 150 ký tự |
| 7 | data.items.source | string | có | `apps.srv_poi_multi_lang.source` | `partner` (usp đối tác khai báo) hoặc `ai_generated` |
| 8 | meta | object | có | envelope |  |
| 9 | meta.timestamp | integer | có | envelope | Unix seconds. Spec nguồn gọi `server_time`. |
| 10 | meta.trace_id | string | có | envelope | Từ `X-Request-Id`. Spec nguồn gọi `request_id`. |

## Status code

| HTTP | Code | Description |
|---|---|---|
| không có | không có | không có trong file nguồn |

## Sample request

```json
{
  "poi_id": "3f1a2b9c-5d6e-4f70-8a91-b2c3d4e5f601"
}
```

## Sample response

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "title": "Tham quan kiến trúc Pháp cổ",
        "description": "Chiêm ngưỡng mặt tiền và sảnh chính xây từ đầu thế kỷ 20.",
        "source": "ai_generated"
      },
      {
        "title": "Xem biểu diễn nghệ thuật",
        "description": "Thưởng thức nhạc kịch, hòa nhạc và ballet theo lịch diễn trong tháng.",
        "source": "ai_generated"
      },
      {
        "title": "Chụp ảnh quanh quảng trường",
        "description": "Quảng trường trước nhà hát đẹp nhất vào buổi tối khi đèn được bật.",
        "source": "ai_generated"
      }
    ]
  },
  "meta": {
    "timestamp": 1791947160,
    "trace_id": "9f1c1e2a-7a1b-4e34-9b7f-0a9d3b2c1d45"
  }
}
```
