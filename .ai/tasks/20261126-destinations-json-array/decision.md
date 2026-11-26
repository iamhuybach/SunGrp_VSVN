# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | destinations là mảng | `destinations.id` và `destinations.name` là mảng chuỗi JSON. `null` hoặc chuỗi rỗng thành `null`. Chuỗi là mảng JSON thì parse. Không phải mảng JSON, hoặc phần tử không phải chuỗi JSON, thì field đó là `null` và request vẫn 200. Không xóa ký tự `\`. Không bịa phần tử. Compact và practical info dùng cùng hình. | `request.md` Yêu cầu nguyên văn | 2026-11-26 |

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

- 2026-11-26 D-1: parse text cột thành mảng. Giá trị hỏng thành `null`, không làm 500 cả trang. Architecture bắt buộc theo mẫu A20.
