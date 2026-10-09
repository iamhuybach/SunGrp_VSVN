# Quyết định

## Giả định còn lại

- Hợp đồng kết thúc chỉ là chỉ dẫn cho Main. Repository không có kiểm tra tự động nào ép được nội dung câu trả lời chat. Muốn kiểm chứng thì đọc câu trả lời cuối của lượt sau.
- Tiêu đề bốn mục (`Đã làm`, `Bạn cần chạy`, `Agent đang chờ`, `Kết thúc`) là chuỗi đầu ra cố định. Vì vậy chúng giữ tiếng Việt ngay trong rule tiếng Anh.

## Sai lệch so với kiến trúc

- Không có. Task không cần kiến trúc.

## Đối chiếu với `AGENTS.md`

- §6 workflow: dừng ở evidence, runtime và quyết định người dùng là đúng luồng hiện có. Hợp đồng mới chỉ quy định câu trả lời lúc dừng, không đổi thứ tự gate.
- §6 quy tắc 10 và §11: chỉ người dùng commit, merge và accept risk. Vì vậy `commit` và `accept-risk` là yêu cầu trong `Agent đang chờ`, Main không tự làm.
- §8: bước Fabric DEV vẫn do người dùng chạy. Giới hạn 50 dòng, không dữ liệu cá nhân, không secret được nhắc lại trong mục `Bạn cần chạy`.
- Rule mục Completion: `runtime-runbook.md` vẫn là bản đầy đủ bằng tiếng Việt. Câu trả lời chat là bản rút gọn, gồm rerun, kiểm tra log control, rollback và forward recovery khi runbook có các mục đó.
- Không sửa `AGENTS.md`. File này dùng chung cho Claude và Codex, còn hợp đồng kết thúc chỉ áp dụng cho Main. Không có mâu thuẫn cần sửa.

## Không thêm skill mới

- Skill `vsvn-task-workflow` đã có mục `Build the closeout`. Mô tả skill có thêm trường hợp "chạy task này thế nào" cho `task-id` đã có. Rule always-apply vẫn là nguồn bắt buộc. Vì vậy không thêm skill riêng.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Không có finding. Không cần reviewer vì rủi ro thấp và không có thay đổi Spark, SQL, pipeline hay trạng thái bền.

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-09: người dùng yêu cầu thay đổi agent-system này và chỉ định rule `00-main-orchestrator.mdc` cùng skill `vsvn-task-workflow` là chỗ sửa ưu tiên.
