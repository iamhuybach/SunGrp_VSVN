# Codex review handoff: 20261020-dictionary-seed-from-mapping, round 2

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

| ID | Severity | Location | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P1 | `.ai/tasks/20261020-dictionary-seed-from-mapping/runtime-runbook.md:28` | `CREATE TABLE IF NOT EXISTS` can reuse a stale backup whose row count matches current data, making rollback restore divergent dictionary state. | Before either `DROP`, prove backup/live schema and row equivalence in both directions with explicit-column `EXCEPT ALL`, or create uniquely named backups for the execution and verify them. |
| GATE-002 | P1 | `.ai/tasks/20261020-dictionary-seed-from-mapping/runtime-runbook.md:47` | The runbook resumes the hourly pipeline before the `p_apply=true` idempotency reruns, allowing a pipeline run to race or trip the active-run guard. | Move both idempotency reruns and assertions before R10, reconfirm pause/no active run immediately beforehand, and resume only after all checks pass. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | `runtime-runbook.md` R2: dừng nếu backup đã tồn tại; `CREATE TABLE` cột tường minh; `EXCEPT ALL` hai chiều = 0 dòng trước DROP. | |
| GATE-002 | P1 | fixed | Idempotency `p_apply=true` chuyển lên trước R10. Xác nhận 1H vẫn tắt rồi mới bật lại. | |

### Files changed since round 1

none: no scoped file changed since round 1
