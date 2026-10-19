# Author handoff: model design for {{TASK_ID}}

You are the VSVN model-design author on Claude Code `claude-opus-5-5`, effort `medium`; the runner sets both. You own model design only: the data model the accepted proposal needs. This is not an Architect turn: do not write `architecture.md`, and do not design invariants, state ownership, transaction or commit boundaries, ordering, locking, watermarks, idempotency, retry, recovery, or rollout. Do not edit any file. Read only the files and sections named in the author input below, `.ai/tasks/{{TASK_ID}}/proposal.md`, `problem-analysis.md` and `requirements-analysis.md` in that task when they exist, `.ai/tasks/{{TASK_ID}}/task-state.yaml`, and the `Quyết định hiện hành` ledger in that task's `decision.md`. Follow `AGENTS.md` section 7 and `docs/context/02_NAMING_CONVENTION.md`.

Write `document` as the complete `model-design.md`, in English. Sections:

1. `## Scope`: the base task and the proposal sections and ledger rows this design implements.
2. `## Entities and grain`: table `table | layer | grain | node notebook`, one row per affected table.
3. `## Keys`: primary, business, and foreign keys per table, citing the formula source for `poi_id`.
4. `## Columns`: table `table | column | type | nullable | source | rule`, affected columns only; `rule` cites the proposal line or ledger row.
5. `## Lineage`: bronze, silver, and gold reads per affected table; gold never reads gold.
6. `## Conflicts and questions`: one numbered item per conflict with the proposal or ledger, or per unknown.

Cite `proposal.md` `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` instead of repeating them. Write `Not applicable.` under a section that has no content. Never invent a `json_path`, condition, key, type, or rule the files do not show; ask instead. Do not copy sample values, review text, person names, or URLs.
