---
name: vsvn-data-model-flow
description: Generate a table-level data model and data flow from the current DDL, ctrl pipeline config, and notebooks, with each lineage edge labelled by the join or union in the node build cell. Use when a document needs a table inventory, grain, or lineage diagram that matches the repository today. Do not use for notebooks_lgc/, for designing or changing grain, keys, or columns (that is run-author --kind model), or for editing notebooks or DDL.
---

# VSVN data model and flow

This skill describes the current model only: which tables exist, their grain, which notebook builds each one, and how its inputs combine. It never proposes a table, column, key, or grain. If the task needs a change, stop: that is `model-design.md` through `python scripts/vv.py run-author <task-id> --kind model`.

`AGENTS.md` and `.cursor/rules/` still apply. If this skill conflicts with them or with the current code, stop and report the conflict in the task.

## Where the facts live

| Fact | Source |
|---|---|
| Current tables and types | `TABLE_SPECS` in `notebooks/NB_SETUP_INITIAL_DDL.ipynb` (`id:init_tables`) |
| Silver L1 tables | `ctrl_mng_pipeline_config` and registry seeds (`id:init_cfg_partner`, `id:init_cfg_3p`). The tables are created by `ensure_target`, not by DDL |
| Recompute DAG edges | `ctrl_mng_pipeline_config` edge seeds (`id:init_seed_ctrl`) with `load_mode` `RECOMPUTE` or `APPEND`, read by `build_dag` |
| Node notebook name | the edge `nb_name`, else `NB_<UPPER(trg_tbl)>` (`build_dag`) |
| Inputs, grain, write mode | `SPEC = NodeSpec(...)` in the node notebook: `inputs`, `pk`, `write_mode` |
| Relationship type | `def build` in the node notebook |
| L1 key | registry `is_key` and `key_order` |
| Context cross-check | `docs/context/01_DATA_MODEL.md` §3–§8, `docs/context/NB_00_ORCHES_SLV_TO_GLD.md`, `docs/context/mapping_*.md` |

Never read `notebooks_lgc/` or `01_DATA_MODEL.md` §9. Do not infer a key or a join from column names.

## Procedure

1. **Scope.** Name the lakehouse schemas in scope, for example `lh_vv_gold.dbo` and `lh_vv_gold.enr`. List the targets from `TABLE_SPECS` by name prefix.
2. **Tables outside `TABLE_SPECS`.** A table that has DDL elsewhere (for example in `NB_CREATE_DDL`) but is not in `TABLE_SPECS` is listed as not current. Cite where it appears. It gets no edges.
3. **Node notebook.** For each target, resolve the notebook from the ctrl edge `nb_name` or the default name. Check that the file exists. If there is no file, write "không có node" and draw no edges.
4. **Inputs and grain.** Run `python scripts/vv.py show notebooks/<node>.ipynb grep:NodeSpec`.
   - Record each `inputs` role and its table, plus `pk` and `write_mode`.
   - Compare the inputs with the active ctrl edges of the node. If they differ, write `CONFLICT` and stop.
5. **Relationship per input.** Run `python scripts/vv.py show notebooks/<node>.ipynb def:build`. Then search with `grep:\.join\(|union|groupBy`. Label each input with one value:
   - `dòng gốc`: the base frame;
   - `inner join`;
   - `left join`;
   - `left_semi` (filter only);
   - `left_anti`;
   - `union` / `unionByName`;
   - `không join`: the only input.

   Add `sau groupBy` when the input is aggregated before the join. A join inside a quality count or `ctx.warn` is not an edge. An input declared but not used in `build` is a note, not an edge.
6. **Edge table.** Write one row per edge: target, source, relation, and anchor (`cell <i>` plus `build`). Every edge has an anchor.
7. **Diagram.** Use a Mermaid `flowchart LR`:
   - one `subgraph` per lakehouse schema, sources first;
   - short unique node ids, each labelled with the table name;
   - edges from source to target, labelled with the relation from step 5;
   - one edge per (source, target, relation);
   - no columns;
   - tables from steps 2 and 3 appear without edges.

   The figure in `docs/context/03_OPERATOR_GUIDE.md` §2 is the reference layout.
8. **Data model table.** For each table, write the table, the layer, the grain (`pk` or the registry key, quoted), the `write_mode`, and the producer notebook. Keep `write_mode` and the edge `load_mode` out of edge labels.
9. **Cross-check.** Compare the result with the context sources above. If they disagree, write `CONFLICT` with both sources, record the question in `decision.md`, and stop at `user_decision`.

## Output

Write into the document the task names, such as the operator guide §2 or a context file. This skill never writes `model-design.md` and never edits notebooks or DDL.

## Growing this skill

If a node uses a combine pattern this skill does not label, record it in `decision.md` history. Then add the label rule here. Never add an edge list, a diagram, or a table inventory to this file.

## Checks before handing off

- The edge table row count equals the diagram edge count.
- Every node id in an edge is declared in a `subgraph`.
- Every target from step 1 is either drawn with its edges or marked as having no node.
- No `notebooks_lgc/` path is cited.
- `python scripts/vv.py doctor` prints no `WARN`.

## Stop conditions

- The task needs a new or changed table, column, key, or grain.
- A `CONFLICT` between code and context, or between `NodeSpec` inputs and ctrl edges.
- A fact that only Fabric can show (for example, actual row grain). Use `fabric-runtime-evidence` in a task that allows probes.
