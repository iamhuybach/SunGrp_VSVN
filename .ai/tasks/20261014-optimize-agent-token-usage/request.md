# Request

## User outcome

Reduce Cursor Grok 4.7 Medium token use without reducing agent capability, gate discipline, or review quality. Rewrite `docs/AGENT_PROMPT_SAMPLES.md` with explicit context scopes.

## Scope

### In scope

- `scripts/vv.py`
- `scripts/agent_runner.py`
- `tests/test_vv.py`
- `tests/test_vv_context.py`
- `tests/fixtures/sample_notebook.ipynb`
- `.ai/tasks/_template/decision.md`
- `.ai/tasks/_template/resume.md`
- `.ai/tasks/_template/task-state.yaml`
- `.ai/prompts/architect.md`
- `.ai/prompts/author-proposal.md`
- `.ai/prompts/author-runbook.md`
- `AGENTS.md`
- `docs/agent-system/WORKFLOW.md`
- `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md`
- `.cursor/rules/00-main-orchestrator.mdc`
- `.cursor/skills/vsvn-task-workflow/SKILL.md`
- `.cursor/skills/vsvn-extract-notebook/SKILL.md`
- `.cursor/skills/vsvn-notebook-library/SKILL.md`
- `.cursorindexingignore`
- `.cursorignore`
- `SETUP.md`
- `docs/AGENT_PROMPT_SAMPLES.md`
- `docs/context/00_README.md`

### Out of scope

- Fabric notebooks, pipelines, and schemas
- `.codex/` and `.claude/`
- Model IDs and reasoning efforts
- Fabric data or runtime state

## Acceptance criteria

- Every implementation phase in `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md` §6 passes its phase acceptance checks.
- Gates and authority remain unchanged: the same statuses, gate results, round caps, reviewer routing, and user-only commit and risk acceptance.
- The fixed instruction preamble is at most 12 KB.
- `python scripts/vv.py context` produces at most 400 lines for every existing task.
- After measurement, Cursor tokens per completed phase target a reduction of at least 40%, without more review rounds or missed P0/P1 findings.

## Constraints

- Follow `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md` §0 and implement §6 phase by phase, in order.
- Stop at every phase stop point and report its acceptance result.
- Ask the user D1–D3 once before Phase 1 and record the answers in `decision.md`.
- Do not improvise if repository structure or behavior differs from the plan; record a deviation in `decision.md` before continuing.
- Read only the plan, files named by the current step, and tests. Do not read `notebooks_lgc/`, `docs/context/3p-google/*.txt`, or `.ai/tasks/*/evidence/context/`.
- Do not commit, push, merge, or rewrite Git history.
- Do not change model IDs or efforts in `.codex/config.toml`, `.codex/agents/*.toml`, or `.claude/settings.json`.

## Classification rationale

- Complexity: `high`; this is a multi-phase change across the runner, validator, task artifacts, instructions, skills, prompts, and operator workflow.
- Risk: `medium`; behavior is bounded to the agent system and has deterministic rollback, but validator and state transitions change.
- Architecture: required and supplied by `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md`.
- Evidence: repository inspection is sufficient; Cursor usage aggregates are a measurement baseline, not implementation correctness evidence.
- Runtime proof: not required because no Fabric runtime behavior changes.
- Reviewer routing: `state-correctness-reviewer` reviews validator, gate, runner, and state-transition correctness.
