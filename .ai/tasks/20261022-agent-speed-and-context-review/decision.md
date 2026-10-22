# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| EXC-01 | Model khảo sát | Fable 5.1, effort medium, viết .ai/tasks/20261022-agent-speed-and-context-review/reviews/agent-speed-review.md. Không gọi run-author. | Yêu cầu người dùng | 2026-10-22 |
| EXC-02 | Model review diff | Review thay đổi là Claude Code Opus 5.5, effort high, chỉ diff. Không gọi run-gate. | Yêu cầu người dùng | 2026-10-22 |
| DEC-03 | Cấu hình model | Không đổi model ID hay effort trong .claude/settings.json và .codex/config.toml. | Yêu cầu người dùng | 2026-10-22 |
| DEC-01 | Kiến trúc của task | Người dùng chốt mục 8, dòng 1 đến 15. Architecture của task trỏ tới mục 8 của reviews/agent-speed-review.md. | Yêu cầu người dùng, reviews/agent-speed-review.md mục 8 | 2026-10-22 |
| DEC-02 | Ba phiên | Một task cho ba phiên dùng chung. | Yêu cầu người dùng | 2026-10-22 |
| DEC-04 | Manifest vòng 2 | Không đổi manifest vòng 2. Không sửa agent_runner, review.md, WORKFLOW.md §6. | Yêu cầu người dùng, mục 9.1 | 2026-10-22 |
| DEC-05 | Architect vòng 2 | Không đổi _architect_appendix. | Yêu cầu người dùng, mục 9.2 | 2026-10-22 |
| DEC-06 | fabric-pipeline-reviewer | Không đổi luật fabric-pipeline-reviewer. | Yêu cầu người dùng, mục 9.3 | 2026-10-22 |
| DEC-07 | Review task agent-system | Không sửa AGENT_PROMPT_SAMPLES.md A18. EXC-02 chỉ áp cho task này. | Yêu cầu người dùng, mục 9.4 | 2026-10-22 |
| DEC-08 | Tên pipeline _15P | Giữ tên PL_VV_TRANS_SLV_TO_ENR_15P. Làm mục 8 dòng 4 đúng câu trong báo cáo. | Yêu cầu người dùng, mục 9.5 | 2026-10-22 |
| DEC-09 | Grep dòng 9 sau DIFF-003 | Dòng lịch sử `13 bảng SUCCESS (registry lúc đó)` được giữ. `grep "13 bảng\|langs"` khớp dòng đó và không gắn nhãn mã chết. | reviews/round-1.md DIFF-003 | 2026-10-22 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- EXC-01 dùng `role: architect` và `runtime: cursor`. Validator chỉ nhận `main`, `architect`, `review`, `author`, `author_proposal`. Báo cáo Fable là architecture sau khi chốt mục 8. Runtime là Cursor vì phiên này không đổi model trong `.claude/settings.json`.
- EXC-02 dùng `role: review` và `runtime: claude-code`. Đây là review diff đã duyệt, không phải specialist reviewer của `run-gate`.

## Sai lệch so với kiến trúc

- DEC-09: cách kiểm tra mục 8 dòng 9 nói `grep "13 bảng|langs"` chỉ còn dòng mã chết. Sau DIFF-003, một dòng lịch sử 04/10 vẫn khớp `13 bảng`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| DIFF-001 | P2 | fixed | Gỡ `LANG_MODES`, `uses_langs`, `need_langs`, `langs`, `ENTRY_TYPE`, `lang_entries`. `presence` và `expand_rows` chỉ còn `DOC` / `DOC_ARRAY`, khớp notebook. | |
| DIFF-002 | P3 | fixed | Dòng vận hành chỉ còn exit key `bad_shape`. Notebook không emit `primary_without_lang`. | |
| DIFF-003 | P3 | fixed | Khôi phục `13 bảng SUCCESS (registry lúc đó)`. DEC-09 ghi grep còn khớp dòng lịch sử. | |
| DIFF-004 | P2 | fixed | `CLAUDE.md` cấm sửa file ngoài artifact của vai. | |
| DIFF-005 | P3 | fixed | Header nêu cả hai notebook. `Luồng hiện có` là `PL_VV_TRANS_SLV_TO_ENR_15P`. `p_pl_name` ghi `_15P` làm lib WARN. | |
| DIFF-006 | P3 | fixed | §11 `[PROPOSED]` nhận lại danh sách cột, Run 1, và `has_required_langs`. | |
| DIFF-007 | P3 | fixed | Xóa câu đặt context ngang notebook. Dòng 8 của tóm tắt nhận lại `C2 lib extract`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-22: duyệt EXC-01, EXC-02, và DEC-03 (không đổi model ID hay effort trong `.claude/settings.json` và `.codex/config.toml`).
- 2026-10-22: architecture của task là báo cáo Fable sau khi chốt mục 8. Ba phiên dùng chung một task.
- 2026-10-22: chốt mục 8, dòng 1 đến 15. Mục 9: không đổi manifest vòng 2; không sửa agent_runner, review.md, WORKFLOW.md §6; không đổi _architect_appendix; không đổi luật fabric-pipeline-reviewer; không sửa AGENT_PROMPT_SAMPLES.md A18; EXC-02 chỉ áp cho task này; giữ tên PL_VV_TRANS_SLV_TO_ENR_15P và làm mục 8 dòng 4 đúng câu trong báo cáo.
- 2026-10-22: đóng task. Workflow không có status `done`; status kết thúc là `ready_to_merge`.

## Lịch sử quyết định

- 2026-10-22: Người dùng yêu cầu chuyển status sang done. `verifying` -> `ready_to_merge`. `validate` PASS. Commit nội dung đã ở `bbb508c` trên `origin/main`.
- 2026-10-22: Review `reviews/round-1.md` verdict `FIX_REQUIRED`, 0 P0/P1, 2 P2, 5 P3. DIFF-001 đến DIFF-007 xử lý `fixed`. DEC-09 ghi lệch grep của dòng lịch sử. `gates.specialist_review` về `not_required` vì `required_reviewers` rỗng và validator không nhận `pass`. `models.review.actual` là `claude-opus-5-5`.
- 2026-10-22: Người dùng duyệt exception cho phiên khảo sát và phiên review diff. EXC-01 ghi `role: architect`, `model: claude-fable-5-1`, `effort: medium`, `runtime: cursor`. EXC-02 ghi `role: review`, `model: claude-opus-5-5`, `effort: high`, `runtime: claude-code`. `models.*.expected` và `models.*.effort` giữ mặc định. Không gọi `run-author`. Không gọi `run-gate`.
- 2026-10-22: DEC-01 sửa tại chỗ. Câu trước: architecture của task là báo cáo Fable sau khi người dùng chốt mục 8. Câu hiện hành: người dùng đã chốt mục 8 dòng 1–15, architecture trỏ tới mục 8 của `reviews/agent-speed-review.md`. DEC-04 đến DEC-08 ghi năm câu trả lời mục 9. Không sửa `scripts/agent_runner.py`, `.ai/prompts/review.md`, `docs/agent-system/WORKFLOW.md` §6, `_architect_appendix`, luật `fabric-pipeline-reviewer`, hay `AGENT_PROMPT_SAMPLES.md` A18.
