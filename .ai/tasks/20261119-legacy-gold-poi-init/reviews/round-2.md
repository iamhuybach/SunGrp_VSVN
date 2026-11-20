## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`
- Risk gate: completed

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P1 | `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:223` | So sánh `full_outer` tính các dòng source-only mới là drift, khiến lần RUN đầu với map rỗng luôn dừng. | Thêm marker hai phía, chỉ tính drift khi persisted row bị thiếu nguồn hoặc xung đột field; giữ source-only trong tập fresh insert và bổ sung test tương ứng. |
| GATE-004 | P1 | `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:164` | MERGE có thể đã commit nhưng lỗi đọc history làm summary thiếu version/count; lỗi cleanup hoặc release lock còn có thể che exception gốc. | Đối soát best-effort theo tag `LEGACY_INIT:<exec_id>` và `v_pre`, báo trạng thái commit hoặc `UNKNOWN`, đồng thời cô lập lỗi cleanup/unlock để giữ exception gốc. |

GATE-002, GATE-003 và GATE-005 đã được xác nhận đóng.

P2: 2. P3: 0.

Probe: Không cần probe để xác nhận hai lỗi code trên; runtime evidence Fabric DEV vẫn phải hoàn tất sau khi sửa.
