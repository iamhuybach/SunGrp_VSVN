## Model và reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium` — khớp yêu cầu.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`.
- `risk-gate`: đã hoàn tất.

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| STATE-001 | P1 | `.ai/tasks/20261020-entity-drop-op-cols-add-website/runtime-runbook.md:76,79-88` | Lock `UPDATE` không có assertion thực thi và nhánh thiếu flow row bỏ qua lock, nên `DROP`/`DELETE` vẫn có thể chạy khi NB_00 đang hoạt động. | Tạo/giành flow lock kể cả khi flow row chưa tồn tại, xác nhận ownership bằng bước thực thi trước destructive block riêng, giữ lock đến khi reset hoàn tất. |
| STATE-002 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2066-2078` | Contact-edge patch chỉ kiểm tra lock rồi `INSERT` mà không giữ lock, cho phép NB_00 quan sát topology thay đổi giữa run. | Giữ flow lock xuyên suốt `INSERT`, validation và release, hoặc loại bỏ writer trực tiếp và chỉ dùng setup path có lock. |
| STATE-003 | P1 | `.ai/tasks/20261020-entity-drop-op-cols-add-website/runtime-runbook.md:137-149` | Rollback deploy code cũ và đổi edge trước khi lấy lock, làm lộ trạng thái code/config/schema không tương thích cho run đồng thời. | Lấy flow lock trước mọi thay đổi rollback, giữ xuyên suốt deploy, đổi edge, reset và rebuild; chỉ release sau validation. |

Không có P0. `SPARK-001` được gộp vào `STATE-001`.

## P2/P3

- P2: 6 báo cáo specialist; chưa deduplicate vì không ảnh hưởng verdict.
- P3: 0.

## Probe

`SELECT count(*) AS dup_poi FROM (SELECT poi_id FROM lh_vv_silver.dbo.slv_3p_poi_contact WHERE poi_id IS NOT NULL GROUP BY poi_id HAVING count(*) > 1);` — phải trả `dup_poi = 0` trước destructive step; nếu lớn hơn 0 thì `USER_DECISION`.
