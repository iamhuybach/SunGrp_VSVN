## Model và reviewer manifest

`gpt-5.6-sol`, reasoning `medium`. Đã chạy độc lập: state-correctness, spark-runtime, sql-data, api-contract, jpa-performance; risk-gate đã hoàn tất.

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| GATE-010 | P0 | `notebooks/NB_CREATE_DDL.ipynb:5967,5990` | `_confirm_skip` có thể `RESTORE` về trước rewrite sau khi luồng bình thường đã ghi dữ liệu mới, làm mất dữ liệu hợp lệ. | Lưu attempt ID cùng version trước/sau rewrite; chỉ tự động restore khi HEAD vẫn là commit cuối của attempt, nếu có commit mới thì dừng để phục hồi thủ công và thêm test timeline này. |
| GATE-011 | P1 | `notebooks/NB_CREATE_DDL.ipynb:5967,5990` | Sau overwrite, code không heartbeat hoặc xác nhận lại quyền sở hữu trước `ALTER COLUMN` và `SET TBLPROPERTIES`, nên stale owner vẫn có thể commit. | Heartbeat và revalidate trước từng durable write, đồng thời fence bằng Delta version kỳ vọng và dừng khi version drift. |
| GATE-008 | P1 | `.ai/tasks/20261116-enr-lang-destination-from-bronze/runtime-runbook.md:34` | Các file được phép kiểm tra chưa chứng minh Copy Job luôn dừng trước migration và chỉ mở lại sau khi toàn bộ bước thành công. | Cung cấp và review trình tự B5 cùng điều kiện stop/rollback; không cần quyết định kiến trúc mới nếu khả năng pause đã được xác nhận. |

P2/P3: **3/0**.

Probe: xác nhận B5 bắt buộc `pause Copy Job → confirm no active run → enrgldpy → PostgreSQL ALTER → API deploy/restart → forced NB_00/read checks → resume Copy Job`, và không có nhánh resume sau bất kỳ bước lỗi nào.
