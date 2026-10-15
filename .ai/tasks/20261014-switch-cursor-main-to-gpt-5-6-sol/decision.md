# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| MODEL-001 | Main model tạm thời | Ngoại lệ `EXC-MAIN-GPT-20261014` đã được thu hồi; Main quay lại Grok 4.7, effort `medium`. | Yêu cầu người dùng | 2026-10-14 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Lịch sử quyết định

- Giữ `grok-4.7` làm baseline trong task template và validator để không làm sai lịch sử task cũ. Trong thời gian override, Main ghi `EXC-MAIN-GPT-20261014` vào task đang thực hiện và xác nhận model thực tế là `gpt-5.6-sol`.
- Đã cập nhật `AGENTS.md`, Always Apply rule, `SETUP.md` và prompt samples. `doctor`, task validation, `git diff --check` và local verification đều PASS.
- Người dùng yêu cầu quay lại Grok 4.7 Medium ngày 2026-10-14. Bốn file agent-system đã được khôi phục về baseline Grok; lịch sử thời gian dùng GPT vẫn được giữ trong artifact này.

## Quyết định của người dùng

- Chưa có.

## Lịch sử quyết định

- Chưa có.
