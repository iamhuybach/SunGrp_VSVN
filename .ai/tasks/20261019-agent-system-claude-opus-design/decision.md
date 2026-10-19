# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| EX-20261019-CLAUDE-DESIGN-HIGH | Effort Claude cho phân tích và đề xuất | Trừ architecture và đề xuất giải pháp vẫn là effort high, còn lại Phân tích nghiệp vụ, phân tích bài toán và thiết kế model chạy trên Claude Code claude-opus-5-5 effort medium. | user query | 2026-10-20 |
| D1 | Tách effort author | Giữ `models.author` cho lane runbook (effort `medium`) và thêm `models.author_proposal` tùy chọn (effort `high`). | architecture.md §Decisions and alternatives | 2026-10-19 |
| D2 | Phân tích bài toán | Phân tích bài toán là `run-author --kind analysis` trên lane `models.author`, effort `medium`, ghi `problem-analysis.md`. | architecture.md §D-A | 2026-10-20 |
| D-B | Thiết kế model | Thiết kế model là `run-author --kind model` trên lane `models.author`, effort `medium`, ghi `model-design.md`. Architect effort `high` đọc file đó và không viết thiết kế model. | architecture.md §D-B | 2026-10-20 |
| D-C | Cổng model design | Signal `data_model_change` khiến `run-gate` từ chối gọi Architect khi `model-design.md` thiếu hoặc rỗng. | architecture.md §D-C | 2026-10-20 |
| D3 | Effort phân tích nghiệp vụ | `requirements-analyst` dùng `claude-opus-5-5` effort `medium`. Không hạ `.claude/settings.json` vì lane Architect giữ effort `high`. | user query | 2026-10-20 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- 2026-10-19: `materialize` từ chối mọi path có tên `task-state.yaml`, gồm `.ai/tasks/_template/task-state.yaml`. Main thu hẹp guard trong `scripts/vv.py`: vẫn cấm `task-state.yaml` của từng task, cho phép đúng `_template/task-state.yaml`. Sau đó chạy `python scripts/vv.py materialize 20261019-agent-system-claude-opus-design --write`. Nội dung FILE block không đổi.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-19: Phân tích nghiệp vụ, phân tích bài toán, đề xuất giải pháp và thiết kế model do Claude Code, model claude-opus-5-5, effort high, thực hiện.
- Author kind `runbook` giữ `claude-opus-5-5` effort `medium`.
- Main Grok 4.7 Medium vẫn là người duy nhất sửa source, notebook, pipeline, schema và `task-state.yaml`.
- Review giữ `gpt-5.6-sol` effort `medium`.
- `requirements-analyst` không viết `architecture.md` và không thay Architect.
- Thiết kế model nằm trong `architecture.md` do Architect viết qua `run-gate`.
- 2026-10-20: Trừ architecture và đề xuất giải pháp vẫn là effort high, còn lại Phân tích nghiệp vụ, phân tích bài toán và thiết kế model chạy trên Claude Code claude-opus-5-5 effort medium.

## Lịch sử quyết định

- 2026-10-19: người dùng duyệt exception `EX-20261019-CLAUDE-DESIGN-HIGH` (`kind: model_override`, `role: author`, `model: claude-opus-5-5`, `effort: high`, `runtime: Claude Code`). Phạm vi: phân tích nghiệp vụ, phân tích bài toán và đề xuất giải pháp chuyển sang Claude Code `claude-opus-5-5` effort `high`; thiết kế model giữ lane Architect, cùng model và effort `high`. Runbook author giữ effort `medium`.
- 2026-10-19: D1 giữ `models.author` cho runbook effort `medium` và thêm `models.author_proposal` effort `high`. D2 đặt phân tích bài toán vào `proposal.md` qua `run-author --kind proposal`. D3 đặt `requirements-analyst` effort `high` và không đổi `.claude/settings.json`.
- 2026-10-20: người dùng sửa exception `EX-20261019-CLAUDE-DESIGN-HIGH`. Architecture và đề xuất giải pháp giữ effort `high`. Phân tích nghiệp vụ, phân tích bài toán và thiết kế model chuyển sang Claude Code `claude-opus-5-5` effort `medium`. D1 vẫn tách runbook `medium` và đề xuất giải pháp `high`. D2 và D3 ngày 2026-10-19 hết hiệu lực.
- 2026-10-20: Architect chọn D-A kind `analysis`, D-B kind `model`, D-C signal `data_model_change`. Cả hai kind dùng lane `models.author` effort `medium`.
