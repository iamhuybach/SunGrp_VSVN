# Review round 1 — FIX_REQUIRED

Model đã xác nhận: `gpt-5.6-sol`, reasoning `medium`.

## P1 findings

### API-001 — `poi_name` dạng scalar không phải chuỗi có thể được chấp nhận

- Vị trí: `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PracticalInfoSearchRequest.java:15`
- Test thiếu bao phủ: `services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/PoiControllerIntegrationTest.java:612`
- Ảnh hưởng: trường `String poiName` đang phụ thuộc vào scalar coercion mặc định của Jackson. JSON number hoặc boolean như `"poi_name":123` hay `"poi_name":true` có thể bị chuyển thành chuỗi và đi tới service, trái invariant yêu cầu mọi `poi_name` không phải JSON string hoặc `null` phải trả HTTP 400.
- Cách sửa: áp dụng deserialization string-or-null riêng cho `poi_name`, không thay đổi coercion toàn cục. Bổ sung test cho number, boolean, array và object; xác nhận HTTP 400 với error envelope dùng chung và service không được gọi. Cập nhật mapping document để nói rõ mọi giá trị không phải chuỗi đều trả 400.

## Specialist results

- `api-contract-reviewer`: `FIX_REQUIRED` với `API-001`.
- `app-security-reviewer`: `PASS`. Finding sơ bộ về matrix parameter đã được rút lại vì Spring Security dùng `StrictHttpFirewall` mặc định và repository không cấu hình custom `HttpFirewall`; đường dẫn chứa dấu chấm phẩy bị chặn trước filter/MVC.

Không chạy `risk-gate` vì `task-state.yaml` đánh dấu gate này là `not_required`. Không có file nào được chỉnh sửa.
