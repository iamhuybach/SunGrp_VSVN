# Request

## User outcome

A read-only consistency audit reports whether documented context, invariants, and contracts match the notebooks, Fabric pipeline JSON, and SQL currently in the repository.

## Scope

### In scope

- Compare `AGENTS.md`, `docs/context/**`, and `.cursor/rules/20-data-pipeline.mdc` with notebook, pipeline, and SQL implementations.
- Record a traceability matrix, missing inputs, findings, hypotheses, and required probes.
- Run deterministic verification and the automated review gate.

### Out of scope

- Editing context, notebooks, pipelines, SQL, or other source code to force a match.
- Committing or pushing.
- Running Fabric DEV.

## Acceptance criteria

- The task artifact states `MATCH`, `PARTIAL_MATCH`, `MISMATCH`, `NOT_IMPLEMENTED`, `UNDOCUMENTED_IMPLEMENTATION`, `NOT_VERIFIABLE`, or `MISSING_INPUT` for each checked invariant, with a file and location.
- `python scripts/vv.py verify` passes before review.
- Round 1 review uses `gpt-5.6-sol` at high effort and the reviewers required by the notebook, pipeline, SQL, and state surface.

## Constraints

- Review-only. Do not treat context or implementation as automatically correct.
- Do not infer control-table semantics beyond `docs/context/CTRL_TABLES_CONTEXT.md`.
- `PASS` is valid only when every in-scope invariant is checkable, required evidence is present, and no P0/P1 remains open.

## Classification rationale

- Complexity: high. The audit crosses notebooks, one pipeline, control-table contracts, and several written invariants.
- Risk: high. Mismatches include watermark, lock expiry, skipped third-party extract, and missing gold-log columns. `risk-gate` is required.
- Architecture: not required. This task does not change grain, commit order, or pipeline structure.
- Evidence: the comparison uses the repository. Live control-table columns and schedule overlap stay `NOT_VERIFIABLE` inside the report; they do not block writing the audit.
- Runtime proof: not a gate for this review-only task. Probes are listed for a later fix task.
- Reviewer routing: `spark-runtime-reviewer`, `fabric-pipeline-reviewer`, `sql-data-reviewer`, `state-correctness-reviewer`, plus `risk-gate` because risk is high.
