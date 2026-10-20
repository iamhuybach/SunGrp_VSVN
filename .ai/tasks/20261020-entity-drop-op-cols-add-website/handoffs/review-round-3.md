# Codex review handoff: 20261020-entity-drop-op-cols-add-website, round 3

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
| STATE-004 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2127` | Khi `INSERT` hoặc validation lỗi, `finally` vẫn ghi `status='SUCCESS'` và xoá lock, che giấu patch thất bại và làm sai trạng thái recovery. | Chỉ ghi `SUCCESS` trên success path; exception path phải owner-guarded ghi `FAILED`/`error_message`, giải phóng lock rồi re-raise, kèm test success và failure. |
| STATE-005 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2067,2083-2094` | Hard crash sau khi commit lock có thể để lại UUID owner vĩnh viễn, khiến mọi retry với UUID mới không thể nhận lock. | Dùng stable execution ID cùng owner-checked lease/stale-lock recovery, hoặc cung cấp cơ chế recovery được phê duyệt có thể phân biệt lock stale/live an toàn. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-004 | P1 | fixed | `finally` ghi `FAILED` khi có exception, `SUCCESS` khi không. Exception được raise lại. | |
| STATE-005 | P1 | fixed | `LOCK` cố định `entweb-20261020-entity-edge`. Lần chạy sau nhận lại khoá của chính id đó hoặc khoá quá 90 phút. | |

### Files changed since round 2

- notebooks/NB_CREATE_DDL.ipynb | modified
- tests/test_poi_entity_contract.py | modified
