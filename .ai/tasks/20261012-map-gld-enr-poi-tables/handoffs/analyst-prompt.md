You are the VSVN requirements-analyst defined in .claude/agents/requirements-analyst.md. Follow that file exactly.

Before reading inputs, confirm the active model is claude-opus-5-5 and effort is medium. If either differs, stop and report the active model and effort. Do not continue on a substitute.

Required inputs:
- task_id: 20261012-map-gld-enr-poi-tables
- Mapping path: docs/requirements/20261012-map-gld-enr-poi-tables/MAPPING.md
- BRD path: docs/requirements/20261012-map-gld-enr-poi-tables/BRD.md

This is a rerun. Mapping version is 13. BRD version is 11. Replace the whole file `.ai/tasks/20261012-map-gld-enr-poi-tables/requirements-analysis.md`. Do not edit any other path.

Apply "Template exceptions" and "Out-of-scope legacy physical facts". `src_id` is not a required mapping cell. A blank `src_id` is not `MISSING_SOURCE`. `MQ-055` and `ID-005` are removed. `MQ-057` names `review_text` from `slv_3p_poi_review.text`. `MQ-058` states append, not join, and drops the mandatory `src_id` rule. `MQ-059` states that `notebooks_lgc` is a field-business comparison source, not a design model. Do not reopen `AG-001` to `AG-012`. Keep platform checks as `PLATFORM_VIOLATION` when they still match. Do not invent answers for anything still blank.

If the write is denied, return the complete file after a line `ANALYSIS_FILE: .ai/tasks/20261012-map-gld-enr-poi-tables/requirements-analysis.md` and before a line `END_ANALYSIS_FILE`.
