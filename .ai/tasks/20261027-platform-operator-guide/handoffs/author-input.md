# Author input

Guide: `docs/context/03_OPERATOR_GUIDE.md`, five sections in order.

1. Ctrl tables and required fields. Required = NOT NULL in `NB_SETUP_INITIAL_DDL` cell 3 plus ConfigError. That DDL has no NOT NULL on ctrl columns.
2. Gold table lineage for `dbo` and `enr` from `TABLE_SPECS`, relationship from `join` or `union` in each node `build` cell.
3. Add a bronze-to-silver field: registry row, both DDL notebooks, `p_apply` on setup, patch cell on `NB_CREATE_DDL`, `ensure_target` ALTER.
4. Add a bronze-to-silver table: pipeline-config row plus registry rows. Watermark is per raw source.
5. Parameter contracts for the two extract notebooks and `NB_00_ORCHES_SLV_TO_ENR` / `NB_00_ORCHES_SLV_TO_GLD`. Sub-notebook frame is already in the guide, from `NB_LIB_TRANSFORM_SLV_GLD.md` §5.

Skills, same frontmatter style as the four skills in `.cursor/skills/`:

- `.cursor/skills/vsvn-operator-docs/SKILL.md` — write or update this operator guide. Not for editing notebooks or DDL.
- `.cursor/skills/vsvn-data-model-flow/SKILL.md` — table-level data model and data flow from current DDL and notebooks. Not for `notebooks_lgc/` and not for changing grain, keys, or columns.

Put only reusable steps and paths into `SKILL.md`. Do not copy ctrl tables, lineage diagrams, or column lists. Description states what the skill does, when to use it, and when not to use it. Keep each description short enough that `python scripts/vv.py doctor` has no budget WARN.

Procedures to encode, from `decision.md` history:

- Ctrl required from `TABLE_SPECS` plus `build_table_specs`, `build_dag`, `check_config`, and `require_ctrl_columns`. Skip seed sections titled "Dữ liệu hiện có".
- Lineage from the current gold `TABLE_SPECS` and the node `build` cell. No node file means say there is no node. Keep `write_mode` separate from the join.
- Field or table add: both DDL notebooks, setup `p_apply` versus a final `NB_CREATE_DDL` cell. `ensure_target` adds the silver column.
- Parameters: parameter cell plus the validation function. Two sources that disagree: write CONFLICT and stop.

Decisions already applied: notebook name `NB_00_ORCHES_SLV_TO_ENR`; pipeline `PL_VV_TRANS_SLV_TO_ENR_15M`; partner hash is the `reject_rows` expression in cell 6; 3rd-party `after_payload` comes from `normalized_payload`.

Public structure only, do not copy external skill text: `skill-creator` (description has WHAT and WHEN; short procedure; detail in another file), `datahub-lineage` (each edge has a source), `creating-mermaid-dbt-dag` (diagram steps in the skill, figure rules in the referenced doc). Sources are in `decision.md`.

Emit `FILE` blocks for the two skills. `SKILL_FILE` is also accepted by materialize. Do not emit notebook, DDL, pipeline, test, rule, `AGENTS.md`, or `vv.py` blocks. One context-map row for `docs/AGENT_PROMPT_SAMPLES.md` may be a `FILE` block only if it is the full file.
