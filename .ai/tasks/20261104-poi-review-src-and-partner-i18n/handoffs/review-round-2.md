# Codex review handoff: 20261104-poi-review-src-and-partner-i18n, round 2

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

| ID | Severity | file:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4800`, `:4823` | An unexpected inactive review edge passes precheck, but after the expected-edge update the exact-map postcheck fails permanently, making retries unable to forward-recover. | Reject unexpected edges before the first write, or validate that expected edges occur once and all target edges are inactive; add the corresponding retry test. |
| GATE-002 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4771`, `:4929` | If lock acquisition commits and the following owner-read action fails before `held=True`, cleanup is skipped and scheduled work remains blocked until lease expiry. | In both migration cells, perform token-guarded cleanup based on the persisted lock token and preserve the original exception if cleanup also fails. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | Cạnh lạ mọi is_active bị từ chối trước UPDATE ctrl. | |
| GATE-002 | P1 | fixed | `owns_lock` bật ngay sau UPDATE khoá; finally nhả theo token và giữ lỗi gốc. | |

### Files changed since round 1

- notebooks/NB_CREATE_DDL.ipynb | modified
- tests/test_enr_poi_contract.py | modified
- tests/test_gld_srv_poi_contract.py | modified
