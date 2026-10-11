# Quyết định

## Giả định còn lại

- Không có. Mẫu tài liệu bám `docs/context/` đã có trong repository. Chỗ context chưa nêu schema hoặc rule thì để trống hoặc ghi là thiếu evidence. Không suy diễn dữ liệu Fabric DEV.

## Sai lệch so với kiến trúc

- Lượt Codex theo lệnh `spawn` ở architecture round 1 không khởi tạo được agent con `requirements-reviewer` khi có `--ephemeral` (`no rollout found`). Báo cáo đã lưu là lượt Codex read-only dùng đúng `developer_instructions` của file reviewer, model CLI `gpt-5.6-sol`, effort `medium`. Header báo cáo đó ghi `gpt-5.6-sol` và `medium`. Không đổi `.codex/config.toml`.
- Architecture round 2 chọn cùng cách gọi trực tiếp đó. `codex` không có trên `PATH`. Main gọi đúng binary mà `scripts/agent_runner.py` tìm thấy: `C:\Users\bachnh\.vscode\extensions\openai.chatgpt-26.1007.21434-win32-x64\bin\windows-x86_64\codex.exe`. Cờ model, effort, sandbox và `--ephemeral` giữ như architecture.

## Xử lý findings

Architecture round 2 đã viết lại bốn file. Main chép nguyên văn và `check` báo `MATCH`. `python scripts/vv.py verify` pass. Lượt review các file đó được gọi bằng `--model gpt-5.6-sol` và effort `medium`. JSONL không có `error` hay `turn.failed`. Header ghi `Model: GPT-5 (Codex)` và `Reasoning effort: medium`. Người dùng chấp nhận header đó là model đã truyền trên CLI. Báo cáo được lưu tại `reviews/requirements-review.md`.

Sáu P1 trong báo cáo đó thay các ID cùng tên của review round 1, vì review mới đọc bản round 2. Review round 1 có `REQ-007` P1 và `REQ-008` P2; báo cáo mới không mở lại hai ID đó. `rounds.architecture` là 2. Ngày 2026-10-11 người dùng nhận risk cho `REQ-001` đến `REQ-006`. Không còn P0 hoặc P1 mở.

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| REQ-001 | P1 | accepted-risk | 2026-10-11: Người dùng nhận risk. Mapping chưa có cột evidence riêng cho `src_tbl` và `trg_tbl`. Mẫu vẫn có `name_status`, `context_ref` và mục thiếu evidence. | |
| REQ-002 | P1 | accepted-risk | 2026-10-11: Người dùng nhận risk. BRD mục 5 chưa có cột evidence riêng cho `trg_tbl`. Grain và khóa vẫn có cột evidence. | |
| REQ-003 | P1 | accepted-risk | 2026-10-11: Người dùng nhận risk. Đoạn quy ước chung nêu bảng cũ mà không bắt đầu bằng `[EXAMPLE]`. Các dòng ví dụ trong bảng vẫn có nhãn. | |
| REQ-004 | P1 | accepted-risk | 2026-10-11: Người dùng nhận risk. `BR-EX-03` ghi `short_description` khi nguồn chưa biết. Dòng này là ví dụ có nhãn, không phải dữ liệu production. | |
| REQ-005 | P1 | accepted-risk | 2026-10-11: Người dùng nhận risk. Guardrail ghi thêm tiền tố `slv_pm_` với nhãn `[PROPOSED]`. Tiền tố đang dùng vẫn là `slv_pn_` và `slv_3p_`. | |
| REQ-006 | P1 | accepted-risk | 2026-10-11: Người dùng nhận risk. Agent chưa nêu đủ câu bronze chỉ append từ Eventstream và gold chỉ expose/sync. Hai ràng buộc này vẫn nằm trong `AGENTS.md` và `docs/context/`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-11: Người dùng duyệt ngoại lệ có giới hạn cho task này. `AGENTS.md` giao source code cho Main và chỉ cho Claude Code viết `architecture.md`. Trong task này Claude Code là tác giả của mẫu Mapping, mẫu Business Requirements Document, định nghĩa agent phân tích, và `.codex/agents/requirements-reviewer.toml`. Main không soạn và không sửa câu chữ các tài liệu đó. Main chép nguyên văn từng khối `FILE:` sau verdict `PASS`.
- `python scripts/vv.py run-gate` tại `waiting_architecture` vẫn là lượt Claude read-only. Runner chỉ lưu `architecture.md`. Không đổi `scripts/agent_runner.py` để Claude ghi tự do vào repository.
- Không đổi model hay effort trong `.claude/settings.json` và `.codex/config.toml`. Architect giữ `claude-opus-5-5` với effort `high`. Agent phân tích dùng `claude-opus-5-5` với effort `medium` và không thay Architect.
- Không đi qua vòng review Codex hiện tại. `review_plan.required_reviewers` để trống. `gates.specialist_review` và `gates.risk_gate` là `not_required`. Không gọi `python scripts/vv.py run-gate` khi status là `reviewing`. Không thêm reviewer vào `REVIEWERS` trong `scripts/vv.py`.
- Với finding P0 hoặc P1 về nội dung tài liệu, disposition `fixed` chỉ được ghi sau khi Claude viết lại trong một lượt architecture mới và Main đã chép nguyên văn khối đó. Main không sửa tài liệu để đáp finding.
- 2026-10-11: Người dùng quyết định: nếu lượt review trước dùng `gpt-5.6-sol` thì header `GPT-5 (Codex)` được coi là model đó. Lượt này được gọi bằng `--model gpt-5.6-sol` và effort `medium`, nên điều kiện đúng.
- 2026-10-11: Người dùng nhận risk cho `REQ-001` đến `REQ-006`. Không sửa tài liệu để đáp các finding đó.
