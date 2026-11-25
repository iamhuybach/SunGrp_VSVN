# Codex review handoff: 20261125-legacy-init-destination-and-poi-name, round 2

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

- `GATE-001` — P1 — `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb:123`, `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1094`: `poi_name=NULL` có thể làm đổi toàn bộ `row_hash` nếu Fabric không bỏ trường null khi `to_json`, gây mass rewrite và chuyển ownership các dòng khớp `LEGACY_INIT`. Fix: chứng minh JSON/hash không đổi trên Fabric DEV, hoặc loại `poi_name` khỏi hash hay cố định null serialization.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | Fabric DEV: `spark.sql.jsonGenerator.ignoreNullFields=true`. `old_json` bằng `new_json`. `old_hash` bằng `new_hash`. Verdict `null_poi_name_hash_unchanged`. `poi_name` null không đổi `to_json` và không đổi hash. | |

### Files changed since round 1

none: no scoped file changed since round 1
