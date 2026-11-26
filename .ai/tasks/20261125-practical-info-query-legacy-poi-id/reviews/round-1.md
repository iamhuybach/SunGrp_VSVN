## Manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `api-contract-reviewer`, `app-security-reviewer`, `jpa-performance-reviewer`
- Risk gate: completed

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `API-001` — P1 — `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java:141`: OpenAPI của endpoint mới thiếu các response thực tế và dùng `List<Object>`, khiến client nhận contract không định kiểu và thiếu error schemas. Khắc phục bằng cách khai báo shared envelopes cho `200/400/401/415/422/500` và success schema/projection có kiểu rõ ràng.
- `SEC-001` — P1 — `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java:144`: Bean validation chạy sau khi Jackson materialize body không giới hạn byte, nên request xác thực quá lớn có thể gây áp lực heap trước khi bị từ chối. Khắc phục bằng giới hạn byte trước deserialization cho cả fixed-length và chunked body, kèm test oversized request.
- `JPA-001` — P1 — `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiIdResolver.java:37`: Resolver đưa tối đa 500 ID vào một repository `IN`, vi phạm giới hạn 100 ID mỗi repository call và tạo rủi ro hiệu năng. Khắc phục để mọi `IN` call không quá 100 ID nhưng vẫn giữ tổng số SQL không quá 5, đồng thời test cả hai invariant.

## Lower severity

P2: 1; P3: 0.
