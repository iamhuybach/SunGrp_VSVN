# Codex review handoff: 20261019-amenity-raw-key-only, round 3

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

- `STATE-001` — P1 — `notebooks/NB_SLV_POI_AMENITY.ipynb:205`, `tests/test_poi_amenity_contract.py:380`: `legacy` chỉ được ghi metric, nên dictionary chứa đủ 41 key mới cùng các key legacy vẫn vượt coverage gate và có thể chạy RECOMPUTE/write trong trạng thái không đồng nhất. Fix: raise `QualityGateError` khi `legacy > 0` trước khi tạo output/write và đổi regression test mixed-state để yêu cầu failure.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-001 | P1 | fixed | `legacy > 0` ném `QualityGateError` trước khi tạo output. Test mixed-state yêu cầu `legacy_blocks_write`. | |

### Files changed since round 2

- notebooks/NB_SLV_POI_AMENITY.ipynb | modified
- tests/test_poi_amenity_contract.py | modified
