# Codex review handoff: 20261127-slv-pn-product-l2-transform, round 3

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

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| STATE-002 | P1 | `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1109`; `tests/test_slv_pn_product_l2_contract.py:217` | `deleted_flag=""` vượt qua các validation dùng truthiness, nên `ensure_target` có thể chạy theo semantics mặc định và ghi trạng thái sai. | Xử lý mọi giá trị khác `None` là cấu hình cờ, từ chối tên rỗng/không hợp lệ trước write và thêm test thực thi chứng minh `ensure_target`/MERGE không được gọi. |
| SPARK-001 | P1 | `.ai/tasks/20261127-slv-pn-product-l2-transform/task-state.yaml:14` | `runtime_required` đã được sửa thành `true`, nhưng chưa có kết quả Fabric DEV để xác minh Delta MERGE, diff parity và rerun không tạo commit. | Chạy đầy đủ R1–R3 trên Fabric DEV và lưu kết quả; chỉ đóng finding khi mọi invariant đạt. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-002 | P1 | fixed | Mọi `deleted_flag` khác None đều là cờ đang bật. `reject_deleted_flag` chạy trước `add_row_hash`, `diff_counts`, `ensure_target` và `merge_target`. Chuỗi rỗng raise `ConfigError` và test chứng minh hai lời gọi ghi không chạy. Chưa có vòng review thứ ba. | |
| SPARK-001 | P1 | fixed | Fabric DEV 2026-11-27: R1 PASS, R2 0/0/0 và version giữ 1, R3 mọi count 0, cột đúng, `_is_deleted` không có, K3 `n = 0`. `evidence/results/r2_r3.txt`. | |

### Files changed since round 2

- notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | modified
- tests/test_slv_pn_product_l2_contract.py | modified
