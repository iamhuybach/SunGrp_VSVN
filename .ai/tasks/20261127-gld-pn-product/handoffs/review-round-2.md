# Codex review handoff: 20261127-gld-pn-product, round 2

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

- `SQL-001` — P1 — `notebooks/NB_CREATE_DDL.ipynb:7366`: All missing control edges receive the same `MAX(id) + 1`, potentially corrupting control-row identity. Fix: carry `seq` into the MERGE source and assign `COALESCE(MAX(id), 0) + s.seq`.
- `SQL-002` — P1 — `notebooks/NB_GLD_SRV_PRODUCT_OFFER.ipynb:461`: The union lacks an enforced `product_id` uniqueness gate, so cross-branch collisions can create duplicate MERGE source keys. Fix: call `_require_unique` after `unionByName` and before enrichment/write.
- `SQL-003` — P1 — `.ai/tasks/20261127-gld-pn-product/evidence/probes/p7_gld_product_offer_readiness.sql:64`: P-7 checks destination duplicates for unused/deleted source keys and can incorrectly block deployment. Fix: derive candidate POIs only from effective live holiday and hotel rows before checking duplicates.
- `SPARK-001` — P1 — `notebooks/NB_CREATE_DDL.ipynb:7300`: A failure during the owner read after lease acquisition skips cleanup because `held` is still false, leaving `_GLD30` locked for up to 90 minutes. Fix: set `held = True` immediately after the acquisition update and clear it only when a successful owner read proves another owner.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SQL-001 | P1 | fixed | Cạnh mới lấy `COALESCE(MAX(id), 0) + s.seq`. | |
| SQL-002 | P1 | fixed | `_require_unique` trên `product_id` ngay sau union, trước join destination. | |
| SQL-003 | P1 | fixed | P-7 chỉ lấy `poi_id` từ dòng holiday và hotel còn sống sau U-04. | |
| SPARK-001 | P1 | fixed | `held = True` ngay sau UPDATE chiếm khoá. Chỉ hạ `held` khi đọc owner thấy chủ khác. | |

### Files changed since round 1

- notebooks/NB_CREATE_DDL.ipynb | modified
- notebooks/NB_GLD_SRV_PRODUCT_OFFER.ipynb | modified
