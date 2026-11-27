# Codex review handoff: 20261127-slv-pn-product-l2-transform, round 2

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
| STATE-002 | P1 | `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1109` | Tên `deleted_flag` không hợp lệ chỉ bị phát hiện sau khi `ensure_target` đã tạo hoặc đổi schema, để lại trạng thái dở dang và retry tiếp tục thất bại. | Kiểm tra quy tắc tên cờ trong validation trước write và thêm test chứng minh cờ không hợp lệ không tạo bảng hoặc commit schema. |
| SPARK-001 | P1 | `.ai/tasks/20261127-slv-pn-product-l2-transform/task-state.yaml:14` | `runtime_required: false` trái với bằng chứng runtime bắt buộc tại `architecture.md:446`, nên MERGE Delta, UDF, diff parity và no-commit rerun chưa được xác minh trên Fabric. | Đặt `runtime_required: true` và thực hiện các probe Fabric DEV R1–R3 đã quy định trong architecture. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-002 | P1 | fixed | `_flag_name_ok` chạy trong `add_row_hash` và trong `run_node` trước `ensure_target`. Test `test_invalid_flag_name_rejected_before_schema_write`. | |
| SPARK-001 | P1 | fixed | `runtime_required` = true. Probe đọc R3: `evidence/probes/pnl2_invariants.py`. R1 và R2 nằm trong runbook vì có ghi bảng tạm. Người dùng chạy trên Fabric DEV. | |

### Files changed since round 1

- notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | modified
- tests/test_slv_pn_product_l2_contract.py | modified
