## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium`.
- Reviewers: `state-correctness-reviewer`, `sql-data-reviewer`, `spark-runtime-reviewer`, `fabric-pipeline-reviewer`.
- Risk gate: completed.

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

| ID | Severity | file:line | Failure | Fix |
|---|---|---|---|---|
| GATE-003 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4143` | Fast path có thể đọc lock hết hạn, thua race với owner vừa refresh, không nhả được lock nhưng vẫn báo hội tụ vì không đọc lại trạng thái. | Sau conditional release, đọc lại đúng một cặp lock; chỉ tiếp tục khi owner là `NULL`, dừng với live owner và retry có giới hạn nếu vẫn hết hạn. |
| GATE-002 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4136` | Fast path chạy trước `_issues`, nên duplicate hoặc clash dưới tên mới không được phát hiện và trạng thái sai vẫn được báo thành công. | Chạy `_issues(old, new)` trước fast path và trước mọi write; dừng khi có bất kỳ issue nào. |
| SPARK-001 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4187` | Lock `UPDATE` có thể đã commit nhưng lỗi khi `collect()` xảy ra trước `held=True`, khiến `finally` bỏ cleanup và giữ lock `RUNNING` trong 35/90 phút. | Đánh dấu cần cleanup trước `UPDATE`, cleanup theo owner `LOCK`, đồng thời giữ nguyên lỗi gốc nếu cleanup cũng thất bại. |

`GATE-001` P0 đã được xác nhận fixed. Ba P1 trên độc lập, không trùng lặp.

## P2/P3

P2: 1; P3: 0.

Probe: không cần; các lỗi được chứng minh trực tiếp từ control flow và ranh giới commit của Delta.
