# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Selector poi_name hoặc ids | `poi_name` và `ids` là hai cách chọn POI. Không dùng `poi_name` để lọc giao với `ids`. Chỉ `ids`: chọn theo id, không có vị từ tên. Chỉ `poi_name`: chọn theo tên, không bắt buộc `ids`. Có cả hai: hợp (union), không giao (intersection). Không có selector nào: 422. `poi_name` vẫn một chuỗi, tối đa 128, khớp chứa không phân biệt hoa thường, escape `%`, `_` và `\`. Query `poi_name` không lọc. `GET` và các query còn lại không đổi. | `request.md` Yêu cầu nguyên văn | 2026-11-26 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Chưa có.

## Lịch sử quyết định

- 2026-11-26 D-1: người dùng thu hồi AND của task `20261126-practical-info-poi-name-body`. Body query bằng `poi_name` hoặc `ids`. Có cả hai thì union. Architecture bắt buộc theo mẫu A20. Evidence không bắt buộc vì quy tắc khớp tên đã có trong mapping và `containsPattern`.
