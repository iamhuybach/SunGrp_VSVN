# Codex review handoff: 20261126-legacy-init-enriched-cols-and-dest-portal, round 2

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

- `SPARK-001` — P1 — `notebooks/NB_CREATE_DDL.ipynb:6967`: A failed MERGE leaves session-scoped Delta commit metadata active, so a later commit may be falsely tagged and corrupt recovery/audit attribution. Wrap the MERGE in `try/finally` and always unset `spark.databricks.delta.commitInfo.userMetadata` while preserving the original exception.
- `SPARK-002` — P1 — `notebooks/NB_CREATE_DDL.ipynb:6894`: Driver loss or hard cancellation can retain the extraction watermark lock for the hard-coded 780 minutes, exceeding the 30–60 minute SLA. Use the canonical bounded extraction-lock timeout and add a DEV cancellation/reacquisition check to the runtime runbook.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SPARK-001 | P1 | fixed | `finally` của `destportalpy` gỡ `userMetadata` khi MERGE lỗi, rồi mới nhả khoá. | |
| SPARK-002 | P1 | fixed | Hạn khoá lấy `LEASE_MINUTES = 90`, cùng mốc `LOCK_TIMEOUT_DEFAULT_MIN`. Runbook sẽ có bước chiếm lại khoá sau khi hủy giữa chừng. | |

### Files changed since round 1

- notebooks/NB_CREATE_DDL.ipynb | modified
- tests/test_enr_poi_contract.py | modified
