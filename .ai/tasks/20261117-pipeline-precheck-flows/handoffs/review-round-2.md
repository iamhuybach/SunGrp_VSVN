# Codex review handoff: 20261117-pipeline-precheck-flows, round 2

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
| PIPE-001 | P1 | `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json:21`; `pipelines/PL_VV_TRANS_SLV_TO_GLD_30M/PL_VV_TRANS_SLV_TO_GLD_30M.json:21` | Binding guards call Fabric `or()` with four arguments, so evaluation can fail before the SQL gate. | Replace with nested binary `or()` calls and add expression-arity coverage. |
| SQL-001 | P1 | `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json:1` | Query grain includes `src_schema`, but dispatch matches only `src_tbl` and passes a fixed schema, allowing duplicate or misrouted execution. | Constrain the query to the canonical schema or consistently match and pass the full schema/table identity. |
| SQL-002 | P1 | `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json:58`; `pipelines/PL_VV_TRANS_SLV_TO_GLD_30M/PL_VV_TRANS_SLV_TO_GLD_30M.json:58` | Nullable `status` values are excluded by `<>` and `NOT IN`, potentially producing a false `NO_DATA` decision. | Make predicates null-safe or prove `status` is non-nullable and cannot contain nulls. |
| PIPE-002 | P1 | `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json:1` | Continue-after-failure behavior of the sequential `ForEach` is unproven; an early failure may starve later sources. | Provide Fabric DEV C4 evidence or redesign the orchestration to prevent starvation while propagating failure. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| PIPE-001 | P1 | fixed | `or()` binding ENR và GLD lồng hai đối số. Test `test_expression_calls_are_binary`. | |
| SQL-001 | P1 | fixed | Mỗi `Get_Config_*` lọc `src_schema = 'lh_vv_bronze.dbo'` và một `src_tbl`. | |
| SQL-002 | P1 | fixed | `COALESCE(status, '')` trên `me` và `up` của ENR và GLD. NULL không bị loại khỏi quyết định có việc. | |
| PIPE-002 | P1 | fixed | Bốn `ForEach_*` nối `Completed`; `Fail_Source_*` phụ thuộc `Failed`. Nguồn sau vẫn chạy, pipeline vẫn Failed. | |

### Files changed since round 1

- pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json | modified
- pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json | modified
- pipelines/PL_VV_TRANS_SLV_TO_GLD_30M/PL_VV_TRANS_SLV_TO_GLD_30M.json | modified
- tests/test_pipeline_precheck_contract.py | modified
