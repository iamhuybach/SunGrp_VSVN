## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium` — khớp cấu hình bắt buộc.
- Reviewers: `spark-runtime-reviewer`, `sql-data-reviewer`, `state-correctness-reviewer`, `fabric-pipeline-reviewer`.
- Risk gate: đã hoàn thành.

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P1 | `.cursor/skills/vsvn-extract-notebook/SKILL.md:49` | Hash ghép bằng delimiter và đổi `NULL` thành chuỗi rỗng có thể hợp nhất các reject khác nhau, làm sai lịch sử và số đếm. | Băm serialization canonical có ranh giới trường và phân biệt `NULL`, chẳng hạn JSON của struct có thứ tự ổn định. |
| GATE-002 | P1 | `.cursor/skills/vsvn-notebook-library/SKILL.md:42,53-54`; `.cursor/skills/vsvn-extract-notebook/SKILL.md:88` | Quy tắc identifier bắt đầu bằng chữ mâu thuẫn với temp view bắt buộc `_v_...`, khiến MERGE thất bại hoặc buộc bỏ qua validation. | Tách validator cho external identifier và generated internal temp-view name; chỉ cho phép mẫu `_v_...` đã được sanitize. |
| GATE-003 | P1 | `.cursor/skills/vsvn-notebook-library/SKILL.md:43,55-56` | Retry blind append sau ambiguous commit có thể tạo nhiều dòng `ctrl_log_table_run` cho cùng logical attempt. | Dùng idempotency key cùng MERGE/deduplication, hoặc không retry append khi trạng thái commit không xác định. |
| GATE-004 | P1 | `.cursor/skills/vsvn-extract-notebook/SKILL.md:144`; `.cursor/skills/vsvn-notebook-library/SKILL.md:99` | `json.load()` không phát hiện lỗi cú pháp code cell hay lỗi contract `%run`/exit trước khi deploy. | Bắt buộc compile các Python code cell sau khi xử lý magic và yêu cầu Fabric DEV smoke cho `%run` cùng nhánh `NO_DATA`/exit đối với notebook mới. |
| GATE-005 | P1 | `.cursor/skills/vsvn-extract-notebook/SKILL.md:48` | `collect()` trên aggregate theo source object/key name không có giới hạn cardinality có thể gây OOM driver F16 và kéo dài thời gian giữ lock. | Chỉ collect miền hữu hạn có cap được enforce; nếu không, dùng scalar summary hoặc yêu cầu evidence cardinality. |

P2/P3: `P2=1`, `P3=0`.
