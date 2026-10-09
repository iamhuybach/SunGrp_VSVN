# Request

## User outcome

Every final Main answer for a task tells the operator what was done, what the operator must run (in order, with parameters, the expected result, and where to paste sanitized output), and what Main is waiting for. When nothing is needed, the answer says the turn is finished in the repository. The operator no longer has to ask how to run a task.

## Scope

### In scope

- `.cursor/rules/00-main-orchestrator.mdc`: add a mandatory turn-closeout contract.
- `.cursor/skills/vsvn-task-workflow/SKILL.md`: add the procedure that builds the closeout from `runtime-runbook.md`, probes, and task state. Extend the description so it also answers "how do I run this task" for an existing `task-id`.
- Cross-check against `AGENTS.md` §6 workflow and the rule's Completion section.

### Out of scope

- A new skill, unless the rule and the workflow skill cannot cover the behavior.
- Moving Fabric DEV execution to the agent.
- Changing `runtime-runbook.md` structure or the `vv.py` validator.
- Rewriting closeouts of past tasks.

## Acceptance criteria

- A task at `waiting_evidence` or `waiting_runtime` cannot end with only a file path. The answer contains ordered run steps and the data to paste back.
- When the operator has nothing to do, the answer states that the turn is finished in the repository.
- No new skill if the rule and the workflow skill cover the behavior.

## Constraints

- Agent-system change explicitly requested by the user on 2026-10-09.
- Main is Grok 4.7 Medium.
- `runtime-runbook.md` stays the full Vietnamese source. The chat answer is the condensed list of steps to run now, including rerun, control-log check, rollback, and forward recovery when the runbook has them.
- Do not commit or push.

## Classification rationale

- Complexity: low. Two instruction files. No stateful logic, data path, or orchestration change.
- Risk: low. Changes only the shape of Main's chat answer. No source code, notebook, pipeline, control table, or validator change. Rollback is a file revert.
- Architecture: not required. No grain, state owner, transaction boundary, orchestration, or multi-service change.
- Evidence: not required. Correctness does not depend on Fabric data.
- Runtime proof: not required. Nothing runs in Fabric.
- Reviewer routing: none. No Spark, SQL, pipeline, or durable-state change. Risk is low, so `risk-gate` is not required. Not fast lane because Main's behavior changes.
