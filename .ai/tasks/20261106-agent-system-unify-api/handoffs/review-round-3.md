# Codex review handoff: 20261106-agent-system-unify-api, round 3

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

- **GATE-001 — P1 — `docs/poi-serving-api/API-GAPS.md:177`**: Lines 177 and 188 still assign S2S authentication to the service, contradicting the accepted gateway-auth boundary at line 39 and leaving deployment behavior ambiguous. **Fix:** State consistently that authentication and allowlisting belong to API Management, remove service-auth from Wave 0, and make network-isolation verification a mandatory deployment condition.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | accepted-risk | User chốt 2026-11-06: xác thực Bearer S2S do API Management (gateway) đảm nhận; service không kiểm tra token. Rủi ro còn lại: gọi thẳng cổng 8080 sẽ bỏ qua xác thực, nên khi deploy phải để service chỉ nhận traffic qua gateway (mạng nội bộ). Không sửa code; thêm ghi chú ranh giới ở `docs/poi-serving-api/API-GAPS.md:39`. Sau round 2, sửa cho thống nhất: `API-GAPS.md:177` (auth và allowlist ở API Management; network isolation là điều kiện bắt buộc khi deploy), `:188` (bỏ "S2S auth" khỏi Wave 0), `:58,61` (401/403 do API Management trả), `DESIGN-AND-PLAN.md:159` (sơ đồ ghi "sau APIM" thay cho "S2S auth"). | Nếu có task deploy: kiểm tra network isolation |

### Files changed since round 2

- docs/poi-serving-api/API-GAPS.md | modified
- docs/poi-serving-api/DESIGN-AND-PLAN.md | modified
