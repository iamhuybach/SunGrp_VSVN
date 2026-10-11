# Request

## User outcome

The repository contains agent-readable sample documents and one new analysis agent. Claude Code authors the sample Mapping, the sample Business Requirements Document, the analysis-agent definition, and the Codex reviewer definition. Main stores each file as the exact text Claude returned. The analysis agent reads a Mapping and a Business Requirements Document and writes an analysis for the open task. It does not replace the Architect.

## Scope

### In scope

- One Mapping template and one Business Requirements Document template. Sample prose is Vietnamese. Field names, table names, column names, status values, and identifiers stay English. Every example is labeled as an example and is not written as production data.
- The templates must be readable by an agent and stay on the VSVN platform already described in `docs/context/`: bronze, silver, gold, `poi_id`, extract, and control tables. Each template has places to fill source, target, grain, key, business rules, and items that still lack evidence. Do not invent a schema or a business rule when `docs/context/` does not state it.
- One new agent. Runtime is Claude Code. Model is `claude-opus-5-5`. Effort is `medium`. The agent reads one Mapping and one Business Requirements Document that follow the new templates, then writes an analysis for the open task. The analysis states which requirements are mapped, which requirements lack a source or a grain, and which questions the user must answer. The agent stops when evidence is missing. It does not propose a new notebook while a key or a grain is still missing. It does not write a notebook, a pipeline, a schema, or source code.
- The Architect remains Claude Code on `claude-opus-5-5` with effort `high` and still writes only `architecture.md` through `python scripts/vv.py run-gate`.
- A separate Codex reviewer definition at `.codex/agents/requirements-reviewer.toml`. That reviewer reads only the Mapping template, the Business Requirements Document template, and the analysis-agent definition.

Read these context files before choosing template fields:

- `docs/context/00_README.md`
- `docs/context/01_DATA_MODEL.md`
- `docs/context/02_NAMING_CONVENTION.md`
- `docs/context/CTRL_TABLES_CONTEXT.md`
- `AGENTS.md` sections 2, 3, and 9

An example may cite a name that already appears in those files. Label it as an example. Do not add a column, key, or rule that the cited context does not state. Leave the field blank, or mark it as missing evidence, when context does not state the value.

### Out of scope

- Notebooks, pipelines, schemas, and source code.
- Changes to `scripts/vv.py`, including the `REVIEWERS` set.
- Changes to `scripts/agent_runner.py`.
- Changes to model or effort in `.claude/settings.json` and `.codex/config.toml`.
- Changes to `AGENTS.md`.
- The existing Codex review cycle: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`, `fabric-pipeline-reviewer`, and `risk-gate`.
- Fabric DEV probes and runtime proof.
- Commit, push, or merge.

## Acceptance criteria

- `architecture.md` contains every new file in a `FILE:` block.
- `git diff` of those files matches the blocks character for character.
- The repository contains the Mapping template, the Business Requirements Document template, the Claude Code analysis-agent definition, and `.codex/agents/requirements-reviewer.toml`.
- A path that is not in `architecture.md` is not created.
- `python scripts/vv.py verify <task-id>` passes.
- `.ai/tasks/<task-id>/reviews/requirements-review.md` exists and no P0 or P1 about the document content remains open.
- `review_plan.required_reviewers` stays empty. `gates.specialist_review` and `gates.risk_gate` stay `not_required`.

## Constraints

- This is a user-requested agent-system change. Fast lane does not apply.
- Risk is `medium`.
- The user-approved exception dated 2026-10-11 is recorded in `task-state.yaml` and `decision.md` before the architecture gate. Claude Code authors the Mapping template, the Business Requirements Document template, the analysis-agent definition, and `.codex/agents/requirements-reviewer.toml`. Main does not draft or edit the wording of those documents. Main copies each `FILE:` block verbatim after architecture verdict `PASS`.
- `python scripts/vv.py run-gate` at `waiting_architecture` stays a read-only Claude turn. The runner persists only `architecture.md`. Do not change `scripts/agent_runner.py` so Claude can write freely into the repository.
- Do not call `python scripts/vv.py run-gate` when status is `reviewing`.
- After the files are stored, Main runs one read-only Codex turn with model `gpt-5.6-sol` and effort `medium`, using `.codex/agents/requirements-reviewer.toml` only. Main stores that report at `.ai/tasks/<task-id>/reviews/requirements-review.md`.
- A P0 or P1 about document content goes back to Claude through a new architecture round. Main copies the new document verbatim and does not edit the documents to satisfy the finding.
- Move to `ready_to_merge` only when the separate review file exists and no P0 or P1 remains open.
- If Claude or Codex falls back to another model, stop and report it. Do not substitute a model.
- There is no existing Claude Code agent file in this repository. Put model `claude-opus-5-5` and effort `medium` on the analysis agent itself. Do not change `.claude/settings.json`, which stays `claude-opus-5-5` at effort `high` for the Architect.
- The reviewer file must be valid TOML. Set `name` to `requirements-reviewer`, `model` to `gpt-5.6-sol`, `model_reasoning_effort` to `medium`, and `sandbox_mode` to `read-only`. Follow the field shape of the existing files in `.codex/agents/` so the file loads. Do not add this reviewer to `REVIEWERS` in `scripts/vv.py`.

## Architecture delivery contract

Architecture prose outside the file blocks is English. The Mapping body and the Business Requirements Document body are Vietnamese, as required above. That Vietnamese is the file payload. The analysis-agent definition and the reviewer TOML are English, because they are agent definitions.

Return verdict `PASS` only when every required file is present in the document. Use `EVIDENCE_REQUIRED` only when a template decision is blocked by a fact that is not in the repository. Do not invent that fact.

Each new file is one block. A block starts with a line that is exactly:

```text
FILE: <relative-posix-path>
```

The body is every following line until, but not including, a line that is exactly `END_FILE`. `END_FILE` is a delimiter and is not part of the file. Do not wrap a block in Markdown fences. Do not indent the `FILE:` line or the `END_FILE` line. Do not emit either exact line except as a real delimiter.

Main copies the body character for character, including blank lines and trailing spaces, and does not add or remove a final newline beyond the characters inside the block.

Required blocks:

1. The Mapping template, at the path you select. The path must sit in the repository outside `.ai/tasks/`.
2. The Business Requirements Document template, at the path you select. The path must sit in the repository outside `.ai/tasks/`.
3. The Claude Code analysis-agent definition, at the path you select. The path must sit in the repository outside `.ai/tasks/`. The definition states the agent name, runtime Claude Code, model `claude-opus-5-5`, effort `medium`, the required Mapping and Business Requirements Document inputs, the analysis output inside the open task, the stop rule when evidence is missing, and the prohibition on proposing a new notebook while a key or a grain is missing.
4. `.codex/agents/requirements-reviewer.toml`.

The reviewer reads only those three artifacts. It does not review notebooks, pipelines, schemas, or source code.

After verdict `PASS`, Main creates only those paths and writes only those bodies. On a later architecture round caused by a P0 or P1 document-content finding, Main replaces those files with the new verbatim bodies and does not edit them itself.

## Classification rationale

- Complexity: `high`. The template contract, the boundary between the analysis agent and the Architect, and the rule against inventing schema are design trade-offs that need deep reasoning over `docs/context/`. This is a user-requested agent-system change, so fast lane does not apply.
- Risk: `medium`. The change is bounded to templates and agent definitions. Rollback is deleting those files. It does not write Lakehouse data. `risk-gate` is not required.
- Architecture: required. Claude Code owns the document content, the agent definition, and the reviewer definition through the architecture gate.
- Evidence: not required. The templates point at context already in the repository and leave unknown facts blank. No Fabric DEV probe is required to author the templates.
- Runtime proof: not required. No pipeline, notebook, or table behavior changes.
- Reviewer routing: `required_reviewers` is empty. The separate review uses `requirements-reviewer` only and is not a `run-gate` review.
