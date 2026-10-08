# Quyết định

## Giả định còn lại

- `notebookId` `2baecfc9-a8a3-4905-965f-f16eb6244fee` vẫn trỏ notebook partner trên Fabric. Task này không đổi GUID.
- Timeout activity `0.12:00:00` là 12 giờ.
- ForEach `isSequential = true`. Activity notebook không đọc `item()`; tham số gắn cứng `partner_raw_data`.

## Sai lệch so với kiến trúc

- Không có. Không qua architecture gate.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| CTX-1 | P2 | fixed | Tài liệu khoá và MERGE cạnh viết lại theo `NB_LIB_TRANSFORM_SLV_GLD.ipynb`: hết hạn bằng `lock_at` + timeout của run đang xét; MERGE cạnh không lùi version cùng table id và không có `EXISTS`. | Vá `LOCK_EXPIRES_AT` trong notebook là việc khác |
| CTX-2 | P2 | fixed | Giữ JSON pipeline, đổi tên activity, tài liệu mô tả đúng ForEach → If_HasWork và không có Switch. | Thêm activity 3rd-party khi có thiết kế pipeline mới |

## Cổng review

`python scripts/vv.py run-gate 20261008-align-context-pipeline` dừng vì máy không có Codex CLI (`codex` không có trên PATH). `specialist_review` vẫn `pending`. Chưa merge.

## Quyết định của người dùng

- Đổi tên activity, không đổi notebook GUID hay tham số.
- Chưa deploy pipeline lên Fabric.
