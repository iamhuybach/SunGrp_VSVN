## Model and reviewer manifest

`gpt-5.6-sol`, reasoning `medium`. Đã chạy độc lập: `spark-runtime-reviewer`, `sql-data-reviewer`, `api-contract-reviewer`, `jpa-performance-reviewer`; `risk-gate` đã hoàn tất.

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `SPARK-SQL-001` — P1 — `notebooks/NB_SLV_POI_AMENITY.ipynb:235`: `COND_SCHEMA` có 9 cột nhưng tuple điều kiện có 10 giá trị sau khi thêm `amenity_en`, khiến `createDataFrame` lỗi trước Delta write. Thêm `amenity_en string` ngay sau `amenity string` và kiểm thử thứ tự/arity của schema.
- `API-002` — P1 — `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java:125`: endpoint danh sách amenities vẫn không phân trang, vi phạm quy tắc bắt buộc `size <= 100` trong service `AGENTS.md`. Dùng `Pageable`/`PageResponse` với giới hạn 100, hoặc xin ngoại lệ được người dùng phê duyệt và ghi nhận theo quy trình.

`API-001` bị loại: thay đổi response tại cùng path là quyết định D-01/D-02 đã được người dùng chốt.

## P2/P3

0.
