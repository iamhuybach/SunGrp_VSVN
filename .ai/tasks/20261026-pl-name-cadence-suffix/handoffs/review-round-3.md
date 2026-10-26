# Codex review handoff: 20261026-pl-name-cadence-suffix, round 3

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

| ID | Severity | file:line | Failure | Fix |
|---|---|---|---|---|
| GATE-003 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4143` | Fast path có thể đọc lock hết hạn, thua race với owner vừa refresh, không nhả được lock nhưng vẫn báo hội tụ vì không đọc lại trạng thái. | Sau conditional release, đọc lại đúng một cặp lock; chỉ tiếp tục khi owner là `NULL`, dừng với live owner và retry có giới hạn nếu vẫn hết hạn. |
| GATE-002 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4136` | Fast path chạy trước `_issues`, nên duplicate hoặc clash dưới tên mới không được phát hiện và trạng thái sai vẫn được báo thành công. | Chạy `_issues(old, new)` trước fast path và trước mọi write; dừng khi có bất kỳ issue nào. |
| SPARK-001 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4187` | Lock `UPDATE` có thể đã commit nhưng lỗi khi `collect()` xảy ra trước `held=True`, khiến `finally` bỏ cleanup và giữ lock `RUNNING` trong 35/90 phút. | Đánh dấu cần cleanup trước `UPDATE`, cleanup theo owner `LOCK`, đồng thời giữ nguyên lỗi gốc nếu cleanup cũng thất bại. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-003 | P1 | fixed | Sau khi nhả khoá hết hạn, đọc lại đúng một cặp. Chỉ báo đã đổi khi `lock_exec_id` là NULL. Owner còn sống thì dừng. Hết hạn thì thử lại tối đa 3 lần. | |
| GATE-002 | P1 | fixed | `_issues(old, new)` chạy trước nhánh đã đổi và trước mọi ghi. Trùng khoá logic hoặc lệch cặp thì dừng, không báo đã đổi. | |
| SPARK-001 | P1 | fixed | `held = True` trước `UPDATE` nhận khoá. `finally` nhả theo `lock_exec_id = LOCK`. Cleanup lỗi không che lỗi gốc. | |

### Files changed since round 2

- notebooks/NB_CREATE_DDL.ipynb | modified
- notebooks/NB_SETUP_POI_AMENITY.ipynb | entered the diff after round 2
- pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json | entered the diff after round 2
- tests/test_gld_srv_poi_contract.py | entered the diff after round 2
- tests/test_initial_ddl_contract.py | entered the diff after round 2
- tests/test_poi_amenity_contract.py | entered the diff after round 2
- tests/test_poi_media_amenity_contract.py | entered the diff after round 2
