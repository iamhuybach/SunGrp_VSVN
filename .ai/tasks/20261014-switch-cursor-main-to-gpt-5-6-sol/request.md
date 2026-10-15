# Request

## User outcome

Use `gpt-5.6-sol` with `medium` reasoning as Cursor Main until the user explicitly requests a return to Grok 4.7 Medium.

## Scope

### In scope

- Record a global user-approved temporary Main-model override.
- Update the Cursor Main rule, setup guide, and prompt samples.
- Require each active task to record the override in `task-state.yaml`.

### Out of scope

- Changing `.codex/` or `.claude/` model and effort configuration.
- Migrating historical task state or changing the Grok baseline expectation.
- Automatically changing Cursor's model picker.

## Acceptance criteria

- Instructions consistently select `gpt-5.6-sol`, `medium`, in Cursor.
- The override remains active until an explicit user revocation.
- `doctor`, task validation, and deterministic verification pass.

## Constraints

- Use Cursor quota for Main.
- Preserve Grok 4.7 Medium as the reversible baseline.
- Do not commit, push, merge, or modify Git history.

## Classification rationale

- Complexity: medium; four coordinated instruction files.
- Risk: medium; model-routing behavior changes but no source-data behavior changes.
- Architecture: not required; the user selected the model and the reversible override mechanism already exists.
- Evidence: not required; repository inspection and deterministic validation are sufficient.
- Runtime proof: not required; Cursor model selection is confirmed by the operator in the model picker.
- Reviewer routing: `state-correctness-reviewer` for exception and gate consistency.
