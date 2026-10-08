# Quyết định

## Giả định còn lại

- File người dùng gửi là bản nguồn cần lưu trong repo, giữ nguyên nội dung.
- Notebook đặt ở `notebooks/`, pipeline ARM template và `manifest.json` đặt cùng thư mục `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/`.
- Chưa chuyển sang định dạng Fabric Git (`.Notebook/notebook-content.py`, `.DataPipeline/pipeline-content.json`). Việc đó là thay đổi định dạng, ngoài phạm vi yêu cầu thêm source.

## Sai lệch so với kiến trúc

- Không có. Task không yêu cầu architecture gate.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Chưa có. Người dùng là người merge.
