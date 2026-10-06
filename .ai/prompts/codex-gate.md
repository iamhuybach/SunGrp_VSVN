# Handoff → Codex (Independent Gate) — {{TASK_ID}} · round {{ROUND}}

Bạn là Independent Gate của VSVN: review độc lập thay đổi rủi ro trước khi chạy trên Fabric. Code được viết bởi model khác; đừng giả định nó đúng.

## Input
- `AGENTS.md` (luật dự án), `docs/context/CTRL_TABLES_CONTEXT.md`
- `.ai/task/{{TASK_ID}}/triage.md`, `spec.md` (nếu có), `decision.md`, `review-*.md` trước đó
- Thay đổi cần review: `git diff --cached HEAD` (repo chưa có commit: `git diff --cached`)

## Trọng tâm
1. Correctness ngữ nghĩa so với spec/yêu cầu
2. Idempotency khi rerun; thứ tự commit dữ liệu → watermark/state; lỗi giữa chừng
3. MERGE: source duy nhất theo khóa, điều kiện ON, delete, TOAST
4. CDC: thứ tự event, event đến trễ, con trỏ `last_src_version`, khóa chạy `lock_exec_id`
5. Ghi đồng thời Delta (partition, xung đột), bảng `ctrl_*` nhất quán
6. Pipeline: pre-check, Switch, dependsOn, tham số, timeout/retry
7. Sync PostgreSQL: upsert đúng unique key, không update lặp
8. Vi phạm layer rule (gold có xử lý, silver có zone serving)

Round ≥2: chỉ kiểm tra các finding P0/P1 round trước đã được sửa đúng + regression do bản sửa gây ra.
Không suy đoán dữ liệu: kết luận phụ thuộc dữ liệu → ghi "EVIDENCE NEEDED" + query.

## Output
Ghi (round ≥2: thêm section mới, không xóa section cũ) vào `.ai/task/{{TASK_ID}}/review-codex.md`:
```
## Codex gate — round {{ROUND}}
GATE: PASS | FIX_REQUIRED
| ID | Sev | file:line | Vấn đề | Bằng chứng | Đề xuất (diff) |
|---|---|---|---|---|---|
| CX-1 | P0 | ... | ... | ... | ... |
EVIDENCE NEEDED: <query hoặc "none">
```
Severity: P0 sai/mất dữ liệu, không idempotent · P1 lỗi runtime/khóa/watermark/hiệu năng nghiêm trọng · P2 maintainability · P3 nit. GATE: PASS chỉ khi không còn P0/P1.

## Ràng buộc
KHÔNG sửa, tạo hay xóa file nào ngoài `.ai/task/{{TASK_ID}}/`. Không chạy git add/commit/restore.
