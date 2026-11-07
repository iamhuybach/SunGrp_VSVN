## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium` — khớp yêu cầu.
- Specialist reviewers: không có theo manifest `[]`.
- `risk-gate`: đã hoàn tất.

## Gate verdict: `USER_DECISION`

Các mâu thuẫn vòng 2 tại `API-GAPS.md:177,188` và `DESIGN-AND-PLAN.md:159` đã được sửa thống nhất. Tuy nhiên, rủi ro đã chấp nhận vẫn cần bằng chứng network isolation trước khi mở traffic.

## P0/P1

- **GATE-001 — P1 — `docs/poi-serving-api/API-GAPS.md:39`**: Nếu gọi trực tiếp cổng 8080, request sẽ bỏ qua API Management trong khi service không xác thực token hoặc allowlist. **Fix:** Chỉ cho phép ingress từ API Management, chặn truy cập trực tiếp tới 8080 và xác minh cấu hình trước khi mở traffic.

## P2/P3

- P2: 0; P3: 0.

**Probe:** Từ nguồn không phải gateway, gọi `<service>:8080` phải timeout hoặc bị từ chối; qua API Management phải thành công với token hợp lệ và trả 401/403 với token hoặc caller không hợp lệ.
