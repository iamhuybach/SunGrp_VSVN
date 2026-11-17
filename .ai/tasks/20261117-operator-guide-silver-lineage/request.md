# Request

## User outcome

`docs/context/03_OPERATOR_GUIDE.md` describes the repository model as it exists today, including a silver data-lineage section that is not in the guide now.

## Scope

### In scope

- Refresh `docs/context/03_OPERATOR_GUIDE.md` so its table inventory and lineage match current DDL, ctrl seeds, and node notebooks.
- Add silver data lineage in section 2, after the gold lineage, using the same diagram layout as the existing gold figures.

### Out of scope

- Notebooks, DDL, seeds, pipeline JSON, and `notebooks_lgc/`.
- `docs/context/01_DATA_MODEL.md` §9.
- `.cursor/skills/vsvn-operator-docs/SKILL.md` (see decision D-01).

## Acceptance criteria

- The guide still has the five `##` sections in the skill order.
- Section 2 lists every current gold `dbo` and `enr` table, and every current silver L1 and silver recompute table, with grain, write mode, and producer.
- Each lineage edge has a repository anchor. Edge-table row count equals the diagram edge count.
- `python scripts/vv.py doctor` prints no `WARN`.

## Constraints

- Document only. A fact that needs a code, DDL, seed, or pipeline change stops the task.
- Vietnamese prose. Identifiers stay in English, copied from the code.
- Cite a file plus a section or a notebook cell for every required row, edge, command, and required parameter.
- Do not infer a key or a join from column names.

## Classification rationale

- Complexity: `low`. No signal. The change rewrites one Markdown guide from repository facts. It does not change a table, column, grain, key, or runtime behavior.
- Risk: `low`. No behavior change. The result is checked by reading the cited anchors and by `vv.py doctor`.
- Architecture: not required. No grain, key, owner, transaction, CDC, watermark, lock, or orchestration change.
- Evidence: not required. Correctness is repository inspection.
- Runtime proof: not required. No Fabric DEV step and no `docker compose` step.
- Reviewer routing: `required_reviewers` empty. No specialist path in WORKFLOW.md §7 matches a single operator-guide Markdown file. `risk_gate` is not required at `risk_level` `low`. Fast lane: one file, no behavior change.
