## Model and reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium` (confirmed).
- Reviewers: `spark-runtime-reviewer`, `sql-data-reviewer`, `state-correctness-reviewer`, `fabric-pipeline-reviewer`.
- Risk gate: completed.

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `GATE-001` — P1 — `.cursor/skills/vsvn-extract-notebook/SKILL.md:59`: Existing reject hashes still collapse `NULL` with `''` and permit delimiter ambiguity, so distinct rejects can share an identity. Fix: migrate to deterministic SHA-256 over a fixed, aliased canonical JSON structure and define handling for existing reject rows.
- `GATE-003` — P1 — `.cursor/skills/vsvn-notebook-library/SKILL.md:63`: Retrying a blind append after an ambiguous post-commit error can duplicate log rows at their logical grain. Fix: use an idempotent `MERGE` on the grain key or reconcile commit outcomes before retrying, updating both library copies and affected readers.
- `GATE-005` — P1 — `.cursor/skills/vsvn-extract-notebook/SKILL.md:49`: Existing profile paths can group or collect unbounded raw-derived values, risking driver exhaustion on shared F16 capacity. Fix: map non-configured values to a bounded literal and cap sorted watch-list collections at 50 rows with truncation logging.

`GATE-002` and `GATE-004` are resolved.

## P2/P3

Count: `0`.
