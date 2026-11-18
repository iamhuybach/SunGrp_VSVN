# Codex review handoff: 20261118-amenity-poi-id-align, round 2

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
| SQL-001 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2211`, `:2233`, `:2260` | Edge đã tồn tại với `load_mode != 'RECOMPUTE'` có thể được kích hoạt mà không sửa mode, trong khi post-check vẫn báo thành công. | Kiểm tra hoặc cập nhật `load_mode` thành `RECOMPUTE`, rồi đưa trường này vào post-check. |
| SQL-002 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2176`, `:2211` | Hai edge vật lý trùng nhau bị gom thành một dòng `n=2`, khiến guard `len(hits) == 1` không chặn trước khi ghi. | Trước mọi write, yêu cầu `len(hits) == 1` và `hits[0]['n'] == 1`. |
| SPARK-001 | P1 | `notebooks/NB_SLV_POI_AMENITY.ipynb:292` | Hai `collect()` không giới hạn đưa toàn bộ dictionary key và nhãn sống lên driver, có thể làm cạn bộ nhớ Fabric F16 trước quality gate/write. | Phát hiện duplicate bằng phép `groupBy`/join phân tán và chỉ collect diagnostic sample có `orderBy(...).limit(20)`. |

### Dispositions in decision.md

- SQL-001: no details found
- SQL-002: no details found
- SPARK-001: no details found

### Files changed since round 1

none: no scoped file changed since round 1
