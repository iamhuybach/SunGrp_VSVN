## Manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`
- Risk gate: completed

## Gate verdict: `EVIDENCE_REQUIRED`

| ID | Severity | Location | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P1 | `.ai/tasks/20261020-dictionary-seed-from-mapping/runtime-runbook.md:28` | Không có diff hoặc nội dung R2 để chứng minh backup cũ không thể được tái sử dụng và làm rollback khôi phục dictionary sai lệch. | Cung cấp R2 có số dòng, thể hiện dừng khi backup tồn tại, danh sách cột tường minh và kiểm tra hai chiều `EXCEPT ALL = 0` trước mỗi `DROP`. |
| GATE-002 | P1 | `.ai/tasks/20261020-dictionary-seed-from-mapping/runtime-runbook.md:47` | Không có diff hoặc trình tự lệnh để chứng minh các rerun `p_apply=true` và assertions hoàn tất trước R10, rồi xác nhận lại pause/no-active-run trước resume. | Cung cấp đầy đủ đoạn từ rerun `p_apply=true` qua assertions đến R10/1H, gồm thứ tự thực thi và các kiểm tra pause/active-run. |

P2/P3: `0`.

Probe: trích xuất `runtime-runbook.md` có số dòng gồm toàn bộ R2 và toàn bộ đoạn từ rerun `p_apply=true` đến R10/1H; disposition `fixed` chưa đủ để đóng hai P1 khi handoff ghi nhận không có file thay đổi kể từ round 1.
