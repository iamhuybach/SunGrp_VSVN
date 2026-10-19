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
