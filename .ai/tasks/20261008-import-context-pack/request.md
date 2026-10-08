# Request

## User outcome

The Visit Vietnam context pack is in `docs/context/`, with `CTRL_TABLES_CONTEXT.md` at the path agents already treat as the control-table contract.

## Scope

### In scope

- Store the 11 supplied files under `docs/context/` with their original names.
- Point `docs/context/README.md` at the pack and at the review notes.
- Keep `CHECK_CTRL_SNAPSHOT.py` byte-for-byte; ignore its unused Fabric imports in `ruff.toml`.

### Out of scope

- Rewriting the context to match the notebooks or pipeline currently in the repository.
- Running `CHECK_CTRL_SNAPSHOT.py` in Fabric DEV.
- Changing notebook or pipeline code.

## Acceptance criteria

- Each supplied file exists at `docs/context/<original name>`.
- File bytes match the supplied copies.
- `python scripts/vv.py verify` passes for this task.

## Constraints

- Do not treat "Dữ liệu hiện có" counts as a live Fabric snapshot.
- Do not infer `ctrl_*` behavior beyond what `CTRL_TABLES_CONTEXT.md` states.

## Classification rationale

- Complexity: low. This task copies reviewed documentation and does not change pipeline logic.
- Risk: low. No Fabric write path changes. The new contract can mislead a later code change, so the review notes name the two known gaps.
- Architecture: not required. No grain, lock, or orchestration design is being chosen here.
- Evidence: not required for the import. Live row counts stay labeled as logs through 05/10/2026.
- Runtime proof: not required.
- Reviewer routing: none. The review in this task is Main's comparison against the notebooks already in the repository.
