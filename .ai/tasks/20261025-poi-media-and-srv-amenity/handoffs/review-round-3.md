# Codex review handoff: 20261025-poi-media-and-srv-amenity, round 3

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
| STATE-001 | P1 | `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1609` | Lease chỉ được refresh trước `ensure_target`; run có thể mất lease trong hoặc sau bước này rồi vẫn thực hiện `merge_target`, ghi đè snapshot mới hơn. | Refresh lại sau `ensure_target` và ngay trước `merge_target`; cập nhật test để bắt buộc thứ tự này. Nếu MERGE có thể kéo dài quá lease, cần atomic fencing hoặc bảo đảm lease còn hiệu lực đến lúc commit. |
| SPARK-001 | P1 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:113` | Nếu aggregation hoặc `ctx.warn` lỗi sau khi cache được materialize, `unpersist()` bị bỏ qua, khiến cache tồn tại trong Fabric session và gây áp lực bộ nhớ F16 khi retry. | Bọc toàn bộ metrics block sau `persist()` bằng `try/finally` và gọi `unpersist()` trong `finally`. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-001 | P1 | fixed | Vòng 2: `refresh_flow_lock` một lần trước `ensure_target` và một lần nữa ngay trước `merge_target`. Lease 90 phút được gia hạn lại lúc bắt đầu MERGE. Vòng review đã hết cap 2, chưa có vòng 3. | |
| SPARK-001 | P1 | fixed | Vòng 2: `unpersist()` nằm trong `finally` sau `persist()`. Vòng review đã hết cap 2, chưa có vòng 3. | |

### Files changed since round 2

- notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | modified
- notebooks/NB_SLV_POI_MEDIA_INFO.ipynb | modified
- tests/test_poi_media_amenity_contract.py | modified
