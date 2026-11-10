# Codex review handoff: 20261109-srv-poi-amenity-en, round 2

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

- `SPARK-SQL-001` — P1 — `notebooks/NB_SLV_POI_AMENITY.ipynb:235`: `COND_SCHEMA` có 9 cột nhưng tuple điều kiện có 10 giá trị sau khi thêm `amenity_en`, khiến `createDataFrame` lỗi trước Delta write. Thêm `amenity_en string` ngay sau `amenity string` và kiểm thử thứ tự/arity của schema.
- `API-002` — P1 — `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java:125`: endpoint danh sách amenities vẫn không phân trang, vi phạm quy tắc bắt buộc `size <= 100` trong service `AGENTS.md`. Dùng `Pageable`/`PageResponse` với giới hạn 100, hoặc xin ngoại lệ được người dùng phê duyệt và ghi nhận theo quy trình.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SPARK-SQL-001 | P1 | fixed | `COND_SCHEMA` thêm `amenity_en string` ngay sau `amenity string`, đủ 10 trường với tuple điều kiện. | |
| API-002 | P1 | rejected-false-positive | D-01 chốt `data` là mảng không phân trang. Architecture vòng 2 giữ `List` và nói một POI dưới 100 dòng. Endpoint amenities đã là list trước task này. Thêm `PageResponse` đổi cây JSON đã chốt. | |

### Files changed since round 1

- notebooks/NB_SLV_POI_AMENITY.ipynb | modified
