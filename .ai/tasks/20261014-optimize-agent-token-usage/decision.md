# Quyết định

## Giả định còn lại

- Baseline đã có `Total tokens`, `Included tokens`, `On-demand tokens` và tỷ trọng Grok 4.7 theo ngày. Hai ngày chính có tổng `198.0513M` token Grok 4.7, tương đương khoảng `92.1%` của `215.1M` toàn kỳ; các ngày khác được người dùng xác nhận là không đáng kể. Tooltip không hiển thị một giá trị riêng cho `Number of requests`.
- Cursor UI không hiển thị `Active Rules` hoặc `Rules/Context`, nhưng phép thử trong chat mới, không gắn `@AGENTS.md`, trả lời đúng hai chỉ dẫn riêng của repository: hội thoại bằng tiếng Việt và chỉ người dùng được commit/merge. Kết quả này xác nhận `AGENTS.md` được tự động nạp.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-001 | P1 | fixed | `models.author.actual` nay chỉ chấp nhận model chuẩn hoặc Author override hợp lệ; có test cho model không được duyệt và override được duyệt. | Không |
| STATE-002 | P1 | fixed | `materialize --write` preflight toàn bộ block và yêu cầu status `implementing` trước byte ghi đầu tiên; có test không tệp nào được tạo khi status là `ready_to_merge`. | Không |
| MEASURE-001 | P2 | backlog | Sau merge và 7 ngày làm việc, ghi aggregate Cursor Dashboard cùng số phase hoàn tất vào `evidence/results/cursor-usage-after.md`; so token/phase, review round, missed P0/P1 và Claude quota. Nếu mức giảm dưới 20%, báo người dùng trước khi cân nhắc D1. | Mục tiêu 2026-10-23 |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Ngày 2026-10-14, người dùng chỉ định Claude Code (`claude-opus-5-5`, effort `high`) viết `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md` làm kiến trúc cho task này.
- Người dùng chỉ định Codex (`gpt-5.6-sol`, effort `medium`) triển khai tại chỗ thay cho Grok Main; review vẫn chạy độc lập qua `python scripts/vv.py run-gate 20261014-optimize-agent-token-usage`.
- D1: Chưa dùng Grok 4.7 Low cho các việc cơ học; quyết định sau khi có số đo từ Phases 1–5. Đây là phương án khuyến nghị trong kế hoạch.
- D2: Dùng Claude Author lane cho `proposal` và `runtime-runbook.md`.
- D3: Tách `AGENTS.md` thành core và `docs/agent-system/WORKFLOW.md`.
- Ngày 2026-10-14, người dùng chấp nhận kết quả Phase 6, tự chuyển task từ `user_decision` sang `ready_to_merge`, và xác nhận validation PASS.

## Nhật ký phase

### Phase 0

- Task được tạo và metadata, request, architecture pointer, reviewer routing đã được thiết lập.
- Đã ghi baseline quan sát được cho kỳ 2026-10-03 đến 2026-10-09: `Total tokens = 215.1M`, `Included = 215.1M`, `On-demand = 0`.
- Đã ghi tỷ trọng Grok 4.7: 94.4% ngày 2026-10-08, 92.3% ngày 2026-10-09, và khoảng 92.1% toàn kỳ theo tổng token hiển thị.
- Đã ghi D1–D3. Không hỏi lại các quyết định này.
- `AGENTS.md` active rule được xác nhận bằng phép thử chức năng vì UI không hiển thị danh sách active rules.
- Acceptance Phase 0: `python scripts/vv.py validate 20261014-optimize-agent-token-usage` PASS; task giữ `triage` cho đến khi Phase 1 step 1 được áp dụng.

### Phase 1

- Đã thêm validation typed `exceptions`; `EXC-01` cho phép `gpt-5.6-sol` triển khai task này mà không đổi expected model/effort.
- Đã thêm `toc`, `show`, `context`, compact `verify --full`, `materialize`, `closeout` và budget lint trong `doctor`.
- Đã thêm `tests/test_vv_context.py` và `tests/fixtures/sample_notebook.ipynb`.
- `python scripts/vv.py verify 20261014-optimize-agent-token-usage`: PASS. Lần chạy trong sandbox thất bại do pytest không có quyền dọn thư mục tạm trên Windows (`WinError 5`); chạy lại ngoài sandbox với cùng verifier PASS.
- `python scripts/vv.py doctor`: PASS; các WARN về budget và `.cursorindexingignore` được phép trong Phase 1 và sẽ được xử lý ở các phase sau.
- `python scripts/vv.py context 20261013-3p-extract-from-raw-payload`: PASS, 133 dòng, dưới giới hạn 400 dòng.
- Acceptance Phase 1: PASS.

### Phase 2

- Đã thêm ledger `Quyết định hiện hành`, `Lịch sử quyết định`, template `resume.md`, và optional `models.author` vào task templates.
- Validator chấp nhận task cũ không có `models.author`; nếu có thì bắt buộc đúng `claude-opus-5-5`, effort `medium`, và `actual` là string.
- Architect schema bắt buộc `main_brief` dài 200–14.000 ký tự. Runner ghép brief ngay sau `RESULT:`, hạ `##` trong brief thành `###`, và cảnh báo nếu `document` đã chứa `## Main brief`.
- Đã thay `.ai/prompts/architect.md` theo Appendix E.
- Local regression: ruff PASS, `validate --all` PASS cho 15 task, pytest `46 passed`, và `python scripts/vv.py verify 20261014-optimize-agent-token-usage` PASS.
- Người dùng đã chạy `python scripts/vv.py external-smoke --timeout 600`: `EXTERNAL SMOKE PASS`.
- Claude CLI `2.1.296`, architecture verdict `EVIDENCE_REQUIRED`; Codex CLI `0.162.0-alpha.17.2`, review verdict `FIX_REQUIRED`; reviewers `state-correctness-reviewer`, `sql-data-reviewer`; `risk-gate` đã chạy; repository không thay đổi.
- Hai verdict trên hợp lệ cho kịch bản smoke giả lập; mục tiêu là kiểm tra schema, manifest, routing, model và repository immutability, không yêu cầu verdict `PASS`.
- Acceptance Phase 2: PASS.

### Phase 3

- Đã tách procedures sang `docs/agent-system/WORKFLOW.md`; `AGENTS.md` còn 7.083 byte và giữ nguyên văn toàn bộ 13 platform invariant.
- Đã thay Always Apply rule và `vsvn-task-workflow` skill bằng bản context-bounded; thêm read budget đúng phạm vi được duyệt vào hai notebook skill.
- Đã thêm `.cursorindexingignore`, `.cursorignore`, cập nhật `SETUP.md`, context README, và các tham chiếu số mục `AGENTS.md` bị đổi trong requirements/templates.
- `python scripts/vv.py doctor`: PASS. WARN duy nhất là budget của `docs/AGENT_PROMPT_SAMPLES.md`, thuộc Phase 5; không còn WARN cho `AGENTS.md`, rules hoặc `.cursorindexingignore`.
- Không còn kết quả cho `rg -n 'Read `AGENTS.md`' .cursor`; đủ bảy heading bắt buộc trong `WORKFLOW.md`; so sánh invariant cũ/mới có `diff_lines=0`.
- Regression: task validation PASS, `git diff --check` PASS, pytest `46 passed`.
- Acceptance Phase 3: PASS.

### Phase 4

- Đã thêm Claude Author lane với model `claude-opus-5-5`, effort `medium`, schema document tối thiểu 200 ký tự, giới hạn 40 lượt, read-only tools và kiểm tra repository immutability.
- Đã thêm `vv.py run-author <task-id> --kind proposal|runbook [--timeout]`, giới hạn `handoffs/author-input.md` tối đa 60 dòng, xử lý template placeholder và bảo toàn artifact hiện có qua hậu tố `.new.md`.
- Runner chỉ cập nhật `models.author.actual`; không thay đổi status hoặc gates.
- Đã thêm hai prompt template từ Appendix F. `AGENTS.md` đã có ngôn ngữ `proposal.md` và Author row từ Phase 3 theo Appendix C.
- Local acceptance: ruff PASS, compile PASS, pytest `51 passed`, `validate --all` PASS cho 15 task, CLI help PASS, `doctor` PASS, `git diff --check` PASS.
- Người dùng đã chạy dry trial bằng Claude Code `2.1.296`: `run-author --kind proposal` tạo `proposal.md`, `Test-Path` trả về `True`, và scratch task validate PASS.
- Người dùng xác nhận đã xóa scratch task; kiểm tra repository cho kết quả `scratch_exists=False`. Bằng chứng sanitized nằm tại `evidence/results/author-lane-dry-trial.md`.
- Acceptance Phase 4: PASS.

### Phase 5

- Đã thay toàn bộ `docs/AGENT_PROMPT_SAMPLES.md` bằng Appendix A, giữ các nhánh D2 Author lane và bỏ các dòng fallback `không D2`.
- File giảm từ 37.784 byte xuống 14.604 byte, dưới giới hạn 25.600 byte.
- Coverage check: 22/22 case cũ được ánh xạ, 19/19 mẫu A1–A19 hiện diện, không thiếu target.
- CLI help PASS cho chín command được nêu rõ: `closeout`, `context`, `external-smoke`, `materialize`, `run-author`, `run-gate`, `show`, `toc`, `verify`.
- `doctor` PASS không còn budget WARN; `validate --all` PASS cho 15 task; `git diff --check` PASS.
- Acceptance Phase 5: PASS.

### Phase 6

- Local verification chính thức PASS cho 21 file: ruff, pytest và task-state PASS; các checker không có file liên quan được SKIP. Log nằm tại `verification/verify.log`.
- Task đã chuyển `implementing -> verifying -> reviewing`; `gates.local_verification=pass`, `rounds.verification=1`.
- Fixed preamble gồm `AGENTS.md` 7.083 byte và Always Apply rule 2.570 byte, tổng 9.653 byte, dưới giới hạn 12.288 byte.
- `vv.py context` PASS cho toàn bộ 15 task; lớn nhất 163 dòng tại `20261013-3p-extract-from-raw-payload`, dưới giới hạn 400 dòng.
- Specialist review round 1 đang chờ người dùng chạy `vv.py run-gate`; Phase 6 chưa hoàn tất.
- Review round 1 trả `FIX_REQUIRED` với `STATE-001` và `STATE-002`, đều P1; `state-correctness-reviewer` đã chạy độc lập và risk gate không bắt buộc.
- Đã sửa cả hai finding; ruff và compile PASS, pytest `53 passed`. Đặt lại local verification thành `pending` trước verification round 2.
- Local verification round 2 PASS cho 21 file; task đã chuyển lại `reviewing`, `gates.local_verification=pass`, `rounds.verification=2`.
- Review round 2 PASS: `STATE-001` và `STATE-002` đã resolved, không có P0/P1 mới, P2/P3 bằng 0; task chuyển `user_decision` với `gates.specialist_review=pass`.
- Immediate Phase 6 acceptance: PASS. Toàn bộ phase 0–6 đã qua acceptance; fixed preamble 9.653/12.288 byte và context pack lớn nhất 163/400 dòng.
- Chỉ tiêu giảm Cursor token trên mỗi phase ≥40% được hoãn đúng theo kế hoạch thành `MEASURE-001`, đo sau merge và 7 ngày làm việc; chưa có cơ sở tuyên bố đạt trước cửa sổ đó.
- Người dùng đã chuyển task sang `ready_to_merge`; Phase 6 kết thúc, không còn gate triển khai hoặc review đang mở.
