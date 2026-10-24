## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`
- Risk gate: không bắt buộc, không chạy

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `STATE-001` — P1 — `notebooks/NB_CREATE_DDL.ipynb:3309`: Run cũ có thể tiếp tục `ALTER`/`CREATE`/`INSERT` sau khi lease 90 phút hết hạn và run mới đã chiếm lock, gây hai owner ghi đồng thời và trạng thái patch xen kẽ. Fix: gia hạn lease và xác nhận `lock_exec_id = LOCK` ngay trước mỗi durable write; dừng ngay khi mất ownership.

## P2/P3

- P2: 2
- P3: 0
