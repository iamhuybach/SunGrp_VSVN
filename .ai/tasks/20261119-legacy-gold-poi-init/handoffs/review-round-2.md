# Codex review handoff: 20261119-legacy-gold-poi-init, round 2

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

- `GATE-001` — **P0** — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:216`: `drift_n` luôn bằng 0 và PLAN/RUN dùng map khác nhau, nên retry với pin mới có thể ghi payload vào sai `poi_id`. Fix: tính drift null-safe trên toàn bộ field định danh, chặn RUN khi drift khác 0 và dùng cùng effective map cho PLAN/RUN.
- `GATE-002` — **P1** — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:270`: PLAN coi khóa soft-deleted là có thể insert/được dùng làm parent trong khi RUN bỏ qua mọi khóa đã tồn tại. Fix: loại cả khóa live và deleted khỏi planned inserts và parent sets cho info/multi-lang.
- `GATE-003` — **P1** — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:221`: persisted map được join mà không assert grain duy nhất theo `legacy_poi_id`, nên duplicate có thể nhân dòng downstream. Fix: thêm preflight uniqueness assertion hoặc cung cấp probe đạt `bad_key_n = 0`.
- `GATE-004` — **P1** — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:298`: lỗi sau partial commit re-raise trước khi in summary, làm mất thông tin cần cho recovery. Fix: in failure summary gồm stage, version và count đã commit trước khi re-raise, đồng thời giữ nguyên exception gốc.
- `GATE-005` — **P1** — `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1247`: MERGE retry không kiểm tra lại quyền sở hữu lease, nên execution cũ có thể commit sau khi lock đã chuyển chủ. Fix: fence từng retry bằng refresh/ownership check nguyên tử hoặc tắt retry cho write path này.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P0 | fixed | PLAN và RUN dùng cùng map hiệu lực. `drift_n` so sánh null-safe mọi cột định danh. RUN dừng khi drift khác 0. | |
| GATE-002 | P1 | fixed | `to_insert` và parent bỏ mọi khóa đã có, kể cả `deleted_at` khác NULL. | |
| GATE-003 | P1 | fixed | Dừng khi `legacy_poi_id` trùng trên map nguồn hoặc map đã ghi. | |
| GATE-004 | P1 | fixed | Lỗi in summary với `failed_stage` và số đã commit trước khi raise. | |
| GATE-005 | P1 | fixed | `merge_target` gọi `refresh_flow_lock` trước mỗi lần thử, kể cả retry. | |

### Files changed since round 1

- notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | modified
- notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb | modified
- tests/test_legacy_gold_poi_init_contract.py | modified
