# Architect handoff: 20261019-agent-system-claude-opus-design

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own model design on Claude Code `claude-opus-5-5`, effort `high`. A task's `requirements-analysis.md` (business analysis) and `proposal.md` (problem analysis and solution proposal) are inputs when they exist; they never replace this design.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261019-agent-system-claude-opus-design/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

The first non-blank line is `RESULT: PASS` or `RESULT: EVIDENCE_REQUIRED`. Cover: scope, non-goals, invariants, state ownership, grain and keys, ordering, transaction and commit boundaries, idempotency, concurrency, retry and recovery, partial failure, observability, security, rollout, rollback and forward recovery, implementation plan, and verification. Compare material alternatives and explain the selected trade-off. Write a section that does not apply as one line: `Not applicable: <reason>`.

Size: for `low` or `medium` risk, keep the document under 25 KB, excluding `FILE:` blocks. For `high` or `critical` risk, use the space the failure analysis needs, without repeating the request or the evidence.

Files that Main must save verbatim go in blocks: a line `FILE: <repo-relative path>`, the exact content, then a line `END_FILE`. Every path must be in `scope.files`.

## Main brief contract

Return a separate Main brief, at most 14,000 characters, in English. It is the only part Main reads by default. Use `###` headings only, in this order:

1. `Decision`: at most 5 lines.
2. `Invariants Main must preserve`: at most 10 testable bullets.
3. `Edit list`: table `# | file | anchor (cell id, function, or heading) | change | done-when`, one row per anchor.
4. `Order and stop points`: numbered; mark each stop for evidence or a user decision.
5. `Tests and verification`: exact test names and commands.
6. `Read only if needed`: full-document headings mapped to the edit rows they justify.

Do not restate the request or the evidence in the brief. Code longer than 15 lines goes in the full document under a heading the edit list references.

If evidence is missing, list exact probes and the decisions each one blocks. Do not implement code, update task state, or fill gaps with assumptions.

## Generated context pack

`vv.py` generated this block. Do not re-read the task state, request, decision ledger, or task file list it covers.

# Context 20261019-agent-system-claude-opus-design | phase=triage

## STATE

id: 20261019-agent-system-claude-opus-design
title: Split Claude effort for analysis and model design
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=False
signals: design_tradeoffs, cross_system
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=not_required, risk_gate=not_required, runtime=not_required
rounds: verification=1, review=1, architecture=1, runtime_failure=0
reviewers: none
open findings: none
exceptions: EX-20261019-CLAUDE-DESIGN-HIGH author claude-opus-5-5 high 2026-10-20
scope.files:
- AGENTS.md
- .claude/agents/requirements-analyst.md
- .claude/settings.json
- .cursor/rules/00-main-orchestrator.mdc
- .cursor/skills/vsvn-task-workflow/SKILL.md
- .ai/prompts/architect.md
- .ai/prompts/author-proposal.md
- .ai/prompts/author-runbook.md
- .ai/tasks/_template/task-state.yaml
- docs/agent-system/WORKFLOW.md
- docs/AGENT_PROMPT_SAMPLES.md
- scripts/agent_runner.py
- scripts/vv.py
- tests/test_vv.py
- tests/test_vv_context.py

## VALIDATION

PASS

## RESUME

# Resume

Status: user_decision. Owner: user. Gates: evidence=not_required, architecture=pass, local_verification=pass, specialist_review=not_required, risk_gate=not_required, runtime=not_required. Review round 1 PASS.

Done this session:
- Recorded exception EX-20261019-CLAUDE-DESIGN-HIGH (user approved 2026-10-19).
- Architecture PASS. Proposal lane is models.author_proposal effort high. Runbook lane stays models.author effort medium. Problem analysis is the proposal.md section `## Phân tích bài toán`. requirements-analyst effort is high. Model design stays with the Architect.
- Deviation: materialize now allows only `.ai/tasks/_template/task-state.yaml`, still blocks every other task-state.yaml.
- verify PASS. doctor PASS with no budget WARN. Codex review round 1 PASS, no P0/P1.

Next action: user commits. Do not run another gate.

Read next: `.ai/tasks/20261019-agent-system-claude-opus-design/decision.md` heading `Quyết định hiện hành`; `reviews/round-1.md` heading `Gate verdict`.

Waiting on: commit.

## REQUEST

# Request

## User outcome

On 2026-10-20 the user revised the 2026-10-19 approval. Architecture and solution proposal stay effort `high`. Business analysis, problem analysis, and model design run on Claude Code, model `claude-opus-5-5`, effort `medium`. Main still implements.

## Scope

### In scope

- Record the 2026-10-20 revision in `exceptions` and `decision.md`. The 2026-10-19 all-high approval is history.
- Business analysis stays on `requirements-analyst`, which writes only `requirements-analysis.md`. Set its effort back to `medium`. It does not write `architecture.md` and does not replace the Architect.
- Problem analysis runs on Claude Code `claude-opus-5-5` effort `medium`. It must not share the effort-`high` solution-proposal run. Do not give it to Main. Do not create a role that writes `architecture.md` or replaces the Architect.
- Solution proposal stays effort `high` on the proposal author lane.
- Model design runs on Claude Code `claude-opus-5-5` effort `medium`. It must not be produced by the effort-`high` Architect invocation. The Architect invocation stays effort `high`.
- If runbook author stays `medium`, split proposal effort from runbook effort in the validator, runner, template, and prompts.
- Update `AGENTS.md`, `.ai/tasks/_template/task-state.yaml`, `.ai/prompts/author-proposal.md`, `.ai/prompts/architect.md` where the model-design lane is stated, `docs/AGENT_PROMPT_SAMPLES.md` samples A13–A16, and the validator tests that encode author effort `medium`.
- Keep `docs/agent-system/WORKFLOW.md` author-input and `run-author` rules aligned if they state a single author effort.
- `python scripts/vv.py doctor` must not emit a budget WARN. Current sizes: `AGENTS.md` 7237 bytes (limit 8192), always-apply rules 2570 bytes (limit 4096), `vsvn-task-workflow` skill 4925 bytes (limit 20480), `docs/AGENT_PROMPT_SAMPLES.md` 14604 bytes (limit 25600).

### Out of scope

- Main stays Grok 4.7 Medium and remains the only writer of source, notebooks, pipelines, schemas, and `task-state.yaml`. Main still writes `decision.md` and `resume.md` and runs `verify`.
- Review stays `gpt-5.6-sol` effort `medium`.
- Author kind `runbook` stays `claude-opus-5-5` effort `medium`.
- Evidence, architecture, review, risk-gate, runtime, and round-cap gates stay. The user still commits, accepts risk, and runs Fabric DEV.
- No Fabric runtime change. No data-model or notebook change in this task.
- Do not rewrite `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md`. It is historical context for SOL-10 and D2.

## Revision 2026-10-20

The 2026-10-19 design is already implemented and review round 1 passed. Change it. One Claude invocation has one effort, so two products at different efforts cannot share one run.

Current code:

- Business analysis is `requirements-analyst` at effort `high`.
- Problem analysis is the `## Phân tích bài toán` section of `proposal.md`, written by `run-author --kind proposal` at effort `high`, in the same run as the solution proposal.
- Solution proposal is `models.author_proposal` effort `high`.
- Model design is inside `architecture.md`, written by the Architect at effort `high`.
- Runbook author is `models.author` effort `medium`.
- `.claude/settings.json` `effortLevel` is `high`. `AGENTS.md` is 7909 bytes. The limit is 8192.

Required outcome:

- Architecture (`run-gate` Architect) stays `claude-opus-5-5` effort `high`.
- Solution proposal stays `claude-opus-5-5` effort `high`.
- Business analysis, problem analysis, and model design run on Claude Code `claude-opus-5-5` effort `medium`.
- Do not lower `.claude/settings.json`, because the Architect lane stays `high`.
- `requirements-analyst` still does not write `architecture.md` and does not replace the Architect.
- Runbook author stays effort `medium`.
- D1 stays: `models.author` is the runbook lane. `models.author_proposal` is the solution-proposal lane.

## Acceptance criteria

- The 2026-10-20 decision is the current ledger row and the `exceptions` scope.
- Solution proposal invocations use effort `high`. Runbook invocations use effort `medium`.
- Business analysis, problem analysis, and model design each name an existing Claude Code lane at effort `medium`.
- The Architect invocation stays effort `high` and no longer produces model design inside that same invocation.
- A13–A16 and `AGENTS.md` state this split. `doctor` has no budget WARN.
- `python scripts/vv.py verify <task-id>` passes.
- Stop before commit.

## Constraints

- Agent-system change. Architecture is required. Not a fast lane.
- Implement only after architecture `RESULT: PASS`. Save `FILE:` blocks with `python scripts/vv.py materialize <task-id> --write`.
- `.claude/settings.json` already sets `claude-opus-5-5` `effortLevel` `high` for the Architect. Do not lower it. Change it only if the selected design needs a settings change.
- Read-only context: `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md` SOL-10 and D2; `docs/agent-system/WORKFLOW.md` §5–§7, author-input, and `run-author`.

## Classification rationale

- Complexity: `medium`. The effort split is a design trade-off across the validator, runner, template, prompts, and samples.
- Risk: `medium`. Gate behavior changes, rollback is a revert, and local `verify` plus `doctor` can prove it.
- Architecture: required. The user required it. The change exceeds two files and has more than one viable way to split proposal and runbook effort and to place problem analysis.
- Evidence: not required. Repository inspection and deterministic tests are sufficient.
- Runtime proof: not required. No Fabric object changes.
- Reviewer routing: none of the §7 specialists apply. `required_reviewers` is empty. Codex still runs through `run-gate` at `reviewing`. Risk is not `high` or `critical`, so `risk-gate` is not required.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| EX-20261019-CLAUDE-DESIGN-HIGH | Effort Claude cho phân tích và đề xuất | Trừ architecture và đề xuất giải pháp vẫn là effort high, còn lại Phân tích nghiệp vụ, phân tích bài toán và thiết kế model chạy trên Claude Code claude-opus-5-5 effort medium. | user query | 2026-10-20 |
| D1 | Tách effort author | Giữ `models.author` cho lane runbook (effort `medium`) và thêm `models.author_proposal` tùy chọn (effort `high`). | architecture.md §Decisions and alternatives | 2026-10-19 |
| D2 | Phân tích bài toán | Rút quyết định 2026-10-19. Phân tích bài toán chạy Claude Code `claude-opus-5-5` effort `medium`, không dùng lần chạy effort `high` của đề xuất giải pháp. Lane do Architect chọn. | user query | 2026-10-20 |
| D3 | Effort phân tích nghiệp vụ | `requirements-analyst` dùng `claude-opus-5-5` effort `medium`. Không hạ `.claude/settings.json` vì lane Architect giữ effort `high`. | user query | 2026-10-20 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: PASS
size: 35667 bytes

## FILES

- architecture.md | 35667 bytes | large: use toc/show
- decision.md | 4050 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 11222 bytes
- handoffs/review-round-1.md | 1606 bytes
- request.md | 5882 bytes
- resume.md | 1048 bytes
- reviews/README.md | 157 bytes | placeholder
- reviews/round-1.json | 1302 bytes
- reviews/round-1.md | 239 bytes
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 2217 bytes
- verification/verify.log | 708 bytes

## NEXT

python scripts/vv.py run-gate 20261019-agent-system-claude-opus-design

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### .claude/agents/requirements-analyst.md (26026 bytes)

# requirements-analyst | L9-L353
## Identity | L13-L25
## Role boundary | L26-L34
## Required inputs | L35-L46
## Shared conventions | L47-L117
## Input validation | L118-L136
## Context you read | L137-L148
## Reading rules | L149-L161
## Template exceptions | L162-L168
## Out-of-scope legacy physical facts | L169-L184
## Analysis procedure | L185-L217
## Platform checks | L218-L231
## Status | L232-L242
## Stop rule | L243-L246
## Notebook proposal rule | L247-L255
## Output file | L256-L330
## Write failure | L331-L339
## Reply to the user | L340-L348
## How to run | L349-L353
