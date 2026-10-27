# Codex review handoff: 20261027-platform-operator-guide, round 2

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

- `REV-001` — **P1** — `docs/context/03_OPERATOR_GUIDE.md:382`: Quy trình thêm bảng L1 mới không backfill khi nguồn đã có `last_src_version`, nên lần chạy incremental có thể bỏ vĩnh viễn toàn bộ dữ liệu lịch sử nhưng vẫn tiến watermark. Bổ sung bước chạy riêng `table_filter="<new trg_tbl>"` với `full_reload=True`, phân biệt với nguồn hoàn toàn mới dùng `allow_full_scan=True`, đồng thời cập nhật procedure tương ứng tại `.cursor/skills/vsvn-operator-docs/SKILL.md:71`.

### Dispositions in decision.md

| REV-001 | P1 | fixed | `03_OPERATOR_GUIDE.md` §4.4 và `vsvn-operator-docs` mục thêm bảng: raw đã có `last_src_version` thì `table_filter` + `full_reload = True`; raw chưa có con trỏ thì `allow_full_scan = True`. | |

### Files changed since round 1

- .cursor/skills/vsvn-operator-docs/SKILL.md | modified
- docs/context/03_OPERATOR_GUIDE.md | modified
