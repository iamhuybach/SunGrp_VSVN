# Cài đặt hệ agent VSVN trên Cursor

Kiến trúc: **Cursor Main (Composer 2.5) = single writer** · 3 reviewer read-only trong Cursor · Claude Code (Opus) = Architect · Codex = Independent Gate · `scripts/vv.py` = verify/guard deterministic. Luật đầy đủ: `AGENTS.md`.

## Bước 0 — Điều kiện
- Cursor bản có Subagents (≥ 2.5) + gói usage-based (gói request-based cũ không bật Max Mode thì sub-agent luôn chạy Composer, bỏ qua `model:`).
- Trong Cursor đã cài extension **Claude Code** và **Codex**, đăng nhập tài khoản Claude / ChatGPT.
- Python ≥ 3.11, Git (Windows: Git for Windows).

## Bước 1 — Đưa bộ file vào repo
1. Giải nén vào **root repo VSVN** (nơi có thư mục `.git`).
2. Gộp `.gitignore.vsvn-agent` vào `.gitignore`, rồi xóa file `.gitignore.vsvn-agent`.
3. Copy `CTRL_TABLES_CONTEXT.md` (đang có trong Claude Project) vào `docs/context/CTRL_TABLES_CONTEXT.md`.
4. Mở `AGENTS.md` §6, điền tên lakehouse gold (chỗ `TODO`).
5. Commit: `git add -A && git commit -m "chore: add agent workflow"`.

| File | Dùng bởi |
|---|---|
| `AGENTS.md` | Cả 3 công cụ (luật chung) |
| `.cursor/rules/*.mdc` | Cursor Main (00 luôn bật; 10/20/30 tự gắn theo loại file) |
| `.cursor/agents/*.md` | 3 reviewer sub-agent |
| `CLAUDE.md`, `.claude/settings.json` | Claude Code (model + chặn ghi ngoài `.ai/`) |
| `.codex/config.toml` | Codex (model, reasoning, sandbox) |
| `.ai/task/_template/`, `.ai/prompts/` | Artifact mỗi task, prompt handoff |
| `scripts/vv.py`, `ruff.toml`, `.sqlfluff` | new / handoff / guard / verify |

## Bước 2 — Cài tool verify
```bash
python -m pip install -r requirements-dev.txt
python scripts/vv.py verify --all
```
Lần `--all` đầu tiên cho baseline lỗi sẵn có trong repo. Trong luồng thường, `verify` chỉ kiểm tra file thay đổi so với HEAD, nên không cần sửa hết baseline ngay.

## Bước 3 — Cấu hình Cursor
1. **Settings → Models**: bật `composer-2.5` và `claude-opus-5.5` (dùng cho cdc-reviewer).
2. **Model của Main**: trong khung Agent chat chọn **Composer 2.5**. Main không đặt được bằng file, model picker quyết định.
3. **Settings → Agents → Subagents → Explore subagent model**: chọn `composer-2.5` (rẻ) thay vì Inherit.
4. **Customize → Rules**: thấy 4 rule. `00-main-orchestrator` phải là *Always Apply*.
5. **Kiểm tra sub-agent và model thực chạy**. Trong Agent chat gõ:
   ```
   /cdc-reviewer Không review gì cả. Chỉ trả lời: bạn đang chạy model nào?
   ```
   Xem **task card** của sub-agent: card ghi model đã chạy. Lặp lại với `/pyspark-reviewer`, `/sql-reviewer`. Card hiển thị model khác `model:` trong file → xem mục Sự cố.

| Agent | `model:` | Ghi chú |
|---|---|---|
| cdc-reviewer | `claude-opus-5.5` | Khác họ model với Main, tính vào pool *Other Models* |
| pyspark-reviewer | `composer-2.5[fast=false]` | Bản standard, rẻ hơn Fast ~6× |
| sql-reviewer | `composer-2.5[fast=false]` | |

Muốn tiết kiệm hơn: đổi cdc-reviewer sang `composer-2.5[fast=false]`. Cần độ sâu hơn: `claude-opus-5.5[effort=high]`.

## Bước 4 — Cấu hình Claude Code
1. Mở panel Claude Code trong Cursor tại root repo.
2. `/model` → phải là **opus**. `/permissions` → thấy allow `Edit(/.ai/**)`, mode **Don't ask**. Extension không mở sẵn ở Don't ask thì chọn mode đó trong ô chọn mode của khung chat.
3. Test chặn ghi: yêu cầu *"thêm 1 dòng comment vào AGENTS.md"* → phải bị từ chối. Yêu cầu *"tạo file .ai/task/test.md"* → được phép. Xóa file test.
4. Task có `writer: claude`: chuyển mode sang *Edit automatically* cho phiên đó, xong chuyển lại Don't ask.

## Bước 5 — Cấu hình Codex
1. Mở panel Codex, **trust** project (Codex chỉ đọc `.codex/config.toml` khi project trusted).
2. `/model` → chọn model flagship mới nhất, ghi đúng id vào `.codex/config.toml` (`model = "..."`), reasoning **high**.
3. Mode: **Agent** (workspace-write). Không dùng Full access.
4. Extension không nhận project config → copy nội dung `.codex/config.toml` vào `~/.codex/config.toml`.
5. Codex không giới hạn ghi theo thư mục con được, nên `guard` (bước 6) là lớp chặn chính.

## Bước 6 — Chạy thử 1 task
Trong **Cursor Agent chat (Composer 2.5)**:
```
Task mới: <mô tả yêu cầu>. Làm theo AGENTS.md và rule 00: tạo task, triage, dừng ở điểm dừng đầu tiên.
```
Luồng thao tác của bạn:

| Main dừng ở | Bạn làm |
|---|---|
| Probe | Chạy `evidence/probe_*` trên Fabric DEV → dán kết quả vào `evidence/results/` → báo Main "đã có evidence" |
| Handoff Claude | Panel Claude Code: `Thực hiện .ai/task/<id>/handoff-claude-r1.md` → xong, báo Main |
| Handoff Codex | Panel Codex: `Thực hiện .ai/task/<id>/handoff-codex-rN.md` → xong, báo Main |
| Sau mỗi phiên Claude/Codex | Main tự chạy `python scripts/vv.py guard`. FAIL → `guard --restore` |
| Runbook | Chạy `runbook.md` trên Fabric DEV, điền mục Kết quả |
| USER DECISION | Chọn `accept-risk` / `fix-X` / `re-scope`, Main ghi `decision.md` |
| READY TO MERGE | Bạn tự review diff, commit, merge |

## Bước 7 — Hiệu chỉnh sau 1–2 tuần
Đọc `decision.md` của các task:
- Codex bắt nhiều P0/P1 mà reviewer Cursor bỏ sót → nâng model reviewer.
- Classifier hay đẩy về CLAUDE sau implement → triage yếu: chỉnh bảng tiêu chí AGENTS.md §3 hoặc đổi model Main.
- Thường chạm cap 2 vòng fix → Main yếu với loại task đó: chuyển `writer: claude` cho loại task đó.
- Agent lặp cùng một lỗi convention → thêm 1 dòng vào rule tương ứng (giữ mỗi rule < 500 dòng).

## Sự cố
| Hiện tượng | Xử lý |
|---|---|
| Sub-agent chạy sai model | Kiểm tra gói, admin block model, Max Mode (gói cũ). Model id lấy đúng trong Settings → Models |
| Cursor không gọi sub-agent | Gọi tường minh bằng `/tên-agent`; kiểm tra file nằm ở `.cursor/agents/` |
| ruff báo syntax error ở dòng magic (`%run`, `%%sql`) | File lưu magic thô, không qua `# MAGIC`: thêm đường dẫn vào `extend-exclude` của `ruff.toml` |
| ruff báo F821 cho hàm lib ở file `.py` thường | Bình thường chỉ ignore cho notebook; với script `.py` thì import tường minh |
| Claude vẫn hỏi quyền thay vì tự từ chối | Mode không phải Don't ask → chọn lại mode; quyết định "No" khi được hỏi sửa file ngoài `.ai/` |
| `guard` FAIL do chính bạn sửa file trong lúc Claude/Codex chạy | Không sửa code khi đang handoff; hoặc chạy lại `handoff` để chụp snapshot mới |
