# Codex review handoff: 20261119-gsm-as-google-extract, round 2

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

- `STATE-001` — P1 — `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:96`: Khi Google takeover thiếu một child block, parent vẫn có thể đổi sang Google trong khi child SGM cũ tồn tại và các Google event cũ hơn về sau bị guard loại, gây lệch xuyên bảng lâu dài. Fix: chỉ flip parent sau khi mọi child hiện hữu đã được ghi/xóa rõ ràng, hoặc lưu takeover debt theo table/key cho đến khi từng child hoàn tất; thêm test missing-block rồi replay Google cũ hơn.
- `SPARK-001` — P1 — `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:96`: Forced broadcast toàn bộ owner snapshot và Google key set chưa có bằng chứng an toàn trên F16, có thể gây memory pressure hoặc timeout. Fix: giới hạn owner theo POI của batch và bỏ broadcast hint, hoặc cung cấp DEV plan/size/peak-memory/spill/runtime đạt ngưỡng.
- `SQL-001` — P1 — `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:119`: `resolve_latest` không có tie-break ổn định khi các event trùng `source_id`, `crawled_at`, `event_id` nhưng khác payload, nên rerun có thể chọn kết quả khác nhau. Fix: thêm payload tie-break/reject conflict xác định, hoặc chứng minh không có conflict bằng probe DEV.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-001 | P1 | rejected-false-positive | `architecture.md` mục Partial failure: document `google` thiếu khối thì không sinh dòng, dòng `sgm` cũ ở bảng con giữ nguyên vì không có nhánh xoá. Gate chỉ chặn khi bảng khác FAILED. | |
| SPARK-001 | P1 | fixed | Bỏ `F.broadcast` trên owner snapshot, tập google trong lần chạy, và bảng đích. Join giữ nguyên. | |
| SQL-001 | P1 | rejected-false-positive | `resolve_latest` giữ thứ tự `(crawled_at, event_id, dedup_order, _pos)` như trước task. Architecture yêu cầu thứ tự này không đổi ngoài takeover. | |

### Files changed since round 1

- notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb | modified
