# Request

## User outcome

One task shared by three sessions. Fable 5.1 medium surveys the Agent setup, models, workflow, and how `docs/context` drifts from the notebooks that are running. The user locks item 8 of that report. Grok 4.7 Medium then changes only the locked items. Claude Code Opus 5.5 high reviews that diff.

## Scope

### In scope

- Survey criteria: performance, cost, daily work, and each agent's run speed.
- Survey output: `.ai/tasks/20261022-agent-speed-and-context-review/reviews/agent-speed-review.md`, written by Fable 5.1, effort medium.
- After the user locks item 8, that report is this task's architecture.
- Implementation is limited to the items the user locked, done by Grok 4.7 Medium.
- Diff review is Claude Code Opus 5.5, effort high, diff only.
- Classification: agent-system. No `data_model_change`, no evidence, no runtime proof.

### Out of scope

- `python scripts/vv.py run-author` for the Fable survey.
- `python scripts/vv.py run-gate` for the Opus diff review.
- Any change to the model id or effort in `.claude/settings.json` and `.codex/config.toml`.
- Data-model changes, Fabric evidence, and runtime proof.
- Repository survey or source edits before the user locks item 8.

## Acceptance criteria

- `request.md`, `task-state.yaml` `exceptions`, and `decision.md` record this request and the 2026-10-22 approval.
- `python scripts/vv.py validate 20261022-agent-speed-and-context-review` passes.
- Status stays `triage` until the user locks item 8.
- Later implementation matches only the locked items, and the Opus session reviews only the resulting diff.

## Constraints

- Approved 2026-10-22. Fable 5.1, effort medium, writes `.ai/tasks/20261022-agent-speed-and-context-review/reviews/agent-speed-review.md`. Do not call `run-author`.
- The change review is Claude Code Opus 5.5, effort high, diff only. Do not call `run-gate`.
- Do not change the model id or effort in `.claude/settings.json` and `.codex/config.toml`.
- `models.*.expected` and `models.*.effort` stay on the repository defaults. The overrides live only in `exceptions`.

## Classification rationale

- Complexity: medium. The survey compares performance, cost, daily work, and agent speed, and the locked items can change agent-system behavior across more than a fast-lane edit.
- Risk: medium. Rollback is Git and local checks can prove the agent-system edit. No data-loss or runtime-only path.
- Architecture: required. The user defined the Fable report, after item 8 is locked, as this task's architecture. Signal: `design_tradeoffs`. The Architect runner is not used.
- Evidence: not required. No `data_model_change`. Correctness of the later edit does not depend on Fabric data.
- Runtime proof: not required.
- Reviewer routing: no specialist reviewer. `gates.specialist_review` stays `pending` until the Opus diff review is recorded. Do not call `run-gate`.
