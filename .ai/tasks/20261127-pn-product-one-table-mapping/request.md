# Request

## User outcome

The partner product mapping documents specify one table in the shape of the legacy `ai_product` model. Task `20261127-gld-pn-product` stays blocked on D-A until that mapping exists. This task does not change a notebook, DDL, or pipeline.

## Scope

### In scope

- Rewrite the partner product mapping so the documented target is one table, using `docs/context/mapping_legacy_ai_product.md` section `## 1. Table: ai_product` as the legacy shape.
- Read-only sources: `docs/context/mapping_slv_pn_product.md`, `docs/context/mapping_slv_pn_product_l2.md`, `.ai/tasks/20261127-slv-pn-product-business-mapping/decision.md` section `## Quyết định hiện hành`, and D-A in `.ai/tasks/20261127-gld-pn-product/decision.md`.
- After the user answers the eight open choices, record those answers in this task's `decision.md`, then continue model design and architecture. The mapping file edited later is only a file named by the architecture edit list.

### Out of scope

- Notebooks, DDL, pipeline JSON, and seeds.
- Any file under `.ai/tasks/20261127-gld-pn-product/`.
- `run-author --kind analysis` and `run-author --kind proposal`.
- Implementing or unblocking the gold task in this task.

## Acceptance criteria

- Classification matches `docs/agent-system/WORKFLOW.md` §Classification and §Review routing: signal `data_model_change`, `architecture_required` true, required reviewer `sql-data-reviewer` only.
- Mapping prose is written only after all eight choices are rows in `## Quyết định hiện hành`, and only in files the architecture edit list names.
- The task stops when specialist review finishes, or earlier at `EVIDENCE_REQUIRED` or `USER_DECISION`.

## Constraints

- One chat per phase.
- Do not infer the eight choices. They are user decisions.
- Signal `data_model_change` requires `model-design.md` from `run-author --kind model` before the Architect.
- Do not route `spark-runtime-reviewer`. No notebook is in scope.

## Classification rationale

- Complexity: medium. The documented grain moves from the current L1 tables plus the three Q-19 L2 tables toward one table. That is a model change, not a wording fix.
- Risk: medium. The mapping is the contract task `20261127-gld-pn-product` will follow after D-A. This task does not write notebooks or tables. Rollback is reverting the mapping document.
- Architecture: required. WORKFLOW §5 requires architecture when a table grain or key changes. Signal `data_model_change`. `gates.architecture` is pending.
- Evidence: not required at triage. The open items are choices among options already written in the named mapping docs and decision ledgers.
- Runtime proof: not required. No notebook, pipeline, or table is changed or executed.
- Reviewer routing: `sql-data-reviewer` owns grain, joins, types, and field mapping. `spark-runtime-reviewer` is omitted because no notebook is in scope. Risk is medium, so `risk-gate` is not required.
