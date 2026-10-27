---
name: vsvn-operator-docs
description: Write or update the operator guide docs/context/03_OPERATOR_GUIDE.md from the current repository, covering ctrl table meaning and required columns, gold lineage, steps to add a bronze-to-silver field or table, and notebook parameter contracts. Use when a guide section is stale or a notebook parameter, ctrl column, registry rule, or gold table changed. Do not use to edit notebooks, DDL, seeds, or pipeline JSON, or to read notebooks_lgc/.
---

# VSVN operator docs

The operator guide `docs/context/03_OPERATOR_GUIDE.md` describes what the repository does today. This skill is the procedure to write or refresh it. The facts live in the guide and in the code it cites, never in this file.

`AGENTS.md` and `.cursor/rules/` still apply. If this skill conflicts with them or with the current code, stop and report the conflict in the task.

## Boundary

- Document only. A doc fix that needs a notebook, DDL, seed, or pipeline change becomes a separate task.
- Sources: `notebooks/`, `docs/context/`, `pipelines/<PL>/<PL>.json`. Never `notebooks_lgc/`. Never `docs/context/01_DATA_MODEL.md` §9 (old model). Never a "Dữ liệu hiện có" seed section or a migration note in `docs/context/CTRL_TABLES_CONTEXT.md` to decide what is required.
- Write prose in Vietnamese. Keep table, column, parameter, notebook, pipeline, and command names in English, exactly as in the code.
- Keep the five `##` sections in order: ctrl tables, gold lineage, add a field, add a table, notebook parameters. Keep the existing table layouts when updating a row.

## Citation rule

- Every required row, lineage edge, command, and required parameter cites a file plus a section (`§n`) or a notebook cell. Write a cell as `cell <i>` plus the function name or cell id, because cell indexes move.
- If something is not in the repository, write `MISSING`. Never write a command from memory. The user runs notebooks in Fabric. There is no shell command for that unless one exists in the repository.
- If two sources disagree on the same fact (parameter cell versus validator, notebook versus context, two context files):
  1. Write `CONFLICT: <source A> vs <source B>` in the row.
  2. Add the question to `decision.md`.
  3. Set the task to `user_decision` and stop. Never pick one.
- If the user decides: record the decision in the `decision.md` ledger, fix the row, and remove the marker.
- Two different objects that both exist (for example two pipeline names seeded side by side) are not a conflict. List both and say which one the notebook uses by default.

## Read budget

- Markdown: run `python scripts/vv.py toc <file>`, then `python scripts/vv.py show <file> "<heading prefix>"`. The prefix must match one heading. `"1."` also matches `1.1` and fails as ambiguous, so use `"1. Bảng ctrl"`.
- Guide anchors: `"1. Bảng ctrl"`, `"2. Data lineage"`, `"3. Thêm một field"`, `"4. Thêm một bảng"`, `"5. Tham số"`, and subsections such as `"5.4"`.
- Notebooks: `python scripts/vv.py show notebooks/<name>.ipynb id:<cell id>`, `def:<function>`, or `grep:<regex>`. Search before opening cells.

## Procedure by guide section

### 1. Ctrl tables

1. Get the table list and column types from `TABLE_SPECS` in `notebooks/NB_SETUP_INITIAL_DDL.ipynb` (`id:init_tables`). Take the entries whose name starts with `lh_vv_ctrl.dbo.ctrl_`.
2. Take meaning from `CTRL_TABLES_CONTEXT.md` §3–§9, one section per table.
3. A column is required when either of these holds:
   - the DDL declares it `NOT NULL`;
   - a `ConfigError` is raised when the column is empty or invalid.

   Find the conditions with `grep:ConfigError`, then `def:` in these functions:
   - `build_table_specs` and `load_table_specs` (`NB_LIB_EXTRACT_RAWDATA`);
   - `load_config_rows`, `build_dag`, `require_ctrl_columns`, and `_validate_orch_params` (`NB_LIB_TRANSFORM_SLV_GLD`);
   - `check_config` (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`).
4. A column that only filters rows (for example, a row is skipped unless the value is `1`) is "Không theo DDL" plus the filter. It is not required.
5. Library code fills log, state, and reject columns. Mark them not required unless step 3 applies, and name the function that writes them.
6. For a column whose values are a fixed set, list every value, what it means, and which notebook accepts it. Take the set from the tuple or dict in code (`LOAD_MODES`, `CONVERT_RULES`, `EXTRACT_MODES`, `EDGE_LOAD_MODES`, `RUN_MODES`, status literals). Do not copy that table into this skill.

### 2. Data lineage

Follow `vsvn-data-model-flow` with scope `lh_vv_gold.dbo` and `lh_vv_gold.enr`. One diagram per gold table. Put `enr` tables before `dbo`. Each diagram is a row of equal boxes and a straight arrow. Do not write the join type on the arrow. Put the join type in a table under the figure. Do not add a code-citation column.

### 3. Add a bronze-to-silver field

1. Configuration is a `MERGE` the operator runs. Do not send them to `NB_SETUP_INITIAL_DDL` or `NB_CREATE_DDL`. Number the guide steps. Each step contains the SQL or parameter assignment, with placeholders only for the new names. The `MERGE` keys match `init_seed_write`, but the guide shows the statement itself.
2. Required configuration: list the checks `build_table_specs` makes on a registry row, plus `check_config` for third party. Cite each check.
3. The same `MERGE` is used whether the control tables are empty or already populated. It inserts only unmatched keys.
4. On the next extract run, `ensure_target` adds the column. Show that statement. Do not add a hand-written `ALTER` as a separate operator step.
5. Notes: take `full_reload` and `allow_full_scan` steps only from the context file of that source. Never carry one source's step over to the other source.

### 4. Add a bronze-to-silver table

1. Repeat section 3, and also give a `MERGE` into `ctrl_mng_pipeline_config`. Same rule: direct SQL, not the two DDL notebooks.
2. Take the allowed `load_mode` values from the tuple that each extract notebook passes to `load_table_specs`.
3. The source watermark is one row per raw table, not one per target (`CTRL_TABLES_CONTEXT.md` §4). A new raw table needs a watermark row. A new target on an existing raw table does not.
4. After the config is in place, the first extract run depends on whether the source watermark row already has a read pointer (`CTRL_TABLES_CONTEXT.md` §4). Write both steps in guide section 4 Step 6 and cite them there:
   - No pointer yet: one run with `allow_full_scan = True` (partner context §9, third-party context §10).
   - Pointer already set: one run with `table_filter` set to the new `trg_tbl` and `full_reload = True`. Do not use an incremental run for that table. An incremental read starts after the pointer, and a `SUCCESS` run moves the pointer (`CTRL_TABLES_CONTEXT.md` §4), so older events for the new table are never read. `full_reload` and `table_filter` do not move the watermark (`NB_LIB_EXTRACT_RAWDATA.md` §6, partner context §9).
5. `ensure_target` creates the target table. Do not document a `CREATE TABLE` in the DDL notebooks, except the cases listed in `02_NAMING_CONVENTION.md` §2.1.

### 5. Notebook parameters

1. The parameter cell is the cell tagged `parameters`. Take defaults only from that cell.
2. A parameter is required when it is blank or out of range and that raises `ConfigError` before any write. The checks are in:
   - `build_context` (extract notebooks) and `check_config` (third party);
   - `_validate_orch_params`, `build_dag`, and `plan_run` (orchestrators).

   Copy the ranges from the validator, not from the context file.
3. Take meaning from the parameter cell comments and the notebook's context file. If they disagree, apply the citation rule.
4. To compare pipeline names, check:
   - the parameter default;
   - `02_NAMING_CONVENTION.md` §3;
   - the `pipelines/` folders;
   - the constants in `id:init_seed_ctrl`.
5. Reuse: name the `%run` library and the final call, `run_extract` or `orchestrate`.
6. Sub-notebook frame: build it from `docs/context/NB_LIB_TRANSFORM_SLV_GLD.md` §5. Check it against:
   - the parameters `build_run_multiple_dag` passes;
   - the `run_node` signature;
   - the `NodeSpec` fields.

   The frame lives only in the guide. Never add an `.ipynb` file.

## Re-check map

When a task changes one of these code anchors, re-check the matching guide section in the same task. If the guide is not in that task's scope, record it as follow-up.

| Changed anchor | Guide section |
|---|---|
| `NB_SETUP_INITIAL_DDL` `id:init_tables` | 1, 2 (table list) |
| `build_table_specs`, `ensure_target`, `load_table_specs` | 1, 3, 4 |
| `build_dag`, `load_config_rows`, `require_ctrl_columns` | 1, 5 |
| `_validate_orch_params`, `plan_run`, `build_run_multiple_dag`, `run_node`, `NodeSpec` | 5 |
| A node notebook `build` cell or `SPEC` | 2 |
| Parameter cell or `build_context` / `check_config` of an extract notebook | 5 |
| `NB_CREATE_DDL` patch convention, `02_NAMING_CONVENTION.md` §2.1 | 3, 4 |
| `pipelines/<PL>/<PL>.json` names, `id:init_seed_ctrl` | 5 |

## Growing this skill

If a guide edit reveals a procedure this skill lacks, record it in `decision.md` history first. Then add it here as steps and paths only. Never add ctrl column tables, lineage edges or diagrams, parameter tables, or default values to this file.

## Checks before handing off

- `python scripts/vv.py toc docs/context/03_OPERATOR_GUIDE.md` lists the five `##` sections in order.
- No `CONFLICT` remains unless the task is at `user_decision`. List every `MISSING` in the handoff.
- Each anchor this skill names still resolves with `python scripts/vv.py show`.
- `python scripts/vv.py doctor` prints no `WARN`.

## Stop conditions

- A `CONFLICT` that needs a user decision.
- A fix that needs a code, DDL, seed, or pipeline change.
- A fact that only Fabric can show. Use `fabric-runtime-evidence` in a task that allows probes.
