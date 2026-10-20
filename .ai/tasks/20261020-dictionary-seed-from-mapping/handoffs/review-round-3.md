# Codex review handoff: 20261020-dictionary-seed-from-mapping, round 3

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

## Round 2 carry-over

`vv.py` generated this block. Use it instead of opening past review files. Re-check each round-2 P0/P1 against its disposition, then review only the changed files below for regressions caused by the fixes.

### Round 2 P0/P1 findings

| ID | Severity | Location | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P1 | `.ai/tasks/20261020-dictionary-seed-from-mapping/runtime-runbook.md:28` | Không có diff hoặc nội dung R2 để chứng minh backup cũ không thể được tái sử dụng và làm rollback khôi phục dictionary sai lệch. | Cung cấp R2 có số dòng, thể hiện dừng khi backup tồn tại, danh sách cột tường minh và kiểm tra hai chiều `EXCEPT ALL = 0` trước mỗi `DROP`. |
| GATE-002 | P1 | `.ai/tasks/20261020-dictionary-seed-from-mapping/runtime-runbook.md:47` | Không có diff hoặc trình tự lệnh để chứng minh các rerun `p_apply=true` và assertions hoàn tất trước R10, rồi xác nhận lại pause/no-active-run trước resume. | Cung cấp đầy đủ đoạn từ rerun `p_apply=true` qua assertions đến R10/1H, gồm thứ tự thực thi và các kiểm tra pause/active-run. |

### Dispositions in decision.md

### GATE-001

`runtime-runbook.md` L23 dừng nếu `*_bak_20261020` đã tồn tại. L30–L35 tạo backup bằng `CREATE TABLE` (không `IF NOT EXISTS`) với cột tường minh. L41–L60 là bốn câu `EXCEPT ALL` hai chiều, mỗi câu phải 0 dòng trước mọi `DROP`.
### GATE-002

Thứ tự trong `runtime-runbook.md`: L74 chạy lại idempotency khi 1H vẫn tắt và Monitor không có run active; L75 R10 chỉ bật `PL_VV_TRANS_SLV_TO_SLV_1H` sau kiểm tra đó. L99–L101 nhắc lại: `NB_SETUP_POI_ENTITY` rồi `NB_SETUP_POI_AMENITY`, `p_apply` = `true`, kỳ vọng `inserted=0`, `drift=0`, trước R10.

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

### Files changed since round 2

none: no scoped file changed since round 2
