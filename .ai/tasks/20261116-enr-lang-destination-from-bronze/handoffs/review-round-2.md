# Codex review handoff: 20261116-enr-lang-destination-from-bronze, round 2

You are the VSVN Review Coordinator. Use the project agents in `.codex/agents/`.

Confirm the active model is `gpt-5.6-sol` with `medium` reasoning. Stop and report a model mismatch instead of silently substituting.

Read `architecture.md` when it exists, the open items in `decision.md`, and the implementation diff. Do not read the rest of the repository, past reviews, or evidence files unless one finding depends on a named path.

For round 1, invoke every reviewer named in `review_plan.required_reviewers` independently. Spawn each project custom agent without a full-history fork and without another specialist's findings. For round 2, use the generated round-1 carry-over at the end of this prompt: pass each specialist only the round-1 P0/P1 findings it owns, their dispositions, and the diff of the files listed as changed since round 1 (`git diff -- <path>`, or the file itself when untracked). Invoke `risk-gate` after the specialist results when task state requires it. Risk-gate reads those findings and the diff, not the whole repository.

Specialists are read-only. Do not edit repository files.

Return one short consolidated Markdown report:

1. Model and reviewer manifest.
2. Gate verdict: `PASS`, `FIX_REQUIRED`, `EVIDENCE_REQUIRED`, or `USER_DECISION`.
3. Deduplicated P0/P1 findings: ID, severity, `file:line`, one-sentence failure, one-sentence fix.
4. P2/P3 as a count.
5. One probe line when evidence is missing.

Do not promote style issues to P0/P1. Do not write a repository tour.

## Round 1 carry-over

`vv.py` generated this block. Use it instead of opening past review files. Re-check each round-1 P0/P1 against its disposition, then review only the changed files below for regressions caused by the fixes.

### Round 1 P0/P1 findings

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P0 | `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb:117` | State dùng thời gian thay cho `version`, nên event version cao đến muộn có thể bị loại vĩnh viễn. | Sắp thứ tự bằng `version`, `EventProcessedUtcTime`, `event_id` và kiểm thử replay hai lần. |
| GATE-002 | P1 | `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb:117,232` | Các tên `sources`, `TABLE_SOURCE`, `_crawled_at` không tồn tại làm notebook lỗi trước khi xử lý. | Loại source routing cũ; dùng `TABLE_EVENT_TYPE` và `_event_processed_at` nhất quán. |
| GATE-003 | P1 | `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb:164` | Projection làm mất `_src_version`, khiến bước chọn bản ghi mới nhất lỗi trước MERGE. | Giữ `_src_version` xuyên suốt projection, state và MERGE. |
| GATE-004 | P1 | `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb:164` | JSON `destinations` lỗi bị chuyển thành NULL mà không kích hoạt fail gate. | Thêm cờ parse failure và đưa vào reject/fail policy. |
| GATE-005 | P1 | `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb:117,164` | `event_id` rỗng hoặc tie toàn bộ tuple làm kết quả `row_number()` không xác định. | Reject ID rỗng và fail tie xung đột, hoặc thêm tie-breaker được phê duyệt. |
| GATE-006 | P1 | `notebooks/NB_CREATE_DDL.ipynb:5967,5990` | Crash sau overwrite có thể khiến retry trả `SKIP` cho rewrite chưa được kiểm chứng. | Lưu version/phase migration và resume validation hoặc RESTORE trước `SKIP`. |
| GATE-007 | P1 | `notebooks/NB_CREATE_DDL.ipynb:5967,5990`; `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb:23` | Lease 120 phút không heartbeat trong khi extract có thể chạy 780 phút, cho phép stale owner tiếp tục ghi. | Heartbeat, revalidate ownership trước mọi durable write/RESTORE và đồng bộ timeout. |
| GATE-008 | P1 | `.ai/tasks/20261116-enr-lang-destination-from-bronze/runtime-runbook.md:34` | Copy Job truncate-first không thể pause có thể xóa dữ liệu PostgreSQL rồi lỗi vì schema lệch. | Người dùng phải chọn pause job hoặc staging + atomic swap; nếu không phải quyết định chấp nhận rủi ro rõ ràng. |
| GATE-009 | P1 | `notebooks/NB_CREATE_DDL.ipynb:299` | Thiếu dấu phẩy giữa các tuple `FROM VALUES` làm seed watermark lỗi cú pháp. | Thêm dấu phẩy và chạy lại deterministic validation. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P0 | fixed | `_cdc_ts_ms` là `version`. State so `(version, EventProcessedUtcTime, event_id)`. | |
| GATE-002 | P1 | fixed | Bỏ `sources`, `TABLE_SOURCE`, `_crawled_at` trong code chạy. | |
| GATE-003 | P1 | fixed | `_src_version` được giữ qua các `select` tới MERGE. | |
| GATE-004 | P1 | fixed | JSON `destinations` hỏng tăng `_cn__` và FAIL trước MERGE. | |
| GATE-005 | P1 | fixed | `event_id` rỗng bị reject. Cùng bộ thứ tự mà payload khác thì dừng. | |
| GATE-006 | P1 | fixed | `SKIP` sau commit rewrite kiểm lại từ version trước; lệch thì `RESTORE`. | |
| GATE-007 | P1 | fixed | Lease rewrite 780 phút. Gia hạn và xác nhận chủ khoá trước khi ghi hoặc `RESTORE`. | |
| GATE-008 | P1 | fixed | Runbook B5 dừng Copy Job, chạy `enrgldpy`, `ALTER`, rồi mở lại. | |
| GATE-009 | P1 | fixed | Thêm dấu phẩy giữa tuple watermark trong `NB_CREATE_DDL`. | |

### Files changed since round 1

- docs/context/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md | modified
- notebooks/NB_CREATE_DDL.ipynb | modified
- notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb | modified
- tests/test_enr_extract_contract.py | modified
