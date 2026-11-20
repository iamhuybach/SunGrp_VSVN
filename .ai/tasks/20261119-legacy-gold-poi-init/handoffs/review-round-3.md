# Codex review handoff: 20261119-legacy-gold-poi-init, round 3

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

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P1 | `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:223` | So sánh `full_outer` tính các dòng source-only mới là drift, khiến lần RUN đầu với map rỗng luôn dừng. | Thêm marker hai phía, chỉ tính drift khi persisted row bị thiếu nguồn hoặc xung đột field; giữ source-only trong tập fresh insert và bổ sung test tương ứng. |
| GATE-004 | P1 | `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:164` | MERGE có thể đã commit nhưng lỗi đọc history làm summary thiếu version/count; lỗi cleanup hoặc release lock còn có thể che exception gốc. | Đối soát best-effort theo tag `LEGACY_INIT:<exec_id>` và `v_pre`, báo trạng thái commit hoặc `UNKNOWN`, đồng thời cô lập lỗi cleanup/unlock để giữ exception gốc. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | Drift chỉ tính dòng đã ghi bị thiếu nguồn hoặc lệch field. Dòng chỉ có ở nguồn vẫn là insert. Map rỗng không còn drift. | |
| GATE-004 | P1 | fixed | Sau MERGE, đối soát history theo tag `LEGACY_INIT` và `v_pre`. Lỗi history ghi `UNKNOWN`. Lỗi cleanup và nhả khóa không che exception gốc. | |

### Files changed since round 2

- notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb | modified
- tests/test_legacy_gold_poi_init_contract.py | modified
