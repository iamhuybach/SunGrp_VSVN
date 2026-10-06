# Handoff → Claude Code (Architect) — {{TASK_ID}} · round {{ROUND}}

Bạn là Architect của VSVN. Đọc theo thứ tự:
1. `AGENTS.md`
2. `.ai/task/{{TASK_ID}}/triage.md`
3. `.ai/task/{{TASK_ID}}/evidence/` (nếu có) và `decision.md` (nếu đây là lần quay lại)
4. `docs/context/` và code liên quan trong repo

## Nhiệm vụ
Viết `.ai/task/{{TASK_ID}}/spec.md` theo template sẵn trong file, mức LLD: Main (Composer) phải implement được mà không cần tự ra quyết định thiết kế — tên bảng/cột/kiểu/khóa, signature hàm, thứ tự cell, tham số, thay đổi pipeline và control tables cụ thể.
Dùng skill `visitvn-fabric-platform-architect` nếu có. Pattern nào cũng phải đối chiếu tài liệu chính thức Microsoft Fabric / Delta và ghi nguồn ở mục 3.

## Ràng buộc
- CHỈ ghi trong `.ai/task/{{TASK_ID}}/`. Không sửa code, không chạy lệnh thay đổi repo.
- Không suy đoán dữ liệu. Kết luận phụ thuộc dữ liệu chưa có trong `evidence/results/` → ghi vào mục 8 "Evidence needed" kèm query probe đề xuất, đánh dấu phần spec bị ảnh hưởng, rồi dừng.
- Tuân thủ layer rules, khóa, naming trong AGENTS.md §6. Muốn đổi luật → ghi đề xuất ở mục 9, không tự áp dụng.

## Kết thúc
In ra: 5 dòng tóm tắt thiết kế · Evidence needed (hoặc "none") · Open questions.
