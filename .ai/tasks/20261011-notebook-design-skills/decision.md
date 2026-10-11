# Quyết định

## Giả định còn lại

- Không có. Khảo sát notebook dùng file trong repository. Không suy diễn dữ liệu Fabric DEV.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

Architecture round 2 viết lại cả hai skill. Main chép nguyên văn và `git diff` byte khớp khối trong `architecture.md`. Review round 2 không mở lại `GATE-002` và `GATE-004`. Ba finding còn lại vẫn P1 vì skill chỉ gắn nhãn gap trên notebook hiện có, không chỉ thị sửa notebook. `rounds.architecture`, `rounds.review` và `rounds.verification` đều đã là 2, nên không có round mới. P2 round 1 có count `1` nhưng không có ID; round 2 báo P2/P3 count `0`. Finding không tên đó không còn mở.

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | accepted-risk | 2026-10-11: Người dùng nhận risk. Skill cấm chép `concat_ws` sang nguồn mới và gắn known gap cho notebook hiện có. Đổi hash trên notebook hiện có là migration `ctrl_cdc_reject`, ngoài phạm vi task skill. | |
| GATE-002 | P1 | fixed | Architecture round 2 tách external identifier và temp view `_v_...`. Main chép nguyên văn. Review round 2 không mở lại. | |
| GATE-003 | P1 | accepted-risk | 2026-10-11: Người dùng nhận risk. Skill cấm blind append cho dữ liệu đổi hành vi và gắn gap cho `append_rows`. Đổi `append_rows` thành MERGE là thay đổi cả hai library, cần architecture và runtime proof riêng. | |
| GATE-004 | P1 | fixed | Architecture round 2 thay `json.load` bằng `compile()` và yêu cầu runbook Fabric DEV cho notebook mới hoặc library đổi cấu trúc. Lệnh compile chạy trên 7 notebook, in `compiled 7 notebooks`. Review round 2 không mở lại. | Pytest compile notebook, ghi ở architecture round 2 mục discrepancy 10 |
| GATE-005 | P1 | accepted-risk | 2026-10-11: Người dùng nhận risk. Skill yêu cầu bound cho nguồn mới và gắn known gap cho `profile_events` / `profile_docs`. Sửa hai hàm hiện có là task notebook riêng. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-11: Người dùng duyệt ngoại lệ có giới hạn cho task này. `AGENTS.md` giao source code cho Main và chỉ cho Claude Code viết `architecture.md`. Trong task này Claude Code là tác giả của mọi file `.cursor/skills/<tên>/SKILL.md`. Main không soạn, không sửa câu chữ, không rút gọn và không bổ sung nội dung skill. Codex vẫn chỉ đọc và review. `python scripts/vv.py run-gate` tại `waiting_architecture` vẫn là lượt Claude read-only. Runner từ chối mọi sửa file và chỉ lưu `architecture.md`. Không đổi `scripts/agent_runner.py` để Claude ghi tự do vào repository.
- Với finding P0 hoặc P1 về nội dung skill, disposition `fixed` chỉ được ghi sau khi Claude viết lại trong một lượt architecture mới và Main đã chép nguyên văn khối đó.
- 2026-10-11: Người dùng nhận risk cho `GATE-001`, `GATE-003` và `GATE-005`. Skill giữ nguyên văn Claude đã viết. Không sửa notebook trong task này.
