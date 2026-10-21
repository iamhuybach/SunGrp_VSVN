# Codex review handoff: 20261021-refresh-gld-enr-poi-info, round 3

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

- `SQL-001` — P1 — `notebooks/NB_ENR_POI_INFO.ipynb:240`: The entity spine does not enforce one non-null row per `poi_id`, so duplicate or null keys can fail the append PK check on every retry. Fix: prove the source invariant in DEV or deterministically reduce the spine to exactly one non-null row per `poi_id`.
- `SQL-002` — P1 — `notebooks/NB_ENR_POI_INFO.ipynb:199`: Multiple live Vietnamese i18n rows for one `business_service_id` can multiply partner candidates at the join on line 256. Fix: prove uniqueness in DEV or deterministically select one row per service and reject conflicting values.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SQL-001 | P1 | rejected-false-positive | Probe DEV `evidence/results/sql-001-sql-002.txt` (2026-10-21): câu SQL-001 trả 0 dòng. Không có `poi_id` null hoặc trùng trên `slv_poi_entity_non_enrich`. Node vẫn chặn bằng `pk_duplicate` nếu sau này có trùng. | |
| SQL-002 | P1 | rejected-false-positive | Cùng file kết quả: câu SQL-002 trả 0 dòng. Không có `business_service_id` null hoặc nhiều hơn một dòng `locale = vi` chưa deleted. | |

### Files changed since round 2

none: no scoped file changed since round 2
