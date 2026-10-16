# Codex review handoff: 20261016-ref-amenities-poi-amenity, round 2

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

- `SPARK-001` — **P1** — `notebooks/NB_SLV_POI_AMENITY.ipynb:158`: Khi các POI chỉ có cờ không khớp hoặc giá trị null/false hợp lệ, điều kiện `joined > 0` và `n == 0` làm notebook lỗi trước MERGE, khiến RECOMPUTE không thể soft-delete các amenity cũ. Xóa quality gate `if joined and not n`, cho phép DataFrame rỗng đi qua `run_node` và ghi metric `rows=0` vì không có kết quả khớp là trạng thái hợp lệ.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SPARK-001 | P1 | fixed | Bỏ `if joined and not n` trong `notebooks/NB_SLV_POI_AMENITY.ipynb` cell `d1amenbuild`. Metric `rows` vẫn ghi 0. DataFrame rỗng là trạng thái hợp lệ. | |

### Files changed since round 1

- notebooks/NB_SLV_POI_AMENITY.ipynb | modified
- tests/test_poi_amenity_contract.py | modified
