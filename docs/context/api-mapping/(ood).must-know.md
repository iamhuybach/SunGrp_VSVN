# GET /api/v1/pois/{poi_id}/general-information

## Tổng quan

| Mục | Giá trị |
|---|---|
| Description | Mục Thông tin cần biết: giờ hoạt động, thời lượng trải nghiệm, chi phí tham khảo, mùa đẹp nhất, theo từng loại hình. |
| Method | GET |
| Endpoint | /api/v1/pois/{poi_id}/general-information |
| Trạng thái | (ood) |
| Thay bằng | /api/v1/pois/{poi_id}/practical_info |

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
| 2 | lang | string | không | query. Ưu tiên hơn `Accept-Language`. Rỗng thì fallback `vi`. Bản dịch lấy `gld_srv_poi_multi_lang` theo lang đó, thiếu thì fallback `vi`. |

## Response

| Stt | Field | Type | Required | Source Field | Description |
|---|---|---|---|---|---|
| 1 | code | integer | có | không có cột | `0` = success |
| 2 | message | string | có | không có cột | `success` hoặc mô tả lỗi |
| 3 | data | object | có | không có cột | POI chưa có dữ liệu nào thì là object rỗng |
| 4 | data.business_sector | string | có | `gld_srv_poi_info.business_sector` | Quyết định bộ nhãn hiển thị |
| 5 | data.time_to_spend | object | không | `gld_srv_poi_multi_lang.time_to_spend` |  |
| 6 | data.cost | object | không | `gld_srv_poi_multi_lang.cost` |  |
| 7 | data.best_time | object | không | `gld_srv_poi_multi_lang.best_time` |  |
| 8 | data.operating_hours | object | không | `apps.srv_poi_info.operating_hours` |  |
| 9 | data.operating_hours.value.day_of_week | integer | có | `apps.srv_poi_info.operating_hours.day_of_week` | 1 = Thứ Hai … 7 = Chủ Nhật |
| 10 | data.operating_hours.value.open_time | string | không | `apps.srv_poi_info.operating_hours.open_time` | HH:mm |
| 11 | data.operating_hours.value.close_time | string | không | `apps.srv_poi_info.operating_hours.close_time` | HH:mm |
| 12 | data.operating_hours.value.is_open_all_day | boolean | có | `apps.srv_poi_info.operating_hours.is_open_all_day` |  |
| 13 | data.operating_hours.value.is_closed | boolean | có | `apps.srv_poi_info.operating_hours.is_closed` |  |
| 14 | data.holiday_exceptions.date | string | có | `apps.srv_poi_info.holiday_exceptions.date` | YYYY-MM-DD |
| 15 | data.holiday_exceptions.name | string | không | `apps.srv_poi_info.holiday_exceptions.title` | Tên ngày lễ |
| 16 | data.holiday_exceptions.value | string | có | `apps.srv_poi_info.holiday_exceptions.value` | Giờ mở cửa dạng hiển thị hoặc "Đóng cửa" |
| 17 | data.holiday_exceptions.open_time | string | không | `apps.srv_poi_info.holiday_exceptions.open_time` | HH:mm |
| 18 | data.holiday_exceptions.close_time | string | không | `apps.srv_poi_info.holiday_exceptions.close_time` | HH:mm |
| 19 | data.holiday_exceptions.is_open_all_day | boolean | có | `apps.srv_poi_info.holiday_exceptions.is_open_all_day` |  |
| 20 | data.holiday_exceptions.is_closed | boolean | có | `apps.srv_poi_info.holiday_exceptions.is_closed` |  |
| 21 | meta | object | có | envelope |  |
| 22 | meta.timestamp | integer | có | envelope | Spec nguồn gọi `server_time`. |
| 23 | meta.trace_id | string | có | envelope | Từ `X-Request-Id`. Spec nguồn gọi `request_id`. |

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
    "business_sector": "attraction",
    "time_to_spend": { "label": "Thời gian tham quan", "value": "1 - 2 giờ" },
    "cost": { "label": "Chi phí tham khảo", "value": "120.000đ" },
    "best_time": { "label": "Mùa đẹp nhất", "value": "Tháng 10 - Tháng 4" },
    "operating_hours": {
      "label": "Giờ tham quan",
      "timezone": "Asia/Ho_Chi_Minh",
      "value": [
        { "day_of_week": 1, "label": "Thứ Hai", "value": "08:00 - 17:00", "open_time": "08:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false },
        { "day_of_week": 2, "label": "Thứ Ba", "value": "08:00 - 17:00", "open_time": "08:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false },
        { "day_of_week": 3, "label": "Thứ Tư", "value": "08:00 - 17:00", "open_time": "08:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false },
        { "day_of_week": 4, "label": "Thứ Năm", "value": "08:00 - 17:00", "open_time": "08:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false },
        { "day_of_week": 5, "label": "Thứ Sáu", "value": "08:00 - 17:00", "open_time": "08:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false },
        { "day_of_week": 6, "label": "Thứ Bảy", "value": "08:00 - 17:00", "open_time": "08:00", "close_time": "17:00", "is_open_all_day": false, "is_closed": false },
        { "day_of_week": 7, "label": "Chủ Nhật", "value": "Đóng cửa", "subvalue": "Nghỉ bảo trì", "is_open_all_day": false, "is_closed": true }
      ]
    },
    "holiday_exceptions": [
      { "date": "2026-11-20", "name": "Ngày Nhà giáo Việt Nam", "value": "09:00 - 15:00", "open_time": "09:00", "close_time": "15:00", "is_open_all_day": false, "is_closed": false },
      { "date": "2027-02-06", "name": "Mùng 1 Tết Nguyên Đán", "value": "Đóng cửa", "is_open_all_day": false, "is_closed": true }
    ]
  },
  "meta": {
    "timestamp": 1791947160,
    "trace_id": "9f1c1e2a-7a1b-4e34-9b7f-0a9d3b2c1d45"
  }
}
```
