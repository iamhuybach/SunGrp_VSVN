# Codex review handoff: 20261105-partner-hours-both-media-grain, round 2

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

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P1 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:176`; `notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb:81` | Fabric chấp nhận khóa `(media_id, poi_id)` nhưng PostgreSQL vẫn dùng `PRIMARY KEY (media_id)`, nên một `media_id` thuộc nhiều POI có thể làm sync thất bại và gây divergence. | Chuyển khóa và conflict target của PostgreSQL sang `(media_id, poi_id)`, hoặc chặn global duplicate `media_id` trong Fabric; nếu hoãn thì cần user chấp nhận risk rõ ràng. |
| GATE-002 | P1 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:128` | `countDistinct(key)` tạo thêm full-cardinality shuffle chưa có bằng chứng đáp ứng cadence trên shared F16. | Chỉ tính metric trong `DRY_RUN`, dùng phép đếm bounded/approximate, hoặc cung cấp DEV evidence đạt ngưỡng. |

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | backlog | PostgreSQL apps.srv_poi_media_gallery tôi sẽ sửa lại key là media và poi_id. Tôi sẽ tự thao tác. Cột Fabric tương ứng là media_id. Task này không sửa file PostgreSQL. | User sửa apps.srv_poi_media_gallery |
| GATE-002 | P1 | fixed | Chỉ tính metric khi DRY_RUN. `countDistinct` nằm trong `if ctx.mode == "DRY_RUN"` của `partner_media`. | |

### Files changed since round 1

- docs/context/mapping_poi_media_info.md | modified
- notebooks/NB_SLV_POI_MEDIA_INFO.ipynb | modified
- tests/test_poi_media_amenity_contract.py | modified
