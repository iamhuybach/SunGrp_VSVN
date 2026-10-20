## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`
- Risk gate: completed

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| STATE-004 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2127` | Khi `INSERT` hoặc validation lỗi, `finally` vẫn ghi `status='SUCCESS'` và xoá lock, che giấu patch thất bại và làm sai trạng thái recovery. | Chỉ ghi `SUCCESS` trên success path; exception path phải owner-guarded ghi `FAILED`/`error_message`, giải phóng lock rồi re-raise, kèm test success và failure. |
| STATE-005 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2067,2083-2094` | Hard crash sau khi commit lock có thể để lại UUID owner vĩnh viễn, khiến mọi retry với UUID mới không thể nhận lock. | Dùng stable execution ID cùng owner-checked lease/stale-lock recovery, hoặc cung cấp cơ chế recovery được phê duyệt có thể phân biệt lock stale/live an toàn. |

P2: 1. P3: 0.

Carry-over `STATE-001`, `STATE-002`, và `STATE-003` được đóng theo disposition; `STATE-002` đã được xác nhận trực tiếp trong diff.
