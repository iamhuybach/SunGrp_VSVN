# Codex review handoff: 20261021-refresh-gld-enr-poi-info, round 2

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

- `SPARK-001` — P1 — `notebooks/NB_ENR_POI_INFO.ipynb:241`: Removing or soft-deleting a rating, price, hours, or review row does not emit its `poi_id`, leaving stale gold values. Fix by unioning reverse-diff removal keys into the changed POIs while retaining the full-spine fallback when no baseline exists.
- `STATE-001` — P1 — `notebooks/NB_CREATE_DDL.ipynb:2331`: An existing inactive desired edge is skipped by `WHERE NOT EXISTS`, so verification and every retry fail, potentially after the DEV reset leaves gold empty. Fix by failing before mutations or deterministically reactivating exactly the three task-owned desired edges while holding the flow lock.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SPARK-001 | P1 | fixed | `_role_keys` lấy poi_id biến mất khỏi snapshot live của rating, price, hours, review và amenity. Không baseline thì trả cả spine. `ctx.changed` vẫn là `current.subtract(old)`. | |
| STATE-001 | P1 | fixed | `enrinfopy` đọc cạnh `EDGES_ON` trước INSERT/UPDATE. Dòng đã có mà không đúng một dòng `is_active = 1` thì raise và không ghi cạnh. Cell không tự bật cạnh (I7). | |

### Files changed since round 1

- notebooks/NB_CREATE_DDL.ipynb | modified
- notebooks/NB_ENR_POI_INFO.ipynb | modified
- tests/test_enr_poi_contract.py | modified
