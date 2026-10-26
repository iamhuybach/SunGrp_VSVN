# Codex review handoff: 20261026-pl-name-cadence-suffix, round 2

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

| ID | Severity | file:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P0 | `notebooks/NB_CREATE_DDL.ipynb:4124`; `notebooks/NB_SETUP_POI_ENTITY.ipynb:944`; `notebooks/NB_SETUP_POI_AMENITY.ipynb:732` | Setup có thể tạo `wm_flow__<new>` giữa precheck và rename; do Delta không bảo đảm uniqueness, migration có thể commit dòng trùng rồi mới phát hiện corruption. | Serialize cả `old_id` và `new_id` hoặc dùng protocol tạo/rename conflict-safe dùng chung cho mọi writer; thêm concurrency test chứng minh luôn còn tối đa một dòng mới. |
| GATE-002 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4102`, `:4177` | Duplicate logical key sẵn có trong cùng old/new `pl_name` chỉ bị phát hiện sau khi `UPDATE CFG` đã commit. | Trước mọi write, group cả hai tên theo complete logical key và dừng nếu bất kỳ nhóm nào có `count(*) > 1`. |
| GATE-003 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4089`, `:4168`, `:4198` | Watermark malformed hoặc crash sau CFG commit có thể để new lock còn giữ, nhưng rerun fast path vẫn báo hội tụ mà không kiểm tra hoặc recovery. | Cả pre-write và idempotent path phải xác nhận đúng một cặp `watermark_id`/`src_tbl`, yêu cầu lock-free, dừng với live owner và guarded-recover expired owner; thêm crash-recovery test. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P0 | fixed | Đổi id khoá chỉ khi cùng câu lệnh đếm `new_id` = 0; nhận khoá cả `old_id` và `new_id` nếu dòng đã có. Test `test_pl_cadence_rename_is_conditional`. | |
| GATE-002 | P1 | fixed | `_issues` nhóm `pl_name, src_schema, src_tbl, trg_schema, trg_tbl` và dừng khi `count(*) > 1` trước mọi ghi. Test `test_pl_cadence_dup_key_before_write`. | |
| GATE-003 | P1 | fixed | Nhánh đã đổi yêu cầu đúng một cặp `watermark_id`/`src_tbl`, dừng nếu khoá còn sống, nhả khoá quá hạn. Test `test_pl_cadence_rerun_checks_lock`. | |

### Files changed since round 1

- notebooks/NB_CREATE_DDL.ipynb | modified
