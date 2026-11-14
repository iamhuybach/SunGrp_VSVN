# Codex review handoff: 20261112-enr-poi-append-to-merge, round 2

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
| STATE-001 | P1 | `notebooks/NB_CREATE_DDL.ipynb:5776` | Một lần refresh trước vòng lặp không bảo đảm quyền sở hữu lease trước từng `ALTER TABLE`, cho phép stale owner ghi bảng thứ hai. | Đặt `_refresh_lock()` ngay trước mỗi `ALTER`, giữ refresh trước UPDATE config và kiểm thử đúng vị trí. |
| SPARK-001 | P1 | `notebooks/NB_CREATE_DDL.ipynb:5804` | Cleanup lock trong `finally` có thể che lỗi gốc và để pipeline bị khóa tới khi lease hết hạn. | Bọc cleanup bằng `try/except`, bảo toàn lỗi gốc và thêm test cho cả body-failure lẫn cleanup-failure. |
| SPARK-002 | P1 | `notebooks/NB_ENR_POI_INFO.ipynb:160` | Full snapshot mỗi 15 phút chưa có bằng chứng đáp ứng shared F16 và SLA, có nguy cơ spill, throttling, OOM hoặc backlog. | Chạy DEV `DRY_RUN` khi schedule tạm dừng và thu duration, rows/bytes, shuffle, spill, peak memory và capacity utilization. |
| SQL-001 | P1 | `notebooks/NB_ENR_POI_INFO.ipynb:164` | Null/trùng `poi_id` ở entity hoặc nhiều rating/price trên một key có thể nhân bản nguồn và làm PK/MERGE gate thất bại. | Chứng minh các nguồn duy nhất bằng probe hoặc lọc/deduplicate có thứ tự xác định. |
| SQL-002 | P1 | `notebooks/NB_ENR_POI_REVIEW.ipynb:103` | `rv_all` chỉ loại key null, không xử lý nhiều dòng cùng `review_id`, nên MERGE có thể nhận nguồn không duy nhất. | Chứng minh `review_id` duy nhất hoặc chọn một dòng xác định cho mỗi key. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-001 | P1 | fixed | `enrmergepy` gọi `_refresh_lock()` ngay trước từng `ALTER`, rồi một lần nữa trước `UPDATE` config. `test_enr_merge_patch_cell_guards` khóa vị trí đó. | |
| SPARK-001 | P1 | fixed | `_release_lock` bọc lệnh nhả khoá. Test chạy cả lỗi thân cell và lỗi lúc nhả khoá. | |
| SPARK-002 | P1 | fixed | `info-dry-run.txt`: sau `enrmergepy`, `DRY_RUN` + `p_force = true` kết thúc SUCCESS trong 53s, nguồn 20829 dòng, không có dòng OOM, throttling, hay spill. Log không có bytes, shuffle, spill, peak memory, capacity. | |
| SQL-001 | P1 | fixed | `source-uniqueness.txt` 2026-11-14: entity, rating, price đều `null_key_count = 0` và `row_count = distinct_key_count`. Không thêm dedupe. | |
| SQL-002 | P1 | fixed | Cùng file: `slv_3p_poi_review.review_id` 109682 dòng, 0 null, 109682 khoá phân biệt. Không thêm dedupe. | |

### Files changed since round 1

- notebooks/NB_CREATE_DDL.ipynb | modified
- tests/test_enr_poi_contract.py | modified
