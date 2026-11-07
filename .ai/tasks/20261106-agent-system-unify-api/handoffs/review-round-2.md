# Codex review handoff: 20261106-agent-system-unify-api, round 2

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

- **GATE-001 — P1 — `docs/poi-serving-api/API-GAPS.md:39`**: The documented S2S Bearer-authentication contract is not enforced by the service, allowing unauthenticated access to PostgreSQL-backed POI data. **Fix:** Decide whether authentication belongs in the service or upstream gateway, record that boundary in architecture, and add a negative unauthenticated-request test.
- **GATE-002 — P1 — `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/config/OpenApiConfig.java:46`**: OpenAPI embeds an internal DEV hostname, violating the architecture invariant prohibiting DEV hostnames in the repository. **Fix:** Remove or environment-parameterize the server URL and scan the implementation paths for remaining DEV hostnames.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | accepted-risk | User chốt 2026-11-06: xác thực Bearer S2S do API Management (gateway) đảm nhận; service không kiểm tra token. Rủi ro còn lại: gọi thẳng cổng 8080 sẽ bỏ qua xác thực, nên khi deploy phải để service chỉ nhận traffic qua gateway (mạng nội bộ). Không sửa code; thêm ghi chú ranh giới ở `docs/poi-serving-api/API-GAPS.md:39`. | Nếu có task deploy: kiểm tra network isolation |
| GATE-002 | P1 | fixed | User chọn lấy URL từ biến môi trường. `OpenApiConfig` đọc `OPENAPI_GATEWAY_URL` (mặc định rỗng) và chỉ thêm server "Gateway" khi biến có giá trị. Host DEV bị xoá khỏi code. Tên biến được thêm vào `services/data-serving-service/AGENTS.md` §Environment variables. Sau đó chạy review round 2. | — |

### Files changed since round 1

- docs/poi-serving-api/API-GAPS.md | modified
- services/data-serving-service/AGENTS.md | modified
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/config/OpenApiConfig.java | modified
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/config/OpenApiConfigTest.java | entered the diff after round 1
