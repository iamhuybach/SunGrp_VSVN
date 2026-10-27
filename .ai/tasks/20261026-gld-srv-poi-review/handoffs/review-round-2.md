# Codex review handoff: 20261026-gld-srv-poi-review, round 2

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

- `SQL-001` — **P1** — `notebooks/NB_GLD_SRV_POI_REVIEW.ipynb:99`: Duplicate rating rows or a multiplicative `multi_lang × review` join can violate the required one-row-per-`review_id` MERGE source and stop the run before writing. Fix: prove both source assumptions in Fabric DEV; if duplicates exist, remediate the source or obtain an explicit grain decision without selecting an arbitrary row.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SQL-001 | P1 | fixed | Probe `sql-001` trên Fabric DEV không trả dòng. Tiêu chí pass là 0 dòng. `evidence/results/sql-001.txt` | |

### Files changed since round 1

- notebooks/NB_CREATE_DDL.ipynb | entered the diff after round 1
- tests/test_enr_poi_contract.py | entered the diff after round 1
- tests/test_gld_srv_poi_contract.py | entered the diff after round 1
- tests/test_initial_ddl_contract.py | entered the diff after round 1
- tests/test_poi_entity_contract.py | entered the diff after round 1
