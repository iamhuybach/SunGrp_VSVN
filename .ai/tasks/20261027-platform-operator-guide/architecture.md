RESULT: PASS

## Main brief

### Decision
Write the two skills as procedure plus pointers (option A). Facts stay in `03_OPERATOR_GUIDE.md` and the code. The skills hold only steps, function names, and `vv.py show` anchors. `vsvn-operator-docs` adds a map from changed code anchors to guide sections. `vsvn-data-model-flow` labels each edge only from `join`/`union` in `def build`. `write_mode` and `load_mode` are per-table notes, and quality-check joins are not edges. Save the skills with `materialize --write`. Add one context-map row. The guide content is unchanged.

### Invariants Main must preserve
- I1: Neither new `SKILL.md` contains a ```` ```mermaid ```` fence or the strings `lock_exec_id|last_src_version|reject_count|gld_srv_poi_|gld_enr_poi_`.
- I2: Each frontmatter has only `name` (equal to the folder) and `description`. The description is ≤ 500 characters with no `": "`.
- I3: The descriptions keep their "Do not use" clauses: no notebooks/DDL/seeds/pipeline JSON for operator-docs; no `notebooks_lgc/` and no grain/key/column change for data-model-flow.
- I4: `python scripts/vv.py doctor` prints no `WARN:`.
- I5: Every guide anchor the skills use resolves to exactly one heading with `vv.py show`.
- I6: The guide `toc` shows the five `##` sections in order. The guide has no `CONFLICT`.
- I7: Existing notebook diffs touch only markdown, comments, or docstrings. All three changed notebooks compile.
- I8: No external `SKILL.md` text is in the repository.
- The runtime gate stays not run. Do not commit.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| 1 | `.cursor/skills/vsvn-operator-docs/SKILL.md` | whole file | Create from the `FILE` block via `materialize --write` | The file bytes equal the block; I1–I3 hold |
| 2 | `.cursor/skills/vsvn-data-model-flow/SKILL.md` | whole file | Create from the `FILE` block via `materialize --write` | The file bytes equal the block; I1–I3 hold |
| 3 | `docs/AGENT_PROMPT_SAMPLES.md` | `## Bản đồ context` table, directly after the `\| Data model \|` row | Insert the row given in full doc "Implementation plan" step 4. Insert only if `vsvn-operator-docs` is not already in the file | The row is present once; doctor has no prompt-sample budget WARN |
| 4 | `.ai/tasks/20261027-platform-operator-guide/decision.md` | ledger row D6 and `## Lịch sử quyết định` | D6 becomes "Hai `SKILL.md` ghi từ FILE block của architecture PASS bằng `materialize --write`". Add one dated history line | `validate` PASS |
| 5 | `.ai/tasks/20261027-platform-operator-guide/resume.md` | whole file | Overwrite with the current status and next step (review) | The file reflects the post-materialize state |

### Order and stop points
1. Run `git diff --stat` and `git diff -- notebooks/`, then the compile command. **STOP for user decision** if any executable code line changed or compile fails.
2. Run `python scripts/vv.py materialize 20261027-platform-operator-guide`. **STOP for evidence** if it lists anything other than exactly the two skill paths.
3. Run `python scripts/vv.py materialize 20261027-platform-operator-guide --write`.
4. Edit row 3.
5. Run every check under Tests and verification. **STOP** if an anchor is ambiguous or missing, or if doctor warns. Report the output. Do not rename guide headings without recording it in `decision.md`.
6. Edit rows 4–5. Hand off to review (`sql-data-reviewer`, `spark-runtime-reviewer`). **STOP before commit.**

### Tests and verification
- `python scripts/vv.py doctor` → exit 0 with no `WARN:` lines.
- `python scripts/vv.py validate 20261027-platform-operator-guide` → `PASS`.
- `python scripts/vv.py verify 20261027-platform-operator-guide` → pass. Its pytest step includes `tests/test_l1_ts_contract.py` and `tests/test_3p_l1_contract.py`.
- `python scripts/vv.py toc docs/context/03_OPERATOR_GUIDE.md` → sections 1–5 in order.
- Anchor checks, each printing one section:
  - `python scripts/vv.py show docs/context/03_OPERATOR_GUIDE.md "1. Bảng ctrl"`
  - the same for `"2. Data lineage"`, `"3. Thêm một field"`, `"4. Thêm một bảng"`, `"5. Tham số"`, `"5.3"`, `"5.4"`
  - `python scripts/vv.py show docs/context/NB_LIB_TRANSFORM_SLV_GLD.md "5. Hợp đồng"`
  - `python scripts/vv.py show notebooks/NB_SETUP_INITIAL_DDL.ipynb id:init_tables`, and the same for `id:init_cfg_partner`, `id:init_cfg_3p`, `id:init_seed_ctrl`, `id:init_seed_write`, `id:init_param`
- Grep checks:
  - `Grep "```mermaid"` in `.cursor/skills/vsvn-operator-docs` and `.cursor/skills/vsvn-data-model-flow` → 0 matches.
  - `Grep "lock_exec_id|last_src_version|reject_count|gld_srv_poi_|gld_enr_poi_"` in the same two folders → 0 matches.
  - `Grep "CONFLICT"` in `docs/context/03_OPERATOR_GUIDE.md` → 0 matches.
- Compile: run the one-line `python -c "...compile..."` command from the full doc "Verification" on `notebooks/NB_00_ORCHES_SLV_TO_ENR.ipynb notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb notebooks/NB_SETUP_INITIAL_DDL.ipynb` → `compiled 3 notebooks`.

### Read only if needed
- `Alternatives`: rows 1–2 (why there are pointers and no tables, why two skills, why no reference file).
- `Invariants`: rows 1–3 (exact test strings).
- `Implementation plan`: row 3 (exact context-map row text) and step 1 (I7 check).
- `Verification`: full compile command and anchor list.
- `Skill files`: the `FILE` blocks for rows 1–2.
- `Partial failure`, `Retry and recovery`: if materialize or doctor fails.

# Architecture: 20261027-platform-operator-guide

Task: operator guide plus two project skills. Risk `low`, complexity `medium`, signal `design_tradeoffs`. No table, column, grain, or key changes, so `model-design.md` is not required (D1).

## Scope

- Materialize two new skills from the `FILE` blocks in this document:
  - `.cursor/skills/vsvn-operator-docs/SKILL.md`
  - `.cursor/skills/vsvn-data-model-flow/SKILL.md`
- Add one row to the `## Bản đồ context` table in `docs/AGENT_PROMPT_SAMPLES.md`. It points at `docs/context/03_OPERATOR_GUIDE.md` and the two skills.
- Update the task ledger: set D6 to "skills written from architecture FILE blocks", and add a history line.
- `docs/context/03_OPERATOR_GUIDE.md` is already written. This design does not change its content. Change it only when an anchor check in the verification section fails.
- The working tree already has edits from triage under the user decision of 2026-10-27 (D4, D5): context files, `AGENTS.md`, `vsvn-notebook-library/SKILL.md`, and comments, titles, and docstrings in three notebooks. This design leaves them alone. It only requires them to be non-executable (invariant I7).

## Non-goals

- No notebook, DDL, seed, pipeline, test, rule, or `scripts/vv.py` behavior change.
- No `notebooks_lgc/` and no `01_DATA_MODEL.md` §9.
- No `run-author --kind model`, no `model_override`, no `exceptions`.
- No Fabric probe and no runtime gate. Runtime stays not run.
- No commit.
- No change to the activity name `NB_00_ORCHES_SLV_TO_ENR_15P` in pipeline JSON (D4).

## Invariants

- I1. A `SKILL.md` holds only reusable steps, paths, and section anchors. It holds no ctrl column table, no lineage diagram or edge list, no parameter table with defaults, and no registry rows. Test: neither skill contains a ```` ```mermaid ```` fence. Neither contains a ctrl column name from `TABLE_SPECS` (for example `lock_exec_id`, `last_src_version`, `reject_count`) outside a procedure step that names a function.
- I2. Each skill's frontmatter has exactly `name` and `description`, in the same style as the four existing skills. `name` matches the folder. The description says what the skill does, when to use it, and when not to. It has no `": "` sequence, so the plain YAML scalar stays valid. It is at most 500 characters.
- I3. `vsvn-operator-docs` says it is not for editing notebooks, DDL, seeds, or pipeline JSON. `vsvn-data-model-flow` says it is not for `notebooks_lgc/` and not for changing grain, keys, or columns.
- I4. `python scripts/vv.py doctor` prints no `WARN`. Each `SKILL.md` is ≤ 20480 bytes, `docs/AGENT_PROMPT_SAMPLES.md` is ≤ 25600 bytes, and `AGENTS.md` is ≤ 8192 bytes.
- I5. Every Markdown anchor a skill passes to `vv.py show` resolves to exactly one heading in the current guide.
- I6. The guide keeps five `##` sections in the requested order. It has no unresolved `CONFLICT`.
- I7. Every notebook diff in the working tree is in markdown cells, comments, or docstrings. Every code cell compiles.
- I8. External skills are cited only by name, source, and technique (already in `decision.md`). No external `SKILL.md` text is copied.

## State ownership

| Artifact | Owner | Writer in this task |
|---|---|---|
| `03_OPERATOR_GUIDE.md` facts | Repository code and context files | Main, already written in triage. No new edits unless an I5 or I6 check fails |
| Skill procedure | This architecture (`FILE` blocks) | `vv.py materialize --write` |
| Context-map row | `docs/AGENT_PROMPT_SAMPLES.md` | Main, one-row edit |
| Decisions | `decision.md` | Main |
| Task gates | `task-state.yaml` through `vv.py` | Main, through gate commands only |

## Grain and keys

Not applicable: no table, column, grain, or key changes. The data-model skill reads grain from `NodeSpec.pk` and registry `is_key` and does not define it.

## Ordering

1. Run the I7 check on the existing notebook diffs, so later steps start from a clean base.
2. Run `materialize` without `--write`. It must list exactly two paths.
3. Run `materialize --write`.
4. Add the context-map row.
5. Run the anchor check (I5), `doctor`, `validate`, and `verify`.
6. Update the ledger and `resume.md`. Then hand off to review: `sql-data-reviewer` for the lineage and join wording in the data-model skill, and `spark-runtime-reviewer` for the parameter and orchestration procedure.

## Transaction and commit boundaries

Not applicable: these are local file writes with no shared state and no commit (request).

## Idempotency

`materialize --write` writes the exact block bytes. A second run gives the same files. The context-map row is inserted once: check that `vsvn-operator-docs` is absent from the file before inserting it.

## Concurrency

Not applicable: one Main session edits local files.

## Retry and recovery

If `materialize` fails on a path outside scope or on a block parse error, fix nothing by hand: report it and stop, because the fault is in this architecture. If `doctor` warns, remove the cause rather than raising a limit.

## Partial failure

- Skills written but row not added: the skills still work, and the map just omits them. Finish step 4.
- One skill written and the other not: `materialize` writes both or fails during parsing, before any write. If a file system error leaves one file, rerun `--write`.

## Observability

Outputs to check: `materialize` lists the two paths, `doctor` exit code and output, `validate` prints `PASS`, `verify` output, and the `toc` of the guide. Record the outputs in the verification record. Do not paraphrase them.

## Security

Not applicable for data. The skills contain no credentials, workspace GUIDs, or email addresses. The public skill URLs are already in `decision.md`. The skills cite only skill names, not URLs, so the repository does not depend on external content.

## Rollout

The skills take effect the next time an agent loads `.cursor/skills/`. No deploy is needed.

## Rollback and forward recovery

To roll back, delete the two skill folders and the one context-map row. Nothing else depends on them. Forward recovery: edit the skill, then record the change in `decision.md` history.

## Alternatives

| Option | Description | Verdict |
|---|---|---|
| A. Procedure plus pointers (selected) | `SKILL.md` holds steps, file paths, function names, and `vv.py show` anchors. Facts stay in the guide and context files | Selected. Facts have one copy, and skills stay small and do not drift when ctrl columns or nodes change. Cost: the agent must open the guide or code, which the read-budget commands keep cheap |
| B. Skill embeds tables and diagram | Copy ctrl columns, lineage edges, and parameter tables into `SKILL.md` | Rejected. It duplicates facts, drifts from the guide on the next node or column change, risks the 20 KB budget, and the request forbids it |
| C. One combined skill | A single skill for docs and model/flow | Rejected. The triggers differ: guide upkeep versus inventory and lineage for any document. The request names two skills. A combined description cannot state both "not for" limits clearly |
| D. Skill folder with a `reference.md` | Progressive disclosure inside the skill folder | Rejected. `scope.files` lists only `SKILL.md`. The detail file already exists (`03_OPERATOR_GUIDE.md`), as the `skill-creator` technique recommends |
| E. Data-model skill writes `model-design.md` | Reuse the model-design path | Rejected. That path designs changes (`run-author --kind model`). This skill describes the current state only (request constraint) |

Selected trade-off: option A, with a section-to-code dependency map in `vsvn-operator-docs`. The map tells a later agent which guide section to re-check when a given function or cell changes. It replaces copied facts with a cheap way to locate them.

Lineage-labelling decision for `vsvn-data-model-flow`:

- The edge label comes only from `join(..., how)` or `union*` inside `build`.
- `write_mode` and the edge `load_mode` are written as per-table notes (D3).
- Joins used only inside a quality count, such as the `ctx.warn(..., left_anti ...)` in `NB_GLD_SRV_POI_REVIEW`, are not edges.

The rejected alternative was labelling edges from `load_mode`. It loses the join type the request asks for.

## Implementation plan

1. Check the existing diffs (I7). Run `git diff --stat`, then `git diff -- notebooks/`, and compile the three changed notebooks with the command under Verification. If an executable line changed, stop for a user decision.
2. Run `python scripts/vv.py materialize 20261027-platform-operator-guide`. It must list exactly the two skill paths.
3. Run `python scripts/vv.py materialize 20261027-platform-operator-guide --write`.
4. In `docs/AGENT_PROMPT_SAMPLES.md`, under `## Bản đồ context`, insert this row directly after the `| Data model |` row:

   `| Vận hành, data model và flow | `docs/context/03_OPERATOR_GUIDE.md` (42 KB), skill `vsvn-operator-docs`, skill `vsvn-data-model-flow` | `toc` rồi `show … "<tiền tố tiêu đề>"`, ví dụ `"2. Data lineage"`. Không đọc cả file |`

5. Run the checks in Verification.
6. Update `decision.md`: change D6 to "Hai `SKILL.md` ghi từ FILE block của architecture PASS bằng `materialize --write`", and add one history line. Overwrite `resume.md`.

## Verification

- `python scripts/vv.py materialize 20261027-platform-operator-guide` lists exactly two paths.
- `python scripts/vv.py doctor` exits 0 and prints no `WARN:` line (I4).
- `python scripts/vv.py validate 20261027-platform-operator-guide` prints `PASS`.
- `python scripts/vv.py verify 20261027-platform-operator-guide` passes. Its pytest step reads the extract notebooks and `NB_CREATE_DDL`.
- `python scripts/vv.py toc docs/context/03_OPERATOR_GUIDE.md` lists `1. Bảng ctrl`, `2. Data lineage gold`, `3. Thêm một field…`, `4. Thêm một bảng…`, `5. Tham số notebook`, in that order (I6).
- Anchor check (I5). Each command must print one section without an "Ambiguous" or "No Markdown heading" error:
  - `python scripts/vv.py show docs/context/03_OPERATOR_GUIDE.md "1. Bảng ctrl"`
  - same for `"2. Data lineage"`, `"3. Thêm một field"`, `"4. Thêm một bảng"`, `"5. Tham số"`, `"5.3"`, `"5.4"`
  - `python scripts/vv.py show docs/context/NB_LIB_TRANSFORM_SLV_GLD.md "5. Hợp đồng"`
  - `python scripts/vv.py show notebooks/NB_SETUP_INITIAL_DDL.ipynb id:init_tables` (also `id:init_cfg_partner`, `id:init_cfg_3p`, `id:init_seed_ctrl`, `id:init_seed_write`, `id:init_param`)
- Content checks (I1, I3):
  - `Grep` for ```` ```mermaid ```` in `.cursor/skills/vsvn-*/SKILL.md` returns 0 matches.
  - `Grep` for `lock_exec_id|last_src_version|reject_count|gld_srv_poi_|gld_enr_poi_` in the two new skills returns 0 matches.
  - `Grep` for `CONFLICT` in `docs/context/03_OPERATOR_GUIDE.md` returns 0 matches.
- Notebook compile (I7). Run from the repository root:

  ```text
  python -c "import json,sys;[compile(''.join('\n' if l.startswith('%') else l for l in ''.join(c['source']).splitlines(True)),p+'#cell'+str(i),'exec') for p in sys.argv[1:] for i,c in enumerate(json.load(open(p,encoding='utf-8'))['cells']) if c['cell_type']=='code' and c.get('metadata',{}).get('microsoft',{}).get('language','python')=='python' and not ''.join(c['source']).startswith('%%')];print('compiled',len(sys.argv)-1,'notebooks')" notebooks/NB_00_ORCHES_SLV_TO_ENR.ipynb notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb notebooks/NB_SETUP_INITIAL_DDL.ipynb
  ```

  It must print `compiled 3 notebooks`.
- Runtime gate stays not run (`runtime_required=False`). Do not mark it pass.

## Skill files

FILE: .cursor/skills/vsvn-operator-docs/SKILL.md
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

### 2. Gold lineage

Follow `vsvn-data-model-flow` with scope `lh_vv_gold.dbo` and `lh_vv_gold.enr`. Put the diagram and one subsection per gold table in this section.

### 3. Add a bronze-to-silver field

1. Configuration: add a registry row in the seed for the source, in both DDL notebooks (`docs/context/02_NAMING_CONVENTION.md` §2.1). In `NB_SETUP_INITIAL_DDL` the seed is `TABLE_CONFIGS` (`id:init_cfg_partner`) or `TABLE_CONFIGS_3P` (`id:init_cfg_3p`).
2. Required configuration: list the checks `build_table_specs` makes on a registry row, plus `check_config` for third party. Cite each check.
3. Re-init means `NB_SETUP_INITIAL_DDL` on an empty environment:
   - `p_apply` is in `id:init_param`. Read its default and the values `to_bool` accepts.
   - Name the MERGE keys used in `id:init_seed_write`.
4. No re-init means a patch to an existing environment:
   - Add a final patch cell in `NB_CREATE_DDL`, per `02_NAMING_CONVENTION.md` §2.1.
   - On the next extract run, `ensure_target` adds the column.
5. Notes: take `full_reload` and `allow_full_scan` steps only from the context file of that source. Never carry one source's step over to the other source.

### 4. Add a bronze-to-silver table

1. Repeat section 3, and also add a `ctrl_mng_pipeline_config` row in both DDL notebooks.
2. Take the allowed `load_mode` values from the tuple that each extract notebook passes to `load_table_specs`.
3. The source watermark is one row per raw table, not one per target (`CTRL_TABLES_CONTEXT.md` §4). A new raw table needs a watermark row. A new target on an existing raw table does not.
4. `ensure_target` creates the target table. Do not document a `CREATE TABLE` in the DDL notebooks, except the cases listed in `02_NAMING_CONVENTION.md` §2.1.

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
END_FILE

FILE: .cursor/skills/vsvn-data-model-flow/SKILL.md
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
END_FILE
