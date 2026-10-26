# Codex review handoff: 20261025-poi-media-and-srv-amenity, round 2

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

| ID | Severity | Vị trí | Failure | Fix |
|---|---|---|---|---|
| STATE-001 | P1 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:169`; `notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb:101`; `notebooks/NB_GLD_SRV_POI_AMENITY.ipynb:91` | Run đã mất lease vẫn có thể MERGE snapshot cũ sau run mới hơn, làm target lùi trong khi watermark đã tiến. | Fence quyền sở hữu ngay trước target MERGE và edge-watermark commit; stale owner phải bị từ chối mọi durable write. |
| SQL-001 | P1 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:116` | Chưa có bằng chứng toàn bộ union source duy nhất theo `media_id`; URL partner trùng hoặc va chạm với key 3P sẽ làm MERGE thất bại. | Chứng minh uniqueness trên full build; nếu fail, xin quyết định nghiệp vụ về key hoặc xử lý duplicate xác định, không tự dedupe. |
| SPARK-001 | P1 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:112` | Năm action `count()` có thể đánh giá lại cùng lineage nhiều lần, gây rủi ro vượt cadence/SLA trên F16 dùng chung. | Gộp metric vào một aggregation, bỏ action thừa, hoặc materialize có cleanup rõ ràng. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-001 | P1 | fixed | `refresh_flow_lock` ngay trước `ensure_target`/`merge_target` trong `run_node` và ngay trước `advance_edges` trong `orchestrate`. Chủ cũ không ghi. | |
| SQL-001 | P1 | fixed | Full build trên DEV: `rows 1131`, `dup_media_id 0`. Không dedupe. `evidence/results/media_id_unique.txt`. | |
| SPARK-001 | P1 | fixed | Metric partner là hai `agg` trên một `persist`, rồi `unpersist`. `poi_without_cover` = 0 vì A8 luôn gán một cover. | |

### Files changed since round 1

- notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | entered the diff after round 1
- notebooks/NB_SLV_POI_MEDIA_INFO.ipynb | modified
- tests/test_poi_media_amenity_contract.py | modified
