# VSVN agent-system setup

The repository uses three deliberately separate model lanes:

| Lane | Model | Purpose | Write authority |
|---|---|---|---|
| Cursor Main | Grok 4.7 High | Triage, implementation, remediation, and task state | Source code and Main-owned task artifacts |
| Claude Code Architect | Claude Opus 5.5 High | Architecture for complex changes | Current task `architecture.md` only |
| Codex review | GPT-5.6 Sol High | Independent specialist review and risk gate | Read-only |

Cursor-native subagents are not used for review. This avoids conflicting reviewer definitions and keeps review usage in Codex authenticated with ChatGPT rather than Cursor's Other Models pool.

## Prerequisites

- Python 3.11 or later and Git for Windows.
- Cursor with access to Grok 4.7 High.
- Claude Code authenticated with an account that exposes Claude Opus 5.5.
- Codex extension or CLI authenticated with ChatGPT and access to `gpt-5.6-sol`.
- A trusted checkout of this repository.

Install deterministic verification tools:

```powershell
python -m pip install -r requirements-dev.txt
python scripts/vv.py doctor
python scripts/vv.py external-doctor
python scripts/vv.py verify --all
```

`doctor` warns if `docs/context/CTRL_TABLES_CONTEXT.md` is absent. That warning does not block unrelated work, but any `ctrl_*` change then requires evidence and user action.

## Cursor Main

1. Open the repository root in Cursor.
2. Select Grok 4.7 and High reasoning in the model picker. Repository files cannot force Cursor's active model.
3. Confirm that `.cursor/rules/00-main-orchestrator.mdc` is Always Apply.
4. Confirm that the notebook, pipeline, and SQL rules attach to their declared globs.
5. Confirm that `vsvn-task-workflow` and `fabric-runtime-evidence` appear as project skills.
6. Record the actual model in each task's `task-state.yaml`. A fallback is a stopped gate, not an implicit substitution.

The `.cursor/agents/` directory intentionally contains no reviewer definitions.

## Claude Code Architect

Project settings select `claude-opus-5-5`, High effort, and `dontAsk` permission mode. Automated runs pass the model, effort, and read-only tools explicitly, use Claude safe mode, and load only user settings, so they do not depend on an interactive workspace-trust dialog or load project customizations. Claude returns structured architecture content and the deterministic runner persists `architecture.md`.

The runner discovers Claude in this order: `VSVN_CLAUDE_EXE`, `claude` on `PATH`, then the newest Claude Code binary bundled with Cursor or VS Code. Run `python scripts/vv.py external-doctor` to verify discovery and authentication without spending a model turn.

If the installed client does not recognize the configured model ID, do not silently select another model. Report the mismatch and update configuration only with user approval.

## Codex review lane

Project configuration fixes the coordinator and specialists to `gpt-5.6-sol`, medium reasoning, read-only sandbox, and no approval prompts. Custom agents are defined under `.codex/agents/`:

- `state-correctness-reviewer`
- `spark-runtime-reviewer`
- `sql-data-reviewer`
- `fabric-pipeline-reviewer`
- `risk-gate`

1. Sign in to the Codex extension or CLI with ChatGPT.
2. Trust the repository so project configuration is loaded.
3. Run `python scripts/vv.py external-doctor` and confirm Codex authentication.
4. At `reviewing`, Main runs `python scripts/vv.py run-gate <task-id>`. The runner uses `codex exec` with structured output, the read-only sandbox, the exact configured model and reasoning effort, and an enforced reviewer manifest.

Review agents never edit files. Main stores the returned consolidated report as `reviews/round-<N>.md` and records every disposition in `decision.md`.

## Task workflow

Copyable Cursor Agent entry prompts for common task types are available in [`docs/AGENT_PROMPT_SAMPLES.md`](docs/AGENT_PROMPT_SAMPLES.md). Choose the closest case, replace its placeholders, and submit it from the repository root with Grok 4.7 High selected.

```powershell
python scripts/vv.py new <slug>
python scripts/vv.py validate <task-id>
python scripts/vv.py transition <task-id> <status>
python scripts/vv.py prompt <task-id> architect
python scripts/vv.py prompt <task-id> review --round 1
python scripts/vv.py external-doctor
python scripts/vv.py external-smoke
python scripts/vv.py run-gate <task-id>
python scripts/vv.py verify <task-id>
```

There is no Git-index snapshot, `handoff`, or `guard --restore` mechanism. Role permissions, read-only review sandboxes, task-state validation, and normal Git diff review replace that fragile workflow.

## Model-change evaluation

Before changing a model family or effort level:

1. Run the routing cases in `.ai/evals/cases.yaml` against the proposed configuration.
2. Score outputs with `.ai/evals/rubric.md`.
3. Compare missed P0/P1 findings, false P0/P1 findings, evidence discipline, routing, and latency/cost with the current baseline.
4. Record the evaluation result or explicit user exception in `decision.md`.

## Troubleshooting

| Symptom | Action |
|---|---|
| Cursor runs a different Main model | Re-select Grok 4.7 High and record the mismatch; repository config cannot control the picker. |
| External CLI is not found | Set `VSVN_CLAUDE_EXE` or `VSVN_CODEX_EXE`; otherwise install the CLI on `PATH` or update the corresponding IDE extension. |
| Automated gate changes an unexpected file | Stop. Inspect the Git diff; the runner will not update task state or overwrite the unexpected change. |
| Codex ignores project agents | Trust the repository, restart the session, and run `python scripts/vv.py doctor`. |
| Codex uses a fallback model | Stop the review gate; verify account availability and project config. |
| Claude automation cannot read required context | Verify the file is inside the repository and rerun; automated Architect receives only `Read`, `Glob`, and `Grep`. |
| A control-table change lacks context | Restore `CTRL_TABLES_CONTEXT.md` or create a task evidence plan and wait for Fabric DEV results. |
| Verification reports a missing module | Install `requirements-dev.txt`; use `--allow-missing` only for diagnosis, never as a passing gate. |
