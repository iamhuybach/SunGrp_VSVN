# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Hợp đồng poi_name | Thu hồi. `poi_name` không phải bộ lọc AND trên `ids`. Hợp đồng đúng nằm ở task `20261126-practical-info-poi-name-or-ids`: body có thể query bằng `poi_name` hoặc `ids`. | Người dùng, 2026-11-26 | 2026-11-26 |
| D-2 | Kiểu JSON của poi_name | `poi_name` chỉ nhận chuỗi JSON hoặc `null`. Số, boolean, mảng và object trả HTTP 400 `ERR_BAD_REQUEST`. Deserializer gắn trên field, không đổi coercion toàn cục. | `reviews/round-1.md` API-001 | 2026-11-26 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- D-2: I9 trong `architecture.md` chỉ nêu mảng và object. API-001 yêu cầu mọi giá trị không phải chuỗi JSON cũng trả 400. Sửa bằng deserializer cục bộ trên `poi_name`, không đụng `PoiService`, repository, hay SQL.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| API-001 | P1 | fixed | `PracticalInfoNameDeserializer` chỉ nhận `VALUE_STRING`. Test number, boolean, array, object trả 400 `ERR_BAD_REQUEST` và không gọi service. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Chưa có.

## Lịch sử quyết định

- 2026-11-26 D-1: chốt diễn giải hợp đồng từ yêu cầu người dùng. Architecture bắt buộc theo mẫu A20 vì đổi hợp đồng HTTP. Evidence không bắt buộc vì quy tắc lọc đã có trong mapping và repository.
- 2026-11-26 D-2: xử lý API-001. Mở rộng I9: số và boolean cũng trả 400, cùng mảng và object.
- 2026-11-26 D-1 thu hồi: người dùng xác nhận `poi_name` phải query tương đương `ids`, không lọc từ `ids`. Task kế tiếp: `20261126-practical-info-poi-name-or-ids`.
