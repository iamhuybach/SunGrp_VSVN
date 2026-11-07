# User-action inventory (facts and counts, 2026-11-06)

## Method

- Script: `evidence/probes/user_actions_scan.py`, run locally: `python .ai/tasks/20261106-agent-system-unify-api/evidence/probes/user_actions_scan.py`. Exit 0.
- Sources: `.ai/tasks/*/task-state.yaml` (50 tasks, this task excluded), `.ai/tasks/*/resume.md`, `## Quyết định hiện hành` of `.ai/tasks/*/decision.md`, `git log --stat -n 200` (79 commits returned), and this project's agent transcripts (69 parent chats, 17 subagent files, 708 user turns).
- Transcripts store tool calls but not tool results, so CLI errors are counted only where the assistant quoted them.
- Template matching is by each template's fixed phrase; the first match wins. Mention counts are substring matches and include prompt text, so they are upper bounds.
- No names, emails, tokens, or payload values are recorded. Errors are sanitized and cut to 160 characters.

## 1. Prompt templates A1–A19 (user turns)

| Template | Turns | Template | Turns |
|---|---:|---|---:|
| A1 new task triage | 28 | A11 explain | 4 |
| A2 fast lane | 1 | A12 review diff | 0 |
| A3 load evidence | 0 | A13 Mapping + BRD | 5 |
| A4 implement | 2 | A14 analyse Mapping + BRD | 1 |
| A5 remediate | 0 | A15 proposal | 1 |
| A6 run pending gate | 0 | A16 comment on proposal | 1 |
| A7 Fabric DEV guide | 0 | A17 Codex performance | 1 |
| A8 record runtime result | 0 | A18 agent-system change | 1 |
| A9 runtime failure | 2 | A19 smoke test | 3 |
| A10 resume task | 4 | No template | 654 |

Templates matched 54 of 708 turns (7.6%). Most frequent first two words of the 654 unmatched turns:

| Opener | Turns | Opener | Turns |
|---|---:|---|---:|
| "dựa vào" | 48 | "chấp nhận" | 9 |
| "commit và" | 28 | "tại sao" | 8 |
| "briefly inform" | 22 | "kết quả" | 8 |
| "đã chạy" | 16 | "tôi cần" | 7 |
| "tôi đã" | 13 | "đồng ý" | 7 |
| "đây là" | 11 | "result sau" | 6 |
| "cho tôi" | 10 | "accept risk" / "1 result" | 6 / 6 |

## 2. Repeated commands (assistant tool calls in parent chats)

Tool calls: Shell 3,973; Read 3,604; StrReplace 3,033; Grep 2,583; Write 851; Glob 279; CallDynamicTool 144.

| Command (in Shell calls) | Count | Command | Count |
|---|---:|---|---:|
| `vv.py show` | 975 | `git status` | 322 |
| `vv.py transition` | 438 | `git diff` | 169 |
| `vv.py validate` | 409 | `git push` | 122 |
| `vv.py context` | 382 | `git add` | 114 |
| `vv.py toc` | 315 | `git log` | 110 |
| `vv.py closeout` | 208 | `git commit` | 102 |
| `vv.py run-gate` | 128 | `git branch` | 64 |
| `vv.py verify` | 92 | `claude` (CLI mention) | 197 |
| `vv.py new` | 46 | `codex` (CLI mention) | 48 |
| `vv.py run-author` | 46 | `pytest` | 123 |
| `vv.py materialize` | 12 | `docker` | 25 |
| `vv.py doctor` | 12 | `ruff` | 7 |

`git` counts include only `git` at the start of a command segment. `git commit` 102 and `git push` 122 ran from agent Shell calls, while `AGENTS.md` §8 says agents do not commit or push. The 28 user turns opening with "commit và" are the matching requests.

## 3. Stop points

| Final `task.status` | Tasks |
|---|---:|
| `ready_to_merge` | 31 |
| `user_decision` | 10 |
| `waiting_runtime` | 3 |
| `blocked` | 2 |
| `reviewing`, `implementing`, `verifying`, `waiting_architecture` | 1 each |

| Gate | pass | not_required | pending | user_decision | fix_required | evidence_required |
|---|---:|---:|---:|---:|---:|---:|
| architecture | 35 | 14 | 1 | 0 | 0 | 0 |
| evidence | 15 | 32 | 0 | 1 | 0 | 2 |
| local_verification | 46 | 1 | 2 | 1 | 0 | 0 |
| specialist_review | 27 | 12 | 3 | 5 | 2 | 1 |
| risk_gate | 13 | 30 | 1 | 4 | 1 | 1 |
| runtime | 17 | 25 | 7 | 1 | 0 | 0 |

Classification signals (tasks): `design_tradeoffs` 25, `idempotency` 24, `runtime_proof_required` 22, `data_model_change` 17, `stateful_logic` 14, `cross_state_impact` 14, `cross_system` 12, `deep_reasoning_required` 11, `data_evidence_required` 11.

Chats mentioning a stop keyword: `waiting_runtime` 27 (316 messages); "round cap" 24 (45); `materialize` 26 (78).

## 4. Gate and CLI failures (sanitized, verbatim where quoted)

| Failure | Chats | Messages | Sanitized text |
|---|---:|---:|---|
| Runner banner | 7 | 20 | `AUTOMATED GATE FAIL: …` |
| Repository changed during a read-only run | 5 | 8 | `AUTOMATED GATE FAIL: Codex review changed the repository unexpectedly.`; also "working tree changed while the Architect ran read-only" (2 consecutive `run-gate` attempts) |
| Codex structured-output schema rejected | 1 | 1 | `{"type":"turn.failed","error":{"message":"{ "type": "error", "error": { "type": "invalid_request_error", "code": "invalid_json_schema", …` — cause quoted: `uniqueItems` on `reviewers_run` in `_review_schema()` (during `external-smoke`) |
| Claude Architect non-zero exit | 1 | 1 | `AUTOMATED GATE FAIL: Claude Architect failed with exit code 1:` … `is_error: true`, `terminal_reason: api_…` |
| Claude Code OAuth expired | 1 | 5 | "Gate architecture fail vì OAuth Claude Code hết hạn"; status stayed `waiting_architecture`, no artifact written |
| Token/usage exhaustion | 6 | 14 | Led to a temporary Cursor Opus medium fallback (1 chat), later removed |
| Long gate runtime | 8 | 29 | `run-gate … --timeout 2700` used; one attempt failed "before the runner accepted the result" |

## 5. Review rounds and model exceptions

| Value | `rounds.review` | `rounds.architecture` | `rounds.verification` |
|---:|---:|---:|---:|
| 0 | 15 | 15 | 26 |
| 1 | 8 | 25 | 14 |
| 2 | 19 | 10 | 10 |
| 3 | 8 | 0 | 0 |

Eight tasks reached review round 3 (an approved extra round). 5 tasks have `runtime_failure > 0`. 10 open findings remain across tasks.

Model exceptions in `task-state.yaml`: legacy `model_policy_exception` 4; `main → gpt-5.6-sol` 2; `author → claude-opus-5-5` 1; `architect → claude-fable-5-1` 1; `review → claude-opus-5-5` 1. Ledger rows: `EXC` 2, `EX` 1, `MODEL` 1.

## 6. Repeated manual steps

| Step | Evidence | Count |
|---|---|---:|
| User asks for commit/push | user turns containing "commit" | 105 |
| User ran a runbook or Fabric DEV step | user turns containing runbook / Fabric DEV / "đã chạy" | 59 |
| User sets or changes a model or exception | user turns containing exception / EX-n / model_override | 50 |
| User copies or pastes content | user turns containing "chép", "copy", "dán" | 23 |
| User pastes probe results | user turns containing `evidence/results/` / "đã dán" | 5 |
| Review artifacts committed | `git log --stat` file changes under `reviews/` | 181 |
| Probes committed | file changes under `evidence/probes/` | 89 |
| Runbooks committed | `runtime-runbook.md` file changes | 52 |
| `decision.md` / `architecture.md` / `resume.md` | file changes | 64 / 50 / 45 |
| Agent config (`.cursor`, `.claude`, `.codex`, `AGENTS.md`, `CLAUDE.md`) | file changes | 75 |
| `notebooks/` / `tests/` / `docs/context/` | file changes | 114 / 84 / 131 |
| `pipelines/` / `sql/` | file changes | 1 / 2 |
