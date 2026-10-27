## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`
- Risk gate: not required, not run

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `REV-001` — **P1** — `docs/context/03_OPERATOR_GUIDE.md:382`: Quy trình thêm bảng L1 mới không backfill khi nguồn đã có `last_src_version`, nên lần chạy incremental có thể bỏ vĩnh viễn toàn bộ dữ liệu lịch sử nhưng vẫn tiến watermark. Bổ sung bước chạy riêng `table_filter="<new trg_tbl>"` với `full_reload=True`, phân biệt với nguồn hoàn toàn mới dùng `allow_full_scan=True`, đồng thời cập nhật procedure tương ứng tại `.cursor/skills/vsvn-operator-docs/SKILL.md:71`.

## P2/P3

P2: 3 · P3: 0
