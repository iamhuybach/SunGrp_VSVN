# Codex review handoff: 20261020-entity-drop-op-cols-add-website, round 2

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
| STATE-001 | P1 | `.ai/tasks/20261020-entity-drop-op-cols-add-website/runtime-runbook.md:76,79-88` | Lock `UPDATE` không có assertion thực thi và nhánh thiếu flow row bỏ qua lock, nên `DROP`/`DELETE` vẫn có thể chạy khi NB_00 đang hoạt động. | Tạo/giành flow lock kể cả khi flow row chưa tồn tại, xác nhận ownership bằng bước thực thi trước destructive block riêng, giữ lock đến khi reset hoàn tất. |
| STATE-002 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2066-2078` | Contact-edge patch chỉ kiểm tra lock rồi `INSERT` mà không giữ lock, cho phép NB_00 quan sát topology thay đổi giữa run. | Giữ flow lock xuyên suốt `INSERT`, validation và release, hoặc loại bỏ writer trực tiếp và chỉ dùng setup path có lock. |
| STATE-003 | P1 | `.ai/tasks/20261020-entity-drop-op-cols-add-website/runtime-runbook.md:137-149` | Rollback deploy code cũ và đổi edge trước khi lấy lock, làm lộ trạng thái code/config/schema không tương thích cho run đồng thời. | Lấy flow lock trước mọi thay đổi rollback, giữ xuyên suốt deploy, đổi edge, reset và rebuild; chỉ release sau validation. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-001 | P1 | fixed | Runbook R3a nhận khoá cả khi chưa có dòng flow, R3b đọc lại `lock_exec_id` trước DROP, R3d nhả sau khi kiểm tra. | |
| STATE-002 | P1 | fixed | `entwebpy` giữ khoá từ trước INSERT đến `finally`. Không còn cửa sổ INSERT khi khoá trống. | |
| STATE-003 | P1 | fixed | Rollback chạy R3a/R3b trước revert và trước UPDATE cạnh. DROP nằm trong lúc còn khoá. Nhả ngay trước notebook cũ vì notebook đó tự nhận khoá. | |

### Files changed since round 1

- notebooks/NB_CREATE_DDL.ipynb | modified
- tests/test_poi_entity_contract.py | modified
