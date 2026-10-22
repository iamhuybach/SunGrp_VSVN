# Codex review handoff: 20261021-move-poi-nodes-enr-15p-cleanup, round 2

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

- `GATE-001` — P1 — `notebooks/NB_SETUP_POI_ENTITY.ipynb:942`, `notebooks/NB_SETUP_POI_AMENITY.ipynb:730`, `notebooks/NB_CREATE_DDL.ipynb:2433`: lease setup 90 phút có thể bị contender dùng ngưỡng 35 phút chiếm khi setup vẫn chạy, phá vỡ mutual exclusion. Fix: dùng một lease tương thích hoặc heartbeat/explicit expiry cho mọi lock owner và thêm concurrency test.
- `GATE-002` — P1 — `notebooks/NB_CREATE_DDL.ipynb:2593`: retained info-edge set chỉ được kiểm tra sau hai `DELETE`, nên patch có thể ghi rồi mới phát hiện trạng thái sai. Fix: kiểm tra đầy đủ retained info edges trước `DELETE` đầu tiên và giữ post-check.
- `GATE-003` — P1 — `notebooks/NB_CREATE_DDL.ipynb:2496`: `_info_edges()` bỏ qua `src_schema` và full logical key, nên cạnh đúng tên bảng nhưng sai schema vẫn có thể vượt kiểm tra. Fix: so sánh đủ khóa `(pl_name, src_schema, src_tbl, trg_schema, trg_tbl)`.
- `GATE-004` — P1 — `notebooks/NB_CREATE_DDL.ipynb:2566`, `notebooks/NB_SETUP_POI_ENTITY.ipynb:845`, `notebooks/NB_SETUP_POI_AMENITY.ipynb:646`: SQL three-valued logic cho phép owner hoặc key chứa `NULL` thoát khỏi các predicate `=`/`<>` trước ghi. Fix: từ chối `NULL` trong toàn bộ owner/logical-key columns hoặc dùng predicate null-safe và thêm test tương ứng.
- `GATE-005` — P1 — `notebooks/NB_CREATE_DDL.ipynb:2621`: một optimistic-concurrency conflict ở lệnh release lock duy nhất có thể để lock ở trạng thái `RUNNING` và chặn R4 tới khi lease hết hạn. Fix: release bằng bounded Delta retry và cung cấp recovery rõ ràng khi retry cạn.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | rejected-false-positive | §9 giữ lease setup 90 phút để setup không chiếm khóa NB_00. §10 thu hồi khóa cell sau tối đa 35 phút. Chiều ngược lại không xảy ra trong rollout: trigger ENR_15P được tạm dừng và setup không chạy trong `mvpoipy`. | |
| GATE-002 | P1 | fixed | So `_info_edges()` với `WANT_INFO` được đưa vào `issues` trước `Dừng trước khi ghi`. Post-check sau DELETE giữ nguyên. | |
| GATE-003 | P1 | fixed | `_info_edges()` nhóm theo `(src_schema, src_tbl)`. `WANT_INFO` là `(lh_vv_silver.dbo, src)`. | |
| GATE-004 | P1 | fixed | Cell đếm dòng khóa NULL trước khi ghi. Hai notebook setup đổi predicate owner thành `pl_name <> ENR OR pl_name IS NULL`. | |
| GATE-005 | P1 | rejected-false-positive | §10: C4 không nhả khóa thì chờ lease hết hạn, tối đa 35 phút. §9 không thêm vòng retry, theo tiền lệ `enrinfopy`. | |

### Files changed since round 1

- notebooks/NB_CREATE_DDL.ipynb | modified
- notebooks/NB_SETUP_POI_AMENITY.ipynb | modified
- notebooks/NB_SETUP_POI_ENTITY.ipynb | modified
- tests/test_enr_poi_contract.py | modified
- tests/test_poi_amenity_contract.py | modified
- tests/test_poi_entity_contract.py | modified
